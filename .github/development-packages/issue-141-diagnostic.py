#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".github" / "development-packages" / "issue-141-mission-requirements-completeness.py"

result = subprocess.run(
    [sys.executable, str(TARGET)],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
if result.returncode == 0:
    print(result.stdout)
    raise SystemExit(0)

output = result.stdout[-10000:]
output = re.sub(r"(?i)(authorization:\s*(?:basic|bearer)\s+)[^\s]+", r"\1[redacted]", output)
body = "Issue #141 package diagnostic (bounded, no production commit):\n\n```text\n" + output + "\n```"

header = subprocess.check_output(
    ["git", "config", "--local", "--get", "http.https://github.com/.extraheader"],
    cwd=ROOT,
    text=True,
).strip()
if ":" not in header:
    raise RuntimeError("GitHub checkout authorization header unavailable")
name, value = header.split(":", 1)
request = urllib.request.Request(
    "https://api.github.com/repos/Conroy1988/missionchief-toolkit-assets/issues/141/comments",
    data=json.dumps({"body": body}).encode("utf-8"),
    headers={
        name.strip(): value.strip(),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "missionchief-toolkit-diagnostic",
    },
    method="POST",
)
with urllib.request.urlopen(request, timeout=20) as response:
    if response.status not in (200, 201):
        raise RuntimeError(f"Diagnostic comment failed with HTTP {response.status}")

print(output)
raise SystemExit(result.returncode)
