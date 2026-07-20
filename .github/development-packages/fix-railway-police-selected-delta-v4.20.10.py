#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
DOC = ROOT / "docs" / "issue-242-railway-police-selected-delta-contract.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.9", "// @version      4.20.10", "metadata version")
source = replace_once(source, "version: '4.20.9',", "version: '4.20.10',", "runtime version")
source = replace_once(source, "guideVersion: '4.20.9',", "guideVersion: '4.20.10',", "guide version")

resolve_marker = "function missionRequirementsResolve(candidate, parsed, catalogue = null)"
if source.count(resolve_marker) != 1:
    raise AssertionError(f"resolver marker count: {source.count(resolve_marker)}")
helper = r'''function missionRequirementsReconcileCommittedDelta(requirement, baselineValue, selectedCapacity, respondingCapacity, onSiteCapacity) {
        const baseline = missionRequirementsOptionalNumber(baselineValue);
        const selected = missionRequirementsCapacity(selectedCapacity?.min ?? selectedCapacity?.value ?? 0, selectedCapacity?.max, selectedCapacity?.known);
        const responding = missionRequirementsCapacity(respondingCapacity?.min ?? respondingCapacity?.value ?? 0, respondingCapacity?.max, respondingCapacity?.known);
        const onSite = missionRequirementsCapacity(onSiteCapacity?.min ?? onSiteCapacity?.value ?? 0, onSiteCapacity?.max, onSiteCapacity?.known);
        if (baseline === null || requirement?.statedRequirement === false) return { selected, responding, onSite };

        const liveMissing = Math.max(0, Number(requirement?.missing) || 0);
        const committed = Math.max(0, baseline - liveMissing);
        const operationalMin = onSite.min + responding.min;
        const operationalMax = onSite.max === null || responding.max === null ? null : onSite.max + responding.max;
        const inferredSelectedMin = operationalMax === null ? 0 : Math.max(0, committed - operationalMax);
        const inferredSelectedMax = Math.max(0, committed - operationalMin);
        if (inferredSelectedMax <= selected.min) return { selected, responding, onSite };

        const selectedMin = Math.max(selected.min, inferredSelectedMin);
        const selectedMax = selected.max === null ? inferredSelectedMax : Math.max(selected.max, inferredSelectedMax);
        const selectedKnown = selectedMax !== null && selectedMin === selectedMax && onSite.known && responding.known;
        return {
            selected: missionRequirementsCapacity(selectedMin, selectedMax, selectedKnown),
            responding,
            onSite
        };
    }

    '''
source = source.replace(resolve_marker, helper + resolve_marker, 1)

old_inference = re.compile(
    r"if \(baseline !== null && hasStatedRequirement\) \{\s*"
    r"const inferredOnSite = Math\.max\(0, baseline - Math\.max\(0, Number\(requirement\.missing\) \|\| 0\)\);\s*"
    r"if \(inferredOnSite > onSite\.min\) \{\s*"
    r"const inferredMax = onSite\.max === null \? null : Math\.max\(onSite\.max, inferredOnSite\);\s*"
    r"onSite = missionRequirementsCapacity\(inferredOnSite, inferredMax, onSite\.known && inferredMax === inferredOnSite\);\s*"
    r"\}\s*\}"
)
replacement = "if (baseline !== null && hasStatedRequirement) { ({ selected, responding, onSite } = missionRequirementsReconcileCommittedDelta(requirement, baseline, selected, responding, onSite)); }"
source, inference_count = old_inference.subn(replacement, source, count=1)
if inference_count != 1:
    raise AssertionError(f"legacy inferred-On-site block count: {inference_count}")
