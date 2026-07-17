#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
OUTPUT = ROOT / "docs" / "issue-133-help-version-inspection.json"
TOKENS = ("Help Centre", "Help Center", "Guide for Toolkit", "guideVersion", "4.14.10")
SKIP_PARTS = {".git", "node_modules"}
ALLOWED_SUFFIXES = {".js", ".md", ".html", ".json", ".txt", ".py", ".yml", ".yaml"}

results = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
        continue
    if any(part in SKIP_PARTS for part in path.parts):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    lines = text.splitlines()
    matches = []
    for index, line in enumerate(lines, 1):
        if any(token in line for token in TOKENS):
            matches.append({"line": index, "text": line.strip()[:500]})
    if matches:
        results.append({"path": path.relative_to(ROOT).as_posix(), "matches": matches})

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps({"results": results}, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(results)} matching files")
