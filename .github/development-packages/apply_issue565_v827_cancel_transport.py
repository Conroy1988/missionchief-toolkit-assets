#!/usr/bin/env python3
"""Issue #565 v8.2.7: recognise MissionChief's real Cancel Transport control."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
EXPECTED_SOURCE_SHA = "f287e5694c0f617f1152d964f8084eae0c82a8bebe5d39bc5392339b364e3553"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return value.replace(old, new, 1)


source = SOURCE_PATH.read_text(encoding="utf-8")
if hashlib.sha256(source.encode()).hexdigest() != EXPECTED_SOURCE_SHA:
    raise RuntimeError("Released v8.2.6 source authority moved")

source = replace_once(source, "// @version      8.2.6", "// @version      8.2.7", "metadata version")
source = replace_once(source, "version: '8.2.6'", "version: '8.2.7'", "runtime version")

old_detector = """    function transportSweepVisibleDischargeButtons() {
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
new_detector = """    const TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS = new Set(['discharge patient', 'cancel transport']);

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
source = replace_once(source, old_detector, new_detector, "native release-control detector")

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
    "capture native release label",
)
source = replace_once(
    source,
    "return normaliseTransportSweepReleaseText(button.textContent) !== 'discharge patient' ? true : null;",
    "return transportSweepNativeReleaseControlText(button) !== releaseControlLabel ? true : null;",
    "post-click label transition",
)
source = replace_once(
    source,
    "no usable Discharge patient control was available",
    "no usable Cancel Transport or Discharge patient control was available",
    "skip message",
)
source = replace_once(
    source,
    "The sweep opens verified alliance-owned FMS 5 patient vehicles and uses MissionChief's native Discharge patient control.",
    "The sweep opens verified alliance-owned FMS 5 patient vehicles and uses MissionChief's native Cancel Transport or Discharge patient control.",
    "confirmation copy",
)

for marker in [
    "TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS = new Set(['discharge patient', 'cancel transport'])",
    "button, a, input[type=\"button\"], input[type=\"submit\"]",
    "const releaseControlLabel = transportSweepNativeReleaseControlText(button);",
    "transportSweepNativeReleaseControlText(button) !== releaseControlLabel",
    "/patient (?:is not|isn['’]t) transported\\.?/gi",
]:
    if marker not in source:
        raise RuntimeError(f"Missing v8.2.7 marker: {marker}")
write("src/MissionChief_Map_Command_Toolkit.user.js", source)

native_contract = r'''#!/usr/bin/env python3
import re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
assert re.search(r'(?m)^//\s*@version\s+8\.2\.7$',s) and "version: '8.2.7'" in s
for x in [
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
]: assert x in s,x
m=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',s);assert m
b=m.group(1);cur=-1
for x in [
    "await openTransportSweepPath(`/missions/${missionId}`, 'mission')",
    'const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);',
    'const vehicleResult = await openTransportSweepVehicle(candidate);',
    'const releaseControlLabel = transportSweepNativeReleaseControlText(button);',
    'button.click();',
    'clickTransportSweepDischargeConfirmation(releaseKey);',
    'recordTransportSweepConfirmedRelease(',
]: cur=b.index(x,cur+1)
assert "!== 'discharge patient'" not in b
print('Native Patient Transport Sweep Cancel Transport contract passed.')
'''
write(".github/scripts/test_transport_sweep_native_contract.py", native_contract)

issue_contract = r'''#!/usr/bin/env python3
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
h=(R/'help/index.html').read_text(encoding='utf-8')
c=(R/'CHANGELOG.md').read_text(encoding='utf-8')
p=json.loads((R/'.github/performance-budget.json').read_text(encoding='utf-8'))
assert re.search(r'(?m)^//\s*@version\s+8\.2\.7$',s)
assert "'cancel transport'" in s
assert "querySelectorAll(\n                    'button, a, input[type=\"button\"], input[type=\"submit\"]'" in s
assert 'const releaseControlLabel = transportSweepNativeReleaseControlText(button);' in s
assert 'transportSweepNativeReleaseControlText(button) !== releaseControlLabel' in s
assert '## [8.2.7] - 2026-07-29' in c
assert 'Cancel Transport' in h and 'Patient isn’t transported' in h
assert p['transitionApproval']['version']=='8.2.7'
assert p['transitionApproval']['approvedNetworkRequestDelta']==0
assert p['absoluteLimits']['network_request_calls']==5
print('Issue #565 v8.2.7 Cancel Transport contract passed.')
'''
write(".github/scripts/test_issue565_transport_sweep_no_reward.py", issue_contract)

runtime_contract = r'''#!/usr/bin/env node
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
assert.ok(start>=0&&end>start,"native release-control helper block missing");
const block=source.slice(start,end);
const dom=new JSDOM(`<!doctype html><html><body>
<a id="cancel" class="btn btn-default" href="/vehicles/111/patient/-1">Cancel Transport</a>
<button id="discharge">Discharge patient</button>
<input id="input-cancel" type="submit" value="Cancel Transport">
<a id="unrelated" href="#">Cancel mission</a>
</body></html>`,{url:"https://www.missionchief.co.uk/vehicles/111"});
const sandbox={
 console,Set,Array,String,
 normaliseTransportSweepReleaseText:value=>String(value||"").replace(/\s+/gu," ").trim().toLowerCase(),
 transportSweepDocumentContexts:()=>[{doc:dom.window.document,label:"top"}],
 transportSweepElementVisible:element=>Boolean(element?.isConnected),
};
vm.createContext(sandbox);
vm.runInContext(`${block}\nthis.controls=transportSweepVisibleDischargeButtons;this.find=findVisibleDischargePatientButton;this.label=transportSweepNativeReleaseControlText;`,sandbox);
const controls=sandbox.controls();
assert.deepEqual(controls.map(control=>control.id),["cancel","discharge","input-cancel"]);
assert.equal(sandbox.label(dom.window.document.querySelector("#cancel")),"cancel transport");
assert.equal(sandbox.find(new Set([dom.window.document.querySelector("#cancel")])),dom.window.document.querySelector("#discharge"));
dom.window.document.querySelector("#cancel").setAttribute("aria-disabled","true");
assert.deepEqual(sandbox.controls().map(control=>control.id),["discharge","input-cancel"]);
const processorStart=source.indexOf("    async function processTransportSweepMission(item, remainingAllowance) {");
const processorEnd=source.indexOf("    async function startTransportSweep()",processorStart);
const processor=source.slice(processorStart,processorEnd);
assert.ok(processor.includes("const releaseControlLabel = transportSweepNativeReleaseControlText(button);"));
assert.ok(processor.includes("transportSweepNativeReleaseControlText(button) !== releaseControlLabel"));
assert.equal(processor.includes("!== 'discharge patient'"),false);
assert.match(source,/patient \(\?:is not\|isn\['’\]t\) transported/iu);
console.log("Issue #565 v8.2.7 runtime passed: anchor, button and input Cancel Transport controls are discovered without false completion.");
'''
write(".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs", runtime_contract)

performance = json.loads(read(".github/performance-budget.json"))
performance["revision"] = "2026-07-29-issue-565-cancel-transport-control"
performance["rationale"] = "Recognise MissionChief's real Cancel Transport anchor/button control without adding requests, observers, intervals or Toolkit-managed timers."
performance["transitionApproval"] = {
    "issue": 565,
    "version": "8.2.7",
    "approvedNetworkRequestDelta": 0,
    "scope": "Discover and click the real Cancel Transport native vehicle control and verify its post-click transition.",
    "approvedMutationObserverDelta": 0,
}
if not any(item.get("version") == "8.2.7" for item in performance.setdefault("approvalHistory", [])):
    performance["approvalHistory"].append(dict(performance["transitionApproval"]))
write(".github/performance-budget.json", json.dumps(performance, indent=2) + "\n")

changelog = read("CHANGELOG.md")
entry = """## [8.2.7] - 2026-07-29

### Patient Transport Sweep — click the real Cancel Transport control

- Fixed the vehicle window opening correctly but the sweep not clicking the visible **Cancel Transport** control.
- Discovers MissionChief native release controls rendered as links, buttons or submit inputs.
- Accepts both real labels: **Cancel Transport** and **Discharge patient**.
- Captures the original control label before clicking so **Cancel Transport** cannot be mistaken for an already-completed action.
- Continues to require the native **Patient isn’t transported** evidence, control removal/disablement or a genuine post-click control transition.
- Adds no request, observer, interval or Toolkit-managed timer.

"""
if "## [8.2.7] - 2026-07-29" not in changelog:
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + entry, "changelog insertion")
write("CHANGELOG.md", changelog)

write(
    "docs/issue-565-transport-sweep-no-reward.md",
    """# Issue #565 — native Patient Transport Sweep restoration

Toolkit v8.2.7 follows the observed MissionChief UK flow: open each mission, await the alliance-owned FMS 5 vehicle list, open the flashing vehicle, locate the visible **Cancel Transport** control, click it, recognise **Patient isn’t transported**, then continue to the next patient and mission.

The control detector now accepts native controls rendered as links, buttons or submit inputs and recognises both **Cancel Transport** and **Discharge patient**. It records the original label before clicking so the unchanged Cancel Transport label cannot be treated as successful completion. Verified personal vehicle IDs, bounded waits, cancellation, progress, duplicate protection and sweep-owned window cleanup remain preserved.
""",
)

manifest = json.loads(read("help/manifest.json"))
manifest.update(
    guideVersion="8.2.7",
    toolkitVersion="8.2.7",
    updated="2026-07-29",
    runtimeGuidePatch="Toolkit v8.2.7 recognises the real Cancel Transport link/button, clicks it and waits for Patient isn’t transported or a genuine native control transition.",
)
write("help/manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

help_html = read("help/index.html").replace("8.2.6", "8.2.7")
help_html, count = re.subn(
    r'<section id="transport-sweep-native">.*?</section>',
    '<section id="transport-sweep-native"><h2>Patient Transport Sweep — native vehicle workflow</h2><p>The sweep opens the mission, opens the flashing alliance-owned FMS 5 vehicle, locates the native <strong>Cancel Transport</strong> control whether MissionChief renders it as a link, button or submit input, clicks it, recognises <strong>Patient isn’t transported</strong>, and repeats for every eligible patient and mission. The alternative native label <strong>Discharge patient</strong> remains supported.</p></section>',
    help_html,
    count=1,
    flags=re.S,
)
if count != 1:
    raise RuntimeError(f"help section matches: {count}")
write("help/index.html", help_html)

site_data = json.loads(read("docs/site-data.json"))
found = False
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Patient Transport Sweep":
            feature["summary"] = "Opens each mission and alliance-owned FMS 5 patient vehicle, clicks MissionChief's real Cancel Transport control and verifies the native result."
            feature["details"] = [
                "Mission-by-mission FMS 5 vehicle discovery",
                "Cancel Transport link, button and submit-input support",
                "Discharge patient compatibility",
                "Patient isn’t transported verification",
                "Sequential patients and missions",
                "Verified personal vehicle exclusion",
            ]
            found = True
if not found:
    raise RuntimeError("site-data Patient Transport Sweep missing")
write("docs/site-data.json", json.dumps(site_data, indent=2, ensure_ascii=False) + "\n")

headroom = json.loads(read(".github/fixtures/main-style-source-headroom.json"))
text = read("src/MissionChief_Map_Command_Toolkit.user.js")
style_start = text.index("function installMainStyles()")
template_start = text.index("addStyle(`", style_start) + len("addStyle(`")
metric = text.index("recordStartupMetric('stylesheetInstallMs'", template_start)
template_end = text.rfind("`);", template_start, metric)
css = text[template_start:template_end]
css_lines = css.split("\n")
canonical = re.sub(
    r"\n[\t ]*}",
    "}",
    "\n".join(line for index, line in enumerate(css_lines) if not (0 < index < len(css_lines) - 1 and not line.strip())),
)
candidate = headroom["v8Candidate"]
previous_bytes = int(candidate["sourceBytes"])
previous_lines = int(candidate["sourceLines"])
previous_growth_bytes = int(candidate["approvedGrowth"]["sourceBytes"])
previous_growth_lines = int(candidate["approvedGrowth"]["sourceLines"])
source_bytes = len(text.encode())
source_lines = len(text.splitlines())
candidate.update(
    issue=565,
    version="8.2.7",
    sourceBytes=source_bytes,
    sourceLines=source_lines,
    sourceSha256=hashlib.sha256(text.encode()).hexdigest(),
    templateBytes=len(css.encode()),
    templateLines=len(css_lines),
    templateSha256=hashlib.sha256(css.encode()).hexdigest(),
    canonicalCssSha256=hashlib.sha256(canonical.encode()).hexdigest(),
    maxSourceBytes=source_bytes + 20000,
    maxSourceLines=source_lines + 250,
    baseline="8.2.6",
    scope="Issue #565 real Cancel Transport link/button discovery, click and post-click verification",
)
candidate["approvedGrowth"] = {
    "sourceBytes": previous_growth_bytes + source_bytes - previous_bytes,
    "sourceLines": previous_growth_lines + source_lines - previous_lines,
    "templateBytes": 0,
    "templateLines": 0,
}
write(".github/fixtures/main-style-source-headroom.json", json.dumps(headroom, indent=2) + "\n")

print(json.dumps({
    "version": "8.2.7",
    "sourceBytes": source_bytes,
    "sourceLines": source_lines,
    "sourceSha256": candidate["sourceSha256"],
    "controlLabels": ["Cancel Transport", "Discharge patient"],
    "controlElements": ["a", "button", "input[type=button]", "input[type=submit]"],
}, indent=2))
