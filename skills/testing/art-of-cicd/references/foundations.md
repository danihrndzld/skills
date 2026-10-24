# Foundations, levels and change-related testing

Terms follow the ISTQB CTFL syllabus v4.0.1 [1]. Test design techniques (equivalence partitioning, boundary values, decision tables, state transition, coverage) live in the art-of-unit-testing skill.

## QA, QC and testing

QA contains QC, and QC contains testing.

| Term | Focus | Notes |
|---|---|---|
| Quality assurance (QA) | Process, preventive | A good process, followed correctly, produces a good product. Everyone owns it. |
| Quality control (QC) | Product meets its quality requirements | Includes formal methods, simulation and prototyping as well as testing. |
| Testing | Product, corrective | Exercise the product to find defects and build evidence about its quality. |

## Error, defect, failure

The causal chain is error, then defect, then failure.

- Error: a human action or decision that produces a wrong result. For example, a developer assumes a value is in pounds when the spec says newtons.
- Defect (bug): a flaw in a work product (requirement, design, code) that can cause a failure. It exists whether or not anyone runs the code.
- Failure: the system does not perform a required function within specified limits. A failure happens only when the defect is executed under the right conditions.
- Root cause: the deepest reason the error happened. Root cause analysis looks for it.

Static testing finds defects. Only execution produces failures. In a pipeline, a red lint job reports a defect and a red test job reports a failure.

Cases with published inquiry reports:

- Ariane 5 Flight 501 (1996) [24]. The team reused Ariane 4 inertial reference software without retesting it under Ariane 5 flight parameters. A 64 bit float to 16 bit integer conversion overflowed, both guidance computers failed, and the rocket self destructed 37 seconds after launch. Reused code in a new context needs retesting.
- Mars Climate Orbiter (1999) [25]. Ground software produced thrust data in pound force seconds and navigation software expected newton seconds. No check caught the mismatch, and the probe was lost. Interfaces between teams need explicit, tested assumptions.

## The seven ISTQB principles

1. Testing shows the presence of defects, not their absence.
2. Exhaustive testing is impossible. Use techniques, prioritization and risk to focus effort.
3. Early testing saves time and money. Defects found before release cost less to fix.
4. Defects cluster together. A small number of modules usually holds most defects, which is why risk based testing works.
5. Tests wear out (the pesticide paradox). Repeating the same tests eventually finds no new defects, so review and update them, including the smoke suite.
6. Testing is context dependent. An online shop, a safety critical system and an internal tool need different strategies.
7. The absence of defects is a fallacy. A system with no known defects can still fail its users.

## Verification and validation

Verification asks whether the system matches its specification. Validation asks whether it meets the need behind the specification. Unit, integration and system testing mostly verify, and acceptance testing validates. Many defects found at acceptance are a project risk, because the validation question was asked too late.

## Balance models

| Model | Shape | Use |
|---|---|---|
| Test pyramid (Cohn [6]) | Many unit tests at the base, fewer integration tests, few end to end tests at the top | Stacks where units are cheap to isolate. Bottom is fast and cheap, top is slow and expensive. |
| Testing trophy (Dodds [7]) | Static at the base, then unit, a wide integration layer, a thin end to end layer | Modern stacks, especially frontend JavaScript. Guiding quote: "The more your tests resemble the way your software is used, the more confidence they can give you." |
| Agile testing quadrants (Marick, Crispin and Gregory [5]) | 2 by 2 grid: business facing or technology facing, supporting the team or critiquing the product | Q1 unit and component tests (automated). Q2 functional and story tests (automated and manual). Q3 exploratory, usability, UAT (manual). Q4 performance, load, security (tool driven). |

Shift left means static testing, reviews and early test design during requirements, design and coding. Shift right means monitoring, observability, canary releases, feature flags and user feedback in production. A pipeline covers both ends.

## Levels

Levels stack from unit to acceptance. Types (functional and non-functional) cut across every level. Smoke, sanity and regression are selections of tests, not levels.

| Level | Target | Owner | Usual perspective | Skill |
|---|---|---|---|---|
| Unit | Smallest building blocks in isolation, always automated | Developers | White box | art-of-unit-testing |
| Integration | Interfaces and the data that crosses them. Component integration (two of your modules) and system integration (a third party API). Contract tests (for example Pact) live here. | Developers and testers | Gray box | art-of-integration-testing |
| System | The whole system in a dedicated test environment, end to end flows. Keep it thin. | Testers | Black box | art-of-e2e-testing |
| Acceptance | "Do we accept it?" against acceptance criteria agreed in advance | Users, customers, regulators | Black box | art-of-e2e-testing |

Acceptance forms: UAT (real users, environment close to production), alpha (internal testers), beta (real users in production, the only form that finds defects tied to environments you cannot reproduce), contractual or regulatory (independent testers or regulators).

This skill owns how those levels run inside a pipeline: order, triggers, time budgets, gates and the signal each one produces.

## Types overview

| | Functional | Non-functional |
|---|---|---|
| Question | What the system does | How well it does it |
| Oracle | The requirement | A threshold, or judgment |
| Example | Login accepts a valid password | Login responds in under 2 seconds |

Non-functional dimensions, each testable at every level:

- Performance. Load testing holds expected usage and checks response. Stress testing pushes past normal usage to find the breaking point and check recovery. Production monitoring catches slow degradation between releases.
- Usability. ISO 9241-11 [8] measures effectiveness, efficiency and satisfaction, with feedback from the target audience.
- Security. Runs in every phase. The OWASP Top 10 [9] has listed broken access control first since 2021.
- Visual. Rendering across browsers, operating systems and screen sizes.
- Resilience. Holds the agreed service level under real conditions and recovers. Chaos engineering breaks things on purpose in production.

Non-functional defects found late are usually architectural, so plan these tests early.

## Smoke, sanity and regression selection

| Selection | Question | Shape | When |
|---|---|---|---|
| Smoke | Is this build worth testing? | Broad and shallow over the critical path | Every build, before anything else |
| Sanity | Did they fix it? | Narrow and deep, only the changed area and its neighbors | A build that claims specific fixes. Usually unscripted and time boxed. |
| Regression | Did the change break what worked? | Rerun tests that already passed | After every change, within a time budget |

Smoke and sanity are gates. They decide whether expensive testing starts, and neither replaces regression testing.

Smoke suite constraints that work: at most 5 checks, the whole suite under 3 minutes, and any failure rejects the build without discussion. Cover only the money path. For a food delivery app: open the app and log in; load the restaurant list with at least one result; add an item and see the total update; pay with a sandbox card and create an order; see the order on the status page.

Choosing from release notes:

| Release note | Selection |
|---|---|
| Fixed checkout crash when the cart had 0 items | Sanity |
| New build, 40 files changed in login, search and checkout | Smoke |
| Hotfix, profile photo upload works again | Sanity |
| First build after switching payment provider | Smoke, then deep regression on payments |

Regression strategies, usually combined:

1. Retest all. Run everything. Fits a weekend or release run.
2. Test selection. Run only what the change can reach. Fits the per push run.
3. Prioritization. Run the riskiest tests first. Fits the nightly order.

Brooks [3] noted that every fix can break something else, so in theory you rerun every test after every change, and in practice you get close at a real cost. The CrowdStrike Falcon update of July 2024 crashed millions of Windows machines at boot after passing some testing but no regression pass that would catch a boot level driver crash.

When smoke testing an API, assert the body as well as the status line. Some APIs return 200 with `success: false` in the body.
