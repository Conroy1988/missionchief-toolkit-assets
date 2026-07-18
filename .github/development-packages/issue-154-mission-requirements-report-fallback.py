#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
DIAG = ROOT / "docs" / "diagnostics" / "issue-154-mission-requirements-source.txt"
PAYLOAD_DIR = ROOT / ".github" / "development-packages" / "issue-154-payload"

def payload(name: str) -> str:
    return (PAYLOAD_DIR / f"{name}.txt").read_text(encoding="utf-8")


def replace_function(text: str, name: str, replacement: str) -> str:
    start = text.find(f"    function {name}(")
    if start < 0:
        raise AssertionError(f"Function not found: {name}")
    end = text.find("\n    function ", start + 12)
    if end < 0:
        raise AssertionError(f"Next function boundary not found after: {name}")
    return text[:start] + replacement.rstrip() + "\n" + text[end:]


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise AssertionError(f"Start marker not found: {start_marker[:80]}")
    end = text.find(end_marker, start)
    if end < 0:
        raise AssertionError(f"End marker not found: {end_marker[:80]}")
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:]


def run(*cmd: str) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


source = SRC.read_text(encoding="utf-8")
if "// @version      4.15.3" not in source:
    raise AssertionError("Expected v4.15.3 canonical source")

source = source.replace("// @version      4.15.3", "// @version      4.15.4", 1)
source = source.replace("version: '4.15.3'", "version: '4.15.4'", 1)
source = source.replace("guideVersion: '4.15.3'", "guideVersion: '4.15.4'", 1)

source_for_candidate = payload("source_for_candidate")
source = replace_function(source, "missionRequirementsSourceForCandidate", source_for_candidate)

helpers_and_candidates = payload("helpers_and_candidates")
source = replace_between(
    source,
    "    function missionRequirementsPrimaryRuntime()",
    "    function missionRequirementsDocumentCss()",
    helpers_and_candidates,
)

css_start = source.find("    function missionRequirementsDocumentCss()")
css_end = source.find("\n    function ensureMissionRequirementsDocumentStyle", css_start)
if css_start < 0 or css_end < 0:
    raise AssertionError("Mission Requirements CSS function not found")
css_block = source[css_start:css_end]
pos = css_block.rfind("`;")
if pos < 0:
    raise AssertionError("Mission Requirements CSS template terminator not found")
extra_css = payload("extra_css")
css_block = css_block[:pos] + extra_css + css_block[pos:]
source = source[:css_start] + css_block + source[css_end:]

panel_html = payload("panel_html")
source = replace_function(source, "missionRequirementsPanelHtml", panel_html)

payload("report_helpers")
render_function = payload("render_function")
source = replace_function(source, "missionRequirementsRenderRecord", render_function)

ownership_block = payload("ownership_block")
source = replace_between(
    source,
    "    function missionRequirementsHostPanels(source)",
    "    function missionRequirementsRemoveRecord(source)",
    ownership_block,
)

source = replace_function(source, "missionRequirementsRemoveRecord", payload("remove_record"))
source = replace_function(source, "clearMissionRequirementsPanels", payload("clear_function"))
source = replace_function(source, "scanMissionRequirementsWindows", payload("scan_function"))

