#!/usr/bin/env python3
"""Enforce public documentation against published or candidate Toolkit state."""

from __future__ import annotations

import json
import re
from pathlib import Path

import check_documentation_drift as drift_audit

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = (
    "Enhanced Operational Requirements",
    "Extended Call Window",
    "Extended Call List",
    "Enhanced Transport Requests",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads((ROOT / "dist/release-manifest.json").read_text(encoding="utf-8"))
    dashboard = json.loads((ROOT / "status/release-dashboard.json").read_text(encoding="utf-8"))
    version = str(manifest["version"])
    production_version = str(dashboard["latestRelease"]["version"])
    candidate = version != production_version

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    hero = (ROOT / "docs/media/readme-hero.svg").read_text(encoding="utf-8")
    site_text = (ROOT / "docs/site-data.json").read_text(encoding="utf-8")
    site = json.loads(site_text)
    help_text = (ROOT / "help/index.html").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")

    drift = drift_audit.audit(ROOT, allow_release_candidate=True)
    drift_md = drift_audit.markdown(drift)

    if candidate:
        require(
            f"Current verified release: `v{production_version}` · Development candidate: `v{version}`" in readme,
            "README does not distinguish production from the development candidate",
        )
        expected_drift_state = "source-transition"
    else:
        require(
            f"Current verified release: `v{version}`" in readme,
            "README current release differs from the manifest",
        )
        expected_drift_state = "published"

    require("v4.20.33" not in readme, "README still advertises the obsolete v4.20.33 line")
    require(
        "Mission Requirements Matrix" not in readme,
        "README still advertises the retired Matrix as current",
    )

    for family in FAMILIES:
        require(family in readme, f"README is missing {family}")
        require(family in site_text, f"site-data is missing {family}")
        require(family in help_text, f"Help Centre is missing {family}")

    require(
        "Operational Window Suite" in hero,
        "README hero is not aligned with the Operational Window Suite",
    )
    require(
        not re.search(r"\bv\d+\.\d+\.\d+\b", hero),
        "README hero must remain version-neutral",
    )
    require(
        "Mission Requirements Matrix" not in hero,
        "README hero still presents the retired Matrix",
    )

    category = next(
        (item for item in site["featureCategories"] if item["name"] == "Operational Window Suite"),
        None,
    )
    require(category is not None, "site-data has no Operational Window Suite category")
    require(
        [item["name"] for item in category["features"]] == list(FAMILIES),
        "site-data operational families differ from the canonical order",
    )
    require(
        any(item["title"] == "Operational Window Suite" for item in site["documentation"]),
        "site-data has no Operational Window guide",
    )

    if candidate:
        require(
            f"v{version}" in help_text and "candidate" in help_text.lower(),
            "Help Centre does not identify the candidate version and state",
        )
    else:
        require(
            f"Guide for Toolkit v{version}" in help_text,
            "Help Centre version differs from the manifest",
        )
    require(
        "live Mission Requirements matrix" not in help_text,
        "Help Centre still advertises the retired matrix wording",
    )
    require(drift["status"] == "passed", f"live documentation drift audit failed: {drift['failures']}")
    require(drift["userscriptVersion"] == version, "documentation drift version is stale")
    require(
        drift["versionState"] == expected_drift_state,
        f"documentation drift state {drift['versionState']!r} differs from {expected_drift_state!r}",
    )
    require(
        drift["featureCount"] == sum(len(item.get("features", [])) for item in site["featureCategories"]),
        "documentation drift feature count differs from site-data",
    )
    require(
        f"Toolkit version: **{version}**" in drift_md,
        "documentation drift Markdown version is stale",
    )
    require(
        "python3 .github/scripts/test_documentation_consistency.py" in workflow,
        "canonical validation does not run the documentation contract",
    )

    state_label = f"candidate over production {production_version}" if candidate else "published"
    print(
        f"Documentation consistency passed for Toolkit {version} ({state_label}): "
        "README, hero, site data, Help Centre and live drift evidence agree."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
