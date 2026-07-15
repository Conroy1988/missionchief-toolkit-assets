#!/usr/bin/env python3
"""Static integrity audit for the MissionChief Map Command Toolkit.

The audit fails on high-confidence repository problems and on newly introduced
duplicate interface IDs or keyboard shortcut collisions relative to a supplied
baseline userscript.
"""

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

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "discord-webhook",
        re.compile(
            r"https://(?:canary\.|ptb\.)?(?:discord(?:app)?\.com)/api/webhooks/"
            r"\d{8,}/[A-Za-z0-9._-]{20,}"
        ),
    ),
    (
        "github-token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    ),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "slack-webhook",
        re.compile(
            r"https://hooks\.slack\.com/services/[A-Z0-9]{8,}/[A-Z0-9]{8,}/"
            r"[A-Za-z0-9]{20,}"
        ),
    ),
    (
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ),
)

STATIC_ID_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "html",
        re.compile(r"(?<![.\w])id\s*=\s*([\"'])([A-Za-z][A-Za-z0-9_:.-]*)\1"),
    ),
    (
        "property",
        re.compile(r"\.id\s*=\s*([\"'])([A-Za-z][A-Za-z0-9_:.-]*)\1"),
    ),
    (
        "attribute",
        re.compile(
            r"\.setAttribute\(\s*([\"'])id\1\s*,\s*([\"'])"
            r"([A-Za-z][A-Za-z0-9_:.-]*)\2\s*\)"
        ),
    ),
)

KEY_COMPARISON_RE = re.compile(
    r"(?P<event>[A-Za-z_$][\w$]*)\.(?P<field>key|code)\s*(?:===|==)\s*"
    r"([\"'])(?P<key>[^\"']+)\3"
    r"|([\"'])(?P<reverse_key>[^\"']+)\5\s*(?:===|==)\s*"
    r"(?P<reverse_event>[A-Za-z_$][\w$]*)\."
    r"(?P<reverse_field>key|code)"
)
CASE_RE = re.compile(r"\bcase\s+([\"'])(?P<key>[^\"']+)\1\s*:")
DATA_SHORTCUT_RE = re.compile(
    r"\bdata-(?:hotkey|shortcut)\s*=\s*([\"'])(?P<key>[^\"']+)\1",
    re.I,
)
KEYDOWN_RE = re.compile(
    r"(?:addEventListener\s*\(\s*['\"]keydown['\"]|onkeydown\s*=)",
    re.I,
)
SELECTOR_CALL_RE = re.compile(
    r"\b(?:querySelector|querySelectorAll|matches|closest)\s*\("
)


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
    start = text.find(METADATA_START)
    end = text.find(METADATA_END)
    if start < 0 or end < 0 or end <= start:
        return {}, [
            Finding(
                "failure",
                "metadata-block",
                "Userscript metadata block is missing or malformed.",
            )
        ]

    block = text[start:end].splitlines()
    result: dict[str, list[str]] = defaultdict(list)
    for index, raw_line in enumerate(block, start=line_number(text, start)):
        stripped = raw_line.strip()
        if not stripped or stripped == METADATA_START:
            continue
        match = re.match(
            r"^//\s*@([A-Za-z0-9:_-]+)\s+(.+?)\s*$",
            raw_line,
        )
        if match:
            result[match.group(1).lower()].append(match.group(2))
        elif stripped.startswith("// @"):
            findings.append(
                Finding(
                    "failure",
                    "metadata-line",
                    "Malformed metadata directive.",
                    raw_line.strip(),
                    line=index,
                )
            )
    return dict(result), findings


