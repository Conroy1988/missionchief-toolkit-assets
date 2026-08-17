#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def source_section(source: str, start: str, end: str) -> str:
    left = source.index(start)
    right = source.index(end, left)
    return source[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert "version: '10.9.1'" in source
    assert "const COMMAND_SECTION_ORDER = Object.freeze(['map', 'missions', 'alliance', 'dispatch', 'finance', 'locations', 'appearance', 'settings']);" in source
    assert "label: 'Alliance Admin'" in source and "title: 'Alliance Administration'" in source
    assert "'allianceCourses'" in source, "Alliance Courses analytics allow-list entry is missing"

    panel = source_section(source, "    function createPanel(", "    function ensureUi()")
    alliance_start = panel.index('<section class="mcms-tab-panel" data-panel="alliance">')
    resources_start = panel.index('<section class="mcms-tab-panel" data-panel="resources">', alliance_start)
    alliance_panel = panel[alliance_start:resources_start]
    resources_end = panel.index('<section class="mcms-tab-panel" data-panel="ops">', resources_start)
    resources_panel = panel[resources_start:resources_end]
    for token in (
        'data-action="scan-alliance-courses"',
        'data-action="start-alliance-courses"',
        'data-action="stop-alliance-courses"',
        'data-setting="alliance-course-day"',
        'data-setting="alliance-course-duration"',
        'data-setting="alliance-course-delay"',
        'data-alliance-courses',
        'Alliance setup &amp; supported building names',
        'data-action="scan-transport-sweep"',
    ):
        assert token in alliance_panel, f"Alliance Admin is missing {token}"
    assert 'data-action="scan-transport-sweep"' not in resources_panel, "Patient Transport Sweep remains under Missions"
    assert '<option value="86400">1 day</option>' in alliance_panel
    assert 'maximum rooms exposed by MissionChief' in alliance_panel
    assert '0 Credits' in alliance_panel
    assert 'Native Admin, Co-Admin or Alliance Educator access is required.' in alliance_panel

    catalog = source_section(source, "    const ALLIANCE_COURSE_CATALOG", "    function normaliseAllianceCourseText(")
    academy_counts = {
        "ambulance": 6,
        "police": 12,
        "fire": 7,
        "rescue": 14,
    }
    for academy, expected in academy_counts.items():
        match = re.search(rf"\n        {academy}: Object\.freeze\(\[(?P<body>.*?)(?=\n        \]\)[,\n])", catalog, re.S)
        assert match, f"Missing {academy} course catalog"
        actual = match.group("body").count("Object.freeze({ key:")
        assert actual == expected, f"{academy} catalog has {actual} mappings, expected {expected}"
    for native_label in (
        "Ambulance Officer",
        "HART Training",
        "Drone Operator Training",
        "Level 1 Public Order Training",
        "Aircraft Rescue and Firefighting",
        "High Volume Pump Training",
        "Coastguard Search Advisor Training",
        "Search Management Training",
    ):
        assert f"nativeLabel: '{native_label}'" in catalog

    implementation = source_section(source, "    function normaliseAllianceCourseText(", "    function vehicleTargetInfo(")
    for native_field in (
        '#building_rooms_use[name="building_rooms_use"]',
        '#education_select[name="education_select"]',
        '#alliance_duration[name="alliance[duration]"]',
        '#alliance_cost[name="alliance[cost]"]',
        'input[name="authenticity_token"]',
        "params.set('commit', 'Educate')",
    ):
        assert native_field in implementation, f"Missing native form guard: {native_field}"
    assert "sort((left, right) => Number(right.value) - Number(left.value))[0]" in implementation
    assert "Number(option.value) === 0" in implementation
    assert "action.pathname === `/buildings/${item.buildingId}/education`" in implementation
    assert "countAllianceCourseEvidence(responseDocument, item.nativeLabel)" in implementation
    assert "if (evidence <= prepared.baseline)" in implementation
    assert "no automatic retry was made" in implementation
    assert "busyNames: [], unmappedNames: []" in implementation
    assert "Busy / unavailable" in implementation
    assert "Unmapped / ambiguous" in implementation
    assert "pageWindow.confirm(`Alliance Courses will start" in implementation
    assert "for (let index = 0; index < planned.length; index += 1)" in implementation
    assert "await runtimeDelay(state.allianceCourses.delayMs)" in implementation
    assert "Promise.all" not in source_section(source, "    async function startAllianceCourses(", "    function stopAllianceCourses(")
    assert "ALLIANCE_COURSE_START_LIMIT = 100" in source
    assert "ALLIANCE_COURSE_SCAN_LIMIT = 150" in source
    assert "ALLIANCE_COURSE_REQUEST_TIMEOUT_MS = 12000" in source
    assert "setting.startsWith('alliance-course-') && (allianceCourseRuntime.running || allianceCourseRuntime.scanPromise)" in source
    assert "if (allianceCourseRuntime.running || runtime.destroyed) return;" in implementation
    assert "[data-setting^=\"alliance-course-\"]" in implementation

    assert "allianceCourses: { day: 'today', shareDuration: 86400, delayMs: 1500 }" in source
    assert "ALLIANCE_COURSE_SHARE_DURATION_OPTIONS.includes" in source
    assert "ALLIANCE_COURSE_DELAY_OPTIONS.includes" in source
    assert "ALLIANCE_COURSE_DAY_OPTIONS.includes" in source
    print("Issue #704 Alliance Courses source contract passed: 39 academy mappings and fail-closed native submission guards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
