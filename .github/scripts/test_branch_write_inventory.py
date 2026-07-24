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


def workflow_set(entries: list[dict]) -> set[str]:
    result = {str(entry.get("workflow") or "") for entry in entries}
    if "" in result:
        fail("Every classified workflow requires a repository-relative path")
    return result


def main() -> int:
    inventory = load_json(INVENTORY_PATH)
    security = load_json(POLICY_PATH)
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

    expected_direct = {".github/workflows/release-toolkit.yml"}
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
    expected_state_writers = {
        ".github/workflows/greasyfork-release-monitor.yml",
        ".github/workflows/release-recovery.yml",
    }
    if direct != expected_direct:
        fail(f"Unexpected direct public-main writers: {sorted(direct)}")
    if orchestrators != expected_orchestrators:
        fail(f"Unexpected release orchestrators: {sorted(orchestrators)}")
    if artifacts != expected_artifacts:
        fail(f"Unexpected artifact-only workflows: {sorted(artifacts)}")
    if state_writers != expected_state_writers:
        fail(f"Unexpected release-state writers: {sorted(state_writers)}")

    groups = [direct, orchestrators, artifacts, state_writers]
    for index, left in enumerate(groups):
        for right in groups[index + 1 :]:
            if left & right:
                fail(f"Workflow classifications overlap: {sorted(left & right)}")

    approved_contents = {
        path
        for path, permissions in (security.get("allowedWritePermissions") or {}).items()
        if "contents" in (permissions or [])
    }
    inventory_contents = set(inventory.get("contentsWriteAuthority") or [])
    classified_contents = direct | orchestrators | state_writers
    if approved_contents != inventory_contents:
        fail("Actions security contents-write authority differs from inventory")
    if classified_contents != inventory_contents:
        fail(
            "Every contents-write workflow must have an explicit branch class: "
            f"unclassified={sorted(inventory_contents - classified_contents)}, "
            f"unexpected={sorted(classified_contents - inventory_contents)}"
        )

    declared_contents = {
        relative(path)
        for path in workflow_files()
        if re.search(r"(?m)^\s*contents:\s*write\s*$", path.read_text(encoding="utf-8"))
    }
    if declared_contents != inventory_contents:
        fail(
            "Workflow contents-write declarations differ from authority: "
            f"declared-only={sorted(declared_contents - inventory_contents)}, "
            f"authority-only={sorted(inventory_contents - declared_contents)}"
        )

    for workflow in sorted(direct | orchestrators | artifacts | state_writers):
        path = ROOT / workflow
        if not path.is_file():
            fail(f"Classified workflow is missing: {workflow}")
        if workflow not in document and Path(workflow).name not in document:
            fail(f"Human inventory omits classified workflow: {workflow}")

    discovered_main = {
        relative(path)
        for path in executable_automation_files()
        if contains_main_ref_mutation(path.read_text(encoding="utf-8", errors="replace"))
    }
    expected_public = set(inventory.get("directMainPushSources") or [])
    expected_external = {str(entry.get("path") or "") for entry in external_entries}
    if discovered_main != expected_public | expected_external:
        fail(
            "Executable main-ref mutation sources differ from inventory: "
            f"unclassified={sorted(discovered_main - expected_public - expected_external)}, "
            f"missing={sorted((expected_public | expected_external) - discovered_main)}"
        )
    if direct - expected_public:
        fail(f"Direct writers missing from main push sources: {sorted(direct - expected_public)}")
    if (orchestrators | artifacts | state_writers) & discovered_main:
        fail("Non-main workflow classes must not mutate public main")

    for entry in orchestrator_entries:
        workflow = str(entry["workflow"])
        invoked = str(entry["invokes"])
        text = (ROOT / workflow).read_text(encoding="utf-8")
        if invoked.replace(".github/workflows/", "./.github/workflows/") not in text:
            fail(f"Orchestrator {workflow} no longer invokes {invoked}")

    artifact_markers = {
        ".github/workflows/validate-userscript.yml": "Write immutable validation candidate evidence",
        ".github/workflows/release-toolkit-dry-run.yml": "Upload reviewable release bundle and evidence",
        ".github/workflows/repository-audit.yml": "Upload immutable audit reports",
        ".github/workflows/update-release-dashboard.yml": "Upload dashboard projection evidence",
        ".github/workflows/import-canonical-userscript.yml": "Upload immutable parity evidence",
        ".github/workflows/reconcile-release-announcement-state.yml": "Upload immutable announcement-state evidence",
        ".github/workflows/publish-update-manifest.yml": "Upload immutable update-manifest evidence",
    }
    for workflow, marker in artifact_markers.items():
        text = (ROOT / workflow).read_text(encoding="utf-8")
        require(text, ["permissions:\n  contents: read", "persist-credentials: false", marker], workflow)
        forbid(text, ["contents: write", "git push origin HEAD:main", "git push origin HEAD:refs/heads/main"], workflow)

    if len(state_entries) != 2:
        fail(f"Expected two release-state writers, found {len(state_entries)}")
    entries_by_workflow = {entry["workflow"]: entry for entry in state_entries}
    monitor_entry = entries_by_workflow[".github/workflows/greasyfork-release-monitor.yml"]
    recovery_entry = entries_by_workflow[".github/workflows/release-recovery.yml"]

    expected_monitor = {
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
    expected_recovery = {
        "workflow": ".github/workflows/release-recovery.yml",
        "helper": ".github/scripts/release_recovery_state.py",
        "branchHelper": ".github/scripts/release_state_branch.py",
        "sourceAuthority": "verified GitHub Release bundle plus governed recovery inputs",
        "target": "release-state",
        "writes": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ],
        "credential": "github.token",
        "actor": "github-actions[bot]",
        "mainMutationAllowed": False,
        "forcePushAllowed": False,
        "liveConsumerCutoverAllowed": False,
        "migrationState": "operational recovery ledger authority",
    }
    if monitor_entry != expected_monitor:
        fail("Fallback-monitor release-state inventory changed")
    if recovery_entry != expected_recovery:
        fail("Release-recovery state inventory changed")

    monitor = (ROOT / monitor_entry["workflow"]).read_text(encoding="utf-8")
    recovery = (ROOT / recovery_entry["workflow"]).read_text(encoding="utf-8")
    branch_helper = (ROOT / recovery_entry["branchHelper"]).read_text(encoding="utf-8")
    recovery_helper = (ROOT / recovery_entry["helper"]).read_text(encoding="utf-8")

    require(
        monitor,
        [
            "Check out latest main authority",
            "persist-credentials: false",
            "Prepare governed release-state worktree",
            "release_state_branch.py prepare",
            "Record announced version on release-state",
        ],
        "Greasy Fork fallback monitor",
    )
    require(
        recovery,
        [
            "Check out latest main authority",
            "persist-credentials: false",
            "Prepare governed release-state worktree",
            "release_recovery_state.py seed",
            "Record Greasy Fork recovery on release-state",
            "Record private backup recovery on release-state",
            "Claim Discord retry on release-state without posting",
            "Finalize Discord recovery on release-state",
            "Rebuild verified release dashboard on release-state",
            "Recovery ledger: \\`release-state\\`",
            "Public main changed: no",
        ],
        "Release recovery workflow",
    )
    for label, text in {
        "monitor": monitor,
        "recovery": recovery,
        "branch helper": branch_helper,
        "recovery helper": recovery_helper,
    }.items():
        forbid(
            text,
            [
                "git push origin HEAD:main",
                "git push origin HEAD:refs/heads/main",
                "git pull --rebase origin main",
                "git reset --hard origin/main",
                "force-with-lease",
            ],
            label,
        )

    require(
        branch_helper,
        [
            'TARGET_BRANCH = "release-state"',
            'PUSH_REF = f"HEAD:refs/heads/{TARGET_BRANCH}"',
            "release-state branch role is immutable",
            "release-state moved after preparation",
            "Release-state branch writer self-tests passed.",
        ],
        "Release-state branch helper",
    )
    require(
        recovery_helper,
        [
            "Apply controlled Toolkit recovery-state transitions",
            "seed_from_main",
            "record_greasyfork",
            "record_backup",
            "claim_discord",
            "finalize_discord",
            "rebuild_dashboard",
            "build_manifest(state_root)",
            "commit_state",
            "Release recovery state self-tests passed.",
        ],
        "Release recovery state helper",
    )

    for entry in external_entries:
        path = ROOT / str(entry["path"])
        repository = str(entry["repository"])
        if not path.is_file():
            fail(f"External writer is missing: {relative(path)}")
        text = path.read_text(encoding="utf-8")
        if repository not in text or relative(path) not in discovered_main:
            fail(f"External writer contract changed: {relative(path)}")

    for entry in review_entries:
        workflow = ROOT / str(entry["workflow"])
        if not workflow.is_file():
            fail(f"Review-branch writer is missing: {relative(workflow)}")
        if relative(workflow) in discovered_main:
            fail(f"Review-branch writer contains prohibited public-main mutation: {relative(workflow)}")
        if str(entry.get("credential") or "") not in workflow.read_text(encoding="utf-8"):
            fail(f"Review-branch writer no longer uses reviewed credential: {relative(workflow)}")

    if len(shadow_entries) != 1:
        fail(f"Expected one shadow synchronization writer, found {len(shadow_entries)}")
    shadow_workflow = ROOT / str(shadow_entries[0].get("workflow") or "")
    if not shadow_workflow.is_file() or relative(shadow_workflow) in discovered_main:
        fail("Shadow synchronization writer is missing or can mutate public main")

    for claim in [
        "one workflow that can commit directly to public `main`",
        "two workflows write governed operational state to `release-state`",
        "release recovery ledger is now written only to `release-state`",
        "seven workflows use read-only repository access",
    ]:
        if claim not in document:
            fail(f"Human inventory is missing migration claim: {claim}")

    print(
        "Branch-write inventory passed: "
        f"{len(direct)} direct main writer, "
        f"{len(state_writers)} release-state writers, "
        f"{len(orchestrators)} orchestrators, "
        f"{len(artifacts)} artifact-only workflows, "
        f"{len(review_entries)} review-branch writers and "
        f"{len(external_entries)} external-repository writer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
