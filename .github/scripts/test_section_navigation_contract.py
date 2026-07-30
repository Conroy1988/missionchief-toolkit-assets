#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/section-navigation-contract.json"


def rule_body(source: str, selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{(?P<body>.*?)\}", source, re.S)
    assert match, f"Missing CSS rule: {selector}"
    return match.group("body")


def wrapped_lines(label: str, width: float, font: float) -> int:
    capacity = max(1, int(width / max(1.0, font * 0.56)))
    lines = 1
    used = 0
    for word in label.split():
        length = len(word)
        if used == 0:
            used = length
        elif used + 1 + length <= capacity:
            used += 1 + length
        else:
            lines += 1
            used = length
    return lines


def object_body(source: str, declaration: str) -> str:
    start = source.index(declaration)
    open_brace = source.index("{", start)
    close = source.index("\n    });", open_brace)
    return source[open_brace + 1 : close]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    expected_keys = [item["key"] for item in fixture["tabs"]]

    order_match = re.search(r"const COMMAND_SECTION_ORDER = Object\.freeze\(\[([^\]]+)\]\);", source)
    assert order_match, "Missing canonical v9 section order"
    order = re.findall(r"'([^']+)'", order_match.group(1))
    assert order == expected_keys, f"Command section order drifted: {order}"

    meta = object_body(source, "const COMMAND_SECTION_META")
    for item in fixture["tabs"]:
        entry = re.search(
            rf"{re.escape(item['key'])}:\s*Object\.freeze\(\{{(?P<body>.*?)\}}\)",
            meta,
            re.S,
        )
        assert entry, f"Missing metadata for {item['key']}"
        body = entry.group("body")
        for field in ("label", "title", "description"):
            assert f"{field}: '{item[field]}'" in body, f"{item['key']} {field} drifted"

    migration = object_body(source, "const LEGACY_COMMAND_SECTION_MAP")
    actual_migration = dict(re.findall(r"(\w+):\s*'([^']+)'", migration))
    assert actual_migration == fixture["legacyStateMigration"], actual_migration
    assert "merged.activeTab = LEGACY_COMMAND_SECTION_MAP[merged.activeTab] || merged.activeTab;" in source
    assert "merged.activeTab = COMMAND_SECTION_ORDER.includes(merged.activeTab) ? merged.activeTab : 'map';" in source

    start = source.index("        panel.innerHTML = `", source.index("const positionButtons"))
    end = source.index("\n        `;", start)
    panel = source[start:end]
    legacy_panels = re.findall(r'<section class="mcms-tab-panel" data-panel="([^"]+)">', panel)
    expected_legacy = [
        legacy
        for key in expected_keys
        for legacy in fixture["legacyPanelSources"][key]
    ]
    assert set(legacy_panels) == set(expected_legacy), f"Legacy source panel inventory drifted: {legacy_panels}"

    section_ranges = {}
    matches = list(re.finditer(r'<section class="mcms-tab-panel" data-panel="([^"]+)">', panel))
    for index, match in enumerate(matches):
        section_ranges[match.group(1)] = panel[match.start() : matches[index + 1].start() if index + 1 < len(matches) else len(panel)]

    for section, tokens in fixture["placements"].items():
        body = "".join(section_ranges[source_name] for source_name in fixture["legacyPanelSources"][section])
        for token in tokens:
            assert token in body, f"{token!r} is not routed into canonical section {section}"
    for token in fixture["singlePlacementTokens"]:
        assert panel.count(token) == 1, f"{token!r} must appear once, found {panel.count(token)}"

    upgrade = source[source.index("    function upgradeCommandInterface(") : source.index("    function commandInterfaceApplySearch(")]
    for token in [
        "tabs.replaceChildren();",
        "tabs.insertAdjacentHTML('afterbegin', commandSectionNavigationMarkup());",
        "missions.append(...Array.from(missionOperations.childNodes));",
        "finance.append(...Array.from(payout.childNodes));",
        "wrapCommandSectionCards(section);",
        "content.appendChild(section);",
        "panel.dataset.mcmsCommandInterface = 'v9';",
    ]:
        assert token in upgrade, f"Missing v9 runtime upgrade guarantee: {token}"
    assert "const COMMAND_SECTION_ORDER" in source and "${commandSectionNavigationMarkup()}" in panel

    label = rule_body(source, '#${SCRIPT.panelId} .mcms-label')
    assert "white-space: normal !important" in label
    assert "overflow-wrap: anywhere !important" in label
    assert "text-overflow: ellipsis" not in label
    row_label = rule_body(source, '#${SCRIPT.panelId} .mcms-row-label')
    assert "white-space: normal !important" in row_label
    assert "overflow-wrap: anywhere !important" in row_label
    section_label = rule_body(source, '#${SCRIPT.panelId} .mcms-section-label')
    assert "overflow-wrap: anywhere !important" in section_label

    for selector in [
        '#${SCRIPT.panelId} .mcms-small-btn',
        'html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn',
        'html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn',
    ]:
        body = rule_body(source, selector)
        assert "height: auto !important" in body or "height:auto !important" in body
        assert "line-height: 1.15 !important" in body or "line-height:1.15 !important" in body

    backup_actions = rule_body(source, '#${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn')
    assert "white-space:normal" in backup_actions.replace(" ", "")
    assert "text-overflow:ellipsis" not in backup_actions.replace(" ", "")

    for theme in fixture["themes"]:
        assert theme in source, f"Supported theme missing from source: {theme}"

    for case in fixture["narrowLabelCases"]:
        assert case["label"] in panel, f"Narrow-layout fixture label missing: {case['label']}"
        usable = case["width"] - case["icon"] - case["gap"] - case["padding"]
        needed = wrapped_lines(case["label"], usable, case["font"])
        assert needed <= case["maxLines"], f"{case['label']} needs {needed} lines at fixture width"

    print(
        f"Section-navigation contract passed: {len(order)} v9 sections, "
        f"{len(fixture['singlePlacementTokens'])} canonical controls and "
        f"{len(fixture['narrowLabelCases'])} narrow-label cases."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
