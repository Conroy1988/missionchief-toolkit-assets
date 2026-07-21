#!/usr/bin/env python3
"""Exercise the canonical Financial Advisor credits-overview implementation."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURES = ROOT / ".github" / "fixtures" / "financial-overview-contract.json"

FUNCTION_NAMES = [
    "financeNormaliseText",
    "parseCreditInteger",
    "localIsoDate",
    "localDayStart",
    "addLocalDays",
    "formatSignedCredits",
    "standardDeviation",
    "normaliseFinancialOverviewHeader",
    "parseFinancialOverviewDate",
    "financialPaginationLastPage",
    "parseCreditOverviewDocument",
    "financialOverviewCacheCovers",
    "fetchCreditOverview",
    "financialOverviewDayIsAuthoritative",
    "reconcileFinancialOverview",
]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    match = matches[0]
    open_pos = masked.find("{", match.start())
    close_pos = audit.matching_brace(masked, open_pos)
    if close_pos is None:
        raise AssertionError(f"Closing brace not found for {name}")
    return source[match.start():close_pos + 1]


def build_harness(source: str, fixtures: dict) -> str:
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(extract_function(source, masked, name) for name in FUNCTION_NAMES)
    fixture_json = json.dumps(fixtures, ensure_ascii=False)
    return f'''"use strict";
const assert = require("node:assert/strict");
const fixtures = {fixture_json};

let document = {{ baseURI: "https://www.missionchief.co.uk/credits/overview" }};
let pageWindow = {{ location: {{ href: "https://www.missionchief.co.uk/credits/overview", origin: "https://www.missionchief.co.uk" }} }};
let FINANCE_OVERVIEW_CACHE_TTL_MS = 5 * 60 * 1000;
let FINANCE_OVERVIEW_MAX_PAGES = 500;
let FINANCE_FETCH_YIELD_EVERY = 5;
let financialOverviewCache = {{ fetchedAt: 0, rows: [], pageCount: 0, lastPage: 0, coverageStartMs: null, coverageEndMs: null, complete: false, malformedRowCount: 0, duplicateDateCount: 0 }};
let fetchCreditOverviewPage;
let runtimeDelay = async () => true;

{functions}

function cell(text) {{ return {{ textContent: String(text) }}; }}
function fakeDocument(fixture) {{
    const table = {{
        querySelectorAll(selector) {{
            if (selector === "thead th" || selector === "tr th") return fixture.headers.map(cell);
            if (selector === "tbody tr") return fixture.rows.map(values => ({{ children: values.map(cell) }}));
            return [];
        }}
    }};
    const pagination = fixture.pagination.map(item => ({{
        textContent: item.text,
        querySelector(selector) {{
            if (selector !== "a[href]" || !item.href) return null;
            return {{ getAttribute(name) {{ return name === "href" ? item.href : null; }} }};
        }}
    }}));
    return {{
        querySelectorAll(selector) {{
            if (selector === "table") return [table];
            if (selector === ".pagination li") return pagination;
            return [];
        }}
    }};
}}
function overviewRow(raw) {{
    const start = Date.parse(raw.dayStart);
    return {{ ...raw, dayStartMs: start, dayEndMs: addLocalDays(start, 1), calculatedNet: raw.revenue + raw.spending, netMismatch: false, page: 1, row: 0 }};
}}
function summaryFixture(raw) {{
    return {{
        transactions: [], incomeCategories: [], spendingCategories: [], operatingExpenseCategories: [], capitalCategories: [],
        operatingIncome: raw.income, otherIncome: 0, operatingExpense: raw.operatingExpense, capitalInvestment: raw.capitalInvestment,
        incomeCount: 2, spendingCount: 1, activityCount: 3, missionCount: 2, missionIncome: raw.income,
        averageIncome: 650, averageSpend: 200, averageMissionReward: 650, medianMissionReward: 650,
        largestReward: 800, smallestReward: 500, largestSpend: 200, allianceIncome: raw.allianceIncome,
        personalIncome: raw.personalIncome, transportIncome: 0, allianceIncomePercent: 0, personalIncomePercent: 0,
        incomePerHour: 27, activeIncomePerHour: 433, activeHours: raw.activeHours, calendarHours: raw.calendarHours,
        calendarDays: 2, classificationConfidence: 100, unclassifiedAmount: 0, unclassifiedCount: 0,
        unclassifiedEntries: [], operatingMarginPercent: 0, capitalInvestmentRatioPercent: 0,
        incomeConcentrationPercent: 0, incomeVolatilityPercent: 0, topIncomeCategory: raw.topIncomeCategory,
        topPayouts: [], ...raw,
        buckets: raw.buckets.map(bucket => ({{ ...bucket, start: Date.parse(bucket.start), end: Date.parse(bucket.end) }}))
    }};
}}

async function testParser() {{
    const fixture = fixtures.parser;
    const parsed = parseCreditOverviewDocument(fakeDocument(fixture), fixture.pageNumber);
    assert.equal(parsed.rows.length, fixture.expected.rowCount);
    assert.equal(parsed.malformedRowCount, fixture.expected.malformedRowCount);
    assert.equal(parsed.duplicateDateCount, fixture.expected.duplicateDateCount);
    assert.equal(parsed.lastPage, fixture.expected.lastPage);
    assert.equal(parsed.rows[0].dateKey, fixture.expected.firstDate);
    assert.equal(parsed.rows.find(row => row.dateKey === "2026-07-12").net, fixture.expected.netNegative);
    assert.equal(parsed.rows.find(row => row.dateKey === "2026-07-16").spending, fixture.expected.positiveSpendingNormalised);
    assert.equal(parseFinancialOverviewDate("31/02/2026"), null);
    assert.equal(parseCreditInteger("-3,667,080"), -3667080);
}}

async function testPaginationAndCache() {{
    const fixture = fixtures.pagination;
    const pages = new Map(Object.entries(fixture.pages).map(([key, value]) => [Number(key), {{
        ...value,
        malformedRowCount: 0,
        duplicateDateCount: 0,
        rows: value.rows.map(overviewRow)
    }}]));
    const calls = [];
    fetchCreditOverviewPage = async page => {{ calls.push(page); return pages.get(page); }};
    financialOverviewCache = {{ fetchedAt: 0, rows: [], pageCount: 0, lastPage: 0, coverageStartMs: null, coverageEndMs: null, complete: false, malformedRowCount: 0, duplicateDateCount: 0 }};
    const start = Date.parse(fixture.requiredStart);
    const end = Date.parse(fixture.requiredEnd);
    const first = await fetchCreditOverview(start, end);
    assert.deepEqual(calls, fixture.expectedCalls);
    assert.equal(first.available, true);
    assert.equal(first.coverageReached, true);
    assert.equal(first.rows.length, 4);
    const second = await fetchCreditOverview(start, end);
    assert.equal(second.fromCache, true);
    assert.deepEqual(calls, fixture.expectedCalls);

    financialOverviewCache = {{ fetchedAt: 0, rows: [], pageCount: 0, lastPage: 0, coverageStartMs: null, coverageEndMs: null, complete: false, malformedRowCount: 0, duplicateDateCount: 0 }};
    fetchCreditOverviewPage = async () => {{ throw new Error("fixture unavailable"); }};
    const missing = await fetchCreditOverview(start, end, {{ force: true }});
    assert.equal(missing.available, false);
    assert.match(missing.error, /fixture unavailable/);
}}

async function testReconciliation() {{
    const fixture = fixtures.reconciliation;
    const period = {{ startMs: Date.parse(fixture.periodStart), endMs: Date.parse(fixture.periodEnd), durationMs: Date.parse(fixture.periodEnd) - Date.parse(fixture.periodStart) }};
    const transactions = fixture.ledger.map(entry => ({{ ...entry, timestamp: Date.parse(entry.timestamp) }}));
    const overview = {{ available: true, rows: fixture.overviewRows.map(overviewRow), pageCount: 1, lastPage: 1, coverageReached: true, malformedRowCount: 0, duplicateDateCount: 0, error: "" }};
    const result = reconcileFinancialOverview(summaryFixture(fixture.summary), transactions, period, overview);
    assert.equal(result.income, fixture.expected.income);
    assert.equal(result.spending, fixture.expected.spending);
    assert.equal(result.net, fixture.expected.net);
    assert.equal(result.overviewAudit.netVariance, fixture.expected.netVariance);
    assert.equal(result.overviewAudit.status, fixture.expected.status);
    assert.equal(result.incomeCategories.length, 0, "overview variance must not invent categories");
    assert.equal(reconcileFinancialOverview(result, transactions, period, overview), result, "reconciliation must be idempotent");

    const exactOverview = {{ ...overview, rows: [
        overviewRow({{ dateKey: "2026-07-18", dayStart: "2026-07-18T00:00:00Z", revenue: 800, spending: 0, net: 800 }}),
        overviewRow({{ dateKey: "2026-07-17", dayStart: "2026-07-17T00:00:00Z", revenue: 500, spending: -200, net: 300 }})
    ] }};
    const exact = reconcileFinancialOverview(summaryFixture(fixture.summary), transactions, period, exactOverview);
    assert.equal(exact.overviewAudit.status, "reconciled");
    assert.equal(exact.overviewAudit.unresolvedVariance, 0);
    assert.equal(exact.net, fixture.summary.net);

    const partialPeriod = {{ ...period, startMs: Date.parse("2026-07-17T12:00:00Z") }};
    const partial = reconcileFinancialOverview(summaryFixture(fixture.summary), transactions, partialPeriod, overview);
    assert.equal(partial.overviewAudit.rowsUsed, 1);
    assert.equal(partial.overviewAudit.days[0].dateKey, "2026-07-18");
}}

(async () => {{
    await testParser();
    await testPaginationAndCache();
    await testReconciliation();
    console.log("Financial overview contract fixtures passed.");
}})().catch(error => {{ console.error(error); process.exit(1); }});
'''



def assert_static_contract(source: str) -> None:
    required = [
        "const overview = await fetchCreditOverview(",
        "const current = reconcileFinancialOverview(currentLedgerSummary",
        "const previous = previousLedgerSummary ? reconcileFinancialOverview",
        "overviewIncomeVariance: overviewAudit.incomeVariance",
        "overviewSpendingVariance: overviewAudit.spendingVariance",
        "overviewNetVariance: overviewAudit.netVariance",
        "Daily aggregate audit:",
        "Overview vs ledger: income",
        "drawFinancialMetricCard(context, 412, 148, 337, 98, 'Net movement', formatSignedCompactCredits(report.net)",
        "report.overviewRowsUsed ? `${report.overviewRowsUsed.toLocaleString('en-GB')} overview day",
    ]
    missing = [snippet for snippet in required if snippet not in source]
    if missing:
        raise AssertionError("Missing Financial Advisor integration contract(s): " + ", ".join(missing))


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert_static_contract(source)
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    harness = build_harness(source, fixtures)
    with tempfile.TemporaryDirectory(prefix="financial-overview-") as temp_dir:
        path = Path(temp_dir) / "harness.js"
        path.write_text(harness, encoding="utf-8")
        completed = subprocess.run(["node", str(path)], cwd=ROOT, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
