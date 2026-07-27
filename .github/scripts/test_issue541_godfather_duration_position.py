#!/usr/bin/env python3
# Owner-reviewed Issue #541 release contract from Toolkit v8.0.4 onward.
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', value)
    assert match, value
    return tuple(map(int, match.groups()))


metadata = re.search(r'(?m)^//\s*@version\s+([^\s]+)$', SOURCE)
runtime = re.search(r"version:\s*'([^']+)'", SOURCE)
assert metadata and runtime
current_version = metadata.group(1)
assert current_version == runtime.group(1)
assert version_tuple(current_version) >= (8, 0, 4)
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
print(f'Issue #541 Godfather duration and payout-position contract passed for Toolkit {current_version}.')
