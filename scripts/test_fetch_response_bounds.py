"""Offline synthetic response-bound regressions, no external accounts or TV."""
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
import fetch_query_log as m


class FakeResponse(io.BytesIO):
    def __init__(self, body):
        super().__init__(body)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


class ResponseBoundTests(unittest.TestCase):
    def fetch(self, body):
        response = FakeResponse(body)
        with patch.object(m.urllib.request, 'build_opener') as factory:
            factory.return_value.open.return_value = response
            try:
                value = m.fetch_page('http://192.0.2.1', 'synthetic', 'fake', 1)
            finally:
                self.assertEqual(response.read_sizes, [m.MAX_PAGE_BYTES + 1])
        return value

    def test_valid_small_page(self):
        self.assertEqual(self.fetch(b'{"data": []}'), {'data': []})

    def test_exact_byte_boundary_accepted(self):
        with patch.object(m, 'MAX_PAGE_BYTES', 64):
            self.assertEqual(self.fetch(b'{"data": []}' + b' ' * 52), {'data': []})

    def test_oversized_page_rejected_without_body(self):
        with patch.object(m, 'MAX_PAGE_BYTES', 64):
            with self.assertRaisesRegex(ValueError, 'byte limit') as error:
                self.fetch(b'private-secret' * 100)
        self.assertNotIn('private-secret', str(error.exception))

    def test_invalid_json_and_utf8_are_private(self):
        for body in [b'private-secret', b'"private-secret\xff"', b'{"private-secret":']:
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, '^Invalid JSON response from AdGuard Home$'):
                self.fetch(body)

    def test_decoder_recursion_error_is_private(self):
        # The C decoder's depth threshold varies across supported Python versions.
        # Test our exception contract, not one interpreter's recursion threshold.
        with patch.object(m.json, 'loads', side_effect=RecursionError('private-secret')):
            with self.assertRaisesRegex(ValueError, '^Invalid JSON response from AdGuard Home$') as error:
                self.fetch(b'[]')
        self.assertNotIn('private-secret', str(error.exception))

    def test_failed_fetch_does_not_replace_existing_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'export.json'
            dest.write_text('original private export')
            args = ['fetch_query_log.py', '--host', 'http://192.0.2.1', '--user', 'synthetic', '-o', str(dest)]
            with patch.object(sys, 'argv', args), patch.dict(os.environ, ADGUARD_PASSWORD='fake'), patch.object(m, 'fetch_page', side_effect=ValueError('Invalid JSON response from AdGuard Home')):
                with self.assertRaises(SystemExit):
                    m.main()
            self.assertEqual(dest.read_text(), 'original private export')


if __name__ == '__main__':
    unittest.main()
