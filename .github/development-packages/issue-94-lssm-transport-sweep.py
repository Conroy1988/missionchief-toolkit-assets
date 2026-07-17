#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
AUDIT_WORKFLOW = ROOT / ".github/workflows/full-userscript-audit.yml"
FIXTURE = ROOT / ".github/fixtures/transport-sweep-lssm-contract.json"
TEST = ROOT / ".github/scripts/test_transport_sweep_lssm_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: expected one regex match, found {count}")
    return updated


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.13.9", "// @version      4.14.0", "metadata version")
source = replace_once(source, "version: '4.13.9'", "version: '4.14.0'", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4139'", "styleId: 'mc-map-command-toolkit-style-v4140'", "style id")
source = replace_once(source, "guideVersion: '4.13.9'", "guideVersion: '4.14.0'", "help guide version")
source = replace_once(
    source,
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4139__ = true;",
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4139__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4140__ = true;",
    "runtime compatibility flag",
)

vehicle_id_block = """    function transportSweepVehicleIdFromHref(href) {
        let pathname = String(href || '').trim();
        try { pathname = new URL(pathname, document.baseURI || pageWindow.location.href).pathname; } catch (err) {}
        const match = pathname.match(/^\\/vehicles\\/(\\d+)(?:\\/|$)/);
        return match ? match[1] : null;
    }
"""
release_helpers = """

    function transportSweepReleaseVehicleIdFromHref(href) {
        let pathname = String(href || '').trim();
        try { pathname = new URL(pathname, document.baseURI || pageWindow.location.href).pathname; } catch (err) {}
        const match = pathname.match(/^\\/vehicles\\/(\\d+)\\/patient\\/-1\\/?$/);
        return match ? match[1] : null;
    }

    function transportSweepOwnerProfileId(row) {
        if (!row?.querySelector) return null;
        const ownerLink = row.querySelector('td.hidden-xs a[href*="/profile/"], small.visible-xs a[href*="/profile/"]');
        const href = String(ownerLink?.getAttribute?.('href') || '');
        const match = href.match(/\\/profile\\/(\\d+)(?:\\/|$)/);
        return match ? match[1] : null;
    }
"""
source = replace_once(source, vehicle_id_block, vehicle_id_block + release_helpers, "release action helpers")

collector_block = """    function collectTransportSweepVehicleCandidates() {
        const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : null;
        let anchors = root ? transportSweepVehicleAnchorsWithin(root) : [];
        if (!anchors.length) anchors = transportSweepVisibleVehicleAnchors().filter(anchor => transportSweepAnchorBelongsToMissionWindow(anchor));

        const result = collectTransportSweepStaticCandidates(anchors, 'mission window', true);
        transportSweepRuntime.rejectedOwn = result.stats.rejectedOwn || 0;
        transportSweepRuntime.lastCandidateStats = result.stats;
        return result.candidates;
    }
"""
lssm_collector = """

    function collectTransportSweepLssmCandidates(excludedVehicleIds = null) {
        const excluded = excludedVehicleIds instanceof Set ? excludedVehicleIds : new Set();
        const ownIds = transportSweepOwnVehicleIdSet();
        const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : null;
        const anchors = [];
        const seenAnchors = new Set();
        const collectFrom = scope => {
            let matches = [];
            try { matches = Array.from(scope?.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || []); } catch (err) {}
            for (const anchor of matches) {
                if (seenAnchors.has(anchor)) continue;
                seenAnchors.add(anchor);
                anchors.push(anchor);
            }
        };
        if (root) collectFrom(root);
        if (!anchors.length) {
            for (const context of transportSweepDocumentContexts()) collectFrom(context.doc);
        }

        const unique = new Map();
        let rejectedOwn = 0;
        let rejectedAmbiguousOwner = 0;
        let rejectedNotFms5 = 0;
        for (const anchor of anchors) {
            if (!transportSweepAnchorUsable(anchor)) continue;
            const actionHref = String(anchor.getAttribute?.('href') || '').trim();
            const vehicleId = transportSweepReleaseVehicleIdFromHref(actionHref);
            if (!vehicleId || excluded.has(String(vehicleId))) continue;
            const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, [id^="vehicle_row_"]');
            if (!row?.querySelector?.('.building_list_fms_5')) {
                rejectedNotFms5 += 1;
                continue;
            }
            if (ownIds.has(String(vehicleId))) {
                rejectedOwn += 1;
                continue;
            }
            const ownerProfileId = transportSweepOwnerProfileId(row);
            if (!ownerProfileId) {
                rejectedAmbiguousOwner += 1;
                continue;
            }
            const vehicleLink = Array.from(row.querySelectorAll?.('a[href*="/vehicles/"]') || [])
                .find(item => transportSweepVehicleIdFromHref(item.getAttribute?.('href')) === String(vehicleId));
            const ownerLink = row.querySelector('td.hidden-xs a[href*="/profile/"], small.visible-xs a[href*="/profile/"]');
            const label = String(vehicleLink?.textContent || `Alliance ambulance ${vehicleId}`).trim() || `Alliance ambulance ${vehicleId}`;
            const owner = String(ownerLink?.textContent || `profile ${ownerProfileId}`).trim() || `profile ${ownerProfileId}`;
            const normalisedActionHref = `/vehicles/${vehicleId}/patient/-1`;
            if (!unique.has(normalisedActionHref)) {
                unique.set(normalisedActionHref, {
                    actionHref: normalisedActionHref,
                    vehicleId: String(vehicleId),
                    ownerProfileId,
                    owner,
                    label,
                    anchor,
                    row,
                    source: 'LSSM mission release control'
                });
            }
        }

        const candidates = Array.from(unique.values())
            .sort((a, b) => a.label.localeCompare(b.label) || Number(a.vehicleId) - Number(b.vehicleId))
            .slice(0, TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION);
        transportSweepRuntime.rejectedOwn = rejectedOwn;
        transportSweepRuntime.lastCandidateStats = {
            source: 'LSSM mission release controls',
            totalLinks: anchors.length,
            candidates: candidates.length,
            rejectedOwn,
            rejectedAmbiguousOwner,
            rejectedNotFms5
        };
        return candidates;
    }

    async function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000) {
        const first = await transportSweepWaitFor(() => {
            const candidates = collectTransportSweepLssmCandidates(excludedVehicleIds);
            return candidates.length ? candidates : null;
        }, timeoutMs, 180);
        if (!first?.length || transportSweepRuntime.stopRequested) return [];
        await transportSweepSleep(1200);
        return collectTransportSweepLssmCandidates(excludedVehicleIds);
    }

    function transportSweepReleaseConfirmationVisible() {
        const text = transportSweepVisibleWindowRoots()
            .map(root => String(root.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase())
            .join(' | ');
        return /released the patient|patient (?:is not|isn['’]t) transported|patient.*released|patient.*discharged/.test(text);
    }

    async function activateTransportSweepLssmRelease(candidate) {
        if (!candidate?.actionHref || transportSweepRuntime.stopRequested) return false;
        let anchor = candidate.anchor;
        if (!anchor?.isConnected) {
            const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : document;
            anchor = Array.from(root.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || [])
                .find(item => transportSweepReleaseVehicleIdFromHref(item.getAttribute?.('href')) === String(candidate.vehicleId));
        }
        if (!anchor?.isConnected || !transportSweepAnchorUsable(anchor)) return false;
        const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, [id^="vehicle_row_"]');
        anchor.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
        anchor.click();
        return Boolean(await transportSweepWaitFor(() => {
            if (!anchor.isConnected || !transportSweepAnchorUsable(anchor)) return true;
            if (row && (!row.isConnected || !row.querySelector?.(`a[href="${candidate.actionHref}"]`))) return true;
            return transportSweepReleaseConfirmationVisible() ? true : null;
        }, 7000, 140));
    }
"""
source = replace_once(source, collector_block, collector_block + lssm_collector, "LSSM candidate collector")

new_process = """    async function processTransportSweepMission(item, remainingAllowance) {
        const missionId = normaliseMissionId(item?.missionId);
        if (missionId === null || remainingAllowance <= 0) return 0;

        transportSweepRuntime.currentMissionId = missionId;
        renderTransportSweepPanel();

        const attemptedVehicleIds = new Set();
        let clearedHere = 0;
        let lssmSeen = false;
        let fallbackLogged = false;
        let initialScanLogged = false;
        let missionHadCandidates = false;

        while (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
            transportSweepLog(`${attemptedVehicleIds.size ? 'Reopening' : 'Opening'} ${item.caption}`);
            const opened = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
            if (!opened || transportSweepRuntime.stopRequested) break;

            const lssmCandidates = await waitForTransportSweepLssmCandidates(attemptedVehicleIds, lssmSeen ? 8000 : 18000);
            if (transportSweepRuntime.stopRequested) break;
            const lssmCandidate = lssmCandidates.find(entry => !attemptedVehicleIds.has(String(entry.vehicleId)));
            if (lssmCandidate) {
                lssmSeen = true;
                missionHadCandidates = true;
                attemptedVehicleIds.add(String(lssmCandidate.vehicleId));
                transportSweepRuntime.currentVehicleHref = lssmCandidate.actionHref;
                renderTransportSweepPanel();
                transportSweepLog(`Releasing ${lssmCandidate.label} · ${lssmCandidate.owner} · direct LSSM control`);
                try {
                    const cleared = await activateTransportSweepLssmRelease(lssmCandidate);
                    if (!cleared) throw new Error('LSSM release confirmation timed out');
                    clearedHere += 1;
                    transportSweepRuntime.cleared += 1;
                    transportSweepRuntime.processed += 1;
                    transportSweepLog(`Released ${lssmCandidate.label} for ${lssmCandidate.owner} at ${item.caption}`);
                } catch (err) {
                    transportSweepRuntime.errors += 1;
                    transportSweepLog(`Failed ${lssmCandidate.label}: ${err?.message || 'unknown error'}`, 'error');
                }
                if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
                    await transportSweepSleep(state.transportSweep.delayMs);
                }
                continue;
            }

            if (lssmSeen) {
                transportSweepLog(`No further LSSM alliance release controls remain at ${item.caption}`);
                break;
            }

            if (!fallbackLogged) {
                fallbackLogged = true;
                transportSweepLog(`LSSM release controls did not appear at ${item.caption}; using the verified vehicle-window fallback`, 'warn');
            }
            const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);
            const candidateStats = transportSweepRuntime.lastCandidateStats || {};
            if (!initialScanLogged) {
                const source = candidateStats.source ? ` · ${candidateStats.source}` : '';
                transportSweepLog(`Fallback scan: ${candidateStats.totalLinks || 0} vehicle links · ${candidateStats.allianceLinks || 0} alliance FMS 5 · ${candidateStats.candidates || 0} patient candidates${source}`);
                if (transportSweepRuntime.rejectedOwn > 0) {
                    transportSweepLog(`Ignored ${transportSweepRuntime.rejectedOwn} of your own FMS 5 vehicle${transportSweepRuntime.rejectedOwn === 1 ? '' : 's'} at ${item.caption}`);
                }
                initialScanLogged = true;
            }

            if (candidates.length) missionHadCandidates = true;
            const candidate = candidates.find(entry => !attemptedVehicleIds.has(String(entry.vehicleId)));
            if (!candidate) {
                if (!missionHadCandidates) transportSweepLog(`No alliance-owned FMS 5 patient vehicles were found inside ${item.caption}`, 'warn');
                else transportSweepLog(`Checked every alliance-owned FMS 5 patient vehicle at ${item.caption}; none exposed a release control`, 'warn');
                break;
            }

            attemptedVehicleIds.add(String(candidate.vehicleId));
            transportSweepRuntime.currentVehicleHref = candidate.href;
            renderTransportSweepPanel();
            transportSweepLog(`Fallback check: FMS 5 ${candidate.label} (${candidate.vehicleId})`);

            const vehicleResult = await openTransportSweepVehicle(candidate);
            if (transportSweepRuntime.stopRequested) break;
            const button = vehicleResult?.button || (vehicleResult?.opened ? await transportSweepWaitFor(
                () => findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline),
                3200,
                120
            ) : null);
            if (!button) {
                transportSweepLog(`${candidate.label} is carrying a patient but is not release-ready; continuing in the same mission`);
                await transportSweepSleep(350);
                continue;
            }

            try {
                button.click();
                const cleared = await transportSweepWaitFor(() => {
                    if (!button.isConnected || !transportSweepElementVisible(button) || button.disabled) return true;
                    return String(button.textContent || '').trim().toLowerCase() !== 'discharge patient' ? true : null;
                }, 5000, 140);
                if (!cleared) throw new Error('Discharge confirmation timed out');
                clearedHere += 1;
                transportSweepRuntime.cleared += 1;
                transportSweepRuntime.processed += 1;
                transportSweepLog(`Cleared ${candidate.label} at ${item.caption}`);
            } catch (err) {
                transportSweepRuntime.errors += 1;
                transportSweepLog(`Failed ${candidate.label}: ${err?.message || 'unknown error'}`, 'error');
            }

            if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
                await transportSweepSleep(state.transportSweep.delayMs);
            }
        }

        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
        return clearedHere;
    }
"""
source = regex_replace_once(
    source,
    r"    async function processTransportSweepMission\(item, remainingAllowance\) \{.*?\n    \}\n\n(?=    async function startTransportSweep\(\))",
    new_process + "\n",
    "transport sweep mission processor",
)

old_confirm = """        const confirmed = pageWindow.confirm(`Transport Sweep will use MissionChief's visible co-admin controls to attempt up to ${planned} patient discharges across ${queue.length} alliance mission${queue.length === 1 ? '' : 's'}.\n\nYour own vehicle IDs are excluded before any vehicle window is opened. The sweep will inspect each non-personal FMS 5 patient vehicle until MissionChief exposes the enabled “Discharge patient” button. Continue?`);"""
new_confirm = """        const confirmed = pageWindow.confirm(`Transport Sweep will attempt up to ${planned} alliance-member patient releases across ${queue.length} alliance mission${queue.length === 1 ? '' : 's'}.\n\nThe sweep waits dynamically for LSSM's “Release patient (No reward)” controls and processes one alliance ambulance at a time. Your own verified vehicle IDs are always excluded. If LSSM controls do not appear, the existing vehicle-window route remains available as a fallback. Continue?`);"""
source = replace_once(source, old_confirm, new_confirm, "transport sweep confirmation")
SOURCE.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.14.0] - 2026-07-17

