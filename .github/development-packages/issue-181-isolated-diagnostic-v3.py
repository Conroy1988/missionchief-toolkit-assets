#!/usr/bin/env python3
from pathlib import Path
import runpy
import shutil
import tempfile
import traceback

root = Path(__file__).resolve().parents[2]
package = Path('.github/development-packages/issue-181-patient-ambulance-demand.py')
output = root / '.github/diagnostics/issue-181-package-result-v3.txt'
with tempfile.TemporaryDirectory(prefix='issue-181-v3-') as folder:
    isolated = Path(folder) / 'repository'
    shutil.copytree(root, isolated, ignore=shutil.ignore_patterns('.git'))
    try:
        runpy.run_path(str(isolated / package), run_name='__main__')
    except BaseException:
        result = 'DIAGNOSTIC_V3\n' + traceback.format_exc()
    else:
        result = 'DIAGNOSTIC_V3\nSUCCESS\n'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(result, encoding='utf-8')
print(output.relative_to(root))
