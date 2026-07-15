#!/usr/bin/env python3
"""Apply mechanically verified, behaviour-preserving userscript audit fixes.

Every replacement is assertion-backed. The script aborts rather than making a
partial edit when the audited source no longer matches the expected text.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


def replace_exact(text: str, old: str, new: str, label: str, expected: int = 1) -> tuple[str, int]:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} exact occurrence(s), found {count}")
    return text.replace(old, new), count


def remove_function(text: str, name: str) -> tuple[str, int]:
    match = re.search(rf"(?m)^    function {re.escape(name)}\s*\([^\n]*\)\s*\{{", text)
    if not match:
        raise SystemExit(f"dead function {name}: declaration not found")
    open_pos = text.find("{", match.start(), match.end())
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    index = open_pos
    while index < len(text):
        ch = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            index += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if ch in "'\"`":
            quote = ch
            index += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                if text[end:end + 2] == "\n\n":
                    end += 1
                return text[:match.start()] + text[end:], 1
        index += 1
    raise SystemExit(f"dead function {name}: closing brace not found")


def transform(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    for name in (
        "runtimeUnregisterTask",
        "missionWatchType",
        "missionWatchTypeLabel",
        "synchronisePersonalBuildingMarkerClasses",
    ):
        text, _ = remove_function(text, name)
        changes.append(f"removed proven-unreferenced function {name}")

    replacements = [
        ("    let operationalRenderSignature = '';\n", "", "remove write-only operationalRenderSignature declaration"),
        ("        operationalRenderSignature = summarySignature;\n", "", "remove write-only operationalRenderSignature assignment"),
        ("    let discordPreviewRenderSignature = '';\n", "", "remove write-only discordPreviewRenderSignature declaration"),
        ("        discordPreviewRenderSignature = '';\n", "", "remove write-only discordPreviewRenderSignature assignment"),
        ("    let payoutMediaPrimed = false;\n", "", "remove write-only payoutMediaPrimed declaration"),
        ("        payoutMediaPrimed = false;\n", "", "remove payoutMediaPrimed reset", 2),
        ("            payoutMediaPrimed = true;\n", "", "remove payoutMediaPrimed success assignment"),
        ("    let discordFinancePreview = null;\n", "", "remove write-only discordFinancePreview declaration"),
        ("        discordFinancePreview = null;\n", "", "remove discordFinancePreview assignments", 2),
        ("    let discordFinanceChartBlobRef = null;\n", "", "remove write-only discordFinanceChartBlobRef declaration"),
        ("        discordFinanceChartBlobRef = null;\n", "", "remove discordFinanceChartBlobRef assignment"),
        ("        let bootTimer = null;\n", "", "remove write-only bootTimer declaration"),
        ("            bootTimer = null;\n", "", "remove write-only bootTimer reset"),
        ("            bootTimer = runtimeSetTimeout(runBootAttempt, delay);\n", "            runtimeSetTimeout(runBootAttempt, delay);\n", "schedule boot retry without write-only handle"),
        ("        bootTimer = runtimeSetTimeout(runBootAttempt, 250);\n", "        runtimeSetTimeout(runBootAttempt, 250);\n", "schedule initial boot attempt without write-only handle"),
        ("        let match;\n        while ((match = matcher.exec(content))) {\n", "        while (matcher.exec(content)) {\n", "remove unused mission marker regex binding"),
        ("            if (runtime.destroyed) return reject(new Error('Toolkit runtime stopped.'));\n", "            if (runtime.destroyed) {\n                reject(new Error('Toolkit runtime stopped.'));\n                return;\n            }\n", "make destroyed-runtime Promise rejection explicit"),
        ("            if (typeof GM_xmlhttpRequest !== 'function') return reject(new Error('Tampermonkey cross-origin requests are unavailable.'));\n", "            if (typeof GM_xmlhttpRequest !== 'function') {\n                reject(new Error('Tampermonkey cross-origin requests are unavailable.'));\n                return;\n            }\n", "make missing-GM Promise rejection explicit"),
        ("            return await new Promise(resolve => canvas.toBlob(resolve, 'image/png', 0.92));\n", "            return await new Promise(resolve => {\n                canvas.toBlob(resolve, 'image/png', 0.92);\n            });\n", "remove unread Promise-executor return from canvas conversion"),
        ("            let path = '';\n", "            let path;\n", "remove overwritten path initializer"),
        ("        let registry = null;\n", "        let registry;\n", "remove overwritten registry initializer"),
        ("            let properties = [];\n", "            let properties;\n", "remove overwritten properties initializer"),
        ("        let node = walker.currentNode;\n", "        let node;\n", "remove overwritten tree-walker initializer"),
        ("        let rect = null;\n", "        let rect;\n", "remove overwritten rectangle initializer"),
        ("        let missionTooltip = null;\n", "        let missionTooltip;\n", "remove overwritten tooltip initializer"),
        ("        let matched = false;\n", "        let matched;\n", "remove overwritten rule-match initializer"),
        ("        let scanLimitReached = false;\n", "        let scanLimitReached;\n", "remove overwritten scan-limit initializer"),
        (
            "        return SUPPRESSION_SELECTORS.some(selector => {\n            let nodes = [];\n            try { nodes = Array.from(document.querySelectorAll(selector)); } catch (err) { return false; }\n",
            "        return SUPPRESSION_SELECTORS.some(selector => {\n            let nodes;\n            try { nodes = Array.from(document.querySelectorAll(selector)); } catch (err) { return false; }\n",
            "remove overwritten suppression-node initializer",
        ),
    ]

    for item in replacements:
        old, new, label, *rest = item
        expected = rest[0] if rest else 1
        text, _ = replace_exact(text, old, new, label, expected)
        changes.append(label)

    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    reports: list[str] = ["# Verified userscript audit fixes", ""]
    transformed: list[tuple[Path, str]] = []
    reference_output: str | None = None

    for path in args.paths:
        original = path.read_text(encoding="utf-8")
        updated, changes = transform(original)
        if updated == original:
            raise SystemExit(f"{path}: transformer produced no changes")
        if reference_output is None:
            reference_output = updated
        elif updated != reference_output:
            raise SystemExit(f"{path}: transformed source no longer matches canonical output")
        transformed.append((path, updated))
        reports.extend([
            f"## `{path}`",
            "",
            f"- Before: `{len(original.encode('utf-8')):,}` bytes · `{hashlib.sha256(original.encode()).hexdigest()}`",
            f"- After: `{len(updated.encode('utf-8')):,}` bytes · `{hashlib.sha256(updated.encode()).hexdigest()}`",
            f"- Net: `{len(updated.encode('utf-8')) - len(original.encode('utf-8')):+,}` bytes",
            "",
        ])
        for change in changes:
            reports.append(f"- {change}")
        reports.append("")

    for path, updated in transformed:
        path.write_text(updated, encoding="utf-8")

    args.report.write_text("\n".join(reports) + "\n", encoding="utf-8")
    print(args.report.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
