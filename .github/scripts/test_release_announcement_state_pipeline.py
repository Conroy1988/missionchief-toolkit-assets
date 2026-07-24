#!/usr/bin/env python3
"""Contracts for authoritative announcement state and read-only verification."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / ".github" / "workflows" / "release-toolkit.yml"
VERIFY = ROOT / ".github" / "workflows" / "reconcile-release-announcement-state.yml"
DASHBOARD = ROOT / "status" / "release-dashboard.json"
TRACKER = ROOT / ".github" / "greasyfork-version.txt"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains forbidden marker: {marker}")


def main() -> int:
    release = RELEASE.read_text(encoding="utf-8")
    verify = VERIFY.read_text(encoding="utf-8")
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    tracker = TRACKER.read_text(encoding="utf-8").strip()

    require(
        release,
        [
            "Post verified release to Discord",
            "Prepare governed release-state worktree",
            "Prepare authoritative production state projection",
            "release_recovery_state.py prepare-production",
            "Publish backward-compatible main state copy",
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
            "Record Toolkit ${RELEASE_VERSION} compatibility state",
            "Publish authoritative release-state ledger",
            "Record Toolkit ${RELEASE_VERSION} verified release state",
            "Verify authoritative and compatibility state parity",
            "Authoritative release-state ledger committed",
            "Backward-compatible main state copied",
        ],
        "Production release workflow",
    )
    discord_index = release.index("      - name: Post verified release to Discord")
    prepare_index = release.index("      - name: Prepare governed release-state worktree")
    projection_index = release.index("      - name: Prepare authoritative production state projection")
    compatibility_index = release.index("      - name: Publish backward-compatible main state copy")
    authority_index = release.index("      - name: Publish authoritative release-state ledger")
    parity_index = release.index("      - name: Verify authoritative and compatibility state parity")
    if not (
        discord_index
        < prepare_index
        < projection_index
        < compatibility_index
        < authority_index
        < parity_index
    ):
        raise AssertionError(
            "Verified Discord publication must precede one state projection, the compatibility copy, "
            "the authoritative release-state commit and the parity gate"
        )

    require(
        verify,
        [
            "name: Verify Release Announcement State",
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Verify dashboard and announcement tracker",
            "announcementTrackerChanged: false",
            "Upload immutable announcement-state evidence",
            "missionchief-release-announcement-state-${{ github.sha }}",
            "No automatic mutation was attempted.",
        ],
        "Announcement-state verification workflow",
    )
    forbid(
        verify,
        [
            "contents: write",
            "git commit",
            "git push",
            "git pull --rebase",
            "github-actions[bot]",
            "git reset --hard",
        ],
        "Announcement-state verification workflow",
    )

    latest = dashboard.get("latestRelease") or {}
    if str(latest.get("version") or "") != tracker:
        raise AssertionError("Committed compatibility announcement tracker does not match latest verified release")
    if latest.get("greasyForkVerified") is not True:
        raise AssertionError("Latest verified release is not marked Greasy Fork verified")
    if latest.get("discordPosted") is not True:
        raise AssertionError("Latest verified release is not marked Discord posted")

    print(
        "Release announcement state passed: release-state authority, byte-identical compatibility copy "
        "and read-only verification."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
