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


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    start = source.index("        panel.innerHTML = `", source.index("const positionButtons"))
    end = source.index("\n        `;", start)
    panel = source[start:end]

    tabs = re.findall(r'data-tab="([^"]+)">([^<]+)</button>', panel)
    expected_tabs = [(item["key"], item["label"]) for item in fixture["tabs"]]
    assert tabs == expected_tabs, f"Tab order/labels drifted: {tabs}"
    panels = re.findall(r'<section class="mcms-tab-panel" data-panel="([^"]+)">', panel)
    assert panels == [item["key"] for item in fixture["tabs"]], f"Panel order drifted: {panels}"

    section_ranges = {}
    matches = list(re.finditer(r'<section class="mcms-tab-panel" data-panel="([^"]+)">', panel))
    for index, match in enumerate(matches):
        section_ranges[match.group(1)] = panel[match.start() : matches[index + 1].start() if index + 1 < len(matches) else len(panel)]

    for section, tokens in fixture["placements"].items():
        body = section_ranges[section]
        for token in tokens:
            assert token in body, f"{token!r} is not in canonical section {section}"
    for token in fixture["singlePlacementTokens"]:
        assert panel.count(token) == 1, f"{token!r} must appear once, found {panel.count(token)}"

    assert "if (merged.activeTab === 'fleet') merged.activeTab = 'resources';" in source
    assert "['skins', 'tools', 'resources', 'ops', 'payouts', 'discord', 'places', 'settings']" in source

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

    print(f"Section-navigation contract passed: {len(tabs)} sections, {len(fixture['singlePlacementTokens'])} canonical controls and {len(fixture['narrowLabelCases'])} narrow-label cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
