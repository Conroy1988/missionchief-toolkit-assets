import test from 'node:test';
import assert from 'node:assert/strict';
import {plan,circle,contains,distanceMiles,SPACING_MILES} from './planner.mjs';
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
