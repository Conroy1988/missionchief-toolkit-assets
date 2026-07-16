#!/usr/bin/env python3
"""Protect production incident reconciliation from pull-request preview runs."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "pages-production-monitor.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
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
    print("Pages incident reconciliation contract passed: PR previews cannot mutate the production incident.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
