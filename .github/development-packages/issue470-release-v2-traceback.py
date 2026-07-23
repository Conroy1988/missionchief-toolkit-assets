#!/usr/bin/env python3
from __future__ import annotations
import os,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SELF=Path(__file__).resolve();OUT=ROOT/'.github/diagnostics/issue470-release-v2-traceback.txt'
with tempfile.TemporaryDirectory(prefix='issue470-release-v2-trace-') as td:
    repo=Path(td)/'repo';shutil.copytree(ROOT,repo,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    package=subprocess.run(['python3','.github/development-packages/issue470-release-v2.py'],cwd=repo,env=env,text=True,capture_output=True)
    lines=[f'package_exit={package.returncode}','','=== PACKAGE STDOUT ===',package.stdout,'=== PACKAGE STDERR ===',package.stderr]
    if package.returncode==0:
        validator=subprocess.run(['python3','.github/scripts/validate_userscript.py'],cwd=repo,env=env,text=True,capture_output=True)
        syntax=subprocess.run(['node','--check','src/MissionChief_Map_Command_Toolkit.user.js'],cwd=repo,env=env,text=True,capture_output=True)
        issue470=subprocess.run(['node','.github/scripts/test_issue470_menu_requirements_runtime.js'],cwd=repo,env=env,text=True,capture_output=True)
        lines.extend([f'validator_exit={validator.returncode}',f'syntax_exit={syntax.returncode}',f'issue470_exit={issue470.returncode}','','=== VALIDATOR STDOUT ===',validator.stdout,'=== VALIDATOR STDERR ===',validator.stderr,'=== SYNTAX STDOUT ===',syntax.stdout,'=== SYNTAX STDERR ===',syntax.stderr,'=== ISSUE470 STDOUT ===',issue470.stdout,'=== ISSUE470 STDERR ===',issue470.stderr])
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines),encoding='utf-8');SELF.unlink(missing_ok=True);print(OUT.relative_to(ROOT))
