#!/usr/bin/env node
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const start = source.indexOf("    // <mcms-alliance-member-manager>");
const end = source.indexOf("    // </mcms-alliance-member-manager>", start);
const block = source.slice(start, end);
assert.ok(start >= 0 && end > start);
assert.ok(block.includes("disposeAllianceMemberManager();"));
assert.ok(!block.includes("teardownAllianceMemberManager"));
assert.ok(block.includes("allianceMemberManagerEnsureMountObserver"));
assert.ok(block.includes("!allianceMemberManagerHasDomContext()"));
assert.ok(block.includes("Member route found; waiting for a confirmed member view"));
assert.ok(block.includes("characterData: true"));
assert.ok(block.includes("pageWindow.__MCMS_UI_MOUNTS__"));
assert.ok(block.includes("GM_getValue"));
assert.ok(block.includes("GM_setValue"));
console.log("Alliance Member Manager lifecycle symbols passed: real dispose path, enabled-only observer, userscript storage and mount receipts.");
