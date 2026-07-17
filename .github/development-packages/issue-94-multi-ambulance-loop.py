#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
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
source = replace_once(source, "// @version      4.14.0", "// @version      4.14.1", "metadata version")
source = replace_once(source, "version: '4.14.0'", "version: '4.14.1'", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4140'", "styleId: 'mc-map-command-toolkit-style-v4141'", "style id")
source = replace_once(source, "guideVersion: '4.14.0'", "guideVersion: '4.14.1'", "help guide version")
source = replace_once(
    source,
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4140__ = true;",
    "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4140__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4141__ = true;",
    "runtime compatibility flag",
)

new_activation = r'''    async function activateTransportSweepLssmRelease(candidate) {
        if (!candidate?.actionHref || transportSweepRuntime.stopRequested) return false;
        let anchor = candidate.anchor;
        if (!anchor?.isConnected) {
            const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : document;
            anchor = Array.from(root.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || [])
                .find(item => transportSweepReleaseVehicleIdFromHref(item.getAttribute?.('href')) === String(candidate.vehicleId));
        }
        if (!anchor?.isConnected || !transportSweepAnchorUsable(anchor)) return false;
        const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, [id^="vehicle_row_"]');
        const rowId = String(row?.id || `vehicle_row_${candidate.vehicleId}`);
        const ownerDocument = anchor.ownerDocument || document;
        const clickedAt = Date.now();
        anchor.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
        anchor.click();
        return Boolean(await transportSweepWaitFor(() => {
            if (transportSweepReleaseConfirmationVisible()) return true;
            if (Date.now() - clickedAt < 900) return null;
            const liveRow = ownerDocument.getElementById?.(rowId) || null;
            if (!liveRow) return null;
            const liveAction = Array.from(liveRow.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || [])
                .find(item => transportSweepReleaseVehicleIdFromHref(item.getAttribute?.('href')) === String(candidate.vehicleId));
            const stillFms5 = Boolean(liveRow.querySelector?.('.building_list_fms_5'));
            const stillPatient = /\bpatient\s*:/i.test(String(liveRow.textContent || ''));
            return !liveAction && (!stillFms5 || !stillPatient) ? true : null;
        }, 10000, 140));
    }
'''
source = regex_replace_once(
    source,
    r"    async function activateTransportSweepLssmRelease\(candidate\) \{.*?\n    \}\n\n(?=    function transportSweepVisibleDischargeButtons\(\))",
    new_activation + "\n",
    "LSSM release confirmation",
)

new_process = r'''    async function processTransportSweepMission(item, remainingAllowance) {
        const missionId = normaliseMissionId(item?.missionId);
        if (missionId === null || remainingAllowance <= 0) return 0;

        transportSweepRuntime.currentMissionId = missionId;
        renderTransportSweepPanel();

        const attemptedVehicleIds = new Set();
        let clearedHere = 0;
        let lssmSeen = false;
        let fallbackMode = false;
        let fallbackLogged = false;
        let initialScanLogged = false;
        let missionHadCandidates = false;

        transportSweepLog(`Opening ${item.caption}`);
        let missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
        if (!missionOpen || transportSweepRuntime.stopRequested) {
            if (!transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
            return 0;
        }

        while (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
            if (!fallbackMode) {
                const lssmCandidates = await waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000);
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
                        transportSweepLog(`Returning to ${item.caption} for remaining alliance ambulances`);
                        missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
                        if (!missionOpen) {
                            transportSweepRuntime.errors += 1;
                            transportSweepLog(`Could not return to ${item.caption} after releasing ${lssmCandidate.label}`, 'error');
                            break;
                        }
                    }
                    continue;
                }

                if (lssmSeen) {
                    transportSweepLog(`No further LSSM alliance release controls remain at ${item.caption}`);
                    break;
                }
                fallbackMode = true;
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
                transportSweepLog(`${candidate.label} is carrying a patient but is not transport-ready; continuing in the same mission`);
            } else {
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
            }

            if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
                await transportSweepSleep(state.transportSweep.delayMs);
                transportSweepLog(`Returning to ${item.caption} for remaining alliance ambulances`);
                missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
                if (!missionOpen) {
                    transportSweepRuntime.errors += 1;
                    transportSweepLog(`Could not return to ${item.caption} during fallback processing`, 'error');
                    break;
                }
            }
        }

        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
        return clearedHere;
    }
'''
source = regex_replace_once(
    source,
    r"    async function processTransportSweepMission\(item, remainingAllowance\) \{.*?\n    \}\n\n(?=    async function startTransportSweep\(\))",
    new_process + "\n",
    "multi-ambulance mission processor",
)
SOURCE.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.14.1] - 2026-07-17

