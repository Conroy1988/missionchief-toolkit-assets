#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const fixture = JSON.parse(fs.readFileSync(".github/fixtures/operational-pressure-board-contract.json", "utf8"));

function extractFunctions(names) {
  return names.map(name => {
    const marker = `    function ${name}(`;
    const start = source.indexOf(marker);
    assert.notEqual(start, -1, `${name} is missing`);
    const candidates = [
      source.indexOf("\n    function ", start + marker.length),
      source.indexOf("\n    async function ", start + marker.length),
      source.indexOf("\n    const ", start + marker.length),
    ].filter(index => index >= 0);
    const end = Math.min(...candidates);
    assert.ok(Number.isFinite(end), `Unable to find the end of ${name}`);
    return source.slice(start, end).trim();
  });
}

const functionNames = [
  "normaliseSearchText",
  "resourceSearchToken",
  "requirementSearchParts",
  "preparedVehicleMatchesRequirement",
  "haversineMiles",
  "operationalPressureRequirementKey",
  "formatOperationalPressureDuration",
  "calculateOperationalPressureModel",
  "escapeDiscordMarkdown",
  "truncateDiscord",
  "discordEmbedCharacterCount",
  "fitDiscordEmbedsToBudget",
  "operationalPressureSeverityLabel",
  "operationalSitrepMissionLink",
  "operationalSitrepActionsField",
  "operationalSitrepCapacityField",
  "buildOperationalSitrepPayload",
];

const catalogueStart = source.indexOf("    const UK_VEHICLE_REQUIREMENT_CATALOGUE");
const catalogueEnd = source.indexOf("\n    function resourceSearchToken", catalogueStart);
assert.ok(catalogueStart >= 0 && catalogueEnd > catalogueStart, "embedded UK vehicle catalogue is missing");
const catalogueBlock = source.slice(catalogueStart, catalogueEnd).trim();

const sandbox = {
  console,
  pageWindow: { location: { origin: "https://www.missionchief.co.uk" } },
  SCRIPT: { name: "MissionChief Map Command Toolkit", version: "9.1.0" },
  DISCORD_MAX_FIELD_LENGTH: 1024,
};
vm.createContext(sandbox);
const extracted = extractFunctions(functionNames);
vm.runInContext(`${extracted[0]}
${catalogueBlock}
${extracted.slice(1).join("\n")}
this.__probe = {
  token: resourceSearchToken,
  model: calculateOperationalPressureModel,
  payload: buildOperationalSitrepPayload,
  count: discordEmbedCharacterCount
};`, sandbox, { filename: "issue601-operational-pressure-runtime.js" });

const available = fixture.availableVehicles.map(vehicle => {
  const signal = sandbox.__probe.token(vehicle.signal);
  return {
    id: vehicle.id,
    typeId: vehicle.typeId,
    signal,
    tokens: new Set(vehicle.signal.split(/\s+/u).map(sandbox.__probe.token).filter(Boolean)),
    classificationSignal: "",
    classificationTokens: new Set(),
    point: { lat: vehicle.lat, lng: vehicle.lng },
  };
});
const model = sandbox.__probe.model(fixture.missions, { available }, {
  now: fixture.now,
  radiusMi: fixture.radiusMi,
  pinnedMissionIds: fixture.pinnedMissionIds,
  missionReady: true,
  vehicleReady: true,
  scope: "Contract missions",
});
const expected = fixture.expected;

assert.equal(model.missions, expected.missions);
assert.equal(model.resourcePressure.required, expected.required);
assert.equal(model.resourcePressure.assigned, expected.assigned);
assert.equal(model.resourcePressure.shortfall, expected.shortfall);
assert.equal(model.resourcePressure.allocatedVehicles, expected.allocatedVehicles);
assert.equal(model.transport.missions, expected.transportMissions);
assert.equal(model.transport.people, expected.transportPeople);
assert.equal(model.fleetConflicts.length, expected.fleetConflicts);
assert.equal(model.topActions[0].missionId, expected.topMissionId, "pinned mission did not lead Top Actions");
assert.equal(model.topActions[0].pinned, true);
assert.equal(model.severity, expected.severity);
assert.equal(model.complete, true);
assert.equal(model.locationEvidenceMissing, false);

const arv = model.resourcePressure.groups.find(group => group.key === "armed-response");
assert.ok(arv, "ARV pressure group is missing");
assert.equal(arv.demand, 2);
assert.equal(arv.available, 1);
assert.equal(arv.assigned, 1);
assert.equal(arv.shortfall, 1);
assert.equal(arv.conflict, true, "shared ARV demand was not detected as a fleet conflict");

const dsu = model.resourcePressure.groups.find(group => group.key === "dog-support-unit");
assert.ok(dsu, "DSU pressure group is missing");
assert.equal(dsu.available, 0);
assert.equal(dsu.shortfall, 1);

