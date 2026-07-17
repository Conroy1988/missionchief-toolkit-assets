#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[2]
source_path = root / "src/MissionChief_Map_Command_Toolkit.user.js"
report_path = root / "docs/internal/issue-92-navigation-audit.md"
text = source_path.read_text(encoding="utf-8")
lines = text.splitlines()
sections = ["Skins", "Tools", "Resources", "Ops", "Payouts", "Discord", "Places", "Settings"]

out = [
    "# Issue 92 navigation diagnostic",
    "",
    f"Canonical source lines: {len(lines)}",
    "",
]

for section in sections:
    out.extend([f"## {section}", ""])
    hits = [n for n, line in enumerate(lines, 1) if section in line]
    out.append(f"Occurrences: {len(hits)}")
    out.append("")
    for hit in hits[:20]:
        start = max(1, hit - 10)
        end = min(len(lines), hit + 10)
        out.append(f"### Lines {start}-{end}")
        out.append("```text")
        for number in range(start, end + 1):
            out.append(f"{number:05d}: {lines[number - 1]}")
        out.extend(["```", ""])

patterns = [
    "data-tab", "data-section", "activeTab", "activeSection",
    "mcms-tab", "mcms-section", "sectionOrder", "tabOrder",
    "white-space", "text-overflow", "overflow-wrap", "word-break",
    "grid-template-columns", "flex-wrap", "@media"
]
out.extend(["## Navigation and responsive-layout anchors", ""])
seen = set()
for number, line in enumerate(lines, 1):
    if not any(token.lower() in line.lower() for token in patterns):
        continue
    start = max(1, number - 5)
    end = min(len(lines), number + 5)
    key = (start, end)
    if key in seen:
        continue
    seen.add(key)
    out.append(f"### Lines {start}-{end}")
    out.append("```text")
    for item in range(start, end + 1):
        out.append(f"{item:05d}: {lines[item - 1]}")
    out.extend(["```", ""])

label_context = re.compile(r"button|toggle|select|control|setting|section|tab|label|title|textContent|innerHTML", re.I)
quoted = re.compile(r"(['\"])([^'\"\n]{3,64})\1")
candidates = {}
for number, line in enumerate(lines, 1):
    if not label_context.search(line):
        continue
    for match in quoted.finditer(line):
        value = match.group(2).strip()
        if not value or value.startswith(("#", ".", "[", "<", "http", "mcms-")):
            continue
        if " " not in value:
            continue
        candidates.setdefault(value, []).append(number)

out.extend(["## Long control-label candidates", ""])
for value, numbers in sorted(candidates.items(), key=lambda item: (-len(item[0]), item[0].lower()))[:250]:
    out.append(f"- {len(value):02d} chars | `{value}` | lines {', '.join(map(str, numbers[:8]))}")

report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(out) + "\n", encoding="utf-8")
print(report_path.relative_to(root))
