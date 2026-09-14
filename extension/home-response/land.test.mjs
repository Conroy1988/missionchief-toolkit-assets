import test from 'node:test';import assert from 'node:assert/strict';
import {isDryLand} from './land.mjs';import {LAND_GEOMETRY} from './land-data.mjs';import {planAsync} from './planner.mjs';import {nativeAdapter} from './native.mjs';
test('Northern Ireland sea and Lough Neagh excluded; inland cities retained',()=>{
 for(const p of [[-5.2,54.6],[-6.2,55.4],[-6.4,54.63],[-5.5,54]])assert.equal(isDryLand(p),false,JSON.stringify(p));
 for(const p of [[-5.93,54.60],[-6.33,54.18],[-7.32,54.997],[-3.19,55.95],[-.1276,51.5074]])assert.equal(isDryLand(p),true,JSON.stringify(p));
});
test('large maritime-boundary preview contains only dry land',async()=>{
 const geometry={type:'Polygon',coordinates:[[[-8.2,54],[-5,54],[-5,55.5],[-8.2,55.5],[-8.2,54]]]};
 const p=await planAsync({geometry,landGeometry:LAND_GEOMETRY,spacingMiles:3,maxBuildings:1000});assert.ok(p.count>100);assert.ok(p.waterExcluded>100);assert.ok(p.sites.every(isDryLand));
});
test('water in legacy saved plan is skipped before network calls',async()=>{
 const api=nativeAdapter({location:{origin:'https://www.missionchief.co.uk'},fetch:async()=>{throw Error('Must not request');}});
 const r=await api.checkSite({point:[-5.2,54.6]},{spacingMiles:3});assert.match(r.skip,/Water/);
});
