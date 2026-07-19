#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
output = ROOT / '.github' / 'diagnostics' / 'issue-183-resolver-probe.txt'
needles = [
    'function missionRequirementsResolve(',
    'function missionRequirementsCatalogueParseDocument(',
    'function missionRequirementsCatalogueEnsure(',
    'function missionRequirementsPanelHtml(',
]
parts = []
for needle in needles:
    index = source.find(needle)
    parts.append(f'===== {needle} index={index} =====\n')
    if index >= 0:
        parts.append(source[index:index + 9000])
    parts.append('\n\n')
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(''.join(parts), encoding='utf-8')
print(output.relative_to(ROOT))
