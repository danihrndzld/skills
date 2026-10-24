# Stability

A flaky test fails inconsistently, with the same code and what looks like the same conditions. Treat each flake as a bug to investigate. Rerunning until green turns real information into noise, and the team learns to ignore red builds. In one documented case, a retry wrapped around a whole test hid a billing defect that charged wrong amounts, and the defect caused a production outage. The safe fix retries only the isolated nondeterministic call, never the assertions or the business logic around them.

## Causes and fixes

| Cause | Symptom | Fix |
|---|---|---|
| Fixed sleeps or missing waits | Fails on slow CI, passes locally | Wait on a condition, e.g., element visible, response received, URL changed. Use auto-waiting assertions. |
| Brittle selectors | Fails after a style or layout change | Locate by role and name, label, or test ID |
| Shared test data | Fails when run in parallel or in another order | Create unique data per test through the API, and clean it up |
| Leftover state | First run passes, second fails | Fresh browser context per test. Reset or delete data the test created. |
| Animations and transitions | Click lands on a moving element | Disable animations in the test environment, or wait for the element to be stable (Playwright does this by default) |
| Third-party services | Timeouts, rate limits, changed sandbox data | Stub at the network level, or use the vendor sandbox with fixed accounts. Never call production services. |
| Time and locale | Fails at midnight, at month end, or on a runner in another time zone | Fix the clock, time zone, and locale in the browser context and the server |
| Asynchronous back end | Outcome appears after the assertion timed out | Wait for the specific response or the visible outcome with a deadline that matches the service level |
| Test order dependency | Passes in the full suite, fails alone | Every test creates its own preconditions |
| Resource limits | Random failures with many workers | Lower the worker count, or give the app under test more resources |
| Real defect (race condition in the app) | Rare failure in the same step | Report it as a defect. Don't make the test tolerate it. |

## Waits

- Never use fixed waits such as `sleep(2)`, `page.waitForTimeout(2000)`, `cy.wait(2000)`, or `Thread.sleep(2000)`.
- Prefer assertions that retry until a timeout, e.g., Playwright `await expect(locator).toHaveText(...)`, Cypress `cy.contains(...).should('be.visible')`, Selenium `WebDriverWait(driver, 10).until(...)`.
- Wait for a network response when the visible change follows it, e.g., Playwright `page.waitForResponse('**/api/orders')` or Cypress `cy.intercept(...).as('order')` with `cy.wait('@order')`.
- Don't use the implicit and explicit waits of Selenium together. Pick explicit waits.
- Keep the default assertion timeout short (5 seconds) and raise it only for the one step that is known to be slow, with a comment that names the reason.

## Selectors

Priority order:

1. Role and accessible name, e.g., `getByRole('button', { name: 'Pay now' })`. The test then reads like the user's view and checks accessibility for free.
2. Label or placeholder text for form fields, e.g., `getByLabel('Email')`.
3. Visible text for static content.
4. A dedicated test ID such as `data-testid="order-number"`, when the element has no role or stable text.

Avoid CSS classes, generated IDs, `nth-child`, and absolute XPath, because a style change or a new wrapper breaks them while behavior stays the same.

## Page objects, kept thin

A page object holds the locators of one page or component and exposes user actions in domain words, e.g., `checkout.payWithSavedCard()`.

- No assertions inside page objects. The test asserts.
- No branching or business rules. A method does one user action.
- Return the next page object from actions that navigate, so the test reads in journey order.
- Prefer components (header, cart drawer) over one huge class per page.
- When a page object grows past about 15 methods, split it by component.

## Test data

- Create data through the public or admin API, or a seed script, before the UI steps. Building state through the UI is slow and couples the test to unrelated screens.
- Use unique values per test (e.g., `ana+<run id>@example.test`) so parallel workers don't collide.
- Delete the created data in teardown, or run each pipeline against a fresh environment or database snapshot.
- Use the payment provider's sandbox cards and a test inbox service for emails. Never use real customer data.
- Log in once per worker through the API and save the session (Playwright `storageState`, Cypress `cy.session`).

## Parallelism and sharding

- Tests can run in parallel only when they don't depend on each other, don't need a specific order, and don't share mutable state.
- Parallel workers split tests across CPU cores on one machine. Sharding splits them across machines, e.g., Playwright `--shard=1/4`.
- Sizing example: 50 browser tests at 2.5 minutes each take 125 minutes in one worker. A 25 minute target needs 5 shards, and 7 leave margin.
- Parallelism and sharding trade hardware for time. They don't make a test more trustworthy.

## Evidence on failure

Configure the runner to keep evidence only when a test fails or is retried, so passing runs stay fast and artifacts stay small.

| Runner | Config |
|---|---|
| Playwright | `use: { trace: 'on-first-retry', screenshot: 'only-on-failure', video: 'retain-on-failure' }`. Output in `test-results/`. Open traces with `npx playwright show-trace`. |
| Cypress | `screenshotOnRunFailure: true` (default), `video: true` in config. Output in `cypress/screenshots/` and `cypress/videos/`. |
| Selenium | Take a screenshot and save the page source in the test runner's failure hook (pytest `pytest_runtest_makereport`, JUnit 5 `TestWatcher`, Mocha `afterEach` with `this.currentTest.state`) |
| Appium | Same as Selenium, plus the device log and the Appium server log |

Upload the evidence folders as CI artifacts with `if: always()`.

## Flaky test policy

1. When a test fails and then passes on retry, mark it flaky in the report with the run link.
2. Move a test that flaked twice into a quarantine job that doesn't block merges, as `art-of-cicd` describes, and open a ticket with the suspected cause from the table above.
3. Fix or delete a quarantined test within a set time, e.g., two weeks. A quarantine with no deadline is a place where tests are forgotten.
4. Track the flake rate per test from JUnit history. A suite whose failures people trust is the goal, not a green dashboard.
