#!/usr/bin/env python3
"""Contracts for the generated canonical userscript fingerprint."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "sync_candidate_fingerprint.py"
FIXTURE = ROOT / ".github" / "fixtures" / "current-toolkit-candidate.json"


def load_module():
    spec = importlib.util.spec_from_file_location("candidate_fingerprint", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    fingerprint = load_module()
    expected = fingerprint.build_fingerprint(fingerprint.DEFAULT_SOURCE)
    actual = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert actual == expected, "Tracked candidate fingerprint is stale"
    assert fingerprint.serialized(actual) == FIXTURE.read_text(encoding="utf-8")
    source = actual["source"]
    assert source["path"] == "src/MissionChief_Map_Command_Toolkit.user.js"
    assert source["version"].count(".") == 2
    assert source["bytes"] > 100_000 and source["lines"] > 1_000
    assert len(source["sha256"]) == 64
    print("Canonical candidate fingerprint contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
