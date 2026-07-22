#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

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
listener_start_marker = "        runtimeListen(doc, 'change', event => {"
arr_listener_marker = "runtimeListen(doc, 'click', event => { if (!event.target?.closest?.('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]')) return;"
listener_start = source.find(listener_start_marker)
arr_listener_start = source.find(arr_listener_marker, listener_start)
if listener_start < 0 or arr_listener_start < 0:
    raise RuntimeError("unable to locate the existing change/ARR listener pair")
listener_end = source.find("}, true);", arr_listener_start)
if listener_end < 0:
    raise RuntimeError("unable to locate the end of the ARR listener")
listener_end += len("}, true);")
old_listener = source[listener_start:listener_end]
if old_listener.count("runtimeListen(") != 2:
    raise RuntimeError("listener boundary did not contain exactly two managed listeners")
if old_listener.count("runtimeSetTimeout(") != 2 or old_listener.count("runtimeRequestAnimationFrame(") != 1:
    raise RuntimeError("listener boundary did not contain the expected deferred refresh calls")
new_listener = """        runtimeListen(doc, 'click', event => {
            const target = event.target; if (!target?.matches?.('.vehicle_checkbox, input[type=\"checkbox\"][vehicle_type_id]') && !target?.closest?.('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true);"""
source = source[:listener_start] + new_listener + source[listener_end:]
SOURCE.write_text(source, encoding="utf-8")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

# Replace only the Issue #353 delegated-listener test block, retaining the
# existing final animation-queue flush and subsequent cross-source tests.
test = TEST.read_text(encoding="utf-8")
test_start_marker = "const issue353ClickRegistration = listenedEvents.find(entry => entry.target === issue353RefreshDoc && entry.type === 'click');"
test_end_marker = "flushAnimationFrames();\nlistenedEvents.splice(issue353ListenerStart);"
test_start = test.find(test_start_marker)
test_end = test.find(test_end_marker, test_start)
if test_start < 0 or test_end < 0:
    raise RuntimeError("unable to locate the Issue #353 delegated refresh test boundary")
new_test = """const issue353ClickRegistration = listenedEvents.find(entry => entry.target === issue353RefreshDoc && entry.type === 'click');
assert(issue353ClickRegistration, 'Matrix registers one delegated selection refresh listener');
const issue353Checkbox = new FakeElement('input', issue353RefreshDoc);
issue353Checkbox.matches = selector => selector.includes('.vehicle_checkbox');
const issue353CheckboxQueue = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353Checkbox });
assert.strictEqual(animationQueue.length, issue353CheckboxQueue + 1, 'direct checkbox click schedules a post-selection Matrix refresh');
flushAnimationFrames();
const issue353AaoControl = new FakeElement('a', issue353RefreshDoc);
const issue353AaoChild = new FakeElement('span', issue353RefreshDoc);
issue353AaoChild.closestMap.set('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]', issue353AaoControl);
const issue353QueueBefore = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353AaoChild });
assert.strictEqual(animationQueue.length, issue353QueueBefore + 1, 'ARR click schedules a post-selection Matrix refresh');
const issue353Unrelated = new FakeElement('span', issue353RefreshDoc);
const issue353UnrelatedQueue = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353Unrelated });
assert.strictEqual(animationQueue.length, issue353UnrelatedQueue, 'unrelated clicks do not schedule Matrix refreshes');
"""
test = test[:test_start] + new_test + test[test_end:]
TEST.write_text(test, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
old_changelog = "- Added deferred Matrix refresh after ARR and vehicle-group controls programmatically update selected vehicles."
new_changelog = "- Reused one delegated selection listener for direct checkbox, ARR and vehicle-group updates without adding lifecycle call sites."
if old_changelog in changelog:
    changelog = replace_once(changelog, old_changelog, new_changelog, "Issue #353 changelog refresh wording")
elif new_changelog not in changelog:
    raise RuntimeError("Issue #353 changelog refresh line is missing")
CHANGELOG.write_text(changelog, encoding="utf-8")

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

if source_lines != 31653:
    raise RuntimeError(f"source line count changed unexpectedly: {source_lines}")
if headroom["recoveredSourceLines"] != 504:
    raise RuntimeError(f"source-headroom recovery changed unexpectedly: {headroom['recoveredSourceLines']}")

# Raw token counts include each wrapper declaration. The official performance
# checker reports only invocations, so these limits correspond to the locked
# call-site budgets of 99 timeouts, 14 animation frames and 31 listeners.
managed_limits = {
    "runtimeSetTimeout(": 100,
    "runtimeRequestAnimationFrame(": 15,
    "runtimeListen(": 32,
}
managed_counts = {token: source.count(token) for token in managed_limits}
for token, limit in managed_limits.items():
    if managed_counts[token] > limit:
        raise RuntimeError(f"{token} raw token count is {managed_counts[token]}; limit is {limit}")

env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
subprocess.check_call(["node", str(TEST)], cwd=ROOT, env=env)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print(
    "Prepared performance-safe Issue #353 correction; "
    + ", ".join(f"{token}={count}" for token, count in managed_counts.items())
)
