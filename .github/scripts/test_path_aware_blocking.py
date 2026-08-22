#!/usr/bin/env python3
"""Static contracts for Pipeline v5.2 path-aware blocking rules."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github/path-aware-validation.json"
CLASSIFIER = ROOT / ".github/scripts/classify_pr_paths.py"
VALIDATION = ROOT / ".github/workflows/validate-userscript.yml"
AUTOMATIC = ROOT / ".github/workflows/auto-release-after-validation.yml"
DOC = ROOT / "docs/PATH_AWARE_BLOCKING.md"


def load_classifier():
    spec = importlib.util.spec_from_file_location(
        "classify_pr_paths",
        CLASSIFIER,
    )
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load path classifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} missing marker: {marker}")


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    classifier = load_classifier()
    classifier.self_test(policy)
    validation = VALIDATION.read_text(encoding="utf-8")
    automatic = AUTOMATIC.read_text(encoding="utf-8")

    require(
        validation,
        (
            "gate:",
            "name: Classify changed paths",
            "classify_pr_paths.py",
            "steps.paths.outputs.runtime == 'true'",
            "steps.paths.outputs.integrity == 'true'",
            "steps.paths.outputs.performance == 'true'",
            "steps.paths.outputs.releaseCandidate == 'true'",
            "steps.paths.outputs.developmentChecks == 'true'",
            "Run deterministic runtime contracts",
            "Prove local development loop",
            "Run fail-fast candidate checks",
            "Check lightweight performance budget",
            "tools/candidate_gate.py --stage static",
            "tools/candidate_gate.py --stage performance",
            "Parallel validation lanes: **0**",
        ),
        "validation workflow",
    )
    require(
        automatic,
        (
            "Classify merged pull-request paths",
            "PR_BASE_SHA: ${{ github.event.pull_request.base.sha }}",
            "classify_pr_paths.py",
            "No release-critical path changed; exact candidate promotion is intentionally skipped.",
            "Path-aware release candidate required",
        ),
        "automatic release workflow",
    )
    require(
        DOC.read_text(encoding="utf-8"),
        (
            "fail closed",
            "Documentation-only",
            "Retired external distribution checks",
            "exact-tree",
        ),
        "path-aware documentation",
    )
    print(
        "Path-aware blocking contract passed: selective sequential checks, "
        "fail-closed unknown paths and release-aware promotion on one runner."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
