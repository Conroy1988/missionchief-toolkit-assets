#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-mission-age-runtime.txt'
text = SOURCE.read_text(encoding='utf-8')


def line_number(offset: int) -> int:
    return text.count('\n', 0, max(0, offset)) + 1


def function_span(name: str) -> tuple[int, int] | None:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{', text)
    if not match:
        return None
    open_pos = text.find('{', match.start(), match.end())
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = open_pos
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ''
        if line_comment:
            if ch == '\n':
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == '/' and nxt == '/':
            line_comment = True
            i += 2
            continue
        if ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return match.start(), i + 1
        i += 1
    raise RuntimeError(f'unclosed function {name}')


function_names = [m.group(1) for m in re.finditer(r'(?m)^\s*function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{', text)]
selected = []
for name in function_names:
    lower = name.lower()
    if 'missionage' in lower or name in {
        'toggleFeature', 'handleKeyboard', 'scheduleEnabledMapRefreshes',
        'refreshMissionSnapshots', 'missionMarkerIndex', 'getMissionMarkers',
        'mutationAffectsMissionData', 'mutationAddsLeafletMarkerIcon'
    }:
        selected.append(name)

parts = [
    'ISSUE #464 MISSION AGE RUNTIME DIAGNOSTIC',
    f'source_lines={len(text.splitlines())}',
    '',
    'MISSION AGE TOKEN LOCATIONS',
]
for match in re.finditer(r'(?i)missionAge|mission-age|mcms-mission-age', text):
    start = max(0, text.rfind('\n', 0, match.start() - 1))
    end = text.find('\n', match.end())
    if end < 0:
        end = len(text)
    parts.append(f'{line_number(match.start()):05d}: {text[start:end].strip()}')

parts += ['', 'SELECTED FUNCTIONS']
for name in selected:
    span = function_span(name)
    if not span:
        continue
    start, end = span
    parts += [
        '',
        '=' * 110,
        f'{name} lines {line_number(start)}-{line_number(end)}',
        text[start:end],
    ]

for marker in [
    "case 'missionAge'", "case '6'", "key === '6'", "event.key === '6'",
    "scheduleMissionAgeRefresh", "clearMissionAgeLabels", "missionAgeGroup"
]:
    parts += ['', '=' * 110, f'CONTEXT {marker!r}']
    pos = text.find(marker)
    if pos < 0:
        parts.append('[missing]')
        continue
    left = max(0, text.rfind('\n', 0, max(0, pos - 1800)))
    right = text.find('\n', min(len(text), pos + 3000))
    if right < 0:
        right = len(text)
    parts.append(text[left:right])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
