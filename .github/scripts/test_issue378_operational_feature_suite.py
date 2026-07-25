#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")
start = source.index("// Issue #378 complete operational feature suite.")
end = source.index("// Issue #378 end complete operational feature suite.", start)
block = source[start:end]
required = [
    "function operationalWindowSettingsInnerMarkup()",
    "function operationalWindowSectionMarkup(section)",
    "function handleOperationalWindowSettingChange(target)",
    "function operationalCallWindowApply(context)",
    "function operationalMissionListComputeOrder(records",
    "function operationalMissionListApply(context)",
    "function operationalTransportChooseAction(route",
    "eligible.length === 1 ? eligible[0] : null",
    "feature.transportTokens.add(action.token)",
    "function operationalFeatureObservationRoots(doc)",
    "function operationalFeatureRenderContext(context)",
    "function operationalFeatureCleanupContext(context)",
    "env(safe-area-inset-left)",
    "data-operational-setting",
    "data-operational-settings-root",
    "OPERATIONAL_SETTINGS_SCHEMA.map(operationalWindowSectionMarkup).join('')",
    "operationalFeatureRenderContext(context);",
    "...operationalFeatureObservationRoots(doc)",
    "operationalFeatureCleanupContext(context);",
    "${operationalWindowSettingsInnerMarkup()}",
    "if (handleOperationalWindowSettingChange(target)) return;",
    "operationalWindowSyncSettingsUi();",
    "phase: 'operational-suite'",
]
for needle in required:
    if needle not in source:
        raise SystemExit(f"Issue #378 operational feature marker missing: {needle}")
for retired in ["function operationalWindowSettingsMarkup()", "${operationalWindowSettingsMarkup()}"]:
    if retired in source:
        raise SystemExit(f"Issue #378 obsolete raw settings renderer returned: {retired}")
for forbidden in ["new MutationObserver(", ".addEventListener(", "setInterval(", "LSS-Manager", "createPinia(", "new Vue("]:
    if forbidden in block:
        raise SystemExit(f"Issue #378 operational feature block contains forbidden pattern: {forbidden}")
for path in [
    ROOT / ".github" / "diagnostics" / "issue378-suite-integration-map.txt",
    ROOT / ".github" / "diagnostics" / "issue378-targeted-integration-excerpts.txt",
    ROOT / ".github" / "development-packages" / "issue378-operational-feature-suite.payload.00",
    ROOT / ".github" / "development-packages" / "issue378-operational-feature-suite.payload.01",
]:
    if path.exists():
        raise SystemExit(f"Issue #378 temporary staging file remains: {path.relative_to(ROOT)}")
print("Issue #378 complete operational feature-suite contract passed with typed v6 settings.")
