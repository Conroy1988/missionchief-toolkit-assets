#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
HELP = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
README = ROOT / "README.md"
GREASY = ROOT / "docs" / "greasyfork-description.md"
SITE_DATA = ROOT / "docs" / "site-data.json"
DOC_CONTRACT = ROOT / ".github" / "documentation-contract.json"
INSPECTION = ROOT / "docs" / "issue-133-help-version-inspection.json"
INSPECTION_PACKAGE = ROOT / ".github" / "development-packages" / "issue-133-help-version-inspect.py"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
DOC_AUDIT = ROOT / ".github" / "scripts" / "check_documentation_drift.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(
    source,
    "        guideVersion: '4.14.4',",
    "        guideVersion: '4.15.0',",
    "runtime Help Centre version",
)
SOURCE.write_text(source, encoding="utf-8")

help_html = HELP.read_text(encoding="utf-8")
help_html = replace_once(help_html, "Guide for Toolkit v4.14.10", "Guide for Toolkit v4.15.0", "Help Centre header version")
help_html = replace_once(help_html, "Help Centre for v4.14.5", "Help Centre for v4.15.0", "Help Centre footer version")
help_html = replace_once(
    help_html,
    "Mission Age Watch, Mission Value, resource and transport tools",
    "Mission Age Watch, Mission Value, the live Mission Requirements matrix, resource and transport tools",
    "Help Centre hero capability list",
)
help_html = replace_once(
    help_html,
    '<section class="section" id="resources" data-title="Resource and Transport Tools" data-keywords="resource gap radius transport watcher patient prisoner alliance sweep lssm release discharge code 5"><div class="head"><span class="num">08</span><div><h2>Resource and Transport Tools</h2><p class="summary">Coverage analysis, passive transport monitoring and manual alliance patient-release support.</p></div></div><h3>Resource Gap</h3>',
    '<section class="section" id="resources" data-title="Resource and Transport Tools" data-keywords="mission requirements selected en-route still needed resource gap radius transport watcher patient prisoner alliance sweep lssm release discharge code 5"><div class="head"><span class="num">08</span><div><h2>Resource and Transport Tools</h2><p class="summary">Live mission requirements, coverage analysis, passive transport monitoring and manual alliance patient-release support.</p></div></div><h3>Mission Requirements</h3><p>The default-enabled matrix appears above MissionChief dispatch controls in normal document flow. It shows each supported requirement with <strong>Missing on mission</strong>, <strong>En-route</strong>, <strong>Still needed</strong> and <strong>Selected</strong> values, updating immediately when eligible vehicles are checked or unchecked.</p><ul><li>Red means a known requirement is definitely still open.</li><li>Green means every displayed requirement is definitely covered by en-route and selected capacity.</li><li>Amber means personnel capacity, mission conditions or unknown MissionChief wording cannot be resolved exactly.</li><li>Normal and occupied vehicle lists are included. Trailer/towing pairs and capacity factors are deduplicated.</li><li>When the equivalent LSSM enhanced-missing-vehicles panel is active, the Toolkit yields rather than displaying a competing panel.</li></ul><h3>Resource Gap</h3>',
    "Help Centre Mission Requirements guide",
)
HELP.write_text(help_html, encoding="utf-8")

manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
manifest["guideVersion"] = "4.15.0"
manifest["toolkitVersion"] = "4.15.0"
manifest["updated"] = "2026-07-17"
manifest["runtimeGuidePatch"] = "Toolkit v4.15.0 documents the live Mission Requirements matrix while retaining Financial Command and all seven interface-system guide patches."
HELP_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

readme = README.read_text(encoding="utf-8")
readme = replace_once(
    readme,
    "| **Mission Value** | Displays a correctly formatted mission value inside opened mission windows, with dynamic clearance from native controls. |\n",
    "| **Mission Value** | Displays a correctly formatted mission value inside opened mission windows, with dynamic clearance from native controls. |\n| **Mission Requirements** | Adds a live, normal-flow matrix of missing, en-route, still-needed and selected capacity above MissionChief dispatch controls. |\n",
    "README Mission Requirements capability",
)
readme = replace_once(
    readme,
    "- Mission Value inside opened mission windows\n",
    "- Mission Value inside opened mission windows\n- Live Mission Requirements matrix with selected and en-route reconciliation\n",
    "README complete capability inventory",
)
README.write_text(readme, encoding="utf-8")

greasy = GREASY.read_text(encoding="utf-8")
greasy = replace_once(
    greasy,
    "- Mission Age Watch, Mission Value, Critical View and Mission Inspector\n",
    "- Mission Age Watch, Mission Value, live Mission Requirements, Critical View and Mission Inspector\n",
    "Greasy Fork Mission Requirements claim",
)
GREASY.write_text(greasy, encoding="utf-8")

site = json.loads(SITE_DATA.read_text(encoding="utf-8"))
mission_features = next(category["features"] for category in site["featureCategories"] if category["name"] == "Mission command")
if not any(feature.get("name") == "Mission Requirements" for feature in mission_features):
    mission_value_index = next(index for index, feature in enumerate(mission_features) if feature.get("name") == "Mission Value")
    mission_features.insert(mission_value_index + 1, {
        "name": "Mission Requirements",
        "summary": "Shows live missing, en-route, still-needed and selected capacity inside opened MissionChief mission windows.",
        "details": [
            "Mounted in normal document flow above dispatch controls",
            "Updates immediately from normal and occupied vehicle selections",
            "Range-aware personnel, equipment, trailer and capacity-factor handling",
            "Fails safely on unknown wording and yields to an active LSSM equivalent"
        ],
        "visual": "mission-requirements",
        "tags": ["missions", "requirements", "dispatch"]
    })
SITE_DATA.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")

contract = json.loads(DOC_CONTRACT.read_text(encoding="utf-8"))
for key in ("requiredSourceTokens", "requiredFeatureNames"):
    if "Mission Requirements" not in contract[key]:
        anchor = "Mission Value"
        index = contract[key].index(anchor) + 1 if anchor in contract[key] else len(contract[key])
        contract[key].insert(index, "Mission Requirements")
public_docs = contract["publicDocumentation"]
for key in ("readmeRequiredTokens", "helpRequiredTokens", "greasyForkRequiredTokens"):
    if "Mission Requirements" not in public_docs[key]:
        anchor = "Mission Value"
        index = public_docs[key].index(anchor) + 1 if anchor in public_docs[key] else 0
        public_docs[key].insert(index, "Mission Requirements")
DOC_CONTRACT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

for path in (INSPECTION, INSPECTION_PACKAGE):
    if path.exists():
        path.unlink()

validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
doc_audit = subprocess.run([sys.executable, str(DOC_AUDIT)], cwd=ROOT)
if doc_audit.returncode != 0:
    raise SystemExit(doc_audit.returncode)
print("Synchronized Issue #133 public documentation and Help Centre v4.15.0 contract")
