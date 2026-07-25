#!/usr/bin/env python3
"""Reconcile v6 preboot declaration order, lifecycle fixtures and source evidence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
BOOT_FIXTURE = ROOT / ".github" / "fixtures" / "boot-lifecycle-contract.json"
STYLE_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
EVIDENCE = ROOT / "docs" / "audits" / "v6-critical-performance-evidence.json"
BASELINE = ROOT / "docs" / "audits" / "v6-critical-performance-baseline.md"

SETTINGS_DECLARATION = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 2;"
SCHEMA_DECLARATION = "    const OPERATIONAL_SETTINGS_SCHEMA = Object.freeze(["
DEFAULT_FUNCTION = "    function defaultOperationalWindowState"
STATE_PATTERN = re.compile(
    r"(?m)^[ \t]*(?:const|let|var)\s+state\s*=\s*loadState\(\);\s*$"
)


def reconcile_preboot_order(source: str) -> str:
    if source.count(SETTINGS_DECLARATION) != 1:
        raise SystemExit("Unexpected Operational Suite settings-version declaration count")
    if source.count(SCHEMA_DECLARATION) != 1:
        raise SystemExit("Unexpected Operational Window schema declaration count")

    state_match = STATE_PATTERN.search(source)
    if state_match is None:
        raise SystemExit("Top-level loadState declaration was not found")

    settings_index = source.index(SETTINGS_DECLARATION)
    schema_index = source.index(SCHEMA_DECLARATION)
    default_index = source.index(DEFAULT_FUNCTION)
    if settings_index < schema_index < state_match.start() < default_index:
        return source

    state_line = state_match.group(0).rstrip()
    source = source[: state_match.start()] + source[state_match.end() :]

    settings_pattern = re.compile(
        rf"(?m)^{re.escape(SETTINGS_DECLARATION)}[ \t]*\r?\n?"
    )
    source, removed = settings_pattern.subn("", source, count=1)
    if removed != 1:
        raise SystemExit("Could not detach the Operational Suite settings-version declaration")

    schema_index = source.index(SCHEMA_DECLARATION)
    default_index = source.index(DEFAULT_FUNCTION, schema_index)
    schema_region = source[schema_index:default_index]
    schema_close = schema_region.rfind("]);")
    if schema_close < 0:
        raise SystemExit("Could not locate the end of the Operational Window schema")
    schema_end = schema_index + schema_close + len("]);")

    source = (
        source[:schema_index]
        + SETTINGS_DECLARATION
        + "\n"
        + source[schema_index:schema_end]
        + "\n"
        + state_line
        + source[schema_end:]
    )

    state_match = STATE_PATTERN.search(source)
    if state_match is None:
        raise SystemExit("Reconciled loadState declaration was not found")
    settings_index = source.index(SETTINGS_DECLARATION)
    schema_index = source.index(SCHEMA_DECLARATION)
    default_index = source.index(DEFAULT_FUNCTION)
    if not settings_index < schema_index < state_match.start() < default_index:
        raise SystemExit("v6 preboot declaration order remains invalid after reconciliation")
    return source


def refresh_source_evidence(raw: bytes) -> None:
    sha256 = hashlib.sha256(raw).hexdigest()
    source_bytes = len(raw)
    source_lines = raw.decode("utf-8").count("\n") + 1

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    candidate = evidence.setdefault("candidate", {})
    candidate["sha256"] = sha256
    candidate["bytes"] = source_bytes
    candidate["lines"] = source_lines
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    fixture = json.loads(STYLE_FIXTURE.read_text(encoding="utf-8"))
    v6 = fixture.setdefault("v6Candidate", {})
    v6["sourceSha256"] = sha256
    v6["sourceBytes"] = source_bytes
    v6["sourceLines"] = source_lines
    STYLE_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    baseline_bytes = 2_060_765
    baseline_lines = 31_761
    byte_delta = source_bytes - baseline_bytes
    line_delta = source_lines - baseline_lines
    byte_pct = byte_delta / baseline_bytes * 100
    line_pct = line_delta / baseline_lines * 100

    def signed(value: int) -> str:
        return f"−{abs(value):,}" if value < 0 else f"+{value:,}"

    def signed_pct(value: float) -> str:
        return f"−{abs(value):.1f}%" if value < 0 else f"+{value:.1f}%"

    baseline = BASELINE.read_text(encoding="utf-8")
    baseline = re.sub(
        r"(?m)^\*\*Candidate canonical SHA-256:\*\* `[^`]+`\s*$",
        f"**Candidate canonical SHA-256:** `{sha256}`  ",
        baseline,
    )
    baseline = re.sub(
        r"(?m)^\| Source bytes \| 2,060,765 \| [^|]+ \|.*$",
        f"| Source bytes | 2,060,765 | {source_bytes:,} | {signed(byte_delta)} ({signed_pct(byte_pct)}) |",
        baseline,
    )
    baseline = re.sub(
        r"(?m)^\| Source lines \| 31,761 \| [^|]+ \|.*$",
        f"| Source lines | 31,761 | {source_lines:,} | {signed(line_delta)} ({signed_pct(line_pct)}) |",
        baseline,
    )
    BASELINE.write_text(baseline, encoding="utf-8")


def reconcile_boot_fixture() -> None:
    data = json.loads(BOOT_FIXTURE.read_text(encoding="utf-8"))
    retired = {
        "data-mcms-critical-view",
        "[data-mcms-critical-view]",
        "auto-night",
        "critical-countdowns",
        "pointerover",
        "pointermove",
        "pointerout",
        "criticalMissionStableCache",
        "clearCoverageHeatmap",
    }
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = [item for item in value if item not in retired]
    BOOT_FIXTURE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source = reconcile_preboot_order(source)
    SOURCE.write_text(source, encoding="utf-8")
    refresh_source_evidence(SOURCE.read_bytes())
    reconcile_boot_fixture()
    print("v6 preboot order, lifecycle fixture and source evidence reconciled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
