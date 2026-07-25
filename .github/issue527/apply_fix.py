#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
STATIC_TEST = ROOT / ".github" / "scripts" / "test_issue527_transport_sweep_skipped_patients.py"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_issue527_transport_sweep_skipped_patients_runtime.js"
NATIVE_TEST = ROOT / ".github" / "scripts" / "test_transport_sweep_native_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
README = ROOT / "README.md"
HELP = ROOT / "help" / "index.html"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
SELF = ROOT / ".github" / "issue527" / "apply_fix.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue527-transport-sweep-skipped.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def function_bounds(source: str, name: str) -> tuple[int, int]:
    markers = [f"    function {name}(", f"    async function {name}("]
    starts = [source.find(marker) for marker in markers]
    starts = [index for index in starts if index >= 0]
    if not starts:
        raise SystemExit(f"Missing function {name}")
    start = min(starts)
    signature_end = source.find(") {", start)
    if signature_end < 0:
        raise SystemExit(f"Could not locate signature end for {name}")
    opening = signature_end + 2
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = opening
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char in {"'", '"', "`"}:
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
        index += 1
    raise SystemExit(f"Could not locate end of {name}")


def update_headroom(source: str) -> None:
    start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", start) + len("addStyle(`")
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, metric)
    raw = source[template_start:template_end]
    lines = raw.split("\n")
    canonical = re.sub(
        r"\n[\t ]*}",
        "}",
        "\n".join(
            line for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["v7Candidate"].update({
        "issue": 527,
        "version": "7.1.5",
        "sourceBytes": len(source.encode("utf-8")),
        "sourceLines": len(source.splitlines()),
        "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "templateBytes": len(raw.encode("utf-8")),
        "templateLines": len(lines),
        "templateSha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, "// @version      7.1.4", "// @version      7.1.5", "metadata version")
    source = replace_once(source, "version: '7.1.4',", "version: '7.1.5',", "runtime version")

    source = replace_once(
        source,
        "        confirmedReleaseKeys: new Set(),\n        rejectedOwn: 0,",
        "        confirmedReleaseKeys: new Set(),\n        skippedPatientKeys: new Set(),\n        rejectedOwn: 0,",
        "skipped patient identity state",
    )

    confirmed_start, confirmed_end = function_bounds(source, "recordTransportSweepConfirmedRelease")
    helper = """

    function recordTransportSweepSkippedPatient(skipKey, message) {
        const key = String(skipKey || '').trim();
        if (!key || transportSweepRuntime.confirmedReleaseKeys.has(key) || transportSweepRuntime.skippedPatientKeys.has(key)) return false;
        transportSweepRuntime.skippedPatientKeys.add(key);
        transportSweepRuntime.skipped += 1;
        transportSweepRuntime.processed += 1;
        transportSweepLog(message, 'warn');
        renderTransportSweepPanel();
        return true;
    }"""
    source = source[:confirmed_end] + helper + source[confirmed_end:]

    source = replace_once(
        source,
        """        if (!missionOpen || transportSweepRuntime.stopRequested) {
            if (!transportSweepRuntime.stopRequested) {
                transportSweepRuntime.skipped += 1;
                transportSweepLog(`Skipped ${item.caption} because its mission window did not become available`, 'warn');
            }
            return 0;
        }""",
        """        if (!missionOpen || transportSweepRuntime.stopRequested) {
            if (!transportSweepRuntime.stopRequested) {
                transportSweepLog(`Could not inspect ${item.caption} because its mission window did not become available; no patient skip was recorded`, 'warn');
            }
            return 0;
        }""",
        "mission-window fallback skip",
    )

    source = replace_once(
        source,
        """            let confirmedThisAttempt = false;
            if (!button) {
                transportSweepLog(`${candidate.label} is carrying a patient but is not transport-ready; continuing in the same mission`);
            } else {""",
        """            let confirmedThisAttempt = false;
            if (!button) {
                recordTransportSweepSkippedPatient(
                    transportSweepReleaseKey(missionId, candidate.vehicleId),
                    `Skipped ${candidate.label} at ${item.caption}: no usable Discharge patient control was available`
                );
            } else {""",
        "non-transport-ready patient skip",
    )

    source = replace_once(
        source,
        """        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) {
            transportSweepRuntime.skipped += 1;
            renderTransportSweepPanel();
        }
        return clearedHere;""",
        """        return clearedHere;""",
        "mission-level fallback skip",
    )

    source = replace_once(
        source,
        "        transportSweepRuntime.confirmedReleaseKeys = new Set();\n        transportSweepRuntime.rejectedOwn = 0;",
        "        transportSweepRuntime.confirmedReleaseKeys = new Set();\n        transportSweepRuntime.skippedPatientKeys = new Set();\n        transportSweepRuntime.rejectedOwn = 0;",
        "skipped patient run reset",
    )

    old_toast = """            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared · ${missionProgress.text} missions` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared · ${missionProgress.text} missions`);"""
    new_toast = """            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared · ${transportSweepRuntime.skipped} skipped · ${missionProgress.text} missions` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared · ${transportSweepRuntime.skipped} skipped · ${missionProgress.text} missions`);"""
    source = replace_once(source, old_toast, new_toast, "completion toast skipped count")

    if source.count("transportSweepRuntime.skipped += 1") != 1:
        raise SystemExit(f"Expected one canonical skipped increment, found {source.count('transportSweepRuntime.skipped += 1')}")

    SOURCE.write_text(source, encoding="utf-8")

    native = NATIVE_TEST.read_text(encoding="utf-8")
    native = replace_once(
        native,
        "'confirmedReleaseKeys: new Set()',",
        "'confirmedReleaseKeys: new Set()','skippedPatientKeys: new Set()','function recordTransportSweepSkippedPatient(skipKey, message)',",
        "native contract skip markers",
    )
    native = replace_once(
        native,
        "assert source.count('transportSweepRuntime.processed += 1')==1",
        "assert source.count('transportSweepRuntime.processed += 1')==2\nassert source.count('transportSweepRuntime.skipped += 1')==1",
        "native counter mutation contract",
    )
    NATIVE_TEST.write_text(native, encoding="utf-8")

    STATIC_TEST.write_text("""#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js'
def section(text,start,end):
 left=text.index(start);right=text.index(end,left);return text[left:right]
def main():
 source=SOURCE.read_text(encoding='utf-8')
 metadata=re.search(r'(?m)^//\\s*@version\\s+([^\\s]+)$',source);runtime=re.search(r"version:\\s*'([^']+)'",source)
 assert metadata and runtime and metadata.group(1)==runtime.group(1)=='7.1.5'
 for marker in ['skippedPatientKeys: new Set()','function recordTransportSweepSkippedPatient(skipKey, message)','transportSweepRuntime.skippedPatientKeys = new Set();']:
  assert marker in source,marker
 helper=section(source,'    function recordTransportSweepSkippedPatient(','    function transportSweepVisibleDischargeButtons(')
 processor=re.search(r'async function processTransportSweepMission\\(item, remainingAllowance\\) \\{([\\s\\S]*?)\\n    \\}\\n\\n    async function startTransportSweep',source);assert processor
 body=processor.group(1)
 assert source.count('transportSweepRuntime.skipped += 1')==1
 assert source.count('transportSweepRuntime.processed += 1')==2
 assert 'confirmedReleaseKeys.has(key)' in helper and 'skippedPatientKeys.has(key)' in helper
 assert 'renderTransportSweepPanel();' in helper and "transportSweepLog(message, 'warn');" in helper
 assert 'recordTransportSweepSkippedPatient(' in body
 assert 'transportSweepReleaseKey(missionId, candidate.vehicleId)' in body
 assert 'no usable Discharge patient control was available' in body
 assert 'transportSweepRuntime.skipped += 1' not in body
 assert 'clearedHere === 0' not in body
 assert 'no patient skip was recorded' in body
 assert '${transportSweepRuntime.skipped} skipped' in source
 print('Issue #527 skipped-patient static contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
""", encoding="utf-8")

    RUNTIME_TEST.write_text("""#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const signatureEnd=source.indexOf(') {',start);assert.ok(signatureEnd>=0);const open=signatureEnd+2;let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const logs=[];let renders=0;const runtime={cleared:0,skipped:0,processed:0,errors:0,confirmedReleaseKeys:new Set(),skippedPatientKeys:new Set(),missionIndex:2,missionTotal:4,completedMissionCount:1};
const sandbox={console,String,Math,transportSweepRuntime:runtime,transportSweepLog:(message,level)=>logs.push({message,level}),renderTransportSweepPanel:()=>{renders+=1;}};vm.createContext(sandbox);vm.runInContext(`${extractFunction('recordTransportSweepSkippedPatient')}\\nthis.recordTransportSweepSkippedPatient=recordTransportSweepSkippedPatient;`,sandbox);const record=sandbox.recordTransportSweepSkippedPatient;
assert.equal(record('101:201','Skipped patient one'),true);assert.equal(runtime.skipped,1);assert.equal(runtime.processed,1);assert.equal(renders,1);assert.equal(logs.length,1);
assert.equal(record('101:201','Duplicate patient one'),false);assert.equal(runtime.skipped,1);assert.equal(runtime.processed,1);assert.equal(renders,1);assert.equal(logs.length,1);
assert.equal(record('101:202','Skipped patient two'),true);assert.equal(runtime.skipped,2);assert.equal(runtime.processed,2);assert.equal(renders,2);
runtime.confirmedReleaseKeys.add('101:203');assert.equal(record('101:203','Must not skip a confirmed release'),false);assert.equal(runtime.skipped,2);assert.equal(runtime.processed,2);assert.equal(renders,2);
assert.equal(record('','No identity'),false);assert.equal(runtime.skipped,2);assert.equal(runtime.missionIndex,2);assert.equal(runtime.missionTotal,4);assert.equal(runtime.completedMissionCount,1);
console.log('Issue #527 skipped-patient runtime contract passed.');
""", encoding="utf-8")

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    preflight = replace_once(
        preflight,
        ".github/scripts/test_issue523_transport_sweep_progress.py; do",
        ".github/scripts/test_issue523_transport_sweep_progress.py .github/scripts/test_issue527_transport_sweep_skipped_patients.py; do",
        "Python preflight registration",
    )
    preflight = replace_once(
        preflight,
        "node .github/scripts/test_issue523_transport_sweep_progress_runtime.js\n",
        "node .github/scripts/test_issue523_transport_sweep_progress_runtime.js\nnode .github/scripts/test_issue527_transport_sweep_skipped_patients_runtime.js\n",
        "Node preflight registration",
    )
    PREFLIGHT.write_text(preflight, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    marker = "## [7.1.4] - 2026-07-25"
    section = """## [7.1.5] - 2026-07-25

### Patient Transport Sweep skipped-patient accounting

- Made **Skipped** an idempotent patient/vehicle outcome counter instead of a mission-level fallback.
- Counted each unique patient vehicle once when no usable native MissionChief **Discharge patient** control is available.
- Updated the persistent HUD and Toolkit panel immediately when a patient skip is recorded.
- Prevented mission-window failures and missions with no identifiable patient vehicle from fabricating skipped patients.
- Included skipped patients in the final completion toast while preserving errors and confirmed releases as separate outcomes.
- Added permanent static and executable coverage for duplicate observations, multiple skipped patients, confirmed-release exclusion and mission-progress isolation.

"""
    if marker not in changelog or "## [7.1.5]" in changelog:
        raise SystemExit("Unexpected changelog state")
    CHANGELOG.write_text(changelog.replace(marker, section + marker, 1), encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    readme, count = re.subn(
        r"## \*\*Current verified release: `v[^`]+`[^\n]*\*\*(?:\n### \*\*[^\n]+\*\*)?",
        "## **Current verified release: `v7.1.4` · Development candidate: `v7.1.5` — Patient Transport Sweep skipped-patient accounting**",
        readme,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Expected one README release heading, found {count}")
    README.write_text(readme, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = help_text.replace("v7.1.4 candidate", "v7.1.5 candidate")
    help_text, count = re.subn(
        r'<main><section class="notice"><h2>.*?</p></section>',
        '<main><section class="notice"><h2>What changed in v7.1.5</h2><p>Patient Transport Sweep now counts each identifiable patient vehicle skipped because no usable native Discharge patient control was available. The HUD and panel update immediately, duplicate observations cannot double-count, and mission progress remains independent.</p></section>',
        help_text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f"Expected one Help Centre notice, found {count}")
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("Issue #527 v7.1.5 skipped-patient accounting fix applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
