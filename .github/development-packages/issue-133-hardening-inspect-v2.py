#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "docs" / "issue-133-hardening-inspection.md"
OLD_PACKAGE = ROOT / ".github" / "development-packages" / "issue-133-hardening-inspect.py"

source = SOURCE.read_text(encoding="utf-8")
start_marker = "    // Issue #133 clean-room live mission requirements matrix."
end_marker = "    function criticalMissionValueForEntry(entry) {"
start = source.find(start_marker)
end = source.find(end_marker, start)
if start < 0 or end < 0 or end <= start:
    raise SystemExit(f"Unable to resolve bounded Issue #133 source region: start={start}, end={end}")

block = source[start:end].rstrip()
start_line = source.count("\n", 0, start) + 1
end_line = source.count("\n", 0, end) + 1
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    "# Issue #133 — hardening inspection\n\n"
    "Generated mechanically from the applied v4.15.0 candidate. Inspection only.\n\n"
    f"Canonical source lines {start_line}–{end_line - 1}.\n\n"
    "```javascript\n"
    + block
    + "\n```\n",
    encoding="utf-8",
)
if OLD_PACKAGE.exists():
    OLD_PACKAGE.unlink()
print(f"Wrote {OUTPUT.relative_to(ROOT)} and removed failed inspection helper")
