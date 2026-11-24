#!/usr/bin/env python3
"""Build a privacy-safe HTML "session pack" from local DNS query logs.

Usage:
    python3 scripts/build_session_pack.py LOG -o report.html [--before OLDLOG]
        [--format FMT] [--blocklist LIST]... [--name-domain DOMAIN]...

Privacy by default: no domain is named in the report unless you list it with
--name-domain, one deliberate choice per domain. Matching a blocklist is used
only for aggregate counts - a list you supply can contain anything, so a
match is not evidence that a domain is public or non-personal. File names,
client addresses, timestamps and DNS answers never enter the report. There
is no flag that relaxes this. No network requests are made. Review the
report before sharing it; aggregate counts still describe usage volume.
"""
import argparse
import datetime
import html
import os
import sys
import tempfile
from collections import Counter

from classify_dns_log import DOMAIN_RE, iter_queries, load_blocklist, norm, is_blocked

CSS = """
body { font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 46rem;
       padding: 0 1rem; color: #1a1a1a; line-height: 1.5; }
h1 { font-size: 1.4rem; } h2 { font-size: 1.1rem; margin-top: 2rem; }
table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
th, td { border: 1px solid #ccc; padding: 0.3rem 0.6rem; text-align: left; }
.domains td:first-child { overflow-wrap: anywhere; word-break: break-word; }
th { background: #f0f0f0; }
td.num, th.num { text-align: right; }
.note { background: #fff8e6; border: 1px solid #e0c878; padding: 0.6rem 0.9rem; }
.meta { color: #555; font-size: 0.9rem; }
@media (max-width: 40rem) {
  .domains, .domains thead, .domains tbody, .domains tr, .domains td {
    display: block; width: 100%; box-sizing: border-box; }
  .domains thead { display: none; }
  .domains tr { border: 1px solid #ccc; margin-bottom: 0.6rem; padding: 0.2rem 0; }
  .domains td { border: none; text-align: left; padding: 0.15rem 0.6rem; }
  .domains td::before { content: attr(data-label) ": "; font-weight: 600; }
  .domains td.num { text-align: left; }
}
"""


def summarize(path, input_format, blocked, name_domains):
    """Aggregate one local log. Returns counts plus counts for opted-in domains."""
    total = 0
    filtered = 0
    all_domains = Counter()
    for domain, _client, is_filtered in iter_queries(path, input_format):
        total += 1
        all_domains[domain] += 1
        if is_filtered:
            filtered += 1
    matched = {d: c for d, c in all_domains.items() if is_blocked(d, blocked)}
    named = {}
    for domain in name_domains:
        if domain in all_domains:
            named[domain] = (all_domains[domain], 0)
    # Recompute filtered counts for the few named domains only.
    if named:
        for domain, _client, is_filtered in iter_queries(path, input_format):
            if domain in named and is_filtered:
                named[domain] = (named[domain][0], named[domain][1] + 1)
    return {
        "total": total,
        "filtered": filtered,
        "unique": len(all_domains),
        "matched_unique": len(matched),
        "matched_queries": sum(matched.values()),
        "named": named,
    }


def load_blocklists(paths):
    blocked = {}
    for list_path in paths:
        for domain, scope in load_blocklist(list_path).items():
            blocked[domain] = blocked.get(domain, False) or scope
    return blocked


def _pct(part, whole):
    return (100.0 * part / whole) if whole else 0.0


