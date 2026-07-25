#!/usr/bin/env python3
"""Fail-closed contracts for the v6.0.0 feature retirement boundary."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert re.search(r"(?m)^// @version\s+6\.0\.0$", source), "Userscript metadata is not v6.0.0"
    assert "version: '6.0.0'" in source, "Runtime version is not v6.0.0"

    retired_state_keys = ["autoNight", "heatmap", "missionInspector", "missionAgeWatch"]
    for key in retired_state_keys:
        marker = f"delete merged.{key};"
        assert source.count(key) == 1, f"Retired feature {key} still has live references"
        assert marker in source, f"Retired feature {key} lacks safe persisted-state migration"

    forbidden = [
        "Automatic day / night",
        "Automatic day/night",
        "Heatmap",
        "Mission Inspector",
        "Mission Age Workflow",
        "Age Watch",
        "criticalView",
        "criticalDrawerId",
        "missionInspectorId",
        "open-critical-drawer",
        "fit-critical",
        "critical-countdowns",
        "auto-night",
        "clearCoverageHeatmap",
        "scheduleCriticalDrawerDock",
        "closeCriticalViewControls",
    ]
    present = [token for token in forbidden if token in source]
    assert not present, f"Retired feature artefacts remain: {present}"

    retained = [
        "missionAge: false",
        "function formatMissionAge(",
        "function clearMissionAgeLabels(",
        "function makeMissionAgeIcon(",
        "function updateMissionAgeLabels(",
        "function scheduleMissionAgeRefresh(",
        "function missionAgeSeverity(",
        "makeToggleButton('missionAge'",
    ]
    missing = [token for token in retained if token not in source]
    assert not missing, f"Retained Mission Age map badges were damaged: {missing}"

    print("v6 feature retirement passed: five obsolete systems removed and Mission Age map badges retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
