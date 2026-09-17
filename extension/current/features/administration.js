(() => {const seed=window.__MCMS_EXTENSION_SEED__||window.__MCMS_EXTENSION_PILOT__?.documentIdentity;if(!seed||(seed.documentToken&&(location.origin!==seed.origin||document.documentElement.getAttribute('data-mcms-extension-document')!==seed.documentToken)))return;
(()=>{'use strict';window.__MCMS_EXTENSION_FEATURES__ ||= Object.create(null);window.__MCMS_EXTENSION_FEATURES__["administration"] ||= {"transportSweepWaitFor":__mcmsModuleContext=>(async function transportSweepWaitFor(test, timeoutMs = 5000, intervalMs = 120) {
        const started = __mcmsModuleContext.Date.now();
        while (__mcmsModuleContext.Date.now() - started < timeoutMs) {
        if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.transportSweepRuntime.stopRequested) return null;
        try {
            const value = test();
            if (value) return value;
        } catch (err) {}
        if (!await (0,__mcmsModuleContext.transportSweepSleep)(intervalMs)) return null;
        }
        return null;
    }),
"hydrateTransportSweepMobileMissions":__mcmsModuleContext=>(async function hydrateTransportSweepMobileMissions() {
        const all = __mcmsModuleContext.Array.from(__mcmsModuleContext.missionProgressPageMissionRecords.values()).filter(record =>
            record.ownership === 'alliance' && (record.patientSignal || (0,__mcmsModuleContext.Number)(record.patientsCount) > 0
                || (0,__mcmsModuleContext.transportRequirementFromSnapshot)(record)?.type === 'patient'));
        all.sort((a, b) => (a.createdAt || __mcmsModuleContext.Number.MAX_SAFE_INTEGER) - (b.createdAt || __mcmsModuleContext.Number.MAX_SAFE_INTEGER));
        // Finite snapshot, four requests at most in flight. Continue past the old
        // first-80 cutoff rather than silently leaving the same tail unchecked.
        const owner=String((0,__mcmsModuleContext.currentMissionUserId)()||'');
        const rt=__mcmsModuleContext.transportSweepRuntime;
        if(!owner||rt.discoveryCache?.owner!==owner)rt.discoveryCache={owner,rows:new Map()};
        const cache=rt.discoveryCache.rows,now=Date.now();
        const fingerprint=r=>JSON.stringify([r.createdAt,r.patientsCount,r.prisonersCount,r.missingText,r.patientSignal]);
        const currentIds=new Set(all.map(r=>String(r.missionId)));
        for(const id of cache.keys())if(!currentIds.has(id))cache.delete(id);
        let reused=0;
        const candidates=all.filter(record=>{
            const hit=cache.get(String(record.missionId));
            if(owner&&hit&&hit.expires>now&&hit.fingerprint===fingerprint(record)){
                __mcmsModuleContext.missionProgressPageMissionRecords.set(String(record.missionId),{...record,...hit.snapshot,transportVerified:true});reused++;return false;
            }
            return true;
        });
        // Surface existing evidence immediately; uncertain missions are still scanned.
        (0,__mcmsModuleContext.buildTransportSweepQueue)();
        const stats = {reused, candidates: candidates.length, checked: 0, failed: 0, found: 0, capped: 0, vehicleLinks: 0, fms5Rows: 0, patientVehicles: 0, shellPages: 0};
        __mcmsModuleContext.transportSweepRuntime.discovery = stats;
        let cursor = 0;
        const worker = async () => {
            while (cursor < candidates.length && !__mcmsModuleContext.runtime.destroyed && !__mcmsModuleContext.transportSweepRuntime.stopRequested) {
                const record = candidates[cursor++];
                let fetched = null;
                try { fetched = await (0,__mcmsModuleContext.transportSweepFetchMissionDocument)(record.missionId, {fresh:false}); } catch {}
                // A login/error document must not become evidence that transport is absent.
                const doc = fetched?.doc;
                const anchors = __mcmsModuleContext.Array.from(doc?.querySelectorAll('a[href*="/vehicles/"]') || []);
                const nativeCandidates = doc ? (0,__mcmsModuleContext.collectTransportSweepStaticCandidates)(anchors, 'mission scan') : {candidates: []};
                stats.vehicleLinks += anchors.length;
                stats.fms5Rows += doc?.querySelectorAll('.building_list_fms_5').length || 0;
                stats.patientVehicles += nativeCandidates.candidates.length;
                if (!doc?.querySelector('#missionH1, #mission_vehicle_at_mission, #missing_text, .mission_patient, [data-transport-request]')) {
                    stats.failed += 1;
                } else {
                    let snapshot = (0,__mcmsModuleContext.transportSweepSnapshotFromMissionDocument)(doc, record);
                    // The release path already accepts a non-owned FMS-5 patient
                    // vehicle. Do not additionally demand a duplicate green link.
                    if (nativeCandidates.candidates.length) snapshot = {...record,
                        patientsCount: nativeCandidates.candidates.length, prisonersCount: 0,
                        missingText: `Patient transport required (${nativeCandidates.candidates.length})`, missingTextKnown: true};
                    if (!snapshot && !doc.querySelector('#mission_vehicle_at_mission, #missing_text, .mission_patient, [data-transport-request]')) {
                        stats.shellPages += 1;
                        stats.failed += 1;
                    } else {
                    __mcmsModuleContext.missionProgressPageMissionRecords.set((0,__mcmsModuleContext.String)(record.missionId), {
                        ...record, ...(snapshot || {patientsCount: 0, prisonersCount: 0, missingText: '', missingTextKnown: true}),
                        transportVerified: true
                    });
                    const verified=__mcmsModuleContext.missionProgressPageMissionRecords.get(String(record.missionId));
                    cache.set(String(record.missionId),{fingerprint:fingerprint(record),snapshot:verified,expires:Date.now()+(snapshot?15000:5000)});
                    if (snapshot) stats.found += 1;
                    }
                }
                stats.checked += 1;
                (0,__mcmsModuleContext.buildTransportSweepQueue)();
                if(typeof __mcmsModuleContext.pilot !== 'undefined' && __mcmsModuleContext.pilot.job){
                    __mcmsModuleContext.Object.assign(__mcmsModuleContext.pilot.job,{checked:stats.checked,total:candidates.length,found:stats.found});
                    if(stats.checked%10===0||stats.checked===candidates.length) await (0,__mcmsModuleContext.pilotCall)({...__mcmsModuleContext.pilot.job,action:'update'}).promise.catch(()=>{__mcmsModuleContext.transportSweepRuntime.stopRequested=true;});
                }
                // Yield between parsed documents so the page can paint during a large scan.
                if(typeof __mcmsModuleContext.requestAnimationFrame==='function' && !__mcmsModuleContext.document.hidden) await new __mcmsModuleContext.Promise(resolve=>(0,__mcmsModuleContext.setTimeout)(resolve,0));
                if (stats.checked === candidates.length || stats.checked % 10 === 0) {
                    (0,__mcmsModuleContext.transportSweepLog)(`Checked ${stats.checked}/${candidates.length} alliance patient missions · ${stats.found} transport missions found · ${stats.failed} unavailable`);
                }
            }
        };
        await __mcmsModuleContext.Promise.all(__mcmsModuleContext.Array.from({length: __mcmsModuleContext.Math.min(__mcmsModuleContext.TRANSPORT_SWEEP_MOBILE_DISCOVERY_CONCURRENCY, candidates.length)}, worker));
        stats.unchecked = candidates.length - stats.checked;
        (0,__mcmsModuleContext.transportSweepLog)(`Scan evidence: ${stats.vehicleLinks} vehicle links · ${stats.fms5Rows} status-5 entries · ${stats.patientVehicles} eligible patient vehicles · ${stats.shellPages} incomplete page shells`);
        (0,__mcmsModuleContext.transportSweepLog)(`Discovery: ${reused} recent results reused · ${stats.checked} fetched · ${stats.failed} unavailable`);
        return stats.found;
    }),
"scanTransportSweepQueue":__mcmsModuleContext=>(async function scanTransportSweepQueue({force=false} = {}) {
        if (__mcmsModuleContext.transportSweepRuntime.scanPromise) return __mcmsModuleContext.transportSweepRuntime.scanPromise;
        const scanPromise = __mcmsModuleContext.Promise.resolve().then(async () => {
            __mcmsModuleContext.transportSweepRuntime.stopRequested = false;
            if(force){__mcmsModuleContext.transportSweepRuntime.discoveryCache=null;if(typeof __mcmsModuleContext.pilotCall==='function')await (0,__mcmsModuleContext.pilotCall)({op:'clearReadCache'}).promise;}
            (0,__mcmsModuleContext.scanInlineMissionMarkerData)(true);
            let records = (0,__mcmsModuleContext.captureTransportSweepMissionListDataFromDocument)(__mcmsModuleContext.document);
            let refreshed = false;
            if (!records.size) {
                (0,__mcmsModuleContext.transportSweepLog)('Refreshing the current mission list for transport discovery');
                refreshed = await (0,__mcmsModuleContext.refreshMissionProgressFromPage)(true, 5000);
                if (refreshed) records = new __mcmsModuleContext.Map(__mcmsModuleContext.missionProgressPageMissionRecords);
            }
            const now = __mcmsModuleContext.Date.now();
            for (const marker of (0,__mcmsModuleContext.getMissionMarkerIndex)().markers) {
                const id = (0,__mcmsModuleContext.missionIdFromMarker)(marker);
                if (id === null || (0,__mcmsModuleContext.isPersonalMissionLayer)(marker, id)) continue;
                const snapshot = (0,__mcmsModuleContext.missionSnapshotFromMarker)(marker, now) || __mcmsModuleContext.liveMissionSnapshots.get(id);
                if (!snapshot) continue;
                const previous = records.get((0,__mcmsModuleContext.String)(id));
                if (previous?.ownership === 'personal') continue;
                records.set((0,__mcmsModuleContext.String)(id), {...snapshot, ...previous, missionId: (0,__mcmsModuleContext.String)(id), ownership: 'alliance',
                    patientSignal: (0,__mcmsModuleContext.Boolean)(previous?.patientSignal || (0,__mcmsModuleContext.Number)(snapshot.patientsCount) > 0
                        || (0,__mcmsModuleContext.transportRequirementFromSnapshot)(snapshot)?.type === 'patient')});
            }
            // Each deliberate scan gets fresh evidence; do not retain prior verified negatives.
            for (const record of records.values()) delete record.transportVerified;
            __mcmsModuleContext.missionProgressPageMissionRecords = records;
            __mcmsModuleContext.missionProgressPageMissionIds = new __mcmsModuleContext.Set(records.keys());
            __mcmsModuleContext.missionProgressPageLastSuccessAt = now;
            (0,__mcmsModuleContext.buildTransportSweepQueue)();
            await (0,__mcmsModuleContext.hydrateTransportSweepMobileMissions)();
            const queue = (0,__mcmsModuleContext.buildTransportSweepQueue)();
            const stats = __mcmsModuleContext.transportSweepRuntime.discovery;
            const incomplete = stats.failed + stats.unchecked;
            if (!records.size && !refreshed) {
                (0,__mcmsModuleContext.transportSweepLog)('Scan incomplete: no current mission data could be read. Reload MissionChief and scan again.', 'warn');
            } else if (incomplete) {
                (0,__mcmsModuleContext.transportSweepLog)(`Scan incomplete: ${queue.length} transport missions found; ${stats.failed} unavailable and ${stats.unchecked} unchecked.${stats.capped ? ' The bounded mission-page scan limit was reached.' : ' Retry the scan to check unavailable missions.'}`, 'warn');
            } else {
                (0,__mcmsModuleContext.transportSweepLog)(queue.length
                    ? `Scan complete: ${queue.length} alliance patient transport mission${queue.length === 1 ? '' : 's'} ready`
                    : 'Scan complete: no active alliance patient transports found', queue.length ? 'info' : 'warn');
            }
            return queue;
        });
        __mcmsModuleContext.transportSweepRuntime.scanPromise = scanPromise;
        (0,__mcmsModuleContext.renderTransportSweepPanel)();
        try { return await scanPromise; }
        finally {
            if (__mcmsModuleContext.transportSweepRuntime.scanPromise === scanPromise) __mcmsModuleContext.transportSweepRuntime.scanPromise = null;
            (0,__mcmsModuleContext.renderTransportSweepPanel)();
        }
    }),
"transportSweepFetchMissionDocument":__mcmsModuleContext=>(async function transportSweepFetchMissionDocument(missionId, {fresh = true} = {}) {
        const id = (0,__mcmsModuleContext.normaliseMissionId)(missionId);
        if (id === null || __mcmsModuleContext.transportSweepRuntime.stopRequested) return null;
        let best = null;
        let bestScore = -1;
        const modes = [
            {'X-Requested-With': 'XMLHttpRequest', Accept: 'text/html, */*;q=0.8'},
            {Accept: 'text/html,application/xhtml+xml'}
        ];
        for (const headers of modes) {
            if (__mcmsModuleContext.transportSweepRuntime.stopRequested || __mcmsModuleContext.runtime.destroyed) break;
            try {
                let html;
                if (typeof __mcmsModuleContext.pilotCall === 'function') {
                    const response = await (0,__mcmsModuleContext.pilotCall)({op:'gameRead',missionId:id,mode:headers['X-Requested-With']?'ajax':'full',fresh}).promise;
                    html=response.html;
                } else {
                    const response = await (0,__mcmsModuleContext.runtimeFetch)(`/missions/${id}`, {method:'GET',credentials:'same-origin',cache:'no-store',headers,timeoutMs:__mcmsModuleContext.TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS});
                    if(!response.ok)continue;
                    if(response.url){const url=new __mcmsModuleContext.URL(response.url,__mcmsModuleContext.pageWindow.location.origin);if(url.origin!==__mcmsModuleContext.pageWindow.location.origin||!new __mcmsModuleContext.RegExp(`^/missions/${id}/?$`).test(url.pathname))continue;}
                    html=await response.text();
                }
                if (!html || html.length < 100) continue;
                const doc = new __mcmsModuleContext.DOMParser().parseFromString(html, 'text/html');
                if (!doc.querySelector('#missionH1, #mission_vehicle_at_mission, #missing_text, .mission_patient, [data-transport-request]')) continue;
                const score = doc.querySelectorAll('.building_list_fms_5').length * 10
                    + doc.querySelectorAll('a[href*="/vehicles/"]').length
                    + doc.querySelectorAll('#missing_text, .mission_patient, #mission_vehicle_at_mission').length;
                if (score > bestScore) { best = {doc, htmlLength: html.length}; bestScore = score; }
                const completeVehicleList=doc.querySelector('#mission_vehicle_at_mission')
                    && !doc.querySelector('#load_all_vehicles, [data-load-vehicles], a[href*="load_all_vehicles"]')
                    && !/load (?:all|more|additional) vehicles/i.test(doc.querySelector('#mission_vehicle_at_mission').textContent||'');
                if (doc.querySelector('.building_list_fms_5') || completeVehicleList) break;
            } catch (error) {
                if (error?.name === 'AbortError' && __mcmsModuleContext.transportSweepRuntime.stopRequested) break;
            }
        }
        return best;
    }),
"transportSweepFetchMissionCandidates":__mcmsModuleContext=>(async function transportSweepFetchMissionCandidates(missionId) {
        const fetched = await (0,__mcmsModuleContext.transportSweepFetchMissionDocument)(missionId);
        if (!fetched?.doc) return null;
        const anchors = __mcmsModuleContext.Array.from(fetched.doc.querySelectorAll('a[href*="/vehicles/"]'))
            .filter(anchor => (0,__mcmsModuleContext.transportSweepVehicleIdFromHref)(anchor.getAttribute('href')));
        const result = { ...(0,__mcmsModuleContext.collectTransportSweepStaticCandidates)(anchors, 'mission HTML'), htmlLength: fetched.htmlLength };
        return result;
    }),
"transportSweepFetchBackgroundCancelAction":__mcmsModuleContext=>(async function transportSweepFetchBackgroundCancelAction(candidate) {
        const vehicleId = (0,__mcmsModuleContext.String)(candidate?.vehicleId || '').trim();
        if (!/^\d+$/u.test(vehicleId)) return { status: 'unsupported', reason: 'invalid vehicle identity' };
        if ((0,__mcmsModuleContext.transportSweepOwnVehicleIdSet)().has(vehicleId)) {
            return { status: 'unsupported', reason: 'vehicle is in the verified personal ownership list' };
        }
        try {
            const response = await (0,__mcmsModuleContext.runtimeFetch)(`/vehicles/${vehicleId}`, {
                method: 'GET',
                credentials: 'same-origin',
                cache: 'no-store',
                headers: { Accept: 'text/html,application/xhtml+xml' },
                timeoutMs: __mcmsModuleContext.TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS
            });
            if (!response.ok) return { status: 'unsupported', reason: `vehicle page returned HTTP ${response.status}` };
            const html = await response.text();
            if (!html || html.length < 40) return { status: 'unsupported', reason: 'vehicle page was empty' };
            const doc = new __mcmsModuleContext.DOMParser().parseFromString(html, 'text/html');
            const action = (0,__mcmsModuleContext.transportSweepBackgroundCancelAction)(doc, candidate);
            return action
                ? { status: 'ready', action, confirmationBaseline: (0,__mcmsModuleContext.transportSweepReleaseConfirmationSignature)(doc.body?.textContent || '') }
                : { status: 'unsupported', reason: 'no exact native Cancel Transport link was exposed' };
        } catch (err) {
            return { status: 'unsupported', reason: err?.name === 'AbortError' ? 'vehicle-page check timed out' : 'vehicle-page check failed' };
        }
    }),
"transportSweepAttemptBackgroundRelease":__mcmsModuleContext=>(async function transportSweepAttemptBackgroundRelease(candidate) {
        if (__mcmsModuleContext.transportSweepRuntime.stopRequested) return { status: 'stopped', writeAttempted: false };
        const prepared = await (0,__mcmsModuleContext.transportSweepFetchBackgroundCancelAction)(candidate);
        if (prepared.status !== 'ready') return { ...prepared, writeAttempted: false };
        if (__mcmsModuleContext.transportSweepRuntime.stopRequested) return { status: 'stopped', writeAttempted: false };

        try {
            const response = await (0,__mcmsModuleContext.runtimeFetch)(prepared.action.href, {
                method: 'GET',
                credentials: 'same-origin',
                cache: 'no-store',
                redirect: 'follow',
                headers: { Accept: 'text/html,application/xhtml+xml' },
                timeoutMs: __mcmsModuleContext.TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS
            });
            const html = await response.text();
            if (response.ok && html) {
                const doc = new __mcmsModuleContext.DOMParser().parseFromString(html, 'text/html');
                if ((0,__mcmsModuleContext.transportSweepBackgroundReleaseConfirmed)(doc, prepared.confirmationBaseline)) {
                    return { status: 'confirmed', writeAttempted: true, action: prepared.action };
                }
            }
            return {
                status: 'ambiguous',
                writeAttempted: true,
                action: prepared.action,
                reason: response.ok ? 'MissionChief returned no fresh release confirmation' : `MissionChief returned HTTP ${response.status}`
            };
        } catch (err) {
            return {
                status: 'ambiguous',
                writeAttempted: true,
                action: prepared.action,
                reason: err?.name === 'AbortError' ? 'release request timed out after it was sent' : 'release response could not be verified'
            };
        }
    }),
"collectTransportSweepVehicleCandidatesForMission":__mcmsModuleContext=>(async function collectTransportSweepVehicleCandidatesForMission(missionId) {
        const domCandidates = (0,__mcmsModuleContext.collectTransportSweepVehicleCandidates)();
        const domStats = { ...(__mcmsModuleContext.transportSweepRuntime.lastCandidateStats || {}) };
        if (domCandidates.length) return domCandidates;

        const fetched = await (0,__mcmsModuleContext.transportSweepFetchMissionCandidates)(missionId);
        if (fetched) {
            __mcmsModuleContext.transportSweepRuntime.rejectedOwn = fetched.stats.rejectedOwn || 0;
            __mcmsModuleContext.transportSweepRuntime.lastCandidateStats = fetched.stats;
            if (fetched.candidates?.length) {
                (0,__mcmsModuleContext.transportSweepLog)(`Recovered ${fetched.stats.totalLinks} vehicle links from mission HTML`);
                return fetched.candidates;
            }
        }

        if (!fetched) __mcmsModuleContext.transportSweepRuntime.lastCandidateStats = domStats;
        return [];
    }),
"closeTransportSweepWindows":__mcmsModuleContext=>(async function closeTransportSweepWindows(reason = 'navigation') {
        const target = __mcmsModuleContext.transportSweepRuntime.activeWindowRoot;
        const ownedLayers = __mcmsModuleContext.Array.from(__mcmsModuleContext.transportSweepRuntime.ownedWindowLayers || []).filter(layer => layer?.isConnected);
        __mcmsModuleContext.transportSweepRuntime.missionWindowRoot = null;
        if ((!target || !target.isConnected || !(0,__mcmsModuleContext.transportSweepElementVisible)(target)) && !ownedLayers.length) {
            __mcmsModuleContext.transportSweepRuntime.activeWindowRoot = null;
            __mcmsModuleContext.transportSweepRuntime.ownedWindowLayers = new __mcmsModuleContext.Set();
            __mcmsModuleContext.transportSweepRuntime.activeWindowCreatedLayer = false;
            return true;
        }

        const waitUntilClosed = timeoutMs => (0,__mcmsModuleContext.transportSweepWaitFor)(
            () => !target?.isConnected || !(0,__mcmsModuleContext.transportSweepElementVisible)(target) ? true : null,
            timeoutMs,
            100
        );

        let closed = !target?.isConnected || !(0,__mcmsModuleContext.transportSweepElementVisible)(target);
        if (!closed) {
            const closeControl = (0,__mcmsModuleContext.transportSweepWindowCloseControl)(target);
            if (closeControl) {
                try {
                    closeControl.click();
                    closed = (0,__mcmsModuleContext.Boolean)(await waitUntilClosed(1200));
                } catch (err) {}
            }
        }

        if (!closed && typeof __mcmsModuleContext.pageWindow.lightboxClose === 'function') {
            try {
                __mcmsModuleContext.pageWindow.lightboxClose();
                closed = (0,__mcmsModuleContext.Boolean)(await waitUntilClosed(1400));
            } catch (err) {}
        }

        if (__mcmsModuleContext.transportSweepRuntime.activeWindowCreatedLayer) {
            const removable = __mcmsModuleContext.Array.from(new __mcmsModuleContext.Set(ownedLayers.filter(layer => layer?.isConnected)));
            removable.sort((a, b) => a.contains?.(b) ? -1 : b.contains?.(a) ? 1 : 0);
            for (const layer of removable) {
                if (!layer?.isConnected) continue;
                try {
                    layer.querySelectorAll?.('iframe, frame').forEach(frame => {
                        try { frame.src = 'about:blank'; } catch (err) {}
                    });
                    layer.remove();
                } catch (err) {}
            }
            closed = !target?.isConnected || !(0,__mcmsModuleContext.transportSweepElementVisible)(target);
        }

        const ownedStillConnected = ownedLayers.some(layer => layer?.isConnected && (0,__mcmsModuleContext.transportSweepElementVisible)(layer));
        if (!closed || ownedStillConnected) {
            (0,__mcmsModuleContext.transportSweepLog)(`MissionChief did not remove the sweep-owned window before ${reason}`, 'error');
            return false;
        }

        __mcmsModuleContext.transportSweepRuntime.activeWindowRoot = null;
        __mcmsModuleContext.transportSweepRuntime.ownedWindowLayers = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.activeWindowCreatedLayer = false;
        await (0,__mcmsModuleContext.transportSweepSleep)(80);
        return true;
    }),
"openTransportSweepPath":__mcmsModuleContext=>(async function openTransportSweepPath(path, mode) {
        if (__mcmsModuleContext.transportSweepRuntime.stopRequested) return false;
        if (typeof __mcmsModuleContext.pageWindow.lightboxOpen !== 'function') throw new __mcmsModuleContext.Error('MissionChief lightboxOpen is unavailable');
        const closed = await (0,__mcmsModuleContext.closeTransportSweepWindows)(mode === 'mission' ? 'opening a mission' : 'opening a vehicle');
        if (!closed || __mcmsModuleContext.transportSweepRuntime.stopRequested) return false;

        const beforeRoots = (0,__mcmsModuleContext.transportSweepVisibleWindowRoots)();
        const beforeRootText = new __mcmsModuleContext.Map(beforeRoots.map(root => [root, (0,__mcmsModuleContext.String)(root.textContent || '').trim()]));
        const beforeLayers = new __mcmsModuleContext.Set((0,__mcmsModuleContext.transportSweepNativeWindowLayers)());

        if (mode === 'mission') {
            __mcmsModuleContext.transportSweepRuntime.missionAnchorBaseline = new __mcmsModuleContext.Set((0,__mcmsModuleContext.transportSweepVisibleVehicleAnchors)());
            __mcmsModuleContext.transportSweepRuntime.rejectedOwn = 0;
            __mcmsModuleContext.transportSweepRuntime.missionWindowRoot = null;
            const missionId = (0,__mcmsModuleContext.normaliseMissionId)((0,__mcmsModuleContext.String)(path || '').match(/\/missions\/(\d+)/)?.[1]);
            __mcmsModuleContext.pageWindow.lightboxOpen(path);
            await (0,__mcmsModuleContext.transportSweepWaitFor)(() => {
                const root = (0,__mcmsModuleContext.transportSweepFindMissionWindowRoot)(missionId);
                if (root) {
                    const anchors = (0,__mcmsModuleContext.transportSweepVehicleAnchorsWithin)(root);
                    const afterText = (0,__mcmsModuleContext.String)(root.textContent || '').trim();
                    const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root);
                    if (anchors.length || (afterText && changed)) {
                        __mcmsModuleContext.transportSweepRuntime.missionWindowRoot = root;
                        (0,__mcmsModuleContext.transportSweepClaimWindow)(root, beforeLayers);
                        return { root, anchors };
                    }
                }
                const newAnchor = (0,__mcmsModuleContext.transportSweepVisibleVehicleAnchors)().find(anchor => !__mcmsModuleContext.transportSweepRuntime.missionAnchorBaseline.has(anchor));
                if (newAnchor) {
                    __mcmsModuleContext.transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.parentElement;
                    (0,__mcmsModuleContext.transportSweepClaimWindow)(__mcmsModuleContext.transportSweepRuntime.missionWindowRoot, beforeLayers);
                    return { root: __mcmsModuleContext.transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
                }
                return null;
            }, 4200, 120);
            return !__mcmsModuleContext.transportSweepRuntime.stopRequested && (0,__mcmsModuleContext.Boolean)(__mcmsModuleContext.transportSweepRuntime.activeWindowRoot);
        }

        __mcmsModuleContext.pageWindow.lightboxOpen(path);
        const vehicleWindow = await (0,__mcmsModuleContext.transportSweepWaitFor)(() => {
            const button = (0,__mcmsModuleContext.findVisibleDischargePatientButton)(__mcmsModuleContext.transportSweepRuntime.vehicleButtonBaseline);
            if (button) {
                const root = button.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || button.parentElement;
                return { root };
            }
            const root = (0,__mcmsModuleContext.transportSweepVisibleWindowRoots)().find(candidate => {
                const text = (0,__mcmsModuleContext.String)(candidate.textContent || '').trim();
                return !beforeRootText.has(candidate) || text !== beforeRootText.get(candidate);
            });
            return root ? { root } : null;
        }, 4200, 120);
        (0,__mcmsModuleContext.transportSweepClaimWindow)(vehicleWindow?.root, beforeLayers);
        return !__mcmsModuleContext.transportSweepRuntime.stopRequested && (0,__mcmsModuleContext.Boolean)(__mcmsModuleContext.transportSweepRuntime.activeWindowRoot);
    }),
"openTransportSweepVehicle":__mcmsModuleContext=>(async function openTransportSweepVehicle(candidate) {
        if (__mcmsModuleContext.transportSweepRuntime.stopRequested || !candidate?.href) return null;
        __mcmsModuleContext.transportSweepRuntime.vehicleButtonBaseline = new __mcmsModuleContext.Set((0,__mcmsModuleContext.transportSweepVisibleDischargeButtons)());
        const opened = await (0,__mcmsModuleContext.openTransportSweepPath)(candidate.href, 'vehicle');
        if (!opened || __mcmsModuleContext.transportSweepRuntime.stopRequested) return null;

        const openedAt = __mcmsModuleContext.Date.now();
        return await (0,__mcmsModuleContext.transportSweepWaitFor)(() => {
            const button = (0,__mcmsModuleContext.findVisibleDischargePatientButton)(__mcmsModuleContext.transportSweepRuntime.vehicleButtonBaseline);
            if (button) return { opened: true, button };
            const roots = (0,__mcmsModuleContext.transportSweepTopLevelWindowRoots)();
            if (roots.length && __mcmsModuleContext.Date.now() - openedAt > 350) return { opened: true, button: null };
            return null;
        }, 7500, 140);
    }),
"processTransportSweepMission":__mcmsModuleContext=>(async function processTransportSweepMission(item, remainingAllowance) {
        const missionId = (0,__mcmsModuleContext.normaliseMissionId)(item?.missionId);
        if (missionId === null || remainingAllowance <= 0) return 0;

        const missionLabel = (0,__mcmsModuleContext.String)(item?.caption || `Mission ${missionId}`);
        __mcmsModuleContext.transportSweepRuntime.currentMissionId = missionId;
        __mcmsModuleContext.transportSweepRuntime.currentItem = missionLabel;
        (0,__mcmsModuleContext.renderTransportSweepPanel)();

        const attemptedVehicleIds = new __mcmsModuleContext.Set();
        let clearedHere = 0;
        let releaseAttemptsHere = 0;
        let initialScanLogged = false;
        let missionHadCandidates = false;
        let nativeMode = __mcmsModuleContext.state.transportSweep.backgroundFirst === false;
        let missionOpen = false;

        const openNativeMission = async reason => {
            (0,__mcmsModuleContext.transportSweepLog)(`${reason} ${missionLabel}`);
            missionOpen = await (0,__mcmsModuleContext.openTransportSweepPath)(`/missions/${missionId}`, 'mission');
            if (!missionOpen && !__mcmsModuleContext.transportSweepRuntime.stopRequested) {
                (0,__mcmsModuleContext.transportSweepLog)(`Could not inspect ${missionLabel} because its mission window did not become available; no patient skip was recorded`, 'warn');
            }
            return missionOpen;
        };

        if (nativeMode) {
            if (!await openNativeMission('Opening')) return 0;
        } else {
            (0,__mcmsModuleContext.transportSweepLog)(`Background-first scan: ${missionLabel}`);
        }

        while (!__mcmsModuleContext.transportSweepRuntime.stopRequested && releaseAttemptsHere < remainingAllowance && __mcmsModuleContext.transportSweepRuntime.releaseAttempts < __mcmsModuleContext.state.transportSweep.maxPerRun) {
            let candidates = [];
            if (nativeMode) {
                candidates = await (0,__mcmsModuleContext.collectTransportSweepVehicleCandidatesForMission)(missionId);
            } else {
                const fetched = await (0,__mcmsModuleContext.transportSweepFetchMissionCandidates)(missionId);
                if (fetched) {
                    __mcmsModuleContext.transportSweepRuntime.rejectedOwn = fetched.stats.rejectedOwn || 0;
                    __mcmsModuleContext.transportSweepRuntime.lastCandidateStats = fetched.stats;
                    candidates = fetched.candidates || [];
                } else {
                    __mcmsModuleContext.transportSweepRuntime.lastCandidateStats = { source: 'mission HTML', candidates: 0 };
                }
            }
            const candidateStats = __mcmsModuleContext.transportSweepRuntime.lastCandidateStats || {};
            if (!initialScanLogged) {
                const source = candidateStats.source ? ` · ${candidateStats.source}` : '';
                (0,__mcmsModuleContext.transportSweepLog)(`Vehicle scan: ${candidateStats.totalLinks || 0} vehicle links · ${candidateStats.allianceLinks || 0} alliance FMS 5 · ${candidateStats.candidates || 0} patient candidates${source}`);
                if (__mcmsModuleContext.transportSweepRuntime.rejectedOwn > 0) {
                    (0,__mcmsModuleContext.transportSweepLog)(`Ignored ${__mcmsModuleContext.transportSweepRuntime.rejectedOwn} of your own FMS 5 vehicle${__mcmsModuleContext.transportSweepRuntime.rejectedOwn === 1 ? '' : 's'} at ${missionLabel}`);
                }
                initialScanLogged = true;
            }

            if (candidates.length) missionHadCandidates = true;
            const candidate = candidates.find(entry => !attemptedVehicleIds.has((0,__mcmsModuleContext.String)(entry.vehicleId)));
            if (!candidate) {
                if (!nativeMode && !missionHadCandidates) {
                    nativeMode = true;
                    (0,__mcmsModuleContext.transportSweepLog)(`Background mission data was unavailable for ${missionLabel}; falling back to the visible native workflow`, 'warn');
                    if (await openNativeMission('Opening native fallback for')) continue;
                    break;
                }
                if (!missionHadCandidates) (0,__mcmsModuleContext.transportSweepLog)(`No alliance-owned FMS 5 patient vehicles were found inside ${missionLabel}`, 'warn');
                else if (nativeMode) (0,__mcmsModuleContext.transportSweepLog)(`Checked every alliance-owned FMS 5 patient vehicle at ${missionLabel}; none exposed a release control`, 'warn');
                else (0,__mcmsModuleContext.transportSweepLog)(`Background pass finished for every discovered patient vehicle at ${missionLabel}`);
                break;
            }

            __mcmsModuleContext.transportSweepRuntime.currentVehicleHref = candidate.href;
            __mcmsModuleContext.transportSweepRuntime.currentItem = (0,__mcmsModuleContext.String)(candidate.label || `Vehicle ${candidate.vehicleId}`);
            (0,__mcmsModuleContext.renderTransportSweepPanel)();
            (0,__mcmsModuleContext.transportSweepLog)(`Vehicle check: FMS 5 ${candidate.label} (${candidate.vehicleId})`);

            if (!nativeMode) {
                const releaseKey = (0,__mcmsModuleContext.transportSweepReleaseKey)(missionId, candidate.vehicleId);
                const backgroundResult = await (0,__mcmsModuleContext.transportSweepAttemptBackgroundRelease)(candidate);
                if (backgroundResult.status === 'stopped' || __mcmsModuleContext.transportSweepRuntime.stopRequested) break;
                if (backgroundResult.status === 'unsupported') {
                    nativeMode = true;
                    (0,__mcmsModuleContext.transportSweepLog)(`No authoritative background action for ${candidate.label}; using MissionChief's visible native workflow`, 'warn');
                    if (await openNativeMission('Opening native fallback for')) continue;
                    break;
                }

                attemptedVehicleIds.add((0,__mcmsModuleContext.String)(candidate.vehicleId));
                if (backgroundResult.writeAttempted) {
                    releaseAttemptsHere += 1;
                    __mcmsModuleContext.transportSweepRuntime.releaseAttempts += 1;
                }
                if (backgroundResult.status === 'confirmed') {
                    const confirmed = (0,__mcmsModuleContext.recordTransportSweepConfirmedRelease)(
                        releaseKey,
                        `Cleared ${candidate.label} at ${missionLabel} in the background`
                    );
                    if (confirmed) clearedHere += 1;
                } else {
                    (0,__mcmsModuleContext.recordTransportSweepAmbiguousRelease)(
                        releaseKey,
                        `Background result for ${candidate.label} at ${missionLabel} was ambiguous (${backgroundResult.reason || 'no confirmation'}); it will not be retried`
                    );
                }

                if (!__mcmsModuleContext.transportSweepRuntime.stopRequested && releaseAttemptsHere < remainingAllowance && __mcmsModuleContext.transportSweepRuntime.releaseAttempts < __mcmsModuleContext.state.transportSweep.maxPerRun) {
                    await (0,__mcmsModuleContext.transportSweepSleep)(__mcmsModuleContext.state.transportSweep.delayMs);
                }
                continue;
            }

            attemptedVehicleIds.add((0,__mcmsModuleContext.String)(candidate.vehicleId));

            const vehicleResult = await (0,__mcmsModuleContext.openTransportSweepVehicle)(candidate);
            if (__mcmsModuleContext.transportSweepRuntime.stopRequested) break;
            const button = vehicleResult?.button || (vehicleResult?.opened ? await (0,__mcmsModuleContext.transportSweepWaitFor)(
                () => (0,__mcmsModuleContext.findVisibleDischargePatientButton)(__mcmsModuleContext.transportSweepRuntime.vehicleButtonBaseline),
                3200,
                120
            ) : null);

            let confirmedThisAttempt = false;
            if (!button) {
                (0,__mcmsModuleContext.recordTransportSweepSkippedPatient)(
                    (0,__mcmsModuleContext.transportSweepReleaseKey)(missionId, candidate.vehicleId),
                    `Skipped ${candidate.label} at ${missionLabel}: no usable Cancel Transport or Discharge patient control was available`
                );
            } else {
                try {
                    const releaseKey = (0,__mcmsModuleContext.transportSweepReleaseKey)(missionId, candidate.vehicleId);
                    const confirmationBaseline = (0,__mcmsModuleContext.captureTransportSweepReleaseConfirmationBaseline)();
                    const releaseControlLabel = (0,__mcmsModuleContext.transportSweepNativeReleaseControlText)(button);
                    __mcmsModuleContext.transportSweepRuntime.pendingDischargeKey = releaseKey;
                    releaseAttemptsHere += 1;
                    __mcmsModuleContext.transportSweepRuntime.releaseAttempts += 1;
                    button.click();
                    (0,__mcmsModuleContext.clickTransportSweepDischargeConfirmation)(releaseKey);
                    let cleared = false;
                    try {
                        cleared = await (0,__mcmsModuleContext.transportSweepWaitFor)(() => {
                            (0,__mcmsModuleContext.clickTransportSweepDischargeConfirmation)(releaseKey);
                            if ((0,__mcmsModuleContext.transportSweepReleaseConfirmationVisible)(confirmationBaseline)) return true;
                            if (!button.isConnected || !(0,__mcmsModuleContext.transportSweepElementVisible)(button) || button.disabled) return true;
                            return (0,__mcmsModuleContext.transportSweepNativeReleaseControlText)(button) !== releaseControlLabel ? true : null;
                        }, 5000, 70);
                    } finally {
                        if (__mcmsModuleContext.transportSweepRuntime.pendingDischargeKey === releaseKey) __mcmsModuleContext.transportSweepRuntime.pendingDischargeKey = '';
                    }
                    if (!cleared) throw new __mcmsModuleContext.Error('Discharge confirmation timed out');
                    confirmedThisAttempt = (0,__mcmsModuleContext.recordTransportSweepConfirmedRelease)(
                        releaseKey,
                        `Cleared ${candidate.label} at ${missionLabel}`
                    );
                    if (confirmedThisAttempt) clearedHere += 1;
                } catch (err) {
                    __mcmsModuleContext.transportSweepRuntime.errors += 1;
                    (0,__mcmsModuleContext.transportSweepLog)(`Failed ${candidate.label}: ${err?.message || 'unknown error'}`, 'error');
                }
            }

            if (!__mcmsModuleContext.transportSweepRuntime.stopRequested && releaseAttemptsHere < remainingAllowance && __mcmsModuleContext.transportSweepRuntime.releaseAttempts < __mcmsModuleContext.state.transportSweep.maxPerRun) {
                await (0,__mcmsModuleContext.transportSweepSleep)(__mcmsModuleContext.state.transportSweep.delayMs);
                (0,__mcmsModuleContext.transportSweepLog)(`Returning to ${missionLabel} for remaining alliance ambulances`);
                missionOpen = await (0,__mcmsModuleContext.openTransportSweepPath)(`/missions/${missionId}`, 'mission');
                if (!missionOpen) {
                    if (confirmedThisAttempt) (0,__mcmsModuleContext.transportSweepLog)(`Cleared ${candidate.label}, but could not reopen ${missionLabel}; continuing with the confirmed patient result`, 'warn');
                    else {
                        __mcmsModuleContext.transportSweepRuntime.errors += 1;
                        (0,__mcmsModuleContext.transportSweepLog)(`Could not return to ${missionLabel} during native processing`, 'error');
                    }
                    break;
                }
            }
        }

        await (0,__mcmsModuleContext.closeTransportSweepWindows)('finishing the mission');

        return clearedHere;
    }),
"startTransportSweep":__mcmsModuleContext=>(async function startTransportSweep() {
        if (__mcmsModuleContext.transportSweepRuntime.running) return;
        const recent=__mcmsModuleContext.transportSweepRuntime.scannedAt && Date.now()-__mcmsModuleContext.transportSweepRuntime.scannedAt<30000 && !__mcmsModuleContext.transportSweepRuntime.scanPromise && !__mcmsModuleContext.transportSweepRuntime.stopRequested;
        const queue = recent ? __mcmsModuleContext.transportSweepRuntime.queue : await (0,__mcmsModuleContext.scanTransportSweepQueue)();
if(__mcmsModuleContext.transportSweepRuntime.stopRequested||__mcmsModuleContext.pilot.job?.cancelled)return;
        if (!queue.length) {
            (0,__mcmsModuleContext.showToast)('No alliance patient transports found');
            return;
        }
        (0,__mcmsModuleContext.showToast)('Verifying your personal vehicle list…');
        const ownershipReady = await (0,__mcmsModuleContext.refreshPersonalVehicleData)(true);
        if (!ownershipReady || !__mcmsModuleContext.vehicleApiReady || __mcmsModuleContext.personalVehicleApiCache.size === 0) {
            (0,__mcmsModuleContext.showToast)('Transport Sweep cancelled — your vehicle ownership list could not be verified');
            return;
        }
        __mcmsModuleContext.transportSweepRuntime.ownVehicleIds = new __mcmsModuleContext.Set(__mcmsModuleContext.Array.from(__mcmsModuleContext.personalVehicleApiCache.keys(), id => (0,__mcmsModuleContext.String)(id)));
        const totalRequests = queue.reduce((sum, item) => sum + __mcmsModuleContext.Math.max(1, (0,__mcmsModuleContext.Number)(item.count) || 1), 0);
        const planned = __mcmsModuleContext.Math.min(totalRequests, __mcmsModuleContext.state.transportSweep.maxPerRun);
        const confirmed = __mcmsModuleContext.pageWindow.confirm(`Transport Sweep will attempt up to ${planned} alliance-member patient releases across ${queue.length} alliance mission${queue.length === 1 ? '' : 's'}.

Background-first mode uses only an exact same-origin native Cancel Transport link fetched from the verified vehicle page. If that safe path is unavailable before a release request, the sweep falls back to MissionChief's visible native workflow. Ambiguous requests are never retried. Your own verified vehicle IDs are always excluded. Continue?`);
        if (!confirmed) return;
        (0,__mcmsModuleContext.dismissTransportSweepReport)({ quiet: true, render: false });
        (0,__mcmsModuleContext.toolkitAnalyticsRecordFeature)('patientTransportSweep');
        __mcmsModuleContext.transportSweepRuntime.running = true;
        __mcmsModuleContext.transportSweepRuntime.stopRequested = false;
        __mcmsModuleContext.transportSweepRuntime.currentMissionId = null;
        __mcmsModuleContext.transportSweepRuntime.currentVehicleHref = '';
        __mcmsModuleContext.transportSweepRuntime.cleared = 0;
        __mcmsModuleContext.transportSweepRuntime.skipped = 0;
        __mcmsModuleContext.transportSweepRuntime.errors = 0;
        __mcmsModuleContext.transportSweepRuntime.processed = 0;
        __mcmsModuleContext.transportSweepRuntime.releaseAttempts = 0;
        __mcmsModuleContext.transportSweepRuntime.confirmedReleaseKeys = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.ambiguousReleaseKeys = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.skippedPatientKeys = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.confirmedDischargeDialogKeys = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.pendingDischargeKey = '';
        __mcmsModuleContext.transportSweepRuntime.rejectedOwn = 0;
        __mcmsModuleContext.transportSweepRuntime.missionAnchorBaseline = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.vehicleButtonBaseline = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.missionWindowRoot = null;
        __mcmsModuleContext.transportSweepRuntime.activeWindowRoot = null;
        __mcmsModuleContext.transportSweepRuntime.ownedWindowLayers = new __mcmsModuleContext.Set();
        __mcmsModuleContext.transportSweepRuntime.activeWindowCreatedLayer = false;
        __mcmsModuleContext.transportSweepRuntime.lastCandidateStats = null;
        __mcmsModuleContext.transportSweepRuntime.startedAt = __mcmsModuleContext.Date.now();
        __mcmsModuleContext.transportSweepRuntime.completedMissionCount = 0;
        (0,__mcmsModuleContext.setTransportSweepMissionProgress)(queue.length ? 1 : 0, queue.length, {
            item: 'Preparing sweep',
            message: 'Preparing patient transport sweep',
            render: false
        });
        __mcmsModuleContext.transportSweepRuntime.statusLevel = 'info';
        __mcmsModuleContext.transportSweepRuntime.hudFinal = false;
        __mcmsModuleContext.transportSweepRuntime.log = [];
        (0,__mcmsModuleContext.renderTransportSweepPanel)();
        (0,__mcmsModuleContext.transportSweepLog)(`Sweep started: ${queue.length} missions, maximum ${__mcmsModuleContext.state.transportSweep.maxPerRun} requests`);
        try {
            for (let missionOffset = 0; missionOffset < queue.length; missionOffset += 1) {
                const item = queue[missionOffset];
                if (__mcmsModuleContext.transportSweepRuntime.stopRequested || __mcmsModuleContext.transportSweepRuntime.releaseAttempts >= __mcmsModuleContext.state.transportSweep.maxPerRun) break;
                const missionNumber = missionOffset + 1;
                const missionLabel = (0,__mcmsModuleContext.String)(item?.caption || `Mission ${item?.missionId || missionNumber}`);
                (0,__mcmsModuleContext.setTransportSweepMissionProgress)(missionNumber, queue.length, {
                    item: missionLabel,
                    message: `Processing mission ${missionNumber} of ${queue.length}`,
                    forceRender: true
                });
                const remaining = __mcmsModuleContext.state.transportSweep.maxPerRun - __mcmsModuleContext.transportSweepRuntime.releaseAttempts;
                try {
                    await (0,__mcmsModuleContext.processTransportSweepMission)(item, remaining);
                } catch (err) {
                    __mcmsModuleContext.transportSweepRuntime.errors += 1;
                    (0,__mcmsModuleContext.transportSweepLog)(`Mission ${missionLabel} failed: ${err?.message || 'unknown error'}`, 'error');
                    await (0,__mcmsModuleContext.closeTransportSweepWindows)('recovering from a mission error');
                } finally {
                    __mcmsModuleContext.transportSweepRuntime.currentItem = missionLabel;
                    (0,__mcmsModuleContext.completeTransportSweepMissionProgress)(missionNumber, { forceRender: true });
                }
                if (!__mcmsModuleContext.transportSweepRuntime.stopRequested) await (0,__mcmsModuleContext.transportSweepSleep)(__mcmsModuleContext.state.transportSweep.delayMs);
            }
        } catch (err) {
            __mcmsModuleContext.transportSweepRuntime.errors += 1;
            (0,__mcmsModuleContext.transportSweepLog)(`Sweep stopped by error: ${err?.message || 'unknown error'}`, 'error');
        } finally {
            await (0,__mcmsModuleContext.closeTransportSweepWindows)('finishing the sweep');
            const wasStopped = __mcmsModuleContext.transportSweepRuntime.stopRequested;
            __mcmsModuleContext.transportSweepRuntime.running = false;
            __mcmsModuleContext.transportSweepRuntime.stopRequested = false;
            __mcmsModuleContext.transportSweepRuntime.currentMissionId = null;
            __mcmsModuleContext.transportSweepRuntime.currentVehicleHref = '';
            __mcmsModuleContext.transportSweepRuntime.pendingDischargeKey = '';
            __mcmsModuleContext.transportSweepRuntime.currentItem = '';
            __mcmsModuleContext.transportSweepRuntime.missionAnchorBaseline = new __mcmsModuleContext.Set();
            __mcmsModuleContext.transportSweepRuntime.vehicleButtonBaseline = new __mcmsModuleContext.Set();
            __mcmsModuleContext.transportSweepRuntime.activeWindowRoot = null;
            __mcmsModuleContext.transportSweepRuntime.ownedWindowLayers = new __mcmsModuleContext.Set();
            __mcmsModuleContext.transportSweepRuntime.activeWindowCreatedLayer = false;
            __mcmsModuleContext.transportSweepRuntime.hudFinal = false;
            const missionProgress = (0,__mcmsModuleContext.finaliseTransportSweepMissionProgress)(wasStopped);
            (0,__mcmsModuleContext.transportSweepLog)(`${wasStopped ? 'Stopped' : 'Complete'}: missions ${missionProgress.text}, ${__mcmsModuleContext.transportSweepRuntime.cleared} cleared, ${__mcmsModuleContext.transportSweepRuntime.skipped} skipped, ${__mcmsModuleContext.transportSweepRuntime.errors} errors`, __mcmsModuleContext.transportSweepRuntime.errors ? 'error' : 'info');
            const finalReport = (0,__mcmsModuleContext.setTransportSweepReport)((0,__mcmsModuleContext.createTransportSweepReport)(wasStopped, missionProgress), { render: false });
            (0,__mcmsModuleContext.buildTransportSweepQueue)();
            (0,__mcmsModuleContext.scheduleTransportWatcherRefresh)(0);
            (0,__mcmsModuleContext.showToast)(wasStopped ? `Transport Sweep stopped · ${__mcmsModuleContext.transportSweepRuntime.cleared} cleared · ${__mcmsModuleContext.transportSweepRuntime.skipped} skipped · ${missionProgress.text} missions` : `Transport Sweep complete · ${__mcmsModuleContext.transportSweepRuntime.cleared} cleared · ${__mcmsModuleContext.transportSweepRuntime.skipped} skipped · ${missionProgress.text} missions`);
            (0,__mcmsModuleContext.renderTransportSweepPanel)();
            if (finalReport) void (0,__mcmsModuleContext.postTransportSweepDiscordReport)(finalReport);
        }
    }),
"fetchAllianceCourseDocument":__mcmsModuleContext=>(async function fetchAllianceCourseDocument(pathOrUrl) {
        const url = new __mcmsModuleContext.URL(pathOrUrl, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        if (url.origin !== __mcmsModuleContext.pageWindow.location.origin) throw new __mcmsModuleContext.Error('Blocked an unexpected external Alliance Courses URL.');
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'text/html,application/xhtml+xml' },
            timeoutMs: __mcmsModuleContext.ALLIANCE_COURSE_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} for ${url.pathname}.`);
        const html = await response.text();
        return { doc: new __mcmsModuleContext.DOMParser().parseFromString(html, 'text/html'), url: response.url || url.href };
    }),
"scanAllianceCourseQueue":__mcmsModuleContext=>(async function scanAllianceCourseQueue({ force = true } = {}) {
        if (__mcmsModuleContext.allianceCourseRuntime.scanPromise) return __mcmsModuleContext.allianceCourseRuntime.scanPromise;
        if (__mcmsModuleContext.allianceCourseRuntime.running) return __mcmsModuleContext.allianceCourseRuntime.queue;
        const selectedDay = (0,__mcmsModuleContext.allianceCourseResolvedDay)();
        if (!force && __mcmsModuleContext.allianceCourseRuntime.scannedDay === selectedDay && __mcmsModuleContext.allianceCourseRuntime.scannedAt) return __mcmsModuleContext.allianceCourseRuntime.queue;
        __mcmsModuleContext.allianceCourseRuntime.currentItem = `Scanning ${(0,__mcmsModuleContext.allianceCourseDayLabel)(selectedDay)} buildings`;
        const scanPromise = (async () => {
            try {
                const localRows = __mcmsModuleContext.document.querySelectorAll?.('tr.alliance_buildings_table_searchable');
                const sourceDocument = (0,__mcmsModuleContext.isAllianceBuildingsPath)(__mcmsModuleContext.pageWindow.location.pathname) && localRows?.length
                    ? __mcmsModuleContext.document
                    : (await (0,__mcmsModuleContext.fetchAllianceCourseDocument)('/verband/gebauede')).doc;
                const result = (0,__mcmsModuleContext.buildAllianceCourseQueue)(sourceDocument, selectedDay);
                __mcmsModuleContext.allianceCourseRuntime.queue = result.queue;
                __mcmsModuleContext.allianceCourseRuntime.summary = result.summary;
                __mcmsModuleContext.allianceCourseRuntime.scannedAt = __mcmsModuleContext.Date.now();
                __mcmsModuleContext.allianceCourseRuntime.scannedDay = selectedDay;
                __mcmsModuleContext.allianceCourseRuntime.currentItem = '';
                __mcmsModuleContext.allianceCourseRuntime.processed = 0;
                __mcmsModuleContext.allianceCourseRuntime.created = 0;
                __mcmsModuleContext.allianceCourseRuntime.skipped = 0;
                __mcmsModuleContext.allianceCourseRuntime.errors = 0;
                __mcmsModuleContext.allianceCourseRuntime.log = [];
                (0,__mcmsModuleContext.allianceCourseLog)(`${(0,__mcmsModuleContext.allianceCourseDayLabel)(selectedDay)} scan: ${result.summary.ready} ready, ${result.summary.busy} busy or unavailable, ${result.summary.unmapped} unmapped`);
                if (result.summary.truncated) (0,__mcmsModuleContext.allianceCourseLog)(`${result.summary.truncated} additional day-matched buildings were left outside the ${__mcmsModuleContext.ALLIANCE_COURSE_SCAN_LIMIT}-building scan limit`, 'warn');
                return __mcmsModuleContext.allianceCourseRuntime.queue;
            } catch (err) {
                __mcmsModuleContext.allianceCourseRuntime.queue = [];
                __mcmsModuleContext.allianceCourseRuntime.summary = null;
                __mcmsModuleContext.allianceCourseRuntime.scannedAt = 0;
                __mcmsModuleContext.allianceCourseRuntime.scannedDay = '';
                __mcmsModuleContext.allianceCourseRuntime.currentItem = '';
                (0,__mcmsModuleContext.allianceCourseLog)(`Course scan failed: ${err?.message || 'unknown error'}`, 'error');
                return [];
            }
        })();
        __mcmsModuleContext.allianceCourseRuntime.scanPromise = scanPromise;
        (0,__mcmsModuleContext.renderAllianceCoursesPanel)();
        try { return await scanPromise; }
        finally {
            if (__mcmsModuleContext.allianceCourseRuntime.scanPromise === scanPromise) __mcmsModuleContext.allianceCourseRuntime.scanPromise = null;
            (0,__mcmsModuleContext.renderAllianceCoursesPanel)();
        }
    }),
"submitAllianceCourse":__mcmsModuleContext=>(async function submitAllianceCourse(item, shareDuration) {
        const building = await (0,__mcmsModuleContext.fetchAllianceCourseDocument)(item.path);
        const prepared = (0,__mcmsModuleContext.prepareAllianceCourseSubmission)(building.doc, item, shareDuration);
        const response = await (0,__mcmsModuleContext.runtimeFetch)(prepared.action, {
            method: 'POST',
            credentials: 'same-origin',
            cache: 'no-store',
            redirect: 'follow',
            headers: {
                Accept: 'text/html,application/xhtml+xml',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: prepared.body,
            timeoutMs: __mcmsModuleContext.ALLIANCE_COURSE_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} while starting the course`);
        const responseHtml = await response.text();
        const responseDocument = new __mcmsModuleContext.DOMParser().parseFromString(responseHtml, 'text/html');
        const evidence = (0,__mcmsModuleContext.countAllianceCourseEvidence)(responseDocument, item.nativeLabel);
        if (evidence <= prepared.baseline) throw new __mcmsModuleContext.Error('MissionChief did not return new matching course evidence; no automatic retry was made');
        return { roomCount: prepared.roomCount, evidenceAdded: evidence - prepared.baseline };
    }),
"startAllianceCourses":__mcmsModuleContext=>(async function startAllianceCourses() {
        if (__mcmsModuleContext.allianceCourseRuntime.running) return;
        const queue = await (0,__mcmsModuleContext.scanAllianceCourseQueue)({ force: true });
        if (__mcmsModuleContext.allianceCourseRuntime.running || __mcmsModuleContext.runtime.destroyed) return;
        const planned = queue.slice(0, __mcmsModuleContext.ALLIANCE_COURSE_START_LIMIT);
        if (!planned.length) {
            (0,__mcmsModuleContext.showToast)('No mapped Alliance Courses are currently ready');
            return;
        }
        const day = (0,__mcmsModuleContext.allianceCourseResolvedDay)();
        const duration = __mcmsModuleContext.state.allianceCourses.shareDuration;
        const confirmed = __mcmsModuleContext.pageWindow.confirm(`Alliance Courses will start ${planned.length} ${(0,__mcmsModuleContext.allianceCourseDayLabel)(day)} course${planned.length === 1 ? '' : 's'}.

Each course will use the maximum classroom count currently exposed by MissionChief, share with the alliance for ${(0,__mcmsModuleContext.allianceCourseShareLabel)(duration)}, and keep alliance cost at 0 Credits. Courses are submitted one at a time and an unverified result is never retried automatically. Continue?`);
        if (!confirmed) return;
        (0,__mcmsModuleContext.toolkitAnalyticsRecordFeature)('allianceCourses');
        __mcmsModuleContext.allianceCourseRuntime.running = true;
        __mcmsModuleContext.allianceCourseRuntime.stopRequested = false;
        __mcmsModuleContext.allianceCourseRuntime.currentBuildingId = '';
        __mcmsModuleContext.allianceCourseRuntime.currentItem = '';
        __mcmsModuleContext.allianceCourseRuntime.processed = 0;
        __mcmsModuleContext.allianceCourseRuntime.created = 0;
        __mcmsModuleContext.allianceCourseRuntime.skipped = 0;
        __mcmsModuleContext.allianceCourseRuntime.errors = 0;
        __mcmsModuleContext.allianceCourseRuntime.log = [];
        for (const item of __mcmsModuleContext.allianceCourseRuntime.queue) {
            item.outcome = 'ready';
            item.outcomeDetail = '';
        }
        (0,__mcmsModuleContext.allianceCourseLog)(`Run started: ${planned.length} ${(0,__mcmsModuleContext.allianceCourseDayLabel)(day)} courses · ${(0,__mcmsModuleContext.allianceCourseShareLabel)(duration)} sharing · maximum rooms`);
        try {
            for (let index = 0; index < planned.length; index += 1) {
                if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.allianceCourseRuntime.stopRequested) break;
                const item = planned[index];
                __mcmsModuleContext.allianceCourseRuntime.currentBuildingId = item.buildingId;
                __mcmsModuleContext.allianceCourseRuntime.currentItem = item.name;
                (0,__mcmsModuleContext.renderAllianceCoursesPanel)();
                (0,__mcmsModuleContext.allianceCourseLog)(`Checking ${item.name} for ${item.nativeLabel}`);
                try {
                    const result = await (0,__mcmsModuleContext.submitAllianceCourse)(item, duration);
                    item.outcome = 'created';
                    item.outcomeDetail = `${result.roomCount} room${result.roomCount === 1 ? '' : 's'}`;
                    __mcmsModuleContext.allianceCourseRuntime.created += 1;
                    (0,__mcmsModuleContext.allianceCourseLog)(`Started ${item.nativeLabel} at ${item.name} using ${result.roomCount} room${result.roomCount === 1 ? '' : 's'}`);
                } catch (err) {
                    if (err?.allianceCourseSafeSkip) {
                        item.outcome = 'skipped';
                        item.outcomeDetail = (0,__mcmsModuleContext.String)(err.message || 'native form mismatch');
                        __mcmsModuleContext.allianceCourseRuntime.skipped += 1;
                        (0,__mcmsModuleContext.allianceCourseLog)(`Skipped ${item.name}: ${item.outcomeDetail}`, 'warn');
                    } else {
                        item.outcome = 'error';
                        item.outcomeDetail = (0,__mcmsModuleContext.String)(err?.message || 'unknown error');
                        __mcmsModuleContext.allianceCourseRuntime.errors += 1;
                        (0,__mcmsModuleContext.allianceCourseLog)(`Error at ${item.name}: ${item.outcomeDetail}`, 'error');
                    }
                } finally {
                    __mcmsModuleContext.allianceCourseRuntime.processed += 1;
                    (0,__mcmsModuleContext.renderAllianceCoursesPanel)();
                }
                if (index < planned.length - 1 && !__mcmsModuleContext.allianceCourseRuntime.stopRequested) {
                    const completedDelay = await (0,__mcmsModuleContext.runtimeDelay)(__mcmsModuleContext.state.allianceCourses.delayMs);
                    if (!completedDelay) break;
                }
            }
        } finally {
            const wasStopped = __mcmsModuleContext.allianceCourseRuntime.stopRequested || __mcmsModuleContext.runtime.destroyed;
            __mcmsModuleContext.allianceCourseRuntime.running = false;
            __mcmsModuleContext.allianceCourseRuntime.stopRequested = false;
            __mcmsModuleContext.allianceCourseRuntime.currentBuildingId = '';
            __mcmsModuleContext.allianceCourseRuntime.currentItem = '';
            (0,__mcmsModuleContext.allianceCourseLog)(`${wasStopped ? 'Stopped' : 'Complete'}: ${__mcmsModuleContext.allianceCourseRuntime.created} created, ${__mcmsModuleContext.allianceCourseRuntime.skipped} skipped, ${__mcmsModuleContext.allianceCourseRuntime.errors} errors`, __mcmsModuleContext.allianceCourseRuntime.errors ? 'error' : 'info');
            (0,__mcmsModuleContext.showToast)(`${wasStopped ? 'Alliance Courses stopped' : 'Alliance Courses complete'} · ${__mcmsModuleContext.allianceCourseRuntime.created} created · ${__mcmsModuleContext.allianceCourseRuntime.skipped} skipped · ${__mcmsModuleContext.allianceCourseRuntime.errors} errors`);
            (0,__mcmsModuleContext.renderAllianceCoursesPanel)();
        }
    }),
"fetchDispatchRecruitmentDocument":__mcmsModuleContext=>(async function fetchDispatchRecruitmentDocument(pathOrUrl) {
        const url = new __mcmsModuleContext.URL(pathOrUrl, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        if (url.origin !== __mcmsModuleContext.pageWindow.location.origin) throw new __mcmsModuleContext.Error('Blocked an unexpected external Dispatch Recruitment URL.');
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'text/html,application/xhtml+xml' },
            timeoutMs: __mcmsModuleContext.DISPATCH_RECRUITMENT_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} for ${url.pathname}.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin) throw new __mcmsModuleContext.Error('MissionChief redirected Dispatch Recruitment outside the current game origin.');
        const html = await response.text();
        return { doc: new __mcmsModuleContext.DOMParser().parseFromString(html, 'text/html'), url: finalUrl.href };
    }),
