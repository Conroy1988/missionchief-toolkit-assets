#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-marker-ingestion-contract.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_marker_ingestion_contract.py"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
OLD_VERSION = "4.20.33"
NEW_VERSION = "4.20.34"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(
    source,
    f"// @version      {OLD_VERSION}",
    f"// @version      {NEW_VERSION}",
    "userscript metadata version",
)
source = replace_once(
    source,
    f"version: '{OLD_VERSION}'",
    f"version: '{NEW_VERSION}'",
    "runtime version",
)
old_capture = """    function captureMissionMarkerData(payload) {
        if (!payload) return;
        if (Array.isArray(payload)) {
        payload.forEach(captureMissionMarkerData);
        return;
        }
        if (typeof payload !== 'object') return;

        const candidates = [payload, payload.params, payload.mission, payload.data].filter(item => item && typeof item === 'object');
        for (const item of candidates) {
        const missionId = normaliseMissionId(item.id ?? item.mission_id ?? item.missionId);
        if (missionId === null) continue;

        const existing = missionOverlayData.get(missionId) || {};
        setMissionOverlayRecord(missionId, normaliseMissionOverlayRecord(item, existing));
        }
    }
"""
new_capture = """    function resolveMissionMarkerCandidates(payload) {
        if (!payload) return [];
        if (Array.isArray(payload)) return payload.flatMap(resolveMissionMarkerCandidates);
        if (typeof payload !== 'object') return [];
        return [payload, payload.params, payload.mission, payload.data]
        .filter(item => item && typeof item === 'object')
        .map(item => ({ item, missionId: normaliseMissionId(item.id ?? item.mission_id ?? item.missionId) }))
        .filter(candidate => candidate.missionId !== null);
    }
    function captureMissionMarkerData(payload) {
        for (const { item, missionId } of resolveMissionMarkerCandidates(payload)) {
        const existing = missionOverlayData.get(missionId) || {};
        setMissionOverlayRecord(missionId, normaliseMissionOverlayRecord(item, existing));
        }
    }
"""
source = replace_once(source, old_capture, new_capture, "mission-marker candidate extraction")
SOURCE.write_text(source, encoding="utf-8")
for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture["candidateResolution"] = {
    "objectPayload": {
        "id": "root",
        "mission_id": "ignored-root",
        "params": {"mission_id": 200},
        "mission": {"missionId": 300},
        "data": {"id": 400},
    },
    "objectExpectedIds": ["root", "200", "300", "400"],
    "arrayPayload": [
        {"id": 10},
        None,
        "ignored",
        {"data": {"mission_id": 20}},
        [{"missionId": 30}, {"id": ""}, {"id": 0}, {"id": -2}],
    ],
    "arrayExpectedIds": ["10", "20", "30", "0", "-2"],
    "emptyIdBlocksFallback": {"id": "", "mission_id": 88},
    "nullFallsThrough": {"mission_id": None, "missionId": 77},
    "duplicatePayload": {"id": 70, "data": {"id": 70}},
    "duplicateExpectedIds": ["70", "70"],
}
FIXTURE.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '    "normaliseMissionId",\n    "missionIdFromMarker",',
    '    "normaliseMissionId",\n    "resolveMissionMarkerCandidates",\n    "missionIdFromMarker",',
    "marker contract function inventory",
)
candidate_test = r'''
function testCandidateResolution() {
    const candidateFixture = fixtures.candidateResolution;
    const objectCandidates = resolveMissionMarkerCandidates(candidateFixture.objectPayload);
    assert.deepEqual(objectCandidates.map(candidate => candidate.missionId), candidateFixture.objectExpectedIds);
    assert.equal(objectCandidates[0].item, candidateFixture.objectPayload, "root candidate reference changed");
    assert.equal(objectCandidates[1].item, candidateFixture.objectPayload.params, "params candidate reference changed");
    assert.equal(objectCandidates[2].item, candidateFixture.objectPayload.mission, "mission candidate reference changed");
    assert.equal(objectCandidates[3].item, candidateFixture.objectPayload.data, "data candidate reference changed");

    const arrayCandidates = resolveMissionMarkerCandidates(candidateFixture.arrayPayload);
    assert.deepEqual(arrayCandidates.map(candidate => candidate.missionId), candidateFixture.arrayExpectedIds, "recursive array order changed");

    assert.deepEqual(resolveMissionMarkerCandidates(candidateFixture.emptyIdBlocksFallback), [], "empty id must continue blocking fallback exactly as production does");
    assert.deepEqual(resolveMissionMarkerCandidates(candidateFixture.nullFallsThrough).map(candidate => candidate.missionId), ["77"], "nullish ID fallback changed");
    assert.deepEqual(resolveMissionMarkerCandidates(candidateFixture.duplicatePayload).map(candidate => candidate.missionId), candidateFixture.duplicateExpectedIds, "duplicate candidate behavior changed");
    assert.deepEqual(resolveMissionMarkerCandidates(null), []);
    assert.deepEqual(resolveMissionMarkerCandidates(false), []);
    assert.deepEqual(resolveMissionMarkerCandidates(0), []);
    assert.deepEqual(resolveMissionMarkerCandidates("mission"), []);
}

'''
contract = replace_once(
    contract,
    "function testOverlayRecordNormalisation() {",
    candidate_test + "function testOverlayRecordNormalisation() {",
    "direct candidate-resolution contract",
)
contract = replace_once(
    contract,
    "testOverlayRecordNormalisation();\n",
    "testCandidateResolution();\ntestOverlayRecordNormalisation();\n",
    "candidate-resolution contract invocation",
)
contract = replace_once(
    contract,
    'console.log("Mission marker ingestion contract passed: direct normalization, payload capture, partial updates, ownership, events, inline scripts, coordinates and cache invalidation.");',
    'console.log("Mission marker ingestion contract passed: candidate resolution, direct normalization, payload capture, partial updates, ownership, events, inline scripts, coordinates and cache invalidation.");',
    "marker contract result summary",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = f"""## [{NEW_VERSION}] - 2026-07-22

### Core mission-data reliability
- Extracted mission-marker candidate discovery and mission-ID normalization from `captureMissionMarkerData()` into `resolveMissionMarkerCandidates()`.
- Preserved array recursion, payload/params/mission/data ordering, exact ID-key precedence, stringification, duplicate behavior and overlay publication.
- Added direct fixtures for nested containers, arrays, nullish fall-through, empty-ID blocking, zero/negative values and duplicate candidates.

### Benefit
- Mission payload-shape changes are now easier to isolate and support without risking overlay publication, ownership classification or downstream mission windows.

### Compatibility
- No mission ownership, coordinates, timestamps, requirements, patients, prisoners, event state, visual design, device layout, theme, payout, notification, timing or public asset changed.

"""
changelog_path.write_text(
    replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog insertion"),
    encoding="utf-8",
)

help_path = ROOT / "help" / "index.html"
help_text = help_path.read_text(encoding="utf-8")
if OLD_VERSION not in help_text:
    raise RuntimeError("help page does not contain the current version")
help_path.write_text(help_text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
source_lines = len(source.splitlines())
headroom["candidateVersion"] = NEW_VERSION
headroom["candidateSourceLines"] = source_lines
headroom["recoveredSourceLines"] = headroom["originalSourceLines"] - source_lines
headroom["candidateSourceSha256"] = hashlib.sha256(source.encode()).hexdigest()
headroom["invariant"] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines '
    "while mission-marker candidate resolution remains fixture-backed and managed runtime budgets remain unchanged."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.check_call(
    [sys.executable, str(CONTRACT)],
    cwd=ROOT,
    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print(
    f"Prepared Toolkit {NEW_VERSION}; source lines={source_lines}; "
    f"recovered={headroom['recoveredSourceLines']}"
)
