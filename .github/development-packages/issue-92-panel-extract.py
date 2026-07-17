#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = (root / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8").splitlines()
out_path = root / "docs/internal/issue-92-panel-source-extract.md"


def render(start, end):
    start = max(1, start)
    end = min(len(source), end)
    return [f"{n:05d}: {source[n - 1]}" for n in range(start, end + 1)]

out = ["# Issue 92 focused panel source extract", "", "## Complete command-panel markup", "", "```text"]
out += render(27860, 28480)
out += ["```", ""]

anchors = [
    ".mcms-tabs", ".mcms-tab-btn", ".mcms-tab-panel", ".mcms-section-label",
    ".mcms-control-grid", ".mcms-actions-grid", ".mcms-toggle-row",
    "data-tab", "data-panel", "switchTab", "activeTab", "tabButtons",
    "white-space", "text-overflow", "overflow-wrap", "word-break"
]
hits = []
for n, line in enumerate(source, 1):
    if any(anchor.lower() in line.lower() for anchor in anchors):
        hits.append(n)

ranges = []
for n in sorted(set(hits)):
    start, end = max(1, n - 8), min(len(source), n + 8)
    if ranges and start <= ranges[-1][1] + 1:
        ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
    else:
        ranges.append((start, end))

out += ["## Navigation, control-grid and label-layout anchors", ""]
for start, end in ranges:
    out += [f"### Lines {start}-{end}", "", "```text"]
    out += render(start, end)
    out += ["```", ""]

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
print(out_path.relative_to(root))
