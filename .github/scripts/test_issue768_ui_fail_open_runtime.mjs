#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import { webcrypto } from "node:crypto";
import { JSDOM, VirtualConsole } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const RUNTIME_KEY = "__MC_MAP_COMMAND_TOOLKIT_RUNTIME__";
const CONTROL_ID = "mc-map-command-toolkit-control";
const STYLE_ID = "mc-map-command-toolkit-style-v4146";
const EMERGENCY_ID = "mcms-toolkit-emergency-launcher";
const EMERGENCY_STYLE_ID = "mcms-toolkit-emergency-style";
const STORAGE_KEY = "mc_map_command_toolkit_state_v150";
const LIVE_MAP_HTML = `<!doctype html>
<html><head><title>MissionChief</title></head>
<body class="dark bigMap bigMapDark missionchief">
  <nav id="navbar-main"></nav>
  <div id="map_outer"><div id="map" class="leaflet-container"><div class="leaflet-map-pane"></div></div></div>
  <aside id="mission_list"></aside>
</body></html>`;

function waitFor(predicate, label, timeoutMs = 20000) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const poll = () => {
      let value = null;
      try { value = predicate(); } catch (error) {}
      if (value) { resolve(value); return; }
      if (Date.now() - started >= timeoutMs) { reject(new Error(`Timed out waiting for ${label}`)); return; }
      setTimeout(poll, 20);
    };
    poll();
  });
}

function createProductionDom({ savedState = null } = {}) {
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", error => {
    if (!/Not implemented: (?:HTMLCanvasElement|navigation)/u.test(String(error?.message || error))) throw error;
  });
  const dom = new JSDOM(LIVE_MAP_HTML, {
    url: "https://www.missionchief.co.uk/",
    pretendToBeVisual: true,
    runScripts: "dangerously",
    virtualConsole,
  });
  const { window } = dom;
  const map = window.document.getElementById("map");
  const rectangleFor = element => {
    if (element?.id === "map" || element?.id === "map_outer") {
      return { x: 0, y: 40, left: 0, top: 40, right: 1363, bottom: 925, width: 1363, height: 885, toJSON() { return this; } };
    }
    if (element?.id === CONTROL_ID) {
      return { x: 12, y: 820, left: 12, top: 820, right: 222, bottom: 912, width: 210, height: 92, toJSON() { return this; } };
    }
    if (element?.id === EMERGENCY_ID) {
      return { x: 48, y: 50, left: 48, top: 50, right: 205, bottom: 94, width: 157, height: 44, toJSON() { return this; } };
    }
    return { x: 0, y: 0, left: 0, top: 0, right: 100, bottom: 40, width: 100, height: 40, toJSON() { return this; } };
  };
  Object.defineProperty(window.HTMLElement.prototype, "getBoundingClientRect", {
    configurable: true,
    value() { return rectangleFor(this); },
  });
  for (const [property, value] of [["offsetWidth", 1363], ["clientWidth", 1363], ["offsetHeight", 885], ["clientHeight", 885]]) {
    Object.defineProperty(map, property, { configurable: true, value });
  }
  Object.defineProperty(window, "innerWidth", { configurable: true, value: 1363 });
  Object.defineProperty(window, "innerHeight", { configurable: true, value: 936 });
  Object.defineProperty(window, "crypto", { configurable: true, value: webcrypto });
  Object.defineProperty(window.document, "hidden", { configurable: true, value: false });
  Object.defineProperty(window.document, "visibilityState", { configurable: true, value: "visible" });
  window.unsafeWindow = window;
  window.Response = globalThis.Response;
  window.Request = globalThis.Request;
  window.Headers = globalThis.Headers;
  window.TextEncoder = globalThis.TextEncoder;
  window.TextDecoder = globalThis.TextDecoder;
  window.AbortController = globalThis.AbortController;
  window.fetch = async () => new window.Response("{}", { status: 404, headers: { "content-type": "application/json" } });
  window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
  window.requestIdleCallback = callback => window.setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 50 }), 0);
  window.cancelIdleCallback = id => window.clearTimeout(id);
  window.ResizeObserver = class { observe() {} disconnect() {} };
  window.CSS ||= {};
  window.CSS.escape ||= value => String(value).replace(/[^a-zA-Z0-9_-]/gu, "_");
  window.open = () => null;
  window.confirm = () => true;
  window.GM_getValue = (_key, fallback) => fallback;
  window.GM_setValue = () => undefined;
  window.GM_deleteValue = () => undefined;
  window.GM_xmlhttpRequest = () => ({ abort() {} });
  if (savedState) window.localStorage.setItem(STORAGE_KEY, JSON.stringify(savedState));
  return { dom, window };
}

