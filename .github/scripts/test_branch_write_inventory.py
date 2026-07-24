#!/usr/bin/env python3
"""Enforce the protected-branch write inventory used by Issue #41."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / ".github" / "branch-write-inventory.json"
POLICY_PATH = ROOT / ".github" / "actions-security-policy.json"
DOCUMENT_PATH = ROOT / "docs" / "BRANCH_WRITE_INVENTORY.md"
WORKFLOW_DIR = ROOT / ".github" / "workflows"
SCRIPT_DIR = ROOT / ".github" / "scripts"
SELF = Path(__file__).resolve()


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"Required inventory input is missing: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"Required inventory input is not a JSON object: {path.relative_to(ROOT)}")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def workflow_files() -> list[Path]:
    return sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])


def executable_automation_files() -> list[Path]:
    files = workflow_files()
    files.extend(sorted(SCRIPT_DIR.glob("*.sh")))
    files.extend(sorted(path for path in SCRIPT_DIR.glob("*.py") if not path.name.startswith("test_")))
    return [path for path in files if path.resolve() != SELF]


def contains_main_ref_mutation(text: str) -> bool:
    return bool(
        re.search(r"\bgit\s+push\b[^\n]*(?:HEAD:main|HEAD:refs/heads/main|(?:origin|upstream)\s+main(?:\s|$))", text)
        or re.search(r"\bgit\s+update-ref\s+refs/heads/main\b", text)
        or re.search(r"(?:gh\s+api|curl)[\s\S]{0,240}(?:git/refs/heads/main|refs/heads/main)", text)
    )


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            fail(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            fail(f"{label} contains forbidden marker: {marker}")


def document_mentions(document: str, repository_path: str) -> bool:
    return repository_path in document or Path(repository_path).name in document


def workflow_set(entries: list[dict]) -> set[str]:
    result = {str(entry.get("workflow") or "") for entry in entries}
    if "" in result:
        fail("Every classified workflow requires a repository-relative path")
    return result


def main() -> int:
    inventory = load_json(INVENTORY_PATH)
    policy = load_json(POLICY_PATH)
    document = DOCUMENT_PATH.read_text(encoding="utf-8")

    if inventory.get("schemaVersion") != 1:
        fail("Branch-write inventory schemaVersion must remain 1")
    if inventory.get("strictProtectionEnabled") is not False:
        fail("Strict branch protection must remain disabled during migration")

    direct_entries = inventory.get("directMainWriters") or []
    orchestrator_entries = inventory.get("indirectMainWriteOrchestrators") or []
    artifact_entries = inventory.get("artifactOnlyEvidenceWorkflows") or []
    state_entries = inventory.get("releaseStateBranchWriters") or []
    external_entries = inventory.get("externalRepositoryMainPushSources") or []
    review_entries = inventory.get("reviewBranchWriters") or []
    shadow_entries = inventory.get("shadowBranchWriters") or []

    direct = workflow_set(direct_entries)
    orchestrators = workflow_set(orchestrator_entries)
    artifacts = workflow_set(artifact_entries)
    state_writers = workflow_set(state_entries)

    expected_direct = {
        ".github/workflows/release-recovery.yml",
        ".github/workflows/release-toolkit.yml",
    }
    expected_orchestrators = {
        ".github/workflows/auto-release-after-validation.yml",
        ".github/workflows/owner-release-command.yml",
    }
    expected_artifacts = {
        ".github/workflows/validate-userscript.yml",
        ".github/workflows/release-toolkit-dry-run.yml",
        ".github/workflows/repository-audit.yml",
        ".github/workflows/update-release-dashboard.yml",
        ".github/workflows/import-canonical-userscript.yml",
        ".github/workflows/reconcile-release-announcement-state.yml",
        ".github/workflows/publish-update-manifest.yml",
    }
    expected_state_writers = {".github/workflows/greasyfork-release-monitor.yml"}

    if direct != expected_direct:
        fail(f"Unexpected direct public-main writers: {sorted(direct)}")
    if orchestrators != expected_orchestrators:
        fail(f"Unexpected release orchestrators: {sorted(orchestrators)}")
    if artifacts != expected_artifacts:
        fail(f"Unexpected artifact-only workflow inventory: {sorted(artifacts)}")
    if state_writers != expected_state_writers:
        fail(f"Unexpected release-state writer inventory: {sorted(state_writers)}")

    classified_groups = [direct, orchestrators, artifacts, state_writers]
    for index, left in enumerate(classified_groups):
        for right in classified_groups[index + 1 :]:
            if left & right:
                fail(f"Workflow classifications overlap: {sorted(left & right)}")

    policy_contents = {
        path
        for path, permissions in (policy.get("allowedWritePermissions") or {}).items()
        if "contents" in (permissions or [])
    }
    inventory_contents = set(inventory.get("contentsWriteAuthority") or [])
    classified_contents = direct | orchestrators | state_writers
    if policy_contents != inventory_contents:
        fail(
            "Contents-write authority differs between policy and inventory: "
            f"policy-only={sorted(policy_contents - inventory_contents)}, "
            f"inventory-only={sorted(inventory_contents - policy_contents)}"
        )
    if classified_contents != inventory_contents:
        fail(
            "Every contents-write workflow must have an explicit branch class: "
            f"unclassified={sorted(inventory_contents - classified_contents)}, "
            f"unexpected={sorted(classified_contents - inventory_contents)}"
        )

    declared_contents_write = {
        relative(workflow)
        for workflow in workflow_files()
        if re.search(r"(?m)^\s*contents:\s*write\s*$", workflow.read_text(encoding="utf-8"))
    }
    if declared_contents_write != inventory_contents:
        fail(
            "Workflow declarations and approved contents-write authority differ: "
            f"declared-only={sorted(declared_contents_write - inventory_contents)}, "
            f"inventory-only={sorted(inventory_contents - declared_contents_write)}"
        )

    all_classified = direct | orchestrators | artifacts | state_writers
    for workflow in sorted(all_classified):
        path = ROOT / workflow
        if not path.is_file():
            fail(f"Classified workflow is missing: {workflow}")
        if not document_mentions(document, workflow):
            fail(f"Human inventory does not mention classified workflow: {workflow}")

    discovered_main_sources = {
        relative(path)
        for path in executable_automation_files()
        if contains_main_ref_mutation(path.read_text(encoding="utf-8", errors="replace"))
    }
    expected_public_sources = set(inventory.get("directMainPushSources") or [])
    expected_external_sources = {str(entry.get("path") or "") for entry in external_entries}
    expected_all_sources = expected_public_sources | expected_external_sources
    if discovered_main_sources != expected_all_sources:
        fail(
            "Executable main-ref mutation sources differ from inventory: "
            f"unclassified={sorted(discovered_main_sources - expected_all_sources)}, "
            f"missing={sorted(expected_all_sources - discovered_main_sources)}"
        )
    if direct - expected_public_sources:
        fail(f"Direct writers missing from directMainPushSources: {sorted(direct - expected_public_sources)}")
    if (orchestrators | artifacts | state_writers) & discovered_main_sources:
        fail("Non-main workflow classes must not mutate public main")

    for entry in orchestrator_entries:
        workflow = str(entry["workflow"])
        invoked = str(entry["invokes"])
        text = (ROOT / workflow).read_text(encoding="utf-8")
        if invoked.replace(".github/workflows/", "./.github/workflows/") not in text:
            fail(f"Orchestrator {workflow} no longer invokes {invoked}")

    artifact_markers = {
        ".github/workflows/validate-userscript.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Write immutable validation candidate evidence",
        ],
        ".github/workflows/release-toolkit-dry-run.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Upload reviewable release bundle and evidence",
        ],
        ".github/workflows/repository-audit.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Upload immutable audit reports",
        ],
        ".github/workflows/update-release-dashboard.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Upload dashboard projection evidence",
        ],
        ".github/workflows/import-canonical-userscript.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Upload immutable parity evidence",
        ],
        ".github/workflows/reconcile-release-announcement-state.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Upload immutable announcement-state evidence",
        ],
        ".github/workflows/publish-update-manifest.yml": [
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "Upload immutable update-manifest evidence",
        ],
    }
    for workflow, markers in artifact_markers.items():
        text = (ROOT / workflow).read_text(encoding="utf-8")
        require(text, markers, workflow)
        forbid(
            text,
            ["contents: write", "git push origin HEAD:main", "git push origin HEAD:refs/heads/main"],
            workflow,
        )

    if len(state_entries) != 1:
        fail(f"Expected one release-state writer, found {len(state_entries)}")
    state_entry = state_entries[0]
    expected_state = {
        "workflow": ".github/workflows/greasyfork-release-monitor.yml",
        "helper": ".github/scripts/release_state_branch.py",
        "sourceAuthority": "main release dashboard",
        "target": "release-state",
        "writes": [".github/greasyfork-version.txt"],
        "credential": "github.token",
        "actor": "github-actions[bot]",
        "mainMutationAllowed": False,
        "forcePushAllowed": False,
        "liveConsumerCutoverAllowed": False,
        "migrationState": "transitional fallback-tracker authority",
    }
    if state_entry != expected_state:
        fail("Release-state fallback-monitor inventory changed")

    monitor = (ROOT / state_entry["workflow"]).read_text(encoding="utf-8")
    helper = (ROOT / state_entry["helper"]).read_text(encoding="utf-8")
    require(
        monitor,
        [
            "Check out latest main authority",
            "persist-credentials: false",
            "Prepare governed release-state worktree",
            "release_state_branch.py prepare",
            "RELEASE_STATE_ROOT/.github/greasyfork-version.txt",
            "DASHBOARD_FILE=\"status/release-dashboard.json\"",
            "Reconcile release-state tracker from verified main dashboard",
            "Record announced version on release-state",
            "release_state_branch.py commit",
            "GH_TOKEN: ${{ github.token }}",
        ],
        "Greasy Fork fallback monitor",
    )
    forbid(
        monitor,
        [
            "git push origin HEAD:main",
            "git push origin HEAD:refs/heads/main",
            "git reset --hard origin/main",
            "STATE_FILE=\".github/greasyfork-version.txt\"",
        ],
        "Greasy Fork fallback monitor",
    )
    require(
        helper,
        [
            'TARGET_BRANCH = "release-state"',
            'PUSH_REF = f"HEAD:refs/heads/{TARGET_BRANCH}"',
            "release-state branch role is immutable",
            "release-state moved after preparation",
            "http.https://github.com/.extraheader",
            "Release-state branch writer self-tests passed.",
        ],
        "Release-state branch helper",
    )
    forbid(
        helper,
        [
            'TARGET_BRANCH = "main"',
            "HEAD:refs/heads/main",
            "--force",
            "force-with-lease",
            "git reset --hard origin/main",
        ],
        "Release-state branch helper",
    )

    for entry in external_entries:
        path = ROOT / str(entry["path"])
        repository = str(entry["repository"])
        if not path.is_file():
            fail(f"External writer is missing: {relative(path)}")
        text = path.read_text(encoding="utf-8")
        if repository not in text or relative(path) not in discovered_main_sources:
            fail(f"External writer contract changed: {relative(path)}")

    for entry in review_entries:
        workflow = ROOT / str(entry["workflow"])
        if not workflow.is_file():
            fail(f"Review-branch writer is missing: {relative(workflow)}")
        if relative(workflow) in discovered_main_sources:
            fail(f"Review-branch writer contains prohibited public-main mutation: {relative(workflow)}")
        if str(entry.get("credential") or "") not in workflow.read_text(encoding="utf-8"):
            fail(f"Review-branch writer no longer uses reviewed credential: {relative(workflow)}")

    if len(shadow_entries) != 1:
        fail(f"Expected one shadow synchronization writer, found {len(shadow_entries)}")
    shadow_workflow = ROOT / str(shadow_entries[0].get("workflow") or "")
    if not shadow_workflow.is_file():
        fail("Shadow synchronization workflow is missing")
    if relative(shadow_workflow) in discovered_main_sources:
        fail("Shadow synchronization workflow must not mutate public main")

    for path in sorted(expected_public_sources | expected_external_sources):
        if not document_mentions(document, path):
            fail(f"Human inventory omits executable write source: {path}")

    for claim in [
        "Strict pull-request-only protection is **not yet safe to enable**",
        "two workflows that can commit directly to public `main`",
        "seven workflows use read-only repository access",
        "fallback announcement tracker is now written only to `release-state`",
    ]:
        if claim not in document:
            fail(f"Human inventory is missing migration claim: {claim}")

    print(
        "Branch-write inventory passed: "
        f"{len(direct)} direct main writers, "
        f"{len(state_writers)} release-state writer, "
        f"{len(orchestrators)} orchestrators, "
        f"{len(artifacts)} artifact-only workflows, "
        f"{len(review_entries)} review-branch writers and "
        f"{len(external_entries)} external-repository writer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
