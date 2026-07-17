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

runtime_check = subprocess.run(["node", str(TEST)], cwd=ROOT, text=True, capture_output=True)
if runtime_check.returncode != 0:
    combined = "\n".join(part for part in [runtime_check.stdout, runtime_check.stderr] if part)
    diagnostic = " ".join(combined.strip().split())[-900:] or "unknown lifecycle fixture failure"
    diagnostic = diagnostic.replace("**", "").replace("`", "'")
    stage = Path(__import__("os").environ.get("RUNNER_TEMP", "/tmp")) / "development-package-stage"
    stage.write_text(f"lifecycle-runtime-fixture: {diagnostic}", encoding="utf-8")
    if runtime_check.stdout:
        print(runtime_check.stdout, end="")
    if runtime_check.stderr:
        print(runtime_check.stderr, end="", file=sys.stderr)
    raise SystemExit(runtime_check.returncode)

validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(TEST)], cwd=ROOT, check=True)
print("Added isolated Issue #133 lifecycle VM state")
