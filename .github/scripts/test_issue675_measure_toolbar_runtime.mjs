#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const match = new RegExp(`\\bfunction\\s+${name}\\s*\\(`, "u").exec(source);
  assert.ok(match, `${name} is missing`);
  const start = match.index;
  const brace = source.indexOf("{", source.indexOf("(", start));
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === "'" || character === '"' || character === "`") { quote = character; continue; }
    if (character === "{") depth += 1;
    if (character === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const iconsStart = source.indexOf("    const MAP_CONTROL_ICONS = Object.freeze(");
const iconsEnd = source.indexOf("\n\n    function makeFloatButton(", iconsStart);
assert.ok(iconsStart >= 0 && iconsEnd > iconsStart);

const stateNode = { textContent: "OFF" };
const button = {
  classList: { values: new Set(), toggle(name, enabled) { if (enabled) this.values.add(name); else this.values.delete(name); } },
  dataset: {},
  attributes: new Map(),
  querySelector(selector) { return selector === ".mcms-control-state" ? stateNode : null; },
  setAttribute(name, value) { this.attributes.set(name, value); },
};
const sandbox = {
  SCRIPT: { controlId: "toolkit-control" },
  mapMeasureRuntime: { active: false },
  document: { querySelector() { return button; } },
  escapeHtml(value) { return String(value); },
  updateUiToggleClass(target, name, enabled) { target.classList.toggle(name, enabled); },
  updateUiSetAttribute(target, name, value) { target.setAttribute(name, value); },
  updateUiSetDataset(target, name, value) { target.dataset[name] = value; },
  updateUiSetText(target, value) { target.textContent = value; },
};
vm.createContext(sandbox);
vm.runInContext(
  `${source.slice(iconsStart, iconsEnd)}\n${extractFunction("makeActionFloatButton")}\n${extractFunction("syncMapMeasureToolbarButton")}\n` +
    "globalThis.__api = { makeActionFloatButton, syncMapMeasureToolbarButton };",
  sandbox,
);

const markup = sandbox.__api.makeActionFloatButton("open-map-measure", "", "Drawing", "Activate Drawing", "Drawing", "Draw", "measure");
assert.match(markup, /data-action="open-map-measure"/u);
assert.match(markup, />Drawing</u);
assert.match(markup, /mcms-float-key[^>]*aria-hidden="true">↔</u);
assert.doesNotMatch(markup, /aria-keyshortcuts=""/u);

assert.equal(sandbox.__api.syncMapMeasureToolbarButton(), true);
assert.equal(stateNode.textContent, "READY");
assert.equal(button.dataset.mcmsState, "off");
assert.equal(button.attributes.get("aria-pressed"), "false");

sandbox.mapMeasureRuntime.active = true;
assert.equal(sandbox.__api.syncMapMeasureToolbarButton(), true);
assert.equal(stateNode.textContent, "ACTIVE");
assert.equal(button.dataset.mcmsState, "on");
assert.equal(button.attributes.get("aria-pressed"), "true");
assert.ok(button.classList.values.has("mcms-on"));

console.log("Issue #675 toolbar runtime passed: the compatibility action is labelled Drawing, activates without a blank shortcut and reports READY/ACTIVE state.");
