#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
SITE_DATA = ROOT / "docs" / "site-data.json"

PREVIOUS = "4.20.0"
VERSION = "4.20.1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")

style_function = """    function ensureVersionStatusStyle() { if (document.getElementById(VERSION_STATUS.styleId)) return; const style = document.createElement('style'); style.id = VERSION_STATUS.styleId; style.textContent = `#${VERSION_STATUS.buttonId}{--mcms-version-accent:#6fb7ff;--mcms-version-accent-rgb:111,183,255;box-sizing:border-box;position:relative;display:inline-grid;grid-template-rows:20px auto;place-items:center;align-self:flex-start;flex:0 0 48px;width:48px;min-width:48px;height:48px;margin:0;padding:5px 4px 4px;overflow:hidden;border:1px solid rgba(var(--mcms-version-accent-rgb),.48);border-bottom:3px solid var(--mcms-version-accent);border-radius:11px;background:linear-gradient(180deg,rgba(30,36,43,.97) 0%,rgba(12,16,21,.97) 100%);color:#f5f7fa;font:800 7px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.48px;text-align:center;text-transform:uppercase;white-space:nowrap;box-shadow:0 3px 10px rgba(0,0,0,.34),inset 0 1px 0 rgba(255,255,255,.1);cursor:pointer;touch-action:manipulation;user-select:none;-webkit-tap-highlight-color:transparent;transition:transform .14s ease,filter .14s ease,border-color .14s ease,box-shadow .14s ease}#${VERSION_STATUS.buttonId}::before{content:"•";display:grid;place-items:center;width:18px;height:18px;border:1px solid rgba(var(--mcms-version-accent-rgb),.72);border-radius:7px;background:rgba(var(--mcms-version-accent-rgb),.14);color:var(--mcms-version-accent);font:900 11px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:0;box-shadow:0 0 8px rgba(var(--mcms-version-accent-rgb),.2),inset 0 1px 0 rgba(255,255,255,.08)}#${VERSION_STATUS.buttonId}:hover{transform:translateY(-1px);filter:brightness(1.08);box-shadow:0 5px 13px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.13)}#${VERSION_STATUS.buttonId}:active{transform:translateY(0);filter:brightness(.97)}#${VERSION_STATUS.buttonId}:focus-visible{outline:2px solid var(--mcms-version-accent);outline-offset:2px}#${VERSION_STATUS.buttonId}[data-state="latest"]{--mcms-version-accent:#5bd391;--mcms-version-accent-rgb:91,211,145}#${VERSION_STATUS.buttonId}[data-state="latest"]::before{content:"✓"}#${VERSION_STATUS.buttonId}[data-state="update"]{--mcms-version-accent:#ffc452;--mcms-version-accent-rgb:255,196,82}#${VERSION_STATUS.buttonId}[data-state="update"]::before{content:"↑"}#${VERSION_STATUS.buttonId}[data-state="checking"]{--mcms-version-accent:#76c7ff;--mcms-version-accent-rgb:118,199,255;cursor:progress;opacity:.88}#${VERSION_STATUS.buttonId}[data-state="checking"]::before{content:"…"}#${VERSION_STATUS.buttonId}[data-state="error"]{--mcms-version-accent:#ff7e7e;--mcms-version-accent-rgb:255,126,126}#${VERSION_STATUS.buttonId}[data-state="error"]::before{content:"!"}html[data-mcms-tablet-active="true"] #${VERSION_STATUS.buttonId}{grid-template-rows:17px auto;flex-basis:43px;width:43px;min-width:43px;height:43px;padding:4px 3px 3px;border-radius:10px;font-size:6.3px;letter-spacing:.35px}html[data-mcms-tablet-active="true"] #${VERSION_STATUS.buttonId}::before{width:16px;height:16px;border-radius:6px;font-size:10px}html[data-mcms-mobile-active="true"] #${VERSION_STATUS.buttonId}{grid-template-rows:19px auto;flex-basis:46px;width:46px;min-width:46px;height:46px;padding:4px 3px 4px;border-radius:11px;font-size:6.6px;letter-spacing:.38px}html[data-mcms-mobile-active="true"] #${VERSION_STATUS.buttonId}::before{width:18px;height:18px;border-radius:7px;font-size:11px}@media (prefers-reduced-motion:reduce){#${VERSION_STATUS.buttonId}{transition:none}}`; (document.head || document.documentElement).appendChild(style); }
"""
pattern = re.compile(r"    function ensureVersionStatusStyle\(\) \{.*?\n    function versionStatusOpen\(\)", re.S)
match = pattern.search(source)
if not match:
    raise AssertionError("version status style function boundary not found")
source = source[:match.start()] + style_function + "    function versionStatusOpen()" + source[match.end():]

