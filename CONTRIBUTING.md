# Contributing

Thanks for helping make VIDAA TVs less noisy. This project grows the same way
it started: small, honest, and verified piece by piece.

## The one rule that matters

A claim about a specific TV counts as verified only when it has a row in
[TESTING.md](TESTING.md): date, firmware version, step, expected result,
observed result, and whether it was reverted. Everything else must be labeled
with its source ("documented setting", "reported by the upstream blocklist
author", "hypothesis"). If you cannot point to a source or a log row, say so
in the text instead of smoothing it over.

## Reporting a new model

The most valuable contribution right now is a first-session report from a
VIDAA model we do not cover yet. Open an issue with the "New VIDAA model
report" template and include:

- Brand, model and region (menu wording varies by region).
- Firmware version (Settings > Support > System info, or similar).
- The exact menu names you saw, word for word - not what the docs expected.
- What each step changed, and anything you had to revert.

A new page under `docs/tv/` is welcome once that information exists. Follow
the structure of [docs/tv/toshiba-50uv1553db.md](docs/tv/toshiba-50uv1553db.md):
what is verified on this set, what is sourced but unverified, and what is
unknown.

## Scripts

- Standard library only, no dependencies. The test suite must run fully
  offline: `python3 scripts/test_classify_dns_log.py -v`.
- Keep `validate_blocklist.py` passing on any blocklist change.
- Never copy an upstream blocklist into this repo. We subscribe to
  [ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist](https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist)
  and keep only a small supplement for domains observed on other VIDAA brands.

## Documentation style

- English, plain sentences, no marketing tone.
- Distinguish "verified on device X" from "documented by source Y" from
  "hypothesis". Do not upgrade a claim's strength without the evidence.
- No absolutes about effects we have not measured ("the TV stops reporting",
  "zero risk"). Describe the setting and its documented scope instead.
- Internal links must resolve; CI checks them with
  `python3 scripts/test_docs_links.py -v`.

## Out of scope

Firmware modification, service menus, rooting, ADB (VIDAA has none), invented
APIs, and anything that touches another person's network or device. Pull
requests in those directions will be closed.

## License

Contributions are licensed under the project's MIT license. Third-party
projects referenced here keep their own licenses (see NOTICE.md).
