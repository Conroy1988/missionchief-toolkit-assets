#!/usr/bin/env python3
"""Enforce the public-main write inventory used by Issue #41.

The contract is intentionally static and fail-closed. It classifies every workflow
with contents write authority, every executable public-main push source, explicit
review-branch writers, and the separate private-recovery repository writer.
"""

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
    files.extend(sorted(SCRIPT_DIR.glob("*.py")))
    return [path for path in files if path.resolve() != SELF]


def contains_main_ref_mutation(text: str) -> bool:
    push = re.search(
        r"\bgit\s+push\b[^\n]*(?:HEAD:main|(?:origin|upstream)\s+main(?:\s|$))",
        text,
    )
    update_ref = re.search(r"\bgit\s+update-ref\s+refs/heads/main\b", text)
    api_ref = re.search(
        r"(?:gh\s+api|curl)[\s\S]{0,240}(?:git/refs/heads/main|refs/heads/main)",
        text,
    )
    return bool(push or update_ref or api_ref)


def main() -> int:
    inventory = load_json(INVENTORY_PATH)
    policy = load_json(POLICY_PATH)
    document = DOCUMENT_PATH.read_text(encoding="utf-8")

    if inventory.get("schemaVersion") != 1:
        fail("Branch-write inventory schemaVersion must remain 1 until a reviewed migration updates the contract")
    if inventory.get("strictProtectionEnabled") is not False:
        fail("Strict branch protection must remain disabled during the inventory-only stage")

    direct_entries = inventory.get("directMainWriters") or []
    orchestrator_entries = inventory.get("indirectMainWriteOrchestrators") or []
    external_entries = inventory.get("externalRepositoryMainPushSources") or []
    review_entries = inventory.get("reviewBranchWriters") or []

    direct_workflows = {str(entry.get("workflow") or "") for entry in direct_entries}
    orchestrator_workflows = {str(entry.get("workflow") or "") for entry in orchestrator_entries}
    classified_contents = direct_workflows | orchestrator_workflows

    if "" in classified_contents:
        fail("Every classified workflow requires a repository-relative path")
    if direct_workflows & orchestrator_workflows:
        fail("A workflow cannot be both a direct main writer and an indirect orchestrator")
    if len(direct_workflows) != 10:
        fail(f"Expected ten reviewed direct public-main writers, found {len(direct_workflows)}")
    if len(orchestrator_workflows) != 2:
        fail(f"Expected two reviewed release orchestrators, found {len(orchestrator_workflows)}")

    policy_contents = {
        path
        for path, permissions in (policy.get("allowedWritePermissions") or {}).items()
        if "contents" in (permissions or [])
    }
    inventory_contents = set(inventory.get("contentsWriteAuthority") or [])
    if policy_contents != inventory_contents:
        fail(
            "Contents-write authority differs between actions-security-policy.json and "
            f"branch-write-inventory.json: policy-only={sorted(policy_contents - inventory_contents)}, "
            f"inventory-only={sorted(inventory_contents - policy_contents)}"
        )
    if classified_contents != inventory_contents:
        fail(
            "Every contents-write workflow must be classified as a direct writer or orchestrator: "
            f"unclassified={sorted(inventory_contents - classified_contents)}, "
            f"unexpected={sorted(classified_contents - inventory_contents)}"
        )

    declared_contents_write: set[str] = set()
    for workflow in workflow_files():
        text = workflow.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*contents:\s*write\s*$", text):
            declared_contents_write.add(relative(workflow))
    if declared_contents_write != inventory_contents:
        fail(
            "Workflow declarations and approved contents-write authority differ: "
            f"declared-only={sorted(declared_contents_write - inventory_contents)}, "
            f"inventory-only={sorted(inventory_contents - declared_contents_write)}"
        )

    for workflow in sorted(classified_contents):
        path = ROOT / workflow
        if not path.is_file():
            fail(f"Classified workflow is missing: {workflow}")
        if workflow not in document:
            fail(f"Human branch-write inventory does not mention classified workflow: {workflow}")

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
            "Executable main-ref mutation sources differ from the reviewed inventory: "
            f"unclassified={sorted(discovered_main_sources - expected_all_sources)}, "
            f"missing={sorted(expected_all_sources - discovered_main_sources)}"
        )

    missing_direct_pushes = direct_workflows - expected_public_sources
    if missing_direct_pushes:
        fail(f"Direct writer workflows missing from directMainPushSources: {sorted(missing_direct_pushes)}")
    if orchestrator_workflows & discovered_main_sources:
        fail("Release orchestrators must not contain their own public-main push or ref-update command")

    for entry in orchestrator_entries:
        workflow = str(entry["workflow"])
        invoked = str(entry["invokes"])
        text = (ROOT / workflow).read_text(encoding="utf-8")
        if invoked.replace(".github/workflows/", "./.github/workflows/") not in text:
            fail(f"Orchestrator {workflow} no longer invokes its reviewed reusable workflow {invoked}")

    for entry in external_entries:
        path = ROOT / str(entry["path"])
        repository = str(entry["repository"])
        if not path.is_file():
            fail(f"External-repository writer is missing: {relative(path)}")
        text = path.read_text(encoding="utf-8")
        if repository not in text:
            fail(f"External writer {relative(path)} no longer pins the reviewed repository {repository}")
        if relative(path) not in discovered_main_sources:
            fail(f"External writer no longer contains the reviewed main push: {relative(path)}")

    for entry in review_entries:
        workflow = ROOT / str(entry["workflow"])
        if not workflow.is_file():
            fail(f"Review-branch writer is missing: {relative(workflow)}")
        if relative(workflow) in discovered_main_sources:
            fail(f"Review-branch writer contains a prohibited public-main mutation: {relative(workflow)}")
        if str(entry.get("credential") or "") not in workflow.read_text(encoding="utf-8"):
            fail(f"Review-branch writer no longer uses its reviewed owner credential: {relative(workflow)}")

    for path in sorted(expected_public_sources | expected_external_sources):
        if path not in document and path not in {str(entry["path"]) for entry in external_entries}:
            fail(f"Human inventory omits executable write source: {path}")

    required_document_claims = [
        "Strict pull-request-only protection is **not yet safe to enable**",
        "ten workflows that can commit directly to public `main`",
        "Stage one is complete",
    ]
    for claim in required_document_claims:
        if claim not in document:
            fail(f"Human inventory is missing required stage-one claim: {claim}")

    print(
        "Branch-write inventory passed: "
        f"{len(direct_workflows)} direct main writers, "
        f"{len(orchestrator_workflows)} orchestrators, "
        f"{len(review_entries)} review-branch writers and "
        f"{len(external_entries)} external-repository writer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
