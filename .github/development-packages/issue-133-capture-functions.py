#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs" / "issue-133-function-inspection.md"

source = SOURCE.read_text(encoding="utf-8")

names = [
    "normaliseMissingRequirementText",
    "resourceRequirementsFromSnapshot",
    "buildResourceGapVehicleContext",
    "getPersonalVehicleRecords",
    "normaliseVehicleApiPayload",
    "transportSweepDocumentContexts",
    "transportSweepVisibleWindowRoots",
    "missionValueWindowCandidates",
    "scanMissionValueWindows",
    "observeMissionValueDocument",
    "installMissionValueWindows",
    "toggleFeature",
    "handleAction",
    "updateUI",
    "saveState",
    "loadState",
    "applyRootAttributes",
    "connectMainMutationObserver",
    "scheduleDeferredOperationalStartup",
    "startBootAttemptCoordinator",
    "boot"
]


def extract_function(name: str) -> tuple[int, str] | None:
    candidates = [f"function {name}(", f"async function {name}("]
    starts = [source.find(candidate) for candidate in candidates]
    starts = [start for start in starts if start >= 0]
    if not starts:
        return None
    start = min(starts)
    brace = source.find("{", start)
    if brace < 0:
        return None

    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    index = brace
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""

        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char in ("'", '"', "`"):
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                line = source.count("\n", 0, start) + 1
                return line, source[start:end]
        index += 1
    return None

report = [
    "# Issue #133 — Canonical function inspection",
    "",
    "Generated mechanically from the canonical userscript. Inspection only.",
    ""
]

for name in names:
    report.extend([f"## `{name}`", ""])
    extracted = extract_function(name)
    if not extracted:
        report.extend(["Not found.", ""])
        continue
    line, block = extracted
    report.extend([f"Starts at canonical line {line}.", "", "```javascript", block, "```", ""])

REPORT.write_text("\n".join(report), encoding="utf-8")
print(f"Wrote {REPORT.relative_to(ROOT)}")