### Added
- Upgraded Patient Transport Sweep to use LSSM's mission-level **Release patient (No reward)** controls before opening individual vehicle windows.
- The sweep waits dynamically for delayed LSSM controls, processes alliance-member ambulances sequentially, rescans after every release and supports several patient-held units in the same mission.

### Safety
- The signed-in player's verified vehicle IDs remain excluded before any release action.
- Ambiguous owner rows are skipped, duplicate mission/vehicle actions are blocked, cancellation and per-run limits remain active, and the existing vehicle-window route is retained only as a fallback when LSSM controls do not appear.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

fixture = {
    "description": "LSSM direct alliance-patient release row contract",
    "current_player_vehicle_ids": ["1111111"],
    "rows": [
        {
            "name": "alliance ambulance",
            "html": '<tr id="vehicle_row_5983835"><td><span class="building_list_fms building_list_fms_5">5</span></td><td><a href="/vehicles/5983835" vehicle_type_id="5">Ambulance</a><br>Patient: Harrison D.<small class="visible-xs">(<a href="/profile/450396">Turbotam401</a>)</small></td><td class="hidden-xs">Ballingry Ambulance station</td><td>2</td><td class="hidden-xs"><a href="/profile/450396">Turbotam401</a></td><td><div class="btn-group"><a class="btn btn-default btn-xs" href="/vehicles/5983835/patient/-1">Release patient (No reward)</a></div></td></tr>',
            "vehicle_id": "5983835",
            "owner_profile_id": "450396",
            "eligible": True,
        },
        {
            "name": "own ambulance",
            "html": '<tr id="vehicle_row_1111111"><td><span class="building_list_fms building_list_fms_5">5</span></td><td><a href="/vehicles/1111111" vehicle_type_id="5">Ambulance</a><br>Patient: Example</td><td class="hidden-xs"><a href="/profile/27301455">Conroy1988</a></td><td><a href="/vehicles/1111111/patient/-1">Release patient (No reward)</a></td></tr>',
            "vehicle_id": "1111111",
            "owner_profile_id": "27301455",
            "eligible": False,
        },
    ],
}
FIXTURE.parent.mkdir(parents=True, exist_ok=True)
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

