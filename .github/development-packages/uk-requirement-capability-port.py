#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-requirements-contract.json"
CHANGELOG = ROOT / "CHANGELOG.md"
DIST_FILES = [ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js", ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one exact anchor, found {count}")
    return text.replace(old, new, 1)


def find_matching(text: str, start: int, opening: str, closing: str) -> int:
    if text[start] != opening:
        raise AssertionError(f"matching scan must start on {opening!r}")
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    i = start
    while i < len(text):
        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if char == "\n": line_comment = False
            i += 1; continue
        if block_comment:
            if char == "*" and nxt == "/": block_comment = False; i += 2; continue
            i += 1; continue
        if quote:
            if escaped: escaped = False
            elif char == "\\": escaped = True
            elif char == quote: quote = ""
            i += 1; continue
        if char in ("'", '"', "`"): quote = char; i += 1; continue
        if char == "/" and nxt == "/": line_comment = True; i += 2; continue
        if char == "/" and nxt == "*": block_comment = True; i += 2; continue
        if char == opening: depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0: return i
        i += 1
    raise AssertionError(f"unterminated {opening}{closing} structure")


def function_bounds(text: str, signature: str) -> tuple[int, int]:
    start = text.index(signature)
    brace = text.index("{", start)
    return start, find_matching(text, brace, "{", "}") + 1


