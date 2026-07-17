#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "reports" / "issue-64-boot-lifecycle-inspection.md"


def mask_non_code(text: str) -> str:
    chars = list(text)
    index = 0
    state = "code"
    quote = ""
    escaped = False
    while index < len(chars):
        char = chars[index]
        next_char = chars[index + 1] if index + 1 < len(chars) else ""
        if state == "line-comment":
            if char != "\n":
                chars[index] = " "
            else:
                state = "code"
            index += 1
            continue
        if state == "block-comment":
            if char != "\n":
                chars[index] = " "
            if char == "*" and next_char == "/":
                if next_char != "\n":
                    chars[index + 1] = " "
                index += 2
                state = "code"
            else:
                index += 1
            continue
        if state == "string":
            if char != "\n":
                chars[index] = " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                state = "code"
            index += 1
            continue
        if char == "/" and next_char == "/":
            chars[index] = chars[index + 1] = " "
            index += 2
            state = "line-comment"
            continue
        if char == "/" and next_char == "*":
            chars[index] = chars[index + 1] = " "
            index += 2
            state = "block-comment"
            continue
        if char in "'\"`":
            quote = char
            chars[index] = " "
            index += 1
            state = "string"
            escaped = False
            continue
        index += 1
    return "".join(chars)


def matching_brace(masked: str, opening: int) -> int | None:
    depth = 0
    for index in range(opening, len(masked)):
        if masked[index] == "{":
            depth += 1
        elif masked[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


source = SOURCE.read_text(encoding="utf-8")
masked = mask_non_code(source)
match = re.search(r"\b(?:async\s+)?function\s+boot\s*\(", masked)
if not match:
    raise SystemExit("boot() declaration not found")
open_pos = masked.find("{", match.start())
close_pos = matching_brace(masked, open_pos)
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
