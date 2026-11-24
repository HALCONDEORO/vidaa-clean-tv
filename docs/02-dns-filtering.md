# Route 2: DNS filtering

**What it is:** a DNS filter can block matching domain lookups that reach it.
That is not a view of every TV connection: cached answers, other resolvers or
encrypted DNS can leave traffic outside its query log. The TV software is not
modified. Revert by restoring your recorded DNS settings and removing the list.

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

Point only the TV at a dedicated resolver when possible, or use a filtering
system whose client/group isolation you have verified. Setting manual DNS on
the TV does not isolate a newly enabled list on an AdGuard Home instance that
other devices already use. Record the previous DNS and list settings first.

## The blocklist

Subscribe, do not copy:

```text
https://raw.githubusercontent.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist/main/Blocked_Domains_AdGuard.txt
```

AdGuard Home: **Filters → DNS blocklists → Add blocklist → Add a custom list**,
paste the URL, save, then **Update filters**.

Pi-hole: **Lists** (v6; **Group Management → Adlists** on v5) → paste the
same URL in the address field, save, then update gravity
(**Tools → Update Gravity** or `pihole -g`). Pi-hole parses the AdGuard
syntax of that list directly; use `Blocked_Domains.txt` from the same repo
if your filter wants plain hostnames.

### Limit the filter to the TV only

AdGuard Home: do not assume **Client settings** offers a per-client blocklist
selector. As checked 24 November 2026, the upstream
[per-client list assignment proposal](https://github.com/AdguardTeam/AdGuardHome/issues/8274)
is still open. The official
[client guide](https://adguard-dns.io/kb/adguard-home/clients/) documents custom
rules using `client`/`ctag`, not assigning a downloaded subscription to one TV.
MAC identification also requires AdGuard Home to be the network's DHCP server.

For a first reversible trial, use a separate AdGuard Home instance used only
by the TV, and change only the TV's DNS settings. If that is not available,
stop before enabling this subscription on a shared resolver. A client entry
alone does not make the subscription TV-only. Custom scoped rules are an
advanced alternative, not a way to scope an unmodified downloaded list; this
project's offline validator deliberately rejects rule options. Do not strip
options or disable every other client's protection as a workaround.

Pi-hole: **Group Management** (v5; **Clients/Groups** on v6) → create a
group (for example `tv`), add the TV as a client by IP or MAC, then assign
the VIDAA list to that group only. Every other device keeps your previous
setup unchanged, and removing the TV from the group reverts it instantly.

The author's observations come from Hisense VIDAA sets in Europe/Germany;
individual rule comments distinguish observed hosts from inferred candidates.
The author reports YouTube and Netflix working, not every app or every model.
Effects on Toshiba remain untested here (see [TESTING.md](../TESTING.md)).

### Upstream snapshot: 11 November 2026

[IPanalytics' update `045c377`](https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist/commit/045c377)
adds 13 active rules and two documented-but-disabled options: **150 active,
45 disabled, 195 total** at that commit, checked 14 November. These are
upstream counts, not a hardware-verification result or a fixed promise about
future subscriptions. Refreshing the subscription brings future changes too.

The new active rules cover advertising/monetization reporting and resources,
regional monetization backends, an advertising-portal CDN, Hisense/Xumo
beacons and telemetry/tracking hosts. These additions overlap the reporting
and monetization coverage that our 9 November community comparison described
as missing. Do not add a second list just to fill that old gap.

The same update explicitly documents the **Prime Video trade-off**: six
recommendation API/UI rules remain active because upstream prioritizes the
clean home screen, but owners reported missing Prime Video thumbnails and
parts of its UI. That setup does not use Prime Video. See the six named hosts
and smallest-change recovery procedure in
[TROUBLESHOOTING.md](../TROUBLESHOOTING.md#an-app-stopped-loading-after-enabling-the-blocklist).
The upstream author credits the
[Owen3H fork](https://github.com/Owen3H/Hisense-VIDAA-DNS-Clean-TV-Blocklist)
that disables those rules; this is a reported workaround, not a test here.

Two additional options stay disabled upstream: `recommend-ui.vidaahub.com`
can affect launcher tiles and artwork; `api-4know-eu.hismarttv.com` can affect
search suggestions and voice answers. They are not default blocks, and this
project does not recommend enabling them without observations on your set.
No rules are copied into our supplement and no TV results are added by this
documentation update.

## Other community lists

The upstream list above is the one this project documents and tests against.
Others exist; know their trade-offs before mixing:

- [Okazakee/tv-dns-blocklist](https://github.com/Okazakee/tv-dns-blocklist) -
  multi-brand, with a "non-breaking" curation policy claimed by its author.
  Its README distinguishes device tests on Sony/LG from resolution-level
  checks on other platforms, so that label is not VIDAA hardware validation.
  It also uses `$important` exceptions that can override other AdGuard
  subscriptions, and offers separate Pi-hole files. The 11 November
  IPanalytics update closes part of the earlier coverage gap; compare current
  rules and exception semantics rather than choosing by rule count. Use one
  TV list at a time and observe its effects before mixing lists.
- Lists recommended in forum threads come and go:
  `jnmobilesoft/hisense-u8n-pihole-blocklist`, widely linked on Reddit in
  2025, already returns 404. This is the practical
  reason for "subscribe, do not copy": a copied snapshot never gets fixes,
  and a dead subscription fails loudly instead of silently protecting you.
- [Perflyst/PiHoleBlocklist](https://github.com/Perflyst/PiHoleBlocklist) -
  the long-running smart-TV list for other brands; its issues are a good
  preview of the breakage patterns to expect.

## The supplement

[blocklists/toshiba-uv1553db-supplement.txt](https://github.com/HALCONDEORO/vidaa-clean-tv/blob/main/blocklists/toshiba-uv1553db-supplement.txt)
holds domains observed on our Toshiba that the upstream list misses. It starts
empty on purpose: rules are added only from real DNS observations on the
device, never guessed.

Before you subscribe the TV to any list of your own, check the file offline:

```
python3 scripts/validate_blocklist.py your-list.txt
```

It rejects malformed rules (including scoped Adblock options like
`$client=`, which this project does not interpret), duplicates and rules
shadowed by a parent-domain rule, and `--upstream` checks your list adds
nothing the upstream list already covers. This validates syntax only;
whether the rules block the right domains comes from observing your own TV,
never from the validator.

## Honest warnings

From the upstream author and justatv.eu:

- Blocking blind breaks things. The same domains can serve artwork, search or
  updates. If an app stops loading, check the query log first.
- The TV may queue telemetry while blocked and send it later if you unblock.
- If anything you need breaks: remove the list and refresh the filters.
  Nothing on the TV was modified.
