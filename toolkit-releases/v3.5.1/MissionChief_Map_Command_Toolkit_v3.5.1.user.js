// ==UserScript==
// @name         MissionChief Map Command Toolkit
// @namespace    https://github.com/Conroy1988/missionchief-map-command-toolkit
// @version      3.5.1
// @description  MissionChief operational map command centre.
// @author       Conroy1988
// @license      MIT
// @match        *://missionchief.co.uk/*
// @match        *://www.missionchief.co.uk/*
// @match        *://*.missionchief.co.uk/*
// @match        *://missionchief.com/*
// @match        *://www.missionchief.com/*
// @match        *://*.missionchief.com/*
// @match        *://leitstellenspiel.de/*
// @match        *://www.leitstellenspiel.de/*
// @match        *://*.leitstellenspiel.de/*
// @match        *://meldkamerspel.com/*
// @match        *://www.meldkamerspel.com/*
// @match        *://*.meldkamerspel.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_deleteValue
// @grant        unsafeWindow
// @connect      discord.com
// @connect      discordapp.com
// @run-at       document-idle
// @downloadURL https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js
// @updateURL https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.meta.js
// ==/UserScript==

/*
MIT License

Copyright (c) 2026 Conroy1988

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
*/

(function () {
    'use strict';

    const pageWindow = typeof unsafeWindow !== 'undefined' ? unsafeWindow : window;

    const SCRIPT = {
        name: 'MissionChief Map Command Toolkit',
        version: '3.5.1',
        author: 'Conroy1988',
        controlId: 'mc-map-command-toolkit-control',
        panelId: 'mc-map-command-toolkit-panel',
        toastId: 'mc-map-command-toolkit-toast',
        payoutFlashId: 'mc-map-command-toolkit-payout-flash',
        criticalDrawerId: 'mc-map-command-toolkit-critical-drawer',
        missionInspectorId: 'mc-map-command-toolkit-mission-inspector',
        cleanExitId: 'mcms-clean-exit',
        styleId: 'mc-map-command-toolkit-style-v351',
        oldControlId: 'mc-map-command-skins-control',
        oldGeoLabelLayerId: 'mcms-persistent-label-layer',
        storageState: 'mc_map_command_toolkit_state_v150',
        payoutHistoryState: 'mc_map_command_toolkit_payout_history_v200',
        sessionPerformanceState: 'mc_map_command_toolkit_session_v200',
        missionProgressState: 'mc_map_command_toolkit_mission_progress_v250',
        discordWebhookState: 'mc_map_command_toolkit_discord_webhook_v300',
        discordLastReportState: 'mc_map_command_toolkit_discord_last_report_v310',
        oldStorageKeys: [
            'mc_map_command_toolkit_state_v149',
            'mc_map_command_toolkit_state_v148',
            'mc_map_command_toolkit_state_v147',
            'mc_map_command_toolkit_state_v146',
            'mc_map_command_toolkit_state_v145',
            'mc_map_command_toolkit_state_v144',
            'mc_map_command_toolkit_state_v143',
            'mc_map_command_toolkit_state_v142',
            'mc_map_command_toolkit_state_v141',
            'mc_map_command_toolkit_state_v140',
            'mc_map_command_toolkit_state_v130'
        ],
        legacyTheme: 'mc_map_command_skins_theme_v2',
        legacyPosition: 'mc_map_command_skins_position_v1'
    };

    const RUNTIME_KEY = '__MC_MAP_COMMAND_TOOLKIT_RUNTIME__';
    const previousRuntime = pageWindow[RUNTIME_KEY];
    if (previousRuntime?.version === SCRIPT.version && previousRuntime.destroyed !== true) return;
    try { previousRuntime?.destroy?.('replaced by a newer toolkit runtime'); } catch (err) {}

    const runtime = {
        version: SCRIPT.version,
        destroyed: false,
        timeouts: new Set(),
        intervals: new Set(),
        animationFrames: new Set(),
        observers: new Set(),
        waiters: new Set(),
        requests: new Set(),
        fetchControllers: new Set(),
        listeners: [],
        mapBindings: [],
        hookRestorers: [],
        cleanupCallbacks: [],
        destroy(reason = 'runtime shutdown') {
            if (this.destroyed) return;
            this.destroyed = true;
            for (const id of this.timeouts) { try { pageWindow.clearTimeout(id); } catch (err) {} }
            for (const id of this.intervals) { try { pageWindow.clearInterval(id); } catch (err) {} }
            for (const id of this.animationFrames) { try { pageWindow.cancelAnimationFrame(id); } catch (err) {} }
            this.timeouts.clear();
            this.intervals.clear();
            this.animationFrames.clear();
            for (const settle of Array.from(this.waiters)) { try { settle(false); } catch (err) {} }
            this.waiters.clear();
            for (const request of Array.from(this.requests)) { try { request.abort?.(); } catch (err) {} }
            this.requests.clear();
            for (const controller of Array.from(this.fetchControllers)) { try { controller.abort(); } catch (err) {} }
            this.fetchControllers.clear();
            for (const observer of this.observers) { try { observer.disconnect(); } catch (err) {} }
            this.observers.clear();
            for (const { target, type, listener, options } of this.listeners.splice(0)) {
                try { target.removeEventListener(type, listener, options); } catch (err) {}
            }
            for (const binding of this.mapBindings.splice(0)) {
                try { binding.map.off(binding.types, binding.handler); } catch (err) {}
            }
            for (const restore of this.hookRestorers.splice(0).reverse()) { try { restore(); } catch (err) {} }
            for (const cleanup of this.cleanupCallbacks.splice(0).reverse()) { try { cleanup(reason); } catch (err) {} }
            if (pageWindow[RUNTIME_KEY] === this) {
                try { delete pageWindow[RUNTIME_KEY]; } catch (err) { pageWindow[RUNTIME_KEY] = null; }
            }
        }
    };
    pageWindow[RUNTIME_KEY] = runtime;

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

    function runtimeClearTimeout(id) {
        if (id === null || id === undefined) return;
        runtime.timeouts.delete(id);
        try { pageWindow.clearTimeout(id); } catch (err) {}
    }

    function runtimeDelay(delay = 0) {
        if (runtime.destroyed) return Promise.resolve(false);
        return new Promise(resolve => {
            let timerId = null;
            let settled = false;
            const settle = completed => {
                if (settled) return;
                settled = true;
                runtime.waiters.delete(settle);
                if (timerId !== null) runtimeClearTimeout(timerId);
                resolve(Boolean(completed));
            };
            runtime.waiters.add(settle);
            timerId = runtimeSetTimeout(() => settle(true), Math.max(0, Number(delay) || 0));
            if (timerId === null) settle(false);
        });
    }

    function runtimeSetInterval(callback, delay = 0, ...args) {
        if (runtime.destroyed) return null;
        const id = pageWindow.setInterval((...callbackArgs) => {
            if (!runtime.destroyed) callback(...callbackArgs);
        }, delay, ...args);
        runtime.intervals.add(id);
        return id;
    }

    function runtimeClearInterval(id) {
        if (id === null || id === undefined) return;
        runtime.intervals.delete(id);
        try { pageWindow.clearInterval(id); } catch (err) {}
    }

    function runtimeRequestAnimationFrame(callback) {
        if (runtime.destroyed) return null;
        let id = null;
        id = pageWindow.requestAnimationFrame(timestamp => {
            runtime.animationFrames.delete(id);
            if (!runtime.destroyed) callback(timestamp);
        });
        runtime.animationFrames.add(id);
        return id;
    }

    function runtimeCancelAnimationFrame(id) {
        if (id === null || id === undefined) return;
        runtime.animationFrames.delete(id);
        try { pageWindow.cancelAnimationFrame(id); } catch (err) {}
    }

    function runtimeListen(target, type, listener, options) {
        if (!target?.addEventListener || runtime.destroyed) return listener;
        target.addEventListener(type, listener, options);
        runtime.listeners.push({ target, type, listener, options });
        return listener;
    }

    function runtimeTrackObserver(observer) {
        if (!observer) return observer;
        if (runtime.destroyed) {
            try { observer.disconnect(); } catch (err) {}
            return observer;
        }
        runtime.observers.add(observer);
        return observer;
    }

    function runtimeOnCleanup(callback) {
        if (typeof callback === 'function') runtime.cleanupCallbacks.push(callback);
        return callback;
    }

    function runtimeFetch(input, init = {}) {
        if (runtime.destroyed) return Promise.reject(new Error('Toolkit runtime stopped.'));
        const Controller = pageWindow.AbortController || globalThis.AbortController;
        const controller = typeof Controller === 'function' ? new Controller() : null;
        if (controller) runtime.fetchControllers.add(controller);
        const fetchFunction = pageWindow.fetch || globalThis.fetch;
        if (typeof fetchFunction !== 'function') {
            if (controller) runtime.fetchControllers.delete(controller);
            return Promise.reject(new Error('Browser fetch is unavailable.'));
        }
        const options = controller ? { ...init, signal: controller.signal } : init;
        return Promise.resolve(fetchFunction.call(pageWindow, input, options))
            .finally(() => { if (controller) runtime.fetchControllers.delete(controller); });
    }

    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V341__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V340__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V318__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V317__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V316__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V315__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V314__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V313__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V311__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V310__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V300__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V290__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V287__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V286__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V285__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V284__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V283__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V282__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V281__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V280__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V272__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V271__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V270__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V263__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V262__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V261__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V260__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V251__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V250__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V240__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V230__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V220__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V210__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V203__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V202__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V201__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V200__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V184__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V183__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V182__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V181__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V180__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V171__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V170__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V169__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V168__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V167__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V166__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V165__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V164__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V163__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V162__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V161__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V160__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V155__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V154__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V153__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V152__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V151__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V150__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V149__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V148__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V147__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V146__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V145__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V144__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V143__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V142__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V141__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V140__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V130__ = true;

    const UI_THEMES = Object.freeze({
        mapCommand: Object.freeze({ label: 'Map Command', short: 'DEFAULT', icon: '▦', description: 'The original operational command interface.' }),
        cyberpunk: Object.freeze({ label: 'Cyberpunk', short: 'NEON', icon: '⚡', description: 'Neon tactical interface with angular panels, signal animations and high-contrast controls.' })
    });
    const UI_THEME_ORDER = Object.freeze(['mapCommand', 'cyberpunk']);

    const THEMES = {
        default: { full: 'Default', label: 'Default', short: 'STD', icon: '□' },
        control: { full: 'Control Room', label: 'Control', short: 'CTL', icon: '◐' },
        incident: { full: 'Incident Focus', label: 'Incident', short: 'INC', icon: '▣' },
        roads: { full: 'Road Priority', label: 'Roads', short: 'RD', icon: '═' },
        urban: { full: 'Urban Grey', label: 'Urban', short: 'URB', icon: '◫' },
        rural: { full: 'Rural Watch', label: 'Rural', short: 'RUR', icon: '◇' },
        nightshift: { full: 'Night Shift', label: 'Night', short: 'NIT', icon: '◆' },
        fireCommand: { full: 'Fire Command', label: 'Fire', short: 'FIRE', icon: '🔥' },
        policeTactical: { full: 'Police Tactical', label: 'Police', short: 'POL', icon: '◆' },
        medicalControl: { full: 'Medical Control', label: 'Medical', short: 'MED', icon: '✚' },
        coastalCommand: { full: 'Coastal Command', label: 'Coastal', short: 'SEA', icon: '⚓' }
    };

    const PAYOUT_TEMPLATES = {
        gta5: { label: 'GTA V Inspired', kicker: 'PAYOUT RECEIVED', titleCase: false, particleMode: 'none' },
        viceCity: { label: 'Vice City Inspired', kicker: 'PAYOUT RECEIVED', titleCase: true, particleMode: 'none' },
        badCompany: { label: 'Bad Company Inspired', kicker: 'PAYOUT RECEIVED', titleCase: false, particleMode: 'embers' },
        scarface: { label: 'Scarface Inspired', kicker: 'EMPIRE PAYOUT CONFIRMED', titleCase: false, particleMode: 'stars' },
        cyberpunk: { label: 'Cyberpunk Inspired', kicker: 'CREDIT TRANSFER CONFIRMED', titleCase: false, particleMode: 'glitch' },
        hellfire: { label: 'Hellfire Inspired', kicker: 'REWARD CLAIMED', titleCase: false, particleMode: 'embers' },
        wasteland: { label: 'Fallout Inspired', kicker: 'VAULT-TEC REWARD AUTHORIZED', titleCase: false, particleMode: 'dust' },
        galactic: { label: 'Galactic Command', kicker: 'CREDIT ALLOCATION CONFIRMED', titleCase: false, particleMode: 'stars' },
        darkFantasy: { label: 'Dark Fantasy Inspired', kicker: 'REWARD BESTOWED', titleCase: true, particleMode: 'ash' },
        biohazard: { label: 'Biohazard Containment', kicker: 'COMPENSATION RELEASED', titleCase: false, particleMode: 'none' },
        underworld: { label: 'Underworld Inspired', kicker: 'REWARD CLAIMED', titleCase: true, particleMode: 'embers' },
        pixelArcade: { label: 'Pixel Arcade Inspired', kicker: 'SCORE BONUS AWARDED', titleCase: false, particleMode: 'pixels' }
    };

    const PAYOUT_TEMPLATE_ORDER = ['gta5', 'viceCity', 'badCompany', 'scarface', 'cyberpunk', 'hellfire', 'wasteland', 'galactic', 'darkFantasy', 'biohazard', 'underworld', 'pixelArcade'];

    // Hosted real-audio cues remain lazy-loaded through direct raw GitHub URLs.
    // Hosted payout cues are mapped by template and lazy-loaded only when played.
    const PAYOUT_MEDIA_SOUNDS = Object.freeze({
        viceCity: Object.freeze({
            label: 'GTA Vice City Cashout',
            url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/gta-vice-city-cashout.mp3'
        }),
        badCompany: Object.freeze({
            label: 'BF Bad Company Cashout',
            url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/bf-bad-company-cashout.mp3'
        }),
        scarface: Object.freeze({
            label: 'Scarface Cashout',
            url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/scarface-cashout.mp3'
        }),
        cyberpunk: Object.freeze({
            label: 'Cyberpunk Cashout',
            url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/cyberpunk-cashout.mp3'
        }),
        wasteland: Object.freeze({
            label: 'Fallout Cashout',
            url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/fallout-cashout.mp3'
        })
    });

    const CORE_THEME_ORDER = ['default', 'control', 'incident', 'roads', 'urban', 'rural', 'nightshift'];
    const SERVICE_THEME_ORDER = ['fireCommand', 'policeTactical', 'medicalControl', 'coastalCommand'];
    const THEME_ORDER = [...CORE_THEME_ORDER, ...SERVICE_THEME_ORDER];
    const PAYOUT_FLASH_MIN_MS = 2000;
    const PAYOUT_FLASH_MAX_MS = 30000;
    const PAYOUT_FLASH_STEP_MS = 2000;
    const PAYOUT_HISTORY_LIMIT = 40;
    const PAYOUT_MATCH_WINDOW_MS = 20000;
    const CRITICAL_VIEW_MIN_AGE_MS = 8 * 60 * 60 * 1000;
    const STUCK_MIN_MINUTES = 5;
    const STUCK_MAX_MINUTES = 180;
    const MISSION_SPAWN_DURATION_MS = 2400;
    const MAP_PROFILE_LIMIT = 5;
    const VEHICLE_API_REFRESH_MS = 2 * 60 * 1000;
    const VEHICLE_API_MIN_REFRESH_MS = 20 * 1000;
    const DOM_REFRESH_DEBOUNCE_MS = 260;
    const BUILDING_VISIBILITY_RECHECK_MS = 4000;
    const MAP_DISCOVERY_RETRY_MS = 2000;
    const FALLBACK_MISSION_REFRESH_MS = 15 * 1000;
    const MARKER_REGISTRY_CACHE_MS = 180;
    const PERSONAL_BUILDING_ID_CACHE_MS = 1200;
    const VEHICLE_API_ERROR_BACKOFF_MS = 60 * 1000;
    const HEATMAP_SOURCE_CACHE_MS = 3000;
    const MISSION_CACHE_RETENTION_MS = 10 * 60 * 1000;
    const RESOURCE_GAP_REFRESH_MS = 15 * 1000;
    const RESOURCE_GAP_RADIUS_OPTIONS = [10, 25, 50, 100];
    const TRANSPORT_SWEEP_DELAY_OPTIONS = [1500, 2000, 2500, 3000, 4000, 5000];
    const TRANSPORT_SWEEP_MAX_REQUESTS = 50;
    const TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION = 40;
    const LEGACY_THEME_MAP = { night: 'control', grey: 'urban', blue: 'nightshift', muted: 'rural', contrast: 'incident' };
    const POSITIONS = {
        tl: { label: 'Top left', short: 'TL' },
        tr: { label: 'Top right', short: 'TR' },
        bl: { label: 'Bottom left', short: 'BL' },
        br: { label: 'Bottom right', short: 'BR' }
    };

    const QUICK_PLACES = [
        { id: 'edi', label: 'EDI', name: 'Edinburgh', lat: 55.9533, lng: -3.1883, zoom: 11 },
        { id: 'fife', label: 'FIFE', name: 'Fife', lat: 56.2082, lng: -3.1495, zoom: 10 },
        { id: 'glas', label: 'GLAS', name: 'Glasgow', lat: 55.8642, lng: -4.2518, zoom: 11 },
        { id: 'dund', label: 'DUND', name: 'Dundee', lat: 56.4620, lng: -2.9707, zoom: 11 },
        { id: 'stir', label: 'STIR', name: 'Stirling', lat: 56.1165, lng: -3.9369, zoom: 11 }
    ];

    const SUPPRESSION_SELECTORS = [
        '.modal.show', '.modal.in', '.modal-backdrop', '.bootbox.modal',
        '[role="dialog"][aria-modal="true"]', '.popover.show', '.popover.in',
        '.dropdown-menu.show', '.dropdown.open > .dropdown-menu', '.ui-dialog',
        '.fancybox-overlay', '#fancybox-wrap'
    ];

    let state = loadState();
    let cachedMap = null;
    let cachedMapElement = null;
    let mapDiscoveryLastAttempt = 0;
    const markerRegistryCache = new Map();
    let markerRegistryRevision = 0;
    let buildingRegistryRevision = 0;
    let vehicleDataRevision = 0;
    let cachedUserId = null;
    let cachedUserIdReadAt = 0;
    let personalBuildingIdsCache = { revision: -1, userId: null, createdAt: 0, values: new Set() };
    let missionIconMarkerCache = new WeakMap();
    let panelPositionTimer = null;
    let coverageRenderSignature = '';
    let heatmapRenderSignature = '';
    let heatmapSourceCache = { key: '', createdAt: 0, points: [] };
    let operationalRenderSignature = '';
    let discordPreviewRenderSignature = '';
    let missionInspectorLastPosition = '';
    let missionInspectorTooltipCache = { marker: null, createdAt: 0, rect: null };
    const missionLifecycleLastSeen = new Map();
    let coverageGroup = null;
    let mutationTimer = null;
    let classifyTimer = null;
    let coverageTimer = null;
    let fitTimer = null;
    let dragState = null;
    let suppressNextOutsideClick = false;
    const hiddenPersonalBuildingLayers = new Set();
    const personalBuildingLayerOpacity = new Map();
    let enforcingPersonalBuildingVisibility = false;
    let heatmapGroup = null;
    let heatmapTimer = null;
    let allianceCreditGroup = null;
    let allianceCreditTimer = null;
    let missionAgeGroup = null;
    let missionAgeTimer = null;
    let unitCommitmentGroup = null;
    let unitCommitmentTimer = null;
    let transportWatcherGroup = null;
    let transportWatcherTimer = null;
    let resourceGapGroup = null;
    let resourceGapTimer = null;
    let missionSnapshotTimer = null;
    let opsRefreshTimer = null;
    let payoutFlashTimer = null;
    let toastFlashTimer = null;
    let payoutFlashFallbackInterval = null;
    let payoutFlashAnimations = [];
    let payoutAmountAnimationFrame = null;
    let payoutAudioContext = null;
    let payoutMediaAudio = null;
    let payoutMediaTemplate = '';
    let payoutMediaPrimed = false;
    let payoutMediaGeneration = 0;
    let payoutEventCounter = 0;
    let creditsValueObserver = null;
    let observedCreditsElement = null;
    let lastObservedCredits = null;
    let inlineMissionDataScanned = false;
    let missionSnapshotReady = false;
    let criticalViewActive = false;
    let criticalViewLoading = false;
    let criticalViewSnapshot = null;
    let vehicleApiFetchPromise = null;
    let vehicleApiLastFetch = 0;
    let vehicleApiReady = false;
    let vehicleApiLastError = 0;
    let missionCommitmentIndexDirty = true;
    let operationalPanelsLastRender = 0;
    let missionInspectorMarker = null;
    let missionInspectorPointer = null;
    let missionInspectorRefreshTimer = null;
    let missionInspectorMoveFrame = null;
    let missionProgressSaveTimer = null;
    let stuckMissionGroup = null;
    let stuckMissionTimer = null;
    let missionSpawnArmed = false;
    let missionSpawnPrimeTimer = null;
    const missionOverlayData = new Map();
    const liveMissionSnapshots = new Map();
    const recentCompletedMissions = [];
    const missionProgressState = loadMissionProgressState();
    const knownMissionIds = new Set();
    const stuckMissionLabels = new Map();
    const MISSION_OVERLAY_PANE = 'mcmsMissionFloatPane';
    const allianceCreditLabels = new Map();
    const missionAgeLabels = new Map();
    const unitCommitmentLabels = new Map();
    const transportWatcherLabels = new Map();
    const resourceGapLabels = new Map();
    const resourceGapAnalysisCache = new Map();
    let resourceGapVehicleContextCache = { key: '', createdAt: 0, available: [] };
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
        lastCandidateStats: null,
        log: []
    };
    const personalVehicleApiCache = new Map();
    const missionCommitmentIndex = new Map();
    const payoutHistory = loadPayoutHistory();
    const sessionPerformance = loadSessionPerformance();
    let discordFinancePreview = null;
    let discordFinanceBusy = false;
    let discordFinanceStatus = 'Select a reporting period, then generate and post the financial intelligence report.';
    let discordFinanceStatusTone = 'neutral';
    let tabletModeActive = false;
    let mobileModeActive = false;
    let activeDeviceLayout = 'desktop';
    let tabletLayoutTimer = null;
    let tabletDockResizeObserver = null;
    let tabletDockObservedMap = null;
    let commandBarAnimationTimer = null;
    let commandBarAnimating = false;

    function defaultState() {
        return {
            uiTheme: 'mapCommand',
            theme: getLegacyTheme(),
            position: getLegacyPosition(),
            activeTab: 'skins',
            cleanMode: false,
            markerFocus: false,
            missionPulse: false,
            roadPriority: false,
            compactDock: false,
            commandBarOpen: true,
            tabletMode: 'auto',
            mobileMode: 'auto',
            shortcuts: true,
            allianceCredits: false,
            allianceCreditMinimum: 0,
            missionAge: false,
            unitCommitment: false,
            transportWatcher: true,
            missionInspector: true,
            stuckDetector: { enabled: true, thresholdMin: 20 },
            missionSpawn: { enabled: true },
            resourceGap: { enabled: false, radiusMi: 25 },
            transportSweep: { delayMs: 2000, maxPerRun: 25 },
            payoutFlash: { enabled: true, threshold: 10000, durationMs: 4000, template: 'gta5', soundEnabled: false, soundVolume: 0.35 },
            discordReport: { webhookName: 'MissionChief Finance', topCategories: 5, period: 'today', customStart: localIsoDate(new Date(Date.now() - 6 * 86400000)), customEnd: localIsoDate(), includeChart: true, includeComparison: true },
            profiles: Array.from({ length: MAP_PROFILE_LIMIT }, () => null),
            nudge: { x: 0, y: 0 },
            panelPosition: null,
            visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true },
            quickPins: Object.fromEntries(QUICK_PLACES.map(place => [place.id, false])),
            coverage: { enabled: false, radiusMi: 10 },
            heatmap: { enabled: false, source: 'stations', service: 'all', radiusMi: 10, opacity: 0.30 },
            autoNight: {
                enabled: false,
                nightStart: '19:00',
                dayStart: '07:00',
                nightTheme: 'nightshift',
                dayTheme: 'default',
                lastBucket: ''
            },
            bookmarks: [null, null, null, null, null]
        };
    }

    function loadState() {
        const base = defaultState();
        const raw = localStorage.getItem(SCRIPT.storageState) || SCRIPT.oldStorageKeys.map(key => localStorage.getItem(key)).find(Boolean);
        if (!raw) return base;

        try {
            const parsed = JSON.parse(raw);
            const merged = {
                ...base,
                ...parsed,
                nudge: { ...base.nudge, ...(parsed.nudge || {}) },
                visibility: { ...base.visibility, ...(parsed.visibility || {}) },
                quickPins: { ...base.quickPins, ...(parsed.quickPins || {}) },
                coverage: { ...base.coverage, ...(parsed.coverage || {}) },
                heatmap: { ...base.heatmap, ...(parsed.heatmap || {}) },
                stuckDetector: { ...base.stuckDetector, ...(parsed.stuckDetector || {}) },
                missionSpawn: { ...base.missionSpawn, ...(parsed.missionSpawn || {}) },
                resourceGap: { ...base.resourceGap, ...(parsed.resourceGap || {}) },
                transportSweep: { ...base.transportSweep, ...(parsed.transportSweep || {}) },
                payoutFlash: { ...base.payoutFlash, ...(parsed.payoutFlash || {}) },
                discordReport: { ...base.discordReport, ...(parsed.discordReport || {}) },
                autoNight: { ...base.autoNight, ...(parsed.autoNight || {}) },
                profiles: Array.isArray(parsed.profiles) ? parsed.profiles.slice(0, MAP_PROFILE_LIMIT) : base.profiles,
                bookmarks: Array.isArray(parsed.bookmarks) ? parsed.bookmarks.slice(0, 5) : base.bookmarks
            };

            while (merged.bookmarks.length < 5) merged.bookmarks.push(null);
            while (merged.profiles.length < MAP_PROFILE_LIMIT) merged.profiles.push(null);

            merged.uiTheme = normaliseUiTheme(merged.uiTheme);
            merged.theme = normaliseTheme(merged.theme);
            merged.position = POSITIONS[merged.position] ? merged.position : 'bl';
            if (merged.activeTab === 'fleet') merged.activeTab = 'resources';
            merged.activeTab = ['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings'].includes(merged.activeTab) ? merged.activeTab : 'skins';
            delete merged.fleetFilter;
            merged.nudge.x = clamp(merged.nudge.x, -220, 220, 0);
            merged.nudge.y = clamp(merged.nudge.y, -220, 220, 0);
            merged.coverage.radiusMi = Number(merged.coverage.radiusMi) || 10;
            merged.heatmap.radiusMi = Number(merged.heatmap.radiusMi) || 10;
            merged.heatmap.opacity = clamp(merged.heatmap.opacity, 0.12, 0.55, 0.30);
            merged.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(merged.allianceCreditMinimum)) ? Number(merged.allianceCreditMinimum) : 0;
            merged.commandBarOpen = merged.commandBarOpen !== false;
            merged.tabletMode = ['auto', 'on', 'off'].includes(String(merged.tabletMode)) ? String(merged.tabletMode) : 'auto';
            merged.mobileMode = ['auto', 'on', 'off'].includes(String(merged.mobileMode)) ? String(merged.mobileMode) : 'auto';
            merged.transportWatcher = merged.transportWatcher !== false;
            merged.missionInspector = merged.missionInspector !== false;
            merged.stuckDetector.enabled = merged.stuckDetector.enabled !== false;
            merged.stuckDetector.thresholdMin = Math.round(clamp(merged.stuckDetector.thresholdMin, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
            merged.missionSpawn.enabled = merged.missionSpawn.enabled !== false;
            merged.resourceGap.enabled = Boolean(merged.resourceGap.enabled);
            merged.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(merged.resourceGap.radiusMi)) ? Number(merged.resourceGap.radiusMi) : 25;
            merged.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(merged.transportSweep.delayMs)) ? Number(merged.transportSweep.delayMs) : 2000;
            merged.transportSweep.maxPerRun = Math.round(clamp(merged.transportSweep.maxPerRun, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
            merged.payoutFlash.enabled = merged.payoutFlash.enabled !== false;
            merged.payoutFlash.threshold = Math.round(clamp(merged.payoutFlash.threshold, 1000, 1000000000, 10000));
            merged.payoutFlash.durationMs = normalisePayoutFlashDuration(merged.payoutFlash.durationMs);
            merged.payoutFlash.template = PAYOUT_TEMPLATES[merged.payoutFlash.template] ? merged.payoutFlash.template : 'gta5';
            merged.payoutFlash.soundEnabled = Boolean(merged.payoutFlash.soundEnabled);
            merged.payoutFlash.soundVolume = clamp(merged.payoutFlash.soundVolume, 0, 1, 0.35);
            merged.discordReport.webhookName = String(merged.discordReport.webhookName || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
            merged.discordReport.topCategories = [3, 5, 8].includes(Number(merged.discordReport.topCategories)) ? Number(merged.discordReport.topCategories) : 5;
            merged.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'session', 'sinceLast', 'custom'].includes(merged.discordReport.period) ? merged.discordReport.period : 'today';
            merged.discordReport.customStart = /^\d{4}-\d{2}-\d{2}$/u.test(String(merged.discordReport.customStart || '')) ? String(merged.discordReport.customStart) : localIsoDate(new Date(Date.now() - 6 * 86400000));
            merged.discordReport.customEnd = /^\d{4}-\d{2}-\d{2}$/u.test(String(merged.discordReport.customEnd || '')) ? String(merged.discordReport.customEnd) : localIsoDate();
            merged.discordReport.includeChart = merged.discordReport.includeChart !== false;
            merged.discordReport.includeComparison = merged.discordReport.includeComparison !== false;
            merged.autoNight.nightTheme = normaliseTheme(merged.autoNight.nightTheme);
            merged.autoNight.dayTheme = normaliseTheme(merged.autoNight.dayTheme);
            merged.bookmarks = merged.bookmarks.map(item => item ? { ...item, pinned: Boolean(item.pinned) } : null);
            merged.profiles = merged.profiles.map(item => item && typeof item === 'object' ? item : null);

            if (!merged.panelPosition || !Number.isFinite(Number(merged.panelPosition.left)) || !Number.isFinite(Number(merged.panelPosition.top))) {
                merged.panelPosition = null;
            } else {
                merged.panelPosition = { left: Number(merged.panelPosition.left), top: Number(merged.panelPosition.top) };
            }

            delete merged.requiresAttention;
            return merged;
        } catch (err) {
            return base;
        }
    }

    function saveState() {
        try {
            localStorage.setItem(SCRIPT.storageState, JSON.stringify(state));
            localStorage.setItem(SCRIPT.legacyTheme, state.theme);
            localStorage.setItem(SCRIPT.legacyPosition, state.position);
        } catch (err) {}
    }

    function getLegacyTheme() {
        return normaliseTheme(localStorage.getItem(SCRIPT.legacyTheme) || 'default');
    }

    function getLegacyPosition() {
        const saved = localStorage.getItem(SCRIPT.legacyPosition);
        return POSITIONS[saved] ? saved : 'bl';
    }

    function normaliseUiTheme(key) {
        return UI_THEMES[key] ? key : 'mapCommand';
    }

    function applyUiTheme(key, announce = false) {
        const nextTheme = normaliseUiTheme(key);
        const changed = state.uiTheme !== nextTheme;
        state.uiTheme = nextTheme;
        saveState();
        updateUI();
        if (announce && changed) showToast(`${UI_THEMES[nextTheme].label} interface active`);
    }

    function normaliseTheme(key) {
        if (THEMES[key]) return key;
        if (LEGACY_THEME_MAP[key]) return LEGACY_THEME_MAP[key];
        return 'default';
    }

    function payoutTemplateMeta(key = state?.payoutFlash?.template) {
        return PAYOUT_TEMPLATES[key] || PAYOUT_TEMPLATES.gta5;
    }

    function buildPayoutTemplateOptions(selected = state?.payoutFlash?.template) {
        return PAYOUT_TEMPLATE_ORDER.map(key => `<option value="${key}"${key === selected ? ' selected' : ''}>${PAYOUT_TEMPLATES[key].label}</option>`).join('');
    }

    function payoutTitleForTemplate(presentation, template = state?.payoutFlash?.template) {
        const tier = presentation?.tier || 'standard';
        const themedTitles = {
            gta5: {
                standard: 'MISSION COMPLETE', major: 'BIG SCORE SECURED', high: 'HEIST PAYDAY', elite: 'LEGENDARY TAKE'
            },
            viceCity: {
                standard: 'Cash Collected', major: 'Miami Money', high: 'Empire Payday', elite: 'King of the City'
            },
            badCompany: {
                standard: 'CONTRACT COMPLETE', major: 'OBJECTIVE SECURED', high: 'PAYDAY EXTRACTED', elite: 'FORTUNE OF WAR'
            },
            scarface: {
                standard: 'CASHOUT COMPLETE', major: 'EMPIRE EXPANDED', high: 'POWER SECURED', elite: 'THE WORLD IS YOURS'
            },
            cyberpunk: {
                standard: 'EDdies TRANSFERRED', major: 'DATA HEIST PAID', high: 'MEGACORP JACKPOT', elite: 'NIGHT CITY LEGEND'
            },
            hellfire: {
                standard: 'BOUNTY CLAIMED', major: 'INFERNAL PAYDAY', high: 'HELLGATE FORTUNE', elite: 'CROWN OF CINDERS'
            },
            wasteland: {
                standard: 'CAPS SECURED', major: 'VAULT RESERVES INCREASED', high: 'WASTELAND FORTUNE FOUND', elite: 'JACKPOT OF THE COMMONWEALTH'
            },
            galactic: {
                standard: 'CREDITS RECEIVED', major: 'FLEET BONUS CLEARED', high: 'SECTOR TREASURY UNLOCKED', elite: 'GALACTIC FORTUNE'
            },
            darkFantasy: {
                standard: 'Reward Bestowed', major: 'Royal Bounty', high: 'Ancient Treasure Claimed', elite: 'Fortune of the Realm'
            },
            biohazard: {
                standard: 'COMPENSATION CLEARED', major: 'HAZARD BONUS RELEASED', high: 'BLACKSITE PAYOUT', elite: 'OMEGA CLEARANCE AWARD'
            },
            underworld: {
                standard: 'Tribute Collected', major: 'Blood Money Secured', high: 'Dynasty Fortune', elite: 'Sovereign of the Night'
            },
            pixelArcade: {
                standard: 'STAGE CLEAR', major: 'BONUS ROUND', high: 'HIGH SCORE PAYOUT', elite: '1UP JACKPOT'
            }
        };
        return themedTitles[template]?.[tier] || presentation?.title || '';
    }

    function formatPayoutTitleForTemplate(title, template = state?.payoutFlash?.template) {
        const clean = String(title || '').replace(/\s+/g, ' ').trim();
        if (!payoutTemplateMeta(template).titleCase) return clean.toUpperCase();
        return clean.toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
    }

    function clamp(value, min, max, fallback) {
        const num = Number(value);
        if (!Number.isFinite(num)) return fallback;
        return Math.max(min, Math.min(max, num));
    }

    function normalisePayoutFlashDuration(value) {
        const duration = Number(value);
        if (!Number.isFinite(duration)) return 4000;
        const rounded = Math.round(duration / PAYOUT_FLASH_STEP_MS) * PAYOUT_FLASH_STEP_MS;
        return Math.max(PAYOUT_FLASH_MIN_MS, Math.min(PAYOUT_FLASH_MAX_MS, rounded));
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function closestEventTarget(event, selector) {
        const target = event?.target;
        if (target && typeof target.closest === 'function') return target.closest(selector);
        return target?.parentElement?.closest?.(selector) || null;
    }


    function decodeMissionTextEntities(value) {
        const text = String(value ?? '');
        if (!/&(?:#\d+|#x[\da-f]+|[a-z]+);/i.test(text)) return text;
        try {
            const textarea = document.createElement('textarea');
            textarea.innerHTML = text;
            return textarea.value;
        } catch (err) {
            return text;
        }
    }

    function missingRequirementKeyLabel(key) {
        const clean = String(key ?? '').replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
        const labels = {
            vehicle: 'VEHICLES',
            vehicles: 'VEHICLES',
            personnel: 'PERSONNEL',
            staff: 'PERSONNEL',
            people: 'PERSONNEL',
            patient: 'PATIENTS',
            patients: 'PATIENTS',
            prisoner: 'PRISONERS',
            prisoners: 'PRISONERS',
            transport: 'TRANSPORT',
            other: 'OTHER'
        };
        return labels[clean] || clean.replace(/\b\w/g, char => char.toUpperCase());
    }

    function missingRequirementValueText(value) {
        if (value === undefined || value === null || value === false) return '';
        if (Array.isArray(value)) {
            return value.map(missingRequirementValueText).filter(Boolean).join(', ');
        }
        if (typeof value === 'object') {
            return Object.entries(value)
                .map(([key, nestedValue]) => {
                    const nested = missingRequirementValueText(nestedValue);
                    return nested ? `${missingRequirementKeyLabel(key)}: ${nested}` : '';
                })
                .filter(Boolean)
                .join(', ');
        }
        return decodeMissionTextEntities(value)
            .replace(/<[^>]*>/g, ' ')
            .replace(/\\[nrt]/g, ' ')
            .replace(/\s+/g, ' ')
            .replace(/^['"]+|['"]+$/g, '')
            .trim();
    }

    function formatMissingRequirementObject(value) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) return '';
        const priority = ['vehicles', 'vehicle', 'personnel', 'staff', 'people', 'patients', 'patient', 'prisoners', 'prisoner', 'transport', 'other'];
        const entries = Object.entries(value).sort(([keyA], [keyB]) => {
            const a = priority.indexOf(String(keyA).toLowerCase());
            const b = priority.indexOf(String(keyB).toLowerCase());
            return (a < 0 ? priority.length : a) - (b < 0 ? priority.length : b);
        });
        return entries
            .map(([key, rawValue]) => {
                const formatted = missingRequirementValueText(rawValue);
                return formatted ? `${missingRequirementKeyLabel(key)}: ${formatted}` : '';
            })
            .filter(Boolean)
            .join(' • ');
    }

    function normaliseMissingRequirementText(value) {
        if (value === undefined || value === null) return '';
        if (typeof value === 'object') return formatMissingRequirementObject(value) || missingRequirementValueText(value);

        let text = decodeMissionTextEntities(value)
            .replace(/<br\s*\/?>/gi, ' ')
            .replace(/<[^>]*>/g, ' ')
            .replace(/\\[nrt]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
        if (!text) return '';

        // MissionChief can expose the requirement payload as JSON, escaped JSON,
        // or occasionally as a key/value fragment without its opening brace.
        for (let pass = 0; pass < 3; pass += 1) {
            let candidate = text;
            if (!candidate.startsWith('{') && /^(?:["']?[a-z][\w -]*["']?)\s*:/i.test(candidate)) candidate = `{${candidate}`;
            if (candidate.startsWith('{') && !candidate.endsWith('}')) candidate += '}';
            try {
                const parsed = JSON.parse(candidate);
                if (parsed && typeof parsed === 'object') return formatMissingRequirementObject(parsed) || missingRequirementValueText(parsed);
                if (typeof parsed === 'string' && parsed.trim() && parsed.trim() !== text) {
                    text = parsed.trim();
                    continue;
                }
            } catch (err) {}
            break;
        }

        // Fallback for malformed but still recognisable object fragments.
        const parsedPairs = {};
        const pairPattern = /["']?([a-z][\w -]*)["']?\s*:\s*(?:"([^"]*)"|'([^']*)'|([^,}\]]+))/gi;
        let match;
        while ((match = pairPattern.exec(text))) {
            const key = match[1];
            const pairValue = match[2] ?? match[3] ?? match[4] ?? '';
            parsedPairs[key] = pairValue;
        }
        if (Object.keys(parsedPairs).length) {
            const formatted = formatMissingRequirementObject(parsedPairs);
            if (formatted) return formatted;
        }

        return text.replace(/^[{\[]+|[}\]]+$/g, '').replace(/\s+/g, ' ').trim();
    }

    function removeOldInstances() {
        document.querySelectorAll(`#${SCRIPT.controlId}, #${SCRIPT.panelId}, #${SCRIPT.toastId}, #${SCRIPT.payoutFlashId}, #${SCRIPT.criticalDrawerId}, #${SCRIPT.missionInspectorId}, #${SCRIPT.oldControlId}, #${SCRIPT.cleanExitId}, #${SCRIPT.oldGeoLabelLayerId}`)
            .forEach(el => el.remove());

        document.querySelectorAll('style').forEach(style => {
            const text = style.textContent || '';
            if (style.id.startsWith('mc-map-command-') || (text.includes('mcms-') && text.includes('data-mc-map-skin'))) {
                style.remove();
            }
        });
    }

    function addStyle(css) {
        const style = document.createElement('style');
        style.id = SCRIPT.styleId;
        style.textContent = css;
        document.head.appendChild(style);
    }

    removeOldInstances();
    try { localStorage.removeItem('mc_map_command_toolkit_attention_v170'); } catch (err) {}

    addStyle(`
        html[data-mc-map-skin="default"] .leaflet-tile-pane img.leaflet-tile { filter: none !important; }
        html[data-mc-map-skin="control"] .leaflet-container { background: #111820 !important; }
        html[data-mc-map-skin="control"] .leaflet-tile-pane img.leaflet-tile { filter: invert(92%) hue-rotate(182deg) brightness(62%) contrast(112%) saturate(72%) !important; }
        html[data-mc-map-skin="incident"] .leaflet-tile-pane img.leaflet-tile { filter: brightness(108%) contrast(142%) saturate(118%) !important; }
        html[data-mc-map-skin="roads"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(28%) brightness(104%) contrast(126%) saturate(70%) !important; }
        html[data-mc-map-skin="urban"] .leaflet-container { background: #111 !important; }
        html[data-mc-map-skin="urban"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(100%) invert(88%) brightness(61%) contrast(122%) saturate(54%) !important; }
        html[data-mc-map-skin="rural"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(42%) brightness(94%) contrast(108%) saturate(58%) !important; }
        html[data-mc-map-skin="nightshift"] .leaflet-container { background: #07111f !important; }
        html[data-mc-map-skin="nightshift"] .leaflet-tile-pane img.leaflet-tile { filter: invert(88%) hue-rotate(165deg) brightness(68%) contrast(119%) saturate(72%) !important; }

        /* Emergency-service skins: static tile filters, no extra tile provider or animation. */
        html[data-mc-map-skin="fireCommand"] .leaflet-container { background: #17120f !important; }
        html[data-mc-map-skin="fireCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(38%) sepia(58%) hue-rotate(335deg) saturate(145%) brightness(76%) contrast(124%) !important; }
        html[data-mc-map-skin="policeTactical"] .leaflet-container { background: #071321 !important; }
        html[data-mc-map-skin="policeTactical"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(24%) invert(89%) sepia(18%) saturate(118%) hue-rotate(166deg) brightness(64%) contrast(126%) !important; }
        html[data-mc-map-skin="medicalControl"] .leaflet-container { background: #061b1c !important; }
        html[data-mc-map-skin="medicalControl"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(18%) invert(88%) sepia(22%) saturate(126%) hue-rotate(126deg) brightness(68%) contrast(116%) !important; }
        html[data-mc-map-skin="coastalCommand"] .leaflet-container { background: #061725 !important; }
        html[data-mc-map-skin="coastalCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(22%) sepia(24%) hue-rotate(145deg) saturate(138%) brightness(82%) contrast(118%) !important; }

        html[data-mcms-road-priority="true"][data-mc-map-skin="default"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(18%) brightness(106%) contrast(132%) saturate(82%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="control"] .leaflet-tile-pane img.leaflet-tile { filter: invert(92%) hue-rotate(182deg) brightness(68%) contrast(132%) saturate(70%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="incident"] .leaflet-tile-pane img.leaflet-tile { filter: brightness(112%) contrast(156%) saturate(110%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="roads"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(35%) brightness(110%) contrast(150%) saturate(58%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="urban"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(100%) invert(88%) brightness(68%) contrast(144%) saturate(50%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="rural"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(48%) brightness(101%) contrast(130%) saturate(52%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="nightshift"] .leaflet-tile-pane img.leaflet-tile { filter: invert(88%) hue-rotate(165deg) brightness(73%) contrast(136%) saturate(68%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="fireCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(42%) sepia(62%) hue-rotate(335deg) saturate(150%) brightness(82%) contrast(142%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="policeTactical"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(28%) invert(89%) sepia(18%) saturate(112%) hue-rotate(166deg) brightness(70%) contrast(144%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="medicalControl"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(22%) invert(88%) sepia(22%) saturate(122%) hue-rotate(126deg) brightness(74%) contrast(134%) !important; }
        html[data-mcms-road-priority="true"][data-mc-map-skin="coastalCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(26%) sepia(24%) hue-rotate(145deg) saturate(132%) brightness(88%) contrast(136%) !important; }

        @keyframes mcmsMissionPulse {
            0% { filter: drop-shadow(0 0 1px rgba(255,70,70,.25)) brightness(1); }
            50% { filter: drop-shadow(0 0 8px rgba(255,70,70,.95)) brightness(1.18); }
            100% { filter: drop-shadow(0 0 1px rgba(255,70,70,.25)) brightness(1); }
        }

        /* Focus Mode fallback: newly-redrawn markers begin dimmed before MissionChief's
           marker registries and our classification classes have finished updating. */
        html[data-mcms-marker-focus="true"] .leaflet-marker-pane > .leaflet-marker-icon:not(.mcms-marker-mission),
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon.mcms-marker-building,
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon.mcms-marker-vehicle,
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon[data-mcms-vehicle-marker="true"],
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon[data-mcms-personal-building-marker="true"] {
            opacity: .38 !important;
            filter: grayscale(35%) brightness(.82) !important;
        }
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon.mcms-marker-mission {
            opacity: 1 !important;
            filter: drop-shadow(0 0 5px rgba(255,75,75,.75)) brightness(1.12) !important;
            z-index: 999 !important;
        }
        html[data-mcms-mission-pulse="true"] .leaflet-marker-icon.mcms-marker-mission { animation: mcmsMissionPulse 1.65s ease-in-out infinite !important; }
        html[data-mcms-show-alliance-missions="false"] .leaflet-marker-icon.mcms-marker-alliance-mission { display: none !important; }
        html[data-mcms-show-my-missions="false"] .leaflet-marker-icon.mcms-marker-my-mission { display: none !important; }
        html[data-mcms-show-vehicles="false"] .leaflet-marker-icon.mcms-marker-vehicle,
        html[data-mcms-show-vehicles="false"] .leaflet-marker-icon[data-mcms-vehicle-marker="true"] { display: none !important; }
        html[data-mcms-show-buildings="false"] .leaflet-marker-icon.mcms-marker-personal-building,
        html[data-mcms-show-buildings="false"] .leaflet-marker-icon[data-mcms-personal-building-marker="true"] { display: none !important; }

        html[data-mcms-critical-view="true"] .leaflet-marker-icon.mcms-critical-view-hidden { display: none !important; }
        .leaflet-marker-icon.mcms-critical-view-focus {
            filter: drop-shadow(0 0 5px #fff) drop-shadow(0 0 12px #ff5252) brightness(1.22) !important;
            z-index: 1000 !important;
        }

        html[data-mcms-clean="true"] .leaflet-control-zoom,
        html[data-mcms-clean="true"] .leaflet-control-scale,
        html[data-mcms-clean="true"] .leaflet-control-attribution,
        html[data-mcms-clean="true"] #${SCRIPT.controlId} { display: none !important; }

        #${SCRIPT.cleanExitId} {
            display: none; position: fixed; top: 10px; right: 12px; z-index: 999999;
            padding: 7px 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,.22);
            background: rgba(10,14,20,.88); color: #fff; font: 900 11px/1.1 Arial, Helvetica, sans-serif;
            cursor: pointer; box-shadow: 0 8px 22px rgba(0,0,0,.34); backdrop-filter: blur(8px);
        }
        html[data-mcms-clean="true"] #${SCRIPT.cleanExitId} { display: block; }

        #${SCRIPT.controlId}, #${SCRIPT.controlId} *, #${SCRIPT.controlId} *::before, #${SCRIPT.controlId} *::after,
        #${SCRIPT.panelId}, #${SCRIPT.panelId} *, #${SCRIPT.panelId} *::before, #${SCRIPT.panelId} *::after {
            box-sizing: border-box !important;
            font-family: Arial, Helvetica, sans-serif !important;
            text-shadow: none !important;
            letter-spacing: normal !important;
        }

        #${SCRIPT.controlId} {
            position: absolute !important; z-index: 980 !important; color: #e9eef5 !important;
            user-select: none !important; pointer-events: auto !important; font-size: 11px !important; line-height: 1.15 !important;
            margin-left: var(--mcms-nudge-x, 0px) !important; margin-top: var(--mcms-nudge-y, 0px) !important;
            max-width: 210px !important;
        }
        #${SCRIPT.controlId}.mcms-hidden-by-menu { opacity: .28 !important; }
        #${SCRIPT.controlId}.mcms-pos-tl { left: 54px !important; top: 10px !important; }
        #${SCRIPT.controlId}.mcms-pos-tr { right: 12px !important; top: 48px !important; }
        #${SCRIPT.controlId}.mcms-pos-bl { left: 12px !important; bottom: 42px !important; }
        #${SCRIPT.controlId}.mcms-pos-br { right: 12px !important; bottom: 42px !important; }

        #${SCRIPT.controlId} button, #${SCRIPT.panelId} button, #${SCRIPT.panelId} input, #${SCRIPT.panelId} select {
            appearance: none !important; -webkit-appearance: none !important; margin: 0 !important; font: inherit !important;
            text-transform: none !important; box-shadow: none !important; outline: none !important;
        }

        #${SCRIPT.controlId} .mcms-shell {
            position: relative !important; display: inline-flex !important; align-items: stretch !important;
            width: 40px !important; height: 48px !important; border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,.25) !important; background: rgba(10,14,20,.80) !important;
            box-shadow: 0 5px 16px rgba(0,0,0,.30) !important; backdrop-filter: blur(6px) !important; overflow: hidden !important;
            flex-direction: column !important;
        }

        #${SCRIPT.controlId} .mcms-menu-btn {
            width: 100% !important; height: auto !important; min-height: 0 !important; flex: 1 1 auto !important; border: 0 !important; background: transparent !important;
            color: #fff !important; cursor: pointer !important; display: flex !important; align-items: center !important;
            justify-content: center !important; padding: 0 !important; font-size: 17px !important;
        }
        #${SCRIPT.controlId} .mcms-menu-btn:hover,
        #${SCRIPT.controlId} .mcms-menu-btn:focus-visible { background: rgba(255,255,255,.12) !important; }
        #${SCRIPT.controlId} .mcms-dock-toggle-btn {
            width: 100% !important; height: 15px !important; flex: 0 0 15px !important; border: 0 !important; border-top: 1px solid rgba(255,255,255,.16) !important;
            padding: 0 !important; background: rgba(255,255,255,.055) !important; color: rgba(255,255,255,.82) !important; cursor: pointer !important;
            display: flex !important; align-items: center !important; justify-content: center !important; font-size: 11px !important; line-height: 1 !important; font-weight: 900 !important;
        }
        #${SCRIPT.controlId} .mcms-dock-toggle-btn:hover,
        #${SCRIPT.controlId} .mcms-dock-toggle-btn:focus-visible { background: rgba(86,169,255,.22) !important; color: #fff !important; }
        #${SCRIPT.controlId} .mcms-dock-toggle-icon { display: block !important; transform: translateY(-1px) !important; }

        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins { display: none !important; }

        #${SCRIPT.controlId} .mcms-floating-filter {
            display: grid !important; grid-template-columns: repeat(2, 82px) !important; gap: 4px !important; margin-top: 6px !important; width: 168px !important;
        }
        #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"],
        #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] {
            grid-column: 1 / -1 !important;
        }
        #${SCRIPT.controlId} .mcms-float-btn, #${SCRIPT.controlId} .mcms-screen-pin-btn {
            border: 1px solid rgba(255,255,255,.18) !important; border-radius: 8px !important; color: rgba(255,255,255,.74) !important;
            cursor: pointer !important; font-size: 8.5px !important; line-height: 1 !important; font-weight: 900 !important;
            box-shadow: 0 3px 10px rgba(0,0,0,.25) !important; backdrop-filter: blur(6px) !important;
        }
        #${SCRIPT.controlId} .mcms-float-btn {
            height: 29px !important; background: rgba(10,14,20,.78) !important; padding: 0 5px !important;
            display: grid !important; grid-template-columns: 17px minmax(0,1fr) !important; align-items: center !important; gap: 5px !important;
            text-align: left !important; overflow: hidden !important;
        }
        #${SCRIPT.controlId} .mcms-float-key {
            width: 17px !important; height: 17px !important; border-radius: 6px !important; background: rgba(255,255,255,.12) !important;
            display: flex !important; align-items: center !important; justify-content: center !important; color: #fff !important;
            font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important;
        }
        #${SCRIPT.controlId} .mcms-float-label {
            min-width: 0 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important;
            font-size: 8.5px !important; line-height: 1 !important; font-weight: 900 !important;
        }
        #${SCRIPT.controlId} .mcms-float-label-tablet,
        #${SCRIPT.controlId} .mcms-float-label-mobile { display: none !important; }
        #${SCRIPT.controlId} .mcms-float-btn.mcms-on { background: rgba(25,118,210,.78) !important; color: #fff !important; border-color: rgba(120,190,255,.8) !important; }
        #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key { background: rgba(255,255,255,.22) !important; }
        #${SCRIPT.controlId} .mcms-screen-pins {
            display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 4px !important; margin-top: 6px !important;
            width: 160px !important; max-height: 156px !important; overflow-y: auto !important; overflow-x: hidden !important; scrollbar-width: thin !important;
        }
        #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
        #${SCRIPT.controlId} .mcms-screen-pin-btn {
            height: 25px !important; min-width: 0 !important; padding: 0 6px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; color: #fff !important;
        }
        #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-quick { background: rgba(16,78,138,.86) !important; border-color: rgba(86,169,255,.68) !important; }
        #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-custom { background: rgba(106,80,10,.88) !important; border-color: rgba(255,213,79,.70) !important; }

        #${SCRIPT.panelId} {
            display: none !important;
            position: fixed !important;
            width: 318px !important;
            max-width: calc(100vw - 24px) !important;
            padding: 9px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,.18) !important;
            background: rgba(10,14,20,.94) !important;
            color: #e9eef5 !important;
            box-shadow: 0 10px 28px rgba(0,0,0,.46) !important;
            backdrop-filter: blur(9px) !important;
            max-height: calc(100vh - 24px) !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            scrollbar-width: thin !important;
            left: 12px;
            top: 12px;
            right: auto;
            bottom: auto;
            z-index: 981 !important;
            user-select: none !important;
            font-size: 11px !important;
            line-height: 1.15 !important;
        }
        #${SCRIPT.panelId}.mcms-open { display: block !important; }
        #${SCRIPT.panelId}.mcms-dragging { opacity: .96 !important; cursor: grabbing !important; }

        #${SCRIPT.panelId} .mcms-header {
            display: grid !important; grid-template-columns: minmax(0, 1fr) 24px 24px !important; align-items: center !important; gap: 7px !important;
            margin: 0 0 8px 0 !important; padding: 0 0 7px 0 !important; border-bottom: 1px solid rgba(255,255,255,.12) !important; overflow: hidden !important;
        }
        #${SCRIPT.panelId} .mcms-drag-handle {
            min-width: 0 !important; cursor: grab !important; touch-action: none !important; user-select: none !important;
            border-radius: 9px !important; padding: 4px 6px !important; background: rgba(255,255,255,.055) !important; border: 1px solid rgba(255,255,255,.075) !important;
        }
        #${SCRIPT.panelId} .mcms-drag-handle:hover { background: rgba(255,255,255,.10) !important; }
        #${SCRIPT.panelId}.mcms-dragging .mcms-drag-handle { cursor: grabbing !important; }
        #${SCRIPT.panelId} .mcms-title { display: block !important; font-size: 13px !important; line-height: 1.1 !important; font-weight: 900 !important; color: #f2f6ff !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
        #${SCRIPT.panelId} .mcms-subtitle { display: block !important; margin-top: 2px !important; font-size: 9px !important; line-height: 1.15 !important; color: rgba(233,238,245,.64) !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
        #${SCRIPT.panelId} .mcms-close, #${SCRIPT.panelId} .mcms-reset-panel {
            width: 24px !important; height: 24px !important; border: 0 !important; border-radius: 8px !important; background: rgba(255,255,255,.10) !important;
            color: rgba(255,255,255,.88) !important; cursor: pointer !important; font-size: 15px !important; line-height: 24px !important; text-align: center !important; padding: 0 !important;
        }
        #${SCRIPT.panelId} .mcms-close:hover, #${SCRIPT.panelId} .mcms-reset-panel:hover { background: rgba(255,255,255,.18) !important; }
        #${SCRIPT.panelId} .mcms-tabs { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 5px !important; margin-bottom: 8px !important; }
        #${SCRIPT.panelId} .mcms-tab-btn { height: 26px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 8px !important; background: rgba(255,255,255,.06) !important; color: rgba(255,255,255,.78) !important; cursor: pointer !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; padding: 0 !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-tab-btn.mcms-active, #${SCRIPT.panelId} .mcms-theme-btn.mcms-active, #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on, #${SCRIPT.panelId} .mcms-position-btn.mcms-active, #${SCRIPT.panelId} .mcms-pin-btn.mcms-on { background: rgba(25,118,210,.42) !important; border-color: rgba(120,190,255,.78) !important; color: #fff !important; }
        #${SCRIPT.panelId} .mcms-tab-panel { display: none !important; }
        #${SCRIPT.panelId} .mcms-tab-panel.mcms-active { display: block !important; }
        #${SCRIPT.panelId} .mcms-grid-2 { display: grid !important; grid-template-columns: repeat(2, minmax(0,1fr)) !important; gap: 7px !important; width: 100% !important; min-width: 0 !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-theme-btn, #${SCRIPT.panelId} .mcms-toggle-btn, #${SCRIPT.panelId} .mcms-place-main {
            width: 100% !important; min-width: 0 !important; height: 42px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 10px !important;
            background: rgba(255,255,255,.065) !important; color: #eef4ff !important; padding: 6px !important; cursor: pointer !important; text-align: left !important;
            display: grid !important; grid-template-columns: 20px minmax(0,1fr) !important; align-items: center !important; gap: 6px !important; overflow: hidden !important;
        }
        #${SCRIPT.panelId} .mcms-theme-btn:hover, #${SCRIPT.panelId} .mcms-toggle-btn:hover, #${SCRIPT.panelId} .mcms-place-main:hover { background: rgba(255,255,255,.14) !important; border-color: rgba(255,255,255,.30) !important; }
        #${SCRIPT.panelId} .mcms-iconbox { width: 20px !important; height: 20px !important; min-width: 20px !important; border-radius: 7px !important; background: rgba(255,255,255,.11) !important; display: flex !important; align-items: center !important; justify-content: center !important; color: rgba(255,255,255,.86) !important; font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-text { display: block !important; min-width: 0 !important; max-width: 100% !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-label { display: block !important; width: 100% !important; color: #f4f7ff !important; font-size: 10.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
        #${SCRIPT.panelId} .mcms-pill { display: inline-block !important; margin-top: 4px !important; max-width: 78px !important; padding: 1px 5px !important; border-radius: 999px !important; background: rgba(255,255,255,.13) !important; color: rgba(255,255,255,.82) !important; font-size: 7.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-section-label { margin: 9px 0 6px 0 !important; color: rgba(233,238,245,.62) !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; letter-spacing: .55px !important; text-transform: uppercase !important; }
        #${SCRIPT.panelId} .mcms-row { display: grid !important; grid-template-columns: minmax(0,1fr) 100px !important; gap: 7px !important; align-items: center !important; margin-bottom: 7px !important; }
        #${SCRIPT.panelId} .mcms-row-label { color: rgba(255,255,255,.82) !important; font-size: 10px !important; font-weight: 800 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
        #${SCRIPT.panelId} .mcms-input, #${SCRIPT.panelId} .mcms-select { width: 100% !important; height: 27px !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 8px !important; background: rgba(255,255,255,.08) !important; color: #fff !important; font-size: 10px !important; font-weight: 800 !important; padding: 0 7px !important; }
        #${SCRIPT.panelId} .mcms-select option { color: #111 !important; }
        #${SCRIPT.panelId} .mcms-position-grid, #${SCRIPT.panelId} .mcms-nudge-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 6px !important; width: 100% !important; }
        #${SCRIPT.panelId} .mcms-nudge-grid { grid-template-columns: repeat(5, minmax(0,1fr)) !important; }
        #${SCRIPT.panelId} .mcms-position-btn, #${SCRIPT.panelId} .mcms-small-btn, #${SCRIPT.panelId} .mcms-bookmark-btn, #${SCRIPT.panelId} .mcms-pin-btn { width: 100% !important; min-width: 0 !important; height: 28px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 9px !important; background: rgba(255,255,255,.065) !important; color: rgba(255,255,255,.84) !important; cursor: pointer !important; font-size: 9px !important; line-height: 28px !important; font-weight: 900 !important; text-align: center !important; padding: 0 !important; overflow: hidden !important; }
        #${SCRIPT.panelId} .mcms-position-btn:hover, #${SCRIPT.panelId} .mcms-small-btn:hover, #${SCRIPT.panelId} .mcms-bookmark-btn:hover, #${SCRIPT.panelId} .mcms-pin-btn:hover { background: rgba(255,255,255,.14) !important; }
        #${SCRIPT.panelId} .mcms-quick-row { display: grid !important; grid-template-columns: minmax(0,1fr) 44px !important; gap: 6px !important; margin-bottom: 6px !important; }
        #${SCRIPT.panelId} .mcms-bookmark-row { display: grid !important; grid-template-columns: minmax(0,1fr) 32px 38px 34px 26px !important; gap: 5px !important; align-items: center !important; margin-bottom: 5px !important; }
        #${SCRIPT.panelId} .mcms-bookmark-name { color: rgba(255,255,255,.86) !important; font-size: 10px !important; font-weight: 850 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
        #${SCRIPT.panelId} .mcms-status { margin-top: 8px !important; padding: 7px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.12) !important; background: rgba(255,255,255,.055) !important; color: rgba(255,255,255,.68) !important; font-size: 9px !important; line-height: 1.25 !important; }
        #${SCRIPT.panelId} .mcms-input, #${SCRIPT.panelId} .mcms-select { user-select: text !important; }
        #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 92px minmax(0,1fr) !important; }
        #${SCRIPT.panelId} .mcms-discord-preview { margin-top:8px !important; min-height:72px !important; }
        #${SCRIPT.panelId} .mcms-discord-empty { padding:14px 10px !important; border:1px dashed rgba(88,166,255,.28) !important; border-radius:10px !important; background:linear-gradient(135deg,rgba(88,166,255,.06),rgba(124,77,255,.05)) !important; color:rgba(255,255,255,.58) !important; font-size:9px !important; line-height:1.35 !important; text-align:center !important; }
        #${SCRIPT.panelId} .mcms-discord-card { padding:10px !important; border-radius:12px !important; border:1px solid rgba(255,255,255,.14) !important; background:linear-gradient(145deg,rgba(22,28,38,.96),rgba(11,15,22,.98)) !important; box-shadow:inset 0 1px rgba(255,255,255,.04),0 8px 18px rgba(0,0,0,.22) !important; }
        #${SCRIPT.panelId} .mcms-discord-card[data-tone="positive"] { border-color:rgba(46,204,113,.48) !important; box-shadow:inset 3px 0 #2ecc71,0 8px 18px rgba(0,0,0,.22) !important; }
        #${SCRIPT.panelId} .mcms-discord-card[data-tone="negative"] { border-color:rgba(231,76,60,.52) !important; box-shadow:inset 3px 0 #e74c3c,0 8px 18px rgba(0,0,0,.22) !important; }
        #${SCRIPT.panelId} .mcms-discord-card[data-tone="neutral"] { border-color:rgba(241,196,15,.42) !important; box-shadow:inset 3px 0 #f1c40f,0 8px 18px rgba(0,0,0,.22) !important; }
        #${SCRIPT.panelId} .mcms-discord-head { display:flex !important; justify-content:space-between !important; align-items:flex-start !important; gap:8px !important; margin-bottom:8px !important; }
        #${SCRIPT.panelId} .mcms-discord-title { color:#fff !important; font-size:10px !important; font-weight:950 !important; letter-spacing:.35px !important; }
        #${SCRIPT.panelId} .mcms-discord-date { margin-top:2px !important; color:rgba(255,255,255,.54) !important; font-size:8px !important; font-weight:800 !important; }
        #${SCRIPT.panelId} .mcms-discord-result { padding:3px 6px !important; border-radius:999px !important; background:rgba(255,255,255,.08) !important; color:#fff !important; font-size:8px !important; font-weight:950 !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-discord-stats { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
        #${SCRIPT.panelId} .mcms-discord-stat { min-width:0 !important; padding:7px 5px !important; border-radius:8px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }
        #${SCRIPT.panelId} .mcms-discord-stat span { display:block !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:900 !important; text-transform:uppercase !important; letter-spacing:.5px !important; }
        #${SCRIPT.panelId} .mcms-discord-stat strong { display:block !important; margin-top:3px !important; color:#fff !important; font-size:10px !important; font-weight:950 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.panelId} .mcms-discord-breakdowns { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:6px !important; margin-top:7px !important; }
        #${SCRIPT.panelId} .mcms-discord-breakdown { min-width:0 !important; padding:7px !important; border-radius:8px !important; background:rgba(255,255,255,.04) !important; }
        #${SCRIPT.panelId} .mcms-discord-breakdown b { display:block !important; margin-bottom:4px !important; color:#bbdefb !important; font-size:7.5px !important; text-transform:uppercase !important; letter-spacing:.55px !important; }
        #${SCRIPT.panelId} .mcms-discord-line { display:flex !important; justify-content:space-between !important; gap:5px !important; margin-top:3px !important; color:rgba(255,255,255,.68) !important; font-size:7.5px !important; }
        #${SCRIPT.panelId} .mcms-discord-line span { min-width:0 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-discord-line strong { color:#fff !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-discord-foot { margin-top:7px !important; padding-top:6px !important; border-top:1px solid rgba(255,255,255,.08) !important; color:rgba(255,255,255,.48) !important; font-size:7.5px !important; line-height:1.3 !important; }
        #${SCRIPT.panelId} .mcms-discord-status[data-tone="good"] { border-color:rgba(46,204,113,.38) !important; color:#9be8b8 !important; }
        #${SCRIPT.panelId} .mcms-discord-status[data-tone="bad"] { border-color:rgba(231,76,60,.42) !important; color:#ffaaa1 !important; }
        #${SCRIPT.panelId} .mcms-discord-status[data-tone="busy"] { border-color:rgba(52,152,219,.42) !important; color:#9bd5ff !important; }
        #${SCRIPT.panelId} .mcms-discord-mini-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:6px !important; }
        #${SCRIPT.panelId} .mcms-discord-mini-stats span { min-width:0 !important; padding:5px 4px !important; border-radius:7px !important; background:rgba(88,166,255,.07) !important; color:rgba(255,255,255,.52) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }
        #${SCRIPT.panelId} .mcms-discord-mini-stats b { display:block !important; margin-top:2px !important; color:#fff !important; font-size:7.8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-discord-chart { display:block !important; width:100% !important; margin-top:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:#0b1018 !important; }
        #${SCRIPT.panelId} .mcms-discord-date-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
        #${SCRIPT.panelId} .mcms-discord-date-grid .mcms-row { grid-template-columns:56px minmax(0,1fr) !important; }
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
            border: 1px solid rgba(255,193,74,.94) !important; background: linear-gradient(145deg, rgba(86,46,3,.96), rgba(27,17,6,.96)) !important;
            color: #ffe4a8 !important; box-shadow: 0 0 0 2px rgba(0,0,0,.48), 0 0 11px rgba(255,145,24,.55) !important;
            font: 950 9px/1 Arial, Helvetica, sans-serif !important; overflow: visible !important;
            animation: mcmsTransportWatcherPulse 1.85s ease-in-out infinite !important;
        }
        .mcms-transport-watcher-badge svg { width: 17px !important; height: 17px !important; display:block !important; overflow:visible !important; }
        .mcms-transport-watcher-badge svg * { vector-effect: non-scaling-stroke !important; }
        .mcms-transport-watcher-badge.mcms-transport-patient { border-color: rgba(255,194,71,.96) !important; color:#fff1c7 !important; }
        .mcms-transport-watcher-badge.mcms-transport-prisoner { border-color: rgba(255,139,53,.98) !important; color:#ffd0a5 !important; background:linear-gradient(145deg,rgba(91,35,4,.97),rgba(28,12,4,.97)) !important; }
        .mcms-transport-watcher-count { position:absolute !important; right:-7px !important; top:-7px !important; min-width:15px !important; height:15px !important; padding:0 3px !important; border-radius:999px !important; border:1px solid rgba(255,255,255,.86) !important; background:#e67600 !important; color:#fff !important; font:950 8px/13px Arial,Helvetica,sans-serif !important; text-align:center !important; box-shadow:0 1px 4px rgba(0,0,0,.65) !important; }
        .mcms-transport-watcher-badge.mcms-transport-side-left .mcms-transport-watcher-count { left:-7px !important; right:auto !important; }
        @keyframes mcmsTransportWatcherPulse { 0%,100%{transform:translate(-50%,-50%) scale(1);box-shadow:0 0 0 2px rgba(0,0,0,.48),0 0 8px rgba(255,145,24,.38)} 50%{transform:translate(-50%,-50%) scale(1.08);box-shadow:0 0 0 2px rgba(0,0,0,.55),0 0 16px rgba(255,145,24,.82)} }
        @media (prefers-reduced-motion: reduce) { .mcms-transport-watcher-badge { animation:none !important; } }

        .mcms-resource-gap-badge {
            min-width: 31px !important; height: 19px !important; padding: 0 6px !important; border-radius: 7px !important;
            border: 1px solid rgba(255,146,49,.88) !important; background: rgba(48,20,3,.91) !important; color: #ffd29a !important;
            box-shadow: 0 0 0 2px rgba(0,0,0,.38), 0 2px 8px rgba(255,112,20,.27) !important;
            font: 950 8.5px/1 Arial,Helvetica,sans-serif !important; letter-spacing:.1px !important;
        }
        .mcms-resource-gap-badge.mcms-gap-uncovered { border-color:#ff574d !important; color:#fff !important; background:rgba(91,11,7,.94) !important; box-shadow:0 0 0 2px rgba(0,0,0,.42),0 0 11px rgba(255,45,35,.46) !important; }

        #${SCRIPT.missionInspectorId} .mcms-inspector-gap { margin-top:6px !important; padding:7px !important; border-radius:7px !important; border:1px solid rgba(255,152,52,.38) !important; background:rgba(77,31,4,.18) !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-gap-title { display:flex !important; align-items:center !important; justify-content:space-between !important; gap:8px !important; color:#ffd29a !important; font-size:8px !important; font-weight:950 !important; letter-spacing:.4px !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-gap-row { display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:7px !important; margin-top:4px !important; color:#e8edf4 !important; font-size:8px !important; line-height:1.3 !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-gap-row span:last-child { color:#9fb0c2 !important; text-align:right !important; white-space:nowrap !important; }

        #${SCRIPT.panelId} .mcms-ops-session-grid {
            display: grid !important; grid-template-columns: repeat(2,minmax(0,1fr)) !important; gap: 6px !important;
        }
        #${SCRIPT.panelId} .mcms-ops-stat {
            min-width: 0 !important; padding: 8px !important; border-radius: 9px !important;
            border: 1px solid rgba(255,255,255,.11) !important; background: rgba(255,255,255,.055) !important;
        }
        #${SCRIPT.panelId} .mcms-ops-stat-label { display:block !important; color:rgba(255,255,255,.56) !important; font-size:7.5px !important; font-weight:900 !important; text-transform:uppercase !important; letter-spacing:.45px !important; }
        #${SCRIPT.panelId} .mcms-ops-stat-value { display:block !important; margin-top:4px !important; color:#fff !important; font-size:13px !important; line-height:1 !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-ops-list { display:grid !important; gap:5px !important; }
        #${SCRIPT.panelId} .mcms-ops-entry {
            display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important;
            padding:7px !important; border-radius:8px !important; border:1px solid rgba(255,255,255,.10) !important; background:rgba(255,255,255,.045) !important;
        }
        #${SCRIPT.panelId} .mcms-ops-entry-main { min-width:0 !important; }
        #${SCRIPT.panelId} .mcms-ops-entry-title { display:block !important; color:#f5f7ff !important; font-size:9.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.panelId} .mcms-ops-entry-meta { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:7.5px !important; font-weight:800 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.panelId} .mcms-ops-entry-value { color:#ffe082 !important; font-size:10px !important; font-weight:950 !important; white-space:nowrap !important; }
        #${SCRIPT.panelId} .mcms-history-latest { display:grid !important; gap:5px !important; }
        #${SCRIPT.panelId} .mcms-history-older {
            margin-top:2px !important; border:1px solid rgba(255,255,255,.11) !important; border-radius:8px !important;
            background:rgba(255,255,255,.035) !important; overflow:hidden !important;
        }
        #${SCRIPT.panelId} .mcms-history-older > summary {
            display:block !important; padding:7px 9px !important; cursor:pointer !important; list-style:none !important;
            color:rgba(255,255,255,.68) !important; font-size:8px !important; font-weight:900 !important; letter-spacing:.35px !important; text-transform:uppercase !important;
            user-select:none !important;
        }
        #${SCRIPT.panelId} .mcms-history-older > summary::-webkit-details-marker { display:none !important; }
        #${SCRIPT.panelId} .mcms-history-older > summary::after { content:'▾' !important; float:right !important; color:rgba(255,255,255,.48) !important; }
        #${SCRIPT.panelId} .mcms-history-older:not([open]) > summary::after { content:'▸' !important; }
        #${SCRIPT.panelId} .mcms-history-scroll {
            display:grid !important; gap:5px !important; max-height:126px !important; overflow-y:auto !important; overscroll-behavior:contain !important;
            padding:0 5px 5px !important; scrollbar-width:thin !important;
        }
        #${SCRIPT.panelId} .mcms-empty-state { padding:10px !important; border:1px dashed rgba(255,255,255,.12) !important; border-radius:8px !important; color:rgba(255,255,255,.52) !important; font-size:8.5px !important; text-align:center !important; }

        #${SCRIPT.criticalDrawerId} {
            display:none !important; position:fixed !important; right:14px !important; top:66px !important; z-index:990 !important;
            width:330px !important; max-width:calc(100vw - 28px) !important; max-height:calc(100vh - 82px) !important; overflow:auto !important;
            padding:10px !important; border-radius:14px !important; border:1px solid rgba(255,255,255,.18) !important;
            background:rgba(10,14,20,.95) !important; color:#fff !important; box-shadow:0 14px 34px rgba(0,0,0,.48) !important;
            backdrop-filter:blur(10px) !important; -webkit-backdrop-filter:blur(10px) !important;
            font-family:Arial,Helvetica,sans-serif !important;
        }
        #${SCRIPT.criticalDrawerId}.mcms-open { display:block !important; }
        #${SCRIPT.criticalDrawerId}, #${SCRIPT.criticalDrawerId} * { box-sizing:border-box !important; }
        #${SCRIPT.criticalDrawerId} .mcms-drawer-head { display:grid !important; grid-template-columns:minmax(0,1fr) 28px !important; gap:8px !important; align-items:center !important; padding-bottom:8px !important; border-bottom:1px solid rgba(255,255,255,.12) !important; }
        #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size:13px !important; font-weight:950 !important; letter-spacing:.3px !important; }
        #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.58) !important; font-size:8px !important; font-weight:800 !important; }
        #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width:28px !important; height:28px !important; border:0 !important; border-radius:8px !important; background:rgba(255,255,255,.10) !important; color:#fff !important; cursor:pointer !important; font-weight:900 !important; }
        #${SCRIPT.criticalDrawerId} .mcms-drawer-list { display:grid !important; gap:6px !important; margin-top:8px !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-row { width:100% !important; display:grid !important; grid-template-columns:86px minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:rgba(255,255,255,.05) !important; color:#fff !important; cursor:pointer !important; text-align:left !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-row:hover { background:rgba(255,255,255,.11) !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-aged { border-color:rgba(255,183,77,.34) !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-high { border-color:rgba(255,112,67,.48) !important; background:rgba(68,24,8,.18) !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-critical { border-color:rgba(255,82,82,.62) !important; background:rgba(88,12,12,.32) !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { color:#ffb74d !important; font-size:8px !important; font-weight:950 !important; letter-spacing:.45px !important; white-space:nowrap !important; text-transform:uppercase !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-row.mcms-age-critical .mcms-critical-age-band { color:#ff6b6b !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-name { display:block !important; min-width:0 !important; color:#fff !important; font-size:9.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-meta { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:7.5px !important; font-weight:800 !important; }
        #${SCRIPT.criticalDrawerId} .mcms-critical-age { color:#bbdefb !important; font-size:8.5px !important; font-weight:950 !important; white-space:nowrap !important; }

        #${SCRIPT.payoutFlashId} {
            position: fixed !important; left: 0; top: 0; width: 0; height: 0;
            z-index: 2147483647 !important; overflow: hidden !important;
            pointer-events: none !important; opacity: 0 !important;
            isolation: isolate !important;
        }
        #${SCRIPT.payoutFlashId}.mcms-payout-active { opacity: 1 !important; }
        #${SCRIPT.payoutFlashId}, #${SCRIPT.payoutFlashId} * {
            box-sizing: border-box !important; pointer-events: none !important; user-select: none !important;
            font-family: Arial, Helvetica, sans-serif !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-light {
            position: absolute !important; inset: -12% !important; opacity: 0;
            will-change: opacity, transform !important; mix-blend-mode: screen !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-red {
            background:
                radial-gradient(ellipse at 0% 45%, rgba(255,22,22,.62) 0%, rgba(255,22,22,.30) 25%, rgba(255,22,22,0) 62%),
                linear-gradient(90deg, rgba(255,18,18,.34) 0%, rgba(255,18,18,0) 48%) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-blue {
            background:
                radial-gradient(ellipse at 100% 55%, rgba(25,113,255,.68) 0%, rgba(25,113,255,.32) 25%, rgba(25,113,255,0) 62%),
                linear-gradient(270deg, rgba(20,103,255,.38) 0%, rgba(20,103,255,0) 48%) !important;
        }
        #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-red {
            animation: mcmsPayoutRed var(--mcms-payout-duration, 3000ms) ease-in-out both !important;
        }
        #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-blue {
            animation: mcmsPayoutBlue var(--mcms-payout-duration, 3000ms) ease-in-out both !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-cinematic {
            position: absolute !important; inset: 0 !important; opacity: 0;
            background:
                radial-gradient(ellipse at center, rgba(0,0,0,0) 25%, rgba(0,0,0,.18) 72%, rgba(0,0,0,.38) 100%),
                linear-gradient(180deg, rgba(0,0,0,.22) 0%, rgba(0,0,0,0) 24%, rgba(0,0,0,0) 76%, rgba(0,0,0,.22) 100%) !important;
            will-change: opacity !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-banner {
            position: absolute !important; left: 50% !important; top: 50% !important;
            width: min(660px, calc(100% - 34px)) !important; min-width: 280px !important;
            padding: 19px 34px 17px !important; border-radius: 0 !important;
            border-top: 1px solid var(--mcms-payout-accent-soft, rgba(247,205,83,.42)) !important;
            border-bottom: 1px solid var(--mcms-payout-accent-soft, rgba(247,205,83,.42)) !important;
            border-left: 0 !important; border-right: 0 !important;
            background: linear-gradient(90deg, rgba(2,5,10,0) 0%, rgba(2,5,10,.42) 10%, rgba(2,5,10,.84) 50%, rgba(2,5,10,.42) 90%, rgba(2,5,10,0) 100%) !important;
            color: #fff !important;
            box-shadow: 0 18px 42px rgba(0,0,0,.40), inset 0 1px 0 rgba(255,255,255,.035) !important;
            backdrop-filter: blur(3px) !important; -webkit-backdrop-filter: blur(3px) !important;
            text-align: center !important; overflow: visible !important;
            opacity: 0; transform: translate(-50%, -50%) scale(1.08); filter: blur(7px);
        }
        #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-banner {
            animation: mcmsPayoutBanner var(--mcms-payout-duration, 3000ms) cubic-bezier(.16,.78,.24,1) both !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-title {
            display: block !important; color: var(--mcms-payout-accent, #f4c84f) !important;
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", "Arial Black", sans-serif !important;
            font-size: clamp(34px, 5.4vw, 64px) !important; line-height: .92 !important; font-weight: 900 !important;
            letter-spacing: 1.9px !important; text-transform: uppercase !important; white-space: nowrap !important;
            text-shadow: 0 3px 0 rgba(0,0,0,.78), 0 5px 18px rgba(0,0,0,.74), 0 0 18px var(--mcms-payout-glow, rgba(244,200,79,.16)) !important;
            transform: scaleX(.94) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-divider {
            display: block !important; width: min(390px, 78%) !important; height: 1px !important;
            margin: 11px auto 9px !important;
            background: linear-gradient(90deg, transparent, var(--mcms-payout-accent, #f4c84f) 24%, rgba(255,255,255,.90) 50%, var(--mcms-payout-accent, #f4c84f) 76%, transparent) !important;
            box-shadow: 0 0 8px rgba(244,200,79,.24) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-particles {
            position:absolute !important; inset:0 !important; opacity:0; transform:scale(1.04);
            background-image:
                radial-gradient(circle at 18% 34%, var(--mcms-payout-accent, #f4c84f) 0 1px, transparent 2px),
                radial-gradient(circle at 32% 68%, var(--mcms-payout-accent, #f4c84f) 0 1.5px, transparent 2.5px),
                radial-gradient(circle at 61% 27%, #fff 0 1px, transparent 2px),
                radial-gradient(circle at 78% 61%, var(--mcms-payout-accent, #f4c84f) 0 1.4px, transparent 2.4px),
                radial-gradient(circle at 89% 42%, #fff 0 1px, transparent 2px);
            background-size:190px 150px,230px 170px,270px 210px,310px 190px,350px 230px !important;
            mix-blend-mode:screen !important; pointer-events:none !important;
        }
        #${SCRIPT.payoutFlashId}[data-tier="high"] .mcms-payout-particles,
        #${SCRIPT.payoutFlashId}[data-tier="elite"] .mcms-payout-particles { opacity:.34; }
        #${SCRIPT.payoutFlashId}[data-tier="elite"] .mcms-payout-particles { opacity:.52; }
        #${SCRIPT.payoutFlashId} .mcms-payout-tier {
            display:inline-block !important; margin-bottom:7px !important; padding:3px 8px !important; border-radius:999px !important;
            border:1px solid var(--mcms-payout-accent-soft, rgba(247,205,83,.42)) !important; background:rgba(0,0,0,.28) !important;
            color:var(--mcms-payout-accent, #f4c84f) !important; font-size:7.5px !important; line-height:1 !important; font-weight:950 !important;
            letter-spacing:1.6px !important; text-transform:uppercase !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-mission {
            display:block !important; margin-top:8px !important; color:#fff !important;
            font-size:clamp(12px,2vw,18px) !important; line-height:1.05 !important; font-weight:950 !important;
            white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;
            text-shadow:0 2px 8px rgba(0,0,0,.85) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-mission:empty { display:none !important; }
        #${SCRIPT.payoutFlashId} .mcms-payout-source {
            display:block !important; margin-top:5px !important; color:var(--mcms-payout-accent, #f4c84f) !important;
            font-size:8px !important; line-height:1 !important; font-weight:950 !important; letter-spacing:2px !important; text-transform:uppercase !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-kicker {
            display: block !important; color: rgba(255,255,255,.78) !important;
            font-family: "Arial Narrow", Arial, Helvetica, sans-serif !important;
            font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important;
            letter-spacing: 3px !important; text-transform: uppercase !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-amount {
            display: block !important; margin-top: 7px !important; color: #fff !important;
            font-family: "Arial Black", "Arial Narrow Bold", Arial, Helvetica, sans-serif !important;
            font-size: clamp(20px, 3vw, 32px) !important; line-height: 1 !important; font-weight: 950 !important;
            letter-spacing: 1.5px !important; white-space: nowrap !important;
            text-shadow: 0 2px 0 rgba(0,0,0,.74), 0 5px 15px rgba(0,0,0,.68) !important;
        }

        #${SCRIPT.payoutFlashId} .mcms-payout-vc-sunset,
        #${SCRIPT.payoutFlashId} .mcms-payout-vc-grid {
            position: absolute !important; inset: 0 !important; opacity: 0;
            pointer-events: none !important; will-change: opacity, transform !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-vc-sunset {
            background:
                radial-gradient(circle at 50% 54%, rgba(255,238,104,.92) 0 5%, rgba(255,132,160,.58) 5.5% 11%, rgba(255,71,180,.24) 12% 25%, transparent 39%),
                linear-gradient(180deg, rgba(17,9,62,.76) 0%, rgba(85,19,112,.64) 34%, rgba(241,48,142,.34) 60%, rgba(5,17,50,.72) 100%) !important;
            mix-blend-mode: screen !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-vc-grid {
            top: 56% !important;
            background:
                repeating-linear-gradient(90deg, rgba(44,238,255,.24) 0 1px, transparent 1px 54px),
                repeating-linear-gradient(180deg, rgba(255,70,201,.22) 0 1px, transparent 1px 32px) !important;
            transform-origin: 50% 0 !important;
            transform: perspective(380px) rotateX(62deg) scale(1.35) !important;
            mask-image: linear-gradient(180deg, rgba(0,0,0,.82), transparent 76%) !important;
            -webkit-mask-image: linear-gradient(180deg, rgba(0,0,0,.82), transparent 76%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-cinematic {
            background:
                radial-gradient(ellipse at center, rgba(0,0,0,0) 18%, rgba(20,3,45,.20) 62%, rgba(4,3,20,.58) 100%),
                linear-gradient(180deg, rgba(9,3,33,.38), transparent 28%, transparent 72%, rgba(4,5,28,.52)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner {
            width: min(720px, calc(100% - 28px)) !important;
            padding: 25px 38px 23px !important;
            border-top: 2px solid rgba(255,92,210,.78) !important;
            border-bottom: 2px solid rgba(62,232,255,.78) !important;
            background:
                linear-gradient(90deg, transparent 0%, rgba(16,4,42,.58) 8%, rgba(29,5,58,.92) 30%, rgba(12,7,45,.94) 70%, rgba(7,25,57,.62) 92%, transparent 100%) !important;
            box-shadow:
                0 0 18px rgba(255,64,199,.28),
                0 0 34px rgba(44,220,255,.20),
                0 20px 46px rgba(0,0,0,.42),
                inset 0 1px 0 rgba(255,255,255,.09) !important;
            backdrop-filter: blur(5px) saturate(125%) !important;
            -webkit-backdrop-filter: blur(5px) saturate(125%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::after {
            content: "" !important; position: absolute !important; top: -7px !important; bottom: -7px !important;
            width: 2px !important; opacity: .75 !important; pointer-events: none !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::before {
            left: 9% !important; background: linear-gradient(180deg, transparent, #ff5ed8, transparent) !important;
            box-shadow: 0 0 13px #ff5ed8 !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::after {
            right: 9% !important; background: linear-gradient(180deg, transparent, #42e9ff, transparent) !important;
            box-shadow: 0 0 13px #42e9ff !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title {
            color: #ff75cf !important;
            font-family: "Brush Script MT", "Segoe Script", "Lucida Handwriting", cursive !important;
            font-size: clamp(42px, 7vw, 82px) !important;
            font-style: italic !important; font-weight: 900 !important;
            letter-spacing: -1px !important; line-height: .86 !important;
            text-transform: none !important;
            transform: rotate(-2deg) skewX(-5deg) !important;
            text-shadow:
                2px 2px 0 #4cecff,
                4px 4px 0 rgba(13,7,48,.95),
                0 0 12px rgba(255,74,201,.82),
                0 0 28px rgba(54,226,255,.42) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-divider {
            height: 2px !important; margin: 15px auto 11px !important;
            background: linear-gradient(90deg, transparent, #ff61d1 20%, #fff 48%, #4cecff 78%, transparent) !important;
            box-shadow: 0 0 9px rgba(255,72,202,.54), 0 0 14px rgba(54,228,255,.42) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-tier {
            border-color: rgba(255,91,210,.72) !important;
            background: rgba(19,4,52,.60) !important;
            color: #72efff !important;
            box-shadow: 0 0 10px rgba(255,75,203,.22), inset 0 0 8px rgba(69,228,255,.10) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-mission {
            color: #fff4fb !important; font-style: italic !important;
            text-shadow: 0 2px 8px #090318, 0 0 10px rgba(255,70,196,.28) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-source {
            color: var(--mcms-payout-accent, #77f2ff) !important;
            text-shadow: 0 0 9px var(--mcms-payout-glow, rgba(80,234,255,.34)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-kicker {
            color: #ff9bde !important; letter-spacing: 4px !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-amount {
            color: #f8ffff !important;
            font-style: italic !important;
            text-shadow:
                2px 2px 0 #e63fae,
                4px 4px 0 rgba(7,16,52,.94),
                0 0 12px rgba(67,231,255,.56) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-dust,
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-hud,
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-embers {
            position: absolute !important; inset: 0 !important; opacity: 0;
            pointer-events: none !important; will-change: opacity, transform, background-position !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-dust {
            background:
                radial-gradient(ellipse at 50% 105%, rgba(255,114,15,.42) 0 8%, rgba(135,61,14,.22) 24%, transparent 53%),
                radial-gradient(circle at 14% 74%, rgba(255,153,43,.22) 0 3%, rgba(90,76,48,.18) 15%, transparent 35%),
                radial-gradient(circle at 86% 28%, rgba(213,222,188,.14) 0 4%, rgba(65,73,54,.24) 18%, transparent 40%),
                radial-gradient(ellipse at 50% 52%, rgba(160,156,122,.12) 0 14%, rgba(26,31,23,.34) 48%, rgba(4,6,5,.70) 100%),
                repeating-radial-gradient(circle at 37% 44%, rgba(255,255,255,.028) 0 1px, transparent 1px 7px) !important;
            filter: contrast(126%) saturate(88%) !important;
            mix-blend-mode: screen !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-hud {
            background:
                linear-gradient(90deg, transparent 0 5.5%, rgba(255,151,28,.30) 5.5% 5.72%, transparent 5.72% 94.28%, rgba(255,151,28,.30) 94.28% 94.5%, transparent 94.5%),
                linear-gradient(180deg, transparent 0 12%, rgba(224,232,208,.10) 12% 12.2%, transparent 12.2% 87.8%, rgba(224,232,208,.08) 87.8% 88%, transparent 88%),
                repeating-linear-gradient(0deg, rgba(224,232,208,.035) 0 1px, transparent 1px 5px),
                repeating-linear-gradient(118deg, transparent 0 42px, rgba(255,151,30,.048) 42px 44px, transparent 44px 88px) !important;
            mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0,0,0,.86) 64%, transparent 100%) !important;
            -webkit-mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0,0,0,.86) 64%, transparent 100%) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-embers {
            overflow: hidden !important;
            mix-blend-mode: screen !important;
            filter: saturate(125%) contrast(110%) !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-ember {
            position: absolute !important;
            left: 50%; bottom: -18px;
            width: 3px; height: 9px;
            border-radius: 999px !important;
            opacity: 0;
            background: linear-gradient(180deg, #fff7bb 0%, #ffc14e 28%, #ff6d12 72%, rgba(154,24,0,0) 100%) !important;
            box-shadow: 0 0 5px rgba(255,200,83,.95), 0 0 12px rgba(255,92,16,.78), 0 0 22px rgba(255,66,0,.34) !important;
            transform-origin: 50% 100% !important;
            will-change: transform, opacity !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-cinematic {
            background:
                radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 10%, rgba(20,24,18,.16) 49%, rgba(2,4,3,.78) 100%),
                linear-gradient(180deg, rgba(12,17,11,.52), transparent 25%, transparent 68%, rgba(15,8,3,.72)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {
            width: min(820px, calc(100% - 24px)) !important;
            padding: 25px 34px 23px !important;
            border: 0 !important;
            border-left: 6px solid #ff8d18 !important;
            border-right: 2px solid rgba(217,224,200,.28) !important;
            background:
                radial-gradient(circle at 6% 102%, rgba(255,109,12,.26) 0 8%, transparent 30%),
                radial-gradient(circle at 90% -20%, rgba(160,176,134,.16) 0 15%, transparent 42%),
                linear-gradient(104deg, rgba(5,7,6,.98) 0%, rgba(23,28,20,.97) 34%, rgba(13,17,12,.98) 70%, rgba(4,6,5,.96) 100%),
                repeating-linear-gradient(116deg, rgba(255,255,255,.028) 0 1px, transparent 1px 6px),
                repeating-linear-gradient(24deg, transparent 0 48px, rgba(255,139,23,.035) 48px 50px, transparent 50px 96px) !important;
            clip-path: polygon(0 13px, 22px 0, 78% 0, calc(78% + 14px) 7px, 100% 7px, 100% calc(100% - 14px), calc(100% - 23px) 100%, 20% 100%, calc(20% - 13px) calc(100% - 7px), 0 calc(100% - 7px)) !important;
            box-shadow:
                0 0 0 1px rgba(218,224,201,.13),
                0 24px 58px rgba(0,0,0,.68),
                -15px 0 38px rgba(255,116,12,.18),
                inset 0 1px 0 rgba(255,255,255,.055),
                inset 0 -18px 40px rgba(0,0,0,.26) !important;
            backdrop-filter: blur(5px) contrast(120%) saturate(88%) !important;
            -webkit-backdrop-filter: blur(5px) contrast(120%) saturate(88%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::after {
            content: "" !important; position: absolute !important; pointer-events: none !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::before {
            left: 0 !important; right: 0 !important; top: 0 !important; height: 5px !important;
            background:
                repeating-linear-gradient(135deg, #ff941c 0 11px, #171a14 11px 22px),
                linear-gradient(90deg, rgba(255,145,27,.9), transparent) !important;
            box-shadow: 0 0 12px rgba(255,115,13,.26) !important;
            opacity: .94 !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::after {
            right: 17px !important; bottom: 11px !important; width: 92px !important; height: 10px !important;
            border-top: 2px solid rgba(255,145,25,.82) !important;
            border-bottom: 1px solid rgba(224,229,207,.24) !important;
            background: repeating-linear-gradient(90deg, rgba(255,145,25,.84) 0 6px, transparent 6px 11px) !important;
            filter: drop-shadow(0 0 5px rgba(255,112,10,.24)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title {
            display: block !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 8px !important;
            color: #f1f0e8 !important;
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", "Arial Black", sans-serif !important;
            font-size: clamp(31px, 5.05vw, 58px) !important;
            font-weight: 900 !important;
            letter-spacing: clamp(.8px, .24vw, 2.6px) !important;
            word-spacing: -1px !important;
            line-height: .88 !important;
            text-transform: uppercase !important;
            white-space: nowrap !important;
            transform: skewX(-5deg) scaleX(.89) !important;
            transform-origin: 50% 50% !important;
            text-shadow:
                2px 2px 0 rgba(2,3,2,.98),
                5px 5px 0 rgba(2,3,2,.96),
                8px 8px 0 rgba(255,116,13,.34),
                -1px -1px 0 rgba(255,255,255,.18),
                0 0 24px rgba(255,126,17,.15) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-long {
            font-size: clamp(27px, 4.25vw, 49px) !important;
            letter-spacing: clamp(.3px, .16vw, 1.5px) !important;
            transform: skewX(-5deg) scaleX(.84) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-very-long {
            font-size: clamp(23px, 3.65vw, 42px) !important;
            white-space: normal !important;
            text-wrap: balance !important;
            line-height: .94 !important;
            transform: skewX(-4deg) scaleX(.88) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-divider {
            height: 3px !important; width: min(500px, 76%) !important; margin: 14px auto 10px !important;
            background:
                linear-gradient(90deg, transparent, #ff8e19 14%, #f4f1e4 45%, #747f68 75%, transparent) !important;
            box-shadow: 0 0 12px rgba(255,121,15,.28) !important;
            transform: skewX(-18deg) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-tier {
            border-radius: 1px !important;
            border-color: rgba(255,145,25,.78) !important;
            background: linear-gradient(90deg, rgba(255,125,15,.18), rgba(20,24,18,.60)) !important;
            color: #ffac43 !important;
            letter-spacing: 2.25px !important;
            box-shadow: inset 4px 0 0 rgba(255,139,21,.92), 0 0 10px rgba(255,111,9,.10) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-mission {
            color: #f3f2e9 !important;
            text-transform: uppercase !important;
            letter-spacing: .6px !important;
            font-family: "Arial Narrow", Arial, sans-serif !important;
            text-shadow: 0 2px 10px rgba(0,0,0,.96) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-source {
            color: #ff9421 !important; letter-spacing: 2.7px !important;
            text-shadow: 0 0 12px rgba(255,112,10,.32) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-kicker {
            color: rgba(225,229,211,.64) !important; letter-spacing: 3.4px !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-amount {
            color: #ff9b27 !important;
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif !important;
            font-size: clamp(23px, 3.25vw, 35px) !important;
            letter-spacing: 2px !important;
            text-shadow: 2px 2px 0 #11140e, 0 0 14px rgba(255,126,17,.36), 0 0 28px rgba(255,78,4,.12) !important;
        }
        @media (max-width: 620px) {
            #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {
                width: calc(100% - 16px) !important;
                padding: 21px 16px 19px !important;
            }
            #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title {
                font-size: clamp(25px, 8vw, 39px) !important;
                letter-spacing: .5px !important;
                transform: skewX(-4deg) scaleX(.84) !important;
            }
            #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-long {
                font-size: clamp(21px, 6.8vw, 33px) !important;
                white-space: normal !important;
                text-wrap: balance !important;
            }
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-theme-fx,
        #${SCRIPT.payoutFlashId} .mcms-payout-theme-particles {
            position:absolute !important; inset:0 !important; opacity:0;
            pointer-events:none !important; overflow:hidden !important;
            will-change:opacity, transform, background-position, filter !important;
        }
        #${SCRIPT.payoutFlashId} .mcms-payout-theme-particles { mix-blend-mode:screen !important; }
        #${SCRIPT.payoutFlashId} .mcms-payout-theme-particle {
            position:absolute !important; opacity:0; pointer-events:none !important;
            will-change:opacity, transform !important;
        }



        /* Scarface Inspired — original black/ivory/red Miami-crime treatment. */
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-red {
            background:
                radial-gradient(ellipse at 10% 48%, rgba(154,5,14,.82) 0%, rgba(154,5,14,.36) 27%, transparent 64%),
                linear-gradient(90deg, rgba(4,4,4,.76) 0 49.2%, rgba(166,11,20,.22) 49.2% 51%, transparent 51%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-blue {
            background:
                radial-gradient(ellipse at 90% 52%, rgba(255,244,216,.46) 0%, rgba(219,178,87,.18) 31%, transparent 66%),
                linear-gradient(270deg, rgba(241,236,225,.28) 0 45%, rgba(164,12,20,.18) 49% 51%, transparent 55%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-cinematic {
            background:
                linear-gradient(90deg, rgba(0,0,0,.91) 0 49.35%, rgba(163,12,20,.78) 49.35% 50.65%, rgba(239,234,223,.80) 50.65% 100%),
                radial-gradient(ellipse at 50% 52%, transparent 10%, rgba(0,0,0,.24) 70%, rgba(0,0,0,.66) 100%) !important;
            mix-blend-mode:normal !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-a {
            background:
                radial-gradient(circle at 50% 71%, rgba(235,193,95,.32) 0 2%, transparent 2.5% 13%, rgba(235,193,95,.16) 13.5% 14%, transparent 14.5%),
                repeating-conic-gradient(from -18deg at 50% 71%, rgba(229,186,87,.12) 0 1deg, transparent 1deg 12deg),
                linear-gradient(90deg, rgba(0,0,0,.18) 0 49.25%, rgba(173,12,20,.40) 49.25% 50.75%, rgba(255,255,255,.05) 50.75% 100%) !important;
            mask-image:linear-gradient(180deg, transparent 0%, #000 15%, #000 88%, transparent 100%) !important;
            -webkit-mask-image:linear-gradient(180deg, transparent 0%, #000 15%, #000 88%, transparent 100%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-b {
            background:
                linear-gradient(108deg, transparent 0 46.8%, rgba(168,12,20,.78) 47% 47.7%, transparent 47.9% 100%),
                linear-gradient(72deg, transparent 0 52.2%, rgba(168,12,20,.36) 52.4% 52.8%, transparent 53% 100%),
                repeating-linear-gradient(0deg, rgba(230,193,106,.035) 0 1px, transparent 1px 7px),
                repeating-linear-gradient(90deg, rgba(230,193,106,.025) 0 1px, transparent 1px 96px) !important;
            opacity:.55;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-c {
            left:-22% !important; right:auto !important; width:45% !important;
            background:linear-gradient(100deg, transparent 0 42%, rgba(168,8,17,.10) 43%, rgba(204,20,29,.84) 48%, rgba(255,225,188,.42) 50%, rgba(152,5,13,.72) 52%, transparent 58% 100%) !important;
            filter:drop-shadow(0 0 15px rgba(181,12,21,.42)) !important;
            transform:skewX(-9deg) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {
            width:min(790px,calc(100% - 26px)) !important;
            padding:28px 44px 24px !important;
            border:1px solid rgba(217,178,89,.72) !important;
            border-top:4px solid #a70d16 !important;
            border-bottom:4px solid #a70d16 !important;
            background:
                linear-gradient(90deg, rgba(5,5,5,.985) 0 63%, rgba(34,20,18,.97) 63% 65%, rgba(234,228,215,.97) 65% 100%),
                repeating-linear-gradient(135deg, rgba(255,255,255,.018) 0 1px, transparent 1px 8px) !important;
            box-shadow:
                0 0 0 2px rgba(0,0,0,.84),
                0 0 0 3px rgba(217,178,89,.28),
                0 26px 62px rgba(0,0,0,.74),
                0 0 36px rgba(158,10,19,.18),
                inset -220px 0 80px rgba(255,255,255,.035) !important;
            overflow:hidden !important;
            backdrop-filter:none !important;
            -webkit-backdrop-filter:none !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::before {
            content:"MIAMI  •  POWER  •  MONEY" !important;
            position:absolute !important; left:18px !important; top:10px !important;
            color:rgba(224,188,101,.68) !important;
            font:900 7px/1 "Arial Narrow",Arial,sans-serif !important;
            letter-spacing:2.6px !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::after {
            content:"THE WORLD IS YOURS" !important;
            position:absolute !important; right:-58px !important; top:50% !important;
            width:180px !important;
            transform:translateY(-50%) rotate(90deg) !important;
            color:rgba(82,14,18,.68) !important;
            font:950 7px/1 "Arial Narrow",Arial,sans-serif !important;
            letter-spacing:2.2px !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title {
            color:#f1e8d7 !important;
            font-family:Impact,Haettenschweiler,"Arial Narrow Bold","Arial Black",sans-serif !important;
            font-size:clamp(36px,5.8vw,70px) !important;
            letter-spacing:2.4px !important;
            transform:skewX(-3deg) scaleX(.92) !important;
            -webkit-text-stroke:1px rgba(214,171,77,.82) !important;
            text-shadow:3px 3px 0 #120405,6px 6px 0 #8d0b13,0 0 22px rgba(220,179,84,.20) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title.mcms-payout-title-long {
            font-size:clamp(31px,5vw,59px) !important; letter-spacing:1.6px !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title.mcms-payout-title-very-long {
            font-size:clamp(27px,4.4vw,52px) !important; letter-spacing:1px !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-divider {
            height:3px !important; width:min(440px,82%) !important;
            background:linear-gradient(90deg,transparent,#9f0c15 13%,#d9b259 34%,#fff8e8 50%,#d9b259 66%,#9f0c15 87%,transparent) !important;
            box-shadow:0 0 11px rgba(173,15,24,.48),0 0 20px rgba(219,181,91,.20) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-tier {
            border-radius:0 !important; border:1px solid #cda954 !important;
            color:#f0d68d !important; background:rgba(15,5,5,.78) !important;
            box-shadow:inset 4px 0 0 #a70d16 !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-mission {
            color:#fff8ea !important; letter-spacing:.25px !important;
            text-shadow:0 2px 0 #000,0 0 9px #000 !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-source {
            color:#d7b45f !important; text-shadow:0 1px 0 #000,0 0 6px #000 !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-kicker {
            color:#bd2630 !important; font-weight:950 !important; letter-spacing:3.2px !important;
            text-shadow:0 1px 0 #000,0 0 6px rgba(0,0,0,.8) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-amount {
            color:#f2d27d !important;
            font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important;
            font-size:clamp(25px,3.55vw,39px) !important;
            letter-spacing:2.2px !important;
            -webkit-text-stroke:.5px rgba(83,12,16,.55) !important;
            text-shadow:2px 2px 0 #120405,4px 4px 0 #8c0a12,0 0 18px rgba(225,184,89,.36) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-particle {
            border-radius:0 !important;
            background:#f5e8be !important;
            box-shadow:0 0 5px #fff7d7,0 0 12px rgba(218,176,79,.78) !important;
            transform:rotate(45deg);
        }
        @media (max-width:620px) {
            #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {
                width:calc(100% - 16px) !important; padding:25px 19px 21px !important;
                background:linear-gradient(90deg,rgba(5,5,5,.985) 0 76%,rgba(234,228,215,.97) 76% 100%) !important;
            }
            #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title {
                font-size:clamp(29px,8.2vw,47px) !important; letter-spacing:1px !important; transform:skewX(-2deg) scaleX(.88) !important;
            }
            #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::after { display:none !important; }
        }

        /* Cyberpunk Inspired */
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-cinematic {
            background:radial-gradient(ellipse at 52% 48%, transparent 8%, rgba(0,12,18,.22) 52%, rgba(0,0,0,.86) 100%), linear-gradient(115deg, rgba(245,226,0,.12), transparent 35%, rgba(0,229,255,.10)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-a {
            background:linear-gradient(112deg, rgba(247,229,0,.18) 0 2%, transparent 2% 9%, rgba(247,229,0,.08) 9% 10%, transparent 10% 88%, rgba(0,229,255,.12) 88% 90%, transparent 90%), repeating-linear-gradient(135deg, transparent 0 34px, rgba(247,229,0,.045) 34px 36px, transparent 36px 70px) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-b {
            background:repeating-linear-gradient(0deg, rgba(255,255,255,.035) 0 1px, transparent 1px 4px), repeating-linear-gradient(90deg, transparent 0 78px, rgba(0,229,255,.055) 78px 80px, transparent 80px 156px) !important;
            mix-blend-mode:screen !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-c {
            background:radial-gradient(circle at 50% 50%, rgba(0,229,255,.13) 0 2%, transparent 3% 17%, rgba(247,229,0,.10) 18% 18.5%, transparent 19% 35%, rgba(0,229,255,.06) 36% 36.5%, transparent 37%), conic-gradient(from 35deg at 50% 50%, transparent 0 12%, rgba(247,229,0,.07) 12% 13%, transparent 13% 49%, rgba(0,229,255,.06) 49% 50%, transparent 50%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner {
            width:min(780px,calc(100% - 22px)) !important; padding:24px 42px 22px !important;
            border:0 !important; border-left:7px solid #f2df00 !important; border-right:2px solid #00e5ff !important;
            clip-path:polygon(0 12px,18px 0,78% 0,calc(78% + 14px) 8px,100% 8px,100% calc(100% - 14px),calc(100% - 20px) 100%,15% 100%,calc(15% - 12px) calc(100% - 8px),0 calc(100% - 8px)) !important;
            background:linear-gradient(104deg,rgba(3,5,5,.98),rgba(12,14,13,.96) 42%,rgba(2,12,16,.96)), repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 5px) !important;
            box-shadow:0 24px 58px rgba(0,0,0,.68),-14px 0 34px rgba(242,223,0,.18),14px 0 34px rgba(0,229,255,.13),inset 0 1px rgba(255,255,255,.05) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner::before { content:"" !important; position:absolute !important; left:0 !important; right:0 !important; top:0 !important; height:5px !important; background:linear-gradient(90deg,#f2df00 0 34%,transparent 34% 68%,#00e5ff 68%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-title { color:#f3e800 !important; font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important; font-size:clamp(34px,5.3vw,63px) !important; letter-spacing:1.5px !important; transform:skewX(-6deg) scaleX(.94) !important; text-shadow:3px 3px 0 #020202,6px 6px 0 rgba(0,229,255,.32),0 0 20px rgba(242,223,0,.18) !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-divider { height:3px !important; background:linear-gradient(90deg,transparent,#f2df00 12%,#fff 48%,#00e5ff 82%,transparent) !important; transform:skewX(-18deg) !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-tier { border-radius:0 !important; border-color:#f2df00 !important; color:#f2df00 !important; background:rgba(0,0,0,.66) !important; box-shadow:inset 4px 0 0 #00e5ff !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-source { color:#00e5ff !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-kicker { color:#f2df00 !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-amount { color:#fff !important; text-shadow:2px 2px 0 #101010,4px 4px 0 rgba(242,223,0,.58),0 0 18px rgba(0,229,255,.44) !important; }
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-particle { background:#f2df00 !important; box-shadow:0 0 8px rgba(0,229,255,.8) !important; }

        /* Hellfire Inspired */
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-cinematic { background:radial-gradient(ellipse at 50% 46%,transparent 8%,rgba(38,0,0,.20) 52%,rgba(0,0,0,.88) 100%),linear-gradient(180deg,rgba(0,0,0,.25),transparent 45%,rgba(72,8,0,.42)) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-a { background:radial-gradient(ellipse at 18% 110%,rgba(255,197,44,.82) 0 5%,rgba(255,72,0,.48) 13%,transparent 37%),radial-gradient(ellipse at 52% 115%,rgba(255,229,92,.72) 0 6%,rgba(255,52,0,.44) 15%,transparent 40%),radial-gradient(ellipse at 84% 110%,rgba(255,155,28,.76) 0 5%,rgba(170,0,0,.40) 17%,transparent 39%),linear-gradient(180deg,transparent 48%,rgba(92,0,0,.28)) !important; mix-blend-mode:screen !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-b { background:repeating-conic-gradient(from 18deg at 50% 85%,transparent 0 7deg,rgba(255,85,0,.08) 7deg 8deg,transparent 8deg 17deg),radial-gradient(ellipse at 50% 88%,transparent 0 18%,rgba(255,43,0,.14) 42%,transparent 68%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-c { background:radial-gradient(circle at 15% 25%,rgba(255,255,255,.05),transparent 18%),radial-gradient(circle at 75% 35%,rgba(255,120,60,.08),transparent 22%),repeating-radial-gradient(circle at 40% 55%,rgba(255,255,255,.025) 0 1px,transparent 1px 8px) !important; filter:blur(1px) contrast(130%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner { width:min(760px,calc(100% - 24px)) !important; padding:25px 36px 23px !important; border:1px solid rgba(255,111,23,.62) !important; border-left:6px solid #ff4a0b !important; border-right:6px solid #8e0800 !important; clip-path:polygon(0 14px,18px 0,100% 0,100% calc(100% - 16px),calc(100% - 20px) 100%,0 100%) !important; background:radial-gradient(circle at 50% 110%,rgba(130,18,0,.26),transparent 44%),linear-gradient(108deg,rgba(4,4,4,.98),rgba(27,9,5,.97) 48%,rgba(5,3,3,.98)),repeating-linear-gradient(120deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px) !important; box-shadow:0 24px 60px rgba(0,0,0,.72),0 0 38px rgba(255,53,0,.18),inset 0 -16px 38px rgba(112,5,0,.18) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-title { color:#f4eee1 !important; font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important; font-size:clamp(35px,5.5vw,66px) !important; letter-spacing:1.4px !important; transform:scaleX(.92) !important; text-shadow:2px 2px 0 #170100,5px 5px 0 #7d0b00,0 0 17px rgba(255,79,10,.72),0 0 38px rgba(255,26,0,.28) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-divider { height:3px !important; background:linear-gradient(90deg,transparent,#7d0b00 12%,#ff5c12 36%,#fff3b3 50%,#ff5c12 64%,#7d0b00 88%,transparent) !important; box-shadow:0 0 16px rgba(255,63,0,.55) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-tier { border-radius:2px !important; border-color:#ff5b18 !important; color:#ffb14f !important; background:rgba(37,3,0,.72) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-source { color:#ff6b22 !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-kicker { color:#d8b8a7 !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-amount { color:#ffd76a !important; text-shadow:2px 2px 0 #2c0500,0 0 14px #ff4b00,0 0 30px rgba(255,18,0,.48) !important; }
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-particle { border-radius:999px !important; background:linear-gradient(180deg,#fff2a5,#ff7b18 55%,rgba(170,8,0,0)) !important; box-shadow:0 0 8px #ff8d21,0 0 18px rgba(255,34,0,.75) !important; }

        /* Fallout Inspired — retro-futurist terminal / vault broadcast */
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-cinematic { background:radial-gradient(ellipse at 50% 42%,rgba(122,178,55,.12),rgba(9,18,6,.60) 52%,rgba(0,0,0,.94) 100%),repeating-linear-gradient(0deg,rgba(211,255,132,.027) 0 1px,transparent 1px 4px) !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-fx-a { opacity:.86 !important; background:repeating-linear-gradient(0deg,rgba(201,255,116,.055) 0 1px,transparent 1px 4px),radial-gradient(circle at 50% 50%,transparent 0 20%,rgba(183,233,90,.13) 20.4% 20.8%,transparent 21.2% 34%,rgba(183,233,90,.09) 34.4% 34.8%,transparent 35.2%) !important; animation:mcms-fallout-scan 5.6s linear infinite !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-fx-b { opacity:.78 !important; background:linear-gradient(90deg,rgba(105,151,44,.12),transparent 18%,transparent 82%,rgba(105,151,44,.12)),repeating-radial-gradient(circle at 42% 38%,rgba(255,244,196,.045) 0 1px,transparent 1px 7px) !important; filter:contrast(155%) sepia(28%) !important; animation:mcms-fallout-flicker 3.8s steps(1,end) infinite !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-fx-c { opacity:.72 !important; background:conic-gradient(from 0deg at 50% 50%,rgba(210,242,112,.18) 0 1deg,transparent 1deg 29deg,rgba(210,242,112,.08) 29deg 30deg,transparent 30deg 60deg) !important; mask-image:radial-gradient(circle at center,transparent 0 25%,#000 27% 42%,transparent 65%) !important; -webkit-mask-image:radial-gradient(circle at center,transparent 0 25%,#000 27% 42%,transparent 65%) !important; animation:mcms-fallout-radar 13s linear infinite !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner { width:min(760px,calc(100% - 28px)) !important; padding:31px 38px 25px !important; border:2px solid rgba(193,232,101,.82) !important; border-radius:8px !important; background:linear-gradient(180deg,rgba(18,30,12,.985),rgba(4,10,3,.99)),repeating-linear-gradient(0deg,rgba(197,255,116,.03) 0 1px,transparent 1px 4px) !important; box-shadow:0 0 0 3px rgba(3,7,2,.92),0 0 0 6px rgba(123,158,57,.22),0 0 34px rgba(154,211,69,.28),0 28px 68px rgba(0,0,0,.74),inset 0 0 44px rgba(145,193,66,.10) !important; overflow:hidden !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner::before { content:"VAULT-TEC FINANCIAL TERMINAL // REWARD CLEARANCE" !important; position:absolute !important; left:17px !important; top:11px !important; right:17px !important; color:rgba(214,250,137,.60) !important; font:900 8px/1 "Courier New",Consolas,monospace !important; letter-spacing:1.6px !important; text-align:left !important; border-bottom:1px dashed rgba(176,221,83,.28) !important; padding-bottom:7px !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner::after { content:"ROBCO INDUSTRIES (TM) UNIFIED OPERATING SYSTEM" !important; position:absolute !important; right:15px !important; bottom:8px !important; color:rgba(161,201,84,.40) !important; font:700 6px/1 monospace !important; letter-spacing:1px !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-title { color:#d6ff84 !important; font-family:"Courier New",Consolas,monospace !important; font-size:clamp(28px,4.8vw,56px) !important; font-weight:900 !important; letter-spacing:1.4px !important; transform:none !important; text-shadow:0 0 5px rgba(210,255,128,.95),0 0 15px rgba(151,212,61,.46),2px 0 rgba(113,160,44,.35) !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#6f9134 9%,#d7ff8e 50%,#6f9134 91%,transparent) !important; box-shadow:0 0 11px rgba(175,232,79,.48) !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-tier { border:1px solid #a8d255 !important; color:#dbff91 !important; background:rgba(13,26,8,.88) !important; border-radius:2px !important; font-family:"Courier New",Consolas,monospace !important; letter-spacing:1.2px !important; box-shadow:inset 0 0 9px rgba(153,214,63,.12),0 0 7px rgba(143,197,57,.16) !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-mission,#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-source,#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-kicker,#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-amount { font-family:"Courier New",Consolas,monospace !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-mission { color:#c1e87a !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-source { color:#e1ff9d !important; letter-spacing:.8px !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-kicker { color:#8fb554 !important; letter-spacing:1.4px !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-amount { color:#f0c66c !important; text-shadow:0 0 7px rgba(255,203,93,.88),0 0 24px rgba(178,112,32,.34) !important; }
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-particle { border-radius:50% !important; background:#d7f996 !important; box-shadow:0 0 5px rgba(202,238,123,.82) !important; opacity:.72 !important; }
        @keyframes mcms-fallout-scan { 0% { transform:translateY(-2%) } 100% { transform:translateY(2%) } }
        @keyframes mcms-fallout-radar { from { transform:rotate(0deg) scale(1) } to { transform:rotate(360deg) scale(1.025) } }
        @keyframes mcms-fallout-flicker { 0%,7%,11%,46%,50%,88%,100% { opacity:.78 } 8%,10%,47%,49%,89% { opacity:.42 } }
        /* Galactic Command */
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-cinematic { background:radial-gradient(ellipse at 50% 50%,rgba(20,119,165,.05),rgba(3,11,30,.36) 58%,rgba(0,2,10,.88)),linear-gradient(180deg,rgba(0,8,26,.34),transparent 40%,rgba(0,3,15,.52)) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-a { background-image:radial-gradient(circle at 13% 19%,#fff 0 1px,transparent 1.7px),radial-gradient(circle at 28% 72%,#8adfff 0 1px,transparent 1.8px),radial-gradient(circle at 63% 28%,#fff 0 1px,transparent 1.6px),radial-gradient(circle at 82% 62%,#9ee9ff 0 1.2px,transparent 2px),radial-gradient(circle at 47% 48%,rgba(119,225,255,.6) 0 1px,transparent 2px); background-size:160px 140px,230px 190px,290px 240px,340px 270px,420px 330px !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-b { background:repeating-linear-gradient(90deg,transparent 0 72px,rgba(80,205,255,.055) 72px 73px,transparent 73px 144px),repeating-linear-gradient(0deg,transparent 0 50px,rgba(80,205,255,.045) 50px 51px,transparent 51px 100px),linear-gradient(90deg,transparent 5%,rgba(105,219,255,.18) 5% 5.2%,transparent 5.2% 94.8%,rgba(105,219,255,.18) 94.8% 95%,transparent 95%) !important; mask-image:radial-gradient(ellipse at center,#000 8%,transparent 86%) !important; -webkit-mask-image:radial-gradient(ellipse at center,#000 8%,transparent 86%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-c { background:conic-gradient(from 0deg at 50% 50%,transparent 0 72%,rgba(91,220,255,.24) 74%,rgba(91,220,255,.04) 78%,transparent 82%),radial-gradient(circle at center,transparent 0 27%,rgba(91,220,255,.13) 27.5% 28%,transparent 28.5% 42%,rgba(91,220,255,.08) 42.5% 43%,transparent 43.5%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner { width:min(790px,calc(100% - 24px)) !important; padding:24px 40px 22px !important; border:1px solid rgba(111,221,255,.55) !important; border-left:5px solid #6fddff !important; border-right:5px solid rgba(235,192,79,.70) !important; clip-path:polygon(0 12px,16px 0,85% 0,100% 18px,100% calc(100% - 18px),85% 100%,16px 100%,0 calc(100% - 12px)) !important; background:linear-gradient(100deg,rgba(3,13,31,.94),rgba(8,31,57,.91) 48%,rgba(3,12,30,.95)),repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 5px) !important; box-shadow:0 24px 58px rgba(0,0,0,.65),0 0 32px rgba(74,200,255,.18),inset 0 1px rgba(255,255,255,.06) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-title { color:#f2fbff !important; font-family:"Arial Narrow",Arial,sans-serif !important; font-size:clamp(34px,5.2vw,61px) !important; letter-spacing:3px !important; transform:scaleX(.94) !important; text-shadow:0 0 7px #6fddff,0 0 24px rgba(52,177,255,.36),3px 3px 0 rgba(0,7,22,.94) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#6fddff 18%,#fff 49%,#e8c154 81%,transparent) !important; box-shadow:0 0 11px rgba(98,217,255,.46) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-tier { border-color:#6fddff !important; color:#a9eeff !important; background:rgba(3,18,39,.72) !important; box-shadow:inset 3px 0 0 #e8c154 !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-source { color:#6fddff !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-kicker { color:#e8c154 !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-amount { color:#fff !important; text-shadow:0 0 9px #6fddff,0 0 24px rgba(69,180,255,.34) !important; }
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-particle { border-radius:50% !important; background:#fff !important; box-shadow:0 0 8px #6fddff !important; }

        /* Dark Fantasy Inspired */
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,rgba(122,89,24,.05),rgba(15,11,8,.36) 52%,rgba(0,0,0,.90)),linear-gradient(180deg,rgba(10,8,7,.34),transparent 42%,rgba(27,17,8,.46)) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-a { background:radial-gradient(circle at 50% 52%,rgba(233,192,87,.16) 0 2%,transparent 3% 18%,rgba(233,192,87,.09) 18.5% 19%,transparent 19.5% 31%,rgba(233,192,87,.06) 31.5% 32%,transparent 32.5%),conic-gradient(from 0deg at 50% 52%,transparent 0 14%,rgba(233,192,87,.06) 14% 15%,transparent 15% 38%,rgba(233,192,87,.05) 38% 39%,transparent 39%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-b { background:radial-gradient(ellipse at 18% 82%,rgba(185,122,38,.15),transparent 32%),radial-gradient(ellipse at 82% 18%,rgba(218,184,102,.09),transparent 28%),repeating-radial-gradient(circle at 32% 48%,rgba(255,255,255,.02) 0 1px,transparent 1px 8px) !important; filter:sepia(35%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-c { background:linear-gradient(115deg,transparent 0 15%,rgba(237,199,99,.07) 15% 15.3%,transparent 15.3% 84.7%,rgba(237,199,99,.07) 84.7% 85%,transparent 85%),linear-gradient(180deg,transparent 8%,rgba(237,199,99,.06) 8% 8.3%,transparent 8.3% 91.7%,rgba(237,199,99,.06) 91.7% 92%,transparent 92%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner { width:min(740px,calc(100% - 28px)) !important; padding:27px 40px 24px !important; border:1px solid rgba(216,174,73,.66) !important; border-top:3px double #d8ae49 !important; border-bottom:3px double #d8ae49 !important; background:radial-gradient(circle at 50% 120%,rgba(100,61,12,.22),transparent 44%),linear-gradient(102deg,rgba(7,7,7,.97),rgba(28,24,19,.96) 50%,rgba(6,6,6,.98)),repeating-linear-gradient(35deg,rgba(255,255,255,.018) 0 1px,transparent 1px 8px) !important; box-shadow:0 24px 60px rgba(0,0,0,.72),0 0 30px rgba(203,155,54,.14),inset 0 0 36px rgba(126,91,26,.08) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::before,#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::after { content:"◆" !important; position:absolute !important; top:50% !important; transform:translateY(-50%) !important; color:#d8ae49 !important; font-size:18px !important; text-shadow:0 0 10px rgba(216,174,73,.55) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::before { left:15px !important; } #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::after { right:15px !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title { color:#e8c96f !important; font-family:Georgia,"Times New Roman",serif !important; font-size:clamp(34px,5.2vw,62px) !important; letter-spacing:1px !important; text-transform:none !important; transform:none !important; text-shadow:0 2px 0 #130d05,0 0 10px rgba(229,190,84,.54),0 0 28px rgba(174,116,20,.22) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#7b5b23 12%,#e3bf5c 36%,#fff1ae 50%,#e3bf5c 64%,#7b5b23 88%,transparent) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-tier { border-color:#b9903c !important; color:#e8c96f !important; background:rgba(16,12,8,.72) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-source { color:#e3bf5c !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-kicker { color:#a89569 !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-amount { color:#fff0b1 !important; font-family:Georgia,"Times New Roman",serif !important; text-shadow:0 2px 0 #100a03,0 0 13px rgba(225,181,67,.58) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-particle { border-radius:50% !important; background:#d5c39c !important; box-shadow:0 0 5px rgba(220,183,92,.45) !important; }

        /* Biohazard Containment */
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,transparent 12%,rgba(11,18,20,.28) 55%,rgba(0,0,0,.88)),linear-gradient(180deg,rgba(21,28,30,.26),transparent 48%,rgba(8,13,14,.40)) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-a { background:repeating-linear-gradient(90deg,transparent 0 59px,rgba(218,234,236,.045) 59px 60px,transparent 60px 120px),repeating-linear-gradient(0deg,transparent 0 39px,rgba(218,234,236,.04) 39px 40px,transparent 40px 80px),linear-gradient(90deg,rgba(207,25,35,.12),transparent 28%,transparent 72%,rgba(46,178,112,.08)) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-b { background:repeating-linear-gradient(135deg,rgba(204,20,30,.10) 0 10px,transparent 10px 20px) !important; mask-image:linear-gradient(180deg,#000 0 7%,transparent 7% 90%,#000 90%) !important; -webkit-mask-image:linear-gradient(180deg,#000 0 7%,transparent 7% 90%,#000 90%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-c { background:linear-gradient(180deg,transparent 0 45%,rgba(83,255,164,.12) 49%,rgba(83,255,164,.22) 50%,rgba(83,255,164,.08) 51%,transparent 55%),radial-gradient(circle at 50% 50%,transparent 0 25%,rgba(235,245,246,.07) 25.5% 26%,transparent 26.5%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner { width:min(790px,calc(100% - 24px)) !important; padding:24px 38px 22px !important; border:1px solid rgba(221,234,235,.38) !important; border-left:8px solid #c81724 !important; border-right:3px solid #43d887 !important; background:linear-gradient(104deg,rgba(8,12,13,.98),rgba(25,32,34,.96) 48%,rgba(7,12,13,.98)),repeating-linear-gradient(0deg,rgba(255,255,255,.02) 0 1px,transparent 1px 5px) !important; clip-path:polygon(0 0,96% 0,100% 14px,100% 100%,4% 100%,0 calc(100% - 14px)) !important; box-shadow:0 24px 58px rgba(0,0,0,.68),-12px 0 30px rgba(200,23,36,.16),12px 0 24px rgba(67,216,135,.10),inset 0 1px rgba(255,255,255,.05) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before { content:"CONTAINMENT PROTOCOL // SECURE" !important; position:absolute !important; right:18px !important; top:10px !important; color:rgba(87,229,150,.58) !important; font:900 7px/1 monospace !important; letter-spacing:1.4px !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title { color:#f0f5f5 !important; font-family:"Arial Narrow",Arial,sans-serif !important; font-size:clamp(33px,5vw,59px) !important; letter-spacing:2.7px !important; transform:scaleX(.96) !important; text-shadow:3px 3px 0 #101415,6px 6px 0 rgba(200,23,36,.50),0 0 18px rgba(255,255,255,.10) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#c81724 16%,#f0f5f5 49%,#43d887 82%,transparent) !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-tier { border-radius:0 !important; border-color:#c81724 !important; color:#f3f6f6 !important; background:rgba(30,5,8,.64) !important; box-shadow:inset 4px 0 0 #43d887 !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-source { color:#43d887 !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-kicker { color:#d65b63 !important; }
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-amount { color:#fff !important; text-shadow:0 0 10px rgba(67,216,135,.62),3px 3px 0 rgba(200,23,36,.55) !important; }

        /* Underworld Inspired */
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,rgba(113,11,15,.06),rgba(17,4,7,.42) 56%,rgba(0,0,0,.91)),linear-gradient(180deg,rgba(45,0,5,.28),transparent 42%,rgba(50,5,0,.34)) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-a { background:radial-gradient(ellipse at 22% 110%,rgba(233,46,18,.35),transparent 38%),radial-gradient(ellipse at 78% 110%,rgba(190,13,20,.32),transparent 36%),radial-gradient(circle at 50% 50%,transparent 0 26%,rgba(226,181,63,.08) 26.5% 27%,transparent 27.5%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-b { background:repeating-linear-gradient(90deg,transparent 0 44px,rgba(224,181,68,.07) 44px 47px,transparent 47px 88px),repeating-linear-gradient(0deg,transparent 0 44px,rgba(224,181,68,.045) 44px 47px,transparent 47px 88px) !important; mask-image:linear-gradient(90deg,#000 0 12%,transparent 12% 88%,#000 88%) !important; -webkit-mask-image:linear-gradient(90deg,#000 0 12%,transparent 12% 88%,#000 88%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-c { background:conic-gradient(from 25deg at 50% 50%,transparent 0 15%,rgba(222,173,55,.08) 15% 16%,transparent 16% 33%,rgba(170,13,21,.10) 33% 34%,transparent 34%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner { width:min(740px,calc(100% - 28px)) !important; padding:27px 40px 24px !important; border:1px solid rgba(221,174,57,.58) !important; border-top:4px solid #b3131d !important; border-bottom:4px solid #d9ad3b !important; background:radial-gradient(circle at 50% 120%,rgba(126,10,12,.24),transparent 42%),linear-gradient(105deg,rgba(5,4,5,.98),rgba(31,9,12,.96) 48%,rgba(5,4,5,.98)),repeating-linear-gradient(35deg,rgba(255,255,255,.018) 0 1px,transparent 1px 8px) !important; box-shadow:0 24px 60px rgba(0,0,0,.72),0 0 32px rgba(185,20,27,.18),inset 0 0 32px rgba(213,168,51,.06) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::before,#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::after { content:"◆" !important; position:absolute !important; top:50% !important; transform:translateY(-50%) rotate(45deg) !important; color:#d9ad3b !important; font-size:14px !important; } #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::before { left:18px !important; } #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::after { right:18px !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title { color:#f4e9d6 !important; font-family:Georgia,"Times New Roman",serif !important; font-size:clamp(35px,5.4vw,64px) !important; text-transform:none !important; letter-spacing:.5px !important; transform:none !important; text-shadow:0 2px 0 #160306,0 0 10px rgba(217,173,59,.55),4px 4px 0 rgba(151,12,20,.48) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-divider { height:3px !important; background:linear-gradient(90deg,transparent,#8d1118 12%,#d9ad3b 36%,#fff0b0 50%,#d9ad3b 64%,#8d1118 88%,transparent) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-tier { border-color:#b3131d !important; color:#e8bf55 !important; background:rgba(35,3,7,.68) !important; box-shadow:inset 4px 0 0 #d9ad3b !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-source { color:#e4b94c !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-kicker { color:#bd7b80 !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-amount { color:#ffe08a !important; font-family:Georgia,"Times New Roman",serif !important; text-shadow:0 2px 0 #190307,0 0 13px rgba(218,169,48,.62),0 0 25px rgba(162,8,16,.30) !important; }
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-particle { border-radius:50% !important; background:#ffd96d !important; box-shadow:0 0 7px #e15e25,0 0 16px rgba(180,10,18,.62) !important; }

        /* Pixel Arcade Inspired */
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,rgba(78,31,143,.08),rgba(8,5,21,.38) 55%,rgba(0,0,0,.89)),repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 4px) !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-a { background:repeating-linear-gradient(90deg,rgba(109,62,220,.06) 0 8px,transparent 8px 16px),repeating-linear-gradient(0deg,rgba(33,222,196,.05) 0 8px,transparent 8px 16px) !important; image-rendering:pixelated !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-b { background:radial-gradient(circle at 18% 28%,#ffdc4a 0 3px,transparent 4px),radial-gradient(circle at 82% 34%,#4af7df 0 3px,transparent 4px),radial-gradient(circle at 32% 76%,#ff5ea9 0 3px,transparent 4px),radial-gradient(circle at 68% 72%,#8b6cff 0 3px,transparent 4px); background-size:120px 100px,170px 140px,210px 180px,250px 220px !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-c { background:linear-gradient(90deg,transparent 0 8%,rgba(255,255,255,.06) 8% 8.5%,transparent 8.5% 91.5%,rgba(255,255,255,.06) 91.5% 92%,transparent 92%),linear-gradient(180deg,transparent 0 12%,rgba(255,255,255,.05) 12% 12.5%,transparent 12.5% 87.5%,rgba(255,255,255,.05) 87.5% 88%,transparent 88%) !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner { width:min(700px,calc(100% - 24px)) !important; padding:24px 34px 22px !important; border:4px solid #ecebff !important; border-radius:0 !important; clip-path:polygon(0 10px,10px 10px,10px 0,calc(100% - 10px) 0,calc(100% - 10px) 10px,100% 10px,100% calc(100% - 10px),calc(100% - 10px) calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,10px calc(100% - 10px),0 calc(100% - 10px)) !important; background:linear-gradient(180deg,rgba(20,10,45,.98),rgba(7,5,21,.98)),repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 8px,transparent 8px 16px) !important; box-shadow:8px 8px 0 #5f3aca,-8px -8px 0 #22d8c3,0 24px 50px rgba(0,0,0,.64) !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-title { color:#fff36a !important; font-family:"Courier New",Consolas,monospace !important; font-size:clamp(29px,4.5vw,52px) !important; letter-spacing:1px !important; transform:none !important; text-shadow:4px 0 0 #ff5aaa,0 4px 0 #25dfcb,4px 4px 0 #38206f !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-divider { height:4px !important; background:repeating-linear-gradient(90deg,#ff5aaa 0 12px,#fff36a 12px 24px,#25dfcb 24px 36px,#8b6cff 36px 48px) !important; box-shadow:none !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-tier { border-radius:0 !important; border:2px solid #25dfcb !important; color:#fff36a !important; background:#12092c !important; font-family:monospace !important; box-shadow:3px 3px 0 #5f3aca !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-mission,#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-source,#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-kicker,#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-amount { font-family:"Courier New",Consolas,monospace !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-source { color:#25dfcb !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-kicker { color:#ff79b8 !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-amount { color:#fff !important; text-shadow:3px 0 0 #ff5aaa,0 3px 0 #25dfcb,3px 3px 0 #4d2da5 !important; }
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-particle { background:#fff36a !important; box-shadow:4px 4px 0 #ff5aaa !important; image-rendering:pixelated !important; }


        /* v3.1.8 cinematic theme remaster: CSS-only artwork to preserve performance. */
        #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner {
            isolation:isolate !important;
            overflow:hidden !important;
        }
        #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner > * {
            position:relative !important;
            z-index:3 !important;
        }

        /* GTA V — black-and-gold heist completion card with angular city-map geometry. */
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-cinematic {
            background:radial-gradient(circle at 50% 48%,transparent 0 16%,rgba(0,0,0,.35) 55%,rgba(0,0,0,.92) 100%),linear-gradient(135deg,rgba(12,28,21,.30),transparent 42%,rgba(70,53,9,.18)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-theme-fx-a {
            background:linear-gradient(26deg,transparent 0 46%,rgba(255,210,72,.10) 46% 46.4%,transparent 46.4%),linear-gradient(154deg,transparent 0 54%,rgba(255,255,255,.055) 54% 54.35%,transparent 54.35%),repeating-linear-gradient(90deg,transparent 0 119px,rgba(255,255,255,.028) 120px,transparent 121px) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-theme-fx-b {
            background:radial-gradient(circle at 12% 16%,rgba(229,190,64,.24),transparent 20%),radial-gradient(circle at 88% 82%,rgba(22,111,72,.22),transparent 26%),linear-gradient(90deg,transparent 8%,rgba(255,255,255,.035) 8% 8.2%,transparent 8.2% 92%,rgba(255,255,255,.035) 92% 92.2%,transparent 92.2%) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-theme-fx-c {
            background:repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 4px),linear-gradient(90deg,rgba(0,0,0,.30),transparent 20%,transparent 80%,rgba(0,0,0,.30)) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner {
            width:min(770px,calc(100% - 26px)) !important;padding:27px 42px 24px !important;border-radius:2px !important;
            border:1px solid rgba(245,211,102,.62) !important;border-left:8px solid #d3a928 !important;border-right:3px solid #2d6c4e !important;
            clip-path:polygon(0 0,96% 0,100% 16px,100% 100%,4% 100%,0 calc(100% - 16px)) !important;
            background:linear-gradient(112deg,rgba(5,8,7,.985),rgba(17,23,19,.97) 48%,rgba(6,8,7,.985)),repeating-linear-gradient(135deg,rgba(255,255,255,.025) 0 1px,transparent 1px 9px) !important;
            box-shadow:0 28px 70px rgba(0,0,0,.78),0 0 36px rgba(217,177,49,.16),inset 0 1px rgba(255,255,255,.06),inset 0 -22px 45px rgba(11,64,43,.12) !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner::before {content:"LOS SANTOS // SCORE SETTLED" !important;position:absolute !important;top:11px !important;right:18px !important;color:rgba(234,204,100,.58) !important;font:900 7px/1.1 monospace !important;letter-spacing:1.8px !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:linear-gradient(122deg,transparent 0 68%,rgba(230,193,72,.075) 68% 69%,transparent 69% 73%,rgba(52,130,91,.07) 73% 74%,transparent 74%) !important;z-index:1 !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-title {color:#f4efe1 !important;font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important;font-size:clamp(36px,5.6vw,68px) !important;letter-spacing:1.5px !important;transform:skewX(-5deg) scaleX(.93) !important;text-shadow:3px 3px 0 #111,6px 6px 0 rgba(185,143,24,.48),0 0 20px rgba(255,219,90,.18) !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-divider {height:3px !important;background:linear-gradient(90deg,transparent,#d9ac2f 10%,#f7e2a0 48%,#2b8d66 88%,transparent) !important;transform:skewX(-15deg) !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-tier {border-radius:1px !important;border-color:#d3a928 !important;color:#f3d873 !important;background:rgba(8,12,10,.78) !important;box-shadow:inset 4px 0 0 #2d7957 !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-source {color:#77d7a8 !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-kicker {color:#e1ba45 !important;}
        #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-amount {color:#fff7d8 !important;text-shadow:2px 2px 0 #0a0a0a,4px 4px 0 rgba(181,139,26,.58),0 0 18px rgba(239,208,83,.24) !important;}

        /* Vice City — neon sunset, chrome script and ocean-grid atmosphere. */
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 50% 13%,rgba(255,188,75,.22),transparent 20%),linear-gradient(180deg,rgba(255,62,168,.10),transparent 45%),repeating-linear-gradient(90deg,transparent 0 109px,rgba(48,245,238,.038) 110px,transparent 111px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-theme-fx-b {background:linear-gradient(116deg,transparent 0 20%,rgba(255,83,183,.08) 20% 21%,transparent 21% 79%,rgba(34,239,233,.08) 79% 80%,transparent 80%),radial-gradient(ellipse at 50% 120%,rgba(48,233,221,.15),transparent 48%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner {box-shadow:0 28px 74px rgba(0,0,0,.72),-16px 0 42px rgba(255,47,161,.22),16px 0 42px rgba(0,229,222,.20),inset 0 1px rgba(255,255,255,.12) !important;}
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::before {content:"VICE CITY // CASHOUT" !important;position:absolute !important;top:10px !important;left:18px !important;color:rgba(71,242,231,.68) !important;font:900 7px/1 monospace !important;letter-spacing:1.7px !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-amount {filter:drop-shadow(0 0 8px rgba(41,245,234,.35)) !important;}

        /* Bad Company — battlefield extraction HUD with dust, range marks and hazard framing. */
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-theme-fx-a {background:linear-gradient(90deg,rgba(0,0,0,.36),transparent 18%,transparent 82%,rgba(0,0,0,.36)),repeating-linear-gradient(0deg,transparent 0 38px,rgba(244,214,123,.035) 39px,transparent 40px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-theme-fx-b {background:radial-gradient(circle at 10% 78%,rgba(248,145,37,.16),transparent 25%),radial-gradient(circle at 88% 22%,rgba(168,195,146,.12),transparent 23%),linear-gradient(135deg,transparent 49.6%,rgba(255,210,109,.10) 49.8% 50.2%,transparent 50.4%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {border-top-color:rgba(247,206,112,.76) !important;border-bottom-color:rgba(121,145,103,.72) !important;box-shadow:0 28px 70px rgba(0,0,0,.78),0 0 38px rgba(230,151,54,.16),inset 0 0 40px rgba(112,94,48,.08) !important;}
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::before {content:"FIELD OPS // PAYMENT EXTRACTED" !important;position:absolute !important;top:10px !important;right:18px !important;color:rgba(242,210,132,.60) !important;font:900 7px/1 monospace !important;letter-spacing:1.5px !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:linear-gradient(90deg,transparent 0 7%,rgba(255,211,113,.06) 7% 7.3%,transparent 7.3% 92.7%,rgba(255,211,113,.06) 92.7% 93%,transparent 93%),repeating-linear-gradient(135deg,rgba(255,199,84,.035) 0 4px,transparent 4px 12px) !important;z-index:1 !important;}

        /* Scarface — sharper Art-Deco palace card, marble contrast and blood-red power line. */
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-c {background:linear-gradient(90deg,rgba(255,255,255,.035),transparent 15%,transparent 85%,rgba(255,255,255,.035)),repeating-linear-gradient(45deg,transparent 0 72px,rgba(212,175,55,.035) 73px,transparent 74px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {box-shadow:0 30px 78px rgba(0,0,0,.80),-14px 0 36px rgba(147,0,18,.20),14px 0 34px rgba(211,175,55,.14),inset 0 0 34px rgba(255,255,255,.035) !important;}
        #${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::before {content:"MIAMI // EMPIRE ACCOUNT" !important;position:absolute !important;top:10px !important;left:18px !important;color:rgba(215,178,62,.68) !important;font:900 7px/1 serif !important;letter-spacing:2px !important;z-index:2 !important;}

        /* Cyberpunk — layered megacorp UI, warning rails, chromatic offset and data noise. */
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 50%,transparent 0 12%,rgba(0,0,0,.26) 58%,rgba(0,0,0,.88) 100%),linear-gradient(120deg,rgba(242,223,0,.07),transparent 36%,rgba(0,229,255,.075)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-a {background:repeating-linear-gradient(0deg,rgba(0,229,255,.035) 0 1px,transparent 1px 5px),linear-gradient(90deg,transparent 0 9%,rgba(242,223,0,.10) 9% 9.5%,transparent 9.5% 90.5%,rgba(0,229,255,.10) 90.5% 91%,transparent 91%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-b {background:linear-gradient(135deg,transparent 0 46%,rgba(242,223,0,.08) 46% 46.4%,transparent 46.4% 52%,rgba(0,229,255,.08) 52% 52.4%,transparent 52.4%),repeating-linear-gradient(90deg,transparent 0 137px,rgba(255,255,255,.028) 138px,transparent 139px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-c {background:radial-gradient(circle at 18% 25%,rgba(242,223,0,.12),transparent 20%),radial-gradient(circle at 82% 78%,rgba(0,229,255,.13),transparent 23%),linear-gradient(90deg,rgba(0,0,0,.25),transparent 18%,transparent 82%,rgba(0,0,0,.25)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner {width:min(800px,calc(100% - 24px)) !important;padding:28px 42px 24px !important;border:1px solid rgba(242,223,0,.68) !important;border-left:9px solid #f2df00 !important;border-right:4px solid #00e5ff !important;clip-path:polygon(0 0,94% 0,100% 18px,100% 100%,6% 100%,0 calc(100% - 18px)) !important;background:linear-gradient(108deg,rgba(4,5,7,.985),rgba(18,20,23,.97) 52%,rgba(4,6,8,.985)),repeating-linear-gradient(0deg,rgba(255,255,255,.02) 0 1px,transparent 1px 5px) !important;box-shadow:0 30px 74px rgba(0,0,0,.78),-16px 0 38px rgba(242,223,0,.14),16px 0 38px rgba(0,229,255,.15),inset 0 0 34px rgba(0,229,255,.04) !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner::before {content:"ARASAKA FINANCIAL NODE // VERIFIED" !important;position:absolute !important;top:10px !important;right:18px !important;height:auto !important;background:none !important;color:rgba(0,229,255,.68) !important;font:900 7px/1 monospace !important;letter-spacing:1.6px !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:linear-gradient(90deg,transparent 0 31%,rgba(242,223,0,.055) 31% 31.4%,transparent 31.4% 67%,rgba(0,229,255,.055) 67% 67.4%,transparent 67.4%) !important;z-index:1 !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-title {font-size:clamp(36px,5.7vw,70px) !important;letter-spacing:1.8px !important;text-shadow:3px 3px 0 #020202,6px 5px 0 rgba(0,229,255,.30),-2px -1px 0 rgba(255,36,116,.32),0 0 22px rgba(242,223,0,.20) !important;}
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-tier {box-shadow:inset 5px 0 0 #00e5ff,3px 3px 0 rgba(255,38,118,.28) !important;}

        /* Hellfire — infernal altar, molten seams and ember-lit reward seal. */
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-a {background:radial-gradient(ellipse at 14% 112%,rgba(255,222,92,.88) 0 4%,rgba(255,74,0,.50) 13%,transparent 35%),radial-gradient(ellipse at 50% 118%,rgba(255,237,118,.78) 0 5%,rgba(255,48,0,.48) 16%,transparent 41%),radial-gradient(ellipse at 87% 112%,rgba(255,166,36,.84) 0 4%,rgba(150,0,0,.43) 18%,transparent 38%),linear-gradient(180deg,transparent 46%,rgba(96,0,0,.32)) !important;mix-blend-mode:screen !important;}
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-b {background:repeating-conic-gradient(from 0deg at 50% 86%,transparent 0 8deg,rgba(255,96,0,.075) 8deg 9deg,transparent 9deg 18deg),radial-gradient(ellipse at 50% 91%,transparent 0 16%,rgba(255,48,0,.17) 38%,transparent 66%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner {border-top:3px solid #ffad26 !important;border-bottom:3px solid #760000 !important;box-shadow:0 30px 76px rgba(0,0,0,.80),0 0 44px rgba(255,48,0,.23),inset 0 -24px 48px rgba(122,4,0,.20),inset 0 1px rgba(255,232,173,.10) !important;}
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner::before {content:"INFERNAL TREASURY // SEAL BROKEN" !important;position:absolute !important;top:10px !important;right:18px !important;color:rgba(255,176,62,.67) !important;font:900 7px/1 serif !important;letter-spacing:1.7px !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:radial-gradient(circle at 50% 125%,rgba(255,82,0,.16),transparent 46%),linear-gradient(118deg,transparent 0 48%,rgba(255,134,24,.055) 48% 49%,transparent 49%) !important;z-index:1 !important;}
        #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-title {text-shadow:2px 2px 0 #170100,5px 5px 0 #7d0b00,0 0 20px rgba(255,91,13,.82),0 0 48px rgba(255,30,0,.30) !important;}

        /* Galactic Command — deep-space fleet HUD, orbital rings and command telemetry. */
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 45%,transparent 0 12%,rgba(2,7,23,.30) 58%,rgba(0,2,10,.94) 100%),linear-gradient(135deg,rgba(42,98,255,.08),transparent 42%,rgba(146,74,255,.08)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 50% 50%,transparent 0 18%,rgba(82,149,255,.11) 18.5% 19%,transparent 19.5% 31%,rgba(153,99,255,.075) 31.5% 32%,transparent 32.5%),repeating-conic-gradient(from 0deg at 50% 50%,transparent 0 18deg,rgba(88,157,255,.045) 18deg 18.5deg,transparent 18.5deg 36deg) !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-b {background:radial-gradient(circle at 15% 22%,#fff 0 1px,transparent 2px),radial-gradient(circle at 78% 17%,#8fc3ff 0 1px,transparent 2px),radial-gradient(circle at 85% 74%,#c69cff 0 1px,transparent 2px),radial-gradient(circle at 28% 80%,#fff 0 1px,transparent 2px);background-size:170px 130px,220px 180px,280px 230px,320px 260px !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-c {background:linear-gradient(90deg,transparent 0 8%,rgba(102,169,255,.06) 8% 8.2%,transparent 8.2% 91.8%,rgba(102,169,255,.06) 91.8% 92%,transparent 92%),linear-gradient(180deg,transparent 0 13%,rgba(185,135,255,.05) 13% 13.2%,transparent 13.2% 86.8%,rgba(185,135,255,.05) 86.8% 87%,transparent 87%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner {width:min(790px,calc(100% - 24px)) !important;padding:28px 42px 24px !important;border:1px solid rgba(113,178,255,.60) !important;border-left:6px solid #5ca8ff !important;border-right:6px solid #9c6cff !important;clip-path:polygon(0 14px,14px 0,calc(100% - 14px) 0,100% 14px,100% calc(100% - 14px),calc(100% - 14px) 100%,14px 100%,0 calc(100% - 14px)) !important;background:linear-gradient(110deg,rgba(3,8,22,.985),rgba(12,22,45,.97) 50%,rgba(4,7,20,.985)),repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 5px) !important;box-shadow:0 30px 76px rgba(0,0,0,.80),-14px 0 36px rgba(72,149,255,.18),14px 0 36px rgba(151,92,255,.17),inset 0 0 38px rgba(88,155,255,.05) !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner::before {content:"FLEET COMMAND // TREASURY UPLINK" !important;position:absolute !important;top:10px !important;right:18px !important;color:rgba(137,194,255,.70) !important;font:900 7px/1 monospace !important;letter-spacing:1.6px !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-title {color:#ecf5ff !important;font-family:Eurostile,"Arial Narrow",Arial,sans-serif !important;font-size:clamp(34px,5.2vw,64px) !important;letter-spacing:2.3px !important;transform:scaleX(.95) !important;text-shadow:0 0 4px #fff,0 0 18px rgba(90,166,255,.66),4px 4px 0 rgba(101,72,189,.34) !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-divider {height:2px !important;background:linear-gradient(90deg,transparent,#5ca8ff 9%,#eef7ff 50%,#9e6fff 91%,transparent) !important;box-shadow:0 0 12px rgba(96,167,255,.42) !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-tier {border-radius:2px !important;border-color:#66b2ff !important;color:#b9dcff !important;background:rgba(4,12,30,.74) !important;box-shadow:inset 4px 0 0 #9e6fff !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-source {color:#aa8fff !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-kicker {color:#79c8ff !important;}
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-amount {color:#fff !important;text-shadow:0 0 9px rgba(111,188,255,.65),3px 3px 0 rgba(79,55,151,.45) !important;}

        /* Dark Fantasy — illuminated manuscript, royal seal and ancient-gold ornament. */
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 46%,transparent 0 13%,rgba(13,7,16,.32) 56%,rgba(2,1,4,.94) 100%),linear-gradient(135deg,rgba(99,57,22,.08),transparent 40%,rgba(53,19,75,.09)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 15% 18%,rgba(214,172,74,.12),transparent 18%),radial-gradient(circle at 83% 76%,rgba(116,52,137,.12),transparent 22%),repeating-radial-gradient(circle at 50% 50%,transparent 0 54px,rgba(220,177,77,.028) 55px,transparent 56px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-b {background:linear-gradient(45deg,transparent 0 49.6%,rgba(219,176,72,.055) 49.8% 50.2%,transparent 50.4%),linear-gradient(135deg,transparent 0 49.6%,rgba(117,66,133,.055) 49.8% 50.2%,transparent 50.4%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner {width:min(750px,calc(100% - 28px)) !important;padding:31px 46px 27px !important;border:2px solid #9f7a2d !important;border-top:5px solid #d6ad4d !important;border-bottom:5px solid #4b203f !important;background:radial-gradient(circle at 50% 118%,rgba(82,29,71,.21),transparent 44%),linear-gradient(110deg,rgba(9,6,8,.985),rgba(27,16,26,.97) 50%,rgba(8,6,8,.985)),repeating-linear-gradient(45deg,rgba(255,255,255,.018) 0 1px,transparent 1px 9px) !important;box-shadow:0 32px 80px rgba(0,0,0,.82),0 0 36px rgba(213,169,67,.16),inset 0 0 48px rgba(92,44,91,.12) !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::before {content:"✦" !important;left:17px !important;font-size:22px !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::after {content:"✦" !important;right:17px !important;font-size:22px !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title {color:#f1e2b7 !important;font-family:Georgia,"Times New Roman",serif !important;font-size:clamp(33px,5vw,61px) !important;font-weight:900 !important;letter-spacing:.8px !important;text-shadow:2px 2px 0 #140c12,0 0 15px rgba(215,174,75,.36),4px 4px 0 rgba(72,32,68,.58) !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-divider {height:3px !important;background:linear-gradient(90deg,transparent,#8a6524 10%,#e3c56f 46%,#8e4f7b 88%,transparent) !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-tier {border:1px solid #c99f42 !important;color:#e6c96e !important;background:rgba(20,10,18,.72) !important;font-family:Georgia,serif !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-source {color:#c48daf !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-kicker {color:#d9b75d !important;}
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-amount {color:#fff4cf !important;font-family:Georgia,serif !important;text-shadow:0 0 12px rgba(220,177,72,.42),3px 3px 0 #291426 !important;}

        /* Biohazard — sterile blacksite containment console with warning stripes and diagnostic grid. */
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 48%,transparent 0 13%,rgba(3,12,10,.31) 58%,rgba(0,3,3,.94) 100%),linear-gradient(120deg,rgba(28,199,107,.07),transparent 40%,rgba(207,28,42,.075)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-a {background:repeating-linear-gradient(0deg,rgba(91,235,158,.025) 0 1px,transparent 1px 5px),linear-gradient(90deg,transparent 0 12%,rgba(85,230,150,.07) 12% 12.3%,transparent 12.3% 87.7%,rgba(205,36,48,.07) 87.7% 88%,transparent 88%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-b {background:repeating-conic-gradient(from 0deg at 50% 50%,transparent 0 29deg,rgba(85,229,151,.035) 29deg 30deg,transparent 30deg 59deg,rgba(206,32,45,.03) 59deg 60deg),radial-gradient(circle at 50% 50%,transparent 0 18%,rgba(72,224,146,.065) 18.5% 19%,transparent 19.5% 31%,rgba(209,33,45,.05) 31.5% 32%,transparent 32.5%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-c {background:linear-gradient(135deg,transparent 0 48%,rgba(208,35,47,.055) 48% 48.5%,transparent 48.5% 51.5%,rgba(74,225,148,.055) 51.5% 52%,transparent 52%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner {border-top:3px solid #dfe9e9 !important;border-bottom:3px solid #243f37 !important;box-shadow:0 30px 76px rgba(0,0,0,.80),-15px 0 38px rgba(200,23,36,.18),15px 0 38px rgba(67,216,135,.14),inset 0 0 40px rgba(80,220,148,.035) !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before {content:"BSL-4 CLEARANCE // COMPENSATION AUTHORIZED" !important;color:rgba(88,231,152,.66) !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:repeating-linear-gradient(135deg,transparent 0 18px,rgba(201,24,36,.045) 18px 22px,transparent 22px 40px),linear-gradient(90deg,transparent 0 73%,rgba(79,225,149,.04) 73% 74%,transparent 74%) !important;z-index:1 !important;}
        #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title {text-shadow:2px 2px 0 #080a0a,5px 5px 0 rgba(190,26,38,.34),0 0 18px rgba(74,222,146,.28) !important;}

        /* Underworld — aristocratic nocturne, crimson velvet, silver moonlight and gold sigils. */
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 44%,transparent 0 13%,rgba(16,3,8,.34) 58%,rgba(1,1,3,.95) 100%),linear-gradient(135deg,rgba(157,20,31,.07),transparent 42%,rgba(194,166,93,.06)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 18% 20%,rgba(223,224,239,.10),transparent 18%),radial-gradient(circle at 82% 75%,rgba(156,14,29,.13),transparent 23%),repeating-radial-gradient(circle at 50% 50%,transparent 0 62px,rgba(214,172,69,.025) 63px,transparent 64px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-b {background:linear-gradient(45deg,transparent 0 49.7%,rgba(219,176,73,.045) 49.8% 50.2%,transparent 50.3%),linear-gradient(135deg,transparent 0 49.7%,rgba(173,25,39,.05) 49.8% 50.2%,transparent 50.3%) !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner {padding:30px 44px 26px !important;border:1px solid rgba(222,184,85,.68) !important;border-top:5px solid #a51320 !important;border-bottom:5px solid #d9ad3b !important;background:radial-gradient(circle at 50% 120%,rgba(130,9,16,.26),transparent 44%),linear-gradient(106deg,rgba(4,4,6,.99),rgba(29,7,13,.97) 49%,rgba(4,4,6,.99)),repeating-linear-gradient(35deg,rgba(255,255,255,.018) 0 1px,transparent 1px 8px) !important;box-shadow:0 32px 80px rgba(0,0,0,.84),0 0 40px rgba(173,18,29,.20),inset 0 0 40px rgba(213,168,51,.075) !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::before {content:"✦" !important;left:18px !important;transform:translateY(-50%) !important;font-size:19px !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::after {content:"✦" !important;right:18px !important;transform:translateY(-50%) !important;font-size:19px !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title {color:#f2e7d0 !important;font-family:Georgia,"Times New Roman",serif !important;font-size:clamp(34px,5.2vw,63px) !important;font-weight:900 !important;text-shadow:2px 2px 0 #170309,0 0 16px rgba(213,171,65,.36),4px 4px 0 rgba(108,9,20,.56) !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-divider {height:3px !important;background:linear-gradient(90deg,transparent,#9c1420 10%,#e0bd63 50%,#9c1420 90%,transparent) !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-tier {border:1px solid #c99d39 !important;color:#e2c366 !important;background:rgba(17,4,9,.76) !important;font-family:Georgia,serif !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-source {color:#d7d8e6 !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-kicker {color:#d1a43e !important;}
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-amount {color:#fff0c8 !important;font-family:Georgia,serif !important;text-shadow:0 0 12px rgba(218,174,67,.42),3px 3px 0 #4e0812 !important;}

        /* Pixel Arcade — premium cabinet bezel, CRT raster, score rails and true 8-bit geometry. */
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 48%,transparent 0 13%,rgba(15,5,36,.30) 58%,rgba(3,2,10,.94) 100%),linear-gradient(135deg,rgba(255,84,166,.08),transparent 42%,rgba(38,224,204,.08)) !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-a {background:repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 4px),repeating-linear-gradient(90deg,transparent 0 31px,rgba(139,108,255,.035) 32px,transparent 33px) !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-b {background:radial-gradient(circle at 10% 18%,#fff36a 0 2px,transparent 3px),radial-gradient(circle at 90% 22%,#25dfcb 0 2px,transparent 3px),radial-gradient(circle at 20% 82%,#ff5aaa 0 2px,transparent 3px),radial-gradient(circle at 80% 78%,#8b6cff 0 2px,transparent 3px);background-size:110px 90px,150px 120px,190px 150px,230px 190px !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner {padding:28px 38px 24px !important;border:4px solid #f4f1ff !important;box-shadow:9px 9px 0 #5f3aca,-9px -9px 0 #22d8c3,0 30px 70px rgba(0,0,0,.76),inset 0 0 0 4px #160a38 !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner::before {content:"PLAYER 1 // CREDIT BANK" !important;position:absolute !important;top:10px !important;left:18px !important;color:#25dfcb !important;font:900 8px/1 "Courier New",monospace !important;letter-spacing:1.2px !important;text-shadow:2px 2px 0 #3c287d !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner::after {content:"HI-SCORE" !important;position:absolute !important;top:10px !important;right:18px !important;color:#fff36a !important;font:900 8px/1 "Courier New",monospace !important;letter-spacing:1.2px !important;text-shadow:2px 2px 0 #ff5aaa !important;z-index:2 !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-title {font-size:clamp(31px,4.8vw,56px) !important;text-shadow:4px 0 0 #ff5aaa,0 4px 0 #25dfcb,4px 4px 0 #38206f,0 0 12px rgba(255,243,106,.18) !important;}
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-amount {text-shadow:3px 0 0 #ff5aaa,0 3px 0 #25dfcb,3px 3px 0 #4d2da5,0 0 10px rgba(255,255,255,.22) !important;}

        @media (max-width:620px) {
            #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner::before,
            #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner::after {font-size:6px !important;letter-spacing:.8px !important;}
            #${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner {padding-left:18px !important;padding-right:18px !important;}
        }

        /* Shared title fitting for every template. */
        #${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-long { font-size:clamp(28px,4.35vw,51px) !important; letter-spacing:.6px !important; transform:scaleX(.90) !important; }
        #${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(23px,3.55vw,42px) !important; line-height:.95 !important; white-space:normal !important; text-wrap:balance !important; transform:scaleX(.92) !important; }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-long { font-size:clamp(34px,5.5vw,62px) !important; transform:rotate(-2deg) skewX(-5deg) scaleX(.92) !important; }
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(29px,4.6vw,52px) !important; line-height:.93 !important; transform:rotate(-1deg) skewX(-4deg) scaleX(.94) !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-long,
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-long { transform:none !important; }
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-very-long,
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-very-long { transform:none !important; }
        @media (max-width:620px) {
            #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner,
            #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner { width:calc(100% - 14px) !important; padding:21px 16px 19px !important; }
        }

        @keyframes mcmsPayoutRed {
            0%, 8%, 38%, 58%, 88%, 100% { opacity: 0; transform: scale(1); }
            14%, 28%, 64%, 80% { opacity: .82; transform: scale(1.025); }
        }
        @keyframes mcmsPayoutBlue {
            0%, 28%, 48%, 78%, 100% { opacity: 0; transform: scale(1); }
            34%, 44%, 54%, 72%, 84%, 94% { opacity: .86; transform: scale(1.025); }
        }
        @keyframes mcmsPayoutBanner {
            0% { opacity: 0; transform: translate(-50%, -44%) scale(1.08); filter: blur(8px); }
            5% { opacity: 1; transform: translate(-50%, -50%) scale(1); filter: blur(0); }
            94% { opacity: 1; transform: translate(-50%, -50%) scale(1); filter: blur(0); }
            100% { opacity: 0; transform: translate(-50%, -56%) scale(.985); filter: blur(2px); }
        }
        @media (prefers-reduced-motion: reduce) {
            #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-light {
                animation: none !important; opacity: .24 !important;
            }
            #${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-banner {
                animation: mcmsPayoutBannerReduced var(--mcms-payout-duration, 3000ms) ease-out both !important;
            }
            @keyframes mcmsPayoutBannerReduced {
                0%, 100% { opacity: 0; transform: translate(-50%, -50%); }
                3%, 97% { opacity: 1; transform: translate(-50%, -50%); }
            }
        }

        #${SCRIPT.toastId} { position: fixed !important; left: 12px !important; bottom: 14px !important; z-index: 982 !important; max-width: 280px !important; padding: 6px 9px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.14) !important; background: rgba(10,14,20,.92) !important; color: #fff !important; font: 900 10px/1.15 Arial, Helvetica, sans-serif !important; opacity: 0 !important; transform: translateY(4px) !important; pointer-events: none !important; transition: opacity 140ms ease, transform 140ms ease !important; box-shadow: 0 5px 14px rgba(0,0,0,.28) !important; }
        #${SCRIPT.toastId}.mcms-flash { opacity: 1 !important; transform: translateY(0) !important; }
        #${SCRIPT.panelId}.mcms-map-small { width: 292px !important; }
        #${SCRIPT.panelId}.mcms-map-small .mcms-grid-2 { gap: 6px !important; }
        #${SCRIPT.panelId}.mcms-map-small .mcms-theme-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-toggle-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-place-main { height: 40px !important; padding: 5px !important; grid-template-columns: 18px minmax(0,1fr) !important; gap: 5px !important; }
        #${SCRIPT.panelId}.mcms-map-small .mcms-iconbox { width: 18px !important; height: 18px !important; min-width: 18px !important; font-size: 9px !important; }
        #${SCRIPT.panelId}.mcms-map-small .mcms-label { font-size: 10px !important; }
        #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: none !important; }


        /* v3.3.0 Tablet Mode: map-aware responsive dock, unmistakable enabled states, fitted labels and bottom-sheet panel,
           low-overhead rendering and safe-area aware spacing. */
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId},
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId},
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
            -webkit-tap-highlight-color: transparent !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select,
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} button {
            touch-action: manipulation !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
            width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
            max-width: var(--mcms-tablet-dock-width, min(920px, calc(100% - 20px))) !important;
            display: grid !important;
            grid-template-columns: 52px minmax(0,1fr) !important;
            grid-template-areas: "menu filters" ". pins" !important;
            align-items: start !important;
            column-gap: 7px !important;
            row-gap: 7px !important;
            font-size: 12px !important;
            pointer-events: none !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
            grid-area: menu !important;
            width: 52px !important; height: 48px !important; border-radius: 13px !important;
            background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
            pointer-events: auto !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }
        html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
            width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
            grid-area: filters !important;
            display: grid !important;
            grid-template-columns: repeat(var(--mcms-tablet-filter-columns, 6), minmax(0,1fr)) !important;
            gap: 7px !important;
            width: 100% !important; max-width: none !important; margin-top: 0 !important;
            overflow: visible !important; padding: 0 !important;
            scrollbar-width: none !important; overscroll-behavior: auto !important;
            -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
            pointer-events: none !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
            position: relative !important; isolation: isolate !important; box-sizing: border-box !important;
            flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
            height: var(--mcms-tablet-filter-height, 48px) !important;
            grid-template-columns: 21px minmax(0,1fr) !important; gap: 5px !important; padding: 0 6px !important;
            border-radius: 11px !important; border-width: 1px !important;
            background: linear-gradient(180deg,rgba(14,20,28,.97),rgba(7,11,17,.97)) !important;
            color: rgba(255,255,255,.78) !important; backdrop-filter: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.04) !important;
            scroll-snap-align: none !important; pointer-events: auto !important;
            transition: background 120ms ease,border-color 120ms ease,box-shadow 120ms ease,color 120ms ease,opacity 120ms ease,transform 120ms ease !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) {
            opacity: .76 !important; border-color: rgba(255,255,255,.20) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
            opacity: 1 !important;
            background: linear-gradient(145deg,rgba(8,101,73,.98),rgba(10,72,94,.98) 58%,rgba(14,49,82,.98)) !important;
            border-color: #63f2b1 !important; color: #fff !important;
            box-shadow: 0 0 0 1px rgba(99,242,177,.22),0 0 16px rgba(34,211,153,.38),0 5px 14px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.18) !important;
            transform: translateY(-1px) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::before {
            content: "" !important; position: absolute !important; z-index: 1 !important; pointer-events: none !important;
            left: 5px !important; right: 5px !important; bottom: 3px !important; height: 3px !important;
            border-radius: 999px !important; background: linear-gradient(90deg,transparent,#72ffc0 18%,#61dfff 82%,transparent) !important;
            box-shadow: 0 0 8px rgba(99,242,177,.85) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
            content: "" !important; position: absolute !important; z-index: 3 !important; pointer-events: none !important; top: 5px !important; right: 5px !important;
            width: 5px !important; height: 5px !important; border-radius: 50% !important;
            background: #76ffc1 !important; box-shadow: 0 0 0 2px rgba(5,35,29,.72),0 0 8px rgba(118,255,193,.95) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-key {
            position: relative !important; z-index: 2 !important;
            width: 21px !important; height: 21px !important; border-radius: 7px !important; font-size: 10px !important;
            background: rgba(255,255,255,.11) !important; border: 1px solid rgba(255,255,255,.10) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
            background: rgba(23,198,126,.95) !important; border-color: rgba(194,255,226,.72) !important;
            box-shadow: 0 0 9px rgba(67,239,166,.55) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop { display: none !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet {
            position: relative !important; z-index: 2 !important;
            display: flex !important; align-items: center !important; justify-content: flex-start !important;
            min-width: 0 !important; min-height: 2.05em !important; max-height: 2.05em !important;
            overflow: hidden !important; text-overflow: clip !important; white-space: normal !important;
            overflow-wrap: normal !important; word-break: normal !important; hyphens: none !important;
            font-size: clamp(9px,1.1vw,10.25px) !important; line-height: 1.03 !important; letter-spacing: -.08px !important;
            font-weight: 900 !important; text-align: left !important; padding-right: 4px !important; text-shadow: 0 1px 2px rgba(0,0,0,.72) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
            grid-area: pins !important;
            display: grid !important;
            grid-template-columns: repeat(var(--mcms-tablet-pin-columns, 4), minmax(0,1fr)) !important;
            gap: 7px !important;
            width: 100% !important; max-width: none !important; max-height: none !important; margin-top: 0 !important;
            overflow: visible !important; padding: 0 !important;
            overscroll-behavior: auto !important; -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
            pointer-events: none !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
            flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
            height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
            border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
            pointer-events: auto !important;
        }

        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} {
            padding: 12px !important; border-radius: 18px !important;
            background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
            box-shadow: 0 12px 30px rgba(0,0,0,.52) !important;
            overflow-y: auto !important; overflow-x: hidden !important; overscroll-behavior: contain !important;
            -webkit-overflow-scrolling: touch !important; touch-action: pan-y !important;
            font-size: 13px !important; line-height: 1.25 !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-header {
            position: sticky !important; top: -12px !important; z-index: 8 !important;
            grid-template-columns: minmax(0,1fr) 44px !important; gap: 9px !important;
            min-height: 54px !important; margin: -12px -12px 10px !important; padding: 10px 12px 9px !important;
            background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
            cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close {
            width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 24px !important; line-height: 44px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tabs {
            position: sticky !important; top: 42px !important; z-index: 7 !important;
            grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 8px !important;
            margin: 0 -4px 12px !important; padding: 8px 4px !important; background: rgba(8,12,18,.985) !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
            height: 44px !important; border-radius: 11px !important; font-size: 11.5px !important; padding: 0 6px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap: 9px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-place-main {
            min-height: 58px !important; height: auto !important; padding: 9px !important;
            grid-template-columns: 30px minmax(0,1fr) !important; gap: 9px !important; border-radius: 12px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-iconbox {
            width: 30px !important; height: 30px !important; min-width: 30px !important; border-radius: 9px !important; font-size: 13px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-label { font-size: 12.5px !important; line-height: 1.15 !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top: 5px !important; max-width: 120px !important; padding: 3px 7px !important; font-size: 9px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin: 14px 0 8px !important; font-size: 10.5px !important; letter-spacing: .8px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
            grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
            height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
            min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
            font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
            grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
            margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
            grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }

        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} {
            left: 50% !important; right: auto !important; top: auto !important; bottom: max(8px, env(safe-area-inset-bottom)) !important;
            width: min(700px, calc(100vw - 16px)) !important; max-width: calc(100vw - 16px) !important; max-height: 78dvh !important;
            transform: translateX(-50%) !important; padding: 12px !important; border-radius: 18px !important;
            background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
            overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head { grid-template-columns: minmax(0,1fr) 44px !important; min-height: 52px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title { font-size: 15px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle { font-size: 10px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close { width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { min-height: 56px !important; grid-template-columns: 112px minmax(0,1fr) auto !important; gap: 10px !important; padding: 10px !important; border-radius: 11px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size: 12px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age-band { font-size: 9.5px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-age { font-size: 11px !important; }

        html[data-mcms-tablet-active="true"] #${SCRIPT.missionInspectorId} {
            width: min(420px, calc(100vw - 20px)) !important; padding: 12px 13px !important;
            font-size: 12px !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
            max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
        }

        @media (max-width: 560px) {
            html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }
            html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
            html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row,
            html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 1fr !important; }
            html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { white-space: normal !important; }
        }


        /* v3.3.1 iOS Safari Mobile Mode: map-aware command grid, safe-area bottom sheet,
           Visual Viewport keyboard support and compact high-contrast touch controls. */
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId},
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
        html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId},
        html[data-mcms-mobile-active="true"] #${SCRIPT.missionInspectorId} {
            -webkit-tap-highlight-color: transparent !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} button,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} button,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} select,
        html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} button {
            touch-action: manipulation !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
            width: var(--mcms-mobile-dock-width, calc(100% - 10px)) !important;
            max-width: var(--mcms-mobile-dock-width, calc(100% - 10px)) !important;
            display: grid !important;
            grid-template-columns: repeat(var(--mcms-mobile-columns, 5), minmax(0,1fr)) !important;
            grid-auto-flow: row !important;
            align-items: stretch !important;
            gap: 4px !important;
            margin: 0 !important;
            font-size: 10px !important;
            pointer-events: none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(5px, env(safe-area-inset-left)) !important; top: max(5px, env(safe-area-inset-top)) !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(5px, env(safe-area-inset-right)) !important; top: max(5px, env(safe-area-inset-top)) !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(5px, env(safe-area-inset-left)) !important; bottom: max(5px, env(safe-area-inset-bottom)) !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(5px, env(safe-area-inset-right)) !important; bottom: max(5px, env(safe-area-inset-bottom)) !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-shell {
            grid-column: auto !important; grid-row: auto !important; grid-area: auto !important;
            width: auto !important; min-width: 0 !important; height: var(--mcms-mobile-filter-height,44px) !important;
            border-radius: 10px !important; background: rgba(6,10,16,.97) !important;
            border-color: rgba(116,207,255,.62) !important; box-shadow: 0 3px 10px rgba(0,0,0,.42), inset 0 1px rgba(255,255,255,.08) !important;
            backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 19px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 14px !important; flex-basis: 14px !important; font-size: 10px !important; }
        html[data-mcms-command-bar-open="false"][data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
            width: 50px !important; max-width: 50px !important; grid-template-columns: 50px !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
            display: contents !important; grid-area: auto !important; width: auto !important; max-width: none !important;
            overflow: visible !important; padding: 0 !important; margin: 0 !important; pointer-events: none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter [data-toggle="criticalView"] { grid-column: auto !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
            position: relative !important; isolation: isolate !important; width: auto !important; min-width: 0 !important;
            height: var(--mcms-mobile-filter-height,44px) !important; display: grid !important;
            grid-template-columns: 17px minmax(0,1fr) !important; gap: 3px !important; padding: 0 4px !important;
            border-radius: 10px !important; border: 1px solid rgba(255,255,255,.18) !important;
            background: linear-gradient(180deg,rgba(13,19,27,.98),rgba(6,9,14,.98)) !important;
            color: rgba(255,255,255,.78) !important; box-shadow: 0 3px 10px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.04) !important;
            backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
            transition: background 110ms ease,border-color 110ms ease,box-shadow 110ms ease,color 110ms ease,opacity 110ms ease,transform 110ms ease !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) { opacity: .72 !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
            opacity: 1 !important; transform: translateY(-1px) !important;
            background: linear-gradient(145deg,rgba(7,112,76,.99),rgba(7,77,103,.99) 60%,rgba(12,43,77,.99)) !important;
            border-color: #69ffc0 !important; color: #fff !important;
            box-shadow: 0 0 0 1px rgba(105,255,192,.20),0 0 13px rgba(42,222,158,.45),0 4px 12px rgba(0,0,0,.44),inset 0 1px rgba(255,255,255,.18) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::before {
            content: "" !important; position:absolute !important; z-index:1 !important; left:4px !important; right:4px !important; bottom:2px !important;
            height:3px !important; border-radius:999px !important; background:linear-gradient(90deg,transparent,#72ffc0 18%,#62dcff 82%,transparent) !important;
            box-shadow:0 0 7px rgba(99,242,177,.9) !important; pointer-events:none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
            content:"" !important; position:absolute !important; z-index:3 !important; right:4px !important; top:4px !important;
            width:4px !important; height:4px !important; border-radius:50% !important; background:#7affc5 !important;
            box-shadow:0 0 0 2px rgba(5,35,29,.72),0 0 7px rgba(118,255,193,.98) !important; pointer-events:none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-key {
            position:relative !important; z-index:2 !important; width:17px !important; height:17px !important; border-radius:6px !important;
            font-size:8px !important; background:rgba(255,255,255,.10) !important; border:1px solid rgba(255,255,255,.10) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
            background:rgba(23,198,126,.96) !important; border-color:rgba(194,255,226,.75) !important; box-shadow:0 0 7px rgba(67,239,166,.58) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop,
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet { display:none !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-mobile {
            position:relative !important; z-index:2 !important; display:flex !important; align-items:center !important; justify-content:flex-start !important;
            min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important;
            font-size:clamp(7.5px,2.15vw,9px) !important; line-height:1 !important; font-weight:950 !important; letter-spacing:-.15px !important;
            text-align:left !important; text-shadow:0 1px 2px rgba(0,0,0,.78) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
            grid-area:auto !important; grid-column:1 / -1 !important; display:grid !important;
            grid-template-columns:repeat(var(--mcms-mobile-pin-columns,4),minmax(0,1fr)) !important;
            grid-auto-flow:row !important; justify-self:stretch !important; align-self:stretch !important;
            justify-items:stretch !important; align-items:stretch !important;
            gap:4px !important; width:100% !important; min-width:0 !important; max-width:none !important; max-height:none !important;
            box-sizing:border-box !important; margin:0 !important; padding:0 !important;
            overflow:visible !important; pointer-events:none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display:none !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
            -webkit-appearance:none !important; appearance:none !important;
            display:flex !important; align-items:center !important; justify-content:center !important;
            justify-self:stretch !important; align-self:stretch !important; box-sizing:border-box !important;
            width:100% !important; max-width:none !important; min-width:0 !important;
            height:var(--mcms-mobile-pin-height,34px) !important; padding:0 7px !important;
            border-radius:9px !important; font-size:clamp(8.5px,2.25vw,10px) !important; line-height:1.05 !important;
            letter-spacing:-.08px !important; text-align:center !important; overflow:hidden !important; text-overflow:ellipsis !important;
            white-space:nowrap !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important; pointer-events:auto !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} {
            width:calc(100% - 8px) !important; max-width:calc(100% - 8px) !important;
            border-radius:16px 16px 11px 11px !important; border-color:rgba(112,204,255,.46) !important;
            padding:8px 8px calc(8px + env(safe-area-inset-bottom)) !important;
            overflow-x:hidden !important; overflow-y:auto !important; overscroll-behavior:contain !important;
            -webkit-overflow-scrolling:touch !important; touch-action:pan-y !important;
            background:linear-gradient(180deg,rgba(9,14,21,.99),rgba(4,7,11,.99)) !important;
            box-shadow:0 -12px 38px rgba(0,0,0,.58),inset 0 1px rgba(255,255,255,.06) !important;
            backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}::-webkit-scrollbar,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs::-webkit-scrollbar { display:none !important; width:0 !important; height:0 !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { scrollbar-width:none !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header {
            position:sticky !important; top:-8px !important; z-index:8 !important; min-height:48px !important; margin:-8px -8px 7px !important;
            padding:8px 8px 6px !important; border-radius:16px 16px 0 0 !important; background:rgba(7,11,17,.985) !important;
            border-bottom:1px solid rgba(255,255,255,.10) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-drag-handle { cursor:default !important; touch-action:pan-y !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-title { font-size:12px !important; letter-spacing:.35px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top:3px !important; font-size:9px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display:none !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-close { width:44px !important; height:44px !important; border-radius:12px !important; font-size:20px !important; line-height:42px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
            position:sticky !important; top:40px !important; z-index:7 !important; display:flex !important; gap:5px !important;
            margin:0 -2px 7px !important; padding:2px 2px 6px !important; overflow-x:auto !important; overflow-y:hidden !important;
            overscroll-behavior-x:contain !important; -webkit-overflow-scrolling:touch !important; background:rgba(6,10,15,.96) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
            flex:0 0 auto !important; min-width:74px !important; height:40px !important; padding:0 10px !important; border-radius:10px !important;
            font-size:10px !important; line-height:1 !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap:6px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-place-main { min-height:48px !important; height:auto !important; padding:7px !important; border-radius:11px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-iconbox { width:22px !important; height:22px !important; min-width:22px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-label { font-size:11px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top:4px !important; max-width:110px !important; font-size:8px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin:12px 0 7px !important; font-size:9.5px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:minmax(0,1fr) minmax(132px,44%) !important; gap:7px !important; margin-bottom:7px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size:10.5px !important; white-space:normal !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-input,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-select {
            min-height:44px !important; height:44px !important; border-radius:10px !important; padding:0 9px !important;
            font-size:16px !important; line-height:1.2 !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input[type="range"].mcms-input { min-height:44px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-footer { display:none !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} {
            left:max(4px,env(safe-area-inset-left)) !important; right:max(4px,env(safe-area-inset-right)) !important;
            bottom:max(4px,env(safe-area-inset-bottom)) !important; top:auto !important; width:auto !important; max-width:none !important;
            max-height:min(72dvh,620px) !important; border-radius:15px !important; padding-bottom:calc(9px + env(safe-area-inset-bottom)) !important;
            backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.missionInspectorId} {
            width:min(92vw,340px) !important; max-width:calc(100vw - 16px) !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.toastId} {
            left:50% !important; right:auto !important; bottom:calc(12px + env(safe-area-inset-bottom)) !important;
            max-width:calc(100vw - 24px) !important; transform:translate(-50%,8px) !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.toastId}.mcms-flash { transform:translate(-50%,0) !important; }
        html[data-mcms-mobile-active="true"] .mcms-alliance-credit-badge,
        html[data-mcms-mobile-active="true"] .mcms-mission-age-badge,
        html[data-mcms-mobile-active="true"] .mcms-unit-commitment-badge,
        html[data-mcms-mobile-active="true"] .mcms-transport-watcher-badge,
        html[data-mcms-mobile-active="true"] .mcms-resource-gap-badge {
            backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
        }
        @media (max-width: 430px) {
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
        }
        @media (orientation: landscape) and (max-height: 500px) {
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { min-height:42px !important; padding-top:5px !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { display:none !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { top:34px !important; }
            html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { height:36px !important; }
        }

        /* v3.4.2: collapse after the exit animation and override later tablet/mobile layout rules. */
        #${SCRIPT.controlId} {
            transition: width 180ms cubic-bezier(.2,.78,.22,1), max-width 180ms cubic-bezier(.2,.78,.22,1) !important;
        }
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins {
            display: none !important;
            pointer-events: none !important;
        }
        @media (prefers-reduced-motion: reduce) {
            #${SCRIPT.controlId} { transition: none !important; }
        }

        /* v2.5.x mission intelligence and configuration tools */
        #${SCRIPT.missionInspectorId} {
            position: fixed !important; left: 0 !important; top: 0 !important; z-index: 2147483646 !important;
            width: min(300px, calc(100vw - 24px)) !important; padding: 10px 11px !important;
            border: 1px solid rgba(255,255,255,.18) !important; border-radius: 10px !important;
            background: linear-gradient(180deg, rgba(14,19,27,.97), rgba(7,10,15,.96)) !important;
            color: #eef4fb !important; box-shadow: 0 14px 34px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.06) !important;
            font: 700 10px/1.35 Arial, Helvetica, sans-serif !important; pointer-events: none !important;
            opacity: 0 !important; visibility: hidden !important; transform: translateY(4px) scale(.985) !important;
            transition: opacity 110ms ease, transform 110ms ease, visibility 110ms step-end !important; backdrop-filter: blur(6px) !important;
        }
        #${SCRIPT.missionInspectorId}.mcms-open { opacity: 1 !important; visibility: visible !important; transform: translateY(0) scale(1) !important; transition: opacity 110ms ease, transform 110ms ease, visibility 0s step-start !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-head { display:flex !important; align-items:flex-start !important; justify-content:space-between !important; gap:8px !important; margin-bottom:7px !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-title { display:block !important; min-width:0 !important; color:#fff !important; font-size:12px !important; font-weight:950 !important; line-height:1.2 !important; overflow:hidden !important; text-overflow:ellipsis !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-type { flex:0 0 auto !important; padding:3px 5px !important; border-radius:5px !important; border:1px solid rgba(255,255,255,.16) !important; background:rgba(255,255,255,.06) !important; color:#b9c8d8 !important; font-size:7px !important; font-weight:950 !important; letter-spacing:.6px !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-type.mcms-alliance { color:#8df3ad !important; border-color:rgba(112,239,155,.38) !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-stat { min-width:0 !important; padding:6px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; border:1px solid rgba(255,255,255,.08) !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-stat span { display:block !important; color:#8393a5 !important; font-size:7px !important; font-weight:900 !important; letter-spacing:.4px !important; text-transform:uppercase !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong { display:block !important; margin-top:2px !important; color:#fff !important; font-size:11px !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-alert { margin-top:6px !important; padding:6px 7px !important; border-radius:7px !important; border:1px solid rgba(255,181,71,.34) !important; background:rgba(255,143,31,.11) !important; color:#ffd29a !important; font-size:8px !important; font-weight:900 !important; line-height:1.35 !important; white-space:normal !important; overflow-wrap:anywhere !important; }
        #${SCRIPT.missionInspectorId} .mcms-inspector-alert.mcms-stuck { border-color:rgba(255,74,64,.48) !important; background:rgba(255,44,36,.14) !important; color:#ffaaa4 !important; }

        .mcms-stuck-mission-icon { pointer-events:none !important; }
        .mcms-stuck-mission-badge { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:58px !important; height:17px !important; padding:0 6px !important; border-radius:6px !important; border:1px solid rgba(255,86,72,.72) !important; background:rgba(90,10,8,.88) !important; color:#ffd7d2 !important; font:950 8px/17px Arial,Helvetica,sans-serif !important; letter-spacing:.35px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 10px rgba(255,53,39,.32) !important; white-space:nowrap !important; }
        .mcms-stuck-mission-badge.mcms-stuck-severe { background:rgba(130,7,4,.94) !important; border-color:#ff3d2e !important; color:#fff !important; animation:mcmsStuckPulse 1.3s ease-in-out infinite !important; }
        @keyframes mcmsStuckPulse { 0%,100%{box-shadow:0 0 7px rgba(255,53,39,.28);transform:scale(1)} 50%{box-shadow:0 0 16px rgba(255,53,39,.70);transform:scale(1.035)} }

        .mcms-mission-spawn-ring { transform-box:fill-box !important; stroke:#67d9ff !important; stroke-width:3 !important; fill:rgba(48,183,255,.12) !important; transform-origin:center !important; animation:mcmsMissionSpawnRing 2.35s cubic-bezier(.12,.72,.18,1) both !important; pointer-events:none !important; }
        .mcms-mission-spawn-label-icon { pointer-events:none !important; }
        .mcms-mission-spawn-label { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:86px !important; height:20px !important; padding:0 8px !important; border-radius:7px !important; border:1px solid rgba(98,219,255,.78) !important; background:rgba(4,22,34,.92) !important; color:#aeeeff !important; font:950 8px/20px Arial,Helvetica,sans-serif !important; letter-spacing:.65px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 16px rgba(67,198,255,.42) !important; animation:mcmsMissionSpawnLabel 2.35s ease-out both !important; white-space:nowrap !important; }
        .leaflet-marker-icon.mcms-mission-spawn-focus { animation:mcmsMissionSpawnMarker 2.2s cubic-bezier(.16,.74,.18,1) both !important; }
        @keyframes mcmsMissionSpawnRing { 0%{opacity:0;transform:scale(.25)} 12%{opacity:1;transform:scale(.55)} 75%{opacity:.50;transform:scale(3.2)} 100%{opacity:0;transform:scale(4.2)} }
        @keyframes mcmsMissionSpawnLabel { 0%{opacity:0;transform:translateY(8px) scale(.9)} 14%,72%{opacity:1;transform:translateY(0) scale(1)} 100%{opacity:0;transform:translateY(-8px) scale(.96)} }
        @keyframes mcmsMissionSpawnMarker { 0%{filter:brightness(1);transform:scale(1)} 12%{filter:brightness(1.55) drop-shadow(0 0 10px #53d9ff);transform:scale(1.22)} 34%{filter:brightness(1.15) drop-shadow(0 0 6px #53d9ff);transform:scale(.98)} 58%{filter:brightness(1.35) drop-shadow(0 0 8px #53d9ff);transform:scale(1.12)} 100%{filter:brightness(1);transform:scale(1)} }

        #${SCRIPT.panelId} .mcms-profile-list { display:grid !important; gap:6px !important; }
        #${SCRIPT.panelId} .mcms-profile-row { display:grid !important; grid-template-columns:minmax(0,1fr) 36px 36px 25px !important; gap:5px !important; align-items:center !important; }
        #${SCRIPT.panelId} .mcms-profile-main { min-width:0 !important; padding:6px 7px !important; border:1px solid rgba(255,255,255,.09) !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; }
        #${SCRIPT.panelId} .mcms-profile-main strong,#${SCRIPT.panelId} .mcms-profile-main span { display:block !important; min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
        #${SCRIPT.panelId} .mcms-profile-main strong { color:#edf4fb !important; font-size:9px !important; }
        #${SCRIPT.panelId} .mcms-profile-main span { color:#8393a5 !important; font-size:7px !important; margin-top:2px !important; }
        #${SCRIPT.panelId} .mcms-config-actions { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
        #${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions [data-action="reset-config"] { grid-column:1 / -1 !important; }
        #${SCRIPT.panelId} .mcms-hidden-file { display:none !important; }


        /* v3.5.1 complete interface themes */
        #${SCRIPT.panelId} .mcms-ui-theme-grid {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 7px !important;
            margin-bottom: 7px !important;
        }
        #${SCRIPT.panelId} .mcms-ui-theme-btn {
            position: relative !important;
            display: grid !important;
            grid-template-columns: 48px minmax(0, 1fr) !important;
            align-items: center !important;
            gap: 8px !important;
            min-width: 0 !important;
            height: 58px !important;
            padding: 6px 8px !important;
            border: 1px solid rgba(255,255,255,.14) !important;
            border-radius: 10px !important;
            background: rgba(255,255,255,.055) !important;
            color: rgba(255,255,255,.82) !important;
            cursor: pointer !important;
            text-align: left !important;
            overflow: hidden !important;
            transition: transform 140ms ease, border-color 140ms ease, background 140ms ease !important;
        }
        #${SCRIPT.panelId} .mcms-ui-theme-btn:hover,
        #${SCRIPT.panelId} .mcms-ui-theme-btn:focus-visible {
            transform: translateY(-1px) !important;
            border-color: rgba(124,194,255,.72) !important;
            background: rgba(93,169,255,.12) !important;
        }
        #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active {
            border-color: rgba(124,194,255,.92) !important;
            background: linear-gradient(135deg, rgba(25,118,210,.34), rgba(20,50,82,.26)) !important;
            box-shadow: inset 0 0 0 1px rgba(145,210,255,.14), 0 5px 14px rgba(0,0,0,.18) !important;
            color: #fff !important;
        }
        #${SCRIPT.panelId} .mcms-ui-theme-preview {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            align-items: end !important;
            gap: 3px !important;
            width: 48px !important;
            height: 36px !important;
            padding: 5px !important;
            border: 1px solid rgba(255,255,255,.16) !important;
            border-radius: 7px !important;
            background: rgba(3,7,12,.74) !important;
            overflow: hidden !important;
        }
        #${SCRIPT.panelId} .mcms-ui-theme-preview span { display: block !important; border-radius: 2px 2px 0 0 !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(1) { height: 52% !important; background: #4c89bd !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(2) { height: 86% !important; background: #d7e8f7 !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(3) { height: 68% !important; background: #2c5f87 !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk {
            border-radius: 1px !important;
            border-color: #00f0ff !important;
            background: #080b12 !important;
            box-shadow: inset 0 0 9px rgba(0,240,255,.20) !important;
            clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
        }
        #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span { border-radius: 0 !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(1) { height: 82% !important; background: #fcee0a !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(2) { height: 48% !important; background: #00f0ff !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(3) { height: 68% !important; background: #ff003c !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-copy { min-width: 0 !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-copy strong,
        #${SCRIPT.panelId} .mcms-ui-theme-copy small { display: block !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-copy strong { color: inherit !important; font-size: 10px !important; font-weight: 950 !important; }
        #${SCRIPT.panelId} .mcms-ui-theme-copy small { margin-top: 4px !important; color: rgba(255,255,255,.48) !important; font-size: 7px !important; font-weight: 900 !important; letter-spacing: .7px !important; }

        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 46px !important; height: 38px !important; }

        html[data-mcms-ui-theme="cyberpunk"] {
            --mcms-cp-yellow: #fcee0a;
            --mcms-cp-cyan: #00f0ff;
            --mcms-cp-red: #ff003c;
            --mcms-cp-ink: #070a10;
            --mcms-cp-panel: #0b1019;
            --mcms-cp-panel-2: #111925;
            --mcms-cp-text: #f5f7ef;
            --mcms-cp-muted: #90a3ad;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} *,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} *,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} *,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} * {
            font-family: "Bahnschrift SemiCondensed", "Arial Narrow", Tahoma, Arial, sans-serif !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} {
            color: var(--mcms-cp-text) !important;
            filter: drop-shadow(0 8px 13px rgba(0,0,0,.46)) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-shell {
            border: 1px solid var(--mcms-cp-cyan) !important;
            border-radius: 1px !important;
            background: linear-gradient(145deg, rgba(12,17,27,.97), rgba(3,7,12,.96)) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-yellow), inset 0 -2px 0 rgba(255,0,60,.72), 0 0 13px rgba(0,240,255,.27), 0 7px 18px rgba(0,0,0,.48) !important;
            backdrop-filter: blur(8px) saturate(1.22) !important;
            clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-menu-btn {
            background: linear-gradient(135deg, rgba(252,238,10,.08), rgba(0,240,255,.04)) !important;
            color: var(--mcms-cp-yellow) !important;
            text-shadow: 1px 0 var(--mcms-cp-red), -1px 0 rgba(0,240,255,.75) !important;
            transition: background 120ms steps(2,end), color 120ms ease, filter 120ms ease !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-menu-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-menu-btn:focus-visible {
            background: var(--mcms-cp-yellow) !important;
            color: var(--mcms-cp-ink) !important;
            filter: brightness(1.08) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-dock-toggle-btn {
            border-top: 1px solid rgba(0,240,255,.64) !important;
            background: rgba(0,240,255,.08) !important;
            color: var(--mcms-cp-cyan) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-dock-toggle-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-dock-toggle-btn:focus-visible {
            background: var(--mcms-cp-cyan) !important;
            color: var(--mcms-cp-ink) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-floating-filter { gap: 5px !important; }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
            position: relative !important;
            border: 1px solid rgba(0,240,255,.52) !important;
            border-radius: 1px !important;
            background: linear-gradient(100deg, rgba(7,11,18,.96), rgba(15,24,35,.94)) !important;
            color: #dbeef0 !important;
            box-shadow: inset 2px 0 0 rgba(0,240,255,.65), 0 4px 10px rgba(0,0,0,.36) !important;
            clip-path: polygon(0 0, calc(100% - 7px) 0, 100% 7px, 100% 100%, 5px 100%, 0 calc(100% - 5px)) !important;
            transition: transform 110ms ease, background 110ms ease, border-color 110ms ease, color 110ms ease !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn:hover {
            transform: translateX(2px) !important;
            border-color: var(--mcms-cp-yellow) !important;
            color: #fff !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-key {
            border-radius: 0 !important;
            border: 1px solid rgba(252,238,10,.72) !important;
            background: rgba(252,238,10,.09) !important;
            color: var(--mcms-cp-yellow) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
            border-color: var(--mcms-cp-yellow) !important;
            background: linear-gradient(100deg, var(--mcms-cp-yellow), #d7c900) !important;
            color: var(--mcms-cp-ink) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-red), 0 0 13px rgba(252,238,10,.32), 0 4px 10px rgba(0,0,0,.42) !important;
            animation: mcmsCyberSignal 2.8s ease-in-out infinite !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
            border-color: var(--mcms-cp-ink) !important;
            background: rgba(7,10,16,.92) !important;
            color: var(--mcms-cp-yellow) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-quick {
            border-color: rgba(0,240,255,.80) !important;
            background: linear-gradient(100deg, rgba(0,240,255,.18), rgba(4,18,27,.96)) !important;
            color: #bdfaff !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-custom {
            border-color: rgba(252,238,10,.86) !important;
            background: linear-gradient(100deg, rgba(252,238,10,.16), rgba(24,22,5,.96)) !important;
            color: #fff7a2 !important;
        }

        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} {
            border: 1px solid var(--mcms-cp-cyan) !important;
            border-radius: 1px !important;
            background:
                linear-gradient(180deg, rgba(11,16,25,.985), rgba(5,8,13,.985)),
                repeating-linear-gradient(90deg, rgba(0,240,255,.035) 0 1px, transparent 1px 22px),
                repeating-linear-gradient(0deg, rgba(252,238,10,.022) 0 1px, transparent 1px 22px) !important;
            color: var(--mcms-cp-text) !important;
            box-shadow: inset 4px 0 0 var(--mcms-cp-yellow), inset -2px 0 0 rgba(255,0,60,.78), 0 0 0 1px rgba(252,238,10,.15), 0 0 24px rgba(0,240,255,.24), 0 18px 44px rgba(0,0,0,.62) !important;
            backdrop-filter: blur(12px) saturate(1.18) !important;
            scrollbar-color: var(--mcms-cp-yellow) rgba(0,240,255,.08) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}.mcms-open {
            animation: mcmsCyberPanelIn 190ms cubic-bezier(.16,.78,.22,1) both !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}::-webkit-scrollbar { width: 8px !important; }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}::-webkit-scrollbar-track { background: rgba(0,240,255,.06) !important; }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}::-webkit-scrollbar-thumb { background: var(--mcms-cp-yellow) !important; border: 2px solid #0b1019 !important; }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-header {
            position: relative !important;
            border-bottom: 1px solid var(--mcms-cp-cyan) !important;
            background: linear-gradient(90deg, var(--mcms-cp-yellow) 0 76%, rgba(252,238,10,.13) 76% 100%) !important;
            margin: -3px -3px 9px -3px !important;
            padding: 5px 5px 6px 5px !important;
            overflow: hidden !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-header::after {
            content: '' !important;
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 34% !important;
            height: 2px !important;
            background: var(--mcms-cp-red) !important;
            box-shadow: 0 0 8px var(--mcms-cp-red) !important;
            animation: mcmsCyberScan 4.8s linear infinite !important;
            pointer-events: none !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-drag-handle {
            border: 0 !important;
            border-radius: 0 !important;
            background: transparent !important;
            padding: 2px 5px !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-title {
            color: var(--mcms-cp-ink) !important;
            font-weight: 1000 !important;
            letter-spacing: 1.25px !important;
            text-shadow: 1px 0 rgba(255,0,60,.72) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-subtitle {
            color: rgba(7,10,16,.76) !important;
            font-weight: 900 !important;
            letter-spacing: .35px !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close {
            border: 1px solid var(--mcms-cp-ink) !important;
            border-radius: 0 !important;
            background: var(--mcms-cp-ink) !important;
            color: var(--mcms-cp-yellow) !important;
            clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 0 100%) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close:hover {
            background: var(--mcms-cp-red) !important;
            color: #fff !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tabs {
            gap: 4px !important;
            border-bottom: 1px solid rgba(0,240,255,.20) !important;
            padding-bottom: 7px !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn {
            position: relative !important;
            border: 1px solid rgba(0,240,255,.34) !important;
            border-radius: 0 !important;
            background: rgba(0,240,255,.045) !important;
            color: #9fdce0 !important;
            letter-spacing: .55px !important;
            clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 0 100%) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
            border-color: var(--mcms-cp-cyan) !important;
            color: #fff !important;
            background: rgba(0,240,255,.12) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
            border-color: var(--mcms-cp-yellow) !important;
            background: var(--mcms-cp-yellow) !important;
            color: var(--mcms-cp-ink) !important;
            box-shadow: inset 0 -3px 0 var(--mcms-cp-red), 0 0 10px rgba(252,238,10,.20) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
            animation: mcmsCyberTabIn 150ms steps(3,end) both !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label {
            position: relative !important;
            margin-top: 11px !important;
            padding: 5px 7px 5px 16px !important;
            border: 0 !important;
            border-bottom: 1px solid rgba(0,240,255,.34) !important;
            background: linear-gradient(90deg, rgba(252,238,10,.14), transparent 70%) !important;
            color: var(--mcms-cp-yellow) !important;
            font-size: 9px !important;
            font-weight: 1000 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label::before {
            content: '' !important;
            position: absolute !important;
            left: 4px !important;
            top: 7px !important;
            width: 6px !important;
            height: 6px !important;
            background: var(--mcms-cp-cyan) !important;
            box-shadow: 0 0 7px rgba(0,240,255,.72) !important;
            transform: rotate(45deg) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-place-main,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-position-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-small-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-pin-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
            border-color: rgba(0,240,255,.38) !important;
            border-radius: 1px !important;
            background: linear-gradient(110deg, rgba(8,13,21,.94), rgba(17,25,37,.88)) !important;
            color: #c9e9ec !important;
            box-shadow: inset 2px 0 0 rgba(0,240,255,.34) !important;
            clip-path: polygon(0 0, calc(100% - 7px) 0, 100% 7px, 100% 100%, 5px 100%, 0 calc(100% - 5px)) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-place-main:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-position-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-small-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
            border-color: var(--mcms-cp-yellow) !important;
            background: linear-gradient(110deg, rgba(252,238,10,.13), rgba(0,240,255,.08)) !important;
            color: #fff !important;
            transform: translateY(-1px) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-position-btn.mcms-active,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-pin-btn.mcms-on,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active {
            border-color: var(--mcms-cp-yellow) !important;
            background: linear-gradient(105deg, var(--mcms-cp-yellow), #d7ca00) !important;
            color: var(--mcms-cp-ink) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-red), 0 0 12px rgba(252,238,10,.22) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-iconbox,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-iconbox,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-pill,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-pill {
            background: var(--mcms-cp-ink) !important;
            border-color: var(--mcms-cp-ink) !important;
            color: var(--mcms-cp-yellow) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-iconbox {
            border-radius: 0 !important;
            border: 1px solid rgba(0,240,255,.38) !important;
            background: rgba(0,240,255,.07) !important;
            color: var(--mcms-cp-cyan) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-pill {
            border-radius: 0 !important;
            border: 1px solid rgba(252,238,10,.38) !important;
            background: rgba(252,238,10,.07) !important;
            color: var(--mcms-cp-yellow) !important;
            letter-spacing: .5px !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-row-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-name,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-title,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main strong {
            color: #d8edef !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-input,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-select {
            border: 1px solid rgba(0,240,255,.52) !important;
            border-radius: 0 !important;
            background: rgba(4,10,16,.92) !important;
            color: #e7ffff !important;
            box-shadow: inset 2px 0 0 rgba(0,240,255,.35) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-input:focus,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-select:focus {
            border-color: var(--mcms-cp-yellow) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-red), 0 0 0 2px rgba(252,238,10,.12), 0 0 10px rgba(0,240,255,.20) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-select option {
            background: #080d15 !important;
            color: #e8ffff !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-status,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-history-older,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-empty-state,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-discord-card,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-discord-empty {
            border-color: rgba(0,240,255,.25) !important;
            border-radius: 1px !important;
            background: linear-gradient(105deg, rgba(0,240,255,.055), rgba(252,238,10,.025)) !important;
            box-shadow: inset 2px 0 0 rgba(0,240,255,.22) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-status {
            color: #91b9bd !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-status {
            border-color: rgba(252,238,10,.25) !important;
            box-shadow: inset 2px 0 0 rgba(252,238,10,.50) !important;
            color: #c4c694 !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-value,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-value {
            color: var(--mcms-cp-yellow) !important;
            text-shadow: 0 0 8px rgba(252,238,10,.22) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-footer {
            border-top: 1px solid rgba(0,240,255,.28) !important;
            color: #6f989d !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-build {
            color: var(--mcms-cp-cyan) !important;
            letter-spacing: .55px !important;
        }

        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.toastId} {
            border: 1px solid var(--mcms-cp-cyan) !important;
            border-radius: 1px !important;
            background: linear-gradient(100deg, rgba(4,9,15,.98), rgba(15,23,33,.97)) !important;
            color: var(--mcms-cp-yellow) !important;
            box-shadow: inset 4px 0 0 var(--mcms-cp-red), 0 0 16px rgba(0,240,255,.26), 0 7px 18px rgba(0,0,0,.46) !important;
            font-family: "Bahnschrift SemiCondensed", "Arial Narrow", Tahoma, Arial, sans-serif !important;
            letter-spacing: .6px !important;
            clip-path: polygon(0 0, calc(100% - 9px) 0, 100% 9px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.cleanExitId} {
            border: 1px solid var(--mcms-cp-yellow) !important;
            border-radius: 0 !important;
            background: #080c13 !important;
            color: var(--mcms-cp-yellow) !important;
            box-shadow: inset 4px 0 0 var(--mcms-cp-red), 0 0 14px rgba(252,238,10,.26) !important;
            font-family: "Bahnschrift SemiCondensed", "Arial Narrow", Tahoma, Arial, sans-serif !important;
            letter-spacing: .55px !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} {
            border: 1px solid var(--mcms-cp-cyan) !important;
            border-radius: 1px !important;
            background: linear-gradient(145deg, rgba(8,13,21,.985), rgba(3,7,12,.98)) !important;
            color: var(--mcms-cp-text) !important;
            box-shadow: inset 4px 0 0 var(--mcms-cp-yellow), inset -2px 0 0 rgba(255,0,60,.66), 0 0 20px rgba(0,240,255,.22), 0 14px 34px rgba(0,0,0,.56) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-drawer-head,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-head {
            border-bottom-color: rgba(0,240,255,.35) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-drawer-title,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-title {
            color: var(--mcms-cp-yellow) !important;
            letter-spacing: .7px !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-drawer-close {
            border: 1px solid var(--mcms-cp-red) !important;
            border-radius: 0 !important;
            background: rgba(255,0,60,.12) !important;
            color: #ff8ca8 !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-critical-row,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-alert,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-gap {
            border-radius: 1px !important;
            border-color: rgba(0,240,255,.28) !important;
            background: rgba(0,240,255,.045) !important;
            box-shadow: inset 2px 0 0 rgba(0,240,255,.24) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-critical-row:hover {
            border-color: var(--mcms-cp-yellow) !important;
            background: rgba(252,238,10,.09) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-type {
            border-radius: 0 !important;
            border-color: rgba(0,240,255,.42) !important;
            background: rgba(0,240,255,.08) !important;
            color: var(--mcms-cp-cyan) !important;
        }

        html[data-mcms-ui-theme="cyberpunk"] .mcms-alliance-credit-badge,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-age-badge,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-unit-commitment-badge,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-transport-watcher-badge,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-resource-gap-badge,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-stuck-mission-badge,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-spawn-label {
            border-radius: 1px !important;
            font-family: "Bahnschrift SemiCondensed", "Arial Narrow", Tahoma, Arial, sans-serif !important;
            letter-spacing: .45px !important;
            clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 4px 100%, 0 calc(100% - 4px)) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-spawn-label {
            border-color: var(--mcms-cp-cyan) !important;
            background: rgba(3,12,18,.95) !important;
            color: var(--mcms-cp-yellow) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-red), 0 0 16px rgba(0,240,255,.38) !important;
        }

        /* Cyberpunk readability and contrast pass. */
        html[data-mcms-ui-theme="cyberpunk"] {
            --mcms-cp-text: #f7fbfc;
            --mcms-cp-muted: #b7c9cf;
            --mcms-cp-soft: #d8e7ea;
            --mcms-cp-ink: #05070b;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-row-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-name,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-title,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main strong,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-title,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-critical-name,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat strong,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-gap-row {
            color: var(--mcms-cp-text) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-footer,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-status,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-empty-state,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-history-older > summary,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-history-older > summary::after,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-state,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-stat span,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-meta,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-log,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat span,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-gap-row span:last-child {
            color: var(--mcms-cp-muted) !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-state,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-stat span,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-meta,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} .mcms-critical-meta,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.missionInspectorId} .mcms-inspector-stat span {
            font-size: 8px !important;
            line-height: 1.25 !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-input::placeholder {
            color: #9fb5bc !important;
            opacity: 1 !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-input:focus-visible,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-select:focus-visible,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:focus-visible,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} button:focus-visible,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.criticalDrawerId} button:focus-visible {
            outline: 2px solid var(--mcms-cp-yellow) !important;
            outline-offset: 2px !important;
        }

        /* Yellow active controls always use dark text, including nested labels. */
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-desktop,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-tablet,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-mobile,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-text,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-text,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy strong,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy small {
            color: var(--mcms-cp-ink) !important;
            text-shadow: none !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy strong {
            font-weight: 1000 !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy small {
            color: rgba(5,7,11,.78) !important;
        }

        /* Red controls also use dark text to meet small-text contrast targets. */
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel:focus-visible,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close:focus-visible {
            background: #ff315f !important;
            color: var(--mcms-cp-ink) !important;
            text-shadow: none !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] .mcms-transport-watcher-count {
            border-color: var(--mcms-cp-ink) !important;
            background: var(--mcms-cp-yellow) !important;
            color: var(--mcms-cp-ink) !important;
            text-shadow: none !important;
        }

        /* Disabled controls remain distinguishable without becoming unreadable. */
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} button:disabled {
            border-color: #41535b !important;
            background: #111821 !important;
            color: #9dafb5 !important;
            box-shadow: none !important;
            filter: saturate(.35) !important;
            opacity: .78 !important;
            text-shadow: none !important;
            cursor: not-allowed !important;
            animation: none !important;
        }
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled .mcms-label,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled .mcms-text,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled strong,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled small {
            color: #9dafb5 !important;
            text-shadow: none !important;
        }

        /* Device-specific small copy receives a minimum readable size. */
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
            font-size: 9px !important;
        }
        html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-copy small,
        html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main span,
        html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-stat-label,
        html[data-mcms-mobile-active="true"][data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-meta {
            font-size: 8.5px !important;
        }

        @keyframes mcmsCyberPanelIn {
            0% { opacity: 0; transform: translateY(8px) scale(.985); filter: saturate(.5) brightness(1.35); }
            45% { opacity: 1; transform: translateY(-1px) scale(1.002); filter: saturate(1.35) brightness(1.08); }
            100% { opacity: 1; transform: translateY(0) scale(1); filter: none; }
        }
        @keyframes mcmsCyberTabIn {
            0% { opacity: .22; transform: translateX(-4px); }
            55% { opacity: .85; transform: translateX(1px); }
            100% { opacity: 1; transform: translateX(0); }
        }
        @keyframes mcmsCyberSignal {
            0%, 100% { filter: brightness(1); }
            48% { filter: brightness(1); }
            50% { filter: brightness(1.18); }
            52% { filter: brightness(.94); }
            54% { filter: brightness(1.08); }
        }
        @keyframes mcmsCyberScan {
            0% { transform: translateX(-110%); opacity: 0; }
            8% { opacity: 1; }
            42% { opacity: 1; }
            50%, 100% { transform: translateX(390%); opacity: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}.mcms-open,
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active,
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-header::after,
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
                animation: none !important;
            }
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn,
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn,
            html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button {
                transition: none !important;
            }
        }

    `);

    function isVisible(el) {
        if (!el || !(el instanceof Element)) return false;
        const rect = el.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return false;
        const style = pageWindow.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) !== 0;
    }

    function normaliseRegistryValues(registry) {
        if (!registry) return [];
        if (Array.isArray(registry)) return registry;
        try {
            if (typeof registry.values === 'function') return Array.from(registry.values());
            if (typeof registry[Symbol.iterator] === 'function') return Array.from(registry);
            if (typeof registry === 'object') return Object.values(registry);
        } catch (err) {}
        return [];
    }

    function getCachedRegistry(globalName, maxAge = MARKER_REGISTRY_CACHE_MS) {
        let registry = null;
        try { registry = pageWindow[globalName]; } catch (err) { return []; }
        if (!registry) return [];
        const now = Date.now();
        const cached = markerRegistryCache.get(globalName);
        if (cached && cached.registry === registry && now - cached.createdAt <= maxAge) return cached.values;
        const values = normaliseRegistryValues(registry);
        markerRegistryCache.set(globalName, { registry, createdAt: now, values });
        return values;
    }

    function invalidateMarkerRegistryCaches(scope = 'all') {
        markerRegistryRevision += 1;
        if (scope === 'all' || scope === 'mission') {
            markerRegistryCache.delete('mission_markers');
            missionIconMarkerCache = new WeakMap();
        }
        if (scope === 'all' || scope === 'vehicle') markerRegistryCache.delete('vehicle_markers');
        if (scope === 'all' || scope === 'building') {
            markerRegistryCache.delete('building_markers');
            markerRegistryCache.delete('building_markers_cache');
            buildingRegistryRevision += 1;
            personalBuildingIdsCache.createdAt = 0;
            heatmapSourceCache.createdAt = 0;
        }
    }

    function currentUserIdCached() {
        const now = Date.now();
        if (cachedUserId !== null || now - cachedUserIdReadAt < 1000) return cachedUserId;
        cachedUserIdReadAt = now;
        try {
            const value = pageWindow.user_id;
            cachedUserId = value === undefined || value === null || value === '' ? null : String(value);
        } catch (err) {
            cachedUserId = null;
        }
        return cachedUserId;
    }

    function schedulePanelPosition(useSavedPosition = true, delay = 80) {
        runtimeClearTimeout(panelPositionTimer);
        panelPositionTimer = runtimeSetTimeout(() => positionPanelOverlay(useSavedPosition), Math.max(0, Number(delay) || 0));
    }

    function setInnerHtmlIfChanged(element, html, signature = html) {
        if (!element) return false;
        const nextSignature = String(signature);
        if (element.__mcmsRenderSignature === nextSignature) return false;
        element.__mcmsRenderSignature = nextSignature;
        element.innerHTML = html;
        return true;
    }

    function getLargestLeafletMap() {
        if (cachedMapElement?.isConnected && isVisible(cachedMapElement)) return cachedMapElement;
        const candidates = Array.from(document.querySelectorAll('.leaflet-container')).filter(isVisible);
        let largest = null;
        let largestArea = 0;
        for (const candidate of candidates) {
            const rect = candidate.getBoundingClientRect();
            const area = rect.width * rect.height;
            if (area > largestArea) {
                largest = candidate;
                largestArea = area;
            }
        }
        cachedMapElement = largest;
        return largest;
    }

    function getViewportMetrics() {
        const viewport = pageWindow.visualViewport;
        const width = Math.max(1, Number(viewport?.width) || Number(pageWindow.innerWidth) || Number(document.documentElement.clientWidth) || 1);
        const height = Math.max(1, Number(viewport?.height) || Number(pageWindow.innerHeight) || Number(document.documentElement.clientHeight) || 1);
        const offsetLeft = Number.isFinite(Number(viewport?.offsetLeft)) ? Number(viewport.offsetLeft) : 0;
        const offsetTop = Number.isFinite(Number(viewport?.offsetTop)) ? Number(viewport.offsetTop) : 0;
        return {
            width,
            height,
            offsetLeft,
            offsetTop,
            orientation: width >= height ? 'landscape' : 'portrait'
        };
    }

    function hasCoarsePointer() {
        try {
            return Boolean(
                pageWindow.matchMedia?.('(pointer: coarse)')?.matches ||
                pageWindow.matchMedia?.('(any-pointer: coarse)')?.matches
            );
        } catch (err) {
            return false;
        }
    }

    function getIosBrowserSignals() {
        const nav = pageWindow.navigator || navigator;
        const userAgent = String(nav?.userAgent || '');
        const platform = String(nav?.platform || '');
        const touchPoints = Number(nav?.maxTouchPoints || 0);
        const { width, height } = getViewportMetrics();
        const shortestSide = Math.min(width, height);
        const iosHandheld = /iPhone|iPod/i.test(userAgent) || (/MacIntel/i.test(platform) && touchPoints > 1 && shortestSide < 500);
        const appleWebKit = /AppleWebKit/i.test(userAgent);
        const alternateIosBrowser = /CriOS|FxiOS|EdgiOS|OPiOS|DuckDuckGo|YaBrowser|GSA/i.test(userAgent);
        const safari = appleWebKit && !alternateIosBrowser;
        return { iosHandheld, safari, appleWebKit, touchPoints };
    }

    function autoDetectMobileMode() {
        const { width, height } = getViewportMetrics();
        const shortestSide = Math.min(width, height);
        const longestSide = Math.max(width, height);
        const signals = getIosBrowserSignals();
        return signals.iosHandheld && signals.safari && signals.touchPoints > 0 && shortestSide < 500 && longestSide <= 1100;
    }

    function autoDetectTabletMode() {
        const { width, height } = getViewportMetrics();
        const shortestSide = Math.min(width, height);
        const longestSide = Math.max(width, height);
        const touchPoints = Number(pageWindow.navigator?.maxTouchPoints || navigator.maxTouchPoints || 0);
        return touchPoints > 0 && hasCoarsePointer() && shortestSide >= 500 && longestSide <= 1600;
    }

    function resolveDeviceLayout() {
        if (state.mobileMode === 'on') return 'mobile';
        if (state.tabletMode === 'on') return 'tablet';
        if (state.mobileMode !== 'off' && autoDetectMobileMode()) return 'mobile';
        if (state.tabletMode !== 'off' && autoDetectTabletMode()) return 'tablet';
        return 'desktop';
    }

    function resolveTabletMode(layout = activeDeviceLayout) {
        return layout === 'tablet';
    }

    function resolveMobileMode(layout = activeDeviceLayout) {
        return layout === 'mobile';
    }

    function isTouchLayoutActive() {
        return tabletModeActive || mobileModeActive;
    }

    function deviceLayoutStatusText() {
        const { width, height, orientation } = getViewportMetrics();
        const mobileLabel = state.mobileMode === 'auto' ? 'Mobile auto' : state.mobileMode === 'on' ? 'Mobile forced on' : 'Mobile forced off';
        const tabletLabel = state.tabletMode === 'auto' ? 'Tablet auto' : state.tabletMode === 'on' ? 'Tablet forced on' : 'Tablet forced off';
        const activeLabel = activeDeviceLayout === 'mobile' ? 'iOS mobile layout active' : activeDeviceLayout === 'tablet' ? 'tablet layout active' : 'desktop layout active';
        return `${activeLabel} · ${mobileLabel} · ${tabletLabel} · ${Math.round(width)}×${Math.round(height)} ${orientation}`;
    }

    function tabletModeStatusText() {
        return deviceLayoutStatusText();
    }

    function refreshTabletModeUi(panel = document.getElementById(SCRIPT.panelId)) {
        if (!panel) return;
        panel.classList.toggle('mcms-tablet-active', tabletModeActive);
        panel.classList.toggle('mcms-mobile-active', mobileModeActive);
        const tabletSelect = panel.querySelector('[data-setting="tablet-mode"]');
        const mobileSelect = panel.querySelector('[data-setting="mobile-mode"]');
        if (tabletSelect && document.activeElement !== tabletSelect) tabletSelect.value = state.tabletMode;
        if (mobileSelect && document.activeElement !== mobileSelect) mobileSelect.value = state.mobileMode;
        const status = panel.querySelector('[data-device-layout-status], [data-tablet-status]');
        if (status) status.textContent = tabletModeStatusText();
        const dragHandle = panel.querySelector('.mcms-drag-handle');
        const title = panel.querySelector('.mcms-title');
        const subtitle = panel.querySelector('.mcms-subtitle');
        const touchLayout = isTouchLayoutActive();
        const layoutName = mobileModeActive ? 'MOBILE COMMAND PANEL' : tabletModeActive ? 'TABLET COMMAND PANEL' : '☰ DRAG MENU HERE';
        const layoutHelp = mobileModeActive
            ? 'iPhone Safari layout · swipe vertically · close with ×'
            : tabletModeActive
                ? 'Touch-optimised layout · scroll vertically · close with ×'
                : 'Hold left-click on this title area. Position saves.';
        if (dragHandle) dragHandle.title = touchLayout ? `${mobileModeActive ? 'Mobile' : 'Tablet'} Mode uses a fixed responsive panel` : 'Hold left-click and drag this bar to move the menu';
        if (title) title.textContent = layoutName;
        if (subtitle) subtitle.textContent = layoutHelp;
    }

    function clearTabletDockSizing(control = document.getElementById(SCRIPT.controlId)) {
        if (control) {
            control.style.removeProperty('--mcms-tablet-dock-width');
            control.style.removeProperty('--mcms-tablet-filter-columns');
            control.style.removeProperty('--mcms-tablet-pin-columns');
            control.style.removeProperty('--mcms-tablet-filter-height');
            control.style.removeProperty('--mcms-tablet-pin-height');
            control.style.removeProperty('--mcms-mobile-dock-width');
            control.style.removeProperty('--mcms-mobile-columns');
            control.style.removeProperty('--mcms-mobile-pin-columns');
            control.style.removeProperty('--mcms-mobile-filter-height');
            control.style.removeProperty('--mcms-mobile-pin-height');
            delete control.dataset.mcmsTabletFit;
            delete control.dataset.mcmsMobileFit;
        }
        if (tabletDockResizeObserver && tabletDockObservedMap) {
            try { tabletDockResizeObserver.unobserve(tabletDockObservedMap); } catch (err) {}
            tabletDockObservedMap = null;
        }
    }

    function observeTabletMapArea(mapEl) {
        if (!isTouchLayoutActive() || !mapEl) return;
        const ResizeObserverCtor = pageWindow.ResizeObserver;
        if (typeof ResizeObserverCtor !== 'function') return;

        if (!tabletDockResizeObserver) {
            tabletDockResizeObserver = runtimeTrackObserver(new ResizeObserverCtor(entries => {
                if (!isTouchLayoutActive() || runtime.destroyed) return;
                if (entries.some(entry => entry?.target === tabletDockObservedMap)) fitControlToMap();
            }));
        }

        if (tabletDockObservedMap === mapEl) return;
        if (tabletDockObservedMap) {
            try { tabletDockResizeObserver.unobserve(tabletDockObservedMap); } catch (err) {}
        }
        tabletDockObservedMap = mapEl;
        try { tabletDockResizeObserver.observe(mapEl); } catch (err) {}
    }

    function estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns, filterHeight, pinHeight, gap) {
        const filterRows = Math.max(1, Math.ceil(filterCount / Math.max(1, filterColumns)));
        const filterBlockHeight = Math.max(48, (filterRows * filterHeight) + (Math.max(0, filterRows - 1) * gap));
        if (!pinCount) return filterBlockHeight;
        const pinRows = Math.max(1, Math.ceil(pinCount / Math.max(1, pinColumns)));
        return filterBlockHeight + gap + (pinRows * pinHeight) + (Math.max(0, pinRows - 1) * gap);
    }

    function applyTabletDockLayout(mapEl = getLargestLeafletMap()) {
        const control = document.getElementById(SCRIPT.controlId);
        if (!control || !mapEl || !tabletModeActive) {
            clearTabletDockSizing(control);
            return false;
        }

        const rect = mapEl.getBoundingClientRect();
        if (!Number.isFinite(rect.width) || !Number.isFinite(rect.height) || rect.width < 1 || rect.height < 1) return false;

        observeTabletMapArea(mapEl);

        const margin = rect.width < 700 ? 8 : 10;
        const gap = 7;
        const menuWidth = 52;
        const nudgeX = Math.abs(Number(state.nudge?.x) || 0);
        const nudgeY = Math.abs(Number(state.nudge?.y) || 0);
        const viewport = getViewportMetrics();
        const mapWidth = Math.min(rect.width, viewport.width);
        const availableMapWidth = Math.max(1, mapWidth - (margin * 2) - nudgeX);
        const dockWidth = Math.max(1, Math.min(960, availableMapWidth));
        const contentWidth = Math.max(1, dockWidth - menuWidth - gap);

        const filterCount = Math.max(1, control.querySelectorAll('.mcms-floating-filter .mcms-float-btn').length);
        const pinCount = control.querySelectorAll('.mcms-screen-pins .mcms-screen-pin-btn').length;
        const preferredFilterWidth = contentWidth >= 600 ? 92 : 82;
        const preferredPinWidth = contentWidth >= 600 ? 100 : 92;

        let filterColumns = Math.max(1, Math.min(filterCount, Math.floor((contentWidth + gap) / (preferredFilterWidth + gap)) || 1));
        let pinColumns = pinCount
            ? Math.max(1, Math.min(pinCount, Math.floor((contentWidth + gap) / (preferredPinWidth + gap)) || 1))
            : 1;
        let filterHeight = 48;
        let pinHeight = 42;
        const availableMapHeight = Math.max(80, rect.height - (margin * 2) - nudgeY);

        let estimatedHeight = estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns, filterHeight, pinHeight, gap);
        while (estimatedHeight > availableMapHeight && (filterColumns < filterCount || pinColumns < Math.max(1, pinCount))) {
            const filterCandidate = filterColumns < filterCount
                ? estimateTabletDockHeight(filterCount, filterColumns + 1, pinCount, pinColumns, filterHeight, pinHeight, gap)
                : Number.POSITIVE_INFINITY;
            const pinCandidate = pinCount && pinColumns < pinCount
                ? estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns + 1, filterHeight, pinHeight, gap)
                : Number.POSITIVE_INFINITY;

            if (filterCandidate <= pinCandidate) filterColumns += 1;
            else pinColumns += 1;
            estimatedHeight = Math.min(filterCandidate, pinCandidate);
        }

        if (estimatedHeight > availableMapHeight) {
            filterHeight = 46;
            pinHeight = 40;
            estimatedHeight = estimateTabletDockHeight(filterCount, filterColumns, pinCount, pinColumns, filterHeight, pinHeight, gap);
        }

        control.style.setProperty('--mcms-tablet-dock-width', `${Math.floor(dockWidth)}px`);
        control.style.setProperty('--mcms-tablet-filter-columns', String(filterColumns));
        control.style.setProperty('--mcms-tablet-pin-columns', String(pinColumns));
        control.style.setProperty('--mcms-tablet-filter-height', `${filterHeight}px`);
        control.style.setProperty('--mcms-tablet-pin-height', `${pinHeight}px`);
        control.dataset.mcmsTabletFit = `${Math.floor(dockWidth)}:${filterColumns}:${pinColumns}:${Math.round(estimatedHeight)}`;
        return true;
    }

    function estimateMobileDockHeight(commandCount, columns, pinCount, pinColumns, commandHeight, pinHeight, gap) {
        const commandRows = Math.max(1, Math.ceil(commandCount / Math.max(1, columns)));
        const commandBlockHeight = (commandRows * commandHeight) + (Math.max(0, commandRows - 1) * gap);
        if (!pinCount) return commandBlockHeight;
        const pinRows = Math.max(1, Math.ceil(pinCount / Math.max(1, pinColumns)));
        return commandBlockHeight + gap + (pinRows * pinHeight) + (Math.max(0, pinRows - 1) * gap);
    }

    function applyMobileDockLayout(mapEl = getLargestLeafletMap()) {
        const control = document.getElementById(SCRIPT.controlId);
        if (!control || !mapEl || !mobileModeActive) {
            if (!tabletModeActive) clearTabletDockSizing(control);
            return false;
        }

        const rect = mapEl.getBoundingClientRect();
        if (!Number.isFinite(rect.width) || !Number.isFinite(rect.height) || rect.width < 1 || rect.height < 1) return false;
        observeTabletMapArea(mapEl);

        const viewport = getViewportMetrics();
        const margin = rect.width < 500 ? 5 : 7;
        const gap = rect.width < 500 ? 4 : 5;
        const nudgeX = Math.abs(Number(state.nudge?.x) || 0);
        const nudgeY = Math.abs(Number(state.nudge?.y) || 0);
        const mapWidth = Math.min(rect.width, viewport.width);
        const dockWidth = Math.max(1, Math.min(1000, mapWidth - (margin * 2) - nudgeX));
        const commandCount = 1 + Math.max(1, control.querySelectorAll('.mcms-floating-filter .mcms-float-btn').length);
        const pinCount = control.querySelectorAll('.mcms-screen-pins .mcms-screen-pin-btn').length;
        const minCommandWidth = viewport.orientation === 'landscape' ? 68 : 62;
        const maxPortraitColumns = viewport.orientation === 'portrait' ? 5 : commandCount;
        let columns = Math.max(3, Math.min(commandCount, maxPortraitColumns, Math.floor((dockWidth + gap) / (minCommandWidth + gap)) || 3));
        if (viewport.orientation === 'landscape' && dockWidth >= 700) columns = commandCount;
        let pinColumns = pinCount ? Math.max(2, Math.min(pinCount, Math.floor((dockWidth + gap) / (88 + gap)) || 2)) : 1;
        let commandHeight = viewport.orientation === 'landscape' ? 42 : 44;
        let pinHeight = 34;
        const availableMapHeight = Math.max(72, rect.height - (margin * 2) - nudgeY);

        let estimatedHeight = estimateMobileDockHeight(commandCount, columns, pinCount, pinColumns, commandHeight, pinHeight, gap);
        while (estimatedHeight > availableMapHeight && columns < commandCount) {
            columns += 1;
            estimatedHeight = estimateMobileDockHeight(commandCount, columns, pinCount, pinColumns, commandHeight, pinHeight, gap);
        }
        while (estimatedHeight > availableMapHeight && pinCount && pinColumns < pinCount) {
            pinColumns += 1;
            estimatedHeight = estimateMobileDockHeight(commandCount, columns, pinCount, pinColumns, commandHeight, pinHeight, gap);
        }
        if (estimatedHeight > availableMapHeight) {
            commandHeight = 40;
            pinHeight = 31;
            estimatedHeight = estimateMobileDockHeight(commandCount, columns, pinCount, pinColumns, commandHeight, pinHeight, gap);
        }

        control.style.setProperty('--mcms-mobile-dock-width', `${Math.floor(dockWidth)}px`);
        control.style.setProperty('--mcms-mobile-columns', String(columns));
        control.style.setProperty('--mcms-mobile-pin-columns', String(pinColumns));
        control.style.setProperty('--mcms-mobile-filter-height', `${commandHeight}px`);
        control.style.setProperty('--mcms-mobile-pin-height', `${pinHeight}px`);
        control.dataset.mcmsMobileFit = `${Math.floor(dockWidth)}:${columns}:${pinColumns}:${Math.round(estimatedHeight)}`;
        return true;
    }

    function applyTabletPanelPosition() {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel || !panel.classList.contains('mcms-open') || !isTouchLayoutActive()) return false;

        const viewport = getViewportMetrics();
        const mobile = mobileModeActive;
        const margin = mobile ? 4 : (viewport.width < 700 ? 6 : 10);
        const availableWidth = Math.max(1, viewport.width - (margin * 2));
        const availableHeight = Math.max(mobile ? 160 : 180, viewport.height - (margin * 2));
        const desiredWidth = mobile
            ? availableWidth
            : Math.min(availableWidth, viewport.orientation === 'landscape' ? 760 : 700);
        const heightRatio = mobile
            ? (viewport.orientation === 'landscape' ? 0.94 : 0.88)
            : (viewport.orientation === 'landscape' ? 0.88 : 0.82);
        const maxHeight = Math.min(availableHeight, Math.max(mobile ? 220 : 260, viewport.height * heightRatio));
        const left = Math.round(viewport.offsetLeft + Math.max(margin, (viewport.width - desiredWidth) / 2));

        panel.style.setProperty('position', 'fixed', 'important');
        panel.style.setProperty('width', `${Math.round(desiredWidth)}px`, 'important');
        panel.style.setProperty('max-width', `${Math.round(desiredWidth)}px`, 'important');
        panel.style.setProperty('max-height', `${Math.round(maxHeight)}px`, 'important');
        const layoutViewportHeight = Math.max(viewport.height, Number(pageWindow.innerHeight) || Number(document.documentElement.clientHeight) || viewport.height);
        const bottomOffset = Math.round(Math.max(0, layoutViewportHeight - (viewport.offsetTop + viewport.height)) + margin);
        panel.style.setProperty('left', `${left}px`, 'important');
        panel.style.setProperty('right', 'auto', 'important');
        panel.style.setProperty('top', 'auto', 'important');
        panel.style.setProperty('bottom', `${bottomOffset}px`, 'important');
        panel.style.setProperty('transform', 'none', 'important');
        return true;
    }

    function clearTabletPanelSizing(panel = document.getElementById(SCRIPT.panelId)) {
        if (!panel) return;
        panel.style.removeProperty('width');
        panel.style.removeProperty('max-width');
    }

    function scheduleTabletLayoutRefresh(delay = 40) {
        runtimeClearTimeout(tabletLayoutTimer);
        tabletLayoutTimer = runtimeSetTimeout(() => {
            tabletLayoutTimer = null;
            const previousLayout = activeDeviceLayout;
            applyRootAttributes();
            const panel = document.getElementById(SCRIPT.panelId);
            refreshTabletModeUi(panel);
            if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
                clearTabletPanelSizing(panel);
                clearTabletDockSizing();
            }
            fitControlToMap();
            if (panel?.classList.contains('mcms-open')) positionPanelOverlay(true);
        }, Math.max(0, Number(delay) || 0));
    }

    function applyRootAttributes() {
        const root = document.documentElement;
        root.setAttribute('data-mcms-ui-theme', normaliseUiTheme(state.uiTheme));
        root.setAttribute('data-mc-map-skin', state.theme);
        root.setAttribute('data-mcms-clean', String(Boolean(state.cleanMode)));
        root.setAttribute('data-mcms-marker-focus', String(Boolean(state.markerFocus)));
        root.setAttribute('data-mcms-mission-pulse', String(Boolean(state.missionPulse)));
        root.setAttribute('data-mcms-road-priority', String(Boolean(state.roadPriority)));
        root.setAttribute('data-mcms-compact-dock', String(Boolean(state.compactDock)));
        root.setAttribute('data-mcms-command-bar-open', String(state.commandBarOpen !== false));
        activeDeviceLayout = resolveDeviceLayout();
        tabletModeActive = resolveTabletMode(activeDeviceLayout);
        mobileModeActive = resolveMobileMode(activeDeviceLayout);
        const tabletViewport = getViewportMetrics();
        root.setAttribute('data-mcms-device-layout', activeDeviceLayout);
        root.setAttribute('data-mcms-tablet-mode', String(state.tabletMode));
        root.setAttribute('data-mcms-tablet-active', String(Boolean(tabletModeActive)));
        root.setAttribute('data-mcms-mobile-mode', String(state.mobileMode));
        root.setAttribute('data-mcms-mobile-active', String(Boolean(mobileModeActive)));
        root.setAttribute('data-mcms-tablet-orientation', tabletViewport.orientation);
        root.setAttribute('data-mcms-mobile-orientation', tabletViewport.orientation);
        root.setAttribute('data-mcms-show-alliance-missions', String(Boolean(state.visibility.allianceMissions)));
        root.setAttribute('data-mcms-show-my-missions', String(Boolean(state.visibility.myMissions)));
        root.setAttribute('data-mcms-show-vehicles', String(Boolean(state.visibility.vehicles)));
        root.setAttribute('data-mcms-show-buildings', String(Boolean(state.visibility.buildings)));
        root.setAttribute('data-mcms-critical-view', String(Boolean(criticalViewActive)));
    }

    function getStrongMarkerSignal(icon) {
        if (!icon) return { hrefs: [], srcs: [], classes: '', text: '' };

        const hrefs = [];
        const srcs = [];
        const classes = [];
        const texts = [];

        classes.push(icon.className || '');
        texts.push(icon.title || '', icon.alt || '', icon.getAttribute?.('aria-label') || '');

        try {
            const anchor = icon.closest('a') || icon.querySelector('a');
            if (anchor) {
                hrefs.push(anchor.href || '');
                classes.push(anchor.className || '');
                texts.push(anchor.title || '', anchor.getAttribute('aria-label') || '');
            }
        } catch (err) {}

        try {
            const imgs = icon.tagName === 'IMG' ? [icon] : Array.from(icon.querySelectorAll('img'));
            for (const img of imgs) {
                srcs.push(img.src || '');
                classes.push(img.className || '');
                texts.push(img.alt || '', img.title || '', img.getAttribute('aria-label') || '');
            }
        } catch (err) {}

        try {
            if (icon.dataset) texts.push(Object.entries(icon.dataset).map(([key, value]) => `${key}:${value}`).join(' '));
        } catch (err) {}

        return { hrefs, srcs, classes: classes.join(' ').toLowerCase(), text: texts.join(' ').toLowerCase() };
    }

    function pathFromUrl(value) {
        try { return new URL(value, location.href).pathname.toLowerCase(); }
        catch (err) { return String(value || '').toLowerCase(); }
    }

    function classifyMarker(icon) {
        const signal = getStrongMarkerSignal(icon);
        const hrefPaths = signal.hrefs.map(pathFromUrl);
        const srcPaths = signal.srcs.map(pathFromUrl);
        const combined = `${hrefPaths.join(' ')} ${srcPaths.join(' ')} ${signal.classes} ${signal.text}`;

        const hrefSaysVehicle = hrefPaths.some(path => /\/vehicles\/\d+/.test(path) || /\/vehicles\/?$/.test(path));
        const hrefSaysBuilding = hrefPaths.some(path => /\/buildings\/\d+/.test(path) || /\/buildings\/?$/.test(path));
        const hrefSaysMission = hrefPaths.some(path => /\/missions\/\d+/.test(path) || /\/missions\/?$/.test(path));

        if (hrefSaysVehicle) return 'vehicle';
        if (hrefSaysBuilding) return 'building';
        if (hrefSaysMission) return isAllianceMissionSignal(combined) ? 'alliance-mission' : 'my-mission';

        const explicitVehicle = /\bvehicle[_-]?marker\b/.test(combined) || /\bvehicle[_-]?icon\b/.test(combined) || /\bvehicle[_-]?id\b/.test(combined) || combined.includes('/vehicle_graphic_images/') || combined.includes('/vehicle_images/') || combined.includes('/vehicles/');
        const explicitBuilding = /\bbuilding[_-]?marker\b/.test(combined) || /\bbuilding[_-]?icon\b/.test(combined) || /\bbuilding[_-]?id\b/.test(combined) || combined.includes('/building_icons/') || combined.includes('/buildings/');
        const explicitMission = /\bmission[_-]?marker\b/.test(combined) || /\bmission[_-]?icon\b/.test(combined) || /\bmission[_-]?id\b/.test(combined) || combined.includes('/missions/');

        if (explicitVehicle && !explicitMission && !explicitBuilding) return 'vehicle';
        if (explicitBuilding && !explicitMission && !explicitVehicle) return 'building';
        if (explicitMission && !explicitVehicle && !explicitBuilding) return isAllianceMissionSignal(combined) ? 'alliance-mission' : 'my-mission';

        return 'unknown';
    }

    function isAllianceMissionSignal(signal) {
        return signal.includes('alliance') || signal.includes('shared_mission') || signal.includes('alliance_mission') || signal.includes('verband') || signal.includes('verbandseinsatz') || signal.includes('association');
    }

    function getMissionMarkerLayers() {
        return getCachedRegistry('mission_markers');
    }

    function normaliseMissionId(value) {
        if (value === undefined || value === null || value === '') return null;
        return String(value);
    }

    function parseCreditValue(value) {
        if (typeof value === 'number' && Number.isFinite(value)) return Math.max(0, Math.round(value));
        const raw = String(value ?? '').trim();
        if (!raw) return null;

        const compactMatch = raw.match(/(-?[\d.,]+)\s*([km])\b/i);
        if (compactMatch) {
            const numeric = Number(compactMatch[1].replaceAll(',', ''));
            if (Number.isFinite(numeric)) return Math.max(0, Math.round(numeric * (compactMatch[2].toLowerCase() === 'm' ? 1000000 : 1000)));
        }

        const match = raw.match(/-?\d[\d\s.,]*/);
        if (!match) return null;
        const digits = match[0].replace(/\D/g, '');
        if (!digits) return null;
        const numeric = Number(digits);
        return Number.isFinite(numeric) ? Math.max(0, Math.round(numeric)) : null;
    }

    function parseMissionTimestamp(value) {
        if (value instanceof Date) {
            const timestamp = value.getTime();
            return Number.isFinite(timestamp) && timestamp > 0 ? timestamp : null;
        }

        if (typeof value === 'number' && Number.isFinite(value)) {
            if (value <= 0) return null;
            return value < 100000000000 ? Math.round(value * 1000) : Math.round(value);
        }

        const raw = String(value ?? '').trim();
        if (!raw) return null;
        if (/^\d+(?:\.\d+)?$/.test(raw)) return parseMissionTimestamp(Number(raw));

        const parsed = Date.parse(raw);
        return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    }

    function captureMissionMarkerData(payload) {
        if (!payload) return;
        if (Array.isArray(payload)) {
            payload.forEach(captureMissionMarkerData);
            return;
        }
        if (typeof payload !== 'object') return;

        const candidates = [payload, payload.params, payload.mission, payload.data].filter(item => item && typeof item === 'object');
        for (const item of candidates) {
            const missionId = normaliseMissionId(item.id ?? item.mission_id ?? item.missionId);
            if (missionId === null) continue;

            const existing = missionOverlayData.get(missionId) || {};
            const credits = parseCreditValue(item.average_credits ?? item.averageCredits ?? item.average_credit);
            const createdAt = parseMissionTimestamp(item.created_at ?? item.createdAt ?? item.date_created ?? item.dateCreated);
            const allianceSharedAt = parseMissionTimestamp(item.alliance_shared_at ?? item.allianceSharedAt ?? item.shared_at ?? item.sharedAt);
            const userId = item.user_id ?? item.userId;
            const allianceId = item.alliance_id ?? item.allianceId;
            const rawVehicleState = item.vehicle_state ?? item.vehicleState;
            const vehicleState = Number(rawVehicleState);
            const missingText = item.missing_text ?? item.missingText ?? item.missing_text_short ?? item.missingTextShort;
            const normalisedMissingText = normaliseMissingRequirementText(missingText);
            const patientsCount = Number(item.patients_count ?? item.patientsCount);
            const possiblePatientsCount = Number(item.possible_patients_count ?? item.possiblePatientsCount);
            const prisonersCount = Number(item.prisoners_count ?? item.prisonersCount);
            const possiblePrisonersCount = Number(item.possible_prisoners_count ?? item.possiblePrisonersCount);
            const liveCurrentValue = Number(item.live_current_value ?? item.liveCurrentValue ?? item.current_value ?? item.currentValue);

            missionOverlayData.set(missionId, {
                ...existing,
                ...(credits !== null ? { averageCredits: credits } : {}),
                ...(createdAt !== null ? { createdAt } : {}),
                ...(allianceSharedAt !== null ? { allianceSharedAt } : {}),
                ...(userId !== undefined && userId !== null ? { userId: String(userId) } : {}),
                ...(allianceId !== undefined ? { allianceId } : {}),
                ...(Number.isFinite(vehicleState) ? { vehicleState } : {}),
                ...(normalisedMissingText ? { missingText: normalisedMissingText } : {}),
                ...(Number.isFinite(patientsCount) ? { patientsCount } : {}),
                ...(Number.isFinite(possiblePatientsCount) ? { possiblePatientsCount } : {}),
                ...(Number.isFinite(prisonersCount) ? { prisonersCount } : {}),
                ...(Number.isFinite(possiblePrisonersCount) ? { possiblePrisonersCount } : {}),
                ...(Number.isFinite(liveCurrentValue) ? { liveCurrentValue } : {}),
                ...(item.caption ? { caption: String(item.caption) } : {})
            });
        }
    }

    function readBalancedObject(source, startIndex) {
        if (source[startIndex] !== '{') return null;
        let depth = 0;
        let quote = '';
        let escaped = false;

        for (let index = startIndex; index < source.length; index += 1) {
            const char = source[index];
            if (quote) {
                if (escaped) escaped = false;
                else if (char === '\\') escaped = true;
                else if (char === quote) quote = '';
                continue;
            }
            if (char === '"' || char === "'") { quote = char; continue; }
            if (char === '{') depth += 1;
            else if (char === '}') {
                depth -= 1;
                if (depth === 0) return source.slice(startIndex, index + 1);
            }
        }
        return null;
    }

    function scanInlineMissionMarkerData() {
        if (inlineMissionDataScanned) return;
        inlineMissionDataScanned = true;

        for (const script of document.scripts) {
            const source = script.textContent || '';
            if (!source.includes('missionMarkerAdd')) continue;
            const matcher = /missionMarkerAdd\s*\(/g;
            let match;
            while ((match = matcher.exec(source))) {
                let cursor = matcher.lastIndex;
                while (/\s/.test(source[cursor] || '')) cursor += 1;
                if (source[cursor] !== '{') continue;
                const objectText = readBalancedObject(source, cursor);
                if (!objectText) continue;
                try { captureMissionMarkerData(JSON.parse(objectText)); } catch (err) {}
                matcher.lastIndex = cursor + objectText.length;
            }
        }
    }

    function installMissionMarkerAddHook() {
        let current;
        try { current = pageWindow.missionMarkerAdd; } catch (err) { return false; }
        if (typeof current !== 'function') return false;
        if (current.__mcmsMissionOverlaysWrappedV313) return true;

        const original = current.__mcmsOriginal || current;
        const wrapped = function (...args) {
            args.forEach(captureMissionMarkerData);
            const result = original.apply(this, args);
            invalidateMarkerRegistryCaches('mission');
            handleMissionSpawnArguments(args);
            scheduleEnabledMapRefreshes({ includeSnapshots: true, positionPanel: false });
            return result;
        };

        try {
            Object.defineProperty(wrapped, '__mcmsMissionOverlaysWrappedV313', { value: true });
            Object.defineProperty(wrapped, '__mcmsOriginal', { value: original });
            pageWindow.missionMarkerAdd = wrapped;
            if (pageWindow.missionMarkerAdd !== wrapped) return false;
            runtime.hookRestorers.push(() => {
                try {
                    if (pageWindow.missionMarkerAdd === wrapped) pageWindow.missionMarkerAdd = original;
                } catch (err) {}
            });
            return true;
        } catch (err) {
            return false;
        }
    }

    function exactCreditFromObject(source) {
        if (!source || typeof source !== 'object') return null;
        const direct = parseCreditValue(source.average_credits ?? source.averageCredits ?? source.average_credit);
        if (direct !== null) return direct;
        for (const key of ['options', 'params', 'mission', 'data', 'missionData', '_missionData']) {
            const nested = source[key];
            if (!nested || typeof nested !== 'object') continue;
            const value = parseCreditValue(nested.average_credits ?? nested.averageCredits ?? nested.average_credit);
            if (value !== null) return value;
        }
        return null;
    }

    function creditsFromMissionPanel(missionId) {
        const panel = document.getElementById(`mission_${missionId}`);
        if (!panel) return null;

        const selectors = [
            '[average_credits]', '[average-credits]', '[data-average-credits]',
            '[data-average_credits]', '[data-average-credit]', '[data-mission-credits]'
        ];
        const nodes = [panel, ...panel.querySelectorAll(selectors.join(','))];
        const attributes = ['average_credits', 'average-credits', 'data-average-credits', 'data-average_credits', 'data-average-credit', 'data-mission-credits'];

        for (const node of nodes) {
            for (const attribute of attributes) {
                const value = parseCreditValue(node.getAttribute?.(attribute));
                if (value !== null) return value;
            }
        }

        for (const node of panel.querySelectorAll('span, small, .label, .badge')) {
            const text = String(node.textContent || '').trim();
            if (!/[≈~]/.test(text)) continue;
            const match = text.match(/[≈~]\s*([\d][\d.,\s]*(?:[kKmM])?)/);
            const value = parseCreditValue(match?.[1]);
            if (value !== null) return value;
        }

        return null;
    }

    function getMissionAverageCredits(marker, missionId) {
        const cached = missionOverlayData.get(missionId);
        if (cached && Number.isFinite(cached.averageCredits)) return cached.averageCredits;

        const markerCredits = exactCreditFromObject(marker);
        if (markerCredits !== null) {
            missionOverlayData.set(missionId, { ...(cached || {}), averageCredits: markerCredits });
            return markerCredits;
        }

        const panelCredits = creditsFromMissionPanel(missionId);
        if (panelCredits !== null) {
            missionOverlayData.set(missionId, { ...(cached || {}), averageCredits: panelCredits });
            return panelCredits;
        }

        return null;
    }

    function missionOwnerId(marker, missionId) {
        const cached = missionOverlayData.get(missionId);
        return marker?.user_id ?? marker?.userId ?? marker?.options?.user_id ?? marker?.options?.userId ?? cached?.userId ?? null;
    }

    function currentMissionUserId() {
        return currentUserIdCached();
    }

    function isAllianceMissionLayer(marker, missionId) {
        const currentUserId = currentMissionUserId();
        const ownerId = missionOwnerId(marker, missionId);

        if (currentUserId !== null && ownerId !== undefined && ownerId !== null && ownerId !== '') {
            return String(ownerId) !== currentUserId;
        }

        return Boolean(marker?._icon?.classList?.contains('mcms-marker-alliance-mission'));
    }

    function isPersonalMissionLayer(marker, missionId) {
        const currentUserId = currentMissionUserId();
        const ownerId = missionOwnerId(marker, missionId);

        if (currentUserId !== null && ownerId !== undefined && ownerId !== null && ownerId !== '') {
            return String(ownerId) === currentUserId;
        }

        return Boolean(marker?._icon?.classList?.contains('mcms-marker-my-mission'));
    }

    function formatAllianceCredits(value) {
        const credits = Math.max(0, Math.round(Number(value) || 0));
        const trim = number => String(number).replace(/\.0+$|(\.\d*[1-9])0+$/, '$1');

        if (credits < 1000) return String(credits);
        if (credits < 10000) return `${trim((credits / 1000).toFixed(credits % 1000 === 0 ? 0 : 2))}k`;
        if (credits < 999500) return `${trim((credits / 1000).toFixed(credits % 1000 === 0 ? 0 : 1))}k`;
        return `${trim((credits / 1000000).toFixed(credits % 1000000 === 0 ? 0 : credits < 10000000 ? 2 : 1))}m`;
    }

    function ensureMissionFloatPane(map) {
        if (!map || typeof map.getPane !== 'function' || typeof map.createPane !== 'function') return null;

        let pane = null;
        try { pane = map.getPane(MISSION_OVERLAY_PANE); } catch (err) {}
        if (!pane) {
            try { pane = map.createPane(MISSION_OVERLAY_PANE); } catch (err) { pane = null; }
        }
        if (!pane) return null;

        pane.classList.add('mcms-mission-float-pane');
        pane.style.setProperty('z-index', '750');
        pane.style.setProperty('pointer-events', 'none');
        pane.style.setProperty('touch-action', 'none');
        return MISSION_OVERLAY_PANE;
    }

    function clearAllianceCreditLabels() {
        if (allianceCreditGroup) {
            try { allianceCreditGroup.clearLayers(); allianceCreditGroup.remove(); } catch (err) {}
        }
        allianceCreditLabels.clear();
        allianceCreditGroup = null;
    }

    function missionVehicleStateFromObject(source) {
        if (!source || typeof source !== 'object') return null;
        const containers = [source, source.options, source.params, source.mission, source.data, source.missionData, source._missionData]
            .filter(item => item && typeof item === 'object');

        for (const item of containers) {
            const value = Number(item.vehicle_state ?? item.vehicleState);
            if (Number.isFinite(value)) return value;
        }
        return null;
    }

    function vehicleAssignedMissionId(vehicle) {
        if (!vehicle || typeof vehicle !== 'object') return null;
        const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
            .filter(item => item && typeof item === 'object');
        const keys = ['mission_id', 'missionId', 'target_mission_id', 'targetMissionId'];

        for (const item of containers) {
            const targetType = String(item.target_type ?? item.targetType ?? '').toLowerCase();
            if (targetType === 'mission') {
                const targetMissionId = normaliseMissionId(item.target_id ?? item.targetId);
                if (targetMissionId !== null && targetMissionId !== '0') return targetMissionId;
            }
            for (const key of keys) {
                const missionId = normaliseMissionId(item[key]);
                if (missionId !== null && missionId !== '0') return missionId;
            }
        }
        return null;
    }

    function vehicleOwnerId(vehicle) {
        if (!vehicle || typeof vehicle !== 'object') return null;
        const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
            .filter(item => item && typeof item === 'object');

        for (const item of containers) {
            const value = item.user_id ?? item.userId ?? item.owner_id ?? item.ownerId;
            if (value !== undefined && value !== null && value !== '') return String(value);
        }
        return null;
    }

    function vehicleRecordId(vehicle) {
        if (!vehicle || typeof vehicle !== 'object') return null;
        const containers = [vehicle, vehicle.options, vehicle.params, vehicle.vehicle, vehicle.data, vehicle.vehicleData, vehicle._vehicleData]
            .filter(item => item && typeof item === 'object');
        for (const item of containers) {
            const value = item.id ?? item.vehicle_id ?? item.vehicleId;
            if (value !== undefined && value !== null && value !== '') return String(value);
        }
        return null;
    }

    function normaliseVehicleApiPayload(payload) {
        if (Array.isArray(payload)) return payload.filter(item => item && typeof item === 'object');
        if (Array.isArray(payload?.result)) return payload.result.filter(item => item && typeof item === 'object');
        if (payload && typeof payload === 'object') return Object.values(payload).filter(item => item && typeof item === 'object');
        return [];
    }

    function getPersonalVehicleRecords() {
        if (vehicleApiReady) return Array.from(personalVehicleApiCache.values());

        const merged = new Map(personalVehicleApiCache);
        const currentUserId = currentMissionUserId();
        for (const vehicle of getVehicleMarkerLayers()) {
            const ownerId = vehicleOwnerId(vehicle);
            if (currentUserId !== null && ownerId !== null && ownerId !== currentUserId) continue;
            const id = vehicleRecordId(vehicle) || `marker:${vehicle?._leaflet_id ?? merged.size}`;
            if (!merged.has(id)) merged.set(id, vehicle);
        }
        return Array.from(merged.values());
    }

    function invalidateMissionCommitmentIndex() {
        missionCommitmentIndexDirty = true;
    }

    function rebuildMissionCommitmentIndex() {
        if (!missionCommitmentIndexDirty) return missionCommitmentIndex;

        missionCommitmentIndex.clear();
        const seenVehicles = new Set();
        const currentUserId = currentMissionUserId();

        for (const vehicle of getPersonalVehicleRecords()) {
            const missionId = vehicleAssignedMissionId(vehicle);
            if (missionId === null) continue;

            if (!vehicleApiReady) {
                const ownerId = vehicleOwnerId(vehicle);
                if (currentUserId !== null && ownerId !== null && ownerId !== currentUserId) continue;
            }

            const vehicleId = vehicleRecordId(vehicle) || `anon:${seenVehicles.size}`;
            if (seenVehicles.has(vehicleId)) continue;
            seenVehicles.add(vehicleId);

            let commitment = missionCommitmentIndex.get(missionId);
            if (!commitment) {
                commitment = { total: 0, onScene: 0, travelling: 0 };
                missionCommitmentIndex.set(missionId, commitment);
            }

            commitment.total += 1;
            if (vehicleStatusCode(vehicle) === 4) commitment.onScene += 1;
            else commitment.travelling += 1;
        }

        missionCommitmentIndexDirty = false;
        return missionCommitmentIndex;
    }

    function refreshPersonalVehicleData(force = false) {
        const now = Date.now();
        if (vehicleApiFetchPromise) return vehicleApiFetchPromise;
        if (!force && vehicleApiLastError && now - vehicleApiLastError < VEHICLE_API_ERROR_BACKOFF_MS) return Promise.resolve(false);
        if (!force && vehicleApiReady && now - vehicleApiLastFetch < VEHICLE_API_MIN_REFRESH_MS) return Promise.resolve(true);

        vehicleApiFetchPromise = runtimeFetch(new URL('/api/vehicles', pageWindow.location.origin), {
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'application/json' }
        })
            .then(response => {
                if (!response.ok) throw new Error(`Vehicle API ${response.status}`);
                return response.json();
            })
            .then(payload => {
                const records = normaliseVehicleApiPayload(payload);
                const next = new Map();
                for (const vehicle of records) {
                    const id = vehicleRecordId(vehicle);
                    if (id !== null) next.set(id, vehicle);
                }
                personalVehicleApiCache.clear();
                for (const [id, vehicle] of next) personalVehicleApiCache.set(id, vehicle);
                vehicleApiReady = true;
                vehicleApiLastFetch = Date.now();
                vehicleApiLastError = 0;
                vehicleDataRevision += 1;
                invalidateMarkerRegistryCaches('vehicle');
                invalidateMissionCommitmentIndex();
                rebuildMissionCommitmentIndex();
                resourceGapAnalysisCache.clear();
                resourceGapVehicleContextCache.key = '';
                if (state.unitCommitment) scheduleUnitCommitmentRefresh(280);
                scheduleMissionSnapshotRefresh(650);
                if (state.resourceGap.enabled) scheduleResourceGapRefresh(520);
                if (operationalUiIsVisible()) scheduleOperationalPanelsRender(750);
                if (criticalViewActive) runtimeSetTimeout(() => { applyCriticalViewFilter(); fitCriticalMissions(); }, 320);
                return true;
            })
            .catch(() => {
                vehicleApiLastError = Date.now();
                return false;
            })
            .finally(() => { vehicleApiFetchPromise = null; });

        return vehicleApiFetchPromise;
    }

    function captureRadioVehicleMessage(message) {
        if (!message || typeof message !== 'object' || message.type !== 'vehicle_fms') return;
        const currentUserId = currentMissionUserId();
        if (currentUserId !== null && message.user_id !== undefined && String(message.user_id) !== currentUserId) return;
        const id = vehicleRecordId(message);
        if (id === null) return;

        const existing = personalVehicleApiCache.get(id) || {};
        const targetType = Number(message.target_building_id) > 0 ? 'building' : Number(message.mission_id) > 0 ? 'mission' : null;
        const targetId = targetType === 'building' ? message.target_building_id : targetType === 'mission' ? message.mission_id : null;
        personalVehicleApiCache.set(id, {
            ...existing,
            id: Number.isFinite(Number(message.id)) ? Number(message.id) : message.id,
            caption: message.caption ?? existing.caption,
            fms_real: Number.isFinite(Number(message.fms_real)) ? Number(message.fms_real) : existing.fms_real,
            fms_show: Number.isFinite(Number(message.fms)) ? Number(message.fms) : existing.fms_show,
            target_type: targetType,
            target_id: targetId
        });
        vehicleDataRevision += 1;
        invalidateMarkerRegistryCaches('vehicle');
        invalidateMissionCommitmentIndex();
        resourceGapAnalysisCache.clear();
        resourceGapVehicleContextCache.key = '';
        if (state.unitCommitment) scheduleUnitCommitmentRefresh(500);
        scheduleMissionSnapshotRefresh(850);
        if (state.resourceGap.enabled) scheduleResourceGapRefresh(900);
        if (operationalUiIsVisible()) scheduleOperationalPanelsRender(1000);
    }

    function installRadioMessageHook() {
        let current;
        try { current = pageWindow.radioMessage; } catch (err) { return false; }
        if (typeof current !== 'function') return false;
        if (current.__mcmsVehicleDataWrappedV313) return true;

        const original = current.__mcmsOriginal || current;
        const wrapped = function (...args) {
            for (const arg of args) captureRadioVehicleMessage(arg);
            return original.apply(this, args);
        };
        try {
            Object.defineProperty(wrapped, '__mcmsVehicleDataWrappedV313', { value: true });
            Object.defineProperty(wrapped, '__mcmsOriginal', { value: original });
            pageWindow.radioMessage = wrapped;
            if (pageWindow.radioMessage !== wrapped) return false;
            runtime.hookRestorers.push(() => {
                try {
                    if (pageWindow.radioMessage === wrapped) pageWindow.radioMessage = original;
                } catch (err) {}
            });
            return true;
        } catch (err) {
            return false;
        }
    }

    function missionPersonalUnitState(marker, missionId) {
        const commitment = personalUnitCommitmentForMission(missionId);
        if (commitment.total > 0) return { hasUnit: true, known: true, commitment };
        if (commitment.known) return { hasUnit: false, known: true, commitment };

        const markerState = missionVehicleStateFromObject(marker);
        if (markerState !== null) return { hasUnit: markerState > 0, known: true, commitment };

        const cached = missionOverlayData.get(missionId);
        if (Number.isFinite(Number(cached?.vehicleState))) {
            return { hasUnit: Number(cached.vehicleState) > 0, known: true, commitment };
        }

        return { hasUnit: false, known: false, commitment };
    }

    function missionHasPersonalUnit(marker, missionId) {
        return missionPersonalUnitState(marker, missionId).hasUnit;
    }

    function makeAllianceCreditIcon(credits, qualified) {
        const statusClass = qualified ? 'mcms-credit-qualified' : 'mcms-credit-unqualified';
        return pageWindow.L.divIcon({
            className: 'mcms-alliance-credit-icon',
            html: `<span class="mcms-alliance-credit-badge ${statusClass}">≈ ${escapeHtml(formatAllianceCredits(credits))}</span>`,
            iconSize: [0, 0],
            iconAnchor: [0, 18]
        });
    }

    function updateAllianceCreditLabels() {
        if (!state.allianceCredits || !state.visibility.allianceMissions) {
            clearAllianceCreditLabels();
            return;
        }

        scanInlineMissionMarkerData();
        installMissionMarkerAddHook();

        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L || typeof pageWindow.L.layerGroup !== 'function' || typeof pageWindow.L.marker !== 'function' || typeof pageWindow.L.divIcon !== 'function') {
            clearAllianceCreditLabels();
            return;
        }
        const floatPane = ensureMissionFloatPane(map);
        if (!floatPane) {
            clearAllianceCreditLabels();
            return;
        }

        try {
            if (!allianceCreditGroup || allianceCreditGroup._map !== map) {
                clearAllianceCreditLabels();
                allianceCreditGroup = pageWindow.L.layerGroup();
                allianceCreditGroup.__mcmsAllianceCreditLayer = true;
                allianceCreditGroup.addTo(map);
            }
            const activeMissionIds = new Set();

            for (const marker of getMissionMarkerLayers()) {
                const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
                if (missionId === null || !isAllianceMissionLayer(marker, missionId)) continue;

                let latLng;
                try { latLng = marker.getLatLng?.(); } catch (err) { latLng = null; }
                if (!latLng) continue;

                try {
                    const isOnMap = typeof map.hasLayer === 'function' ? map.hasLayer(marker) : Boolean(marker._map);
                    if (!isOnMap) continue;
                } catch (err) {}

                const credits = getMissionAverageCredits(marker, missionId);
                if (credits === null || credits < state.allianceCreditMinimum) continue;
                const qualified = missionHasPersonalUnit(marker, missionId);
                activeMissionIds.add(missionId);

                let label = allianceCreditLabels.get(missionId);
                if (!label) {
                    label = pageWindow.L.marker(latLng, {
                        interactive: false,
                        keyboard: false,
                        bubblingMouseEvents: false,
                        pane: floatPane,
                        zIndexOffset: 0,
                        icon: makeAllianceCreditIcon(credits, qualified)
                    });
                    label.__mcmsAllianceCreditLabel = true;
                    label.__mcmsAllianceCreditValue = credits;
                    label.__mcmsAllianceCreditQualified = qualified;
                    label.addTo(allianceCreditGroup);
                    allianceCreditLabels.set(missionId, label);
                    continue;
                }

                try { label.setLatLng(latLng); } catch (err) {}
                if (label.__mcmsAllianceCreditValue !== credits || label.__mcmsAllianceCreditQualified !== qualified) {
                    label.__mcmsAllianceCreditValue = credits;
                    label.__mcmsAllianceCreditQualified = qualified;
                    try { label.setIcon(makeAllianceCreditIcon(credits, qualified)); } catch (err) {}
                }
            }

            for (const [missionId, label] of Array.from(allianceCreditLabels.entries())) {
                if (activeMissionIds.has(missionId)) continue;
                allianceCreditLabels.delete(missionId);
                try { allianceCreditGroup.removeLayer(label); } catch (err) {}
            }
        } catch (err) {
            clearAllianceCreditLabels();
        }
    }

    function scheduleAllianceCreditRefresh(delay = 220) {
        runtimeClearTimeout(allianceCreditTimer);
        allianceCreditTimer = runtimeSetTimeout(updateAllianceCreditLabels, delay);
    }

    function exactMissionTimestampFromObject(source) {
        if (!source || typeof source !== 'object') return null;
        const direct = parseMissionTimestamp(source.created_at ?? source.createdAt ?? source.date_created ?? source.dateCreated);
        if (direct !== null) return direct;

        for (const key of ['options', 'params', 'mission', 'data', 'missionData', '_missionData']) {
            const nested = source[key];
            if (!nested || typeof nested !== 'object') continue;
            const value = parseMissionTimestamp(nested.created_at ?? nested.createdAt ?? nested.date_created ?? nested.dateCreated);
            if (value !== null) return value;
        }
        return null;
    }

    function timestampFromMissionPanel(missionId) {
        const panel = document.getElementById(`mission_${missionId}`);
        if (!panel) return null;

        const attributes = [
            'created_at', 'created-at', 'data-created-at', 'data-created_at',
            'mission-created-at', 'data-mission-created-at'
        ];
        const selectors = attributes.map(attribute => `[${attribute}]`).join(',');
        const nodes = [panel, ...panel.querySelectorAll(selectors)];

        for (const node of nodes) {
            for (const attribute of attributes) {
                const value = parseMissionTimestamp(node.getAttribute?.(attribute));
                if (value !== null) return value;
            }
        }
        return null;
    }

    function getMissionCreatedAt(marker, missionId) {
        const cached = missionOverlayData.get(missionId);
        if (cached && Number.isFinite(cached.createdAt)) return cached.createdAt;

        const markerTimestamp = exactMissionTimestampFromObject(marker);
        if (markerTimestamp !== null) {
            missionOverlayData.set(missionId, { ...(cached || {}), createdAt: markerTimestamp });
            return markerTimestamp;
        }

        const panelTimestamp = timestampFromMissionPanel(missionId);
        if (panelTimestamp !== null) {
            missionOverlayData.set(missionId, { ...(cached || {}), createdAt: panelTimestamp });
            return panelTimestamp;
        }

        return null;
    }

    function formatMissionAge(createdAt, now = Date.now()) {
        const ageMs = Math.max(0, now - createdAt);
        const totalHours = Math.floor(ageMs / (60 * 60 * 1000));
        const days = Math.floor(totalHours / 24);
        const hours = totalHours % 24;
        if (days > 0) return `${days}D ${hours}H`;
        return totalHours > 0 ? `${totalHours}H` : '<1H';
    }

    function clearMissionAgeLabels() {
        if (missionAgeGroup) {
            try { missionAgeGroup.clearLayers(); missionAgeGroup.remove(); } catch (err) {}
        }
        missionAgeLabels.clear();
        missionAgeGroup = null;
    }

    function makeMissionAgeIcon(ageText, severity = missionAgeSeverity(0)) {
        const severityClass = severity?.className || 'mcms-age-recent';
        const severityLabel = severity?.label || 'RECENT';
        return pageWindow.L.divIcon({
            className: 'mcms-mission-age-icon',
            html: `<span class="mcms-mission-age-badge ${severityClass}" aria-label="${escapeHtml(`${ageText} · ${severityLabel}`)}">${escapeHtml(ageText)}</span>`,
            iconSize: [0, 0],
            iconAnchor: [0, 18]
        });
    }

    function updateMissionAgeLabels() {
        if (!state.missionAge || !state.visibility.myMissions) {
            clearMissionAgeLabels();
            return;
        }

        scanInlineMissionMarkerData();
        installMissionMarkerAddHook();

        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L || typeof pageWindow.L.layerGroup !== 'function' || typeof pageWindow.L.marker !== 'function' || typeof pageWindow.L.divIcon !== 'function') {
            clearMissionAgeLabels();
            return;
        }
        const floatPane = ensureMissionFloatPane(map);
        if (!floatPane) {
            clearMissionAgeLabels();
            return;
        }

        try {
            if (!missionAgeGroup || missionAgeGroup._map !== map) {
                clearMissionAgeLabels();
                missionAgeGroup = pageWindow.L.layerGroup();
                missionAgeGroup.__mcmsMissionAgeLayer = true;
                missionAgeGroup.addTo(map);
            }

            const activeMissionIds = new Set();
            const now = Date.now();

            for (const marker of getMissionMarkerLayers()) {
                const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
                if (missionId === null || !isPersonalMissionLayer(marker, missionId)) continue;

                let latLng;
                try { latLng = marker.getLatLng?.(); } catch (err) { latLng = null; }
                if (!latLng) continue;

                try {
                    const isOnMap = typeof map.hasLayer === 'function' ? map.hasLayer(marker) : Boolean(marker._map);
                    if (!isOnMap) continue;
                } catch (err) {}

                const createdAt = getMissionCreatedAt(marker, missionId);
                if (createdAt === null) continue;
                if (criticalViewActive && (now - createdAt) < CRITICAL_VIEW_MIN_AGE_MS) continue;

                const ageMs = Math.max(0, now - createdAt);
                const ageText = formatMissionAge(createdAt, now);
                const severity = missionAgeSeverity(ageMs);
                activeMissionIds.add(missionId);

                let label = missionAgeLabels.get(missionId);
                if (!label) {
                    label = pageWindow.L.marker(latLng, {
                        interactive: false,
                        keyboard: false,
                        bubblingMouseEvents: false,
                        pane: floatPane,
                        zIndexOffset: 0,
                        icon: makeMissionAgeIcon(ageText, severity)
                    });
                    label.__mcmsMissionAgeLabel = true;
                    label.__mcmsMissionAgeText = ageText;
                    label.__mcmsMissionAgeSeverityRank = severity.rank;
                    label.addTo(missionAgeGroup);
                    missionAgeLabels.set(missionId, label);
                    continue;
                }

                try { label.setLatLng(latLng); } catch (err) {}
                if (label.__mcmsMissionAgeText !== ageText || label.__mcmsMissionAgeSeverityRank !== severity.rank) {
                    label.__mcmsMissionAgeText = ageText;
                    label.__mcmsMissionAgeSeverityRank = severity.rank;
                    try { label.setIcon(makeMissionAgeIcon(ageText, severity)); } catch (err) {}
                }
            }

            for (const [missionId, label] of Array.from(missionAgeLabels.entries())) {
                if (activeMissionIds.has(missionId)) continue;
                missionAgeLabels.delete(missionId);
                try { missionAgeGroup.removeLayer(label); } catch (err) {}
            }
        } catch (err) {
            clearMissionAgeLabels();
        }
    }

    function scheduleMissionAgeRefresh(delay = 220) {
        runtimeClearTimeout(missionAgeTimer);
        missionAgeTimer = runtimeSetTimeout(updateMissionAgeLabels, delay);
    }

    function missionAgeSeverity(ageMs) {
        const age = Math.max(0, Number(ageMs) || 0);
        if (age >= 24 * 60 * 60 * 1000) return { rank: 3, label: '24H+ CRITICAL', className: 'mcms-age-critical' };
        if (age >= 16 * 60 * 60 * 1000) return { rank: 2, label: '16H+ HIGH', className: 'mcms-age-high' };
        if (age >= CRITICAL_VIEW_MIN_AGE_MS) return { rank: 1, label: '8H+ AGED', className: 'mcms-age-aged' };
        return { rank: 0, label: 'RECENT', className: 'mcms-age-recent' };
    }

    function personalMissionAgeRecord(marker, missionId, now = Date.now()) {
        if (!marker || missionId === null || !isPersonalMissionLayer(marker, missionId)) return null;
        const createdAt = getMissionCreatedAt(marker, missionId);
        if (createdAt === null) return null;
        const ageMs = Math.max(0, now - createdAt);
        return { createdAt, ageMs, severity: missionAgeSeverity(ageMs) };
    }

    function clearUnitCommitmentLabels() {
        if (unitCommitmentGroup) {
            try { unitCommitmentGroup.clearLayers(); unitCommitmentGroup.remove(); } catch (err) {}
        }
        unitCommitmentLabels.clear();
        unitCommitmentGroup = null;
    }

    function unitCommitmentAnchor(marker, missionId) {
        const personal = isPersonalMissionLayer(marker, missionId);
        let rowsAbove = 0;
        if (personal) {
            if (state.missionAge) rowsAbove += 1;
        } else if (state.allianceCredits) rowsAbove += 1;
        return 18 + (rowsAbove * 20);
    }

    function makeUnitCommitmentIcon(commitment, personal, anchor) {
        const text = commitment.onScene && commitment.travelling
            ? `${commitment.onScene}✓ ${commitment.travelling}→`
            : commitment.onScene ? `${commitment.onScene}✓` : commitment.travelling ? `${commitment.travelling}→` : `U ${commitment.total}`;
        return pageWindow.L.divIcon({
            className: 'mcms-unit-commitment-icon',
            html: `<span class="mcms-unit-commitment-badge ${personal ? 'mcms-unit-personal' : 'mcms-unit-alliance'}">${escapeHtml(text)}</span>`,
            iconSize: [0, 0], iconAnchor: [0, anchor]
        });
    }

    function updateUnitCommitmentLabels() {
        if (!state.unitCommitment) { clearUnitCommitmentLabels(); return; }
        if (!vehicleApiReady || Date.now() - vehicleApiLastFetch >= VEHICLE_API_REFRESH_MS) refreshPersonalVehicleData(false);
        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L || typeof pageWindow.L.layerGroup !== 'function' || typeof pageWindow.L.marker !== 'function' || typeof pageWindow.L.divIcon !== 'function') {
            clearUnitCommitmentLabels(); return;
        }
        const floatPane = ensureMissionFloatPane(map);
        if (!floatPane) { clearUnitCommitmentLabels(); return; }
        try {
            if (!unitCommitmentGroup || unitCommitmentGroup._map !== map) {
                clearUnitCommitmentLabels();
                unitCommitmentGroup = pageWindow.L.layerGroup();
                unitCommitmentGroup.__mcmsUnitCommitmentLayer = true;
                unitCommitmentGroup.addTo(map);
            }
            const activeIds = new Set();
            for (const marker of getMissionMarkerLayers()) {
                const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
                if (missionId === null) continue;
                const personal = isPersonalMissionLayer(marker, missionId);
                if (personal && !state.visibility.myMissions) continue;
                if (!personal && !state.visibility.allianceMissions) continue;
                if (criticalViewActive && personal) {
                    const ageRecord = personalMissionAgeRecord(marker, missionId);
                    if (!ageRecord || ageRecord.ageMs < CRITICAL_VIEW_MIN_AGE_MS) continue;
                }
                const commitment = personalUnitCommitmentForMission(missionId);
                if (commitment.total <= 0) continue;
                let latLng = null;
                try { latLng = marker.getLatLng?.() || null; } catch (err) {}
                if (!latLng) continue;
                const anchor = unitCommitmentAnchor(marker, missionId);
                const signature = `${commitment.total}:${commitment.onScene}:${commitment.travelling}:${personal}:${anchor}`;
                activeIds.add(missionId);
                let label = unitCommitmentLabels.get(missionId);
                if (!label) {
                    label = pageWindow.L.marker(latLng, { interactive:false, keyboard:false, bubblingMouseEvents:false, pane:floatPane, zIndexOffset:0, icon:makeUnitCommitmentIcon(commitment, personal, anchor) });
                    label.__mcmsUnitCommitmentSignature = signature;
                    label.__mcmsUnitCommitmentLabel = true;
                    label.addTo(unitCommitmentGroup);
                    unitCommitmentLabels.set(missionId, label);
                } else {
                    try { label.setLatLng(latLng); } catch (err) {}
                    if (label.__mcmsUnitCommitmentSignature !== signature) {
                        label.__mcmsUnitCommitmentSignature = signature;
                        try { label.setIcon(makeUnitCommitmentIcon(commitment, personal, anchor)); } catch (err) {}
                    }
                }
            }
            for (const [missionId, label] of Array.from(unitCommitmentLabels.entries())) {
                if (activeIds.has(missionId)) continue;
                unitCommitmentLabels.delete(missionId);
                try { unitCommitmentGroup.removeLayer(label); } catch (err) {}
            }
        } catch (err) { clearUnitCommitmentLabels(); }
    }

    function scheduleUnitCommitmentRefresh(delay = 400) {
        runtimeClearTimeout(unitCommitmentTimer);
        unitCommitmentTimer = runtimeSetTimeout(updateUnitCommitmentLabels, delay);
    }


    function clearTransportWatcherLabels() {
        if (transportWatcherGroup) {
            try { transportWatcherGroup.clearLayers(); transportWatcherGroup.remove(); } catch (err) {}
        }
        transportWatcherLabels.clear();
        transportWatcherGroup = null;
    }

    function transportRequirementFromSnapshot(snapshot) {
        const raw = normaliseMissingRequirementText(snapshot?.missingText);
        if (!raw) return null;
        const text = raw.toLowerCase();
        const transportRequired = [
            /\btransport(?:ation)?\b.{0,34}\b(?:needed|required|waiting|pending)\b/i,
            /\b(?:needs?|requires?|awaiting)\b.{0,34}\btransport(?:ation)?\b/i,
            /\bmust be transported\b/i,
            /\btransport is needed\b/i,
            /\b(?:transport|abtransport|gefangenentransport)\b.{0,34}\b(?:erforderlich|ben[oö]tigt|notwendig)\b/i,
            /\b(?:muss|müssen)\b.{0,34}\btransportiert werden\b/i,
            /\b(?:transport|vervoer)\b.{0,34}\b(?:nodig|vereist)\b/i,
            /\b(?:moet|moeten)\b.{0,34}\b(?:vervoerd|afgevoerd)\b/i
        ].some(pattern => pattern.test(text));
        if (!transportRequired) return null;

        const prisonerTerms = /prison|prisoner|custod|detainee|arrest|cell|jail|gefangen|haft|arrestant|gevangen/i;
        const patientTerms = /patient|hospital|ambulance|medical|casualt|injur|verletz|krankenhaus|ziekenhuis|gewond/i;
        const patients = Number(snapshot?.patientsCount) || 0;
        const prisoners = Number(snapshot?.prisonersCount) || 0;
        let type = 'general';
        if (prisonerTerms.test(text) || (prisoners > 0 && patients <= 0)) type = 'prisoner';
        else if (patientTerms.test(text) || (patients > 0 && prisoners <= 0)) type = 'patient';

        const explicitCount = raw.match(/\b(\d{1,2})\b/);
        let count = explicitCount ? Number(explicitCount[1]) : 0;
        if (!count && type === 'patient' && patients > 1) count = patients;
        if (!count && type === 'prisoner' && prisoners > 1) count = prisoners;
        count = Math.min(99, Math.max(0, Math.round(count || 0)));

        return {
            type,
            count,
            label: type === 'patient' ? 'Patient transport required' : type === 'prisoner' ? 'Prisoner transport required' : 'Transport required'
        };
    }

    function transportWatcherSvg(type) {
        if (type === 'prisoner') {
            return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 8.5h12.2l3.1 3.3v5.1H3.5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M15.7 8.5v3.3h3.1M7 11.2v3.2M10 11.2v3.2M13 11.2v3.2" fill="none" stroke="currentColor" stroke-width="1.55" stroke-linecap="round"/><circle cx="7.1" cy="18" r="1.7" fill="#171008" stroke="currentColor" stroke-width="1.3"/><circle cx="16.4" cy="18" r="1.7" fill="#171008" stroke="currentColor" stroke-width="1.3"/></svg>`;
        }
        if (type === 'patient') {
            return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 8.5h11.8l3.7 3.5v4.9H3.5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M15.3 8.5V12H19M8.3 10.2v4.3M6.15 12.35h4.3" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round"/><circle cx="7.1" cy="18" r="1.7" fill="#171008" stroke="currentColor" stroke-width="1.3"/><circle cx="16.4" cy="18" r="1.7" fill="#171008" stroke="currentColor" stroke-width="1.3"/></svg>`;
        }
        return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.8 8.8h11.9l3.7 3.4v4.7H2.8z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M14.7 8.8v3.4h3.7M7.4 12.7h5.1M10.8 10.8l2 1.9-2 1.9" fill="none" stroke="currentColor" stroke-width="1.55" stroke-linecap="round" stroke-linejoin="round"/><circle cx="6.5" cy="18" r="1.7" fill="#171008" stroke="currentColor" stroke-width="1.3"/><circle cx="15.8" cy="18" r="1.7" fill="#171008" stroke="currentColor" stroke-width="1.3"/></svg>`;
    }

    function renderedMissionFloatWidth(label, selector, fallback) {
        try {
            const badge = label?._icon?.querySelector?.(selector);
            const width = Number(badge?.getBoundingClientRect?.().width);
            if (Number.isFinite(width) && width > 0) return width;
        } catch (err) {}
        return fallback;
    }

    function transportWatcherPlacement(map, marker, missionId, requirement) {
        const personal = isPersonalMissionLayer(marker, missionId);
        let occupiedWidth = 0;
        let source = 'marker';

        if (personal && state.missionAge) {
            occupiedWidth = renderedMissionFloatWidth(
                missionAgeLabels.get(missionId),
                '.mcms-mission-age-badge',
                52
            );
            source = 'mission-age';
        } else if (!personal && state.allianceCredits) {
            occupiedWidth = renderedMissionFloatWidth(
                allianceCreditLabels.get(missionId),
                '.mcms-alliance-credit-badge',
                64
            );
            source = 'alliance-credit';
        } else if (state.unitCommitment) {
            const commitment = personalUnitCommitmentForMission(missionId);
            if (commitment.total > 0) {
                occupiedWidth = renderedMissionFloatWidth(
                    unitCommitmentLabels.get(missionId),
                    '.mcms-unit-commitment-badge',
                    54
                );
                source = 'unit-count';
            }
        }

        const watcherHalfWidth = 13;
        const gap = occupiedWidth > 0 ? 6 : 4;
        const horizontalOffset = occupiedWidth > 0
            ? Math.ceil((occupiedWidth / 2) + watcherHalfWidth + gap)
            : 21;

        let side = 'right';
        try {
            const latLng = marker?.getLatLng?.();
            const point = latLng && map?.latLngToContainerPoint?.(latLng);
            const size = map?.getSize?.();
            const countExtra = Number(requirement?.count) > 1 ? 10 : 3;
            if (point && size && point.x + horizontalOffset + watcherHalfWidth + countExtra > size.x - 4) side = 'left';
        } catch (err) {}

        return {
            side,
            source,
            horizontalOffset,
            iconAnchor: [side === 'right' ? -horizontalOffset : horizontalOffset, 18],
            signature: `${side}:${source}:${horizontalOffset}`
        };
    }

    function makeTransportWatcherIcon(requirement, placement) {
        const type = ['patient', 'prisoner'].includes(requirement?.type) ? requirement.type : 'general';
        const side = placement?.side === 'left' ? 'left' : 'right';
        const count = Number(requirement?.count) > 1 ? `<span class="mcms-transport-watcher-count">${escapeHtml(requirement.count)}</span>` : '';
        return pageWindow.L.divIcon({
            className: 'mcms-transport-watcher-icon',
            html: `<span class="mcms-transport-watcher-badge mcms-transport-${type} mcms-transport-side-${side}" aria-label="${escapeHtml(requirement?.label || 'Transport required')}" title="${escapeHtml(requirement?.label || 'Transport required')}">${transportWatcherSvg(type)}${count}</span>`,
            iconSize: [0, 0],
            iconAnchor: placement?.iconAnchor || [-21, 18]
        });
    }

    function updateTransportWatcherLabels() {
        runtimeClearTimeout(transportWatcherTimer);
        transportWatcherTimer = null;
        if (!state.transportWatcher) {
            clearTransportWatcherLabels();
            return;
        }

        const map = findLeafletMapInstance(false);
        if (!map || !pageWindow.L || typeof pageWindow.L.layerGroup !== 'function' || typeof pageWindow.L.marker !== 'function' || typeof pageWindow.L.divIcon !== 'function') {
            clearTransportWatcherLabels();
            return;
        }
        const pane = ensureMissionFloatPane(map);
        if (!pane) {
            clearTransportWatcherLabels();
            return;
        }

        try {
            if (!transportWatcherGroup || transportWatcherGroup._map !== map) {
                clearTransportWatcherLabels();
                transportWatcherGroup = pageWindow.L.layerGroup();
                transportWatcherGroup.__mcmsTransportWatcherLayer = true;
                transportWatcherGroup.addTo(map);
            }

            const activeIds = new Set();
            const now = Date.now();
            for (const marker of getMissionMarkerLayers()) {
                const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
                if (missionId === null) continue;
                const personal = isPersonalMissionLayer(marker, missionId);
                if (personal && !state.visibility.myMissions) continue;
                if (!personal && !state.visibility.allianceMissions) continue;
                if (criticalViewActive && personal) {
                    const ageRecord = personalMissionAgeRecord(marker, missionId, now);
                    if (!ageRecord || ageRecord.ageMs < CRITICAL_VIEW_MIN_AGE_MS) continue;
                }

                const snapshot = liveMissionSnapshots.get(missionId) || missionSnapshotFromMarker(marker, now);
                const requirement = transportRequirementFromSnapshot(snapshot);
                if (!requirement) continue;

                let latLng = null;
                try { latLng = marker.getLatLng?.() || null; } catch (err) {}
                if (!latLng) continue;
                try {
                    const onMap = typeof map.hasLayer === 'function' ? map.hasLayer(marker) : Boolean(marker._map);
                    if (!onMap) continue;
                } catch (err) {}

                const placement = transportWatcherPlacement(map, marker, missionId, requirement);
                const signature = `${requirement.type}:${requirement.count}:${requirement.label}:${placement.signature}`;
                activeIds.add(missionId);
                let label = transportWatcherLabels.get(missionId);
                if (!label) {
                    label = pageWindow.L.marker(latLng, {
                        interactive: false, keyboard: false, bubblingMouseEvents: false,
                        pane, zIndexOffset: 0, icon: makeTransportWatcherIcon(requirement, placement)
                    });
                    label.__mcmsTransportWatcherSignature = signature;
                    label.__mcmsTransportWatcherLabel = true;
                    label.addTo(transportWatcherGroup);
                    transportWatcherLabels.set(missionId, label);
                } else {
                    try { label.setLatLng(latLng); } catch (err) {}
                    if (label.__mcmsTransportWatcherSignature !== signature) {
                        label.__mcmsTransportWatcherSignature = signature;
                        try { label.setIcon(makeTransportWatcherIcon(requirement, placement)); } catch (err) {}
                    }
                }
            }

            for (const [missionId, label] of Array.from(transportWatcherLabels.entries())) {
                if (activeIds.has(missionId)) continue;
                transportWatcherLabels.delete(missionId);
                try { transportWatcherGroup.removeLayer(label); } catch (err) {}
            }
        } catch (err) {
            clearTransportWatcherLabels();
        }
    }

    function scheduleTransportWatcherRefresh(delay = 320) {
        runtimeClearTimeout(transportWatcherTimer);
        transportWatcherTimer = runtimeSetTimeout(updateTransportWatcherLabels, delay);
    }

    function transportSweepSleep(ms) {
        return runtimeDelay(ms);
    }

    function transportSweepElementVisible(element) {
        if (!element || !element.isConnected) return false;
        try {
            const view = element.ownerDocument?.defaultView || window;
            const style = view.getComputedStyle(element);
            if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
            const rect = element.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
        } catch (err) {
            return false;
        }
    }

    async function transportSweepWaitFor(test, timeoutMs = 5000, intervalMs = 120) {
        const started = Date.now();
        while (Date.now() - started < timeoutMs) {
            if (runtime.destroyed || transportSweepRuntime.stopRequested) return null;
            try {
                const value = test();
                if (value) return value;
            } catch (err) {}
            if (!await transportSweepSleep(intervalMs)) return null;
        }
        return null;
    }

    function transportSweepLog(message, level = 'info') {
        const clean = String(message || '').trim();
        if (!clean) return;
        transportSweepRuntime.log.unshift({ time: Date.now(), message: clean, level });
        if (transportSweepRuntime.log.length > 18) transportSweepRuntime.log.length = 18;
        renderTransportSweepPanel();
    }

    function buildTransportSweepQueue() {
        const now = Date.now();
        const queue = [];
        const seen = new Set();
        for (const marker of getMissionMarkerLayers()) {
            const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
            if (missionId === null || seen.has(missionId)) continue;
            const personal = isPersonalMissionLayer(marker, missionId);
            if (personal) continue;
            const snapshot = liveMissionSnapshots.get(missionId) || missionSnapshotFromMarker(marker, now);
            const requirement = transportRequirementFromSnapshot(snapshot);
            const patientCount = Math.max(0, Number(snapshot?.patientsCount) || 0);
            if (!requirement || requirement.type === 'prisoner') continue;
            if (requirement.type !== 'patient' && patientCount <= 0) continue;
            const count = Math.max(1, Math.min(99, Number(requirement.count) || patientCount || 1));
            seen.add(missionId);
            queue.push({
                missionId,
                caption: String(snapshot?.caption || `Alliance mission ${missionId}`),
                count,
                createdAt: Number(snapshot?.createdAt) || 0,
                requirement: requirement.label || 'Patient transport required'
            });
        }
        queue.sort((a, b) => (a.createdAt || Number.MAX_SAFE_INTEGER) - (b.createdAt || Number.MAX_SAFE_INTEGER));
        transportSweepRuntime.queue = queue;
        transportSweepRuntime.scannedAt = now;
        renderTransportSweepPanel();
        return queue;
    }

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

    function transportSweepVehicleIdFromHref(href) {
        let pathname = String(href || '').trim();
        try { pathname = new URL(pathname, pageWindow.location.origin).pathname; } catch (err) {}
        const match = pathname.match(/^\/vehicles\/(\d+)(?:\/|$)/);
        return match ? match[1] : null;
    }

    function transportSweepAnchorUsable(anchor) {
        if (!anchor || !anchor.isConnected || anchor.closest?.(`#${SCRIPT.panelId}`)) return false;
        try {
            const view = anchor.ownerDocument?.defaultView || window;
            let node = anchor;
            for (let depth = 0; depth < 7 && node; depth += 1, node = node.parentElement) {
                const style = view.getComputedStyle(node);
                if (style.display === 'none' || style.visibility === 'hidden') continue;
                const rect = node.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) return true;
            }
        } catch (err) {}
        return false;
    }

    function transportSweepDocumentContexts() {
        const contexts = [];
        const seenDocuments = new Set();
        const visit = (doc, label = 'top') => {
            if (!doc || seenDocuments.has(doc)) return;
            seenDocuments.add(doc);
            contexts.push({ doc, label });
            let frames = [];
            try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
            frames.forEach((frame, index) => {
                try {
                    const child = frame.contentDocument || frame.contentWindow?.document;
                    if (child) visit(child, `${label}/frame${index + 1}`);
                } catch (err) {
                    // Cross-origin frames are intentionally ignored.
                }
            });
        };
        visit(document);
        return contexts;
    }

    function transportSweepVehicleAnchorsWithin(root = null, requireUsable = true) {
        const scope = root && (root.isConnected || root.nodeType === 9) ? root : document;
        let anchors = [];
        try { anchors = Array.from(scope.querySelectorAll('a[href*="/vehicles/"]')); } catch (err) {}
        return anchors.filter(anchor => {
            if (!transportSweepVehicleIdFromHref(anchor.getAttribute('href'))) return false;
            return !requireUsable || transportSweepAnchorUsable(anchor);
        });
    }

    function transportSweepVisibleVehicleAnchors() {
        const anchors = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            for (const anchor of transportSweepVehicleAnchorsWithin(context.doc, true)) {
                if (seen.has(anchor)) continue;
                seen.add(anchor);
                anchors.push(anchor);
            }
        }
        return anchors;
    }

    function transportSweepVisibleWindowRoots() {
        const selectors = [
            '#lightbox_box .lightbox_content', '#lightbox_box', '#lightbox', '.lightbox_content',
            '[id*="lightbox"]', '.lightbox', '.modal.show .modal-content', '.modal.in .modal-content',
            '.modal.show', '.modal.in', '[role="dialog"]', '.ui-dialog-content', '.ui-dialog'
        ];
        const roots = [];
        const seen = new Set();
        for (const context of transportSweepDocumentContexts()) {
            for (const selector of selectors) {
                let matches = [];
                try { matches = Array.from(context.doc.querySelectorAll(selector)); } catch (err) {}
                for (const root of matches) {
                    if (!root || seen.has(root) || !transportSweepElementVisible(root)) continue;
                    if (root.closest?.(`#${SCRIPT.panelId}`)) continue;
                    seen.add(root);
                    roots.push(root);
                }
            }
            if (context.doc !== document) {
                const body = context.doc.body;
                if (body && !seen.has(body) && transportSweepElementVisible(body) && transportSweepVehicleAnchorsWithin(body, true).length) {
                    seen.add(body);
                    roots.push(body);
                }
            }
        }
        return roots;
    }

    function transportSweepRootScore(root, missionId = null) {
        if (!root || !root.isConnected) return -1;
        const anchors = transportSweepVehicleAnchorsWithin(root);
        if (!anchors.length) return -1;
        let score = anchors.length * 10;
        const text = String(root.textContent || '').toLowerCase();
        if (/mission|incident|einsatz|call/.test(text)) score += 15;
        if (/patient|transport|ambulance|discharge/.test(text)) score += 30;
        if (missionId !== null) {
            try {
                if (root.querySelector(`a[href*="/missions/${missionId}"]`)) score += 80;
            } catch (err) {}
        }
        const rect = root.getBoundingClientRect();
        score += Math.min(30, Math.round((rect.width * rect.height) / 50000));
        return score;
    }

    function transportSweepFindMissionWindowRoot(missionId = null) {
        const roots = transportSweepVisibleWindowRoots();
        let best = null;
        let bestScore = -1;
        for (const root of roots) {
            const score = transportSweepRootScore(root, missionId);
            if (score > bestScore) {
                best = root;
                bestScore = score;
            }
        }
        if (best) return best;

        // Fallback for MissionChief builds that render lightbox content without a stable wrapper.
        const baseline = transportSweepRuntime.missionAnchorBaseline;
        const anchor = transportSweepVisibleVehicleAnchors().find(item => !(baseline instanceof Set) || !baseline.has(item));
        if (!anchor) return null;
        return anchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || anchor.ownerDocument?.body || anchor.parentElement;
    }

    function transportSweepAnchorBelongsToMissionWindow(anchor) {
        if (!anchor || !transportSweepAnchorUsable(anchor)) return false;
        const root = transportSweepRuntime.missionWindowRoot;
        if (root?.isConnected && root.contains(anchor)) return true;
        const baseline = transportSweepRuntime.missionAnchorBaseline;
        if (baseline instanceof Set && !baseline.has(anchor)) return true;
        return transportSweepVisibleWindowRoots().some(windowRoot => windowRoot.contains(anchor));
    }

    function transportSweepOwnVehicleIdSet() {
        if (transportSweepRuntime.ownVehicleIds instanceof Set && transportSweepRuntime.ownVehicleIds.size) {
            return new Set(Array.from(transportSweepRuntime.ownVehicleIds, id => String(id)));
        }
        const ids = new Set(Array.from(personalVehicleApiCache.keys(), id => String(id)));
        for (const vehicle of getPersonalVehicleRecords()) {
            const id = vehicleRecordId(vehicle);
            if (id !== null) ids.add(String(id));
        }
        transportSweepRuntime.ownVehicleIds = ids;
        return ids;
    }

    function collectTransportSweepStaticCandidates(anchors, source = 'mission HTML', preserveAnchors = false) {
        const unique = new Map();
        const ownIds = transportSweepOwnVehicleIdSet();
        let rejectedOwn = 0;
        let allianceLinks = 0;
        let rejectedNotFms5 = 0;
        let rejectedNotPatient = 0;

        for (const anchor of Array.from(anchors || [])) {
            const href = String(anchor.getAttribute?.('href') || '').trim();
            const vehicleId = transportSweepVehicleIdFromHref(href);
            if (!vehicleId) continue;

            const row = anchor.closest?.('tr[id^="vehicle_row_"], tr, li, [id^="vehicle_row_"], [class*="vehicle_row"]');
            const fms5 = row?.querySelector?.('.building_list_fms_5');
            if (!row || !fms5) {
                rejectedNotFms5 += 1;
                continue;
            }

            if (ownIds.has(String(vehicleId))) {
                rejectedOwn += 1;
                continue;
            }

            allianceLinks += 1;
            const vehicleTypeId = String(anchor.getAttribute?.('vehicle_type_id') || '');
            const label = String(anchor.textContent || 'Alliance vehicle').trim() || 'Alliance vehicle';
            const rowText = String(row.textContent || '').replace(/\s+/g, ' ').trim();
            const isPatientVehicle = vehicleTypeId === '5' || /ambulance|patient|paramedic|rettungs|krankentransport|rtw\b/i.test(`${label} ${rowText}`);
            if (!isPatientVehicle) {
                rejectedNotPatient += 1;
                continue;
            }

            const normalisedHref = `/vehicles/${vehicleId}`;
            const candidate = {
                href: normalisedHref,
                vehicleId,
                label,
                vehicleTypeId,
                score: 500,
                anchor: preserveAnchors ? anchor : null,
                row: preserveAnchors ? row : null,
                source,
                rowText
            };
            if (!unique.has(normalisedHref)) unique.set(normalisedHref, candidate);
        }

        return {
            candidates: Array.from(unique.values())
                .sort((a, b) => a.label.localeCompare(b.label) || Number(a.vehicleId) - Number(b.vehicleId))
                .slice(0, TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION),
            stats: {
                totalLinks: Array.from(anchors || []).length,
                allianceLinks,
                rejectedOwn,
                rejectedNotFms5,
                rejectedNotPatient,
                candidates: unique.size,
                source
            }
        };
    }

    async function transportSweepFetchMissionCandidates(missionId) {
        const id = normaliseMissionId(missionId);
        if (id === null || transportSweepRuntime.stopRequested) return null;
        const requestModes = [
            { headers: { 'X-Requested-With': 'XMLHttpRequest', Accept: 'text/html, */*;q=0.8' } },
            { headers: { Accept: 'text/html,application/xhtml+xml' } }
        ];
        let bestResult = null;
        for (const mode of requestModes) {
            if (transportSweepRuntime.stopRequested) return null;
            try {
                const response = await runtimeFetch(`/missions/${id}`, {
                    method: 'GET',
                    credentials: 'same-origin',
                    cache: 'no-store',
                    headers: mode.headers
                });
                if (!response.ok) continue;
                const html = await response.text();
                if (!html || html.length < 100) continue;
                const doc = new DOMParser().parseFromString(html, 'text/html');
                const anchors = Array.from(doc.querySelectorAll('a[href*="/vehicles/"]'))
                    .filter(anchor => transportSweepVehicleIdFromHref(anchor.getAttribute('href')));
                if (!anchors.length) continue;
                const result = { ...collectTransportSweepStaticCandidates(anchors, 'mission HTML'), htmlLength: html.length };
                if (!bestResult || result.stats.totalLinks > bestResult.stats.totalLinks) bestResult = result;
                if (result.candidates.length) return result;
            } catch (err) {
                // Try the next request mode.
            }
        }
        return bestResult;
    }

    async function collectTransportSweepVehicleCandidatesForMission(missionId) {
        const domCandidates = collectTransportSweepVehicleCandidates();
        const domStats = { ...(transportSweepRuntime.lastCandidateStats || {}) };
        if (domCandidates.length) return domCandidates;

        const fetched = await transportSweepFetchMissionCandidates(missionId);
        if (fetched) {
            transportSweepRuntime.rejectedOwn = fetched.stats.rejectedOwn || 0;
            transportSweepRuntime.lastCandidateStats = fetched.stats;
            if (fetched.candidates?.length) {
                transportSweepLog(`Recovered ${fetched.stats.totalLinks} vehicle links from mission HTML`);
                return fetched.candidates;
            }
        }

        if (!fetched) transportSweepRuntime.lastCandidateStats = domStats;
        return [];
    }

    function collectTransportSweepVehicleCandidates() {
        const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : null;
        let anchors = root ? transportSweepVehicleAnchorsWithin(root) : [];
        if (!anchors.length) anchors = transportSweepVisibleVehicleAnchors().filter(anchor => transportSweepAnchorBelongsToMissionWindow(anchor));

        const result = collectTransportSweepStaticCandidates(anchors, 'mission window', true);
        transportSweepRuntime.rejectedOwn = result.stats.rejectedOwn || 0;
        transportSweepRuntime.lastCandidateStats = result.stats;
        return result.candidates;
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

    async function openTransportSweepPath(path, mode) {
        if (transportSweepRuntime.stopRequested) return false;
        if (typeof pageWindow.lightboxOpen !== 'function') throw new Error('MissionChief lightboxOpen is unavailable');

        if (mode === 'mission') {
            transportSweepRuntime.missionAnchorBaseline = new Set(transportSweepVisibleVehicleAnchors());
            transportSweepRuntime.rejectedOwn = 0;
            transportSweepRuntime.missionWindowRoot = null;
            const beforeWindowText = transportSweepVisibleWindowRoots().map(root => String(root.textContent || '').trim()).join('|');
            const missionId = normaliseMissionId(String(path || '').match(/\/missions\/(\d+)/)?.[1]);
            pageWindow.lightboxOpen(path);
            await transportSweepWaitFor(() => {
                const root = transportSweepFindMissionWindowRoot(missionId);
                if (root) {
                    const anchors = transportSweepVehicleAnchorsWithin(root);
                    const afterText = String(root.textContent || '').trim();
                    const changed = afterText && !beforeWindowText.includes(afterText);
                    if (anchors.length || changed) {
                        transportSweepRuntime.missionWindowRoot = root;
                        return { root, anchors };
                    }
                }
                const newAnchor = transportSweepVisibleVehicleAnchors().find(anchor => !transportSweepRuntime.missionAnchorBaseline.has(anchor));
                if (newAnchor) {
                    transportSweepRuntime.missionWindowRoot = newAnchor.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-content, [role="dialog"], .ui-dialog-content') || newAnchor.ownerDocument?.body || newAnchor.parentElement;
                    return { root: transportSweepRuntime.missionWindowRoot, anchors: [newAnchor] };
                }
                return null;
            }, 3200, 120);
            return !transportSweepRuntime.stopRequested;
        }

        pageWindow.lightboxOpen(path);
        await transportSweepSleep(900);
        return !transportSweepRuntime.stopRequested;
    }

    async function openTransportSweepVehicle(candidate) {
        if (transportSweepRuntime.stopRequested || !candidate?.href) return null;
        transportSweepRuntime.vehicleButtonBaseline = new Set(transportSweepVisibleDischargeButtons());
        const beforeRoots = transportSweepVisibleWindowRoots();
        const beforeText = beforeRoots.map(root => String(root.textContent || '').trim()).join('|');

        let anchor = candidate.anchor;
        if (!anchor?.isConnected) {
            const root = transportSweepRuntime.missionWindowRoot?.isConnected ? transportSweepRuntime.missionWindowRoot : document;
            anchor = Array.from(root.querySelectorAll?.('a[href*="/vehicles/"]') || []).find(item => transportSweepVehicleIdFromHref(item.getAttribute('href')) === String(candidate.vehicleId));
        }

        let usedMissionClick = false;
        if (anchor?.isConnected) {
            try {
                anchor.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
                anchor.click();
                usedMissionClick = true;
            } catch (err) {}
        }

        if (!usedMissionClick) {
            if (typeof pageWindow.lightboxOpen !== 'function') return null;
            pageWindow.lightboxOpen(candidate.href);
        }

        const openedAt = Date.now();
        return await transportSweepWaitFor(() => {
            const button = findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline);
            if (button) return { opened: true, button };
            const afterText = transportSweepVisibleWindowRoots().map(root => String(root.textContent || '').trim()).join('|');
            if (afterText && afterText !== beforeText && Date.now() - openedAt > 350) return { opened: true, button: null };
            return null;
        }, 7500, 140);
    }

    async function processTransportSweepMission(item, remainingAllowance) {
        const missionId = normaliseMissionId(item?.missionId);
        if (missionId === null || remainingAllowance <= 0) return 0;

        transportSweepRuntime.currentMissionId = missionId;
        renderTransportSweepPanel();

        const target = Math.max(1, Math.min(Number(item.count) || 1, remainingAllowance));
        const attemptedVehicleIds = new Set();
        let clearedHere = 0;
        let initialScanLogged = false;
        let missionHadCandidates = false;

        while (!transportSweepRuntime.stopRequested && clearedHere < target && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
            transportSweepLog(`${attemptedVehicleIds.size ? 'Reopening' : 'Opening'} ${item.caption}`);
            const opened = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
            if (!opened || transportSweepRuntime.stopRequested) break;

            const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);
            const candidateStats = transportSweepRuntime.lastCandidateStats || {};
            if (!initialScanLogged) {
                const source = candidateStats.source ? ` · ${candidateStats.source}` : '';
                transportSweepLog(`Mission scan: ${candidateStats.totalLinks || 0} vehicle links · ${candidateStats.allianceLinks || 0} alliance FMS 5 · ${candidateStats.candidates || 0} patient candidates${source}`);
                if (transportSweepRuntime.rejectedOwn > 0) {
                    transportSweepLog(`Ignored ${transportSweepRuntime.rejectedOwn} of your own FMS 5 vehicle${transportSweepRuntime.rejectedOwn === 1 ? '' : 's'} at ${item.caption}`);
                }
                initialScanLogged = true;
            }

            if (candidates.length) missionHadCandidates = true;
            const candidate = candidates.find(entry => !attemptedVehicleIds.has(String(entry.vehicleId)));
            if (!candidate) {
                if (!missionHadCandidates) {
                    transportSweepLog(`No non-personal FMS 5 patient vehicles were found inside ${item.caption}`, 'warn');
                } else {
                    transportSweepLog(`Checked every non-personal FMS 5 patient vehicle at ${item.caption}; none exposed Discharge patient`, 'warn');
                }
                break;
            }

            attemptedVehicleIds.add(String(candidate.vehicleId));
            transportSweepRuntime.currentVehicleHref = candidate.href;
            renderTransportSweepPanel();
            transportSweepLog(`Checking FMS 5 ${candidate.label} (${candidate.vehicleId}) · ${attemptedVehicleIds.size}/${candidates.length}`);

            const vehicleResult = await openTransportSweepVehicle(candidate);
            if (transportSweepRuntime.stopRequested) break;

            const button = vehicleResult?.button || (vehicleResult?.opened ? await transportSweepWaitFor(
                () => findVisibleDischargePatientButton(transportSweepRuntime.vehicleButtonBaseline),
                3200,
                120
            ) : null);

            if (!button) {
                transportSweepLog(`${candidate.label} is carrying a patient but is not transport-ready; continuing in the same mission`);
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

            if (!transportSweepRuntime.stopRequested && clearedHere < target && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
                await transportSweepSleep(state.transportSweep.delayMs);
            }
        }

        if (clearedHere === 0 && !transportSweepRuntime.stopRequested) {
            transportSweepRuntime.skipped += 1;
        }
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
        const confirmed = pageWindow.confirm(`Transport Sweep will use MissionChief's visible co-admin controls to attempt up to ${planned} patient discharges across ${queue.length} alliance mission${queue.length === 1 ? '' : 's'}.\n\nYour own vehicle IDs are excluded before any vehicle window is opened. The sweep will inspect each non-personal FMS 5 patient vehicle until MissionChief exposes the enabled “Discharge patient” button. Continue?`);
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
            const wasStopped = transportSweepRuntime.stopRequested;
            transportSweepRuntime.running = false;
            transportSweepRuntime.stopRequested = false;
            transportSweepRuntime.currentMissionId = null;
            transportSweepRuntime.currentVehicleHref = '';
            transportSweepRuntime.missionAnchorBaseline = new Set();
            transportSweepRuntime.vehicleButtonBaseline = new Set();
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
        const active = new Set();
        for (const marker of getMissionMarkerLayers()) {
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
        for (const [missionId, label] of Array.from(resourceGapLabels.entries())) {
            if (active.has(missionId)) continue;
            resourceGapLabels.delete(missionId);
            try { resourceGapGroup.removeLayer(label); } catch (err) {}
        }
    }

    function scheduleResourceGapRefresh(delay = 420) {
        runtimeClearTimeout(resourceGapTimer);
        resourceGapTimer = runtimeSetTimeout(updateResourceGapLabels, delay);
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

    function synchronisePersonalBuildingMarkerClasses() {
        const personalBuildingMarkerIcons = getPersonalBuildingMarkerIcons();
        for (const icon of personalBuildingMarkerIcons) markPersonalBuildingIcon(icon);
        return personalBuildingMarkerIcons;
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

    function scheduleMarkerClassification() {
        runtimeClearTimeout(classifyTimer);
        classifyTimer = runtimeSetTimeout(classifyMarkersNow, 180);
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
            transportSweepRuntime.running
        );
    }

    function missionSnapshotsNeeded() {
        return Boolean(
            state.payoutFlash.enabled || state.transportWatcher || state.stuckDetector.enabled ||
            state.missionSpawn.enabled || state.allianceCredits || state.missionAge ||
            state.unitCommitment || state.resourceGap.enabled || criticalViewActive ||
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
            layer.__mcmsMissionSpawnLabel || layer.__mcmsMissionSpawnRing || layer.__mcmsMissionSpawnLayer
        ));
    }

    let enabledMapRefreshTimer = null;
    let pendingEnabledMapRefresh = { includeSnapshots: false, positionPanel: false };

    function flushEnabledMapRefreshes() {
        enabledMapRefreshTimer = null;
        if (runtime.destroyed) return;
        const request = pendingEnabledMapRefresh;
        pendingEnabledMapRefresh = { includeSnapshots: false, positionPanel: false };

        if (markerClassificationNeeded()) scheduleMarkerClassification();
        if (state.coverage.enabled) scheduleCoverageRefresh();
        if (state.heatmap.enabled) scheduleHeatmapRefresh();
        if (state.allianceCredits) scheduleAllianceCreditRefresh();
        if (state.missionAge) scheduleMissionAgeRefresh();
        if (state.unitCommitment) scheduleUnitCommitmentRefresh();
        if (state.resourceGap.enabled) scheduleResourceGapRefresh();
        if (request.includeSnapshots && missionSnapshotsNeeded()) {
            scheduleMissionSnapshotRefresh();
        } else {
            if (state.transportWatcher) scheduleTransportWatcherRefresh();
            if (state.stuckDetector.enabled) scheduleStuckMissionRefresh();
        }
        if (operationalUiIsVisible()) scheduleOperationalPanelsRender(800);
        if (request.positionPanel && !dragState) schedulePanelPosition(true, 60);
    }

    function scheduleEnabledMapRefreshes({ includeSnapshots = true, positionPanel = false } = {}) {
        pendingEnabledMapRefresh.includeSnapshots ||= Boolean(includeSnapshots);
        pendingEnabledMapRefresh.positionPanel ||= Boolean(positionPanel);
        if (enabledMapRefreshTimer !== null) return;
        enabledMapRefreshTimer = runtimeSetTimeout(flushEnabledMapRefreshes, 35);
    }

    function reconcileFeatureRefreshes({ includeSnapshots = true, positionPanel = false } = {}) {
        if (!state.coverage.enabled) clearCoverageRings();
        if (!state.heatmap.enabled) clearCoverageHeatmap();
        if (!state.allianceCredits) clearAllianceCreditLabels();
        if (!state.missionAge) clearMissionAgeLabels();
        if (!state.unitCommitment) clearUnitCommitmentLabels();
        if (!state.transportWatcher) clearTransportWatcherLabels();
        if (!state.stuckDetector.enabled) clearStuckMissionLabels();
        if (!state.resourceGap.enabled) clearResourceGapLabels();
        if (!state.missionInspector) hideMissionInspector();
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
            let properties = [];
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
            if (isToolkitLeafletLayer(layer)) return;
            const scope = inferScope(layer);
            invalidateMarkerRegistryCaches(scope);

            const isVehicleLayer = scope === 'vehicle';
            if (isVehicleLayer && layer?._icon) markVehicleIcon(layer._icon);
            if (state.markerFocus && isVehicleLayer) {
                synchroniseVehicleMarkerClasses();
                runtimeSetTimeout(() => { if (state.markerFocus) synchroniseVehicleMarkerClasses(); }, 0);
            }
            if (scope === 'building') {
                const isPersonalBuilding = markPersonalBuildingLayerIfOwned(layer);
                if (isPersonalBuilding && !state.visibility.buildings) hidePersonalBuildingLayer(map, layer);
            }
            scheduleEnabledMapRefreshes({ includeSnapshots: scope === 'mission' || scope === 'vehicle' || scope === 'all', positionPanel: false });
        };

        const onLayerRemove = event => {
            const layer = event?.layer;
            if (isToolkitLeafletLayer(layer) || enforcingPersonalBuildingVisibility) return;
            const scope = inferScope(layer);
            invalidateMarkerRegistryCaches(scope);
            scheduleEnabledMapRefreshes({ includeSnapshots: scope !== 'building', positionPanel: false });
        };

        const onMapMove = () => {
            if (!state.visibility.vehicles || state.markerFocus) synchroniseVehicleMarkerClasses();
            if (!enforcingPersonalBuildingVisibility && !state.visibility.buildings) synchronisePersonalBuildingVisibility(map);
            scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: true });
        };

        try {
            map.on('layeradd', onLayerAdd);
            map.on('layerremove', onLayerRemove);
            map.on('moveend zoomend', onMapMove);
            runtime.mapBindings.push(
                { map, types: 'layeradd', handler: onLayerAdd },
                { map, types: 'layerremove', handler: onLayerRemove },
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
            map.setView([lat, lng], zoom);
            return true;
        } catch (err) {
            showToast('Map jump failed');
            return false;
        }
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
            for (const layer of layers) {
                const ring = pageWindow.L.circle(layer.getLatLng(), {
                    radius: metres,
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
        coverageTimer = runtimeSetTimeout(updateCoverageRings, 220);
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

        const columns = 20;
        const mapRect = map.getContainer?.().getBoundingClientRect?.();
        const aspect = mapRect?.width && mapRect?.height ? mapRect.height / mapRect.width : 0.65;
        const rows = Math.max(10, Math.min(20, Math.round(columns * aspect)));
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
        heatmapTimer = runtimeSetTimeout(updateCoverageHeatmap, 180);
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

        state.bookmarks[slot] = {
            name: String(name || fallback).trim() || fallback,
            lat: Number(center.lat.toFixed(6)),
            lng: Number(center.lng.toFixed(6)),
            zoom: Number(zoom),
            pinned: existing ? Boolean(existing.pinned) : false
        };

        saveState();
        renderBookmarks();
        renderScreenPins();
        updateUI();
        showToast('Bookmark saved');
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
            const caption = String(direct).trim();
            if (cached.caption !== caption) missionOverlayData.set(missionId, { ...cached, caption });
            return caption;
        }
        const panel = document.getElementById(`mission_${missionId}`);
        if (panel) {
            const captionNode = panel.querySelector('.map_position_mover[id^="mission_caption_"], .mission_caption, [id^="mission_caption_"]');
            const caption = captionNode?.textContent?.trim();
            if (caption) {
                missionOverlayData.set(missionId, { ...cached, caption });
                return caption;
            }
        }
        const iconText = marker?._icon?.title || marker?._icon?.alt || marker?._icon?.getAttribute?.('aria-label');
        const caption = iconText && String(iconText).trim() ? String(iconText).trim() : '';
        if (caption) missionOverlayData.set(missionId, { ...cached, caption });
        return caption;
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
                onScene: 0,
                travelling: 0,
                known: vehicleApiReady,
                source: vehicleApiReady ? 'api' : 'unknown'
            };
        }

        return {
            total: commitment.total,
            onScene: commitment.onScene,
            travelling: commitment.travelling,
            known: true,
            source: vehicleApiReady ? 'api' : 'live'
        };
    }

    function missionSnapshotFromMarker(marker, now = Date.now()) {
        const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
        if (missionId === null) return null;
        let latLng = null;
        try { latLng = marker.getLatLng?.() || null; } catch (err) {}
        const alliance = isAllianceMissionLayer(marker, missionId);
        const unitState = missionPersonalUnitState(marker, missionId);
        const units = unitState.commitment;
        const overlay = missionOverlayData.get(missionId) || {};
        const rawMissingText = overlay.missingText || marker?.missing_text || marker?.missingText || marker?.options?.missing_text || marker?.options?.missingText || '';
        return {
            missionId,
            marker,
            caption: getMissionCaption(marker, missionId),
            source: alliance ? 'alliance' : 'personal',
            averageCredits: getMissionAverageCredits(marker, missionId),
            qualified: unitState.hasUnit,
            units,
            createdAt: getMissionCreatedAt(marker, missionId),
            missingText: overlay.missingText || normaliseMissingRequirementText(rawMissingText),
            patientsCount: Number.isFinite(Number(overlay.patientsCount ?? marker?.patients_count ?? marker?.patientsCount ?? marker?.options?.patients_count)) ? Number(overlay.patientsCount ?? marker?.patients_count ?? marker?.patientsCount ?? marker?.options?.patients_count) : null,
            possiblePatientsCount: Number.isFinite(Number(overlay.possiblePatientsCount ?? marker?.possible_patients_count ?? marker?.possiblePatientsCount ?? marker?.options?.possible_patients_count)) ? Number(overlay.possiblePatientsCount ?? marker?.possible_patients_count ?? marker?.possiblePatientsCount ?? marker?.options?.possible_patients_count) : null,
            prisonersCount: Number.isFinite(Number(overlay.prisonersCount ?? marker?.prisoners_count ?? marker?.prisonersCount ?? marker?.options?.prisoners_count)) ? Number(overlay.prisonersCount ?? marker?.prisoners_count ?? marker?.prisonersCount ?? marker?.options?.prisoners_count) : null,
            possiblePrisonersCount: Number.isFinite(Number(overlay.possiblePrisonersCount ?? marker?.possible_prisoners_count ?? marker?.possiblePrisonersCount ?? marker?.options?.possible_prisoners_count)) ? Number(overlay.possiblePrisonersCount ?? marker?.possible_prisoners_count ?? marker?.possiblePrisonersCount ?? marker?.options?.possible_prisoners_count) : null,
            liveCurrentValue: Number.isFinite(Number(overlay.liveCurrentValue ?? marker?.live_current_value ?? marker?.liveCurrentValue ?? marker?.options?.live_current_value)) ? Number(overlay.liveCurrentValue ?? marker?.live_current_value ?? marker?.liveCurrentValue ?? marker?.options?.live_current_value) : null,
            vehicleState: Number.isFinite(Number(overlay.vehicleState ?? marker?.vehicle_state ?? marker?.vehicleState ?? marker?.options?.vehicle_state)) ? Number(overlay.vehicleState ?? marker?.vehicle_state ?? marker?.vehicleState ?? marker?.options?.vehicle_state) : null,
            lat: Number(latLng?.lat),
            lng: Number(latLng?.lng),
            lastSeen: now
        };
    }

    function refreshMissionSnapshots() {
        runtimeClearTimeout(missionSnapshotTimer);
        missionSnapshotTimer = null;
        const now = Date.now();
        const current = new Map();
        const missionMarkers = getMissionMarkerLayers();
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
            for (const [missionId, previous] of liveMissionSnapshots.entries()) {
                if (current.has(missionId)) continue;
                if (now - Number(previous.lastSeen || now) > 15000) continue;
                if (!recentCompletedMissions.some(item => item.missionId === missionId && now - item.removedAt < PAYOUT_MATCH_WINDOW_MS)) {
                    recentCompletedMissions.unshift({ ...previous, removedAt: now, matched: false });
                }
            }
        }

        liveMissionSnapshots.clear();
        for (const [missionId, snapshot] of current.entries()) liveMissionSnapshots.set(missionId, snapshot);
        missionSnapshotReady = missionSnapshotReady || current.size > 0;

        for (let index = recentCompletedMissions.length - 1; index >= 0; index -= 1) {
            const item = recentCompletedMissions[index];
            if (current.has(item.missionId) || now - item.removedAt > PAYOUT_MATCH_WINDOW_MS) recentCompletedMissions.splice(index, 1);
        }
        if (recentCompletedMissions.length > 30) recentCompletedMissions.length = 30;

        let progressEntriesRemoved = false;
        for (const [missionId, progress] of Array.from(missionProgressState.entries())) {
            if (current.has(missionId)) continue;
            if (now - Number(progress.lastSeen || now) > MISSION_CACHE_RETENTION_MS) {
                missionProgressState.delete(missionId);
                progressEntriesRemoved = true;
            }
        }

        for (const [missionId, lastSeen] of Array.from(missionLifecycleLastSeen.entries())) {
            if (current.has(missionId) || now - lastSeen <= MISSION_CACHE_RETENTION_MS) continue;
            missionLifecycleLastSeen.delete(missionId);
            missionOverlayData.delete(missionId);
            knownMissionIds.delete(missionId);
            resourceGapLabels.delete(missionId);
            stuckMissionLabels.delete(missionId);
        }
        if (progressEntriesRemoved) saveMissionProgressState();
        if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(80);
        if (state.transportWatcher) scheduleTransportWatcherRefresh(100);
        refreshVisibleMissionInspector();
    }

    function scheduleMissionSnapshotRefresh(delay = 600) {
        runtimeClearTimeout(missionSnapshotTimer);
        missionSnapshotTimer = runtimeSetTimeout(refreshMissionSnapshots, delay);
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

    function formatElapsedCompact(ms) {
        const totalHours = Math.max(0, Math.floor(Number(ms) / 3600000));
        const days = Math.floor(totalHours / 24);
        const hours = totalHours % 24;
        return days > 0 ? `${days}D ${hours}H` : `${totalHours}H`;
    }

    function getCriticalMissionEntries(minAgeMs = CRITICAL_VIEW_MIN_AGE_MS) {
        const now = Date.now();
        const entries = [];
        for (const marker of getMissionMarkerLayers()) {
            const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
            if (missionId === null || !isPersonalMissionLayer(marker, missionId)) continue;
            const ageRecord = personalMissionAgeRecord(marker, missionId, now);
            if (!ageRecord || ageRecord.ageMs < minAgeMs) continue;
            const units = personalUnitCommitmentForMission(missionId);
            entries.push({
                missionId,
                marker,
                caption: getMissionCaption(marker, missionId) || `Mission ${missionId}`,
                missionAge: ageRecord.ageMs,
                severity: ageRecord.severity,
                units
            });
        }
        return entries.sort((a, b) =>
            b.severity.rank - a.severity.rank ||
            b.missionAge - a.missionAge ||
            a.caption.localeCompare(b.caption)
        );
    }

    function qualifiedAllianceMissionCount() {
        let count = 0;
        for (const marker of getMissionMarkerLayers()) {
            const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId);
            if (missionId !== null && isAllianceMissionLayer(marker, missionId) && missionHasPersonalUnit(marker, missionId)) count += 1;
        }
        return count;
    }

    function operationalUiIsVisible() {
        const panel = document.getElementById(SCRIPT.panelId);
        const opsPanelVisible = Boolean(panel?.classList?.contains('mcms-open') && state.activeTab === 'ops');
        const drawerVisible = Boolean(document.getElementById(SCRIPT.criticalDrawerId)?.classList?.contains('mcms-open'));
        return opsPanelVisible || drawerVisible;
    }

    function scheduleOperationalPanelsRender(delay = 500, force = false) {
        runtimeClearTimeout(opsRefreshTimer);
        if (!force && !operationalUiIsVisible()) return;
        const elapsed = Date.now() - operationalPanelsLastRender;
        const wait = Math.max(Number(delay) || 0, elapsed < 750 ? 750 - elapsed : 0);
        opsRefreshTimer = runtimeSetTimeout(() => renderOperationalPanels(force), wait);
    }

    function renderOperationalPanels(force = false) {
        runtimeClearTimeout(opsRefreshTimer);
        opsRefreshTimer = null;
        if (!force && !operationalUiIsVisible()) return;
        operationalPanelsLastRender = Date.now();

        const criticalEntries = getCriticalMissionEntries(CRITICAL_VIEW_MIN_AGE_MS);
        const qualifiedAlliance = qualifiedAllianceMissionCount();
        const summarySignature = JSON.stringify({
            credits: sessionPerformance.creditsEarned,
            qualifying: sessionPerformance.qualifyingCount,
            largest: sessionPerformance.largestPayout,
            payouts: sessionPerformance.payoutCount,
            critical: criticalEntries.map(entry => [entry.missionId, entry.severity.rank, Math.floor(entry.missionAge / 60000), entry.units.total]),
            qualifiedAlliance,
            history: payoutHistory.map(entry => [entry.id, entry.amount, entry.timestamp])
        });

        const panel = document.getElementById(SCRIPT.panelId);
        if (panel) {
            const session = panel.querySelector('[data-ops-session]');
            if (session) {
                const html = `
                    <div class="mcms-ops-session-grid">
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Credits earned</span><strong class="mcms-ops-stat-value">${escapeHtml(formatOperationalCompactCredits(sessionPerformance.creditsEarned))}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">10K+ completions</span><strong class="mcms-ops-stat-value">${Number(sessionPerformance.qualifyingCount) || 0}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Largest payout</span><strong class="mcms-ops-stat-value">${escapeHtml(formatOperationalCompactCredits(sessionPerformance.largestPayout))}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Aged missions</span><strong class="mcms-ops-stat-value">${criticalEntries.length}</strong></div>
                        <div class="mcms-ops-stat"><span class="mcms-ops-stat-label">Alliance qualified</span><strong class="mcms-ops-stat-value">${qualifiedAlliance}</strong></div>
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
                        <div class="mcms-ops-entry-main"><span class="mcms-ops-entry-title">${escapeHtml(entry.caption || (entry.source === 'alliance' ? 'Alliance mission payout' : entry.source === 'personal' ? 'Personal mission payout' : 'Credit award'))}</span><span class="mcms-ops-entry-meta">${escapeHtml(formatClockTime(entry.timestamp))} · ${escapeHtml(entry.source.toUpperCase())} · ${escapeHtml(entry.tier.toUpperCase())}</span></div>
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
        operationalRenderSignature = summarySignature;
        renderCriticalDrawer(criticalEntries);
    }

    function createCriticalDrawer() {
        let drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (drawer) return drawer;
        drawer = document.createElement('aside');
        drawer.id = SCRIPT.criticalDrawerId;
        drawer.setAttribute('aria-label', 'Personal missions aged 8 hours or more');
        drawer.innerHTML = `<div class="mcms-drawer-head"><div><strong class="mcms-drawer-title">MISSION AGE WATCH</strong><span class="mcms-drawer-subtitle">Personal missions aged 8H+ · click to centre · double-click to open</span></div><button class="mcms-drawer-close" type="button">×</button></div><div class="mcms-drawer-list"></div>`;
        drawer.addEventListener('click', event => {
            if (closestEventTarget(event, '.mcms-drawer-close')) { drawer.classList.remove('mcms-open'); return; }
            const row = closestEventTarget(event, '[data-mission-id]');
            if (row) focusMissionById(row.dataset.missionId, false);
        });
        drawer.addEventListener('dblclick', event => {
            const row = closestEventTarget(event, '[data-mission-id]');
            if (row) { event.preventDefault(); focusMissionById(row.dataset.missionId, true); }
        });
        document.body.appendChild(drawer);
        return drawer;
    }

    function renderCriticalDrawer(entries = null) {
        const drawer = document.getElementById(SCRIPT.criticalDrawerId);
        if (!drawer || !drawer.classList.contains('mcms-open')) return;
        const list = drawer.querySelector('.mcms-drawer-list');
        if (!list) return;
        const criticalEntries = entries || getCriticalMissionEntries(CRITICAL_VIEW_MIN_AGE_MS);
        const html = criticalEntries.length ? criticalEntries.map(entry => `
            <button class="mcms-critical-row ${escapeHtml(entry.severity.className)}" type="button" data-mission-id="${escapeHtml(entry.missionId)}">
                <span class="mcms-critical-age-band">${escapeHtml(entry.severity.label)}</span>
                <span><span class="mcms-critical-name">${escapeHtml(entry.caption)}</span><span class="mcms-critical-meta">${entry.units.onScene} on scene · ${entry.units.travelling} travelling</span></span>
                <span class="mcms-critical-age">${escapeHtml(formatElapsedCompact(entry.missionAge))}</span>
            </button>`).join('') : '<div class="mcms-empty-state">No personal missions are currently 8 hours old or more.</div>';
        setInnerHtmlIfChanged(list, html, `drawer:${criticalEntries.map(entry => `${entry.missionId}:${Math.floor(entry.missionAge / 60000)}:${entry.units.onScene}:${entry.units.travelling}`).join('|')}`);
    }

    function toggleCriticalDrawer() {
        const drawer = createCriticalDrawer();
        drawer.classList.toggle('mcms-open');
        renderCriticalDrawer();
    }

    function focusMissionById(missionId, openMission = false) {
        const id = normaliseMissionId(missionId);
        const marker = getMissionMarkerLayers().find(item => normaliseMissionId(item?.mission_id ?? item?.missionId ?? item?.options?.mission_id ?? item?.options?.missionId) === id);
        if (!marker) { showToast('Mission is no longer available'); return false; }
        let latLng = null;
        try { latLng = marker.getLatLng?.() || null; } catch (err) {}
        const map = findLeafletMapInstance(false);
        if (map && latLng) {
            try { map.setView(latLng, Math.max(Number(map.getZoom?.()) || 0, 13)); } catch (err) {}
        }
        if (marker._icon?.classList) {
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
            document.getElementById(SCRIPT.criticalDrawerId)?.classList.remove('mcms-open');
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
                renderCriticalDrawer();
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

        try {
            if (!stuckMissionGroup || stuckMissionGroup._map !== map) {
                clearStuckMissionLabels();
                stuckMissionGroup = pageWindow.L.layerGroup();
                stuckMissionGroup.__mcmsStuckMissionLayer = true;
                stuckMissionGroup.addTo(map);
            }

            const activeIds = new Set();
            const now = Date.now();
            for (const marker of getMissionMarkerLayers()) {
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
                if (!latLng) continue;
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

            for (const [missionId, label] of Array.from(stuckMissionLabels.entries())) {
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
        stuckMissionTimer = runtimeSetTimeout(updateStuckMissionLabels, delay);
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
        let missionTooltip = null;
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
        if (!missionInspectorMarker) return;
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
        const marker = getMissionMarkerLayers().find(item =>
            normaliseMissionId(item?.mission_id ?? item?.missionId ?? item?.options?.mission_id ?? item?.options?.missionId) === missionId
        );
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
            const ring = pageWindow.L.circleMarker(latLng, {
                radius: 10, interactive: false, bubblingMouseEvents: false,
                className: 'mcms-mission-spawn-ring', pane: 'overlayPane'
            });
            const pane = ensureMissionFloatPane(map) || 'markerPane';
            const label = pageWindow.L.marker(latLng, {
                interactive: false, keyboard: false, bubblingMouseEvents: false, pane,
                icon: pageWindow.L.divIcon({
                    className: 'mcms-mission-spawn-label-icon',
                    html: `<span class="mcms-mission-spawn-label">${personal ? 'NEW INCIDENT' : 'NEW ALLIANCE INCIDENT'}</span>`,
                    iconSize: [0, 0], iconAnchor: [0, 34]
                })
            });
            ring.__mcmsMissionSpawnRing = true;
            label.__mcmsMissionSpawnLabel = true;
            ring.addTo(group);
            label.addTo(group);
            group.addTo(map);
        } catch (err) {}
        runtimeSetTimeout(() => {
            marker._icon?.classList?.remove('mcms-mission-spawn-focus');
            try { group.clearLayers(); group.remove(); } catch (err) {}
        }, MISSION_SPAWN_DURATION_MS);
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
        for (const marker of getMissionMarkerLayers()) {
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
        document.getElementById(SCRIPT.criticalDrawerId)?.classList.remove('mcms-open');
        hideMissionInspector();
        missionSpawnArmed = false;
        runtimeClearTimeout(missionSpawnPrimeTimer);
        knownMissionIds.clear();
        if (state.missionSpawn.enabled) primeMissionSpawnDetector();
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
        return `MC Map Command ${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}-${pad(date.getMinutes())}-${pad(date.getSeconds())}.json`;
    }

    function buildToolkitSettingsBackup(exportedAt = new Date()) {
        const discordWebhook = getDiscordWebhookUrl();
        return {
            format: 'MissionChief Map Command Toolkit Settings Backup',
            schema: 2,
            version: SCRIPT.version,
            exportedAt: exportedAt.toISOString(),
            state: clonePlainData(state),
            integrations: {
                discordWebhook
            },
            containsSensitiveData: Boolean(discordWebhook)
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
                            title: 'MC Map Command settings backup'
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

    function applyImportedToolkitSettings(parsed) {
        const importedState = extractImportedToolkitState(parsed);
        if (!importedState) throw new Error('The file does not contain MissionChief Map Command settings.');

        const importedWebhook = extractImportedDiscordWebhook(parsed);
        const normalisedWebhook = importedWebhook.present ? normaliseDiscordWebhookUrl(importedWebhook.value) : '';
        const previousStateRaw = localStorage.getItem(SCRIPT.storageState);
        const previousWebhook = getDiscordWebhookUrl();

        try {
            localStorage.setItem(SCRIPT.storageState, JSON.stringify(importedState));
            state = loadState();
            saveState();
            if (importedWebhook.present) saveDiscordWebhookUrl(normalisedWebhook);
            applyLoadedConfiguration();
        } catch (err) {
            try {
                if (previousStateRaw === null) localStorage.removeItem(SCRIPT.storageState);
                else localStorage.setItem(SCRIPT.storageState, previousStateRaw);
                state = loadState();
                saveDiscordWebhookUrl(previousWebhook);
                applyLoadedConfiguration();
            } catch (rollbackError) {}
            throw err;
        }

        return importedWebhook.present;
    }

    function importToolkitConfigFile(file) {
        if (!file) return;
        if (Number(file.size) > 5 * 1024 * 1024) {
            showToast('Import failed: settings file is too large');
            return;
        }
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const parsed = JSON.parse(String(reader.result || ''));
                const importedWebhook = applyImportedToolkitSettings(parsed);
                showToast(importedWebhook ? 'All toolkit settings imported' : 'Toolkit settings imported · existing webhook kept');
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
        payoutMediaPrimed = false;
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
            payoutMediaPrimed = false;
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
            payoutMediaPrimed = true;
            return true;
        } catch (err) {
            console.warn(`[${SCRIPT.name}] Hosted payout audio was blocked or unavailable; using synthesized fallback.`, err);
            return false;
        }
    }

    function unlockPayoutAudio() {
        if (!state.payoutFlash.soundEnabled) return null;
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
        if (!overlay) return false;

        let left = 0;
        let top = 0;
        let width = Math.max(1, pageWindow.innerWidth || document.documentElement.clientWidth || 1);
        let height = Math.max(1, pageWindow.innerHeight || document.documentElement.clientHeight || 1);
        let radius = '0px';

        if (mapEl) {
            const rect = mapEl.getBoundingClientRect();
            const mapLeft = Math.max(0, Math.round(rect.left));
            const mapTop = Math.max(0, Math.round(rect.top));
            const mapRight = Math.min(width, Math.round(rect.right));
            const mapBottom = Math.min(height, Math.round(rect.bottom));
            const mapWidth = Math.max(0, mapRight - mapLeft);
            const mapHeight = Math.max(0, mapBottom - mapTop);

            if (mapWidth >= 40 && mapHeight >= 40) {
                left = mapLeft;
                top = mapTop;
                width = mapWidth;
                height = mapHeight;
                try { radius = pageWindow.getComputedStyle(mapEl).borderRadius || '0px'; }
                catch (err) {}
            }
        }

        overlay.style.setProperty('position', 'fixed', 'important');
        overlay.style.setProperty('left', `${left}px`, 'important');
        overlay.style.setProperty('top', `${top}px`, 'important');
        overlay.style.setProperty('right', 'auto', 'important');
        overlay.style.setProperty('bottom', 'auto', 'important');
        overlay.style.setProperty('width', `${width}px`, 'important');
        overlay.style.setProperty('height', `${height}px`, 'important');
        overlay.style.setProperty('border-radius', radius, 'important');
        overlay.style.setProperty('z-index', '2147483647', 'important');
        overlay.style.setProperty('pointer-events', 'none', 'important');
        overlay.style.setProperty('display', 'block', 'important');
        overlay.style.setProperty('visibility', 'visible', 'important');
        return true;
    }

    function ensurePayoutFlashOverlay() {
        let overlay = document.getElementById(SCRIPT.payoutFlashId);
        const preferredParent = document.documentElement;

        if (overlay && overlay.parentElement !== preferredParent) overlay.remove();
        overlay = document.getElementById(SCRIPT.payoutFlashId);

        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = SCRIPT.payoutFlashId;
            overlay.setAttribute('aria-hidden', 'true');
            overlay.setAttribute('role', 'presentation');
            overlay.innerHTML = `
                <div class="mcms-payout-light mcms-payout-red"></div>
                <div class="mcms-payout-light mcms-payout-blue"></div>
                <div class="mcms-payout-cinematic"></div>
                <div class="mcms-payout-vc-sunset"></div>
                <div class="mcms-payout-vc-grid"></div>
                <div class="mcms-payout-bc-dust"></div>
                <div class="mcms-payout-bc-hud"></div>
                <div class="mcms-payout-bc-embers">
                    <i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i>
                    <i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i>
                    <i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i>
                    <i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i>
                    <i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i>
                    <i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i><i class="mcms-payout-bc-ember"></i>
                </div>
                <div class="mcms-payout-theme-fx mcms-payout-theme-fx-a"></div>
                <div class="mcms-payout-theme-fx mcms-payout-theme-fx-b"></div>
                <div class="mcms-payout-theme-fx mcms-payout-theme-fx-c"></div>
                <div class="mcms-payout-theme-particles">
                    <i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i>
                    <i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i>
                    <i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i><i class="mcms-payout-theme-particle"></i>
                </div>
                <div class="mcms-payout-particles"></div>
                <div class="mcms-payout-banner">
                    <span class="mcms-payout-tier">STANDARD PAYOUT</span>
                    <span class="mcms-payout-title">Mission Complete</span>
                    <span class="mcms-payout-mission"></span>
                    <span class="mcms-payout-divider"></span>
                    <span class="mcms-payout-source">CREDIT AWARD</span>
                    <span class="mcms-payout-kicker">Payout received</span>
                    <strong class="mcms-payout-amount">+0 CREDITS</strong>
                </div>
            `;
            preferredParent.appendChild(overlay);
        }

        // Inline fallback styling makes the effect independent of external/game CSS.
        overlay.style.setProperty('opacity', '0', 'important');
        overlay.style.setProperty('overflow', 'hidden', 'important');
        overlay.style.setProperty('background', 'transparent', 'important');

        const red = overlay.querySelector('.mcms-payout-red');
        const blue = overlay.querySelector('.mcms-payout-blue');
        const cinematic = overlay.querySelector('.mcms-payout-cinematic');
        const viceSunset = overlay.querySelector('.mcms-payout-vc-sunset');
        const viceGrid = overlay.querySelector('.mcms-payout-vc-grid');
        const badDust = overlay.querySelector('.mcms-payout-bc-dust');
        const badHud = overlay.querySelector('.mcms-payout-bc-hud');
        const badEmbers = overlay.querySelector('.mcms-payout-bc-embers');
        const themeFxA = overlay.querySelector('.mcms-payout-theme-fx-a');
        const themeFxB = overlay.querySelector('.mcms-payout-theme-fx-b');
        const themeFxC = overlay.querySelector('.mcms-payout-theme-fx-c');
        const themeParticles = overlay.querySelector('.mcms-payout-theme-particles');
        const banner = overlay.querySelector('.mcms-payout-banner');

        for (const light of [red, blue]) {
            if (!light) continue;
            light.style.setProperty('position', 'absolute', 'important');
            light.style.setProperty('inset', '-12%', 'important');
            light.style.setProperty('opacity', '0');
            light.style.setProperty('pointer-events', 'none', 'important');
        }
        if (cinematic) {
            cinematic.style.setProperty('position', 'absolute', 'important');
            cinematic.style.setProperty('inset', '0', 'important');
            cinematic.style.setProperty('opacity', '0');
            cinematic.style.setProperty('pointer-events', 'none', 'important');
        }
        for (const layer of [viceSunset, viceGrid, badDust, badHud, badEmbers, themeFxA, themeFxB, themeFxC, themeParticles]) {
            if (!layer) continue;
            layer.style.setProperty('position', 'absolute', 'important');
            layer.style.setProperty('opacity', '0');
            layer.style.setProperty('pointer-events', 'none', 'important');
        }
        if (red) red.style.setProperty('background', 'radial-gradient(ellipse at 0% 45%, rgba(255,22,22,.72) 0%, rgba(255,22,22,.36) 27%, rgba(255,22,22,0) 64%), linear-gradient(90deg, rgba(255,18,18,.42) 0%, rgba(255,18,18,0) 52%)', 'important');
        if (blue) blue.style.setProperty('background', 'radial-gradient(ellipse at 100% 55%, rgba(25,113,255,.76) 0%, rgba(25,113,255,.38) 27%, rgba(25,113,255,0) 64%), linear-gradient(270deg, rgba(20,103,255,.44) 0%, rgba(20,103,255,0) 52%)', 'important');

        if (banner) {
            banner.style.setProperty('position', 'absolute', 'important');
            banner.style.setProperty('left', '50%', 'important');
            banner.style.setProperty('top', '50%', 'important');
            banner.style.setProperty('transform', 'translate(-50%, -44%) scale(1.08)');
            banner.style.setProperty('filter', 'blur(7px)');
            banner.style.setProperty('opacity', '0');
            banner.style.setProperty('display', 'block', 'important');
            banner.style.setProperty('visibility', 'visible', 'important');
            banner.style.setProperty('pointer-events', 'none', 'important');
        }

        return positionPayoutFlashOverlay(overlay) ? overlay : null;
    }

    function stopPayoutFlashAnimation(overlay = document.getElementById(SCRIPT.payoutFlashId)) {
        runtimeClearTimeout(payoutFlashTimer);
        stopPayoutMediaAudio(true);
        runtimeClearInterval(payoutFlashFallbackInterval);
        payoutFlashFallbackInterval = null;
        if (payoutAmountAnimationFrame) runtimeCancelAnimationFrame(payoutAmountAnimationFrame);
        payoutAmountAnimationFrame = null;
        for (const animation of payoutFlashAnimations) {
            try { animation.cancel(); } catch (err) {}
        }
        payoutFlashAnimations = [];

        if (!overlay) return;
        overlay.classList.remove('mcms-payout-active');
        overlay.style.setProperty('opacity', '0', 'important');
        const red = overlay.querySelector('.mcms-payout-red');
        const blue = overlay.querySelector('.mcms-payout-blue');
        const cinematic = overlay.querySelector('.mcms-payout-cinematic');
        const viceSunset = overlay.querySelector('.mcms-payout-vc-sunset');
        const viceGrid = overlay.querySelector('.mcms-payout-vc-grid');
        const badDust = overlay.querySelector('.mcms-payout-bc-dust');
        const badHud = overlay.querySelector('.mcms-payout-bc-hud');
        const badEmbers = overlay.querySelector('.mcms-payout-bc-embers');
        const themeFxA = overlay.querySelector('.mcms-payout-theme-fx-a');
        const themeFxB = overlay.querySelector('.mcms-payout-theme-fx-b');
        const themeFxC = overlay.querySelector('.mcms-payout-theme-fx-c');
        const themeParticles = overlay.querySelector('.mcms-payout-theme-particles');
        const banner = overlay.querySelector('.mcms-payout-banner');
        if (red) {
            red.style.removeProperty('animation');
            red.style.setProperty('opacity', '0');
        }
        if (blue) {
            blue.style.removeProperty('animation');
            blue.style.setProperty('opacity', '0');
        }
        if (cinematic) cinematic.style.setProperty('opacity', '0');
        if (viceSunset) viceSunset.style.setProperty('opacity', '0');
        if (viceGrid) viceGrid.style.setProperty('opacity', '0');
        if (badDust) badDust.style.setProperty('opacity', '0');
        if (badHud) badHud.style.setProperty('opacity', '0');
        if (badEmbers) badEmbers.style.setProperty('opacity', '0');
        for (const layer of [themeFxA, themeFxB, themeFxC, themeParticles]) {
            if (!layer) continue;
            layer.style.setProperty('opacity', '0');
            layer.style.removeProperty('transform');
            layer.style.removeProperty('background-position');
            layer.style.removeProperty('filter');
        }
        for (const particle of overlay.querySelectorAll('.mcms-payout-theme-particle')) {
            particle.style.setProperty('opacity', '0');
            particle.style.removeProperty('left');
            particle.style.removeProperty('top');
            particle.style.removeProperty('bottom');
            particle.style.removeProperty('width');
            particle.style.removeProperty('height');
            particle.style.removeProperty('transform');
        }
        for (const ember of overlay.querySelectorAll('.mcms-payout-bc-ember')) {
            ember.style.setProperty('opacity', '0');
            ember.style.removeProperty('transform');
        }
        if (banner) {
            banner.style.removeProperty('animation');
            banner.style.setProperty('opacity', '0');
            banner.style.setProperty('transform', 'translate(-50%, -44%) scale(1.08)');
            banner.style.setProperty('filter', 'blur(7px)');
        }
        try {
            if (typeof overlay.hidePopover === 'function' && overlay.matches(':popover-open')) overlay.hidePopover();
        } catch (err) {}
    }

    function animateAdditionalPayoutTemplate(template, elements, duration, reducedMotion) {
        const animations = [];
        const meta = payoutTemplateMeta(template);
        const { fxA, fxB, fxC, particles, particleElements } = elements;
        if (['gta5', 'viceCity', 'badCompany'].includes(template)) return animations;

        const layerOptions = { duration, easing: 'ease-out', fill: 'both' };
        if (fxA) animations.push(fxA.animate([
            { opacity: 0, transform: 'scale(1.06)' },
            { opacity: reducedMotion ? .34 : .72, transform: 'scale(1)', offset: .08 },
            { opacity: reducedMotion ? .30 : .58, transform: 'scale(1.025)', offset: .92 },
            { opacity: 0, transform: 'scale(1.05)' }
        ], layerOptions));
        if (fxB) animations.push(fxB.animate([
            { opacity: 0, backgroundPosition: '0 0, 0 0' },
            { opacity: reducedMotion ? .24 : .54, backgroundPosition: '0 0, 0 0', offset: .08 },
            { opacity: reducedMotion ? .22 : .42, backgroundPosition: '0 30px, 80px 0', offset: .92 },
            { opacity: 0, backgroundPosition: '0 45px, 120px 0' }
        ], { ...layerOptions, easing: 'linear' }));
        if (fxC) {
            const fxCFrames = template === 'galactic'
                ? [
                    { opacity: 0, transform: 'rotate(-8deg) scale(1.06)' },
                    { opacity: reducedMotion ? .22 : .50, transform: 'rotate(0deg) scale(1)', offset: .10 },
                    { opacity: reducedMotion ? .20 : .38, transform: 'rotate(14deg) scale(1.03)', offset: .90 },
                    { opacity: 0, transform: 'rotate(20deg) scale(1.06)' }
                ]
                : template === 'scarface'
                    ? [
                        { opacity: 0, transform: 'translate3d(-18%,0,0) skewX(-9deg) scaleX(.72)' },
                        { opacity: reducedMotion ? .20 : .66, transform: 'translate3d(108%,0,0) skewX(-9deg) scaleX(1)', offset: .14 },
                        { opacity: reducedMotion ? .18 : .42, transform: 'translate3d(205%,0,0) skewX(-9deg) scaleX(.82)', offset: .86 },
                        { opacity: 0, transform: 'translate3d(250%,0,0) skewX(-9deg) scaleX(.58)' }
                    ]
                    : [
                        { opacity: 0, transform: 'scale(1.05)' },
                        { opacity: reducedMotion ? .22 : .50, transform: 'scale(1)', offset: .10 },
                        { opacity: reducedMotion ? .20 : .38, transform: 'scale(1.03)', offset: .90 },
                        { opacity: 0, transform: 'scale(1.06)' }
                    ];
            animations.push(fxC.animate(fxCFrames, layerOptions));
        }

        if (!particles || meta.particleMode === 'none' || reducedMotion) return animations;
        animations.push(particles.animate([{ opacity: 0 }, { opacity: .92, offset: .06 }, { opacity: .78, offset: .92 }, { opacity: 0 }], layerOptions));

        particleElements.forEach((particle, index) => {
            const seedA = (index * 37) % 97;
            const seedB = (index * 61) % 89;
            let frames;
            let options;
            particle.style.removeProperty('border-radius');

            if (meta.particleMode === 'glitch') {
                const top = 8 + seedA * .84;
                const width = 8 + (index % 6) * 5;
                particle.style.setProperty('top', `${top}%`);
                particle.style.setProperty('left', '-12%');
                particle.style.setProperty('width', `${width}px`);
                particle.style.setProperty('height', `${2 + (index % 2)}px`);
                frames = [
                    { opacity: 0, transform: 'translate3d(0,0,0) skewX(-18deg)' },
                    { opacity: .92, transform: `translate3d(${18 + seedB}vw,0,0) skewX(-18deg)`, offset: .14 },
                    { opacity: .58, transform: `translate3d(${78 + seedA * .35}vw,${(index % 3 - 1) * 8}px,0) skewX(-18deg)`, offset: .76 },
                    { opacity: 0, transform: 'translate3d(118vw,0,0) skewX(-18deg)' }
                ];
                const cycle = 950 + (index % 5) * 160;
                options = { duration: cycle, iterations: Math.ceil(duration / cycle) + 1, delay: -((index * 131) % cycle), easing: 'steps(7,end)', fill: 'both' };
            } else if (meta.particleMode === 'embers') {
                particle.style.setProperty('left', `${3 + seedA}%`);
                particle.style.setProperty('bottom', '-16px');
                particle.style.setProperty('width', `${2 + (index % 3)}px`);
                particle.style.setProperty('height', `${7 + (index % 5) * 2}px`);
                const drift = -38 + seedB;
                const rise = 55 + (seedA % 38);
                frames = [
                    { opacity: 0, transform: 'translate3d(0,10px,0) scale(.5)' },
                    { opacity: .96, transform: `translate3d(${drift * .15}px,-${rise * .16}vh,0) scale(1)`, offset: .14 },
                    { opacity: .70, transform: `translate3d(${drift * .72}px,-${rise * .74}vh,0) rotate(${index % 2 ? 22 : -22}deg) scale(.78)`, offset: .78 },
                    { opacity: 0, transform: `translate3d(${drift}px,-${rise}vh,0) rotate(${index % 2 ? 38 : -38}deg) scale(.25)` }
                ];
                const cycle = 1400 + (index % 7) * 170;
                options = { duration: cycle, iterations: Math.ceil(duration / cycle) + 1, delay: -((index * 173) % cycle), easing: 'cubic-bezier(.18,.62,.30,1)', fill: 'both' };
            } else if (meta.particleMode === 'ash') {
                particle.style.setProperty('left', `${2 + seedA}%`);
                particle.style.setProperty('top', '-10px');
                particle.style.setProperty('width', `${2 + (index % 3)}px`);
                particle.style.setProperty('height', `${2 + (index % 3)}px`);
                const fall = 65 + (seedB % 35);
                const drift = -45 + seedA;
                frames = [
                    { opacity: 0, transform: 'translate3d(0,-8px,0) rotate(0deg)' },
                    { opacity: .72, transform: `translate3d(${drift * .18}px,${fall * .12}vh,0) rotate(80deg)`, offset: .16 },
                    { opacity: .48, transform: `translate3d(${drift * .72}px,${fall * .76}vh,0) rotate(250deg)`, offset: .78 },
                    { opacity: 0, transform: `translate3d(${drift}px,${fall}vh,0) rotate(360deg)` }
                ];
                const cycle = 2200 + (index % 6) * 250;
                options = { duration: cycle, iterations: Math.ceil(duration / cycle) + 1, delay: -((index * 197) % cycle), easing: 'linear', fill: 'both' };
            } else if (meta.particleMode === 'dust') {
                particle.style.setProperty('left', `${4 + seedA * .92}%`);
                particle.style.setProperty('top', `${8 + seedB * .88}%`);
                particle.style.setProperty('width', `${1 + (index % 2)}px`);
                particle.style.setProperty('height', `${1 + (index % 2)}px`);
                frames = [
                    { opacity: 0, transform: 'translate3d(-8px,8px,0)' },
                    { opacity: .62, transform: 'translate3d(0,0,0)', offset: .18 },
                    { opacity: .32, transform: `translate3d(${18 + seedA * .30}px,-${12 + seedB * .18}px,0)`, offset: .82 },
                    { opacity: 0, transform: `translate3d(${32 + seedA * .36}px,-${22 + seedB * .22}px,0)` }
                ];
                const cycle = 1800 + (index % 5) * 260;
                options = { duration: cycle, iterations: Math.ceil(duration / cycle) + 1, delay: -((index * 149) % cycle), easing: 'ease-in-out', fill: 'both' };
            } else if (meta.particleMode === 'stars') {
                particle.style.setProperty('left', `${4 + seedA * .92}%`);
                particle.style.setProperty('top', `${5 + seedB}%`);
                const size = 1 + (index % 3);
                const starRotation = template === 'scarface' ? ' rotate(45deg)' : '';
                particle.style.setProperty('width', `${size}px`);
                particle.style.setProperty('height', `${size}px`);
                frames = [
                    { opacity: .08, transform: `scale(.6)${starRotation}` },
                    { opacity: .95, transform: `scale(1.45)${starRotation}`, offset: .30 },
                    { opacity: .18, transform: `translate3d(${(index % 2 ? 1 : -1) * (8 + seedA * .12)}px,${-8 - seedB * .08}px,0) scale(.7)${starRotation}`, offset: .72 },
                    { opacity: .80, transform: `scale(1.1)${starRotation}` }
                ];
                const cycle = 1200 + (index % 7) * 190;
                options = { duration: cycle, iterations: Math.ceil(duration / cycle) + 1, delay: -((index * 167) % cycle), easing: 'ease-in-out', fill: 'both' };
            } else {
                particle.style.setProperty('left', `${4 + seedA * .92}%`);
                particle.style.setProperty('top', `${8 + seedB * .88}%`);
                const size = 4 + (index % 4) * 2;
                particle.style.setProperty('width', `${size}px`);
                particle.style.setProperty('height', `${size}px`);
                frames = [
                    { opacity: 0, transform: 'translate3d(0,12px,0) scale(.3) rotate(0deg)' },
                    { opacity: .94, transform: 'translate3d(0,0,0) scale(1) rotate(0deg)', offset: .16 },
                    { opacity: .62, transform: `translate3d(${(index % 2 ? 1 : -1) * (18 + seedA * .25)}px,-${22 + seedB * .25}px,0) scale(.8) rotate(90deg)`, offset: .72 },
                    { opacity: 0, transform: `translate3d(${(index % 2 ? 1 : -1) * (28 + seedA * .35)}px,-${38 + seedB * .32}px,0) scale(.35) rotate(180deg)` }
                ];
                const cycle = 1250 + (index % 6) * 180;
                options = { duration: cycle, iterations: Math.ceil(duration / cycle) + 1, delay: -((index * 157) % cycle), easing: 'steps(8,end)', fill: 'both' };
            }
            animations.push(particle.animate(frames, options));
        });
        return animations;
    }

    function triggerPayoutFlash(amount, force = false, context = null, options = {}) {
        const credits = Math.max(0, Math.round(Number(amount) || 0));
        if (!force && (!state.payoutFlash.enabled || credits < state.payoutFlash.threshold)) return false;

        const overlay = ensurePayoutFlashOverlay();
        if (!overlay) return false;
        stopPayoutFlashAnimation(overlay);
        positionPayoutFlashOverlay(overlay);

        const duration = normalisePayoutFlashDuration(options.durationMs ?? state.payoutFlash.durationMs);
        const templateKey = PAYOUT_TEMPLATES[options.template] ? options.template : state.payoutFlash.template;
        const resolvedContext = context || (force ? { source: 'personal', caption: 'Emergency Response Test' } : { source: 'unknown', caption: '' });
        const presentation = payoutPresentation(credits, resolvedContext);
        overlay.dataset.tier = presentation.tier;
        overlay.dataset.source = presentation.source;
        overlay.dataset.template = templateKey;
        overlay.style.setProperty('--mcms-payout-accent', presentation.colour);
        overlay.style.setProperty('--mcms-payout-accent-soft', presentation.soft);
        overlay.style.setProperty('--mcms-payout-glow', presentation.glow);

        const amountElement = overlay.querySelector('.mcms-payout-amount');
        const titleElement = overlay.querySelector('.mcms-payout-title');
        const missionElement = overlay.querySelector('.mcms-payout-mission');
        const sourceElement = overlay.querySelector('.mcms-payout-source');
        const tierElement = overlay.querySelector('.mcms-payout-tier');
        const red = overlay.querySelector('.mcms-payout-red');
        const blue = overlay.querySelector('.mcms-payout-blue');
        const cinematic = overlay.querySelector('.mcms-payout-cinematic');
        const viceSunset = overlay.querySelector('.mcms-payout-vc-sunset');
        const viceGrid = overlay.querySelector('.mcms-payout-vc-grid');
        const badDust = overlay.querySelector('.mcms-payout-bc-dust');
        const badHud = overlay.querySelector('.mcms-payout-bc-hud');
        const badEmbers = overlay.querySelector('.mcms-payout-bc-embers');
        const emberElements = Array.from(overlay.querySelectorAll('.mcms-payout-bc-ember'));
        const themeFxA = overlay.querySelector('.mcms-payout-theme-fx-a');
        const themeFxB = overlay.querySelector('.mcms-payout-theme-fx-b');
        const themeFxC = overlay.querySelector('.mcms-payout-theme-fx-c');
        const themeParticles = overlay.querySelector('.mcms-payout-theme-particles');
        const themeParticleElements = Array.from(overlay.querySelectorAll('.mcms-payout-theme-particle'));
        const particles = overlay.querySelector('.mcms-payout-particles');
        const kickerElement = overlay.querySelector('.mcms-payout-kicker');
        const banner = overlay.querySelector('.mcms-payout-banner');
        if (titleElement) {
            const formattedTitle = formatPayoutTitleForTemplate(payoutTitleForTemplate(presentation, templateKey), templateKey);
            titleElement.textContent = formattedTitle;
            titleElement.classList.remove('mcms-payout-title-long', 'mcms-payout-title-very-long');
            const titleLength = formattedTitle.replace(/\s+/g, ' ').trim().length;
            if (titleLength >= 23) titleElement.classList.add('mcms-payout-title-very-long');
            else if (titleLength >= 17) titleElement.classList.add('mcms-payout-title-long');
        }
        if (missionElement) missionElement.textContent = presentation.caption;
        if (sourceElement) sourceElement.textContent = presentation.label;
        if (tierElement) tierElement.textContent = presentation.tierLabel;
        if (kickerElement) kickerElement.textContent = payoutTemplateMeta(templateKey).kicker;

        try {
            if (typeof overlay.showPopover === 'function') {
                if (!overlay.hasAttribute('popover')) overlay.setAttribute('popover', 'manual');
                if (!overlay.matches(':popover-open')) overlay.showPopover();
            }
        } catch (err) {}

        overlay.style.setProperty('opacity', '1', 'important');
        overlay.classList.add('mcms-payout-active');

        const reducedMotion = Boolean(pageWindow.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
        animatePayoutAmount(amountElement, credits, duration, reducedMotion);
        playPayoutSound(presentation.tier, templateKey);

        if (typeof overlay.animate === 'function' && red && blue && banner) {
            red.style.setProperty('animation', 'none', 'important');
            blue.style.setProperty('animation', 'none', 'important');
            banner.style.setProperty('animation', 'none', 'important');
            const pulseCycleMs = reducedMotion ? 1200 : 720;
            const pulseIterations = Math.max(1, Math.ceil(duration / pulseCycleMs));
            const pulseOptions = { duration: pulseCycleMs, iterations: pulseIterations, easing: 'ease-in-out', fill: 'both' };
            const redFrames = reducedMotion
                ? [{ opacity: .20 }, { opacity: .28 }, { opacity: .20 }]
                : [{ opacity: 0, offset: 0 }, { opacity: .88, offset: .10 }, { opacity: .88, offset: .28 }, { opacity: 0, offset: .42 }, { opacity: 0, offset: 1 }];
            const blueFrames = reducedMotion
                ? [{ opacity: .18 }, { opacity: .26 }, { opacity: .18 }]
                : [{ opacity: 0, offset: 0 }, { opacity: 0, offset: .42 }, { opacity: .90, offset: .54 }, { opacity: .90, offset: .72 }, { opacity: 0, offset: .86 }, { opacity: 0, offset: 1 }];
            const activeAnimations = [
                red.animate(redFrames, pulseOptions),
                blue.animate(blueFrames, pulseOptions),
                banner.animate([
                    { opacity: 0, transform: 'translate(-50%, -44%) scale(1.08)', filter: 'blur(8px)' },
                    { opacity: 1, transform: 'translate(-50%, -50%) scale(1)', filter: 'blur(0)', offset: .05 },
                    { opacity: 1, transform: 'translate(-50%, -50%) scale(1)', filter: 'blur(0)', offset: .94 },
                    { opacity: 0, transform: 'translate(-50%, -56%) scale(.985)', filter: 'blur(2px)' }
                ], { duration, easing: 'cubic-bezier(.16,.78,.24,1)', fill: 'both' })
            ];
            if (cinematic) activeAnimations.push(cinematic.animate([{ opacity: 0 }, { opacity: .72, offset: .06 }, { opacity: .72, offset: .94 }, { opacity: 0 }], { duration, easing: 'ease-out', fill: 'both' }));
            if (templateKey === 'viceCity') {
                if (viceSunset) activeAnimations.push(viceSunset.animate([
                    { opacity: 0, transform: 'scale(1.08)' },
                    { opacity: .72, transform: 'scale(1)', offset: .08 },
                    { opacity: .62, transform: 'scale(1.025)', offset: .92 },
                    { opacity: 0, transform: 'scale(1.05)' }
                ], { duration, easing: 'ease-out', fill: 'both' }));
                if (viceGrid) activeAnimations.push(viceGrid.animate([
                    { opacity: 0, transform: 'perspective(380px) rotateX(62deg) scale(1.42) translateY(14px)' },
                    { opacity: .54, transform: 'perspective(380px) rotateX(62deg) scale(1.35) translateY(0)', offset: .10 },
                    { opacity: .38, transform: 'perspective(380px) rotateX(62deg) scale(1.31) translateY(-12px)', offset: .90 },
                    { opacity: 0, transform: 'perspective(380px) rotateX(62deg) scale(1.28) translateY(-18px)' }
                ], { duration, easing: 'linear', fill: 'both' }));
            }
            if (templateKey === 'badCompany') {
                if (badDust) activeAnimations.push(badDust.animate([
                    { opacity: 0, transform: 'scale(1.10) translate3d(-1.5%, 1%, 0)' },
                    { opacity: .62, transform: 'scale(1.02) translate3d(0, 0, 0)', offset: .09 },
                    { opacity: .48, transform: 'scale(1.06) translate3d(1.2%, -1%, 0)', offset: .90 },
                    { opacity: 0, transform: 'scale(1.09) translate3d(2%, -1.5%, 0)' }
                ], { duration, easing: 'ease-out', fill: 'both' }));
                if (badHud) activeAnimations.push(badHud.animate([
                    { opacity: 0, backgroundPosition: '0 0, 0 0, 0 0, 0 0' },
                    { opacity: .52, backgroundPosition: '0 0, 0 0, 0 0, 0 0', offset: .08 },
                    { opacity: .35, backgroundPosition: '0 0, 0 0, 0 24px, 95px 0', offset: .92 },
                    { opacity: 0, backgroundPosition: '0 0, 0 0, 0 30px, 130px 0' }
                ], { duration, easing: 'linear', fill: 'both' }));
                if (badEmbers) activeAnimations.push(badEmbers.animate([
                    { opacity: 0 },
                    { opacity: .92, offset: .06 },
                    { opacity: .82, offset: .92 },
                    { opacity: 0 }
                ], { duration, easing: 'ease-out', fill: 'both' }));
                emberElements.forEach((ember, index) => {
                    const cycle = 1450 + (index % 7) * 185;
                    const iterations = Math.max(2, Math.ceil(duration / cycle) + 1);
                    const left = 3 + ((index * 37) % 94);
                    const drift = -42 + ((index * 29) % 85);
                    const rise = 58 + ((index * 19) % 34);
                    const size = 2 + (index % 3);
                    ember.style.setProperty('left', `${left}%`);
                    ember.style.setProperty('width', `${size}px`);
                    ember.style.setProperty('height', `${7 + (index % 5) * 2}px`);
                    activeAnimations.push(ember.animate([
                        { opacity: 0, transform: `translate3d(0, 10px, 0) rotate(${index % 2 ? -12 : 12}deg) scale(.55)`, offset: 0 },
                        { opacity: .96, transform: `translate3d(${drift * .18}px, -${rise * .18}px, 0) rotate(${index % 2 ? -4 : 4}deg) scale(1)`, offset: .14 },
                        { opacity: .72, transform: `translate3d(${drift * .72}px, -${rise * .72}vh, 0) rotate(${index % 2 ? 18 : -18}deg) scale(.82)`, offset: .76 },
                        { opacity: 0, transform: `translate3d(${drift}px, -${rise}vh, 0) rotate(${index % 2 ? 32 : -32}deg) scale(.30)`, offset: 1 }
                    ], {
                        duration: cycle,
                        iterations,
                        delay: -((index * 173) % cycle),
                        easing: 'cubic-bezier(.18,.62,.30,1)',
                        fill: 'both'
                    }));
                });
            }
            activeAnimations.push(...animateAdditionalPayoutTemplate(templateKey, {
                fxA: themeFxA,
                fxB: themeFxB,
                fxC: themeFxC,
                particles: themeParticles,
                particleElements: themeParticleElements
            }, duration, reducedMotion));
            if (particles && ['high', 'elite'].includes(presentation.tier)) activeAnimations.push(particles.animate([{ opacity: 0, transform:'scale(1.08) translateY(10px)' }, { opacity: presentation.tier === 'elite' ? .58 : .38, transform:'scale(1) translateY(0)', offset:.12 }, { opacity: .22, transform:'scale(1.02) translateY(-8px)', offset:.88 }, { opacity:0, transform:'scale(1.05) translateY(-14px)' }], { duration, easing:'ease-out', fill:'both' }));
            payoutFlashAnimations.push(...activeAnimations);
        } else {
            let bluePhase = false;
            if (cinematic) cinematic.style.setProperty('opacity', '.72');
            if (templateKey === 'viceCity') {
                if (viceSunset) viceSunset.style.setProperty('opacity', '.68');
                if (viceGrid) viceGrid.style.setProperty('opacity', '.48');
            }
            if (templateKey === 'badCompany') {
                if (badDust) badDust.style.setProperty('opacity', '.62');
                if (badHud) badHud.style.setProperty('opacity', '.46');
                if (badEmbers) badEmbers.style.setProperty('opacity', '.82');
                emberElements.forEach((ember, index) => {
                    ember.style.setProperty('left', `${4 + ((index * 37) % 92)}%`);
                    ember.style.setProperty('opacity', index % 3 === 0 ? '.9' : '.45');
                    ember.style.setProperty('transform', `translateY(-${14 + (index % 8) * 7}vh)`);
                });
            }
            if (!['gta5', 'viceCity', 'badCompany'].includes(templateKey)) {
                if (themeFxA) themeFxA.style.setProperty('opacity', '.64');
                if (themeFxB) themeFxB.style.setProperty('opacity', '.42');
                if (themeFxC) themeFxC.style.setProperty('opacity', '.36');
                if (themeParticles && payoutTemplateMeta(templateKey).particleMode !== 'none') {
                    themeParticles.style.setProperty('opacity', '.72');
                    themeParticleElements.slice(0, 10).forEach((particle, index) => {
                        particle.style.setProperty('left', `${8 + ((index * 37) % 84)}%`);
                        particle.style.setProperty('top', `${10 + ((index * 29) % 76)}%`);
                        particle.style.setProperty('width', `${2 + (index % 3) * 2}px`);
                        particle.style.setProperty('height', `${2 + (index % 3) * 2}px`);
                        particle.style.setProperty('opacity', index % 2 ? '.45' : '.85');
                    });
                }
            }
            if (banner) {
                banner.style.setProperty('opacity', '1');
                banner.style.setProperty('transform', 'translate(-50%, -50%) scale(1)');
                banner.style.setProperty('filter', 'blur(0)');
            }
            payoutFlashFallbackInterval = runtimeSetInterval(() => {
                bluePhase = !bluePhase;
                if (red) red.style.setProperty('opacity', bluePhase ? '0' : '.84');
                if (blue) blue.style.setProperty('opacity', bluePhase ? '.88' : '0');
            }, reducedMotion ? 500 : 180);
        }

        payoutFlashTimer = runtimeSetTimeout(() => stopPayoutFlashAnimation(overlay), duration + 120);
        return true;
    }

    function processCreditTotal(value) {
        const total = parseCreditValue(value);
        if (total === null) return;

        if (lastObservedCredits === null) {
            lastObservedCredits = total;
            return;
        }

        if (total === lastObservedCredits) return;
        const previous = lastObservedCredits;
        lastObservedCredits = total;
        const gain = total - previous;
        if (gain <= 0) return;
        const context = resolvePayoutContext(gain);
        recordCreditGain(gain, context);
        if (gain >= state.payoutFlash.threshold) triggerPayoutFlash(gain, false, context);
    }

    function installCreditsUpdateHook() {
        let current;
        try { current = pageWindow.creditsUpdate; } catch (err) { return false; }
        if (typeof current !== 'function') return false;
        if (current.__mcmsPayoutFlashWrappedV313) return true;

        const original = current.__mcmsOriginal || current;
        const wrapped = function (...args) {
            const result = original.apply(this, args);
            if (args.length) processCreditTotal(args[0]);
            else processCreditTotal(readCurrentCreditTotal());
            return result;
        };

        try {
            Object.defineProperty(wrapped, '__mcmsPayoutFlashWrappedV313', { value: true });
            Object.defineProperty(wrapped, '__mcmsOriginal', { value: original });
            pageWindow.creditsUpdate = wrapped;
            if (pageWindow.creditsUpdate !== wrapped) return false;
            runtime.hookRestorers.push(() => {
                try {
                    if (pageWindow.creditsUpdate === wrapped) pageWindow.creditsUpdate = original;
                } catch (err) {}
            });
            return true;
        } catch (err) {
            return false;
        }
    }

    function observeCreditValue() {
        const element = document.querySelector('.credits-value');
        if (!element) return false;

        if (observedCreditsElement === element && creditsValueObserver) return true;
        if (creditsValueObserver) {
            try { creditsValueObserver.disconnect(); } catch (err) {}
            runtime.observers.delete(creditsValueObserver);
        }

        observedCreditsElement = element;
        processCreditTotal(element.textContent);
        creditsValueObserver = runtimeTrackObserver(new MutationObserver(() => processCreditTotal(element.textContent)));
        creditsValueObserver.observe(element, { childList: true, subtree: true, characterData: true });
        return true;
    }


    // --- Discord financial reporting ---------------------------------------------------------
    const DISCORD_WEBHOOK_HOSTS = new Set(['discord.com', 'ptb.discord.com', 'canary.discord.com', 'discordapp.com', 'ptb.discordapp.com', 'canary.discordapp.com']);
    const DISCORD_REQUEST_TIMEOUT_MS = 30000;
    const DISCORD_MAX_FIELD_LENGTH = 1024;
    const FINANCE_MAX_LEDGER_PAGES = 300;
    const FINANCE_FETCH_YIELD_EVERY = 5;
    const FINANCE_SESSION_STARTED_AT = Date.now();
    const FINANCE_PERIOD_IDS = new Set(['today', 'yesterday', 'last24', 'last7', 'last30', 'session', 'sinceLast', 'custom']);
    const FINANCE_CHART_FILENAME = 'missionchief-financial-report.png';
    let discordFinanceChartUrl = '';
    let discordFinanceChartBlobRef = null;

    /**
     * @template T
     * @param {string} key
     * @param {T} fallback
     * @returns {T}
     */
    function gmGetValueSafe(key, fallback) {
        try {
            if (typeof GM_getValue === 'function') return GM_getValue(key, fallback);
        } catch (err) {}
        return fallback;
    }

    function gmSetValueSafe(key, value) {
        try {
            if (typeof GM_setValue === 'function') {
                GM_setValue(key, value);
                return true;
            }
        } catch (err) {}
        return false;
    }

    function gmDeleteValueSafe(key) {
        try {
            if (typeof GM_deleteValue === 'function') {
                GM_deleteValue(key);
                return true;
            }
        } catch (err) {}
        return false;
    }

    function getDiscordWebhookUrl() {
        return String(gmGetValueSafe(SCRIPT.discordWebhookState, '') || '').trim();
    }

    function getLastDiscordReportAt() {
        const value = Number(gmGetValueSafe(SCRIPT.discordLastReportState, 0));
        return Number.isFinite(value) && value > 0 ? value : 0;
    }

    function normaliseDiscordWebhookUrl(rawValue) {
        const raw = String(rawValue || '').trim();
        if (!raw) return '';
        let parsed;
        try { parsed = new URL(raw); } catch (err) { throw new Error('The Discord webhook URL is not valid.'); }
        if (parsed.protocol !== 'https:' || !DISCORD_WEBHOOK_HOSTS.has(parsed.hostname.toLowerCase())) {
            throw new Error('Use a genuine HTTPS Discord webhook URL.');
        }
        if (!/^\/api(?:\/v\d+)?\/webhooks\/\d+\/[A-Za-z0-9._-]+\/?$/u.test(parsed.pathname)) {
            throw new Error('The URL does not contain a valid Discord webhook ID and token.');
        }
        parsed.hash = '';
        parsed.username = '';
        parsed.password = '';
        return parsed.toString();
    }

    function saveDiscordWebhookUrl(rawValue) {
        const normalised = normaliseDiscordWebhookUrl(rawValue);
        if (!normalised) {
            gmDeleteValueSafe(SCRIPT.discordWebhookState);
            return '';
        }
        if (!gmSetValueSafe(SCRIPT.discordWebhookState, normalised)) {
            throw new Error('Tampermonkey storage is unavailable.');
        }
        return normalised;
    }

    function readDiscordWebhookInput({ save = true } = {}) {
        const input = document.querySelector(`#${SCRIPT.panelId} [data-setting="discord-webhook"]`);
        const raw = String(input?.value || getDiscordWebhookUrl()).trim();
        return save ? saveDiscordWebhookUrl(raw) : normaliseDiscordWebhookUrl(raw);
    }

    function setDiscordStatus(message, tone = 'neutral') {
        discordFinanceStatus = String(message || '');
        discordFinanceStatusTone = ['neutral', 'good', 'bad', 'busy'].includes(tone) ? tone : 'neutral';
        const status = document.querySelector(`#${SCRIPT.panelId} [data-discord-status]`);
        if (status) {
            status.textContent = discordFinanceStatus;
            status.dataset.tone = discordFinanceStatusTone;
        }
    }

    function discordHttpRequest({ method = 'GET', url, data = null, headers = {} }) {
        return new Promise((resolve, reject) => {
            if (runtime.destroyed) {
                reject(new Error('Toolkit runtime stopped.'));
                return;
            }
            if (typeof GM_xmlhttpRequest !== 'function') {
                reject(new Error('Tampermonkey cross-origin requests are unavailable.'));
                return;
            }

            let request = null;
            let settled = false;
            const finish = (error, response = null) => {
                if (settled) return;
                settled = true;
                if (request) runtime.requests.delete(request);
                if (error) reject(error);
                else resolve(response);
            };

            try {
                request = GM_xmlhttpRequest({
                    method,
                    url,
                    data,
                    headers,
                    timeout: DISCORD_REQUEST_TIMEOUT_MS,
                    responseType: 'text',
                    onload: response => finish(null, response),
                    onerror: () => finish(new Error('Discord could not be reached.')),
                    ontimeout: () => finish(new Error('Discord request timed out.')),
                    onabort: () => finish(new Error('Discord request was cancelled.'))
                });
                if (!settled && request?.abort) runtime.requests.add(request);
            } catch (err) {
                finish(err instanceof Error ? err : new Error('Discord request could not be created.'));
            }
        });
    }

    function discordWebhookEndpoint(rawUrl, { wait = false, stripQuery = false } = {}) {
        const parsed = new URL(normaliseDiscordWebhookUrl(rawUrl));
        if (stripQuery) parsed.search = '';
        if (wait) parsed.searchParams.set('wait', 'true');
        return parsed.toString();
    }

    function parseDiscordError(response) {
        let detail = '';
        try {
            const body = JSON.parse(response?.responseText || '{}');
            detail = String(body?.message || body?.error || '').trim();
            if (body?.retry_after) detail = `Rate limited. Retry after ${Math.ceil(Number(body.retry_after) / 1000)} seconds.`;
        } catch (err) {}
        return detail || `Discord returned HTTP ${response?.status || 'error'}.`;
    }

    async function testDiscordWebhook() {
        if (discordFinanceBusy) return;
        discordFinanceBusy = true;
        setDiscordStatus('Checking the Discord webhook…', 'busy');
        try {
            const webhookUrl = readDiscordWebhookInput({ save: true });
            const response = await discordHttpRequest({
                method: 'GET',
                url: discordWebhookEndpoint(webhookUrl, { stripQuery: true })
            });
            if (response.status < 200 || response.status >= 300) throw new Error(parseDiscordError(response));
            let webhook = {};
            try { webhook = JSON.parse(response.responseText || '{}'); } catch (err) {}
            const label = String(webhook?.name || state.discordReport.webhookName || 'Discord webhook');
            setDiscordStatus(`Connected successfully: ${label}.`, 'good');
            showToast('Discord webhook connected');
        } catch (err) {
            setDiscordStatus(err?.message || 'Discord webhook test failed.', 'bad');
            showToast('Discord connection failed');
        } finally {
            discordFinanceBusy = false;
        }
    }

    function parseCreditInteger(value) {
        const text = String(value ?? '').replace(/\u2212/gu, '-').trim();
        if (!text) return 0;
        const negative = /(^|[^\d])-/u.test(text) || /^\s*\(/u.test(text);
        const digits = text.replace(/[^\d]/gu, '');
        if (!digits) return 0;
        const amount = Number(digits);
        return Number.isFinite(amount) ? (negative ? -amount : amount) : 0;
    }

    function parseCreditTimestamp(rawValue, fallbackText = '') {
        const raw = String(rawValue || '').trim();
        if (raw) {
            if (/^\d{10,13}$/u.test(raw)) {
                const numeric = Number(raw);
                const timestamp = raw.length === 10 ? numeric * 1000 : numeric;
                if (Number.isFinite(timestamp)) return timestamp;
            }
            const direct = Date.parse(raw);
            if (Number.isFinite(direct)) return direct;
        }
        const text = String(fallbackText || '').replace(/\s+/gu, ' ').trim();
        const match = text.match(/(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?:\D+(\d{1,2}):(\d{2})(?::(\d{2}))?)?/u);
        if (!match) return NaN;
        const [, day, month, year, hour = '0', minute = '0', second = '0'] = match;
        const parsed = new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second), 0).getTime();
        return Number.isFinite(parsed) ? parsed : NaN;
    }

    function parseCreditsListDocument(doc, pageNumber = 1) {
        const entries = [];
        let invalidTimestampCount = 0;
        const rows = Array.from(doc?.querySelectorAll?.('table tbody tr') || []);
        for (let rowIndex = 0; rowIndex < rows.length; rowIndex++) {
            const row = rows[rowIndex];
            const cells = Array.from(row.children || []);
            if (cells.length < 3) continue;
            const amount = parseCreditInteger(cells[0]?.textContent);
            const description = String(cells[1]?.textContent || '').replace(/\s+/gu, ' ').trim();
            const dateLabel = String(cells[2]?.textContent || '').replace(/\s+/gu, ' ').trim();
            const rawTimestamp = String(cells[2]?.getAttribute?.('data-logged-at') || '').trim();
            if (!description || !amount) continue;
            const timestamp = parseCreditTimestamp(rawTimestamp, dateLabel);
            if (!Number.isFinite(timestamp)) invalidTimestampCount++;
            entries.push({ amount, description, dateLabel, rawTimestamp, timestamp, page: pageNumber, row: rowIndex });
        }
        let lastPage = 1;
        const paginationItems = Array.from(doc?.querySelectorAll?.('.pagination li') || []);
        for (const item of paginationItems) {
            const page = Number(String(item.textContent || '').replace(/[^\d]/gu, ''));
            if (Number.isFinite(page) && page > lastPage) lastPage = page;
        }
        return { entries, invalidTimestampCount, lastPage };
    }

    function financialLedgerAnchor(entries, count = 3) {
        return entries.slice(0, Math.max(1, count)).map(entry =>
            `${entry.timestamp}|${entry.amount}|${entry.description}|${entry.rawTimestamp || entry.dateLabel}`
        ).join('||');
    }

    async function fetchSameOriginDocument(pathOrUrl) {
        const url = new URL(pathOrUrl, pageWindow.location.origin);
        if (url.origin !== pageWindow.location.origin) throw new Error('Blocked an unexpected external financial-data URL.');
        const response = await runtimeFetch(url.href, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-store',
            headers: { Accept: 'text/html,application/xhtml+xml' }
        });
        if (!response.ok) throw new Error(`MissionChief returned HTTP ${response.status} for ${url.pathname}.`);
        const html = await response.text();
        return { doc: new DOMParser().parseFromString(html, 'text/html'), url: url.href };
    }

    async function fetchCreditAccount() {
        try {
            const response = await runtimeFetch(new URL('/api/credits', pageWindow.location.origin).href, {
                method: 'GET',
                credentials: 'same-origin',
                cache: 'no-store',
                headers: { Accept: 'application/json' }
            });
            if (!response.ok) return null;
            const data = await response.json();
            const balance = Number(data?.credits_user_current);
            return {
                currentBalance: Number.isFinite(balance) ? Math.round(balance) : null,
                userName: String(data?.user_name || '').trim(),
                userId: Number(data?.user_id) || null
            };
        } catch (err) {
            return null;
        }
    }

    function localIsoDate(date = new Date()) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function localDayStart(value = Date.now()) {
        const date = new Date(value);
        date.setHours(0, 0, 0, 0);
        return date.getTime();
    }

    function addLocalDays(timestamp, days) {
        const date = new Date(timestamp);
        date.setDate(date.getDate() + Number(days || 0));
        return date.getTime();
    }

    function parseLocalDateInput(value) {
        const match = String(value || '').match(/^(\d{4})-(\d{2})-(\d{2})$/u);
        if (!match) return NaN;
        const [, year, month, day] = match;
        return new Date(Number(year), Number(month) - 1, Number(day), 0, 0, 0, 0).getTime();
    }

    function formatReportDate(date = new Date()) {
        try { return date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
        catch (err) { return localIsoDate(date); }
    }

    function formatReportDateTime(timestamp) {
        try { return new Date(timestamp).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }); }
        catch (err) { return new Date(timestamp).toISOString(); }
    }

    function formatPeriodRange(startMs, endMs) {
        const inclusiveEnd = Math.max(startMs, endMs - 1);
        const sameDay = localIsoDate(new Date(startMs)) === localIsoDate(new Date(inclusiveEnd));
        if (sameDay) return `${formatReportDate(new Date(startMs))} · ${new Date(startMs).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}–${new Date(inclusiveEnd).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        return `${formatReportDateTime(startMs)} → ${formatReportDateTime(inclusiveEnd)}`;
    }

    function formatSignedCredits(value) {
        const amount = Math.round(Number(value) || 0);
        const sign = amount > 0 ? '+' : amount < 0 ? '-' : '';
        return `${sign}${Math.abs(amount).toLocaleString('en-GB')} Credits`;
    }

    function formatPlainCredits(value) {
        return `${Math.max(0, Math.round(Number(value) || 0)).toLocaleString('en-GB')} Credits`;
    }

    function formatSignedCompactCredits(value) {
        const amount = Math.abs(Math.round(Number(value) || 0));
        const sign = Number(value) < 0 ? '-' : Number(value) > 0 ? '+' : '';
        if (amount >= 1_000_000_000) return `${sign}${(amount / 1_000_000_000).toFixed(amount >= 10_000_000_000 ? 1 : 2).replace(/\.0+$/u, '')}B`;
        if (amount >= 1_000_000) return `${sign}${(amount / 1_000_000).toFixed(amount >= 10_000_000 ? 1 : 2).replace(/\.0+$/u, '')}M`;
        if (amount >= 1_000) return `${sign}${(amount / 1_000).toFixed(amount >= 100_000 ? 0 : amount >= 10_000 ? 1 : 2).replace(/\.0+$/u, '')}K`;
        return `${sign}${amount.toLocaleString('en-GB')}`;
    }

    function reportTone(net) {
        return net > 0 ? 'positive' : net < 0 ? 'negative' : 'neutral';
    }

    function resolveFinancialPeriod() {
        const now = Date.now();
        const todayStart = localDayStart(now);
        const periodId = FINANCE_PERIOD_IDS.has(state.discordReport.period) ? state.discordReport.period : 'today';
        let startMs = todayStart;
        let endMs = now;
        let label = 'Today';
        let note = '';

        if (periodId === 'yesterday') {
            startMs = addLocalDays(todayStart, -1);
            endMs = todayStart;
            label = 'Yesterday';
        } else if (periodId === 'last24') {
            startMs = now - 24 * 60 * 60 * 1000;
            endMs = now;
            label = 'Last 24 Hours';
        } else if (periodId === 'last7') {
            startMs = now - 7 * 24 * 60 * 60 * 1000;
            endMs = now;
            label = 'Last 7 Days';
        } else if (periodId === 'last30') {
            startMs = now - 30 * 24 * 60 * 60 * 1000;
            endMs = now;
            label = 'Last 30 Days';
        } else if (periodId === 'session') {
            startMs = FINANCE_SESSION_STARTED_AT;
            endMs = now;
            label = 'Current Toolkit Session';
        } else if (periodId === 'sinceLast') {
            const lastReportAt = getLastDiscordReportAt();
            startMs = lastReportAt || FINANCE_SESSION_STARTED_AT;
            endMs = now;
            label = lastReportAt ? 'Since Last Discord Report' : 'Since Toolkit Session Start';
            if (!lastReportAt) note = 'No previous successful Discord report timestamp was stored, so the current toolkit session was used.';
        } else if (periodId === 'custom') {
            const start = parseLocalDateInput(state.discordReport.customStart);
            const end = parseLocalDateInput(state.discordReport.customEnd);
            if (!Number.isFinite(start) || !Number.isFinite(end)) throw new Error('Select valid custom start and end dates.');
            if (end < start) throw new Error('The custom end date cannot be earlier than the start date.');
            startMs = start;
            endMs = Math.min(now, addLocalDays(end, 1));
            if (endMs <= startMs) throw new Error('The selected custom date range contains no elapsed time.');
            if (endMs - startMs > 90 * 24 * 60 * 60 * 1000) throw new Error('Custom financial reports are limited to 90 days per run.');
            label = 'Custom Financial Period';
        }

        const durationMs = Math.max(1, endMs - startMs);
        let comparisonEndMs = startMs;
        let comparisonStartMs = startMs - durationMs;
        if (periodId === 'today') {
            comparisonStartMs = addLocalDays(todayStart, -1);
            comparisonEndMs = Math.min(todayStart, comparisonStartMs + durationMs);
        } else if (periodId === 'yesterday') {
            comparisonEndMs = startMs;
            comparisonStartMs = addLocalDays(startMs, -1);
        }
        return {
            id: periodId,
            startMs,
            endMs,
            durationMs,
            comparisonStartMs,
            comparisonEndMs,
            label,
            rangeLabel: formatPeriodRange(startMs, endMs),
            comparisonRangeLabel: formatPeriodRange(comparisonStartMs, comparisonEndMs),
            note
        };
    }

    async function fetchFinancialLedger(requiredStartMs, attempt = 0) {
        const entries = [];
        let invalidTimestampCount = 0;
        let lastPage = 1;
        let page = 1;
        let fetchedPages = 0;
        let oldestTimestamp = Infinity;
        let reachedStart = false;
        let firstPageAnchor = '';

        while (page <= Math.min(lastPage || 1, FINANCE_MAX_LEDGER_PAGES)) {
            const path = page === 1 ? '/credits' : `/credits?page=${page}`;
            const result = await fetchSameOriginDocument(path);
            const parsed = parseCreditsListDocument(result.doc, page);
            fetchedPages++;
            if (page === 1) {
                lastPage = Math.max(1, parsed.lastPage || 1);
                firstPageAnchor = financialLedgerAnchor(parsed.entries);
            }
            invalidTimestampCount += parsed.invalidTimestampCount;
            for (const entry of parsed.entries) {
                if (!Number.isFinite(entry.timestamp)) continue;
                entries.push(entry);
                if (entry.timestamp < oldestTimestamp) oldestTimestamp = entry.timestamp;
            }
            reachedStart = Number.isFinite(oldestTimestamp) && oldestTimestamp <= requiredStartMs;
            if (reachedStart || page >= lastPage) break;
            page++;
            if (page % FINANCE_FETCH_YIELD_EVERY === 0) {
                setDiscordStatus(`Reading MissionChief ledger page ${page.toLocaleString('en-GB')} of ${lastPage.toLocaleString('en-GB')}…`, 'busy');
                if (!await runtimeDelay(35)) throw new Error('Toolkit runtime stopped while reading the financial ledger.');
            }
        }

        let ledgerStable = true;
        if (fetchedPages > 1 && firstPageAnchor) {
            const verification = await fetchSameOriginDocument('/credits');
            const verificationPage = parseCreditsListDocument(verification.doc, 1);
            ledgerStable = financialLedgerAnchor(verificationPage.entries) === firstPageAnchor;
            if (!ledgerStable && attempt < 1) {
                setDiscordStatus('New credit activity appeared during the scan. Restarting once for an accurate report…', 'busy');
                if (!await runtimeDelay(80)) throw new Error('Toolkit runtime stopped while stabilising the financial ledger.');
                return fetchFinancialLedger(requiredStartMs, attempt + 1);
            }
        }

        if (!entries.length) throw new Error('MissionChief’s timestamped credit ledger could not be read.');
        entries.sort((a, b) => a.timestamp - b.timestamp || a.page - b.page || a.row - b.row);
        const account = await fetchCreditAccount();
        const coverageReached = reachedStart || page >= lastPage;
        const complete = coverageReached && invalidTimestampCount === 0 && ledgerStable;
        return {
            entries,
            pageCount: fetchedPages,
            lastPage,
            invalidTimestampCount,
            oldestTimestamp: Number.isFinite(oldestTimestamp) ? oldestTimestamp : null,
            coverageReached,
            ledgerStable,
            scanRetries: attempt,
            complete,
            account
        };
    }

    function classifyFinancialTransaction(transaction) {
        const description = String(transaction.description || '');
        const amount = Number(transaction.amount) || 0;
        const income = amount > 0;

        if (income) {
            if (/refund|reimburse|cancel(?:ed|led)?/iu.test(description)) return { key: 'refunds', label: 'Refunds & Reimbursements', kind: 'income', missionType: '' };
            if (/^\[alliance\]/iu.test(description)) return { key: 'allianceMissions', label: 'Alliance Missions', kind: 'income', missionType: 'alliance' };
            if (/patient (transport|treatment)|hospital\s*-\s*alliance/iu.test(description)) return { key: 'patientIncome', label: 'Patient Transport & Treatment', kind: 'income', missionType: 'transport' };
            if (/prisoner.*transport|police\s*-\s*alliance/iu.test(description)) return { key: 'prisonerIncome', label: 'Prisoner Transport', kind: 'income', missionType: 'transport' };
            if (/daily login reward/iu.test(description)) return { key: 'dailyLogin', label: 'Daily Login Rewards', kind: 'income', missionType: '' };
            if (/completed task/iu.test(description)) return { key: 'taskRewards', label: 'Task Rewards', kind: 'income', missionType: 'task' };
            if (/event|bonus|reward/iu.test(description)) return { key: 'eventBonus', label: 'Event & Bonus Income', kind: 'income', missionType: 'personal' };
            return { key: 'personalMissions', label: 'Personal Missions & Other Income', kind: 'income', missionType: 'personal' };
        }

        if (/vehicle bought|vehicle purchase|bought vehicle/iu.test(description)) return { key: 'vehicles', label: 'Vehicles', kind: 'spending', missionType: '' };
        if (/vehicle.*upgrad|upgrade.*vehicle|vehicle equipment|equipment for .*vehicle/iu.test(description)) return { key: 'vehicleUpgrades', label: 'Vehicle Upgrades & Equipment', kind: 'spending', missionType: '' };
        if (/education|training|school|course|applicant/iu.test(description)) return { key: 'training', label: 'Training & Education', kind: 'spending', missionType: '' };
        if (/recruit|personnel|staff|hire/iu.test(description)) return { key: 'recruitment', label: 'Recruitment & Staffing', kind: 'spending', missionType: '' };
        if (/alliance|association|verband|fund|donation|contribution/iu.test(description)) return { key: 'allianceSpending', label: 'Alliance Contributions', kind: 'spending', missionType: '' };
        if (/building constructed|station constructed|new building/iu.test(description) && !/building complex.*upgrad|upgraded to building complex/iu.test(description)) return { key: 'buildings', label: 'Buildings', kind: 'spending', missionType: '' };
        if (/upgrad|extended guard|extension|speciali[sz]ation built|attached building|building complex/iu.test(description)) return { key: 'extensions', label: 'Extensions & Upgrades', kind: 'spending', missionType: '' };
        return { key: 'otherSpending', label: 'Other Spending', kind: 'spending', missionType: '' };
    }

    function buildFinancialBuckets(transactions, startMs, endMs) {
        const duration = Math.max(1, endMs - startMs);
        const useHourly = duration <= 48 * 60 * 60 * 1000;
        const bucketMs = useHourly ? Math.max(60 * 60 * 1000, Math.ceil(duration / 12 / (60 * 60 * 1000)) * 60 * 60 * 1000) : 24 * 60 * 60 * 1000;
        const count = Math.max(1, Math.min(31, Math.ceil(duration / bucketMs)));
        const buckets = Array.from({ length: count }, (_, index) => ({
            start: startMs + index * bucketMs,
            end: Math.min(endMs, startMs + (index + 1) * bucketMs),
            income: 0,
            spending: 0,
            net: 0,
            label: ''
        }));
        for (const transaction of transactions) {
            const index = Math.min(count - 1, Math.max(0, Math.floor((transaction.timestamp - startMs) / bucketMs)));
            if (!buckets[index] || transaction.timestamp < startMs || transaction.timestamp >= endMs) continue;
            if (transaction.amount > 0) buckets[index].income += transaction.amount;
            else buckets[index].spending += Math.abs(transaction.amount);
            buckets[index].net += transaction.amount;
        }
        for (const bucket of buckets) {
            const date = new Date(bucket.start);
            bucket.label = useHourly
                ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
        }
        return buckets;
    }

    function summariseFinancialTransactions(transactions, period) {
        const incomeCategoryMap = new Map();
        const spendingCategoryMap = new Map();
        const topPayouts = [];
        let income = 0;
        let spending = 0;
        let incomeCount = 0;
        let spendingCount = 0;
        let missionCount = 0;
        let missionIncome = 0;
        let allianceIncome = 0;
        let personalIncome = 0;
        let transportIncome = 0;
        let largestReward = 0;
        let smallestReward = Infinity;
        let hasMissionPayout = false;

        const addCategory = (map, category, amount) => {
            const existing = map.get(category.key) || { key: category.key, label: category.label, total: 0, count: 0 };
            existing.total += Math.abs(amount);
            existing.count += 1;
            map.set(category.key, existing);
        };
        const addTopPayout = entry => {
            topPayouts.push(entry);
            topPayouts.sort((a, b) => b.amount - a.amount);
            if (topPayouts.length > 8) topPayouts.length = 8;
        };

        for (const entry of transactions) {
            const amount = Number(entry.amount) || 0;
            if (!amount) continue;
            const category = classifyFinancialTransaction(entry);
            if (amount > 0) {
                income += amount;
                incomeCount += 1;
                addCategory(incomeCategoryMap, category, amount);
                if (category.missionType) {
                    missionCount += 1;
                    missionIncome += amount;
                    hasMissionPayout = true;
                    largestReward = Math.max(largestReward, amount);
                    smallestReward = Math.min(smallestReward, amount);
                    addTopPayout(entry);
                }
                if (category.missionType === 'alliance') allianceIncome += amount;
                if (category.missionType === 'personal') personalIncome += amount;
                if (category.missionType === 'transport') transportIncome += amount;
            } else {
                spending += Math.abs(amount);
                spendingCount += 1;
                addCategory(spendingCategoryMap, category, amount);
            }
        }

        if (!hasMissionPayout) {
            topPayouts.length = 0;
            largestReward = 0;
            smallestReward = Infinity;
            for (const entry of transactions) {
                if (entry.amount <= 0) continue;
                largestReward = Math.max(largestReward, entry.amount);
                smallestReward = Math.min(smallestReward, entry.amount);
                addTopPayout(entry);
            }
        }

        const net = income - spending;
        const hours = Math.max(1 / 60, period.durationMs / (60 * 60 * 1000));
        return {
            incomeCategories: Array.from(incomeCategoryMap.values()).sort((a, b) => b.total - a.total || b.count - a.count),
            spendingCategories: Array.from(spendingCategoryMap.values()).sort((a, b) => b.total - a.total || b.count - a.count),
            income,
            spending,
            net,
            incomeCount,
            spendingCount,
            activityCount: incomeCount + spendingCount,
            missionCount,
            missionIncome,
            averageIncome: incomeCount ? Math.round(income / incomeCount) : 0,
            averageSpend: spendingCount ? Math.round(spending / spendingCount) : 0,
            averageMissionReward: missionCount ? Math.round(missionIncome / missionCount) : 0,
            largestReward,
            smallestReward: Number.isFinite(smallestReward) ? smallestReward : 0,
            allianceIncome,
            personalIncome,
            transportIncome,
            allianceIncomePercent: income ? Math.round((allianceIncome / income) * 1000) / 10 : 0,
            personalIncomePercent: income ? Math.round((personalIncome / income) * 1000) / 10 : 0,
            incomePerHour: Math.round(income / hours),
            topPayouts,
            buckets: buildFinancialBuckets(transactions, period.startMs, period.endMs)
        };
    }

    function percentageChange(current, previous) {
        const currentValue = Number(current) || 0;
        const previousValue = Number(previous) || 0;
        if (!previousValue) return currentValue ? null : 0;
        return ((currentValue - previousValue) / Math.abs(previousValue)) * 100;
    }

    function formatPercentageChange(value) {
        if (value === null || !Number.isFinite(value)) return 'New activity';
        const rounded = Math.round(value * 10) / 10;
        return `${rounded > 0 ? '+' : ''}${rounded.toLocaleString('en-GB')}%`;
    }

    function buildFinancialComparison(current, previous) {
        return {
            incomeChange: percentageChange(current.income, previous.income),
            spendingChange: percentageChange(current.spending, previous.spending),
            netChange: percentageChange(current.net, previous.net),
            missionChange: current.missionCount - previous.missionCount,
            averageRewardChange: percentageChange(current.averageMissionReward, previous.averageMissionReward),
            currentNet: current.net,
            previousNet: previous.net
        };
    }

    function calculateFinancialGrade(summary, comparison, { complete = true, balanceAvailable = true } = {}) {
        const margin = summary.income ? summary.net / summary.income : summary.spending ? -1 : 0;
        let score = 50 + Math.max(-35, Math.min(35, margin * 40));
        if (comparison && Number.isFinite(comparison.netChange)) score += Math.max(-12, Math.min(12, comparison.netChange / 5));
        if (summary.income > 0 && summary.spending === 0) score += 4;
        if (complete) score += 6; else score -= 18;
        if (balanceAvailable) score += 2;
        score = Math.max(0, Math.min(100, Math.round(score)));
        const grade = score >= 94 ? 'A+' : score >= 88 ? 'A' : score >= 82 ? 'A−' : score >= 76 ? 'B+' : score >= 70 ? 'B' : score >= 64 ? 'B−' : score >= 57 ? 'C+' : score >= 50 ? 'C' : score >= 40 ? 'D' : 'F';
        const label = score >= 88 ? 'Exceptional control' : score >= 76 ? 'Strong performance' : score >= 64 ? 'Stable performance' : score >= 50 ? 'Mixed performance' : 'Financial pressure';
        return { score, grade, label, marginPercent: Math.round(margin * 1000) / 10 };
    }

    function currentFinancialReportSignature() {
        return JSON.stringify({
            period: state.discordReport.period,
            customStart: state.discordReport.customStart,
            customEnd: state.discordReport.customEnd,
            includeChart: state.discordReport.includeChart,
            includeComparison: state.discordReport.includeComparison,
            topCategories: state.discordReport.topCategories,
            sinceLastAnchor: state.discordReport.period === 'sinceLast' ? getLastDiscordReportAt() : 0
        });
    }

    async function buildFinancialReport() {
        const period = resolveFinancialPeriod();
        const requiredStartMs = state.discordReport.includeComparison ? period.comparisonStartMs : period.startMs;
        setDiscordStatus('Reading MissionChief transaction history…', 'busy');
        const ledger = await fetchFinancialLedger(requiredStartMs);
        const currentTransactions = [];
        const previousTransactions = [];
        let afterPeriodNet = 0;
        const now = Date.now();
        for (const entry of ledger.entries) {
            if (entry.timestamp >= period.startMs && entry.timestamp < period.endMs) currentTransactions.push(entry);
            else if (state.discordReport.includeComparison && entry.timestamp >= period.comparisonStartMs && entry.timestamp < period.comparisonEndMs) previousTransactions.push(entry);
            if (entry.timestamp >= period.endMs && entry.timestamp <= now) afterPeriodNet += entry.amount;
        }

        const current = summariseFinancialTransactions(currentTransactions, period);
        const previousPeriod = { ...period, startMs: period.comparisonStartMs, endMs: period.comparisonEndMs, durationMs: period.durationMs };
        const previous = state.discordReport.includeComparison ? summariseFinancialTransactions(previousTransactions, previousPeriod) : null;
        const comparison = previous ? buildFinancialComparison(current, previous) : null;
        const account = ledger.account;
        const currentBalance = Number.isFinite(account?.currentBalance) ? account.currentBalance : null;
        const closingBalance = currentBalance === null ? null : currentBalance - afterPeriodNet;
        const openingBalance = closingBalance === null ? null : closingBalance - current.net;
        const balanceAvailable = openingBalance !== null && closingBalance !== null;
        const reconciliationLabel = !balanceAvailable
            ? 'Balance unavailable'
            : ledger.complete
                ? 'Calculated from current balance and ledger'
                : 'Estimated from partial ledger coverage';
        const grade = calculateFinancialGrade(current, comparison, { complete: ledger.complete, balanceAvailable });
        const report = {
            generatedAt: Date.now(),
            signature: currentFinancialReportSignature(),
            period,
            reportDate: localIsoDate(),
            reportDateLabel: `${period.label} · ${period.rangeLabel}`,
            userName: account?.userName || '',
            userId: account?.userId || null,
            currentBalance,
            openingBalance,
            closingBalance,
            reconciliationDifference: null,
            reconciled: false,
            balanceCalculated: balanceAvailable,
            reconciliationLabel,
            ledgerComplete: ledger.complete,
            ledgerCoverageReached: ledger.coverageReached,
            ledgerPages: ledger.pageCount,
            ledgerLastPage: ledger.lastPage,
            ledgerStable: ledger.ledgerStable,
            ledgerScanRetries: ledger.scanRetries,
            invalidTimestampCount: ledger.invalidTimestampCount,
            comparison,
            previous,
            grade,
            chartBlob: null,
            ...current
        };
        report.chartBlob = state.discordReport.includeChart ? await buildFinancialChartBlob(report) : null;
        return report;
    }

    function escapeDiscordMarkdown(value) {
        return String(value || '')
            .replace(/\\/gu, '\\\\')
            .replace(/([`*_~>|])/gu, '\\$1')
            .replace(/@/gu, '@\u200b');
    }

    function truncateDiscord(value, maximum = DISCORD_MAX_FIELD_LENGTH) {
        const text = String(value || '');
        return text.length <= maximum ? text : `${text.slice(0, Math.max(0, maximum - 1))}…`;
    }

    function buildDiscordCategoryBreakdown(entries, prefix, limit) {
        const rows = entries.slice(0, limit);
        if (!rows.length) return 'No entries recorded.';
        return truncateDiscord(rows.map(entry => `• **${escapeDiscordMarkdown(entry.label)}** — ${prefix}${entry.total.toLocaleString('en-GB')} Credits · ${entry.count.toLocaleString('en-GB')} entr${entry.count === 1 ? 'y' : 'ies'}`).join('\n'));
    }

    function buildDiscordTopPayouts(report, limit = 5) {
        if (!report.topPayouts.length) return 'No positive payouts recorded.';
        return truncateDiscord(report.topPayouts.slice(0, limit).map((entry, index) => `${index + 1}. **${escapeDiscordMarkdown(entry.description)}** — +${entry.amount.toLocaleString('en-GB')} Credits`).join('\n'));
    }

    function buildDiscordComparisonField(report) {
        if (!report.comparison || !report.previous) return 'Comparison disabled.';
        return [
            `Income: **${formatPercentageChange(report.comparison.incomeChange)}**`,
            `Spending: **${formatPercentageChange(report.comparison.spendingChange)}**`,
            `Net result: **${formatPercentageChange(report.comparison.netChange)}**`,
            `Mission count: **${report.comparison.missionChange > 0 ? '+' : ''}${report.comparison.missionChange.toLocaleString('en-GB')}**`,
            `Average mission reward: **${formatPercentageChange(report.comparison.averageRewardChange)}**`
        ].join('\n');
    }

    function buildDiscordFinancialPayload(report, { withAttachment = false } = {}) {
        const netTone = reportTone(report.net);
        const colour = netTone === 'positive' ? 0x2ecc71 : netTone === 'negative' ? 0xe74c3c : 0xf1c40f;
        const topLimit = state.discordReport.topCategories;
        const statusLabel = report.net > 0 ? 'POSITIVE OPERATING RESULT' : report.net < 0 ? 'NEGATIVE OPERATING RESULT' : 'BREAK EVEN';
        const description = [
            `**${escapeDiscordMarkdown(report.period.label)}**`,
            escapeDiscordMarkdown(report.period.rangeLabel),
            `${statusLabel} · **${formatSignedCredits(report.net)}**`,
            report.userName ? `Account: **${escapeDiscordMarkdown(report.userName)}**` : '',
            report.period.note ? `_${escapeDiscordMarkdown(report.period.note)}_` : ''
        ].filter(Boolean).join('\n');

        const balanceLines = report.openingBalance === null || report.closingBalance === null
            ? ['Balance data was unavailable.']
            : [
                `Opening: **${report.openingBalance.toLocaleString('en-GB')} Credits**`,
                `Closing: **${report.closingBalance.toLocaleString('en-GB')} Credits**`,
                `Basis: **${report.reconciliationLabel}**`
            ];

        const operations = [
            `Missions/transport rewards: **${report.missionCount.toLocaleString('en-GB')}**`,
            `Largest payout: **${formatPlainCredits(report.largestReward)}**`,
            `Average mission reward: **${formatPlainCredits(report.averageMissionReward)}**`,
            `Income per hour: **${formatPlainCredits(report.incomePerHour)}**`,
            `Alliance share: **${report.allianceIncomePercent.toLocaleString('en-GB')}%**`,
            `Personal share: **${report.personalIncomePercent.toLocaleString('en-GB')}%**`
        ].join('\n');

        const gradeLines = [
            `Unofficial grade: **${report.grade.grade}** · ${report.grade.score}/100`,
            `Assessment: **${report.grade.label}**`,
            `Net efficiency: **${report.grade.marginPercent.toLocaleString('en-GB')}%**`
        ].join('\n');

        const embed = {
            title: '📊 MissionChief Financial Intelligence Report',
            description: truncateDiscord(description, 4096),
            color: colour,
            timestamp: new Date(report.generatedAt).toISOString(),
            fields: [
                { name: '💰 Income', value: `**${formatPlainCredits(report.income)}**`, inline: true },
                { name: '💸 Spending', value: `**${formatPlainCredits(report.spending)}**`, inline: true },
                { name: report.net >= 0 ? '📈 Net Result' : '📉 Net Result', value: `**${formatSignedCredits(report.net)}**`, inline: true },
                { name: '🏦 Balance Position', value: truncateDiscord(balanceLines.join('\n')), inline: true },
                { name: '🚨 Operational Performance', value: truncateDiscord(operations), inline: true },
                { name: '🏅 Financial Grade', value: truncateDiscord(gradeLines), inline: true },
                { name: '🟢 Income Breakdown', value: buildDiscordCategoryBreakdown(report.incomeCategories, '+', topLimit), inline: false },
                { name: '🔴 Spending Breakdown', value: buildDiscordCategoryBreakdown(report.spendingCategories, '-', topLimit), inline: false },
                { name: '🏆 Highest Payouts', value: buildDiscordTopPayouts(report, Math.min(5, topLimit)), inline: false },
                { name: '📊 Previous Period Comparison', value: truncateDiscord(buildDiscordComparisonField(report)), inline: false },
                { name: '🧾 Data Quality', value: `${report.activityCount.toLocaleString('en-GB')} transactions · ${report.ledgerPages.toLocaleString('en-GB')} ledger page${report.ledgerPages === 1 ? '' : 's'} read · ${report.ledgerComplete ? 'Full requested-period coverage' : 'Partial requested-period coverage'}${report.invalidTimestampCount ? ` · ${report.invalidTimestampCount.toLocaleString('en-GB')} rows without usable timestamps` : ''}${report.ledgerScanRetries ? ` · ledger scan restarted ${report.ledgerScanRetries.toLocaleString('en-GB')} time${report.ledgerScanRetries === 1 ? '' : 's'} after new activity` : ''}${!report.ledgerStable ? ' · ledger changed again during verification' : ''}`, inline: false }
            ],
            footer: { text: `${SCRIPT.name} • v${SCRIPT.version} • Financial Intelligence` }
        };
        if (withAttachment) embed.image = { url: `attachment://${FINANCE_CHART_FILENAME}` };
        const payload = {
            username: state.discordReport.webhookName || 'MissionChief Finance',
            allowed_mentions: { parse: [] },
            embeds: [embed]
        };
        if (withAttachment) payload.attachments = [{ id: 0, filename: FINANCE_CHART_FILENAME, description: `${report.period.label} MissionChief financial chart` }];
        return payload;
    }

    function roundRectPath(context, x, y, width, height, radius) {
        const r = Math.max(0, Math.min(radius, width / 2, height / 2));
        context.beginPath();
        context.moveTo(x + r, y);
        context.arcTo(x + width, y, x + width, y + height, r);
        context.arcTo(x + width, y + height, x, y + height, r);
        context.arcTo(x, y + height, x, y, r);
        context.arcTo(x, y, x + width, y, r);
        context.closePath();
    }

    function drawFinancialMetricCard(context, x, y, width, height, label, value, accent) {
        roundRectPath(context, x, y, width, height, 18);
        context.fillStyle = 'rgba(255,255,255,0.055)';
        context.fill();
        context.fillStyle = accent;
        context.fillRect(x, y, 5, height);
        context.fillStyle = 'rgba(255,255,255,0.58)';
        context.font = '700 18px Arial, sans-serif';
        context.fillText(label.toUpperCase(), x + 24, y + 31);
        context.fillStyle = '#ffffff';
        context.font = '900 34px Arial, sans-serif';
        context.fillText(value, x + 24, y + 75);
    }

    async function buildFinancialChartBlob(report) {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 1200;
            canvas.height = 675;
            const context = canvas.getContext('2d');
            if (!context) return null;
            const gradient = context.createLinearGradient(0, 0, 1200, 675);
            gradient.addColorStop(0, '#0b1018');
            gradient.addColorStop(0.55, '#111a27');
            gradient.addColorStop(1, '#080b11');
            context.fillStyle = gradient;
            context.fillRect(0, 0, 1200, 675);

            context.fillStyle = 'rgba(88,166,255,0.12)';
            context.beginPath();
            context.arc(1060, 70, 230, 0, Math.PI * 2);
            context.fill();
            context.fillStyle = 'rgba(124,77,255,0.08)';
            context.beginPath();
            context.arc(140, 650, 280, 0, Math.PI * 2);
            context.fill();

            context.fillStyle = '#ffffff';
            context.font = '900 34px Arial, sans-serif';
            context.fillText('MISSIONCHIEF FINANCIAL INTELLIGENCE', 54, 58);
            context.fillStyle = 'rgba(255,255,255,0.62)';
            context.font = '600 18px Arial, sans-serif';
            context.fillText(report.period.label, 54, 89);
            context.fillText(report.period.rangeLabel, 54, 116);

            roundRectPath(context, 1002, 38, 142, 70, 20);
            context.fillStyle = report.net >= 0 ? 'rgba(46,204,113,0.18)' : 'rgba(231,76,60,0.18)';
            context.fill();
            context.fillStyle = report.net >= 0 ? '#67e69b' : '#ff8378';
            context.font = '900 30px Arial, sans-serif';
            context.textAlign = 'center';
            context.fillText(report.grade.grade, 1073, 73);
            context.font = '700 14px Arial, sans-serif';
            context.fillText(`${report.grade.score}/100`, 1073, 96);
            context.textAlign = 'left';

            drawFinancialMetricCard(context, 54, 148, 337, 98, 'Income', formatSignedCompactCredits(report.income), '#2ecc71');
            drawFinancialMetricCard(context, 412, 148, 337, 98, 'Spending', formatSignedCompactCredits(-report.spending), '#e74c3c');
            drawFinancialMetricCard(context, 770, 148, 374, 98, 'Net result', formatSignedCompactCredits(report.net), report.net >= 0 ? '#58a6ff' : '#ff6b61');

            const chartX = 54;
            const chartY = 288;
            const chartW = 730;
            const chartH = 250;
            roundRectPath(context, chartX, chartY, chartW, chartH, 18);
            context.fillStyle = 'rgba(255,255,255,0.04)';
            context.fill();
            context.fillStyle = '#ffffff';
            context.font = '800 19px Arial, sans-serif';
            context.fillText('NET PERFORMANCE TREND', chartX + 22, chartY + 32);
            const buckets = report.buckets.slice(-12);
            const maxMagnitude = Math.max(1, ...buckets.map(bucket => Math.abs(bucket.net)));
            const plotTop = chartY + 58;
            const plotBottom = chartY + chartH - 38;
            const zeroY = plotTop + (plotBottom - plotTop) / 2;
            context.strokeStyle = 'rgba(255,255,255,0.14)';
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(chartX + 22, zeroY);
            context.lineTo(chartX + chartW - 22, zeroY);
            context.stroke();
            const slotW = (chartW - 52) / Math.max(1, buckets.length);
            buckets.forEach((bucket, index) => {
                const height = Math.max(2, Math.abs(bucket.net) / maxMagnitude * ((plotBottom - plotTop) / 2 - 8));
                const x = chartX + 29 + index * slotW;
                const y = bucket.net >= 0 ? zeroY - height : zeroY;
                roundRectPath(context, x, y, Math.max(8, slotW - 10), height, 4);
                context.fillStyle = bucket.net >= 0 ? '#2ecc71' : '#e74c3c';
                context.fill();
                context.fillStyle = 'rgba(255,255,255,0.52)';
                context.font = '600 11px Arial, sans-serif';
                context.textAlign = 'center';
                context.fillText(bucket.label, x + Math.max(8, slotW - 10) / 2, chartY + chartH - 15);
            });
            context.textAlign = 'left';

            const detailX = 810;
            const detailY = 288;
            const detailW = 334;
            const detailH = 250;
            roundRectPath(context, detailX, detailY, detailW, detailH, 18);
            context.fillStyle = 'rgba(255,255,255,0.04)';
            context.fill();
            context.fillStyle = '#ffffff';
            context.font = '800 19px Arial, sans-serif';
            context.fillText('OPERATING SNAPSHOT', detailX + 22, detailY + 32);
            const lines = [
                ['Missions / rewards', report.missionCount.toLocaleString('en-GB')],
                ['Largest payout', formatSignedCompactCredits(report.largestReward)],
                ['Average mission', formatSignedCompactCredits(report.averageMissionReward)],
                ['Income per hour', formatSignedCompactCredits(report.incomePerHour)],
                ['Alliance income', `${report.allianceIncomePercent.toLocaleString('en-GB')}%`],
                ['Balance basis', report.reconciliationLabel]
            ];
            lines.forEach((line, index) => {
                const y = detailY + 65 + index * 29;
                context.fillStyle = 'rgba(255,255,255,0.58)';
                context.font = '600 15px Arial, sans-serif';
                context.fillText(line[0], detailX + 22, y);
                context.fillStyle = '#ffffff';
                context.font = '800 15px Arial, sans-serif';
                context.textAlign = 'right';
                context.fillText(String(line[1]), detailX + detailW - 22, y);
                context.textAlign = 'left';
            });

            context.fillStyle = 'rgba(255,255,255,0.42)';
            context.font = '600 14px Arial, sans-serif';
            context.fillText(`${report.activityCount.toLocaleString('en-GB')} transactions · ${report.ledgerPages.toLocaleString('en-GB')} ledger pages · Generated ${new Date(report.generatedAt).toLocaleString('en-GB')}`, 54, 620);
            context.fillStyle = 'rgba(255,255,255,0.27)';
            context.font = '600 12px Arial, sans-serif';
            context.fillText(`${SCRIPT.name} v${SCRIPT.version} · Performance grade is an unofficial toolkit assessment`, 54, 648);

            return await new Promise(resolve => canvas.toBlob(resolve, 'image/png', 0.92));
        } catch (err) {
            return null;
        }
    }

    async function sendDiscordFinancialPayload(webhookUrl, report) {
        const hasChart = Boolean(report.chartBlob && state.discordReport.includeChart);
        const payload = buildDiscordFinancialPayload(report, { withAttachment: hasChart });
        let response;
        if (hasChart) {
            const formData = new FormData();
            formData.append('payload_json', JSON.stringify(payload));
            formData.append('files[0]', report.chartBlob, FINANCE_CHART_FILENAME);
            response = await discordHttpRequest({
                method: 'POST',
                url: discordWebhookEndpoint(webhookUrl, { wait: true }),
                data: formData
            });
            if (response.status === 400 || response.status === 415) {
                const fallbackPayload = buildDiscordFinancialPayload(report, { withAttachment: false });
                response = await discordHttpRequest({
                    method: 'POST',
                    url: discordWebhookEndpoint(webhookUrl, { wait: true }),
                    headers: { 'Content-Type': 'application/json' },
                    data: JSON.stringify(fallbackPayload)
                });
            }
        } else {
            response = await discordHttpRequest({
                method: 'POST',
                url: discordWebhookEndpoint(webhookUrl, { wait: true }),
                headers: { 'Content-Type': 'application/json' },
                data: JSON.stringify(payload)
            });
        }
        if (response.status < 200 || response.status >= 300) throw new Error(parseDiscordError(response));
        return response;
    }

    function clearDiscordPreviewChartUrl() {
        if (discordFinanceChartUrl) {
            try { URL.revokeObjectURL(discordFinanceChartUrl); } catch (err) {}
        }
        discordFinanceChartUrl = '';
        discordFinanceChartBlobRef = null;
        discordPreviewRenderSignature = '';
    }

    function invalidateDiscordFinancialPreview() {
        clearDiscordPreviewChartUrl();
        discordFinancePreview = null;
    }

    async function postDiscordFinancialReport() {
        if (discordFinanceBusy) return;
        let webhookUrl;
        try { webhookUrl = readDiscordWebhookInput({ save: true }); }
        catch (err) {
            setDiscordStatus(err?.message || 'Enter a valid Discord webhook URL.', 'bad');
            showToast('Discord webhook required');
            return;
        }
        discordFinanceBusy = true;
        setDiscordStatus('Building and posting the financial report…', 'busy');
        try {
            const report = await buildFinancialReport();
            await sendDiscordFinancialPayload(webhookUrl, report);
            gmSetValueSafe(SCRIPT.discordLastReportState, report.generatedAt);
            discordFinancePreview = null;
            clearDiscordPreviewChartUrl();
            setDiscordStatus(`Posted successfully at ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}.`, 'good');
            showToast('Discord financial report posted');
        } catch (err) {
            setDiscordStatus(err?.message || 'The Discord report could not be posted.', 'bad');
            showToast('Discord report failed');
        } finally {
            discordFinanceBusy = false;
        }
    }

    function clearDiscordWebhook() {
        if (!getDiscordWebhookUrl()) {
            setDiscordStatus('No Discord webhook is currently saved.', 'neutral');
            return;
        }
        if (!pageWindow.confirm('Remove the saved Discord webhook from Tampermonkey storage?')) return;
        gmDeleteValueSafe(SCRIPT.discordWebhookState);
        const input = document.querySelector(`#${SCRIPT.panelId} [data-setting="discord-webhook"]`);
        if (input) input.value = '';
        setDiscordStatus('Saved Discord webhook removed.', 'good');
        showToast('Discord webhook cleared');
    }


    function setStatus(text) {
        const status = document.querySelector(`#${SCRIPT.panelId} .mcms-status`);
        if (status) status.textContent = text || 'Ready.';
    }

    function showToast(text) {
        let toast = document.getElementById(SCRIPT.toastId);
        if (!toast) {
            toast = document.createElement('div');
            toast.id = SCRIPT.toastId;
            document.body.appendChild(toast);
        }
        toast.textContent = text;
        toast.classList.add('mcms-flash');
        runtimeClearTimeout(toastFlashTimer);
        toastFlashTimer = runtimeSetTimeout(() => {
            toastFlashTimer = null;
            toast.classList.remove('mcms-flash');
        }, 950);
    }

    function applyTheme(themeKey, persist = true) {
        state.theme = normaliseTheme(themeKey);
        if (persist) saveState();
        applyRootAttributes();
        updateUI();
        showToast(THEMES[state.theme].full);
    }

    function setActiveTab(tab) {
        if (!['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings'].includes(tab)) return;
        state.activeTab = tab;
        saveState();
        updateUI();
        if (!dragState) positionPanelOverlay(true);
    }

    function applyPosition(position, persist = true) {
        state.position = POSITIONS[position] ? position : 'bl';
        if (persist) saveState();
        updateUI();
        fitControlToMap();
    }

    function nudgeControl(dx, dy) {
        state.nudge.x = clamp(state.nudge.x + dx, -220, 220, 0);
        state.nudge.y = clamp(state.nudge.y + dy, -220, 220, 0);
        saveState();
        updateUI();
    }

    function resetNudge() {
        state.nudge = { x: 0, y: 0 };
        saveState();
        updateUI();
    }

    function toggleCommandBar() {
        if (commandBarAnimating) return;

        const control = document.getElementById(SCRIPT.controlId);
        const opening = state.commandBarOpen === false;
        const animatedItems = control
            ? Array.from(control.querySelectorAll('.mcms-float-btn, .mcms-screen-pin-btn'))
            : [];
        const reduceMotion = Boolean(pageWindow.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
        const duration = reduceMotion ? 0 : (mobileModeActive ? 145 : 175);
        const stagger = reduceMotion ? 0 : (mobileModeActive ? 5 : 7);
        const maxDelay = Math.min(Math.max(0, animatedItems.length - 1) * stagger, 70);
        const clearAnimationStyles = () => {
            for (const item of animatedItems) {
                item.style.removeProperty('opacity');
                item.style.removeProperty('transform');
                item.style.removeProperty('transition');
                item.style.removeProperty('transition-delay');
                item.style.removeProperty('will-change');
            }
        };

        if (commandBarAnimationTimer !== null) {
            runtimeClearTimeout(commandBarAnimationTimer);
            commandBarAnimationTimer = null;
        }

        if (opening) {
            state.commandBarOpen = true;
            saveState();
            updateUI();
            fitControlToMap();

            if (duration > 0 && animatedItems.length) {
                commandBarAnimating = true;
                const targetStyles = animatedItems.map(item => {
                    const computed = pageWindow.getComputedStyle(item);
                    return {
                        opacity: computed.opacity || '1',
                        transform: computed.transform === 'none' ? 'none' : computed.transform
                    };
                });

                animatedItems.forEach(item => {
                    item.style.setProperty('transition', 'none', 'important');
                    item.style.setProperty('transition-delay', '0ms', 'important');
                    item.style.setProperty('opacity', '0', 'important');
                    item.style.setProperty('transform', 'translateX(-10px) scale(.94)', 'important');
                    item.style.setProperty('will-change', 'opacity, transform', 'important');
                });
                void control.offsetWidth;

                runtimeRequestAnimationFrame(() => {
                    animatedItems.forEach((item, index) => {
                        item.style.setProperty('transition', `opacity ${duration}ms cubic-bezier(.2,.78,.22,1), transform ${duration}ms cubic-bezier(.2,.78,.22,1)`, 'important');
                        item.style.setProperty('transition-delay', `${Math.min(index * stagger, 70)}ms`, 'important');
                        item.style.setProperty('opacity', targetStyles[index].opacity, 'important');
                        item.style.setProperty('transform', targetStyles[index].transform, 'important');
                    });
                });

                commandBarAnimationTimer = runtimeSetTimeout(() => {
                    commandBarAnimationTimer = null;
                    clearAnimationStyles();
                    commandBarAnimating = false;
                }, duration + maxDelay + 35);
            }

            showToast('Command bar expanded');
            return;
        }

        if (duration <= 0 || !animatedItems.length) {
            state.commandBarOpen = false;
            saveState();
            updateUI();
            fitControlToMap();
            showToast('Command bar collapsed');
            return;
        }

        commandBarAnimating = true;
        animatedItems.forEach((item, index) => {
            const computed = pageWindow.getComputedStyle(item);
            item.style.setProperty('transition', 'none', 'important');
            item.style.setProperty('transition-delay', '0ms', 'important');
            item.style.setProperty('opacity', computed.opacity || '1', 'important');
            item.style.setProperty('transform', computed.transform === 'none' ? 'none' : computed.transform, 'important');
            item.style.setProperty('will-change', 'opacity, transform', 'important');
            item.dataset.mcmsCollapseDelay = String(Math.min(index * stagger, 70));
        });
        void control.offsetWidth;

        runtimeRequestAnimationFrame(() => {
            for (const item of animatedItems) {
                item.style.setProperty('transition', `opacity ${duration}ms cubic-bezier(.4,0,.2,1), transform ${duration}ms cubic-bezier(.4,0,.2,1)`, 'important');
                item.style.setProperty('transition-delay', `${item.dataset.mcmsCollapseDelay || 0}ms`, 'important');
                item.style.setProperty('opacity', '0', 'important');
                item.style.setProperty('transform', 'translateX(-10px) scale(.94)', 'important');
                delete item.dataset.mcmsCollapseDelay;
            }
        });

        commandBarAnimationTimer = runtimeSetTimeout(() => {
            commandBarAnimationTimer = null;
            state.commandBarOpen = false;
            saveState();
            updateUI();
            fitControlToMap();
            clearAnimationStyles();
            commandBarAnimating = false;
        }, duration + maxDelay + 25);

        showToast('Command bar collapsed');
    }

    function toggleFeature(feature) {
        if (feature === 'clean') state.cleanMode = !state.cleanMode;
        if (feature === 'markerFocus') state.markerFocus = !state.markerFocus;
        if (feature === 'missionPulse') state.missionPulse = !state.missionPulse;
        if (feature === 'roadPriority') state.roadPriority = !state.roadPriority;
        if (feature === 'coverage') state.coverage.enabled = !state.coverage.enabled;
        if (feature === 'heatmap') state.heatmap.enabled = !state.heatmap.enabled;
        if (feature === 'shortcuts') state.shortcuts = !state.shortcuts;
        if (feature === 'allianceCredits') state.allianceCredits = !state.allianceCredits;
        if (feature === 'missionAge') state.missionAge = !state.missionAge;
        if (feature === 'unitCommitment') state.unitCommitment = !state.unitCommitment;
        if (feature === 'transportWatcher') state.transportWatcher = !state.transportWatcher;
        if (feature === 'missionInspector') state.missionInspector = !state.missionInspector;
        if (feature === 'stuckDetector') state.stuckDetector.enabled = !state.stuckDetector.enabled;
        if (feature === 'missionSpawn') state.missionSpawn.enabled = !state.missionSpawn.enabled;
        if (feature === 'missionSpawn') {
            missionSpawnArmed = false;
            runtimeClearTimeout(missionSpawnPrimeTimer);
            knownMissionIds.clear();
            if (state.missionSpawn.enabled) primeMissionSpawnDetector();
        }
        if (feature === 'resourceGap') state.resourceGap.enabled = !state.resourceGap.enabled;
        if (feature === 'criticalView') { toggleCriticalView(); return; }
        if (feature === 'payoutFlash') state.payoutFlash.enabled = !state.payoutFlash.enabled;
        if (feature === 'payoutSound') {
            state.payoutFlash.soundEnabled = !state.payoutFlash.soundEnabled;
            if (state.payoutFlash.soundEnabled) unlockPayoutAudio();
            else disposePayoutMediaAudio();
        }
        if (feature === 'compactDock') state.compactDock = !state.compactDock;
        if (feature === 'autoNight') {
            state.autoNight.enabled = !state.autoNight.enabled;
            state.autoNight.lastBucket = '';
        }
        if (feature === 'allianceMissions') state.visibility.allianceMissions = !state.visibility.allianceMissions;
        if (feature === 'myMissions') state.visibility.myMissions = !state.visibility.myMissions;
        if (feature === 'vehicles') state.visibility.vehicles = !state.visibility.vehicles;
        if (feature === 'buildings') state.visibility.buildings = !state.visibility.buildings;

        if (state.cleanMode) closePanel();

        if (!criticalViewActive) saveState();
        applyRootAttributes();
        updateUI();
        if (feature === 'vehicles') synchroniseVehicleMarkerClasses();
        if (feature === 'buildings') synchronisePersonalBuildingVisibility();
        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
        if (feature === 'allianceCredits') showToast(state.allianceCredits ? 'Alliance credits on' : 'Alliance credits off');
        if (feature === 'missionAge') showToast(state.missionAge ? 'Personal mission age on' : 'Personal mission age off');
        if (feature === 'unitCommitment') {
            if (state.unitCommitment) {
                showToast('Loading unit assignments…');
                refreshPersonalVehicleData(true).then(ok => {
                    scheduleUnitCommitmentRefresh(0);
                    showToast(ok ? 'Unit Count on' : 'Unit Count on · live vehicle data unavailable');
                });
            } else showToast('Unit Count off');
        }
        if (feature === 'transportWatcher') showToast(state.transportWatcher ? 'Transport Watcher on' : 'Transport Watcher off');
        if (feature === 'missionInspector') showToast(state.missionInspector ? 'Mission Inspector on' : 'Mission Inspector off');
        if (feature === 'stuckDetector') showToast(state.stuckDetector.enabled ? `Stuck detector on · ${state.stuckDetector.thresholdMin} min` : 'Stuck detector off');
        if (feature === 'missionSpawn') showToast(state.missionSpawn.enabled ? 'New mission animation on' : 'New mission animation off');
        if (feature === 'resourceGap') {
            if (state.resourceGap.enabled) refreshPersonalVehicleData(false).then(() => { scheduleResourceGapRefresh(0); refreshVisibleMissionInspector(); });
            showToast(state.resourceGap.enabled ? `Resource Gap on · ${state.resourceGap.radiusMi}mi` : 'Resource Gap off');
        }
        if (feature === 'payoutSound') showToast(state.payoutFlash.soundEnabled ? 'Theme audio on · hosted MP3 cues load only when played' : 'Theme audio off');
        if (feature === 'payoutFlash') showToast(state.payoutFlash.enabled ? 'Emergency payout flash on' : 'Emergency payout flash off');
        if (feature === 'autoNight') runAutoNight(true);
    }

    function runAutoNight(force = false) {
        if (!state.autoNight.enabled) return;
        const bucket = isNightNow(state.autoNight.nightStart, state.autoNight.dayStart) ? 'night' : 'day';
        if (!force && state.autoNight.lastBucket === bucket) return;
        state.autoNight.lastBucket = bucket;
        state.theme = bucket === 'night' ? normaliseTheme(state.autoNight.nightTheme) : normaliseTheme(state.autoNight.dayTheme);
        saveState();
        applyRootAttributes();
        updateUI();
    }

    function isNightNow(start, end) {
        const now = new Date();
        const current = now.getHours() * 60 + now.getMinutes();
        const startMin = parseTime(start, 19 * 60);
        const endMin = parseTime(end, 7 * 60);
        if (startMin === endMin) return false;
        if (startMin < endMin) return current >= startMin && current < endMin;
        return current >= startMin || current < endMin;
    }

    function parseTime(value, fallback) {
        const match = String(value || '').match(/^(\d{1,2}):(\d{2})$/);
        if (!match) return fallback;
        return clamp(match[1], 0, 23, Math.floor(fallback / 60)) * 60 + clamp(match[2], 0, 59, fallback % 60);
    }

    function shouldSuppressControl() {
        if (state.cleanMode) return false;
        if (document.body && document.body.classList.contains('modal-open')) return true;

        return SUPPRESSION_SELECTORS.some(selector => {
            let nodes = [];
            try { nodes = Array.from(document.querySelectorAll(selector)); } catch (err) { return false; }
            return nodes.some(el => {
                if (!el || el.closest(`#${SCRIPT.controlId}`) || el.closest(`#${SCRIPT.panelId}`)) return false;
                if (!isVisible(el)) return false;
                const rect = el.getBoundingClientRect();
                return (rect.width * rect.height) > 1200;
            });
        });
    }

    function refreshSuppression() {
        const control = document.getElementById(SCRIPT.controlId);
        if (!control) return;
        control.classList.toggle('mcms-hidden-by-menu', shouldSuppressControl());
    }

    function fitControlToMap() {
        runtimeClearTimeout(fitTimer);
        fitTimer = runtimeSetTimeout(() => {
            const panel = document.getElementById(SCRIPT.panelId);
            const mapEl = getLargestLeafletMap();
            if (!mapEl) return;
            if (mobileModeActive) applyMobileDockLayout(mapEl);
            else if (tabletModeActive) applyTabletDockLayout(mapEl);
            else clearTabletDockSizing();
            if (!panel) return;
            const rect = mapEl.getBoundingClientRect();
            panel.classList.toggle('mcms-map-small', rect.height < 560 || rect.width < 650);
        }, 60);
    }

    function setPanelCssPosition(left, top) {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return;
        if (isTouchLayoutActive()) { applyTabletPanelPosition(); return; }
        clearTabletPanelSizing(panel);
        panel.style.setProperty('position', 'fixed', 'important');
        panel.style.setProperty('left', `${Math.round(left)}px`, 'important');
        panel.style.setProperty('top', `${Math.round(top)}px`, 'important');
        panel.style.setProperty('right', 'auto', 'important');
        panel.style.setProperty('bottom', 'auto', 'important');
        panel.style.setProperty('transform', 'none', 'important');
    }

    function clampPanelPosition(left, top) {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return { left: 12, top: 12 };

        const margin = 12;
        const viewportWidth = pageWindow.innerWidth || document.documentElement.clientWidth;
        const viewportHeight = pageWindow.innerHeight || document.documentElement.clientHeight;

        panel.style.setProperty('max-height', '', '');

        let panelWidth = panel.offsetWidth || 318;
        let panelHeight = panel.offsetHeight || 500;
        const maxPanelHeight = Math.max(260, viewportHeight - (margin * 2));

        if (panelHeight > maxPanelHeight) {
            panel.style.setProperty('max-height', `${maxPanelHeight}px`, 'important');
            panelHeight = maxPanelHeight;
        }

        panelWidth = Math.min(panelWidth, viewportWidth - (margin * 2));

        return {
            left: Math.round(Math.max(margin, Math.min(left, viewportWidth - panelWidth - margin))),
            top: Math.round(Math.max(margin, Math.min(top, viewportHeight - panelHeight - margin)))
        };
    }

    function getDefaultPanelPosition() {
        const control = document.getElementById(SCRIPT.controlId);
        const panel = document.getElementById(SCRIPT.panelId);
        const margin = 12;
        if (!control || !panel) return { left: margin, top: margin };

        const controlRect = control.getBoundingClientRect();
        const panelWidth = panel.offsetWidth || 318;
        const viewportWidth = pageWindow.innerWidth || document.documentElement.clientWidth;
        const spaceRight = viewportWidth - controlRect.right - margin;
        const spaceLeft = controlRect.left - margin;

        return {
            left: (spaceRight >= panelWidth || spaceRight >= spaceLeft) ? controlRect.right + margin : controlRect.left - panelWidth - margin,
            top: controlRect.top
        };
    }

    function positionPanelOverlay(useSavedPosition = true) {
        if (dragState) return;
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel || !panel.classList.contains('mcms-open')) return;
        if (isTouchLayoutActive()) { applyTabletPanelPosition(); return; }
        clearTabletPanelSizing(panel);

        let left;
        let top;

        if (useSavedPosition && state.panelPosition && Number.isFinite(Number(state.panelPosition.left)) && Number.isFinite(Number(state.panelPosition.top))) {
            left = Number(state.panelPosition.left);
            top = Number(state.panelPosition.top);
        } else {
            const pos = getDefaultPanelPosition();
            left = pos.left;
            top = pos.top;
        }

        const clamped = clampPanelPosition(left, top);
        setPanelCssPosition(clamped.left, clamped.top);
    }

    function resetPanelPosition() {
        if (isTouchLayoutActive()) { showToast(`${mobileModeActive ? 'Mobile' : 'Tablet'} Mode uses a fixed responsive panel`); return; }
        state.panelPosition = null;
        saveState();
        positionPanelOverlay(false);
        showToast('Menu position reset');
    }

    function nudgePanel(dx, dy) {
        if (isTouchLayoutActive()) { showToast(`${mobileModeActive ? 'Mobile' : 'Tablet'} Mode uses a fixed responsive panel`); return; }
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return;
        const rect = panel.getBoundingClientRect();
        const pos = clampPanelPosition(rect.left + dx, rect.top + dy);
        setPanelCssPosition(pos.left, pos.top);
        state.panelPosition = { left: pos.left, top: pos.top };
        saveState();
        showToast(`Menu ${pos.left}, ${pos.top}`);
    }

    function startPanelDrag(event) {
        if (isTouchLayoutActive()) return;
        const isMouse = event.type === 'mousedown';
        const isTouch = event.type === 'touchstart';
        if (isMouse && event.button !== 0) return;
        if (!isMouse && !isTouch) return;

        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel || !panel.classList.contains('mcms-open')) return;

        const point = isTouch ? event.touches[0] : event;
        if (!point) return;

        const rect = panel.getBoundingClientRect();
        dragState = {
            startX: point.clientX,
            startY: point.clientY,
            startLeft: rect.left,
            startTop: rect.top,
            moved: false
        };

        panel.classList.add('mcms-dragging');
        document.documentElement.style.cursor = 'grabbing';
        document.body.style.userSelect = 'none';

        document.addEventListener('mousemove', movePanelDrag, true);
        document.addEventListener('mouseup', endPanelDrag, true);
        document.addEventListener('touchmove', movePanelDrag, { capture: true, passive: false });
        document.addEventListener('touchend', endPanelDrag, true);
        document.addEventListener('touchcancel', endPanelDrag, true);

        event.preventDefault();
        event.stopPropagation();
    }

    function movePanelDrag(event) {
        if (!dragState) return;

        const isTouch = event.type === 'touchmove';
        const point = isTouch ? event.touches[0] : event;
        if (!point) return;

        const dx = point.clientX - dragState.startX;
        const dy = point.clientY - dragState.startY;
        if (Math.abs(dx) > 2 || Math.abs(dy) > 2) dragState.moved = true;

        const pos = clampPanelPosition(dragState.startLeft + dx, dragState.startTop + dy);
        setPanelCssPosition(pos.left, pos.top);

        event.preventDefault();
        event.stopPropagation();
    }

    function endPanelDrag(event) {
        if (!dragState) return;

        const didMove = Boolean(dragState.moved);
        const panel = document.getElementById(SCRIPT.panelId);

        if (panel) {
            panel.classList.remove('mcms-dragging');
            const rect = panel.getBoundingClientRect();
            const pos = clampPanelPosition(rect.left, rect.top);
            setPanelCssPosition(pos.left, pos.top);
            state.panelPosition = { left: pos.left, top: pos.top };
            saveState();
        }

        dragState = null;
        document.documentElement.style.cursor = '';
        document.body.style.userSelect = '';

        document.removeEventListener('mousemove', movePanelDrag, true);
        document.removeEventListener('mouseup', endPanelDrag, true);
        document.removeEventListener('touchmove', movePanelDrag, true);
        document.removeEventListener('touchend', endPanelDrag, true);
        document.removeEventListener('touchcancel', endPanelDrag, true);

        if (didMove) {
            suppressNextOutsideClick = true;
            showToast('Menu position saved');
            runtimeSetTimeout(() => { suppressNextOutsideClick = false; }, 250);
        }

        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
    }

    function openPanel() {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return;
        applyRootAttributes();
        refreshTabletModeUi(panel);
        panel.classList.add('mcms-open');
        fitControlToMap();
        runtimeSetTimeout(() => positionPanelOverlay(true), 0);
    }

    function closePanel() {
        const panel = document.getElementById(SCRIPT.panelId);
        if (panel) panel.classList.remove('mcms-open');
    }

    function togglePanel() {
        const panel = document.getElementById(SCRIPT.panelId);
        if (!panel) return;
        panel.classList.contains('mcms-open') ? closePanel() : openPanel();
    }

    function stopMapInteraction(event) {
        event.stopPropagation();
    }

    function isTypingTarget(target) {
        if (!target) return false;
        const tag = String(target.tagName || '').toLowerCase();
        return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable;
    }

    function handleKeyboard(event) {
        if (!state.shortcuts || isTypingTarget(event.target)) return;
        const key = String(event.key || '').toLowerCase();

        if (event.key === 'Escape') {
            if (state.cleanMode) toggleFeature('clean');
            closePanel();
            document.getElementById(SCRIPT.criticalDrawerId)?.classList.remove('mcms-open');
            return;
        }
        if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'm') { event.preventDefault(); togglePanel(); return; }
        if (!event.ctrlKey && !event.altKey && !event.metaKey && !event.repeat && /^[1-9]$/.test(event.key)) {
            const visibilityShortcut = {
                '1': 'myMissions',
                '2': 'allianceMissions',
                '3': 'vehicles',
                '4': 'buildings',
                '5': 'allianceCredits',
                '6': 'missionAge',
                '7': 'transportWatcher',
                '8': 'unitCommitment',
                '9': 'criticalView'
            };
            event.preventDefault();
            toggleFeature(visibilityShortcut[event.key]);
            return;
        }
        if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'c') { event.preventDefault(); toggleFeature('clean'); return; }
        if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'f') { event.preventDefault(); toggleFeature('markerFocus'); return; }
        if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'p') { event.preventDefault(); toggleFeature('missionPulse'); return; }
        if (!event.ctrlKey && !event.altKey && !event.metaKey && key === 'r') { event.preventDefault(); toggleFeature('roadPriority'); }
    }

    function buildThemeOptions(selected) {
        return THEME_ORDER.map(key => `<option value="${key}" ${key === selected ? 'selected' : ''}>${THEMES[key].full}</option>`).join('');
    }

    function makeToggleButton(key, icon, label, title) {
        return `
            <button class="mcms-toggle-btn" type="button" data-toggle="${key}" title="${escapeHtml(title || label)}">
                <span class="mcms-iconbox">${icon}</span>
                <span class="mcms-text">
                    <span class="mcms-label">${escapeHtml(label)}</span>
                    <span class="mcms-pill">OFF</span>
                </span>
            </button>
        `;
    }

    function makeFloatButton(key, shortcut, label, title, tabletLabel = label, mobileLabel = tabletLabel) {
        return `
            <button class="mcms-float-btn" type="button" data-toggle="${key}" title="${escapeHtml(title)}" aria-pressed="false">
                <span class="mcms-float-key">${escapeHtml(shortcut)}</span>
                <span class="mcms-float-label mcms-float-label-desktop">${escapeHtml(label)}</span>
                <span class="mcms-float-label mcms-float-label-tablet">${escapeHtml(tabletLabel)}</span>
                <span class="mcms-float-label mcms-float-label-mobile">${escapeHtml(mobileLabel)}</span>
            </button>
        `;
    }

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

    function createControl(mapEl) {
        if (!mapEl || document.getElementById(SCRIPT.controlId)) return;
        const control = document.createElement('div');
        control.id = SCRIPT.controlId;
        control.className = 'mcms-control';
        control.setAttribute('aria-label', `${SCRIPT.name} control`);
        control.innerHTML = `
            <div class="mcms-shell">
                <button class="mcms-menu-btn" type="button" title="Open or close toolkit settings" aria-label="Open or close toolkit settings">🗺️</button>
                <button class="mcms-dock-toggle-btn" type="button" title="Collapse command bar" aria-label="Collapse command bar" aria-expanded="true"><span class="mcms-dock-toggle-icon" aria-hidden="true">▴</span></button>
            </div>
            <div class="mcms-floating-filter" title="Persistent map visibility filters">
                ${makeFloatButton('myMissions', '1', 'Personal', 'Show/hide confidently detected personal missions. Shortcut: 1', 'Personal', 'Mine')}
                ${makeFloatButton('allianceMissions', '2', 'Alliance', 'Show/hide confidently detected alliance missions. Shortcut: 2', 'Alliance', 'Ally')}
                ${makeFloatButton('vehicles', '3', 'Vehicles', 'Show/hide confidently detected vehicles. Shortcut: 3', 'Vehicles', 'Units')}
                ${makeFloatButton('buildings', '4', 'Buildings', 'Show/hide confidently detected buildings/stations. Shortcut: 4', 'Buildings', 'Bldgs')}
                ${makeFloatButton('allianceCredits', '5', 'Ally Cred', 'Show/hide approximate credit values beside alliance mission markers. Shortcut: 5', 'Ally Credits', 'Ally £')}
                ${makeFloatButton('missionAge', '6', 'Miss Age', 'Show personal mission age with progressive 8H amber, 16H orange and 24H red severity. Shortcut: 6', 'Mission Age', 'Age')}
                ${makeFloatButton('transportWatcher', '7', 'Transport', 'Show/hide amber transport-required watchers beside missions. Shortcut: 7', 'Transport', 'Trans')}
                ${makeFloatButton('unitCommitment', '8', 'Unit Count', 'Show your committed units beside missions. Shortcut: 8', 'Unit Count', 'Count')}
                ${makeFloatButton('criticalView', '9', 'Crit View', 'Show only personal missions aged 8 hours or more and frame them on the map. Shortcut: 9', 'Critical View', 'Critical')}
            </div>
            <div class="mcms-screen-pins" title="Pinned screen shortcuts"></div>
        `;

        ['click', 'dblclick', 'mousedown', 'mouseup', 'touchstart', 'touchmove', 'touchend', 'wheel', 'contextmenu'].forEach(eventName => {
            control.addEventListener(eventName, stopMapInteraction, { passive: false });
        });

        control.addEventListener('click', event => {
            const menuButton = closestEventTarget(event, '.mcms-menu-btn');
            const dockToggleButton = closestEventTarget(event, '.mcms-dock-toggle-btn');
            const toggleButton = closestEventTarget(event, '[data-toggle]');
            const actionButton = closestEventTarget(event, '[data-action]');
            if (menuButton) { togglePanel(); return; }
            if (dockToggleButton) { toggleCommandBar(); return; }
            if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
            if (actionButton) handleAction(actionButton);
        });

        control.addEventListener('contextmenu', event => { event.preventDefault(); openPanel(); });

        mapEl.appendChild(control);
        renderScreenPins();
        updateUI();
    }

    function createPanel() {
        if (document.getElementById(SCRIPT.panelId)) return;
        const panel = document.createElement('div');
        panel.id = SCRIPT.panelId;
        panel.setAttribute('aria-label', `${SCRIPT.name} menu`);

        const buildUiThemeButtons = () => UI_THEME_ORDER.map(key => {
            const theme = UI_THEMES[key];
            return `
                <button class="mcms-ui-theme-btn" type="button" data-ui-theme="${key}" title="${escapeHtml(theme.description)}" aria-pressed="false">
                    <span class="mcms-ui-theme-preview mcms-ui-theme-preview-${key}" aria-hidden="true"><span></span><span></span><span></span></span>
                    <span class="mcms-ui-theme-copy"><strong>${escapeHtml(theme.label)}</strong><small>${escapeHtml(theme.short)}</small></span>
                </button>
            `;
        }).join('');

        const buildThemeButtons = keys => keys.map(key => {
            const theme = THEMES[key];
            return `
                <button class="mcms-theme-btn" type="button" data-theme="${key}" title="${theme.full}">
                    <span class="mcms-iconbox">${theme.icon}</span>
                    <span class="mcms-text">
                        <span class="mcms-label">${theme.label}</span>
                        <span class="mcms-pill">${theme.short}</span>
                    </span>
                </button>
            `;
        }).join('');
        const uiThemeButtons = buildUiThemeButtons();
        const coreThemeButtons = buildThemeButtons(CORE_THEME_ORDER);
        const serviceThemeButtons = buildThemeButtons(SERVICE_THEME_ORDER);

        const positionButtons = Object.entries(POSITIONS).map(([key, pos]) => `<button class="mcms-position-btn" type="button" data-position="${key}" title="${pos.label}">${pos.short}</button>`).join('');

        panel.innerHTML = `
            <div class="mcms-header">
                <div class="mcms-drag-handle" title="Hold left-click and drag this bar to move the menu">
                    <span class="mcms-title">☰ DRAG MENU HERE</span>
                    <span class="mcms-subtitle">Hold left-click on this title area. Position saves.</span>
                </div>
                <button class="mcms-reset-panel" type="button" data-action="panel-reset" title="Reset menu position">↺</button>
                <button class="mcms-close" type="button" title="Close">×</button>
            </div>
            <div class="mcms-tabs">
                <button class="mcms-tab-btn" type="button" data-tab="skins">Skins</button>
                <button class="mcms-tab-btn" type="button" data-tab="tools">Tools</button>
                <button class="mcms-tab-btn" type="button" data-tab="resources">Resources</button>
                <button class="mcms-tab-btn" type="button" data-tab="ops">Ops</button>
                <button class="mcms-tab-btn" type="button" data-tab="payouts">Payouts</button>
                <button class="mcms-tab-btn" type="button" data-tab="discord">Discord</button>
                <button class="mcms-tab-btn" type="button" data-tab="places">Places</button>
                <button class="mcms-tab-btn" type="button" data-tab="settings">Settings</button>
            </div>
            <section class="mcms-tab-panel" data-panel="skins">
                <div class="mcms-section-label">Interface theme</div>
                <div class="mcms-ui-theme-grid">${uiThemeButtons}</div>
                <div class="mcms-status mcms-ui-theme-status">Interface themes restyle the complete toolkit without changing your selected operational map skin.</div>
                <div class="mcms-section-label">Core skins</div>
                <div class="mcms-grid-2">${coreThemeButtons}</div>
                <div class="mcms-section-label">Emergency services</div>
                <div class="mcms-grid-2">${serviceThemeButtons}</div>
                <div class="mcms-status">Fire Command, Police Tactical, Medical Control and Coastal Command use lightweight local tile filters and remain compatible with map overlays.</div>
            </section>
            <section class="mcms-tab-panel" data-panel="tools">
                <div class="mcms-section-label">Map tools</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('clean', '▢', 'Clean', 'Hide map controls for screenshots. Shortcut: C')}
                    ${makeToggleButton('markerFocus', '◉', 'Focus', 'Dim detected buildings/vehicles and keep missions clearer. Shortcut: F')}
                    ${makeToggleButton('missionPulse', '✦', 'Pulse', 'Pulse detected mission markers. Shortcut: P')}
                    ${makeToggleButton('roadPriority', '═', 'Roads+', 'Increase road contrast. Shortcut: R')}
                    ${makeToggleButton('coverage', '◎', 'Rings', 'Draw coverage rings around detected buildings/stations.')}
                    ${makeToggleButton('heatmap', '▦', 'Heatmap', 'Show strong and weak operational coverage across the visible map.')}
                </div>
                <div class="mcms-row" style="margin-top:8px">
                    <span class="mcms-row-label">Ring radius</span>
                    <select class="mcms-select" data-setting="coverage-radius">
                        <option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option>
                    </select>
                </div>
                <div class="mcms-section-label">Coverage Heatmap</div>
                <div class="mcms-row"><span class="mcms-row-label">Coverage source</span><select class="mcms-select" data-setting="heatmap-source"><option value="stations">Personal stations</option><option value="vehicles">Current vehicles</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Service</span><select class="mcms-select" data-setting="heatmap-service"><option value="all">All services</option><option value="fire">Fire & rescue</option><option value="ambulance">Ambulance</option><option value="police">Police</option><option value="air">Air assets</option><option value="water">Water/coastal</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Planning radius</span><select class="mcms-select" data-setting="heatmap-radius"><option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Overlay strength</span><select class="mcms-select" data-setting="heatmap-opacity"><option value="0.18">Light</option><option value="0.30">Normal</option><option value="0.42">Strong</option></select></div>
                <div class="mcms-heat-legend"><span class="mcms-heat-key" style="background:#00c853">Strong</span><span class="mcms-heat-key" style="background:#64dd17">Good</span><span class="mcms-heat-key" style="background:#ffd600">Covered</span><span class="mcms-heat-key" style="background:#ff9100">Weak</span><span class="mcms-heat-key" style="background:#d50000">Gap</span></div>
                <div class="mcms-section-label">Map visibility · shortcuts 1–9</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('myMissions', '1', 'Personal Missions', 'Show/hide confidently detected personal missions. Shortcut: 1')}
                    ${makeToggleButton('allianceMissions', '2', 'Alliance Missions', 'Show/hide confidently detected alliance missions. Shortcut: 2')}
                    ${makeToggleButton('vehicles', '3', 'Vehicles', 'Show/hide confidently detected vehicles. Shortcut: 3')}
                    ${makeToggleButton('buildings', '4', 'Buildings', 'Show/hide confidently detected buildings/stations. Shortcut: 4')}
                    ${makeToggleButton('allianceCredits', '5', 'Ally Cred', 'Show/hide approximate credit values beside alliance mission markers. Shortcut: 5')}
                    ${makeToggleButton('missionAge', '6', 'Miss Age', 'Show personal mission age with progressive 8H amber, 16H orange and 24H red severity. Shortcut: 6')}
                    ${makeToggleButton('transportWatcher', '7', 'Transport Watcher', 'Show amber transport-required badges beside personal and alliance missions. Shortcut: 7')}
                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your committed units beside personal and alliance missions. Shortcut: 8')}
                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Temporarily show only personal missions aged 8 hours or more. Shortcut: 9')}
                </div>
                <div class="mcms-row" style="margin-top:8px"><span class="mcms-row-label">Ally Credits filter</span><select class="mcms-select" data-setting="alliance-credit-minimum"><option value="0">All values</option><option value="5000">5K+</option><option value="10000">10K+</option><option value="15000">15K+</option><option value="20000">20K+</option></select></div>
                <div class="mcms-status">Ready.</div>
            </section>
            <section class="mcms-tab-panel" data-panel="resources">
                <div class="mcms-section-label">Co-admin Patient Transport Sweep</div>
                <div class="mcms-grid-2">
                    <button class="mcms-small-btn" type="button" data-action="scan-transport-sweep">Scan Transports</button>
                    <button class="mcms-small-btn" type="button" data-action="start-transport-sweep">Start Sweep</button>
                    <button class="mcms-small-btn" type="button" data-action="stop-transport-sweep">Stop</button>
                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}
                </div>
                <div class="mcms-row"><span class="mcms-row-label">Delay between clears</span><select class="mcms-select" data-setting="transport-sweep-delay"><option value="1500">1.5 seconds</option><option value="2000">2 seconds</option><option value="2500">2.5 seconds</option><option value="3000">3 seconds</option><option value="4000">4 seconds</option><option value="5000">5 seconds</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Maximum per run</span><input class="mcms-input" type="number" min="1" max="50" step="1" data-setting="transport-sweep-max"></div>
                <div data-transport-sweep></div>
                <div class="mcms-status">Manual start only. The sweep excludes your personal vehicle IDs, checks every non-personal FMS 5 patient vehicle in each affected alliance mission, and only clears a vehicle when MissionChief exposes the visible <b>Discharge patient</b> button. Prisoner transports are not included.</div>
                <div class="mcms-section-label">Resource Gap Finder</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('resourceGap', '⚠', 'Resource Gap', 'Show missing-resource badges and nearby available-unit estimates in Mission Inspector.')}
                </div>
                <div class="mcms-row"><span class="mcms-row-label">Nearby radius</span><select class="mcms-select" data-setting="resource-gap-radius"><option value="10">10 miles</option><option value="25">25 miles</option><option value="50">50 miles</option><option value="100">100 miles</option></select></div>
                <div class="mcms-status">Resource Gap uses MissionChief's missing-requirement text and performs best-effort matching against your currently available vehicle types. It never selects or dispatches units.</div>
            </section>
            <section class="mcms-tab-panel" data-panel="ops">
                <div class="mcms-section-label">Mission Intelligence</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('missionInspector', 'ⓘ', 'Inspector', 'Hover a mission marker for a live mission summary.')}
                    ${makeToggleButton('stuckDetector', '⚠', 'Stuck Detect', 'Flag personal or joined missions that show no meaningful progress.')}
                    ${makeToggleButton('missionSpawn', '◎', 'New Mission', 'Animate genuinely new mission spawns with a radar pulse.')}
                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}
                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}
                </div>
                <div class="mcms-row"><span class="mcms-row-label">Stuck after</span><select class="mcms-select" data-setting="stuck-threshold"><option value="10">10 minutes</option><option value="15">15 minutes</option><option value="20">20 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option><option value="60">60 minutes</option></select></div>
                <div class="mcms-status">Stuck detection resets its timer whenever missing requirements, patients, prisoners, progress value or your assigned-unit state changes.</div>
                <div class="mcms-section-label">Session Performance</div>
                <div data-ops-session></div>
                <div class="mcms-section-label">Mission Age Workflow</div>
                <div class="mcms-grid-2">
                    <button class="mcms-small-btn" style="height:34px !important;line-height:34px !important" type="button" data-action="open-critical-drawer">Open Mission Drawer</button>
                    <button class="mcms-small-btn" style="height:34px !important;line-height:34px !important" type="button" data-action="fit-critical">Frame Aged</button>
                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}
                    ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}
                </div>
                <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>
                <div class="mcms-ops-list" data-ops-critical-preview></div>
                <div class="mcms-section-label">Completion History</div>
                <div class="mcms-ops-list" data-ops-history></div>
                <div class="mcms-grid-2" style="margin-top:7px !important">
                    <button class="mcms-small-btn" type="button" data-action="reset-session">Reset Session</button>
                    <button class="mcms-small-btn" type="button" data-action="clear-payout-history">Clear History</button>
                </div>
            </section>
            <section class="mcms-tab-panel" data-panel="payouts">
                <div class="mcms-section-label">Emergency Payout Flash</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('payoutFlash', '🚨', 'Payout Flash', 'Flash the map red and blue when a single credit gain reaches the configured threshold.')}
                    ${makeToggleButton('payoutSound', '♪', 'Theme Audio', 'Play the selected template completion cue. Vice City, Bad Company, Scarface and Cyberpunk use hosted MP3 cashout sounds; other templates retain synthesized cues.')}
                </div>
                <div class="mcms-row"><span class="mcms-row-label">Banner style</span><select class="mcms-select" data-setting="payout-template">${buildPayoutTemplateOptions(state.payoutFlash.template)}</select></div>
                <div class="mcms-row"><span class="mcms-row-label">Minimum payout</span><input class="mcms-input" type="number" min="1000" step="1000" data-setting="payout-threshold"></div>
                <div class="mcms-row"><span class="mcms-row-label">Flash duration (sec)</span><input class="mcms-input" type="number" min="2" max="30" step="2" data-setting="payout-duration"></div>
                <div class="mcms-row"><span class="mcms-row-label">Sound volume</span><input class="mcms-input" type="range" min="0" max="1" step="0.05" data-setting="payout-volume"></div>
                <div class="mcms-row"><span class="mcms-row-label">Test payout tier</span><select class="mcms-select" data-setting="payout-test-amount"><option value="10000">10K Standard</option><option value="25000">25K Major</option><option value="50000">50K High Value</option><option value="100000">100K Elite</option></select></div>
                <button class="mcms-small-btn" style="width:100% !important;margin-bottom:8px !important" type="button" data-action="test-payout-flash">Test Emergency Flash</button>
                <div class="mcms-status">Vice City Inspired, Bad Company Inspired, Scarface Inspired and Cyberpunk Inspired use hosted cashout MP3s from your public GitHub asset repository. Other templates retain synthesized cues. Enable Theme Audio, set the volume, then use Test Emergency Flash.</div>
            </section>
            <section class="mcms-tab-panel" data-panel="discord">
                <div class="mcms-section-label">Discord Financial Intelligence</div>
                <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook URL</span><input class="mcms-input" type="password" autocomplete="off" spellcheck="false" data-setting="discord-webhook" placeholder="https://discord.com/api/webhooks/..."></div>
                <div class="mcms-row mcms-discord-wide"><span class="mcms-row-label">Webhook name</span><input class="mcms-input" type="text" maxlength="80" data-setting="discord-name" value="MissionChief Finance"></div>
                <div class="mcms-row"><span class="mcms-row-label">Report period</span><select class="mcms-select" data-setting="discord-period"><option value="today">Today</option><option value="yesterday">Yesterday</option><option value="last24">Last 24 Hours</option><option value="last7">Last 7 Days</option><option value="last30">Last 30 Days</option><option value="session">Current Session</option><option value="sinceLast">Since Last Report</option><option value="custom">Custom Dates</option></select></div>
                <div class="mcms-discord-date-grid">
                    <div class="mcms-row"><span class="mcms-row-label">From</span><input class="mcms-input" type="date" data-setting="discord-custom-start"></div>
                    <div class="mcms-row"><span class="mcms-row-label">To</span><input class="mcms-input" type="date" data-setting="discord-custom-end"></div>
                </div>
                <div class="mcms-row"><span class="mcms-row-label">Breakdown depth</span><select class="mcms-select" data-setting="discord-top-categories"><option value="3">Top 3</option><option value="5">Top 5</option><option value="8">Top 8</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Previous-period comparison</span><select class="mcms-select" data-setting="discord-comparison"><option value="true">Included</option><option value="false">Disabled</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Discord chart image</span><select class="mcms-select" data-setting="discord-chart"><option value="true">Attach chart</option><option value="false">Text only</option></select></div>
                <div class="mcms-grid-2">
                    <button class="mcms-small-btn" type="button" data-action="discord-test">Test Connection</button>
                    <button class="mcms-small-btn" type="button" data-action="discord-clear">Clear Webhook</button>
                </div>
                <button class="mcms-small-btn" style="width:100% !important;margin-top:7px !important" type="button" data-action="discord-generate-post">Generate and Post</button>
                <div class="mcms-status mcms-discord-status" data-discord-status data-tone="neutral">Select a reporting period, then generate and post the financial intelligence report.</div>
                <div class="mcms-status">Reports use MissionChief’s timestamped transaction ledger, calculate detailed income and spending categories, reconcile opening/closing balances, compare the previous equivalent period, assign an unofficial performance grade, and can attach a generated chart. Longer first-time reports may read several ledger pages.</div>
            </section>
            <section class="mcms-tab-panel" data-panel="places">
                <div class="mcms-section-label">Quick jumps + screen shortcuts</div>
                <div class="mcms-quick-list"></div>
                <div class="mcms-section-label">Custom bookmarks + screen shortcuts</div>
                <div class="mcms-bookmark-list"></div>
            </section>
            <section class="mcms-tab-panel" data-panel="settings">
                <div class="mcms-section-label">Device layout</div>
                <div class="mcms-row"><span class="mcms-row-label">Mobile Mode · iOS Safari</span><select class="mcms-select" data-setting="mobile-mode"><option value="auto">Auto detect iPhone</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
                <div class="mcms-row"><span class="mcms-row-label">Tablet Mode</span><select class="mcms-select" data-setting="tablet-mode"><option value="auto">Auto detect</option><option value="on">Always on</option><option value="off">Always off</option></select></div>
                <div class="mcms-status" data-device-layout-status>Detecting device layout…</div>
                <div class="mcms-status">Mobile Mode is tuned for iPhone Safari with Tampermonkey: a map-aware 5×2 command grid in portrait, a compact single-row dock where space allows, full-width safe-area bottom sheets, 16px form controls to prevent Safari input zoom, and Visual Viewport handling for the iOS keyboard. Tablet and desktop layouts remain separate and unchanged.</div>
                <div class="mcms-section-label">Dock position</div>
                <div class="mcms-position-grid">${positionButtons}</div>
                <div class="mcms-desktop-position-controls">
                    <div class="mcms-section-label">Fine nudge</div>
                    <div class="mcms-nudge-grid">
                        <button class="mcms-small-btn" type="button" data-action="nudge-left">←</button>
                        <button class="mcms-small-btn" type="button" data-action="nudge-up">↑</button>
                        <button class="mcms-small-btn" type="button" data-action="nudge-down">↓</button>
                        <button class="mcms-small-btn" type="button" data-action="nudge-right">→</button>
                        <button class="mcms-small-btn" type="button" data-action="nudge-reset">0</button>
                    </div>
                    <div class="mcms-status mcms-nudge-value">X 0 / Y 0</div>
                    <div class="mcms-section-label">Menu panel</div>
                    <div class="mcms-nudge-grid">
                        <button class="mcms-small-btn" type="button" data-action="panel-left">←</button>
                        <button class="mcms-small-btn" type="button" data-action="panel-up">↑</button>
                        <button class="mcms-small-btn" type="button" data-action="panel-down">↓</button>
                        <button class="mcms-small-btn" type="button" data-action="panel-right">→</button>
                        <button class="mcms-small-btn" type="button" data-action="panel-reset">↺</button>
                    </div>
                </div>
                <div class="mcms-section-label">Behaviour</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('shortcuts', '⌨', 'Keys', 'Keyboard shortcuts on/off. Map tools: 1–9. Menu: M.')}
                    ${makeToggleButton('autoNight', '◑', 'AutoNight', 'Automatically switch skins by time.')}
                </div>
                <div class="mcms-section-label">Auto Night</div>
                <div class="mcms-row"><span class="mcms-row-label">Night starts</span><input class="mcms-input" type="time" data-setting="auto-night-start"></div>
                <div class="mcms-row"><span class="mcms-row-label">Day starts</span><input class="mcms-input" type="time" data-setting="auto-day-start"></div>
                <div class="mcms-row"><span class="mcms-row-label">Night skin</span><select class="mcms-select" data-setting="auto-night-theme">${buildThemeOptions(state.autoNight.nightTheme)}</select></div>
                <div class="mcms-row"><span class="mcms-row-label">Day skin</span><select class="mcms-select" data-setting="auto-day-theme">${buildThemeOptions(state.autoNight.dayTheme)}</select></div>
                <div class="mcms-section-label">Saved Map Profiles</div>
                <div class="mcms-profile-list" data-profile-list></div>
                <div class="mcms-status">Profiles save your map location, zoom, skin, visibility filters and operational overlays.</div>
                <div class="mcms-section-label">Settings Backup</div>
                <div class="mcms-config-actions">
                    <button class="mcms-small-btn" type="button" data-action="export-config" title="Export every toolkit setting, profile, bookmark and saved Discord webhook" aria-label="Export all toolkit settings">Export All</button>
                    <button class="mcms-small-btn" type="button" data-action="import-config" title="Import a current or legacy toolkit settings backup" aria-label="Import all toolkit settings">Import All</button>
                    <button class="mcms-small-btn" type="button" data-action="reset-config">Reset</button>
                </div>
                <input class="mcms-hidden-file" type="file" accept="application/json,text/json,.json" data-import-config-file>
                <div class="mcms-status">Backups include every persistent toolkit preference, desktop/Tablet/iOS layout choice, profile, bookmark and saved Discord webhook. The JSON file can contain the private webhook token, so store it securely. Current and legacy toolkit backup files are supported.</div>
            </section>
            <div class="mcms-footer">
                <span>v3.5.1: Completed a full Cyberpunk readability pass with accessible active-state contrast, clearer secondary text, improved focus visibility and readable disabled controls.</span>
                <span class="mcms-build">${SCRIPT.name} v${SCRIPT.version} · MIT · ${SCRIPT.author}</span>
            </div>
        `;

        panel.addEventListener('click', event => {
            const closeButton = closestEventTarget(event, '.mcms-close');
            const tabButton = closestEventTarget(event, '.mcms-tab-btn');
            const uiThemeButton = closestEventTarget(event, '.mcms-ui-theme-btn');
            const themeButton = closestEventTarget(event, '.mcms-theme-btn');
            const toggleButton = closestEventTarget(event, '[data-toggle]');
            const positionButton = closestEventTarget(event, '.mcms-position-btn');
            const actionButton = closestEventTarget(event, '[data-action]');
            if (closeButton) { closePanel(); return; }
            if (tabButton) { setActiveTab(tabButton.dataset.tab); return; }
            if (uiThemeButton) { applyUiTheme(uiThemeButton.dataset.uiTheme, true); return; }
            if (themeButton) { applyTheme(themeButton.dataset.theme, true); return; }
            if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
            if (positionButton) { applyPosition(positionButton.dataset.position, true); return; }
            if (actionButton) {
                event.preventDefault();
                handleAction(actionButton);
                return;
            }
        });

        panel.addEventListener('change', event => handleSettingChange(event.target));

        const dragHandle = panel.querySelector('.mcms-drag-handle');
        if (dragHandle) {
            dragHandle.addEventListener('mousedown', startPanelDrag, true);
            dragHandle.addEventListener('touchstart', startPanelDrag, { capture: true, passive: false });
        }

        ['click', 'dblclick', 'mousedown', 'mouseup', 'mousemove', 'wheel', 'contextmenu', 'touchstart', 'touchmove', 'touchend'].forEach(eventName => {
            panel.addEventListener(eventName, event => event.stopPropagation(), { passive: false });
        });

        document.body.appendChild(panel);
        const importInput = panel.querySelector('[data-import-config-file]');
        if (importInput) {
            importInput.addEventListener('change', () => {
                const file = importInput.files?.[0];
                if (file) importToolkitConfigFile(file);
                importInput.value = '';
            });
        }
        renderQuickPlaces();
        renderBookmarks();
        renderProfiles();
        updateUI();
    }

    function renderQuickPlaces() {
        const list = document.querySelector(`#${SCRIPT.panelId} .mcms-quick-list`);
        if (!list) return;
        list.innerHTML = QUICK_PLACES.map(place => `
            <div class="mcms-quick-row">
                <button class="mcms-place-main" type="button" data-action="place-go" data-place="${place.id}" title="Jump to ${escapeHtml(place.name)}">
                    <span class="mcms-iconbox">⌖</span><span class="mcms-text"><span class="mcms-label">${escapeHtml(place.name)}</span><span class="mcms-pill">${place.label}</span></span>
                </button>
                <button class="mcms-pin-btn ${state.quickPins[place.id] ? 'mcms-on' : ''}" type="button" data-action="quick-pin" data-place="${place.id}" title="Pin as persistent screen shortcut">${state.quickPins[place.id] ? 'ON' : 'PIN'}</button>
            </div>
        `).join('');
    }

    function renderBookmarks() {
        const list = document.querySelector(`#${SCRIPT.panelId} .mcms-bookmark-list`);
        if (!list) return;
        list.innerHTML = state.bookmarks.map((bookmark, index) => {
            if (!bookmark) {
                return `<div class="mcms-bookmark-row"><span class="mcms-bookmark-name">Slot ${index + 1} empty</span><span></span><span></span><button class="mcms-bookmark-btn" type="button" data-action="bookmark-save" data-slot="${index}">Save</button><span></span></div>`;
            }
            return `
                <div class="mcms-bookmark-row">
                    <span class="mcms-bookmark-name" title="${escapeHtml(bookmark.name)}">${escapeHtml(bookmark.name)}</span>
                    <button class="mcms-bookmark-btn" type="button" data-action="bookmark-go" data-slot="${index}">Go</button>
                    <button class="mcms-pin-btn ${bookmark.pinned ? 'mcms-on' : ''}" type="button" data-action="bookmark-pin" data-slot="${index}" title="Pin as persistent screen shortcut">${bookmark.pinned ? 'ON' : 'PIN'}</button>
                    <button class="mcms-bookmark-btn" type="button" data-action="bookmark-save" data-slot="${index}">Save</button>
                    <button class="mcms-bookmark-btn" type="button" data-action="bookmark-delete" data-slot="${index}">×</button>
                </div>`;
        }).join('');
    }

    function renderScreenPins() {
        const dock = document.querySelector(`#${SCRIPT.controlId} .mcms-screen-pins`);
        if (!dock) return;
        const buttons = [];
        for (const place of QUICK_PLACES) {
            if (!state.quickPins[place.id]) continue;
            buttons.push(`<button class="mcms-screen-pin-btn mcms-pin-quick" type="button" data-action="place-go" data-place="${place.id}" title="Jump to ${escapeHtml(place.name)}">${escapeHtml(place.name)}</button>`);
        }
        state.bookmarks.forEach((bookmark, index) => {
            if (!bookmark || !bookmark.pinned) return;
            buttons.push(`<button class="mcms-screen-pin-btn mcms-pin-custom" type="button" data-action="bookmark-go" data-slot="${index}" title="Jump to ${escapeHtml(bookmark.name)}">${escapeHtml(bookmark.name)}</button>`);
        });
        dock.innerHTML = buttons.join('');
        if (isTouchLayoutActive()) fitControlToMap();
    }

    function handleAction(button) {
        const action = button.dataset.action;
        if (action === 'place-go') {
            const place = QUICK_PLACES.find(item => item.id === button.dataset.place);
            if (place && setMapView(place.lat, place.lng, place.zoom)) showToast(place.name);
            return;
        }
        if (action === 'quick-pin') { toggleQuickPin(button.dataset.place); return; }
        if (action === 'bookmark-save') { saveBookmark(Number(button.dataset.slot)); return; }
        if (action === 'bookmark-go') { goBookmark(Number(button.dataset.slot)); return; }
        if (action === 'bookmark-delete') { deleteBookmark(Number(button.dataset.slot)); return; }
        if (action === 'bookmark-pin') { toggleBookmarkPin(Number(button.dataset.slot)); return; }
        if (action === 'nudge-left') { nudgeControl(-4, 0); return; }
        if (action === 'nudge-right') { nudgeControl(4, 0); return; }
        if (action === 'nudge-up') { nudgeControl(0, -4); return; }
        if (action === 'nudge-down') { nudgeControl(0, 4); return; }
        if (action === 'nudge-reset') { resetNudge(); return; }
        if (action === 'panel-left') { nudgePanel(-24, 0); return; }
        if (action === 'panel-right') { nudgePanel(24, 0); return; }
        if (action === 'panel-up') { nudgePanel(0, -24); return; }
        if (action === 'panel-down') { nudgePanel(0, 24); return; }
        if (action === 'open-critical-drawer') { toggleCriticalDrawer(); return; }
        if (action === 'fit-critical') { fitCriticalMissions(); return; }
        if (action === 'scan-transport-sweep') { const queue = buildTransportSweepQueue(); showToast(queue.length ? `${queue.length} transport mission${queue.length === 1 ? '' : 's'} found` : 'No alliance patient transports found'); return; }
        if (action === 'start-transport-sweep') { startTransportSweep(); return; }
        if (action === 'stop-transport-sweep') { stopTransportSweep(); return; }
        if (action === 'reset-session') { resetSessionPerformance(); return; }
        if (action === 'clear-payout-history') { clearPayoutHistory(); return; }
        if (action === 'critical-go') { focusMissionById(button.dataset.missionId, false); return; }
        if (action === 'profile-save') { saveMapProfile(Number(button.dataset.slot)); return; }
        if (action === 'profile-load') { loadMapProfile(Number(button.dataset.slot)); return; }
        if (action === 'profile-delete') { deleteMapProfile(Number(button.dataset.slot)); return; }
        if (action === 'export-config') { exportToolkitConfig(); return; }
        if (action === 'import-config') { document.querySelector(`#${SCRIPT.panelId} [data-import-config-file]`)?.click?.(); return; }
        if (action === 'reset-config') { resetToolkitConfiguration(); return; }
        if (action === 'discord-test') { testDiscordWebhook(); return; }
        if (action === 'discord-generate-post') { postDiscordFinancialReport(); return; }
        if (action === 'discord-clear') { clearDiscordWebhook(); return; }
        if (action === 'test-payout-flash') {
            const testAmount = Math.max(1000, Number(document.querySelector(`#${SCRIPT.panelId} [data-setting="payout-test-amount"]`)?.value) || state.payoutFlash.threshold);
            const triggered = triggerPayoutFlash(testAmount, true, { source: 'personal', caption: 'Emergency Response Test' });
            showToast(triggered ? 'Emergency flash test' : 'Emergency flash unavailable: map not detected');
            return;
        }
        if (action === 'panel-reset') resetPanelPosition();
    }

    function handleSettingChange(target) {
        const setting = target.dataset.setting;
        if (!setting) return;

        if (setting === 'mobile-mode' || setting === 'tablet-mode') {
            const nextValue = ['auto', 'on', 'off'].includes(String(target.value)) ? String(target.value) : 'auto';
            const previousLayout = activeDeviceLayout;
            if (setting === 'mobile-mode') {
                state.mobileMode = nextValue;
                if (nextValue === 'on') state.tabletMode = 'off';
            } else {
                state.tabletMode = nextValue;
                if (nextValue === 'on') state.mobileMode = 'off';
            }
            saveState();
            applyRootAttributes();
            refreshTabletModeUi();
            if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
                clearTabletPanelSizing();
                clearTabletDockSizing();
            }
            fitControlToMap();
            positionPanelOverlay(true);
            showToast(activeDeviceLayout === 'mobile' ? 'iOS Mobile Mode active' : activeDeviceLayout === 'tablet' ? 'Tablet Mode active' : 'Desktop layout active');
            return;
        }

        if (setting === 'coverage-radius') {
            state.coverage.radiusMi = Number(target.value) || 10;
            saveState();
            updateUI();
            scheduleCoverageRefresh();
            return;
        }

        if (setting === 'heatmap-source') state.heatmap.source = target.value === 'vehicles' ? 'vehicles' : 'stations';
        if (setting === 'heatmap-service') state.heatmap.service = ['all', 'fire', 'ambulance', 'police', 'air', 'water'].includes(target.value) ? target.value : 'all';
        if (setting === 'heatmap-radius') state.heatmap.radiusMi = Number(target.value) || 10;
        if (setting === 'heatmap-opacity') state.heatmap.opacity = clamp(target.value, 0.12, 0.55, 0.30);
        if (setting.startsWith('heatmap-')) {
            saveState(); updateUI(); scheduleHeatmapRefresh(); return;
        }


        if (setting === 'transport-sweep-delay') {
            state.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 2000;
            saveState(); updateUI();
            showToast(`Transport Sweep delay: ${state.transportSweep.delayMs / 1000}s`);
            return;
        }
        if (setting === 'transport-sweep-max') {
            state.transportSweep.maxPerRun = Math.round(clamp(target.value, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
            saveState(); updateUI();
            showToast(`Transport Sweep maximum: ${state.transportSweep.maxPerRun}`);
            return;
        }

        if (setting === 'resource-gap-radius') {
            state.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(target.value)) ? Number(target.value) : 25;
            resourceGapAnalysisCache.clear();
            saveState(); updateUI(); scheduleResourceGapRefresh(0); refreshVisibleMissionInspector();
            showToast(`Resource Gap radius: ${state.resourceGap.radiusMi}mi`);
            return;
        }

        if (setting === 'stuck-threshold') {
            state.stuckDetector.thresholdMin = Math.round(clamp(target.value, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
            saveState();
            updateUI();
            scheduleStuckMissionRefresh(0);
            showToast(`Stuck missions: ${state.stuckDetector.thresholdMin} minutes`);
            return;
        }

        if (setting === 'alliance-credit-minimum') {
            state.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(target.value)) ? Number(target.value) : 0;
            saveState();
            updateUI();
            scheduleAllianceCreditRefresh(0);
            showToast(state.allianceCreditMinimum ? `Alliance credits: ${state.allianceCreditMinimum / 1000}K+` : 'Alliance credits: all values');
            return;
        }

        if (setting === 'discord-webhook') {
            try {
                saveDiscordWebhookUrl(target.value);
                setDiscordStatus(target.value ? 'Webhook saved securely in Tampermonkey storage.' : 'Webhook removed.', 'good');
            } catch (err) {
                setDiscordStatus(err?.message || 'Webhook URL is invalid.', 'bad');
            }
            return;
        }
        if (setting === 'discord-name') {
            state.discordReport.webhookName = String(target.value || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
            saveState(); updateUI();
            return;
        }
        if (setting === 'discord-top-categories') {
            state.discordReport.topCategories = [3, 5, 8].includes(Number(target.value)) ? Number(target.value) : 5;
            invalidateDiscordFinancialPreview();
            saveState(); updateUI();
            return;
        }
        if (setting === 'discord-period') {
            state.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'session', 'sinceLast', 'custom'].includes(target.value) ? target.value : 'today';
            invalidateDiscordFinancialPreview();
            saveState(); updateUI();
            return;
        }
        if (setting === 'discord-custom-start' || setting === 'discord-custom-end') {
            const key = setting === 'discord-custom-start' ? 'customStart' : 'customEnd';
            if (/^\d{4}-\d{2}-\d{2}$/u.test(String(target.value || ''))) state.discordReport[key] = String(target.value);
            invalidateDiscordFinancialPreview();
            saveState(); updateUI();
            return;
        }
        if (setting === 'discord-comparison') {
            state.discordReport.includeComparison = String(target.value) !== 'false';
            invalidateDiscordFinancialPreview();
            saveState(); updateUI();
            return;
        }
        if (setting === 'discord-chart') {
            state.discordReport.includeChart = String(target.value) !== 'false';
            invalidateDiscordFinancialPreview();
            saveState(); updateUI();
            return;
        }

        if (setting === 'payout-template') {
            state.payoutFlash.template = PAYOUT_TEMPLATES[target.value] ? target.value : 'gta5';
            disposePayoutMediaAudio();
            saveState();
            updateUI();
            const hostedCue = PAYOUT_MEDIA_SOUNDS[state.payoutFlash.template];
            showToast(hostedCue
                ? `${payoutTemplateMeta(state.payoutFlash.template).label} · ${hostedCue.label} ready`
                : `${payoutTemplateMeta(state.payoutFlash.template).label} payout template`);
            return;
        }
        if (setting === 'payout-threshold') {
            state.payoutFlash.threshold = Math.round(clamp(target.value, 1000, 1000000000, 10000));
            saveState();
            updateUI();
            showToast(`Payout flash: ${state.payoutFlash.threshold.toLocaleString()}+`);
            return;
        }
        if (setting === 'payout-duration') {
            state.payoutFlash.durationMs = normalisePayoutFlashDuration(Number(target.value) * 1000);
            saveState();
            updateUI();
            showToast(`Payout flash: ${state.payoutFlash.durationMs / 1000} seconds`);
            return;
        }
        if (setting === 'payout-volume') {
            state.payoutFlash.soundVolume = clamp(target.value, 0, 1, 0.35);
            if (payoutMediaAudio && !payoutMediaAudio.paused) payoutMediaAudio.volume = state.payoutFlash.soundVolume;
            saveState();
            updateUI();
            return;
        }
        if (setting === 'payout-test-amount') return;

        if (setting === 'auto-night-start') state.autoNight.nightStart = target.value || '19:00';
        if (setting === 'auto-day-start') state.autoNight.dayStart = target.value || '07:00';
        if (setting === 'auto-night-theme') state.autoNight.nightTheme = normaliseTheme(target.value);
        if (setting === 'auto-day-theme') state.autoNight.dayTheme = normaliseTheme(target.value);

        if (setting.startsWith('auto-')) {
            state.autoNight.lastBucket = '';
            saveState();
            runAutoNight(true);
            updateUI();
        }
    }

    function updateUI() {
        applyRootAttributes();

        const control = document.getElementById(SCRIPT.controlId);
        const panel = document.getElementById(SCRIPT.panelId);

        if (control) {
            for (const pos of Object.keys(POSITIONS)) control.classList.toggle(`mcms-pos-${pos}`, state.position === pos);
            control.style.setProperty('--mcms-nudge-x', `${state.nudge.x}px`);
            control.style.setProperty('--mcms-nudge-y', `${state.nudge.y}px`);
            const controlToggleValues = {
                allianceMissions: state.visibility.allianceMissions,
                myMissions: state.visibility.myMissions,
                vehicles: state.visibility.vehicles,
                buildings: state.visibility.buildings,
                allianceCredits: state.allianceCredits,
                missionAge: state.missionAge,
                transportWatcher: state.transportWatcher,
                unitCommitment: state.unitCommitment,
                criticalView: criticalViewActive
            };
            control.querySelectorAll('[data-toggle]').forEach(btn => {
                const on = Boolean(controlToggleValues[btn.dataset.toggle]);
                btn.classList.toggle('mcms-on', on);
                btn.setAttribute('aria-pressed', String(on));
                btn.dataset.mcmsState = on ? 'on' : 'off';
            });

            const dockToggleButton = control.querySelector('.mcms-dock-toggle-btn');
            if (dockToggleButton) {
                const open = state.commandBarOpen !== false;
                const label = open ? 'Collapse command bar' : 'Expand command bar';
                dockToggleButton.classList.toggle('mcms-open', open);
                dockToggleButton.setAttribute('aria-expanded', String(open));
                dockToggleButton.setAttribute('aria-label', label);
                dockToggleButton.title = label;
                const icon = dockToggleButton.querySelector('.mcms-dock-toggle-icon');
                if (icon) icon.textContent = open ? '▴' : '▾';
            }
        }

        if (!panel) return;

        refreshTabletModeUi(panel);
        panel.querySelectorAll('.mcms-tab-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.tab === state.activeTab));
        panel.querySelectorAll('.mcms-tab-panel').forEach(tabPanel => tabPanel.classList.toggle('mcms-active', tabPanel.dataset.panel === state.activeTab));
        panel.querySelectorAll('.mcms-ui-theme-btn').forEach(btn => {
            const active = btn.dataset.uiTheme === state.uiTheme;
            btn.classList.toggle('mcms-active', active);
            btn.setAttribute('aria-pressed', String(active));
        });
        panel.querySelectorAll('.mcms-theme-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.theme === state.theme));
        panel.querySelectorAll('.mcms-position-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.position === state.position));

        const toggleValues = {
            clean: state.cleanMode,
            markerFocus: state.markerFocus,
            missionPulse: state.missionPulse,
            roadPriority: state.roadPriority,
            coverage: state.coverage.enabled,
            heatmap: state.heatmap.enabled,
            shortcuts: state.shortcuts,
            autoNight: state.autoNight.enabled,
            payoutFlash: state.payoutFlash.enabled,
            payoutSound: state.payoutFlash.soundEnabled,
            missionInspector: state.missionInspector,
            stuckDetector: state.stuckDetector.enabled,
            missionSpawn: state.missionSpawn.enabled,
            resourceGap: state.resourceGap.enabled,
            allianceMissions: state.visibility.allianceMissions,
            myMissions: state.visibility.myMissions,
            vehicles: state.visibility.vehicles,
            buildings: state.visibility.buildings,
            allianceCredits: state.allianceCredits,
            missionAge: state.missionAge,
            transportWatcher: state.transportWatcher,
            unitCommitment: state.unitCommitment,
            criticalView: criticalViewActive
        };

        panel.querySelectorAll('[data-toggle]').forEach(btn => {
            const key = btn.dataset.toggle;
            const on = Boolean(toggleValues[key]);
            btn.classList.toggle('mcms-on', on);
            const pill = btn.querySelector('.mcms-pill');
            if (pill) pill.textContent = key === 'coverage' ? (on ? `${state.coverage.radiusMi}mi` : 'OFF') : key === 'heatmap' ? (on ? `${state.heatmap.radiusMi}mi` : 'OFF') : (on ? 'ON' : 'OFF');
        });

        const radius = panel.querySelector('[data-setting="coverage-radius"]');
        if (radius) radius.value = String(state.coverage.radiusMi);
        const heatmapSource = panel.querySelector('[data-setting="heatmap-source"]');
        if (heatmapSource) heatmapSource.value = state.heatmap.source;
        const heatmapService = panel.querySelector('[data-setting="heatmap-service"]');
        if (heatmapService) heatmapService.value = state.heatmap.service;
        const heatmapRadius = panel.querySelector('[data-setting="heatmap-radius"]');
        if (heatmapRadius) heatmapRadius.value = String(state.heatmap.radiusMi);
        const heatmapOpacity = panel.querySelector('[data-setting="heatmap-opacity"]');
        if (heatmapOpacity) heatmapOpacity.value = String(state.heatmap.opacity);
        const allianceCreditMinimum = panel.querySelector('[data-setting="alliance-credit-minimum"]');
        if (allianceCreditMinimum) allianceCreditMinimum.value = String(state.allianceCreditMinimum);
        const transportSweepDelay = panel.querySelector('[data-setting="transport-sweep-delay"]');
        if (transportSweepDelay) transportSweepDelay.value = String(state.transportSweep.delayMs);
        const transportSweepMax = panel.querySelector('[data-setting="transport-sweep-max"]');
        if (transportSweepMax) transportSweepMax.value = String(state.transportSweep.maxPerRun);
        renderTransportSweepPanel();
        const payoutTemplate = panel.querySelector('[data-setting="payout-template"]');
        if (payoutTemplate) payoutTemplate.value = state.payoutFlash.template;
        const resourceGapRadius = panel.querySelector('[data-setting="resource-gap-radius"]'); if (resourceGapRadius) resourceGapRadius.value = String(state.resourceGap.radiusMi);
        const stuckThreshold = panel.querySelector('[data-setting="stuck-threshold"]');
        if (stuckThreshold) stuckThreshold.value = String(state.stuckDetector.thresholdMin);
        const payoutThreshold = panel.querySelector('[data-setting="payout-threshold"]');
        if (payoutThreshold) payoutThreshold.value = String(state.payoutFlash.threshold);
        const payoutDuration = panel.querySelector('[data-setting="payout-duration"]');
        if (payoutDuration) payoutDuration.value = String(state.payoutFlash.durationMs / 1000);
        const payoutVolume = panel.querySelector('[data-setting="payout-volume"]');
        if (payoutVolume) payoutVolume.value = String(state.payoutFlash.soundVolume);
        const discordWebhook = panel.querySelector('[data-setting="discord-webhook"]');
        if (discordWebhook && document.activeElement !== discordWebhook) discordWebhook.value = getDiscordWebhookUrl();
        const discordName = panel.querySelector('[data-setting="discord-name"]');
        if (discordName && document.activeElement !== discordName) discordName.value = state.discordReport.webhookName;
        const discordTopCategories = panel.querySelector('[data-setting="discord-top-categories"]');
        if (discordTopCategories) discordTopCategories.value = String(state.discordReport.topCategories);
        const discordPeriod = panel.querySelector('[data-setting="discord-period"]');
        if (discordPeriod) discordPeriod.value = state.discordReport.period;
        const discordCustomStart = panel.querySelector('[data-setting="discord-custom-start"]');
        if (discordCustomStart && document.activeElement !== discordCustomStart) discordCustomStart.value = state.discordReport.customStart;
        const discordCustomEnd = panel.querySelector('[data-setting="discord-custom-end"]');
        if (discordCustomEnd && document.activeElement !== discordCustomEnd) discordCustomEnd.value = state.discordReport.customEnd;
        const discordComparison = panel.querySelector('[data-setting="discord-comparison"]');
        if (discordComparison) discordComparison.value = String(state.discordReport.includeComparison);
        const discordChart = panel.querySelector('[data-setting="discord-chart"]');
        if (discordChart) discordChart.value = String(state.discordReport.includeChart);
        setDiscordStatus(discordFinanceStatus, discordFinanceStatusTone);
        const nightStart = panel.querySelector('[data-setting="auto-night-start"]');
        if (nightStart) nightStart.value = state.autoNight.nightStart;
        const dayStart = panel.querySelector('[data-setting="auto-day-start"]');
        if (dayStart) dayStart.value = state.autoNight.dayStart;
        const nightTheme = panel.querySelector('[data-setting="auto-night-theme"]');
        if (nightTheme) nightTheme.value = state.autoNight.nightTheme;
        const dayTheme = panel.querySelector('[data-setting="auto-day-theme"]');
        if (dayTheme) dayTheme.value = state.autoNight.dayTheme;
        const nudge = panel.querySelector('.mcms-nudge-value');
        if (nudge) nudge.textContent = `X ${state.nudge.x} / Y ${state.nudge.y}`;
        renderProfiles();
        renderOperationalPanels();
    }

    function ensureUi() {
        const mapEl = getLargestLeafletMap();
        createPanel();
        if (mapEl) {
            createControl(mapEl);
            const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
            if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay, mapEl);
        }
        return Boolean(document.getElementById(SCRIPT.panelId));
    }

    function mutationBelongsToToolkit(mutation) {
        const target = mutation.target;
        const toolkitTarget = Boolean(
            target &&
            target.nodeType === 1 &&
            (
                target.id === SCRIPT.controlId ||
                target.id === SCRIPT.panelId ||
                target.id === SCRIPT.toastId ||
                target.id === SCRIPT.payoutFlashId ||
                target.id === SCRIPT.criticalDrawerId ||
                target.id === SCRIPT.missionInspectorId ||
                target.closest?.(`#${SCRIPT.controlId}`) ||
                target.closest?.(`#${SCRIPT.panelId}`) ||
                target.closest?.(`#${SCRIPT.toastId}`) ||
                target.closest?.(`#${SCRIPT.payoutFlashId}`) ||
                target.closest?.(`#${SCRIPT.criticalDrawerId}`) ||
                target.closest?.(`#${SCRIPT.missionInspectorId}`)
            )
        );
        if (toolkitTarget) return true;

        if (mutation.type === 'attributes' && mutation.attributeName === 'class' && target?.classList) {
            for (const className of target.classList) {
                if (String(className).startsWith('mcms-')) return true;
            }
        }

        const toolkitSelector = '.mcms-alliance-credit-icon, .mcms-alliance-credit-badge, .mcms-mission-age-icon, .mcms-mission-age-badge, .mcms-unit-commitment-icon, .mcms-unit-commitment-badge, .mcms-transport-watcher-icon, .mcms-transport-watcher-badge, .mcms-resource-gap-icon, .mcms-resource-gap-badge, .mcms-stuck-mission-icon, .mcms-stuck-mission-badge, .mcms-mission-spawn-label-icon, .mcms-mission-spawn-label';
        let elementCount = 0;
        for (const collection of [mutation.addedNodes, mutation.removedNodes]) {
            if (!collection?.length) continue;
            for (const node of collection) {
                if (!node || node.nodeType !== 1) continue;
                elementCount += 1;
                if (!(node.matches?.(toolkitSelector) || node.querySelector?.(toolkitSelector))) return false;
            }
        }
        return elementCount > 0;
    }

    function mutationAddsLeafletMarkerIcon(mutation) {
        if (!mutation || mutation.type !== 'childList' || !mutation.addedNodes?.length) return false;

        for (const node of mutation.addedNodes) {
            if (!node || node.nodeType !== 1) continue;
            if (node.matches?.('.mcms-alliance-credit-icon, .mcms-mission-age-icon, .mcms-unit-commitment-icon, .mcms-transport-watcher-icon, .mcms-resource-gap-icon, .mcms-stuck-mission-icon, .mcms-mission-spawn-label-icon') || node.querySelector?.('.mcms-alliance-credit-icon, .mcms-mission-age-icon, .mcms-unit-commitment-icon, .mcms-transport-watcher-icon, .mcms-resource-gap-icon, .mcms-stuck-mission-icon, .mcms-mission-spawn-label-icon')) continue;
            if (node.matches?.('.leaflet-marker-icon')) return true;
            if (node.querySelector?.('.leaflet-marker-icon')) return true;
        }

        return false;
    }

    function mutationTouchesSelector(mutation, selector) {
        const target = mutation?.target;
        if (target?.nodeType === 1 && (target.matches?.(selector) || target.closest?.(selector))) return true;
        for (const collection of [mutation?.addedNodes, mutation?.removedNodes]) {
            if (!collection?.length) continue;
            for (const node of collection) {
                if (!node || node.nodeType !== 1) continue;
                if (node.matches?.(selector) || node.querySelector?.(selector)) return true;
            }
        }
        return false;
    }

    function mutationRemovesToolkitUi(mutation) {
        for (const node of mutation?.removedNodes || []) {
            if (!node || node.nodeType !== 1) continue;
            if ([SCRIPT.panelId, SCRIPT.controlId].includes(node.id)) return true;
            if (node.querySelector?.(`#${SCRIPT.panelId}, #${SCRIPT.controlId}`)) return true;
        }
        return false;
    }

    function mutationAffectsMissionData(mutation) {
        return mutationTouchesSelector(mutation, '.leaflet-marker-pane, .leaflet-marker-icon, [id^="mission_"], #missions, #mission_list, .missionSideBarEntry, .mission-side-bar-entry, [data-mission-id]');
    }

    function mutationAffectsMapLayout(mutation) {
        const target = mutation?.target;
        if (target?.nodeType === 1) {
            if (target.matches?.('#map, #map_outer, .leaflet-container')) return true;
            if (target.closest?.('.navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
        }
        for (const collection of [mutation?.addedNodes, mutation?.removedNodes]) {
            if (!collection?.length) continue;
            for (const node of collection) {
                if (!node || node.nodeType !== 1) continue;
                if (node.matches?.('#map, #map_outer, .leaflet-container, .navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
                if (node.querySelector?.('#map, #map_outer, .leaflet-container, .navbar, .modal, .modal-backdrop, .dropdown-menu, .popover, [role="dialog"]')) return true;
            }
        }
        return false;
    }


    function boot() {
        if (runtime.destroyed) return;
        applyRootAttributes();
        createCleanExit();
        scanInlineMissionMarkerData();
        installMissionMarkerAddHook();
        installRadioMessageHook();
        runtimeSetTimeout(() => { if (vehicleDataNeeded()) refreshPersonalVehicleData(true); }, 900);
        lastObservedCredits = readCurrentCreditTotal();
        installCreditsUpdateHook();
        observeCreditValue();
        createCriticalDrawer();
        createMissionInspector();
        if (missionSnapshotsNeeded()) refreshMissionSnapshots();
        if (state.missionSpawn.enabled) primeMissionSpawnDetector();
        if (state.stuckDetector.enabled) scheduleStuckMissionRefresh(0);
        if (state.transportWatcher) scheduleTransportWatcherRefresh(0);
        if (state.resourceGap.enabled) scheduleResourceGapRefresh(0);
        scheduleOperationalPanelsRender(0);

        let attempts = 0;
        const bootTimer = runtimeSetInterval(() => {
            attempts += 1;
            installMissionMarkerAddHook();
            installRadioMessageHook();
            installCreditsUpdateHook();
            observeCreditValue();
            const ready = ensureUi();
            if (ready) {
                if (!state.visibility.vehicles) synchroniseVehicleMarkerClasses();
                if (!state.visibility.buildings) synchronisePersonalBuildingVisibility();
            }
            if (ready || attempts >= 90) runtimeClearInterval(bootTimer);
        }, 350);

        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
            const externalMutations = mutations.filter(mutation => !mutationBelongsToToolkit(mutation));
            if (!externalMutations.length) return;

            const addedLeafletMarker = externalMutations.some(mutationAddsLeafletMarkerIcon);
            const missionChanged = addedLeafletMarker || externalMutations.some(mutationAffectsMissionData);
            const layoutChanged = externalMutations.some(mutationAffectsMapLayout);
            const toolkitUiRemoved = externalMutations.some(mutationRemovesToolkitUi);
            if (!missionChanged && !layoutChanged && !toolkitUiRemoved) return;

            if (addedLeafletMarker) {
                invalidateMarkerRegistryCaches('all');
                if (!state.visibility.vehicles || state.markerFocus) {
                    synchroniseVehicleMarkerClasses();
                    runtimeSetTimeout(() => {
                        if (state.markerFocus || !state.visibility.vehicles) synchroniseVehicleMarkerClasses();
                    }, 0);
                }
                if (!state.visibility.buildings) {
                    synchronisePersonalBuildingMarkerClasses();
                    runtimeSetTimeout(() => synchronisePersonalBuildingVisibility(), 0);
                    runtimeSetTimeout(() => synchronisePersonalBuildingVisibility(), 180);
                }
            }
            if (dragState) return;

            runtimeClearTimeout(mutationTimer);
            mutationTimer = runtimeSetTimeout(() => {
                if (dragState || document.hidden || runtime.destroyed) return;
                const panelMissing = !document.getElementById(SCRIPT.panelId);
                const mapElement = getLargestLeafletMap();
                const controlMissing = Boolean(mapElement && !document.getElementById(SCRIPT.controlId));
                if (toolkitUiRemoved || panelMissing || controlMissing) ensureUi();
                if (layoutChanged) {
                    refreshSuppression();
                    fitControlToMap();
                    schedulePanelPosition(true, 50);
                }
                if (missionChanged) scheduleEnabledMapRefreshes({ includeSnapshots: true, positionPanel: false });
            }, DOM_REFRESH_DEBOUNCE_MS);
        }));

        observer.observe(document.body, { childList: true, subtree: true });

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
            applyRootAttributes();
            refreshTabletModeUi();
            scheduleTabletLayoutRefresh(20);
            const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
            if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay);
            if (dragState) return;
            refreshSuppression();
            fitControlToMap();
            schedulePanelPosition(true, 40);
            scheduleEnabledMapRefreshes({ includeSnapshots: false, positionPanel: false });
        });

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
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
            scheduleOperationalPanelsRender(500);
        });

        runtimeSetInterval(() => {
            if (document.hidden || !vehicleDataNeeded()) return;
            installRadioMessageHook();
            refreshPersonalVehicleData(false);
        }, VEHICLE_API_REFRESH_MS);
        runtimeSetInterval(() => {
            if (!document.hidden) runAutoNight(false);
        }, 60 * 1000);
        runtimeSetInterval(() => {
            if (document.hidden) return;
            installMissionMarkerAddHook();
            installRadioMessageHook();
            installCreditsUpdateHook();
            observeCreditValue();
            if (state.allianceCredits) scheduleAllianceCreditRefresh();
            if (state.unitCommitment) scheduleUnitCommitmentRefresh();
            if (state.resourceGap.enabled) scheduleResourceGapRefresh();
            if (missionSnapshotsNeeded()) scheduleMissionSnapshotRefresh();
        }, FALLBACK_MISSION_REFRESH_MS);
        runtimeSetInterval(() => {
            if (document.hidden) return;
            if (state.missionAge) scheduleMissionAgeRefresh();
            if (state.stuckDetector.enabled) scheduleStuckMissionRefresh();
            refreshVisibleMissionInspector();
            scheduleOperationalPanelsRender(500);
        }, 60 * 1000);
        runtimeSetInterval(() => {
            if (!document.hidden && !state.visibility.buildings) synchronisePersonalBuildingVisibility();
        }, BUILDING_VISIBILITY_RECHECK_MS);
        runtimeListen(document, 'visibilitychange', () => {
            if (document.hidden) return;
            refreshSuppression();
            if (vehicleDataNeeded()) refreshPersonalVehicleData(false);
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: true });
        });
        runtimeSetTimeout(() => {
            if (document.hidden) return;
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
        }, 850);
        runtimeSetTimeout(() => scheduleOperationalPanelsRender(0, true), 1100);

        runtimeOnCleanup(() => {
            transportSweepRuntime.stopRequested = true;
            document.removeEventListener('mousemove', movePanelDrag, true);
            document.removeEventListener('mouseup', endPanelDrag, true);
            document.removeEventListener('touchmove', movePanelDrag, true);
            document.removeEventListener('touchend', endPanelDrag, true);
            document.removeEventListener('touchcancel', endPanelDrag, true);
            document.documentElement.style.cursor = '';
            if (document.body) document.body.style.userSelect = '';
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
            removeOldInstances();
            const root = document.documentElement;
            for (const attribute of ['data-mcms-ui-theme', 'data-mc-map-skin', 'data-mcms-clean', 'data-mcms-marker-focus', 'data-mcms-mission-pulse', 'data-mcms-road-priority', 'data-mcms-compact-dock', 'data-mcms-command-bar-open', 'data-mcms-device-layout', 'data-mcms-tablet-mode', 'data-mcms-tablet-active', 'data-mcms-tablet-orientation', 'data-mcms-mobile-mode', 'data-mcms-mobile-active', 'data-mcms-mobile-orientation', 'data-mcms-show-alliance-missions', 'data-mcms-show-my-missions', 'data-mcms-show-vehicles', 'data-mcms-show-buildings', 'data-mcms-critical-view']) root.removeAttribute(attribute);
        });

        runAutoNight(true);
    }

    if (document.readyState === 'loading') {
        runtimeListen(document, 'DOMContentLoaded', boot, { once: true });
    } else {
        boot();
    }
})();
