#!/usr/bin/env python3
"""Self-tests for the static Toolkit performance-budget checker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_performance_budget as budget


class PerformanceBudgetTests(unittest.TestCase):
    def write_source(self, directory: Path, name: str, text: str) -> Path:
        path = directory / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_embedded_css_and_runtime_primitives_are_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_source(
                root,
                "candidate.user.js",
                """// @run-at document-start
const css = `#panel { display: block; color: white; }`;
setInterval(() => {}, 1000);
new MutationObserver(() => {});
document.addEventListener('DOMContentLoaded', () => {});
""",
            )
            metrics = budget.collect_metrics(source)
            self.assertEqual(metrics["set_interval_calls"], 1)
            self.assertEqual(metrics["mutation_observers"], 1)
            self.assertEqual(metrics["startup_hook_calls"], 1)
            self.assertGreater(metrics["css_bytes"], 0)
            self.assertEqual(metrics["css_rule_blocks"], 1)

    def test_required_fragment_failure_is_reported(self) -> None:
        candidate = {metric: 0 for metric in budget.METRIC_LABELS}
        findings = budget.evaluate(
            candidate,
            None,
            {"requiredSourceFragments": ["required-marker"], "absoluteLimits": {}},
            "ordinary source",
        )
        self.assertTrue(any(finding.level == "failure" for finding in findings))

    def test_warning_threshold_does_not_become_failure(self) -> None:
        base = {metric: 0 for metric in budget.METRIC_LABELS}
        candidate = dict(base)
        candidate["set_timeout_calls"] = 2
        findings = budget.evaluate(
            candidate,
            base,
            {
                "absoluteLimits": {},
                "relativeLimits": {"set_timeout_calls": {"warnDelta": 1, "failDelta": 4}},
            },
            "",
        )
        self.assertEqual([finding.level for finding in findings], ["warning"])

    def test_large_runtime_primitive_increase_fails(self) -> None:
        base = {metric: 0 for metric in budget.METRIC_LABELS}
        candidate = dict(base)
        candidate["mutation_observers"] = 5
        findings = budget.evaluate(
            candidate,
            base,
            {
                "absoluteLimits": {},
                "relativeLimits": {"mutation_observers": {"warnDelta": 1, "failDelta": 3}},
            },
            "",
        )
        self.assertTrue(any(finding.level == "failure" for finding in findings))

    def test_percent_and_delta_must_both_exceed_combined_budget(self) -> None:
        base = {metric: 100 for metric in budget.METRIC_LABELS}
        candidate = dict(base)
        candidate["bytes"] = 111
        findings = budget.evaluate(
            candidate,
            base,
            {
                "absoluteLimits": {},
                "relativeLimits": {
                    "bytes": {
                        "warnDelta": 20,
                        "warnPercent": 5,
                        "failDelta": 30,
                        "failPercent": 10,
                    }
                },
            },
            "",
        )
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
