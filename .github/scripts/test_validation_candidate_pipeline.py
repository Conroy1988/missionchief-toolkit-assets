#!/usr/bin/env python3
"""Static and executable contracts for artifact-only validated-tree release authority."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / ".github/workflows/validate-userscript.yml"
AUTOMATIC = ROOT / ".github/workflows/auto-release-after-validation.yml"
OWNER = ROOT / ".github/workflows/owner-release-command.yml"
RELEASE = ROOT / ".github/workflows/release-toolkit.yml"
SYNC = ROOT / ".github/scripts/sync_greasyfork_root_mirror.sh"
VERIFIER = ROOT / ".github/scripts/verify_validation_candidate.py"
DASHBOARD = ROOT / "status/release-dashboard.json"
DASHBOARD_GENERATOR = ROOT / ".github/scripts/generate_release_dashboard.py"
RETIRED_RECONCILER = ROOT / ".github/scripts/reconcile_validation_dashboard.py"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains forbidden marker: {marker}")


def main() -> int:
    validation = VALIDATION.read_text(encoding="utf-8")
    automatic = AUTOMATIC.read_text(encoding="utf-8")
    owner = OWNER.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    sync = SYNC.read_text(encoding="utf-8")
    generator = DASHBOARD_GENERATOR.read_text(encoding="utf-8")
    reconciler = RETIRED_RECONCILER.read_text(encoding="utf-8")
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))

    require(validation, [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Write immutable validation candidate evidence",
        'SOURCE_TREE="$(git rev-parse HEAD^{tree})"',
        "sourceTree: $sourceTree",
        "headCommit: $headCommit",
        "pullRequest: $pullRequest",
        "missionchief-toolkit-validation-candidate-${{ github.sha }}",
        "publicMainChanged: false",
        "releaseDashboardChanged: false",
        "verify_validation_candidate.py --self-test",
        "name: Toolkit Hotfix Gate",
        "name: Classify changed paths",
        "classify_pr_paths.py",
        "name: Runtime lane",
        "name: Integrity lane",
        "name: Performance lane",
        "name: Repository lane",
    ], "Canonical validation workflow")
    forbid(validation, [
        "contents: write",
        "reconcile_validation_dashboard.py",
        "status/release-dashboard.json",
        "git commit",
        "git push",
        "git pull --rebase",
        "github-actions[bot]",
        "  push:\n",
    ], "Canonical validation workflow")

    require(automatic, [
        "types:\n      - closed",
        "workflows:\n      - Toolkit Hotfix Gate",
        "github.event.pull_request.merged == true",
        "Consume exact successful PR validation tree",
        "actions/workflows/validate-userscript.yml/runs",
        '--arg head "$PR_HEAD_SHA"',
        "select(.head_sha == $head)",
        "CANDIDATE_ARTIFACT_COUNT",
        'startswith("missionchief-toolkit-validation-candidate-")',
        "Expected exactly one non-expired validation candidate artifact in exact run",
        '[[ "$EVIDENCE_HEAD" == "$PR_HEAD_SHA" ]]',
        '[[ "$EVIDENCE_PR" == "$PR_NUMBER" ]]',
        "implementation_ready_at",
        "validation_completed_at",
        'CURRENT_TREE="$(git rev-parse HEAD^{tree})"',
        "Merged tree ${CURRENT_TREE} differs from validated PR tree ${CANDIDATE_TREE}",
        "promoted_pull_request",
        "Upload promoted merged-main candidate",
        "validation_run_id: ${{ github.run_id }}",
        "Post-merge userscript validation used: no",
        "Post-merge release bundle rebuild used: no",
        "No release-critical path changed; exact candidate promotion is intentionally skipped.",
        "Path-aware release candidate required",
        "gh workflow run validate-userscript.yml --ref main",
        "github.event.workflow_run.event == 'workflow_dispatch'",
    ], "Automatic release workflow")
    forbid(automatic, [
        ".distributionCandidate",
        ".status.validation",
        "status/release-dashboard.json",
        "github.event.workflow_run.event == 'push'",
        "pull_requests[]",
        '-f branch="$PR_HEAD_REF"',
        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
        "workflows:\n      - Validate Canonical Userscript",
    ], "Automatic release workflow")

    require(owner, [
        "Freshly validate requested main candidate",
        "python3 .github/scripts/validate_userscript.py",
        "persist-credentials: false",
        "gh release view \"v${VERSION}\"",
        "dist/release-manifest.json",
        "validated_sha: ${{ needs.authorize.outputs.expected_main }}",
    ], "Owner release workflow")
    forbid(owner, [
        ".distributionCandidate",
        "status/release-dashboard.json",
        "Verify requested version is a validated candidate",
    ], "Owner release workflow")

    require(sync, [
        "git add dist \"$ROOT_USER\" \"$ROOT_TXT\"",
        "Publish Toolkit ${VERSION} stable distribution source",
        "Stable distribution publication commit",
    ], "Stable distribution publication helper")
    require(release, [
        "run: bash .github/scripts/sync_greasyfork_root_mirror.sh",
        "Record successful release, manifest, announcement and speed state",
        "python3 .github/scripts/build_stable_update_manifest.py",
        "source_sha=$(git rev-parse HEAD)",
        "IMPLEMENTATION_TO_GREEN",
        "GREEN_TO_MERGE",
    ], "Production release workflow")

    if "distributionCandidate" in dashboard or "releaseDryRun" in dashboard:
        raise AssertionError("Persistent release dashboard still contains transient validation state")
    require(generator, [
        'sanitized.pop("distributionCandidate", None)',
        'sanitized.pop("releaseDryRun", None)',
        '"storage": "workflow-artifact"',
    ], "Dashboard stable-ledger sanitizer")
    forbid(generator, ['data.get("distributionCandidate"', "candidate.get("], "Dashboard generator")
    require(reconciler, [
        "Retired compatibility stub",
        "is retired; use the exact canonical-validation artifact instead",
    ], "Retired validation-dashboard reconciler")
    forbid(reconciler, [
        "json.loads",
        "write_text",
        "def reconcile",
        "status[",
        "distributionCandidate",
    ], "Retired validation-dashboard reconciler")

    result = subprocess.run(["python3", str(VERIFIER), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Validation candidate verifier self-tests failed")

    print(
        "Validation candidate pipeline passed: exact-head/exact-run candidate-evidence PR-tree promotion, "
        "no post-merge rebuild, guarded current-main fallback and stable-only publication."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
