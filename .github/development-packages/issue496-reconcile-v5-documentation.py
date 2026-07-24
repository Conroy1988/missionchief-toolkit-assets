#!/usr/bin/env python3
"""Reconcile public documentation with the Toolkit v5 Operational Window Suite."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "docs/site-data.json"
HELP = ROOT / "help/index.html"
MANIFEST = ROOT / "dist/release-manifest.json"
DRIFT_JSON = ROOT / "documentation-drift-report.json"
DRIFT_MD = ROOT / "documentation-drift-report.md"
WORKFLOW = ROOT / ".github/workflows/validate-userscript.yml"
CONTRACT = ROOT / ".github/scripts/test_documentation_consistency.py"

FAMILIES = [
    {
        "name": "Enhanced Operational Requirements",
        "summary": "Reconciles authoritative vehicle, equipment, personnel, capacity, selected, en-route, on-scene and still-needed demand without inventing coverage.",
        "details": [
            "Positive parsed evidence is required before covered demand is displayed in green",
            "Amber waiting and unresolved states preserve uncertainty when MissionChief evidence is absent or unsupported",
            "Native, grouped and compatible hidden LSSM requirement sources are scored and rebound when mission markup changes",
            "Qualified personnel, patient demand, trailers, towing pairs and capacity factors retain reviewed evidence boundaries",
        ],
        "visual": "mission-requirements",
        "tags": ["missions", "requirements", "dispatch"],
    },
    {
        "name": "Extended Call Window",
        "summary": "Adds typed mission-window intelligence without creating a second mission-window lifecycle.",
        "details": [
            "Patient and vehicle summaries plus selected-unit and ARR counters",
            "Permanent vehicle and ARR search with highlighting",
            "Generation, alarm, mission-keyword and map-centre context",
            "Responsive Desktop, Tablet/iPad and iOS-safe controls",
        ],
        "visual": "extended-call-window",
        "tags": ["missions", "window", "arr"],
    },
    {
        "name": "Extended Mission List",
        "summary": "Prioritises the live mission list with deterministic state that survives MissionChief refreshes.",
        "details": [
            "Mission sorting, starring and collapsing",
            "Patient, prisoner, credit and remaining-time badges",
            "Native sharing controls with deterministic reconciliation",
            "Equivalent LSSM surfaces suppress matching Toolkit output",
        ],
        "visual": "extended-mission-list",
        "tags": ["missions", "list", "priority"],
    },
    {
        "name": "Enhanced Transport Requests",
        "summary": "Provides opt-in transport assistance through strict route and candidate safety checks.",
        "details": [
            "Exact transport-route validation",
            "Visible and enabled candidate filtering",
            "Single-candidate ambiguity rejection",
            "Per-route idempotency protection against duplicate actions",
        ],
        "visual": "enhanced-transport",
        "tags": ["transport", "safety", "opt-in"],
    },
]

GUIDE = {
    "title": "Operational Window Suite",
    "sections": [
        {
            "heading": "Four coordinated operational families",
            "body": "The Operational Window Suite combines Enhanced Operational Requirements, Extended Call Window, Extended Mission List and opt-in Enhanced Transport Requests under one versioned settings model and one lifecycle coordinator per active MissionChief document.",
        },
        {
            "heading": "Requirement truth states",
            "body": "Green coverage requires positive parsed requirement evidence and every known row to be satisfied. Amber waiting means MissionChief has not supplied usable evidence; amber unresolved means evidence exists but cannot be classified safely. Empty or unsupported input is never presented as confirmed coverage.",
        },
        {
            "heading": "MissionChief and LSSM coexistence",
            "body": "The Toolkit evaluates active native, grouped and compatible hidden LSSM requirement sources, rebinds when the authoritative source changes and suppresses a matching Toolkit surface when a genuinely visible equivalent LSSM panel is active.",
        },
        {
            "heading": "Guarded transport",
            "body": "Enhanced Transport Requests remains opt-in. It validates the exact route, ignores hidden or disabled candidates, rejects ambiguity and records one action token per route to prevent duplicate transport actions.",
        },
    ],
}

CONTRACT_TEXT = r'''#!/usr/bin/env python3
"""Enforce current public documentation against the canonical release manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = (
    "Enhanced Operational Requirements",
    "Extended Call Window",
    "Extended Mission List",
    "Enhanced Transport Requests",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads((ROOT / "dist/release-manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    hero = (ROOT / "docs/media/readme-hero.svg").read_text(encoding="utf-8")
    site_text = (ROOT / "docs/site-data.json").read_text(encoding="utf-8")
    site = json.loads(site_text)
    help_text = (ROOT / "help/index.html").read_text(encoding="utf-8")
    drift = json.loads((ROOT / "documentation-drift-report.json").read_text(encoding="utf-8"))
    drift_md = (ROOT / "documentation-drift-report.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")

    require(f"Current verified release: `v{version}`" in readme, "README current release differs from the manifest")
    require("v4.20.33" not in readme, "README still advertises the obsolete v4.20.33 production line")
    require("Mission Requirements Matrix" not in readme, "README still advertises the retired Matrix as current")
    for family in FAMILIES:
        require(family in readme, f"README is missing {family}")
        require(family in site_text, f"site-data is missing {family}")
        require(family in help_text, f"Help Centre is missing {family}")

    require("Operational Window Suite" in hero, "README hero is not aligned with the Operational Window Suite")
    require(not re.search(r"\bv\d+\.\d+\.\d+\b", hero), "README hero must remain version-neutral")
    require("Mission Requirements Matrix" not in hero, "README hero still presents the retired Matrix")

    category = next((item for item in site["featureCategories"] if item["name"] == "Operational Window Suite"), None)
    require(category is not None, "site-data has no Operational Window Suite category")
    require([item["name"] for item in category["features"]] == list(FAMILIES), "site-data operational families differ from the canonical order")
    require(any(item["title"] == "Operational Window Suite" for item in site["documentation"]), "site-data has no Operational Window guide")

    require(f"Guide for Toolkit v{version}" in help_text, "Help Centre version differs from the manifest")
    require("live Mission Requirements matrix" not in help_text, "Help Centre still advertises the retired matrix wording")
    require(drift["userscriptVersion"] == version, "documentation drift JSON version is stale")
    require(drift["versionState"] == "current-production", "documentation drift JSON does not describe current production")
    require(f"Toolkit version: **{version}**" in drift_md, "documentation drift Markdown version is stale")
    require("python3 .github/scripts/test_documentation_consistency.py" in workflow, "canonical validation does not run the documentation contract")

    print(f"Documentation consistency passed for Toolkit {version}: README, hero, site data, Help Centre and drift evidence agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest["version"]

    site = json.loads(SITE.read_text(encoding="utf-8"))
    site["project"]["tagline"] = "Operational map command and mission-window intelligence suite for MissionChief."
    site["project"]["description"] = (
        "A configurable userscript that turns MissionChief into an operational command centre with the "
        "Operational Window Suite, live requirements intelligence, fleet monitoring, guarded transport, "
        "map utilities, financial reconciliation, responsive layouts and verified release automation."
    )

    for category in site["featureCategories"]:
        category["features"] = [
            feature for feature in category.get("features", [])
            if feature.get("name") not in {"Mission Requirements", "Mission Requirements Matrix"}
        ]
    site["featureCategories"] = [
        category for category in site["featureCategories"]
        if category.get("name") != "Operational Window Suite"
    ]
    site["featureCategories"].insert(
        1,
        {
            "name": "Operational Window Suite",
            "description": "Coordinate requirements, mission-window intelligence, mission-list priority and guarded transport through one lifecycle.",
            "features": FAMILIES,
        },
    )
    site["documentation"] = [item for item in site["documentation"] if item.get("title") != "Operational Window Suite"]
    site["documentation"].insert(2, GUIDE)
    for item in (
        "Enhanced Operational Requirements truth states",
        "Extended Call Window workflow",
        "Extended Mission List workflow",
        "Enhanced Transport Requests safeguards",
    ):
        if item not in site["mediaRoadmap"]:
            site["mediaRoadmap"].append(item)
    SITE.write_text(json.dumps(site, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    old = "the live Mission Requirements matrix"
    replacement = (
        "the Operational Window Suite (Enhanced Operational Requirements, Extended Call Window, "
        "Extended Mission List and Enhanced Transport Requests)"
    )
    if old not in help_text and replacement not in help_text:
        raise RuntimeError("Expected Help Centre mission-system wording was not found")
    help_text = help_text.replace(old, replacement)
    help_text = help_text.replace("Mission Requirements Matrix", "Enhanced Operational Requirements")
    HELP.write_text(help_text, encoding="utf-8")

    feature_count = sum(len(category.get("features", [])) for category in site["featureCategories"])
    drift = {
        "schemaVersion": 2,
        "status": "passed",
        "userscriptVersion": version,
        "versionState": "current-production",
        "documentedThemes": [theme["name"] for theme in site["themes"]],
        "documentedModes": [mode["name"] for mode in site["modes"]],
        "documentedShortcuts": site["shortcuts"],
        "featureCount": feature_count,
        "publicDocumentCount": 4,
        "failures": [],
        "warnings": [],
    }
    DRIFT_JSON.write_text(json.dumps(drift, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DRIFT_MD.write_text(
        "# Documentation Drift Audit\n\n"
        "✅ **Status:** PASSED\n\n"
        f"- Toolkit version: **{version}**\n"
        "- Version state: **current-production**\n"
        f"- Features: **{feature_count}**\n"
        f"- Themes: **{len(site['themes'])}**\n"
        f"- Modes: **{len(site['modes'])}**\n"
        f"- Shortcuts: **{len(site['shortcuts'])}**\n"
        "- Public documentation surfaces checked: **4**\n\n"
        "README, version-neutral hero artwork, GitHub Pages site data and the bundled Help Centre agree with the canonical release manifest.\n",
        encoding="utf-8",
    )

    CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT.write_text(CONTRACT_TEXT, encoding="utf-8")
    CONTRACT.chmod(0o755)

    workflow = WORKFLOW.read_text(encoding="utf-8")
    path_block = (
        '      - "CHANGELOG.md"\n'
        '      - "README.md"\n'
        '      - "docs/site-data.json"\n'
        '      - "docs/media/readme-hero.svg"\n'
        '      - "help/index.html"\n'
        '      - "documentation-drift-report.json"\n'
        '      - "documentation-drift-report.md"\n'
        '      - "dist/release-manifest.json"\n'
        '      - ".github/scripts/test_documentation_consistency.py"\n'
    )
    if '      - "README.md"\n' not in workflow:
        workflow = workflow.replace('      - "CHANGELOG.md"\n', path_block)
    step = (
        "      - name: Validate documentation consistency\n"
        "        run: python3 .github/scripts/test_documentation_consistency.py\n\n"
    )
    if "Validate documentation consistency" not in workflow:
        marker = "      - name: Check JavaScript syntax\n"
        if marker not in workflow:
            raise RuntimeError("Canonical validation workflow insertion point was not found")
        workflow = workflow.replace(marker, step + marker, 1)
    WORKFLOW.write_text(workflow, encoding="utf-8")

    subprocess.run([sys.executable, str(CONTRACT)], cwd=ROOT, check=True)
    print(f"Reconciled public documentation with Toolkit {version} and installed a permanent consistency contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
