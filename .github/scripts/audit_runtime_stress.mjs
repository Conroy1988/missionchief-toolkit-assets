#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const preflightPath = path.join(root, ".github/scripts/run_userscript_preflight.sh");
const integrationContract = ".github/scripts/test_ui_mount_integration.mjs";

export function discoverRuntimeContracts(preflightSource) {
  const discovered = [];
  const seen = new Set();
  for (const line of String(preflightSource || "").split(/\r?\n/u)) {
    const match = line.match(/^\s*node\s+(\.github\/scripts\/test_[A-Za-z0-9_./-]+\.(?:js|mjs))(?:\s.*)?$/u);
    if (!match) continue;
    const relative = match[1];
    if (seen.has(relative)) continue;
    seen.add(relative);
    discovered.push(relative);
  }
  if (!discovered.length) throw new Error("Canonical preflight contains no Node runtime contracts.");
  return discovered;
}

export function buildRuntimeStressPlan(preflightSource, defaultRepeats = 8) {
  const repeats = Math.max(1, Number.parseInt(String(defaultRepeats), 10) || 8);
  const contracts = discoverRuntimeContracts(preflightSource);
  const plan = contracts.map(relative => [relative, repeats]);
  if (!contracts.includes(integrationContract)) plan.push([integrationContract, Math.max(repeats, 16)]);
  return plan;
}

function median(values) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

