// The adapter owns native validation. Persist intent BEFORE any irreversible request.
export async function runQueue(job,api,{save,stopped=()=>false}={}) {
 if(!save)throw Error('Durable checkpoint storage is required.');
 if(job.state==='complete')return job;
 if(!Number.isFinite(job.budget)||job.budget<0||!Number.isFinite(job.spent)||job.spent<0)throw Error('Invalid budget.');
 job.state='running';await save(job);
 try {
  for(const item of job.items){
   if(stopped())break;
   if(item.state==='complete')continue;
   await api.checkAccount(job.account);
   if(['creating','buying','uncertain'].includes(item.state)){
    if(!api.reconcile)throw Error('An earlier purchase has an uncertain result. No further purchase was attempted.');
    const recovered=await api.reconcile(item,job);
    if(!recovered||!['built','complete'].includes(recovered.state)||!Number.isFinite(recovered.cost)||recovered.cost<0)throw Error('Purchase recovery was inconclusive.');
    if(recovered.state==='built'&&!recovered.buildingId)throw Error('Recovered building identity is missing.');
    job.spent+=recovered.cost;
    if(recovered.buildingId)item.buildingId=String(recovered.buildingId);
    item.state=recovered.state;item.detail=recovered.detail;delete item.error;delete job.error;await save(job);
    if(item.state==='complete')continue;
    if(stopped())break;
   }
   if(!item.buildingId){
    const check=await api.checkSite(item,job);
    if(stopped())break;
    if(check.skip){item.state='skipped';item.detail=check.skip;await save(job);continue;}
    if(item.state==='skipped')continue;
    if(!Number.isFinite(check.total)||check.total<0||job.spent+check.total>job.budget)throw Error('Budget limit reached.');
    item.state='creating';item.reserved=check.total;item.buildingCost=check.cost;item.beforeBuildingIds=check.beforeBuildingIds||[];await save(job);
    const made=await api.create(item,job,check);
    if(!made?.id||!Number.isFinite(made.cost)||made.cost<0)throw Error('Building creation could not be verified.');
    item.buildingId=String(made.id);job.spent+=made.cost;item.state='built';await save(job);
   }
   if(stopped())break;
   await api.checkAccount(job.account);
   const purchase=await api.checkVehicle(item,job);
   if(stopped())break;
   if(purchase.present){item.state='complete';item.detail='Selected vehicle verified.';await save(job);continue;}
   if(!Number.isFinite(purchase.cost)||purchase.cost<0||job.spent+purchase.cost>job.budget)throw Error('Budget limit reached before vehicle purchase.');
   item.state='buying';item.vehicleCost=purchase.cost;item.beforeVehicles=purchase.before||[];await save(job);
   await api.buy(item,job,purchase);
   if(!await api.verifyVehicle(item,job))throw Error('Vehicle purchase could not be verified.');
   job.spent+=purchase.cost;item.state='complete';item.detail='Purchased; crew readiness requires checking.';await save(job);
  }
  job.state=job.items.every(i=>['complete','skipped'].includes(i.state))?'complete':'paused';await save(job);
 }catch(e){job.state='paused';const pending=job.items.find(i=>['creating','buying','uncertain'].includes(i.state));if(pending&&!pending.error)pending.error=e.message;job.error=e.message;await save(job);throw e;}
 return job;
}
