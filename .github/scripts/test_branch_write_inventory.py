#!/usr/bin/env python3
"""Fail-closed contract for Issue #41 protected-branch write authority."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / ".github" / "branch-write-inventory.json"
POLICY = ROOT / ".github" / "actions-security-policy.json"
DOCUMENT = ROOT / "docs" / "BRANCH_WRITE_INVENTORY.md"
WORKFLOWS = ROOT / ".github" / "workflows"
SCRIPTS = ROOT / ".github" / "scripts"
SELF = Path(__file__).resolve()

EXPECTED_ARTIFACT_WORKFLOWS = {
    ".github/workflows/validate-userscript.yml",
    ".github/workflows/release-toolkit-dry-run.yml",
    ".github/workflows/repository-audit.yml",
    ".github/workflows/update-release-dashboard.yml",
    ".github/workflows/import-canonical-userscript.yml",
    ".github/workflows/reconcile-release-announcement-state.yml",
    ".github/workflows/publish-update-manifest.yml",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def workflow_files() -> list[Path]:
    return sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])


def executable_automation_files() -> list[Path]:
    files = workflow_files()
    files.extend(sorted(SCRIPTS.glob("*.sh")))
    files.extend(sorted(path for path in SCRIPTS.glob("*.py") if not path.name.startswith("test_")))
    return [path for path in files if path.resolve() != SELF]


def contains_main_mutation(text: str) -> bool:
    return bool(
        re.search(r"\bgit\s+push\b[^\n]*(?:HEAD:main|(?:origin|upstream)\s+main(?:\s|$))", text)
        or re.search(r"\bgit\s+update-ref\s+refs/heads/main\b", text)
        or re.search(r"(?:gh\s+api|curl)[\s\S]{0,240}(?:git/refs/heads/main|refs/heads/main)", text)
    )


def mentions(document: str, path: str) -> bool:
    return path in document or Path(path).name in document


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            fail(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            fail(f"{label} contains forbidden marker: {marker}")


def read_only_workflow(path: str, required: list[str], extra_forbidden: list[str] | None = None) -> str:
    text = (ROOT / path).read_text(encoding="utf-8")
    require(text, ["permissions:\n  contents: read", "persist-credentials: false", *required], path)
    forbid(
        text,
        [
            "contents: write",
            "git commit",
            "git push",
            "git pull --rebase",
            "github-actions[bot]",
            *(extra_forbidden or []),
        ],
        path,
    )
    return text


def main() -> int:
    inventory = load(INVENTORY)
    policy = load(POLICY)
    document = DOCUMENT.read_text(encoding="utf-8")

    if inventory.get("schemaVersion") != 1:
        fail("branch-write inventory schemaVersion must remain 1")
    if inventory.get("strictProtectionEnabled") is not False:
        fail("strict branch protection must remain disabled during migration")

    direct_entries = inventory.get("directMainWriters") or []
    orchestrator_entries = inventory.get("indirectMainWriteOrchestrators") or []
    artifact_entries = inventory.get("artifactOnlyEvidenceWorkflows") or []
    external_entries = inventory.get("externalRepositoryMainPushSources") or []
    review_entries = inventory.get("reviewBranchWriters") or []

    direct = {str(entry.get("workflow") or "") for entry in direct_entries}
    orchestrators = {str(entry.get("workflow") or "") for entry in orchestrator_entries}
    artifacts = {str(entry.get("workflow") or "") for entry in artifact_entries}
    classified_write = direct | orchestrators

    if "" in direct | orchestrators | artifacts:
        fail("every classified workflow needs a repository-relative path")
    if direct & orchestrators or artifacts & classified_write:
        fail("direct, orchestrator and artifact-only workflow classes must not overlap")
    if len(direct) != 3:
        fail(f"Expected three direct public-main writers, found {len(direct)}")
    if len(orchestrators) != 2:
        fail(f"Expected two release orchestrators, found {len(orchestrators)}")
    if artifacts != EXPECTED_ARTIFACT_WORKFLOWS:
        fail(f"Unexpected artifact-only workflow inventory: {sorted(artifacts)}")

    policy_contents = {
        path
        for path, permissions in (policy.get("allowedWritePermissions") or {}).items()
        if "contents" in (permissions or [])
    }
    inventory_contents = set(inventory.get("contentsWriteAuthority") or [])
    declared_contents = {
        rel(path)
        for path in workflow_files()
        if re.search(r"(?m)^\s*contents:\s*write\s*$", path.read_text(encoding="utf-8"))
    }
    if policy_contents != inventory_contents:
        fail(f"Policy/inventory contents-write mismatch: {sorted(policy_contents ^ inventory_contents)}")
    if inventory_contents != classified_write:
        fail(f"Unclassified contents-write workflow: {sorted(inventory_contents ^ classified_write)}")
    if declared_contents != inventory_contents:
        fail(f"Declared/approved contents-write mismatch: {sorted(declared_contents ^ inventory_contents)}")

    for path in sorted(direct | orchestrators | artifacts):
        if not (ROOT / path).is_file():
            fail(f"Classified workflow is missing: {path}")
        if not mentions(document, path):
            fail(f"Human inventory omits classified workflow: {path}")

    discovered_main_sources = {
        rel(path)
        for path in executable_automation_files()
        if contains_main_mutation(path.read_text(encoding="utf-8", errors="replace"))
    }
    expected_public = set(inventory.get("directMainPushSources") or [])
    expected_external = {str(entry.get("path") or "") for entry in external_entries}
    if discovered_main_sources != expected_public | expected_external:
        fail(
            "Executable main-write discovery differs from inventory: "
            f"unclassified={sorted(discovered_main_sources - expected_public - expected_external)}, "
            f"missing={sorted((expected_public | expected_external) - discovered_main_sources)}"
        )
    if direct - expected_public:
        fail(f"Direct workflows missing from directMainPushSources: {sorted(direct - expected_public)}")
    if (orchestrators | artifacts) & discovered_main_sources:
        fail("orchestrator or artifact-only workflow contains a public-main mutation")

    for entry in orchestrator_entries:
        workflow = str(entry["workflow"])
        invoked = str(entry["invokes"])
        text = (ROOT / workflow).read_text(encoding="utf-8")
        if invoked.replace(".github/workflows/", "./.github/workflows/") not in text:
            fail(f"Orchestrator {workflow} no longer invokes {invoked}")

    read_only_workflow(
        ".github/workflows/release-toolkit-dry-run.yml",
        ["Write immutable dry-run evidence", "publicMainChanged: false", "Upload reviewable release bundle and evidence"],
        ["status/release-dashboard.json"],
    )
    read_only_workflow(
        ".github/workflows/repository-audit.yml",
        ["REPOSITORY_AUDIT_OUTPUT_DIR: repository-audit-output", "Upload immutable audit reports"],
        ["status/release-dashboard.json"],
    )
    read_only_workflow(
        ".github/workflows/update-release-dashboard.yml",
        ["Generate and compare read-only dashboard projection", "--check", "Upload dashboard projection evidence"],
    )
    read_only_workflow(
        ".github/workflows/import-canonical-userscript.yml",
        ["Verify Greasy Fork Canonical Parity", "Upload immutable parity evidence", "Automatic importing is retired"],
        ["DEVELOPMENT_PR_TOKEN", "gh pr create"],
    )
    read_only_workflow(
        ".github/workflows/reconcile-release-announcement-state.yml",
        ["Verify Release Announcement State", "announcementTrackerChanged: false", "Upload immutable announcement-state evidence"],
        ["git reset --hard"],
    )
    manifest_workflow = read_only_workflow(
        ".github/workflows/publish-update-manifest.yml",
        [
            "Verify Toolkit Update Manifest",
            "build_stable_update_manifest.py --check",
            "updateManifestChanged: false",
            "Upload immutable manifest evidence",
            "No automatic mutation was attempted.",
        ],
        ["gh workflow run"],
    )
    if "missionchief-update-manifest-verification-${{ github.sha }}" not in manifest_workflow:
        fail("Update-manifest verifier artifact name changed")

    parity_auditor = (ROOT / ".github/scripts/audit_greasyfork_canonical_parity.py").read_text(encoding="utf-8")
    require(parity_auditor, ['"authority": "GitHub canonical source"', '"automaticImportEnabled": False'], "Parity auditor")

    repository_script = (ROOT / ".github/scripts/audit_repository.py").read_text(encoding="utf-8")
    forbid(repository_script, ['ROOT / "status" / "release-dashboard.json"', 'dashboard["status"]'], "Repository auditor")

    for entry in external_entries:
        path = ROOT / str(entry["path"])
        repository = str(entry["repository"])
        text = path.read_text(encoding="utf-8")
        if repository not in text or rel(path) not in discovered_main_sources:
            fail(f"External writer contract changed: {rel(path)}")

    for entry in review_entries:
        path = ROOT / str(entry["workflow"])
        text = path.read_text(encoding="utf-8")
        if rel(path) in discovered_main_sources:
            fail(f"Review-branch writer contains a public-main mutation: {rel(path)}")
        if str(entry.get("credential") or "") not in text:
            fail(f"Review-branch writer no longer uses reviewed credential: {rel(path)}")

    for path in sorted(expected_public | expected_external):
        if not mentions(document, path):
            fail(f"Human inventory omits executable write source: {path}")

    for claim in [
        "Strict pull-request-only protection is **not yet safe to enable**",
        "three workflows that can commit directly to public `main`",
        "Seven workflows now provide read-only immutable evidence",
    ]:
        if claim not in document:
            fail(f"Human inventory is missing migration claim: {claim}")

    print(
        "Branch-write inventory passed: "
        f"{len(direct)} direct main writers, {len(orchestrators)} orchestrators, "
        f"{len(artifacts)} artifact-only workflows, {len(review_entries)} review-branch writers and "
        f"{len(external_entries)} external-repository writer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
