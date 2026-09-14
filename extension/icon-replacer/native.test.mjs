import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../../.dev/home-response-extension/features/administration.js',import.meta.url),'utf8');
const start=source.indexOf('"applyStationIconToStation":')+'"applyStationIconToStation":'.length;
const end=source.indexOf(',\n"loadStationIconCatalog"',start);
const factory=Function(`return (${source.slice(start,end)})`)();
test('native copier refuses changed or removed original image before opening upload form',async()=>{
 for(const custom of [true,false]){
  let edits=0;
  const copy=factory({fetchStationIconBuilding:async()=>({hasCustomIcon:custom,customIconUrl:'changed'}),stationIconAssertTargetScope:()=>{},STATION_ICON_REPLACE_DEFAULTS:'defaults',fetchStationIconImage:async()=>({pixelDigest:'changed'}),stationIconImagesMatch:(a,b)=>a.pixelDigest===b.pixelDigest,fetchStationIconDocument:async()=>{edits++;throw Error('unexpected upload preparation');}});
  await assert.rejects(copy({buildingId:1},{replaceMode:'all',expectedIcon:{pixelDigest:'original'}},{pixelDigest:'new'}),/Original icon changed/);
  assert.equal(edits,0);
 }
});
