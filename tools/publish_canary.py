#!/usr/bin/env python3
"""Atomically publish the generated canary branch without GitHub Actions."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from build_canary import BUNDLE_NAME, MANIFEST_NAME, ROOT, build

EXPECTED_REMOTE = "https://github.com/Conroy1988/missionchief-toolkit-assets.git"
CANARY_REF = "refs/heads/canary"
EVIDENCE = ROOT / ".dev" / "canary-publish.json"


class CanaryPublishError(RuntimeError):
    """A guarded canary publication could not complete."""


def run(command: list[str], *, cwd: Path = ROOT, capture: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=capture, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout or "").strip()
        raise CanaryPublishError(detail or f"{' '.join(command)} failed")
    return result


def output(command: list[str], *, cwd: Path = ROOT) -> str:
    return run(command, cwd=cwd, capture=True).stdout.strip()


def remote_head(remote: str) -> str:
    lines = output(["git", "ls-remote", "--heads", remote, "canary"]).splitlines()
    if not lines:
        return ""
    if len(lines) != 1:
        raise CanaryPublishError("Remote canary identity is ambiguous")
    sha, ref = lines[0].split(maxsplit=1)
    if ref != CANARY_REF or len(sha) != 40:
        raise CanaryPublishError("Remote canary reference is malformed")
    return sha


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--build-id", default="")
    parser.add_argument("--created-at", default="")
    args = parser.parse_args()

    remote_url = output(["git", "remote", "get-url", args.remote])
    if remote_url.rstrip("/") != EXPECTED_REMOTE.rstrip("/"):
        raise CanaryPublishError(f"Refusing unexpected canary remote: {remote_url}")
    output_dir = ROOT / ".dev" / "canary"
    manifest = build(output=output_dir, build_id=args.build_id, created_at=args.created_at)
    old_head = remote_head(args.remote)
    if args.dry_run:
        print(json.dumps({"state": "dry-run", "oldHead": old_head or None, "manifest": manifest}, indent=2, sort_keys=True))
        return 0

    check_evidence = ROOT / ".dev" / "canary-fast-check.json"
    run([sys.executable, "tools/ensure_dev_dependencies.py"])
    run([sys.executable, "tools/dev_fast_check.py", "--json-output", str(check_evidence)])
    check = json.loads(check_evidence.read_text(encoding="utf-8"))
    if check.get("result") != "passed":
        raise CanaryPublishError("Current worktree did not pass change-aware local validation")
    if check.get("sourceSha256") != manifest["source"]["sha256"]:
        raise CanaryPublishError("Validated source differs from the canary bundle source")

    with tempfile.TemporaryDirectory(prefix="mcms-canary-") as temporary:
        work = Path(temporary)
        run(["git", "init", "--quiet"], cwd=work)
        run(["git", "remote", "add", "origin", remote_url], cwd=work)
        run(["git", "config", "user.name", "Conroy1988"], cwd=work)
        run(["git", "config", "user.email", "Conroy1988@users.noreply.github.com"], cwd=work)
        if old_head:
            run(["git", "fetch", "--quiet", "--depth=1", "origin", f"{CANARY_REF}:refs/remotes/origin/canary"], cwd=work)
            run(["git", "checkout", "--quiet", "-b", "canary", "refs/remotes/origin/canary"], cwd=work)
            for item in work.iterdir():
                if item.name == ".git":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            run(["git", "checkout", "--quiet", "--orphan", "canary"], cwd=work)
        target = work / "canary"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_dir / BUNDLE_NAME, target / BUNDLE_NAME)
        shutil.copy2(output_dir / MANIFEST_NAME, target / MANIFEST_NAME)
        run(["git", "add", "--", f"canary/{BUNDLE_NAME}", f"canary/{MANIFEST_NAME}"], cwd=work)
        run(["git", "commit", "--quiet", "-m", f"canary: publish {manifest['buildId']}"], cwd=work)
        new_head = output(["git", "rev-parse", "HEAD"], cwd=work)
        run(["git", "push", "--quiet", "origin", f"HEAD:{CANARY_REF}"], cwd=work)

    verified_head = remote_head(args.remote)
    if verified_head != new_head:
        raise CanaryPublishError("Remote canary did not resolve to the exact published commit")
    evidence = {
        "schemaVersion": 1,
        "state": "published",
        "branch": "canary",
        "previousHead": old_head or None,
        "publishedHead": new_head,
        "buildId": manifest["buildId"],
        "bundleSha256": manifest["bundle"]["sha256"],
        "publishedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "githubActionsExpected": 0,
        "localValidationSeconds": check["seconds"],
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Canary {manifest['buildId']} published as {new_head}")
    print("GitHub Actions expected: 0")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CanaryPublishError as error:
        raise SystemExit(f"Canary publish failed: {error}") from error
