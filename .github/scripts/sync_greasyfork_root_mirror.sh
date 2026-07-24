#!/usr/bin/env bash
set -euo pipefail

USER_SOURCE="dist/MissionChief_Map_Command_Toolkit.user.js"
TXT_SOURCE="dist/MissionChief_Map_Command_Toolkit.txt"
SUMS_SOURCE="dist/SHA256SUMS.txt"
MANIFEST_SOURCE="dist/release-manifest.json"
ROOT_USER="MissionChief_Map_Command_Toolkit.user.js"
ROOT_TXT="MissionChief_Map_Command_Toolkit.txt"

for file in "$USER_SOURCE" "$TXT_SOURCE" "$SUMS_SOURCE" "$MANIFEST_SOURCE"; do
  test -f "$file" || {
    echo "::error::Validated distribution file is missing: $file"
    exit 1
  }
done

cmp --silent "$USER_SOURCE" "$TXT_SOURCE" || {
  echo "::error::Validated userscript and text distribution files are not byte-identical."
  exit 1
}

EXPECTED_HASH="$(jq -r '.sha256 // empty' "$MANIFEST_SOURCE")"
[[ -n "$EXPECTED_HASH" ]] || { echo "::error::Validated distribution manifest has no SHA-256."; exit 1; }
[[ "$(sha256sum "$USER_SOURCE" | awk '{print $1}')" == "$EXPECTED_HASH" ]]
[[ "$(sha256sum "$TXT_SOURCE" | awk '{print $1}')" == "$EXPECTED_HASH" ]]

cp "$USER_SOURCE" "$ROOT_USER"
cp "$TXT_SOURCE" "$ROOT_TXT"
cmp --silent "$ROOT_USER" "$ROOT_TXT"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add dist "$ROOT_USER" "$ROOT_TXT"

if ! git diff --cached --quiet; then
  VERSION="$(jq -r '.version' "$MANIFEST_SOURCE")"
  git commit -m "Publish Toolkit ${VERSION} stable distribution source"
  git pull --rebase origin main
  git push origin HEAD:main
else
  echo "Stable dist and Greasy Fork root mirrors already match the validated distribution."
fi

TARGET_SHA="$(git rev-parse HEAD)"
echo "target_sha=${TARGET_SHA}" >> "$GITHUB_OUTPUT"
echo "Stable distribution publication commit: ${TARGET_SHA}"
