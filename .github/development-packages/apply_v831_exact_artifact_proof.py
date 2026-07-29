#!/usr/bin/env python3
"""Toolkit v8.3.1: publish Issue #564 through the corrected exact-artifact pipeline."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
EXPECTED_SOURCE_SHA = "292202daee1d6dc4d446f06847801b84d677b3657b0c608a3502832399221609"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return value.replace(old, new, 1)


source = SOURCE_PATH.read_text(encoding="utf-8")
if hashlib.sha256(source.encode()).hexdigest() != EXPECTED_SOURCE_SHA:
    raise RuntimeError("Validated v8.3.0 source authority moved")
source = replace_once(source, "// @version      8.3.0", "// @version      8.3.1", "metadata version")
source = replace_once(source, "version: '8.3.0'", "version: '8.3.1'", "runtime version")
write("src/MissionChief_Map_Command_Toolkit.user.js", source)

auto_path = ".github/workflows/auto-release-after-validation.yml"
auto = read(auto_path)
auto = replace_once(
    auto,
    """    workflows:
      - Validate Canonical Userscript
""",
    """    workflows:
      - Toolkit Hotfix Gate
""",
    "automatic fallback workflow name",
)
write(auto_path, auto)

pipeline_path = ".github/scripts/test_release_pipeline_v4.py"
pipeline = read(pipeline_path)
pipeline = replace_once(
    pipeline,
    'assert "release-readiness-check.yml" not in a and "validation_run_id:" in a and "validated_sha:" in a\n',
    'assert "release-readiness-check.yml" not in a and "validation_run_id:" in a and "validated_sha:" in a\nassert "workflows:\\n      - Toolkit Hotfix Gate" in a\nassert "workflows:\\n      - Validate Canonical Userscript" not in a\n',
    "Pipeline v4 live workflow trigger contract",
)
write(pipeline_path, pipeline)

candidate_path = ".github/scripts/test_validation_candidate_pipeline.py"
candidate = read(candidate_path)
candidate = replace_once(
    candidate,
    '''        "types:\n      - closed",
''',
    '''        "types:\n      - closed",
        "workflows:\n      - Toolkit Hotfix Gate",
''',
    "candidate fallback trigger marker",
)
candidate = replace_once(
    candidate,
    '''        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
''',
    '''        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
        "workflows:\n      - Validate Canonical Userscript",
''',
    "candidate stale trigger prohibition",
)
write(candidate_path, candidate)

issue564_path = ".github/scripts/test_issue564_incident_feed_attended.py"
issue564 = read(issue564_path)
issue564 = replace_once(
    issue564,
    "    assert metadata and runtime and metadata.group(1)==runtime.group(1)=='8.3.0'\n",
    "    assert metadata and runtime and metadata.group(1)==runtime.group(1)\n    version=tuple(int(part) for part in metadata.group(1).split('.'))\n    assert version >= (8,3,0)\n",
    "Issue #564 version floor",
)
write(issue564_path, issue564)

performance = json.loads(read(".github/performance-budget.json"))
performance["revision"] = "2026-07-29-v831-exact-artifact-production-proof"
performance["rationale"] = "Publish the already validated Issue #564 Incident Command Wire behaviour through the corrected exact-run candidate-artifact pipeline."
performance["transitionApproval"] = {
    "issue": 564,
    "version": "8.3.1",
    "approvedNetworkRequestDelta": 0,
    "scope": "Production reconciliation of the v8.3.0 personal FMS 4 Incident Command Wire exclusion with corrected release triggers.",
    "approvedMutationObserverDelta": 0,
}
if not any(item.get("version") == "8.3.1" for item in performance.setdefault("approvalHistory", [])):
    performance["approvalHistory"].append(dict(performance["transitionApproval"]))
write(".github/performance-budget.json", json.dumps(performance, indent=2) + "\n")

changelog = read("CHANGELOG.md")
entry = """## [8.3.1] - 2026-07-29

### Incident Command Wire production reconciliation

- Publishes the fully validated v8.3.0 unattended Incident Command Wire behaviour as the production v8.3.1 release.
- Missions leave the feed only when one of your own vehicles reaches authoritative FMS 4, while responding and alliance-only attendance remain visible.
- Dynamic re-entry, current-card advancement, Pause/Play preservation and compact/expanded queue synchronization are unchanged from the validated v8.3.0 candidate.
- Corrects the automatic fallback trigger to the live **Toolkit Hotfix Gate** workflow name.
- Uses the exact successful head run, its sole candidate artifact and embedded PR/head/tree evidence; no post-merge userscript rebuild or duplicate readiness phase is required.
- Adds no request, observer, interval or Toolkit-managed timer.

