#!/usr/bin/env python3
"""Verify Custom Vehicle Badges against the canonical userscript and runtime fixture."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_custom_vehicle_badges_runtime.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert source == DIST.read_text(encoding="utf-8"), "source/distribution parity failed"
    runtime = subprocess.run(["node", str(RUNTIME)], cwd=ROOT, text=True, capture_output=True)
    if runtime.stdout:
        print(runtime.stdout, end="")
    if runtime.returncode != 0:
        if runtime.stderr:
            print(runtime.stderr, end="")
        raise SystemExit("Custom Vehicle Badges runtime fixtures failed")

    markers = [
        "customVehicleBadgeStyleId: 'mcms-custom-vehicle-badge-style'",
        "customVehicleBadges: true",
        "merged.customVehicleBadges = merged.customVehicleBadges !== false",
        "function customVehicleClassificationFromRecord(record)",
        "record.vehicle_type_caption",
        "record.ignore_aao",
        "function rebuildCustomVehicleClassificationCache()",
        "function customVehicleClassificationForId(vehicleId)",
        "__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__",
        "function customVehicleBadgeApplyRow(row)",
        "data-mcms-custom-vehicle-category",
        "function observeCustomVehicleBadgeDocument(doc)",
        "function installCustomVehicleBadges()",
        "function clearCustomVehicleBadges()",
        "${makeToggleButton('customVehicleBadges', '▣', 'Custom Vehicle Badges', 'Show custom vehicle categories in available vehicles list.')}",
        "if (feature === 'customVehicleBadges') state.customVehicleBadges = !state.customVehicleBadges",
        "customVehicleBadges: state.customVehicleBadges",
        "installCustomVehicleBadges();",
    ]
    compact = re.sub(r"\s+", "", source)
    missing = [marker for marker in markers if marker not in source and re.sub(r"\s+", "", marker) not in compact]
    assert not missing, f"Missing Custom Vehicle Badges markers: {missing}"
    assert source.count("function installCustomVehicleBadges()") == 1
    assert source.count("function customVehicleBadgeApplyRow(row)") == 1
    assert source.count("/api/vehicles") == 1, "feature must reuse the shared vehicle API request"
    module = source.split("// CUSTOM VEHICLE BADGES START", 1)[1].split("// CUSTOM VEHICLE BADGES END", 1)[0]
    assert ".click(" not in module and ".click?.(" not in module, "badge module must not dispatch or select vehicles"
    for theme in ["mapCommand", "cyberpunk", "fallout4", "umbrella", "factorio", "bond007", "hyrule"]:
        assert f'data-mcms-theme=\\"{theme}\\"' in module or f'data-mcms-theme="{theme}"' in module, f"theme missing: {theme}"
    assert "max-width:min(240px,45vw)" in re.sub(r"\s+", "", module)
    assert "@media(max-width:767px)" in re.sub(r"\s+", "", module)
    print("Custom Vehicle Badges contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