def validate_metadata(
    text: str,
    policy: dict,
) -> tuple[dict[str, list[str]], list[Finding]]:
    meta, findings = metadata(text)
    if not meta:
        return meta, findings

    config = policy.get("metadata", {})
    for key in config.get("requiredSingle", ["name", "version"]):
        values = meta.get(key, [])
        if len(values) != 1:
            findings.append(
                Finding(
                    "failure",
                    "metadata-cardinality",
                    f"@{key} must appear exactly once; found {len(values)}.",
                    key,
                )
            )

    version_values = meta.get("version", [])
    if len(version_values) == 1 and not VERSION_RE.fullmatch(version_values[0]):
        findings.append(
            Finding(
                "failure",
                "metadata-version",
                f"Invalid semantic @version: {version_values[0]}",
                version_values[0],
            )
        )

    for key, expected in config.get("contains", {}).items():
        values = meta.get(key, [])
        if len(values) == 1 and expected.casefold() not in values[0].casefold():
            findings.append(
                Finding(
                    "failure",
                    "metadata-value",
                    f"@{key} must contain {expected!r}; found {values[0]!r}.",
                    key,
                )
            )

    for key, expected in config.get("exact", {}).items():
        values = meta.get(key, [])
        if (
            len(values) == 1
            and values[0].strip().casefold()
            != str(expected).strip().casefold()
        ):
            findings.append(
                Finding(
                    "failure",
                    "metadata-value",
                    f"@{key} must equal {expected!r}; found {values[0]!r}.",
                    key,
                )
            )

    rules = meta.get("match", []) + meta.get("include", [])
    host = str(config.get("requiredHost", "missionchief.co.uk")).casefold()
    if host and not any(host in value.casefold() for value in rules):
        findings.append(
            Finding(
                "failure",
                "metadata-host",
                f"No @match or @include entry targets {host}.",
                host,
            )
        )

    for key in ("downloadurl", "updateurl", "homepageurl", "supporturl"):
        for value in meta.get(key, []):
            if value.startswith("http://"):
                findings.append(
                    Finding(
                        "failure",
                        "metadata-insecure-url",
                        f"@{key} uses insecure HTTP.",
                        value,
                    )
                )

    return meta, findings


def extract_static_ids(text: str) -> list[LiteralOccurrence]:
    seen_spans: set[tuple[int, int, str]] = set()
    result: list[LiteralOccurrence] = []
    for kind, pattern in STATIC_ID_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(3) if kind == "attribute" else match.group(2)
            key = (match.start(), match.end(), value)
            if key in seen_spans:
                continue
            seen_spans.add(key)
            result.append(
                LiteralOccurrence(
                    value,
                    line_number(text, match.start()),
                    kind,
                )
            )
    return result


def _find_matching_brace(
    text: str,
    open_pos: int,
    max_chars: int = 120_000,
) -> int | None:
    depth = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    limit = min(len(text), open_pos + max_chars)
    i = open_pos
    while i < limit:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < limit else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def keydown_regions(text: str) -> list[tuple[int, int]]:
    regions: list[tuple[int, int]] = []
    for match in KEYDOWN_RE.finditer(text):
        open_pos = text.find(
            "{",
            match.end(),
            min(len(text), match.end() + 1200),
        )
        if open_pos < 0:
            continue
        close_pos = _find_matching_brace(text, open_pos)
        if close_pos is not None:
            regions.append((match.start(), close_pos + 1))

    compact: list[tuple[int, int]] = []
    for start, end in sorted(regions):
        if compact and start >= compact[-1][0] and end <= compact[-1][1]:
            continue
        compact.append((start, end))
    return compact


def normalize_key(value: str, field: str = "key") -> str:
    raw = value.strip()
    aliases = {
        " ": "space",
        "spacebar": "space",
        "escape": "esc",
        "arrowup": "up",
        "arrowdown": "down",
        "arrowleft": "left",
        "arrowright": "right",
    }
    lowered = raw.casefold()
    if field == "code" and lowered.startswith("key") and len(lowered) == 4:
        lowered = lowered[-1]
    if field == "code" and lowered.startswith("digit") and len(lowered) == 6:
        lowered = lowered[-1]
    return aliases.get(lowered, lowered)


def modifier_prefix(context: str, event_name: str) -> str:
    modifiers: list[str] = []
    patterns = (
        ("ctrl", "ctrlKey"),
        ("alt", "altKey"),
        ("shift", "shiftKey"),
        ("meta", "metaKey"),
    )
    for label, prop in patterns:
        positive = re.search(
            rf"(?<![!.\w]){re.escape(event_name)}\.{prop}\b",
            context,
        )
        negated = re.search(
            rf"!\s*{re.escape(event_name)}\.{prop}\b|"
            rf"{re.escape(event_name)}\.{prop}\s*===?\s*false",
            context,
        )
        if positive and not negated:
            modifiers.append(label)
    return "+".join(modifiers)


