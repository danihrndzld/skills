---
name: art-of-cicd
description: Use when designing or reviewing CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, Azure Pipelines, CircleCI), quality gates and required checks, trunk-based development, DORA metrics, deployment strategies (blue-green, canary, rolling, rollback), flaky tests and retries, suite speed, parallel jobs and sharding, linting and static analysis policy, dependency pinning, lockfiles and SLSA, smoke, sanity and regression selection, or where the test pyramid levels run in a pipeline. Produces findings by severity with file:line, concrete pipeline changes verified by a run, and an optional HTML or PDF report.
---

# The art of CI/CD

A good pipeline fails only on real problems, and it reports them fast enough that the fix is cheap. To get there, order gates from fastest to slowest and investigate every failure. Ship small changes often, and roll back first when a deploy breaks.

For unit, integration and end to end test design, use the art-of-unit-testing, art-of-integration-testing and art-of-e2e-testing skills. ISTQB test design techniques (equivalence partitioning, boundary values, decision tables, state transition, coverage) are in art-of-unit-testing.

## Foundations in brief

- The seven ISTQB principles: testing shows presence, not absence, of defects; exhaustive testing is impossible; early testing saves money; defects cluster; tests wear out; testing depends on context; absence of defects is a fallacy.
- An error (human mistake) creates a defect (flaw in a work product), and executing the defect causes a failure. Lint and review find defects, and only running code shows failures.
- Levels stack from unit to integration, system and acceptance. Functional and non-functional types cut across them. Smoke, sanity and regression are selections of tests, not levels.
- This skill owns how those levels run in a pipeline: order, triggers, time budgets, gates and deployment.
- Details and sources: `references/foundations.md`.

## Workflow for a concrete repo or pipeline

Follow these steps in order when the skill is applied to a real repository, pipeline file or CI run. Pure concept questions get a direct answer from the references.

1. Read the pipeline files first: `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `.circleci/config.yml`, plus lockfiles, linter config, test config and branch protection (`gh api repos/{owner}/{repo}/branches/main/protection` when available).
2. Map the pipeline. For each job, record the trigger, `needs:`, whether it is a gate or a transformation, and its median duration (`gh run list --limit 20` and `gh run view --json jobs`, or the CI provider's API). Draw the critical path.
3. Find the gates. List what blocks a merge or a deploy and with what threshold: lint ruleset, coverage floor, required checks, smoke suite, manual approvals. Flag gates that do not block (`continue-on-error: true`, optional checks, `|| true`).
4. Measure suite health. Run the suites locally or read JUnit XML from CI artifacts. Record totals, duration per suite, the slowest ten tests, flaky tests (failed and passed on the same commit, or rerun plugins) and retries that wrap assertions. Compare against unit under 1 minute, integration under 5 and full suite under 30.
5. Check delivery: branch age and PR size, version and hash pinning (lockfiles, actions pinned by SHA, image digests), secrets handling, deployment strategy, rollback path, and the DORA snapshot from deploy runs and release tags.
6. List findings by severity with `file:line`. High means the finding can ship a defect to production or leak a secret (for example a retry around assertions in billing tests, a secret in the repo, a gate that never blocks). Medium slows feedback or hides signal. Low is hygiene.
7. Make the changes when the user asked for changes, or propose them as diffs when they asked for a review. Fix in the order errors, then speed, then signal.
8. Verify by running. Run the changed jobs locally (`act`, the test command, the linter) or push to a branch and read the run. Report the command, the result and any step you could not run.

## Routing

Load only the file you need.

| Need | File |
|---|---|
| QA, QC, error and defect and failure, the seven principles, verification and validation, pyramid, trophy and quadrants, levels, types, smoke, sanity and regression selection | `references/foundations.md` |
| Reviews, static analysis limits, linter buckets, rulesets, legacy linter adoption, reproducible dependencies | `references/static-testing.md` |
| Gate and transformation, GitHub Actions anatomy, CI and CD vocabulary, signal and noise, flakes and retries, suite speed, parallel and sharding, the gap between merges | `references/ci-fundamentals.md` |
| Source of truth, config as code, secrets, trunk-based development, SLSA, SemVer and pinning, DORA, code freeze, rollback, blue-green and canary | `references/delivery.md` |
| Task order, greenfield and legacy starter packs, one task per signal, leaving bash, errors and speed and signal triage, `always()`, sharding matrix, reusable workflows | `references/pipeline-design.md` |
| Citations for any claim | `references/sources.md` |
| Producing the HTML, PDF or email report | `references/report.md` |

## Quick reference

| Question | Answer |
|---|---|
| Which job runs first? | Build check, then lint, then unit tests, then integration and end to end tests |
| Suite time budget | Unit under 1 minute, integration under 5, full suite under 30 |
| Smoke suite limits | At most 5 checks, under 3 minutes, any failure rejects the build |
| Smoke or sanity? | Smoke is broad and shallow on every build. Sanity is narrow and deep on a build that claims a fix. |
| Regression strategy | Selection per push, prioritization nightly, retest all weekly or per release |
| Starting coverage target | About 80% on greenfield. On legacy, coverage never goes down. |
| Shards needed | Total suite time divided by target time, rounded up, plus margin (50 tests at 2.5 min for 25 min gives 5, choose 7) |
| Bugs between merges | Merge queue (`merge_group` trigger) plus periodic CI on `main` |
| DORA elite | Several deploys a day, lead time under 1 hour, restore under 1 hour, change failure rate 0 to 15% |
| Most hardware for deploys | Blue-green |
| Most automation for deploys | Canary with a baseline and automated golden signal checks |
| Pin that guarantees the same bytes | Content hash or full commit SHA, never a version tag |
| Pipeline problem order | Errors, then speed, then signal |
| Lint priority when time is short | Bugs, then errors, then style |

## Common mistakes

- Wrapping a whole test in a retry. It hides every other bug in that test. Retry only the isolated non-deterministic call.
- Rerunning a flaky test and merging. A flake is a failure to investigate. The second unexplained rerun of the same flake is noise.
- Reading green as signal. A passing test can encode a wrong expected value, and a suite silenced into green is still noisy.
- A gate that does not block. `continue-on-error: true`, `|| true` or a check that is not required in branch protection reports problems nobody acts on.
- One giant script as one job. A failure then says nothing about what broke. Use one task per signal.
- CI and release with separate build and deploy logic. CI then never tests what release does. Call one parameterized workflow from both.
- Deploying less often to reduce risk. Bigger batches raise change failure rate. Code freezes and fixed windows lengthen lead time.
- Forward fixing during an outage. Roll back first and fix calmly after.
- Trusting a version tag. Registries and action tags can move. Only a hash or full SHA pins the bytes.
- Expecting a linter to catch a wrong business rule. Static analysis never runs the code.
- Reporting a lint count without its ruleset. Flask 0.1 shows 22 issues with Ruff defaults and 1,023 with `--select ALL`.
- Slow "unit" tests. Unit tests that need 20 minutes or parallel runners are actually integration tests.

## Report on request

When the user asks for a report, follow `references/report.md`. It covers the `report.json` schema, the sections for a CI/CD report, the `scripts/build_report.py` command with `--formats html,pdf,summary`, several `--junit` files, and the GitHub Actions block that uploads the report and emails it.
