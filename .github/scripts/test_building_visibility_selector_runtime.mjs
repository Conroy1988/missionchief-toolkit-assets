#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

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

const dom = new JSDOM(`<!doctype html><html><body>
  <ul id="map_filters">
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_22" value="22" checked> Ambulance Station</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_fire_small" value="firehouse_small_missions"> Fire Station (Small)</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_2" value="2"> Fire Station</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_6" value="6" checked> Police Station</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_hospital" value="4"> Klinik</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_coastguard" value="coastal_rescue_missions"> SAR</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_lifeboat" value="coastal_rescue"> Lifeboat Stations</label></li>
    <li class="filter_list__element building-filter"><label><input type="checkbox" id="filter_complex" value="building_complex"> Building Complex</label></li>
    <li class="filter_list__element"><label><input type="checkbox" id="user_buildings" value="user_buildings" checked> My buildings</label></li>
  </ul>
  <div id="mcms-control"><label class="building-filter"><input type="checkbox" id="fake_fire" value="fire_station"> Fire Station</label></div>
</body></html>`, { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });

const { window } = dom;
window.I18n = {
  t: key => ({ "map_filters.hospital_missions": "Klinik" })[key] || `translation missing: ${key}`,
};
const changeCounts = new Map();
for (const input of window.document.querySelectorAll("#map_filters input")) {
  input.addEventListener("change", () => changeCounts.set(input.id, (changeCounts.get(input.id) || 0) + 1));
}

const descriptors = Object.freeze({
  ambulance: Object.freeze({ label: "Ambulance Stations", icon: "✚", labels: Object.freeze(["Ambulance Station", "Ambulance Stations"]), tokens: Object.freeze(["ambulance_station", "ambulance_stations", "ambulance_station_missions"]), i18n: Object.freeze(["map_filters.ambulance_station_missions"]), buildingTypeIds: Object.freeze([2]), tone: "medical" }),
  police: Object.freeze({ label: "Police Stations", icon: "★", labels: Object.freeze(["Police Station", "Police Stations"]), tokens: Object.freeze(["police_station", "police_stations", "police_station_missions"]), i18n: Object.freeze(["map_filters.police_station_missions"]), buildingTypeIds: Object.freeze([6]), tone: "police" }),
  fire: Object.freeze({ label: "Fire Stations", icon: "◆", labels: Object.freeze(["Fire Station", "Fire Stations"]), tokens: Object.freeze(["fire_station", "fire_stations", "firehouse_missions"]), i18n: Object.freeze(["map_filters.firehouse_missions"]), buildingTypeIds: Object.freeze([0]), tone: "fire" }),
  hospital: Object.freeze({ label: "Hospitals", icon: "H", labels: Object.freeze(["Hospital", "Hospitals"]), tokens: Object.freeze(["hospital", "hospitals", "hospital_missions"]), i18n: Object.freeze(["map_filters.hospital_missions"]), buildingTypeIds: Object.freeze([4]), tone: "medical" }),
  fire_small: Object.freeze({ label: "Small Fire Stations", icon: "◆", labels: Object.freeze(["Fire Station (Small)", "Small Fire Station"]), tokens: Object.freeze(["fire_station_small", "firehouse_small_missions"]), i18n: Object.freeze(["map_filters.firehouse_small_missions"]), buildingTypeIds: Object.freeze([18]), tone: "fire" }),
  coastguard_rescue: Object.freeze({ label: "Coastguard Rescue Stations", icon: "⚓", labels: Object.freeze(["Coastguard Rescue Station", "SAR"]), tokens: Object.freeze(["coastguard_rescue_station", "coastal_rescue_missions"]), i18n: Object.freeze(["map_filters.coastal_rescue_missions"]), buildingTypeIds: Object.freeze([28]), tone: "rescue" }),
  lifeboat: Object.freeze({ label: "Lifeboat Stations", icon: "⚓", labels: Object.freeze(["Lifeboat Station", "Lifeboat Stations"]), tokens: Object.freeze(["lifeboat_station", "coastal_rescue"]), i18n: Object.freeze(["map_filters.coastal_rescue"]), buildingTypeIds: Object.freeze([27]), tone: "rescue" }),
  building_complexes: Object.freeze({ label: "Building Complexes", icon: "▦", labels: Object.freeze(["Building Complex", "Large complex", "Small complex"]), tokens: Object.freeze(["building_complex"]), i18n: Object.freeze(["map_filters.building_complex"]), buildingTypeIds: Object.freeze([23, 24]), tone: "support" }),
});
const order = Object.freeze(["ambulance", "police", "fire", "hospital", "fire_small", "coastguard_rescue", "lifeboat", "building_complexes"]);

