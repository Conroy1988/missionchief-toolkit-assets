#!/usr/bin/env python3
from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SELF=Path(__file__).resolve()
OUT=ROOT/'.github/diagnostics/issue464-performance-correction-traceback.txt'
with tempfile.TemporaryDirectory(prefix='issue464-performance-correction-') as temp:
    repo=Path(temp)/'repo'
    shutil.copytree(ROOT,repo,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    package=subprocess.run(['python3','.github/development-packages/issue464-performance-budget-correction.py'],cwd=repo,env=env,text=True,capture_output=True)
    body=[f'package_exit={package.returncode}','','=== PACKAGE STDOUT ===',package.stdout,'=== PACKAGE STDERR ===',package.stderr]
    if package.returncode==0:
        validator=subprocess.run(['python3','.github/scripts/validate_userscript.py'],cwd=repo,env=env,text=True,capture_output=True)
        syntax=subprocess.run(['node','--check','src/MissionChief_Map_Command_Toolkit.user.js'],cwd=repo,env=env,text=True,capture_output=True)
        body.extend([f'validator_exit={validator.returncode}',f'syntax_exit={syntax.returncode}','','=== VALIDATOR STDOUT ===',validator.stdout,'=== VALIDATOR STDERR ===',validator.stderr,'=== SYNTAX STDERR ===',syntax.stderr])
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(body),encoding='utf-8');SELF.unlink(missing_ok=True);print(OUT.relative_to(ROOT))
