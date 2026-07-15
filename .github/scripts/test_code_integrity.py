#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_code_integrity.py")
spec = importlib.util.spec_from_file_location("check_code_integrity", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def userscript(
    body: str,
    *,
    version: str = "1.0.0",
    extra_meta: str = "",
) -> str:
    return f"""// ==UserScript==
// @name MissionChief Map Command Toolkit
// @version {version}
// @author Conroy1988
// @license MIT
// @run-at document-start
// @match https://www.missionchief.co.uk/*
{extra_meta}// ==/UserScript==
{body}
"""


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def policy() -> dict:
    return {
        "metadata": {
            "requiredSingle": [
                "name",
                "version",
                "author",
                "license",
                "run-at",
            ],
            "contains": {
                "name": "MissionChief Map Command Toolkit",
                "author": "Conroy1988",
                "license": "MIT",
            },
            "exact": {"run-at": "document-start"},
            "requiredHost": "missionchief.co.uk",
        },
        "duplicateIds": {"failWithoutBaseline": False, "allow": []},
        "shortcuts": {"failWithoutBaseline": False, "allow": []},
        "repository": {
            "textExtensions": [".js", ".txt", ".md"],
            "textFileNames": [],
            "excludedPrefixes": [],
            "maxTextFileBytes": 5_000_000,
        },
        "secrets": {"excludedPaths": []},
        "assets": {
            "sameRepository": "Conroy1988/missionchief-toolkit-assets",
            "allowedHttpHosts": ["localhost"],
        },
    }


def finding_codes(report: dict) -> set[str]:
    return {item["code"] for item in report["findings"]}


def run_case(
    candidate_text: str,
    base_text: str | None = None,
    extra_files: dict[str, str] | None = None,
) -> tuple[dict, int]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "src").mkdir()
        candidate = write(
            root / "src" / "candidate.user.js",
            candidate_text,
        )
        base = (
            write(root / "src" / "base.user.js", base_text)
            if base_text is not None
            else None
        )
        for name, content in (extra_files or {}).items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            write(target, content)
        return module.build_report(candidate, base, policy(), root)


def test_valid_fixture() -> None:
    candidate = userscript(
        "document.addEventListener('keydown', (event) => { "
        "if (event.key === 'v') openPanel(); });\n"
        "const el = document.createElement('div'); "
        "el.id = 'mcms-panel';\n"
        "document.querySelector('.mission-list');"
    )
    report, status = run_case(candidate, candidate)
    assert status == 0, report


def test_new_duplicate_id() -> None:
    base = userscript(
        "const a = document.createElement('div'); "
        "a.id = 'mcms-panel';"
    )
    candidate = userscript(
        "const a = document.createElement('div'); "
        "a.id = 'mcms-panel'; "
        "const b = document.createElement('div'); "
        "b.id = 'mcms-panel';"
    )
    report, status = run_case(candidate, base)
    assert status == 1
    assert finding_codes(report) & {
        "new-interface-id",
        "increased-interface-id",
    }, report


def test_new_shortcut_conflict() -> None:
    base = userscript(
        "document.addEventListener('keydown', (event) => { "
        "if (event.key === 'v') openPanel(); });"
    )
    candidate = userscript(
        "document.addEventListener('keydown', (event) => { "
        "if (event.key === 'v') openPanel(); "
        "if (event.key === 'v') openOther(); });"
    )
    report, status = run_case(candidate, base)
    assert status == 1
    assert "new-shortcut-conflict" in finding_codes(report), report


def test_malformed_selector() -> None:
    candidate = userscript("document.querySelector('div[');")
    report, status = run_case(candidate, candidate)
    assert status == 1
    assert "malformed-static-selector" in finding_codes(report), report


def test_duplicate_metadata() -> None:
    candidate = userscript(
        "void 0;",
        extra_meta="// @version 9.9.9\n",
    )
    report, status = run_case(candidate, candidate)
    assert status == 1
    assert "metadata-cardinality" in finding_codes(report), report


def test_merge_marker() -> None:
    candidate = userscript("void 0;")
    report, status = run_case(
        candidate,
        candidate,
        {
            "notes.txt": (
                "<<<<<<< HEAD\n"
                "left\n"
                "=======\n"
                "right\n"
                ">>>>>>> branch\n"
            )
        },
    )
    assert status == 1
    assert "merge-conflict-marker" in finding_codes(report), report


def test_secret_detection() -> None:
    candidate = userscript("void 0;")
    secret = (
        "https://discord.com/api/"
        + "webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyzABCDE"
    )
    report, status = run_case(
        candidate,
        candidate,
        {"config.txt": secret},
    )
    assert status == 1
    assert "exposed-secret" in finding_codes(report), report


def main() -> None:
    tests = [
        test_valid_fixture,
        test_new_duplicate_id,
        test_new_shortcut_conflict,
        test_malformed_selector,
        test_duplicate_metadata,
        test_merge_marker,
        test_secret_detection,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"All {len(tests)} code-integrity tests passed.")


if __name__ == "__main__":
    main()
