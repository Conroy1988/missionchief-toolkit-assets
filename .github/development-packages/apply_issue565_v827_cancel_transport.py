#!/usr/bin/env python3
"""Issue #565 v8.2.7: click MissionChief's real Cancel Transport control."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
EXPECTED_SHA = "f287e5694c0f617f1152d964f8084eae0c82a8bebe5d39bc5392339b364e3553"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
if hashlib.sha256(source.encode()).hexdigest() != EXPECTED_SHA:
    raise RuntimeError("Released v8.2.6 source authority moved")
source = replace_once(source, "// @version      8.2.6", "// @version      8.2.7", "metadata")
source = replace_once(source, "version: '8.2.6'", "version: '8.2.7'", "runtime")

old = """    function transportSweepVisibleDischargeButtons() {
        const buttons = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            let matches = [];
            try { matches = Array.from(context.doc.querySelectorAll('button')); } catch (err) {}
            for (const button of matches) {
                if (seen.has(button) || !transportSweepElementVisible(button) || button.disabled) continue;
                if (String(button.textContent || '').trim().toLowerCase() !== 'discharge patient') continue;
                seen.add(button);
                buttons.push(button);
            }
        }
        return buttons;
    }
"""
new = """    const TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS = new Set(['discharge patient', 'cancel transport']);

    function transportSweepNativeReleaseControlText(control) {
        return normaliseTransportSweepReleaseText(
            control?.value || control?.textContent || control?.getAttribute?.('aria-label') || control?.title || ''
        );
    }

    function transportSweepVisibleDischargeButtons() {
        const buttons = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            let matches = [];
            try {
                matches = Array.from(context.doc.querySelectorAll(
                    'button, a, input[type="button"], input[type="submit"]'
                ));
            } catch (err) {}
            for (const button of matches) {
                if (seen.has(button) || !transportSweepElementVisible(button) || button.disabled) continue;
                if (button.getAttribute?.('aria-disabled') === 'true') continue;
                if (!TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS.has(transportSweepNativeReleaseControlText(button))) continue;
                seen.add(button);
                buttons.push(button);
            }
        }
        return buttons;
    }
"""
source = replace_once(source, old, new, "release-control detector")
source = replace_once(
    source,
    """                    const confirmationBaseline = captureTransportSweepReleaseConfirmationBaseline();
                    transportSweepRuntime.pendingDischargeKey = releaseKey;
                    button.click();
""",
    """                    const confirmationBaseline = captureTransportSweepReleaseConfirmationBaseline();
                    const releaseControlLabel = transportSweepNativeReleaseControlText(button);
                    transportSweepRuntime.pendingDischargeKey = releaseKey;
                    button.click();
