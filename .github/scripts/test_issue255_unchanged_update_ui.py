#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((ROOT / 'docs/audits/issue-255/manifest.json').read_text(encoding='utf-8'))
report = json.loads((ROOT / 'docs/audits/issue-255/unchanged-update-ui.json').read_text(encoding='utf-8'))
optimised = json.loads((ROOT / 'docs/audits/issue-255/write-suppression-v832.json').read_text(encoding='utf-8'))

assert manifest['issue'] == 255 and manifest['parentIssue'] == 247
assert manifest['measurementOnly'] is True
assert manifest['toolkitVersion'] == '8.3.1'
assert manifest['sourceSha256'] == '363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089'
assert manifest['sourceDistributionParity'] is True
assert manifest['productionOptimisationAuthorised'] is True
assert manifest['optimisedToolkitVersion'] == '8.3.2'
assert manifest['optimisedEvidence'] == 'write-suppression-v832.json'
assert manifest['stateTransitionVerified'] is True
assert manifest['frameworkReplacementVerified'] is True
assert manifest['scenarios'] == ['idle-panel-closed', 'settings-open', 'resources-open', 'operations-open']

assert report['instrumentation']['generator'] == 'tools/build-render-probe-userscript.mjs'
assert report['instrumentation']['productionSourceModified'] is False
assert report['summary']['changedWriteAttempts'] == 0
assert report['summary']['redundantWriteAttempts'] == 14500
assert report['summary']['mutationRecords'] == 7100
for scenario in report['scenarios']:
    assert scenario['repeats'] == 25
    assert scenario['renderProbeBegins'] == 25 and scenario['renderProbeEnds'] == 25
    assert scenario['selectorReads'] > 0 and scenario['writeAttempts'] > 0
    assert scenario['changedWriteAttempts'] == 0

assert optimised['toolkitVersion'] == '8.3.2'
assert optimised['before']['writeAttempts'] == 14500
assert optimised['before']['mutationRecords'] == 7100
assert optimised['after']['writeAttempts'] == 0
assert optimised['after']['mutationRecords'] == 0
assert optimised['stateTransition']['changed']['counters']['changedWriteAttempts'] > 0
assert optimised['stateTransition']['stableRepeat']['counters']['writeAttempts'] == 0
assert optimised['frameworkReplacement']['changed']['counters']['changedWriteAttempts'] > 0
assert optimised['frameworkReplacement']['stableRepeat']['counters']['writeAttempts'] == 0

source = (ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
dist = (ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
txt = (ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt').read_bytes()
assert source == dist == txt
print('Issue #255 baseline and v8.3.2 updateUI write-suppression evidence contract passed.')
