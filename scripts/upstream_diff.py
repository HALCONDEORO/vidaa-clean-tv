#!/usr/bin/env python3
"""Summarize the difference between two upstream blocklist snapshots.

Reads two AdGuard-syntax blocklists (old and new) and prints a short
Markdown summary: active domains added, removed and still disabled.
Used by the upstream-watch workflow; also runnable by hand. Stdlib only,
no network access: fetching the snapshots is the caller's job.

Usage:
    python3 scripts/upstream_diff.py old.txt new.txt
"""

import argparse
import sys


def parse_blocklist(text):
    """Split a blocklist into (active domains, disabled domains).

    Active lines carry a plain domain or an ||domain^ rule; comment lines
    starting with '!' and lines disabled with a leading '! ' or prefixed
    by '# ' count as disabled. Everything else (blank lines, headers) is
    ignored, matching the semantics documented in docs/02-dns-filtering.md.
    """
    active = set()
    disabled = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("!") or line.startswith("#"):
            candidate = line.lstrip("!# ").strip()
            domain = _extract_domain(candidate)
            if domain:
                disabled.add(domain)
            continue
        domain = _extract_domain(line)
        if domain:
            active.add(domain)
    return active, disabled


def _extract_domain(line):
    """Return the bare domain from a plain or ||domain^ rule, else None.

    Adblock options (``||domain^$client=...``) are rejected loudly instead
    of being mangled into a literal fake domain: scoping rules change what
    a line means, and guessing would falsify the diff.
    """
    if line.startswith("||"):
        host = line[2:].rstrip("^").strip()
    else:
        host = line.strip()
    if "$" in host:
        raise ValueError("unsupported rule syntax: scoped Adblock options")
    if not host or " " in host or "/" in host:
        return None
    if "." not in host:
        return None
    return host.lower()


def summarize(old_path, new_path):
    with open(old_path, "r", encoding="utf-8") as handle:
        old_active, old_disabled = parse_blocklist(handle.read())
    with open(new_path, "r", encoding="utf-8") as handle:
        new_active, new_disabled = parse_blocklist(handle.read())

    added = sorted(new_active - old_active)
    removed = sorted(old_active - new_active)
    lines = [
        "### Upstream blocklist diff",
        "",
        "- Active before: %d; active now: %d; disabled now: %d"
        % (len(old_active), len(new_active), len(new_disabled)),
        "- Added: %d; removed: %d" % (len(added), len(removed)),
        "",
    ]
    if added:
        lines.append("**Added domains**")
        lines.extend("- `%s`" % domain for domain in added[:50])
        if len(added) > 50:
            lines.append("- ... and %d more" % (len(added) - 50))
        lines.append("")
    if removed:
        lines.append("**Removed domains**")
        lines.extend("- `%s`" % domain for domain in removed[:50])
        if len(removed) > 50:
            lines.append("- ... and %d more" % (len(removed) - 50))
        lines.append("")
    if not added and not removed:
        lines.append("No domain changes; only comments or ordering changed.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("old", help="previous snapshot")
    parser.add_argument("new", help="current snapshot")
    args = parser.parse_args(argv)
    try:
        print(summarize(args.old, args.new))
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
