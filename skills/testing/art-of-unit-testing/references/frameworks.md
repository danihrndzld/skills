# Framework cheat sheet

Use what the project already has. This table only maps the skill's concepts to common syntax.

| Language | Framework | Parametrized | Expect error | Stub / mock |
|---|---|---|---|---|
| Python | pytest | `@pytest.mark.parametrize` | `with pytest.raises(E):` | hand-written fake, `unittest.mock.Mock(return_value=…)`; verify: `mock.assert_called_once_with(…)` |
| JS/TS | Jest / Vitest | `it.each` / `test.each` | `expect(() => f()).toThrow(E)` / `await expect(p).rejects.toThrow()` | `vi.fn()/jest.fn().mockReturnValue(…)`; verify: `toHaveBeenCalledWith` |
| Java | JUnit 5 + Mockito | `@ParameterizedTest` + `@CsvSource`/`@MethodSource` | `assertThrows(E.class, () -> …)` | `when(x.get()).thenReturn(…)`; verify: `verify(bus).send(…)` |
| Kotlin | JUnit 5 / Kotest + MockK | `@ParameterizedTest` / `withData` | `assertThrows<E> { }` / `shouldThrow<E>` | `every { } returns …`; `verify { }` |
| C# | xUnit + NSubstitute/Moq | `[Theory]` + `[InlineData]` | `Assert.Throws<E>(() => …)` | `sub.Get().Returns(…)`; `sub.Received(1).Send(…)` |
| Go | `testing` (+ testify) | table-driven `for _, tc := range cases { t.Run(tc.name, …) }` (the one sanctioned loop: it only dispatches, no logic) | check returned `err` with `errors.Is` | hand-written struct implementing the interface |
| Rust | built-in `#[test]` (+ rstest, mockall) | `#[rstest] #[case(…)]` | `assert!(matches!(r, Err(E::…)))` / `#[should_panic]` | trait + test impl, or `mockall` |
| Swift | XCTest / Swift Testing | `@Test(arguments:)` | `XCTAssertThrowsError` / `#expect(throws:)` | protocol + test double |
| PHP | PHPUnit | `#[DataProvider]` | `$this->expectException(E::class)` | `createStub` / `createMock` + `expects($this->once())` |
| Ruby | RSpec | shared examples / table with `each` at describe level | `expect { }.to raise_error(E)` | `double(get: …)`; `expect(bus).to receive(:send).with(…)` |
| COBOL | zUnit / COBOL-Check | one test case per input row | assert on RETURN-CODE / status field | stub the called program / file I/O |

Notes:
- Prefer hand-written fakes when they are shorter than mock-library setup; they survive refactoring better.
- Go table tests and RSpec iteration at the describe level are parametrization, not test logic: the loop body must only call the shared test function.
- Async: await the Act; never `sleep` to wait. Use fake timers / injected clocks.
