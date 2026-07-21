#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
V4 = ROOT / ".github/development-packages/issue-282-combined-final-v4.py"
DOC_TEMPLATE = ROOT / ".github/development-packages/issue-282-doc-template.md"
WORKFLOW_TEMPLATE = ROOT / ".github/development-packages/issue-282-workflow-template.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")
    payload = replace_once(
        payload,
        'WORKFLOW = ROOT / ".github/workflows/mission-requirements-cross-source-audit.yml"\n',
        '',
        "workflow output constant",
    )
    payload = replace_once(
        payload,
        'WORKFLOW_TEMPLATE = ROOT / ".github/development-packages/issue-282-workflow-template.yml"\n',
        '',
        "workflow template constant",
    )
    payload = replace_once(
        payload,
        'for path in (AUDIT_TEMPLATE, WORKFLOW_TEMPLATE, DOC_TEMPLATE):',
        'for path in (AUDIT_TEMPLATE, DOC_TEMPLATE):',
        "reviewed template list",
    )
    payload = replace_once(
        payload,
        'UK_CAPABILITY_FIXTURE = ROOT / "src/data/mission-requirements-en_GB.json"\\nCROSS_SOURCE_FIXTURE = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"\\nCROSS_SOURCE_WORKFLOW = ROOT / ".github/workflows/mission-requirements-cross-source-audit.yml"',
        'UK_CAPABILITY_FIXTURE = ROOT / "src/data/mission-requirements-en_GB.json"\\nCROSS_SOURCE_FIXTURE = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"',
        "contract constants without workflow file",
    )
    payload = replace_once(
        payload,
        '\\n    assert CROSS_SOURCE_WORKFLOW.exists()',
        '',
        "workflow existence assertion",
    )
    payload = replace_once(
        payload,
        '    WORKFLOW.write_text(WORKFLOW_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")\n',
        '',
        "workflow generation",
    )
    payload = replace_once(
        payload,
        '- Added a dedicated cross-source audit workflow with machine-readable and Markdown artefacts.',
        '- Integrated the cross-source audit into the canonical Mission Requirements contract and userscript validation gate.',
        "changelog workflow wording",
    )
    payload = replace_once(
        payload,
        '        WORKFLOW_TEMPLATE,\n',
        '',
        "workflow template cleanup reference",
    )
    ORIGINAL.write_text(payload, encoding="utf-8")

    doc = DOC_TEMPLATE.read_text(encoding="utf-8")
    doc = doc.replace(
        "The audit executes the production parser and capability resolver.",
        "The audit is executed by the canonical Mission Requirements contract and userscript validation gate. It executes the production parser and capability resolver.",
    )
    DOC_TEMPLATE.write_text(doc, encoding="utf-8")

    subprocess.run(["python3", str(V4)], cwd=ROOT, check=True)

    for path in (
        V4,
        WORKFLOW_TEMPLATE,
        ROOT / ".github/development-packages/issue-282-combined-final-v3.py",
        ROOT / ".github/development-packages/issue-282-v3-diagnostic.py",
        ROOT / "docs/issue-282-v3-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
