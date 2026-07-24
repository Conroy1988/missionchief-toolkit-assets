#!/usr/bin/env python3
"""Protect the retained Mission Age map timer badge while retiring Age Watch."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "missionAge: false",
        "makeToggleButton('missionAge'",
        "function formatMissionAge(",
        "function makeMissionAgeIcon(",
        "function updateMissionAgeLabels(",
        "function clearMissionAgeLabels(",
        "if (state.missionAge) scheduleMissionAgeRefresh();",
        "if (!state.missionAge) clearMissionAgeLabels();",
    ]
    missing = [marker for marker in required if marker not in source]
    assert not missing, f"Mission Age map timer contract changed: {missing}"
    forbidden = ["Mission Age Workflow", "Age Watch", "missionAgeWatch", "critical-countdowns", "open-critical-drawer"]
    for marker in forbidden:
        if marker == "missionAgeWatch":
            assert source.count(marker) == 1 and "delete merged.missionAgeWatch;" in source
        else:
            assert marker not in source, f"Retired Age Watch artefact returned: {marker}"
    print("v6 Mission Age contract passed: map timer badges retained; workflow/watch removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
