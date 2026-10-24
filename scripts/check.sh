#!/usr/bin/env bash
# Repo invariants. Run before every commit; CI runs it too.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo"
fail=0

echo "== shared report script in sync"
scripts/sync-shared.sh --check || fail=1

echo "== frontmatter name equals folder, and skill is listed in plugin.json and README.md"
for f in skills/*/*/SKILL.md; do
  dir="$(dirname "$f")"
  name="$(basename "$dir")"
  fm="$(sed -n 's/^name: //p' "$f" | head -1)"
  [ "$fm" = "$name" ] || { echo "name mismatch in $f: $fm" >&2; fail=1; }
  grep -q "\"./$dir\"" .claude-plugin/plugin.json || { echo "missing from plugin.json: $dir" >&2; fail=1; }
  grep -q "$dir" README.md || { echo "missing from README.md: $dir" >&2; fail=1; }
done

echo "== no em or en dashes in English prose"
if grep -rn --include='*.md' $'—\|–' README.md CLAUDE.md shared skills/testing skills/*/README.md; then
  echo "dashes found" >&2; fail=1
fi

echo "== report builder tests"
uv run --no-project --with pytest pytest -q shared/report/tests || fail=1

echo "== anti-slop-es self tests"
python3 skills/writing/anti-slop-es/scripts/detectar_slop.py --autotest || fail=1
python3 skills/writing/anti-slop-es/scripts/limpiar_slop.py --autotest || fail=1

exit $fail
