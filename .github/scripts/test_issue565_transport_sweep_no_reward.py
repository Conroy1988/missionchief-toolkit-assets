#!/usr/bin/env python3
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
h=(R/'help/index.html').read_text(encoding='utf-8')
c=(R/'CHANGELOG.md').read_text(encoding='utf-8')
p=json.loads((R/'.github/performance-budget.json').read_text(encoding='utf-8'))
assert re.search(r'(?m)^//\s*@version\s+8\.2\.7$',s)
assert "'cancel transport'" in s
assert 'const releaseControlLabel = transportSweepNativeReleaseControlText(button);' in s
assert 'transportSweepNativeReleaseControlText(button) !== releaseControlLabel' in s
assert '## [8.2.7] - 2026-07-29' in c
assert 'Cancel Transport' in h and 'Patient isn’t transported' in h
assert p['transitionApproval']['version']=='8.2.7'
assert p['transitionApproval']['approvedNetworkRequestDelta']==0
assert p['absoluteLimits']['network_request_calls']==5
print('Issue #565 v8.2.7 Cancel Transport contract passed.')
