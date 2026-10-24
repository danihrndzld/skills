#!/usr/bin/env python3
"""Build report.html, report.pdf and summary.html from report.json, JUnit XML and coverage JSON.

Usage:
  python3 build_report.py report.json [--junit junit.xml ...] [--coverage coverage.json]
      [--root .] [--out DIR] [--formats html,pdf,summary] [--validate-only] [--ci]

Counts, statuses and coverage come from the runner's files, never from report.json.
The contract is in shared/report/README.md of the skills repo.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from string import Template

FORMATS = ("html", "pdf", "summary")
STATUSES = ("pass", "conditional", "fail")
esc = html.escape

CSS = """
:root {
  --paper: #FAF8F4; --card: #FFFFFF; --text: #1F2933; --muted: #5F6B7A; --heading: #223447;
  --th-text: #FFFFFF; --accent: #3F7CAC; --line: #DDE3EA; --zebra: #F2F5F8;
  --pass: #1E7B4F; --warn: #B45309; --fail: #B42318;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #0E141B; --card: #121A24; --text: #E6EAF0; --muted: #A3ADBB; --heading: #9CC7DD;
    --th-text: #0E141B; --accent: #6CC3D5; --line: #2A3645; --zebra: #172230;
    --pass: #5FD39A; --warn: #F6B26B; --fail: #F2877B;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--text); font: 15px/1.55 "DM Sans", Helvetica, Arial, sans-serif; }
main { max-width: 1040px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { color: var(--heading); font-size: 26px; margin: 0 0 4px; }
h2 { color: var(--heading); font-size: 18px; margin: 36px 0 10px; padding-bottom: 6px; border-bottom: 2px solid var(--accent); }
h3 { color: var(--heading); font-size: 15px; margin: 18px 0 6px; }
p { margin: 6px 0 10px; max-width: 78ch; }
.meta { color: var(--muted); font-size: 13px; }
code, pre { font: 13px "JetBrains Mono", Menlo, Consolas, monospace; overflow-wrap: anywhere; }
pre { white-space: pre-wrap; background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 10px 12px; margin: 6px 0 14px; }
.card { overflow-x: auto; background: var(--card); border: 1px solid var(--line); border-radius: 6px; margin: 8px 0 12px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th { background: var(--heading); color: var(--th-text); text-align: left; padding: 8px 10px; font-weight: 600; }
td { padding: 8px 10px; vertical-align: top; border-top: 1px solid var(--line); }
tbody tr:nth-child(even) td { background: var(--zebra); }
td.nw { white-space: nowrap; }
th.n, td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.total td { font-weight: 700; }
.callout { border-left: 4px solid var(--accent); background: var(--card); border-radius: 0 6px 6px 0; padding: 10px 14px; margin: 10px 0 14px; }
.callout.pass { border-color: var(--pass); } .callout.warn { border-color: var(--warn); } .callout.fail { border-color: var(--fail); }
.verdict { font-size: 16px; }
.verdict b { text-transform: uppercase; letter-spacing: .04em; margin-right: 6px; }
.s-pass { color: var(--pass); font-weight: 600; } .s-warn { color: var(--warn); font-weight: 600; }
.s-fail { color: var(--fail); font-weight: 600; } .s-muted { color: var(--muted); }
footer { margin-top: 40px; padding-top: 10px; border-top: 1px solid var(--line); color: var(--muted); font-size: 12px; }
"""

PRINT_CSS = """
@page { size: A4; margin: 18mm 16mm;
  @bottom-center { content: counter(page) " / " counter(pages); font: 9pt Helvetica, Arial, sans-serif; color: #5F6B7A; }
  @top-right { content: "$title"; font: 9pt Helvetica, Arial, sans-serif; color: #5F6B7A; } }
@media print {
  :root, :root:not([data-theme="light"]) {
    --paper: #FFFFFF; --card: #FFFFFF; --text: #1F2933; --muted: #5F6B7A; --heading: #223447;
    --th-text: #FFFFFF; --accent: #3F7CAC; --line: #DDE3EA; --zebra: #F2F5F8;
    --pass: #1E7B4F; --warn: #B45309; --fail: #B42318;
  }
  body { background: none; font-size: 10.5pt; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  main { max-width: none; padding: 0; }
  .card { overflow: visible; }
  table { font-size: 9.5pt; }
  thead { display: table-header-group; }
  tr, .callout, pre { break-inside: avoid; }
  h2, h3 { break-after: avoid; }
}
"""

SUMMARY = Template("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>$title</title></head>
<body style="margin:0;padding:0;background:#FFFFFF;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;margin:0 auto;font-family:Helvetica,Arial,sans-serif;color:#1F2933;font-size:14px;line-height:1.5;">
<tr><td style="padding:24px 16px 4px;"><h1 style="margin:0;font-size:22px;color:#223447;">$title</h1></td></tr>
<tr><td style="padding:0 16px 12px;color:#5F6B7A;font-size:12px;">$meta</td></tr>
<tr><td style="padding:0 16px 16px;"><div style="border-left:4px solid $color;padding:8px 12px;"><b style="color:$color;text-transform:uppercase;">$status</b> $verdict</div></td></tr>
<tr><td style="padding:0 16px 16px;">$counts</td></tr>
<tr><td style="padding:0 16px 24px;">The full report is attached as report.pdf.</td></tr>
</table>
</body></html>
""")
SUMMARY_COLORS = {"pass": "#1E7B4F", "conditional": "#B45309", "fail": "#B42318"}
CASE_LABELS = {"passed": ("passed", "s-pass"), "failed": ("failed", "s-fail"), "error": ("error", "s-fail"),
               "skipped": ("skipped", "s-warn"), None: ("not run", "s-muted")}


# ----------------------------------------------------------------------------- inputs

def parse_junit(paths: list[Path]) -> tuple[list[dict], list[dict]]:
    """Return (cases, suites). Handles <testsuites> and bare <testsuite> roots and nested suites."""
    cases, suites = [], []
    for path in paths:
        for suite in ET.parse(path).getroot().iter("testsuite"):
            own = []
            for tc in suite.findall("testcase"):
                status, message = "passed", ""
                for tag, name in (("failure", "failed"), ("error", "error"), ("skipped", "skipped")):
                    node = tc.find(tag)
                    if node is not None:
                        status = name
                        message = ((node.get("message") or "") + "\n\n" + (node.text or "")).strip()
                        break
                own.append({"name": tc.get("name", ""), "classname": tc.get("classname", ""),
                            "status": status, "message": message, "time": float(tc.get("time") or 0)})
            if own:
                # A suite with child suites reports their time in its own; count only its direct cases.
                nested = suite.find("testsuite") is not None
                time = (0 if nested else float(suite.get("time") or 0)) or sum(c["time"] for c in own)
                suites.append({"name": suite.get("name", path.name), "cases": own, "time": time})
                cases += own
    return cases, suites


def parse_coverage(path: Path) -> dict:
    """coverage.py JSON or istanbul coverage-summary.json -> {"files": [(name, stmt%, branch%)], "total": ...}."""
    data = json.loads(path.read_text())
    if "totals" in data:
        def row(name, s):
            stmt = 100 * s["covered_lines"] / s["num_statements"] if s.get("num_statements") else s.get("percent_covered")
            branch = 100 * s["covered_branches"] / s["num_branches"] if s.get("num_branches") else None
            return (name, stmt, branch)
        files = [row(n, f["summary"]) for n, f in sorted(data.get("files", {}).items())]
        return {"files": files, "total": row("Total", data["totals"])}
    if "total" in data:
        def row(name, s):
            return (name, s["lines"]["pct"], s["branches"]["pct"] if s["branches"]["total"] else None)
        files = [row(n, s) for n, s in sorted(data.items()) if n != "total"]
        return {"files": files, "total": row("Total", data["total"])}
    raise ValueError(f"unknown coverage format: {path}")


# ----------------------------------------------------------------------------- validation

def find_case(cases: list[dict], test: str) -> list[dict]:
    return [c for c in cases if test in (c["name"], f"{c['classname']}.{c['name']}")]


def check_location(entry: dict, kind: str, root: Path) -> str | None:
    loc = str(entry.get("location", ""))
    file, sep, line = loc.rpartition(":")
    if not sep or not file or not line.isdigit():
        return f"{kind} {entry.get('id')}: location '{loc}' is not file:line."
    path = root / file
    if not path.is_file():
        return f"{kind} {entry.get('id')}: file {file} does not exist under {root}."
    lines = path.read_text(errors="replace").splitlines()[int(line) - 1:int(line) + 3]
    needles = [str(entry[k]) for k in ("test", "id") if entry.get(k)]
    if not any(n in text for text in lines for n in needles):
        return f"{kind} {entry.get('id')}: {loc} and the 3 lines after it do not contain '{entry.get('test')}' or '{entry.get('id')}'."
    return None


def undocumented_failures(report: dict, cases: list[dict]) -> list[dict]:
    """Failing or erroring JUnit cases that no defects[] entry names."""
    listed = report.get("defects") or []
    return [c for c in cases if c["status"] in ("failed", "error")
            and not any(find_case([c], str(d.get("test", ""))) for d in listed)]


def undocumented_results(report: dict, cases: list[dict]) -> list[list[str]]:
    """Rows (test, status, message) for the Undocumented results section of a --ci build."""
    rows = [[f"{c['classname']}.{c['name']}", c["status"], c["message"]] for c in undocumented_failures(report, cases)]
    for t in report.get("tests") or []:
        if not find_case(cases, str(t.get("test", ""))):
            rows.append([str(t.get("test", "")), "not in JUnit", f"{t.get('id')} is listed in tests[], but this run has no such test case."])
    return rows


def validate(report: dict, cases: list[dict] | None, root: Path, ci: bool = False) -> list[str]:
    """With ci, results that only this run can know (new failures, missing test cases) are not errors."""
    errors = []
    status = (report.get("verdict") or {}).get("status")
    if status not in STATUSES:
        errors.append(f"verdict.status is '{status}'; it must be one of {', '.join(STATUSES)}.")
    for kind, key in (("Test", "tests"), ("Defect", "defects")):
        for entry in report.get(key) or []:
            if err := check_location(entry, kind, root):
                errors.append(err)
            if cases is not None:
                found = len(find_case(cases, str(entry.get("test", ""))))
                if found != 1 and not (ci and kind == "Test" and found == 0):
                    errors.append(f"{kind} {entry.get('id')}: '{entry.get('test')}' matches {found} JUnit test cases, expected 1.")
    if cases is not None and not ci:
        for c in undocumented_failures(report, cases):
            errors.append(f"JUnit test {c['classname']}.{c['name']} {c['status']} but is not listed in defects[].")
    return errors


# ----------------------------------------------------------------------------- rendering

def td_class(numeric: bool, value) -> str:
    """Numbers align right; short cells (IDs, file:line) never wrap mid-token."""
    short = len(re.sub(r"<[^>]+>", "", str(value))) <= 20
    classes = " ".join(c for c, on in (("n", numeric), ("nw", short)) if on)
    return f' class="{classes}"' if classes else ""


def table(columns: list[str], rows: list[list], numeric=(), trusted=True, total_row=False) -> str:
    num = {i for i, c in enumerate(columns) if i in numeric or c in numeric}
    cell = (lambda v: str(v)) if trusted else (lambda v: esc(str(v)))
    head = "".join(f'<th{" class=n" if i in num else ""}>{esc(c)}</th>' for i, c in enumerate(columns))
    body = []
    for r, row in enumerate(rows):
        cls = ' class="total"' if total_row and r == len(rows) - 1 else ""
        tds = "".join(f'<td{td_class(i in num, v)}>{cell(v)}</td>' for i, v in enumerate(row))
        body.append(f"<tr{cls}>{tds}</tr>")
    return f'<div class="card"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def callout(tone: str, inner: str) -> str:
    tone = tone if tone in ("pass", "warn", "fail", "info") else "info"
    return f'<div class="callout {tone}">{inner}</div>'


def meta_line(report: dict) -> str:
    meta = report.get("meta") or {}
    parts = [esc(str(meta["date"]))] if meta.get("date") else []
    for key, label in (("branch", "Branch"), ("commit", "commit"), ("command", "command")):
        if meta.get(key):
            parts.append(f"{label} <code>{esc(str(meta[key]))}</code>")
    if meta.get("tools"):
        parts.append(esc(str(meta["tools"])))
    if report.get("skill"):
        parts.append(f"Skill <code>{esc(str(report['skill']))}</code>")
    return ", ".join(parts)


def counts(cases: list[dict], time: float | None = None) -> dict:
    out = {s: sum(c["status"] == s for c in cases) for s in ("passed", "failed", "error", "skipped")}
    out["total"], out["time"] = len(cases), sum(c["time"] for c in cases) if time is None else time
    return out


def code(text) -> str:
    """Escaped <code> with break points after _ and / so long test names wrap between words."""
    return "<code>" + re.sub(r"([_/])", r"\1<wbr>", esc(str(text))) + "</code>"


def pct(v) -> str:
    """istanbul writes "Unknown" when a file has nothing to count."""
    is_number = isinstance(v, (int, float)) and not isinstance(v, bool)
    return f"{v:.1f}%" if is_number else "n/a"


def derived_sections(report: dict, cases, suites, coverage, undocumented=()) -> str:
    out = []
    if cases is not None:
        n = counts(cases, sum(s["time"] for s in suites))
        out.append("<h2>Test run</h2>")
        out.append(table(["Total", "Passed", "Failed", "Errors", "Skipped", "Duration"],
                         [[n["total"], n["passed"], n["failed"], n["error"], n["skipped"], f"{n['time']:.2f} s"]],
                         numeric=range(6), trusted=False))
        rows = []
        for s in suites:
            k = counts(s["cases"], s["time"])
            rows.append([s["name"], k["total"], k["passed"], k["failed"], k["error"], k["skipped"], f"{k['time']:.2f} s"])
        out.append(table(["Suite", "Tests", "Passed", "Failed", "Errors", "Skipped", "Duration"], rows,
                         numeric=range(1, 7), trusted=False))
        if undocumented:
            out.append("<h2>Undocumented results</h2>")
            out.append("<p>This CI run has results that report.json does not describe. "
                       "Add each failure to defects[], or fix the test, before the next review.</p>")
            out.append(table(["Test", "Status", "Message"], [[code(t), esc(s), f"<pre>{esc(m)}</pre>" if m else ""]
                                                            for t, s, m in undocumented]))
        failing = [c for c in cases if c["status"] in ("failed", "error")]
        if failing:
            out.append("<h2>Failures</h2>")
            defects = report.get("defects") or []
            for c in failing:
                d = next((d for d in defects if find_case([c], str(d.get("test", "")))), {})
                out.append(f'<h3><span class="s-fail">{c["status"]}</span> {code(c["classname"] + "." + c["name"])}</h3>')
                if d:
                    out.append(callout("fail", f"<b>{esc(str(d.get('id')))}</b> ({esc(str(d.get('severity', 'n/a')))}). "
                                       f"Expected: {esc(str(d.get('expected', '')))}. Actual: {esc(str(d.get('actual', '')))}. "
                                       f"{esc(str(d.get('analysis', '')))}"))
                out.append(f"<pre>{esc(c['message'])}</pre>")
    if coverage:
        out.append("<h2>Coverage</h2>")
        rows = [[name, pct(s), pct(b)] for name, s, b in coverage["files"] + [coverage["total"]]]
        out.append(table(["File", "Statements", "Branches"], rows, numeric=(1, 2), trusted=False, total_row=True))
    if report.get("tests"):
        out.append("<h2>Traceability</h2>")
        rows = []
        for t in report["tests"]:
            if cases is None:
                label, cls = "no JUnit", "s-muted"
            else:
                match = find_case(cases, str(t.get("test", "")))
                label, cls = CASE_LABELS[match[0]["status"] if len(match) == 1 else None]
            rows.append([esc(str(t.get("id", ""))), code(t.get("test", "")), code(t.get("location", "")), esc(str(t.get("covers", ""))),
                         f'<span class="{cls}">{label}</span>'])
        out.append(table(["ID", "Test", "Location", "Covers", "Status"], rows))
    return "\n".join(out)


def render_html(report: dict, cases, suites, coverage, inputs: list[str], undocumented=()) -> str:
    title = str(report.get("title", "Test report"))
    css_title = title.replace("\\", "\\\\").replace('"', '\\"').replace("<", "\\3C ")
    verdict = report.get("verdict") or {}
    status = verdict.get("status", "")
    tone = {"pass": "pass", "conditional": "warn", "fail": "fail"}.get(status, "info")
    body = [f"<h1>{esc(title)}</h1>", f'<p class="meta">{meta_line(report)}</p>', report.get("summary", ""),
            callout(tone, f'<span class="verdict"><b class="s-{tone}">{esc(status)}</b>{esc(str(verdict.get("text", "")))}</span>')]
    for s in report.get("sections") or []:
        body.append(f"<h2>{esc(str(s.get('heading', '')))}</h2>")
        body.append(s.get("text", ""))
        if t := s.get("table"):
            body.append(table(t.get("columns", []), t.get("rows", []), t.get("numeric", [])))
        if c := s.get("callout"):
            body.append(callout(c.get("tone", "info"), esc(str(c.get("text", "")))))
        body.append(s.get("after", ""))
    body.append(derived_sections(report, cases, suites, coverage, undocumented))
    built = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    body.append(f"<footer>Built {esc(built)} by build_report.py from {esc(', '.join(inputs))}.</footer>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap">
<style>{CSS}{Template(PRINT_CSS).substitute(title=css_title)}</style>
</head>
<body>
<main>
{chr(10).join(b for b in body if b)}
</main>
</body>
</html>
"""


def render_summary(report: dict, cases) -> str:
    verdict = report.get("verdict") or {}
    status = verdict.get("status", "")
    td = 'style="padding:6px 8px;border:1px solid #DDE3EA;text-align:right;"'
    if cases is None:
        count_html = "No JUnit XML was given."
    else:
        n = counts(cases)
        heads = "".join(f'<th style="padding:6px 8px;background:#223447;color:#FFFFFF;text-align:right;">{h}</th>'
                        for h in ("Total", "Passed", "Failed", "Errors", "Skipped"))
        cells = "".join(f"<td {td}>{n[k]}</td>" for k in ("total", "passed", "failed", "error", "skipped"))
        count_html = (f'<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:14px;">'
                      f"<tr>{heads}</tr><tr>{cells}</tr></table>")
    plain_meta = html.unescape(meta_line(report).replace("<code>", "").replace("</code>", ""))
    return SUMMARY.substitute(title=esc(str(report.get("title", "Test report"))), meta=esc(plain_meta),
                              color=SUMMARY_COLORS.get(status, "#5F6B7A"), status=esc(status),
                              verdict=esc(str(verdict.get("text", ""))), counts=count_html)


# ----------------------------------------------------------------------------- PDF

def find_chrome() -> str | None:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for app in ("Google Chrome.app/Contents/MacOS/Google Chrome", "Chromium.app/Contents/MacOS/Chromium",
                "Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "Brave Browser.app/Contents/MacOS/Brave Browser"):
        if os.access(f"/Applications/{app}", os.X_OK):
            return f"/Applications/{app}"
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
        if found := shutil.which(name):
            return found
    return None


def print_pdf(chrome: str, html_path: Path, pdf_path: Path) -> None:
    pdf_path.unlink(missing_ok=True)
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--generate-pdf-document-outline", "--virtual-time-budget=5000",
                    f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120, check=False)
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Chrome did not write {pdf_path}")


# ----------------------------------------------------------------------------- main

class Parser(argparse.ArgumentParser):
    """Usage errors exit 1, because exit 2 means the PDF was not built."""

    def error(self, message: str):
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def copy_inputs(pairs: list[tuple[Path, Path]], out: Path) -> None:
    """Copy (source, destination) pairs into out without one input overwriting another.

    Every source is read into a temporary file before any destination is written. JUnit files
    left by an earlier run (junit.xml, junit-N.xml) that this run does not write are removed
    when this run copies JUnit XML, unless they are inputs of this run.
    """
    staged = []
    for i, (src, dest) in enumerate(pairs):
        if dest.exists() and dest.samefile(src):
            continue
        tmp = out / f".build_report-{i}.tmp"
        shutil.copyfile(src, tmp)
        staged.append((tmp, dest))
    keep = {dest.name for _, dest in pairs}
    if any(name.startswith("junit") for name in keep):
        for old in out.glob("junit*.xml"):
            is_input = any(old.samefile(src) for src, _ in pairs)
            if re.fullmatch(r"junit(-\d+)?\.xml", old.name) and old.name not in keep and not is_input:
                old.unlink()
    for tmp, dest in staged:
        tmp.replace(dest)


def main(argv: list[str] | None = None) -> int:
    ap = Parser(description="Build an HTML/PDF test report from report.json, JUnit XML and coverage JSON.")
    ap.add_argument("report", type=Path)
    ap.add_argument("--junit", type=Path, action="append", default=[])
    ap.add_argument("--coverage", type=Path)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--formats", default="html,pdf")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--ci", action="store_true",
                    help="list new failures and missing test cases in an Undocumented results section instead of failing validation")
    args = ap.parse_args(argv)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    if not formats:
        ap.error(f"--formats is empty; choose from {', '.join(FORMATS)}")
    if bad := [f for f in formats if f not in FORMATS]:
        ap.error(f"unknown format(s) {', '.join(bad)}; choose from {', '.join(FORMATS)}")
    try:
        report = json.loads(args.report.read_text())
        if not isinstance(report, dict):
            raise ValueError(f"{args.report} must hold a JSON object")
        cases, suites = parse_junit(args.junit) if args.junit else (None, [])
        coverage = parse_coverage(args.coverage) if args.coverage else None
    except (ET.ParseError, OSError, json.JSONDecodeError, ValueError) as e:
        print(f"Could not read the inputs: {e}", file=sys.stderr)
        return 1

    errors = validate(report, cases, args.root, args.ci)
    if errors:
        print(f"{len(errors)} validation error(s) in {args.report}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    if args.validate_only:
        print(f"{args.report} is valid.")
        return 0

    undocumented = undocumented_results(report, cases) if args.ci and cases is not None else []
    if failures := sum(row[1] in ("failed", "error") for row in undocumented):
        verdict = report.get("verdict") or {}
        report = {**report, "verdict": {"status": "fail", "text": (
            f"The verdict is fail because this run has {failures} failing or erroring test(s) that report.json "
            f"does not list in defects[]; see Undocumented results. The written verdict was "
            f"{verdict.get('status')}: {verdict.get('text', '')}")}}

    out = args.out or args.report.parent
    out.mkdir(parents=True, exist_ok=True)
    pairs = [(src, out / ("junit.xml" if len(args.junit) == 1 else f"junit-{i}.xml")) for i, src in enumerate(args.junit, 1)]
    if args.coverage:
        pairs.append((args.coverage, out / "coverage.json"))
    copy_inputs(pairs, out)

    inputs = [p.name for p in [args.report, *args.junit, *([args.coverage] if args.coverage else [])]]
    html_path = out / "report.html"
    if "html" in formats or "pdf" in formats:
        html_path.write_text(render_html(report, cases, suites, coverage, inputs, undocumented))
        if "html" in formats:
            print(html_path)
    if "summary" in formats:
        (out / "summary.html").write_text(render_summary(report, cases))
        print(out / "summary.html")
    if "pdf" in formats:
        chrome = find_chrome()
        if not chrome:
            print("No Chrome, Chromium, Edge or Brave found, so report.pdf was not built. "
                  "Install one or set the CHROME environment variable to its binary.", file=sys.stderr)
            return 2
        try:
            print_pdf(chrome, html_path, out / "report.pdf")
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            print(f"report.pdf was not built: {e}. The HTML is in {html_path}.", file=sys.stderr)
            return 2
        print(out / "report.pdf")
        if "html" not in formats:
            html_path.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
