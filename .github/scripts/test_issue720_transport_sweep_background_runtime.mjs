#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const source = fs.readFileSync(path.join(root, "src", "MissionChief_Map_Command_Toolkit.user.js"), "utf8");
const start = source.indexOf("    function transportSweepBackgroundControlDisabled(control) {");
const end = source.indexOf("    async function collectTransportSweepVehicleCandidatesForMission(missionId) {", start);
assert.ok(start >= 0 && end > start, "background-first helper block must remain extractable");

const hostDom = new JSDOM("<!doctype html><html><body></body></html>", {
    url: "https://www.missionchief.co.uk/"
});
let personalIds = new Set();
const sandbox = {
    console,
    URL,
    Map,
    Set,
    Array,
    String,
    DOMParser: hostDom.window.DOMParser,
    pageWindow: { location: new URL("https://www.missionchief.co.uk/") },
    transportSweepRuntime: { stopRequested: false },
    transportSweepOwnVehicleIdSet: () => personalIds,
    transportSweepNativeReleaseControlText: control => String(
        control?.value || control?.textContent || control?.getAttribute?.("aria-label") || control?.title || ""
    ).replace(/\s+/gu, " ").trim().toLowerCase(),
    transportSweepReleaseConfirmationSignature: value => {
        const text = String(value || "").replace(/\s+/gu, " ").trim().toLowerCase();
        return text.includes("understood! we have released the patient.") ? "understood! we have released the patient." : "";
    },
    TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS: 6500,
    runtimeFetch: async () => { throw new Error("runtimeFetch mock not installed"); }
};
vm.createContext(sandbox);
vm.runInContext(`${source.slice(start, end)}
this.parseAction = transportSweepBackgroundCancelAction;
this.attemptRelease = transportSweepAttemptBackgroundRelease;`, sandbox);

const parse = html => new hostDom.window.DOMParser().parseFromString(html, "text/html");
const candidate = { vehicleId: "111", href: "/vehicles/111", label: "Alliance Ambulance" };

const exact = sandbox.parseAction(parse('<a href="/vehicles/111/patient/-1">Cancel Transport</a>'), candidate);
assert.equal(exact?.href, "https://www.missionchief.co.uk/vehicles/111/patient/-1");
assert.equal(exact?.patientId, "-1");

for (const html of [
    '<a href="https://evil.example/vehicles/111/patient/-1">Cancel Transport</a>',
    '<a href="/vehicles/222/patient/-1">Cancel Transport</a>',
    '<a href="/vehicles/111/patient/-1?retry=1">Cancel Transport</a>',
    '<a href="/vehicles/111/patient/nope">Cancel Transport</a>',
    '<a href="/vehicles/111/patient/-1" aria-disabled="true">Cancel Transport</a>',
    '<div hidden><a href="/vehicles/111/patient/-1">Cancel Transport</a></div>',
    '<a href="/vehicles/111/patient/-1" style="display:none">Cancel Transport</a>',
    '<button>Discharge patient</button>'
]) {
    assert.equal(sandbox.parseAction(parse(html), candidate), null, `must reject ${html}`);
}
assert.equal(sandbox.parseAction(parse(`
    <a href="/vehicles/111/patient/-1">Cancel Transport</a>
    <a href="/vehicles/111/patient/999">Cancel Transport</a>
`), candidate), null, "conflicting native actions must fail closed");

const response = (html, ok = true, status = ok ? 200 : 500) => ({ ok, status, text: async () => html });
const vehiclePage = '<!doctype html><html><body><a href="/vehicles/111/patient/-1">Cancel Transport</a></body></html>';

let calls = [];
sandbox.runtimeFetch = async (url, init) => {
    calls.push({ url: String(url), init });
    if (calls.length === 1) return response(vehiclePage);
    return response('<!doctype html><html><body><div id="notice">Understood! We have released the patient.</div></body></html>');
};
let result = await sandbox.attemptRelease(candidate);
assert.equal(result.status, "confirmed");
assert.equal(result.writeAttempted, true);
assert.equal(calls.length, 2);
assert.equal(calls[0].url, "/vehicles/111");
assert.equal(calls[1].url, "https://www.missionchief.co.uk/vehicles/111/patient/-1");
assert.equal(calls[1].init.method, "GET");
assert.equal(calls[1].init.credentials, "same-origin");

calls = [];
sandbox.runtimeFetch = async url => {
    calls.push(String(url));
    if (calls.length === 1) return response(vehiclePage);
    return response('<!doctype html><html><body><main>Vehicle page reloaded without confirmation.</main></body></html>');
};
result = await sandbox.attemptRelease(candidate);
assert.equal(result.status, "ambiguous");
assert.equal(result.writeAttempted, true);
assert.equal(calls.length, 2, "an ambiguous write must not be retried");

calls = [];
const staleConfirmationPage = '<!doctype html><html><body><div id="notice">Understood! We have released the patient.</div><a href="/vehicles/111/patient/-1">Cancel Transport</a></body></html>';
sandbox.runtimeFetch = async url => {
    calls.push(String(url));
    return response(staleConfirmationPage);
};
result = await sandbox.attemptRelease(candidate);
assert.equal(result.status, "ambiguous", "confirmation already present before the action is not fresh proof");
assert.equal(calls.length, 2);

