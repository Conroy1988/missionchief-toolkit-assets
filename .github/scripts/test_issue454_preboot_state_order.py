#!/usr/bin/env python3
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
declarations=list(re.finditer(r'(?m)^\s*let\s+state\s*;\s*$',text))
hydrations=list(re.finditer(r'(?m)^\s*state\s*=\s*loadState\(\);\s*$',text))
assert len(declarations)==1,declarations
assert len(hydrations)==1,hydrations
assert declarations[0].start() < text.index('    const COMMAND_SECTION_ORDER')
assert hydrations[0].start() > text.index('    const LEGACY_COMMAND_SECTION_MAP')
assert hydrations[0].start() < text.index('    function defaultState() {')
assert text.count('    function defaultState() {')==1
assert text.count('    function normaliseLoadedState(')==1
assert 'OPERATIONAL_SUITE_SETTINGS_VERSION' not in text
assert 'OPERATIONAL_SETTINGS_SCHEMA' not in text
assert 'delete merged.operationalWindow;' in text
assert 'delete merged.missionRequirements;' in text
meta=re.search(r'(?m)^//\s*@version\s+([^\s]+)\s*$',text).group(1)
runtime=re.search(r"version:\s*'([^']+)',",text).group(1)
assert meta==runtime
assert tuple(int(part) for part in meta.split('.')[:3]) >= (7,0,0)
assert text.rstrip().endswith('})();')
print('v7 preboot hydration contract passed.')
