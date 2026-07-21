#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/development-packages/issue-253-style-assignment-inspection.mjs"


def main() -> int:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run(
        ["npm", "install", "--no-save", "--ignore-scripts", "--no-audit", "--no-fund", "acorn@8.15.0"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    try:
        subprocess.run(["node", "--check", str(SCRIPT)], cwd=ROOT, env=env, check=True)
        subprocess.run(["node", str(SCRIPT)], cwd=ROOT, env=env, check=True)
    finally:
        shutil.rmtree(ROOT / "node_modules", ignore_errors=True)
        (ROOT / "package-lock.json").unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
