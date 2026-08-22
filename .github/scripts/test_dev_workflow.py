#!/usr/bin/env python3
"""Contract tests for the local-first Toolkit development lane."""

from __future__ import annotations

import importlib.util
import fnmatch
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / ".github" / "dev-test-matrix.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        assert marker in text, f"{label} missing {marker!r}"


def main() -> int:
    required = [
        "toolkit",
        "devlab/index.html",
        "devlab/lab.css",
        "devlab/lab.js",
        "devlab/frame.html",
        "devlab/fixture.css",
        "devlab/frame.js",
        "tools/dev_server.py",
        "tools/dev_fast_check.py",
        "tools/ensure_dev_dependencies.py",
        "tools/promote_candidate.py",
        "tools/build_canary.py",
        "tools/publish_canary.py",
        "tools/canary-loader.user.js",
    ]
    for relative in required:
        assert (ROOT / relative).is_file(), f"Development lane file missing: {relative}"

    entrypoint = (ROOT / "toolkit").read_text(encoding="utf-8")
    require(entrypoint, ["tools/dev_server.py", "tools/ensure_dev_dependencies.py", "tools/dev_fast_check.py", "tools/promote_candidate.py", "tools/build_canary.py", "tools/publish_canary.py"], "toolkit entrypoint")
    assert "git push" not in entrypoint, "Entrypoint must delegate guarded publication"

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    assert matrix["schemaVersion"] == 1
    assert {"workflow-policy", "dev-lab", "canary", "dispatch-recruitment", "expansion-planner", "native-visibility", "desktop-workspace", "transport-sweep", "finance", "command-shell"} <= set(matrix["features"])
    assert matrix["sourceFallback"] == [["bash", ".github/scripts/run_userscript_preflight.sh", "--contracts"]]
    commands = [tuple(command) for command in matrix["always"]]
    assert ("node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js") in commands

    fast = load_module("mcms_dev_fast_check", ROOT / "tools" / "dev_fast_check.py")
    selected, fallback = fast.select_features(
        matrix,
        ["src/MissionChief_Map_Command_Toolkit.user.js"],
        "dispatchRecruitmentRuntime.personnelDesired = value; show_vehicle",
        [],
    )
    assert "dispatch-recruitment" in selected and "native-visibility" in selected
    assert fallback is False
    selected, fallback = fast.select_features(
        matrix,
        ["src/MissionChief_Map_Command_Toolkit.user.js"],
        "const completelyNewSubsystem = true;",
        [],
    )
    assert selected == [] and fallback is True
    selected, fallback = fast.select_features(
        matrix,
        ["src/MissionChief_Map_Command_Toolkit.user.js"],
        [
            "function renderDispatchRecruitmentPanel() { dispatchRecruitmentRuntime.personnelDesired = value; }",
            "function unrelatedNewSubsystem() { return 42; }",
        ],
        [],
    )
    assert "dispatch-recruitment" in selected and fallback is True, "Mixed attributed and unknown source hunks must fail closed"
    selected, fallback = fast.select_features(
        matrix,
        ["src/MissionChief_Map_Command_Toolkit.user.js"],
        ["function unrelatedNewSubsystem() { return 42; }"],
        ["command-shell"],
    )
    assert selected == ["command-shell"] and fallback is False, "Explicit feature ownership should select the focused lane"
    selected, fallback = fast.select_features(matrix, ["devlab/frame.js"], "", [])
    assert selected == ["dev-lab"] and fallback is False

    server = load_module("mcms_dev_server", ROOT / "tools" / "dev_server.py")
    state = server.development_state()
    assert state["schemaVersion"] == 1
    assert len(state["sha256"]) == 64 and len(state["labSha256"]) == 64
    assert state["version"].count(".") == 2
    assert server.allowed_request_path("/devlab/frame.html")
    assert server.allowed_request_path("/src/MissionChief_Map_Command_Toolkit.user.js")
    assert not server.allowed_request_path("/.git/config")
    assert not server.allowed_request_path("/.dev/canary/manifest.json")
    assert not server.allowed_request_path("/node_modules/jsdom/package.json")

    dependencies = load_module("mcms_dev_dependencies", ROOT / "tools" / "ensure_dev_dependencies.py")
    assert dependencies.REQUIRED == {"jsdom": "26.1.0", "acorn": "8.15.0"}
    assert dependencies.installed(), "Pinned local development dependencies are unavailable"

    lab = (ROOT / "devlab" / "lab.js").read_text(encoding="utf-8")
    frame = (ROOT / "devlab" / "frame.js").read_text(encoding="utf-8")
    require(lab, ["/__mcms_dev_state", "widthStable", "noHorizontalOverflow", "matrix"], "Dev Lab controller")
    require(frame, ["__MCMS_DEV_LAB_API__", "probeWidth", "buildHealthReport", "mcms-dev-focus", "__MC_MAP_COMMAND_TOOLKIT_RUNTIME__"], "Dev Lab fixture")
    assert "https://missionchief" not in frame, "Dev Lab must not call a live game origin"

    for workflow in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        lines = workflow.read_text(encoding="utf-8").splitlines()
        push_index = next((index for index, line in enumerate(lines) if line == "  push:"), None)
        if push_index is None:
            continue
        block = []
        for line in lines[push_index + 1 :]:
            if line.startswith("  ") and not line.startswith("    "):
                break
            block.append(line)
        branch_index = next((index for index, line in enumerate(block) if line.strip() == "branches:"), None)
        assert branch_index is not None, f"Canary would trigger unrestricted push workflow: {workflow.name}"
        patterns = []
        for line in block[branch_index + 1 :]:
            if not line.startswith("      - "):
                break
            patterns.append(line.split("-", 1)[1].strip().strip("\"'"))
        assert patterns, f"Push workflow has no branch allowlist: {workflow.name}"
        assert not any(fnmatch.fnmatchcase("canary", pattern) for pattern in patterns), f"Canary would trigger {workflow.name}: {patterns}"

    promotion = (ROOT / "tools" / "promote_candidate.py").read_text(encoding="utf-8")
    require(promotion, ["validate_userscript.py", "run_userscript_preflight.sh", "promotion-evidence.json"], "promotion command")
    assert "git push" not in promotion and "gh pr" not in promotion, "Local promotion must finish before GitHub publication"

    print("Local-first development workflow contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
