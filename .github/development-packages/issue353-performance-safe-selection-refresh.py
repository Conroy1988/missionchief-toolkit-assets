#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
old_listener = """        runtimeListen(doc, 'change', event => {
            const target = event.target;
            if (!target?.matches?.('.vehicle_checkbox, input[type=\"checkbox\"][vehicle_type_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true); runtimeListen(doc, 'click', event => { if (!event.target?.closest?.('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]')) return; const refresh = () => missionRequirementsScheduleDocumentRecords(doc); runtimeRequestAnimationFrame(refresh); runtimeSetTimeout(refresh, 80); runtimeSetTimeout(refresh, 220); }, true);"""
new_listener = """        runtimeListen(doc, 'click', event => {
            const target = event.target;
            if (!target?.matches?.('.vehicle_checkbox, input[type=\"checkbox\"][vehicle_type_id]') && !target?.closest?.('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true);"""
source = replace_once(source, old_listener, new_listener, "performance-safe delegated selection listener")
SOURCE.write_text(source, encoding="utf-8")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

# Extend the existing focused regression so direct checkbox selection and
# ARR/vehicle-group selection are both proved through the single listener.
test = TEST.read_text(encoding="utf-8")
old_test = """const issue353ClickRegistration = listenedEvents.find(entry => entry.target === issue353RefreshDoc && entry.type === 'click');
assert(issue353ClickRegistration, 'Matrix registers delegated ARR refresh listener');
const issue353AaoControl = new FakeElement('a', issue353RefreshDoc);
const issue353AaoChild = new FakeElement('span', issue353RefreshDoc);
issue353AaoChild.closestMap.set('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]', issue353AaoControl);
const issue353QueueBefore = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353AaoChild });
assert.strictEqual(animationQueue.length, issue353QueueBefore + 1, 'ARR click schedules a post-selection Matrix refresh');
const issue353Unrelated = new FakeElement('span', issue353RefreshDoc);
const issue353UnrelatedQueue = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353Unrelated });
assert.strictEqual(animationQueue.length, issue353UnrelatedQueue, 'unrelated clicks do not schedule Matrix refreshes');"""
new_test = """const issue353ClickRegistration = listenedEvents.find(entry => entry.target === issue353RefreshDoc && entry.type === 'click');
assert(issue353ClickRegistration, 'Matrix registers one delegated selection refresh listener');
const issue353Checkbox = new FakeElement('input', issue353RefreshDoc);
issue353Checkbox.matches = selector => selector.includes('.vehicle_checkbox');
const issue353CheckboxQueue = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353Checkbox });
assert.strictEqual(animationQueue.length, issue353CheckboxQueue + 1, 'direct checkbox click schedules a post-selection Matrix refresh');
const issue353AaoControl = new FakeElement('a', issue353RefreshDoc);
const issue353AaoChild = new FakeElement('span', issue353RefreshDoc);
issue353AaoChild.closestMap.set('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]', issue353AaoControl);
const issue353QueueBefore = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353AaoChild });
assert.strictEqual(animationQueue.length, issue353QueueBefore + 1, 'ARR click schedules a post-selection Matrix refresh');
const issue353Unrelated = new FakeElement('span', issue353RefreshDoc);
const issue353UnrelatedQueue = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353Unrelated });
assert.strictEqual(animationQueue.length, issue353UnrelatedQueue, 'unrelated clicks do not schedule Matrix refreshes');"""
test = replace_once(test, old_test, new_test, "Issue #353 delegated refresh regression")
TEST.write_text(test, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
changelog = replace_once(
    changelog,
    "- Added deferred Matrix refresh after ARR and vehicle-group controls programmatically update selected vehicles.",
    "- Reused one delegated selection listener for direct checkbox, ARR and vehicle-group updates without adding lifecycle call sites.",
    "Issue #353 changelog refresh wording",
)
CHANGELOG.write_text(changelog, encoding="utf-8")

# Preserve source-headroom accounting and update the candidate fingerprint.
headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
source_lines = len(source.splitlines())
headroom["candidateSourceLines"] = source_lines
headroom["recoveredSourceLines"] = headroom["originalSourceLines"] - source_lines
headroom["candidateSourceSha256"] = hashlib.sha256(source.encode()).hexdigest()
headroom["invariant"] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines '
    "while Police Sergeant and Car Recovery tracking reuse the existing delegated selection lifecycle and managed runtime budgets remain unchanged."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

# The failed performance gate identified these exact baseline-locked call-site
# counts. This correction must restore them before repository-wide validation.
expected_calls = {
    "runtimeSetTimeout(": 99,
    "runtimeRequestAnimationFrame(": 14,
    "runtimeListen(": 31,
}
for token, expected in expected_calls.items():
    actual = source.count(token)
    if actual != expected:
        raise RuntimeError(f"{token} call-site count is {actual}; expected {expected}")

if len(source.splitlines()) != 31653:
    raise RuntimeError(f"source line count changed unexpectedly: {len(source.splitlines())}")
if headroom["recoveredSourceLines"] != 504:
    raise RuntimeError(f"source-headroom recovery changed unexpectedly: {headroom['recoveredSourceLines']}")

env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
subprocess.check_call(["node", str(TEST)], cwd=ROOT, env=env)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print(
    "Prepared performance-safe Issue #353 correction; "
    "runtimeSetTimeout=99, runtimeRequestAnimationFrame=14, runtimeListen=31"
)
