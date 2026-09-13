import test from 'node:test';
import assert from 'node:assert/strict';
import {planAsync,plan,circle,contains,distanceMiles,SPACING_MILES} from './planner.mjs';
const center=[-3.19,55.95],geometry=circle(center,7);
test('all supported spacing choices produce contained, separated sites',()=>{
 for(const spacingMiles of SPACING_MILES){const existing=[center,[-3.4,55.9]];const p=plan({geometry,spacingMiles,existing});
 for(let i=0;i<p.sites.length;i++){assert.ok(contains(geometry,p.sites[i]));for(const q of [...existing,...p.sites.slice(0,i)])assert.ok(distanceMiles(p.sites[i],q)>=spacingMiles-1e-8);}}
});
test('boundary holes and explicit exclusions receive no proposals',()=>{
 const hole=circle(center,2);const g={type:'Polygon',coordinates:[geometry.coordinates[0],hole.coordinates[0]]};
 for(const s of plan({geometry:g,spacingMiles:1}).sites)assert.ok(!contains(hole,s));
 for(const s of plan({geometry,excluded:[hole],spacingMiles:1}).sites)assert.ok(!contains(hole,s));
});
test('outside buildings still enforce minimum spacing',()=>{
 const preliminary=plan({geometry,spacingMiles:1});const site=preliminary.sites[0];const outside=[site[0],site[1]-0.007];
 const result=plan({geometry,spacingMiles:1,existing:[outside]});result.sites.forEach(p=>assert.ok(distanceMiles(p,outside)>=1-1e-8));
});
test('budget count cap is explicit, malformed data fails closed',()=>{
 const result=plan({geometry,spacingMiles:1,maxBuildings:2});assert.equal(result.count,2);assert.equal(result.limitReached,true);
 assert.throws(()=>plan({geometry,spacingMiles:2}));assert.throws(()=>plan({geometry,spacingMiles:1,existing:[[NaN,2]]}));
});
test('same inputs produce same preview; increasing spacing reduces proposals',()=>{
 assert.deepEqual(plan({geometry,spacingMiles:3}),plan({geometry,spacingMiles:3}));
 assert.ok(plan({geometry,spacingMiles:1}).count>plan({geometry,spacingMiles:6}).count);
});

test('detailed region supports 1000 locations without the old complexity error',async()=>{
 const ring=[];for(let i=0;i<24000;i++){const a=i*Math.PI*2/24000;ring.push([-6+Math.cos(a),54.6+Math.sin(a)*.6]);}ring.push(ring[0]);
 const options={geometry:{type:'Polygon',coordinates:[ring]},spacingMiles:1,maxBuildings:1000};let updates=0;const result=await planAsync(options,{onProgress:()=>updates++});
 assert.equal(result.count,1000);assert.equal(result.limitReached,true);assert.ok(updates>0);assert.deepEqual(result,plan(options));
 assert.throws(()=>plan({...options,maxBuildings:1001}),/1000/);
});
test('async planning can be cancelled between rows',async()=>{let stop=false;await assert.rejects(planAsync({geometry,spacingMiles:1},{onProgress:()=>{stop=true;},cancelled:()=>stop}),/cancelled/);});