"""
if "## [8.3.1] - 2026-07-29" not in changelog:
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + entry, "v8.3.1 changelog")
write("CHANGELOG.md", changelog)

doc_path = "docs/issue-564-incident-feed-attended-exclusion.md"
doc = read(doc_path).replace("Toolkit v8.3.0", "Toolkit v8.3.1")
doc += "\nThe v8.3.0 tree was the validated internal candidate. v8.3.1 is the production publication through the corrected exact-run artifact resolver.\n"
write(doc_path, doc)

manifest = json.loads(read("help/manifest.json"))
manifest.update(
    guideVersion="8.3.1",
    toolkitVersion="8.3.1",
    updated="2026-07-29",
    runtimeGuidePatch="Toolkit v8.3.1 publishes the validated personal FMS 4 Incident Command Wire exclusion through the corrected exact-artifact release path.",
)
write("help/manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
help_html = read("help/index.html").replace("v8.3.0", "v8.3.1")
write("help/index.html", help_html)

pipeline_doc = read("docs/RELEASE_PIPELINE_V4.md")
pipeline_doc += "\n\nThe workflow-run fallback listens to the live `Toolkit Hotfix Gate` workflow name. v8.3.1 is the controlled genuine-release proof for exact-run artifact promotion and complete telemetry attribution.\n"
write("docs/RELEASE_PIPELINE_V4.md", pipeline_doc)

headroom = json.loads(read(".github/fixtures/main-style-source-headroom.json"))
text = read("src/MissionChief_Map_Command_Toolkit.user.js")
style_start = text.index("function installMainStyles()")
template_start = text.index("addStyle(`", style_start) + len("addStyle(`")
metric = text.index("recordStartupMetric('stylesheetInstallMs'", template_start)
template_end = text.rfind("`);", template_start, metric)
css = text[template_start:template_end]
css_lines = css.split("\n")
canonical = re.sub(r"\n[\t ]*}", "}", "\n".join(line for i, line in enumerate(css_lines) if not (0 < i < len(css_lines)-1 and not line.strip())))
c = headroom["v8Candidate"]
previous_bytes = int(c["sourceBytes"]); previous_lines = int(c["sourceLines"])
previous_growth_bytes = int(c["approvedGrowth"]["sourceBytes"]); previous_growth_lines = int(c["approvedGrowth"]["sourceLines"])
source_bytes = len(text.encode()); source_lines = len(text.splitlines())
c.update(
    issue=564,
    version="8.3.1",
    sourceBytes=source_bytes,
    sourceLines=source_lines,
    sourceSha256=hashlib.sha256(text.encode()).hexdigest(),
    templateBytes=len(css.encode()),
    templateLines=len(css_lines),
    templateSha256=hashlib.sha256(css.encode()).hexdigest(),
    canonicalCssSha256=hashlib.sha256(canonical.encode()).hexdigest(),
    maxSourceBytes=source_bytes + 20000,
    maxSourceLines=source_lines + 250,
    baseline="8.3.0",
    scope="v8.3.1 production publication of Issue #564 through the corrected exact-run artifact release pipeline",
)
c["approvedGrowth"] = {
    "sourceBytes": previous_growth_bytes + source_bytes - previous_bytes,
    "sourceLines": previous_growth_lines + source_lines - previous_lines,
    "templateBytes": 0,
    "templateLines": 0,
}
write(".github/fixtures/main-style-source-headroom.json", json.dumps(headroom, indent=2) + "\n")

subprocess.run([sys.executable, str(ROOT / pipeline_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / candidate_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / issue564_path)], cwd=ROOT, check=True)
subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / pipeline_path), str(ROOT / candidate_path), str(ROOT / issue564_path)], cwd=ROOT, check=True)
print(json.dumps({
    "version": "8.3.1",
    "sourceSha256": c["sourceSha256"],
    "sourceBytes": source_bytes,
    "sourceLines": source_lines,
    "behaviour": "unchanged from validated v8.3.0 Issue #564 candidate",
    "releaseProof": "exact successful run plus sole candidate artifact plus embedded evidence",
}, indent=2))