source = replace_once(
    source,
    "button.className = 'mcms-version-btn'; const economy",
    "button.className = 'mcms-version-btn mcms-version-btn--tile'; button.dataset.variant = 'status-tile'; button.setAttribute('aria-live', 'polite'); const economy",
    "version tile semantics",
)
SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.0'", "version: '4.20.1'", "runtime fixture version")
runtime = replace_once(
    runtime,
    """    assert.strictEqual(document.getElementById(api.constants.buttonId), first, 'version control uses one collision-resistant ID');
    assert.strictEqual(row.children.indexOf(first), row.children.indexOf(economy) - 1, 'version control is placed immediately before Economy beside the main Toolkit shell');
    const styleText = document.getElementById(api.constants.styleId).textContent;
    assert(styleText.includes('data-mcms-tablet-active'), 'Tablet-specific version-control styling is present');
    assert(styleText.includes('data-mcms-mobile-active'), 'iOS/Mobile-specific version-control styling is present');
""",
    """    assert.strictEqual(document.getElementById(api.constants.buttonId), first, 'version control uses one collision-resistant ID');
    assert.strictEqual(row.children.indexOf(first), row.children.indexOf(economy) - 1, 'version control is placed immediately before Economy beside the main Toolkit shell');
    assert(first.className.includes('mcms-version-btn--tile'), 'version control uses the compact tile variant');
    assert.strictEqual(first.dataset.variant, 'status-tile', 'version control exposes its visual variant');
    assert.strictEqual(first.getAttribute('aria-live'), 'polite', 'version state changes are announced accessibly');
    const styleText = document.getElementById(api.constants.styleId).textContent;
    assert(styleText.includes('grid-template-rows:20px auto'), 'Desktop version control uses vertical tile geometry');
    assert(styleText.includes('width:48px;min-width:48px;height:48px'), 'Desktop version tile has aligned 48px dimensions');
    assert(styleText.includes('[data-state="latest"]::before{content:"✓"'), 'LATEST state includes a check indicator');
    assert(styleText.includes('[data-state="update"]::before{content:"↑"'), 'UPDATE state includes an update indicator');
    assert(styleText.includes('[data-state="error"]::before{content:"!"'), 'RETRY state includes an error indicator');
    assert(!styleText.includes('min-width:56px;height:34px'), 'legacy horizontal status pill is removed');
    assert(styleText.includes('data-mcms-tablet-active'), 'Tablet-specific version-control styling is present');
    assert(styleText.includes('data-mcms-mobile-active'), 'iOS/Mobile-specific version-control styling is present');
""",
    "runtime visual assertions",
)
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '    assert "setInterval(" not in block, "version checker must not poll continuously"\n',
    '    assert "setInterval(" not in block, "version checker must not poll continuously"\n    assert "mcms-version-btn--tile" in block\n    assert "data-variant = \'status-tile\'" not in block  # dataset assignment remains property-based\n    assert "button.dataset.variant = \'status-tile\'" in block\n    assert "width:48px;min-width:48px;height:48px" in block\n    assert "grid-template-rows:20px auto" in block\n    assert "[data-state=\\\"latest\\\"]::before{content:\\"✓\\\"" in block\n    assert "[data-state=\\\"update\\\"]::before{content:\\"↑\\\"" in block\n    assert "min-width:56px;height:34px" not in block\n',
    "version visual contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [Unreleased]

## [4.20.1] - 2026-07-19

### Changed
- Replaced the wide horizontal version-status pill with a compact vertical HUD tile aligned to the primary Toolkit and Economy map controls.
- Moved state emphasis from a large coloured background to a dark theme-neutral surface with a small status badge, accent border and bottom status rail.
- Added distinct non-colour indicators for **LATEST**, **UPDATE**, **CHECK** and **RETRY** while preserving all v4.20.0 checking, caching and manual-refresh behaviour.

### Responsive
- Added dedicated 48px Desktop, 43px Tablet and 46px iOS/Mobile tile geometry with nowrap labels and reliable touch targets.
- Added reduced-motion handling and retained keyboard focus, accessible labels and polite state announcements.

### Validation
- Added deterministic visual-contract fixtures for tile dimensions, state icons, placement, accessibility and removal of the legacy horizontal pill.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8").replace("Guide for Toolkit v4.20.0", "Guide for Toolkit v4.20.1")
HELP_INDEX.write_text(help_index, encoding="utf-8")

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-19"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.20.1 redesigns the live version control as a compact vertical HUD tile with state icons and dedicated Desktop, Tablet and iOS geometry while retaining the 30-minute update-check contract."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
found = False
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Live Version Status":
            found = True
            feature["summary"] = "Shows LATEST or UPDATE in a compact vertical HUD tile beside the main map control using the verified production release contract."
            feature["details"] = [
                "Theme-neutral status tile with distinct check, update, checking and retry indicators",
                "30-minute successful cache and 10-minute failure cooldown",
                "15-second delayed boot check with visibility-based stale refresh",
                "Dedicated Desktop, Tablet and iOS geometry with manual rechecking",
            ]
if not found:
    raise AssertionError("Live Version Status documentation feature not found")
SITE_DATA.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

Path(__file__).unlink(missing_ok=True)
print(f"Prepared Toolkit {VERSION} version-status UI redesign")
