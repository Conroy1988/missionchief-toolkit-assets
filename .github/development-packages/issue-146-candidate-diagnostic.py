#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
parts=[]
for symbol in ('missionRequirementsCandidateFromSource', 'missionRequirementsSourceForCandidate', 'missionRequirementsWindowCandidates', 'transportSweepDocumentContexts'):
    index=source.find(symbol)
    start=max(0,index-1800) if index >= 0 else 0
    end=min(len(source),index+10000) if index >= 0 else 0
    parts.append(f'### {symbol} at byte {index}\n\n'+(source[start:end] if index >= 0 else 'NOT FOUND'))
path=ROOT/'.github/diagnostics/issue-146-mission-requirements-candidates.txt'
path.write_text('Issue #146 candidate diagnostic\n\n'+'\n\n---\n\n'.join(parts)+'\n',encoding='utf-8')
print('Issue #146 candidate diagnostic written')
