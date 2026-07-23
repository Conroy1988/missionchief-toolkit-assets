#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue464-runtime-settings.txt"

text = SOURCE.read_text(encoding="utf-8")


def line_number(offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def matching_brace(open_pos: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    i = open_pos
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise SystemExit(f"Unclosed brace starting at line {line_number(open_pos)}")


def function_block(name: str) -> str:
    pattern = re.compile(rf"(?m)^\s*function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{")
    match = pattern.search(text)
    if not match:
        return f"[missing function: {name}]"
    open_pos = text.find("{", match.start(), match.end())
    close_pos = matching_brace(open_pos)
    start_line = line_number(match.start())
    end_line = line_number(close_pos)
    return f"// lines {start_line}-{end_line}\n{text[match.start():close_pos + 1]}"


def context(needle: str, before: int = 35, after: int = 80) -> str:
    offset = text.find(needle)
    if offset < 0:
        return f"[missing context: {needle}]"
    lines = text.splitlines()
    center = line_number(offset)
    start = max(1, center - before)
    end = min(len(lines), center + after)
    body = "\n".join(f"{index:05d}: {lines[index - 1]}" for index in range(start, end + 1))
    return f"// context for {needle!r}; lines {start}-{end}\n{body}"


function_names = [
    "defaultOperationalWindowState",
    "normaliseOperationalWindowState",
    "operationalWindowSettingsMarkup",
    "operationalWindowSyncSettingsUi",
    "handleOperationalWindowSettingChange",
    "scheduleOperationalSuiteScan",
    "installOperationalSuiteShell",
    "runBootIntegration",
    "startBootAttemptCoordinator",
    "registerBootMaintenanceTasks",
    "ensureUi",
    "boot",
    "scheduleBoot",
]

sections: list[str] = []
sections.append("ISSUE #464 TOOLKIT RUNTIME AND SETTINGS DIAGNOSTIC")
sections.append(f"source_bytes={len(text.encode('utf-8'))}")
sections.append(f"source_lines={len(text.splitlines())}")
sections.append("")

for needle in (
    "const OPERATIONAL_SUITE_SETTINGS_VERSION",
    "Toolkit-native operational controls",
    "data-operational-setting",
    "function operationalWindowSettingsMarkup",
    "function ensureUi",
    "function startBootAttemptCoordinator",
):
    sections.extend(["\n" + "=" * 100, context(needle)])

for name in function_names:
    sections.extend(["\n" + "=" * 100, f"FUNCTION: {name}", function_block(name)])

# Inventory the settings currently emitted by the Toolkit markup and the state keys
# currently present in the operational defaults. This makes label-only and unmapped
# controls explicit without mutating production source.
markup = function_block("operationalWindowSettingsMarkup")
defaults = function_block("defaultOperationalWindowState")
setting_keys = sorted(set(re.findall(r'data-operational-setting=["\']([^"\']+)', markup)))
default_keys = sorted(set(re.findall(r"(?m)^\s{8,}([A-Za-z_$][\w$]*)\s*:", defaults)))
sections.extend([
    "\n" + "=" * 100,
    "CURRENT SETTINGS INVENTORY",
    json.dumps({
        "renderedDataOperationalSettings": setting_keys,
        "defaultOperationalWindowKeys": default_keys,
        "renderedCount": len(setting_keys),
        "defaultCount": len(default_keys),
    }, indent=2),
])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(sections) + "\n", encoding="utf-8")
SELF.unlink(missing_ok=True)
print(json.dumps({"diagnostic": str(OUTPUT.relative_to(ROOT)), "functions": function_names}, indent=2))
