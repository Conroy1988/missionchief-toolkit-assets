#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CONTRACT = ROOT / ".github/scripts/test_section_navigation_contract.py"
FIXTURE = ROOT / ".github/fixtures/section-navigation-contract.json"
VERSION = "4.14.5"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.14.4", f"// @version      {VERSION}", "metadata version")
source, count = re.subn(
    r"(const\s+SCRIPT\s*=\s*\{\s*name\s*:\s*['\"][^'\"]+['\"]\s*,\s*version\s*:\s*['\"])4\.14\.4(['\"])",
    rf"\g<1>{VERSION}\2",
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise RuntimeError(f"runtime version: expected one match, found {count}")

# Preserve the stable internal key while giving the mixed financial section an accurate public label.
source = replace_once(
    source,
    '<button class="mcms-tab-btn" type="button" data-tab="discord">Discord</button>',
    '<button class="mcms-tab-btn" type="button" data-tab="discord">Finance</button>',
    "Finance tab label",
)

# Skins owns map-skin automation.
skins_anchor = '''                <div class="mcms-status">Fire Command, Police Tactical, Medical Control and Coastal Command use lightweight local tile filters and remain compatible with map overlays.</div>
            </section>
            <section class="mcms-tab-panel" data-panel="tools">'''
skins_replacement = '''                <div class="mcms-status">Fire Command, Police Tactical, Medical Control and Coastal Command use lightweight local tile filters and remain compatible with map overlays.</div>
                <div class="mcms-section-label">Automatic day / night</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('autoNight', '◑', 'Auto Night', 'Automatically switch operational map skins at the configured day and night times.')}
                </div>
                <div class="mcms-row"><span class="mcms-row-label">Night starts</span><input class="mcms-input" type="time" data-setting="auto-night-start"></div>
                <div class="mcms-row"><span class="mcms-row-label">Day starts</span><input class="mcms-input" type="time" data-setting="auto-day-start"></div>
                <div class="mcms-row"><span class="mcms-row-label">Night skin</span><select class="mcms-select" data-setting="auto-night-theme">${buildThemeOptions(state.autoNight.nightTheme)}</select></div>
                <div class="mcms-row"><span class="mcms-row-label">Day skin</span><select class="mcms-select" data-setting="auto-day-theme">${buildThemeOptions(state.autoNight.dayTheme)}</select></div>
            </section>
            <section class="mcms-tab-panel" data-panel="tools">'''
source = replace_once(source, skins_anchor, skins_replacement, "move Auto Night into Skins")

# Tools owns map-display controls, visibility and map-specific performance controls.
tools_anchor = '                <div class="mcms-section-label">Map visibility · shortcuts 1–9 · dashboards V/W</div>'
tools_replacement = '''                <div class="mcms-section-label">Map performance</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('allianceBuildingsMapBlocker', '▦', 'Alliance Map Blocker', 'Blocks the heavy map in the Alliance Buildings/Courses menu. ON means blocked. Reload required.')}
                </div>
                <div class="mcms-status"><strong>Map Blocker ON</strong> removes the Alliance Buildings map, expands the courses list and prevents its heavy marker layer attaching.</div>
                <div class="mcms-section-label">Map visibility · shortcuts 1–9 · dashboards V/W</div>'''
source = replace_once(source, tools_anchor, tools_replacement, "move Map Blocker into Tools")

# Remove duplicated controls. Tools remains the canonical home for shortcuts 6–9 and transport/unit overlays.
for old, label in [
    ("                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\n", "Resources Transport Watch duplicate"),
    ("                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\n", "Ops Transport Watch duplicate"),
    ("                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}\n", "Ops Unit Count duplicate"),
    ("                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}\n", "Ops Critical View duplicate"),
    ("                    ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}\n", "Ops Mission Age duplicate"),
]:
    source = replace_once(source, old, "", label)

# Resources owns guarded transport/resource workflows and vehicle-list loading.
resources_anchor = '''                <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
            </section>'''
resources_replacement = '''                <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
                <div class="mcms-section-label">Vehicle loading</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('autoLoadAllVehicles', '⇊', 'Auto-load all vehicles', 'Automatically activates MissionChief’s native Load more vehicles control inside an opened mission.')}
                </div>
                <div class="mcms-status">Transport Watcher and Unit Count remain under Tools as the canonical map-overlay controls for shortcuts 7 and 8.</div>
            </section>'''
source = replace_once(source, resources_anchor, resources_replacement, "move vehicle loading into Resources")

# Ops owns mission intelligence and tracking behaviour.
ops_anchor = "                    ${makeToggleButton('missionSpawn', '◎', 'New Mission', 'Animate genuinely new mission spawns with a radar pulse.')}\n"
ops_replacement = ops_anchor + '''                    ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}
                    ${makeToggleButton('missionLockAudio', '⌁', 'Tracking Audio', 'Play a short synthesized tracking cue during mission zoom and target acquisition.')}
'''
source = replace_once(source, ops_anchor, ops_replacement, "move operational intelligence into Ops")
source = replace_once(
    source,
    '''                    <button class="mcms-small-btn" style="height:34px !important;line-height:34px !important" type="button" data-action="open-critical-drawer">Open Mission Drawer (W)</button>
                    <button class="mcms-small-btn" style="height:34px !important;line-height:34px !important" type="button" data-action="fit-critical">Frame Aged</button>''',
    '''                    <button class="mcms-small-btn" type="button" data-action="open-critical-drawer">Open Mission Drawer (W)</button>
                    <button class="mcms-small-btn" type="button" data-action="fit-critical">Frame Aged</button>''',
    "remove fixed Mission Age action heights",
)
source = replace_once(
    source,
    '''                </div>
                <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>''',
    '''                </div>
                <div class="mcms-status">Mission Age and Critical View remain under Tools as the canonical shortcut controls for 6 and 9. Ops provides the mission workflow and dashboard actions.</div>
                <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>''',
    "Ops canonical-control note",
)

# Places owns all saved spatial destinations, including complete map profiles.
places_anchor = '''                <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
                <div class="mcms-bookmark-list"></div>
            </section>'''
places_replacement = '''                <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
                <div class="mcms-bookmark-list"></div>
                <div class="mcms-section-label">Saved Map Profiles</div>
                <div class="mcms-profile-list" data-profile-list></div>
                <div class="mcms-status">Profiles save your map location, zoom, skin, visibility filters and operational overlays.</div>
            </section>'''
source = replace_once(source, places_anchor, places_replacement, "move profiles into Places")

# Remove controls that now have clearer canonical homes outside Settings.
for old, label in [
    ("                    ${makeToggleButton('autoLoadAllVehicles', '⇊', 'Auto-load all vehicles', 'Automatically presses MissionChief’s Load more vehicles control whenever an opened mission limits the vehicle list.')}\n", "remove Settings vehicle loading"),
    ("                    ${makeToggleButton('autoNight', '◑', 'AutoNight', 'Automatically switch skins by time.')}\n", "remove Settings Auto Night"),
    ("                    ${makeToggleButton('allianceBuildingsMapBlocker', '▦', 'Map Blocker', 'Blocks the heavy map in the Alliance Buildings menu (Courses menu). ON means blocked. Reload required.')}\n", "remove Settings Map Blocker"),
    ("                    ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}\n", "remove Settings Incident Feed"),
    ("                    ${makeToggleButton('missionLockAudio', '⌁', 'Tracking Audio', 'Plays a short synthesized digital tracking cue during mission zoom and target acquisition.')}\n", "remove Settings Tracking Audio"),
]:
    source = replace_once(source, old, "", label)

source = replace_once(
    source,
    '''                <div class="mcms-section-label">Auto Night</div>
                <div class="mcms-row"><span class="mcms-row-label">Night starts</span><input class="mcms-input" type="time" data-setting="auto-night-start"></div>
                <div class="mcms-row"><span class="mcms-row-label">Day starts</span><input class="mcms-input" type="time" data-setting="auto-day-start"></div>
                <div class="mcms-row"><span class="mcms-row-label">Night skin</span><select class="mcms-select" data-setting="auto-night-theme">${buildThemeOptions(state.autoNight.nightTheme)}</select></div>
                <div class="mcms-row"><span class="mcms-row-label">Day skin</span><select class="mcms-select" data-setting="auto-day-theme">${buildThemeOptions(state.autoNight.dayTheme)}</select></div>
''',
    "",
    "remove Settings Auto Night rows",
)
source = replace_once(
    source,
    '''                <div class="mcms-section-label">Saved Map Profiles</div>
                <div class="mcms-profile-list" data-profile-list></div>
                <div class="mcms-status">Profiles save your map location, zoom, skin, visibility filters and operational overlays.</div>
''',
    "",
    "remove Settings profiles",
)
source = replace_once(source, '<div class="mcms-section-label">Behaviour</div>', '<div class="mcms-section-label">Input</div>', "Settings Input label")
source = replace_once(
    source,
    '''                <div class="mcms-status">The Incident Feed shows qualifying personal and alliance missions in the top status bar. Exceptionally old, stuck or mass-casualty incidents can appear regardless of the credit threshold. Hover pauses the feed; click an item to zoom to it.</div>
                <div class="mcms-status"><strong>Map Blocker ON</strong> is the performance mode for the Alliance Buildings menu (Courses menu). It removes that page's map, expands the courses list to full width and prevents its heavy marker layer attaching.</div>
''',
    "",
    "remove moved Settings status text",
)

# Shorter explicit financial actions plus wrapping-safe controls.
for old, new, label in [
    ("Generate and Post Supreme Audit", "Generate & Post Audit", "financial post label"),
    ("Refresh GitHub Financial Intelligence", "Refresh Financial Intelligence", "financial refresh label"),
    ("Clear This Player's Local Archive", "Clear Player Archive", "financial clear label"),
]:
    source = replace_once(source, old, new, label)

source = replace_once(
    source,
    '#${SCRIPT.panelId} .mcms-tab-btn { height: 26px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 8px !important; background: rgba(255,255,255,.06) !important; color: rgba(255,255,255,.78) !important; cursor: pointer !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; padding: 0 !important; overflow: hidden !important; }',
    '#${SCRIPT.panelId} .mcms-tab-btn { height: 26px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 8px !important; background: rgba(255,255,255,.06) !important; color: rgba(255,255,255,.78) !important; cursor: pointer !important; font-size: 9px !important; line-height: 1.1 !important; font-weight: 900 !important; padding: 0 3px !important; overflow: hidden !important; white-space: normal !important; overflow-wrap: anywhere !important; }',
    "wrapping tab labels",
)
source = replace_once(
    source,
    'width: 100% !important; min-width: 0 !important; height: 42px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 10px !important;',
    'width: 100% !important; min-width: 0 !important; min-height: 42px !important; height: auto !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 10px !important;',
    "auto-height main controls",
)
source = replace_once(
    source,
    '#${SCRIPT.panelId} .mcms-label { display: block !important; width: 100% !important; color: #f4f7ff !important; font-size: 10.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }',
    '#${SCRIPT.panelId} .mcms-label { display: block !important; width: 100% !important; color: #f4f7ff !important; font-size: 10.5px !important; line-height: 1.15 !important; font-weight: 900 !important; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; overflow-wrap: anywhere !important; }',
    "wrapping primary labels",
)
source = replace_once(
    source,
    '#${SCRIPT.panelId} .mcms-section-label { margin: 9px 0 6px 0 !important; color: rgba(233,238,245,.62) !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; letter-spacing: .55px !important; text-transform: uppercase !important; }',
    '#${SCRIPT.panelId} .mcms-section-label { margin: 9px 0 6px 0 !important; color: rgba(233,238,245,.62) !important; font-size: 9px !important; line-height: 1.25 !important; font-weight: 900 !important; letter-spacing: .55px !important; text-transform: uppercase !important; white-space: normal !important; overflow-wrap: anywhere !important; }',
    "wrapping section labels",
)
source = replace_once(
    source,
    '#${SCRIPT.panelId} .mcms-row-label { color: rgba(255,255,255,.82) !important; font-size: 10px !important; font-weight: 800 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }',
    '#${SCRIPT.panelId} .mcms-row-label { color: rgba(255,255,255,.82) !important; font-size: 10px !important; line-height: 1.2 !important; font-weight: 800 !important; overflow: visible !important; text-overflow: clip !important; white-space: normal !important; overflow-wrap: anywhere !important; }',
    "wrapping row labels",
)
small_rule = '#${SCRIPT.panelId} .mcms-position-btn, #${SCRIPT.panelId} .mcms-small-btn, #${SCRIPT.panelId} .mcms-bookmark-btn, #${SCRIPT.panelId} .mcms-pin-btn { width: 100% !important; min-width: 0 !important; height: 28px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 9px !important; background: rgba(255,255,255,.065) !important; color: rgba(255,255,255,.84) !important; cursor: pointer !important; font-size: 9px !important; line-height: 28px !important; font-weight: 900 !important; text-align: center !important; padding: 0 !important; overflow: hidden !important; }'
small_replacement = small_rule + '''
        #${SCRIPT.panelId} .mcms-small-btn { height: auto !important; min-height: 28px !important; line-height: 1.15 !important; padding: 5px 6px !important; white-space: normal !important; overflow-wrap: anywhere !important; display: flex !important; align-items: center !important; justify-content: center !important; }'''
source = replace_once(source, small_rule, small_replacement, "base small-button wrapping")
source = replace_once(
    source,
    '#${SCRIPT.panelId}.mcms-map-small .mcms-theme-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-toggle-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-place-main { height: 40px !important; padding: 5px !important; grid-template-columns: 18px minmax(0,1fr) !important; gap: 5px !important; }',
    '#${SCRIPT.panelId}.mcms-map-small .mcms-theme-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-toggle-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-place-main { min-height: 40px !important; height: auto !important; padding: 5px !important; grid-template-columns: 18px minmax(0,1fr) !important; gap: 5px !important; }',
    "map-small auto-height controls",
)
tablet_rule = '''        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
            min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
            font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
        }'''
tablet_replacement = tablet_rule + '''
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn {
            min-height: 44px !important; height: auto !important; line-height: 1.15 !important; padding: 7px 8px !important;
        }'''
source = replace_once(source, tablet_rule, tablet_replacement, "tablet small-button wrapping")
mobile_rule = 'html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }'
mobile_replacement = mobile_rule + '''
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn { min-height:44px !important; height:auto !important; line-height:1.15 !important; padding:7px !important; white-space:normal !important; overflow-wrap:anywhere !important; }'''
source = replace_once(source, mobile_rule, mobile_replacement, "mobile small-button wrapping")
source = replace_once(
    source,
    '#${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:nowrap !important; text-overflow:ellipsis !important; }',
    '#${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:normal !important; text-overflow:clip !important; overflow-wrap:anywhere !important; }',
    "backup-action wrapping",
)

SOURCE.write_text(source, encoding="utf-8")

# Changelog and in-product Help Centre.
changelog = CHANGELOG.read_text(encoding="utf-8")
entry = f'''## [{VERSION}] - 2026-07-17

### Changed
- Audited all command-panel sections and assigned every control one canonical home without changing its internal setting key, shortcut or saved state.
- Moved Auto Night to Skins, Alliance Map Blocker to Tools, vehicle auto-loading to Resources, operational feed/audio controls to Ops and saved map profiles to Places.
- Renamed the visible Discord tab to Finance while preserving the stable `discord` tab key for saved settings and imports.

### Fixed
- Removed duplicate Transport Watcher, Unit Count, Mission Age and Critical View controls from secondary sections.
- Reworked static, row and action-button labels to wrap safely across Desktop, compact Desktop, Tablet and iOS widths instead of clipping or overlapping.

### Compatibility
- Section order, theme support, feature behaviour, localStorage/import-export contracts and keyboard shortcuts remain unchanged.
- Added a fixture-backed section-navigation and narrow-label contract to the permanent userscript preflight.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
help_text = replace_once(help_text, "Guide for Toolkit v4.14.4", f"Guide for Toolkit v{VERSION}", "Help header version")
help_text = replace_once(help_text, "Help Centre for v4.14.4", f"Help Centre for v{VERSION}", "Help footer version")
old_tabs = '''<tr><td>Skins</td><td>Interface themes and operational map skins.</td></tr><tr><td>Tools</td><td>Map display controls, coverage and mission visibility.</td></tr><tr><td>Resources</td><td>Transport Sweep, Resource Gap and resource tools.</td></tr><tr><td>Ops</td><td>Session statistics, dashboards and completion history.</td></tr><tr><td>Payouts</td><td>Payout flash, themes, audio, threshold and tests.</td></tr><tr><td>Discord</td><td>Financial intelligence reports through your webhook.</td></tr><tr><td>Places</td><td>Quick Places, bookmarks and jumps.</td></tr><tr><td>Settings</td><td>Layouts, profiles, Auto Night, backup and recovery.</td></tr>'''
new_tabs = '''<tr><td>Skins</td><td>Interface themes, operational map skins and Auto Night.</td></tr><tr><td>Tools</td><td>Map display, coverage, visibility shortcuts and map-performance controls.</td></tr><tr><td>Resources</td><td>Transport Sweep, Resource Gap and vehicle-list loading.</td></tr><tr><td>Ops</td><td>Mission intelligence, operational dashboards, Mission Age workflow and session history.</td></tr><tr><td>Payouts</td><td>Payout flash, themes, audio, threshold and tests.</td></tr><tr><td>Finance</td><td>Discord financial reports and the player-linked local archive.</td></tr><tr><td>Places</td><td>Quick Places, bookmarks, screen shortcuts and saved map profiles.</td></tr><tr><td>Settings</td><td>Device layout, dock positioning, input, Economy Mode, backup and recovery.</td></tr>'''
help_text = replace_once(help_text, old_tabs, new_tabs, "Help panel-tab table")
HELP.write_text(help_text, encoding="utf-8")

fixture = {
    "tabs": [
        {"key": "skins", "label": "Skins"},
        {"key": "tools", "label": "Tools"},
        {"key": "resources", "label": "Resources"},
        {"key": "ops", "label": "Ops"},
        {"key": "payouts", "label": "Payouts"},
        {"key": "discord", "label": "Finance"},
        {"key": "places", "label": "Places"},
        {"key": "settings", "label": "Settings"},
    ],
    "placements": {
        "skins": ["makeToggleButton('autoNight'", "data-setting=\"auto-night-start\""],
        "tools": ["makeToggleButton('allianceBuildingsMapBlocker'", "makeToggleButton('transportWatcher'", "makeToggleButton('unitCommitment'", "makeToggleButton('criticalView'", "makeToggleButton('missionAge'"],
        "resources": ["data-action=\"scan-transport-sweep\"", "makeToggleButton('resourceGap'", "makeToggleButton('autoLoadAllVehicles'"],
        "ops": ["makeToggleButton('missionInspector'", "makeToggleButton('majorIncidentFeed'", "makeToggleButton('missionLockAudio'", "data-action=\"open-vehicle-status\""],
        "payouts": ["makeToggleButton('payoutFlash'", "data-action=\"test-payout-flash\""],
        "discord": ["data-setting=\"discord-webhook\"", "data-action=\"finance-archive-scan\""],
        "places": ["mcms-quick-list", "mcms-bookmark-list", "data-profile-list"],
        "settings": ["makeToggleButton('shortcuts'", "data-device-layout-status", "data-action=\"export-config\""],
    },
    "singlePlacementTokens": [
        "makeToggleButton('autoNight'",
        "makeToggleButton('allianceBuildingsMapBlocker'",
        "makeToggleButton('autoLoadAllVehicles'",
        "makeToggleButton('majorIncidentFeed'",
        "makeToggleButton('missionLockAudio'",
        "makeToggleButton('transportWatcher'",
        "makeToggleButton('unitCommitment'",
        "makeToggleButton('criticalView'",
        "makeToggleButton('missionAge'",
        "data-profile-list",
    ],
    "themes": ["Map Command", "Cyberpunk", "Fallout 4", "Umbrella", "Factorio", "007 Intelligence", "Hyrule Command"],
    "narrowLabelCases": [
        {"label": "Auto-load all vehicles", "width": 126, "icon": 18, "gap": 5, "padding": 10, "font": 10, "maxLines": 2},
        {"label": "Alliance Map Blocker", "width": 126, "icon": 20, "gap": 6, "padding": 12, "font": 10.5, "maxLines": 2},
        {"label": "Open Mission Drawer (W)", "width": 136, "icon": 0, "gap": 0, "padding": 12, "font": 9, "maxLines": 2},
        {"label": "Deep Scan All Available", "width": 136, "icon": 0, "gap": 0, "padding": 12, "font": 9, "maxLines": 2},
        {"label": "Refresh Financial Intelligence", "width": 276, "icon": 0, "gap": 0, "padding": 12, "font": 9, "maxLines": 2},
        {"label": "Generate & Post Audit", "width": 276, "icon": 0, "gap": 0, "padding": 12, "font": 9, "maxLines": 1},
    ],
}
FIXTURE.parent.mkdir(parents=True, exist_ok=True)
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

contract_text = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/section-navigation-contract.json"


def rule_body(source: str, selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{(?P<body>.*?)\}", source, re.S)
    assert match, f"Missing CSS rule: {selector}"
    return match.group("body")


def wrapped_lines(label: str, width: float, font: float) -> int:
    capacity = max(1, int(width / max(1.0, font * 0.56)))
    lines = 1
    used = 0
    for word in label.split():
        length = len(word)
        if used == 0:
            used = length
        elif used + 1 + length <= capacity:
            used += 1 + length
        else:
            lines += 1
            used = length
    return lines


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    start = source.index("        panel.innerHTML = `", source.index("const positionButtons"))
    end = source.index("\n        `;", start)
    panel = source[start:end]

    tabs = re.findall(r'data-tab="([^"]+)">([^<]+)</button>', panel)
    expected_tabs = [(item["key"], item["label"]) for item in fixture["tabs"]]
    assert tabs == expected_tabs, f"Tab order/labels drifted: {tabs}"
    panels = re.findall(r'<section class="mcms-tab-panel" data-panel="([^"]+)">', panel)
    assert panels == [item["key"] for item in fixture["tabs"]], f"Panel order drifted: {panels}"

    section_ranges = {}
    matches = list(re.finditer(r'<section class="mcms-tab-panel" data-panel="([^"]+)">', panel))
    for index, match in enumerate(matches):
        section_ranges[match.group(1)] = panel[match.start() : matches[index + 1].start() if index + 1 < len(matches) else len(panel)]

    for section, tokens in fixture["placements"].items():
        body = section_ranges[section]
        for token in tokens:
            assert token in body, f"{token!r} is not in canonical section {section}"
    for token in fixture["singlePlacementTokens"]:
        assert panel.count(token) == 1, f"{token!r} must appear once, found {panel.count(token)}"

    assert "if (merged.activeTab === 'fleet') merged.activeTab = 'resources';" in source
    assert "['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings']" in source

    label = rule_body(source, '#${SCRIPT.panelId} .mcms-label')
    assert "white-space: normal !important" in label
    assert "overflow-wrap: anywhere !important" in label
    assert "text-overflow: ellipsis" not in label
    row_label = rule_body(source, '#${SCRIPT.panelId} .mcms-row-label')
    assert "white-space: normal !important" in row_label
    assert "overflow-wrap: anywhere !important" in row_label
    section_label = rule_body(source, '#${SCRIPT.panelId} .mcms-section-label')
    assert "overflow-wrap: anywhere !important" in section_label

    for selector in [
        '#${SCRIPT.panelId} .mcms-small-btn',
        'html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn',
        'html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn',
    ]:
        body = rule_body(source, selector)
        assert "height: auto !important" in body or "height:auto !important" in body
        assert "line-height: 1.15 !important" in body or "line-height:1.15 !important" in body

    backup_actions = rule_body(source, '#${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn')
    assert "white-space:normal" in backup_actions.replace(" ", "")
    assert "text-overflow:ellipsis" not in backup_actions.replace(" ", "")

    for theme in fixture["themes"]:
        assert theme in source, f"Supported theme missing from source: {theme}"

    for case in fixture["narrowLabelCases"]:
        assert case["label"] in panel, f"Narrow-layout fixture label missing: {case['label']}"
        usable = case["width"] - case["icon"] - case["gap"] - case["padding"]
        needed = wrapped_lines(case["label"], usable, case["font"])
        assert needed <= case["maxLines"], f"{case['label']} needs {needed} lines at fixture width"

    print(f"Section-navigation contract passed: {len(tabs)} sections, {len(fixture['singlePlacementTokens'])} canonical controls and {len(fixture['narrowLabelCases'])} narrow-label cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
CONTRACT.write_text(contract_text, encoding="utf-8")

preflight = PREFLIGHT.read_text(encoding="utf-8")
preflight = replace_once(
    preflight,
    "  .github/scripts/test_desktop_panel_layout_contract.py\n",
    "  .github/scripts/test_desktop_panel_layout_contract.py\n  .github/scripts/test_section_navigation_contract.py\n",
    "preflight navigation contract",
)
PREFLIGHT.write_text(preflight, encoding="utf-8")

# Remove disposable audit material from the implementation branch.
for path in [
    ROOT / "docs/internal/issue-92-navigation-audit.md",
    ROOT / "docs/internal/issue-92-panel-source-extract.md",
    ROOT / "docs/internal/issue-92-label-css-audit.md",
]:
    path.unlink(missing_ok=True)
try:
    (ROOT / "docs/internal").rmdir()
except OSError:
    pass

subprocess.run(["python3", str(CONTRACT)], check=True, cwd=ROOT)
subprocess.run(["node", "--check", str(SOURCE)], check=True, cwd=ROOT)
print(f"Prepared Toolkit {VERSION} section-navigation candidate")
