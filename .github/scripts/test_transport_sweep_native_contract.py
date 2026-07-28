#!/usr/bin/env python3
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
