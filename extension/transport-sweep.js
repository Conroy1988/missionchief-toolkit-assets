// @section hydrate
    async function hydrateTransportSweepMobileMissions() {
        const all = Array.from(missionProgressPageMissionRecords.values()).filter(record =>
            record.ownership === 'alliance' && (record.patientSignal || Number(record.patientsCount) > 0
                || transportRequirementFromSnapshot(record)?.type === 'patient'));
        all.sort((a, b) => (a.createdAt || Number.MAX_SAFE_INTEGER) - (b.createdAt || Number.MAX_SAFE_INTEGER));
        // Finite snapshot, four requests at most in flight. Continue past the old
        // first-80 cutoff rather than silently leaving the same tail unchecked.
        const candidates = all;
        const stats = {candidates: all.length, checked: 0, failed: 0, found: 0, capped: 0, vehicleLinks: 0, fms5Rows: 0, patientVehicles: 0, shellPages: 0};
        transportSweepRuntime.discovery = stats;
        let cursor = 0;
        const worker = async () => {
            while (cursor < candidates.length && !runtime.destroyed && !transportSweepRuntime.stopRequested) {
                const record = candidates[cursor++];
                let fetched = null;
                try { fetched = await transportSweepFetchMissionDocument(record.missionId); } catch {}
                // A login/error document must not become evidence that transport is absent.
                const doc = fetched?.doc;
                const anchors = Array.from(doc?.querySelectorAll('a[href*="/vehicles/"]') || []);
                const nativeCandidates = doc ? collectTransportSweepStaticCandidates(anchors, 'mission scan') : {candidates: []};
                stats.vehicleLinks += anchors.length;
                stats.fms5Rows += doc?.querySelectorAll('.building_list_fms_5').length || 0;
                stats.patientVehicles += nativeCandidates.candidates.length;
                if (!doc?.querySelector('#missionH1, #mission_vehicle_at_mission, #missing_text, .mission_patient, [data-transport-request]')) {
                    stats.failed += 1;
                } else {
                    let snapshot = transportSweepSnapshotFromMissionDocument(doc, record);
                    // The release path already accepts a non-owned FMS-5 patient
                    // vehicle. Do not additionally demand a duplicate green link.
                    if (nativeCandidates.candidates.length) snapshot = {...record,
                        patientsCount: nativeCandidates.candidates.length, prisonersCount: 0,
                        missingText: `Patient transport required (${nativeCandidates.candidates.length})`, missingTextKnown: true};
                    if (!snapshot && !doc.querySelector('#mission_vehicle_at_mission, #missing_text, .mission_patient, [data-transport-request]')) {
                        stats.shellPages += 1;
                        stats.failed += 1;
                    } else {
                    missionProgressPageMissionRecords.set(String(record.missionId), {
                        ...record, ...(snapshot || {patientsCount: 0, prisonersCount: 0, missingText: '', missingTextKnown: true}),
                        transportVerified: true
                    });
                    if (snapshot) stats.found += 1;
                    }
                }
                stats.checked += 1;
                if (stats.checked === candidates.length || stats.checked % 10 === 0) {
                    transportSweepLog(`Checked ${stats.checked}/${candidates.length} alliance patient missions · ${stats.found} transport missions found · ${stats.failed} unavailable`);
                }
            }
        };
        await Promise.all(Array.from({length: Math.min(TRANSPORT_SWEEP_MOBILE_DISCOVERY_CONCURRENCY, candidates.length)}, worker));
        stats.unchecked = all.length - stats.checked;
        transportSweepLog(`Scan evidence: ${stats.vehicleLinks} vehicle links · ${stats.fms5Rows} status-5 entries · ${stats.patientVehicles} eligible patient vehicles · ${stats.shellPages} incomplete page shells`);
        return stats.found;
    }

// @section fetch
    async function transportSweepFetchMissionDocument(missionId) {
        const id = normaliseMissionId(missionId);
        if (id === null || transportSweepRuntime.stopRequested) return null;
        let best = null;
        let bestScore = -1;
        const modes = [
            {'X-Requested-With': 'XMLHttpRequest', Accept: 'text/html, */*;q=0.8'},
            {Accept: 'text/html,application/xhtml+xml'}
        ];
        for (const headers of modes) {
            if (transportSweepRuntime.stopRequested || runtime.destroyed) break;
            try {
                const response = await runtimeFetch(`/missions/${id}`, {method: 'GET', credentials: 'same-origin', cache: 'no-store', headers,
                    timeoutMs: TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS});
                if (!response.ok) continue;
                if (response.url) {
                    const finalUrl = new URL(response.url, pageWindow.location.origin);
                    if (finalUrl.origin !== pageWindow.location.origin || !new RegExp(`^/missions/${id}/?$`).test(finalUrl.pathname)) continue;
                }
                const html = await response.text();
                if (!html || html.length < 100) continue;
                const doc = new DOMParser().parseFromString(html, 'text/html');
                if (!doc.querySelector('#missionH1, #mission_vehicle_at_mission, #missing_text, .mission_patient, [data-transport-request]')) continue;
                const score = doc.querySelectorAll('.building_list_fms_5').length * 10
                    + doc.querySelectorAll('a[href*="/vehicles/"]').length
                    + doc.querySelectorAll('#missing_text, .mission_patient, #mission_vehicle_at_mission').length;
                if (score > bestScore) { best = {doc, htmlLength: html.length}; bestScore = score; }
                if (doc.querySelector('.building_list_fms_5')) break;
            } catch (error) {
                if (error?.name === 'AbortError' && transportSweepRuntime.stopRequested) break;
            }
        }
        return best;
    }

