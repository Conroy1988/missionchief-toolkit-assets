#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / ".github" / "diagnostics" / "issue-144-source-budget.txt"
OLD_PAYLOAD = ROOT / ".github" / "development-packages" / "issue-141-source-budget-compaction.payload.py"
REMOVE_COUNT = 182
VERSION = "4.15.2"


def template_line_flags(lines: list[str]) -> list[bool]:
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


def indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def compact_nested_blank_lines(source: str) -> tuple[str, list[int]]:
    lines = source.splitlines(keepends=True)
    template_flags = template_line_flags(lines)
    previous_nonblank: list[int | None] = [None] * len(lines)
    next_nonblank: list[int | None] = [None] * len(lines)
    previous: int | None = None
    for index, line in enumerate(lines):
        previous_nonblank[index] = previous
        if line.strip():
            previous = index
    following: int | None = None
    for index in range(len(lines) - 1, -1, -1):
        next_nonblank[index] = following
        if lines[index].strip():
            following = index

    candidates: list[int] = []
    for index, line in enumerate(lines):
        if line.strip() or template_flags[index]:
            continue
        left = previous_nonblank[index]
        right = next_nonblank[index]
        if left is None or right is None:
            continue
        left_line = lines[left]
        right_line = lines[right]
        right_code = right_line.strip()
        if min(indent(left_line), indent(right_line)) < 8:
            continue
        if re.match(r"^(?:async\s+)?function\b|^class\b", right_code):
            continue
        candidates.append(index)

    if len(candidates) < REMOVE_COUNT:
        raise AssertionError(
            f"Only {len(candidates)} nested non-template blank lines are safely removable; {REMOVE_COUNT} required"
        )
    selected = set(candidates[-REMOVE_COUNT:])
    compacted = "".join(line for index, line in enumerate(lines) if index not in selected)
    if source.endswith("\n") and not compacted.endswith("\n"):
        compacted += "\n"
    return compacted, sorted(selected)


def run_preflight() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", ".github/scripts/run_userscript_preflight.sh"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


original = SOURCE.read_text(encoding="utf-8")
if f"// @version      {VERSION}" not in original or f"version: '{VERSION}'" not in original:
    raise AssertionError(f"Issue #144 compaction expects Toolkit v{VERSION}")

REPORT.unlink(missing_ok=True)
OLD_PAYLOAD.unlink(missing_ok=True)

try:
    compacted, removed_indexes = compact_nested_blank_lines(original)
    compacted_lines = len(compacted.splitlines())
    compacted_bytes = len(compacted.encode("utf-8"))
    if compacted_lines > 31000:
        raise AssertionError(f"Targeted compaction leaves {compacted_lines} lines")
    if compacted_bytes > 1900000:
        raise AssertionError(f"Targeted compaction leaves {compacted_bytes} bytes")
    SOURCE.write_text(compacted, encoding="utf-8")
    preflight = run_preflight()
    if preflight.returncode != 0:
        SOURCE.write_text(original, encoding="utf-8")
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            "Issue #144 targeted source-budget diagnostic\n"
            "============================================\n\n"
            f"Removed candidate lines: {len(removed_indexes)}\n"
            f"Compacted lines: {compacted_lines}\n"
            f"Compacted bytes: {compacted_bytes}\n"
            f"Preflight return code: {preflight.returncode}\n\n"
            "Bounded output:\n\n"
            + preflight.stdout[-16000:]
            + "\n",
            encoding="utf-8",
        )
        print("Targeted compaction was restored after preflight failure; diagnostic recorded")
    else:
        print(
            f"Targeted compaction retained: removed {len(removed_indexes)} nested blank lines; "
            f"candidate is {compacted_lines} lines and {compacted_bytes} bytes; full preflight passed"
        )
except BaseException as error:
    SOURCE.write_text(original, encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "Issue #144 targeted source-budget diagnostic\n"
        "============================================\n\n"
        f"{type(error).__name__}: {error}\n",
        encoding="utf-8",
    )
    print(f"Targeted compaction was restored after {type(error).__name__}; diagnostic recorded")
