#!/usr/bin/env python3
"""fetch_query_log.py - download the AdGuard Home query log for classify_dns_log.py.

Part of VIDAA Clean TV. Standard library only. Run it yourself on your own
network: it talks only to the AdGuard Home address you give it, with the
admin credentials of your own installation.

Example:
  python3 fetch_query_log.py --host http://192.168.1.10:3000 \
      --user admin --limit 500 -o querylog.json

The password is read from the ADGUARD_PASSWORD environment variable, or
prompted for (not echoed). Output is the same JSON shape classify_dns_log.py
accepts, so the pipeline is:

  fetch_query_log.py ... -o querylog.json
  python3 classify_dns_log.py querylog.json --client TV_IP --rules
"""

import argparse
import base64
import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects: following one would forward the Authorization header
    (your admin credentials) to the redirect target."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_querylog_url(host, limit, offset=0):
    """Build the AdGuard Home /control/querylog URL for one page."""
    query = urllib.parse.urlencode({"limit": limit, "offset": offset})
    return f"{host.rstrip('/')}/control/querylog?{query}"


def basic_auth_header(user, password):
    """Return the HTTP Basic Authorization header value."""
    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def fetch_page(host, user, password, limit, offset=0):
    url = build_querylog_url(host, limit, offset)
    scheme = urllib.parse.urlparse(url).scheme
    if scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme: {scheme!r}")
    req = urllib.request.Request(url, headers={"Authorization": basic_auth_header(user, password)})
    opener = urllib.request.build_opener(_NoRedirect)
    with opener.open(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_pages(host, user, password, limit, pages):
    """Fetch up to `pages` consecutive pages and merge their 'data' lists.

    Stops early when a page comes back short (fewer entries than `limit`),
    which marks the oldest available entries. Returns
    (merged_dict, pages_fetched, maybe_more): maybe_more is True when fetching
    stopped on a full page, i.e. the export may be incomplete.
    """
    merged = None
    fetched = 0
    last_len = 0
    for i in range(pages):
        page = fetch_page(host, user, password, limit, offset=i * limit)
        if not isinstance(page, dict) or not isinstance(page.get("data"), list):
            raise ValueError("Unexpected response from AdGuard Home: expected an object with a 'data' list")
        fetched = i + 1
        last_len = len(page["data"])
        if merged is None:
            merged = page
        else:
            merged["data"].extend(page["data"])
        if last_len < limit:
            break
    # Stopping on a full page means the log MAY hold older entries (possible,
    # not certain: the log might end exactly on a page boundary).
    return merged, fetched, last_len == limit


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True, help="AdGuard Home base URL, e.g. http://192.168.1.10:3000")
    ap.add_argument("--user", required=True, help="AdGuard Home admin username")
    ap.add_argument("--limit", type=int, default=500, help="Max entries per page (default: 500)")
    ap.add_argument("--pages", type=int, default=1,
                    help="Pages to fetch, continuing to older entries until a short page (default: 1, max: 100)")
    ap.add_argument("-o", "--output", required=True, help="Output JSON file for classify_dns_log.py")
    args = ap.parse_args()

    if not 1 <= args.pages <= 100:
        sys.exit("--pages must be between 1 and 100")

    password = os.environ.get("ADGUARD_PASSWORD") or getpass.getpass("AdGuard Home password: ")
    try:
        if args.pages == 1:
            data = fetch_page(args.host, args.user, password, args.limit)
            pages_fetched = 1
            maybe_more = isinstance(data, dict) and len(data.get("data", [])) == args.limit
        else:
            data, pages_fetched, maybe_more = fetch_all_pages(
                args.host, args.user, password, args.limit, args.pages)
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            sys.exit(f"Redirect to {e.headers.get('Location')} refused - give the exact AdGuard Home address instead")
        sys.exit(f"HTTP {e.code} from AdGuard Home - check host and credentials")
    except ValueError as e:
        sys.exit(str(e))
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Cannot reach {args.host} - {e}. Run this on the same network as AdGuard Home.")

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    entries = len(data.get("data", [])) if isinstance(data, dict) else 0
    print(f"Wrote {entries} entries ({pages_fetched} page(s)) to {args.output}")
    if maybe_more:
        print("Warning: the last page fetched was full, so the log may hold older entries "
              "that were not exported. Re-run with a higher --pages value to be sure.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
