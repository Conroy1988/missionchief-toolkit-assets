#!/usr/bin/env python3
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
