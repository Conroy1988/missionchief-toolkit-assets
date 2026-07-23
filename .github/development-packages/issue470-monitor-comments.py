#!/usr/bin/env python3
from __future__ import annotations
import json
import time
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SELF=Path(__file__).resolve()
OUT=ROOT/'.github/diagnostics/issue470-monitor-comments.txt'
url=f'https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/470/comments?per_page=100&page=3&_={time.time_ns()}'
request=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'Toolkit-Issue-470-Monitor','X-GitHub-Api-Version':'2022-11-28','Cache-Control':'no-cache'})
with urllib.request.urlopen(request,timeout=30) as response: comments=json.loads(response.read().decode('utf-8'))
lines=[f'count={len(comments)}','']
for item in comments[-30:]: lines.extend(['='*100,f"id={item.get('id')} at={item.get('created_at')} author={(item.get('user') or {}).get('login')}",str(item.get('body') or ''),''])
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines),encoding='utf-8');SELF.unlink(missing_ok=True);print(OUT.relative_to(ROOT))
