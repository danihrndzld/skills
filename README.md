# Skills for testing and writing

These are the agent skills I use for testing software and for writing. They work with Claude Code, Codex, Cursor and the other agents that read `SKILL.md` files.

There are four testing skills, one for each level of testing and one for the pipeline that runs them. Each one tells the agent which tests are worth writing, how to write them so they fail only when behavior breaks, and how to prove that each test can fail. Each one can also turn the results into an HTML report, a PDF and an email summary, with the JUnit XML from your test runner attached, and you choose which of those files go to your CI artifacts and to an email. There are also two writing skills, one that removes AI writing patterns from Spanish text and one for writing exams.

## Installation

Pick one route per agent, because installing both gives you every skill twice.

<details>
<summary><strong>Any agent, with the skills CLI</strong> (pick the skills you want)</summary>

```bash
npx skills@latest add danihrndzld/skills
```

The installer shows a list of the six skills, and you pick the ones you want with the space bar. Add `--global` to install them for every project, or `--skill art-of-unit-testing` to skip the list and install one skill. To update, run `npx skills@latest update`.

</details>

<details>
<summary><strong>Claude Code, as a plugin</strong> (installs all six and updates itself)</summary>

```bash
claude plugin marketplace add danihrndzld/skills
claude plugin install danihrndzld-skills@danihrndzld
```

</details>

<details>
<summary><strong>By hand, with git</strong></summary>

```bash
git clone https://github.com/danihrndzld/skills ~/src/danihrndzld-skills
~/src/danihrndzld-skills/scripts/link-skills.sh
```

The script links every skill folder into `~/.claude/skills` and `~/.agents/skills`. Run `git pull` to update.

</details>

After you install, restart your agent. The agent loads a skill on its own when your request matches the skill's description, and you can also call a skill by name. Skills installed with `npx skills` are called as `/art-of-unit-testing`. With the Claude Code plugin they are namespaced, as in `/danihrndzld-skills:art-of-unit-testing`.

## Why these skills exist

### Agents write too many weak tests

When you ask an agent for tests, it often writes a test for every getter, mocks every class, and checks calls that only exist inside the code. Those tests break when someone refactors the code, and they still pass when a real bug comes in. The testing skills make the agent sort the code first, so it tests domain logic, skips trivial code, and sends orchestration code to integration tests. The agent then writes one test for each observable result and breaks the production code on purpose to confirm that each test fails.

### Test results stay in the terminal

A passing test run is hard to share with a team lead, an auditor or a client. Each testing skill includes the same report builder, which reads the JUnit XML from your test runner, the coverage file, and a short `report.json` that the agent writes with its reasoning. The builder checks that every test the agent lists exists in the JUnit file and in the source code at the line it names, and then it writes the report.

### AI text in Spanish reads like AI text

The `anti-slop-es` skill measures how often AI writing patterns appear in a Spanish text, and it rewrites the parts that go over the limit.

## Reference

### Testing

- [art-of-unit-testing](./skills/testing/art-of-unit-testing/SKILL.md): writes few unit tests with high signal in any language, using entry and exit points, functional requirements, real collaborators instead of mocks, and a check that breaks the code to confirm that each test fails.
- [art-of-integration-testing](./skills/testing/art-of-integration-testing/SKILL.md): tests controllers, services and API endpoints against a real database that only your app uses, with mocks only for outside systems such as email or a message bus.
- [art-of-e2e-testing](./skills/testing/art-of-e2e-testing/SKILL.md): covers the few user journeys that carry the most risk, through the browser or the public API, with rules that keep the tests stable.
- [art-of-cicd](./skills/testing/art-of-cicd/SKILL.md): designs and reviews pipelines, quality gates, flaky test handling, suite speed, trunk-based development, DORA metrics and deployment strategies.

### Writing

- [anti-slop-es](./skills/writing/anti-slop-es/SKILL.md): finds and removes AI writing patterns in Spanish text, code and slides, using density limits instead of lists of banned words. Its content is in Spanish.
- [exam-writing](./skills/writing/exam-writing/SKILL.md): writes, reviews and versions exams and quizzes, and reads item analysis after the exam.

## Reports

Each testing skill has a copy of `scripts/build_report.py`, which needs only Python 3.10 or later. Google Chrome, Chromium, Edge or Brave is needed for the PDF. The agent writes `report.json` and runs the script from the skill's own folder by its absolute path, because the skill may be installed in the project's `.claude/skills`, globally in `~/.claude/skills` or `~/.agents/skills`, or inside a plugin. You choose the output files with `--formats`.

```bash
python3 ~/.claude/skills/art-of-unit-testing/scripts/build_report.py test-reports/2026-10-24-rates/report.json \
  --junit junit.xml --coverage coverage.json --formats html,pdf,summary
```

| File | What it is | Typical use |
|---|---|---|
| `junit.xml` | The JUnit XML from your test runner, copied into the report folder | CI test tabs and dashboards |
| `report.html` | The full report, readable in a browser in light or dark mode | CI artifact or a page in your docs |
| `report.pdf` | The same report on A4 pages, with page numbers and bookmarks | Email attachment or audit record |
| `summary.html` | A short summary with inline styles that email clients can show | Email body |

Each skill's `references/report.md` has a GitHub Actions example that uploads the report folder as an artifact and sends the summary by email with the PDF attached. You decide which files to upload and which files to attach. The build step runs with `if: always()` and `--ci`, so a failing test step does not stop the job before the report is built, and new failures show up in an Undocumented results section instead of a validation error. That example calls `.claude/skills/<skill>/scripts/build_report.py`, which exists in CI only when the skill is installed at project level (`npx skills add danihrndzld/skills --skill <skill>`, with the folder committed) or when you commit a copy of the script to the repo.

## Local development

Clone the repo and run `scripts/link-skills.sh`, so your agent uses the files in the repo. The report builder lives in `shared/report/`, and `scripts/sync-shared.sh` copies it into each testing skill. Run `scripts/check.sh` before you commit, because CI runs the same checks.

## Sources

The testing skills are based on the sources below. References [1] and [2] shaped art-of-unit-testing and the rules for test doubles in the integration skill. Reference [3] shaped art-of-cicd, and [4] covers the agile practices behind the pipeline and testing advice. Reference [5] is the basis for the test design techniques, test levels and test types in all four testing skills. Each skill lists more specific sources in its `references` folder, for example `skills/testing/art-of-cicd/references/sources.md`.

[1] R. Osherove and V. Khorikov, *The Art of Unit Testing: With Examples in JavaScript*, 3rd ed. Shelter Island, NY, USA: Manning Publications, 2024.

[2] V. Khorikov, *Unit Testing: Principles, Practices, and Patterns*. Shelter Island, NY, USA: Manning Publications, 2020.

[3] G. Kim, J. Humble, P. Debois, J. Willis, and N. Forsgren, *The DevOps Handbook: How to Create World-Class Agility, Reliability, and Security in Technology Organizations*, 2nd ed. Portland, OR, USA: IT Revolution Press, 2021.

[4] P. Flewelling, *The Agile Developer's Handbook: Get More Value from Your Software Development: Get the Best Out of the Agile Methodology*. Birmingham, U.K.: Packt Publishing, 2018.

[5] International Software Testing Qualifications Board, "Certified Tester Foundation Level (CTFL) syllabus," v4.0.1, Sep. 15, 2024. [Online]. Available: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf

## License

MIT
