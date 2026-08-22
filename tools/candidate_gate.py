#!/usr/bin/env python3
"""Run the shared local and CI candidate-validation stages."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "src/MissionChief_Map_Command_Toolkit.user.js"
POLICY_PATH = ".github/performance-budget.json"

STAGE_ORDER = (
    "static",
    "performance",
    "integrity",
    "dependencies",
    "runtime",
    "development",
    "workflow",
)

STAGE_COMMANDS: dict[str, tuple[tuple[str, ...], ...]] = {
    "static": (
        ("python3", ".github/scripts/sync_candidate_fingerprint.py", "--check"),
        ("python3", ".github/scripts/test_candidate_fingerprint.py"),
        ("python3", ".github/scripts/verify_validation_candidate.py", "--self-test"),
        ("python3", ".github/scripts/test_documentation_consistency.py"),
        ("node", "--check", SOURCE_PATH),
    ),
    "integrity": (
        ("python3", ".github/scripts/validate_userscript.py"),
        (
            "cmp",
            "--silent",
            "dist/MissionChief_Map_Command_Toolkit.user.js",
            "dist/MissionChief_Map_Command_Toolkit.txt",
        ),
    ),
    "dependencies": (
        ("python3", "tools/ensure_dev_dependencies.py"),
    ),
    "runtime": (
        ("node", ".github/scripts/test_toolkit_ui_document_start_runtime.mjs"),
        ("node", ".github/scripts/test_toolkit_ui_first_byte_chromium.mjs"),
        ("node", ".github/scripts/test_ui_mount_integration.mjs"),
        ("bash", ".github/scripts/run_userscript_preflight.sh", "--contracts"),
    ),
    "development": (
        ("python3", ".github/scripts/test_dev_workflow.py"),
        ("python3", ".github/scripts/test_canary_workflow.py"),
        ("node", ".github/scripts/test_canary_loader_runtime.mjs"),
        ("node", ".github/scripts/test_dev_lab_runtime.mjs"),
    ),
    "workflow": (
        ("python3", ".github/scripts/audit_actions_security.py"),
        ("python3", ".github/scripts/test_candidate_gate.py"),
        ("python3", ".github/scripts/test_consolidated_pr_gate.py"),
        ("python3", ".github/scripts/test_path_aware_blocking.py"),
        ("python3", ".github/scripts/test_validation_candidate_pipeline.py"),
        ("python3", ".github/scripts/test_branch_write_inventory.py"),
        ("python3", ".github/scripts/test_development_package_workflow.py"),
        ("python3", ".github/scripts/test_automation_record_hygiene.py"),
        ("python3", ".github/scripts/test_release_announcement_state_pipeline.py"),
        ("python3", ".github/scripts/test_release_authority_pipeline.py"),
        ("python3", ".github/scripts/test_release_recovery_state_pipeline.py"),
        ("python3", ".github/scripts/test_shadow_branch_parity.py"),
        ("python3", ".github/scripts/test_shadow_sync_writer.py"),
        ("python3", ".github/scripts/test_update_manifest_pipeline.py"),
        ("python3", ".github/scripts/test_version_status_contract.py"),
    ),
}


def run(command: tuple[str, ...] | list[str]) -> None:
    print(f"[candidate-gate] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def git_output(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def default_base_ref() -> str | None:
    for branch in ("origin/main", "main"):
        if git_output("rev-parse", "--verify", branch):
            return git_output("merge-base", "HEAD", branch)
    return None


def run_performance(base_ref: str | None, report_dir: Path) -> None:
    run(("python3", ".github/scripts/test_performance_budget.py"))
    report_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "python3",
        ".github/scripts/check_performance_budget.py",
        "--candidate",
        SOURCE_PATH,
        "--policy",
        POLICY_PATH,
        "--json-output",
        str(report_dir / "performance-budget-report.json"),
        "--markdown-output",
        str(report_dir / "performance-budget-report.md"),
    ]
    if not base_ref:
        run(command)
        return
    object_name = f"{base_ref}:{SOURCE_PATH}"
    payload = subprocess.run(
        ["git", "show", object_name],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if payload.returncode != 0:
        raise SystemExit(f"Unable to read performance base {object_name}")
    with tempfile.TemporaryDirectory(prefix="mcms-performance-base-") as temporary:
        base_source = Path(temporary) / "base.user.js"
        base_source.write_bytes(payload.stdout)
        run([*command, "--base", str(base_source)])


def run_stage(stage: str, base_ref: str | None, report_dir: Path) -> None:
    started = time.monotonic()
    print(f"[candidate-gate] stage={stage}", flush=True)
    if stage == "performance":
        run_performance(base_ref, report_dir)
    else:
        for command in STAGE_COMMANDS[stage]:
            run(command)
    print(
        f"[candidate-gate] stage={stage} passed in {time.monotonic() - started:.3f}s",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="Run every stage in CI order")
    selection.add_argument("--stage", action="append", choices=STAGE_ORDER)
    parser.add_argument("--base-ref", help="Git commit used as the performance comparison base")
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=ROOT / ".dev" / "candidate-gate",
    )
    args = parser.parse_args()
    stages = list(STAGE_ORDER) if args.all else args.stage
    base_ref = args.base_ref or os.environ.get("PR_BASE_SHA") or default_base_ref()
    for stage in stages:
        run_stage(stage, base_ref, args.report_dir)
    print(f"[candidate-gate] passed stages: {', '.join(stages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
