"""Offline publication guard for common pasted private identifiers.

Inspired by Gathin23/cleanyourtv's MIT documentation privacy checks:
https://github.com/Gathin23/cleanyourtv/blob/main/tests/test_doc_identifiers.py
Original implementation, not copied upstream code. Pattern detection is not
an anonymity guarantee: reviewers must still inspect prose and images.
Diagnostics give file, line and category, never the matched private value.
"""
from pathlib import Path
import ipaddress
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EMAIL = re.compile(r'(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
MAC = re.compile(r'(?i)(?<![\w:])(?:[0-9a-f]{2}:){5}[0-9a-f]{2}(?![\w:])')
IPV4 = re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
LOCAL = re.compile(r'(?i)\b[\w-]+(?:\.[\w-]+)*\.local\b')
HOME = re.compile(r'(?:/Users/|/home/|[A-Za-z]:\\Users\\)(?!<|Shared\b|Public\b)[\w.-]+')
SECRET = re.compile(r'(?i)\b(?:password|authorization|api[_-]?key|access[_-]?token)\s*[:=]\s*["\']?([^\s"\'<>`]{12,})')


def categories(line):
    found = set()
    for label, pattern in [('email', EMAIL), ('MAC', MAC), ('local hostname', LOCAL),
                           ('personal home path', HOME), ('credential assignment', SECRET)]:
        if pattern.search(line):
            found.add(label)
    for value in IPV4.findall(line):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        # Only documentation ranges and loopback are acceptable examples.
        if not (address.is_loopback or address.is_unspecified or any(address in net for net in (
                ipaddress.ip_network('192.0.2.0/24'), ipaddress.ip_network('198.51.100.0/24'),
                ipaddress.ip_network('203.0.113.0/24')))):
            found.add('IP address')
    # IPv6 literals: do not mistake firmware versions or ordinary prose for one.
    for value in re.findall(r'(?<![\w:])\[?([0-9a-fA-F:]*:[0-9a-fA-F:.:%]+)\]?', line):
        try:
            address = ipaddress.ip_address(value.split('%', 1)[0])
        except ValueError:
            continue
        if address.version == 6 and not (address.is_loopback or address.is_unspecified or
                                        address in ipaddress.ip_network('2001:db8::/32')):
            found.add('IP address')
    return sorted(found)


def findings(root):
    root = Path(root)
    pages = list(root.glob('*.md')) + list((root / 'docs').rglob('*.md'))
    # Do not report input values: CI logs are themselves a disclosure surface.
    return ['{}:{}: {}'.format(path.relative_to(root), number, category)
            for path in sorted(pages)
            for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1)
            for category in categories(line)]


class DocsPrivacyTest(unittest.TestCase):
    def test_repository_docs_have_no_common_private_identifiers(self):
        self.assertEqual([], findings(ROOT))

    def test_synthetic_identifiers(self):
        cases = [('person@example.invalid', 'email'), ('aa:bb:cc:dd:ee:ff', 'MAC'),
                 ('10.23.45.67', 'IP address'), ('fe80::1234', 'IP address'),
                 ('fd12:3456::1', 'IP address'), ('television.local', 'local hostname'),
                 ('/home/alice/log.json', 'personal home path'),
                 ('password=synthetic-secret-value', 'credential assignment')]
        for value, expected in cases:
            with self.subTest(category=expected):
                self.assertIn(expected, categories(value))

    def test_diagnostics_do_not_echo_identifiers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = 'sensitive-person@example.invalid'
            (root / 'README.md').write_text(value)
            result = findings(root)
            self.assertEqual(['README.md:1: email'], result)
            self.assertNotIn(value, str(result))

    def test_safe_documentation_examples_and_firmware(self):
        for value in ('192.0.2.5', '198.51.100.2', '203.0.113.4', '127.0.0.1',
                      '2001:db8::2', '::1', 'V0000.09.09G.P0930',
                      'https://github.com/HALCONDEORO/vidaa-clean-tv', '<tv-address>'):
            with self.subTest(example=value):
                self.assertEqual([], categories(value))


if __name__ == '__main__':
    unittest.main()
