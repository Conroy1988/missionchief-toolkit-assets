#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def save(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"{label}: boundary mismatch")
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement + text[b:]


# Canonical validation prepares the complete release-ready candidate once.
path = ".github/workflows/validate-userscript.yml"
text = load(path)
text = once(
    text,
    """      - name: Verify distribution files are identical
        run: cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt

      - name: Write immutable validation candidate evidence
""",
    """      - name: Verify distribution files are identical
        run: cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt

      - name: Prepare immutable release-ready bundle
        id: release_bundle
        shell: bash
        run: |
          set -euo pipefail
          VERSION="$(jq -r '.version' dist/release-manifest.json)"
          python3 .github/scripts/prepare_release_bundle.py "$VERSION"
          USER_FILE="release-bundle/MissionChief_Map_Command_Toolkit_v${VERSION}.user.js"
          TXT_FILE="release-bundle/MissionChief_Map_Command_Toolkit_v${VERSION}.txt"
          MANIFEST="release-bundle/release-manifest-v${VERSION}.json"
          cmp --silent "$USER_FILE" "$TXT_FILE"
          test "$(jq -r '.version' "$MANIFEST")" = "$VERSION"
          test "$(sha256sum "$USER_FILE" | awk '{print $1}')" = "$(jq -r '.sha256' "$MANIFEST")"
          echo "version=$VERSION" >> "$GITHUB_OUTPUT"

      - name: Write immutable validation candidate evidence
""",
    "validation bundle insertion",
)
text = once(
    text,
    """            dist/SHA256SUMS.txt
            dist/release-manifest.json
          if-no-files-found: error
""",
    """            dist/SHA256SUMS.txt
            dist/release-manifest.json
            release-bundle/
          if-no-files-found: error
""",
    "validation artifact expansion",
)
text = once(
    text,
    '            echo "- ✅ Distribution files are byte-identical"\n',
    '            echo "- ✅ Distribution files are byte-identical"\n            echo "- ✅ Complete release bundle prepared once and retained with the candidate"\n',
    "validation summary",
)
save(path, text)


# Automatic releases use the exact candidate and skip the duplicate readiness workflow.
path = ".github/workflows/auto-release-after-validation.yml"
text = load(path)
text = once(
    text,
    """  readiness:
    name: Run mandatory release readiness
    needs: prepare
    if: needs.prepare.outputs.release_needed == 'true'
    permissions:
      actions: write
      contents: read
    uses: ./.github/workflows/release-readiness-check.yml
    with:
      version: ${{ needs.prepare.outputs.version }}
    secrets:
      DISCORD_RELEASE_WEBHOOK: ${{ secrets.DISCORD_RELEASE_WEBHOOK }}
      MIGRATION_REPO_TOKEN: ${{ secrets.MIGRATION_REPO_TOKEN }}

""",
    "",
    "automatic readiness removal",
)
text = once(
    text,
    """  production:
    name: Run guarded production release
    needs:
      - prepare
      - readiness
    if: needs.prepare.outputs.release_needed == 'true' && needs.readiness.result == 'success'
    permissions:
      actions: write
      contents: write
    uses: ./.github/workflows/release-toolkit.yml
    with:
      version: ${{ needs.prepare.outputs.version }}
      confirmation: RELEASE
""",
    """  production:
    name: Run maximum-speed verified production release
    needs: prepare
    if: needs.prepare.outputs.release_needed == 'true'
    permissions:
      actions: write
      contents: write
    uses: ./.github/workflows/release-toolkit.yml
    with:
      version: ${{ needs.prepare.outputs.version }}
      confirmation: RELEASE
      validation_run_id: ${{ github.event.workflow_run.id }}
      validated_sha: ${{ github.event.workflow_run.head_sha }}
""",
    "automatic fast handoff",
)
save(path, text)


