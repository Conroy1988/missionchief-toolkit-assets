#!/usr/bin/env python3
"""Contracts for TKB-only public release and Discord version authority."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED_MONITOR = ROOT / ".github" / "workflows" / "greasyfork-release-monitor.yml"
PAYLOAD = ROOT / ".github" / "scripts" / "build_discord_release_payload.py"
RELEASE = ROOT / ".github" / "workflows" / "release-toolkit.yml"
RECOVERY = ROOT / ".github" / "workflows" / "release-recovery.yml"
SETTINGS = ROOT / ".github" / "release-settings.json"
INVENTORY = ROOT / ".github" / "branch-write-inventory.json"
SECURITY = ROOT / ".github" / "actions-security-policy.json"
POLICY = ROOT / ".github" / "shadow-branch-policy.json"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains retired release authority: {marker}")


def main() -> int:
    if RETIRED_MONITOR.exists():
        raise AssertionError("The Greasy Fork fallback announcement monitor must remain retired")

    payload = PAYLOAD.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    recovery = RECOVERY.read_text(encoding="utf-8")
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    security = json.loads(SECURITY.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))

    distribution = settings.get("distribution") or {}
    expected_urls = {
        "productUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/",
        "installUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/",
        "updateUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/update/",
        "metadataUrl": "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/metadata/",
    }
    for key, expected in expected_urls.items():
        if distribution.get(key) != expected:
            raise AssertionError(f"TKB distribution {key} changed")

    require(
        release,
        [
            "Verify live TKB distribution and private backup",
            "INSTALL_URL=\"$(jq -r '.distribution.installUrl' .github/release-settings.json)\"",
            "UPDATE_URL=\"$(jq -r '.distribution.updateUrl' .github/release-settings.json)\"",
            "META_URL=\"$(jq -r '.distribution.metadataUrl' .github/release-settings.json)\"",
            "TKB_VERSION",
            "cmp --silent \"$FULL\" \"$RUNNER_TEMP/tkb-install.user.js\"",
            "cmp --silent \"$FULL\" \"$RUNNER_TEMP/tkb-update.user.js\"",
            "Post verified release to Discord",
            "--mode primary",
            "'.distribution.productUrl'",
        ],
        "Production release workflow",
    )
    if release.index("Verify live TKB distribution and private backup") > release.index(
        "Post verified release to Discord"
    ):
        raise AssertionError("Discord must run only after live TKB version verification")

    require(
        recovery,
        [
            "Retry verified Discord release announcement",
            "Discord recovery refused because live TKB endpoints do not all serve Toolkit",
            "tkb-recovery-meta.js",
            "--mode primary",
            "'.distribution.productUrl'",
        ],
        "Release recovery workflow",
    )

    require(
        payload,
        [
            'choices=("primary",)',
            "build_primary(args, brief)",
            "available now through TKB Scripts",
            '"value": "TKB Scripts\\n**LIVE** ✅"',
        ],
        "Discord payload builder",
    )
    forbid(
        payload,
        [
            "build_fallback",
            "FALLBACK RELEASE SIGNAL",
            "PUBLIC VERSION DETECTED",
            "Greasy Fork published a new public version",
            'choices=("primary", "fallback")',
        ],
        "Discord payload builder",
    )

    retired_workflow = ".github/workflows/greasyfork-release-monitor.yml"
    if retired_workflow in (inventory.get("contentsWriteAuthority") or []):
        raise AssertionError("Retired monitor remains in contents-write authority")
    state_writers = {
        entry.get("workflow") for entry in (inventory.get("releaseStateBranchWriters") or [])
    }
    if state_writers != {".github/workflows/release-recovery.yml"}:
        raise AssertionError("Release-state writer inventory is not recovery-only")
    if retired_workflow in (security.get("allowedWritePermissions") or {}):
        raise AssertionError("Retired monitor retains Actions write permission")

    release_state = (policy.get("branches") or {}).get("release-state") or {}
    if release_state.get("operationalWriters") != [
        ".github/workflows/release-recovery.yml"
    ]:
        raise AssertionError("Release-state policy is not recovery-only")

    print(
        "Release authority contract passed: TKB live endpoints gate Discord and "
        "Greasy Fork cannot announce a public version."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
