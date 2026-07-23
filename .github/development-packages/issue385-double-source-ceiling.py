#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION_CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
PERFORMANCE_BUDGET = ROOT / ".github" / "performance-budget.json"
COMPACTOR = ROOT / ".github" / "development-packages" / "issue378-compact-engine-source.py"

version_text = VERSION_CONTRACT.read_text(encoding="utf-8")
old_version = 'assert len(source.splitlines()) <= 32000, "source exceeds release performance line ceiling"'
new_version = 'assert len(source.splitlines()) <= 64000, "source exceeds release performance line ceiling"'
if version_text.count(old_version) != 1:
    raise RuntimeError("version-status source ceiling anchor changed")
VERSION_CONTRACT.write_text(version_text.replace(old_version, new_version, 1), encoding="utf-8")

budget = json.loads(PERFORMANCE_BUDGET.read_text(encoding="utf-8"))
if budget.get("absoluteLimits", {}).get("lines") != 32000:
    raise RuntimeError("performance-budget line ceiling is not the expected 32,000 baseline")
budget["absoluteLimits"]["lines"] = 64000
budget["revision"] = "2026-07-23-issue-385-64k-source-ceiling"
budget["rationale"] = (
    "Issue #385 owner-authorized policy change: double the canonical userscript absolute line ceiling "
    "from 32,000 to 64,000 lines for the Issue #378 major operational-suite programme. All byte, CSS, "
    "observer, timer, listener, selector and network ceilings remain unchanged; relative-growth review "
    "thresholds remain active."
)
PERFORMANCE_BUDGET.write_text(json.dumps(budget, indent=2) + "\n", encoding="utf-8")

compactor_text = COMPACTOR.read_text(encoding="utf-8")
old_compactor = "if source_lines > 32000:"
new_compactor = "if source_lines > 64000:"
if compactor_text.count(old_compactor) != 1:
    raise RuntimeError("Issue #378 compactor source ceiling anchor changed")
COMPACTOR.write_text(compactor_text.replace(old_compactor, new_compactor, 1), encoding="utf-8")

subprocess.run([sys.executable, ".github/scripts/test_version_status_contract.py"], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)

print("Issue #385 doubled the userscript source ceiling from 32,000 to 64,000 lines; all other performance ceilings remain unchanged.")
