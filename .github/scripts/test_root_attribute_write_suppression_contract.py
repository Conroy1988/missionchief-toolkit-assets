#!/usr/bin/env python3
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
    setAttribute(name, value) {{ const key = String(name); const text = String(value); this.calls.push([key, text]); this.attributes.set(key, text); }}
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
    uiTheme: "mapCommand", theme: "nightshift", cleanMode: false, markerFocus: true,
    missionPulse: false, roadPriority: true, compactDock: false, commandBarOpen: true,
    economyMode: false, allianceBuildingsMap: true, tabletMode: "auto", mobileMode: "auto",
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
    "data-mcms-ui-theme": "mapCommand", "data-mc-map-skin": "nightshift", "data-mcms-clean": "false",
    "data-mcms-marker-focus": "true", "data-mcms-mission-pulse": "false", "data-mcms-road-priority": "true",
    "data-mcms-compact-dock": "false", "data-mcms-command-bar-open": "true", "data-mcms-economy": "false",
    "data-mcms-alliance-buildings-map": "enabled", "data-mcms-device-layout": "desktop", "data-mcms-tablet-mode": "auto",
    "data-mcms-tablet-active": "false", "data-mcms-mobile-mode": "auto", "data-mcms-mobile-active": "false",
    "data-mcms-tablet-orientation": "landscape", "data-mcms-mobile-orientation": "landscape",
    "data-mcms-show-alliance-missions": "true", "data-mcms-show-my-missions": "false",
    "data-mcms-show-vehicles": "true", "data-mcms-show-buildings": "false", "data-mcms-critical-view": "false"
}};
applyRootAttributes();
assert.equal(root.calls.length, 22, "first call writes every missing attribute");
assert.deepEqual(Object.fromEntries(root.attributes), expected, "first call preserves all baseline values");
assert.deepEqual(calculations, {{ layout: 1, tablet: 1, mobile: 1, viewport: 1 }});
root.clearCalls();
applyRootAttributes();
assert.equal(root.calls.length, 0, "unchanged repeat performs zero attribute mutations");
assert.deepEqual(calculations, {{ layout: 2, tablet: 2, mobile: 2, viewport: 2 }}, "calculations still run on every call");
state.cleanMode = true;
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [["data-mcms-clean", "true"]], "one changed state writes only its attribute");
root.attributes.set("data-mc-map-skin", "externally-broken");
root.attributes.delete("data-mcms-show-buildings");
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [["data-mc-map-skin", "nightshift"], ["data-mcms-show-buildings", "false"]], "external changes are repaired");
nextLayout = "tablet";
orientation = "portrait";
root.clearCalls();
applyRootAttributes();
assert.deepEqual(root.calls, [
    ["data-mcms-device-layout", "tablet"], ["data-mcms-tablet-active", "true"],
    ["data-mcms-tablet-orientation", "portrait"], ["data-mcms-mobile-orientation", "portrait"]
], "layout and orientation changes preserve ordering");
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
