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

## Requests increase after I unblock

A possible explanation is that a TV retains events locally while DNS fails
and sends them when it can resolve again. This is a hypothesis, not a verified
behavior of the target TV; firmware behavior is unknown. A burst of requests
alone does not establish what data was sent.

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

## AdGuard Home: port 53 is already in use

Another program holds the DNS port. Find it on the AdGuard Home device:

```sh
sudo ss -tulpn | grep ':53 '
```

If it is `systemd-resolved` (common on Ubuntu and Debian), turn off its stub
listener and point `/etc/resolv.conf` at the full resolver file:

```sh
sudo mkdir -p /etc/systemd/resolved.conf.d
printf '[Resolve]\nDNS=127.0.0.1\nDNSStubListener=no\n' | sudo tee /etc/systemd/resolved.conf.d/adguardhome.conf
sudo mv /etc/resolv.conf /etc/resolv.conf.backup
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
sudo systemctl reload-or-restart systemd-resolved
```

Run the `ss` check again; it should print nothing. Then start AdGuard Home.
The device itself cannot resolve names until AdGuard Home is running, because
it now asks `127.0.0.1`. To undo, delete the `.conf` file, restore
`/etc/resolv.conf.backup` and restart `systemd-resolved`.

Other common holders: `dnsmasq` (check it is not serving DHCP before
stopping it), `pihole-FTL` (run one DNS filter, not two), `docker-proxy`
(another container maps port 53; see `docker ps`) and `named`/`bind9`.

## AdGuard Home works on its own device but other devices time out

`nslookup example.com <adguard-ip>` from another device times out while
`nslookup example.com 127.0.0.1` on the AdGuard Home device answers. Check
which address it listens on:

```sh
sudo ss -tulpn | grep ':53 '
```

If it shows only `127.0.0.1:53`, AdGuard Home accepts queries from itself
only. Stop it, then in `AdGuardHome.yaml` (`/opt/AdGuardHome/` for a native
install, the mounted `conf` directory for Docker) set:

```yaml
dns:
  bind_hosts:
    - 0.0.0.0
```

Keep the indentation as spaces, start AdGuard Home again and re-run the check:
it should show `0.0.0.0:53` or `*:53`. Stopping first matters, because a
running instance can overwrite the file.

If it already listens on `0.0.0.0` and other devices still time out, look
for a firewall on the device (`sudo ufw status`, `sudo firewall-cmd --state`),
a laptop on a guest network or VPN, or Wi-Fi client isolation on the router.

## The query log shows no traffic from the TV

The TV is not using the filter. First confirm another device on the same
network gets answers from AdGuard Home (see the previous section). Then:

- Check the DNS address on the TV's network information screen. On some sets
  DNS can only be changed after switching the whole IP setting to manual;
  copy the IP address, subnet mask and gateway it showed before.
- Power-cycle the TV at the wall for 30 seconds. Standby can keep the old
  DNS settings.
- With AdGuard Home in Docker on a bridge network, queries can appear under
  a `172.17.x.x` address instead of the TV's. Clear the log filter, or run
  the container with `--network host`.
- If the router announces an IPv6 DNS server, the TV may use that instead.
  Point it at AdGuard Home or stop announcing it.
- Or check your per-client rules in AdGuard Home / Pi-hole.

In the 2026-11-08 session in [TESTING.md](TESTING.md), the TV appeared in the
log after the listen-address fix above (a TV power cycle was suggested at
that point; whether it was done was not recorded).