# Production consumes immutable evidence, parallelises external work and makes Pages non-blocking.
path = ".github/workflows/release-toolkit.yml"
text = load(path)
text = once(
    text,
    """      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string
    secrets:
""",
    """      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string
      validation_run_id:
        description: "Exact successful canonical-validation workflow run ID"
        required: false
        default: ""
        type: string
      validated_sha:
        description: "Exact validated main commit SHA"
        required: false
        default: ""
        type: string
    secrets:
""",
    "workflow_call fast inputs",
)
text = once(
    text,
    """      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string

permissions:
""",
    """      confirmation:
        description: "Type RELEASE to confirm a public release"
        required: true
        type: string
      validation_run_id:
        description: "Optional canonical-validation workflow run ID"
        required: false
        default: ""
        type: string
      validated_sha:
        description: "Optional exact validated main commit SHA"
        required: false
        default: ""
        type: string

permissions:
""",
    "workflow_dispatch fast inputs",
)
text = once(
    text,
    "          ref: main\n          fetch-depth: 0\n",
    "          ref: ${{ inputs.validated_sha != '' && inputs.validated_sha || 'main' }}\n          fetch-depth: 0\n",
    "exact release checkout",
)
start = "      - name: Production release safety gate\n"
end = "      - name: Commit stable Greasy Fork source mirror\n"
replacement = """      - name: Production release safety gate
        id: release_start
        env:
          RELEASE_VERSION: ${{ inputs.version }}
          CONFIRMATION: ${{ inputs.confirmation }}
          VALIDATED_SHA: ${{ inputs.validated_sha }}
          GH_TOKEN: ${{ github.token }}
          MIGRATION_REPO_TOKEN: ${{ secrets.MIGRATION_REPO_TOKEN }}
        shell: bash
        run: |
          set -euo pipefail
          echo "started_epoch=$(date +%s)" >> "$GITHUB_OUTPUT"
          echo "started_at=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_OUTPUT"
          [[ "$CONFIRMATION" == "RELEASE" ]] || { echo "::error::Type RELEASE exactly to confirm."; exit 1; }
          [[ "$RELEASE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([+-][0-9A-Za-z.-]+)?$ ]] || { echo "::error::Invalid release version: $RELEASE_VERSION"; exit 1; }
          [[ "$(jq -r '.greasyFork.syncEnabled' .github/release-settings.json)" == "true" ]] || { echo "::error::Greasy Fork release synchronization is not enabled."; exit 1; }
          [[ -n "${MIGRATION_REPO_TOKEN:-}" ]] || { echo "::error::MIGRATION_REPO_TOKEN is not configured."; exit 1; }
          if [[ -n "$VALIDATED_SHA" ]]; then
            git fetch origin main --prune
            [[ "$(git rev-parse origin/main)" == "$VALIDATED_SHA" ]]
            [[ "$(git rev-parse HEAD)" == "$VALIDATED_SHA" ]]
          fi
          gh release view "v${RELEASE_VERSION}" >/dev/null 2>&1 && { echo "::error::GitHub Release v${RELEASE_VERSION} already exists."; exit 1; } || true

      - name: Resolve exact immutable release candidate
        id: candidate
        env:
          RELEASE_VERSION: ${{ inputs.version }}
          VALIDATION_RUN_ID: ${{ inputs.validation_run_id }}
          VALIDATED_SHA: ${{ inputs.validated_sha }}
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: |
          set -euo pipefail
          if [[ -n "$VALIDATION_RUN_ID" && -n "$VALIDATED_SHA" ]]; then
            ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${VALIDATED_SHA}"
            gh api "repos/${GITHUB_REPOSITORY}/actions/runs/${VALIDATION_RUN_ID}/artifacts" > /tmp/validation-artifacts.json
            ARTIFACT_ID="$(jq -r --arg name "$ARTIFACT_NAME" '.artifacts | map(select(.name == $name and .expired == false)) | sort_by(.created_at) | last | .id // empty' /tmp/validation-artifacts.json)"
            [[ -n "$ARTIFACT_ID" ]] || { echo "::error::Exact validation candidate artifact was not found."; exit 1; }
            rm -rf /tmp/validation-candidate
            mkdir -p /tmp/validation-candidate
            gh api "repos/${GITHUB_REPOSITORY}/actions/artifacts/${ARTIFACT_ID}/zip" > /tmp/validation-candidate.zip
            unzip -q /tmp/validation-candidate.zip -d /tmp/validation-candidate
            EVIDENCE="/tmp/validation-candidate/validation-candidate/validation-candidate.json"
            CANDIDATE_DIST="/tmp/validation-candidate/dist"
            CANDIDATE_BUNDLE="/tmp/validation-candidate/release-bundle"
            python3 .github/scripts/verify_validation_candidate.py --evidence "$EVIDENCE" --source src/MissionChief_Map_Command_Toolkit.user.js --dist-dir "$CANDIDATE_DIST" --expected-commit "$VALIDATED_SHA" --expected-ref refs/heads/main --expected-version "$RELEASE_VERSION"
            test -d "$CANDIDATE_BUNDLE"
            rm -rf dist release-bundle
            cp -a "$CANDIDATE_DIST" dist
            cp -a "$CANDIDATE_BUNDLE" release-bundle
            echo "mode=immutable-candidate" >> "$GITHUB_OUTPUT"
          else
            python3 .github/scripts/validate_userscript.py
            node --check src/MissionChief_Map_Command_Toolkit.user.js
            cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt
            python3 .github/scripts/prepare_release_bundle.py "$RELEASE_VERSION"
            echo "mode=manual-recovery" >> "$GITHUB_OUTPUT"
          fi
          cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt
          test "$(jq -r '.version' dist/release-manifest.json)" = "$RELEASE_VERSION"

"""
text = between(text, start, end, replacement, "exact candidate stage")
text = once(
    text,
    """      - name: Prepare immutable release bundle
        env:
          RELEASE_VERSION: ${{ inputs.version }}
        run: python3 .github/scripts/prepare_release_bundle.py "$RELEASE_VERSION"

""",
    "",
    "duplicate bundle removal",
)
text = once(text, "      - name: Create GitHub Release\n        env:\n", "      - name: Create GitHub Release\n        id: github_release\n        env:\n", "release timing id")
text = once(
    text,
    """            "release-bundle/SHA256SUMS-v${RELEASE_VERSION}.txt" \\
            "release-bundle/migration-handover-v${RELEASE_VERSION}.md"

      - name: Wait for Greasy Fork synchronization
""",
    """            "release-bundle/SHA256SUMS-v${RELEASE_VERSION}.txt" \\
            "release-bundle/migration-handover-v${RELEASE_VERSION}.md"
          echo "created_epoch=$(date +%s)" >> "$GITHUB_OUTPUT"
          echo "created_at=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_OUTPUT"

      - name: Verify Greasy Fork and back up concurrently
""",
    "GitHub release timing",
)
start = "      - name: Verify Greasy Fork and back up concurrently\n"
end = "      - name: Post verified release to Discord\n"
parallel = """      - name: Verify Greasy Fork and back up concurrently
        id: external
        env:
          RELEASE_VERSION: ${{ inputs.version }}
          MIGRATION_REPO_TOKEN: ${{ secrets.MIGRATION_REPO_TOKEN }}
        shell: bash
        run: |
          set -euo pipefail
          META_URL="$(jq -r '.greasyFork.metadataUrl' .github/release-settings.json)"
          BACKUP_OUTPUT="$RUNNER_TEMP/private-backup-output"
          (
            GITHUB_OUTPUT="$BACKUP_OUTPUT" bash .github/scripts/backup_release_to_private_repo.sh > "$RUNNER_TEMP/private-backup.log" 2>&1
            date +%s > "$RUNNER_TEMP/private-backup-epoch"
          ) &
          BACKUP_PID=$!
          (
            attempt=0
            while true; do
              attempt=$((attempt + 1))
              if curl --fail --silent --show-error --location --compressed --max-time 30 --header "Cache-Control: no-cache" "${META_URL}?cache_bust=$(date +%s%N)" --output greasyfork-release.meta.js; then
                LIVE_VERSION="$(sed -nE 's|^//[[:space:]]*@version[[:space:]]+(.+)$|\1|p' greasyfork-release.meta.js | head -n 1 | xargs)"
                if [[ "$LIVE_VERSION" == "$RELEASE_VERSION" ]]; then
                  echo "$attempt" > "$RUNNER_TEMP/greasyfork-attempts"
                  date +%s > "$RUNNER_TEMP/greasyfork-epoch"
                  exit 0
                fi
              fi
              elapsed=$(( $(date +%s) - ${{ steps.github_release.outputs.created_epoch }} ))
              (( elapsed < 30 )) && sleep 2 && continue
              (( elapsed < 150 )) && sleep 5 && continue
              (( elapsed < 1800 )) && sleep 15 && continue
              exit 1
            done
          ) &
          GF_PID=$!
          backup_status=0; gf_status=0
          wait "$BACKUP_PID" || backup_status=$?
          wait "$GF_PID" || gf_status=$?
          cat "$RUNNER_TEMP/private-backup.log" || true
          [[ "$backup_status" -eq 0 ]] || { echo "::error::Private backup failed."; exit "$backup_status"; }
          [[ "$gf_status" -eq 0 ]] || { echo "::error::Greasy Fork verification failed."; exit "$gf_status"; }
          BACKUP_COMMIT="$(sed -n 's/^backup_commit=//p' "$BACKUP_OUTPUT" | tail -n 1)"
          [[ -n "$BACKUP_COMMIT" ]]
          echo "backup_commit=$BACKUP_COMMIT" >> "$GITHUB_OUTPUT"
          echo "backup_epoch=$(cat "$RUNNER_TEMP/private-backup-epoch")" >> "$GITHUB_OUTPUT"
          echo "greasyfork_epoch=$(cat "$RUNNER_TEMP/greasyfork-epoch")" >> "$GITHUB_OUTPUT"
          echo "greasyfork_attempts=$(cat "$RUNNER_TEMP/greasyfork-attempts")" >> "$GITHUB_OUTPUT"

"""
text = between(text, start, end, parallel, "parallel external stage")
text = text.replace("${{ steps.private_backup.outputs.backup_commit }}", "${{ steps.external.outputs.backup_commit }}")
text = once(text, "      - name: Post verified release to Discord\n        env:\n", "      - name: Post verified release to Discord\n        id: discord\n        env:\n", "Discord timing id")
text = once(
    text,
    """            --request POST --header "Content-Type: application/json" \\
            --data @discord-release-payload.json "${DISCORD_WEBHOOK_URL}?wait=true"

      - name: Record successful release, manifest and announcement state
""",
    """            --request POST --header "Content-Type: application/json" \\
            --data @discord-release-payload.json "${DISCORD_WEBHOOK_URL}?wait=true"
          echo "posted_epoch=$(date +%s)" >> "$GITHUB_OUTPUT"
          echo "posted_at=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_OUTPUT"

      - name: Record successful release, manifest, announcement and speed state
""",
    "Discord timing output",
)
text = once(
    text,
    """        shell: bash
        run: |
          set -euo pipefail
          NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
          HASH="$(jq -r '.sha256' "release-bundle/release-manifest-v${RELEASE_VERSION}.json")"
""",
    """        env:
          RELEASE_STARTED_EPOCH: ${{ steps.release_start.outputs.started_epoch }}
          RELEASE_STARTED_AT: ${{ steps.release_start.outputs.started_at }}
          GITHUB_RELEASE_EPOCH: ${{ steps.github_release.outputs.created_epoch }}
          GITHUB_RELEASE_AT: ${{ steps.github_release.outputs.created_at }}
          GREASYFORK_EPOCH: ${{ steps.external.outputs.greasyfork_epoch }}
          GREASYFORK_ATTEMPTS: ${{ steps.external.outputs.greasyfork_attempts }}
          BACKUP_EPOCH: ${{ steps.external.outputs.backup_epoch }}
          DISCORD_EPOCH: ${{ steps.discord.outputs.posted_epoch }}
          DISCORD_AT: ${{ steps.discord.outputs.posted_at }}
          VALIDATED_SHA: ${{ inputs.validated_sha }}
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: |
          set -euo pipefail
          NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
          VERIFIED_EPOCH="$(date +%s)"
          HASH="$(jq -r '.sha256' "release-bundle/release-manifest-v${RELEASE_VERSION}.json")"
""",
    "record timing environment",
)
text = once(
    text,
    """          python3 .github/scripts/generate_release_dashboard.py
          python3 .github/scripts/build_stable_update_manifest.py
          test "$(jq -r '.version' status/update-manifest.json)" = "$RELEASE_VERSION"
          git config user.name "github-actions[bot]"
""",
    """          python3 .github/scripts/generate_release_dashboard.py
          python3 .github/scripts/build_stable_update_manifest.py
          test "$(jq -r '.version' status/update-manifest.json)" = "$RELEASE_VERSION"
          SOURCE_SHA="${VALIDATED_SHA:-$(git rev-parse HEAD)}"
          PR_JSON="$(gh api -H 'Accept: application/vnd.github+json' "repos/${GITHUB_REPOSITORY}/commits/${SOURCE_SHA}/pulls" 2>/dev/null || echo '[]')"
          PR_NUMBER="$(jq -r '.[0].number // empty' <<< "$PR_JSON")"
          PR_CREATED_AT="$(jq -r '.[0].created_at // empty' <<< "$PR_JSON")"
          PR_MERGED_AT="$(jq -r '.[0].merged_at // empty' <<< "$PR_JSON")"
          PR_TO_VERIFIED=null; MERGE_TO_GITHUB=null; MERGE_TO_VERIFIED=null
          if [[ -n "$PR_CREATED_AT" ]]; then PR_TO_VERIFIED=$(( VERIFIED_EPOCH - $(date -d "$PR_CREATED_AT" +%s) )); fi
          if [[ -n "$PR_MERGED_AT" ]]; then
            PR_MERGED_EPOCH="$(date -d "$PR_MERGED_AT" +%s)"
            MERGE_TO_GITHUB=$(( GITHUB_RELEASE_EPOCH - PR_MERGED_EPOCH ))
            MERGE_TO_VERIFIED=$(( VERIFIED_EPOCH - PR_MERGED_EPOCH ))
          fi
          python3 .github/scripts/record_release_speed.py --version "$RELEASE_VERSION" --source "$SOURCE_SHA" --pr "${PR_NUMBER:-}" --pr-created "$PR_CREATED_AT" --merged "$PR_MERGED_AT" --release-started "$RELEASE_STARTED_AT" --github-release "$GITHUB_RELEASE_AT" --discord "$DISCORD_AT" --verified "$NOW" --pr-to-verified "$PR_TO_VERIFIED" --merge-to-github "$MERGE_TO_GITHUB" --merge-to-verified "$MERGE_TO_VERIFIED" --release-workflow "$(( VERIFIED_EPOCH - RELEASE_STARTED_EPOCH ))" --greasyfork "$(( GREASYFORK_EPOCH - GITHUB_RELEASE_EPOCH ))" --backup "$(( BACKUP_EPOCH - GITHUB_RELEASE_EPOCH ))" --discord-seconds "$(( DISCORD_EPOCH - GITHUB_RELEASE_EPOCH ))" --attempts "$GREASYFORK_ATTEMPTS"
          python3 .github/scripts/generate_release_speed_dashboard.py
          git config user.name "github-actions[bot]"
""",
    "speed recording",
)
text = once(
    text,
    """            status/update-manifest.json \\
            .github/greasyfork-version.txt
""",
    """            status/update-manifest.json \\
            status/release-speed-history.json \\
            status/RELEASE_SPEED.md \\
            .github/greasyfork-version.txt
""",
    "speed files commit",
)
text = between(
    text,
    "      - name: Publish GitHub Pages\n",
    "      - name: Write release summary\n",
    """      - name: Dispatch GitHub Pages asynchronously
        id: pages
        env:
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: |
          set -euo pipefail
          gh workflow run github-pages.yml --ref main
          echo "dispatched=true" >> "$GITHUB_OUTPUT"
          echo "GitHub Pages deployment dispatched asynchronously."

""",
    "asynchronous Pages",
)
text = text.replace("PAGES_RUN_ID: ${{ steps.pages.outputs.pages_run_id }}", "PAGES_DISPATCHED: ${{ steps.pages.outputs.dispatched }}")
text = text.replace("- ✅ Canonical source validated", "- ✅ Exact immutable canonical-validation candidate consumed")
text = text.replace("- ✅ JavaScript syntax checked", "- ✅ Duplicate release-readiness and production rebuilds skipped")
text = text.replace("- ✅ Immutable release bundle prepared", "- ✅ Immutable release bundle reused without rebuilding")
text = text.replace("- ✅ Greasy Fork version verified", "- ✅ Greasy Fork verification and private backup ran concurrently\n            echo \"- ✅ Greasy Fork version verified\"")
text = text.replace("- ✅ Dashboard, stable update manifest and announcement tracker updated atomically", "- ✅ Dashboard, release-speed telemetry, stable update manifest and announcement tracker updated atomically")
text = text.replace("- ✅ GitHub Pages deployment completed: run ${PAGES_RUN_ID}", "- ✅ GitHub Pages deployment dispatched asynchronously: ${PAGES_DISPATCHED}")
save(path, text)


