#!/usr/bin/env python3
from __future__ import annotations

import base64
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
PACKAGE_DIR = ROOT / '.github/development-packages'
OUTPUT = ROOT / '.github/diagnostics/issue470-decoded-package.py.txt'
parts = sorted(PACKAGE_DIR.glob('issue470-clean-v3.payload.*'))
encoded = ''.join(path.read_text(encoding='utf-8').strip() for path in parts)
code = zlib.decompress(base64.b64decode(encoded)).decode('utf-8')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(code, encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
