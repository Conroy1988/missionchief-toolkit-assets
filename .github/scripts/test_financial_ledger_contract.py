#!/usr/bin/env python3
"""Execute fixture-backed contracts against the real financial-ledger functions.

The test does not import or rewrite production logic. It extracts the named
function declarations from the canonical userscript, evaluates those exact
functions in a controlled Node.js harness and supplies deterministic browser,
network, vault and clock fixtures.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURES = ROOT / ".github" / "fixtures" / "financial-ledger-contract.json"

FUNCTION_NAMES = [
    "financeNormaliseText",
    "parseCreditInteger",
    "parseCreditTimestamp",
    "parseCreditsListDocument",
    "financialLedgerAnchor",
    "normaliseFinancialLedgerEntry",
    "fetchCreditLedgerPage",
    "fetchFinancialLedger",
    "buildFinancialBuckets",
    "calculateActiveHours",
    "medianNumber",
    "standardDeviation",
    "summariseFinancialTransactions",
]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    match = matches[0]
    open_pos = masked.find("{", match.start())
    if open_pos < 0:
        raise AssertionError(f"Opening brace not found for {name}")
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

let document = {{ baseURI: "https://www.missionchief.co.uk/credits" }};
let pageWindow = {{ location: {{ href: "https://www.missionchief.co.uk/credits", origin: "https://www.missionchief.co.uk" }} }};
let activeFinancialPolicy = {{ scan: {{ retryAttempts: 3, pageCap: 5000, batchSize: 3, checkpointPages: 100 }} }};
let state = {{ financialVault: {{ enabled: false }} }};
let financeArchiveScanCancelled = false;
let FINANCE_MAX_LEDGER_PAGES = 5000;
let FINANCE_INCREMENTAL_MAX_PAGES = 60;
let FINANCE_DEEP_SCAN_HARD_PAGE_CAP = 5000;
let FINANCE_DEEP_SCAN_HARD_BATCH_CAP = 4;
let FINANCE_SCAN_CHECKPOINT_PAGES = 100;
let FINANCE_FETCH_YIELD_EVERY = 5;

let fetchSameOriginDocument;
let runtimeDelay;
let setDiscordStatus;
let setFinanceVaultStatus;
let renderFinanceVaultStatus;
let fetchCreditAccount;
let financePlayerIdentity;
let ensureFinanceVaultCredential;
let loadFinanceVault;
let financeVaultStats;
let mergeFinanceVaultEntries;
let decorateFinancialEntries;
let classifyFinancialTransaction;

{functions}

function clone(value) {{ return JSON.parse(JSON.stringify(value)); }}
function toTimestamp(value) {{
    if (value === "invalid") return Number.NaN;
    if (typeof value === "number") return value;
    return Date.parse(value);
}}
function hydrateEntry(raw) {{
    return {{
        ...clone(raw),
        timestamp: toTimestamp(raw.timestamp),
        page: Number(raw.page) || 1,
        row: Number(raw.row) || 0,
        rawTimestamp: String(raw.rawTimestamp || ""),
        dateLabel: String(raw.dateLabel || "")
    }};
}}
function hydratePage(raw) {{
    return {{
        lastPage: Math.max(1, Number(raw.lastPage) || 1),
        invalidTimestampCount: Math.max(0, Number(raw.invalidTimestampCount) || 0),
        entries: (raw.entries || []).map(hydrateEntry)
    }};
}}
function sourceKey(entry) {{
    const description = financeNormaliseText(entry.description);
    const dateLabel = financeNormaliseText(entry.dateLabel);
    const rawTimestamp = financeNormaliseText(entry.rawTimestamp);
    return `${{entry.timestamp}}|${{Math.round(Number(entry.amount) || 0)}}|${{description.toLowerCase()}}|${{rawTimestamp || dateLabel}}`;
}}
function fakeCell(text, rawTimestamp = "") {{
    return {{
        textContent: text,
        getAttribute(name) {{ return name === "data-logged-at" ? rawTimestamp : null; }}
    }};
}}
function fakeDocument(parserFixture) {{
    const rows = parserFixture.rows.map(row => ({{
        children: [
            fakeCell(row.amount),
            fakeCell(row.description),
            fakeCell(row.dateLabel, row.rawTimestamp)
        ]
    }}));
    const pagination = parserFixture.pagination.map(item => ({{
        textContent: item.text,
        querySelector(selector) {{
            if (selector !== "a[href]" || !item.href) return null;
            return {{ getAttribute(name) {{ return name === "href" ? item.href : null; }} }};
        }}
    }}));
    return {{
        querySelectorAll(selector) {{
            if (selector === "table tbody tr") return rows;
            if (selector === ".pagination li") return pagination;
            return [];
        }}
    }};
}}

async function testParserContract() {{
    const fixture = fixtures.parser;
    const result = parseCreditsListDocument(fakeDocument(fixture), fixture.pageNumber);
    assert.equal(result.entries.length, fixture.expected.entryCount);
    assert.equal(result.invalidTimestampCount, fixture.expected.invalidTimestampCount);
    assert.equal(result.lastPage, fixture.expected.lastPage);
    assert.deepEqual(result.entries.map(entry => entry.amount), fixture.expected.amounts);
    assert.equal(result.entries[0].description, "[Alliance] Warehouse fire");
    assert.equal(result.entries[0].page, fixture.pageNumber);
    assert.equal(result.entries[1].timestamp, new Date(2026, 6, 15, 8, 0, 0, 0).getTime());
    assert.equal(Number.isFinite(result.entries[2].timestamp), false);

    assert.equal(parseCreditInteger("1,234 Credits"), 1234);
    assert.equal(parseCreditInteger("-1.234"), -1234);
    assert.equal(parseCreditInteger("(550)"), -550);
    assert.equal(parseCreditInteger("no amount"), 0);
    assert.equal(parseCreditTimestamp("1784201640"), 1784201640000);
    assert.equal(parseCreditTimestamp("1784201640000"), 1784201640000);

    const normalised = normaliseFinancialLedgerEntry({{
        timestamp: 1784201640000,
        amount: 1250,
        description: "  [Alliance]   Warehouse fire  ",
        dateLabel: " 16/07/2026   12:34 ",
        rawTimestamp: " 1784201640000 ",
        page: 3,
        row: 0
    }});
    assert.deepEqual(normalised, {{
        timestamp: 1784201640000,
        amount: 1250,
        description: "[Alliance] Warehouse fire",
        dateLabel: "16/07/2026 12:34",
        rawTimestamp: "1784201640000",
        page: 3,
        row: 0,
        sourceKey: "1784201640000|1250|[alliance] warehouse fire|1784201640000"
    }});
    assert.equal(normaliseFinancialLedgerEntry({{ timestamp: Number.NaN, amount: 100 }}), null);
}}

async function testRetryContract() {{
    const fixture = fixtures.retry;
    let attempts = 0;
    const delays = [];
    const statuses = [];
    const paths = [];
    const retryDocument = fakeDocument(fixtures.parser);
    fetchSameOriginDocument = async path => {{
        attempts += 1;
        paths.push(path);
        if (attempts <= fixture.failuresBeforeSuccess) throw new Error(`fixture failure ${{attempts}}`);
        return {{ doc: retryDocument, url: `https://www.missionchief.co.uk${{path}}` }};
    }};
    runtimeDelay = async delay => {{ delays.push(delay); return true; }};
    setDiscordStatus = message => statuses.push(message);
    activeFinancialPolicy = {{ scan: {{ retryAttempts: fixture.expectedAttempts }} }};
    const random = Math.random;
    Math.random = () => 0;
    try {{
        const result = await fetchCreditLedgerPage(fixture.page);
        assert.equal(attempts, fixture.expectedAttempts);
        assert.equal(delays.length, fixture.expectedDelays);
        assert.deepEqual(paths, Array(fixture.expectedAttempts).fill(fixture.expectedPath));
        assert.equal(result.entries.length, fixtures.parser.expected.entryCount);
        assert.equal(statuses.length, fixture.expectedDelays);
    }} finally {{
        Math.random = random;
    }}
}}

function emptyVault(raw = {{}}) {{
    return {{
        coverageStartMs: raw.coverageStartMs == null ? null : toTimestamp(raw.coverageStartMs),
        coverageEndMs: raw.coverageEndMs == null ? null : toTimestamp(raw.coverageEndMs),
        archiveComplete: Boolean(raw.archiveComplete),
        archiveTruncated: Boolean(raw.archiveTruncated),
        droppedTransactions: Number(raw.droppedTransactions) || 0,
        transactions: (raw.transactions || []).map(hydrateEntry),
        balanceCheckpoints: clone(raw.balanceCheckpoints || []),
        deepScanInProgress: Boolean(raw.deepScanInProgress),
        deepScanAnchor: String(raw.deepScanAnchor || ""),
        deepScanTotalPages: Number(raw.deepScanTotalPages) || 0,
        deepScanCursorPage: Number(raw.deepScanCursorPage) || 0,
        sourceLastPage: Number(raw.sourceLastPage) || 0,
        syncRevision: Number(raw.syncRevision) || 0
    }};
}}

async function runLedgerScenario(scenario) {{
    state = clone(scenario.state);
    financeArchiveScanCancelled = false;
    FINANCE_MAX_LEDGER_PAGES = 5000;
    FINANCE_INCREMENTAL_MAX_PAGES = Number(scenario.incrementalPageCap) || 60;
    FINANCE_DEEP_SCAN_HARD_PAGE_CAP = 5000;
    FINANCE_DEEP_SCAN_HARD_BATCH_CAP = 4;
    FINANCE_SCAN_CHECKPOINT_PAGES = 100;
    FINANCE_FETCH_YIELD_EVERY = 5;
    activeFinancialPolicy = {{ scan: {{ retryAttempts: 3, pageCap: 5000, batchSize: 3, checkpointPages: 100 }} }};

    const pages = new Map();
    for (const [page, raw] of Object.entries(scenario.pages)) {{
        const responses = Array.isArray(raw) ? raw : [raw];
        pages.set(Number(page), responses.map(hydratePage));
    }}
    const responseIndexes = new Map();
    const pageCalls = [];
    const delays = [];
    const statuses = [];
    let activeFetches = 0;
    let maxConcurrency = 0;
    fetchCreditLedgerPage = async page => {{
        activeFetches += 1;
        maxConcurrency = Math.max(maxConcurrency, activeFetches);
        pageCalls.push(page);
        await Promise.resolve();
        const responses = pages.get(Number(page));
        if (!responses || !responses.length) throw new Error(`No fixture for ledger page ${{page}} in ${{scenario.name}}`);
        const index = responseIndexes.get(Number(page)) || 0;
        responseIndexes.set(Number(page), index + 1);
        const response = responses[Math.min(index, responses.length - 1)];
        activeFetches -= 1;
        return clone(response);
    }};
    runtimeDelay = async delay => {{ delays.push(delay); return true; }};
    setDiscordStatus = message => statuses.push(String(message));
    setFinanceVaultStatus = message => statuses.push(String(message));
    renderFinanceVaultStatus = () => undefined;
    fetchCreditAccount = async () => ({{ currentBalance: 1000000, userName: "Fixture User", userId: 42 }});
    financePlayerIdentity = account => ({{ id: String(account.userId), name: account.userName }});
    ensureFinanceVaultCredential = () => ({{ deviceId: "fixture-device" }});

    let vault = emptyVault(scenario.vault || {{}});
    if (scenario.vaultKnownFromPage1) {{
        const first = pages.get(1)[0].entries;
        vault.transactions = first.map((entry, index) => ({{
            ...entry,
            sourceKey: sourceKey(entry),
            occurrence: 1,
            fingerprint: `known-${{index}}`
        }})).sort((a, b) => a.timestamp - b.timestamp);
    }}
    loadFinanceVault = () => vault;
    financeVaultStats = candidate => {{
        const transactions = Array.isArray(candidate?.transactions) ? candidate.transactions : [];
        return {{
            count: transactions.length,
            firstTimestamp: transactions.length ? transactions[0].timestamp : null,
            lastTimestamp: transactions.length ? transactions[transactions.length - 1].timestamp : null
        }};
    }};
    decorateFinancialEntries = entries => entries.slice().filter(entry => Number.isFinite(entry.timestamp)).sort((a, b) => a.timestamp - b.timestamp || a.page - b.page || a.row - b.row);
    mergeFinanceVaultEntries = (candidate, entries, options = {{}}) => {{
        const merged = new Map();
        for (const entry of candidate.transactions || []) merged.set(`${{entry.sourceKey}}|${{entry.occurrence || 1}}`, entry);
        for (const entry of decorateFinancialEntries(entries)) merged.set(`${{entry.sourceKey}}|${{entry.occurrence || 1}}`, entry);
        candidate.transactions = Array.from(merged.values()).sort((a, b) => a.timestamp - b.timestamp);
        if (Number.isFinite(Number(options.coverageStartMs))) candidate.coverageStartMs = candidate.coverageStartMs == null ? Number(options.coverageStartMs) : Math.min(candidate.coverageStartMs, Number(options.coverageStartMs));
        if (Number.isFinite(Number(options.coverageEndMs))) candidate.coverageEndMs = candidate.coverageEndMs == null ? Number(options.coverageEndMs) : Math.max(candidate.coverageEndMs, Number(options.coverageEndMs));
        if (options.archiveComplete !== null && options.archiveComplete !== undefined) candidate.archiveComplete = Boolean(options.archiveComplete) && !candidate.archiveTruncated;
        candidate.sourceLastPage = Math.max(candidate.sourceLastPage || 0, Number(options.sourceLastPage) || 0);
        candidate.syncRevision = (candidate.syncRevision || 0) + 1;
        vault = candidate;
        return candidate;
    }};

    const result = await fetchFinancialLedger(toTimestamp(scenario.requiredStart), 0, false, false);
    const expected = scenario.expected;
    assert.deepEqual(pageCalls, expected.pageCalls, scenario.name);
    assert.equal(maxConcurrency, expected.maxConcurrency, `${{scenario.name}} concurrency`);
    for (const key of ["pageCount", "lastPage", "entryCount", "invalidTimestampCount", "coverageReached", "ledgerStable", "scanRetries", "complete"]) {{
        if (!(key in expected)) continue;
        const actual = key === "entryCount" ? result.entries.length : result[key];
        assert.equal(actual, expected[key], `${{scenario.name}} ${{key}}`);
    }}
    if (expected.duplicateOccurrences) {{
        const duplicates = result.entries.filter(entry => entry.amount === 100 && entry.description === "[Alliance] Warehouse fire");
        assert.deepEqual(duplicates.map(entry => entry.occurrence), expected.duplicateOccurrences, scenario.name);
    }}
    if (expected.restartDelay) assert.equal(delays.includes(expected.restartDelay), true, scenario.name);
    if (expected.ledgerSourceIncludes) assert.equal(result.ledgerSource.toLowerCase().includes(expected.ledgerSourceIncludes), true, scenario.name);
    return {{ result, pageCalls, delays, statuses, maxConcurrency }};
}}

async function testLedgerScenarios() {{
    for (const scenario of fixtures.ledgerScenarios) await runLedgerScenario(scenario);
}}

async function testSummaryContract() {{
    const fixture = fixtures.summary;
    classifyFinancialTransaction = transaction => clone(transaction.classification);
    const period = {{
        startMs: toTimestamp(fixture.period.start),
        endMs: toTimestamp(fixture.period.end),
        durationMs: toTimestamp(fixture.period.end) - toTimestamp(fixture.period.start)
    }};
    const transactions = fixture.transactions.map(hydrateEntry);
    const summary = summariseFinancialTransactions(transactions, period);
    for (const [key, expected] of Object.entries(fixture.expected)) assert.equal(summary[key], expected, `summary ${{key}}`);
    for (const key of fixture.discordRequiredKeys) assert.equal(Object.hasOwn(summary, key), true, `Discord summary input ${{key}}`);
    assert.equal(summary.incomeCategories[0].key, "alliance");
    assert.equal(summary.operatingExpenseCategories[0].key, "training");
    assert.equal(summary.capitalCategories[0].key, "vehicles");
    assert.deepEqual(summary.topPayouts.map(entry => entry.amount), [1000, 250]);
    assert.equal(summary.buckets.reduce((sum, bucket) => sum + bucket.net, 0), summary.net);
}}

(async () => {{
    await testParserContract();
    await testRetryContract();
    await testLedgerScenarios();
    await testSummaryContract();
    console.log(`Financial ledger contract passed: parser, retry, ${{fixtures.ledgerScenarios.length}} scan scenarios and summary/Discord inputs.`);
}})().catch(error => {{
    console.error(error?.stack || error);
    process.exitCode = 1;
}});
'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    harness = build_harness(source, fixtures)
    with tempfile.TemporaryDirectory(prefix="missionchief-ledger-contract-") as temporary:
        harness_path = Path(temporary) / "financial-ledger-contract.cjs"
        harness_path.write_text(harness, encoding="utf-8")
        completed = subprocess.run(
            ["node", str(harness_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env={**__import__("os").environ, "TZ": "Europe/London"},
        )
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
