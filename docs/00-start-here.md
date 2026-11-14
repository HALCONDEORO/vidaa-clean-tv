# Start here: from "I have a VIDAA TV" to a first real action

English | [Español](00-start-here.es.md)

This page turns the rest of the documentation into a decision. Ten minutes
of reading, then one concrete action you can reverse. Nothing here requires
root, ADB, a firmware change or a purchase.

## Step 1 - Identify the exact set (5 minutes, on the TV)

Open the TV's normal information menu and write down three things:

- **Model** - the full string, not just "Hisense" or "Toshiba".
- **Region** - the country the TV is configured for.
- **Firmware** - the complete build string.

Menu names vary between models; do not enter a service menu. A brand badge
does not tell you the operating system: some VIDAA-branded sets run Android
underneath, and the cleanup route for those is different from the one this
project documents. If you are not sure what you have, read
[Check compatibility by feature, not brand](07-compatibility.md) before
touching anything.

## Step 2 - Choose your routes

Each route is independent. Start with route 1; add the others when you are
ready. "Reversible" means you can put the setting back from the same menu.

| Route | What it does | What you need | Time |
|---|---|---|---|
| [1 - On-device settings](01-on-device-settings.md) | Turns off content recognition, ad personalization and unwanted data-sharing consents | Just the TV remote | ~5 minutes, reversible |
| [2 - DNS filtering](02-dns-filtering.md) | Stops ad and telemetry domains from resolving | An always-on computer, a Raspberry Pi, or router access | ~30 minutes |
| [3 - Observe DNS first](03-observing-dns.md) | Shows what your TV actually talks to, so your rules come from evidence | The same setup as route 2 | One evening of watching |
| [4 - Local control over MQTT](04-local-control-mqtt.md) | Preparatory notes for local remote control | Nothing yet - **untested on the sets covered here** | Read only |

Route 4 is preparation, not a feature: no model covered by this project has
a verified MQTT session yet, and the page says so at the top.

## Step 3 - Do one route and log it

Pick the route you chose and follow its page. While you work, keep a copy
of the [session log template](https://github.com/HALCONDEORO/vidaa-clean-tv/blob/main/docs/templates/session-log.md)
open and fill it in honestly: what you expected, what you saw, what you put
back. [The first hardware session protocol](05-first-hardware-session.md)
explains why the log matters more than the outcome: your menus and firmware
are the evidence other owners of your model need.

The filled log converts to [TESTING.md](../TESTING.md) rows (run the
converter without `--json` for those) and to a shareable report with two
offline commands:

```
python3 scripts/session_to_testing.py your-log.md --json > your-report.json
python3 scripts/validate_model_report.py your-report.json
```

The validator rejects common identifier patterns (IP and MAC addresses,
emails, local hostnames, exact times, long hex tokens) in the JSON report
it inspects. That is a pattern check, not anonymization: it does not cover
every kind of personal data, and it never looks at the prose around the
JSON block. Review all text and photos yourself before sharing anything.

## Step 4 - Check your own rules before relying on them

If you maintain your own blocklist or a supplement file, validate it before
subscribing the TV to it:

```
python3 scripts/validate_blocklist.py your-list.txt
```

It rejects malformed rules, duplicates and rules shadowed by a parent
domain, and with `--upstream` it checks you are not duplicating the
[list this project subscribes to](02-dns-filtering.md). Validation checks
syntax, never whether the list blocks what you want - that only comes from
observing your own TV (route 3).

## What this site will never ask of you

- No account and no sign-in. We add no analytics or tracking scripts; the
  site is static documentation hosted by GitHub Pages.
- No service menu, root, ADB or firmware change.
- No purchase or subscription. The tools are offline Python scripts.
- No blind trust: every page states what is verified, by whom, on which
  model, and what remains unknown. If a page does not say it, it is not
  verified.

Spanish entry points: [start here](00-start-here.es.md),
[README en español](../README.es.md) and [preguntas frecuentes](../FAQ.es.md).
Settings, the first session and feature compatibility also have Spanish guides;
other technical guides and reports remain in English.
