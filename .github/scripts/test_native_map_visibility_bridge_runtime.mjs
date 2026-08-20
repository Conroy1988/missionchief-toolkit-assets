#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const pattern = new RegExp(`\\bfunction\\s+${name}\\s*\\(`, "u");
  const match = pattern.exec(source);
  assert.ok(match, `${name} is missing`);
  const start = match.index;
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
  assert.notEqual(brace, -1, `${name} body is missing`);
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

const descriptors = Object.freeze({
  myMissions: Object.freeze({ filterId: "user_missions", aliases: Object.freeze(["user_missions", "my_missions", "personal_missions"]), labels: Object.freeze(["My missions", "Personal missions"]), i18n: Object.freeze(["map_filters.user_missions"]) }),
  allianceMissions: Object.freeze({ filterId: "alliance_missions", aliases: Object.freeze(["alliance_missions", "shared_missions"]), labels: Object.freeze(["Alliance missions", "Shared by alliance"]), i18n: Object.freeze(["map_filters.alliance_missions"]) }),
  vehicles: Object.freeze({ filterId: "", aliases: Object.freeze(["vehicles", "vehicle_markers", "show_vehicle", "show_vehicles"]), labels: Object.freeze(["Vehicles", "Show vehicles", "Show vehicles on map"]), i18n: Object.freeze(["common.vehicles"]) }),
  buildings: Object.freeze({ filterId: "user_buildings", aliases: Object.freeze(["user_buildings", "my_buildings", "personal_buildings", "own_buildings"]), labels: Object.freeze(["My buildings", "Personal buildings", "Own buildings"]), i18n: Object.freeze(["map_filters.user_buildings"]) }),
});

function makeControl(value, label, checked) {
  const wrapper = { textContent: label };
  return {
    nodeType: 1,
    type: "checkbox",
    value,
    id: `map_filter_${value}`,
    name: "map_filter",
    checked,
    disabled: false,
    ownerDocument: null,
    matches(selector) { return selector.includes('input[type="checkbox"]'); },
    closest(selector) {
      if (selector.includes("#mcms-")) return null;
      if (selector.includes("label") || selector.includes("li")) return wrapper;
      return null;
    },
    getAttribute(name) {
      if (name === "data-filter-id") return value;
      if (name === "aria-disabled") return "false";
      return null;
    },
    hasAttribute() { return false; },
    click() { this.checked = !this.checked; },
    dispatchEvent() { return true; },
  };
}

const controls = [
  makeControl("user_missions", "My missions", true),
  makeControl("alliance_missions", "Shared by alliance", false),
  makeControl("show_vehicle", "Show vehicles on map", true),
  makeControl("user_buildings", "My buildings", true),
  makeControl("alliance_buildings", "Alliance buildings", false),
];
const root = {
  nodeType: 1,
  id: "map_filters",
  matches: () => false,
  querySelectorAll: () => controls,
  contains: control => controls.includes(control),
};
const document = {
  querySelectorAll(selector) {
    if (selector === "#map_filters") return [root];
    if (["[data-map-filters]", ".map-filters-list", ".leaflet-control-layers"].includes(selector)) return [];
    return controls.filter(control => selector.includes(control.value) || selector === `#${control.id}`);
  },
  getElementById: id => id === "map_filters" ? root : null,
  getElementsByTagName: () => [],
};
for (const control of controls) control.ownerDocument = { defaultView: { Event } };

let saveCount = 0;
let rootRefreshes = 0;
let uiRefreshes = 0;
let fallbackReleases = 0;
let opacityRestores = 0;
const mapEvents = [];
const mapLayers = new Set();
const legacyLayers = {
  user_missions: { id: "user_missions" },
  alliance_missions: { id: "alliance_missions" },
  user_buildings: { id: "user_buildings" },
};
const map = {
  hasLayer: layer => mapLayers.has(layer),
  addLayer: layer => mapLayers.add(layer),
  removeLayer: layer => mapLayers.delete(layer),
  fire: (event, payload) => mapEvents.push({ event, payload }),
};

