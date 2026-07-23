#!/usr/bin/env python3
from __future__ import annotations
import os, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SELF=Path(__file__).resolve();OUT=ROOT/'.github/diagnostics/issue464-v4-validation-traceback.txt'
with tempfile.TemporaryDirectory(prefix='issue464-v4-validation-') as temp:
    sandbox=Path(temp)/'repo';shutil.copytree(ROOT,sandbox,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    package=subprocess.run(['python3','.github/development-packages/issue464-complete-v4.py'],cwd=sandbox,env=env,text=True,capture_output=True)
    lines=[f'package_exit={package.returncode}','','=== PACKAGE STDOUT ===',package.stdout,'=== PACKAGE STDERR ===',package.stderr]
    if package.returncode==0:
        validator=subprocess.run(['python3','.github/scripts/validate_userscript.py'],cwd=sandbox,env=env,text=True,capture_output=True)
        syntax=subprocess.run(['node','--check','src/MissionChief_Map_Command_Toolkit.user.js'],cwd=sandbox,env=env,text=True,capture_output=True)
        parity=subprocess.run(['cmp','--silent','dist/MissionChief_Map_Command_Toolkit.user.js','dist/MissionChief_Map_Command_Toolkit.txt'],cwd=sandbox,env=env,text=True,capture_output=True)
        lines.extend([f'validator_exit={validator.returncode}',f'syntax_exit={syntax.returncode}',f'parity_exit={parity.returncode}','','=== VALIDATOR STDOUT ===',validator.stdout,'=== VALIDATOR STDERR ===',validator.stderr,'=== SYNTAX STDERR ===',syntax.stderr,'=== PARITY STDERR ===',parity.stderr])
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines),encoding='utf-8');SELF.unlink(missing_ok=True);print(OUT.relative_to(ROOT))
