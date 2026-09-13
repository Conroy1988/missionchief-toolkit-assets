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
export function plan({geometry,spacingMiles,existing=[],excluded=[],maxBuildings=500}){
  if(!SPACING_MILES.includes(spacingMiles))throw Error('Unsupported spacing.');
  if(!Number.isInteger(maxBuildings)||maxBuildings<1||maxBuildings>500)throw Error('Choose 1–500 buildings.');
  if(existing.some(p=>!valid(p)))throw Error('Existing building coordinates are incomplete. Refresh buildings before planning.');
  const ps=polygons(geometry),ex=excluded.map(polygons);
  const inside=(polys,p)=>polys.some(poly=>inRing(p,poly[0])&&!poly.slice(1).some(r=>inRing(p,r)));
  const coords=ps.flat(2);if(coords.length>20000)throw Error('Boundary is too detailed. Draw a simpler area.');const xs=coords.map(p=>p[0]),ys=coords.map(p=>p[1]);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
  if(minX < -9 || maxX > 3 || minY < 49 || maxY > 61)throw Error('Select an area within the UK planning bounds.');
  const dy=spacingMiles/69*0.8660254, midY=(minY+maxY)/2,dx=spacingMiles/(69.172*Math.cos(rad(midY)));
  const rows=Math.ceil((maxY-minY)/dy)+1,cols=Math.ceil((maxX-minX)/dx)+2;
  if(rows*cols*(coords.length+ex.flat(3).length)>10000000)throw Error('Area is too detailed at this spacing. Draw a simpler boundary or increase spacing.');
  if(rows*cols>60000)throw Error('Area is too large at this spacing. Split it into smaller areas.');
  // A spatial index bounds neighbour checks, including existing sites outside the area.
  const cellY=spacingMiles/69.2,cellX=spacingMiles/(69.2*Math.cos(rad(minY))),buckets=new Map();
  const key=p=>[Math.floor(p[0]/cellX),Math.floor(p[1]/cellY)];
  const add=p=>{const k=key(p).join(',');if(!buckets.has(k))buckets.set(k,[]);buckets.get(k).push(p);};
  const near=p=>{const [x,y]=key(p);for(let i=x-3;i<=x+3;i++)for(let j=y-3;j<=y+3;j++)for(const q of buckets.get(`${i},${j}`)||[])if(distanceMiles(p,q)<spacingMiles-1e-8)return true;return false;};
  existing.forEach(add);const sites=[];let limitReached=false,blocked=0;
  for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
    const p=[minX+(c+(r%2)/2)*dx,minY+r*dy];
    if(!inside(ps,p)||ex.some(polys=>inside(polys,p)))continue;
    if(near(p)){blocked++;continue;}
    if(sites.length>=maxBuildings){limitReached=true;continue;}
    sites.push(p);add(p);
  }
  return {sites,count:sites.length,limitReached,spacingMiles,existingCount:existing.length,blocked,
    distanceBasis:'straight-line',placementStatus:'Geometric proposal: road access and build eligibility require review.'};
}
