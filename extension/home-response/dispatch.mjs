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
