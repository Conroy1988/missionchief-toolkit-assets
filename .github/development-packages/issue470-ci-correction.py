#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
MANIFEST = ROOT / 'dist/release-manifest.json'
SUMS = ROOT / 'dist/SHA256SUMS.txt'
HELP = ROOT / 'help/index.html'
TEST = ROOT / '.github/scripts/test_issue470_menu_requirements_runtime.js'

text = SOURCE.read_text(encoding='utf-8')
if '// @version      5.0.7' not in text or "version: '5.0.7'" not in text:
    raise SystemExit('Issue #470 CI correction requires Toolkit v5.0.7')

old_native = "        const nativeRoots = Array.from(doc.querySelectorAll('[id=\"missing_text\"]') || []);"
new_native = "        const missingTextSelector = `[id=${JSON.stringify('missing_text')}]`;\n        const nativeRoots = Array.from(doc.querySelectorAll(missingTextSelector) || []);"
if text.count(old_native) != 1:
    raise SystemExit(f'Issue #470 native selector anchor count changed: {text.count(old_native)}')
text = text.replace(old_native, new_native, 1)

old_group = "            const root = group.closest?.('[id=\"missing_text\"], .alert-missing-vehicles, [data-mission-requirements], [data-missing-requirements], [data-missing-vehicles], .mission-requirements, .mission_requirements, .missing-vehicles, .missing_vehicles') || group.parentElement;"
new_group = "            const root = group.closest?.(`${missingTextSelector}, .alert-missing-vehicles, [data-mission-requirements], [data-missing-requirements], [data-missing-vehicles], .mission-requirements, .mission_requirements, .missing-vehicles, .missing_vehicles`) || group.parentElement;"
if text.count(old_group) != 1:
    raise SystemExit(f'Issue #470 grouped selector anchor count changed: {text.count(old_group)}')
text = text.replace(old_group, new_group, 1)

if text.count('[id="missing_text"]') > 1:
    raise SystemExit('Issue #470 duplicate literal missing_text selector remains')

SOURCE.write_text(text, encoding='utf-8')
for target in (
    ROOT / 'MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'MissionChief_Map_Command_Toolkit.txt',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
):
    target.write_text(text, encoding='utf-8')

source_bytes = text.encode('utf-8')
source_sha = hashlib.sha256(source_bytes).hexdigest()
SUMS.write_text(
    f'{source_sha}  MissionChief_Map_Command_Toolkit.user.js\n'
    f'{source_sha}  MissionChief_Map_Command_Toolkit.txt\n',
    encoding='utf-8',
)

manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
manifest['version'] = '5.0.7'
manifest['sha256'] = source_sha
manifest['bytes'] = len(source_bytes)
manifest['lines'] = text.count('\n') + 1
manifest.setdefault('metadata', {})['runtimeVersion'] = '5.0.7'
manifest['distributionStatus'] = 'dry-run-not-yet-greasyfork-source'
MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
old_issue_lines = sum(int(item.get('lines', 0)) for item in fixture.get('approvedNonStyleChanges', []) if item.get('issue') == 470)
base_without_issue = int(fixture['expectedSourceLines']) - old_issue_lines
source_lines = len(text.splitlines())
changes = [item for item in fixture.get('approvedNonStyleChanges', []) if item.get('issue') != 470]
changes.append({
    'issue': 470,
    'phase': 'frame-safe-command-state-and-mission-scoped-requirement-recovery',
    'lines': source_lines - base_without_issue,
})
fixture['approvedNonStyleChanges'] = changes
fixture['approvedNonStyleSourceLines'] = sum(int(item['lines']) for item in changes)
fixture['expectedSourceLines'] = source_lines
fixture['candidateVersion'] = '5.0.7'
fixture['candidateSourceSha256'] = source_sha
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

help_text = HELP.read_text(encoding='utf-8')
if 'Guide for Toolkit v4.20.37' not in help_text and 'Guide for Toolkit v5.0.7' not in help_text:
    raise SystemExit('Help Centre version anchor changed')
help_text = help_text.replace('Guide for Toolkit v4.20.37', 'Guide for Toolkit v5.0.7')
HELP.write_text(help_text, encoding='utf-8')

runtime_test = TEST.read_text(encoding='utf-8')
anchor = "for (const token of required) if (!source.includes(token)) throw new Error(`Missing Issue #470 contract token: ${token}`);\n"
addition = anchor + "if ((source.match(/\\[id=\\\"missing_text\\\"\\]/gu) || []).length > 1) throw new Error('duplicate literal missing_text selectors returned');\n"
if anchor not in runtime_test:
    raise SystemExit('Issue #470 runtime-test insertion anchor changed')
if 'duplicate literal missing_text selectors returned' not in runtime_test:
    runtime_test = runtime_test.replace(anchor, addition, 1)
TEST.write_text(runtime_test, encoding='utf-8')

SELF.unlink(missing_ok=True)
print(json.dumps({
    'version': '5.0.7',
    'sha256': source_sha,
    'sourceLines': source_lines,
    'manifestLines': manifest['lines'],
    'helpCentreVersion': 'v5.0.7',
}, indent=2))
