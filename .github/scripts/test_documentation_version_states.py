#!/usr/bin/env python3
"""Fixture-backed tests for documentation release-state classification."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / ".github" / "scripts" / "check_documentation_drift.py"
FIXTURE_PATH = ROOT / ".github" / "fixtures" / "documentation-version-states.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("documentation_drift_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    checker = load_checker()
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    for case in fixture["cases"]:
        dashboard = {
            "currentVersion": case["currentVersion"],
            "latestRelease": {"version": case["latestReleaseVersion"]},
            "status": {"githubRelease": case["githubRelease"]},
        }
        changelog = f"## [{case['changelogVersion']}] - 2026-07-16\n"
        state, state_failures, _warnings = checker.evaluate_version_state(
            case["sourceVersion"],
            dashboard,
            changelog,
            allow_source_transition=bool(case["allowSourceTransition"]),
        )
        failed = bool(state_failures)
        if state != case["expectedState"]:
            failures.append(
                f"{case['name']}: expected state {case['expectedState']!r}, found {state!r}"
            )
        if failed != bool(case["expectedFailure"]):
            failures.append(
                f"{case['name']}: expected failure={case['expectedFailure']}, found {failed}; "
                f"details={state_failures}"
            )

    if failures:
        print("Documentation version-state fixtures failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Documentation version-state fixtures passed: {len(fixture['cases'])} cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
