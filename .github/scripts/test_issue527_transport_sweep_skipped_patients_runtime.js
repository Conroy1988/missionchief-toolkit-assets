#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const signatureEnd=source.indexOf(') {',start);assert.ok(signatureEnd>=0);const open=signatureEnd+2;let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const logs=[];let renders=0;const runtime={cleared:0,skipped:0,processed:0,errors:0,confirmedReleaseKeys:new Set(),skippedPatientKeys:new Set(),missionIndex:2,missionTotal:4,completedMissionCount:1};
const sandbox={console,String,Math,transportSweepRuntime:runtime,transportSweepLog:(message,level)=>logs.push({message,level}),renderTransportSweepPanel:()=>{renders+=1;}};vm.createContext(sandbox);vm.runInContext(`${extractFunction('recordTransportSweepSkippedPatient')}\nthis.recordTransportSweepSkippedPatient=recordTransportSweepSkippedPatient;`,sandbox);const record=sandbox.recordTransportSweepSkippedPatient;
assert.equal(record('101:201','Skipped patient one'),true);assert.equal(runtime.skipped,1);assert.equal(runtime.processed,1);assert.equal(renders,1);assert.equal(logs.length,1);
assert.equal(record('101:201','Duplicate patient one'),false);assert.equal(runtime.skipped,1);assert.equal(runtime.processed,1);assert.equal(renders,1);assert.equal(logs.length,1);
assert.equal(record('101:202','Skipped patient two'),true);assert.equal(runtime.skipped,2);assert.equal(runtime.processed,2);assert.equal(renders,2);
runtime.confirmedReleaseKeys.add('101:203');assert.equal(record('101:203','Must not skip a confirmed release'),false);assert.equal(runtime.skipped,2);assert.equal(runtime.processed,2);assert.equal(renders,2);
assert.equal(record('','No identity'),false);assert.equal(runtime.skipped,2);assert.equal(runtime.missionIndex,2);assert.equal(runtime.missionTotal,4);assert.equal(runtime.completedMissionCount,1);
console.log('Issue #527 skipped-patient runtime contract passed.');
