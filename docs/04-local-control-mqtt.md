# Local control over MQTT (preparatory guide - nothing verified on our TVs yet)

[warrenrees/ha_vidaatv](https://github.com/warrenrees/ha_vidaatv) (MIT) shows
that VIDAA TVs expose a local MQTT-based remote control interface with
on-screen PIN pairing, the same style of channel the official VIDAA mobile app
uses. Its README describes SSDP auto-discovery, a media-player entity (power,
volume, sources, apps), arbitrary remote key presses and optional Wake-on-LAN,
and lists "Hisense Smart TVs (2018+)", "Vidaa U platform TVs" and "Some
Toshiba TVs with Vidaa OS" as supported.

**Status in this project: exploration only.** No model covered by this
project - including the Toshiba 50UV1553DB - has a logged local-control
session. Pairing, key presses and state reading below are what a first
session would check, not instructions we have watched work.

## What this could mean for this project

- Scripted remote key presses (for example, navigating to a setting) from a
  device on the same network, which would make future settings sessions more
  repeatable.
- Reading power/source state as an extra observation channel alongside DNS.
- A documented, reversible way for the community to experiment without
  rooting or changing firmware.

## What we do NOT claim

- that it works on the Toshiba 50UV1553DB or any specific set,
- that it can change settings by itself,
- that it exposes any management beyond remote control,
- or that Wake-on-LAN works on these models.

## Before the first local-control session (preparation checklist)

1. A Home Assistant installation (or another MQTT client) on the same network
   as the TV, with the ha_vidaatv integration downloaded but not yet paired.
2. Physical access to the TV: pairing shows a PIN on the TV screen that must
   be typed into the client. There is no headless pairing.
3. A filled copy of the [session log template](https://github.com/HALCONDEORO/vidaa-clean-tv/blob/main/docs/templates/session-log.md) with
   `session_type: local-control`, so every probe lands as a structured row.
4. The TV's current settings photographed or noted, so anything that changes
   can be reverted.

## Probes for the first session, in order of increasing commitment

| # | Probe | Expected | Passes only if observed |
|---|---|---|---|
| 1 | SSDP discovery finds the TV | The TV appears as a discovered device | Discovery lists the exact model |
| 2 | PIN pairing | A PIN appears on screen and the client accepts it | Pairing completes and survives one TV power cycle |
| 3 | Read state | Power state and current source are visible | Values match what the TV actually shows |
| 4 | One harmless key press | e.g. Volume Up changes the volume overlay | The overlay reacts, once |
| 5 | Source or app switch | Switch to a known input and back | The TV switches and returns |
| 6 | Unpair / revoke | Removing the client revokes access | The client can no longer send keys |

Stop at the first failing probe and log it; a failed probe is a useful row,
not a disaster. Do not script setting changes until probes 1-4 have passed on
the same model and firmware.

## Risks and limits to record

- Any device on the local network that completes PIN pairing can send remote
  keys until unpaired. Note who paired and when, and unpair when done.
- MQTT traffic is local by design, on a separate route from DNS. DNS
  filtering from [route 2](02-dns-filtering.md) is not expected to interact
  with it, but that interaction is untested on a real TV; record what you
  see in the session log.
- Firmware updates can change or remove the interface; the session log must
  record the firmware version every time.

This page turns into a verified guide only when the rows above exist in
[TESTING.md](../TESTING.md) for a named model. Until then it is preparation,
not a feature.
