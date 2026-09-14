// The adapter owns native validation. Persist intent BEFORE any irreversible request.
export async function runQueue(job,api,{save,stopped=()=>false}={}) {
 const timed=async(item,stage,fn)=>{const start=performance.now();try{return await fn();}finally{item.timings??={};item.timings[stage]=(item.timings[stage]||0)+Math.max(0,performance.now()-start);}};
 if(!save)throw Error('Durable checkpoint storage is required.');
 if(job.state==='complete')return job;
 if(!Number.isFinite(job.spent)||job.spent<0)throw Error('Invalid spending record.');
 job.state='running';await save(job);
 try {
  for(const item of job.items){
   if(stopped())break;
   if(item.state==='complete'&&(!job.imageSource||item.imageDone))continue;
   if(!api.validatesPurchaseAccount||['complete','creating','buying','uncertain'].includes(item.state))await timed(item,'account',()=>api.checkAccount(job.account));
   if(item.state==='complete'){await timed(item,'icon',()=>api.copyImage(item,job));item.imageDone=true;await save(job);continue;}
   if(['creating','buying','uncertain'].includes(item.state)){
    if(!api.reconcile)throw Error('An earlier purchase has an uncertain result. No further purchase was attempted.');
    const recovered=await timed(item,'recovery',()=>api.reconcile(item,job));
    if(!recovered||!['built','complete'].includes(recovered.state)||!Number.isFinite(recovered.cost)||recovered.cost<0)throw Error('Purchase recovery was inconclusive.');
    if(recovered.state==='built'&&!recovered.buildingId)throw Error('Recovered building identity is missing.');
    job.spent+=recovered.cost;
    if(recovered.buildingId)item.buildingId=String(recovered.buildingId);
    item.state=recovered.state;item.detail=recovered.detail;delete item.error;delete job.error;await save(job);
    if(item.state==='complete'){if(job.imageSource){await timed(item,'icon',()=>api.copyImage(item,job));item.imageDone=true;await save(job);}continue;}
    if(stopped())break;
   }
   if(!item.buildingId){
    const check=await timed(item,'checks',()=>api.checkSite(item,job));
    if(stopped())break;
    if(check.skip){item.state='skipped';item.detail=check.skip;await save(job);continue;}
    if(item.state==='skipped')continue;
    if(!Number.isFinite(check.total)||check.total<0)throw Error('Building cost is unavailable.');
    item.state='creating';item.reserved=check.total;item.buildingCost=check.cost;item.beforeBuildingIds=check.beforeBuildingIds||[];await save(job);
    const made=await timed(item,'build',()=>api.create(item,job,check));
    if(!made?.id||!Number.isFinite(made.cost)||made.cost<0)throw Error('Building creation could not be verified.');
    item.buildingId=String(made.id);job.spent+=made.cost;item.state='built';await save(job);
   }
   if(stopped())break;
   if(!api.validatesPurchaseAccount)await timed(item,'account',()=>api.checkAccount(job.account));
   const purchase=await timed(item,'vehicleChecks',()=>api.checkVehicle(item,job));
   if(stopped())break;
   if(purchase.present){item.state='complete';item.detail='Selected vehicle verified.';await save(job);if(job.imageSource&&!stopped()){await timed(item,'icon',()=>api.copyImage(item,job));item.imageDone=true;await save(job);}continue;}
   if(!Number.isFinite(purchase.cost)||purchase.cost<0)throw Error('Vehicle cost is unavailable.');
   item.state='buying';item.vehicleCost=purchase.cost;item.beforeVehicles=purchase.before||[];await save(job);
   await timed(item,'buy',()=>api.buy(item,job,purchase));
   if(!await timed(item,'verify',()=>api.verifyVehicle(item,job)))throw Error('Vehicle purchase could not be verified.');
   job.spent+=purchase.cost;item.state='complete';item.detail='Purchased; crew readiness requires checking.';await save(job);
   if(job.imageSource&&!stopped()){await timed(item,'icon',()=>api.copyImage(item,job));item.imageDone=true;await save(job);}
  }
  job.state=job.items.every(i=>i.state==='skipped'||(i.state==='complete'&&(!job.imageSource||i.imageDone)))?'complete':'paused';await save(job);
 }catch(e){job.state='paused';const pending=job.items.find(i=>['creating','buying','uncertain'].includes(i.state));if(pending&&!pending.error)pending.error=e.message;job.error=e.message;await save(job);throw e;}
 return job;
}
