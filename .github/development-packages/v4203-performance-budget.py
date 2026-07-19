#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DASHBOARD = ROOT / "status" / "release-dashboard.json"
MANIFEST = ROOT / "dist" / "release-manifest.json"
DIAGNOSTIC = ROOT / ".github" / "workflows" / "v4203-performance-diagnostic.yml"

FUNCTIONS = [
    ("missionRequirementsVehicleType", "missionRequirementsVehicleId"),
    ("missionRequirementsCapabilityLabel", "missionRequirementsMetadataValues"),
    ("missionRequirementsMetadataValues", "missionRequirementsDefinitionTokens"),
    ("missionRequirementsDefinitionTokens", "missionRequirementsDefinitionMatchesValues"),
    ("missionRequirementsDefinitionMatchesValues", "missionRequirementsKnownDefinitionKeys"),
    ("missionRequirementsKnownDefinitionKeys", "missionRequirementsStaffCapacity"),
    ("missionRequirementsStaffCapacity", "missionRequirementsOperationalSelectors"),
    ("missionRequirementsOperationalSelectors", "missionRequirementsOperationalElementActive"),
    ("missionRequirementsOperationalElementActive", "missionRequirementsCollectUnits"),
    ("missionRequirementsCollectUnits", "missionRequirementsMissionTypeId"),
    ("missionRequirementsUnitContribution", "missionRequirementsAggregate"),
    ("missionRequirementsAggregate", "missionRequirementsProgressValue"),
    ("missionRequirementsCataloguePersonnelRequirements", "missionRequirementsCatalogueMergeRequirement"),
    ("missionRequirementsCatalogueMergeRequirement", "missionRequirementsCatalogueParseDocument"),
    ("missionRequirementsCatalogueParseDocument", "missionRequirementsCataloguePrune"),
]

WORD = re.compile(r"[A-Za-z0-9_$]")
REGEX_KEYWORDS = {"return", "throw", "case", "delete", "void", "typeof", "new", "in", "of", "yield", "await"}
DANGEROUS_PAIRS = {"++", "--", "//", "/*", "<<", ">>", "<=", ">=", "==", "!=", "&&", "||", "??", "**", "=>"}


def needs_space(previous: str, following: str, last_word: str) -> bool:
    if not previous or not following:
        return False
    if WORD.fullmatch(previous) and WORD.fullmatch(following):
        return True
    if previous + following in DANGEROUS_PAIRS:
        return True
    if previous.isdigit() and following == ".":
        return True
    if previous == "." and following.isdigit():
        return True
    if following == "/" and last_word in REGEX_KEYWORDS:
        return True
    return False


def regex_start(previous: str, last_word: str) -> bool:
    return not previous or previous in "([{:;,=!?&|+-*%^~<>" or last_word in REGEX_KEYWORDS


def minify_whitespace(code: str) -> str:
    output: list[str] = []
    index = 0
    length = len(code)
    last_word = ""
    while index < length:
        char = code[index]
        if char in "'\"`":
            quote = char
            output.append(char)
            index += 1
            escaped = False
            while index < length:
                current = code[index]
                output.append(current)
                index += 1
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == quote:
                    break
            last_word = ""
            continue
        if char == "/" and index + 1 < length and code[index + 1] in "/*":
            if code[index + 1] == "/":
                end = code.find("\n", index + 2)
                if end < 0:
                    break
                index = end
                continue
            end = code.find("*/", index + 2)
            if end < 0:
                raise AssertionError("unterminated block comment in compacted Matrix function")
            index = end + 2
            continue
        if char == "/":
            previous = next((item for item in reversed(output) if not item.isspace()), "")
            if regex_start(previous, last_word):
                output.append(char)
                index += 1
                escaped = False
                character_class = False
                while index < length:
                    current = code[index]
                    output.append(current)
                    index += 1
                    if escaped:
                        escaped = False
                        continue
                    if current == "\\":
                        escaped = True
                        continue
                    if current == "[":
                        character_class = True
                    elif current == "]":
                        character_class = False
                    elif current == "/" and not character_class:
                        while index < length and code[index].isalpha():
                            output.append(code[index])
                            index += 1
                        break
                last_word = ""
                continue
        if char.isspace():
            while index < length and code[index].isspace():
                index += 1
            following = code[index] if index < length else ""
            previous = next((item for item in reversed(output) if not item.isspace()), "")
            if needs_space(previous, following, last_word):
                output.append(" ")
            continue
        if char.isalpha() or char in "_$":
            start = index
            index += 1
            while index < length and (code[index].isalnum() or code[index] in "_$"):
                index += 1
            token = code[start:index]
            output.append(token)
            last_word = token
            continue
        output.append(char)
        if char != ".":
            last_word = ""
        index += 1
    return "".join(output)


def compact_functions(source: str) -> tuple[str, int]:
    original_size = len(source.encode("utf-8"))
    for name, next_name in FUNCTIONS:
        marker = f"function {name}"
        next_marker = f"function {next_name}"
        if source.count(marker) != 1:
            raise AssertionError(f"{name}: expected exactly one active function declaration")
        start = source.index(marker)
        end = source.index(next_marker, start)
        block = source[start:end]
        compacted = minify_whitespace(block).strip()
        source = source[:start] + compacted + "\n" + source[end:]
    final_size = len(source.encode("utf-8"))
    return source, original_size - final_size


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


source = SOURCE.read_text(encoding="utf-8")
compacted, saved = compact_functions(source)
if saved < 2100:
    raise AssertionError(f"Matrix compaction saved only {saved} bytes; expected at least 2100")
SOURCE.write_text(compacted, encoding="utf-8")

run(["node", "--check", str(SOURCE.relative_to(ROOT))])
run(["node", ".github/scripts/test_mission_requirements_runtime.js"])
run([sys.executable, ".github/scripts/test_mission_requirements_contract.py"])
run([sys.executable, ".github/scripts/validate_userscript.py"])

source_bytes = SOURCE.stat().st_size
if source_bytes > 1_999_900:
    raise AssertionError(f"v4.20.3 source remains above safe release ceiling: {source_bytes} bytes")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
if manifest.get("version") != "4.20.3":
    raise AssertionError("rebuilt distribution manifest is not v4.20.3")
sha256 = str(manifest.get("sha256") or "")
if not re.fullmatch(r"[0-9a-f]{64}", sha256):
    raise AssertionError("rebuilt v4.20.3 SHA-256 is invalid")

dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
dashboard["currentVersion"] = "4.20.3"
dashboard["status"].update({
    "validation": "passed",
    "githubRelease": "not-published",
    "greasyForkSync": "pending-release",
    "backup": "not-created",
    "discordRelease": "not-posted",
    "assetAudit": "passed",
})
dashboard["source"].update({"validatedSha256": sha256, "state": "validated-canonical-source"})
dashboard["distributionCandidate"].update({"version": "4.20.3", "state": "validated"})
dashboard["lastUpdated"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
DASHBOARD.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
run([sys.executable, ".github/scripts/generate_release_dashboard.py"])

DIAGNOSTIC.unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
print(f"Prepared v4.20.3 performance-safe candidate: saved {saved} bytes, source {source_bytes} bytes, SHA-256 {sha256}")
