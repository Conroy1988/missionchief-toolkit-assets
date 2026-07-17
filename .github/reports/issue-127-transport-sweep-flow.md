# Issue #127 exact Transport Sweep flow

## processTransportSweepMission — line 17213

```javascript
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

```

## startTransportSweep — line 17353

```javascript
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

```

## stopTransportSweep — line 17422

```javascript
function stopTransportSweep() {
        if (!transportSweepRuntime.running) return;
        transportSweepRuntime.stopRequested = true;
        transportSweepLog('Stop requested — finishing the current action');
        renderTransportSweepPanel();
    }

```

## transportSweepLog — line 16474

```javascript
function transportSweepLog(message, level = 'info') {
        const clean = String(message || '').trim();
        if (!clean) return;
        transportSweepRuntime.log.unshift({ time: Date.now(), message: clean, level });
        if (transportSweepRuntime.log.length > 18) transportSweepRuntime.log.length = 18;
        renderTransportSweepPanel();
    }

```

## transportSweepReleaseConfirmationVisible — line 16930

```javascript
function transportSweepReleaseConfirmationVisible() {
        const text = transportSweepVisibleWindowRoots()
            .map(root => String(root.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase())
            .join(' | ');
        return /released the patient|patient (?:is not|isn['’]t) transported|patient.*released|patient.*discharged/.test(text);
    }

```

## renderTransportSweepPanel — line 16513

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

## Existing sweep CSS context — line 2482