const payload = sandbox.__probe.payload(model);
assert.equal(payload.username, "MissionChief Operations");
assert.deepEqual(Array.from(payload.allowed_mentions.parse), []);
assert.equal(payload.embeds.length, 1);
const embed = payload.embeds[0];
assert.match(embed.title, /Operational SITREP · Critical pressure/u);
assert.ok(embed.fields.some(field => field.name === "Command Picture"));
assert.ok(embed.fields.some(field => field.name === "Resource Pressure"));
assert.ok(embed.fields.some(field => field.name === "Fleet Conflicts"));
assert.ok(embed.fields.some(field => field.name === "Top Actions"));
assert.ok(embed.fields.some(field => field.name === "Evidence Scope"));
assert.match(embed.fields.find(field => field.name === "Top Actions").value, /https:\/\/www\.missionchief\.co\.uk\/missions\/2002/u);
assert.match(embed.fields.find(field => field.name === "Fleet Conflicts").value, /Armed Response Vehicle/u);
assert.ok(embed.fields.every(field => field.name.length <= 256 && field.value.length <= 1000));
assert.ok(sandbox.__probe.count(embed) <= 5900, "SITREP exceeds the Discord embed budget");
assert.equal(JSON.stringify(payload).includes("/api/webhooks/"), false, "webhook leaked into the Discord payload");
assert.equal(JSON.stringify(payload).includes("@everyone"), false, "unsafe mention leaked into the Discord payload");

const duplicateVehicleModel = sandbox.__probe.model([
  {
    missionId: "one",
    caption: "First",
    source: "personal",
    unitsTotal: 1,
    createdAt: fixture.now,
    requirements: [{ name: "Ambulance", count: 1 }],
    lat: 51.5074,
    lng: -0.1278,
  },
  {
    missionId: "two",
    caption: "Second",
    source: "personal",
    unitsTotal: 1,
    createdAt: fixture.now,
    requirements: [{ name: "Ambulance", count: 1 }],
    lat: 51.5075,
    lng: -0.1279,
  },
], { available: [available[1]] }, {
  now: fixture.now,
  radiusMi: 25,
  missionReady: true,
  vehicleReady: true,
});
assert.equal(duplicateVehicleModel.resourcePressure.assigned, 1, "one vehicle was allocated to multiple missions");
assert.equal(duplicateVehicleModel.resourcePressure.shortfall, 1);

const scopeSandbox = {};
vm.createContext(scopeSandbox);
vm.runInContext(`${extractFunctions(["operationalPressureMissionInScope"]).join("\n")}
this.__probe = operationalPressureMissionInScope;`, scopeSandbox, {
  filename: "issue601-operational-pressure-scope-runtime.js",
});
assert.equal(scopeSandbox.__probe({ source: "personal" }, false), true, "personal missions must always remain in scope");
assert.equal(scopeSandbox.__probe({ source: "alliance", qualified: true }, false), false, "Alliance missions leaked into the default scope");
assert.equal(scopeSandbox.__probe({ source: "alliance", qualified: true }, true), true, "opted-in qualified Alliance mission was excluded");
assert.equal(scopeSandbox.__probe({ source: "alliance", qualified: false }, true), false, "unqualified Alliance mission entered pressure intelligence");
assert.equal(scopeSandbox.__probe({ source: "unknown" }, true), false, "unknown ownership entered pressure intelligence");

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "https://www.missionchief.co.uk/",
  pretendToBeVisual: true,
});
const interactionCalls = [];
const boardSandbox = {
  console,
  document: dom.window.document,
  SCRIPT: { pressureBoardId: "mc-map-command-toolkit-pressure-board" },
  setInnerHtmlIfChanged(element, html) {
    element.innerHTML = html;
    return true;
  },
  closestEventTarget(event, selector) {
    return event.target?.closest?.(selector) || null;
  },
  closeOperationalPressureBoard() {
    interactionCalls.push(["close"]);
  },
  refreshOperationalPressureBoard(force) {
    interactionCalls.push(["refresh", force]);
  },
  postOperationalSitrep() {
    interactionCalls.push(["sitrep"]);
  },
  toggleOperationalPressureAllianceScope() {
    interactionCalls.push(["alliance-scope"]);
  },
  toggleOperationalTimelineLogging() {
    interactionCalls.push(["timeline-logging"]);
  },
  focusMissionById(missionId, open) {
    interactionCalls.push(["mission", String(missionId), Boolean(open)]);
  },
  toggleOperationalPressurePin(missionId) {
    interactionCalls.push(["pin", String(missionId)]);
  },
};
vm.createContext(boardSandbox);
vm.runInContext(`${extractFunctions([
  "operationalPressureBoardElement",
  "createOperationalPressureBoard",
]).join("\n")}
this.__probe = { create: createOperationalPressureBoard };`, boardSandbox, {
  filename: "issue601-operational-pressure-board-dom.js",
});

