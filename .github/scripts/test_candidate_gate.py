#!/usr/bin/env python3
"""Contract for the shared local and CI candidate gate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "tools" / "candidate_gate.py"


def load_gate():
    spec = importlib.util.spec_from_file_location("candidate_gate", GATE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def command_text(commands) -> str:
    return "\n".join(" ".join(command) for command in commands)


def main() -> int:
    gate = load_gate()
    assert gate.STAGE_ORDER == (
        "static",
        "performance",
        "integrity",
        "dependencies",
        "runtime",
        "development",
        "workflow",
    )
    static = command_text(gate.STAGE_COMMANDS["static"])
    assert "sync_candidate_fingerprint.py --check" in static
    assert "test_candidate_fingerprint.py" in static
    assert "test_documentation_consistency.py" in static
    assert "node --check" in static
    integrity = command_text(gate.STAGE_COMMANDS["integrity"])
    assert "validate_userscript.py" in integrity and "cmp --silent" in integrity
    assert gate.STAGE_COMMANDS["dependencies"] == (
        ("python3", "tools/ensure_dev_dependencies.py"),
    )
    runtime = command_text(gate.STAGE_COMMANDS["runtime"])
    assert "test_ui_mount_integration.mjs" in runtime
    assert "test_issue766_ui_bootstrap_runtime.mjs" in runtime
    assert "run_userscript_preflight.sh --contracts" in runtime
    workflow = command_text(gate.STAGE_COMMANDS["workflow"])
    assert "test_consolidated_pr_gate.py" in workflow
    assert "test_path_aware_blocking.py" in workflow
    source = GATE.read_text(encoding="utf-8")
    assert "test_performance_budget.py" in source
    assert "check_performance_budget.py" in source
    assert "git push" not in source and "gh pr" not in source
    print("Shared candidate gate contract passed: one ordered command catalog for local and CI validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
