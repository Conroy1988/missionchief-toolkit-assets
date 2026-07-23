#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; TARGET=ROOT/'.github/development-packages/issue378-finalise-release-ci-remediation.py'; OUT_REL=Path('.github/diagnostics/issue378-final-ci-failure.txt')
result=subprocess.run(['python3',str(TARGET)],cwd=ROOT,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
payload=f'ISSUE378_FINAL_CI_FAILURE\nreturncode={result.returncode}\n\n=== STDOUT ===\n{result.stdout or ""}\n=== STDERR ===\n{result.stderr or ""}'
subprocess.run(['git','reset','--hard','HEAD'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
out=ROOT/OUT_REL; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(payload,encoding='utf-8'); print(f'Captured final CI result: {result.returncode}')
