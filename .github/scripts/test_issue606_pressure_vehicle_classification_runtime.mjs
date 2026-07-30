#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const catalogueSource = JSON.parse(fs.readFileSync("src/data/mission-requirements-en_GB.json", "utf8"));
const fixture = JSON.parse(fs.readFileSync(".github/fixtures/issue606-pressure-vehicle-classification.json", "utf8"));

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const candidates = [
    source.indexOf("\n    function ", start + marker.length),
    source.indexOf("\n    async function ", start + marker.length),
    source.indexOf("\n    const ", start + marker.length),
  ].filter(index => index >= 0);
  const end = Math.min(...candidates);
  assert.ok(Number.isFinite(end), `Unable to find the end of ${name}`);
  return source.slice(start, end).trim();
}

const catalogueStart = source.indexOf("    const UK_VEHICLE_REQUIREMENT_CATALOGUE");
const catalogueEnd = source.indexOf("\n    function resourceSearchToken", catalogueStart);
assert.ok(catalogueStart >= 0 && catalogueEnd > catalogueStart, "embedded UK vehicle catalogue is missing");
const catalogueBlock = source.slice(catalogueStart, catalogueEnd).trim();

const sandbox = { console };
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("normaliseSearchText")}
${catalogueBlock}
${[
  "resourceSearchToken",
  "requirementSearchParts",
  "preparedVehicleMatchesRequirement",
  "haversineMiles",
  "operationalPressureRequirementKey",
  "formatOperationalPressureDuration",
  "calculateOperationalPressureModel",
  "vehicleTypeIdFromRecord",
].map(extractFunction).join("\n")}
this.__probe = {
  catalogue: UK_VEHICLE_REQUIREMENT_CATALOGUE,
  normalise: normaliseSearchText,
  token: resourceSearchToken,
  parts: requirementSearchParts,
  matches: preparedVehicleMatchesRequirement,
  model: calculateOperationalPressureModel,
  typeId: vehicleTypeIdFromRecord
};`, sandbox, { filename: "issue606-pressure-vehicle-classification-runtime.js" });

const normalise = value => sandbox.__probe.normalise(value);
const expectedCatalogue = catalogueSource.vehicleRequirements.map(row => [
  row.key,
  row.types,
  row.aliases.map(normalise),
]);
assert.deepEqual(
  JSON.parse(JSON.stringify(sandbox.__probe.catalogue)),
  JSON.parse(JSON.stringify(expectedCatalogue)),
  "embedded userscript catalogue drifted from src/data/mission-requirements-en_GB.json",
);

function preparedVehicle(vehicle) {
  const signal = normalise(vehicle.signal);
  const classificationSignal = normalise(vehicle.classificationSignal);
  return {
    id: vehicle.id,
    typeId: vehicle.typeId,
    signal,
    tokens: new Set(signal.split(/\s+/u).map(sandbox.__probe.token).filter(Boolean)),
    classificationSignal,
    classificationTokens: new Set(classificationSignal.split(/\s+/u).map(sandbox.__probe.token).filter(Boolean)),
    point: Number.isFinite(vehicle.lat) && Number.isFinite(vehicle.lng)
      ? { lat: vehicle.lat, lng: vehicle.lng }
      : null,
  };
}

for (const item of fixture.matchingCases) {
  const actual = sandbox.__probe.matches(preparedVehicle({ id: item.requirement, ...item }), sandbox.__probe.parts(item.requirement));
  assert.equal(actual, item.expected, `${item.requirement} type ${item.typeId} classification result`);
}

assert.equal(sandbox.__probe.typeId({ vehicle_type: 0 }), 0);
assert.equal(sandbox.__probe.typeId({ options: { vehicleTypeId: "116" } }), 116);
assert.equal(sandbox.__probe.typeId({ data: { vehicle_type_id: 5 } }), 5);
assert.equal(sandbox.__probe.typeId({ caption: "No numeric type" }), null);

const mixed = sandbox.__probe.model(
  fixture.mixedModel.missions,
  { available: fixture.mixedModel.availableVehicles.map(preparedVehicle) },
  {
    now: fixture.mixedModel.now,
    radiusMi: fixture.mixedModel.radiusMi,
    missionReady: true,
    vehicleReady: true,
  },
);
for (const [key, expected] of Object.entries(fixture.mixedModel.expected)) {
  if (key === "severity") assert.equal(mixed.severity, expected);
  else assert.equal(mixed.resourcePressure[key], expected, `mixed model ${key}`);
}
assert.equal(mixed.complete, false, "unlocated matched vehicle must make radius evidence partial");
const ambulance = mixed.resourcePressure.groups.find(group => group.key === "ambulance");
assert.ok(ambulance, "canonical Ambulance group is missing");
assert.equal(ambulance.available, 2, "recognised Ambulance capacity was discarded");
assert.equal(ambulance.confirmedAvailable, 1);
assert.equal(ambulance.unlocated, 1);
assert.equal(ambulance.assigned, 1);
assert.equal(ambulance.unverified, 1);
assert.equal(ambulance.shortfall, 0);
assert.match(mixed.summary, /need location evidence/u);

const unknownMissionLocation = sandbox.__probe.model([
  {
    missionId: "unknown-mission-location",
    caption: "Unknown mission location",
    source: "personal",
    unitsTotal: 1,
    createdAt: fixture.mixedModel.now,
    requirements: [{ name: "Police car", count: 1 }],
  },
], { available: [preparedVehicle({ id: "police-known", typeId: 8, signal: "Zulu One", lat: 51.5, lng: -0.12 })] }, {
  now: fixture.mixedModel.now,
  radiusMi: 25,
  missionReady: true,
  vehicleReady: true,
});
assert.equal(unknownMissionLocation.resourcePressure.assigned, 0);
assert.equal(unknownMissionLocation.resourcePressure.unverifiedLocation, 1);
assert.equal(unknownMissionLocation.resourcePressure.shortfall, 0);
assert.equal(unknownMissionLocation.resourcePressure.groups[0].available, 1);
assert.equal(unknownMissionLocation.resourcePressure.groups[0].confirmedAvailable, 0);

const outsideRadius = sandbox.__probe.model([
  {
    missionId: "outside-radius",
    caption: "Outside radius",
    source: "personal",
    unitsTotal: 1,
    createdAt: fixture.mixedModel.now,
    requirements: [{ name: "Ambulance", count: 1 }],
    lat: 51.5074,
    lng: -0.1278,
  },
], { available: [preparedVehicle({ id: "ambulance-far", typeId: 5, signal: "Remote Medic", lat: 55.9533, lng: -3.1883 })] }, {
  now: fixture.mixedModel.now,
  radiusMi: 25,
  missionReady: true,
  vehicleReady: true,
});
assert.equal(outsideRadius.resourcePressure.assigned, 0);
assert.equal(outsideRadius.resourcePressure.unverifiedLocation, 0);
assert.equal(outsideRadius.resourcePressure.shortfall, 1);
assert.equal(outsideRadius.resourcePressure.groups[0].available, 1);
assert.equal(outsideRadius.resourcePressure.groups[0].confirmedAvailable, 0);
assert.equal(outsideRadius.resourcePressure.groups[0].outsideRadius, 1);

const oneVehicleTwoMissions = sandbox.__probe.model([
  {
    missionId: "one",
    caption: "One",
    source: "personal",
    unitsTotal: 1,
    createdAt: fixture.mixedModel.now,
    requirements: [{ name: "Fire engine", count: 1 }],
    lat: 51.5074,
    lng: -0.1278,
  },
  {
    missionId: "two",
    caption: "Two",
    source: "personal",
    unitsTotal: 1,
    createdAt: fixture.mixedModel.now,
    requirements: [{ name: "Fire engines", count: 1 }],
    lat: 51.5075,
    lng: -0.1279,
  },
], { available: [preparedVehicle({ id: "single-pump", typeId: 0, signal: "Pump 01", lat: 51.506, lng: -0.13 })] }, {
  now: fixture.mixedModel.now,
  radiusMi: 25,
  missionReady: true,
  vehicleReady: true,
});
assert.equal(oneVehicleTwoMissions.resourcePressure.assigned, 1);
assert.equal(oneVehicleTwoMissions.resourcePressure.shortfall, 1);
assert.equal(oneVehicleTwoMissions.resourcePressure.allocatedVehicles, 1);
assert.equal(oneVehicleTwoMissions.fleetConflicts.length, 1, "canonical aliases did not share one pressure group");

console.log("Issue #606 runtime passed: numeric UK vehicle types, custom classification fallback, callsign safety, one-vehicle allocation and partial location evidence.");
