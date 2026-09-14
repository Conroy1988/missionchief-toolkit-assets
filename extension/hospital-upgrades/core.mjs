// Hospital level upgrades only. Sharing, tax, extensions and Coins are not actions here.
export const HOSPITAL_LEVEL_LIMIT = 30;
export function hospitalCreditBalance(account) {
 const raw=account?.credits_user_current;
 if(typeof raw!=='number'&&(typeof raw!=='string'||!/^\d+$/.test(raw.trim())))throw Error('Could not read your Credit balance from the game. No upgrade was purchased.');
 const balance=Number(raw);
 if(!Number.isSafeInteger(balance)||balance<0)throw Error('Could not read your Credit balance from the game. No upgrade was purchased.');
 return balance;
}
export function hospitalTarget(value) {
 const level=value==='max'?HOSPITAL_LEVEL_LIMIT:Number(value);
 if(!Number.isInteger(level)||level<1||level>HOSPITAL_LEVEL_LIMIT)throw Error('Choose a hospital target level from 1 to 30.');
 return level;
}
export function hospitalPlan(records,target) {
 const wanted=hospitalTarget(target),seen=new Set();
 return records.filter(r=>String(r.typeId)==='4').map(r=>{
  if(!/^\d+$/.test(String(r.id))||seen.has(String(r.id))||!Number.isInteger(r.level)||r.level<0)throw Error('Hospital catalogue is invalid.');
  seen.add(String(r.id));return {id:String(r.id),name:r.caption,startLevel:r.level,level:r.level,target:wanted,steps:Math.max(0,wanted-r.level),selected:r.level<wanted,state:r.level>=wanted?'already-ready':'pending',purchased:0,spent:0};
 });
}
export async function runHospitalUpgrades(job,api,{save,stopped=()=>false}={}) {
 if(!save)throw Error('Checkpoint storage is required.');
 hospitalTarget(job.target);
 if(!Array.isArray(job.items)||!job.items.length||new Set(job.items.map(i=>i.id)).size!==job.items.length)throw Error('Invalid hospital plan.');
 for(const item of job.items){if(!/^\d+$/.test(item.id)||!Number.isInteger(item.level)||!Number.isSafeInteger(item.unitPrice)||item.unitPrice<=0||!Number.isSafeInteger(item.spent)||item.spent<0||!Number.isInteger(item.purchased)||item.purchased<0)throw Error('Invalid hospital checkpoint.');if(item.intent?.to!==undefined&&(!Number.isInteger(item.intent.to)||item.intent.to<=item.intent.from||item.intent.to>item.target))throw Error("Invalid saved target intent.");if(item.quotedPrice!==undefined&&(!Number.isSafeInteger(item.quotedPrice)||item.quotedPrice<=0))throw Error("Invalid quoted price.");if(item.intent&&(!Number.isInteger(item.intent.from)||!Number.isSafeInteger(item.intent.cost)||item.intent.cost<=0||item.intent.cost>item.unitPrice*(item.target-item.intent.from)))throw Error('Invalid purchase intent.');}
 if(!Number.isSafeInteger(job.ceiling)||job.ceiling<0||!Number.isSafeInteger(job.spent)||job.spent<0)throw Error('Invalid confirmed Credit total.');
 const account=await api.account();if(String(account.user_id)!==job.account)throw Error('Game account changed.');
 job.state='running';await save(job);
 try {
  for(const item of job.items){
   if(stopped())break;
   if(item.target!==job.target)throw Error('Saved target changed.');
   let current=await api.inspect(item.id,job.account,item.target);
   if(item.intent){
    if(current.record.level!==(item.intent.to??item.intent.from+1))throw Error('Previous purchase remains uncertain. No purchase will be retried.');
    item.spent+=item.intent.cost;job.spent+=item.intent.cost;item.purchased++;item.level=current.record.level;delete item.intent;await save(job);
   }
   if(current.record.level<item.level)throw Error('Hospital level decreased unexpectedly.');
   item.level=current.record.level;
   while(item.level<item.target&&!stopped()){
    if(!current.operation)throw Error(`${item.name}: the next Credit level upgrade is unavailable. Check the native hospital page.`);
    const to=current.operation.targetLevel??item.level+1;
    if(!Number.isInteger(to)||to<=item.level||to>item.target)throw Error("Invalid native target level.");
    const cost=current.operation.priceCredits;
    if(!Number.isSafeInteger(cost)||cost<=0||cost>(item.quotedPrice??item.unitPrice*(to-item.level))||job.spent+cost>job.ceiling)throw Error('Upgrade price changed. Review a new estimate before purchasing.');
    const funds=await api.account();if(String(funds.user_id)!==job.account)throw Error('Game account changed.');
    const balance=hospitalCreditBalance(funds);
    if(balance<cost)throw Error(`Insufficient Credits: ${balance.toLocaleString()} available; ${cost.toLocaleString()} needed for this upgrade.`);
    if(stopped())break;
    item.intent={from:item.level,to,cost};item.state='upgrading';await save(job);
    if(stopped()){delete item.intent;item.state='paused';await save(job);break;}
    try {await api.apply(current.operation,job.ceiling-job.spent);}
    catch(error){if(error.expansionPlannerStoppedBeforeMutation){delete item.intent;}throw error;}
    const verified=await api.inspect(item.id,job.account,item.target);
    if(verified.record.level!==(item.intent.to??item.intent.from+1))throw Error('Purchased hospital level could not be verified.');
    item.level=verified.record.level;item.spent+=cost;job.spent+=cost;item.purchased++;delete item.intent;current=verified;await save(job);
   }
   item.state=item.level>=item.target?'complete':'paused';await save(job);
  }
  job.state=job.items.every(i=>i.level>=i.target&&!i.intent)?'complete':'paused';delete job.error;await save(job);
 }catch(error){job.state='paused';job.error=error.message;await save(job);throw error;}
 return job;
}
