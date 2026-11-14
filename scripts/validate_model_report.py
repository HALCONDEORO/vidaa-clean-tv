#!/usr/bin/env python3
"""Validate a local model report JSON before review, not its factual truth.

Usage: python3 scripts/validate_model_report.py REPORT.json
Only the agreed fields are allowed. Common private identifiers are rejected,
but this is NOT a guarantee of anonymity: humans must review all prose/photos.
Passing validates structure only, never hardware compatibility or a claim.
Standard library only. No network access or writes.
"""
import argparse
from datetime import date
import ipaddress
import json
import re
import sys

PRIVATE = re.compile(
    r"(?:[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,})"
    r"|(?:\b(?:[0-9A-F]{2}[:-]){5}[0-9A-F]{2}\b)"
    r"|(?:\b[A-Z0-9_.-]+\.local\b)"
    r"|(?:\b\d{1,2}:\d{2}\b)"
    r"|(?:\b[0-9A-F]{24,}\b)", re.I)
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IPV6 = re.compile(r"[0-9A-Fa-f:.%]*:[0-9A-Fa-f:.%]+")


def private_text(text):
    if PRIVATE.search(text):
        return True
    for token in IPV4.findall(text) + IPV6.findall(text):
        try:
            ipaddress.ip_address(token.split("%", 1)[0])
            return True
        except ValueError:
            pass
    return False


def validate_report(data, today=None):
    """Return diagnostics containing only fixed schema paths, never input text."""
    errors = []
    today = today or date.today()
    if not isinstance(data, dict):
        return ["report: expected an object"]
    allowed = {"model", "region", "session_date", "firmware", "menus", "steps", "apps", "outcome"}
    if set(data) - allowed:
        errors.append("report: unknown fields are not allowed")

    def text(value, path, maximum=2000):
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            errors.append(path + ": expected nonempty text within the size limit")
            return
        if any(ord(c) < 32 and c not in "\n\t" for c in value):
            errors.append(path + ": unsupported control character")
        if private_text(value):
            errors.append(path + ": possible private identifier; remove before sharing")

    text(data.get("model"), "model", 60)
    if isinstance(data.get("model"), str) and len(data["model"].strip()) < 3:
        errors.append("model: minimum length is 3")
    for key in ("region", "firmware"):
        text(data.get(key), key, 120)
    stamp = data.get("session_date")
    try:
        if not isinstance(stamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp):
            raise ValueError
        if date.fromisoformat(stamp) > today:
            errors.append("session_date: must not be in the future")
    except ValueError:
        errors.append("session_date: expected a real YYYY-MM-DD date")
    menus = data.get("menus")
    if not isinstance(menus, list) or not 1 <= len(menus) <= 100:
        errors.append("menus: expected 1 to 100 paths")
    else:
        for index, value in enumerate(menus):
            text(value, f"menus[{index}]")
    steps = data.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        errors.append("steps: expected 1 to 100 logged steps")
    else:
        for index, row in enumerate(steps):
            path = f"steps[{index}]"
            if not isinstance(row, dict) or set(row) != {"step", "expected", "observed", "reverted"}:
                errors.append(path + ": expected exactly step, expected, observed, reverted")
                continue
            for key in ("step", "expected", "observed"):
                text(row[key], path + "." + key)
            if row["reverted"] not in ("yes", "no"):
                errors.append(path + ".reverted: expected yes or no")
    apps = data.get("apps", [])
    if not isinstance(apps, list) or len(apps) > 100:
        errors.append("apps: expected a list of at most 100 results")
    else:
        for index, row in enumerate(apps):
            path = f"apps[{index}]"
            if not isinstance(row, dict) or set(row) != {"app", "status", "notes"}:
                errors.append(path + ": expected exactly app, status, notes")
                continue
            text(row["app"], path + ".app", 120)
            text(row["notes"], path + ".notes")
            if row["status"] not in ("works", "broken", "untested"):
                errors.append(path + ".status: expected works, broken or untested")
    if "outcome" in data:
        text(data["outcome"], "outcome")
    return errors


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate field")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report")
    args = parser.parse_args()
    try:
        with open(args.report, encoding="utf-8") as stream:
            data = json.load(stream, object_pairs_hook=no_duplicate_keys)
        errors = validate_report(data)
    except (OSError, ValueError, RecursionError):
        parser.exit(1, "Cannot read report: check JSON, duplicate fields and local path.\n")
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print("Structure/privacy pattern checks passed. Human review and hardware evidence are still required.")


if __name__ == "__main__":
    main()
