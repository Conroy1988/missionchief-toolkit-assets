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
AUDIO_ALIAS_SCRIPT_PATH = Path(__file__).with_name("check_audio_alias_contract.py")
spec = importlib.util.spec_from_file_location("asset_health", SCRIPT_PATH)
assert spec and spec.loader
asset_health = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = asset_health
spec.loader.exec_module(asset_health)

audio_spec = importlib.util.spec_from_file_location("audio_alias_contract", AUDIO_ALIAS_SCRIPT_PATH)
assert audio_spec and audio_spec.loader
audio_alias_contract = importlib.util.module_from_spec(audio_spec)
sys.modules[audio_spec.name] = audio_alias_contract
audio_spec.loader.exec_module(audio_alias_contract)


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



def write_audio_contract_fixture(root: Path) -> Path:
    canonical_a = "themes/cyberpunk/audio/cyberpunk-cashout.mp3"
    canonical_b = "themes/umbrella/audio/umbrella-containment-cashout.mp3"
    legacy = "cyberpunk-cashout.mp3"
    payload_a = b"ID3" + b"A" * 32
    payload_b = b"ID3" + b"B" * 32
    for rel, payload in ((canonical_a, payload_a), (canonical_b, payload_b), (legacy, payload_a)):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    source = root / "src/MissionChief_Map_Command_Toolkit.user.js"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        "const a = 'https://raw.githubusercontent.com/test/repo/main/" + canonical_a + "';\n"
        "const b = 'https://raw.githubusercontent.com/test/repo/main/" + canonical_b + "';\n",
        encoding="utf-8",
    )
    contract = root / ".github/asset-compatibility-aliases.json"
    write_json(
        contract,
        {
            "schemaVersion": 1,
            "canonicalSource": "src/MissionChief_Map_Command_Toolkit.user.js",
            "stableRef": "main",
            "canonicalAudioPaths": [canonical_a, canonical_b],
            "aliases": [
                {
                    "legacyPath": legacy,
                    "canonicalPath": canonical_a,
                }
            ],
        },
    )
    return contract


def audio_contract_codes(report: dict) -> set[str]:
    return {item["code"] for item in report["failures"]}


def test_audio_alias_contract_valid_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        contract = write_audio_contract_fixture(root)
        report = audio_alias_contract.validate_repository(root, contract, "test/repo")
        assert not report["failures"], report


def test_audio_alias_contract_missing_alias() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        contract = write_audio_contract_fixture(root)
        (root / "cyberpunk-cashout.mp3").unlink()
        report = audio_alias_contract.validate_repository(root, contract, "test/repo")
        assert "missing-legacy-alias" in audio_contract_codes(report), report


def test_audio_alias_contract_hash_mismatch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        contract = write_audio_contract_fixture(root)
        (root / "cyberpunk-cashout.mp3").write_bytes(b"ID3" + b"X" * 32)
        report = audio_alias_contract.validate_repository(root, contract, "test/repo")
        assert "alias-hash-mismatch" in audio_contract_codes(report), report


def test_audio_alias_contract_undeclared_duplicate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        contract = write_audio_contract_fixture(root)
        payload = (root / "themes/umbrella/audio/umbrella-containment-cashout.mp3").read_bytes()
        extra = root / "unapproved-copy.mp3"
        extra.write_bytes(payload)
        report = audio_alias_contract.validate_repository(root, contract, "test/repo")
        codes = audio_contract_codes(report)
        assert "undeclared-audio-path" in codes, report
        assert "undeclared-duplicate-audio" in codes, report


def test_audio_alias_contract_orphan_audio() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        contract = write_audio_contract_fixture(root)
        (root / "orphan.mp3").write_bytes(b"ID3" + b"Z" * 32)
        report = audio_alias_contract.validate_repository(root, contract, "test/repo")
        assert "undeclared-audio-path" in audio_contract_codes(report), report


def test_repository_audio_contract() -> None:
    contract = REPOSITORY_ROOT / ".github/asset-compatibility-aliases.json"
    report = audio_alias_contract.validate_repository(
        REPOSITORY_ROOT,
        contract,
        "Conroy1988/missionchief-toolkit-assets",
    )
    assert not report["failures"], report

def main() -> None:
    tests = [
        test_live_success_and_optional_warning,
        test_wrong_release_hash_fails,
        test_missing_stable_raw_path_fails_static,
        test_bad_local_signature_fails,
        test_base_url_filename_resolution,
        test_audio_alias_contract_valid_fixture,
        test_audio_alias_contract_missing_alias,
        test_audio_alias_contract_hash_mismatch,
        test_audio_alias_contract_undeclared_duplicate,
        test_audio_alias_contract_orphan_audio,
        test_repository_audio_contract
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"Asset-health self-tests passed: {len(tests)}")


if __name__ == "__main__":
    main()
