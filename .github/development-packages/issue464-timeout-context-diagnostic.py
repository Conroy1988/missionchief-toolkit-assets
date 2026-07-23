#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-timeout-contexts.txt'

lines = SOURCE.read_text(encoding='utf-8').splitlines()
interesting = []
for index, line in enumerate(lines):
    lowered = line.lower()
    if 'runtimesettimeout' not in lowered:
        continue
    if any(token in lowered for token in ('focus', 'missionage', 'mission age', 'arrsearch', 'dropdown')):
        start = max(0, index - 2)
        end = min(len(lines), index + 3)
        interesting.extend([
            '=' * 120,
            f'line={index + 1}',
            *[f'{cursor + 1:05d}: {lines[cursor]}' for cursor in range(start, end)],
            '',
        ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join([
    'Issue #464 timeout call-site contexts',
    f'total_runtimeSetTimeout={sum(line.count("runtimeSetTimeout") for line in lines)}',
    '',
    *interesting,
]), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
