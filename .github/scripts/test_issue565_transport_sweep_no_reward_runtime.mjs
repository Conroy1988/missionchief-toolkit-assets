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
const releaseHelpers = [
  "transportSweepReleaseKey",
  "recordTransportSweepConfirmedRelease",
].map(extractFunction).join("\n\n");

function createHarness(pages, options = {}) {
  const dom = new JSDOM("<!doctype html><html><body><main id=mission></main></body></html>", {
    url: "https://www.missionchief.co.uk/missions/9001",
  });
  let generation = 0;
  let opens = 0;
  let closes = 0;
  const clicks = [];
  const logs = [];
  const runtime = {
    running: true,
    stopRequested: false,
    cleared: 0,
    processed: 0,
    errors: 0,
    confirmedReleaseKeys: new Set(),
    missionIndex: 7,
    missionTotal: 11,
    completedMissionCount: 6,
  };

  function render() {
    const ids = pages[Math.min(generation, pages.length - 1)] || [];
    dom.window.document.querySelector("#mission").innerHTML = ids.map(id =>
      `<a class="btn btn-default btn-xs" href="/vehicles/${id}/patient/-1">Release patient (No reward)</a>`
    ).join("");
  }
  render();

  dom.window.document.addEventListener("click", event => {
    const anchor = event.target.closest?.('a[href*="/patient/-1"]');
    if (!anchor) return;
    event.preventDefault();
    const id = anchor.getAttribute("href").match(/\/vehicles\/(\d+)\//)?.[1] || "";
    clicks.push(id);
    anchor.remove();
    if (options.stopOnClick) runtime.stopRequested = true;
  });

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
    async transportSweepWaitFor(predicate) {
      for (let index = 0; index < 5; index += 1) {
        const value = predicate();
        if (value) return value;
        await Promise.resolve();
      }
      return false;
    },
    async closeTransportSweepWindows() { closes += 1; },
    async openTransportSweepPath(pathname) {
      assert.equal(pathname, "/missions/9001");
      opens += 1;
      if (options.failOpen) return false;
      generation += 1;
      render();
      return true;
    },
    transportSweepLog(message, level = "info") { logs.push({ message, level }); },
    renderTransportSweepPanel() {},
    renderTransportSweepHud() {},
  };
  vm.createContext(sandbox);
  vm.runInContext(
    `${releaseHelpers}\n${helperSource}\nthis.runOptionalRelease = processTransportSweepOptionalReleaseControls;`,
    sandbox,
    { filename: "issue565-optional-release.js" },
  );
  return {
    dom,
    runtime,
    clicks,
    logs,
    get opens() { return opens; },
    get closes() { return closes; },
    run(allowance = Number.POSITIVE_INFINITY, eligible = pages.flat()) {
      return sandbox.runOptionalRelease(
        { caption: "Multi-patient mission" },
        "9001",
        allowance,
        new Set(eligible.map(String)),
      );
    },
  };
}

{
  const harness = createHarness([["111"], ["222"], []]);
  const outcome = await harness.run();
  assert.deepEqual(JSON.parse(JSON.stringify(outcome)), { cleared: 2, missionAvailable: true });
  assert.deepEqual(harness.clicks, ["111", "222"]);
  assert.equal(harness.opens, 2);
  assert.equal(harness.closes, 2);
  assert.equal(harness.runtime.cleared, 2);
  assert.equal(harness.runtime.processed, 2);
  assert.equal(harness.runtime.errors, 0);
  assert.equal(harness.runtime.missionIndex, 7);
  assert.equal(harness.runtime.completedMissionCount, 6);
}

{
  const harness = createHarness([["111", "999"], ["999"]]);
  const outcome = await harness.run(Number.POSITIVE_INFINITY, ["111"]);
  assert.equal(outcome.cleared, 1);
  assert.deepEqual(harness.clicks, ["111"]);
  assert.ok(harness.dom.window.document.querySelector('a[href="/vehicles/999/patient/-1"]'));
}

{
  const harness = createHarness([[]]);
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(outcome.missionAvailable, true);
  assert.equal(harness.opens, 0);
  assert.equal(harness.clicks.length, 0);
}

{
  const harness = createHarness([["111"], ["111"]]);
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.clicks.length, 1, "A persistent release link must not be clicked repeatedly");
  assert.equal(harness.opens, 1);
  assert.equal(harness.runtime.errors, 1);
  assert.match(harness.logs.at(-1).message, /stopped repeated clicking/u);
}

{
  const harness = createHarness([["111"], ["222"]]);
  const outcome = await harness.run(1);
  assert.equal(outcome.cleared, 1);
  assert.deepEqual(harness.clicks, ["111"]);
  assert.equal(harness.opens, 1);
  assert.ok(harness.dom.window.document.querySelector('a[href="/vehicles/222/patient/-1"]'));
}

{
  const harness = createHarness([["111"], ["222"]], { stopOnClick: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.opens, 0);
  assert.equal(harness.runtime.cleared, 0);
}

{
  const harness = createHarness([["111"]], { failOpen: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(outcome.missionAvailable, false);
  assert.equal(harness.runtime.errors, 1);
}

console.log("Issue #565 optional no-reward Transport Sweep runtime passed: sequential reopening, persistence guard, allowance, fallback and cancellation.");
