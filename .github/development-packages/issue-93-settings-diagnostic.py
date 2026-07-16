#!/usr/bin/env python3
from pathlib import Path
import tempfile
import traceback
import subprocess

root = Path(__file__).resolve().parents[2]
output = root / ".github" / "diagnostics" / "issue-93-settings-diagnostic.txt"
output.parent.mkdir(parents=True, exist_ok=True)
package = root / ".github" / "development-packages" / "issue-93-settings-contract-fix.py"
with tempfile.TemporaryDirectory(prefix="issue93-") as temp:
    temp_root = Path(temp)
    subprocess.run(["cp", "-a", str(root) + "/.", str(temp_root)], check=True)
    temp_package = temp_root / ".github" / "development-packages" / package.name
    try:
        code = temp_package.read_text(encoding="utf-8")
        namespace = {"__name__": "__main__", "__file__": str(temp_package)}
        exec(compile(code, str(temp_package), "exec"), namespace, namespace)
        report = "Settings contract package completed successfully in the isolated copy.\n"
    except BaseException:
        report = traceback.format_exc()
output.write_text(report, encoding="utf-8")
print(report)
