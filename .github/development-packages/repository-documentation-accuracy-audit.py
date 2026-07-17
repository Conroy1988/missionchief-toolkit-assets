#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
HELP = ROOT / "help/index.html"
SITE_DATA = ROOT / "docs/site-data.json"
GREASY = ROOT / "docs/greasyfork-description.md"
SITE_GUIDE = ROOT / "docs/SITE.md"
ROADMAP = ROOT / "ROADMAP.md"
CONTRACT = ROOT / ".github/documentation-contract.json"
DRIFT = ROOT / ".github/scripts/check_documentation_drift.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, replacement: str, label: str, flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"{label}: expected one regex match, found {count}")
    return updated


def category(data: dict, name: str) -> dict:
    for item in data.get("featureCategories", []):
        if item.get("name") == name:
            return item
    raise RuntimeError(f"missing feature category: {name}")


def feature(cat: dict, name: str) -> dict:
    for item in cat.get("features", []):
        if item.get("name") == name:
            return item
    raise RuntimeError(f"missing feature: {name}")


def insert_feature_after(cat: dict, after_name: str, item: dict) -> None:
    features = cat.setdefault("features", [])
    if any(existing.get("name") == item["name"] for existing in features):
        return
    for index, existing in enumerate(features):
        if existing.get("name") == after_name:
            features.insert(index + 1, item)
            return
    raise RuntimeError(f"cannot insert {item['name']}: anchor {after_name} is missing")


