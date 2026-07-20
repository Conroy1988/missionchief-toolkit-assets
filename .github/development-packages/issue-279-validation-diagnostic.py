#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression-v3.py"
OUTPUT = ROOT / "docs/issue-279-validation-diagnostic.txt"


def run(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def main() -> None:
    package = run([sys.executable, str(PACKAGE)])
    preflight = run(["bash", ".github/scripts/run_userscript_preflight.sh", "--all"]) if package[0] == 0 else (-1, "", "package failed")
    node_check = run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"]) if package[0] == 0 else (-1, "", "package failed")

    subprocess.run(["git", "restore", "--", "."], cwd=ROOT, check=True)
    subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)

    sections = []
    for name, result in [("PACKAGE", package), ("PREFLIGHT", preflight), ("NODE CHECK", node_check)]:
        code, stdout, stderr = result
        sections.append(f"{name} RETURN CODE: {code}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n\n=====\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Captured Issue 279 validator transcript at {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
