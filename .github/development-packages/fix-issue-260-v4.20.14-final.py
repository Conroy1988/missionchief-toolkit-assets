#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/fix-issue-260-v4.20.14.py"
DIAGNOSTIC = ROOT / ".github/development-packages/diagnose-issue-260-clean-package.py"
REPORT = ROOT / "docs/issue-260-clean-package-diagnostic.md"

text = PACKAGE.read_text(encoding="utf-8")
anchor = '''    text = replace_once(text, "assert.strictEqual(fightRows.find(item => item.key === 'railway-police-officer').requiredText, '8', 'authoritative trained-personnel baseline reaches Matrix');", "assert.strictEqual(fightRows.some(item => item.key === 'railway-police-officer'), false, 'spawn-availability trained personnel never reach Matrix rows');", "Fight on Train Matrix assertion")

    anchor = "const parsedCatalogues = new Map();"'''
replacement = '''    text = replace_once(text, "assert.strictEqual(fightRows.find(item => item.key === 'railway-police-officer').requiredText, '8', 'authoritative trained-personnel baseline reaches Matrix');", "assert.strictEqual(fightRows.some(item => item.key === 'railway-police-officer'), false, 'spawn-availability trained personnel never reach Matrix rows');", "Fight on Train Matrix assertion")
    text = replace_once(text, "assert(publicOrderRows.every(row => row.uncertain && row.selectedText === '?' && row.enRouteText === '?'), 'unmapped role capacity remains safely uncertain');", "const level1PublicOrderRow = publicOrderRows.find(row => row.key === 'public-order-level-1');\\nconst level2PublicOrderRow = publicOrderRows.find(row => row.key === 'public-order-level-2');\\nassert(level1PublicOrderRow.uncertain && level1PublicOrderRow.selectedText === '?' && level1PublicOrderRow.enRouteText === '?', 'unverified Level 1 Public Order capacity remains safely uncertain');\\nassert.strictEqual(level2PublicOrderRow.uncertain, false, 'verified Level 2 Public Order capacity has an exact empty state');\\nassert.strictEqual(level2PublicOrderRow.selectedText, '0', 'verified Level 2 Public Order selected capacity starts at zero');\\nassert.strictEqual(level2PublicOrderRow.respondingText, '0', 'verified Level 2 Public Order responding capacity starts at zero');", "public order capability boundary")

    anchor = "const parsedCatalogues = new Map();"'''
if text.count(anchor) != 1:
    raise RuntimeError("Issue 260 public-order fixture anchor missing")
PACKAGE.write_text(text.replace(anchor, replacement, 1), encoding="utf-8")
runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink(missing_ok=True)
DIAGNOSTIC.unlink(missing_ok=True)
REPORT.unlink(missing_ok=True)
