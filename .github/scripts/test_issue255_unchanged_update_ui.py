#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'docs/audits/issue-255/manifest.json').read_text(encoding='utf-8'))
report=json.loads((ROOT/'docs/audits/issue-255/unchanged-update-ui.json').read_text(encoding='utf-8'))
assert manifest['issue']==255 and manifest['parentIssue']==247
assert manifest['measurementOnly'] is True
assert manifest['toolkitVersion']=='8.3.1'
assert manifest['sourceSha256']=='363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089'
assert manifest['sourceDistributionParity'] is True
assert manifest['productionOptimisationAuthorised'] is False
assert manifest['scenarios']==['idle-panel-closed','settings-open','resources-open','operations-open']
assert report['instrumentation']['generator']=='tools/build-render-probe-userscript.mjs'
assert report['instrumentation']['productionSourceModified'] is False
assert report['summary']['changedWriteAttempts']==0
assert report['summary']['redundantWriteAttempts']>0
assert report['summary']['mutationRecords']>0
for scenario in report['scenarios']:
    assert scenario['repeats']==25
    assert scenario['renderProbeBegins']==25 and scenario['renderProbeEnds']==25
    assert scenario['selectorReads']>0 and scenario['writeAttempts']>0
    assert scenario['changedWriteAttempts']==0
source=(ROOT/'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
dist=(ROOT/'dist/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
txt=(ROOT/'dist/MissionChief_Map_Command_Toolkit.txt').read_bytes()
assert source==dist==txt
print('Issue #255 v8.3.1 unchanged updateUI measurement contract passed.')
