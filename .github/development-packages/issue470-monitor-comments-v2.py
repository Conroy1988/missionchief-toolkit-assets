#!/usr/bin/env python3
from __future__ import annotations
import json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SELF=Path(__file__).resolve();OUT=ROOT/'.github/diagnostics/issue470-monitor-comments.txt'
url=f'https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/470/comments?per_page=100&page=1&_={time.time_ns()}'
req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'Toolkit-Issue-470-Monitor','Cache-Control':'no-cache'})
with urllib.request.urlopen(req,timeout=30) as response: comments=json.loads(response.read().decode())
lines=[f'count={len(comments)}','']
for item in comments[-35:]: lines.extend(['='*100,f"id={item.get('id')} at={item.get('created_at')} author={(item.get('user') or {}).get('login')}",str(item.get('body') or ''),''])
OUT.write_text('\n'.join(lines),encoding='utf-8');SELF.unlink(missing_ok=True);print(OUT.relative_to(ROOT))
