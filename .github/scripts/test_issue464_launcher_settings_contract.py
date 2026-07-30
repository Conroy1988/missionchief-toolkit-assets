#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
fixture = json.loads((ROOT / '.github/fixtures/main-style-source-headroom.json').read_text(encoding='utf-8'))
line_limit = fixture['v9Candidate']['maxSourceLines']

def section(start, end):
    first = text.index(start)
    last = text.index(end, first)
    return text[first:last]

control = section('    function createControl(', '    function createPanel(')
assert 'const primaryMap = toolkitPrimaryMapElement(mapEl, document);' in control
ensure = section('    function ensureUi()', '    function mutationBelongsToToolkit')
assert 'return Boolean(control || document.getElementById(SCRIPT.controlId));' in ensure
boot = section('    function boot()', '    function scheduleBoot()')
assert 'installMissionMarkerAddHook' in boot
assert 'installCustomVehicleBadges' in boot
assert 'installOperationalSuiteShell' not in boot
age = section('    function updateMissionAgeLabels()', '    function scheduleMissionAgeRefresh(')
assert 'missionAgeRefreshPlan' in age
metadata = re.search(r'^//\s*@version\s+([^\s]+)', text, re.M).group(1)
runtime = re.search(r"version:\s*'([^']+)'", text).group(1)
assert metadata == runtime
assert tuple(int(part) for part in metadata.split('.')[:3]) >= (8, 0, 0)
assert len(text.splitlines()) <= line_limit
print('Launcher, boot and Mission Age contract passed through v9.')
