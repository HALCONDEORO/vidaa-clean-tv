import json
import os
from pathlib import Path
import tempfile
import unittest

import build_session_pack as pack


ADGUARD_LOG = {
    "data": [
        {"question": {"name": "ads.example.com."}, "client": "192.0.2.50",
         "reason": "FilteredBlackList", "time": "2026-10-01T09:05:00Z"},
        {"question": {"name": "ads.example.com."}, "client": "192.0.2.50",
         "reason": "FilteredBlackList", "time": "2026-10-01T09:15:00Z"},
        {"question": {"name": "tracker.example.net."}, "client": "192.0.2.50",
         "reason": "NotFilteredNotFound", "time": "2026-10-01T09:20:00Z"},
        {"question": {"name": "mybank-private.example.org."}, "client": "192.0.2.99",
         "reason": "NotFilteredNotFound", "time": "2026-10-01T10:05:00Z"},
        {"question": {"name": "family-secret.example.org."}, "client": "192.0.2.99",
         "reason": "NotFilteredNotFound", "time": "2026-10-01T10:10:00Z"},
    ]
}

# A user blocklist can contain anything, including personal domains.
BLOCKLIST = "||ads.example.com^\n||tracker.example.net^\n||mybank-private.example.org^\n"

BEFORE_LOG = {
    "data": [
        {"question": {"name": "ads.example.com."}, "client": "192.0.2.50",
         "reason": "NotFilteredNotFound", "time": "2026-09-01T09:05:00Z"},
        {"question": {"name": "other-older.example.org."}, "client": "192.0.2.51",
         "reason": "NotFilteredNotFound", "time": "2026-09-01T09:06:00Z"},
    ]
}

PRIVATE_VALUES = ("mybank-private", "family-secret", "other-older", "192.0.2",
                  "2026-10-01", "2026-09-01", "09:05")


