#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import { webcrypto } from "node:crypto";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const frameHtml = fs.readFileSync("devlab/frame.html", "utf8").replace(/<script src="\/devlab\/frame\.js"><\/script>/u, "");
const frameRuntime = fs.readFileSync("devlab/frame.js", "utf8");

async function waitFor(predicate, message, timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = predicate();
    if (value) return value;
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  throw new Error(message);
}

async function boot(device = "desktop") {
  const query = new URLSearchParams({ device, tab: "map", theme: "mapCommand" });
  const dom = new JSDOM(frameHtml, {
    url: `http://127.0.0.1:4173/devlab/frame.html?${query}`,
    pretendToBeVisual: true,
    runScripts: "dangerously",
  });
  const { window } = dom;
  window.__MCMS_DEV_LAB_TEST__ = true;
  window.Response = globalThis.Response;
  window.Request = globalThis.Request;
  window.Headers = globalThis.Headers;
  window.TextEncoder = globalThis.TextEncoder;
  window.TextDecoder = globalThis.TextDecoder;
  Object.defineProperty(window, "crypto", { configurable: true, value: webcrypto });
  window.eval(frameRuntime);
  const panel = await window.__MCMS_DEV_LAB_API__.boot({ sourceText: source });
  await waitFor(() => window.document.querySelector(".mcms-fast-map-btn"), `${device}: Fast Map control did not mount`);
  return { dom, window, panel };
}

function diagnostics(window) {
  assert.equal(typeof window.__MCMS_FAST_MAP_DIAGNOSTICS__, "function", "Fast Map diagnostics hook is unavailable");
  return window.__MCMS_FAST_MAP_DIAGNOSTICS__();
}

function assertNativeRestored(window, originalMapElement, nativeMap, device) {
  const current = window.document.getElementById("map");
  assert.equal(current, originalMapElement, `${device}: restoration did not return the exact original map node`);
  assert.equal(originalMapElement.isConnected, true, `${device}: original map node is detached after restoration`);
  assert.equal(nativeMap.getContainer(), originalMapElement, `${device}: native Leaflet object lost its original container`);
  assert.equal(window.document.querySelector(".mcms-fast-map"), null, `${device}: Fast Map shell leaked after restoration`);
  assert.ok(nativeMap._handlers.every(handler => handler.enabled()), `${device}: native Leaflet handlers were not restored`);
  assert.ok(originalMapElement.contains(window.document.getElementById("mc-map-command-toolkit-control")), `${device}: Toolkit controls did not return to the native map`);
}

