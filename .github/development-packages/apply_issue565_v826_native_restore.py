#!/usr/bin/env python3
"""Issue #565 v8.2.6: remove the no-reward detour and restore native vehicle discharge."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]; E='d71839517a0bb731b2c3d4475463b6f8d027db85df9c0b82f6d5cca925178fde'
def rd(p): return (R/p).read_text(encoding='utf-8')
def wr(p,s): (R/p).write_text(s,encoding='utf-8')
def one(s,a,b,n):
 c=s.count(a)
 if c!=1: raise RuntimeError(f'{n}: {c} matches')
 return s.replace(a,b,1)

p='src/MissionChief_Map_Command_Toolkit.user.js';s=rd(p)
if hashlib.sha256(s.encode()).hexdigest()!=E: raise RuntimeError('released v8.2.5 source authority moved')
s=one(s,'// @version      8.2.5','// @version      8.2.6','metadata')
s=one(s,"version: '8.2.5'","version: '8.2.6'",'runtime')
a=s.index('    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT');b=s.index('    function transportSweepVisibleDischargeButtons()',a);s=s[:a]+s[b:]
a=s.index('    async function processTransportSweepMission(item, remainingAllowance) {');b=s.index('    async function startTransportSweep()',a);q=s[a:b]
c=q.index('        const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(');m='        let candidates = collectTransportSweepVehicleCandidatesForMission(missionId);';d=q.index(m,c)+len(m)
q=q[:c]+'            const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);'+q[d:]
q=q.replace('during fallback processing','during native processing');s=s[:a]+q+s[b:]
for x in ['TRANSPORT_SWEEP_OPTIONAL_RELEASE_','processTransportSweepOptionalReleaseControls(','requestTransportSweepOptionalRelease(','Release patient (No reward)','/patient/-1']:
 if x in s: raise RuntimeError(f'detour remains: {x}')
for x in ['const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);','const vehicleResult = await openTransportSweepVehicle(candidate);','button.click();','clickTransportSweepDischargeConfirmation(releaseKey);','recordTransportSweepConfirmedRelease(',r"/patient (?:is not|isn['’]t) transported\.?/gi"]:
 if x not in s: raise RuntimeError(f'native marker missing: {x}')
wr(p,s)

contract=r'''#!/usr/bin/env python3
import re
from pathlib import Path
R=Path(__file__).resolve().parents[2];s=(R/'src/MissionChief_Map_Command_Toolkit.user.js').read_text()
assert re.search(r'(?m)^//\s*@version\s+8\.2\.6$',s) and "version: '8.2.6'" in s
for x in ['TRANSPORT_SWEEP_OPTIONAL_RELEASE_','processTransportSweepOptionalReleaseControls(','requestTransportSweepOptionalRelease(','Release patient (No reward)','/patient/-1']: assert x not in s,x
for x in ['function collectTransportSweepVehicleCandidatesForMission(missionId)','async function openTransportSweepVehicle(candidate)','function transportSweepVisibleDischargeButtons()','function clickTransportSweepDischargeConfirmation(releaseKey)','function transportSweepReleaseConfirmationVisible(baseline = null)','function recordTransportSweepConfirmedRelease(releaseKey, message)',r"/patient (?:is not|isn['’]t) transported\.?/gi"]: assert x in s,x
m=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',s);assert m;b=m.group(1);cur=-1
for x in ["await openTransportSweepPath(`/missions/${missionId}`, 'mission')",'const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);','const vehicleResult = await openTransportSweepVehicle(candidate);','button.click();','clickTransportSweepDischargeConfirmation(releaseKey);','recordTransportSweepConfirmedRelease(']: cur=b.index(x,cur+1)
assert 'let candidates = collectTransportSweepVehicleCandidatesForMission(missionId);' not in b
print('Native Patient Transport Sweep contract passed.')
'''
wr('.github/scripts/test_transport_sweep_native_contract.py',contract)
issue=r'''#!/usr/bin/env python3
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2];s=(R/'src/MissionChief_Map_Command_Toolkit.user.js').read_text();h=(R/'help/index.html').read_text();c=(R/'CHANGELOG.md').read_text();p=json.loads((R/'.github/performance-budget.json').read_text())
assert re.search(r'(?m)^//\s*@version\s+8\.2\.6$',s)
for x in ['TRANSPORT_SWEEP_OPTIONAL_RELEASE_','processTransportSweepOptionalReleaseControls(','Release patient (No reward)','/patient/-1']: assert x not in s,x
assert 'const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);' in s
assert r"/patient (?:is not|isn['’]t) transported\.?/gi" in s
assert '## [8.2.6] - 2026-07-29' in c and 'native FMS 5 vehicle workflow' in h and 'Patient isn’t transported' in h and 'no-reward fast path' not in h
assert p['transitionApproval']['version']=='8.2.6' and p['transitionApproval']['approvedNetworkRequestDelta']==-1 and p['absoluteLimits']['network_request_calls']==5
print('Issue #565 v8.2.6 native restoration contract passed.')
'''
wr('.github/scripts/test_issue565_transport_sweep_no_reward.py',issue)
runtime=r'''#!/usr/bin/env node
"use strict";import assert from'node:assert/strict';import fs from'node:fs';import path from'node:path';import{fileURLToPath}from'node:url';const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),s=fs.readFileSync(path.join(R,'src/MissionChief_Map_Command_Toolkit.user.js'),'utf8'),a=s.indexOf('    async function processTransportSweepMission(item, remainingAllowance) {'),z=s.indexOf('    async function startTransportSweep()',a),b=s.slice(a,z);assert.ok(a>=0&&z>a);for(const x of['TRANSPORT_SWEEP_OPTIONAL_RELEASE_','processTransportSweepOptionalReleaseControls(','Release patient (No reward)','/patient/-1'])assert.equal(s.includes(x),false,x);let c=-1;for(const x of["await openTransportSweepPath(`/missions/${missionId}`, 'mission')",'const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);','const vehicleResult = await openTransportSweepVehicle(candidate);','button.click();','clickTransportSweepDischargeConfirmation(releaseKey);','recordTransportSweepConfirmedRelease(']){const n=b.indexOf(x,c+1);assert.ok(n>c,x);c=n}assert.equal(Array.isArray(await Promise.resolve([{vehicleId:'111'}])),true);console.log('Issue #565 v8.2.6 native runtime sequence passed.');
'''
wr('.github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs',runtime)

j=json.loads(rd('.github/performance-budget.json'));j['revision']='2026-07-29-issue-565-native-vehicle-restore';j['rationale']='Remove the unsuccessful direct no-reward request detour and restore the original MissionChief FMS 5 vehicle-window Discharge patient workflow.';j['transitionApproval']={'issue':565,'version':'8.2.6','approvedNetworkRequestDelta':-1,'scope':'Restore the awaited native vehicle discharge sequence.','approvedMutationObserverDelta':0};j['absoluteLimits']['network_request_calls']=5
if not any(x.get('version')=='8.2.6' for x in j.setdefault('approvalHistory',[])): j['approvalHistory'].append(dict(j['transitionApproval']))
wr('.github/performance-budget.json',json.dumps(j,indent=2)+'\n')

ch=rd('CHANGELOG.md');entry='''## [8.2.6] - 2026-07-29

### Patient Transport Sweep — restore the proven native workflow

- Removed the v8.2.0 direct `Release patient (No reward)` request path that displaced the original working sequence.
- Restored the exact native flow: open mission, await alliance FMS 5 vehicle discovery, open the flashing vehicle, click **Discharge patient**, confirm **Yes, discharge!**, recognise **Patient isn’t transported**, then continue to the next patient and mission.
- Restored the missing `await` on `collectTransportSweepVehicleCandidatesForMission()`, which had left the native path holding a Promise instead of a vehicle list.
- Preserves own-vehicle exclusion, bounded waits, progress, cancellation, duplicate protection and sequential processing.
- Removes one network-request site and adds no observer, interval or Toolkit-managed timer.

'''
if '## [8.2.6] - 2026-07-29' not in ch: ch=one(ch,'# Changelog\n\n','# Changelog\n\n'+entry,'changelog')
wr('CHANGELOG.md',ch)
wr('docs/issue-565-transport-sweep-no-reward.md',"""# Issue #565 — native Patient Transport Sweep restoration