def extract_shortcuts(text: str) -> list[LiteralOccurrence]:
    result: list[LiteralOccurrence] = []
    for handler_index, (start, end) in enumerate(keydown_regions(text), start=1):
        region = text[start:end]
        for match in KEY_COMPARISON_RE.finditer(region):
            key = match.group("key") or match.group("reverse_key") or ""
            event_name = (
                match.group("event")
                or match.group("reverse_event")
                or "event"
            )
            field = match.group("field") or match.group("reverse_field") or "key"
            context = region[
                max(0, match.start() - 260) : min(len(region), match.end() + 80)
            ]
            prefix = modifier_prefix(context, event_name)
            combo = normalize_key(key, field)
            if prefix:
                combo = f"{prefix}+{combo}"
            result.append(
                LiteralOccurrence(
                    combo,
                    line_number(text, start + match.start()),
                    f"keydown-{handler_index}",
                )
            )

        if re.search(r"\bswitch\s*\([^)]*\.(?:key|code)\b", region):
            for match in CASE_RE.finditer(region):
                result.append(
                    LiteralOccurrence(
                        normalize_key(match.group("key"), "key"),
                        line_number(text, start + match.start()),
                        f"keydown-{handler_index}-case",
                    )
                )

    for match in DATA_SHORTCUT_RE.finditer(text):
        result.append(
            LiteralOccurrence(
                normalize_key(match.group("key")),
                line_number(text, match.start()),
                "data-shortcut",
            )
        )
    return result


def _scan_quoted_literal(text: str, start: int) -> tuple[str, int] | None:
    quote = text[start]
    if quote not in "'\"`":
        return None
    value: list[str] = []
    escaped = False
    i = start + 1
    while i < len(text):
        ch = text[i]
        if escaped:
            value.append(ch)
            escaped = False
        elif ch == "\\":
            value.append(ch)
            escaped = True
        elif ch == quote:
            return "".join(value), i + 1
        else:
            value.append(ch)
        i += 1
    return None


def extract_static_selectors(text: str) -> list[LiteralOccurrence]:
    result: list[LiteralOccurrence] = []
    for call in SELECTOR_CALL_RE.finditer(text):
        i = call.end()
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] not in "'\"`":
            continue
        parsed = _scan_quoted_literal(text, i)
        if not parsed:
            continue
        selector, end = parsed
        if "${" in selector:
            continue
        j = end
        while j < len(text) and text[j].isspace():
            j += 1
        if j >= len(text) or text[j] not in "),":
            continue
        result.append(
            LiteralOccurrence(
                selector,
                line_number(text, call.start()),
                "selector",
            )
        )
    return result


def selector_error(selector: str) -> str | None:
    value = selector.strip()
    if not value:
        return "selector is empty"
    if value.endswith((">", "+", "~", ",")):
        return "selector ends with a combinator or comma"
    if re.search(r"(^|,)\s*,", value):
        return "selector contains an empty comma-separated group"
    if re.search(r"(?:^|[\s>+~,])(?:#|\.)($|[\s>+~,])", value):
        return "selector contains a bare ID or class marker"

    stack: list[str] = []
    quote: str | None = None
    escaped = False
    pairs = {")": "(", "]": "["}
    for ch in value:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
            continue
        if ch in "([":
            stack.append(ch)
        elif ch in ")]":
            if not stack or stack[-1] != pairs[ch]:
                return f"selector has unmatched {ch}"
            stack.pop()
    if quote:
        return "selector has an unterminated quote"
    if stack:
        return f"selector has unmatched {stack[-1]}"
    return None


def duplicate_map(
    items: Iterable[LiteralOccurrence],
) -> dict[str, list[LiteralOccurrence]]:
    grouped: dict[str, list[LiteralOccurrence]] = defaultdict(list)
    for item in items:
        grouped[item.value].append(item)
    return {
        key: values
        for key, values in grouped.items()
        if len(values) > 1
    }