"fetchDispatchRecruitmentBuilding":__mcmsModuleContext=>(async function fetchDispatchRecruitmentBuilding(buildingId) {
        const id = (0,__mcmsModuleContext.String)(buildingId || '');
        if (!/^\d+$/u.test(id)) throw new __mcmsModuleContext.Error('Invalid station identifier.');
        const url = new __mcmsModuleContext.URL(`/api/buildings/${id}`, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'application/json' },
            timeoutMs: __mcmsModuleContext.DISPATCH_RECRUITMENT_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} while checking station ${id}.`);
        const payload = await response.json();
        const record = __mcmsModuleContext.Array.isArray(payload) ? payload.find(item => (0,__mcmsModuleContext.String)(item?.id) === id) : payload;
        if (!record || (0,__mcmsModuleContext.String)(record.id) !== id) throw new __mcmsModuleContext.Error(`MissionChief did not return authoritative station ${id} data.`);
        return record;
    }),
"loadDispatchRecruitmentCatalog":__mcmsModuleContext=>(async function loadDispatchRecruitmentCatalog({ force = false } = {}) {
        if (__mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise) return __mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise;
        if (__mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.preparing || __mcmsModuleContext.stationIconCopierRuntime.scanPromise || __mcmsModuleContext.stationIconCopierRuntime.catalogPromise || __mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return __mcmsModuleContext.dispatchRecruitmentRuntime.dispatches;
        if (!force && __mcmsModuleContext.dispatchRecruitmentRuntime.catalogAt && __mcmsModuleContext.dispatchRecruitmentRuntime.dispatches.length) return __mcmsModuleContext.dispatchRecruitmentRuntime.dispatches;
        __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = 'Loading native Dispatch Centre and building-type options';
        const catalogPromise = (async () => {
            try {
                const { doc } = await (0,__mcmsModuleContext.fetchDispatchRecruitmentDocument)('/buildings/new');
                const catalog = (0,__mcmsModuleContext.parseDispatchRecruitmentCatalog)(doc);
                if (!catalog.dispatches.length) throw new __mcmsModuleContext.Error('MissionChief did not expose any Dispatch Centre options.');
                __mcmsModuleContext.dispatchRecruitmentRuntime.dispatches = catalog.dispatches;
                __mcmsModuleContext.dispatchRecruitmentRuntime.typeLabels = catalog.typeLabels;
                __mcmsModuleContext.dispatchRecruitmentRuntime.catalogAt = __mcmsModuleContext.Date.now();
                const selectedDispatchId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.dispatchRecruitment.dispatchId || '');
                const selected = selectedDispatchId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES
                    ? { id: __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES }
                    : catalog.dispatches.find(item => item.id === selectedDispatchId) || catalog.dispatches[0];
                const selectedTypeId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.dispatchRecruitment.buildingTypeId || __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES);
                const buildingTypeId = selectedTypeId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES || __mcmsModuleContext.Object.prototype.hasOwnProperty.call(catalog.typeLabels, selectedTypeId)
                    ? selectedTypeId
                    : __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES;
                if (force && __mcmsModuleContext.dispatchRecruitmentRuntime.scannedAt) (0,__mcmsModuleContext.clearDispatchRecruitmentScan)();
                let scopeChanged = false;
                if (__mcmsModuleContext.state.dispatchRecruitment.dispatchId !== selected.id) {
                    __mcmsModuleContext.state.dispatchRecruitment.dispatchId = selected.id;
                    scopeChanged = true;
                }
                if (__mcmsModuleContext.state.dispatchRecruitment.buildingTypeId !== buildingTypeId) {
                    __mcmsModuleContext.state.dispatchRecruitment.buildingTypeId = buildingTypeId;
                    scopeChanged = true;
                }
                if (scopeChanged) {
                    (0,__mcmsModuleContext.clearDispatchRecruitmentScan)();
                    (0,__mcmsModuleContext.saveState)();
                }
                __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = '';
                (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Loaded ${catalog.dispatches.length} Dispatch Centre${catalog.dispatches.length === 1 ? '' : 's'} and ${__mcmsModuleContext.Object.keys(catalog.typeLabels).length} native building types`);
                return catalog.dispatches;
            } catch (err) {
                __mcmsModuleContext.dispatchRecruitmentRuntime.dispatches = [];
                __mcmsModuleContext.dispatchRecruitmentRuntime.typeLabels = {};
                __mcmsModuleContext.dispatchRecruitmentRuntime.catalogAt = 0;
                __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = '';
                (0,__mcmsModuleContext.clearDispatchRecruitmentScan)();
                (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Dispatch Centre load failed: ${err?.message || 'unknown error'}`, 'error');
                return [];
            }
        })();
        __mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise = catalogPromise;
        (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
        try { return await catalogPromise; }
        finally {
            if (__mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise === catalogPromise) __mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise = null;
            (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
        }
    }),
"scanDispatchRecruitmentStations":__mcmsModuleContext=>(async function scanDispatchRecruitmentStations({ forceCatalog = false } = {}) {
        if (__mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise) return __mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise;
        if (__mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.preparing || __mcmsModuleContext.stationIconCopierRuntime.scanPromise || __mcmsModuleContext.stationIconCopierRuntime.catalogPromise || __mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return __mcmsModuleContext.dispatchRecruitmentRuntime.queue;
        const dispatches = await (0,__mcmsModuleContext.loadDispatchRecruitmentCatalog)({ force: forceCatalog });
        if (!dispatches.length || __mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.runtime.destroyed) return [];
        const dispatchId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.dispatchRecruitment.dispatchId || '');
        const buildingTypeId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.dispatchRecruitment.buildingTypeId || __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES);
        const allCentres = dispatchId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES;
        const allTypes = buildingTypeId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES;
        const dispatch = allCentres ? null : dispatches.find(item => item.id === dispatchId);
        const scanDispatches = allCentres ? dispatches : dispatch ? [dispatch] : [];
        if (!scanDispatches.length) {
            (0,__mcmsModuleContext.showToast)('Choose a valid Dispatch Centre before scanning');
            return [];
        }
        if (!allTypes && !__mcmsModuleContext.Object.prototype.hasOwnProperty.call(__mcmsModuleContext.dispatchRecruitmentRuntime.typeLabels, buildingTypeId)) {
            (0,__mcmsModuleContext.showToast)('Choose a building type loaded from MissionChief before scanning');
            return [];
        }
        const scanName = allCentres ? 'ALL DISPATCH CENTRES' : dispatch.name;
        const typeName = allTypes ? 'ALL BUILDING TYPES' : __mcmsModuleContext.dispatchRecruitmentRuntime.typeLabels[buildingTypeId];
        __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = `Scanning ${scanName} · ${typeName}`;
        const scanPromise = (async () => {
            try {
                const matrices = [];
                for (let index = 0; index < scanDispatches.length; index += 1) {
                    const matrixDispatch = scanDispatches[index];
                    const matrixPath = `/buildings/${matrixDispatch.id}/leitstelle-buildings`;
                    __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = allCentres ? `Scanning ${index + 1} of ${scanDispatches.length} · ${matrixDispatch.name}` : `Scanning ${matrixDispatch.name}`;
                    (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
                    const { doc, url } = await (0,__mcmsModuleContext.fetchDispatchRecruitmentDocument)(matrixPath);
                    const finalUrl = new __mcmsModuleContext.URL(url);
                    if (finalUrl.pathname.replace(/\/+$/u, '') !== matrixPath || finalUrl.search || finalUrl.hash || doc.getElementsByTagName('table').namedItem('building_table')?.id !== 'building_table') throw new __mcmsModuleContext.Error(`MissionChief did not return the native Buildings matrix for ${matrixDispatch.name}.`);
                    matrices.push(doc);
                }
                const result = (0,__mcmsModuleContext.buildDispatchRecruitmentQueue)(allCentres ? matrices : matrices[0], __mcmsModuleContext.dispatchRecruitmentRuntime.typeLabels, dispatchId, dispatches, buildingTypeId);
                __mcmsModuleContext.dispatchRecruitmentRuntime.queue = result.queue;
                __mcmsModuleContext.dispatchRecruitmentRuntime.summary = result.summary;
                __mcmsModuleContext.dispatchRecruitmentRuntime.scannedAt = __mcmsModuleContext.Date.now();
                __mcmsModuleContext.dispatchRecruitmentRuntime.scannedDispatchId = dispatchId;
                __mcmsModuleContext.dispatchRecruitmentRuntime.scannedTypeId = buildingTypeId;
                const selectionPlan = (0,__mcmsModuleContext.dispatchRecruitmentConfiguredPlan)();
                __mcmsModuleContext.dispatchRecruitmentRuntime.selectedBuildingIds = (0,__mcmsModuleContext.dispatchRecruitmentDefaultSelectedBuildingIds)(result.queue, selectionPlan);
                __mcmsModuleContext.dispatchRecruitmentRuntime.matchingBuildingIds = new __mcmsModuleContext.Set(selectionPlan
                    ? result.queue.filter(item => (0,__mcmsModuleContext.dispatchRecruitmentScanItemMatchesPlan)(item, selectionPlan)).map(item => item.buildingId)
                    : []);
                __mcmsModuleContext.dispatchRecruitmentRuntime.selectedTypeIds = new __mcmsModuleContext.Set(result.queue.map(item => item.typeId));
                __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = '';
                __mcmsModuleContext.dispatchRecruitmentRuntime.log = [];
                (0,__mcmsModuleContext.resetDispatchRecruitmentResults)();
                const centreCount = __mcmsModuleContext.Object.keys(result.summary.dispatchCounts || {}).length;
                const assignmentDetail = allCentres
                    ? `${centreCount} Dispatch Centre${centreCount === 1 ? '' : 's'}; ${result.summary.outsideDispatch} outside the loaded catalogue`
                    : `${result.summary.outsideDispatch} assigned elsewhere`;
                const typeDetail = allTypes ? `${__mcmsModuleContext.Object.keys(result.summary.typeCounts).length} native type${__mcmsModuleContext.Object.keys(result.summary.typeCounts).length === 1 ? '' : 's'}` : typeName;
                const selectedCount = __mcmsModuleContext.dispatchRecruitmentRuntime.selectedBuildingIds.size;
                const matchingCount = selectionPlan ? result.queue.length - selectedCount : 0;
                const selectionDetail = selectionPlan
                    ? `${selectedCount} selected for changes; ${matchingCount} already match and were left unselected`
                    : 'configured values were incomplete; no stations were auto-selected';
                (0,__mcmsModuleContext.dispatchRecruitmentLog)(`${scanName} · ${typeName}: ${result.summary.eligible} editable assigned station${result.summary.eligible === 1 ? '' : 's'} across ${typeDetail} and ${assignmentDetail}; ${result.summary.outsideType} outside the selected type; ${result.summary.unassigned} unassigned; ${result.summary.unavailable} unavailable; ${selectionDetail}`);
                if (result.summary.truncated) (0,__mcmsModuleContext.dispatchRecruitmentLog)(`${result.summary.truncated} rows exceed the ${__mcmsModuleContext.DISPATCH_RECRUITMENT_SCAN_LIMIT}-station safety limit and were not selected`, 'warn');
                return result.queue;
            } catch (err) {
                (0,__mcmsModuleContext.clearDispatchRecruitmentScan)();
                __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = '';
                (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Station scan failed: ${err?.message || 'unknown error'}`, 'error');
                return [];
            }
        })();
        __mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise = scanPromise;
        (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
        try { return await scanPromise; }
        finally {
            if (__mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise === scanPromise) __mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise = null;
            (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
        }
    }),
