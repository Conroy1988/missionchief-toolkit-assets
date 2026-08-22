#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import { webcrypto } from "node:crypto";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const frameHtml = fs.readFileSync("devlab/frame.html", "utf8").replace(/<script src="\/devlab\/frame\.js"><\/script>/u, "");
const frameRuntime = fs.readFileSync("devlab/frame.js", "utf8");

async function waitFor(predicate, label, timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = predicate();
    if (value) return value;
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  throw new Error(`Timed out waiting for ${label}`);
}

const dom = new JSDOM(frameHtml, {
  url: "http://127.0.0.1:4173/devlab/frame.html?device=desktop&tab=dispatch&theme=mapCommand",
  pretendToBeVisual: true,
  runScripts: "dangerously",
});
const { window } = dom;
window.__MCMS_DEV_LAB_TEST__ = true;
window.Response = globalThis.Response;
window.Request = globalThis.Request;
window.Headers = globalThis.Headers;
window.TextEncoder = globalThis.TextEncoder;
window.TextDecoder = globalThis.TextDecoder;
Object.defineProperty(window, "crypto", { configurable: true, value: webcrypto });
window.eval(frameRuntime);

await window.__MCMS_DEV_LAB_API__.boot({ sourceText: source });
const firstRuntime = await waitFor(
  () => window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.version === "10.16.4" && window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__,
  "v10.16.4 runtime",
);
const firstControl = await waitFor(
  () => window.document.getElementById("mc-map-command-toolkit-control"),
  "v10.16.4 command launcher",
);
assert.ok(window.document.getElementById("mc-map-command-toolkit-style-v4146"), "v10.16.4 stylesheet is missing");

const upgradedSource = source
  .replace("// @version      10.16.4", "// @version      10.16.5")
  .replace("version: '10.16.4'", "version: '10.16.5'")
  .replace('version: "10.16.4"', 'version: "10.16.5"');
assert.match(upgradedSource, /^\/\/ @version\s+10\.16\.5$/mu);
assert.match(upgradedSource, /version: '10\.16\.5'/u);

const handoffMarker = "    // Issue #766: a working runtime is not destroyed until this replacement bundle has";
assert.ok(upgradedSource.includes(handoffMarker), "The deferred runtime handoff marker is missing");
const interruptedSource = upgradedSource.replace(handoffMarker, `    throw new Error("Issue #766 replacement evaluation interruption");\n${handoffMarker}`);
const expectedInterruption = event => {
  if (String(event.error?.message || event.message || "").includes("Issue #766 replacement evaluation interruption")) event.preventDefault();
};
window.addEventListener("error", expectedInterruption);
await window.__MCMS_DEV_LAB_API__.loadToolkit(interruptedSource);
await new Promise(resolve => setTimeout(resolve, 50));
window.removeEventListener("error", expectedInterruption);
assert.equal(window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__, firstRuntime, "An interrupted replacement stole runtime ownership");
assert.equal(firstRuntime.destroyed, false, "An interrupted replacement destroyed the working runtime");
assert.equal(window.document.getElementById("mc-map-command-toolkit-control"), firstControl, "An interrupted replacement removed the working launcher");

await window.__MCMS_DEV_LAB_API__.loadToolkit(upgradedSource);
const replacementRuntime = await waitFor(
  () => window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.version === "10.16.5" && window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__,
  "v10.16.5 replacement runtime",
);
const replacementControl = await waitFor(
  () => window.document.getElementById("mc-map-command-toolkit-control"),
  "v10.16.5 replacement command launcher",
);

assert.equal(firstRuntime.destroyed, true, "The superseded runtime was not shut down");
assert.equal(replacementRuntime.destroyed, false, "The replacement runtime is not active");
assert.notEqual(replacementControl, firstControl, "The upgrade reused the detached launcher");
assert.equal(window.document.querySelectorAll("#mc-map-command-toolkit-control").length, 1, "The upgrade did not leave exactly one launcher");
assert.ok(window.document.getElementById("mc-map-command-toolkit-style-v4146"), "The replacement stylesheet is missing");
replacementControl.querySelector(".mcms-menu-btn")?.click();
await waitFor(() => window.document.getElementById("mc-map-command-toolkit-panel"), "replacement command panel");

replacementControl.remove();
assert.equal(window.document.getElementById("mc-map-command-toolkit-control"), null, "The launcher removal fixture failed");
assert.equal(replacementRuntime.recoverUi(), true, "The runtime recovery entry point did not recover the command shell");
assert.ok(window.document.getElementById("mc-map-command-toolkit-control"), "The recovery entry point did not restore the launcher");

replacementRuntime.destroy("Issue #766 bootstrap runtime test complete");
window.__MCMS_DEV_LAB_OBSERVER__?.disconnect?.();
dom.window.close();
console.log("Issue #766 UI bootstrap runtime passed: the main launcher, panel, stylesheet and active runtime survive an exact same-page version replacement.");
