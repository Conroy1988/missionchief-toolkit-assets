#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path(".github/development-packages/issue391-complete-retirement-package-v2.py")
RETIRE_REL = Path(".github/development-packages/issue391-retire-matrix.py")
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-panel-token-context.txt"

with tempfile.TemporaryDirectory(prefix="issue391-panel-token-context-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    retire = sandbox / RETIRE_REL
    text = retire.read_text(encoding="utf-8")
    old = '            raise RuntimeError(f"legacy Matrix token survived retirement: {token}")\n'
    new = '''            positions = [index for index in range(len(source)) if source.startswith(token, index)]
            contexts = []
            for position in positions:
                contexts.append(source[max(0, position - 220):min(len(source), position + len(token) + 220)])
            raise RuntimeError(f"legacy Matrix token survived retirement: {token}; positions={positions}; contexts={contexts!r}")
'''
    if text.count(old) != 1:
        raise RuntimeError("retirement survivor diagnostic anchor drifted")
    retire.write_text(text.replace(old, new), encoding="utf-8")
    result = subprocess.run(
        ["python3", str(sandbox / PACKAGE_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

payload = [
    "ISSUE391_PANEL_TOKEN_CONTEXT_V1",
    f"returncode={result.returncode}",
    "",
    "=== STDOUT ===",
    result.stdout.rstrip(),
    "",
    "=== STDERR ===",
    result.stderr.rstrip(),
    "",
]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(payload), encoding="utf-8")
print(f"Captured panel-token context in {OUTPUT.relative_to(ROOT)}")
