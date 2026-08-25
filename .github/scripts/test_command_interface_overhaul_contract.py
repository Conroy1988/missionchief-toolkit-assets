#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def section(source: str, start: str, end: str) -> str:
    left = source.index(start)
    right = source.index(end, left)
    return source[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert "// @version      10.18.0" in source
    assert "const VERSION = '10.18.0';" in source
    assert "version: '10.18.0'" in source
    assert 'version: "10.18.0"' in source

    assert "const COMMAND_SECTION_ORDER = Object.freeze(['map', 'incidents', 'fleet', 'administration', 'finance', 'status', 'settings']);" in source
    for legacy, target in {
        "missions": "incidents",
        "resources": "fleet",
        "alliance": "administration",
        "dispatch": "administration",
        "locations": "map",
        "appearance": "settings",
    }.items():
        assert re.search(rf"\b{legacy}:\s*'{target}'", source), f"missing {legacy} → {target} migration"

    command_bar = section(source, "    const COMMAND_BAR_PRIMARY_MIN", "    // <mcms-fast-map>")
    assert "COMMAND_BAR_PRIMARY_MIN = 4" in command_bar
    assert "COMMAND_BAR_PRIMARY_MAX = 6" in command_bar
    assert "['myMissions', 'allianceMissions', 'vehicles', 'buildings', 'open-command-palette']" in command_bar
    control = section(source, "    function createControl(", "    function commandSectionSlug(")
    for token in (
        'class="mcms-command-primary mcms-control-group"',
        'data-action="toggle-command-overflow"',
        'class="mcms-command-overflow"',
        'class="mcms-command-overflow-groups"',
    ):
        assert token in control, token
    assert source.count("makeFloatButton(") >= 9
    assert source.count("makeActionFloatButton(") >= 4
    assert "normaliseCommandBarPrimary(parsed.commandBarPrimary)" in source
    assert 'data-command-primary="${escapeHtml(key)}"' in source

    workflows = section(source, "    const ADMIN_WORKFLOW_STAGES", "    function upgradeCommandInterface(")
    for stage in ("scope", "configure", "review", "run", "results"):
        assert f"key: '{stage}'" in workflows
    for card in (
        "alliance-courses",
        "co-admin-patient-transport-sweep",
        "dispatch-recruitment",
        "station-icon-copier",
        "expansion-and-upgrade-planner",
    ):
        assert f"'{card}'" in workflows
    for token in (
        "setAdministrationWorkflowStage",
        "advanceAdministrationWorkflowFromAction",
        "enhanceAdministrationWorkflow",
        "enhanceProgressiveGuidance",
        "data-workflow-stage-button",
        "data-workflow-stage-panel",
    ):
        assert token in workflows

    status = section(source, "    function createStatusCentreSection(", "    function upgradeCommandInterface(")
    for token in (
        "Operations Status Centre",
        "versionStatusModel",
        "fastMapRuntime",
        "allianceCourseRuntime",
        "transportSweepRuntime",
        "dispatchRecruitmentRuntime",
        "stationIconCopierRuntime",
        "expansionPlannerRuntime",
        "authority",
    ):
        assert token in status, token
    for forbidden in ("runtimeSetInterval(", "runtimeRegisterTask(", "MutationObserver", "GM_xmlhttpRequest", "fetch("):
        assert forbidden not in status, f"Status Centre added active work: {forbidden}"

    personalisation = section(source, "    function personalisationTabsMarkup(", "    function saveAndApplyPersonalisation(")
    for tab in ("layout", "appearance", "controls", "alerts", "recovery"):
        assert f"['{tab}'," in personalisation
    for old, new in {
        "theme": "appearance",
        "shell": "appearance",
        "wheel": "controls",
        "input": "controls",
        "notifications": "alerts",
        "backup": "recovery",
        "setup": "recovery",
    }.items():
        assert f"{old}: '{new}'" in personalisation

    palette = section(source, "    function commandPaletteNormalise(", "    function closeHelpCenter(")
    assert "COMMAND_PALETTE_SCOPES" in source
    for label in ("All", "Commands", "Missions", "Vehicles", "Buildings", "Places", "Settings"):
        assert f"label: '{label}'" in source
    for token in ("commandPaletteScope", "commandPaletteRecentIds", "data-command-palette-scope", "RECENT ·"):
        assert token in palette or token in source
    panel = section(source, "    function createPanel(", "    function renderQuickPlaces(")
    assert 'data-action="open-command-palette" title="Search every command' in panel
    assert 'data-action="toggle-command-search"' not in panel

    mobile = section(source, "    function mobileCommandNavigationMarkup(", "    function commandInterfacePanel(")
    assert "['map', 'incidents', 'fleet', 'administration']" in mobile
    assert "['finance', 'status', 'settings']" in mobile
    assert 'data-action="toggle-mobile-more"' in mobile
    assert "grid-template-columns:repeat(5,minmax(0,1fr))" in source

    for token in (
        ".mcms-state-pill",
        ".mcms-guidance",
        ".mcms-workflow-steps",
        ".mcms-status-centre-grid",
        "font-size:max(11.5px,1em)",
        "@media(prefers-reduced-motion:reduce)",
    ):
        assert token in source, token

    print("v10.18 command-interface overhaul contract passed: task navigation, configurable command bar, guided workflows, status, mobile, personalisation, search, typography and motion are retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
