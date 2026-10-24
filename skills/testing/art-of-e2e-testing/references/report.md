# Test report (on request)

Build a report only when the user asks for one, e.g., "give me a report", "a PDF", "something for CI", or "email the results". The tests and the step 7 block in `SKILL.md` come first. The report adds a document for people who won't read the code.

You write one file, `report.json`. The script `scripts/build_report.py` reads it together with the JUnit XML from the test runner, validates both, and writes the outputs. Counts, pass and fail results, and durations come from the JUnit XML, so never type them by hand.

## Steps

1. Create the folder `test-reports/YYYY-MM-DD-<subject>/` in the tested project, e.g., `test-reports/2026-10-24-checkout/`. Call it `$R` below.
2. Run the e2e suite with JUnit XML output into `$R`:

   | Runner | Command |
   |---|---|
   | Playwright (JS/TS) | `PLAYWRIGHT_JUNIT_OUTPUT_NAME=$R/junit.xml npx playwright test --reporter=junit` |
   | Playwright (Python), Selenium or Appium with pytest | `pytest tests/e2e --junitxml=$R/junit.xml` |
   | Cypress | `npx cypress run --reporter junit --reporter-options "mochaFile=$R/junit-[hash].xml"` |
   | Selenium or Appium with JUnit 5 | `mvn verify`, then copy `target/surefire-reports/*.xml` to `$R` |
   | WebdriverIO | `@wdio/junit-reporter` with `outputDir: '$R'` in `wdio.conf` |

   Keep a retry count of 0 for the reported run, or report every test that passed on retry as flaky in the Stability section.
3. Write `$R/report.json` with the sections below.
4. Build the outputs:

   ```
   python3 .claude/skills/art-of-e2e-testing/scripts/build_report.py $R/report.json \
     --junit $R/junit.xml --root . --formats html,pdf
   ```

   Pass one `--junit` flag per file when the runner writes several (Cypress, shards). Use `uv run` instead of `python3` if the project uses uv. Add `--validate-only` to check `report.json` without rendering. Exit 1 lists validation errors, so fix them and run again. Exit 2 means no Chrome was found. The HTML is still written, and you can set the `CHROME` environment variable to the browser path.

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
  "title": "End-to-end tests for checkout",
  "skill": "art-of-e2e-testing",
  "meta": { "date": "2026-10-24", "branch": "main", "commit": "406f877",
            "command": "npx playwright test --reporter=junit",
            "tools": "Playwright 1.48, Chromium 130, Firefox 131, staging build 2026.10.24-3" },
  "summary": "<p>Facts with numbers.</p>",
  "verdict": { "status": "pass | conditional | fail", "text": "One or two sentences." },
  "sections": [ { "heading": "...", "text": "<p>...</p>", "table": { "columns": [], "rows": [] } } ],
  "tests": [ { "id": "J-1", "test": "checkout > customer pays for a cart with a saved card",
               "location": "e2e/checkout.spec.ts:18", "covers": "Returning customer pays with a saved card (AC-3)" } ],
  "defects": [ { "id": "D-1", "test": "checkout > declined card keeps the cart", "location": "e2e/checkout.spec.ts:44",
                 "severity": "high", "expected": "Cart still holds 3 items", "actual": "Cart is empty", "analysis": "..." } ]
}
```

- `skill` is the folder name, `art-of-e2e-testing`.
- `tests[]` has one row per journey or acceptance criterion. Use journey IDs (`J-1`) or acceptance criterion IDs (`AC-3`).
- `tests[].test` must match exactly one JUnit case by `name` or `classname.name`. Playwright and Cypress build the name from the describe titles and the test title, so copy the `name` attribute from the JUnit XML, not the string in the `test()` call.
- `location` is `file:line`, and that line or the 3 lines after it must contain the test name or the ID. Put the journey ID in the test title, e.g., `test('J-1 customer pays with a saved card', ...)`, when the title and the JUnit name differ.
- Every failing or erroring JUnit case must appear in `defects[]`. A test that fails because the app is wrong stays failing and is reported as a defect. Never change the expected outcome to make it pass. A failure caused by the test or the environment is fixed, not reported as a product defect.
- Severity: high is a journey the user can't finish, or a wrong result for money, data, or security, with no workaround. Medium is a wrong result with a workaround or in a rare case. Low is a message, layout, or cosmetic problem.

## Sections to write (in `sections[]`, in this order)

The script adds Test run, Failures, Coverage, and Traceability from the JUnit XML and `tests[]`. Don't repeat them.

1. Journeys covered and why. A table with columns Journey, Source (ticket or acceptance criterion), Likelihood (1 to 3), Impact (1 to 3), Level, Decision (e2e, integration, unit). Include the journeys that were moved to a lower level.
2. Flow table. For each journey, the steps in order with the visible check after each step, e.g., "Pay with saved card -> heading 'Order confirmed' and order number".
3. Cases. Columns ID, Journey, Given, When, Then, Location. One row per test.
4. Environment and test data. Base URL, build or commit deployed, browsers and versions, viewports, stubbed third-party services, how data is created and cleaned up.
5. Stability. Repeats per new test and results, retries used in the reported run, tests that passed on retry, and tests in quarantine with their tickets.
6. Run time and parallelism. Total duration, workers, shards, and the slowest 3 tests with their durations.
7. Defects. One paragraph per entry in `defects[]` that walks from the error to the defect to the observed failure, with the name of the trace or screenshot file. Write "No defects found in N tests" when there are none.
8. Not covered. Journeys left out and why, browsers or devices not run, and checks left to manual testing (e.g., the screen reader checklist). Name the next test with its level.
9. Verdict. Release, release with conditions, or don't release, with the numeric threshold behind it, e.g., "all risk 6 to 9 journeys pass in 2 browsers and no test passed only on retry". Put the same decision in `verdict`.

Write in the past tense, with a number, an ID, or a `file:line` in each sentence.

## CI and email

The user picks the formats with `--formats` and the attachments in the mail step. Upload the whole report folder as the CI artifact, and add the runner's failure evidence folders to the same artifact: Playwright `test-results/` (traces, screenshots, videos), Cypress `cypress/screenshots/` and `cypress/videos/`. Send `summary.html` as the email body and attach `report.pdf` and `junit.xml`. Don't attach traces or videos to email, because they are large. The email can point to the CI run instead.

```yaml
- run: python3 .claude/skills/art-of-e2e-testing/scripts/build_report.py test-reports/latest/report.json --junit test-reports/latest/junit.xml --formats html,pdf,summary
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-report
    path: |
      test-reports/latest/
      test-results/
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

In CI, the JUnit step must write to `test-reports/latest/junit.xml`, and `report.json` must already be in that folder, either committed or written by an earlier step. Replace `test-results/` with `cypress/screenshots/` and `cypress/videos/` for Cypress.
