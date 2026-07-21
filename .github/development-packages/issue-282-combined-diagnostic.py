#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue-282-combined-final.py"
REPORT = ROOT / "docs/issue-282-combined-package-diagnostic.txt"


def main() -> int:
    result = subprocess.run(
        ["python3", str(PACKAGE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    # Preserve only the diagnostic report. The package is required to prove
    # itself in a later clean preflight before any product change is retained.
    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True, capture_output=True)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "Issue #282 combined final-package diagnostic\n"
        f"Return code: {result.returncode}\n\n"
        "===== STDOUT =====\n"
        + result.stdout
        + "\n===== STDERR =====\n"
        + result.stderr,
        encoding="utf-8",
    )
    print(f"Captured combined package diagnostic return code {result.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
