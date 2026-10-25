#!/usr/bin/env python3
"""Offline test suite for classify_dns_log.py. Run: python3 -m unittest scripts.test_classify_dns_log
or directly: python3 scripts/test_classify_dns_log.py"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classify_dns_log as m

ADGUARD_LOG = {
    "oldest": "",
    "data": [
        {"question": {"class": "IN", "name": "ads.vidaa.com.", "type": "A"},
         "client": "192.168.1.50", "reason": "NotFilteredNotFound"},
        {"question": {"class": "IN", "name": "ads.vidaa.com.", "type": "A"},
         "client": "192.168.1.50", "reason": "FilteredBlackList"},
        {"question": {"class": "IN", "name": "www.youtube.com.", "type": "A"},
         "client": "192.168.1.50", "reason": "NotFilteredNotFound"},
        {"question": {"class": "IN", "name": "telemetry.example.net.", "type": "A"},
         "client": "192.168.1.50", "reason": "NotFilteredNotFound"},
        {"question": {"class": "IN", "name": "other-device.example.com.", "type": "A"},
         "client": "192.168.1.99", "reason": "NotFilteredNotFound"},
        {"question": None, "client": "192.168.1.50", "reason": "NotFilteredNotFound"},
        {"question": {"name": None}, "client": "192.168.1.50", "reason": "NotFilteredNotFound"},
        {"question": {"name": "clientinfo.example.com."}, "client": None,
         "client_info": None, "reason": None},
    ],
}

DNSMASQ_LOG = (
    "Oct 25 09:00:01 dnsmasq[123]: query[A] foo.vidaa.com from 192.168.1.50\n"
    "Oct 25 09:00:02 dnsmasq[123]: query[A] foo.vidaa.com from 192.168.1.50\n"
    "Oct 25 09:00:03 dnsmasq[123]: query[A] bar.metrics.io from 192.168.1.50\n"
)

BLOCKLIST = "||ads.vidaa.com^\n! comment\nblocked.example.net\n"


class TempFileMixin:
    def write_tmp(self, content):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as fh:
            fh.write(content)
        self.addCleanup(os.unlink, path)
        return path


class TestInputs(TempFileMixin, unittest.TestCase):
    def test_adguard_json_aggregation(self):
        path = self.write_tmp(json.dumps(ADGUARD_LOG))
        rows = list(m.iter_queries(path))
        self.assertEqual(len(rows), 6)  # two malformed entries skipped
        self.assertEqual(rows[0], ("ads.vidaa.com", "192.168.1.50", False))
        self.assertEqual(rows[1], ("ads.vidaa.com", "192.168.1.50", True))

    def test_null_question_does_not_crash(self):
        # Regression: an AdGuard export entry with "question": null raised
        # AttributeError before the fix.
        path = self.write_tmp(json.dumps({"data": [{"question": None}]}))
        self.assertEqual(list(m.iter_queries(path)), [])

    def test_null_client_and_reason(self):
        path = self.write_tmp(json.dumps(ADGUARD_LOG))
        rows = [r for r in m.iter_queries(path) if r[0] == "clientinfo.example.com"]
        self.assertEqual(rows, [("clientinfo.example.com", "", False)])

    def test_dnsmasq_parsing(self):
        path = self.write_tmp(DNSMASQ_LOG)
        rows = list(m.iter_queries(path))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], ("foo.vidaa.com", "192.168.1.50", False))

    def test_plain_domain_list(self):
        path = self.write_tmp("plain.example.org\nwww.youtube.com\n")
        rows = list(m.iter_queries(path))
        self.assertEqual([r[0] for r in rows], ["plain.example.org", "www.youtube.com"])


class TestBlocklist(TempFileMixin, unittest.TestCase):
    def test_load_adguard_and_plain(self):
        path = self.write_tmp(BLOCKLIST)
        self.assertEqual(m.load_blocklist(path), {"ads.vidaa.com", "blocked.example.net"})

    def test_exact_and_subdomain_match(self):
        blocked = {"blocked.example.net"}
        self.assertTrue(m.is_blocked("blocked.example.net", blocked))
        self.assertTrue(m.is_blocked("sub.blocked.example.net", blocked))
        self.assertFalse(m.is_blocked("notblocked.example.net", blocked))
        self.assertFalse(m.is_blocked("example.net", blocked))


class TestCli(TempFileMixin, unittest.TestCase):
    def run_cli(self, argv):
        buf = io.StringIO()
        argv0 = sys.argv
        sys.argv = ["classify_dns_log.py"] + argv
        try:
            with redirect_stdout(buf):
                m.main()
        finally:
            sys.argv = argv0
        return buf.getvalue()

    def test_report_with_client_filter_and_blocklist(self):
        log = self.write_tmp(json.dumps(ADGUARD_LOG))
        bl = self.write_tmp(BLOCKLIST)
        out = self.run_cli([log, "--client", "192.168.1.50", "--blocklist", bl])
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "domain\tqueries\talready_blocked\tseen_filtered")
        self.assertIn("ads.vidaa.com\t2\tyes\tyes", lines[1])
        joined = "\n".join(lines)
        self.assertNotIn("other-device.example.com", joined)  # filtered out by --client
        self.assertNotIn("clientinfo.example.com", joined)    # client "None" != filter

    def test_rules_mode_excludes_blocked(self):
        log = self.write_tmp(json.dumps(ADGUARD_LOG))
        bl = self.write_tmp(BLOCKLIST)
        out = self.run_cli([log, "--blocklist", bl, "--rules"])
        rules = set(out.strip().splitlines())
        self.assertNotIn("||ads.vidaa.com^", rules)
        self.assertIn("||telemetry.example.net^", rules)

    def test_min_count(self):
        log = self.write_tmp(json.dumps(ADGUARD_LOG))
        out = self.run_cli([log, "--client", "192.168.1.50", "--min-count", "2"])
        self.assertIn("ads.vidaa.com", out)
        self.assertNotIn("www.youtube.com", out)

    def test_empty_input_exits_with_message(self):
        log = self.write_tmp("{}")
        with self.assertRaises(SystemExit) as ctx:
            self.run_cli([log])
        self.assertIn("No DNS queries found", str(ctx.exception))




import validate_blocklist as vb
import fetch_query_log as fql


class TestValidateBlocklist(TempFileMixin, unittest.TestCase):
    def run_validator(self, argv):
        argv0 = sys.argv
        sys.argv = ["validate_blocklist.py"] + argv
        try:
            vb.main()
        finally:
            sys.argv = argv0

    def test_valid_file_passes(self):
        path = self.write_tmp("! comment\n||ads.example.com^\nplain.example.net\n")
        self.run_validator([path])  # no SystemExit

    def test_duplicate_detected(self):
        path = self.write_tmp("||ads.example.com^\n||ads.example.com^\n")
        with self.assertRaises(SystemExit) as ctx:
            self.run_validator([path])
        self.assertEqual(ctx.exception.code, 1)

    def test_bad_syntax_detected(self):
        path = self.write_tmp("||unclosed\n")
        with self.assertRaises(SystemExit) as ctx:
            self.run_validator([path])
        self.assertEqual(ctx.exception.code, 1)

    def test_upstream_overlap_detected(self):
        mine = self.write_tmp("||ads.example.com^\n")
        upstream = self.write_tmp("||ads.example.com^\n||other.example.com^\n")
        with self.assertRaises(SystemExit) as ctx:
            self.run_validator([mine, "--upstream", upstream])
        self.assertEqual(ctx.exception.code, 1)

    def test_real_supplement_is_valid(self):
        import os
        supplement = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "blocklists", "toshiba-uv1553db-supplement.txt")
        rules, errors = vb.load_rules(supplement)
        self.assertEqual(errors, [])


class TestFetchQueryLogHelpers(unittest.TestCase):
    def test_build_url(self):
        url = fql.build_querylog_url("http://192.168.1.10:3000/", 500)
        self.assertEqual(url, "http://192.168.1.10:3000/control/querylog?limit=500&offset=0")

    def test_basic_auth_header(self):
        # base64 of "admin:secret"
        self.assertEqual(fql.basic_auth_header("admin", "secret"), "Basic YWRtaW46c2VjcmV0")

    def test_redirect_handler_refuses_redirects(self):
        handler = fql._NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Found", {}, "http://evil.example/"))

    def test_fetch_page_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            fql.fetch_page("file:///etc/passwd", "u", "p", 10)

    def test_fetch_page_refuses_redirect(self):
        # A redirect response must surface as HTTPError, never as followed content.
        import http.server, threading
        class Redirector(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", "http://127.0.0.1:1/")
                self.end_headers()
            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), Redirector)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with self.assertRaises(fql.urllib.error.HTTPError) as ctx:
                fql.fetch_page(f"http://127.0.0.1:{srv.server_port}", "u", "p", 10)
            self.assertEqual(ctx.exception.code, 302)
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
