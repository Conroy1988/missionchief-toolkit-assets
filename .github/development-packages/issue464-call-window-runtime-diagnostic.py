#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github/diagnostics/issue464-call-window-runtime.txt'
text = SOURCE.read_text(encoding='utf-8')
start = text.index('    // Issue #378 complete operational feature suite.')
end = text.index('    // Issue #378 end complete operational feature suite.', start)
block = text[start:end]


def line_number(offset: int) -> int:
    return text.count('\n', 0, max(offset, 0)) + 1


def brace_end(open_pos: int) -> int:
    depth = 0; quote = None; escaped = False; line = False; comment = False; i = open_pos
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
            if depth == 0: return i
        i += 1
    raise RuntimeError('unclosed function')

matches = list(re.finditer(r'(?m)^\s*function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{', block))
names = [match.group(1) for match in matches]
selected = [name for name in names if any(token in name.lower() for token in ('callwindow', 'arr', 'patient', 'vehiclelist', 'vehiclecounter', 'playercounter', 'selectedvehicle', 'generation'))]
parts = ['ISSUE #464 CALL WINDOW RUNTIME DIAGNOSTIC', 'FUNCTION INVENTORY', '\n'.join(names), '', 'SELECTED RUNTIME FUNCTIONS']
for name in selected:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{', text[start:end])
    if not match: continue
    absolute = start + match.start(); op = text.find('{', absolute, start + match.end()); close = brace_end(op)
    parts += ['\n' + '='*110, f'{name} lines {line_number(absolute)}-{line_number(close)}', text[absolute:close+1]]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(parts) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
