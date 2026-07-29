#!/usr/bin/env python3
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
assert "workflows:\n      - Toolkit Hotfix Gate" in a
assert "workflows:\n      - Validate Canonical Userscript" not in a
assert "Consume exact successful PR validation tree" in a
assert "Upload promoted merged-main candidate" in a
assert "Post-merge userscript validation used: no" in a
assert "No release-critical path changed; exact candidate promotion is intentionally skipped." in a
assert "Path-aware release candidate required" in a
assert '-f branch="$PR_HEAD_REF"' not in a
assert "pull_requests[]" not in a
assert 'CANDIDATE_ARTIFACT_COUNT' in a
assert 'startswith("missionchief-toolkit-validation-candidate-")' in a
assert 'Expected exactly one non-expired validation candidate artifact in exact run' in a
assert '[[ "$EVIDENCE_HEAD" == "$PR_HEAD_SHA" ]]' in a
assert '[[ "$EVIDENCE_PR" == "$PR_NUMBER" ]]' in a
assert 'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"' not in a
for token in ("implementation_ready_at","validation_completed_at","pull_request_number","pr_created_at","pr_merged_at"):
    assert token in a, token
for token in ("Resolve exact immutable release candidate","Verify Greasy Fork and back up concurrently","BACKUP_PID=$!","GF_PID=$!","sleep 2","sleep 5","sleep 15","Dispatch GitHub Pages asynchronously","status/release-speed-history.json","status/RELEASE_SPEED.md","source_sha=$(git rev-parse HEAD)","IMPLEMENTATION_TO_GREEN","GREEN_TO_MERGE"):
    assert token in p, token
assert "gh run watch" not in p
assert 'validated_sha: ${{ needs.authorize.outputs.expected_main }}' in o
assert '"candidateCommit":a.source' in rec and 'previous["recordedCommit"]=previous.pop("sourceSha256")' in rec
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