```css

        #${SCRIPT.panelId} .mcms-discord-mini-stats span { min-width:0 !important; padding:5px 4px !important; border-radius:7px !important; background:rgba(88,166,255,.07) !important; color:rgba(255,255,255,.52) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }
        #${SCRIPT.panelId} .mcms-discord-mini-stats b { display:block !important; margin-top:2px !important; color:#fff !important; font-size:7.8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-discord-chart { display:block !important; width:100% !important; margin-top:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:#0b1018 !important; }
        #${SCRIPT.panelId} .mcms-discord-date-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
        #${SCRIPT.panelId} .mcms-discord-date-grid .mcms-row { grid-template-columns:56px minmax(0,1fr) !important; }
        #${SCRIPT.panelId} .mcms-finance-vault-summary { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:5px !important; margin:7px 0 !important; }
        #${SCRIPT.panelId} .mcms-finance-vault-summary span { min-width:0 !important; padding:7px 5px !important; border:1px solid rgba(88,166,255,.18) !important; border-radius:8px !important; background:rgba(88,166,255,.055) !important; color:rgba(255,255,255,.54) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }
        #${SCRIPT.panelId} .mcms-finance-vault-summary b { display:block !important; margin-bottom:2px !important; color:#fff !important; font-size:8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-finance-vault-summary small { grid-column:1/-1 !important; padding:5px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; color:rgba(255,255,255,.48) !important; font-size:7.2px !important; line-height:1.35 !important; text-align:center !important; }
        #${SCRIPT.panelId} .mcms-finance-private-note { border-color:rgba(241,196,15,.34) !important; color:#f5d984 !important; }
        #${SCRIPT.panelId} .mcms-sweep-card { margin-top:8px !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,183,72,.28) !important; background:rgba(88,46,4,.13) !important; }
        #${SCRIPT.panelId} .mcms-sweep-head { display:flex !important; justify-content:space-between !important; align-items:center !important; gap:8px !important; color:#ffe0a3 !important; font-size:9px !important; font-weight:950 !important; }
        #${SCRIPT.panelId} .mcms-sweep-state { padding:2px 6px !important; border-radius:999px !important; background:rgba(255,255,255,.10) !important; color:rgba(255,255,255,.78) !important; font-size:7px !important; letter-spacing:.35px !important; }
        #${SCRIPT.panelId} .mcms-sweep-state.mcms-running { background:rgba(255,145,24,.28) !important; color:#fff1cf !important; }
        #${SCRIPT.panelId} .mcms-sweep-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:7px !important; }
        #${SCRIPT.panelId} .mcms-sweep-stat { min-width:0 !important; padding:5px 3px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }
        #${SCRIPT.panelId} .mcms-sweep-stat b { display:block !important; color:#fff !important; font-size:11px !important; line-height:1 !important; }
        #${SCRIPT.panelId} .mcms-sweep-stat span { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.50) !important; font-size:6.5px !important; font-weight:900 !important; text-transform:uppercase !important; }
        #${SCRIPT.panelId} .mcms-sweep-queue { display:grid !important; gap:4px !important; max-height:128px !important; overflow-y:auto !important; margin-top:7px !important; padding-right:2px !important; overscroll-behavior:contain !important; scrollbar-width:thin !important; }
        #${SCRIPT.panelId} .mcms-sweep-entry { display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:6px !important; padding:6px !important; border-radius:7px !important; border:1px solid rgba(255,255,255,.08) !important; background:rgba(255,255,255,.04) !important; }
        #${SCRIPT.panelId} .mcms-sweep-entry.mcms-current { border-color:rgba(255,177,57,.62) !important; background:rgba(255,145,24,.11) !important; }
        #${SCRIPT.panelId} .mcms-sweep-title { min-width:0 !important; color:#f7f8fb !important; font-size:8.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.panelId} .mcms-sweep-meta { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:800 !important; }
        #${SCRIPT.panelId} .mcms-sweep-count { color:#ffc86b !important; font-size:9px !important; font-weight:950 !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-sweep-log { max-height:72px !important; overflow-y:auto !important; margin-top:7px !important; padding:6px !important; border-radius:7px !important; background:rgba(0,0,0,.18) !important; color:rgba(255,255,255,.64) !important; font:700 7px/1.35 Arial,Helvetica,sans-serif !important; white-space:normal !important; }
        #${SCRIPT.panelId} .mcms-heat-legend { display: grid !important; grid-template-columns: repeat(5,minmax(0,1fr)) !important; gap: 3px !important; margin-top: 7px !important; }
        #${SCRIPT.panelId} .mcms-heat-key { padding: 4px 2px !important; border-radius: 6px !important; color: #fff !important; font-size: 7px !important; font-weight: 900 !important; text-align: center !important; text-shadow: 0 1px 2px #000 !important; }
        #${SCRIPT.panelId} .mcms-footer { margin: 9px 0 0 0 !important; padding: 7px 0 0 0 !important; border-top: 1px solid rgba(255,255,255,.10) !important; color: rgba(233,238,245,.58) !important; font-size: 9px !important; line-height: 1.25 !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-build { display: block !important; margin-top: 4px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }

        .mcms-mission-float-pane,
        .mcms-mission-float-pane * {
            pointer-events: none !important;
            touch-action: none !important;
        }
        .mcms-alliance-credit-icon,
        .mcms-mission-age-icon,
        .mcms-unit-commitment-icon,
        .mcms-transport-watcher-icon,
        .mcms-resource-gap-icon {
            width: 0 !important; height: 0 !important; overflow: visible !important;
            border: 0 !important; background: transparent !important;
            pointer-events: none !important; touch-action: none !important;
        }
        .mcms-alliance-credit-badge,
        .mcms-mission-age-badge,
        .mcms-unit-commitment-badge,
        .mcms-transport-watcher-badge,
        .mcms-resource-gap-badge {
            position: absolute !important; left: 0 !important; top: 0 !important;
            transform: translate(-50%, -50%) !important;
            display: inline-flex !important; align-items: center !important; justify-content: center !important;
            white-space: nowrap !important; pointer-events: none !important; touch-action: none !important;
            backdrop-filter: blur(3px) !important;
            -webkit-backdrop-filter: blur(3px) !important;
            text-shadow: 0 1px 2px rgba(0,0,0,.80) !important;
        }
        .mcms-alliance-credit-badge {
            min-width: 48px !important; height: 22px !important; padding: 0 7px !important; border-radius: 8px !important;
            border: 1px solid rgba(255,213,79,.46) !important; background: rgba(10,14,20,.46) !important;
            color: #ffe082 !important; box-shadow: 0 2px 7px rgba(0,0,0,.18) !important;
            font: 900 10px/1 Arial, Helvetica, sans-serif !important; letter-spacing: .1px !important;
        }
        .mcms-alliance-credit-badge.mcms-credit-qualified {
            border-color: rgba(76,225,126,.52) !important;
            color: #79f2a3 !important;
            text-shadow: 0 1px 2px rgba(0,0,0,.88), 0 0 5px rgba(44,210,103,.20) !important;
        }
        .mcms-alliance-credit-badge.mcms-credit-unqualified {
            border-color: rgba(255,213,79,.46) !important;
            color: #ffe082 !important;
        }
        .mcms-mission-age-badge {
            min-width: 38px !important; height: 20px !important; padding: 0 6px !important; border-radius: 7px !important;
            border: 1px solid rgba(100,181,246,.48) !important; background: rgba(10,14,20,.66) !important;
            color: #c8e6ff !important; box-shadow: 0 2px 7px rgba(0,0,0,.22) !important;
            font: 900 9.5px/1 Arial, Helvetica, sans-serif !important; letter-spacing: .1px !important;
            transition: color .18s ease, border-color .18s ease, background-color .18s ease, box-shadow .18s ease !important;
        }
        .mcms-mission-age-badge.mcms-age-aged {
            border-color: rgba(255,202,40,.88) !important;
            background: rgba(74,52,3,.88) !important;
            color: #fff0a8 !important;
            box-shadow: 0 2px 7px rgba(0,0,0,.28), 0 0 8px rgba(255,193,7,.30) !important;
        }
        .mcms-mission-age-badge.mcms-age-high {
            border-color: rgba(255,133,46,.96) !important;
            background: rgba(88,34,4,.92) !important;
            color: #ffd0a3 !important;
            box-shadow: 0 2px 7px rgba(0,0,0,.30), 0 0 10px rgba(255,111,0,.42) !important;
        }
        .mcms-mission-age-badge.mcms-age-critical {
            border-color: rgba(255,72,72,1) !important;
            background: rgba(102,8,12,.95) !important;
            color: #ffe3e3 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,.34), 0 0 12px rgba(255,45,45,.58) !important;
            text-shadow: 0 1px 2px rgba(0,0,0,.90), 0 0 5px rgba(255,104,104,.42) !important;
        }


        .mcms-unit-commitment-badge {
            min-width: 42px !important; height: 18px !important; padding: 0 6px !important; border-radius: 7px !important;
            border: 1px solid rgba(255,255,255,.42) !important; background: rgba(10,14,20,.46) !important;
            color: #f4f7ff !important; box-shadow: 0 2px 7px rgba(0,0,0,.18) !important;
            font: 900 8.5px/1 Arial, Helvetica, sans-serif !important; letter-spacing: .15px !important;
        }
        .mcms-unit-commitment-badge.mcms-unit-personal { border-color: rgba(244,200,79,.54) !important; color: #ffe082 !important; }
        .mcms-unit-commitment-badge.mcms-unit-alliance { border-color: rgba(76,225,126,.54) !important; color: #79f2a3 !important; }


        .mcms-transport-watcher-badge {
            width: 25px !important; height: 25px !important; padding: 0 !important; border-radius: 8px !important;
            border: 1px solid rgba(255,193,74,.94) !important; background: linear-gradient
```

