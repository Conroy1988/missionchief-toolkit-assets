#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
CHANGELOG = ROOT / 'CHANGELOG.md'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
TEST = ROOT / '.github/scripts/test_issue464_launcher_settings_contract.py'

text = SOURCE.read_text(encoding='utf-8')
if '// @version      5.0.6' not in text or "version: '5.0.6'" not in text:
    raise SystemExit('Issue #464 performance correction requires Toolkit v5.0.6')

replacements = [
    (
        "runtimeSetTimeout(() => button.focus?.(),0);",
        "button.focus?.();",
        'ARR dropdown focus deferral',
    ),
    (
        "if(settings.arrSearchAutoFocus) runtimeSetTimeout(()=>arrSearch.focus(),0);",
        "if(settings.arrSearchAutoFocus) queueMicrotask(()=>arrSearch.focus());",
        'ARR search autofocus deferral',
    ),
    (
        "if (state.missionAge) { missionOverlayData.clear(); runtimeSetTimeout(() => scheduleMissionAgeRefresh(0), 0); }",
        "if (state.missionAge) { missionOverlayData.clear(); scheduleMissionAgeRefresh(0); }",
        'Mission Age immediate refresh wrapper',
    ),
]
for old, new, label in replacements:
    if text.count(old) != 1:
        raise SystemExit(f'Expected one {label} anchor, found {text.count(old)}')
    text = text.replace(old, new, 1)

SOURCE.write_text(text, encoding='utf-8')
for target in (ROOT / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'MissionChief_Map_Command_Toolkit.txt'):
    target.write_text(text, encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
if len(text.splitlines()) != int(fixture['expectedSourceLines']):
    raise SystemExit('Performance correction unexpectedly changed the source-line ledger')
fixture['candidateSourceSha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

test = TEST.read_text(encoding='utf-8')
anchor = "assert 'inlineMissionDataScanned=captured>0' in text\n"
addition = """assert 'inlineMissionDataScanned=captured>0' in text
assert 'runtimeSetTimeout(() => button.focus?.(),0)' not in block
assert 'button.focus?.();' in block
assert 'if(settings.arrSearchAutoFocus) queueMicrotask(()=>arrSearch.focus());' in call
assert 'runtimeSetTimeout(()=>arrSearch.focus(),0)' not in call
assert 'if (state.missionAge) { missionOverlayData.clear(); scheduleMissionAgeRefresh(0); }' in toggle
assert 'runtimeSetTimeout(() => scheduleMissionAgeRefresh(0), 0)' not in toggle
"""
if anchor not in test:
    raise SystemExit('Issue #464 performance contract anchor is missing')
test = test.replace(anchor, addition, 1)
TEST.write_text(test, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
anchor = '- Restored immediate Mission Age rendering for the button and shortcut `6`, forced fresh late-data scans after early empty pages, rebound labels to replaced maps/markers, prevented duplicates and removed labels cleanly when disabled.\n'
addition = anchor + '- Preserved the established managed-timeout performance budget by removing three redundant scheduling wrappers from ARR focus and Mission Age refresh paths.\n'
if anchor not in changelog:
    raise SystemExit('v5.0.6 changelog anchor is missing')
if 'three redundant scheduling wrappers' not in changelog:
    changelog = changelog.replace(anchor, addition, 1)
CHANGELOG.write_text(changelog, encoding='utf-8')

SELF.unlink(missing_ok=True)
print(json.dumps({
    'version': '5.0.6',
    'sha256': fixture['candidateSourceSha256'],
    'removedRuntimeTimeoutSites': 3,
    'sourceLines': len(text.splitlines()),
}, indent=2))
