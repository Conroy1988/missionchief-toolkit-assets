#!/usr/bin/env python3
import os, shutil, subprocess, tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
self_path=Path(__file__).resolve()
out=root/'.github/diagnostics/issue464-post-contract-validation.txt'
with tempfile.TemporaryDirectory(prefix='issue464-post-contract-') as td:
    repo=Path(td)/'repo'
    shutil.copytree(root,repo,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    package=subprocess.run(['python3','.github/development-packages/issue464-complete-v5.py'],cwd=repo,env=env,text=True,capture_output=True)
    validator=None
    if package.returncode==0:
        validator=subprocess.run(['python3','.github/scripts/validate_userscript.py'],cwd=repo,env=env,text=True,capture_output=True)
    body=[f'package_exit={package.returncode}',package.stdout,package.stderr]
    if validator is not None:
        body += [f'validator_exit={validator.returncode}',validator.stdout,validator.stderr]
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text('\n\n'.join(body),encoding='utf-8')
self_path.unlink(missing_ok=True)
print(out.relative_to(root))
