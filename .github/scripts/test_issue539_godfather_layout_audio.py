#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')
EXPECTED_SOURCE_SHA = '773d6686fdcfe0af5901f54bdd58c58cf0ef8503bddaae354f32ed25879ac19b'
EXPECTED_AUDIO_SHA = '53160bd03bacf043ea3b0ffbd202163c2621e16a47ecd0f7090bfeacaf00b0d4'
EXPECTED_AUDIO_BYTES = 136254

assert hashlib.sha256(SOURCE.encode()).hexdigest() == EXPECTED_SOURCE_SHA
assert re.search(r'(?m)^//\s*@version\s+8\.0\.2$', SOURCE)
assert 'godfather-flash-payout.mp3?v=8.0.3' in SOURCE

marker = '/* v8.0.3 — Godfather launcher, dock and payout placement hotfix. */'
start = SOURCE.index(marker)
end = SOURCE.index('/* v7.1.0 Incident Command Wire:', start)
css = SOURCE[start:end]
assert start > SOURCE.rfind('html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn', 0, start)
for token in (
    'width:22px !important;',
    'height:22px !important;',
    'left:-5px !important;',
    'top:-7px !important;',
    'grid-template-columns:109px minmax(0,1fr) !important;',
    'width:52px !important;',
    'height:44px !important;',
    'min-height:44px !important;',
    'top:42% !important;',
    'top:38% !important;',
    'top:34% !important;',
):
    assert token in css, token
assert css.count('height:44px !important;') >= 2
seal = SOURCE[SOURCE.index('.mcms-shell::before', SOURCE.index('/* v8.0.3 — The Godfather')):start]
assert 'pointer-events:none !important;' in seal

audio_path = ROOT / 'themes/godfather/audio/godfather-flash-payout.mp3'
audio = audio_path.read_bytes()
assert len(audio) == EXPECTED_AUDIO_BYTES
assert hashlib.sha256(audio).hexdigest() == EXPECTED_AUDIO_SHA
assert audio[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2') or audio.startswith(b'ID3')

manifest = json.loads((ROOT / 'themes/godfather/manifest.json').read_text(encoding='utf-8'))
assert manifest['toolkitVersion'] == '8.0.3'
assert manifest['audio']['sha256'] == EXPECTED_AUDIO_SHA
assert manifest['audio']['channels'] == 2
assert manifest['audio']['bitRateBps'] == 128000
assert manifest['audio']['byteSize'] == EXPECTED_AUDIO_BYTES

for path in (
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
):
    assert path.read_bytes() == SOURCE_PATH.read_bytes(), path

print('Issue #539 Godfather layout and replacement-audio contract passed.')
