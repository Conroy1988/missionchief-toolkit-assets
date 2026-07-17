#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "reports" / "issue-127-transport-sweep-inspection.md"
source = SOURCE.read_text(encoding="utf-8")


def mask_non_code(text: str) -> str:
    chars = list(text)
    i = 0
    state = "code"
    quote = ""
    escaped = False
    while i < len(chars):
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if state == "line":
            if ch != "\n": chars[i] = " "
            else: state = "code"
            i += 1; continue
        if state == "block":
            if ch != "\n": chars[i] = " "
            if ch == "*" and nxt == "/":
                if nxt != "\n": chars[i + 1] = " "
                i += 2; state = "code"
            else: i += 1
            continue
        if state == "string":
            if ch != "\n": chars[i] = " "
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == quote: state = "code"
            i += 1; continue
        if ch == "/" and nxt == "/":
            chars[i] = chars[i + 1] = " "; i += 2; state = "line"; continue
        if ch == "/" and nxt == "*":
            chars[i] = chars[i + 1] = " "; i += 2; state = "block"; continue
        if ch in "'\"`":
            quote = ch; chars[i] = " "; i += 1; state = "string"; continue
        i += 1
    return "".join(chars)


def matching_brace(masked: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(masked)):
        if masked[index] == "{": depth += 1
        elif masked[index] == "}":
            depth -= 1
            if depth == 0: return index
    raise RuntimeError("Unmatched brace")


masked = mask_non_code(source)
functions = [
    "renderTransportSweepPanel",
    "transportSweepReleaseConfirmationVisible",
    "processTransportSweepMission",
    "startTransportSweep",
    "stopTransportSweep",
    "closeTransportSweepWindows",
]
sections = []
for name in functions:
    match = re.search(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(", masked)
    if not match:
        sections.append(f"## `{name}`\n\n_NOT FOUND_\n")
        continue
    opening = masked.find("{", match.start())
    closing = matching_brace(masked, opening)
    line = source.count("\n", 0, match.start()) + 1
    sections.append(f"## `{name}()` — line {line}\n\n```javascript\n{source[match.start():closing + 1]}\n```\n")

runtime_match = re.search(r"\bconst\s+transportSweepRuntime\s*=\s*\{", masked)
if runtime_match:
    opening = masked.find("{", runtime_match.start())
    closing = matching_brace(masked, opening)
    line = source.count("\n", 0, runtime_match.start()) + 1
    sections.insert(0, f"## `transportSweepRuntime` — line {line}\n\n```javascript\n{source[runtime_match.start():closing + 2]}\n```\n")

css_lines = []
for number, line in enumerate(source.splitlines(), 1):
    if "transport-sweep" in line.lower() or "transportSweep" in line and any(token in line for token in ("Id:", "className", "innerHTML", "dataset")):
        css_lines.append(f"{number:05d}: {line}")
sections.append("## Selector and markup references\n\n```text\n" + "\n".join(css_lines) + "\n```\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("# Issue #127 Transport Sweep inspection\n\n" + "\n".join(sections), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
