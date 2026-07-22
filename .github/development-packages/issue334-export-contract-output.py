#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
package_name = 'issue332-mission-monitoring-toggles-v42032.py'
package = Path(__file__).with_name(package_name)
diagnostic = root / '.github' / 'diagnostics' / 'issue334-contract-output.txt'
diagnostic.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as temp_dir:
    work = Path(temp_dir) / 'repo'
    shutil.copytree(root, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    temp_package = work / '.github' / 'development-packages' / package_name
    completed = subprocess.run(
        [sys.executable, str(temp_package)],
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
package.unlink(missing_ok=True)
print('Exported isolated Issue #334 contract output')