""",
    "release label baseline",
)
source = replace_once(
    source,
    "return normaliseTransportSweepReleaseText(button.textContent) !== 'discharge patient' ? true : null;",
    "return transportSweepNativeReleaseControlText(button) !== releaseControlLabel ? true : null;",
    "post-click transition",
)
source = replace_once(
    source,
    "no usable Discharge patient control was available",
    "no usable Cancel Transport or Discharge patient control was available",
    "skip copy",
)
source = replace_once(
    source,
    "The sweep opens verified alliance-owned FMS 5 patient vehicles and uses MissionChief's native Discharge patient control.",
    "The sweep opens verified alliance-owned FMS 5 patient vehicles and uses MissionChief's native Discharge patient control or Cancel Transport control.",
    "confirmation copy",
)
write("src/MissionChief_Map_Command_Toolkit.user.js", source)

write(".github/scripts/test_transport_sweep_native_contract.py", r'''#!/usr/bin/env python3
import re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
assert re.search(r'(?m)^//\s*@version\s+8\.2\.7$',s)
for marker in [
 "TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS = new Set(['discharge patient', 'cancel transport'])",
 'function transportSweepNativeReleaseControlText(control)',
 "'button, a, input[type=\"button\"], input[type=\"submit\"]'",
 "button.getAttribute?.('aria-disabled') === 'true'",
 'const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);',
 'const vehicleResult = await openTransportSweepVehicle(candidate);',
 'const releaseControlLabel = transportSweepNativeReleaseControlText(button);',
 'button.click();',
 'clickTransportSweepDischargeConfirmation(releaseKey);',
 'transportSweepNativeReleaseControlText(button) !== releaseControlLabel',
 'recordTransportSweepConfirmedRelease(',
 r"/patient (?:is not|isn['’]t) transported\.?/gi",
 "MissionChief's native Discharge patient control",
]: assert marker in s,marker
m=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',s);assert m
body=m.group(1)
assert "!== 'discharge patient'" not in body
print('Native Patient Transport Sweep Cancel Transport contract passed.')
''')

write(".github/scripts/test_issue565_transport_sweep_no_reward.py", r'''#!/usr/bin/env python3
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
h=(R/'help/index.html').read_text(encoding='utf-8')
c=(R/'CHANGELOG.md').read_text(encoding='utf-8')
p=json.loads((R/'.github/performance-budget.json').read_text(encoding='utf-8'))
assert re.search(r'(?m)^//\s*@version\s+8\.2\.7$',s)
assert "'cancel transport'" in s
assert 'const releaseControlLabel = transportSweepNativeReleaseControlText(button);' in s
assert 'transportSweepNativeReleaseControlText(button) !== releaseControlLabel' in s
assert '## [8.2.7] - 2026-07-29' in c
assert 'Cancel Transport' in h and 'Patient isn’t transported' in h
assert p['transitionApproval']['version']=='8.2.7'
assert p['transitionApproval']['approvedNetworkRequestDelta']==0
assert p['absoluteLimits']['network_request_calls']==5
print('Issue #565 v8.2.7 Cancel Transport contract passed.')
''')

write(".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs", r'''#!/usr/bin/env node
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
''')

performance=json.loads(read(".github/performance-budget.json"))
performance["revision"]="2026-07-29-issue-565-cancel-transport-control"
performance["rationale"]="Recognise MissionChief's real Cancel Transport link/button without adding requests, observers, intervals or Toolkit-managed timers."
performance["transitionApproval"]={
 "issue":565,"version":"8.2.7","approvedNetworkRequestDelta":0,
 "scope":"Discover and click the real Cancel Transport native vehicle control and verify its post-click transition.",
 "approvedMutationObserverDelta":0,
}
if not any(item.get("version")=="8.2.7" for item in performance.setdefault("approvalHistory",[])):
    performance["approvalHistory"].append(dict(performance["transitionApproval"]))
write(".github/performance-budget.json",json.dumps(performance,indent=2)+"\n")

changelog=read("CHANGELOG.md")
entry="""## [8.2.7] - 2026-07-29

### Patient Transport Sweep — click the real Cancel Transport control

- Fixed the vehicle window opening correctly but the sweep not clicking the visible **Cancel Transport** control.
- Discovers MissionChief native release controls rendered as links, buttons or submit inputs.
- Accepts both real labels: **Cancel Transport** and **Discharge patient**.
- Captures the original control label before clicking so an unchanged label cannot be mistaken for completion.
- Continues to require **Patient isn’t transported**, control removal/disablement or a genuine post-click transition.
- Adds no request, observer, interval or Toolkit-managed timer.

"""
if "## [8.2.7] - 2026-07-29" not in changelog:
    changelog=replace_once(changelog,"# Changelog\n\n","# Changelog\n\n"+entry,"changelog")
write("CHANGELOG.md",changelog)
write("docs/issue-565-transport-sweep-no-reward.md","""# Issue #565 — native Patient Transport Sweep restoration

Toolkit v8.2.7 follows the observed MissionChief UK flow: open the mission, open the flashing alliance-owned FMS 5 vehicle, click the visible **Cancel Transport** control, recognise **Patient isn’t transported**, then continue to the next patient and mission.

