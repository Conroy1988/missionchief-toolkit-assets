#!/usr/bin/env python3
"""Validate canonical payout audio and declared public compatibility aliases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg"}
EXCLUDED_DIRECTORIES = {".git", "node_modules", "release-bundle", "__pycache__"}
RAW_URL_RE = re.compile(r"https://raw\.githubusercontent\.com/(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)/(?P<ref>[^/\s]+)/(?P<path>[^'\"\s)<>]+)")


def failure(code: str, message: str, subject: str = "") -> dict[str, str]:
    return {"code": code, "message": message, "subject": subject}


def safe_relative_path(value: object) -> str:
    if not isinstance(value, str) or not value or value.startswith(("/", "\\")):
        raise ValueError(f"Invalid repository-relative path: {value!r}")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe repository-relative path: {value!r}")
    return path.as_posix()


def load_contract(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("schemaVersion") != 1:
        raise ValueError("Audio alias contract must be a schemaVersion 1 object")
    return document


def discover_audio(root: Path) -> set[str]:
    result: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRECTORIES for part in rel.parts):
            continue
        if len(rel.parts) >= 2 and rel.parts[:2] == (".github", "development-packages"):
            continue
        if path.suffix.lower() in AUDIO_EXTENSIONS:
            result.add(rel.as_posix())
    return result


def source_audio_paths(source: str, repository: str, stable_ref: str) -> set[str]:
    expected_owner, expected_repo = repository.split("/", 1)
    result: set[str] = set()
    for match in RAW_URL_RE.finditer(source):
        if match.group("owner").casefold() != expected_owner.casefold():
            continue
        if match.group("repo").casefold() != expected_repo.casefold():
            continue
        if match.group("ref") != stable_ref:
            continue
        path = match.group("path").rstrip(".,;:")
        if Path(path).suffix.lower() in AUDIO_EXTENSIONS:
            result.add(path)
    return result


def validate_repository(
    root: Path,
    contract_path: Path,
    repository: str = "Conroy1988/missionchief-toolkit-assets",
) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    try:
        contract = load_contract(contract_path)
    except Exception as exc:
        return {
            "schemaVersion": 1,
            "failures": [failure("contract-load-error", f"{type(exc).__name__}: {exc}", str(contract_path))],
            "summary": {"failures": 1},
        }

    try:
        canonical_source = safe_relative_path(contract.get("canonicalSource"))
        stable_ref = str(contract.get("stableRef") or "main")
        canonical_paths = {
            safe_relative_path(value) for value in contract.get("canonicalAudioPaths", [])
        }
        alias_entries = contract.get("aliases", [])
        if not isinstance(alias_entries, list):
            raise ValueError("aliases must be an array")
        aliases: dict[str, str] = {}
        for entry in alias_entries:
            if not isinstance(entry, dict):
                raise ValueError("Each alias entry must be an object")
            legacy = safe_relative_path(entry.get("legacyPath"))
            canonical = safe_relative_path(entry.get("canonicalPath"))
            if legacy in aliases:
                raise ValueError(f"Duplicate legacy alias entry: {legacy}")
            aliases[legacy] = canonical
    except Exception as exc:
        return {
            "schemaVersion": 1,
            "failures": [failure("contract-schema-error", f"{type(exc).__name__}: {exc}", str(contract_path))],
            "summary": {"failures": 1},
        }

    if not canonical_paths:
        failures.append(failure("canonical-audio-empty", "No canonical audio paths are declared", str(contract_path)))

    undeclared_targets = sorted(set(aliases.values()) - canonical_paths)
    if undeclared_targets:
        failures.append(
            failure(
                "alias-target-not-canonical",
                f"Alias targets are not declared canonical audio: {undeclared_targets}",
                str(contract_path),
            )
        )

    overlap = sorted(set(aliases) & canonical_paths)
    if overlap:
        failures.append(
            failure(
                "alias-canonical-overlap",
                f"Paths cannot be both canonical and legacy aliases: {overlap}",
                str(contract_path),
            )
        )

    actual_audio = discover_audio(root)
    declared_audio = canonical_paths | set(aliases)
    for path in sorted(canonical_paths - actual_audio):
        failures.append(failure("missing-canonical-audio", "Canonical audio file is missing", path))
    for path in sorted(set(aliases) - actual_audio):
        failures.append(failure("missing-legacy-alias", "Legacy compatibility alias is missing", path))
    for path in sorted(actual_audio - declared_audio):
        failures.append(failure("undeclared-audio-path", "Repository audio is not declared by the contract", path))

    source_path = root / canonical_source
    if not source_path.is_file():
        failures.append(failure("missing-canonical-source", "Canonical userscript is missing", canonical_source))
        referenced: set[str] = set()
    else:
        referenced = source_audio_paths(source_path.read_text(encoding="utf-8", errors="replace"), repository, stable_ref)

    for path in sorted(canonical_paths - referenced):
        failures.append(failure("canonical-source-reference", "Canonical userscript does not reference canonical audio", path))
    for path in sorted(set(aliases) & referenced):
        failures.append(failure("legacy-source-reference", "Canonical userscript still references a legacy root alias", path))
    for path in sorted(referenced - canonical_paths):
        failures.append(failure("unexpected-source-audio", "Canonical userscript references audio outside the canonical contract", path))

    allowed_duplicate_groups = {
        frozenset((legacy, canonical)) for legacy, canonical in aliases.items()
    }
    hashes: dict[str, set[str]] = {}
    for path in sorted(actual_audio):
        digest = hashlib.sha256((root / path).read_bytes()).hexdigest()
        hashes.setdefault(digest, set()).add(path)

    for legacy, canonical in sorted(aliases.items()):
        legacy_path = root / legacy
        canonical_path = root / canonical
        if not legacy_path.is_file() or not canonical_path.is_file():
            continue
        if legacy_path.read_bytes() != canonical_path.read_bytes():
            failures.append(
                failure(
                    "alias-hash-mismatch",
                    "Legacy alias is not byte-identical to its canonical target",
                    f"{legacy} -> {canonical}",
                )
            )

    for paths in sorted((group for group in hashes.values() if len(group) > 1), key=lambda value: sorted(value)):
        frozen = frozenset(paths)
        if frozen not in allowed_duplicate_groups:
            failures.append(
                failure(
                    "undeclared-duplicate-audio",
                    f"Duplicate audio payload is not one declared alias pair: {sorted(paths)}",
                    ", ".join(sorted(paths)),
                )
            )

    report = {
        "schemaVersion": 1,
        "repository": repository,
        "contract": contract_path.relative_to(root).as_posix() if contract_path.is_relative_to(root) else str(contract_path),
        "canonicalSource": canonical_source,
        "canonicalAudioPaths": sorted(canonical_paths),
        "legacyAliases": dict(sorted(aliases.items())),
        "referencedAudioPaths": sorted(referenced),
        "repositoryAudioPaths": sorted(actual_audio),
        "failures": failures,
        "summary": {
            "canonicalAudio": len(canonical_paths),
            "legacyAliases": len(aliases),
            "repositoryAudio": len(actual_audio),
            "failures": len(failures),
        },
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Audio compatibility alias report",
        "",
        f"- Canonical audio: **{summary.get('canonicalAudio', 0)}**",
        f"- Legacy aliases: **{summary.get('legacyAliases', 0)}**",
        f"- Repository audio: **{summary.get('repositoryAudio', 0)}**",
        f"- Failures: **{summary.get('failures', 0)}**",
        "",
    ]
    for item in report.get("failures", []):
        lines.append(f"- **{item['code']}** — {item['message']} `{item.get('subject', '')}`")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--contract", default=".github/asset-compatibility-aliases.json")
    parser.add_argument("--repository", default="Conroy1988/missionchief-toolkit-assets")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    contract = root / args.contract
    report = validate_repository(root, contract, args.repository)
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        Path(args.markdown_output).write_text(render_markdown(report), encoding="utf-8")
    print(
        "Audio alias contract: "
        f"{report['summary'].get('canonicalAudio', 0)} canonical, "
        f"{report['summary'].get('legacyAliases', 0)} aliases, "
        f"{report['summary'].get('failures', 0)} failures"
    )
    for item in report.get("failures", []):
        print(f"FAIL {item['code']}: {item['message']} {item.get('subject', '')}".rstrip())
    return 1 if report["summary"].get("failures") else 0


if __name__ == "__main__":
    raise SystemExit(main())
