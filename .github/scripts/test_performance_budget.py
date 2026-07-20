#!/usr/bin/env python3
"""Self-tests for the Toolkit performance-budget checker."""
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

    def test_embedded_css_and_direct_runtime_primitives_are_counted(self) -> None:
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
            self.assertEqual(metrics["mutation_observer_constructions"], 1)
            self.assertEqual(metrics["startup_hook_calls"], 1)
            self.assertGreater(metrics["css_bytes"], 0)
            self.assertEqual(metrics["css_rule_blocks"], 1)

    def test_managed_wrapper_calls_exclude_function_declarations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(
                Path(temporary),
                "candidate.user.js",
                """function runtimeSetTimeout(callback, delay) { return setTimeout(callback, delay); }
runtimeSetTimeout(run, 10);
runtimeSetTimeout(run, 20);
function runtimeListen() {}
runtimeListen(document, 'click', run);
""",
            )
            metrics = budget.collect_metrics(source)
            self.assertEqual(metrics["runtime_timeout_calls"], 2)
            self.assertEqual(metrics["runtime_listener_calls"], 1)
            self.assertEqual(metrics["set_timeout_calls"], 1)

    def test_observer_aliases_are_resolved_without_double_counting_direct_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(
                Path(temporary),
                "candidate.user.js",
                """const MutationObserverCtor = pageWindow.MutationObserver || MutationObserver;
const Observer = doc.defaultView?.MutationObserver || MutationObserver;
const ResizeObserverCtor = pageWindow.ResizeObserver || ResizeObserver;
new MutationObserver(() => {});
new pageWindow.MutationObserver(() => {});
new MutationObserverCtor(() => {});
new Observer(() => {});
new ResizeObserverCtor(() => {});
""",
            )
            metrics = budget.collect_metrics(source)
            self.assertEqual(metrics["mutation_observers"], 2)
            self.assertEqual(metrics["mutation_observer_constructions"], 4)
            self.assertEqual(metrics["resize_observers"], 0)
            self.assertEqual(metrics["resize_observer_constructions"], 1)

    def test_subtree_and_document_wide_observers_are_distinguished(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(
                Path(temporary),
                "candidate.user.js",
                """first.observe(componentRoot, { childList: true, subtree: true });
second.observe(document.body, { childList: true, subtree: true });
third.observe(document.documentElement, { attributes: true, subtree: true });
fourth.observe(localRoot, { childList: true });
""",
            )
            metrics = budget.collect_metrics(source)
            self.assertEqual(metrics["broad_subtree_observers"], 3)
            self.assertEqual(metrics["document_wide_subtree_observers"], 2)

    def test_dom_and_network_indicators_are_counted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(
                Path(temporary),
                "candidate.user.js",
                """document.getElementById('one');
node.innerHTML = html;
GM_xmlhttpRequest({ url: '/one' });
fetch('/two');
new XMLHttpRequest();
""",
            )
            metrics = budget.collect_metrics(source)
            self.assertEqual(metrics["get_element_by_id_calls"], 1)
            self.assertEqual(metrics["inner_html_writes"], 1)
            self.assertEqual(metrics["network_request_calls"], 3)

    def test_required_fragment_failure_is_reported(self) -> None:
        candidate = {metric: 0 for metric in budget.METRIC_LABELS}
        findings = budget.evaluate(candidate, None, {"requiredSourceFragments": ["required-marker"], "absoluteLimits": {}}, "ordinary source")
        self.assertTrue(any(finding.level == "failure" for finding in findings))

    def test_absolute_utilisation_threshold_warns_without_failure(self) -> None:
        candidate = {metric: 0 for metric in budget.METRIC_LABELS}
        candidate["lines"] = 95
        findings = budget.evaluate(
            candidate,
            None,
            {"absoluteLimits": {"lines": 100}, "absoluteReviewPercent": {"lines": 95}},
            "",
        )
        self.assertEqual([finding.level for finding in findings], ["warning"])
        self.assertIn("95.0%", findings[0].message)

    def test_absolute_limit_still_fails_before_utilisation_warning(self) -> None:
        candidate = {metric: 0 for metric in budget.METRIC_LABELS}
        candidate["lines"] = 101
        findings = budget.evaluate(
            candidate,
            None,
            {"absoluteLimits": {"lines": 100}, "absoluteReviewPercent": {"lines": 95}},
            "",
        )
        self.assertEqual([finding.level for finding in findings], ["failure"])

    def test_warning_threshold_does_not_become_failure(self) -> None:
        base = {metric: 0 for metric in budget.METRIC_LABELS}
        candidate = dict(base)
        candidate["set_timeout_calls"] = 2
        findings = budget.evaluate(
            candidate,
            base,
            {"absoluteLimits": {}, "relativeLimits": {"set_timeout_calls": {"warnDelta": 1, "failDelta": 4}}},
            "",
        )
        self.assertEqual([finding.level for finding in findings], ["warning"])

    def test_baseline_locked_metric_fails_on_any_increase(self) -> None:
        base = {metric: 0 for metric in budget.METRIC_LABELS}
        candidate = dict(base)
        candidate["runtime_timeout_calls"] = 100
        base["runtime_timeout_calls"] = 99
        findings = budget.evaluate(
            candidate,
            base,
            {"absoluteLimits": {}, "relativeLimits": {"runtime_timeout_calls": {"warnDelta": 0, "failDelta": 0}}},
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
                    "bytes": {"warnDelta": 20, "warnPercent": 5, "failDelta": 30, "failPercent": 10}
                },
            },
            "",
        )
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
