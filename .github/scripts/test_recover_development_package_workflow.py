#!/usr/bin/env python3
"""Contract for the owner-dispatched reviewed-package recovery lane."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/recover-development-package.yml"
INVENTORY = ROOT / ".github/branch-write-inventory.json"

def main() -> int:
    source = WORKFLOW.read_text(encoding="utf-8")
    for marker in [
        "workflow_dispatch:",
        "github.actor == 'Conroy1988'",
        "Pull request must target main.",
        "Pull request must be owned by Conroy1988.",
        "Recovery accepts exactly one staged package file",
        ".github/development-packages/",
        "DEVELOPMENT_PR_TOKEN",
        "git rebase \"$MAIN_SHA\"",
        "python3 \"$PACKAGE_PATH\"",
        "python3 .github/scripts/validate_userscript.py",
        "node --check src/MissionChief_Map_Command_Toolkit.user.js",
        "cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt",
        "--force-with-lease=\"refs/heads/${BRANCH}:${EXPECTED_HEAD}\"",
        "HEAD:${BRANCH}",
    ]:
        assert marker in source, marker
    for forbidden in ["contents: write", "HEAD:main", "HEAD:refs/heads/main", "pull_request_target"]:
        assert forbidden not in source, forbidden
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    entries = {entry["workflow"]: entry for entry in inventory["reviewBranchWriters"]}
    entry = entries[".github/workflows/recover-development-package.yml"]
    assert entry["credential"] == "DEVELOPMENT_PR_TOKEN"
    assert "package-only" in entry["target"]
    print("Reviewed development-package recovery contract passed.")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