async function exerciseDevice(device, deep = false) {
  const { dom, window, panel } = await boot(device);
  window.__MCMS_DEV_LAB_API__.stopHealthMonitoring();
  const nativeMap = window.map;
  const originalMapElement = window.document.getElementById("map");
  const vehicleMarker = window.vehicle_markers[0];
  const writesBeforeActivation = vehicleMarker._renderWrites;
  const fastButton = window.document.querySelector(".mcms-fast-map-btn");

  assert.equal(fastButton.getAttribute("aria-pressed"), "false", `${device}: Fast Map must default off`);
  assert.equal(diagnostics(window).engineLoaded, true, `${device}: deterministic Dev Lab adapter was not selected`);
  fastButton.click();
  const active = await waitFor(() => {
    const report = diagnostics(window);
    return report.active ? report : null;
  }, `${device}: Fast Map did not activate`);

  assert.equal(originalMapElement.isConnected, false, `${device}: native Leaflet container remained connected underneath Fast Map`);
  assert.equal(originalMapElement.id, "mc-map-command-toolkit-native-map-suspended", `${device}: suspended native map was not positively identified`);
  assert.notEqual(window.document.getElementById("map"), originalMapElement, `${device}: replacement did not own the canonical map slot`);
  assert.equal(active.nativeRenderingSuspended, true, `${device}: native-render suspension diagnostic failed`);
  assert.equal(active.connectedLeafletPanes, 0, `${device}: connected Leaflet panes are still rendering underneath Fast Map`);
  assert.equal(active.connectedRenderers, 1, `${device}: Fast Map must mount exactly one renderer`);
  assert.equal(active.adapterRenderers, 1, `${device}: adapter reported more than one renderer`);
  assert.equal(active.baseMapReady, true, `${device}: Fast Map became active before its base map was ready`);
  assert.equal(JSON.stringify(active.featureCounts), JSON.stringify({ buildings: 4, allianceMissions: 1, personalMissions: 1, vehicles: 3 }), `${device}: live MissionChief marker bridge lost data`);
  assert.equal(active.totalFeatures, 9, `${device}: unexpected Fast Map point total`);
  assert.ok(nativeMap._handlers.every(handler => !handler.enabled()), `${device}: native Leaflet interaction handlers are still running`);
  assert.ok(nativeMap.stopCalls >= 1, `${device}: native Leaflet animations were not stopped`);
  assert.ok(window.document.getElementById("map").contains(window.document.getElementById("mc-map-command-toolkit-control")), `${device}: Fast Map lost its own off switch`);
  assert.equal(window.document.querySelector(".mcms-fast-map-btn").getAttribute("aria-pressed"), "true", `${device}: active control state is inaccessible`);
  assert.ok(window.document.querySelector("#mc-map-command-toolkit-fast-map-hud [data-fast-map-health]").textContent.includes("Leaflet parked"), `${device}: suspension state is not visible to the player`);
  const attributionLinks = Array.from(window.document.querySelectorAll(".mcms-fast-map-attribution a"));
  assert.deepEqual(attributionLinks.map(link => link.textContent.trim()), ["© OpenStreetMap contributors", "OpenFreeMap"], `${device}: relocated base-map attribution is incomplete`);

  vehicleMarker.setLatLng({ lat: 55.99, lng: -3.04 });
  assert.equal(vehicleMarker._renderWrites, writesBeforeActivation, `${device}: guarded Leaflet marker still wrote to detached DOM`);
  await waitFor(() => {
    const adapter = window.__MCMS_FAST_MAP_TEST_ENGINE_STATE__.adapters.at(-1);
    const feature = adapter?.sourceFeatures("mcms-fast-vehicles").find(item => item.properties?.recordId === "701");
    return feature?.geometry?.coordinates?.[0] === -3.04;
  }, `${device}: live vehicle movement did not reach the Fast Map source`);

  const adapter = window.__MCMS_FAST_MAP_TEST_ENGINE_STATE__.adapters.at(-1);
  adapter.triggerFeature("mission:1001");
  assert.equal(window.__MCMS_LAST_LIGHTBOX__, "/missions/1001", `${device}: Fast Map mission click did not use MissionChief's native mission route`);

  if (deep) {
    const buildingsButton = window.document.querySelector(`#mc-map-command-toolkit-control [data-toggle="buildings"]`);
    buildingsButton.click();
    const fireFilter = await waitFor(
      () => window.document.querySelector(".mcms-native-building-filter-fire:not(:disabled)"),
      `${device}: native Fire station shortcut did not open while Fast Map was active`,
    );
    fireFilter.click();
    await waitFor(
      () => adapter.sourceFeatures("mcms-fast-buildings").length === 2,
      `${device}: hidden native Fire stations remained in the Fast Map source`,
    );
    assert.equal(originalMapElement.isConnected, false, `${device}: native filter use reconnected Leaflet underneath Fast Map`);
    assert.equal(window.document.querySelector("#mc-map-command-toolkit-building-quick-filter").hidden, false, `${device}: station popup closed during Fast Map multi-selection`);
    const restoredFireFilter = window.document.querySelector(".mcms-native-building-filter-fire:not(:disabled)");
    restoredFireFilter.click();
    await waitFor(
      () => adapter.sourceFeatures("mcms-fast-buildings").length === 4,
      `${device}: restored native Fire stations did not return to the Fast Map source`,
    );

    const liveMission = window.L.marker({ lat: 55.86, lng: -3.08 });
    Object.assign(liveMission, { mission_id: 1003, id: 1003, user_id: 1988, caption: "Live Fast Map mission" });
    liveMission.options = { ...liveMission.options, mission_id: 1003, user_id: 1988 };
    nativeMap.addLayer(liveMission);
    window.mission_markers.push(liveMission);
    window.missions.push({ id: 1003, mission_id: 1003, user_id: 1988, caption: "Live Fast Map mission" });
    await waitFor(
      () => adapter.sourceFeatures("mcms-fast-personal-missions").some(feature => feature.properties?.recordId === "1003"),
      `${device}: live mission added while native events were detached did not reach Fast Map`,
    );
    assert.equal(liveMission._renderWrites, 0, `${device}: newly added native mission rendered inside the parked Leaflet map`);
    nativeMap.removeLayer(liveMission);
    window.mission_markers.splice(window.mission_markers.indexOf(liveMission), 1);
    window.missions.splice(window.missions.findIndex(record => Number(record.id) === 1003), 1);
    await waitFor(
      () => !adapter.sourceFeatures("mcms-fast-personal-missions").some(feature => feature.properties?.recordId === "1003"),
      `${device}: removed live mission remained in Fast Map`,
    );
  }

  if (deep) {
    const health = await window.__MCMS_DEV_LAB_API__.buildHealthReport(panel);
    assert.equal(health.noHorizontalOverflow, true, `${device}: Fast Map caused a text or viewport overflow`);
    assert.equal(health.errors.length, 0, `${device}: Fast Map generated Dev Lab runtime errors`);
  }

  window.document.querySelector(".mcms-fast-map-btn").click();
  await waitFor(() => diagnostics(window).phase === "off", `${device}: Fast Map did not switch off`);
  assertNativeRestored(window, originalMapElement, nativeMap, device);
  assert.ok(vehicleMarker._renderWrites > writesBeforeActivation, `${device}: dirty native markers were not redrawn after restoration`);

  if (deep) {
    const engineState = window.__MCMS_FAST_MAP_TEST_ENGINE_STATE__;
    engineState.failNext = true;
    window.document.querySelector(".mcms-fast-map-btn").click();
    await waitFor(() => diagnostics(window).phase === "error", "forced startup failure did not enter the safe error state");
    assertNativeRestored(window, originalMapElement, nativeMap, device);
    assert.match(diagnostics(window).error, /forced Fast Map startup failure/iu, "startup failure reason was not retained");
    assert.equal(window.document.querySelector(".mcms-fast-map-btn").dataset.mcmsPhase, "error", "error state is not exposed on the toggle");

    engineState.readyDelayMs = 250;
    window.document.querySelector(".mcms-fast-map-btn").click();
    await waitFor(() => diagnostics(window).phase === "starting", "delayed Fast Map did not reach cancellable startup");
    assert.equal(originalMapElement.isConnected, false, "native map was not suspended during delayed startup");
    window.document.querySelector(".mcms-fast-map-btn").click();
    await waitFor(() => diagnostics(window).phase === "off", "startup cancellation did not restore the off state");
    assertNativeRestored(window, originalMapElement, nativeMap, device);
    await new Promise(resolve => setTimeout(resolve, 320));
    assert.equal(diagnostics(window).phase, "off", "cancelled asynchronous startup reactivated Fast Map");
    assertNativeRestored(window, originalMapElement, nativeMap, device);
  }

  window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.destroy?.("Fast Map runtime test complete");
  window.__MCMS_DEV_LAB_API__.stopHealthMonitoring();
  dom.window.close();
}

