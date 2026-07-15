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


def userscript(body: str, *, version: str = "1.0.0", extra_meta: str = "") -> str:
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
        "metadata": {"requiredSingle": ["name", "version", "author", "license", "run-at"], "contains": {"name": "MissionChief Map Command Toolkit", "author": "Conroy1988", "license": "MIT"}, "exact": {"run-at": "document-start"}, "requiredHost": "missionchief.co.uk"},
        "duplicateIds": {"failWithoutBaseline": False, "allow": []},
        "shortcuts": {"failWithoutBaseline": False, "allow": []},
        "repository": {"textExtensions": [".js", ".txt", ".md"], "textFileNames": [], "excludedPrefixes": [], "maxTextFileBytes": 5_000_000},
        "secrets": {"excludedPaths": []},
        "assets": {"sameRepository": "Conroy1988/missionchief-toolkit-assets", "allowedHttpHosts": ["localhost"]},
    }


def finding_codes(report: dict) -> set[str]:
    return {item["code"] for item in report["findings"]}


def run_case(candidate_text: str, base_text: str | None = None, extra_files: dict[str, str] | None = None) -> tuple[dict, int]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "src").mkdir()
        candidate = write(root / "src" / "candidate.user.js", candidate_text)
        base = write(root / "src" / "base.user.js", base_text) if base_text is not None else None
        for name, content in (extra_files or {}).items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            write(target, content)
        return module.build_report(candidate, base, policy(), root)


def full_valid_body() -> str:
    return """
const SCRIPT = { panelId: 'mcms-panel' };
function handleKeyboard(event) {
  const key = String(event.key || '').toLowerCase();
  if (key === 'v') { toggleVehicleCodeStatus(); return; }
}
runtimeListen(document, 'keydown', handleKeyboard);
const panel = document.createElement('div');
panel.id = SCRIPT.panelId;
const html = `${makeActionFloatButton('open-vehicle-status', 'V', 'Codes', 'Codes')}`;
document.querySelector('.mission-list');
"""


def test_valid_fixture() -> None:
    candidate = userscript(full_valid_body())
    report, status = run_case(candidate, candidate)
    assert status == 0, report
    assert report["metrics"]["staticIds"] == 1, report
    assert report["metrics"]["shortcutBindings"] >= 2, report


def test_search_string_is_not_dom_id() -> None:
    candidate = userscript("const ok = source.includes('id=\"financial-command\"');")
    report, status = run_case(candidate, candidate)
    assert status == 0, report
    assert report["metrics"]["staticIds"] == 0, report


def test_resolved_script_id_counts() -> None:
    candidate = userscript("const SCRIPT = { panelId: 'mcms-panel' }; const el = document.createElement('div'); el.id = SCRIPT.panelId;")
    report, status = run_case(candidate, candidate)
    assert status == 0, report
    assert [item["value"] for item in report["interfaceIds"]] == ["mcms-panel"], report


def test_new_duplicate_id() -> None:
    base = userscript("const SCRIPT = { panelId: 'mcms-panel' }; const a = document.createElement('div'); a.id = SCRIPT.panelId;")
    candidate = userscript("const SCRIPT = { panelId: 'mcms-panel' }; const a = document.createElement('div'); a.id = SCRIPT.panelId; const b = document.createElement('div'); b.id = SCRIPT.panelId;")
    report, status = run_case(candidate, base)
    assert status == 1
    assert finding_codes(report) & {"new-interface-id", "increased-interface-id"}, report


def test_named_handler_and_visible_shortcut() -> None:
    candidate = userscript(full_valid_body())
    report, status = run_case(candidate, candidate)
    assert status == 0, report
    values = [item["value"] for item in report["shortcutBindings"]]
    assert values.count("v") >= 2, report


def test_new_visible_shortcut_conflict() -> None:
    base = userscript(full_valid_body())
    candidate = userscript(full_valid_body() + "\nconst second = `${makeActionFloatButton('open-other', 'V', 'Other', 'Other')}`;")
    report, status = run_case(candidate, base)
    assert status == 1, report
    assert "new-shortcut-conflict" in finding_codes(report), report


def test_unhandled_visible_shortcut() -> None:
    candidate = userscript("const button = `${makeActionFloatButton('open-other', 'X', 'Other', 'Other')}`;")
    report, status = run_case(candidate, candidate)
    assert status == 1
    assert "unhandled-visible-shortcut" in finding_codes(report), report


def test_malformed_selector() -> None:
    candidate = userscript("document.querySelector('div[');")
    report, status = run_case(candidate, candidate)
    assert status == 1
    assert "malformed-static-selector" in finding_codes(report), report


def test_duplicate_metadata() -> None:
    candidate = userscript("void 0;", extra_meta="// @version 9.9.9\n")
    report, status = run_case(candidate, candidate)
    assert status == 1
    assert "metadata-cardinality" in finding_codes(report), report


def test_merge_marker() -> None:
    candidate = userscript("void 0;")
    report, status = run_case(candidate, candidate, {"notes.txt": "<<<<<<< HEAD\nleft\n=======\nright\n>>>>>>> branch\n"})
    assert status == 1
    assert "merge-conflict-marker" in finding_codes(report), report


def test_secret_detection() -> None:
    candidate = userscript("void 0;")
    secret = "https://discord.com/api/" + "webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyzABCDE"
    report, status = run_case(candidate, candidate, {"config.txt": secret})
    assert status == 1
    assert "exposed-secret" in finding_codes(report), report


def main() -> None:
    tests = [test_valid_fixture, test_search_string_is_not_dom_id, test_resolved_script_id_counts, test_new_duplicate_id, test_named_handler_and_visible_shortcut, test_new_visible_shortcut_conflict, test_unhandled_visible_shortcut, test_malformed_selector, test_duplicate_metadata, test_merge_marker, test_secret_detection]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"All {len(tests)} code-integrity tests passed.")

if __name__ == "__main__":
    main()
