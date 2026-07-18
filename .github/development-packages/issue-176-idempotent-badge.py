#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_USER = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_TEXT = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'
DIST_SUMS = ROOT / 'dist' / 'SHA256SUMS.txt'
DIST_MANIFEST = ROOT / 'dist' / 'release-manifest.json'
RUNTIME = ROOT / '.github' / 'scripts' / 'test_custom_vehicle_badges_runtime.js'
CONTRACT = ROOT / '.github' / 'scripts' / 'test_custom_vehicle_badges_contract.py'
MISSION_CONTRACT = ROOT / '.github' / 'scripts' / 'test_mission_requirements_contract.py'
SETTINGS_CONTRACT = ROOT / '.github' / 'scripts' / 'test_settings_ui_contract.py'
CHANGELOG = ROOT / 'CHANGELOG.md'
DOC = ROOT / 'docs' / 'issue-176-custom-vehicle-badges-contract.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f'{label}: expected one match, found {count}')
    return text.replace(old, new, 1)

source = SOURCE.read_text(encoding='utf-8')
source = replace_once(
    source,
    '        host.appendChild(badge);\n        row.dataset.mcmsCustomVehicleCategory = classification.category;',
    '        if (badge.parentElement !== host) host.appendChild(badge);\n        row.dataset.mcmsCustomVehicleCategory = classification.category;',
    'idempotent badge placement',
)
SOURCE.write_text(source, encoding='utf-8')

runtime = RUNTIME.read_text(encoding='utf-8')
runtime = replace_once(
    runtime,
    '        this.isConnected = true;\n    }',
    '        this.isConnected = true;\n        this.appendCount = 0;\n    }',
    'fake element append counter state',
)
runtime = replace_once(
    runtime,
    '    appendChild(child) {\n        if (child.parentElement) child.parentElement.children = child.parentElement.children.filter(item => item !== child);',
    '    appendChild(child) {\n        this.appendCount += 1;\n        if (child.parentElement) child.parentElement.children = child.parentElement.children.filter(item => item !== child);',
    'fake element append counter increment',
)
runtime = replace_once(
    runtime,
    'assert.equal(badge.parentElement, specialist.label, "badge was not placed beside the native label");\n\nbadge = api.applyRow(specialist.row);',
    'assert.equal(badge.parentElement, specialist.label, "badge was not placed beside the native label");\nconst specialistHostAppendCount = specialist.label.appendCount;\n\nbadge = api.applyRow(specialist.row);',
    'capture first badge insertion count',
)
runtime = replace_once(
    runtime,
    'assert.equal(badge.textContent, "[Railway Police Officer]");\n\npersonalVehicleApiCache.set("102",',
    'assert.equal(badge.textContent, "[Railway Police Officer]");\nassert.equal(specialist.label.appendCount, specialistHostAppendCount, "repeat scan reinserted an already placed badge");\n\npersonalVehicleApiCache.set("102",',
    'assert no repeat badge insertion',
)
RUNTIME.write_text(runtime, encoding='utf-8')

contract = CONTRACT.read_text(encoding='utf-8')
contract = replace_once(
    contract,
    '        "function customVehicleBadgeApplyRow(row)",\n        "data-mcms-custom-vehicle-category",',
    '        "function customVehicleBadgeApplyRow(row)",\n        "if (badge.parentElement !== host) host.appendChild(badge)",\n        "data-mcms-custom-vehicle-category",',
    'idempotent placement contract marker',
)
CONTRACT.write_text(contract, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
changelog = replace_once(
    changelog,
    '- Reapplies badges after MissionChief or LSSM replaces, filters or sorts the Available Units DOM, without duplicates or dispatch-side effects.',
    '- Reapplies badges after MissionChief or LSSM replaces, filters or sorts the Available Units DOM, without duplicates, repeat DOM insertion or dispatch-side effects.',
    'changelog idempotence note',
)
CHANGELOG.write_text(changelog, encoding='utf-8')

doc = DOC.read_text(encoding='utf-8')
doc = replace_once(
    doc,
    'Repeated scans are idempotent and replacement rows receive the badge automatically.',
    'Repeated scans are idempotent, do not reinsert an already correctly hosted badge, and replacement rows receive the badge automatically.',
    'documentation idempotence contract',
)
DOC.write_text(doc, encoding='utf-8')

DIST_USER.write_text(source, encoding='utf-8')
DIST_TEXT.write_text(source, encoding='utf-8')
digest = hashlib.sha256(source.encode('utf-8')).hexdigest()
DIST_SUMS.write_text(
    f'{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n',
    encoding='utf-8',
)
manifest = json.loads(DIST_MANIFEST.read_text(encoding='utf-8'))
manifest['sha256'] = digest
manifest['bytes'] = len(source.encode('utf-8'))
manifest['lines'] = len(source.splitlines())
manifest['metadata']['warnings'] = []
manifest['baselineHashMatch'] = None
manifest['distributionStatus'] = 'dry-run-not-yet-greasyfork-source'
DIST_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

subprocess.run(['node', '--check', str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(['node', str(RUNTIME)], cwd=ROOT, check=True)
subprocess.run(['python3', str(CONTRACT)], cwd=ROOT, check=True)
subprocess.run(['python3', str(MISSION_CONTRACT)], cwd=ROOT, check=True)
subprocess.run(['python3', str(SETTINGS_CONTRACT)], cwd=ROOT, check=True)
assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
print(f'Issue #176 idempotent v4.17.0 candidate SHA-256: {digest}')
