# Test design techniques for unit tests

Exhaustive testing is impossible, so a test design technique picks the few inputs worth a test and gives a reason for skipping the rest. For example, an 8 character field of letters and digits has 36^8 (about 2.8 trillion) possible inputs, and a unit suite gets about ten tests for it.

Each technique below produces coverage items (partitions, boundaries, rules, transitions, branches). Each coverage item becomes one scenario in step 3 of SKILL.md, in the form `entry point → exit point → scenario`. Scenarios that share an entry point and an exit point and differ only in input and expected value go into one parametrized test, with one row per coverage item and the item ID in the row name.

Section numbers such as §4.2.1 refer to the ISTQB Certified Tester Foundation Level syllabus v4.0.1 (2024). The syllabus groups techniques into black box (from the specification), white box (from the code) and experience based (from what the tester knows), and it treats experience based techniques as a complement to the other two (§4.1).

## Equivalence partitioning (§4.2.1)

Equivalence partitioning groups inputs so that every value in a group gets the same treatment. One value stands for the whole partition, because if it finds a defect, any other value in that partition should find it too. Partitions are valid (accepted) or invalid (rejected), they don't overlap, and none is empty. You can partition inputs, outputs, configuration, internal values, time and interfaces.

Coverage is partitions exercised divided by partitions identified, and the invalid partitions count. With several parameters, the minimum is Each Choice, which means each partition of each parameter appears at least once. Each Choice does not cover combinations.

Example spec for cinema tickets by age: 0 to 12 is a child, 13 to 64 is an adult, 65 to 120 is a senior, and any other age is rejected.

| ID | Partition | Value | Expected |
|---|---|---|---|
| EP-1 | age < 0 | -3 | rejected |
| EP-2 | 0 to 12 | 7 | child |
| EP-3 | 13 to 64 | 30 | adult |
| EP-4 | 65 to 120 | 70 | senior |
| EP-5 | age > 120 | 130 | rejected |
| EP-6 | not an integer | `"abc"` | rejected |

Six partitions give six scenarios. A seventh test with 31 adds nothing, because 31 is in the same partition as 30. The rejection list in SKILL.md calls that a duplicate test.

The entry point is `ticket_type(age)`. EP-2 to EP-4 share one exit point (the return value), so they become one parametrized test. EP-1, EP-5 and EP-6 share the other exit point (the thrown error), so they become a second parametrized test.

## Boundary value analysis (§4.2.2)

Boundary value analysis tests the edges of ordered partitions. It only applies when the partition is ordered, e.g., ranges, amounts, dates and lengths. The boundary values are the minimum and maximum of each partition. Developers make more mistakes at a boundary than in the middle of a range, e.g., an off by one error or `<` written in place of `<=`. Boundary value analysis refines equivalence partitioning and does not replace it.

There are two variants.

- **2-value BVA** tests each boundary and its nearest neighbor in the adjacent partition (Craig 2002, Myers 2011).
- **3-value BVA** tests each boundary and both of its neighbors (Koomen 2006).

The syllabus gives an example of the difference. The spec says `x <= 10`, and the code says `x == 10`. With 2-value BVA you test 10 and 11, and both give the same result under the spec and the code, so the defect survives. With 3-value BVA you also test 9, where the spec says true and the code says false, so the defect is found. Use 3 values when the boundary decides money, permissions or security.

Example spec: a name field accepts only letters, from 5 to 12 characters long. Equivalence partitioning gives three partitions (under 5, 5 to 12, over 12). 2-value BVA gives the values 4, 5, 12 and 13. 3-value BVA adds 6 and 11. The values 4 and 13 are the negative tests, where off by one defects show up.

Neighbors repeat between adjacent partitions. For example, the upper neighbor of 12 is 13, which is also the lower boundary of the next partition. Test each value once, and report coverage as coverage items exercised divided by items identified, with the number of distinct values that covered them.

Boundary rows join the equivalence partitioning rows in the same parametrized test, because the entry point and the exit point are the same:

