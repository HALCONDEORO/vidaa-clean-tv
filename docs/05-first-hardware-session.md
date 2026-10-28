# The first hardware session

Protocol for the first real cleanup session on the target TV (Toshiba
50UV1553DB, VIDAA). Until this is done and logged, nothing in this repo is
verified on that model. Do it with the remote, TV in front of you, about 15
minutes.

## Before

- Note the firmware version: **Settings → Support → About**, or
  **Settings → Support → System Info → Version** on older sets (paths from
  the official VIDAA manuals). Write it in the session log.
- Note exactly which privacy-related options exist and their exact wording.
  Menu names vary; the log needs the real ones, not the ones in docs/01.

## During (route 1 only: on-device settings, reversible)

1. Follow docs/01 one step at a time.
2. After each toggle, write down: what the option was called, what you set it
   to, and anything unexpected.
3. Take a photo of any screen whose wording differs from docs/01. Those
   photos are the evidence for correcting the docs.

## After

- Confirm the TV still behaves normally: home screen loads, one app opens
  (for example YouTube), one HDMI input works.
- Fill the session log in TESTING.md: date, firmware, every step, expected
  vs observed, reverted (yes/no).
- Only then do claims about this model stop being "unverified".

## Rollback

Every step in route 1 is a normal setting: switch it back the same way. If
something behaves oddly after a change, revert that one change first and
note it in the log.

## Not in this session

No DNS filtering, no router changes, no MQTT pairing experiments. Those are
separate decisions with their own session and their own log entries.
