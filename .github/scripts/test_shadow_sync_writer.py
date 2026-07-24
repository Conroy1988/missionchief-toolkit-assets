#!/usr/bin/env python3
"""Contracts for the Issue #41 owner-authenticated shadow sync rehearsal."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "shadow-branch-policy.json"
INVENTORY = ROOT / ".github" / "branch-write-inventory.json"
SECURITY = ROOT / ".github" / "actions-security-policy.json"
SCRIPT = ROOT / ".github" / "scripts" / "sync_shadow_branches.py"
WORKFLOW = ROOT / ".github" / "workflows" / "sync-shadow-branches.yml"
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
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    security = json.loads(SECURITY.read_text(encoding="utf-8"))
    script = SCRIPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    document = DOCUMENT.read_text(encoding="utf-8")

    writer = policy.get("writerRehearsal") or {}
    expected_writer = {
        "enabled": True,
        "manualDispatchOnly": True,
        "authorizedActor": "Conroy1988",
        "sourceBranch": "main",
        "allowedTargets": ["release-state", "distribution"],
        "planConfirmation": "PLAN SHADOW SYNC",
        "applyConfirmation": "SYNC SHADOWS",
        "credentialSecret": "DEVELOPMENT_PR_TOKEN",
        "workflowPermission": "contents: read",
        "allowIdempotentEmptyProbeCommit": True,
        "liveConsumerCutoverAllowed": False,
        "replacementIdentity": "narrowly scoped GitHub App",
    }
    if writer != expected_writer:
        raise AssertionError("writerRehearsal policy changed")

    release_state = (policy.get("branches") or {}).get("release-state") or {}
    expected_state_paths = [
        "status/release-dashboard.json",
        "status/README.md",
        "status/update-manifest.json",
        ".github/greasyfork-version.txt",
    ]
    if release_state.get("mirroredPaths") != []:
        raise AssertionError("release-state must have no manual mirror-copy paths")
    if release_state.get("operationalPaths") != expected_state_paths:
        raise AssertionError("release-state operational ledger changed")
    if release_state.get("operationalWriters") != [
        ".github/workflows/greasyfork-release-monitor.yml",
        ".github/workflows/release-recovery.yml",
    ]:
        raise AssertionError("release-state operational writers changed")

    entries = inventory.get("shadowBranchWriters") or []
    if len(entries) != 1:
        raise AssertionError(f"Expected one reviewed shadow writer, found {len(entries)}")
    entry = entries[0]
    for key, expected in {
        "workflow": ".github/workflows/sync-shadow-branches.yml",
        "script": ".github/scripts/sync_shadow_branches.py",
        "source": "main",
        "targets": ["release-state", "distribution"],
        "credential": "DEVELOPMENT_PR_TOKEN",
        "workflowPermission": "contents: read",
        "dispatch": "manual owner-confirmed rehearsal",
        "mainMutationAllowed": False,
        "liveConsumerCutoverAllowed": False,
        "replacementIdentity": "narrowly scoped GitHub App",
    }.items():
        if entry.get(key) != expected:
            raise AssertionError(f"Shadow writer inventory {key} changed")

    if ".github/workflows/sync-shadow-branches.yml" in (security.get("allowedWritePermissions") or {}):
        raise AssertionError("Shadow sync workflow must not receive workflow-level write permission")

    require(
        workflow,
        [
            "name: Rehearse Shadow Branch Synchronization",
            "workflow_dispatch:",
            "permissions:\n  contents: read",
            "github.actor == 'Conroy1988'",
            "github.ref == 'refs/heads/main'",
            "ref: main",
            "persist-credentials: false",
            "PLAN SHADOW SYNC",
            "SYNC SHADOWS",
            "source_sha",
            "write_probe",
            "+refs/heads/release-state:refs/remotes/origin/release-state",
            "+refs/heads/distribution:refs/remotes/origin/distribution",
            "DEVELOPMENT_PR_TOKEN",
            "sync_shadow_branches.py --self-test",
            "Verify post-operation shadow parity",
        ],
        "Shadow sync workflow",
    )
    forbid(
        workflow,
        ["schedule:", "contents: write", "HEAD:refs/heads/main", "secrets: inherit"],
        "Shadow sync workflow",
    )

    require(
        script,
        [
            "Synchronize only reviewed mirror files",
            "preserves every operational",
            'RELEASE_STATE_PATHS = [',
            'RELEASE_STATE_WRITERS = [',
            'mirrored != [] or operational != RELEASE_STATE_PATHS',
            'writers != RELEASE_STATE_WRITERS',
            'mirrored_paths, operational_paths = validate_path_classes',
            'for path in mirrored_paths:',
            'for path in operational_paths:',
            '"mode": "operational-preserved"',
            '"preservedOperationalPaths": operational_paths',
            "operational path was modified during mirror sync",
            '"DEVELOPMENT_PR_TOKEN is required for apply mode"',
            '"owner-token-rehearsal"',
            '"publicMainChanged": False',
            '"externalConsumersChanged": False',
            '"workflowContentsWrite": False',
            "Shadow synchronization self-tests passed.",
        ],
        "Shadow sync script",
    )
    forbid(
        script,
        [
            '"HEAD:refs/heads/main"',
            "git update-ref refs/heads/main",
            "git push origin HEAD:main",
            'paths = list(branch_policy["governedPaths"])',
            "push --force",
            "force-with-lease",
        ],
        "Shadow sync script",
    )

    for marker in [
        "sync-shadow-branches.yml",
        "DEVELOPMENT_PR_TOKEN",
        "release-state",
        "distribution",
        "public `main` rejected as a target",
        "manual synchronizer has no file-copy authority on `release-state`",
    ]:
        if marker not in document:
            raise AssertionError(f"Human inventory is missing shadow writer marker: {marker}")

    result = subprocess.run(["python3", str(SCRIPT), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Shadow synchronization self-tests failed")

    print(
        "Shadow sync writer passed: release-state mirror set empty, operational ledger preserved, "
        "distribution mirror-only and no main mutation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
