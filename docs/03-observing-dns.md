# Route 3: observe what your TV talks to

Goal: replace guesses with observations. Record everything the TV resolves,
then classify it.

1. Set up AdGuard Home (route 2, option A) and point only the TV at it.
2. Use the TV normally for a day or two: home screen, YouTube, Netflix,
   settings.
3. Export the query log (AdGuard Home web UI or its `/control/querylog` API).
4. Run `scripts/classify_dns_log.py` on the export. It aggregates domains,
   marks which are already covered by the upstream blocklist, and prints
   candidate rules for the rest.
5. Add candidates one functional group at a time, test after each group, keep
   what breaks nothing. Log everything in TESTING.md.

Never add a domain you have not observed your own TV resolve.

```sh
python3 scripts/classify_dns_log.py querylog.json \
    --client 192.168.1.50 \
    --blocklist Blocked_Domains.txt \
    --min-count 3 --rules
```
