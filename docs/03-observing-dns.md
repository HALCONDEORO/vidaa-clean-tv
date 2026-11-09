# Route 3: observe what your TV talks to

Goal: replace guesses with observations. Record everything the TV resolves,
then classify it.

1. Set up AdGuard Home (route 2, option A) or Pi-hole (option B) and point
   only the TV at it.
2. Use the TV normally for a day or two: home screen, YouTube, Netflix,
   settings.
3. Get the query log. AdGuard Home: export from the web UI, or use
   `scripts/fetch_query_log.py`, which pulls it from the `/control/querylog`
   API of your own AdGuard Home. Pi-hole: copy `/etc/pihole/pihole-FTL.db`
   to your working directory (copy, never move: Pi-hole keeps writing to the
   original) and classify the copy; the classifier opens it read-only.

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

### Catching startup and input-switch ads

Owners also report full-screen ads at power-on or when switching inputs.
To find the domains behind them instead of guessing: note the exact time,
cold-boot the TV or switch inputs once, then export the query log and
search the raw entries in the seconds around that moment. `--timeline 1`
narrows the search to the one-minute bucket that spikes, but buckets only
carry counts - the domains come from the log itself. Cross-check each
candidate against the classified table: a domain that appears only in the
seconds around the ad is a candidate; one that also serves artwork or
search shows up in normal browsing too, which is how you avoid breaking
the home screen.

```sh
python3 scripts/fetch_query_log.py --host http://192.168.1.10:3000 \
    --user admin --pages 10 -o querylog.json
python3 scripts/classify_dns_log.py querylog.json \
    --client 192.168.1.50 \
    --blocklist Blocked_Domains.txt \
    --min-count 3 --rules

# Pi-hole: same command on a copy of the FTL database
python3 scripts/classify_dns_log.py pihole-FTL.db \
    --client 192.168.1.50 \
    --blocklist Blocked_Domains.txt \
    --min-count 3 --rules
```

To see *when* the TV is most active, run a separate command with `--timeline` (bucket size in minutes,
default 60). It prints per-bucket counts split into filtered and unblocked:

```sh
python3 scripts/classify_dns_log.py querylog.json --client 192.168.1.50 --timeline
```

Timestamps exist in AdGuard Home JSON exports and in Pi-hole FTL
databases; dnsmasq logs and plain domain lists cannot produce a timeline. A timeline shows request volume over
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
log. Identifiers have a literal `client:` prefix and a JSON-quoted value so
unusual characters cannot break the table or become spreadsheet formulas;
for normal IP addresses, copy the address inside the quotes to `--client`
(not the quotes themselves). A label with escaped control characters is not
a normal IP address; inspect your export before using it as a filter.
`<unknown>` means the input had no client identifier; plain domain files cannot
identify a TV. Check the TV's network settings or your router to choose the
right client. This command cannot prove which physical device owns an address.
Counts include only supported, valid query records, not malformed entries.
Keep the inventory private just like the log. `--clients` is a separate mode,
not combined with client filters, blocklist comparisons, rules or timelines.

### Choose one output mode

| Output | Options you can combine |
| --- | --- |
| Domain table (default) | `--client`, `--blocklist`, `--min-count N` |
| Candidate rules (`--rules`) | `--client`, `--blocklist`, `--min-count N` |
| Timeline (`--timeline [MINUTES]`) | `--client` only |
| Client inventory (`--clients`) | No other filtering or output options |

`--min-count` is a domain-query threshold, not a timeline-bucket or client
threshold. It must be at least 1; its default is 1 for tables and rules.
Timeline minutes must also be at least 1. Conflicting options are rejected
before the log or comparison list is read, with an error on stderr and exit
code 2. No partial table or rules are printed. Run separate commands when you
need both rules and a timeline; options are never silently ignored.