const sandbox = {
  console,
  Event,
  document,
  SCRIPT: { controlId: "mcms-control", panelId: "mcms-panel", commandExperienceModalId: "mcms-modal", commandPaletteId: "mcms-palette" },
  NATIVE_VISIBILITY_FILTERS: descriptors,
  NATIVE_VISIBILITY_FEATURES: Object.freeze(["myMissions", "allianceMissions", "vehicles", "buildings"]),
  pageWindow: {
    I18n: { t: key => ({ "map_filters.user_missions": "My missions", "map_filters.alliance_missions": "Shared by alliance", "map_filters.user_buildings": "My buildings", "common.vehicles": "Vehicles" })[key] || key },
  },
  runtime: { destroyed: false },
  state: { visibility: { myMissions: true, allianceMissions: false, vehicles: true, buildings: true }, nativeVisibility: { migratedFeatures: [] }, economyMode: false },
  saveState: () => { saveCount += 1; },
  applyRootAttributes: () => { rootRefreshes += 1; },
  updateUI: () => { uiRefreshes += 1; },
  reconcileFeatureRefreshes() {},
  scheduleEconomyLayerSync() {},
  scheduleMarkerClassification() {},
  synchroniseVehicleMarkerClasses() {},
  synchronisePersonalBuildingVisibility: () => { fallbackReleases += 1; },
  restorePersonalBuildingLayerOpacity: () => { opacityRestores += 1; },
  findLeafletMapInstance: () => map,
};

vm.createContext(sandbox);
const declarations = `
const nativeVisibilityBoundFeatures=new Set();
const nativeVisibilitySessionInitialised=new Set();
const nativeVisibilityPendingFeatures=new Set();
const hiddenPersonalBuildingLayers=new Set();
const personalBuildingLayerOpacity=new Map();
let nativeVisibilityReconcileTimer=null;
let nativeVisibilityWriteDepth=0;
let toolkitFreshInstallAtLoad=false;
`;
const functionNames = [
  "normaliseNativeVisibilityToken",
  "normaliseNativeVisibilityLabel",
  "nativeVisibilityDescriptor",
  "nativeVisibilityTranslatedLabels",
  "nativeVisibilityControlRoots",
  "nativeVisibilityControlBelongsToToolkit",
  "nativeVisibilityControlTokens",
  "nativeVisibilityControlLabel",
  "nativeVisibilityControlMatchesFeature",
  "nativeVisibilityInteractiveControls",
  "findNativeVisibilityControl",
  "nativeVisibilityFeatureForControl",
  "nativeVisibilityControlState",
  "nativeVisibilityServiceState",
  "readNativeVisibilityState",
  "dispatchNativeVisibilityControl",
  "writeNativeVisibilityState",
  "releasePersonalBuildingVisibilityFallback",
  "nativeVisibilityFeatureMigrated",
  "markNativeVisibilityFeatureMigrated",
  "nativeVisibilityFallbackNeeded",
  "applyNativeVisibilityPreference",
  "adoptNativeVisibilityFeature",
  "reconcileNativeVisibilityBridge",
];
vm.runInContext(declarations + functionNames.map(extractFunction).join("\n\n") + `
this.__probe={
  findNativeVisibilityControl,nativeVisibilityFeatureForControl,writeNativeVisibilityState,
  applyNativeVisibilityPreference,adoptNativeVisibilityFeature,nativeVisibilityFallbackNeeded,
  releasePersonalBuildingVisibilityFallback,reconcileNativeVisibilityBridge,
  resetBridge(fresh=false){
    nativeVisibilityBoundFeatures.clear();nativeVisibilitySessionInitialised.clear();nativeVisibilityPendingFeatures.clear();
    hiddenPersonalBuildingLayers.clear();personalBuildingLayerOpacity.clear();nativeVisibilityReconcileTimer=null;
    toolkitFreshInstallAtLoad=fresh;state.nativeVisibility.migratedFeatures=[];
  },
  hideBuildingForFallback(layer,opacity=1){hiddenPersonalBuildingLayers.add(layer);personalBuildingLayerOpacity.set(layer,opacity);}
};
`, sandbox, { filename: "native-map-visibility-bridge.js" });

assert.equal(sandbox.__probe.findNativeVisibilityControl("myMissions").value, "user_missions");
assert.equal(sandbox.__probe.findNativeVisibilityControl("allianceMissions").value, "alliance_missions");
assert.equal(sandbox.__probe.findNativeVisibilityControl("vehicles").value, "show_vehicle");
assert.equal(sandbox.__probe.findNativeVisibilityControl("buildings").value, "user_buildings");
assert.equal(sandbox.__probe.nativeVisibilityFeatureForControl(controls[4]), "", "alliance buildings must remain independent");

let result = sandbox.__probe.writeNativeVisibilityState("myMissions", false);
assert.deepEqual(JSON.parse(JSON.stringify(result)), { handled: true, verified: true, source: "native-control" });
assert.equal(controls[0].checked, false);

