const OPERATIONS=new Set(['startTransportSweep','startAllianceCourses','startDispatchRecruitment','startStationIconCopier','startExpansionPlanner','scanTransportSweepQueue','scanAllianceCourseQueue','scanDispatchRecruitmentStations','scanStationIconTargets','scanExpansionPlanner']);
const TYPES = new Set(['transport-scan','administration','administration-scan']);
export function createJobs(storage, now = Date.now, isAlive = async () => true) {
  let serial = Promise.resolve();
  const keyFor = (origin,account,type) => `job:v1:${origin}:${account}:${type}`;
  async function run(sender, message) {
    const {origin,documentId,tabId}=sender;
    if (!/^[a-zA-Z0-9_-]{1,64}$/.test(message.account || '') || !TYPES.has(message.type)) throw Error('Invalid job scope.');
    const key=keyFor(origin,message.account,message.type), previous=(await storage.get(key))[key];
    const owned=previous?.documentId===documentId;
    if (message.action==='claim') {
      if (previous?.state==='running' && (previous.expires>now() || await isAlive(previous))) throw Error(owned?'This task is already running.':'This task is running in another MissionChief tab.');
      const historyKey=`job-history:v1:${origin}:${message.account}`;
      if(previous){const history=(await storage.get(historyKey))[historyKey]||[];await storage.set({[historyKey]:[{...previous,state:previous.state==='running'?'interrupted':previous.state},...history.filter(item=>item.documentId!==previous.documentId||item.started!==previous.started)].slice(0,20)});}
      const job={operation:OPERATIONS.has(message.operation)?message.operation:message.type,type:message.type,documentId,tabId,state:'running',started:now(),updated:now(),expires:now()+60000,checked:0,total:0,found:0,interrupted:previous?.state==='running'};
      await storage.set({[key]:job}); return job;
    }
    if (!owned || previous?.state!=='running') throw Error('Task ownership was lost. Stop and review its status.');
    const status = ['complete','cancelled','error','interrupted','partial'].includes(message.state)?message.state:'running';
    const job={...previous,state:status,updated:now(),expires:now()+60000};
    for(const field of ['checked','total','found','succeeded','failed','skipped']) if(Number.isFinite(message[field])) job[field]=Math.max(0,Math.min(100000,message[field]));
    await storage.set({[key]:job}); return job;
  }
  return {
    update(sender,message) {const next=serial.then(()=>run(sender,message));serial=next.catch(()=>{});return next;},
    interruptTab(tabId,documentId=null){
      const next=serial.then(async()=>{const all=await storage.get(null),updates={};for(const [key,j]of Object.entries(all))if(key.startsWith('job:v1:')&&j.tabId===tabId&&j.state==='running'&&j.documentId!==documentId)updates[key]={...j,state:'interrupted',updated:now()};if(Object.keys(updates).length)await storage.set(updates);});serial=next.catch(()=>{});return next;
    },
    async history(origin,account){if(!/^[a-zA-Z0-9_-]{1,64}$/.test(account||''))throw Error('Invalid account.');const key=`job-history:v1:${origin}:${account}`;return (await storage.get(key))[key]||[];},
    async list(origin,account=null) {const all=await storage.get(null);return Object.entries(all).filter(([k])=>k.startsWith(`job:v1:${origin}:${account?account+':':''}`)).map(([,j])=>({...j,state:j.state==='running'&&j.expires<=now()?'check-required':j.state}));}
  };
}
