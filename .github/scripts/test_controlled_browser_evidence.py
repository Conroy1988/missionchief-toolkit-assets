#!/usr/bin/env python3
"""Deterministic contracts for the controlled Chrome evidence collector."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLLECTOR = ROOT / '.github/scripts/collect_controlled_browser_evidence.py'
spec = importlib.util.spec_from_file_location('controlled_browser_evidence', COLLECTOR)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

attributes = [f'data-mcms-test-{index}' for index in range(22)]
source = "\n".join([
    '// ==UserScript==',
    '// @version      8.3.2',
    '// ==/UserScript==',
    '    function installMainStyles() {',
    '        addStyle(`.mcms-card { display: block; }\\n.mcms-row { color: red; }`);',
    '    }',
    '    function applyRootAttributes() {',
    '        const root = document.documentElement;',
    *[f"        setAttributeIfChanged(root, '{name}', 'value');" for name in attributes],
    '    }',
    '    function getStrongMarkerSignal() {}',
])

assert module.toolkit_version(source) == '8.3.2'
assert module.extract_main_css(source) == '.mcms-card { display: block; }\\n.mcms-row { color: red; }'
assert module.extract_root_attributes(source) == attributes
assert module.median([1, 2, 8, 10]) == 5.0
assert module.percentile([1, 2, 3, 4, 5], 0.9) == 5

result = {
    'baseline': {
        'version': '8.3.2',
        'sourceSha256': 'a' * 64,
        'sourceBytes': 100,
        'sourceLines': 20,
        'cssBytes': 50,
        'cssRuleEstimate': 2,
        'rootAttributeCount': 22,
    },
    'environment': {'samplesPerViewport': 11},
    'scenarios': [{
        'label': 'desktop',
        'viewport': {'width': 1440, 'height': 900},
        'styleInsertMedianMs': 1.0,
        'styleInsertP90Ms': 2.0,
        'forcedStyleLayoutMedianMs': 3.0,
        'forcedStyleLayoutP90Ms': 4.0,
        'longTasksMs': [],
        'layoutShiftTotal': 0,
        'rootAttributeContract': {
            'attributeCount': 22,
            'initialWrites': 22,
            'unchangedWrites': 0,
            'changedWrites': 1,
            'repairedWrites': 1,
        },
    }],
}
markdown = module.render_markdown(result)
assert '# Controlled Chrome evidence — Toolkit v8.3.2' in markdown
assert 'authenticated MissionChief runtime evidence' in markdown
assert 'does not justify CSS modularisation' in markdown
assert '| desktop | 1440×900 | 1.0000 ms | 2.0000 ms | 3.0000 ms | 4.0000 ms | 0 | 0.000000 | 0 |' in markdown

for malformed in [source.replace('// @version      8.3.2\n', ''), source.replace(attributes[-1], attributes[-2])]:
    failed = False
    try:
        if '@version' not in malformed:
            module.toolkit_version(malformed)
        else:
            module.extract_root_attributes(malformed)
    except ValueError:
        failed = True
    assert failed

production = (ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
assert module.toolkit_version(production) == '8.3.2'
assert len(module.extract_root_attributes(production)) == 22
assert len(module.extract_main_css(production).encode('utf-8')) > 500_000
print('Controlled Chrome evidence collector contracts passed.')
