# Issue #86 release-to-Pages inspection

## `.github/workflows/actions-security-audit.yml`

```text
0017:       - ".github/dependabot.yml"
0018:       - ".github/scripts/audit_actions_security.py"
0019:       - ".github/workflows/**"
0020:   schedule:
0021:     - cron: "41 5 * * 1"
0022:   workflow_dispatch:
0023: 
0024: permissions:
0025:   contents: read
0026: 
0027: jobs:
0028:   audit:
0029:     runs-on: ubuntu-latest
0030:     timeout-minutes: 10
```

## `.github/workflows/asset-health-monitor.yml`

```text
0010:       - ".github/ASSET_HEALTH.md"
0011:       - ".github/scripts/check_asset_health.py"
0012:       - ".github/scripts/check_distribution_body_parity.py"
0013:       - ".github/scripts/test_asset_health.py"
0014:       - ".github/workflows/asset-health-monitor.yml"
0015:       - "status/release-dashboard.json"
0016:       - "**/*.mp3"
0017:       - "**/*.wav"
0018:       - "**/*.ogg"
0019:       - "**/*.png"
0020:       - "**/*.jpg"
0021:       - "**/*.jpeg"
0022:       - "**/*.gif"
0023:       - "**/*.webp"

---

0032:       - ".github/ASSET_HEALTH.md"
0033:       - ".github/scripts/check_asset_health.py"
0034:       - ".github/scripts/check_distribution_body_parity.py"
0035:       - ".github/scripts/test_asset_health.py"
0036:       - ".github/workflows/asset-health-monitor.yml"
0037:       - "status/release-dashboard.json"
0038:       - "**/*.mp3"
0039:       - "**/*.wav"
0040:       - "**/*.ogg"
0041:       - "**/*.png"
0042:       - "**/*.jpg"
0043:       - "**/*.jpeg"
0044:       - "**/*.gif"
0045:       - "**/*.webp"

---

0044:       - "**/*.gif"
0045:       - "**/*.webp"
0046:       - "**/*.svg"
0047:   schedule:
0048:     - cron: "17 */6 * * *"
0049:   workflow_dispatch:
0050: 
0051: permissions:
0052:   contents: read
0053:   issues: write
0054: 
0055: concurrency:
0056:   group: ${{ github.event_name == 'pull_request' && format('toolkit-asset-health-pr-{0}', github.event.pull_request.number) || 'toolkit-production-coordination' }}
0057:   cancel-in-progress: false
```

## `.github/workflows/branch-cleanup-audit.yml`

```text
0003: run-name: Branch cleanup candidates
0004: 
0005: on:
0006:   schedule:
0007:     - cron: "11 6 * * 1"
0008:   workflow_dispatch:
0009: 
0010: permissions:
0011:   contents: read
0012:   pull-requests: read
0013: 
0014: jobs:
0015:   audit:
0016:     runs-on: ubuntu-latest
```

## `.github/workflows/code-integrity-audit.yml`

```text
0016:       - "src/MissionChief_Map_Command_Toolkit.user.js"
0017:       - ".github/code-integrity-policy.json"
0018:       - ".github/scripts/check_code_integrity.py"
0019:       - ".github/scripts/test_code_integrity.py"
0020:       - ".github/workflows/code-integrity-audit.yml"
0021:   workflow_dispatch:
0022: 
0023: permissions:
0024:   contents: read
0025: 
0026: concurrency:
0027:   group: toolkit-code-integrity-${{ github.event_name == 'pull_request' && github.event.pull_request.number || github.ref }}
0028:   cancel-in-progress: true
0029: 
```

## `.github/workflows/documentation-drift-check.yml`

```text
0010:       - ".github/scripts/check_documentation_drift.py"
0011:       - ".github/scripts/test_documentation_version_states.py"
0012:       - ".github/workflows/documentation-drift-check.yml"
0013:       - ".github/release-settings.json"
0014:       - "docs/site-data.json"
0015:       - "status/release-dashboard.json"
0016:       - "src/MissionChief_Map_Command_Toolkit.user.js"
0017:       - "CHANGELOG.md"
0018:       - "README.md"
0019:   push:
0020:     branches:
0021:       - main
0022:     paths:
0023:       - ".github/documentation-contract.json"

---

0025:       - ".github/scripts/check_documentation_drift.py"
0026:       - ".github/scripts/test_documentation_version_states.py"
0027:       - ".github/workflows/documentation-drift-check.yml"
0028:       - ".github/release-settings.json"
0029:       - "docs/site-data.json"
0030:       - "status/release-dashboard.json"
0031:       - "src/MissionChief_Map_Command_Toolkit.user.js"
0032:       - "CHANGELOG.md"
0033:       - "README.md"
0034:   schedule:
0035:     - cron: "23 4 * * 3"
0036:   workflow_dispatch:
0037: 
0038: permissions:

---

0031:       - "src/MissionChief_Map_Command_Toolkit.user.js"
0032:       - "CHANGELOG.md"
0033:       - "README.md"
0034:   schedule:
0035:     - cron: "23 4 * * 3"
0036:   workflow_dispatch:
0037: 
0038: permissions:
0039:   contents: read
0040: 
0041: concurrency:
0042:   group: documentation-drift-${{ github.event_name == 'pull_request' && github.event.pull_request.number || github.ref }}
0043:   cancel-in-progress: ${{ github.event_name == 'pull_request' }}
0044: 
```

## `.github/workflows/full-userscript-audit.yml`

```text
0029:       - ".github/scripts/test_settings_ui_contract.py"
0030:       - ".github/scripts/test_desktop_panel_layout_contract.py"
0031:       - ".github/scripts/test_mission_value_contract.py"
0032:       - ".github/scripts/test_transport_sweep_lssm_contract.py"
0033:       - ".github/workflows/full-userscript-audit.yml"
0034:   workflow_dispatch:
0035: 
0036: permissions:
0037:   contents: read
0038: 
0039: concurrency:
0040:   group: toolkit-full-userscript-audit-${{ github.event.pull_request.number || github.ref }}
0041:   cancel-in-progress: true
0042: 
```

## `.github/workflows/github-pages.yml`

