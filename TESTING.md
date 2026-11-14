# Hardware test log

Target device: Toshiba 50UV1553DB, VIDAA, Europe region. Sessions on other
VIDAA models are logged here too, with the model in its own column.

Rule: a claim counts as verified only with a row in the session log below -
date, firmware version, step, expected result, observed result, reverted
(yes/no). Everything else is a sourced claim, labeled as such.

## Status table

| Claim | Source | Status on UV1553DB |
|---|---|---|
| The Android ADB/package-cleanup route is not documented for the non-Android VIDAA sets covered here | cleanyourtv.wiki, justatv.eu; [compatibility scope](docs/07-compatibility.md) | No on-device capability check logged for this model; this is not a platform-wide claim about every VIDAA-branded set |
| Privacy settings exist and are reversible | vidaa.com policy, justatv.eu, velmo.one | Menu names unverified on this model |
| Upstream blocklist cleans the home screen, YouTube/Netflix keep working | ipanalytics (Hisense, Germany) | Not tested on Toshiba. Observed on one Hisense 65A67H, firmware V0000.09.09G.P0930 (session log, 2026-11-08) |
| MQTT local control works on Toshiba VIDAA | warrenrees/ha_vidaatv README | Not tested on this model |

The step-by-step protocol for the first session is [docs/05-first-hardware-session.md](docs/05-first-hardware-session.md).

## Session log

| Date | Model | Firmware | Step | Expected | Observed | Reverted |
|---|---|---|---|---|---|---|
| 2026-11-08 | Hisense 65A67H | V0000.09.09G.P0930 | Route 2: TV DNS set manually to an AdGuard Home instance on the LAN | TV queries appear in the AdGuard Home query log | TV queries appear in the query log once AdGuard Home listened on all addresses (power cycle suggested, not confirmed) | No |
| 2026-11-08 | Hisense 65A67H | V0000.09.09G.P0930 | Route 2: subscribe to the upstream `Blocked_Domains_AdGuard.txt` list | Some TV queries blocked; home screen less cluttered; YouTube and Netflix keep working | Some TV queries marked blocked; owner reports the home screen is cleaner; YouTube and Netflix still work | No |
| _pending_ | Toshiba 50UV1553DB | | First session (route 1) | | | |

Notes on the 2026-11-08 session: owner-reported, region not recorded, router a
FRITZ!Box (AdGuard Home ran on a separate device; TV DNS set on the TV). Route 1
(on-device settings) was not logged in this session, so its menu paths remain
unverified on this model. "Home screen is cleaner" is the owner's observation;
which tiles disappeared was not itemised. No query-log export was analysed.
