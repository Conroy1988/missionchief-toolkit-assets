// Pure planning module. Coordinates are GeoJSON [longitude, latitude].
export const SPACING_MILES = Object.freeze([1, 3, 4, 6, 8, 10]);
const R = 3958.7613, rad = n => n * Math.PI / 180;
export function distanceMiles(a,b) {
  const dlat=rad(b[1]-a[1]),dlon=rad(b[0]-a[0]);
  const h=Math.sin(dlat/2)**2+Math.cos(rad(a[1]))*Math.cos(rad(b[1]))*Math.sin(dlon/2)**2;
  return 2*R*Math.asin(Math.sqrt(Math.min(1,h)));
}
function valid(p){return Array.isArray(p)&&p.length>=2&&Number.isFinite(p[0])&&Number.isFinite(p[1])&&Math.abs(p[0])<=180&&Math.abs(p[1])<=90;}
function inRing(p,ring) {
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++) {
    const a=ring[i],b=ring[j];
    if((a[1]>p[1])!==(b[1]>p[1]) && p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
  }
  return inside;
}
export function polygons(geometry){
  const ps=geometry?.type==='Polygon'?[geometry.coordinates]:geometry?.type==='MultiPolygon'?geometry.coordinates:null;
  if(!ps?.length||ps.some(p=>!p.length||p.some(r=>r.length<4||r.some(c=>!valid(c)))))throw Error('Choose a valid area boundary.');
  return ps;
}
export function contains(geometry,point){return polygons(geometry).some(p=>inRing(point,p[0])&&!p.slice(1).some(r=>inRing(point,r)));}
export function circle(center,radiusMiles){
  if(!valid(center)||!Number.isFinite(radiusMiles)||radiusMiles<=0||radiusMiles>100)throw Error('Choose a radius between 0 and 100 miles.');
  const phi=rad(center[1]),lambda=rad(center[0]),delta=radiusMiles/R,ring=[];
  for(let i=0;i<96;i++){
    const bearing=2*Math.PI*i/96;
    const lat=Math.asin(Math.sin(phi)*Math.cos(delta)+Math.cos(phi)*Math.sin(delta)*Math.cos(bearing));
    const lon=lambda+Math.atan2(Math.sin(bearing)*Math.sin(delta)*Math.cos(phi),Math.cos(delta)-Math.sin(phi)*Math.sin(lat));
    ring.push([lon*180/Math.PI,lat*180/Math.PI]);
  }
  ring.push([...ring[0]]);return {type:'Polygon',coordinates:[ring]};
}
// Intersect one latitude with boundary edges once, rather than retesting every
// candidate against every vertex. Even/odd intersections preserve boundary holes.
function spansAt(polys,y){
 const spans=[];
 for(const poly of polys){const xs=[];for(const ring of poly)for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y))xs.push(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]));
 }xs.sort((a,b)=>a-b);for(let i=0;i+1<xs.length;i+=2)spans.push([xs[i],xs[i+1]]);}
 return spans;
}
function* generatePlan({geometry,spacingMiles,existing=[],excluded=[],landGeometry=null,maxBuildings=1000,fillGaps=true}){
 if(!SPACING_MILES.includes(spacingMiles))throw Error('Unsupported spacing.');
 if(!Number.isInteger(maxBuildings)||maxBuildings<1||maxBuildings>1000)throw Error('Choose 1–1000 buildings.');
 if(existing.some(p=>!valid(p)))throw Error('Existing building coordinates are incomplete. Refresh buildings before planning.');
 const ps=polygons(geometry),ex=excluded.flatMap(polygons),land=landGeometry?polygons(landGeometry):null;
 let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
 for(const poly of ps)for(const ring of poly)for(const [x,y]of ring){minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}
 if(minX < -9 || maxX > 3 || minY < 49 || maxY > 61)throw Error('Select an area within the UK planning bounds.');
 // Use the same Earth radius as the distance check; approximate degree lengths
 // previously made neighbouring grid points slightly closer than requested.
 const angular=spacingMiles/R*180/Math.PI*1.002;
 const dy=angular*Math.sqrt(3)/2,dx=angular/Math.cos(rad(maxY));
 const rows=Math.ceil((maxY-minY)/dy)+1,cols=Math.ceil((maxX-minX)/dx)+2;
 const cellY=spacingMiles/69.2,cellX=spacingMiles/(69.2*Math.cos(rad(minY))),buckets=new Map();
 const key=p=>[Math.floor(p[0]/cellX),Math.floor(p[1]/cellY)];
 const add=(p,kind)=>{const k=key(p).join(',');if(!buckets.has(k))buckets.set(k,[]);buckets.get(k).push({p,kind});};
 const near=p=>{const [x,y]=key(p);let proposed=false;for(let i=x-3;i<=x+3;i++)for(let j=y-3;j<=y+3;j++)for(const q of buckets.get(`${i},${j}`)||[])if(distanceMiles(p,q.p)<spacingMiles-1e-8){if(q.kind==='existing')return 'existing';proposed=true;}return proposed?'proposed':null;};
 existing.forEach(p=>add(p,'existing'));const sites=[];let limitReached=false,blocked=0,waterExcluded=0,existingBlocked=0,proposedBlocked=0,excludedPoints=0,gapAdded=0;
 const scanlines=new Map();
 const offsets=fillGaps?[[0,0],[.5,0],[.25,.5],[.75,.5]]:[[0,0]];
 // Refine between the initial sample lines without removing accepted sites.
 if(fillGaps)for(const y of [0,.25,.5,.75])for(const x of [0,.25,.5,.75])if(!offsets.some(([a,b])=>a===x&&b===y))offsets.push([x,y]);
 // Bit-reversed cell order visits distant parts of the grid early. A small
 // building cap therefore does not simply truncate a south-to-north scan.
 const cells=rows*cols,bits=Math.ceil(Math.log2(cells)),slots=2**bits;
 outer:for(let pass=0;pass<offsets.length;pass++)for(let i=0;i<slots;i++){
  let index=0,n=i;for(let bit=0;bit<bits;bit++){index=index*2+(n%2);n=Math.floor(n/2);}
  if(index>=cells)continue;
  const r=Math.floor(index/cols),c=index%cols,[ox,oy]=offsets[pass],y=minY+(r+oy)*dy;
  if(!scanlines.has(y)){const spans=spansAt(ps,y);scanlines.set(y,{spans,holes:spans.length?spansAt(ex,y):[],dry:land&&spans.length?spansAt(land,y):null});}
  const {spans,holes,dry}=scanlines.get(y),p=[minX+(c+(r%2)/2+ox)*dx,y];
  do{
   if(!spans.some(([a,b])=>p[0]>=a&&p[0]<b))break;
   if(holes.some(([a,b])=>p[0]>=a&&p[0]<b)){excludedPoints++;break;}
   if(dry&&!dry.some(([a,b])=>p[0]>=a&&p[0]<b)){waterExcluded++;break;}
   const reason=near(p);if(reason){blocked++;if(reason==='existing')existingBlocked++;else proposedBlocked++;break;}
   if(sites.length>=maxBuildings){limitReached=true;break outer;}
   sites.push(p);add(p,'proposed');if(pass)gapAdded++;
  }while(false);
  yield {cellsDone:i+1,cells:slots,count:sites.length,pass:pass+1};
 }

 return {sites,count:sites.length,limitReached,spacingMiles,existingCount:existing.length,blocked,waterExcluded,existingBlocked,proposedBlocked,excludedPoints,gapAdded,distanceBasis:'straight-line',placementStatus:'Geometric proposal: road access and build eligibility require review.'};
}
export function plan(options){const iterator=generatePlan(options);let step;do{step=iterator.next();}while(!step.done);return step.value;}
export async function planAsync(options,{onProgress=()=>{},cancelled=()=>false}={}){
 const iterator=generatePlan(options);let step,lastYield=performance.now(),firstProgress=true;
 do{if(cancelled())throw Error('Planning cancelled.');step=iterator.next();if(!step.done){if(firstProgress||performance.now()-lastYield>=8){onProgress(step.value);firstProgress=false;}if(performance.now()-lastYield>=8){await new Promise(resolve=>setTimeout(resolve,0));lastYield=performance.now();}}}while(!step.done);
 return step.value;
}
