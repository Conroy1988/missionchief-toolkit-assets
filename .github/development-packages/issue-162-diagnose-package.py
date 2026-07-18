#!/usr/bin/env python3
from pathlib import Path
import subprocess
import traceback

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".github" / "development-packages" / "issue-162-report-template-label.py"
OUT = ROOT / "docs" / "diagnostics" / "issue-162-package-error.txt"

result = subprocess.run(["python3", str(TARGET.relative_to(ROOT))], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
report = ["Issue #162 package diagnostic", f"return_code={result.returncode}", "", result.stdout[-12000:]]
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
subprocess.run(["git", "clean", "-fd", "--", ".github/ISSUE_TEMPLATE/mission-info-missing.yml"], cwd=ROOT, check=False, stdout=subprocess.DEVNULL)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
print("Issue #162 diagnostic captured")
