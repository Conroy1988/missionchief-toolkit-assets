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
  const brace = source.indexOf("{", start);
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

const sandbox = { Math, Number, Array };
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("resolveDesktopDockGrid")}\nthis.resolveGrid = resolveDesktopDockGrid;`, sandbox);
const resolveGrid = sandbox.resolveGrid;

const scenarios = [
  { name: "2560x1440", width: 2200, height: 1080, columns: 4, size: "wide" },
  { name: "1920x1080", width: 1700, height: 780, columns: 4, size: "wide" },
  { name: "1366x768", width: 1200, height: 520, columns: 4, size: "wide" },
  { name: "1024x768", width: 900, height: 520, columns: 3, size: "standard" },
  { name: "603px forced Desktop", width: 564, height: 700, columns: 2, size: "compact" },
  { name: "480px forced Desktop", width: 440, height: 700, columns: 1, size: "tight" },
];

for (const scenario of scenarios) {
  const grid = resolveGrid(scenario.width, scenario.height, [4, 5, 3, 1], 4, 117, 6);
  assert.ok(grid.dockWidth > 240, `${scenario.name} retained the old narrow column`);
  assert.ok(grid.dockWidth <= scenario.width, `${scenario.name} exceeded the visible map width`);
  assert.equal(grid.groupColumns, scenario.columns, `${scenario.name} chose the wrong group grid`);
  assert.ok(grid.groupWidth > 0, `${scenario.name} lost its command-group width`);
  if (scenario.columns >= 3) {
    assert.ok(grid.groupWidth <= 210, `${scenario.name} spread command groups beyond the compact Desktop track`);
    assert.equal(
      grid.contentWidth,
      (grid.groupWidth * grid.groupColumns) + (6 * (grid.groupColumns - 1)),
      `${scenario.name} left unused horizontal space inside the command cluster`,
    );
  }
  if (scenario.width >= 1200) assert.ok(grid.dockWidth <= 981, `${scenario.name} retained the over-wide Desktop deck`);
  assert.equal(grid.size, scenario.size, `${scenario.name} chose the wrong density tier`);
  assert.equal(grid.scrollFallback, false, `${scenario.name} scrolls during normal use`);
  assert.ok(grid.groupButtonColumns.every(columns => columns >= 1), `${scenario.name} produced an empty button grid`);
  assert.ok(grid.filterMaxHeight >= grid.naturalFilterHeight, `${scenario.name} clipped its command groups`);
  assert.ok(grid.pinMaxHeight >= grid.naturalPinHeight, `${scenario.name} clipped its pinned shortcuts`);
}

const short = resolveGrid(900, 145, [4, 5, 3, 1], 8, 117, 6);
assert.equal(short.scrollFallback, true, "emergency scroll fallback was not enabled for a short map");
assert.ok(short.filterMaxHeight < short.naturalFilterHeight, "short-map filter was not bounded");
assert.ok(short.filterMaxHeight + short.pinMaxHeight + short.pinMargin <= 145, "short-map deck exceeded its safe height");

for (const scale of [0.8, 1, 1.25, 1.5, 2]) {
  const availableWidth = Math.max(360, Math.floor(1280 / scale));
  const availableHeight = Math.max(180, Math.floor(620 / scale));
  const grid = resolveGrid(availableWidth, availableHeight, [4, 5, 3, 1], 4, 117, 6);
  assert.ok(grid.dockWidth <= availableWidth, `${scale * 100}% zoom overflowed horizontally`);
  assert.ok(grid.filterMaxHeight + grid.pinMaxHeight + grid.pinMargin <= availableHeight, `${scale * 100}% zoom overflowed vertically`);
  assert.ok(grid.contentWidth > 0, `${scale * 100}% zoom lost the command workspace`);
}

console.log("Issue #645 adaptive Desktop command workspace runtime regression passed.");
