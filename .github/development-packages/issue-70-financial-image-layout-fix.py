#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "full-userscript-audit.yml"
FIXTURE = ROOT / ".github" / "fixtures" / "financial-discord-image-layout-contract.json"
TEST = ROOT / ".github" / "scripts" / "test_financial_discord_image_layout_contract.py"

source = SOURCE.read_text(encoding="utf-8")
version_count = source.count("4.14.7")
if version_count < 2:
    raise RuntimeError(f"Expected at least two 4.14.7 source markers, found {version_count}")
source = source.replace("4.14.7", "4.14.8")
source = source.replace("V4147", "V4148").replace("v4147", "v4148")

helpers = r'''    function fitFinancialCanvasText(context, value, maxWidth, { weight = 600, size = 15, minSize = 11 } = {}) {
        const sourceText = String(value ?? '');
        const widthLimit = Math.max(1, Number(maxWidth) || 1);
        let fontSize = Math.max(minSize, Number(size) || 15);
        const applyFont = () => {
            context.font = `${weight} ${fontSize}px Arial, sans-serif`;
        };
        applyFont();
        while (fontSize > minSize && context.measureText(sourceText).width > widthLimit) {
            fontSize -= 1;
            applyFont();
        }
        let renderedText = sourceText;
        let measuredWidth = context.measureText(renderedText).width;
        if (measuredWidth > widthLimit) {
            let remaining = sourceText;
            while (remaining.length > 1) {
                remaining = remaining.slice(0, -1);
                const candidate = `${remaining}…`;
                const candidateWidth = context.measureText(candidate).width;
                if (candidateWidth <= widthLimit) {
                    renderedText = candidate;
                    measuredWidth = candidateWidth;
                    break;
                }
            }
            if (measuredWidth > widthLimit) {
                renderedText = '…';
                measuredWidth = context.measureText(renderedText).width;
            }
        }
        return { text: renderedText, width: Math.min(measuredWidth, widthLimit), fontSize };
    }

    function financialSnapshotRows(report) {
        const rawDifference = report?.reconciliationDifference;
        const hasDifference = rawDifference !== null && rawDifference !== undefined && Number.isFinite(Number(rawDifference));
        let auditRow;
        if (hasDifference) {
            const difference = Number(rawDifference);
            auditRow = Math.abs(difference) <= 1
                ? ['Checkpoint audit', 'Reconciled']
                : ['Checkpoint variance', formatSignedCompactCredits(difference)];
        } else {
            auditRow = ['Audit basis', report?.balanceCalculated ? 'Reconstructed' : 'Unavailable'];
        }
        return [
            ['Operating result', formatSignedCompactCredits(report.operatingResult)],
            ['Capital deployed', formatSignedCompactCredits(-Math.abs(report.capitalInvestment || 0))],
            ['Active-hour income', formatSignedCompactCredits(report.activeIncomePerHour || report.incomePerHour)],
            ['Classification', `${Number(report.classificationConfidence || 0).toLocaleString('en-GB', { maximumFractionDigits: 1 })}%`],
            ['Condition score', `${Number(report.scorecard?.overall || 0).toLocaleString('en-GB', { maximumFractionDigits: 0 })}/100`],
            auditRow
        ];
    }

    function drawFinancialSnapshotRow(context, x, y, width, label, value) {
        const gap = 14;
        const valueMaxWidth = Math.min(142, Math.max(96, width * 0.48));
        const valueLayout = fitFinancialCanvasText(context, value, valueMaxWidth, { weight: 800, size: 15, minSize: 11 });
        const valueRight = x + width;
        const valueLeft = valueRight - valueLayout.width;
        const labelMaxWidth = Math.max(56, valueLeft - gap - x);
        const labelLayout = fitFinancialCanvasText(context, label, labelMaxWidth, { weight: 600, size: 15, minSize: 11 });

        context.fillStyle = 'rgba(255,255,255,0.58)';
        context.textAlign = 'left';
        context.font = `600 ${labelLayout.fontSize}px Arial, sans-serif`;
        context.fillText(labelLayout.text, x, y);

        context.fillStyle = '#ffffff';
        context.textAlign = 'right';
        context.font = `800 ${valueLayout.fontSize}px Arial, sans-serif`;
        context.fillText(valueLayout.text, valueRight, y);
        context.textAlign = 'left';

        return {
            gap,
            label: { text: labelLayout.text, left: x, right: x + labelLayout.width, width: labelLayout.width, fontSize: labelLayout.fontSize },
            value: { text: valueLayout.text, left: valueLeft, right: valueRight, width: valueLayout.width, fontSize: valueLayout.fontSize }
        };
    }

'''

