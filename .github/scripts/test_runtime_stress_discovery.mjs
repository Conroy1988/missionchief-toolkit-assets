#!/usr/bin/env node
"use strict";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildRuntimeStressPlan, discoverRuntimeContracts } from "./audit_runtime_stress.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const fixture = `
node --check src/toolkit.user.js
node .github/scripts/test_alpha_runtime.js
node .github/scripts/test_beta_runtime.mjs --flag
python3 .github/scripts/test_not_runtime.py
node .github/scripts/test_alpha_runtime.js
 echo node .github/scripts/test_not_a_command.js
`;
assert.deepEqual(discoverRuntimeContracts(fixture), [
  ".github/scripts/test_alpha_runtime.js",
  ".github/scripts/test_beta_runtime.mjs",
]);
assert.throws(() => discoverRuntimeContracts("python3 test.py\n"), /no Node runtime contracts/u);
const fixturePlan = buildRuntimeStressPlan(fixture, 3);
assert.deepEqual(fixturePlan.slice(0, 2), [
  [".github/scripts/test_alpha_runtime.js", 3],
  [".github/scripts/test_beta_runtime.mjs", 3],
]);
assert.deepEqual(fixturePlan.at(-1), [".github/scripts/test_ui_mount_integration.mjs", 16]);

const preflight = fs.readFileSync(path.join(root, ".github/scripts/run_userscript_preflight.sh"), "utf8");
const independentlyParsed = preflight.split(/\r?\n/u)
  .map(line => line.trim().split(/\s+/u))
  .filter(parts => parts[0] === "node" && /^\.github\/scripts\/test_.+\.(?:js|mjs)$/u.test(parts[1] || ""))
  .map(parts => parts[1]);
const discovered = discoverRuntimeContracts(preflight);
assert.deepEqual(discovered, [...new Set(independentlyParsed)]);
assert.ok(discovered.includes(".github/scripts/test_issue564_incident_feed_attended_runtime.js"));
const realPlan = buildRuntimeStressPlan(preflight, 8);
assert.equal(realPlan.filter(([test]) => test === ".github/scripts/test_ui_mount_integration.mjs").length, 1);
assert.equal(realPlan.reduce((sum, [, repeats]) => sum + repeats, 0), (discovered.length * 8) + 16);
console.log(`Runtime-stress discovery contract passed with ${discovered.length} canonical contracts and ${realPlan.reduce((sum, [, repeats]) => sum + repeats, 0)} planned executions.`);
