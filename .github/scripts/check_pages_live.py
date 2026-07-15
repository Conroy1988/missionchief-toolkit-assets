#!/usr/bin/env python3
"""Verify the deployed GitHub Pages site and current release marker."""
from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch(url: str, timeout: int) -> tuple[int, str, bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "User-Agent": "missionchief-toolkit-pages-monitor/1.0",
        },
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return (
            int(response.status),
            response.headers.get("Content-Type", ""),
            response.read(),
            response.geturl(),
        )


def audit(root: Path) -> dict[str, Any]:
    policy = load_json(root / ".github/pages-monitor-policy.json")
    dashboard = load_json(root / "status/release-dashboard.json")
    version = str(dashboard.get("currentVersion") or dashboard.get("latestRelease", {}).get("version") or "")
    base_url = str(policy["baseUrl"])
    timeout = int(policy.get("timeoutSeconds", 25))
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    for route in policy.get("routes", []):
        path = str(route.get("path", ""))
        url = urllib.parse.urljoin(base_url, path)
        check: dict[str, Any] = {"path": path, "url": url, "status": "failed"}
        try:
            status, content_type, body, final_url = fetch(url, timeout)
            text = body.decode("utf-8", errors="replace")
            check.update({
                "httpStatus": status,
                "contentType": content_type,
                "bytes": len(body),
                "finalUrl": final_url,
            })
            if status != 200:
                failures.append(f"{path or '/'} returned HTTP {status}")
            expected_type = str(route.get("contentType", ""))
            if expected_type and expected_type.lower() not in content_type.lower():
                failures.append(
                    f"{path or '/'} returned content type {content_type!r}; expected {expected_type!r}"
                )
            minimum = int(route.get("minimumBytes", 1))
            if len(body) < minimum:
                failures.append(f"{path or '/'} returned only {len(body)} bytes; expected at least {minimum}")
            for required in route.get("requiredText", []):
                if str(required) not in text:
                    failures.append(f"{path or '/'} is missing required text: {required}")
            if path == "" and version and version not in text:
                failures.append(f"Home page does not expose current Toolkit version {version}")
            if not any(item.startswith(path or "/") for item in failures):
                check["status"] = "passed"
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            message = f"{path or '/'} could not be fetched: {error}"
            failures.append(message)
            check["error"] = str(error)
        checks.append(check)

    return {
        "schemaVersion": 1,
        "status": "failed" if failures else "passed",
        "checkedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "baseUrl": base_url,
        "expectedVersion": version,
        "checks": checks,
        "failures": failures,
    }


def markdown(report: dict[str, Any]) -> str:
    icon = "✅" if report["status"] == "passed" else "❌"
    lines = [
        "# GitHub Pages Production Health",
        "",
        f"{icon} **Status:** {report['status'].upper()}",
        "",
        f"- Site: {report['baseUrl']}",
        f"- Expected Toolkit version: **{report['expectedVersion']}**",
        f"- Routes checked: **{len(report['checks'])}**",
        f"- Checked: `{report['checkedAt']}`",
        "",
        "## Route results",
    ]
    for check in report["checks"]:
        route_icon = "✅" if check.get("status") == "passed" else "❌"
        lines.append(
            f"- {route_icon} `{check['path'] or '/'}` — {check.get('httpStatus', 'unavailable')}, "
            f"{check.get('bytes', 0)} bytes"
        )
    if report["failures"]:
        lines.extend(["", "## Failures", *[f"- {item}" for item in report["failures"]]])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-output", default="pages-production-health.json")
    parser.add_argument("--markdown-output", default="pages-production-health.md")
    args = parser.parse_args()
    report = audit(Path(args.root).resolve())
    Path(args.json_output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report), encoding="utf-8")
    print(markdown(report))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