def evaluate_plain_js_array(expression: str) -> list[dict]:
    helper = r"""
const fs = require('fs'); const vm = require('vm');
const expression = fs.readFileSync(0, 'utf8');
const value = vm.runInNewContext('(' + expression + ')', Object.create(null));
function validate(item, path = '$') {
  if (item === null) return;
  const type = typeof item;
  if (['string', 'number', 'boolean'].includes(type)) return;
  if (Array.isArray(item)) { item.forEach((entry, index) => validate(entry, path + '[' + index + ']')); return; }
  if (type === 'object' && Object.prototype.toString.call(item) === '[object Object]') { Object.entries(item).forEach(([key, entry]) => validate(entry, path + '.' + key)); return; }
  throw new Error('Unsupported value in requirement definitions at ' + path + ': ' + type);
}
validate(value); process.stdout.write(JSON.stringify(value));
"""
    result = subprocess.run(["node", "-e", helper], input=expression, text=True, capture_output=True, cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError(f"unable to evaluate mission requirement definitions:\n{result.stderr}")
    parsed = json.loads(result.stdout)
    if not isinstance(parsed, list): raise AssertionError("mission requirement definitions must evaluate to an array")
    return parsed


def normalise_alias(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def merge_unique(existing: list, incoming: list) -> list:
    result = list(existing or [])
    for item in incoming or []:
        if item not in result: result.append(item)
    return result


source = SOURCE.read_text(encoding="utf-8")
dataset = json.loads(DATA.read_text(encoding="utf-8"))
if dataset.get("schemaVersion") != 1 or dataset.get("locale") != "en_GB": raise AssertionError("UK capability dataset is invalid")
if "// @version      4.20.5" not in source or "version: '4.20.5'" not in source: raise AssertionError("requires verified v4.20.5 source")
source = replace_once(source, "// @version      4.20.5", "// @version      4.20.6", "metadata version")
source = replace_once(source, "version: '4.20.5'", "version: '4.20.6'", "runtime version")
marker = "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze(["
marker_index = source.index(marker)
array_start = source.index("[", marker_index)
array_end = find_matching(source, array_start, "[", "]")
definitions = evaluate_plain_js_array(source[array_start:array_end + 1])
for definition in definitions:
    definition.setdefault("aliases", [])
    definition.setdefault("types", [])
for group, entries in (("vehicles", dataset["vehicleRequirements"]), ("staff", dataset["staffRequirements"])):
    for entry in entries:
        aliases = [str(value) for value in entry.get("aliases", []) if str(value).strip()]
        alias_set = {normalise_alias(value) for value in aliases}
        matches = [definition for definition in definitions if definition.get("group") == group and (definition.get("key") == entry.get("key") or alias_set.intersection(normalise_alias(value) for value in definition.get("aliases", [])))]
        if len(matches) > 1: raise AssertionError(f"ambiguous definitions for {group}:{entry.get('key')}: {[item.get('key') for item in matches]}")
        if matches:
            target = matches[0]
        else:
            key = str(entry.get("key") or "").strip()
            existing_keys = {str(item.get("key") or "") for item in definitions}
            if not key: raise AssertionError(f"missing stable key for {group} requirement")
            if key in existing_keys:
                suffix = 2
                while f"{key}-{suffix}" in existing_keys: suffix += 1
                key = f"{key}-{suffix}"
            target = {"key": key, "group": group, "aliases": [], "types": []}
            definitions.append(target)
        target["aliases"] = merge_unique(target.get("aliases", []), aliases)
        target["types"] = merge_unique([int(value) for value in target.get("types", [])], [int(value) for value in entry.get("types", [])])
        if entry.get("equipment"):
            target["equipment"] = merge_unique([str(value) for value in target.get("equipment", [])], [str(value) for value in entry.get("equipment", [])])
compact_definitions = json.dumps(definitions, ensure_ascii=False, separators=(",", ":"))
source = source[:array_start] + compact_definitions + source[array_end + 1:]
definition_close = array_start + len(compact_definitions)
freeze_close = source.index(");", definition_close) + 2
sort_block = "\n    const MISSION_REQUIREMENT_PARSE_DEFINITIONS = Object.freeze([...MISSION_REQUIREMENT_DEFINITIONS].sort((left, right) => Math.max(...((right.aliases && right.aliases.length) ? right.aliases : ['']).map(value => String(value).length)) - Math.max(...((left.aliases && left.aliases.length) ? left.aliases : ['']).map(value => String(value).length))));"
source = source[:freeze_close] + sort_block + source[freeze_close:]
parse_start, parse_end = function_bounds(source, "function missionRequirementsParseText(rawText, group = 'vehicles')")
parse_block = source[parse_start:parse_end]
if parse_block.count("MISSION_REQUIREMENT_DEFINITIONS") < 1: raise AssertionError("parser no longer references definitions")
parse_block = parse_block.replace("MISSION_REQUIREMENT_DEFINITIONS", "MISSION_REQUIREMENT_PARSE_DEFINITIONS")
source = source[:parse_start] + parse_block + source[parse_end:]
if "v4.lss-manager.de" in source or "LSS-Manager" in source: raise AssertionError("runtime must remain independent")
SOURCE.write_text(source, encoding="utf-8")
for distribution in DIST_FILES: distribution.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "const catalogueFixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-catalogue-pages.json'), 'utf8'));\n", "const catalogueFixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-catalogue-pages.json'), 'utf8'));\nconst ukCapabilityFixture = JSON.parse(fs.readFileSync(path.join(root, 'src', 'data', 'mission-requirements-en_GB.json'), 'utf8'));\n", "runtime fixture import")
runtime_tests = r"""
for (const [group, entries] of [['vehicles', ukCapabilityFixture.vehicleRequirements], ['staff', ukCapabilityFixture.staffRequirements]]) {
    for (const entry of entries) {
        const matchingDefinitions = api.definitions.filter(definition => definition.group === group && entry.aliases.some(alias => (definition.aliases || []).some(value => String(value).trim().toLowerCase() === String(alias).trim().toLowerCase())));
        assert.strictEqual(matchingDefinitions.length, 1, `${group}:${entry.key}: one canonical definition`);
        const definition = matchingDefinitions[0];
        for (const alias of entry.aliases) {
            assert.ok((definition.aliases || []).includes(alias), `${group}:${entry.key}: alias ${alias}`);
            const parsed = api.parseText(`1 ${alias}`, group);
            assert.ok(parsed.requirements.some(requirement => requirement.key === definition.key && requirement.missing === 1), `${group}:${entry.key}: parser handles ${alias}`);
            assert.strictEqual(parsed.remaining, '', `${group}:${entry.key}: parser consumes ${alias}`);
        }
        for (const typeId of entry.types) assert.ok((definition.types || []).includes(typeId), `${group}:${entry.key}: vehicle type ${typeId}`);
        for (const equipment of entry.equipment || []) assert.ok((definition.equipment || []).includes(equipment), `${group}:${entry.key}: equipment ${equipment}`);
    }
}

"""
runtime = replace_once(runtime, "for (const testCase of fixture.coverageCases) {\n", runtime_tests + "for (const testCase of fixture.coverageCases) {\n", "runtime capability coverage")
runtime = runtime.replace("version: '4.20.4'", "version: '4.20.6'")
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(contract, 'CATALOGUE_FIXTURE = ROOT / ".github/fixtures/mission-catalogue-pages.json"\n', 'CATALOGUE_FIXTURE = ROOT / ".github/fixtures/mission-catalogue-pages.json"\nUK_CAPABILITY_FIXTURE = ROOT / "src/data/mission-requirements-en_GB.json"\n', "contract fixture path")
contract = replace_once(contract, '    catalogue_fixture = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))\n', '    catalogue_fixture = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))\n    uk_capabilities = json.loads(UK_CAPABILITY_FIXTURE.read_text(encoding="utf-8"))\n    assert uk_capabilities["schemaVersion"] == 1\n    assert uk_capabilities["locale"] == "en_GB"\n    assert len(uk_capabilities["vehicleRequirements"]) >= 68\n    assert len(uk_capabilities["staffRequirements"]) >= 2\n', "contract fixture load")
contract = replace_once(contract, '        "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",\n', '        "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",\n        "const MISSION_REQUIREMENT_PARSE_DEFINITIONS = Object.freeze(",\n', "sorted parser contract")
contract = replace_once(contract, '    assert "return { root, parent: operational.parentNode, before: operational };" not in source\n', '    assert "return { root, parent: operational.parentNode, before: operational };" not in source\n    assert "v4.lss-manager.de" not in source\n    assert "LSS-Manager" not in source\n    aliases_seen = set()\n    for group_name in ("vehicleRequirements", "staffRequirements"):\n        for entry in uk_capabilities[group_name]:\n            assert entry["aliases"] and entry["types"]\n            for alias in entry["aliases"]:\n                folded = re.sub(r"\\s+", " ", alias).strip().casefold()\n                assert folded not in aliases_seen, f"duplicate UK capability alias: {alias}"\n                aliases_seen.add(folded)\n                assert alias in source, f"UK capability alias missing from source: {alias}"\n            for vehicle_type in entry["types"]: assert isinstance(vehicle_type, int) and vehicle_type >= 0\n', "contract capability invariants")
CONTRACT.write_text(contract, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture["parserCases"].extend([
    {"name":"operational support combination","group":"vehicles","input":"1 Operational Support Van, Trailer or Personal SAR Vehicle","expected":[{"key":"operational-support-van-trailer-or-personal-sar-vehicle","missing":1}],"remaining":""},
    {"name":"new mountain rescue capability","group":"vehicles","input":"2 Rescue Dogs","expected":[{"key":"rescue-dog","missing":2}],"remaining":""},
    {"name":"new railway capability","group":"vehicles","input":"1 Road Rail Unit","expected":[{"key":"road-rail-unit","missing":1}],"remaining":""}
])
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.20.6] - 2026-07-19

### Added
- Added the complete current UK MissionChief vehicle and personnel requirement capability dataset to the Mission Requirements Matrix.
- Added explicit capability coverage for specialist fire, ambulance, police, coastguard, airfield, mountain rescue, railway and specialist response assets.
- Added dataset-driven parser and vehicle-type regression coverage for every imported UK requirement alias.

### Changed
- Requirement parsing now prioritises the longest recognised phrase so combined requirements are not consumed by shorter generic aliases.
- Existing Toolkit selected, responding, on-site, authoritative-catalogue and patient-demand reconciliation remains unchanged.
- The capability dataset is compiled into the userscript with no external manager service at runtime.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")
subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
if SOURCE.stat().st_size > 3_000_000: raise AssertionError("v4.20.6 exceeds source ceiling")
if len(SOURCE.read_text(encoding="utf-8").splitlines()) > 32_000: raise AssertionError("v4.20.6 exceeds line ceiling")
Path(__file__).unlink()
print("Prepared v4.20.6 complete UK requirement capability port")
