#!/usr/bin/env python3
"""One-use deterministic repository reconciliation for Issue #510."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


def reconcile_changelog() -> None:
    text = read("CHANGELOG.md")
    if "## [6.0.0]" in text:
        return
    block = """## [6.0.0] - 2026-07-25

### Critical performance overhaul

- Removed Automatic day/night, Coverage Heat Map, Mission Inspector, Mission Age Workflow and Age Watch from runtime state, settings, timers, observers, map ownership, styles and teardown.
- Preserved the separate Mission Age map timer badges and shortcut `6`.
- Rebuilt Operational Window settings with typed toggles, numbers, colours, selects, multiselects, structured editors and current LSSM V.4 dependency rules.
- Prevented Toolkit-owned Operational Window mutations and unrelated structural text changes from repeatedly scheduling full reconciliation.
- Replaced repeated document-wide Operational Window cleanup scans with per-document owned-node and decorated-node registries.
- Removed duplicate Operational Window scheduling and stopped settings changes from rebuilding the complete Toolkit panel.
- Reduced the canonical source by more than 330 KB and 6,600 lines while lowering recurring tasks, managed timer call sites, listeners and selector call sites.
- Added permanent v6 retirement, Mission Age retention, typed-settings and static runtime-budget contracts.
- Browser profiler evidence remains mandatory before the guarded production release.

