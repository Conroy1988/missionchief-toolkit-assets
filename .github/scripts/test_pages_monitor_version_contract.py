#!/usr/bin/env python3
"""Fixture-backed contract for GitHub Pages public-version monitoring."""
from __future__ import annotations

import importlib.util
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / ".github" / "scripts" / "check_pages_live.py"
FIXTURE_PATH = ROOT / ".github" / "fixtures" / "pages-monitor-version-contract.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "pages-production-monitor.yml"
RELEASE_DASHBOARD_PATH = '      - "status/release-dashboard.json"'


def load_checker():
    spec = importlib.util.spec_from_file_location("pages_live_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event_block(workflow: str, event_name: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(event_name)}:\n(?P<body>.*?)(?=^  [A-Za-z_][A-Za-z0-9_-]*:|\Z)",
        workflow,
    )
    if match is None:
        raise AssertionError(f"Pages monitor workflow is missing the {event_name!r} trigger")
    return match.group("body")


def assert_workflow_trigger_contract() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    push = event_block(workflow, "push")
    pull_request = event_block(workflow, "pull_request")
    workflow_run = event_block(workflow, "workflow_run")

    assert RELEASE_DASHBOARD_PATH in push, (
        "A verified release dashboard update must trigger the production monitor directly; "
        "otherwise an existing incident can remain frozen on the previous expected version."
    )
    assert RELEASE_DASHBOARD_PATH in pull_request, (
        "Pull requests that change the release dashboard must validate the monitor contract."
    )
    assert "GitHub Pages Documentation" in workflow_run, (
        "The production monitor must also reconcile after the corresponding Pages deployment."
    )


def run_case(checker, item: dict) -> None:
    with tempfile.TemporaryDirectory(prefix="mcms-pages-monitor-") as temp:
        root = Path(temp)
        (root / ".github").mkdir(parents=True)
        (root / "status").mkdir(parents=True)
        policy = {
            "schemaVersion": 1,
            "baseUrl": "https://example.invalid/toolkit/",
            "timeoutSeconds": 1,
            "routes": [
                {
                    "path": "",
                    "contentType": "text/html",
                    "requiredText": ["MissionChief Map Command Toolkit"],
                }
            ],
        }
        (root / ".github" / "pages-monitor-policy.json").write_text(
            json.dumps(policy, indent=2) + "\n",
            encoding="utf-8",
        )
        (root / "status" / "release-dashboard.json").write_text(
            json.dumps(item["dashboard"], indent=2) + "\n",
            encoding="utf-8",
        )

        body = item["homepage"].encode("utf-8")

        def fake_fetch(url: str, timeout: int):
            assert timeout == 1
            return 200, "text/html; charset=utf-8", body, url

        checker.fetch = fake_fetch
        report = checker.audit(root)

        assert report["expectedVersion"] == item["expectedVersion"], item["name"]
        assert report["status"] == item["expectedStatus"], item["name"]


def main() -> int:
    assert_workflow_trigger_contract()
    checker = load_checker()
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    for item in fixture["cases"]:
        run_case(checker, item)
    print(
        "Pages monitor version contract passed: "
        f"dashboard push trigger plus {len(fixture['cases'])} published/candidate transition cases."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
