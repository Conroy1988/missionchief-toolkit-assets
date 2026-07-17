# Issue #64 Boot/Lifecycle inspection

Source lines: 29951

## Runtime ownership block — canonical lines 480–850

```javascript
00480:     if (earlyAllianceBuildingsPage) {
00481:         document.documentElement?.setAttribute('data-mcms-alliance-buildings-page', 'true');
00482:         document.documentElement?.setAttribute('data-mcms-alliance-buildings-map', earlyAllianceBuildingsMapEnabled ? 'enabled' : 'disabled');
00483:     }
00484:     if (!earlyAllianceBuildingsMapEnabled) {
00485:         installAllianceBuildingsEarlyStyle();
00486:         installAllianceBuildingsLeafletAssignmentGuard();
00487:         installAllianceBuildingsContextWatcherEarly();
00488:     }
00489: 
00490: 
00491:     const SCRIPT = {
00492:         name: 'MissionChief Map Command Toolkit',
00493:         version: '4.14.8',
00494:         author: 'Conroy1988',
00495:         controlId: 'mc-map-command-toolkit-control',
00496:         panelId: 'mc-map-command-toolkit-panel',
00497:         toastId: 'mc-map-command-toolkit-toast',
00498:         payoutFlashId: 'mc-map-command-toolkit-payout-flash',
00499:         criticalDrawerId: 'mc-map-command-toolkit-critical-drawer',
00500:         vehicleStatusId: 'mc-map-command-toolkit-vehicle-status',
00501:         majorIncidentFeedId: 'mc-map-command-toolkit-major-incident-feed',
00502:         missionInspectorId: 'mc-map-command-toolkit-mission-inspector',
00503:         helpCenterId: 'mc-map-command-toolkit-help-center',
00504:         cleanExitId: 'mcms-clean-exit',
00505:         styleId: 'mc-map-command-toolkit-style-v4146',
00506:         oldControlId: 'mc-map-command-skins-control',
00507:         oldGeoLabelLayerId: 'mcms-persistent-label-layer',
00508:         storageState: 'mc_map_command_toolkit_state_v150',
00509:         payoutHistoryState: 'mc_map_command_toolkit_payout_history_v200',
00510:         sessionPerformanceState: 'mc_map_command_toolkit_session_v200',
00511:         missionProgressState: 'mc_map_command_toolkit_mission_progress_v250',
00512:         discordWebhookState: 'mc_map_command_toolkit_discord_webhook_v300',
00513:         discordLastReportState: 'mc_map_command_toolkit_discord_last_report_v310',
00514:         financeVaultState: 'mc_map_command_toolkit_finance_vault_v450',
00515:         financeVaultCredentialState: 'mc_map_command_toolkit_finance_vault_credential_v450',
00516:         financeRulesCacheState: 'mc_map_command_toolkit_finance_rules_v450',
00517:         financePolicyCacheState: 'mc_map_command_toolkit_finance_policy_v460',
00518:         oldStorageKeys: [
00519:             'mc_map_command_toolkit_state_v149',
00520:             'mc_map_command_toolkit_state_v148',
00521:             'mc_map_command_toolkit_state_v147',
00522:             'mc_map_command_toolkit_state_v146',
00523:             'mc_map_command_toolkit_state_v145',
00524:             'mc_map_command_toolkit_state_v144',
00525:             'mc_map_command_toolkit_state_v143',
00526:             'mc_map_command_toolkit_state_v142',
00527:             'mc_map_command_toolkit_state_v141',
00528:             'mc_map_command_toolkit_state_v140',
00529:             'mc_map_command_toolkit_state_v130'
00530:         ],
00531:         legacyTheme: 'mc_map_command_skins_theme_v2',
00532:         legacyPosition: 'mc_map_command_skins_position_v1'
00533:     };
00534: 
00535:     const RUNTIME_KEY = '__MC_MAP_COMMAND_TOOLKIT_RUNTIME__';
00536:     const previousRuntime = pageWindow[RUNTIME_KEY];
00537:     if (previousRuntime?.version === SCRIPT.version && previousRuntime.destroyed !== true) return;
00538:     try { previousRuntime?.destroy?.('replaced by a newer toolkit runtime'); } catch (err) {}
00539: 
00540:     const runtime = {
00541:         version: SCRIPT.version,
00542:         destroyed: false,
00543:         timeouts: new Set(),
00544:         intervals: new Set(),
00545:         animationFrames: new Set(),
00546:         observers: new Set(),
00547:         waiters: new Set(),
00548:         requests: new Set(),
00549:         fetchControllers: new Set(),
00550:         listeners: [],
00551:         mapBindings: [],
00552:         hookRestorers: [],
00553:         cleanupCallbacks: [],
00554:         destroy(reason = 'runtime shutdown') {
00555:             if (this.destroyed) return;
00556:             this.destroyed = true;
00557:             for (const id of this.timeouts) { try { pageWindow.clearTimeout(id); } catch (err) {} }
00558:             for (const id of this.intervals) { try { pageWindow.clearInterval(id); } catch (err) {} }
00559:             for (const id of this.animationFrames) { try { pageWindow.cancelAnimationFrame(id); } catch (err) {} }
00560:             this.timeouts.clear();
00561:             this.intervals.clear();
00562:             this.animationFrames.clear();
00563:             for (const settle of Array.from(this.waiters)) { try { settle(false); } catch (err) {} }
00564:             this.waiters.clear();
00565:             for (const request of Array.from(this.requests)) { try { request.abort?.(); } catch (err) {} }
00566:             this.requests.clear();
00567:             for (const controller of Array.from(this.fetchControllers)) { try { controller.abort(); } catch (err) {} }
00568:             this.fetchControllers.clear();
00569:             for (const observer of this.observers) { try { observer.disconnect(); } catch (err) {} }
00570:             this.observers.clear();
00571:             for (const { target, type, listener, options } of this.listeners.splice(0)) {
00572:                 try { target.removeEventListener(type, listener, options); } catch (err) {}
00573:             }
00574:             for (const binding of this.mapBindings.splice(0)) {
00575:                 try { binding.map.off(binding.types, binding.handler); } catch (err) {}
00576:             }
00577:             for (const restore of this.hookRestorers.splice(0).reverse()) { try { restore(); } catch (err) {} }
00578:             for (const cleanup of this.cleanupCallbacks.splice(0).reverse()) { try { cleanup(reason); } catch (err) {} }
00579:             if (pageWindow[RUNTIME_KEY] === this) {
00580:                 try { delete pageWindow[RUNTIME_KEY]; } catch (err) { pageWindow[RUNTIME_KEY] = null; }
00581:             }
00582:         }
00583:     };
00584:     pageWindow[RUNTIME_KEY] = runtime;
00585: 
00586:     function runtimeSetTimeout(callback, delay = 0, ...args) {
00587:         if (runtime.destroyed) return null;
00588:         let id = null;
00589:         id = pageWindow.setTimeout((...callbackArgs) => {
00590:             runtime.timeouts.delete(id);
00591:             if (!runtime.destroyed) callback(...callbackArgs);
00592:         }, delay, ...args);
00593:         runtime.timeouts.add(id);
00594:         return id;
00595:     }
00596: 
00597:     function runtimeClearTimeout(id) {
00598:         if (id === null || id === undefined) return;
00599:         runtime.timeouts.delete(id);
00600:         try { pageWindow.clearTimeout(id); } catch (err) {}
00601:     }
00602: 
00603:     function runtimeDelay(delay = 0) {
00604:         if (runtime.destroyed) return Promise.resolve(false);
00605:         return new Promise(resolve => {
00606:             let timerId = null;
00607:             let settled = false;
00608:             const settle = completed => {
00609:                 if (settled) return;
00610:                 settled = true;
00611:                 runtime.waiters.delete(settle);
00612:                 if (timerId !== null) runtimeClearTimeout(timerId);
00613:                 resolve(Boolean(completed));
00614:             };
00615:             runtime.waiters.add(settle);
00616:             timerId = runtimeSetTimeout(() => settle(true), Math.max(0, Number(delay) || 0));
00617:             if (timerId === null) settle(false);
00618:         });
00619:     }
00620: 
00621:     function runtimeSetInterval(callback, delay = 0, ...args) {
00622:         if (runtime.destroyed) return null;
00623:         const id = pageWindow.setInterval((...callbackArgs) => {
00624:             if (!runtime.destroyed) callback(...callbackArgs);
00625:         }, delay, ...args);
00626:         runtime.intervals.add(id);
00627:         return id;
00628:     }
00629: 
00630:     function runtimeClearInterval(id) {
00631:         if (id === null || id === undefined) return;
00632:         runtime.intervals.delete(id);
00633:         try { pageWindow.clearInterval(id); } catch (err) {}
00634:     }
00635: 
00636:     function runtimeRequestAnimationFrame(callback) {
00637:         if (runtime.destroyed) return null;
00638:         let id = null;
00639:         id = pageWindow.requestAnimationFrame(timestamp => {
00640:             runtime.animationFrames.delete(id);
00641:             if (!runtime.destroyed) callback(timestamp);
00642:         });
00643:         runtime.animationFrames.add(id);
00644:         return id;
00645:     }
00646: 
00647:     function runtimeCancelAnimationFrame(id) {
00648:         if (id === null || id === undefined) return;
00649:         runtime.animationFrames.delete(id);
00650:         try { pageWindow.cancelAnimationFrame(id); } catch (err) {}
00651:     }
00652: 
00653:     function runtimeListen(target, type, listener, options) {
00654:         if (!target?.addEventListener || runtime.destroyed) return listener;
00655:         target.addEventListener(type, listener, options);
00656:         runtime.listeners.push({ target, type, listener, options });
00657:         return listener;
00658:     }
00659: 
00660:     function runtimeTrackObserver(observer) {
00661:         if (!observer) return observer;
00662:         if (runtime.destroyed) {
00663:             try { observer.disconnect(); } catch (err) {}
00664:             return observer;
00665:         }
00666:         runtime.observers.add(observer);
00667:         return observer;
00668:     }
00669: 
00670:     function runtimeUntrackObserver(observer, disconnect = true) {
00671:         if (!observer) return;
00672:         if (disconnect) {
00673:             try { observer.disconnect(); } catch (err) {}
00674:         }
00675:         runtime.observers.delete(observer);
00676:     }
00677: 
00678:     const runtimeTasks = new Map();
00679:     let runtimeTaskTimer = null;
00680: 
00681:     function runtimeWakeTaskScheduler(delay = 0) {
00682:         runtimeClearTimeout(runtimeTaskTimer);
00683:         runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(0, Number(delay) || 0));
00684:     }
00685: 
00686:     function runtimeRegisterTask(name, intervalMs, callback, options = {}) {
00687:         if (!name || typeof callback !== 'function') return null;
00688:         const interval = Math.max(250, Number(intervalMs) || 1000);
00689:         const initialDelay = Math.max(0, Number(options.initialDelayMs ?? interval) || 0);
00690:         runtimeTasks.set(String(name), {
00691:             name: String(name),
00692:             intervalMs: interval,
00693:             intervalResolver: typeof options.intervalResolver === 'function' ? options.intervalResolver : null,
00694:             economyIntervalMs: Math.max(interval, Number(options.economyIntervalMs) || interval),
00695:             economyIntervalResolver: typeof options.economyIntervalResolver === 'function' ? options.economyIntervalResolver : null,
00696:             callback,
00697:             runWhenHidden: Boolean(options.runWhenHidden),
00698:             nextRun: Date.now() + initialDelay,
00699:             running: false
00700:         });
00701:         runtimeWakeTaskScheduler(0);
00702:         return String(name);
00703:     }
00704: 
00705: 
00706:     function runtimeTaskInterval(task) {
00707:         if (!task) return 1000;
00708:         let resolved = task.intervalMs;
00709:         if (typeof task.intervalResolver === 'function') {
00710:             try { resolved = Number(task.intervalResolver(task)) || resolved; } catch (err) {}
00711:         }
00712:         resolved = Math.max(task.intervalMs, resolved);
00713:         if (!state?.economyMode) return resolved;
00714:         let economyResolved = Math.max(resolved, task.economyIntervalMs || resolved);
00715:         if (typeof task.economyIntervalResolver === 'function') {
00716:             try { economyResolved = Number(task.economyIntervalResolver(task)) || economyResolved; } catch (err) {}
00717:         }
00718:         return Math.max(resolved, economyResolved);
00719:     }
00720: 
00721:     function runtimeRescheduleTasks(runSoon = false) {
00722:         const now = Date.now();
00723:         for (const task of runtimeTasks.values()) task.nextRun = runSoon ? now : Math.min(task.nextRun, now + runtimeTaskInterval(task));
00724:         runtimeWakeTaskScheduler(runSoon ? 0 : 50);
00725:     }
00726: 
00727:     function runtimeRunScheduledTasks() {
00728:         runtimeTaskTimer = null;
00729:         if (runtime.destroyed || !runtimeTasks.size) return;
00730:         const now = Date.now();
00731:         const hidden = Boolean(document.hidden);
00732:         let nextDelay = hidden ? 5 * 60 * 1000 : 60000;
00733: 
00734:         for (const task of runtimeTasks.values()) {
00735:             const dueIn = task.nextRun - now;
00736:             if (dueIn > 0) {
00737:                 nextDelay = Math.min(nextDelay, dueIn);
00738:                 continue;
00739:             }
00740:             if (hidden && !task.runWhenHidden) {
00741:                 const deferredInterval = Math.max(60 * 1000, runtimeTaskInterval(task));
00742:                 task.nextRun = now + deferredInterval;
00743:                 nextDelay = Math.min(nextDelay, deferredInterval);
00744:                 continue;
00745:             }
00746: 
00747:             const effectiveInterval = runtimeTaskInterval(task);
00748:             task.nextRun = now + effectiveInterval;
00749:             nextDelay = Math.min(nextDelay, effectiveInterval);
00750:             if (task.running) continue;
00751:             task.running = true;
00752:             try {
00753:                 const result = task.callback();
00754:                 if (result && typeof result.then === 'function') {
00755:                     Promise.resolve(result)
00756:                         .catch(err => console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err))
00757:                         .finally(() => { task.running = false; });
00758:                 } else {
00759:                     task.running = false;
00760:                 }
00761:             } catch (err) {
00762:                 task.running = false;
00763:                 console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err);
00764:             }
00765:         }
00766: 
00767:         runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(50, Math.min(hidden ? 5 * 60 * 1000 : 60000, nextDelay)));
00768:     }
00769: 
00770:     function runtimeOnCleanup(callback) {
00771:         if (typeof callback === 'function') runtime.cleanupCallbacks.push(callback);
00772:         return callback;
00773:     }
00774: 
00775: 
00776:     function runtimeRunWhenIdle(callback, timeout = STARTUP_IDLE_TIMEOUT_MS) {
00777:         if (runtime.destroyed || typeof callback !== 'function') return null;
00778:         const maxWait = Math.max(50, Number(timeout) || STARTUP_IDLE_TIMEOUT_MS);
00779:         let settled = false;
00780:         let idleId = null;
00781:         let fallbackTimer = null;
00782: 
00783:         const run = deadline => {
00784:             if (settled || runtime.destroyed) return;
00785:             settled = true;
00786:             if (fallbackTimer !== null) runtimeClearTimeout(fallbackTimer);
00787:             fallbackTimer = null;
00788:             callback(deadline || { didTimeout: true, timeRemaining: () => 0 });
00789:         };
00790: 
00791:         if (typeof pageWindow.requestIdleCallback === 'function') {
00792:             try {
00793:                 idleId = pageWindow.requestIdleCallback(run, { timeout: maxWait });
00794:                 fallbackTimer = runtimeSetTimeout(() => run(null), maxWait + 120);
00795:                 runtimeOnCleanup(() => {
00796:                     if (settled || idleId === null || typeof pageWindow.cancelIdleCallback !== 'function') return;
00797:                     try { pageWindow.cancelIdleCallback(idleId); } catch (err) {}
00798:                 });
00799:                 return idleId;
00800:             } catch (err) {}
00801:         }
00802: 
00803:         fallbackTimer = runtimeSetTimeout(() => run(null), Math.min(350, maxWait));
00804:         return fallbackTimer;
00805:     }
00806: 
00807:     function startupClock() {
00808:         try { return Number(pageWindow.performance?.now?.()) || Date.now(); }
00809:         catch (err) { return Date.now(); }
00810:     }
00811: 
00812:     function recordStartupMetric(name, startedAt, extra = {}) {
00813:         const finishedAt = startupClock();
00814:         const elapsedMs = Math.max(0, finishedAt - Number(startedAt || finishedAt));
00815:         const metrics = pageWindow.__MCMS_STARTUP_METRICS__ || {};
00816:         metrics.version = SCRIPT.version;
00817:         metrics[name] = Math.round(elapsedMs * 10) / 10;
00818:         Object.assign(metrics, extra);
00819:         pageWindow.__MCMS_STARTUP_METRICS__ = metrics;
00820:         return elapsedMs;
00821:     }
00822: 
00823:     function runtimeFetch(input, init = {}) {
00824:         if (runtime.destroyed) return Promise.reject(new Error('Toolkit runtime stopped.'));
00825:         const Controller = pageWindow.AbortController || globalThis.AbortController;
00826:         const controller = typeof Controller === 'function' ? new Controller() : null;
00827:         if (controller) runtime.fetchControllers.add(controller);
00828:         const fetchFunction = pageWindow.fetch || globalThis.fetch;
00829:         if (typeof fetchFunction !== 'function') {
00830:             if (controller) runtime.fetchControllers.delete(controller);
00831:             return Promise.reject(new Error('Browser fetch is unavailable.'));
00832:         }
00833:         const options = controller ? { ...init, signal: controller.signal } : init;
00834:         return Promise.resolve(fetchFunction.call(pageWindow, input, options))
00835:             .finally(() => { if (controller) runtime.fetchControllers.delete(controller); });
00836:     }
00837: 
00838:     runtimeOnCleanup(() => {
00839:         runtimeTasks.clear();
00840:         runtimeClearTimeout(runtimeTaskTimer);
00841:         runtimeTaskTimer = null;
00842:     });
00843: 
00844:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4100__ = true;
00845:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V3130__ = true;
00846:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V3121__ = true;
00847:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V380__ = true;
00848:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V341__ = true;
00849:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V340__ = true;
00850:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V318__ = true;
```

