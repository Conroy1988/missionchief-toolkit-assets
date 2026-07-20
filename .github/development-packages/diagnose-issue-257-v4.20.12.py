#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "fix-issue-257-combined-capabilities-v4.20.12.py"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
STAGE_FILE = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "development-package-stage"

# Apply the exact reviewed transformation first.
runpy.run_path(str(PACKAGE), run_name="__main__")

# Neutral preflight deliberately uses the normal validator. The diagnostic hook
# activates only in the publish-capable workspace, where the workflow creates
# the stage file before invoking this package.
if STAGE_FILE.exists():
    result = subprocess.run(
        ["node", str(RUNTIME_TEST)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        output = "\n".join(part for part in (result.stderr, result.stdout) if part).strip()
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        useful = []
        for line in reversed(lines):
            if any(token in line for token in ("AssertionError", "actual:", "expected:", "operator:", "at Object")):
                useful.append(line)
            if len(useful) >= 6:
                break
        detail = " | ".join(reversed(useful)) or (lines[-1] if lines else f"exit {result.returncode}")
        detail = re.sub(r"[^A-Za-z0-9 .,:_+()\-=/]", " ", detail)
        detail = re.sub(r"\s+", " ", detail).strip()[:700]
        STAGE_FILE.write_text(f"issue257-runtime {detail}", encoding="utf-8")
        raise SystemExit(result.returncode)

print("Issue #257 apply-only diagnostic passed")
