# Shared test report builder

`build_report.py` is the only report script in this repo. The canonical copy lives here. `scripts/sync-shared.sh` copies it into `skills/testing/*/scripts/build_report.py`, and `scripts/sync-shared.sh --check` fails when a copy differs. Edit only this folder.

Each testing skill must work when it is installed alone, because `npx skills` copies one skill folder at a time. That is why the script is duplicated instead of shared through a sibling skill.

## Contract

The script is one file with no dependencies beyond the Python 3.10+ standard library. It runs as `python3 scripts/build_report.py` or `uv run scripts/build_report.py`. The CSS, the print CSS and the email summary template are string constants inside the file. The script does not branch on skill type. Each skill's `references/report.md` decides which sections the agent writes.

```
python3 scripts/build_report.py test-reports/2026-10-24-rates/report.json \
  [--junit junit.xml ...] [--coverage coverage.json] [--root .] \
  [--out DIR] [--formats html,pdf,summary] [--validate-only] [--ci]
```

The agent runs `scripts/build_report.py` from the skill's own folder by its absolute path, because the skill may be installed in the project's `.claude/skills`, globally in `~/.claude/skills` or `~/.agents/skills`, or inside a plugin.

- Outputs go next to `report.json` unless `--out` is given. The convention is `test-reports/YYYY-MM-DD-<subject>/` in the tested project.
- `--formats` takes any comma-separated subset of `html`, `pdf`, `summary`. The default is `html,pdf`. An empty list is a usage error. Output names are `report.html`, `report.pdf` and `summary.html`.
- JUnit XML and coverage JSON passed in are copied into the output folder (as `junit.xml`, or `junit-1.xml`, `junit-2.xml` when there are several, and `coverage.json`), so the artifact folder is complete. An input that already sits in the output folder under its target name is not copied again. Every input is read before any copy is written, so one input never overwrites another, and `junit.xml` or `junit-N.xml` files left by an earlier run are removed when the run copies JUnit XML, unless they are inputs of this run. The script never writes JUnit XML itself. JUnit XML from the test runner is the generic, machine-readable format.
- Exit 0 on success. Exit 1 with a list of validation errors, with a message for an unreadable or malformed input (missing file, bad JSON, bad XML), or for a usage error. Exit 2 when `pdf` was requested and Chrome was not found, timed out, or wrote no PDF. The HTML is still written, and the message names the `CHROME` environment variable.
- Chrome lookup order: `$CHROME`, macOS app paths (Google Chrome, Chromium, Microsoft Edge, Brave), then `google-chrome`, `google-chrome-stable`, `chromium`, `chromium-browser`, `microsoft-edge`, `brave-browser` on `PATH`.
- PDF: one Chrome run, `--headless=new --disable-gpu --no-pdf-header-footer --generate-pdf-document-outline --virtual-time-budget=5000 --print-to-pdf=<path> file://<report.html>`.

## report.json (written by the agent)

```json
{
  "title": "Unit test review of parcel-rates",
  "skill": "art-of-unit-testing",
  "meta": { "date": "2026-10-24", "branch": "main", "commit": "406f877", "command": "pytest -q", "tools": "pytest 8.3, Python 3.12" },
  "summary": "<p>HTML paragraphs.</p>",
  "verdict": { "status": "pass | conditional | fail", "text": "One or two sentences." },
  "sections": [
    {
      "heading": "What I deleted",
      "text": "<p>Optional HTML before the table.</p>",
      "table": { "columns": ["Test", "File", "Why"], "rows": [["<code>x</code>", "a.py", "..."]], "numeric": [] },
      "callout": { "tone": "pass | warn | fail | info", "text": "Optional." },
      "after": "<p>Optional HTML after the table.</p>"
    }
  ],
  "tests": [ { "id": "FR-1", "test": "test_order_over_limit_requires_approval", "location": "tests/test_order.py:12", "covers": "Orders over Q10,000 require approval" } ],
  "defects": [ { "id": "D-1", "test": "test_x", "location": "tests/test_x.py:40", "severity": "high", "expected": "...", "actual": "...", "analysis": "..." } ]
}
```

`sections`, `tests` and `defects` are optional, and `null` counts as empty. Strings in `summary`, `text`, `after` and table cells are trusted HTML written by the agent. All other strings are escaped.

## Derived by the script

