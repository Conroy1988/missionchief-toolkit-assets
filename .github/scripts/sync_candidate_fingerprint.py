#!/usr/bin/env python3
"""Generate or verify the canonical userscript's deterministic fingerprint."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DEFAULT_OUTPUT = ROOT / ".github" / "fixtures" / "current-toolkit-candidate.json"
VERSION_RE = re.compile(r"^//\s*@version\s+([^\s]+)\s*$", re.MULTILINE)


def repository_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_fingerprint(source: Path) -> dict[str, object]:
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    versions = VERSION_RE.findall(text)
    if len(versions) != 1:
        raise SystemExit("Canonical userscript must contain exactly one @version")
    return {
        "schemaVersion": 1,
        "source": {
            "bytes": len(raw),
            "lines": len(text.splitlines()),
            "path": repository_path(source),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "version": versions[0],
        },
    }


def serialized(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def verify(source: Path, output: Path) -> None:
    expected = build_fingerprint(source)
    try:
        current = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Candidate fingerprint is unavailable: {error}") from error
    if current != expected:
        raise SystemExit(
            "Candidate fingerprint is stale. Run "
            "`python3 .github/scripts/sync_candidate_fingerprint.py` before promotion."
        )
    print(
        "[candidate-fingerprint] verified "
        f"{expected['source']['version']} · {expected['source']['sha256']}"
    )


def write(source: Path, output: Path) -> None:
    payload = build_fingerprint(source)
    content = serialized(payload)
    previous = output.read_text(encoding="utf-8") if output.exists() else None
    if previous == content:
        print("[candidate-fingerprint] already current")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(
        "[candidate-fingerprint] updated "
        f"{output.relative_to(ROOT)} for {payload['source']['version']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        verify(args.source, args.output)
    else:
        write(args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