function evaluate(window, candidate = source, label = "issue768-production-runtime.js") {
  return window.eval(`${candidate}\n//# sourceURL=${label}`);
}

function destroyScenario(scenario, reason) {
  try { scenario.window[RUNTIME_KEY]?.destroy?.(reason); } catch (error) {}
  scenario.window.__MCMS_DEV_LAB_OBSERVER__?.disconnect?.();
  scenario.dom.window.close();
}

assert.match(source, /^\/\/ @version\s+10\.16\.5$/mu, "Issue #768 must ship as v10.16.5");
assert.ok(source.indexOf("ensureToolkitEmergencyLauncher();") < source.indexOf("const ALLIANCE_BUILDINGS_PATH_PATTERN"), "Emergency launcher must mount before the full bundle starts");

// 1. A half-created same-version runtime must not suppress a complete replacement.
const incomplete = createProductionDom();
let incompleteDestroyReason = "";
incomplete.window[RUNTIME_KEY] = {
  version: "10.16.5",
  phase: "ready",
  destroyed: false,
  recoverUi() { return true; },
  destroy(reason) { incompleteDestroyReason = reason; this.destroyed = true; },
};
evaluate(incomplete.window);
const replacementRuntime = await waitFor(
  () => incomplete.window[RUNTIME_KEY]?.version === "10.16.5" && incomplete.window[RUNTIME_KEY]?.phase === "ready" && incomplete.window[RUNTIME_KEY],
  "complete replacement runtime",
);
const replacementControl = await waitFor(
  () => incomplete.window.document.getElementById(CONTROL_ID)?.dataset?.mcmsLauncherReady === "true" && incomplete.window.document.getElementById(CONTROL_ID),
  "production-map command launcher",
);
assert.equal(incompleteDestroyReason, "replaced by a fully evaluated toolkit runtime");
assert.equal(replacementRuntime.destroyed, false);
assert.ok(replacementControl.classList.contains("mcms-pos-bl"), "launcher did not receive a fail-open map position");
assert.ok(incomplete.window.document.getElementById(STYLE_ID), "main Toolkit stylesheet is absent");
assert.equal(incomplete.window.document.getElementById(EMERGENCY_ID), null, "emergency launcher remained after the primary launcher became usable");

// 2. A complete same-version runtime is asked to self-heal instead of being replaced blindly.
const healthy = createProductionDom();
const healthyControl = healthy.window.document.createElement("div");
healthyControl.id = CONTROL_ID;
healthyControl.dataset.mcmsLauncherReady = "true";
healthy.window.document.getElementById("map").appendChild(healthyControl);
let healthyRecoveries = 0;
const healthyRuntime = {
  version: "10.16.5",
  phase: "ready",
  destroyed: false,
  recoverUi() { healthyRecoveries += 1; return true; },
};
healthy.window[RUNTIME_KEY] = healthyRuntime;
evaluate(healthy.window, source, "issue768-healthy-reinjection.js");
assert.equal(healthy.window[RUNTIME_KEY], healthyRuntime, "healthy same-version runtime was replaced");
assert.equal(healthyRecoveries, 1, "healthy same-version runtime was not asked to recover its UI");
assert.equal(healthy.window.document.getElementById(EMERGENCY_ID), null, "healthy same-version recovery retained the emergency launcher");

