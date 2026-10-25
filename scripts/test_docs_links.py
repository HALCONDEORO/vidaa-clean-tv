#!/usr/bin/env python3
"""Offline test: internal links and anchors in Markdown files resolve.

Run directly:  python3 scripts/test_docs_links.py -v
or as module:  python3 -m unittest scripts.test_docs_links

Checks every [text](target) and ![alt](target) in *.md files:
- external targets (http://, https://, mailto:, tel:) are skipped;
- pure anchors (#x) are checked against the file's own headings;
- relative paths must exist; their #anchor must match a heading slug.
GitHub slug rules: lowercase, drop characters outside [a-z0-9 -], spaces to
hyphens. Docs are English/ASCII, which keeps this predictable.
"""

import os
import re
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)[^)]*\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def slugify(heading):
    text = heading.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = text.replace("_", "")
    return re.sub(r"\s", "-", text)


def heading_slugs(path):
    slugs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = HEADING_RE.match(line)
            if m:
                slugs.append(slugify(m.group(1)))
    return slugs


def markdown_files():
    found = []
    for base, dirs, names in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in names:
            if name.endswith(".md"):
                found.append(os.path.join(base, name))
    return sorted(found)


class DocsLinksTest(unittest.TestCase):
    def test_internal_links_resolve(self):
        errors = []
        slug_cache = {}
        for path in markdown_files():
            rel = os.path.relpath(path, REPO_ROOT)
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    for target in LINK_RE.findall(line):
                        if target.startswith(SKIP_PREFIXES):
                            continue
                        if target.startswith("#"):
                            dest_file, anchor = path, target[1:]
                        else:
                            dest, _, anchor = target.partition("#")
                            dest_file = os.path.normpath(
                                os.path.join(os.path.dirname(path), dest))
                        if not os.path.exists(dest_file):
                            errors.append(
                                f"{rel}:{lineno}: missing file for '{target}'")
                            continue
                        if anchor:
                            if dest_file not in slug_cache:
                                slug_cache[dest_file] = heading_slugs(dest_file)
                            if anchor not in slug_cache[dest_file]:
                                errors.append(
                                    f"{rel}:{lineno}: no heading matching "
                                    f"anchor '#{anchor}'")
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + sys.argv[1:])
