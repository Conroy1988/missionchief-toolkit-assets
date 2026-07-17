# Issue #133 — Selected canonical source ranges

Generated mechanically to support a small, anchored source transformation.

## Runtime ownership, observers and cleanup

Canonical lines 560–820

```javascript
00560:             for (const id of this.animationFrames) { try { pageWindow.cancelAnimationFrame(id); } catch (err) {} }
00561:             this.timeouts.clear();
00562:             this.intervals.clear();
00563:             this.animationFrames.clear();
00564:             for (const settle of Array.from(this.waiters)) { try { settle(false); } catch (err) {} }
00565:             this.waiters.clear();
00566:             for (const request of Array.from(this.requests)) { try { request.abort?.(); } catch (err) {} }
00567:             this.requests.clear();
00568:             for (const controller of Array.from(this.fetchControllers)) { try { controller.abort(); } catch (err) {} }
00569:             this.fetchControllers.clear();
00570:             for (const observer of this.observers) { try { observer.disconnect(); } catch (err) {} }
00571:             this.observers.clear();
00572:             for (const { target, type, listener, options } of this.listeners.splice(0)) {
00573:                 try { target.removeEventListener(type, listener, options); } catch (err) {}
00574:             }
00575:             for (const binding of this.mapBindings.splice(0)) {
00576:                 try { binding.map.off(binding.types, binding.handler); } catch (err) {}
00577:             }
00578:             for (const restore of this.hookRestorers.splice(0).reverse()) { try { restore(); } catch (err) {} }
00579:             for (const cleanup of this.cleanupCallbacks.splice(0).reverse()) { try { cleanup(reason); } catch (err) {} }
00580:             if (pageWindow[RUNTIME_KEY] === this) {
00581:                 try { delete pageWindow[RUNTIME_KEY]; } catch (err) { pageWindow[RUNTIME_KEY] = null; }
00582:             }
00583:         }
00584:     };
00585:     pageWindow[RUNTIME_KEY] = runtime;
00586: 
00587:     function runtimeSetTimeout(callback, delay = 0, ...args) {
00588:         if (runtime.destroyed) return null;
00589:         let id = null;
00590:         id = pageWindow.setTimeout((...callbackArgs) => {
00591:             runtime.timeouts.delete(id);
00592:             if (!runtime.destroyed) callback(...callbackArgs);
00593:         }, delay, ...args);
00594:         runtime.timeouts.add(id);
00595:         return id;
00596:     }
00597: 
00598:     function runtimeClearTimeout(id) {
00599:         if (id === null || id === undefined) return;
00600:         runtime.timeouts.delete(id);
00601:         try { pageWindow.clearTimeout(id); } catch (err) {}
00602:     }
00603: 
00604:     function runtimeDelay(delay = 0) {
00605:         if (runtime.destroyed) return Promise.resolve(false);
00606:         return new Promise(resolve => {
00607:             let timerId = null;
00608:             let settled = false;
00609:             const settle = completed => {
00610:                 if (settled) return;
00611:                 settled = true;
00612:                 runtime.waiters.delete(settle);
00613:                 if (timerId !== null) runtimeClearTimeout(timerId);
00614:                 resolve(Boolean(completed));
00615:             };
00616:             runtime.waiters.add(settle);
00617:             timerId = runtimeSetTimeout(() => settle(true), Math.max(0, Number(delay) || 0));
00618:             if (timerId === null) settle(false);
00619:         });
00620:     }
00621: 
00622:     function runtimeSetInterval(callback, delay = 0, ...args) {
00623:         if (runtime.destroyed) return null;
00624:         const id = pageWindow.setInterval((...callbackArgs) => {
00625:             if (!runtime.destroyed) callback(...callbackArgs);
00626:         }, delay, ...args);
00627:         runtime.intervals.add(id);
00628:         return id;
00629:     }
00630: 
00631:     function runtimeClearInterval(id) {
00632:         if (id === null || id === undefined) return;
00633:         runtime.intervals.delete(id);
00634:         try { pageWindow.clearInterval(id); } catch (err) {}
00635:     }
00636: 
00637:     function runtimeRequestAnimationFrame(callback) {
00638:         if (runtime.destroyed) return null;
00639:         let id = null;
00640:         id = pageWindow.requestAnimationFrame(timestamp => {
00641:             runtime.animationFrames.delete(id);
00642:             if (!runtime.destroyed) callback(timestamp);
00643:         });
00644:         runtime.animationFrames.add(id);
00645:         return id;
00646:     }
00647: 
00648:     function runtimeCancelAnimationFrame(id) {
00649:         if (id === null || id === undefined) return;
00650:         runtime.animationFrames.delete(id);
00651:         try { pageWindow.cancelAnimationFrame(id); } catch (err) {}
00652:     }
00653: 
00654:     function runtimeListen(target, type, listener, options) {
00655:         if (!target?.addEventListener || runtime.destroyed) return listener;
00656:         target.addEventListener(type, listener, options);
00657:         runtime.listeners.push({ target, type, listener, options });
00658:         return listener;
00659:     }
00660: 
00661:     function runtimeTrackObserver(observer) {
00662:         if (!observer) return observer;
00663:         if (runtime.destroyed) {
00664:             try { observer.disconnect(); } catch (err) {}
00665:             return observer;
00666:         }
00667:         runtime.observers.add(observer);
00668:         return observer;
00669:     }
00670: 
00671:     function runtimeUntrackObserver(observer, disconnect = true) {
00672:         if (!observer) return;
00673:         if (disconnect) {
00674:             try { observer.disconnect(); } catch (err) {}
00675:         }
00676:         runtime.observers.delete(observer);
00677:     }
00678: 
00679:     const runtimeTasks = new Map();
00680:     let runtimeTaskTimer = null;
00681: 
00682:     function runtimeWakeTaskScheduler(delay = 0) {
00683:         runtimeClearTimeout(runtimeTaskTimer);
00684:         runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(0, Number(delay) || 0));
00685:     }
00686: 
00687:     function runtimeRegisterTask(name, intervalMs, callback, options = {}) {
00688:         if (!name || typeof callback !== 'function') return null;
00689:         const interval = Math.max(250, Number(intervalMs) || 1000);
00690:         const initialDelay = Math.max(0, Number(options.initialDelayMs ?? interval) || 0);
00691:         runtimeTasks.set(String(name), {
00692:             name: String(name),
00693:             intervalMs: interval,
00694:             intervalResolver: typeof options.intervalResolver === 'function' ? options.intervalResolver : null,
00695:             economyIntervalMs: Math.max(interval, Number(options.economyIntervalMs) || interval),
00696:             economyIntervalResolver: typeof options.economyIntervalResolver === 'function' ? options.economyIntervalResolver : null,
00697:             callback,
00698:             runWhenHidden: Boolean(options.runWhenHidden),
00699:             nextRun: Date.now() + initialDelay,
00700:             running: false
00701:         });
00702:         runtimeWakeTaskScheduler(0);
00703:         return String(name);
00704:     }
00705: 
00706: 
00707:     function runtimeTaskInterval(task) {
00708:         if (!task) return 1000;
00709:         let resolved = task.intervalMs;
00710:         if (typeof task.intervalResolver === 'function') {
00711:             try { resolved = Number(task.intervalResolver(task)) || resolved; } catch (err) {}
00712:         }
00713:         resolved = Math.max(task.intervalMs, resolved);
00714:         if (!state?.economyMode) return resolved;
00715:         let economyResolved = Math.max(resolved, task.economyIntervalMs || resolved);
00716:         if (typeof task.economyIntervalResolver === 'function') {
00717:             try { economyResolved = Number(task.economyIntervalResolver(task)) || economyResolved; } catch (err) {}
00718:         }
00719:         return Math.max(resolved, economyResolved);
00720:     }
00721: 
00722:     function runtimeRescheduleTasks(runSoon = false) {
00723:         const now = Date.now();
00724:         for (const task of runtimeTasks.values()) task.nextRun = runSoon ? now : Math.min(task.nextRun, now + runtimeTaskInterval(task));
00725:         runtimeWakeTaskScheduler(runSoon ? 0 : 50);
00726:     }
00727: 
00728:     function runtimeRunScheduledTasks() {
00729:         runtimeTaskTimer = null;
00730:         if (runtime.destroyed || !runtimeTasks.size) return;
00731:         const now = Date.now();
00732:         const hidden = Boolean(document.hidden);
00733:         let nextDelay = hidden ? 5 * 60 * 1000 : 60000;
00734: 
00735:         for (const task of runtimeTasks.values()) {
00736:             const dueIn = task.nextRun - now;
00737:             if (dueIn > 0) {
00738:                 nextDelay = Math.min(nextDelay, dueIn);
00739:                 continue;
00740:             }
00741:             if (hidden && !task.runWhenHidden) {
00742:                 const deferredInterval = Math.max(60 * 1000, runtimeTaskInterval(task));
00743:                 task.nextRun = now + deferredInterval;
00744:                 nextDelay = Math.min(nextDelay, deferredInterval);
00745:                 continue;
00746:             }
00747: 
00748:             const effectiveInterval = runtimeTaskInterval(task);
00749:             task.nextRun = now + effectiveInterval;
00750:             nextDelay = Math.min(nextDelay, effectiveInterval);
00751:             if (task.running) continue;
00752:             task.running = true;
00753:             try {
00754:                 const result = task.callback();
00755:                 if (result && typeof result.then === 'function') {
00756:                     Promise.resolve(result)
00757:                         .catch(err => console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err))
00758:                         .finally(() => { task.running = false; });
00759:                 } else {
00760:                     task.running = false;
00761:                 }
00762:             } catch (err) {
00763:                 task.running = false;
00764:                 console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err);
00765:             }
00766:         }
00767: 
00768:         runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(50, Math.min(hidden ? 5 * 60 * 1000 : 60000, nextDelay)));
00769:     }
00770: 
00771:     function runtimeOnCleanup(callback) {
00772:         if (typeof callback === 'function') runtime.cleanupCallbacks.push(callback);
00773:         return callback;
00774:     }
00775: 
00776: 
00777:     function runtimeRunWhenIdle(callback, timeout = STARTUP_IDLE_TIMEOUT_MS) {
00778:         if (runtime.destroyed || typeof callback !== 'function') return null;
00779:         const maxWait = Math.max(50, Number(timeout) || STARTUP_IDLE_TIMEOUT_MS);
00780:         let settled = false;
00781:         let idleId = null;
00782:         let fallbackTimer = null;
00783: 
00784:         const run = deadline => {
00785:             if (settled || runtime.destroyed) return;
00786:             settled = true;
00787:             if (fallbackTimer !== null) runtimeClearTimeout(fallbackTimer);
00788:             fallbackTimer = null;
00789:             callback(deadline || { didTimeout: true, timeRemaining: () => 0 });
00790:         };
00791: 
00792:         if (typeof pageWindow.requestIdleCallback === 'function') {
00793:             try {
00794:                 idleId = pageWindow.requestIdleCallback(run, { timeout: maxWait });
00795:                 fallbackTimer = runtimeSetTimeout(() => run(null), maxWait + 120);
00796:                 runtimeOnCleanup(() => {
00797:                     if (settled || idleId === null || typeof pageWindow.cancelIdleCallback !== 'function') return;
00798:                     try { pageWindow.cancelIdleCallback(idleId); } catch (err) {}
00799:                 });
00800:                 return idleId;
00801:             } catch (err) {}
00802:         }
00803: 
00804:         fallbackTimer = runtimeSetTimeout(() => run(null), Math.min(350, maxWait));
00805:         return fallbackTimer;
00806:     }
00807: 
00808:     function startupClock() {
00809:         try { return Number(pageWindow.performance?.now?.()) || Date.now(); }
00810:         catch (err) { return Date.now(); }
00811:     }
00812: 
00813:     function recordStartupMetric(name, startedAt, extra = {}) {
00814:         const finishedAt = startupClock();
00815:         const elapsedMs = Math.max(0, finishedAt - Number(startedAt || finishedAt));
00816:         const metrics = pageWindow.__MCMS_STARTUP_METRICS__ || {};
00817:         metrics.version = SCRIPT.version;
00818:         metrics[name] = Math.round(elapsedMs * 10) / 10;
00819:         Object.assign(metrics, extra);
00820:         pageWindow.__MCMS_STARTUP_METRICS__ = metrics;
```

## Global state and feature lifecycle variables

Canonical lines 1180–1540

```javascript
01180:     let missionRegistryRevision = 0;
01181:     let vehicleRegistryRevision = 0;
01182:     let buildingRegistryRevision = 0;
01183:     let vehicleDataRevision = 0;
01184:     let missionMarkerIndexCache = { revision: -1, registry: null, markers: [], byId: new Map() };
01185:     let personalVehicleRecordsCache = { vehicleRevision: -1, markerRevision: -1, apiReady: false, createdAt: 0, records: [] };
01186:     let cachedUserId = null;
01187:     let cachedUserIdReadAt = 0;
01188:     let personalBuildingIdsCache = { revision: -1, userId: null, createdAt: 0, values: new Set() };
01189:     let missionIconMarkerCache = new WeakMap();
01190:     let panelPositionTimer = null;
01191:     let coverageRenderSignature = '';
01192:     let heatmapRenderSignature = '';
01193:     let heatmapSourceCache = { key: '', createdAt: 0, points: [] };
01194:     let majorIncidentFeedRenderSignature = '';
01195:     let majorIncidentFeedRenderTimer = null;
01196:     let majorIncidentFeedLayoutFrame = null;
01197:     let majorIncidentFeedLayoutTimer = null;
01198:     let majorIncidentFeedMotionTimer = null;
01199:     let majorIncidentFeedMotionRevision = 0;
01200:     let majorIncidentFeedResizeObserver = null;
01201:     let majorIncidentFeedObservedElement = null;
01202:     let missionInspectorLastPosition = '';
01203:     let missionInspectorTooltipCache = { marker: null, createdAt: 0, rect: null };
01204:     const missionLifecycleLastSeen = new Map();
01205:     let coverageGroup = null;
01206:     let mutationTimer = null;
01207:     let classifyTimer = null;
01208:     let markerStateSyncTimer = null;
01209:     let markerStateTrailingTimer = null;
01210:     let coverageTimer = null;
01211:     let fitTimer = null;
01212:     let dragState = null;
01213:     let suppressNextOutsideClick = false;
01214:     const hiddenPersonalBuildingLayers = new Set();
01215:     const personalBuildingLayerOpacity = new Map();
01216:     let enforcingPersonalBuildingVisibility = false;
01217:     const economyHiddenVehicleLayers = new Set();
01218:     const economyHiddenBuildingLayers = new Set();
01219:     const economyLeafletOptionSnapshots = new Map();
01220:     let economyLayerSyncTimer = null;
01221:     let economyLayerEnforcement = false;
01222:     let economyMapMoving = false;
01223:     let economyDeferredMapRefresh = false;
01224:     let economyDeferredDomMutation = false;
01225:     let economyCanvasRenderer = null;
01226:     let heatmapGroup = null;
01227:     let heatmapTimer = null;
01228:     let allianceCreditGroup = null;
01229:     let allianceCreditTimer = null;
01230:     let missionAgeGroup = null;
01231:     let missionAgeTimer = null;
01232:     let unitCommitmentGroup = null;
01233:     let unitCommitmentTimer = null;
01234:     let transportWatcherGroup = null;
01235:     let transportWatcherTimer = null;
01236:     let resourceGapGroup = null;
01237:     let resourceGapTimer = null;
01238:     let missionSnapshotTimer = null;
01239:     let bootStarted = false;
01240:     let bootStartedAt = 0;
01241:     let operationalStartupStarted = false;
01242:     let operationalStartupComplete = false;
01243:     let startupDataPassActive = false;
01244:     let mainMutationObserver = null;
01245:     let mainMutationObserverFallbackActive = false;
01246:     let settingsPanelActivated = false;
01247:     let opsRefreshTimer = null;
01248:     let payoutFlashTimer = null;
01249:     let toastFlashTimer = null;
01250:     let payoutFlashFallbackInterval = null;
01251:     let payoutFlashAnimations = [];
01252:     let payoutAmountAnimationFrame = null;
01253:     let payoutAudioContext = null;
01254:     let payoutMediaAudio = null;
01255:     let payoutMediaTemplate = '';
01256:     let payoutMediaGeneration = 0;
01257:     let payoutEventCounter = 0;
01258:     let creditsValueObserver = null;
01259:     let observedCreditsElement = null;
01260:     let lastObservedCredits = null;
01261:     let inlineMissionDataScanned = false;
01262:     let missionProgressPageFetchPromise = null;
01263:     let missionProgressPageLastFetch = 0;
01264:     let missionProgressPageLastSuccessAt = 0;
01265:     let missionSnapshotReady = false;
01266:     let criticalViewActive = false;
01267:     let criticalViewLoading = false;
01268:     let criticalDrawerRefreshing = false;
01269:     let criticalDrawerLastDataSyncAt = 0;
01270:     let criticalDrawerLastViewUpdatedAt = 0;
01271:     let criticalDrawerDockTimer = null;
01272:     let criticalDrawerRenderLimit = CRITICAL_RENDER_BATCH_SIZE;
01273:     let criticalDrawerVirtualScrollTimer = null;
01274:     const criticalMissionStableCache = new Map();
01275:     let criticalViewSnapshot = null;
01276:     let vehicleApiFetchPromise = null;
01277:     let vehicleApiLastFetch = 0;
01278:     let vehicleApiReady = false;
01279:     let vehicleApiLastError = 0;
01280:     let vehicleStatusLastUpdate = 0;
01281:     let missionCommitmentIndexDirty = true;
01282:     let operationalPanelsLastRender = 0;
01283:     let missionInspectorMarker = null;
01284:     let missionInspectorPointer = null;
01285:     let missionLockOnMarker = null;
01286:     let missionLockOnTravelOverlay = null;
01287:     let missionLockOnTargetIcon = null;
01288:     let missionLockOnTimer = null;
01289:     let missionLockOnMoveEndMap = null;
01290:     let missionLockOnMoveEndHandler = null;
01291:     let missionLockOnToken = 0;
01292:     let missionInspectorRefreshTimer = null;
01293:     let missionInspectorMoveFrame = null;
01294:     let missionProgressSaveTimer = null;
01295:     let stuckMissionGroup = null;
01296:     let stuckMissionTimer = null;
01297:     let missionSpawnArmed = false;
01298:     let missionSpawnPrimeTimer = null;
01299:     const missionOverlayData = new Map();
01300:     const missionOverlayVersions = new Map();
01301:     const missionSnapshotCache = new Map();
01302:     const missionPanelCache = new Map();
01303:     let liveMissionSnapshots = new Map();
01304:     const recentCompletedMissions = [];
01305:     const missionProgressState = loadMissionProgressState();
01306:     const knownMissionIds = new Set();
01307:     const stuckMissionLabels = new Map();
01308:     const MISSION_OVERLAY_PANE = 'mcmsMissionFloatPane';
01309:     const allianceCreditLabels = new Map();
01310:     const missionAgeLabels = new Map();
01311:     const unitCommitmentLabels = new Map();
01312:     const transportWatcherLabels = new Map();
01313:     const resourceGapLabels = new Map();
01314:     const resourceGapAnalysisCache = new Map();
01315:     let resourceGapVehicleContextCache = { key: '', createdAt: 0, available: [] };
01316:     const transportSweepRuntime = {
01317:         running: false,
01318:         stopRequested: false,
01319:         queue: [],
01320:         scannedAt: 0,
01321:         currentMissionId: null,
01322:         currentVehicleHref: '',
01323:         cleared: 0,
01324:         skipped: 0,
01325:         errors: 0,
01326:         processed: 0,
01327:         rejectedOwn: 0,
01328:         missionAnchorBaseline: new Set(),
01329:         vehicleButtonBaseline: new Set(),
01330:         ownVehicleIds: new Set(),
01331:         missionWindowRoot: null,
01332:         activeWindowRoot: null,
01333:         ownedWindowLayers: new Set(),
01334:         activeWindowCreatedLayer: false,
01335:         lastCandidateStats: null,
01336:         startedAt: 0,
01337:         missionIndex: 0,
01338:         missionTotal: 0,
01339:         currentItem: '',
01340:         statusMessage: '',
01341:         statusLevel: 'info',
01342:         hudFinal: false,
01343:         hudDismissTimer: null,
01344:         log: []
01345:     };
01346:     const personalVehicleApiCache = new Map();
01347:     const missionCommitmentIndex = new Map();
01348:     const payoutHistory = loadPayoutHistory();
01349:     const sessionPerformance = loadSessionPerformance();
01350:     let discordFinanceBusy = false;
01351:     let discordFinanceStatus = 'Select a reporting period, then generate and post the financial intelligence report.';
01352:     let discordFinanceStatusTone = 'neutral';
01353:     let financeVaultStatus = 'Local Financial Archive ready.';
01354:     let financeVaultStatusTone = 'neutral';
01355:     let financeRuleFeedStatus = 'Built-in financial intelligence active.';
01356:     let financeRuleFeedStatusTone = 'neutral';
01357:     let financeArchiveScanBusy = false;
01358:     let financeArchiveScanCancelled = false;
01359:     let financeRuleRefreshPromise = null;
01360:     let financePolicyRefreshPromise = null;
01361:     let tabletModeActive = false;
01362:     let mobileModeActive = false;
01363:     let activeDeviceLayout = 'desktop';
01364:     let tabletLayoutTimer = null;
01365:     let tabletDockResizeObserver = null;
01366:     let tabletDockObservedMap = null;
01367:     let desktopPanelResizeObserver = null;
01368:     let desktopPanelObservedElements = new Set();
01369:     let missionValueScanTimer = null;
01370:     let missionValueFeatureInstalled = false;
01371:     const missionValueObservedDocuments = new WeakSet();
01372:     const missionValueObservedFrames = new WeakSet();
01373:     const missionValueHostObservers = new Map();
01374:     const missionValueRetryState = new WeakMap();
01375:     let commandBarAnimationTimer = null;
01376:     let commandBarAnimating = false;
01377:     let helpGuideDocumentCache = '';
01378:     let helpGuideLoadedAt = 0;
01379:     let helpGuideLoadPromise = null;
01380:     let helpCenterReturnFocus = null;
01381: 
01382:     function defaultState() {
01383:         return {
01384:             uiTheme: 'mapCommand',
01385:             theme: getLegacyTheme(),
01386:             position: getLegacyPosition(),
01387:             activeTab: 'skins',
01388:             cleanMode: false,
01389:             markerFocus: false,
01390:             missionPulse: false,
01391:             roadPriority: false,
01392:             compactDock: false,
01393:             commandBarOpen: true,
01394:             economyMode: false,
01395:             tabletMode: 'auto',
01396:             mobileMode: 'auto',
01397:             shortcuts: true,
01398:             autoLoadAllVehicles: false,
01399:             allianceBuildingsMap: true,
01400:             majorIncidentFeed: { enabled: true, minimumCredits: 25000 },
01401:             missionAgeWatch: {
01402:                 ageFilter: '8h',
01403:                 sortMode: 'age',
01404:                 expanded: false,
01405:                 ownershipFilter: 'personal',
01406:                 categoryFilter: 'all',
01407:                 primaryStatus: 'all',
01408:                 advancedFiltersOpen: false,
01409:                 hasVehiclesOnWay: false,
01410:                 onlyMyUnits: false,
01411:                 valueMode: 'total',
01412:                 distanceOrigin: 'live',
01413:                 lockedOrigin: null
01414:             },
01415:             missionLockAudio: true,
01416:             missionValue: true,
01417:             allianceCredits: false,
01418:             allianceCreditMinimum: 0,
01419:             missionAge: false,
01420:             unitCommitment: false,
01421:             transportWatcher: true,
01422:             missionInspector: true,
01423:             stuckDetector: { enabled: true, thresholdMin: 20 },
01424:             missionSpawn: { enabled: true },
01425:             resourceGap: { enabled: false, radiusMi: 25 },
01426:             transportSweep: { delayMs: 2000, maxPerRun: 25 },
01427:             payoutFlash: { enabled: true, threshold: 10000, durationMs: 4000, template: 'gta5', soundEnabled: false, soundVolume: 0.35 },
01428:             discordReport: { webhookName: 'MissionChief Finance', topCategories: 5, period: 'today', customStart: localIsoDate(new Date(Date.now() - 6 * 86400000)), customEnd: localIsoDate(), includeChart: true, includeComparison: true, reportMode: 'fullAudit', includeForecast: true, includeRisk: true },
01429:             financialVault: { enabled: true, ruleFeedEnabled: true, retentionDays: 'all' },
01430:             profiles: Array.from({ length: MAP_PROFILE_LIMIT }, () => null),
01431:             nudge: { x: 0, y: 0 },
01432:             panelPosition: null,
01433:             visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true },
01434:             quickPins: Object.fromEntries(QUICK_PLACES.map(place => [place.id, false])),
01435:             coverage: { enabled: false, radiusMi: 10 },
01436:             heatmap: { enabled: false, source: 'stations', service: 'all', radiusMi: 10, opacity: 0.30 },
01437:             autoNight: {
01438:                 enabled: false,
01439:                 nightStart: '19:00',
01440:                 dayStart: '07:00',
01441:                 nightTheme: 'nightshift',
01442:                 dayTheme: 'default',
01443:                 lastBucket: ''
01444:             },
01445:             bookmarks: [null, null, null, null, null]
01446:         };
01447:     }
01448: 
01449:     function normaliseLoadedState(parsed, base = defaultState()) {
01450:         const merged = {
01451:             ...base,
01452:             ...parsed,
01453:             nudge: { ...base.nudge, ...(parsed.nudge || {}) },
01454:             visibility: { ...base.visibility, ...(parsed.visibility || {}) },
01455:             quickPins: { ...base.quickPins, ...(parsed.quickPins || {}) },
01456:             coverage: { ...base.coverage, ...(parsed.coverage || {}) },
01457:             heatmap: { ...base.heatmap, ...(parsed.heatmap || {}) },
01458:             stuckDetector: { ...base.stuckDetector, ...(parsed.stuckDetector || {}) },
01459:             missionSpawn: { ...base.missionSpawn, ...(parsed.missionSpawn || {}) },
01460:             resourceGap: { ...base.resourceGap, ...(parsed.resourceGap || {}) },
01461:             transportSweep: { ...base.transportSweep, ...(parsed.transportSweep || {}) },
01462:             majorIncidentFeed: { ...base.majorIncidentFeed, ...(parsed.majorIncidentFeed || {}) },
01463:             missionAgeWatch: { ...base.missionAgeWatch, ...(parsed.missionAgeWatch || {}) },
01464:             payoutFlash: { ...base.payoutFlash, ...(parsed.payoutFlash || {}) },
01465:             discordReport: { ...base.discordReport, ...(parsed.discordReport || {}) },
01466:             financialVault: { ...base.financialVault, ...(parsed.financialVault || {}) },
01467:             autoNight: { ...base.autoNight, ...(parsed.autoNight || {}) },
01468:             profiles: Array.isArray(parsed.profiles) ? parsed.profiles.slice(0, MAP_PROFILE_LIMIT) : base.profiles,
01469:             bookmarks: Array.isArray(parsed.bookmarks) ? parsed.bookmarks.slice(0, 5) : base.bookmarks
01470:         };
01471: 
01472:         while (merged.bookmarks.length < 5) merged.bookmarks.push(null);
01473:         while (merged.profiles.length < MAP_PROFILE_LIMIT) merged.profiles.push(null);
01474: 
01475:         merged.uiTheme = normaliseUiTheme(merged.uiTheme);
01476:         merged.theme = normaliseTheme(merged.theme);
01477:         merged.position = POSITIONS[merged.position] ? merged.position : 'bl';
01478:         if (merged.activeTab === 'fleet') merged.activeTab = 'resources';
01479:         merged.activeTab = ['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings'].includes(merged.activeTab) ? merged.activeTab : 'skins';
01480:         delete merged.fleetFilter;
01481:         merged.nudge.x = clamp(merged.nudge.x, -220, 220, 0);
01482:         merged.nudge.y = clamp(merged.nudge.y, -220, 220, 0);
01483:         merged.coverage.radiusMi = Number(merged.coverage.radiusMi) || 10;
01484:         merged.heatmap.radiusMi = Number(merged.heatmap.radiusMi) || 10;
01485:         merged.heatmap.opacity = clamp(merged.heatmap.opacity, 0.12, 0.55, 0.30);
01486:         merged.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(merged.allianceCreditMinimum)) ? Number(merged.allianceCreditMinimum) : 0;
01487:         merged.commandBarOpen = merged.commandBarOpen !== false;
01488:         merged.economyMode = Boolean(merged.economyMode);
01489:         merged.autoLoadAllVehicles = merged.autoLoadAllVehicles === true;
01490:         merged.allianceBuildingsMap = merged.allianceBuildingsMap !== false;
01491:         merged.majorIncidentFeed.enabled = merged.majorIncidentFeed.enabled !== false;
01492:         merged.majorIncidentFeed.minimumCredits = MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS.includes(Number(merged.majorIncidentFeed.minimumCredits)) ? Number(merged.majorIncidentFeed.minimumCredits) : 25000;
01493:         merged.missionAgeWatch.ageFilter = CRITICAL_AGE_FILTER_KEYS.includes(String(merged.missionAgeWatch.ageFilter)) ? String(merged.missionAgeWatch.ageFilter) : '8h';
01494:         merged.missionAgeWatch.sortMode = CRITICAL_SORT_KEYS.includes(String(merged.missionAgeWatch.sortMode)) ? String(merged.missionAgeWatch.sortMode) : 'age';
01495:         merged.missionAgeWatch.expanded = Boolean(merged.missionAgeWatch.expanded);
01496:         merged.missionAgeWatch.ownershipFilter = CRITICAL_OWNERSHIP_FILTER_KEYS.includes(String(merged.missionAgeWatch.ownershipFilter)) ? String(merged.missionAgeWatch.ownershipFilter) : 'personal';
01497:         merged.missionAgeWatch.categoryFilter = CRITICAL_CATEGORY_FILTER_KEYS.includes(String(merged.missionAgeWatch.categoryFilter)) ? String(merged.missionAgeWatch.categoryFilter) : 'all';
01498:         merged.missionAgeWatch.primaryStatus = CRITICAL_PRIMARY_STATUS_KEYS.includes(String(merged.missionAgeWatch.primaryStatus)) ? String(merged.missionAgeWatch.primaryStatus) : 'all';
01499:         merged.missionAgeWatch.hasVehiclesOnWay = Boolean(merged.missionAgeWatch.hasVehiclesOnWay);
01500:         merged.missionAgeWatch.onlyMyUnits = Boolean(merged.missionAgeWatch.onlyMyUnits);
01501:         merged.missionAgeWatch.valueMode = CRITICAL_VALUE_MODE_KEYS.includes(String(merged.missionAgeWatch.valueMode)) ? String(merged.missionAgeWatch.valueMode) : 'total';
01502:         merged.missionAgeWatch.distanceOrigin = /^(?:live|locked|quick:[a-z0-9_-]+|bookmark:\d+)$/iu.test(String(merged.missionAgeWatch.distanceOrigin || '')) ? String(merged.missionAgeWatch.distanceOrigin) : 'live';
01503:         const lockedOrigin = merged.missionAgeWatch.lockedOrigin;
01504:         merged.missionAgeWatch.lockedOrigin = lockedOrigin && Number.isFinite(Number(lockedOrigin.lat)) && Number.isFinite(Number(lockedOrigin.lng))
01505:             ? { lat: Number(lockedOrigin.lat), lng: Number(lockedOrigin.lng), label: String(lockedOrigin.label || 'Locked centre').slice(0, 80) }
01506:             : null;
01507:         merged.missionLockAudio = merged.missionLockAudio !== false;
01508:         merged.missionValue = merged.missionValue !== false;
01509:         merged.tabletMode = ['auto', 'on', 'off'].includes(String(merged.tabletMode)) ? String(merged.tabletMode) : 'auto';
01510:         merged.mobileMode = ['auto', 'on', 'off'].includes(String(merged.mobileMode)) ? String(merged.mobileMode) : 'auto';
01511:         merged.transportWatcher = merged.transportWatcher !== false;
01512:         merged.missionInspector = merged.missionInspector !== false;
01513:         merged.stuckDetector.enabled = merged.stuckDetector.enabled !== false;
01514:         merged.stuckDetector.thresholdMin = Math.round(clamp(merged.stuckDetector.thresholdMin, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
01515:         merged.missionSpawn.enabled = merged.missionSpawn.enabled !== false;
01516:         merged.resourceGap.enabled = Boolean(merged.resourceGap.enabled);
01517:         merged.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(merged.resourceGap.radiusMi)) ? Number(merged.resourceGap.radiusMi) : 25;
01518:         merged.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(merged.transportSweep.delayMs)) ? Number(merged.transportSweep.delayMs) : 2000;
01519:         merged.transportSweep.maxPerRun = Math.round(clamp(merged.transportSweep.maxPerRun, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
01520:         merged.payoutFlash.enabled = merged.payoutFlash.enabled !== false;
01521:         merged.payoutFlash.threshold = Math.round(clamp(merged.payoutFlash.threshold, 1000, 1000000000, 10000));
01522:         merged.payoutFlash.durationMs = normalisePayoutFlashDuration(merged.payoutFlash.durationMs);
01523:         merged.payoutFlash.template = PAYOUT_TEMPLATES[merged.payoutFlash.template] ? merged.payoutFlash.template : 'gta5';
01524:         merged.payoutFlash.soundEnabled = Boolean(merged.payoutFlash.soundEnabled);
01525:         merged.payoutFlash.soundVolume = clamp(merged.payoutFlash.soundVolume, 0, 1, 0.35);
01526:         merged.discordReport.webhookName = String(merged.discordReport.webhookName || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
01527:         merged.discordReport.topCategories = [3, 5, 8].includes(Number(merged.discordReport.topCategories)) ? Number(merged.discordReport.topCategories) : 5;
01528:         merged.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'last90', 'last180', 'last365', 'allAvailable', 'session', 'sinceLast', 'custom'].includes(merged.discordReport.period) ? merged.discordReport.period : 'today';
01529:         merged.discordReport.customStart = /^\d{4}-\d{2}-\d{2}$/u.test(String(merged.discordReport.customStart || '')) ? String(merged.discordReport.customStart) : localIsoDate(new Date(Date.now() - 6 * 86400000));
01530:         merged.discordReport.customEnd = /^\d{4}-\d{2}-\d{2}$/u.test(String(merged.discordReport.customEnd || '')) ? String(merged.discordReport.customEnd) : localIsoDate();
01531:         merged.discordReport.includeChart = merged.discordReport.includeChart !== false;
01532:         merged.discordReport.includeComparison = merged.discordReport.includeComparison !== false;
01533:         merged.discordReport.reportMode = ['executive', 'fullAudit'].includes(String(merged.discordReport.reportMode)) ? String(merged.discordReport.reportMode) : 'fullAudit';
01534:         merged.discordReport.includeForecast = merged.discordReport.includeForecast !== false;
01535:         merged.discordReport.includeRisk = merged.discordReport.includeRisk !== false;
01536:         merged.financialVault.enabled = merged.financialVault.enabled !== false;
01537:         merged.financialVault.ruleFeedEnabled = merged.financialVault.ruleFeedEnabled !== false;
01538:         merged.financialVault.retentionDays = String(merged.financialVault.retentionDays) === 'all'
01539:             ? 'all'
01540:             : ([90, 180, 365, 730, 1825].includes(Number(merged.financialVault.retentionDays)) ? Number(merged.financialVault.retentionDays) : 'all');
```

## Mission-window and Mission Value CSS vicinity

Canonical lines 3800–4380

