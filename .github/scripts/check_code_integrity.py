#!/usr/bin/env python3
"""Static structural-integrity audit for MissionChief Map Command Toolkit."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DEFAULT_POLICY = ROOT / ".github" / "code-integrity-policy.json"
METADATA_START = "// ==UserScript=="
METADATA_END = "// ==/UserScript=="
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
LEFT_CONFLICT_RE = re.compile(r"^<<<<<<<\s+.+$", re.MULTILINE)
RIGHT_CONFLICT_RE = re.compile(r"^>>>>>>>\s+.+$", re.MULTILINE)
URL_RE = re.compile(r"https?://[^\s'\"`<>\\)]+")
IDENT = r"[A-Za-z_$][\w$]*"
SYMBOL = rf"{IDENT}(?:\.{IDENT})*"

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("discord-webhook", re.compile(r"https://(?:canary\.|ptb\.)?(?:discord(?:app)?\.com)/api/webhooks/\d{8,}/[A-Za-z0-9._-]{20,}")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Z0-9]{8,}/[A-Z0-9]{8,}/[A-Za-z0-9]{20,}")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
)

CONST_ID_RE = re.compile(
    rf"\b(?:const|let|var)\s+(?P<name>{IDENT}(?:_ID|Id|ID))\s*=\s*"
    r"(?P<q>['\"])(?P<value>[^'\"\r\n]+)(?P=q)"
)
OBJECT_START_RE = re.compile(
    rf"\b(?:const|let|var)\s+(?P<name>{IDENT})\s*=\s*"
    r"(?:Object\.freeze\s*\(\s*)?\{"
)
OBJECT_ID_PROP_RE = re.compile(
    rf"(?<![.\w])(?P<prop>{IDENT}(?:Id|ID))\s*:\s*"
    r"(?P<q>['\"])(?P<value>[^'\"\r\n]+)(?P=q)"
)
DIRECT_ID_LITERAL_RE = re.compile(
    r"\.id\s*(?<![=!])=(?!=)\s*(?P<q>['\"])(?P<value>[A-Za-z][A-Za-z0-9_:.-]*)(?P=q)"
)
DIRECT_ID_SYMBOL_RE = re.compile(
    rf"\.id\s*(?<![=!])=(?!=)\s*(?P<symbol>{SYMBOL})\b"
)
SET_ID_LITERAL_RE = re.compile(
    r"\.setAttribute\(\s*(['\"])id\1\s*,\s*(?P<q>['\"])(?P<value>[A-Za-z][A-Za-z0-9_:.-]*)(?P=q)\s*\)"
)
SET_ID_SYMBOL_RE = re.compile(
    rf"\.setAttribute\(\s*(['\"])id\1\s*,\s*(?P<symbol>{SYMBOL})\s*\)"
)
HTML_TAG_ID_RE = re.compile(
    r"<[A-Za-z][^<>]{0,1800}?\bid\s*=\s*(?P<q>['\"`])(?P<value>.*?)(?P=q)",
    re.S,
)
TEMPLATE_SYMBOL_RE = re.compile(rf"\$\{{\s*(?P<symbol>{SYMBOL})\s*\}}")

FLOAT_SHORTCUT_RE = re.compile(
    r"\b(?P<fn>make(?:Action)?FloatButton)\s*\(\s*"
    r"(?P<q1>['\"])(?P<action>[^'\"]+)(?P=q1)\s*,\s*"
    r"(?P<q2>['\"])(?P<shortcut>[^'\"]+)(?P=q2)"
)
KEYDOWN_INLINE_RE = re.compile(r"(?:addEventListener|runtimeListen)\s*\([^;\n]{0,500}?['\"]keydown['\"]", re.I)
KEYDOWN_NAMED_RE = re.compile(
    rf"(?:addEventListener|runtimeListen)\s*\([^;\n]{{0,500}}?['\"]keydown['\"]\s*,\s*(?P<handler>{IDENT})\b",
    re.I,
)
FUNCTION_DECL_RE_TEMPLATE = r"\bfunction\s+{name}\s*\([^)]*\)\s*\{{"
KEY_COMPARISON_RE = re.compile(
    r"(?P<event>[A-Za-z_$][\w$]*)\.(?P<field>key|code)\s*(?:===|==)\s*([\"'])(?P<key>[^\"']+)\3"
    r"|([\"'])(?P<reverse_key>[^\"']+)\5\s*(?:===|==)\s*(?P<reverse_event>[A-Za-z_$][\w$]*)\.(?P<reverse_field>key|code)"
)
KEY_VARIABLE_COMPARISON_RE = re.compile(r"(?<![.\w])key\s*(?:===|==)\s*(['\"])(?P<key>[^'\"]+)\1")
CASE_RE = re.compile(r"\bcase\s+([\"'])(?P<key>[^\"']+)\1\s*:")
KEY_ACTION_MAP_RE = re.compile(
    r"(?P<q1>['\"])(?P<key>[^'\"]+)(?P=q1)\s*:\s*(?P<q2>['\"])(?P<action>[^'\"]+)(?P=q2)"
)
DATA_SHORTCUT_RE = re.compile(r"\bdata-(?:hotkey|shortcut)\s*=\s*([\"'])(?P<key>[^\"']+)\1", re.I)
SELECTOR_CALL_RE = re.compile(r"\b(?:querySelector|querySelectorAll|matches|closest)\s*\(")
NAVIGATION_KEYS = {"esc", "enter", "space", "tab", "home", "end", "up", "down", "left", "right"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    subject: str = ""
    path: str = ""
    line: int | None = None


@dataclass(frozen=True)
class LiteralOccurrence:
    value: str
    line: int
    kind: str


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def metadata(text: str) -> tuple[dict[str, list[str]], list[Finding]]:
    findings: list[Finding] = []
    start, end = text.find(METADATA_START), text.find(METADATA_END)
    if start < 0 or end < 0 or end <= start:
        return {}, [Finding("failure", "metadata-block", "Userscript metadata block is missing or malformed.")]
    result: dict[str, list[str]] = defaultdict(list)
    for index, raw_line in enumerate(text[start:end].splitlines(), start=line_number(text, start)):
        stripped = raw_line.strip()
        if not stripped or stripped == METADATA_START:
            continue
        match = re.match(r"^//\s*@([A-Za-z0-9:_-]+)\s+(.+?)\s*$", raw_line)
        if match:
            result[match.group(1).lower()].append(match.group(2))
        elif stripped.startswith("// @"):
            findings.append(Finding("failure", "metadata-line", "Malformed metadata directive.", raw_line.strip(), line=index))
    return dict(result), findings


def validate_metadata(text: str, policy: dict) -> tuple[dict[str, list[str]], list[Finding]]:
    meta, findings = metadata(text)
    if not meta:
        return meta, findings
    config = policy.get("metadata", {})
    for key in config.get("requiredSingle", ["name", "version"]):
        values = meta.get(key, [])
        if len(values) != 1:
            findings.append(Finding("failure", "metadata-cardinality", f"@{key} must appear exactly once; found {len(values)}.", key))
    versions = meta.get("version", [])
    if len(versions) == 1 and not VERSION_RE.fullmatch(versions[0]):
        findings.append(Finding("failure", "metadata-version", f"Invalid semantic @version: {versions[0]}", versions[0]))
    for key, expected in config.get("contains", {}).items():
        values = meta.get(key, [])
        if len(values) == 1 and str(expected).casefold() not in values[0].casefold():
            findings.append(Finding("failure", "metadata-value", f"@{key} must contain {expected!r}; found {values[0]!r}.", key))
    for key, expected in config.get("exact", {}).items():
        values = meta.get(key, [])
        if len(values) == 1 and values[0].strip().casefold() != str(expected).strip().casefold():
            findings.append(Finding("failure", "metadata-value", f"@{key} must equal {expected!r}; found {values[0]!r}.", key))
    rules = meta.get("match", []) + meta.get("include", [])
    host = str(config.get("requiredHost", "missionchief.co.uk")).casefold()
    if host and not any(host in value.casefold() for value in rules):
        findings.append(Finding("failure", "metadata-host", f"No @match or @include entry targets {host}.", host))
    for key in ("downloadurl", "updateurl", "homepageurl", "supporturl"):
        for value in meta.get(key, []):
            if value.startswith("http://"):
                findings.append(Finding("failure", "metadata-insecure-url", f"@{key} uses insecure HTTP.", value))
    return meta, findings


def _find_matching_brace(text: str, open_pos: int, max_chars: int = 2_000_000) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = line_comment = block_comment = False
    limit, i = min(len(text), open_pos + max_chars), open_pos
    while i < limit:
        ch, nxt = text[i], text[i + 1] if i + 1 < limit else ""
        if line_comment:
            if ch == "\n": line_comment = False
            i += 1; continue
        if block_comment:
            if ch == "*" and nxt == "/": block_comment = False; i += 2
            else: i += 1
            continue
        if quote:
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if ch == "/" and nxt == "/": line_comment = True; i += 2; continue
        if ch == "/" and nxt == "*": block_comment = True; i += 2; continue
        if ch in "'\"`": quote = ch; i += 1; continue
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: return i
        i += 1
    return None


def resolve_id_symbols(text: str) -> dict[str, str]:
    symbols: dict[str, str] = {}
    for match in CONST_ID_RE.finditer(text):
        symbols[match.group("name")] = match.group("value")
    for start in OBJECT_START_RE.finditer(text):
        open_pos = text.find("{", start.start(), start.end() + 2)
        if open_pos < 0:
            continue
        close_pos = _find_matching_brace(text, open_pos)
        if close_pos is None:
            continue
        body = text[open_pos + 1:close_pos]
        object_name = start.group("name")
        for prop in OBJECT_ID_PROP_RE.finditer(body):
            symbols[f"{object_name}.{prop.group('prop')}"] = prop.group("value")
    return symbols


def resolve_template_id(value: str, symbols: dict[str, str]) -> str | None:
    if "${" not in value:
        return value if re.fullmatch(r"[A-Za-z][A-Za-z0-9_:.-]*", value) else None
    unresolved = False
    def replace(match: re.Match[str]) -> str:
        nonlocal unresolved
        resolved = symbols.get(match.group("symbol"))
        if resolved is None:
            unresolved = True
            return ""
        return resolved
    result = TEMPLATE_SYMBOL_RE.sub(replace, value)
    if unresolved or "${" in result:
        return None
    return result if re.fullmatch(r"[A-Za-z][A-Za-z0-9_:.-]*", result) else None


def extract_static_ids(text: str) -> list[LiteralOccurrence]:
    symbols = resolve_id_symbols(text)
    result: list[LiteralOccurrence] = []
    seen: set[tuple[int, str, str]] = set()
    def add(value: str | None, offset: int, kind: str) -> None:
        if not value:
            return
        key = (offset, value, kind)
        if key in seen:
            return
        seen.add(key)
        result.append(LiteralOccurrence(value, line_number(text, offset), kind))

    for match in DIRECT_ID_LITERAL_RE.finditer(text):
        add(match.group("value"), match.start(), "property-literal")
    for match in DIRECT_ID_SYMBOL_RE.finditer(text):
        add(symbols.get(match.group("symbol")), match.start(), f"property-symbol:{match.group('symbol')}")
    for match in SET_ID_LITERAL_RE.finditer(text):
        add(match.group("value"), match.start(), "attribute-literal")
    for match in SET_ID_SYMBOL_RE.finditer(text):
        add(symbols.get(match.group("symbol")), match.start(), f"attribute-symbol:{match.group('symbol')}")
    for match in HTML_TAG_ID_RE.finditer(text):
        add(resolve_template_id(match.group("value"), symbols), match.start(), "html-tag")
    return sorted(result, key=lambda item: (item.line, item.value, item.kind))


def normalize_key(value: str, field: str = "key") -> str:
    raw = value.strip().casefold()
    aliases = {" ": "space", "spacebar": "space", "escape": "esc", "arrowup": "up", "arrowdown": "down", "arrowleft": "left", "arrowright": "right"}
    if field == "code" and raw.startswith("key") and len(raw) == 4: raw = raw[-1]
    if field == "code" and raw.startswith("digit") and len(raw) == 6: raw = raw[-1]
    return aliases.get(raw, raw)


def _function_region(text: str, name: str) -> tuple[int, int] | None:
    pattern = re.compile(FUNCTION_DECL_RE_TEMPLATE.format(name=re.escape(name)))
    match = pattern.search(text)
    if not match:
        return None
    open_pos = text.find("{", match.start(), match.end())
    close_pos = _find_matching_brace(text, open_pos)
    return (match.start(), close_pos + 1) if close_pos is not None else None


def keydown_regions(text: str) -> list[tuple[int, int]]:
    regions: list[tuple[int, int]] = []
    for registration in KEYDOWN_NAMED_RE.finditer(text):
        region = _function_region(text, registration.group("handler"))
        if region:
            regions.append(region)
    for match in KEYDOWN_INLINE_RE.finditer(text):
        tail = text[match.end():match.end() + 500]
        if re.match(r"\s*,?\s*[A-Za-z_$][\w$]*\s*\)?", tail):
            continue
        open_pos = text.find("{", match.end(), min(len(text), match.end() + 1500))
        if open_pos >= 0:
            close_pos = _find_matching_brace(text, open_pos)
            if close_pos is not None:
                regions.append((match.start(), close_pos + 1))
    compact: list[tuple[int, int]] = []
    for start, end in sorted(set(regions)):
        if compact and start >= compact[-1][0] and end <= compact[-1][1]:
            continue
        compact.append((start, end))
    return compact


def _binding_action(region: str, match_end: int, fallback: str) -> str:
    tail = region[match_end:match_end + 280]
    call = re.search(r"\b(toggleFeature|togglePanel|toggleVehicleCodeStatus|toggleCriticalDrawer|close[A-Za-z_$][\w$]*)\s*\(([^;}]*)", tail)
    if call:
        return f"{call.group(1)}:{re.sub(r'\s+', '', call.group(2))[:100]}"
    return fallback


def extract_shortcut_contract(text: str) -> tuple[list[LiteralOccurrence], dict[str, list[LiteralOccurrence]], list[Finding]]:
    bindings: list[LiteralOccurrence] = []
    visible: dict[str, list[LiteralOccurrence]] = defaultdict(list)
    handlers: dict[str, list[LiteralOccurrence]] = defaultdict(list)
    findings: list[Finding] = []

    for match in FLOAT_SHORTCUT_RE.finditer(text):
        key = normalize_key(match.group("shortcut"))
        occurrence = LiteralOccurrence(key, line_number(text, match.start()), f"button:{match.group('action')}")
        visible[key].append(occurrence); bindings.append(occurrence)

    for start, end in keydown_regions(text):
        region = text[start:end]
        region_line = line_number(text, start)
        for match in KEY_COMPARISON_RE.finditer(region):
            key = normalize_key(match.group("key") or match.group("reverse_key") or "", match.group("field") or match.group("reverse_field") or "key")
            if not key or key in NAVIGATION_KEYS:
                continue
            action = _binding_action(region, match.end(), "comparison")
            occurrence = LiteralOccurrence(key, region_line + region.count("\n", 0, match.start()), f"handler:{action}")
            handlers[key].append(occurrence); bindings.append(occurrence)
        for match in KEY_VARIABLE_COMPARISON_RE.finditer(region):
            key = normalize_key(match.group("key"))
            if not key or key in NAVIGATION_KEYS:
                continue
            action = _binding_action(region, match.end(), "key-variable")
            occurrence = LiteralOccurrence(key, region_line + region.count("\n", 0, match.start()), f"handler:{action}")
            handlers[key].append(occurrence); bindings.append(occurrence)
        for map_match in re.finditer(r"\b(?:const|let|var)\s+\w+Shortcut\s*=\s*\{(?P<body>[^{}]{1,4000})\}", region, re.S):
            for item in KEY_ACTION_MAP_RE.finditer(map_match.group("body")):
                key = normalize_key(item.group("key"))
                occurrence = LiteralOccurrence(key, region_line + region.count("\n", 0, map_match.start() + item.start()), f"handler-map:{item.group('action')}")
                handlers[key].append(occurrence); bindings.append(occurrence)
        if re.search(r"\bswitch\s*\([^)]*\.(?:key|code)\b", region):
            for match in CASE_RE.finditer(region):
                key = normalize_key(match.group("key"))
                if key in NAVIGATION_KEYS:
                    continue
                occurrence = LiteralOccurrence(key, region_line + region.count("\n", 0, match.start()), "handler-case")
                handlers[key].append(occurrence); bindings.append(occurrence)

    for match in DATA_SHORTCUT_RE.finditer(text):
        key = normalize_key(match.group("key"))
        occurrence = LiteralOccurrence(key, line_number(text, match.start()), "data-shortcut")
        visible[key].append(occurrence); bindings.append(occurrence)

    conflict_map: dict[str, list[LiteralOccurrence]] = {}
    for key, occurrences in visible.items():
        actions = {item.kind for item in occurrences}
        if len(actions) > 1:
            conflict_map[key] = occurrences
    for key, occurrences in handlers.items():
        actions = {item.kind for item in occurrences}
        if len(actions) > 1:
            normalized_actions = {action.split(":", 2)[-1] for action in actions}
            if len(normalized_actions) > 1:
                conflict_map[key] = sorted(set(conflict_map.get(key, []) + occurrences), key=lambda item: (item.line, item.kind))

    for key, occurrences in sorted(visible.items()):
        if key not in handlers:
            findings.append(Finding("failure", "unhandled-visible-shortcut", "Visible shortcut is not handled by a registered keydown handler.", key, line=occurrences[0].line))

    unique_bindings = sorted({(item.value, item.line, item.kind): item for item in bindings}.values(), key=lambda item: (item.line, item.value, item.kind))
    return unique_bindings, conflict_map, findings


def _scan_quoted_literal(text: str, start: int) -> tuple[str, int] | None:
    quote = text[start]
    if quote not in "'\"`": return None
    value: list[str] = []; escaped = False; i = start + 1
    while i < len(text):
        ch = text[i]
        if escaped: value.append(ch); escaped = False
        elif ch == "\\": value.append(ch); escaped = True
        elif ch == quote: return "".join(value), i + 1
        else: value.append(ch)
        i += 1
    return None


def extract_static_selectors(text: str) -> list[LiteralOccurrence]:
    result: list[LiteralOccurrence] = []
    for call in SELECTOR_CALL_RE.finditer(text):
        i = call.end()
        while i < len(text) and text[i].isspace(): i += 1
        if i >= len(text) or text[i] not in "'\"`": continue
        parsed = _scan_quoted_literal(text, i)
        if not parsed: continue
        selector, end = parsed
        if "${" in selector: continue
        j = end
        while j < len(text) and text[j].isspace(): j += 1
        if j >= len(text) or text[j] not in "),": continue
        result.append(LiteralOccurrence(selector, line_number(text, call.start()), "selector"))
    return result


def selector_error(selector: str) -> str | None:
    value = selector.strip()
    if not value: return "selector is empty"
    if value.endswith((">", "+", "~", ",")): return "selector ends with a combinator or comma"
    if re.search(r"(^|,)\s*,", value): return "selector contains an empty comma-separated group"
    if re.search(r"(?:^|[\s>+~,])(?:#|\.)($|[\s>+~,])", value): return "selector contains a bare ID or class marker"
    stack: list[str] = []; quote: str | None = None; escaped = False; pairs = {")": "(", "]": "["}
    for ch in value:
        if escaped: escaped = False; continue
        if ch == "\\": escaped = True; continue
        if quote:
            if ch == quote: quote = None
            continue
        if ch in "'\"": quote = ch; continue
        if ch in "([": stack.append(ch)
        elif ch in ")]":
            if not stack or stack[-1] != pairs[ch]: return f"selector has unmatched {ch}"
            stack.pop()
    if quote: return "selector has an unterminated quote"
    if stack: return f"selector has unmatched {stack[-1]}"
    return None


def duplicate_map(items: Iterable[LiteralOccurrence]) -> dict[str, list[LiteralOccurrence]]:
    grouped: dict[str, list[LiteralOccurrence]] = defaultdict(list)
    for item in items: grouped[item.value].append(item)
    return {key: values for key, values in grouped.items() if len(values) > 1}


def compare_duplicate_sets(candidate: dict[str, list[LiteralOccurrence]], base: dict[str, list[LiteralOccurrence]], code_prefix: str, allowed: set[str]) -> list[Finding]:
    findings: list[Finding] = []; allowed_folded = {entry.casefold() for entry in allowed}
    for value, occurrences in sorted(candidate.items()):
        if value.casefold() in allowed_folded: continue
        base_count, candidate_count = len(base.get(value, [])), len(occurrences)
        if base_count == 0:
            lines = ", ".join(str(item.line) for item in occurrences[:8])
            findings.append(Finding("failure", f"new-{code_prefix}", f"New duplicate {code_prefix.replace('-', ' ')} {value!r} appears {candidate_count} times (lines {lines}).", value))
        elif candidate_count > base_count:
            findings.append(Finding("failure", f"increased-{code_prefix}", f"Duplicate {code_prefix.replace('-', ' ')} {value!r} increased from {base_count} to {candidate_count} occurrences.", value))
    return findings


def tracked_files(root: Path, policy: dict) -> Iterator[Path]:
    try:
        output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root, stderr=subprocess.DEVNULL)
        names = [entry.decode("utf-8") for entry in output.split(b"\0") if entry]
    except Exception:
        names = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() and ".git" not in path.parts]
    cfg = policy.get("repository", {})
    extensions = {entry.casefold() for entry in cfg.get("textExtensions", [])}
    excluded = tuple(cfg.get("excludedPrefixes", [])); file_names = set(cfg.get("textFileNames", [])); max_bytes = int(cfg.get("maxTextFileBytes", 5_000_000))
    for name in names:
        if excluded and any(name == prefix or name.startswith(prefix.rstrip("/") + "/") for prefix in excluded): continue
        path = root / name
        if not path.is_file() or path.stat().st_size > max_bytes: continue
        if extensions and path.suffix.casefold() not in extensions and path.name not in file_names: continue
        yield path


def scan_repository(root: Path, policy: dict) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []; scanned_files = scanned_bytes = 0
    secret_excluded = set(policy.get("secrets", {}).get("excludedPaths", []))
    for path in tracked_files(root, policy):
        relative = path.relative_to(root).as_posix()
        try: raw = path.read_bytes(); text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError): continue
        scanned_files += 1; scanned_bytes += len(raw)
        if LEFT_CONFLICT_RE.search(text) or RIGHT_CONFLICT_RE.search(text):
            findings.append(Finding("failure", "merge-conflict-marker", "Unresolved merge-conflict marker found.", relative, relative))
        if relative not in secret_excluded:
            for code, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    findings.append(Finding("failure", "exposed-secret", f"High-confidence {code} value is committed in repository text.", code, relative, line_number(text, match.start())))
    return findings, {"files": scanned_files, "bytes": scanned_bytes}


def scan_asset_references(text: str, root: Path, policy: dict) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []; urls = sorted(set(URL_RE.findall(text)))
    cfg = policy.get("assets", {}); allowed_http = set(cfg.get("allowedHttpHosts", ["localhost", "127.0.0.1"])); same_repo = str(cfg.get("sameRepository", "Conroy1988/missionchief-toolkit-assets"))
    missing = insecure = blob_runtime = 0
    for url in urls:
        parsed = urlparse(url); host = (parsed.hostname or "").casefold()
        if parsed.scheme == "http" and host not in allowed_http:
            insecure += 1; findings.append(Finding("failure", "insecure-runtime-url", "Runtime URL uses insecure HTTP.", url))
        if host == "github.com" and "/blob/" in parsed.path and re.search(r"\.(?:png|jpe?g|gif|webp|svg|mp3|wav|ogg)(?:$|[?#])", url, re.I):
            blob_runtime += 1; findings.append(Finding("failure", "github-blob-asset-url", "Runtime media uses a GitHub blob page instead of a raw or release URL.", url))
        if host == "raw.githubusercontent.com":
            parts = [unquote(part) for part in parsed.path.strip("/").split("/")]
            if len(parts) >= 4:
                repo, ref, relative = f"{parts[0]}/{parts[1]}", parts[2], "/".join(parts[3:])
                if repo.casefold() == same_repo.casefold() and ref == "main" and not (root / relative).is_file():
                    missing += 1; findings.append(Finding("failure", "missing-raw-asset", "Same-repository raw URL does not resolve to a committed file.", url, relative))
    return findings, {"urls": len(urls), "insecureUrls": insecure, "blobAssetUrls": blob_runtime, "missingSameRepositoryAssets": missing}


def analyse_source(path: Path, policy: dict) -> dict:
    text = read_text(path); meta, metadata_findings = validate_metadata(text, policy)
    ids = extract_static_ids(text); shortcuts, shortcut_conflicts, shortcut_findings = extract_shortcut_contract(text); selectors = extract_static_selectors(text)
    selector_findings: list[Finding] = []
    for occurrence in selectors:
        error = selector_error(occurrence.value)
        if error: selector_findings.append(Finding("failure", "malformed-static-selector", f"Malformed static selector: {error}.", occurrence.value, str(path), occurrence.line))
    return {"text": text, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "metadata": meta, "metadataFindings": metadata_findings, "ids": ids, "duplicateIds": duplicate_map(ids), "shortcuts": shortcuts, "shortcutConflicts": shortcut_conflicts, "shortcutFindings": shortcut_findings, "selectors": selectors, "selectorFindings": selector_findings}


def finding_key(finding: Finding) -> tuple:
    return (finding.severity, finding.code, finding.path, finding.line or 0, finding.subject, finding.message)


def build_report(candidate_path: Path, base_path: Path | None, policy: dict, root: Path) -> tuple[dict, int]:
    candidate = analyse_source(candidate_path, policy); base = analyse_source(base_path, policy) if base_path and base_path.exists() else None
    findings: list[Finding] = [*candidate["metadataFindings"], *candidate["selectorFindings"], *candidate["shortcutFindings"]]
    duplicate_policy, shortcut_policy = policy.get("duplicateIds", {}), policy.get("shortcuts", {})
    if base:
        findings.extend(compare_duplicate_sets(candidate["duplicateIds"], base["duplicateIds"], "interface-id", set(duplicate_policy.get("allow", []))))
        findings.extend(compare_duplicate_sets(candidate["shortcutConflicts"], base["shortcutConflicts"], "shortcut-conflict", set(shortcut_policy.get("allow", []))))
    else:
        if duplicate_policy.get("failWithoutBaseline", False): findings.extend(compare_duplicate_sets(candidate["duplicateIds"], {}, "interface-id", set(duplicate_policy.get("allow", []))))
        if shortcut_policy.get("failWithoutBaseline", False): findings.extend(compare_duplicate_sets(candidate["shortcutConflicts"], {}, "shortcut-conflict", set(shortcut_policy.get("allow", []))))
    repository_findings, repository_metrics = scan_repository(root, policy); findings.extend(repository_findings)
    asset_findings, asset_metrics = scan_asset_references(candidate["text"], root, policy); findings.extend(asset_findings)
    unique = sorted({finding_key(item): item for item in findings}.values(), key=finding_key)
    failures = [item for item in unique if item.severity == "failure"]; warnings = [item for item in unique if item.severity == "warning"]
    try: candidate_display = str(candidate_path.relative_to(root))
    except ValueError: candidate_display = str(candidate_path)
    report = {
        "schemaVersion": 2,
        "candidate": {"path": candidate_display, "sha256": candidate["sha256"]},
        "base": {"path": str(base_path) if base_path else None, "sha256": base["sha256"] if base else None, "available": bool(base)},
        "metrics": {"metadataKeys": len(candidate["metadata"]), "staticIds": len(candidate["ids"]), "duplicateIdValues": len(candidate["duplicateIds"]), "shortcutBindings": len(candidate["shortcuts"]), "shortcutConflictValues": len(candidate["shortcutConflicts"]), "staticSelectors": len(candidate["selectors"]), "repositoryTextFiles": repository_metrics["files"], "repositoryTextBytes": repository_metrics["bytes"], **asset_metrics},
        "interfaceIds": [asdict(item) for item in candidate["ids"]],
        "shortcutBindings": [asdict(item) for item in candidate["shortcuts"]],
        "duplicateIds": {key: [asdict(item) for item in values] for key, values in sorted(candidate["duplicateIds"].items())},
        "shortcutConflicts": {key: [asdict(item) for item in values] for key, values in sorted(candidate["shortcutConflicts"].items())},
        "findings": [asdict(item) for item in unique],
        "summary": {"failures": len(failures), "warnings": len(warnings), "result": "failed" if failures else "passed"},
    }
    return report, 1 if failures else 0


def markdown(report: dict) -> str:
    m, s = report["metrics"], report["summary"]
    lines = ["# Toolkit code-integrity audit", "", f"- Result: **{s['result'].upper()}**", f"- Failures: **{s['failures']}**", f"- Warnings: **{s['warnings']}**", f"- Baseline available: **{'yes' if report['base']['available'] else 'no'}**", "", "## Inventory", "", f"- Resolved static interface IDs: **{m['staticIds']}**", f"- Duplicate interface ID values: **{m['duplicateIdValues']}**", f"- Detected shortcut bindings: **{m['shortcutBindings']}**", f"- Shortcut conflict values: **{m['shortcutConflictValues']}**", f"- Fully static selectors validated: **{m['staticSelectors']}**", f"- Runtime URLs inspected: **{m['urls']}**", f"- Repository text files scanned: **{m['repositoryTextFiles']}**", ""]
    lines.extend(["## Findings", ""])
    if report["findings"]:
        for item in report["findings"]:
            location = ""
            if item.get("path"):
                location = f" — `{item['path']}" + (f":{item['line']}" if item.get("line") else "") + "`"
            subject = f" (`{item['subject']}`)" if item.get("subject") else ""
            icon = "❌" if item["severity"] == "failure" else "⚠️"
            lines.append(f"- {icon} **{item['code']}**{subject}: {item['message']}{location}")
    else: lines.append("No integrity failures or warnings were detected.")
    lines.extend(["", "## Resolved interface-ID inventory", ""])
    for item in report.get("interfaceIds", [])[:120]: lines.append(f"- `{item['value']}` — line {item['line']} ({item['kind']})")
    lines.extend(["", "## Shortcut binding inventory", ""])
    for item in report.get("shortcutBindings", [])[:120]: lines.append(f"- `{item['value']}` — line {item['line']} ({item['kind']})")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(); parser.add_argument("--candidate", type=Path, default=DEFAULT_SOURCE); parser.add_argument("--base", type=Path); parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY); parser.add_argument("--root", type=Path, default=ROOT); parser.add_argument("--json-output", type=Path, default=Path("code-integrity-report.json")); parser.add_argument("--markdown-output", type=Path, default=Path("code-integrity-report.md")); return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:]); root = args.root.resolve(); policy = json.loads(args.policy.read_text(encoding="utf-8")); report, status = build_report(args.candidate.resolve(), args.base.resolve() if args.base else None, policy, root); args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8"); args.markdown_output.write_text(markdown(report), encoding="utf-8"); print(json.dumps(report["summary"], indent=2)); return status

if __name__ == "__main__":
    raise SystemExit(main())
