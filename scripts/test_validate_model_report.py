import contextlib
import copy
from datetime import date
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import validate_model_report as v


class TestModelReport(unittest.TestCase):
    def fixture(self):
        return json.loads((Path(__file__).resolve().parent.parent /
                           "examples/model-report.example.json").read_text())

    def test_example_and_optional_fields(self):
        data = self.fixture()
        self.assertEqual(v.validate_report(data), [])
        del data["apps"]
        del data["outcome"]
        self.assertEqual(v.validate_report(data), [])

    def test_required_types_values_and_limits(self):
        for key, value in (("model", "a"), ("model", "x" * 61), ("region", ""),
                           ("firmware", None), ("menus", []), ("menus", "menu"),
                           ("steps", []), ("steps", [None]), ("apps", [{}]),
                           ("session_date", "2026-02-30"),
                           ("session_date", "2026-1-01"), ("session_date", "2027-01-01")):
            data = self.fixture()
            data[key] = value
            with self.subTest(key=key, value=value):
                self.assertTrue(v.validate_report(data, today=date(2026, 11, 14)))
        for key in ("model", "region", "firmware", "menus", "steps", "session_date"):
            data = self.fixture()
            del data[key]
            self.assertTrue(v.validate_report(data))

    def test_reverted_and_app_states_are_strict(self):
        for value in (True, "Yes", "unknown", {}, []):
            data = self.fixture()
            data["steps"][0]["reverted"] = value
            self.assertTrue(v.validate_report(data))
            data = self.fixture()
            data["apps"][0]["status"] = value
            self.assertTrue(v.validate_report(data))
        for value in ("works", "broken", "untested"):
            data = self.fixture()
            data["apps"][0]["status"] = value
            self.assertEqual(v.validate_report(data), [])

    def test_private_patterns_every_free_text_location(self):
        private = ["192.0.2.15", "[2001:db8::1]", "::1", "fe80::abcd%en0",
                   "AA:BB:CC:DD:EE:FF", "aa-bb-cc-dd-ee-ff", "person@example.com",
                   "tv.local", "08:45", "a" * 40]
        paths = [("model",), ("region",), ("firmware",), ("menus", 0),
                 ("steps", 0, "step"), ("steps", 0, "expected"),
                 ("steps", 0, "observed"), ("apps", 0, "app"),
                 ("apps", 0, "notes"), ("outcome",)]
        for value in private:
            for path in paths:
                data = self.fixture()
                target = data
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = "Value " + value
                with self.subTest(value=value, path=path):
                    errors = v.validate_report(data)
                    self.assertTrue(errors)
                    self.assertTrue(any("private identifier" in e for e in errors))
                    self.assertNotIn(value, " ".join(errors))

    def test_no_private_unknown_field_names_in_errors(self):
        data = self.fixture()
        data["SECRET-person@example.com"] = "anything"
        errors = v.validate_report(data)
        self.assertTrue(errors)
        self.assertNotIn("SECRET", " ".join(errors))
        data = self.fixture()
        data["steps"][0]["private"] = "192.0.2.1"
        self.assertTrue(v.validate_report(data))

    def test_cli_status_no_traceback_or_private_echo(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            for text, valid in ((json.dumps(self.fixture()), True),
                                ('{"model":"SECRET","model":"again"}', False),
                                ('{"SECRET":', False), ('[]', False)):
                path.write_text(text)
                with patch("sys.argv", ["validate_model_report.py", str(path)]), \
                        contextlib.redirect_stdout(io.StringIO()) as out, \
                        contextlib.redirect_stderr(io.StringIO()) as err:
                    if valid:
                        v.main()
                        self.assertIn("Human review", out.getvalue())
                    else:
                        with self.assertRaises(SystemExit) as ctx:
                            v.main()
                        self.assertEqual(ctx.exception.code, 1)
                        self.assertEqual(out.getvalue(), "")
                    self.assertNotIn("SECRET", err.getvalue())
                    self.assertNotIn("Traceback", err.getvalue())


if __name__ == "__main__":
    unittest.main()
