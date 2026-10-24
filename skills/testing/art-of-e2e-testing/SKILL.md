---
name: art-of-e2e-testing
description: Use when writing, reviewing, or deleting end-to-end tests, UI tests, or browser tests in any stack, when working with Playwright, Cypress, Selenium/WebDriver, or Appium, when choosing which user journeys to automate, when writing acceptance tests in Given/When/Then form, or when fixing flaky browser tests. Produces a small set of stable journey tests that drive the deployed system from its outermost edge and assert what the user can see.
---

# The art of end-to-end testing (language-agnostic)

An end-to-end test earns its place when it fails because a real user can no longer finish a journey that the business depends on, e.g., sign up, pay, or submit a claim, and no lower level test could have caught the cause. End-to-end tests are the slowest and most expensive tests to run and to keep green, so every one of them must cover a journey whose failure would stop a release.

The value formula is `Value = Protection x Resistance to refactoring x Speed x Maintainability`. End-to-end tests give the most protection per test and the least speed. A flaky end-to-end test has zero value, because the team stops believing its failures.

## Foundations (for readers who installed only this skill)

- The pyramid has many unit tests on the domain, fewer integration tests on orchestration, and a minimal number of end-to-end tests on critical journeys. Keep that shape.
- An entry point at this level is a user action, e.g., a click, a form submit, or a request to the public API of the whole deployed system.
- An exit point at this level is what the user can observe, e.g., text on the page, a URL, a downloaded file, or an email in a test inbox.
- One test may contain several sequential steps, because a journey is a sequence. Each step still has a visible check before the next one starts.
- Expected outcomes come from acceptance criteria, the spec, or the user, never from what the app shows today.

Test design techniques and naming rules live in `art-of-unit-testing`. Integration and API tests with real databases live in `art-of-integration-testing`. Pipeline placement, sharding, and flaky test quarantine live in `art-of-cicd`. Details for this skill are in `references/journeys-and-scenarios.md`, `references/stability.md`, `references/frameworks.md`, and `references/report.md`.

## Workflow (follow in order)

### 1. Read before writing
- Find the project's e2e runner, its config (base URL, browsers, retries, trace settings), its page objects or helpers, and how it seeds test data. Read 1 to 3 existing e2e tests and match them. Don't add a second browser automation tool.
- Read the acceptance criteria, the ticket, and the user flow. Write one line per journey with its source and the business risk if it breaks.

### 2. Pick the journeys
- List candidate journeys and score each by likelihood of failure and business impact, from 1 to 3 each. Automate only journeys with a score of 6 or more, plus a smoke set of at most 5 checks that runs in under 3 minutes.
- For each journey, ask whether an integration or API test can observe the same outcome. If it can, write that test instead and leave the journey out.
- Cover variations of a rule (every invalid input, every discount tier) with unit tests. An end-to-end test checks that the rule shows up in the flow once.
- Write the result as `journey -> risk score -> steps -> visible outcome`. See `references/journeys-and-scenarios.md`.

### 3. Write each journey test
- Write it as Given, When, Then, in code or in a feature file if the project uses one. Given is the starting state, created through the API or the database, not through the UI. When is the user actions. Then is the visible outcome.
- Log in once per worker through the API and reuse the saved session, except in the one test that covers the login journey itself.
- Locate elements by role and accessible name, then by label, then by a dedicated test ID such as `data-testid`. Never by CSS classes, generated IDs, or XPath positions.
- After each step that changes the screen, assert the visible result before the next step, e.g., the heading "Order confirmed" and the order number.
- Keep page objects thin. They hold locators and user actions, and they never hold assertions or business logic.
- Name the test after the journey, e.g., `customer pays for a cart with a saved card`.