## Runtime state updates

```text
16464:             if (runtime.destroyed || transportSweepRuntime.stopRequested) return null;
16779:         if (id === null || transportSweepRuntime.stopRequested) return null;
16786:             if (transportSweepRuntime.stopRequested) return null;
16925:         if (!first?.length || transportSweepRuntime.stopRequested) return [];
16938:         if (!candidate?.actionHref || transportSweepRuntime.stopRequested) return false;
17142:         if (transportSweepRuntime.stopRequested) return false;
17145:         if (!closed || transportSweepRuntime.stopRequested) return false;
17177:             return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
17194:         return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
17198:         if (transportSweepRuntime.stopRequested || !candidate?.href) return null;
17201:         if (!opened || transportSweepRuntime.stopRequested) return null;
17217:         transportSweepRuntime.currentMissionId = missionId;
17230:         if (!missionOpen || transportSweepRuntime.stopRequested) {
17231:             if (!transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
17235:         while (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
17238:                 if (transportSweepRuntime.stopRequested) break;
17244:                     transportSweepRuntime.currentVehicleHref = lssmCandidate.actionHref;
17251:                         transportSweepRuntime.cleared += 1;
17252:                         transportSweepRuntime.processed += 1;
17255:                         transportSweepRuntime.errors += 1;
17259:                     if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
17264:                             transportSweepRuntime.errors += 1;
17303:             transportSweepRuntime.currentVehicleHref = candidate.href;
17308:             if (transportSweepRuntime.stopRequested) break;
17326:                     transportSweepRuntime.cleared += 1;
17327:                     transportSweepRuntime.processed += 1;
17330:                     transportSweepRuntime.errors += 1;
17335:             if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
17340:                     transportSweepRuntime.errors += 1;
17349:         if (clearedHere === 0 && !transportSweepRuntime.stopRequested) transportSweepRuntime.skipped += 1;
17354:         if (transportSweepRuntime.running) return;
17373:         transportSweepRuntime.running = true;
17374:         transportSweepRuntime.stopRequested = false;
17375:         transportSweepRuntime.currentMissionId = null;
17376:         transportSweepRuntime.currentVehicleHref = '';
17377:         transportSweepRuntime.cleared = 0;
17378:         transportSweepRuntime.skipped = 0;
17379:         transportSweepRuntime.errors = 0;
17380:         transportSweepRuntime.processed = 0;
17394:                 if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;
17395:                 const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;
17397:                 if (!transportSweepRuntime.stopRequested) await transportSweepSleep(state.transportSweep.delayMs);
17400:             transportSweepRuntime.errors += 1;
17404:             const wasStopped = transportSweepRuntime.stopRequested;
17405:             transportSweepRuntime.running = false;
17406:             transportSweepRuntime.stopRequested = false;
17407:             transportSweepRuntime.currentMissionId = null;
17408:             transportSweepRuntime.currentVehicleHref = '';
17417:             showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared`);
17418:             transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`);
17423:         if (!transportSweepRuntime.running) return;
17424:         transportSweepRuntime.stopRequested = true;
18204:             transportSweepRuntime.running
29877:             transportSweepRuntime.stopRequested = true;
```
