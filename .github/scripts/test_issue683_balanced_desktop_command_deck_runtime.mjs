#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const start = source.indexOf(`    function ${name}(`);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0, quote = "", escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const char = source[index];
    if (quote) { if (escaped) escaped = false; else if (char === "\\") escaped = true; else if (char === quote) quote = ""; continue; }
    if (char === "'" || char === '"' || char === "`") { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const group = (name, count) => `<div class="mcms-control-group" data-control-group="${name}">${Array.from({ length: count }, () => "<button></button>").join("")}</div>`;
const dom = new JSDOM(`<!doctype html><html><body><div id="map"><div id="dock"><div class="mcms-launch-row"></div><div class="mcms-floating-filter">${group("visibility", 4)}${group("intelligence", 5)}${group("dashboard", 4)}${group("performance", 1)}</div><div class="mcms-screen-pins"><button></button><button></button><button></button><button></button></div></div><div id="panel"></div></div></body></html>`);
const control = dom.window.document.getElementById("dock");
const mapElement = dom.window.document.getElementById("map");
const viewport = { width: 1688, height: 1384, offsetLeft: 0, offsetTop: 0 };
const mapRect = { left: 15, right: 1130, top: 160, bottom: 722 };
control.querySelector(".mcms-launch-row").getBoundingClientRect = () => ({ width: 109, height: 56 });
mapElement.getBoundingClientRect = () => mapRect;
const sandbox = {
  Math, Number, String, Array, document: dom.window.document,
  SCRIPT: { controlId: "dock", panelId: "panel" }, activeDeviceLayout: "desktop",
  state: { commandBarOpen: true, nudge: { x: 246, y: 0 } }, isTouchLayoutActive: () => false,
  getLargestLeafletMap: () => mapElement, getViewportMetrics: () => viewport,
  collectDesktopWorkspaceObstructions: () => [{ rect: { left: 15, right: 1130, top: 160, bottom: 191 } }], activeDockPosition: () => "bl",
};
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("resolveDesktopDockWorkspace")}\n${extractFunction("resolveDesktopDockGrid")}\n${extractFunction("clearDesktopDockSizing")}\n${extractFunction("applyDesktopDockLayout")}\nthis.apply = applyDesktopDockLayout;`, sandbox);

assert.equal(sandbox.apply(mapElement, control), true);
assert.equal(control.dataset.mcmsDesktopDockFlow, "balanced");
assert.equal(control.style.getPropertyValue("--mcms-desktop-group-columns"), "2");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-width"), "646px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-width"), "646px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-max-height"), "36px");
assert.equal(control.dataset.mcmsDesktopDockScroll, "false");
assert.deepEqual(Array.from(control.querySelectorAll(".mcms-control-group"), node => node.style.getPropertyValue("--mcms-desktop-group-width")), ["320px", "320px", "320px", "320px"]);

sandbox.state.nudge.x = 0;
assert.equal(sandbox.apply(mapElement, control), true);
assert.equal(control.dataset.mcmsDesktopDockFlow, "compact", "wide workspace did not retain its compact command band");
assert.equal(control.dataset.mcmsDesktopPinsInline, "true");

sandbox.activeDeviceLayout = "tablet";
assert.equal(sandbox.apply(mapElement, control), false);
assert.equal(control.dataset.mcmsDesktopDockFlow, undefined);
console.log("Issue #683 balanced Desktop command deck runtime regression passed.");
