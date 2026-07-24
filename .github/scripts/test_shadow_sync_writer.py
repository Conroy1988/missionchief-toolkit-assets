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
    for key, expected in expected_writer.items():
        if writer.get(key) != expected:
            raise AssertionError(f"writerRehearsal {key}={writer.get(key)!r}, expected {expected!r}")

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
            "Apply owner-authorized shadow changes",
            "Verify post-operation shadow parity",
            "missionchief-shadow-sync-${{ inputs.mode }}-${{ inputs.target }}-${{ inputs.source_sha }}",
            "retention-days: 30",
        ],
        "Shadow sync workflow",
    )
    forbid(
        workflow,
        [
            "pull_request_target:",
            "schedule:",
            "contents: write",
            "HEAD:refs/heads/main",
            "git update-ref refs/heads/main",
            "gh api repos/${GITHUB_REPOSITORY}/git/refs/heads/main",
            "secrets: inherit",
        ],
        "Shadow sync workflow",
    )

    require(
        script,
        [
            '"release-state"',
            '"distribution"',
            'value == "main"',
            'branch == "main"',
            'f"HEAD:refs/heads/{branch}"',
            '"DEVELOPMENT_PR_TOKEN is required for apply mode"',
            '"owner-token-rehearsal"',
            '"publicMainChanged": False',
            '"liveConsumersChanged": False',
            '"workflowContentsWrite": False',
            '"narrowly scoped GitHub App"',
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
            '"liveConsumerCutoverAllowed": True',
        ],
        "Shadow sync script",
    )

    for marker in [
        "sync-shadow-branches.yml",
        "sync_shadow_branches.py",
        "DEVELOPMENT_PR_TOKEN",
        "release-state",
        "distribution",
        "cannot update public `main`",
    ]:
        if marker not in document:
            raise AssertionError(f"Human inventory is missing shadow writer marker: {marker}")

    result = subprocess.run(["python3", str(SCRIPT), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Shadow synchronization self-tests failed")

    print("Shadow sync writer passed: manual owner confirmation, fixed targets, read-only workflow permission and no main mutation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
