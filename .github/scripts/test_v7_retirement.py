#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
TOKEN = "ls" + "sm"
def main() -> int:
    source = SOURCE.read_text(encoding="utf-8"); lower = source.lower()
    metadata = re.search(r"(?m)^// @version\s+([0-9]+)\.([0-9]+)\.([0-9]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(0).split()[-1] == runtime.group(1)
    assert tuple(map(int, metadata.groups())) >= (7, 0, 0)
    assert TOKEN not in lower
    forbidden = ["Operational Window Suite", "Enhanced Operational Requirements", "Extended Call Window", "Extended Call List", "Enhanced Transport Requests", "operationalSuite", "operationalFeature", "operationalRequirements", "OPERATIONAL_SETTINGS_SCHEMA", "data-operational-settings-root", "installOperationalSuiteShell", "handleOperationalWindowSettingChange"]
    present = [item for item in forbidden if item in source]; assert not present, present
    assert source.count("operationalWindow") == 1 and "delete merged.operationalWindow;" in source
    assert source.count("missionRequirements") == 1 and "delete merged.missionRequirements;" in source
    retained = ["missionAge: false", "function missionAgeRefreshPlan(", "function updateMissionAgeLabels(", "makeToggleButton('missionAge'", "function missionWindowValueDetails(", "function customVehicleBadgeVehicleId(", "function collectTransportSweepVehicleCandidatesForMission(", "async function openTransportSweepVehicle(", "function transportSweepVisibleDischargeButtons(", "function recordTransportSweepConfirmedRelease(", "function renderTransportSweepHud(", "Vehicle Code Status", "Transport Watcher", "Resource Gap", "Major Incident Feed"]
    missing = [item for item in retained if item not in source]; assert not missing, missing
    assert "missionRequirementsVehicleId(checkbox || row)" not in source
    assert "MissionChief's visible native workflow" in source
    tracked=[]
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
        if path.parent == ROOT and path.name in {"MissionChief_Map_Command_Toolkit.user.js", "MissionChief_Map_Command_Toolkit.txt"}: continue
        if "toolkit-current" in path.parts or "dist" in path.parts: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())
        try: text=path.read_text(encoding="utf-8")
        except (UnicodeDecodeError,OSError): continue
        if TOKEN in text.lower(): tracked.append(path.as_posix())
    assert not tracked, sorted(set(tracked))
    print("v7 retirement contract passed.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
