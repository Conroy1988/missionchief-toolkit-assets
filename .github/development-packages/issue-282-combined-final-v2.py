#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
COMBINED = ROOT / ".github/development-packages/issue-282-combined-final.py"

OLD = '''    contract = replace_once(
        '["python3", str(LSSM_COMPATIBILITY_AUDIT)]',
        '["python3", str(LSSM_COMPATIBILITY_AUDIT), "--skip-runtime"]',
        "avoid duplicate runtime audit",
    )
'''
NEW = '''    contract = replace_once(
        contract,
        '["python3", str(LSSM_COMPATIBILITY_AUDIT)]',
        '["python3", str(LSSM_COMPATIBILITY_AUDIT), "--skip-runtime"]',
        "avoid duplicate runtime audit",
    )
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    if payload.count(OLD) != 1:
        raise RuntimeError("unable to locate malformed contract transformation")
    ORIGINAL.write_text(payload.replace(OLD, NEW, 1), encoding="utf-8")

    subprocess.run(["python3", str(COMBINED)], cwd=ROOT, check=True)

    for path in (
        COMBINED,
        ROOT / ".github/development-packages/issue-282-combined-diagnostic.py",
        ROOT / "docs/issue-282-combined-package-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
