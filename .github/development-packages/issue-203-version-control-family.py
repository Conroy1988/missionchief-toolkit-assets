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

PREVIOUS = "4.20.1"
VERSION = "4.20.2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_pattern_once(text: str, pattern: str, replacement: str, label: str) -> str:
    matches = list(re.finditer(pattern, text, flags=re.S))
    if len(matches) != 1:
        raise AssertionError(f"{label}: expected one match, found {len(matches)}")
    match = matches[0]
    return text[:match.start()] + replacement + text[match.end():]


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")

render_function = """    function versionStatusRender() { const button = document.getElementById(VERSION_STATUS.buttonId); if (!button) return; const installed = SCRIPT.version; const available = versionStatusModel.manifest?.version || ''; const stateName = versionStatusModel.state; const labels = { idle: 'CHECK', checking: 'CHECK', latest: 'LATEST', update: 'UPDATE', error: 'RETRY' }; const label = labels[stateName] || 'CHECK'; button.textContent = ''; button.dataset.label = label; button.dataset.state = stateName; button.setAttribute('aria-busy', String(stateName === 'checking')); let title = `Check Toolkit ${installed} against the verified production release.`; if (stateName === 'checking') title = `Checking Toolkit ${installed} for updates…`; if (stateName === 'latest') title = `Toolkit ${installed} is current — open release notes. Shift-click, right-click or long-press to recheck.`; if (stateName === 'update') title = `Toolkit ${installed} installed; ${available} available — open update page. Shift-click, right-click or long-press to recheck.`; if (stateName === 'error') title = 'Version check unavailable — activate to retry.'; button.title = title; button.setAttribute('aria-label', title); }
"""
source = replace_pattern_once(
    source,
    r"    function versionStatusRender\(\) \{.*?\n    function ensureVersionStatusStyle\(\)",
    render_function + "    function ensureVersionStatusStyle()",
    "version status renderer",
)

