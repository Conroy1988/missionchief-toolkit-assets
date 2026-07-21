#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / '.github/fixtures/unchanged-render-scenarios-v4.20.24.json'
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
PROFILER = ROOT / 'tools/mcms-performance-profiler.user.js'

def fail(message: str) -> None:
    raise AssertionError(message)

data = json.loads(FIXTURE.read_text(encoding='utf-8'))
source = SOURCE.read_bytes()
source_hash = hashlib.sha256(source).hexdigest()
lines = SOURCE.read_text(encoding='utf-8').count('\n')
base = data['baseline']
if base['sourceSha256'] != source_hash: fail('scenario fixture source hash is stale')
if base['sourceLines'] != lines: fail(f'scenario fixture source lines are stale: {base["sourceLines"]} != {lines}')
if base['instrumentedPaths'] != ['updateUI', 'renderOperationalPanels']: fail('instrumented path contract changed')
profiler = PROFILER.read_text(encoding='utf-8')
if f"// @version      {base['profilerVersion']}" not in profiler: fail('profiler version contract changed')
if f"const SCHEMA_VERSION = {base['profilerSchemaVersion']};" not in profiler: fail('profiler schema contract changed')
scenario_ids = [item['id'] for item in data['scenarios']]
expected = ['idle-map', 'settings-open-close', 'mission-open-close', 'unit-selection', 'map-pan-zoom', 'layout-change']
if scenario_ids != expected: fail('scenario ordering or coverage changed')
if any(item['minimumAttempts'] < 2 for item in data['scenarios']): fail('scenario attempt floor is too low')
if data['privacy'] != {
    'freeTextScenarioLabels': False,
    'missionContent': False,
    'addresses': False,
    'coordinates': False,
    'vehicleOrPersonnelNames': False,
    'fullUrls': False,
}: fail('privacy contract changed')
print('Unchanged-render scenario contracts passed.')
