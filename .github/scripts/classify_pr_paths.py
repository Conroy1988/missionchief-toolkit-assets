#!/usr/bin/env python3
"""Classify changed repository paths into fail-closed Toolkit validation lanes."""
from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / ".github/path-aware-validation.json"
BOOL_KEYS = (
    "runtime",
    "integrity",
    "performance",
    "repository",
    "workflowChecks",
    "documentationChecks",
    "assetChecks",
    "releaseChecks",
    "releaseCandidate",
    "exhaustiveIntegrity",
    "exhaustivePerformance",
    "externalParity",
)


def matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def normalize_path(raw: str) -> str:
    path = raw.strip().replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path.lstrip("/")


def classify(paths: Iterable[str], policy: dict, *, full: bool = False) -> dict:
    normalized = sorted(
        {
            path
            for raw in paths
            if (path := normalize_path(raw))
        }
    )
    groups = policy["groups"]
    result = {key: bool(full) for key in BOOL_KEYS}
    result["repository"] = True
    result["mode"] = "full" if full else "paths"
    result["paths"] = normalized
    result["unknownPaths"] = []
    result["matchedGroups"] = {name: [] for name in groups}

    if full:
        result["externalParity"] = True
        return result

    if not normalized:
        for key in BOOL_KEYS:
            result[key] = True
        result["unknownPaths"] = ["<empty-diff>"]
        return result

    known_patterns = [pattern for patterns in groups.values() for pattern in patterns]
    for path in normalized:
        matched_names = [
            name
            for name, patterns in groups.items()
            if matches(path, patterns)
        ]
        for name in matched_names:
            result["matchedGroups"][name].append(path)
        if not matches(path, known_patterns):
            result["unknownPaths"].append(path)

    product = bool(result["matchedGroups"]["product"])
    critical = bool(result["matchedGroups"]["criticalInfrastructure"])
    unknown = bool(result["unknownPaths"])
    workflow = bool(result["matchedGroups"]["workflowPolicy"])

    result["runtime"] = (
        product
        or critical
        or unknown
        or bool(result["matchedGroups"]["runtime"])
    )
    result["integrity"] = (
        product
        or critical
        or unknown
        or bool(result["matchedGroups"]["integrity"])
        or bool(result["matchedGroups"]["integrityExhaustive"])
    )
    result["performance"] = (
        product
        or critical
        or unknown
        or bool(result["matchedGroups"]["performance"])
        or bool(result["matchedGroups"]["performanceExhaustive"])
    )
    result["workflowChecks"] = workflow or critical or unknown
    result["documentationChecks"] = (
        product
        or bool(result["matchedGroups"]["documentation"])
        or bool(result["matchedGroups"]["release"])
    )
    result["assetChecks"] = (
        product
        or bool(result["matchedGroups"]["assets"])
    )
    result["releaseChecks"] = (
        product
        or bool(result["matchedGroups"]["release"])
    )
    result["releaseCandidate"] = product or unknown
    result["exhaustiveIntegrity"] = (
        critical
        or unknown
        or bool(result["matchedGroups"]["integrityExhaustive"])
    )
    result["exhaustivePerformance"] = (
        critical
        or unknown
        or bool(result["matchedGroups"]["performanceExhaustive"])
    )
    result["externalParity"] = False
    return result


