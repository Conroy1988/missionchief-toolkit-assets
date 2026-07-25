#!/usr/bin/env python3
"""Static performance and lifecycle budgets for the v6.0.0 critical overhaul."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
BUDGET = ROOT / ".github" / "fixtures" / "v6-performance-budget.json"


def function_body(source: str, name: str) -> str:
    match = re.search(rf"(?m)^\s*(?:async\s+)?function\s+{re.escape(name)}\s*\(", source)
    assert match, f"Function not found: {name}"
    start = source.find("{", match.start())
    depth = 0
    quote = None
    escaped = False
    index = start
    while index < len(source):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():index + 1]
        index += 1
    raise AssertionError(f"Unclosed function: {name}")


def metrics(source: str, byte_count: int) -> dict[str, int]:
    feature_remove = function_body(source, "operationalFeatureRemove")
    reset = function_body(source, "operationalResetNativeDecorations")
    return {
        "bytes": byte_count,
        "lines": source.count("\n") + 1,
        "functionDeclarations": len(re.findall(r"(?m)^\s*(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(", source)),
        "mutationObservers": source.count("new MutationObserver"),
        "recurringTasks": len(re.findall(r"runtimeRegisterTask\(\s*['\"]", source)),
        "runtimeSetTimeoutCallsites": source.count("runtimeSetTimeout("),
        "runtimeRafCallsites": source.count("runtimeRequestAnimationFrame("),
        "eventListenerCallsites": source.count("addEventListener("),
        "querySelectorAllCallsites": source.count("querySelectorAll("),
        "operationalOwnedFullDocumentQueries": feature_remove.count("querySelectorAll") + feature_remove.count("operationalQueryAll"),
        "operationalDecorationFullDocumentQueries": reset.count("querySelectorAll") + reset.count("operationalQueryAll"),
    }


def main() -> int:
    raw = SOURCE.read_bytes()
    source = raw.decode("utf-8")
    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    actual = metrics(source, len(raw))
    limits = budget["v6Budgets"]
    mapping = {
        "bytes": "maxBytes",
        "lines": "maxLines",
        "functionDeclarations": "maxFunctionDeclarations",
        "mutationObservers": "maxMutationObservers",
        "recurringTasks": "maxRecurringTasks",
        "runtimeSetTimeoutCallsites": "maxRuntimeSetTimeoutCallsites",
        "runtimeRafCallsites": "maxRuntimeRafCallsites",
        "eventListenerCallsites": "maxEventListenerCallsites",
        "querySelectorAllCallsites": "maxQuerySelectorAllCallsites",
        "operationalOwnedFullDocumentQueries": "maxOperationalOwnedFullDocumentQueries",
        "operationalDecorationFullDocumentQueries": "maxOperationalDecorationFullDocumentQueries",
    }
    failures = [f"{name}={actual[name]} > {limits[key]}" for name, key in mapping.items() if actual[name] > limits[key]]
    assert not failures, "v6 static performance budget exceeded: " + ", ".join(failures)

    required = [
        "const operationalOwnedNodes = new WeakMap();",
        "const operationalDecoratedNodes = new WeakMap();",
        "const contentRoots = Array.from(new Set([",
        "const structuralRoots = Array.from(new Set([",
        "for (const root of contentRoots) context.observer.observe(root, { ...attributes, characterData: true });",
        "for (const root of structuralRoots) context.observer.observe(root, attributes);",
        "target?.closest?.(`[${OP_FEATURE_ATTR}], #${SCRIPT.panelId}`)",
        "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(120);",
        "operationalWindowSyncSettingsUi(); showToast(message);",
    ]
    missing = [marker for marker in required if marker not in source]
    assert not missing, f"v6 operational lifecycle markers missing: {missing}"
    forbidden = [
        "scheduleOperationalSuiteScan(35);\n                    if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(35);",
        "operationalQueryAll(context?.doc, safe ?",
        "function operationalResetNativeDecorations(doc){operationalQueryAll",
        "for (const root of roots) {\n            context.observer.observe(root, {\n                childList: true,\n                subtree: true,\n                characterData: true",
    ]
    present = [marker for marker in forbidden if marker in source]
    assert not present, f"v6 operational hot-path regression: {present}"

    print(json.dumps({"state": "passed", "metrics": actual, "baseline": budget["baseline"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
