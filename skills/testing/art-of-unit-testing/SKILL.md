---
name: art-of-unit-testing
description: Use when writing, generating, reviewing, or deleting unit tests, or doing TDD, in any programming language (Python, JS/TS, Java, C#, Go, Rust, Kotlin, Swift, PHP, Ruby, COBOL, etc.), when asked for "unit tests", "tests for this function/class", "increase coverage", or when judging whether existing tests are noise. Produces few, high-signal tests built from entry and exit points, the four pillars (regression protection, refactoring resistance, fast feedback, maintainability), AAA, classical-school test doubles, and the code-quadrant triage.
---

# The art of unit testing (language-agnostic)

A unit test earns its place only if it fails when behavior breaks and stays green when internals are refactored. Everything else is noise: delete it or don't write it.

`Value = Protection x Resistance to refactoring x Speed x Maintainability`. A zero in any factor makes the test worthless. Resistance to refactoring and maintainability are non-negotiable; the only real trade-off is protection (more real code executed) versus speed.

Framework syntax per language: see `references/frameworks.md`. Good and bad examples: `references/examples.md`. Test design techniques (partitions, boundaries, decision tables, state transitions, risk): `references/test-design.md`. HTML, PDF and email reports: `references/report.md`.

Testing can show that defects are present, and it can't show that they are absent. Exhaustive testing is impossible, so each test is chosen by a technique and by product risk (ISTQB CTFL v4.0.1, §1.3).

## Workflow (follow in order)

### 1. Read before writing
- Find the project's test framework, file locations, naming and helper conventions. Read 1 to 3 existing tests and match their style. Never introduce a new test framework or mocking library if one exists.
- Read the code under test and its callers. Read specs/tickets/docs if present.
- Write the functional requirements (FRs) for the unit, one line each. Sources, in order: ticket/spec/issue, docs/README, callers' expectations, existing behavior (last resort, and say so). Write any assumption next to its FR; never invent requirements.

```
FR-1  An order with a past delivery date is rejected.
FR-2  Orders over Q10,000 require manager approval.
FR-3  A rejected order sends no confirmation email.
```

Every test traces to exactly one FR (FR id in a one-line comment or the test name). An FR without a test is a gap; a test without an FR is a deletion candidate.

### 2. Triage the code (decide what NOT to test)

| | Few collaborators | Many collaborators |
|---|---|---|
| High complexity or domain value | Domain model, algorithms: unit test thoroughly | Overcomplicated: propose a split (Humble Object: pure logic out, orchestration stays thin), then test the extracted logic |
| Low complexity or domain value | Trivial (getters, setters, one-line constructors, DTOs, pass-through): no tests | Controllers, app services, orchestration: not unit tests; recommend 1 integration test for the happy path plus the edge cases the unit tests can't reach |

State the triage result in one line per unit before writing anything. Skipping trivial code is correct, not lazy.

### 3. Map entry and exit points
For each unit of behavior (one class or several working together, starting at a public entry point):

- Entry point: the public function/method/endpoint the test calls. Never a private/protected/internal method. If private logic is too complex to reach through the public API, that is a missing abstraction: extract it to its own unit.
- Exit points (the only things a test may assert):
  1. Return value or thrown error: output-based test (preferred; cheapest and most robust).
  2. Public state change observable via the public API: state-based test.
  3. Outgoing call to an unmanaged out-of-process dependency (email, message bus, third-party API, logger only if logging is a requirement): communication-based test with a mock.

Write the list: `entry -> exit point -> scenarios`. Write one test per exit point per scenario. Scenarios per behavior: happy path, each boundary (both sides), each distinct failure mode. Nothing else.
Derive partitions, boundaries and combinations with `references/test-design.md`, where product risk sets how many scenarios each FR gets.

### 4. Choose test doubles (classical or Detroit school)
- In-process collaborators (other domain classes, value objects, pure helpers): use the real objects. Do not mock them.
- Incoming data from out-of-process (DB read, config, clock, random, HTTP GET): stub it. Never assert on a stub (no "was called", no call counts).
- Outgoing side effects to unmanaged systems: mock it and verify the call and its arguments. Use at most one mock per test.
- Managed out-of-process dependencies (your own DB that only your app touches): leave to integration tests, don't mock in unit tests.
- Mock only at the system edge. Don't mock what you don't own: wrap the vendor SDK in a thin adapter and mock the adapter.
- Non-determinism (time, randomness, UUIDs, env vars, locale, timezone) is injected or stubbed. A unit test that can't pass 1000 times in a row is broken.
- Commands (side effect, no return) go with mocks. Queries (return, no side effect) go with stubs.

### 5. Write each test

Each test has three parts, Arrange, Act and Assert, separated by blank lines.
- Arrange: build the SUT and inputs. Name the system under test `sut`. Put repetitive setup in private factory functions, Test Data Builders or Object Mothers in the test file, with defaults so each test only overrides what matters to it: `make_order(total=10_001)`. Every value that affects the outcome must be visible in the test. Shared `setUp` or `beforeEach` is allowed only for things irrelevant to every assertion (e.g., a stub clock).
- Act: exactly one line, calling the entry point. If you need two calls to perform one behavior, the SUT's API leaks; note it as a design finding.
- Assert: the one exit point for this test. Several asserts are fine only if they check facets of the same outcome (e.g., fields of the returned object). Different exit points need different tests. Never put the Act inside the assert expression.

Name each test with a plain-English statement of the behavior, readable by a domain expert: `delivery with a past date is invalid`, `withdrawal over balance is rejected`. Do not encode method names (`Method_Scenario_Result`): renaming the method must not force renaming the test. No "should", no implementation words (`returns_false`, `calls_repo`). Someone reading only the failure list must know what broke. Follow the project's case convention (snake_case, `it("…")`, `@DisplayName`, etc.).

Keep zero logic in tests: no `if`, `switch`, `for`, `while`, `try/catch` for flow, no string building of expected values, no re-implementing the algorithm to compute the expected result. Expected values are hardcoded literals derived independently (by hand, from the spec, from a domain expert). Use the framework's parametrized tests for input tables and its "expect throws" helper for errors.

```python
assert tax(100) == 100 * TAX_RATE                     # tautology: passes even if the formula is wrong
assert tax(Decimal("100.00")) == Decimal("12.00")     # signal
```

Keep tests fast and isolated: in-memory only, milliseconds; the whole unit suite runs in seconds. No filesystem, network, DB, sleeps, real clocks. Tests must pass alone, in any order, and in parallel; no shared mutable state between tests. A flaky unit test is a bug: fix the nondeterminism, never add retries.

### 6. Verify the signal (mandatory, don't skip)
1. Run the tests. All new tests pass. Report the exact command and result.
2. Red check. Every test must be seen failing for the right reason (an assertion failure, not an import error, typo or missing symbol). A test you never saw fail proves nothing.
   - TDD (new code): Red, then Green, then Refactor. Write one test for one FR, run it, see it fail with the expected message. Write the minimum production code to pass (no speculative branches or params). Refactor with all tests green; tests must not change during a pure refactor.
   - Existing code (mutation check): temporarily break the production line the test protects (flip a condition, change a boundary from `<` to `<=`, change a constant, remove the side effect). The test must go red with a readable failure message. Restore the code. A test that stays green is deleted or rewritten.
3. Refactoring check: ask "if I rewrote the internals with identical behavior (rename private methods, inline a helper, split a class, reorder internal calls), would this test still pass?" If no, it's coupled to implementation: rewrite it.
4. Run the whole suite once to confirm nothing else broke.

### 7. Report
Return exactly this block, facts only (no prose about what tests "ensure" or "validate"):

```
FRs:          FR-1 to FR-n (source: <ticket/spec/docs/assumed>)
Triage:       <unit> -> <domain | trivial | orchestration | overcomplicated> -> <tested | skipped | needs integration test | needs refactor>
Tests:        <n> added, <n> changed, <n> deleted (reason per deletion)
Traceability: FR-1 -> test_a (exit: return), test_b (exit: mock call); FR-3 -> GAP (<why>)
Red seen:     test_a: `>` to `>=` -> red; test_b: removed send() -> red | list exceptions
Run:          <command> -> <passed>/<total>, <duration>
Assumptions:  <each assumed requirement, one line>
Out of scope: <behaviors needing integration/E2E>
Design notes: <multi-line Act, untestable private logic, fat controllers>
```

Don't refactor production code unasked beyond what's needed to inject a dependency, and list it under Design notes when you did.

### 8. Report on request
When the user asks for a report (HTML, PDF, email summary or CI artifacts), write `report.json` and run `scripts/build_report.py` as described in `references/report.md`. Otherwise the step 7 block is the output.

## Rejection list (never generate; delete in reviews)
- Tests that trace to no FR, or that you never saw fail.
- Tests for getters/setters/constructors/DTOs/pass-throughs/framework or library behavior (the ORM saves, the router routes)/constants.
- Tests with no assertion, or whose main assertion is `is not None`, `toBeDefined()`, `toBeTruthy()`, a type check, or "no exception" when a real outcome exists.
- Tautologies: expected value computed with the same logic as production, or asserting what a mock was just configured to return.
- Asserting on stubs (`verify(repo).findById(...)`), on internal call order, or on how many times a private helper ran.
- Mocking in-process domain collaborators; more than one mock per test.
- Testing private/protected methods via reflection, `@VisibleForTesting`, `_private` access, or `friend` hacks.
- Snapshot tests of large structures used as a substitute for asserting a specific behavior.
- Duplicate tests that exercise the same exit point with an equivalent input (same equivalence class).
- Control flow inside a test; multiple Act phases; `sleep`; real I/O; order-dependent tests.
- Names with "should", a bare method name, or that need the body to be understood.
- Tests written to raise coverage. Coverage is a negative indicator only (low coverage on domain code means gaps; high coverage proves nothing). Never chase a percentage, never wrap code in `try/catch` to satisfy it. If asked for "more coverage", add tests only for uncovered FRs, boundaries, or failure modes, never for lines.

## Reviewing existing tests
Score each test 0 to 3 on the four pillars. Any pillar at 0 means you recommend delete or rewrite, with the reason. Flag every rejection-list hit with `file:line`. Flag flaky tests for quarantine in a separate pipeline so the unit-test suite stays a deterministic green zone. Prefer deleting noise over adding tests.

## Beyond unit tests
Integration tests belong to art-of-integration-testing, e2e tests to art-of-e2e-testing, and pipeline placement to art-of-cicd. If the user asked for unit tests on orchestration code, say it needs an integration test and offer it instead of producing mock-heavy unit tests.
