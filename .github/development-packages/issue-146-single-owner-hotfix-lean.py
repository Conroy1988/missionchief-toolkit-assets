#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = 'f8dc390ef31de78c4f9a8819bd9411af277dfe3e'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-minified.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.lean.payload.py'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)

write_anchor = "SOURCE.write_text(source, encoding='utf-8')\n\nfor relative in ("
insert = r'''SOURCE.write_text(source, encoding='utf-8')

source = SOURCE.read_text(encoding='utf-8')

def replace_symbols(start_symbol: str, end_symbol: str, replacement: str) -> None:
    global source
    start = source.find(start_symbol)
    end = source.find(end_symbol, start + len(start_symbol))
    if start < 0 or end < 0:
        raise AssertionError(f'Issue #146 lean helper boundary missing: {start_symbol} -> {end_symbol}')
    source = source[:start] + replacement + '\n\n' + source[end:]

replace_symbols(
    '    function missionRequirementsPrimaryRuntime',
    '    function missionRequirementsDocumentCss',
    '''    function missionRequirementsPrimaryRuntime(){try{return!pageWindow.top||pageWindow.top===pageWindow}catch{return true}}function missionRequirementsMissionIdentity(candidate,source){const r=candidate?.root,l=r?.querySelector?.('a[href*="/missions/"],form[action*="/missions/"]');for(const v of[candidate?.missionId,candidate?.mission_id,r?.dataset?.missionId,r?.getAttribute?.('mission_id'),r?.getAttribute?.('action'),l?.getAttribute?.('href'),l?.getAttribute?.('action'),source?.ownerDocument?.defaultView?.location?.pathname]){const m=String(v??'').match(/(?:\/missions\/|mission[_-]?)(\d+)|^(\d+)$/i),id=+(m?.[1]||m?.[2]);if(id>0)return id}return 0}function missionRequirementsWindowCandidates(){const a=[],s=new Set(),add=c=>{const x=missionRequirementsSourceForCandidate(c);if(x&&x.isConnected!==false&&!s.has(x)){s.add(x);a.push({...c,source:x})}};missionValueWindowCandidates().forEach(add);for(const c of transportSweepDocumentContexts()){const d=c?.doc;if(d?.querySelectorAll)for(const x of d.querySelectorAll('#missing_text'))add(missionRequirementsCandidateFromSource(x))}const ids=new Set();return a.sort((x,y)=>2*(missionRequirementsRecords.has(y.source)-missionRequirementsRecords.has(x.source))+isVisible(y.source)-isVisible(x.source)).filter(c=>{const id=missionRequirementsMissionIdentity(c,c.source);return!id||!ids.has(id)&&(ids.add(id),true)})}'''
)
replace_symbols(
    '    function missionRequirementsHostPanels',
    '    function missionRequirementsRemoveRecord',
    '''    function missionRequirementsHostPanels(source){return[...(source?.parentNode?.children||[])].filter(p=>p?.id===SCRIPT.missionRequirementsPanelId||p?.getAttribute?.('data-mcms-requirements-panel')==='1')}function missionRequirementsCanonicalPanel(source,p){const a=missionRequirementsHostPanels(source);if(!a.length)return null;p=p&&a.includes(p)?p:a[0];p.id=SCRIPT.missionRequirementsPanelId;p.setAttribute?.('data-mcms-requirements-panel','1');for(const x of a)if(x!==p)x.remove();return p}function missionRequirementsBindPanel(p){if(!p||p.getAttribute?.('data-mcms-requirements-collapse-bound'))return;p.setAttribute?.('data-mcms-requirements-collapse-bound','1');p.addEventListener('click',e=>{const b=e.target?.closest?.('[data-mcms-requirements-collapse]');if(!b)return;const c=p.classList.toggle('mcms-collapsed');b.setAttribute('aria-expanded',String(!c));b.setAttribute('aria-label',c?'Expand mission requirements':'Collapse mission requirements');b.textContent=c?'⌄':'⌃'})}function missionRequirementsEnsureRecord(candidate,source){let r=missionRequirementsRecords.get(source),p=missionRequirementsCanonicalPanel(source,r?.panel?.isConnected?r.panel:null);if(r&&p){r.panel=p;r.candidate=candidate;missionRequirementsBindPanel(p);missionRequirementsHideSource(source);missionRequirementsScheduleRecord(r);return r}if(r)missionRequirementsRemoveRecord(source);const d=source.ownerDocument||document;for(const[x]of missionRequirementsRecords)if(x!==source&&x.ownerDocument===d)missionRequirementsRemoveRecord(x);ensureMissionRequirementsDocumentStyle(d);p=missionRequirementsCanonicalPanel(source);if(!p){p=d.createElement('section');p.id=SCRIPT.missionRequirementsPanelId;p.setAttribute('data-mcms-requirements-panel','1');p.setAttribute('aria-label','Live mission requirements');source.parentNode?.insertBefore(p,source)}p.dataset.mcmsTheme=state.uiTheme;missionRequirementsBindPanel(p);missionRequirementsHideSource(source);r={candidate,source,panel:p};const root=candidate.root?.isConnected?candidate.root:candidate.mount,O=d.defaultView?.MutationObserver||pageWindow.MutationObserver||MutationObserver;if(root&&typeof O==='function'){r.observer=runtimeTrackObserver(new O(ms=>ms.some(m=>missionRequirementsMutationRelevant(r,m))&&missionRequirementsScheduleRecord(r)));r.observer.observe(root,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['checked','class','style','vehicle_type_id','data-vehicle-type-id','data-vehicle_type_id','data-equipment-types','data-equipment-type','data-current-personnel','data-min-personnel','data-max-personnel','tractive_vehicle_id','data-tractive-vehicle-id','trailer_id','data-trailer-id','sortvalue']})}missionRequirementsRecords.set(source,r);missionRequirementsScheduleRecord(r);return r}'''
)
SOURCE.write_text(source, encoding='utf-8')

contract = CONTRACT_TEST.read_text(encoding='utf-8')
old_missing = '    missing = [marker for marker in required_markers if marker not in source]\n'
new_missing = '    compact_source = re.sub(r"\\s+", "", source)\n    missing = [marker for marker in required_markers if marker not in source and re.sub(r"\\s+", "", marker) not in compact_source]\n'
if contract.count(old_missing) != 1:
    raise AssertionError('Mission Requirements whitespace-tolerant marker anchor missing or duplicated')
contract = contract.replace(old_missing, new_missing, 1)
old_insert_count = '    assert source.count("source.parentNode?.insertBefore(panel, source)") == 1\n'
new_insert_count = '    assert compact_source.count("source.parentNode?.insertBefore(p,source)") == 1\n'
if contract.count(old_insert_count) != 1:
    raise AssertionError('Mission Requirements insertion-count anchor missing or duplicated')
contract = contract.replace(old_insert_count, new_insert_count, 1)
CONTRACT_TEST.write_text(contract, encoding='utf-8')

for relative in ('''
if payload.count(write_anchor) != 1:
    raise AssertionError('Issue #146 lean injection anchor missing or duplicated')
payload = payload.replace(write_anchor, insert, 1)

cleanup_anchor = "    '.github/development-packages/issue-146-single-owner-hotfix-budget.py',\n    '.github/diagnostics/issue-146-hotfix-failure.txt',"
cleanup_replacement = """    '.github/development-packages/issue-146-single-owner-hotfix-budget.py',
    '.github/development-packages/issue-146-single-owner-hotfix-minified.py',
    '.github/development-packages/issue-146-single-owner-hotfix-final.py',
    '.github/development-packages/issue-146-mission-requirements-single-owner-diagnostic.py',
    '.github/diagnostics/issue-146-hotfix-failure.txt',
    '.github/diagnostics/issue-146-mission-requirements-candidates.txt',
    '.github/diagnostics/issue-146-mission-requirements-ownership.txt',"""
if payload.count(cleanup_anchor) != 1:
    raise AssertionError('Issue #146 lean cleanup anchor missing or duplicated')
payload = payload.replace(cleanup_anchor, cleanup_replacement, 1)

TEMP.write_text(payload, encoding='utf-8')
try:
    runpy.run_path(str(TEMP), run_name='__main__')
finally:
    TEMP.unlink(missing_ok=True)
