#!/usr/bin/env python3
"""Verify Mission Value defaults, routing, formatting and cross-document safety."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


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


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    masked = audit.mask_non_code(source)
    required = [
        "missionValue: true",
        "merged.missionValue = merged.missionValue !== false",
        "makeToggleButton('missionValue', '£', 'Mission Value'",
        "if (feature === 'missionValue') state.missionValue = !state.missionValue",
        "missionValue: state.missionValue",
        "criticalMissionValueDetails({ missionId, marker, snapshot })",
        "installMissionValueWindows()",
        "ensureMissionValueDocumentStyle(doc)",
        "clearMissionValueDocumentStyles()",
        "mcms-mission-value-document-style",
        "clearMissionValueIndicators()",
        "missionValueRightControlOffset(candidate)",
        "positionMissionValueRow(candidate, nextRow)",
        "row.style.setProperty('padding-right'",
        "const fallback = 72",
        "mountRect.right - leftEdge + 16",
        "transportSweepVisibleWindowRoots()",
        "transportSweepDocumentContexts()",
        "data-mcms-mission-value",
        ".mcms-mission-value-row",
        ".mcms-mission-value-badge",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    assert not missing, f"Mission Value contract fragments missing: {missing}"

    row_rule = re.search(r"\.mcms-mission-value-row\s*\{(?P<body>.*?)\n\s*\}", source, re.S)
    assert row_rule, "Mission Value row style missing"
    row_body = row_rule.group("body")
    assert "position: absolute" not in row_body
    assert "justify-content: flex-end" in row_body
    assert "padding: 5px 46px 5px 8px" in row_body
    assert "pointer-events: none" in row_body

    functions = "\n\n".join(extract_function(source, masked, name) for name in [
        "missionValueCurrencyMeta",
        "formatMissionWindowValue",
        "missionValueIdFromUrl",
    ])
    harness = r'''"use strict";
const assert = require("node:assert/strict");
global.location = { hostname: "missionchief.co.uk", href: "https://missionchief.co.uk/" };
function normaliseMissionId(value) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : null;
}
''' + functions + r'''
assert.equal(formatMissionWindowValue(12345, "missionchief.co.uk"), "£12,345");
assert.equal(formatMissionWindowValue(12345, "www.missionchief.com"), "$12,345");
assert.equal(formatMissionWindowValue(12345, "leitstellenspiel.de"), "€12.345");
assert.equal(formatMissionWindowValue(12345, "meldkamerspel.com"), "€12.345");
assert.equal(formatMissionWindowValue(-1, "missionchief.co.uk"), "");
assert.equal(formatMissionWindowValue("not-a-value", "missionchief.co.uk"), "");
assert.equal(missionValueIdFromUrl("/missions/98765"), 98765);
assert.equal(missionValueIdFromUrl("https://missionchief.co.uk/missions/42/missing_vehicles"), 42);
assert.equal(missionValueIdFromUrl("/vehicles/42"), null);
console.log("Mission Value formatting and route contract passed.");
'''
    with tempfile.TemporaryDirectory(prefix="mcms-mission-value-") as temp:
        path = Path(temp) / "contract.js"
        path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(path)], check=True, cwd=ROOT)
    print("Mission Value static integration contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