"verifyDispatchRecruitmentMutation":__mcmsModuleContext=>(async function verifyDispatchRecruitmentMutation(item, expectedDispatchId, label, expected = () => true) {
        let lastRecord = null;
        for (const delay of [250, 500, 1000]) {
            const settled = await (0,__mcmsModuleContext.runtimeDelay)(delay);
            if (!settled) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)(`${label} was submitted, but the Toolkit stopped before its assignment could be verified.`);
            try {
                lastRecord = (0,__mcmsModuleContext.dispatchRecruitmentAssertStationScope)(await (0,__mcmsModuleContext.fetchDispatchRecruitmentBuilding)(item.buildingId), item, expectedDispatchId, true);
            } catch (err) {
                if (err?.dispatchRecruitmentFatal) throw err;
                if (delay === 1000) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)(`${label} was submitted, but authoritative Dispatch Centre verification failed. No further stations were changed.`);
                continue;
            }
            if (expected(lastRecord)) return lastRecord;
        }
        return lastRecord;
    }),
"prepareDispatchRecruitmentHiring":__mcmsModuleContext=>(async function prepareDispatchRecruitmentHiring(item, currentPhase, desiredPhase) {
        if (currentPhase === desiredPhase) return null;
        const { doc } = await (0,__mcmsModuleContext.fetchDispatchRecruitmentDocument)(`/buildings/${item.buildingId}/hire`);
        if (currentPhase === '0') {
            const desiredAction = (0,__mcmsModuleContext.dispatchRecruitmentNativeHireAction)(doc, item.buildingId, __mcmsModuleContext.DISPATCH_RECRUITMENT_PHASE_META[desiredPhase].token);
            if (!desiredAction) throw (0,__mcmsModuleContext.dispatchRecruitmentSafeSkip)(`native ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(desiredPhase)} Hiring Phase action is unavailable`);
            return { cancelAction: '', desiredAction, originalPhase: currentPhase, desiredPhase };
        }
        const cancelAction = (0,__mcmsModuleContext.dispatchRecruitmentNativeHireAction)(doc, item.buildingId, '0');
        if (!cancelAction) throw (0,__mcmsModuleContext.dispatchRecruitmentSafeSkip)('native Cancel recruitment phase action is unavailable');
        return { cancelAction, desiredAction: '', originalPhase: currentPhase, desiredPhase };
    }),
