#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
function extractFunction(name) {
    const marker = `    function ${name}(`;
    const start = source.indexOf(marker);
    assert.ok(start >= 0, `${name} missing`);
    const open = source.indexOf('{', start);
    let depth = 0, quote = '', escaped = false;
    for (let index = open; index < source.length; index += 1) {
        const char = source[index];
        if (quote) {
            if (escaped) escaped = false;
            else if (char === '\\') escaped = true;
            else if (char === quote) quote = '';
            continue;
        }
        if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
        if (char === '{') depth += 1;
        if (char === '}' && --depth === 0) return source.slice(start, index + 1);
    }
    throw new Error(`Could not extract ${name}`);
}
const functions = ['majorIncidentFeedEntryCount','majorIncidentFeedInteractionActive','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedScheduleAdvance','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance'];
function classList() { return { values:new Set(), toggle(name,on){ if(on)this.values.add(name); else this.values.delete(name); }, contains(name){ return this.values.has(name); }, add(name){this.values.add(name);}, remove(name){this.values.delete(name);} }; }
function button(action) { return { action, disabled:false, attrs:{}, textContent:'', title:'', setAttribute(name,value){this.attrs[name]=String(value);} }; }
const items = Array.from({length:3}, (_,index)=>({ index, attrs:{}, tabIndex:0, setAttribute(name,value){this.attrs[name]=String(value);} }));
const track = { style:{ values:{}, setProperty(name,value){this.values[name]=String(value);}, removeProperty(name){delete this.values[name];} }, querySelectorAll(selector){ return selector === '.mcms-incident-feed-item' ? items : []; } };
const counter = { textContent:'' };
const panel = { hidden:true };
const controls = { previous:button('previous'), pause:button('pause'), next:button('next'), expand:button('expand') };
const feed = {
    isConnected:true, dataset:{mcmsEntryCount:'3'}, classList:classList(),
    querySelector(selector) {
        if (selector === '.mcms-incident-feed-track') return track;
        if (selector === '.mcms-incident-feed-count') return counter;
        if (selector === '.mcms-incident-feed-panel') return panel;
        const match = selector.match(/data-mcms-incident-action="([^"]+)"/);
        return match ? controls[match[1]] : null;
    },
    querySelectorAll(selector) { return selector.includes('previous') ? [controls.previous, controls.next] : []; }
};
let timers = [], cleared = [];
const sandbox = {
    console, Date, Math, Number, Boolean, String,
    document:{ hidden:false },
    pageWindow:{ matchMedia:()=>({matches:false}) },
    state:{ economyMode:false },
    MAJOR_INCIDENT_FEED_ROTATION_MS:6500,
    MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS:9000,
    majorIncidentFeedMotionTimer:null,
    majorIncidentFeedMotionRevision:0,
    majorIncidentFeedCurrentIndex:0,
    majorIncidentFeedManualPaused:false,
    majorIncidentFeedInteractionPauseUntil:0,
    majorIncidentFeedExpanded:false,
    runtimeClearTimeout:id=>cleared.push(id),
    runtimeSetTimeout:(callback,delay)=>{ timers.push({callback,delay}); return timers.length; }
};
vm.createContext(sandbox);
vm.runInContext(`${functions.map(extractFunction).join('\n\n')}\nthis.api={${functions.join(',')},state:()=>({index:majorIncidentFeedCurrentIndex,paused:majorIncidentFeedManualPaused,expanded:majorIncidentFeedExpanded,pauseUntil:majorIncidentFeedInteractionPauseUntil})};`, sandbox);
const api = sandbox.api;
assert.equal(api.majorIncidentFeedEntryCount(feed), 3);
assert.equal(api.majorIncidentFeedApplyIndex(feed, 1), true);
assert.equal(track.style.values.transform, 'translate3d(-100%,0,0)');
assert.equal(counter.textContent, '2 / 3');
assert.equal(items[1].attrs['aria-hidden'], 'false');
assert.equal(items[0].tabIndex, -1);
assert.equal(api.majorIncidentFeedAdvance(feed, 1, true), true);
assert.equal(api.state().index, 2);
assert.ok(api.state().pauseUntil > Date.now());
assert.equal(track.style.values.transform, 'translate3d(-200%,0,0)');
api.majorIncidentFeedSetPaused(feed, true);
assert.equal(api.state().paused, true);
assert.equal(controls.pause.attrs['aria-pressed'], 'true');
assert.equal(controls.pause.textContent, '▶');
feed.classList.add('mcms-feed-interacting');
api.majorIncidentFeedSetPaused(feed, false);
assert.equal(controls.pause.textContent, 'Ⅱ');
assert.equal(api.state().pauseUntil, 0);
assert.equal(feed.classList.contains('mcms-feed-interacting'), false);
const resumeTimer = timers.at(-1);
assert.equal(resumeTimer.delay, 650);
const resumeIndex = api.state().index;
resumeTimer.callback();
assert.equal(api.state().index, (resumeIndex + 1) % 3);
assert.equal(timers.at(-1).delay, 6500);
api.majorIncidentFeedSetExpanded(feed, true);
assert.equal(api.state().expanded, true);
assert.equal(panel.hidden, false);
assert.equal(controls.expand.attrs['aria-expanded'], 'true');
api.majorIncidentFeedSetExpanded(feed, false);
assert.equal(panel.hidden, true);
feed.dataset.mcmsEntryCount = '1';
api.majorIncidentFeedSyncControls(feed);
assert.equal(controls.previous.disabled, true);
assert.equal(controls.next.disabled, true);
console.log('Issue #517 Incident Command Wire runtime contract passed.');
