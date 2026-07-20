#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
VALIDATOR = ROOT / ".github/scripts/validate_userscript.py"
CONTRACT = ROOT / ".github/scripts/test_root_attribute_write_suppression_contract.py"
TEMPLATE = ROOT / ".github/development-packages/issue-279-root-attribute-contract.template"
DOC = ROOT / "docs/issue-279-root-attribute-write-suppression.md"
OLD = "4.20.17"
NEW = "4.20.18"
CLEANUP = [
    ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression.py",
    ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression-v2.py",
    ROOT / ".github/development-packages/issue-279-root-attribute-write-suppression-v3.py",
    TEMPLATE,
    ROOT / "docs/issue-279-validation-diagnostic.txt",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def function_end(text: str, name: str) -> int:
    start = text.find(f"function {name}(")
    if start < 0:
        raise RuntimeError(f"{name}: function not found")
    opening = text.find("{", start)
    depth = 0
    quote = None
    escaped = False
    index = opening
    while index < len(text):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in "'\"`":
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise RuntimeError(f"{name}: unterminated function")


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, f"// @version      {OLD}", f"// @version      {NEW}", "metadata version")
    source = replace_once(source, f"version: '{OLD}'", f"version: '{NEW}'", "runtime version")

    helper = """    function setAttributeIfChanged(element, name, value) {
        const nextValue = String(value);
        if (element.getAttribute(name) === nextValue) return false;
        element.setAttribute(name, nextValue);
        return true;
    }

"""
    marker = "    function applyRootAttributes() {"
    source = replace_once(source, marker, helper + marker, "helper insertion")
    start = source.index(marker)
    end = function_end(source, "applyRootAttributes")
    block = source[start:end]
    direct_writes = block.count("root.setAttribute(")
    if direct_writes != 22:
        raise RuntimeError(f"applyRootAttributes expected 22 direct writes, found {direct_writes}")
    source = source[:start] + block.replace("root.setAttribute(", "setAttributeIfChanged(root, ") + source[end:]
    SOURCE.write_text(source, encoding="utf-8")

    CONTRACT.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    preflight = replace_once(
        preflight,
        "  .github/scripts/test_settings_ui_contract.py\n",
        "  .github/scripts/test_settings_ui_contract.py\n  .github/scripts/test_root_attribute_write_suppression_contract.py\n",
        "preflight contract registration",
    )
    PREFLIGHT.write_text(preflight, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    entry = f"""## [{NEW}] - 2026-07-21

### Performance
- Root Toolkit state attributes now mutate only when their string value changes, eliminating 22 redundant DOM mutations from unchanged `updateUI()` passes while preserving every calculation and output value.

### Validation
- Added fixture-backed first-write, unchanged-repeat, changed-state, external-repair, layout-orientation and helper return-value regressions against the extracted production functions.

"""
    CHANGELOG.write_text(
        replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog insertion"),
        encoding="utf-8",
    )

    help_text = HELP.read_text(encoding="utf-8")
    HELP.write_text(
        replace_once(help_text, f"Guide for Toolkit v{OLD}", f"Guide for Toolkit v{NEW}", "help version"),
        encoding="utf-8",
    )

    DOC.write_text(
        f"""# Issue 279 — unchanged root-attribute write suppression

Toolkit v{NEW} preserves the complete `applyRootAttributes()` output while avoiding redundant `setAttribute()` calls whose current string value is already correct.

## Safety boundary

- All 22 root attributes remain present and retain their original ordering.
- Device, tablet, mobile and viewport calculations still execute on every call.
- No root node, value snapshot or state cache is retained.
- No observer, timer, animation frame, event listener or network path is added.
- External attribute removal or alteration is repaired on the next invocation.

## Deterministic evidence

The contract extracts the real helper and `applyRootAttributes()` from the canonical userscript and proves 22 initial writes, zero unchanged-repeat writes, selective state updates, external repair and ordered layout/orientation changes.
""",
        encoding="utf-8",
    )

    for path in CLEANUP:
        path.unlink(missing_ok=True)

    # Rebuild source-derived distribution before repository-wide parity contracts run.
    subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)
    print(f"Prepared Toolkit {NEW} root-attribute write-suppression candidate with canonical distribution parity")


if __name__ == "__main__":
    main()
