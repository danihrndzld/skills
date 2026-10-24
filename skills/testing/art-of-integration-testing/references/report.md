# Test report (on request)

Build a report only when the user asks for one, e.g., "give me a report", "a PDF", "something for CI", or "email the results". The tests and the step 8 block in `SKILL.md` come first. The report adds a document for people who won't read the code.

You write one file, `report.json`. The script `scripts/build_report.py` reads it together with the JUnit XML from the test runner, validates both, and writes the outputs. Counts, pass and fail results, and durations come from the JUnit XML, so never type them by hand.

## Steps

1. Create the folder `test-reports/YYYY-MM-DD-<subject>/` in the tested project, e.g., `test-reports/2026-10-24-orders-api/`. Call it `$R` below.
2. Run the integration suite with JUnit XML output into `$R`:

   | Runner | Command |
   |---|---|
   | pytest | `pytest -m integration --junitxml=$R/junit.xml` |
   | Vitest | `npx vitest run --config vitest.integration.config.ts --reporter=junit --outputFile=$R/junit.xml` |
   | Jest | `JEST_JUNIT_OUTPUT_FILE=$R/junit.xml npx jest --reporters=default --reporters=jest-junit` |
   | Maven | `mvn verify`, then copy `target/failsafe-reports/*.xml` (or `surefire-reports`) to `$R` |
   | Gradle | `gradle integrationTest`, then copy `build/test-results/integrationTest/*.xml` |
   | dotnet | `dotnet test --filter Category=Integration --logger "junit;LogFilePath=$R/junit.xml"` |
   | Go | `gotestsum --junitfile $R/junit.xml -- -tags=integration ./...` |

3. Write `$R/report.json` with the sections below.
4. Build the outputs:

   ```
   python3 .claude/skills/art-of-integration-testing/scripts/build_report.py $R/report.json \
     --junit $R/junit.xml [--coverage $R/coverage.json] --root . --formats html,pdf
   ```

   Use `uv run` instead of `python3` if the project uses uv. Add `--validate-only` to check `report.json` without rendering. Exit 1 lists validation errors, so fix them and run again. Exit 2 means no Chrome was found. The HTML is still written, and you can set the `CHROME` environment variable to the browser path.

## Formats

The user chooses the outputs with `--formats`, which takes any comma-separated subset of `html`, `pdf`, and `summary`. The default is `html,pdf`.

| Output | File | Use |
|---|---|---|
| html | `report.html` | Reading in a browser, CI artifact |
| pdf | `report.pdf` | Attachment for email or a ticket |
| summary | `summary.html` | Email body with the verdict and counts, inline styles only |

Ask the user which formats they want when they mention CI or email. Otherwise produce the default.

## report.json

```json
{
  "title": "Integration tests for the orders API",
  "skill": "art-of-integration-testing",
  "meta": { "date": "2026-10-24", "branch": "main", "commit": "406f877",
            "command": "pytest -m integration --junitxml=test-reports/2026-10-24-orders-api/junit.xml",
            "tools": "pytest 8.3, Python 3.12, PostgreSQL 16 (Testcontainers)" },
  "summary": "<p>Facts with numbers.</p>",
  "verdict": { "status": "pass | conditional | fail", "text": "One or two sentences." },
  "sections": [ { "heading": "...", "text": "<p>...</p>", "table": { "columns": [], "rows": [] } } ],
  "tests": [ { "id": "FR-1", "test": "test_placing_an_order_saves_it_and_publishes_order_placed",
               "location": "tests/integration/test_orders_api.py:31", "covers": "A placed order is stored" } ],
  "defects": [ { "id": "D-1", "test": "test_duplicate_order_returns_409", "location": "tests/integration/test_orders_api.py:58",
                 "severity": "high", "expected": "409 and no second row", "actual": "500 and no row", "analysis": "..." } ]
}
```

- `skill` is the folder name, `art-of-integration-testing`.
- `tests[]` has one row per FR. A test that asserts several exit points often covers several FRs, so repeat the same `test` and `location` on one row per FR.
- `tests[].test` must match exactly one JUnit case by `name` or `classname.name`. Copy the `name` attribute from the JUnit XML when the runner adds class or describe prefixes.
- `location` is `file:line`, and that line or the 3 lines after it must contain the test name or the ID.
- Every failing or erroring JUnit case must appear in `defects[]`. A test that fails because the code is wrong stays failing and is reported as a defect. Never change the expected value to make it pass.
- Severity: high is a wrong result for money, data, security, or a business rule with no workaround. Medium is a wrong result with a workaround or in a rare case. Low is a message, format, or cosmetic problem.

## Sections to write (in `sections[]`, in this order)

The script adds Test run, Failures, Coverage, and Traceability from the JUnit XML, the coverage file, and `tests[]`. Don't repeat them.

1. Scope and boundaries. The orchestrations under test with their entry points. A table with columns Dependency, Kind (managed or unmanaged), Treatment (real or doubled), and How (e.g., "PostgreSQL 16 container, one per run" or "mock of `EventPublisher`").
2. Test base and oracle. Where each expected value came from (ticket, spec, OpenAPI file, user). List assumptions as A1, A2, with the tests that depend on each.
3. Risk table. Columns Condition, Risk, Likelihood (1 to 3), Impact (1 to 3), Level (likelihood times impact), Tests. A level of 6 or more needs an edge case test, not only the happy path.
4. Cases. Columns ID, Entry point, Scenario, Exit points asserted, Location. One row per test.
5. Environment and data. Engine versions, how containers start, the reset strategy, seed data, and the stub servers with the contract or schema each one follows.
6. Defects. One paragraph per entry in `defects[]` that walks from the error to the defect to the observed failure. Write "No defects found in N tests" when there are none.
7. Residual risk. What wasn't tested and why, e.g., the real payment provider, broker redelivery, or load. Name the next test with its level.
8. Verdict. Release, release with conditions, or don't release, with the numeric threshold behind it. Put the same decision in `verdict`.

Write in the past tense, with a number, an ID, or a `file:line` in each sentence.

## CI and email

The user picks the formats with `--formats` and the attachments in the mail step. Upload the whole report folder as the CI artifact. Send `summary.html` as the email body and attach `report.pdf` and `junit.xml`.

```yaml
- run: python3 .claude/skills/art-of-integration-testing/scripts/build_report.py test-reports/latest/report.json --junit test-reports/latest/junit.xml --formats html,pdf,summary
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

In CI, the JUnit step must write to `test-reports/latest/junit.xml`, and `report.json` must already be in that folder, either committed or written by an earlier step.
