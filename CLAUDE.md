# Repo rules

This repo holds agent skills under `skills/<bucket>/<name>/SKILL.md`. Users install them with `npx skills add danihrndzld/skills`, which copies each chosen skill folder on its own, or as the Claude Code plugin described in `.claude-plugin/`.

- Every skill appears in `README.md` (Reference section), in its bucket `README.md`, and in `.claude-plugin/plugin.json`.
- The frontmatter `name` of each `SKILL.md` equals its folder name.
- A skill never reads files from another skill folder, because a user can install one skill alone.
- The report builder is edited only in `shared/report/build_report.py`. Run `scripts/sync-shared.sh` to copy it into the four testing skills. The copies must stay identical.
- Prose is English and follows the plain-writing rules: plain words, complete sentences, no em or en dashes, no analogies, sentence-case headings. The body and references of `anti-slop-es` stay in Spanish.
- Run `scripts/check.sh` before every commit.
- Use `scripts/link-skills.sh` to point `~/.claude/skills` and `~/.agents/skills` at this repo during development.
- Bump the version in `.claude-plugin/plugin.json` when a skill changes in a way users should pick up.
