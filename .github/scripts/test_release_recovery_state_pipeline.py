#!/usr/bin/env python3
"""Contracts for Issue #41 release recovery state on release-state."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "release-recovery.yml"
STATE = ROOT / ".github" / "scripts" / "release_recovery_state.py"
BRANCH = ROOT / ".github" / "scripts" / "release_state_branch.py"
INVENTORY = ROOT / ".github" / "branch-write-inventory.json"
POLICY = ROOT / ".github" / "shadow-branch-policy.json"
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
    state = STATE.read_text(encoding="utf-8")
    branch = BRANCH.read_text(encoding="utf-8")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    document = DOCUMENT.read_text(encoding="utf-8")

    state_entries = {
        entry["workflow"]: entry
        for entry in (inventory.get("releaseStateBranchWriters") or [])
    }
    expected = {
        "workflow": ".github/workflows/release-recovery.yml",
        "helper": ".github/scripts/release_recovery_state.py",
        "branchHelper": ".github/scripts/release_state_branch.py",
        "sourceAuthority": "verified GitHub Release bundle plus governed recovery inputs",
        "target": "release-state",
        "writes": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ],
        "credential": "github.token",
        "actor": "github-actions[bot]",
        "mainMutationAllowed": False,
        "forcePushAllowed": False,
        "liveConsumerCutoverAllowed": False,
        "migrationState": "operational recovery ledger authority",
    }
    if state_entries.get(expected["workflow"]) != expected:
        raise AssertionError("Release recovery inventory changed")

    release_state = (policy.get("branches") or {}).get("release-state") or {}
    if release_state.get("operationalPaths") != expected["writes"]:
        raise AssertionError("Release-state recovery path authority changed")
    if release_state.get("operationalWriters") != [
        ".github/workflows/greasyfork-release-monitor.yml",
        ".github/workflows/release-recovery.yml",
    ]:
        raise AssertionError("Release-state recovery writers changed")
    if release_state.get("mirroredPaths") != []:
        raise AssertionError("Release-state cannot retain mirror-copy authority")
    if release_state.get("externalConsumersEnabled") is not False:
        raise AssertionError("Release-state external consumers must remain disabled")

    require(
        workflow,
        [
            "name: Release Recovery",
            "permissions:\n  contents: write",
            "group: toolkit-production-release",
            "Check out latest main authority",
            "ref: main",
            "persist-credentials: false",
            "VERIFY ${RELEASE_VERSION}",
            "RETRY GREASYFORK ${RELEASE_VERSION}",
            "RETRY BACKUP ${RELEASE_VERSION}",
            "RETRY DISCORD ${RELEASE_VERSION}",
            "REBUILD DASHBOARD ${RELEASE_VERSION}",
            "REPAIR ASSETS ${RELEASE_VERSION}",
            "Verify recovery-state self-tests",
            "Prepare governed release-state worktree",
            "release_state_branch.py prepare",
            "Seed recovery ledger from verified main compatibility state",
            "release_recovery_state.py seed",
            "Record Greasy Fork recovery on release-state",
            "record-greasyfork",
            "Record private backup recovery on release-state",
            "record-backup",
            "Claim Discord retry on release-state without posting",
            "claim-discord",
            "Finalize Discord recovery on release-state",
            "finalize-discord",
            "Rebuild verified release dashboard on release-state",
            "rebuild-dashboard",
            "Repair stable GitHub Release assets",
            "Recovery ledger: \\`release-state\\`",
            "Public main changed: no",
        ],
        "Release recovery workflow",
    )
    forbid(
        workflow,
        [
            "git push origin HEAD:main",
            "git push origin HEAD:refs/heads/main",
            "git pull --rebase origin main",
            "git reset --hard origin/main",
            "git add status/release-dashboard.json",
            "git add \"$DASHBOARD\"",
            "github-actions[bot]@users.noreply.github.com",
        ],
        "Release recovery workflow",
    )

    require(
        state,
        [
            "Apply controlled Toolkit recovery-state transitions",
            'DASHBOARD_REL = Path("status/release-dashboard.json")',
            'README_REL = Path("status/README.md")',
            'MANIFEST_REL = Path("status/update-manifest.json")',
            'TRACKER_REL = Path(".github/greasyfork-version.txt")',
            "seed_from_main",
            "record_greasyfork",
            "record_backup",
            "claim_discord",
            "finalize_discord",
            "rebuild_dashboard",
            "render_dashboard(state_root)",
            "build_manifest(state_root)",
            "commit_state",
            "Discord recovery claim changed before finalization",
            "Release recovery state self-tests passed.",
        ],
        "Release recovery state helper",
    )
    forbid(
        state,
        [
            "git push",
            "HEAD:refs/heads/main",
            "git reset --hard origin/main",
            "force-with-lease",
            "DEVELOPMENT_PR_TOKEN",
        ],
        "Release recovery state helper",
    )

    require(
        branch,
        [
            'TARGET_BRANCH = "release-state"',
            'PUSH_REF = f"HEAD:refs/heads/{TARGET_BRANCH}"',
            "release-state branch role is immutable",
            "release-state moved after preparation",
            "GH_TOKEN is required to publish release-state changes",
        ],
        "Release-state branch helper",
    )

    for marker in [
        "release recovery ledger is now written only to `release-state`",
        "release_recovery_state.py",
        "release-recovery.yml",
        "one workflow that can commit directly to public `main`",
    ]:
        if marker not in document:
            raise AssertionError(f"Human inventory is missing recovery migration marker: {marker}")

    for helper in [BRANCH, STATE]:
        result = subprocess.run(["python3", str(helper), "--self-test"], cwd=ROOT)
        if result.returncode != 0:
            raise AssertionError(f"Self-tests failed: {helper.name}")

    print(
        "Release recovery state contract passed: guarded API side effects, release-state-only ledger, "
        "atomic Discord claim/finalization and no public-main mutation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
