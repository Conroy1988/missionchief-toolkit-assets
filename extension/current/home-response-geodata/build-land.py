"""Rebuild the bundled UK planning mask: python build-land.py /path/gshhg-shp-2.3.7.zip.
Requires shapely and pyshp. Data is LGPL-3.0-or-later, separate from Toolkit code.
"""
import sys,zipfile,pathlib,json,hashlib,io
import shapefile
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
from shapely import make_valid
root=pathlib.Path(__file__).resolve().parent
archive=pathlib.Path(sys.argv[1]);z=zipfile.ZipFile(archive)
bounds=(-9,49,3,61);clip=box(*bounds);levels=[]
for level in range(1,5):
 stem=f'GSHHS_shp/f/GSHHS_f_L{level}'
 if stem+'.shp' not in z.namelist():levels.append(box(0,0,0,0));continue
 reader=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),shx=io.BytesIO(z.read(stem+'.shx')))
 parts=[]
 for s in reader.iterShapes(bbox=bounds):
  g=make_valid(shape(s.__geo_interface__)).intersection(clip)
  if not g.is_empty:parts.append(g)
 levels.append(unary_union(parts));print('level',level,'polygons',len(parts),flush=True)
land=levels[0].difference(levels[1]).union(levels[2]).difference(levels[3])
# Small inward margin is conservative about uncertain shoreline positions.
land=land.buffer(-.0005).simplify(.00003,preserve_topology=True)
coords=[]
for p in (list(land.geoms) if hasattr(land,'geoms') else [land]):
 if p.geom_type=='Polygon':coords.append([[[round(x,6),round(y,6)] for x,y in r.coords] for r in [p.exterior,*p.interiors]])
data={'type':'MultiPolygon','coordinates':coords}
(root.parent/'land-data.mjs').write_text('// Derived GSHHG 2.3.7 shoreline data; LGPL-3.0-or-later. See geodata/.\nexport const LAND_GEOMETRY='+json.dumps(data,separators=(',',':'))+';\n')
for n in ['LICENSE.TXT','COPYING.LESSERv3','README.TXT']:(root/n).write_bytes(z.read(n))
(root/'provenance.json').write_text(json.dumps({'source':'https://ftp.soest.hawaii.edu/gshhg/gshhg-shp-2.3.7.zip','version':'2.3.7','archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'resolution':'full','bounds':bounds,'inwardMarginDegrees':.0005,'simplificationDegrees':.00003,'limitations':'Historical shoreline dataset. Not all small ponds, narrow waterways or recent changes are mapped. Does not verify road access.'},indent=2)+'\n')
print('mask bytes',(root.parent/'land-data.mjs').stat().st_size)
