#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')

def function_block(name: str, next_name: str) -> str:
    start_token = f'    function {name}'
    end_token = f'    function {next_name}'
    start = source.find(start_token)
    end = source.find(end_token, start + len(start_token))
    if start < 0 or end < 0:
        raise AssertionError(f'missing diagnostic boundary: {name} -> {next_name}')
    return source[start:end].rstrip()

parts = [
    function_block('missionRequirementsRemoveRecord(source)', 'missionRequirementsEnsureRecord(candidate, source)'),
    function_block('missionRequirementsEnsureRecord(candidate, source)', 'scanMissionRequirementsWindows()'),
]
report = 'Issue #146 Mission Requirements ownership diagnostic\n\n' + '\n\n---\n\n'.join(parts) + '\n'
path = ROOT / '.github' / 'diagnostics' / 'issue-146-mission-requirements-ownership.txt'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(report, encoding='utf-8')
print('Issue #146 ownership diagnostic written')