history = {
    "schemaVersion": 1,
    "targets": {
        "normalHotfixPrToVerifiedMedianSeconds": 240,
        "normalHotfixPrToVerifiedP90Seconds": 420,
        "mergeToVerifiedMedianSeconds": 60,
        "mergeToGitHubReleaseMedianSeconds": 40
    },
    "releases": [
        {"version":"8.0.1","pipelineVersion":3,"benchmarkClass":"normal","includeInHotfixBaseline":True,"pullRequest":538,"prCreatedAt":"2026-07-26T08:30:33Z","mergedAt":"2026-07-26T09:02:31Z","verifiedAt":"2026-07-26T09:03:57Z","durationsSeconds":{"prToVerified":2004,"mergeToVerified":86}},
        {"version":"8.0.2","pipelineVersion":3,"benchmarkClass":"binary-transfer-exception","includeInHotfixBaseline":False,"pullRequest":540,"prCreatedAt":"2026-07-26T10:06:29Z","mergedAt":"2026-07-26T13:38:20Z","verifiedAt":"2026-07-26T13:39:45Z","durationsSeconds":{"prToVerified":12796,"mergeToVerified":85}},
        {"version":"8.0.3","pipelineVersion":3,"benchmarkClass":"normal","includeInHotfixBaseline":True,"pullRequest":542,"prCreatedAt":"2026-07-26T14:02:09Z","mergedAt":"2026-07-26T14:31:18Z","verifiedAt":"2026-07-26T14:33:11Z","durationsSeconds":{"prToVerified":1862,"mergeToVerified":113}}
    ]
}
save("status/release-speed-history.json", json.dumps(history, indent=2) + "\n")

