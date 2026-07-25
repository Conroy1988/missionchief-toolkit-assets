#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const open=source.indexOf('{',start);let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const functions=['majorIncidentFeedEntryCount','majorIncidentFeedSyncControls','majorIncidentFeedAnimation','majorIncidentFeedSyncReelState','majorIncidentFeedApplyIndex','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance'];
function classList(){return{values:new Set(),toggle(n,on){if(on)this.values.add(n);else this.values.delete(n);},contains(n){return this.values.has(n);},add(n){this.values.add(n);},remove(n){this.values.delete(n);}};}
function button(){return{disabled:false,attrs:{},textContent:'',title:'',setAttribute(n,v){this.attrs[n]=String(v);}};}
const animation={animationName:'mcmsIncidentWireReel',currentTime:0,playState:'running',effect:{getTiming:()=>({duration:12000})},play(){this.playState='running';},pause(){this.playState='paused';}};
const track={getAnimations:()=>[animation]};const counter={textContent:''};const panel={hidden:true};const controls={previous:button(),pause:button(),next:button(),expand:button()};
const feed={isConnected:true,dataset:{mcmsEntryCount:'3'},classList:classList(),querySelector(selector){if(selector==='.mcms-incident-feed-track')return track;if(selector==='.mcms-incident-feed-count')return counter;if(selector==='.mcms-incident-feed-panel')return panel;const m=selector.match(/data-mcms-incident-action="([^"]+)"/);return m?controls[m[1]]:null;},querySelectorAll(selector){return selector.includes('previous')?[controls.previous,controls.next]:[];}};
const sandbox={console,Date,Math,Number,Boolean,String,document:{hidden:false},state:{economyMode:false},majorIncidentFeedCurrentIndex:0,majorIncidentFeedManualPaused:false,majorIncidentFeedExpanded:false};
vm.createContext(sandbox);vm.runInContext(`${functions.map(extractFunction).join('\n\n')}\nthis.api={${functions.join(',')},state:()=>({index:majorIncidentFeedCurrentIndex,paused:majorIncidentFeedManualPaused,expanded:majorIncidentFeedExpanded})};`,sandbox);const api=sandbox.api;
assert.equal(api.majorIncidentFeedEntryCount(feed),3);api.majorIncidentFeedSyncControls(feed);assert.equal(counter.textContent,'3 LIVE');
api.majorIncidentFeedSetPaused(feed,true);assert.equal(animation.playState,'paused');assert.equal(controls.pause.textContent,'▶');
api.majorIncidentFeedSetPaused(feed,false);assert.equal(animation.playState,'running');assert.equal(controls.pause.textContent,'Ⅱ');
assert.equal(api.majorIncidentFeedAdvance(feed,1,true),true);assert.equal(animation.currentTime,4000);
assert.equal(api.majorIncidentFeedAdvance(feed,-1,true),true);assert.equal(animation.currentTime,0);
api.majorIncidentFeedSetExpanded(feed,true);assert.equal(panel.hidden,false);assert.equal(animation.playState,'paused');
api.majorIncidentFeedSetExpanded(feed,false);assert.equal(panel.hidden,true);assert.equal(animation.playState,'running');
feed.classList.add('mcms-feed-interacting');api.majorIncidentFeedSyncReelState(feed);assert.equal(animation.playState,'paused');feed.classList.remove('mcms-feed-interacting');api.majorIncidentFeedSyncReelState(feed);assert.equal(animation.playState,'running');
console.log('Issue #519 continuous Incident Command Wire reel runtime contract passed.');
