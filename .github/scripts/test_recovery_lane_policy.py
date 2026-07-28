#!/usr/bin/env python3
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
policy = json.loads((ROOT / ".github/recovery-development-package-policy.json").read_text(encoding="utf-8"))
assert policy["workflow"] == ".github/workflows/recover-development-package.yml"
assert policy["acceptedPullRequest"]["changedFiles"] == 1
assert policy["publication"]["exactHeadLease"] is True
assert policy["publication"]["publicMainAllowed"] is False
print("Recovery lane policy passed.")
