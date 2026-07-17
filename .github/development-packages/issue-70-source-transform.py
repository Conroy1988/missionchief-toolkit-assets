#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
TEST = ROOT / ".github" / "scripts" / "test_financial_discord_image_layout_contract.py"

source = SOURCE.read_text(encoding="utf-8")
if source.count("4.14.7") < 2:
    raise RuntimeError("Expected current Toolkit 4.14.7 version markers")
if "function drawFinancialSnapshotRow(" in source:
    raise RuntimeError("Financial snapshot row helpers already exist")

source = source.replace("4.14.7", "4.14.8")
source = source.replace("V4147", "V4148").replace("v4147", "v4148")

helpers = '''    function fitFinancialCanvasText(context, value, maxWidth, { weight = 600, size = 15, minSize = 11 } = {}) {
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

changelog = CHANGELOG.read_text(encoding="utf-8")
marker = "## [Unreleased]\n"
entry = '''## [Unreleased]

## [4.14.8] - 2026-07-17

### Fixed
- Financial Command Discord graphics now reserve independent label and value columns throughout the Operating Snapshot card.
- Checkpoint reconciliation now renders as a compact signed variance, reconciled state, reconstructed basis or unavailable state instead of a long sentence that can collide with the row label.
- Long positive and negative multi-million-credit values are measured, reduced only when required and kept clear of neighbouring text.

### Compatibility
- Financial calculations, ledger reconciliation, Discord payloads, image dimensions, visual styling and all non-image report content remain unchanged.
- Added fixture-backed canvas layout coverage for reconciliation states and deliberately oversized labels and values.
'''
if changelog.count(marker) != 1:
    raise RuntimeError("Unreleased changelog marker was not unique")
CHANGELOG.write_text(changelog.replace(marker, entry, 1), encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
old_help = "Guide for Toolkit v4.14.7"
if help_text.count(old_help) != 1:
    raise RuntimeError(f"Expected one Help Centre version marker, found {help_text.count(old_help)}")
HELP.write_text(help_text.replace(old_help, "Guide for Toolkit v4.14.8", 1), encoding="utf-8")

subprocess.run([sys.executable, str(TEST)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / ".github" / "scripts" / "validate_userscript.py")], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(
    ["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"],
    cwd=ROOT,
    check=True,
)
print("Issue #70 Financial Command image layout fix prepared and validated for Toolkit 4.14.8")
