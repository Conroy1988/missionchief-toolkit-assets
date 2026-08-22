#!/usr/bin/env python3
"""Serve the local MissionChief Toolkit Dev Lab with a live source identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sys
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
LAB_FILES = (
    ROOT / "devlab" / "index.html",
    ROOT / "devlab" / "lab.css",
    ROOT / "devlab" / "lab.js",
    ROOT / "devlab" / "frame.html",
    ROOT / "devlab" / "fixture.css",
    ROOT / "devlab" / "frame.js",
)
VERSION_PATTERN = re.compile(r"^//\s*@version\s+(\S+)\s*$", re.MULTILINE)
PUBLIC_PREFIXES = ("devlab/", "src/", "assets/", "themes/", "help/")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def combined_sha256(paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def development_state() -> dict[str, object]:
    source_text = SOURCE.read_text(encoding="utf-8")
    version_match = VERSION_PATTERN.search(source_text)
    return {
        "schemaVersion": 1,
        "version": version_match.group(1) if version_match else "unknown",
        "sha256": sha256(SOURCE),
        "labSha256": combined_sha256(LAB_FILES),
        "sourceBytes": SOURCE.stat().st_size,
        "sourceMtimeNs": SOURCE.stat().st_mtime_ns,
    }


def allowed_request_path(raw_path: str) -> bool:
    path = unquote(urlsplit(raw_path).path).lstrip("/")
    if path in {"", "devlab", "__mcms_dev_state"}:
        return True
    parts = Path(path).parts
    if any(part.startswith(".") or part in {"node_modules", "release-bundle"} for part in parts):
        return False
    return any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES)


class DevLabHandler(SimpleHTTPRequestHandler):
    server_version = "MissionChiefDevLab/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, message: str, *args: object) -> None:
        sys.stdout.write(f"[dev-lab] {self.address_string()} {message % args}\n")
        sys.stdout.flush()

    def end_headers(self) -> None:
        path = urlsplit(self.path).path
        if path.startswith(("/devlab/", "/src/", "/__mcms_")):
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        path = urlsplit(self.path).path
        if not allowed_request_path(self.path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if path == "/__mcms_dev_state":
            payload = json.dumps(development_state(), sort_keys=True).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path in {"/", "/devlab"}:
            self.path = "/devlab/index.html"
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib handler API
        if not allowed_request_path(self.path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if urlsplit(self.path).path in {"/", "/devlab"}:
            self.path = "/devlab/index.html"
        super().do_HEAD()

    def translate_path(self, path: str) -> str:
        clean = unquote(urlsplit(path).path).lstrip("/")
        candidate = (ROOT / clean).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            return str(ROOT / "__dev_lab_forbidden__")
        return str(candidate)

    def guess_type(self, path: str) -> str:
        if path.endswith((".user.js", ".mjs", ".js")):
            return "text/javascript; charset=utf-8"
        if path.endswith(".json"):
            return "application/json; charset=utf-8"
        return mimetypes.guess_type(path)[0] or "application/octet-stream"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--open", action="store_true", dest="open_browser")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        raise SystemExit("Port must be between 1 and 65535")
    if not SOURCE.is_file() or any(not path.is_file() for path in LAB_FILES):
        raise SystemExit("Dev Lab source files are incomplete")

    server = ThreadingHTTPServer((args.host, args.port), DevLabHandler)
    url = f"http://{args.host}:{args.port}/devlab/"
    print(f"MissionChief Toolkit Dev Lab: {url}", flush=True)
    print("Watching canonical source; Ctrl+C stops the local server.", flush=True)
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nDev Lab stopped.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
