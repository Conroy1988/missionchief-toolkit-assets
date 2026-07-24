#!/usr/bin/env python3
"""Contracts for Issue #41 read-only operational branch governance."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "shadow-branch-policy.json"
SCRIPT = ROOT / ".github" / "scripts" / "verify_shadow_branch_parity.py"
WORKFLOW = ROOT / ".github" / "workflows" / "verify-shadow-branch-parity.yml"


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
    script = SCRIPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    if policy.get("schemaVersion") != 1:
        raise AssertionError("Shadow branch policy schemaVersion must remain 1")
    for key, expected in {
        "mode": "shadow-rehearsal",
        "mainAuthorityPreserved": True,
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }.items():
        if policy.get(key) != expected:
            raise AssertionError(f"Shadow branch policy {key}={policy.get(key)!r}, expected {expected!r}")

    branches = policy.get("branches") or {}
    if set(branches) != {"release-state", "distribution"}:
        raise AssertionError(f"Unexpected operational branches: {sorted(branches)}")

    release_state = branches["release-state"]
    if release_state.get("governedPaths") != [
        "status/release-dashboard.json",
        "status/README.md",
        "status/update-manifest.json",
        ".github/greasyfork-version.txt",
    ]:
        raise AssertionError("release-state governed paths changed")
    if release_state.get("mirroredPaths") != [
        "status/release-dashboard.json",
        "status/README.md",
        "status/update-manifest.json",
    ]:
        raise AssertionError("release-state mirrored paths changed")
    if release_state.get("operationalPaths") != [".github/greasyfork-version.txt"]:
        raise AssertionError("release-state operational paths changed")
    if release_state.get("operationalWriter") != ".github/workflows/greasyfork-release-monitor.yml":
        raise AssertionError("release-state operational writer changed")
    if release_state.get("externalConsumersEnabled") is not False:
        raise AssertionError("release-state external consumers must remain disabled")

    distribution = branches["distribution"]
    expected_distribution = [
        "dist/MissionChief_Map_Command_Toolkit.user.js",
        "dist/MissionChief_Map_Command_Toolkit.txt",
        "dist/SHA256SUMS.txt",
        "dist/release-manifest.json",
        "MissionChief_Map_Command_Toolkit.user.js",
        "MissionChief_Map_Command_Toolkit.txt",
    ]
    if distribution.get("governedPaths") != expected_distribution:
        raise AssertionError("distribution governed paths changed")
    if distribution.get("mirroredPaths") != expected_distribution:
        raise AssertionError("distribution mirrored paths changed")
    if distribution.get("operationalPaths") != []:
        raise AssertionError("distribution cannot have operational paths before cutover")
    if distribution.get("externalConsumersEnabled") is not False:
        raise AssertionError("distribution external consumers must remain disabled")

    require(
        script,
        [
            "Mirrored paths must remain byte-identical",
            "Transitional operational paths may differ",
            'POLICY_PATH = ROOT / ".github" / "shadow-branch-policy.json"',
            '"release-state"',
            '"distribution"',
            '"mode": "shadow-rehearsal"',
            '"liveConsumersEnabled": False',
            '"strictProtectionEnabled": False',
            '"administratorRecoveryRequired": True',
            '"cutoverIssue": 41',
            'operational != [".github/greasyfork-version.txt"]',
            "validate_operational_content",
            'SEMVER.fullmatch(value)',
            '"schemaVersion": 2',
            '"publicMainChanged": False',
            '"externalConsumersChanged": False',
            "Shadow branch parity self-tests passed.",
        ],
        "Operational branch verifier",
    )
    forbid(
        script,
        [
            "git push",
            "git commit",
            "git update-ref",
            "gh api",
            "DEVELOPMENT_PR_TOKEN",
            "contents: write",
        ],
        "Operational branch verifier",
    )

    require(
        workflow,
        [
            "name: Verify Shadow Branch Parity",
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Fetch shadow branch refs read-only",
            "+refs/heads/release-state:refs/remotes/origin/release-state",
            "+refs/heads/distribution:refs/remotes/origin/distribution",
            "Verify governed paths and branch roles",
            "Upload immutable shadow-branch evidence",
            "missionchief-shadow-branch-parity-${{ github.sha }}",
        ],
        "Operational branch verification workflow",
    )
    forbid(
        workflow,
        [
            "contents: write",
            "git push",
            "git commit",
            "github-actions[bot]",
            "DEVELOPMENT_PR_TOKEN",
        ],
        "Operational branch verification workflow",
    )

    result = subprocess.run(["python3", str(SCRIPT), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Operational branch verifier self-tests failed")

    print(
        "Operational branch governance passed: mirrored paths remain equal, "
        "the fallback tracker has a reviewed schema, and no external cutover is enabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