def render_html(after, before, generated_on):
    """Render the report. Every dynamic value is HTML-escaped."""

    # Metrics as rows, logs as columns: readable on narrow screens.
    after_label = "Current log" if before else "This log"
    col_head = ("<th class=\"num\">Earlier log</th>" if before else "")
    col_head += "<th class=\"num\">{}</th>".format(html.escape(after_label))

    def metric_row(label, before_value, after_value):
        row = "<tr><td>{}</td>".format(html.escape(label))
        if before:
            row += "<td class=\"num\">{}</td>".format(before_value)
        return row + "<td class=\"num\">{}</td></tr>".format(after_value)

    def cells(stats):
        return (str(stats["total"]),
                "{} ({:.1f}%)".format(stats["filtered"],
                                      _pct(stats["filtered"], stats["total"])),
                str(stats["unique"]),
                "{} ({} queries)".format(stats["matched_unique"], stats["matched_queries"]),
                "{} ({} queries)".format(stats["unique"] - stats["matched_unique"],
                                        stats["total"] - stats["matched_queries"]))

    metrics = ("Queries", "Blocked", "Unique domains in the log",
               "Blocklist matches (counted, not named)", "Other domains (counted, not named)")
    b_cells = cells(before) if before else (None,) * len(metrics)
    a_cells = cells(after)
    rows = "".join(metric_row(label, b_cells[i], a_cells[i])
                   for i, label in enumerate(metrics))
    summary_table = "<table><thead><tr><th>Metric</th>{}</tr></thead><tbody>{}</tbody></table>".format(
        col_head, rows)

    comparison_note = ""
    if before:
        comparison_note = """
<p class="note">The two logs are not a controlled experiment. Differences can
come from what was watched, how long the TV was on, resolver caching and the
time of day. This comparison does not measure the effect of the TV, the
filter or any settings change.</p>"""

    named_union = sorted(set(after["named"]) | set(before["named"]) if before
                         else set(after["named"]))
    if named_union:
        body = []
        for domain in named_union:
            a_q, a_f = after["named"].get(domain, (0, 0))
            cells = ("<td data-label=\"Domain\">{}</td>"
                     "<td class=\"num\" data-label=\"Queries\">{}</td>"
                     "<td class=\"num\" data-label=\"Blocked\">{}</td>").format(
                         html.escape(domain), a_q, a_f)
            if before:
                b_q, b_f = before["named"].get(domain, (0, 0))
                cells += ("<td class=\"num\" data-label=\"Queries (earlier log)\">{}</td>"
                          "<td class=\"num\" data-label=\"Blocked (earlier log)\">{}</td>"
                          ).format(b_q, b_f)
            body.append("<tr>{}</tr>".format(cells))
        cols = ("<th>Domain (you chose to name it)</th><th class=\"num\">Queries</th>"
                "<th class=\"num\">Blocked</th>")
        if before:
            cols += ("<th class=\"num\">Queries (earlier log)</th>"
                     "<th class=\"num\">Blocked (earlier log)</th>")
        named_table = ("<table class=\"domains\"><thead><tr>{}</tr></thead>"
                       "<tbody>{}</tbody></table>").format(cols, "".join(body))
        named_intro = ("Only the domains below are named, each one because you "
                       "listed it explicitly when building this report.")
    else:
        named_table = "<p>No domain is named in this report.</p>"
        named_intro = ""

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VIDAA Clean TV - DNS session pack</title>
<style>{css}</style>
</head>
<body>
<h1>VIDAA Clean TV - DNS session pack</h1>
<p class="meta">Generated {date} by scripts/build_session_pack.py from local
DNS query log(s). The logs themselves stay on the owner's machine.</p>

<h2>Summary</h2>
{summary_table}
{comparison_note}

<h2>Named domains</h2>
<p>{named_intro}</p>
{named_table}

<h2>Privacy</h2>
<p class="note">No domain is named unless the report's author listed it
explicitly. Every other domain appears only as an aggregate count. Blocklist
matches are counted in aggregate too: matching a list is not evidence that a
domain is public or harmless. Client addresses, timestamps, DNS answers and
file names were never read into this report. Aggregate counts still describe
overall usage volume; share the report only where that is acceptable.</p>

