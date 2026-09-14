"""Compose matching icon replacement over the maintained extension. No Store submission."""
import json,pathlib,re,runpy,zipfile,shutil
root=pathlib.Path(__file__).resolve().parent
runpy.run_path(str(root/'prepare-current-release.py'))
out=root.parent/'.dev/home-response-extension'
parts=[]
for name in ['core.mjs','ui.mjs']:
 s=(root/'icon-replacer'/name).read_text()
 s=re.sub(r'^import .*?;\n','',s,flags=re.M);s=re.sub(r'^export ','',s,flags=re.M);parts.append(s)
bundle='const IconReplacement=(()=>{\n'+'\n'.join(parts)+'\nreturn {configureIconReplacement,openIconReplacement,destroyIconReplacement};})();\n'
p=out/'toolkit.js';s=p.read_text();labels={}
for label,ids in re.findall(r"defineNativeBuildingQuickFilter\('([^']+)'.*?, \[([0-9, ]+)\], '\w+'\)",s):
 for type_id in ids.split(','):labels[type_id.strip()]=label
anchor='function createOperationsController(api){';assert s.count(anchor)==1;s=s.replace(anchor,bundle+anchor)
anchor="choose.append(el('h3','1. Choose what to include'));";assert s.count(anchor)==1;s=s.replace(anchor,anchor+"if(definition[0]==='station-icon-copier')choose.prepend(button('Replace matching icons…',()=>IconReplacement.openIconReplacement()));")
anchor='pilot.operations=createOperationsController({';assert s.count(anchor)==1
s=s.replace(anchor,"IconReplacement.configureIconReplacement({account:()=>HomeResponseBuilder.nativeAdapter(window).account(),list:fetchStationIconBuildings,building:fetchStationIconBuilding,image:fetchStationIconImage,apply:applyStationIconToStation,typeName:typeId=>stationIconTypeLabel({typeId}),busy:()=>stationIconCopierRuntime.running||stationIconCopierRuntime.preparing||dispatchRecruitmentRuntime.running||expansionPlannerRuntime.running});\n"+anchor)
s=s.replace('UnitSwitcher.destroySwitcher();','UnitSwitcher.destroySwitcher();IconReplacement.destroyIconReplacement();')
anchor="b.onclick=openSwitcher;grid.append(b);";assert s.count(anchor)==1;s=s.replace(anchor,"const badge=document.createElement('small');badge.textContent='Ready';b.append(badge);"+anchor)
s=s.replace('typeName:typeId=>stationIconTypeLabel({typeId}),','typeName:typeId=>('+json.dumps(labels)+')[typeId]||stationIconTypeLabel({typeId}),')
p.write_text(s)
# Match the original pixels again inside the native copier's last pre-upload read.
p=out/'features/administration.js';s=p.read_text()
anchor="        if (baseline.hasCustomIcon) {";assert s.count(anchor)==1
s=s.replace(anchor,"        if (plan.expectedIcon && !baseline.hasCustomIcon) throw Error('Original icon changed after preview. No upload sent.');\n"+anchor)
anchor="            if ((0,__mcmsModuleContext.stationIconImagesMatch)(currentImage, sourceImage)) return"
assert s.count(anchor)==1
s=s.replace(anchor,"            if (plan.expectedIcon && !(0,__mcmsModuleContext.stationIconImagesMatch)(currentImage, plan.expectedIcon)) throw Error('Original icon changed after preview. No upload sent.');\n"+anchor)
p.write_text(s)
p=out/'command-ui.css';p.write_text(p.read_text()+'\n'+(root/'icon-replacer/operations.css').read_text())
p=out/'manifest.json';m=json.loads(p.read_text());m.update(version='1.3.0',version_name='Extension 1.3.0 testing · Matching icon replacement');p.write_text(json.dumps(m,indent=2)+'\n')
p=out/'BUILD.json';m=json.loads(p.read_text());m.update(extensionVersion='1.3.0',channel='icon-replacement-testing',liveValidation='Matching icon uploads require live acceptance');m.pop('automatedTests',None);p.write_text(json.dumps(m,indent=2)+'\n')
for name in ['popup.html','help.html','privacy.html','release-notes.html','README.md']:
 p=out/name;p.write_text(p.read_text().replace('1.2.5','1.3.0'))
p=out/'help.html';p.write_text(p.read_text().replace('<main>','<main><h2>Replace matching station icons</h2><p>In Operations, open Copy station icons, then Replace matching icons. Choose a building type and dispatch scope, scan custom icons, choose the original and replacement, and refresh the preview. Review the selected buildings before confirming. Saved progress supports Pause and Review &amp; resume. Default icons and unreadable images are excluded. An uncertain upload is verified without automatic replay.</p>',1))
p=out/'privacy.html';p.write_text(p.read_text().replace('<main>','<main><h2>Matching icon replacement</h2><p>Account-scoped browser storage retains icon catalogue URLs, pixel fingerprints, building IDs and scope metadata, plus approved replacement progress. Image bytes are not stored in these checkpoints. Clearing MissionChief site storage removes this data.</p>',1))
p=out/'release-notes.html';s=p.read_text();start=s.index('<main>');end=s.index('</main>',start);p.write_text(s[:start]+'<main><h1>1.3.0 test</h1><p>Replace a matching custom icon across reviewed buildings. Filter by type and dispatch centre, use a saved visual catalogue, preview matching buildings, confirm replacement and follow saved progress. Images are matched by pixel contents. Operations rows now share consistent name, description and status columns, with a stacked narrow layout. Live upload testing remains required.</p>'+s[end:])
for name in ['popup.html','popup.css','popup.js']:
 shutil.copyfile(root/'popup'/name,out/name)
archive=out.parent/'MissionChief-Toolkit-Extension-1.3.0-test.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(out))
print(archive)
