#!/usr/bin/env python3
# Fixture-backed Desktop operational-workspace geometry, including the reported production layout.
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURES = ROOT / ".github" / "fixtures" / "desktop-panel-layout-contract.json"


def extract_function(source: str, masked: str, name: str) -> str:
    matches = list(re.finditer(rf"\bfunction\s+{re.escape(name)}\s*\(", masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Could not extract {name}")
    return source[start:closing + 1]


def assert_static_contract(source: str, masked: str) -> None:
    required = [
        'html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId}.mcms-open',
        'html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack',
        'html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel.mcms-active',
        'grid-template-rows: auto minmax(0, 1fr) !important',
        'position: sticky !important',
        'top: 0 !important',
        'box-sizing: border-box !important',
        'overflow-y: auto !important',
        'min-height: 0 !important',
        'html[data-mcms-tablet-active="true"] #${SCRIPT.panelId}',
        'html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}',
        'collectDesktopWorkspaceObstructions(viewport, mapEl, panel)',
        'observeDesktopPanelWorkspace(mapEl)',
        'applyDesktopPanelSizing(panel, mapEl)',
        'clampDesktopPanelPoint(left, top, panelWidth, panelHeight, bounds)',
        'document.documentElement',
        'document.body',
        'panel.dataset.mcmsDesktopFit',
        'minimumTopChrome',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    assert not missing, f"Desktop layout contract fragments missing: {missing}"

    shell_rule = re.search(
        r'html\[data-mcms-device-layout="desktop"\] body #\$\{SCRIPT\.panelId\}\.mcms-open \{(?P<body>.*?)\n\s*\}',
        source,
        re.S,
    )
    assert shell_rule, "Desktop fixed-chrome grid shell missing"
    shell_body = shell_rule.group("body")
    assert "display: grid !important" in shell_body
    assert "grid-template-rows: auto minmax(0, 1fr) !important" in shell_body

    chrome_rule = re.search(
        r'html\[data-mcms-device-layout="desktop"\] body #\$\{SCRIPT\.panelId\} > \.mcms-panel-sticky-stack \{(?P<body>.*?)\n\s*\}',
        source,
        re.S,
    )
    assert chrome_rule, "Desktop command chrome rule missing"
    chrome_body = chrome_rule.group("body")
    assert "grid-row: 1 !important" in chrome_body
    assert "position: sticky !important" in chrome_body
    assert "top: 0 !important" in chrome_body
    assert "z-index: 30 !important" in chrome_body

    desktop_rule = re.search(
        r'html\[data-mcms-device-layout="desktop"\] body #\$\{SCRIPT\.panelId\} > \.mcms-tab-panel\.mcms-active \{(?P<body>.*?)\n\s*\}',
        source,
        re.S,
    )
    assert desktop_rule, "Desktop content-only scroll rule missing"
    body = desktop_rule.group("body")
    assert "height: 100% !important" in body
    assert "overflow-y: auto !important" in body
    assert "overflow-x: hidden !important" in body
    assert "min-height: 0 !important" in body

    resolver = extract_function(source, masked, "resolveDesktopPanelBounds")
    assert "const areaBottom = viewportBottom;" in resolver
    assert "const areaLeft = viewportLeft;" in resolver
    assert "const areaRight = viewportRight;" in resolver
    assert "Math.min(viewportBottom, mapRect.bottom)" not in resolver
    assert "areaBottom = mapRect.bottom" not in resolver


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    masked = audit.mask_non_code(source)
    assert_static_contract(source, masked)
    functions = "\n\n".join(
        extract_function(source, masked, name)
        for name in ["resolveDesktopPanelBounds", "clampDesktopPanelPoint"]
    )
    harness = f"""\"use strict\";
const assert = require("node:assert/strict");
const fixtures = {json.dumps(fixtures)};
function getViewportMetrics() {{ throw new Error("Explicit fixture viewport expected"); }}
{functions}
for (const item of fixtures.boundsCases) {{
  assert.deepEqual(
    resolveDesktopPanelBounds(
      item.mapRect,
      item.viewport,
      item.margin,
      item.obstructionRects || []
    ),
    item.expected,
    item.name
  );
}}
for (const item of fixtures.clampCases) {{
  assert.deepEqual(
    clampDesktopPanelPoint(item.point.left, item.point.top, item.panel.width, item.panel.height, item.bounds),
    item.expected,
    item.name
  );
}}
console.log(`Desktop operational-workspace contract passed: ${{fixtures.boundsCases.length}} bounds and ${{fixtures.clampCases.length}} saved-position cases.`);
"""
    with tempfile.TemporaryDirectory(prefix="mcms-desktop-layout-") as temp:
        path = Path(temp) / "contract.js"
        path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(path)], check=True, cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