save(".github/scripts/record_release_speed.py", '''#!/usr/bin/env python3
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser()
for name in ("version","source","pr","pr_created","merged","release_started","github_release","discord","verified","pr_to_verified","merge_to_github","merge_to_verified","release_workflow","greasyfork","backup","discord_seconds","attempts"):
    p.add_argument("--"+name.replace("_","-"), dest=name, default="")
a=p.parse_args()
def n(v): return None if v in ("","null") else int(v)
path=Path("status/release-speed-history.json")
data=json.loads(path.read_text(encoding="utf-8"))
record={"version":a.version,"pipelineVersion":4,"benchmarkClass":"normal","includeInHotfixBaseline":True,"sourceSha256":a.source,"pullRequest":n(a.pr),"prCreatedAt":a.pr_created or None,"mergedAt":a.merged or None,"releaseStartedAt":a.release_started,"githubReleaseAt":a.github_release,"discordPostedAt":a.discord,"verifiedAt":a.verified,"durationsSeconds":{"prToVerified":n(a.pr_to_verified),"mergeToGitHubRelease":n(a.merge_to_github),"mergeToVerified":n(a.merge_to_verified),"releaseWorkflow":n(a.release_workflow),"greasyForkPropagation":n(a.greasyfork),"privateBackup":n(a.backup),"discordAfterGitHubRelease":n(a.discord_seconds)},"greasyForkAttempts":n(a.attempts)}
data["releases"]=[r for r in data["releases"] if r.get("version")!=a.version]+[record]
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
''')

