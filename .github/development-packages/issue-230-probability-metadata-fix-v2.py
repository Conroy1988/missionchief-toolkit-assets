#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-230-probability-metadata-fix.py"
RUNTIME = ROOT / ".github/development-packages/.issue-230-probability-runtime.py"

OLD_INSERT = '''    runtime = replace_once(runtime, "// Issue #260: clean labels and typed Mission Info personnel classification.\\n", TEST_BLOCK + "// Issue #260: clean labels and typed Mission Info personnel classification.\\n", "Issue 230 runtime fixtures")
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")
'''
NEW_INSERT = '''    runtime = replace_once(runtime, "// Issue #260: clean labels and typed Mission Info personnel classification.\\n", TEST_BLOCK + "// Issue #260: clean labels and typed Mission Info personnel classification.\\n", "Issue 230 runtime fixtures")
    runtime = replace_once(
        runtime,
        """const conditionalCatalogue = parsedCatalogues.get('alternative and conditional requirements');
const conditionalParsed = api.reconcileCatalogue({ requirements: [], unresolved: [] }, conditionalCatalogue, 'ready', true);
const conditionalRow = api.resolve(authoritativeCandidate, conditionalParsed, conditionalCatalogue).find(item => item.key === 'police-car');
assert.strictEqual(conditionalRow.uncertain, true, 'probabilistic mission-info requirement remains uncertain when not covered');
assert.strictEqual(conditionalRow.definitelyOpen, false, 'probabilistic mission-info requirement is not falsely reported as definitely required');
""",
        """const conditionalCatalogue = parsedCatalogues.get('alternative and conditional requirements');
const conditionalParsed = api.reconcileCatalogue({ requirements: [], unresolved: [] }, conditionalCatalogue, 'ready', true);
assert.strictEqual(conditionalCatalogue.requirements.some(item => item.key === 'police-car' && item.probability < 100), true, 'probabilistic Police Car requirement remains typed in Mission Info');
assert.strictEqual(conditionalParsed.requirements.some(item => item.key === 'police-car'), false, 'catalogue-only probabilistic Police Car demand remains dormant');
assert.strictEqual(api.resolve(authoritativeCandidate, conditionalParsed, conditionalCatalogue).some(item => item.key === 'police-car'), false, 'dormant conditional demand creates no Matrix row');
""",
        "legacy conditional runtime fixture",
    )
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")
'''


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    count = payload.count(OLD_INSERT)
    if count != 1:
        raise RuntimeError(f"runtime fixture insertion: expected one match, found {count}")
    RUNTIME.write_text(payload.replace(OLD_INSERT, NEW_INSERT, 1), encoding="utf-8")
    try:
        subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, check=True)
    finally:
        RUNTIME.unlink(missing_ok=True)
    for path in (
        ORIGINAL,
        ROOT / "docs/issue-230-probability-package-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
