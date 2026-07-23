#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-ui-lifecycle.txt'
text = SOURCE.read_text(encoding='utf-8')


def line_number(offset: int) -> int:
    return text.count('\n', 0, max(offset, 0)) + 1


def matching_brace(open_pos: int) -> int:
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
            if depth == 0: return i
        i += 1
    raise RuntimeError(f'unclosed brace at line {line_number(open_pos)}')


def function(name: str) -> str:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{', text)
    if not match: return f'[missing {name}]'
    op = text.find('{', match.start(), match.end())
    end = matching_brace(op)
    return f'// lines {line_number(match.start())}-{line_number(end)}\n{text[match.start():end+1]}'


def context(needle: str, before: int = 70, after: int = 130) -> str:
    pos = text.find(needle)
    if pos < 0: return f'[missing context {needle}]'
    lines = text.splitlines()
    center = line_number(pos)
    lo = max(1, center-before); hi = min(len(lines), center+after)
    return f'// lines {lo}-{hi}\n' + '\n'.join(f'{i:05d}: {lines[i-1]}' for i in range(lo, hi+1))

names = [
    'getLargestLeafletMap', 'createControl', 'createPanel', 'updateUI', 'ensureUi',
    'removeOldInstances', 'mutationRemovesToolkitUi', 'connectMainMutationObserver',
    'fitControlToMap', 'schedulePanelPosition', 'positionPanel', 'openPanel', 'closePanel'
]
parts = ['ISSUE #464 UI LIFECYCLE DIAGNOSTIC', f'bytes={len(text.encode())}', f'lines={len(text.splitlines())}']
for name in names:
    parts += ['\n' + '='*110, f'FUNCTION {name}', function(name)]
for needle in [
    'const SCRIPT =', '#${SCRIPT.controlId}', 'mcms-map-control', 'mcms-command',
    'settingsPanelActivated', 'data-mcms-command-bar-open', 'function installMainStyles'
]:
    parts += ['\n' + '='*110, f'CONTEXT {needle}', context(needle)]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
