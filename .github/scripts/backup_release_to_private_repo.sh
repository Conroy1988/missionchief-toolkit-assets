#!/usr/bin/env bash
set -euo pipefail

: "${RELEASE_VERSION:?RELEASE_VERSION is required}"
: "${MIGRATION_REPO_TOKEN:?MIGRATION_REPO_TOKEN is required}"

PRIVATE_REPO="Conroy1988/missionchief-map-command-toolkit-private"
PRIVATE_URL="https://github.com/${PRIVATE_REPO}.git"
SOURCE_REPO="${GITHUB_REPOSITORY}"
SOURCE_COMMIT="${GITHUB_SHA}"
RELEASE_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/releases/tag/v${RELEASE_VERSION}"
BUNDLE_DIR="release-bundle"
TARGET_ROOT="releases/v${RELEASE_VERSION}"
WORK_DIR="$(mktemp -d)"
PRIVATE_DIR="${WORK_DIR}/private"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

required=(
  "MissionChief_Map_Command_Toolkit.user.js"
  "MissionChief_Map_Command_Toolkit.txt"
  "MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.user.js"
  "MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.txt"
  "CHANGELOG-v${RELEASE_VERSION}.md"
  "release-manifest-v${RELEASE_VERSION}.json"
  "SHA256SUMS-v${RELEASE_VERSION}.txt"
  "migration-handover-v${RELEASE_VERSION}.md"
)

for file in "${required[@]}"; do
  test -f "${BUNDLE_DIR}/${file}" || {
    echo "::error::Required backup file is missing: ${BUNDLE_DIR}/${file}"
    exit 1
  }
done

cmp --silent \
  "${BUNDLE_DIR}/MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.user.js" \
  "${BUNDLE_DIR}/MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.txt"

EXPECTED_HASH="$(jq -r '.sha256' "${BUNDLE_DIR}/release-manifest-v${RELEASE_VERSION}.json")"
ACTUAL_HASH="$(sha256sum "${BUNDLE_DIR}/MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.user.js" | awk '{print $1}')"
test "$EXPECTED_HASH" = "$ACTUAL_HASH"

HTTP_CODE="$(curl --silent --show-error --output "${WORK_DIR}/private-repo-check.json" --write-out '%{http_code}' \
  --header "Authorization: Bearer ${MIGRATION_REPO_TOKEN}" \
  --header "Accept: application/vnd.github+json" \
  --header "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${PRIVATE_REPO}")"

if [[ "$HTTP_CODE" != "200" ]]; then
  MESSAGE="$(jq -r '.message // "Unknown GitHub API error"' "${WORK_DIR}/private-repo-check.json" 2>/dev/null || true)"
  echo "::error::MIGRATION_REPO_TOKEN cannot access ${PRIVATE_REPO} (HTTP ${HTTP_CODE}: ${MESSAGE})."
  exit 1
fi

[[ "$(jq -r '.permissions.push // false' "${WORK_DIR}/private-repo-check.json")" == "true" ]] || {
  echo "::error::MIGRATION_REPO_TOKEN does not have push permission for ${PRIVATE_REPO}."
  exit 1
}

BASIC_AUTH="$(printf 'x-access-token:%s' "$MIGRATION_REPO_TOKEN" | base64 -w0)"
git -c http.extraheader="AUTHORIZATION: basic ${BASIC_AUTH}" clone --depth 1 "$PRIVATE_URL" "$PRIVATE_DIR"
cd "$PRIVATE_DIR"
git config http."https://github.com/".extraheader "AUTHORIZATION: basic ${BASIC_AUTH}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

if [[ -e "$TARGET_ROOT" ]]; then
  echo "::error::Private backup path already exists: $TARGET_ROOT"
  exit 1
fi

mkdir -p "$TARGET_ROOT" current
cp -a "${GITHUB_WORKSPACE}/${BUNDLE_DIR}/." "$TARGET_ROOT/"
cp "${GITHUB_WORKSPACE}/status/release-dashboard.json" "$TARGET_ROOT/release-dashboard.json"

jq -n \
  --arg project "MissionChief Map Command Toolkit" \
  --arg version "$RELEASE_VERSION" \
  --arg sourceRepository "$SOURCE_REPO" \
  --arg sourceCommit "$SOURCE_COMMIT" \
  --arg releaseUrl "$RELEASE_URL" \
  --arg sha256 "$ACTUAL_HASH" \
  --arg backedUpAt "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  '{project:$project,version:$version,sourceRepository:$sourceRepository,sourceCommit:$sourceCommit,githubRelease:$releaseUrl,sha256:$sha256,greasyForkVerified:true,filesValidated:true,textCopyByteIdentical:true,backedUpAt:$backedUpAt}' > "$TARGET_ROOT/backup-record.json"

rm -rf current/release
mkdir -p current/release
cp -a "$TARGET_ROOT/." current/release/
printf '%s\n' "v${RELEASE_VERSION}" > current/VERSION
printf '%s\n' "$ACTUAL_HASH" > current/SHA256

cat > current/RELEASE_POINTER.md <<EOF
# Current validated Toolkit release

- Version: **v${RELEASE_VERSION}**
- Source repository: \`${SOURCE_REPO}\`
- Source commit: \`${SOURCE_COMMIT}\`
- SHA-256: \`${ACTUAL_HASH}\`
- GitHub Release: ${RELEASE_URL}
- Private archive: \`${TARGET_ROOT}/\`

The complete validated release is mirrored in \`current/release/\` for rapid recovery.
EOF

git add "$TARGET_ROOT" current

if git diff --cached --quiet; then
  echo "::error::Private backup produced no repository changes."
  exit 1
fi

git commit -m "Back up Toolkit v${RELEASE_VERSION} validated release"
git push origin HEAD:main
BACKUP_COMMIT="$(git rev-parse HEAD)"

echo "backup_commit=${BACKUP_COMMIT}" >> "$GITHUB_OUTPUT"
echo "backup_repository=${PRIVATE_REPO}" >> "$GITHUB_OUTPUT"
echo "Private migration backup committed: ${BACKUP_COMMIT}"
