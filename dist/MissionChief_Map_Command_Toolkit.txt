// ==UserScript==
// @name         MissionChief Map Command Toolkit
// @namespace    https://github.com/Conroy1988/missionchief-map-command-toolkit
// @version      10.6.3
// @description  MissionChief operational map command centre.
// @author       Conroy1988
// @license      MIT
// @homepageURL  https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/
// @supportURL   https://github.com/Conroy1988/missionchief-toolkit-assets/issues
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
// @connect      raw.githubusercontent.com
// @connect      tkb-gaming.scot
// @run-at       document-start
// @downloadURL  https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/update/
// @updateURL    https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/metadata/
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
    const ALLIANCE_BUILDINGS_PATH_PATTERN = /\/(?:verband\/(?:gebauede|gebaeude|geb√§ude)|alliance(?:\/|_)(?:buildings|buildings_list))(?:\/|$)/iu;
    const ALLIANCE_BUILDINGS_STORAGE_KEY = 'mc_map_command_toolkit_state_v150';
    const ALLIANCE_BUILDINGS_SETTINGS_VAULT_KEY = 'mc_map_command_toolkit_settings_v1';
    const ALLIANCE_BUILDINGS_EARLY_STYLE_ID = 'mcms-alliance-buildings-map-early-style';
    const ALLIANCE_BUILDINGS_SUPPRESSED_LAYER = Symbol('mcmsAllianceBuildingsSuppressedLayer');
    const ALLIANCE_BUILDINGS_SUPPRESSED_MAP = Symbol('mcmsAllianceBuildingsSuppressedMap');
    const protectedAllianceLeafletLibraries = new Set();
    const allianceLeafletGuardRecords = new WeakMap();
    let allianceBuildingsEarlyCheckQueued = false;
    let allianceBuildingsContextWatcherInstalled = false;
    let allianceBuildingsSuppressionActive = false;
    let allianceBuildingsHadActiveContext = false;
    let allianceLeafletAssignmentRestore = null;
    let allianceSuppressedIcon = null;
    function decodedPathname(pathname = location.pathname) {
        const value = String(pathname || '');
        try { return decodeURIComponent(value); } catch (err) { return value; }
    }
    function isAllianceBuildingsPath(pathname = location.pathname) {
        return ALLIANCE_BUILDINGS_PATH_PATTERN.test(decodedPathname(pathname));
    }
    function isActiveAllianceContextElement(element) {
        if (!element?.isConnected) return false;
        if (element.hidden || element.getAttribute?.('aria-hidden') === 'true') return false;
        let current = element;
        for (let depth = 0; current && current !== document.documentElement && depth < 8; depth += 1, current = current.parentElement) {
        if (current.hidden || current.getAttribute?.('aria-hidden') === 'true') return false;
        try {
            const style = pageWindow.getComputedStyle?.(current);
            if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse') return false;
        } catch (err) {}
        }
        try {
        const rect = element.getBoundingClientRect?.();
        if (rect && (rect.width > 1 || rect.height > 1)) return true;
        if (element.getClientRects?.().length) return true;
        } catch (err) {}
        return isAllianceBuildingsPath();
    }
    function allianceBuildingsTables() {
        return Array.from(document.querySelectorAll?.('table') || []).filter(table => {
        if (!isActiveAllianceContextElement(table)) return false;
        const buildingLinks = table.querySelectorAll?.('a[href*="/buildings/"]')?.length || 0;
        if (buildingLinks < 3) return false;
        const trainingActions = table.querySelectorAll?.('a.btn-success[href*="/buildings/"], button.btn-success, input.btn-success')?.length || 0;
        const allianceNavigationLinks = document.querySelectorAll?.('a[href*="/verband/"], a[href*="/alliance/"]')?.length || 0;
        return trainingActions >= 1 || (allianceNavigationLinks >= 3 && buildingLinks >= 8);
        });
    }
    function hasAllianceBuildingsDomContext() {
        const explicitMaps = Array.from(document.querySelectorAll?.('#verband-gebauede-map, #verband-gebaeude-map, [id*="gebauede"][id*="map"], [id*="gebaeude"][id*="map"]') || []);
        if (explicitMaps.some(isActiveAllianceContextElement)) return true;
        return allianceBuildingsTables().length > 0;
    }
    function isAllianceBuildingsContext() {
        return isAllianceBuildingsPath() || hasAllianceBuildingsDomContext();
    }
    function resolveAllianceMapContainer(target) {
        if (typeof target === 'string') return document.getElementById?.(target) || null;
        return target?.nodeType === 1 ? target : null;
    }
    function isAllianceBuildingsMapTarget(target) {
        const container = resolveAllianceMapContainer(target);
        if (isAllianceBuildingsPath()) return true;
        if (!container) return false;
        if (['verband-gebauede-map', 'verband-gebaeude-map'].includes(container.id)) return true;
        if (/(?:gebauede|gebaeude)/i.test(container.id || '') && /map/i.test(container.id || '')) return true;
        const row = container.closest?.('.row') || container.parentElement?.parentElement;
        const table = row?.querySelector?.('table') || null;
        if (!table || !isActiveAllianceContextElement(table)) return false;
        const buildingLinks = table.querySelectorAll?.('a[href*="/buildings/"]')?.length || 0;
        const trainingActions = table.querySelectorAll?.('a.btn-success[href*="/buildings/"], button.btn-success, input.btn-success')?.length || 0;
        return buildingLinks >= 3 && trainingActions >= 1;
    }
    function readAllianceBuildingsMapPreferenceEarly() {
        const candidates = [];
        try { candidates.push(localStorage.getItem(ALLIANCE_BUILDINGS_STORAGE_KEY)); } catch (err) {}
        try {
        if (typeof GM_getValue === 'function') candidates.push(GM_getValue(ALLIANCE_BUILDINGS_SETTINGS_VAULT_KEY, null));
        } catch (err) {}
        for (const raw of candidates) {
        if (!raw) continue;
        try {
            const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
            const settings = Number(parsed?.schema) === 1 && parsed?.state && typeof parsed.state === 'object'
            ? parsed.state
            : parsed;
            if (Object.prototype.hasOwnProperty.call(settings || {}, 'allianceBuildingsMap')) {
            return settings.allianceBuildingsMap !== false;
            }
        } catch (err) {}
        }
        return true;
    }
    function installAllianceBuildingsEarlyStyle() {
        if (document.getElementById(ALLIANCE_BUILDINGS_EARLY_STYLE_ID)) return;
        const style = document.createElement('style');
        style.id = ALLIANCE_BUILDINGS_EARLY_STYLE_ID;
        style.textContent = `
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] #map,
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] #map_outer,
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] #verband-gebauede-map,
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] #verband-gebaeude-map,
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] [id*="gebauede"][id*="map"],
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] [id*="gebaeude"][id*="map"],
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] .leaflet-container {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] [data-mcms-alliance-map-column="true"] {
                display: none !important;
            }
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] [data-mcms-alliance-list-column="true"] {
                width: 100% !important;
                max-width: 100% !important;
                flex: 0 0 100% !important;
                float: none !important;
                margin-left: 0 !important;
                contain: layout style paint;
            }
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] table[data-mcms-alliance-courses-table="true"] {
                width: 100% !important;
                table-layout: fixed !important;
            }
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] table[data-mcms-alliance-courses-table="true"] th:first-child,
            html[data-mcms-alliance-buildings-page="true"][data-mcms-alliance-buildings-map="disabled"] table[data-mcms-alliance-courses-table="true"] td:first-child {
                display: none !important;
            }
        `;
        const parent = document.head || document.documentElement;
        if (parent) parent.appendChild(style);
        else document.addEventListener('readystatechange', () => (document.head || document.documentElement)?.appendChild(style), { once: true });
    }
    function createSuppressedAllianceLayer() {
        const layer = {
        [ALLIANCE_BUILDINGS_SUPPRESSED_LAYER]: true,
        addTo() { return this; },
        remove() { return this; },
        bindTooltip() { return this; },
        bindPopup() { return this; },
        openTooltip() { return this; },
        closeTooltip() { return this; },
        on() { return this; },
        off() { return this; },
        once() { return this; },
        setOpacity() { return this; },
        setZIndex() { return this; },
        bringToFront() { return this; },
        bringToBack() { return this; }
        };
        return layer;
    }
    function shouldSuppressAllianceFactory() {
        return !readAllianceBuildingsMapPreferenceEarly() && allianceBuildingsSuppressionActive && isAllianceBuildingsContext();
    }
    function protectAllianceBuildingsLeaflet(Library) {
        if (!Library || protectedAllianceLeafletLibraries.has(Library)) return;
        if (!Library.Map?.prototype || typeof Library.marker !== 'function') return;
        const record = { factories: new Map(), factoryGuards: new Map(), mapInitialize: null, mapInitializeGuard: null, mapAddLayer: null, mapAddLayerGuard: null };
        allianceLeafletGuardRecords.set(Library, record);
        protectedAllianceLeafletLibraries.add(Library);
        const guardFactory = (factoryName, strategy = 'tag') => {
        const original = Library[factoryName];
        if (typeof original !== 'function') return;
        record.factories.set(factoryName, original);
        const guarded = function (...args) {
            if (shouldSuppressAllianceFactory()) {
                if (strategy === 'noop') return createSuppressedAllianceLayer();
                if (strategy === 'icon') {
                    allianceSuppressedIcon ||= { options: { ...(args[0] || {}) }, __mcmsAllianceSuppressedIcon: true };
                    return allianceSuppressedIcon;
                }
            }
            const layer = original.apply(this, args);
            if (shouldSuppressAllianceFactory() && layer) {
                try { layer[ALLIANCE_BUILDINGS_SUPPRESSED_LAYER] = true; } catch (err) {}
                if (strategy === 'marker') {
                    try { layer.bindTooltip = function () { return this; }; } catch (err) {}
                    try { layer.bindPopup = function () { return this; }; } catch (err) {}
                    try { layer.on = function () { return this; }; } catch (err) {}
                    try { layer.once = function () { return this; }; } catch (err) {}
                }
            }
            return layer;
        };
        try { Object.assign(guarded, original); } catch (err) {}
        try { Object.setPrototypeOf(guarded, Object.getPrototypeOf(original)); } catch (err) {}
        record.factoryGuards.set(factoryName, guarded);
        Library[factoryName] = guarded;
        };
        guardFactory('icon', 'icon');
        guardFactory('marker', 'marker');
        guardFactory('circleMarker', 'marker');
        guardFactory('tileLayer', 'noop');
        guardFactory('imageOverlay', 'noop');
        const mapPrototype = Library.Map.prototype;
        const originalInitialize = mapPrototype.initialize;
        if (typeof originalInitialize === 'function') {
        record.mapInitialize = originalInitialize;
        const guardedInitialize = function (target, options) {
            const result = originalInitialize.call(this, target, options);
            if (!readAllianceBuildingsMapPreferenceEarly() && isAllianceBuildingsMapTarget(target)) {
                try { this[ALLIANCE_BUILDINGS_SUPPRESSED_MAP] = true; } catch (err) {}
                allianceBuildingsSuppressionActive = true;
                allianceBuildingsHadActiveContext = true;
                document.documentElement?.setAttribute('data-mcms-alliance-buildings-page', 'true');
                document.documentElement?.setAttribute('data-mcms-alliance-buildings-map', 'disabled');
                installAllianceBuildingsEarlyStyle();
                queueAllianceBuildingsEarlyCheck();
            }
            return result;
        };
        record.mapInitializeGuard = guardedInitialize;
        mapPrototype.initialize = guardedInitialize;
        }
        const originalAddLayer = mapPrototype.addLayer;
        if (typeof originalAddLayer === 'function') {
        record.mapAddLayer = originalAddLayer;
        const guardedAddLayer = function (layer) {
            if (this?.[ALLIANCE_BUILDINGS_SUPPRESSED_MAP] || layer?.[ALLIANCE_BUILDINGS_SUPPRESSED_LAYER]) return this;
            return originalAddLayer.call(this, layer);
        };
        record.mapAddLayerGuard = guardedAddLayer;
        mapPrototype.addLayer = guardedAddLayer;
        }
    }
    function restoreAllianceBuildingsLeafletGuards() {
        for (const Library of Array.from(protectedAllianceLeafletLibraries)) {
        const record = allianceLeafletGuardRecords.get(Library);
        if (!record) continue;
        for (const [factoryName, original] of record.factories) {
            try {
                if (Library[factoryName] === record.factoryGuards.get(factoryName)) Library[factoryName] = original;
            } catch (err) {}
        }
        try {
            if (record.mapInitialize && Library.Map.prototype.initialize === record.mapInitializeGuard) Library.Map.prototype.initialize = record.mapInitialize;
            if (record.mapAddLayer && Library.Map.prototype.addLayer === record.mapAddLayerGuard) Library.Map.prototype.addLayer = record.mapAddLayer;
        } catch (err) {}
        protectedAllianceLeafletLibraries.delete(Library);
        }
        allianceSuppressedIcon = null;
    }
    function installAllianceBuildingsLeafletAssignmentGuard() {
        try { protectAllianceBuildingsLeaflet(pageWindow.L); } catch (err) {}
        if (allianceLeafletAssignmentRestore) return;
        const descriptor = Object.getOwnPropertyDescriptor(pageWindow, 'L');
        if (descriptor && !descriptor.configurable) return;
        let leafletValue;
        try { leafletValue = pageWindow.L; } catch (err) { leafletValue = undefined; }
        try {
        Object.defineProperty(pageWindow, 'L', {
            configurable: true,
            enumerable: descriptor?.enumerable ?? true,
            get() { return leafletValue; },
            set(value) {
                leafletValue = value;
                protectAllianceBuildingsLeaflet(value);
            }
        });
        allianceLeafletAssignmentRestore = () => {
            try {
                Object.defineProperty(pageWindow, 'L', {
                    configurable: true,
                    enumerable: descriptor?.enumerable ?? true,
                    writable: true,
                    value: leafletValue
                });
            } catch (err) {}
            allianceLeafletAssignmentRestore = null;
        };
        } catch (err) {}
    }
    function findAllianceBuildingsMapElementEarly() {
        const candidates = Array.from(document.querySelectorAll?.('#verband-gebauede-map, #verband-gebaeude-map, #map, #map_outer .leaflet-container, [id*="gebauede"][id*="map"], [id*="gebaeude"][id*="map"], .leaflet-container') || []);
        return candidates.find(element => {
        if (!element) return false;
        if (['verband-gebauede-map', 'verband-gebaeude-map'].includes(element.id)) return true;
        const row = element.closest?.('.row') || element.parentElement?.parentElement;
        const nearbyTable = row?.querySelector?.('table');
        return Boolean(isAllianceBuildingsPath() || (nearbyTable && isActiveAllianceContextElement(nearbyTable) && nearbyTable.querySelector('a[href*="/buildings/"]')));
        }) || null;
    }
    function markAllianceBuildingsColumnsEarly(mapElement) {
        if (!mapElement) return;
        let mapColumn = mapElement;
        for (let depth = 0; mapColumn && mapColumn !== document.body && depth < 8; depth += 1, mapColumn = mapColumn.parentElement) {
        if (/\bcol-(?:xs|sm|md|lg|xl|xxl)-\d+\b/u.test(String(mapColumn.className || ''))) break;
        }
        if (!mapColumn || mapColumn === document.body) mapColumn = mapElement.parentElement;
        mapColumn?.setAttribute?.('data-mcms-alliance-map-column', 'true');
        const row = mapColumn?.parentElement;
        const listColumn = Array.from(row?.children || []).find(child => child !== mapColumn && child.querySelector?.('table'));
        listColumn?.setAttribute?.('data-mcms-alliance-list-column', 'true');
    }
    function optimiseAllianceBuildingsCourseTableEarly() {
        for (const table of allianceBuildingsTables()) {
        table.setAttribute('data-mcms-alliance-courses-table', 'true');
        table.querySelectorAll('img').forEach(image => {
            image.loading = 'lazy';
            image.decoding = 'async';
            try { image.fetchPriority = 'low'; } catch (err) {}
        });
        }
    }
    function repairVisibleMissionChiefMapAfterAllianceExit() {
        if (!allianceBuildingsHadActiveContext) return;
        allianceBuildingsHadActiveContext = false;
        for (const delay of [0, 120, 500, 1100]) {
        pageWindow.setTimeout(() => {
            if (isAllianceBuildingsContext()) return;
            try {
                cachedMap = null;
                cachedMapElement = null;
                mapDiscoveryLastAttempt = 0;
            } catch (err) {}
            try {
                const map = typeof findLeafletMapInstance === 'function' ? findLeafletMapInstance(false) : null;
                map?.invalidateSize?.({ pan: false, animate: false });
            } catch (err) {}
            try { pageWindow.dispatchEvent(new Event('resize')); } catch (err) {}
        }, delay);
        }
    }
    function clearAllianceBuildingsEarlyContext({ restoreLeaflet = true } = {}) {
        const root = document.documentElement;
        const hadContext = allianceBuildingsSuppressionActive || root?.getAttribute('data-mcms-alliance-buildings-page') === 'true';
        allianceBuildingsSuppressionActive = false;
        root?.removeAttribute('data-mcms-alliance-buildings-page');
        document.querySelectorAll?.('[data-mcms-alliance-map-column], [data-mcms-alliance-list-column]')?.forEach(element => {
        element.removeAttribute('data-mcms-alliance-map-column');
        element.removeAttribute('data-mcms-alliance-list-column');
        });
        document.querySelectorAll?.('[data-mcms-alliance-courses-table]')?.forEach(table => table.removeAttribute('data-mcms-alliance-courses-table'));
        if (restoreLeaflet) {
        restoreAllianceBuildingsLeafletGuards();
        allianceLeafletAssignmentRestore?.();
        }
        if (hadContext) repairVisibleMissionChiefMapAfterAllianceExit();
    }
    function applyAllianceBuildingsEarlySuppression() {
        if (readAllianceBuildingsMapPreferenceEarly()) {
        clearAllianceBuildingsEarlyContext();
        return false;
        }
        if (!isAllianceBuildingsContext()) {
        clearAllianceBuildingsEarlyContext();
        return false;
        }
        allianceBuildingsSuppressionActive = true;
        allianceBuildingsHadActiveContext = true;
        installAllianceBuildingsLeafletAssignmentGuard();
        document.documentElement?.setAttribute('data-mcms-alliance-buildings-page', 'true');
        document.documentElement?.setAttribute('data-mcms-alliance-buildings-map', 'disabled');
        installAllianceBuildingsEarlyStyle();
        markAllianceBuildingsColumnsEarly(findAllianceBuildingsMapElementEarly());
        optimiseAllianceBuildingsCourseTableEarly();
        return true;
    }
    function queueAllianceBuildingsEarlyCheck() {
        if (allianceBuildingsEarlyCheckQueued) return;
        allianceBuildingsEarlyCheckQueued = true;
        queueMicrotask(() => {
        allianceBuildingsEarlyCheckQueued = false;
        applyAllianceBuildingsEarlySuppression();
        });
    }
    function installAllianceBuildingsContextWatcherEarly() {
        if (allianceBuildingsContextWatcherInstalled) return;
        allianceBuildingsContextWatcherInstalled = true;
        const armForAllianceNavigation = event => {
        const anchor = event.target?.closest?.('a[href]');
        if (!anchor) return;
        let path;
        try { path = new URL(anchor.href, location.href).pathname; } catch (err) { path = anchor.getAttribute('href') || ''; }
        if (!isAllianceBuildingsPath(path)) return;
        installAllianceBuildingsEarlyStyle();
        installAllianceBuildingsLeafletAssignmentGuard();
        };
        document.addEventListener('click', armForAllianceNavigation, true);
        const observer = new MutationObserver(mutations => {
        const relevant = mutations.some(mutation => [mutation.addedNodes, mutation.removedNodes].some(collection => Array.from(collection || []).some(node => {
            if (!node || node.nodeType !== 1) return false;
            return node.matches?.('#map, #map_outer, #verband-gebauede-map, #verband-gebaeude-map, .leaflet-container, table, [class*="col-"]') ||
                node.querySelector?.('#map, #map_outer, #verband-gebauede-map, #verband-gebaeude-map, .leaflet-container, table a[href*="/buildings/"]');
        })));
        if (relevant) queueAllianceBuildingsEarlyCheck();
        });
        const begin = () => {
        const root = document.documentElement;
        if (root) observer.observe(root, { childList: true, subtree: true });
        };
        if (document.documentElement) begin();
        else document.addEventListener('readystatechange', begin, { once: true });
        pageWindow.addEventListener?.('popstate', queueAllianceBuildingsEarlyCheck);
        pageWindow.addEventListener?.('hashchange', queueAllianceBuildingsEarlyCheck);
        pageWindow.addEventListener?.('pageshow', queueAllianceBuildingsEarlyCheck);
        pageWindow.addEventListener?.('load', queueAllianceBuildingsEarlyCheck, { once: true });
        applyAllianceBuildingsEarlySuppression();
    }
    const earlyAllianceBuildingsPage = isAllianceBuildingsPath();
    const earlyAllianceBuildingsMapEnabled = readAllianceBuildingsMapPreferenceEarly();
    if (earlyAllianceBuildingsPage) {
        document.documentElement?.setAttribute('data-mcms-alliance-buildings-page', 'true');
        document.documentElement?.setAttribute('data-mcms-alliance-buildings-map', earlyAllianceBuildingsMapEnabled ? 'enabled' : 'disabled');
    }
    if (!earlyAllianceBuildingsMapEnabled) {
        installAllianceBuildingsEarlyStyle();
        installAllianceBuildingsLeafletAssignmentGuard();
        installAllianceBuildingsContextWatcherEarly();
    }


    const SCRIPT = {
        name: 'MissionChief Map Command Toolkit',
        version: '10.6.3',
        author: 'Conroy1988',
        controlId: 'mc-map-command-toolkit-control',
        panelId: 'mc-map-command-toolkit-panel',
        toastId: 'mc-map-command-toolkit-toast',
        payoutFlashId: 'mc-map-command-toolkit-payout-flash',
        vehicleStatusId: 'mc-map-command-toolkit-vehicle-status',
        pressureBoardId: 'mc-map-command-toolkit-pressure-board',
        majorIncidentFeedId: 'mc-map-command-toolkit-major-incident-feed',
        transportSweepHudId: 'mc-map-command-toolkit-transport-sweep-hud',
        customVehicleBadgeStyleId: 'mcms-custom-vehicle-badge-style',
        helpCenterId: 'mc-map-command-toolkit-help-center',
        commandPaletteId: 'mc-map-command-toolkit-command-palette',
        commandExperienceModalId: 'mc-map-command-toolkit-command-experience',
        mapMeasureHudId: 'mc-map-command-toolkit-map-measure',
        contextMenuId: 'mc-map-command-toolkit-context-menu',
        vehicleFollowId: 'mc-map-command-toolkit-vehicle-follow',
        quickWheelId: 'mc-map-command-toolkit-quick-wheel',
        personalisationStyleId: 'mc-map-command-personalisation-style',
        fullscreenExitId: 'mc-map-command-toolkit-fullscreen-exit',
        cleanExitId: 'mcms-clean-exit',
        styleId: 'mc-map-command-toolkit-style-v4146',
        oldControlId: 'mc-map-command-skins-control',
        oldGeoLabelLayerId: 'mcms-persistent-label-layer',
        storageState: 'mc_map_command_toolkit_state_v150',
        settingsVaultState: 'mc_map_command_toolkit_settings_v1',
        settingsRecoveryState: 'mc_map_command_toolkit_settings_recovery_v1',
        settingsSnapshotsState: 'mc_map_command_toolkit_settings_snapshots_v1',
        payoutHistoryState: 'mc_map_command_toolkit_payout_history_v200',
        sessionPerformanceState: 'mc_map_command_toolkit_session_v200',
        missionProgressState: 'mc_map_command_toolkit_mission_progress_v250',
        transportSweepReportState: 'mc_map_command_toolkit_transport_sweep_report_v1',
        discordWebhookState: 'mc_map_command_toolkit_discord_webhook_v300',
        discordLastReportState: 'mc_map_command_toolkit_discord_last_report_v310',
        financeVaultState: 'mc_map_command_toolkit_finance_vault_v450',
        financeVaultCredentialState: 'mc_map_command_toolkit_finance_vault_credential_v450',
        financeRulesCacheState: 'mc_map_command_toolkit_finance_rules_v450',
        financePolicyCacheState: 'mc_map_command_toolkit_finance_policy_v460',
        ukKnowledgeCacheState: 'mc_map_command_toolkit_uk_knowledge_v1',
        analyticsState: 'mc_map_command_toolkit_analytics_v1',
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

    const RELEASE_BRIEFING = Object.freeze({
        version: "10.6.3",
        title: "iOS Patient Transport Sweep hydration repair",
        highlights: Object.freeze([
            "Fixes iPhone scans discovering up to 80 current patient missions but discarding the entire queue when mobile mission HTML omits the desktop missing-requirements block.",
            "Accepts a positively owned alliance mission only when its same-origin page contains concrete FMS-5 ambulance or patient-vehicle evidence.",
            "Shows hydration progress every ten missions and bounds each mobile mission request so the scan cannot remain silently stalled.",
            "Preserves refreshed ownership verification, personal-vehicle exclusion and the requirement for MissionChief's visible native discharge or cancel control before any action.",
            "Extends the real-mobile regression with a missing-requirements fixture while retaining desktop parity, persistent reports and exact-once Discord delivery."
        ])
    });
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
    function runtimeUnlisten(target, type, listener, options) {
        if (!target) return 0;
        let removed = 0;
        for (let index = runtime.listeners.length - 1; index >= 0; index -= 1) {
        const record = runtime.listeners[index];
        if (record.target !== target || record.type !== type || record.listener !== listener || record.options !== options) continue;
        try { record.target.removeEventListener(record.type, record.listener, record.options); } catch (err) {}
        runtime.listeners.splice(index, 1);
        removed += 1;
        }
        return removed;
    }
    function runtimeUnlistenTarget(target, includeDescendants = false) {
        if (!target) return 0;
        let removed = 0;
        for (let index = runtime.listeners.length - 1; index >= 0; index -= 1) {
        const record = runtime.listeners[index];
        let matches = record.target === target;
        if (!matches && includeDescendants && typeof target.contains === 'function') {
            try { matches = target.contains(record.target); } catch (err) {}
        }
        if (!matches) continue;
        try { record.target.removeEventListener(record.type, record.listener, record.options); } catch (err) {}
        runtime.listeners.splice(index, 1);
        removed += 1;
        }
        return removed;
    }
    function runtimeDocumentConnected(doc) {
        if (!doc) return false;
        if (doc === document) return true;
        try {
        const frame = doc.defaultView?.frameElement || null;
        if (!frame?.isConnected) return false;
        return !frame.contentDocument || frame.contentDocument === doc;
        } catch (err) {
        return false;
        }
    }
    function runtimePruneDisconnectedListeners() {
        let removed = 0;
        for (let index = runtime.listeners.length - 1; index >= 0; index -= 1) {
        const record = runtime.listeners[index];
        const target = record.target;
        if (target === pageWindow || target === document) continue;
        let connected = true;
        if (target?.nodeType === 9) connected = runtimeDocumentConnected(target);
        else if (typeof target?.isConnected === 'boolean') connected = target.isConnected;
        if (connected) continue;
        try { target?.removeEventListener?.(record.type, record.listener, record.options); } catch (err) {}
        runtime.listeners.splice(index, 1);
        removed += 1;
        }
        return removed;
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
    function runtimeUntrackObserver(observer, disconnect = true) {
        if (!observer) return;
        if (disconnect) {
        try { observer.disconnect(); } catch (err) {}
        }
        runtime.observers.delete(observer);
    }
    const runtimeTasks = new Map();
    let runtimeTaskTimer = null;
    function runtimeWakeTaskScheduler(delay = 0) {
        runtimeClearTimeout(runtimeTaskTimer);
        runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(0, Number(delay) || 0));
    }
    function runtimeRegisterTask(name, intervalMs, callback, options = {}) {
        if (!name || typeof callback !== 'function') return null;
        const interval = Math.max(250, Number(intervalMs) || 1000);
        const initialDelay = Math.max(0, Number(options.initialDelayMs ?? interval) || 0);
        runtimeTasks.set(String(name), {
        name: String(name),
        intervalMs: interval,
        intervalResolver: typeof options.intervalResolver === 'function' ? options.intervalResolver : null,
        economyIntervalMs: Math.max(interval, Number(options.economyIntervalMs) || interval),
        economyIntervalResolver: typeof options.economyIntervalResolver === 'function' ? options.economyIntervalResolver : null,
        callback,
        runWhenHidden: Boolean(options.runWhenHidden),
        nextRun: Date.now() + initialDelay,
        running: false
        });
        runtimeWakeTaskScheduler(0);
        return String(name);
    }


    function runtimeTaskInterval(task) {
        if (!task) return 1000;
        let resolved = task.intervalMs;
        if (typeof task.intervalResolver === 'function') {
        try { resolved = Number(task.intervalResolver(task)) || resolved; } catch (err) {}
        }
        resolved = Math.max(task.intervalMs, resolved);
        if (!state?.economyMode) return resolved;
        let economyResolved = Math.max(resolved, task.economyIntervalMs || resolved);
        if (typeof task.economyIntervalResolver === 'function') {
        try { economyResolved = Number(task.economyIntervalResolver(task)) || economyResolved; } catch (err) {}
        }
        return Math.max(resolved, economyResolved);
    }
    function runtimeRescheduleTasks(runSoon = false) {
        const now = Date.now();
        for (const task of runtimeTasks.values()) task.nextRun = runSoon ? now : Math.min(task.nextRun, now + runtimeTaskInterval(task));
        runtimeWakeTaskScheduler(runSoon ? 0 : 50);
    }
    function runtimeRunScheduledTasks() {
        runtimeTaskTimer = null;
        if (runtime.destroyed || !runtimeTasks.size) return;
        const now = Date.now();
        const hidden = Boolean(document.hidden);
        let nextDelay = hidden ? 5 * 60 * 1000 : 60000;
        for (const task of runtimeTasks.values()) {
        const dueIn = task.nextRun - now;
        if (dueIn > 0) {
            nextDelay = Math.min(nextDelay, dueIn);
            continue;
        }
        if (hidden && !task.runWhenHidden) {
            const deferredInterval = Math.max(60 * 1000, runtimeTaskInterval(task));
            task.nextRun = now + deferredInterval;
            nextDelay = Math.min(nextDelay, deferredInterval);
            continue;
        }
        const effectiveInterval = runtimeTaskInterval(task);
        task.nextRun = now + effectiveInterval;
        nextDelay = Math.min(nextDelay, effectiveInterval);
        if (task.running) continue;
        task.running = true;
        try {
            const result = task.callback();
            if (result && typeof result.then === 'function') {
                Promise.resolve(result)
                    .catch(err => console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err))
                    .finally(() => { task.running = false; });
            } else {
                task.running = false;
            }
        } catch (err) {
            task.running = false;
            console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err);
        }
        }
        runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(50, Math.min(hidden ? 5 * 60 * 1000 : 60000, nextDelay)));
    }
    function runtimeOnCleanup(callback) {
        if (typeof callback === 'function') runtime.cleanupCallbacks.push(callback);
        return callback;
    }


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

    function startupClock() {
        try { return Number(pageWindow.performance?.now?.()) || Date.now(); }
        catch (err) { return Date.now(); }
    }

    function recordStartupMetric(name, startedAt, extra = {}) {
        const finishedAt = startupClock();
        const elapsedMs = Math.max(0, finishedAt - Number(startedAt || finishedAt));
        const metrics = pageWindow.__MCMS_STARTUP_METRICS__ || {};
        metrics.version = SCRIPT.version;
        metrics[name] = Math.round(elapsedMs * 10) / 10;
        Object.assign(metrics, extra);
        pageWindow.__MCMS_STARTUP_METRICS__ = metrics;
        return elapsedMs;
    }

    const TOOLKIT_ANALYTICS_ENDPOINT = 'https://tkb-gaming.scot/api/toolkit-analytics.php';
    const TOOLKIT_ANALYTICS_FEATURES = new Set([
        'markerFocus', 'missionPulse', 'roadPriority', 'coverage', 'allianceMissions',
        'myMissions', 'vehicles', 'buildings', 'missionValue', 'customVehicleBadges',
        'missionLockAudio', 'payoutFlash', 'payoutSound', 'stuckDetector', 'missionSpawn',
        'clean', 'shortcuts', 'compactDock', 'quickWheel', 'autoLoadAllVehicles',
        'allianceBuildingsMapBlocker', 'majorIncidentFeed', 'allianceCredits',
        'missionAge', 'unitCommitment', 'transportWatcher', 'resourceGap',
        'commandPalette', 'pressureBoard', 'patientTransportSweep', 'unitLocator',
        'financialIntelligence', 'toolkitDoctor', 'safeMode', 'sessionCleanup',
        'mapMeasure'
    ]);
    const toolkitAnalyticsSessionSignals = new Set();

    function toolkitAnalyticsAllowed() {
        try {
        return pageWindow.navigator?.globalPrivacyControl !== true &&
            pageWindow.navigator?.doNotTrack !== '1' &&
            pageWindow.doNotTrack !== '1';
        } catch (err) { return false; }
    }

    function toolkitAnalyticsDevice() {
        const width = Math.max(0, Number(pageWindow.innerWidth) || Number(document.documentElement?.clientWidth) || 0);
        if (width <= 760) return 'mobile';
        if (width <= 1180 || pageWindow.matchMedia?.('(pointer: coarse)')?.matches) return 'tablet';
        return 'desktop';
    }

    function toolkitAnalyticsRoute() {
        const path = String(location.pathname || '').toLowerCase();
        if (/^\/(?:$|missions\/?$)/u.test(path)) return 'map';
        if (path.startsWith('/missions/')) return 'mission';
        if (path.includes('/alliance') || path.includes('/verband')) return 'alliance';
        if (path.includes('/buildings') || path.includes('/gebauede') || path.includes('/gebaeude')) return 'buildings';
        if (path.includes('/credits')) return 'credits';
        return 'other';
    }

    function toolkitAnalyticsPerformance(elapsedMs) {
        const value = Math.max(0, Number(elapsedMs) || 0);
        if (value < 750) return 'fast';
        if (value < 2000) return 'normal';
        if (value < 5000) return 'slow';
        return 'very_slow';
    }

    function toolkitAnalyticsSend(event, dimensions = {}) {
        if (!toolkitAnalyticsAllowed() || runtime.destroyed) return false;
        const allowedEvents = new Set(['telemetry_enrolled', 'install_confirmed', 'update_confirmed', 'active_daily', 'active_7d', 'active_30d', 'core_ready', 'feature_toggle', 'feature_use', 'runtime_error']);
        if (!allowedEvents.has(event)) return false;
        const payload = new URLSearchParams({ event, version: SCRIPT.version });
        for (const key of ['previousVersion', 'device', 'route', 'feature', 'performance', 'error']) {
        const value = String(dimensions[key] || '');
        if (value) payload.set(key, value);
        }
        try {
        void runtimeFetch(TOOLKIT_ANALYTICS_ENDPOINT, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: payload.toString(),
            credentials: 'omit',
            referrerPolicy: 'no-referrer'
        }).catch(() => {});
        return true;
        } catch (err) { return false; }
    }

    function toolkitAnalyticsReadState() {
        const raw = gmGetValueSafe(SCRIPT.analyticsState, null);
        if (!raw) return null;
        try {
        const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
        if (!parsed || Number(parsed.schema) !== 1) return null;
        return parsed;
        } catch (err) { return null; }
    }

    function toolkitAnalyticsConfirmLifecycle(coreReadyMs) {
        if (!toolkitAnalyticsAllowed()) return false;
        const now = Date.now();
        const day = new Date(now).toISOString().slice(0, 10);
        const week = String(Math.floor(now / (7 * 86400000)));
        const month = String(Math.floor(now / (30 * 86400000)));
        const previous = toolkitAnalyticsReadState();
        const next = {
        schema: 1,
        lastVersion: SCRIPT.version,
        lastDay: day,
        lastWeek: week,
        lastMonth: month,
        lastCoreReadyDay: day
        };
        if (!gmSetValueSafe(SCRIPT.analyticsState, JSON.stringify(next))) return false;

        if (!previous) {
        toolkitAnalyticsSend(toolkitFreshInstallAtLoad ? 'install_confirmed' : 'telemetry_enrolled');
        } else if (String(previous.lastVersion || '') !== SCRIPT.version) {
        toolkitAnalyticsSend('update_confirmed', { previousVersion: String(previous.lastVersion || '') });
        }
        const activity = { device: toolkitAnalyticsDevice(), route: toolkitAnalyticsRoute() };
        if (previous?.lastDay !== day) toolkitAnalyticsSend('active_daily', activity);
        if (previous?.lastWeek !== week) toolkitAnalyticsSend('active_7d', activity);
        if (previous?.lastMonth !== month) toolkitAnalyticsSend('active_30d', activity);
        if (previous?.lastCoreReadyDay !== day) toolkitAnalyticsSend('core_ready', { performance: toolkitAnalyticsPerformance(coreReadyMs) });
        return true;
    }

    function toolkitAnalyticsRecordFeature(feature, event = 'feature_use') {
        const safeFeature = String(feature || '');
        const safeEvent = event === 'feature_toggle' ? event : 'feature_use';
        const signal = `${safeEvent}:${safeFeature}`;
        if (!TOOLKIT_ANALYTICS_FEATURES.has(safeFeature) || toolkitAnalyticsSessionSignals.has(signal)) return false;
        toolkitAnalyticsSessionSignals.add(signal);
        return toolkitAnalyticsSend(safeEvent, { feature: safeFeature });
    }

    function toolkitAnalyticsRecordError(error) {
        const safeError = ['boot_integration', 'operational_startup'].includes(error) ? error : '';
        const signal = `runtime_error:${safeError}`;
        if (!safeError || toolkitAnalyticsSessionSignals.has(signal)) return false;
        toolkitAnalyticsSessionSignals.add(signal);
        return toolkitAnalyticsSend('runtime_error', { error: safeError });
    }

    function runtimeFetch(input, init = {}) {
        if (runtime.destroyed) return Promise.reject(new Error('Toolkit runtime stopped.'));
        const { timeoutMs: rawTimeoutMs, ...requestInit } = init || {};
        const timeoutMs = Math.max(0, Number(rawTimeoutMs) || 0);
        const Controller = pageWindow.AbortController || globalThis.AbortController;
        const controller = typeof Controller === 'function' ? new Controller() : null;
        if (controller) runtime.fetchControllers.add(controller);
        const fetchFunction = pageWindow.fetch || globalThis.fetch;
        if (typeof fetchFunction !== 'function') {
        if (controller) runtime.fetchControllers.delete(controller);
        return Promise.reject(new Error('Browser fetch is unavailable.'));
        }
        const options = controller ? { ...requestInit, signal: controller.signal } : requestInit;
        const timeoutId = controller && timeoutMs ? runtimeSetTimeout(() => controller.abort(), timeoutMs) : null;
        const cleanup = () => {
        if (timeoutId !== null) runtimeClearTimeout(timeoutId);
        if (controller) runtime.fetchControllers.delete(controller);
        };
        try {
        return Promise.resolve(fetchFunction.call(pageWindow, input, options)).finally(cleanup);
        } catch (err) {
        cleanup();
        return Promise.reject(err);
        }
    }

    runtimeOnCleanup(() => {
        runtimeTasks.clear();
        runtimeClearTimeout(runtimeTaskTimer);
        runtimeTaskTimer = null;
    });

    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4100__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V3130__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V3121__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V380__ = true;
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
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V411__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V420__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4130__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4131__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4132__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4133__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4134__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4135__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4136__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4137__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4138__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4139__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4140__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4141__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4142__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4143__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4144__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V450__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V410__ = true;
    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V400__ = true;
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

    const HELP_CENTER = Object.freeze({
        guideVersion: '9.3.1',
        rawUrl: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/help/index.html',
        sourceUrl: 'https://github.com/Conroy1988/missionchief-toolkit-assets/blob/main/help/index.html',
        requestTimeoutMs: 15000
    });

    const THEME_ASSETS = Object.freeze({
        bond007Logo: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/007-logo.svg',
        bond007CommandSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/mi6-command-seal.svg',
        bond007Gunbarrel: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/gunbarrel-reticle.svg',
        bond007DossierGrid: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/classified-dossier-grid.svg',
        bond007Agent: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/agent-silhouette.svg',
        bond007Portrait: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/payout/daniel-craig-007-portrait.png',
        bond007GoldDivider: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/ui/gold-divider.svg',
        bond007PayoutSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/payout/funds-authorised-seal.svg',
        umbrellaEmblem: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/umbrella-containment-emblem.svg',
        umbrellaContainmentBadge: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/containment-division-badge.svg',
        umbrellaFacilitySchematic: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/facility-schematic.svg',
        umbrellaSurveillanceTerminal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/surveillance-terminal.svg',
        umbrellaSpecimenVial: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/ui/specimen-vial.svg',
        umbrellaPayoutSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/payout/transfer-authorized-seal.svg',
        hyruleCrest: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/hyrule-command-crest.svg',
        hyruleEye: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/ancient-eye-rune.svg',
        hyruleEnergyRing: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/zonai-energy-ring.svg',
        hyruleSwordShield: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/master-sword-shield-silhouette.svg',
        hyruleMap: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/ui/parchment-command-map.svg',
        hyruleQuestSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/payout/quest-complete-seal.svg',
        hyruleRupeeBurst: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/payout/rupee-burst.svg',
        godfatherFamilySeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/ui/family-command-seal.svg',
        godfatherWaxSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/ui/wax-seal.svg',
        godfatherRose: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/ui/velvet-rose.svg',
        godfatherPinstripe: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/ui/pinstripe-panel.svg',
        godfatherWood: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/ui/polished-wood.svg',
        godfatherPayoutSeal: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/payout/offer-authorised-seal.svg'
    });

    const UI_THEMES = Object.freeze({
        mapCommand: Object.freeze({ label: 'Map Command', short: 'DEFAULT', icon: '‚ñ¶', description: 'The original operational command interface.' }),
        cyberpunk: Object.freeze({ label: 'Cyberpunk', short: 'NEON', icon: '‚ö°', description: 'Neon tactical interface with angular panels, signal animations and high-contrast controls.' }),
        fallout4: Object.freeze({ label: 'Fallout 4', short: 'PIP-BOY', icon: '‚ò¢', description: 'Retro-futurist Pip-Boy terminal interface with phosphor display effects and high-contrast Vault-Tec controls.' }),
        umbrella: Object.freeze({ label: 'Umbrella Containment', short: 'BSL-4', icon: '‚ò£', description: 'Corporate BSL-4 containment interface with original transparent artwork, classified facility schematics, surveillance graphics and protected operational states.' }),
        factorio: Object.freeze({ label: 'Factorio', short: 'AUTOMATION', icon: '‚öô', description: 'Industrial automation interface with riveted steel panels, copper controls, hazard markings and factory-line motion.' }),
        bond007: Object.freeze({ label: '007 Intelligence', short: 'MI6', icon: '‚óâ', description: 'Complete Section 00 intelligence interface with original transparent MI6 artwork, gun-barrel targeting graphics, classified dossiers, champagne-gold controls and protected operational states.' }),
        hyrule: Object.freeze({ label: 'Hyrule Command', short: 'TRIFORCE', icon: '‚ñ≥', description: 'Fantasy command interface with parchment cartography, royal gold, ancient blue technology, green energy glyphs and transparent Hyrule-inspired artwork.' }),
        godfather: Object.freeze({ label: 'The Godfather', short: 'FAMILY', icon: '‚ú¶', description: 'Cinematic old-money command interface with original marionette, wax-seal, rose, pinstripe, leather, brass and polished-wood treatments.' })
    });
    const UI_THEME_ORDER = Object.freeze(['mapCommand', 'cyberpunk', 'fallout4', 'umbrella', 'factorio', 'bond007', 'hyrule', 'godfather']);

    const THEMES = {
        default: { full: 'Default', label: 'Default', short: 'STD', icon: '‚ñ°' },
        control: { full: 'Control Room', label: 'Control', short: 'CTL', icon: '‚óê' },
        incident: { full: 'Incident Focus', label: 'Incident', short: 'INC', icon: '‚ñ£' },
        roads: { full: 'Road Priority', label: 'Roads', short: 'RD', icon: '‚ïê' },
        urban: { full: 'Urban Grey', label: 'Urban', short: 'URB', icon: '‚ó´' },
        rural: { full: 'Rural Watch', label: 'Rural', short: 'RUR', icon: '‚óá' },
        nightshift: { full: 'Night Shift', label: 'Night', short: 'NIT', icon: '‚óÜ' },
        fireCommand: { full: 'Fire Command', label: 'Fire', short: 'FIRE', icon: 'üî•' },
        policeTactical: { full: 'Police Tactical', label: 'Police', short: 'POL', icon: '‚óÜ' },
        medicalControl: { full: 'Medical Control', label: 'Medical', short: 'MED', icon: '‚úö' },
        coastalCommand: { full: 'Coastal Command', label: 'Coastal', short: 'SEA', icon: '‚öì' }
    };

    const PAYOUT_TEMPLATES = {
        gta5: { label: 'GTA V Inspired', kicker: 'PAYOUT RECEIVED', titleCase: false, particleMode: 'none' },
        viceCity: { label: 'Vice City Inspired', kicker: 'PAYOUT RECEIVED', titleCase: true, particleMode: 'none' },
        badCompany: { label: 'Bad Company Inspired', kicker: 'PAYOUT RECEIVED', titleCase: false, particleMode: 'embers' },
        scarface: { label: 'Scarface Inspired', kicker: 'EMPIRE PAYOUT CONFIRMED', titleCase: false, particleMode: 'stars' },
        cyberpunk: { label: 'Cyberpunk Inspired', kicker: 'CREDIT TRANSFER CONFIRMED', titleCase: false, particleMode: 'glitch' },
        hellfire: { label: 'Hellfire Inspired', kicker: 'REWARD CLAIMED', titleCase: false, particleMode: 'embers' },
        wasteland: { label: 'Fallout Inspired', kicker: 'VAULT-TEC REWARD AUTHORIZED', titleCase: false, particleMode: 'dust' },
        factorio: { label: 'Factorio Industrial', kicker: 'AUTOMATION REWARD CONFIRMED', titleCase: false, particleMode: 'embers' },
        galactic: { label: 'Galactic Command', kicker: 'CREDIT ALLOCATION CONFIRMED', titleCase: false, particleMode: 'stars' },
        darkFantasy: { label: 'Dark Fantasy Inspired', kicker: 'REWARD BESTOWED', titleCase: true, particleMode: 'ash' },
        biohazard: { label: 'Umbrella Containment', kicker: 'CREDIT TRANSFER AUTHORIZED', titleCase: false, particleMode: 'none' },
        underworld: { label: 'Underworld Inspired', kicker: 'REWARD CLAIMED', titleCase: true, particleMode: 'embers' },
        pixelArcade: { label: 'Pixel Arcade Inspired', kicker: 'SCORE BONUS AWARDED', titleCase: false, particleMode: 'pixels' },
        jamesBond: { label: '007 Intelligence', kicker: 'MI6 FUNDS TRANSFER AUTHORISED', titleCase: false, particleMode: 'none' },
        hyruleQuest: { label: 'Hyrule Quest Reward', kicker: 'RUPEE REWARD ACQUIRED', titleCase: false, particleMode: 'rupees' },
        godfatherOffer: { label: 'The Godfather Offer', kicker: 'FAMILY ACCOUNT SETTLED', titleCase: true, particleMode: 'embers' }
    };

    const PAYOUT_TEMPLATE_ORDER = ['gta5', 'viceCity', 'badCompany', 'scarface', 'cyberpunk', 'hellfire', 'wasteland', 'factorio', 'jamesBond', 'hyruleQuest', 'godfatherOffer', 'galactic', 'darkFantasy', 'biohazard', 'underworld', 'pixelArcade'];

    // Hosted real-audio cues remain lazy-loaded through direct raw GitHub URLs.
    // Hosted payout cues are mapped by template and lazy-loaded only when played.
    const PAYOUT_MEDIA_SOUNDS = Object.freeze({
        viceCity: Object.freeze({
        label: 'GTA Vice City Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/assets/audio/payout-presets/gta-vice-city-cashout.mp3'
        }),
        badCompany: Object.freeze({
        label: 'BF Bad Company Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/assets/audio/payout-presets/bf-bad-company-cashout.mp3'
        }),
        scarface: Object.freeze({
        label: 'Scarface Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/assets/audio/payout-presets/scarface-cashout.mp3'
        }),
        cyberpunk: Object.freeze({
        label: 'Cyberpunk Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/cyberpunk/audio/cyberpunk-cashout.mp3'
        }),
        wasteland: Object.freeze({
        label: 'Fallout Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/fallout/audio/fallout-cashout.mp3'
        }),
        factorio: Object.freeze({
        label: 'Factorio Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/factorio/audio/factorio-cashout.mp3'
        }),
        biohazard: Object.freeze({
        label: 'Umbrella Containment Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/umbrella/audio/umbrella-containment-cashout.mp3'
        }),
        jamesBond: Object.freeze({
        label: '007 Intelligence Cashout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/james-bond/audio/james-bond-cashout.mp3'
        }),
        hyruleQuest: Object.freeze({
        label: 'Hyrule Quest Reward',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/hyrule/audio/hyrule-quest-reward.mp3'
        }),
        godfatherOffer: Object.freeze({
        label: 'The Godfather Flash Payout',
        url: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/audio/godfather-flash-payout.mp3?v=8.0.4'
        })
    });

    const CORE_THEME_ORDER = ['default', 'control', 'incident', 'roads', 'urban', 'rural', 'nightshift'];
    const SERVICE_THEME_ORDER = ['fireCommand', 'policeTactical', 'medicalControl', 'coastalCommand'];
    const THEME_ORDER = [...CORE_THEME_ORDER, ...SERVICE_THEME_ORDER];
    const PAYOUT_FLASH_MIN_MS = 2000;
    const PAYOUT_FLASH_MAX_MS = 30000;
    const PAYOUT_FLASH_STEP_MS = 1000;
    const PAYOUT_HISTORY_LIMIT = 40;
    const PAYOUT_MATCH_WINDOW_MS = 20000;
    const MISSION_AGE_LABEL_REFRESH_MS = 60 * 1000;
    const MISSION_AGE_LABEL_RETRY_MS = 2500;
    const STUCK_MIN_MINUTES = 5;
    const STUCK_MAX_MINUTES = 180;
    const MISSION_SPAWN_DURATION_MS = 2400;
    const MAP_PROFILE_LIMIT = 5;
    const MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS = [10000, 25000, 50000, 100000];
    const MAJOR_INCIDENT_FEED_MAX_ITEMS = 12;
    const MAJOR_INCIDENT_FEED_ROTATION_MS = 6500;
    const MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS = 9000;
    const MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS = 10;
    const MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS = 5;
    const UK_POSTCODE_PATTERN = /\b(?:GIR\s?0AA|(?:(?:[A-PR-UWYZ][0-9][0-9A-HJKSTUW]?|[A-PR-UWYZ][A-HK-Y][0-9][0-9ABEHMNPRV-Y]?)\s?[0-9][ABD-HJLNP-UW-Z]{2}))\b/iu;
    const VEHICLE_API_REFRESH_MS = 2 * 60 * 1000;
    const VEHICLE_CODE_STATUS_DEFINITIONS = Object.freeze([
        Object.freeze({ code: 1, label: 'Clear and Available' }),
        Object.freeze({ code: 2, label: 'Available at Station' }),
        Object.freeze({ code: 3, label: 'Responding' }),
        Object.freeze({ code: 4, label: 'On Scene' }),
        Object.freeze({ code: 5, label: 'Requesting Dispatch' }),
        Object.freeze({ code: 6, label: 'Out of Service' }),
        Object.freeze({ code: 7, label: 'Transporting' }),
        Object.freeze({ code: 9, label: 'Awaiting Pickup' })
    ]);
    const VEHICLE_CODE_STATUS_BY_CODE = new Map(VEHICLE_CODE_STATUS_DEFINITIONS.map(item => [item.code, item]));
    const VEHICLE_API_MIN_REFRESH_MS = 20 * 1000;
    const DOM_REFRESH_DEBOUNCE_MS = 260;
    const MAP_INTERACTION_SETTLE_MS = 90;
    const STARTUP_IDLE_TIMEOUT_MS = 2500;
    const STARTUP_OPERATIONAL_DELAY_MS = 700;
    const STARTUP_OBSERVER_DELAY_MS = 900;
    const STARTUP_SETTLE_WINDOW_MS = 8000;
    const STARTUP_MUTATION_DEBOUNCE_MS = 520;
    const BUILDING_VISIBILITY_RECHECK_MS = 4000;
    const MAP_DISCOVERY_RETRY_MS = 2000;
    const FALLBACK_MISSION_REFRESH_MS = 15 * 1000;
    const MISSION_PROGRESS_PAGE_REFRESH_MS = 30 * 1000;
    const MARKER_REGISTRY_CACHE_MS = 350;
    const PERSONAL_BUILDING_ID_CACHE_MS = 1200;
    const MAP_ELEMENT_CACHE_MS = 750;
    const MISSION_SNAPSHOT_REUSE_MS = 30000;
    const RUNTIME_CACHE_PRUNE_MS = 60 * 1000;
    const VEHICLE_API_ERROR_BACKOFF_MS = 60 * 1000;
    const MISSION_CACHE_RETENTION_MS = 10 * 60 * 1000;
    const RESOURCE_GAP_REFRESH_MS = 15 * 1000;
    const RESOURCE_GAP_RADIUS_OPTIONS = [10, 25, 50, 100];
    const TRANSPORT_SWEEP_DELAY_OPTIONS = [1500, 2000, 2500, 3000, 4000, 5000];
    const TRANSPORT_SWEEP_MAX_REQUESTS = 50;
    const TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION = 40;
    const TRANSPORT_SWEEP_MAX_MOBILE_DISCOVERY_MISSIONS = 80;
    const TRANSPORT_SWEEP_MOBILE_DISCOVERY_CONCURRENCY = 4;
    const TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS = 6500;
    const FINANCE_REPORT_COMPLEXITIES = Object.freeze(['simple', 'informative', 'wolf']);
    const FINANCE_REPORT_COMPLEXITY_RANK = Object.freeze({ simple: 0, informative: 1, wolf: 2 });
    const FINANCE_REPORT_COMPLEXITY_COPY = Object.freeze({
        simple: 'Key numbers only: money in, money out, net change and balances in one clear Discord card.',
        informative: 'A readable briefing with spending context, activity, leading categories, comparison and important alerts.',
        wolf: 'The complete financial intelligence audit: scorecard, risk, forecast, drawdown, classifications and archive evidence.'
    });
    function normaliseLoadedDiscordReportComplexity(discordReport = {}) {
        const requestedComplexity = String(discordReport?.complexity || '');
        if (FINANCE_REPORT_COMPLEXITIES.includes(requestedComplexity)) return requestedComplexity;
        const legacyReportMode = String(discordReport?.reportMode || '');
        if (legacyReportMode === 'fullAudit') return 'wolf';
        if (legacyReportMode === 'executive') return 'informative';
        return 'informative';
    }
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
        { id: 'wake', label: 'WKFD', name: 'Wakefield', lat: 53.6833, lng: -1.4977, zoom: 11 },
        { id: 'lond', label: 'LDN', name: 'London', lat: 51.5074, lng: -0.1278, zoom: 10 },
        { id: 'newc', label: 'NCL', name: 'Newcastle', lat: 54.9783, lng: -1.6178, zoom: 11 }
    ];
    const LEGACY_QUICK_PLACE_REPLACEMENTS = Object.freeze({
        glas: 'wake',
        dund: 'lond',
        stir: 'newc'
    });

    function normaliseQuickPins(loadedQuickPins, defaultQuickPins) {
        const loaded = loadedQuickPins && typeof loadedQuickPins === 'object' ? loadedQuickPins : {};
        const merged = { ...defaultQuickPins, ...loaded };
        for (const [legacyId, replacementId] of Object.entries(LEGACY_QUICK_PLACE_REPLACEMENTS)) {
        if (loaded[legacyId] === true && !Object.prototype.hasOwnProperty.call(loaded, replacementId)) {
            merged[replacementId] = true;
        }
        }
        return Object.fromEntries(QUICK_PLACES.map(place => [place.id, Boolean(merged[place.id])]));
    }


    const SMART_BOOKMARK_LABEL_MAX = 12;
    const SMART_BOOKMARK_SINGLE_WORD_MAX = 5;
    const SMART_BOOKMARK_WORDS = Object.freeze({
        edinburgh: 'EDIN', glasgow: 'GLA', london: 'LDN', manchester: 'MAN', liverpool: 'LIV',
        birmingham: 'BHM', newcastle: 'NCL', aberdeen: 'ABDN', dundee: 'DND', stirling: 'STIR',
        perth: 'PER', fife: 'FIFE', wakefield: 'WKFD', livingston: 'LVSTN', kirkcaldy: 'KRKDY',
        dunfermline: 'DNFRM', musselburgh: 'MSLBG', bonnyrigg: 'BNYRG', bathgate: 'BTHGT',
        dalkeith: 'DLKTH', leith: 'LEITH', paisley: 'PSLY', ayr: 'AYR', inverness: 'INV',
        centre: 'CTR', center: 'CTR', station: 'STN', headquarters: 'HQ', airport: 'AP',
        hospital: 'HOSP', fire: 'FIRE', police: 'POL', ambulance: 'AMB', training: 'TRG',
        control: 'CTRL', dispatch: 'DSP', operations: 'OPS', response: 'RSP', depot: 'DPT',
        district: 'DIST', central: 'CEN', north: 'N', south: 'S', east: 'E', west: 'W',
        northeast: 'NE', northwest: 'NW', southeast: 'SE', southwest: 'SW',
        northern: 'N', southern: 'S', eastern: 'E', western: 'W'
    });
    const SMART_BOOKMARK_STOP_WORDS = new Set(['the', 'of', 'and', 'at', 'in', 'for', 'on', 'to']);
    const SMART_BOOKMARK_OPTIONAL_WORDS = new Set(['city', 'county', 'area', 'region']);

    const SUPPRESSION_SELECTORS = [
        '.modal.show', '.modal.in', '.modal-backdrop', '.bootbox.modal',
        '[role="dialog"][aria-modal="true"]', '.popover.show', '.popover.in',
        '.dropdown-menu.show', '.dropdown.open > .dropdown-menu', '.ui-dialog',
        '.fancybox-overlay', '#fancybox-wrap'
    ];

    let settingsPersistenceMeta = { revision: 0, savedAt: 0, source: 'defaults' };
    const COMMAND_DENSITIES = Object.freeze(['spacious', 'standard', 'compact', 'command']);
    const QUICK_WHEEL_ACTIONS = Object.freeze({
        myMissions: Object.freeze({ label: 'My Missions', icon: '1' }),
        allianceMissions: Object.freeze({ label: 'Alliance', icon: '2' }),
        vehicles: Object.freeze({ label: 'Vehicles', icon: '3' }),
        buildings: Object.freeze({ label: 'Buildings', icon: '4' }),
        pressureBoard: Object.freeze({ label: 'Pressure', icon: 'P' }),
        fullscreen: Object.freeze({ label: 'Full Screen', icon: '‚õ∂' }),
        commandPalette: Object.freeze({ label: 'Palette', icon: '‚åï' }),
        personalisation: Object.freeze({ label: 'Personalise', icon: '‚ú¶' }),
        menu: Object.freeze({ label: 'Toolkit Menu', icon: 'M' }),
        markerFocus: Object.freeze({ label: 'Marker Focus', icon: 'F' }),
        roadPriority: Object.freeze({ label: 'Road Priority', icon: 'R' })
    });
    const DEFAULT_QUICK_WHEEL_ACTIONS = Object.freeze(['myMissions', 'allianceMissions', 'vehicles', 'buildings', 'pressureBoard', 'fullscreen']);
    const LAYOUT_DEVICE_KEYS = Object.freeze(['desktop', 'tablet', 'mobile']);
    const LAYOUT_CONTROL_GROUPS = Object.freeze({
        visibility: Object.freeze({ label: 'Visibility', controls: Object.freeze(['myMissions', 'allianceMissions', 'vehicles', 'buildings']) }),
        intelligence: Object.freeze({ label: 'Intelligence', controls: Object.freeze(['allianceCredits', 'missionAge', 'transportWatcher', 'unitCommitment', 'stuckDetector']) }),
        dashboard: Object.freeze({ label: 'Dashboard', controls: Object.freeze(['open-vehicle-status', 'open-pressure-board', 'open-command-palette', 'open-map-measure']) }),
        performance: Object.freeze({ label: 'Performance', controls: Object.freeze(['toggle-economy']) })
    });
    const DEFAULT_LAYOUT_GROUP_ORDER = Object.freeze(Object.keys(LAYOUT_CONTROL_GROUPS));
    const LAYOUT_CONTROL_LABELS = Object.freeze({
        myMissions: 'Personal Missions', allianceMissions: 'Alliance Missions', vehicles: 'Vehicles', buildings: 'Buildings',
        allianceCredits: 'Alliance Credits', missionAge: 'Mission Age', transportWatcher: 'Transport Watcher', unitCommitment: 'Unit Count', stuckDetector: 'Stuck Detector',
        'open-vehicle-status': 'Vehicle Codes', 'open-pressure-board': 'Pressure Board', 'open-command-palette': 'Command Palette', 'open-map-measure': 'Drawing', 'toggle-economy': 'Economy Mode'
    });
    const QUICK_WHEEL_SLOT_MIN = 4;
    const QUICK_WHEEL_SLOT_MAX = 8;
    const THEME_STUDIO_FORMAT = 'MissionChief Map Command Toolkit Theme';
    const THEME_STUDIO_SCHEMA = 1;
    const SETTINGS_SNAPSHOT_LIMIT = 5;
    const SETTINGS_SNAPSHOT_INTERVAL_MS = 6 * 60 * 60 * 1000;
    const NOTIFICATION_PRESETS = Object.freeze({
        radio: Object.freeze({ label: 'Command Radio', wave: 'square' }),
        soft: Object.freeze({ label: 'Soft Chime', wave: 'sine' }),
        classic: Object.freeze({ label: 'Classic Alert', wave: 'triangle' })
    });
    const NOTIFICATION_EVENT_META = Object.freeze({
        newMission: Object.freeze({ label: 'New mission', icon: '‚óé', title: 'New MissionChief incident' }),
        completion: Object.freeze({ label: 'Mission completed', icon: '‚úì', title: 'Mission completed' }),
        patient: Object.freeze({ label: 'Patient attention', icon: '‚úö', title: 'Patient transport requires attention' }),
        stuck: Object.freeze({ label: 'Stuck incident', icon: '!', title: 'Mission appears stuck' }),
        warning: Object.freeze({ label: 'Toolkit warning', icon: '‚ö†', title: 'Toolkit warning' })
    });
    const FEATURE_BEACON_KEYS = Object.freeze(['context', 'reskin', 'dock', 'input', 'safeMode', 'unitLocator', 'sessionCleanup']);
    const INPUT_COMMAND_META = Object.freeze({
        menu: Object.freeze({ label: 'Toolkit Menu', action: 'menu' }),
        palette: Object.freeze({ label: 'Command Palette', action: 'palette' }),
        myMissions: Object.freeze({ label: 'Personal Missions', action: 'myMissions' }),
        allianceMissions: Object.freeze({ label: 'Alliance Missions', action: 'allianceMissions' }),
        vehicles: Object.freeze({ label: 'Vehicles', action: 'vehicles' }),
        buildings: Object.freeze({ label: 'Buildings', action: 'buildings' }),
        allianceCredits: Object.freeze({ label: 'Alliance Credits', action: 'allianceCredits' }),
        missionAge: Object.freeze({ label: 'Mission Age', action: 'missionAge' }),
        transportWatcher: Object.freeze({ label: 'Transport Watcher', action: 'transportWatcher' }),
        unitCommitment: Object.freeze({ label: 'Unit Commitment', action: 'unitCommitment' }),
        vehicleCodes: Object.freeze({ label: 'Vehicle Codes', action: 'vehicleCodes' }),
        pressureBoard: Object.freeze({ label: 'Pressure Board', action: 'pressureBoard' }),
        clean: Object.freeze({ label: 'Clean Mode', action: 'clean' }),
        markerFocus: Object.freeze({ label: 'Marker Focus', action: 'markerFocus' }),
        missionPulse: Object.freeze({ label: 'Mission Pulse', action: 'missionPulse' }),
        roadPriority: Object.freeze({ label: 'Road Priority', action: 'roadPriority' }),
        safeMode: Object.freeze({ label: 'Toolkit Safe Mode', action: 'safeMode' })
    });
    const DEFAULT_HOTKEY_BINDINGS = Object.freeze({
        menu: 'M', palette: 'K', myMissions: '1', allianceMissions: '2', vehicles: '3', buildings: '4',
        allianceCredits: '5', missionAge: '6', transportWatcher: '7', unitCommitment: '8', vehicleCodes: 'V',
        pressureBoard: 'B', clean: 'C', markerFocus: 'F', missionPulse: 'P', roadPriority: 'R', safeMode: 'Shift+S'
    });
    const GESTURE_KEYS = Object.freeze(['swipeLeft', 'swipeRight', 'swipeUp', 'swipeDown']);
    const SETTINGS_TRANSFER = Object.freeze({
        format: 'MissionChief Map Command Toolkit Encrypted Settings Transfer',
        schema: 1,
        iterations: 310000,
        saltBytes: 16,
        ivBytes: 12,
        maximumFileBytes: 150 * 1024 * 1024
    });
    let state;
    let cachedMap = null;
    let cachedMapElement = null;
    let cachedMapElementCheckedAt = 0;
    let mapDiscoveryLastAttempt = 0;
    const markerRegistryCache = new Map();
    let markerRegistryRevision = 0;
    let missionRegistryRevision = 0;
    let vehicleRegistryRevision = 0;
    let buildingRegistryRevision = 0;
    let vehicleDataRevision = 0;
    let missionMarkerIndexCache = { revision: -1, registry: null, markers: [], byId: new Map() };
    let personalVehicleRecordsCache = { vehicleRevision: -1, markerRevision: -1, apiReady: false, createdAt: 0, records: [] };
    let cachedUserId = null;
    let cachedUserIdReadAt = 0;
    let personalBuildingIdsCache = { revision: -1, userId: null, createdAt: 0, values: new Set() };
    let buildingRecordIndexCache = { revision: -1, userId: null, recordsById: new Map(), allianceRecords: [] };
    let missionIconMarkerCache = new WeakMap();
    let panelPositionTimer = null;
    let coverageRenderSignature = '';
    let majorIncidentFeedRenderSignature = '';
    let majorIncidentFeedRenderTimer = null;
    let majorIncidentFeedLayoutFrame = null;
    let majorIncidentFeedLayoutTimer = null;
    let majorIncidentFeedMotionTimer = null;
    let majorIncidentFeedMotionRevision = 0;
    let majorIncidentFeedCurrentIndex = 0;
    let majorIncidentFeedManualPaused = false;
    let majorIncidentFeedInteractionPauseUntil = 0;
    let majorIncidentFeedExpanded = false;
    let majorIncidentFeedResizeObserver = null;
    let majorIncidentFeedObservedElement = null;
    const missionLifecycleLastSeen = new Map();
    let coverageGroup = null;
    let mutationTimer = null;
    let classifyTimer = null;
    let markerStateSyncTimer = null;
    let markerStateTrailingTimer = null;
    let coverageTimer = null;
    let fitTimer = null;
    let dragState = null;
    let suppressNextOutsideClick = false;
    const hiddenPersonalBuildingLayers = new Set();
    const personalBuildingLayerOpacity = new Map();
    let enforcingPersonalBuildingVisibility = false;
    const hiddenNativeAllianceBuildingLayers = new Set();
    const nativeAllianceBuildingLayerTargets = new WeakMap();
    let enforcingNativeAllianceBuildingVisibility = false;
    const economyHiddenVehicleLayers = new Set();
    const economyHiddenBuildingLayers = new Set();
    const economyLeafletOptionSnapshots = new Map();
    let economyLayerSyncTimer = null;
    let economyLayerEnforcement = false;
    let mapInteractionMoving = false;
    let mapInteractionSettling = false;
    let mapInteractionDeferredRefresh = false;
    let mapInteractionDeferredSnapshots = false;
    let mapInteractionDeferredDomMutation = false;
    let mapInteractionMarkerSyncNeeded = false;
    const mapInteractionDirtyScopes = new Set();
    let coverageCanvasRenderer = null;
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
    let bootStarted = false;
    let bootStartedAt = 0;
    let operationalStartupStarted = false;
    let operationalStartupComplete = false;
    let startupDataPassActive = false;
    let mainMutationObserver = null;
    let mainMutationObserverFallbackActive = false;
    let settingsPanelActivated = false;
    let opsRefreshTimer = null;
    let payoutFlashTimer = null;
    let toastFlashTimer = null;
    let payoutFlashFallbackInterval = null;
    let payoutFlashAnimations = [];
    let payoutAmountAnimationFrame = null;
    let payoutAudioContext = null;
    let notificationAudioContext = null;
    const notificationEventSeen = new Map();
    const notificationActiveEvents = new Set();
    let setupWizardDraft = null;
    let payoutMediaAudio = null;
    let payoutMediaTemplate = '';
    let payoutMediaGeneration = 0;
    let payoutEventCounter = 0;
    let creditsValueObserver = null;
    let observedCreditsElement = null;
    let lastObservedCredits = null;
    let inlineMissionDataScanned = false;
    let missionProgressPageFetchPromise = null;
    let missionProgressPageLastFetch = 0;
    let missionProgressPageLastSuccessAt = 0;
    let missionProgressPageMissionIds = new Set();
    let missionProgressPageMissionRecords = new Map();
    let missionSnapshotReady = false;
    let vehicleApiFetchPromise = null;
    let vehicleApiLastFetch = 0;
    let vehicleApiReady = false;
    let vehicleApiLastError = 0;
    let vehicleStatusLastUpdate = 0;
    let missionCommitmentIndexDirty = true;
    let operationalPanelsLastRender = 0;
    let missionLockOnMarker = null;
    let missionLockOnTravelOverlay = null;
    let missionLockOnTargetIcon = null;
    let missionLockOnTimer = null;
    let missionLockOnMoveEndMap = null;
    let missionLockOnMoveEndHandler = null;
    let missionLockOnToken = 0;
    let missionProgressSaveTimer = null;
    let followedVehicleId = '';
    let followedVehicleLabel = '';
    let followedVehicleMarker = null;
    let followedVehicleMoveHandler = null;
    let vehicleFollowRecentering = false;
    let unitLocatorQuery = '';
    let stuckMissionGroup = null;
    let stuckMissionTimer = null;
    let missionSpawnArmed = false;
    let missionSpawnPrimeTimer = null;
    const missionOverlayData = new Map();
    const missionOverlayVersions = new Map();
    const missionSnapshotCache = new Map();
    const missionPanelCache = new Map();
    let liveMissionSnapshots = new Map();
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
    let operationalPressureCache = { key: '', snapshot: null };
    let operationalPressureRefreshBusy = false;
    let operationalSitrepBusy = false;
    let operationalSitrepStatus = 'Operational SITREP ready for manual posting.';
    let operationalSitrepStatusTone = 'neutral';
    let ukKnowledgeLoadPromise = null;
    let ukKnowledgeActiveRequirement = null;
    let ukKnowledgeReturnFocus = null;
    const restoredTransportSweepReport = loadTransportSweepReport();
    const transportSweepRuntime = {
        running: false,
        stopRequested: false,
        scanPromise: null,
        queue: [],
        scannedAt: 0,
        currentMissionId: null,
        currentVehicleHref: '',
        cleared: 0,
        skipped: 0,
        errors: 0,
        processed: 0,
        confirmedReleaseKeys: new Set(),
        skippedPatientKeys: new Set(),
        confirmedDischargeDialogKeys: new Set(),
        pendingDischargeKey: '',
        rejectedOwn: 0,
        missionAnchorBaseline: new Set(),
        vehicleButtonBaseline: new Set(),
        ownVehicleIds: new Set(),
        missionWindowRoot: null,
        activeWindowRoot: null,
        ownedWindowLayers: new Set(),
        activeWindowCreatedLayer: false,
        lastCandidateStats: null,
        startedAt: 0,
        missionIndex: 0,
        missionTotal: 0,
        completedMissionCount: 0,
        missionsChecked: 0,
        currentItem: '',
        statusMessage: '',
        statusLevel: 'info',
        hudFinal: Boolean(restoredTransportSweepReport),
        lastReport: restoredTransportSweepReport,
        discordPosting: false,
        log: []
    };
    const personalVehicleApiCache = new Map();
    const missionCommitmentIndex = new Map();
    const payoutHistory = loadPayoutHistory();
    const sessionPerformance = loadSessionPerformance();
    let discordFinanceBusy = false;
    let discordFinanceStatus = 'Choose a period and report complexity, then generate and post the finance report.';
    let discordFinanceStatusTone = 'neutral';
    let financeVaultStatus = 'Local Financial Archive ready.';
    let financeVaultStatusTone = 'neutral';
    let financeRuleFeedStatus = 'Built-in financial intelligence active.';
    let financeRuleFeedStatusTone = 'neutral';
    let financeArchiveScanBusy = false;
    let financeArchiveScanCancelled = false;
    let financeRuleRefreshPromise = null;
    let financePolicyRefreshPromise = null;
    let tabletModeActive = false;
    let mobileModeActive = false;
    let activeDeviceLayout = 'desktop';
    let tabletLayoutTimer = null; let visualViewportRefreshGeneration = 0;
    let tabletDockResizeObserver = null;
    let tabletDockObservedMap = null;
    let desktopPanelResizeObserver = null;
    let desktopPanelObservedElements = new Set();
    let missionValueScanTimer = null;
    let missionValueFeatureInstalled = false;
    const missionValueDocumentObservers = new Map();
    const missionValueFrameListeners = new Map();
    const missionValueHostObservers = new Map();
    const missionValueRetryState = new WeakMap();
    let customVehicleBadgeScanTimer = null;
    let customVehicleBadgeRefreshPromise = null;
    let customVehicleBadgeFeatureInstalled = false;
    const customVehicleBadgeDocumentObservers = new Map();
    const customVehicleBadgeFrameListeners = new Map();
    const customVehicleClassificationCache = new Map();
    let customVehicleClassificationRevision = -1;
    let commandBarAnimationTimer = null;
    let commandBarAnimating = false;
    let helpGuideDocumentCache = '';
    let helpGuideLoadedAt = 0;
    let helpGuideLoadPromise = null;
    let helpCenterReturnFocus = null;
    let commandExperienceReturnFocus = null;
    let settingsTransferPending = null;
    let toolkitDoctorReport = null;
    let fullscreenMapTarget = null;
    let quickWheelRestoreDragging = false;
    let quickWheelReturnFocus = null;
    let autoHideDockRevealed = false;
    let dockGestureStart = null;
    let dockGestureConsumed = false;
    let contextCommandTarget = null;
    const mapMeasureRuntime = {
        active: false,
        mode: 'distance',
        map: null,
        group: null,
        draftGroup: null,
        renderer: null,
        points: [],
        objects: [],
        clickHandler: null,
        pointerStartHandler: null,
        pointerMoveHandler: null,
        pointerEndHandler: null,
        freehandDrawing: false,
        lastContainerPoint: null,
        draggingWasEnabled: null,
        colour: '#62d3ff',
        dashed: false,
        weight: 3,
        hud: null
    };
    runtime.cleanupCallbacks.push(() => {
        stopMapMeasure(false);
    });
    const COMMAND_SECTION_ORDER = Object.freeze(['map', 'missions', 'finance', 'locations', 'appearance', 'settings']);
    const COMMAND_SECTION_META = Object.freeze({
        map: Object.freeze({ label: 'Map', title: 'Map Controls', icon: '‚óé', description: 'Visibility, overlays and map tools' }),
        missions: Object.freeze({ label: 'Missions', title: 'Mission Operations', icon: '‚óÜ', description: 'Intelligence, resources and response tools' }),
        finance: Object.freeze({ label: 'Finance', title: 'Finance Command', icon: '¬£', description: 'Reports, payouts and financial archive' }),
        locations: Object.freeze({ label: 'Locations', title: 'Saved Locations', icon: '‚åÇ', description: 'Jumps, bookmarks and map profiles' }),
        appearance: Object.freeze({ label: 'Appearance', title: 'Appearance', icon: '‚óà', description: 'Interface themes and map skins' }),
        settings: Object.freeze({ label: 'Settings', title: 'Toolkit Settings', icon: '‚öô', description: 'Devices, controls and recovery' }),
    });
    const COMMAND_PALETTE_RESULT_LIMIT = 30;
    const COMMAND_PALETTE_KIND_META = Object.freeze({
        action: Object.freeze({ label: 'COMMAND', icon: '‚åò', priority: 7 }),
        mission: Object.freeze({ label: 'MISSION', icon: '‚óÜ', priority: 6 }),
        vehicle: Object.freeze({ label: 'VEHICLE', icon: '‚ñ∞', priority: 5 }),
        building: Object.freeze({ label: 'BUILDING', icon: '‚ñ¶', priority: 4 }),
        location: Object.freeze({ label: 'LOCATION', icon: '‚åñ', priority: 3 }),
        setting: Object.freeze({ label: 'SETTING', icon: '‚öô', priority: 2 })
    });
    const LEGACY_COMMAND_SECTION_MAP = Object.freeze({
        skins: 'appearance',
        tools: 'map',
        resources: 'missions',
        ops: 'missions',
        payouts: 'finance',
        discord: 'finance',
        places: 'locations',
        fleet: 'missions',
    });
    let commandSearchOpen = false;
    let commandSearchQuery = '';
    let commandPaletteEntries = [];
    let commandPaletteResults = [];
    let commandPaletteSelectedIndex = 0;
    let commandPaletteReturnFocus = null;
    state = loadState();
    const toolkitFreshInstallAtLoad = settingsPersistenceMeta.source === 'defaults';

    function defaultLayoutDeviceState(position = 'bl', device = 'desktop') {
        const safePosition = POSITIONS[position] ? position : 'bl';
        return {
        position: safePosition,
        groupOrder: [...DEFAULT_LAYOUT_GROUP_ORDER],
        controlOrder: Object.fromEntries(Object.entries(LAYOUT_CONTROL_GROUPS).map(([key, group]) => [key, [...group.controls]])),
        hiddenControls: [],
        panelPosition: null,
        panelWidth: device === 'desktop' ? 720 : device === 'tablet' ? 700 : 100,
        panelHeight: device === 'mobile' ? 88 : 82
        };
    }

    function defaultLayoutBuilderState(position = 'bl') {
        return {
        schema: 1,
        layouts: Object.fromEntries(LAYOUT_DEVICE_KEYS.map(device => [device, defaultLayoutDeviceState(position, device)]))
        };
    }

    function normaliseUniqueList(value, allowed, fallback) {
        const allowedSet = new Set(allowed);
        const result = [];
        for (const item of Array.isArray(value) ? value : fallback) {
        const key = String(item || '');
        if (allowedSet.has(key) && !result.includes(key)) result.push(key);
        }
        for (const key of fallback) if (!result.includes(key)) result.push(key);
        return result;
    }

    function normaliseLayoutBuilderState(value, legacyPosition = 'bl') {
        const fallback = defaultLayoutBuilderState(legacyPosition);
        const sourceLayouts = value?.layouts && typeof value.layouts === 'object' ? value.layouts : value;
        const layouts = {};
        for (const device of LAYOUT_DEVICE_KEYS) {
        const base = fallback.layouts[device];
        const source = sourceLayouts?.[device] && typeof sourceLayouts[device] === 'object' ? sourceLayouts[device] : {};
        const groupOrder = normaliseUniqueList(source.groupOrder, DEFAULT_LAYOUT_GROUP_ORDER, DEFAULT_LAYOUT_GROUP_ORDER);
        const controlOrder = {};
        for (const [groupKey, group] of Object.entries(LAYOUT_CONTROL_GROUPS)) {
            controlOrder[groupKey] = normaliseUniqueList(source.controlOrder?.[groupKey], group.controls, group.controls);
        }
        const allControls = Object.values(LAYOUT_CONTROL_GROUPS).flatMap(group => group.controls);
        const hiddenControls = normaliseUniqueList(source.hiddenControls, allControls, []).slice(0, allControls.length);
        layouts[device] = {
            position: POSITIONS[source.position] ? source.position : base.position,
            groupOrder,
            controlOrder,
            hiddenControls,
            panelPosition: source.panelPosition && Number.isFinite(Number(source.panelPosition.left)) && Number.isFinite(Number(source.panelPosition.top))
                ? { left: Number(source.panelPosition.left), top: Number(source.panelPosition.top) }
                : null,
            panelWidth: device === 'mobile' ? 100 : Math.round(clamp(source.panelWidth, device === 'tablet' ? 560 : 560, device === 'tablet' ? 900 : 960, base.panelWidth)),
            panelHeight: Math.round(clamp(source.panelHeight, device === 'mobile' ? 72 : 60, 96, base.panelHeight))
        };
        }
        return { schema: 1, layouts };
    }

    function activeLayoutPreferences(layout = activeDeviceLayout) {
        const key = LAYOUT_DEVICE_KEYS.includes(layout) ? layout : 'desktop';
        return state?.layoutBuilder?.layouts?.[key] || defaultLayoutDeviceState(state?.position || 'bl', key);
    }

    function defaultThemeStudioState() {
        return { enabled: false, name: 'Custom Command', accent: '#68cfff', surface: '#0b1620', text: '#eef8ff', radius: 14, opacity: 94, blur: 10 };
    }

    function normaliseThemeColour(value, fallback) {
        const colour = String(value || '').trim().toLowerCase();
        return /^#[0-9a-f]{6}$/u.test(colour) ? colour : fallback;
    }

    function normaliseThemeStudioState(value) {
        const base = defaultThemeStudioState();
        const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
        return {
        enabled: Boolean(source.enabled),
        name: String(source.name || base.name).trim().slice(0, 40) || base.name,
        accent: normaliseThemeColour(source.accent, base.accent),
        surface: normaliseThemeColour(source.surface, base.surface),
        text: normaliseThemeColour(source.text, base.text),
        radius: Math.round(clamp(source.radius, 4, 28, base.radius)),
        opacity: Math.round(clamp(source.opacity, 72, 100, base.opacity)),
        blur: Math.round(clamp(source.blur, 0, 24, base.blur))
        };
    }

    function defaultQuickWheelSlots() {
        return [
        ...DEFAULT_QUICK_WHEEL_ACTIONS.map(id => ({ kind: 'action', id })),
        { kind: 'palette', id: 'mission' },
        { kind: 'palette', id: 'vehicle' }
        ];
    }

    function normaliseQuickWheelSlot(value) {
        if (typeof value === 'string') {
        if (QUICK_WHEEL_ACTIONS[value]) return { kind: 'action', id: value };
        const [kind, id] = value.split(':', 2);
        return normaliseQuickWheelSlot({ kind, id });
        }
        if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
        const kind = String(value.kind || '');
        const id = String(value.id ?? '');
        if (kind === 'action' && QUICK_WHEEL_ACTIONS[id]) return { kind, id };
        if (kind === 'place' && QUICK_PLACES.some(place => place.id === id)) return { kind, id };
        if (kind === 'bookmark' && Number.isInteger(Number(id)) && Number(id) >= 0 && Number(id) < 5) return { kind, id: String(Number(id)) };
        if (kind === 'palette' && ['mission', 'vehicle', 'building'].includes(id)) return { kind, id };
        return null;
    }

    function defaultNotificationState() {
        return {
        enabled: false,
        browserEnabled: false,
        preset: 'radio',
        volume: 0.3,
        events: Object.fromEntries(Object.keys(NOTIFICATION_EVENT_META).map(key => [key, false]))
        };
    }

    function normaliseNotificationState(value) {
        const base = defaultNotificationState();
        const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
        return {
        enabled: Boolean(source.enabled),
        browserEnabled: Boolean(source.browserEnabled),
        preset: NOTIFICATION_PRESETS[source.preset] ? source.preset : base.preset,
        volume: clamp(source.volume, 0, 1, base.volume),
        events: Object.fromEntries(Object.keys(NOTIFICATION_EVENT_META).map(key => [key, Boolean(source.events?.[key])]))
        };
    }

    function normaliseHotkeyBinding(value, fallback = '') {
        const raw = String(value || '').trim().replace(/\s+/gu, '');
        if (!raw) return fallback;
        const parts = raw.split('+');
        const key = String(parts.pop() || '').toUpperCase();
        const modifiers = new Set(parts.map(part => part.toLowerCase()));
        if (!/^(?:[A-Z0-9]|F(?:[1-9]|1[0-2]))$/u.test(key) || parts.some(part => !['ctrl', 'alt', 'shift'].includes(part.toLowerCase()))) return fallback;
        return [modifiers.has('ctrl') ? 'Ctrl' : '', modifiers.has('alt') ? 'Alt' : '', modifiers.has('shift') ? 'Shift' : '', key].filter(Boolean).join('+');
    }

    function defaultInputStudioState() {
        return {
        hotkeys: { ...DEFAULT_HOTKEY_BINDINGS },
        gestures: { enabled: false, swipeLeft: 'palette', swipeRight: 'menu', swipeUp: 'pressureBoard', swipeDown: 'safeMode' }
        };
    }

    function normaliseInputStudioState(value) {
        const base = defaultInputStudioState();
        const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
        const used = new Set();
        const hotkeys = {};
        for (const command of Object.keys(INPUT_COMMAND_META)) {
        let binding = normaliseHotkeyBinding(source.hotkeys?.[command], base.hotkeys[command]);
        if (used.has(binding)) binding = base.hotkeys[command];
        if (used.has(binding)) binding = '';
        if (binding) used.add(binding);
        hotkeys[command] = binding;
        }
        const gestures = { enabled: Boolean(source.gestures?.enabled) };
        for (const key of GESTURE_KEYS) gestures[key] = INPUT_COMMAND_META[source.gestures?.[key]] ? source.gestures[key] : base.gestures[key];
        return { hotkeys, gestures };
    }

    function defaultAutoHideDockState() {
        return { enabled: false, edge: 'auto' };
    }

    function normaliseAutoHideDockState(value) {
        const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
        return { enabled: Boolean(source.enabled), edge: ['auto', 'horizontal', 'vertical'].includes(source.edge) ? source.edge : 'auto' };
    }

    function normaliseSafeModeState(value) {
        const source = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
        return {
        enabled: Boolean(source.enabled),
        since: Math.max(0, Number(source.since) || 0),
        previousTab: COMMAND_SECTION_ORDER.includes(source.previousTab) ? source.previousTab : 'map'
        };
    }

    function defaultState() {
        return {
        uiTheme: 'mapCommand',
        theme: getLegacyTheme(),
        position: getLegacyPosition(),
        activeTab: 'map',
        cleanMode: false,
        markerFocus: false,
        missionPulse: false,
        roadPriority: false,
        compactDock: false,
        commandBarOpen: true,
        economyMode: false,
        fullscreenMap: false,
        tabletMode: 'auto',
        mobileMode: 'auto',
        interfaceDensity: { desktop: 'standard', tablet: 'standard' },
        layoutBuilder: defaultLayoutBuilderState(getLegacyPosition()),
        themeStudio: defaultThemeStudioState(),
        missionChiefReskin: false,
        autoHideDock: defaultAutoHideDockState(),
        inputStudio: defaultInputStudioState(),
        safeMode: normaliseSafeModeState(null),
        quickWheel: { enabled: true, slotCount: 6, actions: [...DEFAULT_QUICK_WHEEL_ACTIONS], slots: defaultQuickWheelSlots() },
        setupWizard: { completed: false, schema: 1 },
        notifications: defaultNotificationState(),
        updateBriefing: { enabled: true, seenVersion: '', seenFeatures: [] },
        shortcuts: true,
        autoLoadAllVehicles: false,
        allianceBuildingsMap: true,
        majorIncidentFeed: { enabled: true, minimumCredits: 25000 },
        missionLockAudio: true,
        missionValue: true,
        customVehicleBadges: true,
        allianceCredits: false,
        allianceCreditMinimum: 0,
        missionAge: false,
        unitCommitment: false,
        transportWatcher: true,
        stuckDetector: { enabled: true, thresholdMin: 20 },
        missionSpawn: { enabled: true },
        resourceGap: { enabled: false, radiusMi: 25 },
        pressureBoard: { pinnedMissionIds: [] },
        transportSweep: { delayMs: 2000, maxPerRun: 25 },
        payoutFlash: { enabled: true, threshold: 10000, durationMs: 4000, template: 'gta5', soundEnabled: false, soundVolume: 0.35 },
        discordReport: { webhookName: 'MissionChief Finance', topCategories: 5, period: 'today', customStart: localIsoDate(new Date(Date.now() - 6 * 86400000)), customEnd: localIsoDate(), includeChart: true, includeComparison: true, complexity: 'informative', includeForecast: true, includeRisk: true },
        financialVault: { enabled: true, ruleFeedEnabled: true, retentionDays: 'all' },
        profiles: Array.from({ length: MAP_PROFILE_LIMIT }, () => null),
        nudge: { x: 0, y: 0 },
        panelPosition: null,
        visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true },
        quickPins: Object.fromEntries(QUICK_PLACES.map(place => [place.id, false])),
        coverage: { enabled: false, radiusMi: 10 },
        bookmarks: [null, null, null, null, null]
        };
    }

    function normaliseLoadedState(parsed, base = defaultState()) {
        const merged = {
        ...base,
        ...parsed,
        nudge: { ...base.nudge, ...(parsed.nudge || {}) },
        visibility: { ...base.visibility, ...(parsed.visibility || {}) },
        quickPins: normaliseQuickPins(parsed.quickPins, base.quickPins),
        coverage: { ...base.coverage, ...(parsed.coverage || {}) },
        stuckDetector: { ...base.stuckDetector, ...(parsed.stuckDetector || {}) },
        missionSpawn: { ...base.missionSpawn, ...(parsed.missionSpawn || {}) },
        resourceGap: { ...base.resourceGap, ...(parsed.resourceGap || {}) },
        pressureBoard: { ...base.pressureBoard, ...(parsed.pressureBoard || {}) },
        transportSweep: { ...base.transportSweep, ...(parsed.transportSweep || {}) },
        majorIncidentFeed: { ...base.majorIncidentFeed, ...(parsed.majorIncidentFeed || {}) },
        payoutFlash: { ...base.payoutFlash, ...(parsed.payoutFlash || {}) },
        discordReport: { ...base.discordReport, ...(parsed.discordReport || {}) },
        financialVault: { ...base.financialVault, ...(parsed.financialVault || {}) },
        interfaceDensity: { ...base.interfaceDensity, ...(parsed.interfaceDensity || {}) },
        quickWheel: { ...base.quickWheel, ...(parsed.quickWheel || {}) },
        layoutBuilder: normaliseLayoutBuilderState(parsed.layoutBuilder, parsed.position || base.position),
        themeStudio: normaliseThemeStudioState(parsed.themeStudio),
        autoHideDock: normaliseAutoHideDockState(parsed.autoHideDock),
        inputStudio: normaliseInputStudioState(parsed.inputStudio),
        safeMode: normaliseSafeModeState(parsed.safeMode),
        setupWizard: { ...base.setupWizard, ...(parsed.setupWizard || {}) },
        notifications: normaliseNotificationState(parsed.notifications),
        updateBriefing: { ...base.updateBriefing, ...(parsed.updateBriefing || {}) },
        profiles: Array.isArray(parsed.profiles) ? parsed.profiles.slice(0, MAP_PROFILE_LIMIT) : base.profiles,
        bookmarks: Array.isArray(parsed.bookmarks) ? parsed.bookmarks.slice(0, 5) : base.bookmarks
        };

        while (merged.bookmarks.length < 5) merged.bookmarks.push(null);
        while (merged.profiles.length < MAP_PROFILE_LIMIT) merged.profiles.push(null);

        merged.uiTheme = normaliseUiTheme(merged.uiTheme);
        merged.theme = normaliseTheme(merged.theme);
        merged.position = POSITIONS[merged.position] ? merged.position : 'bl';
        merged.activeTab = LEGACY_COMMAND_SECTION_MAP[merged.activeTab] || merged.activeTab;
        merged.activeTab = COMMAND_SECTION_ORDER.includes(merged.activeTab) ? merged.activeTab : 'map';
        delete merged.fleetFilter;
        delete merged.heatmap;
        delete merged.autoNight;
        merged.nudge.x = clamp(merged.nudge.x, -220, 220, 0);
        merged.nudge.y = clamp(merged.nudge.y, -220, 220, 0);
        merged.coverage.radiusMi = Number(merged.coverage.radiusMi) || 10;
        merged.allianceCreditMinimum = [0, 5000, 10000, 15000, 20000].includes(Number(merged.allianceCreditMinimum)) ? Number(merged.allianceCreditMinimum) : 0;
        merged.commandBarOpen = merged.commandBarOpen !== false;
        merged.economyMode = Boolean(merged.economyMode);
        merged.fullscreenMap = Boolean(merged.fullscreenMap);
        merged.autoLoadAllVehicles = merged.autoLoadAllVehicles === true;
        merged.customVehicleBadges = merged.customVehicleBadges !== false;
        merged.allianceBuildingsMap = merged.allianceBuildingsMap !== false;
        merged.majorIncidentFeed.enabled = merged.majorIncidentFeed.enabled !== false;
        merged.majorIncidentFeed.minimumCredits = MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS.includes(Number(merged.majorIncidentFeed.minimumCredits)) ? Number(merged.majorIncidentFeed.minimumCredits) : 25000;
        delete merged.missionAgeWatch;
        delete merged.missionInspector;
        merged.missionLockAudio = merged.missionLockAudio !== false;
        merged.missionValue = merged.missionValue !== false;
        delete merged.operationalWindow;
        delete merged.missionRequirements;
        merged.tabletMode = ['auto', 'on', 'off'].includes(String(merged.tabletMode)) ? String(merged.tabletMode) : 'auto';
        merged.mobileMode = ['auto', 'on', 'off'].includes(String(merged.mobileMode)) ? String(merged.mobileMode) : 'auto';
        merged.interfaceDensity.desktop = COMMAND_DENSITIES.includes(String(merged.interfaceDensity.desktop)) ? String(merged.interfaceDensity.desktop) : 'standard';
        merged.interfaceDensity.tablet = COMMAND_DENSITIES.includes(String(merged.interfaceDensity.tablet)) ? String(merged.interfaceDensity.tablet) : 'standard';
        merged.layoutBuilder = normaliseLayoutBuilderState(merged.layoutBuilder, merged.position);
        merged.themeStudio = normaliseThemeStudioState(merged.themeStudio);
        merged.missionChiefReskin = Boolean(merged.missionChiefReskin);
        delete merged.missionProgressRings;
        delete merged.allianceChatPreviews;
        merged.autoHideDock = normaliseAutoHideDockState(merged.autoHideDock);
        merged.inputStudio = normaliseInputStudioState(merged.inputStudio);
        merged.safeMode = normaliseSafeModeState(merged.safeMode);
        merged.quickWheel.enabled = merged.quickWheel.enabled !== false;
        merged.quickWheel.slotCount = Math.round(clamp(merged.quickWheel.slotCount, QUICK_WHEEL_SLOT_MIN, QUICK_WHEEL_SLOT_MAX, 6));
        const legacyWheelActions = Array.isArray(parsed?.quickWheel?.actions) ? parsed.quickWheel.actions : DEFAULT_QUICK_WHEEL_ACTIONS;
        const wheelSource = Array.isArray(parsed?.quickWheel?.slots) ? parsed.quickWheel.slots : legacyWheelActions;
        merged.quickWheel.slots = wheelSource.map(normaliseQuickWheelSlot).filter(Boolean).slice(0, QUICK_WHEEL_SLOT_MAX);
        for (const action of DEFAULT_QUICK_WHEEL_ACTIONS) {
        if (merged.quickWheel.slots.length >= QUICK_WHEEL_SLOT_MAX) break;
        if (!merged.quickWheel.slots.some(slot => slot.kind === 'action' && slot.id === action)) merged.quickWheel.slots.push({ kind: 'action', id: action });
        }
        while (merged.quickWheel.slots.length < QUICK_WHEEL_SLOT_MAX) merged.quickWheel.slots.push({ kind: 'action', id: 'commandPalette' });
        merged.quickWheel.actions = merged.quickWheel.slots.slice(0, 6).map(slot => slot.kind === 'action' && QUICK_WHEEL_ACTIONS[slot.id] ? slot.id : 'commandPalette');
        merged.setupWizard.schema = 1;
        merged.setupWizard.completed = parsed?.setupWizard && typeof parsed.setupWizard === 'object' ? Boolean(parsed.setupWizard.completed) : true;
        merged.notifications = normaliseNotificationState(merged.notifications);
        merged.updateBriefing.enabled = merged.updateBriefing.enabled !== false;
        merged.updateBriefing.seenVersion = String(merged.updateBriefing.seenVersion || '').slice(0, 32);
        merged.updateBriefing.seenFeatures = Array.from(new Set((Array.isArray(merged.updateBriefing.seenFeatures) ? merged.updateBriefing.seenFeatures : []).filter(key => FEATURE_BEACON_KEYS.includes(key))));
        merged.transportWatcher = merged.transportWatcher !== false;
        merged.stuckDetector.enabled = merged.stuckDetector.enabled !== false;
        merged.stuckDetector.thresholdMin = Math.round(clamp(merged.stuckDetector.thresholdMin, STUCK_MIN_MINUTES, STUCK_MAX_MINUTES, 20));
        merged.missionSpawn.enabled = merged.missionSpawn.enabled !== false;
        merged.resourceGap.enabled = Boolean(merged.resourceGap.enabled);
        merged.resourceGap.radiusMi = RESOURCE_GAP_RADIUS_OPTIONS.includes(Number(merged.resourceGap.radiusMi)) ? Number(merged.resourceGap.radiusMi) : 25;
        merged.pressureBoard.pinnedMissionIds = Array.from(new Set(
        (Array.isArray(merged.pressureBoard.pinnedMissionIds) ? merged.pressureBoard.pinnedMissionIds : [])
            .map(normaliseMissionId)
            .filter(value => value !== null)
            .map(String)
        )).slice(-12);
        merged.transportSweep.delayMs = TRANSPORT_SWEEP_DELAY_OPTIONS.includes(Number(merged.transportSweep.delayMs)) ? Number(merged.transportSweep.delayMs) : 2000;
        merged.transportSweep.maxPerRun = Math.round(clamp(merged.transportSweep.maxPerRun, 1, TRANSPORT_SWEEP_MAX_REQUESTS, 25));
        merged.payoutFlash.enabled = merged.payoutFlash.enabled !== false;
        merged.payoutFlash.threshold = Math.round(clamp(merged.payoutFlash.threshold, 1000, 1000000000, 10000));
        const loadedPayoutDuration = Number(parsed?.payoutFlash?.durationMs);
        merged.payoutFlash.durationMs = normalisePayoutFlashDuration(merged.payoutFlash.durationMs);
        if (merged.uiTheme === 'godfather' && (!Number.isFinite(loadedPayoutDuration) || loadedPayoutDuration === 4000)) {
        merged.payoutFlash.durationMs = 7000;
        }
        merged.payoutFlash.template = PAYOUT_TEMPLATES[merged.payoutFlash.template] ? merged.payoutFlash.template : 'gta5';
        merged.payoutFlash.soundEnabled = Boolean(merged.payoutFlash.soundEnabled);
        merged.payoutFlash.soundVolume = clamp(merged.payoutFlash.soundVolume, 0, 1, 0.35);
        merged.discordReport.webhookName = String(merged.discordReport.webhookName || 'MissionChief Finance').trim().slice(0, 80) || 'MissionChief Finance';
        merged.discordReport.topCategories = [3, 5, 8].includes(Number(merged.discordReport.topCategories)) ? Number(merged.discordReport.topCategories) : 5;
        merged.discordReport.period = ['today', 'yesterday', 'last24', 'last7', 'last30', 'last90', 'last180', 'last365', 'allAvailable', 'session', 'sinceLast', 'custom'].includes(merged.discordReport.period) ? merged.discordReport.period : 'today';
        merged.discordReport.customStart = /^\d{4}-\d{2}-\d{2}$/u.test(String(merged.discordReport.customStart || '')) ? String(merged.discordReport.customStart) : localIsoDate(new Date(Date.now() - 6 * 86400000));
        merged.discordReport.customEnd = /^\d{4}-\d{2}-\d{2}$/u.test(String(merged.discordReport.customEnd || '')) ? String(merged.discordReport.customEnd) : localIsoDate();
        merged.discordReport.includeChart = merged.discordReport.includeChart !== false;
        merged.discordReport.includeComparison = merged.discordReport.includeComparison !== false;
        merged.discordReport.complexity = normaliseLoadedDiscordReportComplexity(parsed?.discordReport);
        delete merged.discordReport.reportMode;
        merged.discordReport.includeForecast = merged.discordReport.includeForecast !== false;
        merged.discordReport.includeRisk = merged.discordReport.includeRisk !== false;
        merged.financialVault.enabled = merged.financialVault.enabled !== false;
        merged.financialVault.ruleFeedEnabled = merged.financialVault.ruleFeedEnabled !== false;
        merged.financialVault.retentionDays = String(merged.financialVault.retentionDays) === 'all'
        ? 'all'
        : ([90, 180, 365, 730, 1825].includes(Number(merged.financialVault.retentionDays)) ? Number(merged.financialVault.retentionDays) : 'all');
        delete merged.financialVault.autoSync;
        delete merged.financialVault.benchmarkOptIn;
        delete merged.financialVault.gatewayUrl;
        delete merged.discordReport.includeBenchmark;
        merged.bookmarks = merged.bookmarks.map(item => item ? {
        ...item,
        name: String(item.name || 'Bookmark').trim().slice(0, 80) || 'Bookmark',
        shortLabel: sanitiseBookmarkShortLabel(item.shortLabel || ''),
        pinned: Boolean(item.pinned)
        } : null);
        merged.profiles = merged.profiles.map(item => item && typeof item === 'object' ? item : null);

        if (!merged.panelPosition || !Number.isFinite(Number(merged.panelPosition.left)) || !Number.isFinite(Number(merged.panelPosition.top))) {
        merged.panelPosition = null;
        } else {
        merged.panelPosition = { left: Number(merged.panelPosition.left), top: Number(merged.panelPosition.top) };
        }
        if (!parsed.layoutBuilder && merged.panelPosition) {
        merged.layoutBuilder.layouts.desktop.panelPosition = { ...merged.panelPosition };
        merged.layoutBuilder.layouts.tablet.panelPosition = { ...merged.panelPosition };
        }

        delete merged.__mcmsPersistence;
        delete merged.requiresAttention;
        return merged;
    }

    function settingsLocalStorageGet(key) {
        try {
        return (pageWindow.localStorage || localStorage).getItem(key);
        } catch (err) {
        return null;
        }
    }

    function settingsLocalStorageSet(key, value) {
        try {
        (pageWindow.localStorage || localStorage).setItem(key, value);
        return true;
        } catch (err) {
        return false;
        }
    }

    function settingsLocalStorageRemove(key) {
        try {
        (pageWindow.localStorage || localStorage).removeItem(key);
        return true;
        } catch (err) {
        return false;
        }
    }

    function loadSettingsSnapshots() {
        const raw = gmGetValueSafe(SCRIPT.settingsSnapshotsState, '');
        try {
        const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
        if (!parsed || Number(parsed.schema) !== 1 || !Array.isArray(parsed.snapshots)) return [];
        return parsed.snapshots.filter(item => item && typeof item === 'object' && item.state && typeof item.state === 'object')
            .map(item => ({
            id: String(item.id || ''),
            createdAt: Math.max(0, Number(item.createdAt) || 0),
            version: String(item.version || ''),
            reason: String(item.reason || 'Recovery snapshot').slice(0, 80),
            state: item.state
            }))
            .sort((left, right) => right.createdAt - left.createdAt)
            .slice(0, SETTINGS_SNAPSHOT_LIMIT);
        } catch (err) {
        return [];
        }
    }

    function saveSettingsSnapshots(snapshots) {
        const safe = Array.isArray(snapshots) ? snapshots.slice(0, SETTINGS_SNAPSHOT_LIMIT) : [];
        return gmSetValueSafe(SCRIPT.settingsSnapshotsState, JSON.stringify({ schema: 1, snapshots: safe }));
    }

    function captureSettingsSnapshot(value, { reason = 'Automatic recovery snapshot', force = false } = {}) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
        const snapshots = loadSettingsSnapshots();
        const now = Date.now();
        if (!force && snapshots[0] && now - snapshots[0].createdAt < SETTINGS_SNAPSHOT_INTERVAL_MS) return false;
        const stateCopy = clonePlainData(value);
        delete stateCopy.__mcmsPersistence;
        const signature = JSON.stringify(stateCopy);
        if (snapshots[0] && JSON.stringify(snapshots[0].state) === signature) return false;
        snapshots.unshift({
        id: `${now}-${Math.random().toString(36).slice(2, 8)}`,
        createdAt: now,
        version: SCRIPT.version,
        reason: String(reason || 'Recovery snapshot').slice(0, 80),
        state: stateCopy
        });
        return saveSettingsSnapshots(snapshots);
    }

    function parseSettingsPersistenceCandidate(raw, source, priority = 0) {
        if (raw === null || raw === undefined || raw === '') return null;
        try {
        const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
        if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null;
        const envelope = Number(parsed.schema) === 1 && parsed.state && typeof parsed.state === 'object' && !Array.isArray(parsed.state);
        const candidateState = envelope ? parsed.state : parsed;
        if (!looksLikeToolkitState(candidateState)) return null;
        const metadata = envelope ? parsed : candidateState.__mcmsPersistence;
        return {
            source,
            priority,
            raw,
            state: candidateState,
            revision: Math.max(0, Number(metadata?.revision) || 0),
            savedAt: Math.max(0, Number(metadata?.savedAt) || 0)
        };
        } catch (err) {
        return null;
        }
    }

    function settingsPersistenceCandidates() {
        const candidates = [
        parseSettingsPersistenceCandidate(gmGetValueSafe(SCRIPT.settingsVaultState, null), 'tampermonkey-primary', 60),
        parseSettingsPersistenceCandidate(settingsLocalStorageGet(SCRIPT.storageState), 'page-primary', 50),
        parseSettingsPersistenceCandidate(gmGetValueSafe(SCRIPT.settingsRecoveryState, null), 'tampermonkey-recovery', 40),
        parseSettingsPersistenceCandidate(gmGetValueSafe(SCRIPT.storageState, null), 'tampermonkey-legacy-primary', 30),
        ...SCRIPT.oldStorageKeys.flatMap((key, index) => [
            parseSettingsPersistenceCandidate(settingsLocalStorageGet(key), `page-legacy-${key}`, 20 - index),
            parseSettingsPersistenceCandidate(gmGetValueSafe(key, null), `tampermonkey-legacy-${key}`, 10 - index)
        ])
        ].filter(Boolean);
        return candidates.sort((left, right) =>
        right.revision - left.revision ||
        right.savedAt - left.savedAt ||
        right.priority - left.priority
        );
    }

    function persistSettingsState(value, { requireWrite = false, preserveRecovery = true } = {}) {
        const stateCopy = JSON.parse(JSON.stringify(value));
        delete stateCopy.__mcmsPersistence;
        const previousPrimaryRaw = gmGetValueSafe(SCRIPT.settingsVaultState, null);
        const previousPrimary = parseSettingsPersistenceCandidate(previousPrimaryRaw, 'tampermonkey-primary', 60);
        const previousLocal = parseSettingsPersistenceCandidate(settingsLocalStorageGet(SCRIPT.storageState), 'page-primary', 50);
        const revision = Math.max(
        Number(settingsPersistenceMeta.revision) || 0,
        Number(previousPrimary?.revision) || 0,
        Number(previousLocal?.revision) || 0
        ) + 1;
        const savedAt = Date.now();
        const envelope = {
        schema: 1,
        revision,
        savedAt,
        version: SCRIPT.version,
        state: stateCopy
        };
        if (preserveRecovery && previousPrimary) {
        captureSettingsSnapshot(previousPrimary.state, { reason: 'Automatic pre-change snapshot' });
        gmSetValueSafe(SCRIPT.settingsRecoveryState, typeof previousPrimaryRaw === 'string' ? previousPrimaryRaw : JSON.stringify(previousPrimaryRaw));
        }
        const durableSaved = gmSetValueSafe(SCRIPT.settingsVaultState, JSON.stringify(envelope));
        const pageCopy = {
        ...stateCopy,
        __mcmsPersistence: { schema: 1, revision, savedAt, version: SCRIPT.version }
        };
        const pageSaved = settingsLocalStorageSet(SCRIPT.storageState, JSON.stringify(pageCopy));
        if (requireWrite && !durableSaved && !pageSaved) throw new Error('Toolkit settings storage is unavailable.');
        if (durableSaved || pageSaved) settingsPersistenceMeta = { revision, savedAt, source: durableSaved ? 'tampermonkey-primary' : 'page-primary' };
        return durableSaved || pageSaved;
    }

    function loadState() {
        const base = defaultState();
        const candidates = settingsPersistenceCandidates();
        for (const candidate of candidates) {
        try {
            const loaded = normaliseLoadedState(candidate.state, base);
            settingsPersistenceMeta = {
            revision: candidate.revision,
            savedAt: candidate.savedAt,
            source: candidate.source
            };
            const durable = parseSettingsPersistenceCandidate(gmGetValueSafe(SCRIPT.settingsVaultState, null), 'tampermonkey-primary', 60);
            const page = parseSettingsPersistenceCandidate(settingsLocalStorageGet(SCRIPT.storageState), 'page-primary', 50);
            const needsRepair = candidate.source !== 'tampermonkey-primary' ||
            !page ||
            page.revision !== candidate.revision ||
            page.savedAt !== candidate.savedAt ||
            !durable;
            if (needsRepair) persistSettingsState(loaded, { preserveRecovery: Boolean(durable) });
            return loaded;
        } catch (err) {}
        }
        base.updateBriefing.seenVersion = SCRIPT.version;
        settingsPersistenceMeta = { revision: 0, savedAt: 0, source: 'defaults' };
        return base;
    }

    function saveState(options = {}) {
        const saved = persistSettingsState(state, options);
        settingsLocalStorageSet(SCRIPT.legacyTheme, state.theme);
        settingsLocalStorageSet(SCRIPT.legacyPosition, state.position);
        return saved;
    }

    function getLegacyTheme() {
        return normaliseTheme(settingsLocalStorageGet(SCRIPT.legacyTheme) || 'default');
    }

    function getLegacyPosition() {
        const saved = settingsLocalStorageGet(SCRIPT.legacyPosition);
        return POSITIONS[saved] ? saved : 'bl';
    }

    function normaliseUiTheme(key) {
        return UI_THEMES[key] ? key : 'mapCommand';
    }

    function applyUiTheme(key, announce = false) {
        const nextTheme = normaliseUiTheme(key);
        const changed = state.uiTheme !== nextTheme;
        const pairedPayoutByTheme = Object.freeze({ hyrule: 'hyruleQuest', godfather: 'godfatherOffer' });
        const pairedTemplate = pairedPayoutByTheme[nextTheme] || '';
        const pairedPayoutChanged = Boolean(pairedTemplate && state.payoutFlash.template !== pairedTemplate);
        const godfatherDurationChanged = nextTheme === 'godfather' && state.payoutFlash.durationMs === 4000;
        state.uiTheme = nextTheme;
        if (pairedPayoutChanged) state.payoutFlash.template = pairedTemplate;
        if (godfatherDurationChanged) state.payoutFlash.durationMs = 7000;
        saveState();
        updateUI();
        const panel = commandInterfacePanel();
        if (panel?.classList.contains('mcms-open') && !dragState) positionPanelOverlay(true);
        if (announce && changed) {
        const pairedMessages = {
            hyrule: 'Hyrule Command interface and Quest Reward payout active',
            godfather: 'The Godfather interface and 7-second Offer payout active'
        };
        showToast(pairedPayoutChanged ? pairedMessages[nextTheme] : `${UI_THEMES[nextTheme].label} interface active`);
        }
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
        factorio: {
            standard: 'PRODUCTION TARGET MET', major: 'ASSEMBLY BONUS SECURED', high: 'MEGABASE PAYOUT', elite: 'THE FACTORY MUST GROW'
        },
        galactic: {
            standard: 'CREDITS RECEIVED', major: 'FLEET BONUS CLEARED', high: 'SECTOR TREASURY UNLOCKED', elite: 'GALACTIC FORTUNE'
        },
        darkFantasy: {
            standard: 'Reward Bestowed', major: 'Royal Bounty', high: 'Ancient Treasure Claimed', elite: 'Fortune of the Realm'
        },
        biohazard: {
            standard: 'CONTAINMENT OPERATION COMPLETE', major: 'SECURE TRANSFER RELEASED', high: 'BLACKSITE CREDIT AUTHORIZED', elite: 'OMEGA CLEARANCE AWARD'
        },
        underworld: {
            standard: 'Tribute Collected', major: 'Blood Money Secured', high: 'Dynasty Fortune', elite: 'Sovereign of the Night'
        },
        pixelArcade: {
            standard: 'STAGE CLEAR', major: 'BONUS ROUND', high: 'HIGH SCORE PAYOUT', elite: '1UP JACKPOT'
        },
        jamesBond: {
            standard: 'MISSION ACCOMPLISHED', major: 'CLASSIFIED BONUS SECURED', high: 'DOUBLE-O PAYDAY', elite: 'TOP SECRET JACKPOT'
        },
        hyruleQuest: {
            standard: 'QUEST COMPLETE', major: "HERO'S REWARD", high: 'TREASURE OF HYRULE', elite: 'LEGENDARY RELIC CLAIMED'
        },
        godfatherOffer: {
            standard: 'The Account Is Settled', major: 'A Respectable Arrangement', high: 'The Family Is Rewarded', elite: 'An Offer No One Refused'
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

    function allianceAwareHtml(value) {
        return escapeHtml(value).replace(/\balliance\b/giu, match => `<span class="mcms-alliance-text">${match}</span>`);
    }

    function closestEventTarget(event, selector) {
        const target = event?.target;
        if (target && typeof target.closest === 'function') return target.closest(selector);
        return target?.parentElement?.closest?.(selector) || null;
    }


    function decodeMissionTextEntities(value) {
        let text = String(value ?? '');
        const entityPattern = /&(?:#\d+|#x[\da-f]+|[a-z]+);/i;
        if (!entityPattern.test(text)) return text;
        try {
        const textarea = document.createElement('textarea');
            // MissionChief can return captions as either &quot; or double-escaped
            // &amp;quot;. Decode a small bounded number of passes until stable.
        for (let pass = 0; pass < 3 && entityPattern.test(text); pass += 1) {
            textarea.innerHTML = text;
            const decoded = textarea.value;
            if (decoded === text) break;
            text = decoded;
        }
        return text;
        } catch (err) {
        return text;
        }
    }

    function normaliseMissionCaption(value) {
        return decodeMissionTextEntities(value).replace(/\s+/g, ' ').trim();
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
        .join(' ‚Ä¢ ');
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
        document.querySelectorAll(`#${SCRIPT.controlId}, #${SCRIPT.panelId}, #${SCRIPT.toastId}, #${SCRIPT.payoutFlashId}, #${SCRIPT.vehicleStatusId}, #${SCRIPT.pressureBoardId}, #${SCRIPT.majorIncidentFeedId}, #${SCRIPT.helpCenterId}, #${SCRIPT.commandPaletteId}, #${SCRIPT.commandExperienceModalId}, #${SCRIPT.mapMeasureHudId}, #${SCRIPT.contextMenuId}, #${SCRIPT.quickWheelId}, #${SCRIPT.fullscreenExitId}, #${SCRIPT.vehicleFollowId}, #${SCRIPT.oldControlId}, #${SCRIPT.cleanExitId}, #${SCRIPT.oldGeoLabelLayerId}`)
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
        const parent = document.head || document.documentElement;
        if (parent) parent.appendChild(style);
        else document.addEventListener('readystatechange', () => (document.head || document.documentElement)?.appendChild(style), { once: true });
    }

    let mainStylesInstalled = false;

    function installMainStyles() {
        if (mainStylesInstalled && document.getElementById(SCRIPT.styleId)) return;
        const styleStartedAt = startupClock();
        mainStylesInstalled = true;
        addStyle(`
html[data-mc-map-skin="default"] .leaflet-tile-pane img.leaflet-tile { filter: none !important; }html[data-mc-map-skin="control"] .leaflet-container { background: #111820 !important; }html[data-mc-map-skin="control"] .leaflet-tile-pane img.leaflet-tile { filter: invert(92%) hue-rotate(182deg) brightness(62%) contrast(112%) saturate(72%) !important; }html[data-mc-map-skin="incident"] .leaflet-tile-pane img.leaflet-tile { filter: brightness(108%) contrast(142%) saturate(118%) !important; }html[data-mc-map-skin="roads"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(28%) brightness(104%) contrast(126%) saturate(70%) !important; }html[data-mc-map-skin="urban"] .leaflet-container { background: #111 !important; }html[data-mc-map-skin="urban"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(100%) invert(88%) brightness(61%) contrast(122%) saturate(54%) !important; }html[data-mc-map-skin="rural"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(42%) brightness(94%) contrast(108%) saturate(58%) !important; }html[data-mc-map-skin="nightshift"] .leaflet-container { background: #07111f !important; }html[data-mc-map-skin="nightshift"] .leaflet-tile-pane img.leaflet-tile { filter: invert(88%) hue-rotate(165deg) brightness(68%) contrast(119%) saturate(72%) !important; }html[data-mc-map-skin="fireCommand"] .leaflet-container { background: #17120f !important; }html[data-mc-map-skin="fireCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(38%) sepia(58%) hue-rotate(335deg) saturate(145%) brightness(76%) contrast(124%) !important; }html[data-mc-map-skin="policeTactical"] .leaflet-container { background: #071321 !important; }html[data-mc-map-skin="policeTactical"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(24%) invert(89%) sepia(18%) saturate(118%) hue-rotate(166deg) brightness(64%) contrast(126%) !important; }html[data-mc-map-skin="medicalControl"] .leaflet-container { background: #061b1c !important; }html[data-mc-map-skin="medicalControl"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(18%) invert(88%) sepia(22%) saturate(126%) hue-rotate(126deg) brightness(68%) contrast(116%) !important; }html[data-mc-map-skin="coastalCommand"] .leaflet-container { background: #061725 !important; }html[data-mc-map-skin="coastalCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(22%) sepia(24%) hue-rotate(145deg) saturate(138%) brightness(82%) contrast(118%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="default"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(18%) brightness(106%) contrast(132%) saturate(82%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="control"] .leaflet-tile-pane img.leaflet-tile { filter: invert(92%) hue-rotate(182deg) brightness(68%) contrast(132%) saturate(70%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="incident"] .leaflet-tile-pane img.leaflet-tile { filter: brightness(112%) contrast(156%) saturate(110%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="roads"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(35%) brightness(110%) contrast(150%) saturate(58%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="urban"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(100%) invert(88%) brightness(68%) contrast(144%) saturate(50%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="rural"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(48%) brightness(101%) contrast(130%) saturate(52%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="nightshift"] .leaflet-tile-pane img.leaflet-tile { filter: invert(88%) hue-rotate(165deg) brightness(73%) contrast(136%) saturate(68%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="fireCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(42%) sepia(62%) hue-rotate(335deg) saturate(150%) brightness(82%) contrast(142%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="policeTactical"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(28%) invert(89%) sepia(18%) saturate(112%) hue-rotate(166deg) brightness(70%) contrast(144%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="medicalControl"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(22%) invert(88%) sepia(22%) saturate(122%) hue-rotate(126deg) brightness(74%) contrast(134%) !important; }html[data-mcms-road-priority="true"][data-mc-map-skin="coastalCommand"] .leaflet-tile-pane img.leaflet-tile { filter: grayscale(26%) sepia(24%) hue-rotate(145deg) saturate(132%) brightness(88%) contrast(136%) !important; }
        @keyframes mcmsMissionPulse {
            0% { filter: drop-shadow(0 0 1px rgba(255,70,70,.25)) brightness(1); }
            50% { filter: drop-shadow(0 0 8px rgba(255,70,70,.95)) brightness(1.18); }
            100% { filter: drop-shadow(0 0 1px rgba(255,70,70,.25)) brightness(1); }}html[data-mcms-marker-focus="true"] .leaflet-marker-pane > .leaflet-marker-icon:not(.mcms-marker-mission),
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon.mcms-marker-building,
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon.mcms-marker-vehicle,
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon[data-mcms-vehicle-marker="true"],
        html[data-mcms-marker-focus="true"] .leaflet-marker-icon[data-mcms-personal-building-marker="true"] {
            opacity: .38 !important;
            filter: grayscale(35%) brightness(.82) !important;}html[data-mcms-marker-focus="true"] .leaflet-marker-icon.mcms-marker-mission {
            opacity: 1 !important;
            filter: drop-shadow(0 0 5px rgba(255,75,75,.75)) brightness(1.12) !important;
            z-index: 999 !important;}html[data-mcms-mission-pulse="true"] .leaflet-marker-icon.mcms-marker-mission { animation: mcmsMissionPulse 1.65s ease-in-out infinite !important; }html[data-mcms-show-alliance-missions="false"] .leaflet-marker-icon.mcms-marker-alliance-mission { display: none !important; }html[data-mcms-show-my-missions="false"] .leaflet-marker-icon.mcms-marker-my-mission { display: none !important; }html[data-mcms-show-vehicles="false"] .leaflet-marker-icon.mcms-marker-vehicle,
        html[data-mcms-show-vehicles="false"] .leaflet-marker-icon[data-mcms-vehicle-marker="true"] { display: none !important; }html[data-mcms-show-buildings="false"] .leaflet-marker-icon.mcms-marker-personal-building,
        html[data-mcms-show-buildings="false"] .leaflet-marker-icon[data-mcms-personal-building-marker="true"] { display: none !important; }.leaflet-marker-icon.mcms-mission-focus {
            filter: drop-shadow(0 0 5px #fff) drop-shadow(0 0 12px #ff5252) brightness(1.22) !important;
            z-index: 1000 !important;}.mcms-mission-lock-travel-overlay,
        .mcms-mission-lock-dom,
        .leaflet-marker-icon.mcms-mission-lock-target {
            --mcms-lock-primary:#67d9ff;
            --mcms-lock-secondary:#e9fbff;
            --mcms-lock-accent:#ff5252;
            --mcms-lock-surface:rgba(3,13,22,.92);
            --mcms-lock-grid:rgba(103,217,255,.12);
            --mcms-lock-x:50%;
            --mcms-lock-y:50%;}.mcms-mission-lock-travel-overlay {
            position:absolute !important;
            inset:0 !important;
            z-index:780 !important;
            overflow:hidden !important;
            pointer-events:none !important;
            opacity:0 !important;
            background:
                linear-gradient(180deg,rgba(0,0,0,.10),transparent 28% 72%,rgba(0,0,0,.18)),
                repeating-linear-gradient(90deg,transparent 0 89px,var(--mcms-lock-grid) 90px 91px,transparent 92px 180px) !important;
            animation:mcmsIntelTravel 860ms cubic-bezier(.2,.72,.2,1) both !important;}.mcms-mission-lock-travel-overlay::before {
            content:'' !important;
            position:absolute !important;
            left:-15% !important;
            right:-15% !important;
            top:12% !important;
            height:1px !important;
            background:linear-gradient(90deg,transparent,var(--mcms-lock-primary) 22%,var(--mcms-lock-secondary) 50%,var(--mcms-lock-primary) 78%,transparent) !important;
            box-shadow:0 0 6px var(--mcms-lock-primary),0 0 14px color-mix(in srgb,var(--mcms-lock-primary) 45%,transparent) !important;
            animation:mcmsIntelTravelScan 860ms cubic-bezier(.16,.72,.18,1) both !important;}.mcms-mission-lock-travel-overlay::after {
            content:'TRACKING / COORDINATE INTERCEPT' !important;
            position:absolute !important;
            left:14px !important;
            bottom:11px !important;
            color:var(--mcms-lock-primary) !important;
            font:900 8px/1 Arial,Helvetica,sans-serif !important;
            letter-spacing:1.15px !important;
            opacity:0 !important;
            text-shadow:0 0 8px color-mix(in srgb,var(--mcms-lock-primary) 62%,transparent) !important;
            animation:mcmsIntelTravelCaption 860ms ease both !important;}.mcms-mission-lock-dom {
            position:absolute !important;
            inset:0 !important;
            z-index:790 !important;
            overflow:hidden !important;
            pointer-events:none !important;}.mcms-mission-lock-intel {
            position:absolute !important;
            inset:0 !important;
            pointer-events:none !important;}.mcms-mission-lock-beam {
            position:absolute !important;
            opacity:0 !important;
            background:linear-gradient(90deg,transparent,var(--mcms-lock-primary) 18%,var(--mcms-lock-secondary) 50%,var(--mcms-lock-primary) 82%,transparent) !important;
            filter:drop-shadow(0 0 4px var(--mcms-lock-primary)) !important;}.mcms-mission-lock-beam-left,
        .mcms-mission-lock-beam-right {
            top:calc(var(--mcms-lock-y) - .5px) !important;
            height:1px !important;}.mcms-mission-lock-beam-left {
            left:0 !important;
            width:max(0px,calc(var(--mcms-lock-x) - 54px)) !important;
            transform-origin:right center !important;
            animation:mcmsIntelBeamLeft 1100ms cubic-bezier(.18,.74,.16,1) 40ms both !important;}.mcms-mission-lock-beam-right {
            left:calc(var(--mcms-lock-x) + 54px) !important;
            right:0 !important;
            transform-origin:left center !important;
            animation:mcmsIntelBeamRight 1100ms cubic-bezier(.18,.74,.16,1) 40ms both !important;}.mcms-mission-lock-beam-top,
        .mcms-mission-lock-beam-bottom {
            left:calc(var(--mcms-lock-x) - .5px) !important;
            width:1px !important;
            background:linear-gradient(180deg,transparent,var(--mcms-lock-primary) 18%,var(--mcms-lock-secondary) 50%,var(--mcms-lock-primary) 82%,transparent) !important;}.mcms-mission-lock-beam-top {
            top:0 !important;
            height:max(0px,calc(var(--mcms-lock-y) - 54px)) !important;
            transform-origin:center bottom !important;
            animation:mcmsIntelBeamTop 1100ms cubic-bezier(.18,.74,.16,1) 40ms both !important;
        }.mcms-mission-lock-beam-bottom {
            top:calc(var(--mcms-lock-y) + 54px) !important;
            bottom:0 !important;
            transform-origin:center top !important;
            animation:mcmsIntelBeamBottom 1100ms cubic-bezier(.18,.74,.16,1) 40ms both !important;
        }.mcms-mission-lock-reticle {
            position:absolute !important;
            left:var(--mcms-lock-x) !important;
            top:var(--mcms-lock-y) !important;
            width:92px !important;
            height:92px !important;
            transform:translate(-50%,-50%) scale(1.7) !important;
            opacity:0 !important;
            animation:mcmsIntelReticleAcquire 2250ms cubic-bezier(.15,.76,.16,1) 480ms both !important;
        }.mcms-mission-lock-reticle::before,
        .mcms-mission-lock-reticle::after {
            content:'' !important;
            position:absolute !important;
            inset:11px !important;
            border-radius:50% !important;
            border:1px solid color-mix(in srgb,var(--mcms-lock-primary) 80%,transparent) !important;
            box-shadow:0 0 10px color-mix(in srgb,var(--mcms-lock-primary) 32%,transparent) !important;
        }.mcms-mission-lock-reticle::before {
            border-style:dashed !important;
            animation:mcmsIntelRingSpin 2.1s linear 650ms both !important;
        }.mcms-mission-lock-reticle::after {
            inset:26px !important;
            border-color:var(--mcms-lock-secondary) !important;
            animation:mcmsIntelInnerPulse 1.05s ease-in-out 1000ms 2 both !important;
        }.mcms-mission-lock-radar {
            position:absolute !important;
            inset:15px !important;
            border-radius:50% !important;
            overflow:hidden !important;
            opacity:0 !important;
            background:conic-gradient(from -35deg,transparent 0 300deg,color-mix(in srgb,var(--mcms-lock-primary) 8%,transparent) 306deg,color-mix(in srgb,var(--mcms-lock-primary) 48%,transparent) 338deg,transparent 348deg 360deg) !important;
            animation:mcmsIntelRadar 1450ms cubic-bezier(.18,.72,.16,1) 500ms both !important;
        }.mcms-mission-lock-bracket {
            position:absolute !important;
            width:19px !important;
            height:19px !important;
            opacity:0 !important;
            border-color:var(--mcms-lock-primary) !important;
            border-style:solid !important;
            filter:drop-shadow(0 0 4px color-mix(in srgb,var(--mcms-lock-primary) 62%,transparent)) !important;
        }.mcms-mission-lock-bracket-a { left:0;top:0;border-width:2px 0 0 2px;animation:mcmsIntelBracketA 720ms cubic-bezier(.12,.78,.16,1) 850ms both !important; }.mcms-mission-lock-bracket-b { right:0;top:0;border-width:2px 2px 0 0;animation:mcmsIntelBracketB 720ms cubic-bezier(.12,.78,.16,1) 850ms both !important; }.mcms-mission-lock-bracket-c { right:0;bottom:0;border-width:0 2px 2px 0;animation:mcmsIntelBracketC 720ms cubic-bezier(.12,.78,.16,1) 850ms both !important; }.mcms-mission-lock-bracket-d { left:0;bottom:0;border-width:0 0 2px 2px;animation:mcmsIntelBracketD 720ms cubic-bezier(.12,.78,.16,1) 850ms both !important; }.mcms-mission-lock-crosshair {
            position:absolute !important;
            left:50% !important;
            top:50% !important;
            width:28px !important;
            height:28px !important;
            transform:translate(-50%,-50%) !important;
            opacity:0 !important;
            animation:mcmsIntelCrosshair 420ms ease 1320ms both !important;
        }.mcms-mission-lock-crosshair::before,
        .mcms-mission-lock-crosshair::after {
            content:'' !important;
            position:absolute !important;
            background:var(--mcms-lock-secondary) !important;
            box-shadow:0 0 5px var(--mcms-lock-primary) !important;
        }.mcms-mission-lock-crosshair::before { left:0;right:0;top:50%;height:1px;transform:translateY(-50%); }.mcms-mission-lock-crosshair::after { top:0;bottom:0;left:50%;width:1px;transform:translateX(-50%); }.mcms-mission-lock-dot {
            position:absolute !important;
            left:50% !important;
            top:50% !important;
            width:5px !important;
            height:5px !important;
            border-radius:50% !important;
            transform:translate(-50%,-50%) !important;
            background:var(--mcms-lock-accent) !important;
            box-shadow:0 0 4px var(--mcms-lock-secondary),0 0 12px var(--mcms-lock-accent) !important;
            opacity:0 !important;
            animation:mcmsIntelDot 1100ms ease 1280ms both !important;
        }.mcms-mission-lock-scan {
            position:absolute !important;
            left:16px !important;
            right:16px !important;
            top:20px !important;
            height:1px !important;
            background:linear-gradient(90deg,transparent,var(--mcms-lock-secondary),transparent) !important;
            box-shadow:0 0 6px var(--mcms-lock-primary) !important;
            opacity:0 !important;
            animation:mcmsIntelLocalScan 980ms ease 780ms both !important;
        }.mcms-mission-lock-label {
            position:absolute !important;
            left:50% !important;
            top:calc(100% + 8px) !important;
            width:max-content !important;
            max-width:190px !important;
            padding:5px 9px !important;
            border:1px solid color-mix(in srgb,var(--mcms-lock-primary) 74%,transparent) !important;
            border-left:3px solid var(--mcms-lock-accent) !important;
            border-radius:3px !important;
            background:var(--mcms-lock-surface) !important;
            color:var(--mcms-lock-secondary) !important;
            box-shadow:0 5px 14px rgba(0,0,0,.38),0 0 10px color-mix(in srgb,var(--mcms-lock-primary) 24%,transparent) !important;
            transform:translateX(-50%) translateY(6px) !important;
            opacity:0 !important;
            white-space:nowrap !important;
            overflow:hidden !important;
            text-overflow:ellipsis !important;
            animation:mcmsIntelLabel 1550ms ease 1450ms both !important;
        }.mcms-mission-lock-label strong {
            display:block !important;
            color:var(--mcms-lock-primary) !important;
            font:950 8px/1 Arial,Helvetica,sans-serif !important;
            letter-spacing:1px !important;
            text-transform:uppercase !important;
        }.mcms-mission-lock-label small {
            display:block !important;
            margin-top:3px !important;
            color:var(--mcms-lock-secondary) !important;
            font:800 8px/1.1 Arial,Helvetica,sans-serif !important;
            overflow:hidden !important;
            text-overflow:ellipsis !important;
        }.leaflet-marker-icon.mcms-mission-lock-target {
            animation:mcmsIntelMarkerPulse 2.65s ease-in-out 920ms both !important;
            z-index:1500 !important;
        }html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-lock-travel-overlay,
        html[data-mcms-ui-theme="cyberpunk"] .mcms-mission-lock-dom,
        html[data-mcms-ui-theme="cyberpunk"] .leaflet-marker-icon.mcms-mission-lock-target {
            --mcms-lock-primary:#fcee0a;--mcms-lock-secondary:#00f0ff;--mcms-lock-accent:#ff2a6d;--mcms-lock-surface:rgba(7,12,20,.94);--mcms-lock-grid:rgba(0,240,255,.12);
        }html[data-mcms-ui-theme="fallout4"] .mcms-mission-lock-travel-overlay,
        html[data-mcms-ui-theme="fallout4"] .mcms-mission-lock-dom,
        html[data-mcms-ui-theme="fallout4"] .leaflet-marker-icon.mcms-mission-lock-target {
            --mcms-lock-primary:#b8ff6a;--mcms-lock-secondary:#e5ffc2;--mcms-lock-accent:#ffcf62;--mcms-lock-surface:rgba(12,28,12,.94);--mcms-lock-grid:rgba(184,255,106,.10);
        }html[data-mcms-ui-theme="umbrella"] .mcms-mission-lock-travel-overlay,
        html[data-mcms-ui-theme="umbrella"] .mcms-mission-lock-dom,
        html[data-mcms-ui-theme="umbrella"] .leaflet-marker-icon.mcms-mission-lock-target {
            --mcms-lock-primary:#f23838;--mcms-lock-secondary:#fff;--mcms-lock-accent:#ffcf62;--mcms-lock-surface:rgba(15,17,20,.95);--mcms-lock-grid:rgba(242,56,56,.10);
        }html[data-mcms-ui-theme="factorio"] .mcms-mission-lock-travel-overlay,
        html[data-mcms-ui-theme="factorio"] .mcms-mission-lock-dom,
        html[data-mcms-ui-theme="factorio"] .leaflet-marker-icon.mcms-mission-lock-target {
            --mcms-lock-primary:#ff9b32;--mcms-lock-secondary:#fff0cf;--mcms-lock-accent:#ffdb59;--mcms-lock-surface:rgba(39,38,32,.95);--mcms-lock-grid:rgba(255,155,50,.10);
        }
        @keyframes mcmsIntelTravel { 0%{opacity:0} 12%{opacity:.34} 70%{opacity:.18} 100%{opacity:0} }
        @keyframes mcmsIntelTravelScan { 0%{opacity:0;top:8%} 14%{opacity:1} 82%{opacity:.82;top:92%} 100%{opacity:0;top:96%} }
        @keyframes mcmsIntelTravelCaption { 0%,18%{opacity:0;transform:translateX(-6px)} 28%,72%{opacity:.85;transform:translateX(0)} 100%{opacity:0;transform:translateX(4px)} }
        @keyframes mcmsIntelBeamLeft { 0%{opacity:0;transform:scaleX(0)} 22%{opacity:.9} 76%{opacity:.92;transform:scaleX(1)} 100%{opacity:0;transform:scaleX(1)} }
        @keyframes mcmsIntelBeamRight { 0%{opacity:0;transform:scaleX(0)} 22%{opacity:.9} 76%{opacity:.92;transform:scaleX(1)} 100%{opacity:0;transform:scaleX(1)} }
        @keyframes mcmsIntelBeamTop { 0%{opacity:0;transform:scaleY(0)} 22%{opacity:.9} 76%{opacity:.92;transform:scaleY(1)} 100%{opacity:0;transform:scaleY(1)} }
        @keyframes mcmsIntelBeamBottom { 0%{opacity:0;transform:scaleY(0)} 22%{opacity:.9} 76%{opacity:.92;transform:scaleY(1)} 100%{opacity:0;transform:scaleY(1)} }
        @keyframes mcmsIntelReticleAcquire { 0%,10%{opacity:0;transform:translate(-50%,-50%) scale(1.7)} 26%{opacity:1;transform:translate(-50%,-50%) scale(.86)} 38%{transform:translate(-50%,-50%) scale(1.04)} 88%{opacity:1;transform:translate(-50%,-50%) scale(1)} 100%{opacity:0;transform:translate(-50%,-50%) scale(1.04)} }
        @keyframes mcmsIntelRingSpin { 0%{transform:rotate(-90deg) scale(1.35);opacity:0} 18%{opacity:1} 100%{transform:rotate(390deg) scale(1);opacity:.8} }
        @keyframes mcmsIntelInnerPulse { 0%{transform:scale(.75);opacity:.2} 50%{transform:scale(1.06);opacity:1} 100%{transform:scale(1);opacity:.55} }
        @keyframes mcmsIntelRadar { 0%{opacity:0;transform:rotate(-120deg) scale(.65)} 15%{opacity:.82} 82%{opacity:.72;transform:rotate(540deg) scale(1)} 100%{opacity:0;transform:rotate(660deg) scale(1)} }
        @keyframes mcmsIntelBracketA { 0%{opacity:0;transform:translate(-32px,-32px)} 100%{opacity:1;transform:translate(0,0)} }
        @keyframes mcmsIntelBracketB { 0%{opacity:0;transform:translate(32px,-32px)} 100%{opacity:1;transform:translate(0,0)} }
        @keyframes mcmsIntelBracketC { 0%{opacity:0;transform:translate(32px,32px)} 100%{opacity:1;transform:translate(0,0)} }
        @keyframes mcmsIntelBracketD { 0%{opacity:0;transform:translate(-32px,32px)} 100%{opacity:1;transform:translate(0,0)} }
        @keyframes mcmsIntelCrosshair { 0%{opacity:0;transform:translate(-50%,-50%) scale(1.8)} 100%{opacity:1;transform:translate(-50%,-50%) scale(1)} }
        @keyframes mcmsIntelDot { 0%,100%{opacity:.3;transform:translate(-50%,-50%) scale(.8)} 35%,65%{opacity:1;transform:translate(-50%,-50%) scale(1.2)} }
        @keyframes mcmsIntelLocalScan { 0%{opacity:0;top:18px} 16%{opacity:1} 82%{opacity:.9;top:73px} 100%{opacity:0;top:76px} }
        @keyframes mcmsIntelLabel { 0%{opacity:0;transform:translateX(-50%) translateY(6px)} 18%,76%{opacity:1;transform:translateX(-50%) translateY(0)} 100%{opacity:0;transform:translateX(-50%) translateY(-2px)} }
        @keyframes mcmsIntelMarkerPulse { 0%,20%,100%{filter:brightness(1)} 38%{filter:drop-shadow(0 0 7px var(--mcms-lock-secondary,#fff)) drop-shadow(0 0 15px var(--mcms-lock-primary,#67d9ff)) brightness(1.45)} 58%{filter:drop-shadow(0 0 5px var(--mcms-lock-primary,#67d9ff)) brightness(1.16)} 74%{filter:drop-shadow(0 0 9px var(--mcms-lock-primary,#67d9ff)) brightness(1.3)} }
        @media (prefers-reduced-motion:reduce) {.mcms-mission-lock-travel-overlay,
        .mcms-mission-lock-travel-overlay::before,
        .mcms-mission-lock-travel-overlay::after,
        .mcms-mission-lock-beam,
        .mcms-mission-lock-reticle,
        .mcms-mission-lock-reticle::before,
        .mcms-mission-lock-reticle::after,
        .mcms-mission-lock-radar,
        .mcms-mission-lock-bracket,
        .mcms-mission-lock-crosshair,
        .mcms-mission-lock-dot,
        .mcms-mission-lock-scan,
        .mcms-mission-lock-label,
        .leaflet-marker-icon.mcms-mission-lock-target { animation:none !important; }.mcms-mission-lock-travel-overlay,
        .mcms-mission-lock-beam,
        .mcms-mission-lock-radar,
        .mcms-mission-lock-scan { display:none !important; }.mcms-mission-lock-reticle { opacity:1 !important; transform:translate(-50%,-50%) !important; }.mcms-mission-lock-bracket,
        .mcms-mission-lock-crosshair,
        .mcms-mission-lock-dot,
        .mcms-mission-lock-label { opacity:1 !important; }.mcms-mission-lock-label { transform:translateX(-50%) !important; }
        }html[data-mcms-clean="true"] .leaflet-control-zoom,
        html[data-mcms-clean="true"] .leaflet-control-scale,
        html[data-mcms-clean="true"] .leaflet-control-attribution,
        html[data-mcms-clean="true"] #${SCRIPT.controlId} { display: none !important; }#${SCRIPT.cleanExitId} {
            display: none; position: fixed; top: 10px; right: 12px; z-index: 999999;
            padding: 7px 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,.22);
            background: rgba(10,14,20,.88); color: #fff; font: 900 11px/1.1 Arial, Helvetica, sans-serif;
            cursor: pointer; box-shadow: 0 8px 22px rgba(0,0,0,.34); backdrop-filter: blur(8px);
        }html[data-mcms-clean="true"] #${SCRIPT.cleanExitId} { display: block; }#${SCRIPT.controlId},
        #${SCRIPT.controlId} *,
        #${SCRIPT.controlId} *::before,
        #${SCRIPT.controlId} *::after,
        #${SCRIPT.panelId},
        #${SCRIPT.panelId} *,
        #${SCRIPT.panelId} *::before,
        #${SCRIPT.panelId} *::after {
            box-sizing: border-box !important;
            font-family: Arial, Helvetica, sans-serif !important;
            text-shadow: none !important;
            letter-spacing: normal !important;
        }#${SCRIPT.controlId} {
            position: absolute !important; z-index: 980 !important; color: #e9eef5 !important;
            user-select: none !important; pointer-events: auto !important; font-size: 11px !important; line-height: 1.15 !important;
            margin-left: var(--mcms-nudge-x, 0px) !important; margin-top: var(--mcms-nudge-y, 0px) !important;
            max-width: 210px !important;
        }#${SCRIPT.controlId}.mcms-hidden-by-menu { opacity: .28 !important; }#${SCRIPT.controlId}.mcms-pos-tl { left: 54px !important; top: 10px !important; }#${SCRIPT.controlId}.mcms-pos-tr { right: 12px !important; top: 48px !important; }#${SCRIPT.controlId}.mcms-pos-bl { left: 12px !important; bottom: 42px !important; }#${SCRIPT.controlId}.mcms-pos-br { right: 12px !important; bottom: 42px !important; }#${SCRIPT.controlId} button,
        #${SCRIPT.panelId} button,
        #${SCRIPT.panelId} input,
        #${SCRIPT.panelId} select {
            appearance: none !important; -webkit-appearance: none !important; margin: 0 !important; font: inherit !important;
            text-transform: none !important; box-shadow: none !important; outline: none !important;
        }#${SCRIPT.controlId} .mcms-shell {
            position: relative !important; display: inline-flex !important; align-items: stretch !important;
            width: 40px !important; height: 48px !important; border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,.25) !important; background: rgba(10,14,20,.80) !important;
            box-shadow: 0 5px 16px rgba(0,0,0,.30) !important; backdrop-filter: blur(6px) !important; overflow: hidden !important;
            flex-direction: column !important;
        }#${SCRIPT.controlId} .mcms-menu-btn {
            width: 100% !important; height: auto !important; min-height: 0 !important; flex: 1 1 auto !important; border: 0 !important; background: transparent !important;
            color: #fff !important; cursor: pointer !important; display: flex !important; align-items: center !important;
            justify-content: center !important; padding: 0 !important; font-size: 17px !important;
        }#${SCRIPT.controlId} .mcms-menu-btn:hover,
        #${SCRIPT.controlId} .mcms-menu-btn:focus-visible { background: rgba(255,255,255,.12) !important; }#${SCRIPT.controlId} .mcms-dock-toggle-btn {
            width: 100% !important; height: 15px !important; flex: 0 0 15px !important; border: 0 !important; border-top: 1px solid rgba(255,255,255,.16) !important;
            padding: 0 !important; background: rgba(255,255,255,.055) !important; color: rgba(255,255,255,.82) !important; cursor: pointer !important;
            display: flex !important; align-items: center !important; justify-content: center !important; font-size: 11px !important; line-height: 1 !important; font-weight: 900 !important;
        }#${SCRIPT.controlId} .mcms-dock-toggle-btn:hover,
        #${SCRIPT.controlId} .mcms-dock-toggle-btn:focus-visible { background: rgba(86,169,255,.22) !important; color: #fff !important; }#${SCRIPT.controlId} .mcms-dock-toggle-icon { display: block !important; transform: translateY(-1px) !important; }html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins { display: none !important; }#${SCRIPT.controlId} .mcms-floating-filter {
            display: grid !important; grid-template-columns: repeat(2, 82px) !important; gap: 4px !important; margin-top: 6px !important; width: 168px !important;
        }#${SCRIPT.controlId} .mcms-float-btn,
        #${SCRIPT.controlId} .mcms-screen-pin-btn {
            border: 1px solid rgba(255,255,255,.18) !important; border-radius: 8px !important; color: rgba(255,255,255,.74) !important;
            cursor: pointer !important; font-size: 8.5px !important; line-height: 1 !important; font-weight: 900 !important;
            box-shadow: 0 3px 10px rgba(0,0,0,.25) !important; backdrop-filter: blur(6px) !important;
        }#${SCRIPT.controlId} .mcms-float-btn {
            height: 29px !important; background: rgba(10,14,20,.78) !important; padding: 0 5px !important;
            display: grid !important; grid-template-columns: 17px minmax(0,1fr) !important; align-items: center !important; gap: 5px !important;
            text-align: left !important; overflow: hidden !important;
        }#${SCRIPT.controlId} .mcms-float-key {
            width: 17px !important; height: 17px !important; border-radius: 6px !important; background: rgba(255,255,255,.12) !important;
            display: flex !important; align-items: center !important; justify-content: center !important; color: #fff !important;
            font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important;
        }#${SCRIPT.controlId} .mcms-float-label {
            min-width: 0 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important;
            font-size: 8.5px !important; line-height: 1 !important; font-weight: 900 !important;
        }#${SCRIPT.controlId} .mcms-float-label-tablet,
        #${SCRIPT.controlId} .mcms-float-label-mobile { display: none !important; }#${SCRIPT.controlId} .mcms-float-btn.mcms-on { background: rgba(25,118,210,.78) !important; color: #fff !important; border-color: rgba(120,190,255,.8) !important; }#${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key { background: rgba(255,255,255,.22) !important; }#${SCRIPT.controlId} .mcms-screen-pins {
            display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 4px !important; margin-top: 6px !important;
            width: 160px !important; max-height: 156px !important; overflow-y: auto !important; overflow-x: hidden !important; scrollbar-width: thin !important;
        }#${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }#${SCRIPT.controlId} .mcms-screen-pin-btn {
            height: 25px !important; min-width: 0 !important; padding: 0 6px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; color: #fff !important;
        }#${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-quick { background: rgba(16,78,138,.86) !important; border-color: rgba(86,169,255,.68) !important; }#${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-custom { background: rgba(106,80,10,.88) !important; border-color: rgba(255,213,79,.70) !important; }#${SCRIPT.panelId} {
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
        }#${SCRIPT.panelId}.mcms-open { display: block !important; }html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} {
            box-sizing: border-box !important;
            max-height: var(--mcms-desktop-panel-max-height, calc(100vh - 24px)) !important;
            overflow: hidden !important;
            overscroll-behavior: contain !important;
        }html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId}.mcms-open {
            display: grid !important;
            grid-template-rows: auto minmax(0, 1fr) !important;
            align-content: stretch !important;
        }html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack {
            grid-row: 1 !important;
            min-height: 0 !important;
            flex: none !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 30 !important;
            overflow: visible !important;
            transform: none !important;
        }html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-header,
        html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-tabs {
            flex: none !important;
        }html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel {
            grid-row: 2 !important;
            min-height: 0 !important;
            max-height: 100% !important;
        }html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel.mcms-active {
            display: block !important;
            height: 100% !important;
            min-height: 0 !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            overscroll-behavior: contain !important;
            scrollbar-width: thin !important;
            padding-right: 2px !important;
        }#${SCRIPT.panelId}.mcms-dragging { opacity: .96 !important; cursor: grabbing !important; }#${SCRIPT.panelId} .mcms-header {
            display: grid !important; grid-template-columns: minmax(0, 1fr) 24px 24px 24px !important; align-items: center !important; gap: 7px !important;
            margin: 0 0 8px 0 !important; padding: 0 0 7px 0 !important; border-bottom: 1px solid rgba(255,255,255,.12) !important; overflow: hidden !important;
        }#${SCRIPT.panelId} .mcms-drag-handle {
            min-width: 0 !important; cursor: grab !important; touch-action: none !important; user-select: none !important;
            border-radius: 9px !important; padding: 4px 6px !important; background: rgba(255,255,255,.055) !important; border: 1px solid rgba(255,255,255,.075) !important;
        }#${SCRIPT.panelId} .mcms-drag-handle:hover { background: rgba(255,255,255,.10) !important; }#${SCRIPT.panelId}.mcms-dragging .mcms-drag-handle { cursor: grabbing !important; }#${SCRIPT.panelId} .mcms-title { display: block !important; font-size: 13px !important; line-height: 1.1 !important; font-weight: 900 !important; color: #f2f6ff !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }#${SCRIPT.panelId} .mcms-subtitle { display: block !important; margin-top: 2px !important; font-size: 9px !important; line-height: 1.15 !important; color: rgba(233,238,245,.64) !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }#${SCRIPT.panelId} .mcms-close,
        #${SCRIPT.panelId} .mcms-reset-panel,
        #${SCRIPT.panelId} .mcms-help-button {
            width: 24px !important; height: 24px !important; border: 0 !important; border-radius: 8px !important; background: rgba(255,255,255,.10) !important;
            color: rgba(255,255,255,.88) !important; cursor: pointer !important; font-size: 15px !important; line-height: 24px !important; text-align: center !important; padding: 0 !important;
        }#${SCRIPT.panelId} .mcms-close:hover,
        #${SCRIPT.panelId} .mcms-reset-panel:hover,
        #${SCRIPT.panelId} .mcms-help-button:hover,
        #${SCRIPT.panelId} .mcms-help-button:focus-visible { background: rgba(58,174,232,.28) !important; color:#fff !important; }#${SCRIPT.panelId} .mcms-tabs { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 5px !important; margin-bottom: 8px !important; }#${SCRIPT.panelId} .mcms-tab-btn { height: 26px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 8px !important; background: rgba(255,255,255,.06) !important; color: rgba(255,255,255,.78) !important; cursor: pointer !important; font-size: 9px !important; line-height: 1.1 !important; font-weight: 900 !important; padding: 0 3px !important; overflow: hidden !important; white-space: normal !important; overflow-wrap: anywhere !important; }#${SCRIPT.panelId} .mcms-tab-btn.mcms-active,
        #${SCRIPT.panelId} .mcms-theme-btn.mcms-active,
        #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on,
        #${SCRIPT.panelId} .mcms-position-btn.mcms-active,
        #${SCRIPT.panelId} .mcms-pin-btn.mcms-on { background: rgba(25,118,210,.42) !important; border-color: rgba(120,190,255,.78) !important; color: #fff !important; }#${SCRIPT.panelId} .mcms-tab-panel { display: none !important; }#${SCRIPT.panelId} .mcms-tab-panel.mcms-active { display: block !important; }#${SCRIPT.panelId} .mcms-grid-2 { display: grid !important; grid-template-columns: repeat(2, minmax(0,1fr)) !important; gap: 7px !important; width: 100% !important; min-width: 0 !important; overflow: hidden !important; }#${SCRIPT.panelId} .mcms-theme-btn,
        #${SCRIPT.panelId} .mcms-toggle-btn,
        #${SCRIPT.panelId} .mcms-place-main {
            width: 100% !important; min-width: 0 !important; min-height: 42px !important; height: auto !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 10px !important;
            background: rgba(255,255,255,.065) !important; color: #eef4ff !important; padding: 6px !important; cursor: pointer !important; text-align: left !important;
            display: grid !important; grid-template-columns: 20px minmax(0,1fr) !important; align-items: center !important; gap: 6px !important; overflow: hidden !important;
        }#${SCRIPT.panelId} .mcms-theme-btn:hover,
        #${SCRIPT.panelId} .mcms-toggle-btn:hover,
        #${SCRIPT.panelId} .mcms-place-main:hover { background: rgba(255,255,255,.14) !important; border-color: rgba(255,255,255,.30) !important; }#${SCRIPT.panelId} .mcms-iconbox { width: 20px !important; height: 20px !important; min-width: 20px !important; border-radius: 7px !important; background: rgba(255,255,255,.11) !important; display: flex !important; align-items: center !important; justify-content: center !important; color: rgba(255,255,255,.86) !important; font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important; overflow: hidden !important; }#${SCRIPT.panelId} .mcms-text { display: block !important; min-width: 0 !important; max-width: 100% !important; overflow: hidden !important; }#${SCRIPT.panelId} .mcms-label { display: block !important; width: 100% !important; color: #f4f7ff !important; font-size: 10.5px !important; line-height: 1.15 !important; font-weight: 900 !important; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; overflow-wrap: anywhere !important; }#${SCRIPT.panelId} .mcms-pill { display: inline-block !important; margin-top: 4px !important; max-width: 78px !important; padding: 1px 5px !important; border-radius: 999px !important; background: rgba(255,255,255,.13) !important; color: rgba(255,255,255,.82) !important; font-size: 7.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; }#${SCRIPT.panelId} .mcms-section-label { margin: 9px 0 6px 0 !important; color: rgba(233,238,245,.62) !important; font-size: 9px !important; line-height: 1.25 !important; font-weight: 900 !important; letter-spacing: .55px !important; text-transform: uppercase !important; white-space: normal !important; overflow-wrap: anywhere !important; }#${SCRIPT.panelId} .mcms-row { display: grid !important; grid-template-columns: minmax(0,1fr) 100px !important; gap: 7px !important; align-items: center !important; margin-bottom: 7px !important; }#${SCRIPT.panelId} .mcms-row-label { color: rgba(255,255,255,.82) !important; font-size: 10px !important; line-height: 1.2 !important; font-weight: 800 !important; overflow: visible !important; text-overflow: clip !important; white-space: normal !important; overflow-wrap: anywhere !important; }#${SCRIPT.panelId} .mcms-input,
        #${SCRIPT.panelId} .mcms-select { width: 100% !important; height: 27px !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 8px !important; background: rgba(255,255,255,.08) !important; color: #fff !important; font-size: 10px !important; font-weight: 800 !important; padding: 0 7px !important; }#${SCRIPT.panelId} .mcms-select option { color: #111 !important; }#${SCRIPT.panelId} .mcms-position-grid,
        #${SCRIPT.panelId} .mcms-nudge-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 6px !important; width: 100% !important; }#${SCRIPT.panelId} .mcms-nudge-grid { grid-template-columns: repeat(5, minmax(0,1fr)) !important; }#${SCRIPT.panelId} .mcms-position-btn,
        #${SCRIPT.panelId} .mcms-small-btn,
        #${SCRIPT.panelId} .mcms-bookmark-btn,
        #${SCRIPT.panelId} .mcms-pin-btn { width: 100% !important; min-width: 0 !important; height: 28px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 9px !important; background: rgba(255,255,255,.065) !important; color: rgba(255,255,255,.84) !important; cursor: pointer !important; font-size: 9px !important; line-height: 28px !important; font-weight: 900 !important; text-align: center !important; padding: 0 !important; overflow: hidden !important; }#${SCRIPT.panelId} .mcms-small-btn { height: auto !important; min-height: 28px !important; line-height: 1.15 !important; padding: 5px 6px !important; white-space: normal !important; overflow-wrap: anywhere !important; display: flex !important; align-items: center !important; justify-content: center !important; }#${SCRIPT.panelId} .mcms-position-btn:hover,
        #${SCRIPT.panelId} .mcms-small-btn:hover,
        #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
        #${SCRIPT.panelId} .mcms-pin-btn:hover { background: rgba(255,255,255,.14) !important; }#${SCRIPT.panelId} .mcms-quick-row { display: grid !important; grid-template-columns: minmax(0,1fr) 44px !important; gap: 6px !important; margin-bottom: 6px !important; }#${SCRIPT.panelId} .mcms-bookmark-row { display: grid !important; grid-template-columns: minmax(0,1fr) 32px 38px 36px 26px !important; gap: 5px !important; align-items: center !important; margin-bottom: 5px !important; }#${SCRIPT.panelId} .mcms-bookmark-name { color: rgba(255,255,255,.86) !important; font-size: 10px !important; font-weight: 850 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }#${SCRIPT.panelId} .mcms-status { margin-top: 8px !important; padding: 7px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.12) !important; background: rgba(255,255,255,.055) !important; color: rgba(255,255,255,.68) !important; font-size: 9px !important; line-height: 1.25 !important; }#${SCRIPT.panelId} .mcms-input,
        #${SCRIPT.panelId} .mcms-select { user-select: text !important; }#${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 92px minmax(0,1fr) !important; }#${SCRIPT.panelId} .mcms-discord-preview { margin-top:8px !important; min-height:72px !important; }#${SCRIPT.panelId} .mcms-discord-empty { padding:14px 10px !important; border:1px dashed rgba(88,166,255,.28) !important; border-radius:10px !important; background:linear-gradient(135deg,rgba(88,166,255,.06),rgba(124,77,255,.05)) !important; color:rgba(255,255,255,.58) !important; font-size:9px !important; line-height:1.35 !important; text-align:center !important; }#${SCRIPT.panelId} .mcms-discord-card { padding:10px !important; border-radius:12px !important; border:1px solid rgba(255,255,255,.14) !important; background:linear-gradient(145deg,rgba(22,28,38,.96),rgba(11,15,22,.98)) !important; box-shadow:inset 0 1px rgba(255,255,255,.04),0 8px 18px rgba(0,0,0,.22) !important; }#${SCRIPT.panelId} .mcms-discord-card[data-tone="positive"] { border-color:rgba(46,204,113,.48) !important; box-shadow:inset 3px 0 #2ecc71,0 8px 18px rgba(0,0,0,.22) !important; }#${SCRIPT.panelId} .mcms-discord-card[data-tone="negative"] { border-color:rgba(231,76,60,.52) !important; box-shadow:inset 3px 0 #e74c3c,0 8px 18px rgba(0,0,0,.22) !important; }#${SCRIPT.panelId} .mcms-discord-card[data-tone="neutral"] { border-color:rgba(241,196,15,.42) !important; box-shadow:inset 3px 0 #f1c40f,0 8px 18px rgba(0,0,0,.22) !important; }#${SCRIPT.panelId} .mcms-discord-head { display:flex !important; justify-content:space-between !important; align-items:flex-start !important; gap:8px !important; margin-bottom:8px !important; }#${SCRIPT.panelId} .mcms-discord-title { color:#fff !important; font-size:10px !important; font-weight:950 !important; letter-spacing:.35px !important; }#${SCRIPT.panelId} .mcms-discord-date { margin-top:2px !important; color:rgba(255,255,255,.54) !important; font-size:8px !important; font-weight:800 !important; }#${SCRIPT.panelId} .mcms-discord-result { padding:3px 6px !important; border-radius:999px !important; background:rgba(255,255,255,.08) !important; color:#fff !important; font-size:8px !important; font-weight:950 !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-discord-stats { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }#${SCRIPT.panelId} .mcms-discord-stat { min-width:0 !important; padding:7px 5px !important; border-radius:8px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }#${SCRIPT.panelId} .mcms-discord-stat span { display:block !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:900 !important; text-transform:uppercase !important; letter-spacing:.5px !important; }#${SCRIPT.panelId} .mcms-discord-stat strong { display:block !important; margin-top:3px !important; color:#fff !important; font-size:10px !important; font-weight:950 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.panelId} .mcms-discord-breakdowns { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:6px !important; margin-top:7px !important; }#${SCRIPT.panelId} .mcms-discord-breakdown { min-width:0 !important; padding:7px !important; border-radius:8px !important; background:rgba(255,255,255,.04) !important; }#${SCRIPT.panelId} .mcms-discord-breakdown b { display:block !important; margin-bottom:4px !important; color:#bbdefb !important; font-size:7.5px !important; text-transform:uppercase !important; letter-spacing:.55px !important; }#${SCRIPT.panelId} .mcms-discord-line { display:flex !important; justify-content:space-between !important; gap:5px !important; margin-top:3px !important; color:rgba(255,255,255,.68) !important; font-size:7.5px !important; }#${SCRIPT.panelId} .mcms-discord-line span { min-width:0 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-discord-line strong { color:#fff !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-discord-foot { margin-top:7px !important; padding-top:6px !important; border-top:1px solid rgba(255,255,255,.08) !important; color:rgba(255,255,255,.48) !important; font-size:7.5px !important; line-height:1.3 !important; }#${SCRIPT.panelId} .mcms-discord-status[data-tone="good"] { border-color:rgba(46,204,113,.38) !important; color:#9be8b8 !important; }#${SCRIPT.panelId} .mcms-discord-status[data-tone="bad"] { border-color:rgba(231,76,60,.42) !important; color:#ffaaa1 !important; }#${SCRIPT.panelId} .mcms-discord-status[data-tone="busy"] { border-color:rgba(52,152,219,.42) !important; color:#9bd5ff !important; }#${SCRIPT.panelId} .mcms-discord-mini-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:6px !important; }#${SCRIPT.panelId} .mcms-discord-mini-stats span { min-width:0 !important; padding:5px 4px !important; border-radius:7px !important; background:rgba(88,166,255,.07) !important; color:rgba(255,255,255,.52) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }#${SCRIPT.panelId} .mcms-discord-mini-stats b { display:block !important; margin-top:2px !important; color:#fff !important; font-size:7.8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-discord-chart { display:block !important; width:100% !important; margin-top:8px !important; border-radius:9px !important; border:1px solid rgba(255,255,255,.11) !important; background:#0b1018 !important; }#${SCRIPT.panelId} .mcms-discord-date-grid { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; }#${SCRIPT.panelId} .mcms-discord-date-grid .mcms-row { grid-template-columns:56px minmax(0,1fr) !important; }#${SCRIPT.panelId} .mcms-finance-vault-summary { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:5px !important; margin:7px 0 !important; }#${SCRIPT.panelId} .mcms-finance-vault-summary span { min-width:0 !important; padding:7px 5px !important; border:1px solid rgba(88,166,255,.18) !important; border-radius:8px !important; background:rgba(88,166,255,.055) !important; color:rgba(255,255,255,.54) !important; font-size:6.8px !important; font-weight:850 !important; text-align:center !important; text-transform:uppercase !important; letter-spacing:.3px !important; }#${SCRIPT.panelId} .mcms-finance-vault-summary b { display:block !important; margin-bottom:2px !important; color:#fff !important; font-size:8px !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-finance-vault-summary small { grid-column:1/-1 !important; padding:5px 7px !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; color:rgba(255,255,255,.48) !important; font-size:7.2px !important; line-height:1.35 !important; text-align:center !important; }#${SCRIPT.panelId} .mcms-finance-private-note { border-color:rgba(241,196,15,.34) !important; color:#f5d984 !important; }#${SCRIPT.panelId} .mcms-sweep-card { margin-top:8px !important; padding:8px !important; border-radius:9px !important; border:1px solid rgba(255,183,72,.28) !important; background:rgba(88,46,4,.13) !important; }#${SCRIPT.panelId} .mcms-sweep-head { display:flex !important; justify-content:space-between !important; align-items:center !important; gap:8px !important; color:#ffe0a3 !important; font-size:9px !important; font-weight:950 !important; }#${SCRIPT.panelId} .mcms-sweep-state { padding:2px 6px !important; border-radius:999px !important; background:rgba(255,255,255,.10) !important; color:rgba(255,255,255,.78) !important; font-size:7px !important; letter-spacing:.35px !important; }#${SCRIPT.panelId} .mcms-sweep-state.mcms-running { background:rgba(255,145,24,.28) !important; color:#fff1cf !important; }#${SCRIPT.panelId} .mcms-sweep-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:7px !important; }#${SCRIPT.panelId} .mcms-sweep-stat { min-width:0 !important; padding:5px 3px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }#${SCRIPT.panelId} .mcms-sweep-stat b { display:block !important; color:#fff !important; font-size:11px !important; line-height:1 !important; }#${SCRIPT.panelId} .mcms-sweep-stat span { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.50) !important; font-size:6.5px !important; font-weight:900 !important; text-transform:uppercase !important; }#${SCRIPT.panelId} .mcms-sweep-queue { display:grid !important; gap:4px !important; max-height:128px !important; overflow-y:auto !important; margin-top:7px !important; padding-right:2px !important; overscroll-behavior:contain !important; scrollbar-width:thin !important; }#${SCRIPT.panelId} .mcms-sweep-entry { display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:6px !important; padding:6px !important; border-radius:7px !important; border:1px solid rgba(255,255,255,.08) !important; background:rgba(255,255,255,.04) !important; }#${SCRIPT.panelId} .mcms-sweep-entry.mcms-current { border-color:rgba(255,177,57,.62) !important; background:rgba(255,145,24,.11) !important; }#${SCRIPT.panelId} .mcms-sweep-title { min-width:0 !important; color:#f7f8fb !important; font-size:8.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.panelId} .mcms-sweep-meta { display:block !important; margin-top:2px !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:800 !important; }#${SCRIPT.panelId} .mcms-sweep-count { color:#ffc86b !important; font-size:9px !important; font-weight:950 !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-sweep-log { max-height:72px !important; overflow-y:auto !important; margin-top:7px !important; padding:6px !important; border-radius:7px !important; background:rgba(0,0,0,.18) !important; color:rgba(255,255,255,.64) !important; font:700 7px/1.35 Arial,Helvetica,sans-serif !important; white-space:normal !important; }#${SCRIPT.transportSweepHudId} { position:fixed !important; top:max(12px,env(safe-area-inset-top)) !important; right:max(12px,env(safe-area-inset-right)) !important; z-index:2147482000 !important; width:min(340px,calc(100vw - 24px)) !important; padding:11px !important; border:1px solid rgba(255,184,72,.72) !important; border-radius:12px !important; background:linear-gradient(145deg,rgba(18,23,31,.97),rgba(34,22,8,.97)) !important; color:#f8fbff !important; box-shadow:0 18px 55px rgba(0,0,0,.55),0 0 0 1px rgba(255,184,72,.08) inset !important; font:800 11px/1.25 Arial,Helvetica,sans-serif !important; pointer-events:none !important; touch-action:none !important; user-select:none !important; backdrop-filter:blur(12px) !important; -webkit-backdrop-filter:blur(12px) !important; }#${SCRIPT.transportSweepHudId}[data-state="complete"] { border-color:rgba(70,229,139,.78) !important; background:linear-gradient(145deg,rgba(12,29,25,.98),rgba(8,47,31,.97)) !important; }#${SCRIPT.transportSweepHudId}[data-state="error"] { border-color:rgba(255,100,108,.82) !important; background:linear-gradient(145deg,rgba(35,17,21,.98),rgba(54,12,18,.97)) !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head { display:flex !important; align-items:center !important; justify-content:space-between !important; gap:10px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head span { min-width:0 !important; display:flex !important; align-items:center !important; gap:7px !important; color:#ffe3ad !important; font-size:11px !important; font-weight:950 !important; letter-spacing:.15px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head i { width:8px !important; height:8px !important; flex:0 0 8px !important; border-radius:50% !important; background:#ffb648 !important; box-shadow:0 0 0 4px rgba(255,182,72,.13),0 0 12px rgba(255,182,72,.58) !important; }#${SCRIPT.transportSweepHudId}[data-state="complete"] .mcms-sweep-hud-head i { background:#46e58b !important; box-shadow:0 0 0 4px rgba(70,229,139,.13),0 0 12px rgba(70,229,139,.58) !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-head b { flex:0 0 auto !important; padding:3px 7px !important; border-radius:999px !important; background:rgba(255,255,255,.09) !important; color:rgba(255,255,255,.74) !important; font-size:7px !important; font-weight:950 !important; text-transform:uppercase !important; letter-spacing:.45px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-status { margin-top:9px !important; color:#fff !important; font-size:10px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-current { margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:8px !important; font-weight:750 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:5px !important; margin-top:9px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats span { min-width:0 !important; padding:7px 4px !important; border-radius:8px !important; background:rgba(255,255,255,.055) !important; text-align:center !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats b { display:block !important; color:#fff !important; font-size:13px !important; line-height:1 !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats small { display:block !important; margin-top:4px !important; color:rgba(255,255,255,.48) !important; font-size:6.4px !important; font-weight:950 !important; text-transform:uppercase !important; letter-spacing:.25px !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-cleared { background:rgba(70,229,139,.15) !important; box-shadow:0 0 0 1px rgba(70,229,139,.24) inset !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-cleared b { color:#73f2ab !important; font-size:17px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-foot { display:flex !important; justify-content:space-between !important; gap:8px !important; margin-top:8px !important; padding-top:7px !important; border-top:1px solid rgba(255,255,255,.09) !important; color:rgba(255,255,255,.42) !important; font-size:7px !important; font-weight:850 !important; text-transform:uppercase !important; letter-spacing:.25px !important; }
        #${SCRIPT.panelId} .mcms-sweep-last-report { margin-top:8px !important; padding:9px !important; border:1px solid rgba(70,229,139,.42) !important; border-radius:10px !important; background:linear-gradient(145deg,rgba(14,40,31,.38),rgba(12,23,29,.54)) !important; }#${SCRIPT.panelId} .mcms-sweep-last-report[data-tone="partial"] { border-color:rgba(255,182,72,.46) !important; background:linear-gradient(145deg,rgba(49,32,10,.38),rgba(12,23,29,.54)) !important; }#${SCRIPT.panelId} .mcms-sweep-last-report[data-tone="error"] { border-color:rgba(255,100,108,.48) !important; background:linear-gradient(145deg,rgba(49,17,22,.38),rgba(12,23,29,.54)) !important; }#${SCRIPT.panelId} .mcms-sweep-last-report[data-tone="stopped"] { border-color:rgba(149,165,166,.45) !important; }#${SCRIPT.panelId} .mcms-sweep-report-summary { margin-top:7px !important; color:#f7fbff !important; font-size:9px !important; font-weight:900 !important; line-height:1.3 !important; }#${SCRIPT.panelId} .mcms-sweep-report-grid { display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:4px !important; margin-top:7px !important; }#${SCRIPT.panelId} .mcms-sweep-report-grid span { min-width:0 !important; padding:6px 3px !important; border-radius:7px !important; background:rgba(255,255,255,.055) !important; color:rgba(255,255,255,.50) !important; font-size:6.5px !important; font-weight:900 !important; text-align:center !important; text-transform:uppercase !important; }#${SCRIPT.panelId} .mcms-sweep-report-grid b { display:block !important; margin-bottom:3px !important; color:#fff !important; font-size:11px !important; line-height:1 !important; }#${SCRIPT.panelId} .mcms-sweep-report-meta { display:flex !important; justify-content:space-between !important; gap:8px !important; margin-top:7px !important; color:rgba(255,255,255,.52) !important; font-size:7px !important; font-weight:850 !important; }#${SCRIPT.panelId} .mcms-sweep-report-meta span[data-tone="good"] { color:#73f2ab !important; }#${SCRIPT.panelId} .mcms-sweep-report-meta span[data-tone="bad"] { color:#ff8b92 !important; }#${SCRIPT.panelId} .mcms-sweep-report-meta span[data-tone="busy"] { color:#8bd3ff !important; }#${SCRIPT.panelId} .mcms-sweep-report-actions { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:5px !important; margin-top:7px !important; }#${SCRIPT.panelId} .mcms-sweep-report-actions > :only-child { grid-column:1/-1 !important; }#${SCRIPT.transportSweepHudId}[data-state="partial"] { border-color:rgba(255,182,72,.82) !important; background:linear-gradient(145deg,rgba(35,25,10,.98),rgba(54,31,8,.97)) !important; }#${SCRIPT.transportSweepHudId}[data-state="stopped"] { border-color:rgba(149,165,166,.78) !important; background:linear-gradient(145deg,rgba(24,29,31,.98),rgba(34,39,41,.97)) !important; }#${SCRIPT.transportSweepHudId}[data-final="true"] { pointer-events:auto !important; touch-action:auto !important; user-select:auto !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions { display:flex !important; align-items:center !important; justify-content:space-between !important; gap:8px !important; margin-top:8px !important; padding-top:8px !important; border-top:1px solid rgba(255,255,255,.09) !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions > span { min-width:0 !important; color:rgba(255,255,255,.58) !important; font-size:7px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions > span[data-tone="good"] { color:#73f2ab !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions > span[data-tone="bad"] { color:#ff8b92 !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions > span[data-tone="busy"] { color:#8bd3ff !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions > div { display:flex !important; gap:5px !important; flex:0 0 auto !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions button { min-height:26px !important; padding:4px 8px !important; border:1px solid rgba(255,255,255,.18) !important; border-radius:7px !important; background:rgba(255,255,255,.08) !important; color:#fff !important; cursor:pointer !important; font:900 7px/1 Arial,Helvetica,sans-serif !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions button:hover { background:rgba(255,255,255,.16) !important; }
        @media (max-width:700px) {#${SCRIPT.transportSweepHudId} { top:auto !important; right:max(8px,env(safe-area-inset-right)) !important; bottom:max(8px,env(safe-area-inset-bottom)) !important; left:max(8px,env(safe-area-inset-left)) !important; width:auto !important; padding:9px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-current { display:none !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-stats { gap:3px !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions { align-items:flex-end !important; }#${SCRIPT.transportSweepHudId} .mcms-sweep-hud-actions > span { white-space:normal !important; }
        }#${SCRIPT.panelId} .mcms-footer { margin: 9px 0 0 0 !important; padding: 7px 0 0 0 !important; border-top: 1px solid rgba(255,255,255,.10) !important; color: rgba(233,238,245,.58) !important; font-size: 9px !important; line-height: 1.25 !important; overflow: hidden !important; }#${SCRIPT.panelId} .mcms-build { display: block !important; margin-top: 4px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }.mcms-mission-float-pane,
        .mcms-mission-float-pane * {
            pointer-events: none !important;
            touch-action: none !important;
        }.mcms-alliance-credit-icon,
        .mcms-mission-age-icon,
        .mcms-unit-commitment-icon,
        .mcms-transport-watcher-icon,
        .mcms-resource-gap-icon {
            width: 0 !important; height: 0 !important; overflow: visible !important;
            border: 0 !important; background: transparent !important;
            pointer-events: none !important; touch-action: none !important;
        }.mcms-alliance-credit-badge,
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
        }.mcms-alliance-credit-badge {
            min-width: 48px !important; height: 22px !important; padding: 0 7px !important; border-radius: 8px !important;
            border: 1px solid rgba(255,213,79,.46) !important; background: rgba(10,14,20,.46) !important;
            color: #ffe082 !important; box-shadow: 0 2px 7px rgba(0,0,0,.18) !important;
            font: 900 10px/1 Arial, Helvetica, sans-serif !important; letter-spacing: .1px !important;
        }.mcms-alliance-credit-badge.mcms-credit-qualified {
            border-color: rgba(76,225,126,.52) !important;
            color: #79f2a3 !important;
            text-shadow: 0 1px 2px rgba(0,0,0,.88), 0 0 5px rgba(44,210,103,.20) !important;
        }.mcms-alliance-credit-badge.mcms-credit-unqualified {
            border-color: rgba(255,213,79,.46) !important;
            color: #ffe082 !important;
        }.mcms-mission-age-badge {
            min-width: 38px !important; height: 20px !important; padding: 0 6px !important; border-radius: 7px !important;
            border: 1px solid rgba(100,181,246,.48) !important; background: rgba(10,14,20,.66) !important;
            color: #c8e6ff !important; box-shadow: 0 2px 7px rgba(0,0,0,.22) !important;
            font: 900 9.5px/1 Arial, Helvetica, sans-serif !important; letter-spacing: .1px !important;
            transition: color .18s ease, border-color .18s ease, background-color .18s ease, box-shadow .18s ease !important;
        }.mcms-mission-age-badge.mcms-age-aged {
            border-color: rgba(255,202,40,.88) !important;
            background: rgba(74,52,3,.88) !important;
            color: #fff0a8 !important;
            box-shadow: 0 2px 7px rgba(0,0,0,.28), 0 0 8px rgba(255,193,7,.30) !important;
        }.mcms-mission-age-badge.mcms-age-high {
            border-color: rgba(255,133,46,.96) !important;
            background: rgba(88,34,4,.92) !important;
            color: #ffd0a3 !important;
            box-shadow: 0 2px 7px rgba(0,0,0,.30), 0 0 10px rgba(255,111,0,.42) !important;
        }.mcms-mission-age-badge.mcms-age-critical {
            border-color: rgba(255,72,72,1) !important;
            background: rgba(102,8,12,.95) !important;
            color: #ffe3e3 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,.34), 0 0 12px rgba(255,45,45,.58) !important;
            text-shadow: 0 1px 2px rgba(0,0,0,.90), 0 0 5px rgba(255,104,104,.42) !important;
        }.mcms-unit-commitment-badge {
            min-width: 42px !important; height: 18px !important; padding: 0 6px !important; border-radius: 7px !important;
            border: 1px solid rgba(255,255,255,.42) !important; background: rgba(10,14,20,.46) !important;
            color: #f4f7ff !important; box-shadow: 0 2px 7px rgba(0,0,0,.18) !important;
            font: 900 8.5px/1 Arial, Helvetica, sans-serif !important; letter-spacing: .15px !important;
        }.mcms-unit-commitment-badge.mcms-unit-personal { border-color: rgba(244,200,79,.54) !important; color: #ffe082 !important; }.mcms-unit-commitment-badge.mcms-unit-alliance { border-color: rgba(76,225,126,.54) !important; color: #79f2a3 !important; }.mcms-transport-watcher-badge {
            width: 25px !important; height: 25px !important; padding: 0 !important; border-radius: 8px !important;
            border: 1px solid rgba(255,193,74,.94) !important; background: linear-gradient(145deg, rgba(86,46,3,.96), rgba(27,17,6,.96)) !important;
            color: #ffe4a8 !important; box-shadow: 0 0 0 2px rgba(0,0,0,.48), 0 0 11px rgba(255,145,24,.55) !important;
            font: 950 9px/1 Arial, Helvetica, sans-serif !important; overflow: visible !important;
            animation: mcmsTransportWatcherPulse 1.85s ease-in-out infinite !important;
        }.mcms-transport-watcher-badge svg { width: 17px !important; height: 17px !important; display:block !important; overflow:visible !important; }.mcms-transport-watcher-badge svg * { vector-effect: non-scaling-stroke !important; }.mcms-transport-watcher-badge.mcms-transport-patient { border-color: rgba(255,194,71,.96) !important; color:#fff1c7 !important; }.mcms-transport-watcher-badge.mcms-transport-prisoner { border-color: rgba(255,139,53,.98) !important; color:#ffd0a5 !important; background:linear-gradient(145deg,rgba(91,35,4,.97),rgba(28,12,4,.97)) !important; }.mcms-transport-watcher-count { position:absolute !important; right:-7px !important; top:-7px !important; min-width:15px !important; height:15px !important; padding:0 3px !important; border-radius:999px !important; border:1px solid rgba(255,255,255,.86) !important; background:#e67600 !important; color:#fff !important; font:950 8px/13px Arial,Helvetica,sans-serif !important; text-align:center !important; box-shadow:0 1px 4px rgba(0,0,0,.65) !important; }.mcms-transport-watcher-badge.mcms-transport-side-left .mcms-transport-watcher-count { left:-7px !important; right:auto !important; }
        @keyframes mcmsTransportWatcherPulse { 0%,100%{transform:translate(-50%,-50%) scale(1);box-shadow:0 0 0 2px rgba(0,0,0,.48),0 0 8px rgba(255,145,24,.38)} 50%{transform:translate(-50%,-50%) scale(1.08);box-shadow:0 0 0 2px rgba(0,0,0,.55),0 0 16px rgba(255,145,24,.82)} }
        @media (prefers-reduced-motion: reduce) {.mcms-transport-watcher-badge { animation:none !important; } }.mcms-resource-gap-badge {
            min-width: 31px !important; height: 19px !important; padding: 0 6px !important; border-radius: 7px !important;
            border: 1px solid rgba(255,146,49,.88) !important; background: rgba(48,20,3,.91) !important; color: #ffd29a !important;
            box-shadow: 0 0 0 2px rgba(0,0,0,.38), 0 2px 8px rgba(255,112,20,.27) !important;
            font: 950 8.5px/1 Arial,Helvetica,sans-serif !important; letter-spacing:.1px !important;
        }.mcms-resource-gap-badge.mcms-gap-uncovered { border-color:#ff574d !important; color:#fff !important; background:rgba(91,11,7,.94) !important; box-shadow:0 0 0 2px rgba(0,0,0,.42),0 0 11px rgba(255,45,35,.46) !important; }#${SCRIPT.panelId} .mcms-ops-session-grid {
            display: grid !important; grid-template-columns: repeat(2,minmax(0,1fr)) !important; gap: 6px !important;
        }#${SCRIPT.panelId} .mcms-ops-stat {
            min-width: 0 !important; padding: 8px !important; border-radius: 9px !important;
            border: 1px solid rgba(255,255,255,.11) !important; background: rgba(255,255,255,.055) !important;
        }#${SCRIPT.panelId} .mcms-ops-stat-label { display:block !important; color:rgba(255,255,255,.56) !important; font-size:7.5px !important; font-weight:900 !important; text-transform:uppercase !important; letter-spacing:.45px !important; }#${SCRIPT.panelId} .mcms-ops-stat-value { display:block !important; margin-top:4px !important; color:#fff !important; font-size:13px !important; line-height:1 !important; font-weight:950 !important; overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-ops-list { display:grid !important; gap:5px !important; }#${SCRIPT.panelId} .mcms-ops-entry {
            display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:7px !important; align-items:center !important;
            padding:7px !important; border-radius:8px !important; border:1px solid rgba(255,255,255,.10) !important; background:rgba(255,255,255,.045) !important;
        }#${SCRIPT.panelId} .mcms-ops-entry-main { min-width:0 !important; }#${SCRIPT.panelId} .mcms-ops-entry-title { display:block !important; color:#f5f7ff !important; font-size:9.5px !important; font-weight:900 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.panelId} .mcms-ops-entry-meta { display:block !important; margin-top:3px !important; color:rgba(255,255,255,.58) !important; font-size:7.5px !important; font-weight:800 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important; }#${SCRIPT.panelId} .mcms-ops-entry-value { color:#ffe082 !important; font-size:10px !important; font-weight:950 !important; white-space:nowrap !important; }#${SCRIPT.panelId} .mcms-history-latest { display:grid !important; gap:5px !important; }#${SCRIPT.panelId} .mcms-history-older {
            margin-top:2px !important; border:1px solid rgba(255,255,255,.11) !important; border-radius:8px !important;
            background:rgba(255,255,255,.035) !important; overflow:hidden !important;
        }#${SCRIPT.panelId} .mcms-history-older > summary {
            display:block !important; padding:7px 9px !important; cursor:pointer !important; list-style:none !important;
            color:rgba(255,255,255,.68) !important; font-size:8px !important; font-weight:900 !important; letter-spacing:.35px !important; text-transform:uppercase !important;
            user-select:none !important;
        }#${SCRIPT.panelId} .mcms-history-older > summary::-webkit-details-marker { display:none !important; }#${SCRIPT.panelId} .mcms-history-older > summary::after { content:'‚ñæ' !important; float:right !important; color:rgba(255,255,255,.48) !important; }#${SCRIPT.panelId} .mcms-history-older:not([open]) > summary::after { content:'‚ñ∏' !important; }#${SCRIPT.panelId} .mcms-history-scroll {
            display:grid !important; gap:5px !important; max-height:126px !important; overflow-y:auto !important; overscroll-behavior:contain !important;
            padding:0 5px 5px !important; scrollbar-width:thin !important;
        }#${SCRIPT.panelId} .mcms-empty-state { padding:10px !important; border:1px dashed rgba(255,255,255,.12) !important; border-radius:8px !important; color:rgba(255,255,255,.52) !important; font-size:8.5px !important; text-align:center !important; }#${SCRIPT.payoutFlashId} {
            position: absolute !important; inset: 0 !important; width: 100% !important; height: 100% !important;
            z-index: 625 !important; overflow: hidden !important;
            pointer-events: none !important; opacity: 0 !important;
            isolation: isolate !important;
        }#${SCRIPT.payoutFlashId}.mcms-payout-active { opacity: 1 !important; }#${SCRIPT.payoutFlashId},
        #${SCRIPT.payoutFlashId} * {
            box-sizing: border-box !important; pointer-events: none !important; user-select: none !important;
            font-family: Arial, Helvetica, sans-serif !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-light {
            position: absolute !important; inset: -12% !important; opacity: 0;
            will-change: opacity, transform !important; mix-blend-mode: screen !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-red {
            background:
                radial-gradient(ellipse at 0% 45%, rgba(255,22,22,.62) 0%, rgba(255,22,22,.30) 25%, rgba(255,22,22,0) 62%),
                linear-gradient(90deg, rgba(255,18,18,.34) 0%, rgba(255,18,18,0) 48%) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-blue {
            background:
                radial-gradient(ellipse at 100% 55%, rgba(25,113,255,.68) 0%, rgba(25,113,255,.32) 25%, rgba(25,113,255,0) 62%),
                linear-gradient(270deg, rgba(20,103,255,.38) 0%, rgba(20,103,255,0) 48%) !important;
        }#${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-red {
            animation: mcmsPayoutRed var(--mcms-payout-duration, 3000ms) ease-in-out both !important;
        }#${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-blue {
            animation: mcmsPayoutBlue var(--mcms-payout-duration, 3000ms) ease-in-out both !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-cinematic {
            position: absolute !important; inset: 0 !important; opacity: 0;
            background:
                radial-gradient(ellipse at center, rgba(0,0,0,0) 25%, rgba(0,0,0,.18) 72%, rgba(0,0,0,.38) 100%),
                linear-gradient(180deg, rgba(0,0,0,.22) 0%, rgba(0,0,0,0) 24%, rgba(0,0,0,0) 76%, rgba(0,0,0,.22) 100%) !important;
            will-change: opacity !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-banner {
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
        }#${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-banner {
            animation: mcmsPayoutBanner var(--mcms-payout-duration, 3000ms) cubic-bezier(.16,.78,.24,1) both !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-title {
            display: block !important; color: var(--mcms-payout-accent, #f4c84f) !important;
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", "Arial Black", sans-serif !important;
            font-size: clamp(34px, 5.4vw, 64px) !important; line-height: .92 !important; font-weight: 900 !important;
            letter-spacing: 1.9px !important; text-transform: uppercase !important; white-space: nowrap !important;
            text-shadow: 0 3px 0 rgba(0,0,0,.78), 0 5px 18px rgba(0,0,0,.74), 0 0 18px var(--mcms-payout-glow, rgba(244,200,79,.16)) !important;
            transform: scaleX(.94) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-divider {
            display: block !important; width: min(390px, 78%) !important; height: 1px !important;
            margin: 11px auto 9px !important;
            background: linear-gradient(90deg, transparent, var(--mcms-payout-accent, #f4c84f) 24%, rgba(255,255,255,.90) 50%, var(--mcms-payout-accent, #f4c84f) 76%, transparent) !important;
            box-shadow: 0 0 8px rgba(244,200,79,.24) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-particles {
            position:absolute !important; inset:0 !important; opacity:0; transform:scale(1.04);
            background-image:
                radial-gradient(circle at 18% 34%, var(--mcms-payout-accent, #f4c84f) 0 1px, transparent 2px),
                radial-gradient(circle at 32% 68%, var(--mcms-payout-accent, #f4c84f) 0 1.5px, transparent 2.5px),
                radial-gradient(circle at 61% 27%, #fff 0 1px, transparent 2px),
                radial-gradient(circle at 78% 61%, var(--mcms-payout-accent, #f4c84f) 0 1.4px, transparent 2.4px),
                radial-gradient(circle at 89% 42%, #fff 0 1px, transparent 2px);
            background-size:190px 150px,230px 170px,270px 210px,310px 190px,350px 230px !important;
            mix-blend-mode:screen !important; pointer-events:none !important;
        }#${SCRIPT.payoutFlashId}[data-tier="high"] .mcms-payout-particles,
        #${SCRIPT.payoutFlashId}[data-tier="elite"] .mcms-payout-particles { opacity:.34; }#${SCRIPT.payoutFlashId}[data-tier="elite"] .mcms-payout-particles { opacity:.52; }#${SCRIPT.payoutFlashId} .mcms-payout-tier {
            display:inline-block !important; margin-bottom:7px !important; padding:3px 8px !important; border-radius:999px !important;
            border:1px solid var(--mcms-payout-accent-soft, rgba(247,205,83,.42)) !important; background:rgba(0,0,0,.28) !important;
            color:var(--mcms-payout-accent, #f4c84f) !important; font-size:7.5px !important; line-height:1 !important; font-weight:950 !important;
            letter-spacing:1.6px !important; text-transform:uppercase !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-mission {
            display:block !important; margin-top:8px !important; color:#fff !important;
            font-size:clamp(12px,2vw,18px) !important; line-height:1.05 !important; font-weight:950 !important;
            white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;
            text-shadow:0 2px 8px rgba(0,0,0,.85) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-mission:empty { display:none !important; }#${SCRIPT.payoutFlashId} .mcms-payout-source {
            display:block !important; margin-top:5px !important; color:var(--mcms-payout-accent, #f4c84f) !important;
            font-size:8px !important; line-height:1 !important; font-weight:950 !important; letter-spacing:2px !important; text-transform:uppercase !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-kicker {
            display: block !important; color: rgba(255,255,255,.78) !important;
            font-family: "Arial Narrow", Arial, Helvetica, sans-serif !important;
            font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important;
            letter-spacing: 3px !important; text-transform: uppercase !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-amount {
            display: block !important; margin-top: 7px !important; color: #fff !important;
            font-family: "Arial Black", "Arial Narrow Bold", Arial, Helvetica, sans-serif !important;
            font-size: clamp(20px, 3vw, 32px) !important; line-height: 1 !important; font-weight: 950 !important;
            letter-spacing: 1.5px !important; white-space: nowrap !important;
            text-shadow: 0 2px 0 rgba(0,0,0,.74), 0 5px 15px rgba(0,0,0,.68) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-vc-sunset,
        #${SCRIPT.payoutFlashId} .mcms-payout-vc-grid {
            position: absolute !important; inset: 0 !important; opacity: 0;
            pointer-events: none !important; will-change: opacity, transform !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-vc-sunset {
            background:
                radial-gradient(circle at 50% 54%, rgba(255,238,104,.92) 0 5%, rgba(255,132,160,.58) 5.5% 11%, rgba(255,71,180,.24) 12% 25%, transparent 39%),
                linear-gradient(180deg, rgba(17,9,62,.76) 0%, rgba(85,19,112,.64) 34%, rgba(241,48,142,.34) 60%, rgba(5,17,50,.72) 100%) !important;
            mix-blend-mode: screen !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-vc-grid {
            top: 56% !important;
            background:
                repeating-linear-gradient(90deg, rgba(44,238,255,.24) 0 1px, transparent 1px 54px),
                repeating-linear-gradient(180deg, rgba(255,70,201,.22) 0 1px, transparent 1px 32px) !important;
            transform-origin: 50% 0 !important;
            transform: perspective(380px) rotateX(62deg) scale(1.35) !important;
            mask-image: linear-gradient(180deg, rgba(0,0,0,.82), transparent 76%) !important;
            -webkit-mask-image: linear-gradient(180deg, rgba(0,0,0,.82), transparent 76%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-cinematic {
            background:
                radial-gradient(ellipse at center, rgba(0,0,0,0) 18%, rgba(20,3,45,.20) 62%, rgba(4,3,20,.58) 100%),
                linear-gradient(180deg, rgba(9,3,33,.38), transparent 28%, transparent 72%, rgba(4,5,28,.52)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner {
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
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::after {
            content: "" !important; position: absolute !important; top: -7px !important; bottom: -7px !important;
            width: 2px !important; opacity: .75 !important; pointer-events: none !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::before {
            left: 9% !important; background: linear-gradient(180deg, transparent, #ff5ed8, transparent) !important;
            box-shadow: 0 0 13px #ff5ed8 !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::after {
            right: 9% !important; background: linear-gradient(180deg, transparent, #42e9ff, transparent) !important;
            box-shadow: 0 0 13px #42e9ff !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title {
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
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-divider {
            height: 2px !important; margin: 15px auto 11px !important;
            background: linear-gradient(90deg, transparent, #ff61d1 20%, #fff 48%, #4cecff 78%, transparent) !important;
            box-shadow: 0 0 9px rgba(255,72,202,.54), 0 0 14px rgba(54,228,255,.42) !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-tier {
            border-color: rgba(255,91,210,.72) !important;
            background: rgba(19,4,52,.60) !important;
            color: #72efff !important;
            box-shadow: 0 0 10px rgba(255,75,203,.22), inset 0 0 8px rgba(69,228,255,.10) !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-mission {
            color: #fff4fb !important; font-style: italic !important;
            text-shadow: 0 2px 8px #090318, 0 0 10px rgba(255,70,196,.28) !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-source {
            color: var(--mcms-payout-accent, #77f2ff) !important;
            text-shadow: 0 0 9px var(--mcms-payout-glow, rgba(80,234,255,.34)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-kicker {
            color: #ff9bde !important; letter-spacing: 4px !important;
        }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-amount {
            color: #f8ffff !important;
            font-style: italic !important;
            text-shadow:
                2px 2px 0 #e63fae,
                4px 4px 0 rgba(7,16,52,.94),
                0 0 12px rgba(67,231,255,.56) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-bc-dust,
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-hud,
        #${SCRIPT.payoutFlashId} .mcms-payout-bc-embers {
            position: absolute !important; inset: 0 !important; opacity: 0;
            pointer-events: none !important; will-change: opacity, transform, background-position !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-bc-dust {
            background:
                radial-gradient(ellipse at 50% 105%, rgba(255,114,15,.42) 0 8%, rgba(135,61,14,.22) 24%, transparent 53%),
                radial-gradient(circle at 14% 74%, rgba(255,153,43,.22) 0 3%, rgba(90,76,48,.18) 15%, transparent 35%),
                radial-gradient(circle at 86% 28%, rgba(213,222,188,.14) 0 4%, rgba(65,73,54,.24) 18%, transparent 40%),
                radial-gradient(ellipse at 50% 52%, rgba(160,156,122,.12) 0 14%, rgba(26,31,23,.34) 48%, rgba(4,6,5,.70) 100%),
                repeating-radial-gradient(circle at 37% 44%, rgba(255,255,255,.028) 0 1px, transparent 1px 7px) !important;
            filter: contrast(126%) saturate(88%) !important;
            mix-blend-mode: screen !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-bc-hud {
            background:
                linear-gradient(90deg, transparent 0 5.5%, rgba(255,151,28,.30) 5.5% 5.72%, transparent 5.72% 94.28%, rgba(255,151,28,.30) 94.28% 94.5%, transparent 94.5%),
                linear-gradient(180deg, transparent 0 12%, rgba(224,232,208,.10) 12% 12.2%, transparent 12.2% 87.8%, rgba(224,232,208,.08) 87.8% 88%, transparent 88%),
                repeating-linear-gradient(0deg, rgba(224,232,208,.035) 0 1px, transparent 1px 5px),
                repeating-linear-gradient(118deg, transparent 0 42px, rgba(255,151,30,.048) 42px 44px, transparent 44px 88px) !important;
            mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0,0,0,.86) 64%, transparent 100%) !important;
            -webkit-mask-image: radial-gradient(ellipse at center, #000 8%, rgba(0,0,0,.86) 64%, transparent 100%) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-bc-embers {
            overflow: hidden !important;
            mix-blend-mode: screen !important;
            filter: saturate(125%) contrast(110%) !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-bc-ember {
            position: absolute !important;
            left: 50%; bottom: -18px;
            width: 3px; height: 9px;
            border-radius: 999px !important;
            opacity: 0;
            background: linear-gradient(180deg, #fff7bb 0%, #ffc14e 28%, #ff6d12 72%, rgba(154,24,0,0) 100%) !important;
            box-shadow: 0 0 5px rgba(255,200,83,.95), 0 0 12px rgba(255,92,16,.78), 0 0 22px rgba(255,66,0,.34) !important;
            transform-origin: 50% 100% !important;
            will-change: transform, opacity !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-cinematic {
            background:
                radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 10%, rgba(20,24,18,.16) 49%, rgba(2,4,3,.78) 100%),
                linear-gradient(180deg, rgba(12,17,11,.52), transparent 25%, transparent 68%, rgba(15,8,3,.72)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {
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
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::after {
            content: "" !important; position: absolute !important; pointer-events: none !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::before {
            left: 0 !important; right: 0 !important; top: 0 !important; height: 5px !important;
            background:
                repeating-linear-gradient(135deg, #ff941c 0 11px, #171a14 11px 22px),
                linear-gradient(90deg, rgba(255,145,27,.9), transparent) !important;
            box-shadow: 0 0 12px rgba(255,115,13,.26) !important;
            opacity: .94 !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::after {
            right: 17px !important; bottom: 11px !important; width: 92px !important; height: 10px !important;
            border-top: 2px solid rgba(255,145,25,.82) !important;
            border-bottom: 1px solid rgba(224,229,207,.24) !important;
            background: repeating-linear-gradient(90deg, rgba(255,145,25,.84) 0 6px, transparent 6px 11px) !important;
            filter: drop-shadow(0 0 5px rgba(255,112,10,.24)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title {
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
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-long {
            font-size: clamp(27px, 4.25vw, 49px) !important;
            letter-spacing: clamp(.3px, .16vw, 1.5px) !important;
            transform: skewX(-5deg) scaleX(.84) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-very-long {
            font-size: clamp(23px, 3.65vw, 42px) !important;
            white-space: normal !important;
            text-wrap: balance !important;
            line-height: .94 !important;
            transform: skewX(-4deg) scaleX(.88) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-divider {
            height: 3px !important; width: min(500px, 76%) !important; margin: 14px auto 10px !important;
            background:
                linear-gradient(90deg, transparent, #ff8e19 14%, #f4f1e4 45%, #747f68 75%, transparent) !important;
            box-shadow: 0 0 12px rgba(255,121,15,.28) !important;
            transform: skewX(-18deg) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-tier {
            border-radius: 1px !important;
            border-color: rgba(255,145,25,.78) !important;
            background: linear-gradient(90deg, rgba(255,125,15,.18), rgba(20,24,18,.60)) !important;
            color: #ffac43 !important;
            letter-spacing: 2.25px !important;
            box-shadow: inset 4px 0 0 rgba(255,139,21,.92), 0 0 10px rgba(255,111,9,.10) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-mission {
            color: #f3f2e9 !important;
            text-transform: uppercase !important;
            letter-spacing: .6px !important;
            font-family: "Arial Narrow", Arial, sans-serif !important;
            text-shadow: 0 2px 10px rgba(0,0,0,.96) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-source {
            color: #ff9421 !important; letter-spacing: 2.7px !important;
            text-shadow: 0 0 12px rgba(255,112,10,.32) !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-kicker {
            color: rgba(225,229,211,.64) !important; letter-spacing: 3.4px !important;
        }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-amount {
            color: #ff9b27 !important;
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif !important;
            font-size: clamp(23px, 3.25vw, 35px) !important;
            letter-spacing: 2px !important;
            text-shadow: 2px 2px 0 #11140e, 0 0 14px rgba(255,126,17,.36), 0 0 28px rgba(255,78,4,.12) !important;
        }
        @media (max-width: 620px) {#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {
                width: calc(100% - 16px) !important;
                padding: 21px 16px 19px !important;
            }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title {
                font-size: clamp(25px, 8vw, 39px) !important;
                letter-spacing: .5px !important;
                transform: skewX(-4deg) scaleX(.84) !important;
            }#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-title.mcms-payout-title-long {
                font-size: clamp(21px, 6.8vw, 33px) !important;
                white-space: normal !important;
                text-wrap: balance !important;
            }
        }#${SCRIPT.payoutFlashId} .mcms-payout-theme-fx,
        #${SCRIPT.payoutFlashId} .mcms-payout-theme-particles {
            position:absolute !important; inset:0 !important; opacity:0;
            pointer-events:none !important; overflow:hidden !important;
            will-change:opacity, transform, background-position, filter !important;
        }#${SCRIPT.payoutFlashId} .mcms-payout-theme-particles { mix-blend-mode:screen !important; }#${SCRIPT.payoutFlashId} .mcms-payout-theme-particle {
            position:absolute !important; opacity:0; pointer-events:none !important;
            will-change:opacity, transform !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-red {
            background:
                radial-gradient(ellipse at 10% 48%, rgba(154,5,14,.82) 0%, rgba(154,5,14,.36) 27%, transparent 64%),
                linear-gradient(90deg, rgba(4,4,4,.76) 0 49.2%, rgba(166,11,20,.22) 49.2% 51%, transparent 51%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-blue {
            background:
                radial-gradient(ellipse at 90% 52%, rgba(255,244,216,.46) 0%, rgba(219,178,87,.18) 31%, transparent 66%),
                linear-gradient(270deg, rgba(241,236,225,.28) 0 45%, rgba(164,12,20,.18) 49% 51%, transparent 55%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-cinematic {
            background:
                linear-gradient(90deg, rgba(0,0,0,.91) 0 49.35%, rgba(163,12,20,.78) 49.35% 50.65%, rgba(239,234,223,.80) 50.65% 100%),
                radial-gradient(ellipse at 50% 52%, transparent 10%, rgba(0,0,0,.24) 70%, rgba(0,0,0,.66) 100%) !important;
            mix-blend-mode:normal !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-a {
            background:
                radial-gradient(circle at 50% 71%, rgba(235,193,95,.32) 0 2%, transparent 2.5% 13%, rgba(235,193,95,.16) 13.5% 14%, transparent 14.5%),
                repeating-conic-gradient(from -18deg at 50% 71%, rgba(229,186,87,.12) 0 1deg, transparent 1deg 12deg),
                linear-gradient(90deg, rgba(0,0,0,.18) 0 49.25%, rgba(173,12,20,.40) 49.25% 50.75%, rgba(255,255,255,.05) 50.75% 100%) !important;
            mask-image:linear-gradient(180deg, transparent 0%, #000 15%, #000 88%, transparent 100%) !important;
            -webkit-mask-image:linear-gradient(180deg, transparent 0%, #000 15%, #000 88%, transparent 100%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-b {
            background:
                linear-gradient(108deg, transparent 0 46.8%, rgba(168,12,20,.78) 47% 47.7%, transparent 47.9% 100%),
                linear-gradient(72deg, transparent 0 52.2%, rgba(168,12,20,.36) 52.4% 52.8%, transparent 53% 100%),
                repeating-linear-gradient(0deg, rgba(230,193,106,.035) 0 1px, transparent 1px 7px),
                repeating-linear-gradient(90deg, rgba(230,193,106,.025) 0 1px, transparent 1px 96px) !important;
            opacity:.55;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-c {
            left:-22% !important; right:auto !important; width:45% !important;
            background:linear-gradient(100deg, transparent 0 42%, rgba(168,8,17,.10) 43%, rgba(204,20,29,.84) 48%, rgba(255,225,188,.42) 50%, rgba(152,5,13,.72) 52%, transparent 58% 100%) !important;
            filter:drop-shadow(0 0 15px rgba(181,12,21,.42)) !important;
            transform:skewX(-9deg) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {
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
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::before {
            content:"MIAMI  ‚Ä¢  POWER  ‚Ä¢  MONEY" !important;
            position:absolute !important; left:18px !important; top:10px !important;
            color:rgba(224,188,101,.68) !important;
            font:900 7px/1 "Arial Narrow",Arial,sans-serif !important;
            letter-spacing:2.6px !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::after {
            content:"THE WORLD IS YOURS" !important;
            position:absolute !important; right:-58px !important; top:50% !important;
            width:180px !important;
            transform:translateY(-50%) rotate(90deg) !important;
            color:rgba(82,14,18,.68) !important;
            font:950 7px/1 "Arial Narrow",Arial,sans-serif !important;
            letter-spacing:2.2px !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title {
            color:#f1e8d7 !important;
            font-family:Impact,Haettenschweiler,"Arial Narrow Bold","Arial Black",sans-serif !important;
            font-size:clamp(36px,5.8vw,70px) !important;
            letter-spacing:2.4px !important;
            transform:skewX(-3deg) scaleX(.92) !important;
            -webkit-text-stroke:1px rgba(214,171,77,.82) !important;
            text-shadow:3px 3px 0 #120405,6px 6px 0 #8d0b13,0 0 22px rgba(220,179,84,.20) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title.mcms-payout-title-long {
            font-size:clamp(31px,5vw,59px) !important; letter-spacing:1.6px !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title.mcms-payout-title-very-long {
            font-size:clamp(27px,4.4vw,52px) !important; letter-spacing:1px !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-divider {
            height:3px !important; width:min(440px,82%) !important;
            background:linear-gradient(90deg,transparent,#9f0c15 13%,#d9b259 34%,#fff8e8 50%,#d9b259 66%,#9f0c15 87%,transparent) !important;
            box-shadow:0 0 11px rgba(173,15,24,.48),0 0 20px rgba(219,181,91,.20) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-tier {
            border-radius:0 !important; border:1px solid #cda954 !important;
            color:#f0d68d !important; background:rgba(15,5,5,.78) !important;
            box-shadow:inset 4px 0 0 #a70d16 !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-mission {
            color:#fff8ea !important; letter-spacing:.25px !important;
            text-shadow:0 2px 0 #000,0 0 9px #000 !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-source {
            color:#d7b45f !important; text-shadow:0 1px 0 #000,0 0 6px #000 !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-kicker {
            color:#bd2630 !important; font-weight:950 !important; letter-spacing:3.2px !important;
            text-shadow:0 1px 0 #000,0 0 6px rgba(0,0,0,.8) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-amount {
            color:#f2d27d !important;
            font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important;
            font-size:clamp(25px,3.55vw,39px) !important;
            letter-spacing:2.2px !important;
            -webkit-text-stroke:.5px rgba(83,12,16,.55) !important;
            text-shadow:2px 2px 0 #120405,4px 4px 0 #8c0a12,0 0 18px rgba(225,184,89,.36) !important;
        }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-particle {
            border-radius:0 !important;
            background:#f5e8be !important;
            box-shadow:0 0 5px #fff7d7,0 0 12px rgba(218,176,79,.78) !important;
            transform:rotate(45deg);
        }
        @media (max-width:620px) {#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {
                width:calc(100% - 16px) !important; padding:25px 19px 21px !important;
                background:linear-gradient(90deg,rgba(5,5,5,.985) 0 76%,rgba(234,228,215,.97) 76% 100%) !important;
            }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-title {
                font-size:clamp(29px,8.2vw,47px) !important; letter-spacing:1px !important; transform:skewX(-2deg) scaleX(.88) !important;
            }#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::after { display:none !important; }
        }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-cinematic {
            background:radial-gradient(ellipse at 52% 48%, transparent 8%, rgba(0,12,18,.22) 52%, rgba(0,0,0,.86) 100%), linear-gradient(115deg, rgba(245,226,0,.12), transparent 35%, rgba(0,229,255,.10)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-a {
            background:linear-gradient(112deg, rgba(247,229,0,.18) 0 2%, transparent 2% 9%, rgba(247,229,0,.08) 9% 10%, transparent 10% 88%, rgba(0,229,255,.12) 88% 90%, transparent 90%), repeating-linear-gradient(135deg, transparent 0 34px, rgba(247,229,0,.045) 34px 36px, transparent 36px 70px) !important;
        }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-b {
            background:repeating-linear-gradient(0deg, rgba(255,255,255,.035) 0 1px, transparent 1px 4px), repeating-linear-gradient(90deg, transparent 0 78px, rgba(0,229,255,.055) 78px 80px, transparent 80px 156px) !important;
            mix-blend-mode:screen !important;
        }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-c {
            background:radial-gradient(circle at 50% 50%, rgba(0,229,255,.13) 0 2%, transparent 3% 17%, rgba(247,229,0,.10) 18% 18.5%, transparent 19% 35%, rgba(0,229,255,.06) 36% 36.5%, transparent 37%), conic-gradient(from 35deg at 50% 50%, transparent 0 12%, rgba(247,229,0,.07) 12% 13%, transparent 13% 49%, rgba(0,229,255,.06) 49% 50%, transparent 50%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner {
            width:min(780px,calc(100% - 22px)) !important; padding:24px 42px 22px !important;
            border:0 !important; border-left:7px solid #f2df00 !important; border-right:2px solid #00e5ff !important;
            clip-path:polygon(0 12px,18px 0,78% 0,calc(78% + 14px) 8px,100% 8px,100% calc(100% - 14px),calc(100% - 20px) 100%,15% 100%,calc(15% - 12px) calc(100% - 8px),0 calc(100% - 8px)) !important;
            background:linear-gradient(104deg,rgba(3,5,5,.98),rgba(12,14,13,.96) 42%,rgba(2,12,16,.96)), repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 5px) !important;
            box-shadow:0 24px 58px rgba(0,0,0,.68),-14px 0 34px rgba(242,223,0,.18),14px 0 34px rgba(0,229,255,.13),inset 0 1px rgba(255,255,255,.05) !important;
        }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner::before { content:"" !important; position:absolute !important; left:0 !important; right:0 !important; top:0 !important; height:5px !important; background:linear-gradient(90deg,#f2df00 0 34%,transparent 34% 68%,#00e5ff 68%) !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-title { color:#f3e800 !important; font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important; font-size:clamp(34px,5.3vw,63px) !important; letter-spacing:1.5px !important; transform:skewX(-6deg) scaleX(.94) !important; text-shadow:3px 3px 0 #020202,6px 6px 0 rgba(0,229,255,.32),0 0 20px rgba(242,223,0,.18) !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-divider { height:3px !important; background:linear-gradient(90deg,transparent,#f2df00 12%,#fff 48%,#00e5ff 82%,transparent) !important; transform:skewX(-18deg) !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-tier { border-radius:0 !important; border-color:#f2df00 !important; color:#f2df00 !important; background:rgba(0,0,0,.66) !important; box-shadow:inset 4px 0 0 #00e5ff !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-source { color:#00e5ff !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-kicker { color:#f2df00 !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-amount { color:#fff !important; text-shadow:2px 2px 0 #101010,4px 4px 0 rgba(242,223,0,.58),0 0 18px rgba(0,229,255,.44) !important; }#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-particle { background:#f2df00 !important; box-shadow:0 0 8px rgba(0,229,255,.8) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-cinematic { background:radial-gradient(ellipse at 50% 46%,transparent 8%,rgba(38,0,0,.20) 52%,rgba(0,0,0,.88) 100%),linear-gradient(180deg,rgba(0,0,0,.25),transparent 45%,rgba(72,8,0,.42)) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-a { background:radial-gradient(ellipse at 18% 110%,rgba(255,197,44,.82) 0 5%,rgba(255,72,0,.48) 13%,transparent 37%),radial-gradient(ellipse at 52% 115%,rgba(255,229,92,.72) 0 6%,rgba(255,52,0,.44) 15%,transparent 40%),radial-gradient(ellipse at 84% 110%,rgba(255,155,28,.76) 0 5%,rgba(170,0,0,.40) 17%,transparent 39%),linear-gradient(180deg,transparent 48%,rgba(92,0,0,.28)) !important; mix-blend-mode:screen !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-b { background:repeating-conic-gradient(from 18deg at 50% 85%,transparent 0 7deg,rgba(255,85,0,.08) 7deg 8deg,transparent 8deg 17deg),radial-gradient(ellipse at 50% 88%,transparent 0 18%,rgba(255,43,0,.14) 42%,transparent 68%) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-c { background:radial-gradient(circle at 15% 25%,rgba(255,255,255,.05),transparent 18%),radial-gradient(circle at 75% 35%,rgba(255,120,60,.08),transparent 22%),repeating-radial-gradient(circle at 40% 55%,rgba(255,255,255,.025) 0 1px,transparent 1px 8px) !important; filter:blur(1px) contrast(130%) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner { width:min(760px,calc(100% - 24px)) !important; padding:25px 36px 23px !important; border:1px solid rgba(255,111,23,.62) !important; border-left:6px solid #ff4a0b !important; border-right:6px solid #8e0800 !important; clip-path:polygon(0 14px,18px 0,100% 0,100% calc(100% - 16px),calc(100% - 20px) 100%,0 100%) !important; background:radial-gradient(circle at 50% 110%,rgba(130,18,0,.26),transparent 44%),linear-gradient(108deg,rgba(4,4,4,.98),rgba(27,9,5,.97) 48%,rgba(5,3,3,.98)),repeating-linear-gradient(120deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px) !important; box-shadow:0 24px 60px rgba(0,0,0,.72),0 0 38px rgba(255,53,0,.18),inset 0 -16px 38px rgba(112,5,0,.18) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-title { color:#f4eee1 !important; font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important; font-size:clamp(35px,5.5vw,66px) !important; letter-spacing:1.4px !important; transform:scaleX(.92) !important; text-shadow:2px 2px 0 #170100,5px 5px 0 #7d0b00,0 0 17px rgba(255,79,10,.72),0 0 38px rgba(255,26,0,.28) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-divider { height:3px !important; background:linear-gradient(90deg,transparent,#7d0b00 12%,#ff5c12 36%,#fff3b3 50%,#ff5c12 64%,#7d0b00 88%,transparent) !important; box-shadow:0 0 16px rgba(255,63,0,.55) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-tier { border-radius:2px !important; border-color:#ff5b18 !important; color:#ffb14f !important; background:rgba(37,3,0,.72) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-source { color:#ff6b22 !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-kicker { color:#d8b8a7 !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-amount { color:#ffd76a !important; text-shadow:2px 2px 0 #2c0500,0 0 14px #ff4b00,0 0 30px rgba(255,18,0,.48) !important; }#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-particle { border-radius:999px !important; background:linear-gradient(180deg,#fff2a5,#ff7b18 55%,rgba(170,8,0,0)) !important; box-shadow:0 0 8px #ff8d21,0 0 18px rgba(255,34,0,.75) !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-cinematic { background:radial-gradient(ellipse at 50% 42%,rgba(122,178,55,.12),rgba(9,18,6,.60) 52%,rgba(0,0,0,.94) 100%),repeating-linear-gradient(0deg,rgba(211,255,132,.027) 0 1px,transparent 1px 4px) !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-fx-a { opacity:.86 !important; background:repeating-linear-gradient(0deg,rgba(201,255,116,.055) 0 1px,transparent 1px 4px),radial-gradient(circle at 50% 50%,transparent 0 20%,rgba(183,233,90,.13) 20.4% 20.8%,transparent 21.2% 34%,rgba(183,233,90,.09) 34.4% 34.8%,transparent 35.2%) !important; animation:mcms-fallout-scan 5.6s linear infinite !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-fx-b { opacity:.78 !important; background:linear-gradient(90deg,rgba(105,151,44,.12),transparent 18%,transparent 82%,rgba(105,151,44,.12)),repeating-radial-gradient(circle at 42% 38%,rgba(255,244,196,.045) 0 1px,transparent 1px 7px) !important; filter:contrast(155%) sepia(28%) !important; animation:mcms-fallout-flicker 3.8s steps(1,end) infinite !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-fx-c { opacity:.72 !important; background:conic-gradient(from 0deg at 50% 50%,rgba(210,242,112,.18) 0 1deg,transparent 1deg 29deg,rgba(210,242,112,.08) 29deg 30deg,transparent 30deg 60deg) !important; mask-image:radial-gradient(circle at center,transparent 0 25%,#000 27% 42%,transparent 65%) !important; -webkit-mask-image:radial-gradient(circle at center,transparent 0 25%,#000 27% 42%,transparent 65%) !important; animation:mcms-fallout-radar 13s linear infinite !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner { width:min(760px,calc(100% - 28px)) !important; padding:31px 38px 25px !important; border:2px solid rgba(193,232,101,.82) !important; border-radius:8px !important; background:linear-gradient(180deg,rgba(18,30,12,.985),rgba(4,10,3,.99)),repeating-linear-gradient(0deg,rgba(197,255,116,.03) 0 1px,transparent 1px 4px) !important; box-shadow:0 0 0 3px rgba(3,7,2,.92),0 0 0 6px rgba(123,158,57,.22),0 0 34px rgba(154,211,69,.28),0 28px 68px rgba(0,0,0,.74),inset 0 0 44px rgba(145,193,66,.10) !important; overflow:hidden !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner::before { content:"VAULT-TEC FINANCIAL TERMINAL // REWARD CLEARANCE" !important; position:absolute !important; left:17px !important; top:11px !important; right:17px !important; color:rgba(214,250,137,.60) !important; font:900 8px/1 "Courier New",Consolas,monospace !important; letter-spacing:1.6px !important; text-align:left !important; border-bottom:1px dashed rgba(176,221,83,.28) !important; padding-bottom:7px !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-banner::after { content:"ROBCO INDUSTRIES (TM) UNIFIED OPERATING SYSTEM" !important; position:absolute !important; right:15px !important; bottom:8px !important; color:rgba(161,201,84,.40) !important; font:700 6px/1 monospace !important; letter-spacing:1px !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-title { color:#d6ff84 !important; font-family:"Courier New",Consolas,monospace !important; font-size:clamp(28px,4.8vw,56px) !important; font-weight:900 !important; letter-spacing:1.4px !important; transform:none !important; text-shadow:0 0 5px rgba(210,255,128,.95),0 0 15px rgba(151,212,61,.46),2px 0 rgba(113,160,44,.35) !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#6f9134 9%,#d7ff8e 50%,#6f9134 91%,transparent) !important; box-shadow:0 0 11px rgba(175,232,79,.48) !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-tier { border:1px solid #a8d255 !important; color:#dbff91 !important; background:rgba(13,26,8,.88) !important; border-radius:2px !important; font-family:"Courier New",Consolas,monospace !important; letter-spacing:1.2px !important; box-shadow:inset 0 0 9px rgba(153,214,63,.12),0 0 7px rgba(143,197,57,.16) !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-mission,
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-source,
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-kicker,
        #${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-amount { font-family:"Courier New",Consolas,monospace !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-mission { color:#c1e87a !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-source { color:#e1ff9d !important; letter-spacing:.8px !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-kicker { color:#8fb554 !important; letter-spacing:1.4px !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-amount { color:#f0c66c !important; text-shadow:0 0 7px rgba(255,203,93,.88),0 0 24px rgba(178,112,32,.34) !important; }#${SCRIPT.payoutFlashId}[data-template="wasteland"] .mcms-payout-theme-particle { border-radius:50% !important; background:#d7f996 !important; box-shadow:0 0 5px rgba(202,238,123,.82) !important; opacity:.72 !important; }
        @keyframes mcms-fallout-scan { 0% { transform:translateY(-2%) } 100% { transform:translateY(2%) } }
        @keyframes mcms-fallout-radar { from { transform:rotate(0deg) scale(1) } to { transform:rotate(360deg) scale(1.025) } }
        @keyframes mcms-fallout-flicker { 0%,7%,11%,46%,50%,88%,100% { opacity:.78 } 8%,10%,47%,49%,89% { opacity:.42 } }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-cinematic { background:radial-gradient(ellipse at 50% 50%,rgba(20,119,165,.05),rgba(3,11,30,.36) 58%,rgba(0,2,10,.88)),linear-gradient(180deg,rgba(0,8,26,.34),transparent 40%,rgba(0,3,15,.52)) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-a { background-image:radial-gradient(circle at 13% 19%,#fff 0 1px,transparent 1.7px),radial-gradient(circle at 28% 72%,#8adfff 0 1px,transparent 1.8px),radial-gradient(circle at 63% 28%,#fff 0 1px,transparent 1.6px),radial-gradient(circle at 82% 62%,#9ee9ff 0 1.2px,transparent 2px),radial-gradient(circle at 47% 48%,rgba(119,225,255,.6) 0 1px,transparent 2px); background-size:160px 140px,230px 190px,290px 240px,340px 270px,420px 330px !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-b { background:repeating-linear-gradient(90deg,transparent 0 72px,rgba(80,205,255,.055) 72px 73px,transparent 73px 144px),repeating-linear-gradient(0deg,transparent 0 50px,rgba(80,205,255,.045) 50px 51px,transparent 51px 100px),linear-gradient(90deg,transparent 5%,rgba(105,219,255,.18) 5% 5.2%,transparent 5.2% 94.8%,rgba(105,219,255,.18) 94.8% 95%,transparent 95%) !important; mask-image:radial-gradient(ellipse at center,#000 8%,transparent 86%) !important; -webkit-mask-image:radial-gradient(ellipse at center,#000 8%,transparent 86%) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-c { background:conic-gradient(from 0deg at 50% 50%,transparent 0 72%,rgba(91,220,255,.24) 74%,rgba(91,220,255,.04) 78%,transparent 82%),radial-gradient(circle at center,transparent 0 27%,rgba(91,220,255,.13) 27.5% 28%,transparent 28.5% 42%,rgba(91,220,255,.08) 42.5% 43%,transparent 43.5%) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner { width:min(790px,calc(100% - 24px)) !important; padding:24px 40px 22px !important; border:1px solid rgba(111,221,255,.55) !important; border-left:5px solid #6fddff !important; border-right:5px solid rgba(235,192,79,.70) !important; clip-path:polygon(0 12px,16px 0,85% 0,100% 18px,100% calc(100% - 18px),85% 100%,16px 100%,0 calc(100% - 12px)) !important; background:linear-gradient(100deg,rgba(3,13,31,.94),rgba(8,31,57,.91) 48%,rgba(3,12,30,.95)),repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 5px) !important; box-shadow:0 24px 58px rgba(0,0,0,.65),0 0 32px rgba(74,200,255,.18),inset 0 1px rgba(255,255,255,.06) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-title { color:#f2fbff !important; font-family:"Arial Narrow",Arial,sans-serif !important; font-size:clamp(34px,5.2vw,61px) !important; letter-spacing:3px !important; transform:scaleX(.94) !important; text-shadow:0 0 7px #6fddff,0 0 24px rgba(52,177,255,.36),3px 3px 0 rgba(0,7,22,.94) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#6fddff 18%,#fff 49%,#e8c154 81%,transparent) !important; box-shadow:0 0 11px rgba(98,217,255,.46) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-tier { border-color:#6fddff !important; color:#a9eeff !important; background:rgba(3,18,39,.72) !important; box-shadow:inset 3px 0 0 #e8c154 !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-source { color:#6fddff !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-kicker { color:#e8c154 !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-amount { color:#fff !important; text-shadow:0 0 9px #6fddff,0 0 24px rgba(69,180,255,.34) !important; }#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-particle { border-radius:50% !important; background:#fff !important; box-shadow:0 0 8px #6fddff !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,rgba(122,89,24,.05),rgba(15,11,8,.36) 52%,rgba(0,0,0,.90)),linear-gradient(180deg,rgba(10,8,7,.34),transparent 42%,rgba(27,17,8,.46)) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-a { background:radial-gradient(circle at 50% 52%,rgba(233,192,87,.16) 0 2%,transparent 3% 18%,rgba(233,192,87,.09) 18.5% 19%,transparent 19.5% 31%,rgba(233,192,87,.06) 31.5% 32%,transparent 32.5%),conic-gradient(from 0deg at 50% 52%,transparent 0 14%,rgba(233,192,87,.06) 14% 15%,transparent 15% 38%,rgba(233,192,87,.05) 38% 39%,transparent 39%) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-b { background:radial-gradient(ellipse at 18% 82%,rgba(185,122,38,.15),transparent 32%),radial-gradient(ellipse at 82% 18%,rgba(218,184,102,.09),transparent 28%),repeating-radial-gradient(circle at 32% 48%,rgba(255,255,255,.02) 0 1px,transparent 1px 8px) !important; filter:sepia(35%) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-c { background:linear-gradient(115deg,transparent 0 15%,rgba(237,199,99,.07) 15% 15.3%,transparent 15.3% 84.7%,rgba(237,199,99,.07) 84.7% 85%,transparent 85%),linear-gradient(180deg,transparent 8%,rgba(237,199,99,.06) 8% 8.3%,transparent 8.3% 91.7%,rgba(237,199,99,.06) 91.7% 92%,transparent 92%) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner { width:min(740px,calc(100% - 28px)) !important; padding:27px 40px 24px !important; border:1px solid rgba(216,174,73,.66) !important; border-top:3px double #d8ae49 !important; border-bottom:3px double #d8ae49 !important; background:radial-gradient(circle at 50% 120%,rgba(100,61,12,.22),transparent 44%),linear-gradient(102deg,rgba(7,7,7,.97),rgba(28,24,19,.96) 50%,rgba(6,6,6,.98)),repeating-linear-gradient(35deg,rgba(255,255,255,.018) 0 1px,transparent 1px 8px) !important; box-shadow:0 24px 60px rgba(0,0,0,.72),0 0 30px rgba(203,155,54,.14),inset 0 0 36px rgba(126,91,26,.08) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::after { content:"‚óÜ" !important; position:absolute !important; top:50% !important; transform:translateY(-50%) !important; color:#d8ae49 !important; font-size:18px !important; text-shadow:0 0 10px rgba(216,174,73,.55) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::before { left:15px !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::after { right:15px !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title { color:#e8c96f !important; font-family:Georgia,"Times New Roman",serif !important; font-size:clamp(34px,5.2vw,62px) !important; letter-spacing:1px !important; text-transform:none !important; transform:none !important; text-shadow:0 2px 0 #130d05,0 0 10px rgba(229,190,84,.54),0 0 28px rgba(174,116,20,.22) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#7b5b23 12%,#e3bf5c 36%,#fff1ae 50%,#e3bf5c 64%,#7b5b23 88%,transparent) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-tier { border-color:#b9903c !important; color:#e8c96f !important; background:rgba(16,12,8,.72) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-source { color:#e3bf5c !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-kicker { color:#a89569 !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-amount { color:#fff0b1 !important; font-family:Georgia,"Times New Roman",serif !important; text-shadow:0 2px 0 #100a03,0 0 13px rgba(225,181,67,.58) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-particle { border-radius:50% !important; background:#d5c39c !important; box-shadow:0 0 5px rgba(220,183,92,.45) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,transparent 12%,rgba(11,18,20,.28) 55%,rgba(0,0,0,.88)),linear-gradient(180deg,rgba(21,28,30,.26),transparent 48%,rgba(8,13,14,.40)) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-a { background:repeating-linear-gradient(90deg,transparent 0 59px,rgba(218,234,236,.045) 59px 60px,transparent 60px 120px),repeating-linear-gradient(0deg,transparent 0 39px,rgba(218,234,236,.04) 39px 40px,transparent 40px 80px),linear-gradient(90deg,rgba(207,25,35,.12),transparent 28%,transparent 72%,rgba(46,178,112,.08)) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-b { background:repeating-linear-gradient(135deg,rgba(204,20,30,.10) 0 10px,transparent 10px 20px) !important; mask-image:linear-gradient(180deg,#000 0 7%,transparent 7% 90%,#000 90%) !important; -webkit-mask-image:linear-gradient(180deg,#000 0 7%,transparent 7% 90%,#000 90%) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-c { background:linear-gradient(180deg,transparent 0 45%,rgba(83,255,164,.12) 49%,rgba(83,255,164,.22) 50%,rgba(83,255,164,.08) 51%,transparent 55%),radial-gradient(circle at 50% 50%,transparent 0 25%,rgba(235,245,246,.07) 25.5% 26%,transparent 26.5%) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner { width:min(790px,calc(100% - 24px)) !important; padding:24px 38px 22px !important; border:1px solid rgba(221,234,235,.38) !important; border-left:8px solid #c81724 !important; border-right:3px solid #43d887 !important; background:linear-gradient(104deg,rgba(8,12,13,.98),rgba(25,32,34,.96) 48%,rgba(7,12,13,.98)),repeating-linear-gradient(0deg,rgba(255,255,255,.02) 0 1px,transparent 1px 5px) !important; clip-path:polygon(0 0,96% 0,100% 14px,100% 100%,4% 100%,0 calc(100% - 14px)) !important; box-shadow:0 24px 58px rgba(0,0,0,.68),-12px 0 30px rgba(200,23,36,.16),12px 0 24px rgba(67,216,135,.10),inset 0 1px rgba(255,255,255,.05) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before { content:"CONTAINMENT PROTOCOL // SECURE" !important; position:absolute !important; right:18px !important; top:10px !important; color:rgba(87,229,150,.58) !important; font:900 7px/1 monospace !important; letter-spacing:1.4px !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title { color:#f0f5f5 !important; font-family:"Arial Narrow",Arial,sans-serif !important; font-size:clamp(33px,5vw,59px) !important; letter-spacing:2.7px !important; transform:scaleX(.96) !important; text-shadow:3px 3px 0 #101415,6px 6px 0 rgba(200,23,36,.50),0 0 18px rgba(255,255,255,.10) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-divider { height:2px !important; background:linear-gradient(90deg,transparent,#c81724 16%,#f0f5f5 49%,#43d887 82%,transparent) !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-tier { border-radius:0 !important; border-color:#c81724 !important; color:#f3f6f6 !important; background:rgba(30,5,8,.64) !important; box-shadow:inset 4px 0 0 #43d887 !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-source { color:#43d887 !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-kicker { color:#d65b63 !important; }#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-amount { color:#fff !important; text-shadow:0 0 10px rgba(67,216,135,.62),3px 3px 0 rgba(200,23,36,.55) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,rgba(113,11,15,.06),rgba(17,4,7,.42) 56%,rgba(0,0,0,.91)),linear-gradient(180deg,rgba(45,0,5,.28),transparent 42%,rgba(50,5,0,.34)) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-a { background:radial-gradient(ellipse at 22% 110%,rgba(233,46,18,.35),transparent 38%),radial-gradient(ellipse at 78% 110%,rgba(190,13,20,.32),transparent 36%),radial-gradient(circle at 50% 50%,transparent 0 26%,rgba(226,181,63,.08) 26.5% 27%,transparent 27.5%) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-b { background:repeating-linear-gradient(90deg,transparent 0 44px,rgba(224,181,68,.07) 44px 47px,transparent 47px 88px),repeating-linear-gradient(0deg,transparent 0 44px,rgba(224,181,68,.045) 44px 47px,transparent 47px 88px) !important; mask-image:linear-gradient(90deg,#000 0 12%,transparent 12% 88%,#000 88%) !important; -webkit-mask-image:linear-gradient(90deg,#000 0 12%,transparent 12% 88%,#000 88%) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-c { background:conic-gradient(from 25deg at 50% 50%,transparent 0 15%,rgba(222,173,55,.08) 15% 16%,transparent 16% 33%,rgba(170,13,21,.10) 33% 34%,transparent 34%) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner { width:min(740px,calc(100% - 28px)) !important; padding:27px 40px 24px !important; border:1px solid rgba(221,174,57,.58) !important; border-top:4px solid #b3131d !important; border-bottom:4px solid #d9ad3b !important; background:radial-gradient(circle at 50% 120%,rgba(126,10,12,.24),transparent 42%),linear-gradient(105deg,rgba(5,4,5,.98),rgba(31,9,12,.96) 48%,rgba(5,4,5,.98)),repeating-linear-gradient(35deg,rgba(255,255,255,.018) 0 1px,transparent 1px 8px) !important; box-shadow:0 24px 60px rgba(0,0,0,.72),0 0 32px rgba(185,20,27,.18),inset 0 0 32px rgba(213,168,51,.06) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::after { content:"‚óÜ" !important; position:absolute !important; top:50% !important; transform:translateY(-50%) rotate(45deg) !important; color:#d9ad3b !important; font-size:14px !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::before { left:18px !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::after { right:18px !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title { color:#f4e9d6 !important; font-family:Georgia,"Times New Roman",serif !important; font-size:clamp(35px,5.4vw,64px) !important; text-transform:none !important; letter-spacing:.5px !important; transform:none !important; text-shadow:0 2px 0 #160306,0 0 10px rgba(217,173,59,.55),4px 4px 0 rgba(151,12,20,.48) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-divider { height:3px !important; background:linear-gradient(90deg,transparent,#8d1118 12%,#d9ad3b 36%,#fff0b0 50%,#d9ad3b 64%,#8d1118 88%,transparent) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-tier { border-color:#b3131d !important; color:#e8bf55 !important; background:rgba(35,3,7,.68) !important; box-shadow:inset 4px 0 0 #d9ad3b !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-source { color:#e4b94c !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-kicker { color:#bd7b80 !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-amount { color:#ffe08a !important; font-family:Georgia,"Times New Roman",serif !important; text-shadow:0 2px 0 #190307,0 0 13px rgba(218,169,48,.62),0 0 25px rgba(162,8,16,.30) !important; }#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-particle { border-radius:50% !important; background:#ffd96d !important; box-shadow:0 0 7px #e15e25,0 0 16px rgba(180,10,18,.62) !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-cinematic { background:radial-gradient(ellipse at center,rgba(78,31,143,.08),rgba(8,5,21,.38) 55%,rgba(0,0,0,.89)),repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 4px) !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-a { background:repeating-linear-gradient(90deg,rgba(109,62,220,.06) 0 8px,transparent 8px 16px),repeating-linear-gradient(0deg,rgba(33,222,196,.05) 0 8px,transparent 8px 16px) !important; image-rendering:pixelated !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-b { background:radial-gradient(circle at 18% 28%,#ffdc4a 0 3px,transparent 4px),radial-gradient(circle at 82% 34%,#4af7df 0 3px,transparent 4px),radial-gradient(circle at 32% 76%,#ff5ea9 0 3px,transparent 4px),radial-gradient(circle at 68% 72%,#8b6cff 0 3px,transparent 4px); background-size:120px 100px,170px 140px,210px 180px,250px 220px !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-c { background:linear-gradient(90deg,transparent 0 8%,rgba(255,255,255,.06) 8% 8.5%,transparent 8.5% 91.5%,rgba(255,255,255,.06) 91.5% 92%,transparent 92%),linear-gradient(180deg,transparent 0 12%,rgba(255,255,255,.05) 12% 12.5%,transparent 12.5% 87.5%,rgba(255,255,255,.05) 87.5% 88%,transparent 88%) !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner { width:min(700px,calc(100% - 24px)) !important; padding:24px 34px 22px !important; border:4px solid #ecebff !important; border-radius:0 !important; clip-path:polygon(0 10px,10px 10px,10px 0,calc(100% - 10px) 0,calc(100% - 10px) 10px,100% 10px,100% calc(100% - 10px),calc(100% - 10px) calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,10px calc(100% - 10px),0 calc(100% - 10px)) !important; background:linear-gradient(180deg,rgba(20,10,45,.98),rgba(7,5,21,.98)),repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 8px,transparent 8px 16px) !important; box-shadow:8px 8px 0 #5f3aca,-8px -8px 0 #22d8c3,0 24px 50px rgba(0,0,0,.64) !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-title { color:#fff36a !important; font-family:"Courier New",Consolas,monospace !important; font-size:clamp(29px,4.5vw,52px) !important; letter-spacing:1px !important; transform:none !important; text-shadow:4px 0 0 #ff5aaa,0 4px 0 #25dfcb,4px 4px 0 #38206f !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-divider { height:4px !important; background:repeating-linear-gradient(90deg,#ff5aaa 0 12px,#fff36a 12px 24px,#25dfcb 24px 36px,#8b6cff 36px 48px) !important; box-shadow:none !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-tier { border-radius:0 !important; border:2px solid #25dfcb !important; color:#fff36a !important; background:#12092c !important; font-family:monospace !important; box-shadow:3px 3px 0 #5f3aca !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-mission,
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-source,
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-kicker,
        #${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-amount { font-family:"Courier New",Consolas,monospace !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-source { color:#25dfcb !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-kicker { color:#ff79b8 !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-amount { color:#fff !important; text-shadow:3px 0 0 #ff5aaa,0 3px 0 #25dfcb,3px 3px 0 #4d2da5 !important; }#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-particle { background:#fff36a !important; box-shadow:4px 4px 0 #ff5aaa !important; image-rendering:pixelated !important; }#${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner {
            isolation:isolate !important;
            overflow:hidden !important;
        }#${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner > * {
            position:relative !important;
            z-index:3 !important;
        }#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-cinematic {
            background:radial-gradient(circle at 50% 48%,transparent 0 16%,rgba(0,0,0,.35) 55%,rgba(0,0,0,.92) 100%),linear-gradient(135deg,rgba(12,28,21,.30),transparent 42%,rgba(70,53,9,.18)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-theme-fx-a {
            background:linear-gradient(26deg,transparent 0 46%,rgba(255,210,72,.10) 46% 46.4%,transparent 46.4%),linear-gradient(154deg,transparent 0 54%,rgba(255,255,255,.055) 54% 54.35%,transparent 54.35%),repeating-linear-gradient(90deg,transparent 0 119px,rgba(255,255,255,.028) 120px,transparent 121px) !important;
        }#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-theme-fx-b {
            background:radial-gradient(circle at 12% 16%,rgba(229,190,64,.24),transparent 20%),radial-gradient(circle at 88% 82%,rgba(22,111,72,.22),transparent 26%),linear-gradient(90deg,transparent 8%,rgba(255,255,255,.035) 8% 8.2%,transparent 8.2% 92%,rgba(255,255,255,.035) 92% 92.2%,transparent 92.2%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-theme-fx-c {
            background:repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 4px),linear-gradient(90deg,rgba(0,0,0,.30),transparent 20%,transparent 80%,rgba(0,0,0,.30)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner {
            width:min(770px,calc(100% - 26px)) !important;padding:27px 42px 24px !important;border-radius:2px !important;
            border:1px solid rgba(245,211,102,.62) !important;border-left:8px solid #d3a928 !important;border-right:3px solid #2d6c4e !important;
            clip-path:polygon(0 0,96% 0,100% 16px,100% 100%,4% 100%,0 calc(100% - 16px)) !important;
            background:linear-gradient(112deg,rgba(5,8,7,.985),rgba(17,23,19,.97) 48%,rgba(6,8,7,.985)),repeating-linear-gradient(135deg,rgba(255,255,255,.025) 0 1px,transparent 1px 9px) !important;
            box-shadow:0 28px 70px rgba(0,0,0,.78),0 0 36px rgba(217,177,49,.16),inset 0 1px rgba(255,255,255,.06),inset 0 -22px 45px rgba(11,64,43,.12) !important;
        }#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner::before {content:"LOS SANTOS // SCORE SETTLED" !important;position:absolute !important;top:11px !important;right:18px !important;color:rgba(234,204,100,.58) !important;font:900 7px/1.1 monospace !important;letter-spacing:1.8px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:linear-gradient(122deg,transparent 0 68%,rgba(230,193,72,.075) 68% 69%,transparent 69% 73%,rgba(52,130,91,.07) 73% 74%,transparent 74%) !important;z-index:1 !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-title {color:#f4efe1 !important;font-family:Impact,Haettenschweiler,"Arial Narrow Bold",sans-serif !important;font-size:clamp(36px,5.6vw,68px) !important;letter-spacing:1.5px !important;transform:skewX(-5deg) scaleX(.93) !important;text-shadow:3px 3px 0 #111,6px 6px 0 rgba(185,143,24,.48),0 0 20px rgba(255,219,90,.18) !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-divider {height:3px !important;background:linear-gradient(90deg,transparent,#d9ac2f 10%,#f7e2a0 48%,#2b8d66 88%,transparent) !important;transform:skewX(-15deg) !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-tier {border-radius:1px !important;border-color:#d3a928 !important;color:#f3d873 !important;background:rgba(8,12,10,.78) !important;box-shadow:inset 4px 0 0 #2d7957 !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-source {color:#77d7a8 !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-kicker {color:#e1ba45 !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-amount {color:#fff7d8 !important;text-shadow:2px 2px 0 #0a0a0a,4px 4px 0 rgba(181,139,26,.58),0 0 18px rgba(239,208,83,.24) !important;}#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 50% 13%,rgba(255,188,75,.22),transparent 20%),linear-gradient(180deg,rgba(255,62,168,.10),transparent 45%),repeating-linear-gradient(90deg,transparent 0 109px,rgba(48,245,238,.038) 110px,transparent 111px) !important;}#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-theme-fx-b {background:linear-gradient(116deg,transparent 0 20%,rgba(255,83,183,.08) 20% 21%,transparent 21% 79%,rgba(34,239,233,.08) 79% 80%,transparent 80%),radial-gradient(ellipse at 50% 120%,rgba(48,233,221,.15),transparent 48%) !important;}#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner {box-shadow:0 28px 74px rgba(0,0,0,.72),-16px 0 42px rgba(255,47,161,.22),16px 0 42px rgba(0,229,222,.20),inset 0 1px rgba(255,255,255,.12) !important;}#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-banner::before {content:"VICE CITY // CASHOUT" !important;position:absolute !important;top:10px !important;left:18px !important;color:rgba(71,242,231,.68) !important;font:900 7px/1 monospace !important;letter-spacing:1.7px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-amount {filter:drop-shadow(0 0 8px rgba(41,245,234,.35)) !important;}#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-theme-fx-a {background:linear-gradient(90deg,rgba(0,0,0,.36),transparent 18%,transparent 82%,rgba(0,0,0,.36)),repeating-linear-gradient(0deg,transparent 0 38px,rgba(244,214,123,.035) 39px,transparent 40px) !important;}#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-theme-fx-b {background:radial-gradient(circle at 10% 78%,rgba(248,145,37,.16),transparent 25%),radial-gradient(circle at 88% 22%,rgba(168,195,146,.12),transparent 23%),linear-gradient(135deg,transparent 49.6%,rgba(255,210,109,.10) 49.8% 50.2%,transparent 50.4%) !important;}#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner {border-top-color:rgba(247,206,112,.76) !important;border-bottom-color:rgba(121,145,103,.72) !important;box-shadow:0 28px 70px rgba(0,0,0,.78),0 0 38px rgba(230,151,54,.16),inset 0 0 40px rgba(112,94,48,.08) !important;}#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::before {content:"FIELD OPS // PAYMENT EXTRACTED" !important;position:absolute !important;top:10px !important;right:18px !important;color:rgba(242,210,132,.60) !important;font:900 7px/1 monospace !important;letter-spacing:1.5px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="badCompany"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:linear-gradient(90deg,transparent 0 7%,rgba(255,211,113,.06) 7% 7.3%,transparent 7.3% 92.7%,rgba(255,211,113,.06) 92.7% 93%,transparent 93%),repeating-linear-gradient(135deg,rgba(255,199,84,.035) 0 4px,transparent 4px 12px) !important;z-index:1 !important;}#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-theme-fx-c {background:linear-gradient(90deg,rgba(255,255,255,.035),transparent 15%,transparent 85%,rgba(255,255,255,.035)),repeating-linear-gradient(45deg,transparent 0 72px,rgba(212,175,55,.035) 73px,transparent 74px) !important;}#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner {box-shadow:0 30px 78px rgba(0,0,0,.80),-14px 0 36px rgba(147,0,18,.20),14px 0 34px rgba(211,175,55,.14),inset 0 0 34px rgba(255,255,255,.035) !important;}#${SCRIPT.payoutFlashId}[data-template="scarface"] .mcms-payout-banner::before {content:"MIAMI // EMPIRE ACCOUNT" !important;position:absolute !important;top:10px !important;left:18px !important;color:rgba(215,178,62,.68) !important;font:900 7px/1 serif !important;letter-spacing:2px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 50%,transparent 0 12%,rgba(0,0,0,.26) 58%,rgba(0,0,0,.88) 100%),linear-gradient(120deg,rgba(242,223,0,.07),transparent 36%,rgba(0,229,255,.075)) !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-a {background:repeating-linear-gradient(0deg,rgba(0,229,255,.035) 0 1px,transparent 1px 5px),linear-gradient(90deg,transparent 0 9%,rgba(242,223,0,.10) 9% 9.5%,transparent 9.5% 90.5%,rgba(0,229,255,.10) 90.5% 91%,transparent 91%) !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-b {background:linear-gradient(135deg,transparent 0 46%,rgba(242,223,0,.08) 46% 46.4%,transparent 46.4% 52%,rgba(0,229,255,.08) 52% 52.4%,transparent 52.4%),repeating-linear-gradient(90deg,transparent 0 137px,rgba(255,255,255,.028) 138px,transparent 139px) !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-theme-fx-c {background:radial-gradient(circle at 18% 25%,rgba(242,223,0,.12),transparent 20%),radial-gradient(circle at 82% 78%,rgba(0,229,255,.13),transparent 23%),linear-gradient(90deg,rgba(0,0,0,.25),transparent 18%,transparent 82%,rgba(0,0,0,.25)) !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner {width:min(800px,calc(100% - 24px)) !important;padding:28px 42px 24px !important;border:1px solid rgba(242,223,0,.68) !important;border-left:9px solid #f2df00 !important;border-right:4px solid #00e5ff !important;clip-path:polygon(0 0,94% 0,100% 18px,100% 100%,6% 100%,0 calc(100% - 18px)) !important;background:linear-gradient(108deg,rgba(4,5,7,.985),rgba(18,20,23,.97) 52%,rgba(4,6,8,.985)),repeating-linear-gradient(0deg,rgba(255,255,255,.02) 0 1px,transparent 1px 5px) !important;box-shadow:0 30px 74px rgba(0,0,0,.78),-16px 0 38px rgba(242,223,0,.14),16px 0 38px rgba(0,229,255,.15),inset 0 0 34px rgba(0,229,255,.04) !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner::before {content:"ARASAKA FINANCIAL NODE // VERIFIED" !important;position:absolute !important;top:10px !important;right:18px !important;height:auto !important;background:none !important;color:rgba(0,229,255,.68) !important;font:900 7px/1 monospace !important;letter-spacing:1.6px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:linear-gradient(90deg,transparent 0 31%,rgba(242,223,0,.055) 31% 31.4%,transparent 31.4% 67%,rgba(0,229,255,.055) 67% 67.4%,transparent 67.4%) !important;z-index:1 !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-title {font-size:clamp(36px,5.7vw,70px) !important;letter-spacing:1.8px !important;text-shadow:3px 3px 0 #020202,6px 5px 0 rgba(0,229,255,.30),-2px -1px 0 rgba(255,36,116,.32),0 0 22px rgba(242,223,0,.20) !important;}#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-tier {box-shadow:inset 5px 0 0 #00e5ff,3px 3px 0 rgba(255,38,118,.28) !important;}#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-a {background:radial-gradient(ellipse at 14% 112%,rgba(255,222,92,.88) 0 4%,rgba(255,74,0,.50) 13%,transparent 35%),radial-gradient(ellipse at 50% 118%,rgba(255,237,118,.78) 0 5%,rgba(255,48,0,.48) 16%,transparent 41%),radial-gradient(ellipse at 87% 112%,rgba(255,166,36,.84) 0 4%,rgba(150,0,0,.43) 18%,transparent 38%),linear-gradient(180deg,transparent 46%,rgba(96,0,0,.32)) !important;mix-blend-mode:screen !important;}#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-theme-fx-b {background:repeating-conic-gradient(from 0deg at 50% 86%,transparent 0 8deg,rgba(255,96,0,.075) 8deg 9deg,transparent 9deg 18deg),radial-gradient(ellipse at 50% 91%,transparent 0 16%,rgba(255,48,0,.17) 38%,transparent 66%) !important;}#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner {border-top:3px solid #ffad26 !important;border-bottom:3px solid #760000 !important;box-shadow:0 30px 76px rgba(0,0,0,.80),0 0 44px rgba(255,48,0,.23),inset 0 -24px 48px rgba(122,4,0,.20),inset 0 1px rgba(255,232,173,.10) !important;}#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner::before {content:"INFERNAL TREASURY // SEAL BROKEN" !important;position:absolute !important;top:10px !important;right:18px !important;color:rgba(255,176,62,.67) !important;font:900 7px/1 serif !important;letter-spacing:1.7px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:radial-gradient(circle at 50% 125%,rgba(255,82,0,.16),transparent 46%),linear-gradient(118deg,transparent 0 48%,rgba(255,134,24,.055) 48% 49%,transparent 49%) !important;z-index:1 !important;}#${SCRIPT.payoutFlashId}[data-template="hellfire"] .mcms-payout-title {text-shadow:2px 2px 0 #170100,5px 5px 0 #7d0b00,0 0 20px rgba(255,91,13,.82),0 0 48px rgba(255,30,0,.30) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 45%,transparent 0 12%,rgba(2,7,23,.30) 58%,rgba(0,2,10,.94) 100%),linear-gradient(135deg,rgba(42,98,255,.08),transparent 42%,rgba(146,74,255,.08)) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 50% 50%,transparent 0 18%,rgba(82,149,255,.11) 18.5% 19%,transparent 19.5% 31%,rgba(153,99,255,.075) 31.5% 32%,transparent 32.5%),repeating-conic-gradient(from 0deg at 50% 50%,transparent 0 18deg,rgba(88,157,255,.045) 18deg 18.5deg,transparent 18.5deg 36deg) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-b {background:radial-gradient(circle at 15% 22%,#fff 0 1px,transparent 2px),radial-gradient(circle at 78% 17%,#8fc3ff 0 1px,transparent 2px),radial-gradient(circle at 85% 74%,#c69cff 0 1px,transparent 2px),radial-gradient(circle at 28% 80%,#fff 0 1px,transparent 2px);background-size:170px 130px,220px 180px,280px 230px,320px 260px !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-theme-fx-c {background:linear-gradient(90deg,transparent 0 8%,rgba(102,169,255,.06) 8% 8.2%,transparent 8.2% 91.8%,rgba(102,169,255,.06) 91.8% 92%,transparent 92%),linear-gradient(180deg,transparent 0 13%,rgba(185,135,255,.05) 13% 13.2%,transparent 13.2% 86.8%,rgba(185,135,255,.05) 86.8% 87%,transparent 87%) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner {width:min(790px,calc(100% - 24px)) !important;padding:28px 42px 24px !important;border:1px solid rgba(113,178,255,.60) !important;border-left:6px solid #5ca8ff !important;border-right:6px solid #9c6cff !important;clip-path:polygon(0 14px,14px 0,calc(100% - 14px) 0,100% 14px,100% calc(100% - 14px),calc(100% - 14px) 100%,14px 100%,0 calc(100% - 14px)) !important;background:linear-gradient(110deg,rgba(3,8,22,.985),rgba(12,22,45,.97) 50%,rgba(4,7,20,.985)),repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 5px) !important;box-shadow:0 30px 76px rgba(0,0,0,.80),-14px 0 36px rgba(72,149,255,.18),14px 0 36px rgba(151,92,255,.17),inset 0 0 38px rgba(88,155,255,.05) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner::before {content:"FLEET COMMAND // TREASURY UPLINK" !important;position:absolute !important;top:10px !important;right:18px !important;color:rgba(137,194,255,.70) !important;font:900 7px/1 monospace !important;letter-spacing:1.6px !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-title {color:#ecf5ff !important;font-family:Eurostile,"Arial Narrow",Arial,sans-serif !important;font-size:clamp(34px,5.2vw,64px) !important;letter-spacing:2.3px !important;transform:scaleX(.95) !important;text-shadow:0 0 4px #fff,0 0 18px rgba(90,166,255,.66),4px 4px 0 rgba(101,72,189,.34) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-divider {height:2px !important;background:linear-gradient(90deg,transparent,#5ca8ff 9%,#eef7ff 50%,#9e6fff 91%,transparent) !important;box-shadow:0 0 12px rgba(96,167,255,.42) !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-tier {border-radius:2px !important;border-color:#66b2ff !important;color:#b9dcff !important;background:rgba(4,12,30,.74) !important;box-shadow:inset 4px 0 0 #9e6fff !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-source {color:#aa8fff !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-kicker {color:#79c8ff !important;}#${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-amount {color:#fff !important;text-shadow:0 0 9px rgba(111,188,255,.65),3px 3px 0 rgba(79,55,151,.45) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 46%,transparent 0 13%,rgba(13,7,16,.32) 56%,rgba(2,1,4,.94) 100%),linear-gradient(135deg,rgba(99,57,22,.08),transparent 40%,rgba(53,19,75,.09)) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 15% 18%,rgba(214,172,74,.12),transparent 18%),radial-gradient(circle at 83% 76%,rgba(116,52,137,.12),transparent 22%),repeating-radial-gradient(circle at 50% 50%,transparent 0 54px,rgba(220,177,77,.028) 55px,transparent 56px) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-theme-fx-b {background:linear-gradient(45deg,transparent 0 49.6%,rgba(219,176,72,.055) 49.8% 50.2%,transparent 50.4%),linear-gradient(135deg,transparent 0 49.6%,rgba(117,66,133,.055) 49.8% 50.2%,transparent 50.4%) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner {width:min(750px,calc(100% - 28px)) !important;padding:31px 46px 27px !important;border:2px solid #9f7a2d !important;border-top:5px solid #d6ad4d !important;border-bottom:5px solid #4b203f !important;background:radial-gradient(circle at 50% 118%,rgba(82,29,71,.21),transparent 44%),linear-gradient(110deg,rgba(9,6,8,.985),rgba(27,16,26,.97) 50%,rgba(8,6,8,.985)),repeating-linear-gradient(45deg,rgba(255,255,255,.018) 0 1px,transparent 1px 9px) !important;box-shadow:0 32px 80px rgba(0,0,0,.82),0 0 36px rgba(213,169,67,.16),inset 0 0 48px rgba(92,44,91,.12) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::before {content:"‚ú¶" !important;left:17px !important;font-size:22px !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-banner::after {content:"‚ú¶" !important;right:17px !important;font-size:22px !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title {color:#f1e2b7 !important;font-family:Georgia,"Times New Roman",serif !important;font-size:clamp(33px,5vw,61px) !important;font-weight:900 !important;letter-spacing:.8px !important;text-shadow:2px 2px 0 #140c12,0 0 15px rgba(215,174,75,.36),4px 4px 0 rgba(72,32,68,.58) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-divider {height:3px !important;background:linear-gradient(90deg,transparent,#8a6524 10%,#e3c56f 46%,#8e4f7b 88%,transparent) !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-tier {border:1px solid #c99f42 !important;color:#e6c96e !important;background:rgba(20,10,18,.72) !important;font-family:Georgia,serif !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-source {color:#c48daf !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-kicker {color:#d9b75d !important;}#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-amount {color:#fff4cf !important;font-family:Georgia,serif !important;text-shadow:0 0 12px rgba(220,177,72,.42),3px 3px 0 #291426 !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 48%,transparent 0 13%,rgba(3,12,10,.31) 58%,rgba(0,3,3,.94) 100%),linear-gradient(120deg,rgba(28,199,107,.07),transparent 40%,rgba(207,28,42,.075)) !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-a {background:repeating-linear-gradient(0deg,rgba(91,235,158,.025) 0 1px,transparent 1px 5px),linear-gradient(90deg,transparent 0 12%,rgba(85,230,150,.07) 12% 12.3%,transparent 12.3% 87.7%,rgba(205,36,48,.07) 87.7% 88%,transparent 88%) !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-b {background:repeating-conic-gradient(from 0deg at 50% 50%,transparent 0 29deg,rgba(85,229,151,.035) 29deg 30deg,transparent 30deg 59deg,rgba(206,32,45,.03) 59deg 60deg),radial-gradient(circle at 50% 50%,transparent 0 18%,rgba(72,224,146,.065) 18.5% 19%,transparent 19.5% 31%,rgba(209,33,45,.05) 31.5% 32%,transparent 32.5%) !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-theme-fx-c {background:linear-gradient(135deg,transparent 0 48%,rgba(208,35,47,.055) 48% 48.5%,transparent 48.5% 51.5%,rgba(74,225,148,.055) 51.5% 52%,transparent 52%) !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner {border-top:3px solid #dfe9e9 !important;border-bottom:3px solid #243f37 !important;box-shadow:0 30px 76px rgba(0,0,0,.80),-15px 0 38px rgba(200,23,36,.18),15px 0 38px rgba(67,216,135,.14),inset 0 0 40px rgba(80,220,148,.035) !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::before {content:"BSL-4 CLEARANCE // COMPENSATION AUTHORIZED" !important;color:rgba(88,231,152,.66) !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-banner::after {content:"" !important;position:absolute !important;inset:0 !important;background:repeating-linear-gradient(135deg,transparent 0 18px,rgba(201,24,36,.045) 18px 22px,transparent 22px 40px),linear-gradient(90deg,transparent 0 73%,rgba(79,225,149,.04) 73% 74%,transparent 74%) !important;z-index:1 !important;}#${SCRIPT.payoutFlashId}[data-template="biohazard"] .mcms-payout-title {text-shadow:2px 2px 0 #080a0a,5px 5px 0 rgba(190,26,38,.34),0 0 18px rgba(74,222,146,.28) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 44%,transparent 0 13%,rgba(16,3,8,.34) 58%,rgba(1,1,3,.95) 100%),linear-gradient(135deg,rgba(157,20,31,.07),transparent 42%,rgba(194,166,93,.06)) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-a {background:radial-gradient(circle at 18% 20%,rgba(223,224,239,.10),transparent 18%),radial-gradient(circle at 82% 75%,rgba(156,14,29,.13),transparent 23%),repeating-radial-gradient(circle at 50% 50%,transparent 0 62px,rgba(214,172,69,.025) 63px,transparent 64px) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-theme-fx-b {background:linear-gradient(45deg,transparent 0 49.7%,rgba(219,176,73,.045) 49.8% 50.2%,transparent 50.3%),linear-gradient(135deg,transparent 0 49.7%,rgba(173,25,39,.05) 49.8% 50.2%,transparent 50.3%) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner {padding:30px 44px 26px !important;border:1px solid rgba(222,184,85,.68) !important;border-top:5px solid #a51320 !important;border-bottom:5px solid #d9ad3b !important;background:radial-gradient(circle at 50% 120%,rgba(130,9,16,.26),transparent 44%),linear-gradient(106deg,rgba(4,4,6,.99),rgba(29,7,13,.97) 49%,rgba(4,4,6,.99)),repeating-linear-gradient(35deg,rgba(255,255,255,.018) 0 1px,transparent 1px 8px) !important;box-shadow:0 32px 80px rgba(0,0,0,.84),0 0 40px rgba(173,18,29,.20),inset 0 0 40px rgba(213,168,51,.075) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::before {content:"‚ú¶" !important;left:18px !important;transform:translateY(-50%) !important;font-size:19px !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-banner::after {content:"‚ú¶" !important;right:18px !important;transform:translateY(-50%) !important;font-size:19px !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title {color:#f2e7d0 !important;font-family:Georgia,"Times New Roman",serif !important;font-size:clamp(34px,5.2vw,63px) !important;font-weight:900 !important;text-shadow:2px 2px 0 #170309,0 0 16px rgba(213,171,65,.36),4px 4px 0 rgba(108,9,20,.56) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-divider {height:3px !important;background:linear-gradient(90deg,transparent,#9c1420 10%,#e0bd63 50%,#9c1420 90%,transparent) !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-tier {border:1px solid #c99d39 !important;color:#e2c366 !important;background:rgba(17,4,9,.76) !important;font-family:Georgia,serif !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-source {color:#d7d8e6 !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-kicker {color:#d1a43e !important;}#${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-amount {color:#fff0c8 !important;font-family:Georgia,serif !important;text-shadow:0 0 12px rgba(218,174,67,.42),3px 3px 0 #4e0812 !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-cinematic {background:radial-gradient(circle at 50% 48%,transparent 0 13%,rgba(15,5,36,.30) 58%,rgba(3,2,10,.94) 100%),linear-gradient(135deg,rgba(255,84,166,.08),transparent 42%,rgba(38,224,204,.08)) !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-a {background:repeating-linear-gradient(0deg,rgba(255,255,255,.025) 0 1px,transparent 1px 4px),repeating-linear-gradient(90deg,transparent 0 31px,rgba(139,108,255,.035) 32px,transparent 33px) !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-theme-fx-b {background:radial-gradient(circle at 10% 18%,#fff36a 0 2px,transparent 3px),radial-gradient(circle at 90% 22%,#25dfcb 0 2px,transparent 3px),radial-gradient(circle at 20% 82%,#ff5aaa 0 2px,transparent 3px),radial-gradient(circle at 80% 78%,#8b6cff 0 2px,transparent 3px);background-size:110px 90px,150px 120px,190px 150px,230px 190px !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner {padding:28px 38px 24px !important;border:4px solid #f4f1ff !important;box-shadow:9px 9px 0 #5f3aca,-9px -9px 0 #22d8c3,0 30px 70px rgba(0,0,0,.76),inset 0 0 0 4px #160a38 !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner::before {content:"PLAYER 1 // CREDIT BANK" !important;position:absolute !important;top:10px !important;left:18px !important;color:#25dfcb !important;font:900 8px/1 "Courier New",monospace !important;letter-spacing:1.2px !important;text-shadow:2px 2px 0 #3c287d !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-banner::after {content:"HI-SCORE" !important;position:absolute !important;top:10px !important;right:18px !important;color:#fff36a !important;font:900 8px/1 "Courier New",monospace !important;letter-spacing:1.2px !important;text-shadow:2px 2px 0 #ff5aaa !important;z-index:2 !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-title {font-size:clamp(31px,4.8vw,56px) !important;text-shadow:4px 0 0 #ff5aaa,0 4px 0 #25dfcb,4px 4px 0 #38206f,0 0 12px rgba(255,243,106,.18) !important;}#${SCRIPT.payoutFlashId}[data-template="pixelArcade"] .mcms-payout-amount {text-shadow:3px 0 0 #ff5aaa,0 3px 0 #25dfcb,3px 3px 0 #4d2da5,0 0 10px rgba(255,255,255,.22) !important;}#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-cinematic {
            background:
                radial-gradient(circle at 50% 48%, transparent 0 14%, rgba(22,18,12,.35) 56%, rgba(3,4,3,.96) 100%),
                linear-gradient(135deg, rgba(219,119,36,.11), transparent 42%, rgba(126,168,71,.07)) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-theme-fx-a {
            background:
                repeating-linear-gradient(135deg, rgba(237,143,48,.16) 0 13px, rgba(25,26,23,.06) 13px 26px),
                repeating-linear-gradient(90deg, transparent 0 98px, rgba(238,151,55,.065) 99px, transparent 100px) !important;
            mask-image: linear-gradient(180deg, transparent 0 6%, #000 15% 85%, transparent 94%) !important;
            -webkit-mask-image: linear-gradient(180deg, transparent 0 6%, #000 15% 85%, transparent 94%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-theme-fx-b {
            background:
                repeating-linear-gradient(0deg, transparent 0 44px, rgba(191,151,93,.055) 44px 45px, transparent 45px 88px),
                repeating-linear-gradient(90deg, transparent 0 70px, rgba(191,151,93,.05) 70px 71px, transparent 71px 140px),
                radial-gradient(circle at 16% 72%, rgba(225,121,31,.16), transparent 24%),
                radial-gradient(circle at 84% 26%, rgba(138,183,72,.11), transparent 22%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-theme-fx-c {
            background:
                repeating-conic-gradient(from 0deg at 50% 50%, rgba(223,130,39,.18) 0 5deg, transparent 5deg 20deg),
                radial-gradient(circle at 50% 50%, transparent 0 16%, rgba(213,132,50,.13) 16.5% 18%, transparent 18.5% 29%, rgba(213,132,50,.09) 29.5% 31%, transparent 31.5%) !important;
            mask-image: radial-gradient(circle at center, transparent 0 13%, #000 14% 34%, transparent 55%) !important;
            -webkit-mask-image: radial-gradient(circle at center, transparent 0 13%, #000 14% 34%, transparent 55%) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-banner {
            width: min(790px, calc(100% - 26px)) !important;
            padding: 31px 42px 27px !important;
            border: 2px solid #a95e24 !important;
            border-top: 7px solid #e18a32 !important;
            border-bottom: 7px solid #282a27 !important;
            border-radius: 3px !important;
            clip-path: polygon(0 8px, 8px 0, calc(100% - 8px) 0, 100% 8px, 100% calc(100% - 8px), calc(100% - 8px) 100%, 8px 100%, 0 calc(100% - 8px)) !important;
            background:
                radial-gradient(circle at 12px 12px, #9a9b91 0 2px, #292b28 2.2px 4px, transparent 4.2px),
                radial-gradient(circle at calc(100% - 12px) 12px, #9a9b91 0 2px, #292b28 2.2px 4px, transparent 4.2px),
                radial-gradient(circle at 12px calc(100% - 12px), #9a9b91 0 2px, #292b28 2.2px 4px, transparent 4.2px),
                radial-gradient(circle at calc(100% - 12px) calc(100% - 12px), #9a9b91 0 2px, #292b28 2.2px 4px, transparent 4.2px),
                repeating-linear-gradient(135deg, rgba(244,157,48,.11) 0 2px, transparent 2px 11px),
                linear-gradient(155deg, rgba(66,68,63,.99), rgba(22,24,21,.99) 58%, rgba(39,40,36,.99)) !important;
            box-shadow:
                0 31px 82px rgba(0,0,0,.84),
                0 0 0 3px rgba(7,8,7,.80),
                0 0 42px rgba(224,126,35,.20),
                inset 0 1px rgba(255,255,255,.10),
                inset 0 -24px 44px rgba(0,0,0,.32) !important;
            overflow: hidden !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-banner::before {
            content: "AUTOMATED PRODUCTION NETWORK // OUTPUT VERIFIED" !important;
            position: absolute !important;
            top: 10px !important;
            left: 19px !important;
            right: 19px !important;
            padding: 0 0 7px !important;
            border-bottom: 1px solid rgba(226,151,73,.34) !important;
            color: #e9c892 !important;
            font: 900 7px/1 Consolas, "Courier New", monospace !important;
            letter-spacing: 1.35px !important;
            text-align: left !important;
            z-index: 2 !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-banner::after {
            content: "‚öô  ASSEMBLY LINE 01  ‚Ä¢  STATUS: OPTIMAL" !important;
            position: absolute !important;
            right: 17px !important;
            bottom: 9px !important;
            color: rgba(170,205,104,.76) !important;
            font: 900 6px/1 Consolas, monospace !important;
            letter-spacing: .9px !important;
            z-index: 2 !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-title {
            color: #f1dfb6 !important;
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif !important;
            font-size: clamp(34px, 5.15vw, 62px) !important;
            font-weight: 900 !important;
            letter-spacing: 1.4px !important;
            transform: scaleX(.94) !important;
            text-shadow: 3px 3px 0 #12130f, 6px 6px 0 rgba(180,91,25,.48), 0 0 18px rgba(239,154,62,.20) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-divider {
            height: 4px !important;
            background: repeating-linear-gradient(135deg, #e58b31 0 9px, #262823 9px 18px) !important;
            border: 1px solid rgba(242,184,104,.32) !important;
            box-shadow: 0 0 11px rgba(224,125,36,.26) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-tier {
            border: 1px solid #f0b360 !important;
            border-radius: 2px !important;
            background: #df852f !important;
            color: #17130e !important;
            font-family: Consolas, "Courier New", monospace !important;
            font-weight: 950 !important;
            letter-spacing: 1px !important;
            box-shadow: inset 0 1px rgba(255,255,255,.24), inset 4px 0 0 #242721, 0 2px 8px rgba(0,0,0,.34) !important;
            text-shadow: none !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-mission,
        #${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-source,
        #${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-kicker,
        #${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-amount {
            font-family: "Arial Narrow", "Segoe UI", sans-serif !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-mission { color: #d7c7a3 !important; }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-source { color: #a9d274 !important; letter-spacing: .7px !important; }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-kicker { color: #eda14f !important; letter-spacing: 1.2px !important; }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-amount {
            color: #ffc064 !important;
            text-shadow: 2px 2px 0 #17130e, 0 0 10px rgba(255,174,75,.72), 0 0 26px rgba(202,101,28,.28) !important;
        }#${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-theme-particle {
            border-radius: 1px !important;
            background: #ffb24d !important;
            box-shadow: 0 0 5px #ff7a22, 0 0 10px rgba(255,123,35,.62) !important;
        }
        @media (max-width:620px) {#${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner::before,
        #${SCRIPT.payoutFlashId}[data-template]:not([data-template="wasteland"]) .mcms-payout-banner::after {font-size:6px !important;letter-spacing:.8px !important;}#${SCRIPT.payoutFlashId}[data-template="gta5"] .mcms-payout-banner,
        #${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
        #${SCRIPT.payoutFlashId}[data-template="factorio"] .mcms-payout-banner,
        #${SCRIPT.payoutFlashId}[data-template="galactic"] .mcms-payout-banner {padding-left:18px !important;padding-right:18px !important;}
        }#${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-long { font-size:clamp(28px,4.35vw,51px) !important; letter-spacing:.6px !important; transform:scaleX(.90) !important; }#${SCRIPT.payoutFlashId} .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(23px,3.55vw,42px) !important; line-height:.95 !important; white-space:normal !important; text-wrap:balance !important; transform:scaleX(.92) !important; }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-long { font-size:clamp(34px,5.5vw,62px) !important; transform:rotate(-2deg) skewX(-5deg) scaleX(.92) !important; }#${SCRIPT.payoutFlashId}[data-template="viceCity"] .mcms-payout-title.mcms-payout-title-very-long { font-size:clamp(29px,4.6vw,52px) !important; line-height:.93 !important; transform:rotate(-1deg) skewX(-4deg) scaleX(.94) !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-long,
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-long { transform:none !important; }#${SCRIPT.payoutFlashId}[data-template="darkFantasy"] .mcms-payout-title.mcms-payout-title-very-long,
        #${SCRIPT.payoutFlashId}[data-template="underworld"] .mcms-payout-title.mcms-payout-title-very-long { transform:none !important; }
        @media (max-width:620px) {#${SCRIPT.payoutFlashId}[data-template="cyberpunk"] .mcms-payout-banner,
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
        @media (prefers-reduced-motion: reduce) {#${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-light {
                animation: none !important; opacity: .24 !important;
            }#${SCRIPT.payoutFlashId}.mcms-payout-active .mcms-payout-banner {
                animation: mcmsPayoutBannerReduced var(--mcms-payout-duration, 3000ms) ease-out both !important;
            }
            @keyframes mcmsPayoutBannerReduced {
                0%, 100% { opacity: 0; transform: translate(-50%, -50%); }
                3%, 97% { opacity: 1; transform: translate(-50%, -50%); }
            }
        }#${SCRIPT.toastId} { position: fixed !important; left: 12px !important; bottom: 14px !important; z-index: 982 !important; max-width: 280px !important; padding: 6px 9px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.14) !important; background: rgba(10,14,20,.92) !important; color: #fff !important; font: 900 10px/1.15 Arial, Helvetica, sans-serif !important; opacity: 0 !important; transform: translateY(4px) !important; pointer-events: none !important; transition: opacity 140ms ease, transform 140ms ease !important; box-shadow: 0 5px 14px rgba(0,0,0,.28) !important; }#${SCRIPT.toastId}.mcms-flash { opacity: 1 !important; transform: translateY(0) !important; }#${SCRIPT.panelId}.mcms-map-small { width: 292px !important; }#${SCRIPT.panelId}.mcms-map-small .mcms-grid-2 { gap: 6px !important; }#${SCRIPT.panelId}.mcms-map-small .mcms-theme-btn,
        #${SCRIPT.panelId}.mcms-map-small .mcms-toggle-btn,
        #${SCRIPT.panelId}.mcms-map-small .mcms-place-main { min-height: 40px !important; height: auto !important; padding: 5px !important; grid-template-columns: 18px minmax(0,1fr) !important; gap: 5px !important; }#${SCRIPT.panelId}.mcms-map-small .mcms-iconbox { width: 18px !important; height: 18px !important; min-width: 18px !important; font-size: 9px !important; }#${SCRIPT.panelId}.mcms-map-small .mcms-label { font-size: 10px !important; }#${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: none !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId},
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} {
            -webkit-tap-highlight-color: transparent !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} button,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} button,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} input,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} select {
            touch-action: manipulation !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
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
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(10px, env(safe-area-inset-left)) !important; top: max(10px, env(safe-area-inset-top)) !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(10px, env(safe-area-inset-right)) !important; top: max(10px, env(safe-area-inset-top)) !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(10px, env(safe-area-inset-left)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(10px, env(safe-area-inset-right)) !important; bottom: max(10px, env(safe-area-inset-bottom)) !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-shell {
            grid-area: menu !important;
            width: 52px !important; height: 48px !important; border-radius: 13px !important;
            background: rgba(8,12,18,.96) !important; backdrop-filter: none !important;
            pointer-events: auto !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 22px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 16px !important; flex-basis: 16px !important; font-size: 12px !important; }html[data-mcms-command-bar-open="false"][data-mcms-tablet-active="true"] #${SCRIPT.controlId} {
            width: 52px !important; max-width: 52px !important; grid-template-columns: 52px !important; grid-template-areas: "menu" !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
            grid-area: filters !important;
            display: grid !important;
            grid-template-columns: repeat(var(--mcms-tablet-filter-columns, 6), minmax(0,1fr)) !important;
            gap: 7px !important;
            width: 100% !important; max-width: none !important; margin-top: 0 !important;
            overflow: visible !important; padding: 0 !important;
            scrollbar-width: none !important; overscroll-behavior: auto !important;
            -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
            pointer-events: none !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
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
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) {
            opacity: .76 !important; border-color: rgba(255,255,255,.20) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
            opacity: 1 !important;
            background: linear-gradient(145deg,rgba(8,101,73,.98),rgba(10,72,94,.98) 58%,rgba(14,49,82,.98)) !important;
            border-color: #63f2b1 !important; color: #fff !important;
            box-shadow: 0 0 0 1px rgba(99,242,177,.22),0 0 16px rgba(34,211,153,.38),0 5px 14px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.18) !important;
            transform: translateY(-1px) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::before {
            content: "" !important; position: absolute !important; z-index: 1 !important; pointer-events: none !important;
            left: 5px !important; right: 5px !important; bottom: 3px !important; height: 3px !important;
            border-radius: 999px !important; background: linear-gradient(90deg,transparent,#72ffc0 18%,#61dfff 82%,transparent) !important;
            box-shadow: 0 0 8px rgba(99,242,177,.85) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
            content: "" !important; position: absolute !important; z-index: 3 !important; pointer-events: none !important; top: 5px !important; right: 5px !important;
            width: 5px !important; height: 5px !important; border-radius: 50% !important;
            background: #76ffc1 !important; box-shadow: 0 0 0 2px rgba(5,35,29,.72),0 0 8px rgba(118,255,193,.95) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-key {
            position: relative !important; z-index: 2 !important;
            width: 21px !important; height: 21px !important; border-radius: 7px !important; font-size: 10px !important;
            background: rgba(255,255,255,.11) !important; border: 1px solid rgba(255,255,255,.10) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
            background: rgba(23,198,126,.95) !important; border-color: rgba(194,255,226,.72) !important;
            box-shadow: 0 0 9px rgba(67,239,166,.55) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop { display: none !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet {
            position: relative !important; z-index: 2 !important;
            display: flex !important; align-items: center !important; justify-content: flex-start !important;
            min-width: 0 !important; min-height: 2.05em !important; max-height: 2.05em !important;
            overflow: hidden !important; text-overflow: clip !important; white-space: normal !important;
            overflow-wrap: normal !important; word-break: normal !important; hyphens: none !important;
            font-size: clamp(9px,1.1vw,10.25px) !important; line-height: 1.03 !important; letter-spacing: -.08px !important;
            font-weight: 900 !important; text-align: left !important; padding-right: 4px !important; text-shadow: 0 1px 2px rgba(0,0,0,.72) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
            grid-area: pins !important;
            display: grid !important;
            grid-template-columns: repeat(var(--mcms-tablet-pin-columns, 4), minmax(0,1fr)) !important;
            gap: 7px !important;
            width: 100% !important; max-width: none !important; max-height: none !important; margin-top: 0 !important;
            overflow: visible !important; padding: 0 !important;
            overscroll-behavior: auto !important; -webkit-overflow-scrolling: auto !important; touch-action: manipulation !important;
            pointer-events: none !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display: none !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
            flex: 0 1 auto !important; width: auto !important; min-width: 0 !important;
            height: var(--mcms-tablet-pin-height, 42px) !important; padding: 0 12px !important;
            border-radius: 10px !important; font-size: 10.5px !important; backdrop-filter: none !important;
            pointer-events: auto !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} {
            padding: 12px !important; border-radius: 18px !important;
            background: rgba(8,12,18,.985) !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
            box-shadow: 0 12px 30px rgba(0,0,0,.52) !important;
            overflow-y: auto !important; overflow-x: hidden !important; overscroll-behavior: contain !important;
            -webkit-overflow-scrolling: touch !important; touch-action: pan-y !important;
            font-size: 13px !important; line-height: 1.25 !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-header {
            position: sticky !important; top: -12px !important; z-index: 8 !important;
            grid-template-columns: minmax(0,1fr) 44px 44px !important; gap: 9px !important;
            min-height: 54px !important; margin: -12px -12px 10px !important; padding: 10px 12px 9px !important;
            background: rgba(8,12,18,.995) !important; border-bottom: 1px solid rgba(255,255,255,.16) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-drag-handle {
            cursor: default !important; touch-action: pan-y !important; padding: 2px 0 !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-title { font-size: 14px !important; letter-spacing: .45px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top: 4px !important; font-size: 10.5px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display: none !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
            width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close { font-size:24px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tabs {
            position: sticky !important; top: 42px !important; z-index: 7 !important;
            grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 8px !important;
            margin: 0 -4px 12px !important; padding: 8px 4px !important; background: rgba(8,12,18,.985) !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
            height: 44px !important; border-radius: 11px !important; font-size: 11.5px !important; padding: 0 6px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap: 9px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-place-main {
            min-height: 58px !important; height: auto !important; padding: 9px !important;
            grid-template-columns: 30px minmax(0,1fr) !important; gap: 9px !important; border-radius: 12px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-iconbox {
            width: 30px !important; height: 30px !important; min-width: 30px !important; border-radius: 9px !important; font-size: 13px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-label { font-size: 12.5px !important; line-height: 1.15 !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top: 5px !important; max-width: 120px !important; padding: 3px 7px !important; font-size: 9px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin: 14px 0 8px !important; font-size: 10.5px !important; letter-spacing: .8px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
            grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
            height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
            min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
            font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn {
            min-height: 44px !important; height: auto !important; line-height: 1.15 !important; padding: 7px 8px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns: minmax(0,1fr) 64px !important; gap: 8px !important; margin-bottom: 8px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row {
            grid-template-columns: minmax(0,1fr) 54px 54px 54px 46px !important; gap: 7px !important; margin-bottom: 8px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size: 12px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-status {
            margin-top: 10px !important; padding: 10px 11px !important; border-radius: 11px !important; font-size: 11px !important; line-height: 1.4 !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-row {
            grid-template-columns: minmax(0,1fr) 54px 54px 44px !important; gap: 7px !important;
        }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height: 52px !important; padding: 9px 10px !important; border-radius: 10px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main strong { font-size: 11.5px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-profile-main span { font-size: 9.5px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-config-actions { gap: 8px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-footer { margin-top: 14px !important; padding-top: 11px !important; font-size: 9.5px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display: none !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small { width: auto !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: block !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.toastId} {
            max-width: min(420px, calc(100vw - 24px)) !important; padding: 10px 13px !important; font-size: 12px !important;
        }
        @media (max-width: 560px) {html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row,
        html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 1fr !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { white-space: normal !important; }
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId},
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} {
            -webkit-tap-highlight-color: transparent !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} button,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} button,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} select {
            touch-action: manipulation !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
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
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-tl { left: max(5px, env(safe-area-inset-left)) !important; top: max(5px, env(safe-area-inset-top)) !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-tr { right: max(5px, env(safe-area-inset-right)) !important; top: max(5px, env(safe-area-inset-top)) !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-bl { left: max(5px, env(safe-area-inset-left)) !important; bottom: max(5px, env(safe-area-inset-bottom)) !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId}.mcms-pos-br { right: max(5px, env(safe-area-inset-right)) !important; bottom: max(5px, env(safe-area-inset-bottom)) !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-shell {
            grid-column: auto !important; grid-row: auto !important; grid-area: auto !important;
            width: auto !important; min-width: 0 !important; height: var(--mcms-mobile-filter-height,44px) !important;
            border-radius: 10px !important; background: rgba(6,10,16,.97) !important;
            border-color: rgba(116,207,255,.62) !important; box-shadow: 0 3px 10px rgba(0,0,0,.42), inset 0 1px rgba(255,255,255,.08) !important;
            backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-menu-btn { font-size: 19px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-dock-toggle-btn { height: 14px !important; flex-basis: 14px !important; font-size: 10px !important; }html[data-mcms-command-bar-open="false"][data-mcms-mobile-active="true"] #${SCRIPT.controlId} {
            width: 50px !important; max-width: 50px !important; grid-template-columns: 50px !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-floating-filter {
            display: contents !important; grid-area: auto !important; width: auto !important; max-width: none !important;
            overflow: visible !important; padding: 0 !important; margin: 0 !important; pointer-events: none !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn {
            position: relative !important; isolation: isolate !important; width: auto !important; min-width: 0 !important;
            height: var(--mcms-mobile-filter-height,44px) !important; display: grid !important;
            grid-template-columns: 17px minmax(0,1fr) !important; gap: 3px !important; padding: 0 4px !important;
            border-radius: 10px !important; border: 1px solid rgba(255,255,255,.18) !important;
            background: linear-gradient(180deg,rgba(13,19,27,.98),rgba(6,9,14,.98)) !important;
            color: rgba(255,255,255,.78) !important; box-shadow: 0 3px 10px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.04) !important;
            backdrop-filter: none !important; -webkit-backdrop-filter: none !important; pointer-events: auto !important;
            transition: background 110ms ease,border-color 110ms ease,box-shadow 110ms ease,color 110ms ease,opacity 110ms ease,transform 110ms ease !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn:not(.mcms-on) { opacity: .72 !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
            opacity: 1 !important; transform: translateY(-1px) !important;
            background: linear-gradient(145deg,rgba(7,112,76,.99),rgba(7,77,103,.99) 60%,rgba(12,43,77,.99)) !important;
            border-color: #69ffc0 !important; color: #fff !important;
            box-shadow: 0 0 0 1px rgba(105,255,192,.20),0 0 13px rgba(42,222,158,.45),0 4px 12px rgba(0,0,0,.44),inset 0 1px rgba(255,255,255,.18) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::before {
            content: "" !important; position:absolute !important; z-index:1 !important; left:4px !important; right:4px !important; bottom:2px !important;
            height:3px !important; border-radius:999px !important; background:linear-gradient(90deg,transparent,#72ffc0 18%,#62dcff 82%,transparent) !important;
            box-shadow:0 0 7px rgba(99,242,177,.9) !important; pointer-events:none !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on::after {
            content:"" !important; position:absolute !important; z-index:3 !important; right:4px !important; top:4px !important;
            width:4px !important; height:4px !important; border-radius:50% !important; background:#7affc5 !important;
            box-shadow:0 0 0 2px rgba(5,35,29,.72),0 0 7px rgba(118,255,193,.98) !important; pointer-events:none !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-key {
            position:relative !important; z-index:2 !important; width:17px !important; height:17px !important; border-radius:6px !important;
            font-size:8px !important; background:rgba(255,255,255,.10) !important; border:1px solid rgba(255,255,255,.10) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
            background:rgba(23,198,126,.96) !important; border-color:rgba(194,255,226,.75) !important; box-shadow:0 0 7px rgba(67,239,166,.58) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-desktop,
        html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-tablet { display:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-float-label-mobile {
            position:relative !important; z-index:2 !important; display:flex !important; align-items:center !important; justify-content:flex-start !important;
            min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important;
            font-size:clamp(7.5px,2.15vw,9px) !important; line-height:1 !important; font-weight:950 !important; letter-spacing:-.15px !important;
            text-align:left !important; text-shadow:0 1px 2px rgba(0,0,0,.78) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins {
            grid-area:auto !important; grid-column:1 / -1 !important; display:grid !important;
            grid-template-columns:repeat(var(--mcms-mobile-pin-columns,4),minmax(0,1fr)) !important;
            grid-auto-flow:row !important; justify-self:stretch !important; align-self:stretch !important;
            justify-items:stretch !important; align-items:stretch !important;
            gap:4px !important; width:100% !important; min-width:0 !important; max-width:none !important; max-height:none !important;
            box-sizing:border-box !important; margin:0 !important; padding:0 !important;
            overflow:visible !important; pointer-events:none !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pins:empty { display:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
            -webkit-appearance:none !important; appearance:none !important;
            display:flex !important; align-items:center !important; justify-content:center !important;
            justify-self:stretch !important; align-self:stretch !important; box-sizing:border-box !important;
            width:100% !important; max-width:none !important; min-width:0 !important;
            height:var(--mcms-mobile-pin-height,34px) !important; padding:0 7px !important;
            border-radius:9px !important; font-size:clamp(8.5px,2.25vw,10px) !important; line-height:1.05 !important;
            letter-spacing:-.08px !important; text-align:center !important; overflow:hidden !important; text-overflow:ellipsis !important;
            white-space:nowrap !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important; pointer-events:auto !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} {
            width:calc(100% - 8px) !important; max-width:calc(100% - 8px) !important;
            border-radius:16px 16px 11px 11px !important; border-color:rgba(112,204,255,.46) !important;
            padding:8px 8px calc(8px + env(safe-area-inset-bottom)) !important;
            overflow-x:hidden !important; overflow-y:auto !important; overscroll-behavior:contain !important;
            -webkit-overflow-scrolling:touch !important; touch-action:pan-y !important;
            background:linear-gradient(180deg,rgba(9,14,21,.99),rgba(4,7,11,.99)) !important;
            box-shadow:0 -12px 38px rgba(0,0,0,.58),inset 0 1px rgba(255,255,255,.06) !important;
            backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}::-webkit-scrollbar,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs::-webkit-scrollbar { display:none !important; width:0 !important; height:0 !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { scrollbar-width:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header {
            position:sticky !important; top:-8px !important; z-index:8 !important; min-height:48px !important; margin:-8px -8px 7px !important;
            grid-template-columns:minmax(0,1fr) 44px 44px !important; gap:6px !important;
            padding:8px 8px 6px !important; border-radius:16px 16px 0 0 !important; background:rgba(7,11,17,.985) !important;
            border-bottom:1px solid rgba(255,255,255,.10) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-drag-handle { cursor:default !important; touch-action:pan-y !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-title { font-size:12px !important; letter-spacing:.35px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top:3px !important; font-size:9px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-close,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-help-button { width:44px !important; height:44px !important; border-radius:12px !important; font-size:20px !important; line-height:42px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
            position:sticky !important; top:40px !important; z-index:7 !important; display:flex !important; gap:5px !important;
            margin:0 -2px 7px !important; padding:2px 2px 6px !important; overflow-x:auto !important; overflow-y:hidden !important;
            overscroll-behavior-x:contain !important; -webkit-overflow-scrolling:touch !important; background:rgba(6,10,15,.96) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
            flex:0 0 auto !important; min-width:74px !important; height:40px !important; padding:0 10px !important; border-radius:10px !important;
            font-size:10px !important; line-height:1 !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap:6px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-place-main { min-height:48px !important; height:auto !important; padding:7px !important; border-radius:11px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-iconbox { width:22px !important; height:22px !important; min-width:22px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-label { font-size:11px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top:4px !important; max-width:110px !important; font-size:8px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin:12px 0 7px !important; font-size:9.5px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:minmax(0,1fr) minmax(132px,44%) !important; gap:7px !important; margin-bottom:7px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size:10.5px !important; white-space:normal !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-input,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-select {
            min-height:44px !important; height:44px !important; border-radius:10px !important; padding:0 9px !important;
            font-size:16px !important; line-height:1.2 !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input[type="range"].mcms-input { min-height:44px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn { min-height:44px !important; height:auto !important; line-height:1.15 !important; padding:7px !important; white-space:normal !important; overflow-wrap:anywhere !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
        html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-quick-row { grid-template-columns:minmax(0,1fr) 58px !important; gap:6px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) 44px 50px 44px 40px !important; gap:4px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-name { font-size:10.5px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.35 !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:1fr !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-discord-date-grid { grid-template-columns:1fr !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-row { grid-template-columns:minmax(0,1fr) 44px 44px 40px !important; gap:4px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-profile-main { min-height:44px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-desktop-position-controls { display:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-footer { display:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.toastId} {
            left:50% !important; right:auto !important; bottom:calc(12px + env(safe-area-inset-bottom)) !important;
            max-width:calc(100vw - 24px) !important; transform:translate(-50%,8px) !important;
        }html[data-mcms-mobile-active="true"] #${SCRIPT.toastId}.mcms-flash { transform:translate(-50%,0) !important; }html[data-mcms-mobile-active="true"] .mcms-alliance-credit-badge,
        html[data-mcms-mobile-active="true"] .mcms-mission-age-badge,
        html[data-mcms-mobile-active="true"] .mcms-unit-commitment-badge,
        html[data-mcms-mobile-active="true"] .mcms-transport-watcher-badge,
        html[data-mcms-mobile-active="true"] .mcms-resource-gap-badge {
            backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
        }
        @media (max-width: 430px) {html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
        }
        @media (orientation: landscape) and (max-height: 500px) {html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { min-height:42px !important; padding-top:5px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { display:none !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { top:34px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { height:36px !important; }
        }#${SCRIPT.controlId} {
            transition: width 180ms cubic-bezier(.2,.78,.22,1), max-width 180ms cubic-bezier(.2,.78,.22,1) !important;
        }html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins {
            display: none !important;
            pointer-events: none !important;
        }
        @media (prefers-reduced-motion: reduce) {#${SCRIPT.controlId} { transition: none !important; }
        }.mcms-mission-value-row {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
            position: relative !important;
            z-index: 2 !important;
            pointer-events: none !important;
        }#navbar-alarm-spacer > .mcms-mission-value-row,
        .mcms-mission-value-row[data-mcms-host="toolbar"] {
            flex: 1 1 auto !important;
            width: 100% !important;
            min-height: 32px !important;
            margin: 0 !important;
            padding: 0 3px 0 6px !important;
            clear: none !important;
            overflow: hidden !important;
        }.mcms-mission-value-row[data-mcms-host="fallback"] {
            width: 100% !important;
            min-height: 30px !important;
            margin: 0 0 6px 0 !important;
            padding: 4px 8px !important;
            clear: both !important;
            overflow: hidden !important;
        }.mcms-mission-value-badge {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            max-width: 100% !important;
            min-width: 0 !important;
            min-height: 24px !important;
            box-sizing: border-box !important;
            padding: 4px 9px !important;
            border: 1px solid rgba(235,190,64,.72) !important;
            border-radius: 8px !important;
            background: linear-gradient(145deg, rgba(48,39,13,.96), rgba(19,21,24,.96)) !important;
            color: #ffe59a !important;
            box-shadow: 0 2px 8px rgba(0,0,0,.34) !important;
            font: 900 11px/1.2 Arial, Helvetica, sans-serif !important;
            letter-spacing: .15px !important;
            text-align: right !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            pointer-events: none !important;
        }.mcms-mission-value-row[data-mcms-mode="value"] .mcms-mission-value-badge {
            padding-left: 7px !important;
            padding-right: 7px !important;
        }
        @media (max-width: 767px) {.mcms-mission-value-row[data-mcms-host="fallback"] {
                padding: 4px 6px !important;
            }.mcms-mission-value-badge {
                font-size: 10px !important;
            }
        }.mcms-stuck-mission-icon { pointer-events:none !important; }.mcms-stuck-mission-badge { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:58px !important; height:17px !important; padding:0 6px !important; border-radius:6px !important; border:1px solid rgba(255,86,72,.72) !important; background:rgba(90,10,8,.88) !important; color:#ffd7d2 !important; font:950 8px/17px Arial,Helvetica,sans-serif !important; letter-spacing:.35px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 10px rgba(255,53,39,.32) !important; white-space:nowrap !important; }.mcms-stuck-mission-badge.mcms-stuck-severe { background:rgba(130,7,4,.94) !important; border-color:#ff3d2e !important; color:#fff !important; animation:mcmsStuckPulse 1.3s ease-in-out infinite !important; }
        @keyframes mcmsStuckPulse { 0%,100%{box-shadow:0 0 7px rgba(255,53,39,.28);transform:scale(1)} 50%{box-shadow:0 0 16px rgba(255,53,39,.70);transform:scale(1.035)} }.mcms-mission-spawn-ring { transform-box:fill-box !important; stroke:#67d9ff !important; stroke-width:3 !important; fill:rgba(48,183,255,.12) !important; transform-origin:center !important; animation:mcmsMissionSpawnRing 2.35s cubic-bezier(.12,.72,.18,1) both !important; pointer-events:none !important; }.mcms-mission-spawn-label-icon { pointer-events:none !important; }.mcms-mission-spawn-label { display:inline-flex !important; align-items:center !important; justify-content:center !important; min-width:86px !important; height:20px !important; padding:0 8px !important; border-radius:7px !important; border:1px solid rgba(98,219,255,.78) !important; background:rgba(4,22,34,.92) !important; color:#aeeeff !important; font:950 8px/20px Arial,Helvetica,sans-serif !important; letter-spacing:.65px !important; text-shadow:0 1px 2px #000 !important; box-shadow:0 0 16px rgba(67,198,255,.42) !important; animation:mcmsMissionSpawnLabel 2.35s ease-out both !important; white-space:nowrap !important; }.leaflet-marker-icon.mcms-mission-spawn-focus { animation:mcmsMissionSpawnMarker 2.2s cubic-bezier(.16,.74,.18,1) both !important; }
        @keyframes mcmsMissionSpawnRing { 0%{opacity:0;transform:scale(.25)} 12%{opacity:1;transform:scale(.55)} 75%{opacity:.50;transform:scale(3.2)} 100%{opacity:0;transform:scale(4.2)} }
        @keyframes mcmsMissionSpawnLabel { 0%{opacity:0;transform:translateY(8px) scale(.9)} 14%,72%{opacity:1;transform:translateY(0) scale(1)} 100%{opacity:0;transform:translateY(-8px) scale(.96)} }
        @keyframes mcmsMissionSpawnMarker { 0%{filter:brightness(1);transform:scale(1)} 12%{filter:brightness(1.55) drop-shadow(0 0 10px #53d9ff);transform:scale(1.22)} 34%{filter:brightness(1.15) drop-shadow(0 0 6px #53d9ff);transform:scale(.98)} 58%{filter:brightness(1.35) drop-shadow(0 0 8px #53d9ff);transform:scale(1.12)} 100%{filter:brightness(1);transform:scale(1)} }#${SCRIPT.panelId} .mcms-profile-list { display:grid !important; gap:6px !important; }#${SCRIPT.panelId} .mcms-profile-row { display:grid !important; grid-template-columns:minmax(0,1fr) 36px 36px 25px !important; gap:5px !important; align-items:center !important; }#${SCRIPT.panelId} .mcms-profile-main { min-width:0 !important; padding:6px 7px !important; border:1px solid rgba(255,255,255,.09) !important; border-radius:7px !important; background:rgba(255,255,255,.035) !important; }#${SCRIPT.panelId} .mcms-profile-main strong,
        #${SCRIPT.panelId} .mcms-profile-main span { display:block !important; min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important; }#${SCRIPT.panelId} .mcms-profile-main strong { color:#edf4fb !important; font-size:9px !important; }#${SCRIPT.panelId} .mcms-profile-main span { color:#8393a5 !important; font-size:7px !important; margin-top:2px !important; }#${SCRIPT.panelId} .mcms-config-actions { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }#${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:normal !important; text-overflow:clip !important; overflow-wrap:anywhere !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions [data-action="reset-config"] { grid-column:1 / -1 !important; }#${SCRIPT.panelId} .mcms-hidden-file { display:none !important; }#${SCRIPT.panelId} .mcms-ui-theme-grid {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 7px !important;
            margin-bottom: 7px !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-btn {
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
        }#${SCRIPT.panelId} .mcms-ui-theme-btn:hover,
        #${SCRIPT.panelId} .mcms-ui-theme-btn:focus-visible {
            transform: translateY(-1px) !important;
            border-color: rgba(124,194,255,.72) !important;
            background: rgba(93,169,255,.12) !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active {
            border-color: rgba(124,194,255,.92) !important;
            background: linear-gradient(135deg, rgba(25,118,210,.34), rgba(20,50,82,.26)) !important;
            box-shadow: inset 0 0 0 1px rgba(145,210,255,.14), 0 5px 14px rgba(0,0,0,.18) !important;
            color: #fff !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview {
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
        }#${SCRIPT.panelId} .mcms-ui-theme-preview span { display: block !important; border-radius: 2px 2px 0 0 !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(1) { height: 52% !important; background: #4c89bd !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(2) { height: 86% !important; background: #d7e8f7 !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview span:nth-child(3) { height: 68% !important; background: #2c5f87 !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk {
            border-radius: 1px !important;
            border-color: #00f0ff !important;
            background: #080b12 !important;
            box-shadow: inset 0 0 9px rgba(0,240,255,.20) !important;
            clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span { border-radius: 0 !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(1) { height: 82% !important; background: #fcee0a !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(2) { height: 48% !important; background: #00f0ff !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-cyberpunk span:nth-child(3) { height: 68% !important; background: #ff003c !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4 {
            position: relative !important;
            border-radius: 5px !important;
            border-color: #7fbd52 !important;
            background:
                repeating-linear-gradient(0deg, rgba(188,255,108,.055) 0 1px, transparent 1px 4px),
                radial-gradient(circle at 50% 44%, #172817, #071008 78%) !important;
            box-shadow: inset 0 0 12px rgba(160,255,94,.26), 0 0 8px rgba(123,206,73,.12) !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4::after {
            content: 'STAT' !important;
            position: absolute !important;
            left: 4px !important;
            top: 2px !important;
            color: #c8ff8b !important;
            font: 800 5px/1 Consolas, monospace !important;
            letter-spacing: .5px !important;
            opacity: .9 !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4 span {
            border-radius: 1px 1px 0 0 !important;
            box-shadow: 0 0 5px currentColor !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4 span:nth-child(1) { height: 66% !important; background: #78b94c !important; color: #78b94c !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4 span:nth-child(2) { height: 88% !important; background: #c8ff8b !important; color: #c8ff8b !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-fallout4 span:nth-child(3) { height: 48% !important; background: #ffcf62 !important; color: #ffcf62 !important; }#${SCRIPT.panelId} .mcms-ui-theme-btn[data-ui-theme="fallout4"] { grid-column: auto !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-umbrella {
            position: relative !important;
            border-radius: 2px !important;
            border-color: #d6193f !important;
            background:
                linear-gradient(135deg, rgba(255,255,255,.96) 0 48%, #171a20 48% 52%, #b80f30 52% 100%) !important;
            box-shadow: inset 0 0 0 1px rgba(0,0,0,.18), 0 0 8px rgba(214,25,63,.20) !important;
            clip-path: polygon(0 0, calc(100% - 7px) 0, 100% 7px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-umbrella::before {
            content: '‚ò£' !important;
            position: absolute !important;
            inset: 0 !important;
            display: grid !important;
            place-items: center !important;
            color: #ffffff !important;
            font: 900 15px/1 "Arial Narrow", "Segoe UI", sans-serif !important;
            text-shadow: 0 1px 2px rgba(0,0,0,.75) !important;
            z-index: 2 !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-umbrella::after {
            content: 'U.C.S.' !important;
            position: absolute !important;
            right: 3px !important;
            bottom: 2px !important;
            color: #ffffff !important;
            font: 900 4.7px/1 "Arial Narrow", "Segoe UI", sans-serif !important;
            letter-spacing: .55px !important;
            z-index: 3 !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-umbrella span { opacity: 0 !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio {
            position: relative !important;
            border-radius: 3px !important;
            border-color: #d17a2b !important;
            background:
                radial-gradient(circle at 5px 5px, #9b9d96 0 1px, transparent 1.4px),
                radial-gradient(circle at calc(100% - 5px) 5px, #9b9d96 0 1px, transparent 1.4px),
                repeating-linear-gradient(135deg, rgba(244,158,47,.92) 0 5px, #242521 5px 10px) 0 100% / 100% 7px no-repeat,
                linear-gradient(145deg, #42443f, #1d1f1c 66%) !important;
            box-shadow: inset 0 0 0 2px rgba(0,0,0,.36), inset 0 8px 14px rgba(255,255,255,.035), 0 0 8px rgba(214,119,35,.20) !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio::before {
            content: '‚öô' !important;
            position: absolute !important;
            left: 5px !important;
            top: 4px !important;
            color: #f0a044 !important;
            font: 900 13px/1 "Arial Narrow", "Segoe UI", sans-serif !important;
            text-shadow: 0 1px 1px #000 !important;
            z-index: 2 !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio::after {
            content: 'LINE 01' !important;
            position: absolute !important;
            right: 4px !important;
            top: 4px !important;
            color: #e7d2a1 !important;
            font: 900 4.8px/1 Consolas, monospace !important;
            letter-spacing: .4px !important;
            z-index: 2 !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span {
            border-radius: 1px 1px 0 0 !important;
            box-shadow: inset 0 1px rgba(255,255,255,.20), 0 0 3px currentColor !important;
        }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span:nth-child(1) { height: 45% !important; background: #d57b2b !important; color: #d57b2b !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span:nth-child(2) { height: 78% !important; background: #9fc55a !important; color: #9fc55a !important; }#${SCRIPT.panelId} .mcms-ui-theme-preview-factorio span:nth-child(3) { height: 60% !important; background: #e9c16e !important; color: #e9c16e !important; }#${SCRIPT.panelId} .mcms-ui-theme-btn[data-ui-theme="factorio"] { grid-column: auto !important; }#${SCRIPT.panelId} .mcms-ui-theme-copy { min-width: 0 !important; }#${SCRIPT.panelId} .mcms-ui-theme-copy strong,
        #${SCRIPT.panelId} .mcms-ui-theme-copy small { display: block !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }#${SCRIPT.panelId} .mcms-ui-theme-copy strong { color: inherit !important; font-size: 10px !important; font-weight: 950 !important; }#${SCRIPT.panelId} .mcms-ui-theme-copy small { margin-top: 4px !important; color: rgba(255,255,255,.48) !important; font-size: 7px !important; font-weight: 900 !important; letter-spacing: .7px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 72px !important; grid-template-columns: 58px minmax(0,1fr) !important; padding: 8px 10px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 58px !important; height: 44px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy strong { font-size: 13px !important; }html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-copy small { font-size: 8.5px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-grid { gap: 6px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { height: 62px !important; grid-template-columns: 46px minmax(0,1fr) !important; padding: 6px !important; }html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-preview { width: 46px !important; height: 38px !important; }html[data-mcms-ui-theme="cyberpunk"] {
            --mcms-cp-yellow: #fcee0a;
            --mcms-cp-cyan: #00f0ff;
            --mcms-cp-red: #ff003c;
            --mcms-cp-ink: #070a10;
            --mcms-cp-panel: #0b1019;
            --mcms-cp-panel-2: #111925;
            --mcms-cp-text: #f5f7ef;
            --mcms-cp-muted: #90a3ad;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} *,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId},
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} * {
            font-family: "Bahnschrift SemiCondensed", "Arial Narrow", Tahoma, Arial, sans-serif !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} {
            color: var(--mcms-cp-text) !important;
            filter: drop-shadow(0 8px 13px rgba(0,0,0,.46)) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-shell {
            border: 1px solid var(--mcms-cp-cyan) !important;
            border-radius: 1px !important;
            background: linear-gradient(145deg, rgba(12,17,27,.97), rgba(3,7,12,.96)) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-yellow), inset 0 -2px 0 rgba(255,0,60,.72), 0 0 13px rgba(0,240,255,.27), 0 7px 18px rgba(0,0,0,.48) !important;
            backdrop-filter: blur(8px) saturate(1.22) !important;
            clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 7px 100%, 0 calc(100% - 7px)) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-menu-btn {
            background: linear-gradient(135deg, rgba(252,238,10,.08), rgba(0,240,255,.04)) !important;
            color: var(--mcms-cp-yellow) !important;
            text-shadow: 1px 0 var(--mcms-cp-red), -1px 0 rgba(0,240,255,.75) !important;
            transition: background 120ms steps(2,end), color 120ms ease, filter 120ms ease !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-menu-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-menu-btn:focus-visible {
            background: var(--mcms-cp-yellow) !important;
            color: var(--mcms-cp-ink) !important;
            filter: brightness(1.08) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-dock-toggle-btn {
            border-top: 1px solid rgba(0,240,255,.64) !important;
            background: rgba(0,240,255,.08) !important;
            color: var(--mcms-cp-cyan) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-dock-toggle-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-dock-toggle-btn:focus-visible {
            background: var(--mcms-cp-cyan) !important;
            color: var(--mcms-cp-ink) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-floating-filter { gap: 5px !important; }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn {
            position: relative !important;
            border: 1px solid rgba(0,240,255,.52) !important;
            border-radius: 1px !important;
            background: linear-gradient(100deg, rgba(7,11,18,.96), rgba(15,24,35,.94)) !important;
            color: #dbeef0 !important;
            box-shadow: inset 2px 0 0 rgba(0,240,255,.65), 0 4px 10px rgba(0,0,0,.36) !important;
            clip-path: polygon(0 0, calc(100% - 7px) 0, 100% 7px, 100% 100%, 5px 100%, 0 calc(100% - 5px)) !important;
            transition: transform 110ms ease, background 110ms ease, border-color 110ms ease, color 110ms ease !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn:hover {
            transform: translateX(2px) !important;
            border-color: var(--mcms-cp-yellow) !important;
            color: #fff !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-key {
            border-radius: 0 !important;
            border: 1px solid rgba(252,238,10,.72) !important;
            background: rgba(252,238,10,.09) !important;
            color: var(--mcms-cp-yellow) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on {
            border-color: var(--mcms-cp-yellow) !important;
            background: linear-gradient(100deg, var(--mcms-cp-yellow), #d7c900) !important;
            color: var(--mcms-cp-ink) !important;
            box-shadow: inset 3px 0 0 var(--mcms-cp-red), 0 0 13px rgba(252,238,10,.32), 0 4px 10px rgba(0,0,0,.42) !important;
            animation: mcmsCyberSignal 2.8s ease-in-out infinite !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-key {
            border-color: var(--mcms-cp-ink) !important;
            background: rgba(7,10,16,.92) !important;
            color: var(--mcms-cp-yellow) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-quick {
            border-color: rgba(0,240,255,.80) !important;
            background: linear-gradient(100deg, rgba(0,240,255,.18), rgba(4,18,27,.96)) !important;
            color: #bdfaff !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-screen-pin-btn.mcms-pin-custom {
            border-color: rgba(252,238,10,.86) !important;
            background: linear-gradient(100deg, rgba(252,238,10,.16), rgba(24,22,5,.96)) !important;
            color: #fff7a2 !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} {
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
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}.mcms-open {
            animation: mcmsCyberPanelIn 190ms cubic-bezier(.16,.78,.22,1) both !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}::-webkit-scrollbar { width: 8px !important; }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}::-webkit-scrollbar-track { background: rgba(0,240,255,.06) !important; }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId}::-webkit-scrollbar-thumb { background: var(--mcms-cp-yellow) !important; border: 2px solid #0b1019 !important; }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-header {
            position: relative !important;
            border-bottom: 1px solid var(--mcms-cp-cyan) !important;
            background: linear-gradient(90deg, var(--mcms-cp-yellow) 0 76%, rgba(252,238,10,.13) 76% 100%) !important;
            margin: -3px -3px 9px -3px !important;
            padding: 5px 5px 6px 5px !important;
            overflow: hidden !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-header::after {
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
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-drag-handle {
            border: 0 !important;
            border-radius: 0 !important;
            background: transparent !important;
            padding: 2px 5px !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-title {
            color: var(--mcms-cp-ink) !important;
            font-weight: 1000 !important;
            letter-spacing: 1.25px !important;
            text-shadow: 1px 0 rgba(255,0,60,.72) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-subtitle {
            color: rgba(7,10,16,.76) !important;
            font-weight: 900 !important;
            letter-spacing: .35px !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close {
            border: 1px solid var(--mcms-cp-ink) !important;
            border-radius: 0 !important;
            background: var(--mcms-cp-ink) !important;
            color: var(--mcms-cp-yellow) !important;
            clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 0 100%) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-reset-panel:hover,
        html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close:hover {
            background: var(--mcms-cp-red) !important;
            color: #fff !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tabs {
            gap: 4px !important;
            border-bottom: 1px solid rgba(0,240,255,.20) !important;
            padding-bottom: 7px !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn {
            position: relative !important;
            border: 1px solid rgba(0,240,255,.34) !important;
            border-radius: 0 !important;
            background: rgba(0,240,255,.045) !important;
            color: #9fdce0 !important;
            letter-spacing: .55px !important;
            clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 0 100%) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
            border-color: var(--mcms-cp-cyan) !important;
            color: #fff !important;
            background: rgba(0,240,255,.12) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
            border-color: var(--mcms-cp-yellow) !important;
            background: var(--mcms-cp-yellow) !important;
            color: var(--mcms-cp-ink) !important;
            box-shadow: inset 0 -3px 0 var(--mcms-cp-red), 0 0 10px rgba(252,238,10,.20) !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
            animation: mcmsCyberTabIn 150ms steps(3,end) both !important;
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label {
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
        }html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label::before {
            content: '' !important;
            position: absolute !important;
            lef◊ﬁ}Áo ◊¨¢h≠µÁ]ôR[ò€€YT\í›\àà›[[X\ûKö[ò€€YT\í›\à
àKçJHô]ô[ùYH
œH¬àô]ô[ùYHHX]úõ›[ô
€[\
ô]ô[ùYKLçJJN¬à]YôöX⁄Y[òﬁHHMH
»›[[X\ûKõ‹\ò][ô”X\ô⁄[î\òŸ[ù
àçN¬àYà
›[[X\ûKõ‹\ò][ô—^[úŸHOOH	âà›[[X\ûKö[ò€€YHà
HYôöX⁄Y[òﬁH
œH¬àYôöX⁄Y[òﬁHHX]úõ›[ô
€[\
YôöX⁄Y[òﬁKLMJJN¬à€€ú›Z[S‹\ò][ô—^[úŸHH›[[X\ûKõ‹\ò][ô—^[úŸH»X]õX^
H»çù[Xô\ä›[[X\ûKòÿ[[ô\ë^\ HH»ç
N¬à€€ú›ù[ùÿ^Q^\»Hò[[òŸP]òZ[XõH	âàZ[S‹\ò][ô—^[úŸHà»X]õX^
ù[Xô\ä€‹⁄[ô–ò[[òŸJH
H»Z[S‹\ò][ô—^[úŸHàù[¬à]\]ZY]HHò[[òŸP]òZ[XõH»çHà¬àYà
ù[ùÿ^Q^\»OOHù[
H\]ZY]H
œHX]õX^
LÃX]õZ[äÃ
ù[ùÿ^Q^\»H H
àäJN¬à\]ZY]HHX]úõ›[ô
€[\
\]ZY]KLå
JN¬à€€ú›ÿ\^ò][»H›[[X\ûKòÿ\][[ùô\›Y[ùò][‘\òŸ[ù¬à]‹õ››H›[[X\ûKòÿ\][[ùô\›Y[ùà»ÃààN¬àYà
ÿ\^ò][»àå
H‹õ››OHN¬à[ŸHYà
ÿ\^ò][»àLå
H‹õ››OH¬à[ŸHYà
ÿ\^ò][»èHå	âàÿ\^ò][»HL
H‹õ››
œHL¬à‹õ››HX]úõ›[ô
€[\
‹õ››Lå
JN¬à]€€ôöY[òŸHH›[[X\ûKò€\‹⁄YöXÿ][€ê€€ôöY[òŸN¬àYà
X€€\]JH€€ôöY[òŸHOHN¬àYà
Xò[[òŸP]òZ[XõJH€€ôöY[òŸHOH¬àYà
ôX€€ò⁄[Y
H€€ôöY[òŸH
œHN¬à€€ôöY[òŸHHX]úõ›[ô
€[\
€€ôöY[òŸKLÕJJN¬à€€ú››ô\ò[HX]úõ›[ô
ô]ô[ùYH
àåçH
»YôöX⁄Y[òﬁH
àåçH
»\]ZY]H
àåå
»‹õ››
àåMH
»€€ôöY[òŸH
àåMJN¬à€€ú›\‹Ÿ\‹€Y[ùHö[ò[ò⁄X[ÿ€‹ôSXô[
›ô\ò[
N¬àô]\õà¬à›ô\ò[à‹òYNà\‹Ÿ\‹€Y[ùô‹òYKàXô[à\‹Ÿ\‹€Y[ùõXô[àô]ô[ùYKàYôöX⁄Y[òﬁKà\]ZY]Kà‹õ››à€€ôöY[òŸKàù[ùÿ^Q^\Œàù[ùÿ^Q^\»OOHù[»ù[àX]úõ›[ô
ù[ùÿ^Q^\»
àL
H»Là‹\ò][ô”X\ô⁄[î\òŸ[ùà›[[X\ûKõ‹\ò][ô”X\ô⁄[î\òŸ[ùàN¬àBÇàù[ò›[€àÿ[›[]Qö[ò[ò⁄X[ò]Ÿ›€ä‹[ö[ô–ò[[òŸKò[úÿX›[€ú H¬àYà
Sù[Xô\ãö\—ö[ö]Jù[Xô\ä‹[ö[ô–ò[[òŸJJJHô]\õà»XZ–ò[[òŸNàù[›–ò[[òŸNàù[\ôŸ\›ò]Ÿ›€éàù[\ôŸ\›ò]Ÿ›€î\òŸ[ùàù[N¬à]ò[[òŸHHù[Xô\ä‹[ö[ô–ò[[òŸJN¬à]XZ»Hò[[òŸN¬à]›»Hò[[òŸN¬à]\ôŸ\›ò]Ÿ›€àH¬à]\ôŸ\›ò]Ÿ›€î\òŸ[ùH¬àõ‹à
€€ú›[ùûHŸàò[úÿX›[€úÀú€XŸJ
Kú€‹ù

KäHOàKù[Y\›[\Hãù[Y\›[\
JH¬àò[[òŸH
œHù[Xô\ä[ùûKò[[›[ù
H¬àXZ»HX]õX^
XZÀò[[òŸJN¬à›»HX]õZ[ä›Àò[[òŸJN¬à€€ú›ò]Ÿ›€àHX]õX^
XZ»Hò[[òŸJN¬àYà
ò]Ÿ›€àà\ôŸ\›ò]Ÿ›€äH¬à\ôŸ\›ò]Ÿ›€àHò]Ÿ›€é¬à\ôŸ\›ò]Ÿ›€î\òŸ[ùHXZ»»ò]Ÿ›€à»XZ»
àLà¬àBàBàô]\õà»XZ–ò[[òŸNàX]úõ›[ô
XZ K›–ò[[òŸNàX]úõ›[ô
› K\ôŸ\›ò]Ÿ›€éàX]úõ›[ô
\ôŸ\›ò]Ÿ›€äK\ôŸ\›ò]Ÿ›€î\òŸ[ùàX]úõ›[ô
\ôŸ\›ò]Ÿ›€î\òŸ[ù
àL
H»LN¬àBÇàù[ò›[€àùZ[ö[ò[ò⁄X[ö\⁄–[\ù ›[[X\ûK€€\\ö\€€ã€€ù^HﬂJH¬à€€ú›[\ù»H◊N¬à€€ú›YH
Ÿ]ô\ö]K]K]Z[
HOà[\ùÀú\⁄
»Ÿ]ô\ö]K]K]Z[JN¬à€€ú›ö\⁄»HX›]ôQö[ò[ò⁄X[€XﬁOÀúö\⁄»ïRSSó—íSêSê“PS‘”P÷Kúö\⁄Œ¬àYà
X€€ù^õYŸ\ê€€\]JHY
	⁄Y⁄	À	‘\ùX[YŸ\à€›ô\òYŸIÀ	’Hô\]Y\›Y\ö[Ÿÿ\»õ›ù[Hô\öYöYYúõ€HHZ\‹⁄[€ê⁄YYàYŸ\à‹àÿÿ[\ò⁄]ôKâ N¬àYà
€€ù^õ›ô\ùöY]‘›]\»OOH	›ò\öX[òŸI HY
	⁄Y⁄	À	–‹ôY]»›ô\ùöY]»ò\öX[òŸIÀZ\‹⁄[€ê⁄YYàZ[HYŸ‹ôYÿ]\»Yôô\àúõ€HH]Z[YYŸ\àûH	Ÿõ‹õX]⁄Y€ôY‹ôY] €€ù^õ›ô\ùöY]’ò\öX[òŸJ_KàYŸ‹ôYÿ]H›[»\ŸHH›ô\ùöY]»⁄X⁄‹⁄[ù⁄[Hÿ]Y€‹öY\»ô[XZ[àYŸ\ãY\ö]ôYò
N¬à[ŸHYà
€€ù^õ›ô\ùöY]‘›]\»OOH	‹\ùX[	 HY
	€YY][IÀ	‘\ùX[›ô\ùöY]»€›ô\òYŸIÀ	”€õHH€€\]HZ[Hõ›‹»]òZ[XõHúõ€HZ\‹⁄[€ê⁄YYàŸ\ôHôX€€ò⁄[Y»Hô[XZ[ö[ô»\ö[Ÿô]Z[ú»]Z[Y[YŸ\à›[Àâ N¬à[ŸHYà
€€ù^õ›ô\ùöY]‘›]\»OOH	›[ò]òZ[XõI HY
	€›…À	–‹ôY]»›ô\ùöY]»[ò]òZ[XõIÀ	’Hô\‹ùô[XZ[ú»‹\ò][€ò[\⁄[ô»H]Z[YYŸ\ãù]Z[HYŸ‹ôYÿ]Hô\öYöXÿ][€à€›[õ›ôH€€\]Yâ N¬àYà
€€ù^ò\ò⁄]ôUù[òÿ]Y
HY
	⁄Y⁄	À	”ÿÿ[\ò⁄]ôHÿ\X⁄]HôXX⁄Y	À	”ù[Xô\ä€€ù^ôõ‹Yò[úÿX›[€ú»
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H€\àò[úÿX›[€ú»Ÿ\ôHõ›ô]Z[ôYÿÿ[Kàù[àHô\‹ù\ôX›HYÿZ[ú›Z\‹⁄[€ê⁄YYàõ‹àH⁄Y\››\úô[ùHXÿŸ\‹⁄XõHò[ôŸKò
N¬àYà
€€ù^úÿÿ[ì[Z]ôXX⁄Y
HY
	⁄Y⁄	À	”YŸ\àYŸHÿYô]Hÿ\ôXX⁄Y	À	”Z\‹⁄[€ê⁄YYà^‹ŸY[‹ôHYŸ\àYŸ\»[àH€€ôöY›\ôYY\\ÿÿ[àÿYô]Hÿ\àHô\‹ù\»^[ú⁄]ôHù]õ›€€\]Kâ N¬àYà
€€ù^úÿÿ[êÿ[òŸ[Y
HY
	€YY][IÀ	—Y\ÿÿ[à›‹Y	À	’Hô\‹ù\Ÿ\»[YŸ\»€€X›YôYõ‹ôHHÿÿ[àÿ\»›‹Yà‹ŸHYŸ\»ô[XZ[à›‹ôY[àHÿÿ[\ò⁄]ôKâ N¬àYà
›[[X\ûKò€\‹⁄YöXÿ][€ê€€ôöY[òŸHö\⁄Àò€\‹⁄YöXÿ][€ê‹ö]Xÿ[
HY
	⁄Y⁄	À	”›»€\‹⁄YöXÿ][€à€€ôöY[òŸIÀ	‹›[[X\ûKù[ò€\‹⁄YöYY€›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Hò[úÿX›[€ú»ô[XZ[à[òŸ\ùZ[é»ô]öY]»H‹öY⁄[ò[\ÿ‹ö\[€úÀò
N¬à[ŸHYà
›[[X\ûKò€\‹⁄YöXÿ][€ê€€ôöY[òŸHö\⁄Àò€\‹⁄YöXÿ][€ïÿ\õö[ô HY
	€YY][IÀ	–€\‹⁄YöXÿ][€àô]öY]»Yö\ŸY	À	‹›[[X\ûKò€\‹⁄YöXÿ][€ê€€ôöY[òŸKù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IHŸZY⁄Y€\‹⁄YöXÿ][€à€€ôöY[òŸKò
N¬àYà
›[[X\ûKõ‹\ò][ô‘ô\›[
HY
	⁄Y⁄	À	”ôYÿ]]ôH‹\ò][ô»ô\›[	À‹\ò][ô»X›]ö]H\»	Ÿõ‹õX]⁄Y€ôY‹ôY] ›[[X\ûKõ‹\ò][ô‘ô\›[
_HôYõ‹ôHÿ\][[ùô\›Y[ùò
N¬àYà
›[[X\ûKòÿ\][[ùô\›Y[ùò][‘\òŸ[ùèHö\⁄Àòÿ\][[ò€€YTò][»	âà›[[X\ûKòÿ\][[ùô\›Y[ùà
HY
	€YY][IÀ	–YŸ‹ô\‹⁄]ôHÿ\][\ﬁ[Y[ù	Àÿ\][[ùô\›Y[ù\»	‹›[[X\ûKòÿ\][[ùô\›Y[ùò][‘\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IHŸà\ö[Ÿ[ò€€YKò
N¬àYà
›[[X\ûKò[X[òŸR[ò€€YT\òŸ[ùèHö\⁄Àò[X[òŸP€€òŸ[ùò][€äHY
	€YY][IÀ	–[X[òŸH[ò€€YH€€òŸ[ùò][€âÀ	‹›[[X\ûKò[X[òŸR[ò€€YT\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IHŸà[ò€€YH\»[X[òŸKY\ö]ôYò
N¬àYà
›[[X\ûKö[ò€€YP€€òŸ[ùò][€î\òŸ[ùèHö\⁄Àòÿ]Y€‹ûP€€òŸ[ùò][€äHY
	€YY][IÀ	‘ô]ô[ùYH€€òŸ[ùò][€âÀ	‹›[[X\ûKö[ò€€YP€€òŸ[ùò][€î\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IHŸà[ò€€YHÿ[YHúõ€H	‹›[[X\ûKù‹[ò€€YPÿ]Y€‹ûOÀõXô[	€€ôHÿ]Y€‹ûIﬂKò
N¬àYà
›[[X\ûKö[ò€€YUõ€][]T\òŸ[ùèHö\⁄Àùõ€][]Uÿ\õö[ô HY
	€›…À	“Y⁄[ò€€YHõ€][]IÀùX⁄Ÿ]]ÀXùX⁄Ÿ][ò€€YHõ€][]H\»	‹›[[X\ûKö[ò€€YUõ€][]T\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IKò
N¬àYà
€€\\ö\€€à	âàù[Xô\ãö\—ö[ö]J€€\\ö\€€ãö[ò€€YP⁄[ôŸJH	âà€€\\ö\€€ãö[ò€€YP⁄[ôŸHHö\⁄Àúô]ô[ùYP€€ùòX›[€äHY
	⁄Y⁄	À	‘ô]ô[ùYH€€ùòX›[€âÀ[ò€€YHô[	”X]òXú X]úõ›[ô
€€\\ö\€€ãö[ò€€YP⁄[ôŸH
àL
H»L
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IHô\ú›\»Hô]ö[›\»\]Z]ò[[ù\ö[Ÿò
N¬àYà
ù[Xô\ãö\—ö[ö]J€€ù^ôò]Ÿ›€èÀõ\ôŸ\›ò]Ÿ›€î\òŸ[ù
H	âà€€ù^ôò]Ÿ›€ãõ\ôŸ\›ò]Ÿ›€î\òŸ[ùèHö\⁄Àôò]Ÿ›€ïÿ\õö[ô HY
	€YY][IÀ	”X]\öX[ô\Ÿ\ùôHò]Ÿ›€âÀ\ôŸ\›ôX€€ú›ùX›Yò]Ÿ›€àÿ\»	ÿ€€ù^ôò]Ÿ›€ãõ\ôŸ\›ò]Ÿ›€î\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IKò
N¬àYà
€€ù^úÿ€‹ôXÿ\ôÀúù[ùÿ^Q^\»OOHù[	âà€€ù^úÿ€‹ôXÿ\ôÀúù[ùÿ^Q^\»ö\⁄Àúù[ùÿ^P‹ö]Xÿ[^\ HY
	⁄Y⁄	À	”›»‹\ò][ô»ù[ùÿ^IÀ›\úô[ùô\Ÿ\ùôH€›ô\ú»\õﬁ[X][H	ÿ€€ù^úÿ€‹ôXÿ\ôúù[ùÿ^Q^\Àù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H^\»]HÿúŸ\ùôY‹\ò][ôÀY^[úŸHXŸKò
N¬àYà
X[\ùÀõ[ô›
HY
	Ÿ€€Ÿ	À	”õ»X]\öX[[\ù…À	”õ»€€ôöY›\ôYö[ò[ò⁄X[ö\⁄»ô\⁄€ÿ\»öYŸŸ\ôYõ‹à\»\ö[Ÿâ N¬àô]\õà[\ùÀú€XŸJ
N¬àBÇàù[ò›[€àùZ[ö[ò[ò⁄X[õ‹ôXÿ\›
›[[X\ûK\ö[Ÿ€‹⁄[ô–ò[[òŸJH¬à€€ú›\ò][€ë^\»HX]õX^
H»ç\ö[Ÿô\ò][€ì\»»ç
N¬à€€ú›Z[R[ò€€YHH›[[X\ûKö[ò€€YH»\ò][€ë^\Œ¬à€€ú›Z[S‹\ò][ô‘ô\›[H›[[X\ûKõ‹\ò][ô‘ô\›[»\ò][€ë^\Œ¬à€€ú›Ÿ]ô[ë^R[ò€€YHHX]úõ›[ô
Z[R[ò€€YH
à N¬à€€ú›\ùQ^R[ò€€YHHX]úõ›[ô
Z[R[ò€€YH
àÃ
N¬à€€ú›ôX€›ô\ûQ^\»H›[[X\ûKòÿ\][[ùô\›Y[ùà	âàZ[S‹\ò][ô‘ô\›[à»›[[X\ûKòÿ\][[ùô\›Y[ù»Z[S‹\ò][ô‘ô\›[àù[¬à][ôŸë^R[ò€€YHHù[¬àYà
\ö[ŸöYOOH	›Ÿ^I H¬à€€ú›[\ŸY›\ú»HX]õX^
åçK
]Kõõ› 
HHÿÿ[^T›\ù

JH»Õå
N¬à[ôŸë^R[ò€€YHHX]úõ›[ô
›[[X\ûKö[ò€€YH»[\ŸY›\ú»
àç
N¬àBà€€ú›€€ôöY[òŸHH›[[X\ûKòX›]ö]P€›[ùèHL	âà\ò][€ë^\»èH»»	“Q“	»à›[[X\ûKòX›]ö]P€›[ùèHçH	âà\ò][€ë^\»èHH»	”QQUSI»à	”’…Œ¬àô]\õà¬àZ[R[ò€€YNàX]úõ›[ô
Z[R[ò€€YJKàZ[S‹\ò][ô‘ô\›[àX]úõ›[ô
Z[S‹\ò][ô‘ô\›[
KàŸ]ô[ë^R[ò€€YKà\ùQ^R[ò€€YKà[ôŸë^R[ò€€YKàôX€›ô\ûQ^\ŒàôX€›ô\ûQ^\»OOHù[»ù[àX]úõ›[ô
ôX€›ô\ûQ^\»
àL
H»Làõ⁄ôX›YŸ]ô[ë^Pò[[òŸNàù[Xô\ãö\—ö[ö]Jù[Xô\ä€‹⁄[ô–ò[[òŸJJH»X]úõ›[ô
ù[Xô\ä€‹⁄[ô–ò[[òŸJH
»Z[S‹\ò][ô‘ô\›[
à Hàù[à€€ôöY[òŸBàN¬àBÇÇàù[ò›[€à›\úô[ùö[ò[ò⁄X[ô\‹ù⁄Y€ò]\ôJ
H¬àô]\õàî””ãú›ö[ô⁄YûJ¬à\ö[Ÿà›]Kô\ÿ€‹ôô\‹ùú\ö[Ÿà›\›€T›\ùà›]Kô\ÿ€‹ôô\‹ùò›\›€T›\ùà›\›€Q[ôà›]Kô\ÿ€‹ôô\‹ùò›\›€Q[ôà[ò€YP⁄\ùà›]Kô\ÿ€‹ôô\‹ùö[ò€YP⁄\ùà[ò€YP€€\\ö\€€éà›]Kô\ÿ€‹ôô\‹ùö[ò€YP€€\\ö\€€ãà€€\^]Nàõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]J›]Kô\ÿ€‹ôô\‹ùò€€\^]JKà[ò€YQõ‹ôXÿ\›à›]Kô\ÿ€‹ôô\‹ùö[ò€YQõ‹ôXÿ\›à[ò€YTö\⁄Œà›]Kô\ÿ€‹ôô\‹ùö[ò€YTö\⁄Àà‹ÿ]Y€‹öY\Œà›]Kô\ÿ€‹ôô\‹ùù‹ÿ]Y€‹öY\Ààù[Uô\ú⁄[€éàX›]ôQö[ò[ò⁄X[ù[Uô\ú⁄[€ãà€XﬁUô\ú⁄[€éàX›]ôQö[ò[ò⁄X[€XﬁUô\ú⁄[€ãà⁄[òŸS\›[ò⁄‹éà›]Kô\ÿ€‹ôô\‹ùú\ö[ŸOOH	‹⁄[òŸS\›	»»Ÿ]\›\ÿ€‹ôô\‹ù]

HààJN¬àBÇà\ﬁ[ò»ù[ò›[€àùZ[ö[ò[ò⁄X[ô\‹ù

H¬à]\ö[ŸHô\€€ôQö[ò[ò⁄X[\ö[Ÿ

N¬à€€ú›ô\‹ù€€\^]HHõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]J›]Kô\ÿ€‹ôô\‹ùò€€\^]JN¬à€€ú›€€\\ö\€€ë[òXõYH\ÿ€‹ôô\‹ù€€\^]P]X\›
	⁄[ôõ‹õX]]ôIÀô\‹ù€€\^]JH	âà›]Kô\ÿ€‹ôô\‹ùö[ò€YP€€\\ö\€€à	âà\ö[ŸöYOOH	ÿ[]òZ[XõIŒ¬à€€ú›ô\]Z\ôY›\ù\»H€€\\ö\€€ë[òXõY»\ö[Ÿò€€\\ö\€€î›\ù\»à\ö[Ÿú›\ù\Œ¬àŸ]\ÿ€‹ô›]\ 	’\][ô»⁄]Xà[ù[YŸ[òŸH[ôôXY[ô»HZ\‹⁄[€ê⁄YYàö[ò[ò⁄X[\ò⁄]ôx†)âÀ	ÿù\ﬁI N¬à]ÿZ]ôYúô\⁄ö[ò[ò⁄X[[ù[YŸ[òŸQôYY ò[ŸJN¬à€€ú›[]òZ[XõHH\ö[ŸöYOOH	ÿ[]òZ[XõIŒ¬àYà
[]òZ[XõJH¬àö[ò[òŸP\ò⁄]ôTÿÿ[êù\ﬁHHùYN¬àö[ò[òŸP\ò⁄]ôTÿÿ[êÿ[òŸ[YHò[ŸN¬àBà]YŸ\é¬àûH¬àYŸ\àH]ÿZ]ô]⁄ö[ò[ò⁄X[YŸ\äô\]Z\ôY›\ù\Àò[ŸKò[ŸJN¬àHö[ò[H¬àYà
[]òZ[XõJH¬àö[ò[òŸP\ò⁄]ôTÿÿ[êù\ﬁHHò[ŸN¬àö[ò[òŸP\ò⁄]ôTÿÿ[êÿ[òŸ[YHò[ŸN¬àBàBàYà
[]òZ[XõJH¬à€€ú›€\›HYŸ\ãõ€\›[Y\›[\YŸ\ãô[ùöY\÷ÃOÀù[Y\›[\]Kõõ› 
N¬à\ö[ŸH¬àããú\ö[Ÿà›\ù\Œà€\›à\ò][€ì\ŒàX]õX^
K\ö[Ÿô[ô\»H€\›
Kà€€\\ö\€€î›\ù\Œàà€€\\ö\€€ë[ô\Œààò[ôŸSXô[àõ‹õX]\ö[Ÿò[ôŸJ€\›\ö[Ÿô[ô\ Kà€€\\ö\€€îò[ôŸSXô[à	”õ›\XÿXõI¬àN¬àBà€€ú››\úô[ùò[úÿX›[€ú»H◊N¬à€€ú›ô]ö[›\’ò[úÿX›[€ú»H◊N¬à]Yù\î\ö[Ÿô]H¬à€€ú›õ›»H]Kõõ› 
N¬àõ‹à
€€ú›[ùûHŸàYŸ\ãô[ùöY\ H¬àYà
[ùûKù[Y\›[\èH\ö[Ÿú›\ù\»	âà[ùûKù[Y\›[\\ö[Ÿô[ô\ H›\úô[ùò[úÿX›[€úÀú\⁄
[ùûJN¬à[ŸHYà
€€\\ö\€€ë[òXõY	âà[ùûKù[Y\›[\èH\ö[Ÿò€€\\ö\€€î›\ù\»	âà[ùûKù[Y\›[\\ö[Ÿò€€\\ö\€€ë[ô\ Hô]ö[›\’ò[úÿX›[€úÀú\⁄
[ùûJN¬àYà
[ùûKù[Y\›[\èH\ö[Ÿô[ô\»	âà[ùûKù[Y\›[\Hõ› HYù\î\ö[Ÿô]
œH[ùûKò[[›[ù¬àBà€€ú››ô\ùöY]»H]ÿZ]ô]⁄‹ôY]›ô\ùöY] €€\\ö\€€ë[òXõY»\ö[Ÿò€€\\ö\€€î›\ù\»à\ö[Ÿú›\ù\À\ö[Ÿô[ô\ N¬à€€ú››\úô[ùYŸ\î›[[X\ûHH›[[X\ö\ŸQö[ò[ò⁄X[ò[úÿX›[€ú ›\úô[ùò[úÿX›[€úÀ\ö[Ÿ
N¬à€€ú››\úô[ùHôX€€ò⁄[Qö[ò[ò⁄X[›ô\ùöY] ›\úô[ùYŸ\î›[[X\ûK›\úô[ùò[úÿX›[€úÀ\ö[Ÿ›ô\ùöY] N¬à€€ú›ô]ö[›\‘\ö[ŸH»ããú\ö[Ÿ›\ù\Œà\ö[Ÿò€€\\ö\€€î›\ù\À[ô\Œà\ö[Ÿò€€\\ö\€€ë[ô\À\ò][€ì\Œà\ö[Ÿô\ò][€ì\»N¬à€€ú›ô]ö[›\”YŸ\î›[[X\ûHH€€\\ö\€€ë[òXõY»›[[X\ö\ŸQö[ò[ò⁄X[ò[úÿX›[€ú ô]ö[›\’ò[úÿX›[€úÀô]ö[›\‘\ö[Ÿ
Hàù[¬à€€ú›ô]ö[›\»Hô]ö[›\”YŸ\î›[[X\ûH»ôX€€ò⁄[Qö[ò[ò⁄X[›ô\ùöY] ô]ö[›\”YŸ\î›[[X\ûKô]ö[›\’ò[úÿX›[€úÀô]ö[›\‘\ö[Ÿ›ô\ùöY] Hàù[¬à€€ú›€€\\ö\€€àHô]ö[›\»»ùZ[ö[ò[ò⁄X[€€\\ö\€€ä›\úô[ùô]ö[›\ Hàù[¬à€€ú›Xÿ€›[ùHYŸ\ãòXÿ€›[ù¬à€€ú››\úô[ùò[[òŸHHù[Xô\ãö\—ö[ö]JXÿ€›[ùÀò›\úô[ùò[[òŸJH»Xÿ€›[ùò›\úô[ùò[[òŸHàù[¬à€€ú›€‹⁄[ô–ò[[òŸHH›\úô[ùò[[òŸHOOHù[»ù[à›\úô[ùò[[òŸHHYù\î\ö[Ÿô]¬à€€ú›‹[ö[ô–ò[[òŸHH€‹⁄[ô–ò[[òŸHOOHù[»ù[à€‹⁄[ô–ò[[òŸHH›\úô[ùõô]¬à€€ú›ò[[òŸP]òZ[XõHH‹[ö[ô–ò[[òŸHOOHù[	âà€‹⁄[ô–ò[[òŸHOOHù[¬à€€ú›ôX€€ò⁄[X][€àHÿ[›[]Uò][ôX€€ò⁄[X][€äYŸ\ãùò][\ö[ŸYŸ\ãô[ùöY\À›\úô[ùò[[òŸJN¬à€€ú››ô\ùöY]–]Y]H›\úô[ùõ›ô\ùöY]–]Y]»›]\Œà	›[ò]òZ[XõIÀXô[à	–‹ôY]»›ô\ùöY]»[ò]òZ[XõIÀ[úô\€€ôYò\öX[òŸNàN¬à€€ú›ôX€€ò⁄[X][€ìXô[H	ÿò[[òŸP]òZ[XõH»ôX€€ò⁄[X][€ãõXô[à	–ò[[òŸH[ò]òZ[XõIﬂH0≠»	€›ô\ùöY]–]Y]õXô[X¬à€€ú›ò]Ÿ›€àHÿ[›[]Qö[ò[ò⁄X[ò]Ÿ›€ä‹[ö[ô–ò[[òŸK›\úô[ùùò[úÿX›[€ú N¬à€€ú›YŸ‹ôYÿ]Uô\öYöYYH…‹ôX€€ò⁄[Y	À	€õ›X\XÿXõI◊Kö[ò€Y\ ›ô\ùöY]–]Y]ú›]\ N¬à€€ú›ÿ€‹ôXÿ\ôHÿ[›[]Qö[ò[ò⁄X[ÿ€‹ôXÿ\ô
›\úô[ù€€\\ö\€€ã»€€\]NàYŸ\ãò€€\]H	âà›ô\ùöY]–]Y]ú›]\»OOH	‹\ùX[	Àò[[òŸP]òZ[XõKôX€€ò⁄[YàôX€€ò⁄[X][€ãúôX€€ò⁄[Y	âàYŸ‹ôYÿ]Uô\öYöYY€‹⁄[ô–ò[[òŸHJN¬à]õ‹ôXÿ\››[[X\ûHH›\úô[ù¬à]õ‹ôXÿ\›\ö[ŸH\ö[Ÿ¬à€€ú›õ‹ôXÿ\›[òXõYHô\‹ù€€\^]HOOH	›€€â»	âà›]Kô\ÿ€‹ôô\‹ùö[ò€YQõ‹ôXÿ\›¬àYà
õ‹ôXÿ\›[òXõY	âà\ö[Ÿô\ò][€ì\»àÃ
àç
H¬à€€ú›ôXŸ[ù›\ùHX]õX^
\ö[Ÿú›\ù\À\ö[Ÿô[ô\»HÃ
àç
N¬à€€ú›ôXŸ[ùò[úÿX›[€ú»H›\úô[ùò[úÿX›[€úÀôö[\ä[ùûHOà[ùûKù[Y\›[\èHôXŸ[ù›\ù
N¬àõ‹ôXÿ\›\ö[ŸH»ããú\ö[Ÿ›\ù\ŒàôXŸ[ù›\ù\ò][€ì\ŒàX]õX^
K\ö[Ÿô[ô\»HôXŸ[ù›\ù
KYà	‹ôXŸ[ùÃ	»N¬àõ‹ôXÿ\››[[X\ûHH›[[X\ö\ŸQö[ò[ò⁄X[ò[úÿX›[€ú ôXŸ[ùò[úÿX›[€úÀõ‹ôXÿ\›\ö[Ÿ
N¬àBà€€ú›õ‹ôXÿ\›Hõ‹ôXÿ\›[òXõY»»ããòùZ[ö[ò[ò⁄X[õ‹ôXÿ\›
õ‹ôXÿ\››[[X\ûKõ‹ôXÿ\›\ö[Ÿ€‹⁄[ô–ò[[òŸJKò\⁄\—^\ŒàX]õX^
KX]úõ›[ô
õ‹ôXÿ\›\ö[Ÿô\ò][€ì\»»ç
JHHàù[¬à€€ú›ô\‹ùH¬àŸ[ô\ò]Y]à]Kõõ› 
Kà⁄Y€ò]\ôNà›\úô[ùö[ò[ò⁄X[ô\‹ù⁄Y€ò]\ôJ
Kà€€\^]Nàô\‹ù€€\^]Kà\ö[Ÿàô\‹ù]Nàÿÿ[\€—]J
Kàô\‹ù]SXô[à	‹\ö[ŸõXô[H0≠»	‹\ö[Ÿúò[ôŸSXô[Xà\Ÿ\ìò[YNàXÿ€›[ùÀù\Ÿ\ìò[YHYŸ\ãùò][Àú^Y\èÀõò[YH	…Àà\Ÿ\íYàXÿ€›[ùÀù\Ÿ\íYYŸ\ãùò][Àú^Y\èÀöYù[à›\úô[ùò[[òŸKà‹[ö[ô–ò[[òŸKà€‹⁄[ô–ò[[òŸKàôX€€ò⁄[X][€ëYôô\ô[òŸNàôX€€ò⁄[X][€ãôYôô\ô[òŸKàôX€€ò⁄[YàôX€€ò⁄[X][€ãúôX€€ò⁄[Yàò[[òŸPÿ[›[]Yàò[[òŸP]òZ[XõKàôX€€ò⁄[X][€ìXô[àYŸ\ê€€\]NàYŸ\ãò€€\]KàYŸ\ê€›ô\òYŸTôXX⁄YàYŸ\ãò€›ô\òYŸTôXX⁄YàYŸ\îYŸ\ŒàYŸ\ãúYŸP€›[ùàYŸ\ì\›YŸNàYŸ\ãõ\›YŸKàYŸ\î›XõNàYŸ\ãõYŸ\î›XõKàYŸ\îÿÿ[îô]öY\ŒàYŸ\ãúÿÿ[îô]öY\ÀàYŸ\îÿÿ[êÿ[òŸ[YàYŸ\ãúÿÿ[êÿ[òŸ[YàYŸ\îÿÿ[ì[Z]ôXX⁄YàYŸ\ãúÿÿ[ì[Z]ôXX⁄YàYŸ\î€›\òŸNàYŸ\ãõYŸ\î€›\òŸKà\ò⁄]ôP€€\]NàYŸ\ãò\ò⁄]ôP€€\]Kà\ò⁄]ôUù[òÿ]YàYŸ\ãò\ò⁄]ôUù[òÿ]Yàõ‹Yò[úÿX›[€úŒàYŸ\ãôõ‹Yò[úÿX›[€úÀàò][ò[úÿX›[€ê€›[ùàYŸ\ãùò][ò[úÿX›[€ê€›[ùà[ùò[Y[Y\›[\€›[ùàYŸ\ãö[ùò[Y[Y\›[\€›[ùà›ô\ùöY]–]òZ[XõNàõ€€X[ä›ô\ùöY]–]Y]ò]òZ[XõJKà›ô\ùöY]‘›]\Œà›ô\ùöY]–]Y]ú›]\Àà›ô\ùöY]”Xô[à›ô\ùöY]–]Y]õXô[à›ô\ùöY]‘õ›‹’\ŸYà›ô\ùöY]–]Y]úõ›‹’\ŸYà›ô\ùöY]‘YŸ\Œà›ô\ùöY]–]Y]úYŸP€›[ùà›ô\ùöY]”\›YŸNà›ô\ùöY]–]Y]õ\›YŸKà›ô\ùöY]–€›ô\òYŸTôXX⁄Yà›ô\ùöY]–]Y]ò€›ô\òYŸTôXX⁄Yà›ô\ùöY]”X[õ‹õYYõ›‹Œà›ô\ùöY]–]Y]õX[õ‹õYYõ›–€›[ùà›ô\ùöY]—\Xÿ]Q]\Œà›ô\ùöY]–]Y]ô\Xÿ]Q]P€›[ùà›ô\ùöY]“[ò€€YNà›ô\ùöY]–]Y]õ›ô\ùöY]“[ò€€YKà›ô\ùöY]‘‹[ô[ôŒà›ô\ùöY]–]Y]õ›ô\ùöY]‘‹[ô[ôÀà›ô\ùöY]”ô]à›ô\ùöY]–]Y]õ›ô\ùöY]”ô]àYŸ\ê⁄X⁄‹⁄[ù[ò€€YNà›ô\ùöY]–]Y]õYŸ\í[ò€€YKàYŸ\ê⁄X⁄‹⁄[ù‹[ô[ôŒà›ô\ùöY]–]Y]õYŸ\î‹[ô[ôÀàYŸ\ê⁄X⁄‹⁄[ùô]à›ô\ùöY]–]Y]õYŸ\ìô]à›ô\ùöY]“[ò€€YUò\öX[òŸNà›ô\ùöY]–]Y]ö[ò€€YUò\öX[òŸKà›ô\ùöY]‘‹[ô[ô’ò\öX[òŸNà›ô\ùöY]–]Y]ú‹[ô[ô’ò\öX[òŸKà›ô\ùöY]”ô]ò\öX[òŸNà›ô\ùöY]–]Y]õô]ò\öX[òŸKà›ô\ùöY]’[úô\€€ôYò\öX[òŸNà›ô\ùöY]–]Y]ù[úô\€€ôYò\öX[òŸKà›ô\ùöY]–]Y]àYŸ‹ôYÿ]TôX€€ò⁄[YàYŸ‹ôYÿ]Uô\öYöYYà€€\\ö\€€ãàô]ö[›\Ààÿ€‹ôXÿ\ôà‹òYNà»ÿ€‹ôNàÿ€‹ôXÿ\ôõ›ô\ò[‹òYNàÿ€‹ôXÿ\ôô‹òYKXô[àÿ€‹ôXÿ\ôõXô[X\ô⁄[î\òŸ[ùàÿ€‹ôXÿ\ôõ‹\ò][ô”X\ô⁄[î\òŸ[ùKàõ‹ôXÿ\›àò]Ÿ›€ãà⁄\ùõÿéàù[àããò›\úô[ùàN¬àô\‹ùúö\⁄–[\ù»H\ÿ€‹ôô\‹ù€€\^]P]X\›
	⁄[ôõ‹õX]]ôIÀô\‹ù€€\^]JH	âà›]Kô\ÿ€‹ôô\‹ùö[ò€YTö\⁄»»ùZ[ö[ò[ò⁄X[ö\⁄–[\ù ›\úô[ù€€\\ö\€€ã¬àYŸ\ê€€\]NàYŸ\ãò€€\]Kàò]Ÿ›€ãàÿ€‹ôXÿ\ôà\ò⁄]ôUù[òÿ]YàYŸ\ãò\ò⁄]ôUù[òÿ]Yàõ‹Yò[úÿX›[€úŒàYŸ\ãôõ‹Yò[úÿX›[€úÀàÿÿ[ì[Z]ôXX⁄YàYŸ\ãúÿÿ[ì[Z]ôXX⁄Yàÿÿ[êÿ[òŸ[YàYŸ\ãúÿÿ[êÿ[òŸ[Yà›ô\ùöY]‘›]\Œà›ô\ùöY]–]Y]ú›]\Àà›ô\ùöY]’ò\öX[òŸNà›ô\ùöY]–]Y]ù[úô\€€ôYò\öX[òŸBàJHà◊N¬àô\‹ùò⁄\ùõÿàH›]Kô\ÿ€‹ôô\‹ùö[ò€YP⁄\ù»]ÿZ]ùZ[ö[ò[ò⁄X[⁄\ùõÿäô\‹ù
Hàù[¬àô]\õàô\‹ù¬àBÇàù[ò›[€à\ÿÿ\Q\ÿ€‹ôX\öŸ›€äò[YJH¬àô]\õà›ö[ô ò[YH	… Bàúô\XŸJ◊Ÿ›K	◊	 Bàúô\XŸJ ÿ
óﬂèüJKŸ›K	◊	I Bàúô\XŸJ–Ÿ›K	–Låâ N¬àBÇàù[ò›[€àù[òÿ]Q\ÿ€‹ô
ò[YKX^[][HHT–”‘ë”PV—íQS”Së’
H¬à€€ú›^H›ö[ô ò[YH	… N¬àô]\õà^õ[ô›HX^[][H»^à	›^ú€XŸJX]õX^
X^[][HHJJ_x†)ò¬àBÇàù[ò›[€àùZ[\ÿ€‹ôÿ]Y€‹ûPúôXZŸ›€ä[ùöY\ÀôYö^[Z]
H¬à€€ú›õ›‹»H[ùöY\Àú€XŸJ[Z]
N¬àYà
\õ›‹Àõ[ô›
Hô]\õà	”õ»[ùöY\»ôX€‹ôYâŒ¬àô]\õàù[òÿ]Q\ÿ€‹ô
õ›‹ÀõX\
[ùûHOà8†(à
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€ä[ùûKõXô[
_Jäà8†%	‹ôYö^IŸ[ùûKù›[ù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H‹ôY]»0≠»	Ÿ[ùûKò€›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H[ùâŸ[ùûKò€›[ùOOHH»	ﬁI»à	⁄Y\…ﬂX
Köõ⁄[ä	◊â JN¬àBÇàù[ò›[€àùZ[\ÿ€‹ô‹^[›] ô\‹ù[Z]HJH¬àYà
\ô\‹ùù‹^[›]Àõ[ô›
Hô]\õà	”õ»‹⁄]]ôH^[›]»ôX€‹ôYâŒ¬àô]\õàù[òÿ]Q\ÿ€‹ô
ô\‹ùù‹^[›]Àú€XŸJ[Z]
KõX\

[ùûK[ô^
HOà	⁄[ô^
»_Kà
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€ä[ùûKô\ÿ‹ö\[€ä_Jäà8†%
…Ÿ[ùûKò[[›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H‹ôY]ÿ
Köõ⁄[ä	◊â JN¬àBÇàù[ò›[€àùZ[\ÿ€‹ô€€\\ö\€€ëöY[
ô\‹ù
H¬àYà
\ô\‹ùò€€\\ö\€€à\ô\‹ùúô]ö[›\ Hô]\õà	–€€\\ö\€€à\ÿXõYâŒ¬àô]\õà¬à[ò€€YNà
äâŸõ‹õX]\òŸ[ùYŸP⁄[ôŸJô\‹ùò€€\\ö\€€ãö[ò€€YP⁄[ôŸJ_Jäòà‹\ò][ô»ô\›[à
äâŸõ‹õX]\òŸ[ùYŸP⁄[ôŸJô\‹ùò€€\\ö\€€ãõ‹\ò][ô‘ô\›[⁄[ôŸJ_Jäòàÿ\][\ﬁYYà
äâŸõ‹õX]\òŸ[ùYŸP⁄[ôŸJô\‹ùò€€\\ö\€€ãòÿ\][[ùô\›Y[ù⁄[ôŸJ_JäòàX›]ôKZ›\àô[ÿ⁄]Nà
äâŸõ‹õX]\òŸ[ùYŸP⁄[ôŸJô\‹ùò€€\\ö\€€ãòX›]ôUô[ÿ⁄]P⁄[ôŸJ_JäòàZ\‹⁄[€à€›[ùà
äâ‹ô\‹ùò€€\\ö\€€ãõZ\‹⁄[€ê⁄[ôŸHà»	 …»à	…ﬂI‹ô\‹ùò€€\\ö\€€ãõZ\‹⁄[€ê⁄[ôŸKù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà]ô\òYŸHZ\‹⁄[€àô]ÿ\ôà
äâŸõ‹õX]\òŸ[ùYŸP⁄[ôŸJô\‹ùò€€\\ö\€€ãò]ô\òYŸTô]ÿ\ô⁄[ôŸJ_JäòàKöõ⁄[ä	◊â N¬àBÇàù[ò›[€àùZ[\ÿ€‹ôÿ€‹ôXÿ\ôöY[
ô\‹ù
H¬à€€ú›ÿ€‹ôHHô\‹ùúÿ€‹ôXÿ\ô¬àô]\õà¬à›ô\ò[à
äâ‹ÿ€‹ôKô‹òY_H0≠»	‹ÿ€‹ôKõ›ô\ò[KÃL
äà8†%	‹ÿ€‹ôKõXô[Xàô]ô[ùYH
äâ‹ÿ€‹ôKúô]ô[ùY_Jäà0≠»YôöX⁄Y[òﬁH
äâ‹ÿ€‹ôKôYôöX⁄Y[òﬁ_Jäòà\]ZY]H
äâ‹ÿ€‹ôKõ\]ZY]_Jäà0≠»‹õ››
äâ‹ÿ€‹ôKô‹õ››Jäòà]Y]€€ôöY[òŸH
äâ‹ÿ€‹ôKò€€ôöY[òŸ_Jäâ‹ÿ€‹ôKúù[ùÿ^Q^\»OOHù[»	…»à0≠»ù[ùÿ^H
äâ‹ÿ€‹ôKúù[ùÿ^Q^\Àù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Y
äòXàKöõ⁄[ä	◊â N¬àBÇàù[ò›[€àùZ[\ÿ€‹ôö\⁄—öY[
ô\‹ù[Z]H
H¬àYà
\ô\‹ùúö\⁄–[\ùœÀõ[ô›
Hô]\õà	‘ö\⁄»[ò[\⁄\»\ÿXõYâŒ¬àô]\õàù[òÿ]Q\ÿ€‹ô
ô\‹ùúö\⁄–[\ùÀú€XŸJX]õX^
Kù[Xô\ä[Z]
H
JKõX\
[\ùOà¬à€€ú›ﬁ[Xõ€H[\ùúŸ]ô\ö]HOOH	⁄Y⁄	»»	¸'Â-	»à[\ùúŸ]ô\ö]HOOH	€YY][I»»	¸'ÁË	»à[\ùúŸ]ô\ö]HOOH	€›…»»	¸'ÁËI»à	¸'ÁËâŒ¬àô]\õà	‹ﬁ[Xõ€H
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€ä[\ùù]J_Jäà8†%	Ÿ\ÿÿ\Q\ÿ€‹ôX\öŸ›€ä[\ùô]Z[
_X¬àJKöõ⁄[ä	◊â KL
N¬àBÇàù[ò›[€àùZ[\ÿ€‹ôõ‹ôXÿ\›öY[
ô\‹ù
H¬à€€ú›õ‹ôXÿ\›Hô\‹ùôõ‹ôXÿ\›¬àYà
Yõ‹ôXÿ\›
Hô]\õà	—õ‹ôXÿ\›[ô»\ÿXõYâŒ¬àô]\õà¬àõ‹ôXÿ\›ô[ôŸë^R[ò€€YHOOHù[»	…»àõ⁄ôX›Y[ô[ŸãY^H[ò€€YNà
äâŸõ‹õX]Z[ê‹ôY] õ‹ôXÿ\›ô[ôŸë^R[ò€€YJ_JäòàÀY^H[ò€€YHXŸNà
äâŸõ‹õX]Z[ê‹ôY] õ‹ôXÿ\›úŸ]ô[ë^R[ò€€YJ_JäòàÃY^H[ò€€YHXŸNà
äâŸõ‹õX]Z[ê‹ôY] õ‹ôXÿ\›ù\ùQ^R[ò€€YJ_Jäòàõ‹ôXÿ\›úôX€›ô\ûQ^\»OOHù[»	–ÿ\][ôX€›ô\ûNà
äìõ»‹⁄]]ôH‹\ò][ô»XŸH]òZ[XõJäâ»àÿ\][ôX€›ô\ûNà
äâŸõ‹ôXÿ\›úôX€›ô\ûQ^\Àù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H^\ äòàõ‹ôXÿ\›úõ⁄ôX›YŸ]ô[ë^Pò[[òŸHOOHù[»	…»àõ⁄ôX›YÀY^Hô\Ÿ\ùôNà
äâŸõ‹õX]Z[ê‹ôY] õ‹ôXÿ\›úõ⁄ôX›YŸ]ô[ë^Pò[[òŸJ_Jäòà€€ôöY[òŸNà
äâŸõ‹ôXÿ\›ò€€ôöY[òŸ_Jäà0≠»ò\⁄\»
äâ”ù[Xô\äõ‹ôXÿ\›òò\⁄\—^\»JKù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H^I”ù[Xô\äõ‹ôXÿ\›òò\⁄\—^\»JHOOHH»	…»à	‹…ﬂJäòàKôö[\äõ€€X[äKöõ⁄[ä	◊â N¬àBÇÇàù[ò›[€àùZ[\ÿ€‹ô]T]X[]QöY[
ô\‹ù
H¬à€€ú›€›ô\òYŸHHô\‹ùò\ò⁄]ôP€€\]H»	–€€\]HXÿŸ\‹⁄XõH\ò⁄]ôI»àô\‹ùò\ò⁄]ôUù[òÿ]Y»	”ÿÿ[\ò⁄]ôHÿ\Y	»àô\‹ùõYŸ\ê€€\]H»	—ù[ô\]Y\›Y\\ö[Ÿ€›ô\òYŸI»à	‘\ùX[ô\]Y\›Y\\ö[Ÿ€›ô\òYŸIŒ¬àô]\õà¬àYŸ\à€›\òŸNà
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùõYŸ\î€›\òŸH	”Z\‹⁄[€ê⁄YYàYŸ\â _Jäòà\ò⁄]ôH\›‹ûNà
äâ”ù[Xô\äô\‹ùùò][ò[úÿX›[€ê€›[ù
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Hò[úÿX›[€ú äà0≠»
äâÿ€›ô\òYŸ_JäòàZ\‹⁄[€ê⁄YYàYŸ\Œà
äâ”ù[Xô\äô\‹ùõYŸ\îYŸ\»
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _HôXY»	”ù[Xô\äô\‹ùõYŸ\ì\›YŸH
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H]òZ[XõJäòà€\‹⁄YöXÿ][€à€€ôöY[òŸNà
äâ‹ô\‹ùò€\‹⁄YöXÿ][€ê€€ôöY[òŸKù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IJäà0≠»ù[\»
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äX›]ôQö[ò[ò⁄X[ù[Uô\ú⁄[€ä_Jäà0≠»€XﬁH
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äX›]ôQö[ò[ò⁄X[€XﬁUô\ú⁄[€ä_Jäòà[ò€\‹⁄YöYYà
äâ‹ô\‹ùù[ò€\‹⁄YöYY€›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäà0≠»	Ÿõ‹õX]Z[ê‹ôY] ô\‹ùù[ò€\‹⁄YöYY[[›[ù
_Xà›ô\ùöY]»⁄X⁄‹⁄[ùà
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùõ›ô\ùöY]”Xô[	’[ò]òZ[XõI _Jäòàô\‹ùõ›ô\ùöY]‘õ›‹’\ŸY»›ô\ùöY]»ú»YŸ\éà[ò€€YH
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ›ô\ùöY]“[ò€€YUò\öX[òŸJ_Jäà0≠»‹[ô[ô»
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ›ô\ùöY]‘‹[ô[ô’ò\öX[òŸJ_Jäà0≠»ô]
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ›ô\ùöY]”ô]ò\öX[òŸJ_Jäòà	”›ô\ùöY]»ú»YŸ\éà
äìõ»€€\]HZ[H⁄X⁄‹⁄[ù\ŸY
äâÀàò[[òŸH]Y]à
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùúôX€€ò⁄[X][€ìXô[
_Jäòà	‹ô\‹ùõYŸ\î›XõH»	”YŸ\àXYô[XZ[ôY›XõI»à	”ô]»X›]ö]H\úö]ôY\ö[ô»ÿÿ[õö[ôŒ»Hÿÿ[\ò⁄]ôHÿ\»YùÿYô[Hô\›[XXõIﬂI‹ô\‹ùõYŸ\îÿÿ[îô]öY\»»0≠»	‹ô\‹ùõYŸ\îÿÿ[îô]öY\ﬂHô\›\ùà	…ﬂI‹ô\‹ùö[ùò[Y[Y\›[\€›[ù»0≠»	‹ô\‹ùö[ùò[Y[Y\›[\€›[ùH[ùò[Y[Y\›[\õ›‹ÿà	…ﬂI‹ô\‹ùõ›ô\ùöY]”X[õ‹õYYõ›‹»»0≠»	‹ô\‹ùõ›ô\ùöY]”X[õ‹õYYõ›‹ﬂHX[õ‹õYY›ô\ùöY]»õ›…‹ô\‹ùõ›ô\ùöY]”X[õ‹õYYõ›‹»OOHH»	…»à	‹…ﬂXà	…ﬂI‹ô\‹ùõ›ô\ùöY]—\Xÿ]Q]\»»0≠»	‹ô\‹ùõ›ô\ùöY]—\Xÿ]Q]\ﬂH\Xÿ]H›ô\ùöY]»]I‹ô\‹ùõ›ô\ùöY]—\Xÿ]Q]\»OOHH»	…»à	‹…ﬂXà	…ﬂI‹ô\‹ùõYŸ\îÿÿ[ì[Z]ôXX⁄Y»	»0≠»YŸHÿYô]Hÿ\ôXX⁄Y	»à	…ﬂI‹ô\‹ùõYŸ\îÿÿ[êÿ[òŸ[Y»	»0≠»ÿÿ[à›‹YûH\Ÿ\â»à	…ﬂXàKöõ⁄[ä	◊â N¬àBÇàù[ò›[€à\ÿ€‹ô[XôY⁄\òX›\ê€›[ù
[XôY
H¬à]›[H›ö[ô [XôYÀù]H	… Kõ[ô›
»›ö[ô [XôYÀô\ÿ‹ö\[€à	… Kõ[ô›
»›ö[ô [XôYÀôõ€›\èÀù^	… Kõ[ô›
»›ö[ô [XôYÀò]]‹èÀõò[YH	… Kõ[ô›¬àõ‹à
€€ú›öY[Ÿà[XôYÀôöY[»◊JH›[
œH›ö[ô öY[õò[YH	… Kõ[ô›
»›ö[ô öY[ùò[YH	… Kõ[ô›¬àô]\õà›[¬àBÇàù[ò›[€àö]\ÿ€‹ô[XôY’–ùYŸ]
[XôYÀX^[][HHNL
H¬à€€ú›ô\›[H[XôYÀõX\
[XôYOà
»ããô[XôYöY[Œà
[XôYôöY[»◊JKõX\
öY[Oà
»ããôöY[JJHJJN¬à€€ú›€›[ùH

HOàô\›[úôYXŸJ
›[K[XôY
HOà›[H
»\ÿ€‹ô[XôY⁄\òX›\ê€›[ù
[XôY
K
N¬à€€ú›‹[€ò[ò[Y\»H…¸'„·àY⁄\›^[›]…À	¸'‰‚àô]ö[›\»\ö[Ÿ	À	¸'Â+Hõ‹ôXÿ\›	À	¸'Â·;Ó#»]Y]]öY[òŸIÀ	¸'ÈÎH]H⁄X⁄…◊N¬à⁄[H
€›[ù

HàX^[][H	âà‹[€ò[ò[Y\Àõ[ô›
H¬à€€ú›ò[YHH‹[€ò[ò[Y\Àú⁄Yù

N¬àõ‹à
€€ú›[XôYŸàô\›[
H¬à€€ú›[ô^H[XôYôöY[Àôö[ô[ô^
öY[OàöY[õò[YHOOHò[YJN¬àYà
[ô^èH
H»[XôYôöY[Àú‹XŸJ[ô^JN»úôXZŒ»BàBàBàõ‹à
€€ú›[XôYŸàô\›[
H¬à[XôYô\ÿ‹ö\[€àHù[òÿ]Q\ÿ€‹ô
[XôYô\ÿ‹ö\[€à	…ÀŒ
N¬à[XôYôöY[»H[XôYôöY[Àú€XŸJçJKõX\
öY[Oà
»ããôöY[ò[YNàù[òÿ]Q\ÿ€‹ô
öY[õò[YKçMäKò[YNàù[òÿ]Q\ÿ€‹ô
öY[ùò[YKL
HJJN¬àBàô]\õàô\›[¬àBÇàù[ò›[€àö[ò[ò⁄X[ô\›[XY[ôJô\‹ù
H¬à€€ú›ô]HX]úõ›[ô
ù[Xô\äô\‹ùÀõô]
H
N¬àYà
ô]à
Hô]\õà[›Hö[ö\⁄Y\»\ö[Ÿ
äâŸõ‹õX]Z[ê‹ôY] ô]
_HZXY
äãò¬àYà
ô]
Hô]\õà[›Hö[ö\⁄Y\»\ö[Ÿ
äâŸõ‹õX]Z[ê‹ôY] X]òXú ô]
J_HôZ[ô
äãò¬àô]\õà	÷[›\àò[[òŸHö[ö\⁄Y\»\ö[Ÿ
äù[ò⁄[ôŸY
äãâŒ¬àBÇàù[ò›[€àùZ[\ÿ€‹ôò[[òŸQöY[
ô\‹ù»[ò€YQò]Ÿ›€àHò[ŸHHHﬂJH¬àYà
ô\‹ùõ‹[ö[ô–ò[[òŸHOOHù[ô\‹ùò€‹⁄[ô–ò[[òŸHOOHù[
Hô]\õà	”‹[ö[ô»[ô€‹⁄[ô»ò[[òŸ\»Ÿ\ôH[ò]òZ[XõKâŒ¬à€€ú›[ô\»H¬à‹[ö[ôŒà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùõ‹[ö[ô–ò[[òŸJ_Jäòà€‹⁄[ôŒà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùò€‹⁄[ô–ò[[òŸJ_JäòàN¬àYà
[ò€YQò]Ÿ›€äH¬à[ô\Àú\⁄
XZŒà
äâ‹ô\‹ùôò]Ÿ›€ãúXZ–ò[[òŸHOOHù[»	’[ò]òZ[XõI»àõ‹õX]Z[ê‹ôY] ô\‹ùôò]Ÿ›€ãúXZ–ò[[òŸJ_Jäò
N¬à[ô\Àú\⁄
\ôŸ\›õ‹úõ€HHXZŒà
äâ‹ô\‹ùôò]Ÿ›€ãõ\ôŸ\›ò]Ÿ›€àOOHù[»	’[ò]òZ[XõI»àõ‹õX]Z[ê‹ôY] ô\‹ùôò]Ÿ›€ãõ\ôŸ\›ò]Ÿ›€ä_I‹ô\‹ùôò]Ÿ›€ãõ\ôŸ\›ò]Ÿ›€î\òŸ[ùOOHù[»	…»à0≠»	‹ô\‹ùôò]Ÿ›€ãõ\ôŸ\›ò]Ÿ›€î\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IXJäò
N¬àBàô]\õàù[òÿ]Q\ÿ€‹ô
[ô\Àöõ⁄[ä	◊â JN¬àBÇàù[ò›[€àùZ[\ÿ€‹ô]P⁄X⁄—öY[
ô\‹ù»]Z[YHò[ŸHHHﬂJH¬àYà
]Z[Y
Hô]\õàù[òÿ]Q\ÿ€‹ô
ùZ[\ÿ€‹ô]T]X[]QöY[
ô\‹ù
JN¬àYà
\ô\‹ùõYŸ\ê€€\]JHô]\õà	¯¶®;Ó#»
äî\ùX[
äà8†%õ›[ô\]Y\›YZ\‹⁄[€ê⁄YYàX›]ö]Hÿ\»]òZ[XõKâŒ¬àYà
ô\‹ùòYŸ‹ôYÿ]TôX€€ò⁄[Y
Hô]\õà	¯ß!H
äê⁄X⁄ŸY
äà8†%H]Z[YYŸ\à[ô]òZ[XõHZ[H›[»Y‹ôYKâŒ¬àYà
ô\‹ùõ›ô\ùöY]‘›]\»OOH	›ò\öX[òŸI Hô]\õà	¯¶®;Ó#»
äîô]öY]»Yö\ŸY
äà8†%Z\‹⁄[€ê⁄YYàZ[H›[»[ôYŸ\à]Z[»õ›ù[HY‹ôYKâŒ¬àô]\õà	¯ß!H
äê€€\]HYŸ\ääà8†%Z[H›[‹õ‹‹ÀX⁄X⁄⁄[ô»ÿ\»õ›ù[H]òZ[XõKâŒ¬àBÇàù[ò›[€àùZ[\ÿ€‹ôX›]ö]QöY[
ô\‹ù»]Z[YHò[ŸHHHﬂJH¬à€€ú›õ›‹»H¬àZ\‹⁄[€ã›ò[ú‹‹ùô]ÿ\ôŒà
äâ‹ô\‹ùõZ\‹⁄[€ê€›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòàò[úÿX›[€ú»€›[ùYà
äâ‹ô\‹ùòX›]ö]P€›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà]ô\òYŸHZ\‹⁄[€àô]ÿ\ôà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùò]ô\òYŸSZ\‹⁄[€îô]ÿ\ô
_JäòàN¬àYà
]Z[Y
H¬àõ›‹Àú\⁄
X›]ôH[YH\›[X]Nà
äâ‹ô\‹ùòX›]ôR›\úÀù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Z
äò
N¬àõ›‹Àú\⁄
[ò€€YH\àX›]ôH›\éà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùòX›]ôR[ò€€YT\í›\ä_Jäò
N¬àõ›‹Àú\⁄
[X[òŸH»\ú€€ò[⁄\ôNà
äâ‹ô\‹ùò[X[òŸR[ò€€YT\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IH»	‹ô\‹ùú\ú€€ò[[ò€€YT\òŸ[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _IJäò
N¬àBàô]\õàù[òÿ]Q\ÿ€‹ô
õ›‹Àöõ⁄[ä	◊â JN¬àBÇàù[ò›[€àùZ[\ÿ€‹ôö[ò[ò⁄X[^[ÿY
ô\‹ù»⁄]]X⁄Y[ùHò[ŸHHHﬂJH¬à€€ú›€€\^]HHõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]Jô\‹ùò€€\^]H›]Kô\ÿ€‹ôô\‹ùò€€\^]JN¬à€€ú›ô\›[€ôHHô\‹ù€ôJô\‹ùõô]
N¬à€€ú›€€›\àHô\›[€ôHOOH	‹‹⁄]]ôI»»ôXÿÕÃHàô\›[€ôHOOH	€ôYÿ]]ôI»»MÕÃÿ»àåXÕé¬à€€ú›‹[Z]H›]Kô\ÿ€‹ôô\‹ùù‹ÿ]Y€‹öY\Œ¬à€€ú›\ö[Ÿ\ÿ‹ö\[€àH¬à
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùú\ö[ŸõXô[
_Jäòà\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùú\ö[Ÿúò[ôŸSXô[
Kàô\‹ùú\ö[Ÿõõ›H»…Ÿ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùú\ö[Ÿõõ›J_Wÿà	…¬àKôö[\äõ€€X[äKöõ⁄[ä	◊â N¬à€€ú›€€[[€ëöY[»H¬à»ò[YNà	¸'‰¨[€ô^H[âÀò[YNà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùö[ò€€YJ_Jäò[õ[ôNàùYHKà»ò[YNà	¸'‰Æ[€ô^H›]	Àò[YNà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùú‹[ô[ô _Jäò[õ[ôNàùYHKà»ò[YNàô\‹ùõô]èH»	¸'‰‚ô]⁄[ôŸI»à	¸'‰‚Hô]⁄[ôŸIÀò[YNà
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõô]
_Jäò[õ[ôNàùYHBàN¬à€€ú›⁄[\HH¬à]Nà	¸'‰≠»Z\‹⁄[€ê⁄YYàö[ò[òŸHô\‹ù	Àà\ÿ‹ö\[€éàù[òÿ]Q\ÿ€‹ô
‹\ö[Ÿ\ÿ‹ö\[€ãö[ò[ò⁄X[ô\›[XY[ôJô\‹ù
WKôö[\äõ€€X[äKöõ⁄[ä	◊óâ KMäKà€€‹éà€€›\ãà[Y\›[\àô]»]Jô\‹ùôŸ[ô\ò]Y]
Kù“T”‘›ö[ô 
KàöY[Œà¬àããò€€[[€ëöY[Àà»ò[YNà	¸'„Èàò[[òŸIÀò[YNàùZ[\ÿ€‹ôò[[òŸQöY[
ô\‹ù
K[õ[ôNàùYHKà»ò[YNà	¸'Ê™X›]ö]IÀò[YNàùZ[\ÿ€‹ôX›]ö]QöY[
ô\‹ù
K[õ[ôNàùYHKà»ò[YNà	¯ß!H]H⁄X⁄…Àò[YNàùZ[\ÿ€‹ô]P⁄X⁄—öY[
ô\‹ù
K[õ[ôNàò[ŸHBàKàõ€›\éà»^à	‘–‘íTõò[Y_H8†(à⁄[\Hô\‹ù8†(àâ‘–‘íTùô\ú⁄[€üXBàN¬à€€ú›[ôõ‹õX]]ôQöY[»H¬àããò€€[[€ëöY[Àà»ò[YNà	¸'ÈÔàù[õö[ô»€‹›…Àò[YNà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùõ‹\ò][ô—^[úŸJ_Jäò[õ[ôNàùYHKà»ò[YNà	¸'„Â˚Ó#»[ùô\›Y[ù	à^[ú⁄[€âÀò[YNà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùòÿ\][[ùô\›Y[ù
_Jäò[õ[ôNàùYHKà»ò[YNàô\‹ùõ‹\ò][ô‘ô\›[èH»	¸'‰‚àô\›[ôYõ‹ôH[ùô\›Y[ù	»à	¯¶®;Ó#»ô\›[ôYõ‹ôH[ùô\›Y[ù	Àò[YNà
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ‹\ò][ô‘ô\›[
_Jäò[õ[ôNàùYHKà»ò[YNà	¸'„Èàò[[òŸIÀò[YNàùZ[\ÿ€‹ôò[[òŸQöY[
ô\‹ù
K[õ[ôNàùYHKà»ò[YNà	¸'Ê™X›]ö]IÀò[YNàùZ[\ÿ€‹ôX›]ö]QöY[
ô\‹ù
K[õ[ôNàùYHKà»ò[YNà	¸'ÁËàXZ[à[ò€€YH€›\òŸ\…Àò[YNàùZ[\ÿ€‹ôÿ]Y€‹ûPúôXZŸ›€äô\‹ùö[ò€€YPÿ]Y€‹öY\À	 …À‹[Z]
K[õ[ôNàò[ŸHKà»ò[YNà	¸'Â-XZ[à‹[ô[ô…Àò[YNàùZ[\ÿ€‹ôÿ]Y€‹ûPúôXZŸ›€äô\‹ùú‹[ô[ô–ÿ]Y€‹öY\À	ÀIÀ‹[Z]
K[õ[ôNàò[ŸHBàN¬àYà
ô\‹ùò€€\\ö\€€à	âàô\‹ùúô]ö[›\ H[ôõ‹õX]]ôQöY[Àú\⁄
»ò[YNà	¸'‰‚àô]ö[›\»\ö[Ÿ	Àò[YNàù[òÿ]Q\ÿ€‹ô
ùZ[\ÿ€‹ô€€\\ö\€€ëöY[
ô\‹ù
JK[õ[ôNàò[ŸHJN¬àYà
ô\‹ùúö\⁄–[\ùœÀõ[ô›
H[ôõ‹õX]]ôQöY[Àú\⁄
»ò[YNà	¸'‰®H[ô‹»»€õ›…Àò[YNàùZ[\ÿ€‹ôö\⁄—öY[
ô\‹ù K[õ[ôNàò[ŸHJN¬à[ôõ‹õX]]ôQöY[Àú\⁄
»ò[YNà	¯ß!H]H⁄X⁄…Àò[YNàùZ[\ÿ€‹ô]P⁄X⁄—öY[
ô\‹ù
K[õ[ôNàò[ŸHJN¬à€€ú›[ôõ‹õX]]ôHH¬à]Nà	¸'‰‚àZ\‹⁄[€ê⁄YYàö[ò[òŸH8†%[ôõ‹õX]]ôHô\‹ù	Àà\ÿ‹ö\[€éàù[òÿ]Q\ÿ€‹ô
¬à\ö[Ÿ\ÿ‹ö\[€ãàö[ò[ò⁄X[ô\›[XY[ôJô\‹ù
KàôYõ‹ôH[ùô\›Y[ù[ô^[ú⁄[€à‹[ô[ôÀHô\›[ÿ\»
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ‹\ò][ô‘ô\›[
_JäãòàKôö[\äõ€€X[äKöõ⁄[ä	◊óâ KMäKà€€‹éà€€›\ãà[Y\›[\àô]»]Jô\‹ùôŸ[ô\ò]Y]
Kù“T”‘›ö[ô 
KàöY[Œà[ôõ‹õX]]ôQöY[Ààõ€›\éà»^à	‘–‘íTõò[Y_H8†(à[ôõ‹õX]]ôHô\‹ù8†(àâ‘–‘íTùô\ú⁄[€üXBàN¬à€€ú›€€ë^X›]]ôHH¬à]Nà	¸'‰.àZ\‹⁄[€ê⁄YYàö[ò[òŸH8†%H€€âÀà\ÿ‹ö\[€éàù[òÿ]Q\ÿ€‹ô
¬à\ö[Ÿ\ÿ‹ö\[€ãàö[ò[ò⁄X[ô\›[XY[ôJô\‹ù
Kà[ò€€YHÿ\»
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùö[ò€€YJ_Jäà[ô›[‹[ô[ô»ÿ\»
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùú‹[ô[ô _Jäãòà‹\ò][ô»ô\›[ôYõ‹ôH[ùô\›Y[ùà
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ‹\ò][ô‘ô\›[
_Jäãòàô\‹ùù\Ÿ\ìò[YH»Xÿ€›[ùà
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùù\Ÿ\ìò[YJ_Jäâ‹ô\‹ùù\Ÿ\íY»0≠»Q	Ÿ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äô\‹ùù\Ÿ\íY
_Xà	…ﬂXà	…¬àKôö[\äõ€€X[äKöõ⁄[ä	◊â KMäKà€€‹éà€€›\ãà[Y\›[\àô]»]Jô\‹ùôŸ[ô\ò]Y]
Kù“T”‘›ö[ô 
KàöY[Œà¬àããò€€[[€ëöY[Àà»ò[YNà	¸'ÈÔàù[õö[ô»€‹›…Àò[YNà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùõ‹\ò][ô—^[úŸJ_Jäò[õ[ôNàùYHKà»ò[YNà	¸'„Â˚Ó#»ÿ\][\ﬁYY	Àò[YNà
äâŸõ‹õX]Z[ê‹ôY] ô\‹ùòÿ\][[ùô\›Y[ù
_Jäò[õ[ôNàùYHKà»ò[YNàô\‹ùõ‹\ò][ô‘ô\›[èH»	¸'‰‚à‹\ò][ô»ô\›[	»à	¯¶®;Ó#»‹\ò][ô»ô\›[	Àò[YNà
äâŸõ‹õX]⁄Y€ôY‹ôY] ô\‹ùõ‹\ò][ô‘ô\›[
_Jäò[õ[ôNàùYHKà»ò[YNà	¸'„Èà\]ZY]H	àò]Ÿ›€âÀò[YNàùZ[\ÿ€‹ôò[[òŸQöY[
ô\‹ù»[ò€YQò]Ÿ›€éàùYHJK[õ[ôNàùYHKà»ò[YNà	¯¶®HõŸX›]ö]IÀò[YNàùZ[\ÿ€‹ôX›]ö]QöY[
ô\‹ù»]Z[YàùYHJK[õ[ôNàùYHKà»ò[YNà	¸'„·Hö[ò[ò⁄X[ÿ€‹ôXÿ\ô	Àò[YNàù[òÿ]Q\ÿ€‹ô
ùZ[\ÿ€‹ôÿ€‹ôXÿ\ôöY[
ô\‹ù
JK[õ[ôNàùYHKà»ò[YNà	¸'Ê™[ù[YŸ[òŸH[\ù…Àò[YNàùZ[\ÿ€‹ôö\⁄—öY[
ô\‹ù
K[õ[ôNàò[ŸHKà»ò[YNà	¸'‰‚àô]ö[›\»\ö[Ÿ	Àò[YNàù[òÿ]Q\ÿ€‹ô
ùZ[\ÿ€‹ô€€\\ö\€€ëöY[
ô\‹ù
JK[õ[ôNàò[ŸHBàKàõ€›\éà»^à	‘–‘íTõò[Y_H8†(àH€€à8†(àâ‘–‘íTùô\ú⁄[€üH8†(à[ù[YŸ[òŸH	ÿX›]ôQö[ò[ò⁄X[ù[Uô\ú⁄[€üH»	ÿX›]ôQö[ò[ò⁄X[€XﬁUô\ú⁄[€üXBàN¬à€€ú›€€ê]Y]H¬à]Nà	¸'ÈËH€€à8†%]Z[	à]öY[òŸIÀà€€‹éàÕNãàöY[Œà¬à»ò[YNà	¸'ÁËà[ò€€YH€\‹⁄YöXÿ][€âÀò[YNàùZ[\ÿ€‹ôÿ]Y€‹ûPúôXZŸ›€äô\‹ùö[ò€€YPÿ]Y€‹öY\À	 …À‹[Z]
K[õ[ôNàò[ŸHKà»ò[YNà	¸'ÈÔà‹\ò][ô»^[ô]\ôIÀò[YNàùZ[\ÿ€‹ôÿ]Y€‹ûPúôXZŸ›€äô\‹ùõ‹\ò][ô—^[úŸPÿ]Y€‹öY\À	ÀIÀ‹[Z]
K[õ[ôNàùYHKà»ò[YNà	¸'„Â˚Ó#»ÿ\][\ﬁ[Y[ù	Àò[YNàùZ[\ÿ€‹ôÿ]Y€‹ûPúôXZŸ›€äô\‹ùòÿ\][ÿ]Y€‹öY\À	ÀIÀ‹[Z]
K[õ[ôNàùYHKà»ò[YNà	¸'„·àY⁄\›^[›]…Àò[YNàùZ[\ÿ€‹ô‹^[›] ô\‹ùX]õZ[äK‹[Z]
JK[õ[ôNàò[ŸHKà»ò[YNà	¸'Â+Hõ‹ôXÿ\›	Àò[YNàù[òÿ]Q\ÿ€‹ô
ùZ[\ÿ€‹ôõ‹ôXÿ\›öY[
ô\‹ù
JK[õ[ôNàùYHKà»ò[YNà	¸'Â·;Ó#»]Y]]öY[òŸIÀò[YNàùZ[\ÿ€‹ô]P⁄X⁄—öY[
ô\‹ù»]Z[YàùYHJK[õ[ôNàò[ŸHBàKàõ€›\éà»^à	”‹\ò][ô»\ôõ‹õX[òŸH\»Ÿ\\ò]Yúõ€Hÿ\][[ùô\›Y[ùàõ‹ôXÿ\›»\ôH[ôXÿ]]ôKõ››X\ò[ùYYâ»BàN¬à][XôY»H€€\^]HOOH	‹⁄[\I»»‹⁄[\WHà€€\^]HOOH	›€€â»»›€€ë^X›]]ôK€€ê]Y]Hà⁄[ôõ‹õX]]ôWN¬àYà
⁄]]X⁄Y[ù
H[XôY÷ÃKö[XYŸHH»\õà]X⁄Y[ùãÀ…—íSêSê—W–“Tï—íSSêSQ_XN¬à[XôY»Hö]\ÿ€‹ô[XôY’–ùYŸ]
[XôY N¬à€€ú›^[ÿYH¬à\Ÿ\õò[YNà›]Kô\ÿ€‹ôô\‹ùùŸXö€⁄”ò[YH	”Z\‹⁄[€ê⁄YYàö[ò[òŸIÀà[›ŸY€Y[ù[€úŒà»\úŸNà◊HKà[XôY¬àN¬àYà
⁄]]X⁄Y[ù
H^[ÿYò]X⁄Y[ù»Hﬁ»Yàö[[ò[YNàíSêSê—W–“Tï—íSSêSQK\ÿ‹ö\[€éà	‹ô\‹ùú\ö[ŸõXô[HZ\‹⁄[€ê⁄YYà	ÿ€€\^]_Hö[ò[òŸHô\‹ùWN¬àô]\õà^[ÿY¬àBàù[ò›[€àõ›[ôôX›]
€€ù^K⁄YZY⁄òY]\ H¬à€€ú›àHX]õX^
X]õZ[äòY]\À⁄Y»ãZY⁄»äJN¬à€€ù^òôY⁄[î]

N¬à€€ù^õ[›ôU 
»ãJN¬à€€ù^ò\ò’ 
»⁄YK
»⁄YH
»ZY⁄äN¬à€€ù^ò\ò’ 
»⁄YH
»ZY⁄H
»ZY⁄äN¬à€€ù^ò\ò’ H
»ZY⁄KäN¬à€€ù^ò\ò’ K
»⁄YKäN¬à€€ù^ò€‹ŸT]

N¬àBÇàù[ò›[€àò]—ö[ò[ò⁄X[Y]öX–ÿ\ô
€€ù^K⁄YZY⁄Xô[ò[YKXÿŸ[ù
H¬àõ›[ôôX›]
€€ù^K⁄YZY⁄N
N¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKåMJIŒ¬à€€ù^ôö[

N¬à€€ù^ôö[›[HHXÿŸ[ù¬à€€ù^ôö[ôX›
KKZY⁄
N¬à€€ú›Xô[^[›]Hö]ö[ò[ò⁄X[ÿ[ùò\’^
€€ù^›ö[ô Xô[	… Kù’\\êÿ\ŸJ
K⁄YH»ŸZY⁄àÃ⁄^ôNàMãZ[î⁄^ôNàLHJN¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKçN
IŒ¬à€€ù^ôõ€ùHÃ	€Xô[^[›]ôõ€ù⁄^ô_\\öX[ÿ[úÀ\Ÿ\öYò¬à€€ù^ôö[^
Xô[^[›]ù^
»çH
»ÃJN¬à€€ú›ò[YS^[›]Hö]ö[ò[ò⁄X[ÿ[ùò\’^
€€ù^ò[YK⁄YH»ŸZY⁄àL⁄^ôNàÃKZ[î⁄^ôNàNJN¬à€€ù^ôö[›[HH	»ŸôôôôôâŒ¬à€€ù^ôõ€ùHL	›ò[YS^[›]ôõ€ù⁄^ô_\\öX[ÿ[úÀ\Ÿ\öYò¬à€€ù^ôö[^
ò[YS^[›]ù^
»çH
»ÕJN¬àBÇàù[ò›[€àö]ö[ò[ò⁄X[ÿ[ùò\’^
€€ù^ò[YKX^⁄Y»ŸZY⁄Hå⁄^ôHHMKZ[î⁄^ôHHLHHHﬂJH¬à€€ú›€›\òŸU^H›ö[ô ò[YHœ»	… N¬à€€ú›⁄Y[Z]HX]õX^
Kù[Xô\äX^⁄Y
HJN¬à]õ€ù⁄^ôHHX]õX^
Z[î⁄^ôKù[Xô\ä⁄^ôJHMJN¬à€€ú›\Qõ€ùH

HOà¬à€€ù^ôõ€ùH	›ŸZY⁄H	Ÿõ€ù⁄^ô_\\öX[ÿ[úÀ\Ÿ\öYò¬àN¬à\Qõ€ù

N¬à⁄[H
õ€ù⁄^ôHàZ[î⁄^ôH	âà€€ù^õYX\›\ôU^
€›\òŸU^
Kù⁄Yà⁄Y[Z]
H¬àõ€ù⁄^ôHOHN¬à\Qõ€ù

N¬àBà]ô[ô\ôY^H€›\òŸU^¬à]YX\›\ôY⁄YH€€ù^õYX\›\ôU^
ô[ô\ôY^
Kù⁄Y¬àYà
YX\›\ôY⁄Yà⁄Y[Z]
H¬à]ô[XZ[ö[ô»H€›\òŸU^¬à⁄[H
ô[XZ[ö[ôÀõ[ô›àJH¬àô[XZ[ö[ô»Hô[XZ[ö[ôÀú€XŸJLJN¬à€€ú›ÿ[ôY]HH	‹ô[XZ[ö[ôﬂx†)ò¬à€€ú›ÿ[ôY]U⁄YH€€ù^õYX\›\ôU^
ÿ[ôY]JKù⁄Y¬àYà
ÿ[ôY]U⁄YH⁄Y[Z]
H¬àô[ô\ôY^Hÿ[ôY]N¬àYX\›\ôY⁄YHÿ[ôY]U⁄Y¬àúôXZŒ¬àBàBàYà
YX\›\ôY⁄Yà⁄Y[Z]
H¬àô[ô\ôY^H	¯†)âŒ¬àYX\›\ôY⁄YH€€ù^õYX\›\ôU^
ô[ô\ôY^
Kù⁄Y¬àBàBàô]\õà»^àô[ô\ôY^⁄YàX]õZ[äYX\›\ôY⁄Y⁄Y[Z]
Kõ€ù⁄^ôHN¬àBÇàù[ò›[€àö[ò[ò⁄X[‹ò\X—]P⁄X⁄ ô\‹ù
H¬àYà
\ô\‹ùÀõYŸ\ê€€\]JHô]\õà	‘\ùX[	Œ¬àYà
ô\‹ùÀòYŸ‹ôYÿ]TôX€€ò⁄[Y
Hô]\õà	–⁄X⁄ŸY	Œ¬àYà
ô\‹ùÀõ›ô\ùöY]‘›]\»OOH	›ò\öX[òŸI Hô]\õà	‘ô]öY]…Œ¬àô]\õà	–€€\]HYŸ\âŒ¬àBÇàù[ò›[€àö[ò[ò⁄X[€ò\⁄›õ›‹ ô\‹ù€€\^]HH	›€€â H¬à€€ú›ô\‹ù€€\^]HHõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]J€€\^]JN¬àYà
ô\‹ù€€\^]HOOH	‹⁄[\I H¬àô]\õà¬à…”‹[ö[ô»ò[[òŸIÀô\‹ùõ‹[ö[ô–ò[[òŸHOOHù[»	’[ò]òZ[XõI»àõ‹õX]€€\X›‹ôY] ô\‹ùõ‹[ö[ô–ò[[òŸJWKà…–€‹⁄[ô»ò[[òŸIÀô\‹ùò€‹⁄[ô–ò[[òŸHOOHù[»	’[ò]òZ[XõI»àõ‹õX]€€\X›‹ôY] ô\‹ùò€‹⁄[ô–ò[[òŸJWKà…”Z\‹⁄[€àô]ÿ\ô…Àù[Xô\äô\‹ùõZ\‹⁄[€ê€›[ù
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â WKà…–]ô\òYŸHô]ÿ\ô	Àõ‹õX]€€\X›‹ôY] ô\‹ùò]ô\òYŸSZ\‹⁄[€îô]ÿ\ô
WKà…—[ùöY\»€›[ùY	Àù[Xô\äô\‹ùòX›]ö]P€›[ù
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â WKà…—]H⁄X⁄…Àö[ò[ò⁄X[‹ò\X—]P⁄X⁄ ô\‹ù
WBàN¬àBàYà
ô\‹ù€€\^]HOOH	⁄[ôõ‹õX]]ôI H¬àô]\õà¬à…–ôYõ‹ôH[ùô\›Y[ù	Àõ‹õX]⁄Y€ôY€€\X›‹ôY] ô\‹ùõ‹\ò][ô‘ô\›[
WKà…‘ù[õö[ô»€‹›…Àõ‹õX]⁄Y€ôY€€\X›‹ôY] SX]òXú ô\‹ùõ‹\ò][ô—^[úŸH
JWKà…“[ùô\›Y[ù	Àõ‹õX]⁄Y€ôY€€\X›‹ôY] SX]òXú ô\‹ùòÿ\][[ùô\›Y[ù
JWKà…”Z\‹⁄[€àô]ÿ\ô…Àù[Xô\äô\‹ùõZ\‹⁄[€ê€›[ù
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â WKà…–]ô\òYŸHô]ÿ\ô	Àõ‹õX]€€\X›‹ôY] ô\‹ùò]ô\òYŸSZ\‹⁄[€îô]ÿ\ô
WKà…“[ò€€YHú»ô]ö[›\…Àô\‹ùò€€\\ö\€€à»õ‹õX]\òŸ[ùYŸP⁄[ôŸJô\‹ùò€€\\ö\€€ãö[ò€€YP⁄[ôŸJHà	”õ›€€\\ôY	◊BàN¬àBà€€ú›ò]—Yôô\ô[òŸHHô\‹ùÀúôX€€ò⁄[X][€ëYôô\ô[òŸN¬à€€ú›\—Yôô\ô[òŸHHò]—Yôô\ô[òŸHOOHù[	âàò]—Yôô\ô[òŸHOOH[ôYö[ôY	âàù[Xô\ãö\—ö[ö]Jù[Xô\äò]—Yôô\ô[òŸJJN¬à]]Y]õ›Œ¬àYà
\—Yôô\ô[òŸJH¬à€€ú›Yôô\ô[òŸHHù[Xô\äò]—Yôô\ô[òŸJN¬à]Y]õ›»HX]òXú Yôô\ô[òŸJHHBà»…–⁄X⁄‹⁄[ù]Y]	À	‘ôX€€ò⁄[Y	◊Bàà…–⁄X⁄‹⁄[ùò\öX[òŸIÀõ‹õX]⁄Y€ôY€€\X›‹ôY] Yôô\ô[òŸJWN¬àH[ŸH¬à]Y]õ›»Hô\‹ùÀõ›ô\ùöY]‘õ›‹’\ŸYà»‹ô\‹ùõ›ô\ùöY]‘›]\»OOH	›ò\öX[òŸI»»	”›ô\ùöY]»ò\öX[òŸI»à	”›ô\ùöY]»]Y]	Àô\‹ùõ›ô\ùöY]‘›]\»OOH	›ò\öX[òŸI»»õ‹õX]⁄Y€ôY€€\X›‹ôY] ô\‹ùõ›ô\ùöY]”ô]ò\öX[òŸJHà	‘ôX€€ò⁄[Y	◊Bàà…–]Y]ò\⁄\…Àô\‹ùÀòò[[òŸPÿ[›[]Y»	‘ôX€€ú›ùX›Y	»à	’[ò]òZ[XõI◊N¬àBàô]\õà¬à…”‹\ò][ô»ô\›[	Àõ‹õX]⁄Y€ôY€€\X›‹ôY] ô\‹ùõ‹\ò][ô‘ô\›[
WKà…–ÿ\][\ﬁYY	Àõ‹õX]⁄Y€ôY€€\X›‹ôY] SX]òXú ô\‹ùòÿ\][[ùô\›Y[ù
JWKà…–X›]ôKZ›\à[ò€€YIÀõ‹õX]€€\X›‹ôY] ô\‹ùòX›]ôR[ò€€YT\í›\àô\‹ùö[ò€€YT\í›\äWKà…–€\‹⁄YöXÿ][€âÀ	”ù[Xô\äô\‹ùò€\‹⁄YöXÿ][€ê€€ôöY[òŸH
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–âÀ»X^[][QúòX›[€ëY⁄]ŒàHJ_IXKà…–€€ô][€àÿ€‹ôIÀ	”ù[Xô\äô\‹ùúÿ€‹ôXÿ\ôÀõ›ô\ò[
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–âÀ»X^[][QúòX›[€ëY⁄]ŒàJ_KÃLKà]Y]õ›¬àN¬àBÇàù[ò›[€àò]—ö[ò[ò⁄X[€ò\⁄›õ› €€ù^K⁄YXô[ò[YJH¬à€€ú›ÿ\HM¬à€€ú›ò[YSX^⁄YHX]õZ[äMãX]õX^
Mã⁄Y
àç
JN¬à€€ú›ò[YS^[›]Hö]ö[ò[ò⁄X[ÿ[ùò\’^
€€ù^ò[YKò[YSX^⁄Y»ŸZY⁄à⁄^ôNàMKZ[î⁄^ôNàLHJN¬à€€ú›ò[YTöY⁄H
»⁄Y¬à€€ú›ò[YSYùHò[YTöY⁄Hò[YS^[›]ù⁄Y¬à€€ú›Xô[X^⁄YHX]õX^
Mãò[YSYùHÿ\H
N¬à€€ú›Xô[^[›]Hö]ö[ò[ò⁄X[ÿ[ùò\’^
€€ù^Xô[Xô[X^⁄Y»ŸZY⁄àå⁄^ôNàMKZ[î⁄^ôNàLHJN¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKçN
IŒ¬à€€ù^ù^[Y€àH	€Yù	Œ¬à€€ù^ôõ€ùHå	€Xô[^[›]ôõ€ù⁄^ô_\\öX[ÿ[úÀ\Ÿ\öYò¬à€€ù^ôö[^
Xô[^[›]ù^JN¬à€€ù^ôö[›[HH	»ŸôôôôôâŒ¬à€€ù^ù^[Y€àH	‹öY⁄	Œ¬à€€ù^ôõ€ùH	›ò[YS^[›]ôõ€ù⁄^ô_\\öX[ÿ[úÀ\Ÿ\öYò¬à€€ù^ôö[^
ò[YS^[›]ù^ò[YTöY⁄JN¬à€€ù^ù^[Y€àH	€Yù	Œ¬àô]\õà¬àÿ\àXô[à»^àXô[^[›]ù^YùàöY⁄à
»Xô[^[›]ù⁄Y⁄YàXô[^[›]ù⁄Yõ€ù⁄^ôNàXô[^[›]ôõ€ù⁄^ôHKàò[YNà»^àò[YS^[›]ù^Yùàò[YSYùöY⁄àò[YTöY⁄⁄Yàò[YS^[›]ù⁄Yõ€ù⁄^ôNàò[YS^[›]ôõ€ù⁄^ôHBàN¬àBÇà\ﬁ[ò»ù[ò›[€àùZ[ö[ò[ò⁄X[⁄\ùõÿäô\‹ù
H¬àûH¬à€€ú›€€\^]HHõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]Jô\‹ùò€€\^]H›]Kô\ÿ€‹ôô\‹ùò€€\^]JN¬à€€ú›ÿ[ùò\»Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿÿ[ùò\… N¬àÿ[ùò\Àù⁄YHLå¬àÿ[ùò\ÀöZY⁄HçÕN¬à€€ú›€€ù^Hÿ[ùò\ÀôŸ]€€ù^
	Ãô	 N¬àYà
X€€ù^
Hô]\õàù[¬à€€ú›‹òYY[ùH€€ù^ò‹ôX]S[ôX\ë‹òYY[ù
LåçÕJN¬à‹òYY[ùòY€€‹î›‹
	»ÃåLN	 N¬à‹òYY[ùòY€€‹î›‹
çMK	»ÃLLXLç… N¬à‹òYY[ùòY€€‹î›‹
K	»ÃåLI N¬à€€ù^ôö[›[HH‹òYY[ù¬à€€ù^ôö[ôX›
LåçÕJN¬à€€ù^ôö[›[HH	‹ôÿòJMçãçMKåLäIŒ¬à€€ù^òôY⁄[î]

N¬à€€ù^ò\ò LåÃåÃX]îH
àäN¬à€€ù^ôö[

N¬à€€ù^ôö[›[HH	‹ôÿòJLçÕÀçMKå
IŒ¬à€€ù^òôY⁄[î]

N¬à€€ù^ò\ò MçLéX]îH
àäN¬à€€ù^ôö[

N¬à€€ù^ôö[›[HH	»ŸôôôôôâŒ¬à€€ù^ôõ€ùH	ŒLÕ\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ú›‹ò\X’]HH€€\^]HOOH	‹⁄[\I¬à»	”RT‘“S”ê“QQàíSêSê—HëT‘ï	¬àà€€\^]HOOH	⁄[ôõ‹õX]]ôI¬à»	”RT‘“S”ê“QQàíSêSê—HîíQQíSë…¬àà	”RT‘“S”ê“QQàíSêSê“PSSïSQ—Sê—IŒ¬à€€ù^ôö[^
‹ò\X’]KMN
N¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKçåäIŒ¬à€€ù^ôõ€ùH	ÕåN\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ú›€€\^]SXô[H€€\^]HOOH	›€€â»»	’H””â»à€€\^]Kù’\\êÿ\ŸJ
N¬à€€ù^ôö[^
	ÿ€€\^]SXô[H0≠»	‹ô\‹ùú\ö[ŸõXô[XMJN¬à€€ù^ôö[^
ô\‹ùú\ö[Ÿúò[ôŸSXô[MLMäN¬àõ›[ôôX›]
€€ù^LãŒMãÃå
N¬à€€ù^ôö[›[HHô\‹ùõô]à»	‹ôÿòJãåLLÀåN
I»àô\‹ùõô]»	‹ôÿòJåÃKÕãååN
I»à	‹ôÿòJçKNMãMKåN
IŒ¬à€€ù^ôö[

N¬à€€ù^ôö[›[HHô\‹ùõô]à»	»ÕçŸMéXâ»àô\‹ùõô]»	»ŸôéÕŒ	»à	»ŸçÕYIŒ¬à€€ù^ôõ€ùHL	ÿ€€\^]HOOH	›€€â»»Ãàåü\\öX[ÿ[úÀ\Ÿ\öYò¬à€€ù^ù^[Y€àH	ÿŸ[ù\âŒ¬à€€ú›ô\›[Xô[Hô\‹ùõô]à»	–RPQ	»àô\‹ùõô]»	–ëRSë	»à	—UëSâŒ¬à€€ù^ôö[^
€€\^]HOOH	›€€â»»ô\‹ùô‹òYKô‹òYHàô\›[Xô[LÃÀÃ N¬à€€ù^ôõ€ùH	ÕÃL‹\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ù^ôö[^
€€\^]HOOH	›€€â»»	‹ô\‹ùô‹òYKúÿ€‹ô_KÃLàõ‹õX]⁄Y€ôY€€\X›‹ôY] ô\‹ùõô]
KLÃÀMäN¬à€€ù^ù^[Y€àH	€Yù	Œ¬à€€ú›Y]öX’⁄YHçåN¬à€€ú›Y]öX—ÿ\HMN¬àò]—ö[ò[ò⁄X[Y]öX–ÿ\ô
€€ù^MMY]öX’⁄YN	”[€ô^H[âÀõ‹õX]⁄Y€ôY€€\X›‹ôY] ô\‹ùö[ò€€YJK	»ÃôXÿÕÃI N¬àò]—ö[ò[ò⁄X[Y]öX–ÿ\ô
€€ù^M
»
Y]öX’⁄Y
»Y]öX—ÿ\
KMY]öX’⁄YN	”[€ô^H›]	Àõ‹õX]⁄Y€ôY€€\X›‹ôY] SX]òXú ô\‹ùú‹[ô[ô»
JK	»ŸMÕÃÿ… N¬àò]—ö[ò[ò⁄X[Y]öX–ÿ\ô
€€ù^M
»à
à
Y]öX’⁄Y
»Y]öX—ÿ\
KMY]öX’⁄YN	”ô]⁄[ôŸIÀõ‹õX]⁄Y€ôY€€\X›‹ôY] ô\‹ùõô]
Kô\‹ùõô]èH»	»ÕNMôôâ»à	»ŸôçòçåI N¬àò]—ö[ò[ò⁄X[Y]öX–ÿ\ô
€€ù^M
»»
à
Y]öX’⁄Y
»Y]öX—ÿ\
KMY]öX’⁄YN	–€‹⁄[ô»ò[[òŸIÀô\‹ùò€‹⁄[ô–ò[[òŸHOOHù[»	’[ò]òZ[XõI»àõ‹õX]€€\X›‹ôY] ô\‹ùò€‹⁄[ô–ò[[òŸJK	»ŸåXÕâ N¬à€€ú›⁄\ùHM¬à€€ú›⁄\ùHHé¬à€€ú›⁄\ù»HÃÃ¬à€€ú›⁄\ùHçL¬àõ›[ôôX›]
€€ù^⁄\ù⁄\ùK⁄\ùÀ⁄\ùN
N¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKå
IŒ¬à€€ù^ôö[

N¬à€€ù^ôö[›[HH	»ŸôôôôôâŒ¬à€€ù^ôõ€ùH	ŒN\\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ù^ôö[^
	”ëUêSSê—HS’ëSQSï	À⁄\ù
»åã⁄\ùH
»ÃäN¬à€€ú›ùX⁄Ÿ]»Hô\‹ùòùX⁄Ÿ]Àú€XŸJLLäN¬à€€ú›X^XY€ö]YHHX]õX^
KããòùX⁄Ÿ]ÀõX\
ùX⁄Ÿ]OàX]òXú ùX⁄Ÿ]õô]
JJN¬à€€ú››‹H⁄\ùH
»N¬à€€ú››õ›€HH⁄\ùH
»⁄\ùHŒ¬à€€ú›ô\õ÷HH›‹
»
›õ›€HH›‹
H»é¬à€€ù^ú›õ⁄ŸT›[HH	‹ôÿòJçMKçMKçMKåM
IŒ¬à€€ù^õ[ôU⁄YHN¬à€€ù^òôY⁄[î]

N¬à€€ù^õ[›ôU ⁄\ù
»åãô\õ÷JN¬à€€ù^õ[ôU ⁄\ù
»⁄\ù»Håãô\õ÷JN¬à€€ù^ú›õ⁄ŸJ
N¬à€€ú›€›»H
⁄\ù»HLäH»X]õX^
KùX⁄Ÿ]Àõ[ô›
N¬àùX⁄Ÿ]Àôõ‹ëXX⁄

ùX⁄Ÿ][ô^
HOà¬à€€ú›ZY⁄HX]õX^
ãX]òXú ùX⁄Ÿ]õô]
H»X^XY€ö]YH
à

›õ›€HH›‹
H»àH
JN¬à€€ú›H⁄\ù
»éH
»[ô^
à€›Œ¬à€€ú›HHùX⁄Ÿ]õô]èH»ô\õ÷HHZY⁄àô\õ÷N¬àõ›[ôôX›]
€€ù^KX]õX^
€›»HL
KZY⁄
N¬à€€ù^ôö[›[HHùX⁄Ÿ]õô]èH»	»ÃôXÿÕÃI»à	»ŸMÕÃÿ…Œ¬à€€ù^ôö[

N¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKçLäIŒ¬à€€ù^ôõ€ùH	ÕåL\\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ù^ù^[Y€àH	ÿŸ[ù\âŒ¬à€€ù^ôö[^
ùX⁄Ÿ]õXô[
»X]õX^
€›»HL
H»ã⁄\ùH
»⁄\ùHMJN¬àJN¬à€€ù^ù^[Y€àH	€Yù	Œ¬à€€ú›]Z[HL¬à€€ú›]Z[HHé¬à€€ú›]Z[»HÃÕ¬à€€ú›]Z[HçL¬àõ›[ôôX›]
€€ù^]Z[]Z[K]Z[À]Z[N
N¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKå
IŒ¬à€€ù^ôö[

N¬à€€ù^ôö[›[HH	»ŸôôôôôâŒ¬à€€ù^ôõ€ùH	ŒN\\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ù^ôö[^
€€\^]HOOH	‹⁄[\I»»	–UH”Sê—I»à€€\^]HOOH	⁄[ôõ‹õX]]ôI»»	’T—QïS””ïV	»à	”‘TêUSë»”êT“’	À]Z[
»åã]Z[H
»ÃäN¬à€€ú›[ô\»Hö[ò[ò⁄X[€ò\⁄›õ›‹ ô\‹ù€€\^]JN¬à[ô\Àôõ‹ëXX⁄

[ôK[ô^
HOà¬à€€ú›HH]Z[H
»çH
»[ô^
àéN¬àò]—ö[ò[ò⁄X[€ò\⁄›õ› €€ù^]Z[
»åãK]Z[»H[ôVÃK[ôVÃWJN¬àJN¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKçäIŒ¬à€€ù^ôõ€ùH	ÕåM\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ù^ôö[^
	‹ô\‹ùòX›]ö]P€›[ùù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Hò[úÿX›[€ú»0≠»	‹ô\‹ùõYŸ\îYŸ\Àù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _HYŸ\àYŸ\»0≠»	‹ô\‹ùõ›ô\ùöY]‘õ›‹’\ŸY»	‹ô\‹ùõ›ô\ùöY]‘õ›‹’\ŸYù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _H›ô\ùöY]»^I‹ô\‹ùõ›ô\ùöY]‘õ›‹’\ŸYOOHH»	…»à	‹…ﬂXà	€›ô\ùöY]»[ò]òZ[XõIﬂH0≠»Ÿ[ô\ò]Y	€ô]»]Jô\‹ùôŸ[ô\ò]Y]
Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _XMåå
N¬à€€ù^ôö[›[HH	‹ôÿòJçMKçMKçMKåç IŒ¬à€€ù^ôõ€ùH	ÕåLú\öX[ÿ[úÀ\Ÿ\öYâŒ¬à€€ù^ôö[^
	‘–‘íTõò[Y_Hâ‘–‘íTùô\ú⁄[€üH0≠»	ÿ€€\^]HOOH	›€€â»»	’H€€àö[ò[ò⁄X[[ù[YŸ[òŸI»à	ÿ€€\^]SXô[Hö[ò[òŸHô\‹ùH0≠»Ÿ[ô\ò]Yÿÿ[XMç
N¬àô]\õà]ÿZ]ô]»õ€Z\ŸJô\€€ôHOà¬àÿ[ùò\Àù–õÿäô\€€ôK	⁄[XYŸK‹ô…ÀéLäN¬àJN¬àHÿ]⁄
\úäH¬àô]\õàù[¬àBàBÇàù[ò›[€à\ÿ€‹ôô]ûQ[^S\ ô\‹€úŸK][\H
H¬à€€ú›XY\ï^H›ö[ô ô\‹€úŸOÀúô\‹€úŸRXY\ú»	… N¬à€€ú›ô]ûRXY\àHXY\ï^õX]⁄
◊úô]ûKXYù\éó ä◊óJ K⁄[]JN¬àYà
ô]ûRXY\äH¬à€€ú›ò[YHHù[Xô\äô]ûRXY\ñÃWJN¬àYà
ù[Xô\ãö\—ö[ö]Jò[YJJHô]\õàX]õX^
çLò[YHàL»ò[YHàò[YH
àL
N¬àBàûH¬à€€ú›õŸHHî””ãú\úŸJô\‹€úŸOÀúô\‹€úŸU^	ﬁﬂI N¬à€€ú›ô]ûPYù\àHù[Xô\äõŸOÀúô]ûWÿYù\äN¬àYà
ù[Xô\ãö\—ö[ö]Jô]ûPYù\äJHô]\õàX]õX^
çLô]ûPYù\ààL»ô]ûPYù\ààô]ûPYù\à
àL
N¬àHÿ]⁄
\úäHﬂBàô]\õàX]õZ[äLÕL
àX]ú› ã][\
JN¬àBÇà\ﬁ[ò»ù[ò›[€àŸ[ô\ÿ€‹ô⁄]ô]ûJòX›‹ûKX^[][P][\»H H¬à]ô\‹€úŸHHù[¬àõ‹à
]][\H»][\X^[][P][\Œ»][\
  H¬àô\‹€úŸHH]ÿZ]òX›‹ûJ
N¬àYà
ô\‹€úŸKú›]\»OOHéH	âàô\‹€úŸKú›]\»L
Hô]\õàô\‹€úŸN¬àYà
][\èHX^[][P][\»HJHô]\õàô\‹€úŸN¬à€€ú›[^S\»H\ÿ€‹ôô]ûQ[^S\ ô\‹€úŸK][\
N¬àŸ]\ÿ€‹ô›]\ \ÿ€‹ô[]ô\ûH[^YYûHò]H[Z]Ààô]ûZ[ô»[à	”X]òŸZ[
[^S\»»L
_\¯†)ò	ÿù\ﬁI N¬àYà
X]ÿZ]ù[ù[YQ[^J[^S\ JHõ›»ô]»\úõ‹ä	’€€⁄]ù[ù[YH›‹Y\ö[ô»\ÿ€‹ôô]ûKâ N¬àBàô]\õàô\‹€úŸN¬àBÇà\ﬁ[ò»ù[ò›[€àŸ[ô\ÿ€‹ôö[ò[ò⁄X[^[ÿY
ŸXö€⁄’\õô\‹ù
H¬à€€ú›\–⁄\ùHõ€€X[äô\‹ùò⁄\ùõÿà	âà›]Kô\ÿ€‹ôô\‹ùö[ò€YP⁄\ù
N¬à€€ú›^[ÿYHùZ[\ÿ€‹ôö[ò[ò⁄X[^[ÿY
ô\‹ù»⁄]]X⁄Y[ùà\–⁄\ùJN¬à]ô\‹€úŸN¬àYà
\–⁄\ù
H¬àô\‹€úŸHH]ÿZ]Ÿ[ô\ÿ€‹ô⁄]ô]ûJ

HOà¬à€€ú›õ‹õQ]HHô]»õ‹õQ]J
N¬àõ‹õQ]Kò\[ô
	‹^[ÿY⁄ú€€âÀî””ãú›ö[ô⁄YûJ^[ÿY
JN¬àõ‹õQ]Kò\[ô
	Ÿö[\÷ÃIÀô\‹ùò⁄\ùõÿãíSêSê—W–“Tï—íSSêSQJN¬àô]\õà\ÿ€‹ôô\]Y\›
¬àY]Ÿà	‘‘’	Àà\õà\ÿ€‹ôŸXö€⁄—[ô⁄[ù
ŸXö€⁄’\õ»ÿZ]àùYHJKà]Nàõ‹õQ]BàJN¬àJN¬àYà
ô\‹€úŸKú›]\»OOHô\‹€úŸKú›]\»OOHL»ô\‹€úŸKú›]\»OOHMJH¬à€€ú›\úõ‹ï^H›ö[ô ô\‹€úŸKúô\‹€úŸU^	… Kù”›Ÿ\êÿ\ŸJ
N¬à€€ú›]X⁄Y[ùô[]YHô\‹€úŸKú›]\»OOHL»ô\‹€úŸKú›]\»OOHMHÿ]X⁄Y[ùö[_\ÿY][\\ùô\]Y\›[ù]H€»\ôŸK⁄]Kù\›
\úõ‹ï^
N¬àYà
]X⁄Y[ùô[]Y
H¬à€€ú›ò[òX⁄‘^[ÿYHùZ[\ÿ€‹ôö[ò[ò⁄X[^[ÿY
ô\‹ù»⁄]]X⁄Y[ùàò[ŸHJN¬àô\‹€úŸHH]ÿZ]Ÿ[ô\ÿ€‹ô⁄]ô]ûJ

HOà\ÿ€‹ôô\]Y\›
¬àY]Ÿà	‘‘’	Àà\õà\ÿ€‹ôŸXö€⁄—[ô⁄[ù
ŸXö€⁄’\õ»ÿZ]àùYHJKàXY\úŒà»	–€€ù[ùU\IŒà	ÿ\Xÿ][€ã⁄ú€€â»Kà]Nàî””ãú›ö[ô⁄YûJò[òX⁄‘^[ÿY
BàJJN¬àBàBàH[ŸH¬àô\‹€úŸHH]ÿZ]Ÿ[ô\ÿ€‹ô⁄]ô]ûJ

HOà\ÿ€‹ôô\]Y\›
¬àY]Ÿà	‘‘’	Àà\õà\ÿ€‹ôŸXö€⁄—[ô⁄[ù
ŸXö€⁄’\õ»ÿZ]àùYHJKàXY\úŒà»	–€€ù[ùU\IŒà	ÿ\Xÿ][€ã⁄ú€€â»Kà]Nàî””ãú›ö[ô⁄YûJ^[ÿY
BàJJN¬àBàYà
ô\‹€úŸKú›]\»åô\‹€úŸKú›]\»èHÃ
Hõ›»ô]»\úõ‹ä\úŸQ\ÿ€‹ô\úõ‹äô\‹€úŸJJN¬àô]\õàô\‹€úŸN¬àBÇàù[ò›[€àùZ[ò[ú‹‹ù›ŸY\\ÿ€‹ô^[ÿY
ô\‹ù
H¬à€€ú››]€€YHHò[ú‹‹ù›ŸY\›]€€YSY]Jô\‹ùõ›]€€YJN¬à€€ú›€€\][€ï[ö^HX]ôõ€‹äô\‹ùò€€\]Y]»L
N¬à€€ú›]HHô\‹ùõ›]€€YHOOH	€X[ùX[K\›‹Y	¬à»	¸'Ê§H]Y[ùò[ú‹‹ù›ŸY\›‹Y	¬àà	¸'Ê§H]Y[ùò[ú‹‹ù›ŸY\€€\]IŒ¬àô]\õà¬à\Ÿ\õò[YNà	”Z\‹⁄[€ê⁄YYàX\€€[X[ô€€⁄]	Àà[›ŸY€Y[ù[€úŒà»\úŸNà◊HKà[XôYŒàﬁ¬à]Kà\ÿ‹ö\[€éà
äâ‹ô\‹ùò€X\ôYH]Y[ù	‹ô\‹ùò€X\ôYOOHH»	…»à	‹…ﬂH€X\ôY
äàX‹õ‹‹»	‹ô\‹ùô[Y⁄XõSZ\‹⁄[€úﬂH[Y⁄XõHZ\‹⁄[€â‹ô\‹ùô[Y⁄XõSZ\‹⁄[€ú»OOHH»	…»à	‹…ﬂKòà€€‹éà›]€€YKò€€›\ãàöY[Œà¬à»ò[YNà	—ö[ò[›]\…Àò[YNà›]€€YKõXô[[õ[ôNàùYHKà»ò[YNà	‘›XÿŸ\‹»ò]IÀò[YNà	‹ô\‹ùú›XÿŸ\‹‘ò]_IX[õ[ôNàùYHKà»ò[YNà	—\ò][€âÀò[YNàõ‹õX]ò[ú‹‹ù›ŸY\\ò][€äô\‹ùô\ò][€ì\ K[õ[ôNàùYHKà»ò[YNà	”Z\‹⁄[€ú»⁄X⁄ŸY	Àò[YNà›ö[ô ô\‹ùõZ\‹⁄[€ú–⁄X⁄ŸY
K[õ[ôNàùYHKà»ò[YNà	—[Y⁄XõHZ\‹⁄[€ú…Àò[YNà›ö[ô ô\‹ùô[Y⁄XõSZ\‹⁄[€ú K[õ[ôNàùYHKà»ò[YNà	”Z\‹⁄[€ú»€€\]Y	Àò[YNà›ö[ô ô\‹ùõZ\‹⁄[€ú–€€\]Y
K[õ[ôNàùYHKà»ò[YNà	‘]Y[ù»€X\ôY	Àò[YNà›ö[ô ô\‹ùò€X\ôY
K[õ[ôNàùYHKà»ò[YNà	‘⁄⁄\Y	Àò[YNà›ö[ô ô\‹ùú⁄⁄\Y
K[õ[ôNàùYHKà»ò[YNà	—\úõ‹ú…Àò[YNà›ö[ô ô\‹ùô\úõ‹ú K[õ[ôNàùYHKà»ò[YNà	‘õÿŸ\‹ŸY	Àò[YNà›ö[ô ô\‹ùúõÿŸ\‹ŸY
K[õ[ôNàùYHKà»ò[YNà	–€€\]Y	Àò[YNàâÿ€€\][€ï[ö^Nëèò[õ[ôNàò[ŸHBàKàõ€›\éà»^àX\€€[X[ô€€⁄]â‹ô\‹ùù€€⁄]ô\ú⁄[€üH0≠»YŸ‹ôYÿ]K[€õH›ŸY\ô\‹ùKà[Y\›[\àô]»]Jô\‹ùò€€\]Y]
Kù“T”‘›ö[ô 
BàWBàN¬àBÇà\ﬁ[ò»ù[ò›[€à‹›ò[ú‹‹ù›ŸY\\ÿ€‹ôô\‹ù
ô\‹ùHò[ú‹‹ù›ŸY\ù[ù[YKõ\›ô\‹ù»X[ùX[Hò[ŸHHHﬂJH¬à€€ú›€X[àHõ‹õX[\ŸUò[ú‹‹ù›ŸY\ô\‹ù
ô\‹ù
N¬à€€ú››\úô[ùHò[ú‹‹ù›ŸY\ù[ù[YKõ\›ô\‹ù¬àYà
X€X[àX›\úô[ù›\úô[ùú›ŸY\YOOH€X[ãú›ŸY\Y
Hô]\õàò[ŸN¬àYà
›\úô[ùô\ÿ€‹ôú›]\»OOH	‹Ÿ[ù	 H¬àYà
X[ùX[
H⁄›’ÿ\›
	’\»›ŸY\ô\‹ù\»[ôXYH€à\ÿ€‹ô	 N¬àô]\õàùYN¬àBàYà
ò[ú‹‹ù›ŸY\ù[ù[YKô\ÿ€‹ô‹›[ô Hô]\õàò[ŸN¬à€€ú›ŸXö€⁄’\õHŸ]\ÿ€‹ôŸXö€⁄’\õ

N¬àYà
]ŸXö€⁄’\õ
H¬à\]Uò[ú‹‹ù›ŸY\ô\‹ù\ÿ€‹ô
€X[ãú›ŸY\Y¬à›]\Œà	€õ›X€€ôöY›\ôY	ÀàY\‹ÿYŸNà	‘ÿ]ôHH\ÿ€‹ôŸXö€⁄»[àö[ò[òŸK[à⁄€‹ŸHŸ[ô»\ÿ€‹ôâÀàŸ[ù]ààJN¬àYà
X[ùX[
H⁄›’ÿ\›
	‘ÿ]ôHH\ÿ€‹ôŸXö€⁄»[àö[ò[òŸHö\ú›	 N¬àô]\õàò[ŸN¬àBàò[ú‹‹ù›ŸY\ù[ù[YKô\ÿ€‹ô‹›[ô»HùYN¬à\]Uò[ú‹‹ù›ŸY\ô\‹ù\ÿ€‹ô
€X[ãú›ŸY\Y¬à›]\Œà	‹Ÿ[ô[ô…ÀàY\‹ÿYŸNà	‘‹›[ô»YŸ‹ôYÿ]H›ŸY\›]\›X‹¯†)âÀàŸ[ù]ààJN¬àûH¬à€€ú›^[ÿYHùZ[ò[ú‹‹ù›ŸY\\ÿ€‹ô^[ÿY
€X[äN¬à€€ú›ô\‹€úŸHH]ÿZ]Ÿ[ô\ÿ€‹ô⁄]ô]ûJ

HOà\ÿ€‹ôô\]Y\›
¬àY]Ÿà	‘‘’	Àà\õà\ÿ€‹ôŸXö€⁄—[ô⁄[ù
ŸXö€⁄’\õ»ÿZ]àùYHJKàXY\úŒà»	–€€ù[ùU\IŒà	ÿ\Xÿ][€ã⁄ú€€â»Kà]Nàî””ãú›ö[ô⁄YûJ^[ÿY
BàJJN¬àYà
ô\‹€úŸKú›]\»åô\‹€úŸKú›]\»èHÃ
Hõ›»ô]»\úõ‹ä\úŸQ\ÿ€‹ô\úõ‹äô\‹€úŸJJN¬à\]Uò[ú‹‹ù›ŸY\ô\‹ù\ÿ€‹ô
€X[ãú›ŸY\Y¬à›]\Œà	‹Ÿ[ù	ÀàY\‹ÿYŸNà	—\ÿ€‹ô€€ôö\õYYôXŸZ\ŸàHYŸ‹ôYÿ]H›ŸY\ô\‹ùâÀàŸ[ù]à]Kõõ› 
BàJN¬à⁄›’ÿ\›
	‘]Y[ùò[ú‹‹ù›ŸY\ô\‹ùŸ[ù»\ÿ€‹ô	 N¬àô]\õàùYN¬àHÿ]⁄
\úäH¬à\]Uò[ú‹‹ù›ŸY\ô\‹ù\ÿ€‹ô
€X[ãú›ŸY\Y¬à›]\Œà	ŸòZ[Y	ÀàY\‹ÿYŸNà›ö[ô \úèÀõY\‹ÿYŸH	—\ÿ€‹ô[]ô\ûHòZ[Yâ Kú€XŸJN
KàŸ[ù]ààJN¬à⁄›’ÿ\›
	‘›ŸY\€€\]H0≠»\ÿ€‹ô[]ô\ûHòZ[Y	 N¬àô]\õàò[ŸN¬àHö[ò[H¬àò[ú‹‹ù›ŸY\ù[ù[YKô\ÿ€‹ô‹›[ô»Hò[ŸN¬àô[ô\ïò[ú‹‹ù›ŸY\[ô[

N¬àBàBÇàù[ò›[€à‹\ò][€ò[⁄]ô\Z\‹⁄[€ì[ö X›[€äH¬à€€ú›‹öY⁄[àH›ö[ô YŸU⁄[ô›Àõÿÿ][€èÀõ‹öY⁄[à	⁄ŒãÀ›››ÀõZ\‹⁄[€ò⁄YYãò€ÀùZ… Kúô\XŸJ◊ …›K	… N¬àô]\õà	€‹öY⁄[üK€Z\‹⁄[€úÀ…Ÿ[ò€ŸUTíP€€\€ô[ù
X›[€ãõZ\‹⁄[€íY
_X¬àBÇàù[ò›[€à‹\ò][€ò[⁄]ô\X›[€ú—öY[
€ò\⁄›
H¬àYà
\€ò\⁄›ù‹X›[€úÀõ[ô›
Hô]\õà	”õ»X›]ôHZ\‹⁄[€à›\úô[ùHÿ\úöY\»[à[[YYX]Hô\‹›\ôH⁄Y€ò[âŒ¬àô]\õàù[òÿ]Q\ÿ€‹ô
€ò\⁄›ù‹X›[€úÀõX\

X›[€ã[ô^
HOà¬à€€ú›ôX\€€ú»HX›[€ãúôX\€€úÀõ[ô›»X›[€ãúôX\€€úÀöõ⁄[ä	»0≠»	 Hà	”[€ö]‹âŒ¬àô]\õà	⁄[ô^
»_Kà
äñ…Ÿ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äX›[€ãòÿ\[€ä_WJ	€‹\ò][€ò[⁄]ô\Z\‹⁄[€ì[ö X›[€ä_JJäà8†%	Ÿ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äôX\€€ú _X¬àJKöõ⁄[ä	◊â KL
N¬àBÇàù[ò›[€à‹\ò][€ò[⁄]ô\ÿ\X⁄]QöY[
€ò\⁄›
H¬à€€ú›õ›‹»H€ò\⁄›úô\€›\òŸTô\‹›\ôKô‹õ›\Àú€XŸJ
N¬àYà
\õ›‹Àõ[ô›
Hô]\õà	”õ»›\úô[ùZ\‹⁄[ôÀ]ôZX€Hô\]Z\ô[Y[ù»\ôH^‹ŸYâŒ¬àô]\õàù[òÿ]Q\ÿ€‹ô
õ›‹ÀõX\
õ›»Oà¬à€€ú››]\»Hõ›Àú⁄‹ùò[àà»
äâ‹õ›Àú⁄‹ùò[H⁄‹ù
äòààõ›Àù[ùô\öYöYYàà»
äâ‹õ›Àù[ùô\öYöYYHÿÿ][€ã][ùô\öYöYY
äòààõ›Àúô\Ÿ\ùôHHBà»
äâ”X]õX^
õ›Àúô\Ÿ\ùôJ_Hô\Ÿ\ùôJäòàà	‹õ›Àúô\Ÿ\ùô_Hô\Ÿ\ùôX¬à€€ú›]öY[òŸHHõ›Àò€€ôö\õYY]òZ[XõHOOHõ›Àò]òZ[XõBà»	‹õ›Àò]òZ[Xõ_HôX€Ÿ€ö\ŸYàà	‹õ›Àò]òZ[Xõ_HôX€Ÿ€ö\ŸY0≠»	‹õ›Àò€€ôö\õYY]òZ[Xõ_H€€ôö\õYY[àòY]\…‹õ›Àù[õÿÿ]Y»0≠»	‹õ›Àù[õÿÿ]YH[õÿÿ]Yà	…ﬂI‹õ›Àõ›]⁄YTòY]\»»0≠»	‹õ›Àõ›]⁄YTòY]\ﬂH›]⁄YHòY]\ÿà	…ﬂX¬àô]\õà8†(à
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äõ›Àõò[YJ_Jäà8†%	‹õ›Àò\‹⁄Y€ôYK…‹õ›Àô[X[ôH€€ôö\õYY0≠»	Ÿ]öY[òŸ_H0≠»	‹›]\ﬂI‹õ›Àò€€ôõX›»	»0≠»õY]€€ôõX›	»à	…ﬂX¬àJKöõ⁄[ä	◊â KL
N¬àBÇàù[ò›[€àùZ[‹\ò][€ò[⁄]ô\^[ÿY
€ò\⁄›
H¬à€€ú›€€›\àH€ò\⁄›úŸ]ô\ö]HOOH	ÿ‹ö]Xÿ[	»»MÕÃÿ¬àà€ò\⁄›úŸ]ô\ö]HOOH	‹ô\‹›\ôY	»»åXÕÇàà€ò\⁄›úŸ]ô\ö]HOOH	‹›XõI»»ôXÿÕÃBààÕNé¬à€€ú››]\”[ô\»H¬àX›]ôHZ\‹⁄[€úŒà
äâ‹€ò\⁄›õZ\‹⁄[€úÀù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _JäòàX›õ›Œà
äâ‹€ò\⁄›òX›õ›Àõ[ô›ù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòàô\€›\òŸH€›Œà
äâ‹€ò\⁄›úô\€›\òŸTô\‹›\ôKò\‹⁄Y€ôYK…‹€ò\⁄›úô\€›\òŸTô\‹›\ôKúô\]Z\ôYH€€ôö\õYY[àòY]\ äòà€€ôö\õYY⁄‹ùò[à
äâ‹€ò\⁄›úô\€›\òŸTô\‹›\ôKú⁄‹ùò[ù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòàÿÿ][€ã][ùô\öYöYY€›Œà
äâ‹€ò\⁄›úô\€›\òŸTô\‹›\ôKù[ùô\öYöYYÿÿ][€ãù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà]òZ[XõHõY][àÿ€‹Nà
äâ‹€ò\⁄›úô\€›\òŸTô\‹›\ôKò]òZ[XõUôZX€\Àù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _JäòàN¬à€€ú›ò[ú‹‹ùò[YHH€ò\⁄›ùò[ú‹‹ùõZ\‹⁄[€ú¬à»¬à›]›[ô[ô»ò[ú‹‹ùZ\‹⁄[€úŒà
äâ‹€ò\⁄›ùò[ú‹‹ùõZ\‹⁄[€úÀù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà[‹H]ÿZ][ô»ò[ú‹‹ùà
äâ‹€ò\⁄›ùò[ú‹‹ùú[‹Kù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà€ò\⁄›ùò[ú‹‹ùú]Y[ù»»]Y[ùŒà
äâ‹€ò\⁄›ùò[ú‹‹ùú]Y[ùÀù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà	…Àà€ò\⁄›ùò[ú‹‹ùúö\€€ô\ú»»ö\€€ô\úŒà
äâ‹€ò\⁄›ùò[ú‹‹ùúö\€€ô\úÀù”ÿÿ[T›ö[ô 	Ÿ[ãQ–â _Jäòà	…¬àKôö[\äõ€€X[äKöõ⁄[ä	◊â Bàà	”õ»]Y[ù‹àö\€€ô\àò[ú‹‹ù[X[ô\»›\úô[ùH^‹ŸYâŒ¬à€€ú›€€ôõX›»H€ò\⁄›ôõY]€€ôõX›Àõ[ô›à»ù[òÿ]Q\ÿ€‹ô
€ò\⁄›ôõY]€€ôõX›Àú€XŸJäKõX\
õ›»Oà8†(à
äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€äõ›Àõò[YJ_Jäà8†%	‹õ›Àô[X[ôHô\]Z\ôYX‹õ‹‹»	‹õ›ÀõZ\‹⁄[€ê€›[ùHZ\‹⁄[€úŒ»	‹õ›Àò]òZ[Xõ_H]òZ[XõX
Köõ⁄[ä	◊â KL
Bàà	”õ»€€ôö\õYY‹õ‹‹À[Z\‹⁄[€à‹X⁄X[\›õY]€€ôõX›âŒ¬à€€ú›[XôYH¬à]Nà‹\ò][€ò[“UëT0≠»	€‹\ò][€ò[ô\‹›\ôTŸ]ô\ö]SXô[
€ò\⁄›úŸ]ô\ö]J_Xà\ÿ‹ö\[€éàù[òÿ]Q\ÿ€‹ô

äâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€ä€ò\⁄›ú›[[X\ûJ_JäóâŸ\ÿÿ\Q\ÿ€‹ôX\öŸ›€ä€ò\⁄›úÿ€‹J_H0≠»	‹€ò\⁄›úòY]\”Z_[ZHô\€›\òŸHòY]\ÿMäKà€€‹éà€€›\ãàöY[Œà¬à»ò[YNà	–€€[X[ôX›\ôIÀò[YNàù[òÿ]Q\ÿ€‹ô
›]\”[ô\Àöõ⁄[ä	◊â KL
K[õ[ôNàùYHKà»ò[YNà	’ò[ú‹‹ùô\‹›\ôIÀò[YNàù[òÿ]Q\ÿ€‹ô
ò[ú‹‹ùò[YKL
K[õ[ôNàùYHKà»ò[YNà	‘ô\€›\òŸHô\‹›\ôIÀò[YNà‹\ò][€ò[⁄]ô\ÿ\X⁄]QöY[
€ò\⁄›
K[õ[ôNàò[ŸHKà»ò[YNà	—õY]€€ôõX›…Àò[YNà€€ôõX›À[õ[ôNàò[ŸHKà»ò[YNà	’‹X›[€ú…Àò[YNà‹\ò][€ò[⁄]ô\X›[€ú—öY[
€ò\⁄›
K[õ[ôNàò[ŸHKà¬àò[YNà	—]öY[òŸHÿ€‹IÀàò[YNàù[òÿ]Q\ÿ€‹ô
	‹€ò\⁄›ò€€\]H»	–€€\]H›\úô[ù€ò\⁄›	»à	‘\ùX[›\úô[ù€ò\⁄›	ﬂH0≠»Z\‹⁄[€à]H	‹€ò\⁄›õZ\‹⁄[€îôXYH»	‹ôXYI»à	€ÿY[ô…ﬂH0≠»õY]]H	‹€ò\⁄›ùôZX€TôXYH»	‹ôXYI»à	€ÿY[ô…ﬂI‹€ò\⁄›õÿÿ][€ë]öY[òŸSZ\‹⁄[ô»»	»0≠»€€YHÿÿ][€à]öY[òŸH[ò]òZ[XõI»à	…ﬂWîôXY[€õHúöYYö[ôŒ»õ»[ö]»Ÿ\ôHŸ[X›Y‹à\‹]⁄YòL
Kà[õ[ôNàò[ŸBàBàKàõ€›\éà»^à	‘–‘íTõò[Y_Hâ‘–‘íTùô\ú⁄[€üH0≠»€ò\⁄›	‹€ò\⁄›öYXKà[Y\›[\àô]»]J€ò\⁄›ôŸ[ô\ò]Y]
Kù“T”‘›ö[ô 
BàN¬àô]\õà¬à\Ÿ\õò[YNà	”Z\‹⁄[€ê⁄YYà‹\ò][€ú…Àà[›ŸY€Y[ù[€úŒà»\úŸNà◊HKà[XôYŒàö]\ÿ€‹ô[XôY’–ùYŸ]
Ÿ[XôYJBàN¬àBÇà\ﬁ[ò»ù[ò›[€à‹›‹\ò][€ò[⁄]ô\

H¬àYà
‹\ò][€ò[⁄]ô\ù\ﬁJHô]\õé¬à]ŸXö€⁄’\õH	…Œ¬àûH¬àŸXö€⁄’\õHôXY\ÿ€‹ôŸXö€⁄“[ú]
»ÿ]ôNàùYHJN¬àYà
]ŸXö€⁄’\õ
Hõ›»ô]»\úõ‹ä	‘ÿ]ôHH\ÿ€‹ôŸXö€⁄»[àö[ò[òŸHôYõ‹ôH‹›[ô»H“UëTâ N¬àHÿ]⁄
\úäH¬àŸ]‹\ò][€ò[⁄]ô\›]\ \úèÀõY\‹ÿYŸH	–Hò[Y\ÿ€‹ôŸXö€⁄»\»ô\]Z\ôYâÀ	ÿòY	 N¬à⁄›’ÿ\›
	—\ÿ€‹ôŸXö€⁄»ô\]Z\ôYõ‹à“UëT	 N¬à›]KòX›]ôUXàH	Ÿö[ò[òŸIŒ¬àÿ]ôT›]J
N¬à‹[î[ô[

N¬à\]URJ
N¬àô]\õé¬àBà‹\ò][€ò[⁄]ô\ù\ﬁHHùYN¬àŸ]‹\ò][€ò[⁄]ô\›]\ 	‘ôYúô\⁄[ô»[ô‹›[ô»H‹\ò][€ò[“UëT8†)âÀ	ÿù\ﬁI N¬àô[ô\ì‹\ò][€ò[ô\‹›\ôPõÿ\ô

N¬àûH¬à€€ú›€ò\⁄›H]ÿZ]ôYúô\⁄‹\ò][€ò[ô\‹›\ôPõÿ\ô
ùYJN¬àYà
\€ò\⁄›
Hõ›»ô]»\úõ‹ä	–H›\úô[ù‹\ò][€ò[€ò\⁄›€›[õ›ôHô\öYöYY€»H“UëTÿ\»õ›‹›Yâ N¬à€€ú›^[ÿYHùZ[‹\ò][€ò[⁄]ô\^[ÿY
€ò\⁄›
N¬à€€ú›ô\‹€úŸHH]ÿZ]Ÿ[ô\ÿ€‹ô⁄]ô]ûJ

HOà\ÿ€‹ôô\]Y\›
¬àY]Ÿà	‘‘’	Àà\õà\ÿ€‹ôŸXö€⁄—[ô⁄[ù
ŸXö€⁄’\õ»ÿZ]àùYHJKàXY\úŒà»	–€€ù[ùU\IŒà	ÿ\Xÿ][€ã⁄ú€€â»Kà]Nàî””ãú›ö[ô⁄YûJ^[ÿY
BàJJN¬àYà
ô\‹€úŸKú›]\»åô\‹€úŸKú›]\»èHÃ
Hõ›»ô]»\úõ‹ä\úŸQ\ÿ€‹ô\úõ‹äô\‹€úŸJJN¬àŸ]‹\ò][€ò[⁄]ô\›]\ ‹\ò][€ò[“UëT‹›Y]	Ÿõ‹õX]ôYúô\⁄€ÿ⁄’[YJ]Kõõ› 
J_Kò	Ÿ€€Ÿ	 N¬à⁄›’ÿ\›
	”‹\ò][€ò[“UëT‹›Y	 N¬àHÿ]⁄
\úäH¬àŸ]‹\ò][€ò[⁄]ô\›]\ \úèÀõY\‹ÿYŸH	’H‹\ò][€ò[“UëT€›[õ›ôH‹›YâÀ	ÿòY	 N¬à⁄›’ÿ\›
	”‹\ò][€ò[“UëTòZ[Y	 N¬àHö[ò[H¬à‹\ò][€ò[⁄]ô\ù\ﬁHHò[ŸN¬àô[ô\ì‹\ò][€ò[ô\‹›\ôPõÿ\ô

N¬àBàBÇàù[ò›[€à€X\ë\ÿ€‹ôô]öY]–⁄\ù\õ

H¬àYà
\ÿ€‹ôö[ò[òŸP⁄\ù\õ
H¬àûH»Tìúô]õ⁄ŸSÿöôX›Tì
\ÿ€‹ôö[ò[òŸP⁄\ù\õ
N»Hÿ]⁄
\úäHﬂBàBà\ÿ€‹ôö[ò[òŸP⁄\ù\õH	…Œ¬àBÇàù[ò›[€à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
H¬à€X\ë\ÿ€‹ôô]öY]–⁄\ù\õ

N¬àBÇà\ﬁ[ò»ù[ò›[€à‹›\ÿ€‹ôö[ò[ò⁄X[ô\‹ù

H¬àYà
\ÿ€‹ôö[ò[òŸPù\ﬁJHô]\õé¬à]ŸXö€⁄’\õ¬àûH»ŸXö€⁄’\õHôXY\ÿ€‹ôŸXö€⁄“[ú]
»ÿ]ôNàùYHJN»Bàÿ]⁄
\úäH¬àŸ]\ÿ€‹ô›]\ \úèÀõY\‹ÿYŸH	—[ù\àHò[Y\ÿ€‹ôŸXö€⁄»TìâÀ	ÿòY	 N¬à⁄›’ÿ\›
	—\ÿ€‹ôŸXö€⁄»ô\]Z\ôY	 N¬àô]\õé¬àBà\ÿ€‹ôö[ò[òŸPù\ﬁHHùYN¬àŸ]\ÿ€‹ô›]\ 	–ùZ[[ô»[ô‹›[ô»Hö[ò[ò⁄X[ô\‹ù8†)âÀ	ÿù\ﬁI N¬àûH¬à€€ú›ô\‹ùH]ÿZ]ùZ[ö[ò[ò⁄X[ô\‹ù

N¬à]ÿZ]Ÿ[ô\ÿ€‹ôö[ò[ò⁄X[^[ÿY
ŸXö€⁄’\õô\‹ù
N¬à€TŸ]ò[YTÿYôJ–‘íTô\ÿ€‹ô\›ô\‹ù›]Kô\‹ùôŸ[ô\ò]Y]
N¬à€X\ë\ÿ€‹ôô]öY]–⁄\ù\õ

N¬àŸ]\ÿ€‹ô›]\ ‹›Y›XÿŸ\‹Ÿù[H]	€ô]»]J
Kù”ÿÿ[U[YT›ö[ô ◊K»›\éà	ÃãYY⁄]	ÀZ[ù]Nà	ÃãYY⁄]	»J_Kò	Ÿ€€Ÿ	 N¬à⁄›’ÿ\›
	—\ÿ€‹ôö[ò[ò⁄X[ô\‹ù‹›Y	 N¬àHÿ]⁄
\úäH¬àŸ]\ÿ€‹ô›]\ \úèÀõY\‹ÿYŸH	’H\ÿ€‹ôô\‹ù€›[õ›ôH‹›YâÀ	ÿòY	 N¬à⁄›’ÿ\›
	—\ÿ€‹ôô\‹ùòZ[Y	 N¬àHö[ò[H¬à\ÿ€‹ôö[ò[òŸPù\ﬁHHò[ŸN¬àBàBÇàù[ò›[€à€X\ë\ÿ€‹ôŸXö€⁄ 
H¬àYà
YŸ]\ÿ€‹ôŸXö€⁄’\õ

JH¬àŸ]\ÿ€‹ô›]\ 	”õ»\ÿ€‹ôŸXö€⁄»\»›\úô[ùHÿ]ôYâÀ	€ô]]ò[	 N¬àô]\õé¬àBàYà
\YŸU⁄[ô›Àò€€ôö\õJ	‘ô[[›ôHHÿ]ôY\ÿ€‹ôŸXö€⁄»úõ€H[\\õ[€öŸ^H›‹òYŸO… JHô]\õé¬à€Q[]Uò[YTÿYôJ–‘íTô\ÿ€‹ôŸXö€⁄‘›]JN¬à€€ú›[ú]Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHŸ]K\Ÿ][ôœHô\ÿ€‹ô]ŸXö€⁄»óX
N¬àYà
[ú]
H[ú]ùò[YHH	…Œ¬àŸ]\ÿ€‹ô›]\ 	‘ÿ]ôY\ÿ€‹ôŸXö€⁄»ô[[›ôYâÀ	Ÿ€€Ÿ	 N¬à⁄›’ÿ\›
	—\ÿ€‹ôŸXö€⁄»€X\ôY	 N¬àBÇÇàù[ò›[€àŸ]›]\ ^
H¬à€€ú››]\»Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHõX€\À\›]\ÿ
N¬àYà
›]\ H›]\Àù^€€ù[ùH^	‘ôXYKâŒ¬àBÇàù[ò›[€à⁄›’ÿ\›
^
H¬à]ÿ\›Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTùÿ\›Y
N¬àYà
]ÿ\›
H¬àÿ\›Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àÿ\›öYH–‘íTùÿ\›Y¬àÿ›[Y[ùòõŸKò\[ô⁄[
ÿ\›
N¬àBàÿ\›ù^€€ù[ùH^¬àÿ\›ò€\‹”\›òY
	€X€\ÀYõ\⁄	 N¬àù[ù[YP€X\ï[Y[›]
ÿ\›õ\⁄[Y\äN¬àÿ\›õ\⁄[Y\àHù[ù[YTŸ][Y[›]


HOà¬àÿ\›õ\⁄[Y\àHù[¬àÿ\›ò€\‹”\›úô[[›ôJ	€X€\ÀYõ\⁄	 N¬àKML
N¬àBÇàù[ò›[€à\U[YJ[YRŸ^K\ú⁄\›HùYJH¬à›]Kù[YHHõ‹õX[\ŸU[YJ[YRŸ^JN¬àYà
\ú⁄\›
Hÿ]ôT›]J
N¬à\Tõ€›]öXù]\ 
N¬à\]URJ
N¬à⁄›’ÿ\›
SQT÷‹›]Kù[YWKôù[
N¬àBÇàù[ò›[€àŸ]X›]ôUXäXäH¬àYà
P””SPSë‘—P’S”ó”‘ëTãö[ò€Y\ XäJHô]\õé¬àYà
XàOOH	Ÿö[ò[òŸI H€€⁄][ò[]X‹‘ôX€‹ôôX]\ôJ	Ÿö[ò[ò⁄X[[ù[YŸ[òŸI N¬à›]KòX›]ôUXàHXé¬àÿ]ôT›]J
N¬à\]URJ
N¬àYà
YòY‘›]JH‹⁄][€î[ô[›ô\õ^JùYJN¬àYà
XàOOH	€Z\‹⁄[€ú… HôYúô\⁄\ú€€ò[ôZX€Q]Jò[ŸJKôö[ò[J

HOàÿ⁄Y[S‹\ò][€ò[[ô[‘ô[ô\äùYJJN¬àBÇàù[ò›[€à\T‹⁄][€ä‹⁄][€ã\ú⁄\›HùYJH¬à€€ú›ô^‹⁄][€àH‘“US”î÷‹‹⁄][€óH»‹⁄][€àà	ÿõ	Œ¬à›]Kú‹⁄][€àHô^‹⁄][€é¬àX›]ôS^[›]ôYô\ô[òŸ\ 
Kú‹⁄][€àHô^‹⁄][€é¬àYà
\ú⁄\›
Hÿ]ôT›]J
N¬à\]URJ
N¬àö]€€ùõ€”X\

N¬àBÇàù[ò›[€àùYŸP€€ùõ€
JH¬à›]KõùYŸKûH€[\
›]KõùYŸKû
»Låååå
N¬à›]KõùYŸKûHH€[\
›]KõùYŸKûH
»KLåååå
N¬àÿ]ôT›]J
N¬à\]URJ
N¬àBÇàù[ò›[€àô\Ÿ]ùYŸJ
H¬à›]KõùYŸHH»àNàN¬àÿ]ôT›]J
N¬à\]URJ
N¬àBàÀ»\‹›YHÕLMHô\›‹ôYH][ò⁄\é»\‹›YHÕåŒô\›öX›»›€ô\ú⁄\»Hÿ[õ€öXÿ[X\YŸKÇàù[ò›[€à€€⁄]‹]ô[ÿ›[Y[ù
ÿ»Hÿ›[Y[ù
H¬àûH¬à€€ú›öY]»HÿœÀôYò][öY]Œ¬àô]\õà]öY]»öY]Àù‹OOHöY]Œ¬àHÿ]⁄
\úõ‹äH¬àô]\õàùYN¬àBàBàù[ò›[€à€€⁄]ÿ›[Y[ù]ò[YJÿ»Hÿ›[Y[ù
H¬à]]ò[YHH	…Œ¬àûH»]ò[YHHÿœÀôYò][öY]œÀõÿÿ][€èÀú]ò[YH	…Œ»Hÿ]⁄
\úõ‹äHﬂBàYà
\]ò[YJH¬àûH»]ò[YHHÿ»OOHÿ›[Y[ù»ÿÿ][€ãú]ò[YHà	…Œ»Hÿ]⁄
\úõ‹äHﬂBàBà€€ú›X€ŸYHX€ŸY]ò[YJ]ò[YJKúô\XŸJ◊ﬁÃãKŸ›K	À… Kúô\XŸJ◊ …Ÿ›K	… N¬àô]\õàX€ŸY	À…Œ¬àBàù[ò›[€à€€⁄]€€[X[ô⁄[õ›]Q[Y⁄XõJÿ»Hÿ›[Y[ù
H¬àô]\õà€€⁄]‹]ô[ÿ›[Y[ù
ÿ H	âà€€⁄]ÿ›[Y[ù]ò[YJÿ HOOH	À…Œ¬àBàù[ò›[€à€€⁄]ö[X\ûSX\[[Y[ù
X\[ÿ»Hÿ›[Y[ù
H¬àYà
]€€⁄]€€[X[ô⁄[õ›]Q[Y⁄XõJÿ JHô]\õàù[¬à€€ú›Z\‹⁄[€îŸ[X›‹àH	»€Z\‹⁄[€ãYõ‹õKõZ\‹⁄[€ã]⁄[ô›ÀõZ\‹⁄[€ó›⁄[ô›Àõ[Ÿ[õ[Ÿ[X€€ù[ùõY⁄õﬁŸ]K[Z\‹⁄[€ãZYIŒ¬à€€ú›X\›]\àHÿœÀú]Y\ûTŸ[X›‹èÀä	»€X\€›]\â Hù[¬à€€ú›ÿ[ôY]\»H¬àÿœÀú]Y\ûTŸ[X›‹èÀä	»€X\	 KàX\›]\èÀú]Y\ûTŸ[X›‹èÀä	ÀõXYõ]X€€ùZ[ô\ãŸ]K[XYõ][X\HõXZ[àóI KàX\[àããê\úò^Kôúõ€JÿœÀú]Y\ûTŸ[X›‹ê[Àä	÷Ÿ]K[XYõ][X\HõXZ[àóI H◊JBàN¬àõ‹à
€€ú›ÿ[ôY]HŸàÿ[ôY]\ H¬àYà
Xÿ[ôY]Hÿ[ôY]Kõ›€ô\ëÿ›[Y[ùOOHÿ»ÿ[ôY]Kö\–€€õôX›YOOHò[ŸJH€€ù[ùYN¬àYà
ÿ[ôY]Kò€‹Ÿ\›ÀäZ\‹⁄[€îŸ[X›‹äJH€€ù[ùYN¬à€€ú›[ú⁄YPÿ[õ€öXÿ[⁄[Hõ€€X[äX\›]\èÀò€€ùZ[úœÀäÿ[ôY]JJN¬à€€ú›^X⁄]XZ[ìX\Hÿ[ôY]KöYOOH	€X\	»	âàõ€€X[äà[ú⁄YPÿ[õ€öXÿ[⁄[àÿ[ôY]Kò€\‹”\›Àò€€ùZ[úœÀä	€XYõ]X€€ùZ[ô\â Bàÿ[ôY]KõX]⁄\œÀä	÷Ÿ]K[XYõ][X\HõXZ[àóI Bà
N¬à€€ú›X€\ôYXZ[ìX\Hÿ[ôY]KõX]⁄\œÀä	÷Ÿ]K[XYõ][X\HõXZ[àóI H	âà[ú⁄YPÿ[õ€öXÿ[⁄[¬à€€ú›ÿ[õ€öXÿ[XYõ]X\H[ú⁄YPÿ[õ€öXÿ[⁄[	âàÿ[ôY]Kò€\‹”\›Àò€€ùZ[úœÀä	€XYõ]X€€ùZ[ô\â N¬àYà
Y^X⁄]XZ[ìX\	âàYX€\ôYXZ[ìX\	âàXÿ[õ€öXÿ[XYõ]X\
H€€ù[ùYN¬àô]\õàÿ[ôY]N¬àBàô]\õàù[¬àBàù[ò›[€à€€⁄]€€ùõ€‹›
X\[ÿ»Hÿ›[Y[ù
H¬àô]\õà€€⁄]ö[X\ûSX\[[Y[ù
X\[ÿ N¬àBàù[ò›[€à€€⁄]€€[X[ô⁄[€€ù^X›]ôJÿ»Hÿ›[Y[ù
H¬àYà
]€€⁄]€€[X[ô⁄[õ›]Q[Y⁄XõJÿ JHô]\õàò[ŸN¬à€€ú›\ÿ€›ô\ôYX\Hÿ»OOHÿ›[Y[ù»Ÿ]\ôŸ\›XYõ]X\

Hàù[¬àô]\õàõ€€X[ä€€⁄]ö[X\ûSX\[[Y[ù
\ÿ€›ô\ôYX\ÿ JN¬àBàù[ò›[€àX\ô›€ï€€⁄]€€[X[ô⁄[
ôX\€€àH	⁄[ô[Y⁄XõH€€[X[ô\⁄[€€ù^	 H¬à\‹‹ŸUô\ú⁄[€î›]\ 
N¬à›‹X\YX\›\ôJò[ŸJN¬à€€ú›õŸRY»H¬à–‘íTò€€ùõ€Yà–‘íTú[ô[Yà–‘íTùÿ\›Yà–‘íTú^[›]õ\⁄Yà–‘íTùôZX€T›]\“Yà–‘íTúô\‹›\ôPõÿ\ôYà–‘íTõXZõ‹í[ò⁄Y[ùôYYYà–‘íTùò[ú‹‹ù›ŸY\YYà–‘íTö[Ÿ[ù\íYà–‘íTò€€[X[ô[]RYà–‘íTò€€[X[ô^\öY[òŸS[Ÿ[Yà–‘íTõX\YX\›\ôRYYà–‘íTò€€ù^Y[ùRYà–‘íTú]ZX⁄’⁄Y[Yà–‘íTôù[ÿ‹ôY[ë^]Yà–‘íTùôZX€Qõ€›“Yà–‘íTò€X[ë^]YàN¬à]ô[[›ôYH¬àõ‹à
€€ú›YŸàõŸRY H¬à€€ú›õŸHHÿ›[Y[ùú]Y\ûTŸ[X›‹èÀä⁄YHâ⁄YHóX
N¬àYà
[õŸJH€€ù[ùYN¬àù[ù[YU[õ\›[ï\ôŸ]
õŸKùYJN¬àõŸKúô[[›ôJ
N¬àô[[›ôY
œHN¬àBàù[ù[YTù[ôQ\ÿ€€õôX›Y\›[ô\ú 
N¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[Àä	ÀõX€\À[X\Yù[ÿ‹ôY[ã]\ôŸ]	 Kôõ‹ëXX⁄
[[Y[ùOà[[Y[ùò€\‹”\›úô[[›ôJ	€X€\À[X\Yù[ÿ‹ôY[ã]\ôŸ]	 JN¬àù[ÿ‹ôY[ìX\\ôŸ]Àò€\‹”\›Àúô[[›ôOÀä	€X€\À[X\Yù[ÿ‹ôY[ã]\ôŸ]	 N¬àù[ÿ‹ôY[ìX\\ôŸ]Hù[¬à]]“YQÿ⁄‘ô]ôX[YHò[ŸN¬àŸ][ô‹‘[ô[X›]ò]YHò[ŸN¬àòY‘›]HHù[¬à€€ù^€€[X[ô\ôŸ]Hù[¬à€€[X[ô[]Q[ùöY\»H◊N¬à€€[X[ô[]Tô\›[»H◊N¬à€€[X[ô[]TŸ[X›Y[ô^H¬à€€[X[ô[]Tô]\õëõÿ›\»Hù[¬à]ZX⁄’⁄Y[ô]\õëõÿ›\»Hù[¬à]ZX⁄’⁄Y[ô\›‹ôQòYŸ⁄[ô»Hò[ŸN¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùÀúô[[›ôP]öXù]OÀä	Ÿ]K[X€\ÀX€€[X[ô\[]K[‹[â N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùÀúô[[›ôP]öXù]OÀä	Ÿ]K[X€\ÀZ[[‹[â N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùÀú›[OÀúô[[›ôTõ‹\ùOÀä	ÿ›\ú€‹â N¬àÿ›[Y[ùòõŸOÀú›[OÀúô[[›ôTõ‹\ùOÀä	›\Ÿ\ã\Ÿ[X›	 N¬àô]\õà»ôX\€€ãô[[›ôYN¬àBàù[ò›[€à€€⁄]\P€€[X[ôò\î›]J€€ùõ€Hù[
H¬à€€ùõ€Hÿ›[Y[ùú]Y\ûTŸ[X›‹èÀä…‘–‘íTò€€ùõ€YX
Hù[¬àYà
X€€ùõ€
Hô]\õàò[ŸN¬à€€ú›‹[àH›]Kò€€[X[ôò\ì‹[àOOHò[ŸN¬à€€ú›]]“Y[ô»Hõ€€X[ä›]Kò]]“YQÿ⁄Àô[òXõY	âà\›]KúÿYôS[ŸKô[òXõY
N¬à€€ú›ö\›X[S‹[àH‹[à	âà
X]]“Y[ô»]]“YQÿ⁄‘ô]ôX[YZ\’›X⁄^[›]X›]ôJ
JN¬à€€ùõ€úŸ]]öXù]J	Ÿ]K[X€\ÀX€€[X[ôXò\ã[‹[âÀ›ö[ô ‹[äJN¬àõ‹à
€€ú›Ÿ[X›‹àŸà…ÀõX€\ÀYõÿ][ôÀYö[\âÀ	ÀõX€\À\ÿ‹ôY[ã\[ú…◊JH¬à€€ú›[[Y[ùH€€ùõ€ú]Y\ûTŸ[X›‹èÀäŸ[X›‹äN¬àYà
Y[[Y[ù
H€€ù[ùYN¬àYà
‹[äH[[Y[ùú›[Kúô[[›ôTõ‹\ùJ	Ÿ\‹^I N¬à[ŸH[[Y[ùú›[KúŸ]õ‹\ùJ	Ÿ\‹^IÀ	€õ€ôIÀ	⁄[\‹ù[ù	 N¬àBà€€ú›ù]€àH€€ùõ€ú]Y\ûTŸ[X›‹èÀä	ÀõX€\ÀYÿ⁄À]ŸŸ€KXùâ N¬àYà
ù]€äH¬à€€ú›Xô[H]]“Y[ô»	âà\’›X⁄^[›]X›]ôJ
H»
]]“YQÿ⁄‘ô]ôX[Y»	“YH]]ÀZY[ô»€€[X[ôò\â»à	‘ô]ôX[]]ÀZY[ô»€€[X[ôò\â Hà
‹[à»	–€€\ŸH€€[X[ôò\â»à	—^[ô€€[X[ôò\â N¬àù]€ãò€\‹”\›ùŸŸ€J	€X€\À[‹[âÀö\›X[S‹[äN¬àù]€ãúŸ]]öXù]J	ÿ\öXKY^[ôY	À›ö[ô ö\›X[S‹[äJN¬àù]€ãúŸ]]öXù]J	ÿ\öXK[Xô[	ÀXô[
N¬àù]€ãù]HHXô[¬à€€ú›X€€àHù]€ãú]Y\ûTŸ[X›‹èÀä	ÀõX€\ÀYÿ⁄À]ŸŸ€KZX€€â N¬àYà
X€€äHX€€ãù^€€ù[ùHö\›X[S‹[à»	¯•≠	»à	¯•ØâŒ¬àBàô]\õà‹[é¬àBÇàù[ò›[€àŸŸ€P€€[X[ôò\ä
H¬à€€ú›€€ùõ€Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬àYà
›]Kò]]“YQÿ⁄Àô[òXõY	âà\’›X⁄^[›]X›]ôJ
H	âà›]Kò€€[X[ôò\ì‹[àOOHò[ŸH	âà\›]KúÿYôS[ŸKô[òXõY
H¬à]]“YQÿ⁄‘ô]ôX[YHX]]“YQÿ⁄‘ô]ôX[Y¬à\Tõ€›]öXù]\ 
N¬à€€⁄]\P€€[X[ôò\î›]J€€ùõ€
N¬à⁄›’ÿ\›
]]“YQÿ⁄‘ô]ôX[Y»	–€€[X[ôò\àô]ôX[Y	»à	–€€[X[ôò\àX⁄ŸY]ÿ^I N¬àô]\õé¬àBà€€ú›‹[ö[ô»H›]Kò€€[X[ôò\ì‹[àOOHò[ŸN¬àù[ù[YP€X\ï[Y[›]
€€[X[ôò\ê[ö[X][€ï[Y\äN¬à€€[X[ôò\ê[ö[X][€ï[Y\àHù[¬à€€[X[ôò\ê[ö[X][ô»Hò[ŸN¬àõ‹à
€€ú›][HŸà\úò^Kôúõ€J€€ùõ€Àú]Y\ûTŸ[X›‹ê[Àä	ÀõX€\ÀYõÿ]XùãõX€\À\ÿ‹ôY[ã\[ãXùâ H◊JJH¬à][Kú›[Kúô[[›ôTõ‹\ùJ	€‹X⁄]I N¬à][Kú›[Kúô[[›ôTõ‹\ùJ	›ò[úŸõ‹õI N¬à][Kú›[Kúô[[›ôTõ‹\ùJ	›ò[ú⁄][€â N¬à][Kú›[Kúô[[›ôTõ‹\ùJ	›ò[ú⁄][€ãY[^I N¬à][Kú›[Kúô[[›ôTõ‹\ùJ	›⁄[X⁄[ôŸI N¬à[]H][Kô]\Ÿ]õX€\–€€\ŸQ[^N¬àBà›]Kò€€[X[ôò\ì‹[àH‹[ö[ôŒ¬àÿ]ôT›]J
N¬à\Tõ€›]öXù]\ 
N¬à€€⁄]\P€€[X[ôò\î›]J€€ùõ€
N¬à\]URJ
N¬àö]€€ùõ€”X\

N¬à⁄›’ÿ\›
‹[ö[ô»»	–€€[X[ôò\à^[ôY	»à	–€€[X[ôò\à€€\ŸY	 N¬àBÇàù[ò›[€à[ôSX\ö\⁄Xö[]UŸŸ€JôX]\ôJH¬àYà
ôX]\ôHOOH	€X\öŸ\ëõÿ›\… H›]KõX\öŸ\ëõÿ›\»H\›]KõX\öŸ\ëõÿ›\Œ¬à[ŸHYà
ôX]\ôHOOH	€Z\‹⁄[€î[ŸI H›]KõZ\‹⁄[€î[ŸHH\›]KõZ\‹⁄[€î[ŸN¬à[ŸHYà
ôX]\ôHOOH	‹õÿYö[‹ö]I H›]KúõÿYö[‹ö]HH\›]KúõÿYö[‹ö]N¬à[ŸHYà
ôX]\ôHOOH	ÿ€›ô\òYŸI H›]Kò€›ô\òYŸKô[òXõYH\›]Kò€›ô\òYŸKô[òXõY¬à[ŸHYà
ôX]\ôHOOH	ÿ[X[òŸSZ\‹⁄[€ú… H›]Kùö\⁄Xö[]Kò[X[òŸSZ\‹⁄[€ú»H\›]Kùö\⁄Xö[]Kò[X[òŸSZ\‹⁄[€úŒ¬à[ŸHYà
ôX]\ôHOOH	€^SZ\‹⁄[€ú… H›]Kùö\⁄Xö[]Kõ^SZ\‹⁄[€ú»H\›]Kùö\⁄Xö[]Kõ^SZ\‹⁄[€úŒ¬à[ŸHYà
ôX]\ôHOOH	›ôZX€\… H›]Kùö\⁄Xö[]KùôZX€\»H\›]Kùö\⁄Xö[]KùôZX€\Œ¬à[ŸHYà
ôX]\ôHOOH	ÿùZ[[ô‹… H›]Kùö\⁄Xö[]KòùZ[[ô‹»H\›]Kùö\⁄Xö[]KòùZ[[ô‹Œ¬à[ŸHô]\õàò[ŸN¬àô]\õàùYN¬àBàù[ò›[€à\SX\ö\⁄Xö[]UŸŸ€QYôôX› ôX]\ôJH»YäôX]\ôOOOI›ôZX€\… \ﬁ[ò⁄õ€ö\ŸUôZX€SX\öŸ\ê€\‹Ÿ\ 
N⁄YäôX]\ôOOOIÿùZ[[ô‹… \ﬁ[ò⁄õ€ö\ŸT\ú€€ò[ùZ[[ô’ö\⁄Xö[]J
N⁄Yä›]KôX€€õ€^S[ŸIâäôX]\ôOOOI›ôZX€\…ﬂôX]\ôOOOIÿùZ[[ô‹… J\ÿ⁄Y[QX€€õ€^S^Y\îﬁ[ò 
N⁄YäôX]\ôOOOI€Z\‹⁄[€êYŸI ^‹ù[ù[YP€X\ï[Y[›]
Z\‹⁄[€êYŸU[Y\äN€Z\‹⁄[€êYŸU[Y\è[ù[⁄Yä›]KõZ\‹⁄[€êYŸJ^⁄[õ[ôSZ\‹⁄[€ë]Tÿÿ[õôYYò[ŸN‹ÿÿ[í[õ[ôSZ\‹⁄[€ìX\öŸ\ë]JùYJN⁄[ùò[Y]SX\öŸ\îôY⁄\›ûPÿX⁄\ 	€Z\‹⁄[€â N‹ÿ⁄Y[SX\öŸ\î›]Tﬁ[ò ùYJN‹ÿ⁄Y[SZ\‹⁄[€êYŸTôYúô\⁄

N‹ù[ù[YTŸ][Y[›]


OOû⁄Yä›]KõZ\‹⁄[€êYŸJ\ÿ⁄Y[SZ\‹⁄[€êYŸTôYúô\⁄

NﬂKL
NﬂY[ŸH€X\ìZ\‹⁄[€êYŸSXô[ 
NﬂHBàù[ò›[€à[ôSZ\‹⁄[€ï⁄[ô›’ŸŸ€JôX]\ôJH¬àYà
ôX]\ôHOOH	€Z\‹⁄[€ïò[YI H›]KõZ\‹⁄[€ïò[YHH\›]KõZ\‹⁄[€ïò[YN¬à[ŸHYà
ôX]\ôHOOH	ÿ›\›€UôZX€PòYŸ\… H›]Kò›\›€UôZX€PòYŸ\»H\›]Kò›\›€UôZX€PòYŸ\Œ¬à[ŸHô]\õàò[ŸN¬àô]\õàùYN¬àBàù[ò›[€à\SZ\‹⁄[€ï⁄[ô›’ŸŸ€QYôôX› ôX]\ôJH¬àYà
ôX]\ôHOOH	€Z\‹⁄[€ïò[YI H»Yà
›]KõZ\‹⁄[€ïò[YJH[ú›[Z\‹⁄[€ïò[YU⁄[ô›‹ 
N»[ŸH€X\ìZ\‹⁄[€ïò[YR[ôXÿ]‹ú 
N»⁄›’ÿ\›
›]KõZ\‹⁄[€ïò[YH»	”Z\‹⁄[€àò[YH€â»à	”Z\‹⁄[€àò[YHŸôâ N»BàYà
ôX]\ôHOOH	ÿ›\›€UôZX€PòYŸ\… H»Yà
›]Kò›\›€UôZX€PòYŸ\ H[ú›[›\›€UôZX€PòYŸ\ 
N»[ŸH€X\ê›\›€UôZX€PòYŸ\ 
N»⁄›’ÿ\›
›]Kò›\›€UôZX€PòYŸ\»»	–›\›€HôZX€HòYŸ\»€â»à	–›\›€HôZX€HòYŸ\»Ÿôâ N»BàBàù[ò›[€à[ôT^[›]]Y[’ŸŸ€JôX]\ôJH¬àYà
ôX]\ôHOOH	€Z\‹⁄[€ìÿ⁄–]Y[… H»›]KõZ\‹⁄[€ìÿ⁄–]Y[»H\›]KõZ\‹⁄[€ìÿ⁄–]Y[Œ»Yà
›]KõZ\‹⁄[€ìÿ⁄–]Y[ H[õÿ⁄‘^[›]]Y[ ùYJN»Bà[ŸHYà
ôX]\ôHOOH	‹^[›]õ\⁄	 H›]Kú^[›]õ\⁄ô[òXõYH\›]Kú^[›]õ\⁄ô[òXõY¬à[ŸHYà
ôX]\ôHOOH	‹^[›]€›[ô	 H»›]Kú^[›]õ\⁄ú€›[ô[òXõYH\›]Kú^[›]õ\⁄ú€›[ô[òXõY»Yà
›]Kú^[›]õ\⁄ú€›[ô[òXõY
H[õÿ⁄‘^[›]]Y[ 
N»[ŸH\‹‹ŸT^[›]YYXP]Y[ 
N»Bà[ŸHô]\õàò[ŸN¬àô]\õàùYN»Bàù[ò›[€à\T^[›]]Y[’ŸŸ€QYôôX› ôX]\ôJH¬àYà
ôX]\ôHOOH	€Z\‹⁄[€ìÿ⁄–]Y[… H⁄›’ÿ\›
›]KõZ\‹⁄[€ìÿ⁄–]Y[»»	”Z\‹⁄[€àòX⁄⁄[ô»]Y[»€â»à	”Z\‹⁄[€àòX⁄⁄[ô»]Y[»Ÿôâ N¬à[ŸHYà
ôX]\ôHOOH	‹^[›]€›[ô	 H⁄›’ÿ\›
›]Kú^[›]õ\⁄ú€›[ô[òXõY»	’[YH]Y[»€à0≠»‹›YT»›Y\»ÿY€õH⁄[à^YY	»à	’[YH]Y[»Ÿôâ N¬à[ŸHYà
ôX]\ôHOOH	‹^[›]õ\⁄	 H⁄›’ÿ\›
›]Kú^[›]õ\⁄ô[òXõY»	—[Y\ôŸ[òﬁH^[›]õ\⁄€â»à	—[Y\ôŸ[òﬁH^[›]õ\⁄Ÿôâ N¬àBàù[ò›[€à[ôSZ\‹⁄[€ì[€ö]‹ö[ô’ŸŸ€JôX]\ôJH¬àYà
ôX]\ôHOOH	‹›X⁄—]X›‹â H›]Kú›X⁄—]X›‹ãô[òXõYH\›]Kú›X⁄—]X›‹ãô[òXõY¬à[ŸHYà
ôX]\ôHOOH	€Z\‹⁄[€î‹]€â H»›]KõZ\‹⁄[€î‹]€ãô[òXõYH\›]KõZ\‹⁄[€î‹]€ãô[òXõY»Z\‹⁄[€î‹]€ê\õYYHò[ŸN»ù[ù[YP€X\ï[Y[›]
Z\‹⁄[€î‹]€îö[YU[Y\äN»€õ›€ìZ\‹⁄[€íYÀò€X\ä
N»Yà
Z\‹⁄[€î‹]€ìYôXﬁX€SôYYY

JHö[YSZ\‹⁄[€î‹]€ë]X›‹ä
N»Bà[ŸHô]\õàò[ŸN¬àô]\õàùYN»Bàù[ò›[€à\SZ\‹⁄[€ì[€ö]‹ö[ô’ŸŸ€QYôôX› ôX]\ôJH¬àYà
ôX]\ôHOOH	‹›X⁄—]X›‹â H⁄›’ÿ\›
›]Kú›X⁄—]X›‹ãô[òXõY»›X⁄»]X›‹à€à0≠»	‹›]Kú›X⁄—]X›‹ãùô\⁄€Z[üHZ[òà	‘›X⁄»]X›‹àŸôâ N¬à[ŸHYà
ôX]\ôHOOH	€Z\‹⁄[€î‹]€â H⁄›’ÿ\›
›]KõZ\‹⁄[€î‹]€ãô[òXõY»	”ô]»Z\‹⁄[€à[ö[X][€à€â»à	”ô]»Z\‹⁄[€à[ö[X][€àŸôâ N»Bàù[ò›[€à[ôR[ù\ôòXŸT⁄[ŸŸ€JôX]\ôJH¬àYà
ôX]\ôHOOH	ÿ€X[â H›]Kò€X[ì[ŸHH\›]Kò€X[ì[ŸN»[ŸHYà
ôX]\ôHOOH	‹⁄‹ù›]… H›]Kú⁄‹ù›]»H\›]Kú⁄‹ù›]Œ»[ŸHYà
ôX]\ôHOOH	ÿ€€\X›ÿ⁄… H›]Kò€€\X›ÿ⁄»H\›]Kò€€\X›ÿ⁄Œ»[ŸHYà
ôX]\ôHOOH	‹]ZX⁄’⁄Y[	 H›]Kú]ZX⁄’⁄Y[ô[òXõYH\›]Kú]ZX⁄’⁄Y[ô[òXõY»[ŸHô]\õàò[ŸN»ô]\õàùYN»Bàù[ò›[€àŸŸ€QôX]\ôJôX]\ôJH¬à[ôSX\ö\⁄Xö[]UŸŸ€JôX]\ôJN¬à[ôSZ\‹⁄[€ï⁄[ô›’ŸŸ€JôX]\ôJN¬à[ôT^[›]]Y[’ŸŸ€JôX]\ôJN¬à[ôSZ\‹⁄[€ì[€ö]‹ö[ô’ŸŸ€JôX]\ôJN¬à[ôR[ù\ôòXŸT⁄[ŸŸ€JôX]\ôJN¬àYà
ôX]\ôHOOH	ÿ]]”ÿY[ôZX€\… H¬à›]Kò]]”ÿY[ôZX€\»H\›]Kò]]”ÿY[ôZX€\Œ¬àYà
›]Kò]]”ÿY[ôZX€\ H[ú›[]]”ÿY[ôZX€\ 
N¬à[ŸH›‹]]”ÿY[ôZX€\ 
N¬àBàYà
ôX]\ôHOOH	ÿ[X[òŸPùZ[[ô‹”X\õÿ⁄Ÿ\â H›]Kò[X[òŸPùZ[[ô‹”X\H›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸN¬àYà
ôX]\ôHOOH	€XZõ‹í[ò⁄Y[ùôYY	 H›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõYH\›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY¬àYà
ôX]\ôHOOH	ÿ[X[òŸP‹ôY]… H›]Kò[X[òŸP‹ôY]»H\›]Kò[X[òŸP‹ôY]Œ¬àYà
ôX]\ôHOOH	€Z\‹⁄[€êYŸI H›]KõZ\‹⁄[€êYŸHH\›]KõZ\‹⁄[€êYŸN¬àYà
ôX]\ôHOOH	›[ö]€€[Z]Y[ù	 H›]Kù[ö]€€[Z]Y[ùH\›]Kù[ö]€€[Z]Y[ù¬àYà
ôX]\ôHOOH	›ò[ú‹‹ùÿ]⁄\â H›]Kùò[ú‹‹ùÿ]⁄\àH\›]Kùò[ú‹‹ùÿ]⁄\é¬àYà
ôX]\ôHOOH	‹ô\€›\òŸQÿ\	 H›]Kúô\€›\òŸQÿ\ô[òXõYH\›]Kúô\€›\òŸQÿ\ô[òXõY¬àYà
›]Kò€X[ì[ŸJH€‹ŸT[ô[

N¬àÿ]ôT›]J
N¬à\Tõ€›]öXù]\ 
N¬à\]URJ
N¬à\SX\ö\⁄Xö[]UŸŸ€QYôôX› ôX]\ôJN¬àôX€€ò⁄[QôX]\ôTôYúô\⁄\ »[ò€YT€ò\⁄›ŒàZ\‹⁄[€î€ò\⁄›”ôYYY

K‹⁄][€î[ô[àò[ŸHJN¬à\SZ\‹⁄[€ï⁄[ô›’ŸŸ€QYôôX› ôX]\ôJN¬à\T^[›]]Y[’ŸŸ€QYôôX› ôX]\ôJN¬à\SZ\‹⁄[€ì[€ö]‹ö[ô’ŸŸ€QYôôX› ôX]\ôJN¬àYà
ôX]\ôHOOH	ÿ]]”ÿY[ôZX€\… H⁄›’ÿ\›
›]Kò]]”ÿY[ôZX€\»»	–]]À[ÿY[ôZX€\»€â»à	–]]À[ÿY[ôZX€\»Ÿôâ N¬àYà
ôX]\ôHOOH	ÿ[X[òŸP‹ôY]… H⁄›’ÿ\›
›]Kò[X[òŸP‹ôY]»»	–[X[òŸH‹ôY]»€â»à	–[X[òŸH‹ôY]»Ÿôâ N¬àYà
ôX]\ôHOOH	€Z\‹⁄[€êYŸI H⁄›’ÿ\›
›]KõZ\‹⁄[€êYŸH»	‘\ú€€ò[Z\‹⁄[€àYŸH€â»à	‘\ú€€ò[Z\‹⁄[€àYŸHŸôâ N¬àYà
ôX]\ôHOOH	›[ö]€€[Z]Y[ù	 H¬àYà
›]Kù[ö]€€[Z]Y[ù
H¬à⁄›’ÿ\›
	”ÿY[ô»[ö]\‹⁄Y€õY[ù¯†)â N¬àôYúô\⁄\ú€€ò[ôZX€Q]JùYJKù[ä⁄»Oà¬àÿ⁄Y[U[ö]€€[Z]Y[ùôYúô\⁄

N¬à⁄›’ÿ\›
⁄»»	’[ö]€›[ù€â»à	’[ö]€›[ù€à0≠»]ôHôZX€H]H[ò]òZ[XõI N¬àJN¬àH[ŸH⁄›’ÿ\›
	’[ö]€›[ùŸôâ N¬àBàYà
ôX]\ôHOOH	›ò[ú‹‹ùÿ]⁄\â H⁄›’ÿ\›
›]Kùò[ú‹‹ùÿ]⁄\à»	’ò[ú‹‹ùÿ]⁄\à€â»à	’ò[ú‹‹ùÿ]⁄\àŸôâ N¬àYà
ôX]\ôHOOH	€XZõ‹í[ò⁄Y[ùôYY	 H¬àYà
›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY
H¬àôYúô\⁄Z\‹⁄[€î€ò\⁄› 
N¬àÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\ä
N¬àH[ŸHô[[›ôSXZõ‹í[ò⁄Y[ùôYY

N¬à⁄›’ÿ\›
›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY»	”XZõ‹à[ò⁄Y[ùôYY€â»à	”XZõ‹à[ò⁄Y[ùôYYŸôâ N¬àBàYà
ôX]\ôHOOH	ÿ[X[òŸPùZ[[ô‹”X\õÿ⁄Ÿ\â H¬àYà
›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸJH¬à[ú›[[X[òŸPùZ[[ô‹—X\õT›[J
N¬à[ú›[[X[òŸPùZ[[ô‹”XYõ]\‹⁄Y€õY[ù›X\ô

N¬à[ú›[[X[òŸPùZ[[ô‹–€€ù^ÿ]⁄\ëX\õJ
N¬àH[ŸH¬à€X\ê[X[òŸPùZ[[ô‹—X\õP€€ù^

N¬àBà⁄›’ÿ\›
›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸH»	–[X[òŸHX\õÿ⁄Ÿ\à”à0≠»ô[ÿY[ô…»à	–[X[òŸHX\õÿ⁄Ÿ\à—ëà0≠»ô[ÿY[ô… N¬àYà
\–[X[òŸPùZ[[ô‹–€€ù^

JHù[ù[YTŸ][Y[›]


HOàÿÿ][€ãúô[ÿY

KN
N¬àBàYà
ôX]\ôHOOH	‹ô\€›\òŸQÿ\	 H¬à⁄›’ÿ\›
›]Kúô\€›\òŸQÿ\ô[òXõY»ô\€›\òŸHÿ\€à0≠»	‹›]Kúô\€›\òŸQÿ\úòY]\”Z_[ZXà	‘ô\€›\òŸHÿ\Ÿôâ N¬àBàYà
ôX]\ôHOOH	‹]ZX⁄’⁄Y[	 H¬àYà
\›]Kú]ZX⁄’⁄Y[ô[òXõY
H€‹ŸUXõ]]ZX⁄’⁄Y[

N¬à⁄›’ÿ\›
›]Kú]ZX⁄’⁄Y[ô[òXõY»	’Xõ]]ZX⁄»⁄Y[€â»à	’Xõ]]ZX⁄»⁄Y[Ÿôâ N¬àBà€€⁄][ò[]X‹‘ôX€‹ôôX]\ôJôX]\ôK	ŸôX]\ôW›ŸŸ€I N¬àBàù[ò›[€à\úŸU[YJò[YKò[òX⁄ H¬à€€ú›X]⁄H›ö[ô ò[YH	… KõX]⁄
◊äÃKüJNäÃüJI N¬àYà
[X]⁄
Hô]\õàò[òX⁄Œ¬àô]\õà€[\
X]⁄ÃWKåÀX]ôõ€‹äò[òX⁄»»å
JH
àå
»€[\
X]⁄ÃóKNKò[òX⁄»	Hå
N¬àBàù[ò›[€à⁄›[›\ô\‹–€€ùõ€

H¬àYà
›]Kò€X[ì[ŸJHô]\õàò[ŸN¬àYà
ÿ›[Y[ùòõŸH	âàÿ›[Y[ùòõŸKò€\‹”\›ò€€ùZ[ú 	€[Ÿ[[‹[â JHô]\õàùYN¬àô]\õà’TëT‘“S”ó‘—SP’‘îÀú€€YJŸ[X›‹àOà¬à]õŸ\Œ¬àûH»õŸ\»H\úò^Kôúõ€Jÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
Ÿ[X›‹äJN»Hÿ]⁄
\úäH»ô]\õàò[ŸN»Bàô]\õàõŸ\Àú€€YJ[Oà¬àYà
Y[[ò€‹Ÿ\›
…‘–‘íTò€€ùõ€YX
H[ò€‹Ÿ\›
…‘–‘íTú[ô[YX
JHô]\õàò[ŸN¬àYà
Z\’ö\⁄XõJ[
JHô]\õàò[ŸN¬à€€ú›ôX›H[ôŸ]õ›[ô[ô–€Y[ùôX›

N¬àô]\õà
ôX›ù⁄Y
àôX›öZY⁄
HàLå¬àJN¬àJN¬àBàù[ò›[€àôYúô\⁄›\ô\‹⁄[€ä
H¬à€€ú›€€ùõ€Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬àYà
X€€ùõ€
Hô]\õé¬à€€ùõ€ò€\‹”\›ùŸŸ€J	€X€\ÀZY[ãXûK[Y[ùIÀ⁄›[›\ô\‹–€€ùõ€

JN¬àBàù[ò›[€àö]€€ùõ€”X\

H¬àù[ù[YP€X\ï[Y[›]
ö][Y\äN¬àö][Y\àHù[ù[YTŸ][Y[›]


HOà¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬à€€ú›X\[HŸ]\ôŸ\›XYõ]X\

N¬àYà
[X\[
H¬àYà
Z\’›X⁄^[›]X›]ôJ
JH¬à€X\ë\⁄›‹ÿ⁄‘⁄^ö[ô 
N¬àÿúŸ\ùôQ\⁄›‹[ô[€‹ö‹‹XŸJù[
N¬à\Q\⁄›‹[ô[⁄^ö[ô [ô[ù[
N¬àBàô]\õé¬àBàYà
[ÿö[S[ŸPX›]ôJH¬à€X\ë\⁄›‹ÿ⁄‘⁄^ö[ô 
N¬à€X\ë\⁄›‹[ô[⁄^ö[ô [ô[
N¬à\S[ÿö[Qÿ⁄”^[›]
X\[
N¬àH[ŸHYà
Xõ][ŸPX›]ôJH¬à€X\ë\⁄›‹ÿ⁄‘⁄^ö[ô 
N¬à€X\ë\⁄›‹[ô[⁄^ö[ô [ô[
N¬à\UXõ]ÿ⁄”^[›]
X\[
N¬àH[ŸH¬à€X\ïXõ]ÿ⁄‘⁄^ö[ô 
N¬à\Q\⁄›‹ÿ⁄”^[›]
X\[
N¬àÿúŸ\ùôQ\⁄›‹[ô[€‹ö‹‹XŸJX\[
N¬à\Q\⁄›‹[ô[⁄^ö[ô [ô[X\[
N¬àBàYà
\[ô[
Hô]\õé¬à€€ú›ôX›HX\[ôŸ]õ›[ô[ô–€Y[ùôX›

N¬à[ô[ò€\‹”\›ùŸŸ€J	€X€\À[X\\€X[	ÀôX›öZY⁄MåôX›ù⁄YçL
N¬àKå
N¬àBàù[ò›[€àŸ][ô[‹‹‘‹⁄][€äYù‹
H¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[
Hô]\õé¬àYà
[ÿö[S[ŸPX›]ôJH»\UXõ][ô[‹⁄][€ä
N»ô]\õé»BàYà
Xõ][ŸPX›]ôJH\UXõ][ô[‹⁄][€ä»⁄^ôS€õNàùYHJN¬à[ŸH€X\ïXõ][ô[⁄^ö[ô [ô[
N¬à[ô[ú›[KúŸ]õ‹\ùJ	‹‹⁄][€âÀ	Ÿö^Y	À	⁄[\‹ù[ù	 N¬à[ô[ú›[KúŸ]õ‹\ùJ	€Yù	À	”X]úõ›[ô
Yù
_\	⁄[\‹ù[ù	 N¬à[ô[ú›[KúŸ]õ‹\ùJ	›‹	À	”X]úõ›[ô
‹
_\	⁄[\‹ù[ù	 N¬à[ô[ú›[KúŸ]õ‹\ùJ	‹öY⁄	À	ÿ]]…À	⁄[\‹ù[ù	 N¬à[ô[ú›[KúŸ]õ‹\ùJ	ÿõ›€IÀ	ÿ]]…À	⁄[\‹ù[ù	 N¬à[ô[ú›[KúŸ]õ‹\ùJ	›ò[úŸõ‹õIÀ	€õ€ôIÀ	⁄[\‹ù[ù	 N¬àBàù[ò›[€à€[\[ô[‹⁄][€äYù‹
H¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[
Hô]\õà»YùàLã‹àLàN¬àYà
Xõ][ŸPX›]ôJH¬à\UXõ][ô[‹⁄][€ä»⁄^ôS€õNàùYHJN¬à€€ú›öY]‹‹ùHŸ]öY]‹‹ùY]öX‹ 
N¬à€€ú›X\ô⁄[àHöY]‹‹ùù⁄YÃ»ààL¬à€€ú›[ô[⁄YHX]õZ[ä[ô[õŸôúŸ]⁄YÃX]õX^
KöY]‹‹ùù⁄YH
X\ô⁄[à
àäJJN¬à€€ú›[ô[ZY⁄HX]õZ[ä[ô[õŸôúŸ]ZY⁄LX]õX^
KöY]‹‹ùöZY⁄H
X\ô⁄[à
àäJJN¬àô]\õà€[\Xõ][ô[⁄[ù
Yù‹[ô[⁄Y[ô[ZY⁄öY]‹‹ùX\ô⁄[äN¬àBà€€ú›X\[HŸ]\ôŸ\›XYõ]X\

N¬à€€ú›õ›[ô»H\Q\⁄›‹[ô[⁄^ö[ô [ô[X\[
Hô\€€ôQ\⁄›‹[ô[õ›[ô ù[
N¬à€€ú›[ô[⁄YHX]õZ[ä[ô[õŸôúŸ]⁄YÃNX]õX^
Kõ›[ôÀúöY⁄Hõ›[ôÀõYù
JN¬à€€ú›[ô[ZY⁄HX]õZ[ä[ô[õŸôúŸ]ZY⁄Lõ›[ôÀõX^ZY⁄
N¬àô]\õà€[\\⁄›‹[ô[⁄[ù
Yù‹[ô[⁄Y[ô[ZY⁄õ›[ô N¬àBàù[ò›[€àŸ]Yò][[ô[‹⁄][€ä
H¬à€€ú›€€ùõ€Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬à€€ú›X\ô⁄[àHLé¬àYà
X€€ùõ€\[ô[
Hô]\õà»YùàX\ô⁄[ã‹àX\ô⁄[àN¬à€€ú›€€ùõ€ôX›H€€ùõ€ôŸ]õ›[ô[ô–€Y[ùôX›

N¬à€€ú›[ô[⁄YH[ô[õŸôúŸ]⁄YÃN¬à€€ú›öY]‹‹ù⁄YHYŸU⁄[ô›Àö[õô\ï⁄Yÿ›[Y[ùôÿ›[Y[ù[[Y[ùò€Y[ù⁄Y¬à€€ú›‹XŸTöY⁄HöY]‹‹ù⁄YH€€ùõ€ôX›úöY⁄HX\ô⁄[é¬à€€ú›‹XŸSYùH€€ùõ€ôX›õYùHX\ô⁄[é¬àô]\õà¬àYùà
‹XŸTöY⁄èH[ô[⁄Y‹XŸTöY⁄èH‹XŸSYù
H»€€ùõ€ôX›úöY⁄
»X\ô⁄[àà€€ùõ€ôX›õYùH[ô[⁄YHX\ô⁄[ãà‹à€€ùõ€ôX›ù‹àN¬àBàù[ò›[€à‹⁄][€î[ô[›ô\õ^J\ŸTÿ]ôY‹⁄][€àHùYJH¬àYà
òY‘›]JHô]\õé¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[\[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â JHô]\õé¬à€€ú›ÿ]ôY‹⁄][€àHX›]ôS^[›]ôYô\ô[òŸ\ 
Kú[ô[‹⁄][€à›]Kú[ô[‹⁄][€é¬àYà
[ÿö[S[ŸPX›]ôJH»\UXõ][ô[‹⁄][€ä
N»ô]\õé»BàYà
Xõ][ŸPX›]ôJH¬à\UXõ][ô[‹⁄][€ä»⁄^ôS€õNàùYHJN¬àYà
J\ŸTÿ]ôY‹⁄][€à	âàÿ]ôY‹⁄][€à	âàù[Xô\ãö\—ö[ö]Jù[Xô\äÿ]ôY‹⁄][€ãõYù
JH	âàù[Xô\ãö\—ö[ö]Jù[Xô\äÿ]ôY‹⁄][€ãù‹
JJJH¬à\UXõ][ô[‹⁄][€ä
N¬àô]\õé¬àBàBàYà
]Xõ][ŸPX›]ôJH€X\ïXõ][ô[⁄^ö[ô [ô[
N¬à]Yù¬à]‹¬àYà
\ŸTÿ]ôY‹⁄][€à	âàÿ]ôY‹⁄][€à	âàù[Xô\ãö\—ö[ö]Jù[Xô\äÿ]ôY‹⁄][€ãõYù
JH	âàù[Xô\ãö\—ö[ö]Jù[Xô\äÿ]ôY‹⁄][€ãù‹
JJH¬àYùHù[Xô\äÿ]ôY‹⁄][€ãõYù
N¬à‹Hù[Xô\äÿ]ôY‹⁄][€ãù‹
N¬àH[ŸH¬à€€ú›‹»HŸ]Yò][[ô[‹⁄][€ä
N¬àYùH‹ÀõYù¬à‹H‹Àù‹¬àBà€€ú›€[\YH€[\[ô[‹⁄][€äYù‹
N¬àŸ][ô[‹‹‘‹⁄][€ä€[\YõYù€[\Yù‹
N¬àBÇàù[ò›[€àô\Ÿ][ô[‹⁄][€ä
H¬àYà
[ÿö[S[ŸPX›]ôJH»⁄›’ÿ\›
	”[ÿö[H[ŸH\Ÿ\»Hö^Yô\‹€ú⁄]ôH[ô[	 N»ô]\õé»BàX›]ôS^[›]ôYô\ô[òŸ\ 
Kú[ô[‹⁄][€àHù[¬à›]Kú[ô[‹⁄][€àHù[¬àÿ]ôT›]J
N¬àYà
Xõ][ŸPX›]ôJH\UXõ][ô[‹⁄][€ä
N¬à[ŸH‹⁄][€î[ô[›ô\õ^Jò[ŸJN¬à⁄›’ÿ\›
	”Y[ùH‹⁄][€àô\Ÿ]	 N¬àBÇàù[ò›[€àùYŸT[ô[
JH¬àYà
[ÿö[S[ŸPX›]ôJH»⁄›’ÿ\›
	”[ÿö[H[ŸH\Ÿ\»Hö^Yô\‹€ú⁄]ôH[ô[	 N»ô]\õé»Bà€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[
Hô]\õé¬à€€ú›ôX›H[ô[ôŸ]õ›[ô[ô–€Y[ùôX›

N¬à€€ú›‹»H€[\[ô[‹⁄][€äôX›õYù
»ôX›ù‹
»JN¬àŸ][ô[‹‹‘‹⁄][€ä‹ÀõYù‹Àù‹
N¬àX›]ôS^[›]ôYô\ô[òŸ\ 
Kú[ô[‹⁄][€àH»Yùà‹ÀõYù‹à‹Àù‹N¬à›]Kú[ô[‹⁄][€àH»Yùà‹ÀõYù‹à‹Àù‹N¬àÿ]ôT›]J
N¬à⁄›’ÿ\›
Y[ùH	‹‹ÀõYùK	‹‹Àù‹X
N¬àBÇàù[ò›[€à›\ù[ô[òY ]ô[ù
H¬àYà
[ÿö[S[ŸPX›]ôJHô]\õé¬à€€ú›\”[›\ŸHH]ô[ùù\HOOH	€[›\ŸY›€âŒ¬à€€ú›\’›X⁄H]ô[ùù\HOOH	››X⁄›\ù	Œ¬àYà
\”[›\ŸH	âà]ô[ùòù]€àOOH
Hô]\õé¬àYà
Z\”[›\ŸH	âàZ\’›X⁄
Hô]\õé¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[\[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â JHô]\õé¬à€€ú›⁄[ùH\’›X⁄»]ô[ùù›X⁄\÷ÃHà]ô[ù¬àYà
\⁄[ù
Hô]\õé¬à€€ú›ôX›H[ô[ôŸ]õ›[ô[ô–€Y[ùôX›

N¬àòY‘›]HH¬à›\ùà⁄[ùò€Y[ùà›\ùNà⁄[ùò€Y[ùKà›\ùYùàôX›õYùà›\ù‹àôX›ù‹à[›ôYàò[ŸBàN¬à[ô[ò€\‹”\›òY
	€X€\ÀYòYŸ⁄[ô… N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùú›[Kò›\ú€‹àH	Ÿ‹òXòö[ô…Œ¬àÿ›[Y[ùòõŸKú›[Kù\Ÿ\îŸ[X›H	€õ€ôIŒ¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	€[›\Ÿ[[›ôIÀ[›ôT[ô[òYÀùYJN¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	€[›\Ÿ]\	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	››X⁄[›ôIÀ[›ôT[ô[òYÀ»ÿ\\ôNàùYK\‹⁄]ôNàò[ŸHJN¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	››X⁄[ô	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	››X⁄ÿ[òŸ[	À[ô[ô[òYÀùYJN¬à]ô[ùúô]ô[ùYò][

N¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬àBÇàù[ò›[€à[›ôT[ô[òY ]ô[ù
H¬àYà
YòY‘›]JHô]\õé¬à€€ú›\’›X⁄H]ô[ùù\HOOH	››X⁄[›ôIŒ¬à€€ú›⁄[ùH\’›X⁄»]ô[ùù›X⁄\÷ÃHà]ô[ù¬àYà
\⁄[ù
Hô]\õé¬à€€ú›H⁄[ùò€Y[ùHòY‘›]Kú›\ù¬à€€ú›HH⁄[ùò€Y[ùHHòY‘›]Kú›\ùN¬àYà
X]òXú 
HààX]òXú JHàäHòY‘›]Kõ[›ôYHùYN¬à€€ú›‹»H€[\[ô[‹⁄][€äòY‘›]Kú›\ùYù
»òY‘›]Kú›\ù‹
»JN¬àŸ][ô[‹‹‘‹⁄][€ä‹ÀõYù‹Àù‹
N¬à]ô[ùúô]ô[ùYò][

N¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬àBÇàù[ò›[€à[ô[ô[òY ]ô[ù
H¬àYà
YòY‘›]JHô]\õé¬à€€ú›Y[›ôHHõ€€X[äòY‘›]Kõ[›ôY
N¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
[ô[
H¬à[ô[ò€\‹”\›úô[[›ôJ	€X€\ÀYòYŸ⁄[ô… N¬à€€ú›ôX›H[ô[ôŸ]õ›[ô[ô–€Y[ùôX›

N¬à€€ú›‹»H€[\[ô[‹⁄][€äôX›õYùôX›ù‹
N¬àŸ][ô[‹‹‘‹⁄][€ä‹ÀõYù‹Àù‹
N¬àX›]ôS^[›]ôYô\ô[òŸ\ 
Kú[ô[‹⁄][€àH»Yùà‹ÀõYù‹à‹Àù‹N¬à›]Kú[ô[‹⁄][€àH»Yùà‹ÀõYù‹à‹Àù‹N¬àÿ]ôT›]J
N¬àBàòY‘›]HHù[¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùú›[Kò›\ú€‹àH	…Œ¬àÿ›[Y[ùòõŸKú›[Kù\Ÿ\îŸ[X›H	…Œ¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	€[›\Ÿ[[›ôIÀ[›ôT[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	€[›\Ÿ]\	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	››X⁄[›ôIÀ[›ôT[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	››X⁄[ô	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	››X⁄ÿ[òŸ[	À[ô[ô[òYÀùYJN¬àYà
Y[›ôJH¬à›\ô\‹”ô^›]⁄YP€X⁄»HùYN¬à⁄›’ÿ\›
	”Y[ùH‹⁄][€àÿ]ôY	 N¬àù[ù[YTŸ][Y[›]


HOà»›\ô\‹”ô^›]⁄YP€X⁄»Hò[ŸN»KçL
N¬àBàYà
]ô[ù
H¬à]ô[ùúô]ô[ùYò][

N¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬àBàBÇàù[ò›[€à‹[î[ô[

H¬àYà
]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JH¬àX\ô›€ï€€⁄]€€[X[ô⁄[
	€Y[ùHô\]Y\››]⁄YHÿ[õ€öXÿ[X\€€ù^	 N¬àô]\õé¬àBà€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
H‹ôX]T[ô[

N¬àYà
\[ô[
Hô]\õé¬à\Tõ€›]öXù]\ 
N¬àôYúô\⁄Xõ][ŸUZJ[ô[
N¬à[ô[ò€\‹”\›òY
	€X€\À[‹[â N¬à[ô[úŸ]]öXù]J	ÿ\öXKZY[âÀ	Ÿò[ŸI N¬à€€ú›Y[ùPù]€àHÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTò€€ùõ€YHõX€\À[Y[ùKXùò
N¬àY[ùPù]€èÀúŸ]]öXù]J	ÿ\öXKY^[ôY	À	›ùYI N¬àö]€€ùõ€”X\

N¬àù[ù[YTŸ][Y[›]


HOà‹⁄][€î[ô[›ô\õ^JùYJK
N¬àBÇàù[ò›[€à€‹ŸT[ô[
»ô\›‹ôQõÿ›\»Hò[ŸHHHﬂJH¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[
Hô]\õé¬à[ô[ò€\‹”\›úô[[›ôJ	€X€\À[‹[â N¬à[ô[úŸ]]öXù]J	ÿ\öXKZY[âÀ	›ùYI N¬à€€ú›Y[ùPù]€àHÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTò€€ùõ€YHõX€\À[Y[ùKXùò
N¬àY[ùPù]€èÀúŸ]]öXù]J	ÿ\öXKY^[ôY	À	Ÿò[ŸI N¬àYà
ô\›‹ôQõÿ›\»	âàY[ùPù]€èÀö\–€€õôX›Y
Hù[ù[YTŸ][Y[›]


HOàY[ùPù]€ãôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJK
N¬àBÇàù[ò›[€àŸŸ€T[ô[

H¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[
H»‹[î[ô[

N»ô]\õé»Bà[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â H»€‹ŸT[ô[

Hà‹[î[ô[

N¬àBÇàù[ò›[€à€€[X[ô[]Sõ‹õX[\ŸJò[YJH¬àô]\õà›ö[ô ò[YH	… Bàõõ‹õX[^ôJ	”ëí—	 Bàúô\XŸJ÷◊LÃWLÕôóKŸ›K	… Bàù”›Ÿ\êÿ\ŸJ
Bàúô\XŸJ÷◊òK^åNWJÀŸ›K	»	 Bàúô\XŸJ◊ ÀŸ›K	»	 Bàùö[J
N¬àBÇàù[ò›[€à€€[X[ô[]TôX€‹ôò[YJôX€‹ôŸ^\ H¬àYà
\ôX€‹ô\[ŸàôX€‹ôOOH	€ÿöôX›	 Hô]\õà	…Œ¬à€€ú›€€ùZ[ô\ú»H‹ôX€‹ôôX€‹ôõ‹[€úÀôX€‹ôú\ò[\ÀôX€‹ôùôZX€KôX€‹ôòùZ[[ôÀôX€‹ôô]KôX€‹ôùôZX€Q]KôX€‹ôó›ôZX€Q]WBàôö[\ä][HOà][H	âà\[Ÿà][HOOH	€ÿöôX›	 N¬àõ‹à
€€ú›€€ùZ[ô\àŸà€€ùZ[ô\ú H¬àõ‹à
€€ú›Ÿ^HŸàŸ^\ H¬à€€ú›ò[YHH€€ùZ[ô\ñ⁄Ÿ^WN¬àYà
ò[YHOOH[ôYö[ôY	âàò[YHOOHù[	âà›ö[ô ò[YJKùö[J
JHô]\õà›ö[ô ò[YJKúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
N¬àBàBàô]\õà	…Œ¬àBÇàù[ò›[€à€€[X[ô[]T⁄[ù
€›\òŸJH¬àYà
\€›\òŸJHô]\õàù[¬àûH¬à€€ú›⁄[ùH€›\òŸKôŸ]]ôœÀä
N¬àYà
ù[Xô\ãö\—ö[ö]Jù[Xô\ä⁄[ùÀõ]
JH	âàù[Xô\ãö\—ö[ö]Jù[Xô\ä⁄[ùÀõô JJHô]\õà»]àù[Xô\ä⁄[ùõ]
KôŒàù[Xô\ä⁄[ùõô HN¬àHÿ]⁄
\úäHﬂBà€€ú›]ô»H€›\òŸKó€]ô»€›\òŸKõ]ô»€›\òŸKú‹⁄][€à€›\òŸKõ‹[€úœÀõ]ôŒ¬à€€ú›]Hù[Xô\ä€›\òŸKõ]œ»€›\òŸKõ]]YHœ»€›\òŸKõ‹[€úœÀõ]œ»€›\òŸKõ‹[€úœÀõ]]YHœ»]ôœÀõ]
N¬à€€ú›ô»Hù[Xô\ä€›\òŸKõô»œ»€›\òŸKõ€àœ»€›\òŸKõ€ô⁄]YHœ»€›\òŸKõ‹[€úœÀõô»œ»€›\òŸKõ‹[€úœÀõ€àœ»€›\òŸKõ‹[€úœÀõ€ô⁄]YHœ»]ôœÀõô»œ»]ôœÀõ€äN¬àô]\õàù[Xô\ãö\—ö[ö]J]
H	âàù[Xô\ãö\—ö[ö]Jô H»»]ô»Hàù[¬àBÇàù[ò›[€à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã[ùûJH¬à€€ú›⁄[ôH””SPSë‘SUW““Së”QUVŸ[ùûOÀö⁄[ôH»[ùûKö⁄[ôà	ÿX›[€âŒ¬à€€ú›]HH›ö[ô [ùûOÀù]H	… Kúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
N¬àYà
]]H\[Ÿà[ùûOÀô^X›]HOOH	Ÿù[ò›[€â Hô]\õé¬à€€ú›YH›ö[ô [ùûKöY	⁄⁄[ôNâ›]_X
N¬àYà
ŸY[ãö\ Y
JHô]\õé¬àŸY[ãòY
Y
N¬à€€ú›]Z[H›ö[ô [ùûKô]Z[	… Kúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
N¬à[ùöY\Àú\⁄
¬àããô[ùûKàYà⁄[ôà]Kà]Z[àôX]\ôYàõ€€X[ä[ùûKôôX]\ôY
KàŸX\ò⁄^à€€[X[ô[]Sõ‹õX[\ŸJ	›]_H	Ÿ]Z[H	Ÿ[ùûKù\õ\»	…ﬂX
BàJN¬àBÇàù[ò›[€à€€[X[ô[]Qõÿ›\”X\ôX€‹ô
⁄[ôY€›\òŸK]JH¬à€€ú›⁄[ùH€€[X[ô[]T⁄[ù
€›\òŸJN¬à€€ú›X\Hö[ôXYõ]X\[ú›[òŸJò[ŸJN¬àYà
X\	âà⁄[ù
H¬àûH¬à€€ú›õ€€HHX]õX^
LÀù[Xô\äX\ôŸ]õ€€OÀä
JHL N¬àX\úŸ]öY] ‹⁄[ùõ]⁄[ùõô◊Kõ€€K›]KôX€€õ€^S[ŸH»»[ö[X]Nàò[ŸHHà[ôYö[ôY
N¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	ÀõXYõ][X\öŸ\ãZX€€ãõX€\ÀX€€[X[ô\[]KYõÿ›\… Kôõ‹ëXX⁄
X€€àOàX€€ãò€\‹”\›úô[[›ôJ	€X€\ÀX€€[X[ô\[]KYõÿ›\… JN¬à€›\òŸOÀó⁄X€€èÀò€\‹”\›ÀòY
	€X€\ÀX€€[X[ô\[]KYõÿ›\… N¬à€›\òŸOÀõ‹[î‹\Àä
N¬à⁄›’ÿ\›
]H	⁄⁄[ôHÿÿ]Y
N¬àô]\õàùYN¬àHÿ]⁄
\úäHﬂBàBàYà
Y	âà…›ôZX€IÀ	ÿùZ[[ô…◊Kö[ò€Y\ ⁄[ô
JH¬à€€ú›]H…⁄⁄[ôOOH	›ôZX€I»»	›ôZX€\…»à	ÿùZ[[ô‹…ﬂK…Ÿ[ò€ŸUTíP€€\€ô[ù
Y
_X¬àûH¬àYà
\[ŸàYŸU⁄[ô›ÀõY⁄õﬁ‹[àOOH	Ÿù[ò›[€â HYŸU⁄[ô›ÀõY⁄õﬁ‹[ä]
N¬à[ŸHYŸU⁄[ô›Àõÿÿ][€ãöôYàH]¬àô]\õàùYN¬àHÿ]⁄
\úäHﬂBàBà⁄›’ÿ\›
	⁄⁄[ôOOH	›ôZX€I»»	’ôZX€I»à	–ùZ[[ô…ﬂH\»õ»€ôŸ\à]òZ[XõX
N¬àô]\õàò[ŸN¬àBÇàù[ò›[€àôZX€SX\öŸ\ëõ‹íY
ôZX€RY
H¬à€€ú›YH›ö[ô ôZX€RY	… N¬àYà
ZY
Hô]\õàù[¬àô]\õàŸ]ôZX€SX\öŸ\ì^Y\ú 
Kôö[ô
X\öŸ\àOàôZX€TôX€‹ôY
X\öŸ\äHOOHY
Hù[¬àBÇàù[ò›[€à[ö]ÿÿ]‹îôX€‹ô ]Y\ûHH[ö]ÿÿ]‹î]Y\ûJH¬à€€ú›X\öŸ\êûRYHô]»X\
Ÿ]ôZX€SX\öŸ\ì^Y\ú 
KõX\
X\öŸ\àOà›ôZX€TôX€‹ôY
X\öŸ\äKX\öŸ\óJKôö[\ä
⁄YJHOàYOOHù[
JN¬à€€ú›õ‹õX[\ŸY]Y\ûHH€€[X[ô[]Sõ‹õX[\ŸJ]Y\ûJN¬à€€ú›\õ\»Hõ‹õX[\ŸY]Y\ûKú‹]
	»	 Kôö[\äõ€€X[äN¬à€€ú›õ›‹»H◊N¬àõ‹à
€€ú›ôX€‹ôŸàŸ]\ú€€ò[ôZX€TôX€‹ô 
JH¬à€€ú›YHôZX€TôX€‹ôY
ôX€‹ô
N¬àYà
ZY
H€€ù[ùYN¬à€€ú›X\öŸ\àHX\öŸ\êûRYôŸ]
Y
Hù[¬à€€ú›€\‹⁄YöXÿ][€àH›\›€UôZX€P€\‹⁄YöXÿ][€ëúõ€TôX€‹ô
ôX€‹ô
H›\›€UôZX€P€\‹⁄YöXÿ][€ëõ‹íY
Y
N¬à€€ú›ÿ\[€àH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…ÿÿ\[€âÀ	€ò[YIÀ	›]I◊JHôZX€H	⁄YX¬à€€ú›\HH€\‹⁄YöXÿ][€èÀòÿ]Y€‹ûH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…›ôZX€W›\Wÿÿ\[€âÀ	›ôZX€U\Pÿ\[€âÀ	›ôZX€W›\W€ò[YIÀ	›ôZX€U\Sò[YIÀ	›\Wÿÿ\[€âÀ	›\Pÿ\[€â◊JN¬à€€ú››][€àH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…ÿùZ[[ô◊ÿÿ\[€âÀ	ÿùZ[[ô–ÿ\[€âÀ	ÿùZ[[ô◊€ò[YIÀ	ÿùZ[[ô”ò[YIÀ	‹›][€óÿÿ\[€âÀ	‹›][€êÿ\[€âÀ	‹›][€ó€ò[YIÀ	‹›][€ìò[YI◊JN¬à€€ú››]\»HôZX€T›]\–€ŸJôX€‹ô
N¬à€€ú›ùX⁄Ÿ]HôZX€T›]\–ùX⁄Ÿ]
ôX€‹ô
N¬à€€ú›⁄Y€ò[H€€[X[ô[]Sõ‹õX[\ŸJ	ÿÿ\[€üH	⁄YH	›\_H	‹›][€üH	›ôZX€TŸX\ò⁄⁄Y€ò[
ôX€‹ô
_H	‹›]\»œ»	…ﬂH	ÿùX⁄Ÿ]X
N¬àYà
\õ\Àú€€YJ\õHOà\⁄Y€ò[ö[ò€Y\ \õJJJH€€ù[ùYN¬à€€ú›ÿ€‹ôHHõ‹õX[\ŸY]Y\ûH	âà€€[X[ô[]Sõ‹õX[\ŸJÿ\[€äKú›\ù’⁄]
õ‹õX[\ŸY]Y\ûJH»ààõ‹õX[\ŸY]Y\ûH	âà›ö[ô Y
Kú›\ù’⁄]
õ‹õX[\ŸY]Y\ûJH»BààX\öŸ\à»ààŒ¬àõ›‹Àú\⁄
»Yÿ\[€ã\K›][€ã›]\ÀùX⁄Ÿ]X\öŸ\ãÿ€‹ôHJN¬àBàô]\õàõ›‹Àú€‹ù

KäHOàKúÿ€‹ôHHãúÿ€‹ôHKòÿ\[€ãõÿÿ[P€€\\ôJãòÿ\[€ã[ôYö[ôY»ù[Y\öXŒàùYHJJKú€XŸJå
N¬àBÇàù[ò›[€àô[ô\ï[ö]ÿÿ]‹îô\›[ ›ô\õ^HH€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô^\öY[òŸS[Ÿ[Y
JH¬à€€ú›\ôŸ]H›ô\õ^OÀú]Y\ûTŸ[X›‹èÀä	÷Ÿ]K][ö][ÿÿ]‹ã\ô\›[◊I N¬àYà
]\ôŸ]
Hô]\õà¬à€€ú›õ›‹»H[ö]ÿÿ]‹îôX€‹ô 
N¬à€€ú›[Hõ›‹Àõ[ô›»õ›‹ÀõX\
õ›»Oà¬à€€ú›ÿÿ]YHõ€€X[äõ›ÀõX\öŸ\äN¬à€€ú›]Z[HÿQ	‹õ›ÀöYXìT»	‹õ›Àú›]\»OOHù[»	œ…»àõ›Àú›]\ﬂXõ›ÀòùX⁄Ÿ]OOH	€›\â»»	…»àõ›ÀòùX⁄Ÿ]õ›Àù\Kõ›Àú›][€óKôö[\äõ€€X[äKöõ⁄[ä	»0≠»	 N¬àô]\õà\ùX€H€\‹œHõX€\À][ö][ÿÿ]‹ã\õ›»à]K]ôZX€KZYHâŸ\ÿÿ\R[
õ›ÀöY
_Hèè]èè›õ€ôœâŸ\ÿÿ\R[
õ›Àòÿ\[€ä_O‹›õ€ôœè€X[âŸ\ÿÿ\R[
]Z[
_O‹€X[èŸ]èè]èèù]€à\OHòù]€àà]K[X€\ÀX€€[X[ôXX›[€èHù[ö][ÿÿ]‹ã[ÿÿ]Hà]K]ôZX€KZYHâŸ\ÿÿ\R[
õ›ÀöY
_Hà	€ÿÿ]Y»	…»à	Ÿ\ÿXõY	ﬂOìÿÿ]Oÿù]€èèù]€à€\‹œHõX€\À\ö[X\ûHà\OHòù]€àà]K[X€\ÀX€€[X[ôXX›[€èHù[ö][ÿÿ]‹ãYõ€›»à]K]ôZX€KZYHâŸ\ÿÿ\R[
õ›ÀöY
_Hà]K]ôZX€K[Xô[HâŸ\ÿÿ\R[
õ›Àòÿ\[€ä_Hà	€ÿÿ]Y»	…»à	Ÿ\ÿXõY	ﬂOâŸõ€›ŸYôZX€RYOOHõ›ÀöY»	—õ€›⁄[ô…»à	—õ€›…ﬂOÿù]€èèŸ]èèÿ\ùX€Oò¬àJKöõ⁄[ä	… Hà	œ€\‹œHõX€\ÀX€€[X[ô[õ›Hèìõ»\ú€€ò[ôZX€\»X]⁄]ŸX\ò⁄è‹âŒ¬àŸ][õô\í[Yê⁄[ôŸY
\ôŸ][
N¬àô]\õàõ›‹Àõ[ô›¬àBÇàù[ò›[€à‹[ï[ö]ÿÿ]‹ä
H¬àYà
›]KúÿYôS[ŸKô[òXõY
H»⁄›’ÿ\›
	—^]€€⁄]ÿYôH[ŸH»\ŸHôZX€Hõ€›… N»ô]\õàò[ŸN»Bà€€⁄][ò[]X‹‘ôX€‹ôôX]\ôJ	›[ö]ÿÿ]‹â N¬àX\ö—ôX]\ôPôXX€€ïöY]ŸY
	›[ö]ÿÿ]‹â N¬à€€ú››ô\õ^HH‹[ê€€[X[ô^\öY[òŸS[Ÿ[
¬à⁄[ôà	’[ö]ÿÿ]‹âÀà]Nà	’[ö]ÿÿ]‹à	àõ€›»[ŸIÀà›Xù]Nà	‘ŸX\ò⁄[›\à›\úô[ù\ú€€ò[ôZX€\»ûHÿ\[€ãQ\K›][€à‹à›]\ÀâÀàõŸNàXô[€\‹œHõX€\ÀX€€[X[ô[õ›Hàõ‹èHõX€\À][ö][ÿÿ]‹ã\ŸX\ò⁄èïôZX€HŸX\ò⁄€Xô[è[ú]YHõX€\À][ö][ÿÿ]‹ã\ŸX\ò⁄à€\‹œHõX€\ÀZ[ú]à]K][ö][ÿÿ]‹ã\]Y\ûH\OHúŸX\ò⁄à]]ÿ€€\]OHõŸôààò[YOHâŸ\ÿÿ\R[
[ö]ÿÿ]‹î]Y\ûJ_HàXŸZ€\èHôKôÀàô\ÿ›YHKTïã›][€à‹àìT»àà]]Ÿõÿ›\œè]à€\‹œHõX€\À][ö][ÿÿ]‹ã\ô\›[»à]K][ö][ÿÿ]‹ã\ô\›[œèŸ]èè€\‹œHõX€\ÀX€€[X[ô[õ›Hèëõ€›»[ŸHŸ[ùô\»€õH⁄[H]ôZX€HX\öŸ\àô[XZ[ú»]ôKàX[ùX[X\[›ô[Y[ù›‹»õ€›⁄[ô»[[YYX][Kè‹òàX›[€úŒàõ€›ŸYôZX€RY»	œù]€à\OHòù]€àà]K[X€\ÀX€€[X[ôXX›[€èHùôZX€KYõ€›À\›‹èî›‹õ€›⁄[ôœÿù]€èâ»à	…¬àJN¬à›ô\õ^Kõ€ö[ú]H]ô[ùOà¬àYà
Y]ô[ùù\ôŸ]ÀõX]⁄\œÀä	÷Ÿ]K][ö][ÿÿ]‹ã\]Y\ûWI JHô]\õé¬à[ö]ÿÿ]‹î]Y\ûHH›ö[ô ]ô[ùù\ôŸ]ùò[YH	… Kú€XŸJLå
N¬àô[ô\ï[ö]ÿÿ]‹îô\›[ ›ô\õ^JN¬àN¬àô[ô\ï[ö]ÿÿ]‹îô\›[ ›ô\õ^JN¬àYà
]ôZX€P\TôXYJHõ€Z\ŸKúô\€€ôJôYúô\⁄\ú€€ò[ôZX€Q]Jò[ŸJJKù[ä

HOà¬àYà
›ô\õ^Kö\–€€õôX›Y	âà›ô\õ^Kô]\Ÿ]ö⁄[ôOOH	’[ö]ÿÿ]‹â Hô[ô\ï[ö]ÿÿ]‹îô\›[ ›ô\õ^JN¬àJKòÿ]⁄


HOàﬂJN¬àô]\õàùYN¬àBÇàù[ò›[€à\]UôZX€Qõ€›–ò[õô\ä
H¬à]ò[õô\àH€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTùôZX€Qõ€›“Y
N¬àYà
Yõ€›ŸYôZX€RY
H»ò[õô\èÀúô[[›ôJ
N»ô]\õàò[ŸN»BàYà
Xò[õô\äH¬àò[õô\àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àò[õô\ãöYH–‘íTùôZX€Qõ€›“Y¬àò[õô\ãúŸ]]öXù]J	‹õ€IÀ	‹›]\… N¬àÿ›[Y[ùòõŸKò\[ô⁄[
ò[õô\äN¬àBàŸ][õô\í[Yê⁄[ôŸY
ò[õô\ã‹[èè›õ€ôœëõ€›⁄[ôœ‹›õ€ôœà	Ÿ\ÿÿ\R[
õ€›ŸYôZX€SXô[ôZX€H	Ÿõ€›ŸYôZX€RYX
_O‹‹[èèù]€à\OHòù]€àà]K[X€\ÀX€€[X[ôXX›[€èHùôZX€KYõ€›À\›‹èî›‹ÿù]€èò
N¬àô]\õàùYN¬àBÇàù[ò›[€à›‹ôZX€Qõ€› [õõ›[òŸHHùYJH¬à€€ú›ÿ\–X›]ôHHõ€€X[äõ€›ŸYôZX€RYõ€›ŸYôZX€SX\öŸ\äN¬àYà
õ€›ŸYôZX€SX\öŸ\à	âàõ€›ŸYôZX€S[›ôR[ô\äH¬àûH»õ€›ŸYôZX€SX\öŸ\ãõŸôèÀä	€[›ôIÀõ€›ŸYôZX€S[›ôR[ô\äN»Hÿ]⁄
\úäHﬂBàBàõ€›ŸYôZX€RYH	…Œ¬àõ€›ŸYôZX€SXô[H	…Œ¬àõ€›ŸYôZX€SX\öŸ\àHù[¬àõ€›ŸYôZX€S[›ôR[ô\àHù[¬àôZX€Qõ€›‘ôXŸ[ù\ö[ô»Hò[ŸN¬à€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTùôZX€Qõ€›“Y
OÀúô[[›ôJ
N¬àYà
[õõ›[òŸH	âàÿ\–X›]ôJH⁄›’ÿ\›
	’ôZX€Hõ€›»[ŸH›‹Y	 N¬àô]\õàÿ\–X›]ôN¬àBÇàù[ò›[€àŸ[ùôQõ€›’ôZX€JX\öŸ\ã»[ö]X[Hò[ŸHHHﬂJH¬àYà
[X\öŸ\àX\öŸ\àOOHõ€›ŸYôZX€SX\öŸ\àYõ€›ŸYôZX€RY
Hô]\õàò[ŸN¬à€€ú›X\Hö[ôXYõ]X\[ú›[òŸJò[ŸJN¬à]]ô»Hù[¬àûH»]ô»HX\öŸ\ãôŸ]]ôœÀä
Hù[»Hÿ]⁄
\úäHﬂBàYà
[X\[]ô Hô]\õàò[ŸN¬àôZX€Qõ€›‘ôXŸ[ù\ö[ô»HùYN¬àûH¬à€€ú›õ€€HHX]õX^
LÀù[Xô\äX\ôŸ]õ€€OÀä
JHL N¬àYà
[ö]X[
HX\úŸ]öY] ]ôÀõ€€K›]KôX€€õ€^S[ŸH»»[ö[X]Nàò[ŸHHà[ôYö[ôY
N¬à[ŸHX\ú[ï ]ôÀ›]KôX€€õ€^S[ŸH»»[ö[X]Nàò[ŸHHà»[ö[X]NàùYK\ò][€éàåÕHJN¬àHÿ]⁄
\úäH¬àûH»X\úŸ]öY] ]ôÀX]õX^
LÀù[Xô\äX\ôŸ]õ€€OÀä
JHL JN»Hÿ]⁄
ô\›Y\úõ‹äH»ô]\õàò[ŸN»BàHö[ò[H¬àôZX€Qõ€›‘ôXŸ[ù\ö[ô»Hò[ŸN¬àBàô]\õàùYN¬àBÇàù[ò›[€à›\ùôZX€Qõ€› ôZX€RYXô[H	… H¬àYà
›]KúÿYôS[ŸKô[òXõY
H»⁄›’ÿ\›
	—^]€€⁄]ÿYôH[ŸH»\ŸHôZX€Hõ€›… N»ô]\õàò[ŸN»Bà€€ú›YH›ö[ô ôZX€RY	… N¬à€€ú›X\öŸ\àHôZX€SX\öŸ\ëõ‹íY
Y
N¬àYà
[X\öŸ\äH»⁄›’ÿ\›
	’ôZX€HX\öŸ\à\»õ››\úô[ùH]òZ[XõI N»ô]\õàò[ŸN»Bà›‹ôZX€Qõ€› ò[ŸJN¬àõ€›ŸYôZX€RYHY¬àõ€›ŸYôZX€SXô[H›ö[ô Xô[€€[X[ô[]TôX€‹ôò[YJX\öŸ\ã…ÿÿ\[€âÀ	€ò[YIÀ	›]I◊JHôZX€H	⁄YX
Kú€XŸJLå
N¬àõ€›ŸYôZX€SX\öŸ\àHX\öŸ\é¬àõ€›ŸYôZX€S[›ôR[ô\àH

HOà¬àYà
XŸ[ùôQõ€›’ôZX€JX\öŸ\äJH›‹ôZX€Qõ€› ùYJN¬àN¬àûH»X\öŸ\ãõ€èÀä	€[›ôIÀõ€›ŸYôZX€S[›ôR[ô\äN»Hÿ]⁄
\úäHﬂBà\]UôZX€Qõ€›–ò[õô\ä
N¬àŸ[ùôQõ€›’ôZX€JX\öŸ\ã»[ö]X[àùYHJN¬àX\ö—ôX]\ôPôXX€€ïöY]ŸY
	›[ö]ÿÿ]‹â N¬à€‹ŸP€€[X[ô^\öY[òŸS[Ÿ[
»ô\›‹ôQõÿ›\Œàò[ŸHJN¬à⁄›’ÿ\›
õ€›⁄[ô»	Ÿõ€›ŸYôZX€SXô[H0≠»[›ôHHX\»›‹
N¬àô]\õàùYN¬àBÇàù[ò›[€àôYúô\⁄ôZX€Qõ€›–ö[ô[ô »›‹YìZ\‹⁄[ô»Hò[ŸHHHﬂJH¬àYà
Yõ€›ŸYôZX€RY
Hô]\õàò[ŸN¬à€€ú›X\öŸ\àHôZX€SX\öŸ\ëõ‹íY
õ€›ŸYôZX€RY
N¬àYà
[X\öŸ\äH¬àYà
›‹YìZ\‹⁄[ô H›‹ôZX€Qõ€› ùYJN¬àô]\õàò[ŸN¬àBàYà
X\öŸ\àOOHõ€›ŸYôZX€SX\öŸ\äH¬àYà
õ€›ŸYôZX€SX\öŸ\à	âàõ€›ŸYôZX€S[›ôR[ô\äH¬àûH»õ€›ŸYôZX€SX\öŸ\ãõŸôèÀä	€[›ôIÀõ€›ŸYôZX€S[›ôR[ô\äN»Hÿ]⁄
\úäHﬂBàBàõ€›ŸYôZX€SX\öŸ\àHX\öŸ\é¬àõ€›ŸYôZX€S[›ôR[ô\àH

HOà¬àYà
XŸ[ùôQõ€›’ôZX€JX\öŸ\äJH›‹ôZX€Qõ€› ùYJN¬àN¬àûH»X\öŸ\ãõ€èÀä	€[›ôIÀõ€›ŸYôZX€S[›ôR[ô\äN»Hÿ]⁄
\úäHﬂBàBà\]UôZX€Qõ€›–ò[õô\ä
N¬àô]\õàùYN¬àBÇàù[ò›[€à€€[X[ô[]S‹[îŸ][ô ŸX›[€ãÿ\ô€Y»H	… H¬à€€ú›Ÿ^HH””SPSë‘—P’S”ó”‘ëTãö[ò€Y\ ŸX›[€äH»ŸX›[€àà	‹Ÿ][ô‹…Œ¬à‹[î[ô[

N¬àŸ]X›]ôUXäŸ^JN¬à€€ú›[ô[H€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTú[ô[Y
N¬à[ô[Àú]Y\ûTŸ[X›‹ê[Àä	ÀõX€\ÀX€€[X[ôXÿ\ôõX€\ÀX€€[X[ô\[]K]\ôŸ]	 Kôõ‹ëXX⁄
ÿ\ôOàÿ\ôò€\‹”\›úô[[›ôJ	€X€\ÀX€€[X[ô\[]K]\ôŸ]	 JN¬à€€ú›Ÿ[X›‹àHÿ\ô€Y»»õX€\À]Xã\[ô[Ÿ]K\[ô[Hâ⁄Ÿ^_HóHõX€\ÀX€€[X[ôXÿ\ôŸ]KX€€[X[ôXÿ\ôHâÿÿ\ô€YﬂHóXàõX€\À]Xã\[ô[Ÿ]K\[ô[Hâ⁄Ÿ^_HóX¬à€€ú›\ôŸ]H[ô[Àú]Y\ûTŸ[X›‹èÀäŸ[X›‹äN¬àYà
]\ôŸ]
Hô]\õàò[ŸN¬àYà
\ôŸ]ò€\‹”\›Àò€€ùZ[ú 	€X€\ÀX€€[X[ôXÿ\ô	 JH\ôŸ]ò€\‹”\›òY
	€X€\ÀX€€[X[ô\[]K]\ôŸ]	 N¬àûH»\ôŸ]úÿ‹õ€[ù’öY] »õÿ⁄Œà	ÿŸ[ù\âÀ[õ[ôNà	€ôX\ô\›	ÀôZ]ö[‹éà	‹€[€›	»JN»Hÿ]⁄
\úäH»\ôŸ]úÿ‹õ€[ù’öY]œÀä
N»Bàô]\õàùYN¬àBÇàù[ò›[€à€€[X[ô[]PX›[€ë[ùöY\ [ùöY\ÀŸY[äH¬à€€ú›YH
Y]K]Z[\õ\À^X›]KôX]\ôYHò[ŸJHOà€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàX›[€éâ⁄YX⁄[ôà	ÿX›[€âÀ]K]Z[\õ\À^X›]KôX]\ôYàJN¬à€€ú›ŸŸ€HH
Y]K[òXõYôX]\ôK\õ\»H	… HOàY
àYà	Ÿ[òXõY»	—\ÿXõI»à	—[òXõIﬂH	›]_Xà€€⁄]€€[X[ô0≠»›\úô[ùH	Ÿ[òXõY»	€€â»à	€ŸôâﬂXà	›]_HŸŸ€H\õà€àŸôà	›\õ\ﬂXà

HOàŸŸ€QôX]\ôJôX]\ôJBà
N¬ÇàY
	‹Ÿ][ô‹…À	”‹[à€€⁄]Ÿ][ô‹…À	”‹[àH[öYöYY€€[X[ô[ù\ôòXŸIÀ	€Y[ùHôYô\ô[òŸ\»€€ôöY›\ò][€âÀ

HOà‹[î[ô[

KùYJN¬àY
	‹\ú€€ò[\ÿ][€âÀ	”‹[à\ú€€ò[\ÿ][€à›Y[…À	”^[›]À[Y\Àÿ[YH›[[ôÀ[ú]]ZX⁄»⁄Y[òX⁄›\ÀŸ]\[ô[\ù…À	ÿ›\›€Z^ôH›\›€Z\ŸH\X\ò[òŸH€›[ôõ›YöXÿ][€àòX⁄›\⁄^ò\ô›Ÿ^\»Ÿ\›\ô\»ô\⁄⁄[âÀ

HOà‹[î\ú€€ò[\ÿ][€î›Y[ 
KùYJN¬àY
	⁄[ú]\›Y[…À	”‹[à›Ÿ^H	àŸ\›\ôH›Y[…À	‘ô[X\€€⁄]Ÿ^\À\‹⁄Y€à›X⁄Ÿ\›\ô\»[ôX\õà€€ù^X[€€[X[ô…À	⁄[ú]⁄‹ù›]»öY⁄€X⁄»€ô»ô\‹»€€ù^Y[ùH›⁄\IÀ

HOà‹[î\ú€€ò[\ÿ][€î›Y[ 	⁄[ú]	 KùYJN¬àY
	‹⁄[\›Y[…À	”‹[à€€⁄]	àÿ[YH›[IÀ	”Z\‹⁄[€ê⁄YYàô\⁄⁄[ã€X\ù]]ÀZY[ô»ÿ⁄»[ôÿYôH[ŸIÀ	›[YHô\⁄⁄[àÿ⁄»€€\ŸHÿYôHôX€›ô\ûIÀ

HOà‹[î\ú€€ò[\ÿ][€î›Y[ 	‹⁄[	 KùYJN¬àY
	›[ö][ÿÿ]‹âÀ	”‹[à[ö]ÿÿ]‹à	àõ€›»[ŸIÀ	—ö[ô[ûH\ú€€ò[ôZX€H[ô[Xô\ò][Hõ€›»]»]ôHX\X\öŸ\âÀ	›ôZX€HŸX\ò⁄ö[ôÿÿ]HòX⁄»›][€à›]\»õ\…À

HOà‹[ï[ö]ÿÿ]‹ä
KùYJN¬àY
	‹Ÿ\‹⁄[€ãX€X[ù\	À	”‹[àŸ\‹⁄[€à€X[ù\	À	‘ô]öY]»[ô€X\à€õH[\‹ò\ûH€€⁄]Ÿ\‹⁄[€à›]IÀ	€XZ[ù[ò[òŸH[\‹ò\ûH›[Hõ›YöXÿ][€ú»YôôX›»ÿX⁄Hô\Ÿ\ùôHŸ][ô‹…À

HOà‹[îŸ\‹⁄[€ê€X[ù\

KùYJN¬àY
	‹ÿYôK[[ŸIÀ	‹›]KúÿYôS[ŸKô[òXõY»	—^]	»à	—[ù\âﬂH€€⁄]ÿYôH[ŸX	’[\‹ò\ö[H›\‹[ô‹[€ò[[Ÿ[\»⁄]›]⁄[ô⁄[ô»Z\àŸ][ô‹…À	ŸXY€õ‹ŸHõ›Xõ\⁄€›ô\›‹ôHôX€›ô\ûIÀ

HOàŸ]€€⁄]ÿYôS[ŸJ\›]KúÿYôS[ŸKô[òXõY
KùYJN¬àY
	‹ô\‹›\ôKXõÿ\ô	À	€‹\ò][€ò[ô\‹›\ôPõÿ\ô‹[ä
H»	–€‹ŸI»à	”‹[âﬂH‹\ò][€ò[ô\‹›\ôHõÿ\ô	”]ôH[X[ô[ôô\‹€úŸHô\‹›\ôHX‹õ‹‹»X›]ôHZ\‹⁄[€ú…À	€Z\‹⁄[€àõÿ\ô\⁄õÿ\ô[X[ôòY\âÀ

HOàŸŸ€S‹\ò][€ò[ô\‹›\ôPõÿ\ô

KùYJN¬àY
	›ôZX€KX€Ÿ\…À	ÿ€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTùôZX€T›]\“Y
OÀò€\‹”\›Àò€€ùZ[ú 	€X€\À[‹[â H»	–€‹ŸI»à	”‹[âﬂHôZX€H€ŸH›]\ÿ	“[ú‹X››\úô[ù\ú€€ò[][ö]]òZ[Xö[]HûHìT»€ŸIÀ	›ôZX€\»[ö]»]òZ[Xö[]H›]\»õ\»€Ÿ\…À

HOàŸŸ€UôZX€P€ŸT›]\ 
KùYJN¬àY
	Ÿù[ÿ‹ôY[âÀ	‹›]Kôù[ÿ‹ôY[ìX\»	—^]	»à	—[ù\âﬂHù[Tÿ‹ôY[àX\X\ù[\ÿ‹ôY[à[ŸH0≠»›\úô[ùH	‹›]Kôù[ÿ‹ôY[ìX\»	€€â»à	€ŸôâﬂX	Ÿù[ÿ‹ôY[àX^[Z\ŸHX^[Z^ôHô\›‹ôIÀ

HOàŸ]X\ù[ÿ‹ôY[ä\›]Kôù[ÿ‹ôY[ìX\
KùYJN¬àY
	€X\[YX\›\ôIÀ	€X\YX\›\ôTù[ù[YKòX›]ôH»	‘ô]\õà…»à	”‹[âﬂHò]⁄[ôÿ	”YX\›\ôH[à⁄[€Y]ô\»[ôY[\‹ò\ûH[ô\À\úõ›‹ÀúôYZ[ô⁄Ÿ]⁄\À⁄\\Àõ€ô\À^[ôX\öŸ\ú…À	Ÿò]⁄[ô»ò]»YX\›\ôHù[\àò[ôŸH⁄[€Y]ô\»€H\ôXH[ôH\úõ›»⁄\ò€HôX›[ô€H€Y€€àõ€ôHXô[X\öŸ\àúôYZ[ô	À

HOà›\ùX\YX\›\ôJ
KùYJN¬àY
	Ÿÿ›‹âÀ	‘ù[à€€⁄]ÿ›‹âÀ	‘ÿYôH\Ÿ\ã]öYŸŸ\ôYXY€õ‹›X‹»[ôRHô\Z\âÀ	⁄X[ô\‹ùÿ\õö[ô»ô\Z\àXY€õ‹›X…À

HOà»õ⁄Yù[ï€€⁄]ÿ›‹ä
N»KùYJN¬àY
	⁄[	À	”‹[à[Ÿ[ùôIÀ	‘ŸX\ò⁄H€€\]H€€⁄]›ZYIÀ	Ÿÿ›[Y[ù][€à[ú›ùX›[€ú»›\‹ù›ZYIÀ

HOà‹[í[Ÿ[ù\ä
JN¬àY
	ÿúöYYö[ô…À	”‹[à\]HúöYYö[ô…Àô]öY]»⁄]⁄[ôŸY[à€€⁄]	‘–‘íTùô\ú⁄[€üX	‹ô[X\ŸHõ›\»⁄]»ô]»ô\ú⁄[€âÀ

HOà‹[ï\]PúöYYö[ô »X[ùX[àùYHJJN¬àY
	‹]ZX⁄À]⁄Y[	À	”‹[àXõ]]ZX⁄»⁄Y[	À⁄›»H€€ôöY›\ôY	‹›]Kú]ZX⁄’⁄Y[ú€›€›[ùK\€››X⁄€€[X[ô⁄Y[	›Xõ]›X⁄€ô»ô\‹»òYX[⁄Y[	À

HOà‹[ïXõ]]ZX⁄’⁄Y[
ù[»X[ùX[àùYHJJN¬àY
	ÿ€€[X[ôXò\âÀ	‹›]Kò€€[X[ôò\ì‹[àOOHò[ŸH»	‘⁄›…»à	“YIﬂHX\€€[X[ôò\ò\ú⁄\›[ùX\€€[X[ô€€ùõ€»0≠»›\úô[ùH	‹›]Kò€€[X[ôò\ì‹[àOOHò[ŸH»	⁄Y[â»à	‹⁄›€âﬂX	Ÿÿ⁄»€€ò\à€€\ŸH^[ô	À

HOàŸŸ€P€€[X[ôò\ä
JN¬àY
	ŸX€€õ€^IÀ	‹›]KôX€€õ€^S[ŸH»	—\ÿXõI»à	—[òXõIﬂHX€€õ€^H[ŸX\ôõ‹õX[òŸH[ŸH0≠»›\úô[ùH	‹›]KôX€€õ€^S[ŸH»	€€â»à	€ŸôâﬂX	‹\ôõ‹õX[òŸH‹H‹H›»›Ÿ\âÀ

HOàŸ]X€€õ€^S[ŸJ\›]KôX€€õ€^S[ŸKùYJKùYJN¬ÇàŸŸ€J	‹\ú€€ò[[Z\‹⁄[€ú…À	‘\ú€€ò[Z\‹⁄[€ú…À›]Kùö\⁄Xö[]Kõ^SZ\‹⁄[€úÀ	€^SZ\‹⁄[€ú…À	€Z[ôHö\⁄Xö[]HX\öŸ\ú… N¬àŸŸ€J	ÿ[X[òŸK[Z\‹⁄[€ú…À	–[X[òŸHZ\‹⁄[€ú…À›]Kùö\⁄Xö[]Kò[X[òŸSZ\‹⁄[€úÀ	ÿ[X[òŸSZ\‹⁄[€ú…À	‹⁄\ôYö\⁄Xö[]HX\öŸ\ú… N¬àŸŸ€J	›ôZX€\…À	’ôZX€HX\öŸ\ú…À›]Kùö\⁄Xö[]KùôZX€\À	›ôZX€\…À	›[ö]»ö\⁄Xö[]I N¬àŸŸ€J	ÿùZ[[ô‹…À	–ùZ[[ô»X\öŸ\ú…À›]Kùö\⁄Xö[]KòùZ[[ô‹À	ÿùZ[[ô‹…À	‹›][€ú»ö\⁄Xö[]I N¬àŸŸ€J	‹›X⁄…À	‘›X⁄»Z\‹⁄[€à]X›[€âÀ›]Kú›X⁄—]X›‹ãô[òXõY	‹›X⁄—]X›‹âÀ	‹›X⁄»ôZX€\»›[Y[ò⁄Y[ù»Xô[… N¬àŸŸ€J	€XZõ‹ãYôYY	À	”XZõ‹à[ò⁄Y[ùôYY	À›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY	€XZõ‹í[ò⁄Y[ùôYY	À	›X⁄Ÿ\àô]‹»⁄\ôI N¬àŸŸ€J	€Z\‹⁄[€ãXYŸIÀ	”Z\‹⁄[€àYŸHXô[…À›]KõZ\‹⁄[€êYŸK	€Z\‹⁄[€êYŸIÀ	€€[ò⁄Y[ù»[YI N¬àŸŸ€J	›ò[ú‹‹ù	À	’ò[ú‹‹ùÿ]⁄\âÀ›]Kùò[ú‹‹ùÿ]⁄\ã	›ò[ú‹‹ùÿ]⁄\âÀ	‹]Y[ù»ö\€€ô\ú»[Xô\â N¬àŸŸ€J	›[ö]X€›[ù	À	’[ö]€€[Z]Y[ù€›[ù	À›]Kù[ö]€€[Z]Y[ù	›[ö]€€[Z]Y[ù	À	‹ô\‹€ô[ô»€àÿŸ[ôI N¬àŸŸ€J	€X\öŸ\ãYõÿ›\…À	”X\öŸ\àõÿ›\…À›]KõX\öŸ\ëõÿ›\À	€X\öŸ\ëõÿ›\…À	Ÿ[HùZ[[ô‹»ôZX€\»Z\‹⁄[€ú… N¬àŸŸ€J	€Z\‹⁄[€ã\[ŸIÀ	”Z\‹⁄[€à[ŸIÀ›]KõZ\‹⁄[€î[ŸK	€Z\‹⁄[€î[ŸIÀ	ÿ[ö[X][€àX\öŸ\ú… N¬àŸŸ€J	‹õÿY\ö[‹ö]IÀ	‘õÿYö[‹ö]IÀ›]KúõÿYö[‹ö]K	‹õÿYö[‹ö]IÀ	ÿ€€ùò\›õÿY»X\	 N¬àŸŸ€J	ÿ€X[ã[[ŸIÀ	–€X[à[ŸIÀ›]Kò€X[ì[ŸK	ÿ€X[âÀ	‹ÿ‹ôY[ú⁄›YH€€ùõ€… N¬àBÇàù[ò›[€à€€[X[ô[]SZ\‹⁄[€ë[ùöY\ [ùöY\ÀŸY[äH¬à€€ú›õ›»H]Kõõ› 
N¬àõ‹à
€€ú›X\öŸ\àŸàŸ]Z\‹⁄[€ìX\öŸ\í[ô^

KõX\öŸ\ú H¬à€€ú›€ò\⁄›H]ôSZ\‹⁄[€î€ò\⁄›ÀôŸ]
Z\‹⁄[€íYúõ€SX\öŸ\äX\öŸ\äJHZ\‹⁄[€î€ò\⁄›úõ€SX\öŸ\äX\öŸ\ãõ› N¬àYà
\€ò\⁄›ÀõZ\‹⁄[€íY
H€€ù[ùYN¬à€€ú›€›\òŸHH€ò\⁄›ú€›\òŸHOOH	ÿ[X[òŸI»»	–[X[òŸHZ\‹⁄[€â»à€ò\⁄›ú€›\òŸHOOH	‹\ú€€ò[	»»	‘\ú€€ò[Z\‹⁄[€â»à	–X›]ôHZ\‹⁄[€âŒ¬à€€ú›ÿÿ][€àH€ò\⁄›ú‹›€ŸH€ò\⁄›ò⁄]H€ò\⁄›òYô\‹»	…Œ¬à€€ú›[ö]»HX]õX^
ù[Xô\ä€ò\⁄›ù[ö]œÀù›[
H
N¬à€€ú›]Z[H‹€›\òŸKÿÿ][€ã[ö]»»	›[ö]ﬂH\ú€€ò[[ö]	›[ö]»OOHH»	…»à	‹…ﬂH€€[Z]Yà	…◊Kôö[\äõ€€X[äKöõ⁄[ä	»0≠»	 N¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàZ\‹⁄[€éâ‹€ò\⁄›õZ\‹⁄[€íYXà⁄[ôà	€Z\‹⁄[€âÀà]Nà€ò\⁄›òÿ\[€àZ\‹⁄[€à	‹€ò\⁄›õZ\‹⁄[€íYXà]Z[à\õ\Œà	‹€ò\⁄›õZ\‹⁄[€íYH	‹€ò\⁄›òYô\‹»	…ﬂH	‹€ò\⁄›ú‹›€ŸH	…ﬂH	‹€ò\⁄›ò⁄]H	…ﬂH	‹€ò\⁄›õZ\‹⁄[ô’^	…ﬂH	‹€›\òŸ_Xà^X›]Nà

HOàõÿ›\”Z\‹⁄[€êûRY
€ò\⁄›õZ\‹⁄[€íYùYJBàJN¬àBàBÇàù[ò›[€à€€[X[ô[]UôZX€Q[ùöY\ [ùöY\ÀŸY[äH¬à€€ú›X\öŸ\êûRYHô]»X\
Ÿ]ôZX€SX\öŸ\ì^Y\ú 
KõX\
X\öŸ\àOà›ôZX€TôX€‹ôY
X\öŸ\äKX\öŸ\óJKôö[\ä
⁄YJHOàYOOHù[
JN¬àõ‹à
€€ú›ôX€‹ôŸàŸ]\ú€€ò[ôZX€TôX€‹ô 
JH¬à€€ú›YHôZX€TôX€‹ôY
ôX€‹ô
N¬àYà
ZY
H€€ù[ùYN¬à€€ú›X\öŸ\àHX\öŸ\êûRYôŸ]
Y
HôX€‹ô¬à€€ú›€\‹⁄YöXÿ][€àH›\›€UôZX€P€\‹⁄YöXÿ][€ëúõ€TôX€‹ô
ôX€‹ô
H›\›€UôZX€P€\‹⁄YöXÿ][€ëõ‹íY
Y
N¬à€€ú›ÿ\[€àH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…ÿÿ\[€âÀ	€ò[YIÀ	›]I◊JN¬à€€ú›\HH€\‹⁄YöXÿ][€èÀòÿ]Y€‹ûH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…›ôZX€W›\Wÿÿ\[€âÀ	›ôZX€U\Pÿ\[€âÀ	›ôZX€W›\W€ò[YIÀ	›ôZX€U\Sò[YIÀ	›\Wÿÿ\[€âÀ	›\Pÿ\[€â◊JN¬à€€ú›]HHÿ\[€à\HôZX€H	⁄YX¬à€€ú››]\»HôZX€T›]\–€ŸJôX€‹ô
N¬à€€ú›ùX⁄Ÿ]HôZX€T›]\–ùX⁄Ÿ]
ôX€‹ô
N¬à€€ú›\ôŸ]HôZX€U\ôŸ][ôõ ôX€‹ô
N¬à€€ú›]Z[HÿìT»	‹›]\»OOHù[»	œ…»à›]\ﬂX\H	âà\HOOH]H»\Hà	…ÀùX⁄Ÿ]OOH	€›\â»»	…»àùX⁄Ÿ]\ôŸ]ù\H»	›\ôŸ]ù\_H	›\ôŸ]öYXà	…◊Kôö[\äõ€€X[äKöõ⁄[ä	»0≠»	 N¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàôZX€Nâ⁄YXà⁄[ôà	›ôZX€IÀà]Kà]Z[à\õ\Œà	⁄YH	›ôZX€TŸX\ò⁄⁄Y€ò[
ôX€‹ô
_H	ÿ€\‹⁄YöXÿ][€èÀòÿ]Y€‹ûH	…ﬂH	‹›]\»œ»	…ﬂH	ÿùX⁄Ÿ]Xà^X›]Nà

HOà€€[X[ô[]Qõÿ›\”X\ôX€‹ô
	›ôZX€IÀYX\öŸ\ã]JBàJN¬àBàBÇàù[ò›[€à€€[X[ô[]PùZ[[ô—[ùöY\ [ùöY\ÀŸY[äH¬à€€ú›^Y\ú»HŸ]ùZ[[ô”X\öŸ\ì^Y\ú 
Kôö[\äõ€€X[äN¬à€€ú›^Y\êûRYHô]»X\
^Y\úÀõX\
^Y\àOàŸŸ]ùZ[[ô”^Y\íY
^Y\äK^Y\óJKôö[\ä
⁄YJHOàYOOHù[
JN¬à€€ú›ôX€‹ô»Hô]»X\
Ÿ]ùZ[[ô‘ôX€‹ô[ô^

KúôX€‹ô–ûRY
N¬àõ‹à
€€ú›^Y\àŸà^Y\ú H¬à€€ú›YHŸ]ùZ[[ô”^Y\íY
^Y\äN¬àYà
YOOHù[	âà\ôX€‹ôÀö\ Y
JHôX€‹ôÀúŸ]
YŸ]ùZ[[ô‘ôX€‹ôõ‹ì^Y\ä^Y\äH^Y\äN¬àBà€€ú››\úô[ù\Ÿ\íYH›\úô[ù\Ÿ\íYÿX⁄Y

N¬àõ‹à
€€ú›⁄YôX€‹ôHŸàôX€‹ôÀô[ùöY\ 
JH¬à€€ú›^Y\àH^Y\êûRYôŸ]
›ö[ô Y
JHôX€‹ô¬à€€ú›]HH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…ÿÿ\[€âÀ	€ò[YIÀ	›]IÀ	ÿùZ[[ô◊€ò[YIÀ	ÿùZ[[ô”ò[YI◊JHùZ[[ô»	⁄YX¬à€€ú›\HH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…ÿùZ[[ô◊›\Wÿÿ\[€âÀ	ÿùZ[[ô’\Pÿ\[€âÀ	ÿùZ[[ô◊›\W€ò[YIÀ	ÿùZ[[ô’\Sò[YIÀ	›\Wÿÿ\[€âÀ	›\Pÿ\[€â◊JN¬à€€ú››€ô\íYH€€[X[ô[]TôX€‹ôò[YJôX€‹ô…›\Ÿ\ó⁄Y	À	›\Ÿ\íY	À	€›€ô\ó⁄Y	À	€›€ô\íY	◊JN¬à€€ú››€ô\ú⁄\H›\úô[ù\Ÿ\íYOOHù[	âà›€ô\íY	âà›€ô\íYOOH›\úô[ù\Ÿ\íY»	–[X[òŸHùZ[[ô…»à	‘\ú€€ò[ùZ[[ô…Œ¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàùZ[[ôŒâ⁄YXà⁄[ôà	ÿùZ[[ô…Àà]Kà]Z[à€›€ô\ú⁄\\WKôö[\äõ€€X[äKöõ⁄[ä	»0≠»	 Kà\õ\Œà	⁄YH	›\_H	€›€ô\ú⁄\Xà^X›]Nà

HOà€€[X[ô[]Qõÿ›\”X\ôX€‹ô
	ÿùZ[[ô…À›ö[ô Y
K^Y\ã]JBàJN¬àBàBÇàù[ò›[€à€€[X[ô[]Sÿÿ][€ë[ùöY\ [ùöY\ÀŸY[äH¬àõ‹à
€€ú›XŸHŸàURP“◊‘P—T H¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàÿÿ][€éú]ZX⁄Œâ‹XŸKöYXà⁄[ôà	€ÿÿ][€âÀà]NàXŸKõò[YKà]Z[à]ZX⁄»XŸH0≠»	‹XŸKõXô[Xà\õ\ŒàX\ù[\⁄]HXŸH	‹XŸKöYXàôX]\ôYàùYKà^X›]Nà

HOà»Yà
Ÿ]X\öY] XŸKõ]XŸKõôÀXŸKûõ€€JJH⁄›’ÿ\›
XŸKõò[YJN»BàJN¬àBà›]Kòõ€⁄€X\ö‹Àôõ‹ëXX⁄

õ€⁄€X\öÀ[ô^
HOà¬àYà
Xõ€⁄€X\ö Hô]\õé¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàÿÿ][€éòõ€⁄€X\öŒâ⁄[ô^Xà⁄[ôà	€ÿÿ][€âÀà]Nàõ€⁄€X\öÀõò[YHõ€⁄€X\ö»	⁄[ô^
»_Xà]Z[à›\›€Hõ€⁄€X\ö»0≠»	ÿõ€⁄€X\ö‘ÿ‹ôY[ìXô[
õ€⁄€X\ö _Xà\õ\Œàÿ]ôYÿÿ][€à€›	⁄[ô^
»_H	ÿõ€⁄€X\öÀú⁄‹ùXô[	…ﬂXà^X›]Nà

HOà€–õ€⁄€X\ö [ô^
BàJN¬àJN¬à›]KúõŸö[\Àôõ‹ëXX⁄

õŸö[K[ô^
HOà¬àYà
\õŸö[JHô]\õé¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàÿÿ][€éúõŸö[Nâ⁄[ô^Xà⁄[ôà	€ÿÿ][€âÀà]NàõŸö[Kõò[YHX\õŸö[H	⁄[ô^
»_Xà]Z[à	‘ÿ]ôYX\õŸö[H0≠»ÿYö\⁄Xö[]K⁄⁄[à[ôX\öY]…Àà\õ\ŒàõŸö[Hô\Ÿ]€›	⁄[ô^
»_Xà^X›]Nà

HOàÿYX\õŸö[J[ô^
BàJN¬àJN¬àBÇàù[ò›[€à€€[X[ô[]TŸ][ô—[ùöY\ [ùöY\ÀŸY[äH¬à€€ú›[ô[H€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTú[ô[Y
H‹ôX]T[ô[

N¬àõ‹à
€€ú›ŸX›[€àŸà\úò^Kôúõ€J[ô[Àú]Y\ûTŸ[X›‹ê[Àä	ÀõX€\À]Xã\[ô[Ÿ]K\[ô[I H◊JJH¬à€€ú›ŸX›[€íŸ^HHŸX›[€ãô]\Ÿ]ú[ô[¬à€€ú›Y]HH””SPSë‘—P’S”ó”QUV‹ŸX›[€íŸ^WN¬àYà
[Y]JH€€ù[ùYN¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàŸ][ôŒúŸX›[€éâ‹ŸX›[€íŸ^_Xà⁄[ôà	‹Ÿ][ô…Àà]NàY]Kù]Kà]Z[àY]Kô\ÿ‹ö\[€ãà\õ\Œà	€Y]KõXô[HŸX›[€àXàôYô\ô[òŸ\ÿà^X›]Nà

HOà€€[X[ô[]S‹[îŸ][ô ŸX›[€íŸ^JBàJN¬àõ‹à
€€ú›ÿ\ôŸà\úò^Kôúõ€JŸX›[€ãú]Y\ûTŸ[X›‹ê[
	ÀõX€\ÀX€€[X[ôXÿ\ôŸ]KX€€[X[ôXÿ\ôI JJH¬à€€ú›XY[ô»H›ö[ô ÿ\ôú]Y\ûTŸ[X›‹ä	ÀõX€\À\ŸX›[€ã[Xô[	 OÀù^€€ù[ùÿ\ôô]\Ÿ]ò€€[X[ôÿ\ô	… Kúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
N¬àYà
ZXY[ô H€€ù[ùYN¬à€€ú›]öXù]\»H\úò^Kôúõ€Jÿ\ôú]Y\ûTŸ[X›‹ê[
	÷›]WKŸ]K]ŸŸ€WKŸ]KXX›[€óKŸ]K\Ÿ][ô◊I JKõX\
[[Y[ùOÇà	Ÿ[[Y[ùù]H	…ﬂH	Ÿ[[Y[ùô]\Ÿ]ùŸŸ€H	…ﬂH	Ÿ[[Y[ùô]\Ÿ]òX›[€à	…ﬂH	Ÿ[[Y[ùô]\Ÿ]úŸ][ô»	…ﬂXà
Köõ⁄[ä	»	 N¬à€€[X[ô[]PY[ùûJ[ùöY\ÀŸY[ã¬àYàŸ][ôŒâ‹ŸX›[€íŸ^_Nâÿÿ\ôô]\Ÿ]ò€€[X[ôÿ\ôXà⁄[ôà	‹Ÿ][ô…Àà]NàXY[ôÀà]Z[à	€Y]Kù]_H0≠»‹[à^X›€€ùõ€‹õ›\à\õ\Œà	ÿÿ\ôù^€€ù[ù	…ﬂH	ÿ]öXù]\ﬂXà^X›]Nà

HOà€€[X[ô[]S‹[îŸ][ô ŸX›[€íŸ^Kÿ\ôô]\Ÿ]ò€€[X[ôÿ\ô
BàJN¬àBàBàBÇàù[ò›[€àùZ[€€[X[ô[]Q[ùöY\ 
H¬à€€ú›[ùöY\»H◊N¬à€€ú›ŸY[àHô]»Ÿ]

N¬à€€[X[ô[]PX›[€ë[ùöY\ [ùöY\ÀŸY[äN¬à€€[X[ô[]SZ\‹⁄[€ë[ùöY\ [ùöY\ÀŸY[äN¬à€€[X[ô[]UôZX€Q[ùöY\ [ùöY\ÀŸY[äN¬à€€[X[ô[]PùZ[[ô—[ùöY\ [ùöY\ÀŸY[äN¬à€€[X[ô[]Sÿÿ][€ë[ùöY\ [ùöY\ÀŸY[äN¬à€€[X[ô[]TŸ][ô—[ùöY\ [ùöY\ÀŸY[äN¬àô]\õà[ùöY\Œ¬àBÇàù[ò›[€à€€[X[ô[]Q[ùûTÿ€‹ôJ[ùûK]Y\ûJH¬à€€ú›€X[î]Y\ûHH€€[X[ô[]Sõ‹õX[\ŸJ]Y\ûJN¬à€€ú›Y]HH””SPSë‘SUW““Së”QUVŸ[ùûKö⁄[ôH””SPSë‘SUW““Së”QUKòX›[€é¬àYà
X€X[î]Y\ûJHô]\õà[ùûKôôX]\ôY»L
»Y]Kúö[‹ö]HàLN¬à€€ú›]HH€€[X[ô[]Sõ‹õX[\ŸJ[ùûKù]JN¬à€€ú›]Z[H€€[X[ô[]Sõ‹õX[\ŸJ[ùûKô]Z[
N¬à€€ú›ŸX\ò⁄H[ùûKúŸX\ò⁄^	›]_H	Ÿ]Z[X¬à€€ú›⁄Ÿ[ú»H€X[î]Y\ûKú‹]
	»	 Kôö[\äõ€€X[äN¬àYà
]⁄Ÿ[úÀô]ô\ûJ⁄Ÿ[àOàŸX\ò⁄ö[ò€Y\ ⁄Ÿ[äJJHô]\õàLN¬à]ÿ€‹ôHHY]Kúö[‹ö]H
à¬àYà
]HOOH€X[î]Y\ûJHÿ€‹ôH
œHL¬à[ŸHYà
]Kú›\ù’⁄]
€X[î]Y\ûJJHÿ€‹ôH
œHÕå¬à[ŸHYà
]Kö[ò€Y\ €X[î]Y\ûJJHÿ€‹ôH
œHMå¬à[ŸHYà
ŸX\ò⁄ö[ò€Y\ €X[î]Y\ûJJHÿ€‹ôH
œHÕå¬àõ‹à
€€ú›⁄Ÿ[àŸà⁄Ÿ[ú H¬àYà
]Kú‹]
	»	 Kú€€YJ€‹ôOà€‹ôú›\ù’⁄]
⁄Ÿ[äJJHÿ€‹ôH
œH¬à[ŸHYà
]Z[ö[ò€Y\ ⁄Ÿ[äJHÿ€‹ôH
œHé¬à[ŸHÿ€‹ôH
œHLé¬àBàYà
[ùûKôôX]\ôY
Hÿ€‹ôH
œHN¬àô]\õàÿ€‹ôN¬àBÇàù[ò›[€à€€[X[ô[]TŸX\ò⁄
]Y\ûHH	… H¬àô]\õà€€[X[ô[]Q[ùöY\¬àõX\
[ùûHOà
»[ùûKÿ€‹ôNà€€[X[ô[]Q[ùûTÿ€‹ôJ[ùûK]Y\ûJHJJBàôö[\äô\›[Oàô\›[úÿ€‹ôHèH
Bàú€‹ù

YùöY⁄
HOàöY⁄úÿ€‹ôHHYùúÿ€‹ôHYùô[ùûKù]Kõÿÿ[P€€\\ôJöY⁄ô[ùûKù]JJBàú€XŸJ””SPSë‘SUW‘ëT’S”SRU
BàõX\
ô\›[Oàô\›[ô[ùûJN¬àBÇàù[ò›[€à€€[X[ô[]U\]TŸ[X›[€ä›ô\õ^HH€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô[]RY
Kô^[ô^H€€[X[ô[]TŸ[X›Y[ô^
H¬àYà
[›ô\õ^HX€€[X[ô[]Tô\›[Àõ[ô›
Hô]\õàò[ŸN¬à€€[X[ô[]TŸ[X›Y[ô^H
ù[Xô\äô^[ô^
H	H€€[X[ô[]Tô\›[Àõ[ô›
»€€[X[ô[]Tô\›[Àõ[ô›
H	H€€[X[ô[]Tô\›[Àõ[ô›¬à€€ú›‹[€ú»H\úò^Kôúõ€J›ô\õ^Kú]Y\ûTŸ[X›‹ê[
	÷Ÿ]KX€€[X[ô\[]K\ô\›[I JN¬à‹[€úÀôõ‹ëXX⁄

‹[€ã[ô^
HOà‹[€ãúŸ]]öXù]J	ÿ\öXK\Ÿ[X›Y	À›ö[ô [ô^OOH€€[X[ô[]TŸ[X›Y[ô^
JJN¬à€€ú›X›]ôHH‹[€ú÷ÿ€€[X[ô[]TŸ[X›Y[ô^N¬à€€ú›[ú]H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\[]KZ[ú]I N¬àYà
X›]ôOÀöY
H[ú]ÀúŸ]]öXù]J	ÿ\öXKXX›]ôY\ÿŸ[ô[ù	ÀX›]ôKöY
N¬àûH»X›]ôOÀúÿ‹õ€[ù’öY]œÀä»õÿ⁄Œà	€ôX\ô\›	»JN»Hÿ]⁄
\úäHﬂBàô]\õàùYN¬àBÇàù[ò›[€àô[ô\ê€€[X[ô[]J]Y\ûHH	…À›ô\õ^HH€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô[]RY
JH¬àYà
[›ô\õ^JHô]\õà¬à€€[X[ô[]Tô\›[»H€€[X[ô[]TŸX\ò⁄
]Y\ûJN¬à€€[X[ô[]TŸ[X›Y[ô^HX]õZ[ä€€[X[ô[]TŸ[X›Y[ô^X]õX^
€€[X[ô[]Tô\›[Àõ[ô›HJJN¬à€€ú›ô\›[»H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\[]K\ô\›[◊I N¬à€€ú››]\»H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\[]K\›]\◊I N¬à€€ú›[H€€[X[ô[]Tô\›[Àõ[ô›»€€[X[ô[]Tô\›[ÀõX\

[ùûK[ô^
HOà¬à€€ú›Y]HH””SPSë‘SUW““Së”QUVŸ[ùûKö⁄[ôH””SPSë‘SUW““Së”QUKòX›[€é¬àô]\õàù]€àYHõX€\ÀX€€[X[ô\[]K[‹[€ãI⁄[ô^Hà€\‹œHõX€\ÀX€€[X[ô\[]K\ô\›[à\OHòù]€ààõ€OHõ‹[€àà]KX€€[X[ô\[]K\ô\›[Hâ⁄[ô^Hà\öXK\Ÿ[X›YHâ⁄[ô^OOH€€[X[ô[]TŸ[X›Y[ô^Hèè‹[à€\‹œHõX€\ÀX€€[X[ô\[]KZ⁄[ôZX€€àà\öXKZY[èHùùYHèâ€Y]KöX€€üO‹‹[èè‹[à€\‹œHõX€\ÀX€€[X[ô\[]KX€‹Hèè›õ€ôœâŸ\ÿÿ\R[
[ùûKù]J_O‹›õ€ôœè€X[âŸ\ÿÿ\R[
[ùûKô]Z[Y]KõXô[
_O‹€X[è‹‹[èè‹[à€\‹œHõX€\ÀX€€[X[ô\[]KZ⁄[ôèâ€Y]KõXô[O‹‹[èèÿù]€èò¬àJKöõ⁄[ä	… Hà]à€\‹œHõX€\ÀX€€[X[ô\[]KY[\Hèè›õ€ôœìõ»X]⁄[ô»€€[X[ô‹›õ€ôœè‹[èïûHHZ\‹⁄[€àò[YKôZX€KùZ[[ôÀXŸKŸ][ô»‹àH⁄‹ù\à€€[X[ôò\ŸKè‹‹[èèŸ]èò¬àŸ][õô\í[Yê⁄[ôŸY
ô\›[À[	‹]Y\û_Nâÿ€€[X[ô[]Tô\›[ÀõX\
[ùûHOà[ùûKöY
Köõ⁄[ä	ﬂ	 _X
N¬àYà
›]\ H›]\Àù^€€ù[ùH€€[X[ô[]Tô\›[Àõ[ô›à»	ÿ€€[X[ô[]Tô\›[Àõ[ô›Hô\›[	ÿ€€[X[ô[]Tô\›[Àõ[ô›OOHH»	…»à	‹…ﬂH0≠»	‹]Y\ûH»	‹ò[öŸYÿÿ[I»à	‹]ZX⁄»XÿŸ\‹…ﬂXàà	”õ»ô\›[…Œ¬à€€[X[ô[]U\]TŸ[X›[€ä›ô\õ^JN¬àô]\õà€€[X[ô[]Tô\›[Àõ[ô›¬àBÇàù[ò›[€à^X›]P€€[X[ô[]Tô\›[
[ô^H€€[X[ô[]TŸ[X›Y[ô^
H¬à€€ú›[ùûHH€€[X[ô[]Tô\›[÷”ù[Xô\ä[ô^
WN¬àYà
Y[ùûJHô]\õàò[ŸN¬à€‹ŸP€€[X[ô[]J»ô\›‹ôQõÿ›\Œàò[ŸHJN¬àûH¬à[ùûKô^X›]J
N¬àô]\õàùYN¬àHÿ]⁄
\úäH¬à⁄›’ÿ\›
	–€€[X[ô€›[õ›ôH€€\]Y	 N¬àô]\õàò[ŸN¬àBàBÇàù[ò›[€à€€[X[ô[]Uò\õÿ›\ ]ô[ù›ô\õ^JH¬àYà
]ô[ùöŸ^HOOH	’Xâ Hô]\õàò[ŸN¬à€€ú›õÿ›\ÿXõHH\úò^Kôúõ€J›ô\õ^Kú]Y\ûTŸ[X›‹ê[
	ÿù]€éõõ›
Ÿ\ÿXõYJK[ú]õõ›
Ÿ\ÿXõYJK›Xö[ô^Nõõ›
›Xö[ô^HãLHóJI JKôö[\ä\’ö\⁄XõJN¬àYà
Yõÿ›\ÿXõKõ[ô›
Hô]\õàò[ŸN¬à€€ú››\úô[ùHõÿ›\ÿXõKö[ô^Ÿäÿ›[Y[ùòX›]ôQ[[Y[ù
N¬à€€ú›ô^H]ô[ùú⁄YùŸ^H»
›\úô[ùH»õÿ›\ÿXõKõ[ô›HHà›\úô[ùHJHà
›\úô[ù›\úô[ùèHõÿ›\ÿXõKõ[ô›HH»à›\úô[ù
»JN¬à]ô[ùúô]ô[ùYò][

N¬àõÿ›\ÿXõV€ô^Kôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJN¬àô]\õàùYN¬àBÇàù[ò›[€à‹ôX]P€€[X[ô[]J
H¬à€€ú›^\›[ô»H€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô[]RY
N¬àYà
^\›[ô Hô]\õà^\›[ôŒ¬à€€ú››ô\õ^HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à›ô\õ^KöYH–‘íTò€€[X[ô[]RY¬à›ô\õ^KúŸ]]öXù]J	‹õ€IÀ	ŸX[Ÿ… N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXK[[Ÿ[	À	›ùYI N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXK[Xô[YûIÀ	€X€\ÀX€€[X[ô\[]K]]I N¬àŸ][õô\í[Yê⁄[ôŸY
›ô\õ^KàŸX›[€à€\‹œHõX€\ÀX€€[X[ô\[]K]⁄[ô›»èÇàXY\à€\‹œHõX€\ÀX€€[X[ô\[]KZXYèÇà]à€\‹œHõX€\ÀX€€[X[ô\[]KXúò[ôèè]à€\‹œHõX€\ÀX€€[X[ô\[]K]]Hèè‹[èë”–êS””SPSë—PTê“‹‹[èè›õ€ô»YHõX€\ÀX€€[X[ô\[]K]]Hèï€€⁄]€€[X[ô[]O‹›õ€ôœèŸ]èèù]€à€\‹œHõX€\ÀX€€[X[ô\[]KX€‹ŸHà\OHòù]€àà]KX€€[X[ô\[]KX€‹ŸH\öXK[Xô[Hê€‹ŸH€€[X[ô[]Hè∞Âœÿù]€èèŸ]èÇàXô[€\‹œHõX€\ÀX€€[X[ô\[]K\ŸX\ò⁄èè‹[à\öXKZY[èHùùYHè∏£%O‹‹[èè[ú]\OHúŸX\ò⁄à[ú][ŸOHúŸX\ò⁄à]]ÿ€€\]OHõŸôàà]]ÿÿ\][^ôOHõõ€ôHà‹[⁄X⁄œHôò[ŸHà]KX€€[X[ô\[]KZ[ú]õ€OHò€€Xõÿõﬁà\öXKX]]ÿ€€\]OHõ\›à\öXKX€€ùõ€œHõX€\ÀX€€[X[ô\[]K\ô\›[»à\öXKY^[ôYHùùYHàXŸZ€\èHîŸX\ò⁄Z\‹⁄[€úÀôZX€\ÀùZ[[ô‹Àÿÿ][€úÀŸ][ô‹»‹à€€[X[ô»èèÿôíœ⁄ÿôè€Xô[Çà⁄XY\èÇà]àYHõX€\ÀX€€[X[ô\[]K\ô\›[»à€\‹œHõX€\ÀX€€[X[ô\[]K\ô\›[»à]KX€€[X[ô\[]K\ô\›[»õ€OHõ\›õﬁà\öXK[Xô[Hê€€[X[ô[]Hô\›[»èèŸ]èÇàõ€›\à€\‹œHõX€\ÀX€€[X[ô\[]KYõ€›èè‹[è∏°§x°§»Ÿ[X›0≠»[ù\àù[à0≠»\ÿ»€‹ŸO‹‹[èè‹[à]KX€€[X[ô\[]K\›]\»\öXK[]ôOHú€]Hèè‹‹[èèŸõ€›\èÇà‹ŸX›[€èÇà
N¬àù[ù[YS\›[ä›ô\õ^K	⁄[ú]	À]ô[ùOà¬àYà
Y]ô[ùù\ôŸ]ÀõX]⁄\œÀä	÷Ÿ]KX€€[X[ô\[]KZ[ú]I JHô]\õé¬à€€[X[ô[]TŸ[X›Y[ô^H¬àô[ô\ê€€[X[ô[]J]ô[ùù\ôŸ]ùò[YK›ô\õ^JN¬àJN¬àù[ù[YS\›[ä›ô\õ^K	ÿ€X⁄…À]ô[ùOà¬àYà
]ô[ùù\ôŸ]OOH›ô\õ^H€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]KX€€[X[ô\[]KX€‹ŸWI JH»€‹ŸP€€[X[ô[]J»ô\›‹ôQõÿ›\ŒàùYHJN»ô]\õé»Bà€€ú›ô\›[H€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]KX€€[X[ô\[]K\ô\›[I N¬àYà
ô\›[
H^X›]P€€[X[ô[]Tô\›[
ù[Xô\äô\›[ô]\Ÿ]ò€€[X[ô[]Tô\›[
JN¬àJN¬àù[ù[YS\›[ä›ô\õ^K	⁄Ÿ^Y›€âÀ]ô[ùOà¬àYà
]ô[ùöŸ^HOOH	—\ÿÿ\I H»]ô[ùúô]ô[ùYò][

N»]ô[ùú›‹õ‹Yÿ][€ä
N»€‹ŸP€€[X[ô[]J»ô\›‹ôQõÿ›\ŒàùYHJN»ô]\õé»BàYà
]ô[ùöŸ^HOOH	–\úõ›—›€â H»]ô[ùúô]ô[ùYò][

N»€€[X[ô[]U\]TŸ[X›[€ä›ô\õ^K€€[X[ô[]TŸ[X›Y[ô^
»JN»ô]\õé»BàYà
]ô[ùöŸ^HOOH	–\úõ›’\	 H»]ô[ùúô]ô[ùYò][

N»€€[X[ô[]U\]TŸ[X›[€ä›ô\õ^K€€[X[ô[]TŸ[X›Y[ô^HJN»ô]\õé»BàYà
]ô[ùöŸ^HOOH	“€YI H»]ô[ùúô]ô[ùYò][

N»€€[X[ô[]U\]TŸ[X›[€ä›ô\õ^K
N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—[ô	 H»]ô[ùúô]ô[ùYò][

N»€€[X[ô[]U\]TŸ[X›[€ä›ô\õ^K€€[X[ô[]Tô\›[Àõ[ô›HJN»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—[ù\â H»]ô[ùúô]ô[ùYò][

N»^X›]P€€[X[ô[]Tô\›[

N»ô]\õé»Bà€€[X[ô[]Uò\õÿ›\ ]ô[ù›ô\õ^JN¬àJN¬àÿ›[Y[ùòõŸKò\[ô⁄[
›ô\õ^JN¬àô]\õà›ô\õ^N¬àBÇàù[ò›[€à‹[ê€€[X[ô[]J»ô]\õëõÿ›\»Hù[[ö]X[]Y\ûHH	…»HHﬂJH¬àYà
]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JHô]\õàù[¬àYà
›]KúÿYôS[ŸKô[òXõY
H»⁄›’ÿ\›
	–€€[X[ô[]H\»›\‹[ôY[à€€⁄]ÿYôH[ŸI N»ô]\õàù[»Bà€€ú›^\›[ô»H€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô[]RY
N¬àYà
^\›[ô H¬à^\›[ôÀú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\[]KZ[ú]I OÀôõÿ›\œÀä»ô]ô[ùÿ‹õ€àùYHJN¬àô]\õà^\›[ôŒ¬àBà€€⁄][ò[]X‹‘ôX€‹ôôX]\ôJ	ÿ€€[X[ô[]I N¬à€€[X[ô[]Tô]\õëõÿ›\»Hô]\õëõÿ›\»[ú›[òŸ[ŸàS[[Y[ù»ô]\õëõÿ›\»àÿ›[Y[ùòX›]ôQ[[Y[ù[ú›[òŸ[ŸàS[[Y[ù»ÿ›[Y[ùòX›]ôQ[[Y[ùàù[¬à€‹ŸUXõ]]ZX⁄’⁄Y[
»ô\›‹ôQõÿ›\Œàò[ŸHJN¬à€‹ŸP€€[X[ô^\öY[òŸS[Ÿ[
»ô\›‹ôQõÿ›\Œàò[ŸHJN¬à€‹ŸR[Ÿ[ù\ä»ô\›‹ôQõÿ›\Œàò[ŸHJN¬à€‹ŸT[ô[

N¬à€€[X[ô[]Q[ùöY\»HùZ[€€[X[ô[]Q[ùöY\ 
N¬à€€[X[ô[]Tô\›[»H◊N¬à€€[X[ô[]TŸ[X›Y[ô^H¬à€€ú››ô\õ^HH‹ôX]P€€[X[ô[]J
N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùúŸ]]öXù]J	Ÿ]K[X€\ÀX€€[X[ô\[]K[‹[âÀ	›ùYI N¬à€€ú›[ú]H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\[]KZ[ú]I N¬àYà
[ú]
H[ú]ùò[YHH›ö[ô [ö]X[]Y\ûH	… N¬àô[ô\ê€€[X[ô[]J›ö[ô [ö]X[]Y\ûH	… K›ô\õ^JN¬à\]URJ
N¬à[ú]Àôõÿ›\œÀä»ô]ô[ùÿ‹õ€àùYHJN¬àô]\õà›ô\õ^N¬àBÇàù[ò›[€à€‹ŸP€€[X[ô[]J»ô\›‹ôQõÿ›\»HùYHHHﬂJH¬à€€ú››ô\õ^HH€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô[]RY
N¬àYà
[›ô\õ^JH»ù[ù[YTù[ôQ\ÿ€€õôX›Y\›[ô\ú 
N»ô]\õàò[ŸN»Bàù[ù[YU[õ\›[ï\ôŸ]
›ô\õ^KùYJN¬à›ô\õ^Kúô[[›ôJ
N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùúô[[›ôP]öXù]J	Ÿ]K[X€\ÀX€€[X[ô\[]K[‹[â N¬à€€[X[ô[]Q[ùöY\»H◊N¬à€€[X[ô[]Tô\›[»H◊N¬à€€[X[ô[]TŸ[X›Y[ô^H¬àYà
ô\›‹ôQõÿ›\»	âà€€[X[ô[]Tô]\õëõÿ›\œÀö\–€€õôX›Y
H¬àûH»€€[X[ô[]Tô]\õëõÿ›\Àôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJN»Hÿ]⁄
\úäHﬂBàBà€€[X[ô[]Tô]\õëõÿ›\»Hù[¬à\]URJ
N¬àô]\õàùYN¬àBÇàù[ò›[€à€‹ŸR[Ÿ[ù\ä»ô\›‹ôQõÿ›\»HùYHHHﬂJH¬à€€ú››ô\õ^HHÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTö[Ÿ[ù\íY
N¬àYà
[›ô\õ^OÀò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â JHô]\õàò[ŸN¬à›ô\õ^Kò€\‹”\›úô[[›ôJ	€X€\À[‹[âÀ	€X€\À[ÿY[ô…À	€X€\ÀY\úõ‹â N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXKZY[âÀ	›ùYI N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùúô[[›ôP]öXù]J	Ÿ]K[X€\ÀZ[[‹[â N¬àYà
ô\›‹ôQõÿ›\»	âà[Ÿ[ù\îô]\õëõÿ›\œÀö\–€€õôX›Y
H¬àù[ù[YTŸ][Y[›]


HOà»ûH»[Ÿ[ù\îô]\õëõÿ›\Àôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJN»Hÿ]⁄
\úäHﬂHK
N¬àBà[Ÿ[ù\îô]\õëõÿ›\»Hù[¬àô]\õàùYN¬àBÇàù[ò›[€à[›ZYTô\]Y\›\õ
õ‹òŸHHò[ŸJH¬à€€ú›Ÿ\\ò]‹àHS–—SïTãúò]’\õö[ò€Y\ 	œ… H»	…â»à	œ…Œ¬à€€ú›ÿX⁄RŸ^HHõ‹òŸH»	‘–‘íTùô\ú⁄[€üKI—]Kõõ› 
_Xà–‘íTùô\ú⁄[€é¬àô]\õà	“S–—SïTãúò]’\õI‹Ÿ\\ò]‹ü]€€⁄]IŸ[ò€ŸUTíP€€\€ô[ù
ÿX⁄RŸ^J_X¬àBÇàù[ò›[€àô\]Y\›[›ZYQÿ›[Y[ù
õ‹òŸHHò[ŸJH¬àYà
Yõ‹òŸH	âà[›ZYQÿ›[Y[ùÿX⁄JHô]\õàõ€Z\ŸKúô\€€ôJ[›ZYQÿ›[Y[ùÿX⁄JN¬àYà
[›ZYSÿYõ€Z\ŸJHô]\õà[›ZYSÿYõ€Z\ŸN¬à€€ú›\õH[›ZYTô\]Y\›\õ
õ‹òŸJN¬à[›ZYSÿYõ€Z\ŸHHô]»õ€Z\ŸJ
ô\€€ôKôZôX›
HOà¬àYà
ù[ù[YKô\›õﬁYY
H¬àôZôX›
ô]»\úõ‹ä	’€€⁄]ù[ù[YH›‹Yâ JN¬àô]\õé¬àBà€€ú›ò[Y]HH^Oà¬à€€ú›ÿ›[Y[ù^H›ö[ô ^	… Kùö[J
N¬àYà
KœYÿ›\H[[◊œóK⁄]Kù\›
ÿ›[Y[ù^
HYÿ›[Y[ù^ö[ò€Y\ 	”Z\‹⁄[€ê⁄YYàX\€€[X[ô€€⁄]	 JH¬àõ›»ô]»\úõ‹ä	’H[Ÿ[ùôHô]\õôY[à[ùò[Yÿ›[Y[ùâ N¬àBà[›ZYQÿ›[Y[ùÿX⁄HHÿ›[Y[ù^¬à[›ZYSÿYY]H]Kõõ› 
N¬àô]\õàÿ›[Y[ù^¬àN¬àYà
\[Ÿà”Wﬁ[ô\]Y\›OOH	Ÿù[ò›[€â H¬à]ô\]Y\›Hù[¬à]Ÿ]YHò[ŸN¬à€€ú›ö[ö\⁄H
\úõ‹ãô\‹€úŸHHù[
HOà¬àYà
Ÿ]Y
Hô]\õé¬àŸ]YHùYN¬àYà
ô\]Y\›
Hù[ù[YKúô\]Y\›Àô[]Jô\]Y\›
N¬àûH¬àYà
\úõ‹äHõ›»\úõ‹é¬àYà
\ô\‹€úŸHù[Xô\äô\‹€úŸKú›]\ Håù[Xô\äô\‹€úŸKú›]\ HèHÃ
Hõ›»ô]»\úõ‹ä[Ÿ[ùôHô]\õôY	‹ô\‹€úŸOÀú›]\»	Ÿ\úõ‹âﬂKò
N¬àô\€€ôJò[Y]Jô\‹€úŸKúô\‹€úŸU^
JN¬àHÿ]⁄
\úäH¬àôZôX›
\úà[ú›[òŸ[Ÿà\úõ‹à»\úààô]»\úõ‹ä	’H[Ÿ[ùôH€›[õ›ôHÿYYâ JN¬àBàN¬àûH¬àô\]Y\›H”Wﬁ[ô\]Y\›
¬àY]Ÿà	——U	À\õ[Y[›]àS–—SïTãúô\]Y\›[Y[›]\Àô\‹€úŸU\Nà	›^	ÀàXY\úŒà»XÿŸ\à	›^⁄[^‹Z[é‹OLéK
ã é‹OLé	»Kà€õÿYàô\‹€úŸHOàö[ö\⁄
ù[ô\‹€úŸJKà€ô\úõ‹éà

HOàö[ö\⁄
ô]»\úõ‹ä	—⁄]Xà€›[õ›ôHôXX⁄Yâ JKà€ù[Y[›]à

HOàö[ö\⁄
ô]»\úõ‹ä	’H[Ÿ[ùôHô\]Y\›[YY›]â JKà€òXõ‹ùà

HOàö[ö\⁄
ô]»\úõ‹ä	’H[Ÿ[ùôHô\]Y\›ÿ\»ÿ[òŸ[Yâ JBàJN¬àYà
\Ÿ]Y	âàô\]Y\›ÀòXõ‹ù
Hù[ù[YKúô\]Y\›ÀòY
ô\]Y\›
N¬àHÿ]⁄
\úäH¬àö[ö\⁄
\úà[ú›[òŸ[Ÿà\úõ‹à»\úààô]»\úõ‹ä	’H[Ÿ[ùôHô\]Y\›€›[õ›ôH‹ôX]Yâ JN¬àBàô]\õé¬àBàù[ù[YQô]⁄
\õ»ÿX⁄Nàõ‹òŸH»	‹ô[ÿY	»à	ŸYò][	À‹ôY[ùX[Œà	€€Z]	»JBàù[äô\‹€úŸHOà¬àYà
\ô\‹€úŸKõ⁄ Hõ›»ô]»\úõ‹ä[Ÿ[ùôHô]\õôY	‹ô\‹€úŸKú›]\ﬂKò
N¬àô]\õàô\‹€úŸKù^

N¬àJBàù[ä^Oàô\€€ôJò[Y]J^
JJBàòÿ]⁄
\úõ‹àOàôZôX›
\úõ‹à[ú›[òŸ[Ÿà\úõ‹à»\úõ‹ààô]»\úõ‹ä	—⁄]Xà€›[õ›ôHôXX⁄Yâ JJN¬àJKôö[ò[J

HOà»[›ZYSÿYõ€Z\ŸHHù[»JN¬àô]\õà[›ZYSÿYõ€Z\ŸN¬àBÇàù[ò›[€à]⁄[›ZYQÿ›[Y[ù
ÿ›[Y[ù^
H¬à]€›\òŸHH›ö[ô ÿ›[Y[ù^	… N¬à€›\òŸHH€›\òŸBàúô\XŸJ—›ZYHõ‹à€€⁄]ó
◊ó
◊ó
À›K›ZYHõ‹à€€⁄]â“S–—SïTãô›ZYUô\ú⁄[€üX
Bàúô\XŸJ“[Ÿ[ùôHõ‹àó
◊ó
◊ó
À›K[Ÿ[ùôHõ‹àâ“S–—SïTãô›ZYUô\ú⁄[€üX
Bàúô\XŸJà	œ]à€\‹œHòÿ\ôèèœï[Xúô[O⁄œèî›\ö[Hö[⁄^ò\ô€€[X[ô›[[ô»⁄]€\‹⁄YöYY€€ùZ[õY[ù[ô[Àè‹èŸ]èâÀà	œ]à€\‹œHòÿ\ôèèœï[Xúô[H€€ùZ[õY[ù⁄œèê€‹ú‹ò]Hî”M€€[X[ô›[[ô»⁄]‹öY⁄[ò[ò[ú‹\ô[ù[Xõ[KòX⁄[]Hÿ⁄[X]XÀ›\ùôZ[[òŸH\õZ[ò[‹X⁄[Y[àöX[[ô€€ùZ[õY[ùY]ö\⁄[€à\ù€‹öÀè‹èŸ]èâ¬à
Bàúô\XŸJ	–ö[⁄^ò\ô€€ùZ[õY[ù‹‹[èâÀ	’[Xúô[H€€ùZ[õY[ù‹‹[èâ Bàúô\XŸJà	‘Ÿ]HZ[ö[][H^[›]ô\⁄€\ò][€ã[YK]Y[»›]H[ôõ€[YKà\ŸHH\›[[›[ù€€ùõ€ôYõ‹ôHô[Z[ô»€àHô]»Ÿ]\âÀà	‘Ÿ]HZ[ö[][H^[›]ô\⁄€\ò][€ã[YK]Y[»›]H[ôõ€[YKà[Xúô[H€€ùZ[õY[ù\Ÿ\»Hÿ[YHY[ù]K\ù€‹ö»X⁄ÿYŸH[ôô[ò[YY‹›Y]Y[»\»H[Xúô[HRH[YKà\ŸHH\›[[›[ù€€ùõ€ôYõ‹ôHô[Z[ô»€àHô]»Ÿ]\â¬à
Bàúô\XŸJà	œOîô\Ÿ[ù][€à]\»[ô\ùX€HôX]Y[ùÿÿ[HûH^[›]Y\ãè€OâÀà	œOîô\Ÿ[ù][€à]\»[ô\ùX€HôX]Y[ùÿÿ[HûH^[›]Y\ãè€OèOï[Xúô[H€€ùZ[õY[ù\‹^\»î”MòX⁄[]K›\ùôZ[[òŸK€‹ú‹ò]H[Xõ[H[ôò[úŸô\ãX]]‹ö\ÿ][€à\ù€‹öÀè€Oâ¬à
N¬à€€ú›Ÿ[X[ùX”X\öŸ\àH	œ]à€\‹œHòÿ[›]ÿ\õö[ô»èè›õ€ôœîõ›X›YŸ[X[ùX»€€›\úŒè‹›õ€ôœà€X\ö[ôÀ\‹⁄\›[òŸKÿ\õö[ôÀ‹ö]Xÿ[[ôﬁ[ò⁄[ô»›]\»ô]Z[àZ\à‹\ò][€ò[YX[ö[ô»X‹õ‹‹»]ô\ûH[YKèŸ]èâŒ¬àYà
\€›\òŸKö[ò€Y\ 	’[Xúô[H€€ùZ[õY[ù\‹Ÿ]X⁄ÿYŸNâ H	âà€›\òŸKö[ò€Y\ Ÿ[X[ùX”X\öŸ\äJH¬à€›\òŸHH€›\òŸKúô\XŸJàŸ[X[ùX”X\öŸ\ãà	œ]à€\‹œHòÿ[›]èè›õ€ôœï[Xúô[H€€ùZ[õY[ù\‹Ÿ]X⁄ÿYŸNè‹›õ€ôœàX€‹ò]]ôH\ù€‹ö»\»ÿYYúõ€HHXõX»€€⁄]\‹Ÿ]»ô\‹⁄]‹ûH€õH⁄[HH[YH\»[à\ŸKàZ\‹⁄[ô»\ù€‹ö»ô]ô\àõÿ⁄‹»H€€⁄][ôH‹ò\X‹»»õ›ô\XŸHõ›X›Y‹\ò][€ò[€€›\úÀèŸ]èâ»
»Ÿ[X[ùX”X\öŸ\Çà
N¬àBàYà
\€›\òŸKö[ò€Y\ 	⁄YHôö[ò[ò⁄X[X€€[X[ôâ JH¬à€€ú›ö[ò[ò⁄X[ŸX›[€àHŸX›[€à€\‹œHúŸX›[€ààYHôö[ò[ò⁄X[X€€[X[ôà]K]]OHë\ÿ€‹ôö[ò[ò⁄X[€€[X[ôà]KZŸ^]€‹ôœHô\ÿ€‹ôö[ò[òŸH\ò⁄]ôHYŸ\à]Y]⁄]Xàù[\»€XﬁHY\ÿÿ[àõ‹ôXÿ\›ö\⁄»ÿ\][[ùô\›Y[ùŸXö€⁄»èÇè]à€\‹œHöXYèè‹[à€\‹œHõù[HèåNO‹‹[èè]èèèë\ÿ€‹ôö[ò[ò⁄X[€€[X[ô⁄èè€\‹œHú›[[X\ûHèìZ\‹⁄[€ê⁄YYàYŸ\à^òX›[€ãZ[Hÿ‹ôY]À€›ô\ùöY]ÿôX€€ò⁄[X][€ãÿÿ[\›‹öXÿ[\ò⁄]ö[ô»[ô⁄]XãZ‹›Yö[ò[ò⁄X[[ù[YŸ[òŸKè‹èŸ]èèŸ]èÇèœë\ÿ€‹ôö[ò[òŸHô\‹ùœ⁄œèê⁄€‹ŸH⁄[\Hõ‹àŸ^Hù[Xô\ú»[û[€ôHÿ[à[ô\ú›[ô[ôõ‹õX]]ôHõ‹à\ŸYù[€€ù^[ô€€\\ö\€€úÀ‹àH€€àõ‹àH€€\]Hö[ò[ò⁄X[[ù[YŸ[òŸH]Y]à]ô\ûH]ô[ŸY\»[ò€€YK‹[ô[ôÀô]⁄[ôŸH[ôò[[òŸ\»ö\ú›à‹\ò][ô»€‹›»ô[XZ[àŸ\\ò]Húõ€H[ùô\›Y[ù[ô^[ú⁄[€à€»X[HX›]ö]H\»õ›XYH»€⁄»[úõŸö]XõKè‹Çè]à€\‹œHô‹öYèè]à€\‹œHòÿ\ôèèëö[ò[ò⁄X[ÿ€‹ôXÿ\ô⁄èîô]ô[ùYK‹\ò][ô»YôöX⁄Y[òﬁK\]ZY]K‹õ››[ùô\›Y[ù[ô]Y]€€ôöY[òŸH\ôHÿ€‹ôY[ô\[ô[ùKè‹èŸ]èè]à€\‹œHòÿ\ôèèëZ[HYŸ‹ôYÿ]H]Y]⁄èìZ\‹⁄[€ê⁄YYàô]ô[ùYK‹[ô[ô‹»[ô›[Hõ›‹»ô\öYûH€€\]H^\»⁄]›]›XõKX€›[ù[ô»H]Z[YYŸ\ãà[ûH[úô\€€ôYò\öX[òŸHô[XZ[ú»ö\⁄XõKè‹èŸ]èè]à€\‹œHòÿ\ôèèîö\⁄»[ù[YŸ[òŸO⁄èíY⁄Y⁄»›ô\ùöY]»ò\öX[òŸKô]ô[ùYH€€ùòX›[€ã€€òŸ[ùò][€ãYŸ‹ô\‹⁄]ôH[ùô\›Y[ùô\Ÿ\ùôHò]Ÿ›€ã›»ù[ùÿ^H[ô[ò€€\]H€\‹⁄YöXÿ][€ãè‹èŸ]èè]à€\‹œHòÿ\ôèèëY\YŸ\àÿÿ[è⁄èê[]òZ[XõH\›‹ûHôXY»]ô\ûHZ\‹⁄[€ê⁄YYà‹ôY][YŸ\àYŸHXÿŸ\‹⁄XõH»HXÿ€›[ù⁄]ô]öY\ÀõŸ‹ô\‹»ô\‹ù[ôÀÿYôHÿ[òŸ[][€à[ôÿÿ[⁄X⁄‹⁄[ù›‹òYŸKè‹èŸ]èè]à€\‹œHòÿ\ôèèë⁄]Xà[ù[YŸ[òŸO⁄èê€\‹⁄YöXÿ][€àù[\»[ô]Y]ô\⁄€»\ôH›€õÿYYúõ€HHXõX»€€⁄]\‹Ÿ]»ô\‹⁄]‹ûH[ôÿX⁄Yÿÿ[Kàõ»^Y\àYŸ\à‹àŸXö€⁄»]H\»\ÿYYè‹èŸ]èèŸ]èÇèœî^Y\ã[[öŸYÿÿ[ö[ò[ò⁄X[\ò⁄]ôO⁄œè€€\‹œHú›\»èèOíŸY\ÿÿ[ö[ò[ò⁄X[\ò⁄]ôH[òXõY»ô]Z[à\ÿ€›ô\ôYò[úÿX›[€ú»ûHZ\‹⁄[€ê⁄YYà^Y\àQ€ò[YKè€OèOîŸ[X›[]òZ[XõH\›‹ûH‹àù[àY\ÿÿ[à[]òZ[XõH»^[ôH\ò⁄]ôH\»ò\àòX⁄»\»Z\‹⁄[€ê⁄YYà^‹Ÿ\Àè€OèOï\ŸH^‹ù\ò⁄]ôH[ô[\‹ù\ò⁄]ôH»ò[úŸô\à‹àY\ôŸH\›‹ûHô]ŸY[à[›\à]öXŸ\»⁄]›]^‹⁄[ô»ô\‹⁄]‹ûH‹ôY[ùX[Àè€OèOë^‹ù[[€»[ò€Y\»Hÿÿ[\ò⁄]ôH[ô\ÿ€‹ôŸXö€⁄»õ‹à€€\]Hö]ò]HôX€›ô\ûKè€OèOë⁄]Xà‹›»€õHXõX»ù[\À]Y]€XﬁH[ô€€⁄]\‹Ÿ]Œ»^Y\àö[ò[ò⁄X[]Hô[XZ[ú»[àHúõ›‹Ÿ\à[ôö]ò]HòX⁄›\Àè€Oè€€Çè]à€\‹œHòÿ[ÿ\õàèè›õ€ôœîö]ò]HòX⁄›\è‹›õ€ôœà^‹ù[[ò€Y\»Hÿ]ôY\ÿ€‹ôŸXö€⁄»[ôÿÿ[ö[ò[ò⁄X[\›‹ûKà›‹ôHHî””àö]ò][N»[û[€ôH€[ô»]X^HôHXõH»‹›õ›Y⁄HŸXö€⁄»[ô[ú‹X›H^‹ùYÿ[YHYŸ\ãèŸ]èÇè‹ŸX›[€èò¬à€›\òŸHH€›\òŸKúô\XŸJ	œ€XZ[èâÀ	Ÿö[ò[ò⁄X[ŸX›[€üO€XZ[èò
N¬àBàYà
\€›\òŸKö[ò€Y\ 	⁄YHôX€€õ€^K[[ŸHâ JH¬à€€ú›X€€õ€^TŸX›[€àHŸX›[€à€\‹œHúŸX›[€ààYHôX€€õ€^K[[ŸHà]K]]OHëX€€õ€^H[ŸHà]KZŸ^]€‹ôœHôX€€õ€^HX€»\ôõ‹õX[òŸH›»[ô\‹ò[H‹H‹HY»XYõ]X\öŸ\ú»èÇè]à€\‹œHöXYèè‹[à€\‹œHõù[Hèåå‹‹[èè]èèèëX€€õ€^H[ŸO⁄èè€\‹œHú›[[X\ûHèêHô]ô\ú⁄XõH›Ÿ\ã[›ô\öXY‹\ò][ô»€XﬁHõ‹à\ôŸHX\»[ô›Ÿ\ãY[ô€€\]\úÀè‹èŸ]èèŸ]èÇèï\ŸHHXYàù]€àô\⁄YHH€€⁄]‹[ô\à»›⁄]⁄X€€õ€^H[ŸH€à‹àŸôãà[›\àõ‹õX[[Y\À›ô\õ^\»[ôôX]\ôHŸ[X›[€ú»ô[XZ[àÿ]ôY»X€€õ€^H[ŸH[\‹ò\ö[Hô[ô\ú»[ôôYúô\⁄\»[H[‹ôHYôöX⁄Y[ùKè‹Çè]à€\‹œHô‹öYèè]à€\‹œHòÿ\ôèèìX\€‹ö€ÿY⁄èìŸôã\ÿ‹ôY[àôZX€H[ôùZ[[ô»^Y\ú»\ôH]X⁄Y⁄]HÿYô]HùYôô\ã[àô\›‹ôY]]€X]Xÿ[H⁄[à^H[ù\àH›\úô[ùX\\ôXH‹àX€€õ€^H[ŸH\»\ÿXõYè‹èŸ]èè]à€\‹œHòÿ\ôèèîô[ô\ö[ôœ⁄èê€€ù[ù[›\»X€‹ò]]ôH[ö[X][€ã[KYö[\à⁄Z[úÀòX⁄Ÿõ‹õ\à[ôX]ûH^[›]\ùX€\»\ôHô\XŸYûH›]X»\]Z]ò[[ù»⁄[H‹\ò][€ò[€€›\ú»ô[XZ[à[ùX›è‹èŸ]èè]à€\‹œHòÿ\ôèèêòX⁄Ÿ‹õ›[ô€‹öœ⁄èìZ\‹⁄[€ãôZX€KùZ[[ô»[ôXZ[ù[ò[òŸHôYúô\⁄\»\ŸH€ôŸ\àYH[ù\ùò[Àà‹[ö[ô»H[Ÿ[K⁄[ô⁄[ô»HŸ][ô»‹àô\‹⁄[ô»ôYúô\⁄›[ô\]Y\›»›\úô[ù]H[[YYX][Kè‹èŸ]èè]à€\‹œHòÿ\ôèèì\ôŸH[ô[œ⁄èì€ô»Z\‹⁄[€ê⁄YYà\›»\ŸHúõ›‹Ÿ\àô[ô\ö[ô»€€ùZ[õY[ù€»Ÿôã\ÿ‹ôY[àõ›‹»»õ›ô\]Z\ôHù[^[›][ôZ[ù[ôÀè‹èŸ]èèŸ]èÇè]à€\‹œHòÿ[èè›õ€ôœëù[ô\›‹ò][€éè‹›õ€ôœà›⁄]⁄[ô»X€€õ€^H[ŸHŸôàôX]X⁄\»]X\ò[ù[ôY^Y\úÀô\›‹ô\»XYõ]‹[€úÀX\⁄⁄[úÀ[ö[X][€à[ôõ‹õX[ÿ⁄Y[\à[ù\ùò[ÀèŸ]èÇè‹ŸX›[€èò¬à€›\òŸHH€›\òŸKúô\XŸJ	œ€XZ[èâÀ	ŸX€€õ€^TŸX›[€üO€XZ[èò
N¬àBàô]\õà€›\òŸN¬àBÇàù[ò›[€àõ›X›[›ZYQÿ›[Y[ù
ÿ›[Y[ù^
H¬à€€ú›ò]öYÿ][€ë›X\ôHèÿ‹ö\]K[X€\ÀZ[[ò]öYÿ][€ãY›X\ôÇä

HOà¬à	›\ŸH›öX›	Œ¬à€€ú›ÿ‹õ€—›ZYTŸX›[€àHò]“ôYàOà¬à€€ú›ôYàH›ö[ô ò]“ôYà	… N¬àYà
ZôYãú›\ù’⁄]
	»… JHô]\õàò[ŸN¬à]YH	…Œ¬àûH»YHX€ŸUTíP€€\€ô[ù
ôYãú€XŸJJJN»Hÿ]⁄
\úõ‹äH»YHôYãú€XŸJJN»Bà€€ú›\ôŸ]HY»ÿ›[Y[ùôŸ][[Y[ùûRY
Y
Hàÿ›[Y[ùôÿ›[Y[ù[[Y[ù¬àYà
]\ôŸ]
Hô]\õàùYN¬à€€ú›ôYXŸS[›[€àH⁄[ô›ÀõX]⁄YYXH	âà⁄[ô›ÀõX]⁄YYXJ	 ôYô\úÀ\ôYXŸY[[›[€éàôYXŸJI KõX]⁄\Œ¬à\ôŸ]úÿ‹õ€[ù’öY] »ôZ]ö[‹éàôYXŸS[›[€à»	ÿ]]…»à	‹€[€›	Àõÿ⁄Œà	‹›\ù	»JN¬àô]\õàùYN¬àN¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	ÿ€X⁄…À]ô[ùOà¬à€€ú›[ö»H]ô[ùù\ôŸ][ú›[òŸ[Ÿà[[Y[ù»]ô[ùù\ôŸ]ò€‹Ÿ\›
	ÿV⁄ôYóI Hàù[¬àYà
[[ö Hô]\õé¬à€€ú›ôYàH[öÀôŸ]]öXù]J	⁄ôYâ H	…Œ¬àYà
ôYãú›\ù’⁄]
	»… JH¬à]ô[ùúô]ô[ùYò][

N¬àÿ‹õ€—›ZYTŸX›[€äôYäN¬àô]\õé¬àBàYà
◊äŒöœŒäO◊◊À⁄Kù\›
ôYäJH¬à]ô[ùúô]ô[ùYò][

N¬àûH»⁄[ô›Àõ‹[äôYã	◊ÿõ[ö…À	€õ€‹[ô\ãõ‹ôYô\úô\â N»Hÿ]⁄
\úõ‹äHﬂBàBàKùYJN¬üJJ
N¬ó–À‹ÿ‹ö\ò¬à€€ú›€›\òŸHH]⁄[›ZYQÿ›[Y[ù
ÿ›[Y[ù^
N¬àYà
€›\òŸKö[ò€Y\ 	Ÿ]K[X€\ÀZ[[ò]öYÿ][€ãY›X\ô	 JHô]\õà€›\òŸN¬àYà
œÿõŸW èã⁄]Kù\›
€›\òŸJJHô]\õà€›\òŸKúô\XŸJœÿõŸW èã⁄]K	€ò]öYÿ][€ë›X\ôOÿõŸOò
N¬àô]\õà	‹€›\òŸ_I€ò]öYÿ][€ë›X\ôX¬àBÇàù[ò›[€à‹ôX]R[Ÿ[ù\ä
H¬à€€ú›^\›[ô»Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTö[Ÿ[ù\íY
N¬àYà
^\›[ô Hô]\õà^\›[ôŒ¬à€€ú››ô\õ^HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à›ô\õ^KöYH–‘íTö[Ÿ[ù\íY¬à›ô\õ^KúŸ]]öXù]J	‹õ€IÀ	ŸX[Ÿ… N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXK[[Ÿ[	À	›ùYI N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXK[Xô[	À	‘–‘íTõò[Y_H[Ÿ[ùôX
N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXKZY[âÀ	›ùYI N¬à›ô\õ^Kö[õô\íSHà]à€\‹œHõX€\ÀZ[]⁄[ô›»àõ€OHôÿ›[Y[ùèÇà]à€\‹œHõX€\ÀZ[]€€ò\àèÇà]à€\‹œHõX€\ÀZ[Xúò[ôèÇà‹[à€\‹œHõX€\ÀZ[Xúò[ôZX€€àà\öXKZY[èHùùYHèèœ‹‹[èÇà‹[à€\‹œHõX€\ÀZ[Xúò[ôX€‹Hèè›õ€ôœï€€⁄][Ÿ[ùôO‹›õ€ôœè€X[îŸX\ò⁄XõH›ZYH0≠»‹›Y€àHXõX»€€⁄]\‹Ÿ]»ô\‹⁄]‹ûO‹€X[è‹‹[èÇàŸ]èÇà]à€\‹œHõX€\ÀZ[XX›[€ú»èÇàù]€à€\‹œHõX€\ÀZ[XX›[€àà\OHòù]€àà]KZ[XX›[€èHúô[ÿYà]OHîô[ÿYH]\››ZYHà\öXK[Xô[Hîô[ÿYH]\››ZYHè∏°Æœÿù]€èÇàù]€à€\‹œHõX€\ÀZ[XX›[€àX€\ÀZ[\€›\òŸHà\OHòù]€àà]KZ[XX›[€èHú€›\òŸHà]OHì‹[àH›ZYH€›\òŸH€à⁄]Xàà\öXK[Xô[Hì‹[àH›ZYH€›\òŸH€à⁄]Xàè∏°•œÿù]€èÇàù]€à€\‹œHõX€\ÀZ[XX›[€àX€\ÀZ[X€‹ŸHà\OHòù]€àà]KZ[XX›[€èHò€‹ŸHà]OHê€‹ŸH[Ÿ[ùôHà\öXK[Xô[Hê€‹ŸH[Ÿ[ùôHè∞Âœÿù]€èÇàŸ]èÇàŸ]èÇà]à€\‹œHõX€\ÀZ[XYô\‹»èè‹[à€\‹œHõX€\ÀZ[XYô\‹À[ÿ⁄»à\öXKZY[èHùùYHè∏•„œ‹‹[èè‹[à€\‹œHõX€\ÀZ[XYô\‹À]^èô⁄]Xãò€€K–€€úõﬁLNN€Z\‹⁄[€ò⁄YYã]€€⁄]X\‹Ÿ]À⁄[⁄[ô^ö[‹‹[èè‹[à€\‹œHõX€\ÀZ[\›]\»à]KZ[\›]\œîôXYO‹‹[èèŸ]èÇà]à€\‹œHõX€\ÀZ[\õŸ‹ô\‹»à\öXKZY[èHùùYHèèŸ]èÇà]à€\‹œHõX€\ÀZ[X€€ù[ùèÇàYúò[YH€\‹œHõX€\ÀZ[Yúò[YHà]OHìZ\‹⁄[€ê⁄YYàX\€€[X[ô€€⁄]ŸX\ò⁄XõH›ZYHàÿ[ôõﬁHò[›À\ÿ‹ö\»[›À\‹\»àôYô\úô\ú€XﬁOHõõÀ\ôYô\úô\àèè⁄Yúò[YOÇà]à€\‹œHõX€\ÀZ[Yò[òX⁄»èÇà]à€\‹œHõX€\ÀZ[Y\úõ‹ãXÿ\ôèÇà›õ€ôœí[Ÿ[ùôH[ò]òZ[XõO‹›õ€ôœÇà]KZ[Y\úõ‹èïHXõX»›ZYH€›[õ›ôHÿYYàHXZ[à€€⁄]ô[XZ[ú»ù[H‹\ò][€ò[è‹Çà]à€\‹œHõX€\ÀZ[Y\úõ‹ãXX›[€ú»èèù]€à\OHòù]€àà]KZ[XX›[€èHúô[ÿYèîô]ûOÿù]€èèù]€à\OHòù]€àà]KZ[XX›[€èHú€›\òŸHèì‹[à⁄]Xà€›\òŸOÿù]€èèŸ]èÇàŸ]èÇàŸ]èÇàŸ]èÇàŸ]èò¬àù[ù[YS\›[ä›ô\õ^K	ÿ€X⁄…À]ô[ùOà¬à€€ú›X›[€êù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]KZ[XX›[€óI N¬àYà
X›[€êù]€äH¬à]ô[ùúô]ô[ùYò][

N¬à€€ú›X›[€àHX›[€êù]€ãô]\Ÿ]ö[X›[€é¬àYà
X›[€àOOH	ÿ€‹ŸI H€‹ŸR[Ÿ[ù\ä
N¬àYà
X›[€àOOH	‹ô[ÿY	 HÿY[Ÿ[ù\ë›ZYJùYJN¬àYà
X›[€àOOH	‹€›\òŸI H¬àûH»YŸU⁄[ô›Àõ‹[äS–—SïTãú€›\òŸU\õ	◊ÿõ[ö…À	€õ€‹[ô\ãõ‹ôYô\úô\â N»Hÿ]⁄
\úäH»ÿÿ][€ãöôYàHS–—SïTãú€›\òŸU\õ»BàBàô]\õé¬àBàYà
]ô[ùù\ôŸ]OOH›ô\õ^JH€‹ŸR[Ÿ[ù\ä
N¬àJN¬àù[ù[YS\›[ä›ô\õ^K	€[›\ŸY›€âÀ›‹X\[ù\òX›[€äN¬àù[ù[YS\›[ä›ô\õ^K	›⁄Y[	À›‹X\[ù\òX›[€ã»\‹⁄]ôNàùYHJN¬àù[ù[YS\›[ä›ô\õ^K	››X⁄›\ù	À›‹X\[ù\òX›[€ã»\‹⁄]ôNàùYHJN¬àÿ›[Y[ùòõŸKò\[ô⁄[
›ô\õ^JN¬àô]\õà›ô\õ^N¬àBÇà\ﬁ[ò»ù[ò›[€àÿY[Ÿ[ù\ë›ZYJõ‹òŸHHò[ŸJH¬à€€ú››ô\õ^HH‹ôX]R[Ÿ[ù\ä
N¬à€€ú›úò[YHH›ô\õ^Kú]Y\ûTŸ[X›‹ä	ÀõX€\ÀZ[Yúò[YI N¬à€€ú››]\»H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KZ[\›]\◊I N¬à€€ú›\úõ‹ï^H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KZ[Y\úõ‹óI N¬à›ô\õ^Kò€\‹”\›òY
	€X€\À[ÿY[ô… N¬à›ô\õ^Kò€\‹”\›úô[[›ôJ	€X€\ÀY\úõ‹â N¬àYà
›]\ H›]\Àù^€€ù[ùHõ‹òŸH»	‘ôYúô\⁄[ô¯†)â»à	”ÿY[ô¯†)âŒ¬àûH¬à€€ú›ÿ›[Y[ù^H]ÿZ]ô\]Y\›[›ZYQÿ›[Y[ù
õ‹òŸJN¬àYà
[›ô\õ^Kö\–€€õôX›Yù[ù[YKô\›õﬁYY
Hô]\õàò[ŸN¬àúò[YKú‹òŸÿ»Hõ›X›[›ZYQÿ›[Y[ù
ÿ›[Y[ù^
N¬à›ô\õ^Kò€\‹”\›úô[[›ôJ	€X€\ÀY\úõ‹â N¬àYà
›]\ H›]\Àù^€€ù[ùH›ZYH	“S–—SïTãô›ZYUô\ú⁄[€üH0≠»€õ[ôX¬àô]\õàùYN¬àHÿ]⁄
\úäH¬àYà
[›ô\õ^Kö\–€€õôX›Yù[ù[YKô\›õﬁYY
Hô]\õàò[ŸN¬à›ô\õ^Kò€\‹”\›òY
	€X€\ÀY\úõ‹â N¬àYà
›]\ H›]\Àù^€€ù[ùH	”Ÿôõ[ôHò[òX⁄…Œ¬àYà
\úõ‹ï^
H\úõ‹ï^ù^€€ù[ùH	Ÿ\úèÀõY\‹ÿYŸH	’HXõX»›ZYH€›[õ›ôHÿYYâﬂHHXZ[à€€⁄]ô[XZ[ú»ù[H‹\ò][€ò[ò¬àô]\õàò[ŸN¬àHö[ò[H¬à›ô\õ^Kò€\‹”\›úô[[›ôJ	€X€\À[ÿY[ô… N¬àBàBÇàù[ò›[€à‹[í[Ÿ[ù\ä
H¬à€€ú››ô\õ^HH‹ôX]R[Ÿ[ù\ä
N¬à[Ÿ[ù\îô]\õëõÿ›\»Hÿ›[Y[ùòX›]ôQ[[Y[ù[ú›[òŸ[ŸàS[[Y[ù»ÿ›[Y[ùòX›]ôQ[[Y[ùàù[¬à€‹ŸT[ô[

N¬à›ô\õ^Kò€\‹”\›òY
	€X€\À[‹[â N¬à›ô\õ^KúŸ]]öXù]J	ÿ\öXKZY[âÀ	Ÿò[ŸI N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùúŸ]]öXù]J	Ÿ]K[X€\ÀZ[[‹[âÀ	›ùYI N¬à€€ú›€‹ŸPù]€àH›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KZ[XX›[€èHò€‹ŸHóI N¬àù[ù[YTŸ][Y[›]


HOà»ûH»€‹ŸPù]€èÀôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJN»Hÿ]⁄
\úäHﬂHK
N¬à€€ú›úò[YHH›ô\õ^Kú]Y\ûTŸ[X›‹ä	ÀõX€\ÀZ[Yúò[YI N¬àYà
Yúò[YOÀú‹òŸÿ HÿY[Ÿ[ù\ë›ZYJò[ŸJN¬à[ŸH¬à€€ú››]\»H›ô\õ^Kú]Y\ûTŸ[X›‹ä	÷Ÿ]KZ[\›]\◊I N¬àYà
›]\ H›]\Àù^€€ù[ùH[›ZYSÿYY]»›ZYH	“S–—SïTãô›ZYUô\ú⁄[€üH0≠»ÿX⁄Yà›ZYH	“S–—SïTãô›ZYUô\ú⁄[€üX¬àBàBÇàù[ò›[€à›‹X\[ù\òX›[€ä]ô[ù
H¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬àBÇàù[ò›[€à\’\[ô’\ôŸ]
\ôŸ]
H¬àYà
]\ôŸ]
Hô]\õàò[ŸN¬à€€ú›Y»H›ö[ô \ôŸ]ùY”ò[YH	… Kù”›Ÿ\êÿ\ŸJ
N¬àô]\õàY»OOH	⁄[ú]	»Y»OOH	›^\ôXI»Y»OOH	‹Ÿ[X›	»\ôŸ]ö\–€€ù[ùY]XõN¬àBÇàù[ò›[€à[ôRŸ^Xõÿ\ô
]ô[ù
H¬àYà
]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JH¬àX\ô›€ï€€⁄]€€[X[ô⁄[
	⁄Ÿ^Xõÿ\ô]ô[ù›]⁄YHÿ[õ€öXÿ[X\€€ù^	 N¬àô]\õé¬àBàYà
X\YX\›\ôTù[ù[YKòX›]ôH	âàY]ô[ùôYò][ô]ô[ùY	âàZ\’\[ô’\ôŸ]
]ô[ùù\ôŸ]
JH¬àYà
]ô[ùöŸ^HOOH	—\ÿÿ\I H»]ô[ùúô]ô[ùYò][

N»]ô[ùú›‹õ‹Yÿ][€ä
N»›‹X\YX\›\ôJ
N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	–òX⁄‹‹XŸI H»]ô[ùúô]ô[ùYò][

N»]ô[ùú›‹õ‹Yÿ][€ä
N»X\YX\›\ôU[ô 
N»ô]\õé»BàBàYà
]ô[ùöŸ^HOOH	—\ÿÿ\I»	âà€‹ŸP€€ù^€€[X[ôY[ùJ»ô\›‹ôQõÿ›\ŒàùYHJJH»]ô[ùúô]ô[ùYò][

N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—\ÿÿ\I»	âà€‹ŸP€€[X[ô[]J»ô\›‹ôQõÿ›\ŒàùYHJJH»]ô[ùúô]ô[ùYò][

N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—\ÿÿ\I»	âà€‹ŸUXõ]]ZX⁄’⁄Y[
»ô\›‹ôQõÿ›\ŒàùYHJJH»]ô[ùúô]ô[ùYò][

N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—\ÿÿ\I»	âà€‹ŸP€€[X[ô^\öY[òŸS[Ÿ[

JH»]ô[ùúô]ô[ùYò][

N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—\ÿÿ\I»	âà€‹ŸR[Ÿ[ù\ä
JH»]ô[ùúô]ô[ùYò][

N»ô]\õé»BàYà
]ô[ùöŸ^HOOH	—\ÿÿ\I H¬àYà
›]Kôù[ÿ‹ôY[ìX\
H»]ô[ùúô]ô[ùYò][

N»Ÿ]X\ù[ÿ‹ôY[äò[ŸJN»ô]\õé»Bà€€ú›Y‹[ïZHHõ€€X[äàÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
OÀò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â Hàÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTùôZX€T›]\“Y
OÀò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â Hà‹\ò][€ò[ô\‹›\ôPõÿ\ô‹[ä
Bà
N¬àYà
›]Kò€X[ì[ŸH	âà›]Kú⁄‹ù›] HŸŸ€QôX]\ôJ	ÿ€X[â N¬à€‹ŸT[ô[
»ô\›‹ôQõÿ›\ŒàY‹[ïZHJN¬à€‹ŸUôZX€P€ŸT›]\ 
N¬à€‹ŸS‹\ò][€ò[ô\‹›\ôPõÿ\ô

N¬àYà
Y‹[ïZJH]ô[ùúô]ô[ùYò][

N¬àô]\õé¬àBàYà
\›]Kú⁄‹ù›]»\’\[ô’\ôŸ]
]ô[ùù\ôŸ]
H]ô[ùôYò][ô]ô[ùY]ô[ùúô\X]]ô[ùõY]RŸ^JHô]\õé¬à€€ú›ö[ô[ô»HŸ^Xõÿ\ôö[ô[ô—úõ€Q]ô[ù
]ô[ù
N¬à€€ú›€€[X[ôHÿöôX›öŸ^\ SîU–””SPSë”QUJKôö[ô
Ÿ^HOà›]Kö[ú]›Y[Àö›Ÿ^\÷⁄Ÿ^WHOOHö[ô[ô N¬àYà
X€€[X[ô
Hô]\õé¬à]ô[ùúô]ô[ùYò][

N¬à^X›]R[ú]€€[X[ô
€€[X[ô
N¬àBÇàù[ò›[€àùZ[[YS‹[€ú Ÿ[X›Y
H¬àô]\õàSQW”‘ëTãõX\
Ÿ^HOà‹[€àò[YOHâ⁄Ÿ^_Hà	⁄Ÿ^HOOHŸ[X›Y»	‹Ÿ[X›Y	»à	…ﬂOâ’SQT÷⁄Ÿ^WKôù[O€‹[€èò
Köõ⁄[ä	… N¬àBÇàù[ò›[€àXZŸUŸŸ€Pù]€äŸ^KX€€ãXô[]KôX]\ôPôXX€€àH	… H¬àô]\õààù]€à€\‹œHõX€\À]ŸŸ€KXùàà\OHòù]€àà]K]ŸŸ€OHâ⁄Ÿ^_Hà]OHâŸ\ÿÿ\R[
]HXô[
_HâŸôX]\ôPôXX€€à»]KYôX]\ôKXôXX€€èHâŸ\ÿÿ\R[
ôX]\ôPôXX€€ä_Hòà	…ﬂOÇà‹[à€\‹œHõX€\ÀZX€€òõﬁèâ⁄X€€üO‹‹[èÇà‹[à€\‹œHõX€\À]^èÇà‹[à€\‹œHõX€\À[Xô[èâŸ\ÿÿ\R[
Xô[
_O‹‹[èÇà‹[à€\‹œHõX€\À\[èì—ëè‹‹[èÇà‹‹[èÇàÿù]€èÇà¬àBÇàù[ò›[€àXZŸPX›[€ïŸŸ€Pù]€äX›[€ãX€€ãXô[]K€\‹”ò[YHH	… H¬àô]\õààù]€à€\‹œHõX€\À]ŸŸ€KXùàX€\ÀXX›[€ã]ŸŸ€H	Ÿ\ÿÿ\R[
€\‹”ò[YJ_Hà\OHòù]€àà]KXX›[€èHâŸ\ÿÿ\R[
X›[€ä_Hà]OHâŸ\ÿÿ\R[
]HXô[
_Hà\öXK\ô\‹ŸYHôò[ŸHèÇà‹[à€\‹œHõX€\ÀZX€€òõﬁèâ⁄X€€üO‹‹[èÇà‹[à€\‹œHõX€\À]^èÇà‹[à€\‹œHõX€\À[Xô[èâŸ\ÿÿ\R[
Xô[
_O‹‹[èÇà‹[à€\‹œHõX€\À\[èì—ëè‹‹[èÇà‹‹[èÇàÿù]€èÇà¬àBÇàù[ò›[€àXZŸP[X[òŸSY[Xô\ìX[òYŸ\ïŸŸ€Pù]€ä
H¬àô]\õààù]€à€\‹œHõX€\À]ŸŸ€KXùàà\OHòù]€àà]KXX›[€èHùŸŸ€KX[X[òŸK[Y[Xô\ã[X[òYŸ\àà]K[X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\ã]ŸŸ€OHùùYHà]OHë[òXõH‹à\ÿXõH[X[òŸHY[Xô\àX[òYŸ\àà\öXK[Xô[Hê[X[òŸHY[Xô\àX[òYŸ\àà\öXK\ô\‹ŸYHôò[ŸHèÇà‹[à€\‹œHõX€\ÀZX€€òõﬁèêSO‹‹[èÇà‹[à€\‹œHõX€\À]^èÇà‹[à€\‹œHõX€\À[Xô[èê[X[òŸHY[Xô\àX[òYŸ\è‹‹[èÇà‹[à€\‹œHõX€\À\[èì—ëè‹‹[èÇà‹‹[èÇàÿù]€èÇà¬àBÇà€€ú›PT–””ïì”“P””î»HÿöôX›ôúôY^ôJ¬à^SZ\‹⁄[€úŒà	¯•„…Àà[X[òŸSZ\‹⁄[€úŒà	¯•·âÀàôZX€\Œà	¯•¨	ÀàùZ[[ô‹Œà	¯•©âÀà[X[òŸP‹ôY]Œà	®…ÀàZ\‹⁄[€êYŸNà	¯•Ì…Ààò[ú‹‹ùÿ]⁄\éà	¯°•…Àà[ö]€€[Z]Y[ùà	»…Àà›X⁄—]X›‹éà	»IÀàôZX€T›]\Œà	¯•©	Ààô\‹›\ôPõÿ\ôà	¯•¨âÀà€€[X[ô[]Nà	¯£%IÀàYX\›\ôNà	¯°•	ÀàX€€õ€^S[ŸNà	¯¶n…ÀàJN¬Çàù[ò›[€àXZŸQõÿ]ù]€äŸ^K⁄‹ù›]Xô[]KXõ]Xô[HXô[[ÿö[SXô[HXõ]Xô[
H¬à€€ú›Ÿ^Xõÿ\ô⁄‹ù›]H›ö[ô ⁄‹ù›]	… Kùö[J
N¬à€€ú›⁄‹ù›]]öXù]HHŸ^Xõÿ\ô⁄‹ù›]»\öXKZŸ^\⁄‹ù›]œHâŸ\ÿÿ\R[
Ÿ^Xõÿ\ô⁄‹ù›]
_Hòà	…Œ¬à€€ú›Ÿ^SXô[HŸ^Xõÿ\ô⁄‹ù›]PT–””ïì”“P””î÷⁄Ÿ^WH	¯†(âŒ¬àô]\õààù]€à€\‹œHõX€\ÀYõÿ]Xùàà\OHòù]€àà]K]ŸŸ€OHâ⁄Ÿ^_Hà]OHâŸ\ÿÿ\R[
]J_Hà\öXK[Xô[HâŸ\ÿÿ\R[
Xô[
_NàŸôãà	Ÿ\ÿÿ\R[
]J_Hâ‹⁄‹ù›]]öXù]_H\öXK\ô\‹ŸYHôò[ŸHèÇà‹[à€\‹œHõX€\ÀYõÿ]ZŸ^Hâ⁄Ÿ^Xõÿ\ô⁄‹ù›]»	…»à	»\öXKZY[èHùùYHâﬂOâŸ\ÿÿ\R[
Ÿ^SXô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ]ZX€€àà\öXKZY[èHùùYHèâ”PT–””ïì”“P””î÷⁄Ÿ^WH	¯†(âﬂO‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ]X€‹HèÇà‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[Y\⁄›‹èâŸ\ÿÿ\R[
Xô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[]Xõ]èâŸ\ÿÿ\R[
Xõ]Xô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[[[ÿö[HèâŸ\ÿÿ\R[
[ÿö[SXô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀX€€ùõ€\›]Hèì—ëè‹‹[èÇà‹‹[èÇàÿù]€èÇà¬àBÇàù[ò›[€àXZŸPX›[€ëõÿ]ù]€äX›[€ã⁄‹ù›]Xô[]KXõ]Xô[HXô[[ÿö[SXô[HXõ]Xô[X€€íŸ^HH	›ôZX€T›]\… H¬à€€ú›Ÿ^Xõÿ\ô⁄‹ù›]H›ö[ô ⁄‹ù›]	… Kùö[J
N¬à€€ú›⁄‹ù›]]öXù]HHŸ^Xõÿ\ô⁄‹ù›]»\öXKZŸ^\⁄‹ù›]œHâŸ\ÿÿ\R[
Ÿ^Xõÿ\ô⁄‹ù›]
_Hòà	…Œ¬à€€ú›Ÿ^SXô[HŸ^Xõÿ\ô⁄‹ù›]PT–””ïì”“P””î÷⁄X€€íŸ^WH	¯†(âŒ¬àô]\õààù]€à€\‹œHõX€\ÀYõÿ]XùàX€\ÀYõÿ]XX›[€ãXùàà\OHòù]€àà]KXX›[€èHâŸ\ÿÿ\R[
X›[€ä_Hà]OHâŸ\ÿÿ\R[
]J_Hà\öXK[Xô[HâŸ\ÿÿ\R[
]J_Hâ‹⁄‹ù›]]öXù]_H\öXK\ô\‹ŸYHôò[ŸHèÇà‹[à€\‹œHõX€\ÀYõÿ]ZŸ^Hâ⁄Ÿ^Xõÿ\ô⁄‹ù›]»	…»à	»\öXKZY[èHùùYHâﬂOâŸ\ÿÿ\R[
Ÿ^SXô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ]ZX€€àà\öXKZY[èHùùYHèâ”PT–””ïì”“P””î÷⁄X€€íŸ^WH	¯†(âﬂO‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ]X€‹HèÇà‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[Y\⁄›‹èâŸ\ÿÿ\R[
Xô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[]Xõ]èâŸ\ÿÿ\R[
Xõ]Xô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[[[ÿö[HèâŸ\ÿÿ\R[
[ÿö[SXô[
_O‹‹[èÇà‹[à€\‹œHõX€\ÀX€€ùõ€\›]Hèì—ëè‹‹[èÇà‹‹[èÇàÿù]€èÇà¬àBÇàÀ»\‹›YHÃML»[ùõŸXŸYH€€ùõ€»\‹›Y\»ÕåŒH[ôÕHXZŸHô\öYöYY–àô[X\ŸH\ÿ€›ô\ûH]ôH[ôô[X\ŸK\›]H]]‹ö]]]ôKÇà€€ú›ëTî“S”ó‘’UT»HÿöôX›ôúôY^ôJ»X[öYô\›\õà	⁄ŒãÀ‹ò]Àô⁄]Xù\Ÿ\ò€€ù[ùò€€K–€€úõﬁLNN€Z\‹⁄[€ò⁄YYã]€€⁄]X\‹Ÿ]À‹ô[X\ŸK\›]K‹›]\À›\]K[X[öYô\›öú€€âÀõŸX›\õà	⁄ŒãÀ›ÿãYÿ[Z[ôÀúÿ€›€Z\‹⁄[€ãX⁄YYã\ÿ‹ö\À€X\X€€[X[ô]€€⁄]…ÀÿX⁄RŸ^Nà	€X€\◊›ô\ú⁄[€ó‹›]\◊ÿÿX⁄W›åIÀòZ[\ôRŸ^Nà	€X€\◊›ô\ú⁄[€ó‹›]\◊ŸòZ[\ôW›åIÀÿX⁄S\Œàå
àL]]“[ù\ùò[\Œàå
àLòZ[\ôP€€€›€ì\Œàå
àLô\]Y\›[Y[›]\Œà
àLõ€›[^S\ŒàML€ô‘ô\‹”\ŒàçL›[RYà	€X€\À]ô\ú⁄[€ã\›]\À\›[IÀ[\ù›[RYà	€X€\À]ô\ú⁄[€ã\›]\ÀX[\ù\›[IÀù]€íYà	€X€\À]ô\ú⁄[€ã\›]\ÀX€€ùõ€	»JN¬à]ô\ú⁄[€î›]\”[Ÿ[H»›]Nà	⁄YIÀX[öYô\›àù[⁄X⁄ŸY]àòZ[Y]à\úõ‹éà	…»N»]ô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸHHù[»]ô\ú⁄[€î›]\“Yò][€îõ€Z\ŸHHù[»]ô\ú⁄[€î›]\’[Y\àHù[»]ô\ú⁄[€î›]\‘ô\]Y\›Hù[»]ô\ú⁄[€î›]\‘ô\]Y\›⁄Ÿ[àH»]ô\ú⁄[€î›]\”€ô‘ô\‹’[Y\àHù[»]ô\ú⁄[€î›]\‘›\ô\‹–€X⁄»Hò[ŸN»]ô\ú⁄[€î›]\“[ö]X[⁄X⁄‘]Y]YYHò[ŸN¬àù[ò›[€àô\ú⁄[€î›]\‘\úŸJò[YJH»€€ú›X]⁄H›ö[ô ò[YH	… Kùö[J
KõX]⁄
◊ä
 Wä
 Wä
 I›JN»ô]\õàX]⁄»X]⁄ú€XŸJJKõX\
ù[Xô\äHàù[»Bàù[ò›[€àô\ú⁄[€î›]\–€€\\ôJYùöY⁄
H»€€ú›HHô\ú⁄[€î›]\‘\úŸJYù
N»€€ú›àHô\ú⁄[€î›]\‘\úŸJöY⁄
N»Yà
XHXäHô]\õàù[»õ‹à
][ô^H»[ô^Œ»[ô^
œHJH»Yà
V⁄[ô^HOOHñ⁄[ô^JHô]\õàV⁄[ô^Hàñ⁄[ô^H»HàLN»Hô]\õà»Bàù[ò›[€àô\ú⁄[€î›]\’\õ
ò[YK⁄[ôô\ú⁄[€äH»]\õ»ûH»\õHô]»Tì
›ö[ô ò[YH	… JN»Hÿ]⁄
\úäH»õ›»ô]»\úõ‹ä[ùò[Y	⁄⁄[ôHTìò
N»HYà
\õúõ›ÿ€€OOH	⁄Œâ Hõ›»ô]»\úõ‹ä	⁄⁄[ôHTì]\›\ŸHÀò
N»Yà
⁄[ôOOH	‹ô[X\ŸI H»€€ú›^X›YH–€€úõﬁLNN€Z\‹⁄[€ò⁄YYã]€€⁄]X\‹Ÿ]À‹ô[X\Ÿ\À›YÀ›â›ô\ú⁄[€üX»Yà
\õö‹›ò[YHOOH	Ÿ⁄]Xãò€€I»\õú]ò[YHOOH^X›Y
Hõ›»ô]»\úõ‹ä	‘ô[X\ŸHTì\»õ›ÿ[õ€öXÿ[â N»H[ŸHYà
\õö‹›ò[YHOOH	›ÿãYÿ[Z[ôÀúÿ€›	»\õú]ò[YHOOH	À€Z\‹⁄[€ãX⁄YYã\ÿ‹ö\À€X\X€€[X[ô]€€⁄]⁄[ú›[… Hõ›»ô]»\úõ‹ä	’\]HTì\»õ›ÿ[õ€öXÿ[â N»ô]\õà\õöôYé»Bàù[ò›[€àô\ú⁄[€î›]\’ò[Y]SX[öYô\›
^[ÿY
H»Yà
\^[ÿY\[Ÿà^[ÿYOOH	€ÿöôX›	»\úò^Kö\–\úò^J^[ÿY
JHõ›»ô]»\úõ‹ä	’ô\ú⁄[€àX[öYô\›\»õ›[àÿöôX›â N»Yà
ù[Xô\ä^[ÿYúÿ⁄[XUô\ú⁄[€äHOOHH^[ÿYò⁄[õô[OOH	‹›XõI Hõ›»ô]»\úõ‹ä	’ô\ú⁄[€àX[öYô\›⁄[õô[\»[ùò[Yâ N»€€ú›ô\ú⁄[€àH›ö[ô ^[ÿYùô\ú⁄[€à	… Kùö[J
N»Yà
]ô\ú⁄[€î›]\‘\úŸJô\ú⁄[€äJHõ›»ô]»\úõ‹ä	’ô\ú⁄[€àX[öYô\›Ÿ\»õ›€€ùZ[àH›XõHŸ[X[ùX»ô\ú⁄[€ãâ N»ô]\õà»ÿ⁄[XUô\ú⁄[€éàK⁄[õô[à	‹›XõIÀô\ú⁄[€ãô[X\ŸSõ›\’\õàô\ú⁄[€î›]\’\õ
^[ÿYúô[X\ŸSõ›\’\õ	‹ô[X\ŸIÀô\ú⁄[€äK\]U\õàô\ú⁄[€î›]\’\õ
^[ÿYù\]U\õ	›\]IÀô\ú⁄[€äKXõ\⁄Y]à›ö[ô ^[ÿYúXõ\⁄Y]	… HN»Bàù[ò›[€àô\ú⁄[€î›]\‘ô\Ÿ[ù][€ä[ú›[Yô\ú⁄[€ãX[öYô\›
H»€€ú›€€\\ö\€€àHô\ú⁄[€î›]\–€€\\ôJX[öYô\›Àùô\ú⁄[€ã[ú›[Yô\ú⁄[€äN»Yà
€€\\ö\€€àOOHù[
Hõ›»ô]»\úõ‹ä	“[ú›[Y‹àXõ\⁄Yô\ú⁄[€à\»X[õ‹õYYâ N»ô]\õà»›]Nà€€\\ö\€€àà»	›\]I»à	€]\›	À\›[ò][€éàëTî“S”ó‘’UTÀúõŸX›\õN»Bàù[ò›[€àô\ú⁄[€î›]\–ÿX⁄R\—úô\⁄
ÿX⁄Kõ›»H]Kõõ› 
JH»Yà
XÿX⁄H\[ŸàÿX⁄HOOH	€ÿöôX›	 Hô]\õàò[ŸN»€€ú›⁄X⁄ŸY]Hù[Xô\äÿX⁄Kò⁄X⁄ŸY]
N»Yà
Sù[Xô\ãö\—ö[ö]J⁄X⁄ŸY]
H⁄X⁄ŸY]àõ›»õ›»H⁄X⁄ŸY]èHëTî“S”ó‘’UTÀòÿX⁄S\ Hô]\õàò[ŸN»ûH»ô\ú⁄[€î›]\’ò[Y]SX[öYô\›
ÿX⁄KõX[öYô\›
N»ô]\õàùYN»Hÿ]⁄
\úäH»ô]\õàò[ŸN»HBàù[ò›[€àô\ú⁄[€î›]\—òZ[\ôP€€€[ô ò[YKõ›»H]Kõõ› 
JH»€€ú›òZ[Y]Hù[Xô\äò[YOÀôòZ[Y]œ»ò[YJN»ô]\õàù[Xô\ãö\—ö[ö]JòZ[Y]
H	âàòZ[Y]Hõ›»	âàõ›»HòZ[Y]ëTî“S”ó‘’UTÀôòZ[\ôP€€€›€ì\Œ»Bà\ﬁ[ò»ù[ò›[€àô\ú⁄[€î›]\‘›‹òYŸTôXY
Ÿ^JH»ûH»Yà
\[Ÿà”WŸŸ]ò[YHOOH	Ÿù[ò›[€â Hô]\õà]ÿZ]”WŸŸ]ò[YJŸ^Kù[
N»Hÿ]⁄
\úäHﬂHûH»€€ú›ò]»HYŸU⁄[ô›Àõÿÿ[›‹òYŸOÀôŸ]][JŸ^JN»ô]\õàò]»»î””ãú\úŸJò] Hàù[»Hÿ]⁄
\úäH»ô]\õàù[»HBà\ﬁ[ò»ù[ò›[€àô\ú⁄[€î›]\‘›‹òYŸU‹ö]JŸ^Kò[YJH»ûH»Yà
\[Ÿà”W‹Ÿ]ò[YHOOH	Ÿù[ò›[€â H»]ÿZ]”W‹Ÿ]ò[YJŸ^Kò[YJN»ô]\õé»HHÿ]⁄
\úäHﬂHûH»YŸU⁄[ô›Àõÿÿ[›‹òYŸOÀúŸ]][JŸ^Kî””ãú›ö[ô⁄YûJò[YJJN»Hÿ]⁄
\úäHﬂHBà\ﬁ[ò»ù[ò›[€àô\ú⁄[€î›]\‘›‹òYŸQ[]JŸ^JH»ûH»Yà
\[Ÿà”WŸ[]Uò[YHOOH	Ÿù[ò›[€â H»]ÿZ]”WŸ[]Uò[YJŸ^JN»ô]\õé»HHÿ]⁄
\úäHﬂHûH»YŸU⁄[ô›Àõÿÿ[›‹òYŸOÀúô[[›ôR][JŸ^JN»Hÿ]⁄
\úäHﬂHBàù[ò›[€àô\ú⁄[€î›]\‘ô[ô\ä
H»€€ú›ù]€àHÿ›[Y[ùôŸ][[Y[ùûRY
ëTî“S”ó‘’UTÀòù]€íY
N»Yà
Xù]€äHô]\õé»€€ú›[ú›[YH–‘íTùô\ú⁄[€é»€€ú›]òZ[XõHHô\ú⁄[€î›]\”[Ÿ[õX[öYô\›Àùô\ú⁄[€à	…Œ»€€ú››]Sò[YHHô\ú⁄[€î›]\”[Ÿ[ú›]N»€€ú›Xô[»H»YNà	–“P“…À⁄X⁄⁄[ôŒà	–“P“…À]\›à	”UT’	À\]Nà	’TUIÀ\úõ‹éà	–“P“…»N»€€ú›Xô[HXô[÷‹›]Sò[YWH	–“P“…Œ»ù]€ãù^€€ù[ùH	…Œ»ù]€ãô]\Ÿ]õXô[HXô[»ù]€ãô]\Ÿ]ú›]HH›]Sò[YN»ù]€ãò€\‹”\›ùŸŸ€J	€X€\À]ô\ú⁄[€ã]\]KX[\ù	À›]Sò[YHOOH	›\]I N»ù]€ãúŸ]]öXù]J	ÿ\öXKXù\ﬁIÀ›ö[ô ›]Sò[YHOOH	ÿ⁄X⁄⁄[ô… JN»]]HH€€⁄]	⁄[ú›[YH8†%‹[àŸôöX⁄X[€€⁄]YŸX»Yà
›]Sò[YHOOH	ÿ⁄X⁄⁄[ô… H]HH⁄X⁄⁄[ô»€€⁄]	⁄[ú›[YHYÿZ[ú›Hô\öYöYYõŸX›[€àô[X\ŸH8†%‹[àŸôöX⁄X[€€⁄]YŸX»Yà
›]Sò[YHOOH	€]\›	 H]HH€€⁄]	⁄[ú›[YH\»›\úô[ù8†%‹[àŸôöX⁄X[€€⁄]YŸX»Yà
›]Sò[YHOOH	›\]I H]HH€€⁄]	⁄[ú›[YH[ú›[Y»	ÿ]òZ[Xõ_H]òZ[XõH8†%‹[àŸôöX⁄X[\]HYŸX»Yà
›]Sò[YHOOH	Ÿ\úõ‹â H]HH€€⁄]	⁄[ú›[YH\]H⁄X⁄»[ò]òZ[XõH8†%‹[àŸôöX⁄X[€€⁄]YŸX»ù]€ãù]HH]N»ù]€ãúŸ]]öXù]J	ÿ\öXK[Xô[	À]JN»Bàù[ò›[€à[ú›\ôUô\ú⁄[€î›]\‘›[J
H»Yà
ÿ›[Y[ùôŸ][[Y[ùûRY
ëTî“S”ó‘’UTÀú›[RY
JHô]\õé»€€ú››[HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹›[I N»›[KöYHëTî“S”ó‘’UTÀú›[RY»›[Kù^€€ù[ùH…’ëTî“S”ó‘’UTÀòù]€íY^ÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ùàÕôòçŸôéÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿéåLLKNÀçMNÿõﬁ\⁄^ö[ôŒòõ‹ô\ãXõﬁZ[\‹ù[ù‹‹⁄][€éúô[]]ôNŸ\‹^Nö[õ[ôKYõ^Z[\‹ù[ùŸõ^Y\ôX›[€éò€€[[àZ[\‹ù[ùÿ[Y€ãZ][\ŒòŸ[ù\àZ[\‹ù[ù⁄ù\›YûKX€€ù[ùòŸ[ù\àZ[\‹ù[ùŸÿ\åúZ[\‹ù[ùÿ[Y€ã\Ÿ[éôõ^\›\ùŸõ^åZ[\‹ù[ù›⁄YçZ[\‹ù[ù€Z[ã]⁄YçZ[\‹ù[ù€X^]⁄YçZ[\‹ù[ù⁄ZY⁄çZ[\‹ù[ù€Z[ãZZY⁄çZ[\‹ù[ù€X^ZZY⁄çZ[\‹ù[ù€X\ô⁄[éåZ[\‹ù[ù‹Y[ôŒç‹‹Z[\‹ù[ù€›ô\ôõ›ŒöY[àZ[\‹ù[ùÿõ‹ô\éå\€€YôÿòJçMKçMKçMKåçäHZ[\‹ù[ùÿõ‹ô\ã\òY]\Œé\Z[\‹ù[ùÿòX⁄Ÿ‹õ›[ôõ[ôX\ãY‹òYY[ù
NYÀôÿòJLÀNKéN
H	KôÿòJMKNKåÀéN
HL	JHZ[\‹ù[ùÿ€€‹éàŸçYçŸòHZ[\‹ù[ù›^X[Y€éòŸ[ù\àZ[\‹ù[ù›^]ò[úŸõ‹õNù\\òÿ\ŸHZ[\‹ù[ù›⁄]K\‹XŸNõõ›‹ò\Z[\‹ù[ù›€‹ôXúôXZŒõõ‹õX[Z[\‹ù[ù€›ô\ôõ›À]‹ò\õõ‹õX[Z[\‹ù[ùÿõﬁ\⁄Y›Œå‹\ôÿòJåŒ
K[úŸ]\ôÿòJçMKçMKçMKåLäK\ôÿòJò\äK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿäKåLJHZ[\‹ù[ùÿ›\ú€‹éú⁄[ù\é››X⁄XX›[€éõX[ö\[][€é›\Ÿ\ã\Ÿ[X›õõ€ôNÀ]ŸXö⁄]]\ZY⁄Y⁄X€€‹éùò[ú‹\ô[ùH…’ëTî“S”ó‘’UTÀòù]€íYNéòôYõ‹ô^ÿ€€ù[ùà∏†(ààZ[\‹ù[ùÿõﬁ\⁄^ö[ôŒòõ‹ô\ãXõﬁŸ\‹^Nôõ^Z[\‹ù[ùÿ[Y€ãZ][\ŒòŸ[ù\àZ[\‹ù[ù⁄ù\›YûKX€€ù[ùòŸ[ù\àZ[\‹ù[ùŸõ^ååZ[\‹ù[ù›⁄YååZ[\‹ù[ù⁄ZY⁄ååZ[\‹ù[ù€X\ô⁄[éåZ[\‹ù[ù‹Y[ôŒåZ[\‹ù[ùÿõ‹ô\éå\€€YôÿòJò\äK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿäKçÃäHZ[\‹ù[ùÿõ‹ô\ã\òY]\ŒçL	HZ[\‹ù[ùÿòX⁄Ÿ‹õ›[ôúôÿòJò\äK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿäKåMäHZ[\‹ù[ùÿ€€‹éùò\äK[X€\À]ô\ú⁄[€ãXXÿŸ[ù
HZ[\‹ù[ùŸõ€ùéLLúÃHﬁ\›[K]ZKX\K\ﬁ\›[Kõ[ö”XX‘ﬁ\›[Qõ€ùîŸY€ŸHRHãÿ[úÀ\Ÿ\öYàZ[\‹ù[ù€]\ã\‹X⁄[ôŒåZ[\‹ù[ù›⁄]K\‹XŸNõõ›‹ò\Z[\‹ù[ùÿõﬁ\⁄Y›Œå‹ôÿòJò\äK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿäKååäK[úŸ]\ôÿòJçMKçMKçMKåJHZ[\‹ù[ùH…’ëTî“S”ó‘’UTÀòù]€íYNéòYù\ûÿ€€ù[ùò]ä]K[Xô[
HZ[\‹ù[ùÿõﬁ\⁄^ö[ôŒòõ‹ô\ãXõﬁŸ\‹^Nòõÿ⁄»Z[\‹ù[ù›⁄YåL	HZ[\‹ù[ù€X^]⁄YåL	HZ[\‹ù[ù€X\ô⁄[éåZ[\‹ù[ù‹Y[ôŒåZ[\‹ù[ù€›ô\ôõ›ŒöY[àZ[\‹ù[ùÿ€€‹éàŸçYçŸòHZ[\‹ù[ùŸõ€ùéÀåúÃHﬁ\›[K]ZKX\K\ﬁ\›[Kõ[ö”XX‘ﬁ\›[Qõ€ùîŸY€ŸHRHãÿ[úÀ\Ÿ\öYàZ[\‹ù[ù€]\ã\‹X⁄[ôŒãåLúZ[\‹ù[ù›^X[Y€éòŸ[ù\àZ[\‹ù[ù›^]ò[úŸõ‹õNù\\òÿ\ŸHZ[\‹ù[ù›⁄]K\‹XŸNõõ›‹ò\Z[\‹ù[ù›€‹ôXúôXZŒöŸY\X[Z[\‹ù[ù€›ô\ôõ›À]‹ò\õõ‹õX[Z[\‹ù[ù›^[›ô\ôõ›Œò€\Z[\‹ù[ùH…’ëTî“S”ó‘’UTÀòù]€íYNôõÿ›\À]ö\⁄Xõ^€›][ôNåú€€Yò\äK[X€\À]ô\ú⁄[€ãXXÿŸ[ù
HZ[\‹ù[ù€›][ôK[ŸôúŸ]åúH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHõ]\›ó^ÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ùàÕXôŒLNÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿééLKåLKM_H…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHõ]\›óNéòôYõ‹ô^ÿ€€ù[ùà∏ß$»àZ[\‹ù[ùH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHù\]Hó^ÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ùàŸôòÕLéÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿéåçMKNMãüH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHù\]HóNéòôYõ‹ô^ÿ€€ù[ùà∏°§HàZ[\‹ù[ùH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHò⁄X⁄⁄[ô»ó^ÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ùàÕÕòÕŸôéÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿéåLNNNKçMNÿ›\ú€‹éúõŸ‹ô\‹Œ€‹X⁄]NãéH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHò⁄X⁄⁄[ô»óNéòôYõ‹ô^ÿ€€ù[ùà∏†)ààZ[\‹ù[ùH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHô\úõ‹àó^ÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ùàŸôçŸMŸNÀK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿéåçMKLçãLçüH…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHô\úõ‹àóNéòôYõ‹ô^ÿ€€ù[ùààHàZ[\‹ù[ùZ[Ÿ]K[X€\À]Xõ]XX›]ôOHùùYHóH…’ëTî“S”ó‘’UTÀòù]€íY^Ÿõ^Xò\⁄\ŒçZ[\‹ù[ù›⁄YçZ[\‹ù[ù€Z[ã]⁄YçZ[\‹ù[ù€X^]⁄YçZ[\‹ù[ù⁄ZY⁄çZ[\‹ù[ù€Z[ãZZY⁄çZ[\‹ù[ù€X^ZZY⁄çZ[\‹ù[ù‹Y[ôŒå‹úZ[\‹ù[ùÿõ‹ô\ã\òY]\ŒéZ[\‹ù[ùZ[Ÿ]K[X€\À]Xõ]XX›]ôOHùùYHóH…’ëTî“S”ó‘’UTÀòù]€íYNéòôYõ‹ô^Ÿõ^Xò\⁄\ŒåNZ[\‹ù[ù›⁄YåNZ[\‹ù[ù⁄ZY⁄åNZ[\‹ù[ùŸõ€ù\⁄^ôNåL\Z[\‹ù[ùZ[Ÿ]K[X€\À]Xõ]XX›]ôOHùùYHóH…’ëTî“S”ó‘’UTÀòù]€íYNéòYù\ûŸõ€ù\⁄^ôNçãç‹Z[\‹ù[ù€]\ã\‹X⁄[ôŒåZ[\‹ù[ùZ[Ÿ]K[X€\À[[ÿö[KXX›]ôOHùùYHóH…’ëTî“S”ó‘’UTÀòù]€íY^Ÿõ^Xò\⁄\ŒçúZ[\‹ù[ù›⁄YçúZ[\‹ù[ù€Z[ã]⁄YçúZ[\‹ù[ù€X^]⁄YçúZ[\‹ù[ù⁄ZY⁄çúZ[\‹ù[ù€Z[ãZZY⁄çúZ[\‹ù[ù€X^ZZY⁄çúZ[\‹ù[ù‹Y[ôŒå‹úZ[\‹ù[ùÿõ‹ô\ã\òY]\Œé\Z[\‹ù[ùZ[Ÿ]K[X€\À[[ÿö[KXX›]ôOHùùYHóH…’ëTî“S”ó‘’UTÀòù]€íYNéòôYõ‹ô^Ÿõ^Xò\⁄\ŒåN\Z[\‹ù[ù›⁄YåN\Z[\‹ù[ù⁄ZY⁄åN\Z[\‹ù[ùŸõ€ù\⁄^ôNåL\Z[\‹ù[ùZ[Ÿ]K[X€\À[[ÿö[KXX›]ôOHùùYHóH…’ëTî“S”ó‘’UTÀòù]€íYNéòYù\ûŸõ€ù\⁄^ôNçãé\Z[\‹ù[ù€]\ã\‹X⁄[ôŒåZ[\‹ù[ùPYYXH
ôYô\úÀ\ôYXŸY[[›[€éúôYXŸJ^»…’ëTî“S”ó‘’UTÀòù]€íY^›ò[ú⁄][€éõõ€ôHZ[\‹ù[ù_X»
ÿ›[Y[ùöXYÿ›[Y[ùôÿ›[Y[ù[[Y[ù
Kò\[ô⁄[
›[JN»Bàù[ò›[€à[ú›\ôUô\ú⁄[€î›]\–[\ù›[J
H¬àYà
ÿ›[Y[ùú]Y\ûTŸ[X›‹ä…’ëTî“S”ó‘’UTÀò[\ù›[RYX
JHô]\õé¬à€€ú››[HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹›[I N¬à›[KöYHëTî“S”ó‘’UTÀò[\ù›[RY¬à›[Kù^€€ù[ùHàŸ^Yúò[Y\»X€\’ô\ú⁄[€ï\]Sô[€à¬à	KL	H»õﬁ\⁄Y›Œå\ôÿòJMÀçMKåÀéäKLúôÿòJMÀçMKåÀçåäKåúôÿòJMÀåLçMKçäK‹\ôÿòJçJK[úŸ]ôÿòJMÀçMKåÀåN
N»BàL	H»õﬁ\⁄Y›ŒåôÿòJMÀçMKåÀJKåôÿòJMÀçMKåÀéMäKÕôÿòJMÀåLçMKçŒ
K‹\ôÿòJçJK[úŸ]MôÿòJMÀçMKåÀåÃäN»BàBà…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHù\]HóH¬àK[X€\À]ô\ú⁄[€ãXXÿŸ[ùàÃŒYôòŸàZ[\‹ù[ù¬àK[X€\À]ô\ú⁄[€ãXXÿŸ[ù\ôÿéçMÀçMKå»Z[\‹ù[ù¬àõ‹ô\ãX€€‹éúôÿòJMçMKååéMäHZ[\‹ù[ù¬àòX⁄Ÿ‹õ›[ôõ[ôX\ãY‹òYY[ù
NYÀôÿòJKçãåãéNJH	KôÿòJãåÀééNJHL	JHZ[\‹ù[ù¬à€€‹éàŸôôàZ[\‹ù[ù¬àõﬁ\⁄Y›Œå\ôÿòJMÀçMKåÀéMJKL‹ôÿòJMÀçMKåÀçŒ
KçôÿòJMÀåLçMKçN
K‹\ôÿòJçJK[úŸ]LôÿòJMÀçMKåÀååäHZ[\‹ù[ù¬à[ö[X][€éõX€\’ô\ú⁄[€ï\]Sô[€àKé»X\ŸKZ[ã[›][ôö[ö]HZ[\‹ù[ù¬àBàYYXH
ôYô\úÀ\ôYXŸY[[›[€éúôYXŸJH¬à…’ëTî“S”ó‘’UTÀòù]€íYVŸ]K\›]OHù\]HóH¬à[ö[X][€éõõ€ôHZ[\‹ù[ù¬àõﬁ\⁄Y›Œå‹ôÿòJMÀçMKåÀJKNôÿòJMÀçMKåÀéJKÃôÿòJMÀåLçMKç K‹\ôÿòJçJK[úŸ]LúôÿòJMÀçMKåÀåé
HZ[\‹ù[ù¬àBàBà¬à
ÿ›[Y[ùöXYÿ›[Y[ùôÿ›[Y[ù[[Y[ù
Kò\[ô⁄[
›[JN¬àBàù[ò›[€àô\ú⁄[€î›]\”‹[ä
H»€€ú›‹[ôYHYŸU⁄[ô›Àõ‹[äëTî“S”ó‘’UTÀúõŸX›\õ	◊ÿõ[ö…À	€õ€‹[ô\ãõ‹ôYô\úô\â N»ûH»Yà
‹[ôY
H‹[ôYõ‹[ô\àHù[»Hÿ]⁄
\úäHﬂHBàù[ò›[€à[ú›\ôUô\ú⁄[€î›]\–ù]€ä
H¬à[ú›\ôUô\ú⁄[€î›]\‘›[J
N¬à[ú›\ôUô\ú⁄[€î›]\–[\ù›[J
N¬à€€ú›€€ùõ€Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬à€€ú›õ›»H€€ùõ€Àú]Y\ûTŸ[X›‹èÀä	ÀõX€\À[][ò⁄\õ›… N¬àYà
X€€ùõ€\õ› Hô]\õàù[¬à]ù]€àHÿ›[Y[ùôŸ][[Y[ùûRY
ëTî“S”ó‘’UTÀòù]€íY
N¬àYà
ù]€à	âàX€€ùõ€ò€€ùZ[ú ù]€äJH»ù[ù[YU[õ\›[ï\ôŸ]
ù]€ãùYJN»ù]€ãúô[[›ôJ
N»ù]€àHù[»BàYà
Xù]€äH¬àù]€àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿù]€â N¬àù]€ãöYHëTî“S”ó‘’UTÀòù]€íY¬àù]€ãù\HH	ÿù]€âŒ¬àù]€ãò€\‹”ò[YHH	€X€\À]ô\ú⁄[€ãXùàX€\À]ô\ú⁄[€ãXùãK][öYöYY	Œ¬àù]€ãô]\Ÿ]ùò\öX[ùH	ÿ€€ùõ€Yò[Z[IŒ¬àù]€ãúŸ]]öXù]J	ÿ\öXK[]ôIÀ	‹€]I N¬à€€ú›X€€õ€^HHõ›Àú]Y\ûTŸ[X›‹èÀä	ÀõX€\ÀYX€€õ€^KXùâ Hù[¬àõ›Àö[úŸ\ùôYõ‹ôJù]€ãX€€õ€^JN¬àù[ù[YS\›[äù]€ã	ÿ€X⁄…À]ô[ùOà¬à]ô[ùúô]ô[ùYò][

N¬àYà
ô\ú⁄[€î›]\‘›\ô\‹–€X⁄ H»ô\ú⁄[€î›]\‘›\ô\‹–€X⁄»Hò[ŸN»ô]\õé»BàYà
]ô[ùú⁄YùŸ^JH»ÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ùYJN»ô]\õé»Bàô\ú⁄[€î›]\”‹[ä
N¬àJN¬àù[ù[YS\›[äù]€ã	ÿ€€ù^Y[ùIÀ]ô[ùOà»]ô[ùúô]ô[ùYò][

N»ÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ùYJN»JN¬àù[ù[YS\›[äù]€ã	‹⁄[ù\ô›€âÀ]ô[ùOà¬àYà
]ô[ùú⁄[ù\ï\HOOH	€[›\ŸI Hô]\õé¬àù[ù[YP€X\ï[Y[›]
ô\ú⁄[€î›]\”€ô‘ô\‹’[Y\äN¬àô\ú⁄[€î›]\”€ô‘ô\‹’[Y\àHù[ù[YTŸ][Y[›]


HOà¬àô\ú⁄[€î›]\‘›\ô\‹–€X⁄»HùYN¬àÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ùYJN¬à⁄›’ÿ\›
	–⁄X⁄⁄[ô»€€⁄]ô\ú⁄[€∏†)â N¬àKëTî“S”ó‘’UTÀõ€ô‘ô\‹”\ N¬àJN¬àõ‹à
€€ú›]ô[ùò[YHŸà…‹⁄[ù\õ[›ôIÀ	‹⁄[ù\ù\	À	‹⁄[ù\òÿ[òŸ[	◊JH¬àù[ù[YS\›[äù]€ã]ô[ùò[YK

HOà¬àù[ù[YP€X\ï[Y[›]
ô\ú⁄[€î›]\”€ô‘ô\‹’[Y\äN¬àô\ú⁄[€î›]\”€ô‘ô\‹’[Y\àHù[¬àK»\‹⁄]ôNàùYHJN¬àBàBàô\ú⁄[€î›]\‘ô[ô\ä
N¬àYà
]ô\ú⁄[€î›]\“Yò][€îõ€Z\ŸJHõ⁄YYò]Uô\ú⁄[€î›]\ 
N¬àYà
]ô\ú⁄[€î›]\“[ö]X[⁄X⁄‘]Y]YY	âàô\ú⁄[€î›]\’[Y\àOOHù[	âà]ô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸJH¬àô\ú⁄[€î›]\“[ö]X[⁄X⁄‘]Y]YYHùYN¬à]Y]YSZX‹õ›\⁄ 

HOà¬àô\ú⁄[€î›]\“[ö]X[⁄X⁄‘]Y]YYHò[ŸN¬àYà
\ù[ù[YKô\›õﬁYY	âàÿ›[Y[ùùö\⁄Xö[]T›]HOOH	⁄Y[â»	âàù]€èÀö\–€€õôX›Y	âà€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
H	âàô\ú⁄[€î›]\’[Y\àOOHù[	âà]ô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸJH¬àÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ëTî“S”ó‘’UTÀòõ€›[^S\Àò[ŸJN¬àBàJN¬àBàô]\õàù]€é¬àBà\ﬁ[ò»ù[ò›[€àYò]Uô\ú⁄[€î›]\ 
H»Yà
ô\ú⁄[€î›]\“Yò][€îõ€Z\ŸJHô]\õàô\ú⁄[€î›]\“Yò][€îõ€Z\ŸN»ô\ú⁄[€î›]\“Yò][€îõ€Z\ŸHH
\ﬁ[ò»

HOà»€€ú›õ›»H]Kõõ› 
N»€€ú›ÿX⁄HH]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸTôXY
ëTî“S”ó‘’UTÀòÿX⁄RŸ^JN»Yà
ô\ú⁄[€î›]\–ÿX⁄R\—úô\⁄
ÿX⁄Kõ› JH»€€ú›X[öYô\›Hô\ú⁄[€î›]\’ò[Y]SX[öYô\›
ÿX⁄KõX[öYô\›
N»ô\ú⁄[€î›]\”[Ÿ[H»›]Nàô\ú⁄[€î›]\‘ô\Ÿ[ù][€ä–‘íTùô\ú⁄[€ãX[öYô\›
Kú›]KX[öYô\›⁄X⁄ŸY]àù[Xô\äÿX⁄Kò⁄X⁄ŸY]
K\úõ‹éà	…»N»ô\ú⁄[€î›]\‘ô[ô\ä
N»ô]\õé»H€€ú›òZ[\ôHH]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸTôXY
ëTî“S”ó‘’UTÀôòZ[\ôRŸ^JN»Yà
ô\ú⁄[€î›]\—òZ[\ôP€€€[ô òZ[\ôKõ› JH»ô\ú⁄[€î›]\”[Ÿ[H»›]Nà	Ÿ\úõ‹âÀX[öYô\›àù[⁄X⁄ŸY]àòZ[Y]àù[Xô\äòZ[\ôKôòZ[Y]
Hõ›À\úõ‹éà	ÿ€€€›€â»N»ô\ú⁄[€î›]\‘ô[ô\ä
N»HJJ
Kôö[ò[J

HOà»ô\ú⁄[€î›]\“Yò][€îõ€Z\ŸHHù[»JN»ô]\õàô\ú⁄[€î›]\“Yò][€îõ€Z\ŸN»Bàù[ò›[€àô\ú⁄[€î›]\‘ô\]Y\›X[öYô\›

H¬à€€ú›ô\]Y\›⁄Ÿ[àH
 ›ô\ú⁄[€î›]\‘ô\]Y\›⁄Ÿ[é¬àô]\õàô]»õ€Z\ŸJ
ô\€€ôKôZôX›
HOà¬à]Ÿ]YHò[ŸN¬à][Y[›][Y\àHù[¬à]ô\]Y\›[ôHHù[¬à€€ú›ö[ö\⁄H
\úõ‹ã^
HOà¬àYà
Ÿ]Y
Hô]\õé¬àŸ]YHùYN¬àù[ù[YP€X\ï[Y[›]
[Y[›][Y\äN¬àYà
ô\]Y\›[ôOÀòXõ‹ù
Hù[ù[YKúô\]Y\›œÀô[]OÀäô\]Y\›[ôJN¬àYà
ô\]Y\›[ôJHù[ù[YKôô]⁄€€ùõ€\úœÀô[]OÀäô\]Y\›[ôJN¬àYà
ô\ú⁄[€î›]\‘ô\]Y\›OOHô\]Y\›[ôJHô\ú⁄[€î›]\‘ô\]Y\›Hù[¬àYà
ù[ù[YKô\›õﬁYYô\]Y\›⁄Ÿ[àOOHô\ú⁄[€î›]\‘ô\]Y\›⁄Ÿ[äH¬àôZôX›
ô]»\úõ‹ä	’ô\ú⁄[€à⁄X⁄»ÿ\»›\\úŸYYâ JN¬àô]\õé¬àBàYà
\úõ‹äH»ôZôX›
\úõ‹äN»ô]\õé»BàûH»ô\€€ôJô\ú⁄[€î›]\’ò[Y]SX[öYô\›
î””ãú\úŸJ›ö[ô ^	… JJJN»Bàÿ]⁄
\úäH»ôZôX›
\úà[ú›[òŸ[Ÿà\úõ‹à»\úààô]»\úõ‹ä	’ô\ú⁄[€àX[öYô\›\»[ùò[Yâ JN»BàN¬à€€ú›\õH	’ëTî“S”ó‘’UTÀõX[öYô\›\õOÿÿX⁄Wÿù\›I—]Kõõ› 
_KI‹ô\]Y\›⁄Ÿ[üX¬àYà
\[Ÿà”Wﬁ[ô\]Y\›OOH	Ÿù[ò›[€â H¬àûH¬àô\]Y\›[ôHH”Wﬁ[ô\]Y\›
¬àY]Ÿà	——U	Àà\õà[Y[›]àëTî“S”ó‘’UTÀúô\]Y\›[Y[›]\Ààô\‹€úŸU\Nà	›^	ÀàXY\úŒà»XÿŸ\à	ÿ\Xÿ][€ã⁄ú€€âÀ	–ÿX⁄KP€€ùõ€	Œà	€õÀXÿX⁄I»Kà€õÿYàô\‹€úŸHOàù[Xô\äô\‹€úŸOÀú›]\ HèHå	âàù[Xô\äô\‹€úŸOÀú›]\ HÃà»ö[ö\⁄
ù[ô\‹€úŸKúô\‹€úŸU^
Bààö[ö\⁄
ô]»\úõ‹äô\ú⁄[€à[ô⁄[ùô]\õôY	‹ô\‹€úŸOÀú›]\»	Ÿ\úõ‹âﬂKò
JKà€ô\úõ‹éà

HOàö[ö\⁄
ô]»\úõ‹ä	’ô\ú⁄[€à[ô⁄[ù€›[õ›ôHôXX⁄Yâ JKà€ù[Y[›]à

HOàö[ö\⁄
ô]»\úõ‹ä	’ô\ú⁄[€à⁄X⁄»[YY›]â JKà€òXõ‹ùà

HOàö[ö\⁄
ô]»\úõ‹ä	’ô\ú⁄[€à⁄X⁄»ÿ\»ÿ[òŸ[Yâ JKàJN¬àô\ú⁄[€î›]\‘ô\]Y\›Hô\]Y\›[ôN¬àYà
ô\]Y\›[ôOÀòXõ‹ù
Hù[ù[YKúô\]Y\›œÀòYÀäô\]Y\›[ôJN¬àHÿ]⁄
\úäH»ö[ö\⁄
\úäN»Bàô]\õé¬àBà€€ú›€€ùõ€\àHYŸU⁄[ô›ÀêXõ‹ù€€ùõ€\à€ÿò[\ÀêXõ‹ù€€ùõ€\é¬à€€ú›€€ùõ€\àH\[Ÿà€€ùõ€\àOOH	Ÿù[ò›[€â»»ô]»€€ùõ€\ä
Hàù[¬àô\]Y\›[ôHH€€ùõ€\é¬àô\ú⁄[€î›]\‘ô\]Y\›H€€ùõ€\é¬àYà
€€ùõ€\äHù[ù[YKôô]⁄€€ùõ€\úœÀòYÀä€€ùõ€\äN¬à[Y[›][Y\àHù[ù[YTŸ][Y[›]


HOà€€ùõ€\èÀòXõ‹ùÀä
KëTî“S”ó‘’UTÀúô\]Y\›[Y[›]\ N¬àõ€Z\ŸKúô\€€ôJ
YŸU⁄[ô›Àôô]⁄€ÿò[\Àôô]⁄
Kòÿ[
YŸU⁄[ô›À\õ¬àÿX⁄Nà	€õÀ\›‹ôIÀà‹ôY[ùX[Œà	€€Z]	Àà⁄Y€ò[à€€ùõ€\èÀú⁄Y€ò[àXY\úŒà»XÿŸ\à	ÿ\Xÿ][€ã⁄ú€€âÀ	–ÿX⁄KP€€ùõ€	Œà	€õÀXÿX⁄I»KàJJBàù[äô\‹€úŸHOà¬àYà
\ô\‹€úŸKõ⁄ Hõ›»ô]»\úõ‹äô\ú⁄[€à[ô⁄[ùô]\õôY	‹ô\‹€úŸKú›]\ﬂKò
N¬àô]\õàô\‹€úŸKù^

N¬àJBàù[ä^Oàö[ö\⁄
ù[^
JBàòÿ]⁄
\úõ‹àOàö[ö\⁄
\úõ‹à[ú›[òŸ[Ÿà\úõ‹à»\úõ‹ààô]»\úõ‹ä	’ô\ú⁄[€à[ô⁄[ù€›[õ›ôHôXX⁄Yâ JJN¬àJN¬àBà\ﬁ[ò»ù[ò›[€àù[ïô\ú⁄[€î›]\–⁄X⁄ õ‹òŸHHò[ŸJH¬à[ú›\ôUô\ú⁄[€î›]\–ù]€ä
N¬àYà
ô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸJHô]\õàô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸN¬à€€ú›[ô[ô–⁄X⁄»H
\ﬁ[ò»

HOà¬à€€ú›õ›»H]Kõõ› 
N¬àYà
Yõ‹òŸJH¬à€€ú›ÿX⁄HH]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸTôXY
ëTî“S”ó‘’UTÀòÿX⁄RŸ^JN¬àYà
ô\ú⁄[€î›]\–ÿX⁄R\—úô\⁄
ÿX⁄Kõ› JH¬à€€ú›X[öYô\›Hô\ú⁄[€î›]\’ò[Y]SX[öYô\›
ÿX⁄KõX[öYô\›
N¬àô\ú⁄[€î›]\”[Ÿ[H»›]Nàô\ú⁄[€î›]\‘ô\Ÿ[ù][€ä–‘íTùô\ú⁄[€ãX[öYô\›
Kú›]KX[öYô\›⁄X⁄ŸY]àù[Xô\äÿX⁄Kò⁄X⁄ŸY]
KòZ[Y]à\úõ‹éà	…»N¬àô\ú⁄[€î›]\‘ô[ô\ä
N¬àô]\õàô\ú⁄[€î›]\”[Ÿ[¬àBà€€ú›òZ[\ôHH]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸTôXY
ëTî“S”ó‘’UTÀôòZ[\ôRŸ^JN¬àYà
ô\ú⁄[€î›]\—òZ[\ôP€€€[ô òZ[\ôKõ› JH¬àYà
]ô\ú⁄[€î›]\”[Ÿ[õX[öYô\›V…€]\›	À	›\]I◊Kö[ò€Y\ ô\ú⁄[€î›]\”[Ÿ[ú›]JJH¬àô\ú⁄[€î›]\”[Ÿ[H»›]Nà	Ÿ\úõ‹âÀX[öYô\›àù[⁄X⁄ŸY]àòZ[Y]àù[Xô\äòZ[\ôKôòZ[Y]
Hõ›À\úõ‹éà	ÿ€€€›€â»N¬àô\ú⁄[€î›]\‘ô[ô\ä
N¬àBàô]\õàô\ú⁄[€î›]\”[Ÿ[¬àBàBà€€ú›ô]ö[›\’ô\öYöYYHô\ú⁄[€î›]\”[Ÿ[õX[öYô\›	âà…€]\›	À	›\]I◊Kö[ò€Y\ ô\ú⁄[€î›]\”[Ÿ[ú›]JBà»»ããùô\ú⁄[€î›]\”[Ÿ[Bààù[¬àYà
\ô]ö[›\’ô\öYöYY
H¬àô\ú⁄[€î›]\”[Ÿ[H»›]Nà	ÿ⁄X⁄⁄[ô…ÀX[öYô\›àù[⁄X⁄ŸY]àòZ[Y]à\úõ‹éà	…»N¬àô\ú⁄[€î›]\‘ô[ô\ä
N¬àBàûH¬à€€ú›X[öYô\›H]ÿZ]ô\ú⁄[€î›]\‘ô\]Y\›X[öYô\›

N¬à€€ú›⁄X⁄ŸY]H]Kõõ› 
N¬à€€ú›ô\Ÿ[ù][€àHô\ú⁄[€î›]\‘ô\Ÿ[ù][€ä–‘íTùô\ú⁄[€ãX[öYô\›
N¬àô\ú⁄[€î›]\”[Ÿ[H»›]Nàô\Ÿ[ù][€ãú›]KX[öYô\›⁄X⁄ŸY]òZ[Y]à\úõ‹éà	…»N¬à]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸU‹ö]JëTî“S”ó‘’UTÀòÿX⁄RŸ^K»⁄X⁄ŸY]X[öYô\›JN¬à]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸQ[]JëTî“S”ó‘’UTÀôòZ[\ôRŸ^JN¬àHÿ]⁄
\úäH¬àYà
›ö[ô \úèÀõY\‹ÿYŸH\úäHOOH	’ô\ú⁄[€à⁄X⁄»ÿ\»›\\úŸYYâ Hô]\õàô\ú⁄[€î›]\”[Ÿ[¬à€€ú›òZ[Y]H]Kõõ› 
N¬à€€ú›\úõ‹àH›ö[ô \úèÀõY\‹ÿYŸH\úà	ŸòZ[Y	 N¬àô\ú⁄[€î›]\”[Ÿ[Hô]ö[›\’ô\öYöYYà»»ããúô]ö[›\’ô\öYöYYòZ[Y]\úõ‹àBàà»›]Nà	Ÿ\úõ‹âÀX[öYô\›àù[⁄X⁄ŸY]àòZ[Y]\úõ‹àN¬à]ÿZ]ô\ú⁄[€î›]\‘›‹òYŸU‹ö]JëTî“S”ó‘’UTÀôòZ[\ôRŸ^K»òZ[Y]JN¬àBàô\ú⁄[€î›]\‘ô[ô\ä
N¬àô]\õàô\ú⁄[€î›]\”[Ÿ[¬àJJ
N¬à€€ú›òX⁄ŸY⁄X⁄»H[ô[ô–⁄X⁄Àôö[ò[J

HOà¬àYà
ô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸHOOHòX⁄ŸY⁄X⁄ Hô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸHHù[¬àJN¬àô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸHHòX⁄ŸY⁄X⁄Œ¬àô]\õàòX⁄ŸY⁄X⁄Œ¬àBàù[ò›[€àô\ú⁄[€î›]\–]]€X]X—[^Jõ›»H]Kõõ› 
JH¬à€€ú››\úô[ùHù[Xô\äõ› H]Kõõ› 
N¬à€€ú›òZ[Y]Hù[Xô\äô\ú⁄[€î›]\”[Ÿ[ôòZ[Y]
H¬àYà
òZ[Y]à
H¬à€€ú›[\ŸYHX]õX^
›\úô[ùHòZ[Y]
N¬àô]\õàX]õX^
LëTî“S”ó‘’UTÀôòZ[\ôP€€€›€ì\»HX]õZ[äëTî“S”ó‘’UTÀôòZ[\ôP€€€›€ì\À[\ŸY
JN¬àBà€€ú›⁄X⁄ŸY]Hù[Xô\äô\ú⁄[€î›]\”[Ÿ[ò⁄X⁄ŸY]
H¬àYà
⁄X⁄ŸY]à	âàô\ú⁄[€î›]\”[Ÿ[õX[öYô\›
H¬à€€ú›[\ŸYHX]õX^
›\úô[ùH⁄X⁄ŸY]
N¬àô]\õàX]õX^
LëTî“S”ó‘’UTÀòÿX⁄S\»HX]õZ[äëTî“S”ó‘’UTÀòÿX⁄S\À[\ŸY
JN¬àBàô]\õàëTî“S”ó‘’UTÀò]]“[ù\ùò[\Œ¬àBàù[ò›[€àÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ [^HHëTî“S”ó‘’UTÀòõ€›[^S\Àõ‹òŸHHò[ŸJH¬àYà
ù[ù[YKô\›õﬁYY]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JH¬à\‹‹ŸUô\ú⁄[€î›]\ 
N¬àô]\õé¬àBà[ú›\ôUô\ú⁄[€î›]\–ù]€ä
N¬àYà
ô\ú⁄[€î›]\’[Y\àOOHù[
H¬àYà
Yõ‹òŸH	âàù[Xô\ä[^JHOOHëTî“S”ó‘’UTÀòõ€›[^S\ Hô]\õé¬àù[ù[YP€X\ï[Y[›]
ô\ú⁄[€î›]\’[Y\äN¬àBàô\ú⁄[€î›]\’[Y\àHù[ù[YTŸ][Y[›]
\ﬁ[ò»

HOà¬àô\ú⁄[€î›]\’[Y\àHù[¬àYà
ù[ù[YKô\›õﬁYY]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JH¬à\‹‹ŸUô\ú⁄[€î›]\ 
N¬àô]\õé¬àBàYà
Yõ‹òŸH	âàÿ›[Y[ùùö\⁄Xö[]T›]HOOH	⁄Y[â Hô]\õé¬àûH¬à]ÿZ]ù[ïô\ú⁄[€î›]\–⁄X⁄ õ‹òŸJN¬àHö[ò[H¬àYà
\ù[ù[YKô\›õﬁYY	âà€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
H	âàÿ›[Y[ùùö\⁄Xö[]T›]HOOH	⁄Y[â H¬àÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ô\ú⁄[€î›]\–]]€X]X—[^J
Kò[ŸJN¬àBàBàKX]õX^
ù[Xô\ä[^JH
JN¬àBàù[ò›[€à\‹‹ŸUô\ú⁄[€î›]\ 
H»ù[ù[YP€X\ï[Y[›]
ô\ú⁄[€î›]\’[Y\äN»ù[ù[YP€X\ï[Y[›]
ô\ú⁄[€î›]\”€ô‘ô\‹’[Y\äN»ô\ú⁄[€î›]\’[Y\àHù[»ô\ú⁄[€î›]\”€ô‘ô\‹’[Y\àHù[»ô\ú⁄[€î›]\“[ö]X[⁄X⁄‘]Y]YYHò[ŸN»ô\ú⁄[€î›]\‘ô\]Y\›⁄Ÿ[à
œHN»ûH»ô\ú⁄[€î›]\‘ô\]Y\›ÀòXõ‹ùÀä
N»Hÿ]⁄
\úäHﬂHô\ú⁄[€î›]\‘ô\]Y\›Hù[»ô\ú⁄[€î›]\–⁄X⁄‘õ€Z\ŸHHù[»€€ú›ù]€àHÿ›[Y[ùôŸ][[Y[ùûRY
ëTî“S”ó‘’UTÀòù]€íY
N»ù[ù[YU[õ\›[ï\ôŸ]
ù]€ãùYJN»ù]€èÀúô[[›ôJ
N»ÿ›[Y[ùôŸ][[Y[ùûRY
ëTî“S”ó‘’UTÀú›[RY
OÀúô[[›ôJ
N»ÿ›[Y[ùú]Y\ûTŸ[X›‹ä…’ëTî“S”ó‘’UTÀò[\ù›[RYX
OÀúô[[›ôJ
N»BÇàù[ò›[€à‹ôX]P€X[ë^]

H¬àYà
]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JHô]\õàù[¬àYà
ÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€X[ë^]Y
JHô]\õé¬à€€ú›ù]€àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿù]€â N¬àù]€ãöYH–‘íTò€X[ë^]Y¬àù]€ãù\HH	ÿù]€âŒ¬àù]€ãù^€€ù[ùH	—^]€X[à[ŸIŒ¬àù]€ãù]HH	—^]€X[à[ŸKà⁄‹ù›]à»‹à\ÿÀâŒ¬àù]€ãòY]ô[ù\›[ô\ä	ÿ€X⁄…À

HOàŸŸ€QôX]\ôJ	ÿ€X[â JN¬àÿ›[Y[ùòõŸKò\[ô⁄[
ù]€äN¬àBÇàù[ò›[€à‹ôX]P€€ùõ€
X\[
H¬à€€ú›ö[X\ûSX\H€€⁄]ö[X\ûSX\[[Y[ù
X\[ÿ›[Y[ù
N¬à€€ú›‹›H€€⁄]€€ùõ€‹›
ö[X\ûSX\ÿ›[Y[ù
N¬àYà
Z‹›
Hô]\õàù[¬à€€ú›^\›[ô»Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬àYà
^\›[ô H¬àYà
^\›[ôÀú\ô[ù[[Y[ùOOH‹›
H‹›ò\[ô⁄[
^\›[ô N¬à^\›[ôÀò€\‹”\›úô[[›ôJ	€X€\ÀX€€ùõ€Yò[òX⁄… N¬à€€⁄]\P€€[X[ôò\î›]J^\›[ô N¬àô]\õà^\›[ôŒ¬àBà€€ú›€€ùõ€Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à€€ùõ€öYH–‘íTò€€ùõ€Y¬à€€ùõ€ò€\‹”ò[YHH	€X€\ÀX€€ùõ€	Œ¬à€€ùõ€úŸ]]öXù]J	ÿ\öXK[Xô[	À	‘–‘íTõò[Y_H€€ùõ€
N¬à€€ùõ€ö[õô\íSHà]à€\‹œHõX€\À[][ò⁄\õ›»èÇà]à€\‹œHõX€\À\⁄[èÇàù]€à€\‹œHõX€\À[Y[ùKXùàà\OHòù]€àà]OHì‹[à‹à€‹ŸHX\€€[X[ô€€⁄]à⁄‹ù›]àHà\öXK[Xô[Hì‹[à‹à€‹ŸHX\€€[X[ô€€⁄]à\öXKZŸ^\⁄‹ù›]œHìHà\öXKY^[ôYHôò[ŸHà\öXKX€€ùõ€œHâ‘–‘íTú[ô[YHèÇà‹[à€\‹œHõX€\À[Y[ùKZX€€àà\öXKZY[èHùùYHè∏•„è‹‹[èÇà‹[à€\‹œHõX€\À[Y[ùK[Xô[èìQSïO‹‹[èÇà‹[à€\‹œHõX€\À[Y[ùKZŸ^HèìO‹‹[èÇàÿù]€èÇàŸ]èÇàŸ]èÇà]à€\‹œHõX€\ÀYõÿ][ôÀYö[\àà\öXK[Xô[Hî\ú⁄\›[ùX\€€[X[ôò\àèÇà]à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\à]KX€€ùõ€Y‹õ›\Hùö\⁄Xö[]Hà\öXK[Xô[Hïö\⁄Xö[]H€€ùõ€»èÇà‹[à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\[Xô[èïö\⁄Xö[]O‹‹[èÇà	€XZŸQõÿ]ù]€ä	€^SZ\‹⁄[€ú…À	ÃIÀ	‘\ú€€ò[	À	‘⁄›À⁄YH€€ôöY[ùH]X›Y\ú€€ò[Z\‹⁄[€úÀà⁄‹ù›]àIÀ	‘\ú€€ò[	À	”Z[ôI _Bà	€XZŸQõÿ]ù]€ä	ÿ[X[òŸSZ\‹⁄[€ú…À	ÃâÀ	–[X[òŸIÀ	‘⁄›À⁄YH€€ôöY[ùH]X›Y[X[òŸHZ\‹⁄[€úÀà⁄‹ù›]àâÀ	–[X[òŸIÀ	–[I _Bà	€XZŸQõÿ]ù]€ä	›ôZX€\…À	Ã…À	’ôZX€\…À	‘⁄›À⁄YH€€ôöY[ùH]X›YôZX€\Àà⁄‹ù›]à…À	’ôZX€\…À	’[ö]… _Bà	€XZŸQõÿ]ù]€ä	ÿùZ[[ô‹…À	Õ	À	–ùZ[[ô‹…À	‘⁄›À⁄YH€€ôöY[ùH]X›YùZ[[ô‹À‹›][€úÀà⁄‹ù›]à	À	–ùZ[[ô‹…À	–õ‹… _BàŸ]èÇà]à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\à]KX€€ùõ€Y‹õ›\Hö[ù[YŸ[òŸHà\öXK[Xô[Hí[ù[YŸ[òŸH€€ùõ€»èÇà‹[à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\[Xô[èí[ù[YŸ[òŸO‹‹[èÇà	€XZŸQõÿ]ù]€ä	ÿ[X[òŸP‹ôY]…À	ÕIÀ	–[H‹ôY]…À	‘⁄›À⁄YH\õﬁ[X]H‹ôY]ò[Y\»ô\⁄YH[X[òŸHZ\‹⁄[€àX\öŸ\úÀà⁄‹ù›]àIÀ	–[H‹ôY]…À	–[H0®… _Bà	€XZŸQõÿ]ù]€ä	€Z\‹⁄[€êYŸIÀ	ÕâÀ	”Z\‹⁄[€àYŸIÀ	‘⁄›»\ú€€ò[Z\‹⁄[€àYŸH⁄]õŸ‹ô\‹⁄]ôH[Xô\ãMí‹ò[ôŸH[ôçôYŸ]ô\ö]Kà⁄‹ù›]àâÀ	”Z\‹⁄[€àYŸIÀ	–YŸI _Bà	€XZŸQõÿ]ù]€ä	›ò[ú‹‹ùÿ]⁄\âÀ	Õ…À	’ò[ú‹‹ù	À	‘⁄›À⁄YH[Xô\àò[ú‹‹ù\ô\]Z\ôYÿ]⁄\ú»ô\⁄YHZ\‹⁄[€úÀà⁄‹ù›]à…À	’ò[ú‹‹ù	À	’ò[ú… _Bà	€XZŸQõÿ]ù]€ä	›[ö]€€[Z]Y[ù	À	Œ	À	’[ö]€›[ù	À	‘⁄›»[›\à€€[Z]Y[ö]»ô\⁄YHZ\‹⁄[€úÀà⁄‹ù›]à	À	’[ö]€›[ù	À	–€›[ù	 _Bà	€XZŸQõÿ]ù]€ä	‹›X⁄—]X›‹âÀ	…À	‘›X⁄…À	‘⁄›À⁄YH›X⁄»Z\‹⁄[€àXô[»⁄[àõ»YX[ö[ôŸù[õŸ‹ô\‹»\»]X›YâÀ	‘›X⁄…À	‘›X⁄… _BàŸ]èÇà]à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\à]KX€€ùõ€Y‹õ›\Hô\⁄õÿ\ôà\öXK[Xô[Hë\⁄õÿ\ô€€ùõ€»èÇà‹[à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\[Xô[èë\⁄õÿ\ô‹‹[èÇà	€XZŸPX›[€ëõÿ]ù]€ä	€‹[ã]ôZX€K\›]\…À	’âÀ	’ôZX€H€Ÿ\…À	”‹[à‹à€‹ŸHôZX€H€ŸH›]\Àà⁄‹ù›]àâÀ	’ôZX€H€Ÿ\…À	–€Ÿ\… _Bà	€XZŸPX›[€ëõÿ]ù]€ä	€‹[ã\ô\‹›\ôKXõÿ\ô	À	–âÀ	‘ô\‹›\ôHõÿ\ô	À	”‹[à‹à€‹ŸHH‹\ò][€ò[ô\‹›\ôHõÿ\ôà⁄‹ù›]àâÀ	‘ô\‹›\ôHõÿ\ô	À	‘ô\‹›\ôIÀ	‹ô\‹›\ôPõÿ\ô	 _Bà	€XZŸPX›[€ëõÿ]ù]€ä	€‹[ãX€€[X[ô\[]IÀ	“…À	–€€[X[ô[]IÀ	‘ŸX\ò⁄Z\‹⁄[€úÀôZX€\ÀùZ[[ô‹Àÿÿ][€úÀŸ][ô‹»[ô€€⁄]€€[X[ôÀà⁄‹ù›]à…À	‘[]IÀ	‘ŸX\ò⁄	À	ÿ€€[X[ô[]I _Bà	€XZŸPX›[€ëõÿ]ù]€ä	€‹[ã[X\[YX\›\ôIÀ	…À	—ò]⁄[ô…À	–X›]ò]Hò]⁄[ô»€àHX\àõ»\›[ô\à‹à^Y\à^\›»[ù[‹[ôYâÀ	—ò]⁄[ô…À	—ò]…À	€YX\›\ôI _BàŸ]èÇà]à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\à]KX€€ùõ€Y‹õ›\Hú\ôõ‹õX[òŸHà\öXK[Xô[Hî\ôõ‹õX[òŸH€€ùõ€»èÇà‹[à€\‹œHõX€\ÀX€€ùõ€Y‹õ›\[Xô[èî\ôõ‹õX[òŸO‹‹[èÇàù]€à€\‹œHõX€\ÀYX€€õ€^KXùàà\OHòù]€àà]KXX›[€èHùŸŸ€KYX€€õ€^Hà]OHë[òXõHX€€õ€^H[ŸHà\öXK[Xô[Hë[òXõHX€€õ€^H[ŸHà\öXK\ô\‹ŸYHôò[ŸHèÇà‹[à€\‹œHõX€\ÀYõÿ]ZŸ^Hà\öXKZY[èHùùYHèëP”œ‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ]ZX€€àà\öXKZY[èHùùYHèâ”PT–””ïì”“P””îÀôX€€õ€^S[Ÿ_O‹‹[èÇà‹[à€\‹œHõX€\ÀYõÿ]X€‹Hèè‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[Y\⁄›‹èëX€€õ€^H[ŸO‹‹[èè‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[]Xõ]èëX€€õ€^O‹‹[èè‹[à€\‹œHõX€\ÀYõÿ][Xô[X€\ÀYõÿ][Xô[[[ÿö[HèëX€€õ€^O‹‹[èè‹[à€\‹œHõX€\ÀX€€ùõ€\›]Hèì—ëè‹‹[èè‹‹[èÇàÿù]€èÇàŸ]èÇàŸ]èÇà]à€\‹œHõX€\À\ÿ‹ôY[ã\[ú»à]OHî[õôYÿ‹ôY[à⁄‹ù›]»èèŸ]èÇà¬à…ÿ€X⁄…À	Ÿõ€X⁄…À	€[›\ŸY›€âÀ	€[›\Ÿ]\	À	‹⁄[ù\ô›€âÀ	‹⁄[ù\ù\	À	‹⁄[ù\òÿ[òŸ[	À	››X⁄›\ù	À	››X⁄[›ôIÀ	››X⁄[ô	À	›⁄Y[	À	ÿ€€ù^Y[ùI◊Kôõ‹ëXX⁄
]ô[ùò[YHOà¬à€€ùõ€òY]ô[ù\›[ô\ä]ô[ùò[YK›‹X\[ù\òX›[€ã»\‹⁄]ôNàò[ŸHJN¬àJN¬à]ÿ‹ôY[î[ì€ô‘ô\‹’[Y\àH¬à]ÿ‹ôY[î[ì€ô‘ô\‹–ù]€àHù[¬à€€ú›ÿ[òŸ[ÿ‹ôY[î[ì€ô‘ô\‹»H

HOà¬àù[ù[YP€X\ï[Y[›]
ÿ‹ôY[î[ì€ô‘ô\‹’[Y\äN¬àÿ‹ôY[î[ì€ô‘ô\‹’[Y\àH¬àÿ‹ôY[î[ì€ô‘ô\‹–ù]€àHù[¬àN¬à€€ùõ€òY]ô[ù\›[ô\ä	‹⁄[ù\ô›€âÀ]ô[ùOà¬à[ôQÿ⁄—Ÿ\›\ôT⁄[ù\ë›€ä]ô[ù
N¬à€€ú›[êù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À\ÿ‹ôY[ã\[ãXùñŸ]KYù[[Xô[KõX€\ÀYõÿ]XùãõX€\ÀYX€€õ€^KXùãõX€\À[Y[ùKXùâ N¬àYà
\[êù]€à]ô[ùú⁄[ù\ï\HOOH	€[›\ŸI Hô]\õé¬àÿ[òŸ[ÿ‹ôY[î[ì€ô‘ô\‹ 
N¬àÿ‹ôY[î[ì€ô‘ô\‹–ù]€àH[êù]€é¬àÿ‹ôY[î[ì€ô‘ô\‹’[Y\àHù[ù[YTŸ][Y[›]


HOà¬àYà
ÿ‹ôY[î[ì€ô‘ô\‹–ù]€àOOH[êù]€äHô]\õé¬à[êù]€ãô]\Ÿ]õX€\”€ô‘ô\‹»H	›ùYIŒ¬à⁄›’ÿ\›
[êù]€ãô]\Ÿ]ôù[Xô[[êù]€ãù]H[êù]€ãôŸ]]öXù]J	ÿ\öXK[Xô[	 H[êù]€ãù^€€ù[ù	’€€⁄]€€ùõ€	 N¬àKMå
N¬àJN¬à€€ùõ€òY]ô[ù\›[ô\ä	‹⁄[ù\õ[›ôIÀÿ[òŸ[ÿ‹ôY[î[ì€ô‘ô\‹À»\‹⁄]ôNàùYHJN¬à€€ùõ€òY]ô[ù\›[ô\ä	‹⁄[ù\òÿ[òŸ[	À

HOà»ÿ⁄—Ÿ\›\ôT›\ùHù[»ÿ[òŸ[ÿ‹ôY[î[ì€ô‘ô\‹ 
N»K»\‹⁄]ôNàùYHJN¬à€€ùõ€òY]ô[ù\›[ô\ä	‹⁄[ù\ù\	À]ô[ùOà¬àÿ⁄—Ÿ\›\ôP€€ú›[YYH[ôQÿ⁄—Ÿ\›\ôT⁄[ù\ï\
]ô[ù
N¬àù[ù[YP€X\ï[Y[›]
ÿ‹ôY[î[ì€ô‘ô\‹’[Y\äN¬àÿ‹ôY[î[ì€ô‘ô\‹’[Y\àH¬àÿ‹ôY[î[ì€ô‘ô\‹–ù]€àHù[¬àK»\‹⁄]ôNàò[ŸHJN¬à€€ùõ€òY]ô[ù\›[ô\ä	ÿ€X⁄…À]ô[ùOà¬àYà
ÿ⁄—Ÿ\›\ôP€€ú›[YY
H»ÿ⁄—Ÿ\›\ôP€€ú›[YYHò[ŸN»]ô[ùúô]ô[ùYò][

N»]ô[ùú›‹õ‹Yÿ][€ä
N»ô]\õé»Bà€€ú›Y[ùPù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À[Y[ùKXùâ N¬à€€ú›ŸŸ€Pù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]K]ŸŸ€WI N¬à€€ú›X›[€êù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]KXX›[€óI N¬à€€ú›X›]ò]Yù]€àHY[ùPù]€àŸŸ€Pù]€àX›[€êù]€é¬àYà
X›]ò]Yù]€èÀô]\Ÿ]õX€\”€ô‘ô\‹»OOH	›ùYI H¬à[]HX›]ò]Yù]€ãô]\Ÿ]õX€\”€ô‘ô\‹Œ¬à]ô[ùúô]ô[ùYò][

N¬àô]\õé¬àBàYà
Y[ùPù]€äH»ŸŸ€T[ô[

N»ô]\õé»BàYà
ŸŸ€Pù]€äH»ŸŸ€QôX]\ôJŸŸ€Pù]€ãô]\Ÿ]ùŸŸ€JN»ô]\õé»BàYà
X›[€êù]€äH[ôPX›[€äX›[€êù]€äN¬àJN¬à€€ùõ€òY]ô[ù\›[ô\ä	ÿ€€ù^Y[ùIÀ]ô[ùOà»]ô[ùúô]ô[ùYò][

N»‹[î[ô[

N»JN¬à€€⁄]\P€€[X[ôò\î›]J€€ùõ€
N¬à‹›ò\[ô⁄[
€€ùõ€
N¬à€€ùõ€ò€\‹”\›úô[[›ôJ	€X€\ÀX€€ùõ€Yò[òX⁄… N¬àô[ô\îÿ‹ôY[î[ú 
N¬à\]URJ
N¬àô]\õà€€ùõ€¬àBÇàù[ò›[€à€€[X[ôŸX›[€î€Y ò[YJH¬àô]\õà›ö[ô ò[YH	‹ŸX›[€â Kù”›Ÿ\êÿ\ŸJ
Kúô\XŸJ…ãŸ›K	»[ô	 Kúô\XŸJ÷◊òK^åNWJÀŸ›K	ÀI Kúô\XŸJ◊ã_IŸ›K	… H	‹ŸX›[€âŒ¬àBÇàù[ò›[€à€€[X[ôŸX›[€ìò]öYÿ][€ìX\ö›\

H¬àô]\õà””SPSë‘—P’S”ó”‘ëTãõX\
Ÿ^HOà¬à€€ú›Y]HH””SPSë‘—P’S”ó”QUV⁄Ÿ^WN¬àô]\õàù]€à€\‹œHõX€\À]XãXùàà\OHòù]€àà]K]XèHâ⁄Ÿ^_Hà]OHâŸ\ÿÿ\R[
Y]Kô\ÿ‹ö\[€ä_Hèè‹[à€\‹œHõX€\À]XãZX€€àà\öXKZY[èHùùYHèâ€Y]KöX€€üO‹‹[èè‹[à€\‹œHõX€\À]XãX€‹Hèè›õ€ôœâŸ\ÿÿ\R[
Y]KõXô[
_O‹›õ€ôœè€X[âŸ\ÿÿ\R[
Y]Kô\ÿ‹ö\[€ä_O‹€X[è‹‹[èèÿù]€èò¬àJKöõ⁄[ä	… N¬àBÇàù[ò›[€à€€[X[ô[ù\ôòXŸT[ô[

H¬àô]\õàÿ›[Y[ùú]Y\ûTŸ[X›‹ä⁄YHâ‘–‘íTú[ô[YHóX
N¬àBÇàù[ò›[€à‹ò\€€[X[ôŸX›[€êÿ\ô ŸX›[€äH¬àYà
\ŸX›[€àŸX›[€ãô]\Ÿ]õX€\–ÿ\ô‘ôXYHOOH	›ùYI Hô]\õé¬à€€ú›úòY€Y[ùHÿ›[Y[ùò‹ôX]Qÿ›[Y[ùúòY€Y[ù

N¬à]ÿ\ôHù[¬àõ‹à
€€ú›õŸHŸà\úò^Kôúõ€JŸX›[€ãò⁄[ô[äJH¬àYà
õŸKò€\‹”\›Àò€€ùZ[ú 	€X€\À\ŸX›[€ã[Xô[	 JH¬à€€ú›Xô[H›ö[ô õŸKù^€€ù[ù	–€€[X[ô‹õ›\	 Kùö[J
N¬à€€ú›€Y»H€€[X[ôŸX›[€î€Y Xô[
N¬àÿ\ôHÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿ\ùX€I N¬àÿ\ôò€\‹”ò[YHH	€X€\ÀX€€[X[ôXÿ\ô	Œ¬àÿ\ôô]\Ÿ]ò€€[X[ôÿ\ôH€YŒ¬àÿ\ôô]\Ÿ]ò€€[X[ôŸX\ò⁄HXô[ù”›Ÿ\êÿ\ŸJ
N¬à€€ú›XY[ô“YHX€\ÀXÿ\ôI‹ŸX›[€ãô]\Ÿ]ú[ô[KI‹€YﬂX¬àõŸKöYHXY[ô“Y¬àÿ\ôúŸ]]öXù]J	ÿ\öXK[Xô[YûIÀXY[ô“Y
N¬àYà
…ÿ€ÀXYZ[ã\]Y[ù]ò[ú‹‹ù\›ŸY\	À	Ÿ\ÿ€‹ôYö[ò[ò⁄X[X€€[X[ô	À	‹^Y\ã[[öŸY[ÿÿ[Yö[ò[ò⁄X[X\ò⁄]ôI◊Kö[ò€Y\ €Y JH¬àÿ\ôò€\‹”\›òY
	€X€\ÀX€€[X[ôXÿ\ô]⁄YI N¬àBàúòY€Y[ùò\[ô⁄[
ÿ\ô
N¬àBà
ÿ\ôúòY€Y[ù
Kò\[ô⁄[
õŸJN¬àBàŸX›[€ãò\[ô⁄[
úòY€Y[ù
N¬àŸX›[€ãô]\Ÿ]õX€\–ÿ\ô‘ôXYHH	›ùYIŒ¬àBÇàù[ò›[€à\‹òYP€€[X[ô[ù\ôòXŸJ[ô[
H¬à€€ú››X⁄ﬁHH[ô[Àú]Y\ûTŸ[X›‹ä	ÀõX€\À\[ô[\›X⁄ﬁK\›X⁄… N¬à€€ú›Xú»H›X⁄ﬁOÀú]Y\ûTŸ[X›‹ä	ÀõX€\À]Xú… N¬àYà
\[ô[\›X⁄ﬁH]Xú»[ô[ô]\Ÿ]õX€\–€€[X[ô[ù\ôòXŸHOOH	›éI Hô]\õà[ô[¬àXúÀúô\XŸP⁄[ô[ä
N¬àXúÀö[úŸ\ùYòXŸ[ùS
	ÿYù\òôY⁄[âÀ€€[X[ôŸX›[€ìò]öYÿ][€ìX\ö›\

JN¬Çà€€ú›ûSYÿXﬁSò[YHHÿöôX›ôúõ€Q[ùöY\ à\úò^Kôúõ€J[ô[ú]Y\ûTŸ[X›‹ê[
	Œúÿ€‹HàõX€\À]Xã\[ô[	 JKõX\
ŸX›[€àOà‹ŸX›[€ãô]\Ÿ]ú[ô[ŸX›[€óJBà
N¬à€€ú›ô[ò[YHH
YÿXﬁSò[YKô^ò[YJHOà¬à€€ú›ŸX›[€àHûSYÿXﬁSò[YV€YÿXﬁSò[YWN¬àYà
\ŸX›[€äHô]\õàù[¬àŸX›[€ãô]\Ÿ]ú[ô[Hô^ò[YN¬àô]\õàŸX›[€é¬àN¬à€€ú›\X\ò[òŸHHô[ò[YJ	‹⁄⁄[ú…À	ÿ\X\ò[òŸI N¬à€€ú›X\Hô[ò[YJ	›€€…À	€X\	 N¬à€€ú›Z\‹⁄[€ú»Hô[ò[YJ	‹ô\€›\òŸ\…À	€Z\‹⁄[€ú… N¬à€€ú›Z\‹⁄[€ì‹\ò][€ú»HûSYÿXﬁSò[YKõ‹Œ¬àYà
Z\‹⁄[€ú»	âàZ\‹⁄[€ì‹\ò][€ú H¬àZ\‹⁄[€úÀò\[ô
ããê\úò^Kôúõ€JZ\‹⁄[€ì‹\ò][€úÀò⁄[õŸ\ JN¬àZ\‹⁄[€ì‹\ò][€úÀúô[[›ôJ
N¬àBà€€ú›ö[ò[òŸHHô[ò[YJ	Ÿ\ÿ€‹ô	À	Ÿö[ò[òŸI N¬à€€ú›^[›]HûSYÿXﬁSò[YKú^[›]Œ¬àYà
ö[ò[òŸH	âà^[›]
H¬àö[ò[òŸKò\[ô
ããê\úò^Kôúõ€J^[›]ò⁄[õŸ\ JN¬à^[›]úô[[›ôJ
N¬àBà€€ú›ÿÿ][€ú»Hô[ò[YJ	‹XŸ\…À	€ÿÿ][€ú… N¬à€€ú›Ÿ][ô‹»HûSYÿXﬁSò[YKúŸ][ô‹Œ¬à€€ú›ŸX›[€ú»H»X\Z\‹⁄[€úÀö[ò[òŸKÿÿ][€úÀ\X\ò[òŸKŸ][ô‹»N¬Çà€€ú›^[›]Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à^[›]ò€\‹”ò[YHH	€X€\ÀX€€[X[ô[^[›]	Œ¬à€€ú›€€ù[ùHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à€€ù[ùò€\‹”ò[YHH	€X€\ÀX€€[X[ôX€€ù[ù	Œ¬à›X⁄ﬁKòYù\ä^[›]
N¬à^[›]ò\[ô
XúÀ€€ù[ù
N¬àõ‹à
€€ú›Ÿ^HŸà””SPSë‘—P’S”ó”‘ëTäH¬à€€ú›ŸX›[€àHŸX›[€ú÷⁄Ÿ^WN¬àYà
\ŸX›[€äH€€ù[ùYN¬à‹ò\€€[X[ôŸX›[€êÿ\ô ŸX›[€äN¬à€€ù[ùò\[ô⁄[
ŸX›[€äN¬àBà€€ú›[\HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à[\Kò€\‹”ò[YHH	€X€\ÀX€€[X[ô\ŸX\ò⁄Y[\IŒ¬à[\KöY[àHùYN¬à€€ú›[\RXY[ô»Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹›õ€ô… N¬à[\RXY[ôÀù^€€ù[ùH	”õ»X]⁄[ô»€€ùõ€…Œ¬à€€ú›[\Q›ZY[òŸHHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹‹[â N¬à[\Q›ZY[òŸKù^€€ù[ùH	’ûHH⁄‹ù\à€‹ô‹à⁄€‹ŸH[õ›\à€€[X[ôŸX›[€ãâŒ¬à[\Kúô\XŸP⁄[ô[ä[\RXY[ôÀ[\Q›ZY[òŸJN¬à€€ù[ùò\[ô⁄[
[\JN¬à[ô[ô]\Ÿ]õX€\–€€[X[ô[ù\ôòXŸHH	›éIŒ¬àô]\õà[ô[¬àBÇàù[ò›[€à€€[X[ô[ù\ôòXŸP\TŸX\ò⁄
[ô[H€€[X[ô[ù\ôòXŸT[ô[

JH¬àYà
\[ô[
Hô]\õà¬à€€ú›]Y\ûHH€€[X[ôŸX\ò⁄]Y\ûKùö[J
Kù”›Ÿ\êÿ\ŸJ
N¬à€€ú›X›]ôTŸX›[€àH[ô[ú]Y\ûTŸ[X›‹äõX€\À]Xã\[ô[Ÿ]K\[ô[Hâ‹›]KòX›]ôUXüHóX
N¬à€€ú›ÿ\ô»H\úò^Kôúõ€JX›]ôTŸX›[€èÀú]Y\ûTŸ[X›‹ê[
	ÀõX€\ÀX€€[X[ôXÿ\ô	 H◊JN¬à]X]⁄\»H¬àõ‹à
€€ú›ÿ\ôŸàÿ\ô H¬à€€ú›ŸX\ò⁄XõHH	ÿÿ\ôô]\Ÿ]ò€€[X[ôŸX\ò⁄	…ﬂH	ÿÿ\ôù^€€ù[ù	…ﬂXù”›Ÿ\êÿ\ŸJ
N¬à€€ú›ö\⁄XõHH\]Y\ûHŸX\ò⁄XõKö[ò€Y\ ]Y\ûJN¬à\]UZUŸŸ€P€\‹ ÿ\ô	€X€\À\ŸX\ò⁄ZY[âÀ]ö\⁄XõJN¬àYà
ö\⁄XõJHX]⁄\»
œHN¬àBà€€ú›[\HH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€[X[ô\ŸX\ò⁄Y[\I N¬à\]UZTŸ]õ‹\ùJ[\K	⁄Y[âÀ\]Y\ûHX]⁄\»à
N¬àô]\õàX]⁄\Œ¬àBÇàù[ò›[€àŸ]€€[X[ôŸX\ò⁄‹[ä‹[ã[ô[H€€[X[ô[ù\ôòXŸT[ô[

Kõÿ›\»HùYJH¬àYà
\[ô[
Hô]\õé¬à€€[X[ôŸX\ò⁄‹[àHõ€€X[ä‹[äN¬à€€ú›ò\àH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€[X[ô\ŸX\ò⁄	 N¬à€€ú›ù]€àH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À\ŸX\ò⁄Xù]€â N¬à€€ú›[ú]H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\ŸX\ò⁄I N¬àYà
ò\äHò\ãöY[àHX€€[X[ôŸX\ò⁄‹[é¬à[ô[ò€\‹”\›ùŸŸ€J	€X€\À\ŸX\ò⁄[‹[âÀ€€[X[ôŸX\ò⁄‹[äN¬àù]€èÀúŸ]]öXù]J	ÿ\öXKY^[ôY	À›ö[ô €€[X[ôŸX\ò⁄‹[äJN¬àYà
X€€[X[ôŸX\ò⁄‹[äH¬à€€[X[ôŸX\ò⁄]Y\ûHH	…Œ¬àYà
[ú]
H[ú]ùò[YHH	…Œ¬àH[ŸHYà
õÿ›\ H¬àûH»[ú]Àôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJN»Hÿ]⁄
\úäHﬂBàBà€€[X[ô[ù\ôòXŸP\TŸX\ò⁄
[ô[
N¬à\]P€€[X[ô[ù\ôòXŸRXY\ä[ô[
N¬àBÇàù[ò›[€à\]P€€[X[ô[ù\ôòXŸRXY\ä[ô[H€€[X[ô[ù\ôòXŸT[ô[

JH¬àYà
\[ô[
Hô]\õé¬à€€ú›Y]HH””SPSë‘—P’S”ó”QUV‹›]KòX›]ôUXóH””SPSë‘—P’S”ó”QUKõX\¬à€€ú›]HH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À]]I N¬à€€ú››Xù]HH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À\›Xù]I N¬à€€ú›X›]ôTŸX›[€àH[ô[ú]Y\ûTŸ[X›‹äõX€\À]Xã\[ô[Ÿ]K\[ô[Hâ‹›]KòX›]ôUXüHóX
N¬à€€ú›X›]ôQôX]\ôP€›[ùHX›]ôTŸX›[€èÀú]Y\ûTŸ[X›‹ê[
	÷Ÿ]K]ŸŸ€WKõX€\À[€ãõX€\ÀXX›[€ã]ŸŸ€KõX€\À[€â Kõ[ô›¬à€€ú›X]⁄\»H€€[X[ô[ù\ôòXŸP\TŸX\ò⁄
[ô[
N¬à\]UZTŸ]^
]K–‘íTõò[YKúô\XŸJ◊ìZ\‹⁄[€ê⁄YYó À›K	… JN¬à\]UZTŸ]^
›Xù]K€€[X[ôŸX\ò⁄]Y\ûBà»	€X]⁄\ﬂHX]⁄	€X]⁄\»OOHH»	…»à	Ÿ\…ﬂH[à	€Y]Kù]_Xàà	€Y]Kù]_H0≠»	ÿX›]ôQôX]\ôP€›[ùHôX]\ôIÿX›]ôQôX]\ôP€›[ùOOHH»	…»à	‹…ﬂHX›]ôX
N¬à€€ú›[ú]H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]KX€€[X[ô\ŸX\ò⁄I N¬à\]UZTŸ]õ‹\ùJ[ú]	‹XŸZ€\âÀŸX\ò⁄	€Y]KõXô[ù”›Ÿ\êÿ\ŸJ
_X
N¬à€€ú›Xú»H[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À]Xú… N¬à\]UZTŸ]]öXù]JXúÀ	ÿ\öXK[‹öY[ù][€âÀ[ÿö[S[ŸPX›]ôH»	⁄‹ö^õ€ù[	»à	›ô\ùXÿ[	 N¬àBÇàù[ò›[€à‹ôX]T[ô[

H¬àYà
]€€⁄]€€[X[ô⁄[€€ù^X›]ôJ
JHô]\õàù[¬à€€ú›^\›[ô‘[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
^\›[ô‘[ô[
H»Ÿ][ô‹‘[ô[X›]ò]YHùYN»ô]\õà^\›[ô‘[ô[»Bà€€ú›[ô[›\ùY]H›\ù\€ÿ⁄ 
N¬àŸ][ô‹‘[ô[X›]ò]YHùYN¬à€€ú›[ô[Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à[ô[öYH–‘íTú[ô[Y¬à[ô[úŸ]]öXù]J	‹õ€IÀ	ŸX[Ÿ… N¬à[ô[úŸ]]öXù]J	ÿ\öXK[[Ÿ[	À	Ÿò[ŸI N¬à[ô[úŸ]]öXù]J	ÿ\öXKZY[âÀ	›ùYI N¬à[ô[úŸ]]öXù]J	ÿ\öXK[Xô[	À	‘–‘íTõò[Y_HY[ùX
N¬à€€ú›ùZ[ZU[YPù]€ú»H

HOàRW’SQW”‘ëTãõX\
Ÿ^HOà¬à€€ú›[YHHRW’SQT÷⁄Ÿ^WN¬àô]\õààù]€à€\‹œHõX€\À]ZK][YKXùàà\OHòù]€àà]K]ZK][YOHâ⁄Ÿ^_Hà]OHâŸ\ÿÿ\R[
[YKô\ÿ‹ö\[€ä_Hà\öXK\ô\‹ŸYHôò[ŸHèÇà‹[à€\‹œHõX€\À]ZK][YK\ô]öY]»X€\À]ZK][YK\ô]öY]ÀI⁄Ÿ^_Hà\öXKZY[èHùùYHèè‹[èè‹‹[èè‹[èè‹‹[èè‹[èè‹‹[èè‹‹[èÇà‹[à€\‹œHõX€\À]ZK][YKX€‹Hèè›õ€ôœâŸ\ÿÿ\R[
[YKõXô[
_O‹›õ€ôœè€X[âŸ\ÿÿ\R[
[YKú⁄‹ù
_O‹€X[è‹‹[èÇàÿù]€èÇà¬àJKöõ⁄[ä	… N¬à€€ú›ùZ[[YPù]€ú»HŸ^\»OàŸ^\ÀõX\
Ÿ^HOà¬à€€ú›[YHHSQT÷⁄Ÿ^WN¬àô]\õààù]€à€\‹œHõX€\À][YKXùàà\OHòù]€àà]K][YOHâ⁄Ÿ^_Hà]OHâ›[YKôù[HèÇà‹[à€\‹œHõX€\ÀZX€€òõﬁèâ›[YKöX€€üO‹‹[èÇà‹[à€\‹œHõX€\À]^èÇà‹[à€\‹œHõX€\À[Xô[èâ›[YKõXô[O‹‹[èÇà‹[à€\‹œHõX€\À\[èâ›[YKú⁄‹ùO‹‹[èÇà‹‹[èÇàÿù]€èÇà¬àJKöõ⁄[ä	… N¬à€€ú›ZU[YPù]€ú»HùZ[ZU[YPù]€ú 
N¬à€€ú›€‹ôU[YPù]€ú»HùZ[[YPù]€ú ”‘ëW’SQW”‘ëTäN¬à€€ú›Ÿ\ùöXŸU[YPù]€ú»HùZ[[YPù]€ú —TïíP—W’SQW”‘ëTäN¬à€€ú›‹⁄][€êù]€ú»HÿöôX›ô[ùöY\ ‘“US”î KõX\

⁄Ÿ^K‹◊JHOàù]€à€\‹œHõX€\À\‹⁄][€ãXùàà\OHòù]€àà]K\‹⁄][€èHâ⁄Ÿ^_Hà]OHâ‹‹ÀõXô[Hèâ‹‹Àú⁄‹ùOÿù]€èò
Köõ⁄[ä	… N¬à[ô[ö[õô\íSHà]à€\‹œHõX€\À\[ô[\›X⁄ﬁK\›X⁄»èÇà]à€\‹œHõX€\ÀZXY\àèÇà]à€\‹œHõX€\ÀYòYÀZ[ôHà]OHí€YùX€X⁄»[ôòY»\»ò\à»[›ôHHY[ùHèÇà‹[à€\‹œHõX€\ÀZXY\ãY‹ö\à\öXKZY[èHùùYHè∏®/œ‹‹[èÇà‹[à€\‹œHõX€\ÀZXY\ãXúò[ôèÇà‹[à€\‹œHõX€\À]]HèìX\€€[X[ô€€⁄]‹‹[èÇà‹[à€\‹œHõX€\À\›Xù]HèìX\€€ùõ€œ‹‹[èÇà‹‹[èÇàŸ]èÇà]à€\‹œHõX€\ÀZXY\ãXX›[€ú»èÇàù]€à€\‹œHõX€\À\ŸX\ò⁄Xù]€àà\OHòù]€àà]KXX›[€èHùŸŸ€KX€€[X[ô\ŸX\ò⁄à]OHîŸX\ò⁄H›\úô[ù€€[X[ôŸX›[€àà\öXK[Xô[HîŸX\ò⁄H›\úô[ù€€[X[ôŸX›[€àà\öXKY^[ôYHôò[ŸHè∏£%Oÿù]€èÇàù]€à€\‹œHõX€\ÀZ[Xù]€àà\OHòù]€àà]KXX›[€èHõ‹[ãZ[XŸ[ù\àà]OHì‹[àŸX\ò⁄XõH[Ÿ[ùôHà\öXK[Xô[Hì‹[àŸX\ò⁄XõH[Ÿ[ùôHèèœÿù]€èÇàù]€à€\‹œHõX€\ÀX€‹ŸHà\OHòù]€àà]OHê€‹ŸHà\öXK[Xô[Hê€‹ŸHX\€€[X[ô€€⁄]è∞Âœÿù]€èÇàŸ]èÇàŸ]èÇà]à€\‹œHõX€\ÀX€€[X[ô\ŸX\ò⁄àY[èÇà‹[à\öXKZY[èHùùYHè∏£%O‹‹[èÇà[ú]\OHúŸX\ò⁄à[ú][ŸOHúŸX\ò⁄à]]ÿ€€\]OHõŸôàà‹[⁄X⁄œHôò[ŸHà]KX€€[X[ô\ŸX\ò⁄XŸZ€\èHîŸX\ò⁄\»ŸX›[€àà\öXK[Xô[HîŸX\ò⁄H›\úô[ù€€[X[ôŸX›[€àèÇàù]€à\OHòù]€àà]KXX›[€èHò€X\ãX€€[X[ô\ŸX\ò⁄à]OHê€X\àŸX\ò⁄à\öXK[Xô[Hê€X\à€€[X[ôŸX\ò⁄è∞Âœÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À]Xú»èÇà	ÿ€€[X[ôŸX›[€ìò]öYÿ][€ìX\ö›\

_BàŸ]èÇàŸ]èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[Hú⁄⁄[ú»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èí[ù\ôòXŸH[YOŸ]èÇà]à€\‹œHõX€\À]ZK][YKY‹öYèâ›ZU[YPù]€úﬂOŸ]èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ã]‹ç‹Z[\‹ù[ùà\OHòù]€àà]KXX›[€èHõ‹[ã][YK\›Y[»èì‹[àö\›X[[YH›Y[œÿù]€èÇà]à€\‹œHõX€\À\›]\»X€\À]ZK][YK\›]\»èí[ù\ôòXŸH[Y\»ô\›[HH€€\]H€€⁄]⁄]›]⁄[ô⁄[ô»[›\àŸ[X›Y‹\ò][€ò[X\⁄⁄[ãèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èê€‹ôH⁄⁄[úœŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèâÿ€‹ôU[YPù]€úﬂOŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èë[Y\ôŸ[òﬁHŸ\ùöXŸ\œŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèâ‹Ÿ\ùöXŸU[YPù]€úﬂOŸ]èÇà]à€\‹œHõX€\À\›]\»èëö\ôH€€[X[ô€XŸHX›Xÿ[YYXÿ[€€ùõ€[ô€ÿ\›[€€[X[ô\ŸHY⁄ŸZY⁄ÿÿ[[Hö[\ú»[ôô[XZ[à€€\]XõH⁄]X\›ô\õ^\ÀèŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[Hù€€»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èìX\€€œŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	ÿ€X[âÀ	¯•®âÀ	–€X[âÀ	“YHX\€€ùõ€»õ‹àÿ‹ôY[ú⁄›Àà⁄‹ù›]à… _Bà	€XZŸUŸŸ€Pù]€ä	€X\öŸ\ëõÿ›\…À	¯•‚IÀ	—õÿ›\…À	—[H]X›YùZ[[ô‹À›ôZX€\»[ôŸY\Z\‹⁄[€ú»€X\ô\ãà⁄‹ù›]àâ _Bà	€XZŸUŸŸ€Pù]€ä	€Z\‹⁄[€î[ŸIÀ	¯ß)âÀ	‘[ŸIÀ	‘[ŸH]X›YZ\‹⁄[€àX\öŸ\úÀà⁄‹ù›]à	 _Bà	€XZŸUŸŸ€Pù]€ä	‹õÿYö[‹ö]IÀ	¯•d	À	‘õÿY …À	“[ò‹ôX\ŸHõÿY€€ùò\›à⁄‹ù›]àâ _Bà	€XZŸUŸŸ€Pù]€ä	ÿ€›ô\òYŸIÀ	¯•„âÀ	‘ö[ô‹…À	—ò]»€›ô\òYŸHö[ô‹»\õ›[ô]X›YùZ[[ô‹À‹›][€úÀâ _Bàù]€à€\‹œHõX€\À]ŸŸ€KXùàX€\ÀXX›[€ãXùàà\OHòù]€àà]KXX›[€èHõ‹[ã[X\[YX\›\ôHà]OHì‹[àò]⁄[ô»õ‹à⁄[€Y]ôHYX\›\ô[Y[ùÀ[ô\À\úõ›‹ÀúôYZ[ô⁄Ÿ]⁄\À⁄\\Àõ€ô\À^[ôX\öŸ\úÀàõ›[ô»ù[ú»[ù[‹[ôYàèè‹[à€\‹œHõX€\ÀZX€€òõﬁè∏ß#è‹‹[èè‹[à€\‹œHõX€\À]^èè‹[à€\‹œHõX€\À[Xô[èëò]⁄[ôœ‹‹[èè‹[à€\‹œHõX€\À\[èì‘Sè‹‹[èè‹‹[èèÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\õ›»à›[OHõX\ô⁄[ã]‹éèÇà‹[à€\‹œHõX€\À\õ›À[Xô[èîö[ô»òY]\œ‹‹[èÇàŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHò€›ô\òYŸK\òY]\»èÇà‹[€àò[YOHçHèçHZ[\œ€‹[€èè‹[€àò[YOHåLèåLZ[\œ€‹[€èè‹[€àò[YOHåçHèåçHZ[\œ€‹[€èè‹[€àò[YOHçLèçLZ[\œ€‹[€èÇà‹Ÿ[X›ÇàŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[à]K[X€\ÀX[X[òŸK[‹\ò][€úœHõXô[èê[X[òŸH‹\ò][€úœŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàà]K[X€\ÀX[X[òŸK[‹\ò][€úœHò€€ùõ€»èÇà	€XZŸUŸŸ€Pù]€ä	ÿ[X[òŸPùZ[[ô‹”X\õÿ⁄Ÿ\âÀ	¯•©âÀ	–[X[òŸHX\õÿ⁄Ÿ\âÀ	–õÿ⁄‹»HX]ûHX\[àH[X[òŸHùZ[[ô‹À–€›\úŸ\»Y[ùKà”àYX[ú»õÿ⁄ŸYàô[ÿYô\]Z\ôYâ _Bà	€XZŸP[X[òŸSY[Xô\ìX[òYŸ\ïŸŸ€Pù]€ä
_BàŸ]èÇà]à€\‹œHõX€\À\›]\»èè›õ€ôœìX\õÿ⁄Ÿ\à”è‹›õ€ôœàô[[›ô\»H[X[òŸHùZ[[ô‹»X\[ô]»X]ûHX\öŸ\à^Y\ãà›õ€ôœê[X[òŸHY[Xô\àX[òYŸ\è‹›õ€ôœàY»õ€KX›]ö]H[ô€‹ù[ô»€€ùõ€»€à[X[òŸHY[Xô\ã[\›YŸ\ÀèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èìX\ö\⁄Xö[]H0≠»⁄‹ù›]»x†$ŒH0≠»\⁄õÿ\ô»ã’œŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	€^SZ\‹⁄[€ú…À	ÃIÀ	‘\ú€€ò[Z\‹⁄[€ú…À	‘⁄›À⁄YH€€ôöY[ùH]X›Y\ú€€ò[Z\‹⁄[€úÀà⁄‹ù›]àI _Bà	€XZŸUŸŸ€Pù]€ä	ÿ[X[òŸSZ\‹⁄[€ú…À	ÃâÀ	–[X[òŸHZ\‹⁄[€ú…À	‘⁄›À⁄YH€€ôöY[ùH]X›Y[X[òŸHZ\‹⁄[€úÀà⁄‹ù›]àâ _Bà	€XZŸUŸŸ€Pù]€ä	›ôZX€\…À	Ã…À	’ôZX€\…À	‘⁄›À⁄YH€€ôöY[ùH]X›YôZX€\Àà⁄‹ù›]à… _Bà	€XZŸUŸŸ€Pù]€ä	ÿùZ[[ô‹…À	Õ	À	–ùZ[[ô‹…À	‘⁄›À⁄YH€€ôöY[ùH]X›YùZ[[ô‹À‹›][€úÀà⁄‹ù›]à	 _Bà	€XZŸUŸŸ€Pù]€ä	ÿ[X[òŸP‹ôY]…À	ÕIÀ	–[H‹ôY	À	‘⁄›À⁄YH\õﬁ[X]H‹ôY]ò[Y\»ô\⁄YH[X[òŸHZ\‹⁄[€àX\öŸ\úÀà⁄‹ù›]àI _Bà	€XZŸUŸŸ€Pù]€ä	€Z\‹⁄[€êYŸIÀ	ÕâÀ	”Z\‹»YŸIÀ	‘⁄›»\ú€€ò[Z\‹⁄[€àYŸH⁄]õŸ‹ô\‹⁄]ôH[Xô\ãMí‹ò[ôŸH[ôçôYŸ]ô\ö]Kà⁄‹ù›]àâ _Bà	€XZŸUŸŸ€Pù]€ä	›ò[ú‹‹ùÿ]⁄\âÀ	Õ…À	’ò[ú‹‹ùÿ]⁄\âÀ	‘⁄›»[Xô\àò[ú‹‹ù\ô\]Z\ôYòYŸ\»ô\⁄YH\ú€€ò[[ô[X[òŸHZ\‹⁄[€úÀà⁄‹ù›]à… _Bà	€XZŸUŸŸ€Pù]€ä	›[ö]€€[Z]Y[ù	À	Œ	À	’[ö]€›[ù	À	‘⁄›»[›\à€€[Z]Y[ö]»ô\⁄YH\ú€€ò[[ô[X[òŸHZ\‹⁄[€úÀà⁄‹ù›]à	 _BàŸ]èÇà]à€\‹œHõX€\À\õ›»à›[OHõX\ô⁄[ã]‹éèè‹[à€\‹œHõX€\À\õ›À[Xô[èê[H‹ôY]»ö[\è‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHò[X[òŸKX‹ôY][Z[ö[][Hèè‹[€àò[YOHåèê[ò[Y\œ€‹[€èè‹[€àò[YOHçLèçR œ€‹[€èè‹[€àò[YOHåLèåL œ€‹[€èè‹[€àò[YOHåMLèåMR œ€‹[€èè‹[€àò[YOHååèåå œ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\›]\»èîôXYKèŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[Húô\€›\òŸ\»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èê€ÀXYZ[à]Y[ùò[ú‹‹ù›ŸY\Ÿ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHúÿÿ[ã]ò[ú‹‹ù\›ŸY\èîÿÿ[àò[ú‹‹ùœÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú›\ù]ò[ú‹‹ù\›ŸY\èî›\ù›ŸY\ÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú›‹]ò[ú‹‹ù\›ŸY\èî›‹ÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èë[^Hô]ŸY[à€X\úœ‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHùò[ú‹‹ù\›ŸY\Y[^Hèè‹[€àò[YOHåMLèåKçHŸX€€ôœ€‹[€èè‹[€àò[YOHååèåàŸX€€ôœ€‹[€èè‹[€àò[YOHåçLèåãçHŸX€€ôœ€‹[€èè‹[€àò[YOHåÃèå»ŸX€€ôœ€‹[€èè‹[€àò[YOHçèçŸX€€ôœ€‹[€èè‹[€àò[YOHçLèçHŸX€€ôœ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èìX^[][H\àù[è‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHõù[Xô\ààZ[èHåHàX^HçLà›\HåHà]K\Ÿ][ôœHùò[ú‹‹ù\›ŸY\[X^èèŸ]èÇà]à]K]ò[ú‹‹ù\›ŸY\èŸ]èÇà]à€\‹œHõX€\À\›]\»èìX[ùX[›\ù€õKàH›ŸY\^€Y\»[›\à\ú€€ò[ôZX€HQÀ⁄X⁄‹»]ô\ûHõ€ã\\ú€€ò[ìT»H]Y[ùôZX€H[àXX⁄YôôX›Y[X[òŸHZ\‹⁄[€ã[ô€õH€X\ú»HôZX€H⁄[àZ\‹⁄[€ê⁄YYà^‹Ÿ\»Hö\⁄XõHèë\ÿ⁄\ôŸH]Y[ùÿèàù]€ãàö\€€ô\àò[ú‹‹ù»\ôHõ›[ò€YYèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èîô\€›\òŸHÿ\ö[ô\èŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	‹ô\€›\òŸQÿ\	À	¯¶®	À	‘ô\€›\òŸHÿ\	À	‘⁄›»Z\‹⁄[ôÀ\ô\€›\òŸHòYŸ\»[ôôX\òûH]òZ[XõK][ö]\›[X]\»€àHX\[ô‹[ôYZ\‹⁄[€úÀâ _BàŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èìôX\òûHòY]\œ‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHúô\€›\òŸKYÿ\\òY]\»èè‹[€àò[YOHåLèåLZ[\œ€‹[€èè‹[€àò[YOHåçHèåçHZ[\œ€‹[€èè‹[€àò[YOHçLèçLZ[\œ€‹[€èè‹[€àò[YOHåLèåLZ[\œ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\›]\»èîô\€›\òŸHÿ\\Ÿ\»Z\‹⁄[€ê⁄YYâ‹»Z\‹⁄[ôÀ\ô\]Z\ô[Y[ù^[ô\ôõ‹õ\»ô\›YYôõ‹ùX]⁄[ô»YÿZ[ú›[›\à›\úô[ùH]òZ[XõHôZX€H\\Àà]ô]ô\àŸ[X›»‹à\‹]⁄\»[ö]ÀèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èïôZX€HÿY[ôœŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	ÿ]]”ÿY[ôZX€\…À	¯°‚âÀ	–]]À[ÿY[ôZX€\…À	–]]€X]Xÿ[HX›]ò]\»Z\‹⁄[€ê⁄YY∏†&\»ò]]ôHÿY[‹ôHôZX€\»€€ùõ€[ú⁄YH[à‹[ôYZ\‹⁄[€ãâ _BàŸ]èÇà]à€\‹œHõX€\À\›]\»èïò[ú‹‹ùÿ]⁄\à[ô[ö]€›[ùô[XZ[à[ô\à€€»\»Hÿ[õ€öXÿ[X\[›ô\õ^H€€ùõ€»õ‹à⁄‹ù›]»»[ôèŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[Hõ‹»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èìZ\‹⁄[€à[ù[YŸ[òŸOŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	€Z\‹⁄[€ïò[YIÀ	®…À	”Z\‹⁄[€àò[YIÀ	‘⁄›»Hõ‹õX]YZ\‹⁄[€àò[YH[à‹[ôYZ\‹⁄[€ê⁄YYà⁄[ô›‹Àâ _Bà	€XZŸUŸŸ€Pù]€ä	ÿ›\›€UôZX€PòYŸ\…À	¯•®…À	–›\›€HôZX€HòYŸ\…À	‘⁄›»›\›€HôZX€Hÿ]Y€‹öY\»[à]òZ[XõHôZX€\»\›â _Bà	€XZŸUŸŸ€Pù]€ä	‹›X⁄—]X›‹âÀ	¯¶®	À	‘›X⁄»]X›	À	—õY»\ú€€ò[‹àõ⁄[ôYZ\‹⁄[€ú»]⁄›»õ»YX[ö[ôŸù[õŸ‹ô\‹Àâ _Bà	€XZŸUŸŸ€Pù]€ä	€Z\‹⁄[€î‹]€âÀ	¯•„âÀ	”ô]»Z\‹⁄[€âÀ	–[ö[X]HŸ[ùZ[ô[Hô]»Z\‹⁄[€à‹]€ú»⁄]HòY\à[ŸKâ _Bà	€XZŸUŸŸ€Pù]€ä	€XZõ‹í[ò⁄Y[ùôYY	À	¯•¨	À	“[ò⁄Y[ùôYY	À	‘⁄›»H[YKX]ÿ\ôHXZõ‹à[ò⁄Y[ùX⁄Ÿ\à[àH‹›]\»ò\ãà›ô\à]\Ÿ\Œ»€X⁄»HZ\‹⁄[€à»õ€€Kâ _Bà	€XZŸUŸŸ€Pù]€ä	€Z\‹⁄[€ìÿ⁄–]Y[…À	¯£ IÀ	’òX⁄⁄[ô»]Y[…À	‘^HH⁄‹ùﬁ[ù\⁄^ôYòX⁄⁄[ô»›YH\ö[ô»Z\‹⁄[€àõ€€H[ô\ôŸ]X‹]Z\⁄][€ãâ _Bàù]€à€\‹œHõX€\À]ŸŸ€KXùàX€\ÀXX›[€ãXùàà\OHòù]€àà]KXX›[€èHõ‹[ã]ôZX€K\›]\»à]OHì‹[à‹à€‹ŸHH]ôHXõHŸà\ú€€ò[ôZX€\»‹õ›\YûHZ\‹⁄[€ê⁄YYà›]\»€ŸKà⁄‹ù›]ààèÇà‹[à€\‹œHõX€\ÀZX€€òõﬁèïè‹‹[èÇà‹[à€\‹œHõX€\À]^èè‹[à€\‹œHõX€\À[Xô[èïôZX€H€Ÿ\œ‹‹[èè‹[à€\‹œHõX€\À\[èïíQUœ‹‹[èè‹‹[èÇàÿù]€èÇà	€XZŸPX›[€ïŸŸ€Pù]€ä	€‹[ã\ô\‹›\ôKXõÿ\ô	À	¯•¨âÀ	‘ô\‹›\ôHõÿ\ô	À	”‹[à‹à€‹ŸHH]ôH‹\ò][€ò[ô\‹›\ôHõÿ\ôà⁄‹ù›]àâÀ	€X€\À\ô\‹›\ôKXõÿ\ô]ŸŸ€I _Bàù]€à€\‹œHõX€\À]ŸŸ€KXùàX€\ÀXX›[€ãXùàà\OHòù]€àà]KXX›[€èHõ‹[ã][ö][ÿÿ]‹àà]KYôX]\ôKXôXX€€èHù[ö]ÿÿ]‹àà]OHîŸX\ò⁄\ú€€ò[ôZX€\»[ô›\ù[Xô\ò]Hõ€›»[ŸHèè‹[à€\‹œHõX€\ÀZX€€òõﬁè∏£%è‹‹[èè‹[à€\‹œHõX€\À]^èè‹[à€\‹œHõX€\À[Xô[èï[ö]ÿÿ]‹è‹‹[èè‹[à€\‹œHõX€\À\[èì‘Sè‹‹[èè‹‹[èèÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èî›X⁄»Yù\è‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHú›X⁄À]ô\⁄€èè‹[€àò[YOHåLèåLZ[ù]\œ€‹[€èè‹[€àò[YOHåMHèåMHZ[ù]\œ€‹[€èè‹[€àò[YOHååèååZ[ù]\œ€‹[€èè‹[€àò[YOHåÃèåÃZ[ù]\œ€‹[€èè‹[€àò[YOHçHèçHZ[ù]\œ€‹[€èè‹[€àò[YOHçåèçåZ[ù]\œ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\›]\»èî›X⁄»]X›[€àô\Ÿ]»]»[Y\à⁄[ô]ô\àZ\‹⁄[ô»ô\]Z\ô[Y[ùÀ]Y[ùÀö\€€ô\úÀõŸ‹ô\‹»ò[YH‹à[›\à\‹⁄Y€ôY][ö]›]H⁄[ôŸ\ÀèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èì‹\ò][€ò[ô\‹›\ôH	ò[\»“UëTŸ]èÇà]à€\‹œHõX€\À[‹\ò][€ò[\ô\‹›\ôK\›[[X\ûHà]K[‹\ò][€ò[\ô\‹›\ôK\›[[X\ûOè›õ€ôœêùZ[[ô»€€[X[ôX›\ôx†)è‹›õ€ôœè‹[èì‹[àHõÿ\ô»ôX€€ò⁄[HZ\‹⁄[€à[X[ôYÿZ[ú›H]òZ[XõHõY]è‹‹[èèŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã\ô\‹›\ôKXõÿ\ôèì‹[àô\‹›\ôHõÿ\ôÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHúôYúô\⁄\ô\‹›\ôKXõÿ\ôèîôYúô\⁄[ù[YŸ[òŸOÿù]€èÇàŸ]èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ã]‹ç‹Z[\‹ù[ùà\OHòù]€àà]KXX›[€èHú‹›[‹\ò][€ò[\⁄]ô\èëŸ[ô\ò]H	ò[\»‹›‹\ò][€ò[“UëTÿù]€èÇà]à€\‹œHõX€\À\›]\»X€\ÀY\ÿ€‹ô\›]\»à]K[‹\ò][€ò[\⁄]ô\\›]\»]K]€ôOHõô]]ò[èì‹\ò][€ò[“UëTôXYHõ‹àX[ùX[‹›[ôÀèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èîŸ\‹⁄[€à\ôõ‹õX[òŸOŸ]èÇà]à]K[‹À\Ÿ\‹⁄[€èèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èê€€\][€à\›‹ûOŸ]èÇà]à€\‹œHõX€\À[‹À[\›à]K[‹ÀZ\›‹ûOèŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàà›[OHõX\ô⁄[ã]‹ç‹Z[\‹ù[ùèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHúô\Ÿ]\Ÿ\‹⁄[€àèîô\Ÿ]Ÿ\‹⁄[€èÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHò€X\ã\^[›]Z\›‹ûHèê€X\à\›‹ûOÿù]€èÇàŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[Hú^[›]»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èë[Y\ôŸ[òﬁH^[›]õ\⁄Ÿ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	‹^[›]õ\⁄	À	¸'Ê™	À	‘^[›]õ\⁄	À	—õ\⁄HX\ôY[ôõYH⁄[àH⁄[ô€H‹ôY]ÿZ[àôXX⁄\»H€€ôöY›\ôYô\⁄€â _Bà	€XZŸUŸŸ€Pù]€ä	‹^[›]€›[ô	À	¯¶jâÀ	’[YH]Y[…À	‘^HHŸ[X›Y[\]H€€\][€à›YKà[YK[›€ôY‹›YT‹»ÿY€õH⁄[àHX]⁄[ô»^[›]\»^YY»ﬁ[ù\⁄^ôYò[òX⁄»ô[XZ[ú»]òZ[XõKâ _BàŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èêò[õô\à›[O‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHú^[›]][\]HèâÿùZ[^[›][\]S‹[€ú ›]Kú^[›]õ\⁄ù[\]J_O‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èìZ[ö[][H^[›]‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHõù[Xô\ààZ[èHåLà›\HåLà]K\Ÿ][ôœHú^[›]]ô\⁄€èèŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èëõ\⁄\ò][€à
ŸX O‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHõù[Xô\ààZ[èHåààX^HåÃà›\HåHà]K\Ÿ][ôœHú^[›]Y\ò][€àèèŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èî€›[ôõ€[YO‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHúò[ôŸHàZ[èHåàX^HåHà›\HååHà]K\Ÿ][ôœHú^[›]]õ€[YHèèŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èï\›^[›]Y\è‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHú^[›]]\›X[[›[ùèè‹[€àò[YOHåLèåL»›[ô\ô€‹[€èè‹[€àò[YOHåçLèåçR»XZõ‹è€‹[€èè‹[€àò[YOHçLèçL»Y⁄ò[YO€‹[€èè‹[€àò[YOHåLèåL»[]O€‹[€èè‹Ÿ[X›èŸ]èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ãXõ›€NéZ[\‹ù[ùà\OHòù]€àà]KXX›[€èHù\›\^[›]Yõ\⁄èï\›[Y\ôŸ[òﬁHõ\⁄ÿù]€èÇà]à€\‹œHõX€\À\›]\»èïöXŸH⁄]H[ú‹\ôYòY€€\[ûH[ú‹\ôYÿÿ\ôòXŸH[ú‹\ôY[ôﬁXô\ú[ö»[ú‹\ôY\ŸH‹›Yÿ\⁄›]T‹»úõ€H[›\àXõX»⁄]Xà\‹Ÿ]ô\‹⁄]‹ûKà›\à[\]\»ô]Z[àﬁ[ù\⁄^ôY›Y\Àà[òXõH[YH]Y[ÀŸ]Hõ€[YK[à\ŸH\›[Y\ôŸ[òﬁHõ\⁄èŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[Hô\ÿ€‹ôèÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èë\ÿ€‹ôö[ò[ò⁄X[€€[X[ôŸ]èÇà]à€\‹œHõX€\À\õ›»X€\ÀY\ÿ€‹ô]⁄YHèè‹[à€\‹œHõX€\À\õ›À[Xô[èïŸXö€⁄»Tì‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHú\‹›€‹ôà]]ÿ€€\]OHõŸôàà‹[⁄X⁄œHôò[ŸHà]K\Ÿ][ôœHô\ÿ€‹ô]ŸXö€⁄»àXŸZ€\èHöŒãÀŸ\ÿ€‹ôò€€Kÿ\K›ŸXö€⁄‹ÀÀããàèèŸ]èÇà]à€\‹œHõX€\À\õ›»X€\ÀY\ÿ€‹ô]⁄YHèè‹[à€\‹œHõX€\À\õ›À[Xô[èïŸXö€⁄»ò[YO‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHù^àX^[ô›Héà]K\Ÿ][ôœHô\ÿ€‹ô[ò[YHàò[YOHìZ\‹⁄[€ê⁄YYàö[ò[òŸHèèŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èîô\‹ù€€\^]O‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ôX€€\^]Hèè‹[€àò[YOHú⁄[\Hèî⁄[\O€‹[€èè‹[€àò[YOHö[ôõ‹õX]]ôHèí[ôõ‹õX]]ôO€‹[€èè‹[€àò[YOHù€€àèïH€€è€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\›]\»X€\ÀY\ÿ€‹ôX€€\^]KZ[à]KY\ÿ€‹ôX€€\^]KZ[â—íSêSê—W‘ëT‘ï–””TVUW–”‘Kö[ôõ‹õX]]ô_OŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èîô\‹ù\ö[Ÿ‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ô\\ö[Ÿèè‹[€àò[YOHùŸ^HèïŸ^O€‹[€èè‹[€àò[YOHûY\›\ô^HèñY\›\ô^O€‹[€èè‹[€àò[YOHõ\›çèì\›ç›\úœ€‹[€èè‹[€àò[YOHõ\›»èì\›»^\œ€‹[€èè‹[€àò[YOHõ\›Ãèì\›Ã^\œ€‹[€èè‹[€àò[YOHõ\›Lèì\›L^\œ€‹[€èè‹[€àò[YOHõ\›Nèì\›N^\œ€‹[€èè‹[€àò[YOHõ\›ÕçHèì\›ÕçH^\œ€‹[€èè‹[€àò[YOHò[]òZ[XõHèê[]òZ[XõH\›‹ûO€‹[€èè‹[€àò[YOHúŸ\‹⁄[€àèê›\úô[ùŸ\‹⁄[€è€‹[€èè‹[€àò[YOHú⁄[òŸS\›èî⁄[òŸH\›ô\‹ù€‹[€èè‹[€àò[YOHò›\›€Hèê›\›€H]\œ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\ÀY\ÿ€‹ôY]KY‹öYèÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èëúõ€O‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHô]Hà]K\Ÿ][ôœHô\ÿ€‹ôX›\›€K\›\ùèèŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èïœ‹‹[èè[ú]€\‹œHõX€\ÀZ[ú]à\OHô]Hà]K\Ÿ][ôœHô\ÿ€‹ôX›\›€KY[ôèèŸ]èÇàŸ]èÇà]à€\‹œHõX€\À\õ›»à]KY\ÿ€‹ô[Z[ãX€€\^]OHö[ôõ‹õX]]ôHèè‹[à€\‹œHõX€\À\õ›À[Xô[èêúôXZŸ›€à\‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ô]‹Xÿ]Y€‹öY\»èè‹[€àò[YOHå»èï‹œ€‹[€èè‹[€àò[YOHçHèï‹O€‹[€èè‹[€àò[YOHéèï‹€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»à]KY\ÿ€‹ô[Z[ãX€€\^]OHö[ôõ‹õX]]ôHèè‹[à€\‹œHõX€\À\õ›À[Xô[èîô]ö[›\À\\ö[Ÿ€€\\ö\€€è‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ôX€€\\ö\€€àèè‹[€àò[YOHùùYHèí[ò€YY€‹[€èè‹[€àò[YOHôò[ŸHèë\ÿXõY€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»à]KY\ÿ€‹ô[Z[ãX€€\^]OHö[ôõ‹õX]]ôHèè‹[à€\‹œHõX€\À\õ›À[Xô[èí[\‹ù[ù[\ùœ‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ô\ö\⁄»èè‹[€àò[YOHùùYHèí[ò€YY€‹[€èè‹[€àò[YOHôò[ŸHèë\ÿXõY€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»à]KY\ÿ€‹ô[Z[ãX€€\^]OHù€€àèè‹[à€\‹œHõX€\À\õ›À[Xô[èëõ‹ôXÿ\›[ù[YŸ[òŸO‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ôYõ‹ôXÿ\›èè‹[€àò[YOHùùYHèí[ò€YY€‹[€èè‹[€àò[YOHôò[ŸHèë\ÿXõY€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èë\ÿ€‹ô⁄\ù[XYŸO‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô\ÿ€‹ôX⁄\ùèè‹[€àò[YOHùùYHèê]X⁄⁄\ù€‹[€èè‹[€àò[YOHôò[ŸHèï^€õO€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHô\ÿ€‹ô]\›èï\›€€õôX›[€èÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHô\ÿ€‹ôX€X\àèê€X\àŸXö€⁄œÿù]€èÇàŸ]èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ã]‹ç‹Z[\‹ù[ùà\OHòù]€àà]KXX›[€èHô\ÿ€‹ôYŸ[ô\ò]K\‹›èëŸ[ô\ò]H	ò[\»‹›ô\‹ùÿù]€èÇà]à€\‹œHõX€\À\›]\»X€\ÀY\ÿ€‹ô\›]\»à]KY\ÿ€‹ô\›]\»]K]€ôOHõô]]ò[èê⁄€‹ŸHH\ö[Ÿ[ôô\‹ù€€\^]K[àŸ[ô\ò]H[ô‹›Hö[ò[òŸHô\‹ùèŸ]èÇÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èî^Y\ãS[öŸYÿÿ[ö[ò[ò⁄X[\ò⁄]ôOŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èìÿÿ[\›‹öXÿ[\ò⁄]ôO‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHôö[ò[òŸK]ò][Y[òXõYèè‹[€àò[YOHùùYHèë[òXõY€‹[€èè‹[€àò[YOHôò[ŸHèë\ÿXõY€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èí\›‹ûHô][ù[€è‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHôö[ò[òŸK]ò][\ô][ù[€àèè‹[€àò[YOHò[èê[]òZ[XõO€‹[€èè‹[€àò[YOHåNçHèçHYX\úœ€‹[€èè‹[€àò[YOHçÃÃèåàYX\úœ€‹[€èè‹[€àò[YOHåÕçHèåHYX\è€‹[€èè‹[€àò[YOHåNèåN^\œ€‹[€èè‹[€àò[YOHéLèéL^\œ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èë⁄]Xà[ù[YŸ[òŸHôYYœ‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHôö[ò[òŸK\ù[KYôYYèè‹[€àò[YOHùùYHèê]]€X]X»ù[\»
»€XﬁO€‹[€èè‹[€àò[YOHôò[ŸHèêùZ[Z[à[ù[YŸ[òŸH€õO€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHôö[ò[òŸKX\ò⁄]ôK\ÿÿ[àèëY\ÿÿ[à[]òZ[XõOÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHôö[ò[òŸKX\ò⁄]ôKXÿ[òŸ[èî›‹ÿÿ[èÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHôö[ò[òŸKX\ò⁄]ôKY^‹ùèë^‹ù\ò⁄]ôOÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHôö[ò[òŸKX\ò⁄]ôKZ[\‹ùèí[\‹ù\ò⁄]ôOÿù]€èÇàŸ]èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ã]‹ç‹Z[\‹ù[ùà\OHòù]€àà]KXX›[€èHôö[ò[òŸK\ù[\À\ôYúô\⁄èîôYúô\⁄ö[ò[ò⁄X[[ù[YŸ[òŸOÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ã]‹ç‹Z[\‹ù[ùà\OHòù]€àà]KXX›[€èHôö[ò[òŸKX\ò⁄]ôKX€X\àèê€X\à^Y\à\ò⁄]ôOÿù]€èÇà[ú]€\‹œHõX€\ÀZY[ãYö[Hà\OHôö[HàXÿŸ\Hò\Xÿ][€ã⁄ú€€ã^⁄ú€€ãöú€€àà]KZ[\‹ùYö[ò[òŸKYö[OÇà]à€\‹œHõX€\ÀYö[ò[òŸK]ò][\›[[X\ûHà]KYö[ò[òŸK]ò][\›[[X\ûOèŸ]èÇà]à€\‹œHõX€\À\›]\»X€\ÀY\ÿ€‹ô\›]\»à]KYö[ò[òŸK]ò][\›]\»]K]€ôOHõô]]ò[èìÿÿ[ö[ò[ò⁄X[\ò⁄]ôHôXYKèŸ]èÇà]à€\‹œHõX€\À\›]\»X€\ÀY\ÿ€‹ô\›]\»à]KYö[ò[òŸK\ù[K\›]\»]K]€ôOHõô]]ò[èêùZ[Z[àö[ò[ò⁄X[[ù[YŸ[òŸHX›]ôKèŸ]èÇà]à€\‹œHõX€\À\›]\»èë⁄]Xà‹›»XõX»ò[úÿX›[€ãX€\‹⁄YöXÿ][€àù[\»[ô]Y]€XﬁH€õKàH€€⁄]ô]ô\à\ÿY»^Y\àYŸ\à]K\ÿ€‹ôŸXö€⁄‹»‹àô\‹⁄]‹ûH‹ôY[ùX[ÀàHÿÿ[\ò⁄]ôH\»[ô^YûHZ\‹⁄[€ê⁄YYà^Y\àQ€ò[YH[ôÿ[àôHò[úŸô\úôYô]ŸY[à]öXŸ\»\⁄[ô»^‹ù\ò⁄]ôH»[\‹ù\ò⁄]ôH‹àH€€\]Hö]ò]H€€⁄]òX⁄›\èŸ]èÇà]à€\‹œHõX€\À\›]\»X€\ÀYö[ò[òŸK\ö]ò]K[õ›Hèîö]ò]HòX⁄›\ÿ\õö[ôŒà^‹ù[[ò€Y\»[›\à\ÿ€‹ôŸXö€⁄»[ôÿÿ[H›‹ôYZ\‹⁄[€ê⁄YYàö[ò[ò⁄X[\›‹ûKà[û[€ôH€[ô»Hö[HX^H‹›õ›Y⁄HŸXö€⁄»[ô[ú‹X›H^‹ùYÿ[YHYŸ\ãèŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[HúXŸ\»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èî]ZX⁄»ù[\»
»ÿ‹ôY[à⁄‹ù›]œŸ]èÇà]à€\‹œHõX€\À\]ZX⁄À[\›èèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èî€X\ùõ€⁄€X\ö»Xô[»
»ÿ‹ôY[à⁄‹ù›]œŸ]èÇà]à€\‹œHõX€\ÀXõ€⁄€X\öÀ[\›èèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èîÿ]ôYX\õŸö[\œŸ]èÇà]à€\‹œHõX€\À\õŸö[K[\›à]K\õŸö[K[\›èŸ]èÇà]à€\‹œHõX€\À\›]\»èîõŸö[\»›‹ôH[›\àX\ÿÿ][€ãõ€€K⁄⁄[ãö\⁄Xö[]Hö[\ú»[ô€€⁄]›ô\õ^\ÀèŸ]èÇà‹ŸX›[€èÇàŸX›[€à€\‹œHõX€\À]Xã\[ô[à]K\[ô[HúŸ][ô‹»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èë]öXŸH^[›]Ÿ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èì[ÿö[H[ŸH0≠»S‘»ÿYò\öO‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHõ[ÿö[K[[ŸHèè‹[€àò[YOHò]]»èê]]»]X›T€ôO€‹[€èè‹[€àò[YOHõ€àèê[ÿ^\»€è€‹[€èè‹[€àò[YOHõŸôàèê[ÿ^\»Ÿôè€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èïXõ][ŸO‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHùXõ][[ŸHèè‹[€àò[YOHò]]»èê]]»]X›€‹[€èè‹[€àò[YOHõ€àèê[ÿ^\»€è€‹[€èè‹[€àò[YOHõŸôàèê[ÿ^\»Ÿôè€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\›]\»à]KY]öXŸK[^[›]\›]\œë]X›[ô»]öXŸH^[›]8†)èŸ]èÇà]à€\‹œHõX€\À\›]\»èì[ÿö[H[ŸH\»[ôYõ‹àT€ôHÿYò\öH⁄][\\õ[€öŸ^NàHX\X]ÿ\ôHpÂÃà€€[X[ô‹öY[à‹ùòZ]H€€\X›⁄[ô€K\õ›»ÿ⁄»⁄\ôH‹XŸH[›‹Àù[]⁄YÿYôKX\ôXHõ›€H⁄Y]ÀMúõ‹õH€€ùõ€»»ô]ô[ùÿYò\öH[ú]õ€€K[ôö\›X[öY]‹‹ù[ô[ô»õ‹àHS‘»Ÿ^Xõÿ\ôàXõ][ô\⁄›‹^[›]»ô[XZ[àŸ\\ò]H[ô[ò⁄[ôŸYèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èí[ù\ôòXŸH[ú⁄]OŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èë\⁄›‹[ú⁄]O‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô[ú⁄]KY\⁄›‹èè‹[€àò[YOHú‹X⁄[›\»èî‹X⁄[›\œ€‹[€èè‹[€àò[YOHú›[ô\ôèî›[ô\ô€‹[€èè‹[€àò[YOHò€€\X›èê€€\X›€‹[€èè‹[€àò[YOHò€€[X[ôèê€€[X[ôŸ[ùôO€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èïXõ][ú⁄]O‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHô[ú⁄]K]Xõ]èè‹[€àò[YOHú‹X⁄[›\»èî‹X⁄[›\œ€‹[€èè‹[€àò[YOHú›[ô\ôèî›[ô\ô€‹[€èè‹[€àò[YOHò€€\X›èê€€\X›€‹[€èè‹[€àò[YOHò€€[X[ôèê€€[X[ôŸ[ùôO€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\›]\»èë\⁄›‹[ôXõ][ú⁄]H\ôH›‹ôY[ô\[ô[ùKàS‘»[ÿö[H[ŸHŸY\»]»õ›X›Y›X⁄\ÿYôH⁄^ö[ôÀèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èëÿ⁄»‹⁄][€èŸ]èÇà]à€\‹œHõX€\À\‹⁄][€ãY‹öYèâ‹‹⁄][€êù]€úﬂOŸ]èÇà]à€\‹œHõX€\ÀY\⁄›‹\‹⁄][€ãX€€ùõ€»èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èëö[ôHùYŸOŸ]èÇà]à€\‹œHõX€\À[ùYŸKY‹öYèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõùYŸK[Yùè∏°§ÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõùYŸK]\è∏°§Oÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõùYŸKY›€àè∏°§œÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõùYŸK\öY⁄è∏°§èÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõùYŸK\ô\Ÿ]èåÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\›]\»X€\À[ùYŸK]ò[YHèñ»HŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èìY[ùH[ô[Ÿ]èÇà]à€\‹œHõX€\À[ùYŸKY‹öYèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú[ô[[Yùè∏°§ÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú[ô[]\è∏°§Oÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú[ô[Y›€àè∏°§œÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú[ô[\öY⁄è∏°§èÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHú[ô[\ô\Ÿ]è∏°Æèÿù]€èÇàŸ]èÇàŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èí[ú]Ÿ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	‹⁄‹ù›]…À	¯£*	À	“Ÿ^\…À	“Ÿ^Xõÿ\ô⁄‹ù›]»€ã€Ÿôãà€€[X[ô[]NàÀàX\€€Œàx†$ŒàôZX€H€Ÿ\ŒàãàY[ùNàKâ _Bàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ãX€€[X[ô\[]Hèì‹[à€€[X[ô[]Oÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã\\ú€€ò[\ÿ][€ã\›Y[»èî\ú€€ò[\ÿ][€à›Y[œÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã[õ›YöXÿ][€ã\›Y[»èî€›[ô»	ò[\»[\ùœÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ãZ[ú]\›Y[»à]KYôX]\ôKXôXX€€èHö[ú]èí›Ÿ^\»	ò[\»Ÿ\›\ô\œÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã\⁄[\›Y[»à]KYôX]\ôKXôXX€€èHúô\⁄⁄[àèï€€⁄]	ò[\»ÿ[YH›[Oÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èïXõ]]ZX⁄»⁄Y[Ÿ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸUŸŸ€Pù]€ä	‹]ZX⁄’⁄Y[	À	¯•‚IÀ	‘]ZX⁄»⁄Y[	À	”€ôÀ\ô\‹»HX\[àXõ][ŸH»‹[à⁄^›X⁄YúöY[ôH€€[X[ôÀâ _Bàù]€à€\‹œHõX€\À\€X[XùààYHõX€\À[‹[ã\]ZX⁄À]⁄Y[\Ÿ][ô»à\OHòù]€àà]KXX›[€èHõ‹[ã]Xõ]\]ZX⁄À]⁄Y[èì‹[à⁄Y[ÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\]ZX⁄À]⁄Y[\Ÿ][ô‹»èâ‹›]Kú]ZX⁄’⁄Y[ú€›Àú€XŸJ›]Kú]ZX⁄’⁄Y[ú€›€›[ù
KõX\

€›[ô^
HOà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èï⁄Y[€›	⁄[ô^
»_O‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHú]ZX⁄À]⁄Y[\€›I⁄[ô^Hèâ‹]ZX⁄’⁄Y[‹[€ú €›
_O‹Ÿ[X›èŸ]èò
Köõ⁄[ä	… _OŸ]èÇàù]€à€\‹œHõX€\À\€X[Xùàà›[OHù⁄YåL	HZ[\‹ù[ù€X\ô⁄[ã]‹ç‹Z[\‹ù[ùà\OHòù]€àà]KXX›[€èHõ‹[ã]⁄Y[\›Y[»èëù[H›\›€Z\ŸH]ZX⁄»⁄Y[ÿù]€èÇà]à€\‹œHõX€\À\›]\»èïXõ]€ôÀ\ô\‹»\Ÿ\»Z\‹⁄[€ê⁄YY∏†&\»XYõ]\Z€Ÿ\›\ôK€»‹ô[ò\ûH\»[ôX\[õö[ô»ô[XZ[àò]]ôH[ù[H€\»€€ôö\õYYèŸ]èÇà]à€\‹œHõX€\À\õ›»èè‹[à€\‹œHõX€\À\õ›À[Xô[èìXZõ‹à[ò⁄Y[ùô\⁄€‹‹[èèŸ[X›€\‹œHõX€\À\Ÿ[X›à]K\Ÿ][ôœHõXZõ‹ãZ[ò⁄Y[ù[Z[ö[][Hèè‹[€àò[YOHåLèåL
»‹ôY]œ€‹[€èè‹[€àò[YOHåçLèåçK
»‹ôY]œ€‹[€èè‹[€àò[YOHçLèçL
»‹ôY]œ€‹[€èè‹[€àò[YOHåLèåL
»‹ôY]œ€‹[€èè‹Ÿ[X›èŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èìX\€€[X[ôò\èŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸPX›[€ïŸŸ€Pù]€ä	›ŸŸ€KX€€[X[ôXò\âÀ	¯•©	À	–€€[X[ôò\âÀ	‘⁄›»‹àYHH‹õ›\YX\€€[X[ô€€ùõ€»⁄[HŸY\[ô»H€€⁄]][ò⁄\à]òZ[XõKâÀ	€X€\ÀX€€[X[ôXò\ã\Ÿ][ô… _Bà	€XZŸPX›[€ïŸŸ€Pù]€ä	›ŸŸ€K[X\Yù[ÿ‹ôY[âÀ	¯¶ÌâÀ	—ù[ÿ‹ôY[âÀ	”X^[Z\ŸHH‹\ò][€ò[X\à\ÿÿ\H[ôH\ú⁄\›[ùô\›‹ôHù]€à[ÿ^\»^]âÀ	€X€\ÀYù[ÿ‹ôY[ã\Ÿ][ô… _BàŸ]èÇà]à€\‹œHõX€\À\›]\»èïH€€⁄]][ò⁄\à[ô]ôHô\ú⁄[€à›]\»ô[XZ[à]òZ[XõH⁄[àH€€[X[ôò\à\»Y[ãà‹[àŸ][ô‹»»ô\›‹ôH]][ûH[YKèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èëX€€õ€^H[ŸOŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇà	€XZŸPX›[€ïŸŸ€Pù]€ä	›ŸŸ€KYX€€õ€^IÀ	¯¶n…À	—X€€õ€^H[ŸIÀ	‘ôYXŸHX€‹ò]]ôH[ö[X][€ãX\[^Y\àô\‹›\ôH[ôòX⁄Ÿ‹õ›[ôôYúô\⁄úô\]Y[òﬁH⁄]›]\ÿXõ[ô»‹\ò][€ò[[Ÿ[\ÀâÀ	€X€\ÀYX€€õ€^K\Ÿ][ô… _BàŸ]èÇà]à€\‹œHõX€\À\›]\»X€\ÀYX€€õ€^K\›]\»èëX€€õ€^H[ŸHô\Ÿ\ùô\»]ô\ûH[Ÿ[H⁄[HôYX⁄[ô»[ö[X][€úÀX\[^Y\àô\‹›\ôH[ôòX⁄Ÿ‹õ›[ôôYúô\⁄úô\]Y[òﬁKèŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èìXZ[ù[ò[òŸH	ò[\»›ZY[òŸOŸ]èÇà]à€\‹œHõX€\ÀY‹öYLàèÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHù€€⁄]Yÿ›‹àèîù[à€€⁄]ÿ›‹èÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã]\]KXúöYYö[ô»à]KYôX]\ôKXôXX€€èHò€€ù^èï⁄]8†&\»ô]»[àâ‘–‘íTùô\ú⁄[€üOÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã\Ÿ]\]⁄^ò\ôèîù[àŸ]\⁄^ò\ôÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã[^[›]\›Y[»èì‹[à^[›]ùZ[\èÿù]€èÇàù]€à€\‹œHõX€\À\€X[XùàX€\À\ÿYôK[[ŸK\Ÿ][ô»à\OHòù]€àà]KXX›[€èHùŸŸ€K\ÿYôK[[ŸHà]KYôX]\ôKXôXX€€èHúÿYôS[ŸHèâ‹›]KúÿYôS[ŸKô[òXõY»	—^]€€⁄]ÿYôH[ŸI»à	—[ù\à€€⁄]ÿYôH[ŸIﬂOÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ã\Ÿ\‹⁄[€ãX€X[ù\à]KYôX]\ôKXôXX€€èHúŸ\‹⁄[€ê€X[ù\èîŸ\‹⁄[€à€X[ù\ÿù]€èÇàŸ]èÇà]à€\‹œHõX€\À\ŸX›[€ã[Xô[èêòX⁄›\	ò[\»ôX€›ô\ûOŸ]èÇà]à€\‹œHõX€\ÀX€€ôöYÀXX›[€ú»èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHô^‹ùX€€ôöY»à]OHë[ò‹û\]ô\ûH€€⁄]Ÿ][ôÀ\ÿ€‹ôŸXö€⁄»[ôö[ò[ò⁄X[\ò⁄]ôHôX€‹ô⁄]H\‹‹ò\ŸHà\öXK[Xô[Hê‹ôX]H[ò‹û\YŸ][ô‹»ò[úŸô\àèë[ò‹û\Y^‹ùÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHö[\‹ùX€€ôöY»à]OHí[\‹ù[à[ò‹û\Y‹àYÿXﬁH€€⁄]Ÿ][ô‹»òX⁄›\à\öXK[Xô[Hí[\‹ù€€⁄]Ÿ][ô‹»èí[\‹ùÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHô^‹ù\ÿYôKX€€ôöY»à]OHë^‹ùŸ][ô‹»⁄]›]\ÿ€‹ôŸXö€⁄À\ò⁄]ôHY[ù]H‹àö[ò[ò⁄X[\›‹ûHà\öXK[Xô[Hë^‹ùÿYôHŸ][ô‹»⁄]›]ö]ò]H[ùY‹ò][€ú»èîÿYôH^‹ùÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHõ‹[ãXòX⁄›\XŸ[ùôHèêòX⁄›\Ÿ[ùôOÿù]€èÇàù]€à€\‹œHõX€\À\€X[Xùàà\OHòù]€àà]KXX›[€èHúô\Ÿ]X€€ôöY»èîô\Ÿ]ÿù]€èÇàŸ]èÇà[ú]€\‹œHõX€\ÀZY[ãYö[Hà\OHôö[HàXÿŸ\Hò\Xÿ][€ã⁄ú€€ã^⁄ú€€ãöú€€ãõX€\»à]KZ[\‹ùX€€ôöYÀYö[OÇà]à€\‹œHõX€\À\›]\»èë[ò‹û\Y^‹ù[ò€Y\»]ô\ûHôYô\ô[òŸKõŸö[Kõ€⁄€X\öÀ\ÿ€‹ôŸXö€⁄»[ôÿÿ[ö[ò[ò⁄X[\ò⁄]ôHôX€‹ô[ú⁄YHQTÀLçMãQ–”H\‹‹ò\ŸH[ò‹û\[€ãàÿYôH^‹ù\»Z[ù^ù][Xô\ò][H^€Y\»[[ùY‹ò][€úÀY[ù]H[ôö[ò[ò⁄X[\›‹ûKàYÿXﬁHî””àòX⁄›\»ô[XZ[à[\‹ùXõHõ›Y⁄HôYX›Yô]öY]»›\èŸ]èÇà‹ŸX›[€èÇà]à€\‹œHõX€\ÀYõ€›\àèÇà‹[èï[öYöYY€€[X[ô[ù\ôòXŸH0≠»\⁄›‹Xõ][ôS‘»0≠»[[Y\»⁄\ôH€ôH‹\ò][€ò[^[›]è‹‹[èÇà‹[à€\‹œHõX€\ÀXùZ[èâ‘–‘íTõò[Y_Hâ‘–‘íTùô\ú⁄[€üH0≠»RU0≠»	‘–‘íTò]]‹üO‹‹[èÇàŸ]èÇà¬à\‹òYP€€[X[ô[ù\ôòXŸJ[ô[
N¬à€€ú›Xì\›H[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À]Xú… N¬àYà
Xì\›
HXì\›úŸ]]öXù]J	‹õ€IÀ	›Xõ\›	 N¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À]XãXùâ Kôõ‹ëXX⁄
ù]€àOà¬à€€ú›XàHù]€ãô]\Ÿ]ùXé¬àù]€ãöYHX€\À]XãI›XüX¬àù]€ãúŸ]]öXù]J	‹õ€IÀ	›Xâ N¬àù]€ãúŸ]]öXù]J	ÿ\öXKX€€ùõ€…ÀX€\À]Xú[ô[I›XüX
N¬àù]€ãúŸ]]öXù]J	ÿ\öXK\Ÿ[X›Y	À	Ÿò[ŸI N¬àù]€ãùXí[ô^HLN¬àJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À]Xã\[ô[	 Kôõ‹ëXX⁄
Xî[ô[Oà¬à€€ú›XàHXî[ô[ô]\Ÿ]ú[ô[¬àXî[ô[öYHX€\À]Xú[ô[I›XüX¬àXî[ô[úŸ]]öXù]J	‹õ€IÀ	›Xú[ô[	 N¬àXî[ô[úŸ]]öXù]J	ÿ\öXK[Xô[YûIÀX€\À]XãI›XüX
N¬àXî[ô[öY[àHùYN¬àJN¬à[ô[òY]ô[ù\›[ô\ä	⁄Ÿ^Y›€âÀ]ô[ùOà¬àYà
]ô[ùöŸ^HOOH	—\ÿÿ\I»	âà€€[X[ôŸX\ò⁄‹[äH¬à]ô[ùúô]ô[ùYò][

N¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬àŸ]€€[X[ôŸX\ò⁄‹[äò[ŸK[ô[
N¬à[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À\ŸX\ò⁄Xù]€â OÀôõÿ›\œÀä»ô]ô[ùÿ‹õ€àùYHJN¬àô]\õé¬àBà€€ú››\úô[ùH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À]XãXùâ N¬àYà
X›\úô[ùV…–\úõ›”Yù	À	–\úõ›‘öY⁄	À	–\úõ›’\	À	–\úõ›—›€âÀ	“€YIÀ	—[ô	◊Kö[ò€Y\ ]ô[ùöŸ^JJHô]\õé¬à€€ú›ù]€ú»H\úò^Kôúõ€J[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À]XãXùâ JN¬à€€ú››\úô[ù[ô^HX]õX^
ù]€úÀö[ô^Ÿä›\úô[ù
JN¬à€€ú›ô^[ô^H]ô[ùöŸ^HOOH	“€YI»»àà]ô[ùöŸ^HOOH	—[ô	»»ù]€úÀõ[ô›HBàà
›\úô[ù[ô^
»
…–\úõ›‘öY⁄	À	–\úõ›—›€â◊Kö[ò€Y\ ]ô[ùöŸ^JH»HàLJH
»ù]€úÀõ[ô›
H	Hù]€úÀõ[ô›¬à]ô[ùúô]ô[ùYò][

N¬à€€ú›ô^ù]€àHù]€ú÷€ô^[ô^N¬àŸ]X›]ôUXäô^ù]€ãô]\Ÿ]ùXäN¬àô^ù]€ãôõÿ›\ »ô]ô[ùÿ‹õ€àùYHJN¬àJN¬à[ô[òY]ô[ù\›[ô\ä	ÿ€X⁄…À]ô[ùOà¬à€€ú›€‹ŸPù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\ÀX€‹ŸI N¬à€€ú›Xêù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À]XãXùâ N¬à€€ú›ZU[YPù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À]ZK][YKXùâ N¬à€€ú›[YPù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À][YKXùâ N¬à€€ú›ŸŸ€Pù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]K]ŸŸ€WI N¬à€€ú›‹⁄][€êù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	ÀõX€\À\‹⁄][€ãXùâ N¬à€€ú›X›[€êù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]KXX›[€óI N¬àYà
€‹ŸPù]€äH»€‹ŸT[ô[
»ô\›‹ôQõÿ›\ŒàùYHJN»ô]\õé»BàYà
Xêù]€äH»Ÿ]X›]ôUXäXêù]€ãô]\Ÿ]ùXäN»ô]\õé»BàYà
ZU[YPù]€äH»\UZU[YJZU[YPù]€ãô]\Ÿ]ùZU[YKùYJN»ô]\õé»BàYà
[YPù]€äH»\U[YJ[YPù]€ãô]\Ÿ]ù[YKùYJN»ô]\õé»BàYà
ŸŸ€Pù]€äH»ŸŸ€QôX]\ôJŸŸ€Pù]€ãô]\Ÿ]ùŸŸ€JN»ô]\õé»BàYà
‹⁄][€êù]€äH»\T‹⁄][€ä‹⁄][€êù]€ãô]\Ÿ]ú‹⁄][€ãùYJN»ô]\õé»BàYà
X›[€êù]€äH¬à]ô[ùúô]ô[ùYò][

N¬à[ôPX›[€äX›[€êù]€äN¬àô]\õé¬àBàJN¬à[ô[òY]ô[ù\›[ô\ä	ÿ⁄[ôŸIÀ]ô[ùOà[ôTŸ][ô–⁄[ôŸJ]ô[ùù\ôŸ]
JN¬à[ô[òY]ô[ù\›[ô\ä	⁄[ú]	À]ô[ùOà¬àYà
Y]ô[ùù\ôŸ]ÀõX]⁄\œÀä	÷Ÿ]KX€€[X[ô\ŸX\ò⁄I JHô]\õé¬à€€[X[ôŸX\ò⁄]Y\ûHH›ö[ô ]ô[ùù\ôŸ]ùò[YH	… Kùö[T›\ù

N¬à€€[X[ô[ù\ôòXŸP\TŸX\ò⁄
[ô[
N¬à\]P€€[X[ô[ù\ôòXŸRXY\ä[ô[
N¬àJN¬à€€ú›òY“[ôHH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\ÀYòYÀZ[ôI N¬àYà
òY“[ôJH¬àòY“[ôKòY]ô[ù\›[ô\ä	€[›\ŸY›€âÀ›\ù[ô[òYÀùYJN¬àòY“[ôKòY]ô[ù\›[ô\ä	››X⁄›\ù	À›\ù[ô[òYÀ»ÿ\\ôNàùYK\‹⁄]ôNàò[ŸHJN¬àBà…ÿ€X⁄…À	Ÿõ€X⁄…À	€[›\ŸY›€âÀ	€[›\Ÿ]\	À	€[›\Ÿ[[›ôIÀ	›⁄Y[	À	ÿ€€ù^Y[ùIÀ	››X⁄›\ù	À	››X⁄[›ôIÀ	››X⁄[ô	◊Kôõ‹ëXX⁄
]ô[ùò[YHOà¬à[ô[òY]ô[ù\›[ô\ä]ô[ùò[YK]ô[ùOà]ô[ùú›‹õ‹Yÿ][€ä
K»\‹⁄]ôNàò[ŸHJN¬àJN¬àÿ›[Y[ùòõŸKò\[ô⁄[
[ô[
N¬à€€ú›[\‹ù[ú]H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]KZ[\‹ùX€€ôöYÀYö[WI N¬àYà
[\‹ù[ú]
H¬à[\‹ù[ú]òY]ô[ù\›[ô\ä	ÿ⁄[ôŸIÀ

HOà¬à€€ú›ö[HH[\‹ù[ú]ôö[\œÀñÃN¬àYà
ö[JH[\‹ù€€⁄]€€ôöY—ö[Jö[JN¬à[\‹ù[ú]ùò[YHH	…Œ¬àJN¬àBà€€ú›ö[ò[òŸR[\‹ù[ú]H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]KZ[\‹ùYö[ò[òŸKYö[WI N¬àYà
ö[ò[òŸR[\‹ù[ú]
H¬àö[ò[òŸR[\‹ù[ú]òY]ô[ù\›[ô\ä	ÿ⁄[ôŸIÀ

HOà¬à€€ú›ö[HHö[ò[òŸR[\‹ù[ú]ôö[\œÀñÃN¬àYà
ö[JH[\‹ùö[ò[ò⁄X[\ò⁄]ôQö[Jö[JN¬àö[ò[òŸR[\‹ù[ú]ùò[YHH	…Œ¬àJN¬àBàô[ô\î]ZX⁄‘XŸ\ 
N¬àô[ô\êõ€⁄€X\ö‹ 
N¬àô[ô\îõŸö[\ 
N¬à\]URJ
N¬àôX€‹ô›\ù\Y]öX 	‹Ÿ][ô‹‘[ô[ùZ[\…À[ô[›\ùY]»Ÿ][ô‹‘[ô[^ûNàùYHJN¬àô]\õà[ô[¬àBÇàù[ò›[€àô[ô\î]ZX⁄‘XŸ\ 
H¬à€€ú›\›Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHõX€\À\]ZX⁄À[\›
N¬àYà
[\›
Hô]\õé¬à\›ö[õô\íSHURP“◊‘P—TÀõX\
XŸHOàà]à€\‹œHõX€\À\]ZX⁄À\õ›»èÇàù]€à€\‹œHõX€\À\XŸK[XZ[àà\OHòù]€àà]KXX›[€èHúXŸKY€»à]K\XŸOHâ‹XŸKöYHà]OHíù[\»	Ÿ\ÿÿ\R[
XŸKõò[YJ_HèÇà‹[à€\‹œHõX€\ÀZX€€òõﬁè∏£%è‹‹[èè‹[à€\‹œHõX€\À]^èè‹[à€\‹œHõX€\À[Xô[èâŸ\ÿÿ\R[
XŸKõò[YJ_O‹‹[èè‹[à€\‹œHõX€\À\[èâ‹XŸKõXô[O‹‹[èè‹‹[èÇàÿù]€èÇàù]€à€\‹œHõX€\À\[ãXùà	‹›]Kú]ZX⁄‘[ú÷‹XŸKöYH»	€X€\À[€â»à	…ﬂHà\OHòù]€àà]KXX›[€èHú]ZX⁄À\[àà]K\XŸOHâ‹XŸKöYHà]OHî[à\»\ú⁄\›[ùÿ‹ôY[à⁄‹ù›]èâ‹›]Kú]ZX⁄‘[ú÷‹XŸKöYH»	””â»à	‘SâﬂOÿù]€èÇàŸ]èÇà
Köõ⁄[ä	… N¬àBÇàù[ò›[€àô[ô\êõ€⁄€X\ö‹ 
H¬à€€ú›\›Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHõX€\ÀXõ€⁄€X\öÀ[\›
N¬àYà
[\›
Hô]\õé¬à\›ö[õô\íSH›]Kòõ€⁄€X\ö‹ÀõX\

õ€⁄€X\öÀ[ô^
HOà¬àYà
Xõ€⁄€X\ö H¬àô]\õà]à€\‹œHõX€\ÀXõ€⁄€X\öÀ\õ›»èè‹[à€\‹œHõX€\ÀXõ€⁄€X\öÀ[ò[YHèî€›	⁄[ô^
»_H[\O‹‹[èè‹[èè‹‹[èè‹[èè‹‹[èèù]€à€\‹œHõX€\ÀXõ€⁄€X\öÀXùàà\OHòù]€àà]KXX›[€èHòõ€⁄€X\öÀ\ÿ]ôHà]K\€›Hâ⁄[ô^Hèîÿ]ôOÿù]€èè‹[èè‹‹[èèŸ]èò¬àBà€€ú›ÿ‹ôY[ìXô[Hõ€⁄€X\ö‘ÿ‹ôY[ìXô[
õ€⁄€X\ö N¬à€€ú›Xô[[ŸHHõ€⁄€X\öÀú⁄‹ùXô[»	–’T’”I»à	–UU…Œ¬à€€ú›Xô[]HH	ÿõ€⁄€X\öÀõò[Y_H0≠»ÿ‹ôY[àXô[à	‹ÿ‹ôY[ìXô[H
	€Xô[[ŸKù”›Ÿ\êÿ\ŸJ
_JX¬àô]\õàà]à€\‹œHõX€\ÀXõ€⁄€X\öÀ\õ›»èÇàù]€à€\‹œHõX€\ÀXõ€⁄€X\öÀ[ò[YHX€\ÀXõ€⁄€X\öÀ[ò[YKXùàà\OHòù]€àà]KXX›[€èHòõ€⁄€X\öÀ[Xô[à]K\€›Hâ⁄[ô^Hà]OHâŸ\ÿÿ\R[
Xô[]J_Hà\öXK[Xô[HëY]	Ÿ\ÿÿ\R[
õ€⁄€X\öÀõò[YJ_Hò[YH[ô⁄‹ùXô[èÇà‹[à€\‹œHõX€\ÀXõ€⁄€X\öÀ[ò[YK[XZ[àèâŸ\ÿÿ\R[
õ€⁄€X\öÀõò[YJ_O‹‹[èÇà‹[à€\‹œHõX€\ÀXõ€⁄€X\öÀ\⁄‹ùèâŸ\ÿÿ\R[
ÿ‹ôY[ìXô[
_H0≠»	€Xô[[Ÿ_O‹‹[èÇàÿù]€èÇàù]€à€\‹œHõX€\ÀXõ€⁄€X\öÀXùàà\OHòù]€àà]KXX›[€èHòõ€⁄€X\öÀY€»à]K\€›Hâ⁄[ô^Hèë€œÿù]€èÇàù]€à€\‹œHõX€\À\[ãXùà	ÿõ€⁄€X\öÀú[õôY»	€X€\À[€â»à	…ﬂHà\OHòù]€àà]KXX›[€èHòõ€⁄€X\öÀ\[àà]K\€›Hâ⁄[ô^Hà]OHî[à\»\ú⁄\›[ùÿ‹ôY[à⁄‹ù›]èâÿõ€⁄€X\öÀú[õôY»	””â»à	‘SâﬂOÿù]€èÇàù]€à€\‹œHõX€\ÀXõ€⁄€X\öÀXùàà\OHòù]€àà]KXX›[€èHòõ€⁄€X\öÀ\ÿ]ôHà]K\€›Hâ⁄[ô^Hà]OHï\]H\»õ€⁄€X\ö»úõ€HH›\úô[ùX\öY]»èîÿ]ôOÿù]€èÇàù]€à€\‹œHõX€\ÀXõ€⁄€X\öÀXùàà\OHòù]€àà]KXX›[€èHòõ€⁄€X\öÀY[]Hà]K\€›Hâ⁄[ô^Hè∞Âœÿù]€èÇàŸ]èò¬àJKöõ⁄[ä	… N¬àBÇàù[ò›[€àô[ô\îÿ‹ôY[î[ú 
H¬à€€ú›ÿ⁄»Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTò€€ùõ€YHõX€\À\ÿ‹ôY[ã\[úÿ
N¬àYà
Yÿ⁄ Hô]\õé¬à€€ú›[ùöY\»H◊N¬àõ‹à
€€ú›XŸHŸàURP“◊‘P—T H¬àYà
\›]Kú]ZX⁄‘[ú÷‹XŸKöYJH€€ù[ùYN¬à[ùöY\Àú\⁄
¬à⁄[ôà	‹]ZX⁄…ÀàYàXŸKöYàù[ò[YNàXŸKõò[YKàò\ŸSXô[àÿ[ö]\ŸPõ€⁄€X\ö‘⁄‹ùXô[
XŸKõXô[
HXZŸT€X\ùõ€⁄€X\ö”Xô[
XŸKõò[YJBàJN¬àBà›]Kòõ€⁄€X\ö‹Àôõ‹ëXX⁄

õ€⁄€X\öÀ[ô^
HOà¬àYà
Xõ€⁄€X\ö»Xõ€⁄€X\öÀú[õôY
Hô]\õé¬à[ùöY\Àú\⁄
¬à⁄[ôà	ÿõ€⁄€X\ö…Àà[ô^àù[ò[YNàõ€⁄€X\öÀõò[YKàò\ŸSXô[àõ€⁄€X\ö‘ÿ‹ôY[ìXô[
õ€⁄€X\ö BàJN¬àJN¬àÿ⁄Àö[õô\íSHô\€€ôTÿ‹ôY[î[ìXô[ [ùöY\ KõX\
[ùûHOà¬à€€ú›X›[€àH[ùûKö⁄[ôOOH	‹]ZX⁄…¬à»]KXX›[€èHúXŸKY€»à]K\XŸOHâŸ\ÿÿ\R[
[ùûKöY
_Hòàà]KXX›[€èHòõ€⁄€X\öÀY€»à]K\€›HâŸ[ùûKö[ô^Hò¬à€€ú›€\‹”ò[YHH[ùûKö⁄[ôOOH	‹]ZX⁄…»»	€X€\À\[ã\]ZX⁄…»à	€X€\À\[ãX›\›€IŒ¬àô]\õàù]€à€\‹œHõX€\À\ÿ‹ôY[ã\[ãXùà	ÿ€\‹”ò[Y_Hà\OHòù]€àà	ÿX›[€üH]KYù[[Xô[HâŸ\ÿÿ\R[
[ùûKôù[ò[YJ_Hà]K\€X\ù[Xô[HâŸ\ÿÿ\R[
[ùûKõXô[
_Hà]OHíù[\»	Ÿ\ÿÿ\R[
[ùûKôù[ò[YJ_Hà\öXK[Xô[Híù[\»	Ÿ\ÿÿ\R[
[ùûKôù[ò[YJ_HèâŸ\ÿÿ\R[
[ùûKõXô[
_Oÿù]€èò¬àJKöõ⁄[ä	… N¬àYà
\’›X⁄^[›]X›]ôJ
JHö]€€ùõ€”X\

N¬àBÇàù[ò›[€à[ôPX›[€äù]€äH¬à€€ú›X›[€àHù]€ãô]\Ÿ]òX›[€é¬àYà
X›[€àOOH	›ŸŸ€KX[X[òŸK[Y[Xô\ã[X[òYŸ\â H¬àŸ][X[òŸSY[Xô\ìX[òYŸ\ë[òXõY
X[X[òŸSY[Xô\ìX[òYŸ\ë[òXõY

JN¬àô]\õé¬àBàYà
X›[€àOOH	‹XŸKY€… H¬à€€ú›XŸHHURP“◊‘P—TÀôö[ô
][HOà][KöYOOHù]€ãô]\Ÿ]úXŸJN¬àYà
XŸH	âàŸ]X\öY] XŸKõ]XŸKõôÀXŸKûõ€€JJH⁄›’ÿ\›
XŸKõò[YJN¬àô]\õé¬àBàYà
X›[€àOOH	‹]ZX⁄À\[â H»ŸŸ€T]ZX⁄‘[äù]€ãô]\Ÿ]úXŸJN»ô]\õé»BàYà
X›[€àOOH	ÿõ€⁄€X\öÀ\ÿ]ôI H»ÿ]ôPõ€⁄€X\ö ù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	ÿõ€⁄€X\öÀ[Xô[	 H»Y]õ€⁄€X\ö”Xô[
ù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	ÿõ€⁄€X\öÀY€… H»€–õ€⁄€X\ö ù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	ÿõ€⁄€X\öÀY[]I H»[]Põ€⁄€X\ö ù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	ÿõ€⁄€X\öÀ\[â H»ŸŸ€Põ€⁄€X\ö‘[äù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	€ùYŸK[Yù	 H»ùYŸP€€ùõ€
M
N»ô]\õé»BàYà
X›[€àOOH	€ùYŸK\öY⁄	 H»ùYŸP€€ùõ€

N»ô]\õé»BàYà
X›[€àOOH	€ùYŸK]\	 H»ùYŸP€€ùõ€
M
N»ô]\õé»BàYà
X›[€àOOH	€ùYŸKY›€â H»ùYŸP€€ùõ€

N»ô]\õé»BàYà
X›[€àOOH	€ùYŸK\ô\Ÿ]	 H»ô\Ÿ]ùYŸJ
N»ô]\õé»BàYà
X›[€àOOH	‹[ô[[Yù	 H»ùYŸT[ô[
Lç
N»ô]\õé»BàYà
X›[€àOOH	‹[ô[\öY⁄	 H»ùYŸT[ô[
ç
N»ô]\õé»BàYà
X›[€àOOH	‹[ô[]\	 H»ùYŸT[ô[
Lç
N»ô]\õé»BàYà
X›[€àOOH	‹[ô[Y›€â H»ùYŸT[ô[
ç
N»ô]\õé»BàYà
X›[€àOOH	›ŸŸ€KX€€[X[ô\ŸX\ò⁄	 H»Ÿ]€€[X[ôŸX\ò⁄‹[äX€€[X[ôŸX\ò⁄‹[äN»ô]\õé»BàYà
X›[€àOOH	ÿ€X\ãX€€[X[ô\ŸX\ò⁄	 H¬à€€[X[ôŸX\ò⁄]Y\ûHH	…Œ¬à€€ú›ŸX\ò⁄Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHŸ]KX€€[X[ô\ŸX\ò⁄X
N¬àYà
ŸX\ò⁄
H¬àŸX\ò⁄ùò[YHH	…Œ¬àŸX\ò⁄ôõÿ›\œÀä»ô]ô[ùÿ‹õ€àùYHJN¬àBà€€[X[ô[ù\ôòXŸP\TŸX\ò⁄

N¬à\]P€€[X[ô[ù\ôòXŸRXY\ä
N¬àô]\õé¬àBàYà
X›[€àOOH	€‹[ãZ[XŸ[ù\â H»‹[í[Ÿ[ù\ä
N»ô]\õé»BàYà
X›[€àOOH	€‹[ãX€€[X[ô\[]I H»‹[ê€€[X[ô[]J»ô]\õëõÿ›\Œàù]€àJN»ô]\õé»BàYà
X›[€àOOH	€‹[ã[X\[YX\›\ôI H»›\ùX\YX\›\ôJ
N»ô]\õé»BàYà
X›[€àOOH	€‹[ã\\ú€€ò[\ÿ][€ã\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	€^[›]	 N»ô]\õé»BàYà
X›[€àOOH	€‹[ã[^[›]\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	€^[›]	 N»ô]\õé»BàYà
X›[€àOOH	€‹[ã][YK\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	›[YI N»ô]\õé»BàYà
X›[€àOOH	€‹[ã]⁄Y[\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	›⁄Y[	 N»ô]\õé»BàYà
X›[€àOOH	€‹[ãZ[ú]\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	⁄[ú]	 N»ô]\õé»BàYà
X›[€àOOH	€‹[ã\⁄[\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	‹⁄[	 N»ô]\õé»BàYà
X›[€àOOH	€‹[ãXòX⁄›\XŸ[ùôI H»‹[î\ú€€ò[\ÿ][€î›Y[ 	ÿòX⁄›\	 N»ô]\õé»BàYà
X›[€àOOH	€‹[ã[õ›YöXÿ][€ã\›Y[… H»‹[î\ú€€ò[\ÿ][€î›Y[ 	€õ›YöXÿ][€ú… N»ô]\õé»BàYà
X›[€àOOH	€‹[ã\Ÿ]\]⁄^ò\ô	 H»‹[îŸ]\⁄^ò\ô
»X[ùX[àùYHJN»ô]\õé»BàYà
X›[€àOOH	›ŸŸ€KX€€[X[ôXò\â H»ŸŸ€P€€[X[ôò\ä
N»ô]\õé»BàYà
X›[€àOOH	›ŸŸ€KYX€€õ€^I H»Ÿ]X€€õ€^S[ŸJ\›]KôX€€õ€^S[ŸKùYJN»ô]\õé»BàYà
X›[€àOOH	€‹[ã]ôZX€K\›]\… H»ŸŸ€UôZX€P€ŸT›]\ 
N»ô]\õé»BàYà
X›[€àOOH	€‹[ã\ô\‹›\ôKXõÿ\ô	 H»ŸŸ€S‹\ò][€ò[ô\‹›\ôPõÿ\ô

N»ô]\õé»BàYà
X›[€àOOH	€‹[ã][ö][ÿÿ]‹â H»‹[ï[ö]ÿÿ]‹ä
N»ô]\õé»BàYà
X›[€àOOH	€‹[ã\Ÿ\‹⁄[€ãX€X[ù\	 H»‹[îŸ\‹⁄[€ê€X[ù\

N»ô]\õé»BàYà
X›[€àOOH	‹ôYúô\⁄\ô\‹›\ôKXõÿ\ô	 H»ôYúô\⁄‹\ò][€ò[ô\‹›\ôPõÿ\ô
ùYJN»ô]\õé»BàYà
X›[€àOOH	‹‹›[‹\ò][€ò[\⁄]ô\	 H»‹›‹\ò][€ò[⁄]ô\

N»ô]\õé»BàYà
X›[€àOOH	‹ÿÿ[ã]ò[ú‹‹ù\›ŸY\	 H»õ⁄Yÿÿ[ïò[ú‹‹ù›ŸY\]Y]YJ
Kù[ä]Y]YHOà⁄›’ÿ\›
]Y]YKõ[ô›»	‹]Y]YKõ[ô›Hò[ú‹‹ùZ\‹⁄[€â‹]Y]YKõ[ô›OOHH»	…»à	‹…ﬂHõ›[ôà	”õ»[X[òŸH]Y[ùò[ú‹‹ù»õ›[ô	 JN»ô]\õé»BàYà
X›[€àOOH	‹›\ù]ò[ú‹‹ù\›ŸY\	 H»›\ùò[ú‹‹ù›ŸY\

N»ô]\õé»BàYà
X›[€àOOH	‹›‹]ò[ú‹‹ù\›ŸY\	 H»›‹ò[ú‹‹ù›ŸY\

N»ô]\õé»BàYà
X›[€àOOH	‹ô]ûK]ò[ú‹‹ù\›ŸY\Y\ÿ€‹ô	 H»õ⁄Y‹›ò[ú‹‹ù›ŸY\\ÿ€‹ôô\‹ù
ò[ú‹‹ù›ŸY\ù[ù[YKõ\›ô\‹ù»X[ùX[àùYHJN»ô]\õé»BàYà
X›[€àOOH	Ÿ\€Z\‹À]ò[ú‹‹ù\›ŸY\\ô\‹ù	 H»\€Z\‹’ò[ú‹‹ù›ŸY\ô\‹ù

N»ô]\õé»BàYà
X›[€àOOH	‹ô\Ÿ]\Ÿ\‹⁄[€â H»ô\Ÿ]Ÿ\‹⁄[€î\ôõ‹õX[òŸJ
N»ô]\õé»BàYà
X›[€àOOH	ÿ€X\ã\^[›]Z\›‹ûI H»€X\î^[›]\›‹ûJ
N»ô]\õé»BàYà
X›[€àOOH	‹õŸö[K\ÿ]ôI H»ÿ]ôSX\õŸö[Jù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	‹õŸö[K[ÿY	 H»ÿYX\õŸö[Jù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	‹õŸö[KY[]I H»[]SX\õŸö[Jù[Xô\äù]€ãô]\Ÿ]ú€›
JN»ô]\õé»BàYà
X›[€àOOH	Ÿ^‹ùX€€ôöY… H»^‹ù€€⁄]€€ôöY 
N»ô]\õé»BàYà
X›[€àOOH	Ÿ^‹ù\ÿYôKX€€ôöY… H»^‹ùÿYôU€€⁄]Ÿ][ô‹ 
N»ô]\õé»BàYà
X›[€àOOH	⁄[\‹ùX€€ôöY… H»ÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHŸ]KZ[\‹ùX€€ôöYÀYö[WX
OÀò€X⁄œÀä
N»ô]\õé»BàYà
X›[€àOOH	›€€⁄]Yÿ›‹â H»õ⁄Yù[ï€€⁄]ÿ›‹ä
N»ô]\õé»BàYà
X›[€àOOH	›ŸŸ€K[X\Yù[ÿ‹ôY[â H»Ÿ]X\ù[ÿ‹ôY[ä\›]Kôù[ÿ‹ôY[ìX\
N»ô]\õé»BàYà
X›[€àOOH	€‹[ã]Xõ]\]ZX⁄À]⁄Y[	 H»‹[ïXõ]]ZX⁄’⁄Y[
ù[»X[ùX[àùYKô]\õëõÿ›\Œàù]€àJN»ô]\õé»BàYà
X›[€àOOH	€‹[ã]\]KXúöYYö[ô… H»‹[ï\]PúöYYö[ô »X[ùX[àùYHJN»ô]\õé»BàYà
X›[€àOOH	›ŸŸ€K\ÿYôK[[ŸI H»Ÿ]€€⁄]ÿYôS[ŸJ\›]KúÿYôS[ŸKô[òXõY
N»ô]\õé»BàYà
X›[€àOOH	‹ô\Ÿ]X€€ôöY… H»ô\Ÿ]€€⁄]€€ôöY›\ò][€ä
N»ô]\õé»BàYà
X›[€àOOH	Ÿ\ÿ€‹ô]\›	 H»\›\ÿ€‹ôŸXö€⁄ 
N»ô]\õé»BàYà
X›[€àOOH	Ÿ\ÿ€‹ôYŸ[ô\ò]K\‹›	 H»‹›\ÿ€‹ôö[ò[ò⁄X[ô\‹ù

N»ô]\õé»BàYà
X›[€àOOH	Ÿ\ÿ€‹ôX€X\â H»€X\ë\ÿ€‹ôŸXö€⁄ 
N»ô]\õé»BàYà
X›[€àOOH	Ÿö[ò[òŸKX\ò⁄]ôK\ÿÿ[â H»ÿÿ[ëö[ò[ò⁄X[\ò⁄]ôJ
N»ô]\õé»BàYà
X›[€àOOH	Ÿö[ò[òŸKX\ò⁄]ôKXÿ[òŸ[	 H»ÿ[òŸ[ö[ò[ò⁄X[\ò⁄]ôTÿÿ[ä
N»ô]\õé»BàYà
X›[€àOOH	Ÿö[ò[òŸKX\ò⁄]ôKY^‹ù	 H»^‹ùö[ò[ò⁄X[\ò⁄]ôJ
N»ô]\õé»BàYà
X›[€àOOH	Ÿö[ò[òŸKX\ò⁄]ôKZ[\‹ù	 H»ÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHŸ]KZ[\‹ùYö[ò[òŸKYö[WX
OÀò€X⁄œÀä
N»ô]\õé»BàYà
X›[€àOOH	Ÿö[ò[òŸKX\ò⁄]ôKX€X\â H»€X\ëö[ò[ò⁄X[\ò⁄]ôJ
N»ô]\õé»BàYà
X›[€àOOH	Ÿö[ò[òŸK\ù[\À\ôYúô\⁄	 H»ôYúô\⁄ö[ò[ò⁄X[[ù[YŸ[òŸQôYY ùYJKù[ä

HOà»ô[ô\ëö[ò[òŸUò][›]\ 
N»⁄›’ÿ\›
	—⁄]Xàö[ò[ò⁄X[[ù[YŸ[òŸHôYúô\⁄Y	 N»JN»ô]\õé»BàYà
X›[€àOOH	›\›\^[›]Yõ\⁄	 H¬à€€ú›\›[[›[ùHX]õX^
Lù[Xô\äÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YHŸ]K\Ÿ][ôœHú^[›]]\›X[[›[ùóX
OÀùò[YJH›]Kú^[›]õ\⁄ùô\⁄€
N¬à€€ú›öYŸŸ\ôYHöYŸŸ\î^[›]õ\⁄
\›[[›[ùùYK»€›\òŸNà	‹\ú€€ò[	Àÿ\[€éà	—[Y\ôŸ[òﬁHô\‹€úŸH\›	»JN¬à⁄›’ÿ\›
öYŸŸ\ôY»	—[Y\ôŸ[òﬁHõ\⁄\›	»à	—[Y\ôŸ[òﬁHõ\⁄[ò]òZ[XõNàX\õ›]X›Y	 N¬àô]\õé¬àBàYà
X›[€àOOH	‹[ô[\ô\Ÿ]	 Hô\Ÿ][ô[‹⁄][€ä
N¬àBàù[ò›[€à[ôQ\ÿ€‹ôö[ò[ò⁄X[Ÿ][ô–⁄[ôŸJ\ôŸ]Ÿ][ô H¬àYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ô]ŸXö€⁄… H¬àûH¬àÿ]ôQ\ÿ€‹ôŸXö€⁄’\õ
\ôŸ]ùò[YJN¬àŸ]\ÿ€‹ô›]\ \ôŸ]ùò[YH»	’ŸXö€⁄»ÿ]ôYŸX›\ô[H[à[\\õ[€öŸ^H›‹òYŸKâ»à	’ŸXö€⁄»ô[[›ôYâÀ	Ÿ€€Ÿ	 N¬àHÿ]⁄
\úäH¬àŸ]\ÿ€‹ô›]\ \úèÀõY\‹ÿYŸH	’ŸXö€⁄»Tì\»[ùò[YâÀ	ÿòY	 N¬àBàô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ô[ò[YI H¬à›]Kô\ÿ€‹ôô\‹ùùŸXö€⁄”ò[YHH›ö[ô \ôŸ]ùò[YH	”Z\‹⁄[€ê⁄YYàö[ò[òŸI Kùö[J
Kú€XŸJ
H	”Z\‹⁄[€ê⁄YYàö[ò[òŸIŒ¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ô]‹Xÿ]Y€‹öY\… H¬à›]Kô\ÿ€‹ôô\‹ùù‹ÿ]Y€‹öY\»HÃÀKKö[ò€Y\ ù[Xô\ä\ôŸ]ùò[YJJH»ù[Xô\ä\ôŸ]ùò[YJHàN¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ô\\ö[Ÿ	 H¬à›]Kô\ÿ€‹ôô\‹ùú\ö[ŸH…›Ÿ^IÀ	ﬁY\›\ô^IÀ	€\›ç	À	€\›…À	€\›Ã	À	€\›L	À	€\›N	À	€\›ÕçIÀ	ÿ[]òZ[XõIÀ	‹Ÿ\‹⁄[€âÀ	‹⁄[òŸS\›	À	ÿ›\›€I◊Kö[ò€Y\ \ôŸ]ùò[YJH»\ôŸ]ùò[YHà	›Ÿ^IŒ¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ôX›\›€K\›\ù	»Ÿ][ô»OOH	Ÿ\ÿ€‹ôX›\›€KY[ô	 H¬à€€ú›Ÿ^HHŸ][ô»OOH	Ÿ\ÿ€‹ôX›\›€K\›\ù	»»	ÿ›\›€T›\ù	»à	ÿ›\›€Q[ô	Œ¬àYà
◊óÕKWÃüKWÃüI›Kù\›
›ö[ô \ôŸ]ùò[YH	… JJH›]Kô\ÿ€‹ôô\‹ù⁄Ÿ^WHH›ö[ô \ôŸ]ùò[YJN¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ôX€€\\ö\€€â H¬à›]Kô\ÿ€‹ôô\‹ùö[ò€YP€€\\ö\€€àH›ö[ô \ôŸ]ùò[YJHOOH	Ÿò[ŸIŒ¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ôX⁄\ù	 H¬à›]Kô\ÿ€‹ôô\‹ùö[ò€YP⁄\ùH›ö[ô \ôŸ]ùò[YJHOOH	Ÿò[ŸIŒ¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ôX€€\^]I H¬à›]Kô\ÿ€‹ôô\‹ùò€€\^]HHõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]J\ôŸ]ùò[YJN¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿ\ÿ€‹ô\ö\⁄…»Ÿ][ô»OOH	Ÿ\ÿ€‹ôYõ‹ôXÿ\›	 H¬à€€ú›Ÿ^HHŸ][ô»OOH	Ÿ\ÿ€‹ô\ö\⁄…»»	⁄[ò€YTö\⁄…»à	⁄[ò€YQõ‹ôXÿ\›	Œ¬à›]Kô\ÿ€‹ôô\‹ù⁄Ÿ^WHH›ö[ô \ôŸ]ùò[YJHOOH	Ÿò[ŸIŒ¬à[ùò[Y]Q\ÿ€‹ôö[ò[ò⁄X[ô]öY] 
N¬àÿ]ôT›]J
N»\]URJ
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿö[ò[òŸK]ò][Y[òXõY	 H¬à›]Kôö[ò[ò⁄X[ò][ô[òXõYH›ö[ô \ôŸ]ùò[YJHOOH	Ÿò[ŸIŒ¬àÿ]ôT›]J
N»\]URJ
N¬àŸ]ö[ò[òŸUò][›]\ ›]Kôö[ò[ò⁄X[ò][ô[òXõY»	”ÿÿ[ö[ò[ò⁄X[\ò⁄]ôH[òXõYâ»à	”ÿÿ[ö[ò[ò⁄X[\ò⁄]ôH\ÿXõY»ô\‹ù»⁄[ÿÿ[àZ\‹⁄[€ê⁄YYà\ôX›H⁄]›]ô]Z[ö[ô»\›‹ûKâÀ	€ô]]ò[	 N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿö[ò[òŸK]ò][\ô][ù[€â H¬à›]Kôö[ò[ò⁄X[ò][úô][ù[€ë^\»H›ö[ô \ôŸ]ùò[YJHOOH	ÿ[	»»	ÿ[	»à
ŒLNÕçKÃÃNçWKö[ò€Y\ ù[Xô\ä\ôŸ]ùò[YJJH»ù[Xô\ä\ôŸ]ùò[YJHà	ÿ[	 N¬àÿ]ôT›]J
N»\]URJ
N»ô[ô\ëö[ò[òŸUò][›]\ 
N¬àô]\õàùYN¬àBàYà
Ÿ][ô»OOH	Ÿö[ò[òŸK\ù[KYôYY	 H¬à›]Kôö[ò[ò⁄X[ò][úù[QôYY[òXõYH›ö[ô \ôŸ]ùò[YJHOOH	Ÿò[ŸIŒ¬àÿ]ôT›]J
N¬àôYúô\⁄ö[ò[ò⁄X[[ù[YŸ[òŸQôYY ùYJKù[ä

HOà»\]URJ
N»ô[ô\ëö[ò[òŸUò][›]\ 
N»JN¬àô]\õàùYN¬àBàô]\õàò[ŸN¬àBàù[ò›[€à[ôQ]öXŸS^[›]Ÿ][ô–⁄[ôŸJ\ôŸ]Ÿ][ô H¬à€€ú›ô^ò[YHH…ÿ]]…À	€€âÀ	€Ÿôâ◊Kö[ò€Y\ ›ö[ô \ôŸ]ùò[YJJH»›ö[ô \ôŸ]ùò[YJHà	ÿ]]…Œ¬à€€ú›ô]ö[›\”^[›]HX›]ôQ]öXŸS^[›]¬àYà
Ÿ][ô»OOH	€[ÿö[K[[ŸI H¬à›]Kõ[ÿö[S[ŸHHô^ò[YN¬àYà
ô^ò[YHOOH	€€â H›]KùXõ][ŸHH	€ŸôâŒ¬àH[ŸHYà
Ÿ][ô»OOH	›Xõ][[ŸI H¬à›]KùXõ][ŸHHô^ò[YN¬àYà
ô^ò[YHOOH	€€â H›]Kõ[ÿö[S[ŸHH	€ŸôâŒ¬àH[ŸHô]\õàò[ŸN¬àÿ]ôT›]J
N¬à\Tõ€›]öXù]\ 
N¬àôYúô\⁄Xõ][ŸUZJ
N¬àYà
ô]ö[›\”^[›]OOHX›]ôQ]öXŸS^[›]	âàZ\’›X⁄^[›]X›]ôJ
JH¬à€X\ïXõ][ô[⁄^ö[ô 
N¬à€X\ïXõ]ÿ⁄‘⁄^ö[ô 
N¬àBàö]€€ùõ€”X\

N¬à‹⁄][€î[ô[›ô\õ^JùYJN¬à⁄›’ÿ\›
X›]ôQ]öXŸS^[›]OOH	€[ÿö[I»»	⁄S‘»[ÿö[H[ŸHX›]ôI»àX›]ôQ]öXŸS^[›]OOH	›Xõ]	»»	’Xõ][ŸHX›]ôI»à	—\⁄›‹^[›]X›]ôI N¬àô]\õàùYN»Bàù[ò›[€à[ôTŸ][ô–⁄[ôŸJ\ôŸ]
H¬à€€ú›Ÿ][ô»H\ôŸ]ô]\Ÿ]úŸ][ôŒ¬àYà
\Ÿ][ô Hô]\õé¬àYà
[ôQ]öXŸS^[›]Ÿ][ô–⁄[ôŸJ\ôŸ]Ÿ][ô JHô]\õé¬àYà
Ÿ][ô»OOH	Ÿ[ú⁄]KY\⁄›‹	»Ÿ][ô»OOH	Ÿ[ú⁄]K]Xõ]	 H¬à€€ú›Ÿ^HHŸ][ô»OOH	Ÿ[ú⁄]KY\⁄›‹	»»	Ÿ\⁄›‹	»à	›Xõ]	Œ¬à›]Kö[ù\ôòXŸQ[ú⁄]V⁄Ÿ^WHH””SPSë—Sî“UQTÀö[ò€Y\ ›ö[ô \ôŸ]ùò[YJJH»›ö[ô \ôŸ]ùò[YJHà	‹›[ô\ô	Œ¬àÿ]ôT›]J
N»\Tõ€›]öXù]\ 
N»ôYúô\⁄Xõ][ŸUZJ
N»ö]€€ùõ€”X\

N»‹⁄][€î[ô[›ô\õ^JùYJN»\]URJ
N¬à⁄›’ÿ\›
	⁄Ÿ^HOOH	Ÿ\⁄›‹	»»	—\⁄›‹	»à	’Xõ]	ﬂH[ú⁄]Nà	‹›]Kö[ù\ôòXŸQ[ú⁄]V⁄Ÿ^WHOOH	ÿ€€[X[ô	»»	–€€[X[ôŸ[ùôI»à›]Kö[ù\ôòXŸQ[ú⁄]V⁄Ÿ^W_X
N¬àô]\õé¬àBàYà
◊ú]ZX⁄À]⁄Y[\€›VÃM◊I›Kù\›
Ÿ][ô JH¬à€€ú›[ô^Hù[Xô\äŸ][ôÀú€XŸJLJJN¬à€€ú›€›Hõ‹õX[\ŸT]ZX⁄’⁄Y[€›
\ôŸ]ùò[YJH»⁄[ôà	ÿX›[€âÀYàQêUS‘URP“◊’“QS–P’S”î÷⁄[ô^H	ÿ€€[X[ô[]I»N¬à›]Kú]ZX⁄’⁄Y[ú€›÷⁄[ô^HH€›¬à›]Kú]ZX⁄’⁄Y[òX›[€ú»H›]Kú]ZX⁄’⁄Y[ú€›Àú€XŸJäKõX\
][HOà][Kö⁄[ôOOH	ÿX›[€â»	âàURP“◊’“QS–P’S”î÷⁄][KöYH»][KöYà	ÿ€€[X[ô[]I N¬àÿ]ôT›]J
N»\]URJ
N¬à⁄›’ÿ\›
]ZX⁄»⁄Y[€›	⁄[ô^
»_Nà	‹]ZX⁄’⁄Y[€›Y]J€›
KõXô[X
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	€XZõ‹ãZ[ò⁄Y[ù[Z[ö[][I H¬à›]KõXZõ‹í[ò⁄Y[ùôYYõZ[ö[][P‹ôY]»HPRì‘ó“Sê“QSï—ëQQ”RSíSUSW”‘S”îÀö[ò€Y\ ù[Xô\ä\ôŸ]ùò[YJJH»ù[Xô\ä\ôŸ]ùò[YJHàçL¬àÿ]ôT›]J
N¬à\]URJ
N¬àôYúô\⁄Z\‹⁄[€î€ò\⁄› 
N¬àÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\ä
N¬à⁄›’ÿ\›
XZõ‹à[ò⁄Y[ùôYYà	Ÿõ‹õX]‹\ò][€ò[€€\X›‹ôY] ›]KõXZõ‹í[ò⁄Y[ùôYYõZ[ö[][P‹ôY] _J»‹ôY]ÿ
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	ÿ€›ô\òYŸK\òY]\… H¬à›]Kò€›ô\òYŸKúòY]\”ZHHù[Xô\ä\ôŸ]ùò[YJHL¬àÿ]ôT›]J
N¬à\]URJ
N¬àÿ⁄Y[P€›ô\òYŸTôYúô\⁄

N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	›ò[ú‹‹ù\›ŸY\Y[^I H¬à›]Kùò[ú‹‹ù›ŸY\ô[^S\»HêSî‘‘ï‘’—QT—SVW”‘S”îÀö[ò€Y\ ù[Xô\ä\ôŸ]ùò[YJJH»ù[Xô\ä\ôŸ]ùò[YJHàå¬àÿ]ôT›]J
N»\]URJ
N¬à⁄›’ÿ\›
ò[ú‹‹ù›ŸY\[^Nà	‹›]Kùò[ú‹‹ù›ŸY\ô[^S\»»L\ÿ
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	›ò[ú‹‹ù\›ŸY\[X^	 H¬à›]Kùò[ú‹‹ù›ŸY\õX^\îù[àHX]úõ›[ô
€[\
\ôŸ]ùò[YKKêSî‘‘ï‘’—QT”PV‘ëTUQT’ÀçJJN¬àÿ]ôT›]J
N»\]URJ
N¬à⁄›’ÿ\›
ò[ú‹‹ù›ŸY\X^[][Nà	‹›]Kùò[ú‹‹ù›ŸY\õX^\îù[üX
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	‹ô\€›\òŸKYÿ\\òY]\… H¬à›]Kúô\€›\òŸQÿ\úòY]\”ZHHëT”’Tê—W—–T‘êQUT◊”‘S”îÀö[ò€Y\ ù[Xô\ä\ôŸ]ùò[YJJH»ù[Xô\ä\ôŸ]ùò[YJHàçN¬àô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kò€X\ä
N¬à⁄›’ÿ\›
ô\€›\òŸHÿ\òY]\Œà	‹›]Kúô\€›\òŸQÿ\úòY]\”Z_[ZX
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	‹›X⁄À]ô\⁄€	 H¬à›]Kú›X⁄—]X›‹ãùô\⁄€Z[àHX]úõ›[ô
€[\
\ôŸ]ùò[YK’P“◊”RSó”RSïUTÀ’P“◊”PV”RSïUTÀå
JN¬àÿ]ôT›]J
N¬à\]URJ
N¬àÿ⁄Y[T›X⁄”Z\‹⁄[€îôYúô\⁄

N¬à⁄›’ÿ\›
›X⁄»Z\‹⁄[€úŒà	‹›]Kú›X⁄—]X›‹ãùô\⁄€Z[üHZ[ù]\ÿ
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	ÿ[X[òŸKX‹ôY][Z[ö[][I H¬à›]Kò[X[òŸP‹ôY]Z[ö[][HHÃLLMLåKö[ò€Y\ ù[Xô\ä\ôŸ]ùò[YJJH»ù[Xô\ä\ôŸ]ùò[YJHà¬àÿ]ôT›]J
N¬à\]URJ
N¬àÿ⁄Y[P[X[òŸP‹ôY]ôYúô\⁄

N¬à⁄›’ÿ\›
›]Kò[X[òŸP‹ôY]Z[ö[][H»[X[òŸH‹ôY]Œà	‹›]Kò[X[òŸP‹ôY]Z[ö[][H»LR ÿà	–[X[òŸH‹ôY]Œà[ò[Y\… N¬àô]\õé¬àBàYà
[ôQ\ÿ€‹ôö[ò[ò⁄X[Ÿ][ô–⁄[ôŸJ\ôŸ]Ÿ][ô JHô]\õé¬àYà
Ÿ][ô»OOH	‹^[›]][\]I H¬à›]Kú^[›]õ\⁄ù[\]HHVS’U’STUT÷›\ôŸ]ùò[YWH»\ôŸ]ùò[YHà	Ÿ›MIŒ¬à\‹‹ŸT^[›]YYXP]Y[ 
N¬àÿ]ôT›]J
N¬à\]URJ
N¬à€€ú›‹›Y›YHHVS’U”QQPW‘”’Së÷‹›]Kú^[›]õ\⁄ù[\]WN¬à⁄›’ÿ\›
‹›Y›YBà»	‹^[›][\]SY]J›]Kú^[›]õ\⁄ù[\]JKõXô[H0≠»	⁄‹›Y›YKõXô[HôXYXàà	‹^[›][\]SY]J›]Kú^[›]õ\⁄ù[\]JKõXô[H^[›][\]X
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	‹^[›]]ô\⁄€	 H¬à›]Kú^[›]õ\⁄ùô\⁄€HX]úõ›[ô
€[\
\ôŸ]ùò[YKLLL
JN¬àÿ]ôT›]J
N¬à\]URJ
N¬à⁄›’ÿ\›
^[›]õ\⁄à	‹›]Kú^[›]õ\⁄ùô\⁄€ù”ÿÿ[T›ö[ô 
_Jÿ
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	‹^[›]Y\ò][€â H¬à›]Kú^[›]õ\⁄ô\ò][€ì\»Hõ‹õX[\ŸT^[›]õ\⁄\ò][€äù[Xô\ä\ôŸ]ùò[YJH
àL
N¬àÿ]ôT›]J
N¬à\]URJ
N¬à⁄›’ÿ\›
^[›]õ\⁄à	‹›]Kú^[›]õ\⁄ô\ò][€ì\»»LHŸX€€ôÿ
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	‹^[›]]õ€[YI H¬à›]Kú^[›]õ\⁄ú€›[ôõ€[YHH€[\
\ôŸ]ùò[YKKåÕJN¬àYà
^[›]YYXP]Y[»	âà\^[›]YYXP]Y[Àú]\ŸY
H^[›]YYXP]Y[Àùõ€[YHH›]Kú^[›]õ\⁄ú€›[ôõ€[YN¬àÿ]ôT›]J
N¬à\]URJ
N¬àô]\õé¬àBàYà
Ÿ][ô»OOH	‹^[›]]\›X[[›[ù	 Hô]\õé¬àBàù[ò›[€à\]UZUŸŸ€P€\‹ [[Y[ù€\‹”ò[YK[òXõY
H¬àYà
Y[[Y[ùÀò€\‹”\›
Hô]\õàò[ŸN¬à€€ú›ô^Hõ€€X[ä[òXõY
N¬àYà
[[Y[ùò€\‹”\›ò€€ùZ[ú €\‹”ò[YJHOOHô^
Hô]\õàò[ŸN¬à[[Y[ùò€\‹”\›ùŸŸ€J€\‹”ò[YKô^
N¬àô]\õàùYN¬àBÇàù[ò›[€à\]UZTŸ]›[Tõ‹\ùJ›[Kò[YKò[YKö[‹ö]HH	… H¬àYà
\›[H\[Ÿà›[KôŸ]õ‹\ùUò[YHOOH	Ÿù[ò›[€â»\[Ÿà›[KúŸ]õ‹\ùHOOH	Ÿù[ò›[€â Hô]\õàò[ŸN¬à€€ú›ô^ò[YHH›ö[ô ò[YJN¬à€€ú›ô^ö[‹ö]HH›ö[ô ö[‹ö]H	… N¬àYà
›[KôŸ]õ‹\ùUò[YJò[YJHOOHô^ò[YH	âà›[KôŸ]õ‹\ùTö[‹ö]Jò[YJHOOHô^ö[‹ö]JHô]\õàò[ŸN¬à›[KúŸ]õ‹\ùJò[YKô^ò[YKô^ö[‹ö]JN¬àô]\õàùYN¬àBÇàù[ò›[€à\]UZTŸ]]öXù]J[[Y[ùò[YKò[YJH¬àYà
Y[[Y[ù\[Ÿà[[Y[ùôŸ]]öXù]HOOH	Ÿù[ò›[€â»\[Ÿà[[Y[ùúŸ]]öXù]HOOH	Ÿù[ò›[€â Hô]\õàò[ŸN¬à€€ú›ô^H›ö[ô ò[YJN¬àYà
[[Y[ùôŸ]]öXù]Jò[YJHOOHô^
Hô]\õàò[ŸN¬à[[Y[ùúŸ]]öXù]Jò[YKô^
N¬àô]\õàùYN¬àBÇàù[ò›[€à\]UZTŸ]]\Ÿ]
[[Y[ùŸ^Kò[YJH¬àYà
Y[[Y[ùÀô]\Ÿ]
Hô]\õàò[ŸN¬à€€ú›ô^H›ö[ô ò[YJN¬àYà
[[Y[ùô]\Ÿ]⁄Ÿ^WHOOHô^
Hô]\õàò[ŸN¬à[[Y[ùô]\Ÿ]⁄Ÿ^WHHô^¬àô]\õàùYN¬àBÇàù[ò›[€à\]UZTŸ]õ‹\ùJ[[Y[ùõ‹\ùKò[YJH¬àYà
Y[[Y[ù
Hô]\õàò[ŸN¬àYà
ÿöôX›ö\ [[Y[ù‹õ‹\ùWKò[YJJHô]\õàò[ŸN¬à[[Y[ù‹õ‹\ùWHHò[YN¬àô]\õàùYN¬àBÇàù[ò›[€à\]UZTŸ]^
[[Y[ùò[YJH¬àô]\õà\]UZTŸ]õ‹\ùJ[[Y[ù	›^€€ù[ù	À›ö[ô ò[YJJN¬àBÇàù[ò›[€à\]URJ
H¬à\Tõ€›]öXù]\ 
N¬àYà
›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY	âà‹\ò][€ò[›\ù\€€\]JHÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\ä
N¬à[ŸHYà
\›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY
Hô[[›ôSXZõ‹í[ò⁄Y[ùôYY

N¬à€€ú›€€ùõ€Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
€€ùõ€
H¬à€€ú›ÿ⁄‘‹⁄][€àHX›]ôQÿ⁄‘‹⁄][€ä
N¬àõ‹à
€€ú›‹»ŸàÿöôX›öŸ^\ ‘“US”î JH\]UZUŸŸ€P€\‹ €€ùõ€X€\À\‹ÀI‹‹ﬂXÿ⁄‘‹⁄][€àOOH‹ N¬à\]UZTŸ]›[Tõ‹\ùJ€€ùõ€ú›[K	ÀK[X€\À[ùYŸK^	À	‹›]KõùYŸKû\
N¬à\]UZTŸ]›[Tõ‹\ùJ€€ùõ€ú›[K	ÀK[X€\À[ùYŸK^IÀ	‹›]KõùYŸKû_\
N¬à€€⁄]\P€€[X[ôò\î›]J€€ùõ€
N¬à€€ú›Y[ùPù]€àH€€ùõ€ú]Y\ûTŸ[X›‹ä	ÀõX€\À[Y[ùKXùâ N¬à€€ú›Y[ùPö[ô[ô»H›]Kö[ú]›Y[Àö›Ÿ^\ÀõY[ùH	¯†%	Œ¬à\]UZTŸ]^
Y[ùPù]€èÀú]Y\ûTŸ[X›‹ä	ÀõX€\À[Y[ùKZŸ^I KY[ùPö[ô[ô N¬à\]UZTŸ]]öXù]JY[ùPù]€ã	ÿ\öXKZŸ^\⁄‹ù›]…À›]Kö[ú]›Y[Àö›Ÿ^\ÀõY[ùH	… N¬à€€ùõ€ú]Y\ûTŸ[X›‹ê[
	÷Ÿ]K]ŸŸ€WI Kôõ‹ëXX⁄
ù]€àOà¬à€€ú›ö[ô[ô»H›]Kö[ú]›Y[Àö›Ÿ^\÷ÿù]€ãô]\Ÿ]ùŸŸ€WH	…Œ¬à\]UZTŸ]^
ù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀYõÿ]ZŸ^I Kö[ô[ô»	¯†%	 N¬à\]UZTŸ]]öXù]Jù]€ã	ÿ\öXKZŸ^\⁄‹ù›]…Àö[ô[ô N¬àJN¬àõ‹à
€€ú›ÿX›[€ã€€[X[ôHŸàÿöôX›ô[ùöY\ »	€‹[ã]ôZX€K\›]\…Œà	›ôZX€P€Ÿ\…À	€‹[ã\ô\‹›\ôKXõÿ\ô	Œà	‹ô\‹›\ôPõÿ\ô	À	€‹[ãX€€[X[ô\[]IŒà	‹[]I»JJH¬à€€ú›ù]€àH\úò^Kôúõ€J€€ùõ€ú]Y\ûTŸ[X›‹ê[
	÷Ÿ]KXX›[€óI JKôö[ô
][HOà][Kô]\Ÿ]òX›[€àOOHX›[€äN¬à€€ú›ö[ô[ô»H›]Kö[ú]›Y[Àö›Ÿ^\÷ÿ€€[X[ôH	…Œ¬à\]UZTŸ]^
ù]€èÀú]Y\ûTŸ[X›‹ä	ÀõX€\ÀYõÿ]ZŸ^I Kö[ô[ô»	¯†%	 N¬à\]UZTŸ]]öXù]Jù]€ã	ÿ\öXKZŸ^\⁄‹ù›]…Àö[ô[ô N¬àBà€€ú›€€ùõ€ŸŸ€Uò[Y\»H¬à[X[òŸSZ\‹⁄[€úŒà›]Kùö\⁄Xö[]Kò[X[òŸSZ\‹⁄[€úÀà^SZ\‹⁄[€úŒà›]Kùö\⁄Xö[]Kõ^SZ\‹⁄[€úÀàôZX€\Œà›]Kùö\⁄Xö[]KùôZX€\ÀàùZ[[ô‹Œà›]Kùö\⁄Xö[]KòùZ[[ô‹Àà[X[òŸP‹ôY]Œà›]Kò[X[òŸP‹ôY]ÀàZ\‹⁄[€êYŸNà›]KõZ\‹⁄[€êYŸKàò[ú‹‹ùÿ]⁄\éà›]Kùò[ú‹‹ùÿ]⁄\ãà[ö]€€[Z]Y[ùà›]Kù[ö]€€[Z]Y[ùà›X⁄—]X›‹éà›]Kú›X⁄—]X›‹ãô[òXõYàN¬à€€ùõ€ú]Y\ûTŸ[X›‹ê[
	÷Ÿ]K]ŸŸ€WI Kôõ‹ëXX⁄
ùàOà¬à€€ú›€àHõ€€X[ä€€ùõ€ŸŸ€Uò[Y\÷ÿùãô]\Ÿ]ùŸŸ€WJN¬à\]UZUŸŸ€P€\‹ ùã	€X€\À[€âÀ€äN¬à\]UZTŸ]]öXù]Jùã	ÿ\öXK\ô\‹ŸY	À›ö[ô €äJN¬à\]UZTŸ]]\Ÿ]
ùã	€X€\‘›]IÀ€à»	€€â»à	€Ÿôâ N¬à\]UZTŸ]^
ùãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€ùõ€\›]I K€à»	””â»à	”—ëâ N¬à€€ú›€€ùõ€ò[YHHùãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀYõÿ][Xô[Y\⁄›‹	 OÀù^€€ù[ùùãù]H	”X\€€ùõ€	Œ¬à\]UZTŸ]]öXù]Jùã	ÿ\öXK[Xô[	À	ÿ€€ùõ€ò[Y_Nà	€€à»	€€â»à	€ŸôâﬂKà	ÿùãù]H	…ﬂXùö[J
JN¬àJN¬à€€ú›ôZX€T›]\–ù]€àH€€ùõ€ú]Y\ûTŸ[X›‹ä	÷Ÿ]KXX›[€èHõ‹[ã]ôZX€K\›]\»óI N¬àYà
ôZX€T›]\–ù]€äH¬à€€ú›‹[àHõ€€X[äÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTùôZX€T›]\“Y
OÀò€\‹”\›Àò€€ùZ[ú 	€X€\À[‹[â JN¬à\]UZUŸŸ€P€\‹ ôZX€T›]\–ù]€ã	€X€\À[€âÀ‹[äN¬à\]UZTŸ]]öXù]JôZX€T›]\–ù]€ã	ÿ\öXK\ô\‹ŸY	À›ö[ô ‹[äJN¬à\]UZTŸ]]\Ÿ]
ôZX€T›]\–ù]€ã	€X€\‘›]IÀ‹[à»	€€â»à	€Ÿôâ N¬à\]UZTŸ]^
ôZX€T›]\–ù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€ùõ€\›]I K‹[à»	–P’UëI»à	”—ëâ N¬à\]UZTŸ]]öXù]JôZX€T›]\–ù]€ã	ÿ\öXK[Xô[	ÀôZX€H€ŸH›]\Œà	€‹[à»	ÿX›]ôI»à	€ŸôâﬂKà⁄‹ù›]à	‹›]Kö[ú]›Y[Àö›Ÿ^\ÀùôZX€P€Ÿ\»	€õ€ôIﬂKò
N¬àBà€€ú›ô\‹›\ôPõÿ\ôù]€àH€€ùõ€ú]Y\ûTŸ[X›‹ä	÷Ÿ]KXX›[€èHõ‹[ã\ô\‹›\ôKXõÿ\ôóI N¬àYà
ô\‹›\ôPõÿ\ôù]€äH¬à€€ú›‹[àH‹\ò][€ò[ô\‹›\ôPõÿ\ô‹[ä
N¬à\]UZUŸŸ€P€\‹ ô\‹›\ôPõÿ\ôù]€ã	€X€\À[€âÀ‹[äN¬à\]UZTŸ]]öXù]Jô\‹›\ôPõÿ\ôù]€ã	ÿ\öXK\ô\‹ŸY	À›ö[ô ‹[äJN¬à\]UZTŸ]]\Ÿ]
ô\‹›\ôPõÿ\ôù]€ã	€X€\‘›]IÀ‹[à»	€€â»à	€Ÿôâ N¬à\]UZTŸ]^
ô\‹›\ôPõÿ\ôù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€ùõ€\›]I K‹[à»	–P’UëI»à	”—ëâ N¬à\]UZTŸ]]öXù]Jô\‹›\ôPõÿ\ôù]€ã	ÿ\öXK[Xô[	À‹\ò][€ò[ô\‹›\ôHõÿ\ôà	€‹[à»	ÿX›]ôI»à	€ŸôâﬂKà⁄‹ù›]à	‹›]Kö[ú]›Y[Àö›Ÿ^\Àúô\‹›\ôPõÿ\ô	€õ€ôIﬂKò
N¬àBà€€ú›€€[X[ô[]Pù]€àH€€ùõ€ú]Y\ûTŸ[X›‹ä	÷Ÿ]KXX›[€èHõ‹[ãX€€[X[ô\[]HóI N¬àYà
€€[X[ô[]Pù]€äH¬à€€ú›‹[àHõ€€X[ä€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€[X[ô[]RY
JN¬à\]UZUŸŸ€P€\‹ €€[X[ô[]Pù]€ã	€X€\À[€âÀ‹[äN¬à\]UZTŸ]]öXù]J€€[X[ô[]Pù]€ã	ÿ\öXK\ô\‹ŸY	À›ö[ô ‹[äJN¬à\]UZTŸ]]\Ÿ]
€€[X[ô[]Pù]€ã	€X€\‘›]IÀ‹[à»	€€â»à	€Ÿôâ N¬à\]UZTŸ]^
€€[X[ô[]Pù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€ùõ€\›]I K‹[à»	–P’UëI»à	‘ëPQI N¬à\]UZTŸ]]öXù]J€€[X[ô[]Pù]€ã	ÿ\öXK[Xô[	À€€⁄]€€[X[ô[]Nà	€‹[à»	ÿX›]ôI»à	‹ôXYIﬂKà⁄‹ù›]à	‹›]Kö[ú]›Y[Àö›Ÿ^\Àú[]H	€õ€ôIﬂKò
N¬àBàﬁ[ò”X\YX\›\ôU€€ò\êù]€ä
N¬à€€ú›X€€õ€^Pù]€àH€€ùõ€ú]Y\ûTŸ[X›‹ä	ÀõX€\ÀYX€€õ€^KXùâ N¬àYà
X€€õ€^Pù]€äH¬à€€ú›€àHõ€€X[ä›]KôX€€õ€^S[ŸJN¬à€€ú›Xô[H€à»	—\ÿXõHX€€õ€^H[ŸI»à	—[òXõHX€€õ€^H[ŸIŒ¬à\]UZUŸŸ€P€\‹ X€€õ€^Pù]€ã	€X€\À[€âÀ€äN¬à\]UZTŸ]]öXù]JX€€õ€^Pù]€ã	ÿ\öXK\ô\‹ŸY	À›ö[ô €äJN¬à\]UZTŸ]]öXù]JX€€õ€^Pù]€ã	ÿ\öXK[Xô[	ÀXô[
N¬à\]UZTŸ]õ‹\ùJX€€õ€^Pù]€ã	›]IÀXô[
N¬à\]UZTŸ]]\Ÿ]
X€€õ€^Pù]€ã	€X€\‘›]IÀ€à»	€€â»à	€Ÿôâ N¬à\]UZTŸ]^
X€€õ€^Pù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\ÀX€€ùõ€\›]I K€à»	–P’UëI»à	”—ëâ N¬àBàBàYà
\[ô[
Hô]\õé¬àôYúô\⁄Xõ][ŸUZJ[ô[
N¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À]XãXùâ Kôõ‹ëXX⁄
ùàOà¬à€€ú›X›]ôHHùãô]\Ÿ]ùXàOOH›]KòX›]ôUXé¬à\]UZUŸŸ€P€\‹ ùã	€X€\ÀXX›]ôIÀX›]ôJN¬à\]UZTŸ]]öXù]Jùã	ÿ\öXK\Ÿ[X›Y	À›ö[ô X›]ôJJN¬à\]UZTŸ]õ‹\ùJùã	›Xí[ô^	ÀX›]ôH»àLJN¬àJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À]Xã\[ô[	 Kôõ‹ëXX⁄
Xî[ô[Oà¬à€€ú›X›]ôHHXî[ô[ô]\Ÿ]ú[ô[OOH›]KòX›]ôUXé¬à\]UZUŸŸ€P€\‹ Xî[ô[	€X€\ÀXX›]ôIÀX›]ôJN¬à\]UZTŸ]õ‹\ùJXî[ô[	⁄Y[âÀXX›]ôJN¬àJN¬à€€ú›[ô[‹[àH[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â N¬à\]UZTŸ]]öXù]J[ô[	ÿ\öXKZY[âÀ›ö[ô \[ô[‹[äJN¬à\]UZTŸ]]öXù]J€€ùõ€Àú]Y\ûTŸ[X›‹ä	ÀõX€\À[Y[ùKXùâ K	ÿ\öXKY^[ôY	À›ö[ô [ô[‹[äJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À]ZK][YKXùâ Kôõ‹ëXX⁄
ùàOà¬à€€ú›X›]ôHHùãô]\Ÿ]ùZU[YHOOH›]KùZU[YN¬à\]UZUŸŸ€P€\‹ ùã	€X€\ÀXX›]ôIÀX›]ôJN¬à\]UZTŸ]]öXù]Jùã	ÿ\öXK\ô\‹ŸY	À›ö[ô X›]ôJJN¬àJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À][YKXùâ Kôõ‹ëXX⁄
ùàOà\]UZUŸŸ€P€\‹ ùã	€X€\ÀXX›]ôIÀùãô]\Ÿ]ù[YHOOH›]Kù[YJJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	ÀõX€\À\‹⁄][€ãXùâ Kôõ‹ëXX⁄
ùàOà\]UZUŸŸ€P€\‹ ùã	€X€\ÀXX›]ôIÀùãô]\Ÿ]ú‹⁄][€àOOHX›]ôQÿ⁄‘‹⁄][€ä
JJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	÷Ÿ]KYôX]\ôKXôXX€€óI Kôõ‹ëXX⁄
[[Y[ùOà\]UZUŸŸ€P€\‹ [[Y[ù	€X€\ÀYôX]\ôK]öY]ŸY	ÀôX]\ôPôXX€€ïöY]ŸY
[[Y[ùô]\Ÿ]ôôX]\ôPôXX€€äJJN¬à€€ú›ÿYôS[ŸPù]€àH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À\ÿYôK[[ŸK\Ÿ][ô… N¬àYà
ÿYôS[ŸPù]€äH¬à\]UZUŸŸ€P€\‹ ÿYôS[ŸPù]€ã	€X€\À[€âÀ›]KúÿYôS[ŸKô[òXõY
N¬à\]UZTŸ]]öXù]JÿYôS[ŸPù]€ã	ÿ\öXK\ô\‹ŸY	À›ö[ô ›]KúÿYôS[ŸKô[òXõY
JN¬à\]UZTŸ]^
ÿYôS[ŸPù]€ã›]KúÿYôS[ŸKô[òXõY»	—^]€€⁄]ÿYôH[ŸI»à	—[ù\à€€⁄]ÿYôH[ŸI N¬àBà€€ú›ŸŸ€Uò[Y\»H¬à€X[éà›]Kò€X[ì[ŸKàX\öŸ\ëõÿ›\Œà›]KõX\öŸ\ëõÿ›\ÀàZ\‹⁄[€î[ŸNà›]KõZ\‹⁄[€î[ŸKàõÿYö[‹ö]Nà›]KúõÿYö[‹ö]Kà€›ô\òYŸNà›]Kò€›ô\òYŸKô[òXõYà⁄‹ù›]Œà›]Kú⁄‹ù›]Àà]ZX⁄’⁄Y[à›]Kú]ZX⁄’⁄Y[ô[òXõYà]]”ÿY[ôZX€\Œà›]Kò]]”ÿY[ôZX€\Àà[X[òŸPùZ[[ô‹”X\õÿ⁄Ÿ\éà›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸKàXZõ‹í[ò⁄Y[ùôYYà›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõYàZ\‹⁄[€ìÿ⁄–]Y[Œà›]KõZ\‹⁄[€ìÿ⁄–]Y[Àà^[›]õ\⁄à›]Kú^[›]õ\⁄ô[òXõYà^[›]€›[ôà›]Kú^[›]õ\⁄ú€›[ô[òXõYàZ\‹⁄[€ïò[YNà›]KõZ\‹⁄[€ïò[YKà›\›€UôZX€PòYŸ\Œà›]Kò›\›€UôZX€PòYŸ\Àà›X⁄—]X›‹éà›]Kú›X⁄—]X›‹ãô[òXõYàZ\‹⁄[€î‹]€éà›]KõZ\‹⁄[€î‹]€ãô[òXõYàô\€›\òŸQÿ\à›]Kúô\€›\òŸQÿ\ô[òXõYà[X[òŸSZ\‹⁄[€úŒà›]Kùö\⁄Xö[]Kò[X[òŸSZ\‹⁄[€úÀà^SZ\‹⁄[€úŒà›]Kùö\⁄Xö[]Kõ^SZ\‹⁄[€úÀàôZX€\Œà›]Kùö\⁄Xö[]KùôZX€\ÀàùZ[[ô‹Œà›]Kùö\⁄Xö[]KòùZ[[ô‹Àà[X[òŸP‹ôY]Œà›]Kò[X[òŸP‹ôY]ÀàZ\‹⁄[€êYŸNà›]KõZ\‹⁄[€êYŸKàò[ú‹‹ùÿ]⁄\éà›]Kùò[ú‹‹ùÿ]⁄\ãà[ö]€€[Z]Y[ùà›]Kù[ö]€€[Z]Y[ùàN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	÷Ÿ]K]ŸŸ€WI Kôõ‹ëXX⁄
ùàOà¬à€€ú›Ÿ^HHùãô]\Ÿ]ùŸŸ€N¬à€€ú›€àHõ€€X[äŸŸ€Uò[Y\÷⁄Ÿ^WJN¬à\]UZUŸŸ€P€\‹ ùã	€X€\À[€âÀ€äN¬à€€ú›[Hùãú]Y\ûTŸ[X›‹ä	ÀõX€\À\[	 N¬à\]UZTŸ]^
[Ÿ^HOOH	ÿ€›ô\òYŸI»»
€à»	‹›]Kò€›ô\òYŸKúòY]\”Z_[ZXà	”—ëâ Hà
€à»	””â»à	”—ëâ JN¬à\]UZTŸ]]öXù]Jùã	ÿ\öXK\ô\‹ŸY	À›ö[ô €äJN¬àJN¬à€€ú›ô\‹›\ôPõÿ\ôŸŸ€HH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À\ô\‹›\ôKXõÿ\ô]ŸŸ€I N¬àYà
ô\‹›\ôPõÿ\ôŸŸ€JH¬à€€ú›‹[àH‹\ò][€ò[ô\‹›\ôPõÿ\ô‹[ä
N¬à\]UZUŸŸ€P€\‹ ô\‹›\ôPõÿ\ôŸŸ€K	€X€\À[€âÀ‹[äN¬à\]UZTŸ]]öXù]Jô\‹›\ôPõÿ\ôŸŸ€K	ÿ\öXK\ô\‹ŸY	À›ö[ô ‹[äJN¬à\]UZTŸ]^
ô\‹›\ôPõÿ\ôŸŸ€Kú]Y\ûTŸ[X›‹ä	ÀõX€\À\[	 K‹[à»	–P’UëI»à	”—ëâ N¬àBàõ‹à
€€ú›‹Ÿ[X›‹ã€óHŸà¬à…ÀõX€\ÀX€€[X[ôXò\ã\Ÿ][ô…À›]Kò€€[X[ôò\ì‹[àOOHò[ŸWKà…ÀõX€\ÀYX€€õ€^K\Ÿ][ô…À›]KôX€€õ€^S[ŸWKà…ÀõX€\ÀYù[ÿ‹ôY[ã\Ÿ][ô…À›]Kôù[ÿ‹ôY[ìX\KàJH¬à€€ú›ù]€àH[ô[ú]Y\ûTŸ[X›‹äŸ[X›‹äN¬àYà
Xù]€äH€€ù[ùYN¬à\]UZUŸŸ€P€\‹ ù]€ã	€X€\À[€âÀõ€€X[ä€äJN¬à\]UZTŸ]]öXù]Jù]€ã	ÿ\öXK\ô\‹ŸY	À›ö[ô õ€€X[ä€äJJN¬à\]UZTŸ]^
ù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\À\[	 K€à»	””â»à	”—ëâ N¬àBà\]P[X[òŸSY[Xô\ìX[òYŸ\ìY[ùP€€ùõ€

N¬à›]Kú]ZX⁄’⁄Y[ú€›Àú€XŸJ›]Kú]ZX⁄’⁄Y[ú€›€›[ù
Kôõ‹ëXX⁄

€›[ô^
HOà¬à€€ú›Ÿ[X›H[ô[ú]Y\ûTŸ[X›‹äŸ]K\Ÿ][ôœHú]ZX⁄À]⁄Y[\€›I⁄[ô^HóX
N¬àYà
Ÿ[X›	âàÿ›[Y[ùòX›]ôQ[[Y[ùOOHŸ[X›
H\]UZTŸ]õ‹\ùJŸ[X›	›ò[YIÀ]ZX⁄’⁄Y[€›ò[YJ€›
JN¬àJN¬à€€ú›XZõ‹í[ò⁄Y[ùZ[ö[][HH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHõXZõ‹ãZ[ò⁄Y[ù[Z[ö[][HóI N¬àYà
XZõ‹í[ò⁄Y[ùZ[ö[][JH\]UZTŸ]õ‹\ùJXZõ‹í[ò⁄Y[ùZ[ö[][K	›ò[YIÀ›ö[ô ›]KõXZõ‹í[ò⁄Y[ùôYYõZ[ö[][P‹ôY] JN¬à€€ú›òY]\»H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHò€›ô\òYŸK\òY]\»óI N¬àYà
òY]\ H\]UZTŸ]õ‹\ùJòY]\À	›ò[YIÀ›ö[ô ›]Kò€›ô\òYŸKúòY]\”ZJJN¬à€€ú›[X[òŸP‹ôY]Z[ö[][HH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHò[X[òŸKX‹ôY][Z[ö[][HóI N¬àYà
[X[òŸP‹ôY]Z[ö[][JH\]UZTŸ]õ‹\ùJ[X[òŸP‹ôY]Z[ö[][K	›ò[YIÀ›ö[ô ›]Kò[X[òŸP‹ôY]Z[ö[][JJN¬à€€ú›ò[ú‹‹ù›ŸY\[^HH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHùò[ú‹‹ù\›ŸY\Y[^HóI N¬àYà
ò[ú‹‹ù›ŸY\[^JH\]UZTŸ]õ‹\ùJò[ú‹‹ù›ŸY\[^K	›ò[YIÀ›ö[ô ›]Kùò[ú‹‹ù›ŸY\ô[^S\ JN¬à€€ú›ò[ú‹‹ù›ŸY\X^H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHùò[ú‹‹ù\›ŸY\[X^óI N¬àYà
ò[ú‹‹ù›ŸY\X^
H\]UZTŸ]õ‹\ùJò[ú‹‹ù›ŸY\X^	›ò[YIÀ›ö[ô ›]Kùò[ú‹‹ù›ŸY\õX^\îù[äJN¬àYà
[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â H	âà›]KòX›]ôUXàOOH	€Z\‹⁄[€ú… Hô[ô\ïò[ú‹‹ù›ŸY\[ô[

N¬à€€ú›^[›][\]HH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHú^[›]][\]HóI N¬àYà
^[›][\]JH\]UZTŸ]õ‹\ùJ^[›][\]K	›ò[YIÀ›]Kú^[›]õ\⁄ù[\]JN¬à€€ú›ô\€›\òŸQÿ\òY]\»H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHúô\€›\òŸKYÿ\\òY]\»óI N»Yà
ô\€›\òŸQÿ\òY]\ H\]UZTŸ]õ‹\ùJô\€›\òŸQÿ\òY]\À	›ò[YIÀ›ö[ô ›]Kúô\€›\òŸQÿ\úòY]\”ZJJN¬à€€ú››X⁄’ô\⁄€H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHú›X⁄À]ô\⁄€óI N¬àYà
›X⁄’ô\⁄€
H\]UZTŸ]õ‹\ùJ›X⁄’ô\⁄€	›ò[YIÀ›ö[ô ›]Kú›X⁄—]X›‹ãùô\⁄€Z[äJN¬à€€ú›^[›]ô\⁄€H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHú^[›]]ô\⁄€óI N¬àYà
^[›]ô\⁄€
H\]UZTŸ]õ‹\ùJ^[›]ô\⁄€	›ò[YIÀ›ö[ô ›]Kú^[›]õ\⁄ùô\⁄€
JN¬à€€ú›^[›]\ò][€àH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHú^[›]Y\ò][€àóI N¬àYà
^[›]\ò][€äH\]UZTŸ]õ‹\ùJ^[›]\ò][€ã	›ò[YIÀ›ö[ô ›]Kú^[›]õ\⁄ô\ò][€ì\»»L
JN¬à€€ú›^[›]õ€[YHH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHú^[›]]õ€[YHóI N¬àYà
^[›]õ€[YJH\]UZTŸ]õ‹\ùJ^[›]õ€[YK	›ò[YIÀ›ö[ô ›]Kú^[›]õ\⁄ú€›[ôõ€[YJJN¬à€€ú›\ÿ€‹ôŸXö€⁄»H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ô]ŸXö€⁄»óI N¬àYà
\ÿ€‹ôŸXö€⁄»	âàÿ›[Y[ùòX›]ôQ[[Y[ùOOH\ÿ€‹ôŸXö€⁄ H\]UZTŸ]õ‹\ùJ\ÿ€‹ôŸXö€⁄À	›ò[YIÀŸ]\ÿ€‹ôŸXö€⁄’\õ

JN¬à€€ú›\ÿ€‹ôò[YHH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ô[ò[YHóI N¬àYà
\ÿ€‹ôò[YH	âàÿ›[Y[ùòX›]ôQ[[Y[ùOOH\ÿ€‹ôò[YJH\]UZTŸ]õ‹\ùJ\ÿ€‹ôò[YK	›ò[YIÀ›]Kô\ÿ€‹ôô\‹ùùŸXö€⁄”ò[YJN¬à€€ú›\ÿ€‹ô‹ÿ]Y€‹öY\»H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ô]‹Xÿ]Y€‹öY\»óI N¬àYà
\ÿ€‹ô‹ÿ]Y€‹öY\ H\]UZTŸ]õ‹\ùJ\ÿ€‹ô‹ÿ]Y€‹öY\À	›ò[YIÀ›ö[ô ›]Kô\ÿ€‹ôô\‹ùù‹ÿ]Y€‹öY\ JN¬à€€ú›\ÿ€‹ô\ö[ŸH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ô\\ö[ŸóI N¬àYà
\ÿ€‹ô\ö[Ÿ
H\]UZTŸ]õ‹\ùJ\ÿ€‹ô\ö[Ÿ	›ò[YIÀ›]Kô\ÿ€‹ôô\‹ùú\ö[Ÿ
N¬à€€ú›\ÿ€‹ô›\›€T›\ùH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ôX›\›€K\›\ùóI N¬àYà
\ÿ€‹ô›\›€T›\ù	âàÿ›[Y[ùòX›]ôQ[[Y[ùOOH\ÿ€‹ô›\›€T›\ù
H\]UZTŸ]õ‹\ùJ\ÿ€‹ô›\›€T›\ù	›ò[YIÀ›]Kô\ÿ€‹ôô\‹ùò›\›€T›\ù
N¬à€€ú›\ÿ€‹ô›\›€Q[ôH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ôX›\›€KY[ôóI N¬àYà
\ÿ€‹ô›\›€Q[ô	âàÿ›[Y[ùòX›]ôQ[[Y[ùOOH\ÿ€‹ô›\›€Q[ô
H\]UZTŸ]õ‹\ùJ\ÿ€‹ô›\›€Q[ô	›ò[YIÀ›]Kô\ÿ€‹ôô\‹ùò›\›€Q[ô
N¬à€€ú›\ÿ€‹ô€€\\ö\€€àH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ôX€€\\ö\€€àóI N¬àYà
\ÿ€‹ô€€\\ö\€€äH\]UZTŸ]õ‹\ùJ\ÿ€‹ô€€\\ö\€€ã	›ò[YIÀ›ö[ô ›]Kô\ÿ€‹ôô\‹ùö[ò€YP€€\\ö\€€äJN¬à€€ú›\ÿ€‹ô⁄\ùH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ôX⁄\ùóI N¬àYà
\ÿ€‹ô⁄\ù
H\]UZTŸ]õ‹\ùJ\ÿ€‹ô⁄\ù	›ò[YIÀ›ö[ô ›]Kô\ÿ€‹ôô\‹ùö[ò€YP⁄\ù
JN¬à€€ú›\ÿ€‹ô€€\^]HH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ôX€€\^]HóI N¬àYà
\ÿ€‹ô€€\^]JH\]UZTŸ]õ‹\ùJ\ÿ€‹ô€€\^]K	›ò[YIÀõ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]J›]Kô\ÿ€‹ôô\‹ùò€€\^]JJN¬à€€ú›\ÿ€‹ô€€\^]R[H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]KY\ÿ€‹ôX€€\^]KZ[I N¬àYà
\ÿ€‹ô€€\^]R[
H\]UZTŸ]^
\ÿ€‹ô€€\^]R[íSêSê—W‘ëT‘ï–””TVUW–”‘V€õ‹õX[\ŸQ\ÿ€‹ôô\‹ù€€\^]J›]Kô\ÿ€‹ôô\‹ùò€€\^]JWJN¬à[ô[ú]Y\ûTŸ[X›‹ê[
	÷Ÿ]KY\ÿ€‹ô[Z[ãX€€\^]WI Kôõ‹ëXX⁄
õ›»Oà¬à€€ú›ö\⁄XõHH\ÿ€‹ôô\‹ù€€\^]P]X\›
õ›Àô]\Ÿ]ô\ÿ€‹ôZ[ê€€\^]K›]Kô\ÿ€‹ôô\‹ùò€€\^]JN¬à\]UZTŸ]õ‹\ùJõ›À	⁄Y[âÀ]ö\⁄XõJN¬àJN¬à€€ú›\ÿ€‹ôö\⁄»H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ô\ö\⁄»óI N¬àYà
\ÿ€‹ôö\⁄ H\]UZTŸ]õ‹\ùJ\ÿ€‹ôö\⁄À	›ò[YIÀ›ö[ô ›]Kô\ÿ€‹ôô\‹ùö[ò€YTö\⁄ JN¬à€€ú›\ÿ€‹ôõ‹ôXÿ\›H[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHô\ÿ€‹ôYõ‹ôXÿ\›óI N¬àYà
\ÿ€‹ôõ‹ôXÿ\›
H\]UZTŸ]õ‹\ùJ\ÿ€‹ôõ‹ôXÿ\›	›ò[YIÀ›ö[ô ›]Kô\ÿ€‹ôô\‹ùö[ò€YQõ‹ôXÿ\›
JN¬à€€ú›ö[ò[òŸUò][[òXõYH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHôö[ò[òŸK]ò][Y[òXõYóI N¬àYà
ö[ò[òŸUò][[òXõY
H\]UZTŸ]õ‹\ùJö[ò[òŸUò][[òXõY	›ò[YIÀ›ö[ô ›]Kôö[ò[ò⁄X[ò][ô[òXõY
JN¬à€€ú›ö[ò[òŸUò][ô][ù[€àH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHôö[ò[òŸK]ò][\ô][ù[€àóI N¬àYà
ö[ò[òŸUò][ô][ù[€äH\]UZTŸ]õ‹\ùJö[ò[òŸUò][ô][ù[€ã	›ò[YIÀ›ö[ô ›]Kôö[ò[ò⁄X[ò][úô][ù[€ë^\ JN¬à€€ú›ö[ò[òŸTù[QôYYH[ô[ú]Y\ûTŸ[X›‹ä	÷Ÿ]K\Ÿ][ôœHôö[ò[òŸK\ù[KYôYYóI N¬àYà
ö[ò[òŸTù[QôYY
H\]UZTŸ]õ‹\ùJö[ò[òŸTù[QôYY	›ò[YIÀ›ö[ô ›]Kôö[ò[ò⁄X[ò][úù[QôYY[òXõY
JN¬àŸ]\ÿ€‹ô›]\ \ÿ€‹ôö[ò[òŸT›]\À\ÿ€‹ôö[ò[òŸT›]\’€ôJN¬àŸ]‹\ò][€ò[⁄]ô\›]\ ‹\ò][€ò[⁄]ô\›]\À‹\ò][€ò[⁄]ô\›]\’€ôJN¬àYà
[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â H	âà›]KòX›]ôUXàOOH	Ÿö[ò[òŸI Hô[ô\ëö[ò[òŸUò][›]\ 
N¬à€€ú›X€€õ€^T›]\»H[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\ÀYX€€õ€^K\›]\… N¬à\]UZTŸ]^
X€€õ€^T›]\À›]KôX€€õ€^S[ŸBà»	—X€€õ€^H[ŸH\»”éà›]X»ö\›X[YôôX›ÀY\]ôHôYúô\⁄[ù\ùò[»[ôŸôã\ÿ‹ôY[àôZX€KÿùZ[[ô»^Y\à›[[ô»\ôHX›]ôKâ¬àà	—X€€õ€^H[ŸH\»—ëãà[òXõH]\ôH‹àúõ€HH\ôõ‹õX[òŸH‹õ›\€àHX\€€[X[ôò\à»ôYXŸH‘K‘H[ôX\öŸ\à€‹ö€ÿYâ N¬à€€ú›ùYŸHH[ô[ú]Y\ûTŸ[X›‹ä	ÀõX€\À[ùYŸK]ò[YI N¬à\]UZTŸ]^
ùYŸK	‹›]KõùYŸKûH»H	‹›]KõùYŸKû_X
N¬àYà
[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â H	âà›]KòX›]ôUXàOOH	‹Ÿ][ô‹… Hô[ô\îõŸö[\ 
N¬àYà

[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â H	âà›]KòX›]ôUXàOOH	€Z\‹⁄[€ú… H‹\ò][€ò[ZR\’ö\⁄XõJ
JHô[ô\ì‹\ò][€ò[[ô[ 
N¬à\]P€€[X[ô[ù\ôòXŸRXY\ä[ô[
N¬àBàù[ò›[€à[ú›\ôUZJ
H¬àYà
]€€⁄]€€[X[ô⁄[õ›]Q[Y⁄XõJÿ›[Y[ù
JH¬àX\ô›€ï€€⁄]€€[X[ô⁄[
	‹õ›]H\»õ›Hÿ[õ€öXÿ[‹[]ô[X\	 N¬àô]\õàùYN¬àBà€€ú›\ÿ€›ô\ôYX\HŸ]\ôŸ\›XYõ]X\

N¬à€€ú›X\[H€€⁄]ö[X\ûSX\[[Y[ù
\ÿ€›ô\ôYX\ÿ›[Y[ù
N¬àYà
[X\[
H¬àX\ô›€ï€€⁄]€€[X[ô⁄[
	ÿÿ[õ€öXÿ[X\\»õ›ôY[à‹⁄]]ô[HY[ùYöYY	 N¬àô]\õàò[ŸN¬àBà€€ú›€€ùõ€H‹ôX]P€€ùõ€
X\[
N¬àYà
Ÿ][ô‹‘[ô[X›]ò]Y	âàYÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
JH‹ôX]T[ô[

N¬àYà
€€ùõ€
H[ú›\ôUô\ú⁄[€î›]\–ù]€ä
N¬àYà
›]Kôù[ÿ‹ôY[ìX\ù[ÿ‹ôY[ìX\\ôŸ]
H\SX\ù[ÿ‹ôY[î›]J
N¬àYà
X\[
H¬à€€ú›X\Hö[ôXYõ]X\[ú›[òŸJò[ŸJN¬àYà
X\YX\›\ôTù[ù[YKòX›]ôH	âàX\YX\›\ôTù[ù[YKõX\OOHX\
H›‹X\YX\›\ôJò[ŸJN¬àYà
›]KôX€€õ€^S[ŸH	âàX\
H»\SXYõ]X€€õ€^T€XﬁJX\
N»ÿ⁄Y[QX€€õ€^S^Y\îﬁ[ò 
N»BàYà
›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY	âà‹\ò][€ò[›\ù\€€\]JHÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\ä
N¬à[ŸHYà
\›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY
Hô[[›ôSXZõ‹í[ò⁄Y[ùôYY

N¬à€€ú›^[›]›ô\õ^HHÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú^[›]õ\⁄Y
N¬àYà
^[›]›ô\õ^OÀò€\‹”\›ò€€ùZ[ú 	€X€\À\^[›]XX›]ôI JH‹⁄][€î^[›]õ\⁄›ô\õ^J^[›]›ô\õ^KX\[
N¬àBà€€⁄]\P€€[X[ôò\î›]J€€ùõ€
N¬àYà
[X^XôT⁄›‘Ÿ]\⁄^ò\ô

JHX^XôT⁄›’\]PúöYYö[ô 
N¬àô]\õàõ€€X[ä€€ùõ€ÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
JN¬àBÇà]€€⁄]€€[X[ô⁄[õ›]TôX€€ò⁄[T]Y]YYHò[ŸN¬àù[ò›[€àôX€€ò⁄[U€€⁄]€€[X[ô⁄[õ›]JôX\€€àH	€ò]öYÿ][€â H¬à[ùò[Y]SX\[[Y[ùÿX⁄J
N¬àYà
]€€⁄]€€[X[ô⁄[õ›]Q[Y⁄XõJÿ›[Y[ù
JH¬àX\ô›€ï€€⁄]€€[X[ô⁄[
	‹ôX\€€üNà[ô[Y⁄XõHõ›]X
N¬àô]\õàùYN¬àBàô]\õà[ú›\ôUZJ
N¬àBàù[ò›[€à]Y]YU€€⁄]€€[X[ô⁄[õ›]TôX€€ò⁄[JôX\€€àH	⁄\›‹ûI H¬àYà
€€⁄]€€[X[ô⁄[õ›]TôX€€ò⁄[T]Y]YYù[ù[YKô\›õﬁYY
Hô]\õé¬à€€⁄]€€[X[ô⁄[õ›]TôX€€ò⁄[T]Y]YYHùYN¬à]Y]YSZX‹õ›\⁄ 

HOà¬à€€⁄]€€[X[ô⁄[õ›]TôX€€ò⁄[T]Y]YYHò[ŸN¬àYà
\ù[ù[YKô\›õﬁYY
HôX€€ò⁄[U€€⁄]€€[X[ô⁄[õ›]JôX\€€äN¬àJN¬àBàù[ò›[€à[ú›[€€⁄]€€[X[ô⁄[ò]öYÿ][€í€⁄‹ 
H¬à€€ú›\›‹ûSÿöôX›HYŸU⁄[ô›Àö\›‹ûN¬àYà
Z\›‹ûSÿöôX›\›‹ûSÿöôX›ó◊€X€\–€€[X[ô⁄[ò]öYÿ][€í€⁄‹»OOH–‘íTùô\ú⁄[€äHô]\õàùYN¬àõ‹à
€€ú›Y]ŸŸà…‹\⁄›]IÀ	‹ô\XŸT›]I◊JH¬à€€ú›‹öY⁄[ò[H\›‹ûSÿöôX›€Y]ŸN¬àYà
\[Ÿà‹öY⁄[ò[OOH	Ÿù[ò›[€â H€€ù[ùYN¬à€€ú›‹ò\YHù[ò›[€à
ããò\ô‹ H¬à€€ú›ô\›[H‹öY⁄[ò[ò\J\À\ô‹ N¬à]Y]YU€€⁄]€€[X[ô⁄[õ›]TôX€€ò⁄[J\›‹ûKâ€Y]ŸX
N¬àô]\õàô\›[¬àN¬àûH¬à\›‹ûSÿöôX›€Y]ŸHH‹ò\Y¬àù[ù[YKö€⁄‘ô\›‹ô\úÀú\⁄


HOà¬àYà
\›‹ûSÿöôX›€Y]ŸHOOH‹ò\Y
H\›‹ûSÿöôX›€Y]ŸHH‹öY⁄[ò[¬àJN¬àHÿ]⁄
\úõ‹äHﬂBàBàûH»\›‹ûSÿöôX›ó◊€X€\–€€[X[ô⁄[ò]öYÿ][€í€⁄‹»H–‘íTùô\ú⁄[€é»Hÿ]⁄
\úõ‹äHﬂBàù[ù[YKö€⁄‘ô\›‹ô\úÀú\⁄


HOà¬àûH¬àYà
\›‹ûSÿöôX›ó◊€X€\–€€[X[ô⁄[ò]öYÿ][€í€⁄‹»OOH–‘íTùô\ú⁄[€äH¬à[]H\›‹ûSÿöôX›ó◊€X€\–€€[X[ô⁄[ò]öYÿ][€í€⁄‹Œ¬àBàHÿ]⁄
\úõ‹äHﬂBàJN¬àô]\õàùYN¬àBÇàù[ò›[€à]]][€êô[€ô‹’’€€⁄]
]]][€äH¬à€€ú›\ôŸ]H]]][€ãù\ôŸ]¬à€€ú›€€⁄]\ôŸ]Hõ€€X[äà\ôŸ]	âÇà\ôŸ]õõŸU\HOOHH	âÇà
à\ôŸ]öYOOH–‘íTò€€ùõ€Yà\ôŸ]öYOOH–‘íTú[ô[Yà\ôŸ]öYOOH–‘íTùÿ\›Yà\ôŸ]öYOOH–‘íTú^[›]õ\⁄Yà\ôŸ]öYOOH–‘íTùôZX€T›]\“Yà\ôŸ]öYOOH–‘íTúô\‹›\ôPõÿ\ôYà\ôŸ]öYOOH–‘íTõXZõ‹í[ò⁄Y[ùôYYYà\ôŸ]öYOOH–‘íTò€€[X[ô[]RYà\ôŸ]öYOOH–‘íTò€€[X[ô^\öY[òŸS[Ÿ[Yà\ôŸ]öYOOH–‘íTõX\YX\›\ôRYYà\ôŸ]öYOOH–‘íTú]ZX⁄’⁄Y[Yà\ôŸ]öYOOH–‘íTôù[ÿ‹ôY[ë^]Yà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTò€€ùõ€YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTú[ô[YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTùÿ\›YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTú^[›]õ\⁄YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTùôZX€T›]\“YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTúô\‹›\ôPõÿ\ôYX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTõXZõ‹í[ò⁄Y[ùôYYYX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTò€€[X[ô[]RYX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTò€€[X[ô^\öY[òŸS[Ÿ[YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTõX\YX\›\ôRYYX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTú]ZX⁄’⁄Y[YX
Hà\ôŸ]ò€‹Ÿ\›Àä…‘–‘íTôù[ÿ‹ôY[ë^]YX
Hàò[ŸBà
Bà
N¬àYà
€€⁄]\ôŸ]
Hô]\õàùYN¬àYà
]]][€ãù\HOOH	ÿ]öXù]\…»	âà]]][€ãò]öXù]Sò[YHOOH	ÿ€\‹…»	âà\ôŸ]Àò€\‹”\›
H¬àõ‹à
€€ú›€\‹”ò[YHŸà\ôŸ]ò€\‹”\›
H¬àYà
›ö[ô €\‹”ò[YJKú›\ù’⁄]
	€X€\ÀI JHô]\õàùYN¬àBàBà€€ú›€€⁄]Ÿ[X›‹àHõX€\ÀX[X[òŸKX‹ôY]ZX€€ãõX€\ÀX[X[òŸKX‹ôY]XòYŸKõX€\À[Z\‹⁄[€ãXYŸKZX€€ãõX€\À[Z\‹⁄[€ãXYŸKXòYŸKõX€\À][ö]X€€[Z]Y[ùZX€€ãõX€\À][ö]X€€[Z]Y[ùXòYŸKõX€\À]ò[ú‹‹ù]ÿ]⁄\ãZX€€ãõX€\À]ò[ú‹‹ù]ÿ]⁄\ãXòYŸKõX€\À\ô\€›\òŸKYÿ\ZX€€ãõX€\À\ô\€›\òŸKYÿ\XòYŸKõX€\À\›X⁄À[Z\‹⁄[€ãZX€€ãõX€\À\›X⁄À[Z\‹⁄[€ãXòYŸKõX€\À[Z\‹⁄[€ã\‹]€ã[Xô[ZX€€ãõX€\À[Z\‹⁄[€ã\‹]€ã[Xô[õX€\À[X\[YX\›\ôK\]õX€\À[X\[YX\›\ôK\⁄[ù…‘–‘íTõX\YX\›\ôRYYX¬à][[Y[ù€›[ùH¬àõ‹à
€€ú›€€X›[€àŸà€]]][€ãòYYõŸ\À]]][€ãúô[[›ôYõŸ\◊JH¬àYà
X€€X›[€èÀõ[ô›
H€€ù[ùYN¬àõ‹à
€€ú›õŸHŸà€€X›[€äH¬àYà
[õŸHõŸKõõŸU\HOOHJH€€ù[ùYN¬à[[Y[ù€›[ù
œHN¬àYà
JõŸKõX]⁄\œÀä€€⁄]Ÿ[X›‹äHõŸKú]Y\ûTŸ[X›‹èÀä€€⁄]Ÿ[X›‹äJJHô]\õàò[ŸN¬àBàBàô]\õà[[Y[ù€›[ùà¬àBÇàù[ò›[€à]]][€í\”XYõ][Sõ⁄\ŸJ]]][€äH¬àYà
[]]][€à]]][€ãù\HOOH	ÿ⁄[\›	 Hô]\õàò[ŸN¬à€€ú›\ôŸ]H]]][€ãù\ôŸ]¬àYà
\ôŸ]ÀõõŸU\HOOHH	âà
\ôŸ]õX]⁄\œÀä	ÀõXYõ]][K\[ôKõXYõ]][KX€€ùZ[ô\â H\ôŸ]ò€‹Ÿ\›Àä	ÀõXYõ]][K\[ôI JJHô]\õàùYN¬à€€ú›õŸ\»HÀããê\úò^Kôúõ€J]]][€ãòYYõŸ\»◊JKããê\úò^Kôúõ€J]]][€ãúô[[›ôYõŸ\»◊JWKôö[\äõŸHOàõŸOÀõõŸU\HOOHJN¬àô]\õàõŸ\Àõ[ô›à	âàõŸ\Àô]ô\ûJõŸHOàõŸKõX]⁄\œÀä	ÀõXYõ]][K\[ôKõXYõ]][KX€€ùZ[ô\ãõXYõ]][I JN¬àBÇàù[ò›[€à]]][€êY”XYõ]X\öŸ\íX€€ä]]][€äH¬àYà
[]]][€à]]][€ãù\HOOH	ÿ⁄[\›	»[]]][€ãòYYõŸ\œÀõ[ô›
Hô]\õàò[ŸN¬àõ‹à
€€ú›õŸHŸà]]][€ãòYYõŸ\ H¬àYà
[õŸHõŸKõõŸU\HOOHJH€€ù[ùYN¬àYà
õŸKõX]⁄\œÀä	ÀõX€\ÀX[X[òŸKX‹ôY]ZX€€ãõX€\À[Z\‹⁄[€ãXYŸKZX€€ãõX€\À][ö]X€€[Z]Y[ùZX€€ãõX€\À]ò[ú‹‹ù]ÿ]⁄\ãZX€€ãõX€\À\ô\€›\òŸKYÿ\ZX€€ãõX€\À\›X⁄À[Z\‹⁄[€ãZX€€ãõX€\À[Z\‹⁄[€ã\‹]€ã[Xô[ZX€€â HõŸKú]Y\ûTŸ[X›‹èÀä	ÀõX€\ÀX[X[òŸKX‹ôY]ZX€€ãõX€\À[Z\‹⁄[€ãXYŸKZX€€ãõX€\À][ö]X€€[Z]Y[ùZX€€ãõX€\À]ò[ú‹‹ù]ÿ]⁄\ãZX€€ãõX€\À\ô\€›\òŸKYÿ\ZX€€ãõX€\À\›X⁄À[Z\‹⁄[€ãZX€€ãõX€\À[Z\‹⁄[€ã\‹]€ã[Xô[ZX€€â JH€€ù[ùYN¬àYà
õŸKõX]⁄\œÀä	ÀõXYõ][X\öŸ\ãZX€€â JHô]\õàùYN¬àYà
õŸKú]Y\ûTŸ[X›‹èÀä	ÀõXYõ][X\öŸ\ãZX€€â JHô]\õàùYN¬àBàô]\õàò[ŸN¬àBÇàù[ò›[€à]]][€ï›X⁄\‘Ÿ[X›‹ä]]][€ãŸ[X›‹äH¬à€€ú›\ôŸ]H]]][€èÀù\ôŸ]¬àYà
\ôŸ]ÀõõŸU\HOOHH	âà
\ôŸ]õX]⁄\œÀäŸ[X›‹äH\ôŸ]ò€‹Ÿ\›ÀäŸ[X›‹äJJHô]\õàùYN¬àõ‹à
€€ú›€€X›[€àŸà€]]][€èÀòYYõŸ\À]]][€èÀúô[[›ôYõŸ\◊JH¬àYà
X€€X›[€èÀõ[ô›
H€€ù[ùYN¬àõ‹à
€€ú›õŸHŸà€€X›[€äH¬àYà
[õŸHõŸKõõŸU\HOOHJH€€ù[ùYN¬àYà
õŸKõX]⁄\œÀäŸ[X›‹äHõŸKú]Y\ûTŸ[X›‹èÀäŸ[X›‹äJHô]\õàùYN¬àBàBàô]\õàò[ŸN¬àBÇàù[ò›[€à]]][€îô[[›ô\’€€⁄]ZJ]]][€äH¬àõ‹à
€€ú›õŸHŸà]]][€èÀúô[[›ôYõŸ\»◊JH¬àYà
[õŸHõŸKõõŸU\HOOHJH€€ù[ùYN¬àYà
‘–‘íTú[ô[Y–‘íTò€€ùõ€Y–‘íTúô\‹›\ôPõÿ\ôY–‘íTõXZõ‹í[ò⁄Y[ùôYYYKö[ò€Y\ õŸKöY
JHô]\õàùYN¬àYà
õŸKú]Y\ûTŸ[X›‹èÀä…‘–‘íTú[ô[YK…‘–‘íTò€€ùõ€YK…‘–‘íTúô\‹›\ôPõÿ\ôYK…‘–‘íTõXZõ‹í[ò⁄Y[ùôYYYX
JHô]\õàùYN¬àBàô]\õàò[ŸN¬àBÇàù[ò›[€à]]][€êYôôX›”Z\‹⁄[€ë]J]]][€äH¬àô]\õà]]][€ï›X⁄\‘Ÿ[X›‹ä]]][€ã	ÀõXYõ][X\öŸ\ã\[ôKõXYõ][X\öŸ\ãZX€€ã⁄YèHõZ\‹⁄[€ó»óK€Z\‹⁄[€úÀ€Z\‹⁄[€ó€\›õZ\‹⁄[€î⁄YPò\ë[ùûKõZ\‹⁄[€ã\⁄YKXò\ãY[ùûKŸ]K[Z\‹⁄[€ãZYI N¬àBÇàù[ò›[€à]]][€êYôôX›”X\^[›]
]]][€äH¬à€€ú›\ôŸ]H]]][€èÀù\ôŸ]¬àYà
\ôŸ]ÀõõŸU\HOOHJH¬àYà
\ôŸ]õX]⁄\œÀä	»€X\€X\€›]\ãõXYõ]X€€ùZ[ô\â JHô]\õàùYN¬àYà
\ôŸ]ò€‹Ÿ\›Àä	Àõò]òò\ãõ[Ÿ[õ[Ÿ[XòX⁄Ÿõ‹ôõ‹›€ã[Y[ùKú‹›ô\ã‹õ€OHôX[Ÿ»óI JHô]\õàùYN¬àBàõ‹à
€€ú›€€X›[€àŸà€]]][€èÀòYYõŸ\À]]][€èÀúô[[›ôYõŸ\◊JH¬àYà
X€€X›[€èÀõ[ô›
H€€ù[ùYN¬àõ‹à
€€ú›õŸHŸà€€X›[€äH¬àYà
[õŸHõŸKõõŸU\HOOHJH€€ù[ùYN¬àYà
õŸKõX]⁄\œÀä	»€X\€X\€›]\ãõXYõ]X€€ùZ[ô\ãõò]òò\ãõ[Ÿ[õ[Ÿ[XòX⁄Ÿõ‹ôõ‹›€ã[Y[ùKú‹›ô\ã‹õ€OHôX[Ÿ»óI JHô]\õàùYN¬àYà
õŸKú]Y\ûTŸ[X›‹èÀä	»€X\€X\€›]\ãõXYõ]X€€ùZ[ô\ãõò]òò\ãõ[Ÿ[õ[Ÿ[XòX⁄Ÿõ‹ôõ‹›€ã[Y[ùKú‹›ô\ã‹õ€OHôX[Ÿ»óI JHô]\õàùYN¬àBàBàô]\õàò[ŸN¬àBÇÇà€€ú›SPSê—W–ïRSSë‘◊”PT”ì’P—W“QH	€X€\ÀX[X[òŸKXùZ[[ô‹À[X\[õ›XŸIŒ¬Çàù[ò›[€àö[ô[X[òŸPùZ[[ô‹”X\[[Y[ù

H¬àYà
Z\–[X[òŸPùZ[[ô‹–€€ù^

JHô]\õàù[¬à€€ú›ÿ[ôY]\»H\úò^Kôúõ€Jÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	»›ô\òò[ôYŸXò]YYK[X\›ô\òò[ôYŸXòY]YK[X\€X\€X\€›]\àõXYõ]X€€ùZ[ô\ã⁄Y
èHôŸXò]YYHóV⁄Y
èHõX\óK⁄Y
èHôŸXòY]YHóV⁄Y
èHõX\óKõXYõ]X€€ùZ[ô\â JN¬àô]\õàÿ[ôY]\Àôö[ô
[[Y[ùOà¬àYà
Y[[Y[ù[[Y[ùò€‹Ÿ\›
…‘–‘íTò€€ùõ€YK…‘–‘íTú[ô[YK…‘–‘íTùôZX€T›]\“YK…‘–‘íTúô\‹›\ôPõÿ\ôYX
JHô]\õàò[ŸN¬à€€ú›ôX›H[[Y[ùôŸ]õ›[ô[ô–€Y[ùôX›Àä
N¬àô]\õà\ôX›ôX›ù⁄YèHLåôX›öZY⁄èHLå[[Y[ùöYOOH	€X\	»[[Y[ùöYOOH	›ô\òò[ôYŸXò]YYK[X\	»[[Y[ùöYOOH	›ô\òò[ôYŸXòY]YK[X\	Œ¬àJHù[¬àBÇàù[ò›[€àö[ôô\‹€ú⁄]ôP€€[[ä[[Y[ù
H¬à]›\úô[ùH[[Y[ù¬àõ‹à
]\H»›\úô[ù	âà›\úô[ùOOHÿ›[Y[ùòõŸH	âà\Œ»\
œHK›\úô[ùH›\úô[ùú\ô[ù[[Y[ù
H¬à€€ú›€\‹”ò[YHH\[Ÿà›\úô[ùò€\‹”ò[YHOOH	‹›ö[ô…»»›\úô[ùò€\‹”ò[YHà	…Œ¬àYà
◊ò€€JŒûﬂ€_Yﬂ
KW
◊ã›Kù\›
€\‹”ò[YJJHô]\õà›\úô[ù¬àBàô]\õà[[Y[ùÀú\ô[ù[[Y[ùù[¬àBÇàù[ò›[€àö[ô[X[òŸPùZ[[ô‹”\›€€[[äX\€€[[äH¬à€€ú›õ›»HX\€€[[èÀú\ô[ù[[Y[ù¬àYà
\õ› Hô]\õàù[¬à€€ú›⁄Xõ[ô‹»H\úò^Kôúõ€Jõ›Àò⁄[ô[äKôö[\ä⁄[Oà⁄[OOHX\€€[[äN¬àô]\õà⁄Xõ[ô‹Àôö[ô
⁄[Oà⁄[ú]Y\ûTŸ[X›‹èÀä	›XõI JH⁄Xõ[ô‹Àôö[ô
⁄[Oà◊ò€€JŒûﬂ€_Yﬂ
KW
◊ã›Kù\›
›ö[ô ⁄[ò€\‹”ò[YH	… JJHX\€€[[ãõô^[[Y[ù⁄Xõ[ôŒ¬àBÇàù[ò›[€à[X[òŸPùZ[[ô‹”X\õ›XŸR[
[òXõY
H¬à€€ú›õÿ⁄ŸYHY[òXõY¬àô]\õàà‹[à€\‹œHõX€\ÀX[X[òŸK[X\X€‹HèÇà›õ€ôœâÿõÿ⁄ŸY»	–[X[òŸHX\õÿ⁄Ÿ\à”â»à	–[X[òŸHX\õÿ⁄Ÿ\à—ëâﬂO‹›õ€ôœÇà€X[âÿõÿ⁄ŸY»	’H[X[òŸHùZ[[ô‹»»€›\úŸ\»\›ô[XZ[ú»]òZ[XõH]ù[⁄Yà]»X\[\»[ô[X[òŸHX\öŸ\à]X⁄Y[ù\ôHõÿ⁄ŸYâ»à	’\õàHõÿ⁄Ÿ\à€à»›‹HX]ûHX\[àH[X[òŸHùZ[[ô‹»»€›\úŸ\»Y[ùKâﬂO‹€X[Çà‹‹[èÇàù]€à\OHòù]€àà]K[X€\ÀX[X[òŸK[X\]ŸŸ€OHâÿõÿ⁄ŸY»	‹ô\›‹ôI»à	ÿõÿ⁄…ﬂHèâÿõÿ⁄ŸY»	—\ÿXõHõÿ⁄Ÿ\à	àô[ÿY	»à	—[òXõHõÿ⁄Ÿ\à	àô[ÿY	ﬂOÿù]€èÇà¬àBÇàù[ò›[€àô[ô\ê[X[òŸPùZ[[ô‹”X\ôYô\ô[òŸJ
H¬àYà
Z\–[X[òŸPùZ[[ô‹–€€ù^

JHô]\õàò[ŸN¬à€€ú›õ€›Hÿ›[Y[ùôÿ›[Y[ù[[Y[ù¬à€€ú›[òXõYH›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸN¬àõ€›úŸ]]öXù]J	Ÿ]K[X€\ÀX[X[òŸKXùZ[[ô‹À\YŸIÀ	›ùYI N¬àõ€›úŸ]]öXù]J	Ÿ]K[X€\ÀX[X[òŸKXùZ[[ô‹À[X\	À[òXõY»	Ÿ[òXõY	»à	Ÿ\ÿXõY	 N¬à€€ú›X\[[Y[ùHö[ô[X[òŸPùZ[[ô‹”X\[[Y[ù

N¬àYà
[X\[[Y[ù
Hô]\õàò[ŸN¬à€€ú›X\€€[[àHö[ôô\‹€ú⁄]ôP€€[[äX\[[Y[ù
N¬à€€ú›\›€€[[àHö[ô[X[òŸPùZ[[ô‹”\›€€[[äX\€€[[äN¬àYà
[X\€€[[äHô]\õàò[ŸN¬àX\€€[[ãò€\‹”\›ùŸŸ€J	€X€\ÀX[X[òŸKXùZ[[ô‹À[X\X€€[[âÀY[òXõY
N¬àX\€€[[ãùŸŸ€P]öXù]J	Ÿ]K[X€\ÀX[X[òŸK[X\X€€[[âÀY[òXõY
N¬àX\€€[[ãúŸ]]öXù]J	ÿ\öXKZY[âÀ›ö[ô Y[òXõY
JN¬àYà
\›€€[[äH¬à\›€€[[ãò€\‹”\›ùŸŸ€J	€X€\ÀX[X[òŸKXùZ[[ô‹À[\›X€€[[âÀY[òXõY
N¬à\›€€[[ãùŸŸ€P]öXù]J	Ÿ]K[X€\ÀX[X[òŸK[\›X€€[[âÀY[òXõY
N¬àBà]õ›XŸHHÿ›[Y[ùôŸ][[Y[ùûRY
SPSê—W–ïRSSë‘◊”PT”ì’P—W“Q
N¬à€€ú›\ôŸ]H[òXõY»X\€€[[àà
\›€€[[àX\€€[[ãú\ô[ù[[Y[ùÿ›[Y[ùòõŸJN¬àYà
[õ›XŸJH¬àõ›XŸHHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àõ›XŸKöYHSPSê—W–ïRSSë‘◊”PT”ì’P—W“Q¬àBàõ›XŸKò€\‹”\›ùŸŸ€J	€X€\ÀX[X[òŸK[X\Y[òXõY	À[òXõY
N¬àõ›XŸKö[õô\íSH[X[òŸPùZ[[ô‹”X\õ›XŸR[
[òXõY
N¬àYà
õ›XŸKú\ô[ù[[Y[ùOOH\ôŸ]
H\ôŸ]ö[úŸ\ùôYõ‹ôJõ›XŸK\ôŸ]ôö\ú›⁄[ù[
N¬àô]\õàùYN¬àBÇàù[ò›[€àù[ôTù[ù[YPÿX⁄\ õ›»H]Kõõ› 
JH¬àõ‹à
€€ú›€Z\‹⁄[€íY[ô[HŸàZ\‹⁄[€î[ô[ÿX⁄Kô[ùöY\ 
JH¬àYà
\[ô[Àö\–€€õôX›Y
HZ\‹⁄[€î[ô[ÿX⁄Kô[]JZ\‹⁄[€íY
N¬àBàõ‹à
€€ú›€Z\‹⁄[€íYÿX⁄YHŸàZ\‹⁄[€î€ò\⁄›ÿX⁄Kô[ùöY\ 
JH¬àYà
]ôSZ\‹⁄[€î€ò\⁄›Àö\ Z\‹⁄[€íY
JH€€ù[ùYN¬àYà
õ›»Hù[Xô\äÿX⁄YÀõ\›\ŸYõ› HàRT‘“S”ó––P“W‘ëUSïS”ó”T HZ\‹⁄[€î€ò\⁄›ÿX⁄Kô[]JZ\‹⁄[€íY
N¬àBàõ‹à
€€ú›Z\‹⁄[€íYŸàZ\‹⁄[€ì›ô\õ^Uô\ú⁄[€úÀöŸ^\ 
JH¬àYà
[Z\‹⁄[€ì›ô\õ^Q]Kö\ Z\‹⁄[€íY
JHZ\‹⁄[€ì›ô\õ^Uô\ú⁄[€úÀô[]JZ\‹⁄[€íY
N¬àBàõ‹à
€€ú›€ò[YKÿX⁄YHŸàX\öŸ\îôY⁄\›ûPÿX⁄Kô[ùöY\ 
JH¬àYà
õ›»Hù[Xô\äÿX⁄YÀò‹ôX]Y]õ› HàïSïSQW––P“W‘ïSëW”T HX\öŸ\îôY⁄\›ûPÿX⁄Kô[]Jò[YJN¬àBàõ‹à
€€ú›⁄Ÿ^KÿX⁄YHŸàô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kô[ùöY\ 
JH¬àYà
õ›»Hù[Xô\äÿX⁄YÀò‹ôX]Y]õ› HàX]õX^
à
àëT”’Tê—W—–T‘ëQîëT“”TÀïSïSQW––P“W‘ïSëW”T JHô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kô[]JŸ^JN¬àBàYà
ô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kú⁄^ôHàN
H¬à€€ú›‹ô\ôYH\úò^Kôúõ€Jô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kô[ùöY\ 
JKú€‹ù

KäHOàù[Xô\äVÃWOÀò‹ôX]Y]
HHù[Xô\äñÃWOÀò‹ôX]Y]
JN¬àõ‹à
€€ú›⁄Ÿ^WHŸà‹ô\ôYú€XŸJô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kú⁄^ôHHN
JHô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kô[]JŸ^JN¬àBà€€ú››\úô[ùôZX€S^Y\ú»Hô]»Ÿ]
Ÿ]ôZX€SX\öŸ\ì^Y\ú 
JN¬à€€ú››\úô[ùùZ[[ô”^Y\ú»Hô]»Ÿ]
Ÿ]ùZ[[ô”X\öŸ\ì^Y\ú 
JN¬àõ‹à
€€ú›^Y\àŸà\úò^Kôúõ€JX€€õ€^RY[ïôZX€S^Y\ú JH¬àYà
[^Y\à
[^Y\ãó€X\	âàX›\úô[ùôZX€S^Y\úÀö\ ^Y\äJJHX€€õ€^RY[ïôZX€S^Y\úÀô[]J^Y\äN¬àBàõ‹à
€€ú›^Y\àŸà\úò^Kôúõ€JX€€õ€^RY[êùZ[[ô”^Y\ú JH¬àYà
[^Y\à
[^Y\ãó€X\	âàX›\úô[ùùZ[[ô”^Y\úÀö\ ^Y\äJJHX€€õ€^RY[êùZ[[ô”^Y\úÀô[]J^Y\äN¬àBàYà
\›]Kúô\€›\òŸQÿ\ô[òXõY
H¬àô\€›\òŸQÿ\[ò[\⁄\–ÿX⁄Kò€X\ä
N¬àô\€›\òŸQÿ\ôZX€P€€ù^ÿX⁄HH»Ÿ^Nà	…À‹ôX]Y]à]òZ[XõNà◊KûU⁄Ÿ[éàô]»X\

HN¬àBàBÇàù[ò›[€à[ú›[[X[òŸPùZ[[ô‹‘YŸS‹[Z\ÿ][€ä
H¬à€€ú›[ö]X[R[ê€€ù^H\–[X[òŸPùZ[[ô‹–€€ù^

N¬à€€ú›[òXõYH›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸN¬à]ô[ô\ï[Y\àHù[¬à€€ú›ô[ô\ï⁄[îô[]ò[ùH

HOà¬àYà
Z\–[X[òŸPùZ[[ô‹–€€ù^

JH¬àÿ›[Y[ùôŸ][[Y[ùûRY
SPSê—W–ïRSSë‘◊”PT”ì’P—W“Q
OÀúô[[›ôJ
N¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	ÀõX€\ÀX[X[òŸKXùZ[[ô‹À[X\X€€[[â Kôõ‹ëXX⁄
[[Y[ùOà[[Y[ùò€\‹”\›úô[[›ôJ	€X€\ÀX[X[òŸKXùZ[[ô‹À[X\X€€[[â JN¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	ÀõX€\ÀX[X[òŸKXùZ[[ô‹À[\›X€€[[â Kôõ‹ëXX⁄
[[Y[ùOà[[Y[ùò€\‹”\›úô[[›ôJ	€X€\ÀX[X[òŸKXùZ[[ô‹À[\›X€€[[â JN¬à€X\ê[X[òŸPùZ[[ô‹—X\õP€€ù^

N¬àô]\õàò[ŸN¬àBàYà
Y[òXõY
H‹[Z\ŸP[X[òŸPùZ[[ô‹–€›\úŸUXõQX\õJ
N¬àô]\õàô[ô\ê[X[òŸPùZ[[ô‹”X\ôYô\ô[òŸJ
N¬àN¬àYà
[ö]X[R[ê€€ù^Y[òXõY
H¬àô[ô\ï⁄[îô[]ò[ù

N¬àù[ù[YTŸ][Y[›]
ô[ô\ï⁄[îô[]ò[ù
N¬àù[ù[YTŸ][Y[›]
ô[ô\ï⁄[îô[]ò[ùÃ
N¬àù[ù[YTŸ][Y[›]
ô[ô\ï⁄[îô[]ò[ùLå
N¬à€€ú›YŸSÿúŸ\ùô\àHù[ù[YUòX⁄”ÿúŸ\ùô\äô]»]]][€ìÿúŸ\ùô\ä]]][€ú»Oà¬àYà
[]]][€úÀú€€YJ]]][€àOà]]][€ãòYYõŸ\œÀõ[ô›]]][€ãúô[[›ôYõŸ\œÀõ[ô›
JHô]\õé¬àù[ù[YP€X\ï[Y[›]
ô[ô\ï[Y\äN¬àô[ô\ï[Y\àHù[ù[YTŸ][Y[›]


HOà¬àô[ô\ï[Y\àHù[¬àô[ô\ï⁄[îô[]ò[ù

N¬àK
N¬àJJN¬àYŸSÿúŸ\ùô\ãõÿúŸ\ùôJÿ›[Y[ùòõŸK»⁄[\›àùYK›XùôYNàùYHJN¬àBàù[ù[YS\›[äÿ›[Y[ù	ÿ€X⁄…À]ô[ùOà¬à€€ú›ù]€àH€‹Ÿ\›]ô[ù\ôŸ]
]ô[ù	÷Ÿ]K[X€\ÀX[X[òŸK[X\]ŸŸ€WI N¬àYà
Xù]€äHô]\õé¬à]ô[ùúô]ô[ùYò][

N¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬à›]Kò[X[òŸPùZ[[ô‹”X\Hù]€ãô]\Ÿ]õX€\–[X[òŸSX\ŸŸ€HOOH	‹ô\›‹ôIŒ¬àÿ]ôT›]J
N¬àù]€ãô\ÿXõYHùYN¬àù]€ãù^€€ù[ùH	‘ô[ÿY[ô¯†)âŒ¬àù[ù[YTŸ][Y[›]


HOàÿÿ][€ãúô[ÿY

KLå
N¬àKùYJN¬àù[ù[YS€ê€X[ù\


HOà¬àÿ›[Y[ùôŸ][[Y[ùûRY
SPSê—W–ïRSSë‘◊”PT”ì’P—W“Q
OÀúô[[›ôJ
N¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	ÀõX€\ÀX[X[òŸKXùZ[[ô‹À[X\X€€[[â Kôõ‹ëXX⁄
[[Y[ùOà[[Y[ùò€\‹”\›úô[[›ôJ	€X€\ÀX[X[òŸKXùZ[[ô‹À[X\X€€[[â JN¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	ÀõX€\ÀX[X[òŸKXùZ[[ô‹À[\›X€€[[â Kôõ‹ëXX⁄
[[Y[ùOà[[Y[ùò€\‹”\›úô[[›ôJ	€X€\ÀX[X[òŸKXùZ[[ô‹À[\›X€€[[â JN¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
	÷Ÿ]K[X€\ÀX[X[òŸK[X\X€€[[óKŸ]K[X€\ÀX[X[òŸK[\›X€€[[óI Kôõ‹ëXX⁄
[[Y[ùOà¬à[[Y[ùúô[[›ôP]öXù]J	Ÿ]K[X€\ÀX[X[òŸK[X\X€€[[â N¬à[[Y[ùúô[[›ôP]öXù]J	Ÿ]K[X€\ÀX[X[òŸK[\›X€€[[â N¬àJN¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùÀúô[[›ôP]öXù]J	Ÿ]K[X€\ÀX[X[òŸKXùZ[[ô‹À\YŸI N¬àJN¬àô]\õà\–[X[òŸPùZ[[ô‹‘]

H	âàY[òXõY¬àBÇÇàù[ò›[€à€€õôX›XZ[ì]]][€ìÿúŸ\ùô\ä
H¬àYà
[XZ[ì]]][€ìÿúŸ\ùô\àù[ù[YKô\›õﬁYYYÿ›[Y[ùòõŸJHô]\õé¬àûH»XZ[ì]]][€ìÿúŸ\ùô\ãô\ÿ€€õôX›

N»Hÿ]⁄
\úäHﬂBà€€ú›õ€›»Hô]»Ÿ]

N¬à€€ú›X\[[Y[ùHŸ]\ôŸ\›XYõ]X\

N¬à€€ú›X\õ€›HX\[[Y[ùÀò€‹Ÿ\›Àä	»€X\€›]\â HX\[[Y[ùÀú\ô[ù[[Y[ùX\[[Y[ù¬à€€ú›Z\‹⁄[€îõ€›Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä	»€Z\‹⁄[€úÀ€Z\‹⁄[€ó€\›õZ\‹⁄[€úÀ\[ô[õZ\‹⁄[€ã[\›	 N¬àYà
X\õ€›Àö\–€€õôX›Y
Hõ€›ÀòY
X\õ€›
N¬àYà
Z\‹⁄[€îõ€›Àö\–€€õôX›Y
Hõ€›ÀòY
Z\‹⁄[€îõ€›
N¬àYà
\õ€›Àú⁄^ôJH¬àXZ[ì]]][€ìÿúŸ\ùô\ëò[òX⁄–X›]ôHHùYN¬àXZ[ì]]][€ìÿúŸ\ùô\ãõÿúŸ\ùôJÿ›[Y[ùòõŸK»⁄[\›àùYK›XùôYNàùYHJN¬àô]\õé¬àBàXZ[ì]]][€ìÿúŸ\ùô\ëò[òX⁄–X›]ôHHò[ŸN¬àõ‹à
€€ú›õ€›Ÿàõ€› HXZ[ì]]][€ìÿúŸ\ùô\ãõÿúŸ\ùôJõ€›»⁄[\›àùYK›XùôYNàùYHJN¬àXZ[ì]]][€ìÿúŸ\ùô\ãõÿúŸ\ùôJÿ›[Y[ùòõŸK»⁄[\›àùYK›XùôYNàò[ŸHJN¬àBà\ﬁ[ò»ù[ò›[€àù[ëYô\úôY‹\ò][€ò[›\ù\

H¬àYà
‹\ò][€ò[›\ù\›\ùYù[ù[YKô\›õﬁYY
Hô]\õé¬à€€ú›‹\ò][€ò[\ôõ‹õX[òŸT›\ùY]H›\ù\€ÿ⁄ 
N¬àYà
ÿ›[Y[ùöY[äH¬àù[ù[YTŸ][Y[›]


HOàÿ⁄Y[QYô\úôY‹\ò][€ò[›\ù\

KL
N¬àô]\õé¬àBà‹\ò][€ò[›\ù\›\ùYHùYN¬àÿYÿX⁄Yö[ò[ò⁄X[ù[\ 
N¬àÿYÿX⁄Yö[ò[ò⁄X[€XﬁJ
N¬à[ú›\ôQö[ò[òŸUò][‹ôY[ùX[
ö[ò[òŸT^Y\íY[ù]J
JN¬àÿÿ[í[õ[ôSZ\‹⁄[€ìX\öŸ\ë]J
N¬à[ú›[Z\‹⁄[€ìX\öŸ\êY€⁄ 
N¬à[ú›[òY[”Y\‹ÿYŸR€⁄ 
N¬àYà
›]KõZ\‹⁄[€ïò[YJH[ú›[Z\‹⁄[€ïò[YU⁄[ô›‹ 
N¬à›\ù\]T\‹–X›]ôHHùYN¬àûH¬àYà
ôZX€Q]SôYYY

JH]ÿZ]ôYúô\⁄\ú€€ò[ôZX€Q]JùYJN¬àHö[ò[H¬à›\ù\]T\‹–X›]ôHHò[ŸN¬àBàù[ù[YP€X\ï[Y[›]
Z\‹⁄[€î€ò\⁄›[Y\äN¬àZ\‹⁄[€î€ò\⁄›[Y\àHù[¬àYà
Z\‹⁄[€î€ò\⁄›”ôYYY

JHôYúô\⁄Z\‹⁄[€î€ò\⁄› 
N¬àYà
Z\‹⁄[€î‹]€ìYôXﬁX€SôYYY

JHö[YSZ\‹⁄[€î‹]€ë]X›‹ä
N¬àYà
\›]KúÿYôS[ŸKô[òXõY
H¬àYà
›]Kú›X⁄—]X›‹ãô[òXõY
Hÿ⁄Y[T›X⁄”Z\‹⁄[€îôYúô\⁄
N
N¬àYà
›]Kùò[ú‹‹ùÿ]⁄\äHÿ⁄Y[Uò[ú‹‹ùÿ]⁄\îôYúô\⁄
åå
N¬àYà
›]Kúô\€›\òŸQÿ\ô[òXõY
Hÿ⁄Y[Tô\€›\òŸQÿ\ôYúô\⁄
çå
N¬àYà
›]Kù[ö]€€[Z]Y[ù
Hÿ⁄Y[U[ö]€€[Z]Y[ùôYúô\⁄
Ã
N¬àYà
›]Kò[X[òŸP‹ôY] Hÿ⁄Y[P[X[òŸP‹ôY]ôYúô\⁄
Ãå
N¬àYà
›]KõZ\‹⁄[€êYŸJHÿ⁄Y[SZ\‹⁄[€êYŸTôYúô\⁄
Õ
N¬àBà‹\ò][€ò[›\ù\€€\]HHùYN¬àÿ⁄Y[S‹\ò][€ò[[ô[‘ô[ô\ä
N¬àYà
›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY	âà\›]KúÿYôS[ŸKô[òXõY
Hÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\äLå
N¬àÿ⁄Y[Q[òXõYX\ôYúô\⁄\ »[ò€YT€ò\⁄›Œàò[ŸK‹⁄][€î[ô[àò[ŸKX\€õNàùYHJN¬àôX€‹ô›\ù\Y]öX 	€‹\ò][€ò[›\ù\\…À‹\ò][€ò[\ôõ‹õX[òŸT›\ùY]»‹\ò][€ò[›\ù\€€\]NàùYHJN¬ÇàBàù[ò›[€àÿ⁄Y[QYô\úôY‹\ò][€ò[›\ù\
[^HH’TïT”‘TêUS”êS—SVW”T H¬àYà
‹\ò][€ò[›\ù\›\ùYù[ù[YKô\›õﬁYY
Hô]\õé¬àù[ù[YTŸ][Y[›]


HOàù[ù[YTù[ï⁄[íYJ

HOà¬àù[ëYô\úôY‹\ò][€ò[›\ù\

Kòÿ]⁄
\úàOà¬à€€⁄][ò[]X‹‘ôX€‹ô\úõ‹ä	€‹\ò][€ò[‹›\ù\	 N¬à‹\ò][€ò[›\ù\€€\]HHùYN¬à›\ù\]T\‹–X›]ôHHò[ŸN¬à€€ú€€KôXùY …‘–‘íTõò[Y_WHYô\úôY›\ù\ôX€›ô\ôYYù\à[à‹\ò][€ò[[ö]X[\ÿ][€à\úõ‹ãò\úäN¬à€€õôX›XZ[ì]]][€ìÿúŸ\ùô\ä
N¬àJN¬àK’TïT“QW’SQS’U”T KX]õX^
ù[Xô\ä[^JH
JN¬àBÇà€€ú›UU◊”–Q–S’ëRP”T◊‘—SP’‘àH	ÿKõZ\‹⁄[ô◊›ôZX€\◊€ÿY⁄ôYäèHã€Z\‹⁄[ô◊›ôZX€\»óIŒ¬à€€ú›UU◊”–Q–S’ëRP”T◊”RT‘“S”ó‘ì”’‘—SP’‘àH	»€Y⁄õﬁÿõﬁ€Y⁄õﬁõY⁄õﬁÿ€€ù[ùõ[Ÿ[ú⁄›Àõ[Ÿ[ö[ãõ[Ÿ[X€€ù[ù‹õ€OHôX[Ÿ»óKùZKYX[ŸÀX€€ù[ùùZKYX[Ÿ…Œ¬à€€ú›UU◊”–Q–S’ëRP”T◊”PV‘ëTUQT’»HL¬à€€ú›UU◊”–Q–S’ëRP”T◊‘—UW”T»HN¬à€€ú›UU◊”–Q–S’ëRP”T◊’SQS’U”T»Hå¬à€€ú›UU◊”–Q–S’ëRP”T◊“QSó‘ëUíQT»Hç¬à]]]”ÿY[ôZX€\”ÿúŸ\ùô\àHù[¬à]]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\àHù[¬à]]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\àHù[¬à]]]”ÿY[ôZX€\‘ÿÿ[ï[Y\àHù[¬à]]]”ÿY[ôZX€\‘ô[X\ŸU[Y\àHù[¬à]]]”ÿY[ôZX€\”Z\‹⁄[€íYHù[¬à]]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›Hù[¬à]]]”ÿY[ôZX€\–X›]ôS[ö»Hù[¬à]]]”ÿY[ôZX€\–X›]ôT⁄Y€ò]\ôHH	…Œ¬à]]]”ÿY[ôZX€\“[ëõY⁄Hò[ŸN¬à]]]”ÿY[ôZX€\‘ô\]Y\›€›[ùH¬à]]]”ÿY[ôZX€\“Y[îô]ûP€›[ùH¬à€€ú›]]”ÿY[ôZX€\‘ô\]Y\›YYŸ\»Hô]»Ÿ]

N¬Çàù[ò›[€à]]”ÿY[ôZX€\”[ö“[ôõ [ö H¬àYà
[[ö»[öÀõõŸU\HOOHH[[öÀõX]⁄\œÀäUU◊”–Q–S’ëRP”T◊‘—SP’‘äJHô]\õàù[¬à]\õ¬àûH»\õHô]»Tì
[öÀôŸ]]öXù]J	⁄ôYâ H[öÀöôYãÿÿ][€ãöôYäN»Hÿ]⁄
\úäH»ô]\õàù[»BàYà
\õõ‹öY⁄[àOOHÿÿ][€ãõ‹öY⁄[äHô]\õàù[¬à€€ú›X]⁄H\õú]ò[YKõX]⁄
◊ó€Z\‹⁄[€ú◊ 
 W€Z\‹⁄[ô◊›ôZX€\◊œ…›JN¬àYà
[X]⁄
Hô]\õàù[¬à€€ú›ò]”ŸôúŸ]H\õúŸX\ò⁄\ò[\ÀôŸ]
	€ŸôúŸ]‹YŸI N¬à€€ú›ŸôúŸ]YŸHHù[Xô\ãö\—ö[ö]Jù[Xô\äò]”ŸôúŸ]
JH»X]õX^
ù[Xô\äò]”ŸôúŸ]
JHà¬àô]\õà¬àZ\‹⁄[€íYàX]⁄ÃWKàŸôúŸ]YŸKà⁄Y€ò]\ôNà	€X]⁄ÃW_Nâ€ŸôúŸ]YŸ_Nâ›\õú]ò[Y_I›\õúŸX\ò⁄XàôYéà\õöôYÇàN¬àBÇàù[ò›[€à]]”ÿY[ôZX€\—[[Y[ùö\⁄XõJ[[Y[ù
H¬àYà
Y[[Y[ùÀö\–€€õôX›Y[[Y[ùöY[à[[Y[ùôŸ]]öXù]OÀä	ÿ\öXKZY[â HOOH	›ùYI Hô]\õàò[ŸN¬àYà
[[Y[ùõX]⁄\œÀä	Œô\ÿXõYô\ÿXõYÿ\öXKY\ÿXõYHùùYHóI JHô]\õàò[ŸN¬àûH¬à€€ú››[HHYŸU⁄[ô›ÀôŸ]€€\]Y›[OÀä[[Y[ù
N¬àYà
›[OÀô\‹^HOOH	€õ€ôI»›[OÀùö\⁄Xö[]HOOH	⁄Y[â»›[OÀùö\⁄Xö[]HOOH	ÿ€€\ŸI»›[OÀú⁄[ù\ë]ô[ù»OOH	€õ€ôI»ù[Xô\ä›[OÀõ‹X⁄]JHOOH
Hô]\õàò[ŸN¬à€€ú›ôX›H[[Y[ùôŸ]õ›[ô[ô–€Y[ùôX›Àä
N¬àô]\õà\ôX›
ôX›ù⁄YàH	âàôX›öZY⁄àJN¬àHÿ]⁄
\úäH¬àô]\õàùYN¬àBàBÇàù[ò›[€à]]”ÿY[ôZX€\‘ô\€€ôSZ\‹⁄[€îõ€›
[ö H¬àô]\õà[öÀò€‹Ÿ\›ÀäUU◊”–Q–S’ëRP”T◊”RT‘“S”ó‘ì”’‘—SP’‘äH[öÀú\ô[ù[[Y[ùÿ›[Y[ùòõŸN¬àBÇàù[ò›[€à]]”ÿY[ôZX€\–ÿ[ôY]S[ö‹ 
H¬àYà
\›]Kò]]”ÿY[ôZX€\ Hô]\õà◊N¬à€€ú›]Y\ûTõ€›H]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›Àö\–€€õôX›Y	âà]]”ÿY[ôZX€\—[[Y[ùö\⁄XõJ]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›
Bà»]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›ààÿ›[Y[ù¬àô]\õà\úò^Kôúõ€J]Y\ûTõ€›ú]Y\ûTŸ[X›‹ê[
UU◊”–Q–S’ëRP”T◊‘—SP’‘äJBàúô]ô\úŸJ
BàõX\
[ö»Oà
»[öÀ[ôõŒà]]”ÿY[ôZX€\”[ö“[ôõ [ö HJJBàôö[\äÿ[ôY]HOàõ€€X[äÿ[ôY]Kö[ôõ JN¬àBÇàù[ò›[€à€X\ê]]”ÿY[ôZX€\‘ô[X\ŸU[Y\ä
H¬àù[ù[YP€X\ï[Y[›]
]]”ÿY[ôZX€\‘ô[X\ŸU[Y\äN¬à]]”ÿY[ôZX€\‘ô[X\ŸU[Y\àHù[¬àBÇàù[ò›[€à\ÿ€€õôX›]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\ä
H¬àù[ù[YU[ùòX⁄”ÿúŸ\ùô\ä]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\äN¬à]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\àHù[¬àBÇàù[ò›[€à\ÿ€€õôX›]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\ä
H¬àù[ù[YU[ùòX⁄”ÿúŸ\ùô\ä]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\äN¬à]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\àHù[¬àBÇàù[ò›[€àô[X\ŸP]]”ÿY[ôZX€\‘ô\]Y\›
»ÿ⁄Y[HHùYHHHﬂJH¬à€X\ê]]”ÿY[ôZX€\‘ô[X\ŸU[Y\ä
N¬à\ÿ€€õôX›]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\ä
N¬à]]”ÿY[ôZX€\“[ëõY⁄Hò[ŸN¬à]]”ÿY[ôZX€\–X›]ôS[ö»Hù[¬à]]”ÿY[ôZX€\–X›]ôT⁄Y€ò]\ôHH	…Œ¬àYà
ÿ⁄Y[H	âà›]Kò]]”ÿY[ôZX€\ Hÿ⁄Y[P]]”ÿY[ôZX€\‘ÿÿ[äUU◊”–Q–S’ëRP”T◊‘—UW”T N¬àBÇàù[ò›[€àô\Ÿ]]]”ÿY[ôZX€\”Z\‹⁄[€ä
H¬àô[X\ŸP]]”ÿY[ôZX€\‘ô\]Y\›
»ÿ⁄Y[Nàò[ŸHJN¬à\ÿ€€õôX›]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\ä
N¬à]]”ÿY[ôZX€\”Z\‹⁄[€íYHù[¬à]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›Hù[¬à]]”ÿY[ôZX€\‘ô\]Y\›€›[ùH¬à]]”ÿY[ôZX€\“Y[îô]ûP€›[ùH¬à]]”ÿY[ôZX€\‘ô\]Y\›YYŸ\Àò€X\ä
N¬àBÇàù[ò›[€àÿúŸ\ùôP]]”ÿY[ôZX€\‘õ€›
õ€›
H¬à\ÿ€€õôX›]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\ä
N¬àYà
\õ€›õ€›OOHÿ›[Y[ùòõŸJHô]\õé¬à€€ú›ÿúŸ\ùô\àHù[ù[YUòX⁄”ÿúŸ\ùô\äô]»]]][€ìÿúŸ\ùô\ä

HOà¬àYà
\›]Kò]]”ÿY[ôZX€\ Hô]\õé¬àYà
\õ€›ö\–€€õôX›YX]]”ÿY[ôZX€\—[[Y[ùö\⁄XõJõ€›
JH¬àô\Ÿ]]]”ÿY[ôZX€\”Z\‹⁄[€ä
N¬àô]\õé¬àBàÿ⁄Y[P]]”ÿY[ôZX€\‘ÿÿ[äUU◊”–Q–S’ëRP”T◊‘—UW”T N¬àJJN¬àÿúŸ\ùô\ãõÿúŸ\ùôJõ€›¬à]öXù]\ŒàùYKà]öXù]Qö[\éà…ÿ€\‹…À	‹›[IÀ	⁄Y[âÀ	ÿ\öXKZY[â◊BàJN¬à]]”ÿY[ôZX€\‘õ€›ÿúŸ\ùô\àHÿúŸ\ùô\é¬àBÇàù[ò›[€àÿúŸ\ùôP]]”ÿY[ôZX€\”[ö [ö H¬à\ÿ€€õôX›]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\ä
N¬àYà
[[ö Hô]\õé¬à€€ú›ÿúŸ\ùô\àHù[ù[YUòX⁄”ÿúŸ\ùô\äô]»]]][€ìÿúŸ\ùô\ä

HOà¬àYà
\›]Kò]]”ÿY[ôZX€\ Hô]\õé¬à€€ú›[ôõ»H]]”ÿY[ôZX€\”[ö“[ôõ [ö N¬à€€ú›⁄[ôŸYHõ€€X[ä[ôõ»	âà[ôõÀú⁄Y€ò]\ôHOOH]]”ÿY[ôZX€\–X›]ôT⁄Y€ò]\ôJN¬àYà
[[öÀö\–€€õôX›YZ[ôõ»X]]”ÿY[ôZX€\—[[Y[ùö\⁄XõJ[ö H⁄[ôŸY
H¬àô[X\ŸP]]”ÿY[ôZX€\‘ô\]Y\›
»ÿ⁄Y[NàùYHJN¬àBàJJN¬àÿúŸ\ùô\ãõÿúŸ\ùôJ[öÀ¬à]öXù]\ŒàùYKà]öXù]Qö[\éà…⁄ôYâÀ	ÿ€\‹…À	‹›[IÀ	⁄Y[âÀ	ÿ\öXKZY[âÀ	ÿ\öXKY\ÿXõY	◊BàJN¬à]]”ÿY[ôZX€\”[ö”ÿúŸ\ùô\àHÿúŸ\ùô\é¬àBÇàù[ò›[€àÿ⁄Y[P]]”ÿY[ôZX€\‘ÿÿ[ä[^HH
H¬àYà
\›]Kò]]”ÿY[ôZX€\»ù[ù[YKô\›õﬁYY
Hô]\õé¬àù[ù[YP€X\ï[Y[›]
]]”ÿY[ôZX€\‘ÿÿ[ï[Y\äN¬à]]”ÿY[ôZX€\‘ÿÿ[ï[Y\àHù[ù[YTŸ][Y[›]


HOà¬à]]”ÿY[ôZX€\‘ÿÿ[ï[Y\àHù[¬àÿÿ[ê]]”ÿY[ôZX€\ 
N¬àKX]õX^
ù[Xô\ä[^JH
JN¬àBÇàù[ò›[€àÿÿ[ê]]”ÿY[ôZX€\ 
H¬àYà
\›]Kò]]”ÿY[ôZX€\»ù[ù[YKô\›õﬁYY]]”ÿY[ôZX€\“[ëõY⁄
Hô]\õàò[ŸN¬à€€ú›ÿ[ôY]\»H]]”ÿY[ôZX€\–ÿ[ôY]S[ö‹ 
N¬àYà
Xÿ[ôY]\Àõ[ô›
H¬à]]”ÿY[ôZX€\“Y[îô]ûP€›[ùH¬àYà
]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›	âà
X]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›ö\–€€õôX›YX]]”ÿY[ôZX€\—[[Y[ùö\⁄XõJ]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›
JJH¬àô\Ÿ]]]”ÿY[ôZX€\”Z\‹⁄[€ä
N¬àBàô]\õàò[ŸN¬àBà€€ú›ö\⁄XõPÿ[ôY]\»Hÿ[ôY]\Àôö[\äÿ[ôY]HOà]]”ÿY[ôZX€\—[[Y[ùö\⁄XõJÿ[ôY]Kõ[ö JN¬àYà
]ö\⁄XõPÿ[ôY]\Àõ[ô›
H¬àYà
]]”ÿY[ôZX€\“Y[îô]ûP€›[ùUU◊”–Q–S’ëRP”T◊“QSó‘ëUíQT H¬à]]”ÿY[ôZX€\“Y[îô]ûP€›[ù
œHN¬àÿ⁄Y[P]]”ÿY[ôZX€\‘ÿÿ[äUU◊”–Q–S’ëRP”T◊‘—UW”T N¬àBàô]\õàò[ŸN¬àBà]]”ÿY[ôZX€\“Y[îô]ûP€›[ùH¬à€€ú›ÿ[ôY]HHö\⁄XõPÿ[ôY]\Àôö[ô
][HOà][Kö[ôõÀõZ\‹⁄[€íYOOH]]”ÿY[ôZX€\”Z\‹⁄[€íYX]]”ÿY[ôZX€\‘ô\]Y\›YYŸ\Àö\ ][Kö[ôõÀú⁄Y€ò]\ôJJHö\⁄XõPÿ[ôY]\÷ÃN¬à€€ú›»[öÀ[ôõ»HHÿ[ôY]N¬à€€ú›Z\‹⁄[€îõ€›H]]”ÿY[ôZX€\‘ô\€€ôSZ\‹⁄[€îõ€›
[ö N¬àYà
[ôõÀõZ\‹⁄[€íYOOH]]”ÿY[ôZX€\”Z\‹⁄[€íYZ\‹⁄[€îõ€›OOH]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›
H¬àô\Ÿ]]]”ÿY[ôZX€\”Z\‹⁄[€ä
N¬à]]”ÿY[ôZX€\”Z\‹⁄[€íYH[ôõÀõZ\‹⁄[€íY¬à]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›HZ\‹⁄[€îõ€›¬àÿúŸ\ùôP]]”ÿY[ôZX€\‘õ€›
Z\‹⁄[€îõ€›
N¬àBàYà
]]”ÿY[ôZX€\‘ô\]Y\›YYŸ\Àö\ [ôõÀú⁄Y€ò]\ôJJHô]\õàò[ŸN¬àYà
]]”ÿY[ôZX€\‘ô\]Y\›€›[ùèHUU◊”–Q–S’ëRP”T◊”PV‘ëTUQT’ H¬à€€ú€€Kùÿ\õä…‘–‘íTõò[Y_WH]]À[ÿY[ôZX€\»›‹YYù\à	–UU◊”–Q–S’ëRP”T◊”PV‘ëTUQT’ﬂHô\]Y\›»õ‹àZ\‹⁄[€à	⁄[ôõÀõZ\‹⁄[€íYKò
N¬àô]\õàò[ŸN¬àBà]]”ÿY[ôZX€\‘ô\]Y\›YYŸ\ÀòY
[ôõÀú⁄Y€ò]\ôJN¬à]]”ÿY[ôZX€\‘ô\]Y\›€›[ù
œHN¬à]]”ÿY[ôZX€\“[ëõY⁄HùYN¬à]]”ÿY[ôZX€\–X›]ôS[ö»H[öŒ¬à]]”ÿY[ôZX€\–X›]ôT⁄Y€ò]\ôHH[ôõÀú⁄Y€ò]\ôN¬à[öÀô]\Ÿ]õX€\–]]”ÿYô\]Y\›YH	›ùYIŒ¬àÿúŸ\ùôP]]”ÿY[ôZX€\”[ö [ö N¬àûH¬à[öÀò€X⁄ 
N¬àHÿ]⁄
\úäH¬à]]”ÿY[ôZX€\‘ô\]Y\›YYŸ\Àô[]J[ôõÀú⁄Y€ò]\ôJN¬àô[X\ŸP]]”ÿY[ôZX€\‘ô\]Y\›
»ÿ⁄Y[Nàò[ŸHJN¬à€€ú€€Kùÿ\õä…‘–‘íTõò[Y_WH]]À[ÿY[ôZX€\»€›[õ›X›]ò]HZ\‹⁄[€ê⁄YYâ‹»ò]]ôH€€ùõ€ò\úäN¬àô]\õàò[ŸN¬àBà€X\ê]]”ÿY[ôZX€\‘ô[X\ŸU[Y\ä
N¬à]]”ÿY[ôZX€\‘ô[X\ŸU[Y\àHù[ù[YTŸ][Y[›]


HOà¬à]]”ÿY[ôZX€\‘ô[X\ŸU[Y\àHù[¬àô[X\ŸP]]”ÿY[ôZX€\‘ô\]Y\›
»ÿ⁄Y[NàùYHJN¬àKUU◊”–Q–S’ëRP”T◊’SQS’U”T N¬àô]\õàùYN¬àBÇàù[ò›[€à]]”ÿY[ôZX€\”]]][€îô[]ò[ù
]]][€äH¬àYà
]]][€ãù\HOOH	ÿ⁄[\›	 Hô]\õàò[ŸN¬à€€ú›õŸ\»HÀããê\úò^Kôúõ€J]]][€ãòYYõŸ\»◊JKããê\úò^Kôúõ€J]]][€ãúô[[›ôYõŸ\»◊JWN¬àô]\õàõŸ\Àú€€YJõŸHOà¬àYà
[õŸHõŸKõõŸU\HOOHJHô]\õàò[ŸN¬àYà
]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›	âà
õŸHOOH]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›õŸKò€€ùZ[úœÀä]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›
JJHô]\õàùYN¬àô]\õàõ€€X[äàõŸKõX]⁄\œÀäUU◊”–Q–S’ëRP”T◊‘—SP’‘äHàõŸKú]Y\ûTŸ[X›‹èÀäUU◊”–Q–S’ëRP”T◊‘—SP’‘äHàõŸKõX]⁄\œÀäUU◊”–Q–S’ëRP”T◊”RT‘“S”ó‘ì”’‘—SP’‘äHàõŸKú]Y\ûTŸ[X›‹èÀäUU◊”–Q–S’ëRP”T◊”RT‘“S”ó‘ì”’‘—SP’‘äBà
N¬àJN¬àBÇàù[ò›[€à›‹]]”ÿY[ôZX€\ 
H¬àù[ù[YP€X\ï[Y[›]
]]”ÿY[ôZX€\‘ÿÿ[ï[Y\äN¬à]]”ÿY[ôZX€\‘ÿÿ[ï[Y\àHù[¬àù[ù[YU[ùòX⁄”ÿúŸ\ùô\ä]]”ÿY[ôZX€\”ÿúŸ\ùô\äN¬à]]”ÿY[ôZX€\”ÿúŸ\ùô\àHù[¬àô\Ÿ]]]”ÿY[ôZX€\”Z\‹⁄[€ä
N¬àBÇàù[ò›[€à[ú›[]]”ÿY[ôZX€\ 
H¬àYà
\›]Kò]]”ÿY[ôZX€\»ù[ù[YKô\›õﬁYY
H¬à›‹]]”ÿY[ôZX€\ 
N¬àô]\õàò[ŸN¬àBàYà
Yÿ›[Y[ùòõŸJH¬àù[ù[YS\›[äÿ›[Y[ù	—”P€€ù[ùÿYY	À[ú›[]]”ÿY[ôZX€\À»€òŸNàùYHJN¬àô]\õàò[ŸN¬àBàYà
X]]”ÿY[ôZX€\”ÿúŸ\ùô\äH¬à€€ú›ÿúŸ\ùô\àHù[ù[YUòX⁄”ÿúŸ\ùô\äô]»]]][€ìÿúŸ\ùô\ä]]][€ú»Oà¬àYà
\›]Kò]]”ÿY[ôZX€\ Hô]\õé¬àYà
]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›	âàX]]”ÿY[ôZX€\”Z\‹⁄[€îõ€›ö\–€€õôX›Y
H¬àô\Ÿ]]]”ÿY[ôZX€\”Z\‹⁄[€ä
N¬àBàYà
]]”ÿY[ôZX€\–X›]ôS[ö»	âàX]]”ÿY[ôZX€\–X›]ôS[öÀö\–€€õôX›Y
H¬àô[X\ŸP]]”ÿY[ôZX€\‘ô\]Y\›
»ÿ⁄Y[Nàò[ŸHJN¬àBàYà
]]][€úÀú€€YJ]]”ÿY[ôZX€\”]]][€îô[]ò[ù
JHÿ⁄Y[P]]”ÿY[ôZX€\‘ÿÿ[äUU◊”–Q–S’ëRP”T◊‘—UW”T N¬àJJN¬àÿúŸ\ùô\ãõÿúŸ\ùôJÿ›[Y[ùòõŸK»⁄[\›àùYK›XùôYNàùYHJN¬à]]”ÿY[ôZX€\”ÿúŸ\ùô\àHÿúŸ\ùô\é¬àBàÿ⁄Y[P]]”ÿY[ôZX€\‘ÿÿ[ä
N¬àô]\õàùYN¬àBÇÇàù[ò›[€àù[êõ€›[ùY‹ò][€äXô[ÿ[òX⁄ H¬àûH¬àô]\õàÿ[òX⁄ 
N¬àHÿ]⁄
\úõ‹äH¬à€€⁄][ò[]X‹‘ôX€‹ô\úõ‹ä	ÿõ€›⁄[ùY‹ò][€â N¬à€€ú€€Kùÿ\õä…‘–‘íTõò[Y_WH	€Xô[HòZ[Y⁄]›]õÿ⁄⁄[ô»H€€⁄]][ò⁄\ãò\úõ‹äN¬àô]\õàù[¬àBàBÇàù[ò›[€à›\ùõ€›][\€€‹ô[ò]‹äõ€›\ôõ‹õX[òŸT›\ùY]
H¬à]][\»H¬à]€€\]HHò[ŸN¬à€€ú›ÿ⁄Y[P][\H[^HOà¬àYà
€€\]Hù[ù[YKô\›õﬁYY
Hô]\õé¬àù[ù[YTŸ][Y[›]
ù[êõ€›][\[^JN¬àN¬à€€ú›ù[êõ€›][\H

HOà¬àYà
€€\]Hù[ù[YKô\›õﬁYY
Hô]\õé¬à][\»
œHN¬à€€ú›ôXYHHõ€€X[äù[êõ€›[ùY‹ò][€ä	ÿ€‹ôHRH[›[ù	À[ú›\ôUZJJN¬à€€ú›X\ôXYHHõ€€X[äù[êõ€›[ùY‹ò][€ä	€X\\ÿ€›ô\ûIÀŸ]\ôŸ\›XYõ]X\
JN¬à€€ú›€€[X[ô⁄[õ›]Q[Y⁄XõHH€€⁄]€€[X[ô⁄[õ›]Q[Y⁄XõJÿ›[Y[ù
N¬àù[êõ€›[ùY‹ò][€ä	€Z\‹⁄[€àX\öŸ\à€⁄…À[ú›[Z\‹⁄[€ìX\öŸ\êY€⁄ N¬àù[êõ€›[ùY‹ò][€ä	‹òY[»Y\‹ÿYŸH€⁄…À[ú›[òY[”Y\‹ÿYŸR€⁄ N¬àù[êõ€›[ùY‹ò][€ä	ÿ‹ôY]»\]H€⁄…À[ú›[‹ôY]’\]R€⁄ N¬àù[êõ€›[ùY‹ò][€ä	ÿ‹ôY]»ÿúŸ\ùô\âÀÿúŸ\ùôP‹ôY]ò[YJN¬àYà
ôXYH	âà
X€€[X[ô⁄[õ›]Q[Y⁄XõHX\ôXYH][\»èHLäJH¬à€€\]HHùYN¬à€€ú›€‹ôTôXYS\»Hù[êõ€›[ùY‹ò][€ä	‹›\ù\Y]öX…À

HOàôX€‹ô›\ù\Y]öX 	ÿ€‹ôUZTôXYS\…Àõ€›\ôõ‹õX[òŸT›\ùY]»õ€›][\Œà][\»JJN¬àù[êõ€›[ùY‹ò][€ä	‹ö]òXﬁK\ÿYôH[ò[]X‹»€€ôö\õX][€âÀ

HOà€€⁄][ò[]X‹–€€ôö\õSYôXﬁX€J€‹ôTôXYS\ JN¬àù[êõ€›[ùY‹ò][€ä	€X\öŸ\à›]Hﬁ[ò…À

HOà¬àÿ⁄Y[SX\öŸ\î›]Tﬁ[ò ò[ŸJN¬àJN¬àù[êõ€›[ùY‹ò][€ä	ŸYô\úôY‹\ò][€ò[›\ù\	À

HOà¬àÿ⁄Y[QYô\úôY‹\ò][€ò[›\ù\

N¬àJN¬àù[êõ€›[ùY‹ò][€ä	›ô\ú⁄[€à›]\»⁄X⁄…À

HOà¬àÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ëTî“S”ó‘’UTÀòõ€›[^S\Àò[ŸJN¬àJN¬àù[êõ€›[ùY‹ò][€ä	€XZ[àÿúŸ\ùô\à€€õôX›[€âÀ

HOà¬àù[ù[YTŸ][Y[›]


HOàù[ù[YTù[ï⁄[íYJ€€õôX›XZ[ì]]][€ìÿúŸ\ùô\ã’TïT”–î—TïëTó—SVW”T K’TïT”–î—TïëTó—SVW”T N¬àJN¬àô]\õé¬àBàYà
][\»èHL
Hô]\õé¬à€€ú›[^HH][\»Là»ÕLà][\»Ã»ÃàM¬àÿ⁄Y[P][\
[^JN¬àN¬àù[êõ€›][\

N¬àBàù[ò›[€àôY⁄\›\êõ€›XZ[ù[ò[òŸU\⁄‹ 
H¬àù[ù[YTôY⁄\›\ï\⁄ 	›ZKZ[ùY‹ö]IÀçL

HOà»Yà
Yÿ›[Y[ùöY[äHô]\õà[ú›\ôUZJ
N»K»[ù\ùò[ô\€€ô\éà

HOàÿ›[Y[ùöY[à»ÃàçLX€€õ€^R[ù\ùò[\ŒàLX€€õ€^R[ù\ùò[ô\€€ô\éà

HOàÿ›[Y[ùöY[à»ÃàLJN¬àù[ù[YTôY⁄\›\ï\⁄ 	›ôZX€KY]K\ôYúô\⁄	ÀëRP”W–TW‘ëQîëT“”TÀ

HOà¬àYà
]ôZX€Q]SôYYY

JHô]\õé¬à[ú›[òY[”Y\‹ÿYŸR€⁄ 
N¬àô]\õàôYúô\⁄\ú€€ò[ôZX€Q]Jò[ŸJN¬àK¬àX€€õ€^R[ù\ùò[\ŒàL
àå
àLàX€€õ€^R[ù\ùò[ô\€€ô\éà

HOà‹\ò][€ò[ZR\’ö\⁄XõJ
H»à
àå
àLàL
àå
àLàJN¬àù[ù[YTôY⁄\›\ï\⁄ 	€Z\‹⁄[€ã[XZ[ù[ò[òŸIÀêSêP“◊”RT‘“S”ó‘ëQîëT“”TÀ

HOà¬àYà
Yô\ìX\[ù\òX›[€îôYúô\⁄
»[ò€YT€ò\⁄›ŒàZ\‹⁄[€î€ò\⁄›”ôYYY

HJJHô]\õé¬à[ú›[Z\‹⁄[€ìX\öŸ\êY€⁄ 
N¬à[ú›[òY[”Y\‹ÿYŸR€⁄ 
N¬à[ú›[‹ôY]’\]R€⁄ 
N¬àÿúŸ\ùôP‹ôY]ò[YJ
N¬àYà
›]Kò[X[òŸP‹ôY] Hÿ⁄Y[P[X[òŸP‹ôY]ôYúô\⁄

N¬àYà
›]Kù[ö]€€[Z]Y[ù
Hÿ⁄Y[U[ö]€€[Z]Y[ùôYúô\⁄

N¬àYà
›]Kúô\€›\òŸQÿ\ô[òXõY
Hÿ⁄Y[Tô\€›\òŸQÿ\ôYúô\⁄

N¬àYà
Z\‹⁄[€î€ò\⁄›”ôYYY

JHÿ⁄Y[SZ\‹⁄[€î€ò\⁄›ôYúô\⁄

N¬àK¬àX€€õ€^R[ù\ùò[\Œàå
àLàX€€õ€^R[ù\ùò[ô\€€ô\éà

HOàå
àLàJN¬àù[ù[YTôY⁄\›\ï\⁄ 	€Z[ù]K[XZ[ù[ò[òŸIÀå
àL

HOà¬àYà
›]KõZ\‹⁄[€êYŸJHÿ⁄Y[SZ\‹⁄[€êYŸTôYúô\⁄

N¬àYà
›]Kú›X⁄—]X›‹ãô[òXõY
Hÿ⁄Y[T›X⁄”Z\‹⁄[€îôYúô\⁄

N¬àÿ⁄Y[S‹\ò][€ò[[ô[‘ô[ô\äL
N¬àù[ôTù[ù[YPÿX⁄\ 
N¬àK¬àX€€õ€^R[ù\ùò[\ŒàH
àå
àLàX€€õ€^R[ù\ùò[ô\€€ô\éà

HOà‹\ò][€ò[ZR\’ö\⁄XõJ
H»à
àå
àLàH
àå
àLàJN¬àù[ù[YTôY⁄\›\ï\⁄ 	€XZõ‹ãZ[ò⁄Y[ùYôYYZ[ùY‹ö]IÀL

HOà¬àYà
\›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY
Hô]\õé¬àôX€›ô\ìXZõ‹í[ò⁄Y[ùôYY
	⁄[ùY‹ö]H⁄X⁄… N¬àK¬à[ù\ùò[ô\€€ô\éà

HOà›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY»Làå
àLàX€€õ€^R[ù\ùò[\ŒàLåàX€€õ€^R[ù\ùò[ô\€€ô\éà

HOà›]KõXZõ‹í[ò⁄Y[ùôYYô[òXõY»Låàà
àå
àLàJN¬àù[ù[YTôY⁄\›\ï\⁄ 	ÿùZ[[ôÀ]ö\⁄Xö[]IÀïRSSë◊’íT“PíSUW‘ëP“P“◊”TÀ

HOà¬àYà
\›]Kùö\⁄Xö[]KòùZ[[ô‹ Hﬁ[ò⁄õ€ö\ŸT\ú€€ò[ùZ[[ô’ö\⁄Xö[]J
N¬àYà
ò]]ôP[X[òŸPùZ[[ô—ö[\ìX^SôYY[ôõ‹òŸ[Y[ù

JHﬁ[ò⁄õ€ö\ŸSò]]ôP[X[òŸPùZ[[ô’ö\⁄Xö[]J
N¬àYà
›]KôX€€õ€^S[ŸJHÿ⁄Y[QX€€õ€^S^Y\îﬁ[ò 
N¬àK¬à[ù\ùò[ô\€€ô\éà

HOà\›]Kùö\⁄Xö[]KòùZ[[ô‹»»ïRSSë◊’íT“PíSUW‘ëP“P“◊”T»àå
àLàX€€õ€^R[ù\ùò[\ŒàH
àLàX€€õ€^R[ù\ùò[ô\€€ô\éà

HOà
\›]Kùö\⁄Xö[]KòùZ[[ô‹»›]KôX€€õ€^S[ŸJH»H
àLàà
àå
àLàJN¬àBÇàù[ò›[€àõ€›

H¬àYà
ù[ù[YKô\›õﬁYYõ€››\ùY
Hô]\õé¬àõ€››\ùYHùYN¬àõ€››\ùY]H]Kõõ› 
N¬à€€ú›õ€›\ôõ‹õX[òŸT›\ùY]H›\ù\€ÿ⁄ 
N¬à€€ú›[X[òŸPùZ[[ô‹”€õHH\–[X[òŸPùZ[[ô‹‘]

H	âà›]Kò[X[òŸPùZ[[ô‹”X\OOHò[ŸN¬àù[êõ€›[ùY‹ò][€ä	ÿ€€[X[ô\⁄[õ›]HYôXﬁX€IÀ[ú›[€€⁄]€€[X[ô⁄[ò]öYÿ][€í€⁄‹ N¬àYà
X[X[òŸPùZ[[ô‹”€õJH›\ùõ€›][\€€‹ô[ò]‹äõ€›\ôõ‹õX[òŸT›\ùY]
N¬àù[êõ€›[ùY‹ò][€ä	‹õ€›]öXù]\…À\Tõ€›]öXù]\ N¬àù[êõ€›[ùY‹ò][€ä	–[X[òŸHùZ[[ô‹»‹[Z\ÿ][€âÀ[ú›[[X[òŸPùZ[[ô‹‘YŸS‹[Z\ÿ][€äN¬àYà
[X[òŸPùZ[[ô‹”€õJHô]\õé¬àù[êõ€›[ùY‹ò][€ä	ÿ€X[ã[[ŸH^]	À‹ôX]P€X[ë^]
N¬àYà
›]Kò]]”ÿY[ôZX€\ Hù[êõ€›[ùY‹ò][€ä	ÿ]]À[ÿY[ôZX€\…À[ú›[]]”ÿY[ôZX€\ N¬àù[êõ€›[ùY‹ò][€ä	€Z\‹⁄[€àX\öŸ\à€⁄…À[ú›[Z\‹⁄[€ìX\öŸ\êY€⁄ N¬àù[êõ€›[ùY‹ò][€ä	‹òY[»Y\‹ÿYŸH€⁄…À[ú›[òY[”Y\‹ÿYŸR€⁄ N¬à\›ÿúŸ\ùôY‹ôY]»Hù[êõ€›[ùY‹ò][€ä	⁄[ö]X[‹ôY]›[	ÀôXY›\úô[ù‹ôY]›[
N¬àù[êõ€›[ùY‹ò][€ä	ÿ‹ôY]»\]H€⁄…À[ú›[‹ôY]’\]R€⁄ N¬àù[êõ€›[ùY‹ò][€ä	ÿ‹ôY]»ÿúŸ\ùô\âÀÿúŸ\ùôP‹ôY]ò[YJN¬àù[êõ€›[ùY‹ò][€ä	ÿ›\›€HôZX€HòYŸ\…À[ú›[›\›€UôZX€PòYŸ\ N¬à€€ú›ÿúŸ\ùô\àHù[ù[YUòX⁄”ÿúŸ\ùô\äô]»]]][€ìÿúŸ\ùô\ä]]][€ú»Oà¬àYà
X\[ù\òX›[€ï€‹ö—Yô\úôY

JH¬àYà
[]]][€úÀô]ô\ûJ]]][€í\”XYõ][Sõ⁄\ŸJJHYô\ìX\[ù\òX›[€îôYúô\⁄
»[ò€YT€ò\⁄›ŒàùYK€S]]][€éàùYHJN¬àô]\õé¬àBà]^\õò[]]][€ëõ›[ôHò[ŸN¬à]YYXYõ]X\öŸ\àHò[ŸN¬à]Z\‹⁄[€ê⁄[ôŸYHò[ŸN¬à]^[›]⁄[ôŸYHò[ŸN¬à]€€⁄]ZTô[[›ôYHò[ŸN¬àõ‹à
€€ú›]]][€àŸà]]][€ú H¬àYà
]]][€í\”XYõ][Sõ⁄\ŸJ]]][€äJH€€ù[ùYN¬à€€ú›ô[[›ô\’€€⁄]ZHH]]][€îô[[›ô\’€€⁄]ZJ]]][€äN¬àYà
ô[[›ô\’€€⁄]ZJH€€⁄]ZTô[[›ôYHùYN¬àYà
]]][€êô[€ô‹’’€€⁄]
]]][€äH	âà\ô[[›ô\’€€⁄]ZJH€€ù[ùYN¬à^\õò[]]][€ëõ›[ôHùYN¬àYà
XYYXYõ]X\öŸ\à	âà]]][€êY”XYõ]X\öŸ\íX€€ä]]][€äJH¬àYYXYõ]X\öŸ\àHùYN¬àZ\‹⁄[€ê⁄[ôŸYHùYN¬àBàYà
[Z\‹⁄[€ê⁄[ôŸY	âà]]][€êYôôX›”Z\‹⁄[€ë]J]]][€äJHZ\‹⁄[€ê⁄[ôŸYHùYN¬àYà
[^[›]⁄[ôŸY	âà]]][€êYôôX›”X\^[›]
]]][€äJH^[›]⁄[ôŸYHùYN¬àYà
]€€⁄]ZTô[[›ôY	âà]]][€îô[[›ô\’€€⁄]ZJ]]][€äJH€€⁄]ZTô[[›ôYHùYN¬àYà
YYXYõ]X\öŸ\à	âàZ\‹⁄[€ê⁄[ôŸY	âà^[›]⁄[ôŸY	âà€€⁄]ZTô[[›ôY
HúôXZŒ¬àBàYà
Y^\õò[]]][€ëõ›[ô
Hô]\õé¬àZ\‹⁄[€ê⁄[ôŸYHYYXYõ]X\öŸ\é¬àYà
[Z\‹⁄[€ê⁄[ôŸY	âà[^[›]⁄[ôŸY	âà]€€⁄]ZTô[[›ôY
Hô]\õé¬àYà
YYXYõ]X\öŸ\äH¬à[ùò[Y]SX\öŸ\îôY⁄\›ûPÿX⁄\ 	ÿ[	 N¬àÿ⁄Y[SX\öŸ\î›]Tﬁ[ò ò[ŸJN¬àYà
\›]Kùö\⁄Xö[]KòùZ[[ô‹»ò]]ôP[X[òŸPùZ[[ô—ö[\ìX^SôYY[ôõ‹òŸ[Y[ù

JHÿ⁄Y[SX\öŸ\î›]Tﬁ[ò NùYJN¬àBàYà
^[›]⁄[ôŸY
H[ùò[Y]SX\[[Y[ùÿX⁄J
N¬àYà
ÿ›[Y[ùöY[àòY‘›]HX\[ù\òX›[€ï€‹ö—Yô\úôY

JHô]\õé¬àù[ù[YP€X\ï[Y[›]
]]][€ï[Y\äN¬à€€ú››\ù\Ÿ][ô»Hõ€››\ùY]à	âà]Kõõ› 
HHõ€››\ùY]’TïT‘—UW’“Së’◊”TŒ¬à€€ú›]]][€ë[^HH›\ù\Ÿ][ô¬à»’TïT”UUUS”ó—Pì’Sê—W”T¬àà
›]KôX€€õ€^S[ŸH»X]õX^
Ãå”W‘ëQîëT“—Pì’Sê—W”T Hà”W‘ëQîëT“—Pì’Sê—W”T N¬à]]][€ï[Y\àHù[ù[YTŸ][Y[›]


HOà¬àYà
òY‘›]Hÿ›[Y[ùöY[àù[ù[YKô\›õﬁYYX\[ù\òX›[€ï€‹ö—Yô\úôY

JHô]\õé¬à€€ú›[ô[Z\‹⁄[ô»HŸ][ô‹‘[ô[X›]ò]Y	âàYÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬à€€ú›X\[[Y[ùHŸ]\ôŸ\›XYõ]X\

N¬à€€ú›€€ùõ€Z\‹⁄[ô»Hõ€€X[äX\[[Y[ù	âàYÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
JN¬àYà
€€⁄]ZTô[[›ôY[ô[Z\‹⁄[ô»€€ùõ€Z\‹⁄[ô H[ú›\ôUZJ
N¬àYà
XZ[ì]]][€ìÿúŸ\ùô\ëò[òX⁄–X›]ôH	âà
X\[[Y[ùÿ›[Y[ùú]Y\ûTŸ[X›‹ä	»€Z\‹⁄[€úÀ€Z\‹⁄[€ó€\›õZ\‹⁄[€úÀ\[ô[õZ\‹⁄[€ã[\›	 JJH¬à€€õôX›XZ[ì]]][€ìÿúŸ\ùô\ä
N¬àBàYà
^[›]⁄[ôŸY
H¬àôYúô\⁄›\ô\‹⁄[€ä
N¬àö]€€ùõ€”X\

N¬àÿ⁄Y[T[ô[‹⁄][€äùYKL
N¬àBàYà
Z\‹⁄[€ê⁄[ôŸY
H¬àÿ⁄Y[Q[òXõYX\ôYúô\⁄\ »[ò€YT€ò\⁄›ŒàZ\‹⁄[€î€ò\⁄›”ôYYY

K‹⁄][€î[ô[àò[ŸHJN¬àBàK]]][€ë[^JN¬àJJN¬àXZ[ì]]][€ìÿúŸ\ùô\àHÿúŸ\ùô\é¬àù[ù[YS\›[äÿ›[Y[ù	⁄Ÿ^Y›€âÀ[ôRŸ^Xõÿ\ô
N¬àù[ù[YS\›[äÿ›[Y[ù	ÿ€€ù^Y[ùIÀ[ôP€€ù^€€[X[ôô\]Y\›ùYJN¬àù[ù[YS\›[äÿ›[Y[ù	‹⁄[ù\ô›€âÀ

HOà»[õÿ⁄‘^[›]]Y[ 
N»Yà
›]Kõõ›YöXÿ][€úÀô[òXõY
H[õÿ⁄”õ›YöXÿ][€ê]Y[ 
N»K»€òŸNàùYKÿ\\ôNàùYHJN¬àù[ù[YS\›[äÿ›[Y[ù	ÿ€X⁄…À]ô[ùOà¬àYà
[ôP€€[X[ô^\öY[òŸPX›[€ä]ô[ù
JHô]\õé¬à€€ú›€€ù^Y[ùHH€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTò€€ù^Y[ùRY
N¬àYà
€€ù^Y[ùH	âàX€€ù^Y[ùKò€€ùZ[ú ]ô[ùù\ôŸ]
JH€‹ŸP€€ù^€€[X[ôY[ùJ
N¬àù[ù[YTŸ][Y[›]
ôYúô\⁄›\ô\‹⁄[€ã
N¬àYà
›\ô\‹”ô^›]⁄YP€X⁄ H¬à]ô[ùúô]ô[ùYò][

N¬à]ô[ùú›‹õ‹Yÿ][€ä
N¬à›\ô\‹”ô^›]⁄YP€X⁄»Hò[ŸN¬àô]\õé¬àBà€€ú›€€ùõ€Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTò€€ùõ€Y
N¬à€€ú›[ô[Hÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú[ô[Y
N¬àYà
\[ô[\[ô[ò€\‹”\›ò€€ùZ[ú 	€X€\À[‹[â JHô]\õé¬àYà
€€ùõ€	âà€€ùõ€ò€€ùZ[ú ]ô[ùù\ôŸ]
JHô]\õé¬àYà
[ô[ò€€ùZ[ú ]ô[ùù\ôŸ]
JHô]\õé¬à€‹ŸT[ô[

N¬àKùYJN¬àù[ù[YS\›[äYŸU⁄[ô›À	‹ô\⁄^ôIÀ

HOà¬à[ùò[Y]SX\[[Y[ùÿX⁄J
N¬à\Tõ€›]öXù]\ 
N¬àôYúô\⁄Xõ][ŸUZJ
N¬àÿ⁄Y[Uö\›X[öY]‹‹ù›Xö[\ÿ][€ä	›⁄[ô›À\ô\⁄^ôI N¬à€€ú›^[›]›ô\õ^HHÿ›[Y[ùôŸ][[Y[ùûRY
–‘íTú^[›]õ\⁄Y
N¬àYà
^[›]›ô\õ^OÀò€\‹”\›ò€€ùZ[ú 	€X€\À\^[›]XX›]ôI JH‹⁄][€î^[›]õ\⁄›ô\õ^J^[›]›ô\õ^JN¬àYà
òY‘›]JHô]\õé¬àôYúô\⁄›\ô\‹⁄[€ä
N¬àö]€€ùõ€”X\

N¬àÿ⁄Y[T[ô[‹⁄][€äùYK
N¬àÿ⁄Y[Q[òXõYX\ôYúô\⁄\ »[ò€YT€ò\⁄›Œàò[ŸK‹⁄][€î[ô[àò[ŸKX\€õNàùYHJN¬àÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYY^[›]

N¬àJN¬àù[ù[YS\›[äYŸU⁄[ô›À	‹ÿ‹õ€	Àÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYY^[›]»\‹⁄]ôNàùYHJN¬àù[ù[YS\›[äYŸU⁄[ô›À	€‹öY[ù][€ò⁄[ôŸIÀ

OOúÿ⁄Y[Uö\›X[öY]‹‹ù›Xö[\ÿ][€ä	€‹öY[ù][€ò⁄[ôŸI JN¬àYäYŸU⁄[ô›Àùö\›X[öY]‹‹ù
^¬àù[ù[YS\›[äYŸU⁄[ô›Àùö\›X[öY]‹‹ù	‹ô\⁄^ôIÀ

OOúÿ⁄Y[Uö\›X[öY]‹‹ù›Xö[\ÿ][€ä	›ö\›X[]öY]‹‹ù\ô\⁄^ôI JN¬àù[ù[YS\›[äYŸU⁄[ô›Àùö\›X[öY]‹‹ù	‹ÿ‹õ€	À

OOû⁄Yä\’›X⁄^[›]X›]ôJ
J\ÿ⁄Y[Uö\›X[öY]‹‹ù›Xö[\ÿ][€ä	›ö\›X[]öY]‹‹ù\ÿ‹õ€	 NﬂK‹\‹⁄]ôNùùY_JN¬àBà\Uö\›X[öY]‹‹ùŸ[€Y]ûJ
N¬àÿ⁄Y[Uö\›X[öY]‹‹ù›Xö[\ÿ][€ä	ÿõ€›]öY]‹‹ù	 N¬àûH¬à€€ú›€ÿ\úŸT⁄[ù\î]Y\ûHHYŸU⁄[ô›ÀõX]⁄YYXOÀä	 [ûK\⁄[ù\éà€ÿ\úŸJI N¬àYà
€ÿ\úŸT⁄[ù\î]Y\ûOÀòY]ô[ù\›[ô\äHù[ù[YS\›[ä€ÿ\úŸT⁄[ù\î]Y\ûK	ÿ⁄[ôŸIÀ

HOàÿ⁄Y[UXõ]^[›]ôYúô\⁄
å
JN¬àHÿ]⁄
\úäHﬂBàù[ù[YS\›[äYŸU⁄[ô›À	Ÿõÿ›\…À

HOà¬àÿ⁄Y[Uö\›X[öY]‹‹ù›Xö[\ÿ][€ä	›⁄[ô›ÀYõÿ›\… N»Yà
òY‘›]JHô]\õé¬àôYúô\⁄›\ô\‹⁄[€ä
N¬àö]€€ùõ€”X\

N¬àÿ⁄Y[T[ô[‹⁄][€äùYK
N¬à[ú›[òY[”Y\‹ÿYŸR€⁄ 
N¬àYà
ôZX€Q]SôYYY

JHôYúô\⁄\ú€€ò[ôZX€Q]Jò[ŸJN¬àYà
›]KôX€€õ€^S[ŸJHÿ⁄Y[QX€€õ€^S^Y\îﬁ[ò 
N¬àÿ⁄Y[Q[òXõYX\ôYúô\⁄\ »[ò€YT€ò\⁄›ŒàZ\‹⁄[€î€ò\⁄›”ôYYY

K‹⁄][€î[ô[àò[ŸHJN¬àÿ⁄Y[S‹\ò][€ò[[ô[‘ô[ô\äL
N¬àÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\ä
N¬àJN¬à€€ú›ôX€›ô\ïZPYù\ìò]öYÿ][€àH]ô[ùOà¬àù[ù[YTŸ][Y[›]


HOà¬àYà
ù[ù[YKô\›õﬁYYÿ›[Y[ùöY[äHô]\õé¬àôX€€ò⁄[U€€⁄]€€[X[ô⁄[õ›]J]ô[ùÀù\H	€ò]öYÿ][€â N¬à€€õôX›XZ[ì]]][€ìÿúŸ\ùô\ä
N¬àôX€›ô\ìXZõ‹í[ò⁄Y[ùôYY
]ô[ùÀù\H	€ò]öYÿ][€â N¬àKLå
N¬àù[ù[YTŸ][Y[›]


HOà¬àYà
ù[ù[YKô\›õﬁYYÿ›[Y[ùöY[äHô]\õé¬àôX€›ô\ìXZõ‹í[ò⁄Y[ùôYY
	Ÿ]ô[ùÀù\H	€ò]öYÿ][€âﬂHŸ]X
N¬àKçL
N¬àN¬àù[ù[YS\›[äYŸU⁄[ô›À	‹YŸ\⁄›…ÀôX€›ô\ïZPYù\ìò]öYÿ][€äN¬àù[ù[YS\›[äYŸU⁄[ô›À	‹‹›]IÀôX€›ô\ïZPYù\ìò]öYÿ][€äN¬àù[ù[YS\›[äYŸU⁄[ô›À	⁄\⁄⁄[ôŸIÀôX€›ô\ïZPYù\ìò]öYÿ][€äN¬àôY⁄\›\êõ€›XZ[ù[ò[òŸU\⁄‹ 
N¬àù[ù[YS\›[äÿ›[Y[ù	›ö\⁄Xö[]X⁄[ôŸIÀ

HOà¬àYà
ÿ›[Y[ùöY[äHô]\õé¬àù[ù[YUÿZŸU\⁄‘ÿ⁄Y[\ä
N¬à[ú›\ôUZJ
N¬àÿ⁄Y[Uô\ú⁄[€î›]\–⁄X⁄ ò[ŸJN¬àôYúô\⁄›\ô\‹⁄[€ä
N¬àYà
ôZX€Q]SôYYY

JHôYúô\⁄\ú€€ò[ôZX€Q]Jò[ŸJN¬àYà
›]KôX€€õ€^S[ŸJHÿ⁄Y[QX€€õ€^S^Y\îﬁ[ò 
N¬àYà
ò]]ôP[X[òŸPùZ[[ô—ö[\ìX^SôYY[ôõ‹òŸ[Y[ù

JHﬁ[ò⁄õ€ö\ŸSò]]ôP[X[òŸPùZ[[ô’ö\⁄Xö[]J
N¬àÿ⁄Y[Q[òXõYX\ôYúô\⁄\ »[ò€YT€ò\⁄›ŒàZ\‹⁄[€î€ò\⁄›”ôYYY

K‹⁄][€î[ô[àùYHJN¬àÿ⁄Y[SXZõ‹í[ò⁄Y[ùôYYô[ô\ä
N¬àJN¬àù[ù[YTŸ][Y[›]


HOà¬àYà
ÿ›[Y[ùöY[à[‹\ò][€ò[›\ù\€€\]JHô]\õé¬àÿ⁄Y[Q[òXõYX\ôYúô\⁄\ »[ò€YT€ò\⁄›Œàò[ŸK‹⁄][€î[ô[àò[ŸKX\€õNàùYHJN¬àKåå
N¬àù[ù[YS€ê€X[ù\


HOà¬à›‹]]”ÿY[ôZX€\ 
N¬àò[ú‹‹ù›ŸY\ù[ù[YKú›‹ô\]Y\›YHùYN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	€[›\Ÿ[[›ôIÀ[›ôT[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	€[›\Ÿ]\	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	››X⁄[›ôIÀ[›ôT[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	››X⁄[ô	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùúô[[›ôQ]ô[ù\›[ô\ä	››X⁄ÿ[òŸ[	À[ô[ô[òYÀùYJN¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùú›[Kò›\ú€‹àH	…Œ¬àYà
ÿ›[Y[ùòõŸJHÿ›[Y[ùòõŸKú›[Kù\Ÿ\îŸ[X›H	…Œ¬àX\[ù\òX›[€ì[›ö[ô»Hò[ŸN¬àX\[ù\òX›[€îŸ][ô»Hò[ŸN¬àX\[ù\òX›[€ëYô\úôYôYúô\⁄Hò[ŸN¬àX\[ù\òX›[€ëYô\úôY€ò\⁄›»Hò[ŸN¬àX\[ù\òX›[€ëYô\úôY€S]]][€àHò[ŸN¬àX\[ù\òX›[€ìX\öŸ\îﬁ[ò”ôYYYHò[ŸN¬àX\[ù\òX›[€ë\ùTÿ€‹\Àò€X\ä
N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùÀúŸ]]öXù]OÀä	Ÿ]K[X€\À[X\[[›ö[ô…À	Ÿò[ŸI N¬àô\›‹ôQX€€õ€^S^Y\ú 
N¬àô\›‹ôSXYõ]X€€õ€^T€XﬁJ
N¬àô[X\ŸSò]]ôP[X[òŸPùZ[[ô’ö\⁄Xö[]JÿX⁄YX\
N¬à\‹‹ŸP€›ô\òYŸPÿ[ùò\‘ô[ô\ô\ä
N¬àù[ù[YP€X\ï[Y[›]
XZõ‹í[ò⁄Y[ùôYY^[›][Y\äN¬àXZõ‹í[ò⁄Y[ùôYY^[›][Y\àHù[¬à€€ú›‹öY⁄[ò[ùZ[[ô’ö\⁄Xö[]HH›]Kùö\⁄Xö[]KòùZ[[ô‹Œ¬àûH¬à›]Kùö\⁄Xö[]KòùZ[[ô‹»HùYN¬àﬁ[ò⁄õ€ö\ŸT\ú€€ò[ùZ[[ô’ö\⁄Xö[]JÿX⁄YX\
N¬àHÿ]⁄
\úäH¬à€€ú€€KôXùY …‘–‘íTõò[Y_WHùZ[[ô»ö\⁄Xö[]Hô\›‹ò][€à⁄⁄\Y\ö[ô»X\ô›€ãò\úäN¬àHö[ò[H¬à›]Kùö\⁄Xö[]KòùZ[[ô‹»H‹öY⁄[ò[ùZ[[ô’ö\⁄Xö[]N¬àBàûH»‹ôY]’ò[YSÿúŸ\ùô\èÀô\ÿ€€õôX›

N»Hÿ]⁄
\úäHﬂBàô[[›ôSXZõ‹í[ò⁄Y[ùôYY

N¬à€X\ìZ\‹⁄[€ìÿ⁄”€ëYôôX›

N¬à›‹ôZX€Qõ€› ò[ŸJN¬à€X\ê[X[òŸP‹ôY]Xô[ 
N¬à€X\ìZ\‹⁄[€êYŸSXô[ 
N¬à€X\ï[ö]€€[Z]Y[ùXô[ 
N¬à€X\ïò[ú‹‹ùÿ]⁄\ìXô[ 
N¬à€X\îô\€›\òŸQÿ\Xô[ 
N¬à€X\î›X⁄”Z\‹⁄[€ìXô[ 
N¬àYà
€›ô\òYŸQ‹õ›\
H¬àûH»€›ô\òYŸQ‹õ›\ò€X\ì^Y\ú 
N»€›ô\òYŸQ‹õ›\úô[[›ôJ
N»Hÿ]⁄
\úäHﬂBà€›ô\òYŸQ‹õ›\Hù[¬àBà›‹^[›]õ\⁄[ö[X][€ä
N¬à\‹‹ŸT^[›]YYXP]Y[ 
N¬àûH»^[›]]Y[–€€ù^Àò€‹ŸOÀä
N»Hÿ]⁄
\úäHﬂBàûH»õ›YöXÿ][€ê]Y[–€€ù^Àò€‹ŸOÀä
N»Hÿ]⁄
\úäHﬂBàõ›YöXÿ][€ê]Y[–€€ù^Hù[¬àõ›YöXÿ][€ë]ô[ùŸY[ãò€X\ä
N¬àõ›YöXÿ][€êX›]ôQ]ô[ùÀò€X\ä
N¬à€X\ë\ÿ€‹ôô]öY]–⁄\ù\õ

N¬à€‹ŸUXõ]]ZX⁄’⁄Y[

N¬à€‹ŸP€€ù^€€[X[ôY[ùJ
N¬à€‹ŸP€€[X[ô[]J»ô\›‹ôQõÿ›\Œàò[ŸHJN¬à€‹ŸP€€[X[ô^\öY[òŸS[Ÿ[
»ô\›‹ôQõÿ›\Œàò[ŸHJN¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú\ú€€ò[\ÿ][€î›[RYX
OÀúô[[›ôJ
N¬àù[ÿ‹ôY[ìX\\ôŸ]Àò€\‹”\›Àúô[[›ôJ	€X€\À[X\Yù[ÿ‹ôY[ã]\ôŸ]	 N¬àù[ÿ‹ôY[ìX\\ôŸ]Hù[¬à€€[X[ô^\öY[òŸQ[[Y[ù
–‘íTôù[ÿ‹ôY[ë^]Y
OÀúô[[›ôJ
N¬à€‹ŸR[Ÿ[ù\ä»ô\›‹ôQõÿ›\Œàò[ŸHJN¬à\‹‹ŸUô\ú⁄[€î›]\ 
N¬à[›ZYQÿ›[Y[ùÿX⁄HH	…Œ¬à[›ZYSÿYY]H¬à›‹\⁄›‹[ô[€‹ö‹‹XŸSÿúŸ\ùò][€ä
N¬àù[ù[YU[ùòX⁄”ÿúŸ\ùô\ä\⁄›‹[ô[ô\⁄^ôSÿúŸ\ùô\äN¬à\⁄›‹[ô[ô\⁄^ôSÿúŸ\ùô\àHù[¬àù[ù[YU[ùòX⁄”ÿúŸ\ùô\äXZõ‹í[ò⁄Y[ùôYYô\⁄^ôSÿúŸ\ùô\äN¬àXZõ‹í[ò⁄Y[ùôYYô\⁄^ôSÿúŸ\ùô\àHù[¬àXZõ‹í[ò⁄Y[ùôYYÿúŸ\ùôY[[Y[ùHù[¬àZ\‹⁄[€î€ò\⁄›ÿX⁄Kò€X\ä
N¬àZ\‹⁄[€î[ô[ÿX⁄Kò€X\ä
N¬àZ\‹⁄[€ì›ô\õ^Uô\ú⁄[€úÀò€X\ä
N¬àX\öŸ\îôY⁄\›ûPÿX⁄Kò€X\ä
N¬àô[[›ôS€[ú›[òŸ\ 
N¬à€€ú›õ€›Hÿ›[Y[ùôÿ›[Y[ù[[Y[ù¬àõ‹à
€€ú›]öXù]HŸà…Ÿ]K[X€\À]ZK][YIÀ	Ÿ]K[X€\ÀX›\›€K][YIÀ	Ÿ]K[X€\À[Z\‹⁄[€ò⁄YYã\ô\⁄⁄[âÀ	Ÿ]K[X€\ÀYÿ⁄ÀX]]ÀZYIÀ	Ÿ]K[X€\ÀX]]ÀZYKX^\…À	Ÿ]K[X€\ÀX]]ÀZYK\ô]ôX[Y	À	Ÿ]K[X€\À\ÿYôK[[ŸIÀ	Ÿ]K[X€\À\[ô[[‹[âÀ	Ÿ]K[XÀ[X\\⁄⁄[âÀ	Ÿ]K[X€\ÀX€X[âÀ	Ÿ]K[X€\À[X\öŸ\ãYõÿ›\…À	Ÿ]K[X€\À[Z\‹⁄[€ã\[ŸIÀ	Ÿ]K[X€\À\õÿY\ö[‹ö]IÀ	Ÿ]K[X€\ÀX€€\X›Yÿ⁄…À	Ÿ]K[X€\ÀX€€[X[ôXò\ã[‹[âÀ	Ÿ]K[X€\ÀYX€€õ€^IÀ	Ÿ]K[X€\À[X\Yù[ÿ‹ôY[âÀ	Ÿ]K[X€\ÀY[ú⁄]IÀ	Ÿ]K[X€\À[X\[[›ö[ô…À	Ÿ]K[X€\ÀX[X[òŸKXùZ[[ô‹À[X\	À	Ÿ]K[X€\ÀX[X[òŸKXùZ[[ô‹À\YŸIÀ	Ÿ]K[X€\ÀY]öXŸK[^[›]	À	Ÿ]K[X€\À]Xõ][[ŸIÀ	Ÿ]K[X€\À]Xõ]XX›]ôIÀ	Ÿ]K[X€\À]Xõ][‹öY[ù][€âÀ	Ÿ]K[X€\À[[ÿö[K[[ŸIÀ	Ÿ]K[X€\À[[ÿö[KXX›]ôIÀ	Ÿ]K[X€\À[[ÿö[K[‹öY[ù][€âÀ	Ÿ]K[X€\À\⁄›ÀX[X[òŸK[Z\‹⁄[€ú…À	Ÿ]K[X€\À\⁄›À[^K[Z\‹⁄[€ú…À	Ÿ]K[X€\À\⁄›À]ôZX€\…À	Ÿ]K[X€\À\⁄›ÀXùZ[[ô‹…À	Ÿ]K[X€\ÀZ[[‹[âÀ	Ÿ]K[X€\ÀX€€[X[ô\[]K[‹[âÀ	Ÿ]K[X€\ÀX€€[X[ôY^\öY[òŸK[‹[â◊JHõ€›úô[[›ôP]öXù]J]öXù]JN¬àJN¬àYà
›]KôX€€õ€^S[ŸJHù[ù[YTŸ][Y[›]


HOàŸ]X€€õ€^S[ŸJùYKò[ŸJKå
N¬à€€ú€€KôXùY …‘–‘íTõò[Y_WHâ‘–‘íTùô\ú⁄[€üH]Y]Yù[ù[YHôXYKò
N¬àBÇàù[ò›[€àÿ⁄Y[Põ€›

H¬àYà
ù[ù[YKô\›õﬁYYõ€››\ùY
Hô]\õé¬àù[êõ€›[ùY‹ò][€ä	⁄YHõ€›ÿ⁄Y[[ô…À

HOàù[ù[YTù[ï⁄[íYJõ€›’TïT“QW’SQS’U”T JN¬àù[ù[YTŸ][Y[›]


HOà¬àYà
\ù[ù[YKô\›õﬁYY	âàXõ€››\ùY
Hõ€›

N¬àKX]õZ[äLå’TïT“QW’SQS’U”T JN¬àBÇàYà
ÿ›[Y[ùúôXYT›]HOOH	€ÿY[ô… H¬àù[ù[YS\›[äÿ›[Y[ù	—”P€€ù[ùÿYY	Àÿ⁄Y[Põ€›»€òŸNàùYHJN¬àH[ŸH¬àÿ⁄Y[Põ€›

N¬àBÇàÀ»X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\èÇàÀ»€€⁄]éåKåàò]]ôK‹Z[à[X[òŸHY[Xô\àX[òYŸ\ãÇà€€ú›SPSê—W”QSPëTó”PSêQ—TàHÿöôX›ôúôY^ôJ¬à›‹òYŸRŸ^Nà	€X€\◊ÿ[X[òŸW€Y[Xô\ó€X[òYŸ\óŸ[òXõY›åIÀà[ô[Yà	€X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\âÀà›[RYà	€X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\ã\›[IÀàY[ùP]öXù]Nà	Ÿ]K[X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\ã]ŸŸ€IÀà‹\ò][€ú–]öXù]Nà	Ÿ]K[X€\ÀX[X[òŸK[‹\ò][€ú…Ààõ‘õ€Nà	◊◊€X€\◊€õ◊‹õ€W◊…ÀàJN¬à][X[òŸSY[Xô\ìX[òYŸ\îYŸHHù[¬à][X[òŸSY[Xô\ìX[òYŸ\ì[›[ùÿúŸ\ùô\àHù[¬à][X[òŸSY[Xô\ìX[òYŸ\ì[›[ùõ€›Hù[¬à][X[òŸSY[Xô\ìX[òYŸ\îôX€€ò⁄[T]Y]YYHò[ŸN¬à][X[òŸSY[Xô\ìX[òYŸ\ì\›[›[ù›]HH	⁄YIŒ¬Çàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ë[òXõY

H¬àûH¬àYà
\[Ÿà”WŸŸ]ò[YHOOH	Ÿù[ò›[€â H¬à€€ú›ò[YHH”WŸŸ]ò[YJSPSê—W”QSPëTó”PSêQ—Tãú›‹òYŸRŸ^Kù[
N¬àYà
\[Ÿàò[YHOOH	ÿõ€€X[â Hô]\õàò[YN¬àBàHÿ]⁄
\úõ‹äHﬂBàûH¬àô]\õàÿÿ[›‹òYŸKôŸ]][JSPSê—W”QSPëTó”PSêQ—Tãú›‹òYŸRŸ^JHOOH	›ùYIŒ¬àHÿ]⁄
\úõ‹äH¬àô]\õàò[ŸN¬àBàBÇàù[ò›[€àŸ][X[òŸSY[Xô\ìX[òYŸ\ë[òXõY
[òXõY
H¬à€€ú›ô^Hõ€€X[ä[òXõY
N¬àûH¬àYà
\[Ÿà”W‹Ÿ]ò[YHOOH	Ÿù[ò›[€â H”W‹Ÿ]ò[YJSPSê—W”QSPëTó”PSêQ—Tãú›‹òYŸRŸ^Kô^
N¬àHÿ]⁄
\úõ‹äHﬂBàûH¬àÿÿ[›‹òYŸKúŸ]][JSPSê—W”QSPëTó”PSêQ—Tãú›‹òYŸRŸ^Kô^»	›ùYI»à	Ÿò[ŸI N¬àHÿ]⁄
\úõ‹äHﬂBà\]P[X[òŸSY[Xô\ìX[òYŸ\ìY[ùP€€ùõ€

N¬àôX€€ò⁄[P[X[òŸSY[Xô\ìX[òYŸ\ä	‹Ÿ][ôÀX⁄[ôŸI N¬àBÇàù[ò›[€à\–[X[òŸSY[Xô\ìX[òYŸ\îõ›]J]ò[YHHÿÿ][€ãú]ò[YJH¬à€€ú›]HX€ŸY]ò[YJ]ò[YJN¬àô]\õà◊›ô\òò[ô€Z]€YY\äŒó◊
 O◊œ…⁄]Kù\›
]
Bà◊ÿ[X[òŸ\œ◊ Œó
◊ O€Y[Xô\ú Œó◊
 O◊œ…⁄]Kù\›
]
Bà◊ÿ[X[òŸW€Y[Xô\ú Œó◊
 O◊œ…⁄]Kù\›
]
N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ì›\ì›€ô\îô\Ÿ[ù

H¬à€€ú›ÿ[ôY]\»Hÿ›[Y[ùú]Y\ûTŸ[X›‹ê[
à	»ÿ[X[òŸSY[Xô\ì\›X€€ùõ€À⁄Y
èHò[X[òŸSY[Xô\ì\›óV⁄Y	HãX€€ùõ€»óK	»
¬à	÷Ÿ]KX[X[òŸK[Y[Xô\ã[X[òYŸ\óKŸ]KY^\õò[X[X[òŸK[Y[Xô\ã[X[òYŸ\óI¬à
N¬àô]\õà\úò^Kôúõ€Jÿ[ôY]\ Kú€€YJÿ[ôY]HOà¬àYà
ÿ[ôY]Kò€‹Ÿ\›Àä…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YX
JHô]\õàò[ŸN¬à€€ú›^H›ö[ô ÿ[ôY]Kù^€€ù[ù	… Kúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
N¬à€€ú›\‘õ€HH◊úõ€JŒú O◊ã⁄]Kù\›
^
Bàõ€€X[äÿ[ôY]Kú]Y\ûTŸ[X›‹èÀä	÷€ò[YJèHúõ€HàWKŸ]KYö[\äèHúõ€HàWI JN¬à€€ú›\–X›]ö]HH◊òX›]ö]Wüõ€õ[ôWãäóõŸôõ[ôWã⁄]Kù\›
^
Bàõ€€X[äÿ[ôY]Kú]Y\ûTŸ[X›‹èÀä	÷€ò[YJèHòX›]ö]HàWKŸ]KYö[\äèHòX›]ö]HàWI JN¬à€€ú›\”ÿY[H◊õÿY[Y[Xô\àYŸ\◊ã⁄]Kù\›
^
Bàõ€€X[äÿ[ôY]Kú]Y\ûTŸ[X›‹èÀä	÷Ÿ]KXX›[€äèHõÿYX[àWI JN¬àô]\õà\‘õ€H	âà\–X›]ö]H	âà\”ÿY[¬àJN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ïXõJÿ»Hÿ›[Y[ù
H¬àô]\õà\úò^Kôúõ€JÿÀú]Y\ûTŸ[X›‹ê[
	›XõI JKôö[ô
XõHOà¬à€€ú›õŸö[S[ö‹»HXõKú]Y\ûTŸ[X›‹ê[
à	›õŸHV⁄ôYóèHã‹õŸö[K»óKõŸHV⁄ôYäèHã‹õŸö[K»óI¬à
N¬àYà
\õŸö[S[ö‹Àõ[ô›
Hô]\õàò[ŸN¬à€€ú›XY\ú»H\úò^Kôúõ€JXõKú]Y\ûTŸ[X›‹ê[
	›XY	 JBàõX\
XY\àOà›ö[ô XY\ãù^€€ù[ù	… Kúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
Kù”›Ÿ\êÿ\ŸJ
JN¬àô]\õàZXY\úÀõ[ô›àXY\úÀú€€YJXY\àOà◊äŒú^Y\üY[Xô\üò[YJI⁄]Kù\›
XY\äJBàõŸö[S[ö‹Àõ[ô›èHé¬àJHù[¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\êõŸJXõJH¬àô]\õàXõH»\úò^Kôúõ€JXõKùõŸY\ Kò]
LJHù[àù[¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ê›\úô[ùYŸJ\õHô]»Tì
ÿÿ][€ãöôYäJH¬à€€ú›]Y\ûTYŸHHù[Xô\ãú\úŸR[ù
\õúŸX\ò⁄\ò[\ÀôŸ]
	‹YŸI H	…ÀL
N¬àYà
ù[Xô\ãö\—ö[ö]J]Y\ûTYŸJH	âà]Y\ûTYŸHà
Hô]\õà]Y\ûTYŸN¬à€€ú›]YŸHHù[Xô\ãú\úŸR[ù
àX€ŸY]ò[YJ\õú]ò[YJKõX]⁄
◊ œYŸOó
 Wœ…›JOÀô‹õ›\œÀúYŸH	…ÀàLà
N¬àô]\õàù[Xô\ãö\—ö[ö]J]YŸJH	âà]YŸHà»]YŸHàN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ï›[YŸ\ ÿ»Hÿ›[Y[ù
H¬à€€ú›ò[Y\»H\úò^Kôúõ€JÿÀú]Y\ûTŸ[X›‹ê[
	ÀúY⁄[ò][€àKúY⁄[ò][€àI JBàõX\
õŸHOàù[Xô\ãú\úŸR[ù
›ö[ô õŸKù^€€ù[ù	… Kúô\XŸJ÷◊åNWKŸ›K	… KL
JBàôö[\äò[YHOàù[Xô\ãö\—ö[ö]Jò[YJH	âàò[YHà
N¬à€€ú››[[X\ûSõŸ\»H\úò^Kôúõ€JÿÀú]Y\ûTŸ[X›‹ê[
	⁄H€X[à€X[öXYŸ]K[Y[Xô\ã\YŸK\›[[X\ûWI JN¬à€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJÿ N¬à€€ú›ô[ô\ôYõ€›HXõOÀú\ô[ù[[Y[ùÀú\ô[ù[[Y[ùù[¬àYà
ô[ô\ôYõ€›	âà\›[[X\ûSõŸ\Àö[ò€Y\ ô[ô\ôYõ€›
JH›[[X\ûSõŸ\Àú\⁄
ô[ô\ôYõ€›
N¬à›[[X\ûSõŸ\Àôõ‹ëXX⁄
õŸHOà¬à€€ú›^H›ö[ô õŸKù^€€ù[ù	… N¬àõ‹à
€€ú›X]⁄Ÿà^õX]⁄[
◊äŒõŸüõ€äW  œYŸ\œñ◊óJ W  ŒúYŸ\œﬂŸZ][äWãŸ⁄]JJH¬à€€ú›ò[YHHù[Xô\ãú\úŸR[ù
X]⁄ô‹õ›\œÀúYŸ\œÀúô\XŸJ÷◊åNWKŸ›K	… H	…ÀL
N¬àYà
ù[Xô\ãö\—ö[ö]Jò[YJH	âàò[YHà
Hò[Y\Àú\⁄
ò[YJN¬àBàJN¬àô]\õàX]õX^
Kããùò[Y\ N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\êX›]ö]Jõ› H¬à€€ú›X€€àHõ›Àú]Y\ûTŸ[X›‹ä	⁄[YÀõ€õ[ôW⁄X€€ã[Y÷‹‹ò èHù\Ÿ\ó»óI N¬à€€ú›€›\òŸHHX€€èÀôŸ]]öXù]J	‹‹ò… H	…Œ¬à€€ú›X]⁄H€›\òŸKõX]⁄
›\Ÿ\ó œ›]OòõY_‹ò^_‹ôY[üôYY[› JŒóñÿK^åNWJ OÀ⁄]JN¬àô]\õàX]⁄Àô‹õ›\œÀú›]OÀù”›Ÿ\êÿ\ŸJ
H	›[ö€õ›€âŒ¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\îõ€\ õ› H¬àô]\õà
õ›ÀòŸ[Àö][JJOÀú]Y\ûTŸ[X›‹ä	‹€X[	 OÀù^€€ù[ù	… Bàú‹]
	À	 BàõX\
õ€HOàõ€Kùö[J
JBàôö[\äõ€€X[äN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\î\úŸTõ› õ›ÀYŸK[ô^
H¬à€€ú›õŸö[HHõ›Àú]Y\ûTŸ[X›‹ä	ÿV⁄ôYóèHã‹õŸö[K»óI N¬àYà
\õŸö[JHô]\õàù[¬à€€ú›ò[YHHõŸö[Kù^€€ù[ùÀùö[J
H	…Œ¬àYà
[ò[YJHô]\õàù[¬à€€ú›]ò[YHHõŸö[KôŸ]]öXù]J	⁄ôYâ H	…Œ¬à€€ú›YH]ò[YKõX]⁄
◊ó‹õŸö[W œYó
 K›JOÀô‹õ›\œÀöY]ò[YHò[YN¬àô]\õà¬àX›]ö]Nà[X[òŸSY[Xô\ìX[òYŸ\êX›]ö]Jõ› KàYàò[YKà‹ô\éàYŸH
àL
»[ô^àõ€\Œà[X[òŸSY[Xô\ìX[òYŸ\îõ€\ õ› Kàõ›ÀàN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ì‹[€äò[YK^
H¬à€€ú›‹[€àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	€‹[€â N¬à‹[€ãùò[YHHò[YN¬à‹[€ãù^€€ù[ùH^¬àô]\õà‹[€é¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\í\—€P€€ù^
ÿ»Hÿ›[Y[ù
H¬à€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJÿ N¬àYà
]XõJHô]\õàò[ŸN¬à€€ú›XY[ô”Xô[HXY[ô»Oà¬à€€ú›€€ôHHXY[ôÀò€€ôSõŸJùYJN¬à€€ôKú]Y\ûTŸ[X›‹ê[
	‹€X[òòYŸKŸ]K[Y[Xô\ã\YŸK\›[[X\ûWI Kôõ‹ëXX⁄
õŸHOàõŸKúô[[›ôJ
JN¬àô]\õà›ö[ô €€ôKù^€€ù[ù	… Kúô\XŸJ◊ ÀŸ›K	»	 Kùö[J
N¬àN¬à]öY]‘õ€›HXõKú\ô[ù[[Y[ù¬àõ‹à
]\H»öY]‘õ€›	âà\»\
œHKöY]‘õ€›HöY]‘õ€›ú\ô[ù[[Y[ù
H¬à€€ú›XY[ô‹»H\úò^Kôúõ€JöY]‘õ€›ò⁄[ô[à◊JBàôö[\äõŸHOàõŸKõX]⁄\œÀä	⁄Kâ JN¬àYà
ZXY[ô‹Àõ[ô›
H€€ù[ùYN¬àô]\õàXY[ô‹Àú€€YJXY[ô»OÇà◊äŒäŒò[X[òŸ_ô\òò[ô
W  O ŒõY[Xô\úœﬂZ]€YY\äWã⁄]Kù\›
XY[ô”Xô[
XY[ô JBà
N¬àBàô]\õà\úò^Kôúõ€JÿÀú]Y\ûTŸ[X›‹ê[
	ÿV⁄ôYóI JKú€€YJ[ö»Oà¬à€€ú›ôYàH›ö[ô [öÀôŸ]]öXù]J	⁄ôYâ H	… N¬à€€ú›Y[Xô\ì[ö»H◊ó›ô\òò[ô€Z]€YY\äŒóﬂ	
K⁄]Kù\›
ôYäBà◊óÿ[X[òŸ\œ◊ Œó
◊ O€Y[Xô\ú Œóﬂ	
K⁄]Kù\›
ôYäBà◊óÿ[X[òŸW€Y[Xô\ú Œóﬂ	
K⁄]Kù\›
ôYäN¬àYà
[Y[Xô\ì[ö Hô]\õàò[ŸN¬àô]\õà[öÀõX]⁄\œÀä	ÀòX›]ôKÿ\öXKX›\úô[ùHúYŸHóI Bàõ€€X[ä[öÀò€‹Ÿ\›Àä	€KòX›]ôKòX›]ôHàKÿ\öXKX›\úô[ùHúYŸHóI JN¬àJN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ù\ôŸ]
XõJH¬à€€ú›[ö[òŸYXõTõ€›HXõOÀú\ô[ù[[Y[ùù[¬à€€ú›Y[Xô\ê€€\€ô[ùõ€›H[ö[òŸYXõTõ€›Àú\ô[ù[[Y[ùù[¬à€€ú›^\õò[[ö[òŸYXõHHõ€€X[äà[ö[òŸYXõTõ€›Àú]Y\ûTŸ[X›‹èÀä	ÀöXY[ú]úŸX\ò⁄⁄[ú]ŸöY[	 Bà
[ö[òŸYXõTõ€›Àú]Y\ûTŸ[X›‹èÀä	ÀöXY	 H	âàY[Xô\ê€€\€ô[ùõ€›Àú]Y\ûTŸ[X›‹èÀä	⁄I JBà
N¬àô]\õà^\õò[[ö[òŸYXõH	âàY[Xô\ê€€\€ô[ùõ€›»Y[Xô\ê€€\€ô[ùõ€›àXõN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùôXŸZ\

H¬à€€ú›ôY⁄\›ûHHYŸU⁄[ô›Àó◊”P”T◊’RW”S’Sï◊◊»HﬂN¬àô]\õàôY⁄\›ûKò[X[òŸSY[Xô\ìX[òYŸ\àù[¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J›]K]Z[H	… H¬à€€ú›ô^›]HH›ö[ô ›]H	›[ö€õ›€â N¬à€€ú›ôY⁄\›ûHHYŸU⁄[ô›Àó◊”P”T◊’RW”S’Sï◊◊»HﬂN¬à€€ú›ô]ö[›\»HôY⁄\›ûKò[X[òŸSY[Xô\ìX[òYŸ\é¬àYà
\ô]ö[›\»ô]ö[›\Àú›]HOOHô^›]Hô]ö[›\Àô]Z[OOH]Z[
H¬àôY⁄\›ûKò[X[òŸSY[Xô\ìX[òYŸ\àHÿöôX›ôúôY^ôJ¬à›]Nàô^›]Kà]Z[à›ö[ô ]Z[	… Kà]à›ö[ô ÿÿ][€ãú]ò[YH	… Kàô\ú⁄[€éà–‘íTùô\ú⁄[€ãà\]Y]à]Kõõ› 
KàJN¬àBà[X[òŸSY[Xô\ìX[òYŸ\ì\›[›[ù›]HHô^›]N¬àÿ›[Y[ùôÿ›[Y[ù[[Y[ùÀúŸ]]öXù]J	Ÿ]K[X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\ã[[›[ù	Àô^›]JN¬à\]P[X[òŸSY[Xô\ìX[òYŸ\ìY[ùP€€ùõ€

N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ì]]][€îô[]ò[ù
ôX€‹ô H¬à€€ú››€ôYŸ[X›‹àH	÷Ÿ]K[X€\À]ZK[›€ôYHò[X[òŸK[Y[Xô\ã[X[òYŸ\àóIŒ¬àô]\õàôX€‹ôÀú€€YJôX€‹ôOà¬àYà
ôX€‹ôù\HOOH	ÿ⁄\òX›\ë]I H¬àô]\õàõ€€X[äôX€‹ôù\ôŸ]Àú\ô[ù[[Y[ùÀò€‹Ÿ\›Àä	⁄KãŸ]K[Y[Xô\ã\YŸK\›[[X\ûWI JN¬àBàô]\õà\úò^Kôúõ€JôX€‹ôòYYõŸ\»◊JBàò€€òÿ]
\úò^Kôúõ€JôX€‹ôúô[[›ôYõŸ\»◊JJBàú€€YJõŸHOà¬àYà
[õŸHVÃKLWKö[ò€Y\ õŸKõõŸU\JJHô]\õàò[ŸN¬àYà
õŸKõõŸU\HOOHH	âà
õŸKõX]⁄\œÀä›€ôYŸ[X›‹äHõŸKò€‹Ÿ\›Àä›€ôYŸ[X›‹äJJHô]\õàò[ŸN¬àYà
õŸKõõŸU\HOOHH	âàõŸKõX]⁄\œÀä	›XõKKãŸ]K[Y[Xô\ã\YŸK\›[[X\ûWK€X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\â JHô]\õàùYN¬àô]\õàõ€€X[äõŸKú]Y\ûTŸ[X›‹èÀäà	›XõKKãV⁄ôYóèHã‹õŸö[K»óKV⁄ôYäèHã‹õŸö[K»óK€X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\â¬à
JN¬àJN¬àJN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\î]Y]YTôX€€ò⁄[JôX\€€àH	Ÿ€KX⁄[ôŸI H¬àYà
[X[òŸSY[Xô\ìX[òYŸ\îôX€€ò⁄[T]Y]YY
Hô]\õé¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€€ò⁄[T]Y]YYHùYN¬à]Y]YSZX‹õ›\⁄ 

HOà¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€€ò⁄[T]Y]YYHò[ŸN¬àôX€€ò⁄[P[X[òŸSY[Xô\ìX[òYŸ\äôX\€€äN¬àJN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ë\ÿ€€õôX›[›[ùÿúŸ\ùô\ä
H¬à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùÿúŸ\ùô\èÀô\ÿ€€õôX›

N¬à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùÿúŸ\ùô\àHù[¬à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùõ€›Hù[¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€€ò⁄[T]Y]YYHò[ŸN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ë[ú›\ôS[›[ùÿúŸ\ùô\ä
H¬à€€ú›õ€›Hÿ›[Y[ùòõŸHÿ›[Y[ùôÿ›[Y[ù[[Y[ù¬àYà
\õ€›
Hô]\õàò[ŸN¬àYà
[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùÿúŸ\ùô\à	âà[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùõ€›OOHõ€›
Hô]\õàùYN¬à[X[òŸSY[Xô\ìX[òYŸ\ë\ÿ€€õôX›[›[ùÿúŸ\ùô\ä
N¬à€€ú›ÿúŸ\ùô\àHYŸU⁄[ô›Àì]]][€ìÿúŸ\ùô\Çà
\[Ÿà]]][€ìÿúŸ\ùô\àOOH	Ÿù[ò›[€â»»]]][€ìÿúŸ\ùô\ààù[
N¬àYà
\[ŸàÿúŸ\ùô\àOOH	Ÿù[ò›[€â Hô]\õàò[ŸN¬à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùõ€›Hõ€›¬à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùÿúŸ\ùô\àHô]»ÿúŸ\ùô\äôX€‹ô»Oà¬àYà
[X[òŸSY[Xô\ìX[òYŸ\ì]]][€îô[]ò[ù
ôX€‹ô JH¬à[X[òŸSY[Xô\ìX[òYŸ\î]Y]YTôX€€ò⁄[J	€Y[Xô\ãY€K[]]][€â N¬àBàJN¬à[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùÿúŸ\ùô\ãõÿúŸ\ùôJõ€›»⁄\òX›\ë]NàùYK⁄[\›àùYK›XùôYNàùYHJN¬àô]\õàùYN¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ê€X\ì[›[ùõ›XŸJ
H¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ä	÷Ÿ]K[X€\À]ZK[›€ôYHò[X[òŸK[Y[Xô\ã[X[òYŸ\àóI OÀúô[[›ôJ
N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\î⁄›”[›[ùõ›XŸJ\úõ‹äH¬à€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJ
N¬à€€ú›\ôŸ]H[X[òŸSY[Xô\ìX[òYŸ\ì[›[ù\ôŸ]
XõJN¬àYà
]\ôŸ]Àú\ô[ù[[Y[ù
Hô]\õé¬à]õ›XŸHHÿ›[Y[ùú]Y\ûTŸ[X›‹ä	÷Ÿ]K[X€\À]ZK[›€ôYHò[X[òŸK[Y[Xô\ã[X[òYŸ\àóI N¬àYà
[õ›XŸJH¬àõ›XŸHHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àõ›XŸKúŸ]]öXù]J	Ÿ]K[X€\À]ZK[›€ôY	À	ÿ[X[òŸK[Y[Xô\ã[X[òYŸ\â N¬àõ›XŸKò€\‹”ò[YHH	ÿ[\ù[\ùY[ôŸ\âŒ¬à\ôŸ]òôYõ‹ôJõ›XŸJN¬àBàõ›XŸKù^€€ù[ùH	–[X[òŸHY[Xô\àX[òYŸ\à€›[õ›]X⁄àH€€⁄]ô]Z[ôYHXY€õ‹›X»[›[ùôXŸZ\[ô⁄[ô]ûH⁄[àHY[Xô\àöY]»⁄[ôŸ\ÀâŒ¬àõ›XŸKù]HH›ö[ô \úõ‹èÀõY\‹ÿYŸH\úõ‹à	’[ö€õ›€à[›[ù\úõ‹â N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\îô[ÿÿ]T[ô[

H¬àYà
X[X[òŸSY[Xô\ìX[òYŸ\îYŸJHô]\õé¬à€€ú›[ô[Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YX
N¬à€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJ
N¬à€€ú›[›[ù\ôŸ]H[X[òŸSY[Xô\ìX[òYŸ\ì[›[ù\ôŸ]
XõJN¬àYà
[ô[	âà[›[ù\ôŸ]	âà[ô[õô^[[Y[ù⁄Xõ[ô»OOH[›[ù\ôŸ]
H¬à[›[ù\ôŸ]òôYõ‹ôJ[ô[
N¬àBàBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\î›[J
H¬à]›[HHÿ›[Y[ùú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—Tãú›[RYX
N¬àYà
›[JHô]\õà›[N¬à›[HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹›[I N¬à›[KöYHSPSê—W”QSPëTó”PSêQ—Tãú›[RY¬à›[Kù^€€ù[ùHà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YH¬àX\ô⁄[éàLúZ[\‹ù[ù¬àõ‹ô\éà\€€YôÿòJçKLNåLåÕJHZ[\‹ù[ù¬àõ‹ô\ã\òY]\ŒàLZ[\‹ù[ù¬àòX⁄Ÿ‹õ›[ôàôÿòJLãåÃKéMäHZ[\‹ù[ù¬à€€‹éàŸYYçôàZ[\‹ù[ù¬àõﬁ\⁄Y›ŒàçôÿòJååäHZ[\‹ù[ù¬à›ô\ôõ›ŒàY[àZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KZXY¬à\‹^Nàõ^Z[\‹ù[ù¬à[Y€ãZ][\ŒàŸ[ù\àZ[\‹ù[ù¬àù\›YûKX€€ù[ùà‹XŸKXô]ŸY[àZ[\‹ù[ù¬àÿ\àLZ[\‹ù[ù¬àY[ôŒàLLúZ[\‹ù[ù¬àõ‹ô\ãXõ›€Nà\€€YôÿòJçMKçMKçMKåL
HZ[\‹ù[ù¬àòX⁄Ÿ‹õ›[ôàôÿòJçKLNåLåN
HZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KZXY›õ€ô»¬àõ€ù\⁄^ôNàMZ[\‹ù[ù¬à[ôKZZY⁄àKåàZ[\‹ù[ù¬à€€‹éàŸôôàZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KZXY‹[à¬àõ€ù\⁄^ôNàL\Z[\‹ù[ù¬à€€‹éàôÿòJåŒççMKçÃäHZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KXõŸH¬àY[ôŒàLLúLúZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KX€€ùõ€»¬à\‹^Nà‹öYZ[\‹ù[ù¬à‹öY][\]KX€€[[úŒàô\X]
ÀZ[õX^
LÃYúäJH]]»Z[\‹ù[ù¬àÿ\àZ[\‹ù[ù¬à[Y€ãZ][\Œà[ôZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHXô[¬à\‹^Nà‹öYZ[\‹ù[ù¬àÿ\àZ[\‹ù[ù¬àX\ô⁄[éàZ[\‹ù[ù¬à€€‹éàôÿòJåŒççMKçŒ
HZ[\‹ù[ù¬àõ€ù\⁄^ôNàL\Z[\‹ù[ù¬àõ€ù]ŸZY⁄àZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHŸ[X›à…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHù]€à¬àZ[ãZZY⁄àŒZ[\‹ù[ù¬àõ‹ô\éà\€€YôÿòJçMKçMKçMKåN
HZ[\‹ù[ù¬àõ‹ô\ã\òY]\ŒàZ[\‹ù[ù¬àòX⁄Ÿ‹õ›[ôàôÿòJçMKçMKçMKå
HZ[\‹ù[ù¬à€€‹éàŸôôàZ[\‹ù[ù¬àõ€ùàLúÃKåàﬁ\›[K]ZKX\K\ﬁ\›[Kõ[ö”XX‘ﬁ\›[Qõ€ùîŸY€ŸHRHãÿ[úÀ\Ÿ\öYàZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHŸ[X›¬à⁄YàL	HZ[\‹ù[ù¬àY[ôŒà\Z[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHŸ[X›‹[€à¬à€€‹éàÃLLHZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHù]€à¬àY[ôŒà‹L\Z[\‹ù[ù¬à›\ú€‹éà⁄[ù\àZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHù]€éö›ô\ãà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHù]€éôõÿ›\À]ö\⁄XõH¬àòX⁄Ÿ‹õ›[ôàôÿòJçKLNåLåÕ
HZ[\‹ù[ù¬àõ‹ô\ãX€€‹éàôÿòJLåNLçMKéäHZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHù]€éô\ÿXõY¬à›\ú€‹éàÿZ]Z[\‹ù[ù¬à‹X⁄]NàçNZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KXX›[€ú»¬à\‹^Nàõ^Z[\‹ù[ù¬àõ^]‹ò\à‹ò\Z[\‹ù[ù¬àÿ\àZ[\‹ù[ù¬àX\ô⁄[ã]‹à\Z[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[K\ö[X\ûH¬àòX⁄Ÿ‹õ›[ôàôÿòJçKLNåLç
HZ[\‹ù[ù¬àõ‹ô\ãX€€‹éàôÿòJLåNLçMKçÃäHZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[K\õŸ‹ô\‹Àà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[K\›[[X\ûH¬àX\ô⁄[éàZ[\‹ù[ù¬à€€‹éàôÿòJåŒççMKçÕ
HZ[\‹ù[ù¬àõ€ù\⁄^ôNàL\Z[\‹ù[ù¬à[ôKZZY⁄àKåÕHZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[K\õŸ‹ô\‹Œô[\H¬à\‹^Nàõ€ôHZ[\‹ù[ù¬àBàYYXH
X^]⁄YàÃå
H¬à…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KZXY¬à[Y€ãZ][\Œàõ^\›\ùZ[\‹ù[ù¬àõ^Y\ôX›[€éà€€[[àZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KX€€ùõ€»¬à‹öY][\]KX€€[[úŒàZ[õX^
YúäHZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHŸ[X›à…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHù]€à¬àZ[ãZZY⁄àZ[\‹ù[ù¬àõ€ù\⁄^ôNàMúZ[\‹ù[ù¬àBà…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YHõX€\ÀX[[KXX›[€ú»¬à\‹^Nà‹öYZ[\‹ù[ù¬à‹öY][\]KX€€[[úŒàZ[õX^
YúäHZ[\‹ù[ù¬àBàBà¬à
ÿ›[Y[ùöXYÿ›[Y[ùôÿ›[Y[ù[[Y[ù
Kò\[ô
›[JN¬àô]\õà›[N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\îôYúô\⁄õ€S‹[€ú €€ù^
H¬à€€ú›Ÿ[X›YH€€ù^úõ€TŸ[X›ùò[YN¬à€€ú›õ€\»H\úò^Kôúõ€Jô]»Ÿ]
à\úò^Kôúõ€J€€ù^õY[Xô\úÀùò[Y\ 
JKôõ]X\
Y[Xô\àOàY[Xô\ãúõ€\ Bà
JKú€‹ù

YùöY⁄
HOà€€ù^ò€€]‹ãò€€\\ôJYùöY⁄
JN¬à€€ù^úõ€TŸ[X›úô\XŸP⁄[ô[äà[X[òŸSY[Xô\ìX[òYŸ\ì‹[€ä	…À	–[õ€\… Kà[X[òŸSY[Xô\ìX[òYŸ\ì‹[€äSPSê—W”QSPëTó”PSêQ—Tãõõ‘õ€K	”õ»õ€I Kàããúõ€\ÀõX\
õ€HOà[X[òŸSY[Xô\ìX[òYŸ\ì‹[€äõ€Kõ€JJBà
N¬àYà
\úò^Kôúõ€J€€ù^úõ€TŸ[X›õ‹[€ú Kú€€YJ‹[€àOà‹[€ãùò[YHOOHŸ[X›Y
JH¬à€€ù^úõ€TŸ[X›ùò[YHHŸ[X›Y¬àBàBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
H¬àYà
[X[òŸSY[Xô\ìX[òYŸ\îYŸHOOH€€ù^
Hô]\õé¬à€€ú›X›]ö]Tò[ö»H¬à‹ôY[éààY[›ŒàKàõYNàãà‹ò^NàÀàôYàà[ö€õ›€éàKàN¬à€€ú›Ÿ[X›Yõ€HH€€ù^úõ€TŸ[X›ùò[YN¬à€€ú›Ÿ[X›YX›]ö]HH€€ù^òX›]ö]TŸ[X›ùò[YN¬à€€ú›€‹ùH€€ù^ú€‹ùŸ[X›ùò[YN¬à€€ú›[ŸYöY\àH€€ù^ô\ÿŸ[ô[ô»»LHàN¬à€€ú›‹ô\ôYH\úò^Kôúõ€J€€ù^õY[Xô\úÀùò[Y\ 
JKú€‹ù

YùöY⁄
HOà¬à]ô\›[H¬àYà
€‹ùOOH	€ò[YI H¬àô\›[H€€ù^ò€€]‹ãò€€\\ôJYùõò[YKöY⁄õò[YJN¬àH[ŸHYà
€‹ùOOH	‹õ€I H¬àô\›[H€€ù^ò€€]‹ãò€€\\ôJàYùúõ€\Àöõ⁄[ä	À	 H	◊YôôôâÀàöY⁄úõ€\Àöõ⁄[ä	À	 H	◊Yôôôâ¬à
N¬àH[ŸHYà
€‹ùOOH	ÿX›]ö]I H¬àô\›[HX›]ö]Tò[ö÷€YùòX›]ö]WHHX›]ö]Tò[ö÷‹öY⁄òX›]ö]WN¬àH[ŸH¬àô\›[HYùõ‹ô\àHöY⁄õ‹ô\é¬àBàYà
\ô\›[
Hô\›[H€€ù^ò€€]‹ãò€€\\ôJYùõò[YKöY⁄õò[YJN¬àô]\õàô\›[
à[ŸYöY\é¬àJN¬à]ö\⁄XõHH¬à‹ô\ôYôõ‹ëXX⁄
Y[Xô\àOà¬à€€ú›õ€SX]⁄\»H\Ÿ[X›Yõ€H
àŸ[X›Yõ€HOOHSPSê—W”QSPëTó”PSêQ—Tãõõ‘õ€Bà»[Y[Xô\ãúõ€\Àõ[ô›ààY[Xô\ãúõ€\Àö[ò€Y\ Ÿ[X›Yõ€JBà
N¬à€€ú›X›]ö]SX]⁄\»H\Ÿ[X›YX›]ö]H
àŸ[X›YX›]ö]HOOH	€€õ[ôI¬à»Y[Xô\ãòX›]ö]HOOH	Ÿ‹ôY[â¬ààY[Xô\ãòX›]ö]HOOH	Ÿ‹ôY[â»	âàY[Xô\ãòX›]ö]HOOH	›[ö€õ›€â¬à
N¬àY[Xô\ãúõ›ÀöY[àHJõ€SX]⁄\»	âàX›]ö]SX]⁄\ N¬àYà
[Y[Xô\ãúõ›ÀöY[äHö\⁄XõH
œHN¬à€€ù^ùõŸKò\[ô
Y[Xô\ãúõ› N¬àJN¬à€€ù^ú›[[X\ûKù^€€ù[ùBà⁄›⁄[ô»	›ö\⁄Xõ_HŸà	ÿ€€ù^õY[Xô\úÀú⁄^ô_HY[Xô\ú»0≠»
¬à	ÿ€€ù^õÿYYYŸ\Àú⁄^ô_HŸà	ÿ€€ù^ù›[YŸ\ﬂHYŸ\»ÿYY¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\êYYŸJ€€ù^ÿÀYŸJH¬à€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJÿ N¬à€€ú›õŸHH[X[òŸSY[Xô\ìX[òYŸ\êõŸJXõJN¬àYà
XõŸJHõ›»ô]»\úõ‹äY[Xô\àXõHZ\‹⁄[ô»€àYŸH	‹YŸ_X
N¬à\úò^Kôúõ€JõŸKúõ›‹ Kôõ‹ëXX⁄

õ›À[ô^
HOà¬à€€ú›[\‹ùYHÿ›[Y[ùö[\‹ùõŸJõ›ÀùYJN¬à€€ú›Y[Xô\àH[X[òŸSY[Xô\ìX[òYŸ\î\úŸTõ› [\‹ùYYŸK[ô^
N¬àYà
[Y[Xô\à€€ù^õY[Xô\úÀö\ Y[Xô\ãöY
JHô]\õé¬à€€ù^õY[Xô\úÀúŸ]
Y[Xô\ãöYY[Xô\äN¬à€€ù^ö[\‹ùYõ›‹ÀòY
[\‹ùY
N¬à€€ù^ùõŸKò\[ô
[\‹ùY
N¬àJN¬à€€ù^õÿYYYŸ\ÀòY
YŸJN¬à[X[òŸSY[Xô\ìX[òYŸ\îôYúô\⁄õ€S‹[€ú €€ù^
N¬à[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
N¬àBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\îYŸU\õ
YŸJH¬à€€ú›\õHô]»Tì
ÿÿ][€ãöôYäN¬à\õúŸX\ò⁄\ò[\ÀúŸ]
	‹YŸIÀ›ö[ô YŸJJN¬à\õö\⁄H	…Œ¬àô]\õà\õöôYé¬àBÇà\ﬁ[ò»ù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\ìÿY[
€€ù^
H¬àYà
€€ù^õÿY[ô»[X[òŸSY[Xô\ìX[òYŸ\îYŸHOOH€€ù^
Hô]\õé¬à€€ù^õÿY[ô»HùYN¬à€€ù^òXõ‹ù€€ùõ€\àHô]»Xõ‹ù€€ùõ€\ä
N¬à€€ù^õÿY[ù]€ãô\ÿXõYHùYN¬àûH¬àõ‹à
]YŸHHN»YŸHH€€ù^ù›[YŸ\Œ»YŸH
œHJH¬àYà
€€ù^õÿYYYŸ\Àö\ YŸJJH€€ù[ùYN¬à€€ù^úõŸ‹ô\‹Àù^€€ù[ùBàÿY[ô»Y[Xô\àYŸH	‹YŸ_HŸà	ÿ€€ù^ù›[YŸ\ﬂx†)ò¬à€€ú›ô\‹€úŸHH]ÿZ]ô]⁄
[X[òŸSY[Xô\ìX[òYŸ\îYŸU\õ
YŸJK¬à‹ôY[ùX[Œà	‹ÿ[YK[‹öY⁄[âÀàXY\úŒà»	÷Tô\]Y\›YU⁄]	Œà	÷Sô\]Y\›	»Kà⁄Y€ò[à€€ù^òXõ‹ù€€ùõ€\ãú⁄Y€ò[àJN¬àYà
\ô\‹€úŸKõ⁄ Hõ›»ô]»\úõ‹äYŸH	‹YŸ_Hô]\õôY	‹ô\‹€úŸKú›]\ﬂX
N¬à€€ú›[H]ÿZ]ô\‹€úŸKù^

N¬à€€ú›ÿ»Hô]»”T\úŸ\ä
Kú\úŸQúõ€T›ö[ô [	›^⁄[	 N¬àYà
[X[òŸSY[Xô\ìX[òYŸ\îYŸHOOH€€ù^
Hô]\õé¬à[X[òŸSY[Xô\ìX[òYŸ\êYYŸJ€€ù^ÿÀYŸJN¬àBà€€ù^úõŸ‹ô\‹Àù^€€ù[ùH	–[Y[Xô\àYŸ\»ÿYYâŒ¬à€€ù^õÿY[ù]€ãù^€€ù[ùH	–[Y[Xô\àYŸ\»ÿYY	Œ¬àHÿ]⁄
\úõ‹äH¬àYà
\úõ‹èÀõò[YHOOH	–Xõ‹ù\úõ‹â»	âà[X[òŸSY[Xô\ìX[òYŸ\îYŸHOOH€€ù^
H¬à€€ù^úõŸ‹ô\‹Àù^€€ù[ùBà€›[õ›ÿY]ô\ûHY[Xô\àYŸNà	Ÿ\úõ‹èÀõY\‹ÿYŸH\úõ‹üX¬àBàHö[ò[H¬àYà
[X[òŸSY[Xô\ìX[òYŸ\îYŸHOOH€€ù^
H¬à€€ù^õÿY[ô»Hò[ŸN¬à€€ù^òXõ‹ù€€ùõ€\àHù[¬à€€ù^õÿY[ù]€ãô\ÿXõYBà€€ù^õÿYYYŸ\Àú⁄^ôHèH€€ù^ù›[YŸ\Œ¬àBàBàBÇàù[ò›[€à[X[òŸSY[Xô\ìX[òYŸ\îô\Ÿ]
€€ù^
H¬à€€ù^úõ€TŸ[X›ùò[YHH	…Œ¬à€€ù^òX›]ö]TŸ[X›ùò[YHH	…Œ¬à€€ù^ú€‹ùŸ[X›ùò[YHH	ŸYò][	Œ¬à€€ù^ô\ÿŸ[ô[ô»Hò[ŸN¬à€€ù^ô\ôX›[€êù]€ãù^€€ù[ùH	¯°§IŒ¬à€€ù^ô\ôX›[€êù]€ãúŸ]]öXù]J	ÿ\öXK\ô\‹ŸY	À	Ÿò[ŸI N¬à[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
N¬àBÇàù[ò›[€à[ú›[[X[òŸSY[Xô\ìX[òYŸ\ä
H¬àYà
à[X[òŸSY[Xô\ìX[òYŸ\îYŸHàX[X[òŸSY[Xô\ìX[òYŸ\ë[òXõY

HàX[X[òŸSY[Xô\ìX[òYŸ\í\—€P€€ù^

Hà[X[òŸSY[Xô\ìX[òYŸ\ì›\ì›€ô\îô\Ÿ[ù

Bà
Hô]\õé¬à€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJÿ›[Y[ù
N¬à€€ú›õŸHH[X[òŸSY[Xô\ìX[òYŸ\êõŸJXõJN¬àYà
]XõH]õŸJHô]\õé¬à€€ú››\úô[ùYŸHH[X[òŸSY[Xô\ìX[òYŸ\ê›\úô[ùYŸJ
N¬à€€ú››[YŸ\»H[X[òŸSY[Xô\ìX[òYŸ\ï›[YŸ\ 
N¬à€€ú›Y[Xô\ú»Hô]»X\

N¬à€€ú›‹öY⁄[ò[õ›‹»H\úò^Kôúõ€JõŸKúõ›‹ N¬à‹öY⁄[ò[õ›‹Àôõ‹ëXX⁄

õ›À[ô^
HOà¬à€€ú›Y[Xô\àH[X[òŸSY[Xô\ìX[òYŸ\î\úŸTõ› õ›À›\úô[ùYŸK[ô^
N¬àYà
Y[Xô\äHY[Xô\úÀúŸ]
Y[Xô\ãöYY[Xô\äN¬àJN¬àYà
[Y[Xô\úÀú⁄^ôJHô]\õé¬Çà[X[òŸSY[Xô\ìX[òYŸ\î›[J
N¬à€€ú›[ô[Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹ŸX›[€â N¬à[ô[öYHSPSê—W”QSPëTó”PSêQ—Tãú[ô[Y¬à[ô[úŸ]]öXù]J	ÿ\öXK[Xô[	À	–[X[òŸHY[Xô\àX[òYŸ\â N¬Çà€€ú›XYHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àXYò€\‹”ò[YHH	€X€\ÀX[[KZXY	Œ¬à€€ú›]HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹›õ€ô… N¬à]Kù^€€ù[ùH	–[X[òŸHY[Xô\àX[òYŸ\âŒ¬à€€ú››Xù]HHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹‹[â N¬à›Xù]Kù^€€ù[ùH	—ö[\à[ô€‹ùH›\úô[ù[X[òŸHY[Xô\à\›	Œ¬àXYò\[ô
]K›Xù]JN¬Çà€€ú›õŸHHÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àõŸKò€\‹”ò[YHH	€X€\ÀX[[KXõŸIŒ¬à€€ú›€€ùõ€»Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬à€€ùõ€Àò€\‹”ò[YHH	€X€\ÀX[[KX€€ùõ€…Œ¬Çà€€ú›‹ôX]TŸ[X›H
Xô[^‹[€ú HOà¬à€€ú›Xô[Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	€Xô[	 N¬àXô[ò\[ô
ÿ›[Y[ùò‹ôX]U^õŸJXô[^
JN¬à€€ú›Ÿ[X›Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹Ÿ[X›	 N¬à‹[€úÀôõ‹ëXX⁄

›ò[YK^JHOÇàŸ[X›ò\[ô
[X[òŸSY[Xô\ìX[òYŸ\ì‹[€äò[YK^
JBà
N¬àXô[ò\[ô
Ÿ[X›
N¬à€€ùõ€Àò\[ô
Xô[
N¬àô]\õàŸ[X›¬àN¬Çà€€ú›õ€TŸ[X›H‹ôX]TŸ[X›
	‘õ€IÀ÷……À	–[õ€\…◊WJN¬à€€ú›X›]ö]TŸ[X›H‹ôX]TŸ[X›
	–X›]ö]IÀ¬à……À	–[Y[Xô\ú…◊Kà…€€õ[ôIÀ	”€õ[ôI◊Kà…€Ÿôõ[ôIÀ	”Ÿôõ[ôI◊KàJN¬à€€ú›€‹ùŸ[X›H‹ôX]TŸ[X›
	‘€‹ùûIÀ¬à…ŸYò][	À	”‹öY⁄[ò[‹ô\â◊Kà…€ò[YIÀ	”Y[Xô\àò[YI◊Kà…‹õ€IÀ	–[X[òŸHõ€I◊Kà…ÿX›]ö]IÀ	–X›]ö]I◊KàJN¬à€€ú›\ôX›[€êù]€àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿù]€â N¬à\ôX›[€êù]€ãù\HH	ÿù]€âŒ¬à\ôX›[€êù]€ãù^€€ù[ùH	¯°§IŒ¬à\ôX›[€êù]€ãù]HH	‘€‹ù\ôX›[€âŒ¬à\ôX›[€êù]€ãúŸ]]öXù]J	ÿ\öXK[Xô[	À	‘€‹ù\ôX›[€â N¬à\ôX›[€êù]€ãúŸ]]öXù]J	ÿ\öXK\ô\‹ŸY	À	Ÿò[ŸI N¬à€€ùõ€Àò\[ô
\ôX›[€êù]€äN¬Çà€€ú›X›[€ú»Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	Ÿ]â N¬àX›[€úÀò€\‹”ò[YHH	€X€\ÀX[[KXX›[€ú…Œ¬à€€ú›ÿY[ù]€àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿù]€â N¬àÿY[ù]€ãù\HH	ÿù]€âŒ¬àÿY[ù]€ãò€\‹”ò[YHH	€X€\ÀX[[K\ö[X\ûIŒ¬àÿY[ù]€ãù^€€ù[ùBà›[YŸ\»àH»	”ÿY[Y[Xô\àYŸ\…»à	–[Y[Xô\àYŸ\»ÿYY	Œ¬àÿY[ù]€ãô\ÿXõYH›[YŸ\»HN¬à€€ú›ô\Ÿ]ù]€àHÿ›[Y[ùò‹ôX]Q[[Y[ù
	ÿù]€â N¬àô\Ÿ]ù]€ãù\HH	ÿù]€âŒ¬àô\Ÿ]ù]€ãù^€€ù[ùH	‘ô\Ÿ]	Œ¬àX›[€úÀò\[ô
ÿY[ù]€ãô\Ÿ]ù]€äN¬Çà€€ú›õŸ‹ô\‹»Hÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹	 N¬àõŸ‹ô\‹Àò€\‹”ò[YHH	€X€\ÀX[[K\õŸ‹ô\‹…Œ¬àõŸ‹ô\‹ÀúŸ]]öXù]J	ÿ\öXK[]ôIÀ	‹€]I N¬à€€ú››[[X\ûHHÿ›[Y[ùò‹ôX]Q[[Y[ù
	‹	 N¬à›[[X\ûKò€\‹”ò[YHH	€X€\ÀX[[K\›[[X\ûIŒ¬à›[[X\ûKúŸ]]öXù]J	ÿ\öXK[]ôIÀ	‹€]I N¬àõŸKò\[ô
€€ùõ€ÀX›[€úÀõŸ‹ô\‹À›[[X\ûJN¬à[ô[ò\[ô
XYõŸJN¬àXõKòôYõ‹ôJ[ô[
N¬Çà€€ú›€€ù^H¬àXõ‹ù€€ùõ€\éàù[àX›]ö]TŸ[X›à€€]‹éàô]»[ùê€€]‹ä[ôYö[ôY»ù[Y\öXŒàùYKŸ[ú⁄]]ö]Nà	ÿò\ŸI»JKà›\úô[ùYŸKà\ÿŸ[ô[ôŒàò[ŸKà\ôX›[€êù]€ãà[\‹ùYõ›‹Œàô]»Ÿ]

KàÿYYYŸ\Œàô]»Ÿ]
ÿ›\úô[ùYŸWJKàÿY[ôŒàò[ŸKàÿY[ù]€ãàY[Xô\úÀà‹öY⁄[ò[õ›‹Àà[ô[àõŸ‹ô\‹Ààô\Ÿ]ù]€ãàõ€TŸ[X›à€‹ùŸ[X›à›[[X\ûKàXõKàõŸKà›[YŸ\ÀàN¬à[X[òŸSY[Xô\ìX[òYŸ\îYŸHH€€ù^¬à[X[òŸSY[Xô\ìX[òYŸ\îôYúô\⁄õ€S‹[€ú €€ù^
N¬à[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
N¬Çàõ€TŸ[X›òY]ô[ù\›[ô\ä	ÿ⁄[ôŸIÀ

HOà[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
JN¬àX›]ö]TŸ[X›òY]ô[ù\›[ô\ä	ÿ⁄[ôŸIÀ

HOà[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
JN¬à€‹ùŸ[X›òY]ô[ù\›[ô\ä	ÿ⁄[ôŸIÀ

HOà[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
JN¬à\ôX›[€êù]€ãòY]ô[ù\›[ô\ä	ÿ€X⁄…À

HOà¬à€€ù^ô\ÿŸ[ô[ô»HX€€ù^ô\ÿŸ[ô[ôŒ¬à\ôX›[€êù]€ãù^€€ù[ùH€€ù^ô\ÿŸ[ô[ô»»	¯°§…»à	¯°§IŒ¬à\ôX›[€êù]€ãúŸ]]öXù]J	ÿ\öXK\ô\‹ŸY	À›ö[ô €€ù^ô\ÿŸ[ô[ô JN¬à[X[òŸSY[Xô\ìX[òYŸ\ê\J€€ù^
N¬àJN¬àÿY[ù]€ãòY]ô[ù\›[ô\ä	ÿ€X⁄…À

HOà¬àõ⁄Y[X[òŸSY[Xô\ìX[òYŸ\ìÿY[
€€ù^
N¬àJN¬àô\Ÿ]ù]€ãòY]ô[ù\›[ô\ä	ÿ€X⁄…À

HOà[X[òŸSY[Xô\ìX[òYŸ\îô\Ÿ]
€€ù^
JN¬àBÇàù[ò›[€à\‹‹ŸP[X[òŸSY[Xô\ìX[òYŸ\ä
H¬à€€ú›€€ù^H[X[òŸSY[Xô\ìX[òYŸ\îYŸN¬àYà
X€€ù^
H¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YX
OÀúô[[›ôJ
N¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—Tãú›[RYX
OÀúô[[›ôJ
N¬àô]\õé¬àBà€€ù^òXõ‹ù€€ùõ€\èÀòXõ‹ù

N¬à€€ù^ö[\‹ùYõ›‹Àôõ‹ëXX⁄
õ›»Oàõ›Àúô[[›ôJ
JN¬à€€ù^õ‹öY⁄[ò[õ›‹Àôõ‹ëXX⁄
õ›»Oà¬àõ›ÀöY[àHò[ŸN¬à€€ù^ùõŸKò\[ô
õ› N¬àJN¬à€€ù^ú[ô[úô[[›ôJ
N¬àÿ›[Y[ùú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—Tãú›[RYX
OÀúô[[›ôJ
N¬à[X[òŸSY[Xô\ìX[òYŸ\îYŸHHù[¬àBÇàù[ò›[€àôX€€ò⁄[P[X[òŸSY[Xô\ìX[òYŸ\äôX\€€àH	‹ôX€€ò⁄[I H¬à€€ú›[òXõYH[X[òŸSY[Xô\ìX[òYŸ\ë[òXõY

N¬àYà
Y[òXõY
H¬à[X[òŸSY[Xô\ìX[òYŸ\ë\ÿ€€õôX›[›[ùÿúŸ\ùô\ä
N¬à[X[òŸSY[Xô\ìX[òYŸ\ê€X\ì[›[ùõ›XŸJ
N¬à\‹‹ŸP[X[òŸSY[Xô\ìX[òYŸ\ä
N¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J	Ÿ\ÿXõY	ÀôX\€€äN¬àô]\õé¬àBÇà€€ú›ÿúŸ\ùö[ô»H[X[òŸSY[Xô\ìX[òYŸ\ë[ú›\ôS[›[ùÿúŸ\ùô\ä
N¬à€€ú›õ›]SX]⁄H\–[X[òŸSY[Xô\ìX[òYŸ\îõ›]J
N¬à€€ú›€SX]⁄H[X[òŸSY[Xô\ìX[òYŸ\í\—€P€€ù^

N¬àYà
Y€SX]⁄
H¬à[X[òŸSY[Xô\ìX[òYŸ\ê€X\ì[›[ùõ›XŸJ
N¬à\‹‹ŸP[X[òŸSY[Xô\ìX[òYŸ\ä
N¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]JàÿúŸ\ùö[ô»»	›ÿ]⁄[ô…»à	›ÿZ][ô…Ààõ›]SX]⁄à»	”Y[Xô\àõ›]Hõ›[ô»ÿZ][ô»õ‹àH€€ôö\õYYY[Xô\àöY]…¬àà	—[òXõY»ÿZ][ô»õ‹à[à[X[òŸHY[Xô\àöY]…¬à
N¬àô]\õé¬àBàYà
[X[òŸSY[Xô\ìX[òYŸ\ì›\ì›€ô\îô\Ÿ[ù

JH¬à[X[òŸSY[Xô\ìX[òYŸ\ê€X\ì[›[ùõ›XŸJ
N¬à\‹‹ŸP[X[òŸSY[Xô\ìX[òYŸ\ä
N¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J	‹›\ô\‹ŸY	À	—\]Z]ò[[ùX[òYŸ\à[ôXYH›€ú»\»öY]… N¬àô]\õé¬àBÇà€€ú›XõHH[X[òŸSY[Xô\ìX[òYŸ\ïXõJ
N¬à€€ú›[ô[Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—Tãú[ô[YX
N¬à€€ú›[ô[€€õôX›YHõ€€X[ä[ô[	âà[ô[ö\–€€õôX›YOOHò[ŸJN¬àYà
à[X[òŸSY[Xô\ìX[òYŸ\îYŸBà	âà
\[ô[€€õôX›Y
XõH	âà[X[òŸSY[Xô\ìX[òYŸ\îYŸKùXõH	âà[X[òŸSY[Xô\ìX[òYŸ\îYŸKùXõHOOHXõJJBà
H¬à\‹‹ŸP[X[òŸSY[Xô\ìX[òYŸ\ä
N¬àBàYà
]XõJH¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J	›ÿZ][ô…À	”Y[Xô\àöY]»õ›[ô»ÿZ][ô»õ‹à]»XõI N¬àô]\õé¬àBÇàûH¬à[ú›[[X[òŸSY[Xô\ìX[òYŸ\ä
N¬àYà
X[X[òŸSY[Xô\ìX[òYŸ\îYŸJH¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J	›ÿZ][ô…À	”Y[Xô\àXõHõ›[ô»[ú›[\à\»õ›€Z[YY]Y]	 N¬àô]\õé¬àBà[X[òŸSY[Xô\ìX[òYŸ\îô[ÿÿ]T[ô[

N¬à[X[òŸSY[Xô\ìX[òYŸ\ê€X\ì[›[ùõ›XŸJ
N¬à[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J	€[›[ùY	À€€õôX›Y»	ÿ[X[òŸSY[Xô\ìX[òYŸ\îYŸKõY[Xô\úœÀú⁄^ôHHY[Xô\úÿ
N¬àHÿ]⁄
\úõ‹äH¬àûH»\‹‹ŸP[X[òŸSY[Xô\ìX[òYŸ\ä
N»Hÿ]⁄
\‹‹ŸQ\úõ‹äHﬂBà[X[òŸSY[Xô\ìX[òYŸ\îôX€‹ô[›[ù›]J	Ÿ\úõ‹âÀ›ö[ô \úõ‹èÀõY\‹ÿYŸH\úõ‹à	’[ö€õ›€à[›[ù\úõ‹â JN¬à[X[òŸSY[Xô\ìX[òYŸ\î⁄›”[›[ùõ›XŸJ\úõ‹äN¬à€€ú€€Kô\úõ‹ä	÷’€€⁄]H[X[òŸHY[Xô\àX[òYŸ\à[›[ùòZ[Y	À\úõ‹äN¬àBàBÇàù[ò›[€à\]P[X[òŸSY[Xô\ìX[òYŸ\ìY[ùP€€ùõ€

H¬à€€ú›[ô[Hÿ›[Y[ùú]Y\ûTŸ[X›‹ä…‘–‘íTú[ô[YX
N¬à€€ú›ù]€àH[ô[Àú]Y\ûTŸ[X›‹ä…–SPSê—W”QSPëTó”PSêQ—TãõY[ùP]öXù]_WX
N¬àYà
Xù]€äHô]\õé¬à€€ú›[òXõYH[X[òŸSY[Xô\ìX[òYŸ\ë[òXõY

N¬à€€ú›[›[ù›]HH[X[òŸSY[Xô\ìX[òYŸ\ì[›[ùôXŸZ\

OÀú›]H[X[òŸSY[Xô\ìX[òYŸ\ì\›[›[ù›]N¬à€€ú›[›[ùYH[›[ù›]HOOH	€[›[ùY	Œ¬à€€ú›òZ[YH[›[ù›]HOOH	Ÿ\úõ‹âŒ¬àù]€ãò€\‹”\›ùŸŸ€J	€X€\À[€âÀ[òXõY
N¬àù]€ãúŸ]]öXù]J	ÿ\öXK\ô\‹ŸY	À›ö[ô [òXõY
JN¬àù]€ãúŸ]]öXù]J	Ÿ]K[X€\À[[›[ù\›]IÀ[›[ù›]H	⁄YI N¬à€€ú›[Hù]€ãú]Y\ûTŸ[X›‹ä	ÀõX€\À\[	 N¬àYà
[
H[ù^€€ù[ùHY[òXõY»	”—ëâ»àòZ[Y»	—Tîâ»à[›[ùY»	””â»à	’–RU	Œ¬à€€ú››]U^HY[òXõYà»	Ÿ\ÿXõY	¬ààòZ[Yà»	Ÿ[òXõYYŸH€€ùõ€»òZ[Y»[›[ù	¬àà[›[ùYà»	Ÿ[òXõY[ô[›[ùY	¬àà	Ÿ[òXõYÿZ][ô»õ‹àH€€\]XõHY[Xô\àöY]…Œ¬àù]€ãù]HH[X[òŸHY[Xô\àX[òYŸ\éà	‹›]U^X¬àù]€ãúŸ]]öXù]J	ÿ\öXK[Xô[	À[X[òŸHY[Xô\àX[òYŸ\à	‹›]U^X
N¬àBÇàYà
\[Ÿàÿ›[Y[ùòY]ô[ù\›[ô\àOOH	Ÿù[ò›[€â H¬àYà
ÿ›[Y[ùúôXYT›]HOOH	€ÿY[ô… H¬àôX€€ò⁄[P[X[òŸSY[Xô\ìX[òYŸ\ä
N¬àH[ŸH¬àÿ›[Y[ùòY]ô[ù\›[ô\ä	—”P€€ù[ùÿYY	ÀôX€€ò⁄[P[X[òŸSY[Xô\ìX[òYŸ\ã»€òŸNàùYHJN¬àBàBàÀ»€X€\ÀX[X[òŸK[Y[Xô\ã[X[òYŸ\èÇüJJ
N¬