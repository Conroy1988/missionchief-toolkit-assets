#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
REPORT = ROOT / 'v8-godfather-architecture.txt'

source = SOURCE.read_text(encoding='utf-8')
lines = source.splitlines()

TERMS = [
    'uiTheme', 'mapCommand', 'cyberpunk', 'fallout4', 'umbrella', 'factorio',
    'bond007', 'hyrule', 'cashout', 'payout', 'flash payout', 'flashPayout',
    'payoutAudio', 'Audio(', 'new Audio', 'raw.githubusercontent.com',
    'themeAsset', 'theme asset', 'data-mcms-ui-theme', 'THEME', 'themeOptions',
]


def blocks_for_term(term: str, radius: int = 12) -> list[str]:
    found: list[str] = []
    lower = term.lower()
    for index, line in enumerate(lines):
        if lower not in line.lower():
            continue
        start = max(0, index - radius)
        end = min(len(lines), index + radius + 1)
        chunk = '\n'.join(f'{i+1:05d}: {lines[i]}' for i in range(start, end))
        found.append(f'--- TERM {term!r} AT LINE {index+1} ---\n{chunk}')
    return found


def function_chunks(pattern: str) -> list[str]:
    matches = list(re.finditer(pattern, source, flags=re.I))
    chunks: list[str] = []
    for match in matches:
        line = source.count('\n', 0, match.start()) + 1
        start = max(0, match.start() - 1800)
        end = min(len(source), match.start() + 6000)
        chunks.append(f'--- FUNCTION PATTERN {pattern!r} AROUND LINE {line} ---\n{source[start:end]}')
    return chunks

parts: list[str] = []
parts.append(f'SOURCE_LINES={len(lines)}\nSOURCE_BYTES={len(source.encode("utf-8"))}')
for term in TERMS:
    chunks = blocks_for_term(term)
    parts.append(f'\n\n######## SEARCH {term!r}: {len(chunks)} MATCHES ########')
    parts.extend(chunks[:35])

for pattern in [
    r'function\s+[^\n]*(?:theme|Theme)[^\n]*\(',
    r'function\s+[^\n]*(?:payout|Payout|cashout|Cashout)[^\n]*\(',
    r'const\s+[^\n]*(?:THEME|Theme|theme)[^\n]*=',
    r'const\s+[^\n]*(?:PAYOUT|Payout|payout|cashout)[^\n]*=',
]:
    parts.append(f'\n\n######## PATTERN {pattern!r} ########')
    parts.extend(function_chunks(pattern)[:60])

# Repository-side supporting files.
for relative in [
    '.github/THEME_ASSET_ARCHITECTURE.md',
    '.github/scripts/test_asset_health.py',
    '.github/scripts/test_main_style_source_headroom.py',
    '.github/scripts/validate_userscript.py',
    '.github/documentation-contract.json',
    'status/theme-asset-inventory.json',
    'status/media-asset-audit.json',
    'docs/site-data.json',
    'help/manifest.json',
]:
    path = ROOT / relative
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8', errors='replace')
    parts.append(f'\n\n######## FILE {relative} ########\n{text}')

manifest_paths = sorted(ROOT.glob('themes/*/manifest.json'))
parts.append('\n\n######## THEME MANIFESTS ########')
for path in manifest_paths:
    parts.append(f'\n--- {path.relative_to(ROOT)} ---\n{path.read_text(encoding="utf-8")}')

REPORT.write_text('\n'.join(parts), encoding='utf-8')
print(f'Wrote {REPORT} ({REPORT.stat().st_size} bytes)')
