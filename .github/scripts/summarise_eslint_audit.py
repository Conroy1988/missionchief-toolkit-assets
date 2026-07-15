#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    documents = json.loads(args.input.read_text(encoding="utf-8"))
    messages = []
    for document in documents:
        path = document.get("filePath", "")
        for message in document.get("messages", []):
            messages.append({
                "path": path,
                "ruleId": message.get("ruleId") or "parser",
                "severity": int(message.get("severity") or 0),
                "message": message.get("message", ""),
                "line": message.get("line"),
                "column": message.get("column"),
                "endLine": message.get("endLine"),
                "endColumn": message.get("endColumn"),
                "nodeType": message.get("nodeType"),
                "messageId": message.get("messageId"),
            })

    by_rule = Counter(item["ruleId"] for item in messages)
    by_severity = Counter(item["severity"] for item in messages)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in messages:
        grouped[item["ruleId"]].append(item)

    payload = {
        "schemaVersion": 1,
        "summary": {
            "errors": by_severity.get(2, 0),
            "warnings": by_severity.get(1, 0),
            "messages": len(messages),
            "rules": dict(by_rule.most_common()),
        },
        "messages": messages,
    }
    args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# AST-backed ESLint userscript audit",
        "",
        f"- Errors: **{by_severity.get(2, 0)}**",
        f"- Warnings: **{by_severity.get(1, 0)}**",
        f"- Total messages: **{len(messages)}**",
        "",
        "## Rule inventory",
        "",
        "| Rule | Count |",
        "|---|---:|",
    ]
    for rule, count in by_rule.most_common():
        lines.append(f"| `{rule}` | {count} |")

    for rule, items in sorted(grouped.items(), key=lambda entry: (-len(entry[1]), entry[0])):
        lines.extend(["", f"## `{rule}`", ""])
        for item in items[:200]:
            level = "error" if item["severity"] == 2 else "warning"
            location = f"line {item['line']}:{item['column']}" if item.get("line") else "unknown location"
            lines.append(f"- **{level}** · {location}: {item['message']}")
        if len(items) > 200:
            lines.append(f"- … {len(items) - 200} additional messages are retained in the JSON report.")

    args.markdown_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    return 1 if by_severity.get(2, 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
