#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const pattern = new RegExp(`\\b(?:async\\s+)?function\\s+${name}\\s*\\(`, "u");
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

function makeMarkerIcon() {
  const classes = new Set(["leaflet-marker-icon"]);
  const attributes = new Map();
  return {
    nodeType: 1,
    dataset: {},
    classList: {
      contains: className => classes.has(className),
      toggle(className, enabled) {
        if (enabled) classes.add(className);
        else classes.delete(className);
      },
    },
    getAttribute: name => attributes.get(name) ?? null,
    setAttribute: (name, value) => attributes.set(name, String(value)),
    hasAttribute: name => attributes.has(name),
    removeAttribute: name => attributes.delete(name),
  };
}

const nativeVehicleIcon = makeMarkerIcon();
const secondaryVehicleIcon = makeMarkerIcon();
const overlappingMissionIcon = makeMarkerIcon();
overlappingMissionIcon.classList.toggle("mcms-marker-vehicle", true);
overlappingMissionIcon.setAttribute("data-mcms-vehicle-marker", "true");
overlappingMissionIcon.dataset.mcmsMarkerKind = "vehicle";
const camelCaseMissionIcon = makeMarkerIcon();
camelCaseMissionIcon.classList.toggle("mcms-marker-vehicle", true);
camelCaseMissionIcon.setAttribute("data-mcms-vehicle-marker", "true");
camelCaseMissionIcon.dataset.mcmsMarkerKind = "vehicle";
const nestedAllianceMissionIcon = makeMarkerIcon();
nestedAllianceMissionIcon.classList.toggle("mcms-marker-vehicle", true);
nestedAllianceMissionIcon.setAttribute("data-mcms-vehicle-marker", "true");
nestedAllianceMissionIcon.dataset.mcmsMarkerKind = "vehicle";
let availableControls = controls;
const root = {
  nodeType: 1,
  id: "map_filters",
  matches: () => false,
  getElementsByTagName: tagName => tagName === "*" || tagName === "input" ? availableControls : [],
  contains: control => controls.includes(control),
};
const document = {
  baseURI: "https://www.missionchief.co.uk/",
  getElementById(id) {
    if (id === "map_filters") return root;
    return availableControls.find(control => control.id === id || control.value === id) || null;
  },
  getElementsByClassName: () => [],
  getElementsByName: name => availableControls.filter(control => control.name === name),
  getElementsByTagName: tagName => tagName === "*" || tagName === "input" ? availableControls : [],
};
for (const control of controls) control.ownerDocument = { defaultView: { Event } };

let saveCount = 0;
let rootRefreshes = 0;
let uiRefreshes = 0;
let fallbackReleases = 0;
let opacityRestores = 0;
const toasts = [];
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

let settingsApiValue = false;
let settingsApiAvailable = true;
let settingsFormAmbiguous = false;
let settingsFormToken = "native-csrf-token";
let settingsFormAction = "/settings/map";
let settingsPostCount = 0;
const settingsRequests = [];
const nativeSettingsForm = {
  getAttribute(name) {
    if (name === "action") return settingsFormAction;
    if (name === "method") return "post";
    return null;
  },
};
const nativeSettingsCheckbox = {
  name: "show_vehicle",
  value: "1",
  checked: false,
  disabled: false,
  closest: selector => selector === "form" ? nativeSettingsForm : null,
};
const duplicateSettingsCheckbox = { ...nativeSettingsCheckbox };
const settingsMapAnchor = {
  href: "https://www.missionchief.co.uk/settings/map",
  getAttribute: name => name === "href" ? "/settings/map" : null,
};
const nativeSettingsIndexDocument = {
  querySelectorAll(selector) {
    if (selector === 'input[type="checkbox"][name]') return [];
    if (selector === "a[href]") return [settingsMapAnchor];
    return [];
  },
};
const nativeSettingsDocument = {
  querySelectorAll(selector) {
    if (selector === 'input[type="checkbox"][name]') {
      return settingsFormAmbiguous ? [nativeSettingsCheckbox, duplicateSettingsCheckbox] : [nativeSettingsCheckbox];
    }
    if (selector === "a[href]") return [];
    return [];
  },
  querySelector(selector) {
    if (selector === 'meta[name="csrf-token"]' && settingsFormToken) {
      return { getAttribute: name => name === "content" ? settingsFormToken : null };
    }
    return null;
  },
};

