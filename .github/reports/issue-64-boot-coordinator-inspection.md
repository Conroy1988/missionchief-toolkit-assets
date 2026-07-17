# Issue #64 boot coordinator inspection

Generated from the exact canonical userscript on the isolated extraction branch.
No Toolkit runtime or distribution file is changed by this inspection.

## `boot()`

Lines `29735-30069` · 335 lines

```javascript
function boot() {
        if (runtime.destroyed || bootStarted) return;
        bootStarted = true;
        bootStartedAt = Date.now();
        const bootPerformanceStartedAt = startupClock();
        applyRootAttributes();
        if (installAllianceBuildingsPageOptimisation()) return;
        createCleanExit();
        if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
        installMissionMarkerAddHook();
        installRadioMessageHook();
        lastObservedCredits = readCurrentCreditTotal();
        installCreditsUpdateHook();
        observeCreditValue();

        let attempts = 0;
        const runBootAttempt = () => {
            attempts += 1;
            installMissionMarkerAddHook();
            installRadioMessageHook();
            installCreditsUpdateHook();
            observeCreditValue();
            const ready = ensureUi();
            const mapReady = Boolean(getLargestLeafletMap());
            if (ready && (mapReady || attempts >= 12)) {
                recordStartupMetric('coreUiReadyMs', bootPerformanceStartedAt, { bootAttempts: attempts });
                scheduleMarkerStateSync(0, false);
                scheduleDeferredOperationalStartup();
                runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
                return;
            }
            if (attempts >= 90 || runtime.destroyed) return;
            const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
            runtimeSetTimeout(runBootAttempt, delay);
        };
        runtimeSetTimeout(runBootAttempt, 250);

        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
            if (state.economyMode && economyMapMoving) {
                economyDeferredDomMutation = true;
                return;
            }
            let externalMutationFound = false;
            let addedLeafletMarker = false;
            let missionChanged = false;
            let layoutChanged = false;
            let toolkitUiRemoved = false;
            for (const mutation of mutations) {
                if (mutationBelongsToToolkit(mutation)) continue;
                externalMutationFound = true;
                if (!addedLeafletMarker && mutationAddsLeafletMarkerIcon(mutation)) {
                    addedLeafletMarker = true;
                    missionChanged = true;
                }
                if (!missionChanged && mutationAffectsMissionData(mutation)) missionChanged = true;
                if (!layoutChanged && mutationAffectsMapLayout(mutation)) layoutChanged = true;
                if (!toolkitUiRemoved && mutationRemovesToolkitUi(mutation)) toolkitUiRemoved = true;
                if (addedLeafletMarker && missionChanged && layoutChanged && toolkitUiRemoved) break;
            }
            if (!externalMutationFound) return;
            missionChanged ||= addedLeafletMarker;
            if (!missionChanged && !layoutChanged && !toolkitUiRemoved) return;

            if (addedLeafletMarker) {
                invalidateMarkerRegistryCaches('all');
                scheduleMarkerStateSync(0, false);
                if (!state.visibility.buildings) scheduleMarkerStateSync(180, true);
            }
            if (layoutChanged) invalidateMapElementCache();
            if (document.hidden || dragState || (state.economyMode && economyMapMoving)) return;

            runtimeClearTimeout(mutationTimer);
            const startupSettling = bootStartedAt > 0 && Date.now() - bootStartedAt < STARTUP_SETTLE_WINDOW_MS;
            const mutationDelay = startupSettling
                ? STARTUP_MUTATION_DEBOUNCE_MS
                : (state.economyMode ? Math.max(320, DOM_REFRESH_DEBOUNCE_MS) : DOM_REFRESH_DEBOUNCE_MS);
            mutationTimer = runtimeSetTimeout(() => {
                if (dragState || document.hidden || runtime.destroyed || (state.economyMode && economyMapMoving)) return;
                const panelMissing = settingsPanelActivated && !document.getElementById(SCRIPT.panelId);
                const mapElement = getLargestLeafletMap();
                const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));
                if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();
                if (mainMutationObserverFallbackActive && (mapElement || document.querySelector('#missions, #mission_list, .missions-panel, .mission-list'))) {
                    connectMainMutationObserver();
                }
                if (layoutChanged) {
                    refreshSuppression();
                    fitControlToMap();
                    schedulePanelPosition(true, 50);
                    scheduleCriticalDrawerDock(60);
                }
                if (missionChanged) scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
            }, mutationDelay);
        }));
        mainMutationObserver = observer;

        runtimeListen(document, 'keydown', handleKeyboard);
        runtimeListen(document, 'pointerover', handleMissionInspectorPointerOver, true);
        runtimeListen(document, 'pointermove', handleMissionInspectorPointerMove, true);
        runtimeListen(document, 'pointerout', handleMissionInspectorPointerOut, true);
        runtimeListen(document, 'pointerdown', () => unlockPayoutAudio(), { once: true, capture: true });
        runtimeListen(document, 'click', event => {
            runtimeSetTimeout(refreshSuppression, 0);
            if (suppressNextOutsideClick) {
                event.preventDefault();
                event.stopPropagation();
                suppressNextOutsideClick = false;
                return;
            }

            const control = document.getElementById(SCRIPT.controlId);
            const panel = document.getElementById(SCRIPT.panelId);
            if (!panel || !panel.classList.contains('mcms-open')) return;
            if (control && control.contains(event.target)) return;
            if (panel.contains(event.target)) return;
            closePanel();
        }, true);

        runtimeListen(pageWindow, 'resize', () => {
            invalidateMapElementCache();
            applyRootAttributes();
            refreshTabletModeUi();
            scheduleTabletLayoutRefresh(20);
            const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
            if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay);
            if (dragState) return;
            refreshSuppression();
            fitControlToMap();
            schedulePanelPosition(true, 40);
            scheduleCriticalDrawerDock(30);
            scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
            scheduleMajorIncidentFeedLayout();
        });

        runtimeListen(pageWindow, 'scroll', scheduleMajorIncidentFeedLayout, { passive: true });
        runtimeListen(pageWindow, 'orientationchange', () => scheduleTabletLayoutRefresh(30));
        if (pageWindow.visualViewport) {
            runtimeListen(pageWindow.visualViewport, 'resize', () => scheduleTabletLayoutRefresh(20));
            runtimeListen(pageWindow.visualViewport, 'scroll', () => {
                if (isTouchLayoutActive() && document.getElementById(SCRIPT.panelId)?.classList.contains('mcms-open')) scheduleTabletLayoutRefresh(20);
            });
        }
        try {
            const coarsePointerQuery = pageWindow.matchMedia?.('(any-pointer: coarse)');
            if (coarsePointerQuery?.addEventListener) runtimeListen(coarsePointerQuery, 'change', () => scheduleTabletLayoutRefresh(20));
        } catch (err) {}

        runtimeListen(pageWindow, 'focus', () => {
            if (dragState) return;
            refreshSuppression();
            fitControlToMap();
            schedulePanelPosition(true, 40);
            installRadioMessageHook();
            if (vehicleDataNeeded()) refreshPersonalVehicleData(false);
            if (state.economyMode) scheduleEconomyLayerSync(0);
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
            scheduleOperationalPanelsRender(500);
            scheduleMajorIncidentFeedRender(80);
        });

        const recoverUiAfterNavigation = event => {
            runtimeSetTimeout(() => {
                if (runtime.destroyed || document.hidden) return;
                invalidateMapElementCache();
                ensureUi();
                connectMainMutationObserver();
                recoverMajorIncidentFeed(event?.type || 'navigation');
            }, 120);
            runtimeSetTimeout(() => {
                if (runtime.destroyed || document.hidden) return;
                recoverMajorIncidentFeed(`${event?.type || 'navigation'} settle`);
            }, 650);
        };
        runtimeListen(pageWindow, 'pageshow', recoverUiAfterNavigation);
        runtimeListen(pageWindow, 'popstate', recoverUiAfterNavigation);
        runtimeListen(pageWindow, 'hashchange', recoverUiAfterNavigation);

        runtimeRegisterTask('vehicle-data-refresh', VEHICLE_API_REFRESH_MS, () => {
            if (!vehicleDataNeeded()) return;
            installRadioMessageHook();
            return refreshPersonalVehicleData(false);
        }, {
            economyIntervalMs: 10 * 60 * 1000,
            economyIntervalResolver: () => operationalUiIsVisible() || document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open') ? 2 * 60 * 1000 : 10 * 60 * 1000
        });
        runtimeRegisterTask('auto-night', 60 * 1000, () => runAutoNight(false), { intervalResolver: () => state.autoNight.enabled ? 60 * 1000 : 15 * 60 * 1000, economyIntervalMs: 5 * 60 * 1000, economyIntervalResolver: () => state.autoNight.enabled ? 5 * 60 * 1000 : 30 * 60 * 1000 });
        runtimeRegisterTask('mission-maintenance', FALLBACK_MISSION_REFRESH_MS, () => {
            if (state.economyMode && economyMapMoving) {
                economyDeferredMapRefresh = true;
                return;
            }
            installMissionMarkerAddHook();
            installRadioMessageHook();
            installCreditsUpdateHook();
            observeCreditValue();
            if (state.allianceCredits) scheduleAllianceCreditRefresh();
            if (state.unitCommitment) scheduleUnitCommitmentRefresh();
            if (state.resourceGap.enabled) scheduleResourceGapRefresh();
            if (missionSnapshotsNeeded()) scheduleMissionSnapshotRefresh();
            const criticalDrawer = document.getElementById(SCRIPT.criticalDrawerId);
            if (criticalDrawer?.classList.contains('mcms-open')) {
                let hasClearingMission = false;
                for (const snapshot of liveMissionSnapshots.values()) {
                    const progress = criticalMissionClearingProgress(snapshot);
                    const units = snapshot?.units || personalUnitCommitmentForMission(snapshot?.missionId);
                    if (progress && Math.max(0, Number(units?.onScene) || 0) > 0) {
                        hasClearingMission = true;
                        break;
                    }
                }
                const refreshInterval = hasClearingMission ? CRITICAL_PROGRESS_REFRESH_ACTIVE_MS : CRITICAL_PROGRESS_REFRESH_IDLE_MS;
                return refreshMissionProgressFromPage(false, refreshInterval).then(refreshed => {
                    if (!refreshed || document.hidden || !criticalDrawer.classList.contains('mcms-open')) return;
                    refreshMissionSnapshots();
                    criticalDrawerLastDataSyncAt = Math.max(criticalDrawerLastDataSyncAt, missionProgressPageLastSuccessAt);
                    renderOperationalPanels(true, { updateViewTime: false, preserveScroll: true });
                });
            }
        }, {
            economyIntervalMs: 60 * 1000,
            economyIntervalResolver: () => document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open') ? 30 * 1000 : 60 * 1000
        });
        runtimeRegisterTask('critical-countdowns', 1000, () => {
            if (document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open')) refreshCriticalClearingCountdowns();
        }, {
            intervalResolver: () => document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open') ? 1000 : 60 * 1000,
            economyIntervalMs: 10000,
            economyIntervalResolver: () => document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open') ? 10000 : 60 * 1000
        });
        runtimeRegisterTask('minute-maintenance', 60 * 1000, () => {
            if (state.missionAge) scheduleMissionAgeRefresh();
            if (state.stuckDetector.enabled) scheduleStuckMissionRefresh();
            refreshVisibleMissionInspector();
            scheduleOperationalPanelsRender(500);
            pruneRuntimeCaches();
        }, {
            economyIntervalMs: 5 * 60 * 1000,
            economyIntervalResolver: () => operationalUiIsVisible() ? 2 * 60 * 1000 : 5 * 60 * 1000
        });
        runtimeRegisterTask('major-incident-feed-integrity', 5000, () => {
            if (!state.majorIncidentFeed.enabled) return;
            recoverMajorIncidentFeed('integrity check');
        }, {
            intervalResolver: () => state.majorIncidentFeed.enabled ? 5000 : 60 * 1000,
            economyIntervalMs: 12000,
            economyIntervalResolver: () => state.majorIncidentFeed.enabled ? 12000 : 2 * 60 * 1000
        });
        runtimeRegisterTask('building-visibility', BUILDING_VISIBILITY_RECHECK_MS, () => {
            if (!state.visibility.buildings) synchronisePersonalBuildingVisibility();
            if (state.economyMode) scheduleEconomyLayerSync(0);
        }, {
            intervalResolver: () => !state.visibility.buildings ? BUILDING_VISIBILITY_RECHECK_MS : 60 * 1000,
            economyIntervalMs: 45 * 1000,
            economyIntervalResolver: () => (!state.visibility.buildings || state.economyMode) ? 45 * 1000 : 2 * 60 * 1000
        });
        runtimeListen(document, 'visibilitychange', () => {
            if (document.hidden) return;
            runtimeWakeTaskScheduler(0);
            ensureUi();
            refreshSuppression();
            if (vehicleDataNeeded()) refreshPersonalVehicleData(false);
            if (state.economyMode) scheduleEconomyLayerSync(0);
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: true });
            scheduleMajorIncidentFeedRender(80);
        });
        runtimeSetTimeout(() => {
            if (document.hidden || !operationalStartupComplete) return;
            scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
        }, 2200);

        runtimeOnCleanup(() => {
            stopAutoLoadAllVehicles();
            transportSweepRuntime.stopRequested = true;
            document.removeEventListener('mousemove', movePanelDrag, true);
            document.removeEventListener('mouseup', endPanelDrag, true);
            document.removeEventListener('touchmove', movePanelDrag, true);
            document.removeEventListener('touchend', endPanelDrag, true);
            document.removeEventListener('touchcancel', endPanelDrag, true);
            document.documentElement.style.cursor = '';
            if (document.body) document.body.style.userSelect = '';
            restoreEconomyLayers();
            restoreLeafletEconomyPolicy();
            disposeEconomyCanvasRenderer();
            runtimeClearTimeout(majorIncidentFeedLayoutTimer);
            majorIncidentFeedLayoutTimer = null;
            const originalBuildingVisibility = state.visibility.buildings;
            try {
                state.visibility.buildings = true;
                synchronisePersonalBuildingVisibility(cachedMap);
            } catch (err) {
                console.debug(`[${SCRIPT.name}] Building visibility restoration skipped during teardown.`, err);
            } finally {
                state.visibility.buildings = originalBuildingVisibility;
            }
            try { creditsValueObserver?.disconnect(); } catch (err) {}
            removeMajorIncidentFeed();
            clearMissionLockOnEffect();
            clearAllianceCreditLabels();
            clearMissionAgeLabels();
            clearUnitCommitmentLabels();
            clearTransportWatcherLabels();
            clearResourceGapLabels();
            clearStuckMissionLabels();
            clearCoverageHeatmap();
            if (coverageGroup) {
                try { coverageGroup.clearLayers(); coverageGroup.remove(); } catch (err) {}
                coverageGroup = null;
            }
            stopPayoutFlashAnimation();
            disposePayoutMediaAudio();
            try { payoutAudioContext?.close?.(); } catch (err) {}
            clearDiscordPreviewChartUrl();
            closeHelpCenter({ restoreFocus: false });
            helpGuideDocumentCache = '';
            helpGuideLoadedAt = 0;
            stopDesktopPanelWorkspaceObservation();
            runtimeUntrackObserver(desktopPanelResizeObserver);
            desktopPanelResizeObserver = null;
            runtimeUntrackObserver(majorIncidentFeedResizeObserver);
            majorIncidentFeedResizeObserver = null;
            majorIncidentFeedObservedElement = null;
            missionSnapshotCache.clear();
            missionPanelCache.clear();
            missionOverlayVersions.clear();
            markerRegistryCache.clear();
            criticalMissionStableCache.clear();
            removeOldInstances();
            const root = document.documentElement;
            for (const attribute of ['data-mcms-ui-theme', 'data-mc-map-skin', 'data-mcms-clean', 'data-mcms-marker-focus', 'data-mcms-mission-pulse', 'data-mcms-road-priority', 'data-mcms-compact-dock', 'data-mcms-command-bar-open', 'data-mcms-economy', 'data-mcms-map-moving', 'data-mcms-alliance-buildings-map', 'data-mcms-alliance-buildings-page', 'data-mcms-device-layout', 'data-mcms-tablet-mode', 'data-mcms-tablet-active', 'data-mcms-tablet-orientation', 'data-mcms-mobile-mode', 'data-mcms-mobile-active', 'data-mcms-mobile-orientation', 'data-mcms-show-alliance-missions', 'data-mcms-show-my-missions', 'data-mcms-show-vehicles', 'data-mcms-show-buildings', 'data-mcms-critical-view', 'data-mcms-help-open']) root.removeAttribute(attribute);
        });

        runtimeSetTimeout(() => runAutoNight(true), 180);
        if (state.economyMode) runtimeSetTimeout(() => setEconomyMode(true, false), 420);
        console.debug(`[${SCRIPT.name}] v${SCRIPT.version} audited runtime ready.`);
    }
```

## `scheduleBoot()`

Lines `30071-30074` · 4 lines

```javascript
function scheduleBoot() {
        if (runtime.destroyed || bootStarted) return;
        runtimeRunWhenIdle(boot, STARTUP_IDLE_TIMEOUT_MS);
    }
```

## Document-start bootstrap tail

Lines `30076-30081` · 6 lines

```javascript
if (document.readyState === 'loading') {
        runtimeListen(document, 'DOMContentLoaded', scheduleBoot, { once: true });
    } else {
        scheduleBoot();
    }

```
