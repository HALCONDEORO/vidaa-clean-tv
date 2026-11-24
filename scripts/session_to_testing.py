#!/usr/bin/env python3
"""Convert a filled hardware session log into TESTING.md rows.

Reads a copy of docs/templates/session-log.md, extracts the fenced JSON
block, validates it against the single shared model-report contract
(scripts/validate_model_report.py) and prints Markdown rows for the
session-log table in TESTING.md. With --json it prints the normalized
report instead, the same format community model reports use.

Stdlib only, fully offline: the script never touches the network.

Usage:
    python3 scripts/session_to_testing.py my-session.md
    python3 scripts/session_to_testing.py my-session.md --json
"""

import argparse
import json
import re
import sys

from validate_model_report import (
    no_duplicate_keys,
    validate_report as shared_validate_report,
)

REQUIRED_FIELDS = ("model", "region", "session_date", "firmware", "menus", "steps")
# session_type is accepted in the template for human context; the
# normalized report drops it because the shared schema has no such field.
SESSION_TYPES = ("settings", "dns-filtering", "local-control", "mixed")


class ValidationError(Exception):
    pass


def extract_json_block(text):
    """Return the parsed JSON from the first ```json fenced block."""
    match = re.search(r"```json\s*\n(.*?)```", text, re.DOTALL)
    if not match:
        raise ValidationError("no ```json fenced block found in the file")
    try:
        return json.loads(match.group(1), object_pairs_hook=no_duplicate_keys)
    except (ValueError, RecursionError):
        # Neutral on purpose: never echo the offending key or value.
        raise ValidationError("the JSON block does not parse or repeats a field")


def validate_report(report):
    """Validate against the shared contract. Raises ValidationError.

    session_type is template-only human context: it is checked here and
    stripped before the shared validator sees the report, so the converter
    and the standalone validator can never diverge. Diagnostics carry fixed
    schema paths only, never input text.
    """
    if not isinstance(report, dict):
        raise ValidationError("the JSON block must be an object")
    report = dict(report)
    session_type = report.pop("session_type", None)
    if session_type is not None and session_type not in SESSION_TYPES:
        raise ValidationError("session_type: expected one of: " + ", ".join(SESSION_TYPES))
    diagnostics = shared_validate_report(report)
    if diagnostics:
        raise ValidationError("; ".join(diagnostics))
    return report


def _cell(text):
    """Render a logged string as inert literal text in a Markdown table cell.

    The cell ends up in a Jekyll-rendered page, and kramdown passes raw
    HTML through, so logged text must be neutralized: HTML metacharacters
    become entities and the Markdown constructs that could form links,
    code spans or emphasis are backslash-escaped. Control characters are
    already rejected by the shared validator before this point.
    """
    text = text.replace("\r", " ").replace("\n", " ").strip()
    text = text.replace("\\", "\\\\")
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    for char in ("|", "[", "]", "`", "*", "_"):
        text = text.replace(char, "\\" + char)
    return text


def to_testing_rows(report):
    """Return Markdown rows for the TESTING.md session-log table."""
    rows = []
    for step in report["steps"]:
        rows.append(
            "| %s | %s | %s | %s | %s | %s | %s |"
            % (
                _cell(report["session_date"]),
                _cell(report["model"]),
                _cell(report["firmware"]),
                _cell(step["step"]),
                _cell(step["expected"]),
                _cell(step["observed"]),
                _cell(step["reverted"]),
            )
        )
    return rows


def to_normalized_report(report):
    """Return the normalized report for validate_model_report.py."""
    normalized = {
        "model": report["model"].strip(),
        "region": report["region"].strip(),
        "session_date": report["session_date"],
        "firmware": report["firmware"].strip(),
        "menus": [m.strip() for m in report["menus"]],
        "steps": [
            {
                "step": s["step"].strip(),
                "expected": s["expected"].strip(),
                "observed": s["observed"].strip(),
                "reverted": s["reverted"],
            }
            for s in report["steps"]
        ],
    }
    if report.get("apps"):
        normalized["apps"] = report["apps"]
    if report.get("outcome"):
        normalized["outcome"] = report["outcome"].strip()
    return normalized


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("session_log", help="filled copy of docs/templates/session-log.md")
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the normalized model report JSON instead of TESTING.md rows",
    )
    args = parser.parse_args(argv)
    try:
        with open(args.session_log, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        print("error: cannot read the session log file", file=sys.stderr)
        return 2
    try:
        report = validate_report(extract_json_block(text))
    except ValidationError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(to_normalized_report(report), indent=2, ensure_ascii=False))
    else:
        for row in to_testing_rows(report):
            print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