if "const inferredOnSite =" in source:
    raise AssertionError("legacy inferred-On-site assignment remains")
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.9'", "version: '4.20.10'", "runtime fixture version")
runtime = replace_once(
    runtime,
    "    resolve: missionRequirementsResolve,\n",
    "    resolve: missionRequirementsResolve,\n    reconcileCommittedDelta: missionRequirementsReconcileCommittedDelta,\n",
    "runtime helper export",
)
anchor = "assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');\n"
tests = r'''

// Issue #242: MissionChief's live missing total can already include selected personnel.
const issue242Zero = api.capacity(0, 0, true);
let issue242Delta = api.reconcileCommittedDelta(
    { missing: 4, statedRequirement: true },
    8,
    issue242Zero,
    issue242Zero,
    issue242Zero
);
assert.strictEqual(issue242Delta.selected.min, 4, '8 required and 4 live missing produces Selected 4');
assert.strictEqual(issue242Delta.selected.max, 4, 'selected committed delta remains exact');
assert.strictEqual(issue242Delta.onSite.min, 0, 'selected committed delta is not falsely shown On site');
assert.strictEqual(issue242Delta.responding.min, 0, 'selected committed delta is not falsely shown Responding');

issue242Delta = api.reconcileCommittedDelta(
    { missing: 4, statedRequirement: true },
    8,
    issue242Zero,
    issue242Zero,
    api.capacity(4, 4, true)
);
assert.strictEqual(issue242Delta.onSite.min, 4, 'real on-site capacity remains On site');
assert.strictEqual(issue242Delta.selected.min, 0, 'real on-site capacity is subtracted before selected inference');

issue242Delta = api.reconcileCommittedDelta(
    { missing: 4, statedRequirement: true },
    8,
    issue242Zero,
    api.capacity(2, 2, true),
    issue242Zero
);
assert.strictEqual(issue242Delta.responding.min, 2, 'real responding capacity remains Responding');
assert.strictEqual(issue242Delta.selected.min, 2, 'remaining committed delta becomes Selected');

issue242Delta = api.reconcileCommittedDelta(
    { missing: 8, statedRequirement: true },
    8,
    issue242Zero,
    issue242Zero,
    issue242Zero
);
assert.strictEqual(issue242Delta.selected.min, 0, 'restored live demand removes inferred Selected after deselection');
'''
runtime = replace_once(runtime, anchor, anchor + tests, "Issue 242 regression fixtures")
RUNTIME.write_text(runtime, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
section = """## [4.20.10] - 2026-07-20

### Fixed
- Corrected Railway Police Officer state reconciliation when MissionChief's live missing count changes after personnel are selected.
- The difference between the authoritative Mission Info baseline and current live missing demand is no longer falsely displayed as On-site capacity.
- Actual On-site and Responding capacity is retained first; any remaining committed capacity is displayed as Selected.

### Validation
- Added deterministic fixtures for the reported `8 required / 4 live missing / 0 on scene` case, real On-site and Responding precedence, and deselection restoration.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + section, "v4.20.10 changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
if "4.20.9" not in help_text:
    raise AssertionError("Help Centre v4.20.9 marker not found")
HELP.write_text(help_text.replace("4.20.9", "4.20.10"), encoding="utf-8")

DOC.write_text("""# Issue #242 — Railway Police selected-capacity contract

MissionChief's live missing total can change when personnel are selected. The difference between the authoritative Mission Info baseline and the current live missing value is committed capacity; it is not proof that personnel are already on scene.

The Matrix reconciles that committed delta in this order:

1. retain capacity proven by canonical Vehicles on Scene rows;
2. retain capacity proven by canonical Units Responding rows;
3. attribute the remaining committed delta to Selected.

For the reported case—eight Railway Police Officers required, four still missing, no responding units and no units on scene—the Matrix must show Selected 4, On site 0 and Still needed 4.
""", encoding="utf-8")

for filename in [
    "fix-railway-police-capacity-v4.20.10.py",
    "fix-railway-police-capacity-v4.20.10-retry.py",
    "diagnose-railway-police-transform.py",
    "diagnose-railway-police-core-anchors.py",
    "diagnose-railway-police-metadata-anchors.py",
    "diagnose-railway-police-resolver-anchors.py",
]:
    (ROOT / ".github" / "development-packages" / filename).unlink(missing_ok=True)

subprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_mission_requirements_contract.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/check_documentation_drift.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_documentation_version_states.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Railway Police selected-delta v4.20.10 hotfix validated")