## `createCleanExit()` — line 27950

```javascript
function createCleanExit() {
        if (document.getElementById(SCRIPT.cleanExitId)) return;
        const button = document.createElement('button');
        button.id = SCRIPT.cleanExitId;
        button.type = 'button';
        button.textContent = 'Exit Clean Mode';
        button.title = 'Exit clean mode. Shortcut: C or Esc.';
        button.addEventListener('click', () => toggleFeature('clean'));
        document.body.appendChild(button);
    }
```

## `runtimeOnCleanup()` — line 770

```javascript
function runtimeOnCleanup(callback) {
        if (typeof callback === 'function') runtime.cleanupCallbacks.push(callback);
        return callback;
    }
```

## `runtimeListen()` — line 653

```javascript
function runtimeListen(target, type, listener, options) {
        if (!target?.addEventListener || runtime.destroyed) return listener;
        target.addEventListener(type, listener, options);
        runtime.listeners.push({ target, type, listener, options });
        return listener;
    }
```

## `runtimeSetTimeout()` — line 586

```javascript
function runtimeSetTimeout(callback, delay = 0, ...args) {
        if (runtime.destroyed) return null;
        let id = null;
        id = pageWindow.setTimeout((...callbackArgs) => {
            runtime.timeouts.delete(id);
            if (!runtime.destroyed) callback(...callbackArgs);
        }, delay, ...args);
        runtime.timeouts.add(id);
        return id;
    }
```

