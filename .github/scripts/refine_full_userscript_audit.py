#!/usr/bin/env python3
"""Refine the conservative userscript audit into a human-reviewable report.

This second stage removes known parser artefacts, recalculates complexity without
counting optional chaining, limits duplicate-name findings to the same lexical
parent and adds exact source excerpts for every actionable item.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

import full_userscript_audit as base

RESERVED = {
    "await", "break", "case", "catch", "class", "const", "continue", "debugger",
    "default", "delete", "do", "else", "export", "extends", "finally", "for",
    "function", "if", "import", "in", "instanceof", "let", "new", "return",
    "super", "switch", "this", "throw", "try", "typeof", "var", "void", "while",
    "with", "yield", "true", "false", "null", "undefined",
}


def corrected_complexity(masked_body: str) -> int:
    patterns = [
        r"\bif\s*\(", r"\bfor\s*(?:await\s*)?\(", r"\bwhile\s*\(",
        r"\bdo\s*\{", r"\bcase\b", r"\bcatch\s*\(",
        r"\?(?![?.])", r"&&", r"\|\|", r"\?\?",
    ]
    return 1 + sum(len(re.findall(pattern, masked_body)) for pattern in patterns)


def excerpt(lines: list[str], line: int | None, radius: int = 4) -> str:
    if not line:
        return ""
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return "\n".join(f"{number}: {lines[number - 1]}" for number in range(start, end + 1))


def lexical_block_parent(masked_source: str, offset: int) -> tuple[int, int] | None:
    """Return the nearest enclosing brace block while preserving source offsets.

    Function extraction is deliberately conservative and may not inventory every
    enclosing function expression. A brace-stack parent therefore provides a more
    reliable same-scope key for local helper names without treating helpers in two
    separate Promise callbacks as duplicates.
    """
    stack: list[int] = []
    for index, character in enumerate(masked_source[:offset]):
        if character == "{":
            stack.append(index)
        elif character == "}" and stack:
            stack.pop()
    if not stack:
        return None
    opening = stack[-1]
    return opening, base.line_number(masked_source, opening)


def finding_key(item: dict) -> tuple:
    return item.get("severity"), item.get("code"), item.get("line"), item.get("subject"), item.get("message")


def refine(raw: dict, source_text: str) -> dict:
    source_lines = source_text.splitlines()
    masked_source = base.mask_non_code(source_text)
    records = [item for item in raw["details"]["functionInventory"] if item["name"] not in RESERVED]

    for item in records:
        body = source_text[item["body_start"]:item["body_end"]]
        item["complexity"] = corrected_complexity(base.mask_non_code(body))
        item["parent"] = lexical_block_parent(masked_source, item["start"])

    findings: list[dict] = []
    empty_catches: list[int] = []
    for original in raw["findings"]:
        item = dict(original)
        if item.get("subject") in RESERVED:
            continue
        if item["code"] in {"duplicate-function-name", "very-high-complexity", "high-complexity", "very-large-function", "large-function"}:
            continue
        if item["code"] == "empty-catch":
            if item.get("line"):
                empty_catches.append(item["line"])
            continue
        if item.get("line") and not item.get("evidence"):
            item["evidence"] = excerpt(source_lines, item["line"])
        findings.append(item)

    by_scope: dict[tuple, list[dict]] = defaultdict(list)
    for record in records:
        by_scope[(tuple(record["parent"]) if record["parent"] else None, record["name"])].append(record)
    for (parent, name), duplicates in sorted(by_scope.items(), key=lambda item: (str(item[0][0]), item[0][1])):
        if len(duplicates) < 2:
            continue
        scope = "top-level Toolkit scope" if parent is None else f"lexical block beginning at line {parent[1]}"
        findings.append({
            "severity": "review",
            "code": "duplicate-function-name-same-scope",
            "message": f"Function-like declaration appears {len(duplicates)} times in the same lexical parent ({scope}).",
            "line": duplicates[0]["line"],
            "subject": name,
            "evidence": ", ".join(str(item["line"]) for item in duplicates),
        })

    for record in records:
        severity = None
        code = None
        message = None
        if record["body_lines"] >= 350:
            severity, code = "review", "very-large-function"
            message = f"Function spans {record['body_lines']} lines and should be reviewed for safe internal extraction."
        elif record["body_lines"] >= 220:
            severity, code = "advisory", "large-function"
            message = f"Function spans {record['body_lines']} lines."
        if severity:
            findings.append({
                "severity": severity, "code": code, "message": message,
                "line": record["line"], "subject": record["name"],
                "evidence": excerpt(source_lines, record["line"]),
            })
        if record["complexity"] >= 80:
            findings.append({
                "severity": "review", "code": "very-high-complexity",
                "message": f"Corrected estimated cyclomatic complexity is {record['complexity']}.",
                "line": record["line"], "subject": record["name"],
                "evidence": excerpt(source_lines, record["line"]),
            })
        elif record["complexity"] >= 45:
            findings.append({
                "severity": "advisory", "code": "high-complexity",
                "message": f"Corrected estimated cyclomatic complexity is {record['complexity']}.",
                "line": record["line"], "subject": record["name"],
                "evidence": excerpt(source_lines, record["line"]),
            })

    if empty_catches:
        findings.append({
            "severity": "advisory",
            "code": "empty-catch-summary",
            "message": (
                f"The userscript contains {len(empty_catches)} empty catch blocks. Many are defensive browser/Leaflet guards; "
                "review only where silent failure would hide a user-visible state transition."
            ),
            "line": empty_catches[0],
            "subject": "defensive exception handling",
            "evidence": "sample lines: " + ", ".join(map(str, empty_catches[:30])),
        })

    unique: dict[tuple, dict] = {}
    for item in findings:
        unique[finding_key(item)] = item
    findings = sorted(
        unique.values(),
        key=lambda item: (
            {"failure": 0, "review": 1, "candidate": 2, "advisory": 3}.get(item["severity"], 9),
            item.get("line") or 10**9,
            item["code"],
        ),
    )

    largest = sorted(records, key=lambda item: item["body_lines"], reverse=True)[:40]
    complex_functions = sorted(records, key=lambda item: item["complexity"], reverse=True)[:40]
    summary = dict(Counter(item["severity"] for item in findings))
    return {
        "schemaVersion": 2,
        "metrics": {**raw["metrics"], "functions": len(records), "named_functions": len(records)},
        "summary": summary,
        "findings": findings,
        "details": {
            **raw["details"],
            "functionInventory": records,
            "largestFunctions": largest,
            "mostComplexFunctions": complex_functions,
            "emptyCatchLines": empty_catches,
        },
    }


def render(report: dict) -> str:
    metrics = report["metrics"]
    summary = report["summary"]
    result = "FAILED" if summary.get("failure") else "PASSED WITH REVIEW ITEMS" if report["findings"] else "PASSED"
    lines = [
        "# Refined Full Userscript Audit",
        "",
        f"- Version: `{report['details'].get('version') or 'unknown'}`",
        f"- SHA-256: `{metrics['sha256']}`",
        f"- Size: `{metrics['bytes']:,}` bytes across `{metrics['lines']:,}` lines",
        f"- Result: `{result}`",
        f"- Findings: failures `{summary.get('failure', 0)}`, review `{summary.get('review', 0)}`, candidates `{summary.get('candidate', 0)}`, advisories `{summary.get('advisory', 0)}`",
        "",
        "## Core workload inventory",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Named function-like blocks | {metrics['functions']:,} |",
        f"| Arrow expressions | {metrics['arrow_functions']:,} |",
        f"| const / let declarations | {metrics['const_declarations'] + metrics['let_declarations']:,} |",
        f"| querySelector / querySelectorAll | {metrics['query_selector_calls'] + metrics['query_selector_all_calls']:,} |",
        f"| getElementById | {metrics['get_element_by_id_calls']:,} |",
        f"| Event listeners added / removed | {metrics['event_listeners_added']:,} / {metrics['event_listeners_removed']:,} |",
        f"| MutationObservers | {metrics['mutation_observers']:,} |",
        f"| Intervals / timeouts | {metrics['intervals_created']:,} / {metrics['timeouts_created']:,} |",
        f"| Generated CSS blocks | {metrics['css_template_blocks']:,} |",
        "",
        "## Largest functions",
        "",
        "| Function | Line | Lines | Corrected complexity | Queries | Listeners | Timers |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["details"]["largestFunctions"][:20]:
        lines.append(
            f"| `{item['name']}` | {item['line']} | {item['body_lines']} | {item['complexity']} | {item['query_calls']} | {item['listener_calls']} | {item['timer_calls']} |"
        )

    for severity in ("failure", "review", "candidate", "advisory"):
        selected = [item for item in report["findings"] if item["severity"] == severity]
        if not selected:
            continue
        lines.extend(["", f"## {severity.title()} findings", ""])
        for item in selected:
            location = f" · line {item['line']}" if item.get("line") else ""
            subject = f" · `{item['subject']}`" if item.get("subject") else ""
            lines.append(f"- **{item['code']}**{location}{subject}: {item['message']}")
            if item.get("evidence"):
                evidence = str(item["evidence"]).replace("```", "```​")
                lines.append("\n```text")
                lines.append(evidence[:2000])
                lines.append("```")

    lines.extend([
        "", "## Safety rule", "",
        "Candidate findings are not proof of dead code. A candidate may be removed only after its complete source block, all identifier references, state contracts and browser/runtime entry paths have been reviewed.", "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    source_text = args.source.read_text(encoding="utf-8")
    report = refine(raw, source_text)
    args.json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render(report), encoding="utf-8")
    print(json.dumps({"result": "failed" if report["summary"].get("failure") else "passed", "summary": report["summary"]}, indent=2))
    return 1 if report["summary"].get("failure") else 0


if __name__ == "__main__":
    raise SystemExit(main())
