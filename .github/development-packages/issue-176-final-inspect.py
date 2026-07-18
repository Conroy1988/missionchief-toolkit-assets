#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = root / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
out = root / '.github' / 'diagnostics' / 'issue-176-final-map.txt'
lines = source.read_text(encoding='utf-8', errors='replace').splitlines()
terms = [
    "const state =",
    "function defaultState",
    "missionRequirements:",
    "function toggleFeature(feature)",
    "const controlToggleValues =",
    "const toggleValues =",
    "installMissionRequirementsWindows();",
    "refreshPersonalVehicleData(",
    "const personalVehicleApiCache",
    "function vehicleRecordId",
    "function normaliseVehicleApiPayload",
    "function saveState",
    "function loadState",
]
result = ['Issue 176 final source map', '']
seen = set()
for term in terms:
    matches = [i for i, line in enumerate(lines) if term in line]
    result.append(f'===== {term!r}: {len(matches)} matches =====')
    for index in matches[:12]:
        start = max(0, index - 55)
        end = min(len(lines), index + 120)
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)
        result.append(f'--- source lines {start + 1}-{end}, match {index + 1} ---')
        result.extend(f'{i + 1:06d}: {lines[i]}' for i in range(start, end))
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(result) + '\n', encoding='utf-8')
print(out.relative_to(root))