```text
0001: name: GitHub Pages Documentation
0002: 
0003: run-name: Documentation site · ${{ github.event_name }}
0004: 
0005: on:
0006:   pull_request:
0007:     paths:
0008:       - ".github/scripts/build_pages_site.py"
0009:       - ".github/scripts/test_pages_release_deploy_contract.py"

---

0005: on:
0006:   pull_request:
0007:     paths:
0008:       - ".github/scripts/build_pages_site.py"
0009:       - ".github/scripts/test_pages_release_deploy_contract.py"
0010:       - ".github/workflows/github-pages.yml"
0011:       - ".github/release-settings.json"
0012:       - "docs/site-data.json"
0013:       - "docs/site-assets/**"
0014:       - "docs/SITE.md"
0015:       - "docs/media/**"
0016:       - "status/release-dashboard.json"
0017:       - "CHANGELOG.md"
0018:       - "README.md"

---

0011:       - ".github/release-settings.json"
0012:       - "docs/site-data.json"
0013:       - "docs/site-assets/**"
0014:       - "docs/SITE.md"
0015:       - "docs/media/**"
0016:       - "status/release-dashboard.json"
0017:       - "CHANGELOG.md"
0018:       - "README.md"
0019:   push:
0020:     branches:
0021:       - main
0022:     paths:
0023:       - ".github/scripts/build_pages_site.py"
0024:       - ".github/scripts/test_pages_release_deploy_contract.py"

---

0020:     branches:
0021:       - main
0022:     paths:
0023:       - ".github/scripts/build_pages_site.py"
0024:       - ".github/scripts/test_pages_release_deploy_contract.py"
0025:       - ".github/workflows/github-pages.yml"
0026:       - ".github/release-settings.json"
0027:       - "docs/site-data.json"
0028:       - "docs/site-assets/**"
0029:       - "docs/SITE.md"
0030:       - "docs/media/**"
0031:       - "status/release-dashboard.json"
0032:       - "CHANGELOG.md"
0033:       - "README.md"

---

0026:       - ".github/release-settings.json"
0027:       - "docs/site-data.json"
0028:       - "docs/site-assets/**"
0029:       - "docs/SITE.md"
0030:       - "docs/media/**"
0031:       - "status/release-dashboard.json"
0032:       - "CHANGELOG.md"
0033:       - "README.md"
0034:   release:
0035:     types:
0036:       - published
0037:   workflow_dispatch:
0038: 
0039: permissions:

---

0032:       - "CHANGELOG.md"
0033:       - "README.md"
0034:   release:
0035:     types:
0036:       - published
0037:   workflow_dispatch:
0038: 
0039: permissions:
0040:   contents: read
0041: 
0042: concurrency:
0043:   group: ${{ github.event_name == 'pull_request' && format('toolkit-pages-pr-{0}', github.event.pull_request.number) || 'toolkit-pages-production' }}
0044:   cancel-in-progress: true
0045: 

---

0106:       contents: read
0107:       pages: write
0108:       id-token: write
0109: 
0110:     environment:
0111:       name: github-pages
0112:       url: ${{ steps.deployment.outputs.page_url }}
0113: 
0114:     steps:
0115:       - name: Check out current production source
0116:         uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7
0117:         with:
0118:           ref: main
0119:           fetch-depth: 1

---

0128:           set -euo pipefail
0129:           EXPECTED_VERSION="${EXPECTED_TAG#v}"
0130:           for ATTEMPT in $(seq 1 40); do
0131:             git fetch --no-tags --depth=1 origin main
0132:             git reset --hard origin/main
0133:             DASHBOARD_VERSION="$(jq -r '.latestRelease.version // empty' status/release-dashboard.json)"
0134:             RELEASE_STATE="$(jq -r '.status.githubRelease // empty' status/release-dashboard.json)"
0135:             GREASY_FORK_STATE="$(jq -r '.status.greasyForkSync // empty' status/release-dashboard.json)"
0136:             if [[ -z "$EXPECTED_VERSION" ]]; then
0137:               EXPECTED_VERSION="$DASHBOARD_VERSION"
0138:             fi
0139:             if [[ -n "$EXPECTED_VERSION" && "$DASHBOARD_VERSION" == "$EXPECTED_VERSION" && "$RELEASE_STATE" == "published" && "$GREASY_FORK_STATE" == "verified" ]]; then
0140:               SOURCE_SHA="$(git rev-parse HEAD)"
0141:               echo "release_version=$EXPECTED_VERSION" >> "$GITHUB_OUTPUT"

---

0129:           EXPECTED_VERSION="${EXPECTED_TAG#v}"
0130:           for ATTEMPT in $(seq 1 40); do
0131:             git fetch --no-tags --depth=1 origin main
0132:             git reset --hard origin/main
0133:             DASHBOARD_VERSION="$(jq -r '.latestRelease.version // empty' status/release-dashboard.json)"
0134:             RELEASE_STATE="$(jq -r '.status.githubRelease // empty' status/release-dashboard.json)"
0135:             GREASY_FORK_STATE="$(jq -r '.status.greasyForkSync // empty' status/release-dashboard.json)"
0136:             if [[ -z "$EXPECTED_VERSION" ]]; then
0137:               EXPECTED_VERSION="$DASHBOARD_VERSION"
0138:             fi
0139:             if [[ -n "$EXPECTED_VERSION" && "$DASHBOARD_VERSION" == "$EXPECTED_VERSION" && "$RELEASE_STATE" == "published" && "$GREASY_FORK_STATE" == "verified" ]]; then
0140:               SOURCE_SHA="$(git rev-parse HEAD)"
0141:               echo "release_version=$EXPECTED_VERSION" >> "$GITHUB_OUTPUT"
0142:               echo "source_sha=$SOURCE_SHA" >> "$GITHUB_OUTPUT"

---

0130:           for ATTEMPT in $(seq 1 40); do
0131:             git fetch --no-tags --depth=1 origin main
0132:             git reset --hard origin/main
0133:             DASHBOARD_VERSION="$(jq -r '.latestRelease.version // empty' status/release-dashboard.json)"
0134:             RELEASE_STATE="$(jq -r '.status.githubRelease // empty' status/release-dashboard.json)"
0135:             GREASY_FORK_STATE="$(jq -r '.status.greasyForkSync // empty' status/release-dashboard.json)"
0136:             if [[ -z "$EXPECTED_VERSION" ]]; then
0137:               EXPECTED_VERSION="$DASHBOARD_VERSION"
0138:             fi
0139:             if [[ -n "$EXPECTED_VERSION" && "$DASHBOARD_VERSION" == "$EXPECTED_VERSION" && "$RELEASE_STATE" == "published" && "$GREASY_FORK_STATE" == "verified" ]]; then
0140:               SOURCE_SHA="$(git rev-parse HEAD)"
0141:               echo "release_version=$EXPECTED_VERSION" >> "$GITHUB_OUTPUT"
0142:               echo "source_sha=$SOURCE_SHA" >> "$GITHUB_OUTPUT"
0143:               echo "Deploying verified Toolkit ${EXPECTED_VERSION} from ${SOURCE_SHA}."
```

## `.github/workflows/greasyfork-release-monitor.yml`

```text
0001: name: Greasy Fork Release Fallback Monitor
0002: 
0003: on:
0004:   schedule:
0005:     - cron: "3-58/5 * * * *"
0006:   workflow_dispatch:
0007: 
0008: permissions:
0009:   contents: write
0010: 
0011: concurrency:
0012:   group: toolkit-production-release
0013:   cancel-in-progress: false
0014: 

---

0030:         shell: bash
0031:         run: |
0032:           set -euo pipefail
0033:           META_URL="https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.meta.js"
0034:           STATE_FILE=".github/greasyfork-version.txt"
0035:           DASHBOARD_FILE="status/release-dashboard.json"
0036: 
0037:           LIVE_VERSION="$(
0038:             curl --fail --silent --show-error --location --compressed --max-time 30 \
0039:               --retry 3 --retry-delay 5 --header 'Cache-Control: no-cache' \
0040:               "${META_URL}?cache_bust=$(date +%s%N)" |
0041:             sed -nE 's|^//[[:space:]]*@version[[:space:]]+(.+)$|\1|p' |
0042:             head -n 1 |
0043:             xargs

---

0082:           CURRENT_VERSION: ${{ steps.version.outputs.live }}
0083:         shell: bash
0084:         run: |
0085:           set -euo pipefail
0086:           STATE_FILE=".github/greasyfork-version.txt"
0087:           DASHBOARD_FILE="status/release-dashboard.json"
0088:           git config user.name "github-actions[bot]"
0089:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0090: 
0091:           for attempt in 1 2 3; do
0092:             git fetch origin main --prune
0093:             git reset --hard origin/main
0094: 
0095:             REMOTE_STATE="$(tr -d '\r\n ' < "$STATE_FILE" 2>/dev/null || true)"

---

0137:         shell: bash
0138:         run: |
0139:           set -euo pipefail
0140:           git fetch origin main --prune
0141:           REMOTE_STATE="$(git show origin/main:.github/greasyfork-version.txt 2>/dev/null | tr -d '\r\n ' || true)"
0142:           REMOTE_DASHBOARD="$(git show origin/main:status/release-dashboard.json 2>/dev/null || true)"
0143:           DASHBOARD_VERSION="$(jq -r '.latestRelease.version // empty' <<< "$REMOTE_DASHBOARD" 2>/dev/null || true)"
0144:           DASHBOARD_GREASYFORK="$(jq -r '.latestRelease.greasyForkVerified // false' <<< "$REMOTE_DASHBOARD" 2>/dev/null || true)"
0145:           DASHBOARD_DISCORD="$(jq -r '.latestRelease.discordPosted // false' <<< "$REMOTE_DASHBOARD" 2>/dev/null || true)"
0146: 
0147:           if [[ "$REMOTE_STATE" == "$CURRENT_VERSION" ]]; then
0148:             echo "pending=false" >> "$GITHUB_OUTPUT"
0149:           elif [[ "$DASHBOARD_VERSION" == "$CURRENT_VERSION" &&
0150:                   "$DASHBOARD_GREASYFORK" == "true" &&
```

