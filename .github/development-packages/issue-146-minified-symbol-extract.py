#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
SOURCE_COMMIT = 'acfe99350657a3a749344ac9bb18138428597fb4'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-final.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-final-package.symbol.payload.py'
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-146-minified-symbols.txt'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
TEMP.write_text(payload, encoding='utf-8')
result = subprocess.run([sys.executable, str(TEMP)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
source = SOURCE.read_text(encoding='utf-8')
parts = []
for symbol in ('missionRequirementsPrimaryRuntime', 'missionRequirementsMissionIdentity', 'missionRequirementsHostPanels', 'missionRequirementsCanonicalPanel', 'missionRequirementsEnsureRecord'):
    index = source.find(symbol)
    if index < 0:
        parts.append(f'{symbol}: NOT FOUND')
        continue
    parts.append(f'### {symbol} at byte {index}\n\n{source[max(0,index-200):min(len(source),index+5000)]}')
subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
TEMP.unlink(missing_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    'Issue #146 minified symbol windows\n'
    '=================================\n\n'
    f'Package return code: {result.returncode}\n\n'
    + '\n\n---\n\n'.join(parts)
    + '\n',
    encoding='utf-8',
)
print('Issue #146 minified symbol windows extracted')