canvas_anchor = "            const canvas = document.createElement('canvas');"
canvas_index = source.find(canvas_anchor)
if canvas_index < 0:
    raise RuntimeError("Financial Discord canvas renderer was not found")
renderer_start = source.rfind("\n    async function ", 0, canvas_index)
if renderer_start < 0 or canvas_index - renderer_start > 1200:
    raise RuntimeError("Unable to resolve the Financial Discord renderer declaration")
if "function drawFinancialSnapshotRow(" in source:
    raise RuntimeError("Financial snapshot row helpers already exist")
source = source[:renderer_start + 1] + helpers + source[renderer_start + 1:]

old_rows = '''            const lines = [
                ['Operating result', formatSignedCompactCredits(report.operatingResult)],
                ['Capital deployed', formatSignedCompactCredits(-Math.abs(report.capitalInvestment || 0))],
                ['Active-hour income', formatSignedCompactCredits(report.activeIncomePerHour || report.incomePerHour)],
                ['Classification', `${Number(report.classificationConfidence || 0).toLocaleString('en-GB', { maximumFractionDigits: 1 })}%`],
                ['Condition score', `${Number(report.scorecard?.overall || 0).toLocaleString('en-GB', { maximumFractionDigits: 0 })}/100`],
                ['Audit basis', report.reconciliationLabel]
            ];
            lines.forEach((line, index) => {
                const y = detailY + 65 + index * 29;
                context.fillStyle = 'rgba(255,255,255,0.58)';
                context.font = '600 15px Arial, sans-serif';
                context.fillText(line[0], detailX + 22, y);
                context.fillStyle = '#ffffff';
                context.font = '800 15px Arial, sans-serif';
                context.textAlign = 'right';
                context.fillText(String(line[1]), detailX + detailW - 22, y);
                context.textAlign = 'left';
            });'''
new_rows = '''            const lines = financialSnapshotRows(report);
            lines.forEach((line, index) => {
                const y = detailY + 65 + index * 29;
                drawFinancialSnapshotRow(context, detailX + 22, y, detailW - 44, line[0], line[1]);
            });'''
if source.count(old_rows) != 1:
    raise RuntimeError(f"Expected one Operating Snapshot row block, found {source.count(old_rows)}")
source = source.replace(old_rows, new_rows, 1)
SOURCE.write_text(source, encoding="utf-8")

fixture = {
    "schemaVersion": 1,
    "auditRows": [
        {
            "name": "positive multi-million checkpoint variance",
            "report": {"reconciliationDifference": 987654321, "balanceCalculated": True},
            "expectedLabel": "Checkpoint variance",
            "expectedValue": "+£987.7m"
        },
        {
            "name": "negative multi-million checkpoint variance",
            "report": {"reconciliationDifference": -876543210, "balanceCalculated": True},
            "expectedLabel": "Checkpoint variance",
            "expectedValue": "-£876.5m"
        },
        {
            "name": "checkpoint reconciliation",
            "report": {"reconciliationDifference": 0, "balanceCalculated": True},
            "expectedLabel": "Checkpoint audit",
            "expectedValue": "Reconciled"
        },
        {
            "name": "reconstructed audit basis",
            "report": {"reconciliationDifference": None, "balanceCalculated": True},
            "expectedLabel": "Audit basis",
            "expectedValue": "Reconstructed"
        },
        {
            "name": "unavailable audit basis",
            "report": {"reconciliationDifference": None, "balanceCalculated": False},
            "expectedLabel": "Audit basis",
            "expectedValue": "Unavailable"
        }
    ],
    "stressRows": [
        {"label": "Checkpoint variance", "value": "+£987.7m"},
        {"label": "Checkpoint variance with an intentionally excessive diagnostic suffix", "value": "-£123,456,789,012,345"}
    ]
}
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

