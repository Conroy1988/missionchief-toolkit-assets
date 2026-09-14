export const iconKey = image => {
  if (!image?.pixelDigest || !(image.width > 0) || !(image.height > 0)) throw Error('Image content could not be verified.');
  return `${image.width}:${image.height}:${image.pixelDigest}`;
};
export const iconScope = (records, type = '', dispatch = '') => records.filter(r =>
  (!type || String(r.typeId) === type) && (!dispatch || String(r.dispatchId || '0') === dispatch));
export const iconTarget = r => ({buildingId:r.id, name:r.caption, dispatchId:r.dispatchId, typeId:r.typeId, small:r.small, latitude:r.latitude, longitude:r.longitude});
export function sameIconTarget(record, item) {
  return ['buildingId','name','dispatchId','typeId','small','latitude','longitude'].every(k => iconTarget(record)[k] === item[k]);
}
// Preview reuses verified scan membership; execution still rechecks pixels before upload.
export function previewIconMatches(group,records,type='',dispatch='') {
  const current=new Map(iconScope(records,type,dispatch).map(r=>[String(r.id),r]));
  return group.items.filter(item=>{const r=current.get(String(item.buildingId));return r?.hasCustomIcon&&r.customIconUrl&&sameIconTarget(r,item);}).map(item=>({...item,state:'pending',selected:true}));
}
export async function scanIcons(api, records, {progress=()=>{}, stopped=()=>false}={}) {
  const urls = new Map(), groups = new Map(), unavailable = [];
  for (const record of records) if (record.hasCustomIcon && record.customIconUrl) {
    if (!urls.has(record.customIconUrl)) urls.set(record.customIconUrl, []);
    urls.get(record.customIconUrl).push(record);
  }
  const entries = [...urls], results = []; let cursor=0, done=0;
  await Promise.all(Array.from({length:Math.min(4,entries.length)}, async()=>{
    while(cursor<entries.length && !stopped()) {
      const [url, stations] = entries[cursor++];
      try {const image=await api.image(url, 'Building icon');results.push({key:iconKey(image),stations});}
      catch {unavailable.push(...stations.map(r=>r.id));}
      progress(++done,entries.length);
    }
  }));
  if(stopped()) throw Error('Scan stopped. No buildings changed.');
  for(const {key,stations} of results) {
    if(!groups.has(key)) groups.set(key,{key,url:stations[0].customIconUrl,sourceId:stations[0].id,items:[]});
    groups.get(key).items.push(...stations.map(iconTarget));
  }
  return {groups:[...groups.values()].sort((a,b)=>b.items.length-a.items.length),unavailable,savedAt:Date.now()};
}
export async function runIconReplacement(job,api,{save,stopped=()=>false,progress=()=>{},stage=()=>{}}) {
  if(job.schema!==1 || !job.items?.length || job.from===job.to) throw Error('Invalid replacement plan.');
  const identity=async()=>{if(String((await api.account()).user_id)!==job.account)throw Error('Game account changed.');if(api.busy())throw Error('Another Operations task is running.');};
  stage('Checking replacement source');
  await identity();
  const source=await api.building(job.sourceId,{requireIcon:true});
  if(!source.hasCustomIcon||!source.customIconUrl)throw Error('Replacement source no longer has a custom icon.');
  const image=await api.image(source.customIconUrl,'Replacement icon');
  if(iconKey(image)!==job.to)throw Error('Replacement icon changed. Scan and review a new plan.');
  job.state='running';await save(job);
  for(const item of job.items) {
    if(stopped())break;
    if(['complete','skipped'].includes(item.state))continue;
    try {
      stage('Checking building and current icon',item);
      await identity();
      const record=await api.building(item.buildingId,{requireIcon:true});
      if(!sameIconTarget(record,item))throw Error('Building identity or scope changed. Review this building before continuing.');
      const current=record.hasCustomIcon&&record.customIconUrl?await api.image(record.customIconUrl,'Current icon'):null;
      const key=current?iconKey(current):null;
      if(key===job.to){item.state='complete';item.detail='Replacement icon verified';}
      else if(item.state==='writing')throw Error('Previous upload is uncertain. No repeat upload was sent. Check this building in the game.');
      else if(key!==job.from){item.state='skipped';item.detail='Original icon changed since preview';}
      else {
        item.state='writing';await save(job);
        stage('Uploading and verifying icon',item);
        await api.apply(item,{replaceMode:'all',expectedIcon:current},image);
        item.state='complete';item.detail='Replacement icon saved and verified';
      }
      delete item.error;await save(job);progress(job);
    } catch(e) {item.error=e.message;job.state='paused';await save(job);throw e;}
  }
  job.state=job.items.every(i=>['complete','skipped'].includes(i.state))?'complete':'paused';
  await save(job);progress(job);
}