assert.equal(sandbox.__probe.applyNativeVisibilityPreference("allianceMissions", true), true);
assert.equal(controls[1].checked, true);
assert.equal(sandbox.state.visibility.allianceMissions, false, "native write must not mutate Toolkit state independently");
assert.ok(sandbox.state.nativeVisibility.migratedFeatures.includes("allianceMissions"));
assert.equal(saveCount, 1);
assert.equal(sandbox.__probe.nativeVisibilityFallbackNeeded("allianceMissions"), false);

controls[4].checked = true;
assert.equal(sandbox.__probe.applyNativeVisibilityPreference("buildings", false), true);
assert.equal(controls[3].checked, false);
assert.equal(controls[4].checked, true, "own-buildings write touched alliance buildings");
assert.equal(fallbackReleases, 0);

const fallbackLayer = { id: "fallback-building" };
sandbox.state.visibility.buildings = true;
sandbox.__probe.hideBuildingForFallback(fallbackLayer, 0.4);
sandbox.__probe.releasePersonalBuildingVisibilityFallback();
assert.equal(fallbackReleases, 1, "visible fallback buildings were not handed back to the map");
sandbox.state.visibility.buildings = false;
sandbox.__probe.releasePersonalBuildingVisibilityFallback();
assert.equal(opacityRestores, 1, "hidden fallback building opacity was not released to the native filter");

controls[2].checked = false;
const adopted = sandbox.__probe.adoptNativeVisibilityFeature("vehicles");
assert.equal(adopted.handled, true);
assert.equal(adopted.changed, true);
assert.equal(sandbox.state.visibility.vehicles, false);
assert.equal(rootRefreshes, 1);
assert.equal(uiRefreshes, 1);

sandbox.__probe.resetBridge(true);
sandbox.state.visibility = { myMissions: true, allianceMissions: true, vehicles: true, buildings: true };
[controls[0].checked, controls[1].checked, controls[2].checked, controls[3].checked] = [false, true, false, false];
const allianceBeforeFreshAdoption = controls[4].checked;
const savesBeforeFreshAdoption = saveCount;
sandbox.__probe.reconcileNativeVisibilityBridge();
assert.deepEqual(JSON.parse(JSON.stringify(sandbox.state.visibility)), { myMissions: false, allianceMissions: true, vehicles: false, buildings: false });
assert.equal(saveCount, savesBeforeFreshAdoption + 1, "fresh native visibility was not persisted once");
assert.equal(controls[4].checked, allianceBeforeFreshAdoption, "fresh adoption changed alliance buildings");

sandbox.__probe.resetBridge(false);
sandbox.state.visibility = { myMissions: true, allianceMissions: false, vehicles: true, buildings: true };
[controls[0].checked, controls[1].checked, controls[2].checked, controls[3].checked] = [false, true, false, false];
const allianceBeforeUpgrade = controls[4].checked;
const savesBeforeUpgrade = saveCount;
sandbox.__probe.reconcileNativeVisibilityBridge();
assert.deepEqual(controls.slice(0, 4).map(control => control.checked), [true, false, true, true]);
assert.deepEqual(Array.from(sandbox.state.nativeVisibility.migratedFeatures), ["myMissions", "allianceMissions", "vehicles", "buildings"]);
assert.equal(saveCount, savesBeforeUpgrade + 1, "upgraded Toolkit visibility was not migrated once");
assert.equal(controls[4].checked, allianceBeforeUpgrade, "upgrade migration changed alliance buildings");

root.querySelectorAll = () => controls.filter(control => control.value !== "show_vehicle");
document.querySelectorAll = selector => {
  if (selector === "#map_filters") return [root];
  if (["[data-map-filters]", ".map-filters-list", ".leaflet-control-layers"].includes(selector)) return [];
  return [];
};
delete sandbox.pageWindow.show_vehicle;
assert.equal(sandbox.__probe.writeNativeVisibilityState("vehicles", true).handled, false);

root.querySelectorAll = () => [];
sandbox.pageWindow.map_filters_service = {
  getMapFiltersLayers: () => legacyLayers,
  getLayerByLayerId: id => legacyLayers[id],
};
mapLayers.add(legacyLayers.user_missions);
result = sandbox.__probe.writeNativeVisibilityState("myMissions", false);
assert.equal(result.handled, true);
assert.equal(result.verified, true);
assert.equal(mapLayers.has(legacyLayers.user_missions), false);
assert.equal(mapEvents.at(-1)?.event, "overlayremove", "legacy filter mutation was not exposed to MissionChief persistence listeners");

console.log("Native map visibility bridge runtime passed: native controls, fresh/upgrade migration, own/alliance building isolation, bidirectional adoption and legacy fallback verified.");