save(".github/scripts/generate_release_speed_dashboard.py", '''#!/usr/bin/env python3
import json, math, statistics
from pathlib import Path
root=Path(__file__).resolve().parents[2]
data=json.loads((root/"status/release-speed-history.json").read_text(encoding="utf-8"))
def vals(records,key): return [r.get("durationsSeconds",{}).get(key) for r in records if isinstance(r.get("durationsSeconds",{}).get(key),int)]
def pct(v,p):
    if not v:return None
    s=sorted(v);return s[max(0,math.ceil(len(s)*p)-1)]
def fmt(v):
    if v is None:return "—"
    m,s=divmod(round(v),60);return f"{m}m {s:02d}s" if m else f"{s}s"
base=[r for r in data["releases"] if r.get("pipelineVersion")==3 and r.get("includeInHotfixBaseline")]
v4=[r for r in data["releases"] if r.get("pipelineVersion")==4]
b=vals(base,"prToVerified");f=vals(v4,"prToVerified");bm=round(statistics.median(b));target=data["targets"]["normalHotfixPrToVerifiedMedianSeconds"]
lines=["# Release Speed Control","","> Machine-generated release telemetry for Pipeline v4.","","## Headline","",f"- **Historical normal-hotfix median:** {fmt(bm)}",f"- **Pipeline v4 target median:** {fmt(target)}",f"- **Expected reduction:** {round((1-target/bm)*100,1)}%",f"- **Expected throughput:** {round(bm/target,1)}×",f"- **Measured Pipeline v4 median:** {fmt(statistics.median(f) if f else None)}","","## Statistics","","| Metric | v3 baseline | v4 measured | v4 target |","|---|---:|---:|---:|",f"| PR → verified median | {fmt(bm)} | {fmt(statistics.median(f) if f else None)} | {fmt(target)} |",f"| PR → verified P90 | {fmt(pct(b,.9))} | {fmt(pct(f,.9))} | {fmt(data['targets']['normalHotfixPrToVerifiedP90Seconds'])} |",f"| Merge → verified median | {fmt(statistics.median(vals(base,'mergeToVerified')))} | {fmt(statistics.median(vals(v4,'mergeToVerified')) if vals(v4,'mergeToVerified') else None)} | {fmt(data['targets']['mergeToVerifiedMedianSeconds'])} |","","## Release history","","| Version | Pipeline | Class | PR → verified | Merge → GitHub | Merge → verified | Greasy Fork | Backup |","|---|---:|---|---:|---:|---:|---:|---:|"]
for r in reversed(data["releases"]):
    d=r.get("durationsSeconds",{});lines.append(f"| {r.get('version')} | v{r.get('pipelineVersion')} | {r.get('benchmarkClass')} | {fmt(d.get('prToVerified'))} | {fmt(d.get('mergeToGitHubRelease'))} | {fmt(d.get('mergeToVerified'))} | {fmt(d.get('greasyForkPropagation'))} | {fmt(d.get('privateBackup'))} |")
lines += ["","The v8.0.2 binary-transfer exception is retained for transparency but excluded from the normal-hotfix baseline. GitHub Pages is asynchronous and does not block userscript delivery.",""]
(root/"status/RELEASE_SPEED.md").write_text("\n".join(lines),encoding="utf-8")
''')
subprocess.run(["python3", ".github/scripts/generate_release_speed_dashboard.py"], cwd=ROOT, check=True)

