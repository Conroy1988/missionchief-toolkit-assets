#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import crypto, { webcrypto } from "node:crypto";
import fs from "node:fs";
import { JSDOM } from "jsdom";

const loader = fs.readFileSync("tools/canary-loader.user.js", "utf8");
const manifestUrl = "https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/canary/canary/manifest.json";
const bundleUrl = "https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/canary/canary/MissionChief_Map_Command_Toolkit.canary.user.js";
const bundle = `window.__MCMS_CANARY_TEST_EXECUTED__ = (window.__MCMS_CANARY_TEST_EXECUTED__ || 0) + 1;\n${"/* canary fixture */\n".repeat(7000)}`;
const digest = crypto.createHash("sha256").update(bundle).digest("hex");
const manifest = {
  schemaVersion: 1,
  channel: "canary",
  buildId: "test-20260822-deadbeef",
  buildVersion: "10.15.3.20260822000000",
  stableVersion: "10.15.3",
  createdAt: "2026-08-22T00:00:00Z",
  minimumLoaderVersion: 1,
  source: { repository: "Conroy1988/missionchief-toolkit-assets", commit: "deadbeef".repeat(5), sha256: "0".repeat(64), bytes: 2700000 },
  bundle: { path: "canary/MissionChief_Map_Command_Toolkit.canary.user.js", url: bundleUrl, sha256: digest, bytes: new TextEncoder().encode(bundle).length },
};

function responseFor(url, mode) {
  if (mode === "network-failure") return { error: true };
  if (url.startsWith(manifestUrl)) return { status: 200, body: JSON.stringify(manifest) };
  if (url.startsWith(bundleUrl)) return { status: 200, body: mode === "corrupt" ? `${bundle}corrupt` : bundle };
  return { status: 404, body: "" };
}

async function waitFor(predicate, timeoutMs = 4000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = predicate();
    if (value) return value;
    await new Promise(resolve => setTimeout(resolve, 10));
  }
  throw new Error("Canary loader runtime probe timed out");
}

async function scenario({ mode, initial = new Map() }) {
  const dom = new JSDOM("<!doctype html><html><head></head><body></body></html>", {
    url: "https://www.missionchief.co.uk/",
    runScripts: "dangerously",
    pretendToBeVisual: true,
  });
  const { window } = dom;
  const gm = new Map(initial);
  const requests = [];
  let destroyed = 0;
  window.unsafeWindow = window;
  window.TextEncoder = globalThis.TextEncoder;
  Object.defineProperty(window, "crypto", { configurable: true, value: webcrypto });
  window.confirm = () => true;
  window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__ = { destroyed: false, destroy() { destroyed += 1; this.destroyed = true; } };
  window.GM_getValue = (key, fallback) => gm.has(key) ? gm.get(key) : fallback;
  window.GM_setValue = (key, value) => { gm.set(key, value); };
  window.GM_deleteValue = key => { gm.delete(key); };
  window.GM_xmlhttpRequest = options => {
    requests.push(options.url);
    const response = responseFor(options.url, mode);
    const timer = setTimeout(() => {
      if (response.error) options.onerror?.({});
      else options.onload?.({ status: response.status, responseText: response.body });
    }, 0);
    return { abort() { clearTimeout(timer); options.onabort?.(); } };
  };
  window.eval(loader);
  await waitFor(() => window.document.querySelector("#mcms-canary-loader-status"));
  await new Promise(resolve => setTimeout(resolve, 40));
  return { dom, window, gm, requests, destroyed, status: window.document.querySelector("#mcms-canary-loader-status").textContent };
}

const network = await scenario({ mode: "network" });
assert.equal(network.window.__MCMS_CANARY_TEST_EXECUTED__, 1, "Verified network canary did not execute");
assert.equal(network.destroyed, 1, "Stable runtime was not replaced exactly once");
assert.match(network.status, /hash verified/u);
assert.ok(network.gm.get("mcms_canary_loader_cache_v1"), "Verified canary was not cached");
assert.ok(network.gm.get("mcms_canary_loader_settings_backup_v1"), "Settings backup was not created");
network.dom.window.close();

const corrupt = await scenario({ mode: "corrupt" });
assert.equal(corrupt.window.__MCMS_CANARY_TEST_EXECUTED__, undefined, "Corrupt canary executed");
assert.equal(corrupt.destroyed, 0, "Stable runtime was destroyed for a corrupt canary");
assert.match(corrupt.status, /stable Toolkit retained/u);
corrupt.dom.window.close();

const cachedState = new Map([["mcms_canary_loader_cache_v1", { schemaVersion: 1, manifest, bundle }]]);
const cached = await scenario({ mode: "network-failure", initial: cachedState });
assert.equal(cached.window.__MCMS_CANARY_TEST_EXECUTED__, 1, "Verified cached canary did not execute");
assert.equal(cached.destroyed, 1, "Cached canary did not replace stable runtime exactly once");
assert.match(cached.status, /cached fallback/u);
cached.dom.window.close();

const paused = await scenario({ mode: "network", initial: new Map([["mcms_canary_loader_enabled_v1", false]]) });
assert.equal(paused.window.__MCMS_CANARY_TEST_EXECUTED__, undefined, "Paused canary executed");
assert.equal(paused.destroyed, 0, "Paused loader destroyed stable runtime");
assert.equal(paused.requests.length, 0, "Paused loader performed a network request");
assert.match(paused.status, /stable Toolkit active/u);
paused.dom.window.close();

console.log("Canary loader runtime passed: verified network execution, corrupt-bundle rejection, verified cached fallback and paused stable mode.");
