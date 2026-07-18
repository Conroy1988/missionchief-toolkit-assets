#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
package = Path('.github/development-packages/issue-181-patient-ambulance-demand.py')
output = root / '.github/diagnostics/issue-181-runtime-result-v6.txt'
with tempfile.TemporaryDirectory(prefix='issue-181-v6-') as folder:
    isolated = Path(folder) / 'repository'
    shutil.copytree(root, isolated, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['python3', str(isolated / package)], cwd=isolated, text=True, capture_output=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f'DIAGNOSTIC_V6\nexit_code={result.returncode}\n--- STDOUT ---\n{result.stdout}\n--- STDERR ---\n{result.stderr}', encoding='utf-8')
print(output.relative_to(root))
