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
for name in ['land-data','planner','land','catalogue','queue','native','images','ui']:
 text=(root/'home-response'/f'{name}.mjs').read_text()
 text=re.sub(r'^import .*?;\n','',text,flags=re.M)
 text=re.sub(r'^export ','',text,flags=re.M)
 parts.append(text)
bundle='const HomeResponseBuilder=(()=>{\n'+'\n'.join(parts)+'\nreturn {mount,destroy,configureImages,createImageBridge};})();\n'
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
anchor='pilot.operations=createOperationsController({'
assert s.count(anchor)==1
s=s.replace(anchor,'''HomeResponseBuilder.configureImages(HomeResponseBuilder.createImageBridge({list:fetchStationIconBuildings,building:fetchStationIconBuilding,image:fetchStationIconImage,apply:applyStationIconToStation}));
'''+anchor)
p.write_text(s)
m=json.loads((out/'manifest.json').read_text());m['version']='0.23.3';m['version_name']='Home Response testing · Extension 0.23.3 · Toolkit 10.18.1';(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
for name in ['TEST-RESULTS.json','TRANSPORT-TEST-RESULTS.json']:(out/name).unlink()
(out/'BUILD.json').write_text(json.dumps({'extensionVersion':'0.23.3','recoveredBaseline':'0.22.3','channel':'home-response-testing','storeSubmission':'not-submitted','livePurchaseValidation':'pending'},indent=2)+'\n')
shutil.copytree(root/'home-response'/'geodata',out/'home-response-geodata')
p=out/'release-notes.html';p.write_text(p.read_text().replace('<main>','<main><h1>Home Response Builder · 0.23.3 testing</h1><p>Excludes mapped sea and lakes using bundled shoreline data. Applies the same check to moved markers and new construction in saved plans. Small waterways and road access still require visual review. Review road access and crew requirements. Live purchase acceptance remains pending.</p>',1))
archive=out.parent/'MissionChief-Toolkit-Extension-0.23.3-test.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.writestr(zipfile.ZipInfo(str(p.relative_to(out)),(2026,1,1,0,0,0)),p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
print(archive)
