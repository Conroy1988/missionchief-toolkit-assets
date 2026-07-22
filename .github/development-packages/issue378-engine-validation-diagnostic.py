#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-enhanced-requirements-engine-core.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue378-engine-validation-failure.txt"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    )


if not ENGINE_PACKAGE.is_file() or ENGINE_PACKAGE.is_symlink():
    raise RuntimeError("reviewed Issue #378 engine package is missing or invalid")

package_result = run([sys.executable, str(ENGINE_PACKAGE)])
if package_result.returncode == 0:
    ENGINE_PACKAGE.unlink()
validator = run([sys.executable, ".github/scripts/validate_userscript.py"])
syntax = run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"])
parity = run([
    "cmp",
    "--silent",
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
])
report = [
    "ISSUE378_ENGINE_VALIDATION_DIAGNOSTIC",
    f"package_returncode={package_result.returncode}",
    f"validator_returncode={validator.returncode}",
    f"syntax_returncode={syntax.returncode}",
    f"distribution_parity_returncode={parity.returncode}",
    "--- package stdout ---",
    package_result.stdout,
    "--- package stderr ---",
    package_result.stderr,
    "--- validator stdout ---",
    validator.stdout,
    "--- validator stderr ---",
    validator.stderr,
    "--- node stdout ---",
    syntax.stdout,
    "--- node stderr ---",
    syntax.stderr,
    "--- parity stdout ---",
    parity.stdout,
    "--- parity stderr ---",
    parity.stderr,
]

subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
print(f"Persisted Issue #378 engine validation diagnostics to {OUTPUT.relative_to(ROOT)}")
