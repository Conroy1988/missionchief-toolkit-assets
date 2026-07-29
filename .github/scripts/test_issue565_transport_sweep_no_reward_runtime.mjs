#!/usr/bin/env node
"use strict";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const source=fs.readFileSync(path.join(root,"src","MissionChief_Map_Command_Toolkit.user.js"),"utf8");
const start=source.indexOf("    const TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS");
const end=source.indexOf("    function transportSweepTopLevelWindowRoots()",start);
assert.ok(start>=0&&end>start);
const dom=new JSDOM(`<!doctype html><html><body>
<a id="cancel" class="btn btn-default" href="/vehicles/111/patient/-1">Cancel Transport</a>
<button id="discharge">Discharge patient</button>
<input id="input-cancel" type="submit" value="Cancel Transport">
<a id="other" href="#">Cancel mission</a>
</body></html>`,{url:"https://www.missionchief.co.uk/vehicles/111"});
const sandbox={console,Set,Array,String,
 normaliseTransportSweepReleaseText:value=>String(value||"").replace(/\s+/gu," ").trim().toLowerCase(),
 transportSweepDocumentContexts:()=>[{doc:dom.window.document}],
 transportSweepElementVisible:element=>Boolean(element?.isConnected)};
vm.createContext(sandbox);
vm.runInContext(`${source.slice(start,end)}\nthis.controls=transportSweepVisibleDischargeButtons;this.find=findVisibleDischargePatientButton;this.label=transportSweepNativeReleaseControlText;`,sandbox);
assert.deepEqual(sandbox.controls().map(control=>control.id),["cancel","discharge","input-cancel"]);
const cancel=dom.window.document.querySelector("#cancel");
assert.equal(sandbox.label(cancel),"cancel transport");
assert.equal(sandbox.find(new Set([cancel])).id,"discharge");
cancel.setAttribute("aria-disabled","true");
assert.deepEqual(sandbox.controls().map(control=>control.id),["discharge","input-cancel"]);
const a=source.indexOf("    async function processTransportSweepMission(item, remainingAllowance) {");
const z=source.indexOf("    async function startTransportSweep()",a);
const body=source.slice(a,z);
assert.ok(body.includes("const releaseControlLabel = transportSweepNativeReleaseControlText(button);"));
assert.ok(body.includes("transportSweepNativeReleaseControlText(button) !== releaseControlLabel"));
assert.equal(body.includes("!== 'discharge patient'"),false);
assert.ok(source.includes("patient (?:is not|isn['’]t) transported"));
console.log("Issue #565 v8.2.7 runtime passed: real Cancel Transport link/button/input discovery and safe completion.");
