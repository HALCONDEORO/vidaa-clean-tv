#!/usr/bin/env python3
"""Create a minimal, pseudonymized AdGuard JSON log locally.

Usage: python3 scripts/redact_dns_log.py PRIVATE.json -o SHARE.json
Domains become file-local .invalid aliases. Client IDs, timestamps, answers and
all other metadata are discarded. Counts/order still reveal usage patterns.
This is NOT anonymous data or original hardware evidence. Review before sharing.
The original is never overwritten. No network requests are made.
"""
import argparse
import json
import os
import sys

from classify_dns_log import DOMAIN_RE, norm
from fetch_query_log import write_private_export


def redact(data):
    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise ValueError("Expected an AdGuard object with a data list")
    aliases = {}
    result = []
    for index, entry in enumerate(data["data"], 1):
        if not isinstance(entry, dict) or not isinstance(entry.get("question"), dict):
            raise ValueError(f"Entry {index}: expected a question object")
        name = entry["question"].get("name")
        reason = entry.get("reason", "")
        if (not isinstance(name, str) or not DOMAIN_RE.fullmatch(name.strip())
                or not isinstance(reason, str)):
            raise ValueError(f"Entry {index}: unsupported domain or reason type")
        name = norm(name)
        if name not in aliases:
            aliases[name] = f"domain-{len(aliases) + 1:06d}.invalid"
        result.append({"question": {"name": aliases[name]},
                       "reason": "Filtered" if reason.startswith("Filtered") else "NotFiltered"})
    return {"data": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Private AdGuard JSON export")
    parser.add_argument("-o", "--output", required=True, help="New local JSON file, not the original")
    args = parser.parse_args()
    try:
        if (os.path.realpath(args.input) == os.path.realpath(args.output)
                or (os.path.exists(args.output) and os.path.samefile(args.input, args.output))):
            parser.exit(1, "Refusing to overwrite the original export. Choose another output.\n")
        with open(args.input, encoding="utf-8") as stream:
            data = json.load(stream)
        output = redact(data)
        write_private_export(args.output, output)
    except (OSError, ValueError, RecursionError):
        parser.exit(1, "Cannot sanitize export. Check JSON structure and local paths; no input values are shown.\n")
    print("Wrote a minimal pseudonymized log. Counts/order remain sensitive; review before sharing.")


if __name__ == "__main__":
    main()
