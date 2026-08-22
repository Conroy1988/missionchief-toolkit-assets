#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import { webcrypto } from "node:crypto";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const frameHtml = fs.readFileSync("devlab/frame.html", "utf8").replace(/<script src="\/devlab\/frame\.js"><\/script>/u, "");
const frameRuntime = fs.readFileSync("devlab/frame.js", "utf8");

async function waitFor(predicate, timeoutMs = 8000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = predicate();
    if (value) return value;
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  throw new Error("Dev Lab runtime probe timed out");
}

async function scenario(device, tab, focus = "") {
  const query = new URLSearchParams({ device, tab, focus, theme: "mapCommand" });
  const dom = new JSDOM(frameHtml, {
    url: `http://127.0.0.1:4173/devlab/frame.html?${query}`,
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
  const panel = await window.__MCMS_DEV_LAB_API__.boot({ sourceText: source });
  const report = await waitFor(() => window.__MCMS_DEV_LAB_LAST_REPORT__);
  assert.ok(panel.isConnected, `${device}: panel is detached`);
  assert.ok(panel.classList.contains("mcms-open"), `${device}: panel is closed`);
  assert.ok(window.document.querySelector("#mc-map-command-toolkit-control"), `${device}: command bar missing`);
  assert.ok(panel.querySelector(`.mcms-tab-panel[data-panel="${tab}"].mcms-active`), `${device}: ${tab} page not active`);
  if (focus) assert.ok(panel.querySelector(`[data-command-card="${focus}"].mcms-dev-focus`), `${device}: ${focus} focus missing`);
  assert.equal(report.mount, true, `${device}: mount probe failed`);
  assert.equal(report.runtimeHealthy, true, `${device}: runtime probe failed`);
  assert.equal(report.widthStable, true, `${device}: page navigation changed panel width by ${report.widthRange}`);
  assert.equal(report.noHorizontalOverflow, true, `${device}: horizontal overflow detected`);
  assert.equal(report.errors.length, 0, `${device}: runtime errors: ${report.errors.join(" | ")}`);
  if (tab === "map") {
    const launcher = panel.querySelector('[data-action="toggle-building-selector"]');
    assert.ok(launcher, `${device}: building selector launcher missing`);
    launcher.click();
    const selector = await waitFor(() => {
      const element = panel.querySelector("[data-building-visibility-selector]");
      return element && !element.hidden ? element : null;
    });
    await waitFor(() => selector.querySelectorAll("[data-building-type-row]").length >= 3);
    assert.ok(selector.querySelector('[data-action="building-type-only"]'), `${device}: building Only action missing`);
    assert.ok(selector.querySelector('[data-building-scope="both"].mcms-on'), `${device}: combined building scope missing`);
  }
  window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.destroy?.("Dev Lab test complete");
  window.__MCMS_DEV_LAB_OBSERVER__?.disconnect?.();
  dom.window.close();
}

await scenario("desktop", "dispatch", "expansion-and-upgrade-planner");
await scenario("tablet", "dispatch", "dispatch-recruitment");
await scenario("ios", "map");
console.log("Dev Lab mounted canonical source across Desktop, Tablet and iOS; page cycling retained width and produced no horizontal overflow or runtime errors.");
