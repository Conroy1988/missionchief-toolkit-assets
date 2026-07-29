#!/usr/bin/env python3
import re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
version_match=re.search(r'(?m)^//\s*@version\s+([^\s]+)$',s);assert version_match and tuple(int(part) for part in version_match.group(1).split('.')) >= (8,2,7)
for marker in [
 "TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS = new Set(['discharge patient', 'cancel transport'])",
 'function transportSweepNativeReleaseControlText(control)',
 "'button, a, input[type=\"button\"], input[type=\"submit\"]'",
 "button.getAttribute?.('aria-disabled') === 'true'",
 'const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);',
 'const vehicleResult = await openTransportSweepVehicle(candidate);',
 'const releaseControlLabel = transportSweepNativeReleaseControlText(button);',
 'button.click();',
 'clickTransportSweepDischargeConfirmation(releaseKey);',
 'transportSweepNativeReleaseControlText(button) !== releaseControlLabel',
 'recordTransportSweepConfirmedRelease(',
 r"/patient (?:is not|isn['’]t) transported\.?/gi",
 "MissionChief's native Discharge patient control",
]: assert marker in s,marker
m=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',s);assert m
body=m.group(1)
assert "!== 'discharge patient'" not in body
print('Native Patient Transport Sweep Cancel Transport contract passed.')
