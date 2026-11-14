# Application compatibility: evidence, not a guarantee

DNS filtering can remove a resource an application needs along with a
promotion. This table records what was reported, on which setup, and what
remains unknown. **No new TV or app tests were performed for this page.**

Read [platform compatibility](07-compatibility.md) first. An app result does
not transfer automatically to another model, region, firmware or list revision.

## Status vocabulary

- **works (owner-reported):** a source says the app worked in its setup;
  this is not an independent test by the maintainer.
- **broken (reported):** a source describes a failure; severity and recovery
  are limited to the functions actually described.
- **untested:** no applicable result is recorded here. It does not mean broken
  or safe. A blank report field must never be treated as a pass.

## Current matrix

| Application / feature | Model, firmware and region | DNS route / list evidence | Status and reported result | Limits and source |
|---|---|---|---|---|
| YouTube | Hisense 65A67H; V0000.09.09G.P0930; region not recorded | AdGuard Home and the IPanalytics upstream subscription, 2026-11-08; exact list revision not recorded | works (owner-reported) after enabling the list | Playback quality, login, casting and in-video ads were not itemised. No raw query-log export analysed. [Session log](../TESTING.md#session-log), contributed by [OliverS45](https://github.com/HALCONDEORO/vidaa-clean-tv/pull/31). |
| Netflix | Hisense 65A67H; V0000.09.09G.P0930; region not recorded | Same 2026-11-08 owner session and unpinned upstream subscription | works (owner-reported) after enabling the list | DRM, resolution, profiles and long-session behavior were not itemised. This result predates the 11 November list update. [Session log](../TESTING.md#session-log), [OliverS45 contribution](https://github.com/HALCONDEORO/vidaa-clean-tv/pull/31). |
| Prime Video thumbnails and parts of its UI | Model, firmware and region not specified in the cited trade-off | Six active recommendation API/UI rules; report dated 2026-11-09, explicitly documented in upstream commit `045c377` (2026-11-11) | broken (reported, thumbnails/UI only); upstream describes the trade-off and credits a fork that disables those six rules | Not proof that all playback fails. Not a 65A67H or Toshiba test. [IPanalytics update](https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist/commit/045c377), [Owen3H fork](https://github.com/Owen3H/Hisense-VIDAA-DNS-Clean-TV-Blocklist). |
| YouTube, Netflix and Prime Video | Toshiba 50UV1553DB; firmware not yet logged; Europe target | No completed application/DNS session in this project's log | untested | Do not copy the Hisense result into this row. [Toshiba page](tv/toshiba-50uv1553db.md), [test log](../TESTING.md). |
| Other apps or other firmware/model combinations | Not recorded | No applicable session recorded here | untested | Add a scoped report; absence of a complaint is not a pass. |

The upstream maintainer also reports YouTube and Netflix working on its
Hisense setup in Europe/Germany. Its tested setup does not use Prime Video.
Those statements are external reports, not additional tests in our log;
see the [dated snapshot](02-dns-filtering.md#upstream-snapshot-11-november-2026).

## Recover without turning a workaround into a universal allowlist

Use the [app-breakage playbook](../TROUBLESHOOTING.md#an-app-stopped-loading-after-enabling-the-blocklist):
reproduce with the query log open, isolate the smallest relevant change and
retest the same action. Record what was reverted and what recovered. An allow
exception may restore a feature and also restore traffic you intended to block.
This page installs no rules and supplies no automatic app allowlist.

## What an app report needs

Use [contribution guidance](../CONTRIBUTING.md#reporting-a-new-model) and record:

- Date, exact model, region and full firmware/build; app version if visible.
- Route and DNS filter version; list URL and revision or last-refresh date.
  If a revision is unknown, say so instead of guessing from today's list.
- Exact action: launch, sign-in, browse artwork, start playback, seek,
  subtitles or casting. A successful launch alone is not a playback test.
- Expected and observed result before and after one change, including any
  unrelated breakage; repeat the same action after reverting that change.
- Source and evidence limits. Never include credentials, account identifiers,
  IP/MAC addresses, `.local` names, exact times, long token-like identifiers or
  a raw mixed-device DNS export in a public report.

A future test may narrow or supersede a row, but keep the original result's
scope and date. A firmware/list update is a reason to retest, not to silently
promote an old owner report into current compatibility.
