#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).with_name("fix-issue-242-inline-v4.20.10-final.py")
namespace = {"__name__": "__main__", "__file__": str(PACKAGE)}
exec(compile(PACKAGE.read_text(encoding="utf-8"), str(PACKAGE), "exec"), namespace)

result = subprocess.run(
    ["python3", ".github/scripts/validate_userscript.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
report = (
    f"exit_code={result.returncode}\n\n"
    "--- stdout ---\n"
    f"{result.stdout}\n"
    "--- stderr ---\n"
    f"{result.stderr}\n"
)

subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
diagnostic = ROOT / "status" / "issue-242-validator-diagnostic.txt"
diagnostic.write_text(report, encoding="utf-8")
print("Issue 242 validator diagnostic captured; product workspace restored")
