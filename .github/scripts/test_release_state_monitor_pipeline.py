#!/usr/bin/env python3
"""Contracts for the transitional Greasy Fork fallback tracker on release-state."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "greasyfork-release-monitor.yml"
HELPER = ROOT / ".github" / "scripts" / "release_state_branch.py"
INVENTORY = ROOT / ".github" / "branch-write-inventory.json"
POLICY = ROOT / ".github" / "actions-security-policy.json"
ROLE_POLICY = ROOT / ".github" / "shadow-branch-policy.json"
DOCUMENT = ROOT / "docs" / "BRANCH_WRITE_INVENTORY.md"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains forbidden marker: {marker}")


def main() -> int:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    helper = HELPER.read_text(encoding="utf-8")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    role_policy = json.loads(ROLE_POLICY.read_text(encoding="utf-8"))
    document = DOCUMENT.read_text(encoding="utf-8")

    entries = inventory.get("releaseStateBranchWriters") or []
    if len(entries) != 1:
        raise AssertionError(f"Expected one release-state branch writer, found {len(entries)}")
    entry = entries[0]
    expected = {
        "workflow": ".github/workflows/greasyfork-release-monitor.yml",
        "helper": ".github/scripts/release_state_branch.py",
        "sourceAuthority": "main release dashboard",
        "target": "release-state",
        "writes": [".github/greasyfork-version.txt"],
        "credential": "github.token",
        "actor": "github-actions[bot]",
        "mainMutationAllowed": False,
        "forcePushAllowed": False,
        "liveConsumerCutoverAllowed": False,
        "migrationState": "transitional fallback-tracker authority",
    }
    if entry != expected:
        raise AssertionError("Fallback-monitor release-state inventory changed")

    permissions = policy.get("allowedWritePermissions") or {}
    if permissions.get(entry["workflow"]) != ["contents"]:
        raise AssertionError("Fallback monitor contents-write permission changed")

    release_state = (role_policy.get("branches") or {}).get("release-state") or {}
    governed = set(release_state.get("governedPaths") or [])
    if ".github/greasyfork-version.txt" not in governed:
        raise AssertionError("Release-state policy no longer governs the fallback tracker")

    require(
        workflow,
        [
            "name: Greasy Fork Release Fallback Monitor",
            "permissions:\n  contents: write",
            "group: toolkit-production-release",
            "Check out latest main authority",
            "ref: main",
            "persist-credentials: false",
            "Prepare governed release-state worktree",
            "release_state_branch.py --self-test",
            "release_state_branch.py prepare",
            "RELEASE_STATE_ROOT: ${{ steps.release_state.outputs.root }}",
            "STATE_FILE=\"$RELEASE_STATE_ROOT/.github/greasyfork-version.txt\"",
            "DASHBOARD_FILE=\"status/release-dashboard.json\"",
            "Reconcile release-state tracker from verified main dashboard",
            "git show origin/release-state:.github/greasyfork-version.txt",
            "git show origin/main:status/release-dashboard.json",
            "Record announced version on release-state",
            "release_state_branch.py commit",
            "--path .github/greasyfork-version.txt",
            "GH_TOKEN: ${{ github.token }}",
        ],
        "Fallback monitor workflow",
    )
    forbid(
        workflow,
        [
            "git push origin HEAD:main",
            "git push origin HEAD:refs/heads/main",
            "git reset --hard origin/main",
            "git add \"$STATE_FILE\"",
            "STATE_FILE=\".github/greasyfork-version.txt\"",
            "DEVELOPMENT_PR_TOKEN",
            "MIGRATION_REPO_TOKEN",
        ],
        "Fallback monitor workflow",
    )

    require(
        helper,
        [
            'TARGET_BRANCH = "release-state"',
            'REMOTE_REF = f"refs/remotes/origin/{TARGET_BRANCH}"',
            'PUSH_REF = f"HEAD:refs/heads/{TARGET_BRANCH}"',
            'ROLE_PATH = Path(".github/branch-role.json")',
            '"mode": "shadow-rehearsal"',
            "release-state mutable-path allowlist changed",
            "release-state branch role is immutable",
            "release-state moved after preparation",
            "GH_TOKEN is required to publish release-state changes",
            "http.https://github.com/.extraheader",
            "Release-state branch writer self-tests passed.",
        ],
        "Release-state writer helper",
    )
    forbid(
        helper,
        [
            'TARGET_BRANCH = "main"',
            "HEAD:refs/heads/main",
            "--force",
            "force-with-lease",
            "git reset --hard origin/main",
            '"README.md"',
        ],
        "Release-state writer helper",
    )

    for marker in [
        "fallback announcement tracker is now written only to `release-state`",
        "release_state_branch.py",
        "greasyfork-release-monitor.yml",
        "two workflows that can commit directly to public `main`",
    ]:
        if marker not in document:
            raise AssertionError(f"Human inventory is missing monitor migration marker: {marker}")

    result = subprocess.run(["python3", str(HELPER), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Release-state branch helper self-tests failed")

    print(
        "Fallback monitor release-state contract passed: main dashboard authority, "
        "single governed tracker path, no main mutation and normal non-force branch push."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
