#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT / ".github" / "development-packages" / "issue-200-version-status-ui.py"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
DIAGNOSTIC = ROOT / ".github" / "workflows" / "issue-200-diagnostic.yml"

subprocess.run([sys.executable, str(BASE_PACKAGE)], cwd=ROOT, check=True)

runtime = RUNTIME.read_text(encoding="utf-8")
old = "context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('4.20.1')) })); return { abort() {} }; };"
new = "context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('4.20.2')) })); return { abort() {} }; };"
if runtime.count(old) != 1:
    raise AssertionError(f"newer live version fixture: expected one match, found {runtime.count(old)}")
RUNTIME.write_text(runtime.replace(old, new, 1), encoding="utf-8")

DIAGNOSTIC.unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
print("Corrected v4.20.1 live-update fixture and removed temporary diagnostics")
