#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "issue530-confirmation-flow.txt"


def function_bounds(source: str, name: str) -> tuple[int, int]:
    markers = [f"    function {name}(", f"    async function {name}("]
    starts = [source.find(marker) for marker in markers]
    starts = [value for value in starts if value >= 0]
    if not starts:
        raise SystemExit(f"Missing function: {name}")
    start = min(starts)
    opening = source.find("{", source.find(")", start))
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
                return start, index + 1
        index += 1
    raise SystemExit(f"Could not find function end: {name}")


def extract_function(source: str, name: str) -> str:
    start, end = function_bounds(source, name)
    return source[start:end]


def extract_runtime(source: str) -> str:
    marker = "    const transportSweepRuntime = {"
    start = source.index(marker)
    end = source.index("\n    };", start) + len("\n    };")
    return source[start:end]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    names = [
        "transportSweepDocumentContexts",
        "transportSweepVisibleWindowRoots",
        "transportSweepElementVisible",
        "captureTransportSweepReleaseConfirmationBaseline",
        "transportSweepReleaseConfirmationVisible",
        "transportSweepReleaseKey",
        "recordTransportSweepConfirmedRelease",
        "recordTransportSweepSkippedPatient",
        "openTransportSweepVehicle",
        "closeTransportSweepWindows",
        "processTransportSweepMission",
        "startTransportSweep",
    ]
    sections = ["===== RUNTIME =====\n" + extract_runtime(source)]
    for name in names:
        sections.append(f"===== {name} =====\n{extract_function(source, name)}")
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
