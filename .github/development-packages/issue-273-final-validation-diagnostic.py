#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOTFIX = ROOT / ".github/development-packages/issue-273-shared-exact-personnel-hotfix.py"
VALIDATOR = ROOT / ".github/scripts/validate_userscript.py"
REPORT = ROOT / "docs/issue-273-final-validation-diagnostic.txt"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def main() -> None:
    sections: list[str] = []
    hotfix = run(["python3", str(HOTFIX)])
    sections.append(f"HOTFIX RETURN CODE: {hotfix.returncode}\n\nSTDOUT:\n{hotfix.stdout}\n\nSTDERR:\n{hotfix.stderr}")
    if hotfix.returncode == 0:
        validation = run(["python3", str(VALIDATOR)])
        sections.append(f"VALIDATOR RETURN CODE: {validation.returncode}\n\nSTDOUT:\n{validation.stdout}\n\nSTDERR:\n{validation.stderr}")
        syntax = run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"])
        sections.append(f"NODE CHECK RETURN CODE: {syntax.returncode}\n\nSTDOUT:\n{syntax.stdout}\n\nSTDERR:\n{syntax.stderr}")
    reset = run(["git", "reset", "--hard", "HEAD"])
    clean = run(["git", "clean", "-fd"])
    if reset.returncode != 0 or clean.returncode != 0:
        raise RuntimeError(f"Unable to restore diagnostic workspace: {reset.stderr} {clean.stderr}")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n\n=====\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
