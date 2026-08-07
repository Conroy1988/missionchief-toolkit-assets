#!/usr/bin/env node
// v10.6.1 release title assertions must track the installed RELEASE_BRIEFING exactly.
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";


const source = fs.readFileSync(new URL("../../src/MissionChief_Map_Command_Toolkit.user.js", import.meta.url), "utf8");
const metadataVersion = source.match(/^\/\/\s*@version\s+([^\s]+)/mu)?.[1];
const runtimeVersion = source.match(/\bversion:\s*'([^']+)'/u)?.[1];
assert.equal(metadataVersion, "10.6.1");
assert.equal(runtimeVersion, metadataVersion);

const releaseStart = source.indexOf("    const RELEASE_BRIEFING = Object.freeze(");
const releaseEnd = source.indexOf("    const RUNTIME_KEY", releaseStart);
const briefingStart = source.indexOf("    function updateBriefingBody(");
const briefingEnd = source.indexOf("    function sessionCleanupSpawnLayers(", briefingStart);
assert.ok(releaseStart >= 0 && releaseEnd > releaseStart && briefingStart >= 0 && briefingEnd > briefingStart);

const opened = [];
let modal = null;
const sandbox = {
  SCRIPT: { version: runtimeVersion },
  state: { updateBriefing: { enabled: true } },
  escapeHtml(value) {
    return String(value).replace(/[&<>"']/gu, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
  },
  pageWindow: {
    open(...args) {
      const handle = { opener: "source-window" };
      opened.push({ args, handle });
      return handle;
    },
  },
  openCommandExperienceModal(value) {
    modal = value;
  },
  encodeURIComponent,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(
  `${source.slice(releaseStart, releaseEnd)}\n${source.slice(briefingStart, briefingEnd)}\n` +
    "globalThis.__api = { RELEASE_BRIEFING, updateBriefingBody, openToolkitReleaseNotes, openUpdateBriefing };",
  sandbox,
);

const { RELEASE_BRIEFING, updateBriefingBody, openToolkitReleaseNotes, openUpdateBriefing } = sandbox.__api;
const body = updateBriefingBody();
assert.match(body, /NOW INSTALLED/u);
assert.match(body, /v10\.6\.1/u);
assert.match(body, /iOS Patient Transport Sweep discovery repair/u);
for (const highlight of RELEASE_BRIEFING.highlights) assert.ok(body.includes(sandbox.escapeHtml(highlight)), highlight);
for (const stale of ["review every v10.2 feature", "Cleaner mission map and Alliance Chat", "Unit Locator &amp; Follow", "Session Cleanup</b>"]) {
  assert.ok(!body.includes(stale), stale);
}

assert.equal(openUpdateBriefing(), true);
assert.equal(modal.kind, "Update Briefing");
assert.equal(modal.title, "What’s New & Feature Beacon · v10.6.1");
assert.equal(modal.subtitle, "iOS Patient Transport Sweep discovery repair");
assert.equal(modal.body, body);

sandbox.state.updateBriefing.enabled = false;
modal = null;
assert.equal(openUpdateBriefing(), false);
assert.equal(modal, null);
assert.equal(openUpdateBriefing({ manual: true }), true);
assert.ok(modal);

openToolkitReleaseNotes();
assert.deepEqual(opened[0].args, [
  "https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v10.6.1",
  "_blank",
  "noopener,noreferrer",
]);
assert.equal(opened[0].handle.opener, null);

console.log("Issue #666 runtime passed: the launch modal renders only the installed release briefing and canonical patch-note route.");
