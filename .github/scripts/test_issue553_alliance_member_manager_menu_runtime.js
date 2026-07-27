#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");
const fixture = JSON.parse(fs.readFileSync(
  path.join(root, ".github/fixtures/issue553-alliance-member-manager-menu.json"),
  "utf8"
));

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"' || char === "`") { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const helperText = extractFunction("makeAllianceMemberManagerToggleButton");
const helperSandbox = {};
vm.runInNewContext(`${helperText}\nthis.renderManagerButton = makeAllianceMemberManagerToggleButton;`, helperSandbox);
const html = helperSandbox.renderManagerButton();
for (const marker of [
  'class="mcms-toggle-btn"',
  'data-action="toggle-alliance-member-manager"',
  'data-mcms-alliance-member-manager-toggle="true"',
  'aria-pressed="false"',
  '<span class="mcms-iconbox">AM</span>',
  '<span class="mcms-label">Alliance Member Manager</span>',
  '<span class="mcms-pill">OFF</span>',
]) assert.ok(html.includes(marker), marker);

for (const marker of [
  '<div class="mcms-section-label" data-mcms-alliance-operations="label">Alliance Operations</div>',
  '<div class="mcms-grid-2" data-mcms-alliance-operations="controls">',
  "${makeToggleButton('allianceBuildingsMapBlocker'",
  "${makeAllianceMemberManagerToggleButton()}",
  "if (action === 'toggle-alliance-member-manager')",
  "setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled())",
]) assert.ok(source.includes(marker), marker);

const updateText = extractFunction("updateAllianceMemberManagerMenuControl");
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

const managerStart = source.indexOf("    // <mcms-alliance-member-manager>");
const managerEnd = source.indexOf("    // </mcms-alliance-member-manager>", managerStart);
const manager = source.slice(managerStart, managerEnd);
for (const forbidden of [
  "new MutationObserver(",
  "requestAnimationFrame(",
  "allianceMemberManagerMapBlockerButton",
  "ensureAllianceMemberManagerMenuControl",
  "queueAllianceMemberManagerMenuControl",
  "allianceMemberManagerMenuObserver",
]) assert.ok(!manager.includes(forbidden), forbidden);

console.log(`Issue #553 canonical Tools runtime passed: ${fixture.states.length} persisted states and zero post-render injection.`);
