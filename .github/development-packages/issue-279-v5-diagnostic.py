#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression-v5.py"
OUTPUT = ROOT / "docs/issue-279-v5-diagnostic.txt"


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(PACKAGE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    subprocess.run(["git", "restore", "--", "."], cwd=ROOT, check=True)
    subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        f"RETURN CODE: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n",
        encoding="utf-8",
    )
    print(f"Captured Issue 279 v5 diagnostic at {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
