#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github' / 'diagnostics' / 'issue378-targeted-integration-excerpts.txt'
source = SOURCE.read_text(encoding='utf-8')


def excerpt(marker: str, before: int = 1600, after: int = 9000, limit: int = 8) -> str:
    indexes = [match.start() for match in re.finditer(re.escape(marker), source)]
    chunks = [f'=== {marker!r} matches={len(indexes)} ===\n']
    for number, index in enumerate(indexes[:limit], 1):
        chunks.append(f'\n--- {number} char={index} ---\n')
        chunks.append(source[max(0, index-before):min(len(source), index+after)])
    return ''.join(chunks)

markers = [
    'data-tab="settings"',
    "data-tab='settings'",
    'function createPanel(',
    'function updateUI()',
    'const setting = target.dataset.setting',
    'target.dataset.setting',
    "addEventListener('change'",
    '#mission_list',
    'mission_panel',
    'mission_list',
    'function transportSweepDocumentContexts()',
    'function installOperationalSuiteShell()',
    'installOperationalSuiteShell();',
    'function boot()',
]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('ISSUE378_TARGETED_INTEGRATION_EXCERPTS_V1\n' + '\n'.join(excerpt(marker) for marker in markers), encoding='utf-8')
print('Wrote targeted Issue #378 integration excerpts.')
