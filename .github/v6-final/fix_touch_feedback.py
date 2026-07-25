#!/usr/bin/env python3
"""Restore retained touch feedback and refresh exact v6 source/style evidence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
STYLE_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
EVIDENCE = ROOT / "docs" / "audits" / "v6-critical-performance-evidence.json"
BASELINE = ROOT / "docs" / "audits" / "v6-critical-performance-baseline.md"

TOUCH_TOKEN = "filter:brightness(1.16) saturate(1.06)!important;opacity:.88!important"
TOUCH_RULE = (
    'html:is([data-mcms-mobile-active="true"],[data-mcms-tablet-active="true"]) '
    ':is(#${SCRIPT.controlId},#${SCRIPT.panelId},#${SCRIPT.vehicleStatusId},#${SCRIPT.majorIncidentFeedId}) '
    ':is(button,[role="button"]){-webkit-touch-callout:none!important;touch-action:manipulation!important}'
    'html:is([data-mcms-mobile-active="true"],[data-mcms-tablet-active="true"]) '
    ':is(#${SCRIPT.controlId},#${SCRIPT.panelId},#${SCRIPT.vehicleStatusId},#${SCRIPT.majorIncidentFeedId}) '
    f':is(button,[role="button"]):active{{{TOUCH_TOKEN}}}'
)
ANCHOR = (
    'html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn '
    '{flex:0 0 auto!important;width:auto!important;min-width:88px!important;height:44px!important;'
    'min-height:44px!important;padding:0 11px!important;font-size:10px!important;scroll-snap-align:start!important}'
)


def canonical_css_formatting(raw: str) -> str:
    lines = raw.split("\n")
    removable = {index for index in range(1, len(lines) - 1) if not lines[index].strip()}
    index = 1
    while index < len(lines) - 1:
        stripped = lines[index].strip()
        if not stripped.startswith("/*"):
            index += 1
            continue
        start = index
        end = index
        valid = "${" not in lines[index]
        remainder = stripped[2:]
        if "*/" in remainder:
            valid = valid and not remainder.split("*/", 1)[1].strip()
        else:
            found = False
            cursor = index + 1
            while cursor < len(lines) - 1:
                end = cursor
                if "${" in lines[cursor]:
                    valid = False
                if "*/" in lines[cursor]:
                    valid = valid and not lines[cursor].split("*/", 1)[1].strip()
                    found = True
                    break
                cursor += 1
            if not found:
                valid = False
        if valid:
            removable.update(range(start, end + 1))
        index = end + 1
    stripped = "\n".join(line for line_index, line in enumerate(lines) if line_index not in removable)
    return re.sub(r"\n[\t ]*}", "}", stripped)


def extract_main_style(source: str) -> str:
    function_start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", function_start) + len("addStyle(`")
    end_anchor = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, end_anchor)
    if template_end < 0:
        raise SystemExit("installMainStyles template closing was not found")
    return source[template_start:template_end]


def signed(value: int) -> str:
    return f"−{abs(value):,}" if value < 0 else f"+{value:,}"


def signed_pct(value: float) -> str:
    return f"−{abs(value):.1f}%" if value < 0 else f"+{value:.1f}%"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    if TOUCH_TOKEN not in source:
        if source.count(ANCHOR) != 1:
            raise SystemExit(f"Expected one mobile tab geometry anchor, found {source.count(ANCHOR)}")
        source = source.replace(ANCHOR, ANCHOR + TOUCH_RULE, 1)
        SOURCE.write_text(source, encoding="utf-8")
    if source.count(TOUCH_TOKEN) != 1:
        raise SystemExit(f"Expected one retained touch-feedback rule, found {source.count(TOUCH_TOKEN)}")
    if "#${SCRIPT.criticalDrawerId}" in TOUCH_RULE:
        raise SystemExit("Retired Critical View ownership returned to the touch rule")

    raw = SOURCE.read_bytes()
    source = raw.decode("utf-8")
    source_sha = hashlib.sha256(raw).hexdigest()
    source_bytes = len(raw)
    source_profile_lines = len(source.splitlines())
    source_physical_lines = source.count("\n") + 1
    template = extract_main_style(source)
    template_bytes = len(template.encode("utf-8"))
    template_lines = len(template.split("\n"))
    template_sha = hashlib.sha256(template.encode("utf-8")).hexdigest()
    canonical_sha = hashlib.sha256(canonical_css_formatting(template).encode("utf-8")).hexdigest()

    fixture = json.loads(STYLE_FIXTURE.read_text(encoding="utf-8"))
    profile = fixture["v6Candidate"]
    profile.update({
        "sourceBytes": source_bytes,
        "sourceLines": source_profile_lines,
        "sourceSha256": source_sha,
        "templateBytes": template_bytes,
        "templateLines": template_lines,
        "templateSha256": template_sha,
        "canonicalCssSha256": canonical_sha,
    })
    STYLE_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    evidence["candidate"].update({"sha256": source_sha, "bytes": source_bytes, "lines": source_physical_lines})
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    baseline_bytes = 2_060_765
    baseline_lines = 31_761
    byte_delta = source_bytes - baseline_bytes
    line_delta = source_physical_lines - baseline_lines
    baseline = BASELINE.read_text(encoding="utf-8")
    baseline = re.sub(
        r"(?m)^\*\*Candidate canonical SHA-256:\*\* `[^`]+`\s*$",
        f"**Candidate canonical SHA-256:** `{source_sha}`  ",
        baseline,
    )
    baseline = re.sub(
        r"(?m)^\| Source bytes \| 2,060,765 \| [^|]+ \|.*$",
        f"| Source bytes | 2,060,765 | {source_bytes:,} | {signed(byte_delta)} ({signed_pct(byte_delta / baseline_bytes * 100)}) |",
        baseline,
    )
    baseline = re.sub(
        r"(?m)^\| Source lines \| 31,761 \| [^|]+ \|.*$",
        f"| Source lines | 31,761 | {source_physical_lines:,} | {signed(line_delta)} ({signed_pct(line_delta / baseline_lines * 100)}) |",
        baseline,
    )
    BASELINE.write_text(baseline, encoding="utf-8")

    print(json.dumps({
        "sourceSha256": source_sha,
        "sourceBytes": source_bytes,
        "sourceProfileLines": source_profile_lines,
        "sourcePhysicalLines": source_physical_lines,
        "templateBytes": template_bytes,
        "templateLines": template_lines,
        "templateSha256": template_sha,
        "canonicalCssSha256": canonical_sha,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
