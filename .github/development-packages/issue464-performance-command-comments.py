#!/usr/bin/env python3
import json
import time
import urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[2]
self_path=Path(__file__).resolve()
out=root/'.github/diagnostics/issue464-performance-command-comments.txt'
url=f'https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/464/comments?per_page=100&page=2&_={time.time_ns()}'
request=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'Toolkit-Issue-464-Performance-Diagnostic','Cache-Control':'no-cache'})
with urllib.request.urlopen(request,timeout=30) as response: comments=json.loads(response.read().decode())
lines=[]
for item in comments[-18:]: lines.extend([str(item.get('id')),str(item.get('created_at')),str((item.get('user') or {}).get('login')),str(item.get('body') or ''),'---'])
out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(lines),encoding='utf-8');self_path.unlink(missing_ok=True);print(out.relative_to(root))
