#!/usr/bin/env python3
"""Apply the v8.2.1 Patient Transport Sweep release-navigation hotfix."""
from __future__ import annotations

import hashlib
import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
STATIC_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github/performance-budget.json"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
HELP_MANIFEST = ROOT / "help/manifest.json"
DOC = ROOT / "docs/issue-565-transport-sweep-no-reward.md"


def clean(value: str) -> str:
    return textwrap.dedent(value).lstrip("\n")


source = SOURCE.read_text(encoding="utf-8")
if not re.search(r"(?m)^//\s*@version\s+8\.2\.0$", source):
    raise RuntimeError("Expected v8.2.0 canonical source")

helper_start = source.index("    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT")
helper_end = source.index("    function transportSweepVisibleDischargeButtons()", helper_start)
new_helper = clean(r'''
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT = 'release patient (no reward)';
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH = /^\/vehicles\/(?<vehicleId>\d+)\/patient\/-1\/?$/u;
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_LIMIT = 100;
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS = 2500;
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_SETTLE_MS = 6000;
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_REQUEST_TIMEOUT_MS = 12000;

    function transportSweepOptionalReleasePatientCount(control) {
        const row = control?.closest?.('tr') || null;
        const vehicleCell = row?.querySelector?.('td:first-child') || row;
        const text = String(vehicleCell?.textContent || '').replace(/\s+/gu, ' ').trim();
        const match = text.match(/\bpatients?\s*:\s*(.+)$/iu);
        if (!match?.[1]) return null;
        const names = match[1]
            .split(/\s*,\s*/u)
            .map(value => value.trim())
            .filter(Boolean);
        return names.length || null;
    }

    function transportSweepOptionalReleaseDetails(control) {
        if (!control || !transportSweepElementVisible(control)) return null;
        if (normaliseTransportSweepReleaseText(control.textContent) !== TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT) return null;
        const rawHref = String(control.getAttribute?.('href') || control.href || '').trim();
        if (!rawHref) return null;
        let url;
        try {
            url = new URL(rawHref, location.href);
        } catch (error) {
            return null;
        }
        let currentOrigin = '';
        try { currentOrigin = new URL(location.href).origin; } catch (error) {}
        if (currentOrigin && url.origin !== currentOrigin) return null;
        const match = url.pathname.match(TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH);
        if (!match?.groups?.vehicleId) return null;
        return {
            control,
            href: url.href,
            path: url.pathname,
            vehicleId: match.groups.vehicleId,
            patientCount: transportSweepOptionalReleasePatientCount(control),
        };
    }

    function transportSweepOptionalReleaseControls() {
        const controls = [];
        const seen = new Set();
        const selector = 'a[href*="/vehicles/"][href*="/patient/-1"]';
        const addControl = control => {
            if (!control || seen.has(control)) return;
            seen.add(control);
            if (transportSweepOptionalReleaseDetails(control)) controls.push(control);
        };
        const inspect = root => {
            if (!root) return;
            try {
                if (root.matches?.(selector)) addControl(root);
                Array.from(root.querySelectorAll?.(selector) || []).forEach(addControl);
            } catch (error) {}
        };
        transportSweepVisibleWindowRoots().forEach(inspect);
        transportSweepDocumentContexts().forEach(context => inspect(context.doc));
        return controls;
    }

    function transportSweepOptionalReleaseState(missionId) {
        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId) || [];
        const eligibleVehicleIds = new Set(
            Array.from(candidates)
                .map(candidate => String(candidate?.vehicleId || '').trim())
                .filter(Boolean)
        );
        const releases = transportSweepOptionalReleaseControls()
            .map(transportSweepOptionalReleaseDetails)
            .filter(details => details && eligibleVehicleIds.has(details.vehicleId));
        return { candidates: Array.from(candidates), eligibleVehicleIds, releases };
    }

    async function waitForTransportSweepOptionalReleaseState(missionId, options = {}) {
        const vehicleId = String(options.vehicleId || '').trim();
        const timeoutMs = Math.max(0, Number(options.timeoutMs) || TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS);
        let latest = transportSweepOptionalReleaseState(missionId);
        const immediatelySettled = vehicleId
            ? latest.releases.some(release => release.vehicleId === vehicleId) || !latest.eligibleVehicleIds.has(vehicleId)
            : latest.releases.length > 0 || latest.eligibleVehicleIds.size === 0;
        if (immediatelySettled) return { ...latest, settled: true, timedOut: false };

        const waited = await transportSweepWaitFor(() => {
            latest = transportSweepOptionalReleaseState(missionId);
            if (vehicleId) {
                if (latest.releases.some(release => release.vehicleId === vehicleId)) return latest;
                if (!latest.eligibleVehicleIds.has(vehicleId)) return latest;
                return null;
            }
            return latest.releases.length ? latest : null;
        }, timeoutMs, 70);
        return waited
            ? { ...waited, settled: true, timedOut: false }
            : { ...latest, settled: false, timedOut: true };
    }

    function findTransportSweepOptionalReleaseControl(state, attemptedSignatures = null) {
        const attempted = attemptedSignatures instanceof Set ? attemptedSignatures : new Set();
        for (const release of state?.releases || []) {
            const signature = `${release.vehicleId}:${release.patientCount ?? 'unknown'}`;
            if (attempted.has(signature)) continue;
            return { ...release, signature };
        }
        return null;
    }

    function transportSweepOptionalReleaseKey(missionId, vehicleId, sequence) {
        const mission = normaliseMissionId(missionId);
        const vehicle = normaliseMissionId(vehicleId);
        const ordinal = Math.max(1, Number(sequence) || 1);
        return mission && vehicle ? `${mission}:${vehicle}:no-reward:${ordinal}` : '';
    }

    function recordTransportSweepOptionalReleaseError(message) {
        transportSweepRuntime.errors += 1;
        transportSweepLog(message, 'error');
        renderTransportSweepPanel();
    }

    async function requestTransportSweepOptionalRelease(release) {
        const ownerWindow = release?.control?.ownerDocument?.defaultView || pageWindow;
        const fetcher = ownerWindow?.fetch || pageWindow?.fetch;
        if (typeof fetcher !== 'function') throw new Error('same-origin request API is unavailable');
        const Controller = ownerWindow?.AbortController || pageWindow?.AbortController;
        const controller = typeof Controller === 'function' ? new Controller() : null;
        const timeoutHandle = controller
            ? runtimeSetTimeout(() => controller.abort(), TRANSPORT_SWEEP_OPTIONAL_RELEASE_REQUEST_TIMEOUT_MS)
            : null;
        try {
            const response = await fetcher.call(ownerWindow, release.href, {
                method: 'GET',
                credentials: 'same-origin',
                redirect: 'follow',
                cache: 'no-store',
                signal: controller?.signal,
            });
            if (!response?.ok) throw new Error(`request returned HTTP ${response?.status || 'unknown'}`);
            await response.text();
            return { status: response.status, url: String(response.url || release.href) };
        } finally {
            if (timeoutHandle !== null) runtimeClearTimeout(timeoutHandle);
        }
    }

    function transportSweepOptionalReleaseProgressed(before, afterState) {
        const after = (afterState?.releases || []).find(release => release.vehicleId === before.vehicleId) || null;
        if (!afterState?.settled) return { progressed: false, after };
        if (!after) return { progressed: !afterState.eligibleVehicleIds.has(before.vehicleId), after };
        if (Number.isFinite(before.patientCount) && Number.isFinite(after.patientCount)) {
            return { progressed: after.patientCount < before.patientCount, after };
        }
        return { progressed: false, after };
    }

    async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance) {
        const outcome = { cleared: 0, missionAvailable: true };
        const allowance = Number.isFinite(remainingAllowance)
            ? Math.max(0, Math.floor(remainingAllowance))
            : TRANSPORT_SWEEP_OPTIONAL_RELEASE_LIMIT;
        const maximum = Math.min(allowance, TRANSPORT_SWEEP_OPTIONAL_RELEASE_LIMIT);
        const attemptedSignatures = new Set();
        let sequence = 0;
        let releaseState = await waitForTransportSweepOptionalReleaseState(missionId);

        while (
            transportSweepRuntime.running
            && !transportSweepRuntime.stopRequested
            && outcome.cleared < maximum
        ) {
            const release = findTransportSweepOptionalReleaseControl(releaseState, attemptedSignatures);
            if (!release) break;
            attemptedSignatures.add(release.signature);
            transportSweepLog(
                `Requesting Release patient (No reward) for vehicle ${release.vehicleId} at ${item.caption}`
            );

            try {
                await requestTransportSweepOptionalRelease(release);
            } catch (error) {
                recordTransportSweepOptionalReleaseError(
                    `Could not complete Release patient (No reward) for vehicle ${release.vehicleId}: ${error?.message || error}`
                );
                break;
            }

            if (transportSweepRuntime.stopRequested) break;
            await closeTransportSweepWindows('reopening mission after completed no-reward patient release');
            if (transportSweepRuntime.stopRequested) break;

            const reopened = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
            if (!reopened) {
                outcome.missionAvailable = false;
                recordTransportSweepOptionalReleaseError(
                    `Could not reopen ${item.caption} after releasing vehicle ${release.vehicleId}`
                );
                break;
            }

            const afterState = await waitForTransportSweepOptionalReleaseState(missionId, {
                vehicleId: release.vehicleId,
                timeoutMs: TRANSPORT_SWEEP_OPTIONAL_RELEASE_SETTLE_MS,
            });
            const verification = transportSweepOptionalReleaseProgressed(release, afterState);
            if (!verification.progressed) {
                recordTransportSweepOptionalReleaseError(
                    `Release patient (No reward) did not reduce the patient count for vehicle ${release.vehicleId}; native fallback retained`
                );
                break;
            }

            sequence += 1;
            const releaseKey = transportSweepOptionalReleaseKey(missionId, release.vehicleId, sequence);
            if (recordTransportSweepConfirmedRelease(
                releaseKey,
                `Cleared patient ${sequence} from vehicle ${release.vehicleId} at ${item.caption} with Release patient (No reward)`
            )) {
                outcome.cleared += 1;
            }
            releaseState = afterState;
        }
        return outcome;
    }

''')
source = source[:helper_start] + new_helper + source[helper_end:]

