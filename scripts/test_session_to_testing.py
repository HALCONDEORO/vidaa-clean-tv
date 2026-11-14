#!/usr/bin/env python3
"""Tests for session_to_testing.py. Stdlib unittest, fully offline."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import session_to_testing as stt


VALID_REPORT = {
    "model": "Toshiba 50UV1553DB",
    "region": "Spain",
    "session_date": "2026-11-14",
    "firmware": "V0000.01.00a.L0923",
    "menus": ["Settings > System > About"],
    "session_type": "settings",
    "steps": [
        {
            "step": "Settings > Privacy > Content recognition set to Off",
            "expected": "Home screen recommendations stop changing",
            "observed": "Setting accepted; home screen unchanged after 10 minutes",
            "reverted": "no",
        },
        {
            "step": "Subscribed router filter to the upstream blocklist",
            "expected": "Ad domains fail to resolve",
            "observed": "Query log shows blocked ad domains; YouTube plays",
            "reverted": "no",
        },
    ],
    "apps": [
        {"app": "YouTube", "status": "works", "notes": "Playback fine"},
        {"app": "Netflix", "status": "untested", "notes": ""},
    ],
    "outcome": "Ads reduced on home screen; no app breakage seen",
}


def md_with_report(report):
    return "# Session\n\n```json\n%s\n```\n" % json.dumps(report, indent=2)


class ExtractTests(unittest.TestCase):
    def test_extracts_json_block(self):
        report = stt.extract_json_block(md_with_report(VALID_REPORT))
        self.assertEqual(report["model"], "Toshiba 50UV1553DB")

    def test_missing_block_fails(self):
        with self.assertRaises(stt.ValidationError):
            stt.extract_json_block("# no block here\n")

    def test_broken_json_fails(self):
        with self.assertRaises(stt.ValidationError):
            stt.extract_json_block("```json\n{not json}\n```\n")


class ValidateTests(unittest.TestCase):
    def test_valid_report_passes(self):
        stt.validate_report(dict(VALID_REPORT))

    def test_missing_required_field_fails(self):
        for field in stt.REQUIRED_FIELDS:
            report = dict(VALID_REPORT)
            report[field] = "" if field != "menus" else []
            with self.assertRaises(stt.ValidationError, msg=field):
                stt.validate_report(report)

    def test_future_date_fails(self):
        report = dict(VALID_REPORT, session_date="2999-01-01")
        with self.assertRaises(stt.ValidationError):
            stt.validate_report(report)

    def test_bad_date_format_fails(self):
        report = dict(VALID_REPORT, session_date="14/11/2026")
        with self.assertRaises(stt.ValidationError):
            stt.validate_report(report)

    def test_bad_reverted_value_fails(self):
        report = dict(VALID_REPORT)
        report["steps"] = [dict(VALID_REPORT["steps"][0], reverted="maybe")]
        with self.assertRaises(stt.ValidationError):
            stt.validate_report(report)

    def test_bad_app_status_fails(self):
        report = dict(VALID_REPORT)
        report["apps"] = [{"app": "YouTube", "status": "fine", "notes": ""}]
        with self.assertRaises(stt.ValidationError):
            stt.validate_report(report)

    def test_bad_session_type_fails(self):
        report = dict(VALID_REPORT, session_type="everything")
        with self.assertRaises(stt.ValidationError):
            stt.validate_report(report)

    def test_private_data_rejected(self):
        bad_values = [
            "TV at 192.168.1.50 refused the setting",
            "seen from fe80::1 on the LAN",
            "MAC 3C:6A:9D:12:34:56",
            "contact me at owner@example.com",
            "router box fritz.local",
            "changed at 21:45 exactly",
            "token a1b2c3d4e5f60718293a4b5c",
        ]
        for value in bad_values:
            report = dict(VALID_REPORT, outcome=value)
            with self.assertRaises(stt.ValidationError, msg=value):
                stt.validate_report(report)


class OutputTests(unittest.TestCase):
    def test_testing_rows_match_table_shape(self):
        rows = stt.to_testing_rows(stt.validate_report(dict(VALID_REPORT)))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row.count("|"), 8)  # 7 columns
        self.assertIn("2026-11-14", rows[0])
        self.assertIn("Toshiba 50UV1553DB", rows[0])
        self.assertIn("V0000.01.00a.L0923", rows[0])

    def test_pipes_and_newlines_escaped(self):
        report = dict(VALID_REPORT)
        report["steps"] = [
            dict(VALID_REPORT["steps"][0], observed="a | b\nc")
        ]
        rows = stt.to_testing_rows(report)
        self.assertIn("a \\| b c", rows[0])

    def test_normalized_report_roundtrip(self):
        report = stt.validate_report(dict(VALID_REPORT))
        normalized = stt.to_normalized_report(report)
        stt.validate_report(normalized)  # still valid
        self.assertEqual(normalized["apps"][0]["status"], "works")


class CliTests(unittest.TestCase):
    def _write(self, content):
        handle, path = tempfile.mkstemp(suffix=".md")
        with os.fdopen(handle, "w", encoding="utf-8") as fh:
            fh.write(content)
        self.addCleanup(os.unlink, path)
        return path

    def test_cli_rows(self):
        path = self._write(md_with_report(VALID_REPORT))
        self.assertEqual(stt.main([path]), 0)

    def test_cli_json(self):
        path = self._write(md_with_report(VALID_REPORT))
        self.assertEqual(stt.main([path, "--json"]), 0)

    def test_cli_invalid_returns_1(self):
        path = self._write("# nothing\n")
        self.assertEqual(stt.main([path]), 1)

    def test_cli_missing_file_returns_2(self):
        self.assertEqual(stt.main(["/nonexistent/session.md"]), 2)


if __name__ == "__main__":
    unittest.main()
