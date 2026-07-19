#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DIST_FILES = [
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
]
DIAGNOSTIC = ROOT / "status" / "railway-police-selected-diagnostic.txt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, replacement: str) -> str:
    marker = f"function {name}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"{marker} not found")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"{marker} opening brace not found")
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"', '`'):
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[index + 1:]
    raise AssertionError(f"{marker} closing brace not found")


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.6", "// @version      4.20.7", "metadata version")
source = replace_once(source, "version: '4.20.6'", "version: '4.20.7'", "runtime version")

new_staff_capacity = r'''function missionRequirementsStaffCapacity(element) {
        const row = element?.closest?.('tr') || element;
        const semanticSelectors = [
            '[data-personnel-count]',
            '[data-current-personnel]',
            '[data-min-personnel]',
            '[data-max-personnel]',
            '[data-min-crew]',
            '[data-max-crew]',
            '[data-column="crew"]',
            '[data-column="personnel"]',
            '[data-column="staff"]'
        ];
        let crewCell = null;
        for (const selector of semanticSelectors) {
            crewCell = row?.querySelector?.(selector) || null;
            if (crewCell) break;
        }
        const scopes = Array.from(new Set([element, row, crewCell].filter(Boolean)));
        const exactAttributes = ['data-personnel-count', 'data-current-personnel', 'data-personnel', 'data-staff', 'data-crew'];
        for (const scope of scopes) {
            for (const attribute of exactAttributes) {
                const value = missionRequirementsOptionalNumber(scope.getAttribute?.(attribute));
                if (value !== null) return missionRequirementsCapacity(value, value, true);
            }
        }
        let min = null;
        let max = null;
        for (const scope of scopes) {
            if (min === null) min = missionRequirementsOptionalNumber(scope.getAttribute?.('data-min-personnel') ?? scope.getAttribute?.('data-min-crew'));
            if (max === null) max = missionRequirementsOptionalNumber(scope.getAttribute?.('data-max-personnel') ?? scope.getAttribute?.('data-max-crew'));
        }
        if (min !== null || max !== null) return missionRequirementsCapacity(min ?? 0, max, min !== null && max !== null && min === max);
        const parseCrewText = cell => {
            const text = String(cell?.textContent || '').trim();
            const currentMaximum = text.match(/(\d[\d,.]*)\s*\/\s*(\d[\d,.]*)/u);
            if (currentMaximum) {
                const current = missionRequirementsNumber(currentMaximum[1]);
                return missionRequirementsCapacity(current, current, true);
            }
            const bounded = text.match(/(\d[\d,.]*)\s*(?:-|–|to)\s*(\d[\d,.]*)/iu);
            if (bounded) return missionRequirementsCapacity(missionRequirementsNumber(bounded[1]), missionRequirementsNumber(bounded[2]), false);
            return null;
        };
        const semanticTextCapacity = parseCrewText(crewCell);
        if (semanticTextCapacity) return semanticTextCapacity;
        for (const cell of Array.from(row?.querySelectorAll?.('td, th') || [])) {
            const capacity = parseCrewText(cell);
            if (capacity) return capacity;
        }
        if (crewCell) {
            const visible = missionRequirementsOptionalNumber(String(crewCell.textContent || '').trim());
            if (visible !== null) return missionRequirementsCapacity(visible, visible, true);
            const sortValue = missionRequirementsOptionalNumber(crewCell.getAttribute?.('sortvalue'));
            if (sortValue !== null) return missionRequirementsCapacity(sortValue, sortValue, true);
        }
        return null;
    }'''
source = replace_function(source, "missionRequirementsStaffCapacity", new_staff_capacity)
SOURCE.write_text(source, encoding="utf-8")
for distribution in DIST_FILES:
    distribution.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.6'", "version: '4.20.7'", "runtime fixture version")
regression_tests = r'''
const railwayRegressionAmbiguousCell = {
    textContent: '239',
    getAttribute(name) { return name === 'sortvalue' ? '239' : null; }
};
const railwayRegressionCrewCell = {
    textContent: '1 / 1',
    getAttribute(name) { return name === 'data-current-personnel' ? '1' : null; }
};
const railwayRegressionRow = {
    getAttribute() { return null; },
    querySelector(selector) {
        if (selector === '[data-current-personnel]') return railwayRegressionCrewCell;
        if (selector === 'td:nth-of-type(4)' || selector === 'td:nth-of-type(5)[sortvalue]') return railwayRegressionAmbiguousCell;
        return null;
    },
    querySelectorAll() { return [railwayRegressionAmbiguousCell, railwayRegressionCrewCell]; }
};
const railwayRegressionCheckbox = {
    getAttribute() { return null; },
    closest(selector) { return selector === 'tr' ? railwayRegressionRow : null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.staffCapacity(railwayRegressionCheckbox))),
    { min: 1, max: 1, known: true, value: 1 },
    'Railway Police semantic crew count wins over unrelated sortvalue 239'
);
const railwayRegressionUnlabelledRow = {
    getAttribute() { return null; },
    querySelector() { return null; },
    querySelectorAll() { return [railwayRegressionAmbiguousCell]; }
};
const railwayRegressionUnlabelledCheckbox = {
    getAttribute() { return null; },
    closest(selector) { return selector === 'tr' ? railwayRegressionUnlabelledRow : null; }
};
assert.strictEqual(
    api.staffCapacity(railwayRegressionUnlabelledCheckbox),
    null,
    'unlabelled numeric table metadata must not become personnel capacity'
);
const railwayPoliceDefinition = api.definitions.find(item => item.key === 'railway-police-officer');
const railwaySelectedUnit = {
    typeId: -1,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(['railway police officer']),
    knownDefinitionKeys: new Set(['railway-police-officer']),
    staff: api.staffCapacity(railwayRegressionCheckbox),
    contributionKey: 'vehicle:239'
};
const railwaySelectedCapacity = api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [railwaySelectedUnit]);
assert.strictEqual(railwaySelectedCapacity.min, 1, 'one selected Railway Police Officer contributes one');
assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');

'''
runtime = replace_once(runtime, "const issue191AmbulanceDefinition = api.definitions.find(item => item.key === 'ambulance');\n", regression_tests + "const issue191AmbulanceDefinition = api.definitions.find(item => item.key === 'ambulance');\n", "Railway Police regression fixtures")
RUNTIME.write_text(runtime, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.20.7] - 2026-07-19

### Fixed
- Fixed Railway Police selected personnel showing inflated values such as `239+` when an unrelated table-cell sort value was mistaken for crew capacity.
- Personnel capacity now uses semantically labelled crew metadata or explicit current/maximum crew text; unlabelled positional numeric cells are ignored.

### Validation
- Added deterministic regression coverage proving one selected Railway Police Officer contributes exactly one and an unlabelled `sortvalue=239` contributes nothing.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog release entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

if DIAGNOSTIC.exists():
    DIAGNOSTIC.unlink()

subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", str(DIST_FILES[0].relative_to(ROOT)), str(DIST_FILES[1].relative_to(ROOT))], cwd=ROOT, check=True)
print("Railway Police selected-capacity hotfix validated")
