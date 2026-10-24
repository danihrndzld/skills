#!/usr/bin/env bash
# Symlink every skill in this repo into ~/.claude/skills and ~/.agents/skills for local development.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
for target in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$target"
  for dir in "$repo"/skills/*/*/; do
    name="$(basename "$dir")"
    dest="$target/$name"
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
      echo "skip $dest (a real folder is there; remove it first)" >&2
      continue
    fi
    ln -sfn "${dir%/}" "$dest"
    echo "linked $dest"
  done
done
