#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const plain = value => JSON.parse(JSON.stringify(value));

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

for (const contract of [
  "const MAP_INTERACTION_SETTLE_MS = 90",
  "html[data-mcms-map-moving=\"true\"][data-mc-map-skin=\"control\"] .leaflet-tile-pane { filter:invert(92%) hue-rotate(182deg) brightness(62%) contrast(112%) saturate(72%) !important; }",
  "html[data-mcms-map-moving=\"true\"] .leaflet-tile-pane img.leaflet-tile { filter:none !important; }",
  "animation-play-state:paused !important",
  "function mutationIsLeafletTileNoise",
  "const renderer = coverageLeafletPathRenderer(map)",
  "renderer,",
]) assert.ok(source.includes(contract), `Missing Issue #668 contract: ${contract}`);

for (const retired of [
  "state.economyMode && economyMapMoving",
  "economyDeferredMapRefresh",
  "economyDeferredDomMutation",
  "economyLeafletPathRenderer",
]) assert.equal(source.includes(retired), false, `${retired} must not return`);

const counters = new Map();
const count = name => counters.set(name, (counters.get(name) || 0) + 1);
const value = name => counters.get(name) || 0;
const timers = new Map();
let nextTimer = 1;
const attributes = new Map();

const sandbox = {
  console,
  MAP_INTERACTION_SETTLE_MS: 90,
  document: {
    hidden: false,
    documentElement: {
      setAttribute(name, next) { attributes.set(name, String(next)); },
    },
  },
  runtime: { destroyed: false, mapBindings: [] },
  state: {
    economyMode: false,
    safeMode: { enabled: false },
    coverage: { enabled: true },
    allianceCredits: true,
    missionAge: true,
    unitCommitment: true,
    resourceGap: { enabled: true },
    transportWatcher: true,
    stuckDetector: { enabled: true },
    markerFocus: true,
    visibility: { vehicles: true, buildings: true },
  },
  runtimeSetTimeout(callback, delay) {
    const id = nextTimer++;
    timers.set(id, { callback, delay });
    return id;
  },
  runtimeClearTimeout(id) { if (id !== null && id !== undefined) timers.delete(id); },
  invalidateMarkerRegistryCaches(scope) { count(`invalidate:${scope}`); },
  scheduleMarkerStateSync() { count("marker-sync"); },
  scheduleEconomyLayerSync() { count("economy-sync"); },
  scheduleNativeVisibilityReconcile() { count("native-visibility"); },
  invalidateMapElementCache() { count("map-cache"); },
  refreshSuppression() { count("suppression"); },
  fitControlToMap() { count("fit"); },
  schedulePanelPosition() { count("panel-position"); },
  markerClassificationNeeded: () => true,
  nativeVisibilityFallbackNeeded: () => true,
  scheduleMarkerClassification() { count("classification"); },
  scheduleCoverageRefresh() { count("coverage"); },
  scheduleAllianceCreditRefresh() { count("alliance-credit"); },
  scheduleMissionAgeRefresh() { count("mission-age"); },
  scheduleUnitCommitmentRefresh() { count("unit-commitment"); },
  scheduleResourceGapRefresh() { count("resource-gap"); },
  missionSnapshotsNeeded: () => true,
  scheduleMissionSnapshotRefresh() { count("snapshots"); },
  scheduleTransportWatcherRefresh() { count("transport"); },
  scheduleStuckMissionRefresh() { count("stuck"); },
  operationalUiIsVisible: () => false,
  scheduleOperationalPanelsRender() { count("operational"); },
  normaliseMissionId: value => value === undefined || value === null || value === "" ? null : String(value),
  getBuildingLayerId: layer => layer?.building_id ?? null,
  applyEconomyToLeafletLayer() { count("economy-layer"); },
  markVehicleIcon() { count("vehicle-icon"); },
  refreshVehicleFollowBinding() { count("follow-refresh"); },
  markPersonalBuildingLayerIfOwned: () => false,
  hidePersonalBuildingLayer() { count("hide-building"); },
  suppressLeakedAllianceBuildingLayer() { count("alliance-building"); },
  stopVehicleFollow() { count("stop-follow"); },
  nativeAllianceBuildingFilterMayNeedEnforcement: () => false,
  openContextCommandMenu: () => false,
  markFeatureBeaconViewed() {},
  openTabletQuickWheel() {},
};

vm.createContext(sandbox);
const declarations = `
let mutationTimer=null,classifyTimer=null,markerStateSyncTimer=null,markerStateTrailingTimer=null,coverageTimer=null;
let allianceCreditTimer=null,missionAgeTimer=null,unitCommitmentTimer=null,transportWatcherTimer=null,resourceGapTimer=null,stuckMissionTimer=null,missionSnapshotTimer=null;
let enabledMapRefreshTimer=null;
let pendingEnabledMapRefresh={includeSnapshots:false,positionPanel:false,refreshOperational:false,fullRefresh:false};
let mapInteractionMoving=false,mapInteractionSettling=false,mapInteractionDeferredRefresh=false,mapInteractionDeferredSnapshots=false,mapInteractionDeferredDomMutation=false,mapInteractionMarkerSyncNeeded=false;
const mapInteractionDirtyScopes=new Set();
let coverageCanvasRenderer=null;
let dragState=null,economyLayerEnforcement=false,enforcingPersonalBuildingVisibility=false,enforcingNativeAllianceBuildingVisibility=false,enforcingBuildingVisibility=false;
let followedVehicleId='',followedVehicleMarker=null,vehicleFollowRecentering=false,activeDeviceLayout='desktop';
`;
vm.runInContext(declarations + [
  "isToolkitLeafletLayer",
  "mapInteractionWorkDeferred",
  "deferMapInteractionRefresh",
  "cancelPendingMapRenderWork",
  "beginMapInteractionBatch",
  "completeMapInteractionBatch",
  "flushEnabledMapRefreshes",
  "scheduleEnabledMapRefreshes",
  "attachMapEvents",
  "mutationIsLeafletTileNoise",
  "coverageLeafletPathRenderer",
].map(extractFunction).join("\n\n") + `
this.__probe={
  attachMapEvents,
  deferMapInteractionRefresh,
  mutationIsLeafletTileNoise,
  coverageLeafletPathRenderer,
  state:()=>({moving:mapInteractionMoving,settling:mapInteractionSettling,scopes:[...mapInteractionDirtyScopes]}),
};`, sandbox, { filename: "issue668-map-interaction.js" });

