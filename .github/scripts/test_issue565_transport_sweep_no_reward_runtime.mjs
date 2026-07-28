#!/usr/bin/env node
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
  let missionRowsReady = options.deferMissionRows !== true;
  const fetchPolls = [];
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
    if (!missionRowsReady) {
      mission.innerHTML = "";
      return;
    }
    if (!count) {
      mission.innerHTML = '<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111"><td>ILB (ILB)</td><td>Station</td><td>Owner</td><td class="actions"></td></tr></tbody></table>';
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
      for (let index = 0; index < 140; index += 1) {
        poll += 1;
        if (!missionRowsReady && poll >= (options.rowsAfterPolls ?? 4)) {
          missionRowsReady = true;
          render(false);
        }
        if (missionRowsReady && countForGeneration() > 0 && poll >= (options.injectAfterPolls ?? 3)) injectDeferredControl();
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
      missionRowsReady = options.deferMissionRowsOnReopen === true ? false : true;
      render(false);
      return true;
    },
    transportSweepLog(message, level = "info") { logs.push({ message, level }); },
    renderTransportSweepPanel() {},
  };

  dom.window.fetch = async href => {
    order.push("fetch-start");
    fetches.push(String(href));
    fetchPolls.push(poll);
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
    fetchPolls,
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
  const harness = createHarness([3, 2, 1, 0], {
    deferMissionRows: true,
    deferMissionRowsOnReopen: true,
    rowsAfterPolls: 4,
    injectAfterPolls: 9,
    fetchDelayMs: 12,
  });
  const outcome = await harness.run();
  assert.deepEqual(JSON.parse(JSON.stringify(outcome)), { cleared: 3, missionAvailable: true });
  assert.equal(harness.fetches.length, 3);
  assert.ok(harness.fetches.every(url => url.endsWith("/vehicles/111/patient/-1")));
  assert.equal(harness.runtime.cleared, 3);
  assert.equal(harness.runtime.processed, 3);
  assert.equal(harness.runtime.errors, 0);
  assert.ok(harness.fetchPolls.every(value => value >= 9), "release request must wait for delayed rows and controls");
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

console.log("Issue #565 v8.2.2 mission-readiness runtime passed: deferred controls, completed requests, same-vehicle 3→2→1→0, allowance, failure, no-control and cancellation.");
