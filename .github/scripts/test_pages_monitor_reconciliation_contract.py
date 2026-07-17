#!/usr/bin/env python3
"""Protect production incident reconciliation from previews and propagation races."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "pages-production-monitor.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "github.event_name != 'workflow_run' ||",
        "github.event.workflow_run.event != 'pull_request'",
        "github.event.workflow_run.conclusion == 'success'",
        "MAX_ATTEMPTS:",
        "github.event_name == 'workflow_run' || github.event_name == 'push'",
        'for ATTEMPT in $(seq 1 "$MAX_ATTEMPTS")',
        'sleep "$RETRY_SECONDS"',
        "github.event_name != 'pull_request'",
        "github.event_name != 'workflow_run' || github.event.workflow_run.event != 'pull_request'",
        ".github/scripts/test_pages_monitor_reconciliation_contract.py",
        "python3 .github/scripts/test_pages_monitor_reconciliation_contract.py",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    assert not missing, f"Pages incident reconciliation contract fragments missing: {missing}"
    assert "if: always() && github.event_name != 'pull_request'\n" not in text, (
        "Legacy reconciliation condition still permits workflow_run events from pull-request previews"
    )

    health_index = text.index("Check live GitHub Pages deployment")
    reconcile_index = text.index("Reconcile persistent incident")
    assert health_index < reconcile_index, "Propagation-aware health retries must finish before incident reconciliation"

    print(
        "Pages monitor contract passed: preview/cancelled runs are ignored and successful deployments "
        "receive a bounded propagation window before incident reconciliation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
