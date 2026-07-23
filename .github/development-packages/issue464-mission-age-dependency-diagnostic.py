#!/usr/bin/env python3
from __future__ import annotations

import difflib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-mission-age-dependencies.txt'
current = SOURCE.read_text(encoding='utf-8')


def git_show(spec: str) -> str:
    result = subprocess.run(['git', 'show', spec], cwd=ROOT, check=False, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ''


baseline = git_show('v4.20.37:src/MissionChief_Map_Command_Toolkit.user.js') or git_show('v4.20.37:MissionChief_Map_Command_Toolkit.user.js')
if not baseline:
    raise SystemExit('Unable to load v4.20.37 source baseline')


def function_span(source: str, name: str) -> tuple[int, int] | None:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\(', source)
    if not match:
        return None
    paren = source.find('(', match.start())
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = paren
    body_open = -1
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if ch == '\n': line_comment = False
            i += 1; continue
        if block_comment:
            if ch == '*' and nxt == '/': block_comment = False; i += 2
            else: i += 1
            continue
        if quote:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if ch == '/' and nxt == '/': line_comment = True; i += 2; continue
        if ch == '/' and nxt == '*': block_comment = True; i += 2; continue
        if ch in "'\"`": quote = ch; i += 1; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                body_open = source.find('{', i + 1)
                break
        i += 1
    if body_open < 0:
        return None
    depth = 0; quote = None; escaped = False; line_comment = False; block_comment = False; i = body_open
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if ch == '\n': line_comment = False
            i += 1; continue
        if block_comment:
            if ch == '*' and nxt == '/': block_comment = False; i += 2
            else: i += 1
            continue
        if quote:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if ch == '/' and nxt == '/': line_comment = True; i += 2; continue
        if ch == '/' and nxt == '*': block_comment = True; i += 2; continue
        if ch in "'\"`": quote = ch; i += 1; continue
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return match.start(), i + 1
        i += 1
    return None


def function_text(source: str, name: str) -> str:
    span = function_span(source, name)
    return source[span[0]:span[1]] if span else '[missing]'


def css_context(source: str, selector: str) -> str:
    positions = [m.start() for m in re.finditer(re.escape(selector), source)]
    blocks = []
    for pos in positions:
        left = max(0, source.rfind('\n', 0, max(0, pos - 500)))
        right = source.find('\n', min(len(source), pos + 900))
        if right < 0: right = len(source)
        blocks.append(source[left:right])
    return '\n---\n'.join(blocks)


names = [
    'getMissionMarkerLayers', 'missionIdFromMarker', 'isPersonalMissionLayer',
    'captureMissionMarkerDataFromDocument', 'captureMissionMarkerData',
    'exactMissionTimestampFromObject', 'timestampFromMissionPanel',
    'findLeafletMapInstance', 'invalidateMarkerRegistryCaches',
    'scheduleEnabledMapRefreshes', 'reconcileFeatureRefreshes',
    'missionSnapshotsNeeded', 'handleMapVisibilityToggle',
]
parts = ['ISSUE #464 MISSION AGE DEPENDENCY COMPARISON']
for name in names:
    old = function_text(baseline, name)
    new = function_text(current, name)
    parts += ['', '=' * 110, name]
    if old == new:
        parts += ['[identical]', new]
    else:
        parts.extend(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=f'v4.20.37/{name}', tofile=f'v5.0.5/{name}', lineterm=''))

for selector in ['.mcms-mission-age-icon', '.mcms-mission-age-badge', '.mcms-mission-float-pane']:
    old = css_context(baseline, selector)
    new = css_context(current, selector)
    parts += ['', '=' * 110, f'CSS {selector}']
    if old == new:
        parts += ['[identical]', new]
    else:
        parts.extend(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=f'v4.20.37/{selector}', tofile=f'v5.0.5/{selector}', lineterm=''))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