The control detector accepts links, buttons and submit inputs and supports both **Cancel Transport** and **Discharge patient**. It records the original label before clicking so an unchanged Cancel Transport label cannot be treated as successful completion.
""")
manifest=json.loads(read("help/manifest.json"))
manifest.update(guideVersion="8.2.7",toolkitVersion="8.2.7",updated="2026-07-29",runtimeGuidePatch="Toolkit v8.2.7 recognises and clicks the real Cancel Transport link/button and waits for Patient isn’t transported or a genuine native transition.")
write("help/manifest.json",json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
help_html=read("help/index.html").replace("8.2.6","8.2.7")
help_html,count=re.subn(r'<section id="transport-sweep-native">.*?</section>','<section id="transport-sweep-native"><h2>Patient Transport Sweep — native vehicle workflow</h2><p>The sweep opens the mission, opens the flashing alliance-owned FMS 5 vehicle, locates and clicks the native <strong>Cancel Transport</strong> control whether rendered as a link, button or submit input, recognises <strong>Patient isn’t transported</strong>, and repeats. The alternative native label <strong>Discharge patient</strong> remains supported.</p></section>',help_html,count=1,flags=re.S)
if count!=1: raise RuntimeError(f"help section matches: {count}")
write("help/index.html",help_html)
site=json.loads(read("docs/site-data.json"))
for category in site.get("featureCategories",[]):
    for feature in category.get("features",[]):
        if feature.get("name")=="Patient Transport Sweep":
            feature["summary"]="Opens each mission and alliance-owned FMS 5 patient vehicle, clicks MissionChief's real Cancel Transport control and verifies the native result."
            feature["details"]=["Mission-by-mission FMS 5 discovery","Cancel Transport link/button/input support","Discharge patient compatibility","Patient isn’t transported verification","Sequential patients and missions","Verified personal vehicle exclusion"]
write("docs/site-data.json",json.dumps(site,indent=2,ensure_ascii=False)+"\n")

headroom=json.loads(read(".github/fixtures/main-style-source-headroom.json"))
text=read("src/MissionChief_Map_Command_Toolkit.user.js")
start=text.index("function installMainStyles()")
ts=text.index("addStyle(`",start)+len("addStyle(`")
metric=text.index("recordStartupMetric('stylesheetInstallMs'",ts)
te=text.rfind("`);",ts,metric)
css=text[ts:te]; lines=css.split("\n")
canonical=re.sub(r"\n[\t ]*}","}","\n".join(line for index,line in enumerate(lines) if not (0<index<len(lines)-1 and not line.strip())))
candidate=headroom["v8Candidate"]
old_bytes=int(candidate["sourceBytes"]);old_lines=int(candidate["sourceLines"])
growth_bytes=int(candidate["approvedGrowth"]["sourceBytes"]);growth_lines=int(candidate["approvedGrowth"]["sourceLines"])
new_bytes=len(text.encode());new_lines=len(text.splitlines())
candidate.update(issue=565,version="8.2.7",sourceBytes=new_bytes,sourceLines=new_lines,sourceSha256=hashlib.sha256(text.encode()).hexdigest(),templateBytes=len(css.encode()),templateLines=len(lines),templateSha256=hashlib.sha256(css.encode()).hexdigest(),canonicalCssSha256=hashlib.sha256(canonical.encode()).hexdigest(),maxSourceBytes=new_bytes+20000,maxSourceLines=new_lines+250,baseline="8.2.6",scope="Issue #565 real Cancel Transport link/button discovery, click and post-click verification")
candidate["approvedGrowth"]={"sourceBytes":growth_bytes+new_bytes-old_bytes,"sourceLines":growth_lines+new_lines-old_lines,"templateBytes":0,"templateLines":0}
write(".github/fixtures/main-style-source-headroom.json",json.dumps(headroom,indent=2)+"\n")
print(json.dumps({"version":"8.2.7","sourceBytes":new_bytes,"sourceLines":new_lines,"sourceSha256":candidate["sourceSha256"]},indent=2))
