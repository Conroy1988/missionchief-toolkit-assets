#!/usr/bin/env python3
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');token='ls'+'sm'
assert token not in source.lower()
required=['function collectTransportSweepVehicleCandidatesForMission(missionId)','async function openTransportSweepVehicle(candidate)','function transportSweepVisibleDischargeButtons()','function findVisibleDischargePatientButton(excludedButtons = null)',"const TRANSPORT_SWEEP_RELEASE_CONFIRMATION_TEXT = 'Understood! We have released the patient.';",'function captureTransportSweepReleaseConfirmationBaseline()','function transportSweepReleaseConfirmationVisible(baseline = null)','function recordTransportSweepConfirmedRelease(releaseKey, message)','confirmedReleaseKeys: new Set()',"async function closeTransportSweepWindows(reason = 'navigation')",'activeWindowRoot: null','ownedWindowLayers: new Set()','function ensureTransportSweepHud()','function renderTransportSweepHud()',"MissionChief's native Discharge patient control"]
missing=[item for item in required if item not in source];assert not missing,missing
processor=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',source);assert processor
body=processor.group(1)
for item in ['collectTransportSweepVehicleCandidatesForMission(missionId)','openTransportSweepVehicle(candidate)','button.click()','recordTransportSweepConfirmedRelease(']: assert item in body
assert body.index('button.click()') < body.index('recordTransportSweepConfirmedRelease(')
assert source.count('transportSweepRuntime.cleared += 1')==1
assert source.count('transportSweepRuntime.processed += 1')==1
print('Native Patient Transport Sweep contract passed.')
