#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const MAP_HTML = '<div id="map_outer"><div id="map" class="leaflet-container"><div class="leaflet-pane"></div></div></div>';
const MISSION_HTML = `
  <main id="mission-form" data-mission-id="638">
    <h1>Standalone mission</h1>
    <button id="alert_button">Dispatch</button>
    <table id="vehicle-list"><tbody><tr><td><input name="vehicle_ids[]" value="12"></td></tr></tbody></table>
    <div class="leaflet-container" data-leaflet-map="mission"></div>
  </main>`;

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

const helperSource = [
  "decodedPathname",
  "toolkitTopLevelDocument",
  "toolkitDocumentPathname",
  "toolkitCommandShellRouteEligible",
  "toolkitPrimaryMapElement",
  "toolkitControlHost",
  "toolkitCommandShellContextActive",
  "teardownToolkitCommandShell",
  "ensureUi",
  "reconcileToolkitCommandShellRoute",
  "queueToolkitCommandShellRouteReconcile",
  "installToolkitCommandShellNavigationHooks",
  "executeInputCommand",
  "handleKeyboard",
  "handleContextCommandRequest",
].map(extractFunction).join("\n\n");

function createHarness(pathname = "/", body = MAP_HTML) {
  const dom = new JSDOM(`<!doctype html><html><head></head><body>${body}</body></html>`, {
    url: `https://www.missionchief.co.uk${pathname}`,
    pretendToBeVisual: true,
  });
  const { window } = dom;
  const calls = { controls: 0, panels: 0, keyboardCommands: 0, invalidations: 0, listenerReleases: 0 };
  const SCRIPT = {
    version: "10.2.5",
    controlId: "mc-map-command-toolkit-control",
    panelId: "mc-map-command-toolkit-panel",
    toastId: "mc-map-command-toolkit-toast",
    payoutFlashId: "mc-map-command-toolkit-payout-flash",
    vehicleStatusId: "mc-map-command-toolkit-vehicle-status",
    pressureBoardId: "mc-map-command-toolkit-pressure-board",
    majorIncidentFeedId: "mc-map-command-toolkit-major-incident-feed",
    transportSweepHudId: "mc-map-command-toolkit-transport-sweep-hud",
    helpCenterId: "mc-map-command-toolkit-help-center",
    commandPaletteId: "mc-map-command-toolkit-command-palette",
    commandExperienceModalId: "mc-map-command-toolkit-command-experience",
    mapMeasureHudId: "mc-map-command-toolkit-map-measure",
    contextMenuId: "mc-map-command-toolkit-context-menu",
    quickWheelId: "mc-map-command-toolkit-quick-wheel",
    fullscreenExitId: "mc-map-command-toolkit-fullscreen-exit",
    vehicleFollowId: "mc-map-command-toolkit-vehicle-follow",
    cleanExitId: "mcms-clean-exit",
  };
  const sandbox = {
    console,
    window,
    pageWindow: window,
    document: window.document,
    location: window.location,
    Element: window.Element,
    HTMLElement: window.HTMLElement,
    Array,
    Boolean,
    String,
    queueMicrotask,
    SCRIPT,
    runtime: { destroyed: false, hookRestorers: [] },
    state: {
      commandBarOpen: true,
      fullscreenMap: false,
      economyMode: false,
      safeMode: { enabled: false },
      majorIncidentFeed: { enabled: false },
      autoHideDock: { enabled: false },
      shortcuts: true,
      inputStudio: { hotkeys: { menu: "M" } },
    },
    operationalStartupComplete: true,
    settingsPanelActivated: false,
    fullscreenMapTarget: null,
    autoHideDockRevealed: false,
    dragState: null,
    contextCommandTarget: null,
    commandPaletteEntries: [],
    commandPaletteResults: [],
    commandPaletteSelectedIndex: 0,
    commandPaletteReturnFocus: null,
    quickWheelReturnFocus: null,
    quickWheelRestoreDragging: false,
    toolkitCommandShellRouteReconcileQueued: false,
    mapMeasureRuntime: { active: false, map: null },
    getLargestLeafletMap: () => window.document.querySelector("#map, .leaflet-container"),
    invalidateMapElementCache: () => { calls.invalidations += 1; },
    createControl: map => {
      let control = window.document.getElementById(SCRIPT.controlId);
      if (control) return control;
      calls.controls += 1;
      control = window.document.createElement("div");
      control.id = SCRIPT.controlId;
      control.dataset.mcmsLauncherReady = "true";
      map.appendChild(control);
      return control;
    },
    createPanel: () => {
      calls.panels += 1;
      const panel = window.document.createElement("div");
      panel.id = SCRIPT.panelId;
      window.document.body.appendChild(panel);
      return panel;
    },
    ensureVersionStatusButton: () => undefined,
    findLeafletMapInstance: () => null,
    applyLeafletEconomyPolicy: () => undefined,
    scheduleEconomyLayerSync: () => undefined,
    scheduleMajorIncidentFeedRender: () => undefined,
    removeMajorIncidentFeed: () => undefined,
    applyMapFullscreenState: () => undefined,
    maybeShowSetupWizard: () => false,
    maybeShowUpdateBriefing: () => undefined,
    positionPayoutFlashOverlay: () => undefined,
    toolkitApplyCommandBarState: () => undefined,
    disposeVersionStatus: () => undefined,
    stopMapMeasure: () => undefined,
    clearIncidentCardRuntime: () => undefined,
    runtimeUnlistenTarget: () => { calls.listenerReleases += 1; return 0; },
    runtimePruneDisconnectedListeners: () => 0,
    ensureToolkitEmergencyLauncher: () => undefined,
    removeToolkitEmergencyLauncher: () => undefined,
    toolkitElementById: id => window.document.getElementById(id),
    toolkitPrimaryControlUsable: control => control?.dataset?.mcmsLauncherReady === "true",
    retireToolkitEmergencyLauncher: () => undefined,
    runBootIntegration: (_label, callback) => callback(),
    INPUT_COMMAND_META: { menu: { action: "menu" } },
    keyboardBindingFromEvent: () => "M",
    isTypingTarget: () => false,
  };
  vm.createContext(sandbox);
  vm.runInContext(`${helperSource}\nthis.probe = {
    routeEligible: toolkitCommandShellRouteEligible,
    primaryMap: toolkitPrimaryMapElement,
    controlHost: toolkitControlHost,
    active: toolkitCommandShellContextActive,
    teardown: teardownToolkitCommandShell,
    ensure: ensureUi,
    reconcile: reconcileToolkitCommandShellRoute,
    installNavigation: installToolkitCommandShellNavigationHooks,
    keyboard: handleKeyboard,
    context: handleContextCommandRequest,
  };`, sandbox, { filename: "issue638-command-shell-route.js" });
  return { dom, window, sandbox, calls, probe: sandbox.probe, SCRIPT };
}

