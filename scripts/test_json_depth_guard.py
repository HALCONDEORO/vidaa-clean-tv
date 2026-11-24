#!/usr/bin/env python3
"""Independent depth-guard tests: JSON nested beyond the interpreter recursion
limit must degrade to the same safe outcomes as malformed JSON - no traceback
escaping to the CLI, no echo of input data. Offline, stdlib only."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classify_dns_log as cdl
import session_to_testing as stt

MARKER = "DEPTHGUARD-PRIVATE-9c41"
DEPTH = 2000  # safely above CPython's default recursion limit of 1000


def deep_json_document():
    # Valid-shaped AdGuard wrapper whose payload nests DEPTH levels deep.
    return '{"data": ' + "[" * DEPTH + MARKER + "]" * DEPTH + "}"


class TestClassifyDepthGuard(unittest.TestCase):
    def test_deep_json_is_not_a_crash(self):
        with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False) as fh:
            fh.write(deep_json_document())
            path = fh.name
        try:
            err = io.StringIO()
            with redirect_stderr(err):
                entries = list(cdl.iter_queries(path))
            self.assertEqual(entries, [])
            self.assertNotIn("Traceback", err.getvalue())
            self.assertNotIn(MARKER, err.getvalue())
        finally:
            os.unlink(path)

    def test_deep_jsonl_lines_already_guarded(self):
        # The JSONL path already caught RecursionError; pin that behavior so
        # a refactor cannot drop it.
        with tempfile.NamedTemporaryFile(
                "w", suffix=".jsonl", delete=False) as fh:
            fh.write("[" * DEPTH + MARKER + "]" * DEPTH + "\n")
            path = fh.name
        try:
            err = io.StringIO()
            with redirect_stderr(err):
                entries = list(cdl.iter_queries(path))
            self.assertEqual(entries, [])
            self.assertNotIn("Traceback", err.getvalue())
            self.assertNotIn(MARKER, err.getvalue())
        finally:
            os.unlink(path)


class TestSessionToTestingDepthGuard(unittest.TestCase):
    def test_deep_block_raises_validation_error(self):
        block = "```json\n" + deep_json_document() + "\n```"
        with self.assertRaises(stt.ValidationError) as ctx:
            stt.extract_json_block(block)
        self.assertNotIn(MARKER, str(ctx.exception))

    def test_moderate_nesting_still_parses(self):
        # The guard must not reject legitimate nesting depth.
        depth = 50
        doc = "[" * depth + json.dumps(MARKER) + "]" * depth
        report = stt.extract_json_block("```json\n" + doc + "\n```")
        node = report
        for _ in range(depth):
            node = node[0]
        self.assertEqual(node, MARKER)


if __name__ == "__main__":
    unittest.main()