"runDispatchRecruitmentNativeAction":__mcmsModuleContext=>(async function runDispatchRecruitmentNativeAction(href, label) {
        const url = (0,__mcmsModuleContext.dispatchRecruitmentGuardMutation)(href);
        if (!/^\/buildings\/\d+\/hire_do\/(?:0|1|2|3|automatic)$/u.test(url.pathname) || url.search || url.hash) {
            throw (0,__mcmsModuleContext.dispatchRecruitmentSafeSkip)(`blocked an unexpected ${label} action`);
        }
        let response;
        try {
            response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
                method: 'GET',
                credentials: 'same-origin',
                cache: 'no-store',
                redirect: 'follow',
                headers: { Accept: 'text/html,application/xhtml+xml' },
                timeoutMs: __mcmsModuleContext.DISPATCH_RECRUITMENT_REQUEST_TIMEOUT_MS
            });
        } catch (err) {
            throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)(`${label} may have been submitted, but MissionChief did not return a verifiable response. No further stations were changed.`);
        }
        if (!response.ok) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)(`MissionChief returned HTTP ${response.status} after ${label}. No further stations were changed.`);
    }),
"applyDispatchRecruitmentHiring":__mcmsModuleContext=>(async function applyDispatchRecruitmentHiring(item, prepared) {
        if (!prepared) return false;
        if (!prepared.cancelAction) {
            await (0,__mcmsModuleContext.runDispatchRecruitmentNativeAction)(prepared.desiredAction, `${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(prepared.desiredPhase)} Hiring Phase`);
            return true;
        }
        try { await (0,__mcmsModuleContext.runDispatchRecruitmentNativeAction)(prepared.cancelAction, 'Cancel recruitment phase'); }
        catch (err) {
            err.message = `${err.message} The station may need manual recruitment review.`;
            throw err;
        }
        if (prepared.desiredPhase === '0') return true;
        let doc;
        try { ({ doc } = await (0,__mcmsModuleContext.fetchDispatchRecruitmentDocument)(`/buildings/${item.buildingId}/hire`)); }
        catch (err) { throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('the current Hiring Phase was cancelled, but MissionChief did not return the next native actions. No further stations were changed.'); }
        const desiredAction = (0,__mcmsModuleContext.dispatchRecruitmentNativeHireAction)(doc, item.buildingId, __mcmsModuleContext.DISPATCH_RECRUITMENT_PHASE_META[prepared.desiredPhase].token);
        if (!desiredAction) {
            const restoreAction = (0,__mcmsModuleContext.dispatchRecruitmentNativeHireAction)(doc, item.buildingId, __mcmsModuleContext.DISPATCH_RECRUITMENT_PHASE_META[prepared.originalPhase].token);
            if (!restoreAction) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)(`Recruitment was cancelled, but neither ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(prepared.desiredPhase)} nor the original ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(prepared.originalPhase)} action was available. No further stations were changed.`);
            await (0,__mcmsModuleContext.runDispatchRecruitmentNativeAction)(restoreAction, `restore ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(prepared.originalPhase)} Hiring Phase`);
            const error = (0,__mcmsModuleContext.dispatchRecruitmentSafeSkip)(`native ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(prepared.desiredPhase)} action was unavailable after cancellation; the original phase was restored`);
            error.dispatchRecruitmentMutationSubmitted = true;
            throw error;
        }
        try { await (0,__mcmsModuleContext.runDispatchRecruitmentNativeAction)(desiredAction, `${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(prepared.desiredPhase)} Hiring Phase`); }
        catch (err) {
            err.message = `${err.message} The previous phase was cancelled first, so this station needs manual recruitment review.`;
            throw err;
        }
        return true;
    }),
"submitDispatchRecruitmentPersonnel":__mcmsModuleContext=>(async function submitDispatchRecruitmentPersonnel(prepared) {
        const guardedAction = (0,__mcmsModuleContext.dispatchRecruitmentGuardMutation)(prepared.action, prepared.body);
        const actionNames = __mcmsModuleContext.Array.from(guardedAction.searchParams.keys());
        const bodyParams = new __mcmsModuleContext.URLSearchParams(prepared.body);
        const parameterNames = __mcmsModuleContext.Array.from(bodyParams.keys());
        const allowedNames = new __mcmsModuleContext.Set(['utf8', '_method', 'authenticity_token', 'building[personal_count_target]', 'commit']);
        if (!/^\/buildings\/\d+$/u.test(guardedAction.pathname)
            || guardedAction.hash
            || actionNames.length !== 1
            || actionNames[0] !== 'personal_count_target_only'
            || guardedAction.searchParams.get('personal_count_target_only') !== '1'
            || parameterNames.some(name => !allowedNames.has(name))
            || new __mcmsModuleContext.Set(parameterNames).size !== parameterNames.length
            || !['put', 'patch'].includes((0,__mcmsModuleContext.String)(bodyParams.get('_method') || '').toLowerCase())
            || !bodyParams.get('authenticity_token')
            || !/^\d+$/u.test((0,__mcmsModuleContext.String)(bodyParams.get('building[personal_count_target]') || ''))
            || !bodyParams.get('commit')) {
            throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('blocked an unexpected Personnel (Desired) mutation shape. No request was sent.');
        }
        let response;
        try {
            response = await (0,__mcmsModuleContext.runtimeFetch)(guardedAction.href, {
                method: 'POST',
                credentials: 'same-origin',
                cache: 'no-store',
                redirect: 'follow',
                headers: prepared.headers,
                body: prepared.body,
                timeoutMs: __mcmsModuleContext.DISPATCH_RECRUITMENT_REQUEST_TIMEOUT_MS
            });
        } catch (err) {
            throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('Personnel (Desired) may have been submitted, but MissionChief did not return a verifiable response. No further stations were changed.');
        }
        if (!response.ok) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)(`MissionChief returned HTTP ${response.status} after Personnel (Desired). No further stations were changed.`);
        return true;
    }),
