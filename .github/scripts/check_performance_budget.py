#!/usr/bin/env python3
"""Static performance-regression guardrails for the MissionChief Toolkit.

The checker compares a candidate userscript with a base userscript and applies
version-controlled absolute and relative budgets. It measures source workload
indicators rather than attempting to benchmark MissionChief in CI.

Direct browser primitives and Toolkit lifecycle-managed wrappers are reported
separately. Observer constructors are resolved through simple local aliases so
that safe wrappers do not disappear from the performance baseline.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


METRIC_LABELS = {
    "bytes": "Source bytes",
    "lines": "Source lines",
    "nonempty_lines": "Non-empty lines",
    "css_bytes": "Estimated embedded CSS bytes",
    "css_rule_blocks": "Estimated embedded CSS rule blocks",
    "set_interval_calls": "Direct setInterval call sites",
    "set_timeout_calls": "Direct setTimeout call sites",
    "mutation_observers": "Direct MutationObserver constructions",
    "resize_observers": "Direct ResizeObserver constructions",
    "request_animation_frame_calls": "Direct requestAnimationFrame call sites",
    "event_listener_calls": "Direct addEventListener call sites",
    "query_selector_calls": "querySelector/querySelectorAll call sites",
    "startup_hook_calls": "DOMContentLoaded/load startup hooks",
    "runtime_interval_calls": "Managed runtimeSetInterval call sites",
    "runtime_timeout_calls": "Managed runtimeSetTimeout call sites",
    "runtime_animation_frame_calls": "Managed runtimeRequestAnimationFrame call sites",
    "runtime_listener_calls": "Managed runtimeListen call sites",
    "runtime_observer_track_calls": "Managed runtimeTrackObserver call sites",
    "runtime_idle_calls": "Managed runtimeRunWhenIdle call sites",
    "mutation_observer_constructions": "MutationObserver constructions including aliases",
    "resize_observer_constructions": "ResizeObserver constructions including aliases",
    "broad_subtree_observers": "Observer registrations with subtree: true",
    "document_wide_subtree_observers": "Document/body subtree observer registrations",
    "get_element_by_id_calls": "getElementById call sites",
    "inner_html_writes": "innerHTML assignment sites",
    "network_request_calls": "GM/fetch/XMLHttpRequest request sites",
}

DIRECT_PATTERNS = {
    "set_interval_calls": re.compile(r"\bsetInterval\s*\("),
    "set_timeout_calls": re.compile(r"\bsetTimeout\s*\("),
    "mutation_observers": re.compile(r"\bnew\s+(?:pageWindow\.)?MutationObserver\s*\("),
    "resize_observers": re.compile(r"\bnew\s+(?:pageWindow\.)?ResizeObserver\s*\("),
    "request_animation_frame_calls": re.compile(r"\brequestAnimationFrame\s*\("),
    "event_listener_calls": re.compile(r"\.addEventListener\s*\("),
    "query_selector_calls": re.compile(r"\.(?:querySelector|querySelectorAll)\s*\("),
    "startup_hook_calls": re.compile(
        r"\.addEventListener\s*\(\s*['\"](?:DOMContentLoaded|load|readystatechange)['\"]"
    ),
    "get_element_by_id_calls": re.compile(r"\.getElementById\s*\("),
    "inner_html_writes": re.compile(r"\.innerHTML\s*=(?!=)"),
}

MANAGED_CALLS = {
    "runtime_interval_calls": "runtimeSetInterval",
    "runtime_timeout_calls": "runtimeSetTimeout",
    "runtime_animation_frame_calls": "runtimeRequestAnimationFrame",
    "runtime_listener_calls": "runtimeListen",
    "runtime_observer_track_calls": "runtimeTrackObserver",
    "runtime_idle_calls": "runtimeRunWhenIdle",
}

TEMPLATE_LITERAL = re.compile(r"`((?:\\.|[^`])*)`", re.DOTALL)
CSS_SIGNAL = re.compile(
    r"(?:!important|--[a-zA-Z0-9_-]+\s*:|(?:display|position|color|background|border|font|padding|margin|width|height|opacity|transform|animation|z-index)\s*:)",
    re.IGNORECASE,
)
ALIAS_ASSIGNMENT = re.compile(
    r"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?P<value>[^;\n]{0,800}(?:MutationObserver|ResizeObserver)[^;\n]{0,800})\s*;"
)
OBSERVE_CALL = re.compile(r"\.observe\s*\(")
NETWORK_PATTERNS = (
    re.compile(r"\bGM_xmlhttpRequest\s*\("),
    re.compile(r"\bGM\.xmlHttpRequest\s*\("),
    re.compile(r"(?<![.\w])fetch\s*\("),
    re.compile(r"\bnew\s+(?:pageWindow\.)?XMLHttpRequest\s*\("),
)


@dataclass(frozen=True)
class Finding:
    level: str
    metric: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--base", type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc


def embedded_css_metrics(text: str) -> tuple[int, int]:
    css_bytes = 0
    rule_blocks = 0
    for match in TEMPLATE_LITERAL.finditer(text):
        value = match.group(1)
        if "{" not in value or "}" not in value or not CSS_SIGNAL.search(value):
            continue
        css_bytes += len(value.encode("utf-8"))
        rule_blocks += value.count("{")
    return css_bytes, rule_blocks


def count_function_calls(text: str, name: str) -> int:
    """Count call sites while excluding a normal function declaration."""
    pattern = re.compile(rf"\b{re.escape(name)}\s*\(")
    count = 0
    for match in pattern.finditer(text):
        prefix = text[max(0, match.start() - 80):match.start()]
        if re.search(r"\bfunction\s*$", prefix):
            continue
        count += 1
    return count


def observer_aliases(text: str, constructor: str) -> set[str]:
    aliases: set[str] = set()
    for match in ALIAS_ASSIGNMENT.finditer(text):
        if constructor in match.group("value"):
            aliases.add(match.group("name"))
    return aliases


def observer_constructions(text: str, constructor: str) -> int:
    direct = re.compile(rf"\bnew\s+(?:(?:pageWindow|window)\.)?{constructor}\s*\(")
    total = len(direct.findall(text))
    for alias in observer_aliases(text, constructor):
        total += len(re.findall(rf"\bnew\s+{re.escape(alias)}\s*\(", text))
    return total


def observer_registration_metrics(text: str) -> tuple[int, int]:
    broad = 0
    document_wide = 0
    for match in OBSERVE_CALL.finditer(text):
        # Observer option objects in the Toolkit are compact; a bounded scan
        # avoids allowing one registration to consume following functions.
        segment = text[match.start():match.start() + 2400]
        terminator = segment.find(");")
        if terminator < 0:
            continue
        call = segment[:terminator + 2]
        if not re.search(r"\bsubtree\s*:\s*true\b", call):
            continue
        broad += 1
        target = call[:call.find(",") if "," in call else len(call)]
        if re.search(r"\b(?:document(?:\.body|\.documentElement)?|doc\.body)\b", target):
            document_wide += 1
    return broad, document_wide


def collect_metrics(path: Path) -> dict[str, int]:
    text = read_text(path)
    css_bytes, css_rule_blocks = embedded_css_metrics(text)
    broad_subtree, document_wide = observer_registration_metrics(text)
    lines = text.splitlines()
    metrics: dict[str, int] = {
        "bytes": len(text.encode("utf-8")),
        "lines": len(lines),
        "nonempty_lines": sum(1 for line in lines if line.strip()),
        "css_bytes": css_bytes,
        "css_rule_blocks": css_rule_blocks,
        "mutation_observer_constructions": observer_constructions(text, "MutationObserver"),
        "resize_observer_constructions": observer_constructions(text, "ResizeObserver"),
        "broad_subtree_observers": broad_subtree,
        "document_wide_subtree_observers": document_wide,
        "network_request_calls": sum(len(pattern.findall(text)) for pattern in NETWORK_PATTERNS),
    }
    metrics.update({name: len(pattern.findall(text)) for name, pattern in DIRECT_PATTERNS.items()})
    metrics.update({metric: count_function_calls(text, name) for metric, name in MANAGED_CALLS.items()})
    return metrics


def load_policy(path: Path) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read performance policy {path}: {exc}") from exc
    if policy.get("schemaVersion") != 1:
        raise SystemExit("Unsupported performance-budget schemaVersion")
    return policy


def format_delta(candidate: int, base: int | None) -> str:
    if base is None:
        return "n/a"
    delta = candidate - base
    if base:
        percent = (delta / base) * 100
        return f"{delta:+,} ({percent:+.2f}%)"
    return f"{delta:+,}"


def evaluate(
    candidate: dict[str, int],
    base: dict[str, int] | None,
    policy: dict[str, Any],
    candidate_text: str,
) -> list[Finding]:
    findings: list[Finding] = []

    for fragment in policy.get("requiredSourceFragments", []):
        if fragment not in candidate_text:
            findings.append(Finding("failure", "required_source_fragment", f"Required source fragment is missing: {fragment}"))

    absolute_limits = policy.get("absoluteLimits", {})
    review_thresholds = policy.get("absoluteReviewPercent", {})
    for metric, limit_value in absolute_limits.items():
        value = candidate.get(metric)
        limit = int(limit_value)
        if value is None:
            findings.append(Finding("failure", metric, f"Policy references unknown metric: {metric}"))
            continue
        if value > limit:
            findings.append(Finding("failure", metric, f"{METRIC_LABELS.get(metric, metric)} is {value:,}; absolute limit is {limit:,}."))
            continue
        review_percent = review_thresholds.get(metric)
        if review_percent is not None and limit > 0:
            utilisation = value / limit * 100
            if utilisation >= float(review_percent):
                findings.append(Finding(
                    "warning",
                    metric,
                    f"{METRIC_LABELS.get(metric, metric)} uses {value:,} of {limit:,} ({utilisation:.1f}%); review threshold is {float(review_percent):.1f}%.",
                ))

    if base is None:
        return findings

    for metric, limits in policy.get("relativeLimits", {}).items():
        if metric not in candidate or metric not in base:
            findings.append(Finding("failure", metric, f"Policy references unknown metric: {metric}"))
            continue

        current = candidate[metric]
        previous = base[metric]
        delta = current - previous
        percent = (delta / previous * 100) if previous else (100.0 if delta > 0 else 0.0)

        fail_delta = limits.get("failDelta")
        fail_percent = limits.get("failPercent")
        warn_delta = limits.get("warnDelta")
        warn_percent = limits.get("warnPercent")

        fail_by_delta = fail_delta is not None and delta > int(fail_delta)
        fail_by_percent = fail_percent is not None and percent > float(fail_percent)
        failed = (fail_by_delta and fail_by_percent) if fail_delta is not None and fail_percent is not None else (fail_by_delta or fail_by_percent)

        warn_by_delta = warn_delta is not None and delta > int(warn_delta)
        warn_by_percent = warn_percent is not None and percent > float(warn_percent)
        warned = (warn_by_delta and warn_by_percent) if warn_delta is not None and warn_percent is not None else (warn_by_delta or warn_by_percent)

        label = METRIC_LABELS.get(metric, metric)
        if failed:
            findings.append(Finding("failure", metric, f"{label} increased from {previous:,} to {current:,} ({format_delta(current, previous)}), exceeding the failure budget."))
        elif warned:
            findings.append(Finding("warning", metric, f"{label} increased from {previous:,} to {current:,} ({format_delta(current, previous)}), exceeding the review threshold."))

    return findings


def build_markdown(candidate: dict[str, int], base: dict[str, int] | None, findings: list[Finding], policy: dict[str, Any]) -> str:
    failures = [finding for finding in findings if finding.level == "failure"]
    result = "FAILED" if failures else "PASSED"
    lines = [
        "# Toolkit performance budget",
        "",
        f"**Result:** {result}",
        "",
        "| Metric | Base | Candidate | Change | Absolute limit | Utilisation |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    absolute_limits = policy.get("absoluteLimits", {})
    for metric, label in METRIC_LABELS.items():
        candidate_value = candidate[metric]
        base_value = base[metric] if base else None
        limit = absolute_limits.get(metric)
        utilisation = f"{candidate_value / int(limit) * 100:.1f}%" if limit not in (None, 0) else "n/a"
        lines.append(
            f"| {label} | {base_value if base_value is not None else 'n/a'} | {candidate_value} | "
            f"{format_delta(candidate_value, base_value)} | {limit if limit is not None else 'n/a'} | {utilisation} |"
        )

    lines.extend(["", "## Findings", ""])
    if not findings:
        lines.append("- ✅ No performance-budget regressions detected.")
    else:
        for finding in findings:
            icon = "❌" if finding.level == "failure" else "⚠️"
            lines.append(f"- {icon} {finding.message}")

    lines.extend([
        "",
        "## Policy",
        "",
        f"- Revision: `{policy.get('revision', 'unknown')}`",
        f"- Rationale: {policy.get('rationale', 'Not recorded')}",
        "- Direct browser primitives and lifecycle-managed Toolkit wrappers are reported separately.",
        "- This is a static regression screen, not a browser benchmark.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    policy = load_policy(args.policy)
    candidate_text = read_text(args.candidate)
    candidate_metrics = collect_metrics(args.candidate)
    base_metrics = collect_metrics(args.base) if args.base and args.base.exists() else None
    findings = evaluate(candidate_metrics, base_metrics, policy, candidate_text)

    payload = {
        "schemaVersion": 2,
        "policyRevision": policy.get("revision"),
        "candidate": candidate_metrics,
        "base": base_metrics,
        "findings": [finding.__dict__ for finding in findings],
        "result": "failure" if any(f.level == "failure" for f in findings) else "success",
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(build_markdown(candidate_metrics, base_metrics, findings, policy), encoding="utf-8")

    for finding in findings:
        annotation = "error" if finding.level == "failure" else "warning"
        print(f"::{annotation} title=Toolkit performance budget::{finding.message}")

    print(args.markdown_output.read_text(encoding="utf-8"))
    return 1 if any(finding.level == "failure" for finding in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
