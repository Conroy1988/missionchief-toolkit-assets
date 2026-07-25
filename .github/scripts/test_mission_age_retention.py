#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
required=['missionAge: false',"makeToggleButton('missionAge'",'function formatMissionAge(','function makeMissionAgeIcon(','function missionAgeRefreshPlan(','function updateMissionAgeLabels(','function clearMissionAgeLabels(','if (state.missionAge) scheduleMissionAgeRefresh();','if (!state.missionAge) clearMissionAgeLabels();']
missing=[item for item in required if item not in source];assert not missing,missing
print('Mission Age map timers retained under v7.')
