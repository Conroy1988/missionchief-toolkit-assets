#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/main-style-source-headroom.json"


def fail(message: str) -> None:
    raise SystemExit(f"MAIN STYLE HEADROOM CONTRACT ERROR: {message}")


def standalone_comment_ranges(lines: list[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
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
            ranges.append((start, end))
        index = end + 1
    return ranges


def canonical_css_formatting(raw: str) -> str:
    lines = raw.split("\n")
    removable = {index for index in range(1, len(lines) - 1) if not lines[index].strip()}
    for start, end in standalone_comment_ranges(lines):
        removable.update(range(start, end + 1))
    stripped = "\n".join(line for index, line in enumerate(lines) if index not in removable)
    return re.sub(r"\n[\t ]*}", "}", stripped)


def userscript_version(text: str) -> str:
    match = re.search(r"^//\s*@version\s+([^\s]+)", text, re.MULTILINE)
    if not match:
        fail("userscript version is missing")
    return match.group(1)


def extract_main_style(text: str) -> str:
    function_start = text.find("function installMainStyles()")
    if function_start < 0:
        fail("installMainStyles function is missing")
    add_style = text.find("addStyle(`", function_start)
    if add_style < 0:
        fail("installMainStyles addStyle template opening is missing")
    template_start = add_style + len("addStyle(`")
    end_anchor = text.find("recordStartupMetric('stylesheetInstallMs'", template_start)
    if end_anchor < 0:
        fail("installMainStyles startup metric anchor is missing")
    closing = text.rfind("`);", template_start, end_anchor)
    if closing < 0:
        fail("installMainStyles addStyle template closing is missing")
    return text[template_start:closing]


def validate_template_shape(raw: str) -> tuple[list[str], str, str]:
    lines = raw.split("\n")
    interior_blank = [index + 1 for index, line in enumerate(lines[1:-1], 1) if not line.strip()]
    if interior_blank:
        fail(f"blank physical lines returned inside installMainStyles: {interior_blank[:10]}")
    comments = standalone_comment_ranges(lines)
    if comments:
        fail(f"standalone full-line CSS comments returned inside installMainStyles: {comments[:5]}")
    template_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    canonical_hash = hashlib.sha256(canonical_css_formatting(raw).encode("utf-8")).hexdigest()
    return lines, template_hash, canonical_hash


def validate_v5(fixture: dict, text: str, raw: str, lines: list[str], template_hash: str, canonical_hash: str) -> None:
    if len(raw.encode("utf-8")) <= 800000:
        fail("reviewed v5 main stylesheet template is unexpectedly small")
    if template_hash != fixture["candidateTemplateSha256"]:
        fail("exact v5 candidate stylesheet template differs from the reviewed fixture")
    if canonical_hash != fixture["canonicalCssSha256"]:
        fail("canonical v5 CSS content differs from the reviewed fixture")
    if len(lines) != fixture["candidateTemplateLines"]:
        fail("v5 candidate stylesheet template line count differs from the reviewed fixture")

    split_lines = re.split(r"\r?\n", text)
    source_lines = len(split_lines) - 1 if text.endswith("\n") else len(split_lines)
    approved_changes = fixture.get("approvedNonStyleChanges", [])
    if not isinstance(approved_changes, list):
        fail("approved non-style source changes must be a list")
    approved_total = 0
    for change in approved_changes:
        if not isinstance(change, dict):
            fail("approved non-style source change entries must be objects")
        issue = change.get("issue")
        phase = str(change.get("phase") or "").strip()
        change_lines = change.get("lines")
        net_delta = change.get("netPhysicalDelta") is True and issue == 464 and phase == "complete-launcher-settings-operational-runtime-and-mission-age-recovery"
        if not isinstance(issue, int) or issue <= 0 or not phase or not isinstance(change_lines, int) or (change_lines < 0 and not net_delta):
            fail("approved non-style source change entry is malformed")
        approved_total += change_lines
    if approved_total != fixture.get("approvedNonStyleSourceLines", 0):
        fail("approved non-style source-line ledger total is inconsistent")
    retired_total = fixture.get("retiredNonStyleSourceLines", 0)
    if not isinstance(retired_total, int) or retired_total < 0:
        fail("retired non-style source-line total is malformed")
    expected_source_lines = fixture["candidateSourceLines"] + approved_total - retired_total
    if fixture.get("expectedSourceLines", expected_source_lines) != expected_source_lines:
        fail("expected source line count is inconsistent with the approved non-style ledger")
    if source_lines != expected_source_lines:
        fail(f"v5 candidate source line count changed: {source_lines} != {expected_source_lines}")
    if fixture["originalSourceLines"] - fixture["candidateSourceLines"] != fixture["recoveredSourceLines"]:
        fail("fixture source-line arithmetic is inconsistent")
    if fixture["removedBlankLines"] + fixture["removedStandaloneCommentLines"] + fixture["joinedClosingBraceLines"] != fixture["recoveredSourceLines"]:
        fail("fixture formatting-category arithmetic is inconsistent")
    if fixture["joinedClosingBraceLines"] != 15:
        fail("reviewed closing-brace join count changed")
    if fixture["recoveredSourceLines"] < 500:
        fail("reviewed implementation recovered fewer than 500 lines")


def validate_v6(profile: dict, text: str, raw: str, lines: list[str], template_hash: str, canonical_hash: str) -> None:
    source_bytes = len(text.encode("utf-8"))
    source_lines = len(text.splitlines())
    source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    template_bytes = len(raw.encode("utf-8"))

    expected = {
        "sourceBytes": source_bytes,
        "sourceLines": source_lines,
        "sourceSha256": source_hash,
        "templateBytes": template_bytes,
        "templateLines": len(lines),
        "templateSha256": template_hash,
        "canonicalCssSha256": canonical_hash,
    }
    mismatches = [f"{key}: {actual!r} != {profile.get(key)!r}" for key, actual in expected.items() if actual != profile.get(key)]
    if mismatches:
        fail("v6 exact source/style profile changed: " + "; ".join(mismatches))
    if source_bytes > profile["maxSourceBytes"]:
        fail("v6 source exceeded the reviewed maximum byte budget")
    if template_bytes < profile["minTemplateBytes"]:
        fail("v6 stylesheet fell below the reviewed remaining-style floor")
    retired = profile.get("retiredSystems")
    if not isinstance(retired, list) or len(retired) != 5:
        fail("v6 retired-system ledger is malformed")


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    text = SOURCE.read_text(encoding="utf-8")
    version = userscript_version(text)
    raw = extract_main_style(text)
    lines, template_hash, canonical_hash = validate_template_shape(raw)

    if version == fixture.get("candidateVersion"):
        validate_v5(fixture, text, raw, lines, template_hash, canonical_hash)
        print(
            "Main-style source-headroom contract passed for v5: "
            f"{fixture['recoveredSourceLines']} lines recovered and "
            f"{fixture['candidateSourceLines']} source lines remain."
        )
        return 0

    profile = fixture.get("v6Candidate")
    if isinstance(profile, dict) and version == profile.get("version"):
        validate_v6(profile, text, raw, lines, template_hash, canonical_hash)
        print(
            "Main-style source-headroom contract passed for v6: "
            f"{profile['sourceBytes']} source bytes, {profile['sourceLines']} source lines, "
            f"{profile['templateBytes']} stylesheet bytes and exact reviewed hashes."
        )
        return 0

    fail(f"unsupported userscript version: {version}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
