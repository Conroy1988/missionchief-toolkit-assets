#!/usr/bin/env python3
"""Contracts for authoritative production state on release-state."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"
STATE = ROOT / ".github" / "scripts" / "release_recovery_state.py"
BRANCH = ROOT / ".github" / "scripts" / "release_state_branch.py"
POLICY = ROOT / ".github" / "shadow-branch-policy.json"
INVENTORY = ROOT / ".github" / "branch-write-inventory.json"
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
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    document = DOCUMENT.read_text(encoding="utf-8")

    release_state = (policy.get("branches") or {}).get("release-state") or {}
    expected_paths = [
        "status/release-dashboard.json",
        "status/README.md",
        "status/update-manifest.json",
        ".github/greasyfork-version.txt",
    ]
    if release_state.get("primaryProductionWriter") != ".github/workflows/release-toolkit.yml":
        raise AssertionError("Primary release-state writer changed")
    if release_state.get("operationalPaths") != expected_paths:
        raise AssertionError("Primary release-state paths changed")
    mirror = release_state.get("compatibilityMirror") or {}
    if mirror != {
        "branch": "main",
        "paths": expected_paths,
        "requiredForRuntimeVersionsThrough": "5.0.7",
        "externalConsumersEnabled": True,
        "retirementRequiresVersionedMigration": True,
    }:
        raise AssertionError("Main compatibility mirror policy changed")
    if release_state.get("externalConsumersEnabled") is not False:
        raise AssertionError("Direct release-state consumers must remain disabled")

    direct = inventory.get("directMainWriters") or []
    if len(direct) != 1 or direct[0].get("workflow") != ".github/workflows/release-toolkit.yml":
        raise AssertionError("Production is not the sole direct main writer")
    state_entries = {
        entry["workflow"]: entry
        for entry in (inventory.get("releaseStateBranchWriters") or [])
    }
    production_entry = state_entries.get(".github/workflows/release-toolkit.yml") or {}
    if production_entry.get("writes") != expected_paths:
        raise AssertionError("Production release-state inventory paths changed")
    if production_entry.get("mainMutationPurpose") != (
        "byte-identical compatibility copy for runtime versions through 5.0.7"
    ):
        raise AssertionError("Production compatibility purpose changed")

    require(
        workflow,
        [
            "name: Release Toolkit",
            "group: toolkit-production-release",
            "Prepare governed release-state worktree",
            "release_state_branch.py prepare",
            "Prepare authoritative production state projection",
            "release_recovery_state.py prepare-production",
            "Publish backward-compatible main state copy",
            "Record Toolkit ${RELEASE_VERSION} compatibility state",
            "git push origin HEAD:main",
            "Publish authoritative release-state ledger",
            "release_state_branch.py commit",
            "Record Toolkit ${RELEASE_VERSION} verified release state",
            "Verify authoritative and compatibility state parity",
            'git show "origin/release-state:${path}"',
            "Authoritative release-state ledger committed",
            "Backward-compatible main state copied",
        ],
        "Production release workflow",
    )
    for path in expected_paths:
        if path not in workflow:
            raise AssertionError(f"Production workflow omits state path: {path}")

    projection_index = workflow.index("Prepare authoritative production state projection")
    compatibility_index = workflow.index("Publish backward-compatible main state copy")
    authority_index = workflow.index("Publish authoritative release-state ledger")
    parity_index = workflow.index("Verify authoritative and compatibility state parity")
    pages_index = workflow.index("Publish GitHub Pages")
    if not projection_index < compatibility_index < authority_index < parity_index < pages_index:
        raise AssertionError("Production dual-publication ordering changed")

    require(
        state,
        [
            "production can prepare one deterministic projection",
            "STATE_PATHS = [DASHBOARD_REL, README_REL, MANIFEST_REL, TRACKER_REL]",
            "def build_complete_state(",
            "def prepare_production(",
            "Prepared authoritative Toolkit v{version} production state",
            'production = subcommands.add_parser("prepare-production")',
            "validate_timestamp",
            "build_manifest(state_root)",
            "Release recovery state self-tests passed.",
        ],
        "Governed release-state builder",
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
    forbid(
        branch,
        ["HEAD:refs/heads/main", "force-with-lease", "push --force"],
        "Release-state branch helper",
    )

    for marker in [
        "release-state is now the primary production state authority",
        "one workflow can still commit a compatibility copy to public `main`",
        "runtime versions through v5.0.7",
    ]:
        if marker not in document:
            raise AssertionError(f"Human inventory is missing production-state marker: {marker}")

    for helper in [BRANCH, STATE]:
        result = subprocess.run(["python3", str(helper), "--self-test"], cwd=ROOT)
        if result.returncode != 0:
            raise AssertionError(f"Self-tests failed: {helper.name}")

    print(
        "Primary production state contract passed: one deterministic release-state projection, "
        "byte-identical v5.0.7 compatibility mirror, non-force authority commit and parity gate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