def compare_duplicate_sets(
    candidate: dict[str, list[LiteralOccurrence]],
    base: dict[str, list[LiteralOccurrence]],
    code_prefix: str,
    allowed: set[str],
) -> list[Finding]:
    findings: list[Finding] = []
    for value, occurrences in sorted(candidate.items()):
        if value.casefold() in {entry.casefold() for entry in allowed}:
            continue
        base_count = len(base.get(value, []))
        candidate_count = len(occurrences)
        if base_count == 0:
            lines = ", ".join(str(item.line) for item in occurrences[:8])
            findings.append(
                Finding(
                    "failure",
                    f"new-{code_prefix}",
                    f"New duplicate {code_prefix.replace('-', ' ')} {value!r} "
                    f"appears {candidate_count} times (lines {lines}).",
                    value,
                )
            )
        elif candidate_count > base_count:
            findings.append(
                Finding(
                    "failure",
                    f"increased-{code_prefix}",
                    f"Duplicate {code_prefix.replace('-', ' ')} {value!r} "
                    f"increased from {base_count} to {candidate_count} occurrences.",
                    value,
                )
            )
    return findings


def tracked_files(root: Path, policy: dict) -> Iterator[Path]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "-z"],
            cwd=root,
            stderr=subprocess.DEVNULL,
        )
        names = [
            entry.decode("utf-8")
            for entry in output.split(b"\0")
            if entry
        ]
    except Exception:
        names = [
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        ]

    repo_policy = policy.get("repository", {})
    extensions = {
        entry.casefold()
        for entry in repo_policy.get("textExtensions", [])
    }
    excluded = tuple(repo_policy.get("excludedPrefixes", []))
    file_names = set(repo_policy.get("textFileNames", []))
    max_bytes = int(repo_policy.get("maxTextFileBytes", 5_000_000))

    for name in names:
        if excluded and any(
            name == prefix
            or name.startswith(prefix.rstrip("/") + "/")
            for prefix in excluded
        ):
            continue
        path = root / name
        if not path.is_file() or path.stat().st_size > max_bytes:
            continue
        if (
            extensions
            and path.suffix.casefold() not in extensions
            and path.name not in file_names
        ):
            continue
        yield path


