#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import full_userscript_audit as audit  # noqa: E402

SOURCE_PATH = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT_PATH = ROOT / ".github" / "reports" / "issue-64-boot-coordinator-inspection.md"


def extract_function(source: str, masked: str, name: str) -> tuple[int, int, str]:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name!r}, found {len(matches)}")
    match = matches[0]
    parameter_open = masked.find("(", match.start())
    depth = 0
    parameter_close = None
    for index in range(parameter_open, len(masked)):
        char = masked[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                parameter_close = index
                break
    if parameter_close is None:
        raise AssertionError(f"Parameter list did not close for {name}")
    opening = masked.find("{", parameter_close + 1)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Unable to match body for {name}")
    return match.start(), closing + 1, source[match.start():closing + 1]


def line_number(source: str, index: int) -> int:
    return source.count("\n", 0, index) + 1


def fenced(title: str, source: str, start: int, end: int, text: str) -> str:
    first = line_number(source, start)
    last = line_number(source, end)
    return f"## {title}\n\nLines `{first}-{last}` · {last - first + 1} lines\n\n```javascript\n{text}\n```\n"


def main() -> int:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    masked = audit.mask_non_code(source)

    boot_start, boot_end, boot_text = extract_function(source, masked, "boot")
    schedule_start, schedule_end, schedule_text = extract_function(source, masked, "scheduleBoot")

    bootstrap_start = source.rfind("if (document.readyState === 'loading')")
    bootstrap_end = source.rfind("})();")
    if bootstrap_start < 0 or bootstrap_end <= bootstrap_start:
        raise AssertionError("Document-start bootstrap tail not found")
    bootstrap_text = source[bootstrap_start:bootstrap_end]

    report = [
        "# Issue #64 boot coordinator inspection",
        "",
        "Generated from the exact canonical userscript on the isolated extraction branch.",
        "No Toolkit runtime or distribution file is changed by this inspection.",
        "",
        fenced("`boot()`", source, boot_start, boot_end, boot_text),
        fenced("`scheduleBoot()`", source, schedule_start, schedule_end, schedule_text),
        fenced("Document-start bootstrap tail", source, bootstrap_start, bootstrap_end, bootstrap_text),
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
