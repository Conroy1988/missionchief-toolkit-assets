#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const match = new RegExp(`\\bfunction\\s+${name}\\s*\\(`, "u").exec(source);
  assert.ok(match, `${name} is missing`);
  const start = match.index;
  const brace = source.indexOf("{", source.indexOf("(", start));
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === "'" || character === '"' || character === "`") { quote = character; continue; }
    if (character === "{") depth += 1;
    if (character === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const sandbox = {
  MAP_MEASURE_EARTH_RADIUS_METRES: 6371008.8,
  mapMeasureRuntime: { points: [], mode: "distance" },
};
vm.createContext(sandbox);
vm.runInContext([
  "mapMeasureRadians",
  "mapMeasurePointDistance",
  "mapMeasureLineDistance",
  "mapMeasureArea",
  "mapMeasureFormatDistance",
  "mapMeasureFormatArea",
].map(extractFunction).join("\n\n") + `
globalThis.__measure = {
  point: mapMeasurePointDistance,
  line: mapMeasureLineDistance,
  area: mapMeasureArea,
  formatDistance: mapMeasureFormatDistance,
  formatArea: mapMeasureFormatArea,
};`, sandbox);

const api = sandbox.__measure;
const oneDegree = api.point({ lat: 0, lng: 0 }, { lat: 0, lng: 1 });
assert.ok(oneDegree > 111190 && oneDegree < 111200, oneDegree);
assert.equal(api.line([{ lat: 0, lng: 0 }]), 0);
assert.ok(Math.abs(api.line([{ lat: 0, lng: 0 }, { lat: 0, lng: 1 }, { lat: 1, lng: 1 }]) - (oneDegree * 2)) < 30);
const squareArea = api.area([{ lat: 0, lng: 0 }, { lat: 0, lng: 1 }, { lat: 1, lng: 1 }, { lat: 1, lng: 0 }]);
assert.ok(squareArea > 12.35e9 && squareArea < 12.37e9, squareArea);
assert.equal(api.formatDistance(1609.344), "1.61 km");
assert.equal(api.formatDistance(1000), "1 km");
assert.equal(api.formatDistance(125), "0.125 km");
assert.equal(api.formatArea(10000), "0.01 km²");
assert.equal(api.formatArea(1250000), "1.25 km²");

console.log("Issue #673 Map Measure runtime passed: kilometre distance, route and spherical boundary calculations remain deterministic.");
