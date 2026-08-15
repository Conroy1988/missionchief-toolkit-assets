#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("toolkit_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def expect_briefing_failure(validator, source: str, version: str) -> None:
    try:
        validator.validate_release_briefing(source, version)
    except SystemExit as error:
        assert "RELEASE_BRIEFING" in str(error)
    else:
        raise AssertionError("release briefing drift was accepted")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.8.0"

    validator = load_validator()
    validator.validate_release_briefing(source, metadata.group(1))
    expect_briefing_failure(
        validator,
        source.replace('version: "10.8.0"', 'version: "10.4.1"', 1),
        metadata.group(1),
    )
    expect_briefing_failure(
        validator,
        source.replace(
            "Adds a dedicated Dispatch administration section for recruitment changes across one selected Dispatch Centre.",
            "This deliberately stale highlight must fail validation.",
            1,
        ),
        metadata.group(1),
    )

    briefing = section(source, "    function updateBriefingBody(", "    function sessionCleanupSpawnLayers(")
    for required in [
        "RELEASE_BRIEFING.highlights.map",
        "escapeHtml(RELEASE_BRIEFING.title)",
        'data-mcms-command-action="open-release-notes"',
        "What’s New & Feature Beacon · v",
        "openToolkitReleaseNotes",
        "releases/tag/v",
    ]:
        assert required in briefing, required
    for stale in [
        "review every v10.2 feature",
        "Cleaner mission map and Alliance Chat",
        "Unit Locator &amp; Follow",
        "Session Cleanup</b>",
    ]:
        assert stale not in briefing, stale
    for forbidden in ["runtimeSetTimeout(", "runtimeSetInterval(", "MutationObserver", "GM_xmlhttpRequest(", "fetch("]:
        assert forbidden not in briefing, forbidden

    handler = section(source, "    function handleCommandExperienceAction(", "    function settingsBackupFilename(")
    assert "if (action === 'open-release-notes') { openToolkitReleaseNotes(); return true; }" in handler
    print("Issue #666 static contract passed: installed release notes and changelog are fail-closed against drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
