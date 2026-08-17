#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
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
    if (char === "'" || char === '"' || char === "`") {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

assert.match(
  source,
  /data-mcms-tablet-active="true"\] #\$\{SCRIPT\.pressureBoardId\} \{[\s\S]*?--mcms-pressure-board-resolved-top:max\([\s\S]*?--mcms-pressure-board-workspace-top,62px[\s\S]*?top:var\(--mcms-pressure-board-resolved-top\) !important;/u,
  "Tablet Pressure Board does not resolve its top edge from the map workspace",
);
assert.match(
  source,
  /max-height:calc\([\s\S]*?--mcms-visual-height,100dvh[\s\S]*?--mcms-pressure-board-resolved-top[\s\S]*?safe-area-inset-bottom/u,
  "Tablet Pressure Board height does not account for its resolved top and bottom safe area",
);
assert.match(
  source,
  /data-mcms-mobile-active="true"\] #\$\{SCRIPT\.pressureBoardId\} \{[\s\S]*?top:auto !important;[\s\S]*?bottom:0 !important;/u,
  "Mobile Pressure Board is no longer a fixed bottom sheet",
);
assert.match(
  extractFunction("refreshTouchViewportLayout"),
  /if\(operationalPressureBoardOpen\(\)\)positionOperationalPressureBoard\(\)/u,
  "Pressure Board is not repositioned when the touch viewport changes",
);
assert.match(
  extractFunction("openOperationalIntelligenceView"),
  /board\.classList\.add\('mcms-open'\);[\s\S]*?positionOperationalPressureBoard\(board\);/u,
  "Pressure Board is not positioned when it opens",
);
assert.match(
  extractFunction("toggleOperationalPressureBoard"),
  /openOperationalIntelligenceView\('live'\)/u,
  "The B shortcut no longer delegates to the positioned Live Pressure view",
);

const properties = new Map();
const board = {
  style: {
    getPropertyValue(name) {
      return properties.get(name) || "";
    },
    setProperty(name, value) {
      properties.set(name, value);
    },
    removeProperty(name) {
      properties.delete(name);
    },
  },
};
const viewport = { offsetLeft: 0, offsetTop: 0, width: 730, height: 1200 };
const mapEl = {
  getBoundingClientRect() {
    return { left: 0, right: 730, top: 53, bottom: 1200 };
  },
};
const sandbox = {
  tabletModeActive: true,
  mobileModeActive: false,
  getViewportMetrics() {
    return viewport;
  },
  getLargestLeafletMap() {
    return mapEl;
  },
  operationalPressureBoardElement() {
    return board;
  },
};
vm.createContext(sandbox);
vm.runInContext(`
${extractFunction("setRootStylePropertyIfChanged")}
${extractFunction("resolveDesktopPanelBounds")}
${extractFunction("resolveOperationalPressureBoardTabletGeometry")}
${extractFunction("positionOperationalPressureBoard")}
this.__probe = {
  resolve: resolveOperationalPressureBoardTabletGeometry,
  position: positionOperationalPressureBoard,
};
`, sandbox, { filename: "issue608-pressure-board-tablet-geometry.js" });

const portrait = sandbox.__probe.resolve(viewport, mapEl);
assert.equal(JSON.stringify(portrait), JSON.stringify({ top: 76, maxHeight: 1114 }));
assert.ok(portrait.top > 53, "Tablet board still overlaps the MissionChief header");

const positioned = sandbox.__probe.position(board, viewport);
assert.equal(JSON.stringify(positioned), JSON.stringify(portrait));
assert.equal(properties.get("--mcms-pressure-board-workspace-top"), "76px");

const landscapeViewport = { offsetLeft: 0, offsetTop: 20, width: 1024, height: 748 };
const landscapeMap = {
  getBoundingClientRect() {
    return { left: 0, right: 1024, top: 70, bottom: 768 };
  },
};
const landscape = sandbox.__probe.resolve(landscapeViewport, landscapeMap);
assert.equal(JSON.stringify(landscape), JSON.stringify({ top: 82, maxHeight: 676 }));
assert.ok(landscape.top > 70, "Visual-viewport offset did not preserve header clearance");

sandbox.tabletModeActive = false;
assert.equal(sandbox.__probe.position(board, viewport), null);
assert.equal(properties.has("--mcms-pressure-board-workspace-top"), false, "Desktop mode retained Tablet geometry");

console.log("Issue #608 passed: Tablet Pressure Board clears native top chrome, tracks visual viewport and preserves Mobile/Desktop geometry.");
