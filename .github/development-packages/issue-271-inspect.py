#!/usr/bin/env python3
from pathlib import Path

source = Path('src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
parts = []
for marker in [
    'function missionRequirementsMetadataValues',
    'function missionRequirementsCollectUnits',
    'function missionRequirementsAggregate',
    'function missionRequirementsUnitContribution',
    'function missionRequirementsStaffCapacity',
]:
    index = source.find(marker)
    parts.append(f'\n===== {marker} @ {index} =====\n')
    if index >= 0:
        parts.append(source[index:index + 12000])
Path('docs/issue-271-runtime-snippets.txt').write_text(''.join(parts), encoding='utf-8')
