#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const catalogue = JSON.parse(fs.readFileSync("src/data/mission-requirements-en_GB.json", "utf8"));
const fixture = JSON.parse(fs.readFileSync(".github/fixtures/issue610-uk-knowledge-link.json", "utf8"));

function extractFunction(name) {
  const markers = [`    function ${name}(`, `    async function ${name}(`];
  const start = Math.max(...markers.map(marker => source.indexOf(marker)));
  assert.notEqual(start, -1, `${name} is missing`);
  const candidates = [
    source.indexOf("\n    function ", start + 20),
    source.indexOf("\n    async function ", start + 20),
    source.indexOf("\n    const ", start + 20),
  ].filter(index => index > start);
  const end = Math.min(...candidates);
  assert.ok(Number.isFinite(end), `Unable to find the end of ${name}`);
  return source.slice(start, end).trim();
}

const catalogueStart = source.indexOf("    const UK_VEHICLE_REQUIREMENT_CATALOGUE");
const catalogueEnd = source.indexOf("\n    const UK_GUIDE_KNOWLEDGE", catalogueStart);
assert.ok(catalogueStart >= 0 && catalogueEnd > catalogueStart);
const catalogueBlock = source.slice(catalogueStart, catalogueEnd).trim();
const configStart = source.indexOf("    const UK_GUIDE_KNOWLEDGE");
const configEnd = source.indexOf("\n    function ukKnowledgeText", configStart);
const configBlock = source.slice(configStart, configEnd).trim();

const sandbox = {
  console,
  URL,
  Date: class FixedDate extends Date {
    static now() {
      return fixture.fetchedAt;
    }
  },
  SCRIPT: {
    version: "9.2.0",
    ukKnowledgeCacheState: "uk-cache",
  },
  gmGetValueSafe() {
    return null;
  },
  gmSetValueSafe() {
    return true;
  },
};
vm.createContext(sandbox);
vm.runInContext(`
${extractFunction("normaliseSearchText")}
${extractFunction("escapeHtml")}
${catalogueBlock}
${configBlock}
${[
  "ukKnowledgeText",
  "ukKnowledgeStrings",
  "normaliseUkKnowledgeKey",
  "validateUkKnowledgeUnit",
  "validateUkKnowledgeRole",
  "validateUkKnowledgeCapability",
  "validateUkKnowledgePayload",
  "validateUkKnowledgeCache",
  "ukKnowledgeLocalCapability",
  "ukKnowledgeGuideHref",
  "ukKnowledgeRequirementModel",
  "ukKnowledgeTrainingHtml",
  "ukKnowledgeUnitsHtml",
  "ukKnowledgeRolesHtml",
  "ukKnowledgeRequirementReportUrl",
  "ukKnowledgeDossierHtml",
].map(extractFunction).join("\n")}
this.__probe = {
  validate: validateUkKnowledgePayload,
  validateCache: validateUkKnowledgeCache,
  model: ukKnowledgeRequirementModel,
  report: ukKnowledgeRequirementReportUrl,
  dossier: ukKnowledgeDossierHtml,
  normalise: normaliseUkKnowledgeKey
};`, sandbox, { filename: "issue610-uk-knowledge-runtime.js" });

const payload = sandbox.__probe.validate(
  fixture.capabilities,
  fixture.units,
  fixture.personnel,
  fixture.fetchedAt,
);
assert.equal(payload.schema, 1);
assert.equal(payload.dataVersion, "2026-07-30");
assert.equal(payload.units.length, 3);
assert.equal(payload.roles.length, 1);
assert.equal(payload.capabilities.length, 2);

const cacheRoundTrip = sandbox.__probe.validateCache(JSON.parse(JSON.stringify(payload)));
assert.ok(cacheRoundTrip, "normalised guide payload did not survive cache validation");
assert.equal(cacheRoundTrip.units[0].training[0].minimumTrainedStaff, 6);
assert.equal(cacheRoundTrip.units[0].training[0].appliesToAllStaff, true);
assert.equal(cacheRoundTrip.capabilities[0].qualifyingUnits.length, 2);
assert.equal(cacheRoundTrip.capabilities[0].verification.checkedAt, "2026-07-30");
assert.equal(cacheRoundTrip.roles[0].courses[0].durationDays, 3);