// @section records
    function transportSweepMissionRecords(now = Date.now()) {
        const records = [];
        const seen = new Set();
        for (const marker of getMissionMarkerIndex().markers) {
            const missionId = missionIdFromMarker(marker);
            if (missionId === null || seen.has(missionId)) continue;
            seen.add(missionId);
            const verified = missionProgressPageMissionRecords.get(String(missionId));
            const snapshot = verified?.transportVerified ? verified : liveMissionSnapshots.get(missionId) || missionSnapshotFromMarker(marker, now);
            if (snapshot) records.push({missionId, marker, snapshot, fallback: false});
        }
        for (const missionId of transportSweepFallbackMissionIds(now)) {
            if (seen.has(missionId)) continue;
            seen.add(missionId);
            const snapshot = transportSweepSnapshotFromOverlay(missionId);
            if (snapshot) records.push({missionId, marker: null, snapshot, fallback: true});
        }
        return records;
    }

// @section scan
    async function scanTransportSweepQueue() {
        if (transportSweepRuntime.scanPromise) return transportSweepRuntime.scanPromise;
        const scanPromise = Promise.resolve().then(async () => {
            transportSweepRuntime.stopRequested = false;
            scanInlineMissionMarkerData(true);
            let records = captureTransportSweepMissionListDataFromDocument(document);
            let refreshed = false;
            if (!records.size) {
                transportSweepLog('Refreshing the current mission list for transport discovery');
                refreshed = await refreshMissionProgressFromPage(true, 5000);
                if (refreshed) records = new Map(missionProgressPageMissionRecords);
            }
            const now = Date.now();
            for (const marker of getMissionMarkerIndex().markers) {
                const id = missionIdFromMarker(marker);
                if (id === null || isPersonalMissionLayer(marker, id)) continue;
                const snapshot = missionSnapshotFromMarker(marker, now) || liveMissionSnapshots.get(id);
                if (!snapshot) continue;
                const previous = records.get(String(id));
                if (previous?.ownership === 'personal') continue;
                records.set(String(id), {...snapshot, ...previous, missionId: String(id), ownership: 'alliance',
                    patientSignal: Boolean(previous?.patientSignal || Number(snapshot.patientsCount) > 0
                        || transportRequirementFromSnapshot(snapshot)?.type === 'patient')});
            }
            // Each deliberate scan gets fresh evidence; do not retain prior verified negatives.
            for (const record of records.values()) delete record.transportVerified;
            missionProgressPageMissionRecords = records;
            missionProgressPageMissionIds = new Set(records.keys());
            missionProgressPageLastSuccessAt = now;
            await hydrateTransportSweepMobileMissions();
            const queue = buildTransportSweepQueue();
            const stats = transportSweepRuntime.discovery;
            const incomplete = stats.failed + stats.unchecked;
            if (!records.size && !refreshed) {
                transportSweepLog('Scan incomplete: no current mission data could be read. Reload MissionChief and scan again.', 'warn');
            } else if (incomplete) {
                transportSweepLog(`Scan incomplete: ${queue.length} transport missions found; ${stats.failed} unavailable and ${stats.unchecked} unchecked.${stats.capped ? ' The bounded mission-page scan limit was reached.' : ' Retry the scan to check unavailable missions.'}`, 'warn');
            } else {
                transportSweepLog(queue.length
                    ? `Scan complete: ${queue.length} alliance patient transport mission${queue.length === 1 ? '' : 's'} ready`
                    : 'Scan complete: no active alliance patient transports found', queue.length ? 'info' : 'warn');
            }
            return queue;
        });
        transportSweepRuntime.scanPromise = scanPromise;
        renderTransportSweepPanel();
        try { return await scanPromise; }
        finally {
            if (transportSweepRuntime.scanPromise === scanPromise) transportSweepRuntime.scanPromise = null;
            renderTransportSweepPanel();
        }
    }
