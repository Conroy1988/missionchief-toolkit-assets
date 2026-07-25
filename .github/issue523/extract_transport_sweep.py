#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "issue523-transport-sweep-diagnostic.txt"


def extract_function(source: str, name: str) -> str:
    patterns = [f"    function {name}(", f"    async function {name}("]
    starts = [source.find(pattern) for pattern in patterns]
    starts = [index for index in starts if index >= 0]
    if not starts:
        return f"[missing function: {name}]\n"
    start = min(starts)
    opening = source.find("{", start)
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = opening
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char in {"'", '"', "`"}:
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1] + "\n"
        index += 1
    return f"[unterminated function: {name}]\n"


def context(source: str, needle: str, before: int = 700, after: int = 2200) -> str:
    index = source.find(needle)
    if index < 0:
        return f"[missing context: {needle}]\n"
    return source[max(0, index - before):min(len(source), index + after)] + "\n"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    sections: list[str] = []

    sections.append("=== TRANSPORT SWEEP RUNTIME DECLARATION ===\n")
    runtime_match = re.search(r"(?:const|let) transportSweepRuntime\s*=\s*\{", source)
    if runtime_match:
        sections.append(source[max(0, runtime_match.start() - 300):runtime_match.start() + 2600] + "\n")
    else:
        sections.append("[runtime declaration not found]\n")

    for name in [
        "ensureTransportSweepHud",
        "renderTransportSweepHud",
        "removeTransportSweepHud",
        "renderTransportSweepPanel",
        "renderTransportSweep",
        "transportSweepSummary",
        "processTransportSweepMission",
        "startTransportSweep",
        "cancelTransportSweep",
        "finishTransportSweep",
    ]:
        sections.append(f"\n=== FUNCTION {name} ===\n")
        sections.append(extract_function(source, name))

    sections.append("\n=== ALL TRANSPORT SWEEP RUNTIME MUTATIONS ===\n")
    lines = source.splitlines()
    for number, line in enumerate(lines, start=1):
        lower = line.lower()
        if "transportsweepruntime" in lower or "rendertransportsweephud" in lower:
            sections.append(f"{number:05d}: {line}\n")

    sections.append("\n=== MISSION/QUEUE PROGRESS TERMS NEAR TRANSPORT SWEEP ===\n")
    for number, line in enumerate(lines, start=1):
        lower = line.lower()
        if "transport" not in lower and "sweep" not in lower:
            continue
        if any(term in lower for term in ["missionindex", "currentmission", "totalmissions", "queue", "missionnumber", "missions:"]):
            sections.append(f"{number:05d}: {line}\n")

    sections.append("\n=== HUD STRING CONTEXT ===\n")
    sections.append(context(source, "Missions:"))

    OUTPUT.write_text("".join(sections), encoding="utf-8")
    print(OUTPUT.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
