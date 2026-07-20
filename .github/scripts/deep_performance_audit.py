#!/usr/bin/env python3
"""Static hotspot inventory for the MissionChief Toolkit.

The report ranks structural pressure only. It never modifies the userscript and
must not be treated as a browser benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

FUNCTION = re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{")
VERSION = re.compile(r"^//\s*@version\s+([^\s]+)", re.M)
TEMPLATE = re.compile(r"`((?:\\.|[^`])*)`", re.S)
CSS_SIGNAL = re.compile(r"(?:!important|--[\w-]+\s*:|(?:display|position|color|background|border|font|padding|margin|width|height|opacity|transform|animation|z-index)\s*:)", re.I)
SELECTOR = re.compile(r"\.(?:querySelector|querySelectorAll)\s*\(\s*(['\"])((?:\\.|(?!\1).)*)\1", re.S)
ALIAS = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*([^;\n]{0,900}(?:MutationObserver|ResizeObserver)[^;\n]{0,900});")
CONSTRUCT = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*new\s+(?:(?:pageWindow|window)\.)?([A-Za-z_$][\w$]*)\s*\(")
OBSERVE = re.compile(r"\b([A-Za-z_$][\w$]*)\.observe\s*\(")
SCHEDULERS = ("runtimeSetTimeout", "runtimeSetInterval", "runtimeRequestAnimationFrame", "runtimeRunWhenIdle", "setTimeout", "setInterval", "requestAnimationFrame")
READS = (r"\.(?:querySelector|querySelectorAll)\s*\(", r"\.getElementById\s*\(", r"\.(?:closest|matches|getAttribute|getBoundingClientRect|getClientRects)\s*\(")
WRITES = (r"\.innerHTML\s*=(?!=)", r"\.(?:textContent|innerText|value|checked|hidden)\s*=(?!=)", r"\.style(?:\.[A-Za-z_$][\w$]*|\s*=)", r"\.(?:setAttribute|removeAttribute|appendChild|replaceChildren|insertBefore|insertAdjacentHTML|remove)\s*\(", r"\.classList\.(?:add|remove|toggle|replace)\s*\(")
FLOW = (r"\bif\s*\(", r"\bfor\s*\(", r"\bwhile\s*\(", r"\bswitch\s*\(", r"\bcase\b", r"\bcatch\s*\(")
NETWORK = (r"\bGM_xmlhttpRequest\s*\(", r"\bGM\.xmlHttpRequest\s*\(", r"(?<![.\w])fetch\s*\(", r"\bnew\s+(?:pageWindow\.)?XMLHttpRequest\s*\(")


@dataclass(frozen=True)
class FunctionRow:
    name: str
    start_line: int
    end_line: int
    lines: int
    bytes: int
    flow: int
    reads: int
    writes: int
    schedulers: int
    observers: int
    network: int
    score: int


def line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def count(text: str, patterns: tuple[str, ...]) -> int:
    return sum(len(re.findall(pattern, text)) for pattern in patterns)


def balanced_end(text: str, opening: int, open_char: str, close_char: str) -> int:
    depth, state, escaped, regex_class = 0, "code", False, False
    previous = ""
    index = opening
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "line-comment":
            if char == "\n": state = "code"
            index += 1; continue
        if state == "block-comment":
            if char == "*" and nxt == "/": state = "code"; index += 2
            else: index += 1
            continue
        if state in {"single", "double", "template"}:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif (state == "single" and char == "'") or (state == "double" and char == '"') or (state == "template" and char == "`"): state = "code"
            index += 1; continue
        if state == "regex":
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == "[": regex_class = True
            elif char == "]": regex_class = False
            elif char == "/" and not regex_class: state = "code"
            index += 1; continue
        if char == "/" and nxt == "/": state = "line-comment"; index += 2; continue
        if char == "/" and nxt == "*": state = "block-comment"; index += 2; continue
        if char == "'": state = "single"; index += 1; continue
        if char == '"': state = "double"; index += 1; continue
        if char == "`": state = "template"; index += 1; continue
        if char == "/" and previous in {"", "(", "[", "{", "=", ":", ",", "!", "?", ";"}: state = "regex"; regex_class = False; index += 1; continue
        if char == open_char: depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0: return index + 1
        if not char.isspace(): previous = char
        index += 1
    raise ValueError("unterminated JavaScript delimiter")


def split_args(value: str) -> list[str]:
    result, start, round_depth, square_depth, curly_depth = [], 0, 0, 0, 0
    state, escaped = "code", False
    for index, char in enumerate(value):
        if state != "code":
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif (state == "single" and char == "'") or (state == "double" and char == '"') or (state == "template" and char == "`"): state = "code"
            continue
        if char == "'": state = "single"
        elif char == '"': state = "double"
        elif char == "`": state = "template"
        elif char == "(": round_depth += 1
        elif char == ")": round_depth -= 1
        elif char == "[": square_depth += 1
        elif char == "]": square_depth -= 1
        elif char == "{": curly_depth += 1
        elif char == "}": curly_depth -= 1
        elif char == "," and round_depth == square_depth == curly_depth == 0:
            result.append(value[start:index].strip()); start = index + 1
    result.append(value[start:].strip())
    return result


def functions(text: str) -> list[tuple[FunctionRow, int, int, str]]:
    rows = []
    for match in FUNCTION.finditer(text):
        opening = text.find("{", match.start(), match.end())
        try: end = balanced_end(text, opening, "{", "}")
        except ValueError: continue
        body = text[opening + 1:end - 1]
        start_line, end_line = line(text, match.start()), line(text, end - 1)
        flow, reads, writes = count(body, FLOW), count(body, READS), count(body, WRITES)
        scheduler_count = sum(len(re.findall(rf"\b{re.escape(name)}\s*\(", body)) for name in SCHEDULERS)
        observer_count = len(re.findall(r"\bnew\s+(?:(?:pageWindow|window)\.)?(?:MutationObserver|ResizeObserver|MutationObserverCtor|ResizeObserverCtor|Observer)\s*\(", body)) + len(OBSERVE.findall(body))
        network_count = count(body, NETWORK)
        lines = end_line - start_line + 1
        byte_count = len(text[match.start():end].encode("utf-8"))
        score = lines + flow * 6 + reads * 5 + writes * 8 + scheduler_count * 6 + observer_count * 10 + network_count * 12
        rows.append((FunctionRow(match.group(1), start_line, end_line, lines, byte_count, flow, reads, writes, scheduler_count, observer_count, network_count, score), match.start(), end, body))
    return rows


def owner(items: list[tuple[FunctionRow, int, int, str]], offset: int) -> str:
    matches = [item for item in items if item[1] <= offset < item[2]]
    return min(matches, key=lambda item: item[2] - item[1])[0].name if matches else "<top-level>"


def observer_inventory(text: str, items: list[tuple[FunctionRow, int, int, str]]) -> list[dict[str, object]]:
    aliases = {"MutationObserver": "MutationObserver", "ResizeObserver": "ResizeObserver"}
    for match in ALIAS.finditer(text):
        if "MutationObserver" in match.group(2): aliases[match.group(1)] = "MutationObserver"
        elif "ResizeObserver" in match.group(2): aliases[match.group(1)] = "ResizeObserver"
    constructed = {}
    for match in CONSTRUCT.finditer(text):
        if match.group(2) in aliases: constructed[match.group(1)] = aliases[match.group(2)]
    result = []
    for match in OBSERVE.finditer(text):
        name = match.group(1)
        if name not in constructed: continue
        opening = text.find("(", match.start(), match.end())
        try: end = balanced_end(text, opening, "(", ")")
        except ValueError: continue
        args = split_args(text[opening + 1:end - 1])
        target, options = (args[0] if args else ""), (args[1] if len(args) > 1 else "")
        function_name = owner(items, match.start())
        entry = next((item for item in items if item[0].name == function_name and item[1] <= match.start() < item[2]), None)
        scope = text[entry[1]:entry[2]] if entry else text[max(0, match.start() - 1000):end + 1000]
        tracked = bool(re.search(rf"runtimeTrackObserver\s*\(\s*{re.escape(name)}\b", scope))
        disconnected = tracked or bool(re.search(rf"\b{re.escape(name)}\.disconnect\s*\(", scope))
        result.append({"observer": name, "constructor": constructed[name], "line": line(text, match.start()), "function": function_name, "target": " ".join(target[:180].split()), "options": " ".join(options[:500].split()), "subtree": bool(re.search(r"\bsubtree\s*:\s*true\b", options)), "childList": bool(re.search(r"\bchildList\s*:\s*true\b", options)), "attributes": bool(re.search(r"\battributes\s*:\s*true\b", options)), "tracked": tracked, "disconnectSignal": disconnected})
    return result


def scheduler_inventory(text: str, items: list[tuple[FunctionRow, int, int, str]]) -> list[dict[str, object]]:
    result = []
    for scheduler in SCHEDULERS:
        for match in re.finditer(rf"\b{re.escape(scheduler)}\s*\(", text):
            if re.search(r"\bfunction\s*$", text[max(0, match.start() - 80):match.start()]): continue
            opening = text.find("(", match.start(), match.end())
            try: args = split_args(text[opening + 1:balanced_end(text, opening, "(", ")") - 1])
            except ValueError: args = []
            mode = "frame" if "AnimationFrame" in scheduler else "idle" if scheduler == "runtimeRunWhenIdle" else " ".join(args[1][:100].split()) if len(args) > 1 else ""
            result.append({"scheduler": scheduler, "line": line(text, match.start()), "function": owner(items, match.start()), "delayOrMode": mode})
    return sorted(result, key=lambda item: (item["line"], item["scheduler"]))


def templates(text: str) -> list[dict[str, object]]:
    result = []
    for match in TEMPLATE.finditer(text):
        value = match.group(1); byte_count = len(value.encode("utf-8"))
        if byte_count < 1000: continue
        kind = "css" if CSS_SIGNAL.search(value) and "{" in value and "}" in value else "html" if "<" in value and ">" in value else "text"
        result.append({"line": line(text, match.start()), "bytes": byte_count, "classification": kind, "braceCount": value.count("{") if kind == "css" else 0})
    return sorted(result, key=lambda item: item["bytes"], reverse=True)


def repeated_selectors(text: str, items: list[tuple[FunctionRow, int, int, str]]) -> list[dict[str, object]]:
    index: dict[str, dict[str, object]] = {}
    for match in SELECTOR.finditer(text):
        selector = match.group(2)
        entry = index.setdefault(selector, {"selector": selector, "count": 0, "functions": set(), "lines": []})
        entry["count"] = int(entry["count"]) + 1
        entry["functions"].add(owner(items, match.start()))
        entry["lines"].append(line(text, match.start()))
    return sorted(({"selector": value["selector"], "count": value["count"], "functions": sorted(value["functions"]), "lines": value["lines"][:20]} for value in index.values() if int(value["count"]) >= 2), key=lambda item: (-int(item["count"]), str(item["selector"])))


def report(source: Path) -> dict[str, object]:
    text = source.read_text(encoding="utf-8")
    extracted = functions(text); rows = [item[0] for item in extracted]
    observers = observer_inventory(text, extracted); schedulers = scheduler_inventory(text, extracted); large_templates = templates(text); selectors = repeated_selectors(text, extracted)
    by_scheduler: dict[str, int] = {}
    for item in schedulers: by_scheduler[item["function"]] = by_scheduler.get(item["function"], 0) + 1
    line_count = len(text.splitlines()); remaining = 32000 - line_count
    findings = []
    if remaining < 500: findings.append({"risk": "high", "category": "source-headroom", "message": f"Only {remaining} lines remain before the existing 32,000-line ceiling."})
    if large_templates and large_templates[0]["classification"] == "css" and int(large_templates[0]["bytes"]) > 500000: findings.append({"risk": "high", "category": "style-parse", "message": "The largest embedded CSS template exceeds 500 KB; live timing and visual contracts are required before changing style delivery."})
    broad = sum(1 for item in observers if item["subtree"]); unowned = sum(1 for item in observers if not item["disconnectSignal"])
    if broad: findings.append({"risk": "medium", "category": "observer-scope", "message": f"{broad} observer registrations use subtree:true; ownership and callback evidence are required before narrowing or merging them."})
    if unowned: findings.append({"risk": "high", "category": "observer-ownership", "message": f"{unowned} registrations lack a statically visible disconnect or runtimeTrackObserver signal and require manual lifecycle verification."})
    if selectors and int(selectors[0]["count"]) >= 4: findings.append({"risk": "low", "category": "selector-repetition", "message": "Repeated literal selectors exist; cache only inside proven document/window lifetimes with invalidation fixtures."})
    return {"schemaVersion": 1, "tool": "mcms-deep-performance-audit", "source": {"path": source.as_posix(), "version": VERSION.search(text).group(1) if VERSION.search(text) else "unknown", "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "bytes": len(text.encode("utf-8")), "lines": line_count, "nonemptyLines": sum(1 for value in text.splitlines() if value.strip())}, "summary": {"namedFunctions": len(rows), "largeTemplates": len(large_templates), "observerRegistrations": len(observers), "broadSubtreeObservers": broad, "schedulerCalls": len(schedulers), "repeatedSelectors": len(selectors)}, "topFunctionsByScore": [asdict(item) for item in sorted(rows, key=lambda value: (-value.score, -value.lines, value.name))[:30]], "topFunctionsByLines": [asdict(item) for item in sorted(rows, key=lambda value: (-value.lines, -value.bytes, value.name))[:30]], "topDomReaders": [asdict(item) for item in sorted(rows, key=lambda value: (-value.reads, -value.lines, value.name))[:25] if item.reads], "topDomWriters": [asdict(item) for item in sorted(rows, key=lambda value: (-value.writes, -value.lines, value.name))[:25] if item.writes], "topSchedulerFunctions": [{"function": name, "calls": calls} for name, calls in sorted(by_scheduler.items(), key=lambda value: (-value[1], value[0]))[:30]], "observerRegistrations": observers, "schedulerCalls": schedulers, "largeTemplates": large_templates[:40], "repeatedSelectors": selectors[:50], "findings": findings, "interpretation": {"staticOnly": True, "liveEvidenceRequired": ["long tasks", "layout shifts", "mutation frequency", "render frequency", "style recalculation", "memory retention"], "safetyRule": "Do not merge runtime changes solely to reduce a static count."}}


def table(headers: list[str], rows: list[list[object]]) -> list[str]:
    return ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"] + ["| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |" for row in rows]


def markdown(data: dict[str, object]) -> str:
    source, summary = data["source"], data["summary"]
    lines = ["# MissionChief Toolkit deep performance audit", "", "> Static structural evidence only. Runtime gains require equivalent browser-profiler scenarios and deterministic behaviour parity.", "", "## Baseline", "", f"- Version: `{source['version']}`", f"- SHA-256: `{source['sha256']}`", f"- Source: `{source['bytes']:,}` bytes, `{source['lines']:,}` lines", f"- Named functions: `{summary['namedFunctions']}`", f"- Scheduler calls: `{summary['schedulerCalls']}`", f"- Observer registrations: `{summary['observerRegistrations']}`", f"- Broad subtree registrations: `{summary['broadSubtreeObservers']}`", "", "## Findings", ""]
    lines.extend([f"- **{item['risk'].upper()} · {item['category']}** — {item['message']}" for item in data["findings"]] or ["- No static review findings."])
    lines += ["", "## Highest structural hotspot scores", ""] + table(["Function", "Lines", "Bytes", "Flow", "Reads", "Writes", "Schedulers", "Observers", "Network", "Score"], [[item["name"], item["lines"], item["bytes"], item["flow"], item["reads"], item["writes"], item["schedulers"], item["observers"], item["network"], item["score"]] for item in data["topFunctionsByScore"][:20]])
    lines += ["", "## DOM-write concentration", ""] + table(["Function", "Lines", "Reads", "Writes", "Schedulers", "Score"], [[item["name"], item["lines"], item["reads"], item["writes"], item["schedulers"], item["score"]] for item in data["topDomWriters"][:20]])
    lines += ["", "## Scheduler concentration", ""] + table(["Function", "Calls"], [[item["function"], item["calls"]] for item in data["topSchedulerFunctions"][:20]])
    lines += ["", "## Observer ownership inventory", ""] + table(["Line", "Function", "Type", "Target", "Options", "Tracked", "Disconnect"], [[item["line"], item["function"], item["constructor"], item["target"], item["options"], item["tracked"], item["disconnectSignal"]] for item in data["observerRegistrations"]])
    lines += ["", "## Largest embedded templates", ""] + table(["Line", "Type", "Bytes", "Brace/rule estimate"], [[item["line"], item["classification"], item["bytes"], item["braceCount"]] for item in data["largeTemplates"][:20]])
    lines += ["", "## Repeated literal selectors", ""] + table(["Count", "Selector", "Functions"], [[item["count"], item["selector"], ", ".join(item["functions"])] for item in data["repeatedSelectors"][:25]])
    lines += ["", "## Safety interpretation", "", "- A large function or repeated selector is a profiling target, not proof of a defect.", "- Observer count must not be reduced by merging different lifecycle owners.", "- Cached DOM references require explicit invalidation when MissionChief replaces documents, dialogs, frames or controls.", "- CSS extraction requires visual contracts and first-paint evidence.", "- Every runtime optimisation must be isolated, benchmarked and reversible.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--source", type=Path, required=True); parser.add_argument("--json-output", type=Path, required=True); parser.add_argument("--markdown-output", type=Path, required=True); args = parser.parse_args()
    data = report(args.source); args.json_output.parent.mkdir(parents=True, exist_ok=True); args.markdown_output.parent.mkdir(parents=True, exist_ok=True); args.json_output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8"); args.markdown_output.write_text(markdown(data), encoding="utf-8"); print(json.dumps(data["summary"], indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
