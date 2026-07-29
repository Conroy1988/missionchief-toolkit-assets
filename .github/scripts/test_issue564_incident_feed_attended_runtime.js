#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const open=source.indexOf('{',start);let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const functions=['majorIncidentFeedMissionAttended','majorIncidentFeedRetainedIndex','majorIncidentFeedEntries'];
const now=Date.parse('2026-07-29T12:00:00Z');
const make=(missionId,sourceName='alliance',units={onScene:0,travelling:0})=>({missionId,caption:`Mission ${missionId}`,source:sourceName,lat:55.95,lng:-3.19,averageCredits:30000,createdAt:now-60000,patientsCount:0,possiblePatientsCount:0,prisonersCount:0,possiblePrisonersCount:0,missingText:'',postcode:'EH1 1AA',address:'Edinburgh EH1 1AA',units});
const sandbox={console,Date,Math,Number,String,Array,Map,
 state:{majorIncidentFeed:{minimumCredits:25000},visibility:{myMissions:true,allianceMissions:true}},
 liveMissionSnapshots:new Map(),missionStuckRecord:()=>null,MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS:10,MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS:10,
 majorIncidentOperationalState:snapshot=>snapshot.units?.travelling?{key:'responding',label:'1 RESPONDING'}:{key:'major',label:'AWAITING RESPONSE'},
 normaliseMissionPostcode:()=>'',MAJOR_INCIDENT_FEED_MAX_ITEMS:20};
vm.createContext(sandbox);vm.runInContext(`${functions.map(extractFunction).join('\n\n')}\nthis.api={${functions.join(',')}};`,sandbox);const api=sandbox.api;
assert.equal(api.majorIncidentFeedMissionAttended(make(1,'alliance',{onScene:0,travelling:1})),false,'responding must remain');
assert.equal(api.majorIncidentFeedMissionAttended(make(1,'alliance',{onScene:1,travelling:0})),true,'personal FMS 4 must suppress');
const waiting=make(1);const responding=make(2,'alliance',{onScene:0,travelling:1});const attended=make(3,'alliance',{onScene:1,travelling:0});const allianceOnly=make(4);allianceOnly.allianceOnScene=8;
sandbox.liveMissionSnapshots=new Map([[1,waiting],[2,responding],[3,attended],[4,allianceOnly]]);
let entries=api.majorIncidentFeedEntries(now);
assert.deepEqual(Array.from(entries,e=>e.snapshot.missionId),[1,2,4],'only personal on-scene attendance suppresses');
attended.units={onScene:0,travelling:0};sandbox.liveMissionSnapshots.set(3,attended);
entries=api.majorIncidentFeedEntries(now);
assert.deepEqual(Array.from(entries,e=>e.snapshot.missionId),[1,2,3,4],'last personal on-scene unit leaving allows one re-entry');
const list=entries.map(entry=>({snapshot:{missionId:entry.snapshot.missionId}}));
assert.equal(api.majorIncidentFeedRetainedIndex(list,'2',1),1,'retained mission follows its new index');
const withoutTwo=list.filter(entry=>entry.snapshot.missionId!==2);
assert.equal(api.majorIncidentFeedRetainedIndex(withoutTwo,'2',1),1,'removed current mission advances to next item');
assert.equal(withoutTwo[1].snapshot.missionId,3);
const withoutLast=list.filter(entry=>entry.snapshot.missionId!==4);
assert.equal(api.majorIncidentFeedRetainedIndex(withoutLast,'4',3),0,'removed final item wraps to first');
assert.equal(api.majorIncidentFeedRetainedIndex([], '1', 4),0);
console.log('Issue #564 runtime passed: personal on-scene exclusion, alliance/responding safety, re-entry and stable next-index behaviour.');
