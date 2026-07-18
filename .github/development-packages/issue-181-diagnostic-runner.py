#!/usr/bin/env python3
from pathlib import Path
import runpy
import traceback

root = Path(__file__).resolve().parents[2]
output = root / '.github/diagnostics/issue-181-package-result.txt'
try:
    runpy.run_path(str(root / '.github/development-packages/issue-181-patient-ambulance-demand.py'), run_name='__main__')
except BaseException:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(traceback.format_exc(), encoding='utf-8')
    print(output.relative_to(root))