save(".github/scripts/test_release_pipeline_v4.py", '''#!/usr/bin/env python3
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
v=(r/".github/workflows/validate-userscript.yml").read_text()
a=(r/".github/workflows/auto-release-after-validation.yml").read_text()
p=(r/".github/workflows/release-toolkit.yml").read_text()
assert "Prepare immutable release-ready bundle" in v and "release-bundle/" in v
assert "release-readiness-check.yml" not in a and "validation_run_id:" in a and "validated_sha:" in a
for token in ("Resolve exact immutable release candidate","Verify Greasy Fork and back up concurrently","BACKUP_PID=$!","GF_PID=$!","sleep 2","sleep 5","sleep 15","Dispatch GitHub Pages asynchronously","status/release-speed-history.json","status/RELEASE_SPEED.md"):
    assert token in p, token
assert "gh run watch" not in p
h=json.loads((r/"status/release-speed-history.json").read_text())
assert h["targets"]["normalHotfixPrToVerifiedMedianSeconds"]==240
assert "Expected reduction" in (r/"status/RELEASE_SPEED.md").read_text()
print("Release Pipeline v4 contract passed.")
''')
subprocess.run(["python3", ".github/scripts/test_release_pipeline_v4.py"], cwd=ROOT, check=True)

preflight=ROOT/".github/scripts/run_userscript_preflight.sh"
payload=preflight.read_text(encoding="utf-8")
if ".github/scripts/test_release_pipeline_v4.py" not in payload:
    payload=payload.replace("node .github/scripts/test_transport_sweep_runtime.js","python3 .github/scripts/test_release_pipeline_v4.py\nnode .github/scripts/test_transport_sweep_runtime.js",1)
preflight.write_text(payload,encoding="utf-8")

save("docs/RELEASE_PIPELINE_V4.md", '''# Release Pipeline v4 — Maximum-Speed Verified Delivery

Pipeline v4 builds one immutable release-ready candidate, verifies it against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.

The manual readiness workflow remains available for recovery releases where no immutable validation candidate is supplied.

## Targets

- Normal critical hotfix PR → verified release median: 4 minutes.
- Normal critical hotfix PR → verified release P90: 7 minutes.
- Merge → GitHub Release median: 40 seconds.
- Merge → fully verified release median: 60 seconds.

See `status/RELEASE_SPEED.md` for live measurements.
''')

print(json.dumps({"issue":543,"pipelineVersion":4,"targetMedianSeconds":240},indent=2))
