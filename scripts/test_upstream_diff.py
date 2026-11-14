#!/usr/bin/env python3
"""Tests for upstream_diff.py. Stdlib unittest, fully offline."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import upstream_diff


OLD = """! Title: upstream list
! Last modified: 2026-11-01
ads.example.com
||telemetry.example.org^
! disabled.example.net
promo.example.io
"""

NEW = """! Title: upstream list
! Last modified: 2026-11-11
ads.example.com
||telemetry.example.org^
! disabled.example.net
new-ad.example.com
||api.example.co^
"""


class ParseTests(unittest.TestCase):
    def test_active_and_disabled_split(self):
        active, disabled = upstream_diff.parse_blocklist(OLD)
        self.assertEqual(
            active,
            {"ads.example.com", "telemetry.example.org", "promo.example.io"},
        )
        self.assertEqual(disabled, {"disabled.example.net"})

    def test_tree_rule_extracts_bare_domain(self):
        active, _ = upstream_diff.parse_blocklist("||Example.COM^")
        self.assertEqual(active, {"example.com"})

    def test_junk_lines_ignored(self):
        active, disabled = upstream_diff.parse_blocklist(
            "\n! a comment\n   \n[Adblock Plus 2.0]\n"
        )
        self.assertEqual(active, set())
        self.assertEqual(disabled, set())


class SummarizeTests(unittest.TestCase):
    def _write(self, content):
        handle, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(handle, "w", encoding="utf-8") as fh:
            fh.write(content)
        self.addCleanup(os.unlink, path)
        return path

    def test_added_and_removed_reported(self):
        old_path = self._write(OLD)
        new_path = self._write(NEW)
        summary = upstream_diff.summarize(old_path, new_path)
        self.assertIn("Active before: 3; active now: 4", summary)
        self.assertIn("Added: 2; removed: 1", summary)
        self.assertIn("`new-ad.example.com`", summary)
        self.assertIn("`api.example.co`", summary)
        self.assertIn("`promo.example.io`", summary)

    def test_comment_only_change(self):
        path = self._write(OLD.replace("2026-11-01", "2026-11-02"))
        same = self._write(OLD)
        summary = upstream_diff.summarize(same, path)
        self.assertIn("No domain changes", summary)


if __name__ == "__main__":
    unittest.main()
