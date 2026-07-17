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


def changelog_contains_version(changelog: str, version: str) -> bool:
    return (
        re.search(
            rf"^## \[{re.escape(version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$",
            changelog,
            re.MULTILINE,
        )
        is not None
    )


def evaluate_version_state(
    source_version: str,
    dashboard: dict[str, Any],
    changelog: str,
    *,
    allow_source_transition: bool = False,
) -> tuple[str, list[str], list[str]]:
    """Classify the published, candidate and guarded source-transition states."""
    failures: list[str] = []
    warnings: list[str] = []

    current_version = str(dashboard.get("currentVersion", "")).strip()
    latest_version = str(dashboard.get("latestRelease", {}).get("version", "")).strip()
    github_release_state = str(dashboard.get("status", {}).get("githubRelease", "")).strip()

    if not current_version or not latest_version:
        failures.append(
            "Version drift: release dashboard must record both currentVersion and latestRelease.version"
        )
        return "invalid", failures, warnings

    try:
        source_semver = semantic_version(source_version)
        current_semver = semantic_version(current_version)
        latest_semver = semantic_version(latest_version)
    except ValueError as exc:
        failures.append(str(exc))
        return "invalid", failures, warnings

    has_changelog = changelog_contains_version(changelog, source_version)

    if source_version == current_version == latest_version:
        return "published", failures, warnings

    if (
        source_version == current_version
        and source_semver > latest_semver
        and has_changelog
        and github_release_state != "published"
    ):
        warnings.append(
            f"Validated release candidate {source_version} is ahead of published release {latest_version}."
        )
        return "release-candidate", failures, warnings

    if (
        allow_source_transition
        and source_semver > current_semver
        and current_version == latest_version
        and has_changelog
    ):
        warnings.append(
            f"Validated guarded source transition {source_version} is ahead of dashboard version {current_version}."
        )
        return "source-transition", failures, warnings

    failures.append(
        "Version drift: "
        f"userscript={source_version}, currentVersion={current_version}, "
        f"latestRelease={latest_version}, githubRelease={github_release_state or 'unknown'}"
    )
    return "invalid", failures, warnings


def audit(root: Path, *, allow_release_candidate: bool = False) -> dict[str, Any]:
    contract = load_json(root / ".github/documentation-contract.json")
    site = load_json(root / "docs/site-data.json")
    dashboard = load_json(root / "status/release-dashboard.json")
    source = (root / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    help_centre = (root / "help/index.html").read_text(encoding="utf-8")
    greasy_fork = (root / "docs/greasyfork-description.md").read_text(encoding="utf-8")

    failures: list[str] = []
    warnings: list[str] = []
    version = userscript_version(source)

    version_state, version_failures, version_warnings = evaluate_version_state(
        version,
        dashboard,
        changelog,
        allow_source_transition=allow_release_candidate,
    )
    failures.extend(version_failures)
    warnings.extend(version_warnings)

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
        for path in [
            root / "README.md",
            root / "help/index.html",
            root / "docs/greasyfork-description.md",
            root / "docs/site-data.json",
            root / ".github/release-settings.json",
        ]
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

    for required_name in contract.get("requiredFeatureNames", []):
        if required_name not in feature_names:
            failures.append(f"Required public feature is absent from the Pages catalogue: {required_name}")

    public_docs = contract.get("publicDocumentation", {})
    document_contracts = [
        ("README", readme, public_docs.get("readmeRequiredTokens", []), []),
        ("Help Centre", help_centre, public_docs.get("helpRequiredTokens", []), public_docs.get("helpForbiddenTokens", [])),
        ("Greasy Fork description", greasy_fork, public_docs.get("greasyForkRequiredTokens", []), public_docs.get("greasyForkForbiddenTokens", [])),
    ]
    for document_name, document_text, required_tokens, forbidden_tokens in document_contracts:
        document_lower = document_text.lower()
        for token in required_tokens:
            if str(token).lower() not in document_lower:
                failures.append(f"{document_name} is missing required public claim: {token}")
        for token in forbidden_tokens:
            if str(token).lower() in document_lower:
                failures.append(f"{document_name} still contains forbidden stale claim: {token}")
    if f"v{version}".lower() not in help_centre.lower():
        failures.append(f"Help Centre does not identify the current Toolkit version v{version}")
    for theme in contract.get("themes", []):
        if str(theme).lower() not in help_centre.lower():
            failures.append(f"Help Centre omits supported interface system: {theme}")

    media_roadmap = site.get("mediaRoadmap", [])
    if len(media_roadmap) < 5:
        warnings.append("Visual media roadmap is unusually small")

    return {
        "schemaVersion": 2,
        "status": "failed" if failures else "passed",
        "userscriptVersion": version,
        "versionState": version_state,
        "documentedThemes": themes,
        "documentedModes": modes,
        "documentedShortcuts": shortcuts,
        "featureCount": len(feature_names),
        "publicDocumentCount": 3,
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
        f"- Version state: **{report['versionState']}**",
        f"- Features: **{report['featureCount']}**",
        f"- Themes: **{len(report['documentedThemes'])}**",
        f"- Modes: **{len(report['documentedModes'])}**",
        f"- Shortcuts: **{len(report['documentedShortcuts'])}**",
        f"- Public documentation surfaces checked: **{report['publicDocumentCount']}**",
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
        help=(
            "Allow the brief changelog-backed source transition before the release dashboard "
            "records the candidate version."
        ),
    )
    args = parser.parse_args()

    report = audit(Path(args.root).resolve(), allow_release_candidate=args.allow_release_candidate)
    Path(args.json_output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(markdown(report))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