### Fixed
- Corrected Patient Transport Sweep so a mission containing several alliance-member ambulances is explicitly reopened after every confirmed release.
- The sweep now waits for release completion before returning to the mission, rescans the fresh mission DOM for the next delayed LSSM control and repeats until no eligible alliance controls remain.

### Safety
- Own-vehicle exclusion, ambiguous-owner rejection, sequential processing, duplicate protection, cancellation, per-run limits and the non-LSSM fallback remain unchanged.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture["description"] = "LSSM direct alliance-patient release and multi-ambulance loop contract"
existing = {row.get("vehicle_id") for row in fixture.get("rows", [])}
for vehicle_id, owner_id, owner_name in [
    ("5983836", "450397", "AllianceTwo"),
    ("5983837", "450398", "AllianceThree"),
]:
    if vehicle_id in existing:
        continue
    fixture["rows"].append({
        "name": f"alliance ambulance {vehicle_id}",
        "html": f'<tr id="vehicle_row_{vehicle_id}"><td><span class="building_list_fms building_list_fms_5">5</span></td><td><a href="/vehicles/{vehicle_id}" vehicle_type_id="5">Ambulance</a><br>Patient: Example</td><td class="hidden-xs"><a href="/profile/{owner_id}">{owner_name}</a></td><td><a href="/vehicles/{vehicle_id}/patient/-1">Release patient (No reward)</a></td></tr>',
        "vehicle_id": vehicle_id,
        "owner_profile_id": owner_id,
        "eligible": True,
    })
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
test = replace_once(
    test,
    '    source = SOURCE.read_text(encoding="utf-8")\n',
    '    eligible_rows = [row for row in data["rows"] if row["eligible"]]\n    assert len(eligible_rows) >= 3, "multi-ambulance fixture must contain at least three eligible alliance rows"\n    assert len({row["vehicle_id"] for row in eligible_rows}) == len(eligible_rows), "eligible alliance vehicle IDs must be unique"\n\n    source = SOURCE.read_text(encoding="utf-8")\n',
    "multi-ambulance fixture assertions",
)
test = replace_once(
    test,
    '        "existing vehicle-window route remains available as a fallback",\n',
    '        "existing vehicle-window route remains available as a fallback",\n        "Returning to ${item.caption} for remaining alliance ambulances",\n        "missionOpen = await openTransportSweepPath(`/missions/${missionId}`, \'mission\');",\n        "if (transportSweepReleaseConfirmationVisible()) return true;",\n',
    "source contract markers",
)
test = replace_once(
    test,
    '    missing = [item for item in required if item not in source]\n',
    '    processor = re.search(r"async function processTransportSweepMission\\(item, remainingAllowance\\) \\{([\\s\\S]*?)\\n    \\}\\n\\n    async function startTransportSweep", source)\n    assert processor, "transport sweep mission processor is missing"\n    processor_text = processor.group(1)\n    release_index = processor_text.index("transportSweepRuntime.cleared += 1")\n    return_index = processor_text.index("Returning to ${item.caption} for remaining alliance ambulances", release_index)\n    reopen_index = processor_text.index("missionOpen = await openTransportSweepPath(`/missions/${missionId}`, \'mission\');", return_index)\n    assert release_index < return_index < reopen_index, "successful releases must explicitly return to the same mission before the next scan"\n    assert "waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000)" in processor_text, "every direct-control scan must allow the full LSSM delay"\n\n    missing = [item for item in required if item not in source]\n',
    "processor sequence assertions",
)
TEST.write_text(test, encoding="utf-8")

subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"], cwd=ROOT, check=True)
print("Issue #94 critical multi-ambulance loop correction applied successfully")
