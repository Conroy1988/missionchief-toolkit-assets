#!/usr/bin/env python3
"""Produce exact source evidence for Toolkit/LSSM coexistence ownership.

This diagnostic is intentionally read-only. It inventories the v6 Operational
Window lifecycle, observer and scheduler call sites, LSSM detection/suppression
logic, and feature-state guards so Issue #512 can be fixed from evidence.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
JSON_OUT = ROOT / "issue512-lssm-coexistence-report.json"
MD_OUT = ROOT / "issue512-lssm-coexistence-report.md"


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def excerpt(lines: list[str], line: int, before: int = 8, after: int = 14) -> str:
    start = max(1, line - before)
    end = min(len(lines), line + after)
    return "\n".join(f"{number}: {lines[number - 1]}" for number in range(start, end + 1))


def match_function_block(source: str, start: int) -> tuple[int, str] | None:
    opening = source.find("{", start)
    if opening < 0:
        return None
    depth = 0
    quote = ""
    escaped = False
    state = "code"
    index = opening
    while index < len(source):
        ch = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if state == "line-comment":
            if ch == "\n":
                state = "code"
            index += 1
            continue
        if state == "block-comment":
            if ch == "*" and nxt == "/":
                state = "code"
                index += 2
            else:
                index += 1
            continue
        if state == "string":
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                state = "code"
            index += 1
            continue
        if ch == "/" and nxt == "/":
            state = "line-comment"
            index += 2
            continue
        if ch == "/" and nxt == "*":
            state = "block-comment"
            index += 2
            continue
        if ch in "'\"`":
            quote = ch
            state = "string"
            index += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return index + 1, source[start:index + 1]
        index += 1
    return None


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines()

    keywords = [
        "lssm", "operationalFeature", "operationalWindow", "scheduleOperational",
        "MutationObserver", "runtimeTrackObserver", "runtimeListen", "runtimeSetTimeout",
        "data-lssm", "lssmv4", "missing_text", "transport", "missionList",
    ]
    keyword_hits: dict[str, list[int]] = {}
    for keyword in keywords:
        keyword_hits[keyword] = [
            line_number(source, match.start())
            for match in re.finditer(re.escape(keyword), source, re.I)
        ]

    function_pattern = re.compile(r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
    selected_functions: list[dict[str, object]] = []
    function_names: list[str] = []
    for match in function_pattern.finditer(source):
        name = match.group(1)
        function_names.append(name)
        lowered = name.casefold()
        if not any(token in lowered for token in ("operational", "lssm", "transport", "missionlist", "requirement")):
            continue
        block = match_function_block(source, match.start())
        if block is None:
            continue
        end, body = block
        calls = len(re.findall(rf"(?<!function\s)\b{re.escape(name)}\s*\(", source))
        selected_functions.append({
            "name": name,
            "line": line_number(source, match.start()),
            "endLine": line_number(source, end),
            "callOccurrences": calls,
            "containsMutationObserver": "MutationObserver" in body,
            "containsDocumentQuery": "document.querySelector" in body or "doc.querySelector" in body,
            "containsLssm": bool(re.search(r"lssm", body, re.I)),
            "containsStateGuard": bool(re.search(r"state\.|operationalWindowState|enabled", body)),
            "body": body,
        })

    observer_sites = []
    for match in re.finditer(r"(?:new\s+)?(?:pageWindow\.)?MutationObserver\s*\(", source):
        line = line_number(source, match.start())
        observer_sites.append({"line": line, "excerpt": excerpt(lines, line)})

    scheduler_sites = []
    scheduler_pattern = re.compile(
        r"\b(?:schedule[A-Za-z0-9_$]*|runtimeSetTimeout|runtimeRequestAnimationFrame|runtimeTrackObserver)\s*\("
    )
    for match in scheduler_pattern.finditer(source):
        line = line_number(source, match.start())
        context = "\n".join(lines[max(0, line - 4):min(len(lines), line + 4)])
        if re.search(r"operational|lssm|mission|transport|requirement", context, re.I):
            scheduler_sites.append({
                "token": match.group(0).split("(", 1)[0],
                "line": line,
                "excerpt": excerpt(lines, line, 5, 8),
            })

    feature_guard_lines = []
    for number, raw in enumerate(lines, 1):
        if re.search(r"operational|lssm", raw, re.I) and re.search(
            r"enabled|disabled|suppress|visible|active|return|cleanup|destroy|disconnect", raw, re.I
        ):
            feature_guard_lines.append({"line": number, "text": raw.rstrip()})

    lssm_owned_selectors = []
    selector_pattern = re.compile(r"(['\"])([^'\"]*(?:lssm|lssmv4)[^'\"]*)\1", re.I)
    for match in selector_pattern.finditer(source):
        lssm_owned_selectors.append({
            "line": line_number(source, match.start()),
            "value": match.group(2),
        })

    function_counter = Counter(function_names)
    duplicate_function_names = {name: count for name, count in function_counter.items() if count > 1}

    report = {
        "source": str(SOURCE.relative_to(ROOT)),
        "version": re.search(r"(?m)^//\s*@version\s+([^\s]+)", source).group(1),
        "sourceLines": len(lines),
        "keywordHits": keyword_hits,
        "observerSites": observer_sites,
        "schedulerSites": scheduler_sites,
        "featureGuardLines": feature_guard_lines,
        "lssmOwnedSelectors": lssm_owned_selectors,
        "selectedFunctions": [
            {key: value for key, value in item.items() if key != "body"}
            for item in selected_functions
        ],
        "duplicateFunctionNames": duplicate_function_names,
    }
    JSON_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md: list[str] = [
        "# Issue #512 Toolkit/LSSM coexistence diagnostic",
        "",
        f"- Toolkit version: **{report['version']}**",
        f"- Source lines: **{report['sourceLines']:,}**",
        f"- MutationObserver construction sites: **{len(observer_sites)}**",
        f"- Relevant scheduler sites: **{len(scheduler_sites)}**",
        f"- Selected operational/LSSM functions: **{len(selected_functions)}**",
        f"- LSSM selector/string references: **{len(lssm_owned_selectors)}**",
        "",
        "## Keyword inventory",
        "",
    ]
    for keyword, hits in keyword_hits.items():
        md.append(f"- `{keyword}`: {len(hits)} hits" + (f" — lines {', '.join(map(str, hits[:30]))}" if hits else ""))

    md.extend(["", "## LSSM-owned selectors and markers", ""])
    for item in lssm_owned_selectors:
        md.append(f"- Line {item['line']}: `{item['value']}`")

    md.extend(["", "## Feature-state, suppression and teardown lines", ""])
    for item in feature_guard_lines:
        md.append(f"- {item['line']}: `{str(item['text']).strip()}`")

    md.extend(["", "## MutationObserver sites", ""])
    for item in observer_sites:
        md.extend([f"### Line {item['line']}", "", "```javascript", item["excerpt"], "```", ""])

    md.extend(["", "## Relevant scheduler sites", ""])
    for item in scheduler_sites:
        md.extend([
            f"### `{item['token']}` at line {item['line']}", "", "```javascript",
            item["excerpt"], "```", "",
        ])

    md.extend(["", "## Operational/LSSM function bodies", ""])
    for item in selected_functions:
        md.extend([
            f"### `{item['name']}` — lines {item['line']}-{item['endLine']}",
            "",
            f"Call occurrences: **{item['callOccurrences']}** · "
            f"observer: **{item['containsMutationObserver']}** · "
            f"LSSM reference: **{item['containsLssm']}** · "
            f"state guard: **{item['containsStateGuard']}**",
            "",
            "```javascript",
            item["body"],
            "```",
            "",
        ])

    if duplicate_function_names:
        md.extend(["", "## Duplicate function declarations", ""])
        for name, count in duplicate_function_names.items():
            md.append(f"- `{name}`: {count}")

    MD_OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({
        "version": report["version"],
        "observerSites": len(observer_sites),
        "relevantSchedulers": len(scheduler_sites),
        "selectedFunctions": len(selected_functions),
        "lssmMarkers": len(lssm_owned_selectors),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
