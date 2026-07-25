#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
STATIC_CONTRACT = ROOT / ".github" / "scripts" / "test_issue517_incident_command_wire.py"
RUNTIME_CONTRACT = ROOT / ".github" / "scripts" / "test_issue517_incident_command_wire_runtime.js"
README = ROOT / "README.md"
HELP = ROOT / "help" / "index.html"
CHANGELOG = ROOT / "CHANGELOG.md"
SELF = ROOT / ".github" / "issue519" / "apply_v712_hotfix.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-v712-hotfix.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def function_bounds(source: str, name: str) -> tuple[int, int]:
    marker = f"    function {name}("
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    quote = ""
    escaped = False
    index = opening
    while index < len(source):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char in {'"', "'", "`"}:
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
        index += 1
    raise SystemExit(f"Could not locate end of {name}")


def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_bounds(source, name)
    return source[:start] + replacement.rstrip() + source[end:]


def update_headroom(source: str) -> None:
    start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", start) + len("addStyle(`")
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, metric)
    raw = source[template_start:template_end]
    lines = raw.split("\n")
    canonical = re.sub(
        r"\n[\t ]*}",
        "}",
        "\n".join(
            line
            for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["v7Candidate"].update({
        "issue": 519,
        "version": "7.1.2",
        "sourceBytes": len(source.encode("utf-8")),
        "sourceLines": len(source.splitlines()),
        "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "templateBytes": len(raw.encode("utf-8")),
        "templateLines": len(lines),
        "templateSha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, "// @version      7.1.1", "// @version      7.1.2", "metadata version")
    source = replace_once(source, "version: '7.1.1',", "version: '7.1.2',", "runtime version")

    source = replace_once(
        source,
        "    let majorIncidentFeedMotionTimer = null;\n    let majorIncidentFeedMotionRevision = 0;",
        "    let majorIncidentFeedMotionTimer = null;\n    let majorIncidentFeedMotionRevision = 0;\n    let majorIncidentFeedAdvanceTimer = null;\n    let majorIncidentFeedAdvanceRevision = 0;",
        "dedicated advance state",
    )

    old_controls = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls{position:relative!important;top:auto!important;bottom:auto!important;z-index:7;flex:0 0 auto;align-self:center!important;display:flex;align-items:center!important;justify-content:center;height:100%!important;min-height:0;box-sizing:border-box!important;margin:0!important;gap:3px;padding:0 5px;border-left:1px solid var(--mcms-wire-border);background:rgba(0,0,0,.12);transform:none!important}'
    new_controls = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls{position:relative!important;inset:auto!important;z-index:7;flex:0 0 auto;align-self:center!important;display:flex!important;align-items:center!important;justify-content:center!important;height:calc(100% - 4px)!important;min-height:0!important;max-height:36px!important;box-sizing:border-box!important;margin:0!important;gap:3px;padding:0 5px!important;border-left:1px solid var(--mcms-wire-border);background:rgba(0,0,0,.12);overflow:hidden!important;transform:none!important;contain:layout paint}'
    source = replace_once(source, old_controls, new_controls, "control rail containment")

    old_buttons = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{appearance:none;-webkit-appearance:none;position:relative!important;top:auto!important;bottom:auto!important;float:none!important;align-self:center!important;box-sizing:border-box!important;display:grid;place-items:center;width:27px;height:27px;min-width:27px;min-height:27px;margin:0!important;padding:0;border:1px solid var(--mcms-wire-border);border-radius:5px;background:rgba(255,255,255,.055);color:var(--mcms-wire-text);font:900 13px/1 Arial,sans-serif;cursor:pointer;transform:none!important;vertical-align:middle}'
    new_buttons = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{appearance:none!important;-webkit-appearance:none!important;position:relative!important;inset:auto!important;float:none!important;align-self:center!important;box-sizing:border-box!important;display:grid!important;place-items:center!important;width:26px!important;height:26px!important;min-width:26px!important;min-height:26px!important;max-width:26px!important;max-height:26px!important;margin:0!important;padding:0!important;border:1px solid var(--mcms-wire-border)!important;border-radius:5px!important;background:rgba(255,255,255,.055);color:var(--mcms-wire-text);font:900 13px/1 Arial,sans-serif!important;cursor:pointer;overflow:hidden!important;transform:none!important;vertical-align:middle!important}'
    source = replace_once(source, old_buttons, new_buttons, "button hard bounds")
    source = replace_once(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:32px;height:32px;min-width:32px;min-height:32px}',
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:30px!important;height:30px!important;min-width:30px!important;min-height:30px!important;max-width:30px!important;max-height:30px!important}',
        "tablet button hard bounds",
    )

    schedule_replacement = """    function majorIncidentFeedCancelAdvance() {
        runtimeClearTimeout(majorIncidentFeedAdvanceTimer);
        majorIncidentFeedAdvanceTimer = null;
        majorIncidentFeedAdvanceRevision += 1;
    }

    function majorIncidentFeedScheduleAdvance(feed, delay = MAJOR_INCIDENT_FEED_ROTATION_MS, restart = false) {
        const count = majorIncidentFeedEntryCount(feed);
        const reducedMotion = Boolean(pageWindow.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
        if (!feed?.isConnected || count <= 1 || state.economyMode || reducedMotion || majorIncidentFeedManualPaused || majorIncidentFeedExpanded || document.hidden) {
            majorIncidentFeedCancelAdvance();
            return false;
        }
        if (majorIncidentFeedAdvanceTimer !== null && !restart) return true;
        majorIncidentFeedCancelAdvance();
        const now = Date.now();
        const interactionDelay = Math.max(0, majorIncidentFeedInteractionPauseUntil - now);
        const wait = Math.max(500, Number(delay) || MAJOR_INCIDENT_FEED_ROTATION_MS, interactionDelay + 350);
        const revision = ++majorIncidentFeedAdvanceRevision;
        majorIncidentFeedAdvanceTimer = runtimeSetTimeout(() => {
            majorIncidentFeedAdvanceTimer = null;
            if (revision !== majorIncidentFeedAdvanceRevision || !feed.isConnected) return;
            if (majorIncidentFeedInteractionActive(feed)) {
                majorIncidentFeedScheduleAdvance(feed, 850, true);
                return;
            }
            majorIncidentFeedApplyIndex(feed, majorIncidentFeedCurrentIndex + 1);
            majorIncidentFeedScheduleAdvance(feed, MAJOR_INCIDENT_FEED_ROTATION_MS, true);
        }, wait);
        return true;
    }"""
    source = replace_function(source, "majorIncidentFeedScheduleAdvance", schedule_replacement)

    paused_replacement = """    function majorIncidentFeedSetPaused(feed, paused) {
        majorIncidentFeedManualPaused = Boolean(paused);
        feed?.classList?.toggle('mcms-feed-paused', majorIncidentFeedManualPaused);
        majorIncidentFeedSyncControls(feed);
        if (majorIncidentFeedManualPaused) {
            majorIncidentFeedCancelAdvance();
        } else {
            majorIncidentFeedInteractionPauseUntil = 0;
            feed?.classList?.remove('mcms-feed-interacting');
            majorIncidentFeedScheduleAdvance(feed, 650, true);
        }
    }"""
    source = replace_function(source, "majorIncidentFeedSetPaused", paused_replacement)

    expanded_replacement = """    function majorIncidentFeedSetExpanded(feed, expanded) {
        majorIncidentFeedExpanded = Boolean(expanded);
        feed?.classList?.toggle('mcms-feed-expanded', majorIncidentFeedExpanded);
        const panel = feed?.querySelector?.('.mcms-incident-feed-panel');
        if (panel) panel.hidden = !majorIncidentFeedExpanded;
        majorIncidentFeedSyncControls(feed);
        if (majorIncidentFeedExpanded) {
            majorIncidentFeedCancelAdvance();
        } else {
            majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;
            majorIncidentFeedScheduleAdvance(feed, 1500, true);
        }
    }"""
    source = replace_function(source, "majorIncidentFeedSetExpanded", expanded_replacement)

    advance_replacement = """    function majorIncidentFeedAdvance(feed, delta, manual = false) {
        if (majorIncidentFeedEntryCount(feed) <= 1) return false;
        if (manual) majorIncidentFeedInteractionPauseUntil = Date.now() + MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS;
        const changed = majorIncidentFeedApplyIndex(feed, majorIncidentFeedCurrentIndex + Number(delta || 0));
        majorIncidentFeedScheduleAdvance(feed, manual ? MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS : MAJOR_INCIDENT_FEED_ROTATION_MS, true);
        return changed;
    }"""
    source = replace_function(source, "majorIncidentFeedAdvance", advance_replacement)

    source = replace_once(
        source,
        "        runtimeClearTimeout(majorIncidentFeedMotionTimer);\n        majorIncidentFeedMotionTimer = null;\n        majorIncidentFeedMotionRevision += 1;\n        majorIncidentFeedCurrentIndex = 0;",
        "        runtimeClearTimeout(majorIncidentFeedMotionTimer);\n        majorIncidentFeedMotionTimer = null;\n        majorIncidentFeedMotionRevision += 1;\n        majorIncidentFeedCancelAdvance();\n        majorIncidentFeedCurrentIndex = 0;",
        "feed teardown advance cancellation",
    )

    source = replace_once(
        source,
        "        majorIncidentFeedScheduleAdvance(feed, forceRestart ? 1200 : MAJOR_INCIDENT_FEED_ROTATION_MS);",
        "        majorIncidentFeedScheduleAdvance(feed, forceRestart ? 1200 : MAJOR_INCIDENT_FEED_ROTATION_MS, forceRestart);",
        "refresh scheduling ownership",
    )

    source = replace_once(
        source,
        "                runtimeClearTimeout(majorIncidentFeedMotionTimer);\n                majorIncidentFeedMotionTimer = null;\n                majorIncidentFeedMotionRevision += 1;",
        "                majorIncidentFeedCancelAdvance();",
        "card hover advance cancellation",
    )
    source = source.replace("majorIncidentFeedScheduleAdvance(feed, 1500);", "majorIncidentFeedScheduleAdvance(feed, 1500, true);")
    if source.count("majorIncidentFeedScheduleAdvance(feed, 1500, true);") < 2:
        raise SystemExit("Expected pointer/focus resume scheduling to use dedicated restart")

    SOURCE.write_text(source, encoding="utf-8")

    static = STATIC_CONTRACT.read_text(encoding="utf-8")
    static = replace_once(static, "== '7.1.1'", "== '7.1.2'", "wire contract version")
    static = replace_once(
        static,
        "['majorIncidentFeedEntryCount','majorIncidentFeedInteractionActive','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedScheduleAdvance','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance']",
        "['majorIncidentFeedEntryCount','majorIncidentFeedInteractionActive','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedCancelAdvance','majorIncidentFeedScheduleAdvance','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance']",
        "function inventory",
    )
    static = replace_once(
        static,
        "    pause = section(source, '    function majorIncidentFeedSetPaused(', '    function majorIncidentFeedSetExpanded(')\n",
        "    cancel = section(source, '    function majorIncidentFeedCancelAdvance(', '    function majorIncidentFeedScheduleAdvance(')\n"
        "    schedule = section(source, '    function majorIncidentFeedScheduleAdvance(', '    function majorIncidentFeedSetPaused(')\n"
        "    pause = section(source, '    function majorIncidentFeedSetPaused(', '    function majorIncidentFeedSetExpanded(')\n",
        "dedicated timer contract sections",
    )
    static = replace_once(
        static,
        "    assert 'majorIncidentFeedInteractionPauseUntil = 0;' in pause\n",
        "    assert 'majorIncidentFeedInteractionPauseUntil = 0;' in pause\n"
        "    assert source.count('let majorIncidentFeedAdvanceTimer = null;') == 1\n"
        "    assert source.count('let majorIncidentFeedAdvanceRevision = 0;') == 1\n"
        "    assert 'majorIncidentFeedAdvanceTimer' in cancel and 'majorIncidentFeedMotionTimer' not in cancel\n"
        "    assert 'majorIncidentFeedAdvanceTimer' in schedule and 'majorIncidentFeedMotionTimer' not in schedule\n"
        "    assert 'if (majorIncidentFeedAdvanceTimer !== null && !restart) return true;' in schedule\n"
        "    assert 'majorIncidentFeedScheduleAdvance(feed, forceRestart ? 1200 : MAJOR_INCIDENT_FEED_ROTATION_MS, forceRestart);' in motion\n",
        "dedicated timer assertions",
    )
    static = replace_once(
        static,
        "    assert 'align-self:center!important' in source and 'height:100%!important' in source\n",
        "    assert 'align-self:center!important' in source and 'height:calc(100% - 4px)!important' in source\n",
        "rail height assertion",
    )
    static = replace_once(
        static,
        "    assert 'box-sizing:border-box!important' in source and 'margin:0!important' in source\n    assert 'min-height:32px' in source\n",
        "    assert 'box-sizing:border-box!important' in source and 'margin:0!important' in source\n"
        "    assert 'width:26px!important' in source and 'max-height:26px!important' in source\n"
        "    assert 'width:30px!important' in source and 'max-height:30px!important' in source\n"
        "    assert 'overflow:hidden!important' in source\n",
        "control hard-bound assertions",
    )
    STATIC_CONTRACT.write_text(static, encoding="utf-8")

    runtime = RUNTIME_CONTRACT.read_text(encoding="utf-8")
    runtime = replace_once(
        runtime,
        "const functions = ['majorIncidentFeedEntryCount','majorIncidentFeedInteractionActive','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedScheduleAdvance','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance'];",
        "const functions = ['majorIncidentFeedEntryCount','majorIncidentFeedInteractionActive','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedCancelAdvance','majorIncidentFeedScheduleAdvance','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance'];",
        "runtime function inventory",
    )
    runtime = replace_once(
        runtime,
        "    majorIncidentFeedMotionRevision:0,\n    majorIncidentFeedCurrentIndex:0,",
        "    majorIncidentFeedMotionRevision:0,\n    majorIncidentFeedAdvanceTimer:null,\n    majorIncidentFeedAdvanceRevision:0,\n    majorIncidentFeedCurrentIndex:0,",
        "runtime advance state",
    )
    runtime = replace_once(
        runtime,
        "this.api={${functions.join(',')},state:()=>({index:majorIncidentFeedCurrentIndex,paused:majorIncidentFeedManualPaused,expanded:majorIncidentFeedExpanded,pauseUntil:majorIncidentFeedInteractionPauseUntil})};",
        "this.api={${functions.join(',')},state:()=>({index:majorIncidentFeedCurrentIndex,paused:majorIncidentFeedManualPaused,expanded:majorIncidentFeedExpanded,pauseUntil:majorIncidentFeedInteractionPauseUntil,motionTimer:majorIncidentFeedMotionTimer,advanceTimer:majorIncidentFeedAdvanceTimer}),setMotionTimer:value=>{majorIncidentFeedMotionTimer=value;}};",
        "runtime state API",
    )
    old_resume_test = """const resumeTimer = timers.at(-1);
assert.equal(resumeTimer.delay, 650);
const resumeIndex = api.state().index;
resumeTimer.callback();
assert.equal(api.state().index, (resumeIndex + 1) % 3);
assert.equal(timers.at(-1).delay, 6500);"""
    new_resume_test = """const resumeTimer = timers.at(-1);
assert.equal(resumeTimer.delay, 650);
const resumeTimerId = api.state().advanceTimer;
const timerCountBeforeReconcile = timers.length;
api.setMotionTimer(777);
assert.equal(api.majorIncidentFeedScheduleAdvance(feed, 6500, false), true);
assert.equal(timers.length, timerCountBeforeReconcile);
assert.equal(api.state().advanceTimer, resumeTimerId);
assert.equal(api.state().motionTimer, 777);
const resumeIndex = api.state().index;
resumeTimer.callback();
assert.equal(api.state().index, (resumeIndex + 1) % 3);
assert.equal(timers.at(-1).delay, 6500);
const cadenceTimerId = api.state().advanceTimer;
api.setMotionTimer(888);
api.majorIncidentFeedSetPaused(feed, true);
assert.ok(cleared.includes(cadenceTimerId));
assert.equal(api.state().advanceTimer, null);
assert.equal(api.state().motionTimer, 888);"""
    runtime = replace_once(runtime, old_resume_test, new_resume_test, "live reconciliation runtime regression")
    RUNTIME_CONTRACT.write_text(runtime, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    marker = "## [7.1.1] - 2026-07-25"
    section = """## [7.1.2] - 2026-07-25

### Incident Command Wire live rotation recovery

- Separated resize/render reconciliation from automatic incident progression with independently owned timers and revision counters.
- Prevented normal renders and ResizeObserver callbacks from repeatedly cancelling the pending 6.5-second card advance.
- Preserved an existing advance deadline during unchanged reconciliation while allowing explicit Play, manual navigation and queue transitions to restart it deliberately.
- Kept Pause, hidden-tab, reduced-motion, Economy Mode and expanded-queue suppression fail-closed on the dedicated advance timer.
- Hard-bounded all four action controls with important min/max dimensions and contained the rail inside the wire across all themes and responsive modes.
- Added a runtime regression that simulates reconciliation while autoplay is pending and proves the automatic deadline survives.

"""
    if marker not in changelog or "## [7.1.2]" in changelog:
        raise SystemExit("Unexpected changelog state for v7.1.2")
    CHANGELOG.write_text(changelog.replace(marker, section + marker, 1), encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    pattern = re.compile(r"## \*\*Current verified release: `v[^`]+`[^\n]*\*\*")
    readme, count = pattern.subn(
        "## **Current verified release: `v7.1.1` · Development candidate: `v7.1.2` — Live rotation recovery**",
        readme,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Expected one README release marker, found {count}")
    README.write_text(readme, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = help_text.replace("v7.1.1 candidate", "v7.1.2 candidate")
    help_text = help_text.replace(
        "Incident Command Wire play and alignment hotfix for The One We Knew Before",
        "Incident Command Wire live rotation recovery for The One We Knew Before",
    )
    help_text, notice_count = re.subn(
        r'<main><section class="notice"><h2>.*?</p></section>',
        '<main><section class="notice"><h2>What changed in v7.1.2</h2><p>Automatic incident progression now owns a dedicated timer that cannot be cancelled by normal feed rendering or resize reconciliation. The action controls are hard-bounded and contained inside the wire across every Toolkit theme and device mode.</p></section>',
        help_text,
        count=1,
        flags=re.S,
    )
    if notice_count != 1:
        raise SystemExit(f"Expected one Help Centre notice, found {notice_count}")
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("Issue #519 v7.1.2 dedicated rotation and control containment hotfix applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
