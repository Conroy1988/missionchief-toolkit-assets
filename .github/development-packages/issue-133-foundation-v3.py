#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-133-foundation.py"

package = ORIGINAL.read_text(encoding="utf-8")

replacements = [
    (
        "        missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements',\\n\",\n",
        "        missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements',\\n        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style',\\n\",\n",
        "SCRIPT-owned mission requirements document style ID",
    ),
    (
        "        const styleId = 'mcms-mission-requirements-document-style';",
        "        const requirementsDocumentStyleId = SCRIPT.missionRequirementsDocumentStyleId;",
        "unique mission requirements style symbol",
    ),
    (
        "        let style = doc.getElementById?.(styleId);",
        "        let style = doc.getElementById?.(requirementsDocumentStyleId);",
        "mission requirements style lookup",
    ),
    (
        "            style.id = styleId;",
        "            style.id = requirementsDocumentStyleId;",
        "mission requirements style assignment",
    ),
    (
        "context.doc.getElementById?.('mcms-mission-requirements-document-style')?.remove()",
        "context.doc.getElementById?.(SCRIPT.missionRequirementsDocumentStyleId)?.remove()",
        "document style cleanup ownership",
    ),
]

for old, new, label in replacements:
    count = package.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one package anchor, found {count}")
    package = package.replace(old, new, 1)

exec(compile(package, str(ORIGINAL), "exec"), {"__name__": "__main__", "__file__": str(ORIGINAL)})

for relative in [
    ".github/development-packages/issue-133-foundation.py",
    ".github/development-packages/issue-133-foundation-v2.py",
    "docs/issue-133-source-inspection.md",
    "docs/issue-133-source-ranges.md",
    "docs/issue-133-function-inspection.md",
    "docs/issue-133-integration-context.md",
    "docs/issue-133-foundation-anchor-diagnostics.json",
    "docs/issue-133-foundation-dryrun.json",
    "docs/issue-133-foundation-validation-dryrun.json",
    "docs/issue-133-release-baseline-dryrun.json",
    "docs/issue-133-v2-diagnostics.json",
]:
    path = ROOT / relative
    if path.exists():
        path.unlink()

print("Applied Issue #133 foundation v3 and removed temporary inspection artefacts")
