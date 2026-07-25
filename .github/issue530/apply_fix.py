#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
PREFLIGHT = ROOT / '.github' / 'scripts' / 'run_userscript_preflight.sh'
NATIVE_TEST = ROOT / '.github' / 'scripts' / 'test_transport_sweep_native_contract.py'
ISSUE527_TEST = ROOT / '.github' / 'scripts' / 'test_issue527_transport_sweep_skipped_patients.py'
STATIC_TEST = ROOT / '.github' / 'scripts' / 'test_issue530_transport_sweep_discharge_confirmation.py'
RUNTIME_TEST = ROOT / '.github' / 'scripts' / 'test_issue530_transport_sweep_discharge_confirmation_runtime.js'
CHANGELOG = ROOT / 'CHANGELOG.md'
README = ROOT / 'README.md'
HELP = ROOT / 'help' / 'index.html'
FIXTURE = ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json'
SELF = ROOT / '.github' / 'issue530' / 'apply_fix.py'
DIAGNOSTIC = ROOT / '.github' / 'issue530' / 'extract_confirmation_flow.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-issue530-discharge-confirmation.yml'
DIAGNOSTIC_WORKFLOW = ROOT / '.github' / 'workflows' / 'diagnose-issue530-discharge-confirmation.yml'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected one {label}, found {count}')
    return text.replace(old, new, 1)


