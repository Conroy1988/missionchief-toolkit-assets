import test from 'node:test';import assert from 'node:assert/strict';import {runQueue} from './queue.mjs';
const make=()=>({state:'ready',account:'1',budget:50000,spent:0,items:[{state:'ready'},{state:'ready'}]});
const adapter=(events)=>({checkAccount:async()=>{},checkSite:async()=>({total:12500}),create:async i=>{events.push('create');return {id:events.length,cost:10000};},checkVehicle:async()=>({cost:2500}),buy:async()=>events.push('buy'),verifyVehicle:async()=>true});
test('serial create then buy with durable intent',async()=>{const events=[],job=make();await runQueue(job,adapter(events),{save:async j=>events.push(j.items.map(i=>i.state).join(','))});assert.equal(job.spent,25000);assert.equal(job.state,'complete');assert.ok(events.indexOf('creating,ready')<events.indexOf('create'));});
test('ambiguous creation never retries after reload',async()=>{const job=make(),events=[],api=adapter(events);api.create=async()=>{throw Error('lost response');};await assert.rejects(runQueue(job,api,{save:async()=>{}}));assert.equal(job.items[0].state,'creating');await assert.rejects(runQueue(job,adapter(events),{save:async()=>{}}),/uncertain/);assert.equal(events.length,0);});
test('pause between building and vehicle preserves location',async()=>{const job=make(),events=[];await runQueue(job,adapter(events),{save:async()=>{},stopped:()=>job.items[0].state==='built'});assert.equal(job.items[0].state,'built');assert.deepEqual(events,['create']);await runQueue(job,adapter(events),{save:async()=>{}});assert.deepEqual(events,['create','buy','create','buy']);});
test('legacy budget does not block and uncertain vehicle purchase remains paused',async()=>{const job=make();job.budget=100;const events=[];await runQueue(job,adapter(events),{save:async()=>{}});assert.equal(job.spent,25000);assert.equal(job.state,'complete');const j=make(),a=adapter(events);a.buy=async()=>{throw Error('timeout');};await assert.rejects(runQueue(j,a,{save:async()=>{}}));assert.equal(j.items[0].state,'buying');});
test('legacy creating resume buys vehicle once, never rebuilds and counts cost once',async()=>{
 const job=make();job.items=[{state:'creating',reserved:12500}];const events=[],api=adapter(events);api.reconcile=async()=>({state:'built',buildingId:'99',cost:10000});
 await runQueue(job,api,{save:async()=>{}});assert.deepEqual(events,['buy']);assert.equal(job.spent,12500);assert.equal(job.items[0].buildingId,'99');
 await runQueue(job,api,{save:async()=>{}});assert.deepEqual(events,['buy']);assert.equal(job.spent,12500);
});
test('recovery ignores the removed legacy spending cap',async()=>{
 const job=make();job.items=[{state:'creating'}];job.budget=10000;const events=[],api=adapter(events);api.reconcile=async()=>({state:'built',buildingId:'99',cost:10000});
 await runQueue(job,api,{save:async()=>{}});assert.equal(job.items[0].state,'complete');assert.equal(job.spent,12500);assert.deepEqual(events,['buy']);
});
test('vehicle recovery does not buy twice and preserves the original failure',async()=>{
 const job=make();job.items=[{state:'buying',buildingId:'99',error:'Original timeout'}];job.spent=10000;
 const events=[],api=adapter(events);api.reconcile=async()=>{throw Error('Still not visible');};await assert.rejects(runQueue(job,api,{save:async()=>{}}));assert.equal(job.items[0].error,'Original timeout');
 api.reconcile=async()=>({state:'complete',cost:2500});await runQueue(job,api,{save:async()=>{}});assert.equal(job.spent,12500);assert.deepEqual(events,[]);
});

test('image failure resumes only copying, never another purchase',async()=>{
 const job=make(),events=[],api=adapter(events);job.items=[{state:'ready'}];job.imageSource={id:'4'};api.copyImage=async()=>{events.push('image');throw Error('Image response lost');};
 await assert.rejects(runQueue(job,api,{save:async()=>{}}),/Image response lost/);assert.equal(job.items[0].state,'complete');assert.equal(job.state,'paused');
 api.copyImage=async()=>events.push('image');await runQueue(job,api,{save:async()=>{}});assert.deepEqual(events,['create','buy','image','image']);assert.equal(job.spent,12500);assert.equal(job.items[0].imageDone,true);assert.equal(job.state,'complete');
});
test('insufficient account credits still stop before purchase',async()=>{const job=make(),events=[],api=adapter(events);delete job.budget;api.checkSite=async()=>{throw Error('Insufficient Credits');};await assert.rejects(runQueue(job,api,{save:async()=>{}}),/Insufficient/);assert.deepEqual(events,[]);});
test('native validated purchase checks avoid redundant account reads while recovery still checks',async()=>{
 const job=make(),api=adapter([]);let checks=0;api.validatesPurchaseAccount=true;api.checkAccount=async()=>checks++;
 await runQueue(job,api,{save:async()=>{}});assert.equal(checks,0);assert.ok(job.items.every(i=>Object.keys(i.timings).length===5&&Object.values(i.timings).every(n=>Number.isFinite(n)&&n>=0)));
 const resumed=make();resumed.items=[{state:'creating'}];api.reconcile=async()=>({state:'complete',cost:10000});await runQueue(resumed,api,{save:async()=>{}});assert.equal(checks,1);
});
