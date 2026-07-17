#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
PACKAGE_REL = Path(".github/development-packages/issue-133-foundation.py")
VALIDATOR_REL = Path(".github/scripts/validate_userscript.py")
SOURCE_REL = Path("src/MissionChief_Map_Command_Toolkit.user.js")
REPORT = ROOT / "docs" / "issue-133-foundation-validation-dryrun.json"


def run(command: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-30000:],
        "stderr": result.stderr[-30000:],
    }

with tempfile.TemporaryDirectory(prefix="mcms-issue-133-validation-") as temp_dir:
    temp_root = Path(temp_dir) / "repo"
    shutil.copytree(
        ROOT,
        temp_root,
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"),
    )
    package_result = run([sys.executable, str(temp_root / PACKAGE_REL)], temp_root)
    payload: dict[str, object] = {"package": package_result}
    if package_result["returncode"] == 0:
        payload["validator"] = run([sys.executable, str(temp_root / VALIDATOR_REL)], temp_root)
        payload["node_check"] = run(["node", "--check", str(temp_root / SOURCE_REL)], temp_root)

REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"Wrote {REPORT.relative_to(ROOT)}")
