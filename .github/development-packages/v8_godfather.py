#!/usr/bin/env python3
"""Apply the reviewed MissionChief Toolkit v8 Godfather development package."""

from __future__ import annotations

import base64
import gzip
import hashlib
import sys
from pathlib import Path

EXPECTED_BUILDER_BYTES = 61_179
EXPECTED_BUILDER_SHA256 = "387ad823c2d361a8d94d49217819ffc92d6ee9d33e70b65d826e91b982cae75e"
EXPECTED_PARTS = ("part-00.b64", "part-01.b64", "part-02.b64")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parts_dir = root / ".github" / "v8-godfather" / "builder-parts"
    parts = sorted(path for path in parts_dir.glob("part-*.b64") if path.is_file())
    names = tuple(path.name for path in parts)
    if names != EXPECTED_PARTS:
        raise SystemExit(f"Unexpected v8 builder parts: {names!r}")

    encoded = "".join("".join(path.read_text(encoding="utf-8").split()) for path in parts)
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
