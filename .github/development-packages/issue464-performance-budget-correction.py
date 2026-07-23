#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
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

# The v5.0.6 call-window renderer added separate zero-delay timeout sites for
# dropdown and text-search autofocus. Microtasks retain post-mount focus without
# increasing the managed runtime timeout budget. Mission Age's two deliberate
# late-data retries remain intact.
replacements = [
    (
        r'if\s*\(\s*settings\.arrSearchAutoFocus\s*\)\s*runtimeSetTimeout\s*\(\s*\(\)\s*=>\s*select\.focus\(\)\s*,\s*0\s*\)\s*;',
        'if(settings.arrSearchAutoFocus)queueMicrotask(()=>select.focus());',
        'ARR dropdown autofocus timeout',
    ),
    (
        r'if\s*\(\s*settings\.arrSearchAutoFocus\s*\)\s*runtimeSetTimeout\s*\(\s*\(\)\s*=>\s*input\.focus\(\)\s*,\s*0\s*\)\s*;',
        'if(settings.arrSearchAutoFocus)queueMicrotask(()=>input.focus());',
        'ARR text-search autofocus timeout',
    ),
]
for pattern, replacement, label in replacements:
    text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise SystemExit(f'Expected one {label} anchor, found {count}')

runtime_timeout_sites = (
    len(re.findall(r'runtimeSetTimeout\s*\(', text))
    - len(re.findall(r'function\s+runtimeSetTimeout\s*\(', text))
)
if runtime_timeout_sites > 99:
    raise SystemExit(f'Managed runtime timeout call-site budget remains above 99: {runtime_timeout_sites}')

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
assert 'if(settings.arrSearchAutoFocus)queueMicrotask(()=>select.focus());' in call
assert 'if(settings.arrSearchAutoFocus)queueMicrotask(()=>input.focus());' in call
assert not re.search(r'arrSearchAutoFocus\\s*\\)\\s*runtimeSetTimeout', call)
assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},250)" in visibility
assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},1000)" in visibility
runtime_timeout_sites = len(re.findall(r'runtimeSetTimeout\\s*\\(', text)) - len(re.findall(r'function\\s+runtimeSetTimeout\\s*\\(', text))
assert runtime_timeout_sites <= 99
"""
if anchor not in test:
    raise SystemExit('Issue #464 performance contract anchor is missing')
test = test.replace(anchor, addition, 1)
TEST.write_text(test, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
anchor = '- Completed the runtime mapping for Extended Call Window and Extended Mission List controls, including ARR counters/search/highlighting, patient and vehicle summaries, structured categories/icons/keywords, sharing gates, sorting and configured badge colours.\n'
addition = anchor + '- Preserved the established managed-timeout performance budget by moving ARR autofocus onto microtasks while retaining Mission Age late-data recovery retries.\n'
if anchor not in changelog:
    raise SystemExit('v5.0.6 changelog anchor is missing')
if 'moving ARR autofocus onto microtasks' not in changelog:
    changelog = changelog.replace(anchor, addition, 1)
CHANGELOG.write_text(changelog, encoding='utf-8')

for disposable in [
    ROOT / '.github/diagnostics/issue464-performance-correction-traceback.txt',
    ROOT / '.github/diagnostics/issue464-performance-correction-v2-traceback.txt',
    ROOT / '.github/diagnostics/issue464-timeout-contexts.txt',
    ROOT / '.github/development-packages/issue464-performance-correction-traceback.py',
    ROOT / '.github/development-packages/issue464-performance-correction-v2-traceback.py',
    ROOT / '.github/development-packages/issue464-timeout-context-diagnostic.py',
]:
    disposable.unlink(missing_ok=True)

SELF.unlink(missing_ok=True)
print(json.dumps({
    'version': '5.0.6',
    'sha256': fixture['candidateSourceSha256'],
    'runtimeTimeoutCallSites': runtime_timeout_sites,
    'removedRuntimeTimeoutSites': 2,
    'missionAgeRetriesPreserved': True,
    'sourceLines': len(text.splitlines()),
}, indent=2))
