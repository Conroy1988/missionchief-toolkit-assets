import {VEHICLES} from '../home-response/catalogue.mjs';
// Match the native Credit action while retaining its navigation parameters.
export function switchCreditUrl(raw,origin,id,type){
 let u;try{u=new URL(raw,origin);}catch{return null;}
 if(u.origin!==origin||u.hash||![`/buildings/${id}/vehicle/${id}/${type}/credits`,`/buildings/${id}/vehicle/${type}/credits`].includes(u.pathname))return null;
 const seen=new Set();for(const [key,value]of u.searchParams){
  if(seen.has(key))return null;seen.add(key);
  if(key==='building'){if(value!==String(id))return null;}
  else if(key==='return_tab'){if(!/^[a-z][a-z0-9_-]*$/i.test(value))return null;}
  else return null;
 }
 return u.href;
}
export function switchNative(win,base){
 const origin=win.location.origin;
 async function request(path,options={}){const url=new URL(path,origin);if(url.origin!==origin)throw Error('Unexpected game destination.');const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),25000);try{const r=await win.fetch(url,{credentials:'same-origin',cache:'no-store',...options,signal:controller.signal});if(!r.ok||new URL(r.url).origin!==origin||/\/users\/sign_in/.test(new URL(r.url).pathname))throw Error(`Game request failed (${r.status}).`);return await r.text();}finally{clearTimeout(timer);}}
 const fleet=async()=>{const data=JSON.parse(await request('/api/vehicles'));if(!Array.isArray(data)||new Set(data.map(v=>String(v.id))).size!==data.length||data.some(v=>!/^\d+$/.test(String(v.id))||!/^\d+$/.test(String(v.building_id))))throw Error('Vehicle list could not be verified.');return data;};
 async function accountCheck(id,cost=0){const a=await base.account();if(String(a.user_id)!==String(id))throw Error('Game account changed.');const n=Number(a.credits_user_current);if(!Number.isSafeInteger(n)||n<cost)throw Error('Could not confirm enough Credits for replacement.');}
 async function owned(i,job){await accountCheck(job.account);const b=(await base.buildings()).find(b=>String(b.id)===i.buildingId&&Number(b.building_type)===22);if(!b||(job.dispatch!=='all'&&String(b.leitstelle_building_id??'')!==job.dispatch))throw Error('Home Response ownership or dispatch assignment changed.');return b;}
 function purchaseFrom(doc,id,type,{allowCapacityEstimate=false}={}){
  const matches=[...doc.querySelectorAll('a[href]')].filter(a=>switchCreditUrl(a.getAttribute('href'),origin,id,type));
  const prices=matches.map(a=>{const m=a.textContent.match(/([\d,]+)\s*Credits/i);return m?Number(m[1].replaceAll(',','')):NaN;});
  const enabled=matches.filter(a=>!a.classList.contains('disabled')&&a.getAttribute('aria-disabled')!=='true');
  if(enabled.length){if(prices.some(n=>!Number.isSafeInteger(n)||n<=0)||new Set(prices).size!==1)throw Error('Replacement Credit price is unavailable or inconsistent.');return {url:new URL(enabled[0].getAttribute('href'),origin).href,cost:prices[0],estimated:false};}
  const text=(doc.body?.textContent||'').replace(/\s+/g,' ');
  const full=/no (?:free|available) (?:vehicle )?(?:parking(?: spaces?)?|places?|spaces?|slots?)|not enough (?:free )?(?:vehicle )?(?:parking )?space|(?:do not|don't|does not|doesn't) have (?:any )?(?:free|available) (?:vehicle )?(?:parking )?(?:spaces?|places?|slots?)/i.test(text);
  const vehicle=VEHICLES.find(v=>v.id===Number(type));
  if(allowCapacityEstimate&&full&&vehicle){
   if(matches.length&&(prices.some(n=>!Number.isSafeInteger(n)||n<=0)||new Set(prices).size!==1))throw Error('Disabled replacement Credit price is unavailable or inconsistent.');
   return {cost:matches.length?prices[0]:vehicle.credits,estimated:true,detail:'Shop reports no free space. Replacement must be enabled and its live price checked after removal.'};
  }
  if(matches.length)throw Error(full?'Replacement is still disabled and the shop reports no free space. The saved slot needs checking.':'Replacement purchase is disabled without a recognised full-slot message. No removal will proceed; open this building’s shop to inspect its restriction.');
  throw Error(full?'The shop reports no free space, but this replacement cannot be estimated.':'No matching replacement Credit offer was found. Open this Home Response’s vehicle shop to check the reason.');
 }
 async function shop(i,to,options){
  const path=`/buildings/${i.buildingId}/vehicles/new`,first=await base.html(path);
  try{return purchaseFrom(first.doc,i.buildingId,to,options);}catch(initial){
   // Follow only native shop navigation, never a generated purchase URL.
   const tabs=new Map();
   for(const a of first.doc.querySelectorAll('a[href]')){
    const label=(a.textContent||'').trim();if(!/^(Firefighting|Ambulance|General Practitioner|Search and Rescue|Coastal Rescue|Police)$/i.test(label))continue;
    const u=new URL(a.getAttribute('href'),origin);if(u.origin!==origin||u.hash||u.pathname!==path||!u.search)continue;
    tabs.set(u.href,label);
   }
   const category=({3:'Firefighting',10:'Ambulance',20:'Ambulance',21:'Ambulance',22:'Ambulance',34:'Ambulance',95:'Ambulance',96:'Ambulance',92:'Search and Rescue',93:'Search and Rescue',101:'Search and Rescue',57:'Coastal Rescue',60:'Coastal Rescue',12:'Police'})[to];
   const ordered=[...tabs].sort((a,b)=>Number(b[1]===category)-Number(a[1]===category));
   for(const [url]of ordered){const page=await base.html(url);try{return purchaseFrom(page.doc,i.buildingId,to,options);}catch(error){if(/disabled|inconsistent/.test(error.message))throw error;}}
   throw initial;
  }
 }
 function deletion(doc,id){const matches=[...doc.querySelectorAll('a[href]')].filter(a=>{const u=new URL(a.getAttribute('href'),origin);return u.origin===origin&&u.pathname===`/vehicles/${id}`&&!u.search&&!u.hash&&String(a.getAttribute('data-method')||a.getAttribute('data-turbo-method')).toLowerCase()==='delete'&&!a.classList.contains('disabled')&&a.getAttribute('aria-disabled')!=='true';});const token=doc.querySelector('meta[name="csrf-token"]')?.content;if(matches.length!==1||!token)throw Error('The game’s native vehicle removal control could not be verified.');return {url:new URL(matches[0].getAttribute('href'),origin).href,token};}
 async function prepare(i,job){await owned(i,job);const all=await fleet(),old=all.find(v=>String(v.id)===i.id);if(!old||String(old.building_id)!==i.buildingId||Number(old.vehicle_type)!==i.from)throw Error('Selected vehicle changed.');if(Number(old.fms_real)!==2)return {skip:'Vehicle is not available at station.'};const [purchase,page]=await Promise.all([shop(i,job.to,{allowCapacityEstimate:all.filter(v=>String(v.building_id)===i.buildingId).length===1}),base.html(`/vehicles/${i.id}`)]);await accountCheck(job.account,purchase.cost);return {...purchase,remove:deletion(page.doc,i.id),before:all.filter(v=>String(v.building_id)===i.buildingId).map(v=>String(v.id))};}
 async function removed(i,job){await owned(i,job);const all=await fleet();if(all.some(v=>String(v.id)===i.id))return false;const ids=all.filter(v=>String(v.building_id)===i.buildingId).map(v=>String(v.id));return Array.isArray(i.before)&&i.before.filter(id=>id!==i.id).every(id=>ids.includes(id))&&ids.every(id=>i.before.includes(id));}
 async function replacement(i,job){await owned(i,job);const all=await fleet();if(all.some(v=>String(v.id)===i.id)||!Array.isArray(i.before))return null;const local=all.filter(v=>String(v.building_id)===i.buildingId),added=local.filter(v=>!i.before.includes(String(v.id)));if(!i.before.filter(id=>id!==i.id).every(id=>local.some(v=>String(v.id)===id)))return null;return added.length===1&&Number(added[0].vehicle_type)===job.to?String(added[0].id):null;}
 async function quoteBatch(items,job,{stopped=()=>false,progress=()=>{}}={}){
  const [a,buildings,all]=await Promise.all([base.account(),base.buildings(),fleet()]);
  if(String(a.user_id)!==String(job.account))throw Error('Game account changed.');
  const balance=Number(a.credits_user_current);if(!Number.isSafeInteger(balance)||balance<0)throw Error('Could not read your Credit balance.');
  const homes=new Map(buildings.map(b=>[String(b.id),b])),units=new Map(all.map(v=>[String(v.id),v])),counts=new Map(),shops=new Map();
  for(const v of all)counts.set(String(v.building_id),(counts.get(String(v.building_id))||0)+1);
  const results=new Array(items.length);let next=0,done=0,failure=null;
  async function worker(){while(!failure&&!stopped()&&next<items.length){const index=next++,item=items[index];try{
   const b=homes.get(item.buildingId),v=units.get(item.id);
   if(!b||Number(b.building_type)!==22||(job.dispatch!=='all'&&String(b.leitstelle_building_id??'')!==job.dispatch))throw Error('Home Response ownership or dispatch assignment changed.');
   if(!v||String(v.building_id)!==item.buildingId||Number(v.vehicle_type)!==item.from)throw Error('Selected vehicle changed.');
   if(Number(v.fms_real)!==2)results[index]={skip:'Vehicle is not available at station.'};
   else{if(!shops.has(item.buildingId))shops.set(item.buildingId,shop(item,job.to,{allowCapacityEstimate:counts.get(item.buildingId)===1}));
    const check=await shops.get(item.buildingId);if(balance<check.cost)throw Error('Not enough Credits for this replacement.');results[index]=check;}
   progress(++done,items.length,item);
  }catch(e){if(!failure)failure=Error(`${item.name||item.buildingId}: ${e.message}`);}}}
  // Drain the current reads before releasing the UI lock, including on failure/pause.
  await Promise.all(Array.from({length:Math.min(4,items.length)},()=>worker()));
  if(failure)throw failure;if(stopped())throw Error('Preview paused. No vehicles were removed.');return results;
 }
 return {fleet,account:base.account,buildings:base.buildings,accountCheck,prepare,removed,replacement,
  quoteBatch,
  async quote(i,job){return prepare(i,job);},
  async remove(i,job,check){let fresh;try{fresh=await prepare(i,job);if(fresh.skip)throw Error('Vehicle became unavailable before removal.');if((fresh.estimated&&!check.estimated)||fresh.cost>check.cost||fresh.before.length!==check.before.length||fresh.before.some(id=>!check.before.includes(id)))throw Error('Vehicle or replacement price changed before removal.');}catch(e){e.switchNotSent=true;throw e;}await request(fresh.remove.url,{method:'DELETE',headers:{'X-CSRF-Token':fresh.remove.token,Accept:'text/html'}});},
  async purchaseCheck(i,job){if(!await removed(i,job))throw Error('The building’s vehicle contents changed. Inspect it before continuing.');const p=await shop(i,job.to);await accountCheck(job.account,p.cost);return p;},
  async buy(i,job,p){try{await accountCheck(job.account,p.cost);}catch(e){e.switchNotSent=true;throw e;}await request(p.url);}
 };
}