class NativeFormData {
  constructor(form) {
    assert.equal(form, nativeSettingsForm);
    this.values = new Map([
      ["authenticity_token", settingsFormToken ? [settingsFormToken] : []],
      ["route_show", ["1"]],
      ["show_vehicle", nativeSettingsCheckbox.checked ? ["0", "1"] : ["0"]],
    ]);
  }
  get(name) { return this.getAll(name)[0] ?? null; }
  getAll(name) { return [...(this.values.get(name) || [])]; }
}

class NativeDOMParser {
  parseFromString(html, type) {
    assert.equal(type, "text/html");
    if (html === "<settings-index-page>") return nativeSettingsIndexDocument;
    if (html === "<native-settings-page>") return nativeSettingsDocument;
    throw new Error(`Unexpected native settings HTML ${html}`);
  }
}

function nativeResponse({ ok = true, status = 200, url, json, text = "" }) {
  return { ok, status, url, json: async () => json, text: async () => text };
}

async function runtimeFetch(urlValue, init = {}) {
  const url = new URL(urlValue, document.baseURI);
  settingsRequests.push({ url: url.href, method: String(init.method || "GET").toUpperCase(), init });
  if (url.pathname === "/api/settings" && String(init.method || "GET").toUpperCase() === "GET") {
    if (!settingsApiAvailable) return nativeResponse({ ok: false, status: 503, url: url.href, json: {} });
    return nativeResponse({ url: url.href, json: { show_vehicle: settingsApiValue, leitstelle_building_id: null } });
  }
  if (url.pathname === "/settings/index" && String(init.method || "GET").toUpperCase() === "GET") {
    return nativeResponse({ url: url.href, text: "<settings-index-page>" });
  }
  if (url.pathname === "/settings/map" && String(init.method || "GET").toUpperCase() === "GET") {
    return nativeResponse({ url: url.href, text: "<native-settings-page>" });
  }
  if (url.pathname === "/settings/map" && String(init.method || "GET").toUpperCase() === "POST") {
    settingsPostCount += 1;
    const values = init.body.getAll("show_vehicle");
    settingsApiValue = values.at(-1) === "1";
    return nativeResponse({ url: url.href, text: "<native-settings-page>" });
  }
  throw new Error(`Unexpected native settings request ${init.method || "GET"} ${url.href}`);
}

let nativeVehicleLoads = 0;
const nativeVehicleRemovals = [];
const nativeVehicleAnimationRemovals = [];
let vehicleCacheInvalidations = 0;
const sandboxConsole = Object.create(console);
sandboxConsole.debug = () => {};

