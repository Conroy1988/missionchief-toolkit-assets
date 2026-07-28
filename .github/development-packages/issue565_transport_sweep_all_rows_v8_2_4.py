#!/usr/bin/env python3
"""Apply v8.2.4 authoritative patient-row eligibility for no-reward releases."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
STATIC_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DOC = ROOT / "docs/issue-565-transport-sweep-no-reward.md"
HELP = ROOT / "help/index.html"
HELP_MANIFEST = ROOT / "help/manifest.json"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"

source = SOURCE.read_text(encoding="utf-8")
if not re.search(r"(?m)^//\s*@version\s+8\.2\.3$", source):
    raise RuntimeError("Expected canonical v8.2.3 source")

count_start = source.index("    function transportSweepOptionalReleasePatientCount(control) {")
details_start = source.index("    function transportSweepOptionalReleaseDetails(control) {", count_start)
new_row_helpers = r'''    function transportSweepOptionalReleasePatientCountFromRow(row) {
        const vehicleCell = row?.querySelector?.('td:first-child') || row;
        const text = String(vehicleCell?.textContent || '').replace(/\s+/gu, ' ').trim();
        const match = text.match(/\bpatients?\s*:\s*(.+)$/iu);
        if (!match?.[1]) return null;
        const names = match[1]
            .split(/\s*,\s*/u)
            .map(value => value.trim())
            .filter(Boolean);
        return names.length || null;
    }

    function transportSweepOptionalReleaseRowVehicleId(row) {
        if (!row) return null;
        const rowId = String(row.id || '');
        const rowMatch = rowId.match(/(?:vehicle(?:_row)?_?)(\d+)$/iu);
        if (rowMatch?.[1]) return rowMatch[1];
        let anchors = [];
        try { anchors = Array.from(row.querySelectorAll?.('a[href*="/vehicles/"]') || []); } catch (error) {}
        for (const anchor of anchors) {
            const vehicleId = transportSweepVehicleIdFromHref(anchor.getAttribute?.('href'));
            if (vehicleId) return String(vehicleId);
        }
        return null;
    }

    function transportSweepOptionalReleasePatientRows() {
        const rows = new Map();
        const ownVehicleIds = transportSweepOwnVehicleIdSet();
        const inspect = root => {
            if (!root) return;
            let matches = [];
            try {
                if (root.matches?.('#mission_vehicle_at_mission tbody tr')) matches.push(root);
                matches.push(...Array.from(root.querySelectorAll?.('#mission_vehicle_at_mission tbody tr') || []));
            } catch (error) {}
            for (const row of matches) {
                const vehicleId = transportSweepOptionalReleaseRowVehicleId(row);
                if (!vehicleId || rows.has(vehicleId) || ownVehicleIds.has(String(vehicleId))) continue;
                if (!row.querySelector?.('.building_list_fms_5')) continue;
                const patientCount = transportSweepOptionalReleasePatientCountFromRow(row);
                if (!Number.isFinite(patientCount) || patientCount <= 0) continue;
                rows.set(String(vehicleId), { vehicleId: String(vehicleId), row, patientCount });
            }
        };
        transportSweepVisibleWindowRoots().forEach(inspect);
        transportSweepDocumentContexts().forEach(context => inspect(context.doc));
        return rows;
    }

'''
source = source[:count_start] + new_row_helpers + source[details_start:]

# Replace the release-details helper so cloned controls resolve through the authoritative row.
details_start = source.index("    function transportSweepOptionalReleaseDetails(control) {")
details_end = source.index("    function transportSweepOptionalReleaseControls()", details_start)
new_details = r'''    function transportSweepOptionalReleaseDetails(control, patientRows = null) {
        if (!control || !transportSweepElementVisible(control)) return null;
        if (normaliseTransportSweepReleaseText(control.textContent) !== TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT) return null;
        const rawHref = String(control.getAttribute?.('href') || control.href || '').trim();
        if (!rawHref) return null;
        let url;
        try {
            url = new URL(rawHref, location.href);
        } catch (error) {
            return null;
        }
        let currentOrigin = '';
        try { currentOrigin = new URL(location.href).origin; } catch (error) {}
        if (currentOrigin && url.origin !== currentOrigin) return null;
        const match = url.pathname.match(TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH);
        if (!match?.groups?.vehicleId) return null;
        const vehicleId = String(match.groups.vehicleId);
        const directRow = control.closest?.('#mission_vehicle_at_mission tbody tr') || null;
        const directVehicleId = transportSweepOptionalReleaseRowVehicleId(directRow);
        const authoritative = directVehicleId === vehicleId
            ? {
                vehicleId,
                row: directRow,
                patientCount: transportSweepOptionalReleasePatientCountFromRow(directRow),
            }
            : patientRows?.get?.(vehicleId) || null;
        return {
            control,
            href: url.href,
            path: url.pathname,
            vehicleId,
            patientCount: authoritative?.patientCount ?? null,
            row: authoritative?.row || null,
            directRow: Boolean(authoritative?.row && authoritative.row === directRow),
        };
    }

'''
source = source[:details_start] + new_details + source[details_end:]

state_start = source.index("    function transportSweepOptionalReleaseState(missionId) {")
state_end = source.index("    async function waitForTransportSweepOptionalReleaseState", state_start)
new_state = r'''    function transportSweepOptionalReleaseState(missionId) {
        const patientRows = transportSweepOptionalReleasePatientRows();
        const eligibleVehicleIds = new Set(patientRows.keys());
        const releaseByVehicle = new Map();
        for (const control of transportSweepOptionalReleaseControls()) {
            const details = transportSweepOptionalReleaseDetails(control, patientRows);
            if (!details || !eligibleVehicleIds.has(details.vehicleId)) continue;
            const existing = releaseByVehicle.get(details.vehicleId);
            const score = (Number.isFinite(details.patientCount) ? 100 : 0) + (details.directRow ? 10 : 0);
            const existingScore = existing
                ? (Number.isFinite(existing.patientCount) ? 100 : 0) + (existing.directRow ? 10 : 0)
                : -1;
            if (!existing || score > existingScore) releaseByVehicle.set(details.vehicleId, details);
        }
        return {
            candidates: Array.from(patientRows.values()),
            eligibleVehicleIds,
            releases: Array.from(releaseByVehicle.values()),
            missionReady: transportSweepOptionalReleaseMissionReady(),
        };
    }

'''
source = source[:state_start] + new_state + source[state_end:]
source = re.sub(r"(?m)^//\s*@version\s+8\.2\.3$", "// @version      8.2.4", source, count=1)
source = source.replace("version: '8.2.3'", "version: '8.2.4'", 1)
SOURCE.write_text(source, encoding="utf-8")

# Harden the browser-faithful runtime: ILB row, duplicate clone first, and native classifier forbidden.
runtime = RUNTIME_TEST.read_text(encoding="utf-8")
runtime = runtime.replace(
    '<!doctype html><html><body><main id=mission></main></body></html>',
    '<!doctype html><html><body><div id="top-alert"></div><main id=mission></main></body></html>',
    1,
)
runtime = runtime.replace(
    "mission.innerHTML = '<table id=\"mission_vehicle_at_mission\"><tbody><tr id=\"vehicle_111\"><td>ILB (ILB)</td><td>Station</td><td>Owner</td><td class=\"actions\"></td></tr></tbody></table>';",
    "mission.innerHTML = '<table id=\"mission_vehicle_at_mission\"><tbody><tr id=\"vehicle_111\"><td><span class=\"building_list_fms building_list_fms_5\">5</span><a href=\"/vehicles/111\">ILB (ILB)</a></td><td>Station</td><td>Owner</td><td class=\"actions\"></td></tr></tbody></table>';",
    1,
)
runtime = runtime.replace(
    'mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111" data-eligible="true"><td>ILB (ILB)<br>Patient: ${names}</td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;',
    'mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111" data-eligible="true"><td><span class="building_list_fms building_list_fms_5">5</span><a href="/vehicles/111">ILB (ILB)</a><br>Patient: ${names}</td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;',
    1,
)
runtime = runtime.replace(
    '''  function injectDeferredControl() {
    const row = dom.window.document.querySelector('tr[data-eligible="true"]');
    const actions = row?.querySelector(".actions");
    if (!actions || actions.querySelector('a[href*="/patient/-1"]')) return;
    actions.innerHTML = releaseLink("111");
    actions.querySelector("a").click = () => { throw new Error("production must not use anchor.click()"); };
  }
''',
    '''  function injectDeferredControl() {
    const row = dom.window.document.querySelector('tr[data-eligible="true"]');
    const actions = row?.querySelector(".actions");
    if (!actions || actions.querySelector('a[href*="/patient/-1"]')) return;
    const topAlert = dom.window.document.querySelector("#top-alert");
    topAlert.innerHTML = releaseLink("111");
    topAlert.querySelector("a").click = () => { throw new Error("production must not use anchor.click()"); };
    actions.innerHTML = releaseLink("111");
    actions.querySelector("a").click = () => { throw new Error("production must not use anchor.click()"); };
  }
''',
    1,
)
old_sandbox = '''    collectTransportSweepVehicleCandidates() {
      return Array.from(dom.window.document.querySelectorAll('tr[data-eligible="true"]')).map(row => ({
        vehicleId: row.id.match(/\d+$/u)?.[0] || "",
      }));
    },
    async collectTransportSweepVehicleCandidatesForMission() {
      throw new Error("optional release state must not consume an async candidate Promise");
    },
'''
new_sandbox = '''    transportSweepVehicleIdFromHref(value) {
      return String(value || "").match(/\/vehicles\/(\d+)/u)?.[1] || null;
    },
    transportSweepOwnVehicleIdSet() {
      return new Set((options.ownVehicleIds || []).map(String));
    },
    collectTransportSweepVehicleCandidates() {
      throw new Error("optional release state must not consume the native ambulance-name classifier");
    },
    async collectTransportSweepVehicleCandidatesForMission() {
      throw new Error("optional release state must not consume async mission HTML recovery");
    },
'''
if old_sandbox not in runtime:
    raise RuntimeError("Unable to replace native candidate test double")
runtime = runtime.replace(old_sandbox, new_sandbox, 1)
own_test = '''
{
  const harness = createHarness([1], { immediateButton: true, ownVehicleIds: ["111"] });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.fetches.length, 0, "own patient vehicle must remain excluded");
}

'''
runtime = runtime.replace(
    'console.log("Issue #565 v8.2.3 async-candidate runtime passed: real synchronous DOM eligibility, deferred controls, completed requests and same-vehicle 3→2→1→0.");',
    own_test + 'console.log("Issue #565 v8.2.4 patient-row runtime passed: ILB eligibility, duplicate clone preference, own exclusion, delayed controls and same-vehicle 3→2→1→0.");',
    1,
)
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

static = STATIC_TEST.read_text(encoding="utf-8")
static = static.replace(r'8\.2\.3$', r'8\.2\.4$', 1)
static = static.replace("version: '8.2.3'", "version: '8.2.4'", 1)
static = static.replace(
    '        "function transportSweepOptionalReleasePatientCount(control)",',
    '        "function transportSweepOptionalReleasePatientCountFromRow(row)",\n        "function transportSweepOptionalReleasePatientRows()",\n        "function transportSweepOptionalReleaseRowVehicleId(row)",',
    1,
)
static = static.replace(
    '    assert "const candidates = collectTransportSweepVehicleCandidates();" in helper\n    assert "collectTransportSweepVehicleCandidatesForMission(missionId)" not in helper\n',
    '    assert "const patientRows = transportSweepOptionalReleasePatientRows();" in helper\n    assert "collectTransportSweepVehicleCandidates()" not in helper\n    assert "collectTransportSweepVehicleCandidatesForMission(missionId)" not in helper\n    assert "releaseByVehicle" in helper\n    assert "details.directRow" in helper\n',
    1,
)
static = static.replace("## [8.2.3] - 2026-07-28", "## [8.2.4] - 2026-07-28", 1)
static = static.replace(
    'print("Issue #565 v8.2.3 synchronous DOM eligibility contract passed.")',
    'print("Issue #565 v8.2.4 authoritative patient-row eligibility contract passed.")',
    1,
)
STATIC_TEST.write_text(static, encoding="utf-8")

CHANGELOG.write_text(
    """# Changelog\n\n## [8.2.4] - 2026-07-28\n\n### Patient Transport Sweep — all patient-bearing alliance vehicle rows\n\n- Replaced the native ambulance-name classifier in the no-reward path with authoritative rendered patient-row eligibility.\n- Processes patient-carrying ILBs and other non-ambulance vehicle types when the exact release control is present.\n- Preserves FMS 5 and own-vehicle exclusions.\n- Deduplicates row and top-alert control clones by vehicle ID and prefers the row control with a finite patient count.\n- Retains delayed readiness, completion-aware requests, same-vehicle multi-patient verification and native fallback.\n\n""" + CHANGELOG.read_text(encoding="utf-8").split("\n", 2)[2],
    encoding="utf-8",
)
DOC.write_text(
    DOC.read_text(encoding="utf-8") + "\nToolkit v8.2.4 makes the rendered patient row authoritative for optional-release eligibility. Patient-carrying ILBs and other non-ambulance vehicle types are included when they have FMS 5, patient names and the exact release control; own vehicles remain excluded. Duplicate top-alert clones are resolved back to the vehicle row and the finite row patient count is preferred.\n",
    encoding="utf-8",
)
help_text = HELP.read_text(encoding="utf-8").replace("v8.2.3", "v8.2.4")
HELP.write_text(help_text, encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.2.4"
help_manifest["toolkitVersion"] = "8.2.4"
help_manifest["runtimeGuidePatch"] = "Toolkit v8.2.4 processes every non-owned FMS 5 patient-bearing vehicle row with the exact no-reward control, including ILBs, and deduplicates cloned controls by vehicle ID."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

source_bytes = SOURCE.read_bytes()
sha = hashlib.sha256(source_bytes).hexdigest()
lines = len(source_bytes.decode("utf-8").splitlines())
for relative in ["dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{sha}  MissionChief_Map_Command_Toolkit.user.js\n{sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({"version": "8.2.4", "sha256": sha, "bytes": len(source_bytes), "lines": lines})
manifest["metadata"]["runtimeVersion"] = "8.2.4"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate.update({
    "issue": 565,
    "version": "8.2.4",
    "sourceBytes": len(source_bytes),
    "sourceLines": lines,
    "sourceSha256": sha,
    "baseline": "8.2.3",
    "scope": "Issue #565 authoritative FMS 5 patient-row eligibility, ILB support and duplicate no-reward control resolution",
})
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), lines + 250)
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + lines - old_lines
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"v8.2.4 patient-row eligibility applied: {sha}, {len(source_bytes)} bytes, {lines} lines")