## `.github/workflows/import-canonical-userscript.yml`

```text
0001: name: Import Canonical Userscript Baseline
0002: 
0003: on:
0004:   workflow_dispatch:
0005:   push:
0006:     branches:
0007:       - main
0008:     paths:
0009:       - ".github/workflows/import-canonical-userscript.yml"
0010: 
0011: permissions:
0012:   contents: write
```

## `.github/workflows/owner-release-command.yml`

```text
0055:         shell: bash
0056:         run: |
0057:           set -euo pipefail
0058:           SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"
0059:           grep -Eq "^//[[:space:]]*@version[[:space:]]+${VERSION//./\.}[[:space:]]*$" "$SOURCE"
0060:           test "$(jq -r '.currentVersion' status/release-dashboard.json)" = "$VERSION"
0061:           test "$(jq -r '.status.validation' status/release-dashboard.json)" = "passed"
0062:           test "$(jq -r '.distributionCandidate.version' status/release-dashboard.json)" = "$VERSION"
0063:           test "$(jq -r '.distributionCandidate.state' status/release-dashboard.json)" = "validated"
0064: 
0065:       - name: Ensure readiness belongs to the requested version
0066:         id: readiness
0067:         env:
0068:           GH_TOKEN: ${{ github.token }}

---

0056:         run: |
0057:           set -euo pipefail
0058:           SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"
0059:           grep -Eq "^//[[:space:]]*@version[[:space:]]+${VERSION//./\.}[[:space:]]*$" "$SOURCE"
0060:           test "$(jq -r '.currentVersion' status/release-dashboard.json)" = "$VERSION"
0061:           test "$(jq -r '.status.validation' status/release-dashboard.json)" = "passed"
0062:           test "$(jq -r '.distributionCandidate.version' status/release-dashboard.json)" = "$VERSION"
0063:           test "$(jq -r '.distributionCandidate.state' status/release-dashboard.json)" = "validated"
0064: 
0065:       - name: Ensure readiness belongs to the requested version
0066:         id: readiness
0067:         env:
0068:           GH_TOKEN: ${{ github.token }}
0069:           VERSION: ${{ steps.command.outputs.version }}

---

0057:           set -euo pipefail
0058:           SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"
0059:           grep -Eq "^//[[:space:]]*@version[[:space:]]+${VERSION//./\.}[[:space:]]*$" "$SOURCE"
0060:           test "$(jq -r '.currentVersion' status/release-dashboard.json)" = "$VERSION"
0061:           test "$(jq -r '.status.validation' status/release-dashboard.json)" = "passed"
0062:           test "$(jq -r '.distributionCandidate.version' status/release-dashboard.json)" = "$VERSION"
0063:           test "$(jq -r '.distributionCandidate.state' status/release-dashboard.json)" = "validated"
0064: 
0065:       - name: Ensure readiness belongs to the requested version
0066:         id: readiness
0067:         env:
0068:           GH_TOKEN: ${{ github.token }}
0069:           VERSION: ${{ steps.command.outputs.version }}
0070:           ISSUE_NUMBER: ${{ github.event.issue.number }}

---

0058:           SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"
0059:           grep -Eq "^//[[:space:]]*@version[[:space:]]+${VERSION//./\.}[[:space:]]*$" "$SOURCE"
0060:           test "$(jq -r '.currentVersion' status/release-dashboard.json)" = "$VERSION"
0061:           test "$(jq -r '.status.validation' status/release-dashboard.json)" = "passed"
0062:           test "$(jq -r '.distributionCandidate.version' status/release-dashboard.json)" = "$VERSION"
0063:           test "$(jq -r '.distributionCandidate.state' status/release-dashboard.json)" = "validated"
0064: 
0065:       - name: Ensure readiness belongs to the requested version
0066:         id: readiness
0067:         env:
0068:           GH_TOKEN: ${{ github.token }}
0069:           VERSION: ${{ steps.command.outputs.version }}
0070:           ISSUE_NUMBER: ${{ github.event.issue.number }}
0071:         shell: bash

---

0069:           VERSION: ${{ steps.command.outputs.version }}
0070:           ISSUE_NUMBER: ${{ github.event.issue.number }}
0071:         shell: bash
0072:         run: |
0073:           set -euo pipefail
0074:           RECORDED_VERSION="$(jq -r '.releaseReadiness.version // empty' status/release-dashboard.json)"
0075:           RECORDED_STATE="$(jq -r '.releaseReadiness.state // empty' status/release-dashboard.json)"
0076:           SUMMARY_STATE="$(jq -r '.status.releaseReadiness // empty' status/release-dashboard.json)"
0077: 
0078:           if [[ "$RECORDED_VERSION" == "$VERSION" && "$RECORDED_STATE" == "passed" && "$SUMMARY_STATE" == "passed" ]]; then
0079:             echo "Current-version release readiness is already recorded."
0080:             echo "run_id=already-verified" >> "$GITHUB_OUTPUT"
0081:             exit 0
0082:           fi

---

0070:           ISSUE_NUMBER: ${{ github.event.issue.number }}
0071:         shell: bash
0072:         run: |
0073:           set -euo pipefail
0074:           RECORDED_VERSION="$(jq -r '.releaseReadiness.version // empty' status/release-dashboard.json)"
0075:           RECORDED_STATE="$(jq -r '.releaseReadiness.state // empty' status/release-dashboard.json)"
0076:           SUMMARY_STATE="$(jq -r '.status.releaseReadiness // empty' status/release-dashboard.json)"
0077: 
0078:           if [[ "$RECORDED_VERSION" == "$VERSION" && "$RECORDED_STATE" == "passed" && "$SUMMARY_STATE" == "passed" ]]; then
0079:             echo "Current-version release readiness is already recorded."
0080:             echo "run_id=already-verified" >> "$GITHUB_OUTPUT"
0081:             exit 0
0082:           fi
0083: 

---

0071:         shell: bash
0072:         run: |
0073:           set -euo pipefail
0074:           RECORDED_VERSION="$(jq -r '.releaseReadiness.version // empty' status/release-dashboard.json)"
0075:           RECORDED_STATE="$(jq -r '.releaseReadiness.state // empty' status/release-dashboard.json)"
0076:           SUMMARY_STATE="$(jq -r '.status.releaseReadiness // empty' status/release-dashboard.json)"
0077: 
0078:           if [[ "$RECORDED_VERSION" == "$VERSION" && "$RECORDED_STATE" == "passed" && "$SUMMARY_STATE" == "passed" ]]; then
0079:             echo "Current-version release readiness is already recorded."
0080:             echo "run_id=already-verified" >> "$GITHUB_OUTPUT"
0081:             exit 0
0082:           fi
0083: 
0084:           gh issue comment "$ISSUE_NUMBER" --body "Release readiness for Toolkit v${VERSION} is being validated automatically before production dispatch."

---

0081:             exit 0
0082:           fi
0083: 
0084:           gh issue comment "$ISSUE_NUMBER" --body "Release readiness for Toolkit v${VERSION} is being validated automatically before production dispatch."
0085:           STARTED_AT="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0086:           gh workflow run release-readiness-check.yml --ref main -f version="$VERSION"
0087: 
0088:           RUN_ID=""
0089:           for attempt in {1..60}; do
0090:             RUN_ID="$(gh run list --workflow release-readiness-check.yml --event workflow_dispatch --branch main --limit 30 --json databaseId,createdAt -q "map(select(.createdAt >= \"${STARTED_AT}\")) | sort_by(.createdAt) | reverse | .[0].databaseId // empty")"
0091:             [[ -n "$RUN_ID" ]] && break
0092:             sleep 2
0093:           done
0094:           [[ -n "$RUN_ID" ]] || { echo "::error::The newly dispatched release-readiness run was not found."; exit 1; }

---

0085:           STARTED_AT="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0086:           gh workflow run release-readiness-check.yml --ref main -f version="$VERSION"
0087: 
0088:           RUN_ID=""
0089:           for attempt in {1..60}; do
0090:             RUN_ID="$(gh run list --workflow release-readiness-check.yml --event workflow_dispatch --branch main --limit 30 --json databaseId,createdAt -q "map(select(.createdAt >= \"${STARTED_AT}\")) | sort_by(.createdAt) | reverse | .[0].databaseId // empty")"
0091:             [[ -n "$RUN_ID" ]] && break
0092:             sleep 2
0093:           done
0094:           [[ -n "$RUN_ID" ]] || { echo "::error::The newly dispatched release-readiness run was not found."; exit 1; }
0095:           echo "run_id=$RUN_ID" >> "$GITHUB_OUTPUT"
0096:           gh issue comment "$ISSUE_NUMBER" --body "Toolkit v${VERSION} release readiness is running as Actions run \`${RUN_ID}\`."
0097:           gh run watch "$RUN_ID" --exit-status
0098: 

---

0103:           VERSION: ${{ steps.command.outputs.version }}
0104:         shell: bash
0105:         run: |
0106:           set -euo pipefail
0107:           STARTED_AT="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0108:           gh workflow run release-toolkit.yml --ref main -f version="$VERSION" -f confirmation=RELEASE
0109: 
0110:           RUN_ID=""
0111:           for attempt in {1..30}; do
0112:             RUN_ID="$(gh run list --workflow release-toolkit.yml --event workflow_dispatch --branch main --limit 20 --json databaseId,createdAt -q "map(select(.createdAt >= \"${STARTED_AT}\")) | sort_by(.createdAt) | reverse | .[0].databaseId // empty")"
0113:             [[ -n "$RUN_ID" ]] && break
0114:             sleep 2
0115:           done
0116:           [[ -n "$RUN_ID" ]] || { echo "::error::The newly dispatched production release run was not found."; exit 1; }

---

0107:           STARTED_AT="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0108:           gh workflow run release-toolkit.yml --ref main -f version="$VERSION" -f confirmation=RELEASE
0109: 
0110:           RUN_ID=""
0111:           for attempt in {1..30}; do
0112:             RUN_ID="$(gh run list --workflow release-toolkit.yml --event workflow_dispatch --branch main --limit 20 --json databaseId,createdAt -q "map(select(.createdAt >= \"${STARTED_AT}\")) | sort_by(.createdAt) | reverse | .[0].databaseId // empty")"
0113:             [[ -n "$RUN_ID" ]] && break
0114:             sleep 2
0115:           done
0116:           [[ -n "$RUN_ID" ]] || { echo "::error::The newly dispatched production release run was not found."; exit 1; }
0117:           echo "run_id=$RUN_ID" >> "$GITHUB_OUTPUT"
0118: 
0119:       - name: Record release dispatch
0120:         env:
```

