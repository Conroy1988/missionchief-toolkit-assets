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
    if (char === "'" || char === '"') { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

function marker(id, userId, typeId) {
  return {
    id,
    record: { id, user_id: userId, building_type: typeId },
    options: { opacity: 1 },
    opacity: 1,
    setOpacity(value) { this.opacity = value; this.options.opacity = value; },
  };
}

function target(name, child) {
  return {
    name,
    isTarget: true,
    children: new Set([child]),
    addLayer(layer) { this.children.add(layer); },
    hasLayer(layer) { return this.children.has(layer); },
  };
}

const ownFire = marker("own-fire", 7, 1);
const ownPolice = marker("own-police", 7, 6);
const allianceFire = marker("alliance-fire", 99, 1);
const alliancePolice = marker("alliance-police", 99, 6);
const ownFireTarget = target("own-fire", ownFire);
const ownPoliceTarget = target("own-police", ownPolice);
const allianceFireTarget = target("alliance-fire", allianceFire);
const alliancePoliceTarget = target("alliance-police", alliancePolice);
for (const [layer, nativeTarget] of [
  [ownFire, ownFireTarget],
  [ownPolice, ownPoliceTarget],
  [allianceFire, allianceFireTarget],
  [alliancePolice, alliancePoliceTarget],
]) layer.target = nativeTarget;

const map = {
  layers: new Set(),
  hasLayer(layer) { return this.layers.has(layer); },
  addLayer(layer) {
    this.layers.add(layer);
    if (layer.isTarget) for (const child of layer.children) this.layers.add(child);
  },
  removeLayer(layer) {
    this.layers.delete(layer);
    if (layer.isTarget) for (const child of layer.children) this.layers.delete(child);
  },
};

for (const nativeTarget of [ownFireTarget, ownPoliceTarget, allianceFireTarget]) map.addLayer(nativeTarget);

const layers = [ownFire, ownPolice, allianceFire, alliancePolice];
const nativeEntries = layers.map(layer => ({
  target: layer.target,
  layer,
  record: layer.record,
  typeId: String(layer.record.building_type),
  scope: layer.record.user_id === 7 ? "own" : "alliance",
}));

const sandbox = {
  state: {
    visibility: { buildings: true },
    buildingVisibility: { scope: "own", mode: "selected", selectedTypeIds: ["1"] },
  },
  currentUserIdCached: () => "7",
  getBuildingRecordForLayer: layer => layer?.record || null,
  isAllianceBuildingLayer: (layer, record) => String(record?.user_id ?? layer?.record?.user_id) !== "7",
  getBuildingMarkerLayers: () => layers,
  buildingVisibilityNativeTargetEntries: () => nativeEntries,
  resolveNativeBuildingFilterTarget: layer => layer?.target || null,
  attachAllianceBuildingToNativeFilterTarget: (layer, nativeTarget) => nativeTarget?.addLayer?.(layer),
  nativeBuildingFilterTargetIsVisible: (leafletMap, nativeTarget) => leafletMap.hasLayer(nativeTarget),
  findLeafletMapInstance: () => map,
};

vm.createContext(sandbox);
const declarations = `
const hiddenBuildingVisibilityLayers = new Set();
const buildingVisibilityLayerOpacity = new Map();
const buildingVisibilityManagedTargets = new Map();
let enforcingBuildingVisibility = false;
`;
const functions = [
  "buildingVisibilityTypeId",
  "buildingVisibilityOwnerScope",
  "buildingVisibilityLayerAllowed",
  "nativeBuildingVisibilityDesired",
  "setBuildingVisibilityTarget",
  "hideBuildingVisibilityLayer",
  "restoreBuildingVisibilityLayer",
  "synchroniseBuildingVisibilitySelector",
  "buildingVisibilityFilterIsCustom",
  "releaseBuildingVisibilitySelector",
];
vm.runInContext(`${declarations}\n${functions.map(extractFunction).join("\n")}\nglobalThis.__probe = { ${functions.join(",")}, hiddenBuildingVisibilityLayers, buildingVisibilityManagedTargets };`, sandbox);

const probe = sandbox.__probe;
assert.equal(probe.buildingVisibilityTypeId(ownFire, ownFire.record), "1");
assert.equal(probe.buildingVisibilityOwnerScope(ownFire, ownFire.record), "own");
assert.equal(probe.buildingVisibilityOwnerScope(allianceFire, allianceFire.record), "alliance");
assert.equal(probe.buildingVisibilityLayerAllowed(ownFire, ownFire.record), true);
assert.equal(probe.buildingVisibilityLayerAllowed(ownPolice, ownPolice.record), false);
assert.equal(probe.buildingVisibilityLayerAllowed(allianceFire, allianceFire.record), false);
assert.equal(probe.nativeBuildingVisibilityDesired(), true);
assert.equal(probe.buildingVisibilityFilterIsCustom(), true);

probe.synchroniseBuildingVisibilitySelector(map);
assert.equal(map.hasLayer(ownFireTarget), true);
assert.equal(map.hasLayer(ownFire), true);
assert.equal(map.hasLayer(ownPoliceTarget), false);
assert.equal(map.hasLayer(ownPolice), false);
assert.equal(map.hasLayer(allianceFireTarget), false);
assert.equal(map.hasLayer(allianceFire), false);
assert.equal(map.hasLayer(alliancePoliceTarget), false);
assert.equal(ownPolice.opacity, 0);
assert.equal(allianceFire.opacity, 0);
assert.equal(probe.hiddenBuildingVisibilityLayers.size, 3);

sandbox.state.buildingVisibility.scope = "both";
probe.synchroniseBuildingVisibilitySelector(map);
assert.equal(map.hasLayer(allianceFireTarget), true, "selected alliance type should be restored when Both is chosen");
assert.equal(map.hasLayer(allianceFire), true);
assert.equal(allianceFire.opacity, 1);
assert.equal(map.hasLayer(ownPolice), false, "unselected type must stay hidden across ownership scopes");

sandbox.state.visibility.buildings = false;
assert.equal(probe.nativeBuildingVisibilityDesired(), false);
probe.synchroniseBuildingVisibilitySelector(map);
assert.equal(layers.some(layer => map.hasLayer(layer)), false, "master off must hide every building");

sandbox.state.visibility.buildings = true;
sandbox.state.buildingVisibility = { scope: "alliance", mode: "all", selectedTypeIds: [] };
assert.equal(probe.nativeBuildingVisibilityDesired(), false, "Alliance-only mode must not be mistaken for native My Buildings off");
probe.synchroniseBuildingVisibilitySelector(map);
assert.equal(map.hasLayer(ownFire), false);
assert.equal(map.hasLayer(allianceFire), true);
assert.equal(map.hasLayer(alliancePoliceTarget), true, "a target originally off may be enabled while managed");
assert.equal(map.hasLayer(alliancePolice), true);

probe.releaseBuildingVisibilitySelector(map);
assert.equal(map.hasLayer(ownFireTarget), true, "teardown restores originally visible targets");
assert.equal(map.hasLayer(ownPoliceTarget), true);
assert.equal(map.hasLayer(allianceFireTarget), true);
assert.equal(map.hasLayer(alliancePoliceTarget), false, "teardown restores originally hidden targets");
assert.equal(probe.buildingVisibilityManagedTargets.size, 0);

console.log("Building Visibility Selector runtime passed: type, ownership, master toggle, native targets, fallback layers and teardown restoration.");
