#!/usr/bin/env python3
# Owner-reviewed release contract for Issue #541 and Toolkit v8.0.4.
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')
assert hashlib.sha256(SOURCE.encode()).hexdigest() == 'e8673da8a40db757f7a1b1165092e1a22f87581de84ebb9c2bc78ce5e4ceb101'
assert re.search(r'(?m)^//\s*@version\s+8\.0\.4$', SOURCE)
for token in (
    'const PAYOUT_FLASH_STEP_MS = 1000;',
    "merged.uiTheme === 'godfather'",
    'merged.payoutFlash.durationMs = 7000;',
    "nextTheme === 'godfather' && state.payoutFlash.durationMs === 4000",
    "if (godfatherDurationChanged) state.payoutFlash.durationMs = 7000;",
    'step="1" data-setting="payout-duration"',
    'margin-top:-24px !important;',
    'margin-top:-32px !important;',
    'margin-top:-58px !important;',
    '@media (max-height:560px)',
    'min-height:210px !important;',
):
    assert token in SOURCE, token
for legacy in (
    'step="2" data-setting="payout-duration"',
):
    assert legacy not in SOURCE, legacy
for path in (
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
):
    assert path.read_bytes() == SOURCE_PATH.read_bytes(), path
print('Issue #541 Godfather duration and payout-position contract passed.')
