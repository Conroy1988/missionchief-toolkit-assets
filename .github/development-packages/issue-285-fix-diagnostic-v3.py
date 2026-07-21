#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_REL = Path('.github/development-packages/issue-285-railway-responding-fix.py')
ORIGINAL = ROOT / ORIGINAL_REL
OUT = ROOT / 'docs/issue-285-package-diagnostic.txt'


def main() -> int:
    payload = ORIGINAL.read_text(encoding='utf-8')
    old = '        """# Issue #285 — Railway Police Responding contract\\n\\n"'
    new = '        "# Issue #285 — Railway Police Responding contract\\n\\n"'
    count = payload.count(old)
    if count != 1:
        OUT.write_text(f'syntax repair anchor count: {count}\n', encoding='utf-8')
        return 0
    with tempfile.TemporaryDirectory(prefix='issue-285-diagnostic-') as temporary:
        sandbox = Path(temporary) / 'repo'
        shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        fixed = sandbox / ORIGINAL_REL
        fixed.write_text(payload.replace(old, new, 1), encoding='utf-8')
        result = subprocess.run(
            ['python3', str(fixed)],
            cwd=sandbox,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        OUT.write_text(
            f'returncode={result.returncode}\n\n{result.stdout}',
            encoding='utf-8',
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
