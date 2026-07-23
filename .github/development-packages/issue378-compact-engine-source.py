#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-enhanced-requirements-engine-core.py"

text = ENGINE_PACKAGE.read_text(encoding="utf-8")
start_token = "engine = r'''"
end_token = "\n'''\n\nsource = source.replace(anchor, engine + anchor, 1)"
if text.count(start_token) != 1 or text.count(end_token) != 1:
    raise RuntimeError("Issue #378 engine package string anchors changed")

prefix, remainder = text.split(start_token, 1)
raw_engine, suffix = remainder.split(end_token, 1)
lines = raw_engine.splitlines()
start_marker = "    // Issue #378 enhanced requirements pure engine."
end_marker = "    // Issue #378 end enhanced requirements pure engine."
if not lines or lines[0] != start_marker or lines[-1] != end_marker:
    raise RuntimeError("Issue #378 engine source markers changed")

chunks: list[str] = []
current: list[str] = []
for line in lines[1:-1]:
    stripped = line.strip()
    if stripped.startswith("//"):
        continue
    if not stripped:
        if current:
            chunks.append(" ".join(current))
            current = []
        continue
    current.append(stripped)
if current:
    chunks.append(" ".join(current))

if not 1 <= len(chunks) <= 28:
    raise RuntimeError(f"unexpected compact engine chunk count: {len(chunks)}")
compact_engine = "\n".join([start_marker, *[f"    {chunk}" for chunk in chunks], end_marker, ""])
updated = prefix + start_token + compact_engine + end_token + suffix
ENGINE_PACKAGE.write_text(updated, encoding="utf-8")
py_compile.compile(str(ENGINE_PACKAGE), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue378-engine-compact-") as temp_dir:
    sandbox = Path(temp_dir) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    package = sandbox / ".github" / "development-packages" / ENGINE_PACKAGE.name
    result = subprocess.run(
        [sys.executable, str(package)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        raise RuntimeError(
            "compacted Issue #378 engine package failed in isolation:\n"
            + result.stdout
            + "\n"
            + result.stderr
        )
    source_lines = len((sandbox / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8").splitlines())
    if source_lines > 64000:
        raise RuntimeError(f"compacted engine still exceeds source ceiling: {source_lines}")
    validator = subprocess.run(
        [sys.executable, ".github/scripts/validate_userscript.py"],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if validator.returncode != 0:
        raise RuntimeError(
            "compacted Issue #378 engine failed canonical validation:\n"
            + validator.stdout
            + "\n"
            + validator.stderr
        )

print(f"Compacted Issue #378 engine into {len(chunks)} logical source lines and verified the full validator.")
