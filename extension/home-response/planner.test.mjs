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
test('gap search recovers positions missed by the first grid without relaxing spacing',()=>{
 const options={geometry:circle([-2.63,53.54],5),spacingMiles:4,existing:[[-2.63,53.54]]};
 const first=plan({...options,fillGaps:false}),filled=plan(options);
 assert.equal(first.count,0);assert.ok(filled.count>=3);assert.equal(filled.gapAdded,filled.count);assert.ok(filled.existingBlocked>0);
 for(let i=0;i<filled.count;i++)for(const q of [...options.existing,...filled.sites.slice(0,i)])assert.ok(distanceMiles(filled.sites[i],q)>=4);
});
test('corrected horizontal grid preserves adjacent candidates at requested distance',()=>{
 const g={type:'Polygon',coordinates:[[[-3,54],[-2.7,54],[-2.7,54.001],[-3,54.001],[-3,54]]]};
 const result=plan({geometry:g,spacingMiles:1,fillGaps:false});
 result.sites.sort((a,b)=>a[0]-b[0]);assert.ok(result.count>=12);for(let i=1;i<result.count;i++){const miles=distanceMiles(result.sites[i-1],result.sites[i]);assert.ok(miles>=1&&miles<1.01);}
});
test('fine search finds narrow dry gaps between the original sample rows',()=>{
 const dy=3/3958.7613*180/Math.PI*1.002*Math.sqrt(3)/2;
 const geometry={type:'Polygon',coordinates:[[[-3,54],[-2.7,54],[-2.7,54.1],[-3,54.1],[-3,54]]]};
 const y=54+dy*.25,landGeometry={type:'Polygon',coordinates:[[[-3,y-.0001],[-2.7,y-.0001],[-2.7,y+.0001],[-3,y+.0001],[-3,y-.0001]]]};
 const p=plan({geometry,landGeometry,spacingMiles:3});assert.ok(p.count>0);assert.equal(p.gapAdded,p.count);
 p.sites.forEach(site=>assert.ok(contains(landGeometry,site)));
});

test('a 20-building cap spreads proposals across the area instead of filling the south first',()=>{
 const geometry=circle([-2.59,51.45],7),p=plan({geometry,spacingMiles:1,maxBuildings:20});
 assert.equal(p.count,20);assert.equal(p.limitReached,true);
 for(const north of [false,true])for(const east of [false,true])assert.ok(p.sites.some(([x,y])=>(y>=51.45)===north&&(x>=-2.59)===east));
 assert.ok(Math.max(...p.sites.map(p=>p[1]))-Math.min(...p.sites.map(p=>p[1]))>.12);
});