## `runtimeTrackObserver()` — line 660

```javascript
function runtimeTrackObserver(observer) {
        if (!observer) return observer;
        if (runtime.destroyed) {
            try { observer.disconnect(); } catch (err) {}
            return observer;
        }
        runtime.observers.add(observer);
        return observer;
    }
```

## `runtimeRegisterTask()` — line 686

```javascript
function runtimeRegisterTask(name, intervalMs, callback, options = {}
```

## `runtimeWakeTaskScheduler()` — line 681

```javascript
function runtimeWakeTaskScheduler(delay = 0) {
        runtimeClearTimeout(runtimeTaskTimer);
        runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(0, Number(delay) || 0));
    }
```

## `runtimeRunWhenIdle()` — line 776

```javascript
function runtimeRunWhenIdle(callback, timeout = STARTUP_IDLE_TIMEOUT_MS) {
        if (runtime.destroyed || typeof callback !== 'function') return null;
        const maxWait = Math.max(50, Number(timeout) || STARTUP_IDLE_TIMEOUT_MS);
        let settled = false;
        let idleId = null;
        let fallbackTimer = null;

        const run = deadline => {
            if (settled || runtime.destroyed) return;
            settled = true;
            if (fallbackTimer !== null) runtimeClearTimeout(fallbackTimer);
            fallbackTimer = null;
            callback(deadline || { didTimeout: true, timeRemaining: () => 0 });
        };

        if (typeof pageWindow.requestIdleCallback === 'function') {
            try {
                idleId = pageWindow.requestIdleCallback(run, { timeout: maxWait });
                fallbackTimer = runtimeSetTimeout(() => run(null), maxWait + 120);
                runtimeOnCleanup(() => {
                    if (settled || idleId === null || typeof pageWindow.cancelIdleCallback !== 'function') return;
                    try { pageWindow.cancelIdleCallback(idleId); } catch (err) {}
                });
                return idleId;
            } catch (err) {}
        }

        fallbackTimer = runtimeSetTimeout(() => run(null), Math.min(350, maxWait));
        return fallbackTimer;
    }
```