calls = [];
sandbox.runtimeFetch = async url => {
    calls.push(String(url));
    return response('<!doctype html><html><body><button>Discharge patient</button></body></html>');
};
result = await sandbox.attemptRelease(candidate);
assert.equal(result.status, "unsupported");
assert.equal(result.writeAttempted, false);
assert.equal(calls.length, 1, "unsupported discovery must stop before any write");

calls = [];
personalIds = new Set(["111"]);
sandbox.runtimeFetch = async url => {
    calls.push(String(url));
    return response(vehiclePage);
};
result = await sandbox.attemptRelease(candidate);
assert.equal(result.status, "unsupported");
assert.match(result.reason, /personal ownership/u);
assert.equal(calls.length, 0, "a personal vehicle must be rejected before network activity");

const processStart = source.indexOf("    async function processTransportSweepMission(item, remainingAllowance) {");
const processEnd = source.indexOf("    async function startTransportSweep()", processStart);
assert.ok(processStart >= 0 && processEnd > processStart, "transport processor must remain extractable");

async function runProcessScenario(backgroundResult) {
    const openCalls = [];
    const ambiguousCalls = [];
    const confirmedCalls = [];
    let attemptCalls = 0;
    const runtime = {
        stopRequested: false,
        cleared: 0,
        releaseAttempts: 0,
        rejectedOwn: 0,
        lastCandidateStats: null,
        currentMissionId: null,
        currentVehicleHref: "",
        currentItem: ""
    };
    const processSandbox = {
        console,
        Set,
        String,
        state: { transportSweep: { backgroundFirst: true, maxPerRun: 25, delayMs: 0 } },
        transportSweepRuntime: runtime,
        normaliseMissionId: value => /^\d+$/u.test(String(value || "")) ? String(value) : null,
        renderTransportSweepPanel() {},
        transportSweepLog() {},
        openTransportSweepPath: async path => { openCalls.push(path); return true; },
        transportSweepFetchMissionCandidates: async () => ({
            candidates: [candidate],
            stats: { totalLinks: 1, allianceLinks: 1, candidates: 1, rejectedOwn: 0, source: "mission HTML" }
        }),
        collectTransportSweepVehicleCandidatesForMission: async () => [],
        transportSweepReleaseKey: (missionId, vehicleId) => `${missionId}:${vehicleId}`,
        transportSweepAttemptBackgroundRelease: async () => { attemptCalls += 1; return backgroundResult; },
        recordTransportSweepConfirmedRelease: (key, message) => {
            confirmedCalls.push({ key, message });
            runtime.cleared += 1;
            return true;
        },
        recordTransportSweepAmbiguousRelease: (key, message) => { ambiguousCalls.push({ key, message }); return true; },
        transportSweepSleep: async () => true,
        openTransportSweepVehicle: async () => null,
        transportSweepWaitFor: async () => null,
        findVisibleDischargePatientButton: () => null,
        recordTransportSweepSkippedPatient: () => true,
        captureTransportSweepReleaseConfirmationBaseline: () => new Map(),
        transportSweepNativeReleaseControlText: () => "cancel transport",
        clickTransportSweepDischargeConfirmation: () => false,
        transportSweepReleaseConfirmationVisible: () => false,
        closeTransportSweepWindows: async () => true
    };
    vm.createContext(processSandbox);
    vm.runInContext(`${source.slice(processStart, processEnd)}
this.processMission = processTransportSweepMission;`, processSandbox);
    await processSandbox.processMission({ missionId: "9001", caption: "Alliance incident" }, 1);
    return { openCalls, ambiguousCalls, confirmedCalls, attemptCalls, runtime };
}

let processResult = await runProcessScenario({ status: "unsupported", writeAttempted: false, reason: "no action" });
assert.equal(processResult.attemptCalls, 1);
assert.deepEqual(processResult.openCalls, ["/missions/9001"], "unsupported discovery must enter the visible native fallback");
assert.equal(processResult.runtime.releaseAttempts, 0, "pre-write fallback must not consume the action cap");

processResult = await runProcessScenario({ status: "ambiguous", writeAttempted: true, reason: "no fresh confirmation" });
assert.equal(processResult.attemptCalls, 1);
assert.equal(processResult.openCalls.length, 0, "an ambiguous write must never enter the visible fallback");
assert.equal(processResult.ambiguousCalls.length, 1);
assert.equal(processResult.runtime.releaseAttempts, 1, "an ambiguous write must consume the action cap");

processResult = await runProcessScenario({ status: "confirmed", writeAttempted: true });
assert.equal(processResult.openCalls.length, 0, "a confirmed background release must not open a lightbox");
assert.equal(processResult.confirmedCalls.length, 1);
assert.equal(processResult.runtime.releaseAttempts, 1);

console.log("Issue #720 runtime passed: background release is exact, same-origin, confirmed once, and fail-closed.");
