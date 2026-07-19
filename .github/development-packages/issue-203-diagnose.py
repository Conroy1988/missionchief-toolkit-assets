#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT / ".github" / "development-packages" / "issue-203-version-control-family.py"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"

log_parts: list[str] = []

package = subprocess.run([sys.executable, str(BASE_PACKAGE)], cwd=ROOT, text=True, capture_output=True)
log_parts.append(f"PACKAGE STATUS: {package.returncode}\n{package.stdout}\n{package.stderr}")

validator = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True)
log_parts.append(f"VALIDATOR STATUS: {validator.returncode}\n{validator.stdout}\n{validator.stderr}")

syntax = subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, text=True, capture_output=True)
log_parts.append(f"SYNTAX STATUS: {syntax.returncode}\n{syntax.stdout}\n{syntax.stderr}")

parity = 0 if SOURCE.read_bytes() == DIST.read_bytes() else 1
log_parts.append(f"PARITY STATUS: {parity}")

combined = "\n\n".join(log_parts)
lines = combined.splitlines()[-180:]
body = "\n".join([
    "### Issue #203 guarded validation diagnostic",
    "",
    f"- Package: `{package.returncode}`",
    f"- Canonical validator: `{validator.returncode}`",
    f"- JavaScript syntax: `{syntax.returncode}`",
    f"- Distribution parity: `{parity}`",
    "",
    "<details><summary>Last 180 diagnostic lines</summary>",
    "",
    "```text",
    *lines,
    "```",
    "</details>",
])
repo = os.environ.get("GITHUB_REPOSITORY", "Conroy1988/missionchief-toolkit-assets")
subprocess.run(["gh", "issue", "comment", "203", "--repo", repo, "--body", body], cwd=ROOT, check=False)
raise SystemExit(1)
