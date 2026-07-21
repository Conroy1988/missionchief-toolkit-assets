#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-230-probability-metadata-fix.py"
V2 = ROOT / ".github/development-packages/issue-230-probability-metadata-fix-v2.py"

OLD = '''    SOURCE.write_text(source, encoding="utf-8")

    runtime = RUNTIME_TEST.read_text(encoding="utf-8")
'''
NEW = '''    SOURCE.write_text(source, encoding="utf-8")
    candidate_bytes = SOURCE.read_bytes()
    for distribution in (
        ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js",
        ROOT / "dist/MissionChief_Map_Command_Toolkit.txt",
    ):
        distribution.write_bytes(candidate_bytes)

    runtime = RUNTIME_TEST.read_text(encoding="utf-8")
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    count = payload.count(OLD)
    if count != 1:
        raise RuntimeError(f"candidate distribution synchronization: expected one match, found {count}")
    ORIGINAL.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")
    subprocess.run(["python3", str(V2)], cwd=ROOT, check=True)
    for path in (
        V2,
        ROOT / "docs/issue-230-probability-v2-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
