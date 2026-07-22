#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CANONICAL = (
    SOURCE,
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
)
FIXTURE = ROOT / ".github" / "fixtures" / "issue-378-enhanced-requirements-cases.json"
TEST = ROOT / ".github" / "scripts" / "test_issue378_requirements_engine.js"
SHELL_TEST = ROOT / ".github" / "scripts" / "test_issue378_operational_suite_shell.py"
HEADROOM_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"

source = SOURCE.read_text(encoding="utf-8")
base_lines = len(source.splitlines())

anchor = "    // Issue #378 LSSM operational-suite lifecycle shell.\n"
if source.count(anchor) != 1:
    raise RuntimeError(f"Issue #378 engine anchor changed: {source.count(anchor)}")

engine = r'''    // Issue #378 enhanced requirements pure engine.
    // This block is intentionally DOM-free. Phase 3 validates the data model before any
    // renderer or observer can replace the stable Matrix runtime.
    const OPERATIONAL_REQUIREMENT_GROUPS = Object.freeze(['vehicles', 'staff', 'other']);

    function operationalRequirementEscapeRegex(value) {
        return String(value ?? '').replace(/[.*+?^${}()|[\]\\]/gu, '\\$&');
    }

    function operationalRequirementNormaliseText(value) {
        return String(value ?? '')
            .replace(/[\u00a0\s]+/gu, ' ')
            .replace(/\s+([,.:])/gu, '$1')
            .trim();
    }

    function operationalRequirementNumber(value, fallback = 0) {
        const normalised = String(value ?? '').replace(/[^0-9-]/gu, '');
        const parsed = Number.parseInt(normalised, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function operationalRequirementCloneRange(value) {
        return {
            min: Math.max(0, Number(value?.min) || 0),
            max: Math.max(0, Number(value?.max) || 0)
        };
    }

    function operationalRequirementDefinitionList(value) {
        return Array.isArray(value) ? value.filter(item => item && typeof item === 'object') : [];
    }

    function operationalRequirementMatcher(texts) {
        const labels = (Array.isArray(texts) ? texts : [texts])
            .map(operationalRequirementNormaliseText)
            .filter(Boolean)
            .sort((left, right) => right.length - left.length)
            .map(operationalRequirementEscapeRegex);
        if (!labels.length) return null;
        const number = '\\d{1,3}(?:[,.\\s]?\\d{3})*x?';
        return new RegExp(`((?:${number}\\s+(?:${labels.join('|')}))|(?:(?:${labels.join('|')}):\\s*${number}))(?=[,.]|$)`, 'iu');
    }

    function operationalRequirementSplitMatch(value) {
        const match = operationalRequirementNormaliseText(value);
        const colon = /:\s*[0-9][0-9,.\s]*x?$/u.test(match);
        const amountText = match.match(colon ? /[0-9][0-9,.\s]*x?$/u : /^[0-9][0-9,.\s]*x?/u)?.[0] ?? '0';
        return {
            requirement: match
                .replace(colon ? /:\s*[0-9][0-9,.\s]*x?$/u : /^[0-9][0-9,.\s]*x?/u, '')
                .trim(),
            missing: Math.max(0, operationalRequirementNumber(amountText, 0))
        };
    }

    function operationalRequirementCleanRemaining(value) {
        return operationalRequirementNormaliseText(value)
            .replace(/,\s*(?=,|$)/gmu, '')
            .replace(/^,\s*/gmu, '')
            .replace(/\s+,/gmu, ',')
            .trim();
    }

    function operationalRequirementIndexAdd(index, type, group, requirementIndex) {
        const key = String(type);
        index[key] ??= {};
        index[key][group] ??= [];
        if (!index[key][group].includes(requirementIndex)) index[key][group].push(requirementIndex);
    }

    function operationalRequirementFactor(requirement, type, fallback = 1) {
        const factor = requirement?.additional?.factors?.[String(type)];
        return Number.isFinite(Number(factor)) ? Number(factor) : fallback;
    }

    function operationalRequirementCreateModel(input = {}) {
        const catalog = input.catalog && typeof input.catalog === 'object' ? input.catalog : {};
        const missionAdditional = input.missionAdditional && typeof input.missionAdditional === 'object'
            ? input.missionAdditional
            : {};
        const requirements = { vehicles: [], staff: [], other: [] };
        const requirementTexts = { vehicles: null, staff: null, other: null };
        const requirementsForVehicle = {};
        const requirementsForEquipment = {};

        for (const group of OPERATIONAL_REQUIREMENT_GROUPS) {
            const supplied = input.texts?.[group];
            if (supplied === undefined || supplied === null) continue;
            const raw = operationalRequirementNormaliseText(
                typeof supplied === 'object' && !Array.isArray(supplied) ? supplied.raw : supplied
            );
            const infoText = operationalRequirementNormaliseText(
                typeof supplied === 'object' && !Array.isArray(supplied) ? supplied.infoText : ''
            );
            requirementTexts[group] = { infoText, raw, remaining: raw };
        }

        for (const bar of ['water', 'foam', 'pump']) {
            const progress = input.progress?.[bar];
            const textGroup = requirementTexts.other;
            if (!progress || !textGroup) continue;
            const matcher = operationalRequirementMatcher(progress.texts ?? progress.requirement ?? bar);
            const match = matcher?.exec(textGroup.remaining)?.[0];
            if (!match) continue;
            textGroup.remaining = textGroup.remaining.replace(match, '');
            const driving = Math.max(0, Number(progress.driving) || 0);
            requirements.other.push({
                key: `progress:${bar}`,
                requirement: operationalRequirementSplitMatch(match).requirement,
                missing: Math.max(0, Number(progress.missing) || 0) + driving,
                driving,
                selected: Math.max(0, Number(progress.selected) || 0),
                bar
            });
        }

        for (const group of OPERATIONAL_REQUIREMENT_GROUPS) {
            const textGroup = requirementTexts[group];
            if (!textGroup) continue;
            const preprocessors = Array.isArray(input.preprocessors?.[group]) ? input.preprocessors[group] : [];
            for (const processor of preprocessors) {
                if (!processor || typeof processor.pattern !== 'string') continue;
                try {
                    textGroup.remaining = textGroup.remaining.replace(
                        new RegExp(processor.pattern, processor.flags || 'gu'),
                        String(processor.replace ?? '')
                    );
                } catch (error) {
                    // Invalid optional locale preprocessors are ignored without corrupting raw text.
                }
            }

            for (const [definitionIndex, definition] of operationalRequirementDefinitionList(catalog[group]).entries()) {
                const matcher = operationalRequirementMatcher(definition.texts);
                const match = matcher?.exec(textGroup.remaining)?.[0];
                if (!match) continue;
                textGroup.remaining = textGroup.remaining.replace(match, '');
                const parsed = operationalRequirementSplitMatch(match);
                const requirementIndex = requirements[group].length;
                const vehicles = new Set(
                    operationalRequirementDefinitionList([])
                );
                for (const vehicle of Array.isArray(definition.vehicles) ? definition.vehicles : []) {
                    if (Number.isFinite(Number(vehicle))) vehicles.add(Number(vehicle));
                }
                for (const [condition, conditional] of Object.entries(definition.conditionalVehicles ?? {})) {
                    if (!missionAdditional[condition]) continue;
                    for (const vehicle of Array.isArray(conditional) ? conditional : []) {
                        if (Number.isFinite(Number(vehicle))) vehicles.add(Number(vehicle));
                    }
                }
                for (const vehicle of vehicles) {
                    operationalRequirementIndexAdd(requirementsForVehicle, vehicle, group, requirementIndex);
                }
                for (const equipment of Array.isArray(definition.equipment) ? definition.equipment : []) {
                    if (String(equipment).trim()) {
                        operationalRequirementIndexAdd(requirementsForEquipment, String(equipment), group, requirementIndex);
                    }
                }
                requirements[group].push({
                    key: String(definition.key ?? `${group}:${definitionIndex}`),
                    requirement: parsed.requirement,
                    missing: parsed.missing,
                    driving: 0,
                    selected: group === 'staff' ? { min: 0, max: 0 } : 0,
                    additional: {
                        texts: Array.isArray(definition.texts) ? definition.texts.slice() : [String(definition.texts ?? '')],
                        vehicles: Array.from(vehicles),
                        equipment: Array.isArray(definition.equipment) ? definition.equipment.slice() : [],
                        conditionalVehicles: { ...(definition.conditionalVehicles ?? {}) },
                        factors: { ...(definition.factors ?? {}) }
                    }
                });
            }
            textGroup.remaining = operationalRequirementCleanRemaining(textGroup.remaining);
        }

        const addDriving = (type, group, amount, isEquipment = false) => {
            const index = isEquipment ? requirementsForEquipment : requirementsForVehicle;
            for (const requirementIndex of index[String(type)]?.[group] ?? []) {
                const requirement = requirements[group][requirementIndex];
                requirement.driving += operationalRequirementFactor(requirement, type, amount);
            }
        };

        for (const vehicle of Array.isArray(input.driving) ? input.driving : []) {
            const vehicleType = Number(vehicle?.vehicleType);
            if (Number.isFinite(vehicleType) && vehicleType >= 0) {
                addDriving(vehicleType, 'vehicles', 1);
                addDriving(vehicleType, 'other', 1);
                const staff = Math.max(0, Number(vehicle?.staff) || 0);
                if (staff > 0) addDriving(vehicleType, 'staff', staff);
            }
            for (const equipment of Array.isArray(vehicle?.equipment) ? vehicle.equipment : []) {
                for (const group of OPERATIONAL_REQUIREMENT_GROUPS) addDriving(String(equipment), group, 1, true);
            }
        }

        const selected = {
            vehicles: new Array(requirements.vehicles.length).fill(0),
            staff: new Array(requirements.staff.length).fill(0).map(() => ({ min: 0, max: 0 })),
            other: new Array(requirements.other.length).fill(0)
        };
        const selectedVehicles = Array.isArray(input.selected) ? input.selected : [];
        const selectedIds = new Set(selectedVehicles.map(vehicle => Number(vehicle?.id)).filter(Number.isFinite));

        const increaseSelected = (type, group, amount = 1, range = null, isEquipment = false) => {
            const index = isEquipment ? requirementsForEquipment : requirementsForVehicle;
            for (const requirementIndex of index[String(type)]?.[group] ?? []) {
                if (group === 'staff') {
                    const staff = operationalRequirementCloneRange(range);
                    selected.staff[requirementIndex].min += staff.min;
                    selected.staff[requirementIndex].max += staff.max;
                } else {
                    selected[group][requirementIndex] += operationalRequirementFactor(
                        requirements[group][requirementIndex],
                        type,
                        amount
                    );
                }
            }
        };

        const vehicleTypes = input.vehicleTypes && typeof input.vehicleTypes === 'object' ? input.vehicleTypes : {};
        const requirementsByRandomTractive = {};
        for (const [trailerType, metadata] of Object.entries(vehicleTypes)) {
            const tractives = Array.isArray(metadata?.tractiveVehicles)
                ? metadata.tractiveVehicles.map(Number).filter(Number.isFinite)
                : [];
            if (!tractives.length) continue;
            requirementsByRandomTractive[trailerType] = {};
            for (const group of OPERATIONAL_REQUIREMENT_GROUPS) {
                let intersection = null;
                for (const tractiveType of tractives) {
                    const values = new Set(requirementsForVehicle[String(tractiveType)]?.[group] ?? []);
                    intersection = intersection === null
                        ? values
                        : new Set(Array.from(intersection).filter(value => values.has(value)));
                }
                requirementsByRandomTractive[trailerType][group] = Array.from(intersection ?? []);
            }
        }

        const randomTractiveCounts = {};
        for (const vehicle of selectedVehicles) {
            const vehicleType = Number(vehicle?.vehicleType);
            if (!Number.isFinite(vehicleType) || vehicleType < 0) continue;
            const staff = operationalRequirementCloneRange(vehicle?.staff);
            increaseSelected(vehicleType, 'vehicles', 1);
            increaseSelected(vehicleType, 'other', 1);
            increaseSelected(vehicleType, 'staff', 1, staff);
            for (const equipment of Array.isArray(vehicle?.equipment) ? vehicle.equipment : []) {
                for (const group of OPERATIONAL_REQUIREMENT_GROUPS) {
                    increaseSelected(String(equipment), group, 1, null, true);
                }
            }

            const tractiveId = Number(vehicle?.tractiveVehicleId);
            const tractiveType = Number(vehicle?.tractiveVehicleType);
            const explicitTractive = vehicle?.tractiveRandom === false || vehicle?.tractiveRandom === 0 || vehicle?.tractiveRandom === '0';
            if (explicitTractive && Number.isFinite(tractiveType) && !selectedIds.has(tractiveId)) {
                const tractiveStaff = operationalRequirementCloneRange(vehicle?.tractiveStaff);
                increaseSelected(tractiveType, 'vehicles', 1);
                increaseSelected(tractiveType, 'other', 1);
                increaseSelected(tractiveType, 'staff', 1, tractiveStaff);
            } else if (vehicleTypes[String(vehicleType)]?.tractiveVehicles) {
                randomTractiveCounts[String(vehicleType)] = (randomTractiveCounts[String(vehicleType)] ?? 0) + 1;
            }
        }

        for (const [trailerType, amount] of Object.entries(randomTractiveCounts)) {
            for (const group of ['vehicles', 'other']) {
                for (const requirementIndex of requirementsByRandomTractive[trailerType]?.[group] ?? []) {
                    selected[group][requirementIndex] += Number(amount) || 0;
                }
            }
        }

        for (const group of OPERATIONAL_REQUIREMENT_GROUPS) {
            requirements[group].forEach((requirement, index) => {
                if (requirement.bar) {
                    const progress = input.progress?.[requirement.bar];
                    requirement.selected = Math.max(0, Number(progress?.selected) || 0);
                } else {
                    requirement.selected = group === 'staff'
                        ? operationalRequirementCloneRange(selected.staff[index])
                        : Math.max(0, Number(selected[group][index]) || 0);
                }
            });
        }

        return {
            requirements,
            requirementTexts,
            requirementsForVehicle,
            requirementsForEquipment
        };
    }

    function operationalRequirementRows(model, options = {}) {
        const calcMaxStaff = options.calcMaxStaff === true;
        const rows = [];
        for (const group of OPERATIONAL_REQUIREMENT_GROUPS) {
            for (const requirement of model?.requirements?.[group] ?? []) {
                const selectedValue = typeof requirement.selected === 'number'
                    ? requirement.selected
                    : calcMaxStaff
                      ? requirement.selected.max
                      : requirement.selected.min;
                const remainingOnMission = requirement.missing - requirement.driving;
                rows.push({
                    ...requirement,
                    group,
                    remainingOnMission,
                    selectedValue,
                    covered: remainingOnMission <= selectedValue
                });
            }
        }
        return rows;
    }

    function operationalRequirementFingerprint(model, options = {}) {
        return JSON.stringify({
            rows: operationalRequirementRows(model, options),
            remaining: OPERATIONAL_REQUIREMENT_GROUPS.map(group => model?.requirementTexts?.[group]?.remaining ?? null)
        });
    }
    // Issue #378 end enhanced requirements pure engine.

'''

