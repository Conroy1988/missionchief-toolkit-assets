#!/usr/bin/env python3
"""Make the verified-vehicle scope package replace the processor block by offsets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue565_verified_vehicle_scope_fix.py"
text = PACKAGE.read_text(encoding="utf-8")
start = text.find("old_processor = '''")
end_marker = "replace_once(SOURCE, old_processor, new_processor)\n"
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise RuntimeError("Unable to locate scope processor replacement")
end += len(end_marker)
replacement = '''source_text = SOURCE.read_text(encoding="utf-8")
processor_start = source_text.find("    async function processTransportSweepMission(item, remainingAllowance) {")
processor_end = source_text.find("\\n    async function startTransportSweep", processor_start)
optional_index = source_text.find("const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(", processor_start, processor_end)
if processor_start < 0 or processor_end <= processor_start or optional_index < 0:
    raise RuntimeError("Generated optional release processor block missing")
optional_start = source_text.rfind("\\n", processor_start, optional_index) + 1
candidate_call = "collectTransportSweepVehicleCandidatesForMission(missionId)"
candidate_call_index = source_text.find(candidate_call, optional_index, processor_end)
if candidate_call_index < 0:
    raise RuntimeError("Generated candidate collection call missing")
candidate_end = source_text.find(";", candidate_call_index, processor_end)
if candidate_end < 0:
    raise RuntimeError("Generated candidate collection terminator missing")
candidate_end += 1
new_processor = ''' + "'''" + '''        let candidates = collectTransportSweepVehicleCandidatesForMission(missionId);
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

        candidates = collectTransportSweepVehicleCandidatesForMission(missionId);''' + "'''" + '''
SOURCE.write_text(
    source_text[:optional_start] + new_processor + source_text[candidate_end:],
    encoding="utf-8",
)
'''
PACKAGE.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
print("Issue #565 verified-vehicle scope patch uses processor-bounded offsets.")
