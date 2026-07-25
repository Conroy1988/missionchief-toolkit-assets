from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
target=ROOT/'.github/v7-retirement/apply_v7_retirement.py'
s=target.read_text(encoding='utf-8')
old="""PREBOOT = r'''#!/usr/bin/env python3
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');state=re.search(r'(?m)^\\s*(?:const|let|var)\\s+state\\s*=\\s*loadState\\(\\);\\s*$',text);assert state
assert text.index('    function defaultState() {') < state.start();assert text.index('    function normaliseLoadedState(') < state.start();assert 'OPERATIONAL_SUITE_SETTINGS_VERSION' not in text
meta=re.search(r'(?m)^//\\s*@version\\s+([^\\s]+)\\s*$',text).group(1);runtime=re.search(r\"version:\\s*'([^']+)',\",text).group(1);assert meta==runtime=='7.0.0';assert text.rstrip().endswith('})();')
print('v7 preboot state-order contract passed.')'''"""
new="""PREBOOT = r'''#!/usr/bin/env python3
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
declarations=list(re.finditer(r'(?m)^\\s*(?:const|let|var)\\s+state\\s*=\\s*loadState\\(\\);\\s*$',text))
assert len(declarations)==1,declarations
assert text.count('    function defaultState() {')==1
assert text.count('    function normaliseLoadedState(')==1
assert 'OPERATIONAL_SUITE_SETTINGS_VERSION' not in text
assert 'OPERATIONAL_SETTINGS_SCHEMA' not in text
assert 'delete merged.operationalWindow;' in text
assert 'delete merged.missionRequirements;' in text
meta=re.search(r'(?m)^//\\s*@version\\s+([^\\s]+)\\s*$',text).group(1)
runtime=re.search(r\"version:\\s*'([^']+)',\",text).group(1)
assert meta==runtime=='7.0.0'
assert text.rstrip().endswith('})();')
print('v7 preboot hydration contract passed.')'''"""
if s.count(old)!=1: raise SystemExit(f'preboot contract block count {s.count(old)}')
s=s.replace(old,new,1)
target.write_text(s,encoding='utf-8')
for p in [ROOT/'.github/v7-retirement/patch_builder9.py',ROOT/'.github/workflows/patch-v7-builder9.yml']:
    p.unlink(missing_ok=True)
