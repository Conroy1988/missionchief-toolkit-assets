#!/usr/bin/env python3
"""Prove deterministic canary construction, loader integrity, and zero-Actions publication policy."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "tools" / "build_canary.py"
PUBLISH_SCRIPT = ROOT / "tools" / "publish_canary.py"
LOADER = ROOT / "tools" / "canary-loader.user.js"


def load_builder():
    spec = importlib.util.spec_from_file_location("mcms_build_canary", BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        assert marker in text, f"{label} missing {marker!r}"


def main() -> int:
    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="mcms-canary-test-") as temporary:
        first = Path(temporary) / "first"
        second = Path(temporary) / "second"
        arguments = {
            "build_id": "test-20260822-deadbeef",
            "created_at": "2026-08-22T00:00:00Z",
            "source_commit": "deadbeef" * 5,
        }
        manifest = builder.build(output=first, **arguments)
        repeated = builder.build(output=second, **arguments)
        assert manifest == repeated, "Fixed-input canary manifest is not deterministic"
        bundle = (first / builder.BUNDLE_NAME).read_bytes()
        repeated_bundle = (second / builder.BUNDLE_NAME).read_bytes()
        assert bundle == repeated_bundle, "Fixed-input canary bundle is not deterministic"
        assert hashlib.sha256(bundle).hexdigest() == manifest["bundle"]["sha256"]
        assert len(bundle) == manifest["bundle"]["bytes"]
        text = bundle.decode("utf-8")
        require(text, [
            "MissionChief Map Command Toolkit — CANARY",
            "@namespace    https://github.com/Conroy1988/missionchief-map-command-toolkit/canary",
            "@version      10.17.1.20260822000000",
            "pageWindow.__MCMS_CANARY_RUNTIME__ = MCMS_CANARY_BUILD",
            '"buildId":"test-20260822-deadbeef"',
        ], "generated canary")
        syntax = subprocess.run(["node", "--check", str(first / builder.BUNDLE_NAME)], cwd=ROOT, check=False)
        assert syntax.returncode == 0, "Generated canary JavaScript is invalid"

    loader = LOADER.read_text(encoding="utf-8")
    require(loader, [
        "@run-at       document-start",
        "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/canary/canary/manifest.json",
        "crypto.subtle.digest('SHA-256'",
        "Canary SHA-256 verification failed",
        "verifiedCachedCandidate",
        "ensureBackup",
        "restoreBackup",
        "previous?.destroy?.('replaced by verified maintainer canary')",
        "new Function",
        "Pause canary",
        "stable Toolkit retained",
    ], "canary loader")
    assert loader.index("await sha256(bundle)") < loader.index("new Function"), "Loader execution is not ordered after SHA-256 verification"
    assert "eval(" not in loader
    assert "@connect      *" not in loader
    assert "github.com/api" not in loader

    publisher = PUBLISH_SCRIPT.read_text(encoding="utf-8")
    require(publisher, [
        'CANARY_REF = "refs/heads/canary"',
        '"githubActionsExpected": 0',
        '"push", "--quiet", "origin", f"HEAD:{CANARY_REF}"',
        '"git", "ls-remote", "--heads"',
        '"tools/dev_fast_check.py"',
        'check.get("sourceSha256") != manifest["source"]["sha256"]',
    ], "canary publisher")
    for forbidden in ["--force", "workflow_dispatch", "actions/runs", "refs/heads/main"]:
        assert forbidden not in publisher, f"Canary publisher contains forbidden marker: {forbidden}"

    cleanup = (ROOT / ".github" / "workflows" / "execute-audited-branch-cleanup.yml").read_text(encoding="utf-8")
    assert " main release-state distribution canary " in cleanup, "Canary branch is not protected from cleanup"

    print("Canary construction and zero-Actions publication contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
