# Changelog

Dated entries, newest first. There are no tagged releases yet; "merged to
main" is the unit of change.

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
