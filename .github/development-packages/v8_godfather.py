#!/usr/bin/env python3
"""Apply the reviewed MissionChief Toolkit v8 Godfather development package."""

from __future__ import annotations

import base64
import gzip
import hashlib
import sys
from pathlib import Path

EXPECTED_BUILDER_BYTES = 62_027
EXPECTED_BUILDER_SHA256 = "3fb14418ac75e0022a40c0bce4a4ffc15f5e2f8ef517b6b8d311fec04c434d13"
EXPECTED_SLICE_COUNT = 39


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    slices_dir = root / ".github" / "v8-godfather" / "builder-slices"
    slices = sorted(path for path in slices_dir.glob("slice-*.b64") if path.is_file())
    expected_names = tuple(f"slice-{index:03d}.b64" for index in range(EXPECTED_SLICE_COUNT))
    names = tuple(path.name for path in slices)
    if names != expected_names:
        raise SystemExit(f"Unexpected v8 builder slices: {names!r}")

    encoded = "".join(path.read_text(encoding="ascii") for path in slices)
    try:
        compressed = base64.b64decode(encoded, validate=True)
        builder = gzip.decompress(compressed)
    except Exception as error:
        raise SystemExit(f"Could not reconstruct reviewed v8 builder: {error}") from error

    digest = hashlib.sha256(builder).hexdigest()
    if len(builder) != EXPECTED_BUILDER_BYTES or digest != EXPECTED_BUILDER_SHA256:
        raise SystemExit(
            "Reviewed v8 builder integrity mismatch: "
            f"bytes={len(builder)}, sha256={digest}"
        )

    filename = str(root / ".github" / "v8-godfather" / "build_v8_godfather.py")
    previous_argv = sys.argv[:]
    try:
        sys.argv = [filename, "--root", str(root), "--clean-staging"]
        namespace = {
            "__name__": "__main__",
            "__file__": filename,
            "__package__": None,
            "__cached__": None,
        }
        exec(compile(builder, filename, "exec"), namespace, namespace)
    finally:
        sys.argv = previous_argv
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
