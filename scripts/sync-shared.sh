#!/usr/bin/env bash
# Copy shared/report/build_report.py into every testing skill. With --check, fail if any copy differs.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
src="$repo/shared/report/build_report.py"
status=0
for dir in "$repo"/skills/testing/*/; do
  dest="$dir/scripts/build_report.py"
  if [ "${1:-}" = "--check" ]; then
    if ! cmp -s "$src" "$dest"; then
      echo "out of sync: ${dest#"$repo"/}" >&2
      status=1
    fi
  else
    mkdir -p "$dir/scripts"
    cp "$src" "$dest"
    echo "copied ${dest#"$repo"/}"
  fi
done
exit $status
