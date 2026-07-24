#!/usr/bin/env python3
"""Contracts for Issue #41 atomic stable update-manifest publication."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / ".github" / "scripts" / "build_stable_update_manifest.py"
WORKFLOW = ROOT / ".github" / "workflows" / "publish-update-manifest.yml"
RELEASE = ROOT / ".github" / "workflows" / "release-toolkit.yml"
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
MANIFEST = ROOT / "status" / "update-manifest.json"
DASHBOARD = ROOT / "status" / "release-dashboard.json"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains forbidden marker: {marker}")


def main() -> int:
    builder = BUILDER.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))

    require(
        builder,
        [
            "def build_manifest(dashboard: dict, settings: dict)",
            "def render_manifest(manifest: dict[str, object])",
            '"publicMainChanged": False',
            '"releaseDashboardChanged": False',
            '"liveConsumersChanged": False',
            "Committed stable update manifest differs from the verified release projection",
            "Stable update manifest self-tests passed.",
        ],
        "Stable manifest builder",
    )

    require(
        workflow,
        [
            "name: Verify Toolkit Update Manifest",
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Validate stable manifest builder self-tests",
            "Verify committed manifest against release ledger",
            "--check",
            "Upload immutable update-manifest evidence",
            "missionchief-update-manifest-verification-${{ github.sha }}",
            "retention-days: 30",
            "No repository mutation was attempted.",
        ],
        "Read-only update-manifest workflow",
    )
    forbid(
        workflow,
        [
            "contents: write",
            "git commit",
            "git push",
            "git pull --rebase",
            "github-actions[bot]",
            "DEVELOPMENT_PR_TOKEN",
        ],
        "Read-only update-manifest workflow",
    )

    require(
        release,
        [
            "Record successful release, manifest and announcement state",
            "python3 .github/scripts/build_stable_update_manifest.py",
            "status/update-manifest.json",
            'git commit -m "Record Toolkit ${RELEASE_VERSION} verified release state"',
            "- name: Publish GitHub Pages",
            "gh workflow run github-pages.yml --ref main",
            'gh run watch "$PAGES_RUN_ID" --exit-status',
            "Dashboard, stable update manifest and announcement tracker updated atomically",
        ],
        "Production release workflow",
    )
    forbid(
        release,
        [
            "gh workflow run publish-update-manifest.yml",
            "MANIFEST_RUN_ID",
            "manifest_run_id",
            "Update-manifest publication failed",
        ],
        "Production release workflow",
    )

    state_index = release.index("Record successful release, manifest and announcement state")
    builder_index = release.index("python3 .github/scripts/build_stable_update_manifest.py", state_index)
    add_index = release.index("git add", builder_index)
    push_index = release.index("git push origin HEAD:main", add_index)
    pages_index = release.index("- name: Publish GitHub Pages", push_index)
    assert state_index < builder_index < add_index < push_index < pages_index

    public_url = "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json"
    assert public_url in source, "Existing v5.0.7 manifest consumer URL changed"
    assert manifest["version"] == dashboard["latestRelease"]["version"]
    assert manifest["sha256"] == dashboard["latestRelease"]["sha256"]

    for command in [
        ["python3", str(BUILDER), "--self-test"],
        ["python3", str(BUILDER), "--check"],
    ]:
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode != 0:
            raise AssertionError(f"Stable update-manifest command failed: {' '.join(command)}")

    print("Atomic update-manifest pipeline passed: one release-state commit, read-only verification and unchanged public URL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
