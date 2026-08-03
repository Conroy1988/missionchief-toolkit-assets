// ==UserScript==
// @name         MissionChief Toolkit v10.5.4 Issue 687 Candidate Performance Capture Loader
// @namespace    https://github.com/Conroy1988/missionchief-toolkit-assets/performance-capture/candidate-loader
// @version      10.5.4-issue687-capture-loader.1
// @description  Temporary diagnostic loader for the reviewed Issue 687 performance candidate.
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
// @connect      raw.githubusercontent.com
// @connect      tkb-gaming.scot
// @run-at       document-start
// ==/UserScript==

(async function loadReviewedCandidateCapture() {
    'use strict';
    const base = 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/diagnostic-issue687-live-capture-20260803/diagnostic/candidate/';
    const parts = await Promise.all([0, 1, 2, 3, 4].map(async index => {
        const response = await fetch(`${base}part-${index}.b64`, { cache: 'no-store', credentials: 'omit' });
        if (!response.ok) throw new Error(`Candidate capture part ${index} failed: ${response.status}`);
        return (await response.text()).trim();
    }));
    const binary = atob(parts.join(''));
    const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    const source = await new Response(stream).text();
    if (!source.includes('captureSourceSha256: "7f6697f9fd292dda7e878db036ff1f248c4624428e528c0a42479dc3f064f886"')) {
        throw new Error('Candidate capture authority marker missing');
    }
    eval(source);
})().catch(error => console.error('[MCMS candidate capture loader]', error));
