#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "diagnostics" / "issue-163-performance-policy.txt"
needles = ["1900000", "1_900_000", "1,900,000", "31000", "31_000", "31,000", "2026-07-14-initial"]
rows: list[str] = []
for path in sorted((ROOT / ".github").rglob("*")):
    if not path.is_file() or path.suffix.lower() not in {".py", ".js", ".json", ".yml", ".yaml", ".md", ".txt"}:
        continue
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        continue
    for number, line in enumerate(lines, 1):
        if any(needle in line for needle in needles):
            rows.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("Issue #163 performance policy locations\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} with {len(rows)} matches")
