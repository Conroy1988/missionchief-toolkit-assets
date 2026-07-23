#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUT_DIR = ROOT / '.github/diagnostics'
lines = SOURCE.read_text(encoding='utf-8').splitlines()


def write_slice(name: str, start: int, end: int) -> None:
    content = [f'ISSUE #470 SOURCE SLICE {name}', f'lines={start}-{end}', '']
    for number in range(start, min(end, len(lines)) + 1):
        content.append(f'{number:05d}: {lines[number - 1]}')
    (OUT_DIR / f'issue470-{name}.txt').write_text('\n'.join(content) + '\n', encoding='utf-8')

OUT_DIR.mkdir(parents=True, exist_ok=True)
write_slice('requirements-source-slice', 22120, 22740)
write_slice('menu-state-slice', 28780, 30720)
SELF.unlink(missing_ok=True)
print('wrote Issue #470 source slices')
