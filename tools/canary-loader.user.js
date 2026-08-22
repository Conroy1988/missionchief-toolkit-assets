// ==UserScript==
// @name         MissionChief Map Command Toolkit — Maintainer Canary Loader
// @namespace    https://github.com/Conroy1988/missionchief-map-command-toolkit/canary-loader
// @version      1.0.0
// @description  Opt-in, hash-verified Toolkit canary loader with cached fallback and local rollback.
// @author       Conroy1988
// @license      MIT
// @homepageURL  https://github.com/Conroy1988/missionchief-toolkit-assets
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
// @connect      raw.githubusercontent.com
// @run-at       document-start
// @downloadURL  https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/tools/canary-loader.user.js
// @updateURL    https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/tools/canary-loader.user.js
// ==/UserScript==

(function () {
    'use strict';

    const LOADER_VERSION = 1;
    const MANIFEST_URL = 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/canary/canary/manifest.json';
    const EXPECTED_BUNDLE_PREFIX = 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/canary/canary/';
    const KEYS = Object.freeze({
        enabled: 'mcms_canary_loader_enabled_v1',
        cache: 'mcms_canary_loader_cache_v1',
        backup: 'mcms_canary_loader_settings_backup_v1',
    });
    const pageWindow = typeof unsafeWindow !== 'undefined' ? unsafeWindow : window;
    const hiddenStyle = document.createElement('style');
    hiddenStyle.textContent = '#mc-map-command-toolkit-control,#mc-map-command-toolkit-panel{visibility:hidden!important}';
    let enabled = true;

    function gmRead(key, fallback) {
        try {
            const value = GM_getValue(key, fallback);
            return Promise.resolve(value === undefined ? fallback : value);
        } catch (error) {
            return Promise.resolve(fallback);
        }
    }

    function gmWrite(key, value) {
        try { return Promise.resolve(GM_setValue(key, value)); }
        catch (error) { return Promise.reject(error); }
    }

    function gmDelete(key) {
        try { return Promise.resolve(GM_deleteValue(key)); }
        catch (error) { return Promise.resolve(); }
    }

    function requestText(url, timeout = 12000) {
        return new Promise((resolve, reject) => {
            let settled = false;
            const request = GM_xmlhttpRequest({
                method: 'GET',
                url: `${url}${url.includes('?') ? '&' : '?'}canary_cache_bust=${Date.now()}`,
                timeout,
                headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache' },
                onload(response) {
                    if (settled) return;
                    settled = true;
                    if (Number(response.status) < 200 || Number(response.status) >= 300) {
                        reject(new Error(`Canary request returned HTTP ${response.status}`));
                        return;
                    }
                    resolve(String(response.responseText || ''));
                },
                onerror() { if (!settled) { settled = true; reject(new Error('Canary request failed')); } },
                ontimeout() { if (!settled) { settled = true; reject(new Error('Canary request timed out')); } },
                onabort() { if (!settled) { settled = true; reject(new Error('Canary request was aborted')); } },
            });
            if (!request || typeof request.abort !== 'function') reject(new Error('Canary request API is unavailable'));
        });
    }

    async function sha256(value) {
        if (!pageWindow.crypto?.subtle) throw new Error('Web Crypto SHA-256 is unavailable');
        const bytes = new TextEncoder().encode(value);
        const digest = await pageWindow.crypto.subtle.digest('SHA-256', bytes);
        return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
    }

    function validateManifest(value) {
        if (!value || typeof value !== 'object' || value.schemaVersion !== 1 || value.channel !== 'canary') throw new Error('Canary manifest schema is invalid');
        if (!/^[0-9A-Za-z][0-9A-Za-z._-]{5,79}$/u.test(String(value.buildId || ''))) throw new Error('Canary build identity is invalid');
        if (!/^\d+\.\d+\.\d+\.\d{14}$/u.test(String(value.buildVersion || ''))) throw new Error('Canary build version is invalid');
        if (Number(value.minimumLoaderVersion) > LOADER_VERSION) throw new Error('Canary requires a newer loader');
        if (!value.bundle || typeof value.bundle !== 'object') throw new Error('Canary bundle declaration is missing');
        if (!String(value.bundle.url || '').startsWith(EXPECTED_BUNDLE_PREFIX)) throw new Error('Canary bundle origin is not authorised');
        if (!/^[0-9a-f]{64}$/u.test(String(value.bundle.sha256 || ''))) throw new Error('Canary bundle hash is invalid');
        if (!Number.isInteger(value.bundle.bytes) || value.bundle.bytes < 100000 || value.bundle.bytes > 4000000) throw new Error('Canary bundle size is outside policy');
        return value;
    }

    function toolkitStorageSnapshot() {
        const values = {};
        try {
            for (let index = 0; index < pageWindow.localStorage.length; index += 1) {
                const key = pageWindow.localStorage.key(index);
                if (!key || (!key.startsWith('mc_map_command_toolkit_') && !key.startsWith('mcms_'))) continue;
                values[key] = pageWindow.localStorage.getItem(key);
            }
        } catch (error) {}
        return { schemaVersion: 1, capturedAt: new Date().toISOString(), values };
    }

    async function ensureBackup() {
        const existing = await gmRead(KEYS.backup, null);
        if (existing?.schemaVersion === 1 && existing.values && typeof existing.values === 'object') return existing;
        const backup = toolkitStorageSnapshot();
        await gmWrite(KEYS.backup, backup);
        return backup;
    }

    async function restoreBackup() {
        const backup = await gmRead(KEYS.backup, null);
        if (!backup?.values || typeof backup.values !== 'object') throw new Error('No canary settings backup exists');
        const remove = [];
        for (let index = 0; index < pageWindow.localStorage.length; index += 1) {
            const key = pageWindow.localStorage.key(index);
            if (key && (key.startsWith('mc_map_command_toolkit_') || key.startsWith('mcms_'))) remove.push(key);
        }
        remove.forEach(key => pageWindow.localStorage.removeItem(key));
        Object.entries(backup.values).forEach(([key, value]) => {
            if (typeof value === 'string') pageWindow.localStorage.setItem(key, value);
        });
    }

    function ready(callback) {
        if (document.body) callback();
        else document.addEventListener('DOMContentLoaded', callback, { once: true });
    }

    function showStatus(status, detail, buildId = '') {
        ready(() => {
            document.getElementById('mcms-canary-loader-status')?.remove();
            const bar = document.createElement('aside');
            bar.id = 'mcms-canary-loader-status';
            bar.setAttribute('data-state', status);
            bar.style.cssText = 'position:fixed;z-index:2147483647;left:12px;bottom:12px;display:flex;align-items:center;gap:8px;max-width:min(94vw,760px);padding:8px 10px;border:1px solid rgba(255,207,77,.72);border-left:4px solid #d11f32;border-radius:7px;background:rgba(12,14,16,.97);box-shadow:0 10px 34px rgba(0,0,0,.5);color:#f7f3e7;font:800 11px/1.3 system-ui,sans-serif';
            const copy = document.createElement('span');
            copy.style.cssText = 'min-width:0;flex:1';
            copy.textContent = `CANARY ${buildId ? `· ${buildId} · ` : '· '}${detail}`;
            const button = (label, action) => {
                const node = document.createElement('button');
                node.type = 'button';
                node.textContent = label;
                node.style.cssText = 'min-height:28px;padding:0 8px;border:1px solid rgba(255,255,255,.18);border-radius:5px;background:#292d30;color:#fff;font:800 10px system-ui,sans-serif;cursor:pointer';
                node.addEventListener('click', action);
                return node;
            };
            const toggle = button(enabled ? 'Pause canary' : 'Enable canary', async () => {
                await gmWrite(KEYS.enabled, !enabled);
                location.reload();
            });
            const refresh = button('Refresh', () => location.reload());
            const restore = button('Restore settings', async () => {
                if (!pageWindow.confirm('Restore the local Toolkit settings captured before Canary was first used?')) return;
                try {
                    await restoreBackup();
                    await gmWrite(KEYS.enabled, false);
                    location.reload();
                } catch (error) {
                    copy.textContent = `CANARY · ${error.message || error}`;
                }
            });
            bar.append(copy, refresh, toggle, restore);
            document.body.append(bar);
        });
    }

    async function verifiedRemoteCandidate() {
        const manifestText = await requestText(MANIFEST_URL);
        const manifest = validateManifest(JSON.parse(manifestText));
        const bundle = await requestText(manifest.bundle.url);
        const digest = await sha256(bundle);
        if (digest !== manifest.bundle.sha256) throw new Error('Canary SHA-256 verification failed');
        if (new TextEncoder().encode(bundle).length !== manifest.bundle.bytes) throw new Error('Canary byte length verification failed');
        const cache = { schemaVersion: 1, cachedAt: new Date().toISOString(), manifest, bundle };
        await gmWrite(KEYS.cache, cache);
        return { ...cache, source: 'network' };
    }

    async function verifiedCachedCandidate() {
        const cache = await gmRead(KEYS.cache, null);
        if (!cache || cache.schemaVersion !== 1 || typeof cache.bundle !== 'string') throw new Error('No verified canary cache exists');
        const manifest = validateManifest(cache.manifest);
        if (await sha256(cache.bundle) !== manifest.bundle.sha256) throw new Error('Cached canary hash is invalid');
        return { ...cache, source: 'cache' };
    }

    function executeCandidate(candidate) {
        const previous = pageWindow.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__;
        try { previous?.destroy?.('replaced by verified maintainer canary'); } catch (error) {}
        pageWindow.__MCMS_CANARY_LOADER__ = Object.freeze({
            loaderVersion: LOADER_VERSION,
            buildId: candidate.manifest.buildId,
            source: candidate.source,
        });
        const execute = new Function(`${candidate.bundle}\n//# sourceURL=${candidate.manifest.bundle.url}`);
        execute();
        hiddenStyle.remove();
        showStatus('running', `${candidate.source === 'cache' ? 'cached fallback' : 'hash verified'} · ${candidate.manifest.buildVersion}`, candidate.manifest.buildId);
    }

    async function boot() {
        enabled = (await gmRead(KEYS.enabled, true)) !== false;
        if (!enabled) {
            hiddenStyle.remove();
            showStatus('paused', 'stable Toolkit active');
            return;
        }
        (document.head || document.documentElement).append(hiddenStyle);
        await ensureBackup();
        try {
            executeCandidate(await verifiedRemoteCandidate());
        } catch (networkError) {
            try {
                executeCandidate(await verifiedCachedCandidate());
            } catch (cacheError) {
                hiddenStyle.remove();
                showStatus('error', `stable Toolkit retained · ${networkError.message || networkError}`);
            }
        }
    }

    void boot();
})();