```javascript
03800:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-key {
03801:             position: relative !important; z-index: 2 !important;
03802:             width: 21px !important; height: 21px !important; border-radius: 7px !important; font-size: 10px !important;
03803:             background: rgba(255,255,255,.11) !important; border: 1px solid rgba(255,255,255,.10) !important;
03804:         }
03805:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
03806:             background: rgba(23,198,126,.95) !important; border-color: rgba(194,255,226,.72) !important;
03807:             box-shadow: 0 0 9px rgba(67,239,166,.55) !important;
03808:         }
03809:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop { display: none !important; }
03810:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet {
03811:             position: relative !important; z-index: 2 !important;
03812:             display: flex !important; align-items: center !important; justify-content: flex-start !important;
03813:             min-width: 0 !important; min-height: 2.05em !important; max-height: 2.05em !important;
03814:             overflow: hidden !important; text-overflow: clip !important; white-space: normal !important;
03815:             overflow-wrap: normal !important; word-break: normal !important; hyphens: none !important;
03816:             font-size: clamp(9px,1.1vw,10.25px) !important; line-height: 1.03 !important; letter-spacing: -.08px !important;
03817:             font-weight: 900 !important; text-align: left !important; padding-right: 4px !important; text-shadow: 0 1px 2px rgba(0,0,0,.72) !important;
03818:         }
03819:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
03820:             grid-area: pins !important;
03821:             display: grid !important;
03822:             grid-template-columns: repeat(var(--mcms-tablet-pin-columns, 4), minmax(0,1fr)) !important;
03823:             gap: 7px !important;
03824:             width: 100% !important; max-width: none !important; max-height: none !important; margin-top: 0 !important;
03825:             overflow: visible !important; padding: 0 !important;
03826:             overscroll-behavior: auto !important; -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
03827:             pointer-events: none !important;
03828:         }
03829:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
03830:         html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
03831:             flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
03832:             height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
03833:             border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
03834:             pointer-events: auto !important;
03835:         }
03836: 
03837:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} {
03838:             padding: 12px !important; border-radius: 18px !important;
03839:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03840:             box-shadow: 0 12px 30px rgba(0,0,0,.52) !important;
03841:             overflow-y: auto !important; overflow-x: hidden !important; overscroll-behavior: contain !important;
03842:             -webkit-overflow-scrolling: touch !important; touch-action: pan-y !important;
03843:             font-size: 13px !important; line-height: 1.25 !important;
03844:         }
03845:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-header {
03846:             position: sticky !important; top: -12px !important; z-index: 8 !important;
03847:             grid-template-columns: minmax(0,1fr) 44px 44px !important; gap: 9px !important;
03848:             min-height: 54px !important; margin: -12px -12px 10px !important; padding: 10px 12px 9px !important;
03849:             background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
03850:         }
03851:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
03852:             cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
03853:         }
03854:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
03858:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03859:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
03860:         }
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close { font-size:24px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tabs {
03863:             position: sticky !important; top: 42px !important; z-index: 7 !important;
03864:             grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 8px !important;
03865:             margin: 0 -4px 12px !important; padding: 8px 4px !important; background: rgba(8,12,18,.985) !important;
03866:         }
03867:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
03868:             height: 44px !important; border-radius: 11px !important; font-size: 11.5px !important; padding: 0 6px !important;
03869:         }
03870:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap: 9px !important; }
03871:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
03872:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
03873:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
03874:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-place-main {
03875:             min-height: 58px !important; height: auto !important; padding: 9px !important;
03876:             grid-template-columns: 30px minmax(0,1fr) !important; gap: 9px !important; border-radius: 12px !important;
03877:         }
03878:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-iconbox {
03879:             width: 30px !important; height: 30px !important; min-width: 30px !important; border-radius: 9px !important; font-size: 13px !important;
03880:         }
03881:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-label { font-size: 12.5px !important; line-height: 1.15 !important; }
03882:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top: 5px !important; max-width: 120px !important; padding: 3px 7px !important; font-size: 9px !important; }
03883:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin: 14px 0 8px !important; font-size: 10.5px !important; letter-spacing: .8px !important; }
03884:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
03885:             grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
03886:         }
03887:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
03888:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03889:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03890:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03891:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03892:         }
03893:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03894:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03895:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03896:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03897:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03898:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03899:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03900:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
03901:         }
03902:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn {
03903:             min-height: 44px !important; height: auto !important; line-height: 1.15 !important; padding: 7px 8px !important;
03904:         }
03905:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
03906:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
03907:             grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
03908:         }
03909:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
03910:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
03911:             margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
03912:         }
03913:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
03914:             grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
03915:         }
03916:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
03917:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
03918:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
03919:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
03920:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
03921:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
03922:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
03923:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }
03924: 
03925:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
03926:             left: 50% !important; right: auto !important; top: auto !important; bottom: max(8px, env(safe-area-inset-bottom)) !important;
03927:             width: min(700px, calc(100vw - 16px)) !important; max-width: calc(100vw - 16px) !important; max-height: 78dvh !important;
03928:             transform: translateX(-50%) !important; padding: 12px !important; border-radius: 18px !important;
03929:             background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03930:             overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
03931:         }
03932:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
03933:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
03934:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
03935:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
03936:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
03937:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
03938:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
03939:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
03940:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }
03941: 
03942:         html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
03943:             width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
03944:             font-size: 12px !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
03945:         }
03946:         html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
03947:             max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
03948:         }
03949: 
03950:         @media (max-width: 560px) {
03951:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }
03952:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
03953:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row,
03954:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 1fr !important; }
03955:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { white-space: normal !important; }
03956:         }
03957: 
03958: 
03959:         /* v3.3.1 iOS Safari Mobile Mode: map-aware command grid, safe-area bottom sheet,
03960:            Visual Viewport keyboard support and compact high-contrast touch controls. */
03961:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId},
03962:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
03963:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId},
03964:         html[data-mcms-mobile-active="true"] #${SCRIPT.missionInspectorId} {
03965:             -webkit-tap-highlight-color: transparent !important;
03966:         }
03967:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} button,
03968:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} button,
03969:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input,
03970:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} select,
03971:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} button {
03972:             touch-action: manipulation !important;
03973:         }
03974:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
03975:             width: var(--mcms-mobile-dock-width, calc(100% - 10px)) !important;
03976:             max-width: var(--mcms-mobile-dock-width, calc(100% - 10px)) !important;
03977:             display: grid !important;
03978:             grid-template-columns: repeat(var(--mcms-mobile-columns, 5), minmax(0,1fr)) !important;
03979:             grid-auto-flow: row !important;
03980:             align-items: stretch !important;
03981:             gap: 4px !important;
03982:             margin: 0 !important;
03983:             font-size: 10px !important;
03984:             pointer-events: none !important;
03985:         }
03986:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(5px, env(safe-area-inset-left)) !important; top: max(5px, env(safe-area-inset-top)) !important; }
03987:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(5px, env(safe-area-inset-right)) !important; top: max(5px, env(safe-area-inset-top)) !important; }
03988:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(5px, env(safe-area-inset-left)) !important; bottom: max(5px, env(safe-area-inset-bottom)) !important; }
03989:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(5px, env(safe-area-inset-right)) !important; bottom: max(5px, env(safe-area-inset-bottom)) !important; }
03990:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-shell {
03991:             grid-column: auto !important; grid-row: auto !important; grid-area: auto !important;
03992:             width: auto !important; min-width: 0 !important; height: var(--mcms-mobile-filter-height,44px) !important;
03993:             border-radius: 10px !important; background: rgba(6,10,16,.97) !important;
03994:             border-color: rgba(116,207,255,.62) !important; box-shadow: 0 3px 10px rgba(0,0,0,.42), inset 0 1px rgba(255,255,255,.08) !important;
03995:             backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
03996:         }
03997:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 19px !important; }
03998:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 14px !important; flex-basis: 14px !important; font-size: 10px !important; }
03999:         html[data-mcms-command-bar-open="false"][data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
04000:             width: 50px !important; max-width: 50px !important; grid-template-columns: 50px !important;
04001:         }
04002:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
04003:             display: contents !important; grid-area: auto !important; width: auto !important; max-width: none !important;
04004:             overflow: visible !important; padding: 0 !important; margin: 0 !important; pointer-events: none !important;
04005:         }
04006:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
04007:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
04008:             position: relative !important; isolation: isolate !important; width: auto !important; min-width: 0 !important;
04009:             height: var(--mcms-mobile-filter-height,44px) !important; display: grid !important;
04010:             grid-template-columns: 17px minmax(0,1fr) !important; gap: 3px !important; padding: 0 4px !important;
04011:             border-radius: 10px !important; border: 1px solid rgba(255,255,255,.18) !important;
04012:             background: linear-gradient(180deg,rgba(13,19,27,.98),rgba(6,9,14,.98)) !important;
04013:             color: rgba(255,255,255,.78) !important; box-shadow: 0 3px 10px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.04) !important;
04014:             backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
04015:             transition: background 110ms ease,border-color 110ms ease,box-shadow 110ms ease,color 110ms ease,opacity 110ms ease,transform 110ms ease !important;
04016:         }
04017:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) { opacity: .72 !important; }
04018:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
04019:             opacity: 1 !important; transform: translateY(-1px) !important;
04020:             background: linear-gradient(145deg,rgba(7,112,76,.99),rgba(7,77,103,.99) 60%,rgba(12,43,77,.99)) !important;
04021:             border-color: #69ffc0 !important; color: #fff !important;
04022:             box-shadow: 0 0 0 1px rgba(105,255,192,.20),0 0 13px rgba(42,222,158,.45),0 4px 12px rgba(0,0,0,.44),inset 0 1px rgba(255,255,255,.18) !important;
04023:         }
04024:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::before {
04025:             content: "" !important; position:absolute !important; z-index:1 !important; left:4px !important; right:4px !important; bottom:2px !important;
04026:             height:3px !important; border-radius:999px !important; background:linear-gradient(90deg,transparent,#72ffc0 18%,#62dcff 82%,transparent) !important;
04027:             box-shadow:0 0 7px rgba(99,242,177,.9) !important; pointer-events:none !important;
04028:         }
04029:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
04030:             content:"" !important; position:absolute !important; z-index:3 !important; right:4px !important; top:4px !important;
04031:             width:4px !important; height:4px !important; border-radius:50% !important; background:#7affc5 !important;
04032:             box-shadow:0 0 0 2px rgba(5,35,29,.72),0 0 7px rgba(118,255,193,.98) !important; pointer-events:none !important;
04033:         }
04034:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-key {
04035:             position:relative !important; z-index:2 !important; width:17px !important; height:17px !important; border-radius:6px !important;
04036:             font-size:8px !important; background:rgba(255,255,255,.10) !important; border:1px solid rgba(255,255,255,.10) !important;
04037:         }
04038:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
04039:             background:rgba(23,198,126,.96) !important; border-color:rgba(194,255,226,.75) !important; box-shadow:0 0 7px rgba(67,239,166,.58) !important;
04040:         }
04041:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop,
04042:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet { display:none !important; }
04043:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-mobile {
04044:             position:relative !important; z-index:2 !important; display:flex !important; align-items:center !important; justify-content:flex-start !important;
04045:             min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important;
04046:             font-size:clamp(7.5px,2.15vw,9px) !important; line-height:1 !important; font-weight:950 !important; letter-spacing:-.15px !important;
04047:             text-align:left !important; text-shadow:0 1px 2px rgba(0,0,0,.78) !important;
04048:         }
04049:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
04050:             grid-area:auto !important; grid-column:1 / -1 !important; display:grid !important;
04051:             grid-template-columns:repeat(var(--mcms-mobile-pin-columns,4),minmax(0,1fr)) !important;
04052:             grid-auto-flow:row !important; justify-self:stretch !important; align-self:stretch !important;
04053:             justify-items:stretch !important; align-items:stretch !important;
04054:             gap:4px !important; width:100% !important; min-width:0 !important; max-width:none !important; max-height:none !important;
04055:             box-sizing:border-box !important; margin:0 !important; padding:0 !important;
04056:             overflow:visible !important; pointer-events:none !important;
04057:         }
04058:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display:none !important; }
04059:         html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
04060:             -webkit-appearance:none !important; appearance:none !important;
04061:             display:flex !important; align-items:center !important; justify-content:center !important;
04062:             justify-self:stretch !important; align-self:stretch !important; box-sizing:border-box !important;
04063:             width:100% !important; max-width:none !important; min-width:0 !important;
04064:             height:var(--mcms-mobile-pin-height,34px) !important; padding:0 7px !important;
04065:             border-radius:9px !important; font-size:clamp(8.5px,2.25vw,10px) !important; line-height:1.05 !important;
04066:             letter-spacing:-.08px !important; text-align:center !important; overflow:hidden !important; text-overflow:ellipsis !important;
04067:             white-space:nowrap !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important; pointer-events:auto !important;
04068:         }
04069:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} {
04070:             width:calc(100% - 8px) !important; max-width:calc(100% - 8px) !important;
04071:             border-radius:16px 16px 11px 11px !important; border-color:rgba(112,204,255,.46) !important;
04072:             padding:8px 8px calc(8px + env(safe-area-inset-bottom)) !important;
04073:             overflow-x:hidden !important; overflow-y:auto !important; overscroll-behavior:contain !important;
04074:             -webkit-overflow-scrolling:touch !important; touch-action:pan-y !important;
04075:             background:linear-gradient(180deg,rgba(9,14,21,.99),rgba(4,7,11,.99)) !important;
04076:             box-shadow:0 -12px 38px rgba(0,0,0,.58),inset 0 1px rgba(255,255,255,.06) !important;
04077:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04078:         }
04079:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}::-webkit-scrollbar,
04080:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs::-webkit-scrollbar { display:none !important; width:0 !important; height:0 !important; }
04081:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
04082:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { scrollbar-width:none !important; }
04083:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header {
04084:             position:sticky !important; top:-8px !important; z-index:8 !important; min-height:48px !important; margin:-8px -8px 7px !important;
04085:             grid-template-columns:minmax(0,1fr) 44px 44px !important; gap:6px !important;
04086:             padding:8px 8px 6px !important; border-radius:16px 16px 0 0 !important; background:rgba(7,11,17,.985) !important;
04087:             border-bottom:1px solid rgba(255,255,255,.10) !important;
04088:         }
04089:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-drag-handle { cursor:default !important; touch-action:pan-y !important; }
04090:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-title { font-size:12px !important; letter-spacing:.35px !important; }
04091:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top:3px !important; font-size:9px !important; }
04092:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display:none !important; }
04093:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-close,
04094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-help-button { width:44px !important; height:44px !important; border-radius:12px !important; font-size:20px !important; line-height:42px !important; }
04095:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
04096:             position:sticky !important; top:40px !important; z-index:7 !important; display:flex !important; gap:5px !important;
04097:             margin:0 -2px 7px !important; padding:2px 2px 6px !important; overflow-x:auto !important; overflow-y:hidden !important;
04098:             overscroll-behavior-x:contain !important; -webkit-overflow-scrolling:touch !important; background:rgba(6,10,15,.96) !important;
04099:         }
04100:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
04101:             flex:0 0 auto !important; min-width:74px !important; height:40px !important; padding:0 10px !important; border-radius:10px !important;
04102:             font-size:10px !important; line-height:1 !important;
04103:         }
04104:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap:6px !important; }
04105:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
04106:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
04107:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-place-main { min-height:48px !important; height:auto !important; padding:7px !important; border-radius:11px !important; }
04108:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-iconbox { width:22px !important; height:22px !important; min-width:22px !important; }
04109:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-label { font-size:11px !important; }
04110:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top:4px !important; max-width:110px !important; font-size:8px !important; }
04111:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin:12px 0 7px !important; font-size:9.5px !important; }
04112:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:minmax(0,1fr) minmax(132px,44%) !important; gap:7px !important; margin-bottom:7px !important; }
04113:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size:10.5px !important; white-space:normal !important; }
04114:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-input,
04115:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-select {
04116:             min-height:44px !important; height:44px !important; border-radius:10px !important; padding:0 9px !important;
04117:             font-size:16px !important; line-height:1.2 !important;
04118:         }
04119:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input[type="range"].mcms-input { min-height:44px !important; }
04120:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
04121:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
04122:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
04123:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }
04124:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn { min-height:44px !important; height:auto !important; line-height:1.15 !important; padding:7px !important; white-space:normal !important; overflow-wrap:anywhere !important; }
04125:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
04126:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }
04127:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }
04128:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
04129:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
04130:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
04131:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
04132:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
04133:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04134:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }
04135:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }
04136:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }
04137:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-footer { display:none !important; }
04138:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
04139:             left:max(4px,env(safe-area-inset-left)) !important; right:max(4px,env(safe-area-inset-right)) !important;
04140:             bottom:max(4px,env(safe-area-inset-bottom)) !important; top:auto !important; width:auto !important; max-width:none !important;
04141:             max-height:min(72dvh,620px) !important; border-radius:15px !important; padding-bottom:calc(9px + env(safe-area-inset-bottom)) !important;
04142:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04143:         }
04144:         html[data-mcms-mobile-active="true"] #${SCRIPT.missionInspectorId} {
04145:             width:min(92vw,340px) !important; max-width:calc(100vw - 16px) !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04146:         }
04147:         html[data-mcms-mobile-active="true"] #${SCRIPT.toastId} {
04148:             left:50% !important; right:auto !important; bottom:calc(12px + env(safe-area-inset-bottom)) !important;
04149:             max-width:calc(100vw - 24px) !important; transform:translate(-50%,8px) !important;
04150:         }
04151:         html[data-mcms-mobile-active="true"] #${SCRIPT.toastId}.mcms-flash { transform:translate(-50%,0) !important; }
04152:         html[data-mcms-mobile-active="true"] .mcms-alliance-credit-badge,
04153:         html[data-mcms-mobile-active="true"] .mcms-mission-age-badge,
04154:         html[data-mcms-mobile-active="true"] .mcms-unit-commitment-badge,
04155:         html[data-mcms-mobile-active="true"] .mcms-transport-watcher-badge,
04156:         html[data-mcms-mobile-active="true"] .mcms-resource-gap-badge {
04157:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04158:         }
04159:         @media (max-width: 430px) {
04160:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04161:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04162:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04163:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04164:         }
04165:         @media (orientation: landscape) and (max-height: 500px) {
04166:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }
04167:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { min-height:42px !important; padding-top:5px !important; }
04168:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { display:none !important; }
04169:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { top:34px !important; }
04170:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { height:36px !important; }
04171:         }
04172: 
04173:         /* v3.4.2: collapse after the exit animation and override later tablet/mobile layout rules. */
04174:         #${SCRIPT.controlId} {
04175:             transition: width 180ms cubic-bezier(.2,.78,.22,1), max-width 180ms cubic-bezier(.2,.78,.22,1) !important;
04176:         }
04177:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
04178:         html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins {
04179:             display: none !important;
04180:             pointer-events: none !important;
04181:         }
04182:         @media (prefers-reduced-motion: reduce) {
04183:             #${SCRIPT.controlId} { transition: none !important; }
04184:         }
04185: 
04186:         /* v2.5.x mission intelligence and configuration tools */
04187:         #${SCRIPT.missionInspectorId} {
04188:             position: fixed !important; left: 0 !important; top: 0 !important; z-index: 2147483646 !important;
04189:             width: min(300px, calc(100vw - 24px)) !important; padding: 10px 11px !important;
04190:             border: 1px solid rgba(255,255,255,.18) !important; border-radius: 10px !important;
04191:             background: linear-gradient(180deg, rgba(14,19,27,.97), rgba(7,10,15,.96)) !important;
04192:             color: #eef4fb !important; box-shadow: 0 14px 34px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.06) !important;
04193:             font: 700 10px/1.35 Arial, Helvetica, sans-serif !important; pointer-events: none !important;
04194:             opacity: 0 !important; visibility: hidden !important; transform: translateY(4px) scale(.985) !important;
04195:             transition: opacity 110ms ease, transform 110ms ease, visibility 110ms step-end !important; backdrop-filter: blur(6px) !important;
04196:         }
04197:         #${SCRIPT.missionInspectorId}.mcms-open { opacity: 1 !important; visibility: visible !important; transform: translateY(0) scale(1) !important; transition: opacity 110ms ease, transform 110ms ease, visibility 0s step-start !important; }
04198:         #${SCRIPT.missionInspectorId} .mcms-inspector-head { display:flex !important; align-items:flex-start !important; justify-content:space-between !important; gap:8px !important; margin-bottom:7px !important; }
04199:         #${SCRIPT.missionInspectorId} .mcms-inspector-title { display:block !important; min-width:0 !important; color:#fff !important; font-size:12px !important; font-weight:950 !important; line-height:1.2 !important; overflow:hidden !important; text-overflow:ellipsis !important; }
04200:         #${SCRIPT.missionInspectorId} .mcms-inspector-type { flex:0 0 auto !important; padding:3px 5px !important; border-radius:5px !important; border:1px solid rgba(255,255,255,.16) !important; background:rgba(255,255,255,.06) !important; color:#b9c8d8 !important; font-size:7px !important; font-weight:950 !important; letter-spacing:.6px !important; }
04201:         #${SCRIPT.missionInspectorId} .mcms-inspector-type.mcms-alliance { color:#8df3ad !important; border-color:rgba(112,239,155,.38) !important; }
04202:         #${SCRIPT.missionInspectorId} .mcms-inspector-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
04203:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat { min-width:0 !important; padding:6px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; border:1px solid rgba(255,255,255,.08) !important; }
04204:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat span { display:block !important; color:#8393a5 !important; font-size:7px !important; font-weight:900 !important; letter-spacing:.4px !important; text-transform:uppercase !important; }
04205:         #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong { display:block !important; margin-top:2px !important; color:#fff !important; font-size:11px !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
04206:         #${SCRIPT.missionInspectorId} .mcms-inspector-alert { margin-top:6px !important; padding:6px 7px !important; border-radius:7px !important; border:1px solid rgba(255,181,71,.34) !important; background:rgba(255,143,31,.11) !important; color:#ffd29a !important; font-size:8px !important; font-weight:900 !important; line-height:1.35 !important; white-space:normal !important; overflow-wrap:anywhere !important; }
04207:         #${SCRIPT.missionInspectorId} .mcms-inspector-alert.mcms-stuck { border-color:rgba(255,74,64,.48) !important; background:rgba(255,44,36,.14) !important; color:#ffaaa4 !important; }
04208: 
04209: 
04210:         .mcms-mission-value-row {
04211:             display: flex !important;
04212:             align-items: center !important;
04213:             justify-content: flex-end !important;
04214:             min-width: 0 !important;
04215:             box-sizing: border-box !important;
04216:             position: relative !important;
04217:             z-index: 2 !important;
04218:             pointer-events: none !important;
04219:         }
04220:         #navbar-alarm-spacer > .mcms-mission-value-row,
04221:         .mcms-mission-value-row[data-mcms-host="toolbar"] {
04222:             flex: 1 1 auto !important;
04223:             width: 100% !important;
04224:             min-height: 32px !important;
04225:             margin: 0 !important;
04226:             padding: 0 3px 0 6px !important;
04227:             clear: none !important;
04228:             overflow: hidden !important;
04229:         }
04230:         .mcms-mission-value-row[data-mcms-host="fallback"] {
04231:             width: 100% !important;
04232:             min-height: 30px !important;
04233:             margin: 0 0 6px 0 !important;
04234:             padding: 4px 8px !important;
04235:             clear: both !important;
04236:             overflow: hidden !important;
04237:         }
04238:         .mcms-mission-value-badge {
04239:             display: inline-flex !important;
04240:             align-items: center !important;
04241:             justify-content: center !important;
04242:             max-width: 100% !important;
04243:             min-width: 0 !important;
04244:             min-height: 24px !important;
04245:             box-sizing: border-box !important;
04246:             padding: 4px 9px !important;
04247:             border: 1px solid rgba(235,190,64,.72) !important;
04248:             border-radius: 8px !important;
04249:             background: linear-gradient(145deg, rgba(48,39,13,.96), rgba(19,21,24,.96)) !important;
04250:             color: #ffe59a !important;
04251:             box-shadow: 0 2px 8px rgba(0,0,0,.34) !important;
04252:             font: 900 11px/1.2 Arial, Helvetica, sans-serif !important;
04253:             letter-spacing: .15px !important;
04254:             text-align: right !important;
04255:             white-space: nowrap !important;
04256:             overflow: hidden !important;
04257:             text-overflow: ellipsis !important;
04258:             pointer-events: none !important;
04259:         }
04260:         .mcms-mission-value-row[data-mcms-mode="value"] .mcms-mission-value-badge {
04261:             padding-left: 7px !important;
04262:             padding-right: 7px !important;
04263:         }
04264:         @media (max-width: 767px) {
04265:             .mcms-mission-value-row[data-mcms-host="fallback"] {
04266:                 padding: 4px 6px !important;
04267:             }
04268:             .mcms-mission-value-badge {
04269:                 font-size: 10px !important;
04270:             }
04271:         }
04272: 
04273:         .mcms-stuck-mission-icon { pointer-events:none !important; }
04274:         .mcms-stuck-mission-badge { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:58px !important; height:17px !important; padding:0 6px !important; border-radius:6px !important; border:1px solid rgba(255,86,72,.72) !important; background:rgba(90,10,8,.88) !important; color:#ffd7d2 !important; font:950 8px/17px Arial,Helvetica,sans-serif !important; letter-spacing:.35px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 10px rgba(255,53,39,.32) !important; white-space:nowrap !important; }
04275:         .mcms-stuck-mission-badge.mcms-stuck-severe { background:rgba(130,7,4,.94) !important; border-color:#ff3d2e !important; color:#fff !important; animation:mcmsStuckPulse 1.3s ease-in-out infinite !important; }
04276:         @keyframes mcmsStuckPulse { 0%,100%{box-shadow:0 0 7px rgba(255,53,39,.28);transform:scale(1)} 50%{box-shadow:0 0 16px rgba(255,53,39,.70);transform:scale(1.035)} }
04277: 
04278:         .mcms-mission-spawn-ring { transform-box:fill-box !important; stroke:#67d9ff !important; stroke-width:3 !important; fill:rgba(48,183,255,.12) !important; transform-origin:center !important; animation:mcmsMissionSpawnRing 2.35s cubic-bezier(.12,.72,.18,1) both !important; pointer-events:none !important; }
04279:         .mcms-mission-spawn-label-icon { pointer-events:none !important; }
04280:         .mcms-mission-spawn-label { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:86px !important; height:20px !important; padding:0 8px !important; border-radius:7px !important; border:1px solid rgba(98,219,255,.78) !important; background:rgba(4,22,34,.92) !important; color:#aeeeff !important; font:950 8px/20px Arial,Helvetica,sans-serif !important; letter-spacing:.65px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 16px rgba(67,198,255,.42) !important; animation:mcmsMissionSpawnLabel 2.35s ease-out both !important; white-space:nowrap !important; }
04281:         .leaflet-marker-icon.mcms-mission-spawn-focus { animation:mcmsMissionSpawnMarker 2.2s cubic-bezier(.16,.74,.18,1) both !important; }
04282:         @keyframes mcmsMissionSpawnRing { 0%{opacity:0;transform:scale(.25)} 12%{opacity:1;transform:scale(.55)} 75%{opacity:.50;transform:scale(3.2)} 100%{opacity:0;transform:scale(4.2)} }
04283:         @keyframes mcmsMissionSpawnLabel { 0%{opacity:0;transform:translateY(8px) scale(.9)} 14%,72%{opacity:1;transform:translateY(0) scale(1)} 100%{opacity:0;transform:translateY(-8px) scale(.96)} }
04284:         @keyframes mcmsMissionSpawnMarker { 0%{filter:brightness(1);transform:scale(1)} 12%{filter:brightness(1.55) drop-shadow(0 0 10px #53d9ff);transform:scale(1.22)} 34%{filter:brightness(1.15) drop-shadow(0 0 6px #53d9ff);transform:scale(.98)} 58%{filter:brightness(1.35) drop-shadow(0 0 8px #53d9ff);transform:scale(1.12)} 100%{filter:brightness(1);transform:scale(1)} }
04285: 
04286:         #${SCRIPT.panelId} .mcms-profile-list { display:grid !important; gap:6px !important; }
04287:         #${SCRIPT.panelId} .mcms-profile-row { display:grid !important; grid-template-columns:minmax(0,1fr) 36px 36px 25px !important; gap:5px !important; align-items:center !important; }
04288:         #${SCRIPT.panelId} .mcms-profile-main { min-width:0 !important; padding:6px 7px !important; border:1px solid rgba(255,255,255,.09) !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; }
04289:         #${SCRIPT.panelId} .mcms-profile-main strong,#${SCRIPT.panelId} .mcms-profile-main span { display:block !important; min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
04290:         #${SCRIPT.panelId} .mcms-profile-main strong { color:#edf4fb !important; font-size:9px !important; }
04291:         #${SCRIPT.panelId} .mcms-profile-main span { color:#8393a5 !important; font-size:7px !important; margin-top:2px !important; }
04292:         #${SCRIPT.panelId} .mcms-config-actions { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
04293:         #${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:normal !important; text-overflow:clip !important; overflow-wrap:anywhere !important; }
04294:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
04295:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions [data-action="reset-config"] { grid-column:1 / -1 !important; }
04296:         #${SCRIPT.panelId} .mcms-hidden-file { display:none !important; }
04297: 
04298: 
04299:         /* v3.7.0 complete interface themes */
04300:         #${SCRIPT.panelId} .mcms-ui-theme-grid {
04301:             display: grid !important;
04302:             grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
04303:             gap: 7px !important;
04304:             margin-bottom: 7px !important;
04305:         }
04306:         #${SCRIPT.panelId} .mcms-ui-theme-btn {
04307:             position: relative !important;
04308:             display: grid !important;
04309:             grid-template-columns: 48px minmax(0, 1fr) !important;
04310:             align-items: center !important;
04311:             gap: 8px !important;
04312:             min-width: 0 !important;
04313:             height: 58px !important;
04314:             padding: 6px 8px !important;
04315:             border: 1px solid rgba(255,255,255,.14) !important;
04316:             border-radius: 10px !important;
04317:             background: rgba(255,255,255,.055) !important;
04318:             color: rgba(255,255,255,.82) !important;
04319:             cursor: pointer !important;
04320:             text-align: left !important;
04321:             overflow: hidden !important;
04322:             transition: transform 140ms ease, border-color 140ms ease, background 140ms ease !important;
04323:         }
04324:         #${SCRIPT.panelId} .mcms-ui-theme-btn:hover,
04325:         #${SCRIPT.panelId} .mcms-ui-theme-btn:focus-visible {
04326:             transform: translateY(-1px) !important;
04327:             border-color: rgba(124,194,255,.72) !important;
04328:             background: rgba(93,169,255,.12) !important;
04329:         }
04330:         #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active {
04331:             border-color: rgba(124,194,255,.92) !important;
04332:             background: linear-gradient(135deg, rgba(25,118,210,.34), rgba(20,50,82,.26)) !important;
04333:             box-shadow: inset 0 0 0 1px rgba(145,210,255,.14), 0 5px 14px rgba(0,0,0,.18) !important;
04334:             color: #fff !important;
04335:         }
04336:         #${SCRIPT.panelId} .mcms-ui-theme-preview {
04337:             display: grid !important;
04338:             grid-template-columns: repeat(3, 1fr) !important;
04339:             align-items: end !important;
04340:             gap: 3px !important;
04341:             width: 48px !important;
04342:             height: 36px !important;
04343:             padding: 5px !important;
04344:             border: 1px solid rgba(255,255,255,.16) !important;
04345:             border-radius: 7px !important;
04346:             background: rgba(3,7,12,.74) !important;
04347:             overflow: hidden !important;
04348:         }
04349:         #${SCRIPT.panelId} .mcms-ui-theme-preview span { display: block !important; border-radius: 2px 2px 0 0 !important; }
04350:         #${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(1) { height: 52% !important; background: #4c89bd !important; }
04351:         #${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(2) { height: 86% !important; background: #d7e8f7 !important; }
04352:         #${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(3) { height: 68% !important; background: #2c5f87 !important; }
04353:         #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk {
04354:             border-radius: 1px !important;
04355:             border-color: #00f0ff !important;
04356:             background: #080b12 !important;
04357:             box-shadow: inset 0 0 9px rgba(0,240,255,.20) !important;
04358:             clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
04359:         }
04360:         #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span { border-radius: 0 !important; }
04361:         #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(1) { height: 82% !important; background: #fcee0a !important; }
04362:         #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(2) { height: 48% !important; background: #00f0ff !important; }
04363:         #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(3) { height: 68% !important; background: #ff003c !important; }
04364:         #${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4 {
04365:             position: relative !important;
04366:             border-radius: 5px !important;
04367:             border-color: #7fbd52 !important;
04368:             background:
04369:                 repeating-linear-gradient(0deg, rgba(188,255,108,.055) 0 1px, transparent 1px 4px),
04370:                 radial-gradient(circle at 50% 44%, #172817, #071008 78%) !important;
04371:             box-shadow: inset 0 0 12px rgba(160,255,94,.26), 0 0 8px rgba(123,206,73,.12) !important;
04372:         }
04373:         #${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4::after {
04374:             content: 'STAT' !important;
04375:             position: absolute !important;
04376:             left: 4px !important;
04377:             top: 2px !important;
04378:             color: #c8ff8b !important;
04379:             font: 800 5px/1 Consolas, monospace !important;
04380:             letter-spacing: .5px !important;
```

## Transport Sweep mission-window discovery and lifecycle patterns

Canonical lines 16350–17580

