#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
wrapper_name = 'issue332-mission-monitoring-toggles-v42032-corrected.py'
wrapper = Path(__file__).with_name(wrapper_name)
original = Path(__file__).with_name('issue332-mission-monitoring-toggles-v42032.py')
diagnostic = root / '.github' / 'diagnostics' / 'issue340-corrected-contract-output.txt'
diagnostic.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as temp_dir:
    work = Path(temp_dir) / 'repo'
    shutil.copytree(root, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    temp_wrapper = work / '.github' / 'development-packages' / wrapper_name
    completed = subprocess.run(
        [sys.executable, str(temp_wrapper)],
        cwd=work,
        text=True,
        capture_output=True,
        check=False,
    )
    result = (
        f'returncode={completed.returncode}\n\n'
        '--- stdout ---\n'
        f'{completed.stdout}\n'
        '--- stderr ---\n'
        f'{completed.stderr}\n'
    )
diagnostic.write_text(result, encoding='utf-8')
wrapper.unlink(missing_ok=True)
original.unlink(missing_ok=True)
print('Exported isolated corrected v4.20.32 contract output')
