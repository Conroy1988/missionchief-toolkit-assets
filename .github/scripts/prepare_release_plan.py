#!/usr/bin/env python3
"""Prepare a read-only release recommendation and draft notes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_version(value: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(value.strip().lstrip("v"))
    if not match:
        raise ValueError(f"Invalid semantic version: {value}")
    return tuple(int(part) for part in match.groups())


def format_version(value: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in value)


def bump(current: tuple[int, int, int], level: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if level == "major":
        return major + 1, 0, 0
    if level == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def labels(pr: dict[str, Any]) -> set[str]:
    result = set()
    for item in pr.get("labels", []):
        if isinstance(item, dict):
            result.add(str(item.get("name", "")).lower())
        else:
            result.add(str(item).lower())
    return result


def classify(pr: dict[str, Any]) -> tuple[str, str]:
    title = str(pr.get("title", "")).strip()
    lower = title.lower()
    pr_labels = labels(pr)
    if "breaking" in lower or "breaking-change" in pr_labels or "major" in pr_labels:
        return "Breaking changes", "major"
    if "enhancement" in pr_labels or lower.startswith(("feat", "add ", "introduce ")):
        return "Features", "minor"
    if "bug" in pr_labels or lower.startswith(("fix", "repair", "prevent", "correct")):
        return "Fixes", "patch"
    if "area: release pipeline" in pr_labels or any(word in lower for word in ("workflow", "release", "github", "pipeline", "audit")):
        return "Infrastructure", "patch"
    if any(word in lower for word in ("document", "readme", "docs", "guide")):
        return "Documentation", "patch"
    return "Other changes", "patch"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull-requests", required=True)
    parser.add_argument("--release-level", choices=["auto", "patch", "minor", "major"], default="auto")
    parser.add_argument("--proposed-version", default="")
    parser.add_argument("--since", default="")
    parser.add_argument("--json-output", default="release-plan.json")
    parser.add_argument("--markdown-output", default="release-plan.md")
    args = parser.parse_args()

    root = Path.cwd()
    dashboard = json.loads((root / "status/release-dashboard.json").read_text(encoding="utf-8"))
    current_text = str(dashboard.get("currentVersion") or dashboard.get("latestRelease", {}).get("version"))
    current = parse_version(current_text)
    release_time = str(dashboard.get("latestRelease", {}).get("releasedAt") or "")
    since = args.since.strip() or release_time
    since_dt = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else None

    pull_requests = json.loads(Path(args.pull_requests).read_text(encoding="utf-8"))
    merged: list[dict[str, Any]] = []
    for pr in pull_requests:
        merged_at = pr.get("merged_at") or pr.get("mergedAt")
        if not merged_at:
            continue
        merged_dt = datetime.fromisoformat(str(merged_at).replace("Z", "+00:00"))
        if since_dt and merged_dt <= since_dt:
            continue
        merged.append(pr)

    severity = {"patch": 0, "minor": 1, "major": 2}
    categories: dict[str, list[dict[str, Any]]] = {}
    automatic_level = "patch"
    for pr in sorted(merged, key=lambda item: str(item.get("merged_at") or item.get("mergedAt"))):
        category, level = classify(pr)
        if severity[level] > severity[automatic_level]:
            automatic_level = level
        categories.setdefault(category, []).append(pr)

    selected_level = automatic_level if args.release_level == "auto" else args.release_level
    recommended = bump(current, selected_level)
    proposed = parse_version(args.proposed_version) if args.proposed_version.strip() else recommended
    if proposed <= current:
        raise SystemExit(f"Proposed version {format_version(proposed)} must be higher than {current_text}")

    proposed_text = format_version(proposed)
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    changelog_ready = bool(re.search(rf"^##\s+\[?v?{re.escape(proposed_text)}\]?\b", changelog, re.MULTILINE))

    source_path = root / "src/MissionChief_Map_Command_Toolkit.user.js"
    dist_path = root / "dist/MissionChief_Map_Command_Toolkit.user.js"
    report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "currentVersion": current_text,
        "recommendedLevel": selected_level,
        "recommendedVersion": format_version(recommended),
        "proposedVersion": proposed_text,
        "since": since,
        "mergedPullRequestCount": len(merged),
        "changelogSectionPresent": changelog_ready,
        "canonicalSha256": sha256(source_path),
        "distributionSha256": sha256(dist_path),
        "categories": {
            category: [
                {
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "url": pr.get("html_url") or pr.get("url"),
                    "mergedAt": pr.get("merged_at") or pr.get("mergedAt"),
                    "labels": sorted(labels(pr)),
                }
                for pr in items
            ]
            for category, items in categories.items()
        },
        "publishesNothing": True,
    }

    order = ["Breaking changes", "Features", "Fixes", "Infrastructure", "Documentation", "Other changes"]
    lines = [
        "# MissionChief Toolkit Release Plan",
        "",
        "> This plan is advisory and publishes nothing.",
        "",
        f"- Current version: **{current_text}**",
        f"- Recommended level: **{selected_level}**",
        f"- Recommended version: **{format_version(recommended)}**",
        f"- Proposed version: **{proposed_text}**",
        f"- Merged pull requests since `{since or 'repository history start'}`: **{len(merged)}**",
        f"- Changelog section present: **{'yes' if changelog_ready else 'no'}**",
        f"- Canonical SHA-256: `{report['canonicalSha256'] or 'unavailable'}`",
        f"- Distribution SHA-256: `{report['distributionSha256'] or 'unavailable'}`",
    ]
    for category in order:
        items = report["categories"].get(category, [])
        if not items:
            continue
        lines.extend(["", f"## {category}"])
        for item in items:
            number = f"#{item['number']}" if item.get("number") else "PR"
            lines.append(f"- {number} — {item['title']}")
    lines.extend([
        "",
        "## Operator gates",
        "",
        "- [ ] Confirm semantic version",
        "- [ ] Confirm changelog section and public wording",
        "- [ ] Review affected features, themes and operating modes",
        "- [ ] Run Release Readiness Check",
        "- [ ] Confirm GitHub Release, Greasy Fork, private backup and Discord targets",
        "- [ ] Publish only through the production release workflow",
        "",
    ])

    Path(args.json_output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
