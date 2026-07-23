#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "v5-menu-boot-slices.txt"
text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()


def line_number(offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_function(name: str) -> str:
    needles = [f"function {name}(", f"async function {name}("]
    starts = [text.find(needle) for needle in needles]
    starts = [value for value in starts if value >= 0]
    if not starts:
        return f"===== {name}: NOT FOUND =====\n"
    start = min(starts)
    brace = text.find("{", start)
    if brace < 0:
        return f"===== {name}: OPEN BRACE NOT FOUND =====\n"
    quote = None
    escaped = False
    template_expr = 0
    line_comment = False
    block_comment = False
    depth = 0
    index = brace
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
        elif block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 1
        elif quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif quote == "`" and char == "$" and nxt == "{":
                template_expr += 1
                index += 1
            elif quote == "`" and char == "}" and template_expr:
                template_expr -= 1
            elif char == quote and not template_expr:
                quote = None
        else:
            if char == "/" and nxt == "/":
                line_comment = True
                index += 1
            elif char == "/" and nxt == "*":
                block_comment = True
                index += 1
            elif char in "'\"`":
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    snippet = text[start:end]
                    base = line_number(start)
                    numbered = "\n".join(f"{base + i:06d}: {line}" for i, line in enumerate(snippet.splitlines()))
                    return f"===== {name} at line {base} =====\n{numbered}\n\n"
        index += 1
    return f"===== {name}: UNTERMINATED =====\n"

parts = ["V5_MENU_BOOT_FOCUSED_SLICES\n\n"]
for name in (
    "loadState",
    "normaliseOperationalWindowSettings",
    "installOperationalSuiteShell",
    "operationalSuiteEnabled",
    "scheduleDeferredOperationalStartup",
    "ensureUi",
    "createControl",
    "createPanel",
    "createCleanExit",
    "handleOperationalWindowSettingChange",
    "operationalWindowSyncSettingsUi",
    "operationalQuery",
    "boot",
):
    parts.append(extract_function(name))

for needle in (
    "installOperationalSuiteShell();",
    "ensureUi();",
    "ensureUi()",
    "operationalWindowSettingsMarkup()",
    "handleOperationalWindowSettingChange(",
    "operationalWindowSyncSettingsUi(",
):
    parts.append(f"===== REFERENCES {needle!r} =====\n")
    for index, line in enumerate(lines):
        if needle in line:
            start = max(0, index - 5)
            end = min(len(lines), index + 8)
            for cursor in range(start, end):
                parts.append(f"{cursor + 1:06d}: {lines[cursor]}\n")
            parts.append("\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
