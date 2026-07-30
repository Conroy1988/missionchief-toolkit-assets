#!/usr/bin/env python3
"""Fixture-backed runtime contract for Finance → Discord report complexity."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "financial-discord-complexity-contract.json"
FUNCTION_NAMES = [
    "normaliseLoadedDiscordReportComplexity",
    "normaliseDiscordReportComplexity",
    "escapeDiscordMarkdown",
    "truncateDiscord",
    "buildDiscordCategoryBreakdown",
    "buildDiscordTopPayouts",
    "buildDiscordComparisonField",
    "buildDiscordScorecardField",
    "buildDiscordRiskField",
    "buildDiscordForecastField",
    "buildDiscordDataQualityField",
    "discordEmbedCharacterCount",
    "fitDiscordEmbedsToBudget",
    "financialResultHeadline",
    "buildDiscordBalanceField",
    "buildDiscordDataCheckField",
    "buildDiscordActivityField",
    "buildDiscordFinancialPayload",
]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\bfunction\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    parameter_open = masked.find("(", start)
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
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(extract_function(source, masked, name) for name in FUNCTION_NAMES)
    fixtures = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_json = json.dumps(fixtures, ensure_ascii=False)
    harness = f'''"use strict";
const assert = require("node:assert/strict");
const fixtures = {fixture_json};
const FINANCE_REPORT_COMPLEXITIES = Object.freeze(["simple", "informative", "wolf"]);
const DISCORD_MAX_FIELD_LENGTH = 1024;
const FINANCE_CHART_FILENAME = "missionchief-financial-report.png";
const SCRIPT = {{ name: "MissionChief Map Command Toolkit", version: "8.4.0" }};
let activeFinancialRuleVersion = "fixture-rules";
let activeFinancialPolicyVersion = "fixture-policy";
let state = {{
    discordReport: {{
        complexity: "informative",
        topCategories: 5,
        webhookName: "MissionChief Finance"
    }}
}};
function formatSignedCredits(value) {{
    const amount = Math.round(Number(value) || 0);
    const sign = amount > 0 ? "+" : amount < 0 ? "-" : "";
    return `${{sign}}${{Math.abs(amount).toLocaleString("en-GB")}} Credits`;
}}
function formatPlainCredits(value) {{
    return `${{Math.max(0, Math.round(Number(value) || 0)).toLocaleString("en-GB")}} Credits`;
}}
function formatPercentageChange(value) {{
    if (!Number.isFinite(Number(value))) return "N/A";
    const rounded = Math.round(Number(value) * 10) / 10;
    return `${{rounded > 0 ? "+" : ""}}${{rounded.toLocaleString("en-GB")}}%`;
}}
function reportTone(value) {{
    return value > 0 ? "positive" : value < 0 ? "negative" : "neutral";
}}
{functions}
function report(complexity, net = 460000) {{
    return {{
        complexity,
        generatedAt: Date.parse("2026-07-30T12:00:00Z"),
        period: {{
            id: "last7",
            label: "Last 7 Days",
            rangeLabel: "23 Jul 2026 → 30 Jul 2026",
            note: ""
        }},
        userName: "Fixture Commander",
        userId: "42",
        income: 2400000,
        spending: 1940000,
        net,
        operatingExpense: 340000,
        capitalInvestment: 1600000,
        operatingResult: 2060000,
        operatingMarginPercent: 85.8,
        openingBalance: 10000000,
        closingBalance: 10000000 + net,
        missionCount: 84,
        activityCount: 101,
        averageMissionReward: 28000,
        medianMissionReward: 26500,
        activeHours: 12.5,
        activeIncomePerHour: 192000,
        incomePerHour: 14285,
        allianceIncomePercent: 64.2,
        personalIncomePercent: 31.4,
        incomeCategories: [
            {{ label: "Alliance Missions", total: 1540000, count: 50 }},
            {{ label: "Personal Missions", total: 754000, count: 28 }}
        ],
        spendingCategories: [
            {{ label: "Buildings & Stations", total: 1200000, count: 3 }},
            {{ label: "Vehicle Purchases", total: 400000, count: 8 }}
        ],
        operatingExpenseCategories: [
            {{ label: "Training & Education", total: 200000, count: 12 }}
        ],
        capitalCategories: [
            {{ label: "Buildings & Stations", total: 1200000, count: 3 }}
        ],
        topPayouts: [
            {{ description: "Major alliance incident", amount: 98000 }}
        ],
        comparison: {{
            incomeChange: 12.5,
            operatingResultChange: 9.1,
            capitalInvestmentChange: -5,
            activeVelocityChange: 4.5,
            missionChange: 7,
            averageRewardChange: 2.2
        }},
        previous: {{}},
        scorecard: {{
            grade: "A",
            overall: 86,
            label: "Strong command",
            revenue: 88,
            efficiency: 92,
            liquidity: 80,
            growth: 76,
            confidence: 94,
            runwayDays: 120
        }},
        riskAlerts: [
            {{ severity: "medium", title: "Expansion pace", detail: "Investment was high but affordable." }},
            {{ severity: "good", title: "No operating pressure", detail: "Operating activity remained positive." }}
        ],
        forecast: {{
            endOfDayIncome: null,
            sevenDayIncome: 2400000,
            thirtyDayIncome: 10285714,
            recoveryDays: 5.4,
            projectedSevenDayBalance: 12520000,
            confidence: "HIGH",
            basisDays: 7
        }},
        drawdown: {{
            peakBalance: 10800000,
            largestDrawdown: 600000,
            largestDrawdownPercent: 5.6
        }},
        ledgerComplete: true,
        aggregateReconciled: true,
        archiveComplete: true,
        archiveTruncated: false,
        ledgerSource: "MissionChief ledger + local archive",
        vaultTransactionCount: 5000,
        ledgerPages: 20,
        ledgerLastPage: 20,
        classificationConfidence: 98.5,
        unclassifiedCount: 0,
        unclassifiedAmount: 0,
        overviewLabel: "Reconciled",
        overviewRowsUsed: 7,
        overviewIncomeVariance: 0,
        overviewSpendingVariance: 0,
        overviewNetVariance: 0,
        reconciliationLabel: "Reconciled",
        ledgerStable: true,
        ledgerScanRetries: 0,
        invalidTimestampCount: 0,
        overviewMalformedRows: 0,
        overviewDuplicateDates: 0,
        ledgerScanLimitReached: false,
        ledgerScanCancelled: false,
        overviewStatus: "reconciled"
    }};
}}
for (const item of fixtures.migration) {{
    assert.equal(normaliseLoadedDiscordReportComplexity(item.input), item.expected, item.name);
}}
assert.equal(normaliseDiscordReportComplexity("simple"), "simple");
assert.equal(normaliseDiscordReportComplexity("invalid"), "informative");
for (const item of fixtures.reports) {{
    state.discordReport.complexity = item.complexity;
    const payload = buildDiscordFinancialPayload(report(item.complexity), {{ withAttachment: true }});
    assert.equal(payload.embeds.length, item.embedCount, item.complexity);
    assert.ok(payload.embeds[0].title.includes(item.titleIncludes), item.complexity);
    assert.deepEqual(payload.allowed_mentions, {{ parse: [] }}, item.complexity);
    assert.equal(payload.attachments.length, 1, item.complexity);
    assert.equal(payload.embeds[0].image.url, `attachment://${{FINANCE_CHART_FILENAME}}`, item.complexity);
    assert.ok(payload.embeds[0].description.includes("ahead"), item.complexity);
    const fields = payload.embeds.flatMap(embed => embed.fields || []);
    const names = fields.map(field => field.name);
    for (const required of item.requiredFields) assert.ok(names.includes(required), `${{item.complexity}} missing ${{required}}`);
    for (const forbidden of item.forbiddenFields) assert.ok(!names.includes(forbidden), `${{item.complexity}} exposed ${{forbidden}}`);
    for (const field of fields) {{
        assert.ok(field.name.length <= 256, `${{item.complexity}} field name limit`);
        assert.ok(field.value.length <= 1024, `${{item.complexity}} field value limit`);
    }}
    const totalCharacters = payload.embeds.reduce((sum, embed) => sum + discordEmbedCharacterCount(embed), 0);
    assert.ok(totalCharacters <= 5900, `${{item.complexity}} embed budget`);
    assert.ok(!JSON.stringify(payload).includes("/api/webhooks/"), `${{item.complexity}} webhook leaked`);
    assert.equal(payload.embeds[0].color, fixtures.colours.positive, item.complexity);
}}
for (const [tone, net] of [["negative", -1], ["neutral", 0]]) {{
    const payload = buildDiscordFinancialPayload(report("simple", net));
    assert.equal(payload.embeds[0].color, fixtures.colours[tone], tone);
}}
console.log(`Financial Discord complexity contract passed: ${{fixtures.migration.length}} migrations and ${{fixtures.reports.length}} report levels.`);
'''
    with tempfile.TemporaryDirectory(prefix="mcms-financial-discord-") as temp:
        harness_path = Path(temp) / "financial-discord-complexity-contract.js"
        harness_path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(harness_path)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
