# Try the DNS tools offline

These examples are invented test data, not a real TV capture or a recommended
blocklist. The example addresses and domains do not identify any actual TV
or service. Run commands from the repository root with Python 3.10 or later.
No dependencies, credentials, TV, router or network requests are needed.

## Count queries from one synthetic client

```sh
python3 scripts/classify_dns_log.py examples/synthetic-dns.json --client 192.0.2.50 --blocklist examples/synthetic-blocklist.txt
```

Expected output (columns are tab-separated):

```text
domain	queries	already_blocked	seen_filtered
ads.example.com	2	yes	yes
video.example.net	1	no	no
```

## Inspect activity over time

```sh
python3 scripts/classify_dns_log.py examples/synthetic-dns.json --client 192.0.2.50 --timeline 60
```

```text
Timeline: 60-minute buckets (times in UTC)
bucket_start	total	filtered	unblocked
2026-10-01T09:00Z	2	2	0
2026-10-01T10:00Z	1	0	1
```

Counts describe DNS queries, not data content or proof that telemetry stopped.

## Preview candidate rules, without installing them

```sh
python3 scripts/classify_dns_log.py examples/synthetic-dns.json --client 192.0.2.50 --blocklist examples/synthetic-blocklist.txt --rules
```

```text
||video.example.net^
```

An unblocked domain is not automatically advertising or telemetry. This
candidate is intentionally fictional: do not install it or treat any
candidate output as a safe blocklist. Real rules need observations,
functional tests and rollback notes from your own device.

For your own capture, see [route 3](03-observing-dns.md). Keep private logs
local. For physical testing, follow the [first-session protocol](05-first-hardware-session.md).
