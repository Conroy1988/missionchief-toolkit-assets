#!/usr/bin/env python3
from pathlib import Path
import base64
import re
import zlib

ROOT = Path(__file__).resolve().parents[2]
PARTS = sorted((ROOT / '.github/development-packages').glob('issue464-complete.payload.*'))
if not PARTS:
    raise SystemExit('Issue #464 payload is missing')
code = zlib.decompress(base64.b64decode(''.join(path.read_text(encoding='utf-8') for path in PARTS))).decode('utf-8')
start = code.find('def function_span(')
end = code.find('\ndef ', start + 1)
if start < 0 or end < 0:
    raise SystemExit('Issue #464 function-span patch anchor is missing')
robust = r'''def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\(', source)
    if not match:
        raise SystemExit(f'Missing function: {name}')
    paren = source.find('(', match.start())
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    index = paren
    body_open = -1
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ''
        if line_comment:
            if char == '\n':
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == '*' and nxt == '/':
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == '/' and nxt == '/':
            line_comment = True
            index += 2
            continue
        if char == '/' and nxt == '*':
            block_comment = True
            index += 2
            continue
        if char in "'\"`":
            quote = char
            index += 1
            continue
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                body_open = source.find('{', index + 1)
                break
        index += 1
    if body_open < 0:
        raise SystemExit(f'Missing function body: {name}')
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    index = body_open
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ''
        if line_comment:
            if char == '\n':
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == '*' and nxt == '/':
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == '/' and nxt == '/':
            line_comment = True
            index += 2
            continue
        if char == '/' and nxt == '*':
            block_comment = True
            index += 2
            continue
        if char in "'\"`":
            quote = char
            index += 1
            continue
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return match.start(), index + 1
        index += 1
    raise SystemExit(f'Unclosed function: {name}')
'''
code = code[:start] + robust + code[end + 1:]
exec(compile(code, __file__, 'exec'))
