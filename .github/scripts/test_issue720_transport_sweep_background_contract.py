#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")

version = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", SOURCE)
assert version and tuple(int(part) for part in version.group(1).split(".")) >= (10, 9, 2)

for marker in [
    "transportSweep: { delayMs: 2000, maxPerRun: 25, backgroundFirst: true }",
    "merged.transportSweep.backgroundFirst = merged.transportSweep.backgroundFirst !== false;",
    "function transportSweepBackgroundCancelAction(doc, candidate)",
    "url.origin !== pageWindow.location.origin || url.search || url.hash",
    r"/^\/vehicles\/(\d+)\/patient\/(-?\d+)\/?$/u",
    "async function transportSweepAttemptBackgroundRelease(candidate)",
    "transportSweepBackgroundReleaseConfirmed(doc, prepared.confirmationBaseline)",
    "status: 'ambiguous'",
    "recordTransportSweepAmbiguousRelease(",
    "transportSweepRuntime.releaseAttempts += 1;",
    "backgroundResult.status === 'unsupported'",
    "Opening native fallback for",
    "data-setting=\"transport-sweep-mode\"",
    "A request without fresh confirmation is never retried.",
]:
    assert marker in SOURCE, marker

helpers = SOURCE[SOURCE.index("    function transportSweepBackgroundControlDisabled"):
                 SOURCE.index("    async function collectTransportSweepVehicleCandidatesForMission")]
assert "querySelectorAll('a[href]')" in helpers
assert "button.click()" not in helpers
assert "setInterval" not in helpers

process = re.search(
    r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep",
    SOURCE,
)
assert process
body = process.group(1)
assert body.index("backgroundResult.status === 'unsupported'") < body.index("attemptedVehicleIds.add(String(candidate.vehicleId));", body.index("backgroundResult.status"))
assert "it will not be retried" in body
assert "transportSweepRuntime.releaseAttempts < state.transportSweep.maxPerRun" in body

print("Issue #720 background-first Patient Transport Sweep contract passed.")