"""
    marker = "## [5.0.7] - 2026-07-24\n"
    if marker not in text:
        raise SystemExit("Could not locate v5.0.7 changelog heading")
    write("CHANGELOG.md", text.replace(marker, block + marker, 1))


def reconcile_readme() -> None:
    text = read("README.md")
    text = replace(text, "**Current verified release: `v5.0.7`**", "**Current verified release: `v5.0.7` · Development candidate: `v6.0.0`**")
    text = replace(text, "Extended Mission List", "Extended Call List")
    text = replace(text, "Use heat maps, rings, bookmarks, focus modes and visibility controls", "Use coverage rings, bookmarks, focus modes and visibility controls")
    text = re.sub(r"(?m)^\| \*\*Mission Age Watch\*\* \|.*$", "| **Mission Age map timers** | Displays compact age timer badges above map missions; shortcut `6` toggles the badges |", text)
    text = re.sub(r"(?m)^\| \*\*Critical View\*\* \|.*\n?", "", text)
    text = re.sub(r"(?m)^\| \*\*Mission Inspector\*\* \|.*\n?", "", text)
    text = re.sub(r"(?m)^\| \*\*Coverage Heat Map\*\* \|.*\n?", "", text)
    if "| **v6.0.0 candidate** |" not in text:
        marker = "| **v5.0.0** |"
        row = "| **v6.0.0 candidate** | Critical performance overhaul, clean feature retirement and typed Operational Window settings rebuild |\n"
        text = text.replace(marker, row + marker, 1)
    text = replace(text, "Mission Age Watch, Critical View, fleet identity", "Mission Age map timer badges, fleet identity")
    write("README.md", text)


def reconcile_help() -> None:
    text = read("help/index.html")
    text = replace(text, "Toolkit v5.0.7", "Toolkit v6.0.0 candidate")
    text = replace(text, "Guide for Toolkit v5.0.7", "Toolkit v6.0.0 candidate guide")
    text = replace(text, "complete v5 guide", "v6 performance candidate guide")
    text = replace(text, "Extended Mission List", "Extended Call List")
    text = replace(text, "Mission Age Watch, Critical View, fleet identity", "Mission Age map timer badges, fleet identity")
    old_mission = '<section class="section" id="mission-command" data-title="Mission Command" data-keywords="mission age critical inspector value spawn stuck feed watcher sweep"><div class="head"><span class="num">07</span><div><h2>Mission command</h2><p class="summary">Triage, inspect and navigate incidents without losing map context.</p></div></div><div class="grid"><article class="card"><h3>Mission Age Watch</h3><p>Filter and sort personal and alliance missions by age, ownership, category, state and distance. Shortcut: <kbd>6</kbd>.</p></article><article class="card"><h3>Critical View and Mission Inspector</h3><p>Concentrate urgent work and load deeper context only when requested.</p></article><article class="card"><h3>Mission Value</h3><p>Shows a verified mission value and hides unavailable values rather than guessing.</p></article><article class="card"><h3>Monitoring</h3><p>Mission Spawn, Stuck Detector, Major Incident Feed, Transport Watcher and Patient Transport Sweep use bounded lifecycle ownership.</p></article></div></section>'
    new_mission = '<section class="section" id="mission-command" data-title="Mission Command" data-keywords="mission age timers value spawn stuck feed watcher sweep"><div class="head"><span class="num">07</span><div><h2>Mission command</h2><p class="summary">Triage and navigate incidents without losing map context.</p></div></div><div class="grid"><article class="card"><h3>Mission Age map timers</h3><p>Displays compact timer badges above map missions. Shortcut: <kbd>6</kbd>.</p></article><article class="card"><h3>Mission Value</h3><p>Shows a verified mission value and hides unavailable values rather than guessing.</p></article><article class="card"><h3>Monitoring</h3><p>Mission Spawn, Stuck Detector, Major Incident Feed, Transport Watcher and Patient Transport Sweep use bounded lifecycle ownership.</p></article><article class="card"><h3>v6 performance architecture</h3><p>Disabled modules create no recurring work, Operational Window mutations are coalesced and owned-node cleanup is deterministic.</p></article></div></section>'
    if old_mission in text:
        text = text.replace(old_mission, new_mission, 1)
    text = replace(text, "Coverage Heat Map, coverage rings, Smart Bookmark Labels", "Coverage rings, Smart Bookmark Labels")
    text = replace(text, "Existing settings are retained across the v5 upgrade line. A manual reset is not required.", "Existing supported settings are retained. Obsolete v6 feature keys are removed safely without requiring a manual reset.")
    write("help/index.html", text)


def reconcile_greasyfork() -> None:
    text = read("docs/greasyfork-description.md")
    text = replace(text, "Extended Mission List", "Extended Call List")
    text = replace(text, "- Mission Age Watch, Mission Value, Critical View and Mission Inspector", "- Mission Age map timer badges and Mission Value")
    text = replace(text, "- Smart bookmarks, Map Jump, coverage rings and Coverage Heat Map", "- Smart bookmarks, Map Jump and coverage rings")
    text = replace(text, "- Performance-aware startup, bounded monitoring and deterministic cleanup", "- v6 performance architecture with bounded monitoring, owned-node cleanup and deterministic teardown")
    write("docs/greasyfork-description.md", text)


def reconcile_site_data() -> None:
    path = ROOT / "docs/site-data.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    retired = {"Mission Age Watch", "Critical View", "Mission Inspector", "Coverage Heat Map"}
    for category in data.get("featureCategories", []):
        features = []
        for feature in category.get("features", []):
            name = feature.get("name")
            if name in retired:
                continue
            if name == "Extended Mission List":
                feature["name"] = "Extended Call List"
            if name == "Resource Gap":
                feature["details"] = [str(item).replace("Mission Inspector breakdown", "Live requirement breakdown") for item in feature.get("details", [])]
            if name == "Coverage rings and map overlays":
                feature["details"] = [item for item in feature.get("details", []) if "Day and night" not in str(item)]
            features.append(feature)
        category["features"] = features
        if category.get("name") == "Mission command" and not any(f.get("name") == "Mission Age map timers" for f in features):
            features.insert(0, {
                "name": "Mission Age map timers",
                "summary": "Displays compact age timer badges above missions on the map without running the retired Age Watch workflow.",
                "details": ["Map timer badges", "Shortcut 6", "Deterministic marker cleanup", "Desktop, Tablet/iPad and iOS support"],
                "visual": "mission-age-map-timers",
                "tags": ["missions", "map", "timers"]
            })
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def reconcile_documentation_contract() -> None:
    path = ROOT / ".github/documentation-contract.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["requiredSourceTokens"] = [x for x in data["requiredSourceTokens"] if x not in {"Mission Age Watch", "Critical View"}]
    if "Mission Age" not in data["requiredSourceTokens"]:
        data["requiredSourceTokens"].insert(0, "Mission Age")
    names = []
    for name in data["requiredFeatureNames"]:
        if name in {"Mission Age Watch", "Coverage Heat Map"}:
            continue
        names.append("Extended Call List" if name == "Extended Mission List" else name)
    if "Mission Age map timers" not in names:
        names.insert(0, "Mission Age map timers")
    data["requiredFeatureNames"] = names
    public = data["publicDocumentation"]
    for key in ["readmeRequiredTokens", "helpRequiredTokens", "greasyForkRequiredTokens"]:
        public[key] = ["Extended Call List" if x == "Extended Mission List" else x for x in public[key]]
    retired = ["Mission Age Watch", "Critical View", "Mission Inspector", "Coverage Heat Map", "Automatic day / night"]
    for key in ["readmeForbiddenTokens", "helpForbiddenTokens", "greasyForkForbiddenTokens"]:
        public[key] = list(dict.fromkeys([*public.get(key, []), *retired]))
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def reconcile_settings_fixture() -> None:
    path = ROOT / ".github/fixtures/settings-ui-contract.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, values in list(data.items()):
        if isinstance(values, list):
            data[key] = [
                item for item in values
                if str(item) not in {"fit-critical", "open-critical-drawer", "critical-go", "autoNight", "criticalView", "heatmap", "missionInspector"}
                and not str(item).startswith("auto-")
                and not str(item).startswith("heatmap-")
            ]
        elif isinstance(values, dict):
            for retired in ["autoNight", "criticalView", "heatmap", "missionInspector"]:
                values.pop(retired, None)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def reconcile_boot_fixture() -> None:
    path = ROOT / ".github/fixtures/boot-lifecycle-contract.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    retired = {"auto-night", "critical-countdowns", "pointerover", "pointermove", "pointerout", "[data-mcms-critical-view]", "criticalMissionStableCache", "clearCoverageHeatmap"}
    for key, values in list(data.items()):
        if isinstance(values, list):
            data[key] = [item for item in values if str(item) not in retired]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def reconcile_hero() -> None:
    path = ROOT / "docs/media/readme-hero.svg"
    text = path.read_text(encoding="utf-8")
    text = replace(text, "MissionChief Map Command Toolkit v5.0.7 Operational Window Suite", "MissionChief Map Command Toolkit v6.0.0 performance candidate")
    text = replace(text, "VERIFIED v5.0.7", "V6 PERFORMANCE CANDIDATE")
    text = replace(text, "Age · Critical · Inspector", "Age timers · Requirements · Triage")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    reconcile_changelog()
    reconcile_readme()
    reconcile_help()
    reconcile_greasyfork()
    reconcile_site_data()
    reconcile_documentation_contract()
    reconcile_settings_fixture()
    reconcile_boot_fixture()
    reconcile_hero()
    print("v6 repository reconciliation complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
