#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]
PARTS = [
    ROOT / ".github" / "development-packages" / "issue-169-lightbox-context.part1.txt",
    ROOT / ".github" / "development-packages" / "issue-169-lightbox-context.part2.txt",
    ROOT / ".github" / "development-packages" / "issue-169-lightbox-context.part3.txt",
]
EXPECTED_SHA256 = "7effd147e2175008628f107309553136d75c78e88483c77d252ac2ea4041198d"

missing = [str(path.relative_to(ROOT)) for path in PARTS if not path.exists()]
if missing:
    raise AssertionError(f"Issue 169 package parts missing: {missing}")

source = "".join(path.read_text(encoding="utf-8") for path in PARTS)
actual = hashlib.sha256(source.encode("utf-8")).hexdigest()
if actual != EXPECTED_SHA256:
    raise AssertionError(f"Issue 169 package checksum mismatch: {actual}")

for path in PARTS:
    path.unlink()

namespace = {"__file__": __file__, "__name__": "__main__"}
exec(compile(source, __file__, "exec"), namespace)
