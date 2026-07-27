#!/usr/bin/env python3
"""Build Toolkit v8.1.1 by removing the mistakenly added Alliance Member Manager."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRE_FEATURE = "de244f8d7baff00479f037c49d77885fa030aa67"
VERSION = "8.1.1"
ISSUE = 554
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
SITE_DATA = ROOT / "docs" / "site-data.json"
CHANGELOG = ROOT / "CHANGELOG.md"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_issue554_alliance_member_manager_rollback.py"
OLD_CONTRACT = ROOT / ".github" / "scripts" / "test_alliance_member_manager_contract.py"

RESTORE_PATHS = (
    "src/MissionChief_Map_Command_Toolkit.user.js",
    "docs/site-data.json",
    "help/index.html",
    "help/manifest.json",
    ".github/performance-budget.json",
    ".github/scripts/run_userscript_preflight.sh",
    ".github/fixtures/main-style-source-headroom.json",
)


def git_show(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{PRE_FEATURE}:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def write_restored(path: str) -> None:
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(git_show(path))


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    value, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"{label}: expected one replacement, found {count}")
    return value


def update_source() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(
        source,
        r"^(//\s*@version\s+)\S+\s*$",
        rf"\g<1>{VERSION}",
        "userscript metadata version",
    )
    source = replace_once(
        source,
        r"(version:\s*')[^']+(')",
        rf"\g<1>{VERSION}\2",
        "runtime version",
    )
    for forbidden in (
        "<mcms-alliance-member-manager>",
        "mcms_alliance_member_manager_enabled_v1",
        "data-mcms-alliance-member-manager-toggle",
        "Alliance Member Manager",
        "Load All Member Pages",
    ):
        if forbidden in source:
            raise SystemExit(f"Alliance Member Manager residue remains in source: {forbidden}")
    SOURCE.write_text(source, encoding="utf-8")


def update_help_index(current_before_restore: str) -> None:
    baseline = HELP_INDEX.read_text(encoding="utf-8")
    version_lines = {
        line.replace("8.1.0", "8.0.4")
        for line in current_before_restore.splitlines()
        if "8.1.0" in line
    }
    rebuilt = "\n".join(
        line.replace("8.0.4", VERSION) if line in version_lines else line
        for line in baseline.splitlines()
    )
    if baseline.endswith("\n"):
        rebuilt += "\n"
    for forbidden in ("Alliance Member Manager", "Load All Member Pages", "mcms-alliance-member-manager"):
        if forbidden in rebuilt:
            raise SystemExit(f"Alliance Member Manager residue remains in Help Centre: {forbidden}")
    HELP_INDEX.write_text(rebuilt, encoding="utf-8")


def update_json_versions() -> None:
    manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
    manifest["toolkitVersion"] = VERSION
    HELP_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    site = json.loads(SITE_DATA.read_text(encoding="utf-8"))
    for key in ("version", "toolkitVersion", "currentVersion"):
        if site.get(key) == "8.0.4":
            site[key] = VERSION
    categories = site.get("featureCategories") or []
    if any(item.get("name") == "Alliance operations" for item in categories if isinstance(item, dict)):
        raise SystemExit("Alliance operations feature category remains in site data")
    SITE_DATA.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")


def update_changelog() -> None:
    changelog = CHANGELOG.read_text(encoding="utf-8")
    if "## [8.1.1] - 2026-07-27" in changelog:
        raise SystemExit("v8.1.1 changelog entry already exists")
    marker = "## [8.1.0] - 2026-07-27"
    if marker not in changelog:
        raise SystemExit("Published v8.1.0 changelog entry is missing")
    entry = """## [8.1.1] - 2026-07-27

### Rollback

- Removed the Alliance Member Manager runtime, Toolkit-menu toggle, alliance-member-page controls and related documentation introduced in v8.1.0.
- Restored the exact pre-feature Toolkit behaviour while retaining Pipeline v5.2 and the generic release-forward regression hardening.
- Preserved the published v8.1.0 release record for auditability; v8.1.1 is the supported replacement release.

