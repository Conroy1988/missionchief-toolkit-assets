#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

PACKAGE = Path(__file__).resolve()
PARTS = [PACKAGE.with_name(f"issue378-requirements-renderer.payload.{index:02d}") for index in range(9)]
missing = [path.name for path in PARTS if not path.exists()]
if missing:
    raise RuntimeError(f"Issue #378 renderer payload is incomplete: {', '.join(missing)}")

payload = "".join(path.read_text(encoding="utf-8") for path in PARTS)
digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
expected = "9b3741ab08292823ce196a19ce4e7855fd449bf5aea21fde0eb813789cde8fe6"
if digest != expected:
    raise RuntimeError(f"Issue #378 renderer payload checksum mismatch: {digest} != {expected}")

for path in PARTS:
    path.unlink()

exec(compile(payload, str(PACKAGE), "exec"), globals(), globals())
