#!/usr/bin/env python3
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path(".github/development-packages/issue391-retire-matrix.py")
PACKAGE = ROOT / PACKAGE_REL

text = PACKAGE.read_text(encoding="utf-8")
old = '''def extract_declaration(text: str, name: str, lower: int, upper: int) -> str:
    token = f"    const {name} ="
    start = text.find(token, lower, upper)
    if start < 0:
        raise RuntimeError(f"shared capability declaration missing: {name}")
'''
new = '''def extract_declaration(text: str, name: str, lower: int, upper: int) -> str:
    declaration_pattern = re.compile(rf"^[ \\t]*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)
    declaration_match = declaration_pattern.search(text, lower, upper)
    if declaration_match is None:
        raise RuntimeError(f"shared capability declaration missing: {name}")
    start = declaration_match.start()
'''
if text.count(old) != 1:
    raise RuntimeError("retirement declaration extractor anchor drifted")
text = text.replace(old, new)

old_matcher = 'declaration_pattern = re.compile(rf"^\\s*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)'
new_matcher = 'declaration_pattern = re.compile(rf"^[ \\t]*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)'
if text.count(old_matcher) != 1:
    raise RuntimeError("retirement declaration validator anchor drifted")
text = text.replace(old_matcher, new_matcher)

old_cleanup = '    ROOT / ".github" / "diagnostics" / "issue391-shared-catalogue-map.txt",\n)'
new_cleanup = '    ROOT / ".github" / "diagnostics" / "issue391-shared-catalogue-map.txt",\n    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure-v3.txt",\n)'
if text.count(old_cleanup) != 1:
    raise RuntimeError("retirement v3 diagnostic cleanup anchor drifted")
text = text.replace(old_cleanup, new_cleanup)

PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(PACKAGE), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue391-retirement-selftest-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / PACKAGE_REL)],
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
        raise SystemExit("Corrected Issue #391 retirement package failed sandbox self-test")

print("Issue #391 declaration extractor corrected; full retirement sandbox self-test passed.")
