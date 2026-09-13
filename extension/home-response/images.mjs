import {distanceMiles} from './planner.mjs';
// Reuse the Toolkit's verified native image copier; checkpoints contain no image bytes.
export function createImageBridge({list,building,image,apply}){
 let cached;
 async function load(id){const record=await building(id,{requireIcon:true});if(!record.hasCustomIcon||!record.customIconUrl)throw Error('The selected source no longer has a custom building image.');const data=await image(record.customIconUrl,`${record.caption} source icon`);if(!data.pixelDigest)throw Error('Could not verify the source image.');return {...data,record};}
 return {
  sources:async({onProgress=()=>{}}={})=>{
   const records=(await list()).filter(b=>b.hasCustomIcon&&b.customIconUrl).sort((a,b)=>a.caption.localeCompare(b.caption));
   const urls=new Map();for(const b of records){if(!urls.has(b.customIconUrl))urls.set(b.customIconUrl,[]);urls.get(b.customIconUrl).push(b);}
   const entries=[...urls.values()],groups=new Map();let next=0,done=0,unavailable=0;
   // Four read-only downloads at most; identical URLs are fetched only once.
   await Promise.all(Array.from({length:Math.min(4,entries.length)},async()=>{while(next<entries.length){const stations=entries[next++],b=stations[0];try{
    const data=await image(b.customIconUrl,`${b.caption} icon`);if(!data.pixelDigest)throw Error('Unreadable icon');
    const key=`${data.width}:${data.height}:${data.pixelDigest}`;
    if(groups.has(key))groups.get(key).count+=stations.length;
    else groups.set(key,{...b,count:stations.length});
   }catch{unavailable+=stations.length;}finally{onProgress({done:++done,total:entries.length});}}}));
   return {icons:[...groups.values()].sort((a,b)=>a.caption.localeCompare(b.caption)),unavailable};
  },
  prepare:async id=>{cached=await load(id);return {id:String(id),name:cached.record.caption,pixelDigest:cached.pixelDigest};},
  copy:async(item,job)=>{
   const source=job.imageSource;
   if(!cached||String(cached.record.id)!==String(source.id)||cached.pixelDigest!==source.pixelDigest)cached=await load(source.id);
   if(cached.pixelDigest!==source.pixelDigest)throw Error('The source image has changed since this plan was approved. No image was copied.');
   const record=await building(item.buildingId,{requireIcon:true});
   if(String(record.id)!==String(item.buildingId)||Number(record.typeId)!==22||record.caption!==item.name||!Number.isFinite(record.longitude)||!Number.isFinite(record.latitude)||distanceMiles([record.longitude,record.latitude],item.point)>.02)throw Error('The new Home Response identity changed. No image was copied.');
   await apply({buildingId:record.id,dispatchId:record.dispatchId,typeId:record.typeId,small:record.small,name:record.caption,latitude:record.latitude,longitude:record.longitude},{replaceMode:'all'},cached);
  }
 };
}
