#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    removals = [
        ROOT / '.github/development-packages/issue-285-railway-responding-diagnostic.py',
        ROOT / '.github/development-packages/__pycache__/issue-285-railway-responding-fix-v7.cpython-312.pyc',
        ROOT / '.github/development-packages/__pycache__/issue-285-railway-responding-fix-v8.cpython-312.pyc',
        ROOT / '.github/development-packages/__pycache__/issue-285-railway-responding-fix.cpython-312.pyc',
        ROOT / '.github/scripts/__pycache__/full_userscript_audit.cpython-312.pyc',
    ]
    for path in removals:
        path.unlink(missing_ok=True)
    for directory in (
        ROOT / '.github/development-packages/__pycache__',
        ROOT / '.github/scripts/__pycache__',
    ):
        try:
            directory.rmdir()
        except OSError:
            pass

    subprocess.run(['python3', '.github/scripts/validate_userscript.py'], cwd=ROOT, check=True)
    subprocess.run(['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'], cwd=ROOT, check=True)
    subprocess.run(['bash', '.github/scripts/run_userscript_preflight.sh', '--contracts'], cwd=ROOT, check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
