from __future__ import annotations

import re
from pathlib import Path

SOURCE = Path("src/MissionChief_Map_Command_Toolkit.user.js")
OUTPUT = Path(".github/diagnostics/issue-73-layout-context.txt")

text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()

patterns = [
    re.compile(r"tablet", re.I),
    re.compile(r"ios(?:\s+mobile|mobile|mode|layout)?", re.I),
    re.compile(r"desktop(?:\s+mode|mode|layout)?", re.I),
    re.compile(r"(?:panel|menu)(?:Position|Pos|Bounds|Height|Layout|Viewport)", re.I),
    re.compile(r"drag(?:ging|gable|Start|Move|End|Handle)?", re.I),
    re.compile(r"max-height|overflow-y|overflow\s*:\s*(?:auto|scroll)", re.I),
    re.compile(r"getBoundingClientRect|ResizeObserver|visualViewport|addEventListener\(\s*['\"]resize", re.I),
    re.compile(r"mcms[^\s'\"]*(?:panel|menu)|(?:panel|menu)[^\s'\"]*mcms", re.I),
]

matched = []
for index, line in enumerate(lines):
    if any(pattern.search(line) for pattern in patterns):
        matched.append(index)

intervals = []
for index in matched:
    start = max(0, index - 7)
    end = min(len(lines), index + 8)
    if intervals and start <= intervals[-1][1] + 2:
        intervals[-1] = (intervals[-1][0], max(intervals[-1][1], end))
    else:
        intervals.append((start, end))

function_re = re.compile(
    r"^\s*(?:async\s+)?function\s+([A-Za-z0-9_$]*(?:panel|menu|drag|layout|tablet|ios|position|viewport)[A-Za-z0-9_$]*)\s*\(",
    re.I,
)
functions = []
for index, line in enumerate(lines, 1):
    match = function_re.search(line)
    if match:
        functions.append((index, match.group(1), line.strip()))

out = [
    "Issue #73 Desktop Mode layout diagnostic",
    "========================================",
    f"Source lines: {len(lines)}",
    f"Matched lines: {len(matched)}",
    f"Merged context blocks: {len(intervals)}",
    "",
    "Relevant function declarations",
    "------------------------------",
]
for line_no, name, declaration in functions:
    out.append(f"{line_no:>6}: {name} :: {declaration}")

out.extend(["", "Matched source context", "----------------------"])
for block_index, (start, end) in enumerate(intervals, 1):
    out.append("")
    out.append(f"### Block {block_index}: lines {start + 1}-{end}")
    for line_no in range(start, end):
        out.append(f"{line_no + 1:>6}: {lines[line_no]}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT} with {len(out)} lines")
