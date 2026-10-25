# Troubleshooting

## A menu option from docs/01 does not exist on my TV

Menu names vary between VIDAA versions and brands. Open the privacy section
and read down it: you are looking for anything about viewing information,
usage data, content recognition or advertising. Note the real names you find
(docs/05 tells you what to record) so the docs can be corrected.

## Settings came back after an update

Known VIDAA behavior: some updates reset privacy options or re-ask for
consent in a way that re-enables them if you accept quickly. Re-check the
privacy section after every update. Thirty seconds.

## An app stopped loading after enabling the blocklist

A domain the app needs is probably blocked. Open the query log (route 3),
reproduce the problem, look at what was just blocked, remove the last group
you added and re-add rules one at a time. If a rule in the upstream list is
the cause, report it there.

## Icons or artwork load slowly, or appear as empty placeholders

Known side effect reported by the upstream blocklist author: the launcher
waits for a blocked resource and then falls back to a cache. It usually
settles in a few seconds. If it does not, disable the functional group that
causes it.

## The TV sends queued telemetry when I unblock

Expected. A TV may retain events locally while DNS fails and send them when
it can resolve again. Firmware-dependent and not publicly documented.

## fetch_query_log.py: "Cannot reach ..."

Run it on the same network as AdGuard Home, and check that the web UI opens
at the same host and port you passed with `--host`.

## fetch_query_log.py: "Redirect ... refused"

Give the exact address AdGuard Home listens on (right port, http vs https).
The script refuses redirects on purpose so your admin credentials cannot be
forwarded somewhere else.

## fetch_query_log.py: HTTP 401 or 403

Wrong admin username or password. The password only ever comes from the
hidden prompt or `ADGUARD_PASSWORD` for that one command - never from the
command line.

## The query log shows no traffic from the TV

The TV is not using the filter. Set the TV's DNS manually to the filter
address, or check your per-client rules in AdGuard Home / Pi-hole.
