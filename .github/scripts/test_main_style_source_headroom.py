#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/main-style-source-headroom.json"
ASSIGNMENT = "style.textContent = `"


def fail(message: str) -> None:
    raise SystemExit(f"MAIN STYLE HEADROOM CONTRACT ERROR: {message}")


def standalone_comment_ranges(lines: list[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    index = 1
    while index < len(lines) - 1:
        stripped = lines[index].strip()
        if not stripped.startswith("/*"):
            index += 1
            continue
        start = index
        end = index
        valid = "${" not in lines[index]
        remainder = stripped[2:]
        if "*/" in remainder:
            valid = valid and not remainder.split("*/", 1)[1].strip()
        else:
            found = False
            cursor = index + 1
            while cursor < len(lines) - 1:
                end = cursor
                if "${" in lines[cursor]:
                    valid = False
                if "*/" in lines[cursor]:
                    valid = valid and not lines[cursor].split("*/", 1)[1].strip()
                    found = True
                    break
                cursor += 1
            if not found:
                valid = False
        if valid:
            ranges.append((start, end))
        index = end + 1
    return ranges


def canonical_css_formatting(raw: str) -> str:
    lines = raw.split("\n")
    removable = {index for index in range(1, len(lines) - 1) if not lines[index].strip()}
    for start, end in standalone_comment_ranges(lines):
        removable.update(range(start, end + 1))
    stripped = "\n".join(line for index, line in enumerate(lines) if index not in removable)
    return re.sub(r"\n[\t ]*}", "}", stripped)


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    text = SOURCE.read_text(encoding="utf-8")
    function_start = text.find("function installMainStyles()")
    if function_start < 0:
        fail("installMainStyles function is missing")
    add_style = text.find("addStyle(`", function_start)
    if add_style < 0:
        fail("installMainStyles addStyle template opening is missing")
    template_start = add_style + len("addStyle(`")
    end_anchor = text.find("recordStartupMetric('stylesheetInstallMs'", template_start)
    if end_anchor < 0:
        fail("installMainStyles startup metric anchor is missing")
    closing = text.rfind("`);", template_start, end_anchor)
    if closing < 0:
        fail("installMainStyles addStyle template closing is missing")
    raw = text[template_start:closing]
    if len(raw.encode("utf-8")) <= 800000:
        fail("reviewed main stylesheet template is unexpectedly small")
    lines = raw.split("\n")
    interior_blank = [index + 1 for index, line in enumerate(lines[1:-1], 1) if not line.strip()]
    if interior_blank:
        fail(f"blank physical lines returned inside installMainStyles: {interior_blank[:10]}")
    comments = standalone_comment_ranges(lines)
    if comments:
        fail(f"standalone full-line CSS comments returned inside installMainStyles: {comments[:5]}")
    candidate_template_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if candidate_template_hash != fixture["candidateTemplateSha256"]:
        fail("exact candidate stylesheet template differs from the reviewed fixture")
    canonical_hash = hashlib.sha256(canonical_css_formatting(raw).encode("utf-8")).hexdigest()
    if canonical_hash != fixture["canonicalCssSha256"]:
        fail("canonical CSS content differs from the reviewed fixture")
    if len(lines) != fixture["candidateTemplateLines"]:
        fail("candidate stylesheet template line count differs from the reviewed fixture")
    split_lines = re.split(r"\r?\n", text)
    source_lines = len(split_lines) - 1 if text.endswith("\n") else len(split_lines)
    if source_lines != fixture["candidateSourceLines"]:
        fail(f"candidate source line count changed: {source_lines} != {fixture['candidateSourceLines']}")
    if fixture["originalSourceLines"] - fixture["candidateSourceLines"] != fixture["recoveredSourceLines"]:
        fail("fixture source-line arithmetic is inconsistent")
    if fixture["removedBlankLines"] + fixture["removedStandaloneCommentLines"] + fixture["joinedClosingBraceLines"] != fixture["recoveredSourceLines"]:
        fail("fixture formatting-category arithmetic is inconsistent")
    if fixture["joinedClosingBraceLines"] != 15:
        fail("reviewed closing-brace join count changed")
    if fixture["recoveredSourceLines"] < 500:
        fail("reviewed implementation recovered fewer than 500 lines")
    version = re.search(r"^//\s*@version\s+([^\s]+)", text, re.MULTILINE)
    if not version or version.group(1) != fixture["candidateVersion"]:
        fail("userscript version does not match the reviewed source-headroom fixture")
    print(
        "Main-style source-headroom contract passed: "
        f"{fixture['recoveredSourceLines']} lines recovered "
        f"({fixture['removedBlankLines']} blank, "
        f"{fixture['removedStandaloneCommentLines']} standalone comment, "
        f"{fixture['joinedClosingBraceLines']} closing-brace joins), "
        f"{fixture['candidateSourceLines']} source lines remain."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
