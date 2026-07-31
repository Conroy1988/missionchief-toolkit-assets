#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const start = source.indexOf("    const QUICK_PLACES = [");
const end = source.indexOf("    const SMART_BOOKMARK_LABEL_MAX", start);
assert.ok(start >= 0 && end > start, "Quick Jump catalogue section is missing");

const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(
  source.slice(start, end) +
    "\nthis.__probe = { places: QUICK_PLACES, normalise: normaliseQuickPins };",
  sandbox,
  { filename: "issue614-quick-places-runtime.js" },
);

const plain = value => JSON.parse(JSON.stringify(value));
assert.deepEqual(
  plain(sandbox.__probe.places.map(({ id, label, name, lat, lng, zoom }) => ({ id, label, name, lat, lng, zoom }))),
  [
    { id: "edi", label: "EDI", name: "Edinburgh", lat: 55.9533, lng: -3.1883, zoom: 11 },
    { id: "fife", label: "FIFE", name: "Fife", lat: 56.2082, lng: -3.1495, zoom: 10 },
    { id: "wake", label: "WKFD", name: "Wakefield", lat: 53.6833, lng: -1.4977, zoom: 11 },
    { id: "lond", label: "LDN", name: "London", lat: 51.5074, lng: -0.1278, zoom: 10 },
    { id: "newc", label: "NCL", name: "Newcastle", lat: 54.9783, lng: -1.6178, zoom: 11 },
  ],
);

const defaults = Object.fromEntries(sandbox.__probe.places.map(place => [place.id, false]));
const legacy = { edi: true, glas: true, dund: false, stir: true, unrelated: true };
const migrated = plain(sandbox.__probe.normalise(legacy, defaults));
assert.deepEqual(migrated, { edi: true, fife: false, wake: true, lond: false, newc: true });
assert.deepEqual(legacy, { edi: true, glas: true, dund: false, stir: true, unrelated: true });

const explicitReplacement = plain(sandbox.__probe.normalise({ glas: true, wake: false, lond: true }, defaults));
assert.deepEqual(explicitReplacement, { edi: false, fife: false, wake: false, lond: true, newc: false });

const fresh = plain(sandbox.__probe.normalise(undefined, defaults));
assert.deepEqual(fresh, { edi: false, fife: false, wake: false, lond: false, newc: false });

console.log("Issue #614 runtime passed: ordered destinations, legacy pin transfer, explicit replacement choice and fresh defaults.");