function fakeMap() {
  const handlers = new Map();
  return {
    handlers,
    on(types, handler) { for (const type of types.split(/\s+/u)) handlers.set(type, handler); },
    off(types) { for (const type of types.split(/\s+/u)) handlers.delete(type); },
    emit(type, event = {}) { handlers.get(type)?.({ type, ...event }); },
    getContainer: () => ({ getBoundingClientRect: () => ({ left: 0, top: 0 }) }),
  };
}

const map = fakeMap();
sandbox.__probe.attachMapEvents(map);
assert.equal(sandbox.runtime.mapBindings.length, 6, "map event ownership changed");
assert.equal(value("marker-sync"), 1, "initial building selector reconciliation was not delegated to the consolidated marker scheduler");
counters.clear();

map.emit("movestart");
assert.equal(attributes.get("data-mcms-map-moving"), "true");
assert.deepEqual(plain(sandbox.__probe.state()), { moving: true, settling: false, scopes: [] });

const layers = [
  { mission_id: 1 },
  { vehicle_id: 2 },
  { building_id: 3 },
  {},
];
for (let cycle = 0; cycle < 1000; cycle += 1) {
  const layer = layers[cycle % layers.length];
  map.emit(cycle % 2 ? "layerremove" : "layeradd", { layer });
}
sandbox.__probe.deferMapInteractionRefresh({ domMutation: true, includeSnapshots: true });

assert.equal(value("invalidate:all") + value("invalidate:mission") + value("invalidate:vehicle") + value("invalidate:building"), 0, "registry work ran during movement");
assert.equal(value("classification") + value("coverage") + value("alliance-credit") + value("mission-age") + value("unit-commitment") + value("resource-gap") + value("snapshots") + value("marker-sync"), 0, "heavy refresh work ran during movement");
assert.equal(timers.size, 0, "movement churn scheduled a timer before settle");
assert.deepEqual(plain(sandbox.__probe.state().scopes).sort(), ["all", "building", "mission", "vehicle"]);

map.emit("moveend");
map.emit("zoomend");
map.emit("viewreset");
assert.equal(timers.size, 1, "map end events did not coalesce into exactly one settle timer");
assert.equal(Array.from(timers.values())[0].delay, 90, "settle refresh delay drifted");
assert.equal(attributes.get("data-mcms-map-moving"), "true", "visual effects resumed before the settled refresh");

const [{ callback }] = timers.values();
timers.clear();
callback();

assert.equal(value("invalidate:all"), 1, "dirty registries were not invalidated exactly once");
assert.equal(value("invalidate:mission") + value("invalidate:vehicle") + value("invalidate:building"), 0, "scoped invalidation duplicated the all-scope refresh");
for (const name of ["classification", "coverage", "alliance-credit", "mission-age", "unit-commitment", "resource-gap", "snapshots", "marker-sync", "map-cache", "suppression", "fit", "panel-position"]) {
  assert.equal(value(name), 1, `${name} did not run exactly once after settle`);
}
assert.equal(attributes.get("data-mcms-map-moving"), "false");
assert.deepEqual(plain(sandbox.__probe.state()), { moving: false, settling: false, scopes: [] });

const tileTarget = {
  nodeType: 1,
  matches: selector => selector.includes(".leaflet-tile-pane"),
  closest: selector => selector === ".leaflet-tile-pane" ? tileTarget : null,
};
const markerTarget = { nodeType: 1, matches: () => false, closest: () => null };
assert.equal(sandbox.__probe.mutationIsLeafletTileNoise({ type: "childList", target: tileTarget, addedNodes: [], removedNodes: [] }), true);
assert.equal(sandbox.__probe.mutationIsLeafletTileNoise({ type: "childList", target: markerTarget, addedNodes: [], removedNodes: [] }), false);

let canvasCreates = 0;
let removedRenderers = 0;
const mapA = { removeLayer() { removedRenderers += 1; } };
const mapB = { removeLayer() { removedRenderers += 1; } };
sandbox.pageWindow = { L: { canvas: () => ({ _map: null, id: ++canvasCreates }) } };
const rendererA = sandbox.__probe.coverageLeafletPathRenderer(mapA);
rendererA._map = mapA;
assert.equal(sandbox.__probe.coverageLeafletPathRenderer(mapA), rendererA, "coverage renderer was not shared on one map");
const rendererB = sandbox.__probe.coverageLeafletPathRenderer(mapB);
assert.notEqual(rendererB, rendererA, "coverage renderer crossed map ownership");
assert.equal(canvasCreates, 2);
assert.equal(removedRenderers, 1);
assert.equal(rendererA.__mcmsCoverageRenderer, true);

console.log("Issue #668 map interaction passed: 1,000 layer changes performed zero heavy work during movement and one consolidated Canvas-backed refresh after settle.");