"applyDispatchRecruitmentStation":__mcmsModuleContext=>(async function applyDispatchRecruitmentStation(item, plan) {
        const baseline = await (0,__mcmsModuleContext.fetchDispatchRecruitmentBuilding)(item.buildingId);
        const expectedDispatchId = (0,__mcmsModuleContext.String)(item.dispatchId || (plan.dispatchId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES ? '' : plan.dispatchId));
        if (!/^\d+$/u.test(expectedDispatchId)) throw (0,__mcmsModuleContext.dispatchRecruitmentSafeSkip)('scanned Dispatch Centre assignment is unavailable');
        (0,__mcmsModuleContext.dispatchRecruitmentAssertStationScope)(baseline, item, expectedDispatchId);
        const currentPhase = (0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(baseline);
        const personnelNeedsUpdate = (0,__mcmsModuleContext.Number)(baseline.personal_count_target) !== plan.personnelDesired;
        const hiringNeedsUpdate = currentPhase !== plan.hiringPhase;
        if (!personnelNeedsUpdate && !hiringNeedsUpdate) return { changed: false, record: baseline, detail: 'already matches' };
        let hiringChanged = false;
        let personnelChanged = false;
        let verified = baseline;
        const safeIssues = [];
        if (personnelNeedsUpdate) {
            let personnelSubmission = null;
            try {
                const { doc } = await (0,__mcmsModuleContext.fetchDispatchRecruitmentDocument)(item.targetEditPath);
                personnelSubmission = (0,__mcmsModuleContext.prepareDispatchRecruitmentPersonnelSubmission)(doc, item, plan.personnelDesired);
            } catch (err) {
                if (err?.dispatchRecruitmentFatal) throw err;
                safeIssues.push(`Personnel (Desired): ${err?.message || 'native edit form could not be prepared'}`);
            }
            if (personnelSubmission) {
                personnelChanged = await (0,__mcmsModuleContext.submitDispatchRecruitmentPersonnel)(personnelSubmission);
                verified = await (0,__mcmsModuleContext.verifyDispatchRecruitmentMutation)(item, expectedDispatchId, 'Personnel (Desired)', record => (0,__mcmsModuleContext.Number)(record?.personal_count_target) === plan.personnelDesired);
                if ((0,__mcmsModuleContext.Number)(verified.personal_count_target) !== plan.personnelDesired) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('MissionChief did not verify the requested Personnel (Desired). No further stations were changed.');
            }
        }
        if (hiringNeedsUpdate) {
            let hiringSubmission = null;
            try {
                hiringSubmission = await (0,__mcmsModuleContext.prepareDispatchRecruitmentHiring)(item, currentPhase, plan.hiringPhase);
            } catch (err) {
                if (err?.dispatchRecruitmentFatal) throw err;
                safeIssues.push(`Hiring Phase: ${err?.message || 'native recruitment action could not be prepared'}`);
            }
            if (hiringSubmission) {
                try {
                    hiringChanged = await (0,__mcmsModuleContext.applyDispatchRecruitmentHiring)(item, hiringSubmission);
                    verified = await (0,__mcmsModuleContext.verifyDispatchRecruitmentMutation)(item, expectedDispatchId, 'Hiring Phase', record => (0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(record) === plan.hiringPhase);
                    if ((0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(verified) !== plan.hiringPhase) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('MissionChief did not verify the requested Hiring Phase. No further stations were changed.');
                } catch (err) {
                    if (!err?.dispatchRecruitmentSafeSkip) throw err;
                    if (err.dispatchRecruitmentMutationSubmitted) {
                        verified = await (0,__mcmsModuleContext.verifyDispatchRecruitmentMutation)(item, expectedDispatchId, 'Hiring Phase restoration', record => (0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(record) === currentPhase);
                        if ((0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(verified) !== currentPhase) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('MissionChief did not verify the restored Hiring Phase. No further stations were changed.');
                    }
                    safeIssues.push(`Hiring Phase: ${err.message}`);
                }
            }
        }
        const changedFields = [hiringChanged ? 'Hiring Phase' : '', personnelChanged ? 'Personnel (Desired)' : ''].filter(__mcmsModuleContext.Boolean);
        if (!changedFields.length && safeIssues.length) throw (0,__mcmsModuleContext.dispatchRecruitmentSafeSkip)(safeIssues.join(' · '));
        if (!safeIssues.length && !(0,__mcmsModuleContext.dispatchRecruitmentRecordMatches)(verified, plan)) throw (0,__mcmsModuleContext.dispatchRecruitmentSafetyStop)('MissionChief did not verify both requested recruitment values. No further stations were changed.');
        const detail = safeIssues.length ? `${changedFields.join(' + ')} updated · ${safeIssues.join(' · ')}` : changedFields.join(' + ');
        return { changed: true, partial: safeIssues.length > 0, record: verified, detail };
    }),
"startDispatchRecruitment":__mcmsModuleContext=>(async function startDispatchRecruitment() {
        if (__mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise || __mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise || __mcmsModuleContext.stationIconCopierRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.preparing || __mcmsModuleContext.stationIconCopierRuntime.scanPromise || __mcmsModuleContext.stationIconCopierRuntime.catalogPromise || __mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return;
        let plan;
        try { plan = (0,__mcmsModuleContext.readDispatchRecruitmentPlan)(); }
        catch (err) { (0,__mcmsModuleContext.showToast)(err?.message || 'Check the Dispatch Recruitment values'); return; }
        if (!__mcmsModuleContext.dispatchRecruitmentRuntime.scannedAt || __mcmsModuleContext.dispatchRecruitmentRuntime.scannedDispatchId !== plan.dispatchId || __mcmsModuleContext.dispatchRecruitmentRuntime.scannedTypeId !== plan.buildingTypeId) {
            (0,__mcmsModuleContext.showToast)(`Scan the selected Dispatch Centre and building-type scope before applying recruitment`);
            return;
        }
        const planned = (0,__mcmsModuleContext.dispatchRecruitmentPlannedQueue)().map(item => ({ ...item }));
        if (!planned.length) { (0,__mcmsModuleContext.showToast)('Select at least one station to update'); return; }
        if (planned.length > __mcmsModuleContext.DISPATCH_RECRUITMENT_APPLY_LIMIT) {
            (0,__mcmsModuleContext.showToast)(`Select no more than ${__mcmsModuleContext.DISPATCH_RECRUITMENT_APPLY_LIMIT} stations per run`);
            return;
        }
        const allCentres = plan.dispatchId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES;
        const dispatch = allCentres ? null : __mcmsModuleContext.dispatchRecruitmentRuntime.dispatches.find(item => item.id === plan.dispatchId);
        if (!allCentres && !dispatch) { (0,__mcmsModuleContext.showToast)('The selected Dispatch Centre is no longer available'); return; }
        const plannedDispatchIds = new __mcmsModuleContext.Set(planned.map(item => (0,__mcmsModuleContext.String)(item.dispatchId || '')).filter(id => /^\d+$/u.test(id)));
        if (!plannedDispatchIds.size || plannedDispatchIds.size !== new __mcmsModuleContext.Set(planned.map(item => (0,__mcmsModuleContext.String)(item.dispatchId || ''))).size) {
            (0,__mcmsModuleContext.showToast)('One or more selected stations has no verified Dispatch Centre assignment');
            return;
        }
        const scopeSummary = allCentres
            ? `across ${plannedDispatchIds.size} Dispatch Centre${plannedDispatchIds.size === 1 ? '' : 's'}`
            : `in ${dispatch.name}`;
        const typeLabels = __mcmsModuleContext.Array.from(new __mcmsModuleContext.Set(planned.map(item => item.typeLabel)));
        const typeSummary = typeLabels.length <= 4 ? typeLabels.join(', ') : `${typeLabels.length} station types`;
        const confirmed = __mcmsModuleContext.pageWindow.confirm(`Dispatch Recruitment will update ${planned.length} selected station${planned.length === 1 ? '' : 's'} ${scopeSummary}.

Hiring Phase: ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(plan.hiringPhase)}
Personnel (Desired): ${plan.personnelDesired}
Types: ${typeSummary}

Each station will be rechecked against its exact scanned Dispatch Centre, submitted through MissionChief's current native controls one at a time, and verified before it is counted as updated. Unverified actions are never retried automatically. Continue?`);
        if (!confirmed) return;
        (0,__mcmsModuleContext.toolkitAnalyticsRecordFeature)('dispatchRecruitment');
        __mcmsModuleContext.dispatchRecruitmentRuntime.running = true;
        __mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested = false;
        __mcmsModuleContext.dispatchRecruitmentRuntime.log = [];
        (0,__mcmsModuleContext.resetDispatchRecruitmentResults)();
        (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Run started: ${planned.length} stations ${scopeSummary} · Hiring ${(0,__mcmsModuleContext.dispatchRecruitmentPhaseLabel)(plan.hiringPhase)} · Personnel (Desired) ${plan.personnelDesired}`);
        try {
            for (let index = 0; index < planned.length; index += 1) {
                if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested) break;
                const snapshot = planned[index];
                const item = __mcmsModuleContext.dispatchRecruitmentRuntime.queue.find(candidate => candidate.buildingId === snapshot.buildingId) || snapshot;
                __mcmsModuleContext.dispatchRecruitmentRuntime.currentBuildingId = item.buildingId;
                __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = item.name;
                (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
                (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Checking ${item.name}`);
                try {
                    const result = await (0,__mcmsModuleContext.applyDispatchRecruitmentStation)(item, plan);
                    if (result.changed) {
                        item.outcome = result.partial ? 'partial' : 'updated';
                        item.outcomeDetail = result.detail;
                        item.currentPhase = (0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(result.record);
                        item.currentDesired = (0,__mcmsModuleContext.Number)(result.record.personal_count_target);
                        if (result.partial) {
                            __mcmsModuleContext.dispatchRecruitmentRuntime.partial += 1;
                            (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Partially updated ${item.name}: ${result.detail}`, 'warn');
                        } else {
                            __mcmsModuleContext.dispatchRecruitmentRuntime.updated += 1;
                            (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Updated ${item.name}: ${result.detail}`);
                        }
                    } else {
                        item.outcome = 'unchanged';
                        item.outcomeDetail = result.detail;
                        item.currentPhase = (0,__mcmsModuleContext.dispatchRecruitmentRecordPhase)(result.record);
                        item.currentDesired = (0,__mcmsModuleContext.Number)(result.record.personal_count_target);
                        __mcmsModuleContext.dispatchRecruitmentRuntime.unchanged += 1;
                        (0,__mcmsModuleContext.dispatchRecruitmentLog)(`No change at ${item.name}: values already match`);
                    }
                } catch (err) {
                    item.outcomeDetail = (0,__mcmsModuleContext.String)(err?.message || 'unknown error');
                    if (err?.dispatchRecruitmentFatal) {
                        item.outcome = 'error';
                        __mcmsModuleContext.dispatchRecruitmentRuntime.errors += 1;
                        __mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested = true;
                        (0,__mcmsModuleContext.dispatchRecruitmentLog)(`SAFETY STOP at ${item.name}: ${item.outcomeDetail}`, 'error');
                    } else if (err?.dispatchRecruitmentSafeSkip) {
                        item.outcome = 'skipped';
                        __mcmsModuleContext.dispatchRecruitmentRuntime.skipped += 1;
                        (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Skipped ${item.name}: ${item.outcomeDetail}`, 'warn');
                    } else {
                        item.outcome = 'error';
                        __mcmsModuleContext.dispatchRecruitmentRuntime.errors += 1;
                        (0,__mcmsModuleContext.dispatchRecruitmentLog)(`Error at ${item.name}: ${item.outcomeDetail}`, 'error');
                    }
                } finally {
                    __mcmsModuleContext.dispatchRecruitmentRuntime.processed += 1;
                    (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
                }
                if (__mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested) break;
                if (index < planned.length - 1 && !__mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested) {
                    const completedDelay = await (0,__mcmsModuleContext.runtimeDelay)(plan.delayMs);
                    if (!completedDelay) break;
                }
            }
        } finally {
            const wasStopped = __mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested || __mcmsModuleContext.runtime.destroyed;
            __mcmsModuleContext.dispatchRecruitmentRuntime.running = false;
            __mcmsModuleContext.dispatchRecruitmentRuntime.stopRequested = false;
            __mcmsModuleContext.dispatchRecruitmentRuntime.currentBuildingId = '';
            __mcmsModuleContext.dispatchRecruitmentRuntime.currentItem = '';
            (0,__mcmsModuleContext.dispatchRecruitmentLog)(`${wasStopped ? 'Stopped' : 'Complete'}: ${__mcmsModuleContext.dispatchRecruitmentRuntime.updated} updated, ${__mcmsModuleContext.dispatchRecruitmentRuntime.partial} partial, ${__mcmsModuleContext.dispatchRecruitmentRuntime.unchanged} unchanged, ${__mcmsModuleContext.dispatchRecruitmentRuntime.skipped} skipped, ${__mcmsModuleContext.dispatchRecruitmentRuntime.errors} errors`, __mcmsModuleContext.dispatchRecruitmentRuntime.errors ? 'error' : __mcmsModuleContext.dispatchRecruitmentRuntime.partial ? 'warn' : 'info');
            (0,__mcmsModuleContext.showToast)(`${wasStopped ? 'Dispatch Recruitment stopped' : 'Dispatch Recruitment complete'} · ${__mcmsModuleContext.dispatchRecruitmentRuntime.updated} updated · ${__mcmsModuleContext.dispatchRecruitmentRuntime.partial} partial · ${__mcmsModuleContext.dispatchRecruitmentRuntime.unchanged} unchanged · ${__mcmsModuleContext.dispatchRecruitmentRuntime.skipped + __mcmsModuleContext.dispatchRecruitmentRuntime.errors} issues`);
            (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
        }
    }),
"fetchStationIconDocument":__mcmsModuleContext=>(async function fetchStationIconDocument(pathOrUrl) {
        const url = new __mcmsModuleContext.URL(pathOrUrl, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        if (url.origin !== __mcmsModuleContext.pageWindow.location.origin) throw new __mcmsModuleContext.Error('Blocked an unexpected external Station Icon Copier URL.');
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'text/html,application/xhtml+xml' },
            timeoutMs: __mcmsModuleContext.STATION_ICON_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} for ${url.pathname}.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || /\/users\/sign_in\/?$/u.test(finalUrl.pathname)) throw new __mcmsModuleContext.Error('MissionChief redirected Station Icon Copier away from the authenticated game page.');
        const html = await response.text();
        return { doc: new __mcmsModuleContext.DOMParser().parseFromString(html, 'text/html'), url: finalUrl.href };
    }),
"fetchStationIconBuildings":__mcmsModuleContext=>(async function fetchStationIconBuildings() {
        const url = new __mcmsModuleContext.URL('/api/v2/buildings', __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'application/json' },
            timeoutMs: __mcmsModuleContext.STATION_ICON_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} while loading owned stations.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || finalUrl.pathname.replace(/\/+$/u, '') !== '/api/v2/buildings') throw new __mcmsModuleContext.Error('MissionChief redirected the owned-station catalogue unexpectedly.');
        const payload = await response.json();
        const records = (0,__mcmsModuleContext.stationIconPayloadRecords)(payload).map(__mcmsModuleContext.normaliseStationIconRecord).filter(__mcmsModuleContext.Boolean);
        if (!__mcmsModuleContext.Array.isArray(payload?.result)) throw new __mcmsModuleContext.Error('MissionChief did not return the expected owned-station catalogue.');
        const reportedTotal = (0,__mcmsModuleContext.Number)(payload?.pagination?.total ?? payload?.pagination?.total_entries ?? payload?.total);
        if (__mcmsModuleContext.Number.isFinite(reportedTotal) && reportedTotal > records.length) throw new __mcmsModuleContext.Error(`MissionChief returned an incomplete owned-station catalogue (${records.length} of ${reportedTotal}).`);
        const unique = new __mcmsModuleContext.Map();
        for (const record of records) {
            if (unique.has(record.id)) throw new __mcmsModuleContext.Error(`MissionChief returned duplicate station ${record.id} records.`);
            unique.set(record.id, record);
        }
        return __mcmsModuleContext.Array.from(unique.values());
    }),
"fetchStationIconApiRecord":__mcmsModuleContext=>(async function fetchStationIconApiRecord(path, buildingId, { allowMissing = false } = {}) {
        const url = new __mcmsModuleContext.URL(path, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'application/json' },
            timeoutMs: __mcmsModuleContext.STATION_ICON_REQUEST_TIMEOUT_MS
        });
        if (allowMissing && [404, 405].includes((0,__mcmsModuleContext.Number)(response.status))) return null;
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} while checking station ${buildingId}.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || finalUrl.pathname.replace(/\/+$/u, '') !== url.pathname.replace(/\/+$/u, '')) throw new __mcmsModuleContext.Error(`MissionChief redirected station ${buildingId} data unexpectedly.`);
        const record = (0,__mcmsModuleContext.stationIconPayloadRecords)(await response.json())
            .map(__mcmsModuleContext.normaliseStationIconRecord)
            .find(item => item.id === (0,__mcmsModuleContext.String)(buildingId));
        if (!record) throw new __mcmsModuleContext.Error(`MissionChief did not return authoritative station ${buildingId} data.`);
        return record;
    }),
"fetchStationIconBuilding":__mcmsModuleContext=>(async function fetchStationIconBuilding(buildingId, { requireIcon = true } = {}) {
        const id = (0,__mcmsModuleContext.String)(buildingId || '');
        if (!/^\d+$/u.test(id)) throw new __mcmsModuleContext.Error('Invalid station identifier.');
        let record = null;
        if (__mcmsModuleContext.stationIconCopierRuntime.singleBuildingApi !== 'legacy') {
            record = await (0,__mcmsModuleContext.fetchStationIconApiRecord)(`/api/v2/buildings/${id}`, id, { allowMissing: __mcmsModuleContext.stationIconCopierRuntime.singleBuildingApi === '' });
            if (record) __mcmsModuleContext.stationIconCopierRuntime.singleBuildingApi = 'v2';
            else __mcmsModuleContext.stationIconCopierRuntime.singleBuildingApi = 'legacy';
        }
        if (!record) record = await (0,__mcmsModuleContext.fetchStationIconApiRecord)(`/api/buildings/${id}`, id);
        if (requireIcon && !record.hasCustomIconField) {
            const refreshed = (await (0,__mcmsModuleContext.fetchStationIconBuildings)()).find(item => item.id === id);
            if (!refreshed) throw new __mcmsModuleContext.Error(`Station ${id} disappeared from the owned-station catalogue.`);
            record = refreshed;
        }
        return record;
    }),
"fetchStationIconImagePrivileged":__mcmsModuleContext=>(async function fetchStationIconImagePrivileged(iconUrl, label) {
        const href = (0,__mcmsModuleContext.stationIconPrivilegedImageUrl)(iconUrl);
        let requested;
        try { requested = new __mcmsModuleContext.URL((0,__mcmsModuleContext.stationIconSafeUrl)(iconUrl)); } catch (err) { requested = null; }
        if (!href) {
            const host = requested?.hostname ? ` (${requested.hostname})` : '';
            throw new __mcmsModuleContext.Error(`The ${label} image host${host} is not an approved MissionChief upload host.`);
        }
        const response = await (0,__mcmsModuleContext.runtimeGmRequest)({
            method: 'GET',
            url: href,
            headers: { Accept: 'image/png,image/jpeg' },
            timeoutMs: __mcmsModuleContext.STATION_ICON_REQUEST_TIMEOUT_MS,
            responseType: 'arraybuffer',
            anonymous: true,
            messages: {
            network: `The ${label} upload host could not be reached.`,
            timeout: `The ${label} upload-host request timed out.`,
            abort: `The ${label} upload-host request was cancelled.`,
            create: `The ${label} upload-host request could not be created.`
            }
        });
        const status = (0,__mcmsModuleContext.Number)(response?.status) || 0;
        if (status < 200 || status >= 300) throw new __mcmsModuleContext.Error(`The ${label} host returned HTTP ${status || 'error'}.`);
        const finalHref = (0,__mcmsModuleContext.String)(response?.finalUrl || '').trim();
        if (!finalHref) throw new __mcmsModuleContext.Error(`The ${label} upload host did not expose its final response URL.`);
        const finalUrl = (0,__mcmsModuleContext.stationIconPrivilegedImageUrl)(finalHref);
        if (!finalUrl) throw new __mcmsModuleContext.Error(`The ${label} redirected outside the approved MissionChief upload host.`);
        const bytes = response?.response;
        const size = (0,__mcmsModuleContext.Number)(bytes?.byteLength);
        if (!__mcmsModuleContext.Number.isFinite(size) || size <= 0) throw new __mcmsModuleContext.Error(`The ${label} host did not return a readable image file.`);
        if (size > __mcmsModuleContext.STATION_ICON_MAX_BYTES) throw new __mcmsModuleContext.Error(`The ${label} exceeds the ${__mcmsModuleContext.Math.round(__mcmsModuleContext.STATION_ICON_MAX_BYTES / 1048576)} MB safety limit.`);
        const headerMime = (0,__mcmsModuleContext.stationIconResponseHeader)(response?.responseHeaders, 'content-type').split(';')[0].trim().toLowerCase();
        const blob = new __mcmsModuleContext.Blob([bytes], { type: headerMime });
        return (0,__mcmsModuleContext.stationIconInspectBlob)(blob, headerMime || blob.type);
    }),
"fetchStationIconImage":__mcmsModuleContext=>(async function fetchStationIconImage(iconUrl, label = 'station icon') {
        const href = (0,__mcmsModuleContext.stationIconSafeUrl)(iconUrl);
        if (!href) throw new __mcmsModuleContext.Error(`The ${label} URL is missing or unsafe.`);
        const url = new __mcmsModuleContext.URL(href);
        let response;
        try {
            response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
                method: 'GET',
                credentials: url.origin === __mcmsModuleContext.pageWindow.location.origin ? 'same-origin' : 'omit',
                mode: 'cors',
                cache: 'no-store',
                headers: { Accept: 'image/png,image/jpeg' },
                timeoutMs: __mcmsModuleContext.STATION_ICON_REQUEST_TIMEOUT_MS
            });
        } catch (err) {
            return (0,__mcmsModuleContext.fetchStationIconImagePrivileged)(url.href, label);
        }
        if (!response.ok) throw new __mcmsModuleContext.Error(`The ${label} host returned HTTP ${response.status}.`);
        const finalUrl = (0,__mcmsModuleContext.stationIconSafeUrl)(response.url || url.href);
        if (!finalUrl) throw new __mcmsModuleContext.Error(`The ${label} redirected to an unsafe URL.`);
        const blob = await response.blob();
        const headerMime = (0,__mcmsModuleContext.String)(response.headers?.get?.('content-type') || '').split(';')[0].trim().toLowerCase();
        return (0,__mcmsModuleContext.stationIconInspectBlob)(blob, headerMime || blob.type);
    }),
"submitStationIconForm":__mcmsModuleContext=>(async function submitStationIconForm(prepared, item) {
        const action = new __mcmsModuleContext.URL(prepared.action, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        if (action.origin !== __mcmsModuleContext.pageWindow.location.origin || action.pathname !== `/buildings/${item.buildingId}` || action.search || action.hash) {
            throw (0,__mcmsModuleContext.stationIconSafetyStop)('blocked an unexpected building-image mutation URL. No request was sent.');
        }
        let response;
        try {
            response = await (0,__mcmsModuleContext.runtimeFetch)(action.href, {
                method: 'POST',
                credentials: 'same-origin',
                cache: 'no-store',
                redirect: 'follow',
                headers: { Accept: 'text/html,application/xhtml+xml' },
                body: prepared.formData,
                timeoutMs: __mcmsModuleContext.STATION_ICON_REQUEST_TIMEOUT_MS
            });
        } catch (err) {
            throw (0,__mcmsModuleContext.stationIconSafetyStop)('the icon may have been submitted, but MissionChief did not return a verifiable response. No further stations were changed.');
        }
        if (!response.ok) throw (0,__mcmsModuleContext.stationIconSafetyStop)(`MissionChief returned HTTP ${response.status} after the icon upload. No further stations were changed.`);
        let finalUrl;
        try { finalUrl = new __mcmsModuleContext.URL(response.url || action.href, action.href); }
        catch (err) {
            throw (0,__mcmsModuleContext.stationIconSafetyStop)('MissionChief returned an unreadable destination after the icon upload. No further stations were changed.');
        }
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || /\/users\/sign_in\/?$/u.test(finalUrl.pathname)) {
            throw (0,__mcmsModuleContext.stationIconSafetyStop)('MissionChief redirected the submitted icon outside the authenticated building flow. No further stations were changed.');
        }
    }),
"prepareStationIconSource":__mcmsModuleContext=>(async function prepareStationIconSource(plan) {
        const scanned = __mcmsModuleContext.stationIconCopierRuntime.buildings.find(record => record.id === plan.sourceBuildingId);
        if (!scanned) throw new __mcmsModuleContext.Error('The selected source station is no longer in the loaded owned-station catalogue.');
        const current = await (0,__mcmsModuleContext.fetchStationIconBuilding)(plan.sourceBuildingId, { requireIcon: true });
        if (!current.hasCustomIcon || !current.customIconUrl) throw new __mcmsModuleContext.Error('The selected source station no longer has a readable custom icon.');
        const dispatchById = (0,__mcmsModuleContext.stationIconDispatchMap)();
        if (!(0,__mcmsModuleContext.stationIconRecordInScope)(current, plan.dispatchId, dispatchById)) throw new __mcmsModuleContext.Error('The source station moved outside the selected Dispatch Centre scope.');
        if (current.caption !== scanned.caption || (0,__mcmsModuleContext.stationIconTypeKey)(current) !== (0,__mcmsModuleContext.stationIconTypeKey)(scanned) || current.dispatchId !== scanned.dispatchId) {
            throw new __mcmsModuleContext.Error('The source station changed after the scan. Load and scan the plan again.');
        }
        const image = await (0,__mcmsModuleContext.fetchStationIconImage)(current.customIconUrl, `${current.caption} source icon`);
        return { ...image, record: current };
    }),
"applyStationIconToStation":__mcmsModuleContext=>(async function applyStationIconToStation(item, plan, sourceImage) {
        const baseline = plan.homeResponseBaseline || await (0,__mcmsModuleContext.fetchStationIconBuilding)(item.buildingId, { requireIcon: true });
        (0,__mcmsModuleContext.stationIconAssertTargetScope)(baseline, item);
        if (plan.replaceMode === __mcmsModuleContext.STATION_ICON_REPLACE_DEFAULTS && baseline.hasCustomIcon) throw (0,__mcmsModuleContext.stationIconSafeSkip)('an existing custom icon is now protected');
        if (plan.expectedIcon && !baseline.hasCustomIcon) throw Error('Original icon changed after preview. No upload sent.');
        if (baseline.hasCustomIcon) {
            if (!baseline.customIconUrl) throw (0,__mcmsModuleContext.stationIconSafeSkip)('the current custom icon URL is not safely readable');
            const currentImage = await (0,__mcmsModuleContext.fetchStationIconImage)(baseline.customIconUrl, `${item.name} current icon`);
            if (plan.expectedIcon && !(0,__mcmsModuleContext.stationIconImagesMatch)(currentImage, plan.expectedIcon)) throw Error('Original icon changed after preview. No upload sent.');
            if ((0,__mcmsModuleContext.stationIconImagesMatch)(currentImage, sourceImage)) return { changed: false, record: baseline, detail: 'already uses the source icon' };
        }
        const { doc } = await (0,__mcmsModuleContext.fetchStationIconDocument)(`/buildings/${item.buildingId}/edit`);
        const prepared = (0,__mcmsModuleContext.prepareStationIconSubmission)(doc, item, sourceImage);
        await (0,__mcmsModuleContext.submitStationIconForm)(prepared, item);
        const settled = await (0,__mcmsModuleContext.runtimeDelay)(250);
        if (!settled) throw (0,__mcmsModuleContext.stationIconSafetyStop)('the icon was submitted, but the Toolkit stopped before it could be verified.');
        let verified;
        try { verified = await (0,__mcmsModuleContext.fetchStationIconBuilding)(item.buildingId, { requireIcon: true }); }
        catch (err) { throw (0,__mcmsModuleContext.stationIconSafetyStop)('the icon was submitted, but authoritative station verification failed. No further stations were changed.'); }
        (0,__mcmsModuleContext.stationIconAssertUnchangedAfterMutation)(verified, baseline, item);
        if (!verified.hasCustomIcon || !verified.customIconUrl) throw (0,__mcmsModuleContext.stationIconSafetyStop)('MissionChief did not expose the saved custom icon after upload. No further stations were changed.');
        let savedImage;
        try { savedImage = await (0,__mcmsModuleContext.fetchStationIconImage)(verified.customIconUrl, `${item.name} saved icon`); }
        catch (err) { throw (0,__mcmsModuleContext.stationIconSafetyStop)(`the saved icon could not be verified: ${err?.message || 'image unavailable'}. No further stations were changed.`); }
        if (!(0,__mcmsModuleContext.stationIconImagesMatch)(savedImage, sourceImage)) throw (0,__mcmsModuleContext.stationIconSafetyStop)('the saved station icon does not match the selected source image. No further stations were changed.');
        return { changed: true, record: verified, detail: `${sourceImage.width}×${sourceImage.height}px ${sourceImage.mime === 'image/png' ? 'PNG' : 'JPEG'} verified` };
    }),
"loadStationIconCatalog":__mcmsModuleContext=>(async function loadStationIconCatalog({ force = false } = {}) {
        if (__mcmsModuleContext.stationIconCopierRuntime.catalogPromise) return __mcmsModuleContext.stationIconCopierRuntime.catalogPromise;
        if (__mcmsModuleContext.stationIconCopierRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.preparing || __mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return __mcmsModuleContext.stationIconCopierRuntime.buildings;
        if (!force && __mcmsModuleContext.stationIconCopierRuntime.catalogAt && __mcmsModuleContext.stationIconCopierRuntime.buildings.length) return __mcmsModuleContext.stationIconCopierRuntime.buildings;
        if (force) (0,__mcmsModuleContext.clearStationIconScan)({ preserveLog: true });
        __mcmsModuleContext.stationIconCopierRuntime.currentItem = 'Loading native Dispatch Centres and owned stations';
        const catalogPromise = (async () => {
            try {
                const { doc } = await (0,__mcmsModuleContext.fetchStationIconDocument)('/buildings/new');
                const nativeCatalog = (0,__mcmsModuleContext.parseDispatchRecruitmentCatalog)(doc);
                if (!nativeCatalog.dispatches.length) throw new __mcmsModuleContext.Error('MissionChief did not expose any Dispatch Centre options.');
                const buildings = await (0,__mcmsModuleContext.fetchStationIconBuildings)();
                __mcmsModuleContext.stationIconCopierRuntime.dispatches = nativeCatalog.dispatches;
                __mcmsModuleContext.stationIconCopierRuntime.typeLabels = nativeCatalog.typeLabels;
                __mcmsModuleContext.stationIconCopierRuntime.buildings = buildings;
                __mcmsModuleContext.stationIconCopierRuntime.catalogAt = __mcmsModuleContext.Date.now();
                __mcmsModuleContext.stationIconCopierRuntime.singleBuildingApi = '';
                const savedDispatchId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.stationIconCopier.dispatchId || '');
                const selectedDispatch = savedDispatchId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES
                    ? __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES
                    : nativeCatalog.dispatches.some(item => item.id === savedDispatchId) ? savedDispatchId : nativeCatalog.dispatches[0].id;
                __mcmsModuleContext.state.stationIconCopier.dispatchId = selectedDispatch;
                const sourceIds = new __mcmsModuleContext.Set((0,__mcmsModuleContext.stationIconSourceChoices)(selectedDispatch).map(record => record.id));
                if (!sourceIds.has((0,__mcmsModuleContext.String)(__mcmsModuleContext.state.stationIconCopier.sourceBuildingId || ''))) __mcmsModuleContext.state.stationIconCopier.sourceBuildingId = '';
                (0,__mcmsModuleContext.saveState)();
                __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
                const customCount = buildings.filter(record => record.hasCustomIcon && record.customIconUrl).length;
                (0,__mcmsModuleContext.stationIconLog)(`Loaded ${buildings.length} owned station${buildings.length === 1 ? '' : 's'} across ${nativeCatalog.dispatches.length} Dispatch Centre${nativeCatalog.dispatches.length === 1 ? '' : 's'} · ${customCount} usable custom-icon source${customCount === 1 ? '' : 's'}`);
                return buildings;
            } catch (err) {
                __mcmsModuleContext.stationIconCopierRuntime.dispatches = [];
                __mcmsModuleContext.stationIconCopierRuntime.typeLabels = {};
                __mcmsModuleContext.stationIconCopierRuntime.buildings = [];
                __mcmsModuleContext.stationIconCopierRuntime.catalogAt = 0;
                __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
                (0,__mcmsModuleContext.clearStationIconScan)({ preserveLog: true });
                (0,__mcmsModuleContext.stationIconLog)(`Station and icon load failed: ${err?.message || 'unknown error'}`, 'error');
                return [];
            }
        })();
        __mcmsModuleContext.stationIconCopierRuntime.catalogPromise = catalogPromise;
        (0,__mcmsModuleContext.renderStationIconCopierPanel)();
        try { return await catalogPromise; }
        finally {
            if (__mcmsModuleContext.stationIconCopierRuntime.catalogPromise === catalogPromise) __mcmsModuleContext.stationIconCopierRuntime.catalogPromise = null;
            (0,__mcmsModuleContext.renderStationIconCopierPanel)();
        }
    }),
"scanStationIconTargets":__mcmsModuleContext=>(async function scanStationIconTargets() {
        if (__mcmsModuleContext.stationIconCopierRuntime.scanPromise) return __mcmsModuleContext.stationIconCopierRuntime.scanPromise;
        if (__mcmsModuleContext.stationIconCopierRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.preparing || __mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return __mcmsModuleContext.stationIconCopierRuntime.queue;
        const scanPromise = (async () => {
            const buildings = await (0,__mcmsModuleContext.loadStationIconCatalog)({ force: true });
            if (!buildings.length || __mcmsModuleContext.runtime.destroyed) return [];
            const dispatchId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.stationIconCopier.dispatchId || '');
            const sourceBuildingId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.stationIconCopier.sourceBuildingId || '');
            const replaceMode = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.stationIconCopier.replaceMode || __mcmsModuleContext.STATION_ICON_REPLACE_DEFAULTS);
            __mcmsModuleContext.stationIconCopierRuntime.currentItem = 'Building the exact matching station preview';
            (0,__mcmsModuleContext.renderStationIconCopierPanel)();
            try {
                const result = (0,__mcmsModuleContext.buildStationIconCopyQueue)(buildings, dispatchId, sourceBuildingId, replaceMode, __mcmsModuleContext.stationIconCopierRuntime.dispatches);
                __mcmsModuleContext.stationIconCopierRuntime.queue = result.queue;
                __mcmsModuleContext.stationIconCopierRuntime.summary = result.summary;
                __mcmsModuleContext.stationIconCopierRuntime.scannedAt = __mcmsModuleContext.Date.now();
                __mcmsModuleContext.stationIconCopierRuntime.scannedDispatchId = dispatchId;
                __mcmsModuleContext.stationIconCopierRuntime.scannedSourceBuildingId = sourceBuildingId;
                __mcmsModuleContext.stationIconCopierRuntime.scannedReplaceMode = replaceMode;
                __mcmsModuleContext.stationIconCopierRuntime.selectedBuildingIds = new __mcmsModuleContext.Set(result.queue.map(item => item.buildingId));
                __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
                __mcmsModuleContext.stationIconCopierRuntime.log = [];
                (0,__mcmsModuleContext.resetStationIconResults)();
                const centreCount = __mcmsModuleContext.Object.keys(result.summary.dispatchCounts).length;
                (0,__mcmsModuleContext.stationIconLog)(`${result.summary.source.caption} · ${(0,__mcmsModuleContext.stationIconTypeLabel)(result.summary.source)}: ${result.summary.eligible} eligible target${result.summary.eligible === 1 ? '' : 's'} across ${centreCount} Dispatch Centre${centreCount === 1 ? '' : 's'} · ${result.summary.protectedCustom} existing custom icon${result.summary.protectedCustom === 1 ? '' : 's'} protected · source excluded`);
                if (result.summary.truncated) (0,__mcmsModuleContext.stationIconLog)(`${result.summary.truncated} matching stations exceed the ${__mcmsModuleContext.STATION_ICON_SCAN_LIMIT}-station safety limit and were not selected`, 'warn');
                return result.queue;
            } catch (err) {
                (0,__mcmsModuleContext.clearStationIconScan)({ preserveLog: true });
                __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
                (0,__mcmsModuleContext.stationIconLog)(`Target scan failed: ${err?.message || 'unknown error'}`, 'error');
                return [];
            }
        })();
        __mcmsModuleContext.stationIconCopierRuntime.scanPromise = scanPromise;
        (0,__mcmsModuleContext.renderStationIconCopierPanel)();
        try { return await scanPromise; }
        finally {
            if (__mcmsModuleContext.stationIconCopierRuntime.scanPromise === scanPromise) __mcmsModuleContext.stationIconCopierRuntime.scanPromise = null;
            (0,__mcmsModuleContext.renderStationIconCopierPanel)();
        }
    }),
"startStationIconCopier":__mcmsModuleContext=>(async function startStationIconCopier() {
        if (__mcmsModuleContext.stationIconCopierRuntime.running || __mcmsModuleContext.stationIconCopierRuntime.preparing || __mcmsModuleContext.stationIconCopierRuntime.scanPromise || __mcmsModuleContext.stationIconCopierRuntime.catalogPromise || __mcmsModuleContext.dispatchRecruitmentRuntime.running || __mcmsModuleContext.dispatchRecruitmentRuntime.scanPromise || __mcmsModuleContext.dispatchRecruitmentRuntime.catalogPromise || __mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return;
        let plan;
        try { plan = (0,__mcmsModuleContext.readStationIconPlan)(); }
        catch (err) { (0,__mcmsModuleContext.showToast)(err?.message || 'Check the Station Icon Copier values'); return; }
        if (!__mcmsModuleContext.stationIconCopierRuntime.scannedAt
            || __mcmsModuleContext.stationIconCopierRuntime.scannedDispatchId !== plan.dispatchId
            || __mcmsModuleContext.stationIconCopierRuntime.scannedSourceBuildingId !== plan.sourceBuildingId
            || __mcmsModuleContext.stationIconCopierRuntime.scannedReplaceMode !== plan.replaceMode) {
            (0,__mcmsModuleContext.showToast)('Scan this exact Dispatch Centre, source and protection policy before applying icons');
            return;
        }
        const planned = (0,__mcmsModuleContext.stationIconPlannedQueue)().map(item => ({ ...item }));
        if (!planned.length) { (0,__mcmsModuleContext.showToast)('Select at least one target station'); return; }
        if (planned.length > __mcmsModuleContext.STATION_ICON_APPLY_LIMIT) { (0,__mcmsModuleContext.showToast)(`Select no more than ${__mcmsModuleContext.STATION_ICON_APPLY_LIMIT} stations per run`); return; }
        __mcmsModuleContext.stationIconCopierRuntime.preparing = true;
        __mcmsModuleContext.stationIconCopierRuntime.currentItem = 'Downloading and verifying the selected source icon';
        (0,__mcmsModuleContext.renderStationIconCopierPanel)();
        (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
        let sourceImage;
        try { sourceImage = await (0,__mcmsModuleContext.prepareStationIconSource)(plan); }
        catch (err) {
            __mcmsModuleContext.stationIconCopierRuntime.preparing = false;
            __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
            (0,__mcmsModuleContext.stationIconLog)(`Source preparation failed: ${err?.message || 'unknown error'}`, 'error');
            (0,__mcmsModuleContext.showToast)(err?.message || 'The selected source icon could not be prepared');
            return;
        }
        __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
        const centreCount = new __mcmsModuleContext.Set(planned.map(item => item.dispatchId)).size;
        const scope = plan.dispatchId === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES ? `${centreCount} Dispatch Centre${centreCount === 1 ? '' : 's'}` : planned[0].dispatchName;
        const replaceWarning = plan.replaceMode === __mcmsModuleContext.STATION_ICON_REPLACE_ALL
            ? 'REPLACE MODE: existing custom icons in the selected target list will be overwritten.'
            : 'PROTECTED MODE: any station that gains a custom icon before its turn will be skipped.';
        const confirmed = __mcmsModuleContext.pageWindow.confirm(`Station Icon Copier will copy the icon from ${sourceImage.record.caption} to ${planned.length} selected ${sourceImage.record.small ? 'small ' : ''}${(0,__mcmsModuleContext.stationIconTypeLabel)(sourceImage.record).replace(/ · Small$/u, '')} station${planned.length === 1 ? '' : 's'} across ${scope}.

Source image: ${sourceImage.width}×${sourceImage.height}px ${sourceImage.mime === 'image/png' ? 'PNG' : 'JPEG'}
${replaceWarning}

Each target will be rechecked, submitted through its current native building-edit form one at a time, and pixel-verified before the next station starts. Unverified uploads are never retried automatically. Continue?`);
        if (!confirmed) {
            __mcmsModuleContext.stationIconCopierRuntime.preparing = false;
            (0,__mcmsModuleContext.renderStationIconCopierPanel)();
            (0,__mcmsModuleContext.renderDispatchRecruitmentPanel)();
            return;
        }
        (0,__mcmsModuleContext.toolkitAnalyticsRecordFeature)('stationIconCopier');
        __mcmsModuleContext.stationIconCopierRuntime.running = true;
        __mcmsModuleContext.stationIconCopierRuntime.preparing = false;
        __mcmsModuleContext.stationIconCopierRuntime.stopRequested = false;
        __mcmsModuleContext.stationIconCopierRuntime.log = [];
        (0,__mcmsModuleContext.resetStationIconResults)();
        __mcmsModuleContext.stationIconCopierRuntime.sourceImage = sourceImage;
        (0,__mcmsModuleContext.stationIconLog)(`Run started: ${planned.length} exact ${(0,__mcmsModuleContext.stationIconTypeLabel)(sourceImage.record)} target${planned.length === 1 ? '' : 's'} · ${replaceWarning}`);
        try {
            for (let index = 0; index < planned.length; index += 1) {
                if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.stationIconCopierRuntime.stopRequested) break;
                const snapshot = planned[index];
                const item = __mcmsModuleContext.stationIconCopierRuntime.queue.find(candidate => candidate.buildingId === snapshot.buildingId) || snapshot;
                __mcmsModuleContext.stationIconCopierRuntime.currentBuildingId = item.buildingId;
                __mcmsModuleContext.stationIconCopierRuntime.currentItem = item.name;
                (0,__mcmsModuleContext.renderStationIconCopierPanel)();
                (0,__mcmsModuleContext.stationIconLog)(`Checking ${item.name}`);
                try {
                    const result = await (0,__mcmsModuleContext.applyStationIconToStation)(item, plan, sourceImage);
                    if (result.changed) {
                        item.outcome = 'updated';
                        item.outcomeDetail = result.detail;
                        item.hasCustomIcon = true;
                        item.customIconUrl = result.record.customIconUrl;
                        __mcmsModuleContext.stationIconCopierRuntime.updated += 1;
                        (0,__mcmsModuleContext.stationIconLog)(`Updated ${item.name}: ${result.detail}`);
                    } else {
                        item.outcome = 'unchanged';
                        item.outcomeDetail = result.detail;
                        item.hasCustomIcon = true;
                        item.customIconUrl = result.record.customIconUrl;
                        __mcmsModuleContext.stationIconCopierRuntime.unchanged += 1;
                        (0,__mcmsModuleContext.stationIconLog)(`No change at ${item.name}: ${result.detail}`);
                    }
                } catch (err) {
                    item.outcomeDetail = (0,__mcmsModuleContext.String)(err?.message || 'unknown error');
                    if (err?.stationIconFatal) {
                        item.outcome = 'error';
                        __mcmsModuleContext.stationIconCopierRuntime.errors += 1;
                        __mcmsModuleContext.stationIconCopierRuntime.stopRequested = true;
                        (0,__mcmsModuleContext.stationIconLog)(`SAFETY STOP at ${item.name}: ${item.outcomeDetail}`, 'error');
                    } else if (err?.stationIconSafeSkip) {
                        item.outcome = 'skipped';
                        __mcmsModuleContext.stationIconCopierRuntime.skipped += 1;
                        (0,__mcmsModuleContext.stationIconLog)(`Skipped ${item.name}: ${item.outcomeDetail}`, 'warn');
                    } else {
                        item.outcome = 'error';
                        __mcmsModuleContext.stationIconCopierRuntime.errors += 1;
                        (0,__mcmsModuleContext.stationIconLog)(`Error at ${item.name}: ${item.outcomeDetail}`, 'error');
                    }
                } finally {
                    __mcmsModuleContext.stationIconCopierRuntime.processed += 1;
                    (0,__mcmsModuleContext.renderStationIconCopierPanel)();
                }
                if (__mcmsModuleContext.stationIconCopierRuntime.stopRequested) break;
                if (index < planned.length - 1) {
                    const completedDelay = await (0,__mcmsModuleContext.runtimeDelay)(plan.delayMs);
                    if (!completedDelay) break;
                }
            }
        } finally {
            const wasStopped = __mcmsModuleContext.stationIconCopierRuntime.stopRequested || __mcmsModuleContext.runtime.destroyed;
            __mcmsModuleContext.stationIconCopierRuntime.running = false;
            __mcmsModuleContext.stationIconCopierRuntime.stopRequested = false;
            __mcmsModuleContext.stationIconCopierRuntime.currentBuildingId = '';
            __mcmsModuleContext.stationIconCopierRuntime.currentItem = '';
            (0,__mcmsModuleContext.stationIconLog)(`${wasStopped ? 'Stopped' : 'Complete'}: ${__mcmsModuleContext.stationIconCopierRuntime.updated} updated, ${__mcmsModuleContext.stationIconCopierRuntime.unchanged} unchanged, ${__mcmsModuleContext.stationIconCopierRuntime.skipped} skipped, ${__mcmsModuleContext.stationIconCopierRuntime.errors} errors`, __mcmsModuleContext.stationIconCopierRuntime.errors ? 'error' : 'info');
            (0,__mcmsModuleContext.showToast)(`${wasStopped ? 'Station Icon Copier stopped' : 'Station Icon Copier complete'} · ${__mcmsModuleContext.stationIconCopierRuntime.updated} updated · ${__mcmsModuleContext.stationIconCopierRuntime.unchanged} unchanged · ${__mcmsModuleContext.stationIconCopierRuntime.skipped + __mcmsModuleContext.stationIconCopierRuntime.errors} issues`);
            (0,__mcmsModuleContext.renderStationIconCopierPanel)();
        }
    }),
"discoverExpansionPlannerActions":__mcmsModuleContext=>(async function discoverExpansionPlannerActions(detailDoc, record, operationKind = 'all') {
        const id = (0,__mcmsModuleContext.String)(record?.id || '');
        const detailPath = `/buildings/${id}`;
        const operations = [];
        const diagnostics = (0,__mcmsModuleContext.emptyExpansionPlannerDiscoveryDiagnostics)();
        let ambiguous = 0;
        if (operationKind === 'all' || operationKind === 'extension') {
            const parsed = (0,__mcmsModuleContext.parseExpansionPlannerActions)(detailDoc, record, 'extension', detailPath);
            operations.push(...parsed.operations);
            ambiguous += parsed.ambiguous;
            (0,__mcmsModuleContext.mergeExpansionPlannerDiscoveryDiagnostics)(diagnostics, parsed.diagnostics);
        }
        if (operationKind === 'all' || operationKind === 'level') {
            const direct = (0,__mcmsModuleContext.parseExpansionPlannerActions)(detailDoc, record, 'level', detailPath);
            operations.push(...direct.operations);
            ambiguous += direct.ambiguous;
            (0,__mcmsModuleContext.mergeExpansionPlannerDiscoveryDiagnostics)(diagnostics, direct.diagnostics);
            if (!direct.operations.length && !direct.ambiguous) {
                const navigation = (0,__mcmsModuleContext.expansionPlannerLevelNavigationReference)(detailDoc, id);
                if (navigation) {
                    diagnostics.levelNavigationFound += 1;
                    const page = await (0,__mcmsModuleContext.fetchExpansionPlannerDocument)(navigation.href);
                    const finalUrl = new __mcmsModuleContext.URL(page.url || navigation.href, navigation.href);
                    if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || finalUrl.pathname !== navigation.path || finalUrl.search || finalUrl.hash) throw new __mcmsModuleContext.Error(`MissionChief redirected station ${id}'s native expansion page unexpectedly.`);
                    diagnostics.levelPagesFetched += 1;
                    const parsed = (0,__mcmsModuleContext.parseExpansionPlannerActions)(page.doc, record, 'level', navigation.path);
                    operations.push(...parsed.operations);
                    ambiguous += parsed.ambiguous;
                    (0,__mcmsModuleContext.mergeExpansionPlannerDiscoveryDiagnostics)(diagnostics, parsed.diagnostics);
                } else diagnostics.levelNavigationMissing += 1;
            }
        }
        return { operations: operations.slice(0, __mcmsModuleContext.EXPANSION_PLANNER_OPERATION_LIMIT), ambiguous, diagnostics };
    }),
"fetchExpansionPlannerDocument":__mcmsModuleContext=>(async function fetchExpansionPlannerDocument(pathOrUrl) {
        const url = new __mcmsModuleContext.URL(pathOrUrl, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        if (url.origin !== __mcmsModuleContext.pageWindow.location.origin) throw new __mcmsModuleContext.Error('Blocked an unexpected external Expansion Planner URL.');
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET', credentials: 'same-origin', cache: 'no-store',
            headers: { Accept: 'text/html,application/xhtml+xml' }, timeoutMs: __mcmsModuleContext.EXPANSION_PLANNER_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} for ${url.pathname}.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || /\/users\/sign_in\/?$/u.test(finalUrl.pathname)) throw new __mcmsModuleContext.Error('MissionChief redirected Expansion Planner away from the authenticated game page.');
        return { doc: new __mcmsModuleContext.DOMParser().parseFromString(await response.text(), 'text/html'), url: finalUrl.href };
    }),
"fetchExpansionPlannerOperationDocument":__mcmsModuleContext=>(async function fetchExpansionPlannerOperationDocument(item) {
        const discoveryPath = (0,__mcmsModuleContext.expansionPlannerBoundDiscoveryPath)(item?.discoveryPath, item?.buildingId, item?.kind);
        if (!discoveryPath || discoveryPath !== item?.discoveryPath) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`${item?.name || 'the selected station'} lost its exact native discovery page. No request was sent.`);
        const page = await (0,__mcmsModuleContext.fetchExpansionPlannerDocument)(discoveryPath);
        const finalUrl = new __mcmsModuleContext.URL(page.url || discoveryPath, `${__mcmsModuleContext.pageWindow.location.origin}${discoveryPath}`);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || finalUrl.pathname !== discoveryPath || finalUrl.search || finalUrl.hash) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`${item.name}'s native discovery page redirected unexpectedly. No request was sent.`);
        return page;
    }),
"fetchExpansionPlannerRevalidationPages":__mcmsModuleContext=>(async function fetchExpansionPlannerRevalidationPages(item) {
        const detailPath = `/buildings/${item.buildingId}`;
        if (item.discoveryPath === detailPath) {
            const page = await (0,__mcmsModuleContext.fetchExpansionPlannerOperationDocument)(item);
            return { detailPage: page, operationPage: page };
        }
        const [detailPage, operationPage] = await __mcmsModuleContext.Promise.all([
            (0,__mcmsModuleContext.fetchExpansionPlannerDocument)(detailPath),
            (0,__mcmsModuleContext.fetchExpansionPlannerOperationDocument)(item)
        ]);
        return { detailPage, operationPage };
    }),
"fetchExpansionPlannerBuildings":__mcmsModuleContext=>(async function fetchExpansionPlannerBuildings() {
        const url = new __mcmsModuleContext.URL('/api/v2/buildings', __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET', credentials: 'same-origin', cache: 'no-store',
            headers: { Accept: 'application/json' }, timeoutMs: __mcmsModuleContext.EXPANSION_PLANNER_REQUEST_TIMEOUT_MS
        });
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} while loading owned stations.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || finalUrl.pathname.replace(/\/+$/u, '') !== '/api/v2/buildings') throw new __mcmsModuleContext.Error('MissionChief redirected the owned-station catalogue unexpectedly.');
        const payload = await response.json();
        if (!__mcmsModuleContext.Array.isArray(payload?.result)) throw new __mcmsModuleContext.Error('MissionChief did not return the expected owned-station catalogue.');
        const records = payload.result.map(__mcmsModuleContext.normaliseExpansionPlannerRecord).filter(__mcmsModuleContext.Boolean);
        const reportedTotal = (0,__mcmsModuleContext.Number)(payload?.pagination?.total ?? payload?.pagination?.total_entries ?? payload?.total);
        if (__mcmsModuleContext.Number.isFinite(reportedTotal) && reportedTotal > records.length) throw new __mcmsModuleContext.Error(`MissionChief returned an incomplete owned-station catalogue (${records.length} of ${reportedTotal}).`);
        const unique = new __mcmsModuleContext.Map();
        for (const record of records) {
            if (unique.has(record.id)) throw new __mcmsModuleContext.Error(`MissionChief returned duplicate station ${record.id} records.`);
            unique.set(record.id, record);
        }
        return __mcmsModuleContext.Array.from(unique.values());
    }),
