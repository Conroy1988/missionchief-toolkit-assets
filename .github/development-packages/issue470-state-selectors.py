#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue470-state-selectors.txt'
text = SOURCE.read_text(encoding='utf-8')
lines = text.splitlines()
patterns = [
    'commandBarOpen', 'mcms-dock-toggle', 'mcms-floating-filter', 'mcms-screen-pins',
    'data-mcms-command', 'applyRootAttributes', 'toggleCommandBar',
    'operationalSuiteScan', 'operationalDocument', 'operationalSuiteContexts',
    'DOMParser', 'fetch(', 'GM_xmlhttpRequest', 'mission-form', 'mission_type_id',
]
parts = ['ISSUE #470 STATE / SELECTOR DIAGNOSTIC', f'lines={len(lines)}', '']
for pattern in patterns:
    parts.append('=' * 100)
    parts.append(f'PATTERN {pattern}')
    count = 0
    for index, line in enumerate(lines, 1):
        if pattern.lower() not in line.lower():
            continue
        lo = max(1, index - 3)
        hi = min(len(lines), index + 3)
        parts.extend(f'{number:05d}: {lines[number - 1]}' for number in range(lo, hi + 1))
        parts.append('---')
        count += 1
        if count >= 80:
            parts.append('[truncated]')
            break
    parts.append(f'count={count}')
    parts.append('')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