processor_start = source.index("    async function processTransportSweepMission(item, remainingAllowance) {")
processor_end = source.index("\n    async function startTransportSweep", processor_start)
processor = source[processor_start:processor_end]
old_start = processor.index("        let candidates = collectTransportSweepVehicleCandidatesForMission(missionId);")
old_end = processor.index("            const candidateStats", old_start)
replacement = clean('''
        const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(
            item,
            missionId,
            Math.max(0, remainingAllowance - clearedHere)
        );
        clearedHere += optionalReleaseResult.cleared;
        if (
            transportSweepRuntime.stopRequested
            || !optionalReleaseResult.missionAvailable
            || clearedHere >= remainingAllowance
        ) {
            await closeTransportSweepWindows('ending no-reward patient release fast path');
            return clearedHere;
        }

        let candidates = collectTransportSweepVehicleCandidatesForMission(missionId);
''')
processor = processor[:old_start] + replacement + processor[old_end:]
source = source[:processor_start] + processor + source[processor_end:]

source = re.sub(r"(?m)^//\s*@version\s+8\.2\.0$", "// @version      8.2.1", source, count=1)
source = source.replace("version: '8.2.0'", "version: '8.2.1'", 1)
SOURCE.write_text(source, encoding="utf-8")

runtime_test = clean(r'''#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");

function extractFunction(name) {
  const markers = [`    function ${name}(`, `    async function ${name}(`];
  const starts = markers.map(marker => source.indexOf(marker)).filter(index => index >= 0);
  assert.ok(starts.length, `${name} missing`);
  const start = Math.min(...starts);
  const signatureEnd = source.indexOf(") {", start);
  assert.ok(signatureEnd >= 0, `${name} signature end missing`);
  const open = signatureEnd + 2;
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = open; index < source.length; index += 1) {
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

const helperStart = source.indexOf("    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT");
const helperEnd = source.indexOf("    function transportSweepVisibleDischargeButtons()", helperStart);
assert.ok(helperStart >= 0 && helperEnd > helperStart, "Optional release helper block missing");
const helperSource = source.slice(helperStart, helperEnd);
const releaseHelpers = ["recordTransportSweepConfirmedRelease"].map(extractFunction).join("\n\n");

function createHarness(pageCounts, options = {}) {
  const dom = new JSDOM("<!doctype html><html><body><main id=mission></main></body></html>", {
    url: "https://www.missionchief.co.uk/missions/9001",
  });
  let generation = 0;
  let poll = 0;
  let closes = 0;
  let opens = 0;
  const fetches = [];
  const order = [];
  const logs = [];
  const runtime = {
    running: true,
    stopRequested: false,
    cleared: 0,
    processed: 0,
    errors: 0,
    confirmedReleaseKeys: new Set(),
  };

  function countForGeneration() {
    return pageCounts[Math.min(generation, pageCounts.length - 1)] ?? 0;
  }

  function releaseLink(vehicleId) {
    return `<a class="btn btn-default btn-xs" href="/vehicles/${vehicleId}/patient/-1">Release patient (No reward)</a>`;
  }

  function render(includeButton = false) {
    const count = countForGeneration();
    const mission = dom.window.document.querySelector("#mission");
    if (!count) {
      mission.innerHTML = '<table id="mission_vehicle_at_mission"><tbody></tbody></table>';
      return;
    }
    const names = Array.from({ length: count }, (_, index) => `Patient ${index + 1}`).join(" , ");
    mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111" data-eligible="true"><td>ILB (ILB)<br>Patient: ${names}</td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;
    const control = mission.querySelector('a[href="/vehicles/111/patient/-1"]');
    if (control) control.click = () => { throw new Error("production must not use anchor.click()"); };
  }

  function injectDeferredControl() {
    const row = dom.window.document.querySelector('tr[data-eligible="true"]');
    const actions = row?.querySelector(".actions");
    if (!actions || actions.querySelector('a[href*="/patient/-1"]')) return;
    actions.innerHTML = releaseLink("111");
    actions.querySelector("a").click = () => { throw new Error("production must not use anchor.click()"); };
  }

  render(options.immediateButton === true);

  const sandbox = {
    console,
    Array,
    Map,
    Set,
    Math,
    Number,
    Object,
    RegExp,
    String,
    URL: dom.window.URL,
    location: dom.window.location,
    document: dom.window.document,
    pageWindow: dom.window,
    transportSweepRuntime: runtime,
    normaliseMissionId(value) {
      const text = String(value ?? "").trim();
      return /^\d+$/u.test(text) ? text : null;
    },
    normaliseTransportSweepReleaseText(value) {
      return String(value || "").replace(/\s+/gu, " ").trim().toLowerCase();
    },
    transportSweepElementVisible(element) { return Boolean(element?.isConnected); },
    transportSweepVisibleWindowRoots() { return [dom.window.document.body]; },
    transportSweepDocumentContexts() { return [{ doc: dom.window.document, label: "top" }]; },
    collectTransportSweepVehicleCandidatesForMission() {
      return Array.from(dom.window.document.querySelectorAll('tr[data-eligible="true"]')).map(row => ({
        vehicleId: row.id.match(/\d+$/u)?.[0] || "",
      }));
    },
    async transportSweepWaitFor(predicate) {
      for (let index = 0; index < 100; index += 1) {
        poll += 1;
        if (countForGeneration() > 0 && poll >= (options.injectAfterPolls ?? 3)) injectDeferredControl();
        const value = predicate();
        if (value) return value;
        await Promise.resolve();
      }
      return false;
    },
    runtimeSetTimeout(callback) { return dom.window.setTimeout(callback, 5000); },
    runtimeClearTimeout(handle) { dom.window.clearTimeout(handle); },
    async closeTransportSweepWindows() { order.push("close"); closes += 1; },
    async openTransportSweepPath(pathname) {
      assert.equal(pathname, "/missions/9001");
      order.push("reopen");
      opens += 1;
      if (options.failOpen) return false;
      generation += 1;
      poll = 0;
      render(false);
      return true;
    },
    transportSweepLog(message, level = "info") { logs.push({ message, level }); },
    renderTransportSweepPanel() {},
  };

  dom.window.fetch = async href => {
    order.push("fetch-start");
    fetches.push(String(href));
    if (options.failFetch) throw new Error("network failed");
    await new Promise(resolve => dom.window.setTimeout(resolve, options.fetchDelayMs ?? 10));
    order.push("fetch-complete");
    if (options.stopAfterFetch) runtime.stopRequested = true;
    return {
      ok: true,
      status: 200,
      url: String(href),
      async text() { return "released"; },
    };
  };

  vm.createContext(sandbox);
  vm.runInContext(
    `${releaseHelpers}\n${helperSource}\nthis.runOptionalRelease = processTransportSweepOptionalReleaseControls;`,
    sandbox,
    { filename: "issue565-live-release.js" },
  );

  return {
    runtime,
    fetches,
    order,
    logs,
    get opens() { return opens; },
    get closes() { return closes; },
    run(allowance = Number.POSITIVE_INFINITY) {
      return sandbox.runOptionalRelease({ caption: "Multi-patient mission" }, "9001", allowance);
    },
  };
}

{
  const harness = createHarness([3, 2, 1, 0], { injectAfterPolls: 4, fetchDelayMs: 12 });
  const outcome = await harness.run();
  assert.deepEqual(JSON.parse(JSON.stringify(outcome)), { cleared: 3, missionAvailable: true });
  assert.equal(harness.fetches.length, 3);
  assert.ok(harness.fetches.every(url => url.endsWith("/vehicles/111/patient/-1")));
  assert.equal(harness.runtime.cleared, 3);
  assert.equal(harness.runtime.processed, 3);
  assert.equal(harness.runtime.errors, 0);
  assert.equal(harness.opens, 3);
  assert.equal(harness.closes, 3);
  for (let index = 0; index < harness.order.length; index += 1) {
    if (harness.order[index] === "close") assert.equal(harness.order[index - 1], "fetch-complete");
  }
}

{
  const harness = createHarness([3, 2], { immediateButton: true });
  const outcome = await harness.run(1);
  assert.equal(outcome.cleared, 1);
  assert.equal(harness.fetches.length, 1);
}

{
  const harness = createHarness([2, 2], { immediateButton: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.fetches.length, 1, "unchanged patient count must stop repeated requests");
  assert.equal(harness.runtime.errors, 1);
  assert.match(harness.logs.at(-1).message, /did not reduce the patient count/u);
}

{
  const harness = createHarness([1], { immediateButton: true, failFetch: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(outcome.missionAvailable, true);
  assert.equal(harness.runtime.errors, 1);
  assert.equal(harness.closes, 0, "failed request must not close the mission before fallback");
}

{
  const harness = createHarness([1], { injectAfterPolls: 1000 });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.fetches.length, 0);
  assert.equal(outcome.missionAvailable, true);
}

{
  const harness = createHarness([1, 0], { immediateButton: true, stopAfterFetch: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.closes, 0);
}

console.log("Issue #565 v8.2.1 live release runtime passed: deferred controls, completed requests, same-vehicle 3→2→1→0, allowance, failure, no-control and cancellation.");
''')
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

