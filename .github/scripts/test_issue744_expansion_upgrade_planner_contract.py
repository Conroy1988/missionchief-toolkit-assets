#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
GUIDE = ROOT / "docs" / "issue-744-expansion-upgrade-planner.md"


def source_section(source: str, start: str, end: str) -> str:
    left = source.index(start)
    right = source.index(end, left)
    return source[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.14.0"
    assert "'expansionPlanner'" in source, "Expansion Planner analytics allow-list entry is missing"
    assert "expansion-upgrade-planner" in source_section(source, "    function commandPaletteActionEntries(", "    function commandPaletteMissionEntries(")
    assert "@connect      *" not in source, "Expansion Planner must not request wildcard userscript network access"

    panel = source_section(source, "    function createPanel(", "    function ensureUi()")
    dispatch_start = panel.index('<section class="mcms-tab-panel" data-panel="dispatch">')
    dispatch_end = panel.index('<section class="mcms-tab-panel" data-panel="resources">', dispatch_start)
    dispatch_panel = panel[dispatch_start:dispatch_end]
    for token in (
        "Expansion &amp; Upgrade Planner",
        'data-action="load-expansion-planner"',
        'data-action="scan-expansion-planner"',
        'data-action="apply-expansion-planner"',
        'data-action="stop-expansion-planner"',
        'data-action="select-all-expansion-planner"',
        'data-action="clear-expansion-planner"',
        'data-setting="expansion-planner-centre"',
        'data-setting="expansion-planner-building-type"',
        'data-setting="expansion-planner-operation"',
        'data-setting="expansion-planner-budget"',
        'data-setting="expansion-planner-max-stations"',
        'data-setting="expansion-planner-delay"',
        "Credits only",
        "never uses a static cost table",
        "never retried automatically",
        "data-expansion-planner",
    ):
        assert token in dispatch_panel, f"Expansion Planner panel is missing {token}"

    implementation = source_section(source, "    function expansionPlannerText(", "    function vehicleTargetInfo(")
    for contract in (
        "/api/v2/buildings",
        "/api/buildings/",
        "/buildings/${record.id}",
        "data-method",
        "data-turbo-method",
        "authenticity_token",
        "credentials: 'same-origin'",
        "cache: 'no-store'",
        "priceCredits",
        "actionPath",
        "fingerprint",
        "expansionPlannerExtensionDigest",
        "expansionPlannerAssertScope",
        "persistExpansionPlannerReport",
    ):
        assert contract in implementation, f"Missing native Expansion Planner contract: {contract}"

    for constant in (
        "EXPANSION_PLANNER_SCAN_STATION_LIMIT = 500",
        "EXPANSION_PLANNER_SCAN_CONCURRENCY = 4",
        "EXPANSION_PLANNER_OPERATION_LIMIT = 1000",
        "EXPANSION_PLANNER_APPLY_LIMIT = 100",
        "EXPANSION_PLANNER_MAX_BUDGET = 2000000000",
        "EXPANSION_PLANNER_REQUEST_TIMEOUT_MS = 15000",
    ):
        assert constant in source, f"Missing Expansion Planner hard limit: {constant}"

    parser = source_section(implementation, "    function expansionPlannerControlText(", "    function expansionPlannerPublicOperation(")
    assert "/\\b(?:coins?|gold)\\b/" in parser, "Coin and gold controls must be rejected before parsing a price"
    assert "\\s*credits?\\b" in parser, "A positive Credits label must be required on the native control itself"
    assert "url.origin !== pageWindow.location.origin" in parser
    assert "method !== 'post'" in parser
    assert "url.search || url.hash" in parser
    assert "(?:ready|finish|cancel|delete|remove|disable|enable|coin|gold)" in parser
    assert "levelPrices" not in implementation and "levelcost" not in implementation, "Prices must never come from a static building table"

    scan = source_section(implementation, "    async function scanExpansionPlanner(", "    function expansionPlannerPlannedQueue(")
    assert "EXPANSION_PLANNER_SCAN_CONCURRENCY" in scan
    assert "fetchExpansionPlannerDocument(`/buildings/${record.id}`)" in scan
    assert "selectedOperationIds = new Set()" in scan, "A fresh scan must not pre-approve purchases"

    selection = source_section(implementation, "    function expansionPlannerSelectTargets(", "    function expansionPlannerFindCurrentAction(")
    assert "usedBuildings" in selection
    assert "candidate.buildingId === item.buildingId" in selection, "Selecting an operation must remove every other operation for that station"

    mutation = source_section(implementation, "    function expansionPlannerFindCurrentAction(", "    function normaliseExpansionPlannerReport(")
    for guard in (
        "matches.length !== 1",
        "operation.priceCredits !== item.priceCredits",
        "before.level !== item.level",
        "expansionPlannerHasPendingConstruction",
        "operation.priceCredits > budgetRemaining",
        "expansionPlannerStoppedBeforeMutation",
        "submitExpansionPlannerOperation",
        "stillOffered",
        "after.level === before.level + 1",
        "expansionPlannerExtensionDigest(after) === expansionPlannerExtensionDigest(before)",
        "No further purchases were attempted",
    ):
        assert guard in mutation, f"Missing fail-closed purchase guard: {guard}"

    run = source_section(implementation, "    async function startExpansionPlanner(", "    function stopExpansionPlanner(")
    assert "preflightExpansionPlannerSelection(planned)" in run
    assert "EXACT TOTAL:" in run and "HARD BUDGET:" in run
    assert "new Set(planned.map(item => item.buildingId)).size !== planned.length" in run
    assert "for (let index = 0; index < confirmedPlan.length; index += 1)" in run
    assert "Promise.all(confirmedPlan" not in run, "Purchase writes must remain sequential"
    assert "await applyExpansionPlannerOperation" in run
    assert "await runtimeDelay(state.expansionPlanner.delayMs)" in run
    assert "expansionPlannerRuntime.stopRequested = true" in run
    assert "toolkitAnalyticsRecordFeature('expansionPlanner')" in run

    assert "setInterval" not in implementation and "MutationObserver" not in implementation, "Expansion Planner must remain manual and on-demand"
    assert "expansionPlannerReportState" in source
    assert "gmDeleteValueSafe(SCRIPT.expansionPlannerReportState)" in implementation
    assert GUIDE.exists(), "Issue #744 operator guide is missing"
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue744_expansion_upgrade_planner_contract.py" in preflight
    assert "test_issue744_expansion_upgrade_planner_runtime.mjs" in preflight

    print("Issue #744 Expansion & Upgrade Planner source contract passed: live Credit-only discovery, exact-total confirmation, one operation per station, sequential writes and persistent fail-closed reporting are enforced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
