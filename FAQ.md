# Frequently asked questions

The questions people actually ask before buying, on day one, and when
something breaks. Answers follow the project rule: verified claims say where
they were verified, everything else is labeled as reported.

## Does a VIDAA TV show ads?

Yes, on most current firmware: recommendation and promo tiles on the home
screen, an auto-playing preview strip (with audio on some models), and
"VIDAA Free" channels. Since 2025 owners also report full-screen video ads
at startup or when switching inputs, which Hisense support describes as a
feature. What you see depends on the model, region and firmware.

## Can the ads be turned off?

There is no single switch. What works today, in increasing effort:

- **Route 1** ([docs/01-on-device-settings.md](docs/01-on-device-settings.md)):
  reversible settings that reduce personalization, promotions and telemetry.
- **Route 2** ([docs/02-dns-filtering.md](docs/02-dns-filtering.md)): DNS
  filtering with a community blocklist. Owners report a cleaner home screen
  with YouTube and Netflix still working, including one logged session on a
  Hisense 65A67H (see [TESTING.md](TESTING.md)). Blocking blind can break
  things; the docs cover the honest cases.
- Startup full-screen ads are the newest form. The evidence-first workflow
  in [docs/03-observing-dns.md](docs/03-observing-dns.md) is how to find out
  which domains serve them on your own TV before blocking anything.

## Does VIDAA require an account?

The TV works without a VIDAA account for the basics (live TV, HDMI inputs,
installed apps). Some cloud features and the VIDAA app store ask for one.
This project's routes 1 and 2 do not need an account.

## What data does the TV collect?

VIDAA's privacy policy (linked in [README.md](README.md)) describes usage
and device data collection, and the settings in route 1 include the consent
and personalization toggles documented from the manual. For what your own TV
actually sends, observe it: route 3 exists exactly so you do not have to
take anyone's word for it, including ours.

## Can I root it, install a launcher, or use ADB?

No. VIDAA has no ADB, no sideloading and no package management. That is why
this project works only with reversible settings and network-level
filtering, and why everything here can be undone.

## Will blocking break YouTube, Netflix or Prime Video?

YouTube and Netflix are reported working with the upstream blocklist, by its
author and in the logged 65A67H session. Prime Video has one reported
casualty: the upstream `recommendation-*` rules cost it thumbnails and parts
of the UI. If any app misbehaves, follow
[TROUBLESHOOTING.md](TROUBLESHOOTING.md) - there is a step-by-step playbook
for unblocking exactly one domain instead of dropping the whole list.

## Which TVs does this cover?

VIDAA-based sets: Hisense (the best documented, including one logged
session) and Toshiba VIDAA models (the project's original target, documented
and awaiting the first logged session). See
[docs/tv/README.md](docs/tv/README.md) for the per-model status table.

## Can I just use a Pi-hole or AdGuard Home list without the rest?

Yes. [docs/02-dns-filtering.md](docs/02-dns-filtering.md) is the short path:
subscribe one URL, scope it to the TV, done. The rest of the project
(observing, your own supplement rules, the session log) is for when you want
proof instead of hope.
