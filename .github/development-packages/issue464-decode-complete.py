#!/usr/bin/env python3
from __future__ import annotations

import base64
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
PARTS = sorted((ROOT / '.github/development-packages').glob('issue464-complete.payload.*'))
if not PARTS:
    raise SystemExit('Issue #464 payload is missing')
code = zlib.decompress(base64.b64decode(''.join(path.read_text(encoding='utf-8') for path in PARTS))).decode('utf-8')
out = ROOT / '.github/diagnostics/issue464-decoded-complete-package.py.txt'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(code, encoding='utf-8')
SELF.unlink(missing_ok=True)
print(out.relative_to(ROOT))
