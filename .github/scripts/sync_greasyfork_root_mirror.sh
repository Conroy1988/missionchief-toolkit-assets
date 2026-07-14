#!/usr/bin/env bash
set -euo pipefail

USER_SOURCE="dist/MissionChief_Map_Command_Toolkit.user.js"
TXT_SOURCE="dist/MissionChief_Map_Command_Toolkit.txt"
ROOT_USER="MissionChief_Map_Command_Toolkit.user.js"
ROOT_TXT="MissionChief_Map_Command_Toolkit.txt"

for file in "$USER_SOURCE" "$TXT_SOURCE"; do
  test -f "$file" || {
    echo "::error::Validated distribution file is missing: $file"
    exit 1
  }
done

cmp --silent "$USER_SOURCE" "$TXT_SOURCE" || {
  echo "::error::Validated userscript and text distribution files are not byte-identical."
  exit 1
}

cp "$USER_SOURCE" "$ROOT_USER"
cp "$TXT_SOURCE" "$ROOT_TXT"
cmp --silent "$ROOT_USER" "$ROOT_TXT"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add "$ROOT_USER" "$ROOT_TXT"

if ! git diff --cached --quiet; then
  git commit -m "Update stable Greasy Fork source mirror"
  git pull --rebase origin main
  git push origin HEAD:main
else
  echo "Stable Greasy Fork source mirror already matches the validated distribution."
fi

TARGET_SHA="$(git rev-parse HEAD)"
echo "target_sha=${TARGET_SHA}" >> "$GITHUB_OUTPUT"
echo "Stable Greasy Fork source mirror commit: ${TARGET_SHA}"
