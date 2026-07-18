#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = root / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
out = root / '.github' / 'diagnostics' / 'issue-176-target-map.txt'
lines = source.read_text(encoding='utf-8', errors='replace').splitlines()
result = ['Issue 176 targeted source map', '']
for start, end, label in [
    (430, 760, 'script and defaults'),
    (15150, 15760, 'vehicle data cache'),
    (22170, 22390, 'vehicle identity and matrix'),
    (23470, 23640, 'mission window observers'),
    (30000, 31643, 'startup tail'),
]:
    result.append(f'===== {label}: {start}-{end} =====')
    result.extend(f'{index + 1:06d}: {lines[index]}' for index in range(start - 1, min(end, len(lines))))
    result.append('')
for term in [
    'missionRequirementsPanel',
    'installMissionRequirementsWindows',
    'clearMissionRequirementsPanels',
    'personalVehicleApiCache',
    'vehicleApiReady',
    'refreshPersonalVehicleData',
    'Available Units',
    'data-setting',
    'toggle',
]:
    result.append(f'===== matches: {term} =====')
    result.extend(f'{index + 1:06d}: {line}' for index, line in enumerate(lines) if term.lower() in line.lower())
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(result) + '\n', encoding='utf-8')
print(out.relative_to(root))
