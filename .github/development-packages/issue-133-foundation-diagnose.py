#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs" / "issue-133-foundation-anchor-diagnostics.json"

source = SOURCE.read_text(encoding="utf-8")
anchors = {
    "script_panel_id": "        transportSweepHudId: 'mc-map-command-toolkit-transport-sweep-hud',\n",
    "lifecycle_state": "    const missionValueRetryState = new WeakMap();\n",
    "default_state": "            missionValue: true,\n",
    "normalised_state": "        merged.missionValue = merged.missionValue !== false;\n",
    "old_instance_cleanup": "#${SCRIPT.missionInspectorId}, #${SCRIPT.helpCenterId}",
    "implementation_insertion": "    function criticalMissionValueForEntry(entry) {\n",
    "ops_toggle": "                    ${makeToggleButton('missionValue', '£', 'Mission Value', 'Show a formatted mission value in opened MissionChief windows.')}\n",
    "toggle_mutation": "        if (feature === 'missionValue') state.missionValue = !state.missionValue;\n",
    "toggle_lifecycle": "        if (feature === 'missionValue') {\n            if (state.missionValue) installMissionValueWindows();\n            else clearMissionValueIndicators();\n            showToast(state.missionValue ? 'Mission Value on' : 'Mission Value off');\n        }\n",
    "update_ui_toggle": "            missionValue: state.missionValue,\n",
    "mutation_ownership_id": "                target.id === SCRIPT.missionInspectorId ||\n",
    "mutation_ownership_ancestor": "                target.closest?.(`#${SCRIPT.missionInspectorId}`)\n",
    "boot_installation": "        observeCreditValue();\n\n        startBootAttemptCoordinator(bootPerformanceStartedAt);\n",
    "main_mutation_routing": "                if (missionChanged) scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n",
}

result = {
    "version_occurrences": source.count("4.14.10"),
    "anchors": {},
}
for name, anchor in anchors.items():
    count = source.count(anchor)
    result["anchors"][name] = {
        "count": count,
        "anchor": anchor,
    }

REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({name: item["count"] for name, item in result["anchors"].items()}, indent=2))
print(f"Wrote {REPORT.relative_to(ROOT)}")
