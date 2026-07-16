#!/usr/bin/env python3
from pathlib import Path
import shutil
import tempfile
import traceback

root = Path(__file__).resolve().parents[2]
output = root / ".github" / "diagnostics" / "issue-93-final2-package-error.txt"
output.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="issue-93-final2-") as temp:
    sandbox = Path(temp) / "repo"
    shutil.copytree(root, sandbox, ignore=shutil.ignore_patterns(".git"))
    package = sandbox / ".github" / "development-packages" / "issue-93-mission-value-final2.py"
    try:
        code = package.read_text(encoding="utf-8")
        namespace = {"__name__": "__main__", "__file__": str(package)}
        exec(compile(code, str(package), "exec"), namespace, namespace)
        report = "Final2 package completed successfully in the isolated copy.\n"
    except BaseException:
        report = traceback.format_exc()
output.write_text(report, encoding="utf-8")
print(report)
