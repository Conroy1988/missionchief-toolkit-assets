#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPACTOR = ROOT / ".github/development-packages/issue-253-main-style-compaction.mjs"
INVENTORY_SCRIPT = ROOT / ".github/development-packages/issue-253-source-headroom-inventory.mjs"
CONTRACT = ROOT / ".github/scripts/test_main_style_source_headroom.py"
VALIDATOR = ROOT / ".github/scripts/validate_userscript.py"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
DOC = ROOT / "docs/issue-253-main-style-source-headroom.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run(
        ["npm", "install", "--no-save", "--ignore-scripts", "--no-audit", "--no-fund", "acorn@8.15.0"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    try:
        subprocess.run(["node", "--check", str(COMPACTOR)], cwd=ROOT, env=env, check=True)
        subprocess.run(["node", str(COMPACTOR)], cwd=ROOT, env=env, check=True)

        CONTRACT.write_text(
            r'''#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/main-style-source-headroom.json"
ASSIGNMENT = "style.textContent = `"


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


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    text = SOURCE.read_text(encoding="utf-8")
    function_start = text.find("function installMainStyles()")
    if function_start < 0:
        fail("installMainStyles function is missing")
    assignment = text.find(ASSIGNMENT, function_start)
    if assignment < 0:
        fail("main style.textContent assignment is missing")
    template_start = assignment + len(ASSIGNMENT)
    closing = text.find("`;", template_start)
    if closing < 0:
        fail("main style template closing delimiter is missing")
    raw = text[template_start:closing]
    lines = raw.split("\n")
    interior_blank = [index + 1 for index, line in enumerate(lines[1:-1], 1) if not line.strip()]
    if interior_blank:
        fail(f"blank physical lines returned inside installMainStyles: {interior_blank[:10]}")
    comments = standalone_comment_ranges(lines)
    if comments:
        fail(f"standalone full-line CSS comments returned inside installMainStyles: {comments[:5]}")
    semantic_lines = list(lines)
    digest = hashlib.sha256("\n".join(semantic_lines).encode("utf-8")).hexdigest()
    if digest != fixture["semanticLinesSha256"]:
        fail("ordered non-formatting stylesheet lines differ from the reviewed fixture")
    if len(semantic_lines) != fixture["semanticLineCount"]:
        fail("semantic stylesheet line count differs from the reviewed fixture")
    source_lines = text.count("\n") + 1
    if source_lines != fixture["candidateSourceLines"]:
        fail(f"candidate source line count changed: {source_lines} != {fixture['candidateSourceLines']}")
    if fixture["originalSourceLines"] - fixture["candidateSourceLines"] != fixture["recoveredSourceLines"]:
        fail("fixture source-line arithmetic is inconsistent")
    if fixture["removedBlankLines"] + fixture["removedStandaloneCommentLines"] != fixture["recoveredSourceLines"]:
        fail("fixture formatting-category arithmetic is inconsistent")
    if fixture["recoveredSourceLines"] < 500:
        fail("reviewed implementation recovered fewer than 500 lines")
    version = re.search(r"^//\s*@version\s+([^\s]+)", text, re.MULTILINE)
    if not version or version.group(1) != fixture["candidateVersion"]:
        fail("userscript version does not match the reviewed source-headroom fixture")
    print(
        "Main-style source-headroom contract passed: "
        f"{fixture['recoveredSourceLines']} lines recovered "
        f"({fixture['removedBlankLines']} blank, "
        f"{fixture['removedStandaloneCommentLines']} standalone comment), "
        f"{fixture['candidateSourceLines']} source lines remain."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
            encoding="utf-8",
        )

        validator = VALIDATOR.read_text(encoding="utf-8")
        validator = replace_once(
            validator,
            'VERSION_STATUS_CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"\n',
            'VERSION_STATUS_CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"\nMAIN_STYLE_HEADROOM_CONTRACT = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"\n',
            "validator contract constant",
        )
        validator = replace_once(
            validator,
            'required = [INTEGRITY_AUDITOR, INTEGRITY_POLICY, ASSET_AUDITOR, AUDIO_ALIAS_AUDITOR, MISSION_REQUIREMENTS_CONTRACT, VERSION_STATUS_CONTRACT]',
            'required = [INTEGRITY_AUDITOR, INTEGRITY_POLICY, ASSET_AUDITOR, AUDIO_ALIAS_AUDITOR, MISSION_REQUIREMENTS_CONTRACT, VERSION_STATUS_CONTRACT, MAIN_STYLE_HEADROOM_CONTRACT]',
            "validator required contracts",
        )
        validator = replace_once(
            validator,
            '''        version_status = subprocess.run(
            [sys.executable, str(VERSION_STATUS_CONTRACT)],
            cwd=ROOT,
        )
        if version_status.returncode != 0:
            fail("live version-status contract failed")
''',
            '''        version_status = subprocess.run(
            [sys.executable, str(VERSION_STATUS_CONTRACT)],
            cwd=ROOT,
        )
        if version_status.returncode != 0:
            fail("live version-status contract failed")

        main_style_headroom = subprocess.run(
            [sys.executable, str(MAIN_STYLE_HEADROOM_CONTRACT)],
            cwd=ROOT,
        )
        if main_style_headroom.returncode != 0:
            fail("main-style source-headroom contract failed")
''',
            "validator contract execution",
        )
        VALIDATOR.write_text(validator, encoding="utf-8")

        preflight = PREFLIGHT.read_text(encoding="utf-8")
        preflight = replace_once(
            preflight,
            '  .github/scripts/test_root_attribute_write_suppression_contract.py\n',
            '  .github/scripts/test_root_attribute_write_suppression_contract.py\n  .github/scripts/test_main_style_source_headroom.py\n',
            "preflight contract list",
        )
        PREFLIGHT.write_text(preflight, encoding="utf-8")

        changelog = CHANGELOG.read_text(encoding="utf-8")
        entry = '''## [4.20.21] - 2026-07-21

### Engineering
- Recovered source headroom by removing only blank physical lines and standalone full-line CSS comments from the existing `installMainStyles` template.
- Preserved every ordered selector, declaration, interpolation, inline comment and rule line byte-for-byte, including cascade order.
- Added a permanent fixture and validation contract for the reviewed stylesheet source sequence, formatting categories and recovered-line target.
- Published the Issue #253 structural inventory and rollback boundary.

'''
        changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog entry")
        CHANGELOG.write_text(changelog, encoding="utf-8")

        help_text = HELP.read_text(encoding="utf-8")
        help_text = replace_once(help_text, "Guide for Toolkit v4.20.20", "Guide for Toolkit v4.20.21", "help version")
        HELP.write_text(help_text, encoding="utf-8")

        DOC.write_text(
            '''# Issue #253 — main stylesheet source headroom

Toolkit v4.20.21 creates maintainable source headroom without changing stylesheet behavior.

## Bounded change

Only standalone source formatting inside the existing `installMainStyles` template is removed: blank physical lines and full-line CSS comment blocks. Every ordered selector, declaration, interpolation, inline comment and rule line remains byte-for-byte identical. The change does not group selectors, consolidate declarations, reorder rules, alter interpolation expressions, defer installation, or change specificity and cascade order.

CSS comments removed by this change occupy complete lines and contain no interpolation. They are parser-ignored documentation rather than selectors or declarations. Adjacent retained lines remain separated by a newline.

No observer, scheduler, network, state, storage or lifecycle code is changed.

## Deterministic proof

`.github/fixtures/main-style-source-headroom.json` records:

- original and candidate source line counts;
- exact recovered line count by blank-line and standalone-comment category;
- original and candidate template line counts;
- semantic stylesheet line count;
- SHA-256 of every ordered non-formatting stylesheet line.

`test_main_style_source_headroom.py` is executed by canonical validation and the shared userscript preflight. It rejects returned removable formatting, altered CSS source, inconsistent line arithmetic, a recovery below 500 lines or version drift.

## Excluded work

This change does not implement the higher-risk stylesheet modularisation work in Issues #63 or #254. Style delivery, selector grouping, visual themes, first paint and responsive behavior remain structurally unchanged.

## Rollback

Revert the single Issue #253 implementation commit. The change introduces no persistent data migration or external dependency.
''',
            encoding="utf-8",
        )

        cleanup_paths = (
            INVENTORY_SCRIPT,
            COMPACTOR,
            ROOT / ".github/development-packages/issue-253-style-formatting-inventory.py",
            ROOT / "docs/issue-253-main-style-package-diagnostic.txt",
            ROOT / "docs/issue-253-style-formatting-diagnostic.txt",
            ROOT / "docs/issue-253-style-formatting-inventory.json",
        )
        for path in cleanup_paths:
            path.unlink(missing_ok=True)

        subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, env=env, check=True)
        subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, env=env, check=True)
        subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=env, check=True)
        subprocess.run(["bash", str(PREFLIGHT), "--contracts"], cwd=ROOT, env=env, check=True)
        with tempfile.TemporaryDirectory(prefix="issue-253-audit-") as temp:
            temp_path = Path(temp)
            subprocess.run(
                [
                    "node",
                    ".github/scripts/deep_performance_audit.mjs",
                    "--source",
                    "src/MissionChief_Map_Command_Toolkit.user.js",
                    "--json-output",
                    str(temp_path / "deep.json"),
                    "--markdown-output",
                    str(temp_path / "deep.md"),
                ],
                cwd=ROOT,
                env=env,
                check=True,
            )
            subprocess.run(
                [
                    "python3",
                    ".github/scripts/full_userscript_audit.py",
                    "--json-output",
                    str(temp_path / "full.json"),
                    "--markdown-output",
                    str(temp_path / "full.md"),
                ],
                cwd=ROOT,
                env=env,
                check=True,
            )
        subprocess.run(["git", "diff", "--check"], cwd=ROOT, env=env, check=True)
    finally:
        shutil.rmtree(ROOT / "node_modules", ignore_errors=True)
        (ROOT / "package-lock.json").unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
