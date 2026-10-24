# Boundaries and test doubles

## Levels and vocabulary

ISTQB names two integration levels, and the same rules apply to both.

| Level | What it checks | Example |
|---|---|---|
| Component integration | The interface between two of your own modules, through a real managed dependency | `OrderService` plus `OrderRepository` plus your PostgreSQL |
| System integration | The interface between your system and another system | your service calling a partner's `getUserData` API and handling `200` with JSON |

| Term | Integration level meaning |
|---|---|
| Entry point | A controller action, an application service method, a message handler, or an HTTP endpoint |
| Exit point | The response (status and body), a state change in a managed dependency (rows, cache keys, files), or an outgoing call to an unmanaged dependency |
| Perspective | Gray box. You know the schema and the API contract, so you can build better data and check side effects, but you don't measure branch coverage here. |

One test may assert several exit points of the same scenario, because the scenario is expensive to set up and the exit points describe one outcome. Two scenarios still need two tests.

## Managed and unmanaged dependencies

The question that decides the treatment is who else can observe the dependency.

| Question | Managed | Unmanaged |
|---|---|---|
| Who reads and writes it? | Only your application | Other applications, other teams, or the outside world |
| Is its state part of your public contract? | No. It is an implementation detail. | Yes. Messages and calls are what other systems see. |
| Treatment in integration tests | Run it for real | Replace it with a mock at your adapter and assert the call |
| Examples | your service's own database, your own Redis, your own blob container | message broker topics others consume, SMTP, SMS, payment gateway, another team's REST API |

A database shared with another application is partly unmanaged. Treat the tables the other application reads as a contract. Assert their content as an outgoing interface and keep their schema under a contract test.

Mock at your own adapter, e.g., `EmailGateway.send(to, template, data)`, not at the vendor SDK. You own the adapter interface, so the mock survives an SDK upgrade, and a separate thin test can check the adapter against the vendor's sandbox.

At most one mock per unmanaged dependency per test. Assert the call happened with the right arguments, and also assert that no call happened in the failure scenarios, e.g., a rejected order sends no email.

## What runs real

| Thing | Real or doubled | Notes |
|---|---|---|
| Your database | Real, same engine and major version as production | Migrations run once per test run, the same migrations production uses |
| Your cache | Real when the code depends on expiry or eviction, otherwise optional | A container is cheap |
| Your file or object storage | Real local container (e.g., MinIO, Azurite, LocalStack S3) or a temporary folder | Temporary folder is fine when the adapter only writes files |
| Message broker | Fake or mock at your publisher adapter | Use a real broker only to test your own consumer's ack, retry, and dead letter handling |
| HTTP APIs of others | Stub server (WireMock, MockServer, `httptest.Server`, `nock`, `respx`) or adapter mock | Check the shape against a contract test, not by calling the real API |
| Clock, IDs, randomness | Stub | Inject at composition root |
| Auth provider | Stub the token validator or issue test tokens signed with a test key | Keep one test that runs the real middleware with an invalid token |

## Containers or in-memory fakes

| Option | When to use it | Risk |
|---|---|---|
| Container with the production engine (Testcontainers, Docker Compose service in CI) | Default for databases, caches, and storage | Startup time of 2 to 10 seconds, so share one container per run or per worker |
| Embedded production engine (SQLite when production is SQLite, embedded Kafka for your own consumer) | Production uses the same engine | None beyond version drift |
| In-memory substitute with a different engine (H2 for PostgreSQL, EF Core InMemory for SQL Server) | Never for tests that touch queries, constraints, transactions, or JSON columns | Different SQL dialect, no real constraints, different locking. Defects pass. |
| Hand-written in-memory fake of an unmanaged adapter | Default for message publishers and email gateways | The fake drifts from the real system, so pair it with a contract test |

## Data reset strategies