"""
    CHANGELOG.write_text(changelog.replace(marker, entry + marker, 1), encoding="utf-8")


def update_headroom() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
    candidate = fixture["v8Candidate"]
    v7 = fixture["v7Candidate"]
    source_bytes = len(source.encode())
    source_lines = len(source.splitlines())
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    candidate.update({
        "issue": ISSUE,
        "version": VERSION,
        "sourceBytes": source_bytes,
        "sourceLines": source_lines,
        "sourceSha256": source_sha,
        "maxSourceBytes": 1650000,
        "maxSourceLines": 24500,
        "baseline": "8.0.4",
        "approvedGrowth": {
            "sourceBytes": source_bytes - int(v7["sourceBytes"]),
            "sourceLines": source_lines - int(v7["sourceLines"]),
            "templateBytes": int(candidate["templateBytes"]) - int(v7["templateBytes"]),
            "templateLines": int(candidate["templateLines"]) - int(v7["templateLines"]),
        },
        "scope": "Issue #554 rollback of the mistakenly added Alliance Member Manager; restore the pre-feature Toolkit source with v8.1.1 release metadata",
    })
    HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def write_contract() -> None:
    CONTRACT.write_text(
        '''#!/usr/bin/env python3
"""Permanent contract for Issue #554 Alliance Member Manager rollback."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
SITE_DATA = ROOT / "docs" / "site-data.json"
HELP = ROOT / "help" / "index.html"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github" / "performance-budget.json"

source = SOURCE.read_text(encoding="utf-8")
assert re.search(r"^// @version\\s+8\\.1\\.1$", source, re.MULTILINE)
assert "version: '8.1.1'" in source
for forbidden in (
    "<mcms-alliance-member-manager>",
    "mcms_alliance_member_manager_enabled_v1",
    "data-mcms-alliance-member-manager-toggle",
    "Alliance Member Manager",
    "Load All Member Pages",
):
    assert forbidden not in source, forbidden

assert "## [8.1.1] - 2026-07-27" in CHANGELOG.read_text(encoding="utf-8")
assert "Alliance Member Manager" not in HELP.read_text(encoding="utf-8")
site = json.loads(SITE_DATA.read_text(encoding="utf-8"))
assert not any(item.get("name") == "Alliance operations" for item in site.get("featureCategories", []))
performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
assert performance["absoluteLimits"]["network_request_calls"] == 4
assert performance["relativeLimits"]["network_request_calls"]["warnDelta"] == 0
assert performance["relativeLimits"]["network_request_calls"]["failDelta"] == 0
preflight = PREFLIGHT.read_text(encoding="utf-8")
assert ".github/scripts/test_alliance_member_manager_contract.py" not in preflight
assert ".github/scripts/test_issue554_alliance_member_manager_rollback.py" in preflight
print("Issue #554 rollback contract passed: Alliance Member Manager removed and pre-feature Toolkit behaviour restored.")
''',
        encoding="utf-8",
    )


def update_preflight() -> None:
    preflight = PREFLIGHT.read_text(encoding="utf-8")
    old = "; do PYTHONDONTWRITEBYTECODE=1 python3 \"$contract\"; done"
    new = f" .github/scripts/{CONTRACT.name}{old}"
    if old not in preflight:
        raise SystemExit("Preflight contract loop marker changed")
    PREFLIGHT.write_text(preflight.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    current_help = HELP_INDEX.read_text(encoding="utf-8")
    for path in RESTORE_PATHS:
        write_restored(path)
    if OLD_CONTRACT.exists():
        OLD_CONTRACT.unlink()
    update_source()
    update_help_index(current_help)
    update_json_versions()
    update_changelog()
    update_headroom()
    write_contract()
    update_preflight()
    print("Prepared Toolkit v8.1.1 rollback: Alliance Member Manager removed, release history preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