TEST.write_text('''#!/usr/bin/env python3
"""Verify the LSSM alliance-patient release contract and source wiring."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/transport-sweep-lssm-contract.json"


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    own_ids = set(data["current_player_vehicle_ids"])
    for row in data["rows"]:
        html = row["html"]
        action = re.search(r'href="/vehicles/(\\d+)/patient/-1"', html)
        owner = re.search(r'href="/profile/(\\d+)"', html)
        fms5 = "building_list_fms_5" in html
        assert action and action.group(1) == row["vehicle_id"], row["name"]
        assert owner and owner.group(1) == row["owner_profile_id"], row["name"]
        eligible = bool(fms5 and action.group(1) not in own_ids and owner.group(1))
        assert eligible is row["eligible"], row["name"]

    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "function transportSweepReleaseVehicleIdFromHref(href)",
        "/patient\\/-1",
        "function transportSweepOwnerProfileId(row)",
        "function collectTransportSweepLssmCandidates(excludedVehicleIds = null)",
        "function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000)",
        "function activateTransportSweepLssmRelease(candidate)",
        "LSSM mission release controls",
        "rejectedAmbiguousOwner",
        "ownIds.has(String(vehicleId))",
        "attemptedVehicleIds.add(String(lssmCandidate.vehicleId))",
        "await collectTransportSweepVehicleCandidatesForMission(missionId)",
        "existing vehicle-window route remains available as a fallback",
    ]
    missing = [item for item in required if item not in source]
    assert not missing, f"Missing LSSM transport sweep contract markers: {missing}"
    print("LSSM transport sweep contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")

preflight = PREFLIGHT.read_text(encoding="utf-8")
preflight = replace_once(
    preflight,
    "  .github/scripts/test_mission_value_contract.py\n)",
    "  .github/scripts/test_mission_value_contract.py\n  .github/scripts/test_transport_sweep_lssm_contract.py\n)",
    "preflight contract registration",
)
PREFLIGHT.write_text(preflight, encoding="utf-8")

audit = AUDIT_WORKFLOW.read_text(encoding="utf-8")
audit = replace_once(
    audit,
    '      - ".github/fixtures/desktop-panel-layout-contract.json"\n',
    '      - ".github/fixtures/desktop-panel-layout-contract.json"\n      - ".github/fixtures/transport-sweep-lssm-contract.json"\n',
    "audit fixture path",
)
audit = replace_once(
    audit,
    '      - ".github/scripts/test_mission_value_contract.py"\n',
    '      - ".github/scripts/test_mission_value_contract.py"\n      - ".github/scripts/test_transport_sweep_lssm_contract.py"\n',
    "audit test path",
)
AUDIT_WORKFLOW.write_text(audit, encoding="utf-8")

subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Issue #94 LSSM transport sweep package applied successfully")
