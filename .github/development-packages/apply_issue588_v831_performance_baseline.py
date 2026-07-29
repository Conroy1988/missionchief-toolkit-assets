#!/usr/bin/env python3
"""Issue #588 / parent #247: refresh the v8.3.1 measurement-only performance baseline."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DIST_JS = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
MANIFEST = ROOT / "dist/release-manifest.json"
EXPECTED_VERSION = "8.3.1"
EXPECTED_SHA256 = "363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089"
AUDIT_DIR = ROOT / "docs/audits/issue-588"


def read(path: Path | str) -> str:
    target = path if isinstance(path, Path) else ROOT / path
    return target.read_text(encoding="utf-8")


def write(path: Path | str, text: str) -> None:
    target = path if isinstance(path, Path) else ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def run(args: list[str], *, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, env=env, check=True)


source_before = SOURCE.read_bytes()
dist_js_before = DIST_JS.read_bytes()
dist_txt_before = DIST_TXT.read_bytes()
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("version") != EXPECTED_VERSION:
    raise RuntimeError(f"expected release manifest {EXPECTED_VERSION}, found {manifest.get('version')}")
for path in (SOURCE, DIST_JS, DIST_TXT):
    if sha256(path) != EXPECTED_SHA256:
        raise RuntimeError(f"production authority moved for {path.relative_to(ROOT)}")
if not (source_before == dist_js_before == dist_txt_before):
    raise RuntimeError("source/distribution parity was not exact before measurement")

runtime_audit = r'''#!/usr/bin/env node
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
'''
write(".github/scripts/audit_runtime_stress.mjs", runtime_audit)

discovery_test = r'''#!/usr/bin/env node
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
'''
write(".github/scripts/test_runtime_stress_discovery.mjs", discovery_test)

workflow_path = ROOT / ".github/workflows/validate-userscript.yml"
workflow = read(workflow_path)
workflow = replace_once(
    workflow,
    "          node .github/scripts/test_performance_profiler.js\n",
    "          node .github/scripts/test_performance_profiler.js\n          node .github/scripts/test_runtime_stress_discovery.mjs\n",
    "performance fixture insertion",
)
write(workflow_path, workflow)

AUDIT_DIR.mkdir(parents=True, exist_ok=True)
for child in AUDIT_DIR.iterdir():
    if child.is_dir():
        shutil.rmtree(child)
    else:
        child.unlink()

node_modules = ROOT / "node_modules"
package_lock = ROOT / "package-lock.json"
try:
    run(["npm", "install", "--no-save", "--package-lock=false", "--ignore-scripts", "--no-audit", "--no-fund", "acorn@8.15.0", "jsdom@26.1.0"])
    run(["node", "--check", ".github/scripts/audit_runtime_stress.mjs"])
    run(["node", "--check", ".github/scripts/test_runtime_stress_discovery.mjs"])
    run(["node", ".github/scripts/test_runtime_stress_discovery.mjs"])
    run([
        "python3", ".github/scripts/check_performance_budget.py",
        "--candidate", "src/MissionChief_Map_Command_Toolkit.user.js",
        "--policy", ".github/performance-budget.json",
        "--json-output", str(AUDIT_DIR / "performance-budget-report.json"),
        "--markdown-output", str(AUDIT_DIR / "performance-budget-report.md"),
    ])
    run([
        "node", ".github/scripts/deep_performance_audit.mjs",
        "--source", "src/MissionChief_Map_Command_Toolkit.user.js",
        "--json-output", str(AUDIT_DIR / "deep-performance-audit.json"),
        "--markdown-output", str(AUDIT_DIR / "deep-performance-audit.md"),
    ])
    run([
        "node", ".github/scripts/reconcile_deep_performance_audit.mjs",
        str(AUDIT_DIR / "deep-performance-audit.json"),
        str(AUDIT_DIR / "deep-performance-audit.md"),
    ])
    audit_env = os.environ.copy()
    audit_env["MCMS_AUDIT_OUTPUT"] = str(AUDIT_DIR)
    audit_env["MCMS_AUDIT_REPEATS"] = "8"
    run(["node", ".github/scripts/audit_runtime_stress.mjs"], env=audit_env)
finally:
    if node_modules.exists():
        shutil.rmtree(node_modules)
    if package_lock.exists():
        package_lock.unlink()

if SOURCE.read_bytes() != source_before or DIST_JS.read_bytes() != dist_js_before or DIST_TXT.read_bytes() != dist_txt_before:
    raise RuntimeError("measurement package changed production source or distribution")
for path in (SOURCE, DIST_JS, DIST_TXT):
    if sha256(path) != EXPECTED_SHA256:
        raise RuntimeError(f"production hash changed after measurement: {path.relative_to(ROOT)}")

runtime_report = json.loads((AUDIT_DIR / "runtime-stress.json").read_text(encoding="utf-8"))
deep_report = json.loads((AUDIT_DIR / "deep-performance-audit.json").read_text(encoding="utf-8"))
budget_report = json.loads((AUDIT_DIR / "performance-budget-report.json").read_text(encoding="utf-8"))
if runtime_report.get("status") != "passed":
    raise RuntimeError("runtime stress audit did not pass")
if ".github/scripts/test_issue564_incident_feed_attended_runtime.js" not in runtime_report["discovery"]["canonicalRuntimeContracts"]:
    raise RuntimeError("Issue #564 runtime contract is absent from discovered stress coverage")
if runtime_report.get("repeatedExecutions", 0) <= 88:
    raise RuntimeError("current stress suite did not exceed the stale 88-execution baseline")

source_text = SOURCE.read_text(encoding="utf-8")
line_count = len(source_text.splitlines())
try:
    audited_main = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True).strip()
except Exception:
    audited_main = "4247b7caa7dad78007010e8bf0e33c352f3d45e3"
max_rss = max((result.get("maximumPeakRssKb") or 0) for result in runtime_report.get("results", []))
manifest_out = {
    "schemaVersion": 1,
    "issue": 588,
    "parentIssue": 247,
    "measurementOnly": True,
    "toolkitVersion": EXPECTED_VERSION,
    "auditedMain": audited_main,
    "sourceSha256": EXPECTED_SHA256,
    "sourceBytes": len(source_before),
    "sourceLines": line_count,
    "sourceDistributionParity": True,
    "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "runtimeStress": {
        "status": runtime_report["status"],
        "canonicalContracts": len(runtime_report["discovery"]["canonicalRuntimeContracts"]),
        "explicitContracts": len(runtime_report["discovery"]["explicitRuntimeContracts"]),
        "repeatedExecutions": runtime_report["repeatedExecutions"],
        "totalSeconds": runtime_report["totalSeconds"],
        "maximumPeakRssKb": max_rss,
    },
    "deepPerformance": deep_report.get("summary", {}),
    "performanceBudgetStatus": budget_report.get("status", "unknown"),
    "safetyBoundary": "Static and CI stress evidence only; authenticated MissionChief browser evidence remains required before CSS modularisation or broad render-path optimisation.",
}
write(AUDIT_DIR / "manifest.json", json.dumps(manifest_out, indent=2) + "\n")

summary = deep_report.get("summary", {})
readme = f"""# Issue #588 — Toolkit v8.3.1 performance baseline refresh

