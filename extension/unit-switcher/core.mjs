export function switchScope(buildings,vehicles,dispatch='all',from=null){
 const homes=new Map(buildings.filter(b=>Number(b.building_type)===22&&(dispatch==='all'||String(b.leitstelle_building_id??'')===String(dispatch))).map(b=>[String(b.id),b]));
 return vehicles.filter(v=>homes.has(String(v.building_id))&&(from===null||Number(v.vehicle_type)===Number(from))).map(v=>({id:String(v.id),buildingId:String(v.building_id),name:String(homes.get(String(v.building_id)).caption||`Home Response ${v.building_id}`),from:Number(v.vehicle_type),selected:Number(v.fms_real)===2,state:Number(v.fms_real)===2?'pending':'unavailable'}));
}
export function switchCentres(buildings){return [{id:'all',name:'All dispatch centres'},...buildings.filter(b=>Number(b.building_type)===7).map(b=>({id:String(b.id),name:String(b.caption||`Dispatch centre ${b.id}`)})).sort((a,b)=>a.name.localeCompare(b.name)),{id:'',name:'Unassigned'}];}
export async function runSwitcher(job,api,{save,stopped=()=>false}){
 if(!save||job.schema!==1||!/^\d+$/.test(job.account)||!Array.isArray(job.items)||!job.items.length||new Set(job.items.map(i=>i.id)).size!==job.items.length)throw Error('Invalid saved switch plan.');
 if(!Number.isSafeInteger(job.ceiling)||job.ceiling<0||!Number.isSafeInteger(job.spent)||job.spent<0||job.spent>job.ceiling)throw Error('Invalid confirmed cost.');
 for(const i of job.items)if(!/^\d+$/.test(i.id)||!/^\d+$/.test(i.buildingId)||!Number.isInteger(i.from)||i.from===job.to||!Number.isInteger(job.to)||!Number.isSafeInteger(i.cost)||i.cost<=0||!['pending','removing','removed','buying','complete','unavailable'].includes(i.state))throw Error('Invalid saved vehicle.');
 let active=null;job.state='running';await save(job);
 try{for(const i of job.items){if(stopped())break;if(['complete','unavailable'].includes(i.state))continue;active=i;delete i.error;
  await api.accountCheck(job.account);
  if(i.state==='removing'){if(!await api.removed(i,job))throw Error('Removal remains uncertain. The vehicle will not be removed again automatically.');i.state='removed';await save(job);}
  if(i.state==='buying'){const id=await api.replacement(i,job);if(!id)throw Error('Purchase remains uncertain. No duplicate will be bought.');i.replacementId=id;i.state='complete';job.spent+=i.cost;await save(job);continue;}
  if(i.state==='pending'){
   const check=await api.prepare(i,job);if(check.skip){i.state='unavailable';i.detail=check.skip;await save(job);continue;}
   if(check.estimated&&!i.estimated)throw Error('The live offer disappeared. Review a new catalogue estimate before removing vehicles.');
   if(!Number.isSafeInteger(check.cost)||check.cost<=0||!Array.isArray(check.before)||!check.before.includes(i.id)||check.cost>i.cost||job.spent+check.cost>job.ceiling)throw Error('Price increased. Review a fresh plan before removing vehicles.');
   if(stopped())break;
   i.cost=check.cost;i.before=check.before;i.state='removing';await save(job);
   if(stopped()){i.state='pending';await save(job);break;}
   try{await api.remove(i,job,check);}catch(e){if(e.switchNotSent)i.state='pending';throw e;}
   if(!await api.removed(i,job))throw Error('Removal could not be verified. No purchase was attempted.');
   i.state='removed';await save(job);
  }
  if(stopped())break;
  const purchase=await api.purchaseCheck(i,job);
  if(!Number.isSafeInteger(purchase.cost)||purchase.cost<=0||purchase.cost>i.cost||job.spent+purchase.cost>job.ceiling)throw Error('Replacement price increased. Building awaits a replacement.');
  if(stopped())break;i.cost=purchase.cost;i.state='buying';await save(job);
  if(stopped()){i.state='removed';await save(job);break;}
  try{await api.buy(i,job,purchase);}catch(e){if(e.switchNotSent)i.state='removed';throw e;}
  const replacement=await api.replacement(i,job);if(!replacement)throw Error('Replacement could not be verified. Resume will check without buying again.');
  i.replacementId=replacement;i.state='complete';job.spent+=i.cost;await save(job);
 }
 job.state=job.items.every(i=>['complete','unavailable'].includes(i.state))?'complete':'paused';delete job.error;await save(job);
 }catch(e){job.state='paused';const stage=active?.state==='removed'?'Vehicle removed; replacement outstanding':active?.state==='buying'?'Purchase outcome needs verification':active?.state==='removing'?'Removal outcome needs verification':'Replacement stopped';job.error=`${active?.name||active?.buildingId||'Unit Switcher'}: ${stage}. ${e.message}`;if(active)active.error=job.error;await save(job);throw Error(job.error);}
 return job;
}
