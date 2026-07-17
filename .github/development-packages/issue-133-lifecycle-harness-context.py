#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"

source = TEST.read_text(encoding="utf-8")
old = "    runtime: { destroyed: false },\n"
new = "    runtime: { destroyed: false },\n    missionRequirementsScanTimer: null,\n    missionRequirementsFeatureInstalled: false,\n    missionRequirementsObservedDocuments: new WeakSet(),\n    missionRequirementsObservedFrames: new WeakSet(),\n    missionRequirementsRecords: new Map(),\n"
if source.count(old) != 1:
    raise SystemExit(f"lifecycle VM context anchor: expected one, found {source.count(old)}")
TEST.write_text(source.replace(old, new, 1), encoding="utf-8")
validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(TEST)], cwd=ROOT, check=True)
print("Added isolated Issue #133 lifecycle VM state")
