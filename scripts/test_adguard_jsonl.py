"""Synthetic-only regression tests for the upstream native log adapter."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import classify_dns_log as m


class NativeLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'querylog.json'
        self.row = {'QH': 'synthetic.invalid.', 'IP': '192.0.2.50',
                    'T': '2026-11-23T12:00:00.123456789Z',
                    'Result': {'IsFiltered': True}, 'Answer': 'ignored'}

    def write(self, rows):
        self.path.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
        return str(self.path)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(Path(m.__file__)), str(self.path),
                               '--format', 'adguard-jsonl', *args],
                              capture_output=True, text=True, check=False)

    def test_native_fields_and_nanosecond_time(self):
        self.write([self.row])
        domain, client, filtered, ts = list(m.iter_queries_timed(str(self.path), 'adguard-jsonl'))[0]
        self.assertEqual((domain, client, filtered), ('synthetic.invalid', '192.0.2.50', True))
        self.assertEqual(ts.microsecond, 123456)

    def test_unfiltered_field_omitted_and_blanks(self):
        self.row['Result'] = {}
        self.write([self.row])
        self.path.write_text('\n' + self.path.read_text() + '\n\n')
        self.assertFalse(list(m.iter_queries(str(self.path), 'adguard-jsonl'))[0][2])

    def test_one_record_requires_explicit_format(self):
        self.write([self.row])
        self.assertEqual(list(m.iter_queries(str(self.path))), [])
        self.assertEqual(len(list(m.iter_queries(str(self.path), 'adguard-jsonl'))), 1)

    def test_cli_clients_and_timeline(self):
        other = dict(self.row, IP='192.0.2.60')
        self.write([self.row, other])
        result = self.cli('--client', '192.0.2.50', '--timeline', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('2026-11-23T12:00Z\t1\t1\t0', result.stdout)
        result = self.cli('--clients')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('192.0.2.50', result.stdout)
        self.assertIn('192.0.2.60', result.stdout)

    def test_cli_rules_does_not_write_input(self):
        self.write([self.row])
        before = self.path.read_bytes()
        result = self.cli('--rules')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '||synthetic.invalid^\n')
        self.assertEqual(self.path.read_bytes(), before)

    def test_invalid_record_never_echoes_private_values(self):
        for field, value in [('QH', 'private-secret/path'), ('IP', 42),
                             ('T', 'private-secret'), ('Result', None),
                             ('Result', {'IsFiltered': 'false'})]:
            with self.subTest(field=field, value=value):
                row = dict(self.row)
                row[field] = value
                self.write([self.row, row])
                result = self.cli('--rules')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                self.assertIn('line 2', result.stderr)
                self.assertNotIn('private-secret', result.stderr)
                self.assertNotIn('Traceback', result.stderr)

    def test_duplicate_keys_and_truncation_rejected(self):
        for text in ['{"QH":"secret.invalid","QH":"other.invalid"}',
                     '{"QH":"secret.invalid",', 'null', '[]']:
            with self.subTest(text=text):
                self.path.write_text(text)
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('secret.invalid', result.stderr)
                self.assertNotIn('Traceback', result.stderr)

    def test_unknown_mode_rejected_by_cli(self):
        self.write([self.row])
        result = subprocess.run([sys.executable, m.__file__, str(self.path), '--format', 'bad'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