## `.github/workflows/pages-production-monitor.yml`

```text
0010:       - ".github/scripts/check_pages_live.py"
0011:       - ".github/scripts/reconcile_pages_incident.sh"
0012:       - ".github/scripts/test_pages_monitor_reconciliation_contract.py"
0013:       - ".github/scripts/test_pages_monitor_version_contract.py"
0014:       - ".github/workflows/pages-production-monitor.yml"
0015:       - "status/release-dashboard.json"
0016:   push:
0017:     branches:
0018:       - main
0019:     paths:
0020:       - ".github/pages-monitor-policy.json"
0021:       - ".github/fixtures/pages-monitor-version-contract.json"
0022:       - ".github/scripts/check_pages_live.py"
0023:       - ".github/scripts/reconcile_pages_incident.sh"

---

0022:       - ".github/scripts/check_pages_live.py"
0023:       - ".github/scripts/reconcile_pages_incident.sh"
0024:       - ".github/scripts/test_pages_monitor_reconciliation_contract.py"
0025:       - ".github/scripts/test_pages_monitor_version_contract.py"
0026:       - ".github/workflows/pages-production-monitor.yml"
0027:       - "status/release-dashboard.json"
0028:   workflow_run:
0029:     workflows:
0030:       - GitHub Pages Documentation
0031:     types:
0032:       - completed
0033:   schedule:
0034:     - cron: "37 */6 * * *"
0035:   workflow_dispatch:

---

0025:       - ".github/scripts/test_pages_monitor_version_contract.py"
0026:       - ".github/workflows/pages-production-monitor.yml"
0027:       - "status/release-dashboard.json"
0028:   workflow_run:
0029:     workflows:
0030:       - GitHub Pages Documentation
0031:     types:
0032:       - completed
0033:   schedule:
0034:     - cron: "37 */6 * * *"
0035:   workflow_dispatch:
0036: 
0037: permissions:
0038:   contents: read

---

0030:       - GitHub Pages Documentation
0031:     types:
0032:       - completed
0033:   schedule:
0034:     - cron: "37 */6 * * *"
0035:   workflow_dispatch:
0036: 
0037: permissions:
0038:   contents: read
0039:   issues: write
0040: 
0041: concurrency:
0042:   group: toolkit-pages-production-monitor-${{ github.event_name == 'pull_request' && github.event.pull_request.number || 'production' }}
0043:   cancel-in-progress: ${{ github.event_name == 'pull_request' }}

---

0098: 
0099:       - name: Upload production diagnostics
0100:         if: always()
0101:         uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
0102:         with:
0103:           name: github-pages-production-health
0104:           path: |
0105:             pages-production-health.json
0106:             pages-production-health.md
0107:           if-no-files-found: error
0108:           retention-days: 30
0109: 
0110:       - name: Reconcile persistent incident
0111:         if: >-
```

## `.github/workflows/performance-regression-check.yml`

```text
0017:       - ".github/performance-budget.json"
0018:       - ".github/scripts/check_performance_budget.py"
0019:       - ".github/scripts/test_performance_budget.py"
0020:       - ".github/scripts/test_runtime_optimisations.py"
0021:       - ".github/workflows/performance-regression-check.yml"
0022:   workflow_dispatch:
0023: 
0024: permissions:
0025:   contents: read
0026: 
0027: concurrency:
0028:   group: toolkit-performance-${{ github.ref }}
0029:   cancel-in-progress: true
0030: 
```

## `.github/workflows/prepare-release-rollback.yml`

```text
0001: name: Prepare Release Rollback
0002: run-name: Prepare rollback · v${{ inputs.source_version }} → v${{ inputs.recovery_version }}
0003: 
0004: on:
0005:   workflow_dispatch:
0006:     inputs:
0007:       source_version:
0008:         description: "Previously verified version whose executable implementation should be restored"
0009:         required: true
0010:         type: string
0011:       recovery_version:
0012:         description: "New version to publish after review; must be higher than the current release"
0013:         required: true

---

0054:           EXPECTED="PREPARE ROLLBACK ${SOURCE_VERSION} TO ${RECOVERY_VERSION}"
0055:           [[ "$CONFIRMATION" == "$EXPECTED" ]] || {
0056:             echo "::error::Confirmation mismatch. Enter exactly: $EXPECTED"
0057:             exit 1
0058:           }
0059:           CURRENT_VERSION="$(jq -r '.latestRelease.version // empty' status/release-dashboard.json)"
0060:           [[ -n "$CURRENT_VERSION" ]] || { echo "::error::Dashboard has no verified latest release."; exit 1; }
0061:           [[ "$SOURCE_VERSION" != "$CURRENT_VERSION" ]] || {
0062:             echo "::error::Source version is already the current release; this is not a rollback."
0063:             exit 1
0064:           }
0065:           echo "current_version=$CURRENT_VERSION" >> "$GITHUB_OUTPUT"
0066: 
0067:       - name: Verify rollback generator self-tests
```

