# Test report (HTML, PDF, email summary)

Write a report only when the user asks for one, e.g., an HTML page, a PDF, an email summary or CI artifacts. Otherwise the step 7 text block in SKILL.md is the output.

The agent writes `report.json`, and `scripts/build_report.py` turns it into the report. The script needs only the Python 3.10+ standard library, plus Chrome for the PDF.

## Steps

First, pick a folder in the tested project, `test-reports/YYYY-MM-DD-<subject>/`, and call it `$R` below.

Second, run the tests so the runner writes JUnit XML into `$R`, and coverage JSON if the project already has a coverage tool.

| Runner | Command |
|---|---|
| pytest | `pytest --junitxml=$R/junit.xml --cov=src --cov-branch --cov-report=json:$R/coverage.json` |
| Vitest | `npx vitest run --reporter=junit --outputFile=$R/junit.xml --coverage --coverage.reporter=json-summary` (copy `coverage/coverage-summary.json` to `$R`) |
| Jest | `JEST_JUNIT_OUTPUT_FILE=$R/junit.xml npx jest --reporters=default --reporters=jest-junit --coverage --coverageReporters=json-summary` |
| JUnit with Maven Surefire | `mvn test`, then pass each `target/surefire-reports/TEST-*.xml` to `--junit` |
| Go | `gotestsum --junitfile $R/junit.xml ./...` |

Coverage must be coverage.py JSON (`coverage json`) or istanbul `coverage-summary.json`. Without either, leave out `--coverage` and say so in the summary.

Third, write `$R/report.json` with the sections listed below.

Fourth, run the script.

```
python3 .claude/skills/art-of-unit-testing/scripts/build_report.py $R/report.json \
  [--junit $R/junit.xml ...] [--coverage $R/coverage.json] [--root .] \
  [--out DIR] [--formats html,pdf,summary] [--validate-only]
```

`uv run` works in place of `python3`. Outputs go next to `report.json` unless you pass `--out`. The script exits 0 on success and 1 with a list of validation errors, which you fix before you run it again. It exits 2 when you asked for `pdf` and it found no Chrome. In that case the HTML is still written, and you can set the `CHROME` environment variable to the browser path. `--validate-only` checks the inputs without writing anything.

## Formats

The user chooses the formats with `--formats`, which takes any comma-separated subset of `html`, `pdf` and `summary`. The default is `html,pdf`.

| Format | File | Use |
|---|---|---|
| `html` | `report.html` | the full report in a browser |
| `pdf` | `report.pdf` | the same page printed by headless Chrome, for an attachment or an archive |
| `summary` | `summary.html` | an email body with the title, meta line, verdict and counts, and the line "The full report is attached as report.pdf." |

The script copies the JUnit XML and coverage JSON you pass into the output folder as `junit.xml` (or `junit-1.xml`, `junit-2.xml`) and `coverage.json`, so the folder is complete. The script never writes JUnit XML itself.

## report.json

The top-level fields are `title`, `skill` (`"art-of-unit-testing"`), `meta` (date, branch, commit, command, tools), `summary` (HTML), `verdict` (`status` is `pass`, `conditional` or `fail`, plus one or two sentences of `text`), `sections`, `tests` and `defects`. Each section has a `heading` and any of `text`, `table` (`columns`, `rows`, `numeric`), `callout` (`tone` is `pass`, `warn`, `fail` or `info`) and `after`. Strings in `summary`, `text`, `after` and table cells are HTML that you write, so escape any code you quote.

Each entry in `tests` is `{ "id", "test", "location", "covers" }`. Each entry in `defects` is `{ "id", "test", "location", "severity", "expected", "actual", "analysis" }`. The script validates the following.

- Every `location` is `file:line`, the file exists under `--root`, and that line or one of the 3 lines after it contains the test name or the ID.
- With `--junit`, every `test` matches exactly one JUnit test case, and every failing or erroring JUnit case appears in `defects`.