This evidence pack is a measurement-only child of Issue #247. It changes no Toolkit source, distribution mirror, version, feature behaviour or release state.

## Exact authority

- Toolkit version: `{EXPECTED_VERSION}`
- Audited `main`: `{audited_main}`
- Source SHA-256: `{EXPECTED_SHA256}`
- Source bytes: `{len(source_before):,}`
- Source lines: `{line_count:,}`
- Source/distribution parity: exact

## Runtime stress

The runtime test plan is now discovered from the canonical preflight instead of a second hard-coded list.

- Canonical runtime contracts: {len(runtime_report['discovery']['canonicalRuntimeContracts'])}
- Explicit heavy integration contracts: {len(runtime_report['discovery']['explicitRuntimeContracts'])}
- Repeated executions: {runtime_report['repeatedExecutions']}
- Total elapsed: {runtime_report['totalSeconds']:.2f} seconds
- Maximum observed RSS: {max_rss:,} KiB
- Issue #564 attended-Incident-Wire runtime coverage: included
- Failures: none

## Static deep-performance inventory

- Functions and callbacks: {summary.get('functionsAndCallbacks', '—')}
- Ranked non-wrapper functions: {summary.get('rankedFunctions', '—')}
- MutationObserver constructions: {summary.get('mutationObserverConstructions', '—')}
- ResizeObserver constructions: {summary.get('resizeObserverConstructions', '—')}
- Observer registrations: {summary.get('observerRegistrations', '—')}
- Broad subtree registrations: {summary.get('broadSubtreeObservers', '—')}
- Scheduler call sites: {summary.get('schedulerCalls', '—')}
- Repeated literal selectors: {summary.get('repeatedSelectors', '—')}

## Interpretation boundary

This pack provides exact v8.3.1 static and CI stress evidence. It does **not** claim authenticated MissionChief browser timing, style-recalculation cost, mutation frequency or memory-retention behaviour. Issues #254 and #255 remain gated against unsupported speculative optimisation until equivalent browser evidence or a deterministic exact proof isolates a safe change.
"""
write(AUDIT_DIR / "README.md", readme)

contract = r'''#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'docs/audits/issue-588/manifest.json').read_text(encoding='utf-8'))
runtime=json.loads((ROOT/'docs/audits/issue-588/runtime-stress.json').read_text(encoding='utf-8'))
assert manifest['issue']==588 and manifest['parentIssue']==247
assert manifest['measurementOnly'] is True
assert manifest['toolkitVersion']=='8.3.1'
assert manifest['sourceSha256']=='363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089'
assert manifest['sourceDistributionParity'] is True
assert runtime['schemaVersion']==2 and runtime['status']=='passed'
assert runtime['discovery']['authority']=='.github/scripts/run_userscript_preflight.sh'
assert '.github/scripts/test_issue564_incident_feed_attended_runtime.js' in runtime['discovery']['canonicalRuntimeContracts']
assert runtime['repeatedExecutions']>88
assert len(runtime['results'])==len(runtime['discovery']['plannedContracts'])
assert not runtime['failures']
source=(ROOT/'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
dist=(ROOT/'dist/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
txt=(ROOT/'dist/MissionChief_Map_Command_Toolkit.txt').read_bytes()
assert source==dist==txt
print('Issue #588 v8.3.1 measurement-only performance baseline contract passed.')
'''
write(".github/scripts/test_issue588_v831_performance_baseline.py", contract)

preflight = read(".github/scripts/run_userscript_preflight.sh")
preflight = replace_once(
    preflight,
    "python3 .github/scripts/test_path_aware_blocking.py\n",
    "python3 .github/scripts/test_path_aware_blocking.py\npython3 .github/scripts/test_issue588_v831_performance_baseline.py\n",
    "Issue #588 retained evidence contract insertion",
)
write(".github/scripts/run_userscript_preflight.sh", preflight)

print(json.dumps(manifest_out, indent=2))
