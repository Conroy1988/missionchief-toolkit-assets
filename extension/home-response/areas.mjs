import {contains} from './planner.mjs';
export function createAreaLookup({request=(...args)=>fetch(...args),wait=ms=>new Promise(r=>setTimeout(r,ms)),now=()=>Date.now()}={}){
 const cache=new Map();let last=0,chain=Promise.resolve();
 function read(path){const work=chain.then(async()=>{if(cache.has(path))return cache.get(path);const delay=1500-(now()-last);if(delay>0)await wait(delay);last=now();const response=await request('https://nominatim.openstreetmap.org/'+path,{credentials:'omit',signal:AbortSignal.timeout(15000)});if(!response.ok)throw Error('Area lookup unavailable. Try city search or draw a boundary.');const data=await response.json();if(data.error)throw Error('No mapped area found here. Try city search or draw a boundary.');cache.set(path,data);if(cache.size>20)cache.delete(cache.keys().next().value);return data;});chain=work.catch(()=>{});return work;}
 return {search:q=>read('search?format=jsonv2&countrycodes=gb&polygon_geojson=1&limit=5&q='+encodeURIComponent(q)),atPoint:async point=>{
 if(!Array.isArray(point)||point.length!==2||!point.every(Number.isFinite)||point[0]<-9||point[0]>3||point[1]<49||point[1]>61)throw Error('Choose a location within the UK.');
 const choices=[];
 for(const zoom of [10,12]){const p=await read(`reverse?format=jsonv2&layer=address&addressdetails=1&polygon_geojson=1&zoom=${zoom}&lon=${point[0]}&lat=${point[1]}`);
 if(p.address?.country_code!=='gb'||!['Polygon','MultiPolygon'].includes(p.geojson?.type))continue;
 if(!contains(p.geojson,point))continue;
 if(!choices.some(c=>c.osm_type===p.osm_type&&c.osm_id===p.osm_id))choices.push(p);
 }return choices;
 }};
}
