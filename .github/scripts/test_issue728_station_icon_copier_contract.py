#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
GUIDE = ROOT / "docs" / "issue-728-station-icon-copier.md"


def source_section(source: str, start: str, end: str) -> str:
    left = source.index(start)
    right = source.index(end, left)
    return source[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.13.0"
    assert "'stationIconCopier'" in source, "Station Icon Copier analytics allow-list entry is missing"
    assert "@connect      *" not in source, "Station Icon Copier must not request wildcard userscript network access"

    panel = source_section(source, "    function createPanel(", "    function ensureUi()")
    dispatch_start = panel.index('<section class="mcms-tab-panel" data-panel="dispatch">')
    dispatch_end = panel.index('<section class="mcms-tab-panel" data-panel="resources">', dispatch_start)
    dispatch_panel = panel[dispatch_start:dispatch_end]
    for token in (
        "Station Icon Copier",
        'data-action="load-station-icons"',
        'data-action="scan-station-icons"',
        'data-action="apply-station-icons"',
        'data-action="stop-station-icons"',
        'data-action="select-all-station-icons"',
        'data-action="clear-station-icons"',
        'data-setting="station-icon-centre"',
        'data-setting="station-icon-source"',
        'data-setting="station-icon-replace-mode"',
        'data-setting="station-icon-delay"',
        'data-station-icon-copier',
        "Protect them (recommended)",
        "Replace selected custom icons",
        "Copy, do not upload",
        "200×200",
    ):
        assert token in dispatch_panel, f"Station Icon Copier panel is missing {token}"

    implementation = source_section(source, "    function stationIconText(", "    function vehicleTargetInfo(")
    for native_contract in (
        "/api/v2/buildings",
        "/api/buildings/",
        "/buildings/${item.buildingId}/edit",
        "new FormData(form)",
        "formData.set('building[image]'",
        "building[leitstelle_building_id]",
        "building[building_type]",
        "building[small_building]",
        "building[caption]",
        "building[latitude]",
        "building[longitude]",
        "authenticity_token",
        "_method",
        "pixelDigest",
    ):
        assert native_contract in implementation, f"Missing native Station Icon Copier contract: {native_contract}"

    for constant in (
        "STATION_ICON_REPLACE_DEFAULTS = 'defaults'",
        "STATION_ICON_REPLACE_ALL = 'all'",
        "STATION_ICON_SCAN_LIMIT = 2000",
        "STATION_ICON_APPLY_LIMIT = 2000",
        "STATION_ICON_REQUEST_TIMEOUT_MS = 15000",
        "STATION_ICON_MAX_DIMENSION = 200",
        "STATION_ICON_MIME_TYPES = Object.freeze(['image/png', 'image/jpeg'])",
    ):
        assert constant in source, f"Missing Station Icon Copier limit or policy: {constant}"

    assert "stationIconTypeKey(record)" in implementation
    assert "record?.small ? '1' : '0'" in implementation, "Small/full station classification must be part of the exact type key"
    assert "record.id === sourceId" in implementation, "Source station must be excluded from its own target queue"
    assert "mode === STATION_ICON_REPLACE_DEFAULTS && record.hasCustomIcon" in implementation
    assert "stationIconRecordInScope(record, scopeId, dispatchById)" in implementation
    assert "scopeId === DISPATCH_RECRUITMENT_ALL_CENTRES" in implementation
    assert "stationIconCopierRuntime.selectedBuildingIds" in implementation
    assert "stationIconCopierRuntime.scannedDispatchId" in implementation
    assert "stationIconCopierRuntime.scannedSourceBuildingId" in implementation
    assert "stationIconCopierRuntime.scannedReplaceMode" in implementation
    assert "stationIconCopierRuntime.preparing = true" in implementation, "Source preparation must lock the plan against double-start and setting races"
    renderer = source_section(implementation, "    function stationIconPanelControlIndex(", "    function readStationIconPlan(")
    assert ".querySelector" not in renderer, "Station Icon Copier rendering must not grow the userscript's exhausted selector-call budget"

    mutation = source_section(implementation, "    function prepareStationIconSubmission(", "    async function loadStationIconCatalog(")
    for guard in (
        "forms.length !== 1",
        "fileControls.length !== 1",
        "action.origin !== pageWindow.location.origin",
        "action.pathname !== `/buildings/${item.buildingId}`",
        "stationIconAssertUnchangedAfterMutation",
        "stationIconImagesMatch(savedImage, sourceImage)",
        "No further stations were changed",
    ):
        assert guard in mutation, f"Missing fail-closed image mutation guard: {guard}"
    assert "headers: { Accept: 'text/html,application/xhtml+xml' }" in mutation
    assert "'Content-Type'" not in source_section(implementation, "    async function submitStationIconForm(", "    async function prepareStationIconSource("), "Multipart uploads must let the browser generate its boundary"

    run = source_section(implementation, "    async function startStationIconCopier(", "    function stopStationIconCopier(")
    assert "const sourceImage =" not in run, "Source preparation uses a mutable binding before confirmation"
    assert "sourceImage = await prepareStationIconSource(plan)" in run
    assert "for (let index = 0; index < planned.length; index += 1)" in run
    assert "Promise.all" not in run, "Station image writes must remain sequential"
    assert "await applyStationIconToStation(item, plan, sourceImage)" in run
    assert "await runtimeDelay(plan.delayMs)" in run
    assert "pageWindow.confirm(`Station Icon Copier will copy" in run
    assert "err?.stationIconFatal" in run
    assert "stationIconCopierRuntime.stopRequested = true" in run
    assert "toolkitAnalyticsRecordFeature('stationIconCopier')" in run

    assert "stationIconCopier: { dispatchId: '', sourceBuildingId: '', replaceMode: STATION_ICON_REPLACE_DEFAULTS, delayMs: 1500 }" in source
    assert "setting.startsWith('station-icon-')" in source
    assert "renderStationIconCopierPanel();" in source
    assert "station-icon-copier" in source_section(source, "    function commandPaletteActionEntries(", "    function commandPaletteMissionEntries(")
    assert GUIDE.exists(), "Issue #728 operator guide is missing"
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue728_station_icon_copier_contract.py" in preflight
    assert "test_issue728_station_icon_copier_runtime.mjs" in preflight

    print("Issue #728 Station Icon Copier source contract passed: exact type/size targeting, protected defaults, native form preservation, sequential writes and pixel verification are fail-closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
