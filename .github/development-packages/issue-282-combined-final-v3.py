#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
COMBINED = ROOT / ".github/development-packages/issue-282-combined-final.py"

REPLACEMENTS = (
    (
        '''    contract = replace_once(
        '["python3", str(LSSM_COMPATIBILITY_AUDIT)]',
        '["python3", str(LSSM_COMPATIBILITY_AUDIT), "--skip-runtime"]',
        "avoid duplicate runtime audit",
    )
''',
        '''    contract = replace_once(
        contract,
        '["python3", str(LSSM_COMPATIBILITY_AUDIT)]',
        '["python3", str(LSSM_COMPATIBILITY_AUDIT), "--skip-runtime"]',
        "avoid duplicate runtime audit",
    )
''',
        "audit invocation transformation",
    ),
    (
        '''    contract = replace_once(
        '"MISSION_REQUIREMENTS_TRACTIVE_TYPES",',
        '"MISSION_REQUIREMENTS_TRACTIVE_TYPES",\\n        "definition.pair !== true && compatibleTractiveTypes.length > 0",\\n        "Inland Rescue Boat (Trailer)",\\n        "Seagoing Vessel",',
        "cross-source source markers",
    )
''',
        '''    contract = replace_once(
        contract,
        '"MISSION_REQUIREMENTS_TRACTIVE_TYPES",',
        '"MISSION_REQUIREMENTS_TRACTIVE_TYPES",\\n        "definition.pair !== true && compatibleTractiveTypes.length > 0",\\n        "Inland Rescue Boat (Trailer)",\\n        "Seagoing Vessel",',
        "cross-source source markers",
    )
''',
        "source-marker transformation",
    ),
)


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    for old, new, label in REPLACEMENTS:
        count = payload.count(old)
        if count != 1:
            raise RuntimeError(f"{label}: expected one match, found {count}")
        payload = payload.replace(old, new, 1)
    ORIGINAL.write_text(payload, encoding="utf-8")

    subprocess.run(["python3", str(COMBINED)], cwd=ROOT, check=True)

    for path in (
        COMBINED,
        ROOT / ".github/development-packages/issue-282-combined-final-v2.py",
        ROOT / ".github/development-packages/issue-282-combined-diagnostic.py",
        ROOT / ".github/development-packages/issue-282-combined-v2-diagnostic.py",
        ROOT / "docs/issue-282-combined-package-diagnostic.txt",
        ROOT / "docs/issue-282-combined-v2-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
