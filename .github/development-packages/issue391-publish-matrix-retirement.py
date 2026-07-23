#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
CHAIN = (
    ROOT / ".github" / "development-packages" / "issue391-update-post-retirement-settings-contract.py",
    ROOT / ".github" / "development-packages" / "issue391-finalize-canonical-retirement.py",
    ROOT / ".github" / "development-packages" / "issue391-retire-matrix.py",
)
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "full-userscript-audit.yml"
CANONICAL = (
    SOURCE,
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
)

original_workflow = WORKFLOW.read_text(encoding="utf-8")
for package in CHAIN:
    if not package.exists():
        raise RuntimeError(f"retirement chain package missing: {package.relative_to(ROOT)}")
    subprocess.run(["python3", str(package)], cwd=ROOT, env=ENV, check=True)

# The GitHub Actions token used by the guarded publisher may not update workflow
# files. Publish the validated runtime/contract cutover first; the equivalent
# workflow path update is committed separately through the repository connector.
WORKFLOW.write_text(original_workflow, encoding="utf-8")

source = SOURCE.read_text(encoding="utf-8")
for token in (
    "Issue #133 clean-room live mission requirements matrix",
    "function installMissionRequirementsWindows(",
    "function scanMissionRequirementsWindows(",
    "scheduleMissionRequirementsScan(",
    "missionRequirementsPanelId",
    "state.missionRequirements",
    "makeToggleButton('missionRequirements'",
):
    if token in source:
        raise RuntimeError(f"legacy Matrix token survived published retirement: {token}")
if source.count("function handleOperationalWindowSettingChange(") != 1:
    raise RuntimeError("operational settings handler was not preserved exactly once")
if "matrixRetired: true" not in source:
    raise RuntimeError("Matrix retirement migration flag is missing")

reference = source
for path in CANONICAL:
    if path.read_text(encoding="utf-8") != reference:
        raise RuntimeError(f"canonical distribution drift after Matrix retirement: {path.relative_to(ROOT)}")

subprocess.run(["bash", str(PREFLIGHT), "--contracts"], cwd=ROOT, env=ENV, check=True)

current = Path(__file__).resolve()
for path in (ROOT / ".github" / "development-packages").glob("issue391-*.py"):
    if path.resolve() != current:
        path.unlink(missing_ok=True)
for path in (ROOT / ".github" / "diagnostics").glob("issue391-*.txt"):
    path.unlink(missing_ok=True)

print("Issue #391 Matrix retirement published; full contract suite passed. Workflow path update deferred to connector commit.")
