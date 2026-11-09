# Hisense VIDAA

Status: best-documented VIDAA family for this project, mostly through other
people's published work. One owner-reported DNS session on a Hisense 65A67H is
logged in [../../TESTING.md](../../TESTING.md); nothing else has been tested
on a Hisense set here.

| What | Status |
|---|---|
| Upstream DNS blocklist | Tested by its author on Hisense VIDAA sets in Europe (Germany), AdGuard Home on a Raspberry Pi; YouTube and Netflix reported working |
| Settings paths in [../01-on-device-settings.md](../01-on-device-settings.md) | Written from Hisense-family guides; verify the wording on your model |
| This project's own hardware tests | Route 2 (DNS) on a 65A67H, firmware V0000.09.09G.P0930, 2026-11-08: TV queries blocked, home screen reported cleaner, YouTube and Netflix working. Route 1 settings not yet logged |

The [Clean Your TV non-Android guide](https://cleanyour.tv/not-android)
covers the VIDAA settings route step by step, sourced to the official VIDAA
U5/U6/U9 manuals; it is the best-maintained external reference for the menu
paths right now.

Newer Hisense generations may call the system **HomeOS U9 / U9.5** instead of
VIDAA. Per the justatv.eu guide it is the same system under a new name, with
the settings in the same places.

Watch out: Hisense also sells Android TV / Google TV models, and some
China-market sets branded "VIDAA" actually run Android underneath. Those
belong to [Clean Your TV](https://github.com/Gathin23/cleanyourtv) territory,
not to this project.
