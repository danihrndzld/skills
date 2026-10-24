# Pipeline design

## The universal task list

Every project ends up with the same tasks: linting, unit tests, integration tests, end to end tests, building, publishing and deploying. Each task is a gate or a transformation (see `ci-fundamentals.md`).

Order tasks to get as much signal as possible, as fast as possible. A build check is nearly instant. Linting and unit tests need more setup and still run in minutes. Integration and end to end tests cost more to build and run slower, so they come last.

CI should reuse the release pipeline's own build and deploy tasks, not separate copies that look similar, so that what CI tests stays close to what reaches production.

## Starter packs

A starter pack is the ordered set of automation tasks to add first when a project has none. It is the smallest set that already gives useful signal, not the full set you will eventually want.

### Greenfield order

1. Build check
2. Linting, as early as possible
3. Fix existing lint violations
4. Unit tests
5. Measure coverage
6. Add tests to reach the coverage target
7. Publish
8. Deploy
9. Integration and end to end tests

The build check comes first because if the code does not build, nothing downstream can run.

```yaml
name: build-check
on: [pull_request, merge_group, schedule]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build .
```

One job, three triggers: PR, merge queue and schedule.

Integration and end to end tests go last on purpose. They take longest to set up, and postponing them lets the faster tasks produce useful signal sooner.

Two early choices:

- Coverage target. Start around 80%. It is a starting point to tune.
- Deployment strategy. Continuous canary is low risk even on day one.

Resulting pipelines:

```yaml
# ci.yml
jobs:
  lint:
  unit-test:
  coverage:
  integration-test:
  e2e-test:
```

```yaml
# release.yml
jobs:
  build:
  publish:
  deploy-canary:
```

### Legacy order

1. Build check, the same as greenfield.
2. Isolate the part of the codebase worth investing in.
3. Tests, focused on the isolated code.
4. Deployment automation, once it feels safe.

Linting drops to "if there is time." It moves from step 2 in greenfield to nearly optional in legacy.

An end to end test can outrank unit tests in legacy. Unit tests need refactoring work in a large existing codebase, and one end to end test can check whether already separated services work together, which nothing else in the pipeline verifies.

Prioritize by pain. Pain is something people avoid because dealing with it causes a real problem: blocked work, after hours effort, repeated postponement. To find it, look for what the team does unusually rarely. Example: deploys every three months at best, all services at once, a manual staging phase with the whole team, bugs found only after deploy. The root cause was the state of the code being deployed, not the deploy mechanics. Coverage per repo started anywhere from 0% to over 60%, and the rule was never a uniform target, only that coverage never goes down.

From manual to automated:

1. Document what people do by hand today.
2. Turn the document into one or more scripts.
3. Commit the scripts to version control.
4. Add automated triggering for the scripted process.

## One task per signal

If the whole pipeline is one task running a large bash script, pass or fail is the only signal, and a failure does not say what broke. Use a separate task for each discrete signal you want the pipeline to produce. Nine functions in one script become nine tasks that report separately.

Design tasks like functions: high cohesion, loose coupling, clear inputs and outputs. A task does too much when logic is duplicated across tasks, or when orchestration (loops, polling) lives inside a task instead of in the pipeline.

Shared pipeline libraries need their own tests. Case: a shared bash library, `e2e_tests.sh`, gained a line that unset an environment variable "to guarantee a clean state." Review approved it, and it silently broke another team's pipeline that relied on the variable. The reviewer had no tests showing the library's expected behavior. The fix was a test that asserts which environment state exists after importing the library.

## When bash falls short

Bash functions return only exit codes, and there is no good way to version or share a bash library. Move off bash when you see any of these: scripts longer than a few lines; multiple conditions and loops; logic complex enough to deserve tests; logic a team wants to share across scripts.

Ways out of bash:

1. A standalone tool in a general purpose language.
2. A library in a general purpose language.
3. A reusable, versioned CD task, referenced by tag or SHA:

```yaml
jobs:
  lint:
    steps:
      - uses: myorg/cd/.github/actions/python-lint@v0.1.0
```

A complex stateful routine becomes a tested, versioned library. A few lines of lint commands can stay as they are.

## Triage: errors, speed, signal

| Category | Symptom |
|---|---|
| Errors | The pipeline does the wrong thing |
| Speed | It takes too long to run when people need it |
| Signal | It reports the right information too late to act cheaply |

Fix in the order errors, then speed, then signal. A slow pipeline cannot run more often, and a pipeline that cannot run more often cannot fix its signal problem. Fixing speed starts fixing signal too.

Example with all three: a pipeline does not clean up test environments on failure (error), takes over an hour so it runs only nightly (speed), and when it fails, the breaking change was merged a full day earlier (signal).

## Cleanup, parallel jobs and sharding in GitHub Actions

Cleanup that must always run uses `if: ${{ always() }}` on the job or step, the same role as a `finally` clause in code.

Jobs without a `needs:` line start at the same time, so total time drops to roughly the slowest job instead of the sum:

```yaml
jobs:
  build-image:
    runs-on: ubuntu-latest
  setup-sut:
    runs-on: ubuntu-latest
```

Sharding splits a long suite across machines with a matrix:

```yaml
jobs:
  e2e:
    strategy:
      matrix: {shard: [1, 2, 3, 4, 5, 6]}
    steps:
      - run: pytest --shard-id=${{ matrix.shard }} --num-shards=6
```

An end to end pipeline that ran nightly because it took over an hour, sharded to under 20 minutes, can run on every PR. It then merges into one CI pipeline where lint, unit, integration and end to end tests all start in parallel, with one job that fans in:

```yaml
jobs:
  gate:
    needs: [lint, unit, integration, e2e]
```

Make the fan in job the required status check in branch protection. Then one check name stays stable while the jobs behind it change.

## Combine pipelines with parameters

If CI and release each have their own build and deploy logic, passing CI never verifies what release will do. Call the same pipeline with different inputs instead of duplicating it:

```yaml
jobs:
  release:
    uses: ./.github/workflows/release.yml
    with: {image-registry: test-registry, deploy-target: test-env}
```

```yaml
on:
  workflow_call:
    inputs: {image-registry, image-name, version-from-tag, deploy-target}
```

Values that must become parameters when a hardcoded release pipeline also serves CI:

1. `image-registry`: production registry or a throwaway test registry.
2. `image-name`: which image the pipeline builds and pushes.
3. `version-from-tag`: where the version number comes from.
4. `deploy-target`: fixed production address or a freshly provisioned test environment.

Credentials also differ between test and production. Pass them as secrets per environment, never as plain inputs.
