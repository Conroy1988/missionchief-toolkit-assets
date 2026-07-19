#!/usr/bin/env python3
from __future__ import annotations

# Fresh guarded-package fingerprint after Issue #153 was reopened.
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / ".github" / "development-packages" / "issue-153-version-status-base.py"
TEMP = ROOT / ".github" / "development-packages" / ".issue-153-version-status-apply.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = BASE.read_text(encoding="utf-8")
source = replace_once(
    source,
    'DIAGNOSTIC = ROOT / ".github" / "development-packages" / "issue-153-diagnostic.txt"\n',
    '',
    'diagnostic constant removal',
)
source = replace_once(
    source,
    'RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"\n',
    '',
    'legacy release-workflow constant removal',
)
source = replace_once(
    source,
    'WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"',
    'WORKFLOW = ROOT / ".github" / "workflows" / "publish-update-manifest.yml"',
    'manifest workflow contract path',
)

marker_start = source.index('    for marker in [\n        "status/update-manifest.json",')
marker_end = source.index('\n\n    result = subprocess.run(["node", str(RUNTIME)], cwd=ROOT)', marker_start)
marker_replacement = '''    for marker in [
        "workflow_run:",
        "- Release Toolkit",
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.head_branch == 'main'",
        "Build manifest from verified release ledger",
        "status/update-manifest.json",
        "'githubRelease': 'published'",
        "'greasyForkSync': 'verified'",
        "'backup': 'private-repository-verified'",
        "'discordRelease': 'posted'",
        "git push origin HEAD:main",
    ]:
        assert marker in workflow, f"verified manifest workflow marker missing: {marker}"
    trigger_index = workflow.index("workflow_run:")
    build_index = workflow.index("Build manifest from verified release ledger")
    push_index = workflow.index("git push origin HEAD:main")
    assert trigger_index < build_index < push_index, "manifest publication must follow successful release reconciliation"
'''
source = source[:marker_start] + marker_replacement + source[marker_end:]

release_start = source.index('\nrelease = RELEASE_WORKFLOW.read_text(encoding="utf-8")')
release_end = source.index('\nchangelog = CHANGELOG.read_text(encoding="utf-8")', release_start)
source = source[:release_start] + source[release_end:]
source = replace_once(source, 'DIAGNOSTIC.unlink(missing_ok=True)\n', '', 'diagnostic cleanup removal')

TEMP.write_text(source, encoding="utf-8")
runpy.run_path(str(TEMP), run_name="__main__")
BASE.unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
