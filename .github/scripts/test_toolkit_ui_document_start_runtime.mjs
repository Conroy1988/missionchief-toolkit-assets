#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import { webcrypto } from "node:crypto";
import { JSDOM, VirtualConsole } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const RUNTIME_KEY = "__MC_MAP_COMMAND_TOOLKIT_RUNTIME__";
const BOOTSTRAP_KEY = "__MCMS_FIRST_BYTE_BOOTSTRAP__";
const CONTROL_ID = "mc-map-command-toolkit-control";
const PANEL_ID = "mc-map-command-toolkit-panel";
const CLEAN_EXIT_ID = "mcms-clean-exit";
const RECOVERY_ID = "mcms-first-byte-recovery";
const RECOVERY_DETAILS_ID = "mcms-first-byte-recovery-details";
const STYLE_ID = "mc-map-command-toolkit-style-v4146";
const STORAGE_KEY = "mc_map_command_toolkit_state_v150";

function waitFor(predicate, label, timeoutMs = 12000) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const poll = () => {
      let value = null;
      try { value = predicate(); } catch (error) {}
      if (value) { resolve(value); return; }
      if (Date.now() - started >= timeoutMs) {
        reject(new Error(`Timed out waiting for ${label}`));
        return;
      }
      setTimeout(poll, 20);
    };
    poll();
  });
}

function mapDimensions(device) {
  if (device === "ios") return { width: 390, height: 844, coarse: true };
  if (device === "tablet") return { width: 1024, height: 768, coarse: true };
  return { width: 1440, height: 900, coarse: false };
}

function createMapStub(mapElement) {
  const bounds = {
    contains: () => true,
    getNorth: () => 56.2,
    getSouth: () => 55.7,
    getEast: () => -2.8,
    getWest: () => -3.6,
  };
  return {
    _leaflet_id: Number(mapElement.dataset.mapGeneration || 1),
    _layers: {},
    getContainer: () => mapElement,
    getBounds: () => bounds,
    getCenter: () => ({ lat: 55.9533, lng: -3.1883 }),
    getZoom: () => 12,
    eachLayer() {},
    on() { return this; },
    off() { return this; },
    hasLayer() { return false; },
    invalidateSize() { return this; },
    latLngToContainerPoint: () => ({ x: 100, y: 100 }),
    containerPointToLatLng: () => ({ lat: 55.9533, lng: -3.1883 }),
  };
}

function installLeaflet(window, map) {
  let id = 20;
  const layer = extra => ({
    _leaflet_id: id++,
    options: {},
    addTo() { return this; },
    remove() { return this; },
    bindTooltip() { return this; },
    setIcon() { return this; },
    setLatLng() { return this; },
    setStyle() { return this; },
    getLatLng: () => ({ lat: 55.9533, lng: -3.1883 }),
    ...extra,
  });
  window.L = {
    map: () => map,
    stamp(value) { if (!value._leaflet_id) value._leaflet_id = id++; return value._leaflet_id; },
    layerGroup: () => layer({ clearLayers() { return this; }, addLayer() { return this; }, eachLayer() {} }),
    featureGroup: () => layer({ clearLayers() { return this; }, addLayer() { return this; }, eachLayer() {} }),
    marker: latlng => layer({ getLatLng: () => latlng }),
    circle: latlng => layer({ getLatLng: () => latlng }),
    circleMarker: latlng => layer({ getLatLng: () => latlng }),
    polyline: () => layer({ getBounds: () => map.getBounds() }),
    divIcon: options => ({ options }),
    latLng: (lat, lng) => ({ lat: Number(lat), lng: Number(lng) }),
    latLngBounds: () => map.getBounds(),
    point: (x, y) => ({ x, y }),
  };
}

