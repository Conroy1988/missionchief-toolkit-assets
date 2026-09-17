"""Verify and package the exact submitted 2.0.0 payload; never compose an older baseline."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
inventory=json.loads((ROOT/'release-2.0.0.json').read_text())
source=ROOT/'current'
actual={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file()}
if actual != inventory['files']:
 missing=sorted(set(inventory['files'])-set(actual)); added=sorted(set(actual)-set(inventory['files']))
 changed=sorted(p for p in actual.keys() & inventory['files'].keys() if actual[p]!=inventory['files'][p])
 raise SystemExit(f'Release integrity failed: missing={missing}, added={added}, changed={changed}')
manifest=json.loads((source/'manifest.json').read_text())
if manifest['version']!=inventory['version'] or len(actual)!=inventory['fileCount']:
 raise SystemExit('Release version or file count mismatch')
out=ROOT.parent/'.dev';out.mkdir(exist_ok=True)
archive=out/f"MissionChief-Toolkit-Extension-{inventory['version']}.zip"
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name in actual:
  info=zipfile.ZipInfo(name,(2026,9,17,0,0,0));info.external_attr=0o100644<<16
  z.writestr(info,(source/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(archive) as z:
 if z.testzip() or {n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}!=actual:
  raise SystemExit('Packaged payload failed read-back verification')
print(json.dumps({'archive':str(archive),'version':manifest['version'],'files':len(actual),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'payloadVerified':True},indent=2))
