#!/usr/bin/env python3
"""Contract for the four-lane consolidated pull-request gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ".github/workflows/validate-userscript.yml"
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
    ".github/workflows/import-canonical-userscript.yml",
    ".github/workflows/github-pages.yml",
    ".github/workflows/release-planning.yml",
    ".github/workflows/publish-update-manifest.yml",
]

def main() -> int:
    text = GATE.read_text(encoding="utf-8")
    for marker in [
        "run-name: Toolkit Hotfix Gate",
        "classify:",
        "name: Classify changed paths",
        "classify_pr_paths.py",
        "runtime:",
        "name: Runtime lane",
        "integrity:",
        "name: Integrity lane",
        "performance:",
        "name: Performance lane",
        "repository:",
        "name: Repository lane",
        "gate:",
        "name: Toolkit Hotfix Gate",
        "needs:",
        "missionchief-toolkit-validation-candidate-${{ github.sha }}",
        "Write immutable validation candidate evidence",
        "test_consolidated_pr_gate.py",
        "test_path_aware_blocking.py",
        "Allow intentionally skipped lanes",
    ]:
        assert marker in text, marker
    assert text.count("runs-on: ubuntu-latest") == 6
    assert "cancel-in-progress: true" in text
    for path in LEGACY:
        legacy = (ROOT / path).read_text(encoding="utf-8")
        on_block = legacy.split("\npermissions:", 1)[0]
        assert "\n  pull_request:" not in on_block, path
        assert "workflow_dispatch:" in on_block or "schedule:" in on_block or "\n  push:" in on_block
    print("Consolidated PR gate contract passed: path classifier, four selective lanes, one aggregate gate and no legacy PR triggers.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
