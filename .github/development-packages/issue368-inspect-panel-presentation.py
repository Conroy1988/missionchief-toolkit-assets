#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "issue368-authoritative-empty-v42037.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue368-panel-presentation.txt"

with tempfile.TemporaryDirectory(prefix="issue368-panel-") as temp:
    copy = Path(temp) / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    package = copy / ".github" / "development-packages" / ORIGINAL.name
    text = package.read_text(encoding="utf-8")
    old = "assert(issue368Html.includes('4/4 covered'), 'Issue #368 panel reports full catalogue coverage');"
    new = "console.log('ISSUE368_PRESENTATION=' + JSON.stringify(issue368Presentation));"
    if text.count(old) != 1:
        raise RuntimeError("unable to locate the Issue #368 summary assertion")
    package.write_text(text.replace(old, new, 1), encoding="utf-8")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        ["python3", str(package)],
        cwd=copy,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    report = f"returncode={result.returncode}\n\n{result.stdout}"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(report, encoding="utf-8")
ORIGINAL.unlink(missing_ok=True)
print(f"Captured Issue #368 panel presentation to {OUTPUT.relative_to(ROOT)}")
