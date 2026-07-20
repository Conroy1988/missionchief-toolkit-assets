#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
SHA_FILE = ROOT / "dist" / "SHA256SUMS.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
OPTIMISATION_TEST = ROOT / ".github" / "scripts" / "test_runtime_optimisations.py"
CONTRACT_DOC = ROOT / "docs" / "issue-251-alliance-observer-performance-contract.md"

OLD_VERSION = "4.20.10"
NEW_VERSION = "4.20.11"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", "metadata version")
source = replace_once(source, f"version: '{OLD_VERSION}',", f"version: '{NEW_VERSION}',", "runtime version")

function_start = source.find("function installAllianceBuildingsContextWatcherEarly")
function_end = source.find("const earlyAllianceBuildingsPage", function_start)
if function_start < 0 or function_end <= function_start:
    raise AssertionError("early Alliance Buildings watcher bounds were not found")
watcher = source[function_start:function_end]
pattern = re.compile(
    r"observer\.observe\(root,\s*\{\s*childList:\s*true,\s*subtree:\s*true,\s*"
    r"attributes:\s*true,\s*attributeFilter:\s*\['style',\s*'class',\s*'hidden',\s*'aria-hidden'\]\s*\}\);"
)
matches = list(pattern.finditer(watcher))
if len(matches) != 1:
    raise AssertionError(f"early watcher observe-options match count: {len(matches)}")
watcher = pattern.sub("observer.observe(root, { childList: true, subtree: true });", watcher, count=1)
if "attributes: true" in watcher or "attributeFilter" in watcher:
    raise AssertionError("early watcher still subscribes to attribute-only records")
if "mutation.addedNodes" not in watcher or "mutation.removedNodes" not in watcher:
    raise AssertionError("early watcher child-list decision logic changed unexpectedly")
source = source[:function_start] + watcher + source[function_end:]
SOURCE.write_text(source, encoding="utf-8")

# Canonical source and both installable distribution files must remain byte-identical.
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
SHA_FILE.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = NEW_VERSION
manifest["sha256"] = digest
manifest["bytes"] = len(source.encode("utf-8"))
manifest["lines"] = len(source.splitlines())
manifest.setdefault("metadata", {})["runtimeVersion"] = NEW_VERSION
manifest["baselineHashMatch"] = None
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

runtime_test = RUNTIME_TEST.read_text(encoding="utf-8")
runtime_test = replace_once(
    runtime_test,
    f"version: '{OLD_VERSION}'",
    f"version: '{NEW_VERSION}'",
    "Mission Requirements runtime fixture version",
)
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

optimisation_test = OPTIMISATION_TEST.read_text(encoding="utf-8")
anchor = '    assert "document.querySelectorAll(AUTO_LOAD_ALL_VEHICLES_SELECTOR)" not in auto_load\n'
contract = '''\n\n    alliance_watcher = section(\n        text,\n        "function installAllianceBuildingsContextWatcherEarly",\n        "const earlyAllianceBuildingsPage",\n    )\n    assert "mutation.addedNodes" in alliance_watcher\n    assert "mutation.removedNodes" in alliance_watcher\n    assert "observer.observe(root, { childList: true, subtree: true });" in alliance_watcher\n    assert "attributes: true" not in alliance_watcher\n    assert "attributeFilter" not in alliance_watcher\n'''
if "alliance_watcher = section(" in optimisation_test:
    raise AssertionError("Issue #251 runtime invariant already exists")
optimisation_test = replace_once(
    optimisation_test,
    anchor,
    anchor + contract,
    "Issue #251 runtime optimisation invariant anchor",
)
OPTIMISATION_TEST.write_text(optimisation_test, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
section = f'''## [{NEW_VERSION}] - 2026-07-20\n\n### Performance\n- Removed redundant presentation-attribute notifications from the document-wide early Alliance Buildings page watcher.\n- Child additions and removals, relevant-element matching, navigation detection, map suppression and repair behaviour remain unchanged.\n\n### Validation\n- Added an exact production-source invariant proving the watcher remains child-list based and no longer subscribes to attribute-only mutation records.\n\n'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + section, "v4.20.11 changelog section")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
help_count = help_text.count(OLD_VERSION)
if help_count < 1:
    raise AssertionError("Help Centre current-version marker was not found")
HELP.write_text(help_text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

CONTRACT_DOC.write_text(
    """# Issue #251 — Alliance Buildings early observer performance contract\n\n"
    "The early Alliance Buildings watcher exists to detect relevant map, table and layout elements being added to or removed from the live document. Its callback bases every scheduling decision on `addedNodes` and `removedNodes`.\n\n"
    "The watcher therefore observes `childList: true` with `subtree: true` and does not request attribute-only mutation records. Navigation listeners, relevant-element selectors, early styling, Leaflet suppression guards, context detection and map repair remain unchanged.\n\n"
    "This is a workload reduction rather than a feature change: presentation-attribute updates that could not satisfy the callback are no longer delivered to this document-wide observer.\n"
    """,
    encoding="utf-8",
)

print(f"Issue #251 v{NEW_VERSION} package applied; sha256={digest}")