readme = README.read_text(encoding="utf-8")
readme = replace_once(
    readme,
    "| **Mission Age Watch** | Sorts and surfaces personal missions by age, urgency, assistance state and clearing progress. |",
    "| **Mission Age Watch** | Sorts and surfaces personal and alliance missions by age, ownership, category, urgency, assistance state and clearing progress. |",
    "README Mission Age Watch accuracy",
)
readme = replace_once(
    readme,
    "| **Transport Watcher** | Identifies missions that still require patient transport and shows current demand. |",
    "| **Transport Watcher** | Identifies missions that still require patient or prisoner transport and shows current demand. |\n| **Patient Transport Sweep** | Manually processes eligible alliance-member ambulances one at a time, preferring delayed LSSM release controls while excluding the signed-in player's own vehicles. |\n| **Resource Gap** | Compares mission requirements with available personal vehicle context inside the selected radius. |",
    "README transport and resource systems",
)
readme = replace_once(
    readme,
    "| **Settings import/export** | Moves the complete Toolkit configuration between devices. |",
    "| **Settings import/export** | Moves Toolkit configuration between devices; exports can contain a saved Discord webhook and must be stored privately. |",
    "README settings privacy",
)
readme = replace_once(
    readme,
    "- Patient and transport monitoring",
    "- Patient and prisoner transport monitoring\n- Manual Patient Transport Sweep with own-vehicle exclusion, sequential alliance processing and a bounded non-LSSM fallback",
    "README mission inventory",
)
readme = replace_once(
    readme,
    "- Transport demand counts",
    "- Transport demand counts\n- Resource Gap analysis within a configurable radius",
    "README fleet inventory",
)
README.write_text(readme, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
help_text = replace_once(help_text, "Guide for Toolkit v4.2.1", "Guide for Toolkit v4.14.4", "Help header version")
help_text = replace_once(
    help_text,
    "the command panel, six interface themes, operational map skins, overlays, Mission Age Watch, resource and transport tools, payout presentation, Discord reporting, locations, profiles, Tablet Mode and iOS Mobile Mode.",
    "the command panel, seven interface systems, operational map skins, overlays, Mission Age Watch, Mission Value, resource and transport tools, payout presentation, Discord reporting, locations, profiles, Economy Mode, Tablet Mode and iOS Mobile Mode.",
    "Help hero capability summary",
)
interface_section = '''<section class="section" id="interface-themes" data-title="Interface Themes" data-keywords="map command cyberpunk fallout umbrella factorio 007 james bond hyrule zelda themes skin"><div class="head"><span class="num">03</span><div><h2>Interface Themes</h2><p class="summary">Restyle the complete Toolkit without changing operational meaning.</p></div></div><div class="grid three"><div class="card"><h4>Map Command</h4><p>The original neutral operational interface.</p></div><div class="card"><h4>Cyberpunk</h4><p>Angular neon styling with cyan, yellow and red accents.</p></div><div class="card"><h4>Fallout 4</h4><p>Retro phosphor and Pip-Boy-inspired controls.</p></div><div class="card"><h4>Umbrella</h4><p>Biohazard containment and classified corporate styling.</p></div><div class="card"><h4>Factorio</h4><p>Industrial steel, copper controls and hazard detail.</p></div><div class="card"><h4>007 Intelligence</h4><p>Black-tie dossier styling with champagne-gold controls.</p></div><div class="card"><h4>Hyrule Command</h4><p>Royal gold, parchment cartography, ancient-blue illumination and luminous green energy.</p></div></div><div class="call warn"><strong>Protected semantic colours:</strong> clearing, assistance, warning and critical states retain their operational meaning across every interface system.</div></section>'''
help_text = replace_regex_once(
    help_text,
    r'<section class="section" id="interface-themes"[\s\S]*?</section>',
    interface_section,
    "Help interface systems section",
)
resource_section = '''<section class="section" id="resources" data-title="Resource and Transport Tools" data-keywords="resource gap radius transport watcher patient prisoner alliance sweep lssm release discharge code 5"><div class="head"><span class="num">08</span><div><h2>Resource and Transport Tools</h2><p class="summary">Coverage analysis, passive transport monitoring and manual alliance patient-release support.</p></div></div><h3>Resource Gap</h3><p>Compares mission requirements with available personal vehicle context inside the selected radius. It can add a map badge and a requirement breakdown to Mission Inspector.</p><h3>Transport Watcher</h3><p>Shows amber patient or prisoner badges beside missions where MissionChief indicates transport is required.</p><h3>Patient Transport Sweep</h3><ol class="steps"><li>Select <strong>Scan Transports</strong> to build the current alliance candidate queue.</li><li>Review the delay and maximum-per-run settings, then start the sweep manually.</li><li>The sweep opens one mission at a time, waits for delayed LSSM <strong>Release patient (No reward)</strong> controls and processes one eligible alliance-member ambulance at a time.</li><li>The signed-in player's verified vehicles are excluded. Rows with ambiguous ownership are skipped.</li><li>After each confirmed release, the same mission is reopened and rescanned. The individual vehicle-window route is used only when the LSSM controls do not appear.</li><li>Select <strong>Stop</strong> at any time. The Toolkit closes and removes only the MissionChief lightbox layers owned by the sweep before continuing or finishing.</li></ol><div class="call danger">Transport Sweep cannot grant alliance permissions and should be used only when your role and alliance rules allow it. It is manual, sequential, bounded and cancellation-aware.</div></section>'''
help_text = replace_regex_once(
    help_text,
    r'<section class="section" id="resources"[\s\S]*?</section>',
    resource_section,
    "Help resources section",
)
help_text = replace_once(
    help_text,
    '<span class="tag">Pixel Arcade Inspired</span>',
    '<span class="tag">Pixel Arcade Inspired</span><span class="tag">Hyrule Quest Reward</span>',
    "Help payout catalogue",
)
performance_section = '''<section class="section" id="performance" data-title="Performance and Cleanup" data-keywords="lag cache throttle interval observer request fetch leaflet blocker alliance buildings courses cleanup lifecycle lightbox sweep stacking"><div class="head"><span class="num">15</span><div><h2>Performance and Cleanup</h2><p class="summary">How background work is limited and safely removed.</p></div></div><div class="grid"><div class="card"><h4>Adaptive refresh</h4><p>Mission, progress and vehicle sources use separate intervals, minimum request gaps and error backoff.</p></div><div class="card"><h4>Caches and signatures</h4><p>Marker registries, building IDs, heatmap sources, mission snapshots and panel renders avoid unnecessary repetition.</p></div><div class="card"><h4>Runtime cleanup</h4><p>Timers, animation frames, observers, listeners, map bindings, requests and fetch controllers are centrally tracked.</p></div><div class="card"><h4>Single-window sweep lifecycle</h4><p>Patient Transport Sweep claims the exact MissionChief lightbox, iframe and backdrop layers created by each open action, closes them before navigation and removes only sweep-owned remnants.</p></div><div class="card"><h4>Alliance Buildings Map Blocker</h4><p>Suppresses the heavy map on the Alliance Buildings/Courses page and expands the list to full width.</p></div></div><p>Changing Map Blocker requires a reload. Repair logic restores and resizes the normal map after leaving the blocked page.</p></section>'''
help_text = replace_regex_once(
    help_text,
    r'<section class="section" id="performance"[\s\S]*?</section>',
    performance_section,
    "Help performance section",
)
help_text = replace_once(help_text, "across all six themes.", "across all seven interface systems.", "Help FAQ theme count")
help_text = replace_once(
    help_text,
    "MissionChief Map Command Toolkit · Help Centre for v4.2.1 · Updated 13 July 2026 · Conroy1988",
    "MissionChief Map Command Toolkit · Help Centre for v4.14.4 · Updated 17 July 2026 · Conroy1988",
    "Help footer version",
)
HELP.write_text(help_text, encoding="utf-8")

site = json.loads(SITE_DATA.read_text(encoding="utf-8"))
site["project"]["description"] = (
    "A configurable userscript that turns the MissionChief map into an operational command centre with mission "
    "intelligence, fleet monitoring, guarded transport tools, map utilities, responsive layouts, themed interfaces "
    "and verified release automation."
)
mission = category(site, "Mission command")
maw = feature(mission, "Mission Age Watch")
maw["summary"] = "Tracks personal and alliance missions by age, ownership, category, severity and clearing state with fast mission controls."
maw["details"] = [
    "Age, ownership, category, status and additional filters",
    "Age, closest and furthest sorting with selectable map or saved-location origins",
    "No Units, Vehicles En-route, Needs Assistance, Stable and Clearing states",
    "Responsive positioning for Desktop, Tablet and iOS Mobile Mode",
]
insert_feature_after(
    mission,
    "Mission Inspector",
    {
        "name": "Mission Value",
        "summary": "Displays verified mission value inside opened MissionChief mission windows without obstructing native controls.",
        "details": [
            "Enabled by default with a persistent Ops toggle",
            "Uses verified live marker, snapshot, overlay and mission-list sources",
            "Hides unavailable values rather than guessing",
            "Measures native close/action controls and reserves safe clearance",
        ],
        "visual": "mission-value",
        "tags": ["missions", "value", "finance"],
    },
)
fleet = category(site, "Fleet and transport")
transport = feature(fleet, "Transport Watcher")
transport["summary"] = "Highlights missions that still require patient or prisoner transport and provides live counts."
transport["details"] = [
    "Patient and prisoner transport-required markers",
    "Dynamic float placement",
    "Count summary integrated with operational overlays",
]
insert_feature_after(
    fleet,
    "Transport Watcher",
    {
        "name": "Patient Transport Sweep",
        "summary": "Manually releases eligible alliance-member ambulances sequentially while excluding the signed-in player's own vehicles.",
        "details": [
            "Prefers delayed LSSM mission-row release controls",
            "Processes one verified alliance vehicle at a time and rescans after every release",
            "Skips ambiguous ownership and blocks duplicate mission/vehicle actions",
            "Uses a bounded vehicle-window fallback only when LSSM controls do not appear",
            "Owns and removes the exact MissionChief lightbox layers created by the sweep",
        ],
        "visual": "transport-sweep",
        "tags": ["transport", "alliance", "lssm"],
    },
)
insert_feature_after(
    fleet,
    "Patient Transport Sweep",
    {
        "name": "Resource Gap",
        "summary": "Compares mission requirements with available personal vehicle context inside a selected radius.",
        "details": [
            "Configurable geographic radius",
            "Mission Inspector requirement breakdown",
            "Optional map badge",
            "Uses personal vehicle context rather than assuming alliance availability",
        ],
        "visual": "resource-gap",
        "tags": ["resources", "vehicles", "coverage"],
    },
)
responsive = category(site, "Responsive operation")
insert_feature_after(
    responsive,
    "Desktop, Tablet and iOS Mobile Mode",
    {
        "name": "Economy Mode",
        "summary": "Suppresses non-essential animation and presentation overhead for performance-sensitive devices or sessions.",
        "details": [
            "Static presentation where possible",
            "Reduced non-essential animation",
            "Works alongside browser reduced-motion preferences",
            "Does not remove operational controls or state information",
        ],
        "visual": "economy-mode",
        "tags": ["performance", "devices", "accessibility"],
    },
)
for payout_name in [
    "Hellfire Inspired",
    "Galactic Command",
    "Dark Fantasy Inspired",
    "Underworld Inspired",
    "Pixel Arcade Inspired",
]:
    if payout_name not in site["payoutThemes"]:
        hyrule_index = site["payoutThemes"].index("Hyrule Quest Reward")
        site["payoutThemes"].insert(hyrule_index, payout_name)

for chapter in site.get("documentation", []):
    if chapter.get("title") == "Mission systems":
        sections = chapter.setdefault("sections", [])
        for section in sections:
            if section.get("heading") == "Mission Age Watch":
                section["body"] = (
                    "Use Mission Age Watch to filter and sort personal and alliance missions by age, ownership, category, "
                    "operational state and selected distance origin, then zoom or open a mission directly."
                )
            if section.get("heading") == "Transport Watcher":
                section["body"] = "Transport Watcher identifies patient or prisoner transport-required missions and places its indicators alongside other active map overlays."
        headings = [item.get("heading") for item in sections]
        inspector_index = headings.index("Critical View and Mission Inspector")
        if "Mission Value" not in headings:
            sections.insert(
                inspector_index + 1,
                {
                    "heading": "Mission Value",
                    "body": "Mission Value displays a verified value inside opened mission windows, hides unavailable values and dynamically stays clear of MissionChief's native close and action controls.",
                },
            )
        headings = [item.get("heading") for item in sections]
        watcher_index = headings.index("Transport Watcher")
        if "Patient Transport Sweep" not in headings:
            sections.insert(
                watcher_index + 1,
                {
                    "heading": "Patient Transport Sweep",
                    "body": "Patient Transport Sweep is a manual, bounded alliance workflow. It excludes the signed-in player's own vehicles, prefers delayed LSSM release controls, processes one eligible alliance ambulance at a time, rescans after every release and closes only its own MissionChief lightbox layers.",
                },
            )
    if chapter.get("title") == "Settings and recovery":
        for section in chapter.get("sections", []):
            if section.get("heading") == "Import and export":
                section["body"] = (
                    "Use the Toolkit settings export to move configuration between Desktop, Tablet and iOS Mobile Mode. "
                    "Exports are timestamped and can contain the saved Discord webhook, so store them privately."
                )

if not any(chapter.get("title") == "Fleet and transport tools" for chapter in site.get("documentation", [])):
    insert_at = next(
        (index for index, chapter in enumerate(site["documentation"]) if chapter.get("title") == "Map and bookmarks"),
        len(site["documentation"]),
    )
    site["documentation"].insert(
        insert_at,
        {
            "title": "Fleet and transport tools",
            "sections": [
                {
                    "heading": "Resource Gap",
                    "body": "Resource Gap compares mission requirements with personal vehicle context inside a configurable radius and can expose the breakdown in Mission Inspector.",
                },
                {
                    "heading": "Auto-load all vehicles",
                    "body": "When enabled, Auto-load all vehicles uses MissionChief's native hidden-vehicle batch control inside the active mission window with bounded retries and duplicate-request protection.",
                },
                {
                    "heading": "Economy Mode",
                    "body": "Economy Mode reduces non-essential animation and presentation overhead while retaining operational state, controls and safety indicators.",
                },
            ],
        },
    )
for item in site.get("knownIssues", []):
    if item.get("title") == "No release-blocking issue is recorded for the current verified release":
        item["body"] = (
            "The release dashboard records the current release channels and integrity state. Confirmed lower-priority defects and planned work remain visible in the public GitHub issue tracker."
        )
site["mediaRoadmap"] = [
    "Before-and-after map comparison",
    "All seven interface systems: Map Command, Cyberpunk, Fallout, Umbrella, Factorio, 007 Intelligence and Hyrule Command",
    "Mission Age Watch workflow",
    "Mission Value inside a native mission window",
    "Patient Transport Sweep workflow",
    "Coverage Heat Map",
    "Smart Bookmark Labels",
    "Payout presentations",
    "Tablet and iOS Mobile Mode",
    "Critical View and Mission Inspector",
]
SITE_DATA.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")

greasy = GREASY.read_text(encoding="utf-8")
greasy = replace_once(
    greasy,
    "- Mission Age Watch, Critical View and Mission Inspector",
    "- Mission Age Watch, Mission Value, Critical View and Mission Inspector",
    "Greasy Fork mission feature summary",
)
greasy = replace_once(
    greasy,
    "- Transport alerts and guarded Transport Sweep",
    "- Patient and prisoner transport alerts plus a manual, guarded Patient Transport Sweep for eligible alliance-member ambulances",
    "Greasy Fork transport summary",
)
greasy = replace_once(
    greasy,
    "- Exported Toolkit settings do not include the Discord webhook",
    "- Exported Toolkit settings can include the saved Discord webhook and should be stored privately",
    "Greasy Fork webhook export privacy",
)
GREASY.write_text(greasy, encoding="utf-8")

site_guide = SITE_GUIDE.read_text(encoding="utf-8")
site_guide = replace_once(
    site_guide,
    "| `CHANGELOG.md` | Release history |",
    "| `CHANGELOG.md` | Release history |\n| `README.md` | Primary GitHub landing page and installation summary |\n| `help/index.html` | Searchable Help Centre loaded by the userscript |\n| `docs/greasyfork-description.md` | Greasy Fork-synchronised Additional Info page |",
    "SITE source table",
)
site_guide = replace_once(
    site_guide,
    "5. Enforces output file-count and size limits.\n6. Retains a complete preview artifact for 14 days.",
    "5. Enforces output file-count and size limits.\n6. Cross-checks the README, Help Centre, Pages catalogue and Greasy Fork description for current version, theme, feature and privacy claims.\n7. Retains a complete preview artifact for 14 days.",
    "SITE validation list",
)
site_guide = replace_once(
    site_guide,
    "Feature documentation should describe current public behaviour. Experimental ideas belong in issues or Discussions rather than the published catalogue.",
    "Feature documentation should describe current public behaviour. The README, Help Centre, Pages catalogue and Greasy Fork description form one public documentation contract and must be updated together when shared claims change. Experimental ideas belong in issues or Discussions rather than the published catalogue.",
    "SITE maintenance contract",
)
SITE_GUIDE.write_text(site_guide, encoding="utf-8")

roadmap = ROADMAP.read_text(encoding="utf-8")
roadmap = replace_once(
    roadmap,
    "- Enable GitHub Discussions and create a public GitHub Project when repository administration permits.",
    "- Keep GitHub Discussions support routes and the public project roadmap aligned with repository configuration.",
    "Roadmap community state",
)
ROADMAP.write_text(roadmap, encoding="utf-8")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
contract["schemaVersion"] = 2
for token in ["Patient Transport Sweep", "Mission Value", "Resource Gap", "Economy Mode"]:
    if token not in contract["requiredSourceTokens"]:
        contract["requiredSourceTokens"].append(token)
contract["requiredFeatureNames"] = [
    "Mission Age Watch",
    "Mission Value",
    "Patient Transport Sweep",
    "Resource Gap",
    "Auto-load all vehicles",
    "Vehicle Code Status",
    "Coverage Heat Map",
    "Smart Bookmark Labels",
    "Alliance Credits",
    "Financial intelligence",
    "Payout presentations",
    "Economy Mode",
    "Desktop, Tablet and iOS Mobile Mode",
]
contract["publicDocumentation"] = {
    "readmeRequiredTokens": [
        "Patient Transport Sweep",
        "Mission Value",
        "Resource Gap",
        "Economy Mode",
        "saved Discord webhook",
        "seven interface systems",
    ],
    "helpRequiredTokens": [
        "Patient Transport Sweep",
        "Hyrule Command",
        "LSSM",
        "saved Discord webhook",
        "seven interface systems",
    ],
    "helpForbiddenTokens": ["v4.2.1", "six interface themes", "all six themes"],
    "greasyForkRequiredTokens": ["Patient Transport Sweep", "Mission Value", "saved Discord webhook"],
    "greasyForkForbiddenTokens": ["Exported Toolkit settings do not include the Discord webhook"],
}
CONTRACT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

drift = DRIFT.read_text(encoding="utf-8")
drift = replace_once(
    drift,
    '    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")\n',
    '    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")\n'
    '    readme = (root / "README.md").read_text(encoding="utf-8")\n'
    '    help_centre = (root / "help/index.html").read_text(encoding="utf-8")\n'
    '    greasy_fork = (root / "docs/greasyfork-description.md").read_text(encoding="utf-8")\n',
    "drift public document reads",
)
drift = replace_once(
    drift,
    '        for path in [root / "README.md", root / "docs/site-data.json", root / ".github/release-settings.json"]\n',
    '        for path in [\n'
    '            root / "README.md",\n'
    '            root / "help/index.html",\n'
    '            root / "docs/greasyfork-description.md",\n'
    '            root / "docs/site-data.json",\n'
    '            root / ".github/release-settings.json",\n'
    '        ]\n',
    "drift install URL document set",
)
drift = replace_once(
    drift,
    '    if len(feature_names) < 10:\n        failures.append("Feature catalogue unexpectedly contains fewer than ten features")\n\n'
    '    media_roadmap = site.get("mediaRoadmap", [])\n',
    '    if len(feature_names) < 10:\n        failures.append("Feature catalogue unexpectedly contains fewer than ten features")\n\n'
    '    for required_name in contract.get("requiredFeatureNames", []):\n'
    '        if required_name not in feature_names:\n'
    '            failures.append(f"Required public feature is absent from the Pages catalogue: {required_name}")\n\n'
    '    public_docs = contract.get("publicDocumentation", {})\n'
    '    document_contracts = [\n'
    '        ("README", readme, public_docs.get("readmeRequiredTokens", []), []),\n'
    '        ("Help Centre", help_centre, public_docs.get("helpRequiredTokens", []), public_docs.get("helpForbiddenTokens", [])),\n'
    '        ("Greasy Fork description", greasy_fork, public_docs.get("greasyForkRequiredTokens", []), public_docs.get("greasyForkForbiddenTokens", [])),\n'
    '    ]\n'
    '    for document_name, document_text, required_tokens, forbidden_tokens in document_contracts:\n'
    '        document_lower = document_text.lower()\n'
    '        for token in required_tokens:\n'
    '            if str(token).lower() not in document_lower:\n'
    '                failures.append(f"{document_name} is missing required public claim: {token}")\n'
    '        for token in forbidden_tokens:\n'
    '            if str(token).lower() in document_lower:\n'
    '                failures.append(f"{document_name} still contains forbidden stale claim: {token}")\n'
    '    if f"v{version}".lower() not in help_centre.lower():\n'
    '        failures.append(f"Help Centre does not identify the current Toolkit version v{version}")\n'
    '    for theme in contract.get("themes", []):\n'
    '        if str(theme).lower() not in help_centre.lower():\n'
    '            failures.append(f"Help Centre omits supported interface system: {theme}")\n\n'
    '    media_roadmap = site.get("mediaRoadmap", [])\n',
    "drift feature and cross-document contract",
)
drift = replace_once(
    drift,
    '        "featureCount": len(feature_names),\n',
    '        "featureCount": len(feature_names),\n        "publicDocumentCount": 3,\n',
    "drift report public document count",
)
drift = replace_once(
    drift,
    '        f"- Shortcuts: **{len(report[\'documentedShortcuts\'])}**",\n',
    '        f"- Shortcuts: **{len(report[\'documentedShortcuts\'])}**",\n'
    '        f"- Public documentation surfaces checked: **{report[\'publicDocumentCount\']}**",\n',
    "drift markdown public document count",
)
DRIFT.write_text(drift, encoding="utf-8")

subprocess.run(["python3", "-m", "py_compile", ".github/scripts/check_documentation_drift.py", ".github/scripts/build_pages_site.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/check_documentation_drift.py", "--allow-release-candidate"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "docs/site-assets/site.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/build_pages_site.py"], cwd=ROOT, check=True)
for path in [CONTRACT, SITE_DATA, ROOT / "status/release-dashboard.json", ROOT / ".github/release-settings.json"]:
    json.loads(path.read_text(encoding="utf-8"))
shutil.rmtree(ROOT / "_site", ignore_errors=True)
for generated in [ROOT / "documentation-drift-report.json", ROOT / "documentation-drift-report.md"]:
    generated.unlink(missing_ok=True)
print("Repository documentation accuracy audit applied and validated")
