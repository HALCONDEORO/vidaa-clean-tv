# Route 3: observe what your TV talks to

Goal: replace guesses with observations. Record everything the TV resolves,
then classify it.

1. Set up AdGuard Home (route 2, option A) and point only the TV at it.
2. Use the TV normally for a day or two: home screen, YouTube, Netflix,
   settings.
3. Export the query log: from the AdGuard Home web UI, or with
   `scripts/fetch_query_log.py`, which pulls it from the `/control/querylog`
   API of your own AdGuard Home.

   Credential and data hygiene:

   - Never put the password on the command line (it lands in your shell
     history), in a chat, or in any file you might commit. The script asks
     for it without echo, or reads `ADGUARD_PASSWORD` from the environment
     of that one command.
   - Run it only against your own AdGuard Home on your own network. The
     script refuses HTTP redirects so your credentials cannot be forwarded
     to a different address. Prefer HTTPS if your AdGuard Home has it.
   - The exported `querylog.json` is a record of what your TV looked up:
     treat it as private browsing data. Keep it local and never commit it
     (it is covered by `.gitignore` along with `.env`).
   One page holds 500 entries by default; a day or two of TV traffic is often more. `--pages N` keeps fetching older pages until the log runs out (max 100 pages). If the export stops on a full page, the script warns that older entries may remain; raise N until the warning disappears.

4. Run `scripts/classify_dns_log.py` on the export. It aggregates domains,
   marks which are already covered by the upstream blocklist, and prints
   candidate rules for the rest.
5. Add candidates one functional group at a time, test after each group, keep
   what breaks nothing. Log everything in TESTING.md.

Never add a domain you have not observed your own TV resolve.

```sh
python3 scripts/fetch_query_log.py --host http://192.168.1.10:3000 \
    --user admin --pages 10 -o querylog.json
python3 scripts/classify_dns_log.py querylog.json \
    --client 192.168.1.50 \
    --blocklist Blocked_Domains.txt \
    --min-count 3 --rules
```

To see *when* the TV is most active, add `--timeline` (bucket size in minutes,
default 60). It prints per-bucket counts split into filtered and unblocked:

```sh
python3 scripts/classify_dns_log.py querylog.json --client 192.168.1.50 --timeline
```

Timestamps exist only in AdGuard Home JSON exports; dnsmasq logs and plain
domain lists cannot produce a timeline. A timeline shows request volume over
time - for example whether queries spike right after you unblock a domain.
Volume says nothing about what data was sent, so use it to decide when to
look closer, not to draw conclusions about content.

### Supported comparison lists

The offline classifier compares plain hostnames and unconditional `||hostname^`
rules, including their subdomains. It is not an AdGuard filtering engine:
options (such as client conditions), exceptions, wildcards, hosts-file lines
and regex filters are rejected with a line number instead of being silently
misreported as coverage. Use a separate supported-syntax list for comparison;
do not strip conditions or exceptions from a real filter to make it pass.
The standalone validator supports some wildcard syntax that the classifier
does not evaluate. Passing validation does not guarantee classifier support.

### Find the client identifier first

Not sure which identifier to use with `--client`? List the clients present in
an export without making a network request:

```sh
python3 scripts/classify_dns_log.py querylog.json --clients
```

The table shows each identifier, query count and count marked filtered in the
log. Identifiers are JSON-quoted so unusual characters cannot break the table;
for normal IP addresses, copy the address inside the quotes to `--client`
(not the quotes themselves). A label with escaped control characters is not
a normal IP address; inspect your export before using it as a filter.
`<unknown>` means the input had no client identifier; plain domain files cannot
identify a TV. Check the TV's network settings or your router to choose the
right client. This command cannot prove which physical device owns an address.
Counts include only supported, valid query records, not malformed entries.
Keep the inventory private just like the log. `--clients` is a separate mode,
not combined with client filters, blocklist comparisons, rules or timelines.