source = source.replace(anchor, engine + anchor, 1)
new_lines = len(source.splitlines())
delta = new_lines - base_lines
if delta <= 0:
    raise RuntimeError(f"Issue #378 engine did not add a positive source delta: {delta}")

for path in CANONICAL:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

fixture = {
    "schemaVersion": 1,
    "upstreamCommit": "88e41646e59a7d620624f90f1d9a0a62320c2775",
    "catalog": {
        "vehicles": [
            {"key": "fire-engine", "texts": ["Fire engine", "Fire engines"], "vehicles": [0, 1, 16], "factors": {"16": 2}},
            {"key": "drone", "texts": ["Drone", "Drones"], "vehicles": [89], "equipment": ["drone"]},
            {"key": "boat", "texts": ["Rescue Boat", "Rescue Boats"], "vehicles": [67], "conditionalVehicles": {"allowPoweredBoat": [68]}},
            {"key": "tractive", "texts": ["Towing Unit", "Towing Units"], "vehicles": [57, 58]}
        ],
        "staff": [
            {"key": "firefighters", "texts": ["more firefighter", "more firefighters"], "vehicles": [0, 1, 16]}
        ],
        "other": []
    },
    "vehicleTypes": {"70": {"tractiveVehicles": [57, 58]}},
    "cases": [
        {
            "name": "x-prefix and unresolved text",
            "input": {"texts": {"vehicles": "2x Fire engines, 1x Mystery Unit"}},
            "expect": {"rows": [{"key": "fire-engine", "missing": 2, "driving": 0, "selectedValue": 0, "covered": False}], "remaining": {"vehicles": "1x Mystery Unit"}}
        },
        {
            "name": "colon requirement syntax",
            "input": {"texts": {"vehicles": "Fire engines: 3"}},
            "expect": {"rows": [{"key": "fire-engine", "missing": 3}]}
        },
        {
            "name": "vehicle factors apply to driving and selected",
            "input": {
                "texts": {"vehicles": "3x Fire engines"},
                "driving": [{"vehicleType": 16}],
                "selected": [{"id": 100, "vehicleType": 0}]
            },
            "expect": {"rows": [{"key": "fire-engine", "driving": 2, "selectedValue": 1, "covered": True}]}
        },
        {
            "name": "equipment contributes independently",
            "input": {
                "texts": {"vehicles": "2x Drones"},
                "driving": [{"vehicleType": 500, "equipment": ["drone"]}],
                "selected": [{"id": 101, "vehicleType": 501, "equipment": ["drone"]}]
            },
            "expect": {"rows": [{"key": "drone", "driving": 1, "selectedValue": 1, "covered": True}]}
        },
        {
            "name": "staff minimum and maximum ranges",
            "input": {
                "texts": {"staff": "6x more firefighters"},
                "driving": [{"vehicleType": 0, "staff": 4}],
                "selected": [{"id": 102, "vehicleType": 1, "staff": {"min": 2, "max": 6}}]
            },
            "expect": {"rows": [{"key": "firefighters", "driving": 4, "selected": {"min": 2, "max": 6}, "selectedValue": 2, "covered": True}]}
        },
        {
            "name": "selected is recomputed from current snapshot",
            "input": {"texts": {"vehicles": "1x Fire engine"}, "selected": []},
            "expect": {"rows": [{"key": "fire-engine", "selectedValue": 0, "covered": False}]}
        },
        {
            "name": "conditional vehicle capability",
            "input": {
                "texts": {"vehicles": "1x Rescue Boat"},
                "missionAdditional": {"allowPoweredBoat": True},
                "selected": [{"id": 103, "vehicleType": 68}]
            },
            "expect": {"rows": [{"key": "boat", "selectedValue": 1, "covered": True}]}
        },
        {
            "name": "random tractive contributes common capability",
            "input": {
                "texts": {"vehicles": "1x Towing Unit"},
                "selected": [{"id": 104, "vehicleType": 70, "tractiveRandom": True}]
            },
            "expect": {"rows": [{"key": "tractive", "selectedValue": 1, "covered": True}]}
        },
        {
            "name": "explicit unselected tractive contributes once",
            "input": {
                "texts": {"vehicles": "1x Towing Unit"},
                "selected": [{"id": 105, "vehicleType": 70, "tractiveRandom": False, "tractiveVehicleId": 900, "tractiveVehicleType": 57}]
            },
            "expect": {"rows": [{"key": "tractive", "selectedValue": 1, "covered": True}]}
        },
        {
            "name": "progress requirement uses live bar values",
            "input": {
                "texts": {"other": "5,000x litres of water"},
                "progress": {"water": {"texts": ["litres of water"], "missing": 4000, "driving": 1000, "selected": 2000}}
            },
            "expect": {"rows": [{"key": "progress:water", "missing": 5000, "driving": 1000, "selectedValue": 2000, "covered": False}], "remaining": {"other": ""}}
        }
    ]
}
FIXTURE.parent.mkdir(parents=True, exist_ok=True)
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