<h2>Method</h2>
<p>Built offline with the open-source VIDAA Clean TV tools
(https://github.com/HALCONDEORO/vidaa-clean-tv): the logs were classified
locally, matched against the blocklist(s) the author supplied, and rendered
without network access. Conclusions cover only queries visible in the logs.</p>
</body>
</html>
""".format(css=CSS, date=html.escape(generated_on), summary_table=summary_table,
           comparison_note=comparison_note, named_intro=html.escape(named_intro),
           named_table=named_table)


def guard_output(output, inputs):
    """Refuse to let the report overwrite any input, via any alias.

    realpath catches symlinks and path aliases; samefile catches hardlinks
    when the output already exists. Every input is checked: both logs and
    every blocklist, not only the main log.
    """
    out_real = os.path.realpath(output)
    for source in inputs:
        if os.path.realpath(source) == out_real:
            raise ValueError("Refusing to overwrite an input file. Choose another output.")
        if os.path.exists(output) and os.path.exists(source):
            try:
                if os.path.samefile(source, output):
                    raise ValueError("Refusing to overwrite an input file. Choose another output.")
            except OSError:
                raise ValueError("Cannot compare input and output paths safely.")


def write_report_atomic(path, text):
    """Write the report atomically; a destination symlink is replaced, never followed."""
    destination = os.path.abspath(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=os.path.dirname(destination),
                                         prefix=".session-pack-", suffix=".tmp",
                                         delete=False) as fh:
            temporary = fh.name
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Local DNS query log (the current one when --before is used)")
    parser.add_argument("-o", "--output", required=True, help="New HTML report, never an input file")
    parser.add_argument("--before", default=None,
                        help="Optional earlier log for a before/after comparison (same formats)")
    parser.add_argument("--format", default="auto",
                        help="Input format: auto (default), adguard, adguard-jsonl, pihole-ftl, dnsmasq")
    parser.add_argument("--blocklist", action="append", default=[],
                        help="Blocklist for aggregate match counts only; repeatable. "
                             "A match never causes a domain to be named.")
    parser.add_argument("--name-domain", action="append", default=[],
                        help="Name this exact domain in the report; repeatable. "
                             "The only way any domain is named.")
    parser.add_argument("--date", default=None,
                        help="Report date (YYYY-MM-DD); defaults to today. Mainly for reproducible tests.")
    args = parser.parse_args(argv)
    generated_on = args.date or datetime.date.today().isoformat()
    if args.date:
        try:
            datetime.date.fromisoformat(args.date)
        except ValueError:
            parser.exit(1, "--date must be YYYY-MM-DD\n")
    name_domains = []
    for domain in args.name_domain:
        cleaned = norm(domain.strip()) if isinstance(domain, str) else ""
        if not cleaned or not DOMAIN_RE.fullmatch(cleaned):
            parser.exit(1, "Invalid --name-domain value; use a plain hostname.\n")
        if cleaned not in name_domains:
            name_domains.append(cleaned)
    try:
        inputs = [args.input] + ([args.before] if args.before else []) + list(args.blocklist)
        guard_output(args.output, inputs)
        blocked = load_blocklists(args.blocklist)
        after = summarize(args.input, args.format, blocked, name_domains)
        before = summarize(args.before, args.format, blocked, name_domains) if args.before else None
        # A zero-query parse is a format problem, not evidence of inactivity:
        # a malformed log or wrong --format must never become "the TV did
        # nothing". Refuse instead of writing a misleading empty report.
        for label, stats in (("input", after), ("--before log", before)):
            if stats is not None and stats["total"] == 0:
                parser.exit(1, "Parsed zero queries from the %s; check the log and --format. "
                               "No report written: an empty parse cannot conclude inactivity.\n"
                               % label)
        report = render_html(after, before, generated_on)
        write_report_atomic(args.output, report)
    except UnicodeError:
        parser.exit(1, "Input must be readable text; private values are not shown.\n")
    except (OSError, ValueError, RecursionError):
        parser.exit(1, "Cannot build the report. Check the log format and local paths; "
                       "no input values are shown.\n")
    print("Wrote the session pack. No domain is named unless you used --name-domain; "
          "review the HTML before sharing.")


if __name__ == "__main__":
    main()
