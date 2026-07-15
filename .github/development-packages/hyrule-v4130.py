#!/usr/bin/env python3
"""Reconstruct and apply the reviewed Hyrule Command v4.13.0 package."""
from __future__ import annotations
import gzip
from pathlib import Path

PARTS = [f".github/development-packages/hyrule-v4130-part-{index:02d}.hex" for index in range(1, 13)]
root = Path(__file__).resolve().parents[2]
compressed = bytes.fromhex("".join((root / part).read_text(encoding="ascii") for part in PARTS))
source = gzip.decompress(compressed)
for part in PARTS:
    (root / part).unlink(missing_ok=True)
namespace = {"__name__": "__main__", "__file__": str(Path(__file__).resolve())}
exec(compile(source, "hyrule-command-v4130-complete.py", "exec"), namespace)
