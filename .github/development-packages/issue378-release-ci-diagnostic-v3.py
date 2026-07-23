#!/usr/bin/env python3
from __future__ import annotations
import os, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PACKAGE=Path('.github/development-packages/issue378-remediate-release-ci.py'); OUTPUT=ROOT/'.github/diagnostics/issue378-release-ci-failure-v3.txt'
with tempfile.TemporaryDirectory(prefix='issue378-release-ci-diagnostic-v3-') as temporary:
    sandbox=Path(temporary)/'repo'; shutil.copytree(ROOT,sandbox,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    result=subprocess.run(['python3',str(sandbox/PACKAGE)],cwd=sandbox,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(f'ISSUE378_RELEASE_CI_FAILURE_V3\nreturncode={result.returncode}\n\n=== STDOUT ===\n{result.stdout or ""}\n=== STDERR ===\n{result.stderr or ""}',encoding='utf-8')
print(f'Captured Issue #378 release-CI remediation v3 result: {result.returncode}')
