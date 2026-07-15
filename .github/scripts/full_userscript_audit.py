#!/usr/bin/env python3
"""Deep static audit for the MissionChief Map Command Toolkit userscript.

The analyser is deliberately conservative. It reports optimisation and dead-code
candidates, but only hard structural defects fail the workflow. Candidate removal
must be reviewed against real call paths before source changes are made.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DEFAULT_DIST = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
IDENT = r"[A-Za-z_$][A-Za-z0-9_$]*"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None
    subject: str = ""
    evidence: str = ""


@dataclass(frozen=True)
class FunctionRecord:
    name: str
    line: int
    start: int
    body_start: int
    body_end: int
    body_lines: int
    parameters: int
    complexity: int
    query_calls: int
    listener_calls: int
    timer_calls: int


@dataclass(frozen=True)
class AuditMetrics:
    bytes: int
    lines: int
    sha256: str
    functions: int
    named_functions: int
    anonymous_functions: int
    arrow_functions: int
    classes: int
    const_declarations: int
    let_declarations: int
    var_declarations: int
    query_selector_calls: int
    query_selector_all_calls: int
    get_element_by_id_calls: int
    event_listeners_added: int
    event_listeners_removed: int
    mutation_observers: int
    resize_observers: int
    intersection_observers: int
    intervals_created: int
    intervals_cleared: int
    timeouts_created: int
    timeouts_cleared: int
    animation_frames_created: int
    animation_frames_cancelled: int
    inner_html_assignments: int
    insert_adjacent_html_calls: int
    local_storage_reads: int
    local_storage_writes: int
    gm_reads: int
    gm_writes: int
    css_template_blocks: int


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_node_syntax_check(path: Path) -> tuple[bool, str]:
    completed = subprocess.run(
        ["node", "--check", str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, completed.stdout.strip()


def metadata(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    start = text.find("// ==UserScript==")
    end = text.find("// ==/UserScript==")
    if start < 0 or end <= start:
        return {}
    for raw in text[start:end].splitlines():
        match = re.match(r"^//\s*@([A-Za-z0-9:_-]+)\s+(.+?)\s*$", raw)
        if match:
            result[match.group(1).lower()].append(match.group(2))
    return dict(result)


def mask_non_code(text: str) -> str:
    """Mask strings and comments while preserving offsets and line breaks.

    Template interpolation is intentionally masked with the template body. Raw
    identifier counts are used for dead-code candidates to avoid false removals.
    """
    chars = list(text)
    i = 0
    state = "code"
    quote = ""
    escaped = False
    regex_class = False
    previous_significant = ""

    def blank(index: int) -> None:
        if chars[index] != "\n":
            chars[index] = " "

    while i < len(chars):
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if state == "line-comment":
            blank(i)
            if ch == "\n":
                state = "code"
            i += 1
            continue
        if state == "block-comment":
            blank(i)
            if ch == "*" and nxt == "/":
                blank(i + 1)
                i += 2
                state = "code"
            else:
                i += 1
            continue
        if state == "string":
            blank(i)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                state = "code"
            i += 1
            continue
        if state == "regex":
            blank(i)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == "[":
                regex_class = True
            elif ch == "]":
                regex_class = False
            elif ch == "/" and not regex_class:
                state = "regex-flags"
            i += 1
            continue
        if state == "regex-flags":
            if ch.isalpha():
                blank(i)
                i += 1
            else:
                state = "code"
            continue

        if ch == "/" and nxt == "/":
            blank(i); blank(i + 1)
            i += 2
            state = "line-comment"
            continue
        if ch == "/" and nxt == "*":
            blank(i); blank(i + 1)
            i += 2
            state = "block-comment"
            continue
        if ch in "'\"`":
            quote = ch
            blank(i)
            i += 1
            state = "string"
            escaped = False
            continue
        if ch == "/":
            # Heuristic: after an operator, delimiter or keyword boundary, slash
            # most likely starts a regex literal rather than division.
            prefix = previous_significant
            if not prefix or prefix[-1] in "([{=,:;!&|?+-*%^~<>" or re.search(
                r"(?:return|throw|case|delete|void|typeof|instanceof|in|of|yield|await)$",
                prefix,
            ):
                blank(i)
                i += 1
                state = "regex"
                escaped = False
                regex_class = False
                continue
        if not ch.isspace():
            previous_significant = (previous_significant + ch)[-32:]
        i += 1
    return "".join(chars)


def matching_brace(masked: str, open_pos: int) -> int | None:
    depth = 0
    for index in range(open_pos, len(masked)):
        ch = masked[index]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def normalise_body(body: str) -> str:
    masked = mask_non_code(body)
    return re.sub(r"\s+", "", masked)


def count_parameters(raw: str) -> int:
    raw = raw.strip()
    if not raw:
        return 0
    depth = 0
    count = 1
    for ch in raw:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            count += 1
    return count


def complexity_score(masked_body: str) -> int:
    patterns = [
        r"\bif\s*\(", r"\belse\s+if\s*\(", r"\bfor\s*\(", r"\bfor\s+await\s*\(",
        r"\bwhile\s*\(", r"\bdo\s*\{", r"\bcase\b", r"\bcatch\s*\(", r"\?",
        r"&&", r"\|\|", r"\?\?",
    ]
    return 1 + sum(len(re.findall(pattern, masked_body)) for pattern in patterns)


def extract_functions(text: str, masked: str) -> list[FunctionRecord]:
    records: list[FunctionRecord] = []
    occupied: list[tuple[int, int]] = []

    patterns: list[tuple[re.Pattern[str], str]] = [
        (re.compile(rf"\b(?:async\s+)?function\s+(?P<name>{IDENT})\s*\((?P<params>[^)]*)\)\s*\{{"), "decl"),
        (re.compile(rf"\b(?:const|let|var)\s+(?P<name>{IDENT})\s*=\s*(?:async\s*)?function\s*\((?P<params>[^)]*)\)\s*\{{"), "expr"),
        (re.compile(rf"\b(?:const|let|var)\s+(?P<name>{IDENT})\s*=\s*(?:async\s*)?\((?P<params>[^)]*)\)\s*=>\s*\{{"), "arrow"),
        (re.compile(rf"\b(?:const|let|var)\s+(?P<name>{IDENT})\s*=\s*(?:async\s*)?(?P<params>{IDENT})\s*=>\s*\{{"), "arrow"),
        (re.compile(rf"(?<![.\w$])(?P<name>{IDENT})\s*\((?P<params>[^)]*)\)\s*\{{"), "method"),
    ]

    for pattern, _kind in patterns:
        for match in pattern.finditer(masked):
            open_pos = masked.find("{", match.start(), match.end())
            if open_pos < 0:
                continue
            if any(start <= open_pos <= end for start, end in occupied):
                continue
            close_pos = matching_brace(masked, open_pos)
            if close_pos is None:
                continue
            occupied.append((match.start(), close_pos))
            body = masked[open_pos + 1:close_pos]
            raw_body = text[open_pos + 1:close_pos]
            name = match.group("name")
            params = match.groupdict().get("params") or ""
            records.append(FunctionRecord(
                name=name,
                line=line_number(text, match.start()),
                start=match.start(),
                body_start=open_pos + 1,
                body_end=close_pos,
                body_lines=raw_body.count("\n") + 1,
                parameters=count_parameters(params),
                complexity=complexity_score(body),
                query_calls=len(re.findall(r"\b(?:querySelector|querySelectorAll|getElementById)\s*\(", body)),
                listener_calls=len(re.findall(r"\baddEventListener\s*\(", body)),
                timer_calls=len(re.findall(r"\b(?:setTimeout|setInterval|requestAnimationFrame)\s*\(", body)),
            ))
    records.sort(key=lambda item: item.start)
    return records


def extract_literal_calls(text: str, method: str) -> list[tuple[str, int]]:
    pattern = re.compile(rf"\b{re.escape(method)}\s*\(\s*(['\"])(?P<value>.*?)\1", re.S)
    return [(match.group("value"), line_number(text, match.start())) for match in pattern.finditer(text)]


def extract_event_types(text: str, method: str) -> Counter[str]:
    result: Counter[str] = Counter()
    pattern = re.compile(rf"\b{re.escape(method)}\s*\(\s*(['\"])(?P<event>[^'\"\r\n]+)\1")
    for match in pattern.finditer(text):
        result[match.group("event")] += 1
    return result


def extract_timer_literals(text: str, method: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    pattern = re.compile(rf"\b{re.escape(method)}\s*\((?P<body>.{{0,1800}}?)\)\s*;", re.S)
    for match in pattern.finditer(text):
        body = match.group("body")
        delay = re.search(r",\s*(?P<delay>[0-9][0-9_]*)\s*$", body)
        if delay:
            result.append((int(delay.group("delay").replace("_", "")), line_number(text, match.start())))
    return result


def extract_css_blocks(text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    pattern = re.compile(r"(?:textContent|innerHTML)\s*=\s*`(?P<body>.*?)`;", re.S)
    for match in pattern.finditer(text):
        body = match.group("body")
        if "{" in body and "}" in body and ("#" in body or "." in body or "@media" in body):
            blocks.append((line_number(text, match.start()), body))
    return blocks


def duplicate_css_selectors(blocks: Iterable[tuple[int, str]]) -> list[tuple[str, list[int]]]:
    selectors: dict[str, list[int]] = defaultdict(list)
    for start_line, body in blocks:
        for match in re.finditer(r"(?P<selector>(?:[^{}]|\{[^{}]*\})+?)\s*\{", body):
            selector = re.sub(r"\s+", " ", match.group("selector").strip())
            if not selector or selector.startswith(("@", "from", "to", "0%", "100%")):
                continue
            line = start_line + body.count("\n", 0, match.start())
            selectors[selector].append(line)
    return sorted(
        ((selector, lines) for selector, lines in selectors.items() if len(lines) > 1),
        key=lambda item: (-len(item[1]), item[0]),
    )


def audit(source: Path, dist: Path | None) -> tuple[AuditMetrics, list[Finding], dict]:
    text = source.read_text(encoding="utf-8")
    masked = mask_non_code(text)
    findings: list[Finding] = []
    syntax_ok, syntax_output = run_node_syntax_check(source)
    if not syntax_ok:
        findings.append(Finding("failure", "syntax", "Node.js rejected the canonical userscript.", evidence=syntax_output))

    meta = metadata(text)
    version = (meta.get("version") or [""])[0]
    if not version:
        findings.append(Finding("failure", "metadata-version", "The userscript has no @version directive."))
    if dist and dist.is_file():
        dist_text = dist.read_text(encoding="utf-8")
        if dist_text != text:
            findings.append(Finding("failure", "distribution-parity", "Canonical source and distribution userscript are not byte-identical."))

    functions = extract_functions(text, masked)
    name_groups: dict[str, list[FunctionRecord]] = defaultdict(list)
    for record in functions:
        name_groups[record.name].append(record)
    for name, records in sorted(name_groups.items()):
        if len(records) > 1:
            findings.append(Finding(
                "review", "duplicate-function-name",
                f"Function-like declaration {name!r} appears {len(records)} times; confirm intentional scoping or shadowing.",
                line=records[0].line, subject=name,
                evidence=", ".join(str(item.line) for item in records),
            ))

    bodies: dict[str, list[FunctionRecord]] = defaultdict(list)
    for record in functions:
        raw_body = text[record.body_start:record.body_end]
        normalised = normalise_body(raw_body)
        if len(normalised) >= 180:
            bodies[hashlib.sha256(normalised.encode("utf-8")).hexdigest()].append(record)
    for records in bodies.values():
        names = {item.name for item in records}
        if len(records) > 1 and len(names) > 1:
            findings.append(Finding(
                "review", "duplicate-function-body",
                "Multiple named functions have an identical substantial body.",
                line=records[0].line,
                subject=", ".join(item.name for item in records),
                evidence=", ".join(f"{item.name}@{item.line}" for item in records),
            ))

    raw_identifier_counts = Counter(re.findall(rf"\b{IDENT}\b", text))
    dead_function_exemptions = {
        "main", "init", "bootstrap", "setup", "cleanup", "destroy", "render", "update",
        "onload", "onclick", "onchange", "onsubmit", "onmessage", "handleEvent",
    }
    for record in functions:
        if raw_identifier_counts[record.name] == 1 and record.name.casefold() not in dead_function_exemptions:
            findings.append(Finding(
                "candidate", "unreferenced-function",
                "Named function appears only at its declaration. Verify no reflective or string-based call path before removal.",
                line=record.line, subject=record.name,
            ))

    declarations: dict[str, list[tuple[str, int]]] = defaultdict(list)
    declaration_re = re.compile(rf"\b(?P<kind>const|let|var)\s+(?P<name>{IDENT})\b")
    for match in declaration_re.finditer(masked):
        declarations[match.group("name")].append((match.group("kind"), line_number(text, match.start())))
    for name, entries in sorted(declarations.items()):
        if len(entries) == 1 and raw_identifier_counts[name] == 1 and name not in {"_", "unused"}:
            kind, line = entries[0]
            findings.append(Finding(
                "candidate", "unreferenced-binding",
                f"{kind} binding appears only at its declaration. Verify destructuring or reflective use before removal.",
                line=line, subject=name,
            ))

    for record in functions:
        if record.body_lines >= 350:
            findings.append(Finding("review", "very-large-function", f"Function spans {record.body_lines} lines.", record.line, record.name))
        elif record.body_lines >= 220:
            findings.append(Finding("advisory", "large-function", f"Function spans {record.body_lines} lines.", record.line, record.name))
        if record.complexity >= 80:
            findings.append(Finding("review", "very-high-complexity", f"Estimated cyclomatic complexity is {record.complexity}.", record.line, record.name))
        elif record.complexity >= 45:
            findings.append(Finding("advisory", "high-complexity", f"Estimated cyclomatic complexity is {record.complexity}.", record.line, record.name))
        if record.parameters >= 10:
            findings.append(Finding("advisory", "long-parameter-list", f"Function declares {record.parameters} parameters.", record.line, record.name))

    fixed_condition_patterns = [
        (r"\bif\s*\(\s*false\s*\)", "if-false"),
        (r"\bwhile\s*\(\s*false\s*\)", "while-false"),
        (r"\bif\s*\(\s*true\s*\)", "if-true"),
    ]
    for pattern, code in fixed_condition_patterns:
        for match in re.finditer(pattern, masked):
            findings.append(Finding("review", code, "Constant control-flow condition found.", line_number(text, match.start()), evidence=match.group(0)))

    for match in re.finditer(r"\b(?:eval\s*\(|new\s+Function\s*\(|document\.write\s*\()", masked):
        findings.append(Finding("failure", "dynamic-code", "Dynamic code execution or document.write is prohibited.", line_number(text, match.start()), evidence=match.group(0)))

    for match in re.finditer(r"\.innerHTML\s*\+=", masked):
        findings.append(Finding("review", "innerhtml-append", "innerHTML += reparses and recreates the entire subtree; replace only after behavioural review.", line_number(text, match.start())))

    for match in re.finditer(r"\bcatch\s*\([^)]*\)\s*\{\s*\}", masked):
        findings.append(Finding("advisory", "empty-catch", "Empty catch block suppresses all diagnostic context.", line_number(text, match.start())))

    marker_re = re.compile(r"\b(TODO|FIXME|HACK|XXX|DEPRECATED|LEGACY|UNUSED|REMOVE ME)\b", re.I)
    for match in marker_re.finditer(text):
        findings.append(Finding("advisory", "maintenance-marker", "Maintenance marker remains in canonical source.", line_number(text, match.start()), subject=match.group(1)))

    comment_code_re = re.compile(r"^\s*//\s*(?:function\s+|(?:const|let|var)\s+|if\s*\(|for\s*\(|while\s*\(|.*(?:querySelector|addEventListener)\s*\()", re.M)
    for match in comment_code_re.finditer(text):
        findings.append(Finding("candidate", "commented-code", "Line resembles disabled code rather than explanatory documentation.", line_number(text, match.start()), evidence=match.group(0).strip()[:180]))

    selectors: Counter[str] = Counter()
    selector_lines: dict[str, list[int]] = defaultdict(list)
    for method in ("querySelector", "querySelectorAll", "matches", "closest"):
        for value, line in extract_literal_calls(text, method):
            compact = re.sub(r"\s+", " ", value.strip())
            selectors[compact] += 1
            selector_lines[compact].append(line)
    for selector, count in selectors.most_common():
        if count >= 8:
            findings.append(Finding(
                "advisory", "repeated-selector",
                f"Literal selector is parsed {count} times; consider a scoped helper or cached reference where lifecycle-safe.",
                line=selector_lines[selector][0], subject=selector,
                evidence=", ".join(map(str, selector_lines[selector][:12])),
            ))

    add_events = extract_event_types(text, "addEventListener")
    remove_events = extract_event_types(text, "removeEventListener")
    for event, added in sorted(add_events.items()):
        removed = remove_events.get(event, 0)
        if added >= 5 and removed == 0:
            findings.append(Finding(
                "advisory", "listener-lifecycle",
                f"Event {event!r} is added {added} times and never explicitly removed. Confirm nodes are short-lived or cleanup is registry-based.",
                subject=event,
            ))

    interval_literals = extract_timer_literals(text, "setInterval")
    for delay, line in interval_literals:
        if delay < 250:
            findings.append(Finding("review", "hot-interval", f"setInterval runs every {delay} ms.", line, evidence=str(delay)))
        elif delay < 1000:
            findings.append(Finding("advisory", "frequent-interval", f"setInterval runs every {delay} ms.", line, evidence=str(delay)))

    broad_observer_re = re.compile(r"\.observe\s*\(\s*(?:document(?:\.body|\.documentElement)?|document\.body)\s*,\s*\{(?P<options>.{0,500}?)\}\s*\)", re.S)
    for match in broad_observer_re.finditer(masked):
        options = match.group("options")
        if re.search(r"\bsubtree\s*:\s*true", options):
            findings.append(Finding("review", "broad-mutation-observer", "Observer watches a document-wide subtree; verify filtering, batching and disconnect lifecycle.", line_number(text, match.start())))

    css_blocks = extract_css_blocks(text)
    for selector, lines in duplicate_css_selectors(css_blocks):
        if len(lines) >= 3:
            findings.append(Finding(
                "advisory", "duplicate-css-selector",
                f"CSS selector appears in {len(lines)} generated rule blocks; verify intentional theme or responsive overrides.",
                line=lines[0], subject=selector[:240], evidence=", ".join(map(str, lines[:12])),
            ))

    storage_calls = extract_literal_calls(text, "getItem") + extract_literal_calls(text, "setItem") + extract_literal_calls(text, "removeItem")
    storage_keys = Counter(value for value, _line in storage_calls if value.startswith(("mc", "MC")))
    direct_storage_key_lines: dict[str, list[int]] = defaultdict(list)
    for value, line in storage_calls:
        if value.startswith(("mc", "MC")):
            direct_storage_key_lines[value].append(line)
    for key, count in storage_keys.items():
        if count >= 3:
            findings.append(Finding(
                "advisory", "repeated-storage-key-literal",
                f"Storage key literal appears {count} times; centralise it if all uses share one contract.",
                line=direct_storage_key_lines[key][0], subject=key,
            ))

    meta_grants = set(meta.get("grant", []))
    grant_usage = {
        "GM_xmlhttpRequest": bool(re.search(r"\bGM_xmlhttpRequest\b", masked)),
        "GM_getValue": bool(re.search(r"\bGM_getValue\b", masked)),
        "GM_setValue": bool(re.search(r"\bGM_setValue\b", masked)),
        "GM_deleteValue": bool(re.search(r"\bGM_deleteValue\b", masked)),
        "unsafeWindow": bool(re.search(r"\bunsafeWindow\b", masked)),
    }
    for grant in sorted(meta_grants):
        if grant in grant_usage and not grant_usage[grant]:
            findings.append(Finding("candidate", "unused-userscript-grant", "Metadata grant is declared but no code reference was found.", subject=grant))
    for grant, used in grant_usage.items():
        if used and grant not in meta_grants:
            findings.append(Finding("failure", "missing-userscript-grant", "Code uses a userscript API without declaring its grant.", subject=grant))

    connect_hosts = {value.strip().casefold() for value in meta.get("connect", [])}
    remote_hosts: Counter[str] = Counter()
    for url in re.findall(r"https?://[^\s'\"`<>\\)]+", text):
        host = (urlparse(url).hostname or "").casefold()
        if host:
            remote_hosts[host] += 1
    for host in sorted(connect_hosts):
        if not any(remote == host or remote.endswith("." + host) for remote in remote_hosts):
            findings.append(Finding("candidate", "unused-connect-host", "@connect host is not present in a static URL. Confirm dynamically constructed requests before removal.", subject=host))

    metrics = AuditMetrics(
        bytes=len(text.encode("utf-8")),
        lines=text.count("\n") + 1,
        sha256=sha256_text(text),
        functions=len(functions),
        named_functions=len(functions),
        anonymous_functions=len(re.findall(r"\bfunction\s*\(", masked)),
        arrow_functions=len(re.findall(r"=>", masked)),
        classes=len(re.findall(r"\bclass\s+" + IDENT, masked)),
        const_declarations=len(re.findall(r"\bconst\s+" + IDENT, masked)),
        let_declarations=len(re.findall(r"\blet\s+" + IDENT, masked)),
        var_declarations=len(re.findall(r"\bvar\s+" + IDENT, masked)),
        query_selector_calls=len(re.findall(r"\bquerySelector\s*\(", masked)),
        query_selector_all_calls=len(re.findall(r"\bquerySelectorAll\s*\(", masked)),
        get_element_by_id_calls=len(re.findall(r"\bgetElementById\s*\(", masked)),
        event_listeners_added=len(re.findall(r"\baddEventListener\s*\(", masked)),
        event_listeners_removed=len(re.findall(r"\bremoveEventListener\s*\(", masked)),
        mutation_observers=len(re.findall(r"\bnew\s+MutationObserver\s*\(", masked)),
        resize_observers=len(re.findall(r"\bnew\s+ResizeObserver\s*\(", masked)),
        intersection_observers=len(re.findall(r"\bnew\s+IntersectionObserver\s*\(", masked)),
        intervals_created=len(re.findall(r"\bsetInterval\s*\(", masked)),
        intervals_cleared=len(re.findall(r"\bclearInterval\s*\(", masked)),
        timeouts_created=len(re.findall(r"\bsetTimeout\s*\(", masked)),
        timeouts_cleared=len(re.findall(r"\bclearTimeout\s*\(", masked)),
        animation_frames_created=len(re.findall(r"\brequestAnimationFrame\s*\(", masked)),
        animation_frames_cancelled=len(re.findall(r"\bcancelAnimationFrame\s*\(", masked)),
        inner_html_assignments=len(re.findall(r"\.innerHTML\s*=", masked)),
        insert_adjacent_html_calls=len(re.findall(r"\binsertAdjacentHTML\s*\(", masked)),
        local_storage_reads=len(re.findall(r"\blocalStorage\.getItem\s*\(", masked)),
        local_storage_writes=len(re.findall(r"\blocalStorage\.(?:setItem|removeItem|clear)\s*\(", masked)),
        gm_reads=len(re.findall(r"\bGM_getValue\s*\(", masked)),
        gm_writes=len(re.findall(r"\bGM_(?:setValue|deleteValue)\s*\(", masked)),
        css_template_blocks=len(css_blocks),
    )

    details = {
        "version": version,
        "syntax": {"passed": syntax_ok, "output": syntax_output},
        "metadata": meta,
        "functionInventory": [asdict(item) for item in functions],
        "largestFunctions": [asdict(item) for item in sorted(functions, key=lambda item: item.body_lines, reverse=True)[:30]],
        "mostComplexFunctions": [asdict(item) for item in sorted(functions, key=lambda item: item.complexity, reverse=True)[:30]],
        "eventTypesAdded": dict(add_events.most_common()),
        "eventTypesRemoved": dict(remove_events.most_common()),
        "intervalLiterals": [{"milliseconds": delay, "line": line} for delay, line in interval_literals],
        "repeatedSelectors": [
            {"selector": selector, "count": count, "lines": selector_lines[selector][:30]}
            for selector, count in selectors.most_common(50)
            if count > 1
        ],
        "storageKeys": dict(storage_keys.most_common()),
        "remoteHosts": dict(remote_hosts.most_common()),
    }
    return metrics, findings, details


def render_markdown(metrics: AuditMetrics, findings: list[Finding], details: dict) -> str:
    counts = Counter(item.severity for item in findings)
    lines = [
        "# Full Userscript Audit",
        "",
        f"- Version: `{details.get('version') or 'unknown'}`",
        f"- SHA-256: `{metrics.sha256}`",
        f"- Size: `{metrics.bytes:,}` bytes across `{metrics.lines:,}` lines",
        f"- Result: `{'FAILED' if counts['failure'] else 'PASSED WITH REVIEW ITEMS' if findings else 'PASSED'}`",
        f"- Findings: failures `{counts['failure']}`, review `{counts['review']}`, candidates `{counts['candidate']}`, advisories `{counts['advisory']}`",
        "",
        "## Structural metrics",
        "",
        "| Metric | Count |",
        "|---|---:|",
    ]
    metric_labels = {
        "functions": "Named function-like blocks",
        "anonymous_functions": "Anonymous function expressions",
        "arrow_functions": "Arrow expressions",
        "classes": "Classes",
        "const_declarations": "const declarations",
        "let_declarations": "let declarations",
        "var_declarations": "var declarations",
        "query_selector_calls": "querySelector calls",
        "query_selector_all_calls": "querySelectorAll calls",
        "get_element_by_id_calls": "getElementById calls",
        "event_listeners_added": "Event listeners added",
        "event_listeners_removed": "Event listeners removed",
        "mutation_observers": "MutationObservers",
        "resize_observers": "ResizeObservers",
        "intersection_observers": "IntersectionObservers",
        "intervals_created": "Intervals created",
        "intervals_cleared": "Intervals cleared",
        "timeouts_created": "Timeouts created",
        "timeouts_cleared": "Timeouts cleared",
        "animation_frames_created": "Animation frames requested",
        "animation_frames_cancelled": "Animation frames cancelled",
        "inner_html_assignments": "innerHTML assignments",
        "insert_adjacent_html_calls": "insertAdjacentHTML calls",
        "local_storage_reads": "localStorage reads",
        "local_storage_writes": "localStorage writes",
        "gm_reads": "GM reads",
        "gm_writes": "GM writes",
        "css_template_blocks": "Generated CSS blocks",
    }
    raw_metrics = asdict(metrics)
    for key, label in metric_labels.items():
        lines.append(f"| {label} | {raw_metrics[key]:,} |")

    lines.extend(["", "## Largest functions", "", "| Function | Line | Lines | Complexity | Queries | Listeners | Timers |", "|---|---:|---:|---:|---:|---:|---:|"])
    for item in details["largestFunctions"][:20]:
        lines.append(
            f"| `{item['name']}` | {item['line']} | {item['body_lines']} | {item['complexity']} | {item['query_calls']} | {item['listener_calls']} | {item['timer_calls']} |"
        )

    severity_order = ["failure", "review", "candidate", "advisory"]
    for severity in severity_order:
        selected = [item for item in findings if item.severity == severity]
        if not selected:
            continue
        lines.extend(["", f"## {severity.title()} findings", ""])
        for item in selected:
            location = f" · line {item.line}" if item.line else ""
            subject = f" · `{item.subject}`" if item.subject else ""
            lines.append(f"- **{item.code}**{location}{subject}: {item.message}")
            if item.evidence:
                lines.append(f"  - Evidence: `{item.evidence[:600]}`")

    lines.extend(["", "## Interpretation", "", "- `failure`: definite structural defect; workflow fails.", "- `review`: potentially unsafe or expensive code requiring direct source inspection.", "- `candidate`: possible dead or redundant code; never remove automatically.", "- `advisory`: maintainability or optimisation opportunity that may be intentional.", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    parser.add_argument("--json-output", type=Path, default=Path("full-userscript-audit.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("full-userscript-audit.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics, findings, details = audit(args.source.resolve(), args.dist.resolve() if args.dist else None)
    payload = {
        "schemaVersion": 1,
        "metrics": asdict(metrics),
        "summary": dict(Counter(item.severity for item in findings)),
        "findings": [asdict(item) for item in findings],
        "details": details,
    }
    args.json_output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(metrics, findings, details), encoding="utf-8")
    print(json.dumps({
        "result": "failed" if any(item.severity == "failure" for item in findings) else "passed",
        "metrics": asdict(metrics),
        "findings": dict(Counter(item.severity for item in findings)),
    }, indent=2))
    return 1 if any(item.severity == "failure" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