| Derived section | Source |
|---|---|
| Test run: totals (passed, failed, errors, skipped, duration) and a per-suite table | JUnit XML |
| Failures: one block per failing case with the message | JUnit XML |
| Coverage: per-file statement and branch percentages and totals | coverage.py JSON (`coverage json`) or istanbul `coverage-summary.json` |
| Undocumented results, only with `--ci`: failing JUnit cases missing from `defects[]` and `tests[]` entries with no JUnit case, as a table of test, status and message | `report.json` + JUnit XML |
| Traceability: `tests[]` joined with the JUnit status of each test, or "no JUnit" when no JUnit XML was given | `report.json` + JUnit XML |
| Footer: input files and build time | arguments |

## Validation

- Every `tests[].location` and `defects[].location` must be `file:line`, the file must exist under `--root`, and that line or the 3 lines after it must contain the test name or the ID.
- With `--junit`: every `tests[].test` and `defects[].test` must match exactly one JUnit test case (by name, or by `classname.name`), and every failing or erroring JUnit case must appear in `defects[]`.
- `verdict.status` must be one of `pass`, `conditional`, `fail`.

With `--ci`, the two JUnit checks that only the current run can satisfy are relaxed, because a committed `report.json` cannot list failures that happen in this run. A failing or erroring JUnit case that is not in `defects[]`, and a `tests[]` entry that matches no JUnit case, are not validation errors. They are listed in the Undocumented results section. When any undocumented case failed or errored, the verdict shown in `report.html` and `summary.html` is fail, with a sentence that says why and repeats the written verdict. Location checks and the `verdict.status` check stay errors. Without `--ci`, validation is strict.

## Page layout

One page for every skill type, in this order: `h1` title, meta line, summary, verdict callout, the agent's sections, the derived sections (Test run, Undocumented results, Failures, Coverage, Traceability) when their inputs exist, and the footer.

The visual design follows a plain review document: a centered 1040 px column, DM Sans for text and JetBrains Mono for code (one Google Fonts link, Helvetica and Menlo fallbacks), `h2` with a 2 px accent rule, tables inside a bordered card with a dark header row and zebra rows, right-aligned tabular numbers for numeric columns, and green, amber and red only for status.

Light tokens: paper `#FAF8F4`, card `#FFFFFF`, text `#1F2933`, muted `#5F6B7A`, heading and table header `#223447`, accent `#3F7CAC`, line `#DDE3EA`, zebra `#F2F5F8`, pass `#1E7B4F`, warn `#B45309`, fail `#B42318`.
Dark tokens (`prefers-color-scheme: dark`, guarded by `:root:not([data-theme="light"])`): paper `#0E141B`, card `#121A24`, text `#E6EAF0`, muted `#A3ADBB`, heading `#9CC7DD`, accent `#6CC3D5`, line `#2A3645`, zebra `#172230`, pass `#5FD39A`, warn `#F6B26B`, fail `#F2877B`.

Print: `@media print` forces the light tokens, removes the page background, repeats `thead`, and avoids breaks inside rows and callouts. `@page { size: A4; margin: 18mm 16mm }` with the page number at the bottom center and the report title at the top right.

`summary.html` is the email body: a 600 px table with inline styles only, no `<style>` block, no web fonts and no dark mode. It holds the title, the meta line, the verdict, the counts table, and the line "The full report is attached as report.pdf."

## CI and email

The skill's `references/report.md` shows this GitHub Actions block. The user picks the formats with `--formats` and picks the attachments in the mail step. The test step must not stop the job before the report is built, so give it `continue-on-error: true` or put `if: always()` on every later step. The `--ci` flag turns failures that the committed `report.json` does not list into an Undocumented results section instead of a validation error. The path `.claude/skills/<skill>/scripts/build_report.py` exists in CI only when the skill is installed at project level (`npx skills add danihrndzld/skills --skill <skill>`, with the folder committed) or when a copy of the script is committed to the repo.

```yaml
- name: Build the test report
  if: always()
  run: python3 .claude/skills/art-of-e2e-testing/scripts/build_report.py test-reports/latest/report.json --junit test-reports/latest/junit.xml --formats html,pdf,summary --ci
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-report
    path: test-reports/latest/
- uses: dawidd6/action-send-mail@v4
  if: always()
  with:
    server_address: ${{ secrets.SMTP_HOST }}
    server_port: 587
    username: ${{ secrets.SMTP_USER }}
    password: ${{ secrets.SMTP_PASS }}
    subject: "Test report for ${{ github.repository }} at ${{ github.sha }}"
    to: team@example.com
    from: ci@example.com
    html_body: file://test-reports/latest/summary.html
    attachments: test-reports/latest/report.pdf,test-reports/latest/junit.xml
```
