#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
package = Path('.github/development-packages/issue-181-compact-source.py')
output = root / '.github/diagnostics/issue-181-compact-result.txt'
with tempfile.TemporaryDirectory(prefix='issue-181-compact-') as folder:
    isolated = Path(folder) / 'repository'
    shutil.copytree(root, isolated, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['python3', str(isolated / package)], cwd=isolated, text=True, capture_output=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = 'exit_code=' + str(result.returncode) + '\n--- STDOUT ---\n' + result.stdout + '\n--- STDERR ---\n' + result.stderr
    output.write_text(report, encoding='utf-8')
print(output.relative_to(root))
