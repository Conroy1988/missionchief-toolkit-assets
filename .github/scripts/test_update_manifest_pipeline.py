#!/usr/bin/env python3
"""Contracts for atomic update-manifest publication and read-only verification."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / ".github" / "scripts" / "build_stable_update_manifest.py"
RELEASE = ROOT / ".github" / "workflows" / "release-toolkit.yml"
VERIFY = ROOT / ".github" / "workflows" / "publish-update-manifest.yml"


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
    release = RELEASE.read_text(encoding="utf-8")
    verify = VERIFY.read_text(encoding="utf-8")

    require(builder, [
        "def build_manifest(dashboard: dict, settings: dict)",
        '"githubRelease": "published"',
        '"greasyForkSync": "verified"',
        '"backup": "private-repository-verified"',
        '"discordRelease": "posted"',
        '"releaseReadiness": "passed"',
        '"channel": "stable"',
        "Committed stable update manifest differs from the verified release projection.",
        "Stable update-manifest self-tests passed.",
    ], "Stable update-manifest builder")

    require(release, [
        "Record successful release, manifest and announcement state",
        "python3 .github/scripts/build_stable_update_manifest.py",
        "status/update-manifest.json",
        "Publish GitHub Pages",
        "gh workflow run github-pages.yml --ref main",
        "Dashboard, update manifest and announcement tracker committed atomically",
    ], "Production release workflow")
    forbid(release, [
        "gh workflow run publish-update-manifest.yml",
        "MANIFEST_RUN_ID",
        "manifest_run_id",
        "Update-manifest publication failed",
    ], "Production release workflow")

    discord_index = release.index("      - name: Post verified release to Discord")
    state_index = release.index("      - name: Record successful release, manifest and announcement state")
    pages_index = release.index("      - name: Publish GitHub Pages")
    if not discord_index < state_index < pages_index:
        raise AssertionError("Manifest/state commit must follow Discord and precede Pages publication")

    require(verify, [
        "name: Verify Toolkit Update Manifest",
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Validate manifest-builder self-tests",
        "Verify committed manifest projection",
        "build_stable_update_manifest.py --check",
        "updateManifestChanged: false",
        "Upload immutable manifest evidence",
        "missionchief-update-manifest-verification-${{ github.sha }}",
        "No automatic mutation was attempted.",
    ], "Update-manifest verification workflow")
    forbid(verify, [
        "contents: write",
        "git commit",
        "git push",
        "git pull --rebase",
        "github-actions[bot]",
        "gh workflow run",
    ], "Update-manifest verification workflow")

    for command, label in [
        (["python3", str(BUILDER), "--self-test"], "builder self-tests"),
        (["python3", str(BUILDER), "--check"], "committed manifest projection"),
    ]:
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode != 0:
            raise AssertionError(f"Stable update-manifest {label} failed")

    print("Stable update-manifest pipeline passed: atomic release commit and read-only verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
