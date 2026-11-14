import contextlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import redact_dns_log as r
import classify_dns_log as c


class TestRedactor(unittest.TestCase):
    def fixture(self):
        return {"password": "TOP-SECRET", "oldest": "PRIVATE-TIME", "data": [
            {"question": {"name": "PRIVATE.example.com", "type": "SECRET"},
             "client": "192.0.2.1", "time": "PRIVATE-TIME", "reason": "FilteredBlocklist",
             "answer": [{"value": "SECRET"}], "extra": "TOP-SECRET"},
            {"question": {"name": "private.EXAMPLE.com."}, "reason": "NotFiltered"},
            {"question": {"name": "other.example.net"}, "reason": "FilteredPRIVATE"}]}

    def test_allowlist_only_and_consistent_aliases(self):
        result = r.redact(self.fixture())
        self.assertEqual(result, {"data": [
            {"question": {"name": "domain-000001.invalid"}, "reason": "Filtered"},
            {"question": {"name": "domain-000001.invalid"}, "reason": "NotFiltered"},
            {"question": {"name": "domain-000002.invalid"}, "reason": "Filtered"}]})
        self.assertNotIn("PRIVATE", json.dumps(result))
        self.assertEqual(r.redact({"data": [{"question": {"name": "new.example.net"}}]})
                         ["data"][0]["question"]["name"], "domain-000001.invalid")

    def test_reject_bad_records_instead_of_silent_loss(self):
        for value in ([], {}, {"data": {}}, {"data": [None]},
                      {"data": [{"question": {"name": "private..example.com"}}]},
                      {"data": [{"question": {"name": "good.example.com"}, "reason": {}}]}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                r.redact(value)
        self.assertEqual(r.redact({"data": []}), {"data": []})

    def invoke(self, source, output):
        with patch("sys.argv", ["redact_dns_log.py", str(source), "-o", str(output)]):
            r.main()

    def test_cli_private_output_original_intact_and_classifier_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "private.json"
            output = Path(directory) / "share.json"
            source.write_text(json.dumps(self.fixture()))
            before = source.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                self.invoke(source, output)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(list(c.iter_queries(str(output))), [
                ("domain-000001.invalid", "", True),
                ("domain-000001.invalid", "", False),
                ("domain-000002.invalid", "", True)])
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.invoke(source, source)
            self.assertEqual(source.read_bytes(), before)

    def test_alias_paths_cannot_overwrite_original(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "private.json"
            source.write_text(json.dumps(self.fixture()))
            for kind in ("symlink", "hardlink"):
                dest = Path(directory) / kind
                try:
                    (dest.symlink_to(source) if kind == "symlink" else os.link(source, dest))
                except OSError:
                    continue
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    self.invoke(source, dest)
                self.assertIn("TOP-SECRET", source.read_text())

    def test_write_failure_keeps_existing_destination_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "private.json"
            output = Path(directory) / "share.json"
            source.write_text(json.dumps(self.fixture()))
            output.write_text("previous")
            with patch("fetch_query_log.os.replace", side_effect=OSError("TOP-SECRET")), \
                    contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit):
                self.invoke(source, output)
            self.assertNotIn("TOP-SECRET", err.getvalue())
            self.assertEqual(output.read_text(), "previous")
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["private.json", "share.json"])


if __name__ == "__main__":
    unittest.main()
