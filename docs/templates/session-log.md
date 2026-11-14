# Hardware session log (fill-in template)

Copy this file, fill it in during your session on the TV, then run
`python3 scripts/session_to_testing.py your-filled-copy.md` to get ready-made
rows for [TESTING.md](../../TESTING.md). The script only reads the JSON block
below; the prose around it is for you.

Rules that keep the log useful and safe to share:

- One session per file. Date only (`YYYY-MM-DD`), never exact times.
- No IP addresses, MAC addresses, email addresses, local hostnames or account
  identifiers anywhere in the file. The converter refuses files that contain
  them.
- Record `expected` before you look at the result, then `observed`. Honest
  surprises are the most valuable rows.
- Menu names exactly as the TV shows them, even where they differ from the
  docs - those differences are worth reporting.

```json
{
  "model": "",
  "region": "",
  "session_date": "YYYY-MM-DD",
  "firmware": "",
  "menus": [
    "Settings > ... > (the path exactly as shown on screen)"
  ],
  "session_type": "settings | dns-filtering | local-control | mixed",
  "steps": [
    {
      "step": "What you did (setting changed, filter subscribed, action tried)",
      "expected": "What you expected to happen",
      "observed": "What actually happened",
      "reverted": "yes | no"
    }
  ],
  "apps": [
    {
      "app": "YouTube",
      "status": "works | broken | untested",
      "notes": "Optional, e.g. ads gone, playback fine"
    }
  ],
  "outcome": "Free summary: what changed overall, anything you reverted, open questions"
}
```

Field reference:

- `model` (required): brand and model, e.g. `Toshiba 50UV1553DB`.
- `region` (required): country or region of the set, e.g. `Spain`. Menu wording
  and firmware vary by region.
- `session_date` (required): the day you ran the session, `YYYY-MM-DD`.
- `firmware` (required): as shown in Settings > Support > System info or the
  closest equivalent.
- `menus` (required): at least one menu path you actually opened, written as
  shown on screen.
- `session_type` (optional): `settings`, `dns-filtering`, `local-control` or
  `mixed`.
- `steps` (required, at least one): the heart of the log. `reverted` is `yes`
  or `no`.
- `apps` (optional): streaming apps you checked after filtering, with
  `status` one of `works`, `broken`, `untested`. Never mark an app `works`
  without having opened it in this session.
- `outcome` (optional): short free-text summary.

The converter prints Markdown rows you can paste into the session-log table in
[TESTING.md](../../TESTING.md), plus a status-table note when a claim changes
state. With `--json` it instead prints a normalized model report, the format
that `scripts/validate_model_report.py` checks for community submissions.
