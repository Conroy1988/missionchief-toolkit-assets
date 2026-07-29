#!/usr/bin/env python3
"""Issue #543: repair exact-candidate release attribution and complete Pipeline v4 telemetry."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return value.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Automatic promotion: resolve exact successful head validation without
# depending on fragile branch or workflow-run pull_requests metadata.
# ---------------------------------------------------------------------------
auto_path = ".github/workflows/auto-release-after-validation.yml"
auto = read(auto_path)
auto = replace_once(
    auto,
    "      validated_sha: ${{ steps.candidate.outputs.validated_sha }}\n",
    "      validated_sha: ${{ steps.candidate.outputs.validated_sha }}\n"
    "      implementation_ready_at: ${{ steps.candidate.outputs.implementation_ready_at }}\n"
    "      validation_completed_at: ${{ steps.candidate.outputs.validation_completed_at }}\n",
    "automatic release outputs",
)
auto = replace_once(
    auto,
    "          echo \"validated_sha=$MERGE_SHA\" >> \"$GITHUB_OUTPUT\"\n",
    "          echo \"validated_sha=$MERGE_SHA\" >> \"$GITHUB_OUTPUT\"\n"
    "          echo \"implementation_ready_at=\" >> \"$GITHUB_OUTPUT\"\n"
    "          echo \"validation_completed_at=\" >> \"$GITHUB_OUTPUT\"\n",
    "automatic release initial outputs",
)
auto = replace_once(
    auto,
    "          PR_HEAD_REF: ${{ github.event.pull_request.head.ref }}\n",
    "",
    "obsolete PR head branch environment",
)
auto = replace_once(
    auto,
    "            -f branch=\"$PR_HEAD_REF\" \\\n",
    "",
    "fragile workflow branch filter",
)
old_run_lookup = '''          VALIDATION_RUN_ID="$(jq -r \\
            --arg head "$PR_HEAD_SHA" \\
            --argjson pr "$PR_NUMBER" \\
            '[.workflow_runs[]
              | select(.conclusion == "success")
              | select(.head_sha == $head)
              | select(any(.pull_requests[]?; .number == $pr))]
             | sort_by(.updated_at)
             | last
             | .id // empty' \\
            /tmp/validation-runs.json)"
'''
new_run_lookup = '''          VALIDATION_RUN_ID="$(jq -r \\
            --arg head "$PR_HEAD_SHA" \\
            '[.workflow_runs[]
              | select(.conclusion == "success")
              | select(.head_sha == $head)]
             | sort_by(.updated_at)
             | last
             | .id // empty' \\
            /tmp/validation-runs.json)"
'''
auto = replace_once(auto, old_run_lookup, new_run_lookup, "exact-head validation run lookup")
auto = replace_once(
    auto,
    '''          if [[ -z "$VALIDATION_RUN_ID" ]]; then
            echo "No successful exact-head PR validation was found; dispatching guarded main fallback."
            gh workflow run validate-userscript.yml --ref main
            exit 0
          fi

          gh api "repos/${GITHUB_REPOSITORY}/actions/runs/${VALIDATION_RUN_ID}/artifacts" > /tmp/validation-artifacts.json
''',
    '''          if [[ -z "$VALIDATION_RUN_ID" ]]; then
            echo "No successful exact-head PR validation was found; dispatching guarded main fallback."
            gh workflow run validate-userscript.yml --ref main
            exit 0
          fi

          VALIDATION_COMPLETED_AT="$(jq -r --argjson id "$VALIDATION_RUN_ID" '.workflow_runs[] | select(.id == $id) | .updated_at // empty' /tmp/validation-runs.json)"
          IMPLEMENTATION_READY_AT="$(gh api "repos/${GITHUB_REPOSITORY}/commits/${PR_HEAD_SHA}" --jq '.commit.committer.date // .commit.author.date // empty')"
          [[ -n "$VALIDATION_COMPLETED_AT" && -n "$IMPLEMENTATION_READY_AT" ]] || {
            echo "::error::Exact implementation-ready and validation-completion timestamps were not resolved."
            exit 1
          }
          echo "implementation_ready_at=$IMPLEMENTATION_READY_AT" >> "$GITHUB_OUTPUT"
          echo "validation_completed_at=$VALIDATION_COMPLETED_AT" >> "$GITHUB_OUTPUT"

          gh api "repos/${GITHUB_REPOSITORY}/actions/runs/${VALIDATION_RUN_ID}/artifacts" > /tmp/validation-artifacts.json
''',
    "validation timing evidence",
)
old_artifact_lookup = '''          ARTIFACT_ID="$(jq -r \\
            '[.artifacts[]
              | select(.expired == false)
              | select(.name | startswith("missionchief-toolkit-validation-candidate-"))]
             | sort_by(.created_at)
             | last
             | .id // empty' \\
            /tmp/validation-artifacts.json)"
'''
new_artifact_lookup = '''          ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"
          ARTIFACT_ID="$(jq -r --arg name "$ARTIFACT_NAME" \\
            '[.artifacts[]
              | select(.expired == false)
              | select(.name == $name)]
             | sort_by(.created_at)
             | last
             | .id // empty' \\
            /tmp/validation-artifacts.json)"
'''
auto = replace_once(auto, old_artifact_lookup, new_artifact_lookup, "exact validation artifact lookup")
auto = replace_once(
    auto,
    '''      validation_run_id: ${{ github.run_id }}
      validated_sha: ${{ needs.prepare_pr.outputs.validated_sha }}
''',
    '''      validation_run_id: ${{ github.run_id }}
      validated_sha: ${{ needs.prepare_pr.outputs.validated_sha }}
      pull_request_number: ${{ format('{0}', github.event.pull_request.number) }}
      pr_created_at: ${{ github.event.pull_request.created_at }}
      pr_merged_at: ${{ github.event.pull_request.merged_at }}
      implementation_ready_at: ${{ needs.prepare_pr.outputs.implementation_ready_at }}
      validation_completed_at: ${{ needs.prepare_pr.outputs.validation_completed_at }}
''',
    "automatic production telemetry inputs",
)
write(auto_path, auto)


# ---------------------------------------------------------------------------
# Release workflow: preserve candidate identity before the mirror commit and
# accept authoritative PR/timing metadata from the automatic promoter.
# ---------------------------------------------------------------------------
release_path = ".github/workflows/release-toolkit.yml"
release = read(release_path)
call_validated = '''      validated_sha:
        description: "Exact validated main commit SHA"
        required: false
        default: ""
        type: string
'''
call_extra = call_validated + '''      pull_request_number:
        description: "Associated merged pull request number for telemetry"
        required: false
        default: ""
        type: string
      pr_created_at:
        description: "Associated pull request creation timestamp"
        required: false
        default: ""
        type: string
      pr_merged_at:
        description: "Associated pull request merge timestamp"
        required: false
        default: ""
        type: string
      implementation_ready_at:
        description: "Final candidate commit timestamp"
        required: false
        default: ""
        type: string
      validation_completed_at:
        description: "Exact successful PR validation completion timestamp"
        required: false
        default: ""
        type: string
'''
release = replace_once(release, call_validated, call_extra, "workflow-call telemetry inputs")
dispatch_validated = '''      validated_sha:
        description: "Optional exact validated main commit SHA"
        required: false
        default: ""
        type: string
'''
dispatch_extra = dispatch_validated + '''      pull_request_number:
        description: "Optional associated merged pull request number"
        required: false
        default: ""
        type: string
      pr_created_at:
        description: "Optional pull request creation timestamp"
        required: false
        default: ""
        type: string
      pr_merged_at:
        description: "Optional pull request merge timestamp"
        required: false
        default: ""
        type: string
      implementation_ready_at:
        description: "Optional final candidate commit timestamp"
        required: false
        default: ""
        type: string
      validation_completed_at:
        description: "Optional exact validation completion timestamp"
        required: false
        default: ""
        type: string
'''
release = replace_once(release, dispatch_validated, dispatch_extra, "workflow-dispatch telemetry inputs")
release = replace_once(
    release,
    '''          echo "started_epoch=$(date +%s)" >> "$GITHUB_OUTPUT"
          echo "started_at=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_OUTPUT"
''',
    '''          echo "started_epoch=$(date +%s)" >> "$GITHUB_OUTPUT"
          echo "started_at=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_OUTPUT"
          echo "source_sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"
''',
    "pre-mirror candidate SHA capture",
)
release = replace_once(
    release,
    '''          VALIDATED_SHA: ${{ inputs.validated_sha }}
          GH_TOKEN: ${{ github.token }}
''',
    '''          VALIDATED_SHA: ${{ inputs.validated_sha }}
          RELEASE_SOURCE_SHA: ${{ steps.release_start.outputs.source_sha }}
          SOURCE_PR_NUMBER: ${{ inputs.pull_request_number }}
          SOURCE_PR_CREATED_AT: ${{ inputs.pr_created_at }}
          SOURCE_PR_MERGED_AT: ${{ inputs.pr_merged_at }}
          SOURCE_IMPLEMENTATION_READY_AT: ${{ inputs.implementation_ready_at }}
          SOURCE_VALIDATION_COMPLETED_AT: ${{ inputs.validation_completed_at }}
          GH_TOKEN: ${{ github.token }}
''',
    "release telemetry environment",
)
old_attribution = '''          SOURCE_SHA="${VALIDATED_SHA:-$(git rev-parse HEAD)}"
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
'''
new_attribution = '''          SOURCE_SHA="${VALIDATED_SHA:-$RELEASE_SOURCE_SHA}"
          [[ "$SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "::error::Exact release candidate commit was not preserved."; exit 1; }
          PR_NUMBER="$SOURCE_PR_NUMBER"
          PR_CREATED_AT="$SOURCE_PR_CREATED_AT"
          PR_MERGED_AT="$SOURCE_PR_MERGED_AT"
          IMPLEMENTATION_READY_AT="$SOURCE_IMPLEMENTATION_READY_AT"
          VALIDATION_COMPLETED_AT="$SOURCE_VALIDATION_COMPLETED_AT"
          if [[ -z "$PR_NUMBER" || -z "$PR_CREATED_AT" || -z "$PR_MERGED_AT" ]]; then
            PR_JSON="$(gh api -H 'Accept: application/vnd.github+json' "repos/${GITHUB_REPOSITORY}/commits/${SOURCE_SHA}/pulls" 2>/dev/null || echo '[]')"
            RESOLVED_PR="$(jq -c '[.[] | select(.merged_at != null and .base.ref == "main")] | sort_by(.merged_at) | last // {}' <<< "$PR_JSON")"
            [[ -n "$PR_NUMBER" ]] || PR_NUMBER="$(jq -r '.number // empty' <<< "$RESOLVED_PR")"
            [[ -n "$PR_CREATED_AT" ]] || PR_CREATED_AT="$(jq -r '.created_at // empty' <<< "$RESOLVED_PR")"
            [[ -n "$PR_MERGED_AT" ]] || PR_MERGED_AT="$(jq -r '.merged_at // empty' <<< "$RESOLVED_PR")"
          fi
          PR_TO_VERIFIED=null; MERGE_TO_GITHUB=null; MERGE_TO_VERIFIED=null
          IMPLEMENTATION_TO_GREEN=null; GREEN_TO_MERGE=null
          if [[ -n "$PR_CREATED_AT" ]]; then PR_TO_VERIFIED=$(( VERIFIED_EPOCH - $(date -d "$PR_CREATED_AT" +%s) )); fi
          if [[ -n "$PR_MERGED_AT" ]]; then
            PR_MERGED_EPOCH="$(date -d "$PR_MERGED_AT" +%s)"
            MERGE_TO_GITHUB=$(( GITHUB_RELEASE_EPOCH - PR_MERGED_EPOCH ))
            MERGE_TO_VERIFIED=$(( VERIFIED_EPOCH - PR_MERGED_EPOCH ))
          fi
          if [[ -n "$IMPLEMENTATION_READY_AT" && -n "$VALIDATION_COMPLETED_AT" ]]; then
            IMPLEMENTATION_TO_GREEN=$(( $(date -d "$VALIDATION_COMPLETED_AT" +%s) - $(date -d "$IMPLEMENTATION_READY_AT" +%s) ))
          fi
          if [[ -n "$VALIDATION_COMPLETED_AT" && -n "$PR_MERGED_AT" ]]; then
            GREEN_TO_MERGE=$(( $(date -d "$PR_MERGED_AT" +%s) - $(date -d "$VALIDATION_COMPLETED_AT" +%s) ))
          fi
          for duration in "$PR_TO_VERIFIED" "$MERGE_TO_GITHUB" "$MERGE_TO_VERIFIED" "$IMPLEMENTATION_TO_GREEN" "$GREEN_TO_MERGE"; do
            [[ "$duration" == "null" || "$duration" -ge 0 ]] || { echo "::error::Release telemetry produced a negative duration."; exit 1; }
          done
          python3 .github/scripts/record_release_speed.py --version "$RELEASE_VERSION" --source "$SOURCE_SHA" --pr "${PR_NUMBER:-}" --pr-created "$PR_CREATED_AT" --merged "$PR_MERGED_AT" --implementation-ready "$IMPLEMENTATION_READY_AT" --validation-completed "$VALIDATION_COMPLETED_AT" --release-started "$RELEASE_STARTED_AT" --github-release "$GITHUB_RELEASE_AT" --discord "$DISCORD_AT" --verified "$NOW" --implementation-to-green "$IMPLEMENTATION_TO_GREEN" --green-to-merge "$GREEN_TO_MERGE" --pr-to-verified "$PR_TO_VERIFIED" --merge-to-github "$MERGE_TO_GITHUB" --merge-to-verified "$MERGE_TO_VERIFIED" --release-workflow "$(( VERIFIED_EPOCH - RELEASE_STARTED_EPOCH ))" --greasyfork "$(( GREASYFORK_EPOCH - GITHUB_RELEASE_EPOCH ))" --backup "$(( BACKUP_EPOCH - GITHUB_RELEASE_EPOCH ))" --discord-seconds "$(( DISCORD_EPOCH - GITHUB_RELEASE_EPOCH ))" --attempts "$GREASYFORK_ATTEMPTS"
'''
release = replace_once(release, old_attribution, new_attribution, "exact release attribution")
release = replace_once(
    release,
    '            echo "- ✅ Dashboard, release-speed telemetry, stable update manifest and announcement tracker updated atomically"\n',
    '            echo "- ✅ Candidate, implementation-to-green, PR, merge and publication telemetry attributed to the exact validated commit"\n'
    '            echo "- ✅ Dashboard, release-speed telemetry, stable update manifest and announcement tracker updated atomically"\n',
    "release telemetry summary",
)
write(release_path, release)


# Manual/owner recovery releases should still preserve the exact authorized
# main candidate for attribution, even though they intentionally retain full
# readiness and fallback validation.
owner_path = ".github/workflows/owner-release-command.yml"
owner = read(owner_path)
owner = replace_once(
    owner,
    '''      version: ${{ needs.authorize.outputs.version }}
      confirmation: RELEASE
''',
    '''      version: ${{ needs.authorize.outputs.version }}
      confirmation: RELEASE
      validated_sha: ${{ needs.authorize.outputs.expected_main }}
''',
    "owner-command candidate SHA handoff",
)
write(owner_path, owner)


# ---------------------------------------------------------------------------
# Telemetry recorder and dashboard schema.
# ---------------------------------------------------------------------------
record_path = ".github/scripts/record_release_speed.py"
record_current = read(record_path)
if '"sourceSha256":a.source' not in record_current:
    raise RuntimeError("release-speed recorder authority moved")
record_new = '''#!/usr/bin/env python3
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser()
for name in ("version","source","pr","pr_created","merged","implementation_ready","validation_completed","release_started","github_release","discord","verified","implementation_to_green","green_to_merge","pr_to_verified","merge_to_github","merge_to_verified","release_workflow","greasyfork","backup","discord_seconds","attempts"):
    p.add_argument("--"+name.replace("_","-"), dest=name, default="")
a=p.parse_args()
def n(v): return None if v in ("","null") else int(v)
path=Path("status/release-speed-history.json")
data=json.loads(path.read_text(encoding="utf-8"))
data["schemaVersion"]=2
for previous in data.get("releases",[]):
    if "sourceSha256" in previous:
        previous["recordedCommit"]=previous.pop("sourceSha256")
record={
    "version":a.version,
    "pipelineVersion":4,
    "benchmarkClass":"normal",
    "includeInHotfixBaseline":True,
    "candidateCommit":a.source,
    "pullRequest":n(a.pr),
    "prCreatedAt":a.pr_created or None,
    "mergedAt":a.merged or None,
    "implementationReadyAt":a.implementation_ready or None,
    "validationCompletedAt":a.validation_completed or None,
    "releaseStartedAt":a.release_started,
    "githubReleaseAt":a.github_release,
    "discordPostedAt":a.discord,
    "verifiedAt":a.verified,
    "durationsSeconds":{
        "implementationToGreen":n(a.implementation_to_green),
        "greenToMerge":n(a.green_to_merge),
        "prToVerified":n(a.pr_to_verified),
        "mergeToGitHubRelease":n(a.merge_to_github),
        "mergeToVerified":n(a.merge_to_verified),
        "releaseWorkflow":n(a.release_workflow),
        "greasyForkPropagation":n(a.greasyfork),
        "privateBackup":n(a.backup),
        "discordAfterGitHubRelease":n(a.discord_seconds),
    },
    "greasyForkAttempts":n(a.attempts),
}
data["releases"]=[r for r in data["releases"] if r.get("version")!=a.version]+[record]
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
'''
write(record_path, record_new)

generator_path = ".github/scripts/generate_release_speed_dashboard.py"
generator_current = read(generator_path)
if "Machine-generated release telemetry for Pipeline v4" not in generator_current:
    raise RuntimeError("release-speed dashboard generator authority moved")
generator_new = '''#!/usr/bin/env python3
import json, math, statistics
from pathlib import Path
root=Path(__file__).resolve().parents[2]
data=json.loads((root/"status/release-speed-history.json").read_text(encoding="utf-8"))
def vals(records,key): return [r.get("durationsSeconds",{}).get(key) for r in records if isinstance(r.get("durationsSeconds",{}).get(key),int)]
def pct(v,p):
    if not v:return None
    s=sorted(v);return s[max(0,math.ceil(len(s)*p)-1)]
def med(v): return statistics.median(v) if v else None
def fmt(v):
    if v is None:return "—"
    m,s=divmod(round(v),60);return f"{m}m {s:02d}s" if m else f"{s}s"
base=[r for r in data["releases"] if r.get("pipelineVersion")==3 and r.get("includeInHotfixBaseline")]
v4=[r for r in data["releases"] if r.get("pipelineVersion")==4]
b=vals(base,"prToVerified");f=vals(v4,"prToVerified");implementation=vals(v4,"implementationToGreen")
bm=round(statistics.median(b));target=data["targets"]["normalHotfixPrToVerifiedMedianSeconds"]
lines=[
    "# Release Speed Control","","> Machine-generated exact-candidate release telemetry for Pipeline v4.","",
    "## Headline","",
    f"- **Historical normal-hotfix median:** {fmt(bm)}",
    f"- **Pipeline v4 target median:** {fmt(target)}",
    f"- **Expected reduction:** {round((1-target/bm)*100,1)}%",
    f"- **Expected throughput:** {round(bm/target,1)}×",
    f"- **Measured Pipeline v4 median:** {fmt(med(f))}",
    f"- **Measured implementation-ready → green median:** {fmt(med(implementation))}","",
    "## Statistics","",
    "| Metric | v3 baseline | v4 measured | v4 target |",
    "|---|---:|---:|---:|",
    f"| Implementation-ready → green median | — | {fmt(med(implementation))} | measured only |",
    f"| PR → verified median | {fmt(bm)} | {fmt(med(f))} | {fmt(target)} |",
    f"| PR → verified P90 | {fmt(pct(b,.9))} | {fmt(pct(f,.9))} | {fmt(data['targets']['normalHotfixPrToVerifiedP90Seconds'])} |",
    f"| Merge → verified median | {fmt(med(vals(base,'mergeToVerified')))} | {fmt(med(vals(v4,'mergeToVerified')))} | {fmt(data['targets']['mergeToVerifiedMedianSeconds'])} |","",
    "## Release history","",
    "| Version | Pipeline | Class | Implementation → green | Green → merge | PR → verified | Merge → GitHub | Merge → verified | Greasy Fork | Backup |",
    "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
]
for r in reversed(data["releases"]):
    d=r.get("durationsSeconds",{})
    lines.append(f"| {r.get('version')} | v{r.get('pipelineVersion')} | {r.get('benchmarkClass')} | {fmt(d.get('implementationToGreen'))} | {fmt(d.get('greenToMerge'))} | {fmt(d.get('prToVerified'))} | {fmt(d.get('mergeToGitHubRelease'))} | {fmt(d.get('mergeToVerified'))} | {fmt(d.get('greasyForkPropagation'))} | {fmt(d.get('privateBackup'))} |")
lines += ["","The v8.0.2 binary-transfer exception is retained for transparency but excluded from the normal-hotfix baseline. GitHub Pages is asynchronous and does not block userscript delivery. Null historical fields are displayed as em dashes rather than inferred.",""]
(root/"status/RELEASE_SPEED.md").write_text("\n".join(lines),encoding="utf-8")
'''
write(generator_path, generator_new)


# Backfill the completed v8.2.7 benchmark only from immutable GitHub evidence:
# final candidate commit, aggregate gate logs, PR metadata and production release
# telemetry already recorded by the release workflow.
history_path = "status/release-speed-history.json"
history = json.loads(read(history_path))
history["schemaVersion"] = 2
for previous in history.get("releases", []):
    if "sourceSha256" in previous:
        previous["recordedCommit"] = previous.pop("sourceSha256")
record = next((item for item in history["releases"] if item.get("version") == "8.2.7"), None)
if not record:
    raise RuntimeError("v8.2.7 release record is missing")
expected_release_times = {
    "releaseStartedAt": "2026-07-29T00:13:15Z",
    "githubReleaseAt": "2026-07-29T00:13:27Z",
    "verifiedAt": "2026-07-29T00:13:40Z",
}
for key, expected in expected_release_times.items():
    if record.get(key) != expected:
        raise RuntimeError(f"v8.2.7 {key} authority moved: {record.get(key)!r}")
record.update({
    "candidateCommit": "fba7b31a9425e43cdb034c15321364e82f7dcfd0",
    "pullRequest": 582,
    "prCreatedAt": "2026-07-28T23:58:13Z",
    "mergedAt": "2026-07-29T00:11:09Z",
    "implementationReadyAt": "2026-07-29T00:09:27Z",
    "validationCompletedAt": "2026-07-29T00:10:24Z",
    "telemetryAttribution": "backfilled-from-exact-github-commit-gate-pr-and-release-evidence",
})
record["durationsSeconds"].update({
    "implementationToGreen": 57,
    "greenToMerge": 45,
    "prToVerified": 927,
    "mergeToGitHubRelease": 138,
    "mergeToVerified": 151,
})
write(history_path, json.dumps(history, indent=2) + "\n")


# Executable contract now covers exact-head resolution, exact artifact naming,
# direct timestamps, candidate preservation and the evidence-backed backfill.
test_path = ".github/scripts/test_release_pipeline_v4.py"
test_new = '''#!/usr/bin/env python3
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
v=(r/".github/workflows/validate-userscript.yml").read_text()
a=(r/".github/workflows/auto-release-after-validation.yml").read_text()
p=(r/".github/workflows/release-toolkit.yml").read_text()
o=(r/".github/workflows/owner-release-command.yml").read_text()
rec=(r/".github/scripts/record_release_speed.py").read_text()
assert "Prepare immutable release-ready bundle" in v and "release-bundle/" in v
assert "release-readiness-check.yml" not in a and "validation_run_id:" in a and "validated_sha:" in a
assert "Consume exact successful PR validation tree" in a
assert "Upload promoted merged-main candidate" in a
assert "Post-merge userscript validation used: no" in a
assert "No release-critical path changed; exact candidate promotion is intentionally skipped." in a
assert "Path-aware release candidate required" in a
assert '-f branch="$PR_HEAD_REF"' not in a
assert "pull_requests[]" not in a
assert 'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"' in a
assert 'select(.name == $name)' in a
for token in ("implementation_ready_at","validation_completed_at","pull_request_number","pr_created_at","pr_merged_at"):
    assert token in a, token
for token in ("Resolve exact immutable release candidate","Verify Greasy Fork and back up concurrently","BACKUP_PID=$!","GF_PID=$!","sleep 2","sleep 5","sleep 15","Dispatch GitHub Pages asynchronously","status/release-speed-history.json","status/RELEASE_SPEED.md","source_sha=$(git rev-parse HEAD)","IMPLEMENTATION_TO_GREEN","GREEN_TO_MERGE"):
    assert token in p, token
assert "gh run watch" not in p
assert 'validated_sha: ${{ needs.authorize.outputs.expected_main }}' in o
assert '"candidateCommit":a.source' in rec and "sourceSha256" not in rec
h=json.loads((r/"status/release-speed-history.json").read_text())
assert h["schemaVersion"]==2
assert h["targets"]["normalHotfixPrToVerifiedMedianSeconds"]==240
v827=next(item for item in h["releases"] if item["version"]=="8.2.7")
assert v827["candidateCommit"]=="fba7b31a9425e43cdb034c15321364e82f7dcfd0"
assert v827["pullRequest"]==582
assert v827["durationsSeconds"]["implementationToGreen"]==57
assert v827["durationsSeconds"]["greenToMerge"]==45
assert v827["durationsSeconds"]["prToVerified"]==927
assert v827["durationsSeconds"]["mergeToGitHubRelease"]==138
assert v827["durationsSeconds"]["mergeToVerified"]==151
dashboard=(r/"status/RELEASE_SPEED.md").read_text()
assert "Implementation-ready → green median" in dashboard
assert "| 8.2.7 | v4 | normal | 57s | 45s | 15m 27s | 2m 18s | 2m 31s | 13s | 6s |" in dashboard
assert chr(1) not in p
assert p.count("      - name: Record successful release, manifest, announcement and speed state") == 1
assert 'echo "- ✅ Greasy Fork verification and private backup ran concurrently"' in p
assert 'GitHub Pages deployment dispatched asynchronously: ${PAGES_DISPATCHED}' in p
assert "name: Toolkit Hotfix Gate" in v
assert "test_consolidated_pr_gate.py" in v
assert "test_path_aware_blocking.py" in v
print("Release Pipeline v4 exact-candidate attribution and complete telemetry contract passed.")
'''
write(test_path, test_new)

docs_path = "docs/RELEASE_PIPELINE_V4.md"
docs = read(docs_path)
docs = replace_once(
    docs,
    "Pipeline v4 builds one immutable release-ready candidate, verifies it against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.\n",
    "Pipeline v4 builds one immutable release-ready candidate, resolves it by exact head SHA and exact artifact name, verifies it against the exact current `main` commit, reuses it without rebuilding, runs Greasy Fork verification and private backup concurrently, posts Discord only after both succeed, records timing telemetry, and dispatches GitHub Pages asynchronously.\n",
    "Pipeline v4 overview",
)
docs = replace_once(
    docs,
    "The manual readiness workflow remains available for recovery releases where no immutable validation candidate is supplied.\n",
    "The automatic path passes authoritative PR creation/merge timestamps plus implementation-ready and validation-completion timestamps directly into production. The release workflow also captures the candidate commit before the stable mirror commit, so telemetry cannot be attributed to release-state writes. The manual readiness workflow remains available for recovery releases where no immutable validation candidate is supplied.\n",
    "Pipeline v4 telemetry documentation",
)
docs += "\n## Telemetry attribution\n\nThe live history records implementation-ready → green, green → merge, PR → verified, merge → GitHub Release, merge → verified ledger, Greasy Fork propagation and private backup. Historical null fields are never guessed; v8.2.7 is backfilled only from immutable GitHub commit, gate, pull-request and release evidence.\n"
write(docs_path, docs)

subprocess.run([sys.executable, str(ROOT / generator_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / test_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / record_path), str(ROOT / generator_path), str(ROOT / test_path)], cwd=ROOT, check=True)
print(json.dumps({
    "issue": 543,
    "schemaVersion": 2,
    "v8.2.7": {
        "implementationToGreen": 57,
        "greenToMerge": 45,
        "prToVerified": 927,
        "mergeToGitHubRelease": 138,
        "mergeToVerified": 151,
    },
    "automaticPromotion": "exact-head-exact-artifact",
    "candidateIdentity": "captured-before-stable-mirror",
}, indent=2))
