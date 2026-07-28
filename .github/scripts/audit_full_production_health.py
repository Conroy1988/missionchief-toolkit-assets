#!/usr/bin/env python3
"""Full production-health inventory for MissionChief Map Command Toolkit.

This audit is deliberately read-only. It verifies production parity, inventories
recurring work and lifecycle-owned resources, and writes machine-readable and
human-readable evidence outside the repository working tree.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_JS = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
DASHBOARD = ROOT / "status" / "release-dashboard.json"
UPDATE_MANIFEST = ROOT / "status" / "update-manifest.json"
RELEASE_MANIFEST = ROOT / "dist" / "release-manifest.json"
PERFORMANCE_BUDGET = ROOT / ".github" / "performance-budget.json"
OUT = Path(os.environ.get("MCMS_AUDIT_OUTPUT", ROOT / "audit-output"))
OUT.mkdir(parents=True, exist_ok=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def git_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, text=True, capture_output=True
    )
    return [line for line in result.stdout.splitlines() if line]


def literal_delays(source: str, function_name: str) -> list[dict[str, int]]:
    pattern = re.compile(
        rf"{re.escape(function_name)}\s*\([\s\S]{{0,700}}?,\s*(\d{{1,8}})\s*\)",
        re.MULTILINE,
    )
    values: list[dict[str, int]] = []
    for match in pattern.finditer(source):
        values.append({"delayMs": int(match.group(1)), "line": line_number(source, match.start())})
    return values


def assigned_resources(source: str, constructor: str) -> list[dict[str, object]]:
    pattern = re.compile(
        rf"(?m)^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*new\s+{re.escape(constructor)}\s*\("
    )
    result = []
    for match in pattern.finditer(source):
        name = match.group(1)
        result.append(
            {
                "name": name,
                "line": line_number(source, match.start()),
                "disconnectPresent": bool(re.search(rf"\b{re.escape(name)}\s*\.\s*disconnect\s*\(", source)),
            }
        )
    return result


def top_level_functions(source: str) -> dict[str, list[int]]:
    found: dict[str, list[int]] = defaultdict(list)
    pattern = re.compile(r"(?m)^    (?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")
    for match in pattern.finditer(source):
        found[match.group(1)].append(line_number(source, match.start()))
    return dict(found)


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode("utf-8")
    dist_js = DIST_JS.read_bytes()
    dist_txt = DIST_TXT.read_bytes()
    dashboard = load_json(DASHBOARD)
    update_manifest = load_json(UPDATE_MANIFEST)
    release_manifest = load_json(RELEASE_MANIFEST)
    performance_budget = load_json(PERFORMANCE_BUDGET)

    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"\bversion:\s*'([^']+)'", source)
    version = metadata.group(1) if metadata else ""
    runtime_version = runtime.group(1) if runtime else ""
    source_sha = sha256_bytes(source_bytes)

    inventory_patterns = {
        "rawSetIntervalCalls": r"(?<![\w$])setInterval\s*\(",
        "rawSetTimeoutCalls": r"(?<![\w$])setTimeout\s*\(",
        "rawAnimationFrameCalls": r"(?<![\w$])requestAnimationFrame\s*\(",
        "eventListenerAdds": r"\.addEventListener\s*\(",
        "eventListenerRemoves": r"\.removeEventListener\s*\(",
        "mutationObserverConstructions": r"new\s+(?:MutationObserver|Observer)\s*\(",
        "resizeObserverConstructions": r"new\s+ResizeObserver\s*\(",
        "managedIntervals": r"\bruntimeSetInterval\s*\(",
        "managedTimeouts": r"\bruntimeSetTimeout\s*\(",
        "managedAnimationFrames": r"\bruntimeRequestAnimationFrame\s*\(",
        "managedListeners": r"\bruntimeAddEventListener\s*\(",
        "managedObserverTracks": r"\bruntimeTrackObserver\s*\(",
        "networkRequestSites": r"\b(?:GM_xmlhttpRequest|fetch)\s*\(",
        "objectUrlCreates": r"\bURL\.createObjectURL\s*\(",
        "objectUrlRevokes": r"\bURL\.revokeObjectURL\s*\(",
        "audioConstructions": r"\bnew\s+Audio\s*\(",
        "abortControllerConstructions": r"\bnew\s+AbortController\s*\(",
    }
    inventory = {
        key: len(re.findall(pattern, source)) for key, pattern in inventory_patterns.items()
    }
    inventory.update(
        {
            "sourceBytes": len(source_bytes),
            "sourceLines": len(source.splitlines()),
            "cssTemplateBytes": len(
                re.search(r"style\.textContent\s*=\s*`([\s\S]*?)`;", source).group(1).encode("utf-8")
            )
            if re.search(r"style\.textContent\s*=\s*`([\s\S]*?)`;", source)
            else 0,
        }
    )

    mutation_resources = assigned_resources(source, "MutationObserver")
    resize_resources = assigned_resources(source, "ResizeObserver")
    duplicate_functions = {
        name: lines for name, lines in top_level_functions(source).items() if len(lines) > 1
    }

    interval_delays = literal_delays(source, "runtimeSetInterval") + literal_delays(source, "setInterval")
    timeout_delays = literal_delays(source, "runtimeSetTimeout") + literal_delays(source, "setTimeout")

    tracked = git_files()
    prohibited_tracked = [
        path
        for path in tracked
        if path.startswith("node_modules/")
        or "/node_modules/" in path
        or path.endswith(".pyc")
        or "__pycache__" in path
        or path.startswith("audit-output/")
    ]
    temporary_tracked = [
        path
        for path in tracked
        if path.startswith(".github/development-packages/")
        or path.startswith(".github/workflows/temporary-")
    ]
    expected_audit_files = {
        ".github/scripts/audit_full_production_health.py",
        ".github/scripts/audit_runtime_stress.mjs",
        ".github/workflows/temporary-full-production-health-audit.yml",
    }
    unexpected_temporary = [path for path in temporary_tracked if path not in expected_audit_files]

    errors: list[str] = []
    warnings: list[str] = []

    if not metadata or not runtime or version != runtime_version:
        errors.append("Userscript metadata and runtime versions do not match.")
    if source_bytes != dist_js or source_bytes != dist_txt:
        errors.append("Canonical source and distribution mirrors are not byte-identical.")
    if dashboard.get("currentVersion") != version:
        errors.append("Release dashboard version does not match the userscript.")
    if update_manifest.get("version") != version:
        errors.append("Stable update manifest version does not match the userscript.")
    if dashboard.get("source", {}).get("validatedSha256") != source_sha:
        errors.append("Release dashboard SHA-256 does not match canonical source.")
    if update_manifest.get("sha256") != source_sha:
        errors.append("Stable update manifest SHA-256 does not match canonical source.")
    release_version = str(release_manifest.get("version") or release_manifest.get("scriptVersion") or "")
    if release_version and release_version != version:
        errors.append("Distribution release manifest version does not match canonical source.")
    if prohibited_tracked:
        errors.append(f"Prohibited generated/dependency files are tracked: {prohibited_tracked}")
    if unexpected_temporary:
        errors.append(f"Unexpected temporary development payloads are tracked: {unexpected_temporary}")

    unpaired_observers = [
        item for item in mutation_resources + resize_resources if not item["disconnectPresent"]
    ]
    if unpaired_observers:
        errors.append(f"Named observers without a visible disconnect path: {unpaired_observers}")

    sub_100_intervals = [item for item in interval_delays if item["delayMs"] < 100]
    if sub_100_intervals:
        errors.append(f"Recurring intervals below 100 ms detected: {sub_100_intervals}")
    sub_250_intervals = [item for item in interval_delays if 100 <= item["delayMs"] < 250]
    if sub_250_intervals:
        warnings.append(f"Recurring intervals below 250 ms require review: {sub_250_intervals}")

    if inventory["objectUrlCreates"] > inventory["objectUrlRevokes"]:
        warnings.append("Object URL creation exceeds explicit revocation call sites.")
    if inventory["eventListenerAdds"] > inventory["eventListenerRemoves"] + inventory["managedListeners"] + 20:
        warnings.append("Raw event-listener additions materially exceed visible removals and managed ownership.")
    if duplicate_functions:
        warnings.append(f"Repeated top-level function declarations require review: {duplicate_functions}")

    absolute = performance_budget.get("absoluteLimits", {})
    source_byte_limit = int(absolute.get("bytes", 0) or 0)
    source_line_limit = int(absolute.get("lines", 0) or 0)
    if source_byte_limit:
        inventory["sourceByteHeadroom"] = source_byte_limit - inventory["sourceBytes"]
        if inventory["sourceBytes"] > source_byte_limit:
            errors.append("Canonical source exceeds the absolute performance byte limit.")
        elif inventory["sourceBytes"] > source_byte_limit * 0.95:
            warnings.append("Canonical source uses more than 95% of its absolute byte limit.")
    if source_line_limit:
        inventory["sourceLineHeadroom"] = source_line_limit - inventory["sourceLines"]
        if inventory["sourceLines"] > source_line_limit:
            errors.append("Canonical source exceeds the absolute performance line limit.")

    report = {
        "schemaVersion": 1,
        "audit": "full-production-health",
        "version": version,
        "sourceSha256": source_sha,
        "status": "failed" if errors else "passed-with-warnings" if warnings else "passed",
        "inventory": inventory,
        "literalIntervalDelays": interval_delays,
        "literalTimeoutDelays": timeout_delays,
        "namedMutationObservers": mutation_resources,
        "namedResizeObservers": resize_resources,
        "duplicateTopLevelFunctions": duplicate_functions,
        "trackedTemporaryFiles": temporary_tracked,
        "errors": errors,
        "warnings": warnings,
    }
    (OUT / "full-production-health.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        f"# Toolkit {version} full production-health audit",
        "",
        f"- **Status:** `{report['status']}`",
        f"- **Source SHA-256:** `{source_sha}`",
        f"- **Source:** {inventory['sourceBytes']:,} bytes · {inventory['sourceLines']:,} lines",
        f"- **Managed recurring intervals:** {inventory['managedIntervals']}",
        f"- **Managed timeouts:** {inventory['managedTimeouts']}",
        f"- **Mutation observers:** {inventory['mutationObserverConstructions']}",
        f"- **Resize observers:** {inventory['resizeObserverConstructions']}",
        f"- **Listener additions/removals:** {inventory['eventListenerAdds']} / {inventory['eventListenerRemoves']}",
        f"- **Network request sites:** {inventory['networkRequestSites']}",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {item}" for item in errors] or ["- None."])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- None."])
    lines.extend(["", "## Resource inventory", "", "```json", json.dumps(inventory, indent=2, sort_keys=True), "```", ""])
    (OUT / "full-production-health.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
