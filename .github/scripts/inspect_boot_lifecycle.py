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
            if char != "\n": chars[index] = " "
            else: state = "code"
            index += 1
            continue
        if state == "block-comment":
            if char != "\n": chars[index] = " "
            if char == "*" and next_char == "/":
                if next_char != "\n": chars[index + 1] = " "
                index += 2
                state = "code"
            else: index += 1
            continue
        if state == "string":
            if char != "\n": chars[index] = " "
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == quote: state = "code"
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
        if masked[index] == "{": depth += 1
        elif masked[index] == "}":
            depth -= 1
            if depth == 0: return index
    return None


def extract_function(source: str, masked: str, name: str) -> tuple[int, str] | None:
    match = re.search(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(", masked)
    if not match: return None
    opening = masked.find("{", match.start())
    closing = matching_brace(masked, opening)
    if opening < 0 or closing is None: raise SystemExit(f"{name}() could not be extracted")
    return source.count("\n", 0, match.start()) + 1, source[match.start():closing + 1]


source = SOURCE.read_text(encoding="utf-8")
masked = mask_non_code(source)
source_lines = source.splitlines()
names = [
    "createCleanExit", "runtimeOnCleanup", "runtimeListen", "runtimeSetTimeout",
    "runtimeTrackObserver", "runtimeRegisterTask", "runtimeWakeTaskScheduler",
    "runtimeRunWhenIdle", "scheduleDeferredOperationalStartup", "boot", "scheduleBoot",
]
output = ["# Issue #64 Boot/Lifecycle inspection", "", f"Source lines: {len(source_lines)}", ""]
output.extend(["## Runtime ownership block — canonical lines 480–850", "", "```javascript"])
output.extend(f"{line_no:05d}: {source_lines[line_no - 1]}" for line_no in range(480, 851))
output.extend(["```", ""])
for name in names:
    extracted = extract_function(source, masked, name)
    if not extracted:
        output.extend([f"## `{name}()`", "", "_Declaration not found._", ""])
        continue
    line, declaration = extracted
    output.extend([f"## `{name}()` — line {line}", "", "```javascript", declaration, "```", ""])
output.extend(["## Final bootstrap tail", "", "```javascript", "\n".join(source_lines[-80:]), "```", ""])
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(output), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
