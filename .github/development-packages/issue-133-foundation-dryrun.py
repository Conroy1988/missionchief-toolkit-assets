#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
PACKAGE = ROOT / ".github" / "development-packages" / "issue-133-foundation.py"
REPORT = ROOT / "docs" / "issue-133-foundation-dryrun.json"

with tempfile.TemporaryDirectory(prefix="mcms-issue-133-") as temp_dir:
    temp_root = Path(temp_dir) / "repo"
    shutil.copytree(
        ROOT,
        temp_root,
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"),
    )
    temp_package = temp_root / PACKAGE.relative_to(ROOT)
    result = subprocess.run(
        [sys.executable, str(temp_package)],
        cwd=temp_root,
        capture_output=True,
        text=True,
    )
    payload = {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "generated": {
            "source": (temp_root / "src" / "MissionChief_Map_Command_Toolkit.user.js").exists(),
            "fixture": (temp_root / ".github" / "fixtures" / "mission-requirements-contract.json").exists(),
            "test": (temp_root / ".github" / "scripts" / "test_mission_requirements_contract.py").exists(),
        },
    }

REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"Wrote {REPORT.relative_to(ROOT)}")
