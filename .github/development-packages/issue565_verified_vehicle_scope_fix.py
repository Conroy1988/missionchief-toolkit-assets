#!/usr/bin/env python3
"""Restrict Issue #565 fast releases to existing verified sweep candidates."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
STATIC = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
RUNTIME = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
DOC = ROOT / "docs/issue-565-transport-sweep-no-reward.md"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one replacement in {path}, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    SOURCE,
    "    function findTransportSweepOptionalReleaseControl(missionId, excludedReleaseKeys = null) {\n",
    "    function findTransportSweepOptionalReleaseControl(missionId, eligibleVehicleIds, excludedReleaseKeys = null) {\n",
)
replace_once(
    SOURCE,
    "            if (!details) continue;\n            const releaseKey = transportSweepReleaseKey(missionId, details.vehicleId);\n",
    "            if (!details) continue;\n            if (!(eligibleVehicleIds instanceof Set) || !eligibleVehicleIds.has(details.vehicleId)) continue;\n            const releaseKey = transportSweepReleaseKey(missionId, details.vehicleId);\n",
)
replace_once(
    SOURCE,
    "    async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance) {\n",
    "    async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance, eligibleVehicleIds) {\n",
)
replace_once(
    SOURCE,
    "            const release = findTransportSweepOptionalReleaseControl(missionId, attemptedReleaseKeys);\n",
    "            const release = findTransportSweepOptionalReleaseControl(missionId, eligibleVehicleIds, attemptedReleaseKeys);\n",
)

old_processor = '''        const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(
            item,
            missionId,
            Math.max(0, remainingAllowance - clearedHere)
        );
        clearedHere += optionalReleaseResult.cleared;
        if (
            transportSweepRuntime.stopRequested
            || !optionalReleaseResult.missionAvailable
            || clearedHere >= remainingAllowance
        ) {
            await closeTransportSweepWindows('ending no-reward patient release fast path');
            return clearedHere;
        }

        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId);
'''
new_processor = '''        let candidates = collectTransportSweepVehicleCandidatesForMission(missionId);
        const optionalEligibleVehicleIds = new Set(
            candidates
                .map(candidate => String(candidate?.vehicleId || '').trim())
                .filter(Boolean)
        );
        const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(
            item,
            missionId,
            Math.max(0, remainingAllowance - clearedHere),
            optionalEligibleVehicleIds
        );
        clearedHere += optionalReleaseResult.cleared;
        if (
            transportSweepRuntime.stopRequested
            || !optionalReleaseResult.missionAvailable
            || clearedHere >= remainingAllowance
        ) {
            await closeTransportSweepWindows('ending no-reward patient release fast path');
            return clearedHere;
        }

        candidates = collectTransportSweepVehicleCandidatesForMission(missionId);
'''
replace_once(SOURCE, old_processor, new_processor)

replace_once(
    STATIC,
    '"function findTransportSweepOptionalReleaseControl(missionId, excludedReleaseKeys = null)",\n        "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)",',
    '"function findTransportSweepOptionalReleaseControl(missionId, eligibleVehicleIds, excludedReleaseKeys = null)",\n        "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance, eligibleVehicleIds)",',
)
replace_once(
    STATIC,
    '''    assert processor.index("processTransportSweepOptionalReleaseControls(") < processor.index(
        "collectTransportSweepVehicleCandidatesForMission(missionId)"
    )
''',
    '''    first_collection = processor.index("let candidates = collectTransportSweepVehicleCandidatesForMission(missionId)")
    fast_path = processor.index("processTransportSweepOptionalReleaseControls(")
    second_collection = processor.index("candidates = collectTransportSweepVehicleCandidatesForMission(missionId)", first_collection + 1)
    assert first_collection < fast_path < second_collection
    assert "optionalEligibleVehicleIds" in processor
''',
)
replace_once(
    STATIC,
    '    assert "clearedHere += optionalReleaseResult.cleared" in processor\n',
    '    assert "clearedHere += optionalReleaseResult.cleared" in processor\n    assert "eligibleVehicleIds.has(details.vehicleId)" in helper\n',
)

replace_once(
    RUNTIME,
    '''    run(allowance = Number.POSITIVE_INFINITY) {
      return sandbox.runOptionalRelease({ caption: "Multi-patient mission" }, "9001", allowance);
    },
''',
    '''    run(allowance = Number.POSITIVE_INFINITY, eligible = pages.flat()) {
      return sandbox.runOptionalRelease(
        { caption: "Multi-patient mission" },
        "9001",
        allowance,
        new Set(eligible.map(String)),
      );
    },
''',
)
insert_marker = '''{
  const harness = createHarness([[]]);
'''
verified_case = '''{
  const harness = createHarness([["111", "999"], ["999"]]);
  const outcome = await harness.run(Number.POSITIVE_INFINITY, ["111"]);
  assert.equal(outcome.cleared, 1);
  assert.deepEqual(harness.clicks, ["111"]);
  assert.ok(harness.dom.window.document.querySelector('a[href="/vehicles/999/patient/-1"]'));
}

'''
replace_once(RUNTIME, insert_marker, verified_case + insert_marker)

replace_once(
    DOC,
    "The sweep releases one patient, reopens the same mission,",
    "Only vehicle IDs already verified by the existing sweep candidate collector are eligible. The sweep releases one patient, reopens the same mission,",
)

print("Issue #565 fast path restricted to verified sweep vehicle IDs.")
