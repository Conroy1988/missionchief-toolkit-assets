#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
GUIDE = ROOT / "docs" / "issue-716-procurement-timeline.md"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.16.5"

    for token in (
        "operationalTimelineState: 'mc_map_command_toolkit_operational_timeline_v1'",
        "const OPERATIONAL_TIMELINE_LIMIT = 1500",
        "const OPERATIONAL_TIMELINE_RETENTION_MS = 30 * 24 * 60 * 60 * 1000",
        "const OPERATIONAL_TIMELINE_RENDER_LIMIT = 120",
        "Object.freeze([1, 7, 30])",
        "'procurementBrain'",
        "'operationalTimeline'",
    ):
        assert token in source, f"Missing Procurement/Timeline contract: {token}"

    for name in (
        "normaliseOperationalTimelineEntry",
        "validateOperationalTimelineState",
        "loadOperationalTimelineState",
        "saveOperationalTimelineState",
        "recordOperationalTimelineEvent",
        "updateOperationalTimelineFromSnapshots",
        "calculateProcurementBrainModel",
        "renderProcurementBrainView",
        "renderOperationalTimelineView",
        "exportOperationalTimeline",
        "clearOperationalTimeline",
        "openOperationalIntelligenceView",
    ):
        assert source.count(f"function {name}(") == 1, name

    lifecycle = section(source, "    function refreshMissionSnapshots()", "    function scheduleMissionSnapshotRefresh(")
    assert "updateOperationalTimelineFromSnapshots(current, now)" in lifecycle

    timeline = section(source, "    function operationalTimelineText(", "    function calculateOperationalPressureModel(")
    for guard in (
        "if (!current.size) return 0",
        "operationalTimelineArmed = true",
        "now - absentSince < 1000",
        "Math.abs(item.timestamp - entry.timestamp) <= 30000",
        ".slice(0, OPERATIONAL_TIMELINE_LIMIT)",
        "raw.length > 2_000_000",
        "if (!operationalTimelineLoggingEnabled())",
        "operationalPressureMissionInScope(snapshot, includeAllianceMissions)",
        "resetOperationalTimelineMonitoring()",
    ):
        assert guard in timeline, f"Missing bounded Timeline guard: {guard}"
    assert "setInterval" not in timeline
    assert "MutationObserver" not in timeline
    assert "runtimeSetTimeout(" not in timeline
    assert "runtimeDelay(" in timeline
    assert "runtimeFetch(" not in timeline and "fetch(" not in timeline

    model = section(source, "    function calculateProcurementBrainModel(", "    function calculateOperationalPressureModel(")
    for evidence in (
        "signal.weightedHistory * 8",
        "signal.currentShortfall * 35",
        "signal.currentUnverified * 10",
        "signal.missionIds.size * 5",
        "signal.events >= 2 || signal.missionIds.size >= 2",
        "Review recruitment levels and training coverage",
        "Monitor repeated demand before purchasing",
    ):
        assert evidence in model, f"Missing Procurement scoring evidence: {evidence}"
    assert "runtimeFetch(" not in model and "fetch(" not in model

    board = section(source, "    function createOperationalPressureBoard()", "    function renderOperationalPressureBoard(")
    for token in (
        'data-pressure-view="live"',
        'data-pressure-view="procurement"',
        'data-pressure-view="timeline"',
        'data-pressure-command="procurement-window"',
        'data-pressure-command="timeline-filter"',
        'data-operational-timeline-search',
        'data-pressure-command="timeline-export"',
        'data-pressure-command="timeline-clear"',
        "never select or dispatch vehicles",
        "never purchases or moves them",
    ):
        assert token in board, f"Operational intelligence board is missing {token}"

    panel = section(source, "    function createPanel(", "    function ensureUi()")
    for action in ('data-action="open-procurement-brain"', 'data-action="open-operational-timeline"'):
        assert action in panel
    palette = section(source, "    function commandPaletteActionEntries(", "    function commandPaletteMissionEntries(")
    assert "Open Procurement Brain" in palette
    assert "Open Operational Timeline" in palette

    assert GUIDE.exists(), "Issue #716 operator guide is missing"
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue716_procurement_timeline_contract.py" in preflight
    assert "test_issue716_procurement_timeline_runtime.mjs" in preflight

    print("Issue #716 static contract passed: bounded local history, evidence-ranked planning, integrated views and read-only safety are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
