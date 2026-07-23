#!/usr/bin/env python3
from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue464-final-preflight-log.txt'
URL = 'https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/actions/jobs/89302259524/logs'
request = urllib.request.Request(URL, headers={
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'MissionChief-Toolkit-Issue464-Diagnostic',
    'X-GitHub-Api-Version': '2022-11-28',
})
with urllib.request.urlopen(request, timeout=45) as response:
    payload = response.read()
text = payload.decode('utf-8', errors='replace')
lines = text.splitlines()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines[-260:]) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
