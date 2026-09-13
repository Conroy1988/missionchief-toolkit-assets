import test from 'node:test';import assert from 'node:assert/strict';
import {dispatchAreaCenter,rankedDispatchCentres} from './dispatch.mjs';
test('dispatch centres rank by distance, with invalid coordinates last and names retained',()=>{
 const records=[{id:1,building_type:7,caption:'Far',longitude:-1,latitude:54},{id:2,building_type:7,caption:'Near',longitude:-3.01,latitude:54},{id:3,building_type:22,longitude:-3,latitude:54},{id:4,building_type:7,caption:'Unknown',longitude:null,latitude:null}];
 const list=rankedDispatchCentres(records,[-3,54]);assert.deepEqual(list.map(b=>b.id),['2','1','4']);assert.ok(list[0].miles<1);assert.equal(list[2].point,null);
 assert.deepEqual(rankedDispatchCentres(records,null).map(b=>b.name),['Far','Near','Unknown']);
});
test('area centre uses all outer polygon bounds',()=>{
 assert.equal(dispatchAreaCenter(null),null);assert.deepEqual(dispatchAreaCenter({type:'Polygon',coordinates:[[[-3,54],[-2,54],[-2,56],[-3,56],[-3,54]]]}),[-2.5,55]);
});
