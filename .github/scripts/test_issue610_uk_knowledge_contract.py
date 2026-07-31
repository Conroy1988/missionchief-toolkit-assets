#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "9.2.0"
    assert "// @connect      tkb-gaming.scot" in source

    knowledge = section(
        source,
        "    const UK_GUIDE_KNOWLEDGE",
        "    function resourceSearchToken(",
    )
    for required in [
        "https://tkb-gaming.scot/games/missionchief/guides/api/v2/",
        "capabilities.json",
        "units.json",
        "personnel.json",
        "validateUkKnowledgePayload",
        "validateUkKnowledgeCache",
        "freshMs",
        "staleMs",
        "runtime.requests.add",
        "runtime.requests.delete",
        "GM_xmlhttpRequest",
    ]:
        assert required in knowledge, required
    assert "setInterval" not in knowledge
    assert "MutationObserver" not in knowledge
    assert knowledge.count("GM_xmlhttpRequest({") == 1

    performance = json.loads(
        (ROOT / ".github" / "performance-budget.json").read_text(encoding="utf-8")
    )
    assert performance["transitionApproval"]["issue"] == 610
    assert performance["transitionApproval"]["approvedNetworkRequestDelta"] == 1
    assert performance["absoluteLimits"]["network_request_calls"] == 6

    board = section(
        source,
        "    function ukKnowledgeLocalCapability(",
        "    function operationalPressureBoardBodyHtml(",
    )
    for required in [
        "UK INTEL",
        "UNKNOWN · REPORT",
        "MissionChief type",
        "trained crew minimum",
        "all staff must qualify",
        "Associated personnel",
        "CATALOGUE DRIFT",
        "mission-info-missing.yml",
        "noopener,noreferrer",
    ]:
        assert required in board, required
    for forbidden in [
        "document.cookie",
        "csrf",
        "missionId",
        "vehicleId",
        "allianceId",
    ]:
        assert forbidden not in board, forbidden

    shell = section(
        source,
        "    function createOperationalPressureBoard()",
        "    function renderOperationalPressureBoard(",
    )
    for command in [
        "knowledge",
        "knowledge-close",
        "knowledge-refresh",
        "knowledge-report",
    ]:
        assert f"'{command}'" in shell or f'"{command}"' in shell
    assert "aria-modal=\"true\"" in shell
    assert "data-uk-knowledge-body" in shell

    assert (
        'html[data-mcms-tablet-active="true"] #${SCRIPT.pressureBoardId} '
        ":is(.mcms-pressure-sitrep,.mcms-pressure-refresh,.mcms-pressure-close,"
        ".mcms-knowledge-trigger,.mcms-knowledge-panel button,.mcms-knowledge-actions a)"
    ) in source
    assert (
        'html[data-mcms-mobile-active="true"] #${SCRIPT.pressureBoardId} '
        ".mcms-knowledge-units"
    ) in source
    assert (
        'html:is([data-mcms-tablet-active="true"],[data-mcms-mobile-active="true"]) '
        '#${SCRIPT.pressureBoardId} :is(.mcms-knowledge-section h4,'
    ) in source
    assert "font-size:10.5px !important" in source

    print("Issue #610 MissionChief UK Knowledge Link static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
