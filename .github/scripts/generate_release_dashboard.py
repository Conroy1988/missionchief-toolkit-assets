#!/usr/bin/env python3
"""Sanitize and render the verified release dashboard."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "status" / "release-dashboard.json"
OUTPUT = ROOT / "status" / "README.md"
CANONICAL = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VERSION_RE = re.compile(r"^//\s*@version\s+([^\s]+)", re.MULTILINE)

ICONS = {
    "passed": "🟢",
    "published": "🟢",
    "verified": "🟢",
    "posted": "🟢",
    "configured": "🟢",
    "secret-configured": "🟢",
    "validated": "🟢",
    "validated-canonical-source": "🟢",
    "private-repository-verified": "🟢",
    "pending-release": "🟡",
    "not-configured": "⚪",
    "not-published": "⚪",
    "not-created": "⚪",
    "not-posted": "⚪",
}


def icon(value: str) -> str:
    return ICONS.get(value, "🔵")


def text(value: object) -> str:
    return str(value).replace("-", " ").strip().title()


def sanitize_verified_ledger(data: dict) -> dict:
    sanitized = deepcopy(data)
    sanitized.pop("distributionCandidate", None)
    sanitized.pop("releaseDryRun", None)
    sanitized.setdefault("pipelineVersion", 3)
    sanitized["validationEvidencePolicy"] = {
        "storage": "workflow-artifact",
        "authority": "exact successful Validate Canonical Userscript run for the source commit",
        "publicMainChanged": False,
        "releaseDashboardChanged": False,
    }

    if CANONICAL.is_file():
        raw = CANONICAL.read_bytes()
        match = VERSION_RE.search(raw.decode("utf-8"))
        source_version = match.group(1).strip() if match else ""
        if source_version and str(sanitized.get("currentVersion") or "") == source_version:
            sanitized["source"] = {
                "canonicalPath": "src/MissionChief_Map_Command_Toolkit.user.js",
                "validatedSha256": hashlib.sha256(raw).hexdigest(),
                "state": "validated-canonical-source",
            }
    return sanitized


def main() -> None:
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    data = sanitize_verified_ledger(original)
    if data != original:
        SOURCE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    status = data.get("status", {})
    latest = data.get("latestRelease") or {}
    assets = data.get("assets", {})
    source = data.get("source", {})

    version = data.get("currentVersion", "Unknown")
    latest_version = latest.get("version") or version
    latest_state = "Verified public release" if latest else "No verified public release recorded"
    validated_hash = source.get("validatedSha256") or latest.get("sha256") or "Not yet recorded"

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
        f"- **Validated SHA-256:** `{validated_hash}`",
        "- **Candidate validation evidence:** immutable GitHub Actions artifact tied to the exact source commit",
        "",
        "## Repository health",
        "",
        f"- **Discovered media files:** {assets.get('discoveredFiles', 'Unknown')}",
        f"- **Referenced hosted paths:** {assets.get('referencedPaths', 'Unknown')}",
        f"- **Missing referenced paths:** {assets.get('missingReferencedPaths', 'Unknown')}",
        f"- **Last release-state update:** `{data.get('lastUpdated', 'Unknown')}`",
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
        "Read-only validation artifact",
        "      ↓",
        "Release readiness and bundle rebuild",
        "      ↓",
        "Stable distribution publication",
        "      ↓",
        "GitHub Release and Greasy Fork verification",
        "      ↓",
        "Private migration backup",
        "      ↓",
        "Discord release confirmation",
        "```",
        "",
        "---",
        "",
        "The JSON file remains the machine-readable verified-release ledger. Transient validation candidates are retained as immutable workflow artifacts and are never written into this dashboard.",
    ])

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
