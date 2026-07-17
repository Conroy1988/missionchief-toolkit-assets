#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = (root / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8").splitlines()
out_path = root / "docs/internal/issue-92-label-css-audit.md"
anchors = [
    ".mcms-tabs", ".mcms-tab-btn", ".mcms-label", ".mcms-small-btn",
    ".mcms-row-label", ".mcms-section-label", "data-mcms-device-layout=\"tablet\"",
    "data-mcms-device-layout=\"mobile\"", "data-mcms-device-layout=\"ios\""
]
hits = [n for n, line in enumerate(source, 1) if any(a.lower() in line.lower() for a in anchors)]
ranges = []
for n in hits:
    start, end = max(1, n - 4), min(len(source), n + 4)
    if ranges and start <= ranges[-1][1] + 1:
        ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
    else:
        ranges.append((start, end))

out = ["# Issue 92 label and responsive CSS audit", ""]
for start, end in ranges:
    out += [f"## Lines {start}-{end}", "", "```text"]
    out += [f"{n:05d}: {source[n - 1]}" for n in range(start, end + 1)]
    out += ["```", ""]
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
print(out_path.relative_to(root))
