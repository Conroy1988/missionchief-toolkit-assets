#!/usr/bin/env python3
"""Upgrade the canonical Tools runtime test for OFF, WAIT, ON and ERR mount states."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / ".github/fixtures/issue553-alliance-member-manager-menu.json"
TEST = ROOT / ".github/scripts/test_issue553_alliance_member_manager_menu_runtime.js"

fixture = {
    "schemaVersion": 4,
    "description": "Canonical Tools control, persisted setting and observable page-mount state cases for Issue #553.",
    "states": [
        {"enabled": False, "mountState": "disabled", "pill": "OFF", "pressed": "false"},
        {"enabled": True, "mountState": "watching", "pill": "WAIT", "pressed": "true"},
        {"enabled": True, "mountState": "mounted", "pill": "ON", "pressed": "true"},
        {"enabled": True, "mountState": "error", "pill": "ERR", "pressed": "true"},
    ],
}
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

text = TEST.read_text(encoding="utf-8")
old = '''const updateText = extractFunction("updateAllianceMemberManagerMenuControl");
const buttonState = { on: false, pressed: "false", pill: "OFF" };
const pill = { get textContent() { return buttonState.pill; }, set textContent(value) { buttonState.pill = value; } };
const button = {
  classList: { toggle(name, value) { assert.equal(name, "mcms-on"); buttonState.on = value; } },
  setAttribute(name, value) { if (name === "aria-pressed") buttonState.pressed = value; },
  querySelector(selector) { assert.equal(selector, ".mcms-pill"); return pill; },
};
const panel = { querySelector(selector) { assert.equal(selector, "[data-mcms-alliance-member-manager-toggle]"); return button; } };
const sandbox = {
  SCRIPT: { panelId: "toolkit-panel" },
  ALLIANCE_MEMBER_MANAGER: { menuAttribute: "data-mcms-alliance-member-manager-toggle" },
  document: { querySelector(selector) { assert.equal(selector, "#toolkit-panel"); return panel; } },
  enabled: false,
};
sandbox.allianceMemberManagerEnabled = () => sandbox.enabled;
vm.runInNewContext(`${updateText}\nthis.updateManagerButton = updateAllianceMemberManagerMenuControl;`, sandbox);
for (const item of fixture.states) {
  sandbox.enabled = item.enabled;
  sandbox.updateManagerButton();
  assert.equal(buttonState.on, item.enabled);
  assert.equal(buttonState.pressed, item.pressed);
  assert.equal(buttonState.pill, item.pill);
}
'''
new = '''const receiptText = extractFunction("allianceMemberManagerMountReceipt");
const updateText = extractFunction("updateAllianceMemberManagerMenuControl");
const buttonState = { on: false, pressed: "false", pill: "OFF", mountState: "idle", label: "" };
const pill = { get textContent() { return buttonState.pill; }, set textContent(value) { buttonState.pill = value; } };
const button = {
  title: "",
  classList: { toggle(name, value) { assert.equal(name, "mcms-on"); buttonState.on = value; } },
  setAttribute(name, value) {
    if (name === "aria-pressed") buttonState.pressed = value;
    if (name === "data-mcms-mount-state") buttonState.mountState = value;
    if (name === "aria-label") buttonState.label = value;
  },
  querySelector(selector) { assert.equal(selector, ".mcms-pill"); return pill; },
};
const panel = { querySelector(selector) { assert.equal(selector, "[data-mcms-alliance-member-manager-toggle]"); return button; } };
const sandbox = {
  SCRIPT: { panelId: "toolkit-panel" },
  ALLIANCE_MEMBER_MANAGER: { menuAttribute: "data-mcms-alliance-member-manager-toggle" },
  document: { querySelector(selector) { assert.equal(selector, "#toolkit-panel"); return panel; } },
  pageWindow: { __MCMS_UI_MOUNTS__: {} },
  allianceMemberManagerLastMountState: "idle",
  enabled: false,
};
sandbox.allianceMemberManagerEnabled = () => sandbox.enabled;
vm.runInNewContext(`${receiptText}\n${updateText}\nthis.updateManagerButton = updateAllianceMemberManagerMenuControl;`, sandbox);
for (const item of fixture.states) {
  sandbox.enabled = item.enabled;
  sandbox.pageWindow.__MCMS_UI_MOUNTS__.allianceMemberManager = { state: item.mountState };
  sandbox.updateManagerButton();
  assert.equal(buttonState.on, item.enabled);
  assert.equal(buttonState.pressed, item.pressed);
  assert.equal(buttonState.pill, item.pill);
  assert.equal(buttonState.mountState, item.mountState);
  assert.match(buttonState.label, /Alliance Member Manager/u);
}
'''
if text.count(old) != 1:
    raise RuntimeError("Unable to replace canonical Tools mount-state test")
text = text.replace(old, new, 1)
text = text.replace(
    'console.log(`Issue #553 canonical Tools runtime passed: ${fixture.states.length} persisted states and zero post-render injection.`);',
    'console.log(`Issue #553 canonical Tools runtime passed: ${fixture.states.length} persisted/mount states including OFF, WAIT, ON and ERR.`);',
)
TEST.write_text(text, encoding="utf-8")

print("Canonical Tools runtime now verifies OFF, WAIT, ON and ERR mount states.")
