import {isDryLand} from './land.mjs';
import {distanceMiles} from './planner.mjs';
export function nativeAdapter(win=window){
 const origin=win.location.origin;
 async function read(path,options={}){
  const url=new URL(path,origin);if(url.origin!==origin)throw Error('Unexpected game destination.');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),25000);
  try{const r=await win.fetch(url,{credentials:'same-origin',cache:'no-store',...options,signal:controller.signal});
   if(!r.ok||new URL(r.url).origin!==origin||/users\/sign_in|login/.test(new URL(r.url).pathname))throw Error('Game session or request failed.');
   const text=await r.text();if(text.length>20*1024*1024)throw Error('Game response is too large.');return {r,text};
  }finally{clearTimeout(timer);}
 }
 const html=async path=>{const {r,text}=await read(path);return {doc:new DOMParser().parseFromString(text,'text/html'),url:r.url};};
 const json=async path=>JSON.parse((await read(path)).text);
 const account=async()=>{const v=await json('/api/credits');if(!/^\d+$/.test(String(v.user_id)))throw Error('Cannot verify signed-in account.');return v;};
 async function buildings(){const data=await json('/api/v2/buildings');if(!Array.isArray(data.result))throw Error('Unexpected buildings response.');
  const total=Number(data.pagination?.total??data.pagination?.total_entries??data.total??data.result.length);
  if(total>data.result.length||data.pagination?.next_page)throw Error('Buildings list is incomplete. Construction is blocked.');
  const ids=new Set();for(const b of data.result){if(!/^\d+$/.test(String(b.id))||ids.has(b.id))throw Error('Invalid building list.');ids.add(b.id);if(Number(b.building_type)===22&&(!Number.isFinite(b.latitude)||!Number.isFinite(b.longitude)))throw Error('Home Response coordinates are missing.');}return data.result;
 }
 function matchCreated(records,item){
  const matches=records.filter(b=>Number(b.building_type)===22&&(b.caption??b.name)===item.name
   &&distanceMiles(item.point,[b.longitude,b.latitude])<=0.02
   &&(!item.buildingId||String(b.id)===String(item.buildingId))
   &&!(item.beforeBuildingIds||[]).map(String).includes(String(b.id)));
  if(matches.length>1)throw Error('Multiple buildings match this saved location. No further purchase was attempted.');
  return matches[0]||null;
 }
 async function reconcile(item,job){
  if(item.state==='creating'){
   const b=matchCreated(await buildings(),item);
   if(!b)throw Error('The saved location has not been verified in your buildings yet. No duplicate will be built. Refresh and resume again.');
   let cost=item.buildingCost;
   if(!Number.isFinite(cost)){
    // Legacy 0.23.0 saved the building-plus-vehicle reservation before posting.
    cost=item.reserved-Number(job.vehicle?.credits);
   }
   if(!Number.isFinite(cost)||cost<0||cost>10000)throw Error('The saved building cost cannot be verified. No further purchase was attempted.');
   return {state:'built',buildingId:String(b.id),cost,detail:'Existing building recovered; vehicle purchase outstanding.'};
  }
  if(item.state==='buying'){
   const b=matchCreated(await buildings(),item);if(!b)throw Error('Saved building identity no longer matches.');
   const data=await json('/api/vehicles');if(!Array.isArray(data))throw Error('Unexpected vehicle verification response.');
   const inBuilding=data.filter(v=>String(v.building_id)===String(item.buildingId));
   const matching=inBuilding.filter(v=>Number(v.vehicle_type)===Number(job.vehicle.id));
   if(matching.length!==1||inBuilding.length!==1)throw Error('Vehicle purchase remains unverified. No second vehicle purchase was attempted.');
   const cost=Number.isFinite(item.vehicleCost)?item.vehicleCost:Number(job.vehicle?.credits);
   if(!Number.isFinite(cost)||cost<0)throw Error('Saved vehicle cost is invalid.');
   return {state:'complete',cost,detail:'Selected vehicle verified in the saved building; check crew readiness.'};
  }
  throw Error('Saved purchase state is not recognised. No further purchase was attempted.');
 }
 const money=text=>{const m=String(text).match(/([\d,]+)\s*Credits/i);if(!m)throw Error('Native Credit price is unavailable.');return Number(m[1].replaceAll(',',''));};
 const vehicles=async id=>{const {doc}=await html('/buildings/'+id);return [...doc.querySelectorAll('a[href]')].filter(a=>/^\/vehicles\/\d+$/.test(a.getAttribute('href'))).map(a=>a.getAttribute('href'));};
 async function checkVehicle(item,job){
  const {doc}=await html('/buildings/'+item.buildingId+'/vehicles/new');
  if(/no free places|No available parking/i.test(doc.body.textContent))throw Error('No free vehicle space. Inspect the created building before continuing.');
  const link=[...doc.querySelectorAll('a[href]')].find(a=>new URL(a.getAttribute('href'),origin).pathname===`/buildings/${item.buildingId}/vehicle/${item.buildingId}/${job.vehicle.id}/credits`);
  if(!link||link.getAttribute('aria-disabled')==='true'||link.classList.contains('disabled'))throw Error('Selected vehicle is unavailable at this location.');
  const cost=money(link.textContent);if(cost>job.vehicle.credits)throw Error('Vehicle price increased. Review a new plan.');
  const [credits,before]=await Promise.all([account(),vehicles(item.buildingId)]);
  if(String(credits.user_id)!==String(job.account))throw Error('Account changed.');if(Number(credits.credits_user_current)<cost)throw Error('Not enough Credits.');
  return {cost,url:link.getAttribute('href'),before};
 }
 return {account,buildings,html,reconcile,async checkAccount(id){if(String((await account()).user_id)!==String(id))throw Error('Account changed.');},
  async checkSite(item,job){if(!isDryLand(item.point))return {skip:'Water or uncertain shoreline: location excluded.'};const current=await buildings();if(current.some(b=>Number(b.building_type)===22&&distanceMiles(item.point,[b.longitude,b.latitude])<job.spacingMiles))return {skip:'A Home Response is now too close.'};
   const [{doc},credits]=await Promise.all([html('/buildings/new'),account()]);const button=doc.querySelector('#build_credits_22'),form=button?.closest('form');
   if(!form||new URL(form.getAttribute('action'),origin).pathname!=='/buildings'||button.disabled)throw Error('Native construction form unavailable.');
   const cost=money(button.value);if(cost>10000)throw Error('Building price increased. Review a new plan.');
   if(String(credits.user_id)!==String(job.account))throw Error('Account changed.');
   const total=cost+job.vehicle.credits;if(Number(credits.credits_user_current)<total)throw Error('Not enough Credits for building and vehicle.');
   return {cost,total,form,commit:button.value,beforeBuildingIds:current.filter(b=>(b.caption??b.name)===item.name).map(b=>String(b.id))};
  },
  async create(item,job,check){const data=new FormData(check.form);
   for(const key of [...data.keys()])if(key.startsWith('building[start_vehicle'))data.delete(key);
   data.set('building[building_type]','22');data.set('building[name]',item.name);data.set('building[latitude]',String(item.point[1]));data.set('building[longitude]',String(item.point[0]));data.set('building[leitstelle_building_id]',job.dispatchId||'');data.set('build_with_coins','0');data.set('build_as_alliance','0');data.delete('build_another');data.set('commit',check.commit);
   await read('/buildings',{method:'POST',body:data});
   // Native construction may return a list or map instead of /buildings/:id.
   // A redirect is not a receipt: verify the exact name, type and coordinates.
   const b=matchCreated(await buildings(),item);
   if(!b)throw Error('Build request finished but the location is not yet visible in the building catalogue. Resume will check again without creating a duplicate.');
   return {id:String(b.id),cost:check.cost};
  },checkVehicle,
  async buy(item,job,purchase){item.beforeVehicles=purchase.before;await read(purchase.url);},
  async verifyVehicle(item,job){const [after,data]=await Promise.all([vehicles(item.buildingId),json('/api/vehicles')]);const added=after.filter(id=>!item.beforeVehicles?.includes(id)).map(path=>path.split('/').pop());if(!Array.isArray(data))throw Error('Unexpected vehicle verification response.');return data.some(v=>added.includes(String(v.id))&&String(v.building_id)===String(item.buildingId)&&Number(v.vehicle_type)===job.vehicle.id);}
 };
}
