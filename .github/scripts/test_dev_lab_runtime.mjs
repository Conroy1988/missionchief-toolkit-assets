#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import { webcrypto } from "node:crypto";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const frameHtml = fs.readFileSync("devlab/frame.html", "utf8").replace(/<script src="\/devlab\/frame\.js"><\/script>/u, "");
const frameRuntime = fs.readFileSync("devlab/frame.js", "utf8");

async function waitFor(predicate, timeoutMs = 15000) {
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
  const control = window.document.querySelector("#mc-map-command-toolkit-control");
  assert.deepEqual(
    Array.from(control.querySelectorAll(".mcms-command-primary > button"), button => button.dataset.toggle || button.dataset.action),
    ["myMissions", "allianceMissions", "vehicles", "buildings", "open-command-palette"],
    `${device}: default primary commands drifted`,
  );
  assert.equal(control.querySelectorAll(".mcms-float-btn, .mcms-economy-btn").length, 15, `${device}: a legacy map command was lost`);
  const more = control.querySelector('[data-action="toggle-command-overflow"]');
  assert.equal(more?.querySelector(".mcms-command-more-count")?.textContent, "10", `${device}: overflow count is wrong`);
  more.click();
  assert.equal(control.querySelector(".mcms-command-overflow")?.hidden, false, `${device}: More did not reveal all other commands`);
  more.click();
  assert.equal(control.querySelector(".mcms-command-overflow")?.hidden, true, `${device}: More did not close cleanly`);
  assert.ok(panel.querySelector(`.mcms-tab-panel[data-panel="${tab}"].mcms-active`), `${device}: ${tab} page not active`);
  assert.deepEqual(
    Array.from(panel.querySelectorAll(".mcms-command-content > .mcms-tab-panel"), section => section.dataset.panel),
    ["map", "incidents", "fleet", "administration", "finance", "status", "settings"],
    `${device}: task navigation order drifted`,
  );
  assert.equal(panel.querySelectorAll('.mcms-command-card[data-workflow-ready="true"]').length, 5, `${device}: guided administration workflow count drifted`);
  panel.querySelectorAll('.mcms-command-card[data-workflow-ready="true"]').forEach(card => {
    assert.equal(card.querySelectorAll("[data-workflow-stage-button]").length, 5, `${device}: ${card.dataset.commandCard} stage count drifted`);
    assert.equal(card.dataset.workflowStage, "scope", `${device}: ${card.dataset.commandCard} did not start at Scope`);
  });
  assert.equal(panel.querySelectorAll("[data-operations-status-centre] .mcms-operations-status-card").length, 8, `${device}: status centre inventory drifted`);
  if (device === "ios") {
    assert.equal(panel.querySelectorAll(".mcms-mobile-nav > button").length, 5, "iOS: bottom navigation must expose five items");
    panel.querySelector('.mcms-mobile-nav [data-action="toggle-mobile-more"]').click();
    assert.equal(panel.querySelector(".mcms-mobile-more")?.hidden, false, "iOS: More sheet did not open");
    assert.deepEqual(Array.from(panel.querySelectorAll(".mcms-mobile-more [data-mobile-tab]"), button => button.dataset.mobileTab), ["finance", "status", "settings"], "iOS: More routes drifted");
  }
  if (focus) assert.ok(panel.querySelector(`[data-command-card="${focus}"].mcms-dev-focus`), `${device}: ${focus} focus missing`);
  assert.equal(report.mount, true, `${device}: mount probe failed`);
  assert.equal(report.runtimeHealthy, true, `${device}: runtime probe failed`);
  assert.equal(report.widthStable, true, `${device}: page navigation changed panel width by ${report.widthRange}`);
  assert.equal(report.noHorizontalOverflow, true, `${device}: horizontal overflow detected`);
  assert.equal(report.errors.length, 0, `${device}: runtime errors: ${report.errors.join(" | ")}`);
  if (tab === "administration") {
    const personnel = panel.querySelector('[data-setting="dispatch-recruitment-personnel"]');
    const delay = panel.querySelector('[data-setting="dispatch-recruitment-delay"]');
    assert.equal(personnel?.value, "400", `${device}: Expansion Planner rendering overwrote Personnel (Desired)`);
    personnel.focus();
    personnel.value = "275";
    personnel.dispatchEvent(new window.InputEvent("input", { bubbles: true, inputType: "insertText", data: "275" }));
    delay.focus();
    delay.value = "2000";
    delay.dispatchEvent(new window.Event("change", { bubbles: true }));
    assert.equal(personnel.value, "275", `${device}: Personnel (Desired) reverted after another Dispatch control changed`);
    const saved = JSON.parse(window.localStorage.getItem("mc_map_command_toolkit_state_v150"));
    assert.equal(saved.dispatchRecruitment.personnelDesired, "275", `${device}: Personnel (Desired) was not persisted after the full delegated UI flow`);
  }
  if (tab === "map") {
    const launcher = panel.querySelector('[data-toggle="buildings"]');
    assert.ok(launcher, `${device}: native building-filter launcher missing`);
    launcher.click();
    const popup = await waitFor(() => {
      const element = window.document.querySelector("#mc-map-command-toolkit-building-quick-filter");
      return element && !element.hidden ? element : null;
    });
    const buildingRows = Array.from(popup.querySelectorAll("[data-native-building-filter]"));
    assert.equal(buildingRows.length, 30, `${device}: popup did not contain the complete popularity-ranked building catalogue`);
    assert.deepEqual(
      buildingRows.slice(0, 3).map(row => row.querySelector(".mcms-native-building-copy strong")?.textContent.trim()),
      ["Ambulance Stations", "Police Stations", "Fire Stations"],
      `${device}: most-popular building filters changed order or label`,
    );
    assert.equal(buildingRows.at(-1)?.querySelector(".mcms-native-building-copy strong")?.textContent.trim(), "Building Complexes", `${device}: final popularity-ranked building filter changed`);
    assert.deepEqual(buildingRows.map(row => Number(row.dataset.popularityRank)), Array.from({ length: 30 }, (_, index) => index + 1), `${device}: popularity ranks are incomplete or out of order`);
    assert.deepEqual(
      Array.from(popup.querySelectorAll(".mcms-native-building-section-title"), element => element.textContent.trim()),
      ["Most popular", "All other buildings · popularity order"],
      `${device}: building filter sections changed`,
    );
    assert.equal(popup.querySelectorAll(".mcms-native-building-featured").length, 3, `${device}: the most-popular trio is not visually distinguished`);
    assert.equal(buildingRows.filter(row => row.disabled).length, 0, `${device}: a Dev Lab building filter could not bind to its native fixture control`);
    popup.querySelector('[data-native-building-filter="fire"]').click();
    await waitFor(() => !window.document.querySelector("#filter_2").checked);
    assert.equal(popup.hidden, false, `${device}: native filter click closed the popup before multi-selection`);
    assert.ok(panel.classList.contains("mcms-open"), `${device}: native filter click closed the settings panel`);
    popup.querySelector('[data-native-building-filter="ambulance"]').click();
    await waitFor(() => !window.document.querySelector("#filter_22").checked);
    assert.equal(popup.hidden, false, `${device}: second native filter click closed the popup`);
    popup.querySelector("[data-native-building-close]").click();
    assert.equal(popup.hidden, true, `${device}: popup close control failed`);
  }
  window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.destroy?.("Dev Lab test complete");
  window.__MCMS_DEV_LAB_OBSERVER__?.disconnect?.();
  dom.window.close();
}

await scenario("desktop", "administration", "expansion-and-upgrade-planner");
await scenario("tablet", "administration", "dispatch-recruitment");
await scenario("ios", "map");
console.log("Dev Lab mounted the task-based command interface across Desktop, Tablet and iOS; guided administration and complete popularity-ranked UK building filters retained stable width, native multi-selection and a clean runtime.");
