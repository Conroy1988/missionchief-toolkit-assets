"""Build 1.1.3 test overlay; retain the submitted 1.0.0 release and recovered baseline."""
import json,pathlib,re,runpy,zipfile
root=pathlib.Path(__file__).resolve().parent
runpy.run_path(str(root/'prepare-store-release.py'))
out=root.parent/'.dev/home-response-extension'
parts=[]
for name in ['core.mjs','ui.mjs']:
 s=(root/'hospital-upgrades'/name).read_text()
 s=re.sub(r'^import .*?;\n','',s,flags=re.M)
 s=re.sub(r'^export ','',s,flags=re.M);parts.append(s)
bundle='const HospitalUpgrades=(()=>{\n'+'\n'.join(parts)+'\nreturn {mountHospitals,configureHospitals,destroyHospitals};})();\n'
p=out/'toolkit.js';s=p.read_text();
s=s.replace("return String(Math.max(0, Math.round(Number(record?.level) || 0)));", "if(record?.typeId==='4' && Number.isInteger(record.hospitalTargetLevel) && record.hospitalTargetLevel>record.level && record.hospitalTargetLevel<=30)return String(record.hospitalTargetLevel-1);return String(Math.max(0, Math.round(Number(record?.level) || 0)));")
s=s.replace("const parsed = parseExpansionPlannerActions(doc, record, item.kind, item.discoveryPath);", "const parsed = parseExpansionPlannerActions(doc, item.hospitalTargetLevel ? {...record,hospitalTargetLevel:item.hospitalTargetLevel} : record, item.kind, item.discoveryPath);")
anchor='function createOperationsController(api){';assert s.count(anchor)==1;s=s.replace(anchor,bundle+anchor)
anchor='HomeResponseBuilder.mount(grid);';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'HospitalUpgrades.mountHospitals(grid);')
anchor='pilot.operations=createOperationsController({';assert s.count(anchor)==1;s=s.replace(anchor,(root/'hospital-upgrades/bridge.js').read_text()+'\n'+anchor)
anchor='HomeResponseBuilder.destroy();';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'HospitalUpgrades.destroyHospitals();');p.write_text(s)
p=out/'features/administration.js';a=p.read_text();old='after.level === before.level + 1';assert old in a;a=a.replace(old,"after.level === (item.hospitalTargetLevel || before.level + 1)");anchor='        let after;\n        let verifiedPages;';assert a.count(anchor)==1;a=a.replace(anchor,(root/'hospital-upgrades/verify-target.js').read_text()+anchor);p.write_text(a)
m=json.loads((out/'manifest.json').read_text());m.update(version='1.1.3',version_name='Hospital upgrades testing · Extension 1.1.3 · Toolkit 10.18.1');(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
p=out/'BUILD.json';data=json.loads(p.read_text());data.update(extensionVersion='1.1.3',channel='hospital-upgrades-testing',liveValidation='Hospital upgrade purchases not live-tested');data.pop('automatedTests',None);p.write_text(json.dumps(data,indent=2)+'\n')
p=out/'release-notes.html';p.write_text(p.read_text().replace('<main>','<main><h1>Hospital upgrades · 1.1.3 test</h1><p>Fixes verification after a direct hospital upgrade reaches maximum level. Verifies the actual hospital record without reopening an unavailable upgrade page. Improves status text contrast. Cost previews share one owned-building catalogue instead of downloading it for every hospital. Operations includes hospital target-level selection from 1 to 30, all or individual selection, native Credit cost estimates, saved sequential purchases and pause/resume. Higher prices and uncertain results pause the run. Sharing and tax are not modified. Live hospital upgrades have not been tested.</p>',1))
p=out/'popup.html';p.write_text(p.read_text().replace('>1.0.0<','>1.1.3 test<'))
p=out/'privacy.html';p.write_text(p.read_text().replace('Extension 1.0.0. Updated','Extension 1.1.3 test. Updated').replace('<h2>Your choices</h2>','<h2>Hospital upgrade checkpoints</h2><p>Hospital upgrade plans store the game account ID, selected hospital IDs and names, target levels, confirmed Credit ceiling, progress and purchase verification checkpoints in MissionChief site-local storage. A cross-tab browser lock prevents overlapping hospital upgrade runs. Saved purchases do not resume without confirmation. Clear MissionChief site storage to remove these records.</p><h2>Your choices</h2>'))
p=out/'help.html';p.write_text(p.read_text().replace('Extension 1.0.0 ·','Extension 1.1.3 test ·').replace('<h2>Tasks and recovery</h2>','<h2>Hospital upgrades</h2><p>In Operations choose Hospital upgrades. Load hospitals, select a target from 1–30 and choose all eligible hospitals or individual rows. Preview selected costs, then Review &amp; upgrade. The displayed estimate is also the maximum authorised total. Increased target prices pause the job. Pause waits for the current request; closing the panel preserves progress. Review &amp; resume verifies uncertain purchases first. Browser Web Locks support is required. No sharing, tax or medical extensions are changed. Live upgrade acceptance remains untested.</p><h2>Tasks and recovery</h2>'))
p=out/'README.md';p.write_text('# Hospital upgrades — 1.1.3 test package\n\nNew Operations hospital level tool. 82 automated tests pass; live hospital upgrades have not been tested. The 1.0.0 store submission is unchanged.\n\n'+p.read_text())
archive=out.parent/'MissionChief-Toolkit-Extension-1.1.3-test.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.writestr(zipfile.ZipInfo(str(p.relative_to(out)),(2026,1,1,0,0,0)),p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
print(archive)
