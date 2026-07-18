#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
SOURCE_COMMIT = 'acfe99350657a3a749344ac9bb18138428597fb4'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-final.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-final-package.extract.payload.py'
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-146-minified-helpers.txt'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
TEMP.write_text(payload, encoding='utf-8')
result = subprocess.run([sys.executable, str(TEMP)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
source = SOURCE.read_text(encoding='utf-8')
parts = []
for start_token, end_token in (
    ('    function missionRequirementsPrimaryRuntime() {', '    function missionRequirementsDocumentCss() {'),
    ('    function missionRequirementsHostPanels(source) {', '    function missionRequirementsRemoveRecord(source) {'),
):
    start = source.find(start_token)
    end = source.find(end_token, start + len(start_token))
    parts.append(source[start:end] if start >= 0 and end > start else f'MISSING: {start_token}')
subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
TEMP.unlink(missing_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    'Issue #146 minified ownership helpers\n'
    '====================================\n\n'
    f'Package return code: {result.returncode}\n\n'
    + '\n\n---\n\n'.join(parts)
    + '\n',
    encoding='utf-8',
)
print('Issue #146 minified ownership helpers extracted')
