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

let prevented = 0;
let rendered = 0;
let updated = 0;
let draggingEnabled = true;
const mapMeasureRuntime = {
  mode: "freehand",
  active: true,
  freehandDrawing: true,
  points: [{ lat: 55.95, lng: -3.19 }],
  lastContainerPoint: { x: 10, y: 10 },
  draggingWasEnabled: null,
  map: {
    dragging: {
      enabled() { return draggingEnabled; },
      disable() { draggingEnabled = false; },
      enable() { draggingEnabled = true; },
    },
  },
};
const sandbox = {
  MAP_MEASURE_EARTH_RADIUS_METRES: 6371008.8,
  MAP_DRAWING_MAX_FREEHAND_POINTS: 160,
  MAP_DRAWING_FREEHAND_SAMPLE_PIXELS: 6,
  mapMeasureRuntime,
  renderMapMeasureLayers() { rendered += 1; },
  updateMapMeasureHud() { updated += 1; },
};
vm.createContext(sandbox);
vm.runInContext([
  "mapMeasureRadians",
  "mapMeasurePointDistance",
  "mapMeasureLineDistance",
  "mapMeasureArea",
  "mapMeasureFormatDistance",
  "mapMeasureFormatArea",
  "mapDrawingPoint",
  "mapDrawingRectanglePoints",
  "mapDrawingBearing",
  "mapDrawingPrepareFreehand",
  "mapDrawingRestoreDragging",
  "mapDrawingHandleFreehandMove",
].map(extractFunction).join("\n\n") + `
globalThis.__drawing = {
  rectangle: mapDrawingRectanglePoints,
  bearing: mapDrawingBearing,
  move: mapDrawingHandleFreehandMove,
  prepare: mapDrawingPrepareFreehand,
  restore: mapDrawingRestoreDragging,
};`, sandbox);

const api = sandbox.__drawing;
const rectangle = Array.from(api.rectangle([{ lat: 55, lng: -4 }, { lat: 56, lng: -3 }]), point => ({ ...point }));
assert.deepEqual(rectangle, [
  { lat: 55, lng: -4 }, { lat: 55, lng: -3 }, { lat: 56, lng: -3 }, { lat: 56, lng: -4 },
]);
assert.ok(Math.abs(api.bearing({ lat: 0, lng: 0 }, { lat: 1, lng: 0 })) < 0.001);
assert.ok(Math.abs(api.bearing({ lat: 0, lng: 0 }, { lat: 0, lng: 1 }) - 90) < 0.001);

api.move({ latlng: { lat: 55.95001, lng: -3.19001 }, containerPoint: { x: 14, y: 13 }, originalEvent: { preventDefault() { prevented += 1; } } });
assert.equal(mapMeasureRuntime.points.length, 1, "sub-six-pixel freehand noise must be ignored");
api.move({ latlng: { lat: 55.9501, lng: -3.1901 }, containerPoint: { x: 17, y: 10 }, originalEvent: { preventDefault() { prevented += 1; } } });
assert.equal(mapMeasureRuntime.points.length, 2);
assert.equal(prevented, 1);
assert.equal(rendered, 1);
assert.equal(updated, 1);

mapMeasureRuntime.freehandDrawing = false;
api.prepare();
assert.equal(draggingEnabled, false);
assert.equal(mapMeasureRuntime.draggingWasEnabled, true);
api.restore();
assert.equal(draggingEnabled, true);
assert.equal(mapMeasureRuntime.draggingWasEnabled, null);

console.log("Issue #677 Drawing runtime passed: rectangle and arrow geometry, freehand thresholding and native-drag restoration are deterministic.");