const sandbox = {
  console: sandboxConsole,
  Event,
  URL,
  FormData: NativeFormData,
  DOMParser: NativeDOMParser,
  document,
  SCRIPT: { name: "MissionChief Map Command Toolkit", controlId: "mcms-control", panelId: "mcms-panel", commandExperienceModalId: "mcms-modal", commandPaletteId: "mcms-palette" },
  NATIVE_VISIBILITY_FILTERS: descriptors,
  NATIVE_VISIBILITY_FEATURES: Object.freeze(["myMissions", "allianceMissions", "vehicles", "buildings"]),
  pageWindow: {
    location: { origin: "https://www.missionchief.co.uk", href: "https://www.missionchief.co.uk/" },
    I18n: { t: key => ({ "map_filters.user_missions": "My missions", "map_filters.alliance_missions": "Shared by alliance", "map_filters.user_buildings": "My buildings", "common.vehicles": "Vehicles" })[key] || key },
    user_id: 7,
    mission_markers: [
      { mission_id: 740, user_id: 7, _icon: overlappingMissionIcon },
      { missionId: 741, userId: 7, _icon: camelCaseMissionIcon },
      { options: { mission_id: 742, user_id: 99 }, _icon: nestedAllianceMissionIcon },
    ],
    vehicle_markers: [
      { _icon: nativeVehicleIcon },
      { _icon: secondaryVehicleIcon },
      { _icon: overlappingMissionIcon },
      { _icon: camelCaseMissionIcon },
      { _icon: nestedAllianceMissionIcon },
    ],
    mission_vehicles_per_vid: new Map(),
    show_vehicle: false,
    loadVehiclesOnTheMove() { nativeVehicleLoads += 1; },
    vehicleArrive(marker) { marker.vehicle_marker_deleted = true; nativeVehicleRemovals.push(marker); },
    deregisterVehicleAnim(index) { nativeVehicleAnimationRemovals.push(index); },
  },
  runtime: { destroyed: false },
  state: { visibility: { myMissions: true, allianceMissions: false, vehicles: true, buildings: true }, nativeVisibility: { migratedFeatures: [] }, economyMode: false },
  saveState: () => { saveCount += 1; },
  applyRootAttributes: () => { rootRefreshes += 1; },
  updateUI: () => { uiRefreshes += 1; },
  reconcileFeatureRefreshes() {},
  scheduleEconomyLayerSync() {},
  scheduleMarkerClassification() {},
  scheduleNativeVisibilityReconcile() {},
  showToast: message => { toasts.push(message); },
  runtimeFetch,
  runtimeDelay: async () => true,
  invalidateMarkerRegistryCaches: scope => { if (scope === "vehicle") vehicleCacheInvalidations += 1; },
  closePanel() {},
  synchronisePersonalBuildingVisibility: () => { fallbackReleases += 1; },
  restorePersonalBuildingLayerOpacity: () => { opacityRestores += 1; },
  findLeafletMapInstance: () => map,
  currentUserIdCached: () => "7",
  missionIdFromMarker: marker => {
    const value = marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId;
    return value === undefined || value === null || value === "" ? null : String(value);
  },
  missionOwnerId: marker => marker?.user_id ?? marker?.userId ?? marker?.options?.user_id ?? marker?.options?.userId ?? null,
};

