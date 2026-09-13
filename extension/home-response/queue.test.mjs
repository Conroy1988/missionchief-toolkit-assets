import test from 'node:test';import assert from 'node:assert/strict';import {runQueue} from './queue.mjs';
const make=()=>({state:'ready',account:'1',budget:50000,spent:0,items:[{state:'ready'},{state:'ready'}]});
const adapter=(events)=>({checkAccount:async()=>{},checkSite:async()=>({total:12500}),create:async i=>{events.push('create');return {id:events.length,cost:10000};},checkVehicle:async()=>({cost:2500}),buy:async()=>events.push('buy'),verifyVehicle:async()=>true});
test('serial create then buy with durable intent',async()=>{const events=[],job=make();await runQueue(job,adapter(events),{save:async j=>events.push(j.items.map(i=>i.state).join(','))});assert.equal(job.spent,25000);assert.equal(job.state,'complete');assert.ok(events.indexOf('creating,ready')<events.indexOf('create'));});
test('ambiguous creation never retries after reload',async()=>{const job=make(),events=[],api=adapter(events);api.create=async()=>{throw Error('lost response');};await assert.rejects(runQueue(job,api,{save:async()=>{}}));assert.equal(job.items[0].state,'creating');await assert.rejects(runQueue(job,adapter(events),{save:async()=>{}}),/uncertain/);assert.equal(events.length,0);});
test('pause between building and vehicle preserves location',async()=>{const job=make(),events=[];await runQueue(job,adapter(events),{save:async()=>{},stopped:()=>job.items[0].state==='built'});assert.equal(job.items[0].state,'built');assert.deepEqual(events,['create']);await runQueue(job,adapter(events),{save:async()=>{}});assert.deepEqual(events,['create','buy','create','buy']);});
test('budget blocks before spending and no retry on uncertain vehicle purchase',async()=>{const job=make();job.budget=100;const events=[];await assert.rejects(runQueue(job,adapter(events),{save:async()=>{}}),/Budget/);assert.deepEqual(events,[]);const j=make(),a=adapter(events);a.buy=async()=>{throw Error('timeout');};await assert.rejects(runQueue(j,a,{save:async()=>{}}));assert.equal(j.items[0].state,'buying');});
test('legacy creating resume buys vehicle once, never rebuilds and counts cost once',async()=>{
 const job=make();job.items=[{state:'creating',reserved:12500}];const events=[],api=adapter(events);api.reconcile=async()=>({state:'built',buildingId:'99',cost:10000});
 await runQueue(job,api,{save:async()=>{}});assert.deepEqual(events,['buy']);assert.equal(job.spent,12500);assert.equal(job.items[0].buildingId,'99');
 await runQueue(job,api,{save:async()=>{}});assert.deepEqual(events,['buy']);assert.equal(job.spent,12500);
});
test('recovery honours budget before further spending',async()=>{
 const job=make();job.items=[{state:'creating'}];job.budget=10000;const events=[],api=adapter(events);api.reconcile=async()=>({state:'built',buildingId:'99',cost:10000});
 await assert.rejects(runQueue(job,api,{save:async()=>{}}),/Budget/);assert.equal(job.items[0].state,'built');assert.equal(job.spent,10000);assert.deepEqual(events,[]);
});
test('vehicle recovery does not buy twice and preserves the original failure',async()=>{
 const job=make();job.items=[{state:'buying',buildingId:'99',error:'Original timeout'}];job.spent=10000;
 const events=[],api=adapter(events);api.reconcile=async()=>{throw Error('Still not visible');};await assert.rejects(runQueue(job,api,{save:async()=>{}}));assert.equal(job.items[0].error,'Original timeout');
 api.reconcile=async()=>({state:'complete',cost:2500});await runQueue(job,api,{save:async()=>{}});assert.equal(job.spent,12500);assert.deepEqual(events,[]);
});
