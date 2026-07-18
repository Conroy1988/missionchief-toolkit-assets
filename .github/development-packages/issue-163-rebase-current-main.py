#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
POLICY = ROOT / ".github" / "performance-budget.json"
CHECKER = ROOT / ".github" / "scripts" / "check_performance_budget.py"
DOC = ROOT / "docs" / "issue-163-mission-catalogue-resolver-contract.md"


def run(*cmd: str) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


source = SOURCE.read_text(encoding="utf-8")
assert "// @version      4.16.0" in source
assert "version: '4.16.0'" in source
assert SOURCE.read_bytes() == DIST.read_bytes()
assert json.loads(POLICY.read_text(encoding="utf-8"))["revision"] == "2026-07-18-v4.16.0"

note = "\nThe final candidate was rebased onto the post-v4.15.5 Greasy Fork version-reconciliation commit before merge.\n"
doc = DOC.read_text(encoding="utf-8")
if note.strip() not in doc:
    DOC.write_text(doc.rstrip() + "\n" + note, encoding="utf-8")

with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    base = temp / "main.user.js"
    base.write_bytes(subprocess.check_output(["git", "show", "origin/main:src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT))
    run(
        "python3", str(CHECKER.relative_to(ROOT)),
        "--candidate", str(SOURCE.relative_to(ROOT)),
        "--base", str(base),
        "--policy", str(POLICY.relative_to(ROOT)),
        "--json-output", str(temp / "report.json"),
        "--markdown-output", str(temp / "report.md"),
    )
    assert json.loads((temp / "report.json").read_text(encoding="utf-8"))["result"] == "success"

run("node", "--check", str(SOURCE.relative_to(ROOT)))
run("node", str(RUNTIME.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
print("Issue #163 candidate validated for current-main rebase")
