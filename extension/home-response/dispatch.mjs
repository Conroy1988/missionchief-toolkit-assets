import {polygons,distanceMiles} from './planner.mjs';
export function dispatchAreaCenter(geometry){
 if(!geometry)return null;let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;
 for(const poly of polygons(geometry))for(const [x,y] of poly[0]){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}
 return [(minX+maxX)/2,(minY+maxY)/2];
}
export function rankedDispatchCentres(records,center){
 return records.filter(b=>Number(b.building_type)===7).map(b=>{
 const point=Number.isFinite(b.longitude)&&Number.isFinite(b.latitude)&&Math.abs(b.longitude)<=180&&Math.abs(b.latitude)<=90?[b.longitude,b.latitude]:null;
 return {id:String(b.id),name:String(b.caption??b.name??`Dispatch centre ${b.id}`),point,miles:point&&center?distanceMiles(center,point):null};
 }).sort((a,b)=>(a.miles??Infinity)-(b.miles??Infinity)||a.name.localeCompare(b.name)||a.id.localeCompare(b.id));
}
export function dispatchAcknowledgement(job,records){
 if(!job.dispatchId)return 'Dispatch centre: Unassigned. These buildings will not be assigned to a dispatch centre. Confirm that this is OK before proceeding.';
 const centre=rankedDispatchCentres(records,job.areaCenter||null).find(b=>b.id===String(job.dispatchId));
 if(!centre)throw Error('The assigned dispatch centre is no longer available. Review the plan before building.');
 const distances=centre.point?job.items.map(i=>distanceMiles(centre.point,i.point)):[];
 return `Dispatch centre: ${centre.name}.\n${centre.miles===null?'Area-centre distance unavailable.':`Distance from area centre: ${centre.miles.toFixed(1)} miles.`}\n${distances.length?`Planned building distances: ${Math.min(...distances).toFixed(1)}–${Math.max(...distances).toFixed(1)} miles.`:'Building distances unavailable.'}\nDistances are straight-line, not driving distances. By choosing OK, you acknowledge that this dispatch assignment and its distances are acceptable.`;
}
