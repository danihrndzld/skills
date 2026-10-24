# Static testing and linting policy

## Two forms of static testing

Static testing examines a work product without running it.

- People review it: code reviews, walkthroughs, pull requests, requirement reviews.
- A tool analyzes it: a parser reports code that matches a rule, for example unreachable code, an ignored return value or SQL built by string concatenation.

Both report defects. A failure needs execution, so static testing never sees one.

## The ceiling of static analysis

Static analysis never runs the program and has no idea what the code was supposed to do. Only a test with the right expected result, or a human review, catches a wrong business rule that compiles and lints clean.

| Case | Caught by |
|---|---|
| Unused variable in a function | Linter, error bucket |
| Variable used before assignment | Linter, bug bucket |
| `camelCaseName` in a Python file | Linter, style bucket |
| Docstring says "returns the newest order" but the code returns the last item of an unordered dict | No linter |
| Discount coded as 12% where the spec says 15% | No linter |

ESLint as a concrete profile: it parses each JS or TS file into a tree and matches rules in the editor and again in CI. It answers before the commit, and `--fix` rewrites many findings. It works one file at a time, so a tainted value from another file escapes it.

Static analysis beyond style: SonarQube, CodeQL, Semgrep.

## Linter buckets

The name comes from the Bell Labs `lint` tool of 1978 [23]. Mainstream linters sort findings into three buckets.

| Bucket | Meaning | Pylint example |
|---|---|---|
| Bug | Misuse that changes behavior in an unwanted way | `used-before-assignment` (E) |
| Error | Misuse that keeps behavior but hurts maintainability | `unused-variable` (W) |
| Style | Inconsistent formatting and code smells | `bad-indentation`, `invalid-name` (C, W) |

When time is short, fix bugs first, then errors, then style.

## Tooling by scale and language

| Setup | Shape |
|---|---|
| Enterprise (SonarQube) | A shared dashboard, quality gates that block a merge, a shared rule catalog across more than 30 languages |
| Small team (Ruff, ESLint) | A small config file in the repo, a handful of agreed rules, fast enough to run on every save |

Linters by language: Ruff for Python, ESLint for TypeScript and JavaScript, golangci-lint for Go (runs dozens of linters in one pass), RuboCop for Ruby.

## The ruleset decides the count

On Flask 0.1 (the first tagged release, from 2010), Ruff 0.15.17 reports 22 issues with the default ruleset and 1,023 with `--select ALL`:

```
git clone --depth 1 --branch 0.1 https://github.com/pallets/flask.git
cd flask && uvx ruff check .
uvx ruff check --select ALL .
```

Report the ruleset with every lint count. A count without its ruleset means nothing.

## Adopting a linter on legacy code

For tens of thousands of warnings, use configure, baseline, enforce, divide:

1. Configure the linter to the team's real coding standard.
2. Record today's issue count as the baseline. Do not fix it yet.
3. Enforce on submission. Each PR lowers the count or keeps it, and never raises it.
4. Divide. Exclude code that rarely changes and has no open bugs (for example a `frozen/` directory excluded in config) instead of forcing a fix.

Bugs skip the queue regardless of the baseline. Zero lint issues at all times is a fair rule only for new or actively changing code.

## Reproducible dependencies

Use a lockfile and a tool that resolves from it in CI. For Python, `uv` [19] installs packages, resolves dependencies, builds virtual environments and runs tools. It replaces `pip`, `pip-tools`, `virtualenv` and most daily Poetry work. Astral released it in February 2024. `uvx <tool>` runs a tool in a throwaway environment.

Speed figures (project benchmarks, not independent):

- uv is 8 to 10 times faster than pip and pip-tools without a cache, 80 to 115 times faster with a warm cache, and creates a virtual environment in as little as 4.1 ms, about 80 times faster than `python -m venv`.
- Ruff claims 10 to 100 times faster than Flake8 [20]. A third party report measured Pylint at about 2.5 minutes and Ruff at about 0.4 seconds on the same 250,000 line codebase.

Pinning by version versus by hash is in `delivery.md`.
