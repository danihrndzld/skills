---
name: art-of-integration-testing
description: Use when writing, reviewing, or deleting integration tests or API tests in any language, when testing controllers, application services, or repositories against a real database, when setting up Testcontainers or an in-memory test server, when writing contract tests between services, or when testing that a use case publishes a message, sends an email, or calls a third-party API. Produces a few tests per orchestration that run real managed dependencies, double only unmanaged ones, and assert several exit points in one test.
---

# The art of integration testing (language-agnostic)

An integration test earns its place when it fails because two real parts stopped working together, e.g., a query that no longer matches the schema, a transaction that commits half the rows, or an endpoint that maps the wrong status code. Unit tests can't see those failures, and an end-to-end test sees them too late and too slowly. Any integration test that only exercises domain logic belongs one level down.

The value formula is the same as for unit tests, `Value = Protection x Resistance to refactoring x Speed x Maintainability`. Integration tests buy more protection, because they run more real code, and they pay for it with speed. Keep the count low, because each integration test adds seconds to every pipeline run.

## Foundations (for readers who installed only this skill)

- The pyramid has many unit tests on the domain, fewer integration tests on orchestration, and a minimal number of end-to-end tests on critical journeys.
- An entry point is what the test calls. At this level it is a controller action, an application service method, or an HTTP endpoint.
- An exit point is what the test asserts. At this level it can be the response, the database state, and an outgoing message, all in one test.
- A managed dependency is out of process and only your application touches it (your own database). Run it for real. An unmanaged dependency is shared or external (message bus, email, third-party API). Replace it with a mock.
- Expected values come from the spec, the ticket, or the user, never from reading the code under test.

Test design techniques (equivalence partitioning, boundary values, decision tables, state transitions) and the rules for naming, AAA, and zero logic in tests live in `art-of-unit-testing`. Pipeline placement, time budgets per stage, and flaky test quarantine live in `art-of-cicd`. Details for this skill are in `references/boundaries-and-doubles.md`, `references/frameworks.md`, and `references/report.md`.

## Workflow (follow in order)

### 1. Read before writing
- Find the project's test runner, its integration test folder or marker, its fixtures, and how it starts the database today. Read 1 to 3 existing integration tests and match them. Don't add a second container library or HTTP test client if one exists.
- Read the controller or service, its callers, and the ticket or spec. Write one line per functional requirement (FR) with its source, as in `art-of-unit-testing`. Mark assumed requirements as assumptions.

### 2. Pick what gets an integration test
- Give each orchestration (controller, application service, message handler, scheduled job) one happy path test that goes through every real managed dependency it uses.
- Add edge cases only when a unit test can't reach them, e.g., a unique constraint violation, a rollback after a failed second write, an optimistic lock conflict, a 404 mapped from an empty query, or a 401 from the auth middleware.
- Push every business rule variation down to unit tests on the domain. If the rule lives in the controller, propose extracting it.
- Write the result as `orchestration -> happy path + edge cases (why a unit test can't reach each one)`.

### 3. Map the boundary
For each orchestration, list each dependency and its treatment.

| Dependency | Example | Treatment |
|---|---|---|
| Managed, out of process | your own database, your own cache, your own file store | Real instance, in a container or in process |
| Unmanaged, out of process | message bus, email or SMS provider, payment API, another team's service | Mock or fake at your adapter, and assert the outgoing call |
| Incoming nondeterminism | clock, random IDs, feature flags | Stub with fixed values |
| In process | domain classes, mappers, validators | Real code, never doubled |

Use the same database engine and version as production. An in-memory substitute with a different SQL dialect hides the defects you are paying to find. Details and exceptions are in `references/boundaries-and-doubles.md`.

### 4. Write each test
- Arrange: insert the rows the scenario needs through the application's own repositories or a small builder, with every value that affects the outcome visible in the test. Configure the mock for the unmanaged dependency.
- Act: one call to the entry point, e.g., `POST /orders` or `service.place(cmd)`.
- Assert every exit point of that one scenario. For an HTTP endpoint, check the status code and the response body, then read the database through a fresh connection or repository to check what was written, then check the outgoing message and its payload on the mock. Assert values, never only `is not None`.
- Name the test after the behavior, e.g., `placing an order saves it and publishes OrderPlaced`.

