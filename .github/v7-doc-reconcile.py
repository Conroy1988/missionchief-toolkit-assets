#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs" / "site-data.json"
data = json.loads(PATH.read_text(encoding="utf-8"))

for category in data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Mission Age map timers":
            feature["summary"] = "Displays compact age timer badges above personal missions on the map."
        elif feature.get("name") == "Transport Watcher":
            feature["details"] = [
                "Patient and prisoner markers",
                "Live counts",
                "Map marker overlay",
            ]
        elif feature.get("name") == "Patient Transport Sweep":
            feature["summary"] = "Manually releases verified eligible alliance ambulances through MissionChief's native vehicle window while excluding the signed-in player's own vehicles."
            feature["details"] = [
                "MissionChief native Discharge patient control",
                "One verified vehicle at a time",
                "Ambiguous ownership is skipped",
                "Bounded retries and confirmation evidence",
            ]
            feature["tags"] = ["transport", "alliance", "native"]

new_documentation = [
    {
        "title": "v7 native Toolkit boundary",
        "sections": [
            {
                "heading": "The One We Knew Before",
                "body": "Version 7 removes the copied requirements, call-window, call-list and enhanced transport-request engines completely. Their settings, stored state, observers, scheduling and DOM rewriting no longer initialise.",
            },
            {
                "heading": "What remains",
                "body": "Mission Age map timers, Mission Value, native Patient Transport Sweep, Transport Watcher, Resource Gap, vehicle identity, map utilities, financial intelligence, themes and responsive layouts remain supported.",
            },
            {
                "heading": "Settings migration",
                "body": "Existing retained settings load normally. Obsolete mission-window settings are discarded during state normalisation without requiring a full reset.",
            },
        ],
    },
    {
        "title": "Installation",
        "sections": [
            {
                "heading": "Install through Greasy Fork",
                "body": "Install Tampermonkey or a compatible userscript manager, open the Toolkit installation link, review permissions and confirm installation. Greasy Fork remains the supported automatic-update channel.",
            },
            {
                "heading": "First launch",
                "body": "Open MissionChief and use the map command button. Core controls load first; larger panels and monitors are constructed only when required.",
            },
        ],
    },
    {
        "title": "Operating model",
        "sections": [
            {
                "heading": "Persistent controls",
                "body": "Feature state, theme, operating mode and toolbar state are retained. Export settings before substantial browser or device changes.",
            },
            {
                "heading": "Map-first behaviour",
                "body": "The Toolkit adds summaries, overlays and shortcuts around MissionChief rather than replacing its native mission windows or mission list.",
            },
        ],
    },
    {
        "title": "Mission and transport systems",
        "sections": [
            {
                "heading": "Mission Age map timers",
                "body": "Compact timer badges appear above personal missions and can be toggled with shortcut 6.",
            },
            {
                "heading": "Mission Value",
                "body": "Mission Value displays a verified value, hides unavailable values and stays clear of native controls.",
            },
            {
                "heading": "Transport Watcher",
                "body": "Transport Watcher identifies patient or prisoner transport-required missions without replacing MissionChief controls.",
            },
            {
                "heading": "Patient Transport Sweep",
                "body": "The manual bounded alliance workflow excludes the signed-in player's vehicles and uses MissionChief's native vehicle-window discharge control for one verified eligible ambulance at a time.",
            },
        ],
    },
    {
        "title": "Fleet, map and finance",
        "sections": [
            {
                "heading": "Resource Gap",
                "body": "Compares mission demand with personal vehicle context inside a configurable radius.",
            },
            {
                "heading": "Coverage rings",
                "body": "Coverage rings provide geographic range context without installing a document-wide heat overlay.",
            },
            {
                "heading": "Smart Bookmark Labels",
                "body": "Automatically shortens labels while retaining the full name through tooltips or touch previews.",
            },
            {
                "heading": "Financial intelligence",
                "body": "Reconciles income, spending and variance and can send configured summaries to a saved Discord webhook.",
            },
        ],
    },
    {
        "title": "Settings and recovery",
        "sections": [
            {
                "heading": "Import and export",
                "body": "Move configuration between Desktop, Tablet and iOS. Exports may contain a saved Discord webhook and must remain private.",
            },
            {
                "heading": "Reset strategy",
                "body": "Export first, reset only the affected feature where possible and test with the default Map Command interface before a full reset.",
            },
        ],
    },
]
data["documentation"] = new_documentation

data["troubleshooting"] = [
    {
        "problem": "MissionChief feels slow immediately after page load",
        "steps": [
            "Confirm the installed version is current",
            "Allow idle bootstrap to complete",
            "Enable Economy Mode on lower-power devices",
            "Compare with the Toolkit disabled and capture startup metrics",
        ],
    },
    {
        "problem": "A button or panel is missing",
        "steps": [
            "Reload MissionChief once",
            "Confirm the correct operating mode",
            "Check whether the toolbar is collapsed",
            "Report browser, userscript manager and Toolkit versions",
        ],
    },
    {
        "problem": "A native mission or vehicle control is unavailable",
        "steps": [
            "Allow the MissionChief window to finish loading",
            "Confirm the control is visible without the Toolkit",
            "Reload the active mission or vehicle window once",
            "Report the exact route and missing native control",
        ],
    },
    {
        "problem": "Settings did not carry to another device",
        "steps": [
            "Export from the original device",
            "Import the complete timestamped file",
            "Confirm the target operating mode",
            "Reload MissionChief once",
        ],
    },
]

data["mediaRoadmap"] = [
    "Before-and-after map comparison",
    "All seven interface systems",
    "Mission Age map timer badges",
    "Mission Value inside a native mission window",
    "Patient Transport Sweep native discharge workflow",
    "Transport Watcher",
    "Resource Gap",
    "Vehicle Code Status",
    "Custom Vehicle Badges",
    "Coverage rings",
    "Smart Bookmark Labels",
    "Financial intelligence",
    "Payout presentations",
    "Tablet and iOS Mobile Mode",
]

PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

for temporary in [
    ROOT / ".github" / "v7-doc-reconcile.py",
    ROOT / ".github" / "workflows" / "apply-v7-doc-reconcile.yml",
]:
    temporary.unlink(missing_ok=True)

print("v7 documentation catalogue reconciled")
