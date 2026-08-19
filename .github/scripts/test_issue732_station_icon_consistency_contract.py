#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
GUIDE = ROOT / "docs" / "issue-732-station-icon-consistency-manager.md"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1)

    panel = section(source, "    function createPanel(", "    function ensureUi()")
    for token in (
        'data-station-icon-centres',
        'data-setting="station-icon-centre-option"',
        'data-action="select-all-station-icon-centres"',
        'data-action="clear-station-icon-centres"',
        "Fix inconsistencies only (pixel verified)",
        "Consistency by Dispatch Centre",
        "Audit, then copy",
    ):
        assert token in source, f"Issue #732 UI contract is missing {token}"
    assert "data-setting=\"station-icon-centre\"" not in panel

    for token in (
        "STATION_ICON_REPLACE_INCONSISTENT = 'inconsistent'",
        "stationIconCopier: { dispatchIds: []",
        "normaliseStationIconDispatchSelection(parsed?.stationIconCopier)",
        "delete merged.stationIconCopier.dispatchId",
        "scannedScopeKey",
        "scannedSourceSignature",
    ):
        assert token in source, f"Issue #732 state or migration contract is missing {token}"

    implementation = section(source, "    function stationIconText(", "    function vehicleTargetInfo(")
    for helper in (
        "function stationIconNormaliseDispatchIds(",
        "function stationIconResolvedDispatchIds(",
        "function stationIconScopeKey(",
        "function stationIconConsistencyPercent(",
        "async function auditStationIconConsistency(",
        "function stationIconImageSignature(",
    ):
        assert helper in implementation, f"Issue #732 helper is missing {helper}"

    audit = section(
        implementation,
        "    async function auditStationIconConsistency(",
        "    function stationIconSafeSkip(",
    )
    for guard in (
        "signatureCache",
        "stationIconMoveConsistency(summary, item, 'consistent')",
        "stationIconMoveConsistency(summary, item, 'inconsistent')",
        "stationIconMoveConsistency(summary, item, 'unverified')",
        "item.auditSignature",
        "item.consistency === 'inconsistent'",
        "sourceSignature",
    ):
        assert guard in audit, f"Issue #732 audit guard is missing {guard}"
    assert "Promise.all" not in audit, "Consistency image reads must remain deliberately sequential"

    apply_one = section(
        implementation,
        "    async function prepareStationIconSource(",
        "    async function loadStationIconCatalog(",
    )
    assert "stationIconImagesMatch(image, stationIconCopierRuntime.scannedSourceSignature)" in apply_one
    assert "plan.replaceMode === STATION_ICON_REPLACE_INCONSISTENT" in apply_one
    assert "!item.auditSignature || !stationIconImagesMatch(currentImage, item.auditSignature)" in apply_one
    assert "the custom icon changed after its pixel audit" in apply_one

    run = section(
        implementation,
        "    async function startStationIconCopier(",
        "    function stopStationIconCopier(",
    )
    assert "stationIconMoveConsistency(stationIconCopierRuntime.summary, item, 'consistent')" in run
    assert "stationIconConsistencyPercent(stationIconCopierRuntime.summary)" in run
    assert "for (let index = 0; index < planned.length; index += 1)" in run
    assert "Promise.all" not in run, "Station image writes must remain sequential"

    assert GUIDE.exists(), "Issue #732 operator and implementation guide is missing"
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue732_station_icon_consistency_contract.py" in preflight
    assert "test_issue732_station_icon_consistency_runtime.mjs" in preflight

    print(
        "Issue #732 Station Icon consistency source contract passed: multi-centre scope, "
        "pixel-only repair, freshness guards and live scoring remain fail-closed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
