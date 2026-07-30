#!/usr/bin/env node
"use strict";

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const ALLOWED_HOSTS = new Set([
  "missionchief.co.uk", "www.missionchief.co.uk",
  "missionchief.com", "www.missionchief.com",
  "leitstellenspiel.de", "www.leitstellenspiel.de",
  "meldkamerspel.com", "www.meldkamerspel.com",
]);
const REQUIRED_SCENARIOS = [
  "idle-map", "settings-open-close", "mission-open-close",
  "unit-selection", "map-pan-zoom", "layout-change",
];
const FORBIDDEN_KEYS = /(?:cookie|authorization|webhook|token|missionTitle|address|coordinate|vehicleName|personnelName|allianceMessage|storageValue)/iu;

function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${key}`);
    result[key.slice(2)] = value;
    index += 1;
  }
  return result;
}

function scanKeys(value, pathName = "report") {
  if (Array.isArray(value)) {
    value.forEach((item, index) => scanKeys(item, `${pathName}[${index}]`));
    return;
  }
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_KEYS.test(key)) throw new Error(`Forbidden sensitive field: ${pathName}.${key}`);
    scanKeys(child, `${pathName}.${key}`);
  }
}

function orderedScenarioCoverage(report) {
  const observed = (report.scenarioTransitions || []).map(item => String(item?.scenario || ""));
  let position = -1;
  for (const required of REQUIRED_SCENARIOS) {
    const next = observed.indexOf(required, position + 1);
    if (next < 0) throw new Error(`Missing or out-of-order scenario transition: ${required}`);
    position = next;
  }
  return observed;
}

function renderCoverage(report) {
  const measurements = Array.isArray(report.renderMeasurements) ? report.renderMeasurements : [];
  const updateRows = measurements.filter(item => item?.path === "updateUI" && Number(item?.attempts) > 0);
  if (!updateRows.length) throw new Error("No updateUI render measurements were captured");
  const covered = new Set(updateRows.map(item => String(item.scenario || "")));
  const missing = REQUIRED_SCENARIOS.filter(name => !covered.has(name));
  if (missing.length) throw new Error(`No updateUI render evidence for: ${missing.join(", ")}`);
  return { measurements, updateRows };
}

export function validateReport(report, manifest) {
  const errors = [];
  const assert = (condition, message) => { if (!condition) errors.push(message); };
  assert(report && typeof report === "object", "Report must be a JSON object");
  if (!report || typeof report !== "object") return { valid: false, errors };

  scanKeys(report);
  assert(report.schemaVersion === 2, "Profiler schemaVersion must be 2");
  assert(report.profilerVersion === manifest.profilerVersion, "Profiler version does not match capture manifest");
  assert(report.active === false, "Stop the profiler before exporting the report");
  assert(Number(report.durationMs) >= 60_000, "Capture duration must be at least 60 seconds");
  assert(ALLOWED_HOSTS.has(String(report.page?.host || "")), "Report host is not an allowed MissionChief domain");
  assert(["other", "mission", "building", "vehicle", "alliance"].includes(String(report.page?.pathClass || "")), "Invalid pathClass");
  assert(report.startupMetrics?.captureProfile === manifest.profile, "Capture profile marker missing");
  assert(report.startupMetrics?.captureToolkitVersion === manifest.toolkitVersion, "Toolkit version marker mismatch");
  assert(report.startupMetrics?.captureSourceSha256 === manifest.canonicalSourceSha256, "Canonical source hash marker mismatch");
  assert(report.startupMetrics?.captureProfilerVersion === manifest.profilerVersion, "Profiler marker mismatch");
  assert(Array.isArray(report.runtimeSamples) && report.runtimeSamples.length >= 2, "At least two runtime resource samples are required");
  assert(Array.isArray(report.longTasks), "longTasks must be an array");
  assert(Array.isArray(report.layoutShifts), "layoutShifts must be an array");
  assert(Array.isArray(report.mutations), "mutations must be an array");
  assert(Array.isArray(report.resources), "resources must be an array");

  let scenarios = [];
  let render = { measurements: [], updateRows: [] };
  try { scenarios = orderedScenarioCoverage(report); } catch (error) { errors.push(error.message); }
  try { render = renderCoverage(report); } catch (error) { errors.push(error.message); }

  const summary = {
    valid: errors.length === 0,
    errors,
    capture: {
      profile: manifest.profile,
      toolkitVersion: manifest.toolkitVersion,
      canonicalSourceSha256: manifest.canonicalSourceSha256,
      bundleSha256: manifest.bundleSha256,
    },
    durationMs: Number(report.durationMs) || 0,
    scenarioTransitions: scenarios,
    updateUiMeasurements: render.updateRows.map(item => ({
      scenario: item.scenario,
      attempts: item.attempts,
      unchangedAttempts: item.unchangedAttempts,
      changedAttempts: item.changedAttempts,
      unchangedRatio: item.unchangedRatio,
      averageDurationMs: item.averageDurationMs,
      maxDurationMs: item.maxDurationMs,
      mutationRecords: item.mutationRecords,
    })),
    longTaskCount: report.longTasks?.length || 0,
    longTaskTotalMs: (report.longTasks || []).reduce((sum, item) => sum + Math.max(0, Number(item?.durationMs) || 0), 0),
    layoutShiftTotal: (report.layoutShifts || []).filter(item => item?.hadRecentInput !== true).reduce((sum, item) => sum + Math.max(0, Number(item?.value) || 0), 0),
    mutationBatches: report.mutations?.length || 0,
    runtimeSamples: report.runtimeSamples?.length || 0,
  };
  return summary;
}

function renderMarkdown(summary) {
  const lines = [
    "# MissionChief Toolkit live performance report validation",
    "",
    `- **Result:** ${summary.valid ? "PASS" : "FAIL"}`,
    `- **Toolkit:** ${summary.capture.toolkitVersion}`,
    `- **Source SHA-256:** \`${summary.capture.canonicalSourceSha256}\``,
    `- **Duration:** ${(summary.durationMs / 1000).toFixed(1)} seconds`,
    `- **Long tasks:** ${summary.longTaskCount} / ${summary.longTaskTotalMs.toFixed(1)} ms total`,
    `- **Layout shift total:** ${summary.layoutShiftTotal.toFixed(6)}`,
    `- **Mutation batches:** ${summary.mutationBatches}`,
    `- **Runtime samples:** ${summary.runtimeSamples}`,
    "",
    "## updateUI scenario evidence",
    "",
    "| Scenario | Attempts | Unchanged | Changed | Unchanged ratio | Average | Maximum | Mutation records |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
    ...summary.updateUiMeasurements.map(row => `| ${row.scenario} | ${row.attempts} | ${row.unchangedAttempts} | ${row.changedAttempts} | ${Number(row.unchangedRatio || 0).toFixed(4)} | ${Number(row.averageDurationMs || 0).toFixed(3)} ms | ${Number(row.maxDurationMs || 0).toFixed(3)} ms | ${row.mutationRecords} |`),
    "",
    "## Validation errors",
    "",
    ...(summary.errors.length ? summary.errors.map(error => `- ${error}`) : ["- None."]),
    "",
  ];
  return lines.join("\n");
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.report || !args.manifest) throw new Error("Usage: validate-live-performance-report.mjs --report REPORT.json --manifest capture-manifest.json [--json-output FILE] [--markdown-output FILE]");
  const report = JSON.parse(fs.readFileSync(path.resolve(args.report), "utf8"));
  const manifest = JSON.parse(fs.readFileSync(path.resolve(args.manifest), "utf8"));
  const summary = validateReport(report, manifest);
  const json = JSON.stringify(summary, null, 2) + "\n";
  const markdown = renderMarkdown(summary);
  if (args["json-output"]) fs.writeFileSync(path.resolve(args["json-output"]), json, "utf8");
  if (args["markdown-output"]) fs.writeFileSync(path.resolve(args["markdown-output"]), markdown, "utf8");
  console.log(json);
  if (!summary.valid) process.exitCode = 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  try { main(); } catch (error) { console.error(error.stack || error.message); process.exit(1); }
}