TEST.parent.mkdir(parents=True, exist_ok=True)
TEST.write_text(r'''#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..', '..');
const sourcePath = path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js');
const fixturePath = path.join(root, '.github', 'fixtures', 'issue-378-enhanced-requirements-cases.json');
const source = fs.readFileSync(sourcePath, 'utf8');
const startMarker = '    // Issue #378 enhanced requirements pure engine.';
const endMarker = '    // Issue #378 end enhanced requirements pure engine.';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker);
if (start < 0 || end <= start) throw new Error('Issue #378 engine markers are missing or invalid');
const block = source.slice(start, end + endMarker.length);
const context = { console };
vm.createContext(context);
vm.runInContext(`${block}\n;globalThis.__issue378Engine = { operationalRequirementCreateModel, operationalRequirementRows, operationalRequirementFingerprint };`, context);
const engine = context.__issue378Engine;
const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

function mergeInput(testCase) {
    return {
        catalog: fixture.catalog,
        vehicleTypes: fixture.vehicleTypes,
        ...(testCase.input || {})
    };
}

function assertEqual(actual, expected, label) {
    const actualJson = JSON.stringify(actual);
    const expectedJson = JSON.stringify(expected);
    if (actualJson !== expectedJson) {
        throw new Error(`${label}\nexpected: ${expectedJson}\nactual:   ${actualJson}`);
    }
}

for (const testCase of fixture.cases) {
    const model = engine.operationalRequirementCreateModel(mergeInput(testCase));
    const rows = engine.operationalRequirementRows(model, testCase.options || {});
    const expectedRows = testCase.expect.rows || [];
    for (const expected of expectedRows) {
        const row = rows.find(candidate => candidate.key === expected.key);
        if (!row) throw new Error(`${testCase.name}: missing row ${expected.key}`);
        const projected = {};
        for (const key of Object.keys(expected)) projected[key] = row[key];
        assertEqual(projected, expected, `${testCase.name}: row ${expected.key}`);
    }
    for (const [group, expected] of Object.entries(testCase.expect.remaining || {})) {
        assertEqual(model.requirementTexts[group]?.remaining ?? null, expected, `${testCase.name}: remaining ${group}`);
    }
    const firstFingerprint = engine.operationalRequirementFingerprint(model, testCase.options || {});
    const secondFingerprint = engine.operationalRequirementFingerprint(
        engine.operationalRequirementCreateModel(mergeInput(testCase)),
        testCase.options || {}
    );
    assertEqual(firstFingerprint, secondFingerprint, `${testCase.name}: deterministic fingerprint`);
}

const staffCase = fixture.cases.find(testCase => testCase.name === 'staff minimum and maximum ranges');
const staffModel = engine.operationalRequirementCreateModel(mergeInput(staffCase));
const maxRow = engine.operationalRequirementRows(staffModel, { calcMaxStaff: true }).find(row => row.key === 'firefighters');
assertEqual({ selectedValue: maxRow.selectedValue, covered: maxRow.covered }, { selectedValue: 6, covered: true }, 'staff maximum mode');

if (source.includes('data-mcms-operational-suite') || source.includes('mcms-operational-suite-panel')) {
    throw new Error('Phase 3 engine core must not render a competing operational-suite surface');
}
if (!source.includes('// Issue #133 clean-room live mission requirements matrix.')) {
    throw new Error('Phase 3 engine core must retain the legacy Matrix rollback runtime');
}

console.log(`Issue #378 enhanced requirements engine passed ${fixture.cases.length} deterministic cases.`);
''', encoding="utf-8")

