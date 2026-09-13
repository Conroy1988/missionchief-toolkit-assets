import test from 'node:test';import assert from 'node:assert/strict';import {JSDOM} from 'jsdom';import {nativeAdapter} from './native.mjs';
const dom=new JSDOM('',{url:'https://www.missionchief.co.uk/'});globalThis.DOMParser=dom.window.DOMParser;globalThis.FormData=dom.window.FormData;
function make(responses){const calls=[];const win={location:dom.window.location,fetch:async(url,options)=>{calls.push({url:String(url),options});const data=responses.shift();if(!data)throw Error('Unexpected request');return {ok:true,url:data.url||String(url),text:async()=>typeof data.body==='string'?data.body:JSON.stringify(data.body)};}};return {api:nativeAdapter(win),calls};}
test('partial building catalogue prevents planning',async()=>{const {api}=make([{body:{result:[],pagination:{total:1}}}]);await assert.rejects(api.buildings(),/incomplete/);});
test('account identity must be known',async()=>{const {api}=make([{body:{credits_user_current:50000}}]);await assert.rejects(api.account(),/account/);});
test('native creation uses Credit form and verifies location identity',async()=>{
 const point=[-3.19,55.95],item={point,name:'Test HR'},job={dispatchId:'7'};
 const doc=new DOMParser().parseFromString('<form action="/buildings" method="post"><input name="authenticity_token" value="fixture-only"><input name="build_with_coins" value="1"><input name="build_as_alliance" value="1"><input name="build_another" value="1"></form>','text/html');
 const {api,calls}=make([{url:'https://www.missionchief.co.uk/buildings/99',body:'Created'},{body:{result:[{id:99,building_type:22,latitude:55.95,longitude:-3.19,caption:'Test HR'}]}}]);
 assert.deepEqual(await api.create(item,job,{form:doc.querySelector('form'),cost:10000,commit:'Build 10,000 Credits'}),{id:'99',cost:10000});
 const data=calls[0].options.body;assert.equal(data.get('build_with_coins'),'0');assert.equal(data.get('build_as_alliance'),'0');assert.equal(data.has('build_another'),false);assert.equal(data.get('building[building_type]'),'22');assert.equal(data.get('building[longitude]'),'-3.19');
});
test('changed account stops construction',async()=>{const {api}=make([{body:{user_id:2}}]);await assert.rejects(api.checkAccount('1'),/Account changed/);});
test('full garage prevents vehicle spending',async()=>{const {api,calls}=make([{body:'<p>No available parking</p>'}]);await assert.rejects(api.checkVehicle({buildingId:'99'},{vehicle:{id:3,credits:10000}}),/No free vehicle/);assert.equal(calls.length,1);});
test('form returning without created identity remains inconclusive',async()=>{const {api}=make([{body:'validation failed'},{body:{result:[]}}]);const doc=new DOMParser().parseFromString('<form></form>','text/html');await assert.rejects(api.create({point:[-3,55],name:'HR'},{},{form:doc.querySelector('form'),commit:'Build 10,000 Credits',cost:10000}),/not yet visible/);});
const recovered={id:99,building_type:22,latitude:55.95,longitude:-3.19,caption:'Home Response 1 [saved-run]'};
const savedItem=()=>({state:'creating',point:[-3.19,55.95],name:recovered.caption,reserved:14000});
test('successful creation returning the map is verified using owned buildings',async()=>{
 const {api}=make([{url:'https://www.missionchief.co.uk/',body:'Map'},{body:{result:[recovered]}}]);
 const doc=new DOMParser().parseFromString('<form></form>','text/html');
 assert.deepEqual(await api.create(savedItem(),{},{form:doc.querySelector('form'),cost:10000,commit:'Build 10,000 Credits'}),{id:'99',cost:10000});
});
test('0.23.0 creating checkpoint recovers existing building and its cost without mutation',async()=>{
 const {api,calls}=make([{body:{result:[recovered]}}]);const result=await api.reconcile(savedItem(),{vehicle:{id:10,credits:4000}});
 assert.equal(result.state,'built');assert.equal(result.buildingId,'99');assert.equal(result.cost,10000);assert.equal(calls.length,1);assert.equal(calls[0].options.method,undefined);
});
test('wrong location, duplicates and preexisting IDs cannot become a purchase receipt',async()=>{
 for(const records of [[{...recovered,longitude:-2}],[recovered,{...recovered,id:100}],[]]){
  const {api}=make([{body:{result:records}}]);await assert.rejects(api.reconcile(savedItem(),{vehicle:{id:10,credits:4000}}));
 }
 const {api}=make([{body:{result:[recovered]}}]);await assert.rejects(api.reconcile({...savedItem(),beforeBuildingIds:['99']},{vehicle:{id:10,credits:4000}}));
});
test('completed vehicle request recovers only the requested vehicle in the verified building',async()=>{
 const item={...savedItem(),buildingId:'99',state:'buying',vehicleCost:4000};
 const {api}=make([{body:{result:[recovered]}},{body:[{id:400,building_id:99,vehicle_type:10}]}]);assert.equal((await api.reconcile(item,{vehicle:{id:10,credits:4000}})).state,'complete');
 const wrong=make([{body:{result:[recovered]}},{body:[{id:400,building_id:99,vehicle_type:3}]}]);await assert.rejects(wrong.api.reconcile(item,{vehicle:{id:10,credits:4000}}),/unverified/);
});
