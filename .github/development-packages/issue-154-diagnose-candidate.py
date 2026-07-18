#!/usr/bin/env python3
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
driver = root / ".github" / "development-packages" / "issue-154-mission-requirements-report-fallback.py"
result = subprocess.run(
    ["python3", str(driver)],
    cwd=root,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
lines = result.stdout.splitlines()
tail = "\n".join(lines[-120:])
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=root, check=True, stdout=subprocess.DEVNULL)
subprocess.run(["git", "clean", "-fd"], cwd=root, check=True, stdout=subprocess.DEVNULL)
report = root / "docs" / "diagnostics" / "issue-154-candidate-result.txt"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(
    f"Issue #154 candidate diagnostic\nreturn_code={result.returncode}\n\n{tail}\n",
    encoding="utf-8",
)
print(f"Recorded bounded Issue #154 diagnostic with return code {result.returncode}")
