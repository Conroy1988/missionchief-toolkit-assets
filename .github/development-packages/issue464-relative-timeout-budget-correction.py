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
    raise SystemExit('Issue #464 relative-budget correction requires Toolkit v5.0.6')

# Immediate Mission Age rendering already schedules the canonical refresh, and the
# retained 1,000 ms retry covers late MissionChief marker/timestamp population. The
# intermediate 250 ms timeout was redundant and caused a relative performance failure.
pattern = r'runtimeSetTimeout\s*\(\s*\(\)\s*=>\s*\{\s*if\s*\(\s*state\.missionAge\s*\)\s*scheduleMissionAgeRefresh\(0\)\s*;\s*\}\s*,\s*250\s*\)\s*;'
text, count = re.subn(pattern, '', text, count=1)
if count != 1:
    raise SystemExit(f'Expected one 250 ms Mission Age retry, found {count}')

runtime_timeout_sites = (
    len(re.findall(r'runtimeSetTimeout\s*\(', text))
    - len(re.findall(r'function\s+runtimeSetTimeout\s*\(', text))
)
if runtime_timeout_sites > 98:
    raise SystemExit(f'Managed runtime timeout call sites remain above released baseline 98: {runtime_timeout_sites}')

SOURCE.write_text(text, encoding='utf-8')
for target in (ROOT / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'MissionChief_Map_Command_Toolkit.txt'):
    target.write_text(text, encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
if len(text.splitlines()) != int(fixture['expectedSourceLines']):
    raise SystemExit('Relative-budget correction unexpectedly changed source-line count')
fixture['candidateSourceSha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

test = TEST.read_text(encoding='utf-8')
old = '''assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},250)" in text
assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},1000)" in text
runtime_timeout_sites = len(re.findall(r'runtimeSetTimeout\\s*\\(', text)) - len(re.findall(r'function\\s+runtimeSetTimeout\\s*\\(', text))
assert runtime_timeout_sites <= 99
'''
new = '''assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},250)" not in text
assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},1000)" in text
runtime_timeout_sites = len(re.findall(r'runtimeSetTimeout\\s*\\(', text)) - len(re.findall(r'function\\s+runtimeSetTimeout\\s*\\(', text))
assert runtime_timeout_sites <= 98
'''
if old not in test:
    raise SystemExit('Issue #464 timeout-budget contract anchor changed')
TEST.write_text(test.replace(old, new, 1), encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
old = '- Preserved the established managed-timeout performance budget by moving ARR autofocus onto microtasks while retaining Mission Age late-data recovery retries.\n'
new = '- Preserved the established managed-timeout performance budget by moving ARR autofocus onto microtasks and retaining one 1,000 ms Mission Age late-data recovery retry.\n'
if old not in changelog:
    raise SystemExit('v5.0.6 performance changelog anchor changed')
CHANGELOG.write_text(changelog.replace(old, new, 1), encoding='utf-8')

SELF.unlink(missing_ok=True)
print(json.dumps({
    'version': '5.0.6',
    'sha256': fixture['candidateSourceSha256'],
    'runtimeTimeoutCallSites': runtime_timeout_sites,
    'removedRetry': '250ms Mission Age',
    'retainedRetry': '1000ms Mission Age',
    'sourceLines': len(text.splitlines()),
}, indent=2))
