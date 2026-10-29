#!/usr/bin/env python3
"""Offline test suite for classify_dns_log.py. Run: python3 -m unittest scripts.test_classify_dns_log
or directly: python3 scripts/test_classify_dns_log.py"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

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


class TestMalformedInputs(TempFileMixin, unittest.TestCase):
    def test_bad_nested_types_are_skipped_or_ignored(self):
        path = self.write_tmp(json.dumps({"data": [
            None, {"question": "bad"}, {"question": ["bad"]},
            {"question": {"name": 42}},
            {"question": {"name": "valid.example.com"}, "client_info": "bad"},
            {"question": {"name": "other.example.com"}, "client_info": {"name": []}},
        ]}))
        self.assertEqual(list(m.iter_queries(path)), [
            ("valid.example.com", "", False), ("other.example.com", "", False)])

    def test_invalid_dns_names_never_become_rules(self):
        bad = ["bad domain|.com", "-bad.example.com", "bad-.example.com",
               "x..example.com", "x\\n||evil.com", "a" * 64 + ".com", "*.example.com"]
        path = self.write_tmp(json.dumps({"data": [
            {"question": {"name": name}} for name in bad + ["API-EU.example.com."]]}))
        from unittest.mock import patch
        output = io.StringIO()
        with patch.object(sys, "argv", ["classify_dns_log.py", path, "--rules"]), redirect_stdout(output):
            m.main()
        self.assertEqual(output.getvalue(), "||api-eu.example.com^\n")

    def test_multiple_trailing_dots_are_rejected_before_normalization(self):
        from unittest.mock import patch
        bad = ["bad.example.com..", "bad.example.com...", "..", "..."]
        inputs = [json.dumps({"data": [{"question": {"name": name}}
                                       for name in bad + ["good.example.com."]]}),
                  "\n".join(bad + ["good.example.com."]),
                  "\n".join("query[A] " + name + " from 192.0.2.50"
                            for name in bad + ["good.example.com."])]
        for text in inputs:
            with self.subTest(text=text):
                path = self.write_tmp(text)
                self.assertEqual([row[0] for row in m.iter_queries(path)], ["good.example.com"])
                output = io.StringIO()
                with patch.object(sys, "argv", ["classify_dns_log.py", path, "--rules"]), redirect_stdout(output):
                    m.main()
                self.assertEqual(output.getvalue(), "||good.example.com^\n")

    def test_dnsmasq_and_plain_reject_label_edge_hyphens(self):
        path = self.write_tmp("query[A] -bad.example.com from 192.0.2.50\n"
                              "bad-.example.com\nvalid-host.example.com\n")
        self.assertEqual(list(m.iter_queries(path)), [("valid-host.example.com", "", False)])


TIMED_LOG = {
    "data": [
        {"question": {"name": "ads.vidaa.com."}, "client": "192.168.1.50",
         "reason": "FilteredBlackList", "time": "2026-10-25T09:05:00Z"},
        {"question": {"name": "ads.vidaa.com."}, "client": "192.168.1.50",
         "reason": "FilteredBlackList", "time": "2026-10-25T09:40:00+00:00"},
        {"question": {"name": "www.youtube.com."}, "client": "192.168.1.50",
         "reason": "NotFilteredNotFound", "time": "2026-10-25T10:15:00Z"},
        {"question": {"name": "telemetry.example.net."}, "client": "192.168.1.99",
         "reason": "NotFilteredNotFound", "time": "2026-10-25T09:50:00Z"},
        {"question": {"name": "untimed.example.com."}, "client": "192.168.1.50",
         "reason": "NotFilteredNotFound"},
        {"question": {"name": "badtime.example.com."}, "client": "192.168.1.50",
         "reason": "NotFilteredNotFound", "time": "not-a-date"},
    ]
}


class TestTimeline(TempFileMixin, unittest.TestCase):
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

    def test_parse_timestamp(self):
        self.assertIsNotNone(m.parse_timestamp("2026-10-25T09:05:00Z"))
        self.assertIsNotNone(m.parse_timestamp("2026-10-25T09:05:00+02:00"))
        self.assertIsNotNone(m.parse_timestamp("2026-10-25 09:05:00"))
        self.assertIsNone(m.parse_timestamp("not-a-date"))
        self.assertIsNone(m.parse_timestamp(None))
        self.assertIsNone(m.parse_timestamp(""))

    def test_out_of_range_utc_offsets_are_unusable(self):
        for value in ["0001-01-01T00:00:00+23:59",
                      "9999-12-31T23:59:59-23:59"]:
            with self.subTest(value=value):
                self.assertIsNone(m.parse_timestamp(value))

    def test_timeline_excludes_unrenderable_buckets(self):
        times = ["0001-01-01T00:00:00+23:59", "9999-12-31T23:59:59-23:59",
                 "0001-01-01T00:00:00Z", "2026-10-25T09:05:00Z"]
        log = self.write_tmp(json.dumps({"data": [
            {"question": {"name": "synthetic.example.com"}, "time": value}
            for value in times]}))
        out = self.run_cli([log, "--timeline", "7"])
        self.assertIn("Entries without a timestamp (excluded): 3", out)
        self.assertIn("2026-10-25", out)

    def test_pre_epoch_fraction_uses_previous_bucket(self):
        log = self.write_tmp(json.dumps({"data": [{
            "question": {"name": "synthetic.example.com"},
            "time": "1969-12-31T23:59:59.500000Z"}]}))
        out = self.run_cli([log, "--timeline", "60"])
        self.assertIn("1969-12-31T23:00Z\t1\t0\t1", out)
        self.assertNotIn("1970-01-01", out)

    def test_timeline_buckets(self):
        log = self.write_tmp(json.dumps(TIMED_LOG))
        out = self.run_cli([log, "--client", "192.168.1.50", "--timeline", "60"])
        self.assertIn("2026-10-25T09:00Z\t2\t2\t0", out)
        self.assertIn("2026-10-25T10:00Z\t1\t0\t1", out)
        self.assertNotIn("telemetry.example.net", out)  # other client excluded
        self.assertIn("Entries without a timestamp (excluded): 2", out)

    def test_timeline_without_client(self):
        log = self.write_tmp(json.dumps(TIMED_LOG))
        out = self.run_cli([log, "--timeline"])
        self.assertIn("2026-10-25T09:00Z\t3\t2\t1", out)  # default 60 minutes

    def test_timeline_rejects_untimed_input(self):
        log = self.write_tmp("plain.example.org\nwww.youtube.com\n")
        with self.assertRaises(SystemExit):
            self.run_cli([log, "--timeline"])

    def test_timed_generator_keeps_legacy_shape(self):
        path = self.write_tmp(json.dumps(ADGUARD_LOG))
        self.assertEqual(list(m.iter_queries(path))[0], ("ads.vidaa.com", "192.168.1.50", False))
        timed = list(m.iter_queries_timed(path))[0]
        self.assertEqual(timed[:3], ("ads.vidaa.com", "192.168.1.50", False))
        self.assertIsNone(timed[3])


class TestBlocklist(TempFileMixin, unittest.TestCase):
    def test_load_adguard_and_plain(self):
        path = self.write_tmp(BLOCKLIST)
        self.assertEqual(m.load_blocklist(path), {"ads.vidaa.com", "blocked.example.net"})

    def test_load_skips_slash_comments(self):
        # The upstream annotated edition comments with '//', not '!'.
        path = self.write_tmp("//Title: annotated edition\n//Purpose: cleanup\nplain.example.net\n")
        self.assertEqual(m.load_blocklist(path), {"plain.example.net"})

    def test_unsupported_filter_semantics_are_not_silently_covered(self):
        unsupported = ["||example.com^$client=192.0.2.1", "@@||example.com^",
                       "||*.example.com^", "||example.com", "||example..com^",
                       "||example.com^junk", "0.0.0.0 example.com", "/example/"]
        for rule in unsupported:
            with self.subTest(rule=rule):
                path = self.write_tmp("! header\n" + rule + "\n")
                with self.assertRaisesRegex(ValueError, "line 2"):
                    m.load_blocklist(path)

    def test_supported_hostnames_normalize_case_and_root_dot(self):
        path = self.write_tmp("||API-EU.example.com.^\n_telemetry.example.net\n")
        self.assertEqual(m.load_blocklist(path),
                         {"api-eu.example.com", "_telemetry.example.net"})

    def test_cli_rejects_options_without_partial_report_or_traceback(self):
        from unittest.mock import patch
        log = self.write_tmp("other.example.com\n")
        blocklist = self.write_tmp("||example.com^$client=192.0.2.1\n")
        for option in [[], ["--rules"]]:
            with self.subTest(option=option), patch.object(sys, "argv",
                    ["classify_dns_log.py", log, "--blocklist", blocklist] + option):
                output = io.StringIO()
                with redirect_stdout(output), self.assertRaises(SystemExit) as ctx:
                    m.main()
                self.assertEqual(output.getvalue(), "")
                self.assertIn("line 1", str(ctx.exception))

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

    def test_slash_comments_accepted(self):
        path = self.write_tmp("// annotated edition header\n||ads.example.com^\nplain.example.net\n")
        self.run_validator([path])  # no SystemExit

    def test_hyphenated_hostnames_accepted(self):
        # Common in the wild: ad-cmp.hismarttv.com and similar.
        path = self.write_tmp("ad-cmp.hismarttv.com\n||api-recommendation-eu.hismarttv.com^\n")
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

    def test_adguard_rules_validate_hostname_structure(self):
        invalid = ["..", "-bad.example.com", "bad-.example.com",
                   "example..com", "example.com.", "singlelabel",
                   "a" * 64 + ".example.com",
                   ".".join(["a" * 63] * 4) + ".com"]
        path = self.write_tmp("\n".join("||" + name + "^" for name in invalid))
        rules, errors = vb.load_rules(path)
        self.assertEqual(rules, [])
        self.assertEqual(len(errors), len(invalid))
        for number, error in enumerate(errors, 1):
            self.assertIn("line " + str(number) + ":", error)

    def test_adguard_rules_keep_supported_wildcards_and_underscores(self):
        path = self.write_tmp("||*.example.com^\n||ad*.example.com^\n"
                              "||_service.example.com^\n||API-EU.example.com^")
        rules, errors = vb.load_rules(path)
        self.assertEqual(errors, [])
        self.assertEqual([row[2] for row in rules],
                         ["*.example.com", "ad*.example.com",
                          "_service.example.com", "api-eu.example.com"])

    def test_invalid_adguard_rule_fails_cli(self):
        path = self.write_tmp("||example..com^\n")
        with self.assertRaises(SystemExit) as ctx:
            self.run_validator([path])
        self.assertEqual(ctx.exception.code, 1)

    def test_real_supplement_is_valid(self):
        import os
        supplement = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "blocklists", "toshiba-uv1553db-supplement.txt")
        rules, errors = vb.load_rules(supplement)
        self.assertEqual(errors, [])


class TestClientInventory(TempFileMixin, unittest.TestCase):
    def run_cli(self, arguments):
        from unittest.mock import patch
        output = io.StringIO()
        with patch.object(sys, "argv", ["classify_dns_log.py"] + arguments), redirect_stdout(output):
            m.main()
        return output.getvalue()

    def test_counts_and_order_are_deterministic(self):
        log = self.write_tmp(json.dumps(ADGUARD_LOG))
        self.assertEqual(self.run_cli([log, "--clients"]),
                         'client\tqueries\tfiltered\nclient:"192.168.1.50"\t4\t1\n'
                         '<unknown>\t1\t0\nclient:"192.168.1.99"\t1\t0\n')

    def test_unknown_plain_input_and_control_characters(self):
        plain = self.write_tmp("synthetic.example.com\n")
        self.assertEqual(self.run_cli([plain, "--clients"]),
                         "client\tqueries\tfiltered\n<unknown>\t1\t0\n")
        log = self.write_tmp(json.dumps({"data": [{
            "question": {"name": "synthetic.example.com"}, "client": "x\ty\nz"}]}))
        output = self.run_cli([log, "--clients"])
        self.assertEqual(len(output.splitlines()), 2)
        self.assertIn('client:"x\\ty\\nz"\t1\t0', output)

    def test_spreadsheet_import_keeps_formula_clients_literal(self):
        import csv
        values = ["=1+1", "+1+1", "-1+1", "@SUM(1)", "\t=1+1", "\r=1+1"]
        log = self.write_tmp(json.dumps({"data": [
            {"question": {"name": "synthetic.example.com"}, "client": client}
            for client in values]}))
        rows = list(csv.reader(io.StringIO(self.run_cli([log, "--clients"])), delimiter="\t"))
        self.assertEqual(len(rows), len(values) + 1)
        self.assertEqual({row[0] for row in rows[1:]},
                         {"client:" + json.dumps(value, ensure_ascii=True) for value in values})
        self.assertTrue(all(len(row) == 3 and row[0].startswith("client:") for row in rows[1:]))

    def test_rejects_conflicting_modes_and_empty_input(self):
        log = self.write_tmp("synthetic.example.com\n")
        for option in [["--client", "192.0.2.50"], ["--blocklist", "unused"],
                       ["--timeline"], ["--rules"]]:
            with self.subTest(option=option), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    self.run_cli([log, "--clients"] + option)
                self.assertEqual(ctx.exception.code, 2)
        empty = self.write_tmp("! no queries\n")
        with self.assertRaises(SystemExit):
            self.run_cli([empty, "--clients"])


class TestLocalInputFailures(unittest.TestCase):
    def test_classifier_missing_log_in_both_modes(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            missing = os.path.join(directory, "missing.json")
            for option in [[], ["--timeline"]]:
                with self.subTest(option=option), patch.object(sys, "argv",
                        ["classify_dns_log.py", missing] + option):
                    with self.assertRaises(SystemExit) as ctx:
                        m.main()
                    self.assertIn("Cannot read a local input file", str(ctx.exception))

    def test_classifier_unreadable_comparison_has_no_partial_output(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            log = os.path.join(directory, "log.txt")
            with open(log, "w", encoding="utf-8") as stream:
                stream.write("synthetic.example.com\n")
            with patch.object(sys, "argv", ["classify_dns_log.py", log,
                    "--blocklist", directory]), redirect_stdout(io.StringIO()) as output:
                with self.assertRaises(SystemExit) as ctx:
                    m.main()
                self.assertIn("Cannot read a local input file", str(ctx.exception))
                self.assertEqual(output.getvalue(), "")

    def test_validator_missing_primary_and_upstream(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            valid = os.path.join(directory, "valid.txt")
            missing = os.path.join(directory, "missing.txt")
            with open(valid, "w", encoding="utf-8") as stream:
                stream.write("synthetic.example.com\n")
            for arguments in [[missing], [valid, "--upstream", missing]]:
                with self.subTest(arguments=arguments), patch.object(sys, "argv",
                        ["validate_blocklist.py"] + arguments):
                    with self.assertRaises(SystemExit) as ctx:
                        vb.main()
                    self.assertIn("Cannot read a blocklist file", str(ctx.exception))


class TestFetchQueryLogHelpers(unittest.TestCase):
    def test_build_url(self):
        url = fql.build_querylog_url("http://192.168.1.10:3000/", 500)
        self.assertEqual(url, "http://192.168.1.10:3000/control/querylog?limit=500&offset=0")

    def test_host_rejects_ambiguous_or_credential_bearing_urls(self):
        invalid = ["https:///missing", "http://", "http://server:bad",
                   "http://server:65536", "http://server:", "http://u:private@server",
                   "http://u@server", "http://server?token=private",
                   "http://server#private", "http://server?", "http://server#",
                   "http://server/\nprivate", "http://server\\private", "file:///tmp/log"]
        for host in invalid:
            with self.subTest(host=host):
                with self.assertRaises(ValueError) as ctx:
                    fql.build_querylog_url(host, 10)
                self.assertNotIn("private", str(ctx.exception))

    def test_host_accepts_ipv6_https_and_reverse_proxy_paths(self):
        for host in ["http://[::1]:3000", "https://adguard.example/proxy/"]:
            with self.subTest(host=host):
                self.assertEqual(fql.build_querylog_url(host, 2),
                                 host.rstrip("/") + "/control/querylog?limit=2&offset=0")

    def test_invalid_host_exits_before_credentials_or_network(self):
        from unittest.mock import patch
        with patch.object(sys, "argv", ["fetch_query_log.py", "--host",
                    "http://user:private@server", "--user", "u", "-o", "unused"]), \
                patch.object(fql.getpass, "getpass") as prompt, \
                patch.object(fql, "fetch_all_pages") as fetch:
            with self.assertRaises(SystemExit) as ctx:
                fql.main()
            self.assertNotIn("private", str(ctx.exception))
            prompt.assert_not_called()
            fetch.assert_not_called()

    def test_network_and_redirect_errors_do_not_echo_remote_details(self):
        from unittest.mock import patch
        errors = [fql.urllib.error.URLError("private-network-detail"),
                  fql.urllib.error.HTTPError("http://server", 302, "Found",
                      {"Location": "https://other/?private-token"}, None)]
        for error in errors:
            with self.subTest(error=type(error).__name__), \
                    patch.object(sys, "argv", ["fetch_query_log.py", "--host",
                        "http://server", "--user", "u", "-o", "unused"]), \
                    patch.dict(os.environ, {"ADGUARD_PASSWORD": "synthetic"}), \
                    patch.object(fql, "fetch_all_pages", side_effect=error):
                with self.assertRaises(SystemExit) as ctx:
                    fql.main()
                self.assertNotIn("private", str(ctx.exception))

    def test_basic_auth_header(self):
        # base64 of "admin:secret"
        self.assertEqual(fql.basic_auth_header("admin", "secret"), "Basic YWRtaW46c2VjcmV0")

    def test_redirect_handler_refuses_redirects(self):
        handler = fql._NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Found", {}, "http://evil.example/"))

    def test_fetch_page_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            fql.fetch_page("file:///etc/passwd", "u", "p", 10)

    def test_truncated_http_response_keeps_export_and_has_safe_error(self):
        import http.server, threading
        from unittest.mock import patch

        class Truncated(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{"data": ["synthetic-private-record"'
                self.send_response(200)
                self.send_header("Content-Length", str(len(body) + 20))
                self.end_headers()
                self.wfile.write(body)
                self.close_connection = True

            def log_message(self, *args):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Truncated)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                output = os.path.join(directory, "export.json")
                with open(output, "w", encoding="utf-8") as stream:
                    stream.write("previous export")
                with patch.object(sys, "argv", ["fetch_query_log.py", "--host",
                        f"http://127.0.0.1:{server.server_port}", "--user", "u",
                        "-o", output]), patch.dict(os.environ, {"ADGUARD_PASSWORD": "synthetic"}):
                    with self.assertRaises(SystemExit) as ctx:
                        fql.main()
                self.assertIn("Cannot reach AdGuard Home", str(ctx.exception))
                self.assertNotIn("synthetic-private-record", str(ctx.exception))
                with open(output, encoding="utf-8") as stream:
                    self.assertEqual(stream.read(), "previous export")
                self.assertEqual(os.listdir(directory), ["export.json"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

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


class TestFetchPagination(unittest.TestCase):
    TOTAL = 7

    def start_server(self):
        import http.server, threading
        total = self.TOTAL

        class PagedHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                qs = fql.urllib.parse.parse_qs(fql.urllib.parse.urlparse(self.path).query)
                limit = int(qs["limit"][0])
                offset = int(qs["offset"][0])
                entries = [
                    {"question": {"name": f"d{i}.example.com."}, "client": "192.168.1.50",
                     "reason": "NotFilteredNotFound", "time": f"2026-10-25T09:0{i}:00Z"}
                    for i in range(total)
                ]
                body = json.dumps({"oldest": "", "data": entries[offset:offset + limit]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), PagedHandler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        return srv

    def test_merges_and_stops_on_short_page(self):
        srv = self.start_server()
        try:
            host = f"http://127.0.0.1:{srv.server_port}"
            merged, pages, maybe_more = fql.fetch_all_pages(host, "u", "p", limit=3, pages=10)
            self.assertEqual(pages, 3)  # 3 + 3 + short page of 1
            self.assertEqual(len(merged["data"]), self.TOTAL)
            self.assertFalse(maybe_more)  # ended on a short page: log is complete
        finally:
            srv.shutdown()

    def test_respects_page_cap(self):
        srv = self.start_server()
        try:
            host = f"http://127.0.0.1:{srv.server_port}"
            merged, pages, maybe_more = fql.fetch_all_pages(host, "u", "p", limit=3, pages=2)
            self.assertEqual(pages, 2)
            self.assertEqual(len(merged["data"]), 6)
            self.assertTrue(maybe_more)  # stopped on a full page: possibly incomplete
        finally:
            srv.shutdown()

    def test_main_warns_when_last_page_full(self):
        srv = self.start_server()
        old_env = os.environ.get("ADGUARD_PASSWORD")
        os.environ["ADGUARD_PASSWORD"] = "x"
        argv0 = sys.argv
        err = io.StringIO()
        out_file = os.path.join(tempfile.mkdtemp(), "q.json")
        try:
            host = f"http://127.0.0.1:{srv.server_port}"
            sys.argv = ["fetch_query_log.py", "--host", host, "--user", "u",
                        "--pages", "1", "--limit", "3", "-o", out_file]
            with redirect_stderr(err):
                fql.main()
            self.assertIn("may hold older entries", err.getvalue())
            with open(out_file, encoding="utf-8") as fh:
                self.assertEqual(len(json.load(fh)["data"]), 3)
        finally:
            sys.argv = argv0
            if old_env is None:
                del os.environ["ADGUARD_PASSWORD"]
            else:
                os.environ["ADGUARD_PASSWORD"] = old_env
            srv.shutdown()

    def test_main_no_warning_on_short_page(self):
        srv = self.start_server()
        old_env = os.environ.get("ADGUARD_PASSWORD")
        os.environ["ADGUARD_PASSWORD"] = "x"
        argv0 = sys.argv
        err = io.StringIO()
        out_file = os.path.join(tempfile.mkdtemp(), "q.json")
        try:
            host = f"http://127.0.0.1:{srv.server_port}"
            sys.argv = ["fetch_query_log.py", "--host", host, "--user", "u",
                        "--pages", "10", "--limit", "3", "-o", out_file]
            with redirect_stderr(err):
                fql.main()
            self.assertNotIn("may hold older entries", err.getvalue())
            with open(out_file, encoding="utf-8") as fh:
                self.assertEqual(len(json.load(fh)["data"]), self.TOTAL)
        finally:
            sys.argv = argv0
            if old_env is None:
                del os.environ["ADGUARD_PASSWORD"]
            else:
                os.environ["ADGUARD_PASSWORD"] = old_env
            srv.shutdown()

    def test_rejects_unexpected_response_shape(self):
        import http.server, threading

        class BadHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{"unexpected": true}'
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), BadHandler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            host = f"http://127.0.0.1:{srv.server_port}"
            with self.assertRaises(ValueError):
                fql.fetch_all_pages(host, "u", "p", limit=3, pages=1)
        finally:
            srv.shutdown()


class TestFetchSchema(TempFileMixin, unittest.TestCase):
    def test_single_and_multi_page_reject_bad_schema_without_writing(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "export.json")
            for pages in (1, 2):
                for data in ([], {}, {"data": None}, {"data": "bad"}, {"data": {}}):
                    with self.subTest(pages=pages, data=data):
                        with open(output, "w") as fh:
                            fh.write("keep existing export")
                        argv = ["fetch_query_log.py", "--host", "http://localhost", "--user", "test",
                                "--pages", str(pages), "-o", output]
                        with patch.object(sys, "argv", argv), patch.dict(os.environ, {"ADGUARD_PASSWORD": "synthetic"}), patch.object(fql, "fetch_page", return_value=data):
                            with self.assertRaises(SystemExit) as ctx:
                                fql.main()
                        self.assertIn("expected an object with a 'data' list", str(ctx.exception))
                        with open(output) as fh:
                            self.assertEqual(fh.read(), "keep existing export")

    def test_nonpositive_limit_rejected_before_credentials_or_fetch(self):
        from unittest.mock import patch
        for limit in (0, -1):
            argv = ["fetch_query_log.py", "--host", "http://localhost", "--user", "test",
                    "--limit", str(limit), "-o", "unused.json"]
            with patch.object(sys, "argv", argv), patch.object(fql.getpass, "getpass") as prompt, patch.object(fql, "fetch_page") as fetch:
                with self.assertRaises(SystemExit) as ctx:
                    fql.main()
                self.assertIn("--limit must be >= 1", str(ctx.exception))
                prompt.assert_not_called()
                fetch.assert_not_called()


class TestEndToEndPipeline(TempFileMixin, unittest.TestCase):
    """The exact flow docs/03 describes: fetch pages, then classify.

    Uses a local paged HTTP server - no real network access.
    """

    def test_fetch_then_classify(self):
        import http.server, threading

        entries = [
            {"question": {"name": "ads.vidaa.com."}, "client": "192.168.1.50",
             "reason": "FilteredBlackList", "time": "2026-10-25T09:05:00Z"},
            {"question": {"name": "new-candidate.example.net."}, "client": "192.168.1.50",
             "reason": "NotFilteredNotFound", "time": "2026-10-25T09:06:00Z"},
            {"question": {"name": "www.youtube.com."}, "client": "192.168.1.50",
             "reason": "NotFilteredNotFound", "time": "2026-10-25T09:07:00Z"},
        ]

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                qs = fql.urllib.parse.parse_qs(fql.urllib.parse.urlparse(self.path).query)
                limit = int(qs["limit"][0])
                offset = int(qs["offset"][0])
                body = json.dumps({"oldest": "", "data": entries[offset:offset + limit]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            host = f"http://127.0.0.1:{srv.server_port}"
            merged, pages, maybe_more = fql.fetch_all_pages(host, "u", "p", limit=2, pages=5)
            self.assertEqual((pages, maybe_more), (2, False))  # full page + short page of 1
            log_path = self.write_tmp(json.dumps(merged))

            # Blocklist mixes AdGuard rules, plain hosts and //-comments,
            # like the current upstream annotated edition.
            bl_path = self.write_tmp(
                "// annotated edition\n||ads.vidaa.com^\nwww.youtube.com\n")
            blocked = m.load_blocklist(bl_path)
            self.assertEqual(blocked, {"ads.vidaa.com", "www.youtube.com"})

            rows = [r for r in m.iter_queries(log_path) if r[1] == "192.168.1.50"]
            candidates = sorted({r[0] for r in rows if not m.is_blocked(r[0], blocked)})
            self.assertEqual(candidates, ["new-candidate.example.net"])
        finally:
            srv.shutdown()


class TestPrivateExport(unittest.TestCase):
    def test_new_and_existing_exports_are_private_and_valid(self):
        import stat
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "export.json")
            for existing in (False, True):
                with self.subTest(existing=existing):
                    if existing:
                        os.chmod(path, 0o644)
                    fql.write_private_export(path, {"data": [], "label": "café"})
                    with open(path, encoding="utf-8") as fh:
                        self.assertEqual(json.load(fh), {"data": [], "label": "café"})
                    if os.name == "posix":
                        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)
                    self.assertEqual(os.listdir(directory), ["export.json"])

    def test_failed_replace_preserves_old_export_and_cleans_temp(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "export.json")
            with open(path, "w") as fh:
                fh.write("old export")
            with patch.object(fql.os, "replace", side_effect=OSError("synthetic failure")):
                with self.assertRaises(OSError):
                    fql.write_private_export(path, {"data": []})
            with open(path) as fh:
                self.assertEqual(fh.read(), "old export")
            self.assertEqual(os.listdir(directory), ["export.json"])

    def test_failed_serialization_preserves_old_export_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "export.json")
            with open(path, "w") as fh:
                fh.write("old export")
            with self.assertRaises(TypeError):
                fql.write_private_export(path, {"bad": object()})
            with open(path) as fh:
                self.assertEqual(fh.read(), "old export")
            self.assertEqual(os.listdir(directory), ["export.json"])

    @unittest.skipUnless(os.name == "posix", "POSIX symlink semantics")
    def test_output_symlink_is_replaced_without_modifying_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "target")
            path = os.path.join(directory, "export.json")
            with open(target, "w") as fh:
                fh.write("do not change")
            os.symlink(target, path)
            fql.write_private_export(path, {"data": []})
            self.assertFalse(os.path.islink(path))
            with open(target) as fh:
                self.assertEqual(fh.read(), "do not change")

    def test_cli_write_error_is_actionable_without_traceback(self):
        from unittest.mock import patch
        argv = ["fetch_query_log.py", "--host", "http://localhost", "--user", "test", "-o", "unused.json"]
        with patch.object(sys, "argv", argv), patch.dict(os.environ, {"ADGUARD_PASSWORD": "synthetic"}), patch.object(fql, "fetch_all_pages", return_value=({"data": []}, 1, False)), patch.object(fql, "write_private_export", side_effect=OSError("synthetic")):
            with self.assertRaises(SystemExit) as ctx:
                fql.main()
            self.assertIn("Cannot save the export", str(ctx.exception))


class TestDocumentedExample(unittest.TestCase):
    def test_readme_example_outputs(self):
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base = [sys.executable, "scripts/classify_dns_log.py", "examples/synthetic-dns.json", "--client", "192.0.2.50"]
        block = ["--blocklist", "examples/synthetic-blocklist.txt"]
        cases = [
            (block, "domain\tqueries\talready_blocked\tseen_filtered\nads.example.com\t2\tyes\tyes\nvideo.example.net\t1\tno\tno\n"),
            (["--timeline", "60"], "Timeline: 60-minute buckets (times in UTC)\nbucket_start\ttotal\tfiltered\tunblocked\n2026-10-01T09:00Z\t2\t2\t0\n2026-10-01T10:00Z\t1\t0\t1\n"),
            (block + ["--rules"], "||video.example.net^\n"),
        ]
        for args, expected in cases:
            with self.subTest(args=args):
                result = subprocess.run(base + args, cwd=root, text=True, capture_output=True, check=True)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
