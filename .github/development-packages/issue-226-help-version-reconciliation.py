#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HELP = ROOT / "help" / "index.html"

text = HELP.read_text(encoding="utf-8")
old = "Guide for Toolkit v4.20.3"
new = "Guide for Toolkit v4.20.9"
count = text.count(old)
if count != 1:
    raise AssertionError(f"Help Centre version marker: expected one match, found {count}")
HELP.write_text(text.replace(old, new, 1), encoding="utf-8")

subprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/test_mission_requirements_contract.py"], cwd=ROOT, check=True)
subprocess.run([
    sys.executable,
    ".github/scripts/check_documentation_drift.py",
    "--allow-release-candidate",
    "--json-output", "/tmp/issue-226-documentation-drift.json",
    "--markdown-output", "/tmp/issue-226-documentation-drift.md",
], cwd=ROOT, check=True)
print("Issue #226 Help Centre version reconciliation validated")