def scan_repository(
    root: Path,
    policy: dict,
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    scanned_files = 0
    scanned_bytes = 0
    secret_excluded = set(
        policy.get("secrets", {}).get("excludedPaths", [])
    )

    for path in tracked_files(root, policy):
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned_files += 1
        scanned_bytes += len(raw)

        if LEFT_CONFLICT_RE.search(text) or RIGHT_CONFLICT_RE.search(text):
            findings.append(
                Finding(
                    "failure",
                    "merge-conflict-marker",
                    "Unresolved merge-conflict marker found.",
                    relative,
                    relative,
                )
            )

        if relative not in secret_excluded:
            for code, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    findings.append(
                        Finding(
                            "failure",
                            "exposed-secret",
                            f"High-confidence {code} value is committed in repository text.",
                            code,
                            relative,
                            line_number(text, match.start()),
                        )
                    )

    return findings, {
        "files": scanned_files,
        "bytes": scanned_bytes,
    }


def scan_asset_references(
    text: str,
    root: Path,
    policy: dict,
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    urls = sorted(set(URL_RE.findall(text)))
    config = policy.get("assets", {})
    allowed_http = set(
        config.get("allowedHttpHosts", ["localhost", "127.0.0.1"])
    )
    same_repo = str(
        config.get(
            "sameRepository",
            "Conroy1988/missionchief-toolkit-assets",
        )
    )
    missing_same_repo = 0
    insecure = 0
    blob_runtime = 0

    for url in urls:
        parsed = urlparse(url)
        host = (parsed.hostname or "").casefold()
        if parsed.scheme == "http" and host not in allowed_http:
            insecure += 1
            findings.append(
                Finding(
                    "failure",
                    "insecure-runtime-url",
                    "Runtime URL uses insecure HTTP.",
                    url,
                )
            )

        if (
            host == "github.com"
            and "/blob/" in parsed.path
            and re.search(
                r"\.(?:png|jpe?g|gif|webp|svg|mp3|wav|ogg)(?:$|[?#])",
                url,
                re.I,
            )
        ):
            blob_runtime += 1
            findings.append(
                Finding(
                    "failure",
                    "github-blob-asset-url",
                    "Runtime media uses a GitHub blob page instead of a raw or release URL.",
                    url,
                )
            )

        if host == "raw.githubusercontent.com":
            parts = [
                unquote(part)
                for part in parsed.path.strip("/").split("/")
            ]
            if len(parts) >= 4:
                repo = f"{parts[0]}/{parts[1]}"
                ref = parts[2]
                relative = "/".join(parts[3:])
                if repo.casefold() == same_repo.casefold() and ref == "main":
                    local = root / relative
                    if not local.is_file():
                        missing_same_repo += 1
                        findings.append(
                            Finding(
                                "failure",
                                "missing-raw-asset",
                                "Same-repository raw URL does not resolve to a committed file.",
                                url,
                                relative,
                            )
                        )

    return findings, {
        "urls": len(urls),
        "insecureUrls": insecure,
        "blobAssetUrls": blob_runtime,
        "missingSameRepositoryAssets": missing_same_repo,
    }


def analyse_source(path: Path, policy: dict) -> dict:
    text = read_text(path)
    meta, metadata_findings = validate_metadata(text, policy)
    ids = extract_static_ids(text)
    shortcuts = extract_shortcuts(text)
    selectors = extract_static_selectors(text)
    selector_findings: list[Finding] = []

    for occurrence in selectors:
        error = selector_error(occurrence.value)
        if error:
            selector_findings.append(
                Finding(
                    "failure",
                    "malformed-static-selector",
                    f"Malformed static selector: {error}.",
                    occurrence.value,
                    str(path),
                    occurrence.line,
                )
            )

    return {
        "text": text,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "metadata": meta,
        "metadataFindings": metadata_findings,
        "ids": ids,
        "duplicateIds": duplicate_map(ids),
        "shortcuts": shortcuts,
        "shortcutConflicts": duplicate_map(shortcuts),
        "selectors": selectors,
        "selectorFindings": selector_findings,
    }


def finding_key(finding: Finding) -> tuple:
    return (
        finding.severity,
        finding.code,
        finding.path,
        finding.line or 0,
        finding.subject,
        finding.message,
    )


def build_report(
    candidate_path: Path,
    base_path: Path | None,
    policy: dict,
    root: Path,
) -> tuple[dict, int]:
    candidate = analyse_source(candidate_path, policy)
    base = (
        analyse_source(base_path, policy)
        if base_path and base_path.exists()
        else None
    )

    findings: list[Finding] = []
    findings.extend(candidate["metadataFindings"])
    findings.extend(candidate["selectorFindings"])

    duplicate_policy = policy.get("duplicateIds", {})
    shortcut_policy = policy.get("shortcuts", {})
    if base:
        findings.extend(
            compare_duplicate_sets(
                candidate["duplicateIds"],
                base["duplicateIds"],
                "interface-id",
                set(duplicate_policy.get("allow", [])),
            )
        )
        findings.extend(
            compare_duplicate_sets(
                candidate["shortcutConflicts"],
                base["shortcutConflicts"],
                "shortcut-conflict",
                set(shortcut_policy.get("allow", [])),
            )
        )
    else:
        if duplicate_policy.get("failWithoutBaseline", False):
            findings.extend(
                compare_duplicate_sets(
                    candidate["duplicateIds"],
                    {},
                    "interface-id",
                    set(duplicate_policy.get("allow", [])),
                )
            )
        if shortcut_policy.get("failWithoutBaseline", False):
            findings.extend(
                compare_duplicate_sets(
                    candidate["shortcutConflicts"],
                    {},
                    "shortcut-conflict",
                    set(shortcut_policy.get("allow", [])),
                )
            )

    repository_findings, repository_metrics = scan_repository(root, policy)
    findings.extend(repository_findings)
    asset_findings, asset_metrics = scan_asset_references(
        candidate["text"],
        root,
        policy,
    )
    findings.extend(asset_findings)

    unique_findings = sorted(
        {finding_key(item): item for item in findings}.values(),
        key=finding_key,
    )
    failures = [
        item for item in unique_findings if item.severity == "failure"
    ]
    warnings = [
        item for item in unique_findings if item.severity == "warning"
    ]

    try:
        candidate_display = str(candidate_path.relative_to(root))
    except ValueError:
        candidate_display = str(candidate_path)

    report = {
        "schemaVersion": 1,
        "candidate": {
            "path": candidate_display,
            "sha256": candidate["sha256"],
        },
        "base": {
            "path": str(base_path) if base_path else None,
            "sha256": base["sha256"] if base else None,
            "available": bool(base),
        },
        "metrics": {
            "metadataKeys": len(candidate["metadata"]),
            "staticIds": len(candidate["ids"]),
            "duplicateIdValues": len(candidate["duplicateIds"]),
            "shortcutBindings": len(candidate["shortcuts"]),
            "shortcutConflictValues": len(candidate["shortcutConflicts"]),
            "staticSelectors": len(candidate["selectors"]),
            "repositoryTextFiles": repository_metrics["files"],
            "repositoryTextBytes": repository_metrics["bytes"],
            **asset_metrics,
        },
        "duplicateIds": {
            key: [asdict(item) for item in values]
            for key, values in sorted(candidate["duplicateIds"].items())
        },
        "shortcutConflicts": {
            key: [asdict(item) for item in values]
            for key, values in sorted(candidate["shortcutConflicts"].items())
        },
        "findings": [asdict(item) for item in unique_findings],
        "summary": {
            "failures": len(failures),
            "warnings": len(warnings),
            "result": "failed" if failures else "passed",
        },
    }
    return report, 1 if failures else 0


def markdown(report: dict) -> str:
    metrics = report["metrics"]
    summary = report["summary"]
    lines = [
        "# Toolkit code-integrity audit",
        "",
        f"- Result: **{summary['result'].upper()}**",
        f"- Failures: **{summary['failures']}**",
        f"- Warnings: **{summary['warnings']}**",
        f"- Baseline available: **{'yes' if report['base']['available'] else 'no'}**",
        "",
        "## Inventory",
        "",
        f"- Static interface ID assignments: **{metrics['staticIds']}**",
        f"- Duplicate interface ID values: **{metrics['duplicateIdValues']}**",
        f"- Detected shortcut bindings: **{metrics['shortcutBindings']}**",
        f"- Shortcut conflict values: **{metrics['shortcutConflictValues']}**",
        f"- Fully static selectors validated: **{metrics['staticSelectors']}**",
        f"- Runtime URLs inspected: **{metrics['urls']}**",
        f"- Repository text files scanned: **{metrics['repositoryTextFiles']}**",
        "",
    ]

    if report["findings"]:
        lines.extend(["## Findings", ""])
        for item in report["findings"]:
            location = ""
            if item.get("path"):
                location = f" — `{item['path']}"
                if item.get("line"):
                    location += f":{item['line']}"
                location += "`"
            subject = (
                f" (`{item['subject']}`)"
                if item.get("subject")
                else ""
            )
            icon = "❌" if item["severity"] == "failure" else "⚠️"
            lines.append(
                f"- {icon} **{item['code']}**{subject}: "
                f"{item['message']}{location}"
            )
    else:
        lines.extend(
            [
                "## Findings",
                "",
                "No integrity failures or warnings were detected.",
            ]
        )

    if report["duplicateIds"]:
        lines.extend(
            [
                "",
                "## Existing duplicate interface-ID inventory",
                "",
            ]
        )
        for value, occurrences in list(report["duplicateIds"].items())[:80]:
            locations = ", ".join(
                str(item["line"])
                for item in occurrences[:10]
            )
            lines.append(
                f"- `{value}`: {len(occurrences)} occurrences "
                f"(lines {locations})"
            )

    if report["shortcutConflicts"]:
        lines.extend(
            [
                "",
                "## Existing shortcut-conflict inventory",
                "",
            ]
        )
        for value, occurrences in list(report["shortcutConflicts"].items())[:80]:
            locations = ", ".join(
                str(item["line"])
                for item in occurrences[:10]
            )
            lines.append(
                f"- `{value}`: {len(occurrences)} occurrences "
                f"(lines {locations})"
            )

    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--base", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("code-integrity-report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("code-integrity-report.md"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    report, status = build_report(
        args.candidate.resolve(),
        args.base.resolve() if args.base else None,
        policy,
        root,
    )
    args.json_output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(
        markdown(report),
        encoding="utf-8",
    )
    print(json.dumps(report["summary"], indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
