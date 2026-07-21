#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-253-style-formatting-inventory.json"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    function_start = text.find("function installMainStyles()")
    if function_start < 0:
        raise RuntimeError("installMainStyles function not found")
    assignment_marker = "style.textContent = `"
    assignment = text.find(assignment_marker, function_start)
    if assignment < 0:
        raise RuntimeError("main style assignment not found")
    append_anchor = text.find("document.head.appendChild(style)", assignment)
    if append_anchor < 0:
        raise RuntimeError("main style append anchor not found")
    closing = text.rfind("`", assignment + len(assignment_marker), append_anchor)
    if closing < 0:
        raise RuntimeError("main style template closing delimiter not found")
    raw = text[assignment + len(assignment_marker):closing]
    lines = raw.split("\n")
    blank = [index + 1 for index, line in enumerate(lines) if not line.strip()]

    comment_blocks: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped.startswith("/*"):
            index += 1
            continue
        start = index
        block_lines = [lines[index]]
        valid = "${" not in lines[index]
        suffix = stripped[2:]
        if "*/" in suffix:
            after = suffix.split("*/", 1)[1]
            valid = valid and not after.strip()
            end = index
        else:
            end = None
            cursor = index + 1
            while cursor < len(lines):
                block_lines.append(lines[cursor])
                if "${" in lines[cursor]:
                    valid = False
                if "*/" in lines[cursor]:
                    after = lines[cursor].split("*/", 1)[1]
                    valid = valid and not after.strip()
                    end = cursor
                    break
                cursor += 1
            if end is None:
                valid = False
                end = len(lines) - 1
        if valid:
            comment_blocks.append({
                "startLine": start + 1,
                "endLine": end + 1,
                "lines": end - start + 1,
                "preview": " ".join(line.strip() for line in block_lines)[:240],
            })
        index = end + 1

    comment_lines = sum(int(block["lines"]) for block in comment_blocks)
    payload = {
        "schemaVersion": 1,
        "templatePhysicalLines": len(lines),
        "blankLines": len(blank),
        "standaloneCommentBlocks": len(comment_blocks),
        "standaloneCommentLines": comment_lines,
        "totalSafelyRemovableFormattingLines": len(blank) + comment_lines,
        "meetsIssue253Target": len(blank) + comment_lines >= 500,
        "commentBlocks": comment_blocks,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in payload if key != "commentBlocks"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