### 4. Keep it deterministic
- Create the test data each test needs through an API or seed script, with unique values per test. Reset or delete it afterwards, or run against a fresh environment.
- Tests never depend on each other or on run order. Each one passes alone and in parallel.
- Never use fixed sleeps. Wait for a condition, e.g., an element is visible, a network response has arrived, or the URL changed. Prefer the runner's auto-waiting assertions.
- Fix the clock, time zone, locale, and feature flags in the test environment. Stub third-party services the team doesn't own at the network level or with their sandbox.
- Retry only the isolated nondeterministic step, e.g., waiting for an email to arrive in the test inbox. Never retry the whole test to make it pass. A runner level retry count above 0 is allowed only to collect evidence, and every test that passed on retry is reported as flaky.

### 5. Keep it fast
- Run tests in parallel workers, and shard across machines when the suite passes the time budget. For example, 50 browser tests at 2.5 minutes each need 5 shards to finish in 25 minutes, and 7 shards leave margin.
- Skip UI steps that aren't under test. Create the cart through the API when the test is about payment.
- Run the smoke set on every deploy and the full journey set before release or on a schedule, as `art-of-cicd` describes.
- Record a trace, a screenshot, and a video only on failure or on the first retry.

### 6. Verify the signal (mandatory)
1. Run each new test alone, then the whole suite in parallel. Report the exact command, the browsers, and the result.
2. See each new test fail for the right reason at least once. Change the expected text, or disable the step that produces the outcome, and confirm the failure message names the missing outcome. Restore it.
3. Run each new test at least 5 times in a row, e.g., with `--repeat-each=5` or a loop in CI. Any failure is a stability bug to fix before hand over. See `references/stability.md`.

### 7. Report
Return exactly this block, with facts only.

```
Journeys:     J-1 <name> (risk 9, source: AC-3) ... J-n
Not e2e:      <journeys or checks moved to integration or unit tests, and why>
Tests:        <n> added, <n> changed, <n> deleted (reason per deletion)
Traceability: J-1 -> test_a (outcomes: "Order confirmed", order number, receipt email)
Red seen:     test_a: expected "Order confirmed" changed -> red
Stability:    5 repeats each: <n>/<n> green; retries used: <n>; flaky: <list or none>
Run:          <command> -> <passed>/<total>, <duration>, <workers or shards>, <browsers>
Data:         <how test data is created and cleaned up>
Not covered:  <journeys left out and why>
```

### 8. Report on request
When the user asks for a test report, a PDF, a CI artifact, or an email summary, follow `references/report.md`. It explains the runner's JUnit flag, what goes into `report.json`, how `scripts/build_report.py` builds HTML, PDF, and an email summary, and how to attach traces and screenshots of failures.

## Rejection list (never generate, delete in reviews)
- Journeys whose outcome an integration or API test can observe.
- Tests for each validation message, each field, or each rule variation through the UI.
- `sleep`, `waitForTimeout`, `Thread.sleep`, or fixed waits.
- Selectors by CSS class, DOM position, generated ID, or long XPath.
- Tests that log in through the UI before every test.
- Tests that depend on another test's data, on run order, or on data someone created by hand.
- Page objects with assertions, branching, or business rules inside.
- Assertions on internal state (local storage keys, Redux store, database rows) instead of what the user sees. A check of server state is allowed only when the outcome has no visible form.
- A retry decorator around the whole test, or a raised timeout as the fix for a flake.
- Pixel-perfect screenshot comparisons as the only assertion of a journey.
- Real payments, real emails to real people, or calls to production third-party APIs.

## Reviewing existing e2e tests
Score each test from 0 to 3 on the four pillars, and flag every rejection list hit with `file:line`. Demote any journey whose outcome the API or the database can show to an integration test, and point to `art-of-integration-testing`. When an e2e test covers logic that a unit test covers, delete the e2e test. Check run history for flakes, send flaky tests to quarantine as `art-of-cicd` describes, and name the probable cause from `references/stability.md`. Prefer deleting tests over adding them.

## Scope reminder
Unit tests check one exit point in memory. Integration tests check one orchestration through real managed dependencies. End-to-end tests check a few critical journeys from the outside, through the deployed system, and assert what the user sees.
