#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'.github/development-packages/issue378-remediate-release-ci.py'
OUTPUT_REL=Path('.github/diagnostics/issue378-release-ci-failure-v4.txt')
result=subprocess.run(['python3',str(PACKAGE)],cwd=ROOT,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
payload=f'ISSUE378_RELEASE_CI_FAILURE_V4\nreturncode={result.returncode}\n\n=== STDOUT ===\n{result.stdout or ""}\n=== STDERR ===\n{result.stderr or ""}'
subprocess.run(['git','reset','--hard','HEAD'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
output=ROOT/OUTPUT_REL; output.parent.mkdir(parents=True,exist_ok=True); output.write_text(payload,encoding='utf-8')
print(f'Captured real-checkout release-CI remediation result: {result.returncode}')
