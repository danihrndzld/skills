# CI/CD report

Produce a report only when the user asks for one. The agent writes `report.json` with its judgment. The script `scripts/build_report.py` validates it, adds the sections it can derive from JUnit XML and coverage JSON, and renders the outputs. Run `scripts/build_report.py` from this skill's own folder by its absolute path. The skill may be installed in the project's `.claude/skills`, globally in `~/.claude/skills` or `~/.agents/skills`, or inside a plugin, so use the folder that holds this skill's `SKILL.md`. It is called `$SKILL_DIR` below. Run it from the root of the project under review.

## Steps

1. Create `test-reports/YYYY-MM-DD-<subject>/` in the project, for example `test-reports/2026-10-24-ci-pipeline/`.
2. Run the suites you measured with JUnit XML output into that folder (`pytest --junitxml`, `jest --reporters=jest-junit`, `vitest --reporter=junit`, `go test` with `gotestsum --junitfile`). Add coverage JSON if the project produces it (`coverage json`, or istanbul `coverage-summary.json`).
3. Write `report.json` with the sections below.
4. Run the script. Fix every validation error it lists and run it again.
5. Open the HTML or render page 1 of the PDF to PNG (`pdftoppm -png -r 80 -f 1 -l 1`) and check it.

## CLI

```
python3 $SKILL_DIR/scripts/build_report.py test-reports/2026-10-24-ci-pipeline/report.json \
  [--junit junit.xml ...] [--coverage coverage.json] [--root .] \
  [--out DIR] [--formats html,pdf,summary] [--validate-only] [--ci]
```

- Outputs go next to `report.json` unless `--out` is given.
- `--formats` takes any comma separated subset of `html`, `pdf` and `summary`. The default is `html,pdf`. Outputs are `report.html`, `report.pdf` and `summary.html` (the email body). Ask the user which formats they want, and default to `html,pdf`.
- A CI/CD report often covers several suites. Pass `--junit` once per file, for example `--junit unit.xml --junit integration.xml --junit e2e.xml`. The script copies them into the output folder as `junit-1.xml`, `junit-2.xml` and so on, and aggregates the totals and the per suite table.
- Exit 0 means success. Exit 1 prints validation errors, unreadable inputs or a usage error. Exit 2 means `pdf` was requested and Chrome was not found, timed out, or wrote no PDF. The HTML is still written, and you can set the `CHROME` environment variable to the browser path.
- `uv run` works in place of `python3`. The script needs only the Python 3.10+ standard library.

## report.json

```json
{
  "title": "CI/CD review of parcel-rates",
  "skill": "art-of-cicd",
  "meta": { "date": "2026-10-24", "branch": "main", "commit": "406f877", "command": "gh run list; pytest -q", "tools": "GitHub Actions, pytest 8.3" },
  "summary": "<p>HTML paragraphs.</p>",
  "verdict": { "status": "pass | conditional | fail", "text": "One or two sentences." },
  "sections": [
    {
      "heading": "Pipeline map",
      "text": "<p>Optional HTML before the table.</p>",
      "table": { "columns": ["Stage", "Trigger", "Median duration"], "rows": [["lint", "pull_request", "0:42"]], "numeric": [2] },
      "callout": { "tone": "pass | warn | fail | info", "text": "Optional." },
      "after": "<p>Optional HTML after the table.</p>"
    }
  ],
  "tests": [ { "id": "F-3", "test": "test_charge_amount", "location": "tests/test_billing.py:40", "covers": "Retry wraps assertions" } ],
  "defects": [ { "id": "D-1", "test": "test_x", "location": "tests/test_x.py:40", "severity": "high", "expected": "...", "actual": "...", "analysis": "..." } ]
}
```

`sections`, `tests` and `defects` are optional. Strings in `summary`, `text`, `after` and table cells are trusted HTML. All other strings are escaped. `numeric` lists the zero based indexes of columns to right align.

The script derives these sections itself, so do not write them: Test run (totals and per suite table from JUnit XML), Failures (one block per failing case), Coverage (per file statement and branch percentages), Traceability (`tests[]` joined with JUnit status) and the footer.

Validation rules:

- Every `tests[].location` and `defects[].location` is `file:line`, the file exists under `--root`, and that line or the next 3 lines contain the test name or the ID.
- With `--junit`, every `tests[].test` and `defects[].test` matches exactly one JUnit test case, and every failing or erroring JUnit case appears in `defects[]`.
- With `--ci`, a failing or erroring JUnit case missing from `defects[]` and a `tests[]` entry that matches no JUnit case are not errors. The script lists them in an Undocumented results section and shows the verdict as fail when any of them failed. Location checks stay errors.
- `verdict.status` is `pass`, `conditional` or `fail`.

Use `tests[]` only for tests you cite as evidence, for example a test with a retry that wraps assertions. Pipeline findings that point at workflow files go in the Findings section table, not in `tests[]`.

## Sections for a CI/CD report

Write these in order. Skip a section only when it does not apply, and say why in one line in the summary.

1. Pipeline map. One row per job: workflow file, job, trigger (`pull_request`, `push`, `merge_group`, `schedule`), `needs:`, gate or transformation, median duration over recent runs and the source of the number (for example `gh run list --limit 20`).
2. Gates and thresholds. Each gate with its threshold and whether it blocks the merge: lint ruleset, coverage floor, required status checks, branch protection, smoke suite limits. Flag gates that run with `continue-on-error: true` or are not required.
3. Suite health. Totals and duration per suite, the slowest ten tests (from the JUnit `time` attribute), flaky tests (tests that failed and passed on the same commit, or that use reruns), and retries that wrap assertions. Compare against the budget of unit under 1 minute, integration under 5 and the full suite under 30.
4. DORA snapshot. The four metrics with the band, the data source and the time window for each. Write "not measured" with the reason when data is missing.
5. Delivery. Trunk practice (branch age, PR size), dependency pinning (lockfile, hashes, actions pinned by SHA), secrets handling, deployment strategy and rollback path.
6. Findings by severity. Table with ID, severity (high, medium, low), `file:line`, finding and proposed fix. High means the finding can ship a defect to production or leak a secret.
7. Changes made. Each change with `file:line`, and the run that verified it (job URL, or local command and result). Write "none" if you only reviewed.
8. Verdict. Use the `verdict` field: `pass` when no high findings remain, `conditional` when every high finding has an agreed fix, and `fail` otherwise.

## GitHub Actions and email

The user chooses the formats with `--formats`, which folder to upload as a CI artifact, and which files to attach to the email. A common choice is `summary.html` as the body and `report.pdf` plus the JUnit files as attachments.

```yaml
- name: Build the test report
  if: always()
  run: python3 .claude/skills/art-of-cicd/scripts/build_report.py test-reports/latest/report.json --junit test-reports/latest/unit.xml --junit test-reports/latest/e2e.xml --formats html,pdf,summary --ci
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: cicd-report
    path: test-reports/latest/
- uses: dawidd6/action-send-mail@v4
  if: always()
  with:
    server_address: ${{ secrets.SMTP_HOST }}
    server_port: 587
    username: ${{ secrets.SMTP_USER }}
    password: ${{ secrets.SMTP_PASS }}
    subject: "CI/CD report for ${{ github.repository }} at ${{ github.sha }}"
    to: team@example.com
    from: ci@example.com
    html_body: file://test-reports/latest/summary.html
    attachments: test-reports/latest/report.pdf,test-reports/latest/junit-1.xml,test-reports/latest/junit-2.xml
```

Pin both actions by commit SHA in a real pipeline (see `delivery.md`). The tags here keep the example readable.

The build step must run even when tests fail. Give the test step `continue-on-error: true`, or put `if: always()` on every later step as above, so the test step does not stop the job before the report is built. A committed `report.json` cannot list failures that first happen in this run, so `--ci` lists them, and `tests[]` entries that match no JUnit case, in an "Undocumented results" section instead of stopping with a validation error. When any of them failed, the verdict shown is fail.

The path `.claude/skills/art-of-cicd/scripts/build_report.py` works in CI only when the skill is installed at project level (`npx skills add danihrndzld/skills --skill art-of-cicd`, with the installed folder committed) or when you commit a copy of the script to the repo and point the step at it.