const hazmat = sandbox.__probe.model(
  "HazMat Unit or CBRN Vehicle",
  "hazmat-unit-or-cbrn-vehicle",
  payload,
  "live",
);
assert.equal(hazmat.known, true);
assert.equal(hazmat.units.length, 2);
assert.deepEqual(Array.from(hazmat.typeIds).slice(0, 2), [7, 32]);
assert.equal(hazmat.units[0].training[0].course, "HazMat");
assert.equal(hazmat.units[0].staffing.maximum, 6);
assert.equal(hazmat.roles[0].name, "HazMat-trained firefighter");
assert.match(hazmat.guideHref, /intelligence\/resources\/hazmat_unit_or_cbrn_vehicle\//u);
const hazmatHtml = sandbox.__probe.dossier(hazmat, {
  tone: "good",
  message: "<script>alert('status')</script>",
});
assert.match(hazmatHtml, /MissionChief type 7/u);
assert.match(hazmatHtml, /HazMat/u);
assert.match(hazmatHtml, /Fire Academy/u);
assert.match(hazmatHtml, /6 trained crew minimum/u);
assert.match(hazmatHtml, /all staff must qualify/u);
assert.match(hazmatHtml, /Associated personnel/u);
assert.match(hazmatHtml, /Refresh Guide data/u);
assert.match(hazmatHtml, /rel="noopener noreferrer"/u);
assert.doesNotMatch(hazmatHtml, /<script>/u);
assert.match(hazmatHtml, /&lt;script&gt;/u);
const hazmatDom = new JSDOM(`<main>${hazmatHtml}</main>`);
assert.equal(hazmatDom.window.document.querySelectorAll(".mcms-knowledge-unit").length, 2);
assert.equal(hazmatDom.window.document.querySelectorAll(".mcms-knowledge-roles a").length, 1);
assert.equal(hazmatDom.window.document.querySelectorAll("script").length, 0);
for (const anchor of hazmatDom.window.document.querySelectorAll("a[target='_blank']")) {
  assert.equal(anchor.rel, "noopener noreferrer");
}

const localOnly = sandbox.__probe.model("Fire Engine or RIV", "fire-engine-or-riv", null, "local");
assert.equal(localOnly.known, true);
assert.ok(localOnly.typeIds.includes(76), "combined local capability lost RIV type");
assert.equal(localOnly.units.length, 0);

const unknown = sandbox.__probe.model("<img src=x onerror=alert(1)>", "", payload, "live");
assert.equal(unknown.known, false);
assert.match(unknown.explanation, /catalogue drift/u);
const unknownHtml = sandbox.__probe.dossier(unknown);
assert.doesNotMatch(unknownHtml, /<img/u);
assert.match(unknownHtml, /&lt;img/u);
assert.match(unknownHtml, /CATALOGUE DRIFT/u);
assert.match(unknownHtml, /data-pressure-command="knowledge-report"/u);
const unknownDom = new JSDOM(`<main>${unknownHtml}</main>`);
assert.equal(unknownDom.window.document.querySelectorAll("img").length, 0);
assert.equal(unknownDom.window.document.querySelector("[data-pressure-command='knowledge-report']")?.textContent, "Report requirement");
const report = new URL(sandbox.__probe.report(unknown));
assert.equal(report.hostname, "github.com");
assert.equal(report.searchParams.get("template"), "mission-info-missing.yml");
assert.match(report.searchParams.get("diagnostic"), /No account, alliance, mission-instance, vehicle, location, cookie, token or webhook data/u);
assert.equal(report.searchParams.get("diagnostic").includes("1785456000000"), false);

assert.throws(
  () => sandbox.__probe.validate(
    { ...fixture.capabilities, collection: "wrong" },
    fixture.units,
    fixture.personnel,
    fixture.fetchedAt,
  ),
  /capability collection is invalid/u,
);
assert.throws(
  () => sandbox.__probe.validate(
    fixture.capabilities,
    { ...fixture.units, schema_version: "3.0.0" },
    fixture.personnel,
    fixture.fetchedAt,
  ),
  /unit collection is invalid/u,
);
assert.equal(sandbox.__probe.validateCache({ schema: 1, fetchedAt: 0, units: [], roles: [], capabilities: [] }), null);

const embeddedKeys = new Set(catalogue.vehicleRequirements.map(row => row.key));
for (const key of ["fire-engine", "hazmat-unit-or-cbrn-vehicle", "ambulance", "police-car"]) {
  assert.ok(embeddedKeys.has(key), `local fallback is missing ${key}`);
}

console.log("Issue #610 runtime passed: schema validation, update-stable cache, verified units/training/personnel, combined local fallback and privacy-safe drift reporting.");
