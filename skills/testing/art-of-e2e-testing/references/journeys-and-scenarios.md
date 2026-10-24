# Journeys and scenarios

## Picking journeys by risk

Exhaustive testing is impossible, and end-to-end tests are the most expensive tests to run, so pick journeys by product risk (ISTQB CTFL 5.2.3). For each candidate journey, estimate:

- Likelihood that it breaks, from 1 to 3. Raise it for code that changes often, code with a defect history, flows that cross many services, and recent rewrites. Defects cluster, so a few modules hold most of them.
- Impact if it breaks in production, from 1 to 3. Raise it for money, legal or regulatory duties, data loss, and the first step of a funnel.

Level is likelihood times impact.

| Level | Treatment |
|---|---|
| 6 to 9 | Automate as an e2e journey. Cover the happy path and the one failure the user must see (e.g., a declined card). |
| 3 to 4 | Cover with integration or API tests. Add to an exploratory charter. |
| 1 to 2 | Unit tests and checklists only |

Example for a food delivery app:

| Journey | Likelihood | Impact | Level | Decision |
|---|---|---|---|---|
| Log in, add an item, pay with the sandbox card, see the order status | 2 | 3 | 6 | e2e |
| Card declined shows a message and keeps the cart | 2 | 3 | 6 | e2e |
| Change profile photo | 2 | 1 | 2 | integration test on the upload endpoint |
| Filter restaurants by cuisine | 2 | 2 | 4 | API test plus unit tests on the filter |

A smoke set is a thin, cheap pass over the critical path that decides whether the rest of the testing should run. Keep it to at most 5 checks that finish in under 3 minutes, and reject the build if any of them fails. For the app above, the smoke set is: the app opens and a known account logs in, the restaurant list shows at least one result, adding an item updates the cart total, paying with the sandbox card creates an order, and the order appears on the status page. Review the smoke set every few releases, because the same checks stop finding new defects over time.

## Use case and scenario testing

A use case describes how an actor reaches a goal through the system. Derive journey tests from it:

1. Take the main success scenario as the happy path test.
2. List each alternative flow and each exception flow. Keep only the ones with a visible outcome the user depends on, and push the rest down to integration or unit tests.
3. Write each kept flow as one test with its own name.

Example use case "Customer checks out":

| Flow | Steps | Visible outcome | Level |
|---|---|---|---|
| Main | Open cart, enter address, pay with saved card | "Order confirmed" and order number | e2e |
| Alt: new card | Same, but enter a new card and save it | Card appears under saved cards | e2e if saving cards is high risk, else integration |
| Exc: card declined | Pay with the sandbox decline card | "Your card was declined", cart still has 3 items | e2e |
| Exc: address outside delivery zone | Enter a far address | "We don't deliver to this address" | integration test on the address endpoint, unit tests on the zone rule |

## Given, When, Then

Acceptance criteria written as Given, When, Then map directly to a journey test (ISTQB CTFL 4.5.2 and 4.5.3, acceptance test driven development).

```gherkin
Scenario: Returning customer pays with a saved card
  Given a customer "ana@example.test" with a saved Visa ending 4242
  And her cart holds 2 "Pepian" at Q45.00 each
  When she checks out with the saved card
  Then she sees "Order confirmed"
  And the order total reads "Q90.00"
```

Rules:

- Given sets state through the API or a seed script. The UI is used only for the steps under test.
- When holds user actions in domain language, e.g., "checks out", not "clicks the button with id btn-3".
- Then holds visible outcomes with exact values from the acceptance criteria.
- Write one scenario per acceptance criterion, plus the negative case the user must see.
- Step definitions call page objects. They don't contain locators.
- Use feature files only if people outside the team read them. Otherwise write the same structure as comments or blocks in code.

## State transitions across screens

When a journey moves an entity through states (e.g., a claim goes from draft to submitted to approved to paid), draw the state table first and choose the transitions to test (ISTQB CTFL 4.2.4).

| From | Event | To | Screen check |
|---|---|---|---|
| Draft | Submit | Submitted | Badge "Submitted", Edit button gone |
| Submitted | Approve (reviewer) | Approved | Badge "Approved" in the customer's list |
| Approved | Pay | Paid | Badge "Paid", receipt link visible |
| Submitted | Edit | (invalid) | Edit button absent or disabled |

- The happy path through every valid state is one e2e journey, with a screen check after each transition.
- Test invalid transitions (editing a submitted claim) through the API in integration tests, one invalid transition per test, and check once in the UI that the control is absent.
- Journeys with two actors (customer and reviewer) use two browser contexts in one test, each with its own session.

## Exploratory charters

Exploratory testing designs, runs, and evaluates tests at the same time, in a time-boxed session guided by a charter (ISTQB CTFL 4.4.2, Hendrickson 2013). It finds problems no script anticipated, and it is a standard technique for acceptance testing.

Charter format: "Explore <area> with <resources or approach> to discover <kind of problem>." Example: "Explore checkout with the browser back button and a second tab to discover ways the cart and the payment get out of sync." Time box is 45 to 90 minutes.

During the session, record what was tried, what was found, and questions for the team. At the debrief, turn each confirmed defect into an automated test at the lowest level that reproduces it. Only defects that need the full flow become e2e tests.

## Checklists

Checklist based testing works through verifiable questions built from experience, standards, or known failure patterns (ISTQB CTFL 4.4.3). Each item is a yes or no question that can be checked separately. Leave out anything the pipeline already checks automatically.

Accessibility checklist for each journey's screens (based on WCAG 2.2 level AA):

- Can the whole journey be completed with the keyboard only, with a visible focus indicator?
- Does every form field have a label that a screen reader announces?
- Are error messages announced and linked to the field they describe?
- Is text contrast at least 4.5 to 1 for normal text?
- Does the page still work at 200 percent zoom and at a 320 px wide viewport?

Automate the parts a tool can check, e.g., run axe (`@axe-core/playwright`, `cypress-axe`) on each journey screen and fail on serious or critical violations. Keep the keyboard and screen reader items as a manual checklist before release.

Other useful checklists: cross-browser and viewport matrix (the browsers your analytics show above a set share), and usability heuristics such as Nielsen's first heuristic, which asks whether every action gives feedback within one second.
