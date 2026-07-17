#!/usr/bin/env python3
"""Fixture-backed layout contract for the Financial Command Discord image."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "financial-discord-image-layout-contract.json"
FUNCTION_NAMES = ["fitFinancialCanvasText", "financialSnapshotRows", "drawFinancialSnapshotRow"]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\bfunction\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    parameter_open = masked.find("(", start)
    if parameter_open < 0:
        raise AssertionError(f"Parameter list not found for {name}")
    depth = 0
    parameter_close = None
    for index in range(parameter_open, len(masked)):
        char = masked[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                parameter_close = index
                break
    if parameter_close is None:
        raise AssertionError(f"Parameter list did not close for {name}")
    opening = masked.find("{", parameter_close + 1)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Unable to extract {name}")
    return source[start:closing + 1]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert "['Audit basis', report.reconciliationLabel]" not in source, (
        "Legacy unconstrained reconciliation row remains"
    )
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(extract_function(source, masked, name) for name in FUNCTION_NAMES)
    fixtures = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_json = json.dumps(fixtures, ensure_ascii=False)
    harness = f'''"use strict";
const assert = require("node:assert/strict");
const fixtures = {fixture_json};
function formatSignedCompactCredits(value) {{
    const numeric = Number(value) || 0;
    const sign = numeric > 0 ? "+" : numeric < 0 ? "-" : "";
    const magnitude = Math.abs(numeric);
    const compact = magnitude >= 1000000000
        ? `${{(magnitude / 1000000000).toFixed(1).replace(/\\.0$/, "")}}b`
        : magnitude >= 1000000
            ? `${{(magnitude / 1000000).toFixed(1).replace(/\\.0$/, "")}}m`
            : magnitude >= 1000
                ? `${{(magnitude / 1000).toFixed(1).replace(/\\.0$/, "")}}k`
                : String(Math.round(magnitude));
    return `${{sign}}£${{compact}}`;
}}
{functions}
class FakeContext {{
    constructor() {{
        this._font = "600 15px Arial, sans-serif";
        this.textAlign = "left";
        this.fillStyle = "";
        this.calls = [];
    }}
    set font(value) {{ this._font = String(value); }}
    get font() {{ return this._font; }}
    measureText(value) {{
        const match = this._font.match(/(\\d+(?:\\.\\d+)?)px/);
        const size = match ? Number(match[1]) : 15;
        return {{ width: String(value).length * size * 0.56 }};
    }}
    fillText(text, x, y) {{
        this.calls.push({{ text: String(text), x, y, align: this.textAlign, font: this._font }});
    }}
}}
function baseReport(extra = {{}}) {{
    return {{
        operatingResult: 1250000,
        capitalInvestment: 2750000,
        activeIncomePerHour: 725000,
        incomePerHour: 700000,
        classificationConfidence: 98.5,
        scorecard: {{ overall: 88 }},
        balanceCalculated: true,
        reconciliationDifference: 0,
        ...extra
    }};
}}
for (const item of fixtures.auditRows) {{
    const rows = financialSnapshotRows(baseReport(item.report));
    assert.equal(rows.length, 6, item.name);
    const auditRow = rows[5];
    assert.equal(auditRow[0], item.expectedLabel, item.name);
    assert.equal(auditRow[1], item.expectedValue, item.name);
    const context = new FakeContext();
    const layout = drawFinancialSnapshotRow(context, 832, 500, 290, auditRow[0], auditRow[1]);
    assert.ok(layout.label.right + layout.gap <= layout.value.left + 0.001, `${{item.name}} overlaps`);
    assert.equal(context.calls.length, 2, item.name);
    assert.equal(context.calls[0].align, "left", item.name);
    assert.equal(context.calls[1].align, "right", item.name);
    assert.ok(layout.value.fontSize >= 11, item.name);
}}
for (const item of fixtures.stressRows) {{
    const context = new FakeContext();
    const layout = drawFinancialSnapshotRow(context, 832, 500, 290, item.label, item.value);
    assert.ok(layout.label.right + layout.gap <= layout.value.left + 0.001, `stress row overlaps: ${{item.label}}`);
    assert.ok(layout.label.width <= 290, item.label);
    assert.ok(layout.value.width <= 142, item.value);
}}
console.log(`Financial Discord image layout contract passed: ${{fixtures.auditRows.length}} audit states and ${{fixtures.stressRows.length}} stress rows.`);
'''
    with tempfile.TemporaryDirectory(prefix="mcms-financial-image-") as temp:
        harness_path = Path(temp) / "financial-image-layout-contract.js"
        harness_path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(harness_path)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