```python
@pytest.mark.parametrize("age, expected", [
    pytest.param(0, "child", id="BVA-1 lower edge of child"),
    pytest.param(12, "child", id="BVA-2 upper edge of child"),
    pytest.param(13, "adult", id="BVA-3 lower edge of adult"),
    pytest.param(64, "adult", id="BVA-4 upper edge of adult"),
    pytest.param(65, "senior", id="BVA-5 lower edge of senior"),
    pytest.param(120, "senior", id="BVA-6 upper edge of senior"),
])
def test_age_sets_ticket_type(age, expected):
    assert ticket_type(age) == expected
```

The values -1 and 121 go into the rejection test. Every expected value is a literal from the spec, as SKILL.md step 5 requires.

## Decision tables (§4.2.3)

A decision table is for an outcome that depends on a combination of conditions. The rows are conditions and actions, and each column is a rule, which is one combination of true and false values. A full table has one column per combination, and you can drop columns that can't happen. The notation is T, F, "-" for a condition that doesn't matter, and N/A for a combination that can't happen. Coverage is feasible columns exercised divided by feasible columns. Building the table often exposes a rule that nobody wrote down, or two requirements that contradict each other. With many conditions the number of rules grows exponentially, so you minimize the table or pick columns by risk.

Example spec: "The cart ships free when the total reaches Q200 or the customer is a loyalty member. Members with a cart of Q200 or more also get an extra 10% off."

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| C1: total >= Q200 | T | T | F | F |
| C2: loyalty member | T | F | T | F |
| A1: free shipping | X | X | X | |
| A2: extra 10% off | X | | | |
| Input | Q250, member | Q250, guest | Q80, member | Q80, guest |
| Expected | shipping Q0, total Q225 | shipping Q0, total Q250 | shipping Q0, total Q80 | shipping charged, total Q80 |

Here is a defect that only the full table finds. The developer wires both actions to the same condition:

```python
free_shipping = total >= 200 or is_member
extra_discount = total >= 200 or is_member   # spec says "and"
```

R1 (all true) and R4 (all false) both pass, because the spec and the code agree when every condition has the same value. R2 and R3 both fail, because the code gives the 10% discount and the spec does not. People tend to write the all true and all false columns first, and those are exactly the two columns that this defect survives. That is why you test every feasible column.

Each column is one row of a parametrized test on the entry point `checkout(cart, customer)`. If the result object holds both shipping and total, the two values are facets of one outcome and can share the assert. If the discount is a separate exit point, it gets its own test.

## State transition testing (§4.2.4)

State transition testing is for an object whose next behavior depends on what already happened to it. A state diagram shows the states and the events that move the object between them, written as `event [guard] / action`. A state table shows the same model as a grid, where an empty cell is an invalid transition. A guard is a condition on the event, so the same event can lead to different states. Defects often sit in the guard.

There are three coverage criteria, from weakest to strongest.

- **All states** visits every state.
- **Valid transitions** (0-switch) takes every valid transition. Valid transitions is the usual baseline.
- **All transitions** also tries every invalid transition, with one invalid transition per test so that one defect can't hide another. All transitions is the minimum for mission critical or safety critical software.

Example of a login object:

| State \ Event | correct password | wrong password | logout | admin unlock |
|---|---|---|---|---|
| Logged out | Logged in | Logged out (attempts + 1); Locked when attempts = 3 | | |
| Logged in | | | Logged out | |
| Locked | | | | Logged out |

| ID | Events | Covers |
|---|---|---|
| ST-1 | correct password, logout | Logged out to Logged in to Logged out |
| ST-2 | wrong, wrong, wrong, admin unlock | the self loop, the guarded move to Locked, and the unlock |
| ST-3 | logout while Logged out | an invalid transition, which should be rejected cleanly |

ST-1 and ST-2 reach all states and take all valid transitions. All transitions needs ST-3 and one test for each other empty cell.

In a unit test, the entry point is the method that sends the last event in the sequence. The earlier events go in Arrange, which keeps the Act to one line. The exit point is the new state, read through the public API, or the error for an invalid transition. Rows with the same exit point can share a parametrized test, with the starting state built by a factory such as `make_session(state="locked")`.

State transition testing in this skill covers an object or a small group of objects with state, e.g., an order, a session or a parser. A lifecycle that a user sees across several screens belongs to art-of-e2e-testing.

## Statement and branch coverage (§4.3.1, §4.3.2)

White box techniques measure what the tests ran, once the code exists.

