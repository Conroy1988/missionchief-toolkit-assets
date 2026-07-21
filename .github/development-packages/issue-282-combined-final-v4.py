#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
V3 = ROOT / ".github/development-packages/issue-282-combined-final-v3.py"

OLD = '''const inlandParsed = { requirements: [inlandRequirement], unresolved: [] };
const inlandCatalogue = { requirements: [{ key: 'boat-or-inland', baseline: 3, missing: 3 }] };
'''
NEW = '''// MissionChief live missing excludes the one asset already on site.
const inlandOperationalRequirement = { ...inlandRequirement, missing: 2 };
const inlandParsed = { requirements: [inlandOperationalRequirement], unresolved: [] };
const inlandCatalogue = { requirements: [{ key: 'boat-or-inland', baseline: 3, missing: 3 }] };
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    count = payload.count(OLD)
    if count != 1:
        raise RuntimeError(f"maritime operational fixture: expected one match, found {count}")
    ORIGINAL.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")

    subprocess.run(["python3", str(V3)], cwd=ROOT, check=True)

    for path in (
        V3,
        ROOT / ".github/development-packages/issue-282-v3-diagnostic.py",
        ROOT / "docs/issue-282-v3-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
