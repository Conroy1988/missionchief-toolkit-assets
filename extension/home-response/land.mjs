import {LAND_GEOMETRY} from './land-data.mjs';
import {contains} from './planner.mjs';
let landIndex;
export function isDryLand(point){
 if(!Array.isArray(point)||!point.every(Number.isFinite))return false;
 if(!landIndex)landIndex=LAND_GEOMETRY.coordinates.map(coordinates=>{let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(const [x,y]of coordinates[0]){minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);}return {minX,minY,maxX,maxY,geometry:{type:'Polygon',coordinates}};});
 const [x,y]=point;return landIndex.some(p=>x>=p.minX&&x<=p.maxX&&y>=p.minY&&y<=p.maxY&&contains(p.geometry,point));
}