A test that fails because the production code has a defect stays failing and goes into `defects`. Never change the expected value to make it pass.

## Sections for review mode

Use these headings, in this order, when the user asked you to review or clean up existing tests.

1. **Result before and after**: tests, run time, pass count and mutants caught, before and after your changes.
2. **What I deleted**: test, file and reason (the rejection list item or the pillar at 0).
3. **What I split**: tests with several exit points or several Act lines, and the tests that replaced them.
4. **What I added**: new tests, with the FR or the gap each one closes.
5. **Mutants**: each mutation you made in SKILL.md step 6, and the test that went red or "survived".
6. **What I left alone**: tests you kept unchanged, and why.
7. **Out of scope and design notes**: behavior that needs integration or e2e tests, multi-line Act, private logic you could not reach, and fat controllers.
8. **Verdict**: repeats `verdict` with the reason.

## Sections for new tests mode

Use these headings when you wrote tests for new or untested code.

1. **Requirements and triage**: the FRs with their source and risk level, and the step 2 triage of each unit.
2. **Tests added, changed and deleted**: one row per test, with the FR, the exit point and the technique from `test-design.md`.
3. **Red check**: for each test, how you saw it fail (TDD red or a mutation).
4. **Assumptions**: each assumed requirement and the tests that depend on it.
5. **Out of scope and design notes**: same as review mode.
6. **Verdict**: same as review mode.

The script adds **Test run** (totals and a per-suite table) and **Failures** from the JUnit XML, **Coverage** from the coverage JSON, and **Traceability** from `tests` joined with the JUnit status. Don't write those sections yourself.

## Example report.json for review mode

```json
{
  "title": "Unit test review of parcel-rates",
  "skill": "art-of-unit-testing",
  "meta": { "date": "2026-10-24", "branch": "main", "commit": "406f877", "command": "pytest -q", "tools": "pytest 8.3, Python 3.12" },
  "summary": "<p>I deleted 9 of 31 tests and added 3. The suite now catches 11 of 12 mutants, up from 5.</p>",
  "verdict": { "status": "conditional", "text": "The rate rules are covered. The weight rounding mutant survives until FR-4 says how to round." },
  "sections": [
    {
      "heading": "Result before and after",
      "table": { "columns": ["Measure", "Before", "After"], "rows": [["Tests", "31", "25"], ["Mutants caught", "5 of 12", "11 of 12"], ["Run time (s)", "4.1", "0.6"]], "numeric": [1, 2] }
    },
    {
      "heading": "What I deleted",
      "table": { "columns": ["Test", "File", "Why"], "rows": [["<code>test_rate_init</code>", "tests/test_rates.py", "Constructor test, on the rejection list"]], "numeric": [] }
    },
    {
      "heading": "Mutants",
      "table": { "columns": ["Mutation", "Line", "Result"], "rows": [["<code>&lt;=</code> to <code>&lt;</code>", "rates.py:22", "red: test_parcel_at_5_kg_uses_base_rate"], ["round() removed", "rates.py:40", "survived"]], "numeric": [] },
      "callout": { "tone": "warn", "text": "The rounding mutant survives because FR-4 does not say how to round." }
    }
  ],
  "tests": [
    { "id": "FR-1", "test": "test_parcel_at_5_kg_uses_base_rate", "location": "tests/test_rates.py:14", "covers": "Parcels up to 5 kg pay the base rate" }
  ]
}
```

## CI and email

The user picks the formats with `--formats` and picks the attachments in the mail step. Upload the whole report folder as the CI artifact, so it holds `report.html`, `report.pdf`, `summary.html`, `junit.xml` and `coverage.json`. The email uses `summary.html` as the body and attaches `report.pdf` and `junit.xml`.

```yaml
- run: python3 .claude/skills/art-of-unit-testing/scripts/build_report.py test-reports/latest/report.json --junit test-reports/latest/junit.xml --formats html,pdf,summary
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

Where the pipeline runs this step is covered by art-of-cicd.
