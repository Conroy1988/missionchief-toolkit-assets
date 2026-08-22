#!/usr/bin/env python3
"""Install the pinned disposable Node runtime used by local Toolkit contracts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"jsdom": "26.1.0", "acorn": "8.15.0"}


def installed() -> bool:
    for package, version in REQUIRED.items():
        path = ROOT / "node_modules" / package / "package.json"
        if not path.is_file():
            return False
        try:
            if json.loads(path.read_text(encoding="utf-8")).get("version") != version:
                return False
        except (OSError, json.JSONDecodeError):
            return False
    return True


def main() -> int:
    if installed():
        print("[dev-dependencies] pinned local runtime already available")
        return 0
    if not shutil.which("node") or not shutil.which("npm"):
        raise SystemExit("Node.js and npm are required for Toolkit runtime contracts")
    packages = [f"{package}@{version}" for package, version in REQUIRED.items()]
    print(f"[dev-dependencies] installing disposable runtime: {' '.join(packages)}", flush=True)
    subprocess.run(
        [
            "npm", "install", "--no-save", "--package-lock=false", "--ignore-scripts",
            "--no-audit", "--no-fund", *packages,
        ],
        cwd=ROOT,
        check=True,
    )
    if not installed():
        raise SystemExit("Pinned Toolkit development dependencies did not install correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
