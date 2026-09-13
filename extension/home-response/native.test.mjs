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
test('form returning without created identity remains inconclusive',async()=>{const {api}=make([{body:'validation failed'}]);const doc=new DOMParser().parseFromString('<form></form>','text/html');await assert.rejects(api.create({point:[-3,55],name:'HR'},{},{form:doc.querySelector('form'),commit:'Build 10,000 Credits',cost:10000}),/inconclusive/);});
