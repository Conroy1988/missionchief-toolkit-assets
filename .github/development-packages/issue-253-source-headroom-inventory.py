#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/development-packages/issue-253-source-headroom-inventory.mjs"


def main() -> int:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run(
        ["npm", "install", "--no-save", "--ignore-scripts", "--no-audit", "--no-fund", "acorn@8.15.0"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    subprocess.run(["node", "--check", str(SCRIPT)], cwd=ROOT, env=env, check=True)
    subprocess.run(["node", str(SCRIPT)], cwd=ROOT, env=env, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
