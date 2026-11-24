# Notices and credits

This project is original work, built on public research by others:

- **AdguardTeam/AdGuardHome** (GPL-3.0) - native query log format reference
  for the offline JSONL adapter. No source code copied, linked or vendored;
  only documented data-field compatibility implemented with Python stdlib.
  https://github.com/AdguardTeam/AdGuardHome/discussions/5653
  https://github.com/AdguardTeam/AdGuardHome/blob/bb189854/internal/querylog/entry.go
  https://github.com/AdguardTeam/AdGuardHome/blob/bb189854/internal/querylog/decode.go

- **Gathin23/cleanyourtv** (MIT License) - goal inspiration. No code copied.
  https://github.com/Gathin23/cleanyourtv
- **cleanyourtv.wiki Hisense compatibility page** - documentation source for
  Clean Your TV needing Android and not covering VIDAA OS sets.
  https://cleanyourtv.wiki/tv/hisense/
- **justatv.eu** - documentation source for VIDAA settings paths and for the
  conclusion that, with no ADB on VIDAA, cleanup means settings and network
  filtering. https://justatv.eu/en/guides/cleaning-up-a-hisense-television-with-vidaa
- **velmo.one ACR guide** - documentation source for the ACR opt-out menu
  paths in the device Settings menu.
  https://velmo.one/guides/turn-off-acr-hisense-tv/
- **Clean Your TV non-Android guide (cleanyour.tv/not-android)** -
  documentation source for the VIDAA menu paths in docs/01 and docs/05,
  compiled there from the official Hisense VIDAA U5/U6/U9 manuals.
  https://cleanyour.tv/not-android
- **ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist** (Apache License 2.0) -
  the upstream DNS blocklist this project subscribes to. The list is
  referenced by URL, not vendored. If we ever vendor a copy, the Apache-2.0
  license text and attribution will ship alongside it.
  https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist
- **warrenrees/ha_vidaatv** (MIT License) - documentation source for the
  VIDAA local MQTT control interface. No code copied.
  https://github.com/warrenrees/ha_vidaatv
- **VIDAA OS privacy policy** - official description of the Enhanced Viewing
  Service / ACR opt-out. https://www.vidaa.com/os-privacy-policy/

- **OliverS45/vidaa-clean-tv** (MIT License) - owner-reported Hisense 65A67H
  DNS session and setup troubleshooting, already imported with authorship in
  PR #31; used as compatibility evidence, not a new hardware test.
  https://github.com/OliverS45/vidaa-clean-tv
- **nineodernein/hisense-vidaa-clean-home** - documentation source for the
  distinction between its reported model-specific native Home trial and its
  generalized public package. Referenced for scope only; no code or device
  files copied and no native modification supported here.
  https://github.com/nineodernein/hisense-vidaa-clean-home

- **carteakey/alvidaa** - model-specific community DNS-observability report,
  credited for the visibility caution only. No code, block rules, root,
  certificate, firewall or update-freezing instructions copied or supported.
  https://carteakey.dev/blog/alvidaa/alvidaa/

"VIDAA" and "Hisense" are trademarks of their respective owners. This is an
independent community project, not affiliated with or endorsed by them.
