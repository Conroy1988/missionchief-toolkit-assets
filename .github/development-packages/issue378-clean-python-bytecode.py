#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
GITIGNORE = ROOT / ".gitignore"

for cache_dir in sorted(ROOT.rglob("__pycache__"), reverse=True):
    if ".git" in cache_dir.parts:
        continue
    shutil.rmtree(cache_dir, ignore_errors=True)

for suffix in ("*.pyc", "*.pyo"):
    for bytecode in ROOT.rglob(suffix):
        if ".git" not in bytecode.parts:
            bytecode.unlink(missing_ok=True)

ignore_lines = [
    "# Python bytecode and interpreter caches",
    "__pycache__/",
    "*.py[cod]",
]
existing = GITIGNORE.read_text(encoding="utf-8").splitlines() if GITIGNORE.exists() else []
for line in ignore_lines:
    if line not in existing:
        existing.append(line)
GITIGNORE.write_text("\n".join(existing).rstrip() + "\n", encoding="utf-8")

remaining = [
    str(path.relative_to(ROOT))
    for path in ROOT.rglob("*")
    if ".git" not in path.parts and (path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"})
]
if remaining:
    raise RuntimeError(f"Python bytecode remained after cleanup: {remaining}")

print("Removed Python bytecode artefacts and installed permanent repository ignore rules.")
