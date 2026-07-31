#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const markers = ["    function " + name + "(", "    async function " + name + "("];
  const starts = markers.map(marker => source.indexOf(marker)).filter(index => index >= 0);
  assert.ok(starts.length, name + " is missing");
  const start = Math.min(...starts);
  const parameters = source.indexOf("(", start);
  let parameterDepth = 0;
  let brace = -1;
  for (let index = parameters; index < source.length; index += 1) {
    if (source[index] === "(") parameterDepth += 1;
    if (source[index] === ")" && --parameterDepth === 0) {
      brace = source.indexOf("{", index);
      break;
    }
  }
  assert.notEqual(brace, -1, name + " body is missing");
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
    if (char === "'" || char === '"' || char === String.fromCharCode(96)) {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error("Unable to extract " + name);
}

const dom = new JSDOM(`<!doctype html><html data-mcms-device-layout="tablet" data-mcms-density="standard"><body>
  <div id="mc-map-command-toolkit-control"></div>
  <div id="mc-map-command-toolkit-panel" class="mcms-open"></div>
  <nav id="normal-navigation" style="position:fixed;z-index:1100"></nav>
  <div id="foreign-overlay" style="position:fixed;z-index:2000"><div id="foreign-overlay-child" style="position:fixed;z-index:2001"></div></div>
  <div id="mc-map-command-toolkit-pressure-board" style="position:fixed;z-index:2147482000"></div>
</body></html>`, { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });

const { document } = dom.window;
const rects = new Map();
function setRect(id, { left, top, right, bottom }) {
  const element = document.getElementById(id);
  const rect = { left, top, right, bottom, width: right - left, height: bottom - top, x: left, y: top };
  element.getBoundingClientRect = () => rect;
  rects.set(element, rect);
  return element;
}

const control = setRect("mc-map-command-toolkit-control", { left: 100, top: 100, right: 300, bottom: 200 });
const panel = setRect("mc-map-command-toolkit-panel", { left: 20, top: 220, right: 720, bottom: 980 });
const navigation = setRect("normal-navigation", { left: 0, top: 0, right: 768, bottom: 60 });
const foreign = setRect("foreign-overlay", { left: 500, top: 100, right: 700, bottom: 180 });
setRect("foreign-overlay-child", { left: 510, top: 110, right: 690, bottom: 170 });
setRect("mc-map-command-toolkit-pressure-board", { left: 120, top: 120, right: 280, bottom: 190 });

const SCRIPT = {
  controlId: "mc-map-command-toolkit-control",
  panelId: "mc-map-command-toolkit-panel",
  toastId: "mc-map-command-toolkit-toast",
  payoutFlashId: "mc-map-command-toolkit-payout-flash",
  vehicleStatusId: "mc-map-command-toolkit-vehicle-status",
  pressureBoardId: "mc-map-command-toolkit-pressure-board",
  majorIncidentFeedId: "mc-map-command-toolkit-major-incident-feed",
  transportSweepHudId: "mc-map-command-toolkit-transport-sweep-hud",
  helpCenterId: "mc-map-command-toolkit-help-center",
  commandExperienceModalId: "mc-map-command-toolkit-command-experience",
  quickWheelId: "mc-map-command-toolkit-quick-wheel",
  fullscreenExitId: "mc-map-command-toolkit-fullscreen-exit",
  cleanExitId: "mcms-clean-exit",
  oldControlId: "mc-map-command-skins-control",
  oldGeoLabelLayerId: "mcms-persistent-label-layer",
};

const viewport = { width: 768, height: 1024, offsetLeft: 0, offsetTop: 0 };
const sandbox = {
  console,
  document,
  pageWindow: dom.window,
  SCRIPT,
  activeDeviceLayout: "tablet",
  state: { interfaceDensity: { desktop: "compact", tablet: "standard" } },
  getViewportMetrics: () => viewport,
  commandExperienceElement: id => document.getElementById(id),
  interfaceDensityForLayout: () => sandbox.state.interfaceDensity.tablet,
  isVisible: element => Boolean(element && element.dataset.hidden !== "true" && Number(element.getBoundingClientRect().width) > 0 && Number(element.getBoundingClientRect().height) > 0),
};

vm.createContext(sandbox);
vm.runInContext([
  "toolkitDoctorRectInsideViewport",
  "toolkitDoctorResponsiveStatus",
  "toolkitDoctorRectIntersectionArea",
  "toolkitDoctorOwnedSurfaceSelector",
  "toolkitDoctorOverlayConflictCount",
].map(extractFunction).join("\n") + "\nthis.__probe={responsive:toolkitDoctorResponsiveStatus,overlays:toolkitDoctorOverlayConflictCount};", sandbox);

let responsive = sandbox.__probe.responsive();
assert.equal(responsive.healthy, true);
assert.match(responsive.detail, /tablet geometry and standard density/u);

document.documentElement.setAttribute("data-mcms-density", "compact");
responsive = sandbox.__probe.responsive();
assert.equal(responsive.healthy, false);
assert.equal(responsive.detail, "Needs reconciliation: density attribute.");
document.documentElement.setAttribute("data-mcms-density", "standard");

panel.getBoundingClientRect = () => ({ left: -12, top: 220, right: 688, bottom: 980, width: 700, height: 760 });
responsive = sandbox.__probe.responsive();
assert.equal(responsive.healthy, false);
assert.equal(responsive.detail, "Needs reconciliation: open Settings panel bounds.");
panel.getBoundingClientRect = () => rects.get(panel);

assert.equal(sandbox.__probe.overlays(), 0, "normal navigation, non-intersecting foreign overlays and Toolkit-owned panels must not warn");
foreign.getBoundingClientRect = () => ({ left: 180, top: 130, right: 360, bottom: 230, width: 180, height: 100 });
assert.equal(sandbox.__probe.overlays(), 1, "a real intersecting foreign overlay must warn once");
navigation.getBoundingClientRect = () => ({ left: 0, top: 80, right: 768, bottom: 150, width: 768, height: 70 });
assert.equal(sandbox.__probe.overlays(), 2, "separate intersecting foreign overlay roots must remain independently visible");

control.dataset.hidden = "true";
panel.dataset.hidden = "true";
document.getElementById(SCRIPT.pressureBoardId).dataset.hidden = "true";
assert.equal(sandbox.__probe.overlays(), 0, "no warning is useful when no Toolkit surface is visible");

dom.window.close();
console.log("Issue #616 Toolkit Doctor runtime passed: precise responsive failures, owned-surface exclusion, non-overlap suppression, nested consolidation and genuine collision retention.");