"fetchExpansionPlannerApiRecord":__mcmsModuleContext=>(async function fetchExpansionPlannerApiRecord(path, buildingId, { allowMissing = false } = {}) {
        const url = new __mcmsModuleContext.URL(path, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        const response = await (0,__mcmsModuleContext.runtimeFetch)(url.href, {
            method: 'GET', credentials: 'same-origin', cache: 'no-store',
            headers: { Accept: 'application/json' }, timeoutMs: __mcmsModuleContext.EXPANSION_PLANNER_REQUEST_TIMEOUT_MS
        });
        if (allowMissing && [404, 405].includes((0,__mcmsModuleContext.Number)(response.status))) return null;
        if (!response.ok) throw new __mcmsModuleContext.Error(`MissionChief returned HTTP ${response.status} while checking station ${buildingId}.`);
        const finalUrl = new __mcmsModuleContext.URL(response.url || url.href, url.href);
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || finalUrl.pathname.replace(/\/+$/u, '') !== url.pathname.replace(/\/+$/u, '')) throw new __mcmsModuleContext.Error(`MissionChief redirected station ${buildingId} data unexpectedly.`);
        const payload = await response.json();
        const raw = __mcmsModuleContext.Array.isArray(payload?.result) ? payload.result.find(item => (0,__mcmsModuleContext.String)(item?.id) === (0,__mcmsModuleContext.String)(buildingId)) : payload?.result && typeof payload.result === 'object' ? payload.result : payload;
        const record = (0,__mcmsModuleContext.normaliseExpansionPlannerRecord)(raw);
        if (!record || record.id !== (0,__mcmsModuleContext.String)(buildingId)) throw new __mcmsModuleContext.Error(`MissionChief did not return authoritative station ${buildingId} data.`);
        return record;
    }),
