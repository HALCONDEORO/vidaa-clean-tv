#!/usr/bin/env python3
"""Guard: links on the published Pages site must not 404 by construction.

Every relative Markdown link in a Jekyll-published page must resolve to a
path that Jekyll also publishes. Links into excluded working trees
(docs/templates/, scripts/, examples/, blocklists/) render as real 404s on
https://halcondeoro.github.io/vidaa-clean-tv/ even though the source file
exists in the repo; those must be absolute repo URLs instead. Stdlib only.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def jekyll_excludes():
    """Parse the top-level exclude: list from _config.yml (flat entries only)."""
    excludes = []
    in_block = False
    for line in (ROOT / "_config.yml").read_text(encoding="utf-8").splitlines():
        if re.match(r"^exclude:\s*$", line):
            in_block = True
            continue
        if in_block:
            match = re.match(r"^\s+-\s+(\S+)\s*$", line)
            if match:
                excludes.append(match.group(1).rstrip("/"))
            elif line and not line.startswith(" "):
                break
    return excludes


def is_excluded(relpath, excludes):
    parts = relpath.split("/")
    for entry in excludes:
        target = entry.split("/")
        if parts[: len(target)] == target or relpath == entry:
            return True
    return False


def prose(text):
    in_fence = False
    out = []
    for line in text.splitlines():
        if re.match(r"^\s{0,3}```", line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(re.sub(r"`[^`\n]*`", "", line))
    return "\n".join(out)


class PublishableLinksTests(unittest.TestCase):
    def test_relative_links_on_published_pages_stay_published(self):
        excludes = jekyll_excludes()
        self.assertIn("docs/templates", excludes)  # guard the parser itself
        published = [p for p in ROOT.glob("*.md")]
        published += [
            p
            for p in (ROOT / "docs").glob("*.md")
            if not is_excluded(p.relative_to(ROOT).as_posix(), excludes)
        ]
        self.assertTrue(published)
        broken = []
        for page in published:
            for target in LINK.findall(prose(page.read_text(encoding="utf-8"))):
                target = target.split("#", 1)[0]
                if not target or re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                    continue
                absolute = (page.parent / target).resolve()
                rel = absolute.relative_to(ROOT.resolve()).as_posix()
                if is_excluded(rel, excludes):
                    broken.append("%s -> %s (excluded from Pages)" % (page.name, target))
                elif not absolute.exists():
                    broken.append("%s -> %s (missing file)" % (page.name, target))
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
