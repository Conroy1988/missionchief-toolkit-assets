#!/usr/bin/env python3
"""Generate a human-readable release dashboard from status/release-dashboard.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "status" / "release-dashboard.json"
OUTPUT = ROOT / "status" / "README.md"

ICONS = {
    "passed": "🟢",
    "published": "🟢",
    "verified": "🟢",
    "posted": "🟢",
    "configured": "🟢",
    "secret-configured": "🟢",
    "dry-run-ready": "🟡",
    "dry-run-built": "🟡",
    "legacy-monitor": "🟡",
    "not-configured": "⚪",
}


def icon(value: str) -> str:
    return ICONS.get(value, "🔵")


def text(value: object) -> str:
    return str(value).replace("-", " ").strip().title()


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    status = data.get("status", {})
    latest = data.get("latestRelease") or {}
    dry_run = data.get("releaseDryRun") or {}
    assets = data.get("assets", {})
    source = data.get("source", {})
    candidate = data.get("distributionCandidate", {})

    version = data.get("currentVersion", "Unknown")
    latest_version = latest.get("version") or dry_run.get("version") or version
    latest_state = "Verified public release" if latest else "Validated dry run"

    rows = [
        ("Canonical source", source.get("state", "unknown")),
        ("Validation", status.get("validation", "unknown")),
        ("GitHub Release", status.get("githubRelease", "unknown")),
        ("Greasy Fork", status.get("greasyForkSync", "unknown")),
        ("Private backup", status.get("backup", "unknown")),
        ("Discord development", status.get("discordDevelopment", "unknown")),
        ("Discord releases", status.get("discordRelease", "unknown")),
        ("Asset audit", status.get("assetAudit", "unknown")),
    ]

    lines = [
        "# MissionChief Toolkit Control Panel",
        "",
        "> Automatically generated from [`release-dashboard.json`](release-dashboard.json). Do not edit this page manually.",
        "",
        f"## Current version: `{version}`",
        "",
        "| System | Health | State |",
        "|---|:---:|---|",
    ]

    for label, value in rows:
        value_str = str(value)
        lines.append(f"| {label} | {icon(value_str)} | {text(value_str)} |")

    lines.extend([
        "",
        "## Release state",
        "",
        f"- **Latest recorded version:** `{latest_version}`",
        f"- **State:** {latest_state}",
        f"- **Canonical path:** `{source.get('canonicalPath', 'src/MissionChief_Map_Command_Toolkit.user.js')}`",
        f"- **Validated SHA-256:** `{source.get('validatedSha256', latest.get('sha256', dry_run.get('sha256', 'Not yet recorded'))}`",
        f"- **Distribution candidate:** `{candidate.get('path', 'dist/MissionChief_Map_Command_Toolkit.user.js')}`",
        "",
        "## Repository health",
        "",
        f"- **Discovered media files:** {assets.get('discoveredFiles', 'Unknown')}",
        f"- **Referenced hosted paths:** {assets.get('referencedPaths', 'Unknown')}",
        f"- **Missing referenced paths:** {assets.get('missingReferencedPaths', 'Unknown')}",
        f"- **Last dashboard update:** `{data.get('lastUpdated', 'Unknown')}`",
        "",
        "## Release channels",
        "",
        f"- Development activity → `{data.get('channels', {}).get('development', 'Mission-Chief-Dev')}`",
        f"- Verified releases → `{data.get('channels', {}).get('releases', 'Mission-Chief')}`",
        "",
        "## Release path",
        "",
        "```text",
        "Canonical source",
        "      ↓",
        "Validation and bundle build",
        "      ↓",
        "GitHub Release",
        "      ↓",
        "Greasy Fork webhook and verification",
        "      ↓",
        "Private migration backup",
        "      ↓",
        "Discord release confirmation",
        "```",
        "",
        "---",
        "",
        "The JSON file remains the machine-readable source of truth. This page is regenerated automatically whenever release state changes.",
    ])

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
