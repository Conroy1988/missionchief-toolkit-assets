import test from 'node:test';
import assert from 'node:assert/strict';
import {iconKey,iconScope,iconTarget,scanIcons,runIconReplacement,previewIconMatches} from './core.mjs';
const image=d=>({width:50,height:50,pixelDigest:d});
const record=(id,url='old')=>({id,caption:`Station ${id}`,typeId:'4',dispatchId:'7',small:false,latitude:55,longitude:-3,hasCustomIcon:true,customIconUrl:url});
function fixture(){
 const records=new Map([[1,record(1)],[2,record(2)],[9,record(9,'new')]]),writes=[];
 const api={account:async()=>({user_id:12}),busy:()=>false,building:async id=>records.get(id),image:async url=>image(url),apply:async(item,plan,data)=>{assert.equal(iconKey(plan.expectedIcon),iconKey(image('old')));writes.push(item.buildingId);records.get(item.buildingId).customIconUrl=data.pixelDigest;}};
 const job={schema:1,account:'12',from:iconKey(image('old')),to:iconKey(image('new')),sourceId:9,state:'ready',items:[1,2].map(id=>({...iconTarget(records.get(id)),state:'pending'}))};
 return {api,job,records,writes};
}
test('scan deduplicates URLs and groups identical pixels across different URLs',async()=>{
 let calls=0,active=0,peak=0;
 const rows=Array.from({length:12},(_,i)=>record(i,`url${i%6}`));
 const result=await scanIcons({image:async()=>{calls++;active++;peak=Math.max(peak,active);await new Promise(r=>setTimeout(r,2));active--;return image('same');}},rows);
 assert.equal(calls,6);assert.ok(peak<=4);assert.equal(result.groups.length,1);assert.equal(result.groups[0].items.length,12);
});
test('scope includes all or exact types and dispatch assignments',()=>{
 const rows=[record(1),{...record(2),typeId:'22',dispatchId:''}];
 assert.equal(iconScope(rows).length,2);assert.deepEqual(iconScope(rows,'22','0').map(r=>r.id),[2]);assert.equal(iconScope(rows,'4','0').length,0);
});
test('unreadable and default icons cannot become matching targets',async()=>{
 const result=await scanIcons({image:async()=>{throw Error('bad');}},[record(1),{...record(2),hasCustomIcon:false}]);assert.equal(result.groups.length,0);assert.deepEqual(result.unavailable,[1]);
});
test('changed icons are skipped while matching icons are copied with pre-upload expectation',async()=>{
 const f=fixture();f.records.get(2).customIconUrl='other';await runIconReplacement(f.job,f.api,{save:async()=>{}});assert.deepEqual(f.writes,[1]);assert.equal(f.job.items[1].state,'skipped');assert.equal(f.job.state,'complete');
});
test('resume verifies successful uncertain upload without repeating it',async()=>{
 const f=fixture();f.job.items[0].state='writing';f.records.get(1).customIconUrl='new';await runIconReplacement(f.job,f.api,{save:async()=>{}});assert.deepEqual(f.writes,[2]);
});
test('unresolved upload stops without repeating any mutation',async()=>{
 const f=fixture();f.job.items[0].state='writing';await assert.rejects(runIconReplacement(f.job,f.api,{save:async()=>{}}),/uncertain/);assert.equal(f.writes.length,0);
});
test('account, replacement source and target scope drift stop changes',async()=>{
 for(const variant of ['account','source','scope']){const f=fixture();if(variant==='account')f.api.account=async()=>({user_id:13});if(variant==='source')f.records.get(9).customIconUrl='changed';if(variant==='scope')f.records.get(1).dispatchId='8';await assert.rejects(runIconReplacement(f.job,f.api,{save:async()=>{}}));assert.equal(f.writes.length,0);}
});
test('failed checkpoint prevents upload; pause retains pending work',async()=>{
 const f=fixture();await assert.rejects(runIconReplacement(f.job,f.api,{save:async j=>{if(j.items[0].state==='writing')throw Error('storage');}}),/storage/);assert.equal(f.writes.length,0);
 const g=fixture();await runIconReplacement(g.job,g.api,{save:async()=>{},stopped:()=>true});assert.equal(g.job.state,'paused');assert.equal(g.writes.length,0);
});
test('reports an active upload before completion without advancing verified progress',async()=>{
 const f=fixture();f.job.items=f.job.items.slice(0,1);let release;const waiting=new Promise(r=>release=r),stages=[];let updates=0;
 f.api.apply=async()=>waiting;
 const run=runIconReplacement(f.job,f.api,{save:async()=>{},stage:(action,item)=>stages.push([action,item?.name]),progress:()=>updates++});
 await new Promise(r=>setTimeout(r,10));
 assert.deepEqual(stages.at(-1),['Uploading and verifying icon','Station 1']);assert.equal(f.job.items[0].state,'writing');assert.equal(updates,0);
 release();await run;assert.equal(f.job.state,'complete');
});

test('preview reuses scan membership and excludes removed or changed-scope buildings',()=>{
 const original=[record(1),record(2),record(3)];const group={items:original.map(iconTarget)};const current=[original[0],{...original[1],dispatchId:'8'},record(4)];
 assert.deepEqual(previewIconMatches(group,current,'4','7').map(i=>i.buildingId),[1]);
});
