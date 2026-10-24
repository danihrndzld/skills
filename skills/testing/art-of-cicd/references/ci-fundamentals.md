# CI fundamentals and test quality as a gate

## Pipeline, gate, transformation

A pipeline is an automated sequence of tasks that runs every time code changes. A task (or step) is one discrete unit of work. Every task is one of two kinds.

| Kind | What it does | Examples |
|---|---|---|
| Gate | Verifies code and can block the pipeline | Linting, testing |
| Transformation | Changes the form of the code and moves it forward without verifying | Building, publishing, deploying |

Run linting first. A slower test suite has no reason to run against code that already fails a fast check. A typical sequence is lint, test, build image, push to registry, update running service.

Define pipelines as config in version control, not by clicking in a GUI. Config in the repo survives staff turnover and gets reviewed.

## GitHub Actions anatomy

```yaml
# .github/workflows/lint.yml
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ruff check .
```

The whole file is a workflow. `on: push` is the trigger. `lint` is a job, which runs on one machine. Each `-` line is a step, run in order.

Manual triggering breaks once a team has more than one person. A webhook lets version control start the pipeline on every push. The rule this enables is that when the pipeline breaks, people stop pushing changes until it is fixed.

## Vocabulary

| Year | Event |
|---|---|
| 1994 | Booch coins "continuous integration" |
| 1999, 2007 | Beck, then Duvall et al. [13] formalize CI. Duvall also coins "continuous deployment" in 2007. |
| 2010 | Humble and Farley [12] name "continuous delivery" |
| 2014 to 2016 | "CI/CD" enters common use as an informal catch all |

- Continuous integration (CI): combining code changes frequently, with each change verified at check in. In gate and transformation terms, CI is the gates.
- Continuous delivery (CD): you can deliver changes safely at any time, and delivering is as simple as pressing a button. CI gives the first guarantee and automated release gives the second.
- Continuous deployment: every commit that passes releases automatically. See `delivery.md` for when to skip it.

## Signal and noise

Signal is information. Noise is anything that distracts from it. Passing does not mean signal, and failing does not mean noise.

| Case | Class | Reason |
|---|---|---|
| A UI test fails because a change moved a button | Signal | It told the engineer something true and new about the change |
| An integration test fails once, nobody knows why, a rerun passes | Signal | Something caused the failure, even if nobody understands it yet |
| The same test fails again weeks later on another PR, rerun, merged | Noise | Ignoring the same unresolved flake twice teaches the team to ignore real information |
| A pagination test expects 3 items when the right answer is 2, and it passes | Noise | The passing test hides a real bug |

Treat every failure as a bug. A failure is a mismatch between what the test expects and what the system does. Either the test is wrong or the system is wrong, and both need investigation. The most common way noise enters a suite is assuming the test is wrong without checking.

A suite that stays green because failures were silenced is still noisy. The goal is that every failure is a signal the team acts on immediately.

## Flakes and retries

A flaky test fails inconsistently under apparently equal conditions. Flakes are the most common source of a noisy suite because "just rerun it" feels harmless. Treat a flake like any other failure.

Retry only the isolated non-deterministic call, never the test body. In a documented case, a test against an unstable third party service failed about 1 in 20 runs on timeouts. An engineer wrapped the whole test body in a retry decorator with up to three attempts. The retry also hid a real billing bug (wrong charge amounts), which then caused a production outage. The safe fix retries the connection call and leaves the assertions and business logic outside the retry.

Finding to report: any test level retry (`@retry`, `pytest-rerunfailures` with `--reruns`, `retries` in Playwright or Jest config, `retry: 2` on a CI job) that wraps assertions. Severity is high when the test covers money, auth or data integrity.

## Suite speed

Set time budgets per layer and use coverage to rebalance. An example budget is unit tests under 1 minute, integration under 5 minutes and the full suite under 30 minutes.

Split the suite by type before everything is fast. With hundreds of unit tests that finish in under a minute and a smaller integration batch that takes four hours, splitting lets the fast layer run before merge now. Use a folder convention or a language feature such as pytest markers. Duvall [13] states the rule as "run the fastest tests first."

Use coverage to find where to add or remove tests, not as a target number. To move tests down the pyramid:

1. Find a unit coverage gap and add the missing unit test.
2. Find a slower integration or end to end test that covers exactly the same logic.
3. If the unit test now covers it, delete the slower duplicate.

Example: a method has five integration tests around it and one happy path unit test. Replace the five with one integration test that checks the components are wired correctly, and add unit tests for each case (no cache, cached, error, empty results).

Diagnosing an unbalanced suite: a suite runs about 3 hours per PR with 10% unit, 0% integration and 90% end to end tests. The "unit" tests take 20 minutes and cover 34% of the code. Real unit tests run in seconds, so these are actually integration tests. Fix in this order: split out the fast tests to run first, measure real unit coverage, then use coverage to find end to end tests that are safe to move down.

## Parallel execution and sharding

Parallel execution spreads tests across CPU cores on one machine. Sharding spreads them across machines. Both trade hardware for time and add no confidence.

Requirements: tests do not depend on each other, do not need a specific order and do not share state. If unit tests are slow enough to need parallel execution, they are probably not unit tests.

```
pytest --shard-id=$SHARD_ID --num-shards=$NUM_SHARDS
```

Sizing: 50 browser tests at about 2.5 minutes each with a 25 minute target need at least 5 shards. Choose 7 for margin. The GitHub Actions matrix syntax is in `pipeline-design.md`.

## The gap between merges

A fast, reliable PR triggered pipeline still misses bugs introduced between merges. Two engineers each change the defaulting logic of the same function on different lines. Both PRs pass CI alone, and together they break production.

| Option | How it works | Cost |
|---|---|---|
| Periodic CI | Runs on `main` at fixed intervals | Catches after the fact, needs an owner who watches it, lets `main` break for a while |
| Up to date branch required | A branch must include the latest `main` before merge | Every merge forces every open PR to resync |
| Merge queue | Reruns CI against the latest `main` before merging | One extra CI run per merge. GitHub and similar hosts offer it natively (`merge_group` trigger). |

Keep periodic CI even with a merge queue. A flake that appears 1 in 500 runs gets investigated from an hourly periodic run, and is usually not investigated when it appears in someone else's PR.
