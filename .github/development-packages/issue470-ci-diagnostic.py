#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue470-ci-failures.txt'
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'

text = SOURCE.read_text(encoding='utf-8')
lines = text.splitlines()
out: list[str] = [
    'Issue #470 CI failure diagnostic',
    f'source_lines={len(lines)}',
    '',
    '=== SOURCE LINES 22290-22355 ===',
]
for number in range(22290, min(22356, len(lines) + 1)):
    out.append(f'{number:05d}: {lines[number - 1]}')

out.extend(['', '=== missing_text selector occurrences ==='])
for index, line in enumerate(lines, start=1):
    if 'missing_text' in line:
        out.append(f'{index:05d}: {line}')

text_suffixes = {'.md', '.txt', '.html', '.js', '.mjs', '.cjs', '.py', '.json', '.yml', '.yaml'}
patterns = [
    ('help-centre', re.compile(r'help\s+centre', re.I)),
    ('version-5.0.6', re.compile(r'\b(?:v)?5\.0\.6\b', re.I)),
    ('contract-lane', re.compile(r'Contract and syntax lane', re.I)),
    ('documentation-drift', re.compile(r'documentation drift', re.I)),
]
for label, pattern in patterns:
    out.extend(['', f'=== SEARCH {label} ==='])
    matches = 0
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in text_suffixes or '.git' in path.parts:
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        for match in pattern.finditer(content):
            line_number = content.count('\n', 0, match.start()) + 1
            content_lines = content.splitlines()
            start = max(0, line_number - 3)
            end = min(len(content_lines), line_number + 2)
            out.append(f'--- {path.relative_to(ROOT)}:{line_number} ---')
            for offset in range(start, end):
                out.append(f'{offset + 1:05d}: {content_lines[offset]}')
            matches += 1
            if matches >= 80:
                out.append('[search result limit reached]')
                break
        if matches >= 80:
            break
    out.append(f'matches={matches}')

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