source = source.replace(
    "#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #vehicle_show_table_body_all",
)
source = source.replace(
    "runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 800);",
    "runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 800);\n        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 1600);",
    1,
)
SRC.write_text(source, encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
test = test.replace(
    "        this.id = '';\n        this.value = '';",
    "        this.id = '';\n        this.className = '';\n        this.hidden = false;\n        this.value = '';",
    1,
)
test = test.replace(
    "    remove() {\n        this.isConnected = false;",
    "    contains(node) {\n        if (this === node) return true;\n        return this.children.some(child => child.contains?.(node));\n    }\n    remove() {\n        this.isConnected = false;",
    1,
)
test = test.replace(
    "        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style'",
    "        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style',\n        version: '4.15.4'",
    1,
)
test = test.replace(
    "    pageWindow: { MutationObserver: FakeMutationObserver },",
    "    pageWindow: { MutationObserver: FakeMutationObserver, navigator: { platform: 'FixtureOS', userAgentData: { platform: 'FixtureOS', mobile: false } }, innerWidth: 1280, innerHeight: 720, open: url => { openedUrls.push(url); return {}; } },\n    URLSearchParams,",
    1,
)
test = test.replace("const listenedEvents = [];", "const listenedEvents = [];\nconst openedUrls = [];", 1)
test = test.replace(
    "    canonicalPanel: missionRequirementsCanonicalPanel,",
    "    canonicalPanel: missionRequirementsCanonicalPanel,\n    fallbackHtml: missionRequirementsFallbackHtml,\n    reportUrl: missionRequirementsReportUrl,\n    sanitize: missionRequirementsSafeDiagnostic,",
    1,
)
test = test.replace(
    "        if (selector === '#missing_text') return sourceNode;",
    "        if (selector === '#missing_text') return sourceNode.isConnected ? sourceNode : null;\n        if (selector === '[data-mcms-requirements-anchor=\"1\"]') return missionRoot.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;",
    1,
)
helper_marker = "    return { root: missionRoot, mount: missionRoot, source: sourceNode };\n}\n"
if helper_marker not in test:
    raise AssertionError("Mission candidate helper marker not found")
test = test.replace(helper_marker, payload("helper_add"), 1)
fixture_insert_marker = "const canonicalDoc = new FakeDocument();"
if fixture_insert_marker not in test:
    raise AssertionError("Runtime fixture insertion marker not found")
test = test.replace(fixture_insert_marker, payload("fixture_tests") + fixture_insert_marker, 1)
TEST.write_text(test, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = contract.replace(
    '        "function missionRequirementsMissionIdentity(candidate, source)",',
    '        "function missionRequirementsMissionIdentity(candidate, source)",\n        "function missionRequirementsAnchorForCandidate(candidate)",\n        "function missionRequirementsFallbackHtml(kind)",\n        "function missionRequirementsReportUrl(record, reason = \'unknown\')",\n        "Unable to pull mission requirements",\n        "data-mcms-report-mission",\n        "Mission Info Missing",\n        "issues/new",',
    1,
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
changelog = changelog.replace("## [4.15.3]", payload("entry") + "## [4.15.3]", 1)
changelog_path.write_text(changelog, encoding="utf-8")

contract_doc = ROOT / "docs" / "issue-133-live-mission-requirements-contract.md"
if contract_doc.exists():
    doc = contract_doc.read_text(encoding="utf-8")
    note = "\n## Missing-data reporting\n\nWhen MissionChief does not expose usable requirement data, the Toolkit keeps one native-window fallback panel visible and offers a sanitised, player-reviewed GitHub issue composer. No GitHub credential is stored or transmitted by the userscript.\n"
    if "## Missing-data reporting" not in doc:
        doc += note
    contract_doc.write_text(doc, encoding="utf-8")

help_manifest_path = ROOT / "help" / "manifest.json"
help_manifest = json.loads(help_manifest_path.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "4.15.4"
help_manifest["toolkitVersion"] = "4.15.4"
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.15.4 documents Mission Requirements missing-data fallback and safe player-reviewed reporting while retaining all seven interface systems."
help_manifest_path.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

help_index = ROOT / "help" / "index.html"
if help_index.exists():
    help_text = help_index.read_text(encoding="utf-8").replace("4.15.3", "4.15.4")
    help_index.write_text(help_text, encoding="utf-8")

if DIAG.exists():
    DIAG.unlink()
try:
    DIAG.parent.rmdir()
except OSError:
    pass
shutil.rmtree(PAYLOAD_DIR)

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
manifest["version"] = "4.15.4"
manifest["sha256"] = digest
manifest["bytes"] = len(canonical)
manifest["lines"] = canonical.count(b"\n")
manifest.setdefault("metadata", {})["runtimeVersion"] = "4.15.4"
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

run("node", "--check", str(SRC.relative_to(ROOT)))
run("node", str(TEST.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
if len(canonical) > 1_900_000:
    raise AssertionError(f"Candidate exceeds existing 1,900,000-byte source ceiling: {len(canonical)}")
print(f"Issue #154 candidate ready: {len(canonical)} bytes, {manifest['lines']} lines, sha256={digest}")
