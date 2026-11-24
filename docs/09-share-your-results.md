# Share your results: the session pack

You ran [docs/03-observing-dns.md](03-observing-dns.md) and have a local DNS
query log. This page shows how to turn one or two logs into a single HTML
file you can post in a forum, attach to an issue or send to a friend, without
publishing your household's browsing.

The session pack is built **offline** by `scripts/build_session_pack.py`
(Python 3.10+, no dependencies, no network requests). The logs never leave
your machine.

## What the report contains - and what it never contains

Privacy is the default, not a setting; there is no flag to relax it:

- **No domain is named** unless you list it yourself, one deliberate choice
  per domain, with `--name-domain`. Matching a blocklist is never enough:
  a list you supply can contain anything, so a match is not evidence that a
  domain is public or non-personal.
- **Counted, never named:** everything else appears only as an aggregate
  ("N other unique domains, M queries"), including blocklist matches.
- **Never in the report:** client addresses, timestamps, DNS answers and
  file names.

Aggregate counts still describe your overall usage volume. Share the report
only where that is acceptable, and review the HTML before posting it.

## Build one

```sh
python3 scripts/build_session_pack.py queries.json \
    --blocklist Blocked_Domains_AdGuard.txt \
    -o session-pack.html
```

- `queries.json` is any log the classifier reads: an AdGuard Home JSON
  export, a native JSONL copy (`--format adguard-jsonl`), a Pi-hole FTL
  database copy, or dnsmasq/plain text. See
  [docs/06-offline-example.md](06-offline-example.md) for a synthetic input
  you can try without a TV.
- `--blocklist` (repeatable) only feeds the aggregate "blocklist matches"
  count, so you can report how much of the traffic those lists cover.
- `--name-domain ads.example.com` (repeatable) is the only way any domain
  appears by name. Use it for public advertising/telemetry hostnames you
  want to discuss; it is your disclosure decision, per domain.
- Add `--before older-log.json` for a before/after comparison, for example
  around enabling DNS filtering. The two logs are not a controlled
  experiment: differences can come from what was watched, resolver caching
  or the time of day. The comparison does not measure the effect of the TV,
  the filter or any settings change, and the report says so.
- The command refuses to overwrite any input (both logs and every
  blocklist), and writes the report atomically.

## Share it

Post the HTML (or a screenshot of it) wherever you discuss the project, or
attach it when you open a tracking issue as
[docs/05-first-hardware-session.md](05-first-hardware-session.md) describes.
Aggregate match counts tell other VIDAA owners how much a list covers; named
domains are talking points you chose, on evidence from your own log.

If someone asks for the underlying log, prefer the pseudonymized export from
`scripts/redact_dns_log.py` over the raw file, and read its warnings first.
Neither output is anonymous data or hardware evidence; both are aids for
discussion.

## Limits

- Conclusions cover only queries visible in the logs; a TV that was off, or
  a resolver that cached a name, leaves no trace.
- A blocklist-match count says something about the lists, not proof that any
  domain served ads on your TV.
- Do not present the pack as a settings-session result: it observes DNS only.