### 5. Keep it deterministic
- Reset data between tests. Prefer a transaction per test that rolls back, or truncate the touched tables before each test. Never let one test depend on rows another test wrote.
- Give each test its own IDs and unique keys so tests can run in parallel against one database.
- Never sleep. For asynchronous work (a consumer, an outbox relay), poll for the condition with a timeout, e.g., "row status is SENT within 5 seconds".
- Fix the clock, random seeds, time zone, and locale.
- Retry only the isolated nondeterministic step, e.g., the container health check or the first connection. Never wrap the whole test or its assertions in a retry, because a retry around assertions hides real defects.

### 6. Keep it fast
- Start the database container once per test run or per worker, not once per test. Run migrations once.
- Target under 5 minutes for the whole integration stage. When it grows past that, delete integration tests whose cases a unit test now covers before you add hardware.
- Mark or folder integration tests so the pipeline can run unit tests first.

### 7. Verify the signal (mandatory)
1. Run the new tests and the whole integration suite. Report the exact command and the result.
2. See each test fail for the right reason. Temporarily remove the production line it protects, e.g., the `repository.save`, the `bus.publish`, the transaction boundary, or the status mapping. The test must go red with a readable message. Restore the code. A test that stays green is rewritten or deleted.
3. Run the suite twice in a row and once in random order or in parallel. Any test whose result changes is a determinism bug to fix before you hand over.

### 8. Report
Return exactly this block, with facts only.

```
FRs:          FR-1 to FR-n (source: ticket | spec | docs | assumed)
Boundary:     real: <db engine version, how started>; doubled: <bus, email, api> at <adapter>
Tests:        <n> added, <n> changed, <n> deleted (reason per deletion)
Traceability: FR-1 -> test_a (exits: 201 body, orders row, OrderPlaced msg); FR-4 -> GAP (<why>)
Red seen:     test_a: removed bus.publish -> red; test_b: dropped unique index -> red
Determinism:  reset by <rollback | truncate>; 2 runs + parallel run identical: yes | no
Run:          <command> -> <passed>/<total>, <duration>
Assumptions:  <each assumed requirement, one line>
Pushed down:  <cases that belong in unit tests>
Out of scope: <journeys that need e2e tests>
```

### 9. Report on request
When the user asks for a test report, a PDF, a CI artifact, or an email summary, follow `references/report.md`. It explains which JUnit flag to pass, what goes into `report.json`, and how `scripts/build_report.py` builds HTML, PDF, and an email summary.

## Rejection list (never generate, delete in reviews)
- Integration tests that cover business rule variations a unit test on the domain could cover.
- Mocks of your own database, ORM, or repository in a test that calls itself an integration test.
- Real calls to a third-party API, a shared message broker, or a real mailbox from the test suite.
- An in-memory database with a different engine than production, used to test queries, constraints, or transactions.
- Tests that assert only the HTTP status, when the endpoint also writes data or sends a message.
- Assertions on stubs, on SQL text, on the number of queries, or on internal call order.
- Tests that share rows, depend on run order, or need a manually seeded database.
- `sleep`, fixed waits, or a retry around the whole test.
- Several Act steps in one test. A multi-step flow across endpoints is an e2e journey, see `art-of-e2e-testing`.
- Tests that mirror the controller line by line with one mock per collaborator.

## Reviewing existing integration tests
Score each test from 0 to 3 on the four pillars, and flag every rejection list hit with `file:line`. Delete any test whose cases are all reachable in process, and replace it with unit tests through `art-of-unit-testing`. When five integration tests circle one method, keep one that proves the wiring and move the case variations into unit tests. Flag flaky tests for quarantine as `art-of-cicd` describes, and report the cause you suspect.

## Scope reminder
Unit tests check one exit point in memory. Integration tests check one scenario of one orchestration through real managed dependencies and may assert several exit points. End-to-end tests drive the deployed system from the outside for a few critical journeys, see `art-of-e2e-testing`.
