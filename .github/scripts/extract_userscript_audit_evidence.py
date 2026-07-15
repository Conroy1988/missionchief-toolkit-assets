#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import full_userscript_audit as base

TARGET_RULES = {
    "no-unused-vars",
    "no-useless-assignment",
    "no-extra-boolean-cast",
    "no-promise-executor-return",
    "no-unmodified-loop-condition",
    "require-atomic-updates",
    "no-await-in-loop",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--eslint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def excerpt(lines: list[str], line: int, before: int = 8, after: int = 12) -> str:
    start = max(1, line - before)
    end = min(len(lines), line + after)
    return "\n".join(f"{number}: {lines[number - 1]}" for number in range(start, end + 1))


def fenced(text: str) -> list[str]:
    return ["```javascript", text.replace("```", "```​"), "```"]


def main() -> int:
    args = parse_args()
    source = args.source.read_text(encoding="utf-8")
    lines = source.splitlines()
    eslint = json.loads(args.eslint.read_text(encoding="utf-8"))
    messages = eslint.get("messages", [])
    masked = base.mask_non_code(source)
    functions = base.extract_functions(source, masked)
    by_name = defaultdict(list)
    for function in functions:
        by_name[function.name].append(function)

    unused_names = []
    for item in messages:
        if item.get("ruleId") != "no-unused-vars":
            continue
        match = re.search(r"'([^']+)'", item.get("message", ""))
        if match:
            unused_names.append(match.group(1))

    output = [
        "# Exact userscript audit evidence",
        "",
        "This file contains source evidence only. It does not authorise automatic removal.",
        "",
        "## Unused binding verification",
        "",
    ]

    for name in unused_names:
        occurrences = [
            base.line_number(source, match.start())
            for match in re.finditer(rf"(?<![A-Za-z0-9_$]){re.escape(name)}(?![A-Za-z0-9_$])", source)
        ]
        output.extend([
            f"### `{name}`",
            "",
            f"Raw identifier occurrences: **{len(occurrences)}** at lines: {', '.join(map(str, occurrences)) or 'none'}",
            "",
        ])
        for line in occurrences:
            output.extend(fenced(excerpt(lines, line, 4, 6)))
            output.append("")
        for record in by_name.get(name, []):
            block = source[record.start:record.body_end + 1]
            output.extend([
                f"Complete function-like block from line {record.line} ({record.body_lines} lines):",
                "",
                *fenced(block),
                "",
            ])

    output.extend(["", "## Actionable ESLint findings", ""])
    for item in messages:
        if item.get("ruleId") not in TARGET_RULES or not item.get("line"):
            continue
        output.extend([
            f"### `{item['ruleId']}` · line {item['line']}:{item.get('column') or 1}",
            "",
            item.get("message", ""),
            "",
            *fenced(excerpt(lines, int(item["line"]))),
            "",
        ])

    selected_ranges = [
        (420, 475, "Alliance suppression assignment restoration"),
        (680, 735, "Runtime task scheduler registration"),
        (1140, 1255, "Runtime render and media state"),
        (1300, 1345, "Discord finance state"),
        (14155, 14210, "Mission marker matching"),
        (14555, 14610, "Mission watcher compatibility wrappers"),
        (15870, 16190, "Transport sweep asynchronous lifecycle"),
        (16735, 16780, "Personal building marker class synchronisation"),
        (17100, 17145, "Map event state assignments"),
        (19350, 19390, "Vehicle status assignment"),
        (20390, 20425, "Critical drawer refresh lifecycle"),
        (20815, 20865, "Critical view async lifecycle"),
        (22770, 22815, "Discord finance chart references"),
        (23145, 23205, "First Promise executor"),
        (23615, 23665, "Second local finish helper"),
        (23780, 23820, "Discord reporting loop"),
        (23995, 24040, "Financial ledger assignment"),
        (24185, 24245, "Financial archive async lifecycle"),
        (25125, 25190, "Chart Promise executor and async loop"),
        (25235, 25270, "Discord finance finalisation"),
        (25550, 25590, "Feature toggle assignment"),
        (27435, 27525, "Mutation observer targeting"),
        (27555, 27620, "Boot timer and startup"),
    ]
    output.extend(["", "## Selected lifecycle and optimisation regions", ""])
    for start, end, title in selected_ranges:
        output.extend([
            f"### {title} · lines {start}-{end}",
            "",
            *fenced("\n".join(f"{number}: {lines[number - 1]}" for number in range(start, min(end, len(lines)) + 1))),
            "",
        ])

    args.output.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(json.dumps({"unusedBindings": unused_names, "eslintEvidenceItems": sum(1 for item in messages if item.get('ruleId') in TARGET_RULES)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