shell_test = SHELL_TEST.read_text(encoding="utf-8")
old_shell_ledger = "if fixture.get('approvedNonStyleChanges') != [{'issue': 378, 'phase': 'operational-suite-shell', 'lines': 317}]:\n    raise SystemExit('Issue #378 source-headroom change ledger is missing or altered')\n"
new_shell_ledger = "approved_changes = fixture.get('approvedNonStyleChanges', [])\nif not approved_changes or approved_changes[0] != {'issue': 378, 'phase': 'operational-suite-shell', 'lines': 317}:\n    raise SystemExit('Issue #378 operational-suite shell source-headroom ledger entry is missing or altered')\n"
if shell_test.count(old_shell_ledger) != 1:
    raise RuntimeError("Issue #378 shell ledger assertion changed")
SHELL_TEST.write_text(shell_test.replace(old_shell_ledger, new_shell_ledger, 1), encoding="utf-8")

headroom = json.loads(HEADROOM_FIXTURE.read_text(encoding="utf-8"))
if headroom.get("schemaVersion") != 5:
    raise RuntimeError("main-style source-headroom schema changed before Phase 3")
if headroom.get("expectedSourceLines") != base_lines:
    raise RuntimeError(f"Phase 3 baseline line count drifted: {headroom.get('expectedSourceLines')} != {base_lines}")
changes = headroom.get("approvedNonStyleChanges")
if changes != [{"issue": 378, "phase": "operational-suite-shell", "lines": 317}]:
    raise RuntimeError("Phase 3 expected only the completed shell ledger entry")
changes.append({"issue": 378, "phase": "enhanced-requirements-engine-core", "lines": delta})
headroom["approvedNonStyleSourceLines"] = sum(change["lines"] for change in changes)
headroom["approvedNonStyleChanges"] = changes
headroom["expectedSourceLines"] = new_lines
HEADROOM_FIXTURE.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["node", str(TEST)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(SHELL_TEST)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(HEADROOM_TEST)], cwd=ROOT, check=True)
print(f"Issue #378 enhanced requirements engine core applied with exact source delta {delta}.")