## `.github/workflows/reconcile-release-announcement-state.yml`

```text
0004:   workflow_run:
0005:     workflows:
0006:       - Release Toolkit
0007:     types:
0008:       - completed
0009:   workflow_dispatch:
0010: 
0011: permissions:
0012:   contents: write
0013: 
0014: concurrency:
0015:   group: toolkit-production-release
0016:   cancel-in-progress: false
0017: 

---

0016:   cancel-in-progress: false
0017: 
0018: jobs:
0019:   reconcile:
0020:     name: Synchronize release announcement tracker
0021:     if: github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success'
0022:     runs-on: ubuntu-latest
0023:     timeout-minutes: 5
0024: 
0025:     steps:
0026:       - name: Check out latest main
0027:         uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7
0028:         with:
0029:           ref: main

---

0032:       - name: Verify completed release state
0033:         id: release
0034:         shell: bash
0035:         run: |
0036:           set -euo pipefail
0037:           DASHBOARD_FILE="status/release-dashboard.json"
0038:           VERSION="$(jq -r '.latestRelease.version // empty' "$DASHBOARD_FILE")"
0039:           GREASYFORK_VERIFIED="$(jq -r '.latestRelease.greasyForkVerified // false' "$DASHBOARD_FILE")"
0040:           DISCORD_POSTED="$(jq -r '.latestRelease.discordPosted // false' "$DASHBOARD_FILE")"
0041: 
0042:           [[ -n "$VERSION" ]] || { echo "::error::The release dashboard has no latest release version."; exit 1; }
0043:           [[ "$GREASYFORK_VERIFIED" == "true" ]] || { echo "::error::The latest release is not verified on Greasy Fork."; exit 1; }
0044:           [[ "$DISCORD_POSTED" == "true" ]] || { echo "::error::The latest release is not recorded as announced to Discord."; exit 1; }
0045: 

---

0050:           CURRENT_VERSION: ${{ steps.release.outputs.version }}
0051:         shell: bash
0052:         run: |
0053:           set -euo pipefail
0054:           STATE_FILE=".github/greasyfork-version.txt"
0055:           DASHBOARD_FILE="status/release-dashboard.json"
0056:           git config user.name "github-actions[bot]"
0057:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0058: 
0059:           for attempt in 1 2 3; do
0060:             git fetch origin main --prune
0061:             git reset --hard origin/main
0062: 
0063:             REMOTE_STATE="$(tr -d '\r\n ' < "$STATE_FILE" 2>/dev/null || true)"
```

## `.github/workflows/release-planning.yml`

```text
0005: on:
0006:   pull_request:
0007:     paths:
0008:       - ".github/scripts/prepare_release_plan.py"
0009:       - ".github/workflows/release-planning.yml"
0010:       - "status/release-dashboard.json"
0011:       - "CHANGELOG.md"
0012:   workflow_dispatch:
0013:     inputs:
0014:       release_level:
0015:         description: Semantic version level to evaluate
0016:         required: true
0017:         type: choice
0018:         default: auto

---

0007:     paths:
0008:       - ".github/scripts/prepare_release_plan.py"
0009:       - ".github/workflows/release-planning.yml"
0010:       - "status/release-dashboard.json"
0011:       - "CHANGELOG.md"
0012:   workflow_dispatch:
0013:     inputs:
0014:       release_level:
0015:         description: Semantic version level to evaluate
0016:         required: true
0017:         type: choice
0018:         default: auto
0019:         options:
0020:           - auto
```

## `.github/workflows/release-readiness-check.yml`

```text
0001: name: Release Readiness Check
0002: 
0003: on:
0004:   workflow_dispatch:
0005:     inputs:
0006:       version:
0007:         description: "Toolkit version to validate without publishing"
0008:         required: true
0009:         default: "4.10.4"
0010:         type: string
0011: 
0012: permissions:
```

## `.github/workflows/release-recovery-validation.yml`

```text
0008:       - ".github/scripts/prepare_rollback_candidate.py"
0009:       - ".github/workflows/release-recovery.yml"
0010:       - ".github/workflows/prepare-release-rollback.yml"
0011:       - ".github/workflows/release-recovery-validation.yml"
0012:       - "docs/RELEASE_RECOVERY.md"
0013:   workflow_dispatch:
0014: 
0015: permissions:
0016:   contents: read
0017: 
0018: concurrency:
0019:   group: toolkit-release-recovery-validation-${{ github.ref }}
0020:   cancel-in-progress: true
0021: 
```

## `.github/workflows/release-recovery.yml`

