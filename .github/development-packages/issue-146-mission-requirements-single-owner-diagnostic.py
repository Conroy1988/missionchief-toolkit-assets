#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
parts = []
for symbol in ('missionRequirementsRemoveRecord', 'missionRequirementsEnsureRecord', 'scanMissionRequirementsWindows'):
    index = source.find(symbol)
    if index < 0:
        parts.append(f'{symbol}: NOT FOUND')
        continue
    start = max(0, index - 2500)
    end = min(len(source), index + 12000)
    parts.append(f'### {symbol} at byte {index}\n\n{source[start:end]}')
report = 'Issue #146 Mission Requirements ownership diagnostic\n\n' + '\n\n---\n\n'.join(parts) + '\n'
path = ROOT / '.github' / 'diagnostics' / 'issue-146-mission-requirements-ownership.txt'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(report, encoding='utf-8')
print('Issue #146 ownership diagnostic written')
