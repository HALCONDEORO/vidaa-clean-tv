# Changelog

Dated entries, newest first. Releases are annotated git tags (vX.Y.Z, see
RELEASE.md); the first tag is v0.1.0. Between tags, "merged to main" is the
unit of change.

 HEAD
## 2026-11-09 - Playbook for apps broken by blocking

- TROUBLESHOOTING's "app stopped loading" entry becomes a step-by-step
  experiment (query log, `seen_filtered`, smallest unblock, log it), with
  the documented Prime Video case: a fork restores Prime Video's thumbnails
  by disabling six upstream rules (four recommendation API hosts on
  hismarttv.com, two recommendation-UI hosts on vidaahub.com) while keeping
  the launcher rules (https://github.com/Owen3H/Hisense-VIDAA-DNS-Clean-TV-Blocklist).

## 2026-11-09 - Compare community blocklists in docs/02

- A short "other community lists" section covers Okazakee/tv-dns-blocklist
  (active, multi-brand, non-breaking policy, VIDAA domains upstream lacks),
  why forum-recommended lists that later go 404
  (jnmobilesoft/hisense-u8n-pihole-blocklist) argue for subscribing over
  copying, and Perflyst/PiHoleBlocklist for other brands. One VIDAA list at
  a time; no rules copied.

## 2026-11-09 - FAQ for pre-purchase and day-one questions

- New FAQ.md answers the questions forums keep asking: does VIDAA show ads,
  can they be turned off, is an account required, what data is collected,
  why no root/ADB, what blocking breaks and which TVs are covered - each
  answer routed to the doc that carries the evidence.

## 2026-11-09 - Release versioning with annotated tags

- RELEASE.md defines vMAJOR.MINOR.PATCH tags cut lazily from green main,
  with the CHANGELOG as source of truth; the first tag is v0.1.0. No build
  artifacts: a release is the tag plus its CHANGELOG section.

## 2026-11-09 - Pi-hole setup and observation docs match AdGuard's

- docs/02 walks Pi-hole through subscribing the blocklist (Lists/Adlists,
  gravity update) and scoping it to only the TV (groups/clients), with the
  same revert-by-removal guidance AdGuard had.
- docs/03 covers observing through Pi-hole: classify a copy of
  `/etc/pihole/pihole-FTL.db` (copied, never moved), and the timeline note
  now correctly says timestamps come from AdGuard JSON exports or Pi-hole
  FTL databases.

## 2026-11-09 - Classify Pi-hole FTL databases

- `classify_dns_log.py` auto-detects a Pi-hole `pihole-FTL.db` (SQLite
  header) and reads its `queries` table read-only: domain, client, epoch
  timestamp and blocked status (gravity, regex, denylist, external blocks
  and their CNAME variants). `--timeline`, `--clients`, `--rules` and the
  table output all work on it; a SQLite file without the expected schema
  exits with a clear error instead of a traceback.
- Offline regressions build a temporary FTL database with the stdlib
  sqlite3 module: counts and blocked mapping, timeline buckets, client
  listing, rules mode and the schema-mismatch error.

## 2026-11-09 - fetch_query_log caps --limit per page

- Reject `--limit` above 10000. AdGuard Home's query-log API accepts any
  limit (default page 500, no maximum: internal/querylog/searchparams.go),
  so a single huge page made the server scan and serialize that many entries
  at once; the cap keeps one request bounded and `--pages` (max 100) still
  reaches older entries.
- Offline regressions cover the limit cap; CI now discovers every
  `scripts/test_*.py` module instead of naming the test files one by one
  (the docs-link check runs inside discovery, not as a duplicate step).

## 2026-11-09 - DeepSource analysis configuration

- Add `.deepsource.toml` (Python analyzer, test files marked) so the
  DeepSource check installed on the repository runs real analysis instead of
  reporting "skipping" on every pull request. If it still skips after this
  merges, the remaining step is dashboard-side: activate analysis for the
  repo on app.deepsource.com or uninstall the integration.

## 2026-11-09 - CI also tests Python 3.14

- Add Python 3.14 (released 7 October 2025) to the test matrix and update
  the documented 3.10-3.14 range.

## 2026-11-09 - CI checks the supplement against the upstream list

- New `upstream-overlap` workflow job downloads the upstream Hisense VIDAA
  blocklist and validates the supplement with `--upstream`, enforcing the
  contribution rule that the supplement never duplicates upstream coverage.
  The unit-test matrix stays fully offline; this is the only job that needs
  the network.

## 2026-11-09 - Validator flags rules shadowed by a parent domain

- Report a rule as redundant when its parent domain is already listed, in
  the same list or in the upstream comparison list: `||example.com^` blocks
  the whole tree, and the classifier's comparison treats plain hostnames the
  same way, so a separate `||ads.example.com^` adds nothing. Exact-duplicate
  and exact-upstream-overlap errors are unchanged.
- Five offline regressions cover shadowing within a list, plain-hostname
  parents, upstream parents and the non-shadowed cases that must keep
  passing. The real supplement (empty by design) still validates.

## 2026-11-09 - Parse AdGuard RFC3339Nano timestamps on every supported Python

- Accept query-log times with 1-9 fractional-second digits. AdGuard Home
  formats entry times with Go's RFC3339Nano, and fromisoformat before
  Python 3.11 accepts only exactly 3 or 6 digits, so real exports lost every
  timestamp on Python 3.10 and timelines reported no timestamped queries.
  Fractions are normalized to microseconds, matching the 3.11+ parser.
- Offline regressions cover 1-, 7- and 9-digit fractions and a timeline run
  on a nanosecond export. Aggregation, tables, rules and client inventories
  are unchanged.

## 2026-11-08 - Explicit classifier output modes

- Reject conflicting timeline/domain options instead of silently ignoring them.
- Reject nonpositive domain thresholds and timeline bucket sizes before reading
  logs. Explicit domain thresholds are not accepted in timeline/client modes.
- Document the option matrix and add offline CLI regressions. Valid table,
  rule, timeline and client-inventory output is unchanged.

## 2026-11-08 - AdGuard Home setup troubleshooting

- Add TROUBLESHOOTING.md entries for port 53 held by `systemd-resolved` and
  for AdGuard Home listening only on `127.0.0.1`, both hit during the
  Hisense 65A67H session.
- Expand "no traffic from the TV" with the manual-IP, power-cycle, Docker
  bridge and IPv6 DNS checks.

## 2026-11-08 - First logged hardware session (Hisense 65A67H, DNS route)

- Log an owner-reported route 2 session on a Hisense 65A67H, firmware
  V0000.09.09G.P0930: the TV used AdGuard Home with the upstream blocklist,
  some queries were blocked, the home screen was reported cleaner, and
  YouTube and Netflix kept working.
- Add a model column to the TESTING.md session log and update the Hisense,
  model-index and README status lines. Route 1 and the Toshiba target remain
  unverified.

## 2026-10-29 - Client inventory for offline logs

- Add `classify_dns_log.py --clients` to list client identifiers, query counts
  and filtered counts before choosing a `--client` filter.
- Label missing identifiers unknown, prefix and escape identifiers safely, and reject
  combinations with other output modes. No network/device discovery occurs.
- Add usage examples and four offline regression tests, including literal
  spreadsheet import of formula-like identifiers.

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
