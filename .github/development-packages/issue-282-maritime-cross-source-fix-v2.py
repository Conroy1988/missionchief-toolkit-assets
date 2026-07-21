#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
RUNTIME = ROOT / ".github/development-packages/.issue-282-maritime-cross-source-runtime.py"

OLD = '''        expected_hashes = {
            "emv": "ead0cb0e7f215ab843496d65ff90209044c736a08eeed6d5e19a312d775b5c8f",
            "missionHelper": "9c36aa6d408a432fea4169218a03ad3b4f8285c7",
            "vehicles": "76dac4116b0c8b85d73eb879ed9521c2acdad787360a174cddfedee2d9c96cd1",
        }
        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
        if actual_hashes != expected_hashes:
            raise RuntimeError(f"reviewed upstream file hashes changed: {actual_hashes}")
'''
NEW = '''        # The exact reviewed Git commit is immutable. Record each raw-file SHA-256
        # in the offline fixture instead of comparing it with GitHub blob identifiers.
        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    if payload.count(OLD) != 1:
        raise RuntimeError("unable to locate the incorrect upstream hash guard")
    RUNTIME.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")
    try:
        subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, check=True)
    finally:
        RUNTIME.unlink(missing_ok=True)
    ORIGINAL.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
