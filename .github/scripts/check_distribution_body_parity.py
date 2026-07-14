#!/usr/bin/env python3
"""Verify executable userscript-body parity across public distribution endpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

VERSION_RE = re.compile(r"^//\s*@version\s+(.+?)\s*$", re.MULTILINE)
END_MARKER = b"// ==/UserScript=="
MANAGED_CODES = {
    "distribution-body-mismatch",
    "distribution-parity-fetch-error",
    "distribution-parity-field-missing",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Top-level JSON value must be an object: {path}")
    return value


def json_pointer(document: Any, pointer: str) -> Any:
    current = document
    for raw in pointer.lstrip("/").split("/") if pointer not in {"", "/"} else []:
        part = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current


def resolve_endpoint_urls(root: Path, policy: dict[str, Any]) -> dict[str, str]:
    urls: dict[str, str] = {}
    for entry in policy.get("explicitEndpoints", []):
        if not isinstance(entry, dict) or not entry.get("id"):
            continue
        url = entry.get("url")
        if not url and isinstance(entry.get("urlSource"), dict):
            source = entry["urlSource"]
            document = load_json(root / source["path"])
            url = json_pointer(document, source["jsonPointer"])
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            urls[str(entry["id"])] = url
    return urls


def cache_bust(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in {"update.greasyfork.org", "raw.githubusercontent.com"}:
        return url
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("asset_health", str(time.time_ns())))
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query)))


def fetch(url: str, timeout: float, retries: int, user_agent: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            cache_bust(url),
            headers={
                "User-Agent": user_agent,
                "Accept": "*/*",
                "Accept-Encoding": "identity",
                "Cache-Control": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
            if attempt < retries:
                time.sleep(attempt)
    raise RuntimeError(str(last_error or "unknown request failure"))


def split_userscript(payload: bytes) -> tuple[bytes, bytes]:
    marker_position = payload.find(END_MARKER)
    if marker_position < 0:
        raise ValueError("userscript metadata end marker was not found")
    line_end = payload.find(b"\n", marker_position)
    if line_end < 0:
        return payload, b""
    return payload[: line_end + 1], payload[line_end + 1 :]


def inspect(payload: bytes) -> dict[str, Any]:
    metadata, body = split_userscript(payload)
    text = payload.decode("utf-8", errors="replace")
    version_match = VERSION_RE.search(text)
    return {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "metadataBytes": len(metadata),
        "bodyBytes": len(body),
        "bodySha256": hashlib.sha256(body).hexdigest(),
        "version": version_match.group(1).strip() if version_match else None,
    }


def recompute_report(report: dict[str, Any]) -> None:
    failures = report.setdefault("failures", [])
    warnings = report.setdefault("warnings", [])
    summary = report.setdefault("summary", {})
    summary["failures"] = len(failures)
    summary["warnings"] = len(warnings)
    material = [
        f"{item.get('code', '')}|{item.get('subject', '')}|{item.get('message', '')}"
        for item in sorted(failures, key=lambda item: (item.get("code", ""), item.get("subject", ""), item.get("message", "")))
    ]
    report["fingerprint"] = hashlib.sha256("\n".join(material).encode()).hexdigest()[:16] if material else "healthy"


def update_markdown(path: Path, report: dict[str, Any], results: list[dict[str, Any]]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else "# Toolkit asset-health report\n"
    text = re.sub(r"- Failures: \*\*\d+\*\*", f"- Failures: **{report['summary']['failures']}**", text)
    text = re.sub(r"- Warnings: \*\*\d+\*\*", f"- Warnings: **{report['summary']['warnings']}**", text)
    text = re.sub(r"- Fingerprint: `[^`]+`", f"- Fingerprint: `{report['fingerprint']}`", text)
    section = ["", "## Distribution executable-body parity", ""]
    for result in results:
        if result.get("error"):
            section.append(f"- ❌ `{result['left']} ↔ {result['right']}` — {result['error']}")
        elif result.get("matched"):
            section.append(
                f"- ✅ `{result['left']} ↔ {result['right']}` — body SHA-256 "
                f"`{result['leftInspection']['bodySha256']}` ({result['leftInspection']['bodyBytes']} bytes)"
            )
        else:
            section.append(
                f"- ❌ `{result['left']} ↔ {result['right']}` — executable-body hashes differ: "
                f"`{result['leftInspection']['bodySha256']}` vs `{result['rightInspection']['bodySha256']}`"
            )
    section.append("")
    path.write_text(text.rstrip() + "\n" + "\n".join(section), encoding="utf-8")


def run(root: Path, policy_path: Path, report_path: Path, markdown_path: Path) -> int:
    policy = load_json(policy_path)
    urls = resolve_endpoint_urls(root, policy)
    network = policy.get("network", {})
    timeout = float(network.get("timeoutSeconds", 30))
    retries = int(network.get("retries", 3))
    user_agent = str(network.get("userAgent", "MissionChief-Toolkit-Asset-Health/1.0"))
    report = load_json(report_path)
    report["failures"] = [item for item in report.get("failures", []) if item.get("code") not in MANAGED_CODES]
    checks = report.setdefault("checks", [])
    checks[:] = [item for item in checks if item.get("kind") != "distribution-body-parity"]
    results: list[dict[str, Any]] = []

    for comparison in policy.get("crossEndpointComparisons", []):
        if comparison.get("field") != "bodySha256":
            continue
        left_id = str(comparison.get("left", ""))
        right_id = str(comparison.get("right", ""))
        code = str(comparison.get("code", "distribution-body-mismatch"))
        description = str(comparison.get("description", "Public executable userscript bodies differ."))
        subject = f"{left_id} ↔ {right_id}"
        result: dict[str, Any] = {"left": left_id, "right": right_id}
        try:
            if left_id not in urls or right_id not in urls:
                raise KeyError("comparison endpoint URL is missing from explicitEndpoints")
            left_inspection = inspect(fetch(urls[left_id], timeout, retries, user_agent))
            right_inspection = inspect(fetch(urls[right_id], timeout, retries, user_agent))
            result.update(
                {
                    "leftInspection": left_inspection,
                    "rightInspection": right_inspection,
                    "matched": left_inspection["bodySha256"] == right_inspection["bodySha256"],
                }
            )
            if not result["matched"]:
                report["failures"].append(
                    {"severity": "failure", "code": code, "message": description, "subject": subject}
                )
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            report["failures"].append(
                {
                    "severity": "failure",
                    "code": "distribution-parity-fetch-error",
                    "message": result["error"],
                    "subject": subject,
                }
            )
        results.append(result)
        checks.append(
            {
                "id": f"distribution-body-parity:{left_id}:{right_id}",
                "kind": "distribution-body-parity",
                "left": left_id,
                "right": right_id,
                "status": 200 if result.get("matched") else None,
                **result,
            }
        )

    recompute_report(report)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_markdown(markdown_path, report, results)
    for result in results:
        if result.get("matched"):
            print(
                f"PASS {result['left']} ↔ {result['right']}: "
                f"{result['leftInspection']['bodySha256']}"
            )
        else:
            print(f"FAIL {result['left']} ↔ {result['right']}: {result.get('error', 'body mismatch')}")
    return 1 if report["summary"]["failures"] else 0


class FixtureHandler(BaseHTTPRequestHandler):
    routes: dict[str, bytes] = {}

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        body = self.routes.get(urllib.parse.urlparse(self.path).path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/javascript")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def self_test() -> int:
    base = b"// ==UserScript==\n// @version 1.2.3\n// ==/UserScript==\nconsole.log('same');\n"
    transformed = b"// ==UserScript==\n// @version 1.2.3\n// served-by Greasy Fork\n// ==/UserScript==\nconsole.log('same');\n"
    changed = b"// ==UserScript==\n// @version 1.2.3\n// ==/UserScript==\nconsole.log('changed');\n"
    assert inspect(base)["bodySha256"] == inspect(transformed)["bodySha256"]
    assert inspect(base)["sha256"] != inspect(transformed)["sha256"]
    assert inspect(base)["bodySha256"] != inspect(changed)["bodySha256"]

    FixtureHandler.routes = {"/left.user.js": base, "/right.user.js": transformed}
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".github").mkdir()
            policy = {
                "explicitEndpoints": [
                    {"id": "left", "url": f"http://127.0.0.1:{server.server_port}/left.user.js"},
                    {"id": "right", "url": f"http://127.0.0.1:{server.server_port}/right.user.js"},
                ],
                "crossEndpointComparisons": [
                    {"left": "left", "right": "right", "field": "bodySha256", "code": "distribution-body-mismatch"}
                ],
                "network": {"timeoutSeconds": 2, "retries": 1, "userAgent": "parity-self-test"},
            }
            policy_path = root / ".github/policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            report_path = root / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "checks": [],
                        "failures": [],
                        "warnings": [],
                        "summary": {"failures": 0, "warnings": 0},
                        "fingerprint": "healthy",
                    }
                ),
                encoding="utf-8",
            )
            markdown_path = root / "report.md"
            markdown_path.write_text(
                "# Toolkit asset-health report\n\n- Failures: **0**\n- Warnings: **0**\n- Fingerprint: `healthy`\n",
                encoding="utf-8",
            )
            assert run(root, policy_path, report_path, markdown_path) == 0
            output = load_json(report_path)
            assert output["summary"]["failures"] == 0
    finally:
        server.shutdown()
        thread.join(timeout=2)
    print("Distribution-body parity self-test passed")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy", default=".github/asset-health-policy.json")
    parser.add_argument("--report", default="asset-health-report.json")
    parser.add_argument("--markdown", default="asset-health-report.md")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    return run(root, root / args.policy, root / args.report, root / args.markdown)


if __name__ == "__main__":
    raise SystemExit(main())