```text
0001: name: Release Recovery
0002: run-name: Release recovery · ${{ inputs.operation }} · v${{ inputs.version }}
0003: 
0004: on:
0005:   workflow_dispatch:
0006:     inputs:
0007:       operation:
0008:         description: "Recovery operation"
0009:         required: true
0010:         type: choice
0011:         options:
0012:           - verify-release
0013:           - retry-greasyfork

---

0163:             'if .latestRelease.version == $version then
0164:                .status.greasyForkSync="verified" |
0165:                .latestRelease.greasyForkVerified=true |
0166:                .lastUpdated=$now
0167:              else error("dashboard latest release does not match recovery version") end' \
0168:             status/release-dashboard.json > status/release-dashboard.tmp
0169:           mv status/release-dashboard.tmp status/release-dashboard.json
0170:           python3 .github/scripts/generate_release_dashboard.py
0171:           git config user.name "github-actions[bot]"
0172:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0173:           git add status/release-dashboard.json status/README.md
0174:           if ! git diff --cached --quiet; then
0175:             git commit -m "Record Toolkit ${RELEASE_VERSION} Greasy Fork recovery"
0176:             git pull --rebase origin main

---

0164:                .status.greasyForkSync="verified" |
0165:                .latestRelease.greasyForkVerified=true |
0166:                .lastUpdated=$now
0167:              else error("dashboard latest release does not match recovery version") end' \
0168:             status/release-dashboard.json > status/release-dashboard.tmp
0169:           mv status/release-dashboard.tmp status/release-dashboard.json
0170:           python3 .github/scripts/generate_release_dashboard.py
0171:           git config user.name "github-actions[bot]"
0172:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0173:           git add status/release-dashboard.json status/README.md
0174:           if ! git diff --cached --quiet; then
0175:             git commit -m "Record Toolkit ${RELEASE_VERSION} Greasy Fork recovery"
0176:             git pull --rebase origin main
0177:             git push origin HEAD:main

---

0168:             status/release-dashboard.json > status/release-dashboard.tmp
0169:           mv status/release-dashboard.tmp status/release-dashboard.json
0170:           python3 .github/scripts/generate_release_dashboard.py
0171:           git config user.name "github-actions[bot]"
0172:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0173:           git add status/release-dashboard.json status/README.md
0174:           if ! git diff --cached --quiet; then
0175:             git commit -m "Record Toolkit ${RELEASE_VERSION} Greasy Fork recovery"
0176:             git pull --rebase origin main
0177:             git push origin HEAD:main
0178:           fi
0179: 
0180:       - name: Retry private migration backup
0181:         id: backup

---

0202:             'if .latestRelease.version == $version then
0203:                .status.backup="private-repository-verified" |
0204:                .latestRelease.privateBackupCommit=$backup |
0205:                .lastUpdated=$now
0206:              else error("dashboard latest release does not match recovery version") end' \
0207:             status/release-dashboard.json > status/release-dashboard.tmp
0208:           mv status/release-dashboard.tmp status/release-dashboard.json
0209:           python3 .github/scripts/generate_release_dashboard.py
0210:           git config user.name "github-actions[bot]"
0211:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0212:           git add status/release-dashboard.json status/README.md
0213:           if ! git diff --cached --quiet; then
0214:             git commit -m "Record Toolkit ${RELEASE_VERSION} private backup recovery"
0215:             git pull --rebase origin main

---

0203:                .status.backup="private-repository-verified" |
0204:                .latestRelease.privateBackupCommit=$backup |
0205:                .lastUpdated=$now
0206:              else error("dashboard latest release does not match recovery version") end' \
0207:             status/release-dashboard.json > status/release-dashboard.tmp
0208:           mv status/release-dashboard.tmp status/release-dashboard.json
0209:           python3 .github/scripts/generate_release_dashboard.py
0210:           git config user.name "github-actions[bot]"
0211:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0212:           git add status/release-dashboard.json status/README.md
0213:           if ! git diff --cached --quiet; then
0214:             git commit -m "Record Toolkit ${RELEASE_VERSION} private backup recovery"
0215:             git pull --rebase origin main
0216:             git push origin HEAD:main

---

0207:             status/release-dashboard.json > status/release-dashboard.tmp
0208:           mv status/release-dashboard.tmp status/release-dashboard.json
0209:           python3 .github/scripts/generate_release_dashboard.py
0210:           git config user.name "github-actions[bot]"
0211:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0212:           git add status/release-dashboard.json status/README.md
0213:           if ! git diff --cached --quiet; then
0214:             git commit -m "Record Toolkit ${RELEASE_VERSION} private backup recovery"
0215:             git pull --rebase origin main
0216:             git push origin HEAD:main
0217:           fi
0218: 
0219:       - name: Claim Discord retry without posting
0220:         id: discord_guard

---

0222:         env:
0223:           RELEASE_VERSION: ${{ inputs.version }}
0224:         shell: bash
0225:         run: |
0226:           set -euo pipefail
0227:           DASHBOARD="status/release-dashboard.json"
0228:           DASHBOARD_VERSION="$(jq -r '.latestRelease.version // empty' "$DASHBOARD")"
0229:           GF_VERIFIED="$(jq -r '.latestRelease.greasyForkVerified // false' "$DASHBOARD")"
0230:           BACKUP_COMMIT="$(jq -r '.latestRelease.privateBackupCommit // empty' "$DASHBOARD")"
0231:           DISCORD_POSTED="$(jq -r '.latestRelease.discordPosted // false' "$DASHBOARD")"
0232:           PENDING="$(jq -r '.recovery.discordAnnouncement.state // empty' "$DASHBOARD")"
0233: 
0234:           [[ "$DASHBOARD_VERSION" == "$RELEASE_VERSION" ]] || { echo "::error::Dashboard latest version does not match."; exit 1; }
0235:           [[ "$GF_VERIFIED" == "true" ]] || { echo "::error::Greasy Fork is not verified; Discord retry is blocked."; exit 1; }

---

0247: 
0248:           NONCE="${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
0249:           NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0250:           jq --arg version "$RELEASE_VERSION" --arg nonce "$NONCE" --arg now "$NOW" \
0251:             '.recovery.discordAnnouncement={version:$version,state:"pending",nonce:$nonce,startedAt:$now}' \
0252:             "$DASHBOARD" > status/release-dashboard.tmp
0253:           mv status/release-dashboard.tmp "$DASHBOARD"
0254:           python3 .github/scripts/generate_release_dashboard.py
0255:           git config user.name "github-actions[bot]"
0256:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0257:           git add "$DASHBOARD" status/README.md
0258:           git commit -m "Claim Toolkit ${RELEASE_VERSION} Discord recovery"
0259:           git pull --rebase origin main
0260:           git push origin HEAD:main

---

0248:           NONCE="${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
0249:           NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0250:           jq --arg version "$RELEASE_VERSION" --arg nonce "$NONCE" --arg now "$NOW" \
0251:             '.recovery.discordAnnouncement={version:$version,state:"pending",nonce:$nonce,startedAt:$now}' \
0252:             "$DASHBOARD" > status/release-dashboard.tmp
0253:           mv status/release-dashboard.tmp "$DASHBOARD"
0254:           python3 .github/scripts/generate_release_dashboard.py
0255:           git config user.name "github-actions[bot]"
0256:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0257:           git add "$DASHBOARD" status/README.md
0258:           git commit -m "Claim Toolkit ${RELEASE_VERSION} Discord recovery"
0259:           git pull --rebase origin main
0260:           git push origin HEAD:main
0261:           echo "skip=false" >> "$GITHUB_OUTPUT"

---

0299:         shell: bash
0300:         run: |
0301:           set -euo pipefail
0302:           git fetch origin main
0303:           git reset --hard origin/main
0304:           DASHBOARD="status/release-dashboard.json"
0305:           NONCE="$(jq -r '.recovery.discordAnnouncement.nonce // empty' "$DASHBOARD")"
0306:           [[ "$NONCE" == "$EXPECTED_NONCE" ]] || { echo "::error::Discord recovery claim changed before finalization."; exit 1; }
0307:           NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0308:           jq --arg version "$RELEASE_VERSION" --arg now "$NOW" \
0309:             'if .latestRelease.version == $version then
0310:                .status.discordRelease="posted" |
0311:                .latestRelease.discordPosted=true |
0312:                .latestRelease.completedAt=(.latestRelease.completedAt // $now) |

---

0311:                .latestRelease.discordPosted=true |
0312:                .latestRelease.completedAt=(.latestRelease.completedAt // $now) |
0313:                .lastUpdated=$now |
0314:                del(.recovery.discordAnnouncement)
0315:              else error("dashboard latest release does not match recovery version") end' \
0316:             "$DASHBOARD" > status/release-dashboard.tmp
0317:           mv status/release-dashboard.tmp "$DASHBOARD"
0318:           printf '%s\n' "$RELEASE_VERSION" > .github/greasyfork-version.txt
0319:           python3 .github/scripts/generate_release_dashboard.py
0320:           git config user.name "github-actions[bot]"
0321:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0322:           git add "$DASHBOARD" status/README.md .github/greasyfork-version.txt
0323:           git commit -m "Record Toolkit ${RELEASE_VERSION} Discord recovery"
0324:           git pull --rebase origin main

---

0312:                .latestRelease.completedAt=(.latestRelease.completedAt // $now) |
0313:                .lastUpdated=$now |
0314:                del(.recovery.discordAnnouncement)
0315:              else error("dashboard latest release does not match recovery version") end' \
0316:             "$DASHBOARD" > status/release-dashboard.tmp
0317:           mv status/release-dashboard.tmp "$DASHBOARD"
0318:           printf '%s\n' "$RELEASE_VERSION" > .github/greasyfork-version.txt
0319:           python3 .github/scripts/generate_release_dashboard.py
0320:           git config user.name "github-actions[bot]"
0321:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0322:           git add "$DASHBOARD" status/README.md .github/greasyfork-version.txt
0323:           git commit -m "Record Toolkit ${RELEASE_VERSION} Discord recovery"
0324:           git pull --rebase origin main
0325:           git push origin HEAD:main

---

0367: 
0368:           case "$DISCORD_STATE" in
0369:             posted) DISCORD_POSTED=true ;;
0370:             not-posted) DISCORD_POSTED=false ;;
0371:             preserve)
0372:               [[ "$(jq -r '.latestRelease.version // empty' status/release-dashboard.json)" == "$RELEASE_VERSION" ]] || {
0373:                 echo "::error::Cannot preserve Discord state because the existing dashboard records a different version."
0374:                 exit 1
0375:               }
0376:               DISCORD_POSTED="$(jq -r '.latestRelease.discordPosted // false' status/release-dashboard.json)"
0377:               ;;
0378:           esac
0379: 
0380:           NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

---

0371:             preserve)
0372:               [[ "$(jq -r '.latestRelease.version // empty' status/release-dashboard.json)" == "$RELEASE_VERSION" ]] || {
0373:                 echo "::error::Cannot preserve Discord state because the existing dashboard records a different version."
0374:                 exit 1
0375:               }
0376:               DISCORD_POSTED="$(jq -r '.latestRelease.discordPosted // false' status/release-dashboard.json)"
0377:               ;;
0378:           esac
0379: 
0380:           NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0381:           jq --arg version "$RELEASE_VERSION" --arg hash "$RELEASE_HASH" --arg releaseUrl "$RELEASE_URL" \
0382:              --arg backup "$BACKUP_COMMIT" --arg now "$NOW" --argjson discord "$DISCORD_POSTED" \
0383:             '.currentVersion=$version |
0384:              .status.validation="passed" |

---

0387:              .status.backup="private-repository-verified" |
0388:              .status.discordRelease=(if $discord then "posted" else "not-posted" end) |
0389:              .latestRelease={version:$version,sha256:$hash,githubRelease:$releaseUrl,greasyForkVerified:true,privateBackupCommit:$backup,discordPosted:$discord,completedAt:$now} |
0390:              .lastUpdated=$now |
0391:              del(.recovery.discordAnnouncement)' \
0392:             status/release-dashboard.json > status/release-dashboard.tmp
0393:           mv status/release-dashboard.tmp status/release-dashboard.json
0394:           if [[ "$DISCORD_POSTED" == "true" ]]; then
0395:             printf '%s\n' "$RELEASE_VERSION" > .github/greasyfork-version.txt
0396:           fi
0397:           python3 .github/scripts/generate_release_dashboard.py
0398:           git config user.name "github-actions[bot]"
0399:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0400:           git add status/release-dashboard.json status/README.md .github/greasyfork-version.txt

---

0388:              .status.discordRelease=(if $discord then "posted" else "not-posted" end) |
0389:              .latestRelease={version:$version,sha256:$hash,githubRelease:$releaseUrl,greasyForkVerified:true,privateBackupCommit:$backup,discordPosted:$discord,completedAt:$now} |
0390:              .lastUpdated=$now |
0391:              del(.recovery.discordAnnouncement)' \
0392:             status/release-dashboard.json > status/release-dashboard.tmp
0393:           mv status/release-dashboard.tmp status/release-dashboard.json
0394:           if [[ "$DISCORD_POSTED" == "true" ]]; then
0395:             printf '%s\n' "$RELEASE_VERSION" > .github/greasyfork-version.txt
0396:           fi
0397:           python3 .github/scripts/generate_release_dashboard.py
0398:           git config user.name "github-actions[bot]"
0399:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0400:           git add status/release-dashboard.json status/README.md .github/greasyfork-version.txt
0401:           git commit -m "Rebuild Toolkit ${RELEASE_VERSION} release dashboard"

---

0395:             printf '%s\n' "$RELEASE_VERSION" > .github/greasyfork-version.txt
0396:           fi
0397:           python3 .github/scripts/generate_release_dashboard.py
0398:           git config user.name "github-actions[bot]"
0399:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0400:           git add status/release-dashboard.json status/README.md .github/greasyfork-version.txt
0401:           git commit -m "Rebuild Toolkit ${RELEASE_VERSION} release dashboard"
0402:           git pull --rebase origin main
0403:           git push origin HEAD:main
0404: 
0405:       - name: Repair stable GitHub Release assets
0406:         if: inputs.operation == 'repair-stable-assets'
0407:         env:
0408:           GH_TOKEN: ${{ github.token }}
```

