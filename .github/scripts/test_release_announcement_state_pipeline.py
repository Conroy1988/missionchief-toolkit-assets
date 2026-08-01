#!/usr/bin/env python3
"""Contracts for atomic release announcement state and read-only verification."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / ".github" / "workflows" / "release-toolkit.yml"
VERIFY = ROOT / ".github" / "workflows" / "reconcile-release-announcement-state.yml"
CARD_OPERATIONS = ROOT / ".github" / "workflows" / "discord-release-preview.yml"
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
    card_operations = CARD_OPERATIONS.read_text(encoding="utf-8")
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    tracker = TRACKER.read_text(encoding="utf-8").strip()

    require(release, [
        "Post verified release to Discord",
        "Record successful release, manifest, announcement and speed state",
        "printf '%s\\n' \"$RELEASE_VERSION\" > .github/greasyfork-version.txt",
        "python3 .github/scripts/build_stable_update_manifest.py",
        "status/update-manifest.json",
        "discord-release-response.json",
        "message_id=$DISCORD_MESSAGE_ID",
        "discordMessageId:$discordMessageId",
        "Dashboard, release-speed telemetry, stable update manifest and announcement tracker updated atomically",
    ], "Production release workflow")
    discord_index = release.index("      - name: Post verified release to Discord")
    state_index = release.index("      - name: Record successful release, manifest, announcement and speed state")
    pages_index = release.index("      - name: Dispatch GitHub Pages asynchronously")
    if not discord_index < state_index < pages_index:
        raise AssertionError("Announcement state must be recorded after Discord and before asynchronous Pages dispatch")

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
    if latest.get("tkbDistributionVerified") is not True:
        raise AssertionError("Latest verified release is not marked TKB distribution verified")
    if latest.get("discordPosted") is not True:
        raise AssertionError("Latest verified release is not marked Discord posted")
    for key in ("discordMessageId", "discordChannelId"):
        if not str(latest.get(key) or "").isdigit():
            raise AssertionError(f"Latest verified release has no stored {key}")

    require(card_operations, [
        "Refresh verified release card in place",
        "github.event.comment.user.login == github.repository_owner",
        "github.event.comment.author_association == 'OWNER'",
        "startsWith(github.event.comment.body, '/refresh-release-card ')",
        "Only the current verified release card can be refreshed.",
        "'.distribution.productUrl'",
        "'.distribution.installUrl'",
        '--request PATCH --header "Content-Type: application/json"',
        '"${DISCORD_WEBHOOK_URL}/messages/${MESSAGE_ID}"',
    ], "Discord release-card operations workflow")

    print("Release announcement state passed: atomic release commit and read-only verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
