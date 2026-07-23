#!/usr/bin/env python3
from __future__ import annotations
import json
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SELF=Path(__file__).resolve()
OUT=ROOT/'.github/diagnostics/issue464-latest-comments-v4.txt'
req=urllib.request.Request('https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/464/comments?per_page=100',headers={'Accept':'application/vnd.github+json','User-Agent':'MissionChief-Toolkit-Issue464-Diagnostic','X-GitHub-Api-Version':'2022-11-28'})
with urllib.request.urlopen(req,timeout=30) as response: comments=json.loads(response.read().decode('utf-8'))
lines=[f'count={len(comments)}','']
for comment in comments[-10:]: lines.extend(['='*90,f"id={comment.get('id')} at={comment.get('created_at')} author={(comment.get('user') or {}).get('login')}",str(comment.get('body') or ''),''])
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines),encoding='utf-8');SELF.unlink(missing_ok=True);print(OUT.relative_to(ROOT))
