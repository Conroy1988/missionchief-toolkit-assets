#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue464-release-comments.txt'
url = f'https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/464/comments?per_page=100&page=2&_={time.time_ns()}'
request = urllib.request.Request(url, headers={
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'MissionChief-Toolkit-Issue464-Release-Diagnostic',
    'X-GitHub-Api-Version': '2022-11-28',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
})
with urllib.request.urlopen(request, timeout=30) as response:
    comments = json.loads(response.read().decode('utf-8'))
lines = [
    'Issue #464 release comment diagnostic',
    f'page_count={len(comments)}',
    '',
]
for comment in comments[-25:]:
    lines.extend([
        '=' * 110,
        f"id={comment.get('id')} created_at={comment.get('created_at')} author={(comment.get('user') or {}).get('login')}",
        str(comment.get('body') or ''),
        '',
    ])
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
