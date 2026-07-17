#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
WRAPPER_REL = Path(".github/development-packages/issue-133-foundation-v2.py")
VALIDATOR_REL = Path(".github/scripts/validate_userscript.py")
REPORT = ROOT / "docs" / "issue-133-v2-diagnostics.json"


def run(command: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-50000:],
        "stderr": result.stderr[-50000:],
    }

with tempfile.TemporaryDirectory(prefix="mcms-issue-133-v2-") as temp_dir:
    worktree = Path(temp_dir) / "repo"
    add = run(["git", "worktree", "add", "--detach", str(worktree), "HEAD"], ROOT)
    payload: dict[str, object] = {"worktree_add": add}
    try:
        if add["returncode"] == 0:
            package = run([sys.executable, str(worktree / WRAPPER_REL)], worktree)
            payload["wrapper"] = package
            if package["returncode"] == 0:
                payload["validator"] = run([sys.executable, str(worktree / VALIDATOR_REL)], worktree)
                payload["node_check"] = run(["node", "--check", str(worktree / "src/MissionChief_Map_Command_Toolkit.user.js")], worktree)
                payload["diff_stat"] = run(["git", "diff", "--stat"], worktree)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT, capture_output=True, text=True)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True, text=True)

REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"Wrote {REPORT.relative_to(ROOT)}")
