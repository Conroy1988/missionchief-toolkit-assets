#!/usr/bin/env python3
"""Build and fully validate one release candidate before any GitHub PR is opened."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
EVIDENCE = ROOT / ".dev" / "promotion-evidence.json"


def run(command: list[str]) -> None:
    print(f"[promote] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def output(*args: str) -> str:
    return subprocess.run([*args], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-full", action="store_true", help="Build only; reserved for local tooling tests")
    args = parser.parse_args()
    branch = output("git", "branch", "--show-current")
    if not branch or branch in {"main", "master"}:
        raise SystemExit("Promotion requires a non-default feature branch")

    started = time.monotonic()
    if args.skip_full:
        run(["python3", ".github/scripts/validate_userscript.py"])
        run(["node", "--check", str(SOURCE.relative_to(ROOT))])
        run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"])
    else:
        run(["bash", ".github/scripts/run_userscript_preflight.sh", "--all"])

    changed = output("git", "status", "--short").splitlines()
    evidence = {
        "schemaVersion": 1,
        "state": "locally-validated",
        "branch": branch,
        "head": output("git", "rev-parse", "HEAD"),
        "sourceSha256": sha256(SOURCE),
        "changedPaths": [line[3:] for line in changed if len(line) > 3 and not line[3:].startswith(".dev/")],
        "fullPreflight": not args.skip_full,
        "seconds": round(time.monotonic() - started, 3),
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[promote] Candidate passed locally in {evidence['seconds']:.3f}s")
    print(f"[promote] Evidence: {EVIDENCE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
