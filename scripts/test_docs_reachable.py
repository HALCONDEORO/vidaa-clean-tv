"""Offline guard for documentation with no path from a reader entry point.

Inspired by Gathin23/cleanyourtv's documentation reachability check (MIT),
https://github.com/Gathin23/cleanyourtv/blob/main/tests/test_docs_pages_reachable.py
Original implementation here; no upstream code copied.
"""
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)')


def prose(text):
    """Code examples are not navigation, including fenced blocks with tildes."""
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r'`[^`\n]*`', '', '\n'.join(lines))


def unreachable(root):
    root = Path(root).resolve()
    pages = {p.resolve() for p in root.glob('*.md')}
    pages |= {p.resolve() for p in (root / 'docs').rglob('*.md')
              if 'templates' not in p.relative_to(root / 'docs').parts}
    entries = [root / name for name in ('README.md', 'FAQ.md')]
    seen = set()
    pending = [p for p in entries if p in pages]
    while pending:
        page = pending.pop()
        if page in seen:
            continue
        seen.add(page)
        for href in LINK.findall(prose(page.read_text(encoding='utf-8'))):
            parsed = urlsplit(href.strip('<>'))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = unquote(parsed.path)
            dest = ((root if path.startswith('/') else page.parent) / path.lstrip('/')).resolve()
            if dest.suffix == '.html':
                dest = dest.with_suffix('.md')
            candidates = [dest, dest / 'index.md', dest / 'README.md']
            pending.extend(p for p in candidates if p in pages and p not in seen)
    return sorted(str(p.relative_to(root)) for p in pages - seen)


class ReachableDocsTest(unittest.TestCase):
    def test_repository_pages_reachable(self):
        self.assertEqual([], unreachable(ROOT))

    def test_graph_not_just_incoming_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'README.md').write_text('[start](docs/start.html#heading)')
            (root / 'docs/start.md').write_text('[back](../README.md)')
            (root / 'docs/a.md').write_text('[b](b.md)')
            (root / 'docs/b.md').write_text('[a](a.md)')
            self.assertEqual(['docs/a.md', 'docs/b.md'], unreachable(root))

    def test_code_images_and_remote_links_do_not_link_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'README.md').write_text('```md\n[x](docs/a.md)\n```\n'
                '~~~\n[x](docs/a.md)\n~~~\n`[x](docs/a.md)`\n'
                '![image](docs/a.md)\n[x](https://example.invalid/docs/a.md)')
            (root / 'docs/a.md').write_text('# Orphan')
            self.assertEqual(['docs/a.md'], unreachable(root))


if __name__ == '__main__':
    unittest.main()
