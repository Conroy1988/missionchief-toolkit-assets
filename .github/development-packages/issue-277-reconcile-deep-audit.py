#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / ".github/scripts/deep_performance_audit.mjs"
TEST = ROOT / ".github/scripts/test_deep_performance_audit.mjs"
WORKFLOW = ROOT / ".github/workflows/deep-performance-audit.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    source = AUDIT.read_text(encoding="utf-8")
    source = replace_once(source, "schemaVersion: 3,", "schemaVersion: 4,", "schema version")
    source = replace_once(
        source,
        "  const broadSubtreeObservers = observerRegistrations.filter(item => item.subtree).length;\n  const visibleOwnershipSignals = observerRegistrations.filter(item => item.disconnectSignal || item.registrySignal).length;",
        "  const resolvedBroadSubtreeObservers = observerRegistrations.filter(item => item.subtree).length;\n  const unresolvedBroadSubtreeObservers = unresolvedObserveCalls.filter(item => /\\bsubtree\\s*:\\s*true\\b/u.test(item.options)).length;\n  const broadSubtreeObservers = resolvedBroadSubtreeObservers + unresolvedBroadSubtreeObservers;\n  const visibleOwnershipSignals = observerRegistrations.filter(item => item.disconnectSignal || item.registrySignal).length;",
        "broad subtree reconciliation",
    )
    source = replace_once(
        source,
        "message: `${broadSubtreeObservers} resolved observer registrations use subtree:true; ownership and callback evidence are required before narrowing or merging them.`",
        "message: `${broadSubtreeObservers} observer registrations use subtree:true (${resolvedBroadSubtreeObservers} locally resolved and ${unresolvedBroadSubtreeObservers} cross-function); ownership and callback evidence are required before narrowing or merging them.`",
        "observer scope finding",
    )
    source = replace_once(
        source,
        "      measuredResolvedBroadSubtreeObservers: broadSubtreeObservers,\n      unresolvedObserveCalls: unresolvedObserveCalls.length",
        "      measuredBroadSubtreeObservers: broadSubtreeObservers,\n      resolvedBroadSubtreeObservers,\n      unresolvedBroadSubtreeObservers,\n      unresolvedObserveCalls: unresolvedObserveCalls.length",
        "baseline cross-check fields",
    )
    source = replace_once(
        source,
        "      broadSubtreeObservers,\n      schedulerCalls:",
        "      broadSubtreeObservers,\n      resolvedBroadSubtreeObservers,\n      unresolvedBroadSubtreeObservers,\n      schedulerCalls:",
        "summary subtree fields",
    )
    source = replace_once(
        source,
        "    `- Resolved broad subtree registrations: \\`${summary.broadSubtreeObservers}\\``,",
        "    `- Broad subtree registrations: \\`${summary.broadSubtreeObservers}\\``,\n    `- Locally resolved broad registrations: \\`${summary.resolvedBroadSubtreeObservers}\\``,\n    `- Cross-function broad registrations: \\`${summary.unresolvedBroadSubtreeObservers}\\``,",
        "markdown subtree summary",
    )
    source = replace_once(
        source,
        "['Broad subtree registrations', baselineCrossCheck.expectedBroadSubtreeObservers, baselineCrossCheck.measuredResolvedBroadSubtreeObservers]",
        "['Broad subtree registrations', baselineCrossCheck.expectedBroadSubtreeObservers, baselineCrossCheck.measuredBroadSubtreeObservers]",
        "markdown cross-check",
    )
    AUDIT.write_text(source, encoding="utf-8")

    test = TEST.read_text(encoding="utf-8")
    test = replace_once(test, "assert.equal(data.schemaVersion, 3);", "assert.equal(data.schemaVersion, 4);", "fixture schema")
    test = replace_once(
        test,
        "assert.equal(data.summary.broadSubtreeObservers, 1);\nassert.equal(data.summary.schedulerCalls, 1);",
        "assert.equal(data.summary.broadSubtreeObservers, 1);\nassert.equal(data.summary.resolvedBroadSubtreeObservers, 1);\nassert.equal(data.summary.unresolvedBroadSubtreeObservers, 0);\nassert.equal(data.summary.schedulerCalls, 1);",
        "fixture subtree summary",
    )
    TEST.write_text(test, encoding="utf-8")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    workflow = replace_once(
        workflow,
        "      - name: Publish audit summary\n        run: cat deep-performance-audit.md >> \"$GITHUB_STEP_SUMMARY\"",
        "      - name: Cross-check trusted v4.20.17 observer baseline\n        shell: bash\n        run: |\n          set -euo pipefail\n          jq -e '\\n            .baselineCrossCheck.measuredMutationObserverConstructions == .baselineCrossCheck.expectedMutationObserverConstructions and\\n            .baselineCrossCheck.measuredResizeObserverConstructions == .baselineCrossCheck.expectedResizeObserverConstructions and\\n            .baselineCrossCheck.measuredBroadSubtreeObservers == .baselineCrossCheck.expectedBroadSubtreeObservers\\n          ' deep-performance-audit.json > /dev/null\n\n      - name: Publish audit summary\n        run: cat deep-performance-audit.md >> \"$GITHUB_STEP_SUMMARY\"",
        "workflow baseline cross-check",
    )
    WORKFLOW.write_text(workflow, encoding="utf-8")
    print("Reconciled deep audit against the trusted v4.20.17 observer baseline")


if __name__ == "__main__":
    main()
