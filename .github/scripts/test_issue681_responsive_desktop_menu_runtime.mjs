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

const sandbox = { Math, Number };
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("resolveResponsiveDesktopPanelHeightCap")}\nthis.resolveCap = resolveResponsiveDesktopPanelHeightCap;`, sandbox);
const resolveCap = sandbox.resolveCap;
const defaults = { panelWidth: 720, panelHeight: 82 };

assert.equal(resolveCap({ width: 1688, height: 1266 }, defaults), 760, "supplied screenshot did not receive the compact height cap");
assert.equal(resolveCap({ width: 1440, height: 900 }, defaults), 760, "1440×900 did not use the compact Desktop surface");
assert.equal(resolveCap({ width: 1366, height: 768 }, defaults), Infinity, "short Desktop viewport should retain the existing proportional safety sizing");
assert.equal(resolveCap({ width: 2560, height: 1440 }, defaults), Infinity, "wide Desktop geometry changed unexpectedly");
assert.equal(resolveCap({ width: 1688, height: 1266 }, { panelWidth: 880, panelHeight: 82 }), Infinity, "custom Desktop width was overridden");
assert.equal(resolveCap({ width: 1688, height: 1266 }, { panelWidth: 720, panelHeight: 96 }), Infinity, "custom Desktop height was overridden");

console.log("Issue #681 responsive Desktop menu geometry regression passed.");
