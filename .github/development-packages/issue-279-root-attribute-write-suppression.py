#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CONTRACT = ROOT / ".github/scripts/test_root_attribute_write_suppression_contract.py"
DOC = ROOT / "docs/issue-279-root-attribute-write-suppression.md"
OLD = "4.20.17"
NEW = "4.20.18"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def function_end(text: str, name: str) -> int:
    marker = f"function {name}("
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"{name}: function not found")
    brace = text.find("{", start)
    depth = 0
    state = "code"
    escaped = False
    index = brace
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "line":
            if char == "\n": state = "code"
            index += 1
            continue
        if state == "block":
            if char == "*" and nxt == "/": state = "code"; index += 2
            else: index += 1
            continue
        if state in {"single", "double", "template"}:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif (state == "single" and char == "'") or (state == "double" and char == '"') or (state == "template" and char == "`"): state = "code"
            index += 1
            continue
        if char == "/" and nxt == "/": state = "line"; index += 2; continue
        if char == "/" and nxt == "*": state = "block"; index += 2; continue
        if char == "'": state = "single"; index += 1; continue
        if char == '"': state = "double"; index += 1; continue
        if char == "`": state = "template"; index += 1; continue
        if char == "{": depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0: return index + 1
        index += 1
    raise RuntimeError(f"{name}: unterminated function")


def contract_content() -> str:
    return r'''#!/usr/bin/env python3
"""Verify unchanged root attributes do not trigger redundant DOM mutations."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"


def extract_function(source: str, masked: str, name: str) -> str:
    marker = f"function {name}("
    start = masked.find(marker)
    assert start >= 0, f"Missing function: {name}"
    assert masked.find(marker, start + len(marker)) < 0, f"Duplicate function: {name}"
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    assert closing is not None, f"Unterminated function: {name}"
    return source[start:closing + 1]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    masked = audit.mask_non_code(source)
    helper = extract_function(source, masked, "setAttributeIfChanged")
    apply_root = extract_function(source, masked, "applyRootAttributes")

    assert "element.getAttribute(name) === nextValue" in helper
    assert "element.setAttribute(name, nextValue)" in helper
    assert apply_root.count("setAttributeIfChanged(root,") == 22
    assert "root.setAttribute(" not in apply_root
    assert apply_root.index("setAttributeIfChanged(root, 'data-mcms-economy'") < apply_root.index("activeDeviceLayout = resolveDeviceLayout()")
    assert apply_root.index("activeDeviceLayout = resolveDeviceLayout()") < apply_root.index("setAttributeIfChanged(root, 'data-mcms-device-layout'")

    harness = f'''"use strict";
const assert = require("node:assert/strict");

class FakeRoot {{
    constructor() {{ this.attributes = new Map(); this.calls = []; }}
    getAttribute(name) {{ return this.attributes.has(String(name)) ? this.attributes.get(String(name)) : null; }}
    setAttribute(name, value) {{
        const key = String(name);
        const text = String(value);
        this.calls.push([key, text]);
        this.attributes.set(key, text);
    }}
    clearCalls() {{ this.calls.length = 0; }}
}}

const root = new FakeRoot();
const document = {{ documentElement: root }};
let activeDeviceLayout = "desktop";
let tabletModeActive = false;
let mobileModeActive = false;
let criticalViewActive = false;
let nextLayout = "desktop";
let orientation = "landscape";
const calculations = {{ layout: 0, tablet: 0, mobile: 0, viewport: 0 }};
const state = {{
    uiTheme: "mapCommand",
    theme: "nightshift",
    cleanMode: false,
    markerFocus: true,
    missionPulse: false,
    roadPriority: true,
    compactDock: false,
    commandBarOpen: true,
    economyMode: false,
    allianceBuildingsMap: true,
    tabletMode: "auto",
    mobileMode: "auto",
    visibility: {{ allianceMissions: true, myMissions: false, vehicles: true, buildings: false }}
}};
function normaliseUiTheme(value) {{ return String(value); }}
function resolveDeviceLayout() {{ calculations.layout += 1; return nextLayout; }}
function resolveTabletMode(layout) {{ calculations.tablet += 1; return layout === "tablet"; }}
function resolveMobileMode(layout) {{ calculations.mobile += 1; return layout === "mobile"; }}
function getViewportMetrics() {{ calculations.viewport += 1; return {{ orientation }}; }}

{helper}

{apply_root}

const expected = {{
    "data-mcms-ui-theme": "mapCommand",
    "data-mc-map-skin": "nightshift",
    "data-mcms-clean": "false",
    "data-mcms-marker-focus": "true",
    "data-mcms-mission-pulse": "false",
    "data-mcms-road-priority": "true",
    "data-mcms-compact-dock": "false",
    "data-mcms-command-bar-open": "true",
    "data-mcms-economy": "false",
    "data-mcms-alliance-buildings-map": "enabled",
    "data-mcms-device-layout": "desktop",
    "data-mcms-tablet-mode": "auto",
    "data-mcms-tablet-active": "false",
    "data-mcms-mobile-mode": "auto",
    "data-mcms-mobile-active": "false",
    "data-mcms-tablet-orientation": "landscape",
    "data-mcms-mobile-orientation": "landscape",
    "data-mcms-show-alliance-missions": "true",
    "data-mcms-show-my-missions": "false",
    "data-mcms-show-vehicles": "true",
    "data-mcms-show-buildings": "false",
    "data-mcms-critical-view": "false"
}};

