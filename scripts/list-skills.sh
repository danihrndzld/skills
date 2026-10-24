#!/usr/bin/env bash
# Print every skill as bucket/name with its description.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$repo"/skills/*/*/SKILL.md; do
  rel="${f#"$repo"/skills/}"
  desc="$(sed -n 's/^description: //p' "$f" | head -1 | cut -c1-110)"
  printf '%-40s %s\n' "${rel%/SKILL.md}" "$desc"
done
