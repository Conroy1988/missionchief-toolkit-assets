#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER_REL = Path('.github/development-packages/issue-285-railway-responding-fix-v7.py')
OUT = ROOT / 'docs/issue-285-v7-diagnostic.txt'


def main() -> int:
    with tempfile.TemporaryDirectory(prefix='issue-285-v7-diagnostic-') as temporary:
        sandbox = Path(temporary) / 'repo'
        shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        result = subprocess.run(
            ['python3', str(sandbox / RUNNER_REL)],
            cwd=sandbox,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        OUT.write_text(f'returncode={result.returncode}\n\n{result.stdout}', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