async function flush() {
  await Promise.resolve();
  await new Promise(resolve => setTimeout(resolve, 0));
}

// 1. Canonical map page mounts normally and repeated reconciliation stays idempotent.
const canonical = createHarness("/", MAP_HTML);
assert.equal(canonical.probe.ensure(), true, "canonical map did not mount");
assert.equal(canonical.calls.controls, 1);
for (let index = 0; index < 6; index += 1) assert.equal(canonical.probe.ensure(), true);
assert.equal(canonical.calls.controls, 1, "repeated reconciliation duplicated the launcher");
assert.equal(canonical.window.document.querySelectorAll(`#${canonical.SCRIPT.controlId}`).length, 1);

// 2-3. Direct standalone missions remain ineligible even with dispatch, vehicles and a Leaflet map.
const standalone = createHarness("/missions/638?fullscreen=true", MISSION_HTML);
assert.equal(standalone.probe.routeEligible(), false);
assert.equal(standalone.probe.ensure(), true, "known ineligible route should settle without mounting");
assert.equal(standalone.calls.controls, 0);
assert.equal(standalone.window.document.getElementById(standalone.SCRIPT.controlId), null);

// 4. A mission lightbox map cannot take ownership away from the canonical map.
const lightbox = canonical.window.document.createElement("div");
lightbox.className = "modal mission-window";
lightbox.innerHTML = '<div class="leaflet-container" data-leaflet-map="main"></div>';
canonical.window.document.body.prepend(lightbox);
assert.equal(canonical.probe.primaryMap(lightbox.querySelector(".leaflet-container")), canonical.window.document.getElementById("map"));
const frame = canonical.window.document.createElement("iframe");
canonical.window.document.body.appendChild(frame);
assert.equal(canonical.probe.routeEligible(frame.contentDocument), false, "child mission document became launcher owner");

