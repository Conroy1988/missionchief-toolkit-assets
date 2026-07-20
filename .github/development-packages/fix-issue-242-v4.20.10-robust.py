#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
DOC = ROOT / "docs" / "issue-242-railway-police-selected-delta-contract.md"

source = SOURCE.read_text(encoding="utf-8")
if "4.20.9" not in source:
    raise AssertionError("Toolkit 4.20.9 source marker missing")
source = source.replace("4.20.9", "4.20.10")

resolve_marker = "function missionRequirementsResolve(candidate, parsed, catalogue = null)"
resolve_at = source.find(resolve_marker)
if resolve_at < 0:
    match = re.search(r"function\s+missionRequirementsResolve\s*\(candidate,\s*parsed,\s*catalogue\s*=\s*null\)", source)
    if not match:
        raise AssertionError("missionRequirementsResolve marker missing")
    resolve_at = match.start()
    resolve_marker = match.group(0)

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
source = source[:resolve_at] + helper + source[resolve_at:]

baseline_start = source.find("if (baseline !== null && hasStatedRequirement)", resolve_at + len(helper))
fixed_minimum = source.find("const fixedMinimum", baseline_start)
if baseline_start < 0 or fixed_minimum < 0:
    raise AssertionError(f"resolver baseline bounds missing: start={baseline_start}, end={fixed_minimum}")
legacy = source[baseline_start:fixed_minimum]
if "inferredOnSite" not in legacy or "missionRequirementsCapacity" not in legacy:
    raise AssertionError("bounded resolver segment is not the legacy inferred-On-site block")
replacement = "if (baseline !== null && hasStatedRequirement) { ({ selected, responding, onSite } = missionRequirementsReconcileCommittedDelta(requirement, baseline, selected, responding, onSite)); } "
source = source[:baseline_start] + replacement + source[fixed_minimum:]
if "const inferredOnSite =" in source:
    raise AssertionError("legacy inferred-On-site assignment remains")
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8").replace("4.20.9", "4.20.10")
if "reconcileCommittedDelta: missionRequirementsReconcileCommittedDelta" not in runtime:
    runtime, export_count = re.subn(
        r"(\n\s*resolve:\s*missionRequirementsResolve,\s*)",
        r"\1\n    reconcileCommittedDelta: missionRequirementsReconcileCommittedDelta,",
        runtime,
        count=1,
    )
    if export_count != 1:
        raise AssertionError(f"runtime resolve export count: {export_count}")

tests = r'''

// Issue #242: live missing demand can already include selected trained personnel.
const issue242Zero = api.capacity(0, 0, true);
let issue242Delta = api.reconcileCommittedDelta({ missing: 4, statedRequirement: true }, 8, issue242Zero, issue242Zero, issue242Zero);
assert.strictEqual(issue242Delta.selected.min, 4, '8 required and 4 live missing produces Selected 4');
assert.strictEqual(issue242Delta.selected.max, 4, 'selected committed delta remains exact');
assert.strictEqual(issue242Delta.onSite.min, 0, 'selected committed delta is not falsely shown On site');
assert.strictEqual(issue242Delta.responding.min, 0, 'selected committed delta is not falsely shown Responding');

issue242Delta = api.reconcileCommittedDelta({ missing: 4, statedRequirement: true }, 8, issue242Zero, issue242Zero, api.capacity(4, 4, true));
assert.strictEqual(issue242Delta.onSite.min, 4, 'real on-site capacity remains On site');
assert.strictEqual(issue242Delta.selected.min, 0, 'real on-site capacity is subtracted before selected inference');

issue242Delta = api.reconcileCommittedDelta({ missing: 4, statedRequirement: true }, 8, issue242Zero, api.capacity(2, 2, true), issue242Zero);
assert.strictEqual(issue242Delta.responding.min, 2, 'real responding capacity remains Responding');
assert.strictEqual(issue242Delta.selected.min, 2, 'remaining committed delta becomes Selected');

issue242Delta = api.reconcileCommittedDelta({ missing: 8, statedRequirement: true }, 8, issue242Zero, issue242Zero, issue242Zero);
assert.strictEqual(issue242Delta.selected.min, 0, 'restored live demand removes inferred Selected after deselection');
'''
if "8 required and 4 live missing produces Selected 4" not in runtime:
    anchor = "assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');\n"
    if anchor in runtime:
        runtime = runtime.replace(anchor, anchor + tests, 1)
    else:
        runtime += tests
RUNTIME.write_text(runtime, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
if "## [4.20.10]" not in changelog:
    section = """## [4.20.10] - 2026-07-20

### Fixed
- Corrected Railway Police Officer state reconciliation when MissionChief's live missing count changes after personnel are selected.
- The difference between the authoritative Mission Info baseline and current live missing demand is no longer falsely displayed as On-site capacity.
- Actual On-site and Responding capacity is retained first; any remaining committed capacity is displayed as Selected.

### Validation
- Added deterministic fixtures for the reported `8 required / 4 live missing / 0 on scene` case, real On-site and Responding precedence, and deselection restoration.

"""
    marker = "## [Unreleased]\n\n"
    if marker not in changelog:
        raise AssertionError("Unreleased changelog marker missing")
    changelog = changelog.replace(marker, marker + section, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
if "4.20.9" in help_text:
    help_text = help_text.replace("4.20.9", "4.20.10")
elif "4.20.10" not in help_text:
    raise AssertionError("Help Centre version marker missing")
HELP.write_text(help_text, encoding="utf-8")

DOC.write_text("""# Issue #242 — Railway Police selected-capacity contract

MissionChief's live missing total can change when personnel are selected. The difference between the authoritative Mission Info baseline and current live missing demand is committed capacity; it is not proof that personnel are already on scene.

The Matrix reconciles that delta in this order:

1. retain capacity proven by canonical Vehicles on Scene rows;
2. retain capacity proven by canonical Units Responding rows;
3. attribute the remaining committed capacity to Selected.

For the reported case—eight Railway Police Officers required, four still missing, no responding units and no units on scene—the Matrix must show Selected 4, On site 0 and Still needed 4.
""", encoding="utf-8")

for filename in ["fix-issue-242-v4.20.10.py"]:
    (ROOT / ".github" / "development-packages" / filename).unlink(missing_ok=True)

print("Issue 242 robust v4.20.10 package applied")