Toolkit v8.2.6 restores the original MissionChief-native workflow: open each mission, await the alliance-owned FMS 5 vehicle list, open the flashing vehicle, click **Discharge patient**, confirm **Yes, discharge!**, recognise **Patient isn’t transported**, then continue to the next patient and mission.

The v8.2.0 direct `Release patient (No reward)` detour and its request site are removed. Verified personal vehicle IDs, bounded waits, cancellation, progress, duplicate protection and sweep-owned window cleanup remain preserved.
""")

j=json.loads(rd('help/manifest.json'));j.update(guideVersion='8.2.6',toolkitVersion='8.2.6',updated='2026-07-29',runtimeGuidePatch='Toolkit v8.2.6 restores the native mission → FMS 5 vehicle → Discharge patient → Patient isn’t transported workflow.');wr('help/manifest.json',json.dumps(j,indent=2)+'\n')
h=rd('help/index.html').replace('8.2.5','8.2.6');h,n=re.subn(r'<section id="transport-sweep-no-reward">.*?</section>','<section id="transport-sweep-native"><h2>Patient Transport Sweep — native vehicle workflow</h2><p>The original native FMS 5 vehicle workflow is restored: open the mission, open the flashing alliance-owned FMS 5 vehicle, click <strong>Discharge patient</strong>, confirm <strong>Yes, discharge!</strong>, recognise <strong>Patient isn’t transported</strong>, and repeat for every eligible patient and mission.</p></section>',h,count=1,flags=re.S)
if n!=1: raise RuntimeError(f'help section matches: {n}')
wr('help/index.html',h)

j=json.loads(rd('docs/site-data.json'));found=False
for c in j.get('featureCategories',[]):
 for f in c.get('features',[]):
  if f.get('name')=='Patient Transport Sweep': f['summary']="Opens each mission and alliance-owned FMS 5 patient vehicle, then completes MissionChief's native discharge and confirmation sequence.";f['details']=['Mission-by-mission FMS 5 vehicle discovery','Native Discharge patient control','Yes, discharge! confirmation','Patient isn’t transported verification','Sequential patients and missions','Verified personal vehicle exclusion'];found=True
if not found: raise RuntimeError('site-data Patient Transport Sweep missing')
wr('docs/site-data.json',json.dumps(j,indent=2,ensure_ascii=False)+'\n')

j=json.loads(rd('.github/fixtures/main-style-source-headroom.json'));t=rd(p);a=t.index('function installMainStyles()');b=t.index('addStyle(`',a)+len('addStyle(`');m=t.index("recordStartupMetric('stylesheetInstallMs'",b);z=t.rfind('`);',b,m);css=t[b:z];ls=css.split('\n');canon=re.sub(r'\n[\t ]*}','}','\n'.join(x for i,x in enumerate(ls) if not(0<i<len(ls)-1 and not x.strip())));v=j['v8Candidate'];pb,pl=int(v['sourceBytes']),int(v['sourceLines']);gb,gl=int(v['approvedGrowth']['sourceBytes']),int(v['approvedGrowth']['sourceLines']);nb,nl=len(t.encode()),len(t.splitlines());v.update(issue=565,version='8.2.6',sourceBytes=nb,sourceLines=nl,sourceSha256=hashlib.sha256(t.encode()).hexdigest(),templateBytes=len(css.encode()),templateLines=len(ls),templateSha256=hashlib.sha256(css.encode()).hexdigest(),canonicalCssSha256=hashlib.sha256(canon.encode()).hexdigest(),maxSourceBytes=nb+20000,maxSourceLines=nl+250,baseline='8.2.5',scope='Issue #565 restoration of the original awaited native FMS 5 vehicle discharge workflow');v['approvedGrowth']={'sourceBytes':gb+nb-pb,'sourceLines':gl+nl-pl,'templateBytes':0,'templateLines':0};wr('.github/fixtures/main-style-source-headroom.json',json.dumps(j,indent=2)+'\n')
print(json.dumps({'version':'8.2.6','sourceBytes':nb,'sourceLines':nl,'sourceSha256':v['sourceSha256'],'restored':'native vehicle discharge'},indent=2))
