#!/usr/bin/env python3
from __future__ import annotations

import os
import runpy
import subprocess
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TARGET = ROOT / '.github/development-packages/issue470-boot-contract-alignment.py'

try:
    runpy.run_path(str(TARGET), run_name='__main__')
except BaseException as error:
    detail = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    body = (
        '### Issue #470 boot-contract diagnostic\n\n'
        '```text\n' + detail[-12000:] + '\n```'
    )
    subprocess.run(
        ['gh', 'issue', 'comment', '485', '--repo', os.environ.get('GITHUB_REPOSITORY', 'Conroy1988/missionchief-toolkit-assets'), '--body', body],
        cwd=ROOT,
        check=False,
        text=True,
    )
    raise

SELF.unlink(missing_ok=True)
print('Boot contract alignment package completed successfully.')
