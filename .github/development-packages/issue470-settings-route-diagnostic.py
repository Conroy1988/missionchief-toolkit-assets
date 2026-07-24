#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
FIXTURE = ROOT / '.github/fixtures/settings-ui-contract.json'
OUTPUT = ROOT / '.github/diagnostics/issue470-settings-route-diagnostic.json'

source = SOURCE.read_text(encoding='utf-8')
fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
start = source.index('    function applyMapVisibilityToggleEffects(')
end = source.index('    function handleMissionWindowToggle(', start)
block = source[start:end]
actual = sorted(set(re.findall(r"feature\s*===\s*['\"]([^'\"]+)['\"]", block)))
expected = sorted(fixture.get('extractedToggleEffectRoutes', []))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps({
    'actual': actual,
    'expected': expected,
    'added': sorted(set(actual) - set(expected)),
    'removed': sorted(set(expected) - set(actual)),
    'function': block,
}, indent=2) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(json.dumps({'actual': actual, 'expected': expected}, indent=2))
