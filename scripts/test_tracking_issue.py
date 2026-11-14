#!/usr/bin/env python3
"""Tests for tracking_issue.sh using a stubbed gh binary. Stdlib, offline."""

import os
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracking_issue.sh")

# A fake gh that mimics only the documented behaviours the script relies on:
# `issue list --json number --jq ...` prints a number or nothing, and
# `issue create` prints the new issue URL on stdout.
FAKE_GH = """#!/usr/bin/env bash
set -euo pipefail
case "$1 $2" in
  "label create")
    exit 0
    ;;
  "issue list")
    if [ -f "$FAKE_STATE/issue_exists" ]; then
      echo 7
    fi
    exit 0
    ;;
  "issue create")
    touch "$FAKE_STATE/issue_exists"
    echo "https://github.com/HALCONDEORO/vidaa-clean-tv/issues/42"
    exit 0
    ;;
  *)
    echo "unexpected gh call: $*" >&2
    exit 1
    ;;
esac
"""


def make_fake_gh(directory):
    state = os.path.join(directory, "state")
    os.mkdir(state)
    fake = os.path.join(directory, "gh")
    with open(fake, "w", encoding="utf-8") as handle:
        handle.write(FAKE_GH)
    os.chmod(fake, os.stat(fake).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    env = dict(os.environ, GH_BIN=fake, FAKE_STATE=state)
    return env, state


class TrackingIssueTests(unittest.TestCase):
    def run_script(self, env):
        return subprocess.run(
            ["bash", SCRIPT], env=env, capture_output=True, text=True, timeout=30
        )

    def test_initial_run_creates_issue_and_parses_url_number(self):
        with tempfile.TemporaryDirectory() as directory:
            env, _ = make_fake_gh(directory)
            result = self.run_script(env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "number=42")

    def test_reuse_returns_existing_issue_without_create(self):
        with tempfile.TemporaryDirectory() as directory:
            env, state = make_fake_gh(directory)
            open(os.path.join(state, "issue_exists"), "w").close()
            result = self.run_script(env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "number=7")

    def test_unresolvable_number_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            env, _ = make_fake_gh(directory)
            broken = os.path.join(directory, "gh-broken")
            with open(env["GH_BIN"], "r", encoding="utf-8") as handle:
                source = handle.read()
            source = source.replace(
                'echo "https://github.com/HALCONDEORO/vidaa-clean-tv/issues/42"',
                'echo "unexpected output with no url"',
            )
            with open(broken, "w", encoding="utf-8") as handle:
                handle.write(source)
            os.chmod(broken, 0o755)
            env["GH_BIN"] = broken
            result = self.run_script(env)
            self.assertEqual(result.returncode, 1)
            self.assertIn("could not resolve", result.stderr)


if __name__ == "__main__":
    unittest.main()
