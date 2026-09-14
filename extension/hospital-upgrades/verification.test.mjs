import {execFileSync} from 'node:child_process';
import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import {readFileSync} from 'node:fs';
function fixture({afterLevel=30,readError=false,scopeError=false}={}){
 const source=execFileSync('python3',['-c','import sys,zipfile;sys.stdout.buffer.write(zipfile.ZipFile(sys.argv[1]).read(sys.argv[2]))',new URL('../../.dev/MissionChief-Toolkit-Extension-1.2.5.zip',import.meta.url).pathname,'features/administration.js'],{encoding:'utf8',maxBuffer:10000000});
 const start=source.indexOf('"applyExpansionPlannerOperation":')+'"applyExpansionPlannerOperation":'.length;
 const end=source.indexOf(',\n"startExpansionPlanner":',start);
 assert.ok(start>30&&end>start);
 const factory=vm.runInNewContext('('+source.slice(start,end)+')',{Number});
 let reads=0,pages=0,writes=0,scopes=0;
 const item={buildingId:'1',name:'Cameron Hospital',typeId:'4',kind:'level',actionSuffix:'expand_do/credits',level:0,hospitalTargetLevel:30,priceCredits:300,extensionDigest:'same'};
 const context={Promise,runtime:{},expansionPlannerRuntime:{},fetchExpansionPlannerBuilding:async()=>{reads++;if(reads>1&&readError)throw Error('HTTP 503');return {id:'1',typeId:'4',level:reads===1?0:afterLevel};},fetchExpansionPlannerRevalidationPages:async()=>{pages++;if(pages>1)throw Error('Maximum-level expansion page redirected');return {detailPage:{doc:{}},operationPage:{doc:{}}};},expansionPlannerAssertScope:(record,item,after)=>{scopes++;if(after&&scopeError)throw Error('Ownership changed');},expansionPlannerExtensionDigest:()=> 'same',expansionPlannerHasPendingConstruction:()=>false,expansionPlannerFindCurrentAction:()=>({priceCredits:300}),expansionPlannerSafetyStop:s=>Error(s),prepareExpansionPlannerSubmission:()=>({}),submitExpansionPlannerOperation:async()=>{writes++;},runtimeDelay:async()=>true};
 return {run:()=>factory(context)(item,300),counts:()=>({reads,pages,writes,scopes})};
}
test('maximum hospital target verifies without fetching vanished expansion page',async()=>{const f=fixture();const result=await f.run();assert.equal(result.record.level,30);assert.deepEqual(f.counts(),{reads:2,pages:1,writes:1,scopes:2});});
test('unreadable post-purchase level retains the read error and never retries purchase',async()=>{const f=fixture({readError:true});await assert.rejects(f.run(),/HTTP 503.*Review & resume/);assert.equal(f.counts().writes,1);});
test('wrong level or changed ownership cannot pass target verification',async()=>{for(const opts of [{afterLevel:1},{scopeError:true}]){const f=fixture(opts);await assert.rejects(f.run(),/expected 30|Ownership changed/);assert.equal(f.counts().writes,1);}});
