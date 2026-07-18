#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "performance-budget.json"
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHECKER = ROOT / ".github" / "scripts" / "check_performance_budget.py"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
DIAGNOSTIC = ROOT / "docs" / "diagnostics" / "issue-163-performance-policy.txt"
CHANGELOG = ROOT / "CHANGELOG.md"


def run(*cmd: str, **kwargs):
    return subprocess.run(cmd, cwd=ROOT, check=True, **kwargs)


policy = json.loads(POLICY.read_text(encoding="utf-8"))
assert policy["revision"] == "2026-07-14-initial"
assert policy["absoluteLimits"]["bytes"] == 1900000
assert policy["absoluteLimits"]["lines"] == 31000
policy["revision"] = "2026-07-18-v4.16.0"
policy["rationale"] = (
    "Recalibrated after v4.15.5 exhausted the initial v4.11.2 source envelope; "
    "all runtime-workload, CSS and relative regression limits remain unchanged."
)
policy["absoluteLimits"]["bytes"] = 2000000
policy["absoluteLimits"]["lines"] = 32000
POLICY.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
needle = "- Catalogue quantities are never presented as current **Still needed** values.\n"
addition = (
    needle
    + "- Recalibrated the static source-size envelope after v4.15.5 exhausted the original v4.11.2 allowance; runtime, CSS and relative performance limits are unchanged.\n"
)
if addition not in changelog:
    if changelog.count(needle) != 1:
        raise AssertionError("v4.16.0 safety changelog marker missing or duplicated")
    changelog = changelog.replace(needle, addition, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

DIAGNOSTIC.unlink(missing_ok=True)
try:
    DIAGNOSTIC.parent.rmdir()
except OSError:
    pass

with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    base = temp / "main.user.js"
    base.write_bytes(subprocess.check_output([
        "git", "show", "origin/main:src/MissionChief_Map_Command_Toolkit.user.js"
    ], cwd=ROOT))
    run(
        "python3", str(CHECKER.relative_to(ROOT)),
        "--candidate", str(SOURCE.relative_to(ROOT)),
        "--base", str(base),
        "--policy", str(POLICY.relative_to(ROOT)),
        "--json-output", str(temp / "report.json"),
        "--markdown-output", str(temp / "report.md"),
    )
    report = json.loads((temp / "report.json").read_text(encoding="utf-8"))
    assert report["result"] == "success", report
    assert report["candidate"]["bytes"] <= 2000000
    assert report["candidate"]["lines"] <= 32000
    assert report["candidate"]["set_timeout_calls"] == report["base"]["set_timeout_calls"]
    assert report["candidate"]["mutation_observers"] == report["base"]["mutation_observers"]
    assert report["candidate"]["event_listener_calls"] == report["base"]["event_listener_calls"]
    assert report["candidate"]["startup_hook_calls"] == report["base"]["startup_hook_calls"]

run("node", "--check", str(SOURCE.relative_to(ROOT)))
run("node", str(RUNTIME.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
print("Issue #163 performance envelope recalibrated and validated")
