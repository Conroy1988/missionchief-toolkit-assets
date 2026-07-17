#!/usr/bin/env python3
"""Self-tests for check_asset_health.py using local fixtures only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("check_asset_health.py")
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_USERSCRIPT = "src/MissionChief_Map_Command_Toolkit.user.js"
ACTIVE_AUDIO_PATHS = {
    "bf-bad-company-cashout.mp3",
    "cyberpunk-cashout.mp3",
    "factorio-cashout.mp3",
    "fallout-cashout.mp3",
    "gta-vice-city-cashout.mp3",
    "james-bond-cashout.mp3",
    "scarface-cashout.mp3",
    "themes/umbrella/audio/umbrella-containment-cashout.mp3",
    "themes/hyrule/audio/hyrule-quest-reward.mp3",
}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg"}
spec = importlib.util.spec_from_file_location("asset_health", SCRIPT_PATH)
assert spec and spec.loader
asset_health = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = asset_health
spec.loader.exec_module(asset_health)


class FixtureHandler(BaseHTTPRequestHandler):
    routes: dict[str, tuple[int, str, bytes]] = {}

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _serve(self, include_body: bool) -> None:
        status, content_type, body = self.routes.get(self.path, (404, "text/plain", b"missing"))
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_HEAD(self) -> None:  # noqa: N802
        self._serve(False)

    def do_GET(self) -> None:  # noqa: N802
        self._serve(True)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def base_policy(port: int, digest: str) -> dict:
    return {
        "schemaVersion": 1,
        "repository": {"stableRef": "main"},
        "latestReleaseDashboard": "status/release-dashboard.json",
        "scanFiles": ["src/MissionChief_Map_Command_Toolkit.user.js"],
        "scanTextExtensions": [],
        "monitoredHosts": ["127.0.0.1", "raw.githubusercontent.com"],
        "excludedHosts": ["discord.com"],
        "scriptContentTypes": ["text/javascript", "text/plain"],
        "mediaExtensions": {
            ".mp3": {
                "contentTypes": ["audio/mpeg", "application/octet-stream"],
                "minBytes": 8,
                "maxBytes": 100000,
                "repositoryAsset": True
            },
            ".png": {
                "contentTypes": ["image/png"],
                "minBytes": 8,
                "maxBytes": 100000,
                "repositoryAsset": True
            },
            ".json": {
                "contentTypes": ["application/json"],
                "minBytes": 2,
                "maxBytes": 100000,
                "repositoryAsset": False
            }
        },
        "explicitEndpoints": [
            {
                "id": "userscript",
                "url": f"http://127.0.0.1:{port}/script.user.js",
                "kind": "userscript",
                "compareLatestReleaseVersion": True,
                "compareLatestReleaseHash": True,
                "minBytes": 20
            },
            {
                "id": "metadata",
                "url": f"http://127.0.0.1:{port}/script.meta.js",
                "kind": "metadata",
                "compareLatestReleaseVersion": True,
                "minBytes": 10
            },
            {
                "id": "optional-blocked",
                "url": f"http://127.0.0.1:{port}/blocked",
                "kind": "url",
                "required": False,
                "allowedWarningStatuses": [403]
            }
        ],
        "network": {
            "timeoutSeconds": 2,
            "retries": 1,
            "retryBackoffSeconds": 0,
            "signatureBytes": 64,
            "maxBytesPerAsset": 100000,
            "userAgent": "asset-health-test"
        },
        "limits": {"maxEndpoints": 50}
    }


def prepare_repo(root: Path, policy: dict, digest: str) -> None:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src/MissionChief_Map_Command_Toolkit.user.js").write_text("// @version 1.2.3\n", encoding="utf-8")
    write_json(root / "status/release-dashboard.json", {"latestRelease": {"version": "1.2.3", "sha256": digest}})
    write_json(root / ".github/asset-health-policy.json", policy)


def assert_has(report: dict, code: str, severity: str = "failure") -> None:
    items = report["failures" if severity == "failure" else "warnings"]
    assert any(item["code"] == code for item in items), (code, report)


def test_live_success_and_optional_warning() -> None:
    userscript = b"// ==UserScript==\n// @version 1.2.3\n// ==/UserScript==\nconsole.log('ok');\n"
    digest = hashlib.sha256(userscript).hexdigest()
    FixtureHandler.routes = {
        "/script.user.js": (200, "text/javascript", userscript),
        "/script.meta.js": (200, "text/javascript", b"// @version 1.2.3\n"),
        "/blocked": (403, "text/html", b"blocked")
    }
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy = base_policy(server.server_port, digest)
            prepare_repo(root, policy, digest)
            report = asset_health.build_report(root, policy, "live", "test/repo")
            assert report["summary"]["failures"] == 0, report
            assert_has(report, "optional-http-status", "warning")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_wrong_release_hash_fails() -> None:
    userscript = b"// @version 1.2.3\nactual\n"
    FixtureHandler.routes = {
        "/script.user.js": (200, "text/javascript", userscript),
        "/script.meta.js": (200, "text/javascript", b"// @version 1.2.3\n"),
        "/blocked": (200, "text/html", b"ok")
    }
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy = base_policy(server.server_port, "0" * 64)
            prepare_repo(root, policy, "0" * 64)
            report = asset_health.build_report(root, policy, "live", "test/repo")
            assert_has(report, "sha256-mismatch")
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_missing_stable_raw_path_fails_static() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        digest = "a" * 64
        policy = base_policy(9, digest)
        policy["explicitEndpoints"] = []
        prepare_repo(root, policy, digest)
        source = root / "src/MissionChief_Map_Command_Toolkit.user.js"
        source.write_text(
            "const url = 'https://raw.githubusercontent.com/test/repo/main/audio/missing.mp3';\n",
            encoding="utf-8"
        )
        report = asset_health.build_report(root, policy, "static", "test/repo")
        assert_has(report, "missing-repository-asset")


def test_bad_local_signature_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        digest = "a" * 64
        policy = base_policy(9, digest)
        policy["explicitEndpoints"] = []
        prepare_repo(root, policy, digest)
        image = root / "images/bad.png"
        image.parent.mkdir(parents=True)
        image.write_bytes(b"not-a-png-file")
        report = asset_health.build_report(root, policy, "static", "test/repo")
        assert_has(report, "local-file-signature")


def test_base_url_filename_resolution() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        digest = "a" * 64
        policy = base_policy(9, digest)
        policy["explicitEndpoints"] = []
        prepare_repo(root, policy, digest)
        audio = root / "audio/tone.mp3"
        audio.parent.mkdir(parents=True)
        audio.write_bytes(b"ID3" + b"0" * 32)
        source = root / "src/MissionChief_Map_Command_Toolkit.user.js"
        source.write_text(
            "const AUDIO_BASE = 'https://raw.githubusercontent.com/test/repo/main/audio/';\n"
            "const theme = { file: 'tone.mp3' };\n",
            encoding="utf-8"
        )
        endpoints, _, _ = asset_health.discover_endpoints(root, policy, "test/repo")
        matching = [item for item in endpoints if item.url.endswith("/audio/tone.mp3")]
        assert matching and matching[0].local_path == "audio/tone.mp3", endpoints



def test_repository_audio_contract() -> None:
    policy = asset_health.load_json(REPOSITORY_ROOT / ".github/asset-health-policy.json")
    canonical_policy = dict(policy)
    canonical_policy["scanFiles"] = [CANONICAL_USERSCRIPT]
    canonical_policy["scanTextExtensions"] = []

    endpoints, _, local_media = asset_health.discover_endpoints(
        REPOSITORY_ROOT,
        canonical_policy,
        "Conroy1988/missionchief-toolkit-assets",
    )
    audio_paths = {
        asset_health.relative_path(path, REPOSITORY_ROOT)
        for path in local_media
        if path.suffix.lower() in AUDIO_EXTENSIONS
    }
    referenced_audio = {
        endpoint.local_path
        for endpoint in endpoints
        if endpoint.local_path
        and Path(endpoint.local_path).suffix.lower() in AUDIO_EXTENSIONS
        and endpoint.source != "repository-media"
    }

    missing_required = sorted(ACTIVE_AUDIO_PATHS - audio_paths)
    unreferenced_required = sorted(ACTIVE_AUDIO_PATHS - referenced_audio)
    orphaned = sorted(audio_paths - referenced_audio)
    assert not missing_required, f"Required public audio paths are missing: {missing_required}"
    assert not unreferenced_required, f"Required public audio paths are no longer referenced: {unreferenced_required}"
    assert not orphaned, f"Unreferenced repository audio assets detected: {orphaned}"

    hashes: dict[str, list[str]] = {}
    for rel in sorted(audio_paths):
        digest = hashlib.sha256((REPOSITORY_ROOT / rel).read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(rel)
    duplicates = [paths for paths in hashes.values() if len(paths) > 1]
    assert not duplicates, f"Duplicate repository audio payloads detected: {duplicates}"


def main() -> None:
    tests = [
        test_live_success_and_optional_warning,
        test_wrong_release_hash_fails,
        test_missing_stable_raw_path_fails_static,
        test_bad_local_signature_fails,
        test_base_url_filename_resolution,
        test_repository_audio_contract
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"Asset-health self-tests passed: {len(tests)}")


if __name__ == "__main__":
    main()