static_test = clean(r'''#!/usr/bin/env python3
"""Issue #565 contract for completion-aware sequential optional releases."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
PERFORMANCE = ROOT / ".github/performance-budget.json"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert re.search(r"(?m)^//\s*@version\s+8\.2\.1$", source)
    assert "version: '8.2.1'" in source
    for marker in [
        "function transportSweepOptionalReleasePatientCount(control)",
        "function transportSweepOptionalReleaseState(missionId)",
        "async function waitForTransportSweepOptionalReleaseState(missionId, options = {})",
        "function transportSweepOptionalReleaseKey(missionId, vehicleId, sequence)",
        "async function requestTransportSweepOptionalRelease(release)",
        "function transportSweepOptionalReleaseProgressed(before, afterState)",
        "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)",
        "credentials: 'same-origin'",
        "await response.text()",
        "did not reduce the patient count",
        "completed no-reward patient release",
    ]:
        assert marker in source, marker

    helper = section(
        source,
        "    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT",
        "    function transportSweepVisibleDischargeButtons()",
    )
    assert "release.control.click()" not in helper
    assert ".click();" not in helper
    assert "MutationObserver" not in helper
    assert "setInterval(" not in helper
    assert "runtimeSetTimeout(" in helper and "runtimeClearTimeout(" in helper
    assert "pageWindow?.fetch" in helper
    assert "after.patientCount < before.patientCount" in helper
    assert "no-reward:${ordinal}" in helper

    processor = re.search(
        r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep",
        source,
    )
    assert processor
    body = processor.group(1)
    assert "processTransportSweepOptionalReleaseControls(" in body
    assert "optionalEligibleVehicleIds" not in body
    assert body.index("processTransportSweepOptionalReleaseControls(") < body.index("collectTransportSweepVehicleCandidatesForMission(missionId)")
    assert "openTransportSweepVehicle(candidate)" in body

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert ".github/scripts/test_issue565_transport_sweep_no_reward.py" in preflight
    assert ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs" in preflight
    assert "## [8.2.1] - 2026-07-28" in CHANGELOG.read_text(encoding="utf-8")
    assert "same vehicle" in HELP.read_text(encoding="utf-8").lower()

    performance = PERFORMANCE.read_text(encoding="utf-8")
    assert '"version": "8.2.1"' in performance
    assert '"approvedNetworkRequestDelta": 1' in performance
    assert '"network_request_calls": 6' in performance
    print("Issue #565 v8.2.1 completion-aware Transport Sweep contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''')
