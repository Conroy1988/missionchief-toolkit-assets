#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-operational-runtime.txt'
text = SOURCE.read_text(encoding='utf-8')


def function_span(name: str) -> tuple[int, int] | None:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\(', text)
    if not match:
        return None
    paren = text.find('(', match.start())
    pdepth = 0; quote = None; escaped = False; line = False; comment = False; i = paren
    body = -1
    while i < len(text):
        ch = text[i]; nxt = text[i+1] if i+1 < len(text) else ''
        if line:
            if ch == '\n': line = False
            i += 1; continue
        if comment:
            if ch == '*' and nxt == '/': comment = False; i += 2
            else: i += 1
            continue
        if quote:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if ch == '/' and nxt == '/': line = True; i += 2; continue
        if ch == '/' and nxt == '*': comment = True; i += 2; continue
        if ch in "'\"`": quote = ch; i += 1; continue
        if ch == '(': pdepth += 1
        elif ch == ')':
            pdepth -= 1
            if pdepth == 0:
                body = text.find('{', i + 1); break
        i += 1
    if body < 0: return None
    depth = 0; quote = None; escaped = False; line = False; comment = False; i = body
    while i < len(text):
        ch = text[i]; nxt = text[i+1] if i+1 < len(text) else ''
        if line:
            if ch == '\n': line = False
            i += 1; continue
        if comment:
            if ch == '*' and nxt == '/': comment = False; i += 2
            else: i += 1
            continue
        if quote:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if ch == '/' and nxt == '/': line = True; i += 2; continue
        if ch == '/' and nxt == '*': comment = True; i += 2; continue
        if ch in "'\"`": quote = ch; i += 1; continue
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: return match.start(), i + 1
        i += 1
    return None

names = [
    'operationalFeatureState','operationalFeatureRemove','operationalFeatureStyle',
    'operationalFeatureBar','operationalPill','operationalCallWindowApply',
    'operationalMissionListRoot','operationalMissionRows','operationalMissionListComputeOrder',
    'operationalMissionListApply','operationalTransportChooseAction','operationalTransportApply',
    'operationalFeatureObservationRoots','operationalFeatureRenderContext','operationalFeatureCleanupContext',
]
parts = ['ISSUE #464 OPERATIONAL RUNTIME DIAGNOSTIC']
for name in names:
    span = function_span(name)
    parts += ['', '=' * 110, name]
    parts.append(text[span[0]:span[1]] if span else '[missing]')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
