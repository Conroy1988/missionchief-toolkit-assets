#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
STATIC_TEST = ROOT / ".github" / "scripts" / "test_issue523_transport_sweep_progress.py"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_issue523_transport_sweep_progress_runtime.js"
CHANGELOG = ROOT / "CHANGELOG.md"
README = ROOT / "README.md"
HELP = ROOT / "help" / "index.html"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
SELF = ROOT / ".github" / "issue523" / "apply_fix.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue523-transport-sweep-progress.yml"
DIAGNOSTIC = ROOT / ".github" / "issue523" / "extract_transport_sweep.py"
DIAGNOSTIC_WORKFLOW = ROOT / ".github" / "workflows" / "diagnose-issue523-transport-sweep.yml"


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
    opening = source.find("{", start)
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
            line
            for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["v7Candidate"].update({
        "issue": 523,
        "version": "7.1.4",
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
    source = replace_once(source, "// @version      7.1.3", "// @version      7.1.4", "metadata version")
    source = replace_once(source, "version: '7.1.3',", "version: '7.1.4',", "runtime version")

    source = replace_once(
        source,
        "        missionIndex: 0,\n        missionTotal: 0,\n        currentItem: '',",
        "        missionIndex: 0,\n        missionTotal: 0,\n        completedMissionCount: 0,\n        currentItem: '',",
        "Transport Sweep mission progress state",
    )

    helper_marker = "    function renderTransportSweepHud() {"
    helpers = """    function transportSweepMissionProgress() {
        const sweep = transportSweepRuntime;
        const total = Math.max(0, Number(sweep.missionTotal) || Number(sweep.queue?.length) || 0);
        const current = total ? Math.min(total, Math.max(1, Number(sweep.missionIndex) || 1)) : 0;
        const completed = total ? Math.min(total, Math.max(0, Number(sweep.completedMissionCount) || 0)) : 0;
        return { current, total, completed, text: `${current}/${total}` };
    }

    function setTransportSweepMissionProgress(missionNumber, missionTotal = transportSweepRuntime.missionTotal, options = {}) {
        const total = Math.max(0, Number(missionTotal) || Number(transportSweepRuntime.queue?.length) || 0);
        const current = total ? Math.min(total, Math.max(1, Number(missionNumber) || 1)) : 0;
        const changed = current !== Number(transportSweepRuntime.missionIndex) || total !== Number(transportSweepRuntime.missionTotal);
        transportSweepRuntime.missionIndex = current;
        transportSweepRuntime.missionTotal = total;
        if (Object.prototype.hasOwnProperty.call(options, 'item')) transportSweepRuntime.currentItem = String(options.item || '');
        if (Object.prototype.hasOwnProperty.call(options, 'message')) transportSweepRuntime.statusMessage = String(options.message || '');
        if (options.level) transportSweepRuntime.statusLevel = String(options.level);
        if (options.render !== false && (changed || options.forceRender)) renderTransportSweepPanel();
        return transportSweepMissionProgress();
    }

    function completeTransportSweepMissionProgress(missionNumber, options = {}) {
        const progress = transportSweepMissionProgress();
        const completed = progress.total ? Math.min(progress.total, Math.max(0, Number(missionNumber) || 0)) : 0;
        const changed = completed > Number(transportSweepRuntime.completedMissionCount || 0);
        if (changed) transportSweepRuntime.completedMissionCount = completed;
        if (options.render !== false && (changed || options.forceRender)) renderTransportSweepPanel();
        return changed;
    }

    function finaliseTransportSweepMissionProgress(wasStopped = false) {
        const progress = transportSweepMissionProgress();
        if (!wasStopped && progress.total > 0) {
            transportSweepRuntime.missionIndex = progress.total;
            transportSweepRuntime.completedMissionCount = progress.total;
        }
        const finalProgress = transportSweepMissionProgress();
        renderTransportSweepPanel();
        return finalProgress;
    }

"""
    if source.count(helper_marker) != 1:
        raise SystemExit("Transport Sweep HUD function boundary is ambiguous")
    source = source.replace(helper_marker, helpers + helper_marker, 1)

    source = replace_once(
        source,
        "        const total = Math.max(0, Number(sweep.missionTotal) || Number(sweep.queue?.length) || 0);\n        const index = total ? Math.min(total, Math.max(1, Number(sweep.missionIndex) || 1)) : 0;",
        "        const progress = transportSweepMissionProgress();",
        "HUD mission progress derivation",
    )
    source = replace_once(
        source,
        '<span><b>${index}/${total}</b><small>Missions</small></span>',
        '<span><b>${escapeHtml(progress.text)}</b><small>Missions</small></span>',
        "HUD mission progress display",
    )

    source = replace_once(
        source,
        "        const runtime = transportSweepRuntime;\n        const queue = runtime.queue || [];",
        "        const runtime = transportSweepRuntime;\n        const queue = runtime.queue || [];\n        const missionProgress = transportSweepMissionProgress();",
        "panel mission progress state",
    )
    source = replace_once(
        source,
        '<div class="mcms-sweep-stat"><b>${queue.length}</b><span>Missions</span></div>',
        '<div class="mcms-sweep-stat"><b>${escapeHtml(missionProgress.text)}</b><span>Mission progress</span></div>',
        "panel mission progress display",
    )

    source = replace_once(
        source,
        "        transportSweepRuntime.startedAt = Date.now();\n        transportSweepRuntime.missionIndex = 0;\n        transportSweepRuntime.missionTotal = queue.length;\n        transportSweepRuntime.currentItem = 'Preparing sweep';\n        transportSweepRuntime.statusMessage = 'Preparing patient transport sweep';",
        "        transportSweepRuntime.startedAt = Date.now();\n        transportSweepRuntime.completedMissionCount = 0;\n        setTransportSweepMissionProgress(queue.length ? 1 : 0, queue.length, {\n            item: 'Preparing sweep',\n            message: 'Preparing patient transport sweep',\n            render: false\n        });",
        "Transport Sweep initial mission progress",
    )

    old_loop = """            for (let missionOffset = 0; missionOffset < queue.length; missionOffset += 1) {
                const item = queue[missionOffset];
                if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;
                transportSweepRuntime.missionIndex = missionOffset + 1;
                transportSweepRuntime.currentItem = String(item?.caption || `Mission ${item?.missionId || missionOffset + 1}`);
                renderTransportSweepPanel();
                const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;
                await processTransportSweepMission(item, remaining);
                if (!transportSweepRuntime.stopRequested) await transportSweepSleep(state.transportSweep.delayMs);
            }"""
    new_loop = """            for (let missionOffset = 0; missionOffset < queue.length; missionOffset += 1) {
                const item = queue[missionOffset];
                if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;
                const missionNumber = missionOffset + 1;
                const missionLabel = String(item?.caption || `Mission ${item?.missionId || missionNumber}`);
                setTransportSweepMissionProgress(missionNumber, queue.length, {
                    item: missionLabel,
                    message: `Processing mission ${missionNumber} of ${queue.length}`,
                    forceRender: true
                });
                const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;
                try {
                    await processTransportSweepMission(item, remaining);
                } catch (err) {
                    transportSweepRuntime.errors += 1;
                    transportSweepLog(`Mission ${missionLabel} failed: ${err?.message || 'unknown error'}`, 'error');
                    await closeTransportSweepWindows('recovering from a mission error');
                } finally {
                    transportSweepRuntime.currentItem = missionLabel;
                    completeTransportSweepMissionProgress(missionNumber, { forceRender: true });
                }
                if (!transportSweepRuntime.stopRequested) await transportSweepSleep(state.transportSweep.delayMs);
            }"""
    source = replace_once(source, old_loop, new_loop, "Transport Sweep queue loop")

    source = replace_once(
        source,
        "            transportSweepRuntime.hudFinal = true;\n            buildTransportSweepQueue();",
        "            transportSweepRuntime.hudFinal = true;\n            const missionProgress = finaliseTransportSweepMissionProgress(wasStopped);\n            buildTransportSweepQueue();",
        "Transport Sweep final mission progress",
    )
    source = replace_once(
        source,
        "            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared`);",
        "            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared · ${missionProgress.text} missions` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared · ${missionProgress.text} missions`);",
        "Transport Sweep completion toast",
    )
    source = replace_once(
        source,
        "            transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`, transportSweepRuntime.errors ? 'error' : 'info');",
        "            transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: missions ${missionProgress.text}, ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`, transportSweepRuntime.errors ? 'error' : 'info');",
        "Transport Sweep completion log",
    )

    SOURCE.write_text(source, encoding="utf-8")

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
 assert metadata and runtime and metadata.group(1)==runtime.group(1)=='7.1.4'
 for marker in ['completedMissionCount: 0','function transportSweepMissionProgress()','function setTransportSweepMissionProgress(','function completeTransportSweepMissionProgress(','function finaliseTransportSweepMissionProgress(']: assert marker in source,marker
 hud=section(source,'    function renderTransportSweepHud()','    function renderTransportSweepPanel()')
 panel=section(source,'    function renderTransportSweepPanel()','    function transportSweepMissionRequirementText(')
 processor=re.search(r'async function processTransportSweepMission\\(item, remainingAllowance\\) \\{([\\s\\S]*?)\\n    \\}\\n\\n    async function startTransportSweep',source);assert processor
 start=section(source,'    async function startTransportSweep()','    function stopTransportSweep(')
 assert 'const progress = transportSweepMissionProgress();' in hud and 'escapeHtml(progress.text)' in hud
 assert 'const missionProgress = transportSweepMissionProgress();' in panel and 'escapeHtml(missionProgress.text)' in panel and 'Mission progress' in panel
 assert 'setTransportSweepMissionProgress(queue.length ? 1 : 0, queue.length' in start
 assert 'setTransportSweepMissionProgress(missionNumber, queue.length' in start
 assert 'completeTransportSweepMissionProgress(missionNumber, { forceRender: true })' in start
 assert 'finally {' in start and "recovering from a mission error" in start
 assert 'finaliseTransportSweepMissionProgress(wasStopped)' in start
 assert 'missionProgress.text' in start
 assert 'transportSweepRuntime.missionIndex = missionOffset + 1' not in source
 patient_body=processor.group(1)
 for forbidden in ['missionIndex','setTransportSweepMissionProgress','completeTransportSweepMissionProgress','finaliseTransportSweepMissionProgress']: assert forbidden not in patient_body,forbidden
 assert "if (!wasStopped && progress.total > 0)" in source
 assert 'transportSweepRuntime.missionIndex = progress.total;' in source
 assert 'transportSweepRuntime.completedMissionCount = progress.total;' in source
 print('Issue #523 Transport Sweep mission-progress static contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
""", encoding="utf-8")

    RUNTIME_TEST.write_text("""#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const markers=[`    function ${name}(`,`    async function ${name}(`];const starts=markers.map(marker=>source.indexOf(marker)).filter(index=>index>=0);assert.ok(starts.length,`${name} missing`);const start=Math.min(...starts);const open=source.indexOf('{',start);let depth=0,quote='',escaped=false;for(let index=open;index<source.length;index+=1){const char=source[index];if(quote){if(escaped)escaped=false;else if(char==='\\\\')escaped=true;else if(char===quote)quote='';continue;}if(char==='"'||char==="'"||char==='`'){quote=char;continue;}if(char==='{')depth+=1;if(char==='}'&&--depth===0)return source.slice(start,index+1);}throw new Error(`Could not extract ${name}`);}
const names=['transportSweepMissionProgress','setTransportSweepMissionProgress','completeTransportSweepMissionProgress','finaliseTransportSweepMissionProgress'];let renders=0;
const runtime={queue:[{},{},{}],missionIndex:0,missionTotal:0,completedMissionCount:0,currentItem:'',statusMessage:'',statusLevel:'info',cleared:0,processed:0,skipped:0,errors:0};
const sandbox={console,Math,Number,String,Boolean,Object,transportSweepRuntime:runtime,renderTransportSweepPanel:()=>{renders+=1;}};vm.createContext(sandbox);vm.runInContext(`${names.map(extractFunction).join('\\n\\n')}\\nthis.api={${names.join(',')}};`,sandbox);const api=sandbox.api;
let progress=api.setTransportSweepMissionProgress(1,3,{item:'Mission one',message:'Processing mission 1 of 3',render:false});assert.deepEqual(JSON.parse(JSON.stringify(progress)),{current:1,total:3,completed:0,text:'1/3'});assert.equal(runtime.currentItem,'Mission one');assert.equal(renders,0);
runtime.cleared=3;runtime.processed=3;assert.equal(api.transportSweepMissionProgress().text,'1/3','Patient outcomes must not increment mission progress');
assert.equal(api.completeTransportSweepMissionProgress(1,{forceRender:true}),true);assert.equal(runtime.completedMissionCount,1);assert.equal(api.completeTransportSweepMissionProgress(1,{forceRender:true}),false,'Repeated finalisation must not increment twice');assert.equal(runtime.completedMissionCount,1);
progress=api.setTransportSweepMissionProgress(2,3,{forceRender:true});assert.equal(progress.text,'2/3');runtime.skipped+=1;assert.equal(api.completeTransportSweepMissionProgress(2,{forceRender:true}),true);assert.equal(runtime.completedMissionCount,2);
runtime.errors+=1;assert.equal(api.completeTransportSweepMissionProgress(2,{forceRender:true}),false,'Mission-level error reconciliation must remain idempotent');assert.equal(api.transportSweepMissionProgress().text,'2/3');
progress=api.finaliseTransportSweepMissionProgress(true);assert.equal(progress.text,'2/3','Cancellation must preserve the last accurate mission position');assert.equal(runtime.completedMissionCount,2);
runtime.missionIndex=1;runtime.missionTotal=3;runtime.completedMissionCount=0;api.completeTransportSweepMissionProgress(1,{render:false});api.setTransportSweepMissionProgress(2,3,{render:false});api.completeTransportSweepMissionProgress(2,{render:false});api.setTransportSweepMissionProgress(3,3,{render:false});api.completeTransportSweepMissionProgress(3,{render:false});progress=api.finaliseTransportSweepMissionProgress(false);assert.deepEqual(JSON.parse(JSON.stringify(progress)),{current:3,total:3,completed:3,text:'3/3'});assert.ok(renders>=5,'Canonical progress changes must drive managed renders');
console.log('Issue #523 Transport Sweep mission-progress runtime contract passed.');
""", encoding="utf-8")

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    preflight = replace_once(
        preflight,
        ".github/scripts/test_transport_sweep_native_contract.py; do",
        ".github/scripts/test_transport_sweep_native_contract.py .github/scripts/test_issue523_transport_sweep_progress.py; do",
        "Python preflight contract list",
    )
    preflight = replace_once(
        preflight,
        "node .github/scripts/test_transport_sweep_runtime.js\n",
        "node .github/scripts/test_transport_sweep_runtime.js\nnode .github/scripts/test_issue523_transport_sweep_progress_runtime.js\n",
        "Transport Sweep runtime preflight",
    )
    PREFLIGHT.write_text(preflight, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    marker = "## [7.1.3] - 2026-07-25"
    section = """## [7.1.4] - 2026-07-25

### Patient Transport Sweep mission-progress synchronization

- Added one canonical mission-position state shared by the persistent HUD, Toolkit panel and final summary.
- Initialised active runs at `1/total` and updated the numerator only at mission queue boundaries, never for individual patients or vehicle candidates.
- Made skipped missions and recoverable mission-level errors finalise exactly once before the queue continues.
- Preserved the last accurate mission position on cancellation and rendered `total/total` on normal completion before HUD dismissal.
- Added deterministic static and runtime contracts for multiple patient releases, repeated renders, skips, mission errors, cancellation and final completion.

"""
    if marker not in changelog or "## [7.1.4]" in changelog:
        raise SystemExit("Unexpected changelog state for v7.1.4")
    CHANGELOG.write_text(changelog.replace(marker, section + marker, 1), encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    readme = replace_once(
        readme,
        "## **Current verified release: `v7.1.3`**\n### **Continuous Incident Command news reel**",
        "## **Current verified release: `v7.1.3` · Development candidate: `v7.1.4`**\n### **Patient Transport Sweep mission-progress synchronization**",
        "README candidate marker",
    )
    README.write_text(readme, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = help_text.replace("Toolkit v7.1.3 candidate", "Toolkit v7.1.4 candidate")
    help_text = help_text.replace("Guide for Toolkit v7.1.3 candidate", "Guide for Toolkit v7.1.4 candidate")
    help_text = help_text.replace("What changed in v7.1.3", "What changed in v7.1.4")
    help_text = re.sub(
        r'<main><section class="notice"><h2>What changed in v7\.1\.4</h2><p>.*?</p></section>',
        '<main><section class="notice"><h2>What changed in v7.1.4</h2><p>Patient Transport Sweep now keeps its mission-position counter synchronized with the immutable queue. Patient releases never increment mission progress; skips and recoverable mission errors advance once, cancellation preserves the last position and normal completion reaches total/total.</p></section>',
        help_text,
        count=1,
        flags=re.S,
    )
    help_text = help_text.replace("MissionChief Map Command Toolkit · v7.1.3 candidate", "MissionChief Map Command Toolkit · v7.1.4 candidate")
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (DIAGNOSTIC, DIAGNOSTIC_WORKFLOW, SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("Issue #523 Patient Transport Sweep mission-progress synchronization applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
