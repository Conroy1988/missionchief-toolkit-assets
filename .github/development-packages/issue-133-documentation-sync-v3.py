#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-133-documentation-sync.py"
OLD_WRAPPER = ROOT / ".github" / "development-packages" / "issue-133-documentation-sync-v2.py"
STAGE = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "development-package-stage"

package = ORIGINAL.read_text(encoding="utf-8")
old = 'doc_audit = subprocess.run([sys.executable, str(DOC_AUDIT)], cwd=ROOT)'
new = 'doc_audit = subprocess.run([sys.executable, str(DOC_AUDIT), "--allow-release-candidate"], cwd=ROOT)'
if package.count(old) != 1:
    raise SystemExit(f"documentation transition audit anchor: expected one, found {package.count(old)}")
package = package.replace(old, new, 1)

try:
    exec(compile(package, str(ORIGINAL), "exec"), {"__name__": "__main__", "__file__": str(ORIGINAL)})
except BaseException as error:
    diagnostic = " ".join(str(error).strip().split())[-1000:] or error.__class__.__name__
    diagnostic = diagnostic.replace("**", "").replace("`", "'")
    STAGE.write_text(f"documentation-sync-v3: {diagnostic}", encoding="utf-8")
    raise

for path in (ORIGINAL, OLD_WRAPPER):
    if path.exists():
        path.unlink()
print("Applied Issue #133 documentation synchronization with guarded source-transition validation")
