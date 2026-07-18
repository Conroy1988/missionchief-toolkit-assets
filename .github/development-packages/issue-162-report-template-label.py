#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "mission-info-missing.yml"
DIAG = ROOT / "docs" / "diagnostics" / "issue-162-report-source.txt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def run(*cmd: str) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


source = SRC.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.15.4", "// @version      4.15.5", "metadata version")
source = replace_once(source, "version: '4.15.4'", "version: '4.15.5'", "runtime version")
source = replace_once(source, "guideVersion: '4.15.4'", "guideVersion: '4.15.5'", "guide version")
source = replace_once(
    source,
    "const params = new URLSearchParams({ title: issueTitle, labels: 'Mission Info Missing', body });",
    "const params = new URLSearchParams({ template: 'mission-info-missing.yml', title: issueTitle, diagnostic: body });",
    "report query",
)
SRC.write_text(source, encoding="utf-8")

FORM.parent.mkdir(parents=True, exist_ok=True)
FORM.write_text(
    '''name: Mission requirements data report
description: Submit a Toolkit-generated diagnostic when MissionChief requirements cannot be resolved.
title: "Mission requirements missing: "
labels:
  - Mission Info Missing
body:
  - type: markdown
    attributes:
      value: |
        This form is opened by the Toolkit's **Report Mission** button. Review the generated diagnostic before submitting.

        Do not add passwords, cookies, account tokens, webhook URLs, addresses, coordinates or private alliance information.

  - type: textarea
    id: diagnostic
    attributes:
      label: Toolkit diagnostic
      description: Automatically harvested and sanitised Mission Requirements information.
      placeholder: The Toolkit will prefill this field.
    validations:
      required: true

  - type: textarea
    id: additional-context
    attributes:
      label: Additional context
      description: Optional details about what was visible in MissionChief when the report was generated.

  - type: checkboxes
    id: confirmation
    attributes:
      label: Confirmation
      options:
        - label: I reviewed the diagnostic and removed any information I do not want to publish.
          required: true
''',
    encoding="utf-8",
)

test = RUNTIME_TEST.read_text(encoding="utf-8")
test = replace_once(test, "version: '4.15.4'", "version: '4.15.5'", "fixture version")
test = replace_once(
    test,
    "assert(reportUrl.includes('Mission+Info+Missing'), 'report requests the Mission Info Missing label');\nassert(reportUrl.length <= 7600, 'report URL remains bounded');\nconst reportBody = new URL(reportUrl).searchParams.get('body');",
    "const reportParams = new URL(reportUrl).searchParams;\nassert.strictEqual(reportParams.get('template'), 'mission-info-missing.yml', 'report selects the repository-owned Mission Info Missing form');\nassert.strictEqual(reportParams.get('labels'), null, 'report does not request permission-dependent labels');\nassert.strictEqual(reportParams.get('body'), null, 'report diagnostic uses the issue-form field rather than the blank issue body');\nassert(reportUrl.length <= 7600, 'report URL remains bounded');\nconst reportBody = reportParams.get('diagnostic');",
    "report fixture",
)
RUNTIME_TEST.write_text(test, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    'RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"',
    'RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"\nREPORT_FORM = ROOT / ".github/ISSUE_TEMPLATE/mission-info-missing.yml"',
    "contract form path",
)
contract = replace_once(
    contract,
    '        "Mission Info Missing",\n        "issues/new",',
    '        "mission-info-missing.yml",\n        "diagnostic",\n        "issues/new",',
    "contract source markers",
)
contract = replace_once(
    contract,
    '    assert source.count("function installMissionRequirementsWindows()") == 1',
    '    report_form = REPORT_FORM.read_text(encoding="utf-8")\n    assert "labels:\\n  - Mission Info Missing" in report_form\n    assert "id: diagnostic" in report_form\n    assert "required: true" in report_form\n\n    assert source.count("function installMissionRequirementsWindows()") == 1',
    "contract form assertions",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = '''## [4.15.5] - 2026-07-18

### Fixed
- Changed **Report Mission** to use a repository-owned GitHub issue form so `Mission Info Missing` is applied for contributor reports as well as maintainer reports.
- Preserved the sanitised diagnostic prefill through the form's canonical `diagnostic` field without storing a GitHub credential in the userscript.

'''
if "## [4.15.5]" not in changelog:
    marker = "## [4.15.4]"
    if marker not in changelog:
        raise AssertionError("4.15.4 changelog marker missing")
    changelog = changelog.replace(marker, entry + marker, 1)
changelog_path.write_text(changelog, encoding="utf-8")

doc_path = ROOT / "docs" / "issue-154-mission-requirements-reporting-contract.md"
if doc_path.exists():
    doc = doc_path.read_text(encoding="utf-8")
    note = "\n## Repository-owned report labelling\n\nFrom v4.15.5, Report Mission opens `.github/ISSUE_TEMPLATE/mission-info-missing.yml` and prefills its `diagnostic` field. The form owns the `Mission Info Missing` label, so labelling does not depend on the reporter having repository permissions.\n"
    if "## Repository-owned report labelling" not in doc:
        doc += note
    doc_path.write_text(doc, encoding="utf-8")

help_manifest_path = ROOT / "help" / "manifest.json"
help_manifest = json.loads(help_manifest_path.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "4.15.5"
help_manifest["toolkitVersion"] = "4.15.5"
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.15.5 guarantees Mission Info Missing labelling through a repository-owned report form."
help_manifest_path.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

help_index = ROOT / "help" / "index.html"
if help_index.exists():
    help_index.write_text(help_index.read_text(encoding="utf-8").replace("4.15.4", "4.15.5"), encoding="utf-8")

if DIAG.exists():
    DIAG.unlink()
try:
    DIAG.parent.rmdir()
except OSError:
    pass

canonical = SRC.read_bytes()
dist_user = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
dist_txt = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
dist_user.write_bytes(canonical)
dist_txt.write_bytes(canonical)
digest = hashlib.sha256(canonical).hexdigest()
(ROOT / "dist" / "SHA256SUMS.txt").write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist" / "release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "4.15.5"
manifest["sha256"] = digest
manifest["bytes"] = len(canonical)
manifest["lines"] = canonical.count(b"\n")
manifest.setdefault("metadata", {})["runtimeVersion"] = "4.15.5"
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

run("node", "--check", str(SRC.relative_to(ROOT)))
run("node", str(RUNTIME_TEST.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
print(f"Issue #162 candidate ready: sha256={digest}")
