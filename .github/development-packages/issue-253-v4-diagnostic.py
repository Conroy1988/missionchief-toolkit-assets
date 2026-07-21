#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue-253-main-style-headroom-v2.py"
REPORT = ROOT / "docs/issue-253-v4-package-diagnostic.txt"


def main() -> int:
    result = subprocess.run(["python3", str(PACKAGE)], cwd=ROOT, text=True, capture_output=True)
    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True, capture_output=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "Issue #253 final contract-selection diagnostic\n"
        f"Return code: {result.returncode}\n\n"
        "===== STDOUT =====\n" + result.stdout + "\n===== STDERR =====\n" + result.stderr,
        encoding="utf-8",
    )
    print(f"Captured Issue #253 final contract-selection return code {result.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