export function runRuntimeStressAudit() {
  const output = process.env.MCMS_AUDIT_OUTPUT || path.join(root, "audit-output");
  fs.mkdirSync(output, { recursive: true });
  const defaultRepeats = Number.parseInt(process.env.MCMS_AUDIT_REPEATS || "8", 10);
  const preflightSource = fs.readFileSync(preflightPath, "utf8");
  const tests = buildRuntimeStressPlan(preflightSource, defaultRepeats);
  const perRunSecondsCeiling = Number.parseFloat(process.env.MCMS_AUDIT_RUN_SECONDS_CEILING || "45");
  const peakRssKbCeiling = Number.parseInt(process.env.MCMS_AUDIT_RSS_KB_CEILING || "700000", 10);
  const totalSecondsCeiling = Number.parseFloat(process.env.MCMS_AUDIT_TOTAL_SECONDS_CEILING || "900");
  const results = [];
  const failures = [];
  const started = process.hrtime.bigint();

  for (const [relative, repeats] of tests) {
    const absolute = path.join(root, relative);
    if (!fs.existsSync(absolute)) {
      failures.push(`${relative}: missing runtime contract`);
      continue;
    }
    const samples = [];
    for (let iteration = 1; iteration <= repeats; iteration += 1) {
      const metricsPath = path.join(os.tmpdir(), `mcms-audit-${process.pid}-${results.length}-${iteration}.txt`);
      const run = spawnSync(
        "/usr/bin/time",
        ["-f", "%e %M", "-o", metricsPath, process.execPath, "--unhandled-rejections=strict", absolute],
        {
          cwd: root,
          encoding: "utf8",
          timeout: Math.ceil(perRunSecondsCeiling * 1000) + 15000,
          env: {
            ...process.env,
            NODE_OPTIONS: [process.env.NODE_OPTIONS, "--unhandled-rejections=strict"].filter(Boolean).join(" "),
          },
          maxBuffer: 16 * 1024 * 1024,
        },
      );
      let elapsedSeconds = Number.NaN;
      let peakRssKb = Number.NaN;
      try {
        const metrics = fs.readFileSync(metricsPath, "utf8").trim().split(/\s+/u);
        elapsedSeconds = Number.parseFloat(metrics[0]);
        peakRssKb = Number.parseInt(metrics[1], 10);
      } catch {}
      try { fs.unlinkSync(metricsPath); } catch {}
      samples.push({ iteration, status: run.status, signal: run.signal, elapsedSeconds, peakRssKb });
      if (run.error) failures.push(`${relative} iteration ${iteration}: ${run.error.message}`);
      if (run.status !== 0) {
        const stderr = String(run.stderr || "").slice(-4000);
        const stdout = String(run.stdout || "").slice(-4000);
        failures.push(`${relative} iteration ${iteration}: exit ${run.status}; stdout=${JSON.stringify(stdout)}; stderr=${JSON.stringify(stderr)}`);
      }
      if (Number.isFinite(elapsedSeconds) && elapsedSeconds > perRunSecondsCeiling) failures.push(`${relative} iteration ${iteration}: ${elapsedSeconds}s exceeded ${perRunSecondsCeiling}s ceiling`);
      if (Number.isFinite(peakRssKb) && peakRssKb > peakRssKbCeiling) failures.push(`${relative} iteration ${iteration}: ${peakRssKb} KiB exceeded ${peakRssKbCeiling} KiB RSS ceiling`);
    }
    const elapsed = samples.map(sample => sample.elapsedSeconds).filter(Number.isFinite);
    const rss = samples.map(sample => sample.peakRssKb).filter(Number.isFinite);
    results.push({
      test: relative,
      repeats,
      passed: samples.every(sample => sample.status === 0),
      medianElapsedSeconds: median(elapsed),
      maximumElapsedSeconds: elapsed.length ? Math.max(...elapsed) : null,
      medianPeakRssKb: median(rss),
      maximumPeakRssKb: rss.length ? Math.max(...rss) : null,
      samples,
    });
  }

  const totalSeconds = Number(process.hrtime.bigint() - started) / 1e9;
  if (totalSeconds > totalSecondsCeiling) failures.push(`Complete runtime stress took ${totalSeconds.toFixed(2)}s, exceeding ${totalSecondsCeiling}s`);
  const sourceText = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");
  const report = {
    schemaVersion: 2,
    audit: "runtime-stress",
    status: failures.length ? "failed" : "passed",
    source: {
      version: sourceText.match(/^\/\/\s*@version\s+([^\s]+)/mu)?.[1] || "unknown",
      sha256: crypto.createHash("sha256").update(sourceText, "utf8").digest("hex"),
    },
    discovery: {
      authority: ".github/scripts/run_userscript_preflight.sh",
      authoritySha256: crypto.createHash("sha256").update(preflightSource, "utf8").digest("hex"),
      canonicalRuntimeContracts: discoverRuntimeContracts(preflightSource),
      explicitRuntimeContracts: tests.map(item => item[0]).filter(item => !discoverRuntimeContracts(preflightSource).includes(item)),
      plannedContracts: tests.map(([test, repeats]) => ({ test, repeats })),
    },
    repeatedExecutions: results.reduce((sum, result) => sum + result.repeats, 0),
    totalSeconds,
    ceilings: { perRunSecondsCeiling, peakRssKbCeiling, totalSecondsCeiling },
    failures,
    results,
  };
  fs.writeFileSync(path.join(output, "runtime-stress.json"), `${JSON.stringify(report, null, 2)}\n`);
  const markdown = [
    "# Toolkit repeated runtime stress audit",
    "",
    `- **Status:** \`${report.status}\``,
    `- **Toolkit version:** \`${report.source.version}\``,
    `- **Source SHA-256:** \`${report.source.sha256}\``,
    `- **Discovery authority:** \`${report.discovery.authority}\``,
    `- **Discovered runtime contracts:** ${report.discovery.canonicalRuntimeContracts.length}`,
    `- **Explicit heavier contracts:** ${report.discovery.explicitRuntimeContracts.length}`,
    `- **Repeated executions:** ${report.repeatedExecutions}`,
    `- **Total elapsed:** ${totalSeconds.toFixed(2)} seconds`,
    `- **Per-run ceiling:** ${perRunSecondsCeiling} seconds`,
    `- **Peak RSS ceiling:** ${peakRssKbCeiling.toLocaleString("en-GB")} KiB`,
    "",
    "| Runtime contract | Repeats | Median | Maximum | Median RSS | Maximum RSS |",
    "|---|---:|---:|---:|---:|---:|",
    ...results.map(result => `| \`${result.test}\` | ${result.repeats} | ${result.medianElapsedSeconds.toFixed(2)}s | ${result.maximumElapsedSeconds?.toFixed(2) ?? "—"}s | ${Math.round(result.medianPeakRssKb || 0).toLocaleString("en-GB")} KiB | ${Math.round(result.maximumPeakRssKb || 0).toLocaleString("en-GB")} KiB |`),
    "",
    "## Failures",
    "",
    ...(failures.length ? failures.map(failure => `- ${failure}`) : ["- None."]),
    "",
  ];
  fs.writeFileSync(path.join(output, "runtime-stress.md"), markdown.join("\n"));
  console.log(JSON.stringify(report, null, 2));
  process.exitCode = failures.length ? 1 : 0;
  return report;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) runRuntimeStressAudit();
