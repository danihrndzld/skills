# Framework cheat sheet

Use what the project already has. The table maps the skill's concepts to common tools. Check flags against the runner's own docs for the installed version.

| Stack | Real database | In-process app or HTTP client | Data reset | JUnit XML |
|---|---|---|---|---|
| Python, pytest | `testcontainers.postgres.PostgresContainer` in a `scope="session"` fixture | FastAPI `TestClient`, Flask `app.test_client()`, Django `Client` | function fixture that opens a transaction and rolls back, or `pytest-django` `transaction=False` | `pytest --junitxml=junit.xml` |
| Java, Spring Boot | `@Testcontainers` + `@Container static PostgreSQLContainer` + `@ServiceConnection` | `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate`, or `@AutoConfigureMockMvc` | `@Transactional` on the test class for MockMvc. Truncate for `RANDOM_PORT`, because the server uses another thread. | Maven Surefire or Failsafe writes `target/surefire-reports/*.xml` with no flag. Gradle writes `build/test-results/test/*.xml`. |
| C#, ASP.NET Core | `Testcontainers.PostgreSql` started in an `IAsyncLifetime` fixture | `WebApplicationFactory<Program>` with `ConfigureTestServices` to swap unmanaged adapters | Respawn before each test | `dotnet test --logger "junit;LogFilePath=junit.xml"` (needs the `JunitXml.TestLogger` package) |
| JS/TS, Node | `@testcontainers/postgresql` in `globalSetup` | `supertest(app)` | truncate in `beforeEach` | Vitest `--reporter=junit --outputFile=junit.xml`. Jest with `jest-junit` and `JEST_JUNIT_OUTPUT_FILE=junit.xml`. |
| Go | `testcontainers-go` modules, started in `TestMain` | `httptest.NewServer(handler)` or `httptest.NewRecorder()` | transaction per test, or truncate | `gotestsum --junitfile junit.xml` |

Stub servers for other teams' HTTP APIs: WireMock (JVM, also as a container), MockServer, `httptest.NewServer` (Go), `nock` or `msw` (Node), `respx` (Python httpx), `responses` (Python requests).

Notes:
- Mark integration tests so the pipeline can select them: pytest `@pytest.mark.integration`, JUnit 5 `@Tag("integration")` or Failsafe `*IT` classes, xUnit `[Trait("Category", "Integration")]`, Go build tag `//go:build integration`, Vitest a separate `vitest.integration.config.ts`.
- Testcontainers' reuse mode keeps containers between local runs. Keep it off in CI.
