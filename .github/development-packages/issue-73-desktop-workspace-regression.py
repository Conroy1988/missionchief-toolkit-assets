#!/usr/bin/env python3
from __future__ import annotations

import base64
import gzip
from pathlib import Path

DATA = Path('.github/development-packages/issue-73-desktop-workspace-regression.py.gz.b64')
payload = gzip.decompress(base64.b64decode(DATA.read_text(encoding='ascii'))).decode('utf-8')
try:
    exec(compile(payload, str(DATA.with_suffix('.decoded.py')), 'exec'), {'__name__': '__main__'})
finally:
    DATA.unlink(missing_ok=True)
