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
    raise RuntimeError("canonical retirement declaration extractor anchor drifted")
text = text.replace(old_extractor, new_extractor)

old_matcher = 'declaration_pattern = re.compile(rf"^\\s*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)'
new_matcher = 'declaration_pattern = re.compile(rf"^[ \\t]*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)'
if text.count(old_matcher) != 1:
    raise RuntimeError("canonical retirement declaration matcher anchor drifted")
text = text.replace(old_matcher, new_matcher)

old_constants = '''HEADROOM_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
'''
new_constants = '''HEADROOM_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
SETTINGS_FIXTURE = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
'''
if text.count(old_constants) != 1:
    raise RuntimeError("canonical retirement settings fixture constant anchor drifted")
text = text.replace(old_constants, new_constants)

old_registry = '''source = re.sub(r"^\\s*missionRequirementsPanelId:\\s*[^\\n]+\\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r"^\\s*missionRequirementsDocumentStyleId:\\s*[^\\n]+\\n", "", source, count=1, flags=re.MULTILINE)
'''
new_registry = '''source = re.sub(r"^[ \\t]*missionRequirementsPanelId:[^\\n]*\\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r"^[ \\t]*missionRequirementsDocumentStyleId:[^\\n]*\\n", "", source, count=1, flags=re.MULTILINE)
source = re.sub(r",?[ \\t]*#\\$\\{SCRIPT\\.missionRequirementsPanelId\\}", "", source)
source = re.sub(r"^[ \\t]*target\\.id === SCRIPT\\.missionRequirementsPanelId \\|\\|[ \\t]*\\n", "", source, flags=re.MULTILINE)
'''
if text.count(old_registry) != 1:
    raise RuntimeError("canonical retirement registry cleanup anchor drifted")
text = text.replace(old_registry, new_registry)

old_migration = r"delete merged.missionRequirements;\n"
new_migration = r"delete merged['missionRequirements'];\n"
if text.count(old_migration) != 1:
    raise RuntimeError("canonical retirement migration cleanup anchor drifted")
text = text.replace(old_migration, new_migration)

old_hooks = '''source = re.sub(r"^\\s*if \\(state\\.missionRequirements\\) scheduleMissionRequirementsScan\\(0\\);\\s*\\n", "", source, flags=re.MULTILINE)
source = re.sub(r"^\\s*installMissionRequirementsWindows\\(\\);\\s*\\n", "", source, flags=re.MULTILINE)
'''
new_hooks = '''source = re.sub(r"^[ \\t]*if \\(state\\.missionRequirements\\) scheduleMissionRequirementsScan\\(0\\);[ \\t]*\\n", "", source, flags=re.MULTILINE)
source = source.replace("scheduleMissionRequirementsScan(", "scheduleOperationalSuiteScan(")
source = re.sub(r"^[ \\t]*installMissionRequirementsWindows\\(\\);[ \\t]*\\n", "", source, flags=re.MULTILINE)
'''
if text.count(old_hooks) != 1:
    raise RuntimeError("canonical retirement external hook anchor drifted")
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
    ROOT / ".github" / "diagnostics" / "issue391-retirement-v3-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-migration-cleanup-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-migration-v2-failure.txt",
)'''
if text.count(old_diagnostics) != 1:
    raise RuntimeError("canonical retirement diagnostic cleanup anchor drifted")
text = text.replace(old_diagnostics, new_diagnostics)

settings_anchor = '''RENDERER_TEST.write_text(renderer_test, encoding="utf-8")

fixture = json.loads(HEADROOM_FIXTURE.read_text(encoding="utf-8"))
'''
settings_replacement = '''RENDERER_TEST.write_text(renderer_test, encoding="utf-8")

settings_fixture = json.loads(SETTINGS_FIXTURE.read_text(encoding="utf-8"))
for list_key in (
    "toggleRoutes",
    "extractedMissionWindowToggleRoutes",
    "extractedMissionWindowEffectRoutes",
):
    values = settings_fixture.get(list_key)
    if not isinstance(values, list) or values.count("missionRequirements") != 1:
        raise RuntimeError(f"settings fixture route inventory drifted: {list_key}")
    values.remove("missionRequirements")
for map_key in (
    "toggleStatePaths",
    "extractedMissionWindowToggleStatePaths",
):
    values = settings_fixture.get(map_key)
    if not isinstance(values, dict) or values.get("missionRequirements") != "missionRequirements":
        raise RuntimeError(f"settings fixture state-path inventory drifted: {map_key}")
    del values["missionRequirements"]
legacy_migration = settings_fixture.get("legacyMigration")
if not isinstance(legacy_migration, dict) or legacy_migration.get("missionRequirements") is not False:
    raise RuntimeError("historical Matrix preference fixture must remain available for migration proof")
SETTINGS_FIXTURE.write_text(json.dumps(settings_fixture, indent=2) + "\\n", encoding="utf-8")

fixture = json.loads(HEADROOM_FIXTURE.read_text(encoding="utf-8"))
'''
if text.count(settings_anchor) != 1:
    raise RuntimeError("canonical retirement settings fixture runtime anchor drifted")
text = text.replace(settings_anchor, settings_replacement)

PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(PACKAGE), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue391-canonical-retirement-selftest-") as temporary:
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
        raise SystemExit("Canonical Issue #391 retirement package failed full sandbox self-test")

for obsolete in (
    ROOT / ".github" / "development-packages" / "issue391-complete-retirement-package.py",
    ROOT / ".github" / "development-packages" / "issue391-complete-retirement-package-v2.py",
    ROOT / ".github" / "development-packages" / "issue391-complete-retirement-package-v3.py",
    ROOT / ".github" / "development-packages" / "issue391-complete-package-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-finalize-retirement-rewrites.py",
    ROOT / ".github" / "development-packages" / "issue391-finalize-rewrites-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-fix-declaration-extractor.py",
    ROOT / ".github" / "development-packages" / "issue391-fix-migration-cleanup-token.py",
    ROOT / ".github" / "development-packages" / "issue391-fix-migration-cleanup-token-v2.py",
    ROOT / ".github" / "development-packages" / "issue391-migration-cleanup-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-migration-v2-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-panel-token-context-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-panel-token-context-diagnostic-v2.py",
    ROOT / ".github" / "development-packages" / "issue391-retirement-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-retirement-diagnostic-v2.py",
    ROOT / ".github" / "development-packages" / "issue391-retirement-diagnostic-v3.py",
    ROOT / ".github" / "development-packages" / "issue391-retirement-v2-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-retirement-v3-diagnostic.py",
):
    obsolete.unlink(missing_ok=True)

print("Canonical Issue #391 retirement package finalized; full sandbox self-test passed.")
