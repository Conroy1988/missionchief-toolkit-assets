#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT / ".github" / "development-packages" / "issue456-v5.0.4-truth-state-dedupe.py"
OLD_FINALISE = ROOT / ".github" / "development-packages" / "issue456-v5.0.4-finalise.py"
RENDERER_CONTRACT = ROOT / ".github" / "scripts" / "test_issue378_requirements_renderer.py"
PREBOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

package = BASE_PACKAGE.read_text(encoding="utf-8")
package = package.replace("\n+- Stopped", "\n- Stopped")
package = package.replace("\n+- Added", "\n- Added")
package = package.replace("\n+- Enforced", "\n- Enforced")
package = package.replace("\n+- Added behavioural", "\n- Added behavioural")
package = package.replace("\n+\n'''", "\n\n'''")
BASE_PACKAGE.write_text(package, encoding="utf-8")

renderer = RENDERER_CONTRACT.read_text(encoding="utf-8")
old_renderer = '''if "requirementRoot.parentNode?.insertBefore(panel, requirementRoot)" not in block:
    raise SystemExit("Issue #378 renderer must remain in normal document flow")
'''
new_renderer = '''if "requirementRoot.parentNode.insertBefore(panel, requirementRoot)" not in block:
    raise SystemExit("Issue #378 renderer must insert the panel in normal document flow")
if "panel.parentNode !== requirementRoot.parentNode || panel.nextSibling !== requirementRoot" not in block:
    raise SystemExit("Issue #378 renderer must keep the panel immediately before the requirement root")
'''
if renderer.count(old_renderer) != 1:
    raise RuntimeError("Issue #378 normal-flow contract anchor changed")
RENDERER_CONTRACT.write_text(renderer.replace(old_renderer, new_renderer, 1), encoding="utf-8")

preboot = PREBOOT_CONTRACT.read_text(encoding="utf-8")
old_preboot = '''assert "// @version      5.0.3" in text
assert "version: '5.0.3'," in text
'''
new_preboot = '''metadata_version = re.search(r"(?m)^//\\s*@version\\s+([^\\s]+)\\s*$", text)
runtime_version = re.search(r"version:\\s*'([^']+)',", text)
assert metadata_version is not None
assert runtime_version is not None
assert metadata_version.group(1) == runtime_version.group(1)
'''
if preboot.count(old_preboot) != 1:
    raise RuntimeError("Issue #454 version contract anchor changed")
PREBOOT_CONTRACT.write_text(preboot.replace(old_preboot, new_preboot, 1), encoding="utf-8")

subprocess.run(["python3", str(BASE_PACKAGE)], cwd=ROOT, env=ENV, check=True, timeout=360)
BASE_PACKAGE.unlink(missing_ok=True)
OLD_FINALISE.unlink(missing_ok=True)
for path in (
    ROOT / ".github" / "diagnostics" / "issue456-v504-package-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue456-v504-finalise-failure.txt",
):
    path.unlink(missing_ok=True)
subprocess.run(["python3", str(ROOT / ".github" / "scripts" / "validate_userscript.py")], cwd=ROOT, env=ENV, check=True, timeout=360)
subprocess.run(["node", "--check", str(ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js")], cwd=ROOT, env=ENV, check=True)
print("Finalised v5.0.4 requirements recovery with structural renderer and version-agnostic preboot contracts.")
