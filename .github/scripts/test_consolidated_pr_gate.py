#!/usr/bin/env python3
"""Contract for the single-runner pull-request hotfix gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ".github/workflows/validate-userscript.yml"
CANDIDATE_GATE = ROOT / "tools/candidate_gate.py"
LEGACY = [
    ".github/workflows/full-userscript-audit.yml",
    ".github/workflows/code-integrity-audit.yml",
    ".github/workflows/userscript-structural-audit.yml",
    ".github/workflows/performance-regression-check.yml",
    ".github/workflows/deep-performance-audit.yml",
    ".github/workflows/documentation-drift-check.yml",
    ".github/workflows/asset-health-monitor.yml",
    ".github/workflows/v7-native-toolkit-boundary.yml",
    ".github/workflows/v7-incident-command-wire.yml",
    ".github/workflows/github-pages.yml",
    ".github/workflows/release-planning.yml",
    ".github/workflows/publish-update-manifest.yml",
    ".github/workflows/actions-security-audit.yml",
    ".github/workflows/validate-development-package-workflow.yml",
    ".github/workflows/discord-development-status.yml",
    ".github/workflows/verify-shadow-branch-parity.yml",
    ".github/workflows/release-recovery-validation.yml",
    ".github/workflows/reconcile-release-announcement-state.yml",
]

def main() -> int:
    text = GATE.read_text(encoding="utf-8")
    for marker in [
        "run-name: Toolkit Hotfix Gate",
        "name: Classify changed paths",
        "classify_pr_paths.py",
        "gate:",
        "name: Toolkit Hotfix Gate",
        "missionchief-toolkit-validation-candidate-${{ github.sha }}",
        "Write immutable validation candidate evidence",
        "Run fail-fast candidate checks",
        "Validate canonical userscript and distribution",
        "Install isolated UI contract runtime",
        "Run deterministic runtime contracts",
        "Prove local development loop",
        "Summarise single-runner gate",
        "GitHub runners used: **1**",
        "Parallel validation lanes: **0**",
        "tools/candidate_gate.py --stage static",
        "tools/candidate_gate.py --stage performance --report-dir /tmp",
        "tools/candidate_gate.py --stage integrity",
        "tools/candidate_gate.py --stage dependencies",
        "tools/candidate_gate.py --stage runtime",
        "tools/candidate_gate.py --stage development",
        "tools/candidate_gate.py --stage workflow",
    ]:
        assert marker in text, marker
    assert text.count("runs-on: ubuntu-latest") == 1
    ordered = [
        "--stage static",
        "--stage performance",
        "--stage integrity",
        "--stage dependencies",
        "--stage runtime",
        "--stage development",
        "--stage workflow",
    ]
    assert [text.index(marker) for marker in ordered] == sorted(text.index(marker) for marker in ordered)
    for duplicated in (
        ".github/scripts/validate_userscript.py",
        ".github/scripts/test_documentation_consistency.py",
        ".github/scripts/check_performance_budget.py",
        ".github/scripts/run_userscript_preflight.sh",
    ):
        assert duplicated not in text, f"workflow duplicates shared candidate gate command: {duplicated}"
    candidate_gate = CANDIDATE_GATE.read_text(encoding="utf-8")
    for marker in (
        "test_documentation_consistency.py",
        "test_performance_budget.py",
        "check_performance_budget.py",
        "run_userscript_preflight.sh",
    ):
        assert marker in candidate_gate, marker
    for retired_lane in ("name: Runtime lane", "name: Integrity lane", "name: Performance lane", "name: Repository lane"):
        assert retired_lane not in text, retired_lane
    assert "cancel-in-progress: true" in text
    for path in LEGACY:
        legacy = (ROOT / path).read_text(encoding="utf-8")
        on_block = legacy.split("\npermissions:", 1)[0]
        assert "\n  pull_request:" not in on_block, path
        assert "workflow_dispatch:" in on_block or "schedule:" in on_block or "\n  push:" in on_block or "\n  workflow_run:" in on_block
    discord = (ROOT / ".github/workflows/discord-development-status.yml").read_text(encoding="utf-8")
    assert "      - Toolkit Hotfix Gate" not in discord
    print("Hotfix PR gate contract passed: one path-aware runner, no parallel validation lanes and no legacy PR triggers.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
