#!/usr/bin/env python3
"""validate_blocklist.py - validate an AdGuard-format blocklist.

Part of VIDAA Clean TV. Standard library only, no network access.

Checks:
  - every non-comment line is a well-formed AdGuard rule (||domain^) or a
    plain hostname
  - no duplicate rules
  - optionally, no overlap with an upstream list (--upstream FILE)

Exit code 0 when valid, 1 with diagnostics otherwise.

Usage:
  python3 validate_blocklist.py LIST [--upstream UPSTREAM_LIST]
"""

import argparse
import re
import sys

ADGUARD_RULE_RE = re.compile(r"^\|\|([A-Za-z0-9*_.-]+)\^$")
HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?\.)+[A-Za-z]{2,63}$")


def load_rules(path):
    """Return (rules, errors): rules as list of (lineno, raw, domain)."""
    rules, errors = [], []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith(("!", "#", "[", "//")):
                continue
            m = ADGUARD_RULE_RE.match(line)
            # Check label structure without dropping supported wildcard patterns.
            if m and HOSTNAME_RE.fullmatch(m.group(1).replace("*", "a")):
                rules.append((lineno, line, m.group(1).lower()))
            elif HOSTNAME_RE.fullmatch(line):
                rules.append((lineno, line, line.lower()))
            else:
                errors.append(f"line {lineno}: not a valid rule or hostname: {line!r}")
    return rules, errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("listfile", help="Blocklist to validate (AdGuard format or plain hostnames)")
    ap.add_argument("--upstream", help="Upstream list; rules duplicated there are reported as errors")
    args = ap.parse_args()

    rules, errors = load_rules(args.listfile)

    seen = {}
    for lineno, raw, domain in rules:
        if domain in seen:
            errors.append(f"line {lineno}: duplicate of line {seen[domain]}: {raw!r}")
        else:
            seen[domain] = lineno

    if args.upstream:
        upstream_rules, upstream_errors = load_rules(args.upstream)
        errors.extend(f"upstream: {e}" for e in upstream_errors)
        upstream_domains = {domain for _, _, domain in upstream_rules}
        for lineno, raw, domain in rules:
            if domain in upstream_domains:
                errors.append(f"line {lineno}: already covered by upstream: {raw!r}")

    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK {args.listfile}: {len(rules)} rules valid")


if __name__ == "__main__":
    main()