const board = boardSandbox.__probe.create();
assert.equal(board.id, "mc-map-command-toolkit-pressure-board");
assert.equal(board.getAttribute("aria-label"), "Operational Pressure Board");
assert.equal(board.getAttribute("aria-hidden"), "true");
assert.equal(dom.window.document.querySelectorAll("#mc-map-command-toolkit-pressure-board").length, 1);
assert.ok(board.querySelector('[data-pressure-command="sitrep"]'));
assert.ok(board.querySelector('[data-pressure-command="refresh"]'));
assert.ok(board.querySelector('[data-pressure-command="close"]'));
assert.equal(board.querySelector('[data-pressure-command="alliance-scope"]').getAttribute("aria-pressed"), "false");
assert.equal(board.querySelector('[data-pressure-command="timeline-logging"]').getAttribute("aria-pressed"), "false");
assert.match(board.querySelector(".mcms-pressure-foot").textContent, /never select or dispatch vehicles/u);

board.querySelector("[data-pressure-body]").innerHTML = `
  <div class="mcms-pressure-action-controls">
    <button data-pressure-action="focus" data-mission-id="2001">Focus</button>
    <button data-pressure-action="open" data-mission-id="2002">Open</button>
    <button data-pressure-action="pin" data-mission-id="2003">Pin</button>
  </div>
`;
for (const selector of [
  '[data-pressure-command="sitrep"]',
  '[data-pressure-command="refresh"]',
  '[data-pressure-command="close"]',
  '[data-pressure-command="alliance-scope"]',
  '[data-pressure-command="timeline-logging"]',
  '[data-pressure-action="focus"]',
  '[data-pressure-action="open"]',
  '[data-pressure-action="pin"]',
]) {
  board.querySelector(selector).dispatchEvent(new dom.window.MouseEvent("click", { bubbles: true, cancelable: true }));
}
assert.deepEqual(interactionCalls, [
  ["sitrep"],
  ["refresh", true],
  ["close"],
  ["alliance-scope"],
  ["timeline-logging"],
  ["mission", "2001", false],
  ["mission", "2002", true],
  ["pin", "2003"],
]);
assert.strictEqual(boardSandbox.__probe.create(), board, "board creation was not idempotent");

const styleStart = source.indexOf("function installMainStyles()");
const templateStart = source.indexOf("addStyle(`", styleStart) + "addStyle(`".length;
const styleMetric = source.indexOf("recordStartupMetric('stylesheetInstallMs'", templateStart);
const templateEnd = source.lastIndexOf("`);", styleMetric);
assert.ok(styleStart >= 0 && templateStart >= 0 && styleMetric >= 0 && templateEnd > templateStart);
const stylesheet = source.slice(templateStart, templateEnd)
  .replace(/\$\{SCRIPT\.([A-Za-z0-9_]+)\}/gu, (_match, key) => key === "pressureBoardId" ? board.id : `mcms-${key}`)
  .replace(/\$\{THEME_ASSETS\.[^}]+\}/gu, "none");
const style = dom.window.document.createElement("style");
style.textContent = stylesheet;
dom.window.document.head.appendChild(style);
assert.ok(style.sheet, "main stylesheet did not parse");
assert.ok(style.sheet.cssRules.length > 100, "main stylesheet parsed incompletely");

board.classList.add("mcms-open");
const geometryKeys = ["position", "top", "right", "width", "maxHeight", "padding", "borderRadius"];
const themeGeometry = [];
const themeAccents = new Set();
for (const theme of ["mapCommand", "cyberpunk", "fallout4", "umbrella", "factorio", "bond007", "hyrule", "godfather"]) {
  dom.window.document.documentElement.dataset.mcmsUiTheme = theme;
  const computed = dom.window.getComputedStyle(board);
  assert.equal(computed.display, "block", `${theme}: board is not visible when open`);
  themeGeometry.push(geometryKeys.map(key => computed[key]));
  themeAccents.add(computed.getPropertyValue("--mcms-pressure-accent").trim());
}
themeGeometry.slice(1).forEach(geometry => assert.deepEqual(geometry, themeGeometry[0], "theme changed Pressure Board geometry"));
assert.ok(themeAccents.size >= 8, "themes did not retain distinct Pressure Board accents");

dom.window.document.documentElement.dataset.mcmsMobileActive = "true";
const mobileStyle = dom.window.getComputedStyle(board);
assert.equal(mobileStyle.position, "fixed");
assert.equal(mobileStyle.left, "0px");
assert.equal(mobileStyle.right, "0px");
assert.match(mobileStyle.paddingBottom, /safe-area-inset-bottom/u);
for (const button of board.querySelectorAll("button")) {
  const computed = dom.window.getComputedStyle(button);
  assert.ok(Number.parseFloat(computed.minHeight) >= 44, `mobile touch target is undersized: ${button.className || button.textContent}`);
  assert.ok(Number.parseFloat(computed.minWidth) >= 44, `mobile touch target is too narrow: ${button.className || button.textContent}`);
}
dom.window.close();

console.log("Issue #601 runtime passed: global fleet allocation, pressure ordering, reserve/conflict evidence and mention-safe Discord SITREP.");
