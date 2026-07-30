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
  /data-mcms-tablet-active="true"[\s\S]*?\.mcms-drag-handle\s*\{[\s\S]*?min-height:44px !important;[\s\S]*?touch-action:none !important;/u,
  "Tablet drag handle is not a 44px touch target with direct drag gesture ownership",
);
assert.match(
  source,
  /data-mcms-tablet-active="true"[\s\S]*?\.mcms-header-grip\s*\{[\s\S]*?width:44px !important;[\s\S]*?height:44px !important;/u,
  "Tablet grip is not a 44×44 touch target",
);
assert.match(
  source,
  /data-mcms-tablet-active="true"[\s\S]*?\.mcms-command-layout\s*\{\s*grid-template-columns:160px minmax\(0,1fr\) !important;/u,
  "Tablet command navigation rail is still too narrow",
);
assert.match(
  source,
  /\.mcms-tab-copy strong\s*\{[\s\S]*?font-size:11px !important;[\s\S]*?white-space:normal !important;[\s\S]*?overflow:visible !important;/u,
  "Tablet section labels are still clipped or ellipsised",
);
assert.match(
  source,
  /data-mcms-mobile-active="true"[\s\S]*?\.mcms-header-grip\s*\{\s*display:none !important;\s*\}/u,
  "Mobile fixed-sheet behavior must remain unchanged",
);

const startPanelDrag = extractFunction("startPanelDrag");
assert.doesNotMatch(startPanelDrag, /isTouchLayoutActive/u, "Tablet dragging is still blocked by the touch-layout guard");
assert.match(startPanelDrag, /if \(mobileModeActive\) return;/u, "Mobile fixed-sheet drag guard was removed");

assert.match(
  source,
  /makeFloatButton\('stuckDetector', '', 'Stuck'/u,
  "Stuck overlay was not restored to the main map command bar",
);
assert.match(
  source,
  /const controlToggleValues = \{[\s\S]*?stuckDetector: state\.stuckDetector\.enabled,[\s\S]*?\};/u,
  "Stuck map control is not synchronized with the detector state",
);
assert.match(
  source,
  /makeToggleButton\('stuckDetector',[\s\S]*?'Stuck Detect'/u,
  "Stuck overlay setting disappeared from the Missions menu",
);
assert.doesNotMatch(
  source,
  /['"]9['"]\s*:\s*['"]stuckDetector['"]/u,
  "Stuck overlay introduced an unapproved keyboard shortcut",
);

const sandbox = {
  MAP_CONTROL_ICONS: {
    stuckDetector: "!",
  },
  escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  },
  clamp(value, minimum, maximum, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.max(minimum, Math.min(maximum, number)) : fallback;
  },
};
vm.createContext(sandbox);
vm.runInContext(`
${extractFunction("makeFloatButton")}
${extractFunction("clampTabletPanelPoint")}
this.__probe = {
  button: makeFloatButton("stuckDetector", "", "Stuck", "Toggle Stuck"),
  clamp: clampTabletPanelPoint,
};
`, sandbox, { filename: "issue604-tablet-controls-runtime.js" });

assert.match(sandbox.__probe.button, /data-toggle="stuckDetector"/u);
assert.match(sandbox.__probe.button, />Stuck</u);
assert.match(sandbox.__probe.button, /mcms-control-state">OFF</u);
assert.doesNotMatch(sandbox.__probe.button, /aria-keyshortcuts/u, "Stuck button advertises a nonexistent shortcut");

assert.equal(
  JSON.stringify(sandbox.__probe.clamp(-500, -500, 700, 500, { offsetLeft: 12, offsetTop: 20, width: 1024, height: 768 }, 10)),
  JSON.stringify({ left: 22, top: 30 }),
  "Tablet drag did not clamp to the visible viewport origin",
);
assert.equal(
  JSON.stringify(sandbox.__probe.clamp(2000, 2000, 700, 500, { offsetLeft: 12, offsetTop: 20, width: 1024, height: 768 }, 10)),
  JSON.stringify({ left: 326, top: 278 }),
  "Tablet drag did not clamp to the visible viewport edge",
);

console.log("Issue #604 Tablet controls passed: readable rail, 44px grip, movable panel, mobile guard, Stuck map toggle and viewport clamping.");
