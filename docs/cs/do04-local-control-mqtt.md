# Note: a legitimate local control interface exists

[warrenrees/ha_vidaatv](https://github.com/warrenrees/ha_vidaatv) (MIT) shows
that VIDAA TVs expose a local MQTT-based remote control interface with
on-screen PIN pairing, the same style of channel the official VIDAA mobile app
uses. Its README lists "Some Toshiba TVs with Vidaa OS" as supported.

What this could mean for this project: scripted remote key presses (for
example, navigating to a setting) and reading power/source state, from a
device on the same network.

What we do NOT claim:

- that it works on the Toshiba 50UV1553DB,
- that it can change settings by itself,
- or that it exposes any management beyond remote control.

Pairing requires physical access to the TV for the PIN. This is an exploration
note, not a feature of this project.
