#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")

    for retired in [
        "function incidentCard",
        "renderIncidentCardCanvas",
        "incidentCardRuntime",
        "clearIncidentCardRuntime",
        'data-action="open-incident-card"',
        "data-action=\"open-incident-card\"",
        "data-mcms-command-action=\"incident-card-copy\"",
        "data-mcms-command-action=\"incident-card-download\"",
        "add('incident-card'",
        "toolkitAnalyticsRecordFeature('incidentCard')",
        "if (command === 'card'",
        ".mcms-incident-card-preview",
    ]:
        assert retired not in source, retired

    for required in [
        "dashboard: Object.freeze({ label: 'Dashboard', controls: Object.freeze(['open-vehicle-status', 'open-pressure-board', 'open-command-palette', 'open-map-measure']) })",
        "'open-map-measure': 'Drawing'",
        "measure: '↔'",
        "makeActionFloatButton('open-map-measure', '', 'Drawing'",
        "function syncMapMeasureToolbarButton()",
        "syncMapMeasureToolbarButton();",
        "active ? 'ACTIVE' : 'READY'",
    ]:
        assert required in source, required

    print("Issue #675 retirement contract passed: Incident Card remains absent and the legacy Measure action has safely evolved into Drawing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