```javascript
16350:         const horizontalOffset = occupiedWidth > 0
16351:             ? Math.ceil((occupiedWidth / 2) + watcherHalfWidth + gap)
16352:             : 21;
16353: 
16354:         let side = 'right';
16355:         try {
16356:             const latLng = marker?.getLatLng?.();
16357:             const point = latLng && map?.latLngToContainerPoint?.(latLng);
16358:             const size = map?.getSize?.();
16359:             const countExtra = Number(requirement?.count) > 1 ? 10 : 3;
16360:             if (point && size && point.x + horizontalOffset + watcherHalfWidth + countExtra > size.x - 4) side = 'left';
16361:         } catch (err) {}
16362: 
16363:         return {
16364:             side,
16365:             source,
16366:             horizontalOffset,
16367:             iconAnchor: [side === 'right' ? -horizontalOffset : horizontalOffset, 18],
16368:             signature: `${side}:${source}:${horizontalOffset}`
16369:         };
16370:     }
16371: 
16372:     function makeTransportWatcherIcon(requirement, placement) {
16373:         const type = ['patient', 'prisoner'].includes(requirement?.type) ? requirement.type : 'general';
16374:         const side = placement?.side === 'left' ? 'left' : 'right';
16375:         const count = Number(requirement?.count) > 1 ? `<span class="mcms-transport-watcher-count">${escapeHtml(requirement.count)}</span>` : '';
16376:         return pageWindow.L.divIcon({
16377:             className: 'mcms-transport-watcher-icon',
16378:             html: `<span class="mcms-transport-watcher-badge mcms-transport-${type} mcms-transport-side-${side}" aria-label="${escapeHtml(requirement?.label || 'Transport required')}" title="${escapeHtml(requirement?.label || 'Transport required')}">${transportWatcherSvg(type)}${count}</span>`,
16379:             iconSize: [0, 0],
16380:             iconAnchor: placement?.iconAnchor || [-21, 18]
16381:         });
16382:     }
16383: 
16384:     function updateTransportWatcherLabels() {
16385:         if (state.economyMode && economyMapMoving) return;
16386:         runtimeClearTimeout(transportWatcherTimer);
16387:         transportWatcherTimer = null;
16388:         if (!state.transportWatcher) {
16389:             clearTransportWatcherLabels();
16390:             return;
16391:         }
16392: 
16393:         const map = findLeafletMapInstance(false);
16394:         if (!map || !pageWindow.L || typeof pageWindow.L.layerGroup !== 'function' || typeof pageWindow.L.marker !== 'function' || typeof pageWindow.L.divIcon !== 'function') {
16395:             clearTransportWatcherLabels();
16396:             return;
16397:         }
16398:         const pane = ensureMissionFloatPane(map);
16399:         if (!pane) {
16400:             clearTransportWatcherLabels();
16401:             return;
16402:         }
16403:         const economyBounds = state.economyMode ? economyPaddedBounds(map, 0.08) : null;
16404: 
16405:         try {
16406:             if (!transportWatcherGroup || transportWatcherGroup._map !== map) {
16407:                 clearTransportWatcherLabels();
16408:                 transportWatcherGroup = pageWindow.L.layerGroup();
16409:                 transportWatcherGroup.__mcmsTransportWatcherLayer = true;
16410:                 transportWatcherGroup.addTo(map);
16411:             }
16412: 
16413:             const activeIds = new Set();
16414:             const now = Date.now();
16415:             for (const marker of getMissionMarkerIndex().markers) {
16416:                 const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
16417:                 if (missionId === null) continue;
16418:                 const personal = isPersonalMissionLayer(marker, missionId);
16419:                 if (personal && !state.visibility.myMissions) continue;
16420:                 if (!personal && !state.visibility.allianceMissions) continue;
16421:                 if (criticalViewActive && personal) {
16422:                     const ageRecord = personalMissionAgeRecord(marker, missionId, now);
16423:                     if (!ageRecord || ageRecord.ageMs < CRITICAL_VIEW_MIN_AGE_MS) continue;
16424:                 }
16425: 
16426:                 const snapshot = liveMissionSnapshots.get(missionId) || missionSnapshotFromMarker(marker, now);
16427:                 const requirement = transportRequirementFromSnapshot(snapshot);
16428:                 if (!requirement) continue;
16429: 
16430:                 let latLng = null;
16431:                 try { latLng = marker.getLatLng?.() || null; } catch (err) {}
16432:                 if (!latLng || (economyBounds && !economyBounds.contains?.(latLng))) continue;
16433:                 try {
16434:                     const onMap = typeof map.hasLayer === 'function' ? map.hasLayer(marker) : Boolean(marker._map);
16435:                     if (!onMap) continue;
16436:                 } catch (err) {}
16437: 
16438:                 const placement = transportWatcherPlacement(map, marker, missionId, requirement);
16439:                 const signature = `${requirement.type}:${requirement.count}:${requirement.label}:${placement.signature}`;
16440:                 activeIds.add(missionId);
16441:                 let label = transportWatcherLabels.get(missionId);
16442:                 if (!label) {
16443:                     label = pageWindow.L.marker(latLng, {
16444:                         interactive: false, keyboard: false, bubblingMouseEvents: false,
16445:                         pane, zIndexOffset: 0, icon: makeTransportWatcherIcon(requirement, placement)
16446:                     });
16447:                     label.__mcmsTransportWatcherSignature = signature;
16448:                     label.__mcmsTransportWatcherLabel = true;
16449:                     label.addTo(transportWatcherGroup);
16450:                     transportWatcherLabels.set(missionId, label);
16451:                 } else {
16452:                     try { label.setLatLng(latLng); } catch (err) {}
16453:                     if (label.__mcmsTransportWatcherSignature !== signature) {
16454:                         label.__mcmsTransportWatcherSignature = signature;
16455:                         try { label.setIcon(makeTransportWatcherIcon(requirement, placement)); } catch (err) {}
16456:                     }
16457:                 }
16458:             }
16459: 
16460:             for (const [missionId, label] of transportWatcherLabels.entries()) {
16461:                 if (activeIds.has(missionId)) continue;
16462:                 transportWatcherLabels.delete(missionId);
16463:                 try { transportWatcherGroup.removeLayer(label); } catch (err) {}
16464:             }
16465:         } catch (err) {
16466:             clearTransportWatcherLabels();
16467:         }
16468:     }
16469: 
16470:     function scheduleTransportWatcherRefresh(delay = 320) {
16471:         runtimeClearTimeout(transportWatcherTimer);
16472:         transportWatcherTimer = runtimeSetTimeout(updateTransportWatcherLabels, state.economyMode ? Math.max(900, delay) : delay);
16473:     }
16474: 
16475:     function transportSweepSleep(ms) {
16476:         return runtimeDelay(ms);
16477:     }
16478: 
16479:     function transportSweepElementVisible(element) {
16480:         if (!element || !element.isConnected) return false;
16481:         try {
16482:             const view = element.ownerDocument?.defaultView || window;
16483:             const style = view.getComputedStyle(element);
16484:             if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
16485:             const rect = element.getBoundingClientRect();
16486:             return rect.width > 0 && rect.height > 0;
16487:         } catch (err) {
16488:             return false;
16489:         }
16490:     }
16491: 
16492:     async function transportSweepWaitFor(test, timeoutMs = 5000, intervalMs = 120) {
16493:         const started = Date.now();
16494:         while (Date.now() - started < timeoutMs) {
16495:             if (runtime.destroyed || transportSweepRuntime.stopRequested) return null;
16496:             try {
16497:                 const value = test();
16498:                 if (value) return value;
16499:             } catch (err) {}
16500:             if (!await transportSweepSleep(intervalMs)) return null;
16501:         }
16502:         return null;
16503:     }
16504: 
16505:     function transportSweepLog(message, level = 'info') {
16506:         const clean = String(message || '').trim();
16507:         if (!clean) return;
16508:         transportSweepRuntime.statusMessage = clean;
16509:         transportSweepRuntime.statusLevel = String(level || 'info');
16510:         transportSweepRuntime.log.unshift({ time: Date.now(), message: clean, level });
16511:         if (transportSweepRuntime.log.length > 18) transportSweepRuntime.log.length = 18;
16512:         renderTransportSweepPanel();
16513:     }
16514: 
16515:     function buildTransportSweepQueue() {
16516:         const now = Date.now();
16517:         const queue = [];
16518:         const seen = new Set();
16519:         for (const marker of getMissionMarkerIndex().markers) {
16520:             const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
16521:             if (missionId === null || seen.has(missionId)) continue;
16522:             const personal = isPersonalMissionLayer(marker, missionId);
16523:             if (personal) continue;
16524:             const snapshot = liveMissionSnapshots.get(missionId) || missionSnapshotFromMarker(marker, now);
16525:             const requirement = transportRequirementFromSnapshot(snapshot);
16526:             const patientCount = Math.max(0, Number(snapshot?.patientsCount) || 0);
16527:             if (!requirement || requirement.type === 'prisoner') continue;
16528:             if (requirement.type !== 'patient' && patientCount <= 0) continue;
16529:             const count = Math.max(1, Math.min(99, Number(requirement.count) || patientCount || 1));
16530:             seen.add(missionId);
16531:             queue.push({
16532:                 missionId,
16533:                 caption: String(snapshot?.caption || `Alliance mission ${missionId}`),
16534:                 count,
16535:                 createdAt: Number(snapshot?.createdAt) || 0,
16536:                 requirement: requirement.label || 'Patient transport required'
16537:             });
16538:         }
16539:         queue.sort((a, b) => (a.createdAt || Number.MAX_SAFE_INTEGER) - (b.createdAt || Number.MAX_SAFE_INTEGER));
16540:         transportSweepRuntime.queue = queue;
16541:         transportSweepRuntime.scannedAt = now;
16542:         renderTransportSweepPanel();
16543:         return queue;
16544:     }
16545: 
16546: 
16547:     function transportSweepHudElements() {
16548:         try { return Array.from(document.querySelectorAll(`#${SCRIPT.transportSweepHudId}`)); }
16549:         catch (err) { return []; }
16550:     }
16551: 
16552:     function ensureTransportSweepHud() {
16553:         const matches = transportSweepHudElements();
16554:         let hud = matches.shift() || null;
16555:         for (const duplicate of matches) {
16556:             try { duplicate.remove(); } catch (err) {}
16557:         }
16558:         if (hud?.isConnected) return hud;
16559:         const mount = document.body || document.documentElement;
16560:         if (!mount) return null;
16561:         hud = document.createElement('section');
16562:         hud.id = SCRIPT.transportSweepHudId;
16563:         hud.className = 'mcms-transport-sweep-hud';
16564:         hud.setAttribute('role', 'status');
16565:         hud.setAttribute('aria-live', 'polite');
16566:         hud.setAttribute('aria-atomic', 'true');
16567:         mount.appendChild(hud);
16568:         return hud;
16569:     }
16570: 
16571:     function removeTransportSweepHud() {
16572:         runtimeClearTimeout(transportSweepRuntime.hudDismissTimer);
16573:         transportSweepRuntime.hudDismissTimer = null;
16574:         for (const hud of transportSweepHudElements()) {
16575:             try { hud.remove(); } catch (err) {}
16576:         }
16577:     }
16578: 
16579:     function scheduleTransportSweepHudDismiss(delay = 6500) {
16580:         runtimeClearTimeout(transportSweepRuntime.hudDismissTimer);
16581:         transportSweepRuntime.hudDismissTimer = runtimeSetTimeout(() => {
16582:             transportSweepRuntime.hudDismissTimer = null;
16583:             transportSweepRuntime.hudFinal = false;
16584:             removeTransportSweepHud();
16585:         }, Math.max(0, Number(delay) || 0));
16586:     }
16587: 
16588:     function transportSweepHudElapsed() {
16589:         const startedAt = Number(transportSweepRuntime.startedAt) || 0;
16590:         if (!startedAt) return '0:00';
16591:         const totalSeconds = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
16592:         const minutes = Math.floor(totalSeconds / 60);
16593:         return `${minutes}:${String(totalSeconds % 60).padStart(2, '0')}`;
16594:     }
16595: 
16596:     function renderTransportSweepHud() {
16597:         const sweep = transportSweepRuntime;
16598:         const visible = sweep.running || sweep.stopRequested || sweep.hudFinal;
16599:         if (!visible) {
16600:             removeTransportSweepHud();
16601:             return;
16602:         }
16603:         const hud = ensureTransportSweepHud();
16604:         if (!hud) return;
16605:         const total = Math.max(0, Number(sweep.missionTotal) || Number(sweep.queue?.length) || 0);
16606:         const index = total ? Math.min(total, Math.max(1, Number(sweep.missionIndex) || 1)) : 0;
16607:         const phase = sweep.hudFinal ? (sweep.statusLevel === 'error' ? 'Finished with errors' : 'Sweep complete')
16608:             : sweep.stopRequested ? 'Stopping'
16609:             : 'Sweep running';
16610:         const current = String(sweep.currentItem || '').trim();
16611:         const message = String(sweep.statusMessage || (sweep.running ? 'Preparing patient transport sweep' : phase)).trim();
16612:         hud.dataset.state = sweep.hudFinal ? (sweep.errors ? 'error' : 'complete') : sweep.stopRequested ? 'stopping' : 'running';
16613:         hud.innerHTML = `<div class="mcms-sweep-hud-head"><span><i></i>Patient Transport Sweep</span><b>${escapeHtml(phase)}</b></div><div class="mcms-sweep-hud-status">${escapeHtml(message)}</div>${current ? `<div class="mcms-sweep-hud-current">${escapeHtml(current)}</div>` : ''}<div class="mcms-sweep-hud-stats"><span><b>${index}/${total}</b><small>Missions</small></span><span class="mcms-sweep-hud-cleared"><b>${Math.max(0, Number(sweep.cleared) || 0)}</b><small>Patients cleared</small></span><span><b>${Math.max(0, Number(sweep.skipped) || 0)}</b><small>Skipped</small></span><span><b>${Math.max(0, Number(sweep.errors) || 0)}</b><small>Errors</small></span></div><div class="mcms-sweep-hud-foot"><span>${escapeHtml(transportSweepHudElapsed())} elapsed</span><span>${Math.max(0, Number(sweep.processed) || 0)} processed</span></div>`;
16614:     }
16615: 
16616:     runtimeOnCleanup(removeTransportSweepHud);
16617: 
16618:     function renderTransportSweepPanel() {
16619:         renderTransportSweepHud();
16620:         const host = document.querySelector(`#${SCRIPT.panelId} [data-transport-sweep]`);
16621:         if (!host) return;
16622:         const runtime = transportSweepRuntime;
16623:         const queue = runtime.queue || [];
16624:         const currentId = normaliseMissionId(runtime.currentMissionId);
16625:         const status = runtime.running ? 'RUNNING' : runtime.stopRequested ? 'STOPPING' : queue.length ? 'READY' : 'IDLE';
16626:         const list = queue.length ? queue.map((item, index) => {
16627:             const current = currentId !== null && normaliseMissionId(item.missionId) === currentId;
16628:             return `<div class="mcms-sweep-entry ${current ? 'mcms-current' : ''}"><div><span class="mcms-sweep-title">${escapeHtml(`${index + 1}. ${item.caption}`)}</span><span class="mcms-sweep-meta">Mission ${escapeHtml(item.missionId)} · ${escapeHtml(item.requirement)}</span></div><span class="mcms-sweep-count">${escapeHtml(item.count)} req</span></div>`;
16629:         }).join('') : `<div class="mcms-empty-state">Scan to find alliance missions currently reporting patient transport requirements.</div>`;
16630:         const logs = runtime.log.length ? runtime.log.map(entry => {
16631:             const stamp = new Date(entry.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
16632:             return `<div>${escapeHtml(stamp)} · ${escapeHtml(entry.message)}</div>`;
16633:         }).join('') : '<div>No sweep activity yet.</div>';
16634:         const html = `<div class="mcms-sweep-card"><div class="mcms-sweep-head"><span>Patient Transport Sweep</span><span class="mcms-sweep-state ${runtime.running ? 'mcms-running' : ''}">${status}</span></div><div class="mcms-sweep-stats"><div class="mcms-sweep-stat"><b>${queue.length}</b><span>Missions</span></div><div class="mcms-sweep-stat"><b>${runtime.cleared}</b><span>Cleared</span></div><div class="mcms-sweep-stat"><b>${runtime.skipped}</b><span>Skipped</span></div><div class="mcms-sweep-stat"><b>${runtime.errors}</b><span>Errors</span></div></div><div class="mcms-sweep-queue">${list}</div><div class="mcms-sweep-log">${logs}</div></div>`;
16635:         setInnerHtmlIfChanged(host, html);
16636:         const start = document.querySelector(`#${SCRIPT.panelId} [data-action="start-transport-sweep"]`);
16637:         const stop = document.querySelector(`#${SCRIPT.panelId} [data-action="stop-transport-sweep"]`);
16638:         const scan = document.querySelector(`#${SCRIPT.panelId} [data-action="scan-transport-sweep"]`);
16639:         if (start) start.disabled = runtime.running;
16640:         if (stop) stop.disabled = !runtime.running;
16641:         if (scan) scan.disabled = runtime.running;
16642:     }
16643: 
16644:     function transportSweepVehicleIdFromHref(href) {
16645:         let pathname = String(href || '').trim();
16646:         try { pathname = new URL(pathname, document.baseURI || pageWindow.location.href).pathname; } catch (err) {}
16647:         const match = pathname.match(/^\/vehicles\/(\d+)(?:\/|$)/);
16648:         return match ? match[1] : null;
16649:     }
16650: 
16651: 
16652:     function transportSweepReleaseVehicleIdFromHref(href) {
16653:         let pathname = String(href || '').trim();
16654:         try { pathname = new URL(pathname, document.baseURI || pageWindow.location.href).pathname; } catch (err) {}
16655:         const match = pathname.match(/^\/vehicles\/(\d+)\/patient\/-1\/?$/);
16656:         return match ? match[1] : null;
16657:     }
16658: 
16659:     function transportSweepOwnerProfileId(row) {
16660:         if (!row?.querySelector) return null;
16661:         const ownerLink = row.querySelector('td.hidden-xs a[href*="/profile/"], small.visible-xs a[href*="/profile/"]');
16662:         const href = String(ownerLink?.getAttribute?.('href') || '');
16663:         const match = href.match(/\/profile\/(\d+)(?:\/|$)/);
16664:         return match ? match[1] : null;
16665:     }
16666: 
16667:     function transportSweepAnchorUsable(anchor) {
16668:         if (!anchor || !anchor.isConnected || anchor.closest?.(`#${SCRIPT.panelId}`)) return false;
16669:         try {
16670:             const view = anchor.ownerDocument?.defaultView || window;
16671:             let node = anchor;
16672:             for (let depth = 0; depth < 7 && node; depth += 1, node = node.parentElement) {
16673:                 const style = view.getComputedStyle(node);
16674:                 if (style.display === 'none' || style.visibility === 'hidden') continue;
16675:                 const rect = node.getBoundingClientRect();
16676:                 if (rect.width > 0 && rect.height > 0) return true;
16677:             }
16678:         } catch (err) {}
16679:         return false;
16680:     }
16681: 
16682:     function transportSweepDocumentContexts() {
16683:         const contexts = [];
16684:         const seenDocuments = new Set();
16685:         const visit = (doc, label = 'top') => {
16686:             if (!doc || seenDocuments.has(doc)) return;
16687:             seenDocuments.add(doc);
16688:             contexts.push({ doc, label });
16689:             let frames = [];
16690:             try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
16691:             frames.forEach((frame, index) => {
16692:                 try {
16693:                     const child = frame.contentDocument || frame.contentWindow?.document;
16694:                     if (child) visit(child, `${label}/frame${index + 1}`);
16695:                 } catch (err) {
16696:                     // Cross-origin frames are intentionally ignored.
16697:                 }
16698:             });
16699:         };
16700:         visit(document);
16701:         return contexts;
16702:     }
16703: 
16704:     function transportSweepVehicleAnchorsWithin(root = null, requireUsable = true) {
16705:         const scope = root && (root.isConnected || root.nodeType === 9) ? root : document;
16706:         let anchors = [];
16707:         try { anchors = Array.from(scope.querySelectorAll('a[href*="/vehicles/"]')); } catch (err) {}
16708:         return anchors.filter(anchor => {
16709:             if (!transportSweepVehicleIdFromHref(anchor.getAttribute('href'))) return false;
16710:             return !requireUsable || transportSweepAnchorUsable(anchor);
16711:         });
16712:     }
16713: 
16714:     function transportSweepVisibleVehicleAnchors() {
16715:         const anchors = [];
16716:         const seen = new Set();
16717:         for (const context of transportSweepDocumentContexts()) {
16718:             for (const anchor of transportSweepVehicleAnchorsWithin(context.doc, true)) {
16719:                 if (seen.has(anchor)) continue;
16720:                 seen.add(anchor);
16721:                 anchors.push(anchor);
16722:             }
16723:         }
16724:         return anchors;
16725:     }
16726: 
16727:     function transportSweepVisibleWindowRoots() {
16728:         const selectors = [
16729:             '#lightbox_box .lightbox_content', '#lightbox_box', '#lightbox', '.lightbox_content',
16730:             '[id*="lightbox"]', '.lightbox', '.modal.show .modal-content', '.modal.in .modal-content',
16731:             '.modal.show', '.modal.in', '[role="dialog"]', '.ui-dialog-content', '.ui-dialog'
16732:         ];
16733:         const roots = [];
16734:         const seen = new Set();
16735:         for (const context of transportSweepDocumentContexts()) {
16736:             for (const selector of selectors) {
16737:                 let matches = [];
16738:                 try { matches = Array.from(context.doc.querySelectorAll(selector)); } catch (err) {}
16739:                 for (const root of matches) {
16740:                     if (!root || seen.has(root) || !transportSweepElementVisible(root)) continue;
16741:                     if (root.closest?.(`#${SCRIPT.panelId}`)) continue;
16742:                     seen.add(root);
16743:                     roots.push(root);
16744:                 }
16745:             }
16746:             if (context.doc !== document) {
16747:                 const body = context.doc.body;
16748:                 if (body && !seen.has(body) && transportSweepElementVisible(body) && transportSweepVehicleAnchorsWithin(body, true).length) {
16749:                     seen.add(body);
16750:                     roots.push(body);
16751:                 }
16752:             }
16753:         }
16754:         return roots;
16755:     }
16756: 
16757:     function transportSweepRootScore(root, missionId = null) {
16758:         if (!root || !root.isConnected) return -1;
16759:         const anchors = transportSweepVehicleAnchorsWithin(root);
16760:         if (!anchors.length) return -1;
16761:         let score = anchors.length * 10;
16762:         const text = String(root.textContent || '').toLowerCase();
16763:         if (/mission|incident|einsatz|call/.test(text)) score += 15;
16764:         if (/patient|transport|ambulance|discharge/.test(text)) score += 30;
16765:         if (missionId !== null) {
16766:             try {
16767:                 if (root.querySelector(`a[href*="/missions/${missionId}"]`)) score += 80;
16768:             } catch (err) {}
16769:         }
16770:         const rect = root.getBoundingClientRect();
16771:         score += Math.min(30, Math.round((rect.width * rect.height) / 50000));
16772:         return score;
16773:     }
16774: 
16775:     function transportSweepFindMissionWindowRoot(missionId = null) {
16776:         const roots = transportSweepVisibleWindowRoots();
16777:         let best = null;
16778:         let bestScore = -1;
16779:         for (const root of roots) {
16780:             const score = transportSweepRootScore(root, missionId);
16781:             if (score > bestScore) {
16782:                 best = root;
16783:                 bestScore = score;
16784:             }
16785:         }
16786:         if (best) return best;
16787: 
16788:         // Fallback for MissionChief builds that render lightbox content without a stable wrapper.
16789:         const baseline = transportSweepRuntime.missionAnchorBaseline;
16790:         const anchor = transportSweepVisibleVehicleAnchors().find(item => !(baseline instanceof Set) || !baseline.has(item));
16791:         if (!anchor) return null;
16792:         return anchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || anchor.ownerDocument?.body || anchor.parentElement;
16793:     }
16794: 
16795:     function transportSweepAnchorBelongsToMissionWindow(anchor) {
16796:         if (!anchor || !transportSweepAnchorUsable(anchor)) return false;
16797:         const root = transportSweepRuntime.missionWindowRoot;
16798:         if (root?.isConnected && root.contains(anchor)) return true;
16799:         const baseline = transportSweepRuntime.missionAnchorBaseline;
16800:         if (baseline instanceof Set && !baseline.has(anchor)) return true;
16801:         return transportSweepVisibleWindowRoots().some(windowRoot => windowRoot.contains(anchor));
16802:     }
16803: 
16804:     function transportSweepOwnVehicleIdSet() {
16805:         if (transportSweepRuntime.ownVehicleIds instanceof Set && transportSweepRuntime.ownVehicleIds.size) {
16806:             return new Set(Array.from(transportSweepRuntime.ownVehicleIds, id => String(id)));
16807:         }
16808:         const ids = new Set(Array.from(personalVehicleApiCache.keys(), id => String(id)));
16809:         for (const vehicle of getPersonalVehicleRecords()) {
16810:             const id = vehicleRecordId(vehicle);
16811:             if (id !== null) ids.add(String(id));
16812:         }
16813:         transportSweepRuntime.ownVehicleIds = ids;
16814:         return ids;
16815:     }
16816: 
16817:     function collectTransportSweepStaticCandidates(anchors, source = 'mission HTML', preserveAnchors = false) {
16818:         const unique = new Map();
16819:         const ownIds = transportSweepOwnVehicleIdSet();
16820:         let rejectedOwn = 0;
16821:         let allianceLinks = 0;
16822:         let rejectedNotFms5 = 0;
16823:         let rejectedNotPatient = 0;
16824: 
16825:         for (const anchor of Array.from(anchors || [])) {
16826:             const href = String(anchor.getAttribute?.('href') || '').trim();
16827:             const vehicleId = transportSweepVehicleIdFromHref(href);
16828:             if (!vehicleId) continue;
16829: 
16830:             const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, li, [id^="vehicle_row_"], [class*="vehicle_row"]');
16831:             const fms5 = row?.querySelector?.('.building_list_fms_5');
16832:             if (!row || !fms5) {
16833:                 rejectedNotFms5 += 1;
16834:                 continue;
16835:             }
16836: 
16837:             if (ownIds.has(String(vehicleId))) {
16838:                 rejectedOwn += 1;
16839:                 continue;
16840:             }
16841: 
16842:             allianceLinks += 1;
16843:             const vehicleTypeId = String(anchor.getAttribute?.('vehicle_type_id') || '');
16844:             const label = String(anchor.textContent || 'Alliance vehicle').trim() || 'Alliance vehicle';
16845:             const rowText = String(row.textContent || '').replace(/\s+/g, ' ').trim();
16846:             const isPatientVehicle = vehicleTypeId === '5' || /ambulance|patient|paramedic|rettungs|krankentransport|rtw\b/i.test(`${label} ${rowText}`);
16847:             if (!isPatientVehicle) {
16848:                 rejectedNotPatient += 1;
16849:                 continue;
16850:             }
16851: 
16852:             const normalisedHref = `/vehicles/${vehicleId}`;
16853:             const candidate = {
16854:                 href: normalisedHref,
16855:                 vehicleId,
16856:                 label,
16857:                 vehicleTypeId,
16858:                 score: 500,
16859:                 anchor: preserveAnchors ? anchor : null,
16860:                 row: preserveAnchors ? row : null,
16861:                 source,
16862:                 rowText
16863:             };
16864:             if (!unique.has(normalisedHref)) unique.set(normalisedHref, candidate);
16865:         }
16866: 
16867:         return {
16868:             candidates: Array.from(unique.values())
16869:                 .sort((a, b) => a.label.localeCompare(b.label) || Number(a.vehicleId) - Number(b.vehicleId))
16870:                 .slice(0, TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION),
16871:             stats: {
16872:                 totalLinks: Array.from(anchors || []).length,
16873:                 allianceLinks,
16874:                 rejectedOwn,
16875:                 rejectedNotFms5,
16876:                 rejectedNotPatient,
16877:                 candidates: unique.size,
16878:                 source
16879:             }
16880:         };
16881:     }
16882: 
16883:     async function transportSweepFetchMissionCandidates(missionId) {
16884:         const id = normaliseMissionId(missionId);
16885:         if (id === null || transportSweepRuntime.stopRequested) return null;
16886:         const requestModes = [
16887:             { headers: { 'X-Requested-With': 'XMLHttpRequest', Accept: 'text/html, */*;q=0.8' } },
16888:             { headers: { Accept: 'text/html,application/xhtml+xml' } }
16889:         ];
16890:         let bestResult = null;
16891:         for (const mode of requestModes) {
16892:             if (transportSweepRuntime.stopRequested) return null;
16893:             try {
16894:                 const response = await runtimeFetch(`/missions/${id}`, {
16895:                     method: 'GET',
16896:                     credentials: 'same-origin',
16897:                     cache: 'no-store',
16898:                     headers: mode.headers
16899:                 });
16900:                 if (!response.ok) continue;
16901:                 const html = await response.text();
16902:                 if (!html || html.length < 100) continue;
16903:                 const doc = new DOMParser().parseFromString(html, 'text/html');
16904:                 const anchors = Array.from(doc.querySelectorAll('a[href*="/vehicles/"]'))
16905:                     .filter(anchor => transportSweepVehicleIdFromHref(anchor.getAttribute('href')));
16906:                 if (!anchors.length) continue;
16907:                 const result = { ...collectTransportSweepStaticCandidates(anchors, 'mission HTML'), htmlLength: html.length };
16908:                 if (!bestResult || result.stats.totalLinks > bestResult.stats.totalLinks) bestResult = result;
16909:                 if (result.candidates.length) return result;
16910:             } catch (err) {
16911:                 // Try the next request mode.
16912:             }
16913:         }
16914:         return bestResult;
16915:     }
16916: 
16917:     async function collectTransportSweepVehicleCandidatesForMission(missionId) {
16918:         const domCandidates = collectTransportSweepVehicleCandidates();
16919:         const domStats = { ...(transportSweepRuntime.lastCandidateStats || {}) };
16920:         if (domCandidates.length) return domCandidates;
16921: 
16922:         const fetched = await transportSweepFetchMissionCandidates(missionId);
16923:         if (fetched) {
16924:             transportSweepRuntime.rejectedOwn = fetched.stats.rejectedOwn || 0;
16925:             transportSweepRuntime.lastCandidateStats = fetched.stats;
16926:             if (fetched.candidates?.length) {
16927:                 transportSweepLog(`Recovered ${fetched.stats.totalLinks} vehicle links from mission HTML`);
16928:                 return fetched.candidates;
16929:             }
16930:         }
16931: 
16932:         if (!fetched) transportSweepRuntime.lastCandidateStats = domStats;
16933:         return [];
16934:     }
16935: 
16936:     function collectTransportSweepVehicleCandidates() {
16937:         const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : null;
16938:         let anchors = root ? transportSweepVehicleAnchorsWithin(root) : [];
16939:         if (!anchors.length) anchors = transportSweepVisibleVehicleAnchors().filter(anchor => transportSweepAnchorBelongsToMissionWindow(anchor));
16940: 
16941:         const result = collectTransportSweepStaticCandidates(anchors, 'mission window', true);
16942:         transportSweepRuntime.rejectedOwn = result.stats.rejectedOwn || 0;
16943:         transportSweepRuntime.lastCandidateStats = result.stats;
16944:         return result.candidates;
16945:     }
16946: 
16947: 
16948:     function collectTransportSweepLssmCandidates(excludedVehicleIds = null) {
16949:         const excluded = excludedVehicleIds instanceof Set ? excludedVehicleIds : new Set();
16950:         const ownIds = transportSweepOwnVehicleIdSet();
16951:         const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : null;
16952:         const anchors = [];
16953:         const seenAnchors = new Set();
16954:         const collectFrom = scope => {
16955:             let matches = [];
16956:             try { matches = Array.from(scope?.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || []); } catch (err) {}
16957:             for (const anchor of matches) {
16958:                 if (seenAnchors.has(anchor)) continue;
16959:                 seenAnchors.add(anchor);
16960:                 anchors.push(anchor);
16961:             }
16962:         };
16963:         if (root) collectFrom(root);
16964:         if (!anchors.length) {
16965:             for (const context of transportSweepDocumentContexts()) collectFrom(context.doc);
16966:         }
16967: 
16968:         const unique = new Map();
16969:         let rejectedOwn = 0;
16970:         let rejectedAmbiguousOwner = 0;
16971:         let rejectedNotFms5 = 0;
16972:         for (const anchor of anchors) {
16973:             if (!transportSweepAnchorUsable(anchor)) continue;
16974:             const actionHref = String(anchor.getAttribute?.('href') || '').trim();
16975:             const vehicleId = transportSweepReleaseVehicleIdFromHref(actionHref);
16976:             if (!vehicleId || excluded.has(String(vehicleId))) continue;
16977:             const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, [id^="vehicle_row_"]');
16978:             if (!row?.querySelector?.('.building_list_fms_5')) {
16979:                 rejectedNotFms5 += 1;
16980:                 continue;
16981:             }
16982:             if (ownIds.has(String(vehicleId))) {
16983:                 rejectedOwn += 1;
16984:                 continue;
16985:             }
16986:             const ownerProfileId = transportSweepOwnerProfileId(row);
16987:             if (!ownerProfileId) {
16988:                 rejectedAmbiguousOwner += 1;
16989:                 continue;
16990:             }
16991:             const vehicleLink = Array.from(row.querySelectorAll?.('a[href*="/vehicles/"]') || [])
16992:                 .find(item => transportSweepVehicleIdFromHref(item.getAttribute?.('href')) === String(vehicleId));
16993:             const ownerLink = row.querySelector('td.hidden-xs a[href*="/profile/"], small.visible-xs a[href*="/profile/"]');
16994:             const label = String(vehicleLink?.textContent || `Alliance ambulance ${vehicleId}`).trim() || `Alliance ambulance ${vehicleId}`;
16995:             const owner = String(ownerLink?.textContent || `profile ${ownerProfileId}`).trim() || `profile ${ownerProfileId}`;
16996:             const normalisedActionHref = `/vehicles/${vehicleId}/patient/-1`;
16997:             if (!unique.has(normalisedActionHref)) {
16998:                 unique.set(normalisedActionHref, {
16999:                     actionHref: normalisedActionHref,
17000:                     vehicleId: String(vehicleId),
17001:                     ownerProfileId,
17002:                     owner,
17003:                     label,
17004:                     anchor,
17005:                     row,
17006:                     source: 'LSSM mission release control'
17007:                 });
17008:             }
17009:         }
17010: 
17011:         const candidates = Array.from(unique.values())
17012:             .sort((a, b) => a.label.localeCompare(b.label) || Number(a.vehicleId) - Number(b.vehicleId))
17013:             .slice(0, TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION);
17014:         transportSweepRuntime.rejectedOwn = rejectedOwn;
17015:         transportSweepRuntime.lastCandidateStats = {
17016:             source: 'LSSM mission release controls',
17017:             totalLinks: anchors.length,
17018:             candidates: candidates.length,
17019:             rejectedOwn,
17020:             rejectedAmbiguousOwner,
17021:             rejectedNotFms5
17022:         };
17023:         return candidates;
17024:     }
17025: 
17026:     async function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000) {
17027:         const first = await transportSweepWaitFor(() => {
17028:             const candidates = collectTransportSweepLssmCandidates(excludedVehicleIds);
17029:             return candidates.length ? candidates : null;
17030:         }, timeoutMs, 180);
17031:         if (!first?.length || transportSweepRuntime.stopRequested) return [];
17032:         await transportSweepSleep(1200);
17033:         return collectTransportSweepLssmCandidates(excludedVehicleIds);
17034:     }
17035: 
17036:     function transportSweepReleaseConfirmationVisible() {
17037:         const text = transportSweepVisibleWindowRoots()
17038:             .map(root => String(root.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase())
17039:             .join(' | ');
17040:         return /released the patient|patient (?:is not|isn['’]t) transported|patient.*released|patient.*discharged/.test(text);
17041:     }
17042: 
17043:     async function activateTransportSweepLssmRelease(candidate) {
17044:         if (!candidate?.actionHref || transportSweepRuntime.stopRequested) return false;
17045:         let anchor = candidate.anchor;
17046:         if (!anchor?.isConnected) {
17047:             const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : document;
17048:             anchor = Array.from(root.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || [])
17049:                 .find(item => transportSweepReleaseVehicleIdFromHref(item.getAttribute?.('href')) === String(candidate.vehicleId));
17050:         }
17051:         if (!anchor?.isConnected || !transportSweepAnchorUsable(anchor)) return false;
17052:         const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, [id^="vehicle_row_"]');
17053:         const rowId = String(row?.id || `vehicle_row_${candidate.vehicleId}`);
17054:         const ownerDocument = anchor.ownerDocument || document;
17055:         const clickedAt = Date.now();
17056:         anchor.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
17057:         anchor.click();
17058:         return Boolean(await transportSweepWaitFor(() => {
17059:             if (transportSweepReleaseConfirmationVisible()) return true;
17060:             if (Date.now() - clickedAt < 900) return null;
17061:             const liveRow = ownerDocument.getElementById?.(rowId) || null;
17062:             if (!liveRow) return null;
17063:             const liveAction = Array.from(liveRow.querySelectorAll?.('a[href*="/vehicles/"][href*="/patient/-1"]') || [])
17064:                 .find(item => transportSweepReleaseVehicleIdFromHref(item.getAttribute?.('href')) === String(candidate.vehicleId));
17065:             const stillFms5 = Boolean(liveRow.querySelector?.('.building_list_fms_5'));
17066:             const stillPatient = /\bpatient\s*:/i.test(String(liveRow.textContent || ''));
17067:             return !liveAction && (!stillFms5 || !stillPatient) ? true : null;
17068:         }, 10000, 140));
17069:     }
17070: 
17071:     function transportSweepVisibleDischargeButtons() {
17072:         const buttons = [];
17073:         const seen = new Set();
17074:         for (const context of transportSweepDocumentContexts()) {
17075:             let matches = [];
17076:             try { matches = Array.from(context.doc.querySelectorAll('button')); } catch (err) {}
17077:             for (const button of matches) {
17078:                 if (seen.has(button) || !transportSweepElementVisible(button) || button.disabled) continue;
17079:                 if (String(button.textContent || '').trim().toLowerCase() !== 'discharge patient') continue;
17080:                 seen.add(button);
17081:                 buttons.push(button);
17082:             }
17083:         }
17084:         return buttons;
17085:     }
17086: 
17087:     function findVisibleDischargePatientButton(excludedButtons = null) {
17088:         const excluded = excludedButtons instanceof Set ? excludedButtons : null;
17089:         return transportSweepVisibleDischargeButtons().find(button => !excluded || !excluded.has(button)) || null;
17090:     }
17091: 
17092:     function transportSweepTopLevelWindowRoots() {
17093:         const visible = transportSweepVisibleWindowRoots();
17094:         return visible.filter(root => !visible.some(other => other !== root && other.contains?.(root)));
17095:     }
17096: 
17097:     const TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR = [
17098:         '#lightbox', '#lightbox_box', '.lightbox', '[id*="lightbox"]',
17099:         '.lightbox_overlay', '.lightbox-overlay', '#lightbox_overlay', '#lightbox_backdrop', '.lightbox-backdrop',
17100:         '.modal.show', '.modal.in', '.modal-backdrop.show', '.modal-backdrop.in',
17101:         '[role="dialog"]', '.ui-dialog', '.ui-widget-overlay'
17102:     ].join(', ');
17103: 
17104:     function transportSweepNativeWindowLayers() {
17105:         const layers = [];
17106:         const seen = new Set();
17107:         for (const context of transportSweepDocumentContexts()) {
17108:             let matches = [];
17109:             try { matches = Array.from(context.doc.querySelectorAll(TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR)); } catch (err) {}
17110:             for (const layer of matches) {
17111:                 if (!layer || seen.has(layer) || !layer.isConnected || layer.closest?.(`#${SCRIPT.panelId}`)) continue;
17112:                 seen.add(layer);
17113:                 layers.push(layer);
17114:             }
17115:         }
17116:         return layers;
17117:     }
17118: 
17119:     function transportSweepWindowLayerChain(root) {
17120:         const chain = [];
17121:         const seen = new Set();
17122:         const collect = start => {
17123:             let node = start;
17124:             while (node?.nodeType === 1) {
17125:                 if (!seen.has(node) && node.matches?.(TRANSPORT_SWEEP_NATIVE_LAYER_SELECTOR)) {
17126:                     seen.add(node);
17127:                     chain.push(node);
17128:                 }
17129:                 node = node.parentElement;
17130:             }
17131:         };
17132:         collect(root);
17133:         try { collect(root?.ownerDocument?.defaultView?.frameElement); } catch (err) {}
17134:         return chain;
17135:     }
17136: 
17137:     function transportSweepOverlayLayer(layer) {
17138:         if (!layer?.matches) return false;
17139:         return layer.matches('.modal-backdrop, .ui-widget-overlay, .lightbox_overlay, .lightbox-overlay, #lightbox_overlay, #lightbox_backdrop, .lightbox-backdrop');
17140:     }
17141: 
17142:     function transportSweepOutermostLayer(layers) {
17143:         const candidates = Array.from(layers || []).filter(layer => layer?.isConnected && !transportSweepOverlayLayer(layer));
17144:         return candidates.find(layer => !candidates.some(other => other !== layer && other.contains?.(layer))) || candidates[0] || null;
17145:     }
17146: 
17147:     function transportSweepClaimWindow(root, beforeLayers = null) {
17148:         if (!root?.isConnected) return null;
17149:         const baseline = beforeLayers instanceof Set ? beforeLayers : new Set();
17150:         const anchor = (() => {
17151:             try { return root.ownerDocument?.defaultView?.frameElement || root; } catch (err) { return root; }
17152:         })();
17153:         const chain = transportSweepWindowLayerChain(root);
17154:         const created = transportSweepNativeWindowLayers().filter(layer => {
17155:             if (baseline.has(layer)) return false;
17156:             if (layer === anchor || layer.contains?.(anchor) || anchor.contains?.(layer)) return true;
17157:             return layer.ownerDocument === anchor.ownerDocument && transportSweepOverlayLayer(layer);
17158:         });
17159:         const owned = new Set([...created, ...chain.filter(layer => !baseline.has(layer))]);
17160:         for (const layer of owned) {
17161:             try { layer.dataset.mcmsTransportSweepOwned = '1'; } catch (err) {}
17162:         }
17163:         transportSweepRuntime.ownedWindowLayers = owned;
17164:         transportSweepRuntime.activeWindowCreatedLayer = owned.size > 0;
17165:         transportSweepRuntime.activeWindowRoot = transportSweepOutermostLayer(owned) || transportSweepOutermostLayer(chain) || root;
17166:         return transportSweepRuntime.activeWindowRoot;
17167:     }
17168: 
17169:     function transportSweepWindowCloseControl(root) {
17170:         if (!root?.querySelectorAll) return null;
17171:         const selectors = [
17172:             '#lightbox_close', '.lightbox-close', '.lightbox_close',
17173:             '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]',
17174:             'button.close', 'a.close', 'button[aria-label="Close"]', 'a[aria-label="Close"]',
17175:             'button[title="Close"]', 'a[title="Close"]'
17176:         ];
17177:         for (const selector of selectors) {
17178:             const control = Array.from(root.querySelectorAll(selector)).find(transportSweepElementVisible);
17179:             if (control) return control;
17180:         }
17181:         return null;
17182:     }
17183: 
17184:     async function closeTransportSweepWindows(reason = 'navigation') {
17185:         const target = transportSweepRuntime.activeWindowRoot;
17186:         const ownedLayers = Array.from(transportSweepRuntime.ownedWindowLayers || []).filter(layer => layer?.isConnected);
17187:         transportSweepRuntime.missionWindowRoot = null;
17188:         if ((!target || !target.isConnected || !transportSweepElementVisible(target)) && !ownedLayers.length) {
17189:             transportSweepRuntime.activeWindowRoot = null;
17190:             transportSweepRuntime.ownedWindowLayers = new Set();
17191:             transportSweepRuntime.activeWindowCreatedLayer = false;
17192:             return true;
17193:         }
17194: 
17195:         const waitUntilClosed = timeoutMs => transportSweepWaitFor(
17196:             () => !target?.isConnected || !transportSweepElementVisible(target) ? true : null,
17197:             timeoutMs,
17198:             100
17199:         );
17200: 
17201:         let closed = !target?.isConnected || !transportSweepElementVisible(target);
17202:         if (!closed) {
17203:             const closeControl = transportSweepWindowCloseControl(target);
17204:             if (closeControl) {
17205:                 try {
17206:                     closeControl.click();
17207:                     closed = Boolean(await waitUntilClosed(1200));
17208:                 } catch (err) {}
17209:             }
17210:         }
17211: 
17212:         if (!closed && typeof pageWindow.lightboxClose === 'function') {
17213:             try {
17214:                 pageWindow.lightboxClose();
17215:                 closed = Boolean(await waitUntilClosed(1400));
17216:             } catch (err) {}
17217:         }
17218: 
17219:         if (transportSweepRuntime.activeWindowCreatedLayer) {
17220:             const removable = Array.from(new Set(ownedLayers.filter(layer => layer?.isConnected)));
17221:             removable.sort((a, b) => a.contains?.(b) ? -1 : b.contains?.(a) ? 1 : 0);
17222:             for (const layer of removable) {
17223:                 if (!layer?.isConnected) continue;
17224:                 try {
17225:                     layer.querySelectorAll?.('iframe, frame').forEach(frame => {
17226:                         try { frame.src = 'about:blank'; } catch (err) {}
17227:                     });
17228:                     layer.remove();
17229:                 } catch (err) {}
17230:             }
17231:             closed = !target?.isConnected || !transportSweepElementVisible(target);
17232:         }
17233: 
17234:         const ownedStillConnected = ownedLayers.some(layer => layer?.isConnected && transportSweepElementVisible(layer));
17235:         if (!closed || ownedStillConnected) {
17236:             transportSweepLog(`MissionChief did not remove the sweep-owned window before ${reason}`, 'error');
17237:             return false;
17238:         }
17239: 
17240:         transportSweepRuntime.activeWindowRoot = null;
17241:         transportSweepRuntime.ownedWindowLayers = new Set();
17242:         transportSweepRuntime.activeWindowCreatedLayer = false;
17243:         await transportSweepSleep(80);
17244:         return true;
17245:     }
17246: 
17247:     async function openTransportSweepPath(path, mode) {
17248:         if (transportSweepRuntime.stopRequested) return false;
17249:         if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');
17250:         const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle');
17251:         if (!closed || transportSweepRuntime.stopRequested) return false;
17252: 
17253:         const beforeRoots = transportSweepVisibleWindowRoots();
17254:         const beforeRootText = new Map(beforeRoots.map(root => [root, String(root.textContent || '').trim()]));
17255:         const beforeLayers = new Set(transportSweepNativeWindowLayers());
17256: 
17257:         if (mode === 'mission') {
17258:             transportSweepRuntime.missionAnchorBaseline = new Set(transportSweepVisibleVehicleAnchors());
17259:             transportSweepRuntime.rejectedOwn = 0;
17260:             transportSweepRuntime.missionWindowRoot = null;
17261:             const missionId = normaliseMissionId(String(path || '').match(/\/missions\/(\d+)/)?.[1]);
17262:             pageWindow.lightboxOpen(path);
17263:             await transportSweepWaitFor(() => {
17264:                 const root = transportSweepFindMissionWindowRoot(missionId);
17265:                 if (root) {
17266:                     const anchors = transportSweepVehicleAnchorsWithin(root);
17267:                     const afterText = String(root.textContent || '').trim();
17268:                     const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root);
17269:                     if (anchors.length || (afterText && changed)) {
17270:                         transportSweepRuntime.missionWindowRoot = root;
17271:                         transportSweepClaimWindow(root, beforeLayers);
17272:                         return { root, anchors };
17273:                     }
17274:                 }
17275:                 const newAnchor = transportSweepVisibleVehicleAnchors().find(anchor => !transportSweepRuntime.missionAnchorBaseline.has(anchor));
17276:                 if (newAnchor) {
17277:                     transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.parentElement;
17278:                     transportSweepClaimWindow(transportSweepRuntime.missionWindowRoot, beforeLayers);
17279:                     return { root: transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
17280:                 }
17281:                 return null;
17282:             }, 4200, 120);
17283:             return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
17284:         }
17285: 
17286:         pageWindow.lightboxOpen(path);
17287:         const vehicleWindow = await transportSweepWaitFor(() => {
17288:             const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
17289:             if (button) {
17290:                 const root = button.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || button.parentElement;
17291:                 return { root };
17292:             }
17293:             const root = transportSweepVisibleWindowRoots().find(candidate => {
17294:                 const text = String(candidate.textContent || '').trim();
17295:                 return !beforeRootText.has(candidate) || text !== beforeRootText.get(candidate);
17296:             });
17297:             return root ? { root } : null;
17298:         }, 4200, 120);
17299:         transportSweepClaimWindow(vehicleWindow?.root, beforeLayers);
17300:         return !transportSweepRuntime.stopRequested && Boolean(transportSweepRuntime.activeWindowRoot);
17301:     }
17302: 
17303:     async function openTransportSweepVehicle(candidate) {
17304:         if (transportSweepRuntime.stopRequested || !candidate?.href) return null;
17305:         transportSweepRuntime.vehicleButtonBaseline = new Set(transportSweepVisibleDischargeButtons());
17306:         const opened = await openTransportSweepPath(candidate.href, 'vehicle');
17307:         if (!opened || transportSweepRuntime.stopRequested) return null;
17308: 
17309:         const openedAt = Date.now();
17310:         return await transportSweepWaitFor(() => {
17311:             const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
17312:             if (button) return { opened: true, button };
17313:             const roots = transportSweepTopLevelWindowRoots();
17314:             if (roots.length && Date.now() - openedAt > 350) return { opened: true, button: null };
17315:             return null;
17316:         }, 7500, 140);
17317:     }
17318: 
17319:     async function processTransportSweepMission(item, remainingAllowance) {
17320:         const missionId = normaliseMissionId(item?.missionId);
17321:         if (missionId === null || remainingAllowance <= 0) return 0;
17322: 
17323:         transportSweepRuntime.currentMissionId = missionId;
17324:         transportSweepRuntime.currentItem = String(item?.caption || `Mission ${missionId}`);
17325:         renderTransportSweepPanel();
17326: 
17327:         const attemptedVehicleIds = new Set();
17328:         let clearedHere = 0;
17329:         let lssmSeen = false;
17330:         let fallbackMode = false;
17331:         let fallbackLogged = false;
17332:         let initialScanLogged = false;
17333:         let missionHadCandidates = false;
17334: 
17335:         transportSweepLog(`Opening ${item.caption}`);
17336:         let missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
17337:         if (!missionOpen || transportSweepRuntime.stopRequested) {
17338:             if (!transportSweepRuntime.stopRequested) {
17339:                 transportSweepRuntime.skipped += 1;
17340:                 transportSweepLog(`Skipped ${item.caption} because its mission window did not become available`, 'warn');
17341:             }
17342:             return 0;
17343:         }
17344: 
17345:         while (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
17346:             if (!fallbackMode) {
17347:                 const lssmCandidates = await waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000);
17348:                 if (transportSweepRuntime.stopRequested) break;
17349:                 const lssmCandidate = lssmCandidates.find(entry => !attemptedVehicleIds.has(String(entry.vehicleId)));
17350:                 if (lssmCandidate) {
17351:                     lssmSeen = true;
17352:                     missionHadCandidates = true;
17353:                     attemptedVehicleIds.add(String(lssmCandidate.vehicleId));
17354:                     transportSweepRuntime.currentVehicleHref = lssmCandidate.actionHref;
17355:                     transportSweepRuntime.currentItem = `${lssmCandidate.label} · ${lssmCandidate.owner}`;
17356:                     renderTransportSweepPanel();
17357:                     transportSweepLog(`Releasing ${lssmCandidate.label} · ${lssmCandidate.owner} · direct LSSM control`);
17358:                     try {
17359:                         const cleared = await activateTransportSweepLssmRelease(lssmCandidate);
17360:                         if (!cleared) throw new Error('LSSM release confirmation timed out');
17361:                         clearedHere += 1;
17362:                         transportSweepRuntime.cleared += 1;
17363:                         transportSweepRuntime.processed += 1;
17364:                         transportSweepLog(`Released ${lssmCandidate.label} for ${lssmCandidate.owner} at ${item.caption}`);
17365:                     } catch (err) {
17366:                         transportSweepRuntime.errors += 1;
17367:                         transportSweepLog(`Failed ${lssmCandidate.label}: ${err?.message || 'unknown error'}`, 'error');
17368:                     }
17369: 
17370:                     if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
17371:                         await transportSweepSleep(state.transportSweep.delayMs);
17372:                         transportSweepLog(`Returning to ${item.caption} for remaining alliance ambulances`);
17373:                         missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
17374:                         if (!missionOpen) {
17375:                             transportSweepRuntime.errors += 1;
17376:                             transportSweepLog(`Could not return to ${item.caption} after releasing ${lssmCandidate.label}`, 'error');
17377:                             break;
17378:                         }
17379:                     }
17380:                     continue;
17381:                 }
17382: 
17383:                 if (lssmSeen) {
17384:                     transportSweepLog(`No further LSSM alliance release controls remain at ${item.caption}`);
17385:                     break;
17386:                 }
17387:                 fallbackMode = true;
17388:             }
17389: 
17390:             if (!fallbackLogged) {
17391:                 fallbackLogged = true;
17392:                 transportSweepLog(`LSSM release controls did not appear at ${item.caption}; using the verified vehicle-window fallback`, 'warn');
17393:             }
17394:             const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);
17395:             const candidateStats = transportSweepRuntime.lastCandidateStats || {};
17396:             if (!initialScanLogged) {
17397:                 const source = candidateStats.source ? ` · ${candidateStats.source}` : '';
17398:                 transportSweepLog(`Fallback scan: ${candidateStats.totalLinks || 0} vehicle links · ${candidateStats.allianceLinks || 0} alliance FMS 5 · ${candidateStats.candidates || 0} patient candidates${source}`);
17399:                 if (transportSweepRuntime.rejectedOwn > 0) {
17400:                     transportSweepLog(`Ignored ${transportSweepRuntime.rejectedOwn} of your own FMS 5 vehicle${transportSweepRuntime.rejectedOwn === 1 ? '' : 's'} at ${item.caption}`);
17401:                 }
17402:                 initialScanLogged = true;
17403:             }
17404: 
17405:             if (candidates.length) missionHadCandidates = true;
17406:             const candidate = candidates.find(entry => !attemptedVehicleIds.has(String(entry.vehicleId)));
17407:             if (!candidate) {
17408:                 if (!missionHadCandidates) transportSweepLog(`No alliance-owned FMS 5 patient vehicles were found inside ${item.caption}`, 'warn');
17409:                 else transportSweepLog(`Checked every alliance-owned FMS 5 patient vehicle at ${item.caption}; none exposed a release control`, 'warn');
17410:                 break;
17411:             }
17412: 
17413:             attemptedVehicleIds.add(String(candidate.vehicleId));
17414:             transportSweepRuntime.currentVehicleHref = candidate.href;
17415:             transportSweepRuntime.currentItem = String(candidate.label || `Vehicle ${candidate.vehicleId}`);
17416:             renderTransportSweepPanel();
17417:             transportSweepLog(`Fallback check: FMS 5 ${candidate.label} (${candidate.vehicleId})`);
17418: 
17419:             const vehicleResult = await openTransportSweepVehicle(candidate);
17420:             if (transportSweepRuntime.stopRequested) break;
17421:             const button = vehicleResult?.button || (vehicleResult?.opened ? await transportSweepWaitFor(
17422:                 () => findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline),
17423:                 3200,
17424:                 120
17425:             ) : null);
17426: 
17427:             if (!button) {
17428:                 transportSweepLog(`${candidate.label} is carrying a patient but is not transport-ready; continuing in the same mission`);
17429:             } else {
17430:                 try {
17431:                     button.click();
17432:                     const cleared = await transportSweepWaitFor(() => {
17433:                         if (!button.isConnected || !transportSweepElementVisible(button) || button.disabled) return true;
17434:                         return String(button.textContent || '').trim().toLowerCase() !== 'discharge patient' ? true : null;
17435:                     }, 5000, 140);
17436:                     if (!cleared) throw new Error('Discharge confirmation timed out');
17437:                     clearedHere += 1;
17438:                     transportSweepRuntime.cleared += 1;
17439:                     transportSweepRuntime.processed += 1;
17440:                     transportSweepLog(`Cleared ${candidate.label} at ${item.caption}`);
17441:                 } catch (err) {
17442:                     transportSweepRuntime.errors += 1;
17443:                     transportSweepLog(`Failed ${candidate.label}: ${err?.message || 'unknown error'}`, 'error');
17444:                 }
17445:             }
17446: 
17447:             if (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
17448:                 await transportSweepSleep(state.transportSweep.delayMs);
17449:                 transportSweepLog(`Returning to ${item.caption} for remaining alliance ambulances`);
17450:                 missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
17451:                 if (!missionOpen) {
17452:                     transportSweepRuntime.errors += 1;
17453:                     transportSweepLog(`Could not return to ${item.caption} during fallback processing`, 'error');
17454:                     break;
17455:                 }
17456:             }
17457:         }
17458: 
17459:         await closeTransportSweepWindows('finishing the mission');
17460: 
17461:         if (clearedHere === 0 && !transportSweepRuntime.stopRequested) {
17462:             transportSweepRuntime.skipped += 1;
17463:             renderTransportSweepPanel();
17464:         }
17465:         return clearedHere;
17466:     }
17467: 
17468:     async function startTransportSweep() {
17469:         if (transportSweepRuntime.running) return;
17470:         const queue = buildTransportSweepQueue();
17471:         if (!queue.length) {
17472:             showToast('No alliance patient transports found');
17473:             return;
17474:         }
17475:         showToast('Verifying your personal vehicle list…');
17476:         const ownershipReady = await refreshPersonalVehicleData(true);
17477:         if (!ownershipReady || !vehicleApiReady || personalVehicleApiCache.size === 0) {
17478:             showToast('Transport Sweep cancelled — your vehicle ownership list could not be verified');
17479:             return;
17480:         }
17481:         transportSweepRuntime.ownVehicleIds = new Set(Array.from(personalVehicleApiCache.keys(), id => String(id)));
17482:         const totalRequests = queue.reduce((sum, item) => sum + Math.max(1, Number(item.count) || 1), 0);
17483:         const planned = Math.min(totalRequests, state.transportSweep.maxPerRun);
17484:         const confirmed = pageWindow.confirm(`Transport Sweep will attempt up to ${planned} alliance-member patient releases across ${queue.length} alliance mission${queue.length === 1 ? '' : 's'}.
17485: 
17486: The sweep waits dynamically for LSSM's “Release patient (No reward)” controls and processes one alliance ambulance at a time. Your own verified vehicle IDs are always excluded. If LSSM controls do not appear, the existing vehicle-window route remains available as a fallback. Continue?`);
17487:         if (!confirmed) return;
17488:         transportSweepRuntime.running = true;
17489:         transportSweepRuntime.stopRequested = false;
17490:         transportSweepRuntime.currentMissionId = null;
17491:         transportSweepRuntime.currentVehicleHref = '';
17492:         transportSweepRuntime.cleared = 0;
17493:         transportSweepRuntime.skipped = 0;
17494:         transportSweepRuntime.errors = 0;
17495:         transportSweepRuntime.processed = 0;
17496:         transportSweepRuntime.rejectedOwn = 0;
17497:         transportSweepRuntime.missionAnchorBaseline = new Set();
17498:         transportSweepRuntime.vehicleButtonBaseline = new Set();
17499:         transportSweepRuntime.missionWindowRoot = null;
17500:         transportSweepRuntime.activeWindowRoot = null;
17501:         transportSweepRuntime.ownedWindowLayers = new Set();
17502:         transportSweepRuntime.activeWindowCreatedLayer = false;
17503:         transportSweepRuntime.lastCandidateStats = null;
17504:         runtimeClearTimeout(transportSweepRuntime.hudDismissTimer);
17505:         transportSweepRuntime.hudDismissTimer = null;
17506:         transportSweepRuntime.startedAt = Date.now();
17507:         transportSweepRuntime.missionIndex = 0;
17508:         transportSweepRuntime.missionTotal = queue.length;
17509:         transportSweepRuntime.currentItem = 'Preparing sweep';
17510:         transportSweepRuntime.statusMessage = 'Preparing patient transport sweep';
17511:         transportSweepRuntime.statusLevel = 'info';
17512:         transportSweepRuntime.hudFinal = false;
17513:         transportSweepRuntime.log = [];
17514:         renderTransportSweepPanel();
17515:         transportSweepLog(`Sweep started: ${queue.length} missions, maximum ${state.transportSweep.maxPerRun} requests`);
17516:         try {
17517:             for (let missionOffset = 0; missionOffset < queue.length; missionOffset += 1) {
17518:                 const item = queue[missionOffset];
17519:                 if (transportSweepRuntime.stopRequested || transportSweepRuntime.cleared >= state.transportSweep.maxPerRun) break;
17520:                 transportSweepRuntime.missionIndex = missionOffset + 1;
17521:                 transportSweepRuntime.currentItem = String(item?.caption || `Mission ${item?.missionId || missionOffset + 1}`);
17522:                 renderTransportSweepPanel();
17523:                 const remaining = state.transportSweep.maxPerRun - transportSweepRuntime.cleared;
17524:                 await processTransportSweepMission(item, remaining);
17525:                 if (!transportSweepRuntime.stopRequested) await transportSweepSleep(state.transportSweep.delayMs);
17526:             }
17527:         } catch (err) {
17528:             transportSweepRuntime.errors += 1;
17529:             transportSweepLog(`Sweep stopped by error: ${err?.message || 'unknown error'}`, 'error');
17530:         } finally {
17531:             await closeTransportSweepWindows('finishing the sweep');
17532:             const wasStopped = transportSweepRuntime.stopRequested;
17533:             transportSweepRuntime.running = false;
17534:             transportSweepRuntime.stopRequested = false;
17535:             transportSweepRuntime.currentMissionId = null;
17536:             transportSweepRuntime.currentVehicleHref = '';
17537:             transportSweepRuntime.currentItem = '';
17538:             transportSweepRuntime.missionAnchorBaseline = new Set();
17539:             transportSweepRuntime.vehicleButtonBaseline = new Set();
17540:             transportSweepRuntime.activeWindowRoot = null;
17541:             transportSweepRuntime.ownedWindowLayers = new Set();
17542:             transportSweepRuntime.activeWindowCreatedLayer = false;
17543:             transportSweepRuntime.hudFinal = true;
17544:             buildTransportSweepQueue();
17545:             scheduleTransportWatcherRefresh(0);
17546:             showToast(wasStopped ? `Transport Sweep stopped · ${transportSweepRuntime.cleared} cleared` : `Transport Sweep complete · ${transportSweepRuntime.cleared} cleared`);
17547:             transportSweepLog(`${wasStopped ? 'Stopped' : 'Complete'}: ${transportSweepRuntime.cleared} cleared, ${transportSweepRuntime.skipped} skipped, ${transportSweepRuntime.errors} errors`, transportSweepRuntime.errors ? 'error' : 'info');
17548:             scheduleTransportSweepHudDismiss(6500);
17549:         }
17550:     }
17551: 
17552:     function stopTransportSweep() {
17553:         if (!transportSweepRuntime.running) return;
17554:         transportSweepRuntime.stopRequested = true;
17555:         transportSweepLog('Stop requested — finishing the current action');
17556:         renderTransportSweepPanel();
17557:     }
17558: 
17559:     function vehicleTargetInfo(vehicle) {
17560:         if (!vehicle || typeof vehicle !== 'object') return { type: null, id: null };
17561:         const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
17562:             .filter(item => item && typeof item === 'object');
17563:         for (const item of containers) {
17564:             const type = String(item.target_type ?? item.targetType ?? '').toLowerCase();
17565:             const id = normaliseMissionId(item.target_id ?? item.targetId);
17566:             if ((type === 'mission' || type === 'building') && id !== null && id !== '0') return { type, id };
17567:             const missionId = normaliseMissionId(item.mission_id ?? item.missionId);
17568:             if (missionId !== null && missionId !== '0') return { type: 'mission', id: missionId };
17569:             const buildingId = normaliseMissionId(item.target_building_id ?? item.targetBuildingId);
17570:             if (buildingId !== null && buildingId !== '0') return { type: 'building', id: buildingId };
17571:         }
17572:         return { type: null, id: null };
17573:     }
17574: 
17575:     function vehicleSearchSignal(vehicle) {
17576:         if (!vehicle || typeof vehicle !== 'object') return '';
17577:         const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
17578:             .filter(item => item && typeof item === 'object');
17579:         const values = [];
17580:         for (const item of containers) {
```

## Mission Value mission-window discovery, rendering and observation

Canonical lines 21000–21920

```javascript
21000:             if (closestEventTarget(event, '[data-critical-advanced-toggle]')) {
21001:                 const next = !state.missionAgeWatch?.advancedFiltersOpen;
21002:                 state.missionAgeWatch = { ...(state.missionAgeWatch || {}), advancedFiltersOpen: next };
21003:                 saveState();
21004:                 setCriticalAdvancedFiltersOpen(next, drawer);
21005:                 return;
21006:             }
21007:             const quickViewButton = closestEventTarget(event, '[data-critical-quick-view]');
21008:             if (quickViewButton) {
21009:                 const quickView = String(quickViewButton.dataset.criticalQuickView || '');
21010:                 if (applyCriticalQuickView(quickView)) {
21011:                     resetCriticalVirtualWindow(drawer);
21012:                     renderCriticalDrawer(null, { updateViewTime: true });
21013:                 }
21014:                 return;
21015:             }
21016:             if (closestEventTarget(event, '.mcms-drawer-expand')) { toggleCriticalDrawerExpanded(); return; }
21017:             if (closestEventTarget(event, '.mcms-drawer-refresh')) { refreshCriticalDrawer(true); return; }
21018:             if (closestEventTarget(event, '.mcms-drawer-close')) { closeCriticalDrawer(); return; }
21019:             if (closestEventTarget(event, '[data-critical-clear-filters]')) {
21020:                 resetCriticalWatchFilters();
21021:                 resetCriticalVirtualWindow(drawer);
21022:                 renderCriticalDrawer(null, { updateViewTime: true });
21023:                 return;
21024:             }
21025:             const ageFilterButton = closestEventTarget(event, '[data-critical-age-filter]');
21026:             if (ageFilterButton) {
21027:                 const ageFilter = String(ageFilterButton.dataset.criticalAgeFilter || '');
21028:                 if (CRITICAL_AGE_FILTER_KEYS.includes(ageFilter)) {
21029:                     state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ageFilter };
21030:                     saveState();
21031:                     resetCriticalVirtualWindow(drawer);
21032:                     renderCriticalDrawer(null, { updateViewTime: true });
21033:                 }
21034:                 return;
21035:             }
21036:             const sortButton = closestEventTarget(event, '[data-critical-sort]');
21037:             if (sortButton) {
21038:                 const sortMode = String(sortButton.dataset.criticalSort || '');
21039:                 if (CRITICAL_SORT_KEYS.includes(sortMode)) {
21040:                     state.missionAgeWatch = { ...(state.missionAgeWatch || {}), sortMode };
21041:                     saveState();
21042:                     resetCriticalVirtualWindow(drawer);
21043:                     renderCriticalDrawer(null, { updateViewTime: true });
21044:                 }
21045:                 return;
21046:             }
21047:             if (closestEventTarget(event, '[data-critical-lock-origin]')) {
21048:                 if (lockCriticalDistanceOrigin()) {
21049:                     resetCriticalVirtualWindow(drawer);
21050:                     renderCriticalDrawer(null, { updateViewTime: true });
21051:                     showToast('Distance origin locked to current map centre');
21052:                 }
21053:                 return;
21054:             }
21055:             const ownershipButton = closestEventTarget(event, '[data-critical-ownership-filter]');
21056:             if (ownershipButton) {
21057:                 const ownership = String(ownershipButton.dataset.criticalOwnershipFilter || '');
21058:                 if (CRITICAL_OWNERSHIP_FILTER_KEYS.includes(ownership)) {
21059:                     state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ownershipFilter: ownership };
21060:                     saveState();
21061:                     resetCriticalVirtualWindow(drawer);
21062:                     renderCriticalDrawer(null, { updateViewTime: true });
21063:                 }
21064:                 return;
21065:             }
21066:             const categoryButton = closestEventTarget(event, '[data-critical-category-filter]');
21067:             if (categoryButton) {
21068:                 const category = String(categoryButton.dataset.criticalCategoryFilter || '');
21069:                 if (CRITICAL_CATEGORY_FILTER_KEYS.includes(category)) {
21070:                     state.missionAgeWatch = { ...(state.missionAgeWatch || {}), categoryFilter: category };
21071:                     saveState();
21072:                     resetCriticalVirtualWindow(drawer);
21073:                     renderCriticalDrawer(null, { updateViewTime: true });
21074:                 }
21075:                 return;
21076:             }
21077:             const statusButton = closestEventTarget(event, '[data-critical-primary-status]');
21078:             if (statusButton) {
21079:                 const status = String(statusButton.dataset.criticalPrimaryStatus || 'all');
21080:                 if (CRITICAL_PRIMARY_STATUS_KEYS.includes(status)) {
21081:                     state.missionAgeWatch = { ...(state.missionAgeWatch || {}), primaryStatus: selectedCriticalPrimaryStatus() === status ? 'all' : status };
21082:                     saveState();
21083:                     resetCriticalVirtualWindow(drawer);
21084:                     renderCriticalDrawer(null, { updateViewTime: true });
21085:                 }
21086:                 return;
21087:             }
21088:             const conditionButton = closestEventTarget(event, '[data-critical-condition]');
21089:             if (conditionButton) {
21090:                 const condition = String(conditionButton.dataset.criticalCondition || '');
21091:                 if (condition === 'onway') state.missionAgeWatch = { ...(state.missionAgeWatch || {}), hasVehiclesOnWay: !state.missionAgeWatch?.hasVehiclesOnWay };
21092:                 if (condition === 'my-units') state.missionAgeWatch = { ...(state.missionAgeWatch || {}), onlyMyUnits: !state.missionAgeWatch?.onlyMyUnits };
21093:                 saveState();
21094:                 resetCriticalVirtualWindow(drawer);
21095:                 renderCriticalDrawer(null, { updateViewTime: true });
21096:                 return;
21097:             }
21098:             const valueModeButton = closestEventTarget(event, '[data-critical-value-mode]');
21099:             if (valueModeButton) {
21100:                 const mode = String(valueModeButton.dataset.criticalValueMode || 'total');
21101:                 if (CRITICAL_VALUE_MODE_KEYS.includes(mode)) {
21102:                     state.missionAgeWatch = { ...(state.missionAgeWatch || {}), valueMode: mode };
21103:                     saveState();
21104:                     renderCriticalDrawer(null, { updateViewTime: true });
21105:                 }
21106:                 return;
21107:             }
21108:             if (closestEventTarget(event, '[data-critical-load-more]')) {
21109:                 criticalDrawerRenderLimit += CRITICAL_RENDER_BATCH_SIZE;
21110:                 renderCriticalDrawer(null, { updateViewTime: false, preserveScroll: true });
21111:                 return;
21112:             }
21113:             const zoomButton = closestEventTarget(event, '.mcms-critical-zoom');
21114:             if (zoomButton) {
21115:                 event.preventDefault();
21116:                 event.stopPropagation();
21117:                 focusMissionById(zoomButton.dataset.zoomMissionId, false);
21118:                 return;
21119:             }
21120:             const openButton = closestEventTarget(event, '.mcms-critical-open');
21121:             if (openButton) {
21122:                 event.preventDefault();
21123:                 event.stopPropagation();
21124:                 focusMissionById(openButton.dataset.openMissionId, true);
21125:                 return;
21126:             }
21127:             const row = closestEventTarget(event, '[data-mission-id]');
21128:             if (row) focusMissionById(row.dataset.missionId, false);
21129:         });
21130:         drawer.addEventListener('dblclick', event => {
21131:             if (closestEventTarget(event, '.mcms-critical-zoom, .mcms-critical-open')) return;
21132:             const row = closestEventTarget(event, '[data-mission-id]');
21133:             if (row) { event.preventDefault(); focusMissionById(row.dataset.missionId, true); }
21134:         });
21135:         runtimeListen(document, 'pointerdown', event => {
21136:             const activeDrawer = document.getElementById(SCRIPT.criticalDrawerId);
21137:             const controls = activeDrawer?.querySelector?.('[data-critical-view-controls]');
21138:             if (!controls?.classList?.contains('mcms-open')) return;
21139:             if (event.target && controls.contains(event.target)) return;
21140:             closeCriticalViewControls(activeDrawer);
21141:         }, true);
21142:         document.body.appendChild(drawer);
21143:         updateCriticalDrawerExpandButton(drawer);
21144:         return drawer;
21145:     }
21146: 
21147:     function criticalEntryNeedsAssistance(entry) {
21148:         return Boolean(summariseCriticalRequirement(entry?.snapshot?.missingText) || entry?.stuckRecord?.isStuck);
21149:     }
21150: 
21151:     function missionAgeWatchHasNonDefaultState() {
21152:         const watch = state.missionAgeWatch || {};
21153:         return selectedCriticalAgeFilter() !== '8h' ||
21154:             selectedCriticalSortMode() !== 'age' ||
21155:             selectedCriticalOwnershipFilter() !== 'personal' ||
21156:             selectedCriticalCategoryFilter() !== 'all' ||
21157:             selectedCriticalPrimaryStatus() !== 'all' ||
21158:             Boolean(watch.hasVehiclesOnWay) ||
21159:             Boolean(watch.onlyMyUnits) ||
21160:             selectedCriticalValueMode() !== 'total' ||
21161:             selectedCriticalDistanceOrigin() !== 'live';
21162:     }
21163: 
21164:     function resetCriticalWatchFilters() {
21165:         const expanded = Boolean(state.missionAgeWatch?.expanded);
21166:         state.missionAgeWatch = {
21167:             ...(state.missionAgeWatch || {}),
21168:             ageFilter: '8h',
21169:             sortMode: 'age',
21170:             expanded,
21171:             ownershipFilter: 'personal',
21172:             categoryFilter: 'all',
21173:             primaryStatus: 'all',
21174:             advancedFiltersOpen: false,
21175:             hasVehiclesOnWay: false,
21176:             onlyMyUnits: false,
21177:             valueMode: 'total',
21178:             distanceOrigin: 'live',
21179:             lockedOrigin: null
21180:         };
21181:         criticalDrawerRenderLimit = CRITICAL_RENDER_BATCH_SIZE;
21182:         saveState();
21183:     }
21184: 
21185:     function criticalAgeFiltersHtml(allEntries) {
21186:         const selected = selectedCriticalAgeFilter();
21187:         const scoped = criticalFilterEntries(allEntries, ['age']);
21188:         const button = key => {
21189:             const definition = criticalAgeFilterDefinition(key);
21190:             const active = selected === key;
21191:             const count = scoped.filter(entry => definition.minAgeMs === 0 ? true : Number.isFinite(entry.missionAge) && entry.missionAge >= definition.minAgeMs).length;
21192:             return `<button type="button" class="mcms-critical-age-filter mcms-age-filter-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}" data-critical-age-filter="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(definition.title)}"><span>${escapeHtml(definition.label)}</span><strong>${count.toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓ SELECTED' : 'SELECT'}</i></button>`;
21193:         };
21194:         return `<span class="mcms-critical-age-label">AGE</span>${CRITICAL_AGE_FILTER_KEYS.map(button).join('')}`;
21195:     }
21196: 
21197:     function criticalDistanceOriginControlsHtml() {
21198:         const selected = selectedCriticalDistanceOrigin();
21199:         const options = criticalDistanceOriginOptions().map(option => `<option value="${escapeHtml(option.key)}"${selected === option.key ? ' selected' : ''}>${escapeHtml(option.label)}</option>`).join('');
21200:         return `<label class="mcms-critical-origin-control" title="Choose the reference point used for mission distances"><span>ORIGIN</span><select data-critical-distance-origin>${options}</select></label><button type="button" class="mcms-critical-lock-origin" data-critical-lock-origin title="Lock distance calculations to the current map centre">LOCK HERE</button>`;
21201:     }
21202: 
21203:     function criticalSortControlsHtml() {
21204:         const selected = selectedCriticalSortMode();
21205:         const ageDefinition = criticalAgeFilterDefinition();
21206:         const button = (key, label, title) => {
21207:             const active = selected === key;
21208:             return `<button type="button" class="mcms-critical-sort-button mcms-sort-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}" data-critical-sort="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span>${escapeHtml(label)}</span><i aria-hidden="true">${active ? '✓ SELECTED' : 'SELECT'}</i></button>`;
21209:         };
21210:         return `<span class="mcms-critical-sort-label">SORT</span>${button('age', 'Age', `Use ${ageDefinition.sort === 'newest' ? 'newest' : 'oldest'} mission ordering for the selected age range`)}${button('closest', 'Closest', 'Sort closest to the selected distance origin first')}${button('furthest', 'Furthest', 'Sort furthest from the selected distance origin first')}${criticalDistanceOriginControlsHtml()}`;
21211:     }
21212: 
21213:     function criticalViewControlsSummary(allEntries = null) {
21214:         const ageDefinition = criticalAgeFilterDefinition();
21215:         let age = String(ageDefinition.label || 'ALL').toUpperCase();
21216:         if (Array.isArray(allEntries)) {
21217:             const scoped = criticalFilterEntries(allEntries, ['age']);
21218:             const count = scoped.filter(entry => ageDefinition.minAgeMs === 0 ? true : Number.isFinite(entry.missionAge) && entry.missionAge >= ageDefinition.minAgeMs).length;
21219:             age = `${age} ${count.toLocaleString('en-GB')}`;
21220:         }
21221:         const sort = {
21222:             age: 'AGE',
21223:             closest: 'CLOSEST',
21224:             furthest: 'FURTHEST'
21225:         }[selectedCriticalSortMode()] || 'AGE';
21226:         const originKey = selectedCriticalDistanceOrigin();
21227:         const originOption = criticalDistanceOriginOptions().find(option => option.key === originKey);
21228:         let origin = String(originOption?.label || 'Live map centre')
21229:             .replace(/^Quick Place:\s*/iu, '')
21230:             .replace(/^Bookmark:\s*/iu, '')
21231:             .trim();
21232:         if (originKey === 'live') origin = 'LIVE MAP';
21233:         else if (originKey === 'locked') origin = 'LOCKED';
21234:         else origin = origin.toUpperCase();
21235:         return `${age} · ${sort} · ${origin}`;
21236:     }
21237: 
21238:     function setCriticalViewControlsOpen(open, drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
21239:         const controls = drawer?.querySelector?.('[data-critical-view-controls]');
21240:         const toggle = controls?.querySelector?.('[data-critical-view-toggle]');
21241:         const menu = controls?.querySelector?.('[data-critical-view-menu]');
21242:         if (!controls || !toggle || !menu) return false;
21243:         const next = Boolean(open);
21244:         controls.classList.toggle('mcms-open', next);
21245:         toggle.setAttribute('aria-expanded', next ? 'true' : 'false');
21246:         menu.hidden = !next;
21247:         return true;
21248:     }
21249: 
21250:     function closeCriticalViewControls(drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
21251:         const controls = drawer?.querySelector?.('[data-critical-view-controls]');
21252:         if (!controls?.classList?.contains('mcms-open')) return false;
21253:         setCriticalViewControlsOpen(false, drawer);
21254:         return true;
21255:     }
21256: 
21257:     function toggleCriticalViewControls(drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
21258:         const controls = drawer?.querySelector?.('[data-critical-view-controls]');
21259:         if (!controls) return false;
21260:         return setCriticalViewControlsOpen(!controls.classList.contains('mcms-open'), drawer);
21261:     }
21262: 
21263:     function selectedCriticalQuickView() {
21264:         const status = selectedCriticalPrimaryStatus();
21265:         const onWay = Boolean(state.missionAgeWatch?.hasVehiclesOnWay);
21266:         const myUnits = Boolean(state.missionAgeWatch?.onlyMyUnits);
21267:         if (status === 'all' && !onWay && !myUnits) return 'all';
21268:         if (status === 'attention' && !onWay && !myUnits) return 'attention';
21269:         if (status === 'all' && onWay && !myUnits) return 'responding';
21270:         if (status === 'clearing' && !onWay && !myUnits) return 'clearing';
21271:         if (status === 'on-scene' && !onWay && !myUnits) return 'stable';
21272:         if (status === 'all' && !onWay && myUnits) return 'my-units';
21273:         return 'custom';
21274:     }
21275: 
21276:     function applyCriticalQuickView(key) {
21277:         const definitions = {
21278:             all: { primaryStatus: 'all', hasVehiclesOnWay: false, onlyMyUnits: false },
21279:             attention: { primaryStatus: 'attention', hasVehiclesOnWay: false, onlyMyUnits: false },
21280:             responding: { primaryStatus: 'all', hasVehiclesOnWay: true, onlyMyUnits: false },
21281:             clearing: { primaryStatus: 'clearing', hasVehiclesOnWay: false, onlyMyUnits: false },
21282:             stable: { primaryStatus: 'on-scene', hasVehiclesOnWay: false, onlyMyUnits: false },
21283:             'my-units': { primaryStatus: 'all', hasVehiclesOnWay: false, onlyMyUnits: true }
21284:         };
21285:         const definition = definitions[String(key || '')];
21286:         if (!definition) return false;
21287:         state.missionAgeWatch = { ...(state.missionAgeWatch || {}), ...definition };
21288:         saveState();
21289:         return true;
21290:     }
21291: 
21292:     function setCriticalAdvancedFiltersOpen(open, drawer = document.getElementById(SCRIPT.criticalDrawerId)) {
21293:         const shell = drawer?.querySelector?.('[data-critical-advanced-shell]');
21294:         const toggle = shell?.querySelector?.('[data-critical-advanced-toggle]');
21295:         const panel = shell?.querySelector?.('[data-critical-advanced-panel]');
21296:         if (!shell || !toggle || !panel) return false;
21297:         const next = Boolean(open);
21298:         shell.classList.toggle('mcms-open', next);
21299:         toggle.setAttribute('aria-expanded', next ? 'true' : 'false');
21300:         panel.hidden = !next;
21301:         return true;
21302:     }
21303: 
21304:     function criticalAdvancedFilterSummaryText() {
21305:         const statusLabels = {
21306:             all: 'Any condition',
21307:             attention: 'Needs attention',
21308:             'no-scene': 'No units on scene',
21309:             assistance: 'Needs assistance',
21310:             clearing: 'Clearing',
21311:             'on-scene': 'On scene / stable'
21312:         };
21313:         const parts = [];
21314:         const status = selectedCriticalPrimaryStatus();
21315:         if (status !== 'all') parts.push(statusLabels[status] || status);
21316:         if (state.missionAgeWatch?.hasVehiclesOnWay) parts.push('Vehicles on way');
21317:         if (state.missionAgeWatch?.onlyMyUnits) parts.push('Only my units');
21318:         return parts.length ? parts.join(' + ') : 'Exact mission conditions and unit scope';
21319:     }
21320: 
21321:     function criticalQuickViewsHtml(allEntries) {
21322:         const scoped = criticalFilterEntries(allEntries, ['status', 'onway', 'myunits']);
21323:         const countStatus = key => scoped.filter(entry => criticalEntryPrimaryStatus(entry) === key).length;
21324:         const counts = {
21325:             all: scoped.length,
21326:             attention: scoped.filter(entry => ['no-scene', 'assistance'].includes(criticalEntryPrimaryStatus(entry))).length,
21327:             responding: scoped.filter(entry => Math.max(0, Number(entry?.units?.onWay ?? entry?.units?.travelling) || 0) > 0).length,
21328:             clearing: countStatus('clearing'),
21329:             stable: countStatus('on-scene'),
21330:             'my-units': scoped.filter(criticalEntryHasMyUnits).length
21331:         };
21332:         const selected = selectedCriticalQuickView();
21333:         const definitions = [
21334:             ['all', 'All', 'Show every mission matching the ownership, category and age filters'],
21335:             ['attention', 'Attention', 'Show missions with no units on scene or detected assistance requirements'],
21336:             ['responding', 'Responding', 'Show missions with at least one vehicle on the way'],
21337:             ['clearing', 'Clearing', 'Show missions currently completing'],
21338:             ['stable', 'Stable', 'Show missions with units on scene and no detected issue'],
21339:             ['my-units', 'My Units', 'Show missions with one of your units committed']
21340:         ];
21341:         return definitions.map(([key, label, title]) => {
21342:             const active = selected === key;
21343:             const count = Number(counts[key]) || 0;
21344:             return `<button type="button" class="mcms-critical-quick-view mcms-quick-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}${count === 0 ? ' mcms-zero' : ''}" data-critical-quick-view="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span>${escapeHtml(label)}</span><strong>${count.toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓' : ''}</i></button>`;
21345:         }).join('');
21346:     }
21347: 
21348:     function criticalOperationalFilterLabel() {
21349:         const quick = selectedCriticalQuickView();
21350:         const labels = {
21351:             all: 'All missions',
21352:             attention: 'Needs attention',
21353:             responding: 'Responding',
21354:             clearing: 'Clearing',
21355:             stable: 'Stable',
21356:             'my-units': 'Only my units'
21357:         };
21358:         return labels[quick] || `Custom: ${criticalAdvancedFilterSummaryText()}`;
21359:     }
21360: 
21361:     function criticalFilterOverviewHtml(allEntries, visibleEntries) {
21362:         const ownership = { all: 'All ownership', personal: 'Personal', alliance: 'Alliance' }[selectedCriticalOwnershipFilter()] || 'Personal';
21363:         const category = { all: 'All categories', standard: 'Standard', event: 'Timed event', special: 'Special event' }[selectedCriticalCategoryFilter()] || 'All categories';
21364:         const filterText = `${ownership} · ${category} · ${criticalOperationalFilterLabel()}`;
21365:         const showing = `Showing ${visibleEntries.length.toLocaleString('en-GB')} of ${allEntries.length.toLocaleString('en-GB')}`;
21366:         return `<span class="mcms-critical-filter-overview-copy"><small>ACTIVE FILTER</small><strong title="${escapeHtml(filterText)}">${escapeHtml(filterText)}</strong></span><span class="mcms-critical-filter-overview-count">${escapeHtml(showing)}</span>${missionAgeWatchHasNonDefaultState() ? '<button type="button" data-critical-clear-filters title="Reset all Mission Age Watch filters and sorting">Clear</button>' : ''}`;
21367:     }
21368: 
21369:     function criticalOwnershipFiltersHtml(allEntries) {
21370:         const selected = selectedCriticalOwnershipFilter();
21371:         const scoped = criticalFilterEntries(allEntries, ['ownership']);
21372:         const counts = { all: scoped.length, personal: 0, alliance: 0 };
21373:         scoped.forEach(entry => { if (CRITICAL_OWNERSHIP_KEYS.includes(entry.ownership)) counts[entry.ownership] += 1; });
21374:         const button = (key, label, title) => {
21375:             const active = selected === key;
21376:             const allianceClass = key === 'alliance' ? ' mcms-alliance-text' : '';
21377:             return `<button type="button" class="mcms-critical-type-filter mcms-ownership-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}" data-critical-ownership-filter="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span class="${allianceClass.trim()}">${escapeHtml(label)}</span><strong>${counts[key].toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓ SELECTED' : 'SELECT'}</i></button>`;
21378:         };
21379:         return `<span class="mcms-critical-type-label">OWNERSHIP</span>${button('all', 'All', 'Show Personal and Alliance missions')}${button('personal', 'Personal', 'Show missions owned by you')}${button('alliance', 'Alliance', 'Show Alliance-owned or Alliance-shared missions')}`;
21380:     }
21381: 
21382:     function criticalCategoryFiltersHtml(allEntries) {
21383:         const selected = selectedCriticalCategoryFilter();
21384:         const scoped = criticalFilterEntries(allEntries, ['category']);
21385:         const counts = { all: scoped.length, standard: 0, event: 0, special: 0 };
21386:         scoped.forEach(entry => { if (CRITICAL_CATEGORY_KEYS.includes(entry.category)) counts[entry.category] += 1; });
21387:         const button = (key, label, title) => {
21388:             const active = selected === key;
21389:             return `<button type="button" class="mcms-critical-category-filter mcms-category-${escapeHtml(key)}${active ? ' mcms-filter-active' : ''}${counts[key] === 0 ? ' mcms-zero' : ''}" data-critical-category-filter="${escapeHtml(key)}" aria-pressed="${active ? 'true' : 'false'}" title="${escapeHtml(title)}"><span>${escapeHtml(label)}</span><strong>${counts[key].toLocaleString('en-GB')}</strong><i aria-hidden="true">${active ? '✓' : ''}</i></button>`;
21390:         };
21391:         return `<span class="mcms-critical-category-label">CATEGORY</span>${button('all', 'All', 'Show Standard, Timed Event and Special Event missions')}${button('standard', 'Standard', 'Show normal missions')}${button('event', 'Timed Event', 'Show ordinary timed or community Event missions')}${button('special', 'Special Event', 'Show official developer-launched Special Event missions')}`;
21392:     }
21393: 
21394:     function criticalMissionValueDetails(entry) {
21395:         if (entry?.valueDetails && Object.prototype.hasOwnProperty.call(entry.valueDetails, 'value')) return entry.valueDetails;
21396:         const missionId = normaliseMissionId(entry?.missionId);
21397:         const marker = entry?.marker || entry?.snapshot?.marker || null;
21398:         const liveMarkerValue = exactCreditFromObject(marker);
21399:         if (liveMarkerValue !== null) return { value: liveMarkerValue, source: 'live marker' };
21400:         const snapshotValue = parseCreditValue(entry?.snapshot?.averageCredits);
21401:         if (snapshotValue !== null) return { value: snapshotValue, source: 'mission snapshot' };
21402:         const overlayValue = missionId === null ? null : parseCreditValue(missionOverlayData.get(missionId)?.averageCredits);
21403:         if (overlayValue !== null) return { value: overlayValue, source: 'captured mission data' };
21404:         const entryValue = parseCreditValue(entry?.averageCredits);
21405:         if (entryValue !== null) return { value: entryValue, source: 'watcher record' };
21406:         const panelValue = missionId === null ? null : creditsFromMissionPanel(missionId);
21407:         if (panelValue !== null) return { value: panelValue, source: 'mission list' };
21408:         return { value: null, source: 'unavailable' };
21409:     }
21410: 
21411: 
21412:     function missionValueCurrencyMeta(hostname = location.hostname) {
21413:         const host = String(hostname || '').trim().toLowerCase();
21414:         if (/(?:^|\.)missionchief\.com$/u.test(host)) return { locale: 'en-US', symbol: '$' };
21415:         if (/(?:^|\.)leitstellenspiel\.de$/u.test(host)) return { locale: 'de-DE', symbol: '€' };
21416:         if (/(?:^|\.)meldkamerspel\.com$/u.test(host)) return { locale: 'nl-NL', symbol: '€' };
21417:         return { locale: 'en-GB', symbol: '£' };
21418:     }
21419: 
21420:     function formatMissionWindowValue(value, hostname = location.hostname) {
21421:         const amount = Number(value);
21422:         if (!Number.isFinite(amount) || amount < 0) return '';
21423:         const { locale, symbol } = missionValueCurrencyMeta(hostname);
21424:         return `${symbol}${Math.round(amount).toLocaleString(locale)}`;
21425:     }
21426: 
21427:     function missionValueIdFromUrl(value, baseUrl = location.href) {
21428:         let pathname = String(value || '').trim();
21429:         if (!pathname) return null;
21430:         try { pathname = new URL(pathname, baseUrl).pathname; } catch (err) {}
21431:         const match = pathname.match(/\/missions\/(\d+)(?:\/|$)/u);
21432:         return match ? normaliseMissionId(match[1]) : null;
21433:     }
21434: 
21435:     function missionValueIdFromElement(root) {
21436:         if (!root) return null;
21437:         const doc = root.ownerDocument || document;
21438:         const directNodes = [root];
21439:         try {
21440:             directNodes.push(...root.querySelectorAll('[data-mission-id], [data-mission_id], input[name="mission_id"], input[name="mission[id]"]'));
21441:         } catch (err) {}
21442:         for (const node of directNodes) {
21443:             const candidates = [
21444:                 node?.dataset?.missionId,
21445:                 node?.dataset?.mission_id,
21446:                 node?.getAttribute?.('data-mission-id'),
21447:                 node?.getAttribute?.('data-mission_id'),
21448:                 node?.value
21449:             ];
21450:             for (const candidate of candidates) {
21451:                 const id = normaliseMissionId(candidate);
21452:                 if (id !== null) return id;
21453:             }
21454:             const idMatch = String(node?.id || '').match(/(?:^|_)(?:mission|mission_content|mission_panel)_(\d+)(?:$|_)/u);
21455:             if (idMatch) return normaliseMissionId(idMatch[1]);
21456:         }
21457: 
21458:         let routeNodes = [];
21459:         try {
21460:             routeNodes = Array.from(root.querySelectorAll('a[href*="/missions/"], form[action*="/missions/"], [data-url*="/missions/"], [data-href*="/missions/"]'));
21461:         } catch (err) {}
21462:         for (const node of routeNodes) {
21463:             for (const attribute of ['href', 'action', 'data-url', 'data-href']) {
21464:                 const id = missionValueIdFromUrl(node.getAttribute?.(attribute), doc.location?.href || location.href);
21465:                 if (id !== null) return id;
21466:             }
21467:         }
21468: 
21469:         if (doc !== document) {
21470:             try {
21471:                 const id = missionValueIdFromUrl(doc.location?.href, location.href);
21472:                 if (id !== null) return id;
21473:             } catch (err) {}
21474:         }
21475:         return null;
21476:     }
21477: 
21478:     function missionValueMountForRoot(root) {
21479:         if (!root) return null;
21480:         const selector = '.lightbox_content, .modal-body, #mission_content, .mission_content, [data-mission-content]';
21481:         try {
21482:             if (root.matches?.(selector)) return root;
21483:             return root.querySelector?.(selector) || root;
21484:         } catch (err) {
21485:             return root;
21486:         }
21487:     }
21488: 
21489:         function missionValueWindowCandidates() {
21490:         const discovered = [];
21491:         const add = root => {
21492:             if (!root?.isConnected) return;
21493:             const missionId = missionValueIdFromElement(root);
21494:             if (missionId === null) return;
21495:             const mount = missionValueMountForRoot(root);
21496:             if (!mount?.isConnected || mount.closest?.(`#${SCRIPT.panelId}, #${SCRIPT.helpCenterId}`)) return;
21497:             const toolbarSpacer = missionValueToolbarSpacer(root, mount);
21498:             const toolbar = missionValueToolbarBar(toolbarSpacer, root, mount);
21499:             discovered.push({ root, mount, missionId, toolbarSpacer, toolbar });
21500:         };
21501: 
21502:         transportSweepVisibleWindowRoots().forEach(add);
21503:         for (const context of transportSweepDocumentContexts()) {
21504:             observeMissionValueDocument(context.doc);
21505:             if (context.doc !== document) {
21506:                 try {
21507:                     if (missionValueIdFromUrl(context.doc.location?.href, location.href) !== null) add(context.doc.body);
21508:                 } catch (err) {}
21509:             }
21510:         }
21511:         return missionValuePreferredCandidates(discovered);
21512:     }
21513: 
21514:     function removeMissionValueRows(scope = document) {
21515:         try { scope.querySelectorAll?.('.mcms-mission-value-row').forEach(row => row.remove()); } catch (err) {}
21516:     }
21517: 
21518:     function clearMissionValueIndicators() {
21519:         for (const context of transportSweepDocumentContexts()) removeMissionValueRows(context.doc);
21520:     }
21521: 
21522: 
21523:         function missionValueToolbarSpacer(root, mount) {
21524:         const scopes = [root, mount].filter(Boolean);
21525:         for (const scope of scopes) {
21526:             try {
21527:                 if (scope.matches?.('#navbar-alarm-spacer')) return scope;
21528:                 const spacer = scope.querySelector?.('#navbar-alarm-spacer');
21529:                 if (spacer) return spacer;
21530:             } catch (err) {}
21531:         }
21532:         const doc = root?.ownerDocument || mount?.ownerDocument || null;
21533:         if (!doc || (root !== doc.body && mount !== doc.body)) return null;
21534:         try {
21535:             return missionValueIdFromUrl(doc.location?.href, location.href) !== null
21536:                 ? doc.getElementById?.('navbar-alarm-spacer') || null
21537:                 : null;
21538:         } catch (err) {
21539:             return null;
21540:         }
21541:     }
21542: 
21543:     function missionValueToolbarBar(spacer, root, mount) {
21544:         if (spacer?.isConnected) {
21545:             try {
21546:                 return spacer.closest?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || spacer.parentElement || null;
21547:             } catch (err) {}
21548:         }
21549:         for (const scope of [root, mount]) {
21550:             try {
21551:                 const bars = Array.from(scope?.querySelectorAll?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || []);
21552:                 const bar = bars.find(candidate => candidate.querySelector?.('#navbar-alarm-spacer'));
21553:                 if (bar) return bar;
21554:             } catch (err) {}
21555:         }
21556:         return null;
21557:     }
21558: 
21559:     function missionValueSpacerVisibleWidth(spacer) {
21560:         if (!spacer?.isConnected) return 0;
21561:         try {
21562:             const view = spacer.ownerDocument?.defaultView || pageWindow;
21563:             const style = view?.getComputedStyle?.(spacer);
21564:             if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse' || Number(style?.opacity) === 0) return 0;
21565:         } catch (err) {}
21566:         try {
21567:             const rect = spacer.getBoundingClientRect?.();
21568:             return rect && rect.width > 0 ? Math.max(0, Math.floor(rect.width)) : 0;
21569:         } catch (err) {
21570:             return 0;
21571:         }
21572:     }
21573: 
21574:     function missionValuePresentation(availableWidth, formatted) {
21575:         const width = Math.max(0, Number(availableWidth) || 0);
21576:         const value = String(formatted || '');
21577:         if (width >= 176) return { mode: 'full', text: `Mission Value · ${value}` };
21578:         if (width >= 110) return { mode: 'short', text: `Value · ${value}` };
21579:         if (width >= 58) return { mode: 'value', text: value };
21580:         return { mode: 'fallback', text: `Mission Value · ${value}` };
21581:     }
21582: 
21583:     function missionValuePreferredCandidates(candidateList) {
21584:         const groups = new Map();
21585:         for (const candidate of Array.from(candidateList || [])) {
21586:             const missionId = normaliseMissionId(candidate?.missionId);
21587:             if (missionId === null || !candidate?.mount?.isConnected) continue;
21588:             if (!groups.has(missionId)) groups.set(missionId, []);
21589:             groups.get(missionId).push(candidate);
21590:         }
21591:         const selected = [];
21592:         for (const group of groups.values()) {
21593:             const toolbarCandidates = group.filter(candidate => candidate.toolbarSpacer?.isConnected && candidate.toolbar?.isConnected);
21594:             const pool = toolbarCandidates.length ? toolbarCandidates : group;
21595:             const seenHosts = new Set();
21596:             for (const candidate of pool) {
21597:                 const host = candidate.toolbarSpacer?.isConnected ? candidate.toolbarSpacer : candidate.mount;
21598:                 if (!host || seenHosts.has(host)) continue;
21599:                 seenHosts.add(host);
21600:                 selected.push(candidate);
21601:             }
21602:         }
21603:         return selected;
21604:     }
21605: 
21606:     function missionValueCandidateScopes(candidate) {
21607:         const scopes = new Set([candidate?.root, candidate?.mount, candidate?.toolbarSpacer, candidate?.toolbar].filter(Boolean));
21608:         const doc = candidate?.root?.ownerDocument || candidate?.mount?.ownerDocument || null;
21609:         try {
21610:             const frame = doc?.defaultView?.frameElement || null;
21611:             if (frame) {
21612:                 scopes.add(frame);
21613:                 const frameWindow = frame.closest?.('#lightbox_box, #lightbox, .modal, [role="dialog"], .ui-dialog, .lightbox_content');
21614:                 if (frameWindow) scopes.add(frameWindow);
21615:             }
21616:         } catch (err) {}
21617:         return Array.from(scopes);
21618:     }
21619: 
21620:     function missionValueRowsForCandidate(candidate) {
21621:         const rows = new Set();
21622:         for (const scope of missionValueCandidateScopes(candidate)) {
21623:             try {
21624:                 if (scope.matches?.('.mcms-mission-value-row')) rows.add(scope);
21625:                 scope.querySelectorAll?.('.mcms-mission-value-row').forEach(row => rows.add(row));
21626:             } catch (err) {}
21627:         }
21628:         return Array.from(rows);
21629:     }
21630: 
21631:     function pruneMissionValueHostObservers(activeSpacers = null) {
21632:         for (const [spacer, record] of missionValueHostObservers) {
21633:             const keep = Boolean(spacer?.isConnected && record?.toolbar?.isConnected && (!activeSpacers || activeSpacers.has(spacer)));
21634:             if (keep) continue;
21635:             try { record?.resizeObserver?.disconnect?.(); } catch (err) {}
21636:             try { record?.mutationObserver?.disconnect?.(); } catch (err) {}
21637:             missionValueHostObservers.delete(spacer);
21638:         }
21639:     }
21640: 
21641:     function observeMissionValueHost(candidate) {
21642:         const spacer = candidate?.toolbarSpacer;
21643:         const toolbar = candidate?.toolbar;
21644:         if (!spacer?.isConnected || !toolbar?.isConnected) return;
21645:         const existing = missionValueHostObservers.get(spacer);
21646:         if (existing?.toolbar === toolbar) return;
21647:         if (existing) {
21648:             try { existing.resizeObserver?.disconnect?.(); } catch (err) {}
21649:             try { existing.mutationObserver?.disconnect?.(); } catch (err) {}
21650:         }
21651:         const view = spacer.ownerDocument?.defaultView || pageWindow;
21652:         const ResizeObserverCtor = view?.ResizeObserver || pageWindow.ResizeObserver;
21653:         const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
21654:         const record = { toolbar, resizeObserver: null, mutationObserver: null };
21655:         if (typeof ResizeObserverCtor === 'function') {
21656:             record.resizeObserver = runtimeTrackObserver(new ResizeObserverCtor(() => scheduleMissionValueScan(24)));
21657:             record.resizeObserver.observe(spacer);
21658:         }
21659:         if (typeof MutationObserverCtor === 'function') {
21660:             record.mutationObserver = runtimeTrackObserver(new MutationObserverCtor(() => scheduleMissionValueScan(24)));
21661:             record.mutationObserver.observe(toolbar, { childList: true, subtree: false });
21662:         }
21663:         missionValueHostObservers.set(spacer, record);
21664:     }
21665: 
21666:     
21667: 
21668:     
21669: 
21670:         function syncMissionValueCandidate(candidate) {
21671:         const { mount, missionId, toolbarSpacer, toolbar } = candidate || {};
21672:         if (!mount?.isConnected || missionId === null) return null;
21673:         const marker = getMissionMarkerIndex().byId.get(missionId) || getMissionMarkerIndex().byId.get(String(missionId)) || null;
21674:         const snapshot = liveMissionSnapshots.get(missionId) || liveMissionSnapshots.get(String(missionId)) || missionSnapshotCache.get(missionId) || missionSnapshotCache.get(String(missionId)) || null;
21675:         const details = criticalMissionValueDetails({ missionId, marker, snapshot });
21676:         const formatted = formatMissionWindowValue(details.value);
21677:         const existingRows = missionValueRowsForCandidate(candidate);
21678:         if (!formatted) {
21679:             existingRows.forEach(row => row.remove());
21680:             return null;
21681:         }
21682: 
21683:         observeMissionValueHost(candidate);
21684:         const availableWidth = missionValueSpacerVisibleWidth(toolbarSpacer);
21685:         const presentation = missionValuePresentation(availableWidth, formatted);
21686:         const useToolbar = Boolean(toolbarSpacer?.isConnected && toolbar?.isConnected && presentation.mode !== 'fallback');
21687:         const targetDocument = (useToolbar ? toolbarSpacer.ownerDocument : mount.ownerDocument) || document;
21688:         let row = null;
21689:         if (useToolbar) {
21690:             row = existingRows.find(candidateRow => candidateRow.parentNode === toolbarSpacer) || null;
21691:         } else if (toolbar?.parentNode) {
21692:             row = existingRows.find(candidateRow => candidateRow.parentNode === toolbar.parentNode && candidateRow.previousElementSibling === toolbar) || null;
21693:         }
21694:         row ||= existingRows.find(candidateRow => candidateRow.ownerDocument === targetDocument) || null;
21695:         existingRows.forEach(candidateRow => {
21696:             if (candidateRow !== row) candidateRow.remove();
21697:         });
21698:         if (!row) row = targetDocument.createElement('div');
21699:         row.className = 'mcms-mission-value-row';
21700:         row.setAttribute('data-mcms-mission-value', 'true');
21701:         row.dataset.mcmsMissionId = String(missionId);
21702:         row.dataset.mcmsHost = useToolbar ? 'toolbar' : 'fallback';
21703:         row.dataset.mcmsMode = useToolbar ? presentation.mode : 'fallback';
21704: 
21705:         let badges = [];
21706:         try { badges = Array.from(row.querySelectorAll('.mcms-mission-value-badge')); } catch (err) {}
21707:         const badge = badges.shift() || targetDocument.createElement('span');
21708:         badges.forEach(extra => extra.remove());
21709:         badge.className = 'mcms-mission-value-badge';
21710:         if (badge.parentNode !== row) row.appendChild(badge);
21711: 
21712:         if (useToolbar) {
21713:             if (row.parentNode !== toolbarSpacer) toolbarSpacer.appendChild(row);
21714:         } else if (toolbar?.parentNode) {
21715:             if (row.parentNode !== toolbar.parentNode || row.previousElementSibling !== toolbar) {
21716:                 toolbar.parentNode.insertBefore(row, toolbar.nextSibling);
21717:             }
21718:         } else if (row.parentNode !== mount || row !== mount.firstElementChild) {
21719:             mount.insertBefore(row, mount.firstChild || null);
21720:         }
21721: 
21722:         const fullLabel = `Mission Value · ${formatted}`;
21723:         const text = useToolbar ? presentation.text : fullLabel;
21724:         if (badge.textContent !== text) badge.textContent = text;
21725:         badge.title = `${fullLabel} · ${details.source}`;
21726:         badge.setAttribute('aria-label', fullLabel);
21727:         row.setAttribute('aria-label', fullLabel);
21728:         return row;
21729:     }
21730: 
21731:     function scheduleMissionValueScan(delay = 80) {
21732:         runtimeClearTimeout(missionValueScanTimer);
21733:         missionValueScanTimer = runtimeSetTimeout(() => {
21734:             missionValueScanTimer = null;
21735:             scanMissionValueWindows();
21736:         }, Math.max(0, Number(delay) || 0));
21737:     }
21738: 
21739:         function scanMissionValueWindows() {
21740:         if (!state.missionValue) {
21741:             clearMissionValueIndicators();
21742:             pruneMissionValueHostObservers(new Set());
21743:             return;
21744:         }
21745:         let needsRetry = false;
21746:         const activeRows = new Set();
21747:         const activeSpacers = new Set();
21748:         for (const candidate of missionValueWindowCandidates()) {
21749:             if (candidate.toolbarSpacer?.isConnected) activeSpacers.add(candidate.toolbarSpacer);
21750:             const renderedRow = syncMissionValueCandidate(candidate);
21751:             if (renderedRow) {
21752:                 activeRows.add(renderedRow);
21753:                 missionValueRetryState.delete(candidate.mount);
21754:                 continue;
21755:             }
21756:             const previous = missionValueRetryState.get(candidate.mount);
21757:             const attempts = previous?.missionId === candidate.missionId ? previous.attempts : 0;
21758:             if (attempts < 3) {
21759:                 missionValueRetryState.set(candidate.mount, { missionId: candidate.missionId, attempts: attempts + 1 });
21760:                 needsRetry = true;
21761:             }
21762:         }
21763:         for (const context of transportSweepDocumentContexts()) {
21764:             try {
21765:                 context.doc.querySelectorAll?.('.mcms-mission-value-row').forEach(row => {
21766:                     if (!activeRows.has(row)) row.remove();
21767:                 });
21768:             } catch (err) {}
21769:         }
21770:         pruneMissionValueHostObservers(activeSpacers);
21771:         if (needsRetry) runtimeSetTimeout(() => scheduleMissionValueScan(0), 650);
21772:     }
21773: 
21774:         function ensureMissionValueDocumentStyle(doc) {
21775:         if (!doc || doc === document) return;
21776:         const styleId = 'mcms-mission-value-document-style';
21777:         if (doc.getElementById?.(styleId)) return;
21778:         const style = doc.createElement?.('style');
21779:         if (!style) return;
21780:         style.id = styleId;
21781:         style.textContent = `
21782:             .mcms-mission-value-row{display:flex!important;align-items:center!important;justify-content:flex-end!important;min-width:0!important;box-sizing:border-box!important;position:relative!important;z-index:2!important;pointer-events:none!important}
21783:             #navbar-alarm-spacer>.mcms-mission-value-row,.mcms-mission-value-row[data-mcms-host="toolbar"]{flex:1 1 auto!important;width:100%!important;min-height:32px!important;margin:0!important;padding:0 3px 0 6px!important;clear:none!important;overflow:hidden!important}
21784:             .mcms-mission-value-row[data-mcms-host="fallback"]{width:100%!important;min-height:30px!important;margin:0 0 6px 0!important;padding:4px 8px!important;clear:both!important;overflow:hidden!important}
21785:             .mcms-mission-value-badge{display:inline-flex!important;align-items:center!important;justify-content:center!important;max-width:100%!important;min-width:0!important;min-height:24px!important;box-sizing:border-box!important;padding:4px 9px!important;border:1px solid rgba(235,190,64,.72)!important;border-radius:8px!important;background:linear-gradient(145deg,rgba(48,39,13,.96),rgba(19,21,24,.96))!important;color:#ffe59a!important;box-shadow:0 2px 8px rgba(0,0,0,.34)!important;font:900 11px/1.2 Arial,Helvetica,sans-serif!important;letter-spacing:.15px!important;text-align:right!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;pointer-events:none!important}
21786:             .mcms-mission-value-row[data-mcms-mode="value"] .mcms-mission-value-badge{padding-left:7px!important;padding-right:7px!important}
21787:             @media(max-width:767px){.mcms-mission-value-row[data-mcms-host="fallback"]{padding:4px 6px!important}.mcms-mission-value-badge{font-size:10px!important}}
21788:         `;
21789:         (doc.head || doc.documentElement)?.appendChild(style);
21790:     }
21791: 
21792:     function clearMissionValueDocumentStyles() {
21793:         for (const context of transportSweepDocumentContexts()) {
21794:             if (context.doc === document) continue;
21795:             try { context.doc.getElementById?.('mcms-mission-value-document-style')?.remove(); } catch (err) {}
21796:         }
21797:     }
21798: 
21799:     function observeMissionValueFrame(frame) {
21800:         if (!frame || missionValueObservedFrames.has(frame)) return;
21801:         missionValueObservedFrames.add(frame);
21802:         const onLoad = () => scheduleMissionValueScan(40);
21803:         frame.addEventListener('load', onLoad);
21804:         runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
21805:     }
21806: 
21807:         function observeMissionValueDocument(doc) {
21808:         if (!doc) return;
21809:         ensureMissionValueDocumentStyle(doc);
21810:         if (missionValueObservedDocuments.has(doc)) return;
21811:         missionValueObservedDocuments.add(doc);
21812:         let frames = [];
21813:         try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
21814:         frames.forEach(observeMissionValueFrame);
21815:         const root = doc.documentElement || doc.body;
21816:         if (!root) return;
21817:         const activitySelector = '#lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame, a[href*="/missions/"], form[action*="/missions/"], #navbar-alarm-spacer, #navbar-right-help-button, [id^="lssmv4-shareAlliancePost_alarm"], .navbar-header';
21818:         const observer = runtimeTrackObserver(new MutationObserver(mutations => {
21819:             const relevant = mutations.some(mutation => Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(node => {
21820:                 if (node?.nodeType !== 1) return false;
21821:                 if (node.matches?.(activitySelector)) return true;
21822:                 return Boolean(node.querySelector?.(activitySelector));
21823:             }));
21824:             if (!relevant) return;
21825:             try { doc.querySelectorAll('iframe, frame').forEach(observeMissionValueFrame); } catch (err) {}
21826:             scheduleMissionValueScan(50);
21827:         }));
21828:         observer.observe(root, { childList: true, subtree: true });
21829:     }
21830: 
21831:     function installMissionValueWindows() {
21832:         if (!missionValueFeatureInstalled) {
21833:             missionValueFeatureInstalled = true;
21834:             runtimeOnCleanup(() => {
21835:                 runtimeClearTimeout(missionValueScanTimer);
21836:                 missionValueScanTimer = null;
21837:                 clearMissionValueIndicators();
21838:                 clearMissionValueDocumentStyles();
21839:             });
21840:         }
21841:         for (const context of transportSweepDocumentContexts()) observeMissionValueDocument(context.doc);
21842:         scheduleMissionValueScan(0);
21843:         runtimeSetTimeout(() => scheduleMissionValueScan(0), 180);
21844:         runtimeSetTimeout(() => scheduleMissionValueScan(0), 800);
21845:     }
21846: 
21847:     function criticalMissionValueForEntry(entry) {
21848:         return criticalMissionValueDetails(entry).value;
21849:     }
21850: 
21851:     function criticalValueEligible(entry) {
21852:         return selectedCriticalValueMode() === 'total' || Boolean(entry?.eligibleForCredits);
21853:     }
21854: 
21855:     function criticalValueGroup(entries, predicate = () => true) {
21856:         let total = 0;
21857:         let known = 0;
21858:         let unknown = 0;
21859:         let eligible = 0;
21860:         const seenMissionIds = new Set();
21861:         const sources = new Map();
21862:         for (const entry of entries) {
21863:             if (!predicate(entry) || !criticalValueEligible(entry)) continue;
21864:             const missionId = normaliseMissionId(entry?.missionId);
21865:             if (missionId !== null && seenMissionIds.has(missionId)) continue;
21866:             if (missionId !== null) seenMissionIds.add(missionId);
21867:             if (entry?.eligibleForCredits) eligible += 1;
21868:             const details = criticalMissionValueDetails(entry);
21869:             const value = details.value;
21870:             if (value === null || !Number.isFinite(Number(value))) {
21871:                 unknown += 1;
21872:                 continue;
21873:             }
21874:             total += Math.max(0, Number(value) || 0);
21875:             known += 1;
21876:             sources.set(details.source, (sources.get(details.source) || 0) + 1);
21877:         }
21878:         return { total: Math.round(total), known, unknown, eligible, count: seenMissionIds.size, sources };
21879:     }
21880: 
21881:     function criticalValueDisplay(group) {
21882:         if (!group?.known) return 'UNKNOWN';
21883:         return `≈${formatOperationalCompactCredits(group.total)} CR`;
21884:     }
21885: 
21886:     function criticalValueCoverage(group) {
21887:         return `${group.known.toLocaleString('en-GB')} / ${(group.known + group.unknown).toLocaleString('en-GB')} valued`;
21888:     }
21889: 
21890:     function criticalValueTitle(label, group) {
21891:         const knownText = `${group.known.toLocaleString('en-GB')} valued mission${group.known === 1 ? '' : 's'}`;
21892:         const unknownText = group.unknown ? ` · ${group.unknown.toLocaleString('en-GB')} value${group.unknown === 1 ? '' : 's'} unavailable` : '';
21893:         return `${label}: approximately ${group.total.toLocaleString('en-GB')} credits from MissionChief average-credit data · ${knownText}${unknownText}`;
21894:     }
21895: 
21896:     function criticalValuesHtml(allEntries, visibleEntries) {
21897:         const scopedEntries = visibleEntries;
21898:         const noScene = criticalValueGroup(scopedEntries, entry => Boolean(entry?.units?.known) && Math.max(0, Number(entry?.units?.onScene) || 0) === 0);
21899:         const assistance = criticalValueGroup(scopedEntries, entry => criticalEntryPrimaryStatus(entry) === 'assistance');
21900:         const visible = criticalValueGroup(scopedEntries);
21901:         const mode = selectedCriticalValueMode();
21902:         const showingText = `${mode === 'eligible' ? 'Eligible' : 'Total'} MissionChief average credits for ${visibleEntries.length.toLocaleString('en-GB')} currently visible mission${visibleEntries.length === 1 ? '' : 's'}`;
21903:         const valueCard = (className, label, group) => `<div class="mcms-critical-value-card ${className}" title="${escapeHtml(criticalValueTitle(label, group))}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(criticalValueDisplay(group))}</strong><small>${escapeHtml(criticalValueCoverage(group))}</small></div>`;
21904:         return `
21905:             <div class="mcms-critical-values-label" title="${escapeHtml(showingText)}"><strong>MISSION</strong><span>VALUE</span></div>
21906:             <div class="mcms-critical-value-mode" role="group" aria-label="Mission value mode">
21907:                 <button type="button" data-critical-value-mode="total" class="${mode === 'total' ? 'mcms-filter-active' : ''}" aria-pressed="${mode === 'total'}">TOTAL</button>
21908:                 <button type="button" data-critical-value-mode="eligible" class="${mode === 'eligible' ? 'mcms-filter-active' : ''}" aria-pressed="${mode === 'eligible'}">ELIGIBLE</button>
21909:             </div>
21910:             <div class="mcms-critical-values-grid">
21911:                 ${valueCard('mcms-value-no-scene', 'No Scene', noScene)}
21912:                 ${valueCard('mcms-value-assistance', 'Assistance', assistance)}
21913:                 ${valueCard('mcms-value-all', 'Visible Value', visible)}
21914:             </div>
21915:             <span class="mcms-critical-showing">SHOWING ${visibleEntries.length.toLocaleString('en-GB')} OF ${allEntries.length.toLocaleString('en-GB')} MISSIONS</span>`;
21916:     }
21917: 
21918:     function criticalSummaryHtml(allEntries) {
21919:         const baseForStatus = criticalFilterEntries(allEntries, ['status']);
21920:         const baseForOnWay = criticalFilterEntries(allEntries, ['onway']);
```

## Control events, createPanel markup, Ops controls and updateUI

Canonical lines 27800–29240

```javascript
27800: 
27801:         return helpGuideLoadPromise;
27802:     }
27803: 
27804:     function patchHelpGuideDocument(documentText) {
27805:         let source = String(documentText || '');
27806:         source = source
27807:             .replace(/Guide for Toolkit v\d+\.\d+\.\d+/u, `Guide for Toolkit v${HELP_CENTER.guideVersion}`)
27808:             .replace(/Help Centre for v\d+\.\d+\.\d+/u, `Help Centre for v${HELP_CENTER.guideVersion}`)
27809:             .replace(
27810:                 '<div class="card"><h3>Umbrella</h3><p>Sterile biohazard command styling with classified containment panels.</p></div>',
27811:                 '<div class="card"><h3>Umbrella Containment</h3><p>Corporate BSL-4 command styling with original transparent emblem, facility schematic, surveillance terminal, specimen vial and containment-division artwork.</p></div>'
27812:             )
27813:             .replace('Biohazard Containment</span>', 'Umbrella Containment</span>')
27814:             .replace(
27815:                 'Set a minimum payout threshold, duration, theme, audio state and volume. Use the test amount control before relying on a new setup.',
27816:                 'Set a minimum payout threshold, duration, theme, audio state and volume. Umbrella Containment uses the same identity, artwork package and renamed hosted audio as the Umbrella UI theme. Use the test amount control before relying on a new setup.'
27817:             )
27818:             .replace(
27819:                 '<li>Presentation titles and particle treatment scale by payout tier.</li>',
27820:                 '<li>Presentation titles and particle treatment scale by payout tier.</li><li>Umbrella Containment displays BSL-4 facility, surveillance, corporate emblem and transfer-authorisation artwork.</li>'
27821:             );
27822:         const semanticMarker = '<div class="callout warning"><strong>Protected semantic colours:</strong> clearing, assistance, warning, critical and syncing states retain their operational meaning across every theme.</div>';
27823:         if (!source.includes('Umbrella Containment asset package:') && source.includes(semanticMarker)) {
27824:             source = source.replace(
27825:                 semanticMarker,
27826:                 '<div class="callout"><strong>Umbrella Containment asset package:</strong> decorative artwork is loaded from the public Toolkit assets repository only while the theme is in use. Missing artwork never blocks the Toolkit, and the graphics do not replace protected operational colours.</div>' + semanticMarker
27827:             );
27828:         }
27829:         if (!source.includes('id="financial-command"')) {
27830:             const financialSection = `<section class="section" id="financial-command" data-title="Discord Financial Command" data-keywords="discord finance archive ledger audit github rules policy deep scan forecast risk capital investment webhook">
27831: <div class="head"><span class="num">19</span><div><h2>Discord Financial Command</h2><p class="summary">Maximum-range MissionChief ledger extraction, local historical archiving and GitHub-hosted financial intelligence.</p></div></div>
27832: <h3>Supreme financial audit</h3><p>The Discord tab can generate an Executive Brief or a complete Executive + Full Audit report. The audit separates operating income, other income, operating expenditure and capital investment so expansion spending does not automatically make healthy operations look unprofitable.</p>
27833: <div class="grid"><div class="card"><h4>Financial scorecard</h4><p>Revenue, operating efficiency, liquidity, growth investment and audit confidence are scored independently.</p></div><div class="card"><h4>Risk intelligence</h4><p>Highlights revenue contraction, concentration, aggressive investment, reserve drawdown, low runway and incomplete classification.</p></div><div class="card"><h4>Deep ledger scan</h4><p>All Available History reads every MissionChief credit-ledger page accessible to the account, with retries, progress reporting, safe cancellation and local checkpoint storage.</p></div><div class="card"><h4>GitHub intelligence</h4><p>Classification rules and audit thresholds are downloaded from the public Toolkit assets repository and cached locally. No player ledger or webhook data is uploaded.</p></div></div>
27834: <h3>Player-linked Local Financial Archive</h3><ol class="steps"><li>Keep Local Financial Archive enabled to retain discovered transactions by MissionChief player ID/name.</li><li>Select All Available History or run Deep Scan All Available to extend the archive as far back as MissionChief exposes.</li><li>Use Export Archive and Import Archive to transfer or merge history between your devices without exposing repository credentials.</li><li>Export All also includes the local archive and Discord webhook for complete private recovery.</li><li>GitHub hosts only public rules, audit policy and Toolkit assets; player financial data remains in the browser and private backups.</li></ol>
27835: <div class="call warn"><strong>Private backup:</strong> Export All includes the saved Discord webhook and local financial history. Store the JSON privately; anyone holding it may be able to post through the webhook and inspect the exported game ledger.</div>
27836: </section>`;
27837:             source = source.replace('</main>', `${financialSection}</main>`);
27838:         }
27839:         if (!source.includes('id="economy-mode"')) {
27840:             const economySection = `<section class="section" id="economy-mode" data-title="Economy Mode" data-keywords="economy eco performance low end laptop ram cpu gpu lag leaflet markers">
27841: <div class="head"><span class="num">20</span><div><h2>Economy Mode</h2><p class="summary">A reversible lower-overhead operating policy for large maps and lower-end computers.</p></div></div>
27842: <p>Use the leaf button beside the Toolkit opener to switch Economy Mode on or off. Your normal themes, overlays and feature selections remain saved; Economy Mode temporarily renders and refreshes them more efficiently.</p>
27843: <div class="grid"><div class="card"><h4>Map workload</h4><p>Off-screen vehicle and building layers are detached with a safety buffer, then restored automatically when they enter the current map area or Economy Mode is disabled.</p></div><div class="card"><h4>Rendering</h4><p>Continuous decorative animation, tile-filter chains, backdrop blur and heavy payout particles are replaced by static equivalents while operational colours remain intact.</p></div><div class="card"><h4>Background work</h4><p>Mission, vehicle, building and maintenance refreshes use longer idle intervals. Opening a module, changing a setting or pressing Refresh still requests current data immediately.</p></div><div class="card"><h4>Large panels</h4><p>Mission Age Watch and long MissionChief lists use browser rendering containment so off-screen rows do not require full layout and painting.</p></div></div>
27844: <div class="call"><strong>Full restoration:</strong> switching Economy Mode off reattaches quarantined layers, restores Leaflet options, map skins, animation and normal scheduler intervals.</div>
27845: </section>`;
27846:             source = source.replace('</main>', `${economySection}</main>`);
27847:         }
27848:         return source;
27849:     }
27850: 
27851:     function protectHelpGuideDocument(documentText) {
27852:         const navigationGuard = `
27853: <script data-mcms-help-navigation-guard>
27854: (() => {
27855:     'use strict';
27856:     const scrollToGuideSection = rawHref => {
27857:         const href = String(rawHref || '');
27858:         if (!href.startsWith('#')) return false;
27859:         let id = '';
27860:         try { id = decodeURIComponent(href.slice(1)); } catch (error) { id = href.slice(1); }
27861:         const target = id ? document.getElementById(id) : document.documentElement;
27862:         if (!target) return true;
27863:         const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
27864:         target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
27865:         return true;
27866:     };
27867:     document.addEventListener('click', event => {
27868:         const link = event.target instanceof Element ? event.target.closest('a[href]') : null;
27869:         if (!link) return;
27870:         const href = link.getAttribute('href') || '';
27871:         if (href.startsWith('#')) {
27872:             event.preventDefault();
27873:             scrollToGuideSection(href);
27874:             return;
27875:         }
27876:         if (/^(?:https?:)?\/\//i.test(href)) {
27877:             event.preventDefault();
27878:             try { window.open(href, '_blank', 'noopener,noreferrer'); } catch (error) {}
27879:         }
27880:     }, true);
27881: })();
27882: \x3C/script>`;
27883:         const source = patchHelpGuideDocument(documentText);
27884:         if (source.includes('data-mcms-help-navigation-guard')) return source;
27885:         if (/<\/body\s*>/iu.test(source)) return source.replace(/<\/body\s*>/iu, `${navigationGuard}</body>`);
27886:         return `${source}${navigationGuard}`;
27887:     }
27888: 
27889:     function createHelpCenter() {
27890:         const existing = document.getElementById(SCRIPT.helpCenterId);
27891:         if (existing) return existing;
27892:         const overlay = document.createElement('div');
27893:         overlay.id = SCRIPT.helpCenterId;
27894:         overlay.setAttribute('role', 'dialog');
27895:         overlay.setAttribute('aria-modal', 'true');
27896:         overlay.setAttribute('aria-label', `${SCRIPT.name} Help Centre`);
27897:         overlay.setAttribute('aria-hidden', 'true');
27898:         overlay.innerHTML = `
27899:             <div class="mcms-help-window" role="document">
27900:                 <div class="mcms-help-toolbar">
27901:                     <div class="mcms-help-brand">
27902:                         <span class="mcms-help-brand-icon" aria-hidden="true">?</span>
27903:                         <span class="mcms-help-brand-copy"><strong>Toolkit Help Centre</strong><small>Searchable guide · hosted on the public Toolkit assets repository</small></span>
27904:                     </div>
27905:                     <div class="mcms-help-actions">
27906:                         <button class="mcms-help-action" type="button" data-help-action="reload" title="Reload the latest guide" aria-label="Reload the latest guide">↻</button>
27907:                         <button class="mcms-help-action mcms-help-source" type="button" data-help-action="source" title="Open the guide source on GitHub" aria-label="Open the guide source on GitHub">↗</button>
27908:                         <button class="mcms-help-action mcms-help-close" type="button" data-help-action="close" title="Close Help Centre" aria-label="Close Help Centre">×</button>
27909:                     </div>
27910:                 </div>
27911:                 <div class="mcms-help-address"><span class="mcms-help-address-lock" aria-hidden="true">●</span><span class="mcms-help-address-text">github.com/Conroy1988/missionchief-toolkit-assets/help/index.html</span><span class="mcms-help-status" data-help-status>Ready</span></div>
27912:                 <div class="mcms-help-progress" aria-hidden="true"></div>
27913:                 <div class="mcms-help-content">
27914:                     <iframe class="mcms-help-frame" title="MissionChief Map Command Toolkit searchable guide" sandbox="allow-scripts allow-popups" referrerpolicy="no-referrer"></iframe>
27915:                     <div class="mcms-help-fallback">
27916:                         <div class="mcms-help-error-card">
27917:                             <strong>Help Centre unavailable</strong>
27918:                             <p data-help-error>The public guide could not be loaded. The main Toolkit remains fully operational.</p>
27919:                             <div class="mcms-help-error-actions"><button type="button" data-help-action="reload">Retry</button><button type="button" data-help-action="source">Open GitHub source</button></div>
27920:                         </div>
27921:                     </div>
27922:                 </div>
27923:             </div>`;
27924: 
27925:         runtimeListen(overlay, 'click', event => {
27926:             const actionButton = closestEventTarget(event, '[data-help-action]');
27927:             if (actionButton) {
27928:                 event.preventDefault();
27929:                 const action = actionButton.dataset.helpAction;
27930:                 if (action === 'close') closeHelpCenter();
27931:                 if (action === 'reload') loadHelpCenterGuide(true);
27932:                 if (action === 'source') {
27933:                     try { pageWindow.open(HELP_CENTER.sourceUrl, '_blank', 'noopener,noreferrer'); } catch (err) { location.href = HELP_CENTER.sourceUrl; }
27934:                 }
27935:                 return;
27936:             }
27937:             if (event.target === overlay) closeHelpCenter();
27938:         });
27939:         runtimeListen(overlay, 'mousedown', stopMapInteraction);
27940:         runtimeListen(overlay, 'wheel', stopMapInteraction, { passive: true });
27941:         runtimeListen(overlay, 'touchstart', stopMapInteraction, { passive: true });
27942:         document.body.appendChild(overlay);
27943:         return overlay;
27944:     }
27945: 
27946:     async function loadHelpCenterGuide(force = false) {
27947:         const overlay = createHelpCenter();
27948:         const frame = overlay.querySelector('.mcms-help-frame');
27949:         const status = overlay.querySelector('[data-help-status]');
27950:         const errorText = overlay.querySelector('[data-help-error]');
27951:         overlay.classList.add('mcms-loading');
27952:         overlay.classList.remove('mcms-error');
27953:         if (status) status.textContent = force ? 'Refreshing…' : 'Loading…';
27954:         try {
27955:             const documentText = await requestHelpGuideDocument(force);
27956:             if (!overlay.isConnected || runtime.destroyed) return false;
27957:             frame.srcdoc = protectHelpGuideDocument(documentText);
27958:             overlay.classList.remove('mcms-error');
27959:             if (status) status.textContent = `Guide ${HELP_CENTER.guideVersion} · online`;
27960:             return true;
27961:         } catch (err) {
27962:             if (!overlay.isConnected || runtime.destroyed) return false;
27963:             overlay.classList.add('mcms-error');
27964:             if (status) status.textContent = 'Offline fallback';
27965:             if (errorText) errorText.textContent = `${err?.message || 'The public guide could not be loaded.'} The main Toolkit remains fully operational.`;
27966:             return false;
27967:         } finally {
27968:             overlay.classList.remove('mcms-loading');
27969:         }
27970:     }
27971: 
27972:     function openHelpCenter() {
27973:         const overlay = createHelpCenter();
27974:         helpCenterReturnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
27975:         closePanel();
27976:         overlay.classList.add('mcms-open');
27977:         overlay.setAttribute('aria-hidden', 'false');
27978:         document.documentElement.setAttribute('data-mcms-help-open', 'true');
27979:         const closeButton = overlay.querySelector('[data-help-action="close"]');
27980:         runtimeSetTimeout(() => { try { closeButton?.focus({ preventScroll: true }); } catch (err) {} }, 0);
27981:         const frame = overlay.querySelector('.mcms-help-frame');
27982:         if (!frame?.srcdoc) loadHelpCenterGuide(false);
27983:         else {
27984:             const status = overlay.querySelector('[data-help-status]');
27985:             if (status) status.textContent = helpGuideLoadedAt ? `Guide ${HELP_CENTER.guideVersion} · cached` : `Guide ${HELP_CENTER.guideVersion}`;
27986:         }
27987:     }
27988: 
27989:     function stopMapInteraction(event) {
27990:         event.stopPropagation();
27991:     }
27992: 
27993:     function isTypingTarget(target) {
27994:         if (!target) return false;
27995:         const tag = String(target.tagName || '').toLowerCase();
27996:         return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable;
27997:     }
27998: 
27999:     function handleKeyboard(event) {
28000:         if (event.key === 'Escape' && closeHelpCenter()) { event.preventDefault(); return; }
28001:         if (event.key === 'Escape' && closeCriticalViewControls()) { event.preventDefault(); return; }
28002:         if (event.key === 'Escape') {
28003:             const hadOpenUi = Boolean(
28004:                 document.getElementById(SCRIPT.panelId)?.classList.contains('mcms-open') ||
28005:                 document.getElementById(SCRIPT.criticalDrawerId)?.classList.contains('mcms-open') ||
28006:                 document.getElementById(SCRIPT.vehicleStatusId)?.classList.contains('mcms-open')
28007:             );
28008:             if (state.cleanMode && state.shortcuts) toggleFeature('clean');
28009:             closePanel({ restoreFocus: hadOpenUi });
28010:             closeCriticalDrawer();
28011:             closeVehicleCodeStatus();
28012:             if (hadOpenUi) event.preventDefault();
28013:             return;
28014:         }
28015:         if (!state.shortcuts || isTypingTarget(event.target)) return;
28016:         const key = String(event.key || '').toLowerCase();
28017:         if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'm') { event.preventDefault(); togglePanel(); return; }
28018:         if (!event.ctrlKey && !event.altKey && !event.metaKey && !event.repeat && /^[1-9]$/.test(event.key)) {
28019:             const visibilityShortcut = {
28020:                 '1': 'myMissions',
28021:                 '2': 'allianceMissions',
28022:                 '3': 'vehicles',
28023:                 '4': 'buildings',
28024:                 '5': 'allianceCredits',
28025:                 '6': 'missionAge',
28026:                 '7': 'transportWatcher',
28027:                 '8': 'unitCommitment',
28028:                 '9': 'criticalView'
28029:             };
28030:             event.preventDefault();
28031:             toggleFeature(visibilityShortcut[event.key]);
28032:             return;
28033:         }
28034:         if (!event.ctrlKey && !event.altKey && !event.metaKey && !event.repeat && key === 'v') { event.preventDefault(); toggleVehicleCodeStatus(); return; }
28035:         if (!event.ctrlKey && !event.altKey && !event.metaKey && !event.repeat && key === 'w') { event.preventDefault(); toggleCriticalDrawer(); return; }
28036:         if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'c') { event.preventDefault(); toggleFeature('clean'); return; }
28037:         if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'f') { event.preventDefault(); toggleFeature('markerFocus'); return; }
28038:         if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'p') { event.preventDefault(); toggleFeature('missionPulse'); return; }
28039:         if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'r') { event.preventDefault(); toggleFeature('roadPriority'); }
28040:     }
28041: 
28042:     function buildThemeOptions(selected) {
28043:         return THEME_ORDER.map(key => `<option value="${key}" ${key === selected ? 'selected' : ''}>${THEMES[key].full}</option>`).join('');
28044:     }
28045: 
28046:     function makeToggleButton(key, icon, label, title) {
28047:         return `
28048:             <button class="mcms-toggle-btn" type="button" data-toggle="${key}" title="${escapeHtml(title || label)}">
28049:                 <span class="mcms-iconbox">${icon}</span>
28050:                 <span class="mcms-text">
28051:                     <span class="mcms-label">${escapeHtml(label)}</span>
28052:                     <span class="mcms-pill">OFF</span>
28053:                 </span>
28054:             </button>
28055:         `;
28056:     }
28057: 
28058:     function makeFloatButton(key, shortcut, label, title, tabletLabel = label, mobileLabel = tabletLabel) {
28059:         return `
28060:             <button class="mcms-float-btn" type="button" data-toggle="${key}" title="${escapeHtml(title)}" aria-pressed="false">
28061:                 <span class="mcms-float-key">${escapeHtml(shortcut)}</span>
28062:                 <span class="mcms-float-label mcms-float-label-desktop">${escapeHtml(label)}</span>
28063:                 <span class="mcms-float-label mcms-float-label-tablet">${escapeHtml(tabletLabel)}</span>
28064:                 <span class="mcms-float-label mcms-float-label-mobile">${escapeHtml(mobileLabel)}</span>
28065:             </button>
28066:         `;
28067:     }
28068: 
28069:     function makeActionFloatButton(action, shortcut, label, title, tabletLabel = label, mobileLabel = tabletLabel) {
28070:         return `
28071:             <button class="mcms-float-btn mcms-float-action-btn" type="button" data-action="${escapeHtml(action)}" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}" aria-keyshortcuts="${escapeHtml(shortcut)}" aria-pressed="false">
28072:                 <span class="mcms-float-key">${escapeHtml(shortcut)}</span>
28073:                 <span class="mcms-float-label mcms-float-label-desktop">${escapeHtml(label)}</span>
28074:                 <span class="mcms-float-label mcms-float-label-tablet">${escapeHtml(tabletLabel)}</span>
28075:                 <span class="mcms-float-label mcms-float-label-mobile">${escapeHtml(mobileLabel)}</span>
28076:             </button>
28077:         `;
28078:     }
28079: 
28080:     function createCleanExit() {
28081:         if (document.getElementById(SCRIPT.cleanExitId)) return;
28082:         const button = document.createElement('button');
28083:         button.id = SCRIPT.cleanExitId;
28084:         button.type = 'button';
28085:         button.textContent = 'Exit Clean Mode';
28086:         button.title = 'Exit clean mode. Shortcut: C or Esc.';
28087:         button.addEventListener('click', () => toggleFeature('clean'));
28088:         document.body.appendChild(button);
28089:     }
28090: 
28091:     function createControl(mapEl) {
28092:         if (!mapEl || document.getElementById(SCRIPT.controlId)) return;
28093:         const control = document.createElement('div');
28094:         control.id = SCRIPT.controlId;
28095:         control.className = 'mcms-control';
28096:         control.setAttribute('aria-label', `${SCRIPT.name} control`);
28097:         control.innerHTML = `
28098:             <div class="mcms-launch-row">
28099:                 <div class="mcms-shell">
28100:                     <button class="mcms-menu-btn" type="button" title="Open or close toolkit settings" aria-label="Open or close toolkit settings" aria-expanded="false" aria-controls="${SCRIPT.panelId}">🗺️</button>
28101:                     <button class="mcms-dock-toggle-btn" type="button" title="Collapse command bar" aria-label="Collapse command bar" aria-expanded="true"><span class="mcms-dock-toggle-icon" aria-hidden="true">▴</span></button>
28102:                 </div>
28103:                 <button class="mcms-economy-btn" type="button" data-action="toggle-economy" title="Enable Economy Mode" aria-label="Enable Economy Mode" aria-pressed="false"><span aria-hidden="true">🍃</span><small>ECO</small></button>
28104:             </div>
28105:             <div class="mcms-floating-filter" title="Persistent map visibility filters">
28106:                 ${makeFloatButton('myMissions', '1', 'Personal', 'Show/hide confidently detected personal missions. Shortcut: 1', 'Personal', 'Mine')}
28107:                 ${makeFloatButton('allianceMissions', '2', 'Alliance', 'Show/hide confidently detected alliance missions. Shortcut: 2', 'Alliance', 'Ally')}
28108:                 ${makeFloatButton('vehicles', '3', 'Vehicles', 'Show/hide confidently detected vehicles. Shortcut: 3', 'Vehicles', 'Units')}
28109:                 ${makeFloatButton('buildings', '4', 'Buildings', 'Show/hide confidently detected buildings/stations. Shortcut: 4', 'Buildings', 'Bldgs')}
28110:                 ${makeFloatButton('allianceCredits', '5', 'Ally Cred', 'Show/hide approximate credit values beside alliance mission markers. Shortcut: 5', 'Ally Credits', 'Ally £')}
28111:                 ${makeFloatButton('missionAge', '6', 'Miss Age', 'Show personal mission age with progressive 8H amber, 16H orange and 24H red severity. Shortcut: 6', 'Mission Age', 'Age')}
28112:                 ${makeFloatButton('transportWatcher', '7', 'Transport', 'Show/hide amber transport-required watchers beside missions. Shortcut: 7', 'Transport', 'Trans')}
28113:                 ${makeFloatButton('unitCommitment', '8', 'Unit Count', 'Show your committed units beside missions. Shortcut: 8', 'Unit Count', 'Count')}
28114:                 ${makeFloatButton('criticalView', '9', 'Crit View', 'Show only personal missions aged 8 hours or more and frame them on the map. Shortcut: 9', 'Critical View', 'Critical')}
28115:                 ${makeActionFloatButton('open-vehicle-status', 'V', 'Veh Codes', 'Open or close Vehicle Code Status. Shortcut: V', 'Veh Codes', 'Codes')}
28116:                 ${makeActionFloatButton('open-critical-drawer', 'W', 'Age Watch', 'Open or close Mission Age Watch. Shortcut: W', 'Age Watch', 'Watch')}
28117:             </div>
28118:             <div class="mcms-screen-pins" title="Pinned screen shortcuts"></div>
28119:         `;
28120: 
28121:         ['click', 'dblclick', 'mousedown', 'mouseup', 'pointerdown', 'pointerup', 'pointercancel', 'touchstart', 'touchmove', 'touchend', 'wheel', 'contextmenu'].forEach(eventName => {
28122:             control.addEventListener(eventName, stopMapInteraction, { passive: false });
28123:         });
28124: 
28125:         let screenPinLongPressTimer = 0;
28126:         let screenPinLongPressButton = null;
28127:         const cancelScreenPinLongPress = () => {
28128:             runtimeClearTimeout(screenPinLongPressTimer);
28129:             screenPinLongPressTimer = 0;
28130:             screenPinLongPressButton = null;
28131:         };
28132:         control.addEventListener('pointerdown', event => {
28133:             const pinButton = closestEventTarget(event, '.mcms-screen-pin-btn[data-full-label]');
28134:             if (!pinButton || event.pointerType === 'mouse') return;
28135:             cancelScreenPinLongPress();
28136:             screenPinLongPressButton = pinButton;
28137:             screenPinLongPressTimer = runtimeSetTimeout(() => {
28138:                 if (screenPinLongPressButton !== pinButton) return;
28139:                 pinButton.dataset.mcmsLongPress = 'true';
28140:                 showToast(pinButton.dataset.fullLabel || pinButton.textContent || 'Bookmark');
28141:             }, 560);
28142:         });
28143:         control.addEventListener('pointermove', cancelScreenPinLongPress, { passive: true });
28144:         control.addEventListener('pointercancel', cancelScreenPinLongPress, { passive: true });
28145:         control.addEventListener('pointerup', () => {
28146:             runtimeClearTimeout(screenPinLongPressTimer);
28147:             screenPinLongPressTimer = 0;
28148:             screenPinLongPressButton = null;
28149:         }, { passive: true });
28150: 
28151:         control.addEventListener('click', event => {
28152:             const menuButton = closestEventTarget(event, '.mcms-menu-btn');
28153:             const dockToggleButton = closestEventTarget(event, '.mcms-dock-toggle-btn');
28154:             const toggleButton = closestEventTarget(event, '[data-toggle]');
28155:             const actionButton = closestEventTarget(event, '[data-action]');
28156:             if (actionButton?.dataset.mcmsLongPress === 'true') {
28157:                 delete actionButton.dataset.mcmsLongPress;
28158:                 event.preventDefault();
28159:                 return;
28160:             }
28161:             if (menuButton) { togglePanel(); return; }
28162:             if (dockToggleButton) { toggleCommandBar(); return; }
28163:             if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
28164:             if (actionButton) handleAction(actionButton);
28165:         });
28166: 
28167:         control.addEventListener('contextmenu', event => { event.preventDefault(); openPanel(); });
28168: 
28169:         mapEl.appendChild(control);
28170:         renderScreenPins();
28171:         updateUI();
28172:     }
28173: 
28174:     function createPanel() {
28175:         const existingPanel = document.getElementById(SCRIPT.panelId);
28176:         if (existingPanel) { settingsPanelActivated = true; return existingPanel; }
28177:         const panelStartedAt = startupClock();
28178:         settingsPanelActivated = true;
28179:         const panel = document.createElement('div');
28180:         panel.id = SCRIPT.panelId;
28181:         panel.setAttribute('role', 'dialog');
28182:         panel.setAttribute('aria-modal', 'false');
28183:         panel.setAttribute('aria-hidden', 'true');
28184:         panel.setAttribute('aria-label', `${SCRIPT.name} menu`);
28185: 
28186:         const buildUiThemeButtons = () => UI_THEME_ORDER.map(key => {
28187:             const theme = UI_THEMES[key];
28188:             return `
28189:                 <button class="mcms-ui-theme-btn" type="button" data-ui-theme="${key}" title="${escapeHtml(theme.description)}" aria-pressed="false">
28190:                     <span class="mcms-ui-theme-preview mcms-ui-theme-preview-${key}" aria-hidden="true"><span></span><span></span><span></span></span>
28191:                     <span class="mcms-ui-theme-copy"><strong>${escapeHtml(theme.label)}</strong><small>${escapeHtml(theme.short)}</small></span>
28192:                 </button>
28193:             `;
28194:         }).join('');
28195: 
28196:         const buildThemeButtons = keys => keys.map(key => {
28197:             const theme = THEMES[key];
28198:             return `
28199:                 <button class="mcms-theme-btn" type="button" data-theme="${key}" title="${theme.full}">
28200:                     <span class="mcms-iconbox">${theme.icon}</span>
28201:                     <span class="mcms-text">
28202:                         <span class="mcms-label">${theme.label}</span>
28203:                         <span class="mcms-pill">${theme.short}</span>
28204:                     </span>
28205:                 </button>
28206:             `;
28207:         }).join('');
28208:         const uiThemeButtons = buildUiThemeButtons();
28209:         const coreThemeButtons = buildThemeButtons(CORE_THEME_ORDER);
28210:         const serviceThemeButtons = buildThemeButtons(SERVICE_THEME_ORDER);
28211: 
28212:         const positionButtons = Object.entries(POSITIONS).map(([key, pos]) => `<button class="mcms-position-btn" type="button" data-position="${key}" title="${pos.label}">${pos.short}</button>`).join('');
28213: 
28214:         panel.innerHTML = `
28215:             <div class="mcms-panel-sticky-stack">
28216:                 <div class="mcms-header">
28217:                     <div class="mcms-drag-handle" title="Hold left-click and drag this bar to move the menu">
28218:                         <span class="mcms-title">☰ DRAG MENU HERE</span>
28219:                         <span class="mcms-subtitle">Hold left-click on this title area. Position saves.</span>
28220:                     </div>
28221:                     <button class="mcms-reset-panel" type="button" data-action="panel-reset" title="Reset menu position">↺</button>
28222:                     <button class="mcms-help-button" type="button" data-action="open-help-center" title="Open searchable Help Centre" aria-label="Open searchable Help Centre">?</button>
28223:                     <button class="mcms-close" type="button" title="Close">×</button>
28224:                 </div>
28225:                 <div class="mcms-tabs">
28226:                     <button class="mcms-tab-btn" type="button" data-tab="skins">Skins</button>
28227:                     <button class="mcms-tab-btn" type="button" data-tab="tools">Tools</button>
28228:                     <button class="mcms-tab-btn" type="button" data-tab="resources">Resources</button>
28229:                     <button class="mcms-tab-btn" type="button" data-tab="ops">Ops</button>
28230:                     <button class="mcms-tab-btn" type="button" data-tab="payouts">Payouts</button>
28231:                     <button class="mcms-tab-btn" type="button" data-tab="discord">Finance</button>
28232:                     <button class="mcms-tab-btn" type="button" data-tab="places">Places</button>
28233:                     <button class="mcms-tab-btn" type="button" data-tab="settings">Settings</button>
28234:                 </div>
28235:             </div>
28236:             <section class="mcms-tab-panel" data-panel="skins">
28237:                 <div class="mcms-section-label">Interface theme</div>
28238:                 <div class="mcms-ui-theme-grid">${uiThemeButtons}</div>
28239:                 <div class="mcms-status mcms-ui-theme-status">Interface themes restyle the complete toolkit without changing your selected operational map skin.</div>
28240:                 <div class="mcms-section-label">Core skins</div>
28241:                 <div class="mcms-grid-2">${coreThemeButtons}</div>
28242:                 <div class="mcms-section-label">Emergency services</div>
28243:                 <div class="mcms-grid-2">${serviceThemeButtons}</div>
28244:                 <div class="mcms-status">Fire Command, Police Tactical, Medical Control and Coastal Command use lightweight local tile filters and remain compatible with map overlays.</div>
28245:                 <div class="mcms-section-label">Automatic day / night</div>
28246:                 <div class="mcms-grid-2">
28247:                     ${makeToggleButton('autoNight', '◑', 'Auto Night', 'Automatically switch operational map skins at the configured day and night times.')}
28248:                 </div>
28249:                 <div class="mcms-row"><span class="mcms-row-label">Night starts</span><input class="mcms-input" type="time" data-setting="auto-night-start"></div>
28250:                 <div class="mcms-row"><span class="mcms-row-label">Day starts</span><input class="mcms-input" type="time" data-setting="auto-day-start"></div>
28251:                 <div class="mcms-row"><span class="mcms-row-label">Night skin</span><select class="mcms-select" data-setting="auto-night-theme">${buildThemeOptions(state.autoNight.nightTheme)}</select></div>
28252:                 <div class="mcms-row"><span class="mcms-row-label">Day skin</span><select class="mcms-select" data-setting="auto-day-theme">${buildThemeOptions(state.autoNight.dayTheme)}</select></div>
28253:             </section>
28254:             <section class="mcms-tab-panel" data-panel="tools">
28255:                 <div class="mcms-section-label">Map tools</div>
28256:                 <div class="mcms-grid-2">
28257:                     ${makeToggleButton('clean', '▢', 'Clean', 'Hide map controls for screenshots. Shortcut: C')}
28258:                     ${makeToggleButton('markerFocus', '◉', 'Focus', 'Dim detected buildings/vehicles and keep missions clearer. Shortcut: F')}
28259:                     ${makeToggleButton('missionPulse', '✦', 'Pulse', 'Pulse detected mission markers. Shortcut: P')}
28260:                     ${makeToggleButton('roadPriority', '═', 'Roads+', 'Increase road contrast. Shortcut: R')}
28261:                     ${makeToggleButton('coverage', '◎', 'Rings', 'Draw coverage rings around detected buildings/stations.')}
28262:                     ${makeToggleButton('heatmap', '▦', 'Heatmap', 'Show strong and weak operational coverage across the visible map.')}
28263:                 </div>
28264:                 <div class="mcms-row" style="margin-top:8px">
28265:                     <span class="mcms-row-label">Ring radius</span>
28266:                     <select class="mcms-select" data-setting="coverage-radius">
28267:                         <option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option>
28268:                     </select>
28269:                 </div>
28270:                 <div class="mcms-section-label">Coverage Heatmap</div>
28271:                 <div class="mcms-row"><span class="mcms-row-label">Coverage source</span><select class="mcms-select" data-setting="heatmap-source"><option value="stations">Personal stations</option><option value="vehicles">Current vehicles</option></select></div>
28272:                 <div class="mcms-row"><span class="mcms-row-label">Service</span><select class="mcms-select" data-setting="heatmap-service"><option value="all">All services</option><option value="fire">Fire & rescue</option><option value="ambulance">Ambulance</option><option value="police">Police</option><option value="air">Air assets</option><option value="water">Water/coastal</option></select></div>
28273:                 <div class="mcms-row"><span class="mcms-row-label">Planning radius</span><select class="mcms-select" data-setting="heatmap-radius"><option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option></select></div>
28274:                 <div class="mcms-row"><span class="mcms-row-label">Overlay strength</span><select class="mcms-select" data-setting="heatmap-opacity"><option value="0.18">Light</option><option value="0.30">Normal</option><option value="0.42">Strong</option></select></div>
28275:                 <div class="mcms-heat-legend"><span class="mcms-heat-key" style="background:#00c853">Strong</span><span class="mcms-heat-key" style="background:#64dd17">Good</span><span class="mcms-heat-key" style="background:#ffd600">Covered</span><span class="mcms-heat-key" style="background:#ff9100">Weak</span><span class="mcms-heat-key" style="background:#d50000">Gap</span></div>
28276:                 <div class="mcms-section-label">Map performance</div>
28277:                 <div class="mcms-grid-2">
28278:                     ${makeToggleButton('allianceBuildingsMapBlocker', '▦', 'Alliance Map Blocker', 'Blocks the heavy map in the Alliance Buildings/Courses menu. ON means blocked. Reload required.')}
28279:                 </div>
28280:                 <div class="mcms-status"><strong>Map Blocker ON</strong> removes the Alliance Buildings map, expands the courses list and prevents its heavy marker layer attaching.</div>
28281:                 <div class="mcms-section-label">Map visibility · shortcuts 1–9 · dashboards V/W</div>
28282:                 <div class="mcms-grid-2">
28283:                     ${makeToggleButton('myMissions', '1', 'Personal Missions', 'Show/hide confidently detected personal missions. Shortcut: 1')}
28284:                     ${makeToggleButton('allianceMissions', '2', 'Alliance Missions', 'Show/hide confidently detected alliance missions. Shortcut: 2')}
28285:                     ${makeToggleButton('vehicles', '3', 'Vehicles', 'Show/hide confidently detected vehicles. Shortcut: 3')}
28286:                     ${makeToggleButton('buildings', '4', 'Buildings', 'Show/hide confidently detected buildings/stations. Shortcut: 4')}
28287:                     ${makeToggleButton('allianceCredits', '5', 'Ally Cred', 'Show/hide approximate credit values beside alliance mission markers. Shortcut: 5')}
28288:                     ${makeToggleButton('missionAge', '6', 'Miss Age', 'Show personal mission age with progressive 8H amber, 16H orange and 24H red severity. Shortcut: 6')}
28289:                     ${makeToggleButton('transportWatcher', '7', 'Transport Watcher', 'Show amber transport-required badges beside personal and alliance missions. Shortcut: 7')}
28290:                     ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your committed units beside personal and alliance missions. Shortcut: 8')}
28291:                     ${makeToggleButton('criticalView', '9', 'Critical View', 'Temporarily show only personal missions aged 8 hours or more. Shortcut: 9')}
28292:                 </div>
28293:                 <div class="mcms-row" style="margin-top:8px"><span class="mcms-row-label">Ally Credits filter</span><select class="mcms-select" data-setting="alliance-credit-minimum"><option value="0">All values</option><option value="5000">5K+</option><option value="10000">10K+</option><option value="15000">15K+</option><option value="20000">20K+</option></select></div>
28294:                 <div class="mcms-status">Ready.</div>
28295:             </section>
28296:             <section class="mcms-tab-panel" data-panel="resources">
28297:                 <div class="mcms-section-label">Co-admin Patient Transport Sweep</div>
28298:                 <div class="mcms-grid-2">
28299:                     <button class="mcms-small-btn" type="button" data-action="scan-transport-sweep">Scan Transports</button>
28300:                     <button class="mcms-small-btn" type="button" data-action="start-transport-sweep">Start Sweep</button>
28301:                     <button class="mcms-small-btn" type="button" data-action="stop-transport-sweep">Stop</button>
28302:                 </div>
28303:                 <div class="mcms-row"><span class="mcms-row-label">Delay between clears</span><select class="mcms-select" data-setting="transport-sweep-delay"><option value="1500">1.5 seconds</option><option value="2000">2 seconds</option><option value="2500">2.5 seconds</option><option value="3000">3 seconds</option><option value="4000">4 seconds</option><option value="5000">5 seconds</option></select></div>
28304:                 <div class="mcms-row"><span class="mcms-row-label">Maximum per run</span><input class="mcms-input" type="number" min="1" max="50" step="1" data-setting="transport-sweep-max"></div>
28305:                 <div data-transport-sweep></div>
28306:                 <div class="mcms-status">Manual start only. The sweep excludes your personal vehicle IDs, checks every non-personal FMS 5 patient vehicle in each affected alliance mission, and only clears a vehicle when MissionChief exposes the visible <b>Discharge patient</b> button. Prisoner transports are not included.</div>
28307:                 <div class="mcms-section-label">Resource Gap Finder</div>
28308:                 <div class="mcms-grid-2">
28309:                     ${makeToggleButton('resourceGap', '⚠', 'Resource Gap', 'Show missing-resource badges and nearby available-unit estimates in Mission Inspector.')}
28310:                 </div>
28311:                 <div class="mcms-row"><span class="mcms-row-label">Nearby radius</span><select class="mcms-select" data-setting="resource-gap-radius"><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>
28312:                 <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
28313:                 <div class="mcms-section-label">Vehicle loading</div>
28314:                 <div class="mcms-grid-2">
28315:                     ${makeToggleButton('autoLoadAllVehicles', '⇊', 'Auto-load all vehicles', 'Automatically activates MissionChief’s native Load more vehicles control inside an opened mission.')}
28316:                 </div>
28317:                 <div class="mcms-status">Transport Watcher and Unit Count remain under Tools as the canonical map-overlay controls for shortcuts 7 and 8.</div>
28318:             </section>
28319:             <section class="mcms-tab-panel" data-panel="ops">
28320:                 <div class="mcms-section-label">Mission Intelligence</div>
28321:                 <div class="mcms-grid-2">
28322:                     ${makeToggleButton('missionInspector', 'ⓘ', 'Inspector', 'Hover a mission marker for a live mission summary.')}
28323:                     ${makeToggleButton('missionValue', '£', 'Mission Value', 'Show a formatted mission value in opened MissionChief windows.')}
28324:                     ${makeToggleButton('stuckDetector', '⚠', 'Stuck Detect', 'Flag personal or joined missions that show no meaningful progress.')}
28325:                     ${makeToggleButton('missionSpawn', '◎', 'New Mission', 'Animate genuinely new mission spawns with a radar pulse.')}
28326:                     ${makeToggleButton('majorIncidentFeed', '▰', 'Incident Feed', 'Show the theme-aware major incident ticker in the top status bar. Hover pauses; click a mission to zoom.')}
28327:                     ${makeToggleButton('missionLockAudio', '⌁', 'Tracking Audio', 'Play a short synthesized tracking cue during mission zoom and target acquisition.')}
28328:                     <button class="mcms-toggle-btn mcms-action-btn" type="button" data-action="open-vehicle-status" title="Open or close a live table of personal vehicles grouped by MissionChief status code. Shortcut: V">
28329:                         <span class="mcms-iconbox">V</span>
28330:                         <span class="mcms-text"><span class="mcms-label">Vehicle Codes</span><span class="mcms-pill">VIEW</span></span>
28331:                     </button>
28332:                 </div>
28333:                 <div class="mcms-row"><span class="mcms-row-label">Stuck after</span><select class="mcms-select" data-setting="stuck-threshold"><option value="10">10 minutes</option><option value="15">15 minutes</option><option value="20">20 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option><option value="60">60 minutes</option></select></div>
28334:                 <div class="mcms-status">Stuck detection resets its timer whenever missing requirements, patients, prisoners, progress value or your assigned-unit state changes.</div>
28335:                 <div class="mcms-section-label">Session Performance</div>
28336:                 <div data-ops-session></div>
28337:                 <div class="mcms-section-label">Mission Age Workflow</div>
28338:                 <div class="mcms-grid-2">
28339:                     <button class="mcms-small-btn" type="button" data-action="open-critical-drawer">Open Mission Drawer (W)</button>
28340:                     <button class="mcms-small-btn" type="button" data-action="fit-critical">Frame Aged</button>
28341:                 </div>
28342:                 <div class="mcms-status">Mission Age and Critical View remain under Tools as the canonical shortcut controls for 6 and 9. Ops provides the mission workflow and dashboard actions.</div>
28343:                 <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>
28344:                 <div class="mcms-ops-list" data-ops-critical-preview></div>
28345:                 <div class="mcms-section-label">Completion History</div>
28346:                 <div class="mcms-ops-list" data-ops-history></div>
28347:                 <div class="mcms-grid-2" style="margin-top:7px !important">
28348:                     <button class="mcms-small-btn" type="button" data-action="reset-session">Reset Session</button>
28349:                     <button class="mcms-small-btn" type="button" data-action="clear-payout-history">Clear History</button>
28350:                 </div>
28351:             </section>
28352:             <section class="mcms-tab-panel" data-panel="payouts">
28353:                 <div class="mcms-section-label">Emergency Payout Flash</div>
28354:                 <div class="mcms-grid-2">
28355:                     ${makeToggleButton('payoutFlash', '🚨', 'Payout Flash', 'Flash the map red and blue when a single credit gain reaches the configured threshold.')}
28356:                     ${makeToggleButton('payoutSound', '♪', 'Theme Audio', 'Play the selected template completion cue. Vice City, Bad Company, Scarface and Cyberpunk use hosted MP3 cashout sounds; other templates retain synthesized cues.')}
28357:                 </div>
28358:                 <div class="mcms-row"><span class="mcms-row-label">Banner style</span><select class="mcms-select" data-setting="payout-template">${buildPayoutTemplateOptions(state.payoutFlash.template)}</select></div>
28359:                 <div class="mcms-row"><span class="mcms-row-label">Minimum payout</span><input class="mcms-input" type="number" min="1000" step="1000" data-setting="payout-threshold"></div>
28360:                 <div class="mcms-row"><span class="mcms-row-label">Flash duration (sec)</span><input class="mcms-input" type="number" min="2" max="30" step="2" data-setting="payout-duration"></div>
28361:                 <div class="mcms-row"><span class="mcms-row-label">Sound volume</span><input class="mcms-input" type="range" min="0" max="1" step="0.05" data-setting="payout-volume"></div>
28362:                 <div class="mcms-row"><span class="mcms-row-label">Test payout tier</span><select class="mcms-select" data-setting="payout-test-amount"><option value="10000">10K Standard</option><option value="25000">25K Major</option><option value="50000">50K High Value</option><option value="100000">100K Elite</option></select></div>
28363:                 <button class="mcms-small-btn" style="width:100% !important;margin-bottom:8px !important" type="button" data-action="test-payout-flash">Test Emergency Flash</button>
28364:                 <div class="mcms-status">Vice City Inspired, Bad Company Inspired, Scarface Inspired and Cyberpunk Inspired use hosted cashout MP3s from your public GitHub asset repository. Other templates retain synthesized cues. Enable Theme Audio, set the volume, then use Test Emergency Flash.</div>
28365:             </section>
28366:             <section class="mcms-tab-panel" data-panel="discord">
28367:                 <div class="mcms-section-label">Discord Financial Command</div>
28368:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook URL</span><input class="mcms-input" type="password" autocomplete="off" spellcheck="false" data-setting="discord-webhook" placeholder="https://discord.com/api/webhooks/..."></div>
28369:                 <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook name</span><input class="mcms-input" type="text" maxlength="80" data-setting="discord-name" value="MissionChief Finance"></div>
28370:                 <div class="mcms-row"><span class="mcms-row-label">Report format</span><select class="mcms-select" data-setting="discord-report-mode"><option value="fullAudit">Executive + Full Audit</option><option value="executive">Executive Brief Only</option></select></div>
28371:                 <div class="mcms-row"><span class="mcms-row-label">Report period</span><select class="mcms-select" data-setting="discord-period"><option value="today">Today</option><option value="yesterday">Yesterday</option><option value="last24">Last 24 Hours</option><option value="last7">Last 7 Days</option><option value="last30">Last 30 Days</option><option value="last90">Last 90 Days</option><option value="last180">Last 180 Days</option><option value="last365">Last 365 Days</option><option value="allAvailable">All Available History</option><option value="session">Current Session</option><option value="sinceLast">Since Last Report</option><option value="custom">Custom Dates</option></select></div>
28372:                 <div class="mcms-discord-date-grid">
28373:                     <div class="mcms-row"><span class="mcms-row-label">From</span><input class="mcms-input" type="date" data-setting="discord-custom-start"></div>
28374:                     <div class="mcms-row"><span class="mcms-row-label">To</span><input class="mcms-input" type="date" data-setting="discord-custom-end"></div>
28375:                 </div>
28376:                 <div class="mcms-row"><span class="mcms-row-label">Breakdown depth</span><select class="mcms-select" data-setting="discord-top-categories"><option value="3">Top 3</option><option value="5">Top 5</option><option value="8">Top 8</option></select></div>
28377:                 <div class="mcms-row"><span class="mcms-row-label">Previous-period comparison</span><select class="mcms-select" data-setting="discord-comparison"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28378:                 <div class="mcms-row"><span class="mcms-row-label">Risk intelligence</span><select class="mcms-select" data-setting="discord-risk"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28379:                 <div class="mcms-row"><span class="mcms-row-label">Forecast intelligence</span><select class="mcms-select" data-setting="discord-forecast"><option value="true">Included</option><option value="false">Disabled</option></select></div>
28380:                 <div class="mcms-row"><span class="mcms-row-label">Discord chart image</span><select class="mcms-select" data-setting="discord-chart"><option value="true">Attach chart</option><option value="false">Text only</option></select></div>
28381:                 <div class="mcms-grid-2">
28382:                     <button class="mcms-small-btn" type="button" data-action="discord-test">Test Connection</button>
28383:                     <button class="mcms-small-btn" type="button" data-action="discord-clear">Clear Webhook</button>
28384:                 </div>
28385:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="discord-generate-post">Generate & Post Audit</button>
28386:                 <div class="mcms-status mcms-discord-status" data-discord-status data-tone="neutral">Select a reporting period, then generate and post the financial intelligence report.</div>
28387: 
28388:                 <div class="mcms-section-label">Player-Linked Local Financial Archive</div>
28389:                 <div class="mcms-row"><span class="mcms-row-label">Local historical archive</span><select class="mcms-select" data-setting="finance-vault-enabled"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
28390:                 <div class="mcms-row"><span class="mcms-row-label">History retention</span><select class="mcms-select" data-setting="finance-vault-retention"><option value="all">All available</option><option value="1825">5 years</option><option value="730">2 years</option><option value="365">1 year</option><option value="180">180 days</option><option value="90">90 days</option></select></div>
28391:                 <div class="mcms-row"><span class="mcms-row-label">GitHub intelligence feeds</span><select class="mcms-select" data-setting="finance-rule-feed"><option value="true">Automatic rules + policy</option><option value="false">Built-in intelligence only</option></select></div>
28392:                 <div class="mcms-grid-2">
28393:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-scan">Deep Scan All Available</button>
28394:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-cancel">Stop Scan</button>
28395:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-export">Export Archive</button>
28396:                     <button class="mcms-small-btn" type="button" data-action="finance-archive-import">Import Archive</button>
28397:                 </div>
28398:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-rules-refresh">Refresh Financial Intelligence</button>
28399:                 <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="finance-archive-clear">Clear Player Archive</button>
28400:                 <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-finance-file>
28401:                 <div class="mcms-finance-vault-summary" data-finance-vault-summary></div>
28402:                 <div class="mcms-status mcms-discord-status" data-finance-vault-status data-tone="neutral">Local Financial Archive ready.</div>
28403:                 <div class="mcms-status mcms-discord-status" data-finance-rule-status data-tone="neutral">Built-in financial intelligence active.</div>
28404:                 <div class="mcms-status">GitHub hosts public transaction-classification rules and audit policy only. The Toolkit never uploads player ledger data, Discord webhooks or repository credentials. The local archive is indexed by MissionChief player ID/name and can be transferred between devices using Export Archive / Import Archive or the complete private Toolkit backup.</div>
28405:                 <div class="mcms-status mcms-finance-private-note">Private backup warning: Export All includes your Discord webhook and locally stored MissionChief financial history. Anyone holding the file may post through the webhook and inspect the exported game ledger.</div>
28406:             </section>
28407:             <section class="mcms-tab-panel" data-panel="places">
28408:                 <div class="mcms-section-label">Quick jumps + screen shortcuts</div>
28409:                 <div class="mcms-quick-list"></div>
28410:                 <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
28411:                 <div class="mcms-bookmark-list"></div>
28412:                 <div class="mcms-section-label">Saved Map Profiles</div>
28413:                 <div class="mcms-profile-list" data-profile-list></div>
28414:                 <div class="mcms-status">Profiles store your map location, zoom, skin, visibility filters and operational overlays.</div>
28415:             </section>
28416:             <section class="mcms-tab-panel" data-panel="settings">
28417:                 <div class="mcms-section-label">Device layout</div>
28418:                 <div class="mcms-row"><span class="mcms-row-label">Mobile Mode · iOS Safari</span><select class="mcms-select" data-setting="mobile-mode"><option value="auto">Auto detect iPhone</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28419:                 <div class="mcms-row"><span class="mcms-row-label">Tablet Mode</span><select class="mcms-select" data-setting="tablet-mode"><option value="auto">Auto detect</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
28420:                 <div class="mcms-status" data-device-layout-status>Detecting device layout…</div>
28421:                 <div class="mcms-status">Mobile Mode is tuned for iPhone Safari with Tampermonkey: a map-aware 5×2 command grid in portrait, a compact single-row dock where space allows, full-width safe-area bottom sheets, 16px form controls to prevent Safari input zoom, and Visual Viewport handling for the iOS keyboard. Tablet and desktop layouts remain separate and unchanged.</div>
28422:                 <div class="mcms-section-label">Dock position</div>
28423:                 <div class="mcms-position-grid">${positionButtons}</div>
28424:                 <div class="mcms-desktop-position-controls">
28425:                     <div class="mcms-section-label">Fine nudge</div>
28426:                     <div class="mcms-nudge-grid">
28427:                         <button class="mcms-small-btn" type="button" data-action="nudge-left">←</button>
28428:                         <button class="mcms-small-btn" type="button" data-action="nudge-up">↑</button>
28429:                         <button class="mcms-small-btn" type="button" data-action="nudge-down">↓</button>
28430:                         <button class="mcms-small-btn" type="button" data-action="nudge-right">→</button>
28431:                         <button class="mcms-small-btn" type="button" data-action="nudge-reset">0</button>
28432:                     </div>
28433:                     <div class="mcms-status mcms-nudge-value">X 0 / Y 0</div>
28434:                     <div class="mcms-section-label">Menu panel</div>
28435:                     <div class="mcms-nudge-grid">
28436:                         <button class="mcms-small-btn" type="button" data-action="panel-left">←</button>
28437:                         <button class="mcms-small-btn" type="button" data-action="panel-up">↑</button>
28438:                         <button class="mcms-small-btn" type="button" data-action="panel-down">↓</button>
28439:                         <button class="mcms-small-btn" type="button" data-action="panel-right">→</button>
28440:                         <button class="mcms-small-btn" type="button" data-action="panel-reset">↺</button>
28441:                     </div>
28442:                 </div>
28443:                 <div class="mcms-section-label">Input</div>
28444:                 <div class="mcms-grid-2">
28445:                     ${makeToggleButton('shortcuts', '⌨', 'Keys', 'Keyboard shortcuts on/off. Map tools: 1–9. Vehicle Codes: V. Mission Age Watch: W. Menu: M.')}
28446:                 </div>
28447:                 <div class="mcms-row"><span class="mcms-row-label">Major incident threshold</span><select class="mcms-select" data-setting="major-incident-minimum"><option value="10000">10,000+ credits</option><option value="25000">25,000+ credits</option><option value="50000">50,000+ credits</option><option value="100000">100,000+ credits</option></select></div>
28448:                 <div class="mcms-section-label">Economy Mode</div>
28449:                 <div class="mcms-status mcms-economy-status">Use the leaf button beside the map-menu opener. Economy Mode preserves every module while reducing animations, map-layer pressure and background refresh frequency.</div>
28450:                 <div class="mcms-section-label">Settings Backup</div>
28451:                 <div class="mcms-config-actions">
28452:                     <button class="mcms-small-btn" type="button" data-action="export-config" title="Export every toolkit setting, private integration, profile, bookmark and Financial Archive history" aria-label="Export all toolkit settings">Export All</button>
28453:                     <button class="mcms-small-btn" type="button" data-action="import-config" title="Import a current or legacy toolkit settings backup" aria-label="Import all toolkit settings">Import All</button>
28454:                     <button class="mcms-small-btn" type="button" data-action="reset-config">Reset</button>
28455:                 </div>
28456:                 <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-config-file>
28457:                 <div class="mcms-status">Backups include every persistent toolkit preference, desktop/Tablet/iOS layout choice, profile, bookmark, saved Discord webhook and local Financial Archive history. A clear private-file warning is shown before export and import. Store the JSON securely. Current and legacy toolkit backup files are supported.</div>
28458:             </section>
28459:             <div class="mcms-footer">
28460:                 <span>Audited runtime: compact Smart Bookmark Labels, responsive modes and every interface theme remain fully preserved.</span>
28461:                 <span class="mcms-build">${SCRIPT.name} v${SCRIPT.version} · MIT · ${SCRIPT.author}</span>
28462:             </div>
28463:         `;
28464: 
28465:         const tabList = panel.querySelector('.mcms-tabs');
28466:         if (tabList) tabList.setAttribute('role', 'tablist');
28467:         panel.querySelectorAll('.mcms-tab-btn').forEach(button => {
28468:             const tab = button.dataset.tab;
28469:             button.id = `mcms-tab-${tab}`;
28470:             button.setAttribute('role', 'tab');
28471:             button.setAttribute('aria-controls', `mcms-tabpanel-${tab}`);
28472:             button.setAttribute('aria-selected', 'false');
28473:             button.tabIndex = -1;
28474:         });
28475:         panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => {
28476:             const tab = tabPanel.dataset.panel;
28477:             tabPanel.id = `mcms-tabpanel-${tab}`;
28478:             tabPanel.setAttribute('role', 'tabpanel');
28479:             tabPanel.setAttribute('aria-labelledby', `mcms-tab-${tab}`);
28480:             tabPanel.hidden = true;
28481:         });
28482: 
28483:         panel.addEventListener('keydown', event => {
28484:             const current = closestEventTarget(event, '.mcms-tab-btn');
28485:             if (!current || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
28486:             const buttons = Array.from(panel.querySelectorAll('.mcms-tab-btn'));
28487:             const currentIndex = Math.max(0, buttons.indexOf(current));
28488:             const nextIndex = event.key === 'Home' ? 0
28489:                 : event.key === 'End' ? buttons.length - 1
28490:                 : (currentIndex + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
28491:             event.preventDefault();
28492:             const nextButton = buttons[nextIndex];
28493:             setActiveTab(nextButton.dataset.tab);
28494:             nextButton.focus({ preventScroll: true });
28495:         });
28496: 
28497:         panel.addEventListener('click', event => {
28498:             const closeButton = closestEventTarget(event, '.mcms-close');
28499:             const tabButton = closestEventTarget(event, '.mcms-tab-btn');
28500:             const uiThemeButton = closestEventTarget(event, '.mcms-ui-theme-btn');
28501:             const themeButton = closestEventTarget(event, '.mcms-theme-btn');
28502:             const toggleButton = closestEventTarget(event, '[data-toggle]');
28503:             const positionButton = closestEventTarget(event, '.mcms-position-btn');
28504:             const actionButton = closestEventTarget(event, '[data-action]');
28505:             if (closeButton) { closePanel({ restoreFocus: true }); return; }
28506:             if (tabButton) { setActiveTab(tabButton.dataset.tab); return; }
28507:             if (uiThemeButton) { applyUiTheme(uiThemeButton.dataset.uiTheme, true); return; }
28508:             if (themeButton) { applyTheme(themeButton.dataset.theme, true); return; }
28509:             if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
28510:             if (positionButton) { applyPosition(positionButton.dataset.position, true); return; }
28511:             if (actionButton) {
28512:                 event.preventDefault();
28513:                 handleAction(actionButton);
28514:                 return;
28515:             }
28516:         });
28517: 
28518:         panel.addEventListener('change', event => handleSettingChange(event.target));
28519: 
28520:         const dragHandle = panel.querySelector('.mcms-drag-handle');
28521:         if (dragHandle) {
28522:             dragHandle.addEventListener('mousedown', startPanelDrag, true);
28523:             dragHandle.addEventListener('touchstart', startPanelDrag, { capture: true, passive: false });
28524:         }
28525: 
28526:         ['click', 'dblclick', 'mousedown', 'mouseup', 'mousemove', 'wheel', 'contextmenu', 'touchstart', 'touchmove', 'touchend'].forEach(eventName => {
28527:             panel.addEventListener(eventName, event => event.stopPropagation(), { passive: false });
28528:         });
28529: 
28530:         document.body.appendChild(panel);
28531:         const importInput = panel.querySelector('[data-import-config-file]');
28532:         if (importInput) {
28533:             importInput.addEventListener('change', () => {
28534:                 const file = importInput.files?.[0];
28535:                 if (file) importToolkitConfigFile(file);
28536:                 importInput.value = '';
28537:             });
28538:         }
28539:         const financeImportInput = panel.querySelector('[data-import-finance-file]');
28540:         if (financeImportInput) {
28541:             financeImportInput.addEventListener('change', () => {
28542:                 const file = financeImportInput.files?.[0];
28543:                 if (file) importFinancialArchiveFile(file);
28544:                 financeImportInput.value = '';
28545:             });
28546:         }
28547:         renderQuickPlaces();
28548:         renderBookmarks();
28549:         renderProfiles();
28550:         updateUI();
28551:         recordStartupMetric('settingsPanelBuildMs', panelStartedAt, { settingsPanelLazy: true });
28552:         return panel;
28553:     }
28554: 
28555:     function renderQuickPlaces() {
28556:         const list = document.querySelector(`#${SCRIPT.panelId} .mcms-quick-list`);
28557:         if (!list) return;
28558:         list.innerHTML = QUICK_PLACES.map(place => `
28559:             <div class="mcms-quick-row">
28560:                 <button class="mcms-place-main" type="button" data-action="place-go" data-place="${place.id}" title="Jump to ${escapeHtml(place.name)}">
28561:                     <span class="mcms-iconbox">⌖</span><span class="mcms-text"><span class="mcms-label">${escapeHtml(place.name)}</span><span class="mcms-pill">${place.label}</span></span>
28562:                 </button>
28563:                 <button class="mcms-pin-btn ${state.quickPins[place.id] ? 'mcms-on' : ''}" type="button" data-action="quick-pin" data-place="${place.id}" title="Pin as persistent screen shortcut">${state.quickPins[place.id] ? 'ON' : 'PIN'}</button>
28564:             </div>
28565:         `).join('');
28566:     }
28567: 
28568:     function renderBookmarks() {
28569:         const list = document.querySelector(`#${SCRIPT.panelId} .mcms-bookmark-list`);
28570:         if (!list) return;
28571:         list.innerHTML = state.bookmarks.map((bookmark, index) => {
28572:             if (!bookmark) {
28573:                 return `<div class="mcms-bookmark-row"><span class="mcms-bookmark-name">Slot ${index + 1} empty</span><span></span><span></span><button class="mcms-bookmark-btn" type="button" data-action="bookmark-save" data-slot="${index}">Save</button><span></span></div>`;
28574:             }
28575:             const screenLabel = bookmarkScreenLabel(bookmark);
28576:             const labelMode = bookmark.shortLabel ? 'CUSTOM' : 'AUTO';
28577:             const labelTitle = `${bookmark.name} · Screen label: ${screenLabel} (${labelMode.toLowerCase()})`;
28578:             return `
28579:                 <div class="mcms-bookmark-row">
28580:                     <button class="mcms-bookmark-name mcms-bookmark-name-btn" type="button" data-action="bookmark-label" data-slot="${index}" title="${escapeHtml(labelTitle)}" aria-label="Edit ${escapeHtml(bookmark.name)} name and short label">
28581:                         <span class="mcms-bookmark-name-main">${escapeHtml(bookmark.name)}</span>
28582:                         <span class="mcms-bookmark-short">${escapeHtml(screenLabel)} · ${labelMode}</span>
28583:                     </button>
28584:                     <button class="mcms-bookmark-btn" type="button" data-action="bookmark-go" data-slot="${index}">Go</button>
28585:                     <button class="mcms-pin-btn ${bookmark.pinned ? 'mcms-on' : ''}" type="button" data-action="bookmark-pin" data-slot="${index}" title="Pin as persistent screen shortcut">${bookmark.pinned ? 'ON' : 'PIN'}</button>
28586:                     <button class="mcms-bookmark-btn" type="button" data-action="bookmark-save" data-slot="${index}" title="Update this bookmark from the current map view">Save</button>
28587:                     <button class="mcms-bookmark-btn" type="button" data-action="bookmark-delete" data-slot="${index}">×</button>
28588:                 </div>`;
28589:         }).join('');
28590:     }
28591: 
28592:     function renderScreenPins() {
28593:         const dock = document.querySelector(`#${SCRIPT.controlId} .mcms-screen-pins`);
28594:         if (!dock) return;
28595:         const entries = [];
28596:         for (const place of QUICK_PLACES) {
28597:             if (!state.quickPins[place.id]) continue;
28598:             entries.push({
28599:                 kind: 'quick',
28600:                 id: place.id,
28601:                 fullName: place.name,
28602:                 baseLabel: sanitiseBookmarkShortLabel(place.label) || makeSmartBookmarkLabel(place.name)
28603:             });
28604:         }
28605:         state.bookmarks.forEach((bookmark, index) => {
28606:             if (!bookmark || !bookmark.pinned) return;
28607:             entries.push({
28608:                 kind: 'bookmark',
28609:                 index,
28610:                 fullName: bookmark.name,
28611:                 baseLabel: bookmarkScreenLabel(bookmark)
28612:             });
28613:         });
28614: 
28615:         dock.innerHTML = resolveScreenPinLabels(entries).map(entry => {
28616:             const action = entry.kind === 'quick'
28617:                 ? `data-action="place-go" data-place="${escapeHtml(entry.id)}"`
28618:                 : `data-action="bookmark-go" data-slot="${entry.index}"`;
28619:             const className = entry.kind === 'quick' ? 'mcms-pin-quick' : 'mcms-pin-custom';
28620:             return `<button class="mcms-screen-pin-btn ${className}" type="button" ${action} data-full-label="${escapeHtml(entry.fullName)}" data-smart-label="${escapeHtml(entry.label)}" title="Jump to ${escapeHtml(entry.fullName)}" aria-label="Jump to ${escapeHtml(entry.fullName)}">${escapeHtml(entry.label)}</button>`;
28621:         }).join('');
28622:         if (isTouchLayoutActive()) fitControlToMap();
28623:     }
28624: 
28625:     function handleAction(button) {
28626:         const action = button.dataset.action;
28627:         if (action === 'place-go') {
28628:             const place = QUICK_PLACES.find(item => item.id === button.dataset.place);
28629:             if (place && setMapView(place.lat, place.lng, place.zoom)) showToast(place.name);
28630:             return;
28631:         }
28632:         if (action === 'quick-pin') { toggleQuickPin(button.dataset.place); return; }
28633:         if (action === 'bookmark-save') { saveBookmark(Number(button.dataset.slot)); return; }
28634:         if (action === 'bookmark-label') { editBookmarkLabel(Number(button.dataset.slot)); return; }
28635:         if (action === 'bookmark-go') { goBookmark(Number(button.dataset.slot)); return; }
28636:         if (action === 'bookmark-delete') { deleteBookmark(Number(button.dataset.slot)); return; }
28637:         if (action === 'bookmark-pin') { toggleBookmarkPin(Number(button.dataset.slot)); return; }
28638:         if (action === 'nudge-left') { nudgeControl(-4, 0); return; }
28639:         if (action === 'nudge-right') { nudgeControl(4, 0); return; }
28640:         if (action === 'nudge-up') { nudgeControl(0, -4); return; }
28641:         if (action === 'nudge-down') { nudgeControl(0, 4); return; }
28642:         if (action === 'nudge-reset') { resetNudge(); return; }
28643:         if (action === 'panel-left') { nudgePanel(-24, 0); return; }
28644:         if (action === 'panel-right') { nudgePanel(24, 0); return; }
28645:         if (action === 'panel-up') { nudgePanel(0, -24); return; }
28646:         if (action === 'panel-down') { nudgePanel(0, 24); return; }
28647:         if (action === 'open-help-center') { openHelpCenter(); return; }
28648:         if (action === 'toggle-economy') { setEconomyMode(!state.economyMode, true); return; }
28649:         if (action === 'open-critical-drawer') { toggleCriticalDrawer(); return; }
28650:         if (action === 'open-vehicle-status') { toggleVehicleCodeStatus(); return; }
28651:         if (action === 'fit-critical') { fitCriticalMissions(); return; }
28652:         if (action === 'scan-transport-sweep') { const queue = buildTransportSweepQueue(); showToast(queue.length ? `${queue.length} transport mission${queue.length === 1 ? '' : 's'} found` : 'No alliance patient transports found'); return; }
28653:         if (action === 'start-transport-sweep') { startTransportSweep(); return; }
28654:         if (action === 'stop-transport-sweep') { stopTransportSweep(); return; }
28655:         if (action === 'reset-session') { resetSessionPerformance(); return; }
28656:         if (action === 'clear-payout-history') { clearPayoutHistory(); return; }
28657:         if (action === 'critical-go') { focusMissionById(button.dataset.missionId, false); return; }
28658:         if (action === 'profile-save') { saveMapProfile(Number(button.dataset.slot)); return; }
28659:         if (action === 'profile-load') { loadMapProfile(Number(button.dataset.slot)); return; }
28660:         if (action === 'profile-delete') { deleteMapProfile(Number(button.dataset.slot)); return; }
28661:         if (action === 'export-config') { exportToolkitConfig(); return; }
28662:         if (action === 'import-config') { document.querySelector(`#${SCRIPT.panelId} [data-import-config-file]`)?.click?.(); return; }
28663:         if (action === 'reset-config') { resetToolkitConfiguration(); return; }
28664:         if (action === 'discord-test') { testDiscordWebhook(); return; }
28665:         if (action === 'discord-generate-post') { postDiscordFinancialReport(); return; }
28666:         if (action === 'discord-clear') { clearDiscordWebhook(); return; }
28667:         if (action === 'finance-archive-scan') { scanFinancialArchive(); return; }
28668:         if (action === 'finance-archive-cancel') { cancelFinancialArchiveScan(); return; }
28669:         if (action === 'finance-archive-export') { exportFinancialArchive(); return; }
28670:         if (action === 'finance-archive-import') { document.querySelector(`#${SCRIPT.panelId} [data-import-finance-file]`)?.click?.(); return; }
28671:         if (action === 'finance-archive-clear') { clearFinancialArchive(); return; }
28672:         if (action === 'finance-rules-refresh') { refreshFinancialIntelligenceFeeds(true).then(() => { renderFinanceVaultStatus(); showToast('GitHub financial intelligence refreshed'); }); return; }
28673:         if (action === 'test-payout-flash') {
28674:             const testAmount = Math.max(1000, Number(document.querySelector(`#${SCRIPT.panelId} [data-setting="payout-test-amount"]`)?.value) || state.payoutFlash.threshold);
28675:             const triggered = triggerPayoutFlash(testAmount, true, { source: 'personal', caption: 'Emergency Response Test' });
28676:             showToast(triggered ? 'Emergency flash test' : 'Emergency flash unavailable: map not detected');
28677:             return;
28678:         }
28679:         if (action === 'panel-reset') resetPanelPosition();
28680:     }
28681: 
28682:     function handleSettingChange(target) {
28683:         const setting = target.dataset.setting;
28684:         if (!setting) return;
28685: 
28686:         if (setting === 'mobile-mode' || setting === 'tablet-mode') {
28687:             const nextValue = ['auto', 'on', 'off'].includes(String(target.value)) ? String(target.value) : 'auto';
28688:             const previousLayout = activeDeviceLayout;
28689:             if (setting === 'mobile-mode') {
28690:                 state.mobileMode = nextValue;
28691:                 if (nextValue === 'on') state.tabletMode = 'off';
28692:             } else {
28693:                 state.tabletMode = nextValue;
28694:                 if (nextValue === 'on') state.mobileMode = 'off';
28695:             }
28696:             saveState();
28697:             applyRootAttributes();
28698:             refreshTabletModeUi();
28699:             if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
28700:                 clearTabletPanelSizing();
28701:                 clearTabletDockSizing();
28702:             }
28703:             fitControlToMap();
28704:             positionPanelOverlay(true);
28705:             showToast(activeDeviceLayout === 'mobile' ? 'iOS Mobile Mode active' : activeDeviceLayout === 'tablet' ? 'Tablet Mode active' : 'Desktop layout active');
28706:             return;
28707:         }
28708: 
28709:         if (setting === 'major-incident-minimum') {
28710:             state.majorIncidentFeed.minimumCredits = MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25000;
28711:             saveState();
28712:             updateUI();
28713:             refreshMissionSnapshots();
28714:             scheduleMajorIncidentFeedRender(0);
28715:             showToast(`Major Incident Feed: ${formatOperationalCompactCredits(state.majorIncidentFeed.minimumCredits)}+ credits`);
28716:             return;
28717:         }
28718: 
28719:         if (setting === 'coverage-radius') {
28720:             state.coverage.radiusMi = Number(target.value) || 10;
28721:             saveState();
28722:             updateUI();
28723:             scheduleCoverageRefresh();
28724:             return;
28725:         }
28726: 
28727:         if (setting === 'heatmap-source') state.heatmap.source = target.value === 'vehicles' ? 'vehicles' : 'stations';
28728:         if (setting === 'heatmap-service') state.heatmap.service = ['all', 'fire', 'ambulance', 'police', 'air', 'water'].includes(target.value) ? target.value : 'all';
28729:         if (setting === 'heatmap-radius') state.heatmap.radiusMi = Number(target.value) || 10;
28730:         if (setting === 'heatmap-opacity') state.heatmap.opacity = clamp(target.value, 0.12, 0.55, 0.30);
28731:         if (setting.startsWith('heatmap-')) {
28732:             saveState(); updateUI(); scheduleHeatmapRefresh(); return;
28733:         }
28734: 
28735: 
28736:         if (setting === 'transport-sweep-delay') {
28737:             state.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 2000;
28738:             saveState(); updateUI();
28739:             showToast(`Transport Sweep delay: ${state.transportSweep.delayMs / 1000}s`);
28740:             return;
28741:         }
28742:         if (setting === 'transport-sweep-max') {
28743:             state.transportSweep.maxPerRun = Math.round(clamp(target.value, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
28744:             saveState(); updateUI();
28745:             showToast(`Transport Sweep maximum: ${state.transportSweep.maxPerRun}`);
28746:             return;
28747:         }
28748: 
28749:         if (setting === 'resource-gap-radius') {
28750:             state.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25;
28751:             resourceGapAnalysisCache.clear();
28752:             saveState(); updateUI(); scheduleResourceGapRefresh(0); refreshVisibleMissionInspector();
28753:             showToast(`Resource Gap radius: ${state.resourceGap.radiusMi}mi`);
28754:             return;
28755:         }
28756: 
28757:         if (setting === 'stuck-threshold') {
28758:             state.stuckDetector.thresholdMin = Math.round(clamp(target.value, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
28759:             saveState();
28760:             updateUI();
28761:             scheduleStuckMissionRefresh(0);
28762:             showToast(`Stuck missions: ${state.stuckDetector.thresholdMin} minutes`);
28763:             return;
28764:         }
28765: 
28766:         if (setting === 'alliance-credit-minimum') {
28767:             state.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(target.value)) ? Number(target.value) : 0;
28768:             saveState();
28769:             updateUI();
28770:             scheduleAllianceCreditRefresh(0);
28771:             showToast(state.allianceCreditMinimum ? `Alliance credits: ${state.allianceCreditMinimum / 1000}K+` : 'Alliance credits: all values');
28772:             return;
28773:         }
28774: 
28775:         if (setting === 'discord-webhook') {
28776:             try {
28777:                 saveDiscordWebhookUrl(target.value);
28778:                 setDiscordStatus(target.value ? 'Webhook saved securely in Tampermonkey storage.' : 'Webhook removed.', 'good');
28779:             } catch (err) {
28780:                 setDiscordStatus(err?.message || 'Webhook URL is invalid.', 'bad');
28781:             }
28782:             return;
28783:         }
28784:         if (setting === 'discord-name') {
28785:             state.discordReport.webhookName = String(target.value || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
28786:             saveState(); updateUI();
28787:             return;
28788:         }
28789:         if (setting === 'discord-top-categories') {
28790:             state.discordReport.topCategories = [3, 5, 8].includes(Number(target.value)) ? Number(target.value) : 5;
28791:             invalidateDiscordFinancialPreview();
28792:             saveState(); updateUI();
28793:             return;
28794:         }
28795:         if (setting === 'discord-period') {
28796:             state.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'last90', 'last180', 'last365', 'allAvailable', 'session', 'sinceLast', 'custom'].includes(target.value) ? target.value : 'today';
28797:             invalidateDiscordFinancialPreview();
28798:             saveState(); updateUI();
28799:             return;
28800:         }
28801:         if (setting === 'discord-custom-start' || setting === 'discord-custom-end') {
28802:             const key = setting === 'discord-custom-start' ? 'customStart' : 'customEnd';
28803:             if (/^\d{4}-\d{2}-\d{2}$/u.test(String(target.value || ''))) state.discordReport[key] = String(target.value);
28804:             invalidateDiscordFinancialPreview();
28805:             saveState(); updateUI();
28806:             return;
28807:         }
28808:         if (setting === 'discord-comparison') {
28809:             state.discordReport.includeComparison = String(target.value) !== 'false';
28810:             invalidateDiscordFinancialPreview();
28811:             saveState(); updateUI();
28812:             return;
28813:         }
28814:         if (setting === 'discord-chart') {
28815:             state.discordReport.includeChart = String(target.value) !== 'false';
28816:             invalidateDiscordFinancialPreview();
28817:             saveState(); updateUI();
28818:             return;
28819:         }
28820: 
28821:         if (setting === 'discord-report-mode') {
28822:             state.discordReport.reportMode = ['executive', 'fullAudit'].includes(String(target.value)) ? String(target.value) : 'fullAudit';
28823:             invalidateDiscordFinancialPreview();
28824:             saveState(); updateUI();
28825:             return;
28826:         }
28827:         if (setting === 'discord-risk' || setting === 'discord-forecast') {
28828:             const key = setting === 'discord-risk' ? 'includeRisk' : 'includeForecast';
28829:             state.discordReport[key] = String(target.value) !== 'false';
28830:             invalidateDiscordFinancialPreview();
28831:             saveState(); updateUI();
28832:             return;
28833:         }
28834:         if (setting === 'finance-vault-enabled') {
28835:             state.financialVault.enabled = String(target.value) !== 'false';
28836:             saveState(); updateUI();
28837:             setFinanceVaultStatus(state.financialVault.enabled ? 'Local Financial Archive enabled.' : 'Local Financial Archive disabled; reports will scan MissionChief directly without retaining history.', 'neutral');
28838:             return;
28839:         }
28840:         if (setting === 'finance-vault-retention') {
28841:             state.financialVault.retentionDays = String(target.value) === 'all' ? 'all' : ([90, 180, 365, 730, 1825].includes(Number(target.value)) ? Number(target.value) : 'all');
28842:             saveState(); updateUI(); renderFinanceVaultStatus();
28843:             return;
28844:         }
28845:         if (setting === 'finance-rule-feed') {
28846:             state.financialVault.ruleFeedEnabled = String(target.value) !== 'false';
28847:             saveState();
28848:             refreshFinancialIntelligenceFeeds(true).then(() => { updateUI(); renderFinanceVaultStatus(); });
28849:             return;
28850:         }
28851: 
28852:         if (setting === 'payout-template') {
28853:             state.payoutFlash.template = PAYOUT_TEMPLATES[target.value] ? target.value : 'gta5';
28854:             disposePayoutMediaAudio();
28855:             saveState();
28856:             updateUI();
28857:             const hostedCue = PAYOUT_MEDIA_SOUNDS[state.payoutFlash.template];
28858:             showToast(hostedCue
28859:                 ? `${payoutTemplateMeta(state.payoutFlash.template).label} · ${hostedCue.label} ready`
28860:                 : `${payoutTemplateMeta(state.payoutFlash.template).label} payout template`);
28861:             return;
28862:         }
28863:         if (setting === 'payout-threshold') {
28864:             state.payoutFlash.threshold = Math.round(clamp(target.value, 1000, 1000000000, 10000));
28865:             saveState();
28866:             updateUI();
28867:             showToast(`Payout flash: ${state.payoutFlash.threshold.toLocaleString()}+`);
28868:             return;
28869:         }
28870:         if (setting === 'payout-duration') {
28871:             state.payoutFlash.durationMs = normalisePayoutFlashDuration(Number(target.value) * 1000);
28872:             saveState();
28873:             updateUI();
28874:             showToast(`Payout flash: ${state.payoutFlash.durationMs / 1000} seconds`);
28875:             return;
28876:         }
28877:         if (setting === 'payout-volume') {
28878:             state.payoutFlash.soundVolume = clamp(target.value, 0, 1, 0.35);
28879:             if (payoutMediaAudio && !payoutMediaAudio.paused) payoutMediaAudio.volume = state.payoutFlash.soundVolume;
28880:             saveState();
28881:             updateUI();
28882:             return;
28883:         }
28884:         if (setting === 'payout-test-amount') return;
28885: 
28886:         if (setting === 'auto-night-start') state.autoNight.nightStart = target.value || '19:00';
28887:         if (setting === 'auto-day-start') state.autoNight.dayStart = target.value || '07:00';
28888:         if (setting === 'auto-night-theme') state.autoNight.nightTheme = normaliseTheme(target.value);
28889:         if (setting === 'auto-day-theme') state.autoNight.dayTheme = normaliseTheme(target.value);
28890: 
28891:         if (setting.startsWith('auto-')) {
28892:             state.autoNight.lastBucket = '';
28893:             saveState();
28894:             runAutoNight(true);
28895:             updateUI();
28896:         }
28897:     }
28898: 
28899:     function updateUI() {
28900:         applyRootAttributes();
28901:         if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(40);
28902:         else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
28903: 
28904:         const control = document.getElementById(SCRIPT.controlId);
28905:         const panel = document.getElementById(SCRIPT.panelId);
28906: 
28907:         if (control) {
28908:             for (const pos of Object.keys(POSITIONS)) control.classList.toggle(`mcms-pos-${pos}`, state.position === pos);
28909:             control.style.setProperty('--mcms-nudge-x', `${state.nudge.x}px`);
28910:             control.style.setProperty('--mcms-nudge-y', `${state.nudge.y}px`);
28911:             const controlToggleValues = {
28912:                 allianceMissions: state.visibility.allianceMissions,
28913:                 myMissions: state.visibility.myMissions,
28914:                 vehicles: state.visibility.vehicles,
28915:                 buildings: state.visibility.buildings,
28916:                 allianceCredits: state.allianceCredits,
28917:                 missionAge: state.missionAge,
28918:                 transportWatcher: state.transportWatcher,
28919:                 unitCommitment: state.unitCommitment,
28920:                 criticalView: criticalViewActive
28921:             };
28922:             control.querySelectorAll('[data-toggle]').forEach(btn => {
28923:                 const on = Boolean(controlToggleValues[btn.dataset.toggle]);
28924:                 btn.classList.toggle('mcms-on', on);
28925:                 btn.setAttribute('aria-pressed', String(on));
28926:                 btn.dataset.mcmsState = on ? 'on' : 'off';
28927:             });
28928: 
28929:             const vehicleStatusButton = control.querySelector('[data-action="open-vehicle-status"]');
28930:             if (vehicleStatusButton) {
28931:                 const open = Boolean(document.getElementById(SCRIPT.vehicleStatusId)?.classList?.contains('mcms-open'));
28932:                 vehicleStatusButton.classList.toggle('mcms-on', open);
28933:                 vehicleStatusButton.setAttribute('aria-pressed', String(open));
28934:                 vehicleStatusButton.dataset.mcmsState = open ? 'on' : 'off';
28935:             }
28936: 
28937:             const missionAgeWatchButton = control.querySelector('[data-action="open-critical-drawer"]');
28938:             if (missionAgeWatchButton) {
28939:                 const open = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
28940:                 missionAgeWatchButton.classList.toggle('mcms-on', open);
28941:                 missionAgeWatchButton.setAttribute('aria-pressed', String(open));
28942:                 missionAgeWatchButton.dataset.mcmsState = open ? 'on' : 'off';
28943:             }
28944: 
28945:             const economyButton = control.querySelector('.mcms-economy-btn');
28946:             if (economyButton) {
28947:                 const on = Boolean(state.economyMode);
28948:                 const label = on ? 'Disable Economy Mode' : 'Enable Economy Mode';
28949:                 economyButton.classList.toggle('mcms-on', on);
28950:                 economyButton.setAttribute('aria-pressed', String(on));
28951:                 economyButton.setAttribute('aria-label', label);
28952:                 economyButton.title = label;
28953:                 economyButton.dataset.mcmsState = on ? 'on' : 'off';
28954:             }
28955: 
28956:             const dockToggleButton = control.querySelector('.mcms-dock-toggle-btn');
28957:             if (dockToggleButton) {
28958:                 const open = state.commandBarOpen !== false;
28959:                 const label = open ? 'Collapse command bar' : 'Expand command bar';
28960:                 dockToggleButton.classList.toggle('mcms-open', open);
28961:                 dockToggleButton.setAttribute('aria-expanded', String(open));
28962:                 dockToggleButton.setAttribute('aria-label', label);
28963:                 dockToggleButton.title = label;
28964:                 const icon = dockToggleButton.querySelector('.mcms-dock-toggle-icon');
28965:                 if (icon) icon.textContent = open ? '▴' : '▾';
28966:             }
28967:         }
28968: 
28969:         if (!panel) return;
28970: 
28971:         refreshTabletModeUi(panel);
28972:         panel.querySelectorAll('.mcms-tab-btn').forEach(btn => {
28973:             const active = btn.dataset.tab === state.activeTab;
28974:             btn.classList.toggle('mcms-active', active);
28975:             btn.setAttribute('aria-selected', String(active));
28976:             btn.tabIndex = active ? 0 : -1;
28977:         });
28978:         panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => {
28979:             const active = tabPanel.dataset.panel === state.activeTab;
28980:             tabPanel.classList.toggle('mcms-active', active);
28981:             tabPanel.hidden = !active;
28982:         });
28983:         const panelOpen = panel.classList.contains('mcms-open');
28984:         panel.setAttribute('aria-hidden', String(!panelOpen));
28985:         control?.querySelector('.mcms-menu-btn')?.setAttribute('aria-expanded', String(panelOpen));
28986:         panel.querySelectorAll('.mcms-ui-theme-btn').forEach(btn => {
28987:             const active = btn.dataset.uiTheme === state.uiTheme;
28988:             btn.classList.toggle('mcms-active', active);
28989:             btn.setAttribute('aria-pressed', String(active));
28990:         });
28991:         panel.querySelectorAll('.mcms-theme-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.theme === state.theme));
28992:         panel.querySelectorAll('.mcms-position-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.position === state.position));
28993: 
28994:         const toggleValues = {
28995:             clean: state.cleanMode,
28996:             markerFocus: state.markerFocus,
28997:             missionPulse: state.missionPulse,
28998:             roadPriority: state.roadPriority,
28999:             coverage: state.coverage.enabled,
29000:             heatmap: state.heatmap.enabled,
29001:             shortcuts: state.shortcuts,
29002:             autoLoadAllVehicles: state.autoLoadAllVehicles,
29003:             allianceBuildingsMapBlocker: state.allianceBuildingsMap === false,
29004:             majorIncidentFeed: state.majorIncidentFeed.enabled,
29005:             missionLockAudio: state.missionLockAudio,
29006:             autoNight: state.autoNight.enabled,
29007:             payoutFlash: state.payoutFlash.enabled,
29008:             payoutSound: state.payoutFlash.soundEnabled,
29009:             missionInspector: state.missionInspector,
29010:             missionValue: state.missionValue,
29011:             stuckDetector: state.stuckDetector.enabled,
29012:             missionSpawn: state.missionSpawn.enabled,
29013:             resourceGap: state.resourceGap.enabled,
29014:             allianceMissions: state.visibility.allianceMissions,
29015:             myMissions: state.visibility.myMissions,
29016:             vehicles: state.visibility.vehicles,
29017:             buildings: state.visibility.buildings,
29018:             allianceCredits: state.allianceCredits,
29019:             missionAge: state.missionAge,
29020:             transportWatcher: state.transportWatcher,
29021:             unitCommitment: state.unitCommitment,
29022:             criticalView: criticalViewActive
29023:         };
29024: 
29025:         panel.querySelectorAll('[data-toggle]').forEach(btn => {
29026:             const key = btn.dataset.toggle;
29027:             const on = Boolean(toggleValues[key]);
29028:             btn.classList.toggle('mcms-on', on);
29029:             const pill = btn.querySelector('.mcms-pill');
29030:             if (pill) pill.textContent = key === 'coverage' ? (on ? `${state.coverage.radiusMi}mi` : 'OFF') : key === 'heatmap' ? (on ? `${state.heatmap.radiusMi}mi` : 'OFF') : (on ? 'ON' : 'OFF');
29031:         });
29032: 
29033:         const majorIncidentMinimum = panel.querySelector('[data-setting="major-incident-minimum"]');
29034:         if (majorIncidentMinimum) majorIncidentMinimum.value = String(state.majorIncidentFeed.minimumCredits);
29035:         const radius = panel.querySelector('[data-setting="coverage-radius"]');
29036:         if (radius) radius.value = String(state.coverage.radiusMi);
29037:         const heatmapSource = panel.querySelector('[data-setting="heatmap-source"]');
29038:         if (heatmapSource) heatmapSource.value = state.heatmap.source;
29039:         const heatmapService = panel.querySelector('[data-setting="heatmap-service"]');
29040:         if (heatmapService) heatmapService.value = state.heatmap.service;
29041:         const heatmapRadius = panel.querySelector('[data-setting="heatmap-radius"]');
29042:         if (heatmapRadius) heatmapRadius.value = String(state.heatmap.radiusMi);
29043:         const heatmapOpacity = panel.querySelector('[data-setting="heatmap-opacity"]');
29044:         if (heatmapOpacity) heatmapOpacity.value = String(state.heatmap.opacity);
29045:         const allianceCreditMinimum = panel.querySelector('[data-setting="alliance-credit-minimum"]');
29046:         if (allianceCreditMinimum) allianceCreditMinimum.value = String(state.allianceCreditMinimum);
29047:         const transportSweepDelay = panel.querySelector('[data-setting="transport-sweep-delay"]');
29048:         if (transportSweepDelay) transportSweepDelay.value = String(state.transportSweep.delayMs);
29049:         const transportSweepMax = panel.querySelector('[data-setting="transport-sweep-max"]');
29050:         if (transportSweepMax) transportSweepMax.value = String(state.transportSweep.maxPerRun);
29051:         if (panel.classList.contains('mcms-open') && state.activeTab === 'resources') renderTransportSweepPanel();
29052:         const payoutTemplate = panel.querySelector('[data-setting="payout-template"]');
29053:         if (payoutTemplate) payoutTemplate.value = state.payoutFlash.template;
29054:         const resourceGapRadius = panel.querySelector('[data-setting="resource-gap-radius"]'); if (resourceGapRadius) resourceGapRadius.value = String(state.resourceGap.radiusMi);
29055:         const stuckThreshold = panel.querySelector('[data-setting="stuck-threshold"]');
29056:         if (stuckThreshold) stuckThreshold.value = String(state.stuckDetector.thresholdMin);
29057:         const payoutThreshold = panel.querySelector('[data-setting="payout-threshold"]');
29058:         if (payoutThreshold) payoutThreshold.value = String(state.payoutFlash.threshold);
29059:         const payoutDuration = panel.querySelector('[data-setting="payout-duration"]');
29060:         if (payoutDuration) payoutDuration.value = String(state.payoutFlash.durationMs / 1000);
29061:         const payoutVolume = panel.querySelector('[data-setting="payout-volume"]');
29062:         if (payoutVolume) payoutVolume.value = String(state.payoutFlash.soundVolume);
29063:         const discordWebhook = panel.querySelector('[data-setting="discord-webhook"]');
29064:         if (discordWebhook && document.activeElement !== discordWebhook) discordWebhook.value = getDiscordWebhookUrl();
29065:         const discordName = panel.querySelector('[data-setting="discord-name"]');
29066:         if (discordName && document.activeElement !== discordName) discordName.value = state.discordReport.webhookName;
29067:         const discordTopCategories = panel.querySelector('[data-setting="discord-top-categories"]');
29068:         if (discordTopCategories) discordTopCategories.value = String(state.discordReport.topCategories);
29069:         const discordPeriod = panel.querySelector('[data-setting="discord-period"]');
29070:         if (discordPeriod) discordPeriod.value = state.discordReport.period;
29071:         const discordCustomStart = panel.querySelector('[data-setting="discord-custom-start"]');
29072:         if (discordCustomStart && document.activeElement !== discordCustomStart) discordCustomStart.value = state.discordReport.customStart;
29073:         const discordCustomEnd = panel.querySelector('[data-setting="discord-custom-end"]');
29074:         if (discordCustomEnd && document.activeElement !== discordCustomEnd) discordCustomEnd.value = state.discordReport.customEnd;
29075:         const discordComparison = panel.querySelector('[data-setting="discord-comparison"]');
29076:         if (discordComparison) discordComparison.value = String(state.discordReport.includeComparison);
29077:         const discordChart = panel.querySelector('[data-setting="discord-chart"]');
29078:         if (discordChart) discordChart.value = String(state.discordReport.includeChart);
29079:         const discordReportMode = panel.querySelector('[data-setting="discord-report-mode"]');
29080:         if (discordReportMode) discordReportMode.value = state.discordReport.reportMode;
29081:         const discordRisk = panel.querySelector('[data-setting="discord-risk"]');
29082:         if (discordRisk) discordRisk.value = String(state.discordReport.includeRisk);
29083:         const discordForecast = panel.querySelector('[data-setting="discord-forecast"]');
29084:         if (discordForecast) discordForecast.value = String(state.discordReport.includeForecast);
29085:         const financeVaultEnabled = panel.querySelector('[data-setting="finance-vault-enabled"]');
29086:         if (financeVaultEnabled) financeVaultEnabled.value = String(state.financialVault.enabled);
29087:         const financeVaultRetention = panel.querySelector('[data-setting="finance-vault-retention"]');
29088:         if (financeVaultRetention) financeVaultRetention.value = String(state.financialVault.retentionDays);
29089:         const financeRuleFeed = panel.querySelector('[data-setting="finance-rule-feed"]');
29090:         if (financeRuleFeed) financeRuleFeed.value = String(state.financialVault.ruleFeedEnabled);
29091:         setDiscordStatus(discordFinanceStatus, discordFinanceStatusTone);
29092:         if (panel.classList.contains('mcms-open') && state.activeTab === 'discord') renderFinanceVaultStatus();
29093:         const nightStart = panel.querySelector('[data-setting="auto-night-start"]');
29094:         if (nightStart) nightStart.value = state.autoNight.nightStart;
29095:         const dayStart = panel.querySelector('[data-setting="auto-day-start"]');
29096:         if (dayStart) dayStart.value = state.autoNight.dayStart;
29097:         const nightTheme = panel.querySelector('[data-setting="auto-night-theme"]');
29098:         if (nightTheme) nightTheme.value = state.autoNight.nightTheme;
29099:         const dayTheme = panel.querySelector('[data-setting="auto-day-theme"]');
29100:         if (dayTheme) dayTheme.value = state.autoNight.dayTheme;
29101:         const economyStatus = panel.querySelector('.mcms-economy-status');
29102:         if (economyStatus) economyStatus.textContent = state.economyMode
29103:             ? 'Economy Mode is ON: static visual effects, adaptive refresh intervals and off-screen vehicle/building layer culling are active.'
29104:             : 'Economy Mode is OFF. Use the leaf button beside the map-menu opener to reduce CPU, GPU and marker workload.';
29105:         const nudge = panel.querySelector('.mcms-nudge-value');
29106:         if (nudge) nudge.textContent = `X ${state.nudge.x} / Y ${state.nudge.y}`;
29107:         if (panel.classList.contains('mcms-open') && state.activeTab === 'settings') renderProfiles();
29108:         if ((panel.classList.contains('mcms-open') && state.activeTab === 'ops') || operationalUiIsVisible()) renderOperationalPanels();
29109:     }
29110: 
29111:     function ensureUi() {
29112:         const mapEl = getLargestLeafletMap();
29113:         if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)) createPanel();
29114:         if (mapEl) {
29115:             createControl(mapEl);
29116:             const map = findLeafletMapInstance(false);
29117:             if (state.economyMode && map) { applyLeafletEconomyPolicy(map); scheduleEconomyLayerSync(0); }
29118:             if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(0);
29119:             else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
29120:             const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
29121:             if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay, mapEl);
29122:         }
29123:         return Boolean(mapEl && document.getElementById(SCRIPT.controlId));
29124:     }
29125: 
29126:     function mutationBelongsToToolkit(mutation) {
29127:         const target = mutation.target;
29128:         const toolkitTarget = Boolean(
29129:             target &&
29130:             target.nodeType === 1 &&
29131:             (
29132:                 target.id === SCRIPT.controlId ||
29133:                 target.id === SCRIPT.panelId ||
29134:                 target.id === SCRIPT.toastId ||
29135:                 target.id === SCRIPT.payoutFlashId ||
29136:                 target.id === SCRIPT.criticalDrawerId ||
29137:                 target.id === SCRIPT.vehicleStatusId ||
29138:                 target.id === SCRIPT.majorIncidentFeedId ||
29139:                 target.id === SCRIPT.missionInspectorId ||
29140:                 target.closest?.(`#${SCRIPT.controlId}`) ||
29141:                 target.closest?.(`#${SCRIPT.panelId}`) ||
29142:                 target.closest?.(`#${SCRIPT.toastId}`) ||
29143:                 target.closest?.(`#${SCRIPT.payoutFlashId}`) ||
29144:                 target.closest?.(`#${SCRIPT.criticalDrawerId}`) ||
29145:                 target.closest?.(`#${SCRIPT.vehicleStatusId}`) ||
29146:                 target.closest?.(`#${SCRIPT.majorIncidentFeedId}`) ||
29147:                 target.closest?.(`#${SCRIPT.missionInspectorId}`)
29148:             )
29149:         );
29150:         if (toolkitTarget) return true;
29151: 
29152:         if (mutation.type === 'attributes' && mutation.attributeName === 'class' && target?.classList) {
29153:             for (const className of target.classList) {
29154:                 if (String(className).startsWith('mcms-')) return true;
29155:             }
29156:         }
29157: 
29158:         const toolkitSelector = '.mcms-alliance-credit-icon, .mcms-alliance-credit-badge, .mcms-mission-age-icon, .mcms-mission-age-badge, .mcms-unit-commitment-icon, .mcms-unit-commitment-badge, .mcms-transport-watcher-icon, .mcms-transport-watcher-badge, .mcms-resource-gap-icon, .mcms-resource-gap-badge, .mcms-stuck-mission-icon, .mcms-stuck-mission-badge, .mcms-mission-spawn-label-icon, .mcms-mission-spawn-label';
29159:         let elementCount = 0;
29160:         for (const collection of [mutation.addedNodes, mutation.removedNodes]) {
29161:             if (!collection?.length) continue;
29162:             for (const node of collection) {
29163:                 if (!node || node.nodeType !== 1) continue;
29164:                 elementCount += 1;
29165:                 if (!(node.matches?.(toolkitSelector) || node.querySelector?.(toolkitSelector))) return false;
29166:             }
29167:         }
29168:         return elementCount > 0;
29169:     }
29170: 
29171:     function mutationAddsLeafletMarkerIcon(mutation) {
29172:         if (!mutation || mutation.type !== 'childList' || !mutation.addedNodes?.length) return false;
29173: 
29174:         for (const node of mutation.addedNodes) {
29175:             if (!node || node.nodeType !== 1) continue;
29176:             if (node.matches?.('.mcms-alliance-credit-icon, .mcms-mission-age-icon, .mcms-unit-commitment-icon, .mcms-transport-watcher-icon, .mcms-resource-gap-icon, .mcms-stuck-mission-icon, .mcms-mission-spawn-label-icon') || node.querySelector?.('.mcms-alliance-credit-icon, .mcms-mission-age-icon, .mcms-unit-commitment-icon, .mcms-transport-watcher-icon, .mcms-resource-gap-icon, .mcms-stuck-mission-icon, .mcms-mission-spawn-label-icon')) continue;
29177:             if (node.matches?.('.leaflet-marker-icon')) return true;
29178:             if (node.querySelector?.('.leaflet-marker-icon')) return true;
29179:         }
29180: 
29181:         return false;
29182:     }
29183: 
29184:     function mutationTouchesSelector(mutation, selector) {
29185:         const target = mutation?.target;
29186:         if (target?.nodeType === 1 && (target.matches?.(selector) || target.closest?.(selector))) return true;
29187:         for (const collection of [mutation?.addedNodes, mutation?.removedNodes]) {
29188:             if (!collection?.length) continue;
29189:             for (const node of collection) {
29190:                 if (!node || node.nodeType !== 1) continue;
29191:                 if (node.matches?.(selector) || node.querySelector?.(selector)) return true;
29192:             }
29193:         }
29194:         return false;
29195:     }
29196: 
29197:     function mutationRemovesToolkitUi(mutation) {
29198:         for (const node of mutation?.removedNodes || []) {
29199:             if (!node || node.nodeType !== 1) continue;
29200:             if ([SCRIPT.panelId, SCRIPT.controlId, SCRIPT.majorIncidentFeedId].includes(node.id)) return true;
29201:             if (node.querySelector?.(`#${SCRIPT.panelId}, #${SCRIPT.controlId}, #${SCRIPT.majorIncidentFeedId}`)) return true;
29202:         }
29203:         return false;
29204:     }
29205: 
29206:     function mutationAffectsMissionData(mutation) {
29207:         return mutationTouchesSelector(mutation, '.leaflet-marker-pane, .leaflet-marker-icon, [id^="mission_"], #missions, #mission_list, .missionSideBarEntry, .mission-side-bar-entry, [data-mission-id]');
29208:     }
29209: 
29210:     function mutationAffectsMapLayout(mutation) {
29211:         const target = mutation?.target;
29212:         if (target?.nodeType === 1) {
29213:             if (target.matches?.('#map, #map_outer, .leaflet-container')) return true;
29214:             if (target.closest?.('.navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
29215:         }
29216:         for (const collection of [mutation?.addedNodes, mutation?.removedNodes]) {
29217:             if (!collection?.length) continue;
29218:             for (const node of collection) {
29219:                 if (!node || node.nodeType !== 1) continue;
29220:                 if (node.matches?.('#map, #map_outer, .leaflet-container, .navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
29221:                 if (node.querySelector?.('#map, #map_outer, .leaflet-container, .navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
29222:             }
29223:         }
29224:         return false;
29225:     }
29226: 
29227: 
29228:     const ALLIANCE_BUILDINGS_MAP_NOTICE_ID = 'mcms-alliance-buildings-map-notice';
29229: 
29230:     function findAllianceBuildingsMapElement() {
29231:         if (!isAllianceBuildingsContext()) return null;
29232:         const candidates = Array.from(document.querySelectorAll('#verband-gebauede-map, #verband-gebaeude-map, #map, #map_outer .leaflet-container, [id*="gebauede"][id*="map"], [id*="gebaeude"][id*="map"], .leaflet-container'));
29233:         return candidates.find(element => {
29234:             if (!element || element.closest(`#${SCRIPT.controlId}, #${SCRIPT.panelId}, #${SCRIPT.criticalDrawerId}, #${SCRIPT.vehicleStatusId}`)) return false;
29235:             const rect = element.getBoundingClientRect?.();
29236:             return !rect || rect.width >= 120 || rect.height >= 120 || element.id === 'map' || element.id === 'verband-gebauede-map' || element.id === 'verband-gebaeude-map';
29237:         }) || null;
29238:     }
29239: 
29240:     function findResponsiveColumn(element) {
```

## Main mutation observer and mission-data mutation routing

Canonical lines 29180–29520

```javascript
29180: 
29181:         return false;
29182:     }
29183: 
29184:     function mutationTouchesSelector(mutation, selector) {
29185:         const target = mutation?.target;
29186:         if (target?.nodeType === 1 && (target.matches?.(selector) || target.closest?.(selector))) return true;
29187:         for (const collection of [mutation?.addedNodes, mutation?.removedNodes]) {
29188:             if (!collection?.length) continue;
29189:             for (const node of collection) {
29190:                 if (!node || node.nodeType !== 1) continue;
29191:                 if (node.matches?.(selector) || node.querySelector?.(selector)) return true;
29192:             }
29193:         }
29194:         return false;
29195:     }
29196: 
29197:     function mutationRemovesToolkitUi(mutation) {
29198:         for (const node of mutation?.removedNodes || []) {
29199:             if (!node || node.nodeType !== 1) continue;
29200:             if ([SCRIPT.panelId, SCRIPT.controlId, SCRIPT.majorIncidentFeedId].includes(node.id)) return true;
29201:             if (node.querySelector?.(`#${SCRIPT.panelId}, #${SCRIPT.controlId}, #${SCRIPT.majorIncidentFeedId}`)) return true;
29202:         }
29203:         return false;
29204:     }
29205: 
29206:     function mutationAffectsMissionData(mutation) {
29207:         return mutationTouchesSelector(mutation, '.leaflet-marker-pane, .leaflet-marker-icon, [id^="mission_"], #missions, #mission_list, .missionSideBarEntry, .mission-side-bar-entry, [data-mission-id]');
29208:     }
29209: 
29210:     function mutationAffectsMapLayout(mutation) {
29211:         const target = mutation?.target;
29212:         if (target?.nodeType === 1) {
29213:             if (target.matches?.('#map, #map_outer, .leaflet-container')) return true;
29214:             if (target.closest?.('.navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
29215:         }
29216:         for (const collection of [mutation?.addedNodes, mutation?.removedNodes]) {
29217:             if (!collection?.length) continue;
29218:             for (const node of collection) {
29219:                 if (!node || node.nodeType !== 1) continue;
29220:                 if (node.matches?.('#map, #map_outer, .leaflet-container, .navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
29221:                 if (node.querySelector?.('#map, #map_outer, .leaflet-container, .navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
29222:             }
29223:         }
29224:         return false;
29225:     }
29226: 
29227: 
29228:     const ALLIANCE_BUILDINGS_MAP_NOTICE_ID = 'mcms-alliance-buildings-map-notice';
29229: 
29230:     function findAllianceBuildingsMapElement() {
29231:         if (!isAllianceBuildingsContext()) return null;
29232:         const candidates = Array.from(document.querySelectorAll('#verband-gebauede-map, #verband-gebaeude-map, #map, #map_outer .leaflet-container, [id*="gebauede"][id*="map"], [id*="gebaeude"][id*="map"], .leaflet-container'));
29233:         return candidates.find(element => {
29234:             if (!element || element.closest(`#${SCRIPT.controlId}, #${SCRIPT.panelId}, #${SCRIPT.criticalDrawerId}, #${SCRIPT.vehicleStatusId}`)) return false;
29235:             const rect = element.getBoundingClientRect?.();
29236:             return !rect || rect.width >= 120 || rect.height >= 120 || element.id === 'map' || element.id === 'verband-gebauede-map' || element.id === 'verband-gebaeude-map';
29237:         }) || null;
29238:     }
29239: 
29240:     function findResponsiveColumn(element) {
29241:         let current = element;
29242:         for (let depth = 0; current && current !== document.body && depth < 7; depth += 1, current = current.parentElement) {
29243:             const className = typeof current.className === 'string' ? current.className : '';
29244:             if (/\bcol-(?:xs|sm|md|lg|xl|xxl)-\d+\b/u.test(className)) return current;
29245:         }
29246:         return element?.parentElement || null;
29247:     }
29248: 
29249:     function findAllianceBuildingsListColumn(mapColumn) {
29250:         const row = mapColumn?.parentElement;
29251:         if (!row) return null;
29252:         const siblings = Array.from(row.children).filter(child => child !== mapColumn);
29253:         return siblings.find(child => child.querySelector?.('table')) || siblings.find(child => /\bcol-(?:xs|sm|md|lg|xl|xxl)-\d+\b/u.test(String(child.className || ''))) || mapColumn.nextElementSibling;
29254:     }
29255: 
29256:     function allianceBuildingsMapNoticeHtml(enabled) {
29257:         const blocked = !enabled;
29258:         return `
29259:             <span class="mcms-alliance-map-copy">
29260:                 <strong>${blocked ? 'Alliance Map Blocker ON' : 'Alliance Map Blocker OFF'}</strong>
29261:                 <small>${blocked ? 'The Alliance Buildings / Courses list remains available at full width. Its map tiles and alliance marker attachment are blocked.' : 'Turn the blocker on to stop the heavy map in the Alliance Buildings / Courses menu.'}</small>
29262:             </span>
29263:             <button type="button" data-mcms-alliance-map-toggle="${blocked ? 'restore' : 'block'}">${blocked ? 'Disable blocker & reload' : 'Enable blocker & reload'}</button>
29264:         `;
29265:     }
29266: 
29267:     function renderAllianceBuildingsMapPreference() {
29268:         if (!isAllianceBuildingsContext()) return false;
29269:         const root = document.documentElement;
29270:         const enabled = state.allianceBuildingsMap !== false;
29271:         root.setAttribute('data-mcms-alliance-buildings-page', 'true');
29272:         root.setAttribute('data-mcms-alliance-buildings-map', enabled ? 'enabled' : 'disabled');
29273: 
29274:         const mapElement = findAllianceBuildingsMapElement();
29275:         if (!mapElement) return false;
29276:         const mapColumn = findResponsiveColumn(mapElement);
29277:         const listColumn = findAllianceBuildingsListColumn(mapColumn);
29278:         if (!mapColumn) return false;
29279: 
29280:         mapColumn.classList.toggle('mcms-alliance-buildings-map-column', !enabled);
29281:         mapColumn.toggleAttribute('data-mcms-alliance-map-column', !enabled);
29282:         mapColumn.setAttribute('aria-hidden', String(!enabled));
29283:         if (listColumn) {
29284:             listColumn.classList.toggle('mcms-alliance-buildings-list-column', !enabled);
29285:             listColumn.toggleAttribute('data-mcms-alliance-list-column', !enabled);
29286:         }
29287: 
29288:         let notice = document.getElementById(ALLIANCE_BUILDINGS_MAP_NOTICE_ID);
29289:         const target = enabled ? mapColumn : (listColumn || mapColumn.parentElement || document.body);
29290:         if (!notice) {
29291:             notice = document.createElement('div');
29292:             notice.id = ALLIANCE_BUILDINGS_MAP_NOTICE_ID;
29293:         }
29294:         notice.classList.toggle('mcms-alliance-map-enabled', enabled);
29295:         notice.innerHTML = allianceBuildingsMapNoticeHtml(enabled);
29296:         if (notice.parentElement !== target) target.insertBefore(notice, target.firstChild || null);
29297:         return true;
29298:     }
29299: 
29300:     function pruneRuntimeCaches(now = Date.now()) {
29301:         for (const [missionId, panel] of missionPanelCache.entries()) {
29302:             if (!panel?.isConnected) missionPanelCache.delete(missionId);
29303:         }
29304:         for (const [missionId, cached] of missionSnapshotCache.entries()) {
29305:             if (liveMissionSnapshots.has(missionId)) continue;
29306:             if (now - Number(cached?.lastUsed || now) > MISSION_CACHE_RETENTION_MS) missionSnapshotCache.delete(missionId);
29307:         }
29308:         for (const missionId of missionOverlayVersions.keys()) {
29309:             if (!missionOverlayData.has(missionId)) missionOverlayVersions.delete(missionId);
29310:         }
29311:         for (const [name, cached] of markerRegistryCache.entries()) {
29312:             if (now - Number(cached?.createdAt || now) > RUNTIME_CACHE_PRUNE_MS) markerRegistryCache.delete(name);
29313:         }
29314:         for (const [missionId, cached] of criticalMissionStableCache.entries()) {
29315:             if (liveMissionSnapshots.has(missionId)) continue;
29316:             if (now - Number(cached?.lastSeen || now) > MISSION_CACHE_RETENTION_MS) criticalMissionStableCache.delete(missionId);
29317:         }
29318:         for (const [key, cached] of resourceGapAnalysisCache.entries()) {
29319:             if (now - Number(cached?.createdAt || now) > Math.max(2 * RESOURCE_GAP_REFRESH_MS, RUNTIME_CACHE_PRUNE_MS)) resourceGapAnalysisCache.delete(key);
29320:         }
29321:         if (resourceGapAnalysisCache.size > 180) {
29322:             const ordered = Array.from(resourceGapAnalysisCache.entries()).sort((a, b) => Number(a[1]?.createdAt || 0) - Number(b[1]?.createdAt || 0));
29323:             for (const [key] of ordered.slice(0, resourceGapAnalysisCache.size - 180)) resourceGapAnalysisCache.delete(key);
29324:         }
29325:         const currentVehicleLayers = new Set(getVehicleMarkerLayers());
29326:         const currentBuildingLayers = new Set(getBuildingMarkerLayers());
29327:         for (const layer of Array.from(economyHiddenVehicleLayers)) {
29328:             if (!layer || (!layer._map && !currentVehicleLayers.has(layer))) economyHiddenVehicleLayers.delete(layer);
29329:         }
29330:         for (const layer of Array.from(economyHiddenBuildingLayers)) {
29331:             if (!layer || (!layer._map && !currentBuildingLayers.has(layer))) economyHiddenBuildingLayers.delete(layer);
29332:         }
29333:         if (!state.resourceGap.enabled) {
29334:             resourceGapAnalysisCache.clear();
29335:             resourceGapVehicleContextCache = { key: '', createdAt: 0, available: [], byToken: new Map() };
29336:         }
29337:         if (!state.heatmap.enabled && heatmapSourceCache.points.length) heatmapSourceCache = { key: '', createdAt: 0, points: [] };
29338:     }
29339: 
29340:     function installAllianceBuildingsPageOptimisation() {
29341:         const initiallyInContext = isAllianceBuildingsContext();
29342:         const enabled = state.allianceBuildingsMap !== false;
29343: 
29344:         let renderTimer = null;
29345:         const renderWhenRelevant = () => {
29346:             if (!isAllianceBuildingsContext()) {
29347:                 document.getElementById(ALLIANCE_BUILDINGS_MAP_NOTICE_ID)?.remove();
29348:                 document.querySelectorAll('.mcms-alliance-buildings-map-column').forEach(element => element.classList.remove('mcms-alliance-buildings-map-column'));
29349:                 document.querySelectorAll('.mcms-alliance-buildings-list-column').forEach(element => element.classList.remove('mcms-alliance-buildings-list-column'));
29350:                 clearAllianceBuildingsEarlyContext();
29351:                 return false;
29352:             }
29353:             if (!enabled) optimiseAllianceBuildingsCourseTableEarly();
29354:             return renderAllianceBuildingsMapPreference();
29355:         };
29356: 
29357:         if (initiallyInContext || !enabled) {
29358:             renderWhenRelevant();
29359:             runtimeSetTimeout(renderWhenRelevant, 40);
29360:             runtimeSetTimeout(renderWhenRelevant, 300);
29361:             runtimeSetTimeout(renderWhenRelevant, 1200);
29362: 
29363:             const pageObserver = runtimeTrackObserver(new MutationObserver(mutations => {
29364:                 if (!mutations.some(mutation => mutation.addedNodes?.length || mutation.removedNodes?.length)) return;
29365:                 runtimeClearTimeout(renderTimer);
29366:                 renderTimer = runtimeSetTimeout(() => {
29367:                     renderTimer = null;
29368:                     renderWhenRelevant();
29369:                 }, 0);
29370:             }));
29371:             pageObserver.observe(document.body, { childList: true, subtree: true });
29372:         }
29373: 
29374:         runtimeListen(document, 'click', event => {
29375:             const button = closestEventTarget(event, '[data-mcms-alliance-map-toggle]');
29376:             if (!button) return;
29377:             event.preventDefault();
29378:             event.stopPropagation();
29379:             state.allianceBuildingsMap = button.dataset.mcmsAllianceMapToggle === 'restore';
29380:             saveState();
29381:             button.disabled = true;
29382:             button.textContent = 'Reloading…';
29383:             runtimeSetTimeout(() => location.reload(), 120);
29384:         }, true);
29385: 
29386:         runtimeOnCleanup(() => {
29387:             document.getElementById(ALLIANCE_BUILDINGS_MAP_NOTICE_ID)?.remove();
29388:             document.querySelectorAll('.mcms-alliance-buildings-map-column').forEach(element => element.classList.remove('mcms-alliance-buildings-map-column'));
29389:             document.querySelectorAll('.mcms-alliance-buildings-list-column').forEach(element => element.classList.remove('mcms-alliance-buildings-list-column'));
29390:             document.querySelectorAll('[data-mcms-alliance-map-column], [data-mcms-alliance-list-column]').forEach(element => {
29391:                 element.removeAttribute('data-mcms-alliance-map-column');
29392:                 element.removeAttribute('data-mcms-alliance-list-column');
29393:             });
29394:             document.documentElement?.removeAttribute('data-mcms-alliance-buildings-page');
29395:         });
29396: 
29397:         return initiallyInContext && !enabled;
29398:     }
29399: 
29400: 
29401:     function connectMainMutationObserver() {
29402:         if (!mainMutationObserver || runtime.destroyed || !document.body) return;
29403:         try { mainMutationObserver.disconnect(); } catch (err) {}
29404: 
29405:         const roots = new Set();
29406:         const mapElement = getLargestLeafletMap();
29407:         const mapRoot = mapElement?.closest?.('#map_outer') || mapElement?.parentElement || mapElement;
29408:         const missionRoot = document.querySelector('#missions, #mission_list, .missions-panel, .mission-list');
29409:         if (mapRoot?.isConnected) roots.add(mapRoot);
29410:         if (missionRoot?.isConnected) roots.add(missionRoot);
29411: 
29412:         if (!roots.size) {
29413:             mainMutationObserverFallbackActive = true;
29414:             mainMutationObserver.observe(document.body, { childList: true, subtree: true });
29415:             return;
29416:         }
29417: 
29418:         mainMutationObserverFallbackActive = false;
29419:         for (const root of roots) mainMutationObserver.observe(root, { childList: true, subtree: true });
29420:         mainMutationObserver.observe(document.body, { childList: true, subtree: false });
29421:     }
29422: 
29423:     async function runDeferredOperationalStartup() {
29424:         if (operationalStartupStarted || runtime.destroyed) return;
29425:         const operationalPerformanceStartedAt = startupClock();
29426:         if (document.hidden) {
29427:             runtimeSetTimeout(() => scheduleDeferredOperationalStartup(0), 1000);
29428:             return;
29429:         }
29430:         operationalStartupStarted = true;
29431: 
29432:         loadCachedFinancialRules();
29433:         loadCachedFinancialPolicy();
29434:         ensureFinanceVaultCredential(financePlayerIdentity());
29435:         scanInlineMissionMarkerData();
29436:         installMissionMarkerAddHook();
29437:         installRadioMessageHook();
29438:         if (state.missionValue) installMissionValueWindows();
29439: 
29440:         startupDataPassActive = true;
29441:         try {
29442:             if (vehicleDataNeeded()) await refreshPersonalVehicleData(true);
29443:         } finally {
29444:             startupDataPassActive = false;
29445:         }
29446: 
29447:         runtimeClearTimeout(missionSnapshotTimer);
29448:         missionSnapshotTimer = null;
29449:         if (missionSnapshotsNeeded()) refreshMissionSnapshots();
29450:         if (state.missionSpawn.enabled) primeMissionSpawnDetector();
29451:         if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(180);
29452:         if (state.transportWatcher) scheduleTransportWatcherRefresh(220);
29453:         if (state.resourceGap.enabled) scheduleResourceGapRefresh(260);
29454:         if (state.unitCommitment) scheduleUnitCommitmentRefresh(300);
29455:         if (state.allianceCredits) scheduleAllianceCreditRefresh(320);
29456:         if (state.missionAge) scheduleMissionAgeRefresh(340);
29457: 
29458:         operationalStartupComplete = true;
29459:         scheduleOperationalPanelsRender(0);
29460:         if (state.majorIncidentFeed.enabled) scheduleMajorIncidentFeedRender(120);
29461:         scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false, mapOnly: true });
29462:         recordStartupMetric('operationalStartupMs', operationalPerformanceStartedAt, { operationalStartupComplete: true });
29463: 
29464:     }
29465: 
29466:     function scheduleDeferredOperationalStartup(delay = STARTUP_OPERATIONAL_DELAY_MS) {
29467:         if (operationalStartupStarted || runtime.destroyed) return;
29468:         runtimeSetTimeout(() => runtimeRunWhenIdle(() => {
29469:             runDeferredOperationalStartup().catch(err => {
29470:                 operationalStartupComplete = true;
29471:                 startupDataPassActive = false;
29472:                 console.debug(`[${SCRIPT.name}] Deferred startup recovered after an operational initialisation error.`, err);
29473:                 connectMainMutationObserver();
29474:             });
29475:         }, STARTUP_IDLE_TIMEOUT_MS), Math.max(0, Number(delay) || 0));
29476:     }
29477: 
29478: 
29479:     const AUTO_LOAD_ALL_VEHICLES_SELECTOR = 'a.missing_vehicles_load[href*="/missing_vehicles"]';
29480:     const AUTO_LOAD_ALL_VEHICLES_MISSION_ROOT_SELECTOR = '#lightbox_box, #lightbox, .lightbox_content, .modal.show, .modal.in, .modal-content, [role="dialog"], .ui-dialog-content, .ui-dialog';
29481:     const AUTO_LOAD_ALL_VEHICLES_MAX_REQUESTS = 50;
29482:     const AUTO_LOAD_ALL_VEHICLES_SETTLE_MS = 180;
29483:     const AUTO_LOAD_ALL_VEHICLES_TIMEOUT_MS = 6000;
29484:     const AUTO_LOAD_ALL_VEHICLES_HIDDEN_RETRIES = 24;
29485:     let autoLoadAllVehiclesObserver = null;
29486:     let autoLoadAllVehiclesLinkObserver = null;
29487:     let autoLoadAllVehiclesRootObserver = null;
29488:     let autoLoadAllVehiclesScanTimer = null;
29489:     let autoLoadAllVehiclesReleaseTimer = null;
29490:     let autoLoadAllVehiclesMissionId = null;
29491:     let autoLoadAllVehiclesMissionRoot = null;
29492:     let autoLoadAllVehiclesActiveLink = null;
29493:     let autoLoadAllVehiclesActiveSignature = '';
29494:     let autoLoadAllVehiclesInFlight = false;
29495:     let autoLoadAllVehiclesRequestCount = 0;
29496:     let autoLoadAllVehiclesHiddenRetryCount = 0;
29497:     const autoLoadAllVehiclesRequestedPages = new Set();
29498: 
29499:     function autoLoadAllVehiclesLinkInfo(link) {
29500:         if (!link || link.nodeType !== 1 || !link.matches?.(AUTO_LOAD_ALL_VEHICLES_SELECTOR)) return null;
29501:         let url;
29502:         try { url = new URL(link.getAttribute('href') || link.href, location.href); } catch (err) { return null; }
29503:         if (url.origin !== location.origin) return null;
29504:         const match = url.pathname.match(/^\/missions\/(\d+)\/missing_vehicles\/?$/u);
29505:         if (!match) return null;
29506:         const rawOffset = url.searchParams.get('offset_page');
29507:         const offsetPage = Number.isFinite(Number(rawOffset)) ? Math.max(0, Number(rawOffset)) : 0;
29508:         return {
29509:             missionId: match[1],
29510:             offsetPage,
29511:             signature: `${match[1]}:${offsetPage}:${url.pathname}${url.search}`,
29512:             href: url.href
29513:         };
29514:     }
29515: 
29516:     function autoLoadAllVehiclesElementVisible(element) {
29517:         if (!element?.isConnected || element.hidden || element.getAttribute?.('aria-hidden') === 'true') return false;
29518:         if (element.matches?.(':disabled, .disabled, [aria-disabled="true"]')) return false;
29519:         try {
29520:             const style = pageWindow.getComputedStyle?.(element);
```

## Boot installation sequence

Canonical lines 29740–29840

```javascript
29740:             installRadioMessageHook();
29741:             installCreditsUpdateHook();
29742:             observeCreditValue();
29743:             const ready = ensureUi();
29744:             const mapReady = Boolean(getLargestLeafletMap());
29745:             if (ready && (mapReady || attempts >= 12)) {
29746:                 recordStartupMetric('coreUiReadyMs', bootPerformanceStartedAt, { bootAttempts: attempts });
29747:                 scheduleMarkerStateSync(0, false);
29748:                 scheduleDeferredOperationalStartup();
29749:                 runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
29750:                 return;
29751:             }
29752:             if (attempts >= 90 || runtime.destroyed) return;
29753:             const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
29754:             runtimeSetTimeout(runBootAttempt, delay);
29755:         };
29756:         runtimeSetTimeout(runBootAttempt, 250);
29757:     }
29758: 
29759:     function boot() {
29760:         if (runtime.destroyed || bootStarted) return;
29761:         bootStarted = true;
29762:         bootStartedAt = Date.now();
29763:         const bootPerformanceStartedAt = startupClock();
29764:         applyRootAttributes();
29765:         if (installAllianceBuildingsPageOptimisation()) return;
29766:         createCleanExit();
29767:         if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
29768:         installMissionMarkerAddHook();
29769:         installRadioMessageHook();
29770:         lastObservedCredits = readCurrentCreditTotal();
29771:         installCreditsUpdateHook();
29772:         observeCreditValue();
29773: 
29774:         startBootAttemptCoordinator(bootPerformanceStartedAt);
29775: 
29776:         const observer = runtimeTrackObserver(new MutationObserver(mutations => {
29777:             if (state.economyMode && economyMapMoving) {
29778:                 economyDeferredDomMutation = true;
29779:                 return;
29780:             }
29781:             let externalMutationFound = false;
29782:             let addedLeafletMarker = false;
29783:             let missionChanged = false;
29784:             let layoutChanged = false;
29785:             let toolkitUiRemoved = false;
29786:             for (const mutation of mutations) {
29787:                 if (mutationBelongsToToolkit(mutation)) continue;
29788:                 externalMutationFound = true;
29789:                 if (!addedLeafletMarker && mutationAddsLeafletMarkerIcon(mutation)) {
29790:                     addedLeafletMarker = true;
29791:                     missionChanged = true;
29792:                 }
29793:                 if (!missionChanged && mutationAffectsMissionData(mutation)) missionChanged = true;
29794:                 if (!layoutChanged && mutationAffectsMapLayout(mutation)) layoutChanged = true;
29795:                 if (!toolkitUiRemoved && mutationRemovesToolkitUi(mutation)) toolkitUiRemoved = true;
29796:                 if (addedLeafletMarker && missionChanged && layoutChanged && toolkitUiRemoved) break;
29797:             }
29798:             if (!externalMutationFound) return;
29799:             missionChanged ||= addedLeafletMarker;
29800:             if (!missionChanged && !layoutChanged && !toolkitUiRemoved) return;
29801: 
29802:             if (addedLeafletMarker) {
29803:                 invalidateMarkerRegistryCaches('all');
29804:                 scheduleMarkerStateSync(0, false);
29805:                 if (!state.visibility.buildings) scheduleMarkerStateSync(180, true);
29806:             }
29807:             if (layoutChanged) invalidateMapElementCache();
29808:             if (document.hidden || dragState || (state.economyMode && economyMapMoving)) return;
29809: 
29810:             runtimeClearTimeout(mutationTimer);
29811:             const startupSettling = bootStartedAt > 0 && Date.now() - bootStartedAt < STARTUP_SETTLE_WINDOW_MS;
29812:             const mutationDelay = startupSettling
29813:                 ? STARTUP_MUTATION_DEBOUNCE_MS
29814:                 : (state.economyMode ? Math.max(320, DOM_REFRESH_DEBOUNCE_MS) : DOM_REFRESH_DEBOUNCE_MS);
29815:             mutationTimer = runtimeSetTimeout(() => {
29816:                 if (dragState || document.hidden || runtime.destroyed || (state.economyMode && economyMapMoving)) return;
29817:                 const panelMissing = settingsPanelActivated && !document.getElementById(SCRIPT.panelId);
29818:                 const mapElement = getLargestLeafletMap();
29819:                 const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));
29820:                 if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();
29821:                 if (mainMutationObserverFallbackActive && (mapElement || document.querySelector('#missions, #mission_list, .missions-panel, .mission-list'))) {
29822:                     connectMainMutationObserver();
29823:                 }
29824:                 if (layoutChanged) {
29825:                     refreshSuppression();
29826:                     fitControlToMap();
29827:                     schedulePanelPosition(true, 50);
29828:                     scheduleCriticalDrawerDock(60);
29829:                 }
29830:                 if (missionChanged) scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
29831:             }, mutationDelay);
29832:         }));
29833:         mainMutationObserver = observer;
29834: 
29835:         runtimeListen(document, 'keydown', handleKeyboard);
29836:         runtimeListen(document, 'pointerover', handleMissionInspectorPointerOver, true);
29837:         runtimeListen(document, 'pointermove', handleMissionInspectorPointerMove, true);
29838:         runtimeListen(document, 'pointerout', handleMissionInspectorPointerOut, true);
29839:         runtimeListen(document, 'pointerdown', () => unlockPayoutAudio(), { once: true, capture: true });
29840:         runtimeListen(document, 'click', event => {
```