const toasts = [];
const analytics = [];
const invalidations = [];
let renders = 0;
let positions = 0;
const sandbox = {
  console,
  Event: window.Event,
  document: window.document,
  pageWindow: window,
  SCRIPT: { controlId: "mcms-control", panelId: "mcms-panel", commandExperienceModalId: "mcms-modal", commandPaletteId: "mcms-palette" },
  NATIVE_BUILDING_QUICK_FILTERS: descriptors,
  NATIVE_BUILDING_QUICK_FILTER_ORDER: order,
  nativeVisibilityWriteDepth: 0,
  showToast: message => toasts.push(message),
  renderNativeBuildingQuickFilterPopover: () => { renders += 1; },
  positionNativeBuildingQuickFilterPopover: () => { positions += 1; },
  invalidateMarkerRegistryCaches: scope => invalidations.push(scope),
  toolkitAnalyticsRecordFeature: (...args) => analytics.push(args),
  escapeHtml: value => String(value).replace(/[&<>'"]/gu, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]),
};

const functionNames = [
  "normaliseNativeVisibilityToken",
  "normaliseNativeVisibilityLabel",
  "nativeVisibilityElementById",
  "nativeVisibilityControlRoots",
  "nativeVisibilityControlBelongsToToolkit",
  "nativeVisibilityControlTokens",
  "nativeVisibilityControlLabel",
  "nativeVisibilityInteractiveControls",
  "nativeVisibilityControlState",
  "dispatchNativeVisibilityControl",
  "nativeBuildingQuickFilterDescriptor",
  "nativeBuildingQuickFilterTranslatedLabels",
  "nativeBuildingQuickFilterControlLabels",
  "nativeBuildingQuickFilterTokenMatches",
  "nativeBuildingQuickFilterControlMatches",
  "nativeBuildingQuickFilterControls",
  "findNativeBuildingQuickFilterControl",
  "nativeBuildingQuickFilterSnapshot",
  "nativeBuildingQuickFilterMarkup",
  "activateNativeBuildingQuickFilter",
];

vm.createContext(sandbox);
vm.runInContext(`${functionNames.map(extractFunction).join("\n\n")}
globalThis.__probe = { ${functionNames.join(",")} };`, sandbox, { filename: "native-building-quick-filter.js" });
const probe = sandbox.__probe;

assert.equal(probe.findNativeBuildingQuickFilterControl("ambulance")?.id, "filter_22");
assert.equal(probe.findNativeBuildingQuickFilterControl("fire")?.id, "filter_2", "Toolkit-owned lookalike must be ignored");
assert.equal(probe.findNativeBuildingQuickFilterControl("fire_small")?.id, "filter_fire_small", "Small station must not be claimed by the main Fire descriptor");
assert.equal(probe.findNativeBuildingQuickFilterControl("police")?.id, "filter_6");
assert.equal(probe.findNativeBuildingQuickFilterControl("hospital")?.id, "filter_hospital", "Live I18n labels must be accepted");
assert.equal(probe.findNativeBuildingQuickFilterControl("coastguard_rescue")?.id, "filter_coastguard");
assert.equal(probe.findNativeBuildingQuickFilterControl("lifeboat")?.id, "filter_lifeboat");
assert.equal(probe.findNativeBuildingQuickFilterControl("building_complexes")?.id, "filter_complex");
assert.equal(probe.findNativeBuildingQuickFilterControl("unknown"), null);
assert.deepEqual(JSON.parse(JSON.stringify(probe.nativeBuildingQuickFilterSnapshot("ambulance"))), {
  available: true,
  enabled: true,
  control: {},
}, "snapshot must report native checked state");

const markup = probe.nativeBuildingQuickFilterMarkup();
assert.equal((markup.match(/data-native-building-filter=/gu) || []).length, order.length, "popup must expose the full supplied UK catalogue");
for (const label of ["Ambulance Stations", "Police Stations", "Fire Stations", "Hospitals", "Coastguard Rescue Stations", "Lifeboat Stations", "Building Complexes"]) assert.ok(markup.includes(label), `${label} missing`);
assert.ok(markup.indexOf("Ambulance Stations") < markup.indexOf("Police Stations"));
assert.ok(markup.indexOf("Police Stations") < markup.indexOf("Fire Stations"));
assert.ok(markup.includes("Most popular"));
assert.ok(markup.includes("All other buildings · popularity order"));
assert.equal((markup.match(/mcms-native-building-featured/gu) || []).length, 3);
assert.equal((markup.match(/data-popularity-rank=/gu) || []).length, order.length);
assert.ok(!markup.includes("My buildings"));

assert.equal(probe.activateNativeBuildingQuickFilter("fire"), true);
assert.equal(window.document.querySelector("#filter_2").checked, true);
assert.equal(changeCounts.get("filter_2"), 1, "MissionChief's native change event must run once");
assert.equal(probe.activateNativeBuildingQuickFilter("fire"), true);
assert.equal(window.document.querySelector("#filter_2").checked, false);
assert.equal(changeCounts.get("filter_2"), 2);
assert.equal(probe.activateNativeBuildingQuickFilter("unknown"), false);

assert.deepEqual(invalidations, ["building", "building"]);
assert.deepEqual(analytics, [
  ["buildingVisibility", "native_building_filter"],
  ["buildingVisibility", "native_building_filter"],
]);
assert.equal(renders, 3);
assert.equal(positions, 2);
assert.equal(toasts.at(-1), "Station filter unavailable · use MissionChief Filters");

dom.window.close();
console.log("Native Building quick-filter runtime passed: popularity order, exact main/small discovery, live translations, Toolkit exclusion, native checkbox events and no custom layer path.");