function installMap(window, device, generation = 1) {
  const { document } = window;
  const dimensions = mapDimensions(device);
  let outer = document.getElementById("map_outer");
  if (!outer) {
    outer = document.createElement("div");
    outer.id = "map_outer";
    document.body.appendChild(outer);
  }
  const mapElement = document.createElement("div");
  mapElement.id = "map";
  mapElement.className = "leaflet-container";
  mapElement.dataset.mapGeneration = String(generation);
  mapElement.innerHTML = '<div class="leaflet-map-pane"></div>';
  outer.replaceChildren(mapElement);
  for (const [property, value] of [
    ["offsetWidth", dimensions.width],
    ["clientWidth", dimensions.width],
    ["offsetHeight", dimensions.height - 46],
    ["clientHeight", dimensions.height - 46],
  ]) Object.defineProperty(mapElement, property, { configurable: true, value });
  const map = createMapStub(mapElement);
  mapElement._leaflet_map = map;
  mapElement._leaflet_id = map._leaflet_id;
  window.map = map;
  window.mapkit = map;
  installLeaflet(window, map);
  return mapElement;
}

async function scenario(device, { cleanMode = false, fatalApplication = false, rootlessStart = false } = {}) {
  const dimensions = mapDimensions(device);
  const virtualConsole = new VirtualConsole();
  const consoleErrors = [];
  virtualConsole.on("jsdomError", error => {
    if (!/Not implemented: (?:HTMLCanvasElement|navigation)/u.test(String(error?.message || error))) {
      consoleErrors.push(String(error?.stack || error));
    }
  });
  const dom = new JSDOM("<!doctype html><html><head></head><body></body></html>", {
    url: "https://www.missionchief.co.uk/",
    pretendToBeVisual: true,
    runScripts: "dangerously",
    virtualConsole,
  });
  const { window } = dom;
  const { document } = window;
  const runtimeErrors = [];

  Object.defineProperty(document, "readyState", { configurable: true, value: "loading" });
  Object.defineProperty(document, "hidden", { configurable: true, value: false });
  Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
  Object.defineProperty(window, "innerWidth", { configurable: true, value: dimensions.width });
  Object.defineProperty(window, "innerHeight", { configurable: true, value: dimensions.height });
  Object.defineProperty(window, "crypto", { configurable: true, value: webcrypto });
  Object.defineProperty(window.navigator, "maxTouchPoints", { configurable: true, value: dimensions.coarse ? 5 : 0 });
  window.unsafeWindow = window;
  window.Response = globalThis.Response;
  window.Request = globalThis.Request;
  window.Headers = globalThis.Headers;
  window.TextEncoder = globalThis.TextEncoder;
  window.TextDecoder = globalThis.TextDecoder;
  window.AbortController = globalThis.AbortController;
  window.fetch = async () => new window.Response("{}", { status: 404, headers: { "content-type": "application/json" } });
  window.matchMedia = query => ({
    matches: /coarse/iu.test(query) ? dimensions.coarse : false,
    addEventListener() {},
    removeEventListener() {},
    addListener() {},
    removeListener() {},
  });
  window.requestIdleCallback = callback => window.setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 50 }), 0);
  window.cancelIdleCallback = id => window.clearTimeout(id);
  window.ResizeObserver = class { observe() {} disconnect() {} };
  window.IntersectionObserver = class { observe() {} disconnect() {} };
  window.CSS ||= {};
  window.CSS.escape ||= value => String(value).replace(/[^a-zA-Z0-9_-]/gu, "_");
  window.open = () => null;
  window.confirm = () => true;
  window.alert = () => undefined;
  window.GM_getValue = (_key, fallback) => fallback;
  window.GM_setValue = () => undefined;
  window.GM_deleteValue = () => undefined;
  window.GM_xmlhttpRequest = () => ({ abort() {} });
  window.HTMLElement.prototype.getBoundingClientRect = function () {
    if (this.id === "map" || this.id === "map_outer") {
      return { x: 0, y: 46, left: 0, top: 46, right: dimensions.width, bottom: dimensions.height, width: dimensions.width, height: dimensions.height - 46 };
    }
    if (
      document.documentElement.getAttribute("data-mcms-clean") === "true"
      && (this.id === CONTROL_ID || this.closest?.(`#${CONTROL_ID}`))
    ) {
      return { x: 0, y: 0, left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
    }
    return { x: 8, y: 54, left: 8, top: 54, right: 208, bottom: 98, width: 200, height: 44 };
  };
  window.addEventListener("error", event => runtimeErrors.push(String(event.error?.stack || event.message || event.error)));
  window.addEventListener("unhandledrejection", event => runtimeErrors.push(String(event.reason?.stack || event.reason)));
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify({
    setupWizard: { completed: true, schema: 1 },
    updateBriefing: { enabled: false, seenVersion: "10.16.7", seenFeatures: [] },
    tabletMode: device === "tablet" ? "on" : "off",
    mobileMode: device === "ios" ? "on" : "off",
    cleanMode,
  }));

  if (rootlessStart) {
    document.documentElement.remove();
    assert.equal(document.documentElement, null, `${device}: rootless fixture retained an HTML root`);
    assert.equal(document.body, null, `${device}: rootless fixture retained a body`);
  }

  // Evaluate against the sparse document first: this is the real @run-at document-start order.
  const evaluatedSource = fatalApplication
    ? source.replace(
      "    MCMS_FIRST_BYTE.mark('application-entered');",
      "    MCMS_FIRST_BYTE.mark('application-entered');\n    throw new Error('intentional application bootstrap failure');",
    )
    : source;
  if (fatalApplication) assert.notEqual(evaluatedSource, source, `${device}: fatal source transform failed`);
  window.eval(`${evaluatedSource}\n//# sourceURL=toolkit-document-start-${device}.user.js`);
  assert.equal(document.getElementById(CONTROL_ID), null, `${device}: launcher mounted before the map existed`);

  if (rootlessStart) {
    const html = document.createElement("html");
    html.append(document.createElement("head"), document.createElement("body"));
    document.appendChild(html);
    assert.ok(document.documentElement && document.body, `${device}: HTML root restoration failed`);
  }

  document.body.innerHTML = '<nav id="navbar-main"></nav><aside id="mission_list"></aside>';
  const initialMap = installMap(window, device, 1);
  Object.defineProperty(document, "readyState", { configurable: true, value: "interactive" });
  document.dispatchEvent(new window.Event("DOMContentLoaded"));

  if (fatalApplication) {
    const recovery = await waitFor(
      () => document.getElementById(RECOVERY_ID),
      `${device} recovery control after fatal application bootstrap`,
    );
    assert.equal(window[RUNTIME_KEY], undefined, `${device}: fatal application unexpectedly installed a runtime`);
    assert.equal(
      document.documentElement.dataset.mcmsFirstBytePhase,
      "application-failed",
      `${device}: fatal application phase was not published`,
    );
    assert.match(
      document.documentElement.dataset.mcmsFirstByteFailure || "",
      /intentional application bootstrap failure/u,
      `${device}: fatal application detail was not published`,
    );
    assert.notEqual(window.getComputedStyle(recovery).display, "none", `${device}: fatal recovery control is hidden`);
    recovery.click();
    const details = await waitFor(
      () => document.getElementById(RECOVERY_DETAILS_ID),
      `${device} recovery repair details after fatal application bootstrap`,
    );
    assert.equal(
      details.querySelector('a[href="https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/MissionChief_Map_Command_Toolkit.user.js"]')?.textContent,
      "Repair Toolkit",
      `${device}: verified repair route is missing`,
    );
    assert.equal(runtimeErrors.length, 0, `${device}: fatal path escaped its first-byte boundary: ${runtimeErrors.join(" | ")}`);
    assert.equal(consoleErrors.length, 0, `${device}: fatal path jsdom errors: ${consoleErrors.join(" | ")}`);
    window[BOOTSTRAP_KEY]?.dispose?.();
    dom.window.close();
    return;
  }

  const control = await waitFor(
    () => document.getElementById(CONTROL_ID),
    `${device} document-start launcher`,
  );
  assert.equal(control.parentElement, initialMap, `${device}: launcher did not mount into the canonical map`);
  assert.ok(document.getElementById(STYLE_ID), `${device}: main stylesheet is missing`);
  assert.equal(window[RUNTIME_KEY]?.version, "10.16.7", `${device}: wrong active runtime`);
  assert.equal(window[RUNTIME_KEY]?.destroyed, false, `${device}: runtime was destroyed during boot`);
  let panel = null;
  if (cleanMode) {
    const cleanExit = await waitFor(() => document.getElementById(CLEAN_EXIT_ID), `${device} clean-mode exit`);
    assert.notEqual(window.getComputedStyle(cleanExit).display, "none", `${device}: clean-mode exit is hidden`);

    // Simulate the live failure state: saved Clean Mode hides the launcher and its exit is missing.
    cleanExit.remove();
    window[BOOTSTRAP_KEY]?.check?.();
    const recovery = await waitFor(() => document.getElementById(RECOVERY_ID), `${device} clean-mode recovery control`);
    assert.notEqual(window.getComputedStyle(recovery).display, "none", `${device}: clean-mode recovery control is hidden`);
    recovery.click();
    await waitFor(
      () => document.documentElement.getAttribute("data-mcms-clean") === "false",
      `${device} clean-mode state restoration`,
    );
    assert.equal(document.documentElement.getAttribute("data-mcms-command-bar-open"), "true");
    assert.equal(document.documentElement.getAttribute("data-mcms-dock-auto-hide"), "false");
    panel = await waitFor(
      () => document.getElementById(PANEL_ID)?.classList.contains("mcms-open") && document.getElementById(PANEL_ID),
      `${device} recovered command panel`,
    );
  } else {
    assert.notEqual(window.getComputedStyle(control).display, "none", `${device}: launcher is hidden`);
    control.querySelector(".mcms-menu-btn")?.click();
    panel = await waitFor(() => document.getElementById(PANEL_ID), `${device} command panel`);
  }
  assert.ok(panel.classList.contains("mcms-open"), `${device}: command panel did not open`);

  // MissionChief can replace its map node after initial parsing. The launcher must self-heal.
  const replacementMap = installMap(window, device, 2);
  const recoveredControl = await waitFor(
    () => {
      const candidate = document.getElementById(CONTROL_ID);
      return candidate?.parentElement === replacementMap ? candidate : null;
    },
    `${device} launcher after native map replacement`,
  );
  assert.ok(recoveredControl.isConnected, `${device}: recovered launcher is detached`);
  assert.ok(document.getElementById(STYLE_ID), `${device}: stylesheet was lost during map replacement`);
  assert.equal(runtimeErrors.length, 0, `${device}: runtime errors: ${runtimeErrors.join(" | ")}`);
  assert.equal(consoleErrors.length, 0, `${device}: jsdom errors: ${consoleErrors.join(" | ")}`);

  window[BOOTSTRAP_KEY]?.dispose?.();
  window[RUNTIME_KEY]?.destroy?.(`${device} document-start test complete`);
  dom.window.close();
}

assert.match(source, /^\/\/ @version\s+10\.16\.7$/mu);
for (const device of ["desktop", "tablet", "ios"]) await scenario(device);
await scenario("desktop", { cleanMode: true });
await scenario("desktop", { fatalApplication: true });
await scenario("desktop", { rootlessStart: true });
console.log("Toolkit UI document-start runtime passed: Desktop, Tablet and iOS mount; null-root document-start and map replacement self-heal; persisted Clean Mode recovers; fatal application bootstrap retains a repair control.");
