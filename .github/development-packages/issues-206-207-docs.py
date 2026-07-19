#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
SITE_DATA = ROOT / "docs" / "site-data.json"
VERSION = "4.20.3"

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [Unreleased]\n\n## [4.20.3] - 2026-07-19\n\n### Fixed\n- Restored live responding-unit reconciliation across MissionChief table and lightbox variants, including tbody-ID layouts, stable vehicle de-duplication, current crew capacity and explicit trained-personnel metadata.\n- Prevented unreadable responding units from being silently treated as zero capacity; affected Matrix rows now remain bounded and unresolved instead of producing false red or green states.\n- Restored the authoritative **Fight on Train** baseline: 4 Police Cars, 1 Dog Support Unit and 8 Railway Police Officers.\n- Parsed `Required Personnel Available` and `Required Personnel` rows outside the main vehicle table and preserved mission variation keys including additive overlays.\n- Prevented empty live missing text from overwriting a loading, failed or non-empty **Requirements for this Mission** authority.\n\n### Validation\n- Added deterministic fixtures for responding table variants, active-lightbox discovery, duplicate and state-transition handling, trained Railway Police crew, Fight on Train authority, additive overlays and unresolved authority rendering.\n\n"""
if "## [4.20.3] - 2026-07-19" not in changelog:
    changelog = changelog.replace("## [Unreleased]\n\n", entry, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8").replace("Guide for Toolkit v4.20.2", "Guide for Toolkit v4.20.3", 1)
HELP_INDEX.write_text(help_index, encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-19"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.20.3 restores authoritative Fight on Train requirements and reconciles active responding units across MissionChief mission-window table variants without double counting."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
updated = False
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Mission Requirements":
            feature["summary"] = "Shows authoritative required, on-site, responding, selected and still-needed capacity, including trained personnel and patient-derived demand."
            feature["details"] = [
                "Mission-specific Requirements for this Mission baseline with safe live-source precedence",
                "Responding and on-site units discovered across normal and AJAX/lightbox table variants",
                "Stable vehicle de-duplication across Selected, Responding and On-site transitions",
                "One ambulance per current patient plus affirmative Critical Care, HEMS and transport conditions",
                "Explicit trained-personnel, equipment, trailer and capacity-factor reconciliation",
                "Unknown classifications fail closed as unresolved rather than false complete or false shortage",
            ]
            updated = True
if not updated:
    raise AssertionError("Mission Requirements documentation feature not found")
SITE_DATA.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

print("Updated v4.20.3 Matrix documentation")