def write_github_output(path: Path, result: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key in BOOL_KEYS:
            handle.write(f"{key}={'true' if result[key] else 'false'}\n")
        handle.write(f"mode={result['mode']}\n")
        handle.write(f"unknown_count={len(result['unknownPaths'])}\n")


def write_markdown(path: Path, result: dict) -> None:
    lines = [
        "# Path-aware Toolkit validation",
        "",
        f"- Mode: `{result['mode']}`",
        f"- Changed paths: **{len(result['paths'])}**",
        "",
        "| Rule | Required |",
        "|---|---:|",
    ]
    for key in BOOL_KEYS:
        lines.append(f"| `{key}` | {'yes' if result[key] else 'no'} |")
    if result["unknownPaths"]:
        lines.extend(["", "## Fail-closed unknown paths", ""])
        lines.extend(f"- `{item}`" for item in result["unknownPaths"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def self_test(policy: dict) -> None:
    source = classify(
        ["src/MissionChief_Map_Command_Toolkit.user.js"],
        policy,
    )
    assert source["runtime"]
    assert source["integrity"]
    assert source["performance"]
    assert source["releaseCandidate"]
    assert source["documentationChecks"]
    assert source["assetChecks"]
    assert source["releaseChecks"]
    assert not source["exhaustiveIntegrity"]
    assert not source["exhaustivePerformance"]
    assert not source["externalParity"]

    docs = classify(["README.md", "docs/SITE.md"], policy)
    assert docs["repository"] and docs["documentationChecks"]
    assert not docs["runtime"]
    assert not docs["integrity"]
    assert not docs["performance"]
    assert not docs["releaseCandidate"]

    assets = classify(["themes/godfather/manifest.json"], policy)
    assert assets["repository"] and assets["assetChecks"]
    assert not assets["releaseCandidate"]
    assert not assets["runtime"]
    assert not assets["integrity"]
    assert not assets["performance"]

    runtime = classify(
        [".github/scripts/test_boot_lifecycle_contract.py"],
        policy,
    )
    assert runtime["runtime"] and runtime["repository"]
    assert not runtime["integrity"]
    assert not runtime["performance"]
    assert not runtime["releaseCandidate"]

    performance = classify(
        [".github/performance-budget.json"],
        policy,
    )
    assert performance["performance"]
    assert not performance["runtime"]
    assert not performance["integrity"]
    assert not performance["exhaustivePerformance"]
    assert not performance["releaseCandidate"]

    deep = classify(
        [".github/scripts/deep_performance_audit.mjs"],
        policy,
    )
    assert deep["performance"] and deep["exhaustivePerformance"]

    workflow = classify(
        [".github/workflows/github-pages.yml"],
        policy,
    )
    assert workflow["workflowChecks"] and workflow["repository"]
    assert not workflow["runtime"]
    assert not workflow["integrity"]
    assert not workflow["performance"]

    infrastructure = classify(
        [".github/workflows/validate-userscript.yml"],
        policy,
    )
    assert infrastructure["runtime"]
    assert infrastructure["integrity"]
    assert infrastructure["performance"]
    assert infrastructure["workflowChecks"]
    assert infrastructure["exhaustiveIntegrity"]
    assert infrastructure["exhaustivePerformance"]
    assert not infrastructure["releaseCandidate"]

    unknown = classify(["new-runtime-surface/file.bin"], policy)
    assert all(
        unknown[key]
        for key in (
            "runtime",
            "integrity",
            "performance",
            "repository",
            "workflowChecks",
            "releaseCandidate",
            "exhaustiveIntegrity",
            "exhaustivePerformance",
        )
    )
    assert unknown["unknownPaths"] == ["new-runtime-surface/file.bin"]

    manual = classify([], policy, full=True)
    assert all(manual[key] for key in BOOL_KEYS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--paths-from", type=Path)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--mode", choices=("paths", "full"), default="paths")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    if (
        policy.get("schemaVersion") != 1
        or not isinstance(policy.get("groups"), dict)
    ):
        raise SystemExit("Unsupported path-aware validation policy schema")

    if args.self_test:
        self_test(policy)
        print("Path-aware classification self-tests passed.")
        return 0

    paths = list(args.path)
    if args.paths_from:
        paths.extend(
            args.paths_from.read_text(encoding="utf-8").splitlines()
        )
    result = classify(paths, policy, full=args.mode == "full")
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        args.json_output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    if args.markdown_output:
        write_markdown(args.markdown_output, result)
    if args.github_output:
        write_github_output(args.github_output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
