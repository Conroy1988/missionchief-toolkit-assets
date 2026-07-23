#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue470-runtime.txt'
text = SOURCE.read_text(encoding='utf-8')
lines = text.splitlines()


def line_no(offset: int) -> int:
    return text.count('\n', 0, max(0, offset)) + 1


def function_span(source: str, match: re.Match[str]) -> tuple[int, int]:
    paren = source.find('(', match.start())
    if paren < 0:
        raise RuntimeError('missing parameter list')
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    body_open = -1
    i = paren
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
        if ch == '(': depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                body_open = source.find('{', i + 1)
                break
        i += 1
    if body_open < 0:
        raise RuntimeError('missing body')
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = body_open
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
    raise RuntimeError('unclosed function')


function_matches = list(re.finditer(r'(?m)^\s*function\s+([A-Za-z_$][\w$]*)\s*\(', text))
functions: dict[str, tuple[int, int, str]] = {}
for match in function_matches:
    name = match.group(1)
    try:
        start, end = function_span(text, match)
    except Exception:
        continue
    functions[name] = (start, end, text[start:end])

menu_tokens = (
    'createControl', 'ensureUi', 'updateUI', 'togglePanel', 'toggleMenu', 'toggleCommand',
    'closePanel', 'openPanel', 'settingsPanelActivated', 'controlId', 'menu-open',
    'command', 'expanded', 'collapsed', 'aria-expanded', 'mcms-menu', 'mcms-float',
)
req_tokens = (
    'operationalRequirements', 'requirementSource', 'missing_text', 'data-requirement-type',
    'requirementsSource', 'requirementsInput', 'operationalFeatureObservationRoots',
    'operationalFeatureRenderContext', 'scheduleOperationalSuiteScan', 'operationalSuiteScan',
)

selected_names: list[str] = []
for name, (_, _, body) in functions.items():
    lowered = body.lower()
    if any(token.lower() in lowered or token.lower() in name.lower() for token in menu_tokens + req_tokens):
        selected_names.append(name)

# Prefer high-value functions first, then include all matching functions.
priority = [
    'createControl', 'ensureUi', 'updateUI', 'togglePanel', 'closePanel', 'createPanel',
    'applyMapVisibilityToggleEffects', 'boot', 'registerBootMaintenanceTasks',
    'operationalRequirementsSourceCandidates', 'operationalRequirementsSourceState',
    'operationalRequirementsInput', 'operationalRequirementsScan', 'operationalRequirementsRender',
    'operationalFeatureObservationRoots', 'operationalFeatureRenderContext',
    'scheduleOperationalSuiteScan', 'operationalSuiteScan',
]
ordered = []
for name in priority + sorted(selected_names):
    if name in functions and name not in ordered:
        ordered.append(name)

parts = [
    'ISSUE #470 RUNTIME DIAGNOSTIC',
    f'version={re.search(r"^//\\s*@version\\s+([^\\s]+)", text, re.M).group(1)}',
    f'source_lines={len(lines)}',
    '',
    'FUNCTION INVENTORY',
    '\n'.join(sorted(functions)),
    '',
    'MENU / REQUIREMENTS TOKEN LOCATIONS',
]

for pattern in [
    r'mcms-[^\s\"\'`]*(?:menu|command|control|float)[^\s\"\'`]*',
    r'settingsPanelActivated', r'aria-expanded', r'#missing_text', r'\[id=["\']missing_text',
    r'data-requirement-type', r'Waiting for MissionChief requirement data',
    r'operationalRequirements[A-Za-z0-9_$]*', r'operationalWindow[A-Za-z0-9_$]*',
]:
    parts.append(f'\nPATTERN {pattern}')
    seen = set()
    for match in re.finditer(pattern, text, re.I):
        ln = line_no(match.start())
        if ln in seen: continue
        seen.add(ln)
        lo = max(1, ln - 1); hi = min(len(lines), ln + 1)
        parts.extend(f'{i:05d}: {lines[i-1]}' for i in range(lo, hi + 1))
        if len(seen) >= 80:
            parts.append('[truncated]')
            break

parts.extend(['', 'SELECTED FUNCTIONS'])
for name in ordered:
    start, end, body = functions[name]
    parts.extend([
        '', '=' * 120,
        f'{name} lines {line_no(start)}-{line_no(end)}',
        body,
    ])

# Include broad contexts around all native requirement selectors even when they live in arrow functions.
parts.extend(['', 'NATIVE REQUIREMENT SELECTOR CONTEXTS'])
for needle in ['missing_text', 'data-requirement-type', 'requirement-type', 'mission_vehicle', 'vehicle_show_table', 'requirements']:
    parts.append(f'\nNEEDLE {needle}')
    positions = [m.start() for m in re.finditer(re.escape(needle), text, re.I)]
    for pos in positions[:40]:
        ln = line_no(pos)
        lo = max(1, ln - 3); hi = min(len(lines), ln + 3)
        parts.extend(f'{i:05d}: {lines[i-1]}' for i in range(lo, hi + 1))
        parts.append('---')

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
