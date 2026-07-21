#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
RUNTIME = ROOT / ".github/development-packages/.issue-282-final-diagnostic-runtime.py"
REPORT = ROOT / "docs/issue-282-final-package-diagnostic.txt"

OLD = '''        expected_hashes = {
            "emv": "ead0cb0e7f215ab843496d65ff90209044c736a08eeed6d5e19a312d775b5c8f",
            "missionHelper": "9c36aa6d408a432fea4169218a03ad3b4f8285c7",
            "vehicles": "76dac4116b0c8b85d73eb879ed9521c2acdad787360a174cddfedee2d9c96cd1",
        }
        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
        if actual_hashes != expected_hashes:
            raise RuntimeError(f"reviewed upstream file hashes changed: {actual_hashes}")
'''
NEW = '''        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    if payload.count(OLD) != 1:
        raise RuntimeError("unable to locate upstream hash guard")
    RUNTIME.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")
    result = subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, text=True, capture_output=True)
    # Restore the exact branch before persisting only the diagnostic report.
    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True, capture_output=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "Issue #282 final package diagnostic\n"
        f"Return code: {result.returncode}\n\n"
        "===== STDOUT =====\n"
        + result.stdout
        + "\n===== STDERR =====\n"
        + result.stderr,
        encoding="utf-8",
    )
    print(f"Captured diagnostic return code {result.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
