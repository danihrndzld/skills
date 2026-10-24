# Framework cheat sheet

Use what the project already has. The table maps the skill's concepts to common tools. Check flags against the runner's own docs for the installed version.

| Tool | Locate by role or test ID | Wait on a condition | Reuse login | Repeat to check stability | JUnit XML |
|---|---|---|---|---|---|
| Playwright (JS/TS) | `page.getByRole('button', { name: 'Pay' })`, `getByLabel`, `getByTestId` | `await expect(locator).toBeVisible()`, `page.waitForResponse(url)` | `storageState` saved in a setup project | `--repeat-each=5` | `--reporter=junit` with `PLAYWRIGHT_JUNIT_OUTPUT_NAME=junit.xml`, or `reporter: [['junit', { outputFile: 'junit.xml' }]]` in config |
| Playwright (Python) | `page.get_by_role("button", name="Pay")` | `expect(locator).to_be_visible()` | `context.storage_state(path=...)` | `pytest --count=5` (pytest-repeat) | `pytest --junitxml=junit.xml` |
| Playwright (Java, .NET) | `getByRole(AriaRole.BUTTON, ...)`, `GetByRole(AriaRole.Button, ...)` | `assertThat(locator).isVisible()`, `Expect(locator).ToBeVisibleAsync()` | `storageState` | JUnit `@RepeatedTest(5)`, NUnit `[Repeat(5)]` | Surefire writes `target/surefire-reports/*.xml`. `dotnet test --logger "junit;LogFilePath=junit.xml"` with `JunitXml.TestLogger`. |
| Cypress | `cy.findByRole('button', { name: 'Pay' })` (Testing Library), `cy.get('[data-testid=pay]')` | `cy.contains('Order confirmed').should('be.visible')`, `cy.wait('@alias')` | `cy.session()` | `--config retries=0` and run the spec 5 times in a loop, or `cypress-repeat` | `--reporter junit --reporter-options "mochaFile=junit-[hash].xml"` |
| Selenium / WebDriver | `By.cssSelector("[data-testid=pay]")`, `By.xpath("//button[normalize-space()='Pay']")` | `WebDriverWait(driver, 10).until(EC.visibility_of_element_located(...))` | inject the session cookie after an API login | the wrapping runner's repeat option | No reporter of its own. Use the wrapping runner: `pytest --junitxml`, JUnit 5 with Surefire, Mocha `--reporter mocha-junit-reporter`. |
| Appium (mobile) | accessibility ID (`AppiumBy.ACCESSIBILITY_ID`) | `WebDriverWait` as in Selenium | deep link or API token injected at launch | the wrapping runner's repeat option | No reporter of its own. Use the wrapping runner (pytest, JUnit, WebdriverIO `@wdio/junit-reporter`). |

Notes:
- Selenium has no role locator. Ask the team to add `data-testid` attributes or use accessible text with a short XPath.
- On mobile, ask developers to set accessibility IDs (`accessibilityIdentifier` on iOS, `contentDescription` on Android). They serve screen readers and tests.
- Cypress names each JUnit file with `[hash]` so parallel specs don't overwrite each other. Pass every file to `build_report.py` with repeated `--junit` flags.
- Playwright's JUnit `name` attribute includes the describe titles. Copy it from the XML when you fill `report.json`.