vm.createContext(sandbox);
const declarations = `
const MARKER_REGISTRY_CACHE_MS=350;
const NATIVE_VEHICLE_SETTINGS_REQUEST_TIMEOUT_MS=12000;
const NATIVE_VEHICLE_SETTINGS_API_PATH='/api/settings';
const NATIVE_VEHICLE_SETTINGS_PATH_PREFIX='/settings';
const NATIVE_VEHICLE_SETTINGS_SEED_PATHS=Object.freeze(['/settings/index','/settings']);
const NATIVE_VEHICLE_SETTINGS_DISCOVERY_LIMIT=8;
const MARKER_CLASS_NAMES=['mcms-marker-mission','mcms-marker-my-mission','mcms-marker-alliance-mission','mcms-marker-building','mcms-marker-personal-building','mcms-marker-vehicle','mcms-marker-unknown'];
const markerRegistryCache=new Map();
const nativeVisibilityBoundFeatures=new Set();
const nativeVisibilitySessionInitialised=new Set();
const nativeVisibilityPendingFeatures=new Set();
const hiddenPersonalBuildingLayers=new Set();
const personalBuildingLayerOpacity=new Map();
let nativeVisibilityReconcileQueued=false;
let nativeVisibilityWriteDepth=0;
let nativeVehicleTogglePromise=null;
let toolkitFreshInstallAtLoad=false;
`;
const functionNames = [
  "normaliseRegistryValues",
  "getCachedRegistry",
  "normaliseNativeVisibilityToken",
  "normaliseNativeVisibilityLabel",
  "nativeVisibilityDescriptor",
  "nativeVisibilityTranslatedLabels",
  "nativeVisibilityElementById",
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
  "nativeVehicleSameOriginUrl",
  "nativeVehicleSettingsPathAllowed",
  "nativeVehicleSettingsControls",
  "nativeVehicleSettingsCandidateUrls",
  "fetchNativeVehicleSetting",
  "fetchNativeVehicleSettingsDocument",
  "prepareNativeVehicleSettingsSubmission",
  "verifyNativeVehicleSetting",
  "submitNativeVehicleSetting",
  "applyNativeVehicleRuntimeSetting",
  "mirrorNativeVehicleSetting",
  "dispatchNativeVisibilityControl",
  "writeNativeVisibilityState",
  "releasePersonalBuildingVisibilityFallback",
  "nativeVisibilityFeatureMigrated",
  "markNativeVisibilityFeatureMigrated",
  "nativeVisibilityFallbackNeeded",
  "applyNativeVisibilityPreference",
  "adoptNativeVisibilityFeature",
  "reconcileNativeVisibilityBridge",
  "getVehicleMarkerLayers",
  "getMissionMarkerLayers",
  "getVehicleMarkerIcons",
  "markVehicleIcon",
  "synchroniseVehicleMarkerClasses",
  "getMissionIconsByOwnership",
  "markerClassesForType",
  "markerTypeIsApplied",
  "applyMarkerType",
  "applyMapVisibilityToggleEffects",
  "toggleNativeVehicleVisibility",
];
vm.runInContext(declarations + functionNames.map(extractFunction).join("\n\n") + `
this.__probe={
  findNativeVisibilityControl,nativeVisibilityFeatureForControl,writeNativeVisibilityState,
  fetchNativeVehicleSetting,prepareNativeVehicleSettingsSubmission,submitNativeVehicleSetting,applyNativeVehicleRuntimeSetting,mirrorNativeVehicleSetting,
  applyNativeVisibilityPreference,adoptNativeVisibilityFeature,nativeVisibilityFallbackNeeded,
  releasePersonalBuildingVisibilityFallback,reconcileNativeVisibilityBridge,applyMapVisibilityToggleEffects,toggleNativeVehicleVisibility,
  synchroniseVehicleMarkerClasses,
  resetBridge(fresh=false){
    nativeVisibilityBoundFeatures.clear();nativeVisibilitySessionInitialised.clear();nativeVisibilityPendingFeatures.clear();
    hiddenPersonalBuildingLayers.clear();personalBuildingLayerOpacity.clear();nativeVisibilityReconcileQueued=false;
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
result = sandbox.__probe.writeNativeVisibilityState("vehicles", true);
assert.deepEqual(JSON.parse(JSON.stringify(result)), { handled: false, verified: false, source: "native-settings-form" }, "vehicle writes must use the persisted native settings form");

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
assert.equal(controls[2].checked, false, "adopting the game setting must not rewrite MissionChief Vehicles OFF");
assert.equal(rootRefreshes, 1);
assert.equal(uiRefreshes, 1);
assert.equal(sandbox.__probe.nativeVisibilityFallbackNeeded("vehicles"), false, "Vehicles must never regain a Toolkit-owned CSS fallback");
assert.equal(sandbox.__probe.nativeVisibilityFallbackNeeded("buildings"), false);
sandbox.__probe.applyMapVisibilityToggleEffects("vehicles");
for (const icon of [nativeVehicleIcon, secondaryVehicleIcon]) {
  assert.equal(icon.classList.contains("mcms-marker-vehicle"), false, "the native Vehicles setting unexpectedly invoked the retired marker mask");
  assert.equal(icon.getAttribute("data-mcms-vehicle-marker"), null);
}

const savesBeforeNativeToggle = saveCount;
settingsApiValue = false;
nativeSettingsCheckbox.checked = false;
assert.equal(await sandbox.__probe.toggleNativeVehicleVisibility(), true);
assert.equal(settingsApiValue, true, "Button 3 did not persist MissionChief show_vehicle ON");
assert.equal(controls[2].checked, true, "Button 3 did not mirror MissionChief's verified Show vehicles on map state");
assert.equal(sandbox.state.visibility.vehicles, true, "Toolkit UI did not mirror MissionChief Vehicles ON");
assert.equal(saveCount, savesBeforeNativeToggle + 1);
assert.equal(settingsPostCount, 1, "Button 3 did not submit exactly one native settings form");
assert.equal(settingsRequests.find(request => request.method === "POST")?.url, "https://www.missionchief.co.uk/settings/map");
assert.ok(settingsRequests.some(request => request.method === "GET" && request.url === "https://www.missionchief.co.uk/settings/index"), "Button 3 did not enter MissionChief's global settings area");
assert.ok(settingsRequests.some(request => request.method === "GET" && request.url === "https://www.missionchief.co.uk/settings/map"), "Button 3 did not discover the native Map and vehicles settings tab");
assert.equal(settingsRequests.find(request => request.method === "POST")?.init.body.get("authenticity_token"), settingsFormToken, "native CSRF token was not preserved");
assert.equal(nativeVehicleLoads, 1, "MissionChief's native vehicle reload was not requested after enabling");
assert.equal(toasts.at(-1), "MissionChief vehicles on");
assert.equal(await sandbox.__probe.toggleNativeVehicleVisibility(), true);
assert.equal(settingsApiValue, false, "Button 3 did not persist MissionChief show_vehicle OFF");
assert.equal(controls[2].checked, false);
assert.equal(sandbox.state.visibility.vehicles, false);
assert.equal(settingsPostCount, 2, "Button 3 submitted an unexpected number of native settings forms");
assert.deepEqual(nativeVehicleRemovals, sandbox.pageWindow.vehicle_markers.slice(0, 2), "MissionChief's native vehicle-removal routine did not receive every vehicle-only marker");
assert.deepEqual(nativeVehicleAnimationRemovals, [0, 1], "MissionChief's native vehicle animations were not retired without touching overlapping mission identities");
for (const marker of sandbox.pageWindow.mission_markers) assert.notEqual(marker.vehicle_marker_deleted, true, "native vehicle removal touched a mission identity that overlapped the vehicle registry");
assert.equal(vehicleCacheInvalidations, 2);
assert.equal(toasts.at(-1), "MissionChief vehicles off");

// Vehicle classification remains available to Marker Focus, but it no longer owns
// visibility and mission identities must still win overlapping game registries.
sandbox.__probe.synchroniseVehicleMarkerClasses?.();
for (const icon of [nativeVehicleIcon, secondaryVehicleIcon]) {
  assert.equal(icon.classList.contains("mcms-marker-vehicle"), true, "every vehicle population must be classified");
  assert.equal(icon.getAttribute("data-mcms-vehicle-marker"), "true");
}
assert.equal(overlappingMissionIcon.classList.contains("mcms-marker-my-mission"), true, "mission identity must win a registry overlap");
assert.equal(overlappingMissionIcon.classList.contains("mcms-marker-vehicle"), false, "overlapping mission retained the vehicle class");
assert.equal(overlappingMissionIcon.getAttribute("data-mcms-vehicle-marker"), null, "overlapping mission retained the vehicle attribute");
assert.equal(overlappingMissionIcon.dataset.mcmsMarkerKind, "my-mission", "overlapping mission ownership was not restored");
assert.equal(camelCaseMissionIcon.classList.contains("mcms-marker-my-mission"), true, "camelCase mission identity was not recognised");
assert.equal(camelCaseMissionIcon.classList.contains("mcms-marker-vehicle"), false, "camelCase mission retained the vehicle class");
assert.equal(camelCaseMissionIcon.getAttribute("data-mcms-vehicle-marker"), null, "camelCase mission retained the vehicle attribute");
assert.equal(nestedAllianceMissionIcon.classList.contains("mcms-marker-alliance-mission"), true, "nested alliance mission identity was not recognised");
assert.equal(nestedAllianceMissionIcon.classList.contains("mcms-marker-vehicle"), false, "nested alliance mission retained the vehicle class");
assert.equal(nestedAllianceMissionIcon.getAttribute("data-mcms-vehicle-marker"), null, "nested alliance mission retained the vehicle attribute");

sandbox.__probe.resetBridge(true);
sandbox.state.visibility = { myMissions: true, allianceMissions: true, vehicles: true, buildings: true };
[controls[0].checked, controls[1].checked, controls[2].checked, controls[3].checked] = [false, true, false, false];
const allianceBeforeFreshAdoption = controls[4].checked;
const savesBeforeFreshAdoption = saveCount;
sandbox.__probe.reconcileNativeVisibilityBridge();
assert.deepEqual(JSON.parse(JSON.stringify(sandbox.state.visibility)), { myMissions: false, allianceMissions: true, vehicles: false, buildings: false });
assert.equal(controls[2].checked, false, "fresh adoption rewrote MissionChief's Vehicles setting");
assert.equal(saveCount, savesBeforeFreshAdoption + 1, "fresh native visibility was not persisted once");
assert.equal(controls[4].checked, allianceBeforeFreshAdoption, "fresh adoption changed alliance buildings");

const savesBeforeStableReconcile = saveCount;
sandbox.__probe.reconcileNativeVisibilityBridge();
assert.equal(sandbox.state.visibility.vehicles, false);
assert.equal(controls[2].checked, false);
assert.equal(saveCount, savesBeforeStableReconcile, "stable native reconciliation rewrote saved state");

controls[2].checked = true;
const savesBeforeManualVehicleEnable = saveCount;
sandbox.__probe.reconcileNativeVisibilityBridge();
assert.equal(sandbox.state.visibility.vehicles, true, "a deliberate MissionChief Vehicles ON change was not adopted");
assert.equal(controls[2].checked, true);
assert.equal(saveCount, savesBeforeManualVehicleEnable + 1, "manual MissionChief Vehicles change was not mirrored exactly once");

sandbox.__probe.resetBridge(false);
sandbox.state.visibility = { myMissions: true, allianceMissions: false, vehicles: true, buildings: true };
[controls[0].checked, controls[1].checked, controls[2].checked, controls[3].checked] = [false, true, false, false];
const allianceBeforeUpgrade = controls[4].checked;
const savesBeforeUpgrade = saveCount;
sandbox.__probe.reconcileNativeVisibilityBridge();
assert.deepEqual(controls.slice(0, 4).map(control => control.checked), [true, false, false, true]);
assert.equal(sandbox.state.visibility.vehicles, false, "upgrade migration overwrote MissionChief's persisted Vehicles setting with stale Toolkit state");
assert.deepEqual(Array.from(sandbox.state.nativeVisibility.migratedFeatures), ["myMissions", "allianceMissions", "vehicles", "buildings"]);
assert.equal(saveCount, savesBeforeUpgrade + 1, "upgraded Toolkit visibility was not migrated once");
assert.equal(controls[4].checked, allianceBeforeUpgrade, "upgrade migration changed alliance buildings");

availableControls = controls.filter(control => control.value !== "show_vehicle");
delete sandbox.pageWindow.show_vehicle;
assert.equal(sandbox.__probe.writeNativeVisibilityState("vehicles", true).handled, false);
const vehicleMirrorBeforeUnavailableToggle = sandbox.state.visibility.vehicles;
settingsApiValue = vehicleMirrorBeforeUnavailableToggle;
settingsFormAmbiguous = true;
const postsBeforeAmbiguousForm = settingsPostCount;
assert.equal(await sandbox.__probe.toggleNativeVehicleVisibility(), false);
assert.equal(settingsPostCount, postsBeforeAmbiguousForm, "an ambiguous native show_vehicle form was submitted");
assert.equal(sandbox.state.visibility.vehicles, vehicleMirrorBeforeUnavailableToggle, "an ambiguous native form created a Toolkit-only vehicle state");
settingsFormAmbiguous = false;
nativeSettingsCheckbox.checked = !settingsApiValue;
assert.equal(await sandbox.__probe.toggleNativeVehicleVisibility(), false);
assert.equal(settingsPostCount, postsBeforeAmbiguousForm, "a stale native show_vehicle form was submitted after the authoritative value changed");
assert.equal(sandbox.state.visibility.vehicles, vehicleMirrorBeforeUnavailableToggle, "a stale native form created a Toolkit-only vehicle state");
nativeSettingsCheckbox.checked = settingsApiValue;
settingsFormAction = "/buildings/314";
assert.equal(await sandbox.__probe.toggleNativeVehicleVisibility(), false);
assert.equal(settingsPostCount, postsBeforeAmbiguousForm, "an out-of-scope native form action was submitted");
assert.equal(sandbox.state.visibility.vehicles, vehicleMirrorBeforeUnavailableToggle, "an out-of-scope form action created a Toolkit-only vehicle state");
settingsFormAction = "/settings/map";
settingsApiAvailable = false;
assert.equal(await sandbox.__probe.toggleNativeVehicleVisibility(), false);
assert.equal(sandbox.state.visibility.vehicles, vehicleMirrorBeforeUnavailableToggle, "unavailable native setting created a Toolkit-only vehicle state");
assert.equal(toasts.at(-1), "MissionChief vehicle setting unavailable · no change made");
settingsApiAvailable = true;

availableControls = [];
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

console.log("Native map visibility bridge runtime passed: nullable Dispatch Centre settings, bounded global Map and vehicles form discovery, persisted show_vehicle writes with API read-back, native live-map refresh, no vehicle CSS fallback, upgrade adoption, marker-focus classification, own/alliance building isolation and legacy filter fallback verified.");