| Strategy | How | Good for | Watch out for |
|---|---|---|---|
| Transaction rollback per test | Begin a transaction in setup, roll back in teardown | Fastest. Most service and repository tests. | Code under test that opens its own transaction or commits. HTTP tests where the server runs on another connection. |
| Truncate touched tables before each test | `TRUNCATE ... RESTART IDENTITY CASCADE` or delete in foreign key order | HTTP tests and code that commits | Slower on large schemas. Truncate before, not after, so a failed test leaves data to inspect. |
| Database per worker | One schema or database per parallel worker | Parallel runs | More migrations at startup |
| Unique data per test | Random suffix on unique keys and IDs, assertions filtered by those IDs | Shared environments where reset is impossible | Assertions on totals or counts across the table break |
| Snapshot and restore | Restore a template database before each test or class | Large reference data sets | Restore time |

Seed reference data (countries, currencies, plan types) with migrations, because production has it. Seed scenario data inside each test so a reader sees every value that affects the outcome.

## Asynchronous work

Messages handled by a consumer, outbox relays, and background jobs finish after the Act returns. Poll for the observable condition with a deadline, e.g., check every 100 ms for up to 5 seconds whether the `outbox` row has `sent_at` set. Fail with a message that names the condition and the last value seen. A fixed sleep either wastes time on every run or fails on a slow CI machine.

When the job is triggered by time, call the job's entry point directly with a stubbed clock instead of waiting for the scheduler.

## Contract tests

A contract test checks that a consumer and a provider agree on the shape of the messages or requests between them, without running both systems together.

| Approach | How | When |
|---|---|---|
| Consumer-driven contracts (Pact) | The consumer's tests record the requests it sends and the responses it needs. The provider's pipeline replays them against the real provider. | Two teams own the two sides and deploy separately |
| Provider schema check | Validate your stub responses and your real responses against the published OpenAPI, AsyncAPI, JSON Schema, or protobuf | You consume a third-party API you can't run |
| Message schema registry | Producer and consumer serialize through a registry with compatibility rules | Event streams with many consumers |

Contract tests replace the end-to-end test that would otherwise deploy both services only to check field names. Keep them in the integration stage of each side's pipeline.

## Configurations and pairwise

When the same orchestration must work across several configurations, e.g., database engine, locale, feature flag, and payment provider, running every combination grows too fast. Kuhn, Wallace, and Gallo (2004) found that most failures in the systems they studied were triggered by one or two interacting parameters. Cover every pair of values instead of every combination (pairwise, ISO/IEC/IEEE 29119-4). Four parameters with three values each need 81 combinations, and pairwise covers all pairs in 9. Use a pairwise tool (PICT, `allpairspy`) to generate the rows and run them as a parametrized integration test. Raise to three-way only for high-risk combinations.

## API tests

An API test is an integration test whose entry point is an HTTP endpoint. Check these things in one test:

1. The status code.
2. The response body fields that the spec defines, with exact values.
3. The server-side state, read back through a repository or a fresh connection.
4. The outgoing message or call, on the mock.

Don't stop at the status line. Some APIs return `200` with an error flag in the body, so the body is part of the oracle. Cover the error mapping once per class, e.g., malformed input `400`, missing or bad credentials `401`, other user's resource `403`, unknown ID `404`, duplicate `409`. Put the validation rules behind those errors in unit tests.

## Other test types at this level (briefly)

| Type | What it asks | Integration level practice |
|---|---|---|
| Performance | Does it stay fast under expected load, and where does it break? | Load test one endpoint with a real database and a fixed data volume. Keep it out of the per-commit stage. Track p95 against a threshold. |
| Security | Does the system enforce its security requirements? | One test per protected endpoint for missing token `401` and for another tenant's resource `403`. Broken access control has been first in the OWASP Top 10 since 2021. Check SQL injection on raw query paths. |
| Resilience | Does it handle a dependency failing, and does it recover? | Make the stub server return `500`, time out, or drop the connection, and assert the retry count, the circuit breaker state, and that no half-written data remains. Tools such as Toxiproxy inject latency between the app and a real container. |
