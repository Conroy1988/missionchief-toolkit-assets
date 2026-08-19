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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.9.3"
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
        'data-setting="dispatch-recruitment-hiring-phase"',
        'data-setting="dispatch-recruitment-personnel"',
        'data-setting="dispatch-recruitment-delay"',
        'data-dispatch-recruitment',
        'Personnel (Desired)',
        'Apply to Selected',
        'station-type filters',
        'ALL DISPATCH CENTRES',
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
    assert "buildDispatchRecruitmentQueue(doc, dispatchRecruitmentRuntime.typeLabels, dispatchId, dispatches)" in implementation
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
    assert 'data-setting="dispatch-recruitment-type"' in implementation
    assert 'data-setting="dispatch-recruitment-station"' in implementation

    for guard in (
        "url.origin !== pageWindow.location.origin",
        "String(baseline.leitstelle_building_id ?? '') !== expectedDispatchId",
        "String(baseline.building_type ?? '') !== item.typeId",
        "dispatchRecruitmentRecordMatches(verified, plan)",
        "no automatic retry was made",
        "pageWindow.confirm(`Dispatch Recruitment will update",
        "await runtimeDelay(plan.delayMs)",
        "stopRequested = true",
    ):
        assert guard in implementation, f"Missing fail-closed recruitment guard: {guard}"
    assert "/hire_do/coins" not in implementation and "hire_do/credits" not in implementation
    run = source_section(source, "    async function startDispatchRecruitment(", "    function stopDispatchRecruitment(")
    assert "for (let index = 0; index < planned.length; index += 1)" in run
    assert "Promise.all" not in run, "Station writes must remain sequential"
    assert "toolkitAnalyticsRecordFeature('dispatchRecruitment')" in run

    assert "dispatchRecruitment: { dispatchId: '', hiringPhase: '3', personnelDesired: '', delayMs: 1500 }" in source
    assert "dispatchRecruitmentDispatchId === DISPATCH_RECRUITMENT_ALL_CENTRES" in source
    assert "DISPATCH_RECRUITMENT_HIRING_PHASE_OPTIONS.includes" in source
    assert "DISPATCH_RECRUITMENT_DELAY_OPTIONS.includes" in source
    assert "setting.startsWith('dispatch-recruitment-')" in source
    assert "[data-setting^=\"dispatch-recruitment-\"]" in implementation
    assert GUIDE.exists(), "Issue #706 operator guide is missing"
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue706_dispatch_recruitment_contract.py" in preflight
    assert "test_issue706_dispatch_recruitment_runtime.mjs" in preflight

    print("Issue #706 Dispatch Recruitment source contract passed: dynamic native types, exact selection, sequential writes and response verification are guarded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
