#!/usr/bin/env python3
"""Static invariants for conservative v4.13.1 runtime reductions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def section(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    finish = text.index(end, begin)
    return text[begin:finish]


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    prune = section(text, "function pruneRuntimeCaches", "function installAllianceBuildingsPageOptimisation")
    assert prune.count("getVehicleMarkerLayers()") == 1
    assert prune.count("getBuildingMarkerLayers()") == 1
    assert "new Set(getVehicleMarkerLayers())" in prune
    assert "new Set(getBuildingMarkerLayers())" in prune
    assert "currentVehicleLayers.has(layer)" in prune
    assert "currentBuildingLayers.has(layer)" in prune

    auto_load = section(text, "function autoLoadAllVehiclesResolveMissionRoot", "function clearAutoLoadAllVehiclesReleaseTimer")
    assert "closest?.(AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR)" in auto_load
    assert "autoLoadAllVehiclesMissionRoot?.isConnected" in auto_load
    assert "autoLoadAllVehiclesElementVisible(autoLoadAllVehiclesMissionRoot)" in auto_load
    assert "queryRoot.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR)" in auto_load
    assert "document.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR)" not in auto_load
    print("Runtime optimisation invariants passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
