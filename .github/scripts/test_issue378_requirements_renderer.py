#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")

required = [
    "// Issue #378 enhanced requirements runtime renderer.",
    "function operationalRequirementsRuntimeCatalog()",
    "MISSION_REQUIREMENT_DEFINITIONS",
    "function operationalRequirementsSelectedSnapshot(doc)",
    "#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked",
    "function operationalRequirementsDrivingSnapshot(doc)",
    "#mission_vehicle_driving tbody tr",
    "function operationalRequirementsBindContext(context)",
    "attributeFilter: ['checked', 'vehicle_type_id'",
    "function operationalRequirementsEquivalentLssmActive(doc)",
    ".alert-missing-vehicles[data-raw-html]",
    "data-mcms-operational-suite",
    "mcms-operational-suite-panel",
    "@media(max-width:760px)",
    "env(safe-area-inset-top)",
    "operationalRequirementFingerprint(model",
    "fingerprint === context.fingerprint",
]
for needle in required:
    if needle not in source:
        raise SystemExit(f"Issue #378 renderer marker missing: {needle}")

for forbidden in [
    "new Vue(",
    "createPinia(",
    "LSS-Manager",
    "document.documentElement.observe",
]:
    if forbidden in source:
        raise SystemExit(f"Issue #378 renderer contains forbidden runtime dependency/pattern: {forbidden}")

start = source.index("// Issue #378 enhanced requirements runtime renderer.")
end = source.index("// Issue #378 end enhanced requirements runtime renderer.", start)
block = source[start:end]
if block.count("new MutationObserver(") != 1:
    raise SystemExit("Issue #378 renderer must use one reusable scoped MutationObserver per context")
if "doc.addEventListener('change', context.changeHandler, true)" not in block:
    raise SystemExit("Issue #378 renderer checkbox change listener is missing")
if "doc.removeEventListener('change', context.changeHandler, true)" not in source:
    raise SystemExit("Issue #378 renderer checkbox listener teardown is missing")
if "panel.innerHTML = rendered.html" not in block:
    raise SystemExit("Issue #378 renderer output assignment is missing")
if "requirementRoot.parentNode?.insertBefore(panel, requirementRoot)" not in block:
    raise SystemExit("Issue #378 renderer must remain in normal document flow")

print("Issue #378 enhanced requirements renderer contract passed.")

if '// Issue #133 clean-room live mission requirements matrix.' in source:
    raise SystemExit('legacy Matrix marker survived renderer cutover')
