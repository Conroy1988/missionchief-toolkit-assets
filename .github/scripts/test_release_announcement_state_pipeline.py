#!/usr/bin/env python3
"""Contracts for atomic release announcement state and read-only verification."""

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

    require(release, [
        "Post verified release to Discord",
        "Record successful release and announcement state",
        "printf '%s\\n' \"$RELEASE_VERSION\" > .github/greasyfork-version.txt",
        "git add status/release-dashboard.json status/README.md .github/greasyfork-version.txt",
        "Release dashboard and announcement tracker updated atomically",
    ], "Production release workflow")
    discord_index = release.index("      - name: Post verified release to Discord")
    state_index = release.index("      - name: Record successful release and announcement state")
    publish_index = release.index("      - name: Publish update channels in parallel")
    if not discord_index < state_index < publish_index:
        raise AssertionError("Announcement state must be recorded after Discord and before update-channel publication")

    require(verify, [
        "name: Verify Release Announcement State",
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Verify dashboard and announcement tracker",
        "announcementTrackerChanged: false",
        "Upload immutable announcement-state evidence",
        "missionchief-release-announcement-state-${{ github.sha }}",
        "No automatic mutation was attempted.",
    ], "Announcement-state verification workflow")
    forbid(verify, [
        "contents: write",
        "git commit",
        "git push",
        "git pull --rebase",
        "github-actions[bot]",
        "git reset --hard",
    ], "Announcement-state verification workflow")

    latest = dashboard.get("latestRelease") or {}
    if str(latest.get("version") or "") != tracker:
        raise AssertionError("Committed announcement tracker does not match latest verified release")
    if latest.get("greasyForkVerified") is not True:
        raise AssertionError("Latest verified release is not marked Greasy Fork verified")
    if latest.get("discordPosted") is not True:
        raise AssertionError("Latest verified release is not marked Discord posted")

    print("Release announcement state passed: atomic release commit and read-only verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
