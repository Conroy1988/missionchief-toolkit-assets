#!/usr/bin/env python3
from pathlib import Path
import re

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "reports" / "issue-64-boot-lifecycle-inspection.md"

source = SOURCE.read_text(encoding="utf-8")
masked = audit.mask_non_code(source)
match = re.search(r"\b(?:async\s+)?function\s+boot\s*\(", masked)
if not match:
    raise SystemExit("boot() declaration not found")
open_pos = masked.find("{", match.start())
close_pos = audit.matching_brace(masked, open_pos)
if open_pos < 0 or close_pos is None:
    raise SystemExit("boot() declaration could not be extracted")

start_line = source.count("\n", 0, match.start()) + 1
boot_source = source[match.start():close_pos + 1]
tail_source = source[close_pos + 1:]
interesting_tail = "\n".join(
    line for line in tail_source.splitlines()
    if any(token in line for token in ("boot", "DOMContentLoaded", "readyState", "visibilitychange", "__MC_MAP_COMMAND_TOOLKIT"))
)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    "# Issue #64 Boot/Lifecycle inspection\n\n"
    f"`boot()` starts at canonical source line {start_line}.\n\n"
    "## Exact boot declaration\n\n```javascript\n"
    + boot_source
    + "\n```\n\n## Bootstrap tail references\n\n```javascript\n"
    + interesting_tail
    + "\n```\n",
    encoding="utf-8",
)
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