"fetchExpansionPlannerBuilding":__mcmsModuleContext=>(async function fetchExpansionPlannerBuilding(buildingId) {
        const id = (0,__mcmsModuleContext.String)(buildingId || '');
        if (!/^\d+$/u.test(id)) throw new __mcmsModuleContext.Error('Invalid station identifier.');
        let record = null;
        if (__mcmsModuleContext.expansionPlannerRuntime.singleBuildingApi !== 'legacy') {
            record = await (0,__mcmsModuleContext.fetchExpansionPlannerApiRecord)(`/api/v2/buildings/${id}`, id, { allowMissing: __mcmsModuleContext.expansionPlannerRuntime.singleBuildingApi === '' });
            if (record) __mcmsModuleContext.expansionPlannerRuntime.singleBuildingApi = 'v2';
            else __mcmsModuleContext.expansionPlannerRuntime.singleBuildingApi = 'legacy';
        }
        return record || (0,__mcmsModuleContext.fetchExpansionPlannerApiRecord)(`/api/buildings/${id}`, id);
    }),
"loadExpansionPlannerCatalog":__mcmsModuleContext=>(async function loadExpansionPlannerCatalog({ force = false } = {}) {
        if (__mcmsModuleContext.expansionPlannerRuntime.catalogPromise) return __mcmsModuleContext.expansionPlannerRuntime.catalogPromise;
        if (__mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || (0,__mcmsModuleContext.expansionPlannerOtherDispatchBusy)()) return __mcmsModuleContext.expansionPlannerRuntime.buildings;
        if (!force && __mcmsModuleContext.expansionPlannerRuntime.catalogAt && __mcmsModuleContext.expansionPlannerRuntime.buildings.length) return __mcmsModuleContext.expansionPlannerRuntime.buildings;
        if (force) (0,__mcmsModuleContext.clearExpansionPlannerScan)({ preserveLog: true });
        __mcmsModuleContext.expansionPlannerRuntime.currentItem = 'Loading native Dispatch Centres and owned stations';
        const catalogPromise = (async () => {
            try {
                const [{ doc }, buildings] = await __mcmsModuleContext.Promise.all([(0,__mcmsModuleContext.fetchExpansionPlannerDocument)('/buildings/new'), (0,__mcmsModuleContext.fetchExpansionPlannerBuildings)()]);
                const catalog = (0,__mcmsModuleContext.parseDispatchRecruitmentCatalog)(doc);
                if (!catalog.dispatches.length) throw new __mcmsModuleContext.Error('MissionChief did not expose any Dispatch Centre options.');
                __mcmsModuleContext.expansionPlannerRuntime.dispatches = catalog.dispatches;
                __mcmsModuleContext.expansionPlannerRuntime.typeLabels = catalog.typeLabels;
                __mcmsModuleContext.expansionPlannerRuntime.buildings = buildings;
                __mcmsModuleContext.expansionPlannerRuntime.catalogAt = __mcmsModuleContext.Date.now();
                __mcmsModuleContext.expansionPlannerRuntime.singleBuildingApi = '';
                const savedDispatch = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.expansionPlanner.dispatchId || '');
                __mcmsModuleContext.state.expansionPlanner.dispatchId = savedDispatch === __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES ? savedDispatch : catalog.dispatches.some(item => item.id === savedDispatch) ? savedDispatch : catalog.dispatches[0].id;
                if (__mcmsModuleContext.state.expansionPlanner.buildingTypeId !== __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES && !__mcmsModuleContext.Object.prototype.hasOwnProperty.call(catalog.typeLabels, __mcmsModuleContext.state.expansionPlanner.buildingTypeId)) __mcmsModuleContext.state.expansionPlanner.buildingTypeId = __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES;
                (0,__mcmsModuleContext.saveState)();
                __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
                (0,__mcmsModuleContext.expansionPlannerLog)(`Loaded ${buildings.length} owned station${buildings.length === 1 ? '' : 's'} across ${catalog.dispatches.length} Dispatch Centre${catalog.dispatches.length === 1 ? '' : 's'}`);
                return buildings;
            } catch (err) {
                __mcmsModuleContext.expansionPlannerRuntime.dispatches = [];
                __mcmsModuleContext.expansionPlannerRuntime.typeLabels = {};
                __mcmsModuleContext.expansionPlannerRuntime.buildings = [];
                __mcmsModuleContext.expansionPlannerRuntime.catalogAt = 0;
                __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
                (0,__mcmsModuleContext.clearExpansionPlannerScan)({ preserveLog: true });
                (0,__mcmsModuleContext.expansionPlannerLog)(`Station load failed: ${err?.message || 'unknown error'}`, 'error');
                return [];
            }
        })();
        __mcmsModuleContext.expansionPlannerRuntime.catalogPromise = catalogPromise;
        (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
        try { return await catalogPromise; }
        finally { __mcmsModuleContext.expansionPlannerRuntime.catalogPromise = null; (0,__mcmsModuleContext.renderExpansionPlannerPanel)(); }
    }),
"scanExpansionPlanner":__mcmsModuleContext=>(async function scanExpansionPlanner() {
        if (__mcmsModuleContext.expansionPlannerRuntime.scanPromise) return __mcmsModuleContext.expansionPlannerRuntime.queue;
        if (__mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || (0,__mcmsModuleContext.expansionPlannerOtherDispatchBusy)()) return __mcmsModuleContext.expansionPlannerRuntime.queue;
        const scanPromise = (async () => {
            const buildings = await (0,__mcmsModuleContext.loadExpansionPlannerCatalog)({ force: true });
            if (!buildings.length || __mcmsModuleContext.runtime.destroyed) return [];
            const dispatchId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.expansionPlanner.dispatchId || '');
            const typeId = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.expansionPlanner.buildingTypeId || __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES);
            const operationKind = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.expansionPlanner.operationKind || 'all');
            const maxStations = __mcmsModuleContext.Math.round((0,__mcmsModuleContext.clamp)(__mcmsModuleContext.state.expansionPlanner.maxStations, 1, __mcmsModuleContext.EXPANSION_PLANNER_SCAN_STATION_LIMIT, 100));
            if (dispatchId !== __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_CENTRES && !__mcmsModuleContext.expansionPlannerRuntime.dispatches.some(item => item.id === dispatchId)) throw new __mcmsModuleContext.Error('Choose a Dispatch Centre loaded from MissionChief.');
            if (typeId !== __mcmsModuleContext.DISPATCH_RECRUITMENT_ALL_TYPES && !__mcmsModuleContext.Object.prototype.hasOwnProperty.call(__mcmsModuleContext.expansionPlannerRuntime.typeLabels, typeId)) throw new __mcmsModuleContext.Error('Choose a building type loaded from MissionChief.');
            if (!__mcmsModuleContext.EXPANSION_PLANNER_OPERATION_OPTIONS.includes(operationKind)) throw new __mcmsModuleContext.Error('Choose a valid upgrade type.');
            const scoped = (0,__mcmsModuleContext.expansionPlannerScopedBuildings)();
            const targets = scoped.slice(0, maxStations);
            const dispatchNames = new __mcmsModuleContext.Map(__mcmsModuleContext.expansionPlannerRuntime.dispatches.map(item => [item.id, item.name]));
            const queue = [];
            const summary = {
                scoped: scoped.length, scanned: 0, eligibleStations: 0, operations: 0, pending: 0, unavailable: 0, ambiguous: 0,
                truncatedStations: __mcmsModuleContext.Math.max(0, scoped.length - targets.length), unavailableNames: [],
                inspectedControls: 0, creditControls: 0, priceRejected: 0, routeRejected: 0, methodRejected: 0, acceptedControls: 0,
                levelNavigationFound: 0, levelNavigationMissing: 0, levelPagesFetched: 0
            };
            let cursor = 0;
            __mcmsModuleContext.expansionPlannerRuntime.stopRequested = false;
            const worker = async () => {
                while (!__mcmsModuleContext.runtime.destroyed && !__mcmsModuleContext.expansionPlannerRuntime.stopRequested) {
                    const index = cursor++;
                    if (index >= targets.length) break;
                    const record = targets[index];
                    __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = record.id;
                    __mcmsModuleContext.expansionPlannerRuntime.currentItem = `Scanning ${index + 1}/${targets.length} · ${record.caption}`;
                    (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
                    try {
                        const { doc } = await (0,__mcmsModuleContext.fetchExpansionPlannerDocument)(`/buildings/${record.id}`);
                        summary.scanned += 1;
                        if ((0,__mcmsModuleContext.expansionPlannerHasPendingConstruction)(record, doc)) { summary.pending += 1; continue; }
                        const parsed = await (0,__mcmsModuleContext.discoverExpansionPlannerActions)(doc, record, operationKind);
                        summary.ambiguous += parsed.ambiguous;
                        for (const key of __mcmsModuleContext.Object.keys(parsed.diagnostics)) summary[key] += __mcmsModuleContext.Math.max(0, (0,__mcmsModuleContext.Number)(parsed.diagnostics[key]) || 0);
                        if (!parsed.operations.length) { summary.unavailable += 1; continue; }
                        summary.eligibleStations += 1;
                        for (const operation of parsed.operations) {
                            if (queue.length >= __mcmsModuleContext.EXPANSION_PLANNER_OPERATION_LIMIT) break;
                            queue.push((0,__mcmsModuleContext.expansionPlannerPublicOperation)(operation, record, dispatchNames.get(record.dispatchId) || `Dispatch Centre ${record.dispatchId}`, __mcmsModuleContext.expansionPlannerRuntime.typeLabels[record.typeId] || `Building type ${record.typeId}`));
                        }
                    } catch (err) {
                        summary.unavailable += 1;
                        if (summary.unavailableNames.length < 20) summary.unavailableNames.push(`${record.caption}: ${err?.message || 'unavailable'}`);
                    }
                }
            };
            await __mcmsModuleContext.Promise.all(__mcmsModuleContext.Array.from({ length: __mcmsModuleContext.Math.min(__mcmsModuleContext.EXPANSION_PLANNER_SCAN_CONCURRENCY, targets.length || 1) }, worker));
            queue.sort((left, right) => left.name.localeCompare(right.name, __mcmsModuleContext.undefined, { sensitivity: 'base', numeric: true }) || left.label.localeCompare(right.label, __mcmsModuleContext.undefined, { sensitivity: 'base', numeric: true }));
            summary.operations = queue.length;
            __mcmsModuleContext.expansionPlannerRuntime.queue = queue;
            __mcmsModuleContext.expansionPlannerRuntime.summary = summary;
            __mcmsModuleContext.expansionPlannerRuntime.scannedAt = __mcmsModuleContext.Date.now();
            __mcmsModuleContext.expansionPlannerRuntime.scannedDispatchId = dispatchId;
            __mcmsModuleContext.expansionPlannerRuntime.scannedTypeId = typeId;
            __mcmsModuleContext.expansionPlannerRuntime.scannedOperationKind = operationKind;
            __mcmsModuleContext.expansionPlannerRuntime.scannedMaxStations = maxStations;
            __mcmsModuleContext.expansionPlannerRuntime.selectedOperationIds = new __mcmsModuleContext.Set();
            __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = '';
            __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
            (0,__mcmsModuleContext.resetExpansionPlannerResults)();
            (0,__mcmsModuleContext.expansionPlannerLog)(`Scan complete: ${queue.length} live Credit action${queue.length === 1 ? '' : 's'} across ${summary.eligibleStations} station${summary.eligibleStations === 1 ? '' : 's'} · ${summary.levelPagesFetched} native expansion page${summary.levelPagesFetched === 1 ? '' : 's'} checked · nothing selected`);
            return queue;
        })();
        __mcmsModuleContext.expansionPlannerRuntime.scanPromise = scanPromise;
        (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
        try { return await scanPromise; }
        catch (err) { (0,__mcmsModuleContext.expansionPlannerLog)(`Scan failed: ${err?.message || 'unknown error'}`, 'error'); return []; }
        finally { __mcmsModuleContext.expansionPlannerRuntime.scanPromise = null; __mcmsModuleContext.expansionPlannerRuntime.stopRequested = false; __mcmsModuleContext.expansionPlannerRuntime.currentItem = ''; (0,__mcmsModuleContext.renderExpansionPlannerPanel)(); }
    }),
