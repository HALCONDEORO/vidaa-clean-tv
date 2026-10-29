# Changelog

Dated entries, newest first. There are no tagged releases yet; "merged to
main" is the unit of change.

## 2026-10-29 - Client inventory for offline logs

- Add `classify_dns_log.py --clients` to list client identifiers, query counts
  and filtered counts before choosing a `--client` filter.
- Label missing identifiers unknown, escape identifiers safely, and reject
  combinations with other output modes. No network/device discovery occurs.
- Add usage examples and three offline regression tests.

## 2026-10-29 - Friendly local-input errors

- Report unreadable/missing query logs and comparison/validation lists with
  short path/permissions guidance, instead of tracebacks.
- Three offline regressions cover missing logs in both modes, unreadable
  comparisons and missing primary/upstream validator files.
- Inputs remain read-only. No files are created or repaired automatically.

## 2026-10-29 - Handle truncated HTTP exports

- Report incomplete or malformed HTTP responses without an unhandled
  traceback. Keep the prior export untouched when the response is truncated.
- A local HTTP-server regression covers premature connection close and
  output preservation. No retries, remote servers or hardware changes.

## 2026-10-29 - Handle timestamp boundaries in timelines

- Exclude offsets outside Python's UTC date range and unrenderable buckets
  instead of crashing on imported timestamps; count them as unusable times.
- Floor negative fractional epochs so pre-1970 queries stay in their actual
  bucket, rather than being moved into 1970 by integer truncation.
- Three offline regression tests; no hardware or DNS changes.

## 2026-10-29 - Refuse unsupported classifier filter semantics

- Do not treat conditional AdGuard rules as unconditional domain coverage.
  Reject options, exceptions, wildcards and malformed filter lines with a
  line-number error before printing a report or candidate rules.
- Keep plain hostnames and unconditional `||hostname^` rules, case folding
  and one trailing root dot. This classifier is not an AdGuard engine.
- Three offline regression tests; no DNS rules or hardware changed.

## 2026-10-29 - Check hostnames inside block rules

- Apply hostname label and length checks inside `||domain^` rules too, not
  just plain hostnames. Reject empty labels, edge hyphens and oversized names.
- Keep the validator's supported wildcard patterns and underscore labels.
  This is a supported-syntax check, not full AdGuard filter validation.
- Three offline regressions; no blocklist contents or TV settings change.

## 2026-10-29 - Validate export endpoints before credentials

- Reject malformed server URLs, embedded credentials, queries and fragments
  before requesting a password or making a network request.
- Keep network errors and refused redirect destinations out of diagnostics.
  HTTP(S), IPv6 and reverse-proxy base paths remain supported. Plain HTTP is
  still unencrypted; use it only on a network you trust.
- Four offline regression tests; no server, DNS or TV changes.

## 2026-10-29 - Private, atomic query-log exports

- Create exports with owner-only permissions on POSIX and atomically replace
  the destination only after successful serialization and flush.
- Preserve prior exports on write failure, clean temporary files, and replace
  output symlinks rather than writing through them. Windows users should use
  a private directory with appropriate ACLs.
- Five offline tests cover permissions, replacement, failure and symlink cases.
  No endpoint, credentials, DNS rules or TV settings change.

## 2026-10-29 - Evidence-first quick start

- Label hardware verification as pending in the README opening and model table.
- Add date and per-step evidence fields to the model report form.
- Add synthetic offline examples with regression-tested expected output.
  Examples are not real captures or recommended blocking rules.

## 2026-10-29 - Validate imported DNS records

- Skip malformed nested query records and names outside the classifier's
  supported domain syntax before aggregation or candidate-rule output.
- Validate single-page exports with the same schema checks as pagination;
  reject nonpositive page sizes before requesting credentials or network data.
- Reject multiple trailing DNS root dots before normalization.
- Add six offline regression tests. No TV settings, blocklist rules, DNS
  configuration or filtering thresholds change.

## 2026-10-28 - Manual-sourced VIDAA menu paths

- docs/01: Enhanced Viewing / ACR, personalised ads and advertising-ID reset
  paths, the consent menu (Support → Disclaimer and Privacy, incl. "Remove
  User Data") and an optional hands-free voice step, all from the official
  VIDAA U5/U6/U9 manuals as compiled by the Clean Your TV non-Android guide
  (cleanyour.tv/not-android, last checked 26 Oct 2026). The Privacy-section
  path from the earlier guides is kept as an alternative. All still
  sourced-but-unverified on the target TV.
- docs/05: firmware version path corrected to the manual path
  (Settings → Support → About / System Info → Version).
- README/NOTICE/docs/tv/hisense.md: Clean Your TV v3.1.0's non-Android guide
  credited and linked; its showcase now lists this project as the VIDAA
  route.

## 2026-10-25 - Claim alignment in docs/01

- docs/01-on-device-settings.md: removed absolutes ("Risk: none", "stops reporting what you watch", "breaks nothing") that survived the earlier editorial pass; effects on the target TV are now labeled documented-but-unverified, matching CONTRIBUTING.md and the README/TROUBLESHOOTING wording.

## 2026-10-25 - Upstream format compatibility

- load_blocklist and validate_blocklist skip '//' comments (the current upstream annotated edition uses them; loading it previously misread 575 comment lines).
- validate_blocklist accepts hyphenated hostnames (previously rejected real domains like ad-cmp.hismarttv.com; found by validating the live upstream list: 137 rules valid).
- End-to-end pipeline test: paged fetch against a local server, then classify + blocklist matching - the exact docs/03 flow.

## 2026-10-25 - Paginated query-log export

- fetch_query_log.py --pages N: keeps fetching older query-log pages until a short page (previously one page only, so long observation windows were silently truncated). Single-page default unchanged. When the export stops on a full page, it warns that older entries may remain (a full page means possible truncation, not certain truncation).

## 2026-10-25 - Timeline and model index

- classify_dns_log.py --timeline: per-bucket (default 60 minutes) filtered/unblocked counts from AdGuard exports; dnsmasq and plain inputs are rejected with a clear message.
- docs/tv/README.md: index of model pages with verification status.
- SECURITY.md: how to report script security issues; data-hygiene expectations.
- docs/03: --timeline usage and what request volume does and does not show.

## 2026-10-25 - Contributor readiness

- CONTRIBUTING.md: verification rule, new-model reporting, script and docs conventions.
- Issue templates: new VIDAA model report, documentation fix.
- scripts/test_docs_links.py: offline check that internal links and anchors resolve; runs in CI.

## 2026-10-25 - Docs restructure

- README reorganized as a quick-start table in the style of Clean Your TV.
- New: TROUBLESHOOTING.md, docs/tv/toshiba-50uv1553db.md, docs/tv/hisense.md.
- Editorial pass: unverified claims relabeled with their actual strength (documented setting vs. hypothesis vs. verified log row).

## 2026-10-25 - First public version

- docs/01-05: on-device settings, DNS filtering, observing DNS, local control (MQTT), first-hardware-session protocol.
- TESTING.md hardware log (empty until the first session on the Toshiba 50UV1553DB).
- scripts/: classify_dns_log.py, fetch_query_log.py, validate_blocklist.py with an offline test suite; CI on Python 3.10-3.13.