async function exerciseScale() {
  const { dom, window } = await boot("desktop");
  window.__MCMS_DEV_LAB_API__.stopHealthMonitoring();
  const nativeMap = window.map;
  const addedMarkers = [];
  const addedRecords = [];
  for (let index = 0; index < 5000; index += 1) {
    const id = 10000 + index;
    const record = {
      id,
      vehicle_id: id,
      user_id: 1988,
      caption: `Scale vehicle ${index + 1}`,
      vehicle_type_caption: "Performance fixture",
      fms_real: 2 + (index % 4),
    };
    const marker = window.L.marker({
      lat: 55.70 + ((index % 100) * 0.004),
      lng: -3.50 + (Math.floor(index / 100) * 0.004),
    });
    Object.assign(marker, record);
    marker.options = { ...marker.options, vehicle_id: id, user_id: 1988 };
    nativeMap.addLayer(marker);
    addedRecords.push(record);
    addedMarkers.push(marker);
  }
  window.vehicles.push(...addedRecords);
  window.vehicle_markers.push(...addedMarkers);

  window.document.querySelector(".mcms-fast-map-btn").click();
  const active = await waitFor(() => {
    const report = diagnostics(window);
    return report.active && report.featureCounts.vehicles === 5003 ? report : null;
  }, "scale: Fast Map did not bridge all 5,003 vehicle points", 15000);
  assert.equal(active.connectedLeafletPanes, 0, "scale: Leaflet panes remained connected beneath the large Fast Map source");
  const adapter = window.__MCMS_FAST_MAP_TEST_ENGINE_STATE__.adapters.at(-1);
  adapter.updateCalls.length = 0;
  const writesBefore = addedMarkers.slice(0, 1000).map(marker => marker._renderWrites);
  addedMarkers.slice(0, 1000).forEach((marker, index) => {
    marker.setLatLng({ lat: 55.72 + ((index % 100) * 0.004), lng: -3.48 + (Math.floor(index / 100) * 0.004) });
  });
  addedMarkers.slice(0, 1000).forEach((marker, index) => {
    assert.equal(marker._renderWrites, writesBefore[index], `scale: detached Leaflet wrote marker ${index} during the movement storm`);
  });
  const vehicleDiff = await waitFor(
    () => adapter.updateCalls.find(call => call.sourceId === "mcms-fast-vehicles" && call.update === 1000),
    "scale: 1,000 vehicle movements did not become one incremental source update",
    10000,
  );
  assert.deepEqual(
    { mode: vehicleDiff.mode, remove: vehicleDiff.remove, add: vehicleDiff.add, update: vehicleDiff.update },
    { mode: "diff", remove: 0, add: 0, update: 1000 },
    "scale: movement storm rebuilt the complete vehicle source instead of applying an ID-based diff",
  );
  assert.ok(diagnostics(window).syncMs < 1000, `scale: deterministic 5,009-point bridge exceeded the 1,000 ms safety ceiling (${diagnostics(window).syncMs.toFixed(1)} ms)`);

  window.document.querySelector(".mcms-fast-map-btn").click();
  await waitFor(() => diagnostics(window).phase === "off", "scale: native map did not restore after the large-source test");
  await waitFor(() => addedMarkers[999]._renderWrites > writesBefore[999], "scale: deferred Leaflet marker updates were not restored in batches");
  window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.destroy?.("Fast Map scale runtime test complete");
  window.__MCMS_DEV_LAB_API__.stopHealthMonitoring();
  dom.window.close();
}

await exerciseDevice("desktop", true);
await exerciseDevice("tablet");
await exerciseDevice("ios");
await exerciseScale();
console.log("Fast Map suspended native Leaflet rendering, bridged 5,009 live points with an incremental 1,000-vehicle update, survived failure/cancellation, restored the exact map, and fit Desktop, Tablet and iOS.");
