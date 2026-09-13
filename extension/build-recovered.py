"""Build an extension overlay without modifying the verified recovered baseline."""
import hashlib,json,pathlib,re,shutil,zipfile
root=pathlib.Path(__file__).resolve().parent
baseline=root/'recovered-0.22.3'
for name,digest in json.loads((root/'recovery-sha256.json').read_text()).items():
 assert hashlib.sha256((baseline/name).read_bytes()).hexdigest()==digest,name
out=root.parent/'.dev/home-response-extension'
if out.exists():shutil.rmtree(out)
shutil.copytree(baseline,out)
parts=[]
for name in ['land-data','planner','land','catalogue','queue','native','images','dispatch','areas','ui']:
 text=(root/'home-response'/f'{name}.mjs').read_text()
 text=re.sub(r'^import .*?;\n','',text,flags=re.M)
 text=re.sub(r'^export ','',text,flags=re.M)
 parts.append(text)
bundle='const HomeResponseBuilder=(()=>{\n'+'\n'.join(parts)+'\nreturn {mount,destroy,configureImages,createImageBridge,nativeAdapter};})();\n'
p=out/'toolkit.js';s=p.read_text()
anchor='function createOperationsController(api){'
assert s.count(anchor)==1
s=s.replace(anchor,bundle+anchor)
anchor="home.append(el('p','You can return here while a task runs. Keep the game tab open; use Stop to end the task.')"
assert s.count(anchor)==1
s=s.replace(anchor,'HomeResponseBuilder.mount(grid);\n    '+anchor)
cleanup='runtimeOnCleanup(()=>{pilot.operations?.destroy();pilot.operations=null;});'
assert s.count(cleanup)==1
s=s.replace(cleanup,'runtimeOnCleanup(()=>{HomeResponseBuilder.destroy();pilot.operations?.destroy();pilot.operations=null;});')
type_labels={}
for label,ids in re.findall(r"defineNativeBuildingQuickFilter\('([^']+)'.*?, \[([0-9, ]+)\], '\w+'\)",s):
 for type_id in ids.split(','):type_labels[type_id.strip()]=label
anchor='pilot.operations=createOperationsController({'
assert s.count(anchor)==1
s=s.replace(anchor,'''HomeResponseBuilder.configureImages(HomeResponseBuilder.createImageBridge({storage:window.localStorage,scope:async()=>String((await HomeResponseBuilder.nativeAdapter(window).account()).user_id),typeLabels:__HR_TYPE_LABELS__,list:fetchStationIconBuildings,building:fetchStationIconBuilding,image:fetchStationIconImage,apply:applyStationIconToStation}));
'''.replace('__HR_TYPE_LABELS__',json.dumps(type_labels))+anchor)
p.write_text(s)
import runpy
runpy.run_path(str(root/'operations-navigation.py'))['patch_operations_navigation'](out)
runpy.run_path(str(root/'icon-form-compatibility.py'))['patch_icon_form'](out)
m=json.loads((out/'manifest.json').read_text());m['version']='0.23.13';m['version_name']='Home Response testing · Extension 0.23.13 · Toolkit 10.18.1';(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
for name in ['TEST-RESULTS.json','TRANSPORT-TEST-RESULTS.json']:(out/name).unlink()
(out/'BUILD.json').write_text(json.dumps({'extensionVersion':'0.23.13','recoveredBaseline':'0.22.3','channel':'home-response-testing','storeSubmission':'not-submitted','livePurchaseValidation':'pending'},indent=2)+'\n')
shutil.copytree(root/'home-response'/'geodata',out/'home-response-geodata')
p=out/'release-notes.html';p.write_text(p.read_text().replace('<main>','<main><h1>Home Response Builder · 0.23.13 testing</h1><p>Adds Select area on map: tap a UK location to retrieve city or town boundaries, choose between overlapping results and continue with the standard preview and nearest dispatch selection. Minimum spacing, water checks and purchase recovery remain enforced. Review road access and crew requirements. Live purchase acceptance remains pending.</p>',1))
archive=out.parent/'MissionChief-Toolkit-Extension-0.23.13-test.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.writestr(zipfile.ZipInfo(str(p.relative_to(out)),(2026,1,1,0,0,0)),p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
print(archive)
