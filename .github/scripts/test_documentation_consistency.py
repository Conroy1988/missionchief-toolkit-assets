#!/usr/bin/env python3
"""Enforce current public documentation against the canonical release manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = (
    "Enhanced Operational Requirements",
    "Extended Call Window",
    "Extended Mission List",
    "Enhanced Transport Requests",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads((ROOT / "dist/release-manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    hero = (ROOT / "docs/media/readme-hero.svg").read_text(encoding="utf-8")
    site_text = (ROOT / "docs/site-data.json").read_text(encoding="utf-8")
    site = json.loads(site_text)
    help_text = (ROOT / "help/index.html").read_text(encoding="utf-8")
    drift = json.loads((ROOT / "documentation-drift-report.json").read_text(encoding="utf-8"))
    drift_md = (ROOT / "documentation-drift-report.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")

    require(
        f"Current verified release: `v{version}`" in readme,
        "README current release differs from the manifest",
    )
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

    require(
        f"Guide for Toolkit v{version}" in help_text,
        "Help Centre version differs from the manifest",
    )
    require(
        "live Mission Requirements matrix" not in help_text,
        "Help Centre still advertises the retired matrix wording",
    )
    require(drift["userscriptVersion"] == version, "documentation drift JSON version is stale")
    require(
        drift["versionState"] == "current-production",
        "documentation drift JSON does not describe current production",
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

    print(
        f"Documentation consistency passed for Toolkit {version}: "
        "README, hero, site data, Help Centre and drift evidence agree."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