// 3. An exception after the dependency-light bootstrap must leave visible recovery ownership behind.
const interrupted = createProductionDom();
const interruptionMarker = "    const ALLIANCE_BUILDINGS_PATH_PATTERN";
assert.ok(source.includes(interruptionMarker), "Issue #768 interruption marker is missing");
const interruptedSource = source.replace(interruptionMarker, `    throw new Error("Issue #768 deliberate bootstrap interruption");\n${interruptionMarker}`);
assert.throws(() => evaluate(interrupted.window, interruptedSource, "issue768-interrupted-runtime.js"), /Issue #768 deliberate bootstrap interruption/u);
assert.ok(interrupted.window.document.getElementById(EMERGENCY_ID), "interrupted evaluation left no recovery launcher");
const emergencyStyle = interrupted.window.document.getElementById(EMERGENCY_STYLE_ID);
assert.ok(emergencyStyle, "interrupted evaluation left no independent recovery style");
assert.match(emergencyStyle.textContent, /1600ms forwards/u, "emergency launcher has no delayed fail-open reveal");

// 4. A late exception after runtime claim still leaves an active recovery entry point.
const claimedInterruption = createProductionDom();
const lateMarker = "    registerBootMaintenanceTasks({ uiOnly: true });";
assert.ok(source.includes(lateMarker), "Issue #768 late-interruption marker is missing");
const claimedInterruptedSource = source.replace(lateMarker, `    throw new Error("Issue #768 deliberate post-claim interruption");\n${lateMarker}`);
assert.throws(() => evaluate(claimedInterruption.window, claimedInterruptedSource, "issue768-post-claim-interruption.js"), /Issue #768 deliberate post-claim interruption/u);
assert.equal(claimedInterruption.window[RUNTIME_KEY]?.phase, "ready", "post-claim interruption left an unrecoverable runtime phase");
assert.equal(typeof claimedInterruption.window[RUNTIME_KEY]?.recoverUi, "function", "post-claim interruption published no recovery entry point");
const claimedRecovery = claimedInterruption.window.document.getElementById(EMERGENCY_ID);
assert.ok(claimedRecovery, "post-claim interruption left no recovery launcher");
claimedRecovery.click();
await waitFor(
  () => claimedInterruption.window.document.getElementById(CONTROL_ID)?.dataset?.mcmsLauncherReady === "true" && !claimedInterruption.window.document.getElementById(EMERGENCY_ID),
  "post-claim command-shell restoration",
);

// 5. Optional command-state and global-render failures cannot abort the primary launcher mount.
const renderFault = createProductionDom({
  savedState: {
    theme: "default",
    position: "bl",
    setupWizard: { completed: true },
    updateBriefing: { enabled: false, seenVersion: "10.16.5" },
    nudge: "legacy-corrupt-value",
    visibility: null,
    cleanMode: false,
  },
});
const faultedSource = source
  .replace("    function toolkitApplyCommandBarState(control = null) {", "    function toolkitApplyCommandBarState(control = null) {\n        throw new Error('Issue #768 command-state fault');")
  .replace("    function updateUI() {", "    function updateUI() {\n        throw new Error('Issue #768 global-render fault');");
evaluate(renderFault.window, faultedSource, "issue768-render-fault-runtime.js");
const faultTolerantControl = await waitFor(
  () => renderFault.window.document.getElementById(CONTROL_ID)?.dataset?.mcmsLauncherReady === "true" && renderFault.window.document.getElementById(CONTROL_ID),
  "fault-tolerant primary launcher",
);
assert.ok(faultTolerantControl.classList.contains("mcms-pos-bl"), "render fault removed the safe launcher position");
assert.equal(renderFault.window.document.getElementById(EMERGENCY_ID), null, "usable fail-open launcher did not retire emergency UI");

// 6. Persisted Clean Mode cannot strand the user: the independent control exits it on activation.
const cleanMode = createProductionDom({
  savedState: {
    theme: "default",
    position: "bl",
    cleanMode: true,
    setupWizard: { completed: true },
    updateBriefing: { enabled: false, seenVersion: "10.16.5" },
  },
});
evaluate(cleanMode.window, source, "issue768-clean-mode-runtime.js");
await waitFor(() => cleanMode.window.document.getElementById(CONTROL_ID), "Clean Mode primary launcher node");
assert.equal(cleanMode.window.document.documentElement.getAttribute("data-mcms-clean"), "true");
const cleanRecovery = await waitFor(() => cleanMode.window.document.getElementById(EMERGENCY_ID), "Clean Mode emergency launcher");
cleanRecovery.click();
await waitFor(
  () => cleanMode.window.document.documentElement.getAttribute("data-mcms-clean") === "false" && !cleanMode.window.document.getElementById(EMERGENCY_ID),
  "Clean Mode emergency restoration",
);
assert.equal(cleanMode.window[RUNTIME_KEY]?.recoverUi?.(), true, "runtime recovery did not remain functional after Clean Mode restoration");

destroyScenario(incomplete, "Issue #768 incomplete-runtime scenario complete");
destroyScenario(healthy, "Issue #768 healthy-runtime scenario complete");
destroyScenario(interrupted, "Issue #768 interrupted-runtime scenario complete");
destroyScenario(claimedInterruption, "Issue #768 post-claim interruption scenario complete");
destroyScenario(renderFault, "Issue #768 render-fault scenario complete");
destroyScenario(cleanMode, "Issue #768 Clean Mode scenario complete");
console.log("Issue #768 UI fail-open runtime passed: production map ownership, interrupted evaluation, same-version health, render faults and Clean Mode all retain a usable Toolkit recovery path.");
