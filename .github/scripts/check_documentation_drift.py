#!/usr/bin/env python3
"""Validate public documentation against the canonical Toolkit contract."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def userscript_version(source: str) -> str:
    match = re.search(r"^//\s*@version\s+([^\s]+)\s*$", source, re.MULTILINE)
    if not match:
        raise ValueError("Canonical userscript has no @version metadata entry")
    return match.group(1)


def semantic_version(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        raise ValueError(f"Unsupported semantic version: {value!r}")
    return tuple(int(part) for part in match.groups())


def audit(root: Path, *, allow_release_candidate: bool = False) -> dict[str, Any]:
    contract = load_json(root / ".github/documentation-contract.json")
    site = load_json(root / "docs/site-data.json")
    dashboard = load_json(root / "status/release-dashboard.json")
    source = (root / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")

    failures: list[str] = []
    warnings: list[str] = []
    version = userscript_version(source)
    dashboard_versions = {
        str(dashboard.get("currentVersion", "")),
        str(dashboard.get("latestRelease", {}).get("version", "")),
    }
    dashboard_versions.discard("")
    if dashboard_versions != {version}:
        candidate_is_valid = False
        if allow_release_candidate and len(dashboard_versions) == 1:
            published_version = next(iter(dashboard_versions))
            try:
                candidate_is_valid = (
                    semantic_version(version) > semantic_version(published_version)
                    and re.search(rf"^## \[{re.escape(version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$", changelog, re.MULTILINE)
                    is not None
                )
            except ValueError as exc:
                failures.append(str(exc))
        if candidate_is_valid:
            warnings.append(
                f"Validated pull-request candidate {version} is ahead of published dashboard version {published_version}."
            )
        elif not failures:
            failures.append(
                f"Version drift: userscript={version}, dashboard={sorted(dashboard_versions)}"
            )

    site_project = site.get("project", {})
    for key, expected in contract.get("project", {}).items():
        actual = site_project.get(key)
        if actual != expected:
            failures.append(f"Project URL drift for {key}: expected {expected!r}, found {actual!r}")

    themes = [item.get("name") for item in site.get("themes", [])]
    if themes != contract.get("themes", []):
        failures.append(f"Theme catalogue drift: expected {contract.get('themes', [])}, found {themes}")
    if len(themes) != len(set(themes)):
        failures.append("Theme catalogue contains duplicate names")

    modes = [item.get("name") for item in site.get("modes", [])]
    if modes != contract.get("modes", []):
        failures.append(f"Operating-mode drift: expected {contract.get('modes', [])}, found {modes}")

    shortcuts = [
        {"key": str(item.get("key", "")), "action": str(item.get("action", ""))}
        for item in site.get("shortcuts", [])
    ]
    if shortcuts != contract.get("shortcuts", []):
        failures.append("Keyboard-shortcut documentation differs from the approved contract")
    keys = [item["key"].upper() for item in shortcuts]
    if len(keys) != len(set(keys)):
        failures.append("Keyboard-shortcut documentation contains duplicate keys")

    source_lower = source.lower()
    for token in contract.get("requiredSourceTokens", []):
        if str(token).lower() not in source_lower:
            failures.append(f"Documented capability token is absent from canonical source: {token}")

    repository_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [root / "README.md", root / "docs/site-data.json", root / ".github/release-settings.json"]
        if path.exists()
    )
    for url in contract.get("installUrls", []):
        if url not in repository_text:
            failures.append(f"Supported installation URL is absent from repository documentation: {url}")

    feature_names: list[str] = []
    visuals: list[str] = []
    categories = site.get("featureCategories", [])
    for category in categories:
        name = str(category.get("name", "")).strip()
        if not name:
            failures.append("Feature category has no name")
        for feature in category.get("features", []):
            feature_name = str(feature.get("name", "")).strip()
            visual = str(feature.get("visual", "")).strip()
            if not feature_name:
                failures.append(f"Feature in category {name!r} has no name")
            if not visual:
                failures.append(f"Feature {feature_name!r} has no visual identifier")
            feature_names.append(feature_name)
            visuals.append(visual)

    if len(feature_names) != len(set(feature_names)):
        failures.append("Feature catalogue contains duplicate names")
    if len(visuals) != len(set(visuals)):
        failures.append("Feature catalogue contains duplicate visual identifiers")
    if len(feature_names) < 10:
        failures.append("Feature catalogue unexpectedly contains fewer than ten features")

    media_roadmap = site.get("mediaRoadmap", [])
    if len(media_roadmap) < 5:
        warnings.append("Visual media roadmap is unusually small")

    return {
        "schemaVersion": 1,
        "status": "failed" if failures else "passed",
        "userscriptVersion": version,
        "documentedThemes": themes,
        "documentedModes": modes,
        "documentedShortcuts": shortcuts,
        "featureCount": len(feature_names),
        "failures": failures,
        "warnings": warnings,
    }


def markdown(report: dict[str, Any]) -> str:
    icon = "✅" if report["status"] == "passed" else "❌"
    lines = [
        "# Documentation Drift Audit",
        "",
        f"{icon} **Status:** {report['status'].upper()}",
        "",
        f"- Toolkit version: **{report['userscriptVersion']}**",
        f"- Features: **{report['featureCount']}**",
        f"- Themes: **{len(report['documentedThemes'])}**",
        f"- Modes: **{len(report['documentedModes'])}**",
        f"- Shortcuts: **{len(report['documentedShortcuts'])}**",
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
    parser.add_argument("--json-output", default="documentation-drift-report.json")
    parser.add_argument("--markdown-output", default="documentation-drift-report.md")
    parser.add_argument(
        "--allow-release-candidate",
        action="store_true",
        help="Allow one higher changelog-backed userscript version while the dashboard still records the published release.",
    )
    args = parser.parse_args()

    report = audit(Path(args.root).resolve(), allow_release_candidate=args.allow_release_candidate)
    Path(args.json_output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(markdown(report))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
