#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "v5-state-runtime-diagnostic.txt"
text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()


def line_number(offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_balanced(start: int) -> tuple[int, int]:
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError("opening brace not found")
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    index = brace
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n": line_comment = False
        elif block_comment:
            if char == "*" and nxt == "/": block_comment = False; index += 1
        elif quote:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == quote: quote = None
        else:
            if char == "/" and nxt == "/": line_comment = True; index += 1
            elif char == "/" and nxt == "*": block_comment = True; index += 1
            elif char in "'\"`": quote = char
            elif char == "{": depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0: return start, index + 1
        index += 1
    raise RuntimeError("unterminated block")


def function(name: str) -> str:
    start = text.find(f"function {name}(")
    if start < 0: return f"===== {name}: NOT FOUND =====\n"
    begin, end = extract_balanced(start)
    base = line_number(begin)
    return f"===== {name} at {base} =====\n" + "\n".join(
        f"{base + i:06d}: {line}" for i, line in enumerate(text[begin:end].splitlines())
    ) + "\n\n"

parts = ["V5_STATE_RUNTIME_DIAGNOSTIC\n\n"]
for name in (
    "defaultState",
    "normaliseLoadedState",
    "normaliseOperationalWindowState",
    "loadState",
    "scheduleOperationalSuiteScan",
    "scanOperationalSuite",
    "installOperationalSuiteShell",
    "runtimeOnCleanup",
    "runtimeSetTimeout",
):
    parts.append(function(name))

for needle in (
    "const state = loadState()",
    "let state = loadState()",
    "const runtime =",
    "let runtime =",
    "Object.freeze(runtime",
    "Object.seal(runtime",
    "Object.preventExtensions(runtime",
    "runtime.operationalSuite",
    "operationalSuiteInstalled",
    "normaliseOperationalWindowState(",
):
    parts.append(f"===== REFERENCES {needle!r} =====\n")
    hits = [i for i, line in enumerate(lines) if needle in line]
    parts.append(f"hits={len(hits)}\n")
    for index in hits[:20]:
        for cursor in range(max(0, index - 8), min(len(lines), index + 12)):
            parts.append(f"{cursor + 1:06d}: {lines[cursor]}\n")
        parts.append("\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
