# Hardware test log

Target device: Toshiba 50UV1553DB, VIDAA, Europe region.

Rule: a claim counts as verified only with a row in the session log below -
date, firmware version, step, expected result, observed result, reverted
(yes/no). Everything else is a sourced claim, labeled as such.

## Status table

| Claim | Source | Status on UV1553DB |
|---|---|---|
| VIDAA has no ADB, no sideloading, no package list | cleanyourtv.wiki, justatv.eu | Consistent across all sources; to be re-confirmed on device |
| Privacy settings exist and are reversible | vidaa.com policy, justatv.eu, velmo.one | Menu names unverified on this model |
| Upstream blocklist cleans the home screen, YouTube/Netflix keep working | ipanalytics (Hisense, Germany) | Not tested on Toshiba |
| MQTT local control works on Toshiba VIDAA | warrenrees/ha_vidaatv README | Not tested on this model |

The step-by-step protocol for the first session is [docs/05-first-hardware-session.md](docs/05-first-hardware-session.md).

## Session log

| Date | Firmware | Step | Expected | Observed | Reverted |
|---|---|---|---|---|---|
| _pending first session_ | | | | | |
