#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT / ".github" / "development-packages" / "issue456-v5.0.4-truth-state-dedupe.py"
RENDERER_CONTRACT = ROOT / ".github" / "scripts" / "test_issue378_requirements_renderer.py"
FAILURE_REPORT = ROOT / ".github" / "diagnostics" / "issue456-v504-package-failure.txt"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

package = BASE_PACKAGE.read_text(encoding="utf-8")
package = package.replace("\n+- Stopped", "\n- Stopped")
package = package.replace("\n+- Added", "\n- Added")
package = package.replace("\n+- Enforced", "\n- Enforced")
package = package.replace("\n+- Added behavioural", "\n- Added behavioural")
package = package.replace("\n+\n'''", "\n\n'''")
BASE_PACKAGE.write_text(package, encoding="utf-8")

contract = RENDERER_CONTRACT.read_text(encoding="utf-8")
old = '''if "requirementRoot.parentNode?.insertBefore(panel, requirementRoot)" not in block:
    raise SystemExit("Issue #378 renderer must remain in normal document flow")
'''
new = '''if "requirementRoot.parentNode.insertBefore(panel, requirementRoot)" not in block:
    raise SystemExit("Issue #378 renderer must insert the panel in normal document flow")
if "panel.parentNode !== requirementRoot.parentNode || panel.nextSibling !== requirementRoot" not in block:
    raise SystemExit("Issue #378 renderer must keep the panel immediately before the requirement root")
'''
if contract.count(old) != 1:
    raise RuntimeError("Issue #378 normal-flow contract anchor changed")
RENDERER_CONTRACT.write_text(contract.replace(old, new, 1), encoding="utf-8")

subprocess.run(["python3", str(BASE_PACKAGE)], cwd=ROOT, env=ENV, check=True, timeout=300)
BASE_PACKAGE.unlink(missing_ok=True)
FAILURE_REPORT.unlink(missing_ok=True)
subprocess.run(["python3", str(ROOT / ".github" / "scripts" / "validate_userscript.py")], cwd=ROOT, env=ENV, check=True, timeout=300)
subprocess.run(["node", "--check", str(ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js")], cwd=ROOT, env=ENV, check=True)
print("Finalised v5.0.4 requirements truth-state recovery and structural renderer contract.")
