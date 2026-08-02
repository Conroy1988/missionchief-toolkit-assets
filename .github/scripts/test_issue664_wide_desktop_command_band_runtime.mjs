#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

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

const group = (name, count) => `<div class="mcms-control-group" data-control-group="${name}">${Array.from({ length: count }, (_, index) => `<button data-index="${index}"></button>`).join("")}</div>`;
const dom = new JSDOM(`<!doctype html><html><body><div id="map"><div id="dock"><div class="mcms-launch-row"></div><div class="mcms-floating-filter">${group("visibility", 4)}${group("intelligence", 5)}${group("dashboard", 3)}${group("performance", 1)}</div><div class="mcms-screen-pins"><button></button><button></button><button></button><button></button></div></div><div id="panel"></div></div></body></html>`);
const control = dom.window.document.getElementById("dock");
const mapElement = dom.window.document.getElementById("map");
const viewport = { width: 1700, height: 900, offsetLeft: 0, offsetTop: 0 };
const mapRect = { left: 0, right: 1700, top: 100, bottom: 900 };
control.querySelector(".mcms-launch-row").getBoundingClientRect = () => ({ width: 109, height: 56 });
mapElement.getBoundingClientRect = () => mapRect;

const sandbox = {
  Math, Number, String, Array,
  document: dom.window.document,
  SCRIPT: { controlId: "dock", panelId: "panel" },
  activeDeviceLayout: "desktop",
  state: { commandBarOpen: true, nudge: { x: 0, y: 0 } },
  isTouchLayoutActive: () => false,
  getLargestLeafletMap: () => mapElement,
  getViewportMetrics: () => viewport,
  collectDesktopWorkspaceObstructions: () => [],
  activeDockPosition: () => "bl",
};
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("resolveDesktopDockWorkspace")}\n${extractFunction("resolveDesktopDockGrid")}\n${extractFunction("clearDesktopDockSizing")}\n${extractFunction("applyDesktopDockLayout")}\nthis.apply = applyDesktopDockLayout;`, sandbox);

assert.equal(sandbox.apply(mapElement, control), true, "wide Desktop layout did not apply");
assert.equal(control.dataset.mcmsDesktopPinsInline, "true", "wide pins were left below the command groups");
assert.match(control.dataset.mcmsDesktopDockFit, /:inline$/, "wide layout identity did not record inline pins");
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-width"), "1661px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-width"), "1160px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-width"), "380px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-columns"), "4");
assert.deepEqual(
  Array.from(control.querySelectorAll(".mcms-control-group"), groupNode => groupNode.style.getPropertyValue("--mcms-desktop-button-columns")),
  ["4", "5", "3", "1"],
  "wide groups did not collapse to one button row",
);
assert.deepEqual(
  Array.from(control.querySelectorAll(".mcms-control-group"), groupNode => groupNode.style.getPropertyValue("--mcms-desktop-group-width")),
  ["350px", "436px", "264px", "92px"],
  "wide groups were stretched instead of content-sized",
);

const screenshot = sandbox.resolveDesktopDockGrid(1120, 330, [4, 5, 3, 1], 4, 109, 6);
assert.deepEqual(Array.from(screenshot.groupButtonColumns), [2, 3, 2, 1]);
assert.equal(screenshot.naturalFilterHeight, 94);
assert.equal(screenshot.pinsInline, true);
assert.equal(screenshot.dockWidth, 1120);

sandbox.activeDeviceLayout = "tablet";
assert.equal(sandbox.apply(mapElement, control), false, "Tablet accepted Desktop wide-band sizing");
assert.equal(control.dataset.mcmsDesktopPinsInline, undefined, "inline-pin state survived Desktop exit");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-width"), "");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-width"), "");
assert.ok(Array.from(control.querySelectorAll(".mcms-control-group")).every(groupNode => !groupNode.style.getPropertyValue("--mcms-desktop-group-width")), "content-sized group widths survived Desktop exit");

console.log("Issue #664 wide Desktop command band runtime regression passed.");
