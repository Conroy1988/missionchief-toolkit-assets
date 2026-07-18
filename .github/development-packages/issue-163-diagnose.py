#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue-163-catalogue-resolver.py"
OUT = ROOT / "docs" / "diagnostics" / "issue-163-package-error.txt"

result = subprocess.run(["python3", str(PACKAGE)], cwd=ROOT, text=True, capture_output=True)
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True, capture_output=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True, capture_output=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    "Issue #163 package diagnostic\n"
    f"return_code={result.returncode}\n\n"
    "=== STDOUT ===\n"
    + result.stdout[-30000:]
    + "\n=== STDERR ===\n"
    + result.stderr[-30000:],
    encoding="utf-8",
)
print(f"Wrote {OUT.relative_to(ROOT)}")
