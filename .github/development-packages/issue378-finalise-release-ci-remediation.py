#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REMEDIATION=ROOT/'.github/development-packages/issue378-remediate-release-ci.py'
text=REMEDIATION.read_text(encoding='utf-8')
anchor='source = replace_exact(source, old_style, new_style, "operational style ownership")\nold_observer = '
insertion='''source = replace_exact(
    source,
    "    function operationalWindowSyncSettingsUi(panel = document.getElementById(SCRIPT.panelId)) {",
    "    function operationalWindowSyncSettingsUi(panel = operationalQuery(document, `#${SCRIPT.panelId}`)) {",
    "operational settings scoped panel lookup",
)
'''
if text.count(anchor)!=1: raise RuntimeError(f'final getElementById remediation anchor drifted: {text.count(anchor)}')
text=text.replace(anchor,'source = replace_exact(source, old_style, new_style, "operational style ownership")\n'+insertion+'old_observer = ',1)
REMEDIATION.write_text(text,encoding='utf-8')
subprocess.run(['python3',str(REMEDIATION)],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},check=True)
for path in (
    REMEDIATION,
    ROOT/'.github/development-packages/issue378-release-ci-diagnostic-v3.py',
    ROOT/'.github/development-packages/issue378-release-ci-diagnostic-v4.py',
    ROOT/'.github/diagnostics/issue378-release-ci-failure-v3.txt',
    ROOT/'.github/diagnostics/issue378-release-ci-failure-v4.txt',
): path.unlink(missing_ok=True)
print('Issue #378 release CI remediation fully passed and temporary diagnostics were removed.')
