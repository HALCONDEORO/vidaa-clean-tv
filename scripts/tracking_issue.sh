#!/usr/bin/env bash
# Find or create the single upstream-watch tracking issue.
# Prints "number=N" on stdout, nothing else. Requires a gh CLI authenticated
# with issues:write on this repository (GH_BIN overrides the binary for tests).
set -euo pipefail

GH="${GH_BIN:-gh}"

"$GH" label create upstream-watch --color BFD4F2 \
  --description "Upstream blocklist change watcher" --force >/dev/null

num=$("$GH" issue list --label upstream-watch --state open \
  --json number --limit 1 --jq '.[0].number // empty')

if [ -z "$num" ]; then
  # gh issue create prints the new issue URL on stdout; the issue number is
  # the last path segment of that documented URL.
  url=$("$GH" issue create --label upstream-watch \
    --title "Upstream blocklist watch" \
    --body "Tracks ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist. Last seen commit: none yet.")
  num=${url##*/}
fi

case "$num" in
  *[!0-9]*|"")
    echo "could not resolve the tracking issue number" >&2
    exit 1
    ;;
esac

echo "number=$num"
