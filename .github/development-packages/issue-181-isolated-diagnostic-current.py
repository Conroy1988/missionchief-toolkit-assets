#!/usr/bin/env python3
from pathlib import Path
import runpy
import shutil
import tempfile
import traceback

root = Path(__file__).resolve().parents[2]
relative_package = Path('.github/development-packages/issue-181-patient-ambulance-demand.py')
output = root / '.github/diagnostics/issue-181-package-result.txt'
with tempfile.TemporaryDirectory(prefix='issue-181-current-') as folder:
    isolated = Path(folder) / 'repository'
    shutil.copytree(root, isolated, ignore=shutil.ignore_patterns('.git'))
    try:
        runpy.run_path(str(isolated / relative_package), run_name='__main__')
    except BaseException:
        result = traceback.format_exc()
    else:
        result = 'SUCCESS: Issue 181 product package completed in the isolated repository copy.\n'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(result, encoding='utf-8')
print(output.relative_to(root))
