#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VERSION = "4.15.2"


def next_lexical_state(line: str, state: str) -> str:
    """Track only constructs that may legally span physical lines."""
    i = 0
    escaped = False
    while i < len(line):
        char = line[i]
        nxt = line[i + 1] if i + 1 < len(line) else ""
        if state == "block-comment":
            if char == "*" and nxt == "/":
                state = "code"
                i += 2
                continue
            i += 1
            continue
        if state in {"single", "double", "template"}:
            if escaped:
                escaped = False
                i += 1
                continue
            if char == "\\":
                escaped = True
                i += 1
                continue
            if state == "single" and char == "'":
                state = "code"
            elif state == "double" and char == '"':
                state = "code"
            elif state == "template" and char == "`":
                state = "code"
            i += 1
            continue
        if char == "/" and nxt == "/":
            break
        if char == "/" and nxt == "*":
            state = "block-comment"
            i += 2
            continue
        if char == "'":
            state = "single"
        elif char == '"':
            state = "double"
        elif char == "`":
            state = "template"
        i += 1
    return state


def compact_blank_lines(source: str) -> tuple[str, int]:
    lines = source.splitlines(keepends=True)
    output: list[str] = []
    state = "code"
    removed = 0
    for line in lines:
        state_before = state
        state = next_lexical_state(line, state)
        if not line.strip() and state_before != "template":
            removed += 1
            continue
        output.append(line)
    compacted = "".join(output)
    if source.endswith("\n") and not compacted.endswith("\n"):
        compacted += "\n"
    return compacted, removed


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


source = SOURCE.read_text(encoding="utf-8")
if f"// @version      {VERSION}" not in source or f"version: '{VERSION}'" not in source:
    raise AssertionError(f"Issue #141 compaction expects Toolkit v{VERSION}")
compacted, removed = compact_blank_lines(source)
remaining_lines = len(compacted.splitlines())
remaining_bytes = len(compacted.encode("utf-8"))
if removed < 182:
    raise AssertionError(f"Compaction removed only {removed} blank lines; at least 182 are required")
if remaining_lines > 31000:
    raise AssertionError(f"Compacted source still has {remaining_lines} lines")
if remaining_bytes > 1900000:
    raise AssertionError(f"Compacted source still has {remaining_bytes} bytes")
if "    // Issue #133 clean-room live mission requirements matrix." not in compacted:
    raise AssertionError("Mission Requirements runtime extraction marker was lost")
SOURCE.write_text(compacted, encoding="utf-8")
run("node", "--check", str(SOURCE))
run("node", str(ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"))
run(sys.executable, str(ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"))
print(f"Issue #141 source compaction removed {removed} non-template blank lines; candidate is {remaining_lines} lines and {remaining_bytes} bytes")
