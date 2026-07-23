#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github' / 'diagnostics' / 'issue378-suite-integration-map.txt'
source = SOURCE.read_text(encoding='utf-8')

TERMS = [
    'data-setting', 'data-action', 'function updateUI(', 'function renderSettings',
    'missionRequirements', 'operationalWindow', 'settings-grid', 'settings-section',
    '#mission_list', 'mission_panel', 'mission_list', 'missionMarker', 'mission_share',
    'alliance_event', 'transportSweepDocumentContexts', 'patient_button', 'patient',
    'prisoner', 'gefangener', 'vehicle_prisoner_select', 'vehicle_patient_select',
    '#vehicle_show_table_body_all', '#mission_vehicle_driving', 'aao', 'arr',
    'alarm', 'generation', 'remaining', 'playerCounter', 'vehicleCounter',
]


def window(index: int, before: int = 850, after: int = 2500) -> str:
    return source[max(0, index-before):min(len(source), index+after)]

parts = ['ISSUE378_SUITE_INTEGRATION_MAP_V1\n', f'source_lines={len(source.splitlines())}\n']
for term in TERMS:
    indexes = [m.start() for m in re.finditer(re.escape(term), source, re.IGNORECASE)]
    parts.append(f'\n=== TERM {term!r} matches={len(indexes)} ===\n')
    for number, index in enumerate(indexes[:10], 1):
        parts.append(f'\n--- {number} char={index} ---\n')
        parts.append(window(index))

symbols = sorted(set(re.findall(r'^\s*(?:async\s+)?function\s+([A-Za-z_$][\w$]*)', source, re.MULTILINE)))
selected = [name for name in symbols if any(token in name.lower() for token in (
    'setting', 'mission', 'patient', 'prison', 'transport', 'vehicle', 'alarm', 'arr', 'call', 'list'
))]
parts.append('\n=== RELEVANT FUNCTION SYMBOLS ===\n' + '\n'.join(selected) + '\n')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(''.join(parts), encoding='utf-8')
print(f'Wrote Issue #378 suite integration map with {len(selected)} relevant symbols.')
