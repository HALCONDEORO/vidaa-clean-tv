<p align="center">
  <img src="assets/hero.png" alt="Illustration: a smart TV with a tidy home screen and a broom-and-sparkles motif" width="100%">
</p>

# VIDAA Clean TV

Reversible cleanup for smart TVs running VIDAA (Hisense, Toshiba and other VIDAA brands): fewer ads and recommendation tiles on the home screen, less telemetry, and content recognition (ACR) turned off. No rooting, no firmware changes, nothing that touches the system.

## Why a separate project

Clean Your TV and similar tools disable packages over ADB. VIDAA has no ADB, no sideloading and no reachable package list, so that approach cannot be ported: [Clean Your TV's Hisense compatibility page](https://cleanyourtv.wiki/tv/hisense/) lists sets running VIDAA OS as not covered because the tool needs Android, and the [justatv.eu VIDAA guide](https://justatv.eu/en/guides/cleaning-up-a-hisense-television-with-vidaa) reaches the same conclusion - with no ADB on VIDAA, cleanup means settings and network filtering, not package tools. A port would not be an adaptation, it would be a different tool. This is that tool.

## The three routes that work

1. **On-device settings** (about 5 minutes with the remote, fully reversible) - [docs/01-on-device-settings.md](docs/01-on-device-settings.md)
2. **DNS filtering on your network** - [docs/02-dns-filtering.md](docs/02-dns-filtering.md)
3. **Observing what your TV actually talks to**, so block rules come from evidence, not guesses - [docs/03-observing-dns.md](docs/03-observing-dns.md) and [scripts/classify_dns_log.py](scripts/classify_dns_log.py)

## What this project does NOT do

- No ADB, no APK sideloading, no launcher replacement, no package disabling. VIDAA does not offer any of these.
- No firmware modification, no factory or service menus, no rooting. Those risk bricking the set and voiding the warranty.
- No invented APIs. Every step is either a documented on-device setting or standard network administration.

## Existing work this builds on

- [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv) (MIT) - ADB-based cleanup for Android TV / Google TV. Not compatible with VIDAA. Inspiration for the goal; none of the code.
- [ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist](https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist) (Apache-2.0) - the blocklist this project subscribes to: 137 active rules observed on real Hisense VIDAA sets in Europe. We do not copy the list; we point at it and keep a small supplement for domains observed on other VIDAA brands.
- [warrenrees/ha_vidaatv](https://github.com/warrenrees/ha_vidaatv) (MIT) - Home Assistant integration that talks to VIDAA TVs over MQTT with on-screen PIN pairing, and lists some Toshiba VIDAA sets as supported. See [docs/04-local-control-mqtt.md](docs/04-local-control-mqtt.md).
- [justatv.eu VIDAA cleanup guide](https://justatv.eu/en/guides/cleaning-up-a-hisense-television-with-vidaa) and the [official VIDAA OS privacy policy](https://www.vidaa.com/os-privacy-policy/) - sources for the settings paths in docs/01.

## Development

`python3 scripts/test_classify_dns_log.py -v` runs the offline test suite (11 tests, stdlib only). CI runs it on every push and pull request across Python 3.10-3.13.

## Hardware verification status

Nothing here is claimed as tested on a specific model until it appears in [TESTING.md](TESTING.md) with a date and a firmware version. The current target device is a Toshiba 50UV1553DB (VIDAA, Europe). Until that first session is logged, treat every menu name as "wording varies - read the privacy section".

## License

MIT for original content (see LICENSE). Third-party projects keep their own licenses (see NOTICE.md).
