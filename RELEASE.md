# Releases

This project versions with annotated git tags, `vMAJOR.MINOR.PATCH`:

- **PATCH**: fixes that change no behavior anyone could depend on.
- **MINOR**: new, backward-compatible capabilities (a new script option, a
  new supported input format, a new CI check).
- **MAJOR**: breaking changes to script CLIs, output formats or documented
  behavior. 0.x means the interface can still shift; do not promise
  stability before v1.0.0.

Rules:

- The CHANGELOG is the source of truth: every user-visible change lands
  there first, dated, newest first.
- Tag from `main` only, after CI is green on the commit being tagged.
  Releases are cut lazily - when main has accumulated changes worth naming,
  not on a schedule.
- Tags are annotated and pushed by a maintainer:
  `git tag -a vX.Y.Z -m "vX.Y.Z" <merge-commit>` then
  `git push origin vX.Y.Z`.
- The tagged release line in the CHANGELOG gets a
  `## YYYY-MM-DD - vX.Y.Z` heading added in the same PR that introduces the
  tag, so the log and the tags never disagree.
- There are no build artifacts: a release is the tag plus its CHANGELOG
  section. The scripts run from a checkout.
