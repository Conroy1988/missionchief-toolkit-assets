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
SELF = ROOT / ".github" / "issue519" / "apply_hotfix.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-wire-hotfix.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


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
    candidate = fixture["v7Candidate"]
    candidate.update({
        "issue": 519,
        "version": "7.1.1",
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
    source = replace_once(source, "// @version      7.1.0", "// @version      7.1.1", "metadata version")
    source = replace_once(source, "version: '7.1.0',", "version: '7.1.1',", "runtime version")

    old_controls = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls{position:relative;z-index:7;flex:0 0 auto;align-self:stretch;display:flex;align-items:center;gap:3px;padding:0 5px;border-left:1px solid var(--mcms-wire-border);background:rgba(0,0,0,.12)}'
    new_controls = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls{position:relative!important;top:auto!important;bottom:auto!important;z-index:7;flex:0 0 auto;align-self:center!important;display:flex;align-items:center!important;justify-content:center;height:100%!important;min-height:0;box-sizing:border-box!important;margin:0!important;gap:3px;padding:0 5px;border-left:1px solid var(--mcms-wire-border);background:rgba(0,0,0,.12);transform:none!important}'
    source = replace_once(source, old_controls, new_controls, "control rail style")

    old_buttons = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{appearance:none;display:grid;place-items:center;width:27px;height:27px;min-width:27px;padding:0;border:1px solid var(--mcms-wire-border);border-radius:5px;background:rgba(255,255,255,.055);color:var(--mcms-wire-text);font:900 13px/1 Arial,sans-serif;cursor:pointer}'
    new_buttons = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{appearance:none;-webkit-appearance:none;position:relative!important;top:auto!important;bottom:auto!important;float:none!important;align-self:center!important;box-sizing:border-box!important;display:grid;place-items:center;width:27px;height:27px;min-width:27px;min-height:27px;margin:0!important;padding:0;border:1px solid var(--mcms-wire-border);border-radius:5px;background:rgba(255,255,255,.055);color:var(--mcms-wire-text);font:900 13px/1 Arial,sans-serif;cursor:pointer;transform:none!important;vertical-align:middle}'
    source = replace_once(source, old_buttons, new_buttons, "control button style")
    source = replace_once(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:32px;height:32px;min-width:32px}',
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:32px;height:32px;min-width:32px;min-height:32px}',
        "tablet control size",
    )

    old_pause = """    function majorIncidentFeedSetPaused(feed, paused) {
        majorIncidentFeedManualPaused = Boolean(paused);
        feed?.classList?.toggle('mcms-feed-paused', majorIncidentFeedManualPaused);
        majorIncidentFeedSyncControls(feed);
        if (majorIncidentFeedManualPaused) {
            runtimeClearTimeout(majorIncidentFeedMotionTimer);
            majorIncidentFeedMotionTimer = null;
            majorIncidentFeedMotionRevision += 1;
        } else {
            majorIncidentFeedScheduleAdvance(feed, 900);
        }
    }"""
    new_pause = """    function majorIncidentFeedSetPaused(feed, paused) {
        majorIncidentFeedManualPaused = Boolean(paused);
        feed?.classList?.toggle('mcms-feed-paused', majorIncidentFeedManualPaused);
        majorIncidentFeedSyncControls(feed);
        if (majorIncidentFeedManualPaused) {
            runtimeClearTimeout(majorIncidentFeedMotionTimer);
            majorIncidentFeedMotionTimer = null;
            majorIncidentFeedMotionRevision += 1;
        } else {
            majorIncidentFeedInteractionPauseUntil = 0;
            feed?.classList?.remove('mcms-feed-interacting');
            runtimeClearTimeout(majorIncidentFeedMotionTimer);
            majorIncidentFeedMotionTimer = null;
            majorIncidentFeedMotionRevision += 1;
            majorIncidentFeedScheduleAdvance(feed, 650);
        }
    }"""
    source = replace_once(source, old_pause, new_pause, "play/resume function")

    old_pointer = """            feed.addEventListener('pointerenter', () => {
                feed.classList.add('mcms-feed-interacting');
                runtimeClearTimeout(majorIncidentFeedMotionTimer);
                majorIncidentFeedMotionTimer = null;
                majorIncidentFeedMotionRevision += 1;
            });
            feed.addEventListener('pointerleave', () => {
                feed.classList.remove('mcms-feed-interacting');
                majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;
                majorIncidentFeedScheduleAdvance(feed, 1500);
            });
            feed.addEventListener('focusin', () => feed.classList.add('mcms-feed-interacting'));
            feed.addEventListener('focusout', () => runtimeSetTimeout(() => {
                if (!feed.contains(document.activeElement)) {
                    feed.classList.remove('mcms-feed-interacting');
                    majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;
                    majorIncidentFeedScheduleAdvance(feed, 1500);
                }
            }, 0));
            feed.addEventListener('pointerdown', () => {
                majorIncidentFeedInteractionPauseUntil = Date.now() + MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS;
            }, { passive: true });"""
    new_pointer = """            feed.addEventListener('pointerover', event => {
                const zone = closestEventTarget(event, '.mcms-incident-feed-viewport,.mcms-incident-feed-panel');
                if (!zone || zone.contains(event.relatedTarget)) return;
                feed.classList.add('mcms-feed-interacting');
                runtimeClearTimeout(majorIncidentFeedMotionTimer);
                majorIncidentFeedMotionTimer = null;
                majorIncidentFeedMotionRevision += 1;
            });
            feed.addEventListener('pointerout', event => {
                const zone = closestEventTarget(event, '.mcms-incident-feed-viewport,.mcms-incident-feed-panel');
                if (!zone || zone.contains(event.relatedTarget)) return;
                const nextZone = event.relatedTarget?.closest?.('.mcms-incident-feed-viewport,.mcms-incident-feed-panel');
                if (nextZone && feed.contains(nextZone)) return;
                feed.classList.remove('mcms-feed-interacting');
                majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;
                majorIncidentFeedScheduleAdvance(feed, 1500);
            });
            feed.addEventListener('focusin', event => {
                if (closestEventTarget(event, '[data-mcms-incident-action]')) return;
                if (closestEventTarget(event, '[data-mcms-major-mission-id],.mcms-incident-feed-panel')) {
                    feed.classList.add('mcms-feed-interacting');
                }
            });
            feed.addEventListener('focusout', () => runtimeSetTimeout(() => {
                const active = document.activeElement;
                if (!feed.contains(active) || active?.closest?.('[data-mcms-incident-action]')) {
                    feed.classList.remove('mcms-feed-interacting');
                    majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;
                    majorIncidentFeedScheduleAdvance(feed, 1500);
                }
            }, 0));
            feed.addEventListener('pointerdown', event => {
                if (closestEventTarget(event, '[data-mcms-incident-action]')) return;
                majorIncidentFeedInteractionPauseUntil = Date.now() + MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS;
            }, { passive: true });"""
    source = replace_once(source, old_pointer, new_pointer, "interaction listener block")
    SOURCE.write_text(source, encoding="utf-8")

    static = STATIC_CONTRACT.read_text(encoding="utf-8")
    static = replace_once(static, "== '7.1.0'", "== '7.1.1'", "wire contract version")
    static = replace_once(
        static,
        "    motion = section(source, '    function refreshMajorIncidentFeedMotion(', '    function scheduleMajorIncidentFeedMotion(')\n",
        "    motion = section(source, '    function refreshMajorIncidentFeedMotion(', '    function scheduleMajorIncidentFeedMotion(')\n"
        "    pause = section(source, '    function majorIncidentFeedSetPaused(', '    function majorIncidentFeedSetExpanded(')\n",
        "pause contract section",
    )
    static = replace_once(
        static,
        "    assert \"feed.addEventListener('pointerenter'\" in ensure\n",
        "    assert \"feed.addEventListener('pointerover'\" in ensure\n"
        "    assert \"feed.addEventListener('pointerout'\" in ensure\n"
        "    assert \"if (closestEventTarget(event, '[data-mcms-incident-action]')) return;\" in ensure\n",
        "pointer contract",
    )
    static = replace_once(
        static,
        "    assert 'state.economyMode' in motion\n",
        "    assert 'state.economyMode' in motion\n"
        "    assert 'majorIncidentFeedInteractionPauseUntil = 0;' in pause\n"
        "    assert \"feed?.classList?.remove('mcms-feed-interacting');\" in pause\n"
        "    assert 'majorIncidentFeedScheduleAdvance(feed, 650);' in pause\n"
        "    assert 'align-self:center!important' in source and 'height:100%!important' in source\n"
        "    assert 'box-sizing:border-box!important' in source and 'margin:0!important' in source\n"
        "    assert 'min-height:32px' in source\n",
        "resume and alignment assertions",
    )
    STATIC_CONTRACT.write_text(static, encoding="utf-8")

    runtime = RUNTIME_CONTRACT.read_text(encoding="utf-8")
    runtime = replace_once(
        runtime,
        "api.majorIncidentFeedSetPaused(feed, false);\nassert.equal(controls.pause.textContent, 'Ⅱ');",
        "feed.classList.add('mcms-feed-interacting');\n"
        "api.majorIncidentFeedSetPaused(feed, false);\n"
        "assert.equal(controls.pause.textContent, 'Ⅱ');\n"
        "assert.equal(api.state().pauseUntil, 0);\n"
        "assert.equal(feed.classList.contains('mcms-feed-interacting'), false);\n"
        "const resumeTimer = timers.at(-1);\n"
        "assert.equal(resumeTimer.delay, 650);\n"
        "const resumeIndex = api.state().index;\n"
        "resumeTimer.callback();\n"
        "assert.equal(api.state().index, (resumeIndex + 1) % 3);\n"
        "assert.equal(timers.at(-1).delay, 6500);",
        "runtime resume assertions",
    )
    RUNTIME_CONTRACT.write_text(runtime, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    marker = "## [7.1.0] - 2026-07-25"
    section = """## [7.1.1] - 2026-07-25

### Incident Command Wire play and alignment hotfix

- Fixed Play so it clears stale hover, focus and manual-interaction delays and resumes visible automatic rotation within 650 ms.
- Excluded the control rail from card-hover and card-focus pause ownership while preserving pauses over incident cards and the expanded queue.
- Prevented control clicks from creating a new nine-second interaction delay before their own command executes.
- Vertically centred the previous, pause/play, next and expand buttons with explicit position, margin, transform, sizing and box-model resets across all seven themes.
- Extended runtime and static contracts for automatic resume, continued cadence, control-zone interaction isolation and responsive alignment.

"""
    if marker not in changelog or "## [7.1.1]" in changelog:
        raise SystemExit("Unexpected changelog state for v7.1.1")
    CHANGELOG.write_text(changelog.replace(marker, section + marker, 1), encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    pattern = re.compile(r"## \*\*Current verified release: `v[^`]+`[^\n]*\*\*")
    readme, count = pattern.subn(
        "## **Current verified release: `v7.1.0` · Development candidate: `v7.1.1` — Incident Command Wire hotfix**",
        readme,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Expected one README release marker, found {count}")
    README.write_text(readme, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = help_text.replace("v7.1.0 candidate", "v7.1.1 candidate")
    help_text = help_text.replace(
        "emergency launcher restoration for The One We Knew Before",
        "Incident Command Wire play and alignment hotfix for The One We Knew Before",
    )
    help_text, notice_count = re.subn(
        r'<main><section class="notice"><h2>.*?</p></section>',
        '<main><section class="notice"><h2>What changed in v7.1.1</h2><p>Play now clears stale interaction delays and restarts automatic incident rotation immediately. The four wire controls are explicitly centred inside the bar across every Toolkit theme and supported device mode.</p></section>',
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

    print("Issue #519 v7.1.1 wire resume and alignment hotfix applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
