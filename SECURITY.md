# Security

This project is documentation plus small offline scripts, so the realistic
risks are credential leaks (your AdGuard Home password) and blocklist changes
that break apps on your TV.

## Reporting a problem

If you find a security issue in the scripts - for example a way credentials
could leak, or a redirect being followed - open a GitHub issue with
"[security]" in the title, or reach the maintainer through the repository
owner's GitHub profile. Never include passwords, tokens or your own query
logs in a report.

## What the scripts do with your data

- `fetch_query_log.py` talks only to the AdGuard Home address you give it,
  rejects base URLs containing credentials, queries or fragments before
  requesting a password, keeps network-error details out of diagnostics,
  refuses HTTP redirects (so credentials cannot be forwarded elsewhere), and
  writes the export atomically to a local file (owner-only mode 0600 on
  POSIX). A failed write leaves an existing export unchanged. An output
  symlink is replaced rather than followed; Windows access follows the
  destination directory ACLs, so use a private directory there. Run it only against your own server.
- `classify_dns_log.py` and `validate_blocklist.py` read local files and make
  no network requests at all.
- The exported `querylog.json` is a record of what your TV looked up: treat
  it as private browsing data, keep it local, and never commit it (it is
  covered by `.gitignore`).

Use HTTPS where available: Basic authentication over HTTP is not encrypted.
HTTP remains supported for trusted local installations. URL validation does
not prove ownership of a server; check the address before entering credentials.
