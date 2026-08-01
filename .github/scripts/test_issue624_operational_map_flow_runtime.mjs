#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const plain = value => JSON.parse(JSON.stringify(value));

function extractFunction(name) {
  const marker = "    function " + name + "(";
  const start = source.indexOf(marker);
  assert.ok(start >= 0, name + " is missing");
  const parameters = source.indexOf("(", start);
  let parameterDepth = 0;
  let brace = -1;
  for (let index = parameters; index < source.length; index += 1) {
    if (source[index] === "(") parameterDepth += 1;
    if (source[index] === ")" && --parameterDepth === 0) { brace = source.indexOf("{", index); break; }
  }
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
    if (char === "'" || char === '"' || char === String.fromCharCode(96)) { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error("Unable to extract " + name);
}

const records = [
  { id: 12, caption: "ARV 12", vehicle_type_caption: "Armed Response Vehicle", building_caption: "Wakefield Police", fms_real: 2 },
  { id: 44, caption: "Rescue Pump 44", vehicle_type_caption: "Rescue Pump", building_caption: "Fife Central", fms_real: 3 },
];
const marker12 = { id: 12 };
const sandbox = {
  console,
  Math,
  SCRIPT: { commandPaletteId: "palette", contextMenuId: "context", quickWheelId: "wheel" },
  getPersonalVehicleRecords: () => records,
  getVehicleMarkerLayers: () => [marker12],
  vehicleRecordId: value => String(value.id),
  customVehicleClassificationFromRecord: () => null,
  customVehicleClassificationForId: () => null,
  commandPaletteRecordValue(record, keys) { for (const key of keys) if (record[key]) return String(record[key]); return ""; },
  vehicleStatusCode: record => Number(record.fms_real ?? record.id === 12 ? 2 : null),
  vehicleStatusBucket: record => Number(record.fms_real) === 3 ? "travelling" : "available",
  vehicleSearchSignal: record => `${record.caption} ${record.vehicle_type_caption}`,
  commandPaletteNormalise: value => String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim(),
  sessionCleanupSpawnLayers: () => ({ map: { removeLayer() {} }, layers: [{ __mcmsMissionSpawnLayer: true }] }),
  findLeafletMapInstance: () => null,
  closeCommandExperienceModal() {},
  stopVehicleFollow() { sandbox.followedVehicleId = ""; },
  clearMissionLockOnEffect() {},
  closeContextCommandMenu() {},
  closeTabletQuickWheel() {},
  closeCommandPalette() {},
  commandExperienceElement: () => null,
  commandInterfaceApplySearch() {},
  updateCommandInterfaceHeader() {},
  scheduleEnabledMapRefreshes() {},
  scheduleMajorIncidentFeedRender() {},
  missionSnapshotsNeeded: () => true,
  showToast(message) { sandbox.toast = message; },
  document: {
    querySelectorAll: () => [],
    getElementById: () => null,
  },
};
vm.createContext(sandbox);
vm.runInContext(
  ["unitLocatorRecords", "sessionCleanupPlan", "performSessionCleanup"].map(extractFunction).join("\n") +
  "\nlet unitLocatorQuery='';var followedVehicleId='12';let missionLockOnMarker={};let missionLockOnTravelOverlay=null;let missionLockOnTimer=null;" +
  "let commandSearchQuery='abc';let majorIncidentFeedManualPaused=true;let majorIncidentFeedExpanded=false;let majorIncidentFeedInteractionPauseUntil=123;" +
  "const notificationEventSeen=new Map([['a',1]]);const notificationActiveEvents=new Set(['b']);const recentCompletedMissions=[{id:1}];" +
  "const missionSnapshotCache=new Map([[1,{}]]);const missionPanelCache=new Map([[1,{}]]);const markerRegistryCache=new Map([[1,{}]]);const resourceGapAnalysisCache=new Map([[1,{}]]);" +
  "let resourceGapVehicleContextCache={key:'x',createdAt:1,available:[1]};let operationalPressureCache={key:'x',snapshot:{}};" +
  "this.__probe={units:unitLocatorRecords,plan:sessionCleanupPlan,clean:performSessionCleanup,state(){return {followedVehicleId,commandSearchQuery,unitLocatorQuery,majorIncidentFeedManualPaused,majorIncidentFeedExpanded,notificationSeen:notificationEventSeen.size,notificationActive:notificationActiveEvents.size,recent:recentCompletedMissions.length,caches:missionSnapshotCache.size+missionPanelCache.size+markerRegistryCache.size+resourceGapAnalysisCache.size,resource:resourceGapVehicleContextCache,pressure:operationalPressureCache}}};",
  sandbox,
  { filename: "issue624-operational-map-flow-runtime.js" },
);

assert.deepEqual(plain(sandbox.__probe.units("arv wakefield").map(row => row.id)), ["12"]);
assert.deepEqual(plain(sandbox.__probe.units("44 travelling").map(row => row.id)), ["44"]);
assert.equal(sandbox.__probe.units("rescue")[0].marker, null, "a searchable vehicle may be listed without a live marker but cannot be followed");

const protectedState = { profiles: [{ name: "Keep" }], bookmarks: [{ name: "Keep" }], webhook: "secret", finance: [{ amount: 1 }] };
const plan = sandbox.__probe.plan();
assert.ok(plan.total >= 10);
const cleared = sandbox.__probe.clean();
assert.equal(cleared, plan.total);
assert.deepEqual(protectedState, { profiles: [{ name: "Keep" }], bookmarks: [{ name: "Keep" }], webhook: "secret", finance: [{ amount: 1 }] });
const state = plain(sandbox.__probe.state());
assert.equal(state.followedVehicleId, "");
assert.equal(state.commandSearchQuery, "");
assert.equal(state.unitLocatorQuery, "");
assert.equal(state.majorIncidentFeedManualPaused, false);
assert.equal(state.notificationSeen, 0);
assert.equal(state.notificationActive, 1, "active alert state must remain armed so cleanup cannot immediately re-notify it");
assert.equal(state.recent, 0);
assert.equal(state.caches, 0);
assert.equal(state.resource.key, "");
assert.equal(state.pressure.snapshot, null);
assert.ok(sandbox.toast.includes("Session cleanup complete"));

console.log("Issue #624 v10.2.3 runtime passed: retained local unit search and allowlisted session cleanup remain operational.");
