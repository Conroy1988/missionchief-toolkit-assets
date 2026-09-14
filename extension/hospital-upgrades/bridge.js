HospitalUpgrades.configureHospitals({
 account:()=>HomeResponseBuilder.nativeAdapter(window).account(),
 list:()=>fetchExpansionPlannerBuildings(),
 async scanContext(accountId){
  const a=await HomeResponseBuilder.nativeAdapter(window).account();
  if(String(a.user_id)!==accountId)throw Error("Game account changed.");
  return {records:await fetchExpansionPlannerBuildings()};
 },
 async inspect(id,accountId,target,context){
  if(!context){const a=await HomeResponseBuilder.nativeAdapter(window).account();
  if(String(a.user_id)!==accountId)throw Error('Game account changed.');}
  // Ownership is verified against the full owned-building catalogue before discovery.
  const records=context?.records||await fetchExpansionPlannerBuildings();
  const record=records.find(r=>r.id===String(id)&&r.typeId==='4');
  if(!record)throw Error('Selected hospital is no longer in your owned buildings.');
  if(record.level>=target)return {record,operation:null};
  const {doc}=await fetchExpansionPlannerDocument(`/buildings/${record.id}`);
  if(expansionPlannerHasPendingConstruction(record,doc))throw Error(`${record.caption} has construction pending.`);
  const parsed=await discoverExpansionPlannerActions(doc,{...record,hospitalTargetLevel:target},'level');
  const actions=parsed.operations.filter(o=>o.kind==='level'&&o.actionSuffix==='expand_do/credits');
  if(parsed.ambiguous||actions.length>1)throw Error('The native hospital upgrade is ambiguous.');
  return {record,operation:actions.length?{...expansionPlannerPublicOperation(actions[0],record,'','Hospital'),hospitalTargetLevel:target,targetLevel:target}:null};
 },
 apply:(operation,remaining)=>applyExpansionPlannerOperation(operation,remaining),
 async exclusive(fn){
  if(runtime.destroyed||expansionPlannerRuntime.running||expansionPlannerRuntime.preparing||expansionPlannerRuntime.scanPromise||expansionPlannerRuntime.catalogPromise||expansionPlannerOtherDispatchBusy())throw Error('Another administration task is busy. Try after it finishes.');
  expansionPlannerRuntime.running=true;expansionPlannerRuntime.stopRequested=false;
  try{return await fn();}finally{expansionPlannerRuntime.running=false;expansionPlannerRuntime.stopRequested=false;}
 }
});