applyRootAttributes();
assert.equal(root.calls.length, 22, "first call writes every missing attribute");
assert.deepEqual(Object.fromEntries(root.attributes), expected, "first call preserves all baseline values");
assert.deepEqual(calculations, {{ layout: 1, tablet: 1, mobile: 1, viewport: 1 }});

root.clearCalls();
applyRootAttributes();
assert.equal(root.calls.length, 0, "unchanged repeat performs zero attribute mutations");
assert.deepEqual(calculations, {{ layout: 2, tablet: 2, mobile: 2, viewport: 2 }}, "layout calculations still run on every call");

state.cleanMode = true;
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [["data-mcms-clean", "true"]], "one changed state writes only its attribute");

root.attributes.set("data-mc-map-skin", "externally-broken");
root.attributes.delete("data-mcms-show-buildings");
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [["data-mc-map-skin", "nightshift"], ["data-mcms-show-buildings", "false"]], "external mutation and removal are repaired");

nextLayout = "tablet";
orientation = "portrait";
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [
    ["data-mcms-device-layout", "tablet"],
    ["data-mcms-tablet-active", "true"],
    ["data-mcms-tablet-orientation", "portrait"],
    ["data-mcms-mobile-orientation", "portrait"]
], "layout and orientation changes preserve baseline ordering");
assert.equal(activeDeviceLayout, "tablet");
assert.equal(tabletModeActive, true);
assert.equal(mobileModeActive, false);

state.commandBarOpen = false;
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [["data-mcms-command-bar-open", "false"]]);

root.clearCalls();
assert.equal(setAttributeIfChanged(root, "data-mcms-command-bar-open", false), false);
assert.equal(root.calls.length, 0);
assert.equal(setAttributeIfChanged(root, "data-mcms-command-bar-open", true), true);
assert.deepEqual(root.calls, [["data-mcms-command-bar-open", "true"]]);

console.log("Root attribute write-suppression runtime fixtures passed");
'''
    with tempfile.TemporaryDirectory(prefix="mcms-root-attributes-") as directory:
        path = Path(directory) / "root-attribute-contract.js"
        path.write_text(harness, encoding="utf-8")
        result = subprocess.run(["node", str(path)], cwd=ROOT)
        assert result.returncode == 0, "root attribute runtime fixtures failed"

    print("Root attribute write-suppression contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, f"// @version      {OLD}", f"// @version      {NEW}", "metadata version")
    source = replace_once(source, f"version: '{OLD}'", f"version: '{NEW}'", "runtime version")

    helper = '''
    function setAttributeIfChanged(element, name, value) {
        const nextValue = String(value);
        if (element.getAttribute(name) === nextValue) return false;
        element.setAttribute(name, nextValue);
        return true;
    }

'''
    marker = "    function applyRootAttributes() {"
    if source.count(marker) != 1:
        raise RuntimeError("applyRootAttributes marker must appear exactly once")
    source = source.replace(marker, helper + marker, 1)

    start = source.index(marker)
    end = function_end(source, "applyRootAttributes")
    block = source[start:end]
    if block.count("root.setAttribute(") != 22:
        raise RuntimeError(f"applyRootAttributes expected 22 root writes, found {block.count('root.setAttribute(')}")
    block = block.replace("root.setAttribute(", "setAttributeIfChanged(root, ")
    source = source[:start] + block + source[end:]
    SOURCE.write_text(source, encoding="utf-8")

    CONTRACT.write_text(contract_content(), encoding="utf-8")

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    preflight = replace_once(
        preflight,
        "  .github/scripts/test_settings_ui_contract.py\n",
        "  .github/scripts/test_settings_ui_contract.py\n  .github/scripts/test_root_attribute_write_suppression_contract.py\n",
        "preflight contract registration",
    )
    PREFLIGHT.write_text(preflight, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    entry = f'''## [{NEW}] - 2026-07-20

### Performance
- Root Toolkit state attributes now mutate only when their string value actually changes, eliminating 22 redundant DOM mutations from unchanged `updateUI()` passes while preserving every layout calculation and output value.

### Validation
- Added fixture-backed first-write, unchanged-repeat, changed-state, external-repair, layout-orientation and helper return-value regressions against the extracted production functions.

'''
    changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog insertion")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(help_text, f"Guide for Toolkit v{OLD}", f"Guide for Toolkit v{NEW}", "help version")
    HELP.write_text(help_text, encoding="utf-8")

    DOC.write_text(f'''# Issue 279 — unchanged root-attribute write suppression

Toolkit v{NEW} preserves the complete `applyRootAttributes()` output while avoiding redundant `setAttribute()` calls whose current string value is already correct.

## Safety boundary

- All 22 root attributes remain present and retain their original ordering.
- Device, tablet, mobile and viewport calculations still execute on every call.
- No root node, value snapshot or state cache is retained.
- No observer, timer, animation frame, event listener or network path is added.
- External attribute removal or alteration is repaired on the next invocation.

## Deterministic evidence

The contract extracts the real helper and `applyRootAttributes()` from the canonical userscript and proves:

- 22 writes on an empty root;
- zero writes on an unchanged repeat;
- one write for one changed state value;
- exact repair of externally changed or removed values;
- correct ordered updates for tablet layout and orientation changes;
- unchanged helper return semantics.
''', encoding="utf-8")

    print(f"Prepared Toolkit {NEW} root-attribute write-suppression candidate")


if __name__ == "__main__":
    main()
