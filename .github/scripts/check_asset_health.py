#!/usr/bin/env python3
"""Static and live health checks for MissionChief Toolkit public assets."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

URL_RE = re.compile(r"https?://[^\s'\"`<>\\]+", re.IGNORECASE)
VERSION_RE = re.compile(r"^//\s*@version\s+(.+?)\s*$", re.MULTILINE)
ASSET_LITERAL_RE = re.compile(
    r"(?P<quote>['\"])(?P<value>[^'\"\r\n]+?\.(?:mp3|wav|ogg|png|jpe?g|gif|webp|svg|json))(?P=quote)",
    re.IGNORECASE,
)
RAW_BASE_RE = re.compile(
    r"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?P<quote>['\"])(?P<url>https://raw\.githubusercontent\.com/[^'\"\r\n]+/)(?P=quote)",
    re.IGNORECASE,
)
TRAILING_URL_PUNCTUATION = ").,;:]}>"
DEFAULT_EXCLUDED_DIRS = {".git", "node_modules", "release-bundle", "__pycache__"}


@dataclasses.dataclass
class Finding:
    severity: str
    code: str
    message: str
    subject: str = ""

    def as_dict(self) -> dict[str, str]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Endpoint:
    id: str
    url: str
    kind: str
    required: bool = True
    source: str = "discovered"
    local_path: str | None = None
    compare_version: bool = False
    compare_hash: bool = False
    allowed_warning_statuses: tuple[int, ...] = ()
    min_bytes: int | None = None
    max_bytes: int | None = None

    def merge(self, other: "Endpoint") -> "Endpoint":
        return Endpoint(
            id=self.id if self.source == "explicit" else other.id,
            url=self.url,
            kind=other.kind if other.source == "explicit" else self.kind,
            required=self.required or other.required,
            source="explicit" if "explicit" in {self.source, other.source} else self.source,
            local_path=other.local_path or self.local_path,
            compare_version=self.compare_version or other.compare_version,
            compare_hash=self.compare_hash or other.compare_hash,
            allowed_warning_statuses=tuple(sorted(set(self.allowed_warning_statuses) | set(other.allowed_warning_statuses))),
            min_bytes=other.min_bytes if other.min_bytes is not None else self.min_bytes,
            max_bytes=other.max_bytes if other.max_bytes is not None else self.max_bytes,
        )


class AssetHealthError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssetHealthError(f"Required JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetHealthError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AssetHealthError(f"Top-level JSON value must be an object: {path}")
    return data


def json_pointer(document: Any, pointer: str) -> Any:
    if pointer in {"", "/"}:
        return document
    current = document
    for raw_part in pointer.lstrip("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise KeyError(pointer)
    return current


def clean_url(value: str) -> str:
    value = html.unescape(value.strip())
    while value and value[-1] in TRAILING_URL_PUNCTUATION:
        value = value[:-1]
    return value


def is_concrete_url(url: str) -> bool:
    return not any(token in url for token in ("${", "{", "}", "*", "<", ">"))


def extension_for_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    if path.endswith(".user.js"):
        return ".user.js"
    if path.endswith(".meta.js"):
        return ".meta.js"
    return Path(path).suffix.lower()


def kind_for_url(url: str, media_policy: dict[str, Any]) -> str:
    ext = extension_for_url(url)
    if ext == ".user.js":
        return "userscript"
    if ext == ".meta.js":
        return "metadata"
    if ext in media_policy:
        return "media"
    if "/releases/" in urllib.parse.urlparse(url).path and "/download/" in urllib.parse.urlparse(url).path:
        return "release-asset"
    return "url"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_scan_files(root: Path, policy: dict[str, Any]) -> list[Path]:
    paths: set[Path] = set()
    for raw in policy.get("scanFiles", []):
        path = root / raw
        if path.is_file():
            paths.add(path)
    extensions = {str(value).lower() for value in policy.get("scanTextExtensions", [])}
    excluded = DEFAULT_EXCLUDED_DIRS | set(policy.get("excludedDirectories", []))
    if extensions:
        for path in root.rglob("*"):
            if not path.is_file() or any(part in excluded for part in path.relative_to(root).parts):
                continue
            if path.suffix.lower() in extensions or path.name.endswith(".user.js"):
                paths.add(path)
    return sorted(paths)


def relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def parse_raw_github_url(url: str) -> tuple[str, str, str, str] | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname != "raw.githubusercontent.com":
        return None
    parts = [urllib.parse.unquote(part) for part in parsed.path.lstrip("/").split("/")]
    if len(parts) < 4:
        return None
    owner, repo, ref = parts[:3]
    return owner, repo, ref, "/".join(parts[3:])


def discover_local_media(root: Path, policy: dict[str, Any]) -> list[Path]:
    extensions = {
        ext.lower()
        for ext, config in policy.get("mediaExtensions", {}).items()
        if not isinstance(config, dict) or config.get("repositoryAsset", True)
    }
    excluded = DEFAULT_EXCLUDED_DIRS | set(policy.get("excludedDirectories", []))
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in excluded for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in extensions:
            paths.append(path)
    return sorted(paths)


def expected_types(kind: str, extension: str, policy: dict[str, Any]) -> set[str]:
    if kind in {"userscript", "metadata"}:
        return {value.lower() for value in policy.get("scriptContentTypes", [])}
    media = policy.get("mediaExtensions", {}).get(extension, {})
    return {value.lower() for value in media.get("contentTypes", [])}


def validate_magic(data: bytes, extension: str) -> bool:
    ext = extension.lower()
    stripped = data.lstrip()
    if ext == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if ext == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a"))
    if ext == ".webp":
        return len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    if ext == ".wav":
        return len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WAVE"
    if ext == ".ogg":
        return data.startswith(b"OggS")
    if ext == ".mp3":
        return data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)
    if ext == ".svg":
        return b"<svg" in stripped[:512].lower()
    if ext == ".json":
        try:
            json.loads(data.decode("utf-8"))
            return True
        except (UnicodeDecodeError, json.JSONDecodeError):
            return False
    return True


def resolve_explicit_endpoints(root: Path, policy: dict[str, Any]) -> list[Endpoint]:
    endpoints: list[Endpoint] = []
    for entry in policy.get("explicitEndpoints", []):
        if not isinstance(entry, dict):
            raise AssetHealthError("Each explicit endpoint must be an object")
        url = entry.get("url")
        if not url and entry.get("urlSource"):
            source = entry["urlSource"]
            document = load_json(root / source["path"])
            try:
                url = json_pointer(document, source["jsonPointer"])
            except (KeyError, IndexError, ValueError, TypeError) as exc:
                raise AssetHealthError(f"Could not resolve URL for endpoint {entry.get('id')}: {exc}") from exc
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise AssetHealthError(f"Endpoint {entry.get('id')} has no valid URL")
        endpoints.append(
            Endpoint(
                id=str(entry.get("id") or clean_url(url)),
                url=clean_url(url),
                kind=str(entry.get("kind") or kind_for_url(url, policy.get("mediaExtensions", {}))),
                required=bool(entry.get("required", True)),
                source="explicit",
                compare_version=bool(entry.get("compareLatestReleaseVersion", False)),
                compare_hash=bool(entry.get("compareLatestReleaseHash", False)),
                allowed_warning_statuses=tuple(int(value) for value in entry.get("allowedWarningStatuses", [])),
                min_bytes=int(entry["minBytes"]) if entry.get("minBytes") is not None else None,
                max_bytes=int(entry["maxBytes"]) if entry.get("maxBytes") is not None else None,
            )
        )
    return endpoints


def discover_endpoints(root: Path, policy: dict[str, Any], repository: str) -> tuple[list[Endpoint], list[Path], list[Path]]:
    media_policy = policy.get("mediaExtensions", {})
    monitored_hosts = {host.lower() for host in policy.get("monitoredHosts", [])}
    excluded_hosts = {host.lower() for host in policy.get("excludedHosts", [])}
    scan_files = iter_scan_files(root, policy)
    discovered: dict[str, Endpoint] = {}
    raw_bases: set[str] = set()
    asset_literals: set[str] = set()

    for path in scan_files:
        text = read_text(path)
        source_name = relative_path(path, root)
        for match in URL_RE.finditer(text):
            url = clean_url(match.group(0))
            if not is_concrete_url(url):
                continue
            parsed = urllib.parse.urlparse(url)
            host = (parsed.hostname or "").lower()
            if host in excluded_hosts:
                continue
            is_release_download = host == "github.com" and "/releases/" in parsed.path and "/download/" in parsed.path
            if host not in monitored_hosts and not is_release_download:
                continue
            if url.endswith("/"):
                if host == "raw.githubusercontent.com":
                    raw_bases.add(url)
                continue
            endpoint = Endpoint(
                id=f"discovered:{hashlib.sha1(url.encode()).hexdigest()[:12]}",
                url=url,
                kind=kind_for_url(url, media_policy),
                source=source_name,
            )
            discovered[url] = discovered[url].merge(endpoint) if url in discovered else endpoint

        for base_match in RAW_BASE_RE.finditer(text):
            raw_bases.add(clean_url(base_match.group("url")))
        for literal_match in ASSET_LITERAL_RE.finditer(text):
            value = literal_match.group("value")
            if not value.startswith(("http://", "https://")):
                asset_literals.add(value.lstrip("./"))

    for base in sorted(raw_bases):
        parsed_base = parse_raw_github_url(base + "placeholder")
        if not parsed_base:
            continue
        owner, repo, _ref, path_with_placeholder = parsed_base
        prefix = path_with_placeholder.rsplit("/", 1)[0]
        if f"{owner}/{repo}".lower() != repository.lower():
            continue
        for literal in sorted(asset_literals):
            candidate_path = "/".join(part for part in (prefix, literal) if part)
            local = root / candidate_path
            if not local.is_file():
                continue
            url = urllib.parse.urljoin(base, urllib.parse.quote(literal, safe="/._-"))
            endpoint = Endpoint(
                id=f"resolved:{hashlib.sha1(url.encode()).hexdigest()[:12]}",
                url=url,
                kind="media",
                source="resolved-base-and-filename",
                local_path=candidate_path,
            )
            discovered[url] = discovered[url].merge(endpoint) if url in discovered else endpoint

    for endpoint in resolve_explicit_endpoints(root, policy):
        discovered[endpoint.url] = discovered[endpoint.url].merge(endpoint) if endpoint.url in discovered else endpoint

    local_media = discover_local_media(root, policy)
    stable_ref = str(policy.get("repository", {}).get("stableRef", "main"))
    owner, repo = repository.split("/", 1)
    for path in local_media:
        rel = relative_path(path, root)
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{stable_ref}/{urllib.parse.quote(rel, safe='/._-')}"
        endpoint = Endpoint(
            id=f"repository-media:{rel}",
            url=url,
            kind="media",
            source="repository-media",
            local_path=rel,
        )
        discovered[url] = discovered[url].merge(endpoint) if url in discovered else endpoint

    return sorted(discovered.values(), key=lambda item: (item.kind, item.url)), scan_files, local_media


def latest_release_expectations(root: Path, policy: dict[str, Any]) -> tuple[str | None, str | None]:
    document = load_json(root / policy.get("latestReleaseDashboard", "status/release-dashboard.json"))
    latest = document.get("latestRelease")
    if not isinstance(latest, dict):
        return None, None
    version = latest.get("version")
    digest = latest.get("sha256")
    return (str(version) if version else None, str(digest).lower() if digest else None)


def content_type_base(value: str | None) -> str:
    return (value or "").split(";", 1)[0].strip().lower()


def request_once(url: str, method: str, timeout: float, user_agent: str, range_prefix: int | None = None) -> tuple[int, dict[str, str], bytes, str]:
    headers = {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
    }
    if range_prefix is not None:
        headers["Range"] = f"bytes=0-{max(0, range_prefix - 1)}"
    request = urllib.request.Request(url, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = int(getattr(response, "status", response.getcode()))
        response_headers = {key.lower(): value for key, value in response.headers.items()}
        body = response.read(range_prefix if range_prefix is not None else -1) if method != "HEAD" else b""
        return status, response_headers, body, response.geturl()


def request_with_retries(url: str, method: str, network: dict[str, Any], range_prefix: int | None = None) -> tuple[int, dict[str, str], bytes, str]:
    retries = int(network.get("retries", 3))
    timeout = float(network.get("timeoutSeconds", 30))
    backoff = float(network.get("retryBackoffSeconds", 2))
    user_agent = str(network.get("userAgent", "MissionChief-Toolkit-Asset-Health/1.0"))
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return request_once(url, method, timeout, user_agent, range_prefix)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504} or attempt == retries:
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt == retries:
                raise
        time.sleep(backoff * attempt)
    assert last_error is not None
    raise last_error


def full_get(url: str, network: dict[str, Any]) -> tuple[int, dict[str, str], bytes, str]:
    maximum = int(network.get("maxBytesPerAsset", 30_000_000))
    status, headers, body, final_url = request_with_retries(url, "GET", network)
    if len(body) > maximum:
        raise AssetHealthError(f"Downloaded payload exceeds maxBytesPerAsset ({maximum})")
    return status, headers, body, final_url


def head_and_prefix(url: str, network: dict[str, Any]) -> tuple[int, dict[str, str], bytes, str]:
    prefix_bytes = int(network.get("signatureBytes", 4096))
    try:
        status, headers, _, final_url = request_with_retries(url, "HEAD", network)
    except urllib.error.HTTPError as exc:
        if exc.code not in {400, 403, 405, 501}:
            raise
        status, headers, body, final_url = request_with_retries(url, "GET", network, range_prefix=prefix_bytes)
        return status, headers, body, final_url
    prefix_status, prefix_headers, body, prefix_final = request_with_retries(url, "GET", network, range_prefix=prefix_bytes)
    combined = dict(prefix_headers)
    combined.update(headers)
    return status if status else prefix_status, combined, body, prefix_final or final_url


def local_file_findings(path: Path, rel: str, extension: str, policy: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    media = policy.get("mediaExtensions", {}).get(extension, {})
    size = path.stat().st_size
    minimum = int(media.get("minBytes", 1))
    maximum = int(media.get("maxBytes", policy.get("network", {}).get("maxBytesPerAsset", 30_000_000)))
    if size < minimum:
        findings.append(Finding("failure", "local-file-too-small", f"Local file is {size} bytes; minimum is {minimum}", rel))
    if size > maximum:
        findings.append(Finding("failure", "local-file-too-large", f"Local file is {size} bytes; maximum is {maximum}", rel))
    prefix = path.read_bytes()[:8192]
    if not validate_magic(prefix, extension):
        findings.append(Finding("failure", "local-file-signature", "Local file signature does not match its extension", rel))
    if prefix.startswith(b"version https://git-lfs.github.com/spec/v1"):
        findings.append(Finding("failure", "git-lfs-pointer", "Repository contains a Git LFS pointer instead of the asset bytes", rel))
    return findings


def status_finding(endpoint: Endpoint, status: int) -> Finding | None:
    if status in {200, 206}:
        return None
    if status in endpoint.allowed_warning_statuses or not endpoint.required:
        return Finding("warning", "optional-http-status", f"Optional endpoint returned HTTP {status}", endpoint.url)
    return Finding("failure", "http-status", f"Endpoint returned HTTP {status}", endpoint.url)


def validate_remote_endpoint(endpoint: Endpoint, root: Path, policy: dict[str, Any], expected_version: str | None, expected_hash: str | None) -> tuple[dict[str, Any], list[Finding]]:
    findings: list[Finding] = []
    network = policy.get("network", {})
    extension = extension_for_url(endpoint.url)
    record: dict[str, Any] = {
        "id": endpoint.id,
        "url": endpoint.url,
        "kind": endpoint.kind,
        "source": endpoint.source,
        "required": endpoint.required,
        "localPath": endpoint.local_path,
    }
    try:
        if endpoint.kind in {"userscript", "metadata"}:
            status, headers, body, final_url = full_get(endpoint.url, network)
        else:
            status, headers, body, final_url = head_and_prefix(endpoint.url, network)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        record.update({"status": status, "error": str(exc)})
        finding = status_finding(endpoint, status)
        if finding:
            findings.append(finding)
        return record, findings
    except (urllib.error.URLError, TimeoutError, OSError, AssetHealthError) as exc:
        severity = "failure" if endpoint.required else "warning"
        findings.append(Finding(severity, "request-error", str(exc), endpoint.url))
        record.update({"status": None, "error": str(exc)})
        return record, findings

    content_type = content_type_base(headers.get("content-type"))
    content_length_raw = headers.get("content-length")
    content_length = int(content_length_raw) if content_length_raw and content_length_raw.isdigit() else None
    record.update(
        {
            "status": status,
            "finalUrl": final_url,
            "contentType": content_type,
            "contentLength": content_length,
            "prefixBytesRead": len(body),
        }
    )
    finding = status_finding(endpoint, status)
    if finding:
        findings.append(finding)
        return record, findings

    allowed_types = expected_types(endpoint.kind, extension, policy)
    if allowed_types and content_type not in allowed_types:
        findings.append(
            Finding(
                "failure" if endpoint.required else "warning",
                "content-type",
                f"Content-Type {content_type or '(missing)'} is not allowed; expected one of {sorted(allowed_types)}",
                endpoint.url,
            )
        )

    actual_size = len(body) if endpoint.kind in {"userscript", "metadata"} else content_length
    minimum = endpoint.min_bytes
    maximum = endpoint.max_bytes
    media = policy.get("mediaExtensions", {}).get(extension, {})
    if minimum is None and media:
        minimum = int(media.get("minBytes", 1))
    if maximum is None and media and media.get("maxBytes") is not None:
        maximum = int(media["maxBytes"])
    if actual_size is not None:
        record["observedBytes"] = actual_size
        if minimum is not None and actual_size < minimum:
            findings.append(Finding("failure", "remote-too-small", f"Remote payload is {actual_size} bytes; minimum is {minimum}", endpoint.url))
        if maximum is not None and actual_size > maximum:
            findings.append(Finding("failure", "remote-too-large", f"Remote payload is {actual_size} bytes; maximum is {maximum}", endpoint.url))
    elif endpoint.kind == "media":
        findings.append(Finding("warning", "missing-content-length", "Remote media did not provide Content-Length", endpoint.url))

    if endpoint.local_path:
        local = root / endpoint.local_path
        if not local.is_file():
            findings.append(Finding("failure", "missing-local-path", f"Referenced repository path is missing: {endpoint.local_path}", endpoint.url))
        else:
            local_size = local.stat().st_size
            record["localBytes"] = local_size
            if content_length is not None and content_length != local_size:
                findings.append(Finding("failure", "remote-size-mismatch", f"Remote size {content_length} does not match local size {local_size}", endpoint.url))

    if endpoint.kind == "media" and extension and not validate_magic(body, extension):
        findings.append(Finding("failure", "remote-file-signature", "Remote response signature does not match the asset extension", endpoint.url))

    if endpoint.kind in {"userscript", "metadata"}:
        digest = hashlib.sha256(body).hexdigest()
        record["sha256"] = digest
        text = body.decode("utf-8", errors="replace")
        version_match = VERSION_RE.search(text)
        version = version_match.group(1).strip() if version_match else None
        record["version"] = version
        if not version:
            findings.append(Finding("failure", "missing-version", "Could not read @version from script payload", endpoint.url))
        if endpoint.compare_version:
            if not expected_version:
                findings.append(Finding("failure", "missing-release-version", "Latest release version is absent from the dashboard", endpoint.url))
            elif version != expected_version:
                findings.append(Finding("failure", "version-mismatch", f"Observed version {version!r}; expected {expected_version!r}", endpoint.url))
        if endpoint.compare_hash:
            if not expected_hash:
                findings.append(Finding("failure", "missing-release-hash", "Latest release SHA-256 is absent from the dashboard", endpoint.url))
            elif digest.lower() != expected_hash.lower():
                findings.append(Finding("failure", "sha256-mismatch", f"Observed SHA-256 {digest}; expected {expected_hash}", endpoint.url))

    return record, findings


def validate_static_endpoint(endpoint: Endpoint, root: Path, repository: str, policy: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    parsed = urllib.parse.urlparse(endpoint.url)
    if not parsed.scheme or not parsed.netloc:
        findings.append(Finding("failure", "invalid-url", "Endpoint URL is invalid", endpoint.url))
        return findings
    raw = parse_raw_github_url(endpoint.url)
    if raw:
        owner, repo, ref, remote_path = raw
        stable_ref = str(policy.get("repository", {}).get("stableRef", "main"))
        if f"{owner}/{repo}".lower() == repository.lower() and ref == stable_ref:
            local = root / remote_path
            if not local.is_file():
                findings.append(Finding("failure", "missing-repository-asset", f"Stable raw URL points to missing repository file: {remote_path}", endpoint.url))
            elif endpoint.local_path and endpoint.local_path != remote_path:
                findings.append(Finding("failure", "raw-path-mismatch", f"Resolved local path {endpoint.local_path} does not match raw path {remote_path}", endpoint.url))
    return findings


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Toolkit asset-health report",
        "",
        f"- Mode: **{report['mode']}**",
        f"- Generated: `{report['generatedAt']}`",
        f"- Endpoints checked: **{summary['endpoints']}**",
        f"- Repository media files: **{summary['localMediaFiles']}**",
        f"- Failures: **{summary['failures']}**",
        f"- Warnings: **{summary['warnings']}**",
        f"- Fingerprint: `{report['fingerprint']}`",
        "",
    ]
    if report["failures"]:
        lines.extend(["## Failures", ""])
        for item in report["failures"][:60]:
            lines.append(f"- **{item['code']}** — {item['message']}  ")
            if item.get("subject"):
                lines.append(f"  `{item['subject']}`")
        lines.append("")
    if report["warnings"]:
        lines.extend(["## Warnings", ""])
        for item in report["warnings"][:40]:
            lines.append(f"- **{item['code']}** — {item['message']}  ")
            if item.get("subject"):
                lines.append(f"  `{item['subject']}`")
        lines.append("")
    lines.extend(["## Endpoint results", "", "| Status | Kind | Endpoint | Type | Bytes |", "|---|---|---|---|---:|"])
    for check in report["checks"][:120]:
        status = check.get("status")
        status_text = "static" if status is None and report["mode"] == "static" else str(status or "error")
        url = str(check.get("url", "")).replace("|", "%7C")
        ctype = str(check.get("contentType") or "—").replace("|", "\\|")
        size = check.get("observedBytes") or check.get("contentLength") or "—"
        lines.append(f"| {status_text} | {check.get('kind', '—')} | `{url}` | {ctype} | {size} |")
    lines.append("")
    return "\n".join(lines)


def build_report(root: Path, policy: dict[str, Any], mode: str, repository: str) -> dict[str, Any]:
    failures: list[Finding] = []
    warnings: list[Finding] = []
    checks: list[dict[str, Any]] = []

    endpoints, scan_files, local_media = discover_endpoints(root, policy, repository)
    maximum_endpoints = int(policy.get("limits", {}).get("maxEndpoints", 250))
    if len(endpoints) > maximum_endpoints:
        failures.append(Finding("failure", "too-many-endpoints", f"Discovered {len(endpoints)} endpoints; maximum is {maximum_endpoints}"))

    for path in local_media:
        rel = relative_path(path, root)
        for finding in local_file_findings(path, rel, path.suffix.lower(), policy):
            (failures if finding.severity == "failure" else warnings).append(finding)

    expected_version, expected_hash = latest_release_expectations(root, policy)

    for endpoint in endpoints:
        for finding in validate_static_endpoint(endpoint, root, repository, policy):
            (failures if finding.severity == "failure" else warnings).append(finding)
        if mode == "static":
            checks.append(
                {
                    "id": endpoint.id,
                    "url": endpoint.url,
                    "kind": endpoint.kind,
                    "source": endpoint.source,
                    "required": endpoint.required,
                    "localPath": endpoint.local_path,
                    "status": None,
                }
            )
            continue
        check, endpoint_findings = validate_remote_endpoint(endpoint, root, policy, expected_version, expected_hash)
        checks.append(check)
        for finding in endpoint_findings:
            (failures if finding.severity == "failure" else warnings).append(finding)

    fingerprint_material = [f"{item.code}|{item.subject}|{item.message}" for item in sorted(failures, key=lambda item: (item.code, item.subject, item.message))]
    fingerprint = hashlib.sha256("\n".join(fingerprint_material).encode()).hexdigest()[:16] if fingerprint_material else "healthy"
    return {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "mode": mode,
        "repository": repository,
        "latestRelease": {"version": expected_version, "sha256": expected_hash},
        "discovery": {
            "scanFiles": [relative_path(path, root) for path in scan_files],
            "localMediaFiles": [relative_path(path, root) for path in local_media],
        },
        "checks": checks,
        "failures": [item.as_dict() for item in failures],
        "warnings": [item.as_dict() for item in warnings],
        "summary": {
            "endpoints": len(endpoints),
            "localMediaFiles": len(local_media),
            "failures": len(failures),
            "warnings": len(warnings),
        },
        "fingerprint": fingerprint,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--policy", default=".github/asset-health-policy.json")
    parser.add_argument("--mode", choices=("static", "live"), default="static")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Conroy1988/missionchief-toolkit-assets"))
    parser.add_argument("--json-output", default="asset-health-report.json")
    parser.add_argument("--markdown-output", default="asset-health-report.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    try:
        policy = load_json(root / args.policy)
        report = build_report(root, policy, args.mode, args.repository)
    except Exception as exc:
        failure = Finding("failure", "checker-error", f"{type(exc).__name__}: {exc}")
        report = {
            "schemaVersion": 1,
            "generatedAt": utc_now(),
            "mode": args.mode,
            "repository": args.repository,
            "latestRelease": {"version": None, "sha256": None},
            "discovery": {"scanFiles": [], "localMediaFiles": []},
            "checks": [],
            "failures": [failure.as_dict()],
            "warnings": [],
            "summary": {"endpoints": 0, "localMediaFiles": 0, "failures": 1, "warnings": 0},
            "fingerprint": hashlib.sha256(str(exc).encode()).hexdigest()[:16],
        }

    Path(args.json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(render_markdown(report), encoding="utf-8")
    print(
        f"Asset health ({report['mode']}): {report['summary']['endpoints']} endpoints, "
        f"{report['summary']['localMediaFiles']} local media files, "
        f"{report['summary']['failures']} failures, {report['summary']['warnings']} warnings"
    )
    for item in report["failures"]:
        print(f"FAIL {item['code']}: {item['message']} {item.get('subject', '')}".rstrip())
    for item in report["warnings"]:
        print(f"WARN {item['code']}: {item['message']} {item.get('subject', '')}".rstrip())
    return 1 if report["summary"]["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
