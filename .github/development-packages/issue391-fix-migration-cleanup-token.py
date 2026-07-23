#!/usr/bin/env python3
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META_REL = Path(".github/development-packages/issue391-complete-retirement-package-v3.py")
META = ROOT / META_REL

text = META.read_text(encoding="utf-8")
anchor = '''if text.count(old_hooks) != 1:
    raise RuntimeError("retirement external-hook rewrite anchor drifted")
text = text.replace(old_hooks, new_hooks)

old_diagnostics = '''
insertion = '''if text.count(old_hooks) != 1:
    raise RuntimeError("retirement external-hook rewrite anchor drifted")
text = text.replace(old_hooks, new_hooks)

old_migration_cleanup = "delete merged.missionRequirements;\\n"
new_migration_cleanup = "delete merged['missionRequirements'];\\n"
if text.count(old_migration_cleanup) != 1:
    raise RuntimeError("retirement migration cleanup anchor drifted")
text = text.replace(old_migration_cleanup, new_migration_cleanup)

old_diagnostics = '''
if text.count(anchor) != 1:
    raise RuntimeError("v3 meta-package migration insertion anchor drifted")
text = text.replace(anchor, insertion)

old_diag = '    ROOT / ".github" / "diagnostics" / "issue391-panel-token-context.txt",\n)'
new_diag = '    ROOT / ".github" / "diagnostics" / "issue391-panel-token-context.txt",\n    ROOT / ".github" / "diagnostics" / "issue391-retirement-v3-failure.txt",\n)'
if text.count(old_diag) != 1:
    raise RuntimeError("v3 diagnostic cleanup anchor drifted")
text = text.replace(old_diag, new_diag)

META.write_text(text, encoding="utf-8")
py_compile.compile(str(META), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue391-migration-cleanup-selftest-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / META_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        raise SystemExit("Issue #391 migration-cleanup correction failed full retirement sandbox")

print("Issue #391 migration cleanup token corrected; full retirement sandbox passed.")
