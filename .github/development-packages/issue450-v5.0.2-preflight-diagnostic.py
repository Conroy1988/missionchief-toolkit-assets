#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path(".github/development-packages/issue450-v5.0.2-menu-bootstrap-recovery-v3.py")
OUTPUT = ROOT / ".github" / "diagnostics" / "issue450-v5.0.2-preflight-failure.txt"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

with tempfile.TemporaryDirectory(prefix="issue450-v502-diagnostic-") as temp_dir:
    sandbox = Path(temp_dir) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    result = subprocess.run(
        [sys.executable, str(sandbox / PACKAGE_REL)],
        cwd=sandbox,
        env=ENV,
        text=True,
        capture_output=True,
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    "ISSUE450 V5.0.2 PREFLIGHT DIAGNOSTIC\n"
    f"returncode={result.returncode}\n\n"
    "===== STDOUT =====\n"
    f"{result.stdout}\n\n"
    "===== STDERR =====\n"
    f"{result.stderr}\n",
    encoding="utf-8",
)

for name in (
    "issue450-v5.0.2-menu-bootstrap-recovery.py",
    "issue450-v5.0.2-menu-bootstrap-recovery-v2.py",
    "issue450-v5.0.2-menu-bootstrap-recovery-v3.py",
):
    (ROOT / ".github" / "development-packages" / name).unlink(missing_ok=True)

print(f"Wrote {OUTPUT.relative_to(ROOT)} with return code {result.returncode}.")
