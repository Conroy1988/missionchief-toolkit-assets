#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue464-release-monitor.txt'
HEADERS = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'MissionChief-Toolkit-Issue464-Release-Monitor',
    'X-GitHub-Api-Version': '2022-11-28',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

def get_json(url: str):
    request = urllib.request.Request(f'{url}{"&" if "?" in url else "?"}_={time.time_ns()}', headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

comments = get_json('https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/464/comments?per_page=100&page=2')
runs = get_json('https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/actions/runs?per_page=30&event=issue_comment')
lines = ['Issue #464 production release monitor', 'LATEST COMMENTS', '']
for comment in comments[-15:]:
    lines.extend([
        '=' * 105,
        f"id={comment.get('id')} created_at={comment.get('created_at')} author={(comment.get('user') or {}).get('login')}",
        str(comment.get('body') or ''),
        '',
    ])
lines.extend(['', 'LATEST ISSUE-COMMENT WORKFLOW RUNS', ''])
for run in (runs.get('workflow_runs') or [])[:15]:
    lines.append(
        f"id={run.get('id')} name={run.get('name')} status={run.get('status')} conclusion={run.get('conclusion')} "
        f"head_sha={run.get('head_sha')} created_at={run.get('created_at')} updated_at={run.get('updated_at')}"
    )
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
