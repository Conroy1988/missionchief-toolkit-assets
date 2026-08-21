#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
GUIDE = ROOT / "docs" / "issue-706-dispatch-recruitment.md"


def source_section(source: str, start: str, end: str) -> str:
    left = source.index(start)
    right = source.index(end, left)
    return source[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.13.3"
    assert "'dispatchRecruitment'" in source, "Dispatch Recruitment analytics allow-list entry is missing"
    assert "'dispatch'" in source_section(source, "    const COMMAND_SECTION_ORDER", "    const COMMAND_PALETTE_RESULT_LIMIT")
    assert "label: 'Dispatch'" in source and "title: 'Dispatch Administration'" in source

    panel = source_section(source, "    function createPanel(", "    function ensureUi()")
    dispatch_start = panel.index('<section class="mcms-tab-panel" data-panel="dispatch">')
    dispatch_end = panel.index('<section class="mcms-tab-panel" data-panel="resources">', dispatch_start)
    dispatch_panel = panel[dispatch_start:dispatch_end]
    for token in (
        'data-action="load-dispatch-recruitment"',
        'data-action="scan-dispatch-recruitment"',
        'data-action="apply-dispatch-recruitment"',
        'data-action="stop-dispatch-recruitment"',
        'data-action="select-all-dispatch-recruitment"',
        'data-action="clear-dispatch-recruitment"',
        'data-setting="dispatch-recruitment-centre"',
        'data-setting="dispatch-recruitment-building-type"',
        'data-setting="dispatch-recruitment-hiring-phase"',
        'data-setting="dispatch-recruitment-personnel"',
        'data-setting="dispatch-recruitment-delay"',
        'data-dispatch-recruitment',
        'Personnel (Desired)',
        'Apply to Selected',
        'ALL DISPATCH CENTRES',
        'ALL BUILDING TYPES',
    ):
        assert token in dispatch_panel, f"Dispatch Recruitment panel is missing {token}"
    for phase in ('value="0">Off', 'value="1">1 day', 'value="2">2 days', 'value="3">3 days', 'value="automatic">Automatic'):
        assert phase in dispatch_panel, f"Hiring Phase option is missing: {phase}"

    implementation = source_section(source, "    const DISPATCH_RECRUITMENT_PHASE_META", "    function vehicleTargetInfo(")
    for native_contract in (
        '#building_leitstelle_building_id[name="building[leitstelle_building_id]"]',
        '#building_building_type[name="building[building_type]"]',
        '#building_table tr.alliance_buildings_table_searchable',
        '.building_leitstelle_set_',
        'leitstelle-set',
        '.personal_count_target_edit_button',
        '/personalCountTarget',
        'input[name="building[personal_count_target]"]',
        'input[name="authenticity_token"]',
        'input[name="_method"]',
        "params.set('_method', 'patch')",
        "params.set('building[personal_count_target]'",
        '/hire_do/',
        '/api/buildings/',
    ):
        assert native_contract in implementation, f"Missing native Dispatch Recruitment contract: {native_contract}"

    assert "catalog.typeLabels" in implementation
    assert "buildDispatchRecruitmentQueue(allCentres ? matrices : matrices[0], dispatchRecruitmentRuntime.typeLabels, dispatchId, dispatches, buildingTypeId)" in implementation
    assert "dispatchId === DISPATCH_RECRUITMENT_ALL_CENTRES" in implementation
    assert "allCentres ? !dispatchById.has(assignedDispatchId) : assignedDispatchId !== dispatchId" in implementation
    assert "outsideDispatch" in implementation
    assert "dispatchCounts" in implementation
    assert "dispatchId: assignedDispatchId" in implementation
    assert "dispatchName: dispatchById.get(assignedDispatchId)?.name" in implementation
    assert "typeLabels[typeId] || `Building type ${typeId}`" in implementation
    assert "DISPATCH_RECRUITMENT_SCAN_LIMIT = 2000" in source
    assert "DISPATCH_RECRUITMENT_APPLY_LIMIT = 2000" in source
    assert "DISPATCH_RECRUITMENT_REQUEST_TIMEOUT_MS = 12000" in source
    assert "DISPATCH_RECRUITMENT_PERSONNEL_MAX = 10000" in source
    assert "selectedBuildingIds: new Set()" in source
    assert "selectedTypeIds: new Set()" in source
    assert "scannedTypeId: ''" in source
    assert 'data-setting="dispatch-recruitment-type"' in implementation
    assert 'data-setting="dispatch-recruitment-station"' in implementation
    assert "const matrices = Array.isArray(doc) ? doc : [doc]" in implementation
    assert "const seen = new Map()" in implementation
    assert "Conflicting native Dispatch Centre or building-type evidence" in implementation
    assert "queue.length >= DISPATCH_RECRUITMENT_SCAN_LIMIT" in implementation
    assert "runtimeState.currentItem" in implementation
    assert "buildingTypeId !== DISPATCH_RECRUITMENT_ALL_TYPES && typeId !== buildingTypeId" in implementation
    assert "setDispatchRecruitmentBuildingTypeScope" in implementation

    scan = source_section(implementation, "    async function scanDispatchRecruitmentStations(", "    function dispatchRecruitmentSafeSkip(")
    assert "const scanDispatches = allCentres ? dispatches : dispatch ? [dispatch] : []" in scan
    assert "for (let index = 0; index < scanDispatches.length; index += 1)" in scan
    assert "Scanning ${index + 1} of ${scanDispatches.length}" in scan
    assert "finalUrl.pathname.replace(/\\/+$/u, '') !== matrixPath" in scan
    assert "doc.getElementsByTagName('table').namedItem('building_table')?.id !== 'building_table'" in scan
    assert "Promise.all" not in scan, "Native centre matrices must be fetched sequentially"
    assert "dispatchRecruitmentRuntime.scannedTypeId = buildingTypeId" in scan

    for guard in (
        "url.origin !== pageWindow.location.origin",
        "actualDispatchId !== expectedDispatchId",
        "String(record?.building_type ?? '') !== item.typeId",
        "dispatchRecruitmentRecordMatches(verified, plan)",
        "No further stations were changed",
        "pageWindow.confirm(`Dispatch Recruitment will update",
        "await runtimeDelay(plan.delayMs)",
        "stopRequested = true",
    ):
        assert guard in implementation, f"Missing fail-closed recruitment guard: {guard}"
    for immutability_guard in (
        "assignedDispatchId === '0'",
        "summary.unassigned += 1",
        "dispatchRecruitmentGuardMutation(action.href, params.toString())",
        "dispatchRecruitmentAssertStationScope(record, item, expectedDispatchId, true)",
        "unexpectedBuildingFields",
        "dispatchRecruitmentFatal = true",
        "No further stations were changed",
        "result.partial ? 'partial' : 'updated'",
    ):
        assert immutability_guard in implementation, f"Missing Dispatch Centre immutability guard: {immutability_guard}"
    personnel = source_section(implementation, "    function prepareDispatchRecruitmentPersonnelSubmission(", "    async function prepareDispatchRecruitmentHiring(")
    assert "for (const hidden of form.querySelectorAll" not in personnel, "Personnel submission must not forward arbitrary hidden form fields"
    assert "params.set('building[leitstelle_building_id]'" not in implementation
    assert "/hire_do/coins" not in implementation and "hire_do/credits" not in implementation
    run = source_section(source, "    async function startDispatchRecruitment(", "    function stopDispatchRecruitment(")
    assert "for (let index = 0; index < planned.length; index += 1)" in run
    assert "Promise.all" not in run, "Station writes must remain sequential"
    assert "err?.dispatchRecruitmentFatal" in run
    assert "dispatchRecruitmentRuntime.stopRequested = true" in run
    assert "if (dispatchRecruitmentRuntime.stopRequested) break" in run
    assert "toolkitAnalyticsRecordFeature('dispatchRecruitment')" in run

    assert "dispatchRecruitment: { dispatchId: '', buildingTypeId: DISPATCH_RECRUITMENT_ALL_TYPES, hiringPhase: '3', personnelDesired: '', delayMs: 1500 }" in source
    assert "dispatchRecruitmentDispatchId === DISPATCH_RECRUITMENT_ALL_CENTRES" in source
    assert "dispatchRecruitmentBuildingTypeId === DISPATCH_RECRUITMENT_ALL_TYPES" in source
    assert "DISPATCH_RECRUITMENT_HIRING_PHASE_OPTIONS.includes" in source
    assert "DISPATCH_RECRUITMENT_DELAY_OPTIONS.includes" in source
    assert "setting.startsWith('dispatch-recruitment-')" in source
    assert "[data-setting^=\"dispatch-recruitment-\"]" in implementation
    assert GUIDE.exists(), "Issue #706 operator guide is missing"
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue706_dispatch_recruitment_contract.py" in preflight
    assert "test_issue706_dispatch_recruitment_runtime.mjs" in preflight

    print("Issues #706/#724/#726 Dispatch Recruitment source contract passed: centre/type scope, complete sequential matrices, global deduplication and mutation immutability are fail-closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
