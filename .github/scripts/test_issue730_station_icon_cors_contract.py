#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
GUIDE = ROOT / "docs" / "issue-728-station-icon-copier.md"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.17.2"

    assert "// @connect      leitstellenspiel.s3.amazonaws.com" in source
    assert "@connect      *" not in source
    assert (
        "const STATION_ICON_PRIVILEGED_IMAGE_HOSTS = "
        "Object.freeze(['leitstellenspiel.s3.amazonaws.com']);"
    ) in source

    request_helper = section(source, "    function runtimeGmRequest(", "    runtimeOnCleanup(")
    for required in (
        "GM_xmlhttpRequest({",
        "anonymous: Boolean(anonymous)",
        "runtime.requests.add(request)",
        "runtime.requests.delete(request)",
        "responseType",
        "timeout:",
    ):
        assert required in request_helper, required

    finance = section(source, "    function financeExternalRequest(", "    function validateFinancialRule(")
    assert "runtimeGmRequest({" in finance
    assert "GM_xmlhttpRequest(" not in finance

    copier = section(source, "    function stationIconText(", "    function vehicleTargetInfo(")
    privileged = section(
        copier,
        "    function stationIconPrivilegedImageUrl(",
        "    function stationIconImagesMatch(",
    )
    for required in (
        "url.protocol !== 'https:'",
        "STATION_ICON_PRIVILEGED_IMAGE_HOSTS.includes(url.hostname.toLowerCase())",
        "responseType: 'arraybuffer'",
        "anonymous: true",
        "response?.finalUrl",
        "response?.responseHeaders",
        "STATION_ICON_MAX_BYTES",
        "stationIconInspectBlob(blob",
    ):
        assert required in privileged, required

    downloader = section(
        copier,
        "    async function fetchStationIconImage(iconUrl",
        "    function stationIconImagesMatch(",
    )
    assert downloader.index("runtimeFetch(url.href") < downloader.index(
        "fetchStationIconImagePrivileged(url.href"
    ), "Normal browser fetch must remain the first path"

    network_patterns = (
        r"\bGM_xmlhttpRequest\s*\(",
        r"\bGM\.xmlHttpRequest\s*\(",
        r"(?<![.\w])fetch\s*\(",
        r"\bnew\s+(?:pageWindow\.)?XMLHttpRequest\s*\(",
    )
    assert sum(len(re.findall(pattern, source)) for pattern in network_patterns) == 6

    guide = GUIDE.read_text(encoding="utf-8")
    assert "CORS-restricted MissionChief upload host" in guide
    assert "leitstellenspiel.s3.amazonaws.com" in guide

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert "test_issue730_station_icon_cors_contract.py" in preflight
    assert "test_issue730_station_icon_cors_runtime.mjs" in preflight

    print(
        "Issue #730 Station Icon Copier CORS contract passed: exact-host anonymous fallback, "
        "redirect/size guards and the six-site request budget are retained."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
