#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".github/development-packages/issue-253-main-style-headroom-v3.py"
REPORT = ROOT / "docs/issue-253-v7-package-diagnostic.txt"


def main() -> int:
    result = subprocess.run(
        ["python3", str(TARGET)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
    subprocess.run(["git", "clean", "-fdx"], cwd=ROOT, check=True)
    REPORT.write_text(
        "Issue #253 direct-v3 package diagnostic\n"
        f"Return code: {result.returncode}\n\n"
        "===== STDOUT =====\n"
        f"{result.stdout}\n"
        "===== STDERR =====\n"
        f"{result.stderr}\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
