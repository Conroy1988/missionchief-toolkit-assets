#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
start = source.index('function missionRequirementsResolve(')
end = source.find('\n    function ', start + 40)
if end < 0:
    end = min(len(source), start + 30000)
body = source[start:end]
formatted = body.replace('; ', ';\n').replace(' { ', ' {\n').replace(' } ', '\n}\n')
output = ROOT / '.github' / 'diagnostics' / 'issue-183-resolver-formatted.txt'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(formatted, encoding='utf-8')
print(output.relative_to(ROOT))
