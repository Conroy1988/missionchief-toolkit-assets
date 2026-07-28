#!/usr/bin/env python3
"""Apply v8.2.2 Patient Transport Sweep mission-readiness correction."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
STATIC = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
RUNTIME = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
HELP_MANIFEST = ROOT / "help/manifest.json"
DOC = ROOT / "docs/issue-565-transport-sweep-no-reward.md"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"

source = SOURCE.read_text(encoding="utf-8")
if not re.search(r"(?m)^//\s*@version\s+8\.2\.1$", source):
    raise RuntimeError("Expected v8.2.1 source")
source = source.replace(
    "    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS = 2500;",
    "    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS = 6000;",
    1,
)

state_pattern = re.compile(
    r"    function transportSweepOptionalReleaseState\(missionId\) \{[\s\S]*?\n    \}\n\n"
    r"    async function waitForTransportSweepOptionalReleaseState\(missionId, options = \{\}\) \{[\s\S]*?\n    \}\n\n"
    r"    function findTransportSweepOptionalReleaseControl",
)
replacement = '''    function transportSweepOptionalReleaseMissionReady() {
        let ready = false;
        const inspect = root => {
            if (!root || ready) return;
            try {
                const table = root.matches?.('#mission_vehicle_at_mission')
                    ? root
                    : root.querySelector?.('#mission_vehicle_at_mission');
                if (table?.querySelector?.('tbody tr')) ready = true;
            } catch (error) {}
        };
        transportSweepVisibleWindowRoots().forEach(inspect);
        transportSweepDocumentContexts().forEach(context => inspect(context.doc));
        return ready;
    }

    function transportSweepOptionalReleaseState(missionId) {
        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId) || [];
        const eligibleVehicleIds = new Set(
            Array.from(candidates)
                .map(candidate => String(candidate?.vehicleId || '').trim())
                .filter(Boolean)
        );
        const releases = transportSweepOptionalReleaseControls()
            .map(transportSweepOptionalReleaseDetails)
            .filter(details => details && eligibleVehicleIds.has(details.vehicleId));
        return {
            candidates: Array.from(candidates),
            eligibleVehicleIds,
            releases,
            missionReady: transportSweepOptionalReleaseMissionReady(),
        };
    }

    async function waitForTransportSweepOptionalReleaseState(missionId, options = {}) {
        const vehicleId = String(options.vehicleId || '').trim();
        const timeoutMs = Math.max(0, Number(options.timeoutMs) || TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS);
        let latest = transportSweepOptionalReleaseState(missionId);
        const releaseVisible = () => vehicleId
            ? latest.releases.some(release => release.vehicleId === vehicleId)
            : latest.releases.length > 0;
        const vehicleConfirmedAbsent = () => Boolean(
            vehicleId
            && latest.missionReady
            && !latest.eligibleVehicleIds.has(vehicleId)
        );
        if (releaseVisible() || vehicleConfirmedAbsent()) {
            return { ...latest, settled: true, timedOut: false };
        }

        const waited = await transportSweepWaitFor(() => {
            latest = transportSweepOptionalReleaseState(missionId);
            if (releaseVisible() || vehicleConfirmedAbsent()) return latest;
            return null;
        }, timeoutMs, 70);
        return waited
            ? { ...waited, settled: true, timedOut: false }
            : { ...latest, settled: false, timedOut: true };
    }

    function findTransportSweepOptionalReleaseControl'''
source, count = state_pattern.subn(replacement, source, count=1)
if count != 1:
    raise RuntimeError(f"Expected one readiness block replacement, found {count}")
source = re.sub(r"(?m)^//\s*@version\s+8\.2\.1$", "// @version      8.2.2", source, count=1)
source = source.replace("version: '8.2.1'", "version: '8.2.2'", 1)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = runtime.replace(
    '  let poll = 0;\n',
    '  let poll = 0;\n  let missionRowsReady = options.deferMissionRows !== true;\n  const fetchPolls = [];\n',
    1,
)
runtime = runtime.replace(
    '''  function render(includeButton = false) {
    const count = countForGeneration();
    const mission = dom.window.document.querySelector("#mission");
    if (!count) {
      mission.innerHTML = '<table id="mission_vehicle_at_mission"><tbody></tbody></table>';
      return;
    }
    const names = Array.from({ length: count }, (_, index) => `Patient ${index + 1}`).join(" , ");
    mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111" data-eligible="true"><td>ILB (ILB)<br>Patient: ${names}</td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;
''',
    '''  function render(includeButton = false) {
    const count = countForGeneration();
    const mission = dom.window.document.querySelector("#mission");
    if (!missionRowsReady) {
      mission.innerHTML = "";
      return;
    }
    if (!count) {
      mission.innerHTML = '<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111"><td>ILB (ILB)</td><td>Station</td><td>Owner</td><td class="actions"></td></tr></tbody></table>';
      return;
    }
    const names = Array.from({ length: count }, (_, index) => `Patient ${index + 1}`).join(" , ");
    mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111" data-eligible="true"><td>ILB (ILB)<br>Patient: ${names}</td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;
''',
    1,
)
runtime = runtime.replace(
    '''      for (let index = 0; index < 100; index += 1) {
        poll += 1;
        if (countForGeneration() > 0 && poll >= (options.injectAfterPolls ?? 3)) injectDeferredControl();
''',
    '''      for (let index = 0; index < 140; index += 1) {
        poll += 1;
        if (!missionRowsReady && poll >= (options.rowsAfterPolls ?? 4)) {
          missionRowsReady = true;
          render(false);
        }
        if (missionRowsReady && countForGeneration() > 0 && poll >= (options.injectAfterPolls ?? 3)) injectDeferredControl();
''',
    1,
)
runtime = runtime.replace(
    '''      generation += 1;
      poll = 0;
      render(false);
''',
    '''      generation += 1;
      poll = 0;
      missionRowsReady = options.deferMissionRowsOnReopen === true ? false : true;
      render(false);
''',
    1,
)
runtime = runtime.replace(
    '    fetches.push(String(href));\n',
    '    fetches.push(String(href));\n    fetchPolls.push(poll);\n',
    1,
)
runtime = runtime.replace(
    '''    fetches,
    order,
''',
    '''    fetches,
    fetchPolls,
    order,
''',
    1,
)
runtime = runtime.replace(
    '''  const harness = createHarness([3, 2, 1, 0], { injectAfterPolls: 4, fetchDelayMs: 12 });
''',
    '''  const harness = createHarness([3, 2, 1, 0], {
    deferMissionRows: true,
    deferMissionRowsOnReopen: true,
    rowsAfterPolls: 4,
    injectAfterPolls: 9,
    fetchDelayMs: 12,
  });
''',
    1,
)
runtime = runtime.replace(
    '''  assert.equal(harness.runtime.errors, 0);
  assert.equal(harness.opens, 3);
''',
    '''  assert.equal(harness.runtime.errors, 0);
  assert.ok(harness.fetchPolls.every(value => value >= 9), "release request must wait for delayed rows and controls");
  assert.equal(harness.opens, 3);
''',
    1,
)
runtime = runtime.replace(
    'console.log("Issue #565 v8.2.1 live release runtime passed:',
    'console.log("Issue #565 v8.2.2 mission-readiness runtime passed:',
    1,
)
RUNTIME.write_text(runtime, encoding="utf-8")

static = STATIC.read_text(encoding="utf-8")
static = static.replace(r'@version\s+8\.2\.1', r'@version\s+8\.2\.2', 1)
static = static.replace("version: '8.2.1'", "version: '8.2.2'", 1)
static = static.replace(
    '        "function transportSweepOptionalReleaseState(missionId)",\n',
    '        "function transportSweepOptionalReleaseMissionReady()",\n        "function transportSweepOptionalReleaseState(missionId)",\n        "missionReady: transportSweepOptionalReleaseMissionReady()",\n        "TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS = 6000",\n',
    1,
)
static = static.replace(
    '    assert "after.patientCount < before.patientCount" in helper\n',
    '    assert "after.patientCount < before.patientCount" in helper\n    assert "latest.eligibleVehicleIds.size === 0" not in helper\n    assert "latest.missionReady" in helper\n',
    1,
)
static = static.replace('assert "## [8.2.1] - 2026-07-28"', 'assert "## [8.2.2] - 2026-07-28"', 1)
static = static.replace('    assert \'"version": "8.2.1"\' in performance\n', '')
static = static.replace('Issue #565 v8.2.1 completion-aware', 'Issue #565 v8.2.2 mission-readiness', 1)
STATIC.write_text(static, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [8.2.2] - 2026-07-28

### Patient Transport Sweep — authoritative mission readiness

- Fixed the sweep treating an empty pre-render mission DOM as a completed no-control state.
- Keeps the mission window open for a bounded six-second discovery period while Vehicles on Scene rows and optional release controls mount asynchronously.
- Requires an authoritative mission vehicle row before post-release vehicle absence can confirm the final patient has cleared.
- Adds browser-faithful delayed-row and delayed-button regression coverage matching the supplied production video.
- Adds no observer, interval, network request or Toolkit-managed timer.

'''
if "## [8.2.2]" not in changelog:
    changelog = changelog.replace("# Changelog\n\n", "# Changelog\n\n" + entry, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
help_text = help_text.replace("v8.2.1", "v8.2.2")
help_text = help_text.replace(
    "completes the exact visible same-origin request before closing the mission window",
    "waits for the authoritative Vehicles on Scene row and delayed control, then completes the exact visible same-origin request before closing the mission window",
)
HELP.write_text(help_text, encoding="utf-8")

manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
manifest["guideVersion"] = "8.2.2"
manifest["toolkitVersion"] = "8.2.2"
manifest["updated"] = "2026-07-28"
manifest["runtimeGuidePatch"] = "Toolkit v8.2.2 keeps the mission open until authoritative vehicle rows and delayed no-reward controls are discoverable, preventing premature fallback and window cleanup."
HELP_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

DOC.write_text('''# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.2 recognises only the exact visible same-origin `Release patient (No reward)` control whose path matches `/vehicles/{vehicleId}/patient/-1`.

The sweep now treats the opened mission as asynchronous. An empty mission DOM is never considered a completed scan. It waits boundedly for an authoritative `#mission_vehicle_at_mission` row and the delayed optional control before falling back. After each completed request and mission reopen, vehicle absence can confirm the final patient only after the authoritative row surface exists. This prevents the mission window from being closed while rows and controls are still loading.

Verified vehicles, sequential same-vehicle patient reduction, allowance, cancellation, request failure and the native MissionChief discharge fallback remain preserved. No persistent observer, interval, additional request site or Toolkit-managed timer is added.
''', encoding="utf-8")

source_bytes = SOURCE.read_bytes()
sha = hashlib.sha256(source_bytes).hexdigest()
lines = len(source_bytes.decode("utf-8").splitlines())
for relative in ["dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{sha}  MissionChief_Map_Command_Toolkit.user.js\n{sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
release_manifest = ROOT / "dist/release-manifest.json"
release = json.loads(release_manifest.read_text(encoding="utf-8"))
release.update({"version": "8.2.2", "sha256": sha, "bytes": len(source_bytes), "lines": lines})
release["metadata"]["runtimeVersion"] = "8.2.2"
release_manifest.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate.update({
    "issue": 565,
    "version": "8.2.2",
    "sourceBytes": len(source_bytes),
    "sourceLines": lines,
    "sourceSha256": sha,
    "baseline": "8.2.1",
    "scope": "Issue #565 authoritative mission-row readiness and delayed optional-control discovery before Patient Transport Sweep fallback or cleanup",
})
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), lines + 250)
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + lines - old_lines
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"v8.2.2 mission-readiness hotfix applied: {sha}, {len(source_bytes)} bytes, {lines} lines")
