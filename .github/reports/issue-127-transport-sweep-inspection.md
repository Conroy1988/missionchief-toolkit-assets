# Issue #127 Transport Sweep inspection

## `transportSweepRuntime` — line 1315

```javascript
const transportSweepRuntime = {
        running: false,
        stopRequested: false,
        queue: [],
        scannedAt: 0,
        currentMissionId: null,
        currentVehicleHref: '',
        cleared: 0,
        skipped: 0,
        errors: 0,
        processed: 0,
        rejectedOwn: 0,
        missionAnchorBaseline: new Set(),
        vehicleButtonBaseline: new Set(),
        ownVehicleIds: new Set(),
        missionWindowRoot: null,
        activeWindowRoot: null,
        ownedWindowLayers: new Set(),
        activeWindowCreatedLayer: false,
        lastCandidateStats: null,
        log: []
    };
```

## `renderTransportSweepPanel()` — line 16513

```javascript
function renderTransportSweepPanel() {
        const host = document.querySelector(`#${SCRIPT.panelId} [data-transport-sweep]`);
        if (!host) return;
        const runtime = transportSweepRuntime;
        const queue = runtime.queue || [];
        const currentId = normaliseMissionId(runtime.currentMissionId);
        const status = runtime.running ? 'RUNNING' : runtime.stopRequested ? 'STOPPING' : queue.length ? 'READY' : 'IDLE';
        const list = queue.length ? queue.map((item, index) => {
            const current = currentId !== null && normaliseMissionId(item.missionId) === currentId;
            return `<div class="mcms-sweep-entry ${current ? 'mcms-current' : ''}"><div><span class="mcms-sweep-title">${escapeHtml(`${index + 1}. ${item.caption}`)}</span><span class="mcms-sweep-meta">Mission ${escapeHtml(item.missionId)} · ${escapeHtml(item.requirement)}</span></div><span class="mcms-sweep-count">${escapeHtml(item.count)} req</span></div>`;
        }).join('') : `<div class="mcms-empty-state">Scan to find alliance missions currently reporting patient transport requirements.</div>`;
        const logs = runtime.log.length ? runtime.log.map(entry => {
            const stamp = new Date(entry.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            return `<div>${escapeHtml(stamp)} · ${escapeHtml(entry.message)}</div>`;
        }).join('') : '<div>No sweep activity yet.</div>';
        const html = `<div class="mcms-sweep-card"><div class="mcms-sweep-head"><span>Patient Transport Sweep</span><span class="mcms-sweep-state ${runtime.running ? 'mcms-running' : ''}">${status}</span></div><div class="mcms-sweep-stats"><div class="mcms-sweep-stat"><b>${queue.length}</b><span>Missions</span></div><div class="mcms-sweep-stat"><b>${runtime.cleared}</b><span>Cleared</span></div><div class="mcms-sweep-stat"><b>${runtime.skipped}</b><span>Skipped</span></div><div class="mcms-sweep-stat"><b>${runtime.errors}</b><span>Errors</span></div></div><div class="mcms-sweep-queue">${list}</div><div class="mcms-sweep-log">${logs}</div></div>`;
        setInnerHtmlIfChanged(host, html);
        const start = document.querySelector(`#${SCRIPT.panelId} [data-action="start-transport-sweep"]`);
        const stop = document.querySelector(`#${SCRIPT.panelId} [data-action="stop-transport-sweep"]`);
        const scan = document.querySelector(`#${SCRIPT.panelId} [data-action="scan-transport-sweep"]`);
        if (start) start.disabled = runtime.running;
        if (stop) stop.disabled = !runtime.running;
        if (scan) scan.disabled = runtime.running;
    }
```

## `transportSweepReleaseConfirmationVisible()` — line 16930

```javascript
function transportSweepReleaseConfirmationVisible() {
        const text = transportSweepVisibleWindowRoots()
            .map(root => String(root.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase())
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

    function transportSweepVisibleDischargeButtons() {
        const buttons = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            let matches = [];
            try { matches = Array.from(context.doc.querySelectorAll('button')); } catch (err) {}
            for (const button of matches) {
                if (seen.has(button) || !transportSweepElementVisible(button) || button.disabled) continue;
                if (String(button.textContent || '').trim().toLowerCase() !== 'discharge patient') continue;
                seen.add(button);
                buttons.push(button);
            }
        }
        return buttons;
    }

    function findVisibleDischargePatientButton(excludedButtons = null) {
        const excluded = excludedButtons instanceof Set ? excludedButtons : null;
        return transportSweepVisibleDischargeButtons().find(button => !excluded || !excluded.has(button)) || null;
    }

    function transportSweepTopLevelWindowRoots() {
        const visible = transportSweepVisibleWindowRoots();
        return visible.filter(root => !visible.some(other => other !== root && other.contains?.(root)));
    }

    const TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR = [
        '#lightbox', '#lightbox_box', '.lightbox', '[id*="lightbox"]',
        '.lightbox_overlay', '.lightbox-overlay', '#lightbox_overlay', '#lightbox_backdrop', '.lightbox-backdrop',
        '.modal.show', '.modal.in', '.modal-backdrop.show', '.modal-backdrop.in',
        '[role="dialog"]', '.ui-dialog', '.ui-widget-overlay'
    ].join(', ');

    function transportSweepNativeWindowLayers() {
        const layers = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            let matches = [];
            try { matches = Array.from(context.doc.querySelectorAll(TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR)); } catch (err) {}
            for (const layer of matches) {
                if (!layer || seen.has(layer) || !layer.isConnected || layer.closest?.(`#${SCRIPT.panelId}`)) continue;
                seen.add(layer);
                layers.push(layer);
            }
        }
        return layers;
    }

    function transportSweepWindowLayerChain(root) {
        const chain = [];
        const seen = new Set();
        const collect = start => {
            let node = start;
            while (node?.nodeType === 1) {
                if (!seen.has(node) && node.matches?.(TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR)) {
                    seen.add(node);
                    chain.push(node);
                }
                node = node.parentElement;
            }
        };
        collect(root);
        try { collect(root?.ownerDocument?.defaultView?.frameElement); } catch (err) {}
        return chain;
    }

    function transportSweepOverlayLayer(layer) {
        if (!layer?.matches) return false;
        return layer.matches('.modal-backdrop, .ui-widget-overlay, .lightbox_overlay, .lightbox-overlay, #lightbox_overlay, #lightbox_backdrop, .lightbox-backdrop');
    }

    function transportSweepOutermostLayer(layers) {
        const candidates = Array.from(layers || []).filter(layer => layer?.isConnected && !transportSweepOverlayLayer(layer));
        return candidates.find(layer => !candidates.some(other => other !== layer && other.contains?.(layer))) || candidates[0] || null;
    }

    function transportSweepClaimWindow(root, beforeLayers = null) {
        if (!root?.isConnected) return null;
        const baseline = beforeLayers instanceof Set ? beforeLayers : new Set();
        const anchor = (() => {
            try { return root.ownerDocument?.defaultView?.frameElement || root; } catch (err) { return root; }
        })();
        const chain = transportSweepWindowLayerChain(root);
        const created = transportSweepNativeWindowLayers().filter(layer => {
            if (baseline.has(layer)) return false;
            if (layer === anchor || layer.contains?.(anchor) || anchor.contains?.(layer)) return true;
            return layer.ownerDocument === anchor.ownerDocument && transportSweepOverlayLayer(layer);
        });
        const owned = new Set([...created, ...chain.filter(layer => !baseline.has(layer))]);
        for (const layer of owned) {
            try { layer.dataset.mcmsTransportSweepOwned = '1'; } catch (err) {}
        }
        transportSweepRuntime.ownedWindowLayers = owned;
        transportSweepRuntime.activeWindowCreatedLayer = owned.size > 0;
        transportSweepRuntime.activeWindowRoot = transportSweepOutermostLayer(owned) || transportSweepOutermostLayer(chain) || root;
        return transportSweepRuntime.activeWindowRoot;
    }

    function transportSweepWindowCloseControl(root) {
        if (!root?.querySelectorAll) return null;
        const selectors = [
            '#lightbox_close', '.lightbox-close', '.lightbox_close',
            '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]',
            'button.close', 'a.close', 'button[aria-label="Close"]', 'a[aria-label="Close"]',
            'button[title="Close"]', 'a[title="Close"]'
        ];
        for (const selector of selectors) {
            const control = Array.from(root.querySelectorAll(selector)).find(transportSweepElementVisible);
            if (control) return control;
        }
        return null;
    }

    async function closeTransportSweepWindows(reason = 'navigation') {
        const target = transportSweepRuntime.activeWindowRoot;
        const ownedLayers = Array.from(transportSweepRuntime.ownedWindowLayers || []).filter(layer => layer?.isConnected);
        transportSweepRuntime.missionWindowRoot = null;
        if ((!target || !target.isConnected || !transportSweepElementVisible(target)) && !ownedLayers.length) {
            transportSweepRuntime.activeWindowRoot = null;
            transportSweepRuntime.ownedWindowLayers = new Set();
            transportSweepRuntime.activeWindowCreatedLayer = false;
            return true;
        }

        const waitUntilClosed = timeoutMs => transportSweepWaitFor(
            () => !target?.isConnected || !transportSweepElementVisible(target) ? true : null,
            timeoutMs,
            100
        );

        let closed = !target?.isConnected || !transportSweepElementVisible(target);
        if (!closed) {
            const closeControl = transportSweepWindowCloseControl(target);
            if (closeControl) {
                try {
                    closeControl.click();
                    closed = Boolean(await waitUntilClosed(1200));
                } catch (err) {}
            }
        }

        if (!closed && typeof pageWindow.lightboxClose === 'function') {
            try {
                pageWindow.lightboxClose();
                closed = Boolean(await waitUntilClosed(1400));
            } catch (err) {}
        }

        if (transportSweepRuntime.activeWindowCreatedLayer) {
            const removable = Array.from(new Set(ownedLayers.filter(layer => layer?.isConnected)));
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
            closed = !target?.isConnected || !transportSweepElementVisible(target);
        }

        const ownedStillConnected = ownedLayers.some(layer => layer?.isConnected && transportSweepElementVisible(layer));
        if (!closed || ownedStillConnected) {
            transportSweepLog(`MissionChief did not remove the sweep-owned window before ${reason}`, 'error');
            return false;
        }

        transportSweepRuntime.activeWindowRoot = null;
        transportSweepRuntime.ownedWindowLayers = new Set();
        transportSweepRuntime.activeWindowCreatedLayer = false;
        await transportSweepSleep(80);
        return true;
    }

    async function openTransportSweepPath(path, mode) {
        if (transportSweepRuntime.stopRequested) return false;
        if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');
        const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle');
        if (!closed || transportSweepRuntime.stopRequested) return false;

        const beforeRoots = transportSweepVisibleWindowRoots();
        const beforeRootText = new Map(beforeRoots.map(root => [root, String(root.textContent || '').trim()]));
        const beforeLayers = new Set(transportSweepNativeWindowLayers());

        if (mode === 'mission') {
            transportSweepRuntime.missionAnchorBaseline = new Set(transportSweepVisibleVehicleAnchors());
            transportSweepRuntime.rejectedOwn = 0;
            transportSweepRuntime.missionWindowRoot = null;
            const missionId = normaliseMissionId(String(path || '').match(/\/missions\/(\d+)/)?.[1]);
            pageWindow.lightboxOpen(path);
            await transportSweepWaitFor(() => {
                const root = transportSweepFindMissionWindowRoot(missionId);
                if (root) {
                    const anchors = transportSweepVehicleAnchorsWithin(root);
                    const afterText = String(root.textContent || '').trim();
                    const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root);
                    if (anchors.length || (afterText && changed)) {
                        transportSweepRuntime.missionWindowRoot = root;
                        transportSweepClaimWindow(root, beforeLayers);
                        return { root, anchors };
                    }
                }
                const newAnchor = transportSweepVisibleVehicleAnchors().find(anchor => !transportSweepRuntime.missionAnchorBaseline.has(anchor));
                if (newAnchor) {
                    transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.parentElement;
                    transportSweepClaimWindow(transportSweepRuntime.missionWindowRoot, beforeLayers);
                    return { root: transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
                }
                return null;
            }, 4200, 120);
            return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
        }

        pageWindow.lightboxOpen(path);
        const vehicleWindow = await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) {
                const root = button.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || button.parentElement;
                return { root };
            }
            const root = transportSweepVisibleWindowRoots().find(candidate => {
                const text = String(candidate.textContent || '').trim();
                return !beforeRootText.has(candidate) || text !== beforeRootText.get(candidate);
            });
            return root ? { root } : null;
        }, 4200, 120);
        transportSweepClaimWindow(vehicleWindow?.root, beforeLayers);
        return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
    }

    async function openTransportSweepVehicle(candidate) {
        if (transportSweepRuntime.stopRequested || !candidate?.href) return null;
        transportSweepRuntime.vehicleButtonBaseline = new Set(transportSweepVisibleDischargeButtons());
        const opened = await openTransportSweepPath(candidate.href, 'vehicle');
        if (!opened || transportSweepRuntime.stopRequested) return null;

        const openedAt = Date.now();
        return await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) return { opened: true, button };
            const roots = transportSweepTopLevelWindowRoots();
            if (roots.length && Date.now() - openedAt > 350) return { opened: true, button: null };
            return null;
        }, 7500, 140);
    }

    async function processTransportSweepMission(item, remainingAllowance) {
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

        await closeTransportSweepWindows('finishing the mission');

        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
        return clearedHere;
    }

    async function startTransportSweep() {
        if (transportSweepRuntime.running) return;
        const queue = buildTransportSweepQueue();
        if (!queue.length) {
            showToast('No alliance patient transports found');
            return;
        }
        showToast('Verifying your personal vehicle list…');
        const ownershipReady = await refreshPersonalVehicleData(true);
        if (!ownershipReady || !vehicleApiReady || personalVehicleApiCache.size === 0) {
            showToast('Transport Sweep cancelled — your vehicle ownership list could not be verified');
            return;
        }
        transportSweepRuntime.ownVehicleIds = new Set(Array.from(personalVehicleApiCache.keys(), id => String(id)));
        const totalRequests = queue.reduce((sum, item) => sum + Math.max(1, Number(item.count) || 1), 0);
        const planned = Math.min(totalRequests, state.transportSweep.maxPerRun);
        const confirmed = pageWindow.confirm(`Transport Sweep will attempt up to ${planned} alliance-member patient releases across ${queue.length} alliance mission${queue.length === 1 ? '' : 's'}.

The sweep waits dynamically for LSSM's “Release patient (No reward)” controls and processes one alliance ambulance at a time. Your own verified vehicle IDs are always excluded. If LSSM controls do not appear, the existing vehicle-window route remains available as a fallback. Continue?`);
        if (!confirmed) return;
        transportSweepRuntime.running = true;
        transportSweepRuntime.stopRequested = false;
        transportSweepRuntime.currentMissionId = null;
        transportSweepRuntime.currentVehicleHref = '';
        transportSweepRuntime.cleared = 0;
        transportSweepRuntime.skipped = 0;
        transportSweepRuntime.errors = 0;
        transportSweepRuntime.processed = 0;
        transportSweepRuntime.rejectedOwn = 0;
        transportSweepRuntime.missionAnchorBaseline = new Set();
        transportSweepRuntime.vehicleButtonBaseline = new Set();
        transportSweepRuntime.missionWindowRoot = null;
        transportSweepRuntime.activeWindowRoot = null;
        transportSweepRuntime.ownedWindowLayers = new Set();
        transportSweepRuntime.activeWindowCreatedLayer = false;
        transportSweepRuntime.lastCandidateStats = null;
        transportSweepRuntime.log = [];
        renderTransportSweepPanel();
        transportSweepLog(`Sweep started: ${queue.length} missions, maximum ${state.transportSweep.maxPerRun} requests`);
        try {
            for (const item of queue) {
                if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;
                const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;
                await processTransportSweepMission(item, remaining);
                if (!transportSweepRuntime.stopRequested) await transportSweepSleep(state.transportSweep.delayMs);
            }
        } catch (err) {
            transportSweepRuntime.errors += 1;
            transportSweepLog(`Sweep stopped by error: ${err?.message || 'unknown error'}`, 'error');
        } finally {
            await closeTransportSweepWindows('finishing the sweep');
            const wasStopped = transportSweepRuntime.stopRequested;
            transportSweepRuntime.running = false;
            transportSweepRuntime.stopRequested = false;
            transportSweepRuntime.currentMissionId = null;
            transportSweepRuntime.currentVehicleHref = '';
            transportSweepRuntime.missionAnchorBaseline = new Set();
            transportSweepRuntime.vehicleButtonBaseline = new Set();
            transportSweepRuntime.activeWindowRoot = null;
            transportSweepRuntime.ownedWindowLayers = new Set();
            transportSweepRuntime.activeWindowCreatedLayer = false;
            buildTransportSweepQueue();
            renderTransportSweepPanel();
            scheduleTransportWatcherRefresh(0);
            showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared`);
            transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`);
        }
    }

    function stopTransportSweep() {
        if (!transportSweepRuntime.running) return;
        transportSweepRuntime.stopRequested = true;
        transportSweepLog('Stop requested — finishing the current action');
        renderTransportSweepPanel();
    }

    function vehicleTargetInfo(vehicle) {
        if (!vehicle || typeof vehicle !== 'object') return { type: null, id: null };
        const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
            .filter(item => item && typeof item === 'object');
        for (const item of containers) {
            const type = String(item.target_type ?? item.targetType ?? '').toLowerCase();
            const id = normaliseMissionId(item.target_id ?? item.targetId);
            if ((type === 'mission' || type === 'building') && id !== null && id !== '0') return { type, id };
            const missionId = normaliseMissionId(item.mission_id ?? item.missionId);
            if (missionId !== null && missionId !== '0') return { type: 'mission', id: missionId };
            const buildingId = normaliseMissionId(item.target_building_id ?? item.targetBuildingId);
            if (buildingId !== null && buildingId !== '0') return { type: 'building', id: buildingId };
        }
        return { type: null, id: null };
    }

    function vehicleSearchSignal(vehicle) {
        if (!vehicle || typeof vehicle !== 'object') return '';
        const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
            .filter(item => item && typeof item === 'object');
        const values = [];
        for (const item of containers) {
            values.push(item.caption, item.name, item.vehicle_type_caption, item.vehicleTypeCaption, item.vehicle_type_name, item.vehicleTypeName, item.type_caption, item.typeCaption, item.title);
        }
        try { values.push(vehicle?._icon?.title, vehicle?._icon?.alt, vehicle?._icon?.getAttribute?.('aria-label')); } catch (err) {}
        return values.filter(Boolean).join(' ');
    }

    function vehicleStatusBucket(vehicle) {
        const status = vehicleStatusCode(vehicle);
        if ([1, 2].includes(status)) return 'available';
        if (status === 3) return 'travelling';
        if (status === 4) return 'scene';
        if ([7, 8].includes(status)) return 'transport';
        return 'other';
    }

    function clearResourceGapLabels() {
        if (resourceGapGroup) {
            try { resourceGapGroup.clearLayers(); resourceGapGroup.remove(); } catch (err) {}
        }
        resourceGapLabels.clear();
        resourceGapGroup = null;
    }

    function splitRequirementItems(value) {
        return String(value || '').split(/\s*(?:•|;|\n|,(?=\s*\d+\s*(?:x|×)?\b))\s*/).map(item => item.trim()).filter(Boolean);
    }

    function parseCountedRequirement(value) {
        const clean = String(value || '').replace(/^[-–—\s]+/, '').trim();
        const match = clean.match(/^(\d+)\s*(?:x|×)?\s+(.+)$/i);
        if (match) return { count: Math.max(1, Number(match[1]) || 1), name: match[2].replace(/[.!]+$/, '').trim() };
        if (clean) return { count: 1, name: clean.replace(/[.!]+$/, '').trim() };
        return null;
    }

    function resourceRequirementsFromSnapshot(snapshot) {
        const raw = normaliseMissingRequirementText(snapshot?.missingText);
        const result = { raw, vehicles: [], personnel: [], other: [] };
        if (!raw) return result;
        const labelled = /\b(?:vehicles?|personnel|other)\s*:/i.test(raw);
        if (labelled) {
            const sectionPattern = /\b(vehicles?|personnel|other)\s*:\s*([\s\S]*?)(?=\s*•?\s*\b(?:vehicles?|personnel|other)\s*:|$)/gi;
            let section;
            while ((section = sectionPattern.exec(raw))) {
                const key = /^vehicle/i.test(section[1]) ? 'vehicles' : /^personnel/i.test(section[1]) ? 'personnel' : 'other';
                for (const item of splitRequirementItems(section[2])) {
                    const parsed = parseCountedRequirement(item);
                    if (parsed && parsed.name) result[key].push(parsed);
                }
            }
        } else {
            const transportOnly = transportRequirementFromSnapshot(snapshot);
            if (!transportOnly && /\b(?:vehicle|engine|unit|carrier|ladder|ambulance|police|car|van|boat|helicopter|support|officer)\b/i.test(raw)) {
                for (const item of splitRequirementItems(raw)) {
                    const parsed = parseCountedRequirement(item.replace(/^missing\s*:?\s*/i, ''));
                    if (parsed && parsed.name) result.vehicles.push(parsed);
                }
            }
        }
        result.vehicles = result.vehicles.filter(item => item.name && !/transport is needed|required transport/i.test(item.name));
        return result;
    }

    function normaliseSearchText(value) {
        return String(value || '').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, ' ').trim();
    }

    function resourceSearchToken(value) {
        let token = normaliseSearchText(value);
        if (token.length > 4 && token.endsWith('ies')) token = `${token.slice(0, -3)}y`;
        else if (token.length > 3 && token.endsWith('s') && !token.endsWith('ss')) token = token.slice(0, -1);
        return token;
    }

    function requirementSearchParts(name) {
        const original = String(name || '');
        const acronyms = Array.from(original.matchAll(/\(([A-Z0-9-]{2,12})\)/g)).map(match => normaliseSearchText(match[1]));
        const cleaned = normaliseSearchText(original.replace(/\([^)]*\)/g, ' '));
        const stop = new Set(['vehicle', 'vehicles', 'unit', 'units', 'the', 'and', 'with', 'required', 'needed', 'personnel']);
        const tokens = cleaned.split(' ').filter(token => token.length > 1 && !stop.has(token)).map(resourceSearchToken).filter(Boolean);
        return { cleaned, acronyms, tokens };
    }

    function buildResourceGapVehicleContext() {
        const key = `${vehicleDataRevision}:${markerRegistryRevision}:${vehicleApiReady}:${personalVehicleApiCache.size}`;
        const now = Date.now();
        if (resourceGapVehicleContextCache.key === key && now - resourceGapVehicleContextCache.createdAt < RESOURCE_GAP_REFRESH_MS) return resourceGapVehicleContextCache;

        const markerById = new Map(getVehicleMarkerLayers().map(marker => [vehicleRecordId(marker), marker]).filter(([id]) => id !== null));
        const available = [];
        const byToken = new Map();
        for (const vehicle of getPersonalVehicleRecords()) {
            if (vehicleStatusBucket(vehicle) !== 'available' || vehicleTargetInfo(vehicle).type !== null) continue;
            const signal = normaliseSearchText(vehicleSearchSignal(vehicle));
            if (!signal) continue;
            const tokens = new Set(signal.split(' ').map(resourceSearchToken).filter(Boolean));
            const prepared = { vehicle, signal, tokens, point: vehicleCoordinates(vehicle, markerById) };
            available.push(prepared);
            for (const token of tokens) {
                const bucket = byToken.get(token) || [];
                bucket.push(prepared);
                byToken.set(token, bucket);
            }
        }
        resourceGapVehicleContextCache = { key, createdAt: now, available, byToken };
        return resourceGapVehicleContextCache;
    }

    function preparedVehicleMatchesRequirement(prepared, parts) {
        if (!prepared?.signal) return false;
        if (parts.acronyms.some(acronym => acronym && prepared.tokens.has(resourceSearchToken(acronym)))) return true;
        if (parts.cleaned && prepared.signal.includes(parts.cleaned)) return true;
        if (!parts.tokens.length) return false;
        const matched = parts.tokens.filter(token => prepared.tokens.has(token)).length;
        return matched >= Math.max(1, Math.ceil(parts.tokens.length * 0.6));
    }

    function vehicleCoordinates(vehicle, markerById = null) {
        const point = heatmapPointFromObject(vehicle);
        if (point) return point;
        const id = vehicleRecordId(vehicle);
        const marker = id !== null ? markerById?.get(id) : null;
        return heatmapPointFromObject(marker);
    }

    function haversineMiles(a, b) {
        if (!a || !b) return null;
        const toRad = value => Number(value) * Math.PI / 180;
        const lat1 = toRad(a.lat), lat2 = toRad(b.lat);
        const dLat = lat2 - lat1, dLng = toRad(b.lng) - toRad(a.lng);
        const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
        return 3958.7613 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(Math.max(0, 1 - h)));
    }

    function analyseResourceGap(snapshot, context = buildResourceGapVehicleContext(), requirements = resourceRequirementsFromSnapshot(snapshot)) {
        const radiusMi = Number(state.resourceGap.radiusMi) || 25;
        const cacheKey = `${snapshot?.missionId}:${requirements.raw}:${radiusMi}:${context.key}`;
        const cached = resourceGapAnalysisCache.get(cacheKey);
        const now = Date.now();
        if (cached && now - cached.createdAt < RESOURCE_GAP_REFRESH_MS) return cached;

        const missionPoint = Number.isFinite(Number(snapshot?.lat)) && Number.isFinite(Number(snapshot?.lng))
            ? { lat: Number(snapshot.lat), lng: Number(snapshot.lng) }
            : null;
        const rows = requirements.vehicles.map(requirement => {
            const parts = requirementSearchParts(requirement.name);
            const candidateSet = new Set();
            for (const token of [...parts.tokens, ...parts.acronyms.map(resourceSearchToken)]) {
                for (const prepared of context.byToken?.get(token) || []) candidateSet.add(prepared);
            }
            const candidates = candidateSet.size ? candidateSet : context.available;
            let nearby = 0;
            let nearest = null;
            for (const prepared of candidates) {
                if (!preparedVehicleMatchesRequirement(prepared, parts)) continue;
                const distance = haversineMiles(missionPoint, prepared.point);
                if (distance === null || distance > radiusMi) continue;
                nearby += 1;
                if (nearest === null || distance < nearest) nearest = distance;
            }
            return { ...requirement, nearby, nearest };
        });
        const analysis = {
            createdAt: now,
            requirements,
            rows,
            radiusMi,
            missingTypes: rows.length,
            uncoveredTypes: rows.filter(row => row.nearby < row.count).length
        };
        if (resourceGapAnalysisCache.size > 180) {
            for (const [key, value] of resourceGapAnalysisCache) {
                if (now - Number(value?.createdAt || 0) > RESOURCE_GAP_REFRESH_MS * 2) resourceGapAnalysisCache.delete(key);
            }
            if (resourceGapAnalysisCache.size > 180) resourceGapAnalysisCache.clear();
        }
        resourceGapAnalysisCache.set(cacheKey, analysis);
        return analysis;
    }

    function makeResourceGapIcon(analysis) {
        const count = Math.max(1, Number(analysis?.missingTypes) || 1);
        const uncovered = Number(analysis?.uncoveredTypes) > 0;
        return pageWindow.L.divIcon({
            className: 'mcms-resource-gap-icon',
            html: `<span class="mcms-resource-gap-badge ${uncovered ? 'mcms-gap-uncovered' : ''}" title="${uncovered ? 'Resource shortfall detected' : 'Missing resource types'}">⚠ ${escapeHtml(count)}</span>`,
            iconSize: [0, 0], iconAnchor: [0, -22]
        });
    }

    function updateResourceGapLabels() {
        if (state.economyMode && economyMapMoving) return;
        runtimeClearTimeout(resourceGapTimer);
        resourceGapTimer = null;
        if (!state.resourceGap.enabled) { clearResourceGapLabels(); return; }
        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L?.layerGroup || !pageWindow.L?.marker || !pageWindow.L?.divIcon) { clearResourceGapLabels(); return; }
        const pane = ensureMissionFloatPane(map);
        if (!pane) { clearResourceGapLabels(); return; }
        if (!resourceGapGroup || resourceGapGroup._map !== map) {
            clearResourceGapLabels();
            resourceGapGroup = pageWindow.L.layerGroup();
            resourceGapGroup.__mcmsResourceGapLayer = true;
            resourceGapGroup.addTo(map);
        }
        const now = Date.now();
        const context = buildResourceGapVehicleContext();
        const economyBounds = state.economyMode ? economyPaddedBounds(map, 0.08) : null;
        const active = new Set();
        for (const marker of getMissionMarkerIndex().markers) {
            const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
            const snapshot = missionId === null ? null : (liveMissionSnapshots.get(missionId) || missionSnapshotFromMarker(marker, now));
            if (!snapshot) continue;
            if (snapshot.source === 'personal' && !state.visibility.myMissions) continue;
            if (snapshot.source === 'alliance' && !state.visibility.allianceMissions) continue;
            const requirements = resourceRequirementsFromSnapshot(snapshot);
            if (!requirements.vehicles.length) continue;
            let latLng = null;
            try { latLng = marker.getLatLng?.(); } catch (err) {}
            if (!latLng) continue;
            if (economyBounds && !economyBounds.contains?.(latLng)) continue;
            const analysis = analyseResourceGap(snapshot, context, requirements);
            active.add(snapshot.missionId);
            const signature = `${analysis.missingTypes}:${analysis.uncoveredTypes}:${analysis.rows.map(row => `${row.count}:${row.nearby}:${row.nearest === null ? 'x' : row.nearest.toFixed(1)}`).join('|')}:${state.resourceGap.radiusMi}`;
            let label = resourceGapLabels.get(snapshot.missionId);
            if (!label) {
                label = pageWindow.L.marker(latLng, { interactive: false, keyboard: false, bubblingMouseEvents: false, pane, zIndexOffset: 0, icon: makeResourceGapIcon(analysis) });
                label.__mcmsResourceGapSignature = signature;
                label.__mcmsResourceGapLabel = true;
                label.addTo(resourceGapGroup);
                resourceGapLabels.set(snapshot.missionId, label);
            } else {
                try { label.setLatLng(latLng); } catch (err) {}
                if (label.__mcmsResourceGapSignature !== signature) {
                    label.__mcmsResourceGapSignature = signature;
                    try { label.setIcon(makeResourceGapIcon(analysis)); } catch (err) {}
                }
            }
        }
        for (const [missionId, label] of resourceGapLabels.entries()) {
            if (active.has(missionId)) continue;
            resourceGapLabels.delete(missionId);
            try { resourceGapGroup.removeLayer(label); } catch (err) {}
        }
    }

    function scheduleResourceGapRefresh(delay = 420) {
        runtimeClearTimeout(resourceGapTimer);
        resourceGapTimer = runtimeSetTimeout(updateResourceGapLabels, state.economyMode ? Math.max(1500, delay) : delay);
    }

    function economyPaddedBounds(map = findLeafletMapInstance(false), padding = 0.35) {
        if (!map?.getBounds) return null;
        try {
            const bounds = map.getBounds();
            return typeof bounds?.pad === 'function' ? bounds.pad(padding) : bounds;
        } catch (err) { return null; }
    }

    function economyLayerIsProtected(layer) {
        if (!layer) return true;
        try {
            if (layer.isPopupOpen?.() || layer.getPopup?.()?.isOpen?.()) return true;
        } catch (err) {}
        const icon = layer._icon;
        return Boolean(icon?.matches?.(':hover, :focus, :focus-within') || icon?.classList?.contains('leaflet-marker-draggable') || icon?.classList?.contains('mcms-mission-lock-target'));
    }

    function economyLayerInsideBounds(layer, bounds) {
        if (!bounds || !layer?.getLatLng) return true;
        try { return Boolean(bounds.contains(layer.getLatLng())); } catch (err) { return true; }
    }

    function setEconomyLayerPresence(map, layer, shouldShow, hiddenSet) {
        if (!map || !layer || !hiddenSet) return;
        const onMap = typeof map.hasLayer === 'function' ? map.hasLayer(layer) : Boolean(layer._map);
        if (shouldShow) {
            if (hiddenSet.delete(layer) && !onMap && typeof map.addLayer === 'function') map.addLayer(layer);
            return;
        }
        hiddenSet.add(layer);
        if (onMap && typeof map.removeLayer === 'function') map.removeLayer(layer);
    }

    function synchroniseEconomyLayers(map = findLeafletMapInstance(false)) {
        runtimeClearTimeout(economyLayerSyncTimer);
        economyLayerSyncTimer = null;
        if (!state.economyMode || !map || economyLayerEnforcement) return;
        const bounds = economyPaddedBounds(map, 0.12);
        if (!bounds) return;
        const vehicleLayers = getVehicleMarkerLayers().filter(Boolean);
        const buildingLayers = getBuildingMarkerLayers().filter(Boolean);
        const vehicleSet = new Set(vehicleLayers);
        const buildingSet = new Set(buildingLayers);
        const personalBuildingIds = getPersonalBuildingIds();

        economyLayerEnforcement = true;
        try {
            for (const layer of Array.from(economyHiddenVehicleLayers)) {
                if (!vehicleSet.has(layer)) economyHiddenVehicleLayers.delete(layer);
            }
            for (const layer of vehicleLayers) {
                const visible = state.visibility.vehicles && (economyLayerIsProtected(layer) || economyLayerInsideBounds(layer, bounds));
                setEconomyLayerPresence(map, layer, visible, economyHiddenVehicleLayers);
            }

            for (const layer of Array.from(economyHiddenBuildingLayers)) {
                if (!buildingSet.has(layer)) economyHiddenBuildingLayers.delete(layer);
            }
            for (const layer of buildingLayers) {
                const personal = isPersonalBuildingLayer(layer, personalBuildingIds);
                const allowedByUser = !personal || state.visibility.buildings;
                const visible = allowedByUser && (economyLayerIsProtected(layer) || economyLayerInsideBounds(layer, bounds));
                setEconomyLayerPresence(map, layer, visible, economyHiddenBuildingLayers);
            }
        } catch (err) {
            console.debug(`[${SCRIPT.name}] Economy marker culling skipped.`, err);
        } finally {
            economyLayerEnforcement = false;
        }
    }

    function scheduleEconomyLayerSync(delay = 120) {
        runtimeClearTimeout(economyLayerSyncTimer);
        economyLayerSyncTimer = runtimeSetTimeout(() => synchroniseEconomyLayers(), Math.max(0, Number(delay) || 0));
    }

    function restoreEconomyLayers(map = findLeafletMapInstance(false)) {
        runtimeClearTimeout(economyLayerSyncTimer);
        economyLayerSyncTimer = null;
        if (!map) {
            if (runtime.destroyed) { economyHiddenVehicleLayers.clear(); economyHiddenBuildingLayers.clear(); }
            else runtimeSetTimeout(() => restoreEconomyLayers(findLeafletMapInstance(false)), 220);
            return;
        }
        if (economyLayerEnforcement) return;
        const vehicleSet = new Set(getVehicleMarkerLayers().filter(Boolean));
        const buildingSet = new Set(getBuildingMarkerLayers().filter(Boolean));
        const personalBuildingIds = getPersonalBuildingIds();
        economyLayerEnforcement = true;
        try {
            for (const layer of Array.from(economyHiddenVehicleLayers)) {
                economyHiddenVehicleLayers.delete(layer);
                if (!vehicleSet.has(layer)) continue;
                const onMap = typeof map.hasLayer === 'function' ? map.hasLayer(layer) : Boolean(layer._map);
                if (!onMap && typeof map.addLayer === 'function') map.addLayer(layer);
            }
            for (const layer of Array.from(economyHiddenBuildingLayers)) {
                economyHiddenBuildingLayers.delete(layer);
                if (!buildingSet.has(layer)) continue;
                if (isPersonalBuildingLayer(layer, personalBuildingIds) && !state.visibility.buildings) continue;
                const onMap = typeof map.hasLayer === 'function' ? map.hasLayer(layer) : Boolean(layer._map);
                if (!onMap && typeof map.addLayer === 'function') map.addLayer(layer);
            }
        } catch (err) {
            console.debug(`[${SCRIPT.name}] Economy marker restoration skipped.`, err);
        } finally {
            economyLayerEnforcement = false;
        }
    }

    function applyEconomyToLeafletLayer(map, layer) {
        const snapshot = economyLeafletOptionSnapshots.get(map);
        if (!snapshot || !layer?.options || (!layer._tiles && typeof layer.getTileUrl !== 'function') || snapshot.layerOptions.has(layer)) return;
        const values = {};
        for (const key of ['updateWhenIdle', 'updateWhenZooming', 'updateInterval', 'keepBuffer']) values[key] = layer.options[key];
        snapshot.layerOptions.set(layer, values);
        layer.options.updateWhenIdle = true;
        layer.options.updateWhenZooming = false;
        layer.options.updateInterval = 850;
        layer.options.keepBuffer = 0;
    }

    function applyLeafletEconomyPolicy(map = findLeafletMapInstance(false)) {
        if (!map || economyLeafletOptionSnapshots.has(map)) return;
        const snapshot = {
            mapOptions: {},
            layerOptions: new Map()
        };
        for (const key of ['zoomAnimation', 'fadeAnimation', 'markerZoomAnimation', 'inertia', 'wheelDebounceTime', 'wheelPxPerZoomLevel']) snapshot.mapOptions[key] = map.options?.[key];
        try {
            map.options.zoomAnimation = false;
            map.options.fadeAnimation = false;
            map.options.markerZoomAnimation = false;
            map.options.inertia = false;
            map.options.wheelDebounceTime = Math.max(80, Number(map.options.wheelDebounceTime) || 0);
            map.options.wheelPxPerZoomLevel = Math.max(90, Number(map.options.wheelPxPerZoomLevel) || 0);
            map.eachLayer?.(layer => {
                if (!layer?.options || (!layer._tiles && typeof layer.getTileUrl !== 'function')) return;
                const values = {};
                for (const key of ['updateWhenIdle', 'updateWhenZooming', 'updateInterval', 'keepBuffer']) values[key] = layer.options[key];
                snapshot.layerOptions.set(layer, values);
                layer.options.updateWhenIdle = true;
                layer.options.updateWhenZooming = false;
                layer.options.updateInterval = 850;
                layer.options.keepBuffer = 0;
            });
        } catch (err) {}
        economyLeafletOptionSnapshots.set(map, snapshot);
    }

    function restoreLeafletEconomyPolicy(map = null) {
        const targets = map ? [[map, economyLeafletOptionSnapshots.get(map)]] : Array.from(economyLeafletOptionSnapshots.entries());
        for (const [target, snapshot] of targets) {
            if (!target || !snapshot) continue;
            try {
                Object.assign(target.options, snapshot.mapOptions);
                for (const [layer, values] of snapshot.layerOptions.entries()) if (layer?.options) Object.assign(layer.options, values);
            } catch (err) {}
            economyLeafletOptionSnapshots.delete(target);
        }
    }

    function setEconomyMode(enabled, announce = false) {
        const next = Boolean(enabled);
        if (state.economyMode === next) {
            const existingMap = findLeafletMapInstance(false);
            if (next) { applyLeafletEconomyPolicy(existingMap); scheduleEconomyLayerSync(0); }
            else {
                runtimeClearTimeout(economyLayerSyncTimer);
                economyLayerSyncTimer = null;
                restoreEconomyLayers(existingMap);
                restoreLeafletEconomyPolicy();
                disposeEconomyCanvasRenderer(existingMap);
                document.documentElement?.setAttribute('data-mcms-map-moving', 'false');
                economyDeferredMapRefresh = false;
                economyDeferredDomMutation = false;
            }
            updateUI();
            return;
        }
        state.economyMode = next;
        saveState();
        applyRootAttributes();
        const map = findLeafletMapInstance(false);
        if (next) {
            applyLeafletEconomyPolicy(map);
            scheduleEconomyLayerSync(0);
        } else {
            runtimeClearTimeout(economyLayerSyncTimer);
            economyLayerSyncTimer = null;
            restoreEconomyLayers(map);
            restoreLeafletEconomyPolicy();
            document.documentElement?.setAttribute('data-mcms-map-moving', 'false');
            try { map?.invalidateSize?.({ animate: false }); } catch (err) {}
        }
        runtimeRescheduleTasks(!next);
        heatmapRenderSignature = '';
        coverageRenderSignature = '';
        majorIncidentFeedRenderSignature = '';
        economyDeferredMapRefresh = false;
        economyDeferredDomMutation = false;
        if (!next) disposeEconomyCanvasRenderer(map);
        if (state.coverage.enabled) { clearCoverageRings(); scheduleCoverageRefresh(); }
        if (state.heatmap.enabled) { clearCoverageHeatmap(); scheduleHeatmapRefresh(); }
        scheduleMajorIncidentFeedRender(0);
        scheduleEnabledMapRefreshes({ includeSnapshots: true, positionPanel: true });
        updateUI();
        if (announce) showToast(next ? 'Maximum Economy Mode on · decorative effects stopped and map work minimised' : 'Economy Mode off · full rendering restored');
    }

    function getVehicleMarkerLayers() {
        return getCachedRegistry('vehicle_markers');
    }

    function getBuildingMarkerLayers() {
        return getCachedRegistry('building_markers');
    }

    function getBuildingMarkerCache() {
        return getCachedRegistry('building_markers_cache', PERSONAL_BUILDING_ID_CACHE_MS);
    }

    function getPersonalBuildingIds() {
        const currentUserId = currentUserIdCached();
        if (currentUserId === null) return new Set();
        const now = Date.now();
        if (
            personalBuildingIdsCache.revision === buildingRegistryRevision &&
            personalBuildingIdsCache.userId === currentUserId &&
            now - personalBuildingIdsCache.createdAt <= PERSONAL_BUILDING_ID_CACHE_MS
        ) return personalBuildingIdsCache.values;

        const personalBuildingIds = new Set();
        for (const building of getBuildingMarkerCache()) {
            if (!building || building.user_id === undefined || building.user_id === null) continue;
            const buildingId = building.id ?? building.building_id;
            if (buildingId === undefined || buildingId === null) continue;
            if (String(building.user_id) === currentUserId) personalBuildingIds.add(String(buildingId));
        }
        personalBuildingIdsCache = {
            revision: buildingRegistryRevision,
            userId: currentUserId,
            createdAt: now,
            values: personalBuildingIds
        };
        return personalBuildingIds;
    }

    function getBuildingLayerId(layer) {
        if (!layer) return null;
        const buildingId = layer.building_id ?? layer.buildingId ?? layer.options?.building_id ?? layer.options?.buildingId ?? layer.building?.id ?? layer.options?.building?.id;
        return buildingId === undefined || buildingId === null ? null : String(buildingId);
    }

    function isPersonalBuildingLayer(layer, personalBuildingIds = getPersonalBuildingIds()) {
        if (!layer) return false;

        const buildingId = getBuildingLayerId(layer);
        if (buildingId === null) return false;
        if (personalBuildingIds.has(buildingId)) return true;

        const currentUserId = currentUserIdCached();
        if (currentUserId === null) return false;

        const layerUserId = layer.user_id ?? layer.userId ?? layer.options?.user_id ?? layer.options?.userId ?? layer.building?.user_id ?? layer.options?.building?.user_id;
        return layerUserId !== undefined && layerUserId !== null && String(layerUserId) === currentUserId;
    }

    function getPersonalBuildingMarkerIcons() {
        const personalBuildingIds = getPersonalBuildingIds();
        const personalBuildingMarkerIcons = new Set();

        for (const marker of getBuildingMarkerLayers()) {
            if (!marker._icon || marker._icon.nodeType !== 1) continue;
            if (isPersonalBuildingLayer(marker, personalBuildingIds)) personalBuildingMarkerIcons.add(marker._icon);
        }

        return personalBuildingMarkerIcons;
    }

    function markPersonalBuildingIcon(icon) {
        applyMarkerType(icon, 'personal-building');
    }


    function markPersonalBuildingLayerIfOwned(layer, personalBuildingIds = getPersonalBuildingIds()) {
        if (!isPersonalBuildingLayer(layer, personalBuildingIds)) return false;
        if (layer._icon) markPersonalBuildingIcon(layer._icon);
        return true;
    }

    function restorePersonalBuildingLayerOpacity(layer) {
        const originalOpacity = personalBuildingLayerOpacity.get(layer);
        personalBuildingLayerOpacity.delete(layer);
        try {
            if (typeof layer?.setOpacity === 'function') layer.setOpacity(Number.isFinite(originalOpacity) ? originalOpacity : 1);
        } catch (err) {}
    }

    function hidePersonalBuildingLayer(map, layer, personalBuildingIds = getPersonalBuildingIds()) {
        if (!map || !markPersonalBuildingLayerIfOwned(layer, personalBuildingIds)) return false;

        hiddenPersonalBuildingLayers.add(layer);

        if (!personalBuildingLayerOpacity.has(layer)) {
            const currentOpacity = Number(layer.options?.opacity);
            personalBuildingLayerOpacity.set(layer, Number.isFinite(currentOpacity) ? currentOpacity : 1);
        }

        try {
            if (typeof layer.setOpacity === 'function') layer.setOpacity(0);
        } catch (err) {}

        try {
            const isOnMap = typeof map.hasLayer === 'function' ? map.hasLayer(layer) : Boolean(layer._map);
            if (isOnMap && typeof map.removeLayer === 'function') {
                const previousEnforcementState = enforcingPersonalBuildingVisibility;
                enforcingPersonalBuildingVisibility = true;
                try { map.removeLayer(layer); }
                finally { enforcingPersonalBuildingVisibility = previousEnforcementState; }
            }
        } catch (err) {}

        return true;
    }

    function synchronisePersonalBuildingVisibility(map = findLeafletMapInstance(false)) {
        if (!map || enforcingPersonalBuildingVisibility) return;

        const currentBuildingLayers = getBuildingMarkerLayers().filter(Boolean);
        const currentBuildingLayerSet = new Set(currentBuildingLayers);
        const personalBuildingIds = getPersonalBuildingIds();

        if (!state.visibility.buildings) {
            for (const layer of Array.from(hiddenPersonalBuildingLayers)) {
                if (!currentBuildingLayerSet.has(layer)) {
                    hiddenPersonalBuildingLayers.delete(layer);
                    restorePersonalBuildingLayerOpacity(layer);
                }
            }

            for (const layer of currentBuildingLayers) hidePersonalBuildingLayer(map, layer, personalBuildingIds);
            return;
        }

        enforcingPersonalBuildingVisibility = true;
        try {
            const layersToRestore = new Set([...hiddenPersonalBuildingLayers, ...personalBuildingLayerOpacity.keys()]);
            for (const layer of layersToRestore) {
                const wasHidden = hiddenPersonalBuildingLayers.delete(layer);
                restorePersonalBuildingLayerOpacity(layer);
                if (!wasHidden || !currentBuildingLayerSet.has(layer)) continue;
                const isOnMap = typeof map.hasLayer === 'function' ? map.hasLayer(layer) : Boolean(layer._map);
                if (!isOnMap && typeof map.addLayer === 'function') map.addLayer(layer);
            }
        } catch (err) {
        } finally {
            enforcingPersonalBuildingVisibility = false;
        }
    }

    function getVehicleMarkerIcons() {
        const vehicleMarkerIcons = new Set();

        for (const marker of getVehicleMarkerLayers()) {
            if (!marker || !marker._icon || marker._icon.nodeType !== 1) continue;
            vehicleMarkerIcons.add(marker._icon);
        }

        return vehicleMarkerIcons;
    }

    function markVehicleIcon(icon) {
        applyMarkerType(icon, 'vehicle');
    }

    function synchroniseVehicleMarkerClasses() {
        const vehicleMarkerIcons = getVehicleMarkerIcons();
        for (const icon of vehicleMarkerIcons) markVehicleIcon(icon);
        return vehicleMarkerIcons;
    }

    function getMissionIconsByOwnership() {
        const personalMissionIcons = new Set();
        const allianceMissionIcons = new Set();
        const normalisedCurrentUserId = currentUserIdCached();
        if (normalisedCurrentUserId === null) return { personalMissionIcons, allianceMissionIcons };
        for (const marker of getMissionMarkerLayers()) {
            if (!marker || marker.mission_id === undefined || marker.mission_id === null) continue;
            if (!marker._icon || marker._icon.nodeType !== 1) continue;
            if (marker.user_id === undefined || marker.user_id === null) continue;
            if (String(marker.user_id) === normalisedCurrentUserId) personalMissionIcons.add(marker._icon);
            else allianceMissionIcons.add(marker._icon);
        }

        return { personalMissionIcons, allianceMissionIcons };
    }

    const MARKER_CLASS_NAMES = [
        'mcms-marker-mission', 'mcms-marker-my-mission', 'mcms-marker-alliance-mission',
        'mcms-marker-building', 'mcms-marker-personal-building', 'mcms-marker-vehicle', 'mcms-marker-unknown'
    ];

    function markerClassesForType(type) {
        if (type === 'vehicle') return ['mcms-marker-vehicle'];
        if (type === 'personal-building') return ['mcms-marker-building', 'mcms-marker-personal-building'];
        if (type === 'building') return ['mcms-marker-building'];
        if (type === 'alliance-mission') return ['mcms-marker-mission', 'mcms-marker-alliance-mission'];
        if (type === 'my-mission') return ['mcms-marker-mission', 'mcms-marker-my-mission'];
        return ['mcms-marker-unknown'];
    }

    function markerTypeIsApplied(icon, type) {
        if (!icon?.classList || icon.dataset?.mcmsMarkerKind !== type) return false;
        const desired = new Set(markerClassesForType(type));
        for (const className of MARKER_CLASS_NAMES) {
            if (icon.classList.contains(className) !== desired.has(className)) return false;
        }
        if (type === 'vehicle' && icon.getAttribute('data-mcms-vehicle-marker') !== 'true') return false;
        if (type === 'personal-building' && icon.getAttribute('data-mcms-personal-building-marker') !== 'true') return false;
        return true;
    }

    function applyMarkerType(icon, type) {
        if (!icon || icon.nodeType !== 1 || !icon.classList) return;
        const normalisedType = ['vehicle', 'personal-building', 'building', 'alliance-mission', 'my-mission'].includes(type) ? type : 'unknown';
        if (markerTypeIsApplied(icon, normalisedType)) return;
        const desired = new Set(markerClassesForType(normalisedType));
        for (const className of MARKER_CLASS_NAMES) {
            const shouldHave = desired.has(className);
            if (icon.classList.contains(className) !== shouldHave) icon.classList.toggle(className, shouldHave);
        }
        if (normalisedType === 'vehicle') {
            if (icon.getAttribute('data-mcms-vehicle-marker') !== 'true') icon.setAttribute('data-mcms-vehicle-marker', 'true');
            if (icon.hasAttribute('data-mcms-personal-building-marker')) icon.removeAttribute('data-mcms-personal-building-marker');
        } else if (normalisedType === 'personal-building') {
            if (icon.getAttribute('data-mcms-personal-building-marker') !== 'true') icon.setAttribute('data-mcms-personal-building-marker', 'true');
            if (icon.hasAttribute('data-mcms-vehicle-marker')) icon.removeAttribute('data-mcms-vehicle-marker');
        } else {
            if (icon.hasAttribute('data-mcms-personal-building-marker')) icon.removeAttribute('data-mcms-personal-building-marker');
            if (icon.hasAttribute('data-mcms-vehicle-marker')) icon.removeAttribute('data-mcms-vehicle-marker');
        }
        if (icon.dataset) icon.dataset.mcmsMarkerKind = normalisedType;
    }

    function classifyMarkersNow() {
        const mapEl = getLargestLeafletMap();
        if (!mapEl) return;

        const { personalMissionIcons, allianceMissionIcons } = getMissionIconsByOwnership();
        const vehicleMarkerIcons = getVehicleMarkerIcons();
        const personalBuildingMarkerIcons = getPersonalBuildingMarkerIcons();

        for (const icon of mapEl.querySelectorAll('.leaflet-marker-icon')) {
            const type = personalMissionIcons.has(icon)
                ? 'my-mission'
                : allianceMissionIcons.has(icon)
                    ? 'alliance-mission'
                    : vehicleMarkerIcons.has(icon)
                        ? 'vehicle'
                        : personalBuildingMarkerIcons.has(icon) || icon.getAttribute('data-mcms-personal-building-marker') === 'true'
                            ? 'personal-building'
                            : classifyMarker(icon);
            applyMarkerType(icon, type);
        }
    }

    function scheduleMarkerStateSync(delay = 20, trailing = false) {
        const timerName = trailing ? 'markerStateTrailingTimer' : 'markerStateSyncTimer';
        const currentTimer = trailing ? markerStateTrailingTimer : markerStateSyncTimer;
        runtimeClearTimeout(currentTimer);
        const callback = () => {
            if (trailing) markerStateTrailingTimer = null;
            else markerStateSyncTimer = null;
            if (runtime.destroyed || document.hidden) return;
            if (!state.visibility.vehicles || state.markerFocus) synchroniseVehicleMarkerClasses();
            if (!state.visibility.buildings) synchronisePersonalBuildingVisibility();
        };
        const id = runtimeSetTimeout(callback, Math.max(0, Number(delay) || 0));
        if (timerName === 'markerStateTrailingTimer') markerStateTrailingTimer = id;
        else markerStateSyncTimer = id;
    }

    function scheduleMarkerClassification() {
        runtimeClearTimeout(classifyTimer);
        classifyTimer = runtimeSetTimeout(classifyMarkersNow, state.economyMode ? 420 : 180);
    }

    function markerClassificationNeeded() {
        return Boolean(
            state.markerFocus || state.missionPulse || criticalViewActive ||
            !state.visibility.vehicles || !state.visibility.buildings ||
            !state.visibility.myMissions || !state.visibility.allianceMissions
        );
    }

    function vehicleDataNeeded() {
        return Boolean(
            state.unitCommitment || state.allianceCredits || state.resourceGap.enabled ||
            state.missionInspector || state.stuckDetector.enabled || criticalViewActive ||
            document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open') ||
            document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open') ||
            transportSweepRuntime.running
        );
    }

    function missionSnapshotsNeeded() {
        return Boolean(
            state.payoutFlash.enabled || state.transportWatcher || state.stuckDetector.enabled ||
            state.missionSpawn.enabled || state.allianceCredits || state.missionAge ||
            state.unitCommitment || state.resourceGap.enabled || state.majorIncidentFeed.enabled || criticalViewActive ||
            operationalUiIsVisible() || missionInspectorMarker
        );
    }

    function isToolkitLeafletLayer(layer) {
        return Boolean(layer && (
            layer.__mcmsHeatmapCell || layer.__mcmsHeatmapLayer ||
            layer.__mcmsCoverageRing || layer.__mcmsCoverageLayer ||
            layer.__mcmsAllianceCreditLabel || layer.__mcmsAllianceCreditLayer ||
            layer.__mcmsMissionAgeLabel || layer.__mcmsMissionAgeLayer ||
            layer.__mcmsUnitCommitmentLabel || layer.__mcmsUnitCommitmentLayer ||
            layer.__mcmsTransportWatcherLabel || layer.__mcmsTransportWatcherLayer ||
            layer.__mcmsResourceGapLabel || layer.__mcmsResourceGapLayer ||
            layer.__mcmsStuckMissionLabel || layer.__mcmsStuckMissionLayer ||
            layer.__mcmsMissionSpawnLabel || layer.__mcmsMissionSpawnRing || layer.__mcmsMissionSpawnLayer ||
            layer.__mcmsMissionLockOnMarker || layer.__mcmsMissionLockOnLayer
        ));
    }

    let enabledMapRefreshTimer = null;
    let pendingEnabledMapRefresh = { includeSnapshots: false, positionPanel: false, refreshOperational: false, fullRefresh: false };

    function flushEnabledMapRefreshes() {
        enabledMapRefreshTimer = null;
        if (runtime.destroyed) return;
        const request = pendingEnabledMapRefresh;
        pendingEnabledMapRefresh = { includeSnapshots: false, positionPanel: false, refreshOperational: false, fullRefresh: false };

        if (request.fullRefresh && markerClassificationNeeded()) scheduleMarkerClassification();
        if (state.coverage.enabled) scheduleCoverageRefresh();
        if (state.heatmap.enabled) scheduleHeatmapRefresh();
        if (request.fullRefresh && state.allianceCredits) scheduleAllianceCreditRefresh();
        if (request.fullRefresh && state.missionAge) scheduleMissionAgeRefresh();
        if (request.fullRefresh && state.unitCommitment) scheduleUnitCommitmentRefresh();
        if (request.fullRefresh && state.resourceGap.enabled) scheduleResourceGapRefresh();
        if (request.includeSnapshots && missionSnapshotsNeeded()) {
            scheduleMissionSnapshotRefresh();
        } else if (request.fullRefresh) {
            if (state.transportWatcher) scheduleTransportWatcherRefresh();
            if (state.stuckDetector.enabled) scheduleStuckMissionRefresh();
        }
        if (request.refreshOperational && operationalUiIsVisible()) scheduleOperationalPanelsRender(800);
        if (request.positionPanel && !dragState) schedulePanelPosition(true, 60);
    }

    function scheduleEnabledMapRefreshes({ includeSnapshots = true, positionPanel = false, refreshOperational = true, mapOnly = false } = {}) {
        pendingEnabledMapRefresh.includeSnapshots ||= Boolean(includeSnapshots);
        pendingEnabledMapRefresh.positionPanel ||= Boolean(positionPanel);
        pendingEnabledMapRefresh.refreshOperational ||= Boolean(refreshOperational);
        pendingEnabledMapRefresh.fullRefresh ||= !mapOnly;
        if (state.economyMode && economyMapMoving) return;
        if (enabledMapRefreshTimer !== null) return;
        enabledMapRefreshTimer = runtimeSetTimeout(flushEnabledMapRefreshes, state.economyMode ? 180 : 35);
    }

    function reconcileFeatureRefreshes({ includeSnapshots = true, positionPanel = false } = {}) {
        if (!state.coverage.enabled) clearCoverageRings();
        if (!state.heatmap.enabled) clearCoverageHeatmap();
        if (!state.allianceCredits) clearAllianceCreditLabels();
        if (!state.missionAge) clearMissionAgeLabels();
        if (!state.unitCommitment) clearUnitCommitmentLabels();
        if (!state.transportWatcher) clearTransportWatcherLabels();
        if (!state.stuckDetector.enabled) clearStuckMissionLabels();
        if (!state.resourceGap.enabled) {
            clearResourceGapLabels();
            resourceGapAnalysisCache.clear();
            resourceGapVehicleContextCache = { key: '', createdAt: 0, available: [], byToken: new Map() };
        }
        if (!state.missionInspector) hideMissionInspector();
        if (state.majorIncidentFeed.enabled) scheduleMajorIncidentFeedRender(80);
        else removeMajorIncidentFeed();
        scheduleEnabledMapRefreshes({ includeSnapshots, positionPanel });
    }

    function detachMapEvents(map) {
        if (!map) return;
        for (let index = runtime.mapBindings.length - 1; index >= 0; index -= 1) {
            const binding = runtime.mapBindings[index];
            if (binding.map !== map) continue;
            try { binding.map.off(binding.types, binding.handler); } catch (err) {}
            runtime.mapBindings.splice(index, 1);
        }
    }

    function findLeafletMapInstance(showStatus = true) {
        const mapEl = getLargestLeafletMap();
        if (!mapEl) {
            detachMapEvents(cachedMap);
            cachedMap = null;
            cachedMapElement = null;
            return null;
        }

        if (cachedMap && typeof cachedMap.getContainer === 'function') {
            try {
                const container = cachedMap.getContainer();
                if (container === mapEl && container?.isConnected !== false) return cachedMap;
            } catch (err) {}
            detachMapEvents(cachedMap);
            cachedMap = null;
            cachedMapElement = null;
        }

        const now = Date.now();
        if (now - mapDiscoveryLastAttempt < MAP_DISCOVERY_RETRY_MS) return null;
        mapDiscoveryLastAttempt = now;

        const candidates = [];
        const seen = new Set();
        const candidateRoots = Array.from(new Set([pageWindow, window].filter(Boolean)));
        const names = [
            'map', 'missionMap', 'mission_map', 'missionChiefMap', 'missionchiefMap',
            'leafletMap', 'leaflet_map', 'mainMap', 'gameMap', 'mapInstance',
            'osmMap', 'osm_map', 'lssmMap'
        ];

        const addCandidate = value => {
            if (!value || seen.has(value) || (typeof value !== 'object' && typeof value !== 'function')) return;
            try {
                if (typeof value.getCenter === 'function' && typeof value.setView === 'function' && typeof value.getZoom === 'function' && typeof value.addLayer === 'function') {
                    seen.add(value);
                    candidates.push(value);
                }
            } catch (err) {}
        };

        for (const root of candidateRoots) {
            for (const name of names) {
                try { addCandidate(root[name]); } catch (err) {}
            }
        }

        // Scan data properties without invoking arbitrary page getters. MissionChief and
        // extensions expose many globals; reading every accessor was an avoidable hot path.
        for (const root of candidateRoots) {
            let properties;
            try { properties = Object.getOwnPropertyNames(root); } catch (err) { continue; }
            const prioritised = properties.filter(name => /map|leaflet/i.test(name));
            const fallback = properties.filter(name => !/map|leaflet/i.test(name)).slice(0, 160);
            for (const prop of [...prioritised, ...fallback]) {
                if (candidates.length >= 80) break;
                try {
                    const descriptor = Object.getOwnPropertyDescriptor(root, prop);
                    if (descriptor && Object.prototype.hasOwnProperty.call(descriptor, 'value')) addCandidate(descriptor.value);
                } catch (err) {}
            }
        }

        for (const map of candidates) {
            try {
                if (map.getContainer?.() === mapEl) {
                    cachedMap = map;
                    cachedMapElement = mapEl;
                    attachMapEvents(map);
                    return map;
                }
            } catch (err) {}
        }

        // Only use a container-agnostic fallback when exactly one credible map exists.
        if (candidates.length === 1) {
            cachedMap = candidates[0];
            cachedMapElement = mapEl;
            attachMapEvents(cachedMap);
            return cachedMap;
        }

        if (showStatus) setStatus('Leaflet map object not detected. Map jumps/rings may be unavailable on this page.');
        return null;
    }

    function attachMapEvents(map) {
        if (runtime.destroyed || !map || runtime.mapBindings.some(binding => binding.map === map)) return;

        const inferScope = layer => {
            if (!layer) return 'all';
            if (normaliseMissionId(layer.mission_id ?? layer.missionId ?? layer.options?.mission_id ?? layer.options?.missionId) !== null) return 'mission';
            if (getBuildingLayerId(layer) !== null) return 'building';
            const vehicleId = layer.vehicle_id ?? layer.vehicleId ?? layer.options?.vehicle_id ?? layer.options?.vehicleId ?? layer.params?.vehicle_id ?? layer.params?.vehicleId;
            if (vehicleId !== undefined && vehicleId !== null && vehicleId !== '') return 'vehicle';
            return 'all';
        };

        const onLayerAdd = event => {
            const layer = event?.layer;
            if (isToolkitLeafletLayer(layer) || economyLayerEnforcement) return;
            if (state.economyMode) applyEconomyToLeafletLayer(map, layer);
            const scope = inferScope(layer);
            invalidateMarkerRegistryCaches(scope);
            if (state.economyMode && economyMapMoving) {
                economyDeferredMapRefresh = true;
                return;
            }

            const isVehicleLayer = scope === 'vehicle';
            if (isVehicleLayer && layer?._icon) markVehicleIcon(layer._icon);
            if (state.markerFocus && isVehicleLayer) scheduleMarkerStateSync(0, false);
            if (scope === 'building') {
                const isPersonalBuilding = markPersonalBuildingLayerIfOwned(layer);
                if (isPersonalBuilding && !state.visibility.buildings) hidePersonalBuildingLayer(map, layer);
            }
            scheduleEnabledMapRefreshes({ includeSnapshots: scope === 'mission' || scope === 'vehicle' || scope === 'all', positionPanel: false });
            if (state.economyMode && (scope === 'vehicle' || scope === 'building')) scheduleEconomyLayerSync(80);
        };

        const onLayerRemove = event => {
            const layer = event?.layer;
            if (isToolkitLeafletLayer(layer) || enforcingPersonalBuildingVisibility || economyLayerEnforcement) return;
            const scope = inferScope(layer);
            invalidateMarkerRegistryCaches(scope);
            if (state.economyMode && economyMapMoving) {
                economyDeferredMapRefresh = true;
                return;
            }
            scheduleEnabledMapRefreshes({ includeSnapshots: scope !== 'building', positionPanel: false });
        };

        const onMapMoveStart = () => {
            economyMapMoving = true;
            document.documentElement.setAttribute('data-mcms-map-moving', 'true');
        };

        const onMapMove = () => {
            economyMapMoving = false;
            document.documentElement.setAttribute('data-mcms-map-moving', 'false');
            const deferredRefresh = economyDeferredMapRefresh || economyDeferredDomMutation;
            economyDeferredMapRefresh = false;
            economyDeferredDomMutation = false;
            if (deferredRefresh) {
                invalidateMarkerRegistryCaches('all');
                ensureUi();
            }
            if (state.economyMode) scheduleEconomyLayerSync(80);
            if (!state.visibility.vehicles || state.markerFocus || (!enforcingPersonalBuildingVisibility && !state.visibility.buildings)) scheduleMarkerStateSync(0, false);
            scheduleEnabledMapRefreshes({ includeSnapshots: deferredRefresh, positionPanel: true, refreshOperational: false, mapOnly: !deferredRefresh });
            if (document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open') && selectedCriticalDistanceOrigin() === 'live') {
                if (selectedCriticalSortMode() === 'closest' || selectedCriticalSortMode() === 'furthest') runtimeSetTimeout(() => renderCriticalDrawer(null, { updateViewTime: false }), 40);
                else runtimeSetTimeout(refreshCriticalDistanceNodes, 40);
            }
        };

        try {
            map.on('layeradd', onLayerAdd);
            map.on('layerremove', onLayerRemove);
            map.on('movestart zoomstart', onMapMoveStart);
            map.on('moveend zoomend', onMapMove);
            runtime.mapBindings.push(
                { map, types: 'layeradd', handler: onLayerAdd },
                { map, types: 'layerremove', handler: onLayerRemove },
                { map, types: 'movestart zoomstart', handler: onMapMoveStart },
                { map, types: 'moveend zoomend', handler: onMapMove }
            );
        } catch (err) {}
    }

    function setMapView(lat, lng, zoom) {
        const map = findLeafletMapInstance(true);
        if (!map || typeof map.setView !== 'function') {
            showToast('Map jump unavailable');
            return false;
        }
        try {
            map.setView([lat, lng], zoom, state.economyMode ? { animate: false } : undefined);
            return true;
        } catch (err) {
            showToast('Map jump failed');
            return false;
        }
    }

    function economyLeafletPathRenderer(map) {
        if (!state.economyMode || !map || typeof pageWindow.L?.canvas !== 'function') return undefined;
        try {
            if (!economyCanvasRenderer || economyCanvasRenderer._map !== map) {
                const previousRenderer = economyCanvasRenderer;
                if (previousRenderer?._map && previousRenderer._map !== map) {
                    try { previousRenderer._map.removeLayer?.(previousRenderer); } catch (err) {}
                }
                economyCanvasRenderer = pageWindow.L.canvas({ padding: 0.08, tolerance: 2 });
                economyCanvasRenderer.__mcmsEconomyRenderer = true;
            }
            return economyCanvasRenderer;
        } catch (err) { return undefined; }
    }

    function disposeEconomyCanvasRenderer(map = findLeafletMapInstance(false)) {
        const renderer = economyCanvasRenderer;
        economyCanvasRenderer = null;
        if (!renderer || !map) return;
        try { if (map.hasLayer?.(renderer)) map.removeLayer(renderer); } catch (err) {}
    }

    function visibleBuildingLayers(map) {
        if (!map) return [];
        const bounds = typeof map.getBounds === 'function' ? map.getBounds() : null;
        const layers = [];
        const seen = new Set();

        for (const layer of getBuildingMarkerLayers()) {
            if (!layer || seen.has(layer) || typeof layer.getLatLng !== 'function') continue;
            if (!isPersonalBuildingLayer(layer)) continue;
            try {
                if (typeof map.hasLayer === 'function' && !map.hasLayer(layer)) continue;
                const latLng = layer.getLatLng();
                if (!latLng || (bounds?.contains && !bounds.contains(latLng))) continue;
                seen.add(layer);
                layers.push(layer);
            } catch (err) {}
        }
        return layers;
    }

    function clearCoverageRings() {
        if (coverageGroup) {
            try { coverageGroup.clearLayers(); coverageGroup.remove(); } catch (err) {}
        }
        coverageGroup = null;
        coverageRenderSignature = '';
    }

    function updateCoverageRings() {
        if (state.economyMode && economyMapMoving) return;
        if (!state.coverage.enabled) { clearCoverageRings(); return; }
        const map = findLeafletMapInstance(false);

        if (!map || !pageWindow.L || typeof pageWindow.L.circle !== 'function' || typeof pageWindow.L.layerGroup !== 'function') {
            setStatus('Coverage rings need access to the active Leaflet map object.');
            return;
        }

        try {
            const layers = visibleBuildingLayers(map).slice(0, 200);
            const radiusMi = Number(state.coverage.radiusMi) || 10;
            const layerSignature = layers.map(layer => {
                const point = layer.getLatLng();
                return `${getBuildingLayerId(layer) ?? layer._leaflet_id ?? ''}:${Number(point.lat).toFixed(5)}:${Number(point.lng).toFixed(5)}`;
            }).join('|');
            const signature = `${radiusMi}:${buildingRegistryRevision}:${layerSignature}`;
            if (coverageGroup?._map === map && coverageRenderSignature === signature) return;

            if (!coverageGroup || coverageGroup._map !== map) {
                if (coverageGroup && typeof coverageGroup.remove === 'function') coverageGroup.remove();
                coverageGroup = pageWindow.L.layerGroup();
                coverageGroup.__mcmsCoverageLayer = true;
                coverageGroup.addTo(map);
            }
            coverageGroup.clearLayers();
            coverageRenderSignature = signature;

            const metres = radiusMi * 1609.344;
            const renderer = economyLeafletPathRenderer(map);
            for (const layer of layers) {
                const ring = pageWindow.L.circle(layer.getLatLng(), {
                    radius: metres,
                    renderer,
                    interactive: false,
                    color: '#56a9ff',
                    weight: 1,
                    opacity: 0.34,
                    fillColor: '#56a9ff',
                    fillOpacity: 0.035
                });
                ring.__mcmsCoverageRing = true;
                ring.addTo(coverageGroup);
            }

            setStatus(`Coverage rings: ${layers.length} visible personal building${layers.length === 1 ? '' : 's'}, ${radiusMi} mile radius.`);
        } catch (err) {
            coverageRenderSignature = '';
            setStatus('Coverage rings failed to draw on this map view.');
        }
    }

    function scheduleCoverageRefresh() {
        runtimeClearTimeout(coverageTimer);
        coverageTimer = runtimeSetTimeout(updateCoverageRings, state.economyMode ? 650 : 220);
    }

    function heatmapServiceFromSignal(value, buildingType = null) {
        const signal = String(value || '').toLowerCase();
        if (/helicopter|air ambulance|aircraft|fixed wing|hangar|hems/.test(signal)) return 'air';
        if (/ambulance|paramedic|medical|hospital|doctor|patient/.test(signal)) return 'ambulance';
        if (/police|constable|armed response|traffic police|prison|dog unit|riot/.test(signal)) return 'police';
        if (/boat|coast|water rescue|marine|lifeboat|dock/.test(signal)) return 'water';
        if (/fire|rescue|engine|ladder|hazmat|foam|aerial/.test(signal)) return 'fire';

        const type = Number(buildingType);
        if ([0, 1].includes(type)) return 'fire';
        if ([2, 3, 4].includes(type)) return 'ambulance';
        if ([5, 9, 12].includes(type)) return 'air';
        if ([6, 7, 11, 13].includes(type)) return 'police';
        return 'other';
    }

    function heatmapPointFromObject(item) {
        if (!item) return null;
        let lat = item.lat ?? item.latitude ?? item.position?.lat ?? item.options?.lat;
        let lng = item.lng ?? item.lon ?? item.longitude ?? item.position?.lng ?? item.options?.lng;
        if ((!Number.isFinite(Number(lat)) || !Number.isFinite(Number(lng))) && typeof item.getLatLng === 'function') {
            try { const point = item.getLatLng(); lat = point?.lat; lng = point?.lng; } catch (err) {}
        }
        lat = Number(lat); lng = Number(lng);
        return Number.isFinite(lat) && Number.isFinite(lng) ? { lat, lng } : null;
    }

    function heatmapSourcePoints() {
        const requestedService = state.heatmap.service;
        const cacheKey = [state.heatmap.source, requestedService, markerRegistryRevision, buildingRegistryRevision, vehicleDataRevision, currentUserIdCached()].join(':');
        const now = Date.now();
        if (heatmapSourceCache.key === cacheKey && now - heatmapSourceCache.createdAt <= HEATMAP_SOURCE_CACHE_MS) return heatmapSourceCache.points;

        const points = [];
        if (state.heatmap.source === 'vehicles') {
            for (const vehicle of getVehicleMarkerLayers()) {
                const point = heatmapPointFromObject(vehicle);
                if (!point) continue;
                const service = heatmapServiceFromSignal([vehicle.caption, vehicle.name, vehicle.vehicle_type, vehicle.vehicle_type_caption, vehicle.options?.title, vehicle._icon?.title, vehicle._icon?.alt].filter(Boolean).join(' '));
                if (requestedService !== 'all' && service !== requestedService) continue;
                points.push(point);
            }
        } else {
            const currentUserId = currentUserIdCached();
            const activeBuildingsById = new Map(getBuildingMarkerLayers().map(layer => [String(layer?.building_id ?? layer?.id ?? ''), layer]));
            for (const building of getBuildingMarkerCache()) {
                if (!building) continue;
                if (currentUserId !== null && (building.user_id === undefined || building.user_id === null || String(building.user_id) !== currentUserId)) continue;
                const activeLayer = activeBuildingsById.get(String(building.id ?? building.building_id ?? ''));
                const point = heatmapPointFromObject(building) || heatmapPointFromObject(activeLayer);
                if (!point) continue;
                const service = heatmapServiceFromSignal([building.caption, building.name, building.building_type_caption, building.type_name, building.building_marker_image, activeLayer?.options?.title, activeLayer?._icon?.title].filter(Boolean).join(' '), building.building_type);
                if (requestedService !== 'all' && service !== requestedService) continue;
                points.push(point);
            }
        }

        heatmapSourceCache = { key: cacheKey, createdAt: now, points };
        return points;
    }

    function heatmapDistanceMiles(a, b) {
        const radians = value => value * Math.PI / 180;
        const dLat = radians(b.lat - a.lat);
        const dLng = radians(b.lng - a.lng);
        const lat1 = radians(a.lat);
        const lat2 = radians(b.lat);
        const value = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
        return 3958.7613 * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
    }

    function heatmapColour(nearest, radius, supportingSources) {
        if (nearest <= radius * 0.30 && supportingSources >= 2) return '#00c853';
        if (nearest <= radius * 0.55) return '#64dd17';
        if (nearest <= radius) return '#ffd600';
        if (nearest <= radius * 1.5) return '#ff9100';
        return '#d50000';
    }

    function clearCoverageHeatmap() {
        if (heatmapGroup) {
            try { heatmapGroup.clearLayers(); heatmapGroup.remove(); } catch (err) {}
        }
        heatmapGroup = null;
        heatmapRenderSignature = '';
    }

    function updateCoverageHeatmap() {
        if (state.economyMode && economyMapMoving) return;
        if (!state.heatmap.enabled) { clearCoverageHeatmap(); return; }
        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L?.layerGroup || !pageWindow.L?.rectangle || typeof map.getBounds !== 'function') {
            setStatus('Coverage Heatmap needs access to the active Leaflet map.');
            return;
        }

        const bounds = map.getBounds();
        const north = Number(bounds.getNorth?.());
        const south = Number(bounds.getSouth?.());
        const east = Number(bounds.getEast?.());
        const west = Number(bounds.getWest?.());
        if (![north, south, east, west].every(Number.isFinite) || north <= south || east <= west) return;

        const radius = Number(state.heatmap.radiusMi) || 10;
        const opacity = Number(state.heatmap.opacity) || 0.30;
        const latitudeMargin = radius * 1.6 / 69;
        const middleLatitude = (north + south) / 2;
        const milesPerLng = Math.max(12, 69 * Math.cos(middleLatitude * Math.PI / 180));
        const longitudeMargin = radius * 1.6 / milesPerLng;
        const sources = heatmapSourcePoints().filter(point => point.lat >= south - latitudeMargin && point.lat <= north + latitudeMargin && point.lng >= west - longitudeMargin && point.lng <= east + longitudeMargin);
        const sourceLabel = `${state.heatmap.service === 'all' ? '' : state.heatmap.service + ' '}${state.heatmap.source}`;

        const columns = state.economyMode ? 8 : 20;
        const mapRect = map.getContainer?.().getBoundingClientRect?.();
        const aspect = mapRect?.width && mapRect?.height ? mapRect.height / mapRect.width : 0.65;
        const rows = state.economyMode
            ? Math.max(4, Math.min(8, Math.round(columns * aspect)))
            : Math.max(10, Math.min(20, Math.round(columns * aspect)));
        const sourceFingerprint = sources.reduce((acc, point) => acc + Math.round(point.lat * 1000) * 31 + Math.round(point.lng * 1000), 0);
        const signature = [north, south, east, west].map(value => value.toFixed(5)).join(':') + `:${rows}:${columns}:${radius}:${opacity}:${state.heatmap.source}:${state.heatmap.service}:${sources.length}:${sourceFingerprint}`;
        if (heatmapGroup?._map === map && heatmapRenderSignature === signature) return;

        if (!heatmapGroup || heatmapGroup._map !== map) {
            clearCoverageHeatmap();
            heatmapGroup = pageWindow.L.layerGroup();
            heatmapGroup.__mcmsHeatmapLayer = true;
            heatmapGroup.addTo(map);
        }
        heatmapGroup.clearLayers();
        heatmapRenderSignature = signature;

        if (!sources.length) {
            setStatus(`Heatmap: no ${sourceLabel} detected in this area.`);
            return;
        }

        const latStep = (north - south) / rows;
        const lngStep = (east - west) / columns;
        const renderer = economyLeafletPathRenderer(map);
        const bucketSize = Math.max(1, radius * 1.5);
        const buckets = new Map();
        const projectedSources = sources.map(source => ({
            ...source,
            x: source.lng * milesPerLng,
            y: source.lat * 69
        }));
        for (const source of projectedSources) {
            const key = `${Math.floor(source.x / bucketSize)}:${Math.floor(source.y / bucketSize)}`;
            const bucket = buckets.get(key) || [];
            bucket.push(source);
            buckets.set(key, bucket);
        }

        for (let row = 0; row < rows; row += 1) {
            for (let column = 0; column < columns; column += 1) {
                const cellSouth = south + row * latStep;
                const cellWest = west + column * lngStep;
                const centre = { lat: cellSouth + latStep / 2, lng: cellWest + lngStep / 2 };
                const centreX = centre.lng * milesPerLng;
                const centreY = centre.lat * 69;
                const bucketX = Math.floor(centreX / bucketSize);
                const bucketY = Math.floor(centreY / bucketSize);
                let nearest = Infinity;
                let supportingSources = 0;
                for (let dx = -1; dx <= 1; dx += 1) {
                    for (let dy = -1; dy <= 1; dy += 1) {
                        const candidates = buckets.get(`${bucketX + dx}:${bucketY + dy}`) || [];
                        for (const source of candidates) {
                            const distance = heatmapDistanceMiles(centre, source);
                            if (distance < nearest) nearest = distance;
                            if (distance <= radius) supportingSources += 1;
                        }
                    }
                }
                const colour = heatmapColour(nearest, radius, supportingSources);
                const cell = pageWindow.L.rectangle([[cellSouth, cellWest], [cellSouth + latStep, cellWest + lngStep]], {
                    interactive: false,
                    stroke: false,
                    fill: true,
                    renderer,
                    fillColor: colour,
                    fillOpacity: opacity
                });
                cell.__mcmsHeatmapCell = true;
                cell.addTo(heatmapGroup);
            }
        }

        setStatus(`Heatmap: ${sources.length} ${sourceLabel}, ${radius} mile planning radius.`);
    }

    function scheduleHeatmapRefresh() {
        runtimeClearTimeout(heatmapTimer);
        heatmapTimer = runtimeSetTimeout(updateCoverageHeatmap, state.economyMode ? 650 : 180);
    }

    function sanitiseBookmarkShortLabel(value) {
        return String(value || '')
            .normalize('NFKD')
            .replace(/[\u0300-\u036f]/gu, '')
            .toUpperCase()
            .replace(/[^A-Z0-9&/+ -]+/gu, ' ')
            .replace(/\s+/gu, ' ')
            .trim()
            .slice(0, SMART_BOOKMARK_LABEL_MAX);
    }

    function compactBookmarkWord(value, targetLength = SMART_BOOKMARK_SINGLE_WORD_MAX) {
        const original = String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/gu, '');
        const key = original.toLowerCase().replace(/[^a-z0-9]+/gu, '');
        if (!key) return '';
        if (SMART_BOOKMARK_WORDS[key]) return SMART_BOOKMARK_WORDS[key];

        let upper = key.toUpperCase();
        if (upper.length <= targetLength) return upper;
        upper = upper
            .replace(/BOROUGH$/u, 'BORO')
            .replace(/BURGH$/u, 'BRG')
            .replace(/FIELD$/u, 'FD')
            .replace(/SHIRE$/u, 'SHR')
            .replace(/INGTON$/u, 'NGTN')
            .replace(/CHESTER$/u, 'CHST');

        let compressed = upper.charAt(0) + upper.slice(1).replace(/[AEIOUY]/gu, '');
        compressed = compressed.replace(/(.)\1+/gu, '$1');
        if (compressed.length <= targetLength) return compressed;

        const target = Math.max(3, targetLength);
        const chars = Array.from(compressed);
        if (target <= 3) return `${chars[0]}${chars[Math.floor(chars.length / 2)]}${chars[chars.length - 1]}`;
        const result = [chars[0]];
        const interior = chars.slice(1, -1);
        const slots = target - 2;
        for (let index = 0; index < slots; index += 1) {
            const position = slots === 1 ? 0 : Math.round(index * (interior.length - 1) / (slots - 1));
            const character = interior[Math.max(0, position)];
            if (character && result[result.length - 1] !== character) result.push(character);
        }
        if (result[result.length - 1] !== chars[chars.length - 1]) result.push(chars[chars.length - 1]);
        return result.join('').slice(0, target);
    }

    function makeSmartBookmarkLabel(name, manualLabel = '') {
        const manual = sanitiseBookmarkShortLabel(manualLabel);
        if (manual) return manual;

        const rawWords = String(name || '')
            .normalize('NFKD')
            .replace(/[\u0300-\u036f]/gu, '')
            .toLowerCase()
            .match(/[a-z0-9]+/gu) || [];
        let words = rawWords.filter(word => !SMART_BOOKMARK_STOP_WORDS.has(word));
        if (words.length > 2) words = words.filter(word => !SMART_BOOKMARK_OPTIONAL_WORDS.has(word));
        if (!words.length) words = rawWords;
        if (!words.length) return 'PIN';

        const tokens = words.map((word, index) => compactBookmarkWord(word, index === 0 ? 5 : 4)).filter(Boolean);
        while (tokens.length > 1 && /^[NSEW]$/u.test(tokens[0]) && /^[NSEW]$/u.test(tokens[1])) {
            tokens.splice(0, 2, `${tokens[0]}${tokens[1]}`);
        }

        if (tokens.length === 1) return sanitiseBookmarkShortLabel(tokens[0]) || 'PIN';
        let label = tokens.join(' ');
        if (label.length <= SMART_BOOKMARK_LABEL_MAX) return label;

        const first = tokens[0].slice(0, 5);
        const remainder = tokens.slice(1).map(token => token.length <= 3 ? token : token.slice(0, 3));
        label = [first, ...remainder].join(' ');
        if (label.length <= SMART_BOOKMARK_LABEL_MAX) return label;

        const initials = tokens.slice(1).map(token => token.charAt(0)).join('');
        label = initials ? `${first} ${initials}` : first;
        return sanitiseBookmarkShortLabel(label) || 'PIN';
    }

    function bookmarkScreenLabel(bookmark) {
        return makeSmartBookmarkLabel(bookmark?.name || 'Bookmark', bookmark?.shortLabel || '');
    }

    function resolveScreenPinLabels(entries) {
        const counts = new Map();
        entries.forEach(entry => {
            const key = entry.baseLabel.toUpperCase();
            counts.set(key, (counts.get(key) || 0) + 1);
        });
        const seen = new Map();
        return entries.map(entry => {
            const key = entry.baseLabel.toUpperCase();
            const total = counts.get(key) || 1;
            if (total === 1) return { ...entry, label: entry.baseLabel };
            const number = (seen.get(key) || 0) + 1;
            seen.set(key, number);
            const suffix = ` ${number}`;
            const available = Math.max(3, SMART_BOOKMARK_LABEL_MAX - suffix.length);
            return { ...entry, label: `${entry.baseLabel.slice(0, available).trim()}${suffix}` };
        });
    }

    function editBookmarkLabel(slot) {
        const bookmark = state.bookmarks[slot];
        if (!bookmark) return;
        const name = pageWindow.prompt('Bookmark name:', bookmark.name || `Bookmark ${slot + 1}`);
        if (name === null) return;
        const cleanName = String(name || bookmark.name || `Bookmark ${slot + 1}`).trim().slice(0, 80) || `Bookmark ${slot + 1}`;
        const currentShortLabel = sanitiseBookmarkShortLabel(bookmark.shortLabel || '');
        const shortLabel = pageWindow.prompt('Short screen label (leave blank for automatic):', currentShortLabel);
        bookmark.name = cleanName;
        if (shortLabel !== null) bookmark.shortLabel = sanitiseBookmarkShortLabel(shortLabel);
        saveState();
        renderBookmarks();
        renderScreenPins();
        updateUI();
        showToast(`${bookmark.name} · ${bookmarkScreenLabel(bookmark)}`);
    }

    function saveBookmark(slot) {
        const map = findLeafletMapInstance(true);
        if (!map || typeof map.getCenter !== 'function' || typeof map.getZoom !== 'function') {
            showToast('Map object not detected');
            setStatus('Bookmark saving needs access to the active Leaflet map object.');
            return;
        }

        let center;
        let zoom;
        try {
            center = map.getCenter();
            zoom = map.getZoom();
        } catch (err) {
            showToast('Could not read map view');
            return;
        }

        const existing = state.bookmarks[slot];
        const fallback = existing?.name || `Bookmark ${slot + 1}`;
        const name = pageWindow.prompt('Bookmark name:', fallback);
        if (name === null) return;

        const cleanName = String(name || fallback).trim().slice(0, 80) || fallback;
        const currentShortLabel = sanitiseBookmarkShortLabel(existing?.shortLabel || '');
        const shortLabelPrompt = pageWindow.prompt('Short screen label (leave blank for automatic):', currentShortLabel);
        const shortLabel = shortLabelPrompt === null ? currentShortLabel : sanitiseBookmarkShortLabel(shortLabelPrompt);

        state.bookmarks[slot] = {
            name: cleanName,
            shortLabel,
            lat: Number(center.lat.toFixed(6)),
            lng: Number(center.lng.toFixed(6)),
            zoom: Number(zoom),
            pinned: existing ? Boolean(existing.pinned) : false
        };

        saveState();
        renderBookmarks();
        renderScreenPins();
        updateUI();
        showToast(`Bookmark saved · ${bookmarkScreenLabel(state.bookmarks[slot])}`);
    }

    function goBookmark(slot) {
        const bookmark = state.bookmarks[slot];
        if (!bookmark) {
            showToast('Empty bookmark');
            return;
        }
        if (setMapView(bookmark.lat, bookmark.lng, bookmark.zoom)) showToast(bookmark.name);
    }

    function deleteBookmark(slot) {
        const bookmark = state.bookmarks[slot];
        if (!bookmark) return;
        if (!pageWindow.confirm(`Delete bookmark "${bookmark.name}"?`)) return;
        state.bookmarks[slot] = null;
        saveState();
        renderBookmarks();
        renderScreenPins();
        updateUI();
        showToast('Bookmark deleted');
    }

    function toggleBookmarkPin(slot) {
        const bookmark = state.bookmarks[slot];
        if (!bookmark) {
            showToast('Save bookmark first');
            return;
        }
        bookmark.pinned = !bookmark.pinned;
        saveState();
        renderBookmarks();
        renderScreenPins();
        updateUI();
        showToast(bookmark.pinned ? 'Shortcut pinned' : 'Shortcut unpinned');
    }

    function toggleQuickPin(id) {
        if (!(id in state.quickPins)) return;
        state.quickPins[id] = !state.quickPins[id];
        saveState();
        renderQuickPlaces();
        renderScreenPins();
        updateUI();
        showToast(state.quickPins[id] ? 'Shortcut pinned' : 'Shortcut unpinned');
    }

    function loadPayoutHistory() {
        try {
            const parsed = JSON.parse(localStorage.getItem(SCRIPT.payoutHistoryState) || '[]');
            if (!Array.isArray(parsed)) return [];
            return parsed.filter(item => item && Number.isFinite(Number(item.amount)) && Number.isFinite(Number(item.timestamp)))
                .slice(0, PAYOUT_HISTORY_LIMIT)
                .map(item => ({
                    id: String(item.id || `${item.timestamp}-${item.amount}`),
                    timestamp: Number(item.timestamp),
                    amount: Math.max(0, Math.round(Number(item.amount))),
                    caption: String(item.caption || ''),
                    source: ['personal', 'alliance', 'unknown'].includes(item.source) ? item.source : 'unknown',
                    tier: ['standard', 'major', 'high', 'elite'].includes(item.tier) ? item.tier : 'standard'
                }));
        } catch (err) { return []; }
    }

    function savePayoutHistory() {
        try { localStorage.setItem(SCRIPT.payoutHistoryState, JSON.stringify(payoutHistory.slice(0, PAYOUT_HISTORY_LIMIT))); }
        catch (err) {}
    }

    function defaultSessionPerformance() {
        return {
            startedAt: Date.now(), creditsEarned: 0, payoutCount: 0, qualifyingCount: 0,
            largestPayout: 0, personalPayouts: 0, alliancePayouts: 0, unknownPayouts: 0
        };
    }

    function loadSessionPerformance() {
        try {
            const parsed = JSON.parse(sessionStorage.getItem(SCRIPT.sessionPerformanceState) || 'null');
            if (!parsed || typeof parsed !== 'object') return defaultSessionPerformance();
            return { ...defaultSessionPerformance(), ...parsed };
        } catch (err) { return defaultSessionPerformance(); }
    }

    function saveSessionPerformance() {
        try { sessionStorage.setItem(SCRIPT.sessionPerformanceState, JSON.stringify(sessionPerformance)); }
        catch (err) {}
    }

    function resetSessionPerformance() {
        Object.assign(sessionPerformance, defaultSessionPerformance());
        saveSessionPerformance();
        renderOperationalPanels();
        showToast('Session performance reset');
    }

    function clearPayoutHistory() {
        payoutHistory.splice(0, payoutHistory.length);
        savePayoutHistory();
        renderOperationalPanels();
        showToast('Payout history cleared');
    }


    function majorIncidentThemeLabel() {
        const labels = {
            mapCommand: 'MAJOR INCIDENTS',
            cyberpunk: 'CITY INCIDENT WIRE',
            fallout4: 'ROBCO EMERGENCY BAND',
            umbrella: 'CONTAINMENT ALERTS',
            factorio: 'FACTORY INCIDENT BUS',
            bond007: 'MI6 INCIDENT WIRE'
        };
        return labels[state.uiTheme] || labels.mapCommand;
    }

    function majorIncidentOperationalState(snapshot, now = Date.now()) {
        const units = snapshot?.units || {};
        const onScene = Math.max(0, Number(units.onScene) || 0);
        const travelling = Math.max(0, Number(units.travelling) || 0);
        const stuck = missionStuckRecord(snapshot?.missionId, now);
        const missing = summariseCriticalRequirement(snapshot?.missingText, 58);
        const clearing = criticalMissionClearingProgress(snapshot);

        if (stuck?.isStuck || missing) {
            return {
                key: 'alert',
                label: stuck?.isStuck ? `ASSISTANCE · STUCK ${formatStuckDuration(stuck.stuckForMs)}` : 'ASSISTANCE REQUIRED'
            };
        }
        if (clearing && onScene > 0) return { key: 'clearing', label: `CLEARING ${clearing.completion}%` };
        if (travelling > 0) return { key: 'responding', label: `${travelling} RESPONDING` };
        if (onScene > 0) return { key: 'active', label: `${onScene} ON SCENE` };
        return { key: 'major', label: 'AWAITING RESPONSE' };
    }

    function majorIncidentFeedEntries(now = Date.now()) {
        const minimumCredits = Math.max(0, Number(state.majorIncidentFeed?.minimumCredits) || 25000);
        const entries = [];
        for (const snapshot of liveMissionSnapshots.values()) {
            if (!snapshot || !Number.isFinite(Number(snapshot.lat)) || !Number.isFinite(Number(snapshot.lng))) continue;
            if (snapshot.source === 'personal' && !state.visibility.myMissions) continue;
            if (snapshot.source === 'alliance' && !state.visibility.allianceMissions) continue;

            const credits = Number(snapshot.averageCredits);
            const createdAt = Number(snapshot.createdAt);
            const ageMs = Number.isFinite(createdAt) && createdAt > 0 ? Math.max(0, now - createdAt) : 0;
            const stuck = missionStuckRecord(snapshot.missionId, now);
            const patients = Math.max(Number(snapshot.patientsCount) || 0, Number(snapshot.possiblePatientsCount) || 0);
            const prisoners = Math.max(Number(snapshot.prisonersCount) || 0, Number(snapshot.possiblePrisonersCount) || 0);
            const creditMajor = Number.isFinite(credits) && credits >= minimumCredits;
            const ageMajor = ageMs >= 24 * 60 * 60 * 1000;
            const massCasualty = patients >= MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS || prisoners >= MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS;
            if (!creditMajor && !ageMajor && !stuck?.isStuck && !massCasualty) continue;

            const operational = majorIncidentOperationalState(snapshot, now);
            const postcode = snapshot.postcode || normaliseMissionPostcode(snapshot.address) || 'POSTCODE N/A';
            const score =
                (stuck?.isStuck ? 900000000 : 0) +
                (snapshot.missingText ? 500000000 : 0) +
                (ageMajor ? Math.min(250000000, ageMs) : 0) +
                (massCasualty ? 150000000 + (patients * 1000000) + (prisoners * 750000) : 0) +
                (Number.isFinite(credits) ? credits : 0) +
                (snapshot.source === 'personal' ? 5000 : 0);

            entries.push({ snapshot, operational, postcode, credits, ageMs, patients, prisoners, score });
        }
        return entries.sort((a, b) => b.score - a.score || String(a.snapshot.caption || '').localeCompare(String(b.snapshot.caption || ''))).slice(0, MAJOR_INCIDENT_FEED_MAX_ITEMS);
    }

    function findLocationSearchInput() {
        const direct = document.querySelector('#map_search, #location_search, #location_search_input, input[name="location_search"]');
        if (direct && isVisible(direct)) return direct;
        const pattern = /(location|place|address|postcode|postal|ort|plaats|lokal|emplacement|ubicaci[oó]n|posizione)/iu;
        return Array.from(document.querySelectorAll('input[type="search"], input[type="text"], input:not([type])'))
            .filter(input => isVisible(input) && pattern.test(`${input.placeholder || ''} ${input.getAttribute('aria-label') || ''} ${input.title || ''}`))
            .sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top)[0] || null;
    }

    function findTopClockElement() {
        const clockPattern = /^\d{1,2}:\d{2}:\d{2}$/u;
        const preferred = Array.from(document.querySelectorAll('[id*="timer" i], [class*="timer" i], .navbar-text, .navbar-brand'))
            .find(element => isVisible(element) && clockPattern.test(String(element.textContent || '').trim()) && element.getBoundingClientRect().top < 160);
        if (preferred) return preferred;

        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
        let node;
        let scanned = 0;
        while ((node = walker.nextNode()) && scanned < 2500) {
            scanned += 1;
            if (node.id === SCRIPT.majorIncidentFeedId || node.closest?.(`#${SCRIPT.majorIncidentFeedId}`)) continue;
            if (node.children?.length > 2) continue;
            const text = String(node.textContent || '').trim();
            if (!clockPattern.test(text) || !isVisible(node)) continue;
            const rect = node.getBoundingClientRect();
            if (rect.top < 160 && rect.height >= 18 && rect.height <= 70) return node;
        }
        return null;
    }

    function findMissionChiefBrandElement(bar) {
        if (!bar) return null;
        const barRect = bar.getBoundingClientRect?.();
        if (!barRect) return null;

        const candidates = new Set();
        const addCandidate = element => {
            if (!element) return;
            const host = element.matches?.('a,button,[role="link"],.navbar-brand')
                ? element
                : element.closest?.('a,button,[role="link"],.navbar-brand') || element;
            if (host && host !== bar && !host.closest?.(`#${SCRIPT.majorIncidentFeedId}`)) candidates.add(host);
        };

        [
            '.navbar-brand',
            '[id*="logo" i]',
            '[class*="logo" i]',
            'a[href="/"]',
            'a[href="./"]',
            'a[href$="/dashboard"]',
            'a[href$="/missions"]'
        ].forEach(selector => {
            try { bar.querySelectorAll(selector).forEach(addCandidate); } catch (err) {}
        });
        try { bar.querySelectorAll('a,button,[role="link"],img,svg').forEach(addCandidate); } catch (err) {}

        const scored = Array.from(candidates).map(element => {
            if (!isVisible(element)) return null;
            const rect = element.getBoundingClientRect?.();
            if (!rect || rect.width < 18 || rect.height < 18 || rect.width > 180 || rect.height > 90) return null;
            if (rect.right <= barRect.left || rect.left >= barRect.right || rect.bottom <= barRect.top || rect.top >= barRect.bottom) return null;
            if (rect.left > barRect.left + Math.min(220, barRect.width * .24)) return null;

            const descriptor = `${element.id || ''} ${element.className || ''} ${element.getAttribute?.('href') || ''} ${element.getAttribute?.('aria-label') || ''} ${element.getAttribute?.('title') || ''} ${element.querySelector?.('img')?.alt || ''}`.toLowerCase();
            let score = Math.max(0, 100 - Math.abs(rect.left - barRect.left));
            if (element.matches?.('.navbar-brand')) score += 180;
            if (/missionchief|leitstellenspiel|meldkamerspel|logo|brand|home/.test(descriptor)) score += 90;
            if (/^(?:https?:\/\/[^/]+)?\/?$/u.test(String(element.getAttribute?.('href') || '').trim())) score += 80;
            if (element.querySelector?.('img,svg') || element.matches?.('img,svg')) score += 35;
            if (rect.left <= barRect.left + 80) score += 55;
            return { element, rect, score };
        }).filter(Boolean).sort((a, b) => b.score - a.score || a.rect.left - b.rect.left);

        return scored[0]?.element || null;
    }

    function commonTopBarAncestor(clockElement, searchInput) {
        if (clockElement && searchInput) {
            const clockAncestors = new Set();
            let current = clockElement;
            for (let depth = 0; current && depth < 10; depth += 1, current = current.parentElement) clockAncestors.add(current);
            current = searchInput;
            for (let depth = 0; current && depth < 10; depth += 1, current = current.parentElement) {
                if (!clockAncestors.has(current)) continue;
                const rect = current.getBoundingClientRect?.();
                if (rect && rect.top < 160 && rect.width >= 420 && rect.height >= 36 && rect.height <= 120) return current;
            }
        }
        const candidates = [
            clockElement?.closest?.('nav,header,.navbar,[role="banner"]'),
            searchInput?.closest?.('nav,header,.navbar,[role="banner"]'),
            ...Array.from(document.querySelectorAll('nav.navbar, header, .navbar, [role="banner"]'))
        ].filter(Boolean);
        return candidates.find(element => {
            if (!isVisible(element)) return false;
            const rect = element.getBoundingClientRect();
            return rect.top < 160 && rect.width >= 320 && rect.height >= 36 && rect.height <= 130;
        }) || null;
    }

    function majorIncidentFeedHeaderContext() {
        const searchInput = findLocationSearchInput();
        const clockElement = findTopClockElement();
        const bar = commonTopBarAncestor(clockElement, searchInput);
        const brandElement = findMissionChiefBrandElement(bar);
        return { bar, brandElement, clockElement, searchInput };
    }

    function removeMajorIncidentFeed() {
        runtimeClearTimeout(majorIncidentFeedRenderTimer);
        majorIncidentFeedRenderTimer = null;
        runtimeClearTimeout(majorIncidentFeedMotionTimer);
        majorIncidentFeedMotionTimer = null;
        majorIncidentFeedMotionRevision += 1;
        if (majorIncidentFeedLayoutFrame !== null) runtimeCancelAnimationFrame(majorIncidentFeedLayoutFrame);
        majorIncidentFeedLayoutFrame = null;
        runtimeClearTimeout(majorIncidentFeedLayoutTimer);
        majorIncidentFeedLayoutTimer = null;
        runtimeUntrackObserver(majorIncidentFeedResizeObserver);
        majorIncidentFeedResizeObserver = null;
        majorIncidentFeedObservedElement = null;
        document.getElementById(SCRIPT.majorIncidentFeedId)?.remove();
        majorIncidentFeedRenderSignature = '';
    }

    function majorIncidentFeedDomComplete(feed) {
        return Boolean(
            feed?.isConnected &&
            feed.querySelector?.('.mcms-incident-feed-label') &&
            feed.querySelector?.('.mcms-incident-feed-viewport') &&
            feed.querySelector?.('.mcms-incident-feed-track')
        );
    }

    function resetMajorIncidentFeedObserver() {
        runtimeUntrackObserver(majorIncidentFeedResizeObserver);
        majorIncidentFeedResizeObserver = null;
        majorIncidentFeedObservedElement = null;
    }

    function recoverMajorIncidentFeed(reason = 'lifecycle') {
        if (runtime.destroyed || document.hidden || !state.majorIncidentFeed.enabled) return false;
        if (!getLargestLeafletMap() || isAllianceBuildingsContext()) return false;

        let feed = document.getElementById(SCRIPT.majorIncidentFeedId);
        const needsRebuild = !majorIncidentFeedDomComplete(feed);
        if (needsRebuild) {
            if (feed) feed.remove();
            resetMajorIncidentFeedObserver();
            majorIncidentFeedRenderSignature = '';
            renderMajorIncidentFeed(true);
            console.debug(`[${SCRIPT.name}] Major Incident Feed recovered after ${reason}.`);
            return true;
        }

        if (majorIncidentFeedObservedElement !== feed && !state.economyMode) {
            resetMajorIncidentFeedObserver();
            majorIncidentFeedRenderSignature = '';
            renderMajorIncidentFeed(true);
            return true;
        }

        scheduleMajorIncidentFeedLayout();
        return false;
    }

    function refreshMajorIncidentFeedMotion(feed, forceRestart = false, attempt = 0, revision = majorIncidentFeedMotionRevision) {
        if (!feed || revision !== majorIncidentFeedMotionRevision || !feed.isConnected || !state.majorIncidentFeed.enabled) return false;
        const viewport = feed.querySelector('.mcms-incident-feed-viewport');
        const track = feed.querySelector('.mcms-incident-feed-track');
        const firstGroup = track?.querySelector('.mcms-incident-feed-group');
        if (!viewport || !track || !firstGroup) return false;

        if (state.economyMode) {
            feed.classList.add('mcms-feed-static');
            feed.style.removeProperty('--mcms-incident-feed-duration');
            track.style.removeProperty('animation');
            return true;
        }

        const viewportWidth = viewport.clientWidth;
        const groupWidth = Math.max(firstGroup.scrollWidth || 0, firstGroup.getBoundingClientRect?.().width || 0);
        if ((viewportWidth < 40 || groupWidth < 20) && attempt < 6) {
            runtimeClearTimeout(majorIncidentFeedMotionTimer);
            majorIncidentFeedMotionTimer = runtimeSetTimeout(() => {
                majorIncidentFeedMotionTimer = null;
                refreshMajorIncidentFeedMotion(feed, true, attempt + 1, revision);
            }, 70 + (attempt * 55));
            return false;
        }

        const entryCount = Math.max(0, Number(feed.dataset.mcmsEntryCount) || 0);
        const shouldScroll = entryCount > 1 || groupWidth > viewportWidth - 8;
        feed.classList.toggle('mcms-feed-static', !shouldScroll);
        if (!shouldScroll) {
            feed.style.removeProperty('--mcms-incident-feed-duration');
            track.style.removeProperty('animation');
            return true;
        }

        const reducedMotion = Boolean(pageWindow.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
        const pixelsPerSecond = reducedMotion ? 25 : 32;
        const duration = Math.round(clamp(groupWidth / pixelsPerSecond, 42, 210, 60));
        feed.style.setProperty('--mcms-incident-feed-duration', `${duration}s`);

        const animations = typeof track.getAnimations === 'function' ? track.getAnimations() : [];
        if (forceRestart || animations.length === 0) {
            track.style.setProperty('animation', 'none', 'important');
            void track.offsetWidth;
            track.style.removeProperty('animation');
        }
        return true;
    }

    function scheduleMajorIncidentFeedMotion(feed = document.getElementById(SCRIPT.majorIncidentFeedId), forceRestart = false, delay = 50) {
        if (!feed) return;
        runtimeClearTimeout(majorIncidentFeedMotionTimer);
        if (state.economyMode) {
            majorIncidentFeedMotionTimer = null;
            refreshMajorIncidentFeedMotion(feed, false, 0, ++majorIncidentFeedMotionRevision);
            return;
        }
        const revision = ++majorIncidentFeedMotionRevision;
        majorIncidentFeedMotionTimer = runtimeSetTimeout(() => {
            majorIncidentFeedMotionTimer = null;
            refreshMajorIncidentFeedMotion(feed, forceRestart, 0, revision);
        }, Math.max(0, Number(delay) || 0));
    }

    function positionMajorIncidentFeed() {
        majorIncidentFeedLayoutFrame = null;
        const feed = document.getElementById(SCRIPT.majorIncidentFeedId);
        if (!feed || !state.majorIncidentFeed.enabled || !getLargestLeafletMap() || isAllianceBuildingsContext()) {
            if (feed) feed.classList.remove('mcms-feed-visible');
            return false;
        }

        const { bar } = majorIncidentFeedHeaderContext();
        if (!bar) {
            feed.classList.remove('mcms-feed-visible');
            return false;
        }
        const barRect = bar.getBoundingClientRect();
        const viewport = getViewportMetrics();
        const mapElement = getLargestLeafletMap();
        const mapRect = mapElement?.getBoundingClientRect?.();
        const edgeGap = viewport.width <= 520 ? 1 : 2;
        const viewportLeft = viewport.offsetLeft;
        const viewportRight = viewport.offsetLeft + viewport.width;
        const mapLeft = Number.isFinite(mapRect?.left) ? Math.max(viewportLeft, mapRect.left) : viewportLeft;
        const mapRight = Number.isFinite(mapRect?.right) ? Math.min(viewportRight, mapRect.right) : viewportRight;
        const feedLeft = Math.round(mapLeft + edgeGap);
        const feedRight = Math.round(mapRight - edgeGap);
        const feedWidth = Math.max(1, feedRight - feedLeft);

        // v4.8.5: keep the permanent under-navigation feed aligned to the actual
        // Leaflet map bounds. This preserves the map's own left/right margins and
        // prevents the incident wire stretching across unrelated page controls.
        feed.dataset.mcmsPlacement = 'underbar';
        feed.style.setProperty('left', `${feedLeft}px`, 'important');
        feed.style.setProperty('top', `${Math.round(barRect.bottom + 1)}px`, 'important');
        feed.style.setProperty('width', `${Math.round(feedWidth)}px`, 'important');
        feed.classList.add('mcms-feed-visible');
        scheduleMajorIncidentFeedMotion(feed, false, 35);
        return true;
    }

    function scheduleMajorIncidentFeedLayout() {
        if (state.economyMode) {
            runtimeClearTimeout(majorIncidentFeedLayoutTimer);
            majorIncidentFeedLayoutTimer = runtimeSetTimeout(() => {
                majorIncidentFeedLayoutTimer = null;
                positionMajorIncidentFeed();
            }, 180);
            return;
        }
        if (majorIncidentFeedLayoutFrame !== null) return;
        majorIncidentFeedLayoutFrame = runtimeRequestAnimationFrame(positionMajorIncidentFeed);
    }

    function majorIncidentFeedItemHtml(entry) {
        const snapshot = entry.snapshot;
        const source = snapshot.source === 'alliance' ? 'ALLIANCE' : 'PERSONAL';
        const creditText = Number.isFinite(entry.credits) ? `≈${formatOperationalCompactCredits(entry.credits)} CR` : 'VALUE UNKNOWN';
        const ageText = entry.ageMs >= 8 * 60 * 60 * 1000 ? ` · ${formatElapsedCompact(entry.ageMs)} OLD` : '';
        const casualtyText = entry.patients >= MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS ? ` · ${entry.patients} PATIENTS` : entry.prisoners >= MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS ? ` · ${entry.prisoners} PRISONERS` : '';
        const caption = snapshot.caption || `Mission ${snapshot.missionId}`;
        const title = `${caption} · ${entry.postcode} · ${creditText} · Click to zoom to the mission`;
        return `<button class="mcms-incident-feed-item mcms-incident-${escapeHtml(entry.operational.key)}" type="button" data-mcms-major-mission-id="${escapeHtml(snapshot.missionId)}" title="${escapeHtml(title)}" aria-label="Zoom to ${escapeHtml(caption)} at ${escapeHtml(entry.postcode)}">
            <span class="mcms-incident-level">MAJOR</span>
            <span class="mcms-incident-name">${allianceAwareHtml(caption)}</span>
            <span class="mcms-incident-postcode">${escapeHtml(entry.postcode)}</span>
            <span class="mcms-incident-meta">${escapeHtml(`${creditText} · `)}<span class="${source === 'ALLIANCE' ? 'mcms-alliance-text' : ''}">${escapeHtml(source)}</span>${escapeHtml(`${ageText}${casualtyText}`)}</span>
            <span class="mcms-incident-state">${escapeHtml(entry.operational.label)}</span>
        </button>`;
    }

    function ensureMajorIncidentFeed() {
        if (!state.majorIncidentFeed.enabled || !getLargestLeafletMap() || isAllianceBuildingsContext()) {
            removeMajorIncidentFeed();
            return null;
        }

        let feed = document.getElementById(SCRIPT.majorIncidentFeedId);
        if (feed && !majorIncidentFeedDomComplete(feed)) {
            feed.remove();
            feed = null;
            resetMajorIncidentFeedObserver();
            majorIncidentFeedRenderSignature = '';
        }

        if (!feed) {
            resetMajorIncidentFeedObserver();
            majorIncidentFeedRenderSignature = '';
            feed = document.createElement('section');
            feed.id = SCRIPT.majorIncidentFeedId;
            feed.setAttribute('aria-label', 'Major incident news feed');
            feed.innerHTML = '<div class="mcms-incident-feed-label"></div><div class="mcms-incident-feed-viewport" aria-live="off"><div class="mcms-incident-feed-track"></div></div>';
            feed.addEventListener('click', event => {
                const item = closestEventTarget(event, '[data-mcms-major-mission-id]');
                if (!item) return;
                event.preventDefault();
                event.stopPropagation();
                focusMissionById(item.dataset.mcmsMajorMissionId, false);
            });
            feed.addEventListener('pointerdown', () => {
                feed.classList.add('mcms-feed-paused');
                runtimeSetTimeout(() => feed?.classList?.remove('mcms-feed-paused'), 1800);
            }, { passive: true });
            document.body.appendChild(feed);
        }

        if (state.economyMode) {
            resetMajorIncidentFeedObserver();
        } else if (majorIncidentFeedObservedElement !== feed && typeof pageWindow.ResizeObserver === 'function') {
            resetMajorIncidentFeedObserver();
            majorIncidentFeedObservedElement = feed;
            majorIncidentFeedResizeObserver = runtimeTrackObserver(new pageWindow.ResizeObserver(() => {
                if (feed.isConnected) scheduleMajorIncidentFeedMotion(feed, false, 70);
                else recoverMajorIncidentFeed('header replacement');
            }));
            majorIncidentFeedResizeObserver.observe(feed);
            const viewport = feed.querySelector('.mcms-incident-feed-viewport');
            if (viewport) majorIncidentFeedResizeObserver.observe(viewport);
        }

        scheduleMajorIncidentFeedLayout();
        return feed;
    }

    function renderMajorIncidentFeed(force = false) {
        const feed = ensureMajorIncidentFeed();
        if (!feed) return;
        const entries = state.economyMode ? majorIncidentFeedEntries().slice(0, 1) : majorIncidentFeedEntries();
        const signature = JSON.stringify({
            theme: state.uiTheme,
            minimum: state.majorIncidentFeed.minimumCredits,
            entries: entries.map(entry => [entry.snapshot.missionId, entry.snapshot.caption, entry.postcode, entry.operational.key, entry.operational.label, entry.credits, Math.floor(entry.ageMs / 60000)])
        });
        const existingTrack = feed.querySelector('.mcms-incident-feed-track');
        const hasRenderedContent = Boolean(existingTrack?.childElementCount);
        if (!force && signature === majorIncidentFeedRenderSignature && hasRenderedContent) {
            scheduleMajorIncidentFeedLayout();
            scheduleMajorIncidentFeedMotion(feed, false, 60);
            return;
        }
        majorIncidentFeedRenderSignature = signature;
        const label = feed.querySelector('.mcms-incident-feed-label');
        const track = feed.querySelector('.mcms-incident-feed-track');
        if (label) label.textContent = majorIncidentThemeLabel();
        if (!track) return;

        feed.classList.toggle('mcms-feed-empty', entries.length === 0);
        feed.classList.remove('mcms-feed-static');
        feed.dataset.mcmsEntryCount = String(entries.length);
        if (!entries.length) {
            track.innerHTML = '<div class="mcms-incident-feed-empty">No qualifying major incidents currently active</div>';
            feed.style.removeProperty('--mcms-incident-feed-duration');
        } else {
            const itemHtml = entries.map(majorIncidentFeedItemHtml).join('');
            const group = `<div class="mcms-incident-feed-group">${itemHtml}</div>`;
            track.innerHTML = state.economyMode ? group : `${group}${group}`;
            scheduleMajorIncidentFeedMotion(feed, true, 70);
        }
        scheduleMajorIncidentFeedLayout();
    }

    function scheduleMajorIncidentFeedRender(delay = 120) {
        runtimeClearTimeout(majorIncidentFeedRenderTimer);
        majorIncidentFeedRenderTimer = runtimeSetTimeout(() => {
            majorIncidentFeedRenderTimer = null;
            renderMajorIncidentFeed();
        }, Math.max(0, Number(delay) || 0));
    }

    function payoutTierForAmount(amount) {
        const value = Math.max(0, Number(amount) || 0);
        if (value >= 100000) return 'elite';
        if (value >= 50000) return 'high';
        if (value >= 25000) return 'major';
        return 'standard';
    }

    function getMissionCaption(marker, missionId) {
        const cached = missionOverlayData.get(missionId) || {};
        const direct = cached.caption ?? marker?.caption ?? marker?.name ?? marker?.options?.title ?? marker?.options?.caption;
        if (direct && String(direct).trim()) {
            const caption = normaliseMissionCaption(direct);
            if (cached.caption !== caption) setMissionOverlayRecord(missionId, { ...cached, caption });
            return caption;
        }
        const panel = getMissionPanelElement(missionId);
        if (panel) {
            const captionNode = panel.querySelector('.map_position_mover[id^="mission_caption_"], .mission_caption, [id^="mission_caption_"]');
            const caption = normaliseMissionCaption(captionNode?.textContent || '');
            if (caption) {
                setMissionOverlayRecord(missionId, { ...cached, caption });
                return caption;
            }
        }
        const iconText = marker?._icon?.title || marker?._icon?.alt || marker?._icon?.getAttribute?.('aria-label');
        const caption = normaliseMissionCaption(iconText || '');
        if (caption) setMissionOverlayRecord(missionId, { ...cached, caption });
        return caption;
    }


    function normaliseMissionPostcode(value) {
        const text = String(value || '').toUpperCase().replace(/\s+/g, ' ').trim();
        const match = text.match(UK_POSTCODE_PATTERN);
        if (!match?.[0]) return '';
        const compact = match[0].replace(/\s+/g, '');
        return compact.length > 3 ? `${compact.slice(0, -3)} ${compact.slice(-3)}` : compact;
    }

    function normaliseMissionCity(value, postcode = '') {
        let text = decodeMissionTextEntities(value).replace(/\s+/g, ' ').trim();
        if (!text) return '';
        const normalisedPostcode = normaliseMissionPostcode(postcode || text);
        if (normalisedPostcode) {
            const compactPattern = normalisedPostcode.replace(/\s+/g, '\\s*');
            try { text = text.replace(new RegExp(`\\b${compactPattern}\\b`, 'iu'), ' '); } catch (err) {}
        }
        text = text.replace(UK_POSTCODE_PATTERN, ' ').replace(/\s+/g, ' ').trim();

        const administrative = text.match(/\b(?:city|borough|district)\s+of\s+([^,;|]+)/iu);
        if (administrative?.[1]) return administrative[1].replace(/\s+/g, ' ').trim();

        const segments = text.split(/[,;|]/u).map(segment => segment.trim()).filter(Boolean);
        const streetPattern = /\b(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|way|close|court|place|pl|terrace|crescent|gardens?|park|square|mews|row|hill|brae|gait|walk|wynd|building|site|airport|station|hospital)\b/iu;
        const numberPattern = /^\d+[A-Z]?\b/iu;
        const candidates = segments.filter(segment => !numberPattern.test(segment) && !streetPattern.test(segment) && !/^uk$/iu.test(segment));
        if (candidates.length) return candidates[candidates.length - 1].replace(/^the\s+/iu, '').trim();
        return '';
    }

    function getMissionAddress(marker, missionId) {
        const cached = missionOverlayData.get(missionId) || {};
        const direct = cached.address ?? marker?.address ?? marker?.mission_address ?? marker?.missionAddress ?? marker?.options?.address ?? marker?.options?.mission_address ?? marker?.options?.missionAddress;
        if (direct && String(direct).trim()) {
            const address = String(direct).replace(/\s+/g, ' ').trim();
            const postcode = normaliseMissionPostcode(address);
            if (cached.address !== address || cached.postcode !== postcode) setMissionOverlayRecord(missionId, { ...cached, address, postcode });
            return address;
        }

        const panel = getMissionPanelElement(missionId);
        const addressNode = document.getElementById(`mission_address_${missionId}`)
            || panel?.querySelector?.('.mission_address, [id^="mission_address_"]')
            || null;
        const address = String(addressNode?.textContent || '').replace(/\s+/g, ' ').trim();
        if (address) {
            const postcode = normaliseMissionPostcode(address);
            setMissionOverlayRecord(missionId, { ...cached, address, postcode });
        }
        return address;
    }

    function vehicleStatusCode(vehicle) {
        if (!vehicle || typeof vehicle !== 'object') return null;
        const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
            .filter(item => item && typeof item === 'object');
        for (const item of containers) {
            const value = Number(item.fms_real ?? item.fmsReal ?? item.fms ?? item.fms_show ?? item.fmsShow);
            if (Number.isFinite(value)) return value;
        }
        return null;
    }

    function personalUnitCommitmentForMission(missionId) {
        const normalisedId = normaliseMissionId(missionId);
        const commitment = normalisedId === null ? null : rebuildMissionCommitmentIndex().get(normalisedId);

        if (!commitment) {
            return {
                total: 0,
                active: 0,
                onScene: 0,
                onWay: 0,
                travelling: 0,
                transporting: 0,
                awaitingPickup: 0,
                requestingDispatch: 0,
                outOfService: 0,
                available: 0,
                unknownStatus: 0,
                markerPresence: false,
                known: vehicleApiReady,
                source: vehicleApiReady ? 'api' : 'unknown'
            };
        }

        return {
            ...commitment,
            markerPresence: false,
            known: true,
            source: vehicleApiReady ? 'api' : 'live'
        };
    }

    function normaliseMissionLiveCurrentValue(value) {
        const parsed = Number(value);
        return Number.isFinite(parsed) && parsed >= 0 && parsed <= 100 ? parsed : null;
    }

    function missionLiveCurrentValueFromMarker(marker) {
        const containers = [marker, marker?.options, marker?.params, marker?.mission, marker?.data, marker?._missionData]
            .filter(item => item && typeof item === 'object');
        for (const item of containers) {
            const value = normaliseMissionLiveCurrentValue(item.live_current_value ?? item.liveCurrentValue ?? item.current_value ?? item.currentValue);
            if (value !== null) return value;
        }
        return null;
    }

    function missionLiveCurrentValueFromDom(missionId) {
        const panel = getMissionPanelElement(missionId);
        if (!panel) return null;
        const candidates = [
            panel,
            ...Array.from(panel.querySelectorAll('[data-live-current-value], [data-live_current_value], [data-current-value], [data-current_value]'))
        ];
        for (const element of candidates) {
            const value = normaliseMissionLiveCurrentValue(
                element.getAttribute?.('data-live-current-value') ??
                element.getAttribute?.('data-live_current_value') ??
                element.getAttribute?.('data-current-value') ??
                element.getAttribute?.('data-current_value')
            );
            if (value !== null) return value;
        }
        return null;
    }

    function resolveMissionLiveCurrentValue(marker, missionId, overlay, now = Date.now()) {
        const overlayValue = normaliseMissionLiveCurrentValue(overlay?.liveCurrentValue);
        const overlayUpdatedAt = Number(overlay?.liveCurrentValueUpdatedAt) || 0;

        // A freshly captured mission payload is authoritative. Prefer it before touching
        // the mission-list DOM, which avoids a subtree query for every active mission.
        if (overlayValue !== null && now - overlayUpdatedAt <= MISSION_PROGRESS_PAGE_REFRESH_MS + 5000) return overlayValue;

        const domValue = missionLiveCurrentValueFromDom(missionId);
        if (domValue !== null) return domValue;
        const markerValue = missionLiveCurrentValueFromMarker(marker);
        if (markerValue !== null) return markerValue;
        return overlayValue;
    }

    function missionSnapshotFromMarker(marker, now = Date.now()) {
        const missionId = missionIdFromMarker(marker);
        if (missionId === null) return null;
        const overlayVersion = missionOverlayVersion(missionId);
        const progressBucket = Math.floor(now / MISSION_SNAPSHOT_REUSE_MS);
        const cachedSnapshot = missionSnapshotCache.get(missionId);
        if (
            cachedSnapshot?.marker === marker &&
            cachedSnapshot.missionRevision === missionRegistryRevision &&
            cachedSnapshot.vehicleRevision === vehicleDataRevision &&
            cachedSnapshot.overlayVersion === overlayVersion &&
            cachedSnapshot.progressBucket === progressBucket
        ) {
            cachedSnapshot.lastUsed = now;
            cachedSnapshot.snapshot.lastSeen = now;
            return cachedSnapshot.snapshot;
        }
        let latLng = null;
        try { latLng = marker.getLatLng?.() || null; } catch (err) {}
        const ownership = missionWatchOwnership(marker, missionId);
        const specialEvent = missionDeveloperEventInfo(marker, missionId);
        const category = missionWatchCategory(marker, missionId, null, specialEvent);
        const unitState = missionPersonalUnitState(marker, missionId);
        const units = {
            ...unitState.commitment,
            markerPresence: Boolean(unitState.hasUnit && Number(unitState.commitment?.total || 0) <= 0)
        };
        const overlay = missionOverlayData.get(missionId) || {};
        const overlayMissingTextKnown = overlay.missingTextKnown === true || Object.prototype.hasOwnProperty.call(overlay, 'missingText');
        const rawMissingText = overlayMissingTextKnown
            ? String(overlay.missingText || '')
            : marker?.missing_text || marker?.missingText || marker?.options?.missing_text || marker?.options?.missingText || '';
        const address = getMissionAddress(marker, missionId);
        const postcode = normaliseMissionPostcode(overlay.postcode || address);
        const area = normaliseMissionCity(overlay.city || address, postcode);
        const liveCurrentValue = resolveMissionLiveCurrentValue(marker, missionId, overlay, now);
        const snapshot = {
            missionId,
            marker,
            caption: getMissionCaption(marker, missionId),
            address,
            postcode,
            city: area,
            area,
            source: ownership,
            ownership,
            category,
            specialEvent,
            missionType: ownership,
            averageCredits: getMissionAverageCredits(marker, missionId),
            qualified: ownership === 'personal' || unitState.hasUnit,
            units,
            createdAt: getMissionCreatedAt(marker, missionId),
            missingText: normaliseMissingRequirementText(rawMissingText),
            patientsCount: Number.isFinite(Number(overlay.patientsCount ?? marker?.patients_count ?? marker?.patientsCount ?? marker?.options?.patients_count)) ? Number(overlay.patientsCount ?? marker?.patients_count ?? marker?.patientsCount ?? marker?.options?.patients_count) : null,
            possiblePatientsCount: Number.isFinite(Number(overlay.possiblePatientsCount ?? marker?.possible_patients_count ?? marker?.possiblePatientsCount ?? marker?.options?.possible_patients_count)) ? Number(overlay.possiblePatientsCount ?? marker?.possible_patients_count ?? marker?.possiblePatientsCount ?? marker?.options?.possible_patients_count) : null,
            prisonersCount: Number.isFinite(Number(overlay.prisonersCount ?? marker?.prisoners_count ?? marker?.prisonersCount ?? marker?.options?.prisoners_count)) ? Number(overlay.prisonersCount ?? marker?.prisoners_count ?? marker?.prisonersCount ?? marker?.options?.prisoners_count) : null,
            possiblePrisonersCount: Number.isFinite(Number(overlay.possiblePrisonersCount ?? marker?.possible_prisoners_count ?? marker?.possiblePrisonersCount ?? marker?.options?.possible_prisoners_count)) ? Number(overlay.possiblePrisonersCount ?? marker?.possible_prisoners_count ?? marker?.possiblePrisonersCount ?? marker?.options?.possible_prisoners_count) : null,
            liveCurrentValue,
            dateEndCalc: Number.isFinite(Number(overlay.dateEndCalc)) ? Number(overlay.dateEndCalc) : null,
            dateEnd: Number.isFinite(Number(overlay.dateEnd)) ? Number(overlay.dateEnd) : null,
            dateNow: Number.isFinite(Number(overlay.dateNow)) ? Number(overlay.dateNow) : null,
            dateNowUpdatedAt: Number.isFinite(Number(overlay.dateNowUpdatedAt)) ? Number(overlay.dateNowUpdatedAt) : null,
            vehicleState: Number.isFinite(Number(overlay.vehicleState ?? marker?.vehicle_state ?? marker?.vehicleState ?? marker?.options?.vehicle_state)) ? Number(overlay.vehicleState ?? marker?.vehicle_state ?? marker?.vehicleState ?? marker?.options?.vehicle_state) : null,
            lat: Number(latLng?.lat),
            lng: Number(latLng?.lng),
            lastSeen: now
        };
        missionSnapshotCache.set(missionId, {
            marker,
            missionRevision: missionRegistryRevision,
            vehicleRevision: vehicleDataRevision,
            overlayVersion: missionOverlayVersion(missionId),
            progressBucket,
            lastUsed: now,
            snapshot
        });
        return snapshot;
    }

    function refreshMissionSnapshots() {
        runtimeClearTimeout(missionSnapshotTimer);
        missionSnapshotTimer = null;
        const now = Date.now();
        const current = new Map();
        const previousSnapshots = liveMissionSnapshots;
        const missionMarkers = getMissionMarkerIndex().markers;
        for (const marker of missionMarkers) {
            const snapshot = missionSnapshotFromMarker(marker, now);
            if (!snapshot) continue;
            updateMissionProgressState(snapshot, now);
            current.set(snapshot.missionId, snapshot);
            missionLifecycleLastSeen.set(snapshot.missionId, now);
            const newlySeen = !knownMissionIds.has(snapshot.missionId);
            knownMissionIds.add(snapshot.missionId);
            if (newlySeen && missionSpawnArmed && state.missionSpawn.enabled) runtimeSetTimeout(() => animateMissionSpawn(snapshot.missionId), 60);
        }

        if (missionSnapshotReady) {
            for (const [missionId, previous] of previousSnapshots.entries()) {
                if (current.has(missionId)) continue;
                if (now - Number(previous.lastSeen || now) > 15000) continue;
                if (!recentCompletedMissions.some(item => item.missionId === missionId && now - item.removedAt < PAYOUT_MATCH_WINDOW_MS)) {
                    recentCompletedMissions.unshift({ ...previous, removedAt: now, matched: false });
                }
            }
        }

        liveMissionSnapshots = current;
        missionSnapshotReady = missionSnapshotReady || current.size > 0;
        if (document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open')) {
            criticalDrawerLastDataSyncAt = Math.max(criticalDrawerLastDataSyncAt, now, missionProgressPageLastSuccessAt, vehicleApiLastFetch, vehicleStatusLastUpdate);
        }

        for (let index = recentCompletedMissions.length - 1; index >= 0; index -= 1) {
            const item = recentCompletedMissions[index];
            if (current.has(item.missionId) || now - item.removedAt > PAYOUT_MATCH_WINDOW_MS) recentCompletedMissions.splice(index, 1);
        }
        if (recentCompletedMissions.length > 30) recentCompletedMissions.length = 30;

        let progressEntriesRemoved = false;
        for (const [missionId, progress] of missionProgressState.entries()) {
            if (current.has(missionId)) continue;
            if (now - Number(progress.lastSeen || now) > MISSION_CACHE_RETENTION_MS) {
                missionProgressState.delete(missionId);
                progressEntriesRemoved = true;
            }
        }

        for (const [missionId, lastSeen] of missionLifecycleLastSeen.entries()) {
            if (current.has(missionId) || now - lastSeen <= MISSION_CACHE_RETENTION_MS) continue;
            missionLifecycleLastSeen.delete(missionId);
            deleteMissionOverlayRecord(missionId);
            knownMissionIds.delete(missionId);
            resourceGapLabels.delete(missionId);
            stuckMissionLabels.delete(missionId);
        }
        if (progressEntriesRemoved) saveMissionProgressState();
        if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(80);
        if (state.transportWatcher) scheduleTransportWatcherRefresh(100);
        refreshVisibleMissionInspector();
        scheduleMajorIncidentFeedRender(0);
    }

    function scheduleMissionSnapshotRefresh(delay = 600) {
        runtimeClearTimeout(missionSnapshotTimer);
        missionSnapshotTimer = null;
        if (runtime.destroyed || document.hidden || !missionSnapshotsNeeded()) return;
        const wait = state.economyMode ? Math.max(1400, Number(delay) || 0) : Math.max(0, Number(delay) || 0);
        missionSnapshotTimer = runtimeSetTimeout(refreshMissionSnapshots, wait);
    }

    function resolvePayoutContext(amount) {
        refreshMissionSnapshots();
        const now = Date.now();
        const value = Math.max(0, Number(amount) || 0);
        const candidates = recentCompletedMissions.filter(item => !item.matched && now - item.removedAt <= PAYOUT_MATCH_WINDOW_MS)
            .filter(item => item.source === 'personal' || item.qualified);
        if (!candidates.length) return { source: 'unknown', caption: '', missionId: null, confidence: 0 };

        let best = null;
        let bestScore = -Infinity;
        for (const item of candidates) {
            const recencyScore = Math.max(0, 35 - ((now - item.removedAt) / 500));
            const sourceScore = item.source === 'personal' || item.qualified ? 18 : -30;
            let creditScore = 5;
            if (Number.isFinite(Number(item.averageCredits)) && Number(item.averageCredits) > 0) {
                const ratio = Math.abs(value - Number(item.averageCredits)) / Math.max(value, Number(item.averageCredits), 1);
                creditScore = Math.max(-20, 70 - (ratio * 100));
            }
            const score = recencyScore + sourceScore + creditScore + (item.caption ? 6 : 0);
            if (score > bestScore) { bestScore = score; best = item; }
        }
        if (!best || bestScore < 20) return { source: 'unknown', caption: '', missionId: null, confidence: 0 };
        best.matched = true;
        return {
            source: best.source,
            caption: best.caption || '',
            missionId: best.missionId,
            confidence: Math.min(1, Math.max(0, bestScore / 120)),
            units: best.units || { total: 0, onScene: 0, travelling: 0 }
        };
    }

    function recordCreditGain(amount, context) {
        const value = Math.max(0, Math.round(Number(amount) || 0));
        if (!value) return;
        const tier = payoutTierForAmount(value);
        const entry = {
            id: `${Date.now()}-${value}-${Math.random().toString(36).slice(2, 7)}`,
            timestamp: Date.now(), amount: value, caption: String(context?.caption || ''),
            source: ['personal', 'alliance'].includes(context?.source) ? context.source : 'unknown', tier
        };
        payoutHistory.unshift(entry);
        if (payoutHistory.length > PAYOUT_HISTORY_LIMIT) payoutHistory.length = PAYOUT_HISTORY_LIMIT;
        savePayoutHistory();

        sessionPerformance.creditsEarned = Math.max(0, Number(sessionPerformance.creditsEarned) || 0) + value;
        sessionPerformance.payoutCount = Math.max(0, Number(sessionPerformance.payoutCount) || 0) + 1;
        if (value >= 10000) sessionPerformance.qualifyingCount = Math.max(0, Number(sessionPerformance.qualifyingCount) || 0) + 1;
        sessionPerformance.largestPayout = Math.max(Number(sessionPerformance.largestPayout) || 0, value);
        if (entry.source === 'personal') sessionPerformance.personalPayouts = Math.max(0, Number(sessionPerformance.personalPayouts) || 0) + 1;
        else if (entry.source === 'alliance') sessionPerformance.alliancePayouts = Math.max(0, Number(sessionPerformance.alliancePayouts) || 0) + 1;
        else sessionPerformance.unknownPayouts = Math.max(0, Number(sessionPerformance.unknownPayouts) || 0) + 1;
        saveSessionPerformance();
        renderOperationalPanels();
    }

    function formatOperationalCompactCredits(value) {
        const amount = Math.max(0, Number(value) || 0);
        if (amount >= 1000000) return `${(amount / 1000000).toFixed(amount >= 10000000 ? 0 : 1)}M`;
        if (amount >= 1000) return `${(amount / 1000).toFixed(amount >= 100000 ? 0 : 1)}K`;
        return Math.round(amount).toLocaleString();
    }

    function formatClockTime(timestamp) {
        try { return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
        catch (err) { return ''; }
    }

    function formatRefreshClockTime(timestamp) {
        try { return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
        catch (err) { return ''; }
    }

    function formatElapsedCompact(ms) {
        const totalHours = Math.max(0, Math.floor(Number(ms) / 3600000));
        const days = Math.floor(totalHours / 24);
        const hours = totalHours % 24;
        return days > 0 ? `${days}D ${hours}H` : `${totalHours}H`;
    }

    function summariseCriticalRequirement(value, maxLength = 82) {
        const text = normaliseMissingRequirementText(value).replace(/\s+/g, ' ').trim();
        if (!text) return '';
        const limit = Math.max(36, Number(maxLength) || 82);
        return text.length > limit ? `${text.slice(0, limit - 1).trimEnd()}…` : text;
    }

    function criticalMissionClearingProgress(snapshot) {
        const remaining = Number(snapshot?.liveCurrentValue);
        if (!Number.isFinite(remaining) || remaining < 0 || remaining >= 100) return null;
        const completion = Math.max(1, Math.min(100, Math.round(100 - remaining)));
        return { remaining, completion };
    }

    function criticalMissionOperationalState(units, snapshot, stuckRecord) {
        const total = Math.max(0, Number(units?.total) || 0);
        const onScene = Math.max(0, Number(units?.onScene) || 0);
        const onWay = Math.max(0, Number(units?.onWay ?? units?.travelling) || 0);
        const transporting = Math.max(0, Number(units?.transporting) || 0);
        const awaitingPickup = Math.max(0, Number(units?.awaitingPickup) || 0);
        const missing = summariseCriticalRequirement(snapshot?.missingText);
        const stuck = Boolean(stuckRecord?.isStuck);
        const clearing = criticalMissionClearingProgress(snapshot);

        if (missing || stuck) {
            return {
                key: 'assistance',
                label: 'VEHICLES NEED ASSISTANCE',
                detail: missing || `No recorded progress for ${formatStuckDuration(stuckRecord.stuckForMs)}`,
                rank: 2
            };
        }

        if (!units?.known) {
            return {
                key: 'syncing',
                label: 'SYNCING VEHICLE DATA',
                detail: units?.markerPresence ? 'Your unit presence is detected · exact vehicle codes are loading' : 'Waiting for current personal vehicle status data',
                rank: 4
            };
        }

        if (clearing && total > 0 && onScene > 0) {
            const respondingDetail = onWay > 0 ? ` · ${onWay} still responding` : '';
            return {
                key: 'clearing',
                label: 'MISSION CLEARING',
                detail: `${clearing.completion}% complete · ${onScene} on scene${respondingDetail}`,
                rank: -1,
                progress: clearing.completion
            };
        }

        if (onScene <= 0 && onWay <= 0) {
            const auxiliary = transporting + awaitingPickup;
            return {
                key: 'no-scene',
                label: 'NO VEHICLES AT SCENE',
                detail: auxiliary > 0 ? `${auxiliary} unit${auxiliary === 1 ? '' : 's'} occupied with transport activity` : 'Immediate dispatch attention required',
                rank: 3
            };
        }

        if (onWay > 0) {
            return {
                key: 'enroute',
                label: 'VEHICLES ON WAY',
                detail: `${onWay} responding · ${onScene} already on scene`,
                rank: 1
            };
        }

        return {
            key: 'on-scene',
            label: 'VEHICLES ON SCENE',
            detail: `${onScene} vehicle${onScene === 1 ? '' : 's'} operating at mission`,
            rank: 0
        };
    }

    function criticalMissionStableData(marker, missionId, snapshot, ownership, category, specialEvent) {
        const overlay = missionOverlayData.get(missionId) || {};
        const rawCaption = snapshot?.caption || overlay.caption || getMissionCaption(marker, missionId) || `Mission ${missionId}`;
        const rawAddress = snapshot?.address || overlay.address || getMissionAddress(marker, missionId) || '';
        const rawValue = parseCreditValue(snapshot?.averageCredits) ?? parseCreditValue(overlay.averageCredits) ?? getMissionAverageCredits(marker, missionId);
        let lat = Number(snapshot?.lat);
        let lng = Number(snapshot?.lng);
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
            try {
                const latLng = marker?.getLatLng?.();
                lat = Number(latLng?.lat);
                lng = Number(latLng?.lng);
            } catch (err) {}
        }
        const signature = [rawCaption, rawAddress, rawValue ?? '', ownership, category, specialEvent?.label || '', lat, lng].join('|');
        const cached = criticalMissionStableCache.get(missionId);
        if (cached?.signature === signature) {
            cached.lastSeen = Date.now();
            return cached.data;
        }
        const address = String(rawAddress || '').replace(/\s+/g, ' ').trim();
        const postcode = normaliseMissionPostcode(snapshot?.postcode || overlay.postcode || address);
        const area = normaliseMissionCity(snapshot?.area || snapshot?.city || overlay.city || address, postcode);
        const data = {
            caption: normaliseMissionCaption(rawCaption),
            address,
            postcode,
            area,
            averageCredits: rawValue,
            lat,
            lng
        };
        criticalMissionStableCache.set(missionId, { signature, data, lastSeen: Date.now() });
        return data;
    }

    function getCriticalMissionEntries(minAgeMs = CRITICAL_VIEW_MIN_AGE_MS, missionTypes = ['personal']) {
        const requestedOwnership = Array.isArray(missionTypes) ? missionTypes : ['personal'];
        const allowedOwnership = new Set(requestedOwnership.filter(type => CRITICAL_OWNERSHIP_KEYS.includes(type)));
        if (!allowedOwnership.size) allowedOwnership.add('personal');
        const now = Date.now();
        const entries = [];
        const includedMissionIds = new Set();
        const markerIndex = getMissionMarkerIndex();
        const markerById = markerIndex.byId;

        const appendEntry = (marker, missionId, snapshotOverride = null) => {
            if (missionId === null || includedMissionIds.has(missionId)) return;
            const snapshot = snapshotOverride || liveMissionSnapshots.get(missionId) || (marker ? missionSnapshotFromMarker(marker, now) : null) || {};
            const ownership = missionWatchOwnership(marker, missionId, snapshot);
            if (!allowedOwnership.has(ownership)) return;
            const specialEvent = snapshot?.specialEvent?.active ? snapshot.specialEvent : missionDeveloperEventInfo(marker, missionId, snapshot);
            const category = missionWatchCategory(marker, missionId, snapshot, specialEvent);
            const createdAt = Number(snapshot?.createdAt) || Number(getMissionCreatedAt(marker, missionId));
            const missionAge = Number.isFinite(createdAt) && createdAt > 0 ? Math.max(0, now - createdAt) : null;
            if (Number.isFinite(Number(minAgeMs)) && Number(minAgeMs) > 0 && (!Number.isFinite(missionAge) || missionAge < Number(minAgeMs))) return;
            const severity = Number.isFinite(missionAge)
                ? missionAgeSeverity(missionAge)
                : { rank: -1, label: 'AGE UNKNOWN', className: 'mcms-age-unknown' };
            const exactUnits = personalUnitCommitmentForMission(missionId);
            const unitState = missionPersonalUnitState(marker, missionId);
            const units = {
                ...exactUnits,
                markerPresence: Boolean(exactUnits.markerPresence || (!exactUnits.known && unitState.hasUnit))
            };
            if (!units.known && units.markerPresence && units.total <= 0) units.total = 1;
            const stuckRecord = missionStuckRecord(missionId, now);
            const operationalState = criticalMissionOperationalState(units, snapshot, stuckRecord);
            const stable = criticalMissionStableData(marker, missionId, snapshot, ownership, category, specialEvent);
            const valueDetails = criticalMissionValueDetails({ missionId, marker, snapshot, averageCredits: stable.averageCredits });
            const eligibleForCredits = ownership === 'personal' || units.active > 0 || units.markerPresence;
            entries.push({
                missionId,
                marker,
                caption: stable.caption,
                address: stable.address,
                postcode: stable.postcode,
                city: stable.area,
                area: stable.area,
                lat: stable.lat,
                lng: stable.lng,
                distanceMi: null,
                missionAge,
                severity,
                units,
                snapshot,
                averageCredits: stable.averageCredits,
                valueDetails,
                ownership,
                category,
                missionType: ownership,
                specialEvent,
                eligibleForCredits,
                stuckRecord,
                operationalState,
                dataQuality: {
                    ageKnown: Number.isFinite(missionAge),
                    unitsKnown: Boolean(units.known),
                    valueKnown: valueDetails.value !== null,
                    locationKnown: Number.isFinite(stable.lat) && Number.isFinite(stable.lng),
                    areaKnown: Boolean(stable.area || stable.postcode)
                }
            });
            includedMissionIds.add(missionId);
        };

        for (const [missionId, marker] of markerById.entries()) appendEntry(marker, missionId);
        for (const [missionId, snapshot] of liveMissionSnapshots.entries()) {
            if (includedMissionIds.has(missionId)) continue;
            appendEntry(markerById.get(missionId) || snapshot?.marker || null, missionId, snapshot);
        }

        const activeIds = new Set(entries.map(entry => entry.missionId));
        for (const [missionId, cached] of criticalMissionStableCache.entries()) {
            if (!activeIds.has(missionId) && now - Number(cached?.lastSeen || now) > MISSION_CACHE_RETENTION_MS) criticalMissionStableCache.delete(missionId);
        }

        return entries.sort((a, b) => {
            const aAge = Number.isFinite(a.missionAge) ? a.missionAge : Number.NEGATIVE_INFINITY;
            const bAge = Number.isFinite(b.missionAge) ? b.missionAge : Number.NEGATIVE_INFINITY;
            return bAge - aAge || a.caption.localeCompare(b.caption) || String(a.missionId).localeCompare(String(b.missionId), undefined, { numeric: true });
        });
    }

    function selectedCriticalAgeFilter() {
        const selected = String(state.missionAgeWatch?.ageFilter || '8h');
        if (CRITICAL_AGE_FILTER_KEYS.includes(selected)) return selected;
        state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ageFilter: '8h' };
        return '8h';
    }

    function criticalAgeFilterDefinition(key = selectedCriticalAgeFilter()) {
        return CRITICAL_AGE_FILTERS[key] || CRITICAL_AGE_FILTERS['8h'];
    }

    function selectedCriticalSortMode() {
        const selected = String(state.missionAgeWatch?.sortMode || 'age');
        if (CRITICAL_SORT_KEYS.includes(selected)) return selected;
        state.missionAgeWatch = { ...(state.missionAgeWatch || {}), sortMode: 'age' };
        return 'age';
    }

    function selectedCriticalOwnershipFilter() {
        const selected = String(state.missionAgeWatch?.ownershipFilter || 'personal');
        return CRITICAL_OWNERSHIP_FILTER_KEYS.includes(selected) ? selected : 'personal';
    }

    function selectedCriticalCategoryFilter() {
        const selected = String(state.missionAgeWatch?.categoryFilter || 'all');
        return CRITICAL_CATEGORY_FILTER_KEYS.includes(selected) ? selected : 'all';
    }

    function selectedCriticalPrimaryStatus() {
        const selected = String(state.missionAgeWatch?.primaryStatus || 'all');
        return CRITICAL_PRIMARY_STATUS_KEYS.includes(selected) ? selected : 'all';
    }

    function selectedCriticalValueMode() {
        const selected = String(state.missionAgeWatch?.valueMode || 'total');
        return CRITICAL_VALUE_MODE_KEYS.includes(selected) ? selected : 'total';
    }

    function selectedCriticalDistanceOrigin() {
        const selected = String(state.missionAgeWatch?.distanceOrigin || 'live');
        let valid = selected === 'live';
        if (selected === 'locked') {
            const locked = state.missionAgeWatch?.lockedOrigin;
            valid = Boolean(locked && Number.isFinite(Number(locked.lat)) && Number.isFinite(Number(locked.lng)));
        } else if (selected.startsWith('quick:')) {
            const id = selected.slice(6);
            valid = QUICK_PLACES.some(place => place.id === id);
        } else if (selected.startsWith('bookmark:')) {
            const index = Number(selected.slice(9));
            const bookmark = state.bookmarks?.[index];
            valid = Boolean(bookmark && Number.isFinite(Number(bookmark.lat)) && Number.isFinite(Number(bookmark.lng)));
        }
        if (valid) return selected;
        state.missionAgeWatch = { ...(state.missionAgeWatch || {}), distanceOrigin: 'live' };
        return 'live';
    }

    function criticalDistanceOriginOptions() {
        const options = [{ key: 'live', label: 'Live map centre' }];
        const locked = state.missionAgeWatch?.lockedOrigin;
        if (locked && Number.isFinite(Number(locked.lat)) && Number.isFinite(Number(locked.lng))) options.push({ key: 'locked', label: locked.label || 'Locked centre' });
        for (const place of QUICK_PLACES) options.push({ key: `quick:${place.id}`, label: place.name });
        state.bookmarks.forEach((bookmark, index) => {
            if (bookmark && Number.isFinite(Number(bookmark.lat)) && Number.isFinite(Number(bookmark.lng))) options.push({ key: `bookmark:${index}`, label: bookmark.name || `Bookmark ${index + 1}` });
        });
        return options;
    }

    function criticalMissionDistanceReference() {
        const mode = selectedCriticalDistanceOrigin();
        const map = findLeafletMapInstance(false);
        if (mode === 'locked') {
            const locked = state.missionAgeWatch?.lockedOrigin;
            if (locked && Number.isFinite(Number(locked.lat)) && Number.isFinite(Number(locked.lng))) return { lat: Number(locked.lat), lng: Number(locked.lng), map, label: locked.label || 'Locked centre' };
        }
        if (mode.startsWith('quick:')) {
            const id = mode.slice(6);
            const place = QUICK_PLACES.find(item => item.id === id);
            if (place) return { lat: Number(place.lat), lng: Number(place.lng), map, label: place.name };
        }
        if (mode.startsWith('bookmark:')) {
            const index = Number(mode.slice(9));
            const bookmark = state.bookmarks[index];
            if (bookmark && Number.isFinite(Number(bookmark.lat)) && Number.isFinite(Number(bookmark.lng))) return { lat: Number(bookmark.lat), lng: Number(bookmark.lng), map, label: bookmark.name || `Bookmark ${index + 1}` };
        }
        if (!map || typeof map.getCenter !== 'function') return null;
        try {
            const centre = map.getCenter();
            const lat = Number(centre?.lat);
            const lng = Number(centre?.lng);
            return Number.isFinite(lat) && Number.isFinite(lng) ? { lat, lng, map, label: 'Live map centre' } : null;
        } catch (err) { return null; }
    }

    function lockCriticalDistanceOrigin() {
        const map = findLeafletMapInstance(false);
        if (!map?.getCenter) return false;
        try {
            const centre = map.getCenter();
            const lat = Number(centre?.lat);
            const lng = Number(centre?.lng);
            if (!Number.isFinite(lat) || !Number.isFinite(lng)) return false;
            state.missionAgeWatch = {
                ...(state.missionAgeWatch || {}),
                distanceOrigin: 'locked',
                lockedOrigin: { lat, lng, label: `Locked ${lat.toFixed(3)}, ${lng.toFixed(3)}` }
            };
            saveState();
            return true;
        } catch (err) { return false; }
    }

    function criticalEntryDistanceMiles(entry, reference) {
        if (!reference) return null;
        const lat = Number(entry?.lat ?? entry?.snapshot?.lat);
        const lng = Number(entry?.lng ?? entry?.snapshot?.lng);
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
        try {
            if (typeof reference.map?.distance === 'function') {
                const metres = Number(reference.map.distance([reference.lat, reference.lng], [lat, lng]));
                if (Number.isFinite(metres)) return Math.max(0, metres / 1609.344);
            }
        } catch (err) {}
        return haversineMiles(reference, { lat, lng });
    }

    function formatCriticalDistance(distanceMi) {
        if (distanceMi === null || distanceMi === undefined || distanceMi === '') return '';
        const distance = Number(distanceMi);
        if (!Number.isFinite(distance)) return '';
        if (distance < 0.1) return '<0.1 MI';
        if (distance < 10) return `${distance.toFixed(1)} MI`;
        return `${Math.round(distance).toLocaleString('en-GB')} MI`;
    }

    function criticalEntryPrimaryStatus(entry) {
        if (criticalEntryNeedsAssistance(entry)) return 'assistance';
        if (entry?.operationalState?.key === 'clearing') return 'clearing';
        if (!entry?.units?.known) return 'syncing';
        if (Math.max(0, Number(entry?.units?.onScene) || 0) <= 0) return 'no-scene';
        return 'on-scene';
    }

    function criticalEntryHasMyUnits(entry) {
        return Math.max(0, Number(entry?.units?.active) || 0) > 0 || Boolean(entry?.units?.markerPresence);
    }

    function criticalEntryMatchesDimension(entry, dimension) {
        if (dimension === 'age') {
            const definition = criticalAgeFilterDefinition();
            if (!Number.isFinite(entry?.missionAge)) return definition.minAgeMs === 0;
            return entry.missionAge >= definition.minAgeMs;
        }
        if (dimension === 'ownership') {
            const selected = selectedCriticalOwnershipFilter();
            return selected === 'all' || entry?.ownership === selected;
        }
        if (dimension === 'category') {
            const selected = selectedCriticalCategoryFilter();
            return selected === 'all' || entry?.category === selected;
        }
        if (dimension === 'status') {
            const selected = selectedCriticalPrimaryStatus();
            const actual = criticalEntryPrimaryStatus(entry);
            if (selected === 'all') return true;
            if (selected === 'attention') return actual === 'no-scene' || actual === 'assistance';
            return actual === selected;
        }
        if (dimension === 'onway') return !state.missionAgeWatch?.hasVehiclesOnWay || Math.max(0, Number(entry?.units?.onWay ?? entry?.units?.travelling) || 0) > 0;
        if (dimension === 'myunits') return !state.missionAgeWatch?.onlyMyUnits || criticalEntryHasMyUnits(entry);
        return true;
    }

    function criticalFilterEntries(entries, omitDimensions = []) {
        const omitted = new Set(Array.isArray(omitDimensions) ? omitDimensions : [omitDimensions]);
        return entries.filter(entry => ['age', 'ownership', 'category', 'status', 'onway', 'myunits'].every(dimension => omitted.has(dimension) || criticalEntryMatchesDimension(entry, dimension)));
    }

    function sortCriticalEntries(entries) {
        const definition = criticalAgeFilterDefinition();
        const reference = criticalMissionDistanceReference();
        const sortMode = selectedCriticalSortMode();
        const withDistance = entries.map(entry => ({ ...entry, distanceMi: criticalEntryDistanceMiles(entry, reference), distanceOriginLabel: reference?.label || '' }));
        return withDistance.sort((a, b) => {
            let primaryDifference = 0;
            if (sortMode === 'closest' || sortMode === 'furthest') {
                const aKnown = Number.isFinite(a.distanceMi);
                const bKnown = Number.isFinite(b.distanceMi);
                if (aKnown !== bKnown) return aKnown ? -1 : 1;
                if (aKnown && bKnown) primaryDifference = sortMode === 'closest' ? Number(a.distanceMi) - Number(b.distanceMi) : Number(b.distanceMi) - Number(a.distanceMi);
            } else {
                const aKnown = Number.isFinite(a.missionAge);
                const bKnown = Number.isFinite(b.missionAge);
                if (aKnown !== bKnown) return aKnown ? -1 : 1;
                if (aKnown && bKnown) primaryDifference = definition.sort === 'newest' ? a.missionAge - b.missionAge : b.missionAge - a.missionAge;
            }
            const aAge = Number.isFinite(a.missionAge) ? a.missionAge : Number.NEGATIVE_INFINITY;
            const bAge = Number.isFinite(b.missionAge) ? b.missionAge : Number.NEGATIVE_INFINITY;
            return primaryDifference || (definition.sort === 'newest' ? aAge - bAge : bAge - aAge) || a.caption.localeCompare(b.caption) || String(a.missionId).localeCompare(String(b.missionId), undefined, { numeric: true });
        });
    }

    function qualifiedAllianceMissionCount() {
        let count = 0;
        if (missionSnapshotReady) {
            for (const snapshot of liveMissionSnapshots.values()) {
                if (snapshot?.ownership === 'alliance' && snapshot.qualified) count += 1;
            }
            return count;
        }
        for (const marker of getMissionMarkerIndex().markers) {
            const missionId = missionIdFromMarker(marker);
            if (missionId !== null && isAllianceMissionLayer(marker, missionId) && missionHasPersonalUnit(marker, missionId)) count += 1;
        }
        return count;
    }

    function operationalUiIsVisible() {
        const panel = document.getElementById(SCRIPT.panelId);
        const opsPanelVisible = Boolean(panel?.classList?.contains('mcms-open') && state.activeTab === 'ops');
        const drawerVisible = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
        const vehicleStatusVisible = Boolean(document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open'));
        return opsPanelVisible || drawerVisible || vehicleStatusVisible;
    }

    function scheduleOperationalPanelsRender(delay = 500, force = false) {
        runtimeClearTimeout(opsRefreshTimer);
        if (!force && !operationalUiIsVisible()) return;
        const elapsed = Date.now() - operationalPanelsLastRender;
        const minimumGap = state.economyMode ? 1200 : 750;
        const wait = Math.max(Number(delay) || 0, elapsed < minimumGap ? minimumGap - elapsed : 0);
        opsRefreshTimer = runtimeSetTimeout(() => renderOperationalPanels(force), wait);
    }

    function renderOperationalPanels(force = false, criticalRenderOptions = null) {
        runtimeClearTimeout(opsRefreshTimer);
        opsRefreshTimer = null;
        const panel = document.getElementById(SCRIPT.panelId);
        const opsPanelVisible = Boolean(panel?.classList?.contains('mcms-open') && state.activeTab === 'ops');
        const criticalDrawerVisible = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
        const vehicleStatusVisible = Boolean(document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open'));
        if (!force && !opsPanelVisible && !criticalDrawerVisible && !vehicleStatusVisible) return;
        operationalPanelsLastRender = Date.now();

        if (vehicleStatusVisible) renderVehicleCodeStatus();
        if (!opsPanelVisible && !criticalDrawerVisible) return;

        const criticalEntries = getCriticalMissionEntries(CRITICAL_VIEW_MIN_AGE_MS);
        const qualifiedAlliance = opsPanelVisible ? qualifiedAllianceMissionCount() : 0;
        const summarySignature = JSON.stringify({
            credits: sessionPerformance.creditsEarned,
            qualifying: sessionPerformance.qualifyingCount,
            largest: sessionPerformance.largestPayout,
            payouts: sessionPerformance.payoutCount,
            critical: criticalEntries.map(entry => [entry.missionId, entry.severity.rank, Math.floor(entry.missionAge / 60000), entry.units.total]),
            qualifiedAlliance,
            history: payoutHistory.map(entry => [entry.id, entry.amount, entry.timestamp])
        });

        if (opsPanelVisible && panel) {
            const session = panel.querySelector('[data-ops-session]');
            if (session) {
                const html = `
                    <div class="mcms-ops-session-grid">
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Credits earned</span><strong class="mcms-ops-stat-value">${escapeHtml(formatOperationalCompactCredits(sessionPerformance.creditsEarned))}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">10K+ completions</span><strong class="mcms-ops-stat-value">${Number(sessionPerformance.qualifyingCount) || 0}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Largest payout</span><strong class="mcms-ops-stat-value">${escapeHtml(formatOperationalCompactCredits(sessionPerformance.largestPayout))}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Aged missions</span><strong class="mcms-ops-stat-value">${criticalEntries.length}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label"><span class="mcms-alliance-text">Alliance</span> qualified</span><strong class="mcms-ops-stat-value">${qualifiedAlliance}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Payout events</span><strong class="mcms-ops-stat-value">${Number(sessionPerformance.payoutCount) || 0}</strong></div>
                    </div>`;
                setInnerHtmlIfChanged(session, html, `session:${summarySignature}`);
            }

            const criticalPreview = panel.querySelector('[data-ops-critical-preview]');
            if (criticalPreview) {
                const entries = criticalEntries.slice(0, 4);
                const html = entries.length ? entries.map(entry => `
                    <div class="mcms-ops-entry">
                        <div class="mcms-ops-entry-main"><span class="mcms-ops-entry-title">${escapeHtml(entry.caption)}</span><span class="mcms-ops-entry-meta">${escapeHtml(entry.severity.label)} · ${escapeHtml(formatElapsedCompact(entry.missionAge))} old · ${entry.units.total} unit${entry.units.total === 1 ? '' : 's'}</span></div>
                        <button class="mcms-small-btn" type="button" data-action="critical-go" data-mission-id="${escapeHtml(entry.missionId)}">GO</button>
                    </div>`).join('') : '<div class="mcms-empty-state">No personal missions are currently 8 hours old or more.</div>';
                setInnerHtmlIfChanged(criticalPreview, html, `critical:${criticalEntries.map(entry => `${entry.missionId}:${Math.floor(entry.missionAge / 60000)}:${entry.units.total}`).join('|')}`);
            }

            const history = panel.querySelector('[data-ops-history]');
            if (history) {
                const historyEntryHtml = entry => `
                    <div class="mcms-ops-entry">
                        <div class="mcms-ops-entry-main"><span class="mcms-ops-entry-title">${allianceAwareHtml(entry.caption || (entry.source === 'alliance' ? 'Alliance mission payout' : entry.source === 'personal' ? 'Personal mission payout' : 'Credit award'))}</span><span class="mcms-ops-entry-meta">${escapeHtml(formatClockTime(entry.timestamp))} · <span class="${entry.source === 'alliance' ? 'mcms-alliance-text' : ''}">${escapeHtml(entry.source.toUpperCase())}</span> · ${escapeHtml(entry.tier.toUpperCase())}</span></div>
                        <strong class="mcms-ops-entry-value">+${escapeHtml(formatOperationalCompactCredits(entry.amount))}</strong>
                    </div>`;
                let html = '<div class="mcms-empty-state">No payout events recorded in this browser yet.</div>';
                if (payoutHistory.length) {
                    const latest = payoutHistory.slice(0, 3);
                    const older = payoutHistory.slice(3, PAYOUT_HISTORY_LIMIT);
                    html = `
                        <div class="mcms-history-latest">${latest.map(historyEntryHtml).join('')}</div>
                        ${older.length ? `<details class="mcms-history-older" data-ops-history-older>
                            <summary>Earlier payouts (${older.length})</summary>
                            <div class="mcms-history-scroll">${older.map(historyEntryHtml).join('')}</div>
                        </details>` : ''}`;
                }
                setInnerHtmlIfChanged(history, html, `history:${payoutHistory.map(entry => entry.id).join('|')}`);
            }
        }
        // Keep Mission Age Watch independent from the personal-only Ops preview.
        // The drawer rebuilds its full Personal/Event/Alliance dataset only when open.
        if (criticalDrawerVisible) renderCriticalDrawer(null, criticalRenderOptions || {});
    }

    function vehicleCodeStatusSnapshot() {
        const counts = new Map();
        const seen = new Set();
        let total = 0;

        for (const vehicle of getPersonalVehicleRecords()) {
            const vehicleId = vehicleRecordId(vehicle) || `anonymous:${seen.size}`;
            if (seen.has(vehicleId)) continue;
            seen.add(vehicleId);

            const code = vehicleStatusCode(vehicle);
            if (!Number.isInteger(code)) continue;
            counts.set(code, (counts.get(code) || 0) + 1);
            total += 1;
        }

        const rows = VEHICLE_CODE_STATUS_DEFINITIONS.map(definition => ({
            ...definition,
            count: counts.get(definition.code) || 0,
            recognised: true
        }));

        const unknownCodes = Array.from(counts.keys())
            .filter(code => !VEHICLE_CODE_STATUS_BY_CODE.has(code))
            .sort((a, b) => a - b);

        for (const code of unknownCodes) {
            rows.push({ code, label: 'Unrecognised Game Status', count: counts.get(code) || 0, recognised: false });
        }

        return {
            rows,
            total,
            complete: vehicleApiReady,
            updatedAt: vehicleStatusLastUpdate || vehicleApiLastFetch || 0
        };
    }

    function createVehicleCodeStatus() {
        let drawer = document.getElementById(SCRIPT.vehicleStatusId);
        if (drawer) return drawer;

        drawer = document.createElement('aside');
        drawer.id = SCRIPT.vehicleStatusId;
        drawer.setAttribute('aria-label', 'Vehicle Code Status');
        drawer.setAttribute('aria-hidden', 'true');
        drawer.innerHTML = `
            <div class="mcms-vcs-head">
                <div class="mcms-vcs-heading">
                    <strong class="mcms-vcs-title">VEHICLE CODE STATUS</strong>
                    <span class="mcms-vcs-subtitle">Live overview of your personal fleet</span>
                </div>
                <div class="mcms-vcs-head-actions">
                    <button class="mcms-vcs-refresh" type="button" title="Refresh vehicle data" aria-label="Refresh vehicle data">↻</button>
                    <button class="mcms-vcs-close" type="button" title="Close Vehicle Code Status" aria-label="Close Vehicle Code Status">×</button>
                </div>
            </div>
            <div class="mcms-vcs-meta">
                <span data-vcs-source>Loading fleet…</span>
                <span data-vcs-updated>Updated —</span>
            </div>
            <div class="mcms-vcs-table" role="table" aria-label="Vehicle status-code counts">
                <div class="mcms-vcs-table-row mcms-vcs-table-head" role="row">
                    <span role="columnheader">Code</span>
                    <span role="columnheader">Status</span>
                    <span role="columnheader">Vehicles</span>
                </div>
                <div class="mcms-vcs-table-body" data-vcs-body></div>
                <div class="mcms-vcs-table-row mcms-vcs-total-row" role="row">
                    <strong role="cell">Total</strong>
                    <span role="cell">Personal fleet</span>
                    <strong role="cell" data-vcs-total>0</strong>
                </div>
            </div>
            <div class="mcms-vcs-footnote">Codes are read from MissionChief's live <code>fms_real</code> vehicle status. Zero-count codes remain visible so out-of-service units are never hidden.</div>`;

        drawer.addEventListener('click', event => {
            event.stopPropagation();
            if (closestEventTarget(event, '.mcms-vcs-close')) {
                closeVehicleCodeStatus();
                return;
            }
            if (closestEventTarget(event, '.mcms-vcs-refresh')) refreshVehicleCodeStatus(true);
        });
        ['dblclick', 'mousedown', 'mouseup', 'mousemove', 'wheel', 'contextmenu', 'touchstart', 'touchmove', 'touchend'].forEach(eventName => {
            drawer.addEventListener(eventName, event => event.stopPropagation(), { passive: false });
        });
        document.body.appendChild(drawer);
        return drawer;
    }

    function renderVehicleCodeStatus() {
        const drawer = document.getElementById(SCRIPT.vehicleStatusId);
        if (!drawer || !drawer.classList.contains('mcms-open')) return;

        const snapshot = vehicleCodeStatusSnapshot();
        const body = drawer.querySelector('[data-vcs-body]');
        const total = drawer.querySelector('[data-vcs-total]');
        const source = drawer.querySelector('[data-vcs-source]');
        const updated = drawer.querySelector('[data-vcs-updated]');
        if (!body || !total || !source || !updated) return;

        const html = snapshot.rows.map(row => `
            <div class="mcms-vcs-table-row mcms-vcs-status-row${row.recognised ? '' : ' mcms-vcs-unknown'}" role="row" data-code="${escapeHtml(row.code)}">
                <span class="mcms-vcs-code" role="cell" data-code="${escapeHtml(row.code)}">${escapeHtml(row.code)}</span>
                <span class="mcms-vcs-status" role="cell">${escapeHtml(row.label)}</span>
                <strong class="mcms-vcs-count" role="cell">${Number(row.count).toLocaleString()}</strong>
            </div>`).join('');
        const signature = `vehicle-status:${snapshot.complete}:${snapshot.updatedAt}:${snapshot.rows.map(row => `${row.code}:${row.count}`).join('|')}`;
        setInnerHtmlIfChanged(body, html, signature);
        total.textContent = snapshot.total.toLocaleString();
        source.textContent = snapshot.complete ? 'Complete personal fleet' : 'Loading complete fleet · visible vehicles shown';
        updated.textContent = snapshot.updatedAt ? `Updated ${formatClockTime(snapshot.updatedAt)}` : 'Updated —';
        drawer.classList.toggle('mcms-vcs-loading', !snapshot.complete);
    }

    function refreshVehicleCodeStatus(force = false) {
        const drawer = createVehicleCodeStatus();
        drawer.classList.add('mcms-vcs-loading');
        const refreshButton = drawer.querySelector('.mcms-vcs-refresh');
        if (refreshButton) refreshButton.disabled = true;
        return refreshPersonalVehicleData(force)
            .then(success => {
                renderVehicleCodeStatus();
                if (force) showToast(success ? 'Vehicle Code Status refreshed' : 'Vehicle status refresh failed');
                return success;
            })
            .finally(() => {
                drawer.classList.remove('mcms-vcs-loading');
                if (refreshButton) refreshButton.disabled = false;
            });
    }

    function closeVehicleCodeStatus() {
        const drawer = document.getElementById(SCRIPT.vehicleStatusId);
        if (!drawer) return;
        closeCriticalViewControls(drawer);
        drawer.classList.remove('mcms-open');
        drawer.setAttribute('aria-hidden', 'true');
        updateUI();
    }

    function toggleVehicleCodeStatus() {
        const drawer = createVehicleCodeStatus();
        const opening = !drawer.classList.contains('mcms-open');
        if (!opening) {
            closeVehicleCodeStatus();
            return;
        }

        const criticalDrawer = document.getElementById(SCRIPT.criticalDrawerId);
        criticalDrawer?.classList.remove('mcms-open');
        criticalDrawer?.setAttribute('aria-hidden', 'true');
        drawer.classList.add('mcms-open');
        drawer.setAttribute('aria-hidden', 'false');
        updateUI();
        renderVehicleCodeStatus();
        refreshVehicleCodeStatus(false);
        runtimeSetTimeout(() => drawer.querySelector('.mcms-vcs-close')?.focus?.(), 0);
    }

    function elementDockRect(element) {
        if (!element?.isConnected || !isVisible(element)) return null;
        let rect;
        try { rect = element.getBoundingClientRect(); } catch (err) { return null; }
        if (!rect || rect.width < 280 || rect.height < 180) return null;
        return rect;
    }

    function findMissionListDockRect() {
        if (mobileModeActive) return null;
        const viewportWidth = Math.max(1, Number(pageWindow.innerWidth) || document.documentElement.clientWidth || 1);
        const viewportHeight = Math.max(1, Number(pageWindow.innerHeight) || document.documentElement.clientHeight || 1);
        const mapElement = getLargestLeafletMap();
        const mapRect = elementDockRect(mapElement);
        const minimumLeft = mapRect ? mapRect.right - 48 : viewportWidth * 0.38;
        const preferredSelectors = [
            '#mission_list', '#missions', '#mission-list', '#missions-panel', '#mission_panel',
            '#mission_list_wrapper', '#mission-list-wrapper', '.mission-list', '.missions-list',
            '.mission-sidebar', '.missionSideBar', '.missionSideBarList', '.mission-list-container',
            '[data-mission-list]', '[class*="mission-list"]'
        ];
        const candidates = new Set();
        for (const selector of preferredSelectors) {
            try { document.querySelectorAll(selector).forEach(element => candidates.add(element)); } catch (err) {}
        }

        const missionLinks = Array.from(document.querySelectorAll('a[href^="/missions/"], a[href*="/missions/"]'))
            .filter(link => {
                if (!link?.isConnected || !isVisible(link)) return false;
                try { return link.getBoundingClientRect().left >= minimumLeft; } catch (err) { return false; }
            })
            .slice(0, 32);
        const missionRows = Array.from(document.querySelectorAll('.missionSideBarEntry, .mission-side-bar-entry, [data-mission-id], [id^="mission_"]'))
            .filter(row => {
                if (!row?.isConnected || !isVisible(row) || row.closest?.(`#${SCRIPT.criticalDrawerId}`)) return false;
                try {
                    const rect = row.getBoundingClientRect();
                    return rect.width >= 250 && rect.height >= 30 && rect.left >= minimumLeft;
                } catch (err) { return false; }
            })
            .slice(0, 80);
        for (const seed of [...missionLinks, ...missionRows]) {
            let node = seed.parentElement;
            for (let depth = 0; node && node !== document.body && depth < 10; depth += 1, node = node.parentElement) candidates.add(node);
        }

        let best = null;
        let bestScore = -Infinity;
        for (const element of candidates) {
            const rect = elementDockRect(element);
            if (!rect || rect.left < minimumLeft || rect.right < viewportWidth * 0.68) continue;
            if (rect.top > viewportHeight - 160 || rect.bottom < 220) continue;
            let linkCount = 0;
            let rowCount = 0;
            try {
                linkCount = element.querySelectorAll('a[href^="/missions/"], a[href*="/missions/"]').length;
                rowCount = element.querySelectorAll('.missionSideBarEntry, .mission-side-bar-entry, [data-mission-id], [id^="mission_"]').length;
            } catch (err) {}
            const missionItemCount = Math.max(linkCount, rowCount);
            if (missionItemCount < 2) continue;
            const id = String(element.id || '').toLowerCase();
            const classes = String(element.className || '').toLowerCase();
            const identityBonus = id === 'mission_list' ? 6000 : id === 'missions' ? 4500 : /mission[-_ ]?list|mission[-_ ]?sidebar/.test(`${id} ${classes}`) ? 2600 : 0;
            const widthPenalty = rect.width > viewportWidth * 0.72 ? (rect.width - viewportWidth * 0.72) * 8 : 0;
            const scrollBonus = element.scrollHeight > element.clientHeight + 80 ? 900 : 0;
            const rightEdgeBonus = rect.right >= viewportWidth - 40 ? 500 : 0;
            const score = identityBonus + Math.min(missionItemCount, 100) * 120 + Math.min(rect.height, viewportHeight) + rect.width * 0.3 + scrollBonus + rightEdgeBonus - widthPenalty;
            if (score > bestScore) {
                bestScore = score;
                best = rect;
            }
        }

        if (best) {
            const left = Math.max(6, best.left);
            const top = Math.max(6, best.top);
            const right = Math.min(viewportWidth - 6, best.right);
            const bottom = Math.min(viewportHeight - 6, best.bottom);
            if (right - left >= 320 && bottom - top >= 240) return { left, top, width: right - left, height: bottom - top };
        }

        if (!mapRect) return null;
        const left = Math.max(mapRect.right + 8, viewportWidth * 0.44);
        const top = Math.max(mapRect.top + 72, 70);
        const right = viewportWidth - 8;
        const bottom = Math.min(mapRect.bottom, viewportHeight - 8);
        if (right - left < 320 || bottom - top < 240) return null;
        return { left, top, width: right - left, height: bottom - top };
    }

    function expandedCriticalDrawerDockRect(baseRect) {
        if (!baseRect || mobileModeActive) return baseRect;
        const viewportWidth = Math.max(1, Number(pageWindow.innerWidth) || document.documentElement.clientWidth || 1);
        const viewportHeight = Math.max(1, Number(pageWindow.innerHeight) || document.documentElement.clientHeight || 1);
        const mapRect = elementDockRect(getLargestLeafletMap());
        const left = Math.max(4, mapRect ? Math.max(baseRect.left, mapRect.right + 2) : baseRect.left);
        const top = Math.max(4, mapRect ? mapRect.top : Math.min(baseRect.top, 70));
        const right = Math.min(viewportWidth - 4, Math.max(baseRect.right, viewportWidth - 4));
        const bottom = viewportHeight - 4;
        if (right - left < 320 || bottom - top < 260) return baseRect;
        return { left, top, width: right - left, height: bottom - top };
    }

    function criticalDrawerExpanded() {
        return Boolean(state.missionAgeWatch?.expanded) && !mobileModeActive;
    }

    function updateCriticalDrawerExpandButton(drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
        if (!drawer) return;
        const button = drawer.querySelector('.mcms-drawer-expand');
        const expanded = criticalDrawerExpanded();
        drawer.classList.toggle('mcms-critical-expanded', expanded);
        if (!button) return;
        button.classList.toggle('mcms-on', expanded);
        button.setAttribute('aria-pressed', String(expanded));
        button.title = expanded ? 'Restore Mission Age Watch to the mission-list area' : 'Expand Mission Age Watch over the Radio area';
        button.setAttribute('aria-label', button.title);
        button.innerHTML = expanded
            ? '<span aria-hidden="true">⤡</span><small>Restore</small>'
            : '<span aria-hidden="true">⤢</span><small>Expand</small>';
    }

    function toggleCriticalDrawerExpanded() {
        state.missionAgeWatch = { ...(state.missionAgeWatch || {}), expanded: !state.missionAgeWatch?.expanded };
        saveState();
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        updateCriticalDrawerExpandButton(drawer);
        positionCriticalDrawerOverMissionList();
    }

    function clearCriticalDrawerDock(drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
        if (!drawer) return;
        drawer.classList.remove('mcms-sidebar-docked', 'mcms-critical-expanded');
        for (const property of [
            '--mcms-critical-dock-left', '--mcms-critical-dock-top', '--mcms-critical-dock-width', '--mcms-critical-dock-height',
            'left', 'right', 'top', 'bottom', 'width', 'max-width', 'height', 'max-height', 'transform'
        ]) drawer.style.removeProperty(property);
    }

    function positionCriticalDrawerOverMissionList() {
        criticalDrawerDockTimer = null;
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (!drawer?.classList.contains('mcms-open')) {
            clearCriticalDrawerDock(drawer);
            return false;
        }
        const baseRect = findMissionListDockRect();
        if (!baseRect) {
            clearCriticalDrawerDock(drawer);
            return false;
        }
        const expanded = criticalDrawerExpanded();
        const rect = expanded ? expandedCriticalDrawerDockRect(baseRect) : baseRect;
        const left = `${Math.round(rect.left)}px`;
        const top = `${Math.round(rect.top)}px`;
        const width = `${Math.round(rect.width)}px`;
        const height = `${Math.round(rect.height)}px`;
        drawer.style.setProperty('--mcms-critical-dock-left', left);
        drawer.style.setProperty('--mcms-critical-dock-top', top);
        drawer.style.setProperty('--mcms-critical-dock-width', width);
        drawer.style.setProperty('--mcms-critical-dock-height', height);
        drawer.style.setProperty('left', left, 'important');
        drawer.style.setProperty('right', 'auto', 'important');
        drawer.style.setProperty('top', top, 'important');
        drawer.style.setProperty('bottom', 'auto', 'important');
        drawer.style.setProperty('width', width, 'important');
        drawer.style.setProperty('max-width', width, 'important');
        drawer.style.setProperty('height', height, 'important');
        drawer.style.setProperty('max-height', height, 'important');
        drawer.style.setProperty('transform', 'none', 'important');
        drawer.classList.add('mcms-sidebar-docked');
        drawer.classList.toggle('mcms-critical-expanded', expanded);
        updateCriticalDrawerExpandButton(drawer);
        return true;
    }

    function scheduleCriticalDrawerDock(delay = 0) {
        runtimeClearTimeout(criticalDrawerDockTimer);
        criticalDrawerDockTimer = runtimeSetTimeout(positionCriticalDrawerOverMissionList, Math.max(0, Number(delay) || 0));
    }

    function resetCriticalVirtualWindow(drawer = null, scrollTop = true) {
        criticalDrawerRenderLimit = CRITICAL_RENDER_BATCH_SIZE;
        const list = (drawer || document.getElementById(SCRIPT.criticalDrawerId))?.querySelector?.('.mcms-drawer-list');
        if (scrollTop && list) list.scrollTop = 0;
    }

    function createCriticalDrawer() {
        let drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (drawer) return drawer;
        drawer = document.createElement('aside');
        drawer.id = SCRIPT.criticalDrawerId;
        drawer.setAttribute('aria-label', 'Mission Age Watch');
        drawer.setAttribute('aria-hidden', 'true');
        drawer.innerHTML = `
            <div class="mcms-drawer-head">
                <div class="mcms-drawer-heading">
                    <div class="mcms-drawer-identity">
                        <strong class="mcms-drawer-title">MISSION AGE WATCH</strong>
                        <span class="mcms-drawer-subtitle">Filter ownership, category and status · sort by age or distance</span>
                        <span class="mcms-critical-refreshed" data-critical-refreshed>Data sync pending</span>
                    </div>
                    <div class="mcms-drawer-header-controls" data-critical-view-controls>
                        <button class="mcms-critical-view-trigger" type="button" data-critical-view-toggle aria-expanded="false" aria-controls="${SCRIPT.criticalDrawerId}-view-menu" aria-label="Open Mission Age Watch view controls" title="Open age, sort and distance-origin controls">
                            <span class="mcms-critical-view-trigger-label">VIEW CONTROLS</span>
                            <strong data-critical-view-summary>ALL · AGE · LIVE MAP</strong>
                            <span class="mcms-critical-view-chevron" aria-hidden="true">⌄</span>
                        </button>
                        <section class="mcms-critical-view-menu" id="${SCRIPT.criticalDrawerId}-view-menu" data-critical-view-menu aria-label="Mission Age Watch view controls" hidden>
                            <div class="mcms-critical-view-menu-head">
                                <span><strong>VIEW CONTROLS</strong><small>Age, ordering and distance origin</small></span>
                                <button type="button" data-critical-view-close>DONE</button>
                            </div>
                            <div class="mcms-critical-age-filters" data-critical-age-filters aria-label="Mission age range"></div>
                            <div class="mcms-critical-sort-controls" data-critical-sort-controls aria-label="Mission ordering and distance origin"></div>
                        </section>
                    </div>
                </div>
                <div class="mcms-drawer-actions">
                    <button class="mcms-drawer-expand" type="button" title="Expand Mission Age Watch over the Radio area" aria-label="Expand Mission Age Watch over the Radio area" aria-pressed="false"><span aria-hidden="true">⤢</span><small>Expand</small></button>
                    <button class="mcms-drawer-refresh" type="button" title="Refresh Mission Age Watch" aria-label="Refresh Mission Age Watch">↻</button>
                    <button class="mcms-drawer-close" type="button" title="Close Mission Age Watch" aria-label="Close Mission Age Watch">×</button>
                </div>
                <section class="mcms-critical-values" data-critical-values aria-label="Mission value overview"></section>
            </div>
            <div class="mcms-critical-type-filters" data-critical-type-filters aria-label="Mission ownership filters"></div>
            <section class="mcms-critical-filter-deck" aria-label="Mission Age Watch filters">
                <div class="mcms-critical-filter-overview" data-critical-filter-overview aria-live="polite"></div>
                <section class="mcms-critical-quick-section" aria-label="Mission Age Watch quick views">
                    <div class="mcms-critical-filter-section-head"><strong>QUICK VIEWS</strong><small>One-click operational presets</small></div>
                    <div class="mcms-critical-quick-views" data-critical-quick-views role="group" aria-label="Quick mission views"></div>
                </section>
                <div class="mcms-critical-category-filters" data-critical-category-filters aria-label="Mission category filters"></div>
                <div class="mcms-critical-advanced-shell" data-critical-advanced-shell>
                    <button class="mcms-critical-advanced-toggle" type="button" data-critical-advanced-toggle aria-expanded="false" aria-controls="${SCRIPT.criticalDrawerId}-advanced-filters">
                        <span><strong>ADVANCED FILTERS</strong><small data-critical-advanced-summary>Exact mission conditions and unit scope</small></span>
                        <i aria-hidden="true">⌄</i>
                    </button>
                    <section class="mcms-critical-advanced-panel" id="${SCRIPT.criticalDrawerId}-advanced-filters" data-critical-advanced-panel aria-label="Advanced mission filters" hidden>
                        <div class="mcms-critical-summary" data-critical-summary aria-label="Mission operational filters"></div>
                    </section>
                </div>
            </section>
            <div class="mcms-drawer-list" tabindex="0" aria-label="Mission Age Watch mission list"></div>`;

        drawer.addEventListener('change', event => {
            const origin = closestEventTarget(event, '[data-critical-distance-origin]');
            if (!origin) return;
            const value = String(origin.value || 'live');
            if (!/^(?:live|locked|quick:[a-z0-9_-]+|bookmark:\d+)$/iu.test(value)) return;
            state.missionAgeWatch = { ...(state.missionAgeWatch || {}), distanceOrigin: value };
            saveState();
            resetCriticalVirtualWindow(drawer);
            renderCriticalDrawer(null, { updateViewTime: true });
        });

        drawer.addEventListener('scroll', event => {
            const list = event.target?.classList?.contains('mcms-drawer-list') ? event.target : null;
            if (!list || criticalDrawerVirtualScrollTimer) return;
            if (list.scrollTop + list.clientHeight < list.scrollHeight - 240) return;
            criticalDrawerVirtualScrollTimer = runtimeSetTimeout(() => {
                criticalDrawerVirtualScrollTimer = null;
                criticalDrawerRenderLimit += CRITICAL_RENDER_BATCH_SIZE;
                renderCriticalDrawer(null, { updateViewTime: false, preserveScroll: true });
            }, 80);
        }, true);

        drawer.addEventListener('click', event => {
            if (closestEventTarget(event, '[data-critical-view-toggle]')) { toggleCriticalViewControls(drawer); return; }
            if (closestEventTarget(event, '[data-critical-view-close]')) {
                closeCriticalViewControls(drawer);
                drawer.querySelector('[data-critical-view-toggle]')?.focus?.({ preventScroll: true });
                return;
            }
            if (closestEventTarget(event, '[data-critical-advanced-toggle]')) {
                const next = !state.missionAgeWatch?.advancedFiltersOpen;
                state.missionAgeWatch = { ...(state.missionAgeWatch || {}), advancedFiltersOpen: next };
                saveState();
                setCriticalAdvancedFiltersOpen(next, drawer);
                return;
            }
            const quickViewButton = closestEventTarget(event, '[data-critical-quick-view]');
            if (quickViewButton) {
                const quickView = String(quickViewButton.dataset.criticalQuickView || '');
                if (applyCriticalQuickView(quickView)) {
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            if (closestEventTarget(event, '.mcms-drawer-expand')) { toggleCriticalDrawerExpanded(); return; }
            if (closestEventTarget(event, '.mcms-drawer-refresh')) { refreshCriticalDrawer(true); return; }
            if (closestEventTarget(event, '.mcms-drawer-close')) { closeCriticalDrawer(); return; }
            if (closestEventTarget(event, '[data-critical-clear-filters]')) {
                resetCriticalWatchFilters();
                resetCriticalVirtualWindow(drawer);
                renderCriticalDrawer(null, { updateViewTime: true });
                return;
            }
            const ageFilterButton = closestEventTarget(event, '[data-critical-age-filter]');
            if (ageFilterButton) {
                const ageFilter = String(ageFilterButton.dataset.criticalAgeFilter || '');
                if (CRITICAL_AGE_FILTER_KEYS.includes(ageFilter)) {
                    state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ageFilter };
                    saveState();
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            const sortButton = closestEventTarget(event, '[data-critical-sort]');
            if (sortButton) {
                const sortMode = String(sortButton.dataset.criticalSort || '');
                if (CRITICAL_SORT_KEYS.includes(sortMode)) {
                    state.missionAgeWatch = { ...(state.missionAgeWatch || {}), sortMode };
                    saveState();
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            if (closestEventTarget(event, '[data-critical-lock-origin]')) {
                if (lockCriticalDistanceOrigin()) {
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                    showToast('Distance origin locked to current map centre');
                }
                return;
            }
            const ownershipButton = closestEventTarget(event, '[data-critical-ownership-filter]');
            if (ownershipButton) {
                const ownership = String(ownershipButton.dataset.criticalOwnershipFilter || '');
                if (CRITICAL_OWNERSHIP_FILTER_KEYS.includes(ownership)) {
                    state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ownershipFilter: ownership };
                    saveState();
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            const categoryButton = closestEventTarget(event, '[data-critical-category-filter]');
            if (categoryButton) {
                const category = String(categoryButton.dataset.criticalCategoryFilter || '');
                if (CRITICAL_CATEGORY_FILTER_KEYS.includes(category)) {
                    state.missionAgeWatch = { ...(state.missionAgeWatch || {}), categoryFilter: category };
                    saveState();
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            const statusButton = closestEventTarget(event, '[data-critical-primary-status]');
            if (statusButton) {
                const status = String(statusButton.dataset.criticalPrimaryStatus || 'all');
                if (CRITICAL_PRIMARY_STATUS_KEYS.includes(status)) {
                    state.missionAgeWatch = { ...(state.missionAgeWatch || {}), primaryStatus: selectedCriticalPrimaryStatus() === status ? 'all' : status };
                    saveState();
                    resetCriticalVirtualWindow(drawer);
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            const conditionButton = closestEventTarget(event, '[data-critical-condition]');
            if (conditionButton) {
                const condition = String(conditionButton.dataset.criticalCondition || '');
                if (condition === 'onway') state.missionAgeWatch = { ...(state.missionAgeWatch || {}), hasVehiclesOnWay: !state.missionAgeWatch?.hasVehiclesOnWay };
                if (condition === 'my-units') state.missionAgeWatch = { ...(state.missionAgeWatch || {}), onlyMyUnits: !state.missionAgeWatch?.onlyMyUnits };
                saveState();
                resetCriticalVirtualWindow(drawer);
                renderCriticalDrawer(null, { updateViewTime: true });
                return;
            }
            const valueModeButton = closestEventTarget(event, '[data-critical-value-mode]');
            if (valueModeButton) {
                const mode = String(valueModeButton.dataset.criticalValueMode || 'total');
                if (CRITICAL_VALUE_MODE_KEYS.includes(mode)) {
                    state.missionAgeWatch = { ...(state.missionAgeWatch || {}), valueMode: mode };
                    saveState();
                    renderCriticalDrawer(null, { updateViewTime: true });
                }
                return;
            }
            if (closestEventTarget(event, '[data-critical-load-more]')) {
                criticalDrawerRenderLimit += CRITICAL_RENDER_BATCH_SIZE;
                renderCriticalDrawer(null, { updateViewTime: false, preserveScroll: true });
                return;
            }
            const zoomButton = closestEventTarget(event, '.mcms-critical-zoom');
            if (zoomButton) {
                event.preventDefault();
                event.stopPropagation();
                focusMissionById(zoomButton.dataset.zoomMissionId, false);
                return;
            }
            const openButton = closestEventTarget(event, '.mcms-critical-open');
            if (openButton) {
                event.preventDefault();
                event.stopPropagation();
                focusMissionById(openButton.dataset.openMissionId, true);
                return;
            }
            const row = closestEventTarget(event, '[data-mission-id]');
            if (row) focusMissionById(row.dataset.missionId, false);
        });
        drawer.addEventListener('dblclick', event => {
            if (closestEventTarget(event, '.mcms-critical-zoom, .mcms-critical-open')) return;
            const row = closestEventTarget(event, '[data-mission-id]');
            if (row) { event.preventDefault(); focusMissionById(row.dataset.missionId, true); }
        });
        runtimeListen(document, 'pointerdown', event => {
            const activeDrawer = document.getElementById(SCRIPT.criticalDrawerId);
            const controls = activeDrawer?.querySelector?.('[data-critical-view-controls]');
            if (!controls?.classList?.contains('mcms-open')) return;
            if (event.target && controls.contains(event.target)) return;
            closeCriticalViewControls(activeDrawer);
        }, true);
        document.body.appendChild(drawer);
        updateCriticalDrawerExpandButton(drawer);
        return drawer;
    }

    function criticalEntryNeedsAssistance(entry) {
        return Boolean(summariseCriticalRequirement(entry?.snapshot?.missingText) || entry?.stuckRecord?.isStuck);
    }

    function missionAgeWatchHasNonDefaultState() {
        const watch = state.missionAgeWatch || {};
        return selectedCriticalAgeFilter() !== '8h' ||
            selectedCriticalSortMode() !== 'age' ||
            selectedCriticalOwnershipFilter() !== 'personal' ||
            selectedCriticalCategoryFilter() !== 'all' ||
            selectedCriticalPrimaryStatus() !== 'all' ||
            Boolean(watch.hasVehiclesOnWay) ||
            Boolean(watch.onlyMyUnits) ||
            selectedCriticalValueMode() !== 'total' ||
            selectedCriticalDistanceOrigin() !== 'live';
    }

    function resetCriticalWatchFilters() {
        const expanded = Boolean(state.missionAgeWatch?.expanded);
        state.missionAgeWatch = {
            ...(state.missionAgeWatch || {}),
            ageFilter: '8h',
            sortMode: 'age',
            expanded,
            ownershipFilter: 'personal',
            categoryFilter: 'all',
            primaryStatus: 'all',
            advancedFiltersOpen: false,
            hasVehiclesOnWay: false,
            onlyMyUnits: false,
            valueMode: 'total',
            distanceOrigin: 'live',
            lockedOrigin: null
        };
        criticalDrawerRenderLimit = CRITICAL_RENDER_BATCH_SIZE;
        saveState();
    }

    function criticalAgeFiltersHtml(allEntries) {
        const selected = selectedCriticalAgeFilter();
        const scoped = criticalFilterEntries(allEntries, ['age']);
        const button = key => {
            const definition = criticalAgeFilterDefinition(key);
            const active = selected === key;
            const count = scoped.filter(entry => definition.minAgeMs === 0 ? true : Number.isFinite(entry.missionAge) && entry.missionAge >= definition.minAgeMs).length;
            return `<button type="button" class="mcms-critical-age-filter mcms-age-filter-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}" data-critical-age-filter="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(definition.title)}"><span>${escapeHtml(definition.label)}</span><strong>${count.toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓ SELECTED' : 'SELECT'}</i></button>`;
        };
        return `<span class="mcms-critical-age-label">AGE</span>${CRITICAL_AGE_FILTER_KEYS.map(button).join('')}`;
    }

    function criticalDistanceOriginControlsHtml() {
        const selected = selectedCriticalDistanceOrigin();
        const options = criticalDistanceOriginOptions().map(option => `<option value="${escapeHtml(option.key)}"${selected === option.key ? ' selected' : ''}>${escapeHtml(option.label)}</option>`).join('');
        return `<label class="mcms-critical-origin-control" title="Choose the reference point used for mission distances"><span>ORIGIN</span><select data-critical-distance-origin>${options}</select></label><button type="button" class="mcms-critical-lock-origin" data-critical-lock-origin title="Lock distance calculations to the current map centre">LOCK HERE</button>`;
    }

    function criticalSortControlsHtml() {
        const selected = selectedCriticalSortMode();
        const ageDefinition = criticalAgeFilterDefinition();
        const button = (key, label, title) => {
            const active = selected === key;
            return `<button type="button" class="mcms-critical-sort-button mcms-sort-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}" data-critical-sort="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span>${escapeHtml(label)}</span><i aria-hidden="true">${active ? '✓ SELECTED' : 'SELECT'}</i></button>`;
        };
        return `<span class="mcms-critical-sort-label">SORT</span>${button('age', 'Age', `Use ${ageDefinition.sort === 'newest' ? 'newest' : 'oldest'} mission ordering for the selected age range`)}${button('closest', 'Closest', 'Sort closest to the selected distance origin first')}${button('furthest', 'Furthest', 'Sort furthest from the selected distance origin first')}${criticalDistanceOriginControlsHtml()}`;
    }

    function criticalViewControlsSummary(allEntries = null) {
        const ageDefinition = criticalAgeFilterDefinition();
        let age = String(ageDefinition.label || 'ALL').toUpperCase();
        if (Array.isArray(allEntries)) {
            const scoped = criticalFilterEntries(allEntries, ['age']);
            const count = scoped.filter(entry => ageDefinition.minAgeMs === 0 ? true : Number.isFinite(entry.missionAge) && entry.missionAge >= ageDefinition.minAgeMs).length;
            age = `${age} ${count.toLocaleString('en-GB')}`;
        }
        const sort = {
            age: 'AGE',
            closest: 'CLOSEST',
            furthest: 'FURTHEST'
        }[selectedCriticalSortMode()] || 'AGE';
        const originKey = selectedCriticalDistanceOrigin();
        const originOption = criticalDistanceOriginOptions().find(option => option.key === originKey);
        let origin = String(originOption?.label || 'Live map centre')
            .replace(/^Quick Place:\s*/iu, '')
            .replace(/^Bookmark:\s*/iu, '')
            .trim();
        if (originKey === 'live') origin = 'LIVE MAP';
        else if (originKey === 'locked') origin = 'LOCKED';
        else origin = origin.toUpperCase();
        return `${age} · ${sort} · ${origin}`;
    }

    function setCriticalViewControlsOpen(open, drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
        const controls = drawer?.querySelector?.('[data-critical-view-controls]');
        const toggle = controls?.querySelector?.('[data-critical-view-toggle]');
        const menu = controls?.querySelector?.('[data-critical-view-menu]');
        if (!controls || !toggle || !menu) return false;
        const next = Boolean(open);
        controls.classList.toggle('mcms-open', next);
        toggle.setAttribute('aria-expanded', next ? 'true' : 'false');
        menu.hidden = !next;
        return true;
    }

    function closeCriticalViewControls(drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
        const controls = drawer?.querySelector?.('[data-critical-view-controls]');
        if (!controls?.classList?.contains('mcms-open')) return false;
        setCriticalViewControlsOpen(false, drawer);
        return true;
    }

    function toggleCriticalViewControls(drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
        const controls = drawer?.querySelector?.('[data-critical-view-controls]');
        if (!controls) return false;
        return setCriticalViewControlsOpen(!controls.classList.contains('mcms-open'), drawer);
    }

    function selectedCriticalQuickView() {
        const status = selectedCriticalPrimaryStatus();
        const onWay = Boolean(state.missionAgeWatch?.hasVehiclesOnWay);
        const myUnits = Boolean(state.missionAgeWatch?.onlyMyUnits);
        if (status === 'all' && !onWay && !myUnits) return 'all';
        if (status === 'attention' && !onWay && !myUnits) return 'attention';
        if (status === 'all' && onWay && !myUnits) return 'responding';
        if (status === 'clearing' && !onWay && !myUnits) return 'clearing';
        if (status === 'on-scene' && !onWay && !myUnits) return 'stable';
        if (status === 'all' && !onWay && myUnits) return 'my-units';
        return 'custom';
    }

    function applyCriticalQuickView(key) {
        const definitions = {
            all: { primaryStatus: 'all', hasVehiclesOnWay: false, onlyMyUnits: false },
            attention: { primaryStatus: 'attention', hasVehiclesOnWay: false, onlyMyUnits: false },
            responding: { primaryStatus: 'all', hasVehiclesOnWay: true, onlyMyUnits: false },
            clearing: { primaryStatus: 'clearing', hasVehiclesOnWay: false, onlyMyUnits: false },
            stable: { primaryStatus: 'on-scene', hasVehiclesOnWay: false, onlyMyUnits: false },
            'my-units': { primaryStatus: 'all', hasVehiclesOnWay: false, onlyMyUnits: true }
        };
        const definition = definitions[String(key || '')];
        if (!definition) return false;
        state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ...definition };
        saveState();
        return true;
    }

    function setCriticalAdvancedFiltersOpen(open, drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
        const shell = drawer?.querySelector?.('[data-critical-advanced-shell]');
        const toggle = shell?.querySelector?.('[data-critical-advanced-toggle]');
        const panel = shell?.querySelector?.('[data-critical-advanced-panel]');
        if (!shell || !toggle || !panel) return false;
        const next = Boolean(open);
        shell.classList.toggle('mcms-open', next);
        toggle.setAttribute('aria-expanded', next ? 'true' : 'false');
        panel.hidden = !next;
        return true;
    }

    function criticalAdvancedFilterSummaryText() {
        const statusLabels = {
            all: 'Any condition',
            attention: 'Needs attention',
            'no-scene': 'No units on scene',
            assistance: 'Needs assistance',
            clearing: 'Clearing',
            'on-scene': 'On scene / stable'
        };
        const parts = [];
        const status = selectedCriticalPrimaryStatus();
        if (status !== 'all') parts.push(statusLabels[status] || status);
        if (state.missionAgeWatch?.hasVehiclesOnWay) parts.push('Vehicles on way');
        if (state.missionAgeWatch?.onlyMyUnits) parts.push('Only my units');
        return parts.length ? parts.join(' + ') : 'Exact mission conditions and unit scope';
    }

    function criticalQuickViewsHtml(allEntries) {
        const scoped = criticalFilterEntries(allEntries, ['status', 'onway', 'myunits']);
        const countStatus = key => scoped.filter(entry => criticalEntryPrimaryStatus(entry) === key).length;
        const counts = {
            all: scoped.length,
            attention: scoped.filter(entry => ['no-scene', 'assistance'].includes(criticalEntryPrimaryStatus(entry))).length,
            responding: scoped.filter(entry => Math.max(0, Number(entry?.units?.onWay ?? entry?.units?.travelling) || 0) > 0).length,
            clearing: countStatus('clearing'),
            stable: countStatus('on-scene'),
            'my-units': scoped.filter(criticalEntryHasMyUnits).length
        };
        const selected = selectedCriticalQuickView();
        const definitions = [
            ['all', 'All', 'Show every mission matching the ownership, category and age filters'],
            ['attention', 'Attention', 'Show missions with no units on scene or detected assistance requirements'],
            ['responding', 'Responding', 'Show missions with at least one vehicle on the way'],
            ['clearing', 'Clearing', 'Show missions currently completing'],
            ['stable', 'Stable', 'Show missions with units on scene and no detected issue'],
            ['my-units', 'My Units', 'Show missions with one of your units committed']
        ];
        return definitions.map(([key, label, title]) => {
            const active = selected === key;
            const count = Number(counts[key]) || 0;
            return `<button type="button" class="mcms-critical-quick-view mcms-quick-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}${count === 0 ? ' mcms-zero' : ''}" data-critical-quick-view="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span>${escapeHtml(label)}</span><strong>${count.toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓' : ''}</i></button>`;
        }).join('');
    }

    function criticalOperationalFilterLabel() {
        const quick = selectedCriticalQuickView();
        const labels = {
            all: 'All missions',
            attention: 'Needs attention',
            responding: 'Responding',
            clearing: 'Clearing',
            stable: 'Stable',
            'my-units': 'Only my units'
        };
        return labels[quick] || `Custom: ${criticalAdvancedFilterSummaryText()}`;
    }

    function criticalFilterOverviewHtml(allEntries, visibleEntries) {
        const ownership = { all: 'All ownership', personal: 'Personal', alliance: 'Alliance' }[selectedCriticalOwnershipFilter()] || 'Personal';
        const category = { all: 'All categories', standard: 'Standard', event: 'Timed event', special: 'Special event' }[selectedCriticalCategoryFilter()] || 'All categories';
        const filterText = `${ownership} · ${category} · ${criticalOperationalFilterLabel()}`;
        const showing = `Showing ${visibleEntries.length.toLocaleString('en-GB')} of ${allEntries.length.toLocaleString('en-GB')}`;
        return `<span class="mcms-critical-filter-overview-copy"><small>ACTIVE FILTER</small><strong title="${escapeHtml(filterText)}">${escapeHtml(filterText)}</strong></span><span class="mcms-critical-filter-overview-count">${escapeHtml(showing)}</span>${missionAgeWatchHasNonDefaultState() ? '<button type="button" data-critical-clear-filters title="Reset all Mission Age Watch filters and sorting">Clear</button>' : ''}`;
    }

    function criticalOwnershipFiltersHtml(allEntries) {
        const selected = selectedCriticalOwnershipFilter();
        const scoped = criticalFilterEntries(allEntries, ['ownership']);
        const counts = { all: scoped.length, personal: 0, alliance: 0 };
        scoped.forEach(entry => { if (CRITICAL_OWNERSHIP_KEYS.includes(entry.ownership)) counts[entry.ownership] += 1; });
        const button = (key, label, title) => {
            const active = selected === key;
            const allianceClass = key === 'alliance' ? ' mcms-alliance-text' : '';
            return `<button type="button" class="mcms-critical-type-filter mcms-ownership-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}" data-critical-ownership-filter="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span class="${allianceClass.trim()}">${escapeHtml(label)}</span><strong>${counts[key].toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓ SELECTED' : 'SELECT'}</i></button>`;
        };
        return `<span class="mcms-critical-type-label">OWNERSHIP</span>${button('all', 'All', 'Show Personal and Alliance missions')}${button('personal', 'Personal', 'Show missions owned by you')}${button('alliance', 'Alliance', 'Show Alliance-owned or Alliance-shared missions')}`;
    }

    function criticalCategoryFiltersHtml(allEntries) {
        const selected = selectedCriticalCategoryFilter();
        const scoped = criticalFilterEntries(allEntries, ['category']);
        const counts = { all: scoped.length, standard: 0, event: 0, special: 0 };
        scoped.forEach(entry => { if (CRITICAL_CATEGORY_KEYS.includes(entry.category)) counts[entry.category] += 1; });
        const button = (key, label, title) => {
            const active = selected === key;
            return `<button type="button" class="mcms-critical-category-filter mcms-category-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}${counts[key] === 0 ? ' mcms-zero' : ''}" data-critical-category-filter="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span>${escapeHtml(label)}</span><strong>${counts[key].toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓' : ''}</i></button>`;
        };
        return `<span class="mcms-critical-category-label">CATEGORY</span>${button('all', 'All', 'Show Standard, Timed Event and Special Event missions')}${button('standard', 'Standard', 'Show normal missions')}${button('event', 'Timed Event', 'Show ordinary timed or community Event missions')}${button('special', 'Special Event', 'Show official developer-launched Special Event missions')}`;
    }

    function criticalMissionValueDetails(entry) {
        if (entry?.valueDetails && Object.prototype.hasOwnProperty.call(entry.valueDetails, 'value')) return entry.valueDetails;
        const missionId = normaliseMissionId(entry?.missionId);
        const marker = entry?.marker || entry?.snapshot?.marker || null;
        const liveMarkerValue = exactCreditFromObject(marker);
        if (liveMarkerValue !== null) return { value: liveMarkerValue, source: 'live marker' };
        const snapshotValue = parseCreditValue(entry?.snapshot?.averageCredits);
        if (snapshotValue !== null) return { value: snapshotValue, source: 'mission snapshot' };
        const overlayValue = missionId === null ? null : parseCreditValue(missionOverlayData.get(missionId)?.averageCredits);
        if (overlayValue !== null) return { value: overlayValue, source: 'captured mission data' };
        const entryValue = parseCreditValue(entry?.averageCredits);
        if (entryValue !== null) return { value: entryValue, source: 'watcher record' };
        const panelValue = missionId === null ? null : creditsFromMissionPanel(missionId);
        if (panelValue !== null) return { value: panelValue, source: 'mission list' };
        return { value: null, source: 'unavailable' };
    }


    function missionValueCurrencyMeta(hostname = location.hostname) {
        const host = String(hostname || '').trim().toLowerCase();
        if (/(?:^|\.)missionchief\.com$/u.test(host)) return { locale: 'en-US', symbol: '$' };
        if (/(?:^|\.)leitstellenspiel\.de$/u.test(host)) return { locale: 'de-DE', symbol: '€' };
        if (/(?:^|\.)meldkamerspel\.com$/u.test(host)) return { locale: 'nl-NL', symbol: '€' };
        return { locale: 'en-GB', symbol: '£' };
    }

    function formatMissionWindowValue(value, hostname = location.hostname) {
        const amount = Number(value);
        if (!Number.isFinite(amount) || amount < 0) return '';
        const { locale, symbol } = missionValueCurrencyMeta(hostname);
        return `${symbol}${Math.round(amount).toLocaleString(locale)}`;
    }

    function missionValueIdFromUrl(value, baseUrl = location.href) {
        let pathname = String(value || '').trim();
        if (!pathname) return null;
        try { pathname = new URL(pathname, baseUrl).pathname; } catch (err) {}
        const match = pathname.match(/\/missions\/(\d+)(?:\/|$)/u);
        return match ? normaliseMissionId(match[1]) : null;
    }

    function missionValueIdFromElement(root) {
        if (!root) return null;
        const doc = root.ownerDocument || document;
        const directNodes = [root];
        try {
            directNodes.push(...root.querySelectorAll('[data-mission-id], [data-mission_id], input[name="mission_id"], input[name="mission[id]"]'));
        } catch (err) {}
        for (const node of directNodes) {
            const candidates = [
                node?.dataset?.missionId,
                node?.dataset?.mission_id,
                node?.getAttribute?.('data-mission-id'),
                node?.getAttribute?.('data-mission_id'),
                node?.value
            ];
            for (const candidate of candidates) {
                const id = normaliseMissionId(candidate);
                if (id !== null) return id;
            }
            const idMatch = String(node?.id || '').match(/(?:^|_)(?:mission|mission_content|mission_panel)_(\d+)(?:$|_)/u);
            if (idMatch) return normaliseMissionId(idMatch[1]);
        }

        let routeNodes = [];
        try {
            routeNodes = Array.from(root.querySelectorAll('a[href*="/missions/"], form[action*="/missions/"], [data-url*="/missions/"], [data-href*="/missions/"]'));
        } catch (err) {}
        for (const node of routeNodes) {
            for (const attribute of ['href', 'action', 'data-url', 'data-href']) {
                const id = missionValueIdFromUrl(node.getAttribute?.(attribute), doc.location?.href || location.href);
                if (id !== null) return id;
            }
        }

        if (doc !== document) {
            try {
                const id = missionValueIdFromUrl(doc.location?.href, location.href);
                if (id !== null) return id;
            } catch (err) {}
        }
        return null;
    }

    function missionValueMountForRoot(root) {
        if (!root) return null;
        const selector = '.lightbox_content, .modal-body, #mission_content, .mission_content, [data-mission-content]';
        try {
            if (root.matches?.(selector)) return root;
            return root.querySelector?.(selector) || root;
        } catch (err) {
            return root;
        }
    }

        function missionValueWindowCandidates() {
        const discovered = [];
        const add = root => {
            if (!root?.isConnected) return;
            const missionId = missionValueIdFromElement(root);
            if (missionId === null) return;
            const mount = missionValueMountForRoot(root);
            if (!mount?.isConnected || mount.closest?.(`#${SCRIPT.panelId}, #${SCRIPT.helpCenterId}`)) return;
            const toolbarSpacer = missionValueToolbarSpacer(root, mount);
            const toolbar = missionValueToolbarBar(toolbarSpacer, root, mount);
            discovered.push({ root, mount, missionId, toolbarSpacer, toolbar });
        };

        transportSweepVisibleWindowRoots().forEach(add);
        for (const context of transportSweepDocumentContexts()) {
            observeMissionValueDocument(context.doc);
            if (context.doc !== document) {
                try {
                    if (missionValueIdFromUrl(context.doc.location?.href, location.href) !== null) add(context.doc.body);
                } catch (err) {}
            }
        }
        return missionValuePreferredCandidates(discovered);
    }

    function removeMissionValueRows(scope = document) {
        try { scope.querySelectorAll?.('.mcms-mission-value-row').forEach(row => row.remove()); } catch (err) {}
    }

    function clearMissionValueIndicators() {
        for (const context of transportSweepDocumentContexts()) removeMissionValueRows(context.doc);
    }


        function missionValueToolbarSpacer(root, mount) {
        const scopes = [root, mount].filter(Boolean);
        for (const scope of scopes) {
            try {
                if (scope.matches?.('#navbar-alarm-spacer')) return scope;
                const spacer = scope.querySelector?.('#navbar-alarm-spacer');
                if (spacer) return spacer;
            } catch (err) {}
        }
        const doc = root?.ownerDocument || mount?.ownerDocument || null;
        if (!doc || (root !== doc.body && mount !== doc.body)) return null;
        try {
            return missionValueIdFromUrl(doc.location?.href, location.href) !== null
                ? doc.getElementById?.('navbar-alarm-spacer') || null
                : null;
        } catch (err) {
            return null;
        }
    }

    function missionValueToolbarBar(spacer, root, mount) {
        if (spacer?.isConnected) {
            try {
                return spacer.closest?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || spacer.parentElement || null;
            } catch (err) {}
        }
        for (const scope of [root, mount]) {
            try {
                const bars = Array.from(scope?.querySelectorAll?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || []);
                const bar = bars.find(candidate => candidate.querySelector?.('#navbar-alarm-spacer'));
                if (bar) return bar;
            } catch (err) {}
        }
        return null;
    }

    function missionValueSpacerVisibleWidth(spacer) {
        if (!spacer?.isConnected) return 0;
        try {
            const view = spacer.ownerDocument?.defaultView || pageWindow;
            const style = view?.getComputedStyle?.(spacer);
            if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse' || Number(style?.opacity) === 0) return 0;
        } catch (err) {}
        try {
            const rect = spacer.getBoundingClientRect?.();
            return rect && rect.width > 0 ? Math.max(0, Math.floor(rect.width)) : 0;
        } catch (err) {
            return 0;
        }
    }

    function missionValuePresentation(availableWidth, formatted) {
        const width = Math.max(0, Number(availableWidth) || 0);
        const value = String(formatted || '');
        if (width >= 176) return { mode: 'full', text: `Mission Value · ${value}` };
        if (width >= 110) return { mode: 'short', text: `Value · ${value}` };
        if (width >= 58) return { mode: 'value', text: value };
        return { mode: 'fallback', text: `Mission Value · ${value}` };
    }

    function missionValuePreferredCandidates(candidateList) {
        const groups = new Map();
        for (const candidate of Array.from(candidateList || [])) {
            const missionId = normaliseMissionId(candidate?.missionId);
            if (missionId === null || !candidate?.mount?.isConnected) continue;
            if (!groups.has(missionId)) groups.set(missionId, []);
            groups.get(missionId).push(candidate);
        }
        const selected = [];
        for (const group of groups.values()) {
            const toolbarCandidates = group.filter(candidate => candidate.toolbarSpacer?.isConnected && candidate.toolbar?.isConnected);
            const pool = toolbarCandidates.length ? toolbarCandidates : group;
            const seenHosts = new Set();
            for (const candidate of pool) {
                const host = candidate.toolbarSpacer?.isConnected ? candidate.toolbarSpacer : candidate.mount;
                if (!host || seenHosts.has(host)) continue;
                seenHosts.add(host);
                selected.push(candidate);
            }
        }
        return selected;
    }

    function missionValueCandidateScopes(candidate) {
        const scopes = new Set([candidate?.root, candidate?.mount, candidate?.toolbarSpacer, candidate?.toolbar].filter(Boolean));
        const doc = candidate?.root?.ownerDocument || candidate?.mount?.ownerDocument || null;
        try {
            const frame = doc?.defaultView?.frameElement || null;
            if (frame) {
                scopes.add(frame);
                const frameWindow = frame.closest?.('#lightbox_box, #lightbox, .modal, [role="dialog"], .ui-dialog, .lightbox_content');
                if (frameWindow) scopes.add(frameWindow);
            }
        } catch (err) {}
        return Array.from(scopes);
    }

    function missionValueRowsForCandidate(candidate) {
        const rows = new Set();
        for (const scope of missionValueCandidateScopes(candidate)) {
            try {
                if (scope.matches?.('.mcms-mission-value-row')) rows.add(scope);
                scope.querySelectorAll?.('.mcms-mission-value-row').forEach(row => rows.add(row));
            } catch (err) {}
        }
        return Array.from(rows);
    }

    function pruneMissionValueHostObservers(activeSpacers = null) {
        for (const [spacer, record] of missionValueHostObservers) {
            const keep = Boolean(spacer?.isConnected && record?.toolbar?.isConnected && (!activeSpacers || activeSpacers.has(spacer)));
            if (keep) continue;
            try { record?.resizeObserver?.disconnect?.(); } catch (err) {}
            try { record?.mutationObserver?.disconnect?.(); } catch (err) {}
            missionValueHostObservers.delete(spacer);
        }
    }

    function observeMissionValueHost(candidate) {
        const spacer = candidate?.toolbarSpacer;
        const toolbar = candidate?.toolbar;
        if (!spacer?.isConnected || !toolbar?.isConnected) return;
        const existing = missionValueHostObservers.get(spacer);
        if (existing?.toolbar === toolbar) return;
        if (existing) {
            try { existing.resizeObserver?.disconnect?.(); } catch (err) {}
            try { existing.mutationObserver?.disconnect?.(); } catch (err) {}
        }
        const view = spacer.ownerDocument?.defaultView || pageWindow;
        const ResizeObserverCtor = view?.ResizeObserver || pageWindow.ResizeObserver;
        const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
        const record = { toolbar, resizeObserver: null, mutationObserver: null };
        if (typeof ResizeObserverCtor === 'function') {
            record.resizeObserver = runtimeTrackObserver(new ResizeObserverCtor(() => scheduleMissionValueScan(24)));
            record.resizeObserver.observe(spacer);
        }
        if (typeof MutationObserverCtor === 'function') {
            record.mutationObserver = runtimeTrackObserver(new MutationObserverCtor(() => scheduleMissionValueScan(24)));
            record.mutationObserver.observe(toolbar, { childList: true, subtree: false });
        }
        missionValueHostObservers.set(spacer, record);
    }

    

    

        function syncMissionValueCandidate(candidate) {
        const { mount, missionId, toolbarSpacer, toolbar } = candidate || {};
        if (!mount?.isConnected || missionId === null) return null;
        const marker = getMissionMarkerIndex().byId.get(missionId) || getMissionMarkerIndex().byId.get(String(missionId)) || null;
        const snapshot = liveMissionSnapshots.get(missionId) || liveMissionSnapshots.get(String(missionId)) || missionSnapshotCache.get(missionId) || missionSnapshotCache.get(String(missionId)) || null;
        const details = criticalMissionValueDetails({ missionId, marker, snapshot });
        const formatted = formatMissionWindowValue(details.value);
        const existingRows = missionValueRowsForCandidate(candidate);
        if (!formatted) {
            existingRows.forEach(row => row.remove());
            return null;
        }

        observeMissionValueHost(candidate);
        const availableWidth = missionValueSpacerVisibleWidth(toolbarSpacer);
        const presentation = missionValuePresentation(availableWidth, formatted);
        const useToolbar = Boolean(toolbarSpacer?.isConnected && toolbar?.isConnected && presentation.mode !== 'fallback');
        const targetDocument = (useToolbar ? toolbarSpacer.ownerDocument : mount.ownerDocument) || document;
        let row = null;
        if (useToolbar) {
            row = existingRows.find(candidateRow => candidateRow.parentNode === toolbarSpacer) || null;
        } else if (toolbar?.parentNode) {
            row = existingRows.find(candidateRow => candidateRow.parentNode === toolbar.parentNode && candidateRow.previousElementSibling === toolbar) || null;
        }
        row ||= existingRows.find(candidateRow => candidateRow.ownerDocument === targetDocument) || null;
        existingRows.forEach(candidateRow => {
            if (candidateRow !== row) candidateRow.remove();
        });
        if (!row) row = targetDocument.createElement('div');
        row.className = 'mcms-mission-value-row';
        row.setAttribute('data-mcms-mission-value', 'true');
        row.dataset.mcmsMissionId = String(missionId);
        row.dataset.mcmsHost = useToolbar ? 'toolbar' : 'fallback';
        row.dataset.mcmsMode = useToolbar ? presentation.mode : 'fallback';

        let badges = [];
        try { badges = Array.from(row.querySelectorAll('.mcms-mission-value-badge')); } catch (err) {}
        const badge = badges.shift() || targetDocument.createElement('span');
        badges.forEach(extra => extra.remove());
        badge.className = 'mcms-mission-value-badge';
        if (badge.parentNode !== row) row.appendChild(badge);

        if (useToolbar) {
            if (row.parentNode !== toolbarSpacer) toolbarSpacer.appendChild(row);
        } else if (toolbar?.parentNode) {
            if (row.parentNode !== toolbar.parentNode || row.previousElementSibling !== toolbar) {
                toolbar.parentNode.insertBefore(row, toolbar.nextSibling);
            }
        } else if (row.parentNode !== mount || row !== mount.firstElementChild) {
            mount.insertBefore(row, mount.firstChild || null);
        }

        const fullLabel = `Mission Value · ${formatted}`;
        const text = useToolbar ? presentation.text : fullLabel;
        if (badge.textContent !== text) badge.textContent = text;
        badge.title = `${fullLabel} · ${details.source}`;
        badge.setAttribute('aria-label', fullLabel);
        row.setAttribute('aria-label', fullLabel);
        return row;
    }

    function scheduleMissionValueScan(delay = 80) {
        runtimeClearTimeout(missionValueScanTimer);
        missionValueScanTimer = runtimeSetTimeout(() => {
            missionValueScanTimer = null;
            scanMissionValueWindows();
        }, Math.max(0, Number(delay) || 0));
    }

        function scanMissionValueWindows() {
        if (!state.missionValue) {
            clearMissionValueIndicators();
            pruneMissionValueHostObservers(new Set());
            return;
        }
        let needsRetry = false;
        const activeRows = new Set();
        const activeSpacers = new Set();
        for (const candidate of missionValueWindowCandidates()) {
            if (candidate.toolbarSpacer?.isConnected) activeSpacers.add(candidate.toolbarSpacer);
            const renderedRow = syncMissionValueCandidate(candidate);
            if (renderedRow) {
                activeRows.add(renderedRow);
                missionValueRetryState.delete(candidate.mount);
                continue;
            }
            const previous = missionValueRetryState.get(candidate.mount);
            const attempts = previous?.missionId === candidate.missionId ? previous.attempts : 0;
            if (attempts < 3) {
                missionValueRetryState.set(candidate.mount, { missionId: candidate.missionId, attempts: attempts + 1 });
                needsRetry = true;
            }
        }
        for (const context of transportSweepDocumentContexts()) {
            try {
                context.doc.querySelectorAll?.('.mcms-mission-value-row').forEach(row => {
                    if (!activeRows.has(row)) row.remove();
                });
            } catch (err) {}
        }
        pruneMissionValueHostObservers(activeSpacers);
        if (needsRetry) runtimeSetTimeout(() => scheduleMissionValueScan(0), 650);
    }

        function ensureMissionValueDocumentStyle(doc) {
        if (!doc || doc === document) return;
        const styleId = 'mcms-mission-value-document-style';
        if (doc.getElementById?.(styleId)) return;
        const style = doc.createElement?.('style');
        if (!style) return;
        style.id = styleId;
        style.textContent = `
            .mcms-mission-value-row{display:flex!important;align-items:center!important;justify-content:flex-end!important;min-width:0!important;box-sizing:border-box!important;position:relative!important;z-index:2!important;pointer-events:none!important}
            #navbar-alarm-spacer>.mcms-mission-value-row,.mcms-mission-value-row[data-mcms-host="toolbar"]{flex:1 1 auto!important;width:100%!important;min-height:32px!important;margin:0!important;padding:0 3px 0 6px!important;clear:none!important;overflow:hidden!important}
            .mcms-mission-value-row[data-mcms-host="fallback"]{width:100%!important;min-height:30px!important;margin:0 0 6px 0!important;padding:4px 8px!important;clear:both!important;overflow:hidden!important}
            .mcms-mission-value-badge{display:inline-flex!important;align-items:center!important;justify-content:center!important;max-width:100%!important;min-width:0!important;min-height:24px!important;box-sizing:border-box!important;padding:4px 9px!important;border:1px solid rgba(235,190,64,.72)!important;border-radius:8px!important;background:linear-gradient(145deg,rgba(48,39,13,.96),rgba(19,21,24,.96))!important;color:#ffe59a!important;box-shadow:0 2px 8px rgba(0,0,0,.34)!important;font:900 11px/1.2 Arial,Helvetica,sans-serif!important;letter-spacing:.15px!important;text-align:right!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;pointer-events:none!important}
            .mcms-mission-value-row[data-mcms-mode="value"] .mcms-mission-value-badge{padding-left:7px!important;padding-right:7px!important}
            @media(max-width:767px){.mcms-mission-value-row[data-mcms-host="fallback"]{padding:4px 6px!important}.mcms-mission-value-badge{font-size:10px!important}}
        `;
        (doc.head || doc.documentElement)?.appendChild(style);
    }

    function clearMissionValueDocumentStyles() {
        for (const context of transportSweepDocumentContexts()) {
            if (context.doc === document) continue;
            try { context.doc.getElementById?.('mcms-mission-value-document-style')?.remove(); } catch (err) {}
        }
    }

    function observeMissionValueFrame(frame) {
        if (!frame || missionValueObservedFrames.has(frame)) return;
        missionValueObservedFrames.add(frame);
        const onLoad = () => scheduleMissionValueScan(40);
        frame.addEventListener('load', onLoad);
        runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
    }

        function observeMissionValueDocument(doc) {
        if (!doc) return;
        ensureMissionValueDocumentStyle(doc);
        if (missionValueObservedDocuments.has(doc)) return;
        missionValueObservedDocuments.add(doc);
        let frames = [];
        try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
        frames.forEach(observeMissionValueFrame);
        const root = doc.documentElement || doc.body;
        if (!root) return;
        const activitySelector = '#lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame, a[href*="/missions/"], form[action*="/missions/"], #navbar-alarm-spacer, #navbar-right-help-button, [id^="lssmv4-shareAlliancePost_alarm"], .navbar-header';
        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
            const relevant = mutations.some(mutation => Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(node => {
                if (node?.nodeType !== 1) return false;
                if (node.matches?.(activitySelector)) return true;
                return Boolean(node.querySelector?.(activitySelector));
            }));
            if (!relevant) return;
            try { doc.querySelectorAll('iframe, frame').forEach(observeMissionValueFrame); } catch (err) {}
            scheduleMissionValueScan(50);
        }));
        observer.observe(root, { childList: true, subtree: true });
    }

    function installMissionValueWindows() {
        if (!missionValueFeatureInstalled) {
            missionValueFeatureInstalled = true;
            runtimeOnCleanup(() => {
                runtimeClearTimeout(missionValueScanTimer);
                missionValueScanTimer = null;
                clearMissionValueIndicators();
                clearMissionValueDocumentStyles();
            });
        }
        for (const context of transportSweepDocumentContexts()) observeMissionValueDocument(context.doc);
        scheduleMissionValueScan(0);
        runtimeSetTimeout(() => scheduleMissionValueScan(0), 180);
        runtimeSetTimeout(() => scheduleMissionValueScan(0), 800);
    }

    function criticalMissionValueForEntry(entry) {
        return criticalMissionValueDetails(entry).value;
    }

    function criticalValueEligible(entry) {
        return selectedCriticalValueMode() === 'total' || Boolean(entry?.eligibleForCredits);
    }

    function criticalValueGroup(entries, predicate = () => true) {
        let total = 0;
        let known = 0;
        let unknown = 0;
        let eligible = 0;
        const seenMissionIds = new Set();
        const sources = new Map();
        for (const entry of entries) {
            if (!predicate(entry) || !criticalValueEligible(entry)) continue;
            const missionId = normaliseMissionId(entry?.missionId);
            if (missionId !== null && seenMissionIds.has(missionId)) continue;
            if (missionId !== null) seenMissionIds.add(missionId);
            if (entry?.eligibleForCredits) eligible += 1;
            const details = criticalMissionValueDetails(entry);
            const value = details.value;
            if (value === null || !Number.isFinite(Number(value))) {
                unknown += 1;
                continue;
            }
            total += Math.max(0, Number(value) || 0);
            known += 1;
            sources.set(details.source, (sources.get(details.source) || 0) + 1);
        }
        return { total: Math.round(total), known, unknown, eligible, count: seenMissionIds.size, sources };
    }

    function criticalValueDisplay(group) {
        if (!group?.known) return 'UNKNOWN';
        return `≈${formatOperationalCompactCredits(group.total)} CR`;
    }

    function criticalValueCoverage(group) {
        return `${group.known.toLocaleString('en-GB')} / ${(group.known + group.unknown).toLocaleString('en-GB')} valued`;
    }

    function criticalValueTitle(label, group) {
        const knownText = `${group.known.toLocaleString('en-GB')} valued mission${group.known === 1 ? '' : 's'}`;
        const unknownText = group.unknown ? ` · ${group.unknown.toLocaleString('en-GB')} value${group.unknown === 1 ? '' : 's'} unavailable` : '';
        return `${label}: approximately ${group.total.toLocaleString('en-GB')} credits from MissionChief average-credit data · ${knownText}${unknownText}`;
    }

    function criticalValuesHtml(allEntries, visibleEntries) {
        const scopedEntries = visibleEntries;
        const noScene = criticalValueGroup(scopedEntries, entry => Boolean(entry?.units?.known) && Math.max(0, Number(entry?.units?.onScene) || 0) === 0);
        const assistance = criticalValueGroup(scopedEntries, entry => criticalEntryPrimaryStatus(entry) === 'assistance');
        const visible = criticalValueGroup(scopedEntries);
        const mode = selectedCriticalValueMode();
        const showingText = `${mode === 'eligible' ? 'Eligible' : 'Total'} MissionChief average credits for ${visibleEntries.length.toLocaleString('en-GB')} currently visible mission${visibleEntries.length === 1 ? '' : 's'}`;
        const valueCard = (className, label, group) => `<div class="mcms-critical-value-card ${className}" title="${escapeHtml(criticalValueTitle(label, group))}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(criticalValueDisplay(group))}</strong><small>${escapeHtml(criticalValueCoverage(group))}</small></div>`;
        return `
            <div class="mcms-critical-values-label" title="${escapeHtml(showingText)}"><strong>MISSION</strong><span>VALUE</span></div>
            <div class="mcms-critical-value-mode" role="group" aria-label="Mission value mode">
                <button type="button" data-critical-value-mode="total" class="${mode === 'total' ? 'mcms-filter-active' : ''}" aria-pressed="${mode === 'total'}">TOTAL</button>
                <button type="button" data-critical-value-mode="eligible" class="${mode === 'eligible' ? 'mcms-filter-active' : ''}" aria-pressed="${mode === 'eligible'}">ELIGIBLE</button>
            </div>
            <div class="mcms-critical-values-grid">
                ${valueCard('mcms-value-no-scene', 'No Scene', noScene)}
                ${valueCard('mcms-value-assistance', 'Assistance', assistance)}
                ${valueCard('mcms-value-all', 'Visible Value', visible)}
            </div>
            <span class="mcms-critical-showing">SHOWING ${visibleEntries.length.toLocaleString('en-GB')} OF ${allEntries.length.toLocaleString('en-GB')} MISSIONS</span>`;
    }

    function criticalSummaryHtml(allEntries) {
        const baseForStatus = criticalFilterEntries(allEntries, ['status']);
        const baseForOnWay = criticalFilterEntries(allEntries, ['onway']);
        const baseForMyUnits = criticalFilterEntries(allEntries, ['myunits']);
        const statusCounts = { all: baseForStatus.length, attention: 0, 'no-scene': 0, assistance: 0, clearing: 0, 'on-scene': 0, syncing: 0 };
        for (const entry of baseForStatus) {
            const key = criticalEntryPrimaryStatus(entry);
            if (Object.prototype.hasOwnProperty.call(statusCounts, key)) statusCounts[key] += 1;
            if (key === 'no-scene' || key === 'assistance') statusCounts.attention += 1;
        }
        let onWayMissions = 0;
        let onWayVehicles = 0;
        for (const entry of baseForOnWay) {
            const count = Math.max(0, Number(entry?.units?.onWay ?? entry?.units?.travelling) || 0);
            if (count > 0) onWayMissions += 1;
            onWayVehicles += count;
        }
        const selectedStatus = selectedCriticalPrimaryStatus();
        const statusCard = (key, className, label, value, title = '') => {
            const active = selectedStatus === key;
            return `<button type="button" class="mcms-critical-summary-card mcms-critical-filter ${className}${active ? ' mcms-filter-active' : ''}" data-critical-primary-status="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title || `Show ${label} missions`)}"><span>${escapeHtml(label)}</span><strong>${Number(value).toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓' : ''}</i></button>`;
        };
        const onWayActive = Boolean(state.missionAgeWatch?.hasVehiclesOnWay);
        const myUnitsActive = Boolean(state.missionAgeWatch?.onlyMyUnits);
        return `
            <section class="mcms-critical-advanced-group">
                <div class="mcms-critical-advanced-group-head"><strong>MISSION CONDITION</strong><small>Select one condition</small></div>
                <div class="mcms-critical-advanced-status-grid">
                    ${statusCard('all', 'mcms-summary-aged', 'Any Status', statusCounts.all)}
                    ${statusCard('attention', 'mcms-summary-attention', 'Attention', statusCounts.attention, 'Show missions with no units on scene or detected assistance requirements')}
                    ${statusCard('no-scene', 'mcms-summary-no-scene', 'No Units', statusCounts['no-scene'])}
                    ${statusCard('assistance', 'mcms-summary-assistance', 'Assistance', statusCounts.assistance)}
                    ${statusCard('clearing', 'mcms-summary-clearing', 'Clearing', statusCounts.clearing)}
                    ${statusCard('on-scene', 'mcms-summary-on-scene', 'Stable', statusCounts['on-scene'])}
                </div>
            </section>
            <section class="mcms-critical-advanced-group">
                <div class="mcms-critical-advanced-group-head"><strong>UNIT SCOPE</strong><small>Optional additional requirements</small></div>
                <div class="mcms-critical-advanced-condition-grid">
                    <button type="button" class="mcms-critical-summary-card mcms-critical-filter mcms-summary-enroute${onWayActive ? ' mcms-filter-active' : ''}" data-critical-condition="onway" aria-pressed="${onWayActive ? 'true' : 'false'}" title="Require at least one Code 3 vehicle responding"><span>Vehicles On Way</span><strong>${onWayMissions.toLocaleString('en-GB')}</strong><small>${onWayVehicles.toLocaleString('en-GB')} vehicles</small><i aria-hidden="true">${onWayActive ? '✓' : ''}</i></button>
                    <button type="button" class="mcms-critical-summary-card mcms-critical-filter mcms-summary-my-units${myUnitsActive ? ' mcms-filter-active' : ''}" data-critical-condition="my-units" aria-pressed="${myUnitsActive ? 'true' : 'false'}" title="Show only missions with one of your units committed"><span>Only My Units</span><strong>${baseForMyUnits.filter(criticalEntryHasMyUnits).length.toLocaleString('en-GB')}</strong><i aria-hidden="true">${myUnitsActive ? '✓' : ''}</i></button>
                </div>
            </section>
            ${statusCounts.syncing ? `<div class="mcms-critical-summary-card mcms-summary-syncing" title="Vehicle data is still loading for these missions"><span>Syncing Data</span><strong>${statusCounts.syncing.toLocaleString('en-GB')}</strong></div>` : ''}`;
    }

    function nativeMissionCountdownText(missionId) {
        const id = normaliseMissionId(missionId);
        if (id === null) return '';
        const node = document.getElementById(`mission_overview_countdown_${id}`)
            || document.querySelector(`#mission_${id} [id^="mission_overview_countdown_"], #mission_${id} .mission_overview_countdown, #mission_${id} .mission-countdown`);
        const text = String(node?.textContent || '').replace(/\s+/g, ' ').trim();
        return text && !/^[-—]+$/u.test(text) ? text : '';
    }

    function formatMissionCountdown(ms) {
        const seconds = Math.max(0, Math.ceil(Number(ms) / 1000));
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = seconds % 60;
        if (hours > 0) return `${hours}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
        return `${minutes}:${String(remainingSeconds).padStart(2, '0')}`;
    }

    function normaliseMissionTimestampMs(value) {
        const number = Number(value);
        if (!Number.isFinite(number) || number <= 0) return null;
        return number < 100000000000 ? number * 1000 : number;
    }

    function missionGameNowMs(snapshot = null) {
        try {
            if (typeof pageWindow.unix_timestamp === 'function') {
                const value = Number(pageWindow.unix_timestamp());
                if (Number.isFinite(value) && value > 0) return value < 100000000000 ? value * 1000 : value;
            }
        } catch (err) {}
        const snapshotNow = normaliseMissionTimestampMs(snapshot?.dateNow);
        if (snapshotNow) {
            const capturedAt = normaliseMissionTimestampMs(snapshot?.dateNowUpdatedAt) || normaliseMissionTimestampMs(snapshot?.lastSeen);
            return capturedAt ? snapshotNow + Math.max(0, Date.now() - capturedAt) : snapshotNow;
        }
        return Date.now();
    }

    function clearingMissionCountdownText(entry) {
        const nativeText = nativeMissionCountdownText(entry?.missionId);
        if (nativeText) return nativeText;
        const snapshot = entry?.snapshot || liveMissionSnapshots.get(normaliseMissionId(entry?.missionId)) || {};
        const target = normaliseMissionTimestampMs(snapshot.dateEndCalc ?? snapshot.dateEnd);
        const now = missionGameNowMs(snapshot);
        if (target && target > now) return formatMissionCountdown(target - now);
        return 'SYNCING';
    }

    function refreshCriticalClearingCountdowns() {
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (!drawer?.classList.contains('mcms-open')) return;
        for (const node of drawer.querySelectorAll('[data-critical-clearing-countdown]')) {
            const missionId = normaliseMissionId(node.getAttribute('data-critical-clearing-countdown'));
            if (missionId === null) continue;
            const nativeText = nativeMissionCountdownText(missionId);
            const snapshot = liveMissionSnapshots.get(missionId) || missionOverlayData.get(missionId) || {};
            const target = normaliseMissionTimestampMs(snapshot.dateEndCalc ?? snapshot.dateEnd);
            const now = missionGameNowMs(snapshot);
            const text = nativeText || (target && target > now ? formatMissionCountdown(target - now) : 'SYNCING');
            node.textContent = `⌛ ${text}`;
            node.title = `Estimated time until mission completion: ${text}`;
        }
    }

    function refreshCriticalDistanceNodes() {
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (!drawer?.classList.contains('mcms-open')) return;
        const reference = criticalMissionDistanceReference();
        if (!reference) return;
        for (const row of drawer.querySelectorAll('[data-mission-id]')) {
            const missionId = normaliseMissionId(row.getAttribute('data-mission-id'));
            if (missionId === null) continue;
            const snapshot = liveMissionSnapshots.get(missionId) || {};
            const marker = snapshot.marker || getMissionMarkerIndex().byId.get(missionId) || null;
            const entry = { lat: snapshot.lat, lng: snapshot.lng, marker };
            if ((!Number.isFinite(Number(entry.lat)) || !Number.isFinite(Number(entry.lng))) && marker?.getLatLng) {
                try { const latLng = marker.getLatLng(); entry.lat = latLng.lat; entry.lng = latLng.lng; } catch (err) {}
            }
            const text = formatCriticalDistance(criticalEntryDistanceMiles(entry, reference));
            const node = row.querySelector('.mcms-critical-distance');
            if (node && text) {
                node.textContent = text;
                node.title = `Distance from ${reference.label || 'selected origin'}`;
            }
        }
    }

    function criticalDataQualityHtml(entry) {
        const badges = [];
        if (!entry?.dataQuality?.unitsKnown) badges.push('<span class="mcms-critical-data-badge mcms-data-sync">UNIT DATA PENDING</span>');
        if (!entry?.dataQuality?.ageKnown) badges.push('<span class="mcms-critical-data-badge mcms-data-unknown">AGE N/A</span>');
        if (!entry?.dataQuality?.valueKnown) badges.push('<span class="mcms-critical-data-badge mcms-data-unknown">VALUE N/A</span>');
        if (!entry?.dataQuality?.locationKnown) badges.push('<span class="mcms-critical-data-badge mcms-data-unknown">LOCATION N/A</span>');
        else if (!entry?.dataQuality?.areaKnown) badges.push('<span class="mcms-critical-data-badge mcms-data-unknown">AREA N/A</span>');
        return badges.join('');
    }

    function criticalAuxiliaryUnitHtml(units) {
        const chips = [];
        const add = (value, label, className) => {
            const count = Math.max(0, Number(value) || 0);
            if (count > 0) chips.push(`<span class="mcms-critical-unit-extra ${className}"><strong>${count}</strong><small>${escapeHtml(label)}</small></span>`);
        };
        add(units?.transporting, 'TRANSPORTING', 'mcms-unit-transporting');
        add(units?.awaitingPickup, 'AWAITING PICKUP', 'mcms-unit-awaiting');
        add(units?.requestingDispatch, 'REQUESTING', 'mcms-unit-requesting');
        add(units?.outOfService, 'OUT OF SERVICE', 'mcms-unit-oos');
        return chips.length ? `<span class="mcms-critical-unit-extras">${chips.join('')}</span>` : '';
    }

    function renderCriticalDrawer(entries = null, options = {}) {
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (!drawer || !drawer.classList.contains('mcms-open')) return;
        const list = drawer.querySelector('.mcms-drawer-list');
        const summary = drawer.querySelector('[data-critical-summary]');
        const values = drawer.querySelector('[data-critical-values]');
        const ownershipFilters = drawer.querySelector('[data-critical-type-filters]');
        const categoryFilters = drawer.querySelector('[data-critical-category-filters]');
        const filterOverview = drawer.querySelector('[data-critical-filter-overview]');
        const quickViews = drawer.querySelector('[data-critical-quick-views]');
        const advancedSummary = drawer.querySelector('[data-critical-advanced-summary]');
        const ageFilters = drawer.querySelector('[data-critical-age-filters]');
        const sortControls = drawer.querySelector('[data-critical-sort-controls]');
        const viewSummary = drawer.querySelector('[data-critical-view-summary]');
        const viewToggle = drawer.querySelector('[data-critical-view-toggle]');
        const refreshed = drawer.querySelector('[data-critical-refreshed]');
        if (!list || !summary || !values || !ownershipFilters || !categoryFilters || !filterOverview || !quickViews || !advancedSummary || !ageFilters || !sortControls || !refreshed) return;

        const previousScrollTop = list.scrollTop;
        const allEntries = Array.isArray(entries) ? entries : getCriticalMissionEntries(0, CRITICAL_OWNERSHIP_KEYS);
        const visibleEntries = sortCriticalEntries(criticalFilterEntries(allEntries));
        const renderedEntries = visibleEntries.slice(0, Math.max(CRITICAL_RENDER_BATCH_SIZE, criticalDrawerRenderLimit));
        criticalDrawerLastViewUpdatedAt = options.updateViewTime === false && criticalDrawerLastViewUpdatedAt ? criticalDrawerLastViewUpdatedAt : Date.now();
        const syncAt = Math.max(criticalDrawerLastDataSyncAt, missionProgressPageLastSuccessAt, vehicleApiLastFetch, vehicleStatusLastUpdate);
        const syncText = syncAt ? formatRefreshClockTime(syncAt) : 'PENDING';
        refreshed.innerHTML = `<span>DATA SYNC ${escapeHtml(syncText)}</span><span>VIEW ${escapeHtml(formatRefreshClockTime(criticalDrawerLastViewUpdatedAt))}</span>`;
        refreshed.title = syncAt ? `Latest live data: ${new Date(syncAt).toLocaleString()} · View updated: ${new Date(criticalDrawerLastViewUpdatedAt).toLocaleString()}` : 'Waiting for the first live data synchronisation';

        const html = renderedEntries.length ? renderedEntries.map(entry => {
            const operational = entry.operationalState || criticalMissionOperationalState(entry.units, entry.snapshot, entry.stuckRecord);
            const clearingProgress = operational.key === 'clearing' ? Math.max(0, Math.min(100, Number(operational.progress) || 0)) : 0;
            const clearingStyle = operational.key === 'clearing' ? ` style="--mcms-clearing-progress:${clearingProgress}%;"` : '';
            const patientCount = Math.max(0, Math.round(Number(entry.snapshot?.patientsCount) || 0));
            const prisonerCount = Math.max(0, Math.round(Number(entry.snapshot?.prisonersCount) || 0));
            const patientHtml = patientCount > 0 ? `<span class="mcms-critical-patients" title="${patientCount.toLocaleString('en-GB')} live patient${patientCount === 1 ? '' : 's'}"><span class="mcms-patient-icon" aria-hidden="true">✚</span><strong>${patientCount.toLocaleString('en-GB')}</strong><small>PATIENT${patientCount === 1 ? '' : 'S'}</small></span>` : '';
            const prisonerHtml = prisonerCount > 0 ? `<span class="mcms-critical-prisoners" title="${prisonerCount.toLocaleString('en-GB')} live prisoner${prisonerCount === 1 ? '' : 's'}"><span aria-hidden="true">⌁</span><strong>${prisonerCount.toLocaleString('en-GB')}</strong><small>PRISONER${prisonerCount === 1 ? '' : 'S'}</small></span>` : '';
            const countdownHtml = operational.key === 'clearing' ? `<span class="mcms-critical-clear-countdown" data-critical-clearing-countdown="${escapeHtml(entry.missionId)}" title="Estimated time until mission completion">⌛ ${escapeHtml(clearingMissionCountdownText(entry))}</span>` : '';
            const locationParts = [];
            if (entry.area) locationParts.push(`<span class="mcms-critical-city mcms-critical-area">${escapeHtml(entry.area)}</span>`);
            if (entry.postcode) locationParts.push(`<span class="mcms-critical-postcode">${escapeHtml(entry.postcode)}</span>`);
            const distanceText = formatCriticalDistance(entry.distanceMi);
            if (distanceText) locationParts.push(`<span class="mcms-critical-distance" title="Distance from ${escapeHtml(entry.distanceOriginLabel || 'selected origin')}">${escapeHtml(distanceText)}</span>`);
            const locationHtml = locationParts.length ? `<span class="mcms-critical-location" title="${escapeHtml(entry.address || [entry.area, entry.postcode].filter(Boolean).join(', '))}">${locationParts.join('')}</span>` : '';
            const specialEventHtml = entry.specialEvent?.active ? `<span class="mcms-critical-special-event" title="Official MissionChief developer-launched event${entry.specialEvent.eventId ? ` · Event ${escapeHtml(entry.specialEvent.eventId)}` : ''}"><span aria-hidden="true">★</span>${escapeHtml(entry.specialEvent.label || 'SPECIAL EVENT')}</span>` : '';
            const hasEnrouteClass = Math.max(0, Number(entry.units?.onWay ?? entry.units?.travelling) || 0) > 0 ? ' mcms-critical-has-enroute' : '';
            const specialEventClass = entry.specialEvent?.active ? ' mcms-critical-developer-event' : '';
            const eligibilityHtml = entry.ownership === 'alliance' ? `<span class="mcms-critical-eligibility ${entry.eligibleForCredits ? 'mcms-eligible' : 'mcms-not-eligible'}">${entry.eligibleForCredits ? 'ELIGIBLE' : 'NO UNIT'}</span>` : '';
            const ageText = Number.isFinite(entry.missionAge) ? formatElapsedCompact(entry.missionAge) : 'N/A';
            return `
            <article class="mcms-critical-row ${escapeHtml(entry.severity.className)} mcms-critical-state-${escapeHtml(operational.key)} mcms-critical-ownership-${escapeHtml(entry.ownership)} mcms-critical-category-${escapeHtml(entry.category)}${hasEnrouteClass}${specialEventClass}" role="group" data-mission-id="${escapeHtml(entry.missionId)}" data-critical-state="${escapeHtml(operational.key)}" data-mission-ownership="${escapeHtml(entry.ownership)}" data-mission-category="${escapeHtml(entry.category)}"${clearingStyle} aria-label="${escapeHtml(entry.caption)} mission status">
                <span class="mcms-critical-topline">
                    <span class="mcms-critical-top-identifiers"><span class="mcms-critical-age-band">${escapeHtml(entry.severity.label)}</span><span class="mcms-critical-type-badge mcms-type-${escapeHtml(entry.ownership)}${entry.ownership === 'alliance' ? ' mcms-alliance-text' : ''}">${escapeHtml(missionWatchOwnershipLabel(entry.ownership))}</span><span class="mcms-critical-category-badge mcms-category-${escapeHtml(entry.category)}">${escapeHtml(missionWatchCategoryLabel(entry.category))}</span>${specialEventHtml}${eligibilityHtml}${locationHtml}${criticalDataQualityHtml(entry)}</span>
                    <span class="mcms-critical-top-actions">${countdownHtml}<span class="mcms-critical-age">${escapeHtml(ageText)}</span><button class="mcms-critical-zoom" type="button" data-zoom-mission-id="${escapeHtml(entry.missionId)}" title="Zoom to ${escapeHtml(entry.caption)}" aria-label="Zoom to ${escapeHtml(entry.caption)}"><span aria-hidden="true">⌖</span> Zoom</button><button class="mcms-critical-open" type="button" data-open-mission-id="${escapeHtml(entry.missionId)}" title="Open ${escapeHtml(entry.caption)}" aria-label="Open ${escapeHtml(entry.caption)}"><span aria-hidden="true">↗</span> Open</button></span>
                </span>
                <span class="mcms-critical-titleline"><span class="mcms-critical-name">${escapeHtml(entry.caption)}</span><span class="mcms-critical-live-markers">${patientHtml}${prisonerHtml}</span></span>
                <span class="mcms-critical-lowerline">
                    <span class="mcms-critical-state"><span class="mcms-critical-state-signal" aria-hidden="true"></span><span class="mcms-critical-state-copy"><strong>${escapeHtml(operational.label)}</strong><small>${escapeHtml(operational.detail)}</small></span></span>
                    <span class="mcms-critical-unit-grid"><span class="mcms-critical-unit-chip mcms-unit-scene"><strong>${Math.max(0, Number(entry.units?.onScene) || 0)}</strong><small>ON SCENE</small></span><span class="mcms-critical-unit-chip mcms-unit-way"><strong>${Math.max(0, Number(entry.units?.onWay ?? entry.units?.travelling) || 0)}</strong><small>ON WAY</small></span></span>
                    ${criticalAuxiliaryUnitHtml(entry.units)}
                </span>
            </article>`;
        }).join('') : allEntries.length ? '<div class="mcms-empty-state">No missions match the selected ownership, category, age and operational filters. Use Clear to reset the watcher.</div>' : '<div class="mcms-empty-state">No missions are currently available.</div>';

        const remaining = Math.max(0, visibleEntries.length - renderedEntries.length);
        const footer = remaining > 0 ? `<div class="mcms-critical-list-footer"><span>Showing ${renderedEntries.length.toLocaleString('en-GB')} of ${visibleEntries.length.toLocaleString('en-GB')}</span><button type="button" data-critical-load-more>Load ${Math.min(CRITICAL_RENDER_BATCH_SIZE, remaining).toLocaleString('en-GB')} more</button></div>` : '';
        const baseSignature = renderedEntries.map(entry => `${entry.missionId}:${entry.ownership}:${entry.category}:${Math.floor((entry.missionAge || 0) / 60000)}:${entry.units.onScene}:${entry.units.onWay}:${entry.units.known}:${Number(entry.snapshot?.patientsCount) || 0}:${Number(entry.snapshot?.prisonersCount) || 0}:${criticalMissionValueForEntry(entry) ?? 'unknown'}:${entry.operationalState?.key}:${entry.operationalState?.detail}:${entry.area || ''}:${entry.postcode || ''}:${Number.isFinite(entry.distanceMi) ? Number(entry.distanceMi).toFixed(2) : ''}`).join('|');
        const allSignature = allEntries.map(entry => `${entry.missionId}:${entry.ownership}:${entry.category}:${Math.floor((entry.missionAge || 0) / 60000)}:${entry.operationalState?.key}`).join('|');
        const stateSignature = JSON.stringify(state.missionAgeWatch || {});
        setInnerHtmlIfChanged(ageFilters, criticalAgeFiltersHtml(allEntries), `critical-ages:${allSignature}:${stateSignature}`);
        setInnerHtmlIfChanged(sortControls, criticalSortControlsHtml(), `critical-sort:${stateSignature}:${state.bookmarks.map(item => item?.name || '').join('|')}`);
        const viewSummaryText = criticalViewControlsSummary(allEntries);
        if (viewSummary && viewSummary.textContent !== viewSummaryText) viewSummary.textContent = viewSummaryText;
        if (viewToggle) {
            viewToggle.title = `Open age, sort and distance-origin controls · ${viewSummaryText}`;
            viewToggle.setAttribute('aria-label', `Open Mission Age Watch view controls · ${viewSummaryText}`);
        }
        setInnerHtmlIfChanged(values, criticalValuesHtml(allEntries, visibleEntries), `critical-values:${allSignature}:${stateSignature}`);
        setInnerHtmlIfChanged(ownershipFilters, criticalOwnershipFiltersHtml(allEntries), `critical-ownership:${allSignature}:${stateSignature}`);
        setInnerHtmlIfChanged(filterOverview, criticalFilterOverviewHtml(allEntries, visibleEntries), `critical-overview:${allSignature}:${visibleEntries.length}:${stateSignature}`);
        setInnerHtmlIfChanged(quickViews, criticalQuickViewsHtml(allEntries), `critical-quick:${allSignature}:${stateSignature}`);
        setInnerHtmlIfChanged(categoryFilters, criticalCategoryFiltersHtml(allEntries), `critical-category:${allSignature}:${stateSignature}`);
        setInnerHtmlIfChanged(summary, criticalSummaryHtml(allEntries), `critical-summary:${allSignature}:${stateSignature}`);
        advancedSummary.textContent = criticalAdvancedFilterSummaryText();
        setCriticalAdvancedFiltersOpen(Boolean(state.missionAgeWatch?.advancedFiltersOpen), drawer);
        setInnerHtmlIfChanged(list, html + footer, `drawer:${baseSignature}:${visibleEntries.length}:${criticalDrawerRenderLimit}:${stateSignature}`);
        if (options.preserveScroll) list.scrollTop = previousScrollTop;
        updateCriticalDrawerExpandButton(drawer);
        runtimeSetTimeout(refreshCriticalClearingCountdowns, 0);
    }

    async function refreshCriticalDrawer(showFeedback = false) {
        if (criticalDrawerRefreshing) return false;
        const drawer = createCriticalDrawer();
        const refreshButton = drawer.querySelector('.mcms-drawer-refresh');
        criticalDrawerRefreshing = true;
        drawer.classList.add('mcms-critical-refreshing');
        if (refreshButton) refreshButton.disabled = true;
        try {
            const [vehicleRefreshSucceeded, missionProgressRefreshed] = await Promise.all([
                refreshPersonalVehicleData(true),
                refreshMissionProgressFromPage(true, 0)
            ]);
            refreshMissionSnapshots();
            applyCriticalViewFilter();
            scheduleMissionAgeRefresh(0);
            scheduleUnitCommitmentRefresh(0);
            if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(0);
            if (vehicleRefreshSucceeded || missionProgressRefreshed) criticalDrawerLastDataSyncAt = Date.now();
            resetCriticalVirtualWindow(drawer, false);
            renderOperationalPanels(true, { updateViewTime: true, preserveScroll: true });
            if (showFeedback) {
                const message = missionProgressRefreshed && vehicleRefreshSucceeded
                    ? 'Mission Age Watch live data refreshed'
                    : missionProgressRefreshed
                        ? 'Mission progress refreshed · vehicle data cached'
                        : vehicleRefreshSucceeded
                            ? 'Vehicle data refreshed · mission progress cached'
                            : 'Mission Age Watch redrawn from cached data';
                showToast(message);
            }
            return vehicleRefreshSucceeded || missionProgressRefreshed;
        } catch (err) {
            if (showFeedback) showToast('Mission Age Watch refresh failed');
            return false;
        } finally {
            criticalDrawerRefreshing = false;
            drawer.classList.remove('mcms-critical-refreshing');
            if (refreshButton) refreshButton.disabled = false;
        }
    }

    function closeCriticalDrawer() {
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (!drawer) return;
        runtimeClearTimeout(criticalDrawerDockTimer);
        criticalDrawerDockTimer = null;
        drawer.classList.remove('mcms-open');
        drawer.setAttribute('aria-hidden', 'true');
        clearCriticalDrawerDock(drawer);
        updateUI();
    }

    function toggleCriticalDrawer() {
        const drawer = createCriticalDrawer();
        const opening = !drawer.classList.contains('mcms-open');
        if (!opening) {
            closeCriticalDrawer();
            return;
        }
        closeVehicleCodeStatus();
        drawer.classList.add('mcms-open');
        drawer.setAttribute('aria-hidden', 'false');
        updateCriticalDrawerExpandButton(drawer);
        resetCriticalVirtualWindow(drawer, false);
        renderCriticalDrawer(null, { updateViewTime: true });
        refreshPersonalVehicleData(false).then(refreshed => {
            if (!refreshed || !drawer.classList.contains('mcms-open')) return;
            refreshMissionSnapshots();
            criticalDrawerLastDataSyncAt = Math.max(criticalDrawerLastDataSyncAt, vehicleApiLastFetch, vehicleStatusLastUpdate);
            renderOperationalPanels(true, { updateViewTime: false, preserveScroll: true });
        });
        positionCriticalDrawerOverMissionList();
        scheduleCriticalDrawerDock(140);
        updateUI();
        runtimeSetTimeout(() => drawer.querySelector('.mcms-drawer-close')?.focus?.(), 0);
    }

    function missionLockOnReducedMotion() {
        try { return Boolean(pageWindow.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches); }
        catch (err) { return false; }
    }

    function missionLockOnThemeLabel() {
        const labels = {
            mapCommand: 'MISSION LOCKED',
            cyberpunk: 'SIGNAL ACQUIRED',
            fallout4: 'TARGET ACQUIRED',
            umbrella: 'INCIDENT LOCKED',
            factorio: 'COORDINATES LOCKED'
        };
        return labels[state.uiTheme] || labels.mapCommand;
    }

    function playMissionLockTrackingSound() {
        if (!state.missionLockAudio) return false;
        const context = unlockPayoutAudio(true);
        if (!context) return false;
        try {
            const now = context.currentTime + 0.012;
            const master = context.createGain();
            master.gain.setValueAtTime(0.0001, now);
            master.gain.exponentialRampToValueAtTime(0.075, now + 0.025);
            master.gain.exponentialRampToValueAtTime(0.0001, now + 1.08);
            master.connect(context.destination);

            connectAudioNoise(context, master, { start: now, duration: 0.075, gain: 0.11, filterFrequency: 1800 });
            const tracking = [
                [0.04, 620, 0.055, 'square', 0.09, 810],
                [0.20, 760, 0.050, 'square', 0.08, 980],
                [0.36, 920, 0.050, 'square', 0.075, 1180],
                [0.52, 1120, 0.048, 'square', 0.07, 1420]
            ];
            for (const [delay, frequency, duration, type, gain, endFrequency] of tracking) {
                connectAudioTone(context, master, {
                    start: now + delay,
                    duration,
                    frequency,
                    endFrequency,
                    type,
                    gain
                });
            }
            connectAudioTone(context, master, {
                start: now + 0.70,
                duration: 0.22,
                frequency: 1480,
                endFrequency: 1960,
                type: 'sine',
                gain: 0.10
            });
            connectAudioTone(context, master, {
                start: now + 0.90,
                duration: 0.16,
                frequency: 980,
                endFrequency: 980,
                type: 'triangle',
                gain: 0.13
            });
            return true;
        } catch (err) {
            return false;
        }
    }

    function clearMissionLockOnEffect() {
        missionLockOnToken += 1;
        runtimeClearTimeout(missionLockOnTimer);
        missionLockOnTimer = null;
        if (missionLockOnMoveEndMap && missionLockOnMoveEndHandler) {
            try { missionLockOnMoveEndMap.off?.('moveend', missionLockOnMoveEndHandler); } catch (err) {}
        }
        missionLockOnMoveEndMap = null;
        missionLockOnMoveEndHandler = null;
        if (missionLockOnTravelOverlay) {
            try { missionLockOnTravelOverlay.remove(); } catch (err) {}
            missionLockOnTravelOverlay = null;
        }
        if (missionLockOnMarker) {
            try { missionLockOnMarker.remove?.(); } catch (err) {
                try { missionLockOnMarker._map?.removeLayer?.(missionLockOnMarker); } catch (nestedError) {}
            }
            missionLockOnMarker = null;
        }
        if (missionLockOnTargetIcon?.classList) {
            missionLockOnTargetIcon.classList.remove('mcms-mission-lock-target', 'mcms-critical-view-focus');
        }
        missionLockOnTargetIcon = null;
    }

    function createMissionLockOnTravelOverlay(map) {
        const container = map?.getContainer?.();
        if (!container) return null;
        const overlay = document.createElement('div');
        overlay.className = 'mcms-mission-lock-travel-overlay';
        overlay.setAttribute('aria-hidden', 'true');
        container.appendChild(overlay);
        missionLockOnTravelOverlay = overlay;
        return overlay;
    }

    function resolveMissionLockOnMarker(marker, missionId) {
        const id = normaliseMissionId(missionId);
        if (id !== null) {
            const current = getMissionMarkerIndex().byId.get(id) || null;
            if (current && !isToolkitLeafletLayer(current)) return current;
        }
        return marker;
    }

    function missionLockOnContainerPoint(map, marker, fallbackLatLng) {
        const mapContainer = map?.getContainer?.();
        if (!mapContainer) return null;
        const activeMarker = resolveMissionLockOnMarker(marker, normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId));
        const icon = activeMarker?._icon;
        try {
            const mapRect = mapContainer.getBoundingClientRect();
            if (icon?.isConnected) {
                const iconRect = icon.getBoundingClientRect();
                if (mapRect.width > 0 && mapRect.height > 0 && iconRect.width > 1 && iconRect.height > 1) {
                    const x = iconRect.left - mapRect.left + iconRect.width / 2;
                    const y = iconRect.top - mapRect.top + iconRect.height / 2;
                    if (x >= -80 && y >= -80 && x <= mapRect.width + 80 && y <= mapRect.height + 80) return { x, y, marker: activeMarker };
                }
            }
            const markerLatLng = activeMarker?.getLatLng?.() || fallbackLatLng;
            if (markerLatLng && typeof map.latLngToContainerPoint === 'function') {
                const point = map.latLngToContainerPoint(markerLatLng);
                if (Number.isFinite(Number(point?.x)) && Number.isFinite(Number(point?.y))) return { x: Number(point.x), y: Number(point.y), marker: activeMarker };
            }
        } catch (err) {}
        return null;
    }

    function positionMissionLockOnDom(map, marker, fallbackLatLng, element) {
        if (!element?.isConnected) return null;
        const point = missionLockOnContainerPoint(map, marker, fallbackLatLng);
        if (!point) return null;
        element.style.setProperty('--mcms-lock-x', `${point.x}px`, 'important');
        element.style.setProperty('--mcms-lock-y', `${point.y}px`, 'important');
        return point.marker;
    }

    function createMissionLockOnReticle(map, marker, missionId, latLng, token) {
        if (token !== missionLockOnToken || !map || !latLng) return false;
        if (missionLockOnTravelOverlay) {
            try { missionLockOnTravelOverlay.remove(); } catch (err) {}
            missionLockOnTravelOverlay = null;
        }

        const activeMarker = resolveMissionLockOnMarker(marker, missionId);
        const caption = getMissionCaption(activeMarker, missionId) || getMissionCaption(marker, missionId) || 'Mission incident';
        const shortCaption = caption.length > 38 ? `${caption.slice(0, 35).trim()}…` : caption;
        const label = missionLockOnThemeLabel();
        const mapContainer = map?.getContainer?.();
        if (!mapContainer) return false;

        if (activeMarker?._icon?.classList) {
            missionLockOnTargetIcon = activeMarker._icon;
            activeMarker._icon.classList.add('mcms-mission-lock-target', 'mcms-critical-view-focus');
        }

        const lockElement = document.createElement('div');
        lockElement.className = 'mcms-mission-lock-dom';
        lockElement.setAttribute('aria-hidden', 'true');
        lockElement.innerHTML = `<div class="mcms-mission-lock-intel">
            <span class="mcms-mission-lock-beam mcms-mission-lock-beam-left"></span>
            <span class="mcms-mission-lock-beam mcms-mission-lock-beam-right"></span>
            <span class="mcms-mission-lock-beam mcms-mission-lock-beam-top"></span>
            <span class="mcms-mission-lock-beam mcms-mission-lock-beam-bottom"></span>
            <div class="mcms-mission-lock-reticle">
                <span class="mcms-mission-lock-radar"></span>
                <span class="mcms-mission-lock-bracket mcms-mission-lock-bracket-a"></span>
                <span class="mcms-mission-lock-bracket mcms-mission-lock-bracket-b"></span>
                <span class="mcms-mission-lock-bracket mcms-mission-lock-bracket-c"></span>
                <span class="mcms-mission-lock-bracket mcms-mission-lock-bracket-d"></span>
                <span class="mcms-mission-lock-crosshair"></span>
                <span class="mcms-mission-lock-dot"></span>
                <span class="mcms-mission-lock-scan"></span>
                <span class="mcms-mission-lock-label"><strong>${escapeHtml(label)}</strong><small>${escapeHtml(shortCaption)}</small></span>
            </div>
        </div>`;
        mapContainer.appendChild(lockElement);
        missionLockOnMarker = lockElement;

        const updatePosition = () => {
            if (token !== missionLockOnToken || missionLockOnMarker !== lockElement || !lockElement.isConnected) return;
            const latestMarker = positionMissionLockOnDom(map, resolveMissionLockOnMarker(activeMarker, missionId), latLng, lockElement);
            if (latestMarker?._icon?.classList && latestMarker._icon !== missionLockOnTargetIcon) {
                missionLockOnTargetIcon?.classList?.remove('mcms-mission-lock-target', 'mcms-critical-view-focus');
                missionLockOnTargetIcon = latestMarker._icon;
                latestMarker._icon.classList.add('mcms-mission-lock-target', 'mcms-critical-view-focus');
            }
        };
        updatePosition();
        runtimeRequestAnimationFrame(() => runtimeRequestAnimationFrame(updatePosition));
        runtimeSetTimeout(updatePosition, 80);
        runtimeSetTimeout(updatePosition, 180);
        runtimeSetTimeout(updatePosition, 360);

        missionLockOnTimer = runtimeSetTimeout(() => {
            if (token !== missionLockOnToken) return;
            if (missionLockOnMarker) {
                try { missionLockOnMarker.remove?.(); } catch (err) {}
                missionLockOnMarker = null;
            }
            if (missionLockOnTargetIcon?.classList) {
                missionLockOnTargetIcon.classList.remove('mcms-mission-lock-target', 'mcms-critical-view-focus');
            }
            missionLockOnTargetIcon = null;
            missionLockOnTimer = null;
        }, missionLockOnReducedMotion() ? 1500 : 3300);
        return true;
    }

    function animateMissionFocus(marker, missionId, latLng, map) {
        clearMissionLockOnEffect();
        playMissionLockTrackingSound();
        const token = missionLockOnToken;
        const reducedMotion = missionLockOnReducedMotion();
        const currentZoom = Math.max(0, Number(map?.getZoom?.()) || 0);
        const targetZoom = Math.min(17, Math.max(currentZoom, 14));
        const travelDuration = reducedMotion ? 0 : 900;

        if (!reducedMotion) createMissionLockOnTravelOverlay(map);
        try {
            if (!reducedMotion && typeof map.flyTo === 'function') {
                map.flyTo(latLng, targetZoom, { duration: travelDuration / 1000, easeLinearity: 0.18 });
            } else {
                map.setView(latLng, targetZoom, { animate: false });
            }
        } catch (err) {
            try { map.setView(latLng, targetZoom); } catch (nestedError) {}
        }

        let completed = false;
        const finishLockOn = () => {
            if (completed) return;
            completed = true;
            if (missionLockOnMoveEndMap === map && missionLockOnMoveEndHandler === finishLockOn) {
                try { map.off?.('moveend', finishLockOn); } catch (err) {}
                missionLockOnMoveEndMap = null;
                missionLockOnMoveEndHandler = null;
            }
            runtimeClearTimeout(missionLockOnTimer);
            missionLockOnTimer = null;
            if (token !== missionLockOnToken) return;
            runtimeRequestAnimationFrame(() => runtimeRequestAnimationFrame(() => runtimeRequestAnimationFrame(() => {
                if (token === missionLockOnToken) createMissionLockOnReticle(map, resolveMissionLockOnMarker(marker, missionId), missionId, latLng, token);
            })));
        };

        if (!reducedMotion && typeof map.once === 'function') {
            missionLockOnMoveEndMap = map;
            missionLockOnMoveEndHandler = finishLockOn;
            try { map.once('moveend', finishLockOn); } catch (err) {}
        }
        missionLockOnTimer = runtimeSetTimeout(finishLockOn, reducedMotion ? 20 : travelDuration + 420);
        return true;
    }

    function focusMissionById(missionId, openMission = false) {
        const id = normaliseMissionId(missionId);
        const marker = getMissionMarkerIndex().byId.get(id) || null;
        if (!marker) { showToast('Mission is no longer available'); return false; }
        let latLng = null;
        try { latLng = marker.getLatLng?.() || null; } catch (err) {}
        const map = findLeafletMapInstance(false);
        if (map && latLng) animateMissionFocus(marker, id, latLng, map);
        else if (marker._icon?.classList) {
            marker._icon.classList.add('mcms-critical-view-focus');
            runtimeSetTimeout(() => marker._icon?.classList?.remove('mcms-critical-view-focus'), 1800);
        }
        if (openMission) {
            try {
                if (typeof pageWindow.lightboxOpen === 'function') pageWindow.lightboxOpen(`/missions/${id}`);
                else pageWindow.location.href = `/missions/${id}`;
            } catch (err) {}
        }
        return true;
    }

    function applyCriticalViewFilter() {
        const now = Date.now();
        for (const marker of getMissionMarkerLayers()) {
            if (!marker?._icon?.classList) continue;
            const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
            if (!criticalViewActive || missionId === null || !isPersonalMissionLayer(marker, missionId)) {
                marker._icon.classList.remove('mcms-critical-view-hidden');
                continue;
            }
            const ageRecord = personalMissionAgeRecord(marker, missionId, now);
            marker._icon.classList.toggle('mcms-critical-view-hidden', !ageRecord || ageRecord.ageMs < CRITICAL_VIEW_MIN_AGE_MS);
        }
    }

    function fitCriticalMissions() {
        const entries = getCriticalMissionEntries(CRITICAL_VIEW_MIN_AGE_MS);
        const map = findLeafletMapInstance(false);
        if (!map || !entries.length) return false;
        const points = entries.map(entry => {
            try { return entry.marker.getLatLng?.(); } catch (err) { return null; }
        }).filter(Boolean);
        if (!points.length) return false;
        try {
            map.invalidateSize?.({ pan: false });
            if (points.length === 1) map.setView(points[0], Math.max(Number(map.getZoom?.()) || 0, 13));
            else map.fitBounds(pageWindow.L.latLngBounds(points), { padding: [54, 54], maxZoom: 14 });
            return true;
        } catch (err) { return false; }
    }

    async function toggleCriticalView() {
        if (criticalViewLoading) return;

        if (criticalViewActive) {
            const previousView = criticalViewSnapshot?.mapView;
            criticalViewActive = false;
            if (criticalViewSnapshot) {
                state.visibility = { ...state.visibility, ...criticalViewSnapshot.visibility };
                state.allianceCredits = criticalViewSnapshot.allianceCredits;
                state.missionAge = criticalViewSnapshot.missionAge;
                state.transportWatcher = criticalViewSnapshot.transportWatcher !== false;
                state.unitCommitment = criticalViewSnapshot.unitCommitment;
            }
            criticalViewSnapshot = null;
            document.querySelectorAll('.mcms-critical-view-hidden').forEach(icon => icon.classList.remove('mcms-critical-view-hidden'));
            const criticalDrawer = document.getElementById(SCRIPT.criticalDrawerId);
            criticalDrawer?.classList.remove('mcms-open');
            criticalDrawer?.setAttribute('aria-hidden', 'true');
            saveState();
            applyRootAttributes();
            updateUI();
            synchroniseVehicleMarkerClasses();
            synchronisePersonalBuildingVisibility();
            reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
            if (previousView) {
                runtimeSetTimeout(() => {
                    const map = findLeafletMapInstance(false);
                    try { map?.setView?.([previousView.lat, previousView.lng], previousView.zoom); } catch (err) {}
                }, 220);
            }
            showToast('Critical View restored');
            return;
        }

        criticalViewLoading = true;
        showToast('Preparing age-based Critical View…');
        try {
            await refreshPersonalVehicleData(true);
            const entries = getCriticalMissionEntries(CRITICAL_VIEW_MIN_AGE_MS);
            if (!entries.length) {
                showToast('No personal missions are currently 8 hours old or more');
                updateUI();
                return;
            }

            const map = findLeafletMapInstance(false);
            let mapView = null;
            try {
                const centre = map?.getCenter?.();
                const zoom = map?.getZoom?.();
                if (centre && Number.isFinite(Number(zoom))) mapView = { lat: centre.lat, lng: centre.lng, zoom: Number(zoom) };
            } catch (err) {}

            criticalViewSnapshot = {
                visibility: { ...state.visibility },
                allianceCredits: state.allianceCredits,
                allianceCreditMinimum: state.allianceCreditMinimum,
                missionAge: state.missionAge,
                transportWatcher: state.transportWatcher,
                unitCommitment: state.unitCommitment,
                mapView
            };
            criticalViewActive = true;
            state.visibility = { ...state.visibility, allianceMissions: false, myMissions: true, vehicles: false, buildings: false };
            state.allianceCredits = false;
            state.missionAge = true;
            state.unitCommitment = true;

            applyRootAttributes();
            updateUI();
            synchroniseVehicleMarkerClasses();
            synchronisePersonalBuildingVisibility();
            reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
            runtimeSetTimeout(() => {
                applyCriticalViewFilter();
                fitCriticalMissions();
                const drawer = createCriticalDrawer();
                drawer.classList.add('mcms-open');
                drawer.setAttribute('aria-hidden', 'false');
                renderCriticalDrawer();
                updateUI();
            }, 360);
            showToast(`Critical View on · ${entries.length} aged mission${entries.length === 1 ? '' : 's'}`);
        } finally {
            criticalViewLoading = false;
            updateUI();
        }
    }


    function loadMissionProgressState() {
        try {
            const parsed = JSON.parse(localStorage.getItem(SCRIPT.missionProgressState) || '{}');
            if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return new Map();
            const now = Date.now();
            return new Map(Object.entries(parsed)
                .filter(([, record]) => record && typeof record === 'object' && now - Number(record.lastSeen || record.lastChanged || now) < 7 * 24 * 60 * 60 * 1000)
                .map(([missionId, record]) => [String(missionId), {
                    signature: String(record.signature || ''),
                    lastChanged: Number(record.lastChanged) || now,
                    lastSeen: Number(record.lastSeen) || now,
                    tracked: Boolean(record.tracked)
                }]));
        } catch (err) {
            return new Map();
        }
    }

    function saveMissionProgressState(delay = 1200) {
        runtimeClearTimeout(missionProgressSaveTimer);
        missionProgressSaveTimer = runtimeSetTimeout(() => {
            try {
                const now = Date.now();
                const entries = Array.from(missionProgressState.entries())
                    .filter(([, record]) => now - Number(record.lastSeen || record.lastChanged || now) < 7 * 24 * 60 * 60 * 1000)
                    .sort((a, b) => Number(b[1].lastSeen || 0) - Number(a[1].lastSeen || 0))
                    .slice(0, 500);
                localStorage.setItem(SCRIPT.missionProgressState, JSON.stringify(Object.fromEntries(entries)));
            } catch (err) {}
        }, Math.max(0, Number(delay) || 0));
    }

    function missionProgressSignature(snapshot) {
        const units = snapshot?.units || {};
        return [
            String(snapshot?.missingText || '').replace(/\s+/g, ' ').trim().toLowerCase(),
            Number.isFinite(Number(snapshot?.patientsCount)) ? Number(snapshot.patientsCount) : '',
            Number.isFinite(Number(snapshot?.prisonersCount)) ? Number(snapshot.prisonersCount) : '',
            Number.isFinite(Number(snapshot?.liveCurrentValue)) ? Number(snapshot.liveCurrentValue) : '',
            Number.isFinite(Number(snapshot?.vehicleState)) ? Number(snapshot.vehicleState) : '',
            Number(units.total) || 0,
            Number(units.onScene) || 0,
            Number(units.travelling) || 0
        ].join('|');
    }

    function updateMissionProgressState(snapshot, now = Date.now()) {
        if (!snapshot?.missionId) return null;
        const tracked = snapshot.source === 'personal' || Number(snapshot.units?.total) > 0;
        const signature = missionProgressSignature(snapshot);
        let record = missionProgressState.get(snapshot.missionId);

        let changed = false;
        if (!record) {
            record = { signature, lastChanged: now, lastSeen: now, tracked };
            missionProgressState.set(snapshot.missionId, record);
            changed = true;
        } else {
            if (record.signature !== signature || record.tracked !== tracked) {
                record.signature = signature;
                record.lastChanged = now;
                changed = true;
            }
            record.lastSeen = now;
            record.tracked = tracked;
        }
        if (changed) saveMissionProgressState();

        snapshot.lastProgressAt = record.lastChanged;
        snapshot.stuckForMs = tracked ? Math.max(0, now - record.lastChanged) : 0;
        return record;
    }

    function missionStuckRecord(missionId, now = Date.now()) {
        const id = normaliseMissionId(missionId);
        const record = id === null ? null : missionProgressState.get(id);
        if (!record?.tracked) return null;
        const stuckForMs = Math.max(0, now - Number(record.lastChanged || now));
        return {
            ...record,
            stuckForMs,
            thresholdMs: state.stuckDetector.thresholdMin * 60 * 1000,
            isStuck: stuckForMs >= state.stuckDetector.thresholdMin * 60 * 1000
        };
    }

    function formatStuckDuration(ms) {
        const minutes = Math.max(0, Math.floor(Number(ms) / 60000));
        if (minutes >= 120) return `${Math.floor(minutes / 60)}H ${minutes % 60}M`;
        return `${minutes}M`;
    }

    function clearStuckMissionLabels() {
        if (stuckMissionGroup) {
            try { stuckMissionGroup.clearLayers(); stuckMissionGroup.remove(); } catch (err) {}
        }
        stuckMissionLabels.clear();
        stuckMissionGroup = null;
    }

    function stuckMissionAnchor(marker, missionId) {
        const personal = isPersonalMissionLayer(marker, missionId);
        let rowsAbove = 0;
        if (personal && state.missionAge) rowsAbove += 1;
        if (!personal && state.allianceCredits) rowsAbove += 1;
        if (state.unitCommitment) rowsAbove += 1;
        return 18 + (rowsAbove * 20);
    }

    function makeStuckMissionIcon(stuckForMs, anchor) {
        const severe = stuckForMs >= Math.max(60 * 60 * 1000, state.stuckDetector.thresholdMin * 2 * 60 * 1000);
        return pageWindow.L.divIcon({
            className: 'mcms-stuck-mission-icon',
            html: `<span class="mcms-stuck-mission-badge ${severe ? 'mcms-stuck-severe' : ''}">STUCK ${escapeHtml(formatStuckDuration(stuckForMs))}</span>`,
            iconSize: [0, 0],
            iconAnchor: [0, anchor]
        });
    }

    function updateStuckMissionLabels() {
        if (state.economyMode && economyMapMoving) return;
        runtimeClearTimeout(stuckMissionTimer);
        stuckMissionTimer = null;
        if (!state.stuckDetector.enabled) {
            clearStuckMissionLabels();
            return;
        }

        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L || typeof pageWindow.L.layerGroup !== 'function' || typeof pageWindow.L.marker !== 'function' || typeof pageWindow.L.divIcon !== 'function') {
            clearStuckMissionLabels();
            return;
        }
        const pane = ensureMissionFloatPane(map);
        if (!pane) {
            clearStuckMissionLabels();
            return;
        }
        const economyBounds = state.economyMode ? economyPaddedBounds(map, 0.08) : null;

        try {
            if (!stuckMissionGroup || stuckMissionGroup._map !== map) {
                clearStuckMissionLabels();
                stuckMissionGroup = pageWindow.L.layerGroup();
                stuckMissionGroup.__mcmsStuckMissionLayer = true;
                stuckMissionGroup.addTo(map);
            }

            const activeIds = new Set();
            const now = Date.now();
            for (const marker of getMissionMarkerIndex().markers) {
                const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
                if (missionId === null) continue;
                const personal = isPersonalMissionLayer(marker, missionId);
                if (personal && !state.visibility.myMissions) continue;
                if (!personal && !state.visibility.allianceMissions) continue;

                let snapshot = liveMissionSnapshots.get(missionId);
                if (!snapshot) {
                    snapshot = missionSnapshotFromMarker(marker, now);
                    if (snapshot) updateMissionProgressState(snapshot, now);
                }
                const stuck = missionStuckRecord(missionId, now);
                if (!snapshot || !stuck?.isStuck) continue;

                let latLng = null;
                try { latLng = marker.getLatLng?.() || null; } catch (err) {}
                if (!latLng || (economyBounds && !economyBounds.contains?.(latLng))) continue;
                try {
                    const onMap = typeof map.hasLayer === 'function' ? map.hasLayer(marker) : Boolean(marker._map);
                    if (!onMap) continue;
                } catch (err) {}

                const anchor = stuckMissionAnchor(marker, missionId);
                const signature = `${Math.floor(stuck.stuckForMs / 60000)}:${anchor}`;
                activeIds.add(missionId);
                let label = stuckMissionLabels.get(missionId);
                if (!label) {
                    label = pageWindow.L.marker(latLng, {
                        interactive: false, keyboard: false, bubblingMouseEvents: false,
                        pane, zIndexOffset: 0, icon: makeStuckMissionIcon(stuck.stuckForMs, anchor)
                    });
                    label.__mcmsStuckSignature = signature;
                    label.__mcmsStuckMissionLabel = true;
                    label.addTo(stuckMissionGroup);
                    stuckMissionLabels.set(missionId, label);
                } else {
                    try { label.setLatLng(latLng); } catch (err) {}
                    if (label.__mcmsStuckSignature !== signature) {
                        label.__mcmsStuckSignature = signature;
                        try { label.setIcon(makeStuckMissionIcon(stuck.stuckForMs, anchor)); } catch (err) {}
                    }
                }
            }

            for (const [missionId, label] of stuckMissionLabels.entries()) {
                if (activeIds.has(missionId)) continue;
                stuckMissionLabels.delete(missionId);
                try { stuckMissionGroup.removeLayer(label); } catch (err) {}
            }
        } catch (err) {
            clearStuckMissionLabels();
        }
    }

    function scheduleStuckMissionRefresh(delay = 300) {
        runtimeClearTimeout(stuckMissionTimer);
        stuckMissionTimer = runtimeSetTimeout(updateStuckMissionLabels, state.economyMode ? Math.max(900, delay) : delay);
    }

    function createMissionInspector() {
        let inspector = document.getElementById(SCRIPT.missionInspectorId);
        if (inspector) return inspector;
        inspector = document.createElement('aside');
        inspector.id = SCRIPT.missionInspectorId;
        inspector.setAttribute('aria-hidden', 'true');
        document.body.appendChild(inspector);
        return inspector;
    }

    function missionMarkerFromIcon(icon) {
        if (!icon) return null;
        const cached = missionIconMarkerCache.get(icon);
        if (cached) return cached;
        for (const marker of getMissionMarkerLayers()) {
            const markerIcon = marker?._icon;
            if (!markerIcon) continue;
            missionIconMarkerCache.set(markerIcon, marker);
            if (markerIcon === icon || markerIcon.contains?.(icon)) return marker;
        }
        return null;
    }

    function positionMissionInspector(event) {
        const inspector = document.getElementById(SCRIPT.missionInspectorId);
        if (!inspector || !event) return;

        const margin = 12;
        const horizontalGap = 16;
        const verticalGap = 44;
        const tooltipGap = 10;
        const pointerX = Number(event.clientX);
        const pointerY = Number(event.clientY);
        if (!Number.isFinite(pointerX) || !Number.isFinite(pointerY)) return;

        const width = inspector.offsetWidth || 300;
        const height = inspector.offsetHeight || 170;
        const viewportWidth = pageWindow.innerWidth || document.documentElement.clientWidth;
        const viewportHeight = pageWindow.innerHeight || document.documentElement.clientHeight;
        let left = pointerX + horizontalGap;
        let top = pointerY + verticalGap;

        const now = Date.now();
        let missionTooltip;
        if (missionInspectorTooltipCache.marker === missionInspectorMarker && now - missionInspectorTooltipCache.createdAt < 160) {
            missionTooltip = missionInspectorTooltipCache.rect;
        } else {
            let tooltipElement = null;
            try {
                const tooltip = missionInspectorMarker?.getTooltip?.();
                tooltipElement = tooltip?.getElement?.() || tooltip?._container || null;
            } catch (err) {}
            if (!tooltipElement?.getClientRects?.().length) {
                tooltipElement = Array.from(document.querySelectorAll('.leaflet-tooltip'))
                    .find(node => node.getClientRects?.().length && pointerX >= node.getBoundingClientRect().left - 48 && pointerX <= node.getBoundingClientRect().right + 48 && pointerY >= node.getBoundingClientRect().top - 48 && pointerY <= node.getBoundingClientRect().bottom + 48) || null;
            }
            const rect = tooltipElement?.getBoundingClientRect?.();
            missionTooltip = rect?.width > 0 && rect?.height > 0 ? rect : null;
            missionInspectorTooltipCache = { marker: missionInspectorMarker, createdAt: now, rect: missionTooltip };
        }
        if (missionTooltip) top = Math.max(top, missionTooltip.bottom + tooltipGap);

        if (left + width + margin > viewportWidth) left = pointerX - width - horizontalGap;
        if (top + height + margin > viewportHeight) {
            const aboveAnchor = missionTooltip ? missionTooltip.top : pointerY;
            top = aboveAnchor - height - tooltipGap;
        }

        left = Math.round(Math.min(Math.max(margin, left), Math.max(margin, viewportWidth - width - margin)));
        top = Math.round(Math.min(Math.max(margin, top), Math.max(margin, viewportHeight - height - margin)));
        const signature = `${left}:${top}`;
        if (missionInspectorLastPosition === signature) return;
        missionInspectorLastPosition = signature;
        inspector.style.setProperty('left', `${left}px`, 'important');
        inspector.style.setProperty('top', `${top}px`, 'important');
    }

    function renderMissionInspector(marker, event = missionInspectorPointer) {
        if (!state.missionInspector || !marker) {
            hideMissionInspector();
            return;
        }
        const inspector = createMissionInspector();
        const now = Date.now();
        const snapshot = missionSnapshotFromMarker(marker, now);
        if (!snapshot) {
            hideMissionInspector();
            return;
        }
        updateMissionProgressState(snapshot, now);
        const age = snapshot.createdAt ? formatMissionAge(snapshot.createdAt, now) : 'Unknown';
        const credits = Number.isFinite(Number(snapshot.averageCredits)) ? `≈${formatOperationalCompactCredits(snapshot.averageCredits)}` : 'Unknown';
        const patients = Number.isFinite(Number(snapshot.patientsCount))
            ? `${snapshot.patientsCount}${Number.isFinite(Number(snapshot.possiblePatientsCount)) && snapshot.possiblePatientsCount > snapshot.patientsCount ? ` / ${snapshot.possiblePatientsCount}` : ''}`
            : '—';
        const prisoners = Number.isFinite(Number(snapshot.prisonersCount))
            ? `${snapshot.prisonersCount}${Number.isFinite(Number(snapshot.possiblePrisonersCount)) && snapshot.possiblePrisonersCount > snapshot.prisonersCount ? ` / ${snapshot.possiblePrisonersCount}` : ''}`
            : '—';
        const unitText = snapshot.units.total
            ? `${snapshot.units.onScene}✓ ${snapshot.units.travelling}→`
            : (snapshot.units.known ? '0' : 'Loading…');
        const stuck = missionStuckRecord(snapshot.missionId, now);
        const alerts = [];
        if (stuck?.isStuck) alerts.push(`<div class="mcms-inspector-alert mcms-stuck">NO PROGRESS FOR ${escapeHtml(formatStuckDuration(stuck.stuckForMs))}</div>`);
        const missingRequirementText = normaliseMissingRequirementText(snapshot.missingText);
        const gapAnalysis = state.resourceGap.enabled ? analyseResourceGap(snapshot) : null;
        let gapHtml = '';
        if (gapAnalysis?.rows?.length) {
            const rows = gapAnalysis.rows.map(row => {
                const nearest = row.nearest === null ? 'none nearby' : `${row.nearby} nearby · ${row.nearest.toFixed(row.nearest < 10 ? 1 : 0)}mi`;
                return `<div class="mcms-inspector-gap-row"><span>${escapeHtml(`${row.count}× ${row.name}`)}</span><span>${escapeHtml(nearest)}</span></div>`;
            }).join('');
            const personnel = gapAnalysis.requirements.personnel.length ? `<div class="mcms-inspector-gap-row"><span>Personnel reported</span><span>${escapeHtml(gapAnalysis.requirements.personnel.map(item => `${item.count}× ${item.name}`).join(', '))}</span></div>` : '';
            gapHtml = `<div class="mcms-inspector-gap"><div class="mcms-inspector-gap-title"><span>RESOURCE GAP</span><span>${gapAnalysis.radiusMi}MI RADIUS</span></div>${rows}${personnel}</div>`;
        } else if (missingRequirementText) alerts.push(`<div class="mcms-inspector-alert">MISSING: ${escapeHtml(missingRequirementText)}</div>`);

        inspector.innerHTML = `
            <div class="mcms-inspector-head">
                <span class="mcms-inspector-title">${escapeHtml(snapshot.caption || `Mission ${snapshot.missionId}`)}</span>
                <span class="mcms-inspector-type ${snapshot.source === 'alliance' ? 'mcms-alliance' : ''}">${snapshot.source === 'alliance' ? 'ALLIANCE' : 'PERSONAL'}</span>
            </div>
            <div class="mcms-inspector-grid">
                <div class="mcms-inspector-stat"><span>Mission age</span><strong>${escapeHtml(age)}</strong></div>
                <div class="mcms-inspector-stat"><span>Est. value</span><strong>${escapeHtml(credits)}</strong></div>
                <div class="mcms-inspector-stat"><span>Your units</span><strong>${escapeHtml(unitText)}</strong></div>
                <div class="mcms-inspector-stat"><span>Patients</span><strong>${escapeHtml(patients)}</strong></div>
                <div class="mcms-inspector-stat"><span>Prisoners</span><strong>${escapeHtml(prisoners)}</strong></div>
                <div class="mcms-inspector-stat"><span>Status</span><strong>${stuck?.isStuck ? 'STUCK' : 'ACTIVE'}</strong></div>
            </div>
            ${alerts.join('')}
            ${gapHtml}`;
        inspector.classList.add('mcms-open');
        inspector.setAttribute('aria-hidden', 'false');
        positionMissionInspector(event);
    }

    function hideMissionInspector() {
        missionInspectorMarker = null;
        missionInspectorPointer = null;
        missionInspectorLastPosition = '';
        missionInspectorTooltipCache = { marker: null, createdAt: 0, rect: null };
        if (missionInspectorMoveFrame) runtimeCancelAnimationFrame(missionInspectorMoveFrame);
        missionInspectorMoveFrame = null;
        runtimeClearTimeout(missionInspectorRefreshTimer);
        missionInspectorRefreshTimer = null;
        const inspector = document.getElementById(SCRIPT.missionInspectorId);
        if (!inspector) return;
        inspector.classList.remove('mcms-open');
        inspector.setAttribute('aria-hidden', 'true');
    }

    function refreshVisibleMissionInspector() {
        if (!missionInspectorMarker) return;
        runtimeClearTimeout(missionInspectorRefreshTimer);
        missionInspectorRefreshTimer = runtimeSetTimeout(() => renderMissionInspector(missionInspectorMarker), 80);
    }

    function handleMissionInspectorPointerOver(event) {
        if (!state.missionInspector) return;
        const icon = closestEventTarget(event, '.leaflet-marker-icon');
        if (!icon) return;
        const marker = missionMarkerFromIcon(icon);
        if (!marker) return;
        missionInspectorMarker = marker;
        missionInspectorPointer = { clientX: Number(event.clientX), clientY: Number(event.clientY) };
        missionInspectorTooltipCache = { marker: null, createdAt: 0, rect: null };
        renderMissionInspector(marker, missionInspectorPointer);
    }

    function handleMissionInspectorPointerMove(event) {
        if (!missionInspectorMarker || state.economyMode) return;
        missionInspectorPointer = { clientX: Number(event.clientX), clientY: Number(event.clientY) };
        if (missionInspectorMoveFrame) return;
        missionInspectorMoveFrame = runtimeRequestAnimationFrame(() => {
            missionInspectorMoveFrame = null;
            if (missionInspectorMarker && missionInspectorPointer) positionMissionInspector(missionInspectorPointer);
        });
    }

    function handleMissionInspectorPointerOut(event) {
        if (!missionInspectorMarker) return;
        const icon = closestEventTarget(event, '.leaflet-marker-icon');
        if (!icon) return;
        const related = event.relatedTarget;
        if (related && icon.contains?.(related)) return;
        if (missionMarkerFromIcon(icon) === missionInspectorMarker) hideMissionInspector();
    }

    function extractMissionIdsFromPayload(payload, target = new Set(), seen = new WeakSet()) {
        if (!payload || typeof payload !== 'object') return target;
        if (seen.has(payload)) return target;
        seen.add(payload);
        if (Array.isArray(payload)) {
            payload.forEach(item => extractMissionIdsFromPayload(item, target, seen));
            return target;
        }
        const id = normaliseMissionId(payload.id ?? payload.mission_id ?? payload.missionId);
        if (id !== null) target.add(id);
        for (const key of ['params', 'mission', 'data']) {
            const nested = payload[key];
            if (nested && typeof nested === 'object') extractMissionIdsFromPayload(nested, target, seen);
        }
        return target;
    }

    function animateMissionSpawn(missionId, attempt = 0) {
        const marker = getMissionMarkerIndex().byId.get(missionId) || null;
        if (!marker) {
            if (attempt < 4) runtimeSetTimeout(() => animateMissionSpawn(missionId, attempt + 1), 120 + attempt * 120);
            return;
        }
        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L) return;
        let latLng = null;
        try { latLng = marker.getLatLng?.() || null; } catch (err) {}
        if (!latLng) return;

        marker._icon?.classList?.add('mcms-mission-spawn-focus');
        const personal = isPersonalMissionLayer(marker, missionId);
        const group = pageWindow.L.layerGroup();
        group.__mcmsMissionSpawnLayer = true;
        try {
            const ring = state.economyMode ? null : pageWindow.L.circleMarker(latLng, {
                radius: 10, interactive: false, bubblingMouseEvents: false,
                className: 'mcms-mission-spawn-ring', pane: 'overlayPane'
            });
            const pane = ensureMissionFloatPane(map) || 'markerPane';
            const label = pageWindow.L.marker(latLng, {
                interactive: false, keyboard: false, bubblingMouseEvents: false, pane,
                icon: pageWindow.L.divIcon({
                    className: 'mcms-mission-spawn-label-icon',
                    html: `<span class="mcms-mission-spawn-label${personal ? '' : ' mcms-alliance-text'}">${personal ? 'NEW INCIDENT' : 'NEW ALLIANCE INCIDENT'}</span>`,
                    iconSize: [0, 0], iconAnchor: [0, 34]
                })
            });
            if (ring) {
                ring.__mcmsMissionSpawnRing = true;
                ring.addTo(group);
            }
            label.__mcmsMissionSpawnLabel = true;
            label.addTo(group);
            group.addTo(map);
        } catch (err) {}
        runtimeSetTimeout(() => {
            marker._icon?.classList?.remove('mcms-mission-spawn-focus');
            try { group.clearLayers(); group.remove(); } catch (err) {}
        }, state.economyMode ? Math.min(1600, MISSION_SPAWN_DURATION_MS) : MISSION_SPAWN_DURATION_MS);
    }

    function handleMissionSpawnArguments(args) {
        if (!state.missionSpawn.enabled) return;
        const ids = new Set();
        args.forEach(arg => extractMissionIdsFromPayload(arg, ids));
        ids.forEach(missionId => {
            if (knownMissionIds.has(missionId)) return;
            knownMissionIds.add(missionId);
            if (!missionSpawnArmed || !state.missionSpawn.enabled) return;
            runtimeSetTimeout(() => animateMissionSpawn(missionId), 80);
        });
    }

    function primeMissionSpawnDetector() {
        missionSpawnArmed = false;
        knownMissionIds.clear();
        for (const marker of getMissionMarkerIndex().markers) {
            const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
            if (missionId !== null) knownMissionIds.add(missionId);
        }
        runtimeClearTimeout(missionSpawnPrimeTimer);
        missionSpawnPrimeTimer = runtimeSetTimeout(() => { missionSpawnArmed = true; }, 5000);
    }

    function clonePlainData(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function currentMapViewSnapshot() {
        const map = findLeafletMapInstance(false);
        try {
            const centre = map?.getCenter?.();
            const zoom = map?.getZoom?.();
            if (centre && Number.isFinite(Number(zoom))) return { lat: Number(centre.lat), lng: Number(centre.lng), zoom: Number(zoom) };
        } catch (err) {}
        return null;
    }

    function buildMapProfile(name) {
        return {
            name: String(name || 'Map Profile').slice(0, 40),
            savedAt: Date.now(),
            mapView: currentMapViewSnapshot(),
            settings: clonePlainData({
                theme: state.theme,
                markerFocus: state.markerFocus,
                missionPulse: state.missionPulse,
                roadPriority: state.roadPriority,
                visibility: state.visibility,
                allianceCredits: state.allianceCredits,
                missionAge: state.missionAge,
                unitCommitment: state.unitCommitment,
                transportWatcher: state.transportWatcher,
                missionInspector: state.missionInspector,
                stuckDetector: state.stuckDetector,
                missionSpawn: state.missionSpawn,
                resourceGap: state.resourceGap,
                coverage: state.coverage,
                heatmap: state.heatmap
            })
        };
    }

    function renderProfiles() {
        const list = document.querySelector(`#${SCRIPT.panelId} [data-profile-list]`);
        if (!list) return;
        list.innerHTML = state.profiles.map((profile, index) => {
            if (!profile) {
                return `<div class="mcms-profile-row"><div class="mcms-profile-main"><strong>Slot ${index + 1}</strong><span>Empty profile</span></div><span></span><button class="mcms-small-btn" type="button" data-action="profile-save" data-slot="${index}">Save</button><span></span></div>`;
            }
            const detail = `${THEMES[profile.settings?.theme]?.label || 'Map'} · ${profile.mapView ? `Z${profile.mapView.zoom}` : 'No view'}`;
            return `<div class="mcms-profile-row">
                <div class="mcms-profile-main"><strong>${escapeHtml(profile.name || `Profile ${index + 1}`)}</strong><span>${escapeHtml(detail)}</span></div>
                <button class="mcms-small-btn" type="button" data-action="profile-load" data-slot="${index}">Go</button>
                <button class="mcms-small-btn" type="button" data-action="profile-save" data-slot="${index}">Save</button>
                <button class="mcms-small-btn" type="button" data-action="profile-delete" data-slot="${index}">×</button>
            </div>`;
        }).join('');
    }

    function saveMapProfile(slot) {
        if (!Number.isInteger(slot) || slot < 0 || slot >= MAP_PROFILE_LIMIT) return;
        const existing = state.profiles[slot];
        const name = pageWindow.prompt('Profile name:', existing?.name || `Profile ${slot + 1}`);
        if (name === null) return;
        state.profiles[slot] = buildMapProfile(name.trim() || `Profile ${slot + 1}`);
        saveState();
        renderProfiles();
        showToast(`Saved ${state.profiles[slot].name}`);
    }

    function applyLoadedConfiguration() {
        criticalViewActive = false;
        criticalViewSnapshot = null;
        document.querySelectorAll('.mcms-critical-view-hidden').forEach(icon => icon.classList.remove('mcms-critical-view-hidden'));
        const criticalDrawer = document.getElementById(SCRIPT.criticalDrawerId);
        criticalDrawer?.classList.remove('mcms-open');
        criticalDrawer?.setAttribute('aria-hidden', 'true');
        const vehicleStatus = document.getElementById(SCRIPT.vehicleStatusId);
        vehicleStatus?.classList.remove('mcms-open');
        vehicleStatus?.setAttribute('aria-hidden', 'true');
        hideMissionInspector();
        missionSpawnArmed = false;
        runtimeClearTimeout(missionSpawnPrimeTimer);
        knownMissionIds.clear();
        if (state.missionSpawn.enabled) primeMissionSpawnDetector();
        if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
        else stopAutoLoadAllVehicles();
        applyRootAttributes();
        renderQuickPlaces();
        renderBookmarks();
        renderProfiles();
        renderScreenPins();
        updateUI();
        synchroniseVehicleMarkerClasses();
        synchronisePersonalBuildingVisibility();
        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: true });
    }

    function loadMapProfile(slot) {
        const profile = state.profiles[slot];
        if (!profile?.settings) return;
        const settings = profile.settings;
        state.theme = normaliseTheme(settings.theme);
        state.markerFocus = Boolean(settings.markerFocus);
        state.missionPulse = Boolean(settings.missionPulse);
        state.roadPriority = Boolean(settings.roadPriority);
        state.visibility = { ...state.visibility, ...(settings.visibility || {}) };
        state.allianceCredits = Boolean(settings.allianceCredits);
        state.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(settings.allianceCreditMinimum)) ? Number(settings.allianceCreditMinimum) : state.allianceCreditMinimum;
        state.missionAge = Boolean(settings.missionAge);
        state.unitCommitment = Boolean(settings.unitCommitment);
        state.transportWatcher = settings.transportWatcher !== false;
        state.missionInspector = settings.missionInspector !== false;
        state.stuckDetector = { ...state.stuckDetector, ...(settings.stuckDetector || {}) };
        state.stuckDetector.thresholdMin = Math.round(clamp(state.stuckDetector.thresholdMin, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
        state.missionSpawn = { ...state.missionSpawn, ...(settings.missionSpawn || {}) };
        state.resourceGap = { ...state.resourceGap, ...(settings.resourceGap || {}) };
        state.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(state.resourceGap.radiusMi)) ? Number(state.resourceGap.radiusMi) : 25;
        state.coverage = { ...state.coverage, ...(settings.coverage || {}) };
        state.heatmap = { ...state.heatmap, ...(settings.heatmap || {}) };
        saveState();
        applyLoadedConfiguration();
        if (profile.mapView) runtimeSetTimeout(() => setMapView(profile.mapView.lat, profile.mapView.lng, profile.mapView.zoom), 180);
        showToast(`Loaded ${profile.name || `Profile ${slot + 1}`}`);
    }

    function deleteMapProfile(slot) {
        if (!state.profiles[slot]) return;
        if (!pageWindow.confirm(`Delete "${state.profiles[slot].name || `Profile ${slot + 1}`}"?`)) return;
        state.profiles[slot] = null;
        saveState();
        renderProfiles();
        showToast('Profile deleted');
    }

    function settingsBackupFilename(date = new Date()) {
        const pad = value => String(value).padStart(2, '0');
        return `MC Map Command PRIVATE Backup ${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}-${pad(date.getMinutes())}-${pad(date.getSeconds())}.json`;
    }

    function buildToolkitSettingsBackup(exportedAt = new Date()) {
        const discordWebhook = getDiscordWebhookUrl();
        const financeIdentity = financeVaultCredential();
        const financialArchiveStore = loadFinanceVaultStore();
        return {
            format: 'MissionChief Map Command Toolkit Private Settings Backup',
            schema: 4,
            version: SCRIPT.version,
            exportedAt: exportedAt.toISOString(),
            state: clonePlainData(state),
            integrations: {
                discordWebhook,
                financialArchiveIdentity: clonePlainData(financeIdentity)
            },
            financialArchiveStore: clonePlainData(financialArchiveStore),
            containsPrivateCredentials: Boolean(discordWebhook),
            containsFinancialHistory: Boolean(financialArchiveStore?.profiles && Object.keys(financialArchiveStore.profiles).length),
            privateCredentialNotice: 'This private backup may contain your Discord webhook token and locally stored MissionChief financial history. Anyone holding it may be able to post through the webhook and inspect the exported game ledger.'
        };
    }

    function downloadToolkitSettingsBlob(blob, filename) {
        const urlApi = pageWindow.URL || globalThis.URL;
        const url = urlApi.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        link.remove();
        runtimeSetTimeout(() => urlApi.revokeObjectURL(url), 2500);
    }

    async function exportToolkitConfig() {
        try {
            const privateItems = [];
            if (getDiscordWebhookUrl()) privateItems.push('your Discord webhook URL and token');
            if (loadFinanceVaultStore()?.profiles && Object.keys(loadFinanceVaultStore().profiles).length) privateItems.push('your locally stored MissionChief financial history');
            if (privateItems.length) {
                const accepted = pageWindow.confirm(`PRIVATE BACKUP WARNING

This export contains ${privateItems.join(', ')}. Anyone with the file may be able to post to your Discord channel or inspect the exported game ledger.

Store it privately and never upload it to a public website or support ticket.

Create the private backup now?`);
                if (!accepted) {
                    showToast('Private settings export cancelled');
                    return;
                }
            }
            const exportedAt = new Date();
            const filename = settingsBackupFilename(exportedAt);
            const json = JSON.stringify(buildToolkitSettingsBackup(exportedAt), null, 2);
            const BlobConstructor = pageWindow.Blob || globalThis.Blob;
            const FileConstructor = pageWindow.File || globalThis.File;
            const blob = new BlobConstructor([json], { type: 'application/json' });
            const shareNavigator = pageWindow.navigator || globalThis.navigator;

            if (activeDeviceLayout === 'mobile' && typeof FileConstructor === 'function' && typeof shareNavigator?.share === 'function') {
                const file = new FileConstructor([json], filename, { type: 'application/json' });
                let canShareFile = false;
                try {
                    canShareFile = typeof shareNavigator.canShare !== 'function' || shareNavigator.canShare({ files: [file] });
                } catch (err) {}
                if (canShareFile) {
                    try {
                        await shareNavigator.share({
                            files: [file],
                            title: 'MC Map Command private settings backup'
                        });
                        showToast('All toolkit settings exported');
                        return;
                    } catch (err) {
                        if (err?.name === 'AbortError') {
                            showToast('Settings export cancelled');
                            return;
                        }
                    }
                }
            }

            downloadToolkitSettingsBlob(blob, filename);
            showToast('All toolkit settings exported');
        } catch (err) {
            showToast('Export failed: settings file could not be created');
        }
    }

    function looksLikeToolkitState(value) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
        return ['theme', 'position', 'visibility', 'bookmarks', 'profiles', 'payoutFlash', 'tabletMode', 'mobileMode']
            .some(key => Object.prototype.hasOwnProperty.call(value, key));
    }

    function extractImportedToolkitState(parsed) {
        const candidates = [
            parsed?.state,
            parsed?.settings?.state,
            parsed?.configuration?.state,
            parsed?.configuration,
            parsed
        ];
        return candidates.find(looksLikeToolkitState) || null;
    }

    function extractImportedDiscordWebhook(parsed) {
        const containers = [
            parsed?.integrations,
            parsed?.settings?.integrations,
            parsed?.configuration?.integrations
        ];
        for (const container of containers) {
            if (!container || typeof container !== 'object') continue;
            if (Object.prototype.hasOwnProperty.call(container, 'discordWebhook')) {
                return { present: true, value: String(container.discordWebhook || '') };
            }
            if (Object.prototype.hasOwnProperty.call(container, 'discordWebhookUrl')) {
                return { present: true, value: String(container.discordWebhookUrl || '') };
            }
        }
        return { present: false, value: '' };
    }

    function extractImportedFinancialVaultCredential(parsed) {
        const candidates = [
            parsed?.integrations?.financialArchiveIdentity,
            parsed?.settings?.integrations?.financialArchiveIdentity,
            parsed?.configuration?.integrations?.financialArchiveIdentity,
            parsed?.financialArchiveIdentity,
            parsed?.integrations?.financialVaultCredential,
            parsed?.settings?.integrations?.financialVaultCredential,
            parsed?.configuration?.integrations?.financialVaultCredential,
            parsed?.financialVaultCredential
        ];
        const value = candidates.find(candidate => candidate && typeof candidate === 'object' && !Array.isArray(candidate));
        return { present: Boolean(value), value: value || null };
    }

    function extractImportedFinancialVaultStore(parsed) {
        const candidates = [
            parsed?.financialArchiveStore,
            parsed?.integrations?.financialArchiveStore,
            parsed?.settings?.financialArchiveStore,
            parsed?.configuration?.financialArchiveStore,
            parsed?.financialVaultStore,
            parsed?.integrations?.financialVaultStore,
            parsed?.settings?.financialVaultStore,
            parsed?.configuration?.financialVaultStore
        ];
        const value = candidates.find(candidate => candidate && typeof candidate === 'object' && !Array.isArray(candidate));
        return { present: Boolean(value), value: value || null };
    }

    function normaliseImportedFinanceVaultCredential(value) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('The Financial Archive identity is invalid.');
        const current = financeVaultCredential();
        return {
            deviceId: current.deviceId || String(value.deviceId || '') || financeRandomToken(16),
            playerId: value.playerId === undefined || value.playerId === null || value.playerId === '' ? null : String(value.playerId).slice(0, 64),
            playerName: financeNormaliseText(value.playerName).slice(0, 120),
            createdAt: Number(value.createdAt) || Date.now()
        };
    }

    function normaliseImportedFinanceVaultStore(value) {
        if (!value || typeof value !== 'object' || Array.isArray(value) || !value.profiles || typeof value.profiles !== 'object') {
            throw new Error('The Financial Archive history is invalid.');
        }
        const credential = financeVaultCredential();
        const profiles = {};
        for (const [rawKey, rawVault] of Object.entries(value.profiles).slice(0, 50)) {
            if (!rawVault || typeof rawVault !== 'object') continue;
            const player = {
                id: rawVault?.player?.id === undefined || rawVault?.player?.id === null || rawVault?.player?.id === '' ? null : String(rawVault.player.id).slice(0, 64),
                name: financeNormaliseText(rawVault?.player?.name).slice(0, 120)
            };
            const key = player.id || player.name ? financePlayerProfileKey(player) : String(rawKey || '').slice(0, 180);
            if (!key) continue;
            profiles[key] = normaliseFinanceVault(rawVault, player, credential.deviceId);
        }
        return { schema: FINANCE_VAULT_SCHEMA, profiles };
    }

    function describePrivateImport(parsed) {
        const importedWebhook = extractImportedDiscordWebhook(parsed);
        const importedCredential = extractImportedFinancialVaultCredential(parsed);
        const importedStore = extractImportedFinancialVaultStore(parsed);
        const privateItems = [];
        if (importedWebhook.present && String(importedWebhook.value || '').trim()) privateItems.push('a Discord webhook URL and token');
        if (importedStore.present && Object.keys(importedStore.value?.profiles || {}).length) privateItems.push('stored MissionChief financial ledger history');
        return { importedWebhook, importedCredential, importedStore, privateItems };
    }

    function applyImportedToolkitSettings(parsed) {
        const importedState = extractImportedToolkitState(parsed);
        if (!importedState) throw new Error('The file does not contain MissionChief Map Command settings.');

        const { importedWebhook, importedCredential, importedStore } = describePrivateImport(parsed);
        const normalisedWebhook = importedWebhook.present ? normaliseDiscordWebhookUrl(importedWebhook.value) : '';
        const normalisedCredential = importedCredential.present ? normaliseImportedFinanceVaultCredential(importedCredential.value) : null;
        const normalisedVaultStore = importedStore.present ? normaliseImportedFinanceVaultStore(importedStore.value) : null;
        const previousStateRaw = localStorage.getItem(SCRIPT.storageState);
        const previousWebhook = getDiscordWebhookUrl();
        const previousCredentialRaw = gmGetValueSafe(SCRIPT.financeVaultCredentialState, null);
        const previousVaultRaw = gmGetValueSafe(SCRIPT.financeVaultState, null);

        try {
            localStorage.setItem(SCRIPT.storageState, JSON.stringify(importedState));
            state = loadState();
            saveState();
            if (importedWebhook.present) saveDiscordWebhookUrl(normalisedWebhook);
            if (normalisedCredential) saveFinanceVaultCredential(normalisedCredential);
            if (normalisedVaultStore) saveFinanceVaultStore(normalisedVaultStore);
            invalidateFinanceVaultMemory();
            loadCachedFinancialRules();
            loadCachedFinancialPolicy();
            applyLoadedConfiguration();
        } catch (err) {
            try {
                if (previousStateRaw === null) localStorage.removeItem(SCRIPT.storageState);
                else localStorage.setItem(SCRIPT.storageState, previousStateRaw);
                state = loadState();
                saveDiscordWebhookUrl(previousWebhook);
                if (previousCredentialRaw === null) gmDeleteValueSafe(SCRIPT.financeVaultCredentialState);
                else gmSetValueSafe(SCRIPT.financeVaultCredentialState, previousCredentialRaw);
                if (previousVaultRaw === null) gmDeleteValueSafe(SCRIPT.financeVaultState);
                else gmSetValueSafe(SCRIPT.financeVaultState, previousVaultRaw);
                invalidateFinanceVaultMemory();
                applyLoadedConfiguration();
            } catch (rollbackError) {}
            throw err;
        }

        return {
            webhook: importedWebhook.present,
            credential: importedCredential.present,
            vaultHistory: importedStore.present
        };
    }

    function importToolkitConfigFile(file) {
        if (!file) return;
        if (Number(file.size) > 150 * 1024 * 1024) {
            showToast('Import failed: settings file is too large');
            return;
        }
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const parsed = JSON.parse(String(reader.result || ''));
                const privateImport = describePrivateImport(parsed);
                if (privateImport.privateItems.length) {
                    const accepted = pageWindow.confirm(`PRIVATE BACKUP IMPORT WARNING\n\nThis file contains ${privateImport.privateItems.join(', ')}. Importing it can replace your saved Discord connection, Financial Archive identity or local financial history.\n\nOnly continue if you trust where this backup came from.\n\nImport this private backup now?`);
                    if (!accepted) {
                        showToast('Private settings import cancelled');
                        return;
                    }
                }
                const imported = applyImportedToolkitSettings(parsed);
                const additions = [imported.webhook && 'webhook', imported.credential && 'archive identity', imported.vaultHistory && 'financial history'].filter(Boolean);
                showToast(additions.length ? `All toolkit settings imported · ${additions.join(', ')}` : 'Toolkit settings imported · existing private integrations kept');
            } catch (err) {
                showToast(`Import failed: ${err?.message || 'invalid settings file'}`);
            }
        };
        reader.onerror = () => showToast('Import failed: file could not be read');
        reader.readAsText(file);
    }

    function resetToolkitConfiguration() {
        if (!pageWindow.confirm('Reset all toolkit settings and saved map profiles? Payout history will be kept.')) return;
        state = defaultState();
        saveState();
        applyLoadedConfiguration();
        showToast('Toolkit settings reset');
    }

    function payoutPresentation(amount, context = {}) {
        const tier = payoutTierForAmount(amount);
        const source = ['personal', 'alliance'].includes(context.source) ? context.source : 'unknown';
        const wording = {
            standard: ['MISSION COMPLETE', 'INCIDENT RESOLVED', 'RESPONSE SUCCESSFUL'],
            major: ['MAJOR PAYOUT', 'OPERATION COMPLETE', 'RESPONSE SUCCESSFUL'],
            high: ['HIGH VALUE MISSION', 'MAJOR INCIDENT CLEARED', 'OPERATION COMPLETE'],
            elite: ['ELITE RESPONSE', 'COMMAND SUCCESS', 'MAJOR INCIDENT CLEARED']
        };
        payoutEventCounter += 1;
        const titles = wording[tier];
        const title = titles[(Math.abs(Math.round(Number(amount) || 0)) + payoutEventCounter) % titles.length];
        const accents = {
            personal: { colour: '#f4c84f', soft: 'rgba(244,200,79,.55)', glow: 'rgba(244,200,79,.24)', label: 'PERSONAL MISSION' },
            alliance: { colour: '#70ef9b', soft: 'rgba(112,239,155,.55)', glow: 'rgba(112,239,155,.24)', label: 'ALLIANCE MISSION' },
            unknown: { colour: '#a8ddff', soft: 'rgba(168,221,255,.52)', glow: 'rgba(168,221,255,.22)', label: 'CREDIT AWARD' }
        };
        const tierLabels = { standard: 'STANDARD PAYOUT', major: 'MAJOR PAYOUT', high: 'HIGH VALUE', elite: 'ELITE RESPONSE' };
        return { tier, source, title, tierLabel: tierLabels[tier], ...accents[source], caption: String(context.caption || '') };
    }

    function stopPayoutMediaAudio(resetPosition = true) {
        payoutMediaGeneration += 1;
        if (!payoutMediaAudio) return;
        try {
            payoutMediaAudio.pause();
            if (resetPosition) payoutMediaAudio.currentTime = 0;
        } catch (err) {}
    }

    function disposePayoutMediaAudio() {
        payoutMediaGeneration += 1;
        if (payoutMediaAudio) {
            try {
                payoutMediaAudio.pause();
                payoutMediaAudio.removeAttribute('src');
                payoutMediaAudio.load();
            } catch (err) {}
        }
        payoutMediaAudio = null;
        payoutMediaTemplate = '';
    }

    function getPayoutMediaAudio(template) {
        const media = PAYOUT_MEDIA_SOUNDS[template];
        if (!media?.url) return null;
        if (!payoutMediaAudio || payoutMediaTemplate !== template) {
            disposePayoutMediaAudio();
            const audio = document.createElement('audio');
            // Do not download/decode hosted MP3s during normal gameplay. The file is
            // requested only when a matching payout popup actually needs to play it.
            audio.preload = 'none';
            audio.addEventListener('error', () => {
                console.warn(`[${SCRIPT.name}] Hosted payout audio failed to load: ${media.label}`);
            });
            audio.src = media.url;
            payoutMediaAudio = audio;
            payoutMediaTemplate = template;
            }
        return payoutMediaAudio;
    }

    async function playPayoutMediaSound(template) {
        if (!state.payoutFlash.soundEnabled || state.payoutFlash.soundVolume <= 0) return false;
        const audio = getPayoutMediaAudio(template);
        if (!audio) return false;
        try {
            const generation = ++payoutMediaGeneration;
            audio.pause();
            audio.currentTime = 0;
            audio.muted = false;
            audio.preload = 'auto';
            audio.volume = clamp(state.payoutFlash.soundVolume, 0, 1, 0.35);
            await audio.play();
            if (generation !== payoutMediaGeneration) {
                audio.pause();
                return false;
            }
            return true;
        } catch (err) {
            console.warn(`[${SCRIPT.name}] Hosted payout audio was blocked or unavailable; using synthesized fallback.`, err);
            return false;
        }
    }

    function unlockPayoutAudio(force = false) {
        if (!force && !state.payoutFlash.soundEnabled) return null;
        try {
            const AudioContextClass = pageWindow.AudioContext || pageWindow.webkitAudioContext;
            if (!AudioContextClass) return null;
            if (!payoutAudioContext) payoutAudioContext = new AudioContextClass();
            if (payoutAudioContext.state === 'suspended') payoutAudioContext.resume().catch(() => {});
            return payoutAudioContext;
        } catch (err) { return null; }
    }

    function connectAudioTone(context, destination, {
        start, duration, frequency, endFrequency = frequency, type = 'sine', gain = 0.3
    }) {
        const osc = context.createOscillator();
        const amp = context.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(Math.max(1, frequency), start);
        if (endFrequency !== frequency) osc.frequency.exponentialRampToValueAtTime(Math.max(1, endFrequency), start + duration);
        amp.gain.setValueAtTime(0.0001, start);
        amp.gain.exponentialRampToValueAtTime(Math.max(0.0001, gain), start + Math.min(.035, duration * .18));
        amp.gain.exponentialRampToValueAtTime(0.0001, start + duration);
        osc.connect(amp);
        amp.connect(destination);
        osc.start(start);
        osc.stop(start + duration + .02);
    }

    function connectAudioNoise(context, destination, { start, duration, gain = 0.18, filterFrequency = 900 }) {
        const length = Math.max(1, Math.floor(context.sampleRate * duration));
        const buffer = context.createBuffer(1, length, context.sampleRate);
        const data = buffer.getChannelData(0);
        for (let index = 0; index < length; index += 1) {
            const envelope = 1 - (index / length);
            data[index] = (Math.random() * 2 - 1) * envelope;
        }
        const source = context.createBufferSource();
        const filter = context.createBiquadFilter();
        const amp = context.createGain();
        source.buffer = buffer;
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(filterFrequency, start);
        amp.gain.setValueAtTime(0.0001, start);
        amp.gain.exponentialRampToValueAtTime(Math.max(0.0001, gain), start + .012);
        amp.gain.exponentialRampToValueAtTime(0.0001, start + duration);
        source.connect(filter);
        filter.connect(amp);
        amp.connect(destination);
        source.start(start);
        source.stop(start + duration + .02);
    }

    function playSynthPayoutSound(tier, template = state.payoutFlash.template) {
        if (!state.payoutFlash.soundEnabled || state.payoutFlash.soundVolume <= 0) return;
        const context = unlockPayoutAudio();
        if (!context) return;

        const now = context.currentTime + 0.015;
        const tierScale = tier === 'elite' ? 1.16 : tier === 'high' ? 1.10 : tier === 'major' ? 1.05 : 1;
        const master = context.createGain();
        const volume = Math.max(0.0001, Math.min(.34, .24 * state.payoutFlash.soundVolume));
        master.gain.setValueAtTime(volume, now);
        master.connect(context.destination);

        const tone = (delay, frequency, duration, type = 'sine', gain = .28, endFrequency = frequency) =>
            connectAudioTone(context, master, {
                start: now + delay,
                duration,
                frequency: frequency * tierScale,
                endFrequency: endFrequency * tierScale,
                type,
                gain
            });
        const noise = (delay, duration, gain = .16, filterFrequency = 900) =>
            connectAudioNoise(context, master, { start: now + delay, duration, gain, filterFrequency });

        switch (template) {
            case 'viceCity':
                tone(0, 220, .34, 'sawtooth', .20, 330);
                tone(.15, 330, .28, 'triangle', .22, 440);
                tone(.32, 440, .45, 'sine', .24, 660);
                tone(.48, 660, .48, 'sine', .17, 880);
                break;
            case 'badCompany':
                noise(0, .52, .26, 520);
                tone(0, 62, .55, 'sine', .30, 34);
                tone(.36, 1180, .12, 'square', .11, 820);
                tone(.53, 960, .13, 'square', .09, 700);
                break;
            case 'cyberpunk':
                tone(0, 96, .42, 'square', .20, 48);
                tone(.08, 740, .08, 'square', .10, 1320);
                tone(.22, 1180, .06, 'square', .08, 520);
                tone(.36, 185, .55, 'sawtooth', .18, 370);
                break;
            case 'hellfire':
                noise(0, .62, .24, 650);
                tone(0, 72, .70, 'sawtooth', .22, 36);
                tone(.28, 220, .70, 'triangle', .17, 110);
                tone(.50, 440, .42, 'sine', .12, 220);
                break;
            case 'wasteland':
                noise(0, .18, .08, 2200);
                tone(.02, 390, .16, 'square', .11, 510);
                tone(.25, 520, .18, 'square', .10, 690);
                tone(.48, 780, .44, 'sine', .15, 1040);
                break;
            case 'factorio':
                noise(0, .10, .13, 1750);
                tone(0, 118, .22, 'square', .22, 78);
                tone(.11, 246, .12, 'square', .13, 184);
                noise(.24, .14, .15, 920);
                tone(.30, 330, .34, 'triangle', .17, 495);
                tone(.52, 660, .22, 'square', .10, 440);
                break;
            case 'galactic':
                tone(0, 220, .72, 'sine', .18, 1100);
                tone(.18, 440, .58, 'triangle', .13, 880);
                tone(.42, 880, .48, 'sine', .15, 1320);
                break;
            case 'darkFantasy':
                tone(0, 110, 1.05, 'sine', .26, 82);
                tone(.08, 164.81, 1.15, 'triangle', .15, 123.47);
                tone(.35, 220, .90, 'sine', .14, 165);
                break;
            case 'biohazard':
                tone(0, 740, .14, 'square', .12, 740);
                tone(.24, 740, .14, 'square', .12, 740);
                tone(.50, 980, .44, 'sine', .17, 1240);
                break;
            case 'underworld':
                tone(0, 98, .55, 'sine', .22, 73);
                tone(.16, 196, .42, 'triangle', .18, 246.94);
                tone(.34, 293.66, .42, 'triangle', .16, 392);
                tone(.54, 392, .55, 'sine', .15, 523.25);
                break;
            case 'pixelArcade':
                tone(0, 659.25, .11, 'square', .13);
                tone(.12, 783.99, .11, 'square', .13);
                tone(.24, 987.77, .12, 'square', .14);
                tone(.38, 1318.51, .36, 'square', .12);
                break;
            case 'jamesBond':
                tone(0, 196, .24, 'sine', .17, 246.94);
                tone(.12, 293.66, .24, 'triangle', .15, 369.99);
                tone(.27, 440, .32, 'sine', .17, 659.25);
                tone(.48, 987.77, .48, 'sine', .13, 1318.51);
                break;
            case 'gta5':
            default:
                tone(0, 110, .48, 'sine', .28, 58);
                tone(.18, 440, .42, 'triangle', .14, 440);
                tone(.30, 660, .42, 'sine', .13, 660);
                tone(.42, 880, .50, 'sine', .12, 880);
                break;
        }

        runtimeSetTimeout(() => {
            try { master.disconnect(); } catch (err) {}
        }, 1700);
    }

    function playPayoutSound(tier, template = state.payoutFlash.template) {
        if (!state.payoutFlash.soundEnabled || state.payoutFlash.soundVolume <= 0) return;
        if (PAYOUT_MEDIA_SOUNDS[template]) {
            playPayoutMediaSound(template).then(played => {
                if (!played) playSynthPayoutSound(tier, template);
            });
            return;
        }
        playSynthPayoutSound(tier, template);
    }

    function animatePayoutAmount(element, amount, duration, reducedMotion) {
        if (!element) return;
        if (payoutAmountAnimationFrame) runtimeCancelAnimationFrame(payoutAmountAnimationFrame);
        const target = Math.max(0, Math.round(Number(amount) || 0));
        if (reducedMotion) { element.textContent = `+${target.toLocaleString()} CREDITS`; return; }
        const animationDuration = Math.min(1250, Math.max(550, duration * 0.22));
        const started = performance.now();
        const tick = time => {
            const progress = Math.min(1, (time - started) / animationDuration);
            const eased = 1 - Math.pow(1 - progress, 3);
            element.textContent = `+${Math.round(target * eased).toLocaleString()} CREDITS`;
            if (progress < 1) payoutAmountAnimationFrame = runtimeRequestAnimationFrame(tick);
            else payoutAmountAnimationFrame = null;
        };
        payoutAmountAnimationFrame = runtimeRequestAnimationFrame(tick);
    }

    function readCurrentCreditTotal() {
        const valueElement = document.querySelector('.credits-value');
        if (!valueElement) return null;
        return parseCreditValue(valueElement.textContent);
    }

    function positionPayoutFlashOverlay(overlay, mapEl = getLargestLeafletMap()) {
        if (!overlay || !mapEl || !mapEl.isConnected) {
            if (overlay) {
                overlay.style.setProperty('opacity', '0', 'important');
                overlay.style.setProperty('display', 'none', 'important');
            }
            return false;
        }

        // v4.8.4: payout presentation is a map layer, never a browser top-layer
        // element. Reparenting it into the active Leaflet container ensures every
        // MissionChief menu, modal and Toolkit drawer naturally remains above it.
        try {
            if (typeof overlay.hidePopover === 'function' && overlay.matches(':popover-open')) overlay.hidePopover();
        } catch (err) {}
        overlay.removeAttribute('popover');
        if (overlay.parentElement !== mapEl) mapEl.appendChild(overlay);

        try {
            const mapStyle = pageWindow.getComputedStyle(mapEl);
            if (mapStyle.position === 'static') mapEl.style.setProperty('position', 'relative');
            // Keep the payout z-index inside the map's own stacking context so it
            // cannot escape above MissionChief sidebars, dropdowns or dialogs.
            mapEl.style.setProperty('isolation', 'isolate');
            mapEl.dataset.mcmsPayoutHost = 'true';
        }
```

## `processTransportSweepMission`

_NOT FOUND_

## `startTransportSweep`

_NOT FOUND_

## `stopTransportSweep`

_NOT FOUND_

## `closeTransportSweepWindows`

_NOT FOUND_

## Selector and markup references

```text
16514:         const host = document.querySelector(`#${SCRIPT.panelId} [data-transport-sweep]`);
16530:         const start = document.querySelector(`#${SCRIPT.panelId} [data-action="start-transport-sweep"]`);
16531:         const stop = document.querySelector(`#${SCRIPT.panelId} [data-action="stop-transport-sweep"]`);
16532:         const scan = document.querySelector(`#${SCRIPT.panelId} [data-action="scan-transport-sweep"]`);
28169:                     <button class="mcms-small-btn" type="button" data-action="scan-transport-sweep">Scan Transports</button>
28170:                     <button class="mcms-small-btn" type="button" data-action="start-transport-sweep">Start Sweep</button>
28171:                     <button class="mcms-small-btn" type="button" data-action="stop-transport-sweep">Stop</button>
28173:                 <div class="mcms-row"><span class="mcms-row-label">Delay between clears</span><select class="mcms-select" data-setting="transport-sweep-delay"><option value="1500">1.5 seconds</option><option value="2000">2 seconds</option><option value="2500">2.5 seconds</option><option value="3000">3 seconds</option><option value="4000">4 seconds</option><option value="5000">5 seconds</option></select></div>
28174:                 <div class="mcms-row"><span class="mcms-row-label">Maximum per run</span><input class="mcms-input" type="number" min="1" max="50" step="1" data-setting="transport-sweep-max"></div>
28175:                 <div data-transport-sweep></div>
28522:         if (action === 'scan-transport-sweep') { const queue = buildTransportSweepQueue(); showToast(queue.length ? `${queue.length} transport mission${queue.length === 1 ? '' : 's'} found` : 'No alliance patient transports found'); return; }
28523:         if (action === 'start-transport-sweep') { startTransportSweep(); return; }
28524:         if (action === 'stop-transport-sweep') { stopTransportSweep(); return; }
28606:         if (setting === 'transport-sweep-delay') {
28612:         if (setting === 'transport-sweep-max') {
28917:         const transportSweepDelay = panel.querySelector('[data-setting="transport-sweep-delay"]');
28919:         const transportSweepMax = panel.querySelector('[data-setting="transport-sweep-max"]');
```
