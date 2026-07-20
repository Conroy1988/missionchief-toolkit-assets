#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
DOC = ROOT / "docs" / "issue-242-railway-police-selected-state-contract.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.9", "// @version      4.20.10", "metadata version")
source = replace_once(source, "version: '4.20.9',", "version: '4.20.10',", "runtime version")
source = replace_once(source, "guideVersion: '4.20.9',", "guideVersion: '4.20.10',", "guide version")

resolver = source.find("function missionRequirementsResolve(candidate, parsed, catalogue = null)")
resolver_end = source.find("function missionRequirementsOverallState(rows, unresolved)", resolver)
start = source.find("if (baseline !== null && hasStatedRequirement)", resolver, resolver_end)
end = source.find("const fixedMinimum", start, resolver_end)
if resolver < 0 or resolver_end < 0 or start < 0 or end < 0:
    raise AssertionError(f"resolver bounds missing: resolver={resolver}, resolver_end={resolver_end}, start={start}, end={end}")
legacy = source[start:end]
if "inferredOnSite" not in legacy or "statedRequiredMin" not in legacy or "statedRequiredMax" not in legacy:
    raise AssertionError("scoped resolver segment does not contain the expected legacy state reconstruction")
replacement = """if (baseline !== null && hasStatedRequirement) { const committed = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0)); const operationalMin = onSite.min + responding.min; const operationalMax = onSite.max === null || responding.max === null ? null : onSite.max + responding.max; const inferredSelectedMin = operationalMax === null ? 0 : Math.max(0, committed - operationalMax); const inferredSelectedMax = Math.max(0, committed - operationalMin); if (inferredSelectedMax > selected.min) { const selectedMin = Math.max(selected.min, inferredSelectedMin); const selectedMax = selected.max === null ? inferredSelectedMax : Math.max(selected.max, inferredSelectedMax); selected = missionRequirementsCapacity(selectedMin, selectedMax, selectedMax !== null && selectedMin === selectedMax && onSite.known && responding.known); } } const statedRequiredMin = hasStatedRequirement ? Math.max(0, Number(requirement.missing) || 0) + onSite.min : 0; const statedRequiredMax = hasStatedRequirement ? (onSite.max === null ? null : Math.max(0, Number(requirement.missing) || 0) + onSite.max) : 0; """
source = source[:start] + replacement + source[end:]
if "const inferredOnSite =" in source[resolver:resolver_end]:
    raise AssertionError("legacy inferred-On-site resolver assignment remains")
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.9'", "version: '4.20.10'", "runtime fixture version")
anchor = "assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');\n"
tests = r'''

// Issue #242: MissionChief's live missing total already reflects selected personnel.
{
const issue242Doc = new FakeDocument();
issue242Doc.defaultView = { MutationObserver: FakeMutationObserver };
const issue242Candidate = makeMissionCandidate(issue242Doc, '4 Railway Police Officers');
const issue242Definition = api.definitions.find(item => item.key === 'railway-police-officer');
const issue242Catalogue = { requirements: [{ key: 'railway-police-officer', baseline: 8, missing: 8 }] };
let issue242Rows = api.resolve(issue242Candidate, {
    requirements: [{ key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 4, group: 'staff', definition: issue242Definition, statedRequirement: true }],
    unresolved: []
}, issue242Catalogue);
let issue242Row = issue242Rows.find(item => item.key === 'railway-police-officer');
assert.strictEqual(issue242Row.requiredText, '8', 'authoritative Railway Police requirement remains eight');
assert.strictEqual(issue242Row.onSiteMin, 0, 'committed selected personnel are not falsely reported On site');
assert.strictEqual(issue242Row.respondingMin, 0, 'committed selected personnel are not falsely reported Responding');
assert.strictEqual(issue242Row.selectedMin, 4, 'baseline eight minus live missing four is reported Selected four');
assert.strictEqual(issue242Row.stillNeededText, '4', 'four Railway Police Officers remain needed');

issue242Rows = api.resolve(issue242Candidate, {
    requirements: [{ key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 8, group: 'staff', definition: issue242Definition, statedRequirement: true }],
    unresolved: []
}, issue242Catalogue);
issue242Row = issue242Rows.find(item => item.key === 'railway-police-officer');
assert.strictEqual(issue242Row.selectedMin, 0, 'restored live missing demand removes inferred Selected after deselection');
assert.strictEqual(issue242Row.onSiteMin, 0, 'deselection does not create false On-site personnel');
}
'''
runtime = replace_once(runtime, anchor, anchor + tests, "Issue 242 resolver regressions")
RUNTIME.write_text(runtime, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
section = """## [4.20.10] - 2026-07-20

### Fixed
- Corrected Railway Police Officer state reconciliation when MissionChief reduces the live missing count after personnel are selected.
- The difference between the Mission Info baseline and live missing demand is no longer falsely displayed as On-site capacity.
- Proven On-site and Responding capacity is retained first; any remaining committed capacity is displayed as Selected.

### Validation
- Added a deterministic regression for the reported `8 required / 4 live missing / no units on scene` case and deselection restoration.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + section, "v4.20.10 changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
if "4.20.9" not in help_text:
    raise AssertionError("Help Centre v4.20.9 marker missing")
HELP.write_text(help_text.replace("4.20.9", "4.20.10"), encoding="utf-8")

DOC.write_text("""# Issue #242 — Railway Police selected-state contract

MissionChief's live missing total can already reflect selected trained personnel. The difference between the authoritative Mission Info baseline and current live missing demand is committed capacity; it is not evidence that those personnel are on scene.

The Matrix keeps capacity proven by canonical Vehicles on Scene and Units Responding rows in their respective columns. Any remaining committed delta is displayed as Selected.

For eight Railway Police Officers required, four still missing and no operational units present, the Matrix must show On site 0, Responding 0, Selected 4 and Still needed 4.
""", encoding="utf-8")

(ROOT / ".github" / "development-packages" / "fix-issue-242-inline-v4.20.10.py").unlink(missing_ok=True)
print("Issue 242 scoped inline v4.20.10 package applied")