style_function = """    function ensureVersionStatusStyle() { if (document.getElementById(VERSION_STATUS.styleId)) return; const style = document.createElement('style'); style.id = VERSION_STATUS.styleId; style.textContent = `#${VERSION_STATUS.buttonId}{--mcms-version-accent:#6fb7ff;--mcms-version-accent-rgb:111,183,255;box-sizing:border-box!important;position:relative;display:inline-flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:2px!important;align-self:flex-start;flex:0 0 48px!important;width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important;min-height:48px!important;max-height:48px!important;margin:0!important;padding:4px 3px 3px!important;overflow:hidden!important;border:1px solid rgba(255,255,255,.26)!important;border-radius:9px!important;background:linear-gradient(180deg,rgba(48,53,59,.98) 0%,rgba(15,19,23,.98) 100%)!important;color:#f5f7fa!important;text-align:center!important;text-transform:uppercase!important;white-space:nowrap!important;word-break:normal!important;overflow-wrap:normal!important;box-shadow:0 3px 9px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.12),0 0 0 1px rgba(var(--mcms-version-accent-rgb),.11)!important;cursor:pointer;touch-action:manipulation;user-select:none;-webkit-tap-highlight-color:transparent}#${VERSION_STATUS.buttonId}::before{content:"•"!important;box-sizing:border-box;display:flex!important;align-items:center!important;justify-content:center!important;flex:0 0 20px!important;width:20px!important;height:20px!important;margin:0!important;padding:0!important;border:1px solid rgba(var(--mcms-version-accent-rgb),.72)!important;border-radius:50%!important;background:rgba(var(--mcms-version-accent-rgb),.16)!important;color:var(--mcms-version-accent)!important;font:900 12px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;letter-spacing:0!important;white-space:nowrap!important;box-shadow:0 0 7px rgba(var(--mcms-version-accent-rgb),.22),inset 0 1px 0 rgba(255,255,255,.1)!important}#${VERSION_STATUS.buttonId}::after{content:attr(data-label)!important;box-sizing:border-box;display:block!important;width:100%!important;max-width:100%!important;margin:0!important;padding:0!important;overflow:hidden!important;color:#f5f7fa!important;font:800 7.2px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;letter-spacing:.12px!important;text-align:center!important;text-transform:uppercase!important;white-space:nowrap!important;word-break:keep-all!important;overflow-wrap:normal!important;text-overflow:clip!important}#${VERSION_STATUS.buttonId}:focus-visible{outline:2px solid var(--mcms-version-accent)!important;outline-offset:2px}#${VERSION_STATUS.buttonId}[data-state="latest"]{--mcms-version-accent:#5bd391;--mcms-version-accent-rgb:91,211,145}#${VERSION_STATUS.buttonId}[data-state="latest"]::before{content:"✓"!important}#${VERSION_STATUS.buttonId}[data-state="update"]{--mcms-version-accent:#ffc452;--mcms-version-accent-rgb:255,196,82}#${VERSION_STATUS.buttonId}[data-state="update"]::before{content:"↑"!important}#${VERSION_STATUS.buttonId}[data-state="checking"]{--mcms-version-accent:#76c7ff;--mcms-version-accent-rgb:118,199,255;cursor:progress;opacity:.88}#${VERSION_STATUS.buttonId}[data-state="checking"]::before{content:"…"!important}#${VERSION_STATUS.buttonId}[data-state="error"]{--mcms-version-accent:#ff7e7e;--mcms-version-accent-rgb:255,126,126}#${VERSION_STATUS.buttonId}[data-state="error"]::before{content:"!"!important}html[data-mcms-tablet-active="true"] #${VERSION_STATUS.buttonId}{flex-basis:44px!important;width:44px!important;min-width:44px!important;max-width:44px!important;height:44px!important;min-height:44px!important;max-height:44px!important;padding:3px 2px!important;border-radius:8px!important}html[data-mcms-tablet-active="true"] #${VERSION_STATUS.buttonId}::before{flex-basis:18px!important;width:18px!important;height:18px!important;font-size:11px!important}html[data-mcms-tablet-active="true"] #${VERSION_STATUS.buttonId}::after{font-size:6.7px!important;letter-spacing:0!important}html[data-mcms-mobile-active="true"] #${VERSION_STATUS.buttonId}{flex-basis:46px!important;width:46px!important;min-width:46px!important;max-width:46px!important;height:46px!important;min-height:46px!important;max-height:46px!important;padding:3px 2px!important;border-radius:9px!important}html[data-mcms-mobile-active="true"] #${VERSION_STATUS.buttonId}::before{flex-basis:19px!important;width:19px!important;height:19px!important;font-size:11px!important}html[data-mcms-mobile-active="true"] #${VERSION_STATUS.buttonId}::after{font-size:6.9px!important;letter-spacing:0!important}@media (prefers-reduced-motion:reduce){#${VERSION_STATUS.buttonId}{transition:none!important}}`; (document.head || document.documentElement).appendChild(style); }
"""
source = replace_pattern_once(
    source,
    r"    function ensureVersionStatusStyle\(\) \{.*?\n    function versionStatusOpen\(\)",
    style_function + "    function versionStatusOpen()",
    "version status control-family style",
)

source = replace_once(
    source,
    "button.className = 'mcms-version-btn mcms-version-btn--tile'; button.dataset.variant = 'status-tile'; button.setAttribute('aria-live', 'polite'); const economy",
    "button.className = 'mcms-economy-btn mcms-version-btn mcms-version-btn--unified'; button.dataset.variant = 'control-family'; button.setAttribute('aria-live', 'polite'); const economy",
    "version control-family semantics",
)

SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.1'", "version: '4.20.2'", "runtime fixture version")
runtime_assertions = """    assert(first.className.includes('mcms-economy-btn'), 'version control participates in the Economy control family');
    assert(first.className.includes('mcms-version-btn--unified'), 'version control uses the unified control-family variant');
    assert(!first.className.includes('mcms-version-btn--tile'), 'legacy standalone tile class is removed');
    assert.strictEqual(first.dataset.variant, 'control-family', 'version control exposes the unified visual variant');
    assert.strictEqual(first.getAttribute('aria-live'), 'polite', 'version state changes are announced accessibly');
    api.render();
    assert.strictEqual(first.dataset.label, 'CHECK', 'idle status is rendered through the dedicated label layer');
    assert.strictEqual(first.textContent, '', 'raw button text is removed to prevent inherited wrapping');
    const styleText = document.getElementById(api.constants.styleId).textContent;
    assert(styleText.includes('content:attr(data-label)!important'), 'visible status uses the dedicated pseudo label layer');
    assert(styleText.includes('white-space:nowrap!important'), 'status label wrapping is forcibly disabled');
    assert(styleText.includes('word-break:keep-all!important'), 'status words cannot be split by inherited game CSS');
    assert(styleText.includes('width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important'), 'Desktop status matches the control-family footprint');
    assert(styleText.includes('[data-state="latest"]::before{content:"✓"!important'), 'LATEST state includes a check indicator');
    assert(styleText.includes('[data-state="update"]::before{content:"↑"!important'), 'UPDATE state includes an update indicator');
    assert(styleText.includes('[data-state="error"]::before{content:"!"!important'), 'RETRY state includes an error indicator');
    assert(!styleText.includes('grid-template-rows:20px auto'), 'standalone grid tile geometry is removed');
    assert(styleText.includes('data-mcms-tablet-active'), 'Tablet-specific version-control styling is present');
    assert(styleText.includes('data-mcms-mobile-active'), 'iOS/Mobile-specific version-control styling is present');
"""
runtime = replace_pattern_once(
    runtime,
    r"    assert\(first\.className\.includes\('mcms-version-btn--tile'\).*?    assert\(styleText\.includes\('data-mcms-mobile-active'\).*?\n",
    runtime_assertions,
    "runtime visual assertions",
)
runtime = replace_once(
    runtime,
    "context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('4.20.2')) })); return { abort() {} }; };",
    "context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('4.20.3')) })); return { abort() {} }; };",
    "newer live version fixture",
)
runtime = replace_once(
    runtime,
    "    api.reset(); await api.runCheck(true); assert.strictEqual(api.model().state, 'update', 'successful live response renders UPDATE');\n",
    "    api.reset(); await api.runCheck(true); assert.strictEqual(api.model().state, 'update', 'successful live response renders UPDATE');\n    assert.strictEqual(first.dataset.label, 'UPDATE', 'UPDATE remains a single dedicated label after a live check');\n",
    "live update label assertion",
)
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract_visual = """    assert "mcms-version-btn--unified" in block
    assert "button.className = 'mcms-economy-btn mcms-version-btn mcms-version-btn--unified'" in block
    assert "button.dataset.variant = 'control-family'" in block
    assert "button.dataset.label = label" in block
    assert "button.textContent = ''" in block
    assert "content:attr(data-label)!important" in block
    assert "white-space:nowrap!important" in block
    assert "word-break:keep-all!important" in block
    assert "width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important" in block
    assert "[data-state=\"latest\"]::before{content:\"✓\"!important" in block
    assert "[data-state=\"update\"]::before{content:\"↑\"!important" in block
    assert "grid-template-rows:20px auto" not in block
    assert "mcms-version-btn--tile" not in block
"""
contract = replace_pattern_once(
    contract,
    r"    assert \"mcms-version-btn--tile\" in block\n.*?    assert \"min-width:56px;height:34px\" not in block\n",
    contract_visual,
    "version status visual contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [Unreleased]

## [4.20.2] - 2026-07-19

### Fixed
- Eliminated live `LATEST`, `UPDATE`, `CHECK` and `RETRY` label wrapping by moving visible status text out of the raw button text node and into a dedicated single-line label layer.
- Added selector-strength safeguards against MissionChief and theme-level `white-space`, word-break and overflow-wrap rules.

### Changed
- Rebuilt the version-status control as a member of the existing Economy control family with the same dark control surface, footprint, radius, shadow rhythm and icon-over-label composition.
- Removed the v4.20.1 standalone tile class, grid geometry and bottom accent rail while retaining compact state-specific circular indicators.

### Validation
- Extended runtime and contract fixtures to verify control-family class reuse, empty raw text, pseudo-label rendering, nowrap enforcement and Desktop, Tablet and iOS geometry.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8")
help_index = replace_once(help_index, "Guide for Toolkit v4.20.1", "Guide for Toolkit v4.20.2", "help guide version")
HELP_INDEX.write_text(help_index, encoding="utf-8")

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-19"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.20.2 prevents version-label wrapping and makes the live update control a unified member of the Menu and Economy map-control family without changing the verified update-check contract."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
found = False
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Live Version Status":
            found = True
            feature["summary"] = "Shows LATEST or UPDATE as a unified Menu/Economy-family map control with a guaranteed single-line status label."
            feature["details"] = [
                "Economy-family dark surface and icon-over-label control composition",
                "Dedicated nowrap label layer resistant to MissionChief and theme CSS",
                "30-minute successful cache and 10-minute failure cooldown",
                "Desktop, Tablet and iOS placement with manual rechecking",
            ]
if not found:
    raise AssertionError("Live Version Status documentation feature not found")
SITE_DATA.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

Path(__file__).unlink(missing_ok=True)
print(f"Prepared Toolkit {VERSION} unified version-control fix")
