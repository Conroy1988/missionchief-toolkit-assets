#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOTFIX = ROOT / ".github/development-packages/issue-273-exact-personnel-hotfix.py"
TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
DIAGNOSTIC = ROOT / "docs/issue-273-validation-diagnostic.txt"


def main() -> None:
    subprocess.run(["python3", str(HOTFIX)], cwd=ROOT, check=True)
    text = TEST.read_text(encoding="utf-8")
    old = """    const unit = makeVehicleElement(issue273Doc, id, 8, { typeOnRow: true });
    cacheVehicle(id, 8, 1);
    sceneUnits.push(unit.row);"""
    new = """    const unit = makeVehicleElement(issue273Doc, id, 8, { typeOnRow: true });
    unit.row.setAttribute('data-vehicle-id', String(id));
    unit.row.id = `mission_vehicle_${id}`;
    cacheVehicle(id, 8, 1);
    sceneUnits.push(unit.row);"""
    if text.count(old) != 1:
        raise RuntimeError("Issue 273 on-scene fixture marker not found exactly once")
    TEST.write_text(text.replace(old, new, 1), encoding="utf-8")
    DIAGNOSTIC.unlink(missing_ok=True)
    HOTFIX.unlink(missing_ok=True)
    print("Applied Issue 273 exact-personnel hotfix with MissionChief-shaped on-scene vehicle IDs")


if __name__ == "__main__":
    main()
