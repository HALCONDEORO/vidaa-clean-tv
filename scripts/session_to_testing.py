#!/usr/bin/env python3
"""Convert a filled hardware session log into TESTING.md rows.

Reads a copy of docs/templates/session-log.md, extracts the fenced JSON
block, validates it against the shared model-report shape and prints
Markdown rows for the session-log table in TESTING.md. With --json it
prints the normalized report instead, the same format community model
reports use (scripts/validate_model_report.py).

Stdlib only, fully offline: the script never touches the network.

Usage:
    python3 scripts/session_to_testing.py my-session.md
    python3 scripts/session_to_testing.py my-session.md --json
"""

import argparse
import datetime
import json
import re
import sys

REQUIRED_FIELDS = ("model", "region", "session_date", "firmware", "menus", "steps")
# session_type is accepted in the template for human context; the
# normalized report drops it because the shared schema has no such field.
ALLOWED_FIELDS = set(REQUIRED_FIELDS) | {"apps", "outcome", "session_type"}
REVERTED_VALUES = ("yes", "no")
APP_STATUS_VALUES = ("works", "broken", "untested")
SESSION_TYPES = ("settings", "dns-filtering", "local-control", "mixed")
MAX_LIST_ITEMS = 100
MAX_FIELD_CHARS = 120
MAX_FREE_CHARS = 2000


def _no_duplicates(pairs):
    """object_pairs_hook that rejects duplicate JSON keys."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate JSON key: %s" % key)
        result[key] = value
    return result

# Patterns that would leak private or machine-identifying data into a
# shareable log. Keep in sync with scripts/validate_model_report.py.
PRIVATE_PATTERNS = (
    ("IP address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("IPv6 address", re.compile(r"\b(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F]{0,4}\b")),
    ("MAC address", re.compile(r"\b[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\b")),
    ("email address", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
    ("local hostname", re.compile(r"\b[\w-]+\.(?:local|lan|home|internal)\b", re.IGNORECASE)),
    ("exact time", re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")),
    ("long hex token", re.compile(r"\b[0-9a-fA-F]{24,}\b")),
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(Exception):
    pass


def extract_json_block(text):
    """Return the parsed JSON from the first ```json fenced block."""
    match = re.search(r"```json\s*\n(.*?)```", text, re.DOTALL)
    if not match:
        raise ValidationError("no ```json fenced block found in the file")
    try:
        return json.loads(match.group(1), object_pairs_hook=_no_duplicates)
    except json.JSONDecodeError as exc:
        raise ValidationError("the JSON block does not parse: %s" % exc)


def _check_no_private_data(value, trail="report"):
    if isinstance(value, str):
        for label, pattern in PRIVATE_PATTERNS:
            if pattern.search(value):
                raise ValidationError("%s contains what looks like a %s" % (trail, label))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _check_no_private_data(item, "%s[%d]" % (trail, index))
    elif isinstance(value, dict):
        for key, item in value.items():
            _check_no_private_data(item, "%s.%s" % (trail, key))


def validate_report(report):
    """Validate the shared model-report shape. Raises ValidationError."""
    if not isinstance(report, dict):
        raise ValidationError("the JSON block must be an object")
    unknown = set(report) - ALLOWED_FIELDS
    if unknown:
        raise ValidationError("unknown fields: %s" % ", ".join(sorted(unknown)))
    for field in REQUIRED_FIELDS:
        value = report.get(field)
        if value in (None, "", []):
            raise ValidationError("missing required field: %s" % field)
    if not isinstance(report["model"], str) or not (3 <= len(report["model"]) <= 60):
        raise ValidationError("model must be a string of 3-60 characters")
    if (
        not isinstance(report["region"], str)
        or not report["region"].strip()
        or len(report["region"]) > MAX_FIELD_CHARS
    ):
        raise ValidationError(
            "region must be a non-empty string of at most %d characters" % MAX_FIELD_CHARS
        )
    date = report["session_date"]
    if not isinstance(date, str) or not DATE_RE.match(date):
        raise ValidationError("session_date must be YYYY-MM-DD")
    try:
        parsed = datetime.date.fromisoformat(date)
    except ValueError:
        raise ValidationError("session_date is not a real date: %s" % date)
    if parsed > datetime.date.today():
        raise ValidationError("session_date is in the future: %s" % date)
    if (
        not isinstance(report["firmware"], str)
        or not report["firmware"].strip()
        or len(report["firmware"]) > MAX_FIELD_CHARS
    ):
        raise ValidationError(
            "firmware must be a non-empty string of at most %d characters" % MAX_FIELD_CHARS
        )
    if not isinstance(report["menus"], list) or not all(
        isinstance(m, str) and m.strip() and len(m) <= MAX_FREE_CHARS for m in report["menus"]
    ):
        raise ValidationError("menus must be a list of non-empty strings")
    if len(report["menus"]) > MAX_LIST_ITEMS:
        raise ValidationError("menus has too many entries (max %d)" % MAX_LIST_ITEMS)
    session_type = report.get("session_type")
    if session_type is not None and session_type not in SESSION_TYPES:
        raise ValidationError(
            "session_type must be one of: %s" % ", ".join(SESSION_TYPES)
        )
    steps = report["steps"]
    if not isinstance(steps, list) or not steps:
        raise ValidationError("steps must be a non-empty list")
    if len(steps) > MAX_LIST_ITEMS:
        raise ValidationError("steps has too many entries (max %d)" % MAX_LIST_ITEMS)
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValidationError("steps[%d] must be an object" % index)
        for key in ("step", "expected", "observed"):
            if not isinstance(step.get(key), str) or not step[key].strip():
                raise ValidationError("steps[%d].%s must be a non-empty string" % (index, key))
        if step.get("reverted") not in REVERTED_VALUES:
            raise ValidationError(
                "steps[%d].reverted must be yes or no" % index
            )
    apps = report.get("apps", [])
    if not isinstance(apps, list):
        raise ValidationError("apps must be a list")
    if len(apps) > MAX_LIST_ITEMS:
        raise ValidationError("apps has too many entries (max %d)" % MAX_LIST_ITEMS)
    for index, app in enumerate(apps):
        if not isinstance(app, dict):
            raise ValidationError("apps[%d] must be an object" % index)
        for key in ("app", "status", "notes"):
            if not isinstance(app.get(key), str) or not app[key].strip():
                raise ValidationError(
                    "apps[%d].%s must be a non-empty string (use 'Not tested' for untested)"
                    % (index, key)
                )
        if len(app["app"]) > MAX_FIELD_CHARS:
            raise ValidationError("apps[%d].app is too long" % index)
        if app["status"] not in APP_STATUS_VALUES:
            raise ValidationError(
                "apps[%d].status must be one of: %s"
                % (index, ", ".join(APP_STATUS_VALUES))
            )
    outcome = report.get("outcome")
    if outcome is not None and (
        not isinstance(outcome, str) or len(outcome) > MAX_FREE_CHARS
    ):
        raise ValidationError(
            "outcome must be a string of at most %d characters" % MAX_FREE_CHARS
        )
    _check_no_private_data(report)
    return report


def _cell(text):
    """Make a string safe for a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


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
    # session_type is human context for the log file only; the shared
    # model-report schema has no such field and validators reject unknowns.
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
    except OSError as exc:
        print("error: cannot read %s: %s" % (args.session_log, exc.strerror), file=sys.stderr)
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