def update_headroom(source: str) -> None:
    start = source.index('function installMainStyles()')
    template_start = source.index('addStyle(`', start) + len('addStyle(`')
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind('`);', template_start, metric)
    raw = source[template_start:template_end]
    lines = raw.split('\n')
    canonical = re.sub(
        r'\n[\t ]*}',
        '}',
        '\n'.join(line for index, line in enumerate(lines) if not (0 < index < len(lines) - 1 and not line.strip())),
    )
    fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
    fixture['v7Candidate'].update({
        'issue': 530,
        'version': '7.1.6',
        'sourceBytes': len(source.encode('utf-8')),
        'sourceLines': len(source.splitlines()),
        'sourceSha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'templateBytes': len(raw.encode('utf-8')),
        'templateLines': len(lines),
        'templateSha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
        'canonicalCssSha256': hashlib.sha256(canonical.encode('utf-8')).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    source = replace_once(source, '// @version      7.1.5', '// @version      7.1.6', 'metadata version')
    source = replace_once(source, "version: '7.1.5',", "version: '7.1.6',", 'runtime version')

    source = replace_once(
        source,
        "        confirmedReleaseKeys: new Set(),\n        skippedPatientKeys: new Set(),",
        "        confirmedReleaseKeys: new Set(),\n        skippedPatientKeys: new Set(),\n        confirmedDischargeDialogKeys: new Set(),\n        pendingDischargeKey: '',",
        'discharge confirmation runtime ownership',
    )

    helper_marker = '    function captureTransportSweepReleaseConfirmationBaseline() {'
    helpers = """    const TRANSPORT_SWEEP_DISCHARGE_DIALOG_TITLE = 'discharge patient';
    const TRANSPORT_SWEEP_DISCHARGE_DIALOG_WARNING = 'do you really want to discharge the patient of this vehicle? no payment will be credited for the patient!';
    const TRANSPORT_SWEEP_DISCHARGE_DIALOG_ABORT = 'abort';
    const TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE = 'discharge and disable confirmation';
    const TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM = 'yes, discharge!';

    function transportSweepDialogControlText(control) {
        return normaliseTransportSweepReleaseText(
            control?.value || control?.textContent || control?.getAttribute?.('aria-label') || control?.title || ''
        );
    }

    function transportSweepDischargeConfirmationRoots() {
        const selectors = [
            '[role="alertdialog"]', '[role="dialog"]', '.modal.show .modal-content', '.modal.in .modal-content',
            '.modal.show', '.modal.in', '.modal-dialog', '.modal-content', '.bootbox', '.bootbox-modal',
            '.swal2-popup', '.sweet-alert', '.ui-dialog', '.ui-dialog-content', '#lightbox_box', '#lightbox'
        ];
        const roots = [];
        const seen = new Set();
        const add = root => {
            if (!root || seen.has(root) || !transportSweepElementVisible(root)) return;
            if (root.closest?.(`#${SCRIPT.panelId}`)) return;
            seen.add(root);
            roots.push(root);
        };
        transportSweepVisibleWindowRoots().forEach(add);
        for (const context of transportSweepDocumentContexts()) {
            for (const selector of selectors) {
                let matches = [];
                try { matches = Array.from(context.doc.querySelectorAll(selector)); } catch (err) {}
                matches.forEach(add);
            }
        }
        return roots;
    }

    function clickTransportSweepDischargeConfirmation(releaseKey) {
        const key = String(releaseKey || '').trim();
        if (!key || !transportSweepRuntime.running || transportSweepRuntime.pendingDischargeKey !== key) return false;
        if (transportSweepRuntime.confirmedDischargeDialogKeys.has(key)) return false;

        for (const root of transportSweepDischargeConfirmationRoots()) {
            const rootText = normaliseTransportSweepReleaseText(root.textContent);
            if (!rootText.includes(TRANSPORT_SWEEP_DISCHARGE_DIALOG_TITLE) || !rootText.includes(TRANSPORT_SWEEP_DISCHARGE_DIALOG_WARNING)) continue;

            let controls = [];
            try {
                controls = Array.from(root.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"], a.btn'));
            } catch (err) {}
            const visibleControls = controls.filter(control => transportSweepElementVisible(control));
            const labels = new Map(visibleControls.map(control => [transportSweepDialogControlText(control), control]));
            const abort = labels.get(TRANSPORT_SWEEP_DISCHARGE_DIALOG_ABORT);
            const disable = labels.get(TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE);
            const confirm = labels.get(TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM);
            if (!abort || !disable || !confirm) continue;
            if (confirm.disabled || confirm.getAttribute?.('aria-disabled') === 'true') continue;

            transportSweepRuntime.confirmedDischargeDialogKeys.add(key);
            confirm.click();
            transportSweepLog('Confirmed MissionChief Discharge patient dialog');
            return true;
        }
        return false;
    }

"""
    if source.count(helper_marker) != 1:
        raise SystemExit('Release confirmation insertion boundary is ambiguous')
    source = source.replace(helper_marker, helpers + helper_marker, 1)

    old_discharge = """                    const confirmationBaseline = captureTransportSweepReleaseConfirmationBaseline();
                    button.click();
                    const cleared = await transportSweepWaitFor(() => {
                        if (transportSweepReleaseConfirmationVisible(confirmationBaseline)) return true;
                        if (!button.isConnected || !transportSweepElementVisible(button) || button.disabled) return true;
                        return normaliseTransportSweepReleaseText(button.textContent) !== 'discharge patient' ? true : null;
                    }, 5000, 140);
                    if (!cleared) throw new Error('Discharge confirmation timed out');
                    confirmedThisAttempt = recordTransportSweepConfirmedRelease(
                        transportSweepReleaseKey(missionId, candidate.vehicleId),
                        `Cleared ${candidate.label} at ${item.caption}`
                    );"""
    new_discharge = """                    const releaseKey = transportSweepReleaseKey(missionId, candidate.vehicleId);
                    const confirmationBaseline = captureTransportSweepReleaseConfirmationBaseline();
                    transportSweepRuntime.pendingDischargeKey = releaseKey;
                    button.click();
                    clickTransportSweepDischargeConfirmation(releaseKey);
                    let cleared = false;
                    try {
                        cleared = await transportSweepWaitFor(() => {
                            clickTransportSweepDischargeConfirmation(releaseKey);
                            if (transportSweepReleaseConfirmationVisible(confirmationBaseline)) return true;
                            if (!button.isConnected || !transportSweepElementVisible(button) || button.disabled) return true;
                            return normaliseTransportSweepReleaseText(button.textContent) !== 'discharge patient' ? true : null;
                        }, 5000, 70);
                    } finally {
                        if (transportSweepRuntime.pendingDischargeKey === releaseKey) transportSweepRuntime.pendingDischargeKey = '';
                    }
                    if (!cleared) throw new Error('Discharge confirmation timed out');
                    confirmedThisAttempt = recordTransportSweepConfirmedRelease(
                        releaseKey,
                        `Cleared ${candidate.label} at ${item.caption}`
                    );"""
    source = replace_once(source, old_discharge, new_discharge, 'sweep discharge click flow')

    source = replace_once(
        source,
        "        transportSweepRuntime.confirmedReleaseKeys = new Set();\n        transportSweepRuntime.skippedPatientKeys = new Set();",
        "        transportSweepRuntime.confirmedReleaseKeys = new Set();\n        transportSweepRuntime.skippedPatientKeys = new Set();\n        transportSweepRuntime.confirmedDischargeDialogKeys = new Set();\n        transportSweepRuntime.pendingDischargeKey = '';",
        'run reset for discharge confirmation ownership',
    )

    source = replace_once(
        source,
        "            transportSweepRuntime.currentVehicleHref = '';\n            transportSweepRuntime.currentItem = '';",
        "            transportSweepRuntime.currentVehicleHref = '';\n            transportSweepRuntime.pendingDischargeKey = '';\n            transportSweepRuntime.currentItem = '';",
        'final discharge confirmation disarm',
    )

    SOURCE.write_text(source, encoding='utf-8')

    native = NATIVE_TEST.read_text(encoding='utf-8')
    native = replace_once(
        native,
        "'function captureTransportSweepReleaseConfirmationBaseline()'",
        "'function transportSweepDischargeConfirmationRoots()','function clickTransportSweepDischargeConfirmation(releaseKey)','function captureTransportSweepReleaseConfirmationBaseline()'",
        'native confirmation helper inventory',
    )
    native = replace_once(
        native,
        "for item in ['collectTransportSweepVehicleCandidatesForMission(missionId)','openTransportSweepVehicle(candidate)','button.click()','recordTransportSweepConfirmedRelease(']: assert item in body",
        "for item in ['collectTransportSweepVehicleCandidatesForMission(missionId)','openTransportSweepVehicle(candidate)','button.click()','clickTransportSweepDischargeConfirmation(releaseKey)','recordTransportSweepConfirmedRelease(']: assert item in body",
        'native discharge flow assertions',
    )
    NATIVE_TEST.write_text(native, encoding='utf-8')

    issue527 = ISSUE527_TEST.read_text(encoding='utf-8')
    issue527 = replace_once(
        issue527,
        " assert metadata and runtime and metadata.group(1)==runtime.group(1)=='7.1.5'\n",
        " assert metadata and runtime and metadata.group(1)==runtime.group(1)\n version=tuple(int(part) for part in metadata.group(1).split('.'))\n assert version >= (7,1,5)\n",
        'Issue 527 patch-release version assertion',
    )
    ISSUE527_TEST.write_text(issue527, encoding='utf-8')

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
 assert metadata and runtime and metadata.group(1)==runtime.group(1)=='7.1.6'
 for marker in ["confirmedDischargeDialogKeys: new Set()","pendingDischargeKey: ''","function transportSweepDischargeConfirmationRoots()","function clickTransportSweepDischargeConfirmation(releaseKey)","TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM = 'yes, discharge!'","TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE = 'discharge and disable confirmation'"]:
  assert marker in source,marker
 helper=section(source,'    function transportSweepDialogControlText(','    function captureTransportSweepReleaseConfirmationBaseline(')
 processor=re.search(r'async function processTransportSweepMission\\(item, remainingAllowance\\) \\{([\\s\\S]*?)\\n    \\}\\n\\n    async function startTransportSweep',source);assert processor
 body=processor.group(1)
 assert "transportSweepRuntime.pendingDischargeKey !== key" in helper
 assert "transportSweepRuntime.confirmedDischargeDialogKeys.has(key)" in helper
 assert "TRANSPORT_SWEEP_DISCHARGE_DIALOG_ABORT" in helper and "TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE" in helper and "TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM" in helper
 assert "confirm.click();" in helper
 assert "abort.click" not in helper and "disable.click" not in helper
 assert "const releaseKey = transportSweepReleaseKey(missionId, candidate.vehicleId);" in body
 assert body.count('clickTransportSweepDischargeConfirmation(releaseKey);') == 2
 assert body.index('button.click();') < body.index('clickTransportSweepDischargeConfirmation(releaseKey);') < body.index('transportSweepReleaseConfirmationVisible(confirmationBaseline)')
 assert '}, 5000, 70);' in body
 assert "pendingDischargeKey = '';" in source
 assert 'MutationObserver' not in helper and 'setInterval' not in helper
 print('Issue #530 discharge confirmation static contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
""", encoding='utf-8')

    RUNTIME_TEST.write_text("""#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const signatureEnd=source.indexOf(') {',start);assert.ok(signatureEnd>=0);const open=signatureEnd+2;let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
function control(label){return{textContent:label,value:'',title:'',isConnected:true,disabled:false,clicks:0,attrs:{},click(){this.clicks+=1;},getAttribute(name){return this.attrs[name]||null;}};}
function dialog(options={}){const abort=control('Abort');const disable=control('discharge and disable confirmation');const confirm=control('Yes, discharge!');const controls=options.controls||[abort,disable,confirm];return{isConnected:true,textContent:options.text||'Discharge patient Do you really want to discharge the patient of this vehicle? No payment will be credited for the patient! Abort discharge and disable confirmation Yes, discharge!',controls,closest(){return null;},querySelectorAll(){return controls;},abort,disable,confirm};}
let roots=[];const logs=[];const runtime={running:true,pendingDischargeKey:'101:201',confirmedDischargeDialogKeys:new Set()};
const sandbox={console,String,Array,Map,Set,SCRIPT:{panelId:'toolkit-panel'},transportSweepRuntime:runtime,normaliseTransportSweepReleaseText:value=>String(value||'').replace(/\\s+/g,' ').trim().toLowerCase(),transportSweepElementVisible:element=>Boolean(element?.isConnected),transportSweepVisibleWindowRoots:()=>roots,transportSweepDocumentContexts:()=>[],transportSweepLog:message=>logs.push(message)};
const constants=`const TRANSPORT_SWEEP_DISCHARGE_DIALOG_TITLE='discharge patient';const TRANSPORT_SWEEP_DISCHARGE_DIALOG_WARNING='do you really want to discharge the patient of this vehicle? no payment will be credited for the patient!';const TRANSPORT_SWEEP_DISCHARGE_DIALOG_ABORT='abort';const TRANSPORT_SWEEP_DISCHARGE_DIALOG_DISABLE='discharge and disable confirmation';const TRANSPORT_SWEEP_DISCHARGE_DIALOG_CONFIRM='yes, discharge!';`;
vm.createContext(sandbox);vm.runInContext(`${constants}\\n${extractFunction('transportSweepDialogControlText')}\\n${extractFunction('transportSweepDischargeConfirmationRoots')}\\n${extractFunction('clickTransportSweepDischargeConfirmation')}\\nthis.clickTransportSweepDischargeConfirmation=clickTransportSweepDischargeConfirmation;`,sandbox);const click=sandbox.clickTransportSweepDischargeConfirmation;
const exact=dialog();roots=[exact];assert.equal(click('101:201'),true);assert.equal(exact.confirm.clicks,1);assert.equal(exact.abort.clicks,0);assert.equal(exact.disable.clicks,0);assert.equal(logs.length,1);
assert.equal(click('101:201'),false);assert.equal(exact.confirm.clicks,1,'Repeated scans must not double-click');
runtime.pendingDischargeKey='101:202';const unrelated=dialog({text:'Delete building Abort discharge and disable confirmation Yes, discharge!'});roots=[unrelated];assert.equal(click('101:202'),false);assert.equal(unrelated.confirm.clicks,0,'Unrelated modal must be ignored');
roots=[];assert.equal(click('101:202'),false,'No dialog is a valid no-op');const delayed=dialog();roots=[delayed];assert.equal(click('101:202'),true,'A later dialog scan must confirm');assert.equal(delayed.confirm.clicks,1);
runtime.running=false;runtime.pendingDischargeKey='101:203';const inactive=dialog();roots=[inactive];assert.equal(click('101:203'),false);assert.equal(inactive.confirm.clicks,0,'Inactive sweep must not confirm');
runtime.running=true;runtime.pendingDischargeKey='different';assert.equal(click('101:203'),false);assert.equal(inactive.confirm.clicks,0,'Unarmed release key must not confirm');
console.log('Issue #530 discharge confirmation runtime contract passed.');
""", encoding='utf-8')

    preflight = PREFLIGHT.read_text(encoding='utf-8')
    preflight = replace_once(
        preflight,
        '.github/scripts/test_issue527_transport_sweep_skipped_patients.py; do',
        '.github/scripts/test_issue527_transport_sweep_skipped_patients.py .github/scripts/test_issue530_transport_sweep_discharge_confirmation.py; do',
        'static preflight registration',
    )
    preflight = replace_once(
        preflight,
        'node .github/scripts/test_issue527_transport_sweep_skipped_patients_runtime.js\n',
        'node .github/scripts/test_issue527_transport_sweep_skipped_patients_runtime.js\nnode .github/scripts/test_issue530_transport_sweep_discharge_confirmation_runtime.js\n',
        'runtime preflight registration',
    )
    PREFLIGHT.write_text(preflight, encoding='utf-8')

    changelog = CHANGELOG.read_text(encoding='utf-8')
    marker = '## [7.1.5] - 2026-07-25'
    section = """## [7.1.6] - 2026-07-25

### Native Discharge patient confirmation handling

- Detected the intermittent MissionChief Discharge patient confirmation dialog only while a sweep-owned mission/vehicle discharge action is armed.
- Clicked the exact **Yes, discharge!** action immediately and during the existing bounded release-evidence wait.
- Explicitly left **Abort** and **discharge and disable confirmation** untouched, preserving the user's MissionChief confirmation preference.
- Ignored unrelated dialogs, manual discharges, inactive sweeps and mismatched release identities.
- Added idempotent dialog-confirmation ownership plus static and executable regressions for immediate, delayed, absent, unrelated and repeated dialog scans.

"""
    if marker not in changelog or '## [7.1.6]' in changelog:
        raise SystemExit('Unexpected changelog state for v7.1.6')
    CHANGELOG.write_text(changelog.replace(marker, section + marker, 1), encoding='utf-8')

    readme = README.read_text(encoding='utf-8')
    readme, count = re.subn(
        r"## \*\*Current verified release: `v[^`]+`[^\n]*\*\*(?:\n### \*\*[^\n]+\*\*)?",
        "## **Current verified release: `v7.1.5` · Development candidate: `v7.1.6`**\n### **Native Discharge patient confirmation handling**",
        readme,
        count=1,
    )
    if count != 1:
        raise SystemExit(f'Expected one README release heading, found {count}')
    README.write_text(readme, encoding='utf-8')

    help_text = HELP.read_text(encoding='utf-8')
    help_text = re.sub(r'v7\.1\.5', 'v7.1.6', help_text)
    help_text, notice_count = re.subn(
        r'<main><section class="notice"><h2>.*?</p></section>',
        '<main><section class="notice"><h2>What changed in v7.1.6</h2><p>Patient Transport Sweep now confirms the intermittent native Discharge patient dialog by clicking only Yes, discharge! during an armed sweep action. Abort and discharge-and-disable-confirmation remain untouched.</p></section>',
        help_text,
        count=1,
        flags=re.S,
    )
    if notice_count != 1:
        raise SystemExit(f'Expected one Help Centre notice, found {notice_count}')
    HELP.write_text(help_text, encoding='utf-8')

    update_headroom(source)

    for path in (SELF, DIAGNOSTIC, WORKFLOW, DIAGNOSTIC_WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print('Issue #530 v7.1.6 discharge confirmation fix applied.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
