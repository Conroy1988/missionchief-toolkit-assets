import test from 'node:test';import assert from 'node:assert/strict';import {createImageBridge} from './images.mjs';
test('picker groups equal pixels across URLs and bounds simultaneous downloads',async()=>{
 const records=Array.from({length:12},(_,i)=>({id:String(i),caption:`Station ${i}`,hasCustomIcon:true,customIconUrl:`https://example.com/${i%8}.png`}));let active=0,max=0,calls=0;
 const bridge=createImageBridge({list:async()=>records,image:async url=>{calls++;max=Math.max(max,++active);await new Promise(r=>setTimeout(r,2));active--;if(url.endsWith('/7.png'))throw Error('Unavailable');return {width:32,height:32,pixelDigest:Number(url.match(/(\d+)\.png/)[1])%2?'odd':'even'};}});
 const result=await bridge.sources();assert.equal(calls,8);assert.equal(max,4);assert.equal(result.icons.length,2);assert.equal(result.unavailable,1);assert.equal(result.icons.reduce((n,i)=>n+i.count,0),11);
});
function fixture(){const source={id:'1',caption:'Source',hasCustomIcon:true,customIconUrl:'https://example.com/icon.png'},target={id:'2',caption:'New home',typeId:22,longitude:-3.19,latitude:55.95,dispatchId:'4',small:false};let digest='a';const calls=[];const deps={list:async()=>[source],building:async id=>String(id)==='1'?source:target,image:async()=>({pixelDigest:digest,width:32,height:32}),apply:async(...args)=>calls.push(args)};return {deps,target,calls,setDigest:d=>digest=d,item:{buildingId:'2',name:'New home',point:[-3.19,55.95]}};}
test('copies verified source through existing copier with precise target identity',async()=>{const f=fixture(),bridge=createImageBridge(f.deps),imageSource=await bridge.prepare('1');await bridge.copy(f.item,{imageSource});assert.equal(f.calls.length,1);assert.equal(f.calls[0][0].buildingId,'2');assert.equal(f.calls[0][0].dispatchId,'4');assert.equal(f.calls[0][2].pixelDigest,'a');});
test('changed source after reload and wrong target both stop image changes',async()=>{const f=fixture(),first=createImageBridge(f.deps),imageSource=await first.prepare('1');f.setDigest('b');await assert.rejects(createImageBridge(f.deps).copy(f.item,{imageSource}),/source image has changed/);f.setDigest('a');f.target.typeId=7;await assert.rejects(first.copy(f.item,{imageSource}),/identity changed/);assert.equal(f.calls.length,0);});
test('saved icons survive a new bridge without list or image scans, isolated by account and type',async()=>{
 const data=new Map(),storage={getItem:k=>data.get(k),setItem:(k,v)=>data.set(k,v)};let account='1',downloads=0,lists=0;
 const deps={storage,scope:async()=>account,list:async()=>{lists++;return [{id:'1',caption:'Home',typeId:22,hasCustomIcon:true,customIconUrl:'https://example.com/home.png'},{id:'2',caption:'Fire',typeId:0,hasCustomIcon:true,customIconUrl:'https://example.com/fire.png'}];},image:async()=>{downloads++;return {width:32,height:32,pixelDigest:'a'};}};
 const result=await createImageBridge(deps).sources({typeId:'22'});assert.equal(result.persisted,true);assert.equal(await createImageBridge(deps).lastType(),'22');assert.equal(downloads,1);assert.equal(result.icons[0].caption,'Home');
 const restored=await createImageBridge(deps).saved({typeId:22});assert.equal(restored.icons.length,1);assert.equal(downloads,1);assert.equal(lists,1);assert.equal(await createImageBridge(deps).saved({typeId:0}),null);
 account='2';assert.equal(await createImageBridge(deps).saved({typeId:22}),null);
});
test('failed cache writes still return scanned icons and corrupted caches can be refreshed',async()=>{
 const f=fixture(),bridge=createImageBridge({...f.deps,scope:async()=>1,storage:{getItem:()=>'{broken',setItem:()=>{throw Error('Quota');}}});
 assert.equal(await bridge.saved(),null);const result=await bridge.sources();assert.equal(result.persisted,false);assert.equal(result.icons.length,1);
});
