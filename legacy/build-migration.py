"""Build the final notification update without changing the historical source."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]
source=(root/'src/MissionChief_Map_Command_Toolkit.user.js').read_text()
version='10.18.2'
old=re.search(r'^//\s*@version\s+(\S+)',source,re.M).group(1)
assert tuple(map(int,version.split('.')))>tuple(map(int,old.split('.')))
# Retain name, namespace, permissions and established update URLs.
source=source.replace(old,version)
notice=(root/'legacy/migration-notice.js').read_text()
marker='// ==/UserScript=='
i=source.index(marker)+len(marker)
payload=source[:i]+'\n\n'+notice+'\n'+source[i:]
folder=root/'.dev/legacy-migration';folder.mkdir(parents=True,exist_ok=True)
for name in ['MissionChief_Map_Command_Toolkit.user.js','MissionChief_Map_Command_Toolkit.update.user.js','MissionChief_Map_Command_Toolkit.install.user.js']:
 (folder/name).write_text(payload)
(folder/'MissionChief_Map_Command_Toolkit.meta.js').write_text(source[:i]+'\n')
manifest={'version':version,'previousVersion':old,'purpose':'Final userscript migration notice; unsupported runtime retained for export','deployment':'prepared-not-live','storeUrl':'https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc','sha256':hashlib.sha256(payload.encode()).hexdigest()}
(folder/'migration-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
