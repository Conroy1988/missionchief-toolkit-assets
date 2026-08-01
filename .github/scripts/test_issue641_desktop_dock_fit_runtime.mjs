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

const sandbox = { Math, Number, String, Array, getViewportMetrics: () => ({ width: 1, height: 1, offsetLeft: 0, offsetTop: 0 }) };
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("resolveDesktopDockWorkspace")}\nthis.resolve = resolveDesktopDockWorkspace;`, sandbox);
const resolve = sandbox.resolve;

const screenshotMap = { left: 23, right: 660, top: 194, bottom: 1031 };
const screenshotViewport = { width: 660, height: 1289, offsetLeft: 0, offsetTop: 0 };
const incidentWire = { left: 25, right: 660, top: 193, bottom: 238 };
const withoutWire = resolve(screenshotMap, screenshotViewport, "bl", 8, []);
const withWire = resolve(screenshotMap, screenshotViewport, "bl", 8, [incidentWire]);
assert.equal(withWire.maxHeight, 743, "screenshot workspace was not reproduced");
assert.ok(withWire.maxHeight < withoutWire.maxHeight, "incident wire did not reserve vertical space");
assert.ok(screenshotMap.bottom - withWire.bottom - withWire.maxHeight >= incidentWire.bottom + 8, "bottom dock can overlap the incident wire");

const shortViewport = { width: 900, height: 600, offsetLeft: 0, offsetTop: 0 };
const tallMap = { left: 0, right: 900, top: 120, bottom: 900 };
const short = resolve(tallMap, shortViewport, "br", 8, [{ left: 0, right: 900, top: 120, bottom: 170 }]);
assert.equal(short.bottom, 308, "off-viewport map bottom was not pulled into view");
assert.ok(short.maxHeight > 0 && tallMap.bottom - short.bottom <= shortViewport.height - 8);

for (const scale of [0.8, 1, 1.25, 1.5, 2]) {
  const viewport = { width: 1366 / scale, height: 768 / scale, offsetLeft: 0, offsetTop: 0 };
  const map = { left: 20, right: viewport.width - 20, top: 112, bottom: viewport.height + 90 };
  const wire = { left: 20, right: viewport.width - 20, top: 112, bottom: 154 };
  for (const position of ["tl", "tr", "bl", "br"]) {
    const workspace = resolve(map, viewport, position, 8, [wire]);
    assert.ok(workspace && workspace.maxHeight >= 1, `${position} failed at ${scale * 100}% zoom`);
    assert.ok(workspace.maxWidth >= 1, `${position} overflowed horizontally at ${scale * 100}% zoom`);
    const top = position.startsWith("b") ? map.bottom - workspace.bottom - workspace.maxHeight : map.top + workspace.top;
    const bottom = position.startsWith("b") ? map.bottom - workspace.bottom : top + workspace.maxHeight;
    assert.ok(top >= wire.bottom + 8, `${position} crossed the wire at ${scale * 100}% zoom`);
    assert.ok(bottom <= viewport.height - 8, `${position} crossed the visible map bottom at ${scale * 100}% zoom`);
  }
}

assert.equal(resolve(null, screenshotViewport), null, "missing map must fail closed");
assert.equal(resolve({ left: 1, right: 1, top: 1, bottom: 2 }, screenshotViewport), null, "empty map must fail closed");

const dom = new JSDOM('<!doctype html><html><body><div id="map"><div id="dock"><div class="mcms-launch-row"></div><div class="mcms-floating-filter"></div><div class="mcms-screen-pins"><button></button><button></button></div></div><div id="panel"></div></div></body></html>');
const control = dom.window.document.getElementById("dock");
const mapElement = dom.window.document.getElementById("map");
control.querySelector(".mcms-launch-row").getBoundingClientRect = () => ({ height: 56 });
control.querySelector(".mcms-screen-pins").getBoundingClientRect = () => ({ height: 64 });
mapElement.getBoundingClientRect = () => screenshotMap;
const layoutSandbox = {
  Math, Number, String, Array,
  document: dom.window.document,
  SCRIPT: { controlId: "dock", panelId: "panel" },
  activeDeviceLayout: "desktop",
  state: { commandBarOpen: true, nudge: { x: 0, y: 0 } },
  isTouchLayoutActive: () => false,
  getLargestLeafletMap: () => mapElement,
  getViewportMetrics: () => screenshotViewport,
  collectDesktopWorkspaceObstructions: () => [{ rect: incidentWire }],
  activeDockPosition: () => "bl",
};
vm.createContext(layoutSandbox);
vm.runInContext(`${extractFunction("resolveDesktopDockWorkspace")}\n${extractFunction("resolveDesktopDockPresentation")}\n${extractFunction("clearDesktopDockSizing")}\n${extractFunction("applyDesktopDockLayout")}\nthis.apply = applyDesktopDockLayout;`, layoutSandbox);
assert.equal(layoutSandbox.apply(mapElement, control), true, "Desktop fit did not apply");
assert.match(control.dataset.mcmsDesktopDockFit, /^bl:/);
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-max-height"), "743px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-max-height"), "673px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-pin-max-height"), "64px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-width"), "617px");
assert.equal(control.style.getPropertyValue("--mcms-desktop-filter-columns"), "2");
layoutSandbox.activeDeviceLayout = "tablet";
assert.equal(layoutSandbox.apply(mapElement, control), false, "touch layout accepted Desktop sizing");
assert.equal(control.dataset.mcmsDesktopDockFit, undefined, "Desktop sizing survived layout exit");
assert.equal(control.style.getPropertyValue("--mcms-desktop-dock-max-height"), "");
console.log("Issue #641 Desktop dock containment runtime regression passed.");
