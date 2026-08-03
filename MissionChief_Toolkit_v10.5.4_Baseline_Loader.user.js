// ==UserScript==
// @name         MissionChief Toolkit v10.5.4 Baseline Performance Capture Loader
// @namespace    https://github.com/Conroy1988/missionchief-toolkit-assets/performance-capture/baseline-loader
// @version      10.5.4-capture-loader.2
// @description  Temporary diagnostic loader for the reviewed v10.5.4 authenticated performance capture.
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
// @connect      cdn.jsdelivr.net
// @connect      tkb-gaming.scot
// @run-at       document-start
// ==/UserScript==

(async function loadReviewedBaselineCapture() {
    'use strict';
    const base = 'https://cdn.jsdelivr.net/gh/Conroy1988/missionchief-toolkit-assets@diagnostic-issue687-live-capture-20260803/diagnostic/baseline/';
    const parts = await Promise.all([0, 1, 2, 3, 4].map(async index => {
        const response = await fetch(`${base}part-${index}.b64`, { cache: 'no-store', credentials: 'omit' });
        if (!response.ok) throw new Error(`Baseline capture part ${index} failed: ${response.status}`);
        return (await response.text()).trim();
    }));
    const binary = atob(parts.join(''));
    const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    const source = await new Response(stream).text();
    if (!source.includes('captureSourceSha256: "3b7f344883f9d44980a7a416cba3dfff1d68cfa5571ce9612a9565390fc21a77"')) {
        throw new Error('Baseline capture authority marker missing');
    }
    eval(source);
})().catch(error => console.error('[MCMS baseline capture loader]', error));
