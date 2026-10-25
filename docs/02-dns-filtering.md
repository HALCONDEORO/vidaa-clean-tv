# Route 2: DNS filtering

**What it is:** the TV asks a DNS resolver for the address of every domain it
wants to reach. A filtering resolver answers "does not exist" for ad and
telemetry domains. The TV itself is not modified at all. Revert by removing
the filter.

**What it is not:** a TV setting. It is network administration, and depending
on how you set it up it can affect every device on the network. Do not start
this on a shared network without the agreement of everyone affected.

## Setup options

- **A. AdGuard Home on an always-on device** (Raspberry Pi or similar).
  Recommended: per-client rules, a query log (needed for route 3), easy
  rollback.
- **B. Pi-hole.** Same idea.
- **C. Router-level DNS filtering.** Only if the router supports per-device
  filtering rules.

Point only the TV at the filter when possible (manual DNS on the TV, or
per-client rules in AdGuard Home / Pi-hole), so nothing else in the house is
affected.

## The blocklist

Subscribe, do not copy:

```text
https://raw.githubusercontent.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist/main/Blocked_Domains_AdGuard.txt
```

AdGuard Home: **Filters → DNS blocklists → Add blocklist → Add a custom list**,
paste the URL, save, then **Update filters**. Pi-hole accepts the same URL; use
`Blocked_Domains.txt` from the same repo if your filter wants plain hostnames.

137 active rules, observed on real Hisense VIDAA sets in Europe; the author
reports YouTube and Netflix keep working. Built for Hisense, so treat its
effect on a Toshiba as probable but unproven until tested (see TESTING.md).

## The supplement

[blocklists/toshiba-uv1553db-supplement.txt](../blocklists/toshiba-uv1553db-supplement.txt)
holds domains observed on our Toshiba that the upstream list misses. It starts
empty on purpose: rules are added only from real DNS observations on the
device, never guessed.

## Honest warnings

From the upstream author and justatv.eu:

- Blocking blind breaks things. The same domains can serve artwork, search or
  updates. If an app stops loading, check the query log first.
- The TV may queue telemetry while blocked and send it later if you unblock.
- If anything you need breaks: remove the list and refresh the filters.
  Nothing on the TV was modified.
