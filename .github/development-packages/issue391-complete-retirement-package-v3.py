#!/usr/bin/env python3
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path(".github/development-packages/issue391-retire-matrix.py")
PACKAGE = ROOT / PACKAGE_REL

text = PACKAGE.read_text(encoding="utf-8")

old_extractor = '''def extract_declaration(text: str, name: str, lower: int, upper: int) -> str:
    token = f"    const {name} ="
    start = text.find(token, lower, upper)
    if start < 0:
        raise RuntimeError(f"shared capability declaration missing: {name}")
'''
new_extractor = '''def extract_declaration(text: str, name: str, lower: int, upper: int) -> str:
    declaration_pattern = re.compile(rf"^[ \\t]*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)
    declaration_match = declaration_pattern.search(text, lower, upper)
    if declaration_match is None:
        raise RuntimeError(f"shared capability declaration missing: {name}")
    start = declaration_match.start()
'''
if text.count(old_extractor) != 1:
    raise RuntimeError("retirement declaration extractor anchor drifted")
text = text.replace(old_extractor, new_extractor)

old_matcher = 'declaration_pattern = re.compile(rf"^\\s*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)'
new_matcher = 'declaration_pattern = re.compile(rf"^[ \\t]*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)'
if text.count(old_matcher) != 1:
    raise RuntimeError("retirement declaration matcher anchor drifted")
text = text.replace(old_matcher, new_matcher)

old_registry = '''source = re.sub(r"^\\s*missionRequirementsPanelId:\\s*[^\\n]+\\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r"^\\s*missionRequirementsDocumentStyleId:\\s*[^\\n]+\\n", "", source, count=1, flags=re.MULTILINE)
'''
new_registry = '''source = re.sub(r"^[ \\t]*missionRequirementsPanelId:[^\\n]*\\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r"^[ \\t]*missionRequirementsDocumentStyleId:[^\\n]*\\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r",?[ \\t]*#\\$\\{SCRIPT\\.missionRequirementsPanelId\\}", "", source)
source = re.sub(r"^[ \\t]*target\\.id === SCRIPT\\.missionRequirementsPanelId \\|\\|[ \\t]*\\n", "", source, flags=re.MULTILINE)
'''
if text.count(old_registry) != 1:
    raise RuntimeError("retirement registry cleanup anchor drifted")
text = text.replace(old_registry, new_registry)

old_hooks = '''source = re.sub(r"^\\s*if \\(state\\.missionRequirements\\) scheduleMissionRequirementsScan\\(0\\);\\s*\\n", "", source, flags=re.MULTILINE)
source = re.sub(r"^\\s*installMissionRequirementsWindows\\(\\);\\s*\\n", "", source, flags=re.MULTILINE)
'''
new_hooks = '''source = re.sub(r"^[ \\t]*if \\(state\\.missionRequirements\\) scheduleMissionRequirementsScan\\(0\\);[ \\t]*\\n", "", source, flags=re.MULTILINE)
source = source.replace("scheduleMissionRequirementsScan(", "scheduleOperationalSuiteScan(")
source = re.sub(r"^[ \\t]*installMissionRequirementsWindows\\(\\);[ \\t]*\\n", "", source, flags=re.MULTILINE)
'''
if text.count(old_hooks) != 1:
    raise RuntimeError("retirement external-hook rewrite anchor drifted")
text = text.replace(old_hooks, new_hooks)

old_diagnostics = '''    ROOT / ".github" / "diagnostics" / "issue391-shared-catalogue-map.txt",
)'''
new_diagnostics = '''    ROOT / ".github" / "diagnostics" / "issue391-shared-catalogue-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure-v3.txt",
    ROOT / ".github" / "diagnostics" / "issue391-extractor-correction-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-finalize-rewrites-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-complete-package-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-retirement-v2-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-panel-token-context.txt",
)'''
if text.count(old_diagnostics) != 1:
    raise RuntimeError("retirement diagnostic cleanup anchor drifted")
text = text.replace(old_diagnostics, new_diagnostics)

PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(PACKAGE), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue391-complete-retirement-v3-selftest-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / PACKAGE_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        raise SystemExit("Issue #391 retirement package v3 failed sandbox self-test")

for obsolete in (
    ROOT / ".github" / "development-packages" / "issue391-complete-retirement-package-v2.py",
    ROOT / ".github" / "development-packages" / "issue391-retirement-v2-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-panel-token-context-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-panel-token-context-diagnostic-v2.py",
):
    obsolete.unlink(missing_ok=True)

print("Issue #391 retirement package v3 completed; full sandbox self-test passed.")
