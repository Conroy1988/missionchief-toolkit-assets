import test from 'node:test';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(new URL('../home-response/package.json',import.meta.url));const {JSDOM}=require('jsdom');
const flush=()=>new Promise(r=>setTimeout(r,10));
test('Operations panel selects individual hospitals, previews costs and confirms upgrades',async()=>{
 const dom=new JSDOM('<div id="grid"></div>',{url:'https://www.missionchief.co.uk'});const w=dom.window;
 for(const name of ['window','document','localStorage','Option'])globalThis[name]=w[name];
 Object.defineProperty(globalThis,'navigator',{configurable:true,value:{locks:{request:async(name,options,fn)=>fn({name})}}});
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
 const {mountHospitals,configureHospitals,destroyHospitals}=await import('./ui.mjs');let level=0,writes=0;
 configureHospitals({account:async()=>({user_id:7,credits_user_current:10000}),list:async()=>[{id:'1',typeId:'4',caption:'Test Hospital',level},{id:'2',typeId:'0',caption:'Fire station',level:0}],inspect:async()=>({record:{level},operation:{priceCredits:100}}),apply:async()=>{level++;writes++;},exclusive:async fn=>fn()});
 mountHospitals(w.document.querySelector('#grid'));w.document.querySelector('[data-hospital-upgrades]').click();await flush();
 const q=s=>w.document.querySelector(s);assert.equal(q('[data-target]').options.length,31);q('[data-scan]').click();await flush();assert.equal(q('tbody').rows.length,1);
 q('[data-target]').value='2';q('[data-target]').dispatchEvent(new w.Event('change'));q('[data-preview]').click();await flush();assert.match(q('[data-status]').textContent,/200 Credits/);
 w.confirm=text=>{assert.match(text,/Your available balance: 10,000 Credits/);assert.match(text,/Upgrade plan spending limit: 200 Credits/);return false;};q('[data-run]').click();await flush();assert.equal(writes,0);
 w.confirm=()=>true;q('[data-run]').click();await flush();assert.equal(writes,2);assert.match(q('[data-status]').textContent,/1\/1 hospitals at target/);
 q('[data-close]').click();assert.equal(q('dialog').open,false);q('[data-hospital-upgrades]').click();assert.equal(q('dialog').open,true);destroyHospitals();w.close();
});
