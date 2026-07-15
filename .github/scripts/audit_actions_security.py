#!/usr/bin/env python3
"""Audit GitHub Actions pinning, publishers, triggers and permission scope."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)(?:\s+#\s*(.+))?\s*$")
PERMISSION_RE = re.compile(r"^\s*([a-z][a-z0-9-]*):\s*(read|write|none)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def action_repository(action_path: str) -> str:
    parts = action_path.split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else action_path


def audit(root: Path, policy_path: Path) -> dict[str, Any]:
    policy = load_json(policy_path)
    approved = set(policy.get("approvedActionRepositories", []))
    allowed_writes = {
        path: set(values)
        for path, values in policy.get("allowedWritePermissions", {}).items()
    }
    forbidden_triggers = set(policy.get("forbiddenTriggers", []))
    forbidden_fragments = list(policy.get("forbiddenFragments", []))

    failures: list[str] = []
    warnings: list[str] = []
    workflows: list[dict[str, Any]] = []
    action_count = 0

    workflow_root = root / ".github" / "workflows"
    paths = sorted([*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")])
    if not paths:
        failures.append("No GitHub Actions workflow files were found.")

    for path in paths:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        actions: list[dict[str, Any]] = []
        writes: set[str] = set()

        for fragment in forbidden_fragments:
            if fragment in text:
                failures.append(f"{relative}: forbidden workflow fragment: {fragment}")
        for trigger in forbidden_triggers:
            if re.search(rf"^\s*{re.escape(trigger)}\s*:", text, re.MULTILINE):
                failures.append(f"{relative}: forbidden trigger: {trigger}")

        for line_no, line in enumerate(lines, 1):
            permission = PERMISSION_RE.match(line)
            if permission and permission.group(2) == "write":
                writes.add(permission.group(1))

            match = USES_RE.match(line)
            if not match:
                continue
            reference = match.group(1)
            label = (match.group(2) or "").strip()
            if reference.startswith("./") or reference.startswith("docker://"):
                continue
            if "@" not in reference:
                failures.append(f"{relative}:{line_no}: malformed action reference: {reference}")
                continue
            action_path, ref = reference.rsplit("@", 1)
            repository = action_repository(action_path)
            action_count += 1
            actions.append({
                "line": line_no,
                "actionPath": action_path,
                "repository": repository,
                "commit": ref,
                "label": label,
            })
            if repository not in approved:
                failures.append(f"{relative}:{line_no}: unapproved action repository: {repository}")
            if not SHA_RE.fullmatch(ref):
                failures.append(
                    f"{relative}:{line_no}: action is not pinned to a 40-character commit SHA: {reference}"
                )
            if not label:
                warnings.append(
                    f"{relative}:{line_no}: pinned action has no human-readable version comment"
                )

        permitted = allowed_writes.get(relative, set())
        if writes and relative not in allowed_writes:
            failures.append(
                f"{relative}: write permissions are not represented in the policy: "
                + ", ".join(sorted(writes))
            )
        else:
            unexpected = sorted(writes - permitted)
            if unexpected:
                failures.append(
                    f"{relative}: unexpected write permissions: {', '.join(unexpected)}"
                )

        stale = sorted(permitted - writes)
        if stale:
            warnings.append(
                f"{relative}: policy allows unused write permissions: {', '.join(stale)}"
            )

        if not writes and "actions/checkout@" in text and "persist-credentials: false" not in text:
            warnings.append(
                f"{relative}: read-only checkout retains credentials; consider persist-credentials: false"
            )

        workflows.append({
            "path": relative,
            "actionReferences": actions,
            "writePermissions": sorted(writes),
            "allowedWritePermissions": sorted(permitted),
        })

    return {
        "schemaVersion": 1,
        "status": "failed" if failures else "passed",
        "workflowCount": len(paths),
        "actionReferenceCount": action_count,
        "failures": failures,
        "warnings": warnings,
        "workflows": workflows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    icon = "✅" if report["status"] == "passed" else "❌"
    lines = [
        "# GitHub Actions Security Audit",
        "",
        f"{icon} **Status:** {report['status'].upper()}",
        "",
        f"- Workflows: **{report['workflowCount']}**",
        f"- External action references: **{report['actionReferenceCount']}**",
        f"- Failures: **{len(report['failures'])}**",
        f"- Warnings: **{len(report['warnings'])}**",
    ]
    if report["failures"]:
        lines.extend(["", "## Failures", *[f"- {item}" for item in report["failures"]]])
    if report["warnings"]:
        lines.extend(["", "## Warnings", *[f"- {item}" for item in report["warnings"]]])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy", default=".github/actions-security-policy.json")
    parser.add_argument("--json-report", default="actions-security-report.json")
    parser.add_argument("--markdown-report", default="actions-security-report.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = audit(root, root / args.policy)
    Path(args.json_report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_report).write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
