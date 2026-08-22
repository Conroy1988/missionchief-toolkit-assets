#!/usr/bin/env python3
"""Run the smallest safe local Toolkit validation set for the current change."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".github" / "dev-test-matrix.json"
SOURCE_PATH = "src/MissionChief_Map_Command_Toolkit.user.js"


class CheckError(RuntimeError):
    """A deterministic development check failed."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if check and result.returncode:
        raise CheckError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def resolve_base(value: str) -> str:
    candidates = [value] if value else ["origin/main", "main", "HEAD"]
    for candidate in candidates:
        if candidate and subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0:
            return git("rev-parse", f"{candidate}^{{commit}}").strip()
    raise CheckError("Unable to resolve a Git comparison base")


def changed_paths(base: str) -> list[str]:
    tracked = git("diff", "--name-only", "--diff-filter=ACDMRTUXB", base, "--").splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted({path.strip().replace("\\", "/") for path in [*tracked, *untracked] if path.strip()})


def source_diff(base: str) -> str:
    return git("diff", "--unified=12", base, "--", SOURCE_PATH, check=False)


def source_diff_hunks(diff: str) -> list[str]:
    hunks: list[list[str]] = []
    current: list[str] | None = None
    for line in diff.splitlines():
        if line.startswith("@@"):
            current = [line]
            hunks.append(current)
            continue
        if current is None or line.startswith(("+++", "---")):
            continue
        current.append(line[1:] if line.startswith(("+", "-", " ")) else line)
    return ["\n".join(hunk) for hunk in hunks if any(line.strip() for line in hunk)]


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def select_features(policy: dict, paths: list[str], diff_hunks: list[str] | str, requested: list[str]) -> tuple[list[str], bool]:
    features = policy["features"]
    hunks = [diff_hunks] if isinstance(diff_hunks, str) else diff_hunks
    unknown_requested = sorted(set(requested) - set(features))
    if unknown_requested:
        raise CheckError(f"Unknown development feature: {', '.join(unknown_requested)}")
    selected = set(requested)
    for name, definition in features.items():
        if any(matches_any(path, definition.get("paths", [])) for path in paths):
            selected.add(name)
        if any(any(anchor in hunk for anchor in definition.get("anchors", [])) for hunk in hunks):
            selected.add(name)
    source_changed = SOURCE_PATH in paths
    attributed = [
        any(
            anchor in hunk
            for definition in features.values()
            for anchor in definition.get("anchors", [])
        )
        for hunk in hunks
    ]
    fallback = source_changed and not requested and (not attributed or not all(attributed))
    return sorted(selected), fallback


def syntax_commands(paths: list[str]) -> list[list[str]]:
    commands: list[list[str]] = []
    for path in paths:
        full = ROOT / path
        if not full.is_file():
            continue
        if path.endswith(".py"):
            commands.append([sys.executable, "-c", f"compile(open({path!r}, encoding='utf-8').read(), {path!r}, 'exec')"])
        elif path.endswith((".js", ".mjs")) and not path.endswith(".user.js"):
            commands.append(["node", "--check", path])
        elif path.endswith(".sh"):
            commands.append(["bash", "-n", path])
    return commands


def deduplicate(commands: list[list[str]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    result = []
    for command in commands:
        key = tuple(command)
        if key in seen:
            continue
        seen.add(key)
        result.append(command)
    return result


def run_command(command: list[str]) -> dict[str, object]:
    started = time.monotonic()
    print(f"[fast-check] {' '.join(command)}", flush=True)
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    elapsed = round(time.monotonic() - started, 3)
    if result.returncode:
        raise CheckError(f"Command failed ({result.returncode}) after {elapsed:.3f}s: {' '.join(command)}")
    return {"command": command, "seconds": elapsed, "result": "passed"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="")
    parser.add_argument("--feature", action="append", default=[])
    parser.add_argument("--all", action="store_true", dest="run_all")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--list", action="store_true", dest="list_only")
    args = parser.parse_args()

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if policy.get("schemaVersion") != 1 or not isinstance(policy.get("features"), dict):
        raise CheckError("Unsupported development test matrix")
    base = resolve_base(args.base)
    paths = changed_paths(base)
    diff_hunks = source_diff_hunks(source_diff(base))
    features, fallback = select_features(policy, paths, diff_hunks, args.feature)

    commands = [*syntax_commands(paths), *policy["always"]]
    for feature in features:
        commands.extend(policy["features"][feature]["tests"])
    if args.run_all:
        commands = [["bash", ".github/scripts/run_userscript_preflight.sh", "--all"]]
        fallback = False
    elif fallback:
        commands.extend(policy["sourceFallback"])
    commands = deduplicate(commands)

    print(f"[fast-check] base={base[:12]} paths={len(paths)} features={','.join(features) or 'none'} fallback={'yes' if fallback else 'no'}")
    if args.list_only:
        for command in commands:
            print(json.dumps(command))
        return 0

    started = time.monotonic()
    results = []
    try:
        for command in commands:
            results.append(run_command(command))
        outcome = "passed"
    except CheckError as error:
        outcome = "failed"
        elapsed = round(time.monotonic() - started, 3)
        report = {"schemaVersion": 1, "result": outcome, "base": base, "paths": paths, "features": features, "fallback": fallback, "sourceSha256": sha256(ROOT / SOURCE_PATH), "seconds": elapsed, "commands": results, "error": str(error)}
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[fast-check] FAILED: {error}", file=sys.stderr)
        return 1

    elapsed = round(time.monotonic() - started, 3)
    report = {"schemaVersion": 1, "result": outcome, "base": base, "paths": paths, "features": features, "fallback": fallback, "sourceSha256": sha256(ROOT / SOURCE_PATH), "seconds": elapsed, "commands": results}
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[fast-check] PASSED in {elapsed:.3f}s ({len(commands)} commands)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckError as error:
        print(f"[fast-check] FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