class TestSessionPack(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.blocklist = self.dir / "list-with-private-names.txt"
        self.blocklist.write_text(BLOCKLIST, encoding="utf-8")
        self.log = self.dir / "household-export-october.json"
        self.log.write_text(json.dumps(ADGUARD_LOG), encoding="utf-8")
        self.out = self.dir / "report.html"

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, extra=None, log=None):
        argv = [str(log or self.log), "-o", str(self.out), "--date", "2026-11-24"]
        pack.main(argv + (extra or []))
        return self.out.read_text(encoding="utf-8")

    def test_default_names_nothing(self):
        report = self.build(["--blocklist", str(self.blocklist)])
        # Even blocklist-matched domains are not named by default.
        for domain in ("ads.example.com", "tracker.example.net") + PRIVATE_VALUES:
            self.assertNotIn(domain, report)
        self.assertIn("No domain is named", report)
        # Aggregates are present: 5 queries, 2 filtered, 4 unique,
        # 3 matched unique (ads, tracker, mybank-private) with 4 queries.
        self.assertIn(">5</td>", report)
        self.assertIn("2 (40.0%)</td>", report)
        self.assertIn(">4</td>", report)
        self.assertIn("3 (4 queries)</td>", report)
        self.assertIn("1 (1 queries)</td>", report)

    def test_name_domain_is_the_only_way_to_name(self):
        report = self.build(["--blocklist", str(self.blocklist),
                             "--name-domain", "ads.example.com",
                             "--name-domain", "tracker.example.net"])
        self.assertIn("ads.example.com", report)
        self.assertIn("tracker.example.net", report)
        row = next(line for line in report.splitlines() if "ads.example.com" in line)
        self.assertIn('data-label="Queries">2</td>', row)
        self.assertIn('data-label="Blocked">2</td>', row)
        for leaked in PRIVATE_VALUES:
            self.assertNotIn(leaked, report)

    def test_name_domain_not_in_log_stays_absent(self):
        report = self.build(["--name-domain", "not-in-the-log.example.com"])
        self.assertNotIn("not-in-the-log.example.com", report)
        self.assertIn("No domain is named", report)

    def test_name_domain_normalizes_case_and_root_dot(self):
        report = self.build(["--name-domain", "ADS.Example.COM."])
        self.assertIn("ads.example.com", report)

    def test_invalid_name_domain_rejected(self):
        for bad in ("", "not a domain", "bad..example.com", "-bad.example.com"):
            with self.subTest(bad=bad), self.assertRaises(SystemExit) as cm:
                self.build(["--name-domain", bad])
            self.assertNotEqual(cm.exception.code, 0)

    def test_blocklist_with_personal_domain_does_not_name_it(self):
        # The blocklist contains mybank-private.example.org. Privacy by
        # default means a list match never lifts a name into the report.
        report = self.build(["--blocklist", str(self.blocklist)])
        self.assertNotIn("mybank-private", report)
        self.assertIn("matching a list is not evidence", report)

    def test_no_file_names_in_report(self):
        report = self.build(["--blocklist", str(self.blocklist),
                             "--name-domain", "ads.example.com"])
        # Neither the input name (personal, dated) nor the blocklist name.
        self.assertNotIn("household-export-october", report)
        self.assertNotIn("list-with-private-names", report)
        self.assertNotIn(".json", report)
        self.assertNotIn(".txt", report)

    def test_before_after_comparison(self):
        before = self.dir / "before.json"
        before.write_text(json.dumps(BEFORE_LOG), encoding="utf-8")
        report = self.build(["--before", str(before), "--blocklist", str(self.blocklist),
                             "--name-domain", "ads.example.com"])
        self.assertIn("Earlier log", report)
        self.assertIn("Current log", report)
        self.assertIn("not a controlled experiment", report)
        row = next(line for line in report.splitlines() if "ads.example.com" in line)
        # After: 2 queries, 2 blocked; before: 1 query, 0 blocked.
        for cell in ('data-label="Queries">2</td>', 'data-label="Blocked">2</td>',
                     'data-label="Queries (earlier log)">1</td>',
                     'data-label="Blocked (earlier log)">0</td>'):
            self.assertIn(cell, row)
        for leaked in PRIVATE_VALUES:
            self.assertNotIn(leaked, report)

    def test_before_refuses_to_overwrite_either_input(self):
        before = self.dir / "before.json"
        before.write_text(json.dumps(BEFORE_LOG), encoding="utf-8")
        for target in (str(self.log), str(before)):
            with self.subTest(target=target), self.assertRaises(SystemExit) as cm:
                pack.main([str(self.log), "-o", target, "--before", str(before)])
            self.assertNotEqual(cm.exception.code, 0)

    def test_deterministic_output(self):
        first = self.build(["--blocklist", str(self.blocklist),
                            "--name-domain", "ads.example.com"])
        second = self.build(["--blocklist", str(self.blocklist),
                             "--name-domain", "ads.example.com"])
        self.assertEqual(first, second)

    def test_plain_text_log(self):
        plain = self.dir / "log.txt"
        plain.write_text("ads.example.com\nfamily-secret.example.org\n", encoding="utf-8")
        report = self.build(["--blocklist", str(self.blocklist)], log=plain)
        self.assertIn("No domain is named", report)
        self.assertNotIn("family-secret", report)
        self.assertNotIn("ads.example.com", report)
        self.assertIn(">2</td>", report)

    def test_adversarial_name_domain_is_html_escaped(self):
        # DOMAIN_RE rejects markup, so an injected tag can never be a "domain".
        with self.assertRaises(SystemExit):
            self.build(["--name-domain", "<script>alert(1)</script>"])

    def test_adversarial_domain_in_log_is_never_rendered(self):
        # Even if a hostile name slipped past DOMAIN_RE upstream, the only
        # rendered names come from --name-domain, which validates strictly.
        evil = dict(ADGUARD_LOG)
        evil["data"] = ADGUARD_LOG["data"] + [
            {"question": {"name": "ads.example.com"}, "reason": "Filtered"}]
        log = self.dir / "evil.json"
        log.write_text(json.dumps(evil), encoding="utf-8")
        report = self.build([], log=log)
        self.assertNotIn("<script>", report)

    def test_invalid_log_fails_without_echoing_values(self):
        # SQLite magic followed by garbage: classified as Pi-hole FTL, unreadable.
        log = self.dir / "broken.db"
        log.write_bytes(b"SQLite format 3\x00SECRET-VALUE not a database")
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(log), "-o", str(self.out)])
        self.assertNotEqual(cm.exception.code, 0)
        self.assertNotIn("SECRET-VALUE", str(cm.exception))
        self.assertFalse(self.out.exists())

    def test_missing_input_fails(self):
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(self.dir / "absent.json"), "-o", str(self.out)])
        self.assertNotEqual(cm.exception.code, 0)

    def test_output_never_truncates_a_blocklist(self):
        # Reviewer repro: output equal to a blocklist path must not truncate
        # the list with HTML. Direct, symlink and hardlink aliases.
        before = self.blocklist.read_bytes()
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(self.log), "-o", str(self.blocklist),
                       "--blocklist", str(self.blocklist)])
        self.assertNotEqual(cm.exception.code, 0)
        self.assertEqual(self.blocklist.read_bytes(), before)

        alias = self.dir / "alias-to-list.txt"
        os.symlink(self.blocklist, alias)
        with self.assertRaises(SystemExit):
            pack.main([str(self.log), "-o", str(alias),
                       "--blocklist", str(self.blocklist)])
        self.assertEqual(self.blocklist.read_bytes(), before)
        self.assertTrue(alias.is_symlink())

        hard = self.dir / "hardlink-to-list.txt"
        os.link(self.blocklist, hard)
        with self.assertRaises(SystemExit):
            pack.main([str(self.log), "-o", str(hard),
                       "--blocklist", str(self.blocklist)])
        self.assertEqual(self.blocklist.read_bytes(), before)

    def test_output_symlink_is_replaced_never_followed(self):
        # An existing symlink AT the output path is replaced by the report;
        # the file it pointed to must survive untouched.
        precious = self.dir / "precious.txt"
        precious.write_text("PRECIOUS-CONTENT", encoding="utf-8")
        link_out = self.dir / "out.html"
        os.symlink(precious, link_out)
        pack.main([str(self.log), "-o", str(link_out), "--date", "2026-11-24"])
        self.assertFalse(link_out.is_symlink())
        self.assertIn("session pack", link_out.read_text(encoding="utf-8"))
        self.assertEqual(precious.read_text(encoding="utf-8"), "PRECIOUS-CONTENT")

    def test_parent_blocklist_rule_never_lifts_private_subdomain(self):
        # Reviewer repro: ||example.com^ with subdomain scope must not cause
        # a queried subdomain carrying a private label to be named.
        log = self.dir / "sub.json"
        log.write_text(json.dumps({"data": [
            {"question": {"name": "secret-diary.example.com."},
             "client": "192.0.2.50", "reason": "FilteredBlackList",
             "time": "2026-10-01T09:05:00Z"}]}), encoding="utf-8")
        parent = self.dir / "parent.txt"
        parent.write_text("||example.com^\n", encoding="utf-8")
        report = self.build(["--blocklist", str(parent)], log=log)
        self.assertNotIn("secret-diary", report)
        self.assertNotIn("example.com", report)
        # Naming the parent explicitly still does not pull the subdomain in.
        report = self.build(["--blocklist", str(parent),
                             "--name-domain", "example.com"], log=log)
        self.assertNotIn("secret-diary", report)
        # The parent had no queries of its own, so it is not rendered either.
        self.assertNotIn("example.com", report)

    def test_zero_queries_never_concludes_inactivity(self):
        # Reviewer repro: a malformed log (or a wrong --format) parses as zero
        # queries; the tool must refuse, not write a report implying the TV
        # was inactive.
        log = self.dir / "broken.json"
        log.write_text('{"data": "SECRET-VALUE not a list"', encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(log), "-o", str(self.out), "--format", "adguard"])
        self.assertNotEqual(cm.exception.code, 0)
        self.assertFalse(self.out.exists())
        # Empty but valid log: same refusal.
        empty = self.dir / "empty.json"
        empty.write_text('{"data": []}', encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(empty), "-o", str(self.out)])
        self.assertNotEqual(cm.exception.code, 0)
        self.assertFalse(self.out.exists())
        # An empty --before log also refuses.
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(self.log), "-o", str(self.out), "--before", str(empty)])
        self.assertNotEqual(cm.exception.code, 0)

    def test_bad_date_rejected(self):
        with self.assertRaises(SystemExit) as cm:
            pack.main([str(self.log), "-o", str(self.out), "--date", "tomorrow"])
        self.assertNotEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
