#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_USER = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_TXT = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'
TEST = ROOT / '.github' / 'scripts' / 'test_financial_ledger_contract.py'
CHANGELOG = ROOT / 'CHANGELOG.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected one match, found {count}')
    return text.replace(old, new, 1)


def update_userscript() -> None:
    text = SOURCE.read_text(encoding='utf-8')
    text = replace_once(text, '// @version      4.13.1', '// @version      4.13.2', 'metadata version')
    text = replace_once(text, "version: '4.13.1'", "version: '4.13.2'", 'runtime version')
    text = replace_once(text, "styleId: 'mc-map-command-toolkit-style-v4131'", "styleId: 'mc-map-command-toolkit-style-v4132'", 'style id')
    text = replace_once(
        text,
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4131__ = true;\n",
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4131__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4132__ = true;\n",
        'runtime sentinel',
    )
    text = replace_once(text, "guideVersion: '4.13.1'", "guideVersion: '4.13.2'", 'guide version')

    fetch_declaration = "    async function fetchFinancialLedger(requiredStartMs, attempt = 0, forceFull = false, exhaustive = false) {\n"
    helper = """    function normaliseFinancialLedgerEntry(entry) {\n        if (!Number.isFinite(entry?.timestamp)) return null;\n        const amount = Math.round(Number(entry.amount) || 0);\n        const description = financeNormaliseText(entry.description);\n        const dateLabel = financeNormaliseText(entry.dateLabel);\n        const rawTimestamp = financeNormaliseText(entry.rawTimestamp);\n        const sourceKey = `${entry.timestamp}|${amount}|${description.toLowerCase()}|${rawTimestamp || dateLabel}`;\n        return { ...entry, amount, description, dateLabel, rawTimestamp, sourceKey };\n    }\n\n"""
    text = replace_once(text, fetch_declaration, helper + fetch_declaration, 'normalisation helper insertion')

    old_loop = """            for (const entry of parsed.entries) {\n                if (!Number.isFinite(entry.timestamp)) continue;\n                const amount = Math.round(Number(entry.amount) || 0);\n                const description = financeNormaliseText(entry.description);\n                const dateLabel = financeNormaliseText(entry.dateLabel);\n                const rawTimestamp = financeNormaliseText(entry.rawTimestamp);\n                const sourceKey = `${entry.timestamp}|${amount}|${description.toLowerCase()}|${rawTimestamp || dateLabel}`;\n                const occurrence = (scanOccurrenceCounts.get(sourceKey) || 0) + 1;\n                scanOccurrenceCounts.set(sourceKey, occurrence);\n                pendingEntries.push({ ...entry, amount, description, dateLabel, rawTimestamp, sourceKey, occurrence });\n                if (entry.timestamp < oldestTimestamp) oldestTimestamp = entry.timestamp;\n                if (entry.timestamp < pageOldest) pageOldest = entry.timestamp;\n                if (canUseIncremental && knownSourceKeys.has(sourceKey)) pageOverlap++;\n            }\n"""
    new_loop = """            for (const entry of parsed.entries) {\n                const normalisedEntry = normaliseFinancialLedgerEntry(entry);\n                if (!normalisedEntry) continue;\n                const occurrence = (scanOccurrenceCounts.get(normalisedEntry.sourceKey) || 0) + 1;\n                scanOccurrenceCounts.set(normalisedEntry.sourceKey, occurrence);\n                pendingEntries.push({ ...normalisedEntry, occurrence });\n                if (normalisedEntry.timestamp < oldestTimestamp) oldestTimestamp = normalisedEntry.timestamp;\n                if (normalisedEntry.timestamp < pageOldest) pageOldest = normalisedEntry.timestamp;\n                if (canUseIncremental && knownSourceKeys.has(normalisedEntry.sourceKey)) pageOverlap++;\n            }\n"""
    text = replace_once(text, old_loop, new_loop, 'absorbPage normalisation extraction')

    SOURCE.write_text(text, encoding='utf-8')
    DIST_USER.write_text(text, encoding='utf-8')
    DIST_TXT.write_text(text, encoding='utf-8')


def update_contract() -> None:
    text = TEST.read_text(encoding='utf-8')
    text = replace_once(
        text,
        '    "financialLedgerAnchor",\n',
        '    "financialLedgerAnchor",\n    "normaliseFinancialLedgerEntry",\n',
        'contract function inventory',
    )
    old = '''    assert.equal(parseCreditTimestamp("1784201640000"), 1784201640000);\n}}\n'''
    new = '''    assert.equal(parseCreditTimestamp("1784201640000"), 1784201640000);\n\n    const normalised = normaliseFinancialLedgerEntry({{\n        timestamp: 1784201640000,\n        amount: 1250,\n        description: "  [Alliance]   Warehouse fire  ",\n        dateLabel: " 16/07/2026   12:34 ",\n        rawTimestamp: " 1784201640000 ",\n        page: 3,\n        row: 0\n    }});\n    assert.deepEqual(normalised, {{\n        timestamp: 1784201640000,\n        amount: 1250,\n        description: "[Alliance] Warehouse fire",\n        dateLabel: "16/07/2026 12:34",\n        rawTimestamp: "1784201640000",\n        page: 3,\n        row: 0,\n        sourceKey: "1784201640000|1250|[alliance] warehouse fire|1784201640000"\n    }});\n    assert.equal(normaliseFinancialLedgerEntry({{ timestamp: Number.NaN, amount: 100 }}), null);\n}}\n'''
    text = replace_once(text, old, new, 'normalisation contract')
    TEST.write_text(text, encoding='utf-8')


def update_changelog() -> None:
    text = CHANGELOG.read_text(encoding='utf-8')
    entry = """## [Unreleased]\n\n## [4.13.2] - 2026-07-16\n\n### Internal reliability\n- Added fixture-backed financial-ledger contracts covering parsing, retries, sequential pagination, archive boundaries, duplicate occurrences, stability restarts, incremental overlap, requested-range fallback and Discord summary inputs.\n- Extracted the deterministic ledger-entry normalization stage into a focused helper while preserving pagination order, retry timing, archive checkpoints, occurrence counting and report calculations.\n\n### Compatibility\n- No settings, themes, payout presentations, public assets or financial-report outputs were changed.\n\n"""
    text = replace_once(text, '## [Unreleased]\n\n', entry, '4.13.2 changelog entry')
    CHANGELOG.write_text(text, encoding='utf-8')


def main() -> int:
    update_userscript()
    update_contract()
    update_changelog()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