## `.github/workflows/release-toolkit-dry-run.yml`

```text
0001: name: Release Toolkit Dry Run
0002: 
0003: on:
0004:   workflow_dispatch:
0005:     inputs:
0006:       version:
0007:         description: "Validated Toolkit version to prepare"
0008:         required: true
0009:         default: "4.10.4"
0010:         type: string
0011: 
0012: permissions:

---

0089:                  greasyForkChanged: false,
0090:                  discordPosted: false,
0091:                  completedAt: $now
0092:                }
0093:              | .lastUpdated = $now' \
0094:             status/release-dashboard.json > status/release-dashboard.tmp
0095: 
0096:           mv status/release-dashboard.tmp status/release-dashboard.json
0097:           git config user.name "github-actions[bot]"
0098:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0099:           git add status/release-dashboard.json
0100: 
0101:           if git diff --cached --quiet; then
0102:             echo "Release dashboard already records this dry run."

---

0091:                  completedAt: $now
0092:                }
0093:              | .lastUpdated = $now' \
0094:             status/release-dashboard.json > status/release-dashboard.tmp
0095: 
0096:           mv status/release-dashboard.tmp status/release-dashboard.json
0097:           git config user.name "github-actions[bot]"
0098:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0099:           git add status/release-dashboard.json
0100: 
0101:           if git diff --cached --quiet; then
0102:             echo "Release dashboard already records this dry run."
0103:             exit 0
0104:           fi

---

0094:             status/release-dashboard.json > status/release-dashboard.tmp
0095: 
0096:           mv status/release-dashboard.tmp status/release-dashboard.json
0097:           git config user.name "github-actions[bot]"
0098:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0099:           git add status/release-dashboard.json
0100: 
0101:           if git diff --cached --quiet; then
0102:             echo "Release dashboard already records this dry run."
0103:             exit 0
0104:           fi
0105: 
0106:           git commit -m "Record Toolkit ${RELEASE_VERSION} release dry run"
0107:           git pull --rebase origin main
```

## `.github/workflows/release-toolkit.yml`

```text
0001: name: Release Toolkit
0002: 
0003: on:
0004:   workflow_dispatch:
0005:     inputs:
0006:       version:
0007:         description: "Validated Toolkit version to publish"
0008:         required: true
0009:         type: string
0010:       confirmation:
0011:         description: "Type RELEASE to confirm a public release"
0012:         required: true

---

0182: 
0183:           curl --fail --silent --show-error --max-time 30 --retry 2 --retry-delay 5 \
0184:             --request POST --header "Content-Type: application/json" \
0185:             --data @discord-release-payload.json "${DISCORD_WEBHOOK_URL}?wait=true"
0186: 
0187:       - name: Record successful release in dashboard
0188:         env:
0189:           RELEASE_VERSION: ${{ inputs.version }}
0190:           BACKUP_COMMIT: ${{ steps.private_backup.outputs.backup_commit }}
0191:         shell: bash
0192:         run: |
0193:           set -euo pipefail
0194:           NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
0195:           HASH="$(jq -r '.sha256' "release-bundle/release-manifest-v${RELEASE_VERSION}.json")"

---

0204:              .status.discordRelease="posted" |
0205:              .status.releaseReadiness="passed" |
0206:              .releaseReadiness={version:$version,state:"passed",requiredSecrets:true,privateRepositoryReadWrite:true,greasyForkMetadataVerified:true,publicReleaseCreated:false,completedAt:$now} |
0207:              .latestRelease={version:$version,sha256:$hash,githubRelease:$releaseUrl,greasyForkVerified:true,privateBackupCommit:$backupCommit,discordPosted:true,completedAt:$now} |
0208:              .lastUpdated=$now' \
0209:             status/release-dashboard.json > status/release-dashboard.tmp
0210:           mv status/release-dashboard.tmp status/release-dashboard.json
0211:           python3 .github/scripts/generate_release_dashboard.py
0212:           git config user.name "github-actions[bot]"
0213:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0214:           git add status/release-dashboard.json status/README.md
0215:           git commit -m "Record Toolkit ${RELEASE_VERSION} verified release"
0216:           git pull --rebase origin main
0217:           git push origin HEAD:main

---

0205:              .status.releaseReadiness="passed" |
0206:              .releaseReadiness={version:$version,state:"passed",requiredSecrets:true,privateRepositoryReadWrite:true,greasyForkMetadataVerified:true,publicReleaseCreated:false,completedAt:$now} |
0207:              .latestRelease={version:$version,sha256:$hash,githubRelease:$releaseUrl,greasyForkVerified:true,privateBackupCommit:$backupCommit,discordPosted:true,completedAt:$now} |
0208:              .lastUpdated=$now' \
0209:             status/release-dashboard.json > status/release-dashboard.tmp
0210:           mv status/release-dashboard.tmp status/release-dashboard.json
0211:           python3 .github/scripts/generate_release_dashboard.py
0212:           git config user.name "github-actions[bot]"
0213:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0214:           git add status/release-dashboard.json status/README.md
0215:           git commit -m "Record Toolkit ${RELEASE_VERSION} verified release"
0216:           git pull --rebase origin main
0217:           git push origin HEAD:main
0218: 

---

0209:             status/release-dashboard.json > status/release-dashboard.tmp
0210:           mv status/release-dashboard.tmp status/release-dashboard.json
0211:           python3 .github/scripts/generate_release_dashboard.py
0212:           git config user.name "github-actions[bot]"
0213:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0214:           git add status/release-dashboard.json status/README.md
0215:           git commit -m "Record Toolkit ${RELEASE_VERSION} verified release"
0216:           git pull --rebase origin main
0217:           git push origin HEAD:main
0218: 
0219:       - name: Write release summary
0220:         env:
0221:           RELEASE_VERSION: ${{ inputs.version }}
0222:           BACKUP_COMMIT: ${{ steps.private_backup.outputs.backup_commit }}
```

