#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SHELL_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-operational-suite-shell.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue378-shell-validation-after-contract-fix.txt"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )


if not SHELL_PACKAGE.is_file() or SHELL_PACKAGE.is_symlink():
    raise RuntimeError("corrected Issue #378 shell package is missing or invalid")
package_text = SHELL_PACKAGE.read_text(encoding="utf-8")
if "repository: 'LSSM-V.4'" not in package_text:
    raise RuntimeError("corrected upstream repository marker is absent")
if "repository: 'LSS-Manager/LSSM-V.4'" in package_text:
    raise RuntimeError("forbidden upstream organisation marker remains in shell package")

shell_result = run([sys.executable, str(SHELL_PACKAGE)])
if shell_result.returncode == 0:
    SHELL_PACKAGE.unlink()
validator = run([sys.executable, ".github/scripts/validate_userscript.py"])
syntax = run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"])
parity = run([
    "cmp",
    "--silent",
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
])
report = [
    "ISSUE378_SHELL_VALIDATION_DIAGNOSTIC_V2",
    f"shell_returncode={shell_result.returncode}",
    f"validator_returncode={validator.returncode}",
    f"syntax_returncode={syntax.returncode}",
    f"distribution_parity_returncode={parity.returncode}",
    "--- shell stdout ---",
    shell_result.stdout,
    "--- shell stderr ---",
    shell_result.stderr,
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

# Observational package: restore the exact branch state before the outer guard validates it.
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
print(f"Persisted corrected Issue #378 validation diagnostics to {OUTPUT.relative_to(ROOT)}")
