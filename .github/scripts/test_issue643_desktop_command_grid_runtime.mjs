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

const presentationSandbox = { Math, Number };
vm.createContext(presentationSandbox);
vm.runInContext(`${extractFunction("resolveDesktopDockPresentation")}\nthis.resolve = resolveDesktopDockPresentation;`, presentationSandbox);
const resolvePresentation = presentationSandbox.resolve;

assert.deepEqual(
  JSON.parse(JSON.stringify(resolvePresentation(920))),
  { dockWidth: 920, contentWidth: 805, filterColumns: 4, pinColumns: 8, launchWidth: 109, columnGap: 6 },
  "wide Desktop did not use the four-group layout",
);
assert.equal(resolvePresentation(700).filterColumns, 3, "medium Desktop did not reduce to three columns");
assert.equal(resolvePresentation(575).filterColumns, 2, "reported narrow Desktop did not reduce to two columns");
assert.equal(resolvePresentation(490).filterColumns, 1, "forced narrow Desktop did not fail closed to one column");
assert.equal(resolvePresentation(1600).dockWidth, 920, "Desktop dock exceeded the readable width cap");
assert.equal(resolvePresentation(250).dockWidth, 250, "Desktop dock exceeded its visible workspace");

const dom = new JSDOM('<!doctype html><html><body><div id="map"><div id="dock"><div class="mcms-launch-row"></div><div class="mcms-floating-filter"></div><div class="mcms-screen-pins"><button></button><button></button><button></button><button></button></div></div><div id="panel"></div></div></body></html>');
const control = dom.window.document.getElementById("dock");
const mapElement = dom.window.document.getElementById("map");
// Exact geometry class from the 603 × 1057 production screenshot supplied for Issue #643.
const mapRect = { left: 21, right: 603, top: 165, bottom: 976 };
const viewport = { width: 603, height: 1057, offsetLeft: 0, offsetTop: 0 };
const incidentWire = { left: 24, right: 603, top: 121, bottom: 166 };
control.querySelector(".mcms-launch-row").getBoundingClientRect = () => ({ height: 56 });
control.querySelector(".mcms-screen-pins").getBoundingClientRect = () => ({ height: 64 });
mapElement.getBoundingClientRect = () => mapRect;

const layoutSandbox = {
  Math, Number, String, Array,
  document: dom.window.document,
  SCRIPT: { controlId: "dock", panelId: "panel" },
  activeDeviceLayout: "desktop",
  state: { commandBarOpen: true, nudge: { x: 0, y: 0 } },
  isTouchLayoutActive: () => false,
  getLargestLeafletMap: () => mapElement,
  getViewportMetrics: () => viewport,
  collectDesktopWorkspaceObstructions: () => [{ rect: incidentWire }],
  activeDockPosition: () => "bl",
};
vm.createContext(layoutSandbox);
vm.runInContext(
  `${extractFunction("resolveDesktopDockWorkspace")}\n${extractFunction("resolveDesktopDockPresentation")}\n${extractFunction("clearDesktopDockSizing")}\n${extractFunction("applyDesktopDockLayout")}\nthis.apply = applyDesktopDockLayout;`,
  layoutSandbox,
);
assert.equal(layoutSandbox.apply(mapElement, control), true);
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-width"), "562px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-content-width"), "447px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-columns"), "2");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-columns"), "5");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-max-height"), "690px");
assert.equal(control.dataset.mcmsDesktopDockColumns, "2");
assert.match(control.dataset.mcmsDesktopDockFit, /^bl:562:760:690:64:2$/);

layoutSandbox.state.commandBarOpen = false;
assert.equal(layoutSandbox.apply(mapElement, control), true);
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-max-height"), "0px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-max-height"), "760px");

layoutSandbox.activeDeviceLayout = "tablet";
assert.equal(layoutSandbox.apply(mapElement, control), false);
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-width"), "");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-columns"), "");
assert.equal(control.dataset.mcmsDesktopDockColumns, undefined);

console.log("Issue #643 responsive Desktop command-grid runtime regression passed.");
