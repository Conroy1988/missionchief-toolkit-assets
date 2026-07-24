#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import os
import shutil
import subprocess
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
PACKAGE_DIR = ROOT / '.github/development-packages'
OUTPUT = ROOT / '.github/diagnostics/issue470-final-package-diagnostic.txt'

parts = sorted(PACKAGE_DIR.glob('issue470-clean-v3.payload.*'))
encoded = ''.join(path.read_text(encoding='utf-8').strip() for path in parts)
lines = [
    'Issue #470 final clean-package diagnostic',
    f'parts={len(parts)}',
    f'encoded_sha256={hashlib.sha256(encoded.encode("utf-8")).hexdigest()}',
]
try:
    code = zlib.decompress(base64.b64decode(encoded)).decode('utf-8')
    lines.extend([
        f'decoded_sha256={hashlib.sha256(code.encode("utf-8")).hexdigest()}',
        f'decoded_lines={len(code.splitlines())}',
    ])
    marker = "pageWindow:{location:{origin:'https://www.missionchief.co.uk'"
    index = code.find(marker)
    lines.extend([
        f'page_window_index={index}',
        '',
        '=== PAGE WINDOW EXCERPT ===',
        code[max(0, index - 250):index + 650] if index >= 0 else 'marker not found',
    ])
except Exception as error:
    lines.extend(['', '=== DECODE ERROR ===', repr(error)])

with tempfile.TemporaryDirectory(prefix='issue470-final-package-') as temporary:
    sandbox = Path(temporary) / 'repo'
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run(
        ['python3', '.github/development-packages/issue470-clean-fix.py'],
        cwd=sandbox,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
    )
    lines.extend([
        '',
        f'wrapper_exit={result.returncode}',
        '',
        '=== WRAPPER STDOUT ===',
        result.stdout,
        '=== WRAPPER STDERR ===',
        result.stderr,
    ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
