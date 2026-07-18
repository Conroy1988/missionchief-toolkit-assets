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
RUNTIME_TEST = ROOT / '.github' / 'scripts' / 'test_mission_requirements_runtime.js'
CONTRACT_TEST = ROOT / '.github' / 'scripts' / 'test_mission_requirements_contract.py'


def compact_region(text: str, start_marker: str, end_marker: str, label: str, preserve_comment: str | None = None) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        fallback = {
            'patient-aware resolver': '    function missionRequirementsOverallState',
            'patient-aware renderer': '    function missionRequirementsScheduleRecord'
        }.get(label)
        if fallback:
            end = text.find(fallback, start + len(start_marker))
    if start < 0 or end < 0 or end <= start:
        raise AssertionError(f'{label}: region markers not found')
    region = text[start:end]
    parts = []
    for raw in region.splitlines():
        line = raw.strip()
        if not line:
            continue
        if preserve_comment and line == preserve_comment:
            continue
        if line.startswith('//'):
            raise AssertionError(f'{label}: unexpected line comment prevents safe compaction: {line}')
        parts.append(line)
    if not parts:
        raise AssertionError(f'{label}: no code found')
    prefix = f'    {preserve_comment}\n' if preserve_comment else ''
    compacted = prefix + '    ' + ' '.join(parts) + '\n\n'
    return text[:start] + compacted + text[end:]


source = SOURCE.read_text(encoding='utf-8')
source = compact_region(
    source,
    '    // Issue #181: patient-derived ambulance demand.',
    '    function missionRequirementsVehicleType(element) {',
    'patient helper block',
    '// Issue #181: patient-derived ambulance demand.',
)
source = compact_region(
    source,
    '    function missionRequirementsResolve(candidate, parsed, catalogue = null) {',
    '    function missionRequirementsOverallState(rows) {',
    'patient-aware resolver',
)
source = compact_region(
    source,
    '    function missionRequirementsRenderRecord(record) {',
    '    function missionRequirementsScheduleRecord(record) {',
    'patient-aware renderer',
)

line_count = len(source.splitlines())
if line_count > 32000:
    raise AssertionError(f'Compacted source remains above the 32,000-line budget: {line_count}')
if source.count('function missionRequirementsPatientCount(candidate)') != 1:
    raise AssertionError('Patient count parser lost during compaction')
if source.count('function missionRequirementsReconcilePatientDemand(parsed, patientState)') != 1:
    raise AssertionError('Patient reconciliation lost during compaction')
if source.count('function missionRequirementsResolve(candidate, parsed, catalogue = null)') != 1:
    raise AssertionError('Resolver lost during compaction')
if source.count('function missionRequirementsRenderRecord(record)') != 1:
    raise AssertionError('Renderer lost during compaction')

SOURCE.write_text(source, encoding='utf-8')
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
manifest['lines'] = line_count
manifest['metadata']['warnings'] = []
manifest['baselineHashMatch'] = None
manifest['distributionStatus'] = 'dry-run-not-yet-greasyfork-source'
DIST_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

subprocess.run(['node', '--check', str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(['node', str(RUNTIME_TEST)], cwd=ROOT, check=True)
subprocess.run(['python3', str(CONTRACT_TEST)], cwd=ROOT, check=True)
assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
print(f'Issue #181 compacted candidate: {line_count} lines; SHA-256 {digest}')
