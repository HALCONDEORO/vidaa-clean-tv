#!/usr/bin/env python3
"""classify_dns_log.py - aggregate a DNS query log and classify domains against a blocklist.

Part of VIDAA Clean TV. Standard library only, no network access.

Accepted inputs (auto-detected):
  - AdGuard Home query log JSON export ({"data": [{"question": {"name": ...}, "client": ..., "reason": ...}, ...]})
  - dnsmasq log lines ('query[A] example.com from 192.168.1.10')
  - plain text, one domain per line

Examples:
  python3 classify_dns_log.py querylog.json --client 192.168.1.50 \
      --blocklist Blocked_Domains.txt --min-count 3
  python3 classify_dns_log.py dnsmasq.log --rules
"""

import argparse
import json
from datetime import datetime, timezone
import re
import sys
from collections import Counter

DNSMASQ_RE = re.compile(r"\bquery\[[A-Z]+\]\s+([A-Za-z0-9._-]+)\s+from\s+(\S+)")
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([A-Za-z0-9_-]{1,63}\.)+[A-Za-z]{2,63}\.?$")
ADGUARD_RULE_RE = re.compile(r"^\|\|([^^/]+)\^?")


def norm(domain):
    return domain.strip().lower().rstrip(".")


def parse_timestamp(value):
    """Parse an AdGuard 'time' field to an aware datetime; None if unusable."""
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def iter_queries_timed(path):
    """Yield (domain, client, filtered, timestamp_or_None) from any supported input.

    Only AdGuard Home JSON exports carry timestamps; dnsmasq and plain lists
    yield None in the last field.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        for entry in data["data"]:
            if not isinstance(entry, dict):
                continue
            question = entry.get("question") or {}
            raw_name = question.get("name")
            if not raw_name:
                continue
            name = norm(str(raw_name))
            if not name:
                continue
            client_info = entry.get("client_info") or {}
            client = entry.get("client") or client_info.get("name") or ""
            reason = str(entry.get("reason") or "")
            yield name, str(client), reason.startswith("Filtered"), parse_timestamp(entry.get("time"))
        return
    for line in text.splitlines():
        m = DNSMASQ_RE.search(line)
        if m:
            yield norm(m.group(1)), m.group(2), False, None
            continue
        candidate = norm(line)
        if DOMAIN_RE.match(candidate):
            yield candidate, "", False, None


def iter_queries(path):
    """Yield (domain, client, filtered) tuples from any supported input format."""
    for domain, client, filtered, _ts in iter_queries_timed(path):
        yield domain, client, filtered


def load_blocklist(path):
    """Load plain hostnames or AdGuard-format rules into a set of domains.

    Comment styles skipped: AdGuard '!', '#', '[' headers and '//' (the
    annotated format the upstream list currently uses).
    """
    domains = set()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("!", "#", "[", "//")):
                continue
            m = ADGUARD_RULE_RE.match(line)
            domains.add(norm(m.group(1) if m else line))
    return domains


def is_blocked(domain, blocked):
    """True if domain or any parent domain is on the blocklist."""
    parts = domain.split(".")
    for i in range(len(parts) - 1):
        if ".".join(parts[i:]) in blocked:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logfile", help="Query log: AdGuard Home JSON, dnsmasq log, or plain domain list")
    ap.add_argument("--client", help="Only count queries from this client IP (e.g. the TV)")
    ap.add_argument("--blocklist", help="Plain-hostname or AdGuard-format list to compare against")
    ap.add_argument("--min-count", type=int, default=1, help="Minimum query count to report (default: 1)")
    ap.add_argument("--rules", action="store_true", help="Print AdGuard candidate rules for unblocked domains")
    ap.add_argument("--timeline", nargs="?", const=60, type=int, metavar="MINUTES",
                    help="Per-bucket query counts over time (default 60). Needs timestamps: AdGuard JSON exports only")
    args = ap.parse_args()

    if args.timeline is not None:
        if args.timeline < 1:
            sys.exit("--timeline minutes must be >= 1")
        buckets = Counter()
        bucket_filtered = Counter()
        untimed = 0
        for domain, client, filtered, ts in iter_queries_timed(args.logfile):
            if args.client and client != args.client:
                continue
            if ts is None:
                untimed += 1
                continue
            epoch = int(ts.timestamp())
            buckets[epoch - (epoch % (args.timeline * 60))] += 1
            if filtered:
                bucket_filtered[epoch - (epoch % (args.timeline * 60))] += 1
        if not buckets:
            sys.exit("No timestamped queries found. --timeline needs an AdGuard Home JSON export.")
        print(f"Timeline: {args.timeline}-minute buckets (times in UTC)")
        print("bucket_start\ttotal\tfiltered\tunblocked")
        for bucket in sorted(buckets):
            stamp = datetime.fromtimestamp(bucket, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
            filt = bucket_filtered.get(bucket, 0)
            print(f"{stamp}\t{buckets[bucket]}\t{filt}\t{buckets[bucket] - filt}")
        if untimed:
            print(f"Entries without a timestamp (excluded): {untimed}")
        return

    counts = Counter()
    filtered_seen = set()
    for domain, client, filtered in iter_queries(args.logfile):
        if args.client and client != args.client:
            continue
        counts[domain] += 1
        if filtered:
            filtered_seen.add(domain)

    if not counts:
        sys.exit("No DNS queries found. Check the input format (see --help).")

    blocked = load_blocklist(args.blocklist) if args.blocklist else set()

    if args.rules:
        for domain, count in sorted(counts.items()):
            if count >= args.min_count and not is_blocked(domain, blocked):
                print(f"||{domain}^")
        return

    print("domain\tqueries\talready_blocked\tseen_filtered")
    for domain, count in counts.most_common():
        if count < args.min_count:
            continue
        print(f"{domain}\t{count}\t{'yes' if is_blocked(domain, blocked) else 'no'}"
              f"\t{'yes' if domain in filtered_seen else 'no'}")


if __name__ == "__main__":
    main()
