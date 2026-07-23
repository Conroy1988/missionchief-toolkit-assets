#!/usr/bin/env python3
from pathlib import Path
import base64
import re
import zlib

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / '.github/development-packages'
PARTS = sorted(PACKAGES.glob('issue464-complete.payload.*'))
BASE = PACKAGES / 'issue464-launcher-settings-final.py'
if not PARTS:
    raise SystemExit('Issue #464 payload is missing')
if not BASE.exists():
    raise SystemExit('Issue #464 base launcher/settings package is missing')

ROBUST = r'''def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\(', source)
    if not match:
        raise SystemExit(f'Missing function: {name}')
    paren = source.find('(', match.start())
    pdepth = 0
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
        if ch == '(': pdepth += 1
        elif ch == ')':
            pdepth -= 1
            if pdepth == 0:
                body_open = source.find('{', i + 1)
                break
        i += 1
    if body_open < 0:
        raise SystemExit(f'Missing body for function: {name}')
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
            if depth == 0: return match.start(), i + 1
        i += 1
    raise SystemExit(f'Unclosed function: {name}')
'''

def patch(code: str) -> str:
    start = code.find('def function_span(')
    end = code.find('\ndef ', start + 1)
    if start < 0 or end < 0:
        raise SystemExit('Issue #464 function-span patch anchor is missing')
    return code[:start] + ROBUST + code[end + 1:]

BASE.write_text(patch(BASE.read_text(encoding='utf-8')), encoding='utf-8')
code = zlib.decompress(base64.b64decode(''.join(path.read_text(encoding='utf-8') for path in PARTS))).decode('utf-8')
code = patch(code)
exec(compile(code, __file__, 'exec'))
