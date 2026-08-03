#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { buildCaptureBundle, CAPTURE_PROFILE, CAPTURE_TARGETS, REQUIRED_SCENARIOS } from "../../tools/build-live-performance-capture.mjs";
import { validateReport } from "../../tools/validate-live-performance-report.mjs";

const root = path.resolve(import.meta.dirname, "../..");
const sourcePath = path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js");
const profilerPath = path.join(root, "tools/mcms-performance-profiler.user.js");
const sourceBefore = fs.readFileSync(sourcePath, "utf8");
const profiler = fs.readFileSync(profilerPath, "utf8");
const result = buildCaptureBundle(sourceBefore, profiler);

assert.equal(result.manifest.profile, CAPTURE_PROFILE);
assert.equal(result.manifest.toolkitVersion, "10.5.4");
assert.equal(result.manifest.canonicalSourceSha256, "3b7f344883f9d44980a7a416cba3dfff1d68cfa5571ce9612a9565390fc21a77");
assert.deepEqual(result.manifest.instrumentedFunctions, [...CAPTURE_TARGETS].sort());
assert.deepEqual(result.manifest.requiredScenarios, REQUIRED_SCENARIOS.map(([name]) => name));
assert.equal(result.manifest.stableUpdateUrlsRemoved, true);
assert.equal(result.manifest.productionSourceModified, false);
assert.equal(result.manifest.requiresStableToolkitDisabled, true);
assert.match(result.bundle, /@name\s+MissionChief Toolkit v10\.5\.4 Authenticated Performance Capture/u);
assert.match(result.bundle, /@namespace\s+https:\/\/github\.com\/Conroy1988\/missionchief-toolkit-assets\/performance-capture/u);
assert.match(result.bundle, /@version\s+10\.5\.4-capture\.1/u);
assert.doesNotMatch(result.bundle, /^\/\/\s*@(downloadURL|updateURL)\s+/mu);
assert.match(result.bundle, /captureSourceSha256/u);
assert.match(result.bundle, /Finish and export report/u);
assert.match(result.bundle, /keep the normal Toolkit userscript disabled/u);
assert.match(result.bundle, /beginRender\?\.\("updateUI"\)/u);
assert.match(result.bundle, /beginRender\?\.\("renderOperationalPanels"\)/u);
assert.match(result.bundle, /beginRender\?\.\("renderMajorIncidentFeed"\)/u);
assert.match(result.bundle, /beginRender\?\.\("positionMajorIncidentFeed"\)/u);
assert.match(result.bundle, /beginRender\?\.\("ensureUi"\)/u);
assert.equal(fs.readFileSync(sourcePath, "utf8"), sourceBefore, "canonical source must remain byte-identical");

const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "mcms-live-capture-"));
const output = path.join(temporary, "capture.user.js");
fs.writeFileSync(output, result.bundle, "utf8");
execFileSync(process.execPath, ["--check", output], { stdio: "inherit" });

const transitions = REQUIRED_SCENARIOS.map(([scenario], index) => ({ at: index * 20_000, scenario }));
const measurements = REQUIRED_SCENARIOS.map(([scenario], index) => ({
  scenario,
  path: "updateUI",
  attempts: 4 + index,
  changedAttempts: 1,
  unchangedAttempts: 3 + index,
  totalDurationMs: 10,
  maxDurationMs: 3,
  mutationRecords: 2,
  unchangedRatio: 0.75,
  averageDurationMs: 2,
}));
const feedMeasurements = REQUIRED_SCENARIOS.map(([scenario], index) => ({
  scenario,
  path: "renderMajorIncidentFeed",
  attempts: 8 + index,
  changedAttempts: 1,
  unchangedAttempts: 7 + index,
  totalDurationMs: 8,
  maxDurationMs: 2,
  mutationRecords: 1,
  unchangedRatio: 0.875,
  averageDurationMs: 1,
}));
const report = {
  schemaVersion: 2,
  profilerVersion: result.manifest.profilerVersion,
  active: false,
  startedAt: 1,
  finishedAt: 120_001,
  durationMs: 120_000,
  page: { host: "www.missionchief.co.uk", pathClass: "other" },
  browser: { userAgent: "test" },
  startupMetrics: {
    captureProfile: result.manifest.profile,
    captureToolkitVersion: result.manifest.toolkitVersion,
    captureSourceSha256: result.manifest.canonicalSourceSha256,
    captureProfilerVersion: result.manifest.profilerVersion,
  },
  longTasks: [{ startTime: 1, durationMs: 60 }],
  layoutShifts: [{ startTime: 2, value: 0.01, hadRecentInput: false }],
  mutations: [{ at: 3, records: 1 }],
  runtimeSamples: [{ at: 1, present: true }, { at: 2, present: true }],
  visibility: [],
  resources: [{ host: "missionchief.co.uk", initiatorType: "script", count: 1, durationMs: 1, transferBytes: 0 }],
  droppedResourceGroups: 0,
  currentScenario: "layout-change",
  scenarioTransitions: transitions,
  renderEvents: [],
  renderMeasurements: [...measurements, ...feedMeasurements],
  limits: {},
};
const validation = validateReport(report, result.manifest);
assert.equal(validation.valid, true, validation.errors.join("\n"));
assert.equal(validation.updateUiMeasurements.length, REQUIRED_SCENARIOS.length);
assert.equal(validation.feedMeasurements.length, REQUIRED_SCENARIOS.length);

const active = validateReport({ ...report, active: true }, result.manifest);
assert.equal(active.valid, false);
assert.ok(active.errors.some(error => /Stop the profiler/u.test(error)));
const missingScenario = validateReport({ ...report, scenarioTransitions: transitions.slice(0, -1) }, result.manifest);
assert.equal(missingScenario.valid, false);
assert.ok(missingScenario.errors.some(error => /layout-change/u.test(error)));
assert.throws(() => validateReport({ ...report, cookie: "forbidden" }, result.manifest), /Forbidden sensitive field/u);

fs.rmSync(temporary, { recursive: true, force: true });
console.log("Authenticated live performance capture bundle and report validator contracts passed.");