- **Statement coverage** is the percentage of executable statements that ran at least once.
- **Branch coverage** is the percentage of true and false outcomes taken at each decision. 100% branch coverage always gives 100% statement coverage, and the reverse is not true.

```python
def grade(score):
    result = "fail"
    if score >= 60:
        result = "pass"
    if score >= 90:
        result = "honors"
    return result
```

With one test, `grade(95)`, every line runs, so statement coverage is 100%. Only two of the four branch outcomes happen, so branch coverage is 50%. Adding `grade(45)` takes both false branches.

Coverage tells you what ran, and it does not tell you what was checked. No white box technique finds an omission, because if the code doesn't implement a requirement, there is no branch to run (Watson 1996, §4.3.3). So you use coverage to find gaps that the black box techniques missed, and never as a target, as the rejection list in SKILL.md says. Mutation testing (the mutation check in SKILL.md step 6) measures whether the tests check anything.

**MC/DC** (modified condition/decision coverage) requires each atomic condition in a compound decision to show that it changes the outcome on its own (Ammann and Offutt 2016). Use it on compound decisions such as `a and (b or c)` with a risk level of 6 or more. MC/DC is outside the Foundation syllabus (§4.3).

## Error guessing and checklists (§4.4.1, §4.4.3)

Error guessing predicts where defects are, from how this code or this kind of code has failed before. The syllabus lists categories for building a list of attacks.

- **Input**: a correct value rejected, or a missing parameter.
- **Output**: wrong format or wrong result.
- **Logic and calculation**: a missing case, a wrong operator, or a wrong operand.
- **Interfaces and data**: mismatched types, or bad initialization.

Typical attacks are `None` or `null`, the empty string, Unicode, zero as a divisor, negative numbers, overflow, time zones, currency rounding and concurrency. The representative value of each invalid partition counts as equivalence partitioning. Extra values from that same partition, chosen because they are typical language failures (e.g., `None`, `True` used as an integer, `"30"` as text), count as error guessing and get `EG-n` IDs.

Checklist based testing works through a list of conditions built from experience or known failure patterns. Write each item as a question you can check on its own, and leave out anything a tool already checks automatically (Brykczynski 1999).

Experience based techniques need no written spec, so they complement the black box and white box techniques. They don't replace them.

## Which technique to use

The technique depends on an observable property of the requirement or the code.

| If the unit has | Use | Coverage item | Stronger variant for high risk |
|---|---|---|---|
| An input or output processed by classes (valid and invalid) | Equivalence partitioning | partition | Each Choice across parameters |
| Ordered partitions (ranges, amounts, dates, lengths) | Boundary value analysis | boundary and neighbor | 3-value BVA |
| Several conditions that combine into different actions | Decision table | feasible column | full table, not minimized |
| Behavior that depends on what happened before | State transition | state or transition | all transitions, one invalid per test |
| Code that exists, and you need to know what ran | Statement coverage | statement | none |
| Decisions (`if`, `switch`, loops) | Branch coverage | branch outcome | MC/DC on critical compound decisions |
| A history of failures, or typical language or domain errors | Error guessing | anticipated error | documented attack list |
| An external standard with checkable criteria | Checklist | checklist item | checklist updated from defect analysis |

Most units need two or three techniques. For example, a pricing function usually needs equivalence partitioning and boundary value analysis on the amount, plus a decision table for the discount rules.

## How product risk sets rigor (§5.2.3)

Product risk analysis decides which techniques you use and how much coverage you aim for. For each requirement, rate likelihood and impact from 1 to 3, and multiply them to get the risk level.

| Level | Risk | Rigor |
|---|---|---|
| 1 to 2 | low | base variant (EP, 2-value BVA, valid transitions, statement coverage) |
| 3 to 4 | medium | base variant, plus error guessing on the requirement, plus branch coverage |
| 6 to 9 | high | strong variant (3-value BVA, full decision table, all transitions, MC/DC on compound decisions) |

Impact is high when a wrong result touches money, data, permissions or security. Likelihood is high when the logic is complex, recently changed or has failed before. Write the level next to each FR from SKILL.md step 1, so the number of tests per FR has a stated reason. A trivial unit in the step 2 triage gets no tests at any risk level.
