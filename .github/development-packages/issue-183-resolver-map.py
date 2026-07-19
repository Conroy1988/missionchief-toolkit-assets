#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-183-resolver-map.txt"
text = SOURCE.read_text(encoding="utf-8")


def function_names(prefix: str) -> list[str]:
    return sorted(set(re.findall(rf"\bfunction\s+({re.escape(prefix)}[A-Za-z0-9_]*)\s*\(", text)))


def extract(name: str) -> str:
    match = re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", text)
    if not match:
        return f"[NOT FOUND] {name}\n"
    start = match.start()
    brace = text.find("{", match.end())
    depth = 0
    quote = None
    escaped = False
    regex_mode = False
    i = brace
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if quote:
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if regex_mode:
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == "/": regex_mode = False
            i += 1; continue
        if ch in "'\"`": quote = ch
        elif ch == "/" and nxt == "/":
            end = text.find("\n", i + 2); i = len(text) if end < 0 else end; continue
        elif ch == "/" and nxt == "*":
            end = text.find("*/", i + 2); i = len(text) if end < 0 else end + 2; continue
        elif ch == "/" and (i == 0 or text[i - 1] in "(=:[,!&|?{};\n "):
            regex_mode = True
        elif ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return text[start:i + 1] + "\n"
        i += 1
    return f"[UNTERMINATED] {name}\n"

names = []
for prefix in ["missionRequirementsCatalogue", "missionRequirementsResolve", "missionRequirementsRecord", "missionRequirementsCreate", "missionRequirementsUpdate", "missionRequirementsPanelHtml"]:
    names.extend(function_names(prefix))
names = sorted(set(names))

out = ["FUNCTIONS:\n", *[f"- {name}\n" for name in names]]
for name in names:
    out.append(f"\n===== {name} =====\n")
    out.append(extract(name))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(out), encoding="utf-8")
print(OUTPUT.relative_to(ROOT))
