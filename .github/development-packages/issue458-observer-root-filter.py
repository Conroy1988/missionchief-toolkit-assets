#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
TEST = ROOT / '.github/scripts/test_issue458_requirements_source_runtime.js'
text = SOURCE.read_text(encoding='utf-8')
old = "].filter(root => root?.isConnected !== false)));"
new = "].filter(root => root && root.isConnected !== false)));"
if text.count(old) != 1:
    raise SystemExit(f'Expected one unsafe observer root filter, found {text.count(old)}')
text = text.replace(old, new, 1)
SOURCE.write_text(text, encoding='utf-8')
for target in (ROOT / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'MissionChief_Map_Command_Toolkit.txt'):
    target.write_text(text, encoding='utf-8')
test = TEST.read_text(encoding='utf-8')
anchor = "if(!source.includes('context.boundRequirementSource === sourceFingerprint'))throw new Error('observer source-rebind contract is missing');\n"
if anchor not in test:
    raise SystemExit('Issue #458 observer fixture anchor is missing')
test = test.replace(anchor, anchor + "if(!source.includes('filter(root => root && root.isConnected !== false)'))throw new Error('observer root filter admits null candidates');\n", 1)
TEST.write_text(test, encoding='utf-8')
fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
fixture['candidateSourceSha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
print(fixture['candidateSourceSha256'])
