#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / ".github/development-packages/issue-273-shared-exact-personnel-hotfix.py"
TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
FINAL_DIAGNOSTIC = ROOT / "docs/issue-273-final-validation-diagnostic.txt"


def main() -> None:
    subprocess.run(["python3", str(BASE)], cwd=ROOT, check=True)
    text = TEST.read_text(encoding="utf-8")
    old = "const cacheVehicle = (id, type, personnel) => api.vehicleApiCache.set(id, { record: { id, vehicle_type: type, assigned_personnel_count: personnel }, expiresAt: Date.now() + 60000 });"
    new = "const cacheVehicle = (id, type, personnel) => api.vehicleApiCache.set(String(id), { id, vehicle_type: type, assigned_personnel_count: personnel });"
    if text.count(old) != 1:
        raise RuntimeError(f"shared cache fixture marker expected once, found {text.count(old)}")
    TEST.write_text(text.replace(old, new, 1), encoding="utf-8")
    FINAL_DIAGNOSTIC.unlink(missing_ok=True)
    BASE.unlink(missing_ok=True)
    print("Corrected Issue 273 fixtures to use raw records in the shared personal vehicle cache")


if __name__ == "__main__":
    main()