"preflightExpansionPlannerSelection":__mcmsModuleContext=>(async function preflightExpansionPlannerSelection(items) {
        const fresh = [];
        for (let index = 0; index < items.length; index += 1) {
            if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.expansionPlannerRuntime.stopRequested) throw new __mcmsModuleContext.Error('Expansion Planner preparation stopped.');
            const item = items[index];
            __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = item.buildingId;
            __mcmsModuleContext.expansionPlannerRuntime.currentItem = `Revalidating ${index + 1}/${items.length} · ${item.name}`;
            (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
            const [record, pages] = await __mcmsModuleContext.Promise.all([(0,__mcmsModuleContext.fetchExpansionPlannerBuilding)(item.buildingId), (0,__mcmsModuleContext.fetchExpansionPlannerRevalidationPages)(item)]);
            if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.expansionPlannerRuntime.stopRequested) throw (0,__mcmsModuleContext.expansionPlannerStoppedBeforeMutation)('Expansion Planner preparation stopped before confirmation. No request was sent.');
            (0,__mcmsModuleContext.expansionPlannerAssertScope)(record, item);
            if (record.level !== item.level || (0,__mcmsModuleContext.expansionPlannerExtensionDigest)(record) !== item.extensionDigest) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`${item.name}'s level or extension state changed after the scan. Scan again before purchasing.`);
            if ((0,__mcmsModuleContext.expansionPlannerHasPendingConstruction)(record, pages.detailPage.doc)) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`${item.name} now has an expansion under construction. No request was sent.`);
            (0,__mcmsModuleContext.expansionPlannerFindCurrentAction)(pages.operationPage.doc, record, item);
            fresh.push({ ...item, level: record.level, extensionDigest: (0,__mcmsModuleContext.expansionPlannerExtensionDigest)(record) });
        }
        return fresh;
    }),
"submitExpansionPlannerOperation":__mcmsModuleContext=>(async function submitExpansionPlannerOperation(prepared, item) {
        const action = new __mcmsModuleContext.URL(prepared.href, __mcmsModuleContext.document.baseURI || __mcmsModuleContext.pageWindow.location.href);
        const method = (0,__mcmsModuleContext.String)(prepared.method || '').toUpperCase();
        if (action.origin !== __mcmsModuleContext.pageWindow.location.origin || action.pathname !== item.actionPath || action.search !== item.actionSearch || action.hash || !['GET', 'POST'].includes(method) || method.toLowerCase() !== item.requestMethod || (method === 'GET' && prepared.body !== null)) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('blocked an unexpected purchase URL or method. No request was sent.');
        let response;
        try {
            response = await (0,__mcmsModuleContext.runtimeFetch)(action.href, {
                method, credentials: 'same-origin', cache: 'no-store', redirect: 'follow',
                headers: prepared.headers, body: prepared.body, timeoutMs: __mcmsModuleContext.EXPANSION_PLANNER_REQUEST_TIMEOUT_MS
            });
        } catch (err) {
            throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('MissionChief may have received the purchase, but its response could not be verified. No further purchases were attempted.');
        }
        if (!response.ok) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`MissionChief returned HTTP ${response.status} after the purchase. No further purchases were attempted.`);
        let finalUrl;
        try { finalUrl = new __mcmsModuleContext.URL(response.url || action.href, action.href); }
        catch (err) { throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('MissionChief returned an unreadable destination after the purchase. No further purchases were attempted.'); }
        if (finalUrl.origin !== __mcmsModuleContext.pageWindow.location.origin || /\/users\/sign_in\/?$/u.test(finalUrl.pathname)) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('MissionChief redirected the purchase outside the authenticated building flow. No further purchases were attempted.');
    }),
"applyExpansionPlannerOperation":__mcmsModuleContext=>(async function applyExpansionPlannerOperation(item, budgetRemaining) {
        const [before, pages] = await __mcmsModuleContext.Promise.all([(0,__mcmsModuleContext.fetchExpansionPlannerBuilding)(item.buildingId), (0,__mcmsModuleContext.fetchExpansionPlannerRevalidationPages)(item)]);
        (0,__mcmsModuleContext.expansionPlannerAssertScope)(before, item);
        if (before.level !== item.level || (0,__mcmsModuleContext.expansionPlannerExtensionDigest)(before) !== item.extensionDigest) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`${item.name}'s level or extension state changed after final confirmation. No request was sent.`);
        if ((0,__mcmsModuleContext.expansionPlannerHasPendingConstruction)(before, pages.detailPage.doc)) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`${item.name} has an expansion under construction. No request was sent.`);
        const operation = (0,__mcmsModuleContext.expansionPlannerFindCurrentAction)(pages.operationPage.doc, before, item);
        if (operation.priceCredits > budgetRemaining) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`the remaining hard budget is lower than ${item.name}'s live price. No request was sent.`);
        if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.expansionPlannerRuntime.stopRequested) throw (0,__mcmsModuleContext.expansionPlannerStoppedBeforeMutation)(`${item.name}'s purchase was stopped before submission. No request was sent.`);
        const prepared = (0,__mcmsModuleContext.prepareExpansionPlannerSubmission)(operation, pages.operationPage.doc);
        await (0,__mcmsModuleContext.submitExpansionPlannerOperation)(prepared, item);
        if (!await (0,__mcmsModuleContext.runtimeDelay)(350)) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('the purchase was submitted, but the Toolkit stopped before verification.');
        // A max-level hospital may no longer expose its expansion page.
        // Verify the authoritative owned record instead of requiring that page.
        if (item.hospitalTargetLevel) {
            if (item.typeId !== '4' || item.kind !== 'level' || item.actionSuffix !== 'expand_do/credits'
                || !Number.isInteger(item.hospitalTargetLevel) || item.hospitalTargetLevel <= before.level || item.hospitalTargetLevel > 30) {
                throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('Invalid hospital target after submission. Review the saved purchase before continuing.');
            }
            let hospitalAfter;
            try { hospitalAfter = await (0,__mcmsModuleContext.fetchExpansionPlannerBuilding)(item.buildingId); }
            catch (err) { throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`Hospital purchase was submitted, but its current level could not be read: ${err?.message || 'unknown read error'}. Use Review & resume to verify it; no purchase will be repeated.`); }
            (0,__mcmsModuleContext.expansionPlannerAssertScope)(hospitalAfter, item, true);
            if (hospitalAfter.level !== item.hospitalTargetLevel) {
                throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`Hospital purchase was submitted, but the game reports level ${hospitalAfter.level}; expected ${item.hospitalTargetLevel}. Use Review & resume to verify it; no purchase will be repeated.`);
            }
            return { record: hospitalAfter, detail: `Level ${hospitalAfter.level} · ${item.priceCredits.toLocaleString()} Credits verified` };
        }
        let after;
        let verifiedPages;
        try { [after, verifiedPages] = await __mcmsModuleContext.Promise.all([(0,__mcmsModuleContext.fetchExpansionPlannerBuilding)(item.buildingId), (0,__mcmsModuleContext.fetchExpansionPlannerRevalidationPages)(item)]); }
        catch (err) { throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)('the purchase was submitted, but authoritative station verification failed. No further purchases were attempted.'); }
        (0,__mcmsModuleContext.expansionPlannerAssertScope)(after, item, true);
        const stillOffered = (0,__mcmsModuleContext.parseExpansionPlannerActions)(verifiedPages.operationPage.doc, after, item.kind, item.discoveryPath).operations.some(candidate => candidate.fingerprint === item.fingerprint);
        if (stillOffered) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`MissionChief still exposes ${item.name}'s exact purchased action. No further purchases were attempted.`);
        if (item.kind === 'level') {
            const verified = item.actionSuffix === 'small_expand' ? before.small && !after.small : after.level === (item.hospitalTargetLevel || before.level + 1);
            if (!verified) throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`MissionChief did not verify ${item.name}'s requested level/bay upgrade. No further purchases were attempted.`);
        } else if ((0,__mcmsModuleContext.expansionPlannerExtensionDigest)(after) === (0,__mcmsModuleContext.expansionPlannerExtensionDigest)(before)) {
            throw (0,__mcmsModuleContext.expansionPlannerSafetyStop)(`MissionChief did not verify ${item.name}'s requested extension state. No further purchases were attempted.`);
        }
        return { record: after, detail: `${item.label} · ${item.priceCredits.toLocaleString()} Credits verified` };
    }),
"startExpansionPlanner":__mcmsModuleContext=>(async function startExpansionPlanner() {
        if (__mcmsModuleContext.expansionPlannerRuntime.running || __mcmsModuleContext.expansionPlannerRuntime.preparing || __mcmsModuleContext.expansionPlannerRuntime.scanPromise || __mcmsModuleContext.expansionPlannerRuntime.catalogPromise || (0,__mcmsModuleContext.expansionPlannerOtherDispatchBusy)()) return;
        const freshScope = __mcmsModuleContext.expansionPlannerRuntime.scannedAt
            && __mcmsModuleContext.expansionPlannerRuntime.scannedDispatchId === __mcmsModuleContext.state.expansionPlanner.dispatchId
            && __mcmsModuleContext.expansionPlannerRuntime.scannedTypeId === __mcmsModuleContext.state.expansionPlanner.buildingTypeId
            && __mcmsModuleContext.expansionPlannerRuntime.scannedOperationKind === __mcmsModuleContext.state.expansionPlanner.operationKind
            && __mcmsModuleContext.expansionPlannerRuntime.scannedMaxStations === (0,__mcmsModuleContext.Number)(__mcmsModuleContext.state.expansionPlanner.maxStations);
        if (!freshScope) { (0,__mcmsModuleContext.showToast)('Scan this exact Dispatch Centre, building type, upgrade type and station limit before purchasing'); return; }
        const planned = (0,__mcmsModuleContext.expansionPlannerPlannedQueue)().map(item => ({ ...item }));
        if (!planned.length) { (0,__mcmsModuleContext.showToast)('Select at least one upgrade or extension'); return; }
        if (planned.length > __mcmsModuleContext.EXPANSION_PLANNER_APPLY_LIMIT || new __mcmsModuleContext.Set(planned.map(item => item.buildingId)).size !== planned.length) { (0,__mcmsModuleContext.showToast)(`Choose at most one operation per station and ${__mcmsModuleContext.EXPANSION_PLANNER_APPLY_LIMIT} per run`); return; }
        const budgetText = (0,__mcmsModuleContext.String)(__mcmsModuleContext.state.expansionPlanner.creditBudget || '').trim();
        if (!/^\d+$/u.test(budgetText) || (0,__mcmsModuleContext.Number)(budgetText) < 1 || (0,__mcmsModuleContext.Number)(budgetText) > __mcmsModuleContext.EXPANSION_PLANNER_MAX_BUDGET) { (0,__mcmsModuleContext.showToast)(`Set a hard Credit budget from 1 to ${__mcmsModuleContext.EXPANSION_PLANNER_MAX_BUDGET.toLocaleString()}`); return; }
        const budget = (0,__mcmsModuleContext.Number)(budgetText);
        __mcmsModuleContext.expansionPlannerRuntime.preparing = true;
        __mcmsModuleContext.expansionPlannerRuntime.stopRequested = false;
        (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
        let confirmedPlan;
        try { confirmedPlan = await (0,__mcmsModuleContext.preflightExpansionPlannerSelection)(planned); }
        catch (err) {
            const stopped = (0,__mcmsModuleContext.Boolean)(err?.expansionPlannerStoppedBeforeMutation);
            __mcmsModuleContext.expansionPlannerRuntime.preparing = false;
            if (stopped) __mcmsModuleContext.expansionPlannerRuntime.stopRequested = false;
            __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = '';
            __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
            (0,__mcmsModuleContext.expansionPlannerLog)(err?.message || 'Final plan revalidation failed', stopped ? 'warn' : 'error');
            (0,__mcmsModuleContext.showToast)(err?.message || 'Final plan revalidation failed');
            return;
        }
        const total = confirmedPlan.reduce((sum, item) => sum + item.priceCredits, 0);
        if (!__mcmsModuleContext.Number.isSafeInteger(total) || total > budget) {
            __mcmsModuleContext.expansionPlannerRuntime.preparing = false;
            __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = '';
            __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
            (0,__mcmsModuleContext.expansionPlannerLog)(`Plan blocked: ${total.toLocaleString()} Credits exceeds the ${budget.toLocaleString()} Credit hard budget`, 'error');
            (0,__mcmsModuleContext.showToast)('The freshly revalidated total exceeds the hard Credit budget');
            return;
        }
        const levels = confirmedPlan.filter(item => item.kind === 'level').length;
        const extensions = confirmedPlan.length - levels;
        const sample = confirmedPlan.slice(0, 8).map(item => `• ${item.name}: ${item.label} — ${item.priceCredits.toLocaleString()} Credits`).join('\n');
        const more = confirmedPlan.length > 8 ? `\n• + ${confirmedPlan.length - 8} more selected operation${confirmedPlan.length - 8 === 1 ? '' : 's'}` : '';
        const confirmed = __mcmsModuleContext.pageWindow.confirm(`Expansion & Upgrade Planner has freshly revalidated ${confirmedPlan.length} selected operation${confirmedPlan.length === 1 ? '' : 's'}.

${sample}${more}

Level / bay upgrades: ${levels}
Extensions: ${extensions}
EXACT TOTAL: ${total.toLocaleString()} Credits
HARD BUDGET: ${budget.toLocaleString()} Credits
UNSPENT BUDGET: ${(budget - total).toLocaleString()} Credits

Credits only. Each station and native action will be fetched again, purchased one at a time and verified before the next starts. A submitted but unverified purchase stops the complete run and is never retried automatically. Continue?`);
        if (!confirmed) {
            __mcmsModuleContext.expansionPlannerRuntime.preparing = false;
            __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = '';
            __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
            (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
            return;
        }
        (0,__mcmsModuleContext.toolkitAnalyticsRecordFeature)('expansionPlanner');
        __mcmsModuleContext.expansionPlannerRuntime.running = true;
        __mcmsModuleContext.expansionPlannerRuntime.preparing = false;
        __mcmsModuleContext.expansionPlannerRuntime.stopRequested = false;
        __mcmsModuleContext.expansionPlannerRuntime.startedAt = __mcmsModuleContext.Date.now();
        __mcmsModuleContext.expansionPlannerRuntime.log = [];
        (0,__mcmsModuleContext.resetExpansionPlannerResults)();
        (0,__mcmsModuleContext.expansionPlannerLog)(`Run started: ${confirmedPlan.length} operation${confirmedPlan.length === 1 ? '' : 's'} · ${total.toLocaleString()} Credits exact total · ${budget.toLocaleString()} Credits hard budget`);
        const resultItems = [];
        try {
            for (let index = 0; index < confirmedPlan.length; index += 1) {
                if (__mcmsModuleContext.runtime.destroyed || __mcmsModuleContext.expansionPlannerRuntime.stopRequested) break;
                const snapshot = confirmedPlan[index];
                const item = __mcmsModuleContext.expansionPlannerRuntime.queue.find(candidate => candidate.operationId === snapshot.operationId) || snapshot;
                __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = item.buildingId;
                __mcmsModuleContext.expansionPlannerRuntime.currentItem = `${index + 1}/${confirmedPlan.length} · ${item.name} · ${item.label}`;
                (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
                let countProcessed = true;
                try {
                    const result = await (0,__mcmsModuleContext.applyExpansionPlannerOperation)(snapshot, budget - __mcmsModuleContext.expansionPlannerRuntime.creditsSpent);
                    item.outcome = 'purchased';
                    item.outcomeDetail = result.detail;
                    __mcmsModuleContext.expansionPlannerRuntime.purchased += 1;
                    __mcmsModuleContext.expansionPlannerRuntime.creditsSpent += snapshot.priceCredits;
                    resultItems.push({ name: item.name, label: item.label, priceCredits: snapshot.priceCredits, outcome: 'purchased', detail: result.detail });
                    (0,__mcmsModuleContext.expansionPlannerLog)(`Purchased ${item.name}: ${result.detail}`);
                } catch (err) {
                    item.outcomeDetail = (0,__mcmsModuleContext.String)(err?.message || 'unknown error');
                    __mcmsModuleContext.expansionPlannerRuntime.stopRequested = true;
                    if (err?.expansionPlannerStoppedBeforeMutation) {
                        countProcessed = false;
                        item.outcome = 'ready';
                        (0,__mcmsModuleContext.expansionPlannerLog)(`Stopped before ${item.name}: ${item.outcomeDetail}`, 'warn');
                    } else {
                        item.outcome = 'error';
                        __mcmsModuleContext.expansionPlannerRuntime.errors += 1;
                        resultItems.push({ name: item.name, label: item.label, priceCredits: snapshot.priceCredits, outcome: 'error', detail: item.outcomeDetail });
                        (0,__mcmsModuleContext.expansionPlannerLog)(`SAFETY STOP at ${item.name}: ${item.outcomeDetail}`, 'error');
                    }
                } finally {
                    if (countProcessed) __mcmsModuleContext.expansionPlannerRuntime.processed += 1;
                    (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
                }
                if (__mcmsModuleContext.expansionPlannerRuntime.stopRequested) break;
                if (index < confirmedPlan.length - 1 && !await (0,__mcmsModuleContext.runtimeDelay)(__mcmsModuleContext.state.expansionPlanner.delayMs)) break;
            }
        } finally {
            const manuallyStopped = __mcmsModuleContext.expansionPlannerRuntime.stopRequested && __mcmsModuleContext.expansionPlannerRuntime.errors === 0;
            for (const item of confirmedPlan.slice(__mcmsModuleContext.expansionPlannerRuntime.processed)) resultItems.push({ name: item.name, label: item.label, priceCredits: item.priceCredits, outcome: 'skipped', detail: manuallyStopped ? 'Run stopped before this purchase' : 'Not attempted after safety stop' });
            __mcmsModuleContext.expansionPlannerRuntime.skipped = __mcmsModuleContext.Math.max(0, confirmedPlan.length - __mcmsModuleContext.expansionPlannerRuntime.processed);
            const outcome = manuallyStopped ? 'manually-stopped' : __mcmsModuleContext.expansionPlannerRuntime.errors ? (__mcmsModuleContext.expansionPlannerRuntime.purchased ? 'partial' : 'failed') : __mcmsModuleContext.expansionPlannerRuntime.purchased === confirmedPlan.length ? 'successful' : 'partial';
            (0,__mcmsModuleContext.persistExpansionPlannerReport)({
                schemaVersion: 1, reportId: `upgrade-${__mcmsModuleContext.Date.now()}-${__mcmsModuleContext.Math.random().toString(36).slice(2, 8).padEnd(6, '0')}`,
                toolkitVersion: __mcmsModuleContext.SCRIPT.version, startedAt: __mcmsModuleContext.expansionPlannerRuntime.startedAt, completedAt: __mcmsModuleContext.Date.now(), outcome,
                planned: confirmedPlan.length, purchased: __mcmsModuleContext.expansionPlannerRuntime.purchased, skipped: __mcmsModuleContext.expansionPlannerRuntime.skipped,
                errors: __mcmsModuleContext.expansionPlannerRuntime.errors, plannedCredits: total, creditsSpent: __mcmsModuleContext.expansionPlannerRuntime.creditsSpent, items: resultItems
            });
            __mcmsModuleContext.expansionPlannerRuntime.running = false;
            __mcmsModuleContext.expansionPlannerRuntime.stopRequested = false;
            __mcmsModuleContext.expansionPlannerRuntime.currentBuildingId = '';
            __mcmsModuleContext.expansionPlannerRuntime.currentItem = '';
            (0,__mcmsModuleContext.expansionPlannerLog)(`${outcome === 'successful' ? 'Complete' : outcome === 'manually-stopped' ? 'Stopped' : 'Ended safely'}: ${__mcmsModuleContext.expansionPlannerRuntime.purchased} purchased · ${__mcmsModuleContext.expansionPlannerRuntime.creditsSpent.toLocaleString()} Credits spent · ${__mcmsModuleContext.expansionPlannerRuntime.skipped} not attempted · ${__mcmsModuleContext.expansionPlannerRuntime.errors} errors`, __mcmsModuleContext.expansionPlannerRuntime.errors ? 'error' : 'info');
            (0,__mcmsModuleContext.showToast)(`Expansion Planner ${outcome === 'successful' ? 'complete' : outcome === 'manually-stopped' ? 'stopped' : 'ended safely'} · ${__mcmsModuleContext.expansionPlannerRuntime.purchased} purchased · ${__mcmsModuleContext.expansionPlannerRuntime.creditsSpent.toLocaleString()} Credits spent`);
            (0,__mcmsModuleContext.renderExpansionPlannerPanel)();
        }
    }),
"postTransportSweepDiscordReport":__mcmsModuleContext=>(async function postTransportSweepDiscordReport(report=__mcmsModuleContext.transportSweepRuntime.lastReport,{manual=false}={}){
  if(!manual)return false;
  const clean=(0,__mcmsModuleContext.normaliseTransportSweepReport)(report);if(!clean||__mcmsModuleContext.transportSweepRuntime.discordPosting)return false;
  __mcmsModuleContext.transportSweepRuntime.discordPosting=true;
  try{await (0,__mcmsModuleContext.pilotCall)({op:'discordPost',account:__mcmsModuleContext.pilot.account(),kind:'sweep',payload:(0,__mcmsModuleContext.buildTransportSweepDiscordPayload)(clean)}).promise;(0,__mcmsModuleContext.showToast)('Posted to Discord.');return true;}
  catch(error){(0,__mcmsModuleContext.showToast)(error.message);return false;}
  finally{__mcmsModuleContext.transportSweepRuntime.discordPosting=false;(0,__mcmsModuleContext.renderTransportSweepPanel)();}
})};})();

})();
