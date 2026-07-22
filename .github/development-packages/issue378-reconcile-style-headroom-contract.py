#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHELL_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-operational-suite-shell.py"

text = SHELL_PACKAGE.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    "import subprocess\nimport sys\n",
    "import json\nimport subprocess\nimport sys\n",
    "json import",
)

replace_once(
    "TEST = ROOT / \".github\" / \"scripts\" / \"test_issue378_operational_suite_shell.py\"\n",
    """TEST = ROOT / ".github" / "scripts" / "test_issue378_operational_suite_shell.py"
HEADROOM_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
""",
    "headroom paths",
)

replace_once(
    """for path in CANONICAL:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

TEST.parent.mkdir(parents=True, exist_ok=True)
""",
    """baseline_source_lines = len(SOURCE.read_text(encoding="utf-8").splitlines())
candidate_source_lines = len(source.splitlines())
approved_non_style_lines = candidate_source_lines - baseline_source_lines
if approved_non_style_lines != 317:
    raise RuntimeError(
        f"Issue #378 shell line delta changed unexpectedly: {approved_non_style_lines} != 317"
    )

for path in CANONICAL:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

TEST.parent.mkdir(parents=True, exist_ok=True)
""",
    "source line accounting",
)

replace_once(
    """print("Issue #378 operational-suite lifecycle/settings shell contract passed.")
''', encoding="utf-8")
subprocess.run([sys.executable, str(TEST)], cwd=ROOT, check=True)
print("Issue #378 operational-suite shell applied and validated.")
""",
    """fixture = __import__('json').loads((ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json').read_text(encoding='utf-8'))
expected_lines = fixture['candidateSourceLines'] + fixture.get('approvedNonStyleSourceLines', 0)
if fixture.get('expectedSourceLines') != expected_lines or expected_lines != len(source.splitlines()):
    raise SystemExit('Issue #378 source-headroom additive accounting is inconsistent')
if fixture.get('approvedNonStyleChanges') != [{'issue': 378, 'phase': 'operational-suite-shell', 'lines': 317}]:
    raise SystemExit('Issue #378 source-headroom change ledger is missing or altered')

print("Issue #378 operational-suite lifecycle/settings shell contract passed.")
''', encoding="utf-8")

headroom_fixture = json.loads(HEADROOM_FIXTURE.read_text(encoding="utf-8"))
if headroom_fixture.get("schemaVersion") != 4:
    raise RuntimeError("main-style source-headroom fixture schema changed before Issue #378 shell apply")
if headroom_fixture.get("candidateSourceLines") != baseline_source_lines:
    raise RuntimeError(
        "main-style source-headroom baseline no longer matches the pre-shell userscript"
    )
headroom_fixture["schemaVersion"] = 5
headroom_fixture["approvedNonStyleSourceLines"] = approved_non_style_lines
headroom_fixture["approvedNonStyleChanges"] = [
    {"issue": 378, "phase": "operational-suite-shell", "lines": approved_non_style_lines}
]
headroom_fixture["expectedSourceLines"] = candidate_source_lines
HEADROOM_FIXTURE.write_text(json.dumps(headroom_fixture, indent=2) + "\n", encoding="utf-8")

headroom_test = HEADROOM_TEST.read_text(encoding="utf-8")
old_headroom_check = '''    split_lines = re.split(r"\\r?\\n", text)
    source_lines = len(split_lines) - 1 if text.endswith("\\n") else len(split_lines)
    if source_lines != fixture["candidateSourceLines"]:
        fail(f"candidate source line count changed: {source_lines} != {fixture['candidateSourceLines']}")
'''
new_headroom_check = '''    split_lines = re.split(r"\\r?\\n", text)
    source_lines = len(split_lines) - 1 if text.endswith("\\n") else len(split_lines)
    approved_changes = fixture.get("approvedNonStyleChanges", [])
    if not isinstance(approved_changes, list):
        fail("approved non-style source changes must be a list")
    approved_total = 0
    for change in approved_changes:
        if not isinstance(change, dict):
            fail("approved non-style source change entries must be objects")
        issue = change.get("issue")
        phase = str(change.get("phase") or "").strip()
        lines = change.get("lines")
        if not isinstance(issue, int) or issue <= 0 or not phase or not isinstance(lines, int) or lines < 0:
            fail("approved non-style source change entry is malformed")
        approved_total += lines
    if approved_total != fixture.get("approvedNonStyleSourceLines", 0):
        fail("approved non-style source-line ledger total is inconsistent")
    expected_source_lines = fixture["candidateSourceLines"] + approved_total
    if fixture.get("expectedSourceLines", expected_source_lines) != expected_source_lines:
        fail("expected source line count is inconsistent with the approved non-style ledger")
    if source_lines != expected_source_lines:
        fail(f"candidate source line count changed: {source_lines} != {expected_source_lines}")
'''
if headroom_test.count(old_headroom_check) != 1:
    raise RuntimeError("main-style source-headroom line-count anchor changed")
HEADROOM_TEST.write_text(headroom_test.replace(old_headroom_check, new_headroom_check, 1), encoding="utf-8")

subprocess.run([sys.executable, str(TEST)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(HEADROOM_TEST)], cwd=ROOT, check=True)
print("Issue #378 operational-suite shell applied and validated.")
""",
    "headroom contract reconciliation",
)

SHELL_PACKAGE.write_text(text, encoding="utf-8")
print("Reconciled Issue #378 shell with exact source-headroom additive accounting.")