STATIC_TEST.write_text(static_test, encoding="utf-8")

performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
performance["revision"] = "2026-07-28-issue-565-transport-release-completion"
performance["rationale"] = "Issue #565 replaces abort-prone anchor clicking with one bounded same-origin request that must complete before mission cleanup, while adding no observer, interval or disabled-state work."
performance["transitionApproval"] = {
    "issue": 565,
    "version": "8.2.1",
    "approvedNetworkRequestDelta": 1,
    "scope": "Completion-aware optional patient release using the exact verified same-origin href, deferred-control waiting and same-vehicle patient-count verification.",
    "approvedMutationObserverDelta": 0,
}
performance["absoluteLimits"]["network_request_calls"] = 6
PERFORMANCE.write_text(json.dumps(performance, indent=2) + "\n", encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = clean('''
## [8.2.1] - 2026-07-28

### Critical Patient Transport Sweep release correction

- Waits boundedly for asynchronously inserted **Release patient (No reward)** controls before selecting native fallback.
- Replaces abort-prone anchor clicking with one completed same-origin request to the exact verified button href.
- Closes and reopens mission windows only after the release request has completed.
- Verifies patient-count reduction in the vehicle row before counting a release.
- Supports several patients on the same vehicle through unique per-patient confirmation identities.
- Stops safely on unchanged patient count, failed request, cancellation or mission reopen failure while retaining the native discharge fallback.
- Replaces the synchronous fake-click regression with delayed-control, delayed-request and same-vehicle `3 → 2 → 1 → 0` browser coverage.

''')
if "## [8.2.1]" not in changelog:
    insertion = changelog.index("\n", changelog.index("# Changelog")) + 1
    changelog = changelog[:insertion] + "\n" + entry + changelog[insertion:]
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
help_text = help_text.replace("Toolkit v8.2.0", "Toolkit v8.2.1")
help_text = help_text.replace("Guide for Toolkit v8.2.0 candidate", "Guide for Toolkit v8.2.1 candidate")
old_help = "When the opened mission exposes the exact <strong>Release patient (No reward)</strong> control, the sweep releases one patient, reopens the same mission, verifies that patient is gone and continues with the next patient. Missions with several patients are processed sequentially."
new_help = "When the opened mission exposes the exact <strong>Release patient (No reward)</strong> control, the sweep waits for deferred controls, completes the exact same-origin request, reopens the mission and verifies the vehicle patient count decreased. The same vehicle can be processed repeatedly for several patients until its count reaches zero."
if old_help in help_text:
    help_text = help_text.replace(old_help, new_help, 1)
else:
    help_text = help_text.replace("Patient Transport Sweep — no-reward fast path", "Patient Transport Sweep — completion-aware no-reward path", 1)
HELP.write_text(help_text, encoding="utf-8")

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.2.1"
help_manifest["toolkitVersion"] = "8.2.1"
help_manifest["updated"] = "2026-07-28"
help_manifest["runtimeGuidePatch"] = "Toolkit v8.2.1 waits for deferred no-reward controls, completes the exact same-origin request before cleanup and verifies same-vehicle patient-count reduction for repeated releases."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

DOC.write_text(clean('''
# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.1 recognises only the exact visible `Release patient (No reward)` control whose same-origin path matches `/vehicles/{vehicleId}/patient/-1` and whose vehicle is already verified by the existing sweep candidate collector.

The control may be inserted after mission render, so the sweep waits boundedly before selecting native fallback. It then completes one same-origin GET using the exact inspected href, waits for the response body, reopens the mission and verifies the patient count in that vehicle row has decreased. A vehicle carrying several patients may therefore be released repeatedly (`3 → 2 → 1 → 0`) with a unique confirmation identity for every patient.

A failed request, unchanged patient count, cancellation or failed mission reopen stops the optional path safely. The established MissionChief-native vehicle-window discharge process remains the fallback. The correction adds one user-invoked network-request site and no observer, interval or disabled-state work.
'''), encoding="utf-8")

source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
sha = hashlib.sha256(source_bytes).hexdigest()
source_lines = len(source_text.splitlines())
manifest_lines = source_text.count("\n") + 1
for relative in [
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{sha}  MissionChief_Map_Command_Toolkit.user.js\n{sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({"version": "8.2.1", "sha256": sha, "bytes": len(source_bytes), "lines": manifest_lines})
manifest["metadata"]["runtimeVersion"] = "8.2.1"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate["issue"] = 565
candidate["version"] = "8.2.1"
candidate["sourceBytes"] = len(source_bytes)
candidate["sourceLines"] = source_lines
candidate["sourceSha256"] = sha
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), source_lines + 250)
candidate["baseline"] = "8.2.0"
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + source_lines - old_lines
candidate["scope"] = "Issue #565 completion-aware same-origin no-reward release, deferred-control wait, same-vehicle patient-count verification and browser-faithful regression"
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"Toolkit v8.2.1 Patient Transport Sweep hotfix applied: {sha}, {len(source_bytes)} bytes, {source_lines} lines")
