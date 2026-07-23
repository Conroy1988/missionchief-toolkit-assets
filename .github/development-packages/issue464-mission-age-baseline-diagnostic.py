#!/usr/bin/env python3
from __future__ import annotations

import difflib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-mission-age-v4-comparison.txt'
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
    open_pos = source.find('{', match.start())
    if open_pos < 0:
        return None
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = open_pos
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
            if depth == 0: return match.start(), i + 1
        i += 1
    return None


def function_text(source: str, name: str) -> str:
    span = function_span(source, name)
    return source[span[0]:span[1]] if span else '[missing]'


names = [
    'ensureMissionFloatPane',
    'getMissionCreatedAt',
    'clearMissionAgeLabels',
    'makeMissionAgeIcon',
    'updateMissionAgeLabels',
    'scheduleMissionAgeRefresh',
    'getMissionMarkerIndex',
    'missionKnownPersonal',
    'scanInlineMissionMarkerData',
    'installMissionMarkerAddHook',
    'scheduleEnabledMapRefreshes',
    'reconcileFeatureRefreshes',
    'applyMapVisibilityToggleEffects',
    'toggleFeature',
]

parts = [
    'ISSUE #464 MISSION AGE v4.20.37 COMPARISON',
    f'baseline_bytes={len(baseline.encode("utf-8"))}',
    f'current_bytes={len(current.encode("utf-8"))}',
]
for name in names:
    old = function_text(baseline, name)
    new = function_text(current, name)
    parts += ['', '=' * 110, name]
    if old == new:
        parts.append('[identical]')
        parts.append(new)
    else:
        parts.extend(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=f'v4.20.37/{name}', tofile=f'v5.0.5/{name}', lineterm=''))

for token in ['MISSION_AGE_LABEL_RETRY_MS', 'MISSION_AGE_LABEL_REFRESH_MS', 'CRITICAL_VIEW_MIN_AGE_MS']:
    parts += ['', '=' * 110, f'CONSTANT {token}']
    for label, source in [('v4.20.37', baseline), ('v5.0.5', current)]:
        match = re.search(rf'(?m)^.*\b{re.escape(token)}\b.*$', source)
        parts.append(f'{label}: {match.group(0).strip() if match else "[missing]"}')

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
