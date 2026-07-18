#!/usr/bin/env python3
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
patterns = [
    r"function missionRequirementsEnsureRecord\(candidate, source\) \{[\s\S]*?\n    \}\n\n    function scanMissionRequirementsWindows",
    r"function missionRequirementsRemoveRecord\(source\) \{[\s\S]*?\n    \}\n\n    function missionRequirementsEnsureRecord",
]
parts=[]
for pattern in patterns:
    match=re.search(pattern, source)
    if not match:
        raise AssertionError(f'missing diagnostic anchor: {pattern[:60]}')
    parts.append(match.group(0)[:12000])
report='Issue #146 Mission Requirements ownership diagnostic\n\n'+'\n\n---\n\n'.join(parts)+'\n'
(ROOT / '.github' / 'diagnostics' / 'issue-146-mission-requirements-ownership.txt').parent.mkdir(parents=True, exist_ok=True)
(ROOT / '.github' / 'diagnostics' / 'issue-146-mission-requirements-ownership.txt').write_text(report, encoding='utf-8')
print('Issue #146 ownership diagnostic written')