TEST.write_text(r'''#!/usr/bin/env python3
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
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Unable to extract {name}")
    return source[start:closing + 1]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(extract_function(source, masked, name) for name in FUNCTION_NAMES)
    fixtures = json.loads(FIXTURE.read_text(encoding="utf-8"))
    harness = f'''"use strict";
const assert = require("node:assert/strict");
const fixtures = {json.dumps(fixtures, ensure_ascii=False)};
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
    constructor() {{ this._font = "600 15px Arial, sans-serif"; this.textAlign = "left"; this.fillStyle = ""; this.calls = []; }}
    set font(value) {{ this._font = String(value); }}
    get font() {{ return this._font; }}
    measureText(value) {{
        const match = this._font.match(/(\\d+(?:\\.\\d+)?)px/);
        const size = match ? Number(match[1]) : 15;
        return {{ width: String(value).length * size * 0.56 }};
    }}
    fillText(text, x, y) {{ this.calls.push({{ text: String(text), x, y, align: this.textAlign, font: this._font }}); }}
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
assert.ok(!source.includes("['Audit basis', report.reconciliationLabel]"), "Legacy unconstrained reconciliation row remains");
console.log(`Financial Discord image layout contract passed: ${{fixtures.auditRows.length}} audit states and ${{fixtures.stressRows.length}} stress rows.`);
'''
    with tempfile.TemporaryDirectory(prefix="mcms-financial-image-") as temp:
        harness_path = Path(temp) / "financial-image-layout-contract.js"
        harness_path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(harness_path)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")

preflight = PREFLIGHT.read_text(encoding="utf-8")
anchor = "  .github/scripts/test_financial_ledger_contract.py\n"
addition = anchor + "  .github/scripts/test_financial_discord_image_layout_contract.py\n"
if preflight.count(anchor) != 1:
    raise RuntimeError("Financial preflight anchor was not unique")
preflight = preflight.replace(anchor, addition, 1)
PREFLIGHT.write_text(preflight, encoding="utf-8")

workflow = WORKFLOW.read_text(encoding="utf-8")
fixture_anchor = '      - ".github/fixtures/financial-ledger-contract.json"\n'
fixture_addition = fixture_anchor + '      - ".github/fixtures/financial-discord-image-layout-contract.json"\n'
script_anchor = '      - ".github/scripts/test_financial_ledger_contract.py"\n'
script_addition = script_anchor + '      - ".github/scripts/test_financial_discord_image_layout_contract.py"\n'
if workflow.count(fixture_anchor) != 1 or workflow.count(script_anchor) != 1:
    raise RuntimeError("Full audit financial path anchors were not unique")
workflow = workflow.replace(fixture_anchor, fixture_addition, 1).replace(script_anchor, script_addition, 1)
WORKFLOW.write_text(workflow, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
marker = "## [Unreleased]\n"
entry = """## [Unreleased]\n\n## [4.14.8] - 2026-07-17\n\n### Fixed\n- Financial Command Discord graphics now reserve independent label and value columns throughout the Operating Snapshot card.\n- Checkpoint reconciliation now renders as a compact signed variance, reconciled state, reconstructed basis or unavailable state instead of a long sentence that can collide with the row label.\n- Long positive and negative multi-million-credit values are measured, reduced only when required and kept clear of neighbouring text.\n\n### Compatibility\n- Financial calculations, ledger reconciliation, Discord payloads, image dimensions, visual styling and all non-image report content remain unchanged.\n- Added fixture-backed canvas layout coverage for reconciliation states and deliberately oversized labels and values.\n"""
if changelog.count(marker) != 1:
    raise RuntimeError("Unreleased changelog marker was not unique")
CHANGELOG.write_text(changelog.replace(marker, entry, 1), encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
if help_text.count("Guide for Toolkit v4.14.7") != 1:
    raise RuntimeError("Help Centre version marker was not unique")
HELP.write_text(help_text.replace("Guide for Toolkit v4.14.7", "Guide for Toolkit v4.14.8", 1), encoding="utf-8")

for diagnostic in [
    ROOT / ".github" / "audits" / "issue-70-financial-renderer-context.md",
    ROOT / ".github" / "audits" / "issue-70-financial-reconciliation-context.md",
]:
    if diagnostic.exists():
        diagnostic.unlink()

subprocess.run([sys.executable, str(TEST)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / ".github" / "scripts" / "validate_userscript.py")], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Issue #70 Financial Command image layout fix prepared and validated for Toolkit 4.14.8")
