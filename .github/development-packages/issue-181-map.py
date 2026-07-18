#!/usr/bin/env python3
from pathlib import Path
root = Path(__file__).resolve().parents[2]
lines = (root / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8').splitlines()
sections = [(21600, 23150), (23150, 23950)]
out = []
for start, end in sections:
    out.append(f'===== lines {start + 1}-{end} =====')
    out.extend(f'{i + 1:05d}: {lines[i]}' for i in range(start, min(end, len(lines))))
path = root / '.github' / 'diagnostics' / 'issue-181-map.txt'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text('\n'.join(out) + '\n', encoding='utf-8')
print(path.relative_to(root))
