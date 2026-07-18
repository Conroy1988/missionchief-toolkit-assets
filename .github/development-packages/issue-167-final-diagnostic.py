#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FINAL_REL = Path('.github/development-packages/issue-167-live-capacity-final.py')
OUTPUT = ROOT / 'docs' / 'diagnostics' / 'issue-167-final-error.txt'

with tempfile.TemporaryDirectory(prefix='mcms-issue-167-final-') as temp_dir:
    work = Path(temp_dir) / 'repo'
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('__pycache__'))
    completed = subprocess.run(
        ['python3', str(FINAL_REL)],
        cwd=work,
        text=True,
        capture_output=True,
    )
    result_text = '\n'.join([
        f'Return code: {completed.returncode}',
        '',
        '--- STDOUT ---',
        completed.stdout,
        '--- STDERR ---',
        completed.stderr,
    ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(result_text, encoding='utf-8')
(ROOT / FINAL_REL).unlink(missing_ok=True)
for stale in (
    ROOT / 'docs' / 'diagnostics' / 'issue-167-package-error.txt',
    ROOT / 'docs' / 'diagnostics' / 'issue-167-source-extract.txt',
):
    stale.unlink(missing_ok=True)
subprocess.run(['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'], cwd=ROOT, check=True)
print(f'Issue #167 final isolated diagnostic written to {OUTPUT.relative_to(ROOT)}')
