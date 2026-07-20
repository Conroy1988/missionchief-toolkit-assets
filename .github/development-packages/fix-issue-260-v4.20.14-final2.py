#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/fix-issue-260-v4.20.14.py"
CLEANUP = [
    ROOT / ".github/development-packages/fix-issue-260-v4.20.14-final.py",
    ROOT / ".github/development-packages/diagnose-issue-260-final-wrapper.py",
    ROOT / "docs/issue-260-clean-package-diagnostic.md",
    ROOT / "docs/issue-260-final-wrapper-diagnostic.md",
]

text = PACKAGE.read_text(encoding="utf-8")

runtime_anchor = '''    text = replace_once(text, "assert.strictEqual(fightRows.find(item => item.key === 'railway-police-officer').requiredText, '8', 'authoritative trained-personnel baseline reaches Matrix');", "assert.strictEqual(fightRows.some(item => item.key === 'railway-police-officer'), false, 'spawn-availability trained personnel never reach Matrix rows');", "Fight on Train Matrix assertion")

    anchor = "const parsedCatalogues = new Map();"'''
runtime_replacement = '''    text = replace_once(text, "assert.strictEqual(fightRows.find(item => item.key === 'railway-police-officer').requiredText, '8', 'authoritative trained-personnel baseline reaches Matrix');", "assert.strictEqual(fightRows.some(item => item.key === 'railway-police-officer'), false, 'spawn-availability trained personnel never reach Matrix rows');", "Fight on Train Matrix assertion")
    text = replace_once(text, "assert(publicOrderRows.every(row => row.uncertain && row.selectedText === '?' && row.enRouteText === '?'), 'unmapped role capacity remains safely uncertain');", "const level1PublicOrderRow = publicOrderRows.find(row => row.key === 'public-order-level-1');\\nconst level2PublicOrderRow = publicOrderRows.find(row => row.key === 'public-order-level-2');\\nassert(level1PublicOrderRow.uncertain && level1PublicOrderRow.selectedText === '?' && level1PublicOrderRow.enRouteText === '?', 'unverified Level 1 Public Order capacity remains safely uncertain');\\nassert.strictEqual(level2PublicOrderRow.uncertain, false, 'verified Level 2 Public Order capacity has an exact empty state');\\nassert.strictEqual(level2PublicOrderRow.selectedText, '0', 'verified Level 2 Public Order selected capacity starts at zero');\\nassert.strictEqual(level2PublicOrderRow.respondingText, '0', 'verified Level 2 Public Order responding capacity starts at zero');", "public order capability boundary")

    anchor = "const parsedCatalogues = new Map();"'''
if text.count(runtime_anchor) != 1:
    raise RuntimeError("Issue 260 public-order fixture anchor missing")
text = text.replace(runtime_anchor, runtime_replacement, 1)

contract_anchor = '''    text = replace_once(text, '"function missionRequirementsCataloguePersonnelRequirements(label, value)",', '"function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null)",', "personnel signature marker")
    lines = text.splitlines()'''
contract_replacement = '''    text = replace_once(text, '"function missionRequirementsCataloguePersonnelRequirements(label, value)",', '"function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null)",', "personnel signature marker")
    text = replace_once(text, '            assert entry["aliases"] and entry["types"]', '            assert entry["aliases"] and (entry["types"] or entry.get("training"))\\n            for training in entry.get("training", []):\\n                assert isinstance(training, str) and training.strip()', "training-only capability contract")
    lines = text.splitlines()'''
if text.count(contract_anchor) != 1:
    raise RuntimeError("Issue 260 dataset contract anchor missing")
PACKAGE.write_text(text.replace(contract_anchor, contract_replacement, 1), encoding="utf-8")

runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink(missing_ok=True)
for path in CLEANUP:
    path.unlink(missing_ok=True)
