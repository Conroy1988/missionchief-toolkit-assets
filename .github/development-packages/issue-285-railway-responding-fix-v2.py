#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-285-railway-responding-fix.py"

OLD = '''    DOC.write_text(
        """# Issue #285 — Railway Police Responding contract\\n\\n"
        "MissionChief Railway Police Officers use the native education key `railway_police`. "
        "The separate key `railway_police_command` represents Mobile Operations Managers and does not satisfy this requirement.\\n\\n"
        "The Matrix reads Units Responding from the canonical `#mission_vehicle_driving` table, resolves the stable vehicle identity, "
        "uses the responding crew cell `sortvalue` only within that canonical table, and combines it with explicit or linked qualification evidence.\\n\\n"
        "Accepted specialist evidence includes MissionChief-native education attributes, compatible filter payloads, and existing discrete bracketed badges. "
        "Generic vehicle captions, custom categories, vehicle type alone and total crew without qualification evidence do not prove Railway Police capacity.\\n\\n"
        "If crew is known but the specialist qualification cannot be proven, capacity remains bounded/unknown instead of being reported as a confident zero.\\n",
        encoding="utf-8",
    )
'''

NEW = '''    DOC.write_text(
        "# Issue #285 — Railway Police Responding contract\\n\\n"
        "MissionChief Railway Police Officers use the native education key `railway_police`. "
        "The separate key `railway_police_command` represents Mobile Operations Managers and does not satisfy this requirement.\\n\\n"
        "The Matrix reads Units Responding from the canonical `#mission_vehicle_driving` table, resolves the stable vehicle identity, "
        "uses the responding crew cell `sortvalue` only within that canonical table, and combines it with explicit or linked qualification evidence.\\n\\n"
        "Accepted specialist evidence includes MissionChief-native education attributes, compatible filter payloads, and existing discrete bracketed badges. "
        "Generic vehicle captions, custom categories, vehicle type alone and total crew without qualification evidence do not prove Railway Police capacity.\\n\\n"
        "If crew is known but the specialist qualification cannot be proven, capacity remains bounded/unknown instead of being reported as a confident zero.\\n",
        encoding="utf-8",
    )
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    count = payload.count(OLD)
    if count != 1:
        raise RuntimeError(f"documentation syntax block: expected one match, found {count}")
    ORIGINAL.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")
    py_compile.compile(str(ORIGINAL), doraise=True)
    subprocess.run(["python3", str(ORIGINAL)], cwd=ROOT, check=True)
    ORIGINAL.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
