#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'docs/audits/issue-588/manifest.json').read_text(encoding='utf-8'))
runtime=json.loads((ROOT/'docs/audits/issue-588/runtime-stress.json').read_text(encoding='utf-8'))
budget=json.loads((ROOT/'docs/audits/issue-588/performance-budget-report.json').read_text(encoding='utf-8'))
assert manifest['issue']==588 and manifest['parentIssue']==247
assert manifest['measurementOnly'] is True
assert manifest['toolkitVersion']=='8.3.1'
assert manifest['sourceSha256']=='363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089'
assert manifest['sourceDistributionParity'] is True
assert budget['result']=='success'
assert manifest['performanceBudgetStatus']==budget['result']=='success'
assert runtime['schemaVersion']==2 and runtime['status']=='passed'
assert runtime['discovery']['authority']=='.github/scripts/run_userscript_preflight.sh'
assert '.github/scripts/test_issue564_incident_feed_attended_runtime.js' in runtime['discovery']['canonicalRuntimeContracts']
assert runtime['repeatedExecutions']>88
assert len(runtime['results'])==len(runtime['discovery']['plannedContracts'])
assert not runtime['failures']
source=(ROOT/'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
dist=(ROOT/'dist/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
txt=(ROOT/'dist/MissionChief_Map_Command_Toolkit.txt').read_bytes()
assert source==dist==txt
print('Issue #588 v8.3.1 measurement-only performance baseline contract passed.')
