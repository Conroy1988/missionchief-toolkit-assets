#!/usr/bin/env bash
set -euo pipefail

: "${RELEASE_VERSION:?RELEASE_VERSION is required}"
: "${GH_TOKEN:?GH_TOKEN is required}"

OUTPUT_DIR="${OUTPUT_DIR:-release-bundle}"
REQUIRE_STABLE_ASSETS="${REQUIRE_STABLE_ASSETS:-true}"
TAG="v${RELEASE_VERSION}"

[[ "$RELEASE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([+-][0-9A-Za-z.-]+)?$ ]] || {
  echo "::error::Invalid release version: ${RELEASE_VERSION}"
  exit 1
}

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

gh release view "$TAG" --json tagName,isDraft,isPrerelease,url > "$OUTPUT_DIR/release.json"
[[ "$(jq -r '.tagName' "$OUTPUT_DIR/release.json")" == "$TAG" ]] || {
  echo "::error::Resolved release tag does not match ${TAG}."
  exit 1
}
[[ "$(jq -r '.isDraft' "$OUTPUT_DIR/release.json")" == "false" ]] || {
  echo "::error::Release ${TAG} is still a draft."
  exit 1
}

gh release download "$TAG" --dir "$OUTPUT_DIR"

VERSIONED_USER="MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.user.js"
VERSIONED_TXT="MissionChief_Map_Command_Toolkit_v${RELEASE_VERSION}.txt"
STABLE_USER="MissionChief_Map_Command_Toolkit.user.js"
STABLE_TXT="MissionChief_Map_Command_Toolkit.txt"
MANIFEST="release-manifest-v${RELEASE_VERSION}.json"
CHANGELOG="CHANGELOG-v${RELEASE_VERSION}.md"
SUMS="SHA256SUMS-v${RELEASE_VERSION}.txt"
HANDOVER="migration-handover-v${RELEASE_VERSION}.md"

required=("$VERSIONED_USER" "$VERSIONED_TXT" "$MANIFEST" "$CHANGELOG" "$SUMS" "$HANDOVER")
if [[ "$REQUIRE_STABLE_ASSETS" == "true" ]]; then
  required+=("$STABLE_USER" "$STABLE_TXT")
fi

for file in "${required[@]}"; do
  [[ -f "$OUTPUT_DIR/$file" ]] || {
    echo "::error::Release ${TAG} is missing required asset: ${file}"
    exit 1
  }
done

cmp --silent "$OUTPUT_DIR/$VERSIONED_USER" "$OUTPUT_DIR/$VERSIONED_TXT" || {
  echo "::error::Versioned userscript and text assets are not byte-identical."
  exit 1
}

EXPECTED_HASH="$(jq -r '.sha256 // empty' "$OUTPUT_DIR/$MANIFEST")"
MANIFEST_VERSION="$(jq -r '.version // empty' "$OUTPUT_DIR/$MANIFEST")"
ACTUAL_HASH="$(sha256sum "$OUTPUT_DIR/$VERSIONED_USER" | awk '{print $1}')"
SCRIPT_VERSION="$(sed -nE 's|^//[[:space:]]*@version[[:space:]]+(.+)$|\1|p' "$OUTPUT_DIR/$VERSIONED_USER" | head -n 1 | xargs)"

[[ "$MANIFEST_VERSION" == "$RELEASE_VERSION" ]] || {
  echo "::error::Release manifest version ${MANIFEST_VERSION:-missing} does not match ${RELEASE_VERSION}."
  exit 1
}
[[ -n "$EXPECTED_HASH" && "$EXPECTED_HASH" == "$ACTUAL_HASH" ]] || {
  echo "::error::Versioned release asset SHA-256 does not match the manifest."
  exit 1
}
[[ "$SCRIPT_VERSION" == "$RELEASE_VERSION" ]] || {
  echo "::error::Versioned userscript @version ${SCRIPT_VERSION:-missing} does not match ${RELEASE_VERSION}."
  exit 1
}

grep -Fq "$EXPECTED_HASH" "$OUTPUT_DIR/$SUMS" || {
  echo "::error::Versioned SHA256SUMS does not contain the verified release hash."
  exit 1
}

if [[ -f "$OUTPUT_DIR/$STABLE_USER" || -f "$OUTPUT_DIR/$STABLE_TXT" ]]; then
  [[ -f "$OUTPUT_DIR/$STABLE_USER" && -f "$OUTPUT_DIR/$STABLE_TXT" ]] || {
    echo "::error::Only one stable release asset is present."
    exit 1
  }
  cmp --silent "$OUTPUT_DIR/$STABLE_USER" "$OUTPUT_DIR/$STABLE_TXT" || {
    echo "::error::Stable userscript and text assets are not byte-identical."
    exit 1
  }
  STABLE_HASH="$(sha256sum "$OUTPUT_DIR/$STABLE_USER" | awk '{print $1}')"
  [[ "$STABLE_HASH" == "$EXPECTED_HASH" ]] || {
    echo "::error::Stable release asset SHA-256 does not match the immutable versioned asset."
    exit 1
  }
fi

jq -n \
  --arg version "$RELEASE_VERSION" \
  --arg tag "$TAG" \
  --arg sha256 "$EXPECTED_HASH" \
  --arg output "$OUTPUT_DIR" \
  --arg releaseUrl "$(jq -r '.url' "$OUTPUT_DIR/release.json")" \
  '{version:$version,tag:$tag,sha256:$sha256,outputDirectory:$output,releaseUrl:$releaseUrl,verified:true}' \
  > "$OUTPUT_DIR/recovery-verification.json"

echo "release_version=${RELEASE_VERSION}" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "release_sha256=${EXPECTED_HASH}" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "release_url=$(jq -r '.url' "$OUTPUT_DIR/release.json")" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "Verified immutable release bundle ${TAG} (${EXPECTED_HASH})."