// 5-6. History navigation tears down every global surface, preserves page enhancements, and remounts once.
const supported = canonical.window.document.createElement("div");
supported.id = "supported-page-enhancement";
canonical.window.document.body.appendChild(supported);
for (const id of [canonical.SCRIPT.panelId, canonical.SCRIPT.pressureBoardId, canonical.SCRIPT.commandPaletteId]) {
  const node = canonical.window.document.createElement("div");
  node.id = id;
  canonical.window.document.body.appendChild(node);
}
canonical.probe.installNavigation();
const wrappedPushState = canonical.window.history.pushState;
canonical.probe.installNavigation();
assert.equal(canonical.window.history.pushState, wrappedPushState, "navigation hooks duplicated");
canonical.window.history.pushState({}, "", "/missions/638");
await flush();
for (const id of [canonical.SCRIPT.controlId, canonical.SCRIPT.panelId, canonical.SCRIPT.pressureBoardId, canonical.SCRIPT.commandPaletteId]) {
  assert.equal(canonical.window.document.getElementById(id), null, `${id} survived map departure`);
}
assert.ok(canonical.window.document.getElementById("supported-page-enhancement"), "page-specific enhancement was removed");
assert.ok(canonical.calls.listenerReleases >= 4, "command-shell teardown did not release removed-node listeners");
canonical.window.history.pushState({}, "", "/");
await flush();
assert.equal(canonical.calls.controls, 2, "returning to map did not remount exactly once");
assert.equal(canonical.window.document.querySelectorAll(`#${canonical.SCRIPT.controlId}`).length, 1);

// 7. Persisted-open state cannot force launcher or menu nodes onto an ineligible route.
standalone.sandbox.state.commandBarOpen = true;
for (const id of [standalone.SCRIPT.controlId, standalone.SCRIPT.panelId]) {
  const stale = standalone.window.document.createElement("div");
  stale.id = id;
  stale.className = "mcms-open";
  standalone.window.document.body.appendChild(stale);
}
standalone.probe.ensure();
assert.equal(standalone.window.document.getElementById(standalone.SCRIPT.controlId), null);
assert.equal(standalone.window.document.getElementById(standalone.SCRIPT.panelId), null);
assert.equal(standalone.sandbox.state.commandBarOpen, true, "saved command-bar preference was mutated");

// 8. Keyboard and context-menu ownership fail closed without consuming native events.
let keyboardPrevented = false;
standalone.probe.keyboard({ key: "M", preventDefault() { keyboardPrevented = true; } });
assert.equal(keyboardPrevented, false, "non-map keyboard shortcut was consumed");
let contextPrevented = false;
const contextResult = standalone.probe.context({
  defaultPrevented: false,
  target: standalone.window.document.getElementById("alert_button"),
  clientX: 1,
  clientY: 1,
  preventDefault() { contextPrevented = true; },
  stopPropagation() {},
});
assert.equal(contextResult, false);
assert.equal(contextPrevented, false, "non-map context menu was consumed");

// 9. Credits, alliance, building and vehicle pages never own the global command shell.
for (const path of ["/credits", "/verband/mitglieder/123", "/buildings/55", "/vehicles/77"]) {
  const scenario = createHarness(path, '<nav>Shared MissionChief navigation</nav><div id="map" class="leaflet-container"></div>');
  assert.equal(scenario.probe.routeEligible(), false, `${path} was route-eligible`);
  assert.equal(scenario.probe.ensure(), true);
  assert.equal(scenario.calls.controls, 0, `${path} mounted the launcher`);
  scenario.dom.window.close();
}

// 10. Teardown preserves explicitly supported page-level enhancement DOM.
assert.ok(canonical.window.document.getElementById("supported-page-enhancement"));

// 11. A generic #map ID without the canonical shell or Leaflet evidence is insufficient.
const genericMap = createHarness("/", '<main><div id="map"></div></main>');
assert.equal(genericMap.probe.active(), false);
assert.equal(genericMap.probe.ensure(), false);
assert.equal(genericMap.calls.controls, 0);

// 12. Desktop, Tablet/iPad and iOS/mobile fixtures use the same fail-closed route gate.
for (const mode of ["desktop", "tablet", "mobile", "ios"]) {
  standalone.window.document.documentElement.setAttribute("data-mcms-device-mode", mode);
  assert.equal(standalone.probe.routeEligible(), false, `${mode} standalone mission became eligible`);
  standalone.probe.ensure();
  assert.equal(standalone.calls.controls, 0);
}

for (const scenario of [canonical, standalone, genericMap]) scenario.dom.window.close();
console.log("Issue #638 route runtime passed: canonical ownership, standalone denial, mission-window isolation, deterministic teardown/remount, persisted-state and shortcut guards, non-map routes, supported enhancements, idempotence and responsive fixtures.");
