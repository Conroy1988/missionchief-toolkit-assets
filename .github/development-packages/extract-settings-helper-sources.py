#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github' / 'development-analysis' / 'settings-helper-sources.txt'
NAMES = ['getLegacyTheme', 'getLegacyPosition', 'normaliseUiTheme', 'normaliseTheme', 'clamp', 'normalisePayoutFlashDuration', 'sanitiseBookmarkShortLabel']


def mask_non_code(source: str) -> str:
    chars = list(source)
    i = 0
    state = 'code'
    quote = ''
    while i < len(chars):
        c = chars[i]
        n = chars[i + 1] if i + 1 < len(chars) else ''
        if state == 'code':
            if c == '/' and n == '/':
                chars[i] = chars[i + 1] = ' '
                i += 2
                state = 'line'
                continue
            if c == '/' and n == '*':
                chars[i] = chars[i + 1] = ' '
                i += 2
                state = 'block'
                continue
            if c in ('"', "'", '`'):
                quote = c
                i += 1
                state = 'string'
                continue
        elif state == 'line':
            if c == '\n': state = 'code'
            else: chars[i] = ' '
            i += 1
            continue
        elif state == 'block':
            if c == '*' and n == '/':
                chars[i] = chars[i + 1] = ' '
                i += 2
                state = 'code'
                continue
            if c != '\n': chars[i] = ' '
            i += 1
            continue
        elif state == 'string':
            if c == '\\':
                if c != '\n': chars[i] = ' '
                if i + 1 < len(chars) and chars[i + 1] != '\n': chars[i + 1] = ' '
                i += 2
                continue
            if c == quote:
                i += 1
                state = 'code'
                continue
            if c != '\n': chars[i] = ' '
            i += 1
            continue
        i += 1
    return ''.join(chars)


def close_brace(masked: str, start: int) -> int:
    depth = 0
    for i in range(start, len(masked)):
        if masked[i] == '{': depth += 1
        elif masked[i] == '}':
            depth -= 1
            if depth == 0: return i
    raise RuntimeError('unbalanced')

source = SOURCE.read_text(encoding='utf-8')
masked = mask_non_code(source)
parts = []
for name in NAMES:
    match = re.search(rf'\bfunction\s+{re.escape(name)}\s*\(', masked)
    if not match:
        parts.append(f'===== {name}: NOT FOUND =====')
        continue
    opening = masked.find('{', match.start())
    closing = close_brace(masked, opening)
    parts.append(f'===== {name} =====\n{source[match.start():closing + 1]}')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n\n'.join(parts) + '\n', encoding='utf-8')