## `scheduleDeferredOperationalStartup()` — line 29336

```javascript
function scheduleDeferredOperationalStartup(delay = STARTUP_OPERATIONAL_DELAY_MS) {
        if (operationalStartupStarted || runtime.destroyed) return;
        runtimeSetTimeout(() => runtimeRunWhenIdle(() => {
            runDeferredOperationalStartup().catch(err => {
                operationalStartupComplete = true;
                startupDataPassActive = false;
                console.debug(`[${SCRIPT.name}] Deferred startup recovered after an operational initialisation error.`, err);
                connectMainMutationObserver();
            });
        }, STARTUP_IDLE_TIMEOUT_MS), Math.max(0, Number(delay) || 0));
    }
```

## `boot()` — line 29605

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

## `scheduleBoot()` — line 29941

```javascript
function scheduleBoot() {
        if (runtime.destroyed || bootStarted) return;
        runtimeRunWhenIdle(boot, STARTUP_IDLE_TIMEOUT_MS);
    }
```

## Final bootstrap tail

```javascript
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

    function scheduleBoot() {
        if (runtime.destroyed || bootStarted) return;
        runtimeRunWhenIdle(boot, STARTUP_IDLE_TIMEOUT_MS);
    }

    if (document.readyState === 'loading') {
        runtimeListen(document, 'DOMContentLoaded', scheduleBoot, { once: true });
    } else {
        scheduleBoot();
    }
})();
```
