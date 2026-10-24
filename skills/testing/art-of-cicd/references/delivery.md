# Continuous delivery: source of truth, trunk, supply chain, deployment, DORA

## Version control and one source of truth

CI assumes a shared, versioned place to check in to. Humble and Farley [12] state it directly: to be doing continuous delivery, you must use version control.

A source of truth is the one place designated as authoritative for a piece of information, such as a configuration value. Every other copy is a mirror, and when a mirror disagrees with the source, the mirror is wrong. The failure mode is two systems that each believe they hold the truth.

Case: a service went down because its database config pointed at a database that no longer existed. An engineer fixed it in the cloud console and the alert cleared. The same outage returned that night, because the deployment tool reconciled the service against its own stored copy of the config and overwrote the manual fix. The fix made version control the single source of truth and had the deployment tool read from it. Adding the repo as a third independent copy would have made it worse.

Finding to report: config that lives in two places (a console and a repo, two repos, a deploy tool's state and the repo).

## Config as code and secrets

Deployment config, connection settings and infrastructure definitions are plain text that defines how the software runs. Store them in version control like source code.

Never commit secrets. Repo access is wider than secret access should be. Commit a config file that references the secret by name, and let the deployment tool resolve it from an access controlled store at deploy time:

```
--db-username=randomCloud:watchMeWatch:userServiceDBUser
```

When a code change depends on a config change, deploy both as one atomic unit. For example, splitting `--db-name` into `--db-users-name` and `--db-movies-name` in the same commit as the code that reads them avoids a window where the code asks for parameters the config does not provide.

## Trunk-based development

The trunk (usually `main`) is the single shared line of history. Trunk-based development merges small changes into it frequently, in days rather than weeks, instead of keeping long feature branches. Incomplete work is merged behind a clear issue reference. One team's average lead time for changes fell from 45 to 18 days after adopting it.

An incremental PR is complete when:

1. All code passes the lint checks.
2. Docstrings on incomplete functions explain why they are incomplete.
3. Every code change has tests and documentation.
4. Disabled tests carry an explanation and a tracking issue.

```python
@unittest.skip("(#2387) AllCatsAllTheTime integration WIP")
```

Merging early lets a second engineer build on the in progress class without coordinating, because the code is already on `main`. Teams whose policy forbids dead or disabled code on `main` use feature flags or build flags and still merge small and often.

Findings to report: branches older than a few days, skipped tests with no issue reference, long lived release branches that receive feature work.

## Supply chain: SLSA

SLSA [16] defines incremental levels of build security. SLSA v0.1 level 3 asks for five things:

| # | Requirement | Meaning |
|---|---|---|
| 1 | Always releasable | The codebase can produce a build at any time. This is the job of CI. |
| 2 | Automated builds | Every step is a script started by automation, never run by hand |
| 3 | Build as code | The build scripts and config are in version control |
| 4 | Use a CD service | A dedicated, consistently configured service, not someone's laptop |
| 5 | Ephemeral environments | Fresh for each build, destroyed after, nothing persists |

Beyond level 3 are hermetic builds (no network access during the build) and reproducible builds (same inputs give byte identical output). Current tooling supports both only partly.

A manual build that a person runs from a document is the normal starting point, not negligence. Assess it against the five requirements and improve one requirement at a time.

## Semantic versioning and pinning

SemVer [17] uses MAJOR.MINOR.PATCH. MAJOR means backward incompatible changes, MINOR means backward compatible features, and PATCH means backward compatible fixes.

Case: a service overwrote its `latest` image on every release. Consumers could not choose a version, could not tell releases apart and could not see what changed. A method changed its interface and a consumer's build broke in production with no warning. Semantic versions plus letting the consumer choose its version fixes all three problems.

Pinning to an exact version (`querytosql == 1.3.2`) stops "always latest" surprises, but it is not a guarantee. Most registries let a maintainer republish the same version tag with different content. Only a content hash guarantees the same bytes, and a changed hash fails the build loudly. The cost is that a hash pin also blocks a maintainer's legitimate same version fix until you repin.

| Pin | Example | Guarantees same bytes |
|---|---|---|
| None or range | `requests>=2`, `actions/checkout@main`, `image:latest` | No |
| Exact version or tag | `requests==2.32.3`, `actions/checkout@v4` | No, tags can move |
| Content hash | `--require-hashes` with `sha256:...`, `actions/checkout@<full commit sha>`, `image@sha256:...` | Yes |

In April 2021 an attacker modified Codecov's shared bash uploader script and collected environment secrets from every pipeline that fetched it [27]. Pin third party actions and scripts by commit SHA or hash.

## DORA metrics

DORA research [15] groups teams into elite, high, medium and low bands on four metrics.

| Pair | Metric | Definition | Elite |
|---|---|---|---|
| Velocity | Deployment frequency | How often the organization releases to production successfully | Multiple times a day |
| Velocity | Lead time for changes | Time from commit to production | Under one hour |
| Stability | Time to restore service | Time to recover from a production failure | Under one hour |
| Stability | Change failure rate | Share of deployments that cause a degradation needing remediation | 0 to 15% |

Velocity bands:

| Band | Deployment frequency | Lead time for changes |
|---|---|---|
| Elite | Multiple times a day | Under one hour |
| High | Once a week to once a month | One day to one week |
| Medium | Once a month to once every 6 months | One month to six months |
| Low | Less than once every 6 months | More than six months |

How to take a snapshot from a repo: deployment frequency from deploy workflow runs or release tags per week; lead time from merge commit time to the deploy run that shipped it; change failure rate from deploys followed by a revert, hotfix or rollback; time to restore from incident open to close. Say which source each number came from and the window it covers.

## Deploy more often, not less

A team with frequent post deploy outages is tempted to deploy monthly instead of weekly. Each deploy then carries more changes and is more likely to contain the breaking one. With the same outages attributed to daily deploys instead of weekly ones, the change failure rate drops from 37.5% (3 of 8) to 10% (4 of 40).

Code freezes and fixed deployment windows do not make deploys safer. Case: a company of more than 50 people deployed in windows every two months with a one week freeze before each. Deployment frequency was once every two months and lead time averaged 45 days, which is medium on both velocity metrics.

| Step | Change | Result |
|---|---|---|
| 1 | Trunk-based development and incremental delivery | Lead time 45 to 18 days, deployment frequency unchanged |
| 2 | Remove fixed windows and the code freeze | Lead time 18 to 4 days, deployment frequency monthly to weekly, maximum 8 days merge to deploy |

After step 2 the team reached DORA high on both velocity metrics. CI discipline came first and deploy cadence second. Removing the windows needed no new tools and no new people.

## Rollback first

When a deploy breaks something, roll back to the last known good version immediately and fix the bug calmly afterwards. In one documented example, adopting rollback first as a policy cut time to restore from several days to 13 to 40 minutes with no new tooling.

## Deployment strategies

| Strategy | How | Cost and effect |
|---|---|---|
| Rolling update | Update one instance at a time in place | Least extra hardware, slowest rollback |
| Blue-green | Two full environments and one traffic switch | Most extra hardware (doubles capacity for a while). Time to restore fell to about 5 to 12 minutes in the same example. |
| Canary | Send a small share of real traffic to the new version. Continue if metrics stay healthy, revert all traffic if not. | Most automation. Needs a configurable load balancer to split traffic, automated health judgment on the four golden signals (latency, traffic, errors, saturation) from Site Reliability Engineering [14], and a baseline instance for a fair comparison. |

## Continuous deployment is optional

Releasing every commit automatically is the most aggressive end of CD, not a requirement. Skip it if any of these apply: any failed request is unacceptable; regulation blocks it; mandatory QA or exploratory gating exists; a human sign off is required; releases need hardware changes.

Combined with canary deploys and rollback first, one worked example reached elite on all four metrics: multiple deploys a day, lead time under an hour, about 7 minutes to restore and a 12.5% change failure rate.
