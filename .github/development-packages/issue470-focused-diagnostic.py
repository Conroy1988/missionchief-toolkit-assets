#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
MENU_OUT = ROOT / '.github/diagnostics/issue470-menu-focus.txt'
REQ_OUT = ROOT / '.github/diagnostics/issue470-requirements-focus.txt'
text = SOURCE.read_text(encoding='utf-8')
lines = text.splitlines()


def line_no(offset: int) -> int:
    return text.count('\n', 0, max(0, offset)) + 1


def function_span(match: re.Match[str]) -> tuple[int, int]:
    paren = text.find('(', match.start())
    pdepth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    body_open = -1
    i = paren
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
        if ch == '(': pdepth += 1
        elif ch == ')':
            pdepth -= 1
            if pdepth == 0:
                body_open = text.find('{', i + 1)
                break
        i += 1
    if body_open < 0:
        raise RuntimeError('function body missing')
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = body_open
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
            if depth == 0:
                return match.start(), i + 1
        i += 1
    raise RuntimeError('unclosed function')


functions: dict[str, tuple[int, int, str]] = {}
for match in re.finditer(r'(?m)^\s*function\s+([A-Za-z_$][\w$]*)\s*\(', text):
    try:
        start, end = function_span(match)
    except Exception:
        continue
    functions[match.group(1)] = (start, end, text[start:end])


def render(title: str, names: list[str], contexts: list[str]) -> str:
    out = [title, f'source_lines={len(lines)}', '']
    used = set()
    for name in names:
        if name not in functions or name in used:
            continue
        used.add(name)
        start, end, body = functions[name]
        out.extend(['=' * 120, f'{name} lines {line_no(start)}-{line_no(end)}', body, ''])
    out.extend(['TOKEN CONTEXTS', ''])
    for token in contexts:
        out.append(f'### {token}')
        found = 0
        for match in re.finditer(re.escape(token), text, re.I):
            ln = line_no(match.start())
            lo = max(1, ln - 4); hi = min(len(lines), ln + 4)
            out.extend(f'{i:05d}: {lines[i-1]}' for i in range(lo, hi + 1))
            out.append('---')
            found += 1
            if found >= 30:
                out.append('[truncated]')
                break
        if found == 0:
            out.append('[not found]')
    return '\n'.join(out) + '\n'

menu_names = [
    'createControl', 'ensureUi', 'updateUI', 'createPanel', 'closePanel', 'togglePanel',
    'applyRootAttributes', 'applyPosition', 'fitControlToMap', 'handleAction',
    'registerBootMaintenanceTasks', 'boot', 'mutationRemovesToolkitUi', 'mutationBelongsToToolkit',
]
menu_dynamic = []
for name, (_, _, body) in functions.items():
    if any(token in body for token in ['mcms-mobile-menu', 'mcms-float-menu', 'mcms-menu-open', 'data-action="menu"', "aria-expanded", 'mcms-control-fallback']):
        menu_dynamic.append(name)
menu_names.extend(sorted(menu_dynamic))
menu_contexts = [
    'mcms-menu-open', 'mcms-mobile-menu', 'mcms-float-menu', 'aria-expanded',
    'settingsPanelActivated', 'mcms-control-fallback', 'data-action="menu"',
    'data-action="toggle', 'classList.toggle', 'createControl(mapEl)',
]

req_names = []
for name, (_, _, body) in functions.items():
    lowered = name.lower()
    if lowered.startswith('operationalrequirements') or any(token in body for token in [
        'Waiting for MissionChief requirement data', '#missing_text', '[id="missing_text"]',
        'data-requirement-type', 'operationalRequirementsSource', 'requirementRoot',
    ]):
        req_names.append(name)
for name in [
    'installOperationalSuiteShell', 'scheduleOperationalSuiteScan', 'operationalSuiteScan',
    'operationalFeatureObservationRoots', 'operationalFeatureRenderContext',
    'operationalFeatureCleanupContext', 'operationalCallWindowApply',
]:
    if name not in req_names:
        req_names.append(name)
req_contexts = [
    'Waiting for MissionChief requirement data', '#missing_text', '[id="missing_text"]',
    'data-requirement-type', 'data-raw-html', 'missing_text', 'requirementRoot',
    'sourceState', 'authoritative', 'mission_vehicle', 'vehicle_show_table',
    'missing vehicles', 'still needed', 'requirement data',
]

MENU_OUT.parent.mkdir(parents=True, exist_ok=True)
MENU_OUT.write_text(render('ISSUE #470 MENU FOCUS', menu_names, menu_contexts), encoding='utf-8')
REQ_OUT.write_text(render('ISSUE #470 REQUIREMENTS FOCUS', sorted(set(req_names)), req_contexts), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(MENU_OUT.relative_to(ROOT))
print(REQ_OUT.relative_to(ROOT))
