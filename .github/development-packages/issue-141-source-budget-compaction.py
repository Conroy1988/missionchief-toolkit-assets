#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VERSION = "4.15.2"


def template_line_flags(lines: list[str]) -> list[bool]:
    """Mirror the repository audit lexer and flag lines that begin inside templates."""
    state = "code"
    quote = ""
    escaped = False
    regex_class = False
    previous_significant = ""
    flags: list[bool] = []

    for line in lines:
        flags.append(state == "string" and quote == "`")
        i = 0
        while i < len(line):
            ch = line[i]
            nxt = line[i + 1] if i + 1 < len(line) else ""
            if state == "line-comment":
                if ch == "\n":
                    state = "code"
                i += 1
                continue
            if state == "block-comment":
                if ch == "*" and nxt == "/":
                    i += 2
                    state = "code"
                else:
                    i += 1
                continue
            if state == "string":
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == quote:
                    state = "code"
                i += 1
                continue
            if state == "regex":
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == "[":
                    regex_class = True
                elif ch == "]":
                    regex_class = False
                elif ch == "/" and not regex_class:
                    state = "regex-flags"
                i += 1
                continue
            if state == "regex-flags":
                if ch.isalpha():
                    i += 1
                else:
                    state = "code"
                continue
            if ch == "/" and nxt == "/":
                i += 2
                state = "line-comment"
                continue
            if ch == "/" and nxt == "*":
                i += 2
                state = "block-comment"
                continue
            if ch in "'\"`":
                quote = ch
                i += 1
                state = "string"
                escaped = False
                continue
            if ch == "/":
                prefix = previous_significant
                if not prefix or prefix[-1] in "([{=,:;!&|?+-*%^~<>" or re.search(
                    r"(?:return|throw|case|delete|void|typeof|instanceof|in|of|yield|await)$",
                    prefix,
                ):
                    i += 1
                    state = "regex"
                    escaped = False
                    regex_class = False
                    continue
            if not ch.isspace():
                previous_significant = (previous_significant + ch)[-32:]
            i += 1
    return flags


def compact_blank_lines(source: str) -> tuple[str, int]:
    lines = source.splitlines(keepends=True)
    template_flags = template_line_flags(lines)
    output: list[str] = []
    removed = 0
    for line, in_template in zip(lines, template_flags, strict=True):
        if not line.strip() and not in_template:
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
    raise AssertionError(f"Compaction removed only {removed} safe blank lines; at least 182 are required")
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
print(f"Issue #141 source compaction removed {removed} safe blank lines; candidate is {remaining_lines} lines and {remaining_bytes} bytes")