## `.github/workflows/repository-audit.yml`

```text
0001: name: Repository and Dependency Audit
0002: 
0003: on:
0004:   workflow_dispatch:
0005:   push:
0006:     branches:
0007:       - main
0008:     paths:
0009:       - ".github/scripts/audit_repository.py"
0010:       - ".github/workflows/repository-audit.yml"
0011:       - "status/release-dashboard.json"
0012: 

---

0006:     branches:
0007:       - main
0008:     paths:
0009:       - ".github/scripts/audit_repository.py"
0010:       - ".github/workflows/repository-audit.yml"
0011:       - "status/release-dashboard.json"
0012: 
0013: permissions:
0014:   contents: write
0015: 
0016: concurrency:
0017:   group: repository-dependency-audit
0018:   cancel-in-progress: false
0019: 

---

0041:         with:
0042:           name: missionchief-repository-audit
0043:           path: |
0044:             status/repository-audit.md
0045:             status/repository-audit.json
0046:             status/release-dashboard.json
0047:           if-no-files-found: error
0048:           retention-days: 90
0049: 
0050:       - name: Commit updated audit state
0051:         shell: bash
0052:         run: |
0053:           set -euo pipefail
0054:           git config user.name "github-actions[bot]"

---

0051:         shell: bash
0052:         run: |
0053:           set -euo pipefail
0054:           git config user.name "github-actions[bot]"
0055:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0056:           git add status/repository-audit.md status/repository-audit.json status/release-dashboard.json
0057: 
0058:           if git diff --cached --quiet; then
0059:             echo "Audit state is already current."
0060:             exit 0
0061:           fi
0062: 
0063:           git commit -m "Update repository dependency audit"
0064:           git pull --rebase origin main
```

## `.github/workflows/sync-repository-labels.yml`

```text
0005:     branches:
0006:       - main
0007:     paths:
0008:       - ".github/labels.json"
0009:       - ".github/workflows/sync-repository-labels.yml"
0010:   workflow_dispatch:
0011: 
0012: permissions:
0013:   contents: read
0014:   issues: write
0015: 
0016: concurrency:
0017:   group: repository-label-sync
0018:   cancel-in-progress: true
```

## `.github/workflows/update-release-dashboard.yml`

```text
0001: name: Update Release Dashboard
0002: 
0003: on:
0004:   workflow_dispatch:
0005:   push:
0006:     branches:
0007:       - main
0008:     paths:
0009:       - "status/release-dashboard.json"
0010:       - ".github/scripts/generate_release_dashboard.py"
0011:       - ".github/workflows/update-release-dashboard.yml"
0012: 

---

0004:   workflow_dispatch:
0005:   push:
0006:     branches:
0007:       - main
0008:     paths:
0009:       - "status/release-dashboard.json"
0010:       - ".github/scripts/generate_release_dashboard.py"
0011:       - ".github/workflows/update-release-dashboard.yml"
0012: 
0013: permissions:
0014:   contents: write
0015: 
0016: concurrency:
0017:   group: update-release-dashboard

---

0006:     branches:
0007:       - main
0008:     paths:
0009:       - "status/release-dashboard.json"
0010:       - ".github/scripts/generate_release_dashboard.py"
0011:       - ".github/workflows/update-release-dashboard.yml"
0012: 
0013: permissions:
0014:   contents: write
0015: 
0016: concurrency:
0017:   group: update-release-dashboard
0018:   cancel-in-progress: true
0019: 

---

0012: 
0013: permissions:
0014:   contents: write
0015: 
0016: concurrency:
0017:   group: update-release-dashboard
0018:   cancel-in-progress: true
0019: 
0020: jobs:
0021:   update:
0022:     name: Generate Toolkit control panel
0023:     runs-on: ubuntu-latest
0024:     timeout-minutes: 5
0025: 

---

0029:         with:
0030:           ref: main
0031:           fetch-depth: 0
0032: 
0033:       - name: Validate dashboard JSON
0034:         run: python3 -m json.tool status/release-dashboard.json >/dev/null
0035: 
0036:       - name: Generate human-readable dashboard
0037:         run: python3 .github/scripts/generate_release_dashboard.py
0038: 
0039:       - name: Commit dashboard update
0040:         shell: bash
0041:         run: |
0042:           set -euo pipefail

---

0054:           git push origin HEAD:main
0055: 
0056:       - name: Write workflow summary
0057:         shell: bash
0058:         run: |
0059:           VERSION="$(jq -r '.currentVersion' status/release-dashboard.json)"
0060:           {
0061:             echo "# MissionChief Toolkit dashboard"
0062:             echo
0063:             echo "- ✅ Dashboard JSON validated"
0064:             echo "- ✅ Human-readable control panel generated"
0065:             echo "- ✅ Current version: ${VERSION}"
0066:           } >> "$GITHUB_STEP_SUMMARY"
```

## `.github/workflows/userscript-structural-audit.yml`

```text
0013:     paths:
0014:       - "src/MissionChief_Map_Command_Toolkit.user.js"
0015:       - ".github/userscript-audit-policy.json"
0016:       - ".github/scripts/audit_userscript_structure.py"
0017:       - ".github/workflows/userscript-structural-audit.yml"
0018:   workflow_dispatch:
0019: 
0020: permissions:
0021:   contents: read
0022: 
0023: concurrency:
0024:   group: userscript-structural-audit-${{ github.ref }}
0025:   cancel-in-progress: true
0026: 
```

## `.github/workflows/validate-issue-intake.yml`

```text
0013:     paths:
0014:       - ".github/ISSUE_TEMPLATE/**"
0015:       - ".github/labels.json"
0016:       - ".github/workflows/sync-repository-labels.yml"
0017:       - ".github/workflows/validate-issue-intake.yml"
0018:   workflow_dispatch:
0019: 
0020: permissions:
0021:   contents: read
0022: 
0023: jobs:
0024:   validate:
0025:     name: Validate forms and managed labels
0026:     runs-on: ubuntu-latest
```

## `.github/workflows/validate-userscript.yml`

```text
0017:       - "CHANGELOG.md"
0018:       - ".github/scripts/validate_userscript.py"
0019:       - ".github/scripts/reconcile_validation_dashboard.py"
0020:       - ".github/workflows/validate-userscript.yml"
0021:       - "status/source-baseline.json"
0022:   workflow_dispatch:
0023: 
0024: permissions:
0025:   contents: write
0026: 
0027: concurrency:
0028:   group: canonical-userscript-validation-${{ github.ref }}
0029:   cancel-in-progress: false
0030: 

---

0097:           python3 .github/scripts/reconcile_validation_dashboard.py
0098:           python3 .github/scripts/generate_release_dashboard.py
0099: 
0100:           git config user.name "github-actions[bot]"
0101:           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
0102:           git add dist status/release-dashboard.json status/README.md
0103: 
0104:           if git diff --cached --quiet; then
0105:             echo "Validated distribution is already current."
0106:             exit 0
0107:           fi
0108: 
0109:           git commit -m "Build validated Toolkit ${VERSION} distribution candidate"
0110:           git pull --rebase origin main
```
