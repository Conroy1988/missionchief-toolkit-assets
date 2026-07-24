#!/usr/bin/env python3
"""Enforce the public-main write inventory used by Issue #41."""

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
    if not path.exists():
        fail(f"Required inventory input is missing: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


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
        re.search(r"\bgit\s+push\b[^\n]*(?:HEAD:main|(?:origin|upstream)\s+main(?:\s|$))", text)
        or re.search(r"\bgit\s+update-ref\s+refs/heads/main\b", text)
        or re.search(r"(?:gh\s+api|curl)[\s\S]{0,240}(?:git/refs/heads/main|refs/heads/main)", text)
    )


def document_mentions(document: str, repository_path: str) -> bool:
    return repository_path in document or Path(repository_path).name in document


def require_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            fail(f"{label} is missing required marker: {marker}")


def forbid_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            fail(f"{label} contains forbidden mutation marker: {marker}")


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
    external_entries = inventory.get("externalRepositoryMainPushSources") or []
    review_entries = inventory.get("reviewBranchWriters") or []

    direct_workflows = {str(entry.get("workflow") or "") for entry in direct_entries}
    orchestrator_workflows = {str(entry.get("workflow") or "") for entry in orchestrator_entries}
    artifact_workflows = {str(entry.get("workflow") or "") for entry in artifact_entries}
    classified_contents = direct_workflows | orchestrator_workflows

    if "" in direct_workflows | orchestrator_workflows | artifact_workflows:
        fail("Every classified workflow requires a repository-relative path")
    if direct_workflows & orchestrator_workflows:
        fail("A workflow cannot be both a direct main writer and an orchestrator")
    if artifact_workflows & classified_contents:
        fail("Artifact-only workflows cannot retain contents-write classification")
    if len(direct_workflows) != 5:
        fail(f"Expected five reviewed direct public-main writers, found {len(direct_workflows)}")
    if len(orchestrator_workflows) != 2:
        fail(f"Expected two reviewed release orchestrators, found {len(orchestrator_workflows)}")
    expected_artifacts = {
        ".github/workflows/validate-userscript.yml",
        ".github/workflows/release-toolkit-dry-run.yml",
        ".github/workflows/repository-audit.yml",
        ".github/workflows/update-release-dashboard.yml",
        ".github/workflows/import-canonical-userscript.yml",
    }
    if artifact_workflows != expected_artifacts:
        fail(f"Unexpected artifact-only workflow inventory: {sorted(artifact_workflows)}")

    policy_contents = {
        path
        for path, permissions in (policy.get("allowedWritePermissions") or {}).items()
        if "contents" in (permissions or [])
    }
    inventory_contents = set(inventory.get("contentsWriteAuthority") or [])
    if policy_contents != inventory_contents:
        fail(
            "Contents-write authority differs between policy and inventory: "
            f"policy-only={sorted(policy_contents - inventory_contents)}, "
            f"inventory-only={sorted(inventory_contents - policy_contents)}"
        )
    if classified_contents != inventory_contents:
        fail(
            "Every contents-write workflow must be classified: "
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

    for workflow in sorted(classified_contents | artifact_workflows):
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
    missing_direct_pushes = direct_workflows - expected_public_sources
    if missing_direct_pushes:
        fail(f"Direct writers missing from directMainPushSources: {sorted(missing_direct_pushes)}")
    if (orchestrator_workflows | artifact_workflows) & discovered_main_sources:
        fail("Orchestrator and artifact-only workflows must not mutate public main")

    for entry in orchestrator_entries:
        workflow = str(entry["workflow"])
        invoked = str(entry["invokes"])
        text = (ROOT / workflow).read_text(encoding="utf-8")
        if invoked.replace(".github/workflows/", "./.github/workflows/") not in text:
            fail(f"Orchestrator {workflow} no longer invokes {invoked}")

    dry_run = (ROOT / ".github/workflows/release-toolkit-dry-run.yml").read_text(encoding="utf-8")
    require_markers(dry_run, [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Write immutable dry-run evidence",
        "publicMainChanged: false",
        "Upload reviewable release bundle and evidence",
    ], "Artifact-only dry-run workflow")
    forbid_markers(dry_run, [
        "contents: write", "status/release-dashboard.json", "git commit", "git push",
        "git pull --rebase", "github-actions[bot]",
    ], "Artifact-only dry-run workflow")

    repository_workflow = (ROOT / ".github/workflows/repository-audit.yml").read_text(encoding="utf-8")
    repository_script = (ROOT / ".github/scripts/audit_repository.py").read_text(encoding="utf-8")
    require_markers(repository_workflow, [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "REPOSITORY_AUDIT_OUTPUT_DIR: repository-audit-output",
        "Upload immutable audit reports",
        "storage.publicMainChanged == false",
        "storage.releaseDashboardChanged == false",
    ], "Artifact-only repository-audit workflow")
    forbid_markers(repository_workflow, [
        "contents: write", "status/release-dashboard.json", "git commit", "git push",
        "git pull --rebase", "github-actions[bot]",
    ], "Artifact-only repository-audit workflow")
    require_markers(repository_script, [
        '"type": "workflow-artifact"',
        '"publicMainChanged": False',
        '"releaseDashboardChanged": False',
        "REPOSITORY_AUDIT_OUTPUT_DIR",
    ], "Repository-audit script")
    forbid_markers(repository_script, [
        'ROOT / "status" / "release-dashboard.json"',
        'dashboard["currentVersion"]',
        'dashboard["status"]',
        'dashboard["lastUpdated"]',
    ], "Repository-audit script")

    dashboard_workflow = (ROOT / ".github/workflows/update-release-dashboard.yml").read_text(encoding="utf-8")
    dashboard_generator = (ROOT / ".github/scripts/generate_release_dashboard.py").read_text(encoding="utf-8")
    require_markers(dashboard_workflow, [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Generate and compare read-only dashboard projection",
        "--check",
        "--output dashboard-projection/status-README.md",
        "cmp --silent status/README.md dashboard-projection/status-README.md",
        "Upload dashboard projection evidence",
        "Public main changed: no",
    ], "Artifact-only dashboard-projection workflow")
    forbid_markers(dashboard_workflow, [
        "contents: write", "git commit", "git push", "git pull --rebase", "github-actions[bot]",
    ], "Artifact-only dashboard-projection workflow")
    require_markers(dashboard_generator, [
        'parser.add_argument("--output"',
        '"--check"',
        "if args.check:",
        "Dashboard ledger sanitation would change the committed JSON",
        "def render_dashboard(data: dict) -> str:",
    ], "Dashboard generator projection mode")

    parity_workflow = (ROOT / ".github/workflows/import-canonical-userscript.yml").read_text(encoding="utf-8")
    parity_auditor = (ROOT / ".github/scripts/audit_greasyfork_canonical_parity.py").read_text(encoding="utf-8")
    require_markers(parity_workflow, [
        "name: Verify Greasy Fork Canonical Parity",
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Audit GitHub canonical authority",
        "Upload immutable parity evidence",
        "missionchief-greasyfork-canonical-parity-${{ github.sha }}",
        "Automatic importing is retired; owner review is required.",
    ], "Artifact-only Greasy Fork parity workflow")
    forbid_markers(parity_workflow, [
        "contents: write", "git commit", "git push", "git pull --rebase",
        "github-actions[bot]", "DEVELOPMENT_PR_TOKEN", "gh pr create",
    ], "Artifact-only Greasy Fork parity workflow")
    require_markers(parity_auditor, [
        '"authority": "GitHub canonical source"',
        '"automaticImportEnabled": False',
        '"publicMainChanged": False',
        '"canonicalSourceChanged": False',
        '"sourceBaselineChanged": False',
        '"liveAheadRequiresOwnerReview": True',
    ], "Greasy Fork parity auditor")

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

    for path in sorted(expected_public_sources | expected_external_sources):
        if not document_mentions(document, path):
            fail(f"Human inventory omits executable write source: {path}")

    for claim in [
        "Strict pull-request-only protection is **not yet safe to enable**",
        "five workflows that can commit directly to public `main`",
        "Canonical validation, release dry runs, repository audits, dashboard projection and Greasy Fork parity are now artifact-only",
    ]:
        if claim not in document:
            fail(f"Human inventory is missing migration claim: {claim}")

    print(
        "Branch-write inventory passed: "
        f"{len(direct_workflows)} direct main writers, "
        f"{len(orchestrator_workflows)} orchestrators, "
        f"{len(artifact_workflows)} artifact-only workflows, "
        f"{len(review_entries)} review-branch writers and "
        f"{len(external_entries)} external-repository writer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
