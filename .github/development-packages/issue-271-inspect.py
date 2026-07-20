#!/usr/bin/env python3
from pathlib import Path

source = Path('src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
for marker in [
    'function missionRequirementsMetadataValues',
    'function missionRequirementsCollectUnits',
    'function missionRequirementsAggregate',
    'function missionRequirementsUnitContribution',
    'function missionRequirementsStaffCapacity',
]:
    index = source.find(marker)
    print(f'\n===== {marker} @ {index} =====')
    if index >= 0:
        print(source[index:index + 9000])
raise RuntimeError('inspection-only package; no repository changes requested')
